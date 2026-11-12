"""The workbench advice endpoints resolve selections on the local server."""

import importlib.util
import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from helpers import PROJECT_ROOT
from doctor.advice import AdviceService
from internal.doctor_adapter.review import ReviewStore


@pytest.fixture(scope="module")
def workbench():
    spec = importlib.util.spec_from_file_location(
        "review_http_server", PROJECT_ROOT / "doctor/serve.py",
    )
    serve = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(serve)
    store = ReviewStore()
    report = store.demo()
    advice = AdviceService(store, environ={})
    server = ThreadingHTTPServer(("127.0.0.1", 0), serve.make_handler(
        lambda: None, review_factory=lambda: store, advice_factory=lambda: advice,
    ))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}", report
    server.shutdown()
    server.server_close()
    thread.join()


def test_advice_http_preserves_selected_finding_and_exposes_no_key(workbench):
    base, report = workbench
    with urlopen(base + "/api/review/ai") as response:
        config = json.load(response)
    assert config == {"configured": False, "provider": "OpenAI", "model": "gpt-4.1-mini"}
    finding = next(f for f in report["findings"]
                   if f["rule_id"] == "PV-001" and f["status"] == "FAIL")
    request = Request(base + "/api/review/advice", data=json.dumps({
        "review_id": report["review_id"], "finding_id": finding["finding_id"],
        "language": "zh", "use_ai": False,
    }).encode(), headers={"Content-Type": "application/json"})
    with urlopen(request) as response:
        answer = json.load(response)
    assert answer["mode"] == "guidance"
    assert answer["finding_id"] == finding["finding_id"]
    assert answer["facts"] and answer["actions"] and answer["verification"]
    assert answer["citations"]


def test_ai_without_configuration_is_a_failure_with_local_guidance_still_available(workbench):
    base, report = workbench
    request = Request(base + "/api/review/advice", data=json.dumps({
        "review_id": report["review_id"], "finding_id": report["findings"][0]["finding_id"],
        "use_ai": True,
    }).encode(), headers={"Content-Type": "application/json"})
    with pytest.raises(HTTPError) as error:
        urlopen(request)
    assert error.value.code == 503
    assert "OPENAI_API_KEY" in json.load(error.value)["error"]


@pytest.mark.parametrize("body,status", [
    ({"review_id": "missing", "finding_id": "missing"}, 404),
    ([], 400),
    ({"review_id": 1, "finding_id": "missing"}, 400),
])
def test_advice_http_reports_a_stale_or_invalid_selection(workbench, body, status):
    base, _ = workbench
    request = Request(base + "/api/review/advice", data=json.dumps(body).encode(),
                      headers={"Content-Type": "application/json"})
    with pytest.raises(HTTPError) as error:
        urlopen(request)
    assert error.value.code == status
    assert json.load(error.value)["error"]
