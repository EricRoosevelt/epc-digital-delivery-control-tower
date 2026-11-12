"""A browser suite is rerun once only for a host socket error, never for its own failure."""

import contextlib
import importlib.util
import sys
from pathlib import Path

from helpers import PROJECT_ROOT

sys.path.insert(0, str(PROJECT_ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "run_browser_qa", PROJECT_ROOT / "tools/run_browser_qa.py"
)
qa = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qa)

HOST_ERROR = (
    '{"phase":"requestfailed","url":"http://127.0.0.1:1/vocabulary.js",'
    '"error":"net::ERR_NO_BUFFER_SPACE"}\n'
)
TEST_FAULT = '{"phase":"requestfailed","error":"net::ERR_INTERNET_DISCONNECTED"}\n'


def run_one(tmp_path, monkeypatch, attempts):
    """attempts: per call, (exit code, diagnostics text written by the suite)."""

    calls = []

    def command(args, directory, *, env=None, cwd=None):
        directory.mkdir(parents=True, exist_ok=True)
        if args[0] != "node":
            return 0
        code, diagnostics = attempts[len(calls)]
        calls.append(directory)
        (directory / "browser-diagnostics.jsonl").write_text(diagnostics, encoding="utf-8")
        return code

    @contextlib.contextmanager
    def server(*_args):
        yield "http://127.0.0.1:1", 0

    monkeypatch.setattr(qa, "command", command)
    monkeypatch.setattr(qa, "server", server)
    results = qa.run_scripts(Path(tmp_path), tmp_path / "out", ("doctor_ui",))
    return results, calls


def test_host_socket_error_reruns_once_and_keeps_the_first_attempt(tmp_path, monkeypatch):
    results, calls = run_one(tmp_path, monkeypatch, [(1, HOST_ERROR), (0, "")])
    assert len(calls) == 2
    assert results == [{
        "script": "doctor_ui", "exit_code": 0,
        "host_socket_retry": {
            "error": "net::ERR_NO_BUFFER_SPACE", "first_exit_code": 1,
            "first_evidence": "doctor_ui-host-socket-error",
        },
    }]
    kept = tmp_path / "out/doctor_ui-host-socket-error/browser-diagnostics.jsonl"
    assert "ERR_NO_BUFFER_SPACE" in kept.read_text(encoding="utf-8")


def test_a_second_host_socket_error_still_fails(tmp_path, monkeypatch):
    results, calls = run_one(tmp_path, monkeypatch, [(1, HOST_ERROR), (1, HOST_ERROR)])
    assert len(calls) == 2
    assert results[0]["exit_code"] == 1


def test_any_other_failure_is_not_rerun(tmp_path, monkeypatch):
    results, calls = run_one(tmp_path, monkeypatch, [(1, TEST_FAULT)])
    assert len(calls) == 1
    assert results == [{"script": "doctor_ui", "exit_code": 1}]


def test_a_passing_suite_with_a_recovered_host_error_is_not_rerun(tmp_path, monkeypatch):
    results, calls = run_one(tmp_path, monkeypatch, [(0, HOST_ERROR)])
    assert len(calls) == 1
    assert results == [{"script": "doctor_ui", "exit_code": 0}]
