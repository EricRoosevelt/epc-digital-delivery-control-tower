"""A single import can atomically save its source only with explicit consent."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
import sqlite3
import threading
import time
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import ifcopenshell
import pytest

from doctor import serve
from doctor.enterprise_service import EnterpriseService
from doctor.import_jobs import ImportJobs
from internal.doctor_adapter.enterprise_library import EnterpriseLibrary
from internal.doctor_adapter.project_library import ProjectLibrary, ProjectLibraryError
from internal.doctor_adapter.review import ReviewStore
from tools.enterprise_rules_example import example_package


def public_body(name="Public source"):
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), Name=name)
    return model.to_string().encode()


def complete(jobs, body):
    job = jobs.submit("public.ifc", body)
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        result = jobs.wait(job["job_id"], 0.05)
        if result["state"] in {"succeeded", "failed"}:
            assert result["state"] == "succeeded", result
            return result["review_id"]
    raise AssertionError(jobs.get(job["job_id"]))


def test_successful_source_uses_bounded_spool_and_close_removes_it(tmp_path):
    body = public_body()
    jobs = ImportJobs(ReviewStore(), tmp_path / "jobs", max_artifacts=1)
    try:
        first = complete(jobs, body)
        assert jobs.source_available(first)
        assert jobs.source_payload(first) == body
        second = complete(jobs, public_body("second"))
        assert jobs.source_available(second)
        assert not jobs.source_available(first)
        with pytest.raises(KeyError):
            jobs.source_payload(first)
    finally:
        jobs.close()
    assert not list((tmp_path / "jobs").glob("task-*"))


def test_source_bytes_count_against_spool_byte_budget(tmp_path):
    body = public_body()
    with ImportJobs(ReviewStore(), tmp_path / "jobs") as jobs:
        identity = complete(jobs, body)
        directory = next((tmp_path / "jobs").glob("task-*"))
        json_size = sum(p.stat().st_size for p in directory.glob("*.json"))
        jobs.max_artifact_bytes = json_size + len(body) - 1
        with jobs._lock:
            jobs._trim()
        assert not jobs.source_available(identity)
        assert not list((tmp_path / "jobs").glob("task-*"))


def test_atomic_opt_in_source_and_revision_survive_restart(tmp_path):
    body, reviews = public_body(), ReviewStore()
    report = reviews.create("public.ifc", body)
    projects = ProjectLibrary(tmp_path, reviews)
    project = projects.create_project("Source consent")
    saved = projects.save_revision(
        project["project_id"], report["review_id"], retain_source=True, source_body=body
    )
    assert saved["revision"]["source_available"] is True
    restarted = ProjectLibrary(tmp_path, ReviewStore())
    enterprise = EnterpriseLibrary(restarted)
    revision_id = saved["revision"]["revision_id"]
    assert enterprise.source(revision_id) == body
    assert restarted.detail(project["project_id"])["models"][0]["revisions"][0][
        "source_available"
    ]


def test_default_does_not_persist_source_and_repeat_save_can_add_it_without_geometry(
    tmp_path, monkeypatch
):
    body, reviews = public_body(), ReviewStore()
    report = reviews.create("public.ifc", body)
    projects = ProjectLibrary(tmp_path, reviews)
    project = projects.create_project("Explicit source")
    saved = projects.save_revision(project["project_id"], report["review_id"])
    assert saved["revision"]["source_available"] is False
    enterprise = EnterpriseLibrary(projects)
    assert not enterprise.source_available(saved["revision"]["revision_id"])
    monkeypatch.setattr(
        reviews, "geometry_payload", lambda _: pytest.fail("Duplicate save read geometry")
    )
    retained = projects.save_revision(
        project["project_id"], report["review_id"], retain_source=True, source_body=body
    )
    assert retained["revision"]["revision_id"] == saved["revision"]["revision_id"]
    assert retained["revision"]["source_available"] is True
    assert (
        projects.save_revision(project["project_id"], report["review_id"], retain_source=True)[
            "revision"
        ]
        == retained["revision"]
    )
    assert projects.projects()[0]["revision_count"] == 1


@pytest.mark.parametrize("problem", ["hash", "source_write"])
def test_source_failure_cannot_leave_a_ghost_revision_or_model_slot(tmp_path, problem):
    body, reviews = public_body(), ReviewStore()
    report = reviews.create("public.ifc", body)
    projects = ProjectLibrary(tmp_path, reviews)
    EnterpriseLibrary(projects)
    project = projects.create_project("Atomic failure")
    if problem == "source_write":
        with sqlite3.connect(projects.path) as db:
            db.execute(
                "CREATE TRIGGER reject_source BEFORE INSERT ON enterprise_sources "
                "BEGIN SELECT RAISE(ABORT, 'simulated source write failure'); END"
            )
    with pytest.raises(ProjectLibraryError):
        projects.save_revision(
            project["project_id"],
            report["review_id"],
            retain_source=True,
            source_body=body + b" " if problem == "hash" else body,
        )
    assert projects.detail(project["project_id"])["models"] == []
    assert projects.projects()[0]["revision_count"] == 0
    with sqlite3.connect(projects.path) as db:
        assert db.execute("SELECT COUNT(*) FROM enterprise_sources").fetchone()[0] == 0


def test_concurrent_opt_in_is_idempotent_and_keeps_one_source(tmp_path):
    body, reviews = public_body(), ReviewStore()
    report = reviews.create("public.ifc", body)
    projects = ProjectLibrary(tmp_path, reviews)
    project = projects.create_project("Concurrent source consent")
    with ThreadPoolExecutor(max_workers=3) as pool:
        saved = list(
            pool.map(
                lambda _: projects.save_revision(
                    project["project_id"],
                    report["review_id"],
                    retain_source=True,
                    source_body=body,
                ),
                range(3),
            )
        )
    assert len({r["revision"]["revision_id"] for r in saved}) == 1
    with sqlite3.connect(projects.path) as db:
        assert db.execute("SELECT COUNT(*) FROM enterprise_sources").fetchone()[0] == 1


def request(base, path, body=None):
    payload = (
        body
        if isinstance(body, bytes)
        else json.dumps(body).encode()
        if body is not None
        else None
    )
    content_type = "application/octet-stream" if isinstance(body, bytes) else "application/json"
    with urlopen(
        Request(base + path, data=payload, headers={"Content-Type": content_type}),
        timeout=15,
    ) as response:
        return json.load(response)


@pytest.fixture
def http_retention(tmp_path):
    reviews = ReviewStore()
    projects = ProjectLibrary(tmp_path / "projects", reviews)
    service = EnterpriseService(EnterpriseLibrary(projects), reviews)
    with ImportJobs(reviews, tmp_path / "jobs") as jobs:
        serve.configure_import_loaders(jobs, projects)
        handler = serve.make_handler(
            lambda: None,
            review_factory=lambda: reviews,
            project_factory=lambda: projects,
            import_factory=lambda: jobs,
            enterprise_factory=lambda: service,
        )
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield "http://127.0.0.1:" + str(server.server_port), projects, jobs, reviews
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
            service.close()


def test_http_one_upload_save_is_directly_purpose_ready_without_second_source_upload(
    http_retention,
):
    base, projects, jobs, _ = http_retention
    body = public_body()
    identity = complete(jobs, body)
    status = request(base, "/api/review/source-status?review=" + identity)
    assert status == {
        "review_id": identity,
        "source_available": False,
        "retainable": True,
        "reason": "temporary",
    }
    project = request(base, "/api/projects", {"name": "One upload"})
    saved = request(
        base,
        "/api/projects/revisions",
        {"project_id": project["project_id"], "review_id": identity, "retain_source": True},
    )
    assert saved["revision"]["source_available"] is True
    assert EnterpriseLibrary(projects).source(saved["revision"]["revision_id"]) == body
    jobs.close()
    assert request(base, "/api/review/source-status?review=" + identity)["reason"] == "retained"
    repeated = request(
        base,
        "/api/projects/revisions",
        {"project_id": project["project_id"], "review_id": identity, "retain_source": True},
    )
    assert repeated["revision"] == saved["revision"]


def test_http_demo_expired_and_nonboolean_retention_are_explicit(http_retention):
    base, projects, jobs, reviews = http_retention
    demo = reviews.demo()
    status = request(base, "/api/review/source-status?review=" + demo["review_id"])
    assert status["reason"] == "federated_demo" and not status["retainable"]
    project = projects.create_project("Invalid consent")
    for value in (True, "true", 1):
        with pytest.raises(HTTPError) as failure:
            request(
                base,
                "/api/projects/revisions",
                {
                    "project_id": project["project_id"],
                    "review_id": demo["review_id"],
                    "retain_source": value,
                },
            )
        assert failure.value.code == 400
    identity = complete(jobs, public_body())
    jobs.close()
    assert request(base, "/api/review/source-status?review=" + identity)["reason"] == "expired"
    with pytest.raises(HTTPError) as failure:
        request(
            base,
            "/api/projects/revisions",
            {"project_id": project["project_id"], "review_id": identity, "retain_source": True},
        )
    assert failure.value.code == 400
    assert projects.projects()[0]["revision_count"] == 0


def test_one_http_upload_can_execute_purpose_after_atomic_save_and_restart(
    http_retention,
    monkeypatch,
):
    base, projects, jobs, _ = http_retention
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity(
        "IfcAirTerminal",
        GlobalId=ifcopenshell.guid.new(),
        Name="Public terminal",
        PredefinedType="DIFFUSER",
    )
    body = model.to_string().encode()
    report = request(base, "/api/review/models?filename=public.ifc", body)
    assert len(jobs.snapshot()["jobs"]) == 1
    project = request(base, "/api/projects", {"name": "Single upload Purpose"})
    saved = request(
        base,
        "/api/projects/revisions",
        {
            "project_id": project["project_id"],
            "review_id": report["review_id"],
            "retain_source": True,
        },
    )
    preview = request(
        base,
        "/api/projects/rules/preview?project=" + project["project_id"] + "&filename=public.zip",
        example_package(),
    )
    rule = request(
        base,
        "/api/projects/rules/confirm",
        {
            "project_id": project["project_id"],
            "preview_id": preview["preview_id"],
            "confirmed_by": "Public reviewer",
            "responsible_team": "Engineering",
        },
    )
    jobs.close()
    restarted = ProjectLibrary(projects.root, ReviewStore())
    monkeypatch.setattr(
        restarted.reviews,
        "geometry_payload",
        lambda _: pytest.fail("Rule execution reopened geometry"),
    )
    enterprise = EnterpriseLibrary(restarted)
    with closing(EnterpriseService(enterprise, restarted.reviews)) as service:
        job = service.submit(
            {
                "project_id": project["project_id"],
                "revision_id": saved["revision"]["revision_id"],
                "rule_revision_id": rule["rule_revision_id"],
                "purpose_id": "terminal-schedule",
                "scope": {"kind": "all"},
            }
        )
        deadline = time.monotonic() + 15
        while job["state"] not in {"succeeded", "failed"}:
            assert time.monotonic() < deadline, job
            job = service.jobs.wait(job["job_id"], 0.05)
        assert job["state"] == "succeeded", job
        assert enterprise.run(job["result"]["run_id"])["conclusion"]["status"] == "READY"
        assert not list(service.jobs.root.glob("*/input.ifc"))
    assert enterprise.source(saved["revision"]["revision_id"]) == body
    assert restarted.reviews.stats()["geometries"] == 0


def test_reusing_retained_bytes_for_another_project_still_needs_explicit_consent(tmp_path):
    body, reviews = public_body(), ReviewStore()
    report = reviews.create("public.ifc", body)
    projects = ProjectLibrary(tmp_path, reviews)
    first, other = projects.create_project("First"), projects.create_project("Other")
    cache_bytes = reviews.stats()["bytes"]
    projects.save_revision(
        first["project_id"], report["review_id"], retain_source=True, source_body=body
    )
    unlinked = projects.save_revision(other["project_id"], report["review_id"])
    assert not unlinked["revision"]["source_available"]
    linked = projects.save_revision(
        other["project_id"], report["review_id"], retain_source=True
    )
    assert linked["revision"]["source_available"]
    assert linked["revision"]["revision_id"] == unlinked["revision"]["revision_id"]
    assert reviews.stats()["bytes"] == cache_bytes  # No source bytes enter the review LRU.
