"""Local project persistence keeps model revision evidence separate from follow-up state."""

import importlib.util
import json
import sqlite3
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import ifcopenshell
import pytest

from helpers import PROJECT_ROOT
from internal.doctor_adapter.project_library import ProjectLibrary, ProjectLibraryError
from internal.doctor_adapter.review import ReviewStore


def make_review(store, name="model.ifc", *, guid=None, predefined="NOTDEFINED"):
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity(
        "IfcAirTerminal",
        GlobalId=guid or ifcopenshell.guid.new(),
        Name="风口",
        PredefinedType=predefined,
    )
    return store.create(name, model.to_string().encode())


def test_projects_and_real_geometry_reopen_after_server_restart(tmp_path):
    reviews = ReviewStore()
    report = reviews.demo()
    library = ProjectLibrary(tmp_path, reviews)
    project = library.create_project("机电协调 / 本地项目")
    saved = library.save_revision(
        project["project_id"], report["review_id"], model_name="公共联邦模型", label="首次审查"
    )
    old_geometry = reviews.geometry(report["review_id"])
    new_reviews = ReviewStore()
    reopened = ProjectLibrary(tmp_path, new_reviews)
    revision = reopened.revision(saved["revision"]["revision_id"])
    assert revision["report"] == report
    assert new_reviews.get(report["review_id"]) == report
    assert new_reviews.geometry(report["review_id"]) == old_geometry
    assert reopened.projects()[0]["revision_count"] == 1
    assert reopened.detail(project["project_id"])["models"][0]["name"] == "公共联邦模型"
    assert list(tmp_path.iterdir()) == [library.path]


def test_model_slot_survives_filename_content_and_label_changes(tmp_path):
    reviews = ReviewStore()
    library = ProjectLibrary(tmp_path, reviews)
    project = library.create_project("Project")
    guid = ifcopenshell.guid.new()
    first = make_review(reviews, "v1.ifc", guid=guid)
    second = make_review(reviews, "renamed-v2.ifc", guid=guid, predefined="DIFFUSER")
    a = library.save_revision(project["project_id"], first["review_id"], model_name="HVAC")
    b = library.save_revision(
        project["project_id"],
        second["review_id"],
        model_id=a["revision"]["model_id"],
        label="已重新导出",
    )
    assert a["revision"]["model_id"] == b["revision"]["model_id"]
    assert a["revision"]["revision_id"] != b["revision"]["revision_id"]
    assert b["revision"]["number"] == 2
    assert b["revision"]["filename"] == "renamed-v2.ifc"
    detail = library.detail(project["project_id"])
    assert len(detail["models"]) == 1
    assert detail["models"][0]["name"] == "HVAC"
    assert len(detail["models"][0]["revisions"]) == 2


def test_duplicate_save_reuses_revision_and_does_not_create_another_slot(tmp_path):
    reviews = ReviewStore()
    library = ProjectLibrary(tmp_path, reviews)
    project = library.create_project("Project")
    report = make_review(reviews)
    a = library.save_revision(project["project_id"], report["review_id"])
    b = library.save_revision(
        project["project_id"],
        report["review_id"],
        model_id=a["revision"]["model_id"],
        label="new label",
    )
    c = library.save_revision(project["project_id"], report["review_id"])
    assert a["revision"] == b["revision"] == c["revision"]
    assert library.projects()[0]["model_count"] == 1
    assert library.projects()[0]["revision_count"] == 1


def test_ready_for_recheck_is_saved_but_never_rewrites_check_status(tmp_path):
    reviews = ReviewStore()
    library = ProjectLibrary(tmp_path, reviews)
    project = library.create_project("Project")
    report = make_review(reviews)
    saved = library.save_revision(project["project_id"], report["review_id"])
    revision_id = saved["revision"]["revision_id"]
    finding = next(f for f in report["findings"] if f["rule_id"] == "PV-001")
    followup = library.update_followup(
        revision_id,
        finding["finding_id"],
        status="ready_for_recheck",
        owner="机电工程师",
        note="已在源软件修改，待复查新 IFC。\n尚未验证。",
    )
    reopened = ProjectLibrary(tmp_path, ReviewStore()).revision(revision_id)
    assert reopened["followups"] == [followup]
    assert reopened["report"] == report
    assert finding["status"] == "FAIL"
    assert reviews.get(report["review_id"]) == report
    assert followup["owner"] == "机电工程师"


def test_revision_and_finding_scope_is_checked_before_followup_write(tmp_path):
    reviews = ReviewStore()
    library = ProjectLibrary(tmp_path, reviews)
    a = library.create_project("A")
    b = library.create_project("B")
    report = make_review(reviews)
    saved = library.save_revision(a["project_id"], report["review_id"])
    revision = saved["revision"]
    with pytest.raises(ProjectLibraryError):
        library.save_revision(
            b["project_id"], report["review_id"], model_id=revision["model_id"]
        )
    with pytest.raises(KeyError):
        library.update_followup(revision["revision_id"], "not-a-finding", status="open")
    with pytest.raises(ProjectLibraryError):
        library.update_followup(
            revision["revision_id"], report["findings"][0]["finding_id"], status="PASS"
        )
    assert library.revision(revision["revision_id"])["followups"] == []


@pytest.mark.parametrize(
    "operation",
    [
        lambda lib: lib.detail("missing"),
        lambda lib: lib.revision("missing"),
        lambda lib: lib.save_revision("missing", "missing"),
    ],
)
def test_stale_ids_raise_lookup_errors(tmp_path, operation):
    with pytest.raises(KeyError):
        operation(ProjectLibrary(tmp_path, ReviewStore()))


@pytest.mark.parametrize("name", ["", "   ", 12, "x" * 161])
def test_bad_project_names_are_input_errors(tmp_path, name):
    with pytest.raises(ProjectLibraryError):
        ProjectLibrary(tmp_path, ReviewStore()).create_project(name)


def test_corrupt_snapshot_is_reported_without_overwriting_it(tmp_path):
    reviews = ReviewStore()
    library = ProjectLibrary(tmp_path, reviews)
    project = library.create_project("Project")
    report = make_review(reviews)
    revision = library.save_revision(project["project_id"], report["review_id"])["revision"]
    with sqlite3.connect(library.path) as db:
        db.execute(
            "UPDATE revisions SET report_json = ? WHERE revision_id = ?",
            ("not json", revision["revision_id"]),
        )
    with pytest.raises(ProjectLibraryError, match="saved review"):
        library.revision(revision["revision_id"])
    with sqlite3.connect(library.path) as db:
        assert db.execute("SELECT report_json FROM revisions").fetchone()[0] == "not json"


def test_review_admit_restores_evidence_and_does_not_alias_callers():
    original = ReviewStore()
    report = original.demo()
    geometry = original.geometry(report["review_id"])
    restored = ReviewStore()
    restored.admit(report, geometry)
    report["elements"].clear()
    geometry["meshes"].clear()
    assert restored.get(report["review_id"])["elements"]
    assert restored.geometry(report["review_id"])["meshes"]
    with pytest.raises(ValueError):
        restored.admit(restored.get(report["review_id"]), {"review_id": "wrong"})


@pytest.fixture
def project_http(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "project_http", PROJECT_ROOT / "doctor/serve.py"
    )
    serve = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(serve)
    reviews = ReviewStore()
    report = make_review(reviews)
    library = ProjectLibrary(tmp_path, reviews)
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        serve.make_handler(
            lambda: None,
            review_factory=lambda: reviews,
            project_factory=lambda: library,
        ),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}", report
    server.shutdown()
    server.server_close()
    thread.join()


def http_json(base, path, body=None):
    request = Request(
        base + path,
        data=None if body is None else json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request) as response:
        return json.load(response)


def test_http_projects_save_reopen_followup_and_stale_errors(project_http):
    base, report = project_http
    project = http_json(base, "/api/projects", {"name": "HTTP 项目"})
    assert http_json(base, "/api/projects")["projects"][0] == project
    saved = http_json(
        base,
        "/api/projects/revisions",
        {
            "project_id": project["project_id"],
            "review_id": report["review_id"],
        },
    )
    revision_id = saved["revision"]["revision_id"]
    answer = http_json(base, "/api/projects/revision?revision=" + revision_id)
    assert answer == saved
    followup = http_json(
        base,
        "/api/projects/followup",
        {
            "revision_id": revision_id,
            "finding_id": report["findings"][0]["finding_id"],
            "status": "in_progress",
            "owner": "张工",
            "note": "核对源对象映射",
        },
    )
    assert followup["status"] == "in_progress"
    assert http_json(base, "/api/projects/revision?revision=" + revision_id)["followups"]
    for path, body, status in [
        ("/api/projects/revision?revision=stale", None, 404),
        ("/api/projects", {"name": ""}, 400),
        ("/api/projects", [], 400),
        ("/api/projects/unknown", None, 404),
    ]:
        with pytest.raises(HTTPError) as failure:
            http_json(base, path, body)
        assert failure.value.code == status
        assert json.load(failure.value)["error"]


def test_revision_insert_failure_rolls_back_its_new_model_slot(tmp_path):
    reviews = ReviewStore()
    library = ProjectLibrary(tmp_path, reviews)
    project = library.create_project("Transaction")
    report = make_review(reviews)
    with sqlite3.connect(library.path) as db:
        db.execute(
            "CREATE TRIGGER reject_revision BEFORE INSERT ON revisions "
            "BEGIN SELECT RAISE(ABORT, 'simulated write failure'); END"
        )
    with pytest.raises(ProjectLibraryError):
        library.save_revision(project["project_id"], report["review_id"])
    assert library.detail(project["project_id"])["models"] == []
    assert library.projects()[0]["revision_count"] == 0


def test_simultaneous_first_save_does_not_create_duplicate_slots(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    reviews = ReviewStore()
    library = ProjectLibrary(tmp_path, reviews)
    project = library.create_project("Double save")
    report = make_review(reviews)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(
            pool.map(
                lambda _: library.save_revision(project["project_id"], report["review_id"]),
                range(4),
            )
        )
    assert len({item["revision"]["revision_id"] for item in results}) == 1
    assert library.projects()[0]["model_count"] == 1
    assert library.projects()[0]["revision_count"] == 1


def test_followups_are_scoped_to_revision_even_when_findings_have_the_same_id(tmp_path):
    reviews = ReviewStore()
    library = ProjectLibrary(tmp_path, reviews)
    report = make_review(reviews)
    project_a, project_b = library.create_project("A"), library.create_project("B")
    a = library.save_revision(project_a["project_id"], report["review_id"])["revision"]
    b = library.save_revision(project_b["project_id"], report["review_id"])["revision"]
    library.update_followup(
        a["revision_id"],
        report["findings"][0]["finding_id"],
        status="ready_for_recheck",
        note="A only",
    )
    assert library.revision(a["revision_id"])["followups"]
    assert library.revision(b["revision_id"])["followups"] == []
    with pytest.raises(ProjectLibraryError):
        library.compare(a["revision_id"], b["revision_id"])


def test_corrupt_sqlite_is_a_useful_error_and_is_never_replaced(tmp_path):
    path = tmp_path / "library.sqlite3"
    path.write_bytes(b"not a sqlite database")
    with pytest.raises(ProjectLibraryError, match="SQLite"):
        ProjectLibrary(tmp_path, ReviewStore())
    assert path.read_bytes() == b"not a sqlite database"


def test_saved_geometry_identity_mismatch_does_not_poison_session(tmp_path):
    reviews = ReviewStore()
    library = ProjectLibrary(tmp_path, reviews)
    report = make_review(reviews)
    project = library.create_project("Corrupt geometry")
    saved = library.save_revision(project["project_id"], report["review_id"])
    with sqlite3.connect(library.path) as db:
        db.execute(
            "UPDATE revisions SET geometry_json=?",
            (
                json.dumps(
                    {
                        "review_id": "wrong",
                        "meshes": [],
                        "unavailable": [],
                    }
                ),
            ),
        )
    restarted = ReviewStore()
    reopened = ProjectLibrary(tmp_path, restarted).revision(saved["revision"]["revision_id"])
    assert reopened["report"] == report  # Report-only reopening does not touch bad geometry.
    with pytest.raises(ProjectLibraryError, match="saved review geometry"):
        restarted.geometry_payload(report["review_id"])
    assert restarted.get(report["review_id"]) == report


def test_saved_recheck_resolves_only_when_new_ifc_passes(tmp_path):
    from doctor.advice import AdviceService

    reviews = ReviewStore()
    library = ProjectLibrary(tmp_path, reviews)
    project = library.create_project("Round trip")
    guid = ifcopenshell.guid.new()
    first = make_review(reviews, "before.ifc", guid=guid)
    a = library.save_revision(project["project_id"], first["review_id"])["revision"]
    finding = next(f for f in first["findings"] if f["rule_id"] == "PV-001")
    library.update_followup(a["revision_id"], finding["finding_id"], status="ready_for_recheck")
    second = make_review(reviews, "renamed-after.ifc", guid=guid, predefined="DIFFUSER")
    b = library.save_revision(
        project["project_id"], second["review_id"], model_id=a["model_id"]
    )["revision"]
    restarted_reviews = ReviewStore()
    restarted = ProjectLibrary(tmp_path, restarted_reviews)
    comparison = restarted.compare(a["revision_id"], b["revision_id"])
    pv = next(item for item in comparison["rows"] if item["rule_id"] == "PV-001")
    assert pv["change"] == "resolved"
    assert pv["before_status"] == "FAIL" and pv["after_status"] == "PASS"
    assert restarted.revision(b["revision_id"])["followups"] == []
    assert restarted.revision(a["revision_id"])["followups"][0]["status"] == "ready_for_recheck"
    answer = AdviceService(restarted_reviews, environ={}).explain(
        first["review_id"], finding["finding_id"], use_ai=False
    )
    assert answer["finding_id"] == finding["finding_id"]
    assert answer["mode"] == "guidance"
    assert restarted_reviews.get(first["review_id"]) == first


def test_runtime_review_identity_changes_with_rule_predicate_version(monkeypatch):
    from internal.doctor_adapter import review_rules

    source = ifcopenshell.file(schema="IFC4")
    source.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new())
    body = source.to_string().encode()
    old_store = ReviewStore()
    original = old_store.create("same.ifc", body)
    next_version = str(int(review_rules.PREDICATE_VERSION) + 1)
    monkeypatch.setattr(review_rules, "PREDICATE_VERSION", next_version)
    new_store = ReviewStore()
    current = new_store.create("same.ifc", body)
    assert original["source"]["sha256"] == current["source"]["sha256"]
    assert original["review_id"] != current["review_id"]
    new_store.admit(original, old_store.geometry(original["review_id"]))
    assert new_store.get(current["review_id"]) == current
    assert new_store.get(original["review_id"]) == original


def test_http_revision_comparison_uses_saved_slot_and_new_ifc_evidence(project_http):
    base, before = project_http
    project = http_json(base, "/api/projects", {"name": "HTTP Recheck"})
    a = http_json(
        base,
        "/api/projects/revisions",
        {
            "project_id": project["project_id"],
            "review_id": before["review_id"],
        },
    )["revision"]
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity(
        "IfcAirTerminal",
        GlobalId=before["elements"][0]["global_id"],
        Name="风口",
        PredefinedType="DIFFUSER",
    )
    request = Request(
        base + "/api/review/models?filename=renamed-after.ifc",
        data=model.to_string().encode(),
        headers={"Content-Type": "application/octet-stream"},
    )
    with urlopen(request) as response:
        after = json.load(response)
    b = http_json(
        base,
        "/api/projects/revisions",
        {
            "project_id": project["project_id"],
            "model_id": a["model_id"],
            "review_id": after["review_id"],
            "label": "复查导出",
        },
    )["revision"]
    comparison = http_json(
        base, "/api/projects/compare?before=" + a["revision_id"] + "&after=" + b["revision_id"]
    )
    assert comparison["summary"]["errors"]["resolved"] == 1
    assert comparison["before_revision"]["revision_id"] == a["revision_id"]
    assert comparison["after_revision"]["revision_id"] == b["revision_id"]
    detail = http_json(base, "/api/projects/detail?project=" + project["project_id"])
    assert [r["number"] for r in detail["models"][0]["revisions"]] == [2, 1]
    other_project = http_json(base, "/api/projects", {"name": "Other"})
    c = http_json(
        base,
        "/api/projects/revisions",
        {
            "project_id": other_project["project_id"],
            "review_id": after["review_id"],
        },
    )["revision"]
    with pytest.raises(HTTPError) as mismatch:
        http_json(
            base,
            "/api/projects/compare?before=" + a["revision_id"] + "&after=" + c["revision_id"],
        )
    assert mismatch.value.code == 400
    assert json.load(mismatch.value)["error"]
