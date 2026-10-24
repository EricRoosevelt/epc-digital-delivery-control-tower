"""A saved revision reopens into the same 3D/advice and work-brief interfaces."""

import importlib.util
import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import ifcopenshell
import pytest

from doctor.advice import AdviceService
from helpers import PROJECT_ROOT
from internal.doctor_adapter.project_library import ProjectLibrary
from internal.doctor_adapter.review import ReviewStore


@pytest.fixture()
def saved_project(tmp_path):
    original = ReviewStore()
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcAirTerminal", GlobalId=ifcopenshell.guid.new(),
                        Name="Roof cap", PredefinedType="NOTDEFINED")
    report = original.create("initial.ifc", model.to_string().encode())
    library = ProjectLibrary(tmp_path, original)
    project = library.create_project("Local coordination project")
    saved = library.save_revision(project["project_id"], report["review_id"],
                                  model_name="HVAC", label="R01")
    # New store and library model a complete application restart.
    restored = ReviewStore()
    reopened = ProjectLibrary(tmp_path, restored)
    advice = AdviceService(restored, environ={})
    spec = importlib.util.spec_from_file_location(
        "brief_http_server", PROJECT_ROOT / "doctor/serve.py",
    )
    serve = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(serve)
    server = ThreadingHTTPServer(("127.0.0.1", 0), serve.make_handler(
        lambda: None, review_factory=lambda: restored,
        advice_factory=lambda: advice, project_factory=lambda: reopened,
    ))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}", project, saved, report
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.parametrize("language,title", [
    ("en", "Project work brief"), ("zh", "项目工作简报"),
])
def test_saved_project_downloads_a_real_utf8_markdown_brief(saved_project, language, title):
    base, project, saved, report = saved_project
    url = f"{base}/api/projects/brief?project={project['project_id']}&language={language}"
    with urlopen(url) as response:
        assert response.headers["Content-Type"] == "text/markdown; charset=utf-8"
        assert "attachment" in response.headers["Content-Disposition"]
        text = response.read().decode("utf-8")
    assert title in text
    assert "Local coordination project" in text
    assert "Roof cap" in text and "R01" in text


def test_reopened_revision_restores_the_exact_selected_evidence_for_advice(saved_project):
    base, project, saved, report = saved_project
    revision_id = saved["revision"]["revision_id"]
    with urlopen(f"{base}/api/projects/revision?revision={revision_id}") as response:
        restored = json.load(response)
    assert restored["report"] == report
    finding = next(f for f in report["findings"] if f["rule_id"] == "PV-001")
    request = Request(base + "/api/review/advice", data=json.dumps({
        "review_id": report["review_id"], "finding_id": finding["finding_id"],
        "language": "en", "use_ai": False,
    }).encode(), headers={"Content-Type": "application/json"})
    with urlopen(request) as response:
        answer = json.load(response)
    assert answer["mode"] == "guidance"
    assert answer["finding_id"] == finding["finding_id"]
    assert any("NOTDEFINED" in str(fact) for fact in answer["facts"])
    assert answer["citations"]


def test_unknown_project_and_unsupported_export_language_are_clear_errors(saved_project):
    base, project, _, _ = saved_project
    for query, status in [("project=missing", 404),
                          (f"project={project['project_id']}&language=fr", 400)]:
        with pytest.raises(HTTPError) as failure:
            urlopen(f"{base}/api/projects/brief?{query}")
        assert failure.value.code == status
