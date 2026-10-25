"""Import supervision must stop work, retain old results and publish only complete output."""

import json
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
        "while True: time.sleep(10)\n",
        encoding="utf-8",
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
        assert not list((tmp_path / "jobs").glob("*/input.ifc"))


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

