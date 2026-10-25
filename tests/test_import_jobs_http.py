"""Actual HTTP task control, including abandoned compatibility requests."""

from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import socket
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from doctor.import_jobs import ImportJobs
from doctor.serve import configure_import_loaders, make_handler
from internal.doctor_adapter.review import ReviewStore
from test_doctor_import_jobs import model_body, wait_for


@pytest.fixture
def supervised(tmp_path):
    worker = tmp_path / "blocked.py"
    worker.write_text(
        "import time\n"
        "print('BIMDOCTOR_IMPORT {\"stage\":\"tessellating\","
        "\"completed\":1,\"total\":100}',flush=True)\n"
        "while True: time.sleep(10)\n",
        encoding="utf-8",
    )
    store = ReviewStore()
    old = store.create("previous.ifc", model_body())
    with ImportJobs(store, tmp_path / "jobs", worker_script=worker) as jobs:
        configure_import_loaders(jobs)
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(
            lambda: None, review_factory=lambda: store, import_factory=lambda: jobs,
        ))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        yield f"http://127.0.0.1:{server.server_port}", jobs, store, old
        server.shutdown()
        server.server_close()
        thread.join()


def request(base, path, body=None):
    headers = {}
    if isinstance(body, dict):
        body = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    elif body is not None:
        headers["Content-Type"] = "application/octet-stream"
    with urlopen(Request(base + path, data=body, headers=headers), timeout=5) as response:
        return response.status, dict(response.headers), json.load(response)


def test_accepted_task_is_observable_and_does_not_block_existing_readers(supervised):
    base, jobs, _, old = supervised
    started = time.monotonic()
    status, headers, job = request(
        base, "/api/review/imports?filename=new.ifc&job=public-client", model_body(),
    )
    assert status == 202 and len(headers["X-Request-ID"]) == 32
    assert time.monotonic() - started < 2
    assert job["job_id"] == "public-client"
    wait_for(jobs, job["job_id"], {"running"})
    for endpoint in ("report", "geometry"):
        started = time.monotonic()
        status, _, result = request(base, f"/api/review/{endpoint}?review={old['review_id']}")
        assert status == 200 and result["review_id"] == old["review_id"]
        assert time.monotonic() - started < 1
    _, _, cancelled = request(
        base, "/api/review/imports/cancel", {"job_id": "public-client"},
    )
    assert cancelled["state"] == "cancelled" and cancelled["worker_exited"]


def test_cancel_before_upload_ack_is_a_backend_tombstone(supervised):
    base, _, _, _ = supervised
    _, _, cancelled = request(base, "/api/review/imports/cancel", {"job_id": "early-cancel"})
    assert cancelled["state"] == "cancelled"
    _, _, late = request(
        base, "/api/review/imports?filename=late.ifc&job=early-cancel", model_body(),
    )
    assert late["state"] == "cancelled" and late["worker_pid"] is None


def test_compatibility_post_uses_worker_and_returns_after_confirmed_cancellation(supervised):
    base, jobs, _, old = supervised
    with ThreadPoolExecutor(max_workers=1) as pool:
        waiting = pool.submit(
            request, base, "/api/review/models?filename=compat.ifc", model_body()
        )
        deadline = time.monotonic() + 3
        while not jobs.snapshot()["jobs"] and time.monotonic() < deadline:
            time.sleep(0.01)
        job = jobs.snapshot()["jobs"][-1]
        wait_for(jobs, job["job_id"], {"running"})
        assert request(base, f"/api/review/report?review={old['review_id']}")[2] == old
        jobs.cancel(job["job_id"])
        with pytest.raises(HTTPError) as error:
            waiting.result(timeout=5)
        assert error.value.code == 400


def test_abandoned_compatibility_connection_stops_the_actual_process(supervised):
    base, jobs, _, _ = supervised
    port = int(base.rsplit(":", 1)[1])
    connection = HTTPConnection("127.0.0.1", port, timeout=5)
    connection.request("POST", "/api/review/models?filename=abandoned.ifc", model_body(),
                       {"Content-Type": "application/octet-stream"})
    deadline = time.monotonic() + 3
    while not jobs.snapshot()["jobs"] and time.monotonic() < deadline:
        time.sleep(0.01)
    job = jobs.snapshot()["jobs"][-1]
    assert wait_for(jobs, job["job_id"], {"running"})["worker_pid"]
    connection.sock.shutdown(socket.SHUT_RDWR)
    connection.close()
    cancelled = wait_for(jobs, job["job_id"], {"cancelled"})
    assert cancelled["worker_exited"] and cancelled["review_id"] is None


def test_geometry_failure_has_a_correlated_request_and_original_phase(supervised, monkeypatch):
    base, _, store, old = supervised

    def fail(_):
        raise RuntimeError("Public injected geometry restore failure")

    monkeypatch.setattr(store, "geometry_payload", fail)
    with pytest.raises(HTTPError) as error:
        request(base, f"/api/review/geometry?review={old['review_id']}")
    response = error.value
    body = json.load(response)
    assert response.code == 500
    assert body["diagnostic"]["request_id"] == response.headers["X-Request-ID"]
    assert body["diagnostic"]["phase"] == "geometry_load"
    assert "RuntimeError: Public injected" in body["error"]
