"""Import supervision must stop work, retain old results and publish only complete output."""

import json
import os
import signal
import time

import ifcopenshell
import pytest

from doctor.import_jobs import ImportBusy, ImportJobs
from internal.doctor_adapter.review import ReviewStore


def wait_for(manager, identity, states, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = manager.get(identity)
        if result["state"] in states:
            return result
        time.sleep(0.02)
    raise AssertionError(manager.get(identity))


def model_body():
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), Name="Public test wall")
    return model.to_string().encode()


@pytest.fixture
def blocked_worker(tmp_path):
    path = tmp_path / "uncooperative_worker.py"
    path.write_text(
        "import json,time\n"
        "print('BIMDOCTOR_IMPORT '+json.dumps({'stage':'tessellating',"
        "'completed':1,'total':20}),flush=True)\n"
        "while True: time.sleep(10)\n", encoding="utf-8",
    )
    return path


def test_cancel_before_submit_prevents_late_upload_from_starting_worker(tmp_path):
    store = ReviewStore()
    with ImportJobs(store, tmp_path / "jobs") as jobs:
        assert jobs.cancel("client-before-ack")["state"] == "cancelled"
        result = jobs.submit("public.ifc", model_body(), job_id="client-before-ack")
        assert result["state"] == "cancelled"
        assert result["worker_pid"] is None
        assert not list((tmp_path / "jobs").glob("*/input.ifc"))


def test_cancel_stops_uncooperative_process_and_preserves_existing_review(
    tmp_path, blocked_worker
):
    store = ReviewStore()
    old = store.create("existing.ifc", model_body())
    with ImportJobs(store, tmp_path / "jobs", worker_script=blocked_worker) as jobs:
        job = jobs.submit("blocked.ifc", model_body())
        running = wait_for(jobs, job["job_id"], {"running"})
        assert running["worker_pid"]
        started = time.monotonic()
        assert store.get(old["review_id"]) == old
        assert time.monotonic() - started < 0.5
        cancelled = jobs.cancel(job["job_id"])
        cancelled = wait_for(jobs, job["job_id"], {"cancelled"})
        assert time.monotonic() - started < 5
        assert cancelled["worker_exited"]
        assert cancelled["review_id"] is None
        assert store.get(old["review_id"]) == old
        assert not list((tmp_path / "jobs").glob("*/input.ifc"))


def test_backend_deadline_terminates_worker_and_allows_retry(tmp_path, blocked_worker):
    store = ReviewStore()
    with ImportJobs(
        store, tmp_path / "jobs", worker_script=blocked_worker, timeout_seconds=0.4
    ) as jobs:
        first = jobs.submit("timeout.ifc", model_body())
        result = wait_for(jobs, first["job_id"], {"timed_out"})
        assert result["worker_exited"] and result["review_id"] is None
        assert result["error"]["code"] == "deadline_exceeded"
        second = jobs.submit("retry.ifc", model_body())
        assert second["job_id"] != first["job_id"]
        jobs.cancel(second["job_id"])


def test_only_one_native_worker_is_active(tmp_path, blocked_worker):
    with ImportJobs(ReviewStore(), tmp_path / "jobs", worker_script=blocked_worker) as jobs:
        first = jobs.submit("first.ifc", model_body())
        with pytest.raises(ImportBusy):
            jobs.submit("second.ifc", model_body())
        jobs.cancel(first["job_id"])


def test_cancel_stops_computing_descendants_not_only_the_python_launcher(tmp_path):
    heartbeat = tmp_path / "heartbeat"
    child_pid = tmp_path / "child.pid"
    child = tmp_path / "child.py"
    child.write_text(
        "import os,time\nfrom pathlib import Path\n"
        f"Path({str(child_pid)!r}).write_text(str(os.getpid()))\n"
        f"heartbeat=Path({str(heartbeat)!r})\n"
        "while True:\n heartbeat.write_text(str(time.monotonic_ns()))\n time.sleep(.02)\n",
        encoding="utf-8",
    )
    worker = tmp_path / "parent.py"
    worker.write_text(
        "import subprocess,sys,time\n"
        f"subprocess.Popen([sys.executable,{str(child)!r}])\n"
        "while True: time.sleep(10)\n",
        encoding="utf-8",
    )
    try:
        with ImportJobs(ReviewStore(), tmp_path / "jobs", worker_script=worker) as jobs:
            job = jobs.submit("public.ifc", model_body())
            deadline = time.monotonic() + 5
            while not heartbeat.exists() and time.monotonic() < deadline:
                time.sleep(.02)
            assert heartbeat.exists(), "The actual computing descendant did not start"
            jobs.cancel(job["job_id"])
            assert wait_for(jobs, job["job_id"], {"cancelled"})["worker_exited"]
            stopped = heartbeat.read_bytes()
            time.sleep(.25)
            assert heartbeat.read_bytes() == stopped, (
                "The computing descendant survived cancellation"
            )
    finally:
        if child_pid.exists():
            try:
                os.kill(int(child_pid.read_text()), signal.SIGTERM)
            except OSError:
                pass


def test_real_worker_publishes_complete_serialized_result_and_reuses_completed_input(tmp_path):
    store = ReviewStore()
    with ImportJobs(store, tmp_path / "jobs") as jobs:
        body = model_body()
        job = jobs.submit("public.ifc", body)
        result = wait_for(jobs, job["job_id"], {"succeeded", "failed"})
        assert result["state"] == "succeeded", result
        assert result["worker_exited"]
        report = store.get(result["review_id"])
        geometry = json.loads(store.geometry_payload(result["review_id"]))
        assert report["summary"]["elements"] == 1
        assert geometry["review_id"] == report["review_id"]
        repeated = jobs.submit("public.ifc", body)
        assert repeated["state"] == "succeeded"
        assert repeated["review_id"] == result["review_id"]
        assert repeated["worker_pid"] is None
        assert jobs.source_payload(result["review_id"]) == body


def test_invalid_input_fails_without_replacing_saved_report(tmp_path):
    store = ReviewStore()
    old = store.create("existing.ifc", model_body())
    with ImportJobs(store, tmp_path / "jobs") as jobs:
        job = jobs.submit("malformed.ifc", b"ISO-10303-21; broken public input")
        result = wait_for(jobs, job["job_id"], {"failed"})
        assert result["error"]["stage"]
        assert result["review_id"] is None and result["worker_exited"]
        assert store.get(old["review_id"]) == old


def test_job_metadata_history_and_artifact_storage_are_bounded(tmp_path):
    with ImportJobs(ReviewStore(), tmp_path / "jobs", max_history=3) as jobs:
        for index in range(10):
            jobs.cancel(f"cancelled-{index}")
        assert len(jobs.snapshot()["jobs"]) == 3
        with pytest.raises(KeyError):
            jobs.get("cancelled-0")


def test_repeated_same_import_keeps_payload_after_original_job_history_expires(tmp_path):
    store = ReviewStore(cache_max_bytes=1)
    body = model_body()
    with ImportJobs(store, tmp_path / "jobs", max_history=2) as jobs:
        store.set_loaders(report_loader=jobs.report_payload,
                          geometry_loader=jobs.geometry_payload)
        first = jobs.submit("public.ifc", body)
        first = wait_for(jobs, first["job_id"], {"succeeded", "failed"})
        assert first["state"] == "succeeded", first
        geometry = store.geometry_payload(first["review_id"])
        for _ in range(2):
            repeated = jobs.submit("public.ifc", body)
            assert repeated["state"] == "succeeded"
            assert repeated["worker_pid"] is None  # No repeated native work.
        assert len(jobs.snapshot()["jobs"]) == 2
        assert jobs.get(repeated["job_id"])["state"] == "succeeded"
        assert store.geometry_payload(first["review_id"]) == geometry
        assert jobs.source_payload(first["review_id"]) == body
        assert len(list((tmp_path / "jobs").glob("task-*"))) == 1


def test_reused_import_keeps_an_existing_source_reader_pinned(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from pathlib import Path
    import threading

    body = model_body()
    with ImportJobs(ReviewStore(cache_max_bytes=1), tmp_path / "jobs", max_history=2) as jobs:
        first = jobs.submit("public.ifc", body)
        first = wait_for(jobs, first["job_id"], {"succeeded", "failed"})
        assert first["state"] == "succeeded", first
        entered, release = threading.Event(), threading.Event()
        original = Path.read_bytes

        def pinned(path):
            if path.name == "input.ifc":
                entered.set()
                assert release.wait(5)
            return original(path)

        monkeypatch.setattr(Path, "read_bytes", pinned)
        with ThreadPoolExecutor(max_workers=1) as pool:
            read = pool.submit(jobs.source_payload, first["review_id"])
            assert entered.wait(3)
            try:
                for _ in range(5):
                    repeated = jobs.submit("public.ifc", body)
                    assert repeated["state"] == "succeeded"
                assert jobs.get(repeated["job_id"])["state"] == "succeeded"
                assert len(jobs.snapshot()["jobs"]) == 2
            finally:
                release.set()
            assert read.result(timeout=3) == body
        assert jobs.source_available(first["review_id"])


def test_a_pinned_old_result_cannot_leave_the_next_import_successful_but_unreadable(
    tmp_path, monkeypatch,
):
    from concurrent.futures import ThreadPoolExecutor
    from pathlib import Path
    import threading

    store = ReviewStore(cache_max_bytes=1)
    with ImportJobs(store, tmp_path / "jobs", max_artifacts=1) as jobs:
        store.set_loaders(report_loader=jobs.report_payload,
                          geometry_loader=jobs.geometry_payload)
        first = jobs.submit("first.ifc", model_body())
        first = wait_for(jobs, first["job_id"], {"succeeded", "failed"})
        assert first["state"] == "succeeded", first
        entered, release = threading.Event(), threading.Event()
        original = Path.read_bytes

        def pinned(path):
            if path.name == "input.ifc":
                entered.set()
                assert release.wait(10)
            return original(path)

        monkeypatch.setattr(Path, "read_bytes", pinned)
        with ThreadPoolExecutor(max_workers=1) as pool:
            read = pool.submit(jobs.source_payload, first["review_id"])
            assert entered.wait(3)
            second_body = model_body()
            try:
                latest = jobs.submit("second.ifc", second_body)
                latest = wait_for(jobs, latest["job_id"], {"succeeded", "failed"})
                if latest["state"] == "succeeded":
                    assert store.geometry_payload(latest["review_id"])
                else:
                    assert "budget" in latest["error"]["message"]
                    assert latest["error"]["code"] == "publication_failed"
                    assert "Retry" in latest["error"]["message"]
                    assert latest["review_id"] is None
            finally:
                release.set()
            assert read.result(timeout=3)
        jobs.wait(latest["job_id"], timeout=2)
        retried = jobs.submit("second.ifc", second_body)
        assert retried["job_id"] != latest["job_id"]
        retried = wait_for(jobs, retried["job_id"], {"succeeded", "failed"})
        assert retried["state"] == "succeeded", retried
        assert store.geometry_payload(retried["review_id"])


def test_pinned_purpose_result_prevents_a_second_result_handler_write(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from pathlib import Path
    import threading

    worker = tmp_path / "check_worker.py"
    worker.write_text(
        "import sys\nfrom pathlib import Path\n"
        "directory=Path(sys.argv[sys.argv.index('--output')+1])\n"
        "(directory/'result.json').write_text('{\"run_id\":\"public\"}')\n",
        encoding="utf-8",
    )
    published = []

    def publish(outputs):
        published.append(True)
        return json.loads(outputs["result.json"])

    with ImportJobs(ReviewStore(), tmp_path / "jobs", worker_script=worker,
                    output_files=("result.json",), result_handler=publish,
                    max_artifacts=1) as jobs:
        first = jobs.submit("first.ifc", model_body())
        first = wait_for(jobs, first["job_id"], {"succeeded", "failed"})
        assert first["state"] == "succeeded", first
        entered, release = threading.Event(), threading.Event()
        original = Path.read_bytes
        pinned_path = next((tmp_path / "jobs").glob("task-*/result.json"))

        def pinned(path):
            if path == pinned_path:
                entered.set()
                assert release.wait(5)
            return original(path)

        monkeypatch.setattr(Path, "read_bytes", pinned)
        with ThreadPoolExecutor(max_workers=1) as pool:
            read = pool.submit(jobs._artifact, None, "result.json")
            assert entered.wait(2)
            try:
                latest = jobs.submit("second.ifc", model_body())
                latest = wait_for(jobs, latest["job_id"], {"succeeded", "failed"})
                assert latest["state"] == "failed", latest
                assert "budget" in latest["error"]["message"]
                assert latest["result"] is None
                assert published == [True]
            finally:
                release.set()
            assert json.loads(read.result(timeout=3)) == {"run_id": "public"}


def test_publication_refuses_source_plus_outputs_that_would_evict_the_current_import(
    tmp_path,
    monkeypatch,
):
    body = model_body()
    fixture = ReviewStore()
    report = fixture.create("public.ifc", body)
    outputs = {
        "report.json": fixture.report_payload(report["review_id"]),
        "geometry.json": fixture.geometry_payload(report["review_id"]),
    }
    worker = tmp_path / "fixture_worker.py"
    worker.write_text(
        "import sys\nfrom pathlib import Path\n"
        "directory=Path(sys.argv[sys.argv.index('--output')+1])\n"
        + "\n".join(
            f"(directory/{name!r}).write_bytes({payload!r})"
            for name, payload in outputs.items()
        ),
        encoding="utf-8",
    )
    store = ReviewStore(cache_max_bytes=1)
    admitted = []
    original = store.admit_serialized

    def track(*args):
        admitted.append(True)
        return original(*args)

    monkeypatch.setattr(store, "admit_serialized", track)
    # Both valid outputs fit exactly. Only retaining input.ifc exceeds this
    # budget; silently trimming the job after success would strand its geometry.
    budget = sum(map(len, outputs.values()))
    assert budget < budget + len(body)
    with ImportJobs(
        store, tmp_path / "jobs", worker_script=worker, max_artifact_bytes=budget
    ) as jobs:
        job = jobs.submit("public.ifc", body)
        result = jobs.wait(job["job_id"], timeout=10)
        assert result["state"] == "failed", result
        assert result["worker_exited"] and result["review_id"] is None
        assert "budget" in result["error"]["message"]
        assert admitted == []
        assert store.stats()["entries"] == 0
        assert not list((tmp_path / "jobs").glob("task-*"))


def test_check_only_publication_budget_excludes_discarded_input(tmp_path):
    worker = tmp_path / "small_check_worker.py"
    payload = b'{"run_id":"small"}'
    worker.write_text(
        "import sys\nfrom pathlib import Path\n"
        "directory=Path(sys.argv[sys.argv.index('--output')+1])\n"
        f"(directory/'result.json').write_bytes({payload!r})\n",
        encoding="utf-8",
    )
    body = model_body()
    assert len(body) > len(payload)
    with ImportJobs(
        ReviewStore(),
        tmp_path / "jobs",
        worker_script=worker,
        output_files=("result.json",),
        result_handler=lambda outputs: {"run_id": json.loads(outputs["result.json"])["run_id"]},
        max_artifact_bytes=len(payload),
    ) as jobs:
        job = jobs.submit("public.ifc", body)
        result = jobs.wait(job["job_id"], timeout=10)
        assert result["state"] == "succeeded", result
        assert result["result"] == {"run_id": "small"}
        assert not list((tmp_path / "jobs").glob("*/input.ifc"))


def test_check_only_jobs_publish_context_bound_results_without_review_geometry(tmp_path):
    worker = tmp_path / "check_worker.py"
    worker.write_text(
        "import json,sys\nfrom pathlib import Path\n"
        "directory=Path(sys.argv[sys.argv.index('--output')+1])\n"
        "context=json.loads((directory/'context.json').read_text())\n"
        "(directory/'result.json').write_text(json.dumps(context))\n",
        encoding="utf-8",
    )
    published = []

    def publish(payloads):
        data = json.loads(payloads["result.json"])
        published.append(data)
        return {"run_id": data["run_id"]}

    store = ReviewStore()
    body = model_body()
    with ImportJobs(
        store, tmp_path / "jobs", worker_script=worker,
        output_files=("result.json",), result_handler=publish,
    ) as jobs:
        first = jobs.submit("public.ifc", body, context={"run_id": "run-1"})
        result = wait_for(jobs, first["job_id"], {"succeeded", "failed"})
        assert result["state"] == "succeeded", result
        assert result["result"] == {"run_id": "run-1"}
        assert result["review_id"] is None
        assert store.stats()["entries"] == 0
        second = jobs.submit("public.ifc", body, context={"run_id": "run-2"})
        result = wait_for(jobs, second["job_id"], {"succeeded", "failed"})
        assert result["result"] == {"run_id": "run-2"}
        assert len(published) == 2
        assert not list((tmp_path / "jobs").glob("*/context.json"))
