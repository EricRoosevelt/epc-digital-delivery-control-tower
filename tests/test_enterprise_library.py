"""Enterprise adoption, source attachment and immutable purpose history."""

import hashlib
import json
from types import SimpleNamespace

import ifcopenshell
import pytest

from internal.doctor_adapter import enterprise_library as module
from internal.doctor_adapter.enterprise_library import EnterpriseLibrary
from internal.doctor_adapter.project_library import ProjectLibrary, ProjectLibraryError
from internal.doctor_adapter.review import ReviewStore


def source_bytes():
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), Name="Public wall")
    return model.to_string().encode()


@pytest.fixture
def library(tmp_path, monkeypatch):
    reviews = ReviewStore()
    projects = ProjectLibrary(tmp_path, reviews)
    project = projects.create_project("Public enterprise project")
    body = source_bytes()
    report = reviews.create("public.ifc", body)
    saved = projects.save_revision(project["project_id"], report["review_id"])
    enterprise = EnterpriseLibrary(projects)

    def parse(body, filename):
        sha = hashlib.sha256(body).hexdigest()
        preview = {
            "package_id": "public-rules", "title": "Public", "version": "1.0.0",
            "source": {"organization": "Public example", "reference": "test"},
            "source_sha256": sha, "rules": [], "unsupported": [], "can_confirm": True,
            "purposes": [{"purpose_id": "internal", "title": "Internal"}],
        }
        return SimpleNamespace(preview=lambda: preview, source_sha256=sha,
                               manifest={"purposes": preview["purposes"]})

    monkeypatch.setattr(module, "_parse", parse)
    return enterprise, projects, project, saved["revision"], report, body


def adopt(library, body=b"public zip"):
    enterprise, _, project, *_ = library
    preview = enterprise.preview(project["project_id"], "public.zip", body)
    rule = enterprise.confirm(project["project_id"], preview["preview_id"],
                              confirmed_by="Reviewer", responsible_team="Engineering")
    return preview, rule


def test_upload_is_preview_until_explicit_project_confirmation(library):
    enterprise, _, project, *_ = library
    preview = enterprise.preview(project["project_id"], "public.zip", b"public zip")
    assert enterprise.rules(project["project_id"])["rule_revisions"] == []
    with pytest.raises(ProjectLibraryError, match="required"):
        enterprise.confirm(project["project_id"], preview["preview_id"],
                           confirmed_by="", responsible_team="")
    rule = enterprise.confirm(project["project_id"], preview["preview_id"],
                              confirmed_by="Reviewer", responsible_team="Engineering")
    assert rule["confirmed_by"] == "Reviewer"
    assert rule["responsible_team"] == "Engineering"
    assert enterprise.rule(rule["rule_revision_id"])["source_sha256"] == \
        preview["source_sha256"]


def test_reused_declared_version_retains_both_content_revisions(library):
    enterprise, _, project, *_ = library
    _, first = adopt(library)
    preview, second = adopt(library, b"public changed zip")
    assert preview["version_reused"]
    assert first["rule_revision_id"] != second["rule_revision_id"]
    assert first["source_sha256"] != second["source_sha256"]
    assert len(enterprise.rules(project["project_id"])["rule_revisions"]) == 2


def test_exact_source_attachment_is_explicit_and_survives_restart(library, monkeypatch):
    enterprise, projects, _, revision, report, body = library
    assert not enterprise.source_available(revision["revision_id"])
    monkeypatch.setattr(projects.reviews, "geometry_payload", lambda _: pytest.fail(
        "Source attachment and inspection must not reload geometry"
    ))
    with pytest.raises(ProjectLibraryError, match="SHA|hash|match"):
        enterprise.attach_source(revision["revision_id"], "wrong.ifc", body + b" ")
    attached = enterprise.attach_source(revision["revision_id"], "public.ifc", body)
    assert attached["source_sha256"] == report["source"]["sha256"]
    restarted = EnterpriseLibrary(ProjectLibrary(projects.root, ReviewStore()))
    assert restarted.source(revision["revision_id"]) == body


def test_runs_are_immutable_and_other_project_cannot_adopt_preview(library):
    enterprise, projects, project, revision, *_ = library
    preview, rule = adopt(library)
    other = projects.create_project("Other project")
    with pytest.raises(ProjectLibraryError, match="project"):
        enterprise.confirm(other["project_id"], preview["preview_id"],
                           confirmed_by="Reviewer", responsible_team="Engineering")
    run = {
        "run_id": "purpose-public-run", "project_id": project["project_id"],
        "revision_id": revision["revision_id"],
        "rule_revision_id": rule["rule_revision_id"], "purpose_id": "internal",
        "scope": {"kind": "all"}, "conclusion": {"status": "UNKNOWN"},
        "evidence_requests": [{"evidence_id": "evidence", "execution": "manual",
                               "method_id": "document-review", "context_digest": "basis",
                               "subject_keys": ["object-a"],
                               "outcomes": ["confirmed", "unmet", "not-yet-confirmed"]}],
    }
    enterprise.publish_run(run)
    assert enterprise.publish_run(run) == {"run_id": run["run_id"]}
    with pytest.raises(ProjectLibraryError, match="immutable|different"):
        enterprise.publish_run({**run, "conclusion": {"status": "READY"}})
    record = enterprise.determination(
        run["run_id"], "evidence", subject_keys=["object-a"], outcome="confirmed",
        method_id="document-review", determiner="Engineer", basis="Checked drawing",
        reference="drawing-A revision 2", context_digest="basis",
    )
    assert record["context_digest"] == "basis"
    assert enterprise.run(run["run_id"])["conclusion"]["status"] == "UNKNOWN"
    assert len(enterprise.judgments(project["project_id"], revision["revision_id"],
                                   rule["rule_revision_id"], "internal")) == 1
    with pytest.raises(ProjectLibraryError, match="context"):
        enterprise.determination(
            run["run_id"], "evidence", subject_keys=["object-a"], outcome="confirmed",
            method_id="document-review", determiner="Engineer", basis="Checked drawing",
            reference="drawing-A", context_digest="forged",
        )


@pytest.mark.parametrize("invalid", ["evidence_collision", "whitespace"])
def test_current_confirmation_revalidates_persisted_legacy_preview_bytes(library, monkeypatch,
                                                                       invalid):
    from internal.doctor_adapter.enterprise_package import digest
    from internal.doctor_adapter.enterprise_rules import parse_package
    from test_enterprise_rules import package_bytes, manifest

    enterprise, projects, project, *_ = library
    original = parse_package(package_bytes(), "public.zip")
    declaration = manifest()
    if invalid == "evidence_collision":
        declaration["purposes"][0]["evidence_requirements"] = [{
            "evidence_id": "check-" + digest(original.checks[0]["requirement_key"])[:16],
            "title": "Independent review", "acceptance": "Evidence required",
            "execution": "manual", "method_id": "review", "method_description": "Review",
        }]
    else:
        declaration["purposes"][0]["purpose_id"] = " schedule "
    body = package_bytes(declaration=declaration)
    snapshot = original.preview()
    snapshot.update(project_id=project["project_id"], preview_id="preview-legacy",
                    filename="legacy.zip", created_at="2026-10-26T00:00:00Z",
                    can_confirm=True, source_sha256=hashlib.sha256(body).hexdigest(),
                    manifest=declaration, purposes=declaration["purposes"])
    serialized = json.dumps(snapshot, ensure_ascii=False)
    with projects._db() as db:
        db.execute("INSERT INTO enterprise_previews VALUES(?,?,?,?,?,?)", (
            snapshot["preview_id"], project["project_id"], snapshot["created_at"],
            "legacy.zip", body, serialized,
        ))
    monkeypatch.setattr(module, "_parse", parse_package)
    with pytest.raises(ProjectLibraryError, match="validation|preview|package"):
        enterprise.confirm(project["project_id"], snapshot["preview_id"],
                           confirmed_by="User", responsible_team="Reviewer")
    with projects._db() as db:
        assert db.execute("SELECT COUNT(*) FROM enterprise_rules").fetchone()[0] == 0
        stored = db.execute("SELECT package,preview_json FROM enterprise_previews "
                            "WHERE preview_id=?", (snapshot["preview_id"],)).fetchone()
    assert bytes(stored["package"]) == body
    assert stored["preview_json"] == serialized


def test_current_validation_keeps_the_reviewed_preview_snapshot(library, monkeypatch):
    from internal.doctor_adapter.enterprise_rules import parse_package
    from test_enterprise_rules import package_bytes

    enterprise, _, project, *_ = library
    monkeypatch.setattr(module, "_parse", parse_package)
    body = package_bytes()
    preview = enterprise.preview(project["project_id"], "public.zip", body)
    confirmed = enterprise.confirm(project["project_id"], preview["preview_id"],
                                   confirmed_by="User", responsible_team="Reviewer")
    for field in ("rules", "checks", "ruleset", "source_sha256", "source", "purposes"):
        assert confirmed[field] == preview[field]
    assert enterprise.package_bytes(confirmed["rule_revision_id"]) == body
