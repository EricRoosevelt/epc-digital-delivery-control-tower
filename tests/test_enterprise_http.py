"""Real package upload, native child checks, purpose evidence, and restart recheck."""

from contextlib import contextmanager
from http.server import ThreadingHTTPServer
import json
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import ifcopenshell
import pytest

from doctor.enterprise_service import EnterpriseService
from doctor.serve import make_handler
from internal.doctor_adapter.enterprise_library import EnterpriseLibrary
from internal.doctor_adapter.project_library import ProjectLibrary
from internal.doctor_adapter.review import ReviewStore
from tools.enterprise_rules_example import example_package


def call(base, path, body=None):
    headers = {}
    if isinstance(body, dict):
        body = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    elif body is not None:
        headers["Content-Type"] = "application/octet-stream"
    with urlopen(Request(base + path, data=body, headers=headers), timeout=8) as response:
        return json.load(response)


def source(guid, predefined="DIFFUSER"):
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcAirTerminal", GlobalId=guid, Name="Public terminal",
                        PredefinedType=predefined)
    return model.to_string().encode()


@pytest.fixture
def runtime(tmp_path):
    reviews = ReviewStore()
    projects = ProjectLibrary(tmp_path, reviews)
    library = EnterpriseLibrary(projects)
    service = EnterpriseService(library, reviews)
    project = projects.create_project("Public purpose closure")
    guid = ifcopenshell.guid.new()
    body = source(guid)
    report = reviews.create("public.ifc", body)
    saved = projects.save_revision(project["project_id"], report["review_id"])
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(
        lambda: None, review_factory=lambda: reviews, project_factory=lambda: projects,
        enterprise_factory=lambda: service,
    ))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield {"base": f"http://127.0.0.1:{server.server_port}", "service": service,
           "project": project, "saved": saved, "report": report, "body": body,
           "guid": guid, "root": tmp_path}
    server.shutdown()
    server.server_close()
    thread.join()
    service.close()


def adopted(rt):
    base, project = rt["base"], rt["project"]["project_id"]
    preview = call(base, f"/api/projects/rules/preview?project={project}&filename=public.zip",
                   example_package())
    assert call(base, f"/api/projects/rules?project={project}")["rule_revisions"] == []
    rule = call(base, "/api/projects/rules/confirm", {
        "project_id": project, "preview_id": preview["preview_id"],
        "confirmed_by": "User reviewer", "responsible_team": "Public design team",
    })
    return rule


def completed(rt, rule, purpose="terminal-schedule", **options):
    revision_id = options.pop("revision_id", rt["saved"]["revision"]["revision_id"])
    job = call(rt["base"], "/api/projects/purpose/runs", {
        "project_id": rt["project"]["project_id"], "revision_id": revision_id,
        "rule_revision_id": rule["rule_revision_id"], "purpose_id": purpose,
        "scope": {"kind": "all"}, **options,
    })
    deadline = time.monotonic() + 20
    while job["state"] not in {"succeeded", "failed", "cancelled", "timed_out"}:
        assert time.monotonic() < deadline, job
        time.sleep(.05)
        job = call(rt["base"], "/api/projects/purpose/jobs?job=" + job["job_id"])
    assert job["state"] == "succeeded", job
    return call(rt["base"], "/api/projects/purpose/run?run=" + job["result"]["run_id"])


def attach(rt, revision_id=None, body=None):
    revision_id = revision_id or rt["saved"]["revision"]["revision_id"]
    return call(rt["base"], f"/api/projects/source?revision={revision_id}&filename=public.ifc",
                body or rt["body"])


def test_real_worker_uses_confirmed_rules_and_requires_exact_source(runtime):
    rt = runtime
    rule = adopted(rt)
    with pytest.raises(HTTPError) as error:
        completed(rt, rule)
    assert error.value.code == 400
    with pytest.raises(HTTPError) as error:
        attach(rt, body=rt["body"] + b" ")
    assert error.value.code == 400
    attach(rt)
    run = completed(rt, rule, job_id="public-job-retry")
    assert run["conclusion"]["status"] == "READY", run
    assert run["record"] and run["assessment_digest"]
    assert run["evaluation"]["elements"][0]["review_element_key"] == \
        rt["report"]["elements"][0]["element_key"]
    assert rt["service"].library.projects.reviews.get(rt["report"]["review_id"]) == rt["report"]
    repeated = completed(rt, rule, job_id="public-job-retry")
    assert repeated["run_id"] == run["run_id"]


def test_manual_evidence_creates_successor_and_restarts_without_changing_old_run(runtime):
    rt = runtime
    rule = adopted(rt)
    attach(rt)
    first = completed(rt, rule, "tender-submission")
    assert first["conclusion"]["status"] == "UNKNOWN", first
    evidence = next(item for item in first["evidence_requests"]
                    if item["execution"] == "manual")
    call(rt["base"], "/api/projects/purpose/determinations", {
        "run_id": first["run_id"], "evidence_id": evidence["evidence_id"],
        "subject_keys": evidence["subject_keys"], "outcome": "confirmed",
        "method_id": evidence["method_id"], "context_digest": evidence["context_digest"],
        "determiner": "Public reviewer", "reference": "Public drawing revision A",
        "basis": "Checked source mapping against the cited view.",
    })
    second = completed(rt, rule, "tender-submission", prior_run_id=first["run_id"])
    assert second["conclusion"]["status"] == "READY", second
    assert second["record"]["successor"]["kind"] == "recheck"
    library = EnterpriseLibrary(ProjectLibrary(rt["root"], ReviewStore()))
    assert library.source_available(rt["saved"]["revision"]["revision_id"])
    assert library.run(first["run_id"])["conclusion"]["status"] == "UNKNOWN"
    with _service(library) as svc:
        job = svc.submit({"project_id": rt["project"]["project_id"],
            "revision_id": rt["saved"]["revision"]["revision_id"],
            "rule_revision_id": rule["rule_revision_id"], "purpose_id": "tender-submission",
            "scope": {"kind": "all"}, "prior_run_id": second["run_id"]})
        deadline = time.monotonic() + 20
        while job["state"] not in {"succeeded", "failed"}:
            assert time.monotonic() < deadline, job
            job = svc.jobs.wait(job["job_id"])
        assert job["state"] == "succeeded", job
        assert library.run(job["result"]["run_id"])["conclusion"]["status"] == "READY"


@contextmanager
def _service(library):
    service = EnterpriseService(library, library.projects.reviews)
    try:
        yield service
    finally:
        service.close()


def test_model_change_is_rechecked_in_same_slot_without_geometry_regeneration(runtime):
    rt = runtime
    rule = adopted(rt)
    attach(rt)
    first = completed(rt, rule)
    body = source(rt["guid"], "NOTDEFINED")
    projects = rt["service"].library.projects
    report = projects.reviews.create("new.ifc", body)
    revision = projects.save_revision(rt["project"]["project_id"], report["review_id"],
                                      model_id=rt["saved"]["revision"]["model_id"])
    attach(rt, revision["revision"]["revision_id"], body)
    second = completed(rt, rule, revision_id=revision["revision"]["revision_id"],
                       prior_run_id=first["run_id"])
    assert second["conclusion"]["status"] == "BLOCKED", second
    assert first["evaluation"]["elements"][0]["element_key"] == \
        second["evaluation"]["elements"][0]["element_key"]
    assert second["blockers"][0]["review_element_key"] == report["elements"][0]["element_key"]
    assert second["record"]["successor"]["kind"] == "recheck"


def test_conflicting_required_evidence_cannot_be_previewed_or_adopted(runtime):
    from internal.doctor_adapter.enterprise_package import digest
    from internal.doctor_adapter.enterprise_rules import parse_package
    from test_enterprise_rules import package_bytes, manifest

    package = parse_package(package_bytes(), "public.zip")
    document = manifest()
    document["purposes"][0]["evidence_requirements"] = [
        {
            "evidence_id": "check-" + digest(package.checks[0]["requirement_key"])[:16],
            "title": "Independent review",
            "acceptance": "Review evidence",
            "execution": "manual",
            "method_id": "review",
            "method_description": "Review",
        }
    ]
    project = runtime["project"]["project_id"]
    with pytest.raises(HTTPError) as error:
        call(
            runtime["base"],
            f"/api/projects/rules/preview?project={project}&filename=public.zip",
            package_bytes(declaration=document),
        )
    assert error.value.code == 400
    assert "conflicts" in json.load(error.value)["error"]
    catalog = call(runtime["base"], f"/api/projects/rules?project={project}")
    assert not catalog["previews"] and not catalog["rule_revisions"]


def test_chinese_brief_download_uses_the_recorded_chinese_next_step(runtime):
    rt = runtime
    rule = adopted(rt)
    attach(rt)
    run = completed(rt, rule, "tender-submission")
    manual = next(block for block in run["blockers"] if block["kind"] == "manual")
    with urlopen(
        rt["base"] + "/api/projects/purpose/brief?run=" + run["run_id"] + "&language=zh",
        timeout=8,
    ) as response:
        brief = response.read().decode("utf8")
    assert manual["next_action_zh"] in brief
    assert manual["next_action"] not in brief
