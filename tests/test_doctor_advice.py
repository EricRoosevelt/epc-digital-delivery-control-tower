"""The AI receives selected evidence; the server owns facts and citations."""

import io
import json
from http.server import ThreadingHTTPServer
import threading
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest

from doctor.advice import AdviceService, AdviceUnavailable
from doctor.serve import make_handler


class Reviews:
    def get(self, review_id):
        if review_id != "review-1":
            raise KeyError(review_id)
        return {
            "review_id": review_id,
            "source": {"filename": "private-project.ifc", "sha256": "file-hash"},
            "geometry": {"positions": [1, 2, 3]},
            "elements": [{
                "element_key": "model::globalid", "global_id": "globalid",
                "model_key": "model", "ifc_class": "IfcAirTerminal",
                "name": "chimney cover", "storey": "Level 1", "tag": "A-17",
            }],
            "findings": [{
                "finding_id": "finding-1", "element_key": "model::globalid",
                "rule_id": "PV-001", "status": "FAIL", "severity": "ERROR",
                "title": "Air-terminal type",
                "expected": "DIFFUSER, GRILLE, LOUVRE or REGISTER",
                "actual": "USERDEFINED: chimney cover", "reason": "Outside the review set",
                "citation": "PV-001 project review requirement",
            }],
        }


def guidance(finding, element, language="en"):
    return {
        "summary": "Check the source category and export mapping.",
        "facts": [finding["actual"]],
        "actions": ["Confirm whether this object is an air terminal."],
        "verification": ["Re-export and run the same check."],
        "citations": [{"id": finding["rule_id"], "label": finding["citation"]}],
        "limitations": ["A target type needs engineering judgement."],
    }


def service(**kwargs):
    return AdviceService(Reviews(), guidance=guidance, **kwargs)


def test_local_guidance_is_explicit_and_never_calls_a_network():
    def no_network(*args, **kwargs):
        pytest.fail("Local guidance must not make a request")

    advice = service(environ={}, opener=no_network)
    assert advice.describe()["configured"] is False
    answer = advice.explain("review-1", "finding-1", use_ai=False)
    assert answer["mode"] == "guidance"
    assert answer["facts"] == ["USERDEFINED: chimney cover"]
    assert answer["finding_id"] == "finding-1"


def test_requesting_ai_without_a_key_is_an_actionable_error():
    with pytest.raises(AdviceUnavailable, match="OPENAI_API_KEY"):
        service(environ={}).explain("review-1", "finding-1", use_ai=True)


def test_ai_only_receives_selected_evidence_and_cannot_replace_facts():
    calls = []

    def opener(request, *, timeout):
        calls.append((request, timeout))
        generated = {
            "summary": "Confirm the object's intended function before editing its type.",
            "actions": ["Compare the object with the source authoring model."],
            "verification": ["Re-export IFC4 and repeat PV-001."],
        }
        return io.BytesIO(json.dumps({
            "status": "completed", "output": [{
                "type": "message", "role": "assistant", "content": [{
                    "type": "output_text", "text": json.dumps(generated),
                }],
            }],
        }).encode())

    advice = service(environ={"OPENAI_API_KEY": "test-secret", "OPENAI_MODEL": "test-model"},
                     opener=opener)
    answer = advice.explain("review-1", "finding-1", language="en", use_ai=True)
    request, timeout = calls[0]
    payload = json.loads(request.data)
    assert request.full_url == "https://api.openai.com/v1/responses"
    assert timeout == 30
    assert payload["store"] is False
    assert payload["model"] == "test-model"
    assert payload["text"]["format"]["strict"] is True
    sent = json.dumps(payload)
    assert "private-project.ifc" not in sent
    assert "positions" not in sent
    assert "file-hash" not in sent
    assert "test-secret" not in sent
    assert "USERDEFINED: chimney cover" in sent
    assert json.loads(payload["input"])["finding"]["severity"] == "ERROR"
    assert "PASS needs no corrective action" in payload["instructions"]
    assert answer["mode"] == "ai"
    assert answer["facts"] == ["USERDEFINED: chimney cover"]
    assert answer["citations"] == [
        {"id": "PV-001", "label": "PV-001 project review requirement"},
    ]
    assert answer["provider"] == "OpenAI"
    assert "test-secret" not in json.dumps(advice.describe())


@pytest.mark.parametrize("failure", [
    URLError("temporary connection failure"),
    HTTPError("https://api.openai.com/v1/responses", 401, "invalid key", {}, None),
])
def test_provider_failures_are_not_reported_as_generated_advice(failure):
    def opener(*args, **kwargs):
        raise failure

    with pytest.raises(AdviceUnavailable):
        service(environ={"OPENAI_API_KEY": "secret"}, opener=opener).explain(
            "review-1", "finding-1", use_ai=True,
        )


@pytest.mark.parametrize("response", [
    {"status": "incomplete", "output": []},
    {"status": "completed", "output": [{"type": "message", "content": [
        {"type": "refusal", "refusal": "Cannot provide a response"},
    ]}]},
    {"status": "completed", "output": [{"type": "message", "content": [
        {"type": "output_text", "text": '{"summary":"ok","actions":[],"verification":[]}'},
    ]}]},
])
def test_incomplete_refused_or_empty_advice_does_not_become_a_success(response):
    with pytest.raises(AdviceUnavailable):
        service(environ={"OPENAI_API_KEY": "secret"}, opener=lambda *a, **k:
                io.BytesIO(json.dumps(response).encode())).explain(
                    "review-1", "finding-1", use_ai=True,
                )


def test_unknown_selection_never_reaches_provider():
    def no_network(*args, **kwargs):
        pytest.fail("Unknown selections must not reach a provider")

    advice = service(environ={"OPENAI_API_KEY": "secret"}, opener=no_network)
    with pytest.raises(KeyError):
        advice.explain("review-1", "another-finding", use_ai=True)
    with pytest.raises(KeyError):
        advice.explain("another-review", "finding-1", use_ai=True)


def test_language_and_ai_choice_are_explicit():
    advice = service(environ={})
    with pytest.raises(ValueError):
        advice.explain("review-1", "finding-1", language="fr")
    with pytest.raises(ValueError):
        advice.explain("review-1", "finding-1", use_ai="false")


@pytest.mark.parametrize("response", [
    [], None,
    {"status": "completed", "output": None},
    {"status": "completed", "output": [None]},
    {"status": "completed", "output": [{"type": "message", "content": None}]},
    {"status": "completed", "output": [{"type": "message", "content": [None]}]},
    {"status": "completed", "output": [{"type": "message", "content": [
        {"type": "output_text"},
    ]}]},
])
def test_unusable_provider_envelope_preserves_local_guidance_and_retry(response):
    advice = service(environ={"OPENAI_API_KEY": "test-only"}, opener=lambda *a, **k:
                     io.BytesIO(json.dumps(response).encode()))
    with pytest.raises(AdviceUnavailable, match="Local rule guidance remains available"):
        advice.explain("review-1", "finding-1", use_ai=True)
    assert advice.explain("review-1", "finding-1")["mode"] == "guidance"


def test_provider_failure_http_is_retryable_without_losing_selected_evidence():
    generated = {"summary": "Verify source", "actions": ["Review source object"],
                 "verification": ["Repeat this rule"]}
    responses = iter([
        {"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text"}]}]},
        {"status": "completed", "output": [{"type": "message", "content": [
            {"type": "output_text", "text": json.dumps(generated)}]}]},
    ])
    advice = service(environ={"OPENAI_API_KEY": "test-only"}, opener=lambda *a, **k:
                     io.BytesIO(json.dumps(next(responses)).encode()))
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(
        lambda: None, review_factory=lambda: advice.reviews, advice_factory=lambda: advice,
    ))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def ask(use_ai):
        request = Request(
            f"http://127.0.0.1:{server.server_port}/api/review/advice",
            data=json.dumps({"review_id": "review-1", "finding_id": "finding-1",
                             "use_ai": use_ai}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            return json.load(response)

    try:
        with pytest.raises(HTTPError) as error:
            ask(True)
        assert error.value.code == 503
        assert "Local rule guidance remains available" in json.load(error.value)["error"]
        local = ask(False)
        retried = ask(True)
        assert local["mode"] == "guidance" and retried["mode"] == "ai"
        assert local["facts"] == retried["facts"] == ["USERDEFINED: chimney cover"]
        assert retried["citations"] == local["citations"]
        assert advice.reviews.get("review-1")["findings"][0]["status"] == "FAIL"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
