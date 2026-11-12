"""The browser set is rerun once only when every failure was a host network error."""

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

NO_BUFFER = (
    '{"phase":"requestfailed","url":"http://127.0.0.1:1/vocabulary.js",'
    '"error":"net::ERR_NO_BUFFER_SPACE"}\n'
)
NETWORK_CHANGED = '{"phase":"requestfailed","error":"net::ERR_NETWORK_CHANGED"}\n'
TEST_FAULT = '{"phase":"requestfailed","error":"net::ERR_INTERNET_DISCONNECTED"}\n'
NAMES = ("doctor_ui_states", "doctor_ui_resilience")


def run_set(tmp_path, monkeypatch, outcomes):
    """outcomes: per suite run in order, (exit code, diagnostics written by the suite)."""

    calls, servers = [], []

    def command(args, directory, *, env=None, cwd=None):
        directory.mkdir(parents=True, exist_ok=True)
        if args[0] != "node":
            return 0
        code, diagnostics = outcomes[len(calls)]
        calls.append(directory.relative_to(tmp_path).as_posix())
        (directory / "browser-diagnostics.jsonl").write_text(diagnostics, encoding="utf-8")
        return code

    @contextlib.contextmanager
    def server(checkout, state, *_args):
        servers.append(state.relative_to(tmp_path).as_posix())
        yield "http://127.0.0.1:1", 0

    monkeypatch.setattr(qa, "command", command)
    monkeypatch.setattr(qa, "server", server)
    scripts, retry = qa.run_with_host_retry(Path(tmp_path), tmp_path, NAMES)
    return scripts, retry, calls, servers


def test_a_host_error_reruns_the_whole_set_on_a_new_server(tmp_path, monkeypatch):
    scripts, retry, calls, servers = run_set(
        tmp_path, monkeypatch, [(1, NO_BUFFER), (0, ""), (0, ""), (0, "")],
    )
    assert servers == ["baseline/checks", "host-network-rerun/checks"]
    assert calls == [
        "baseline/doctor_ui_states", "baseline/doctor_ui_resilience",
        "host-network-rerun/doctor_ui_states", "host-network-rerun/doctor_ui_resilience",
    ]
    assert scripts == [{"script": name, "exit_code": 0} for name in NAMES]
    assert retry == {
        "first_failures": [{"script": "doctor_ui_states", "error": "net::ERR_NO_BUFFER_SPACE"}],
        "rerun_evidence": "host-network-rerun",
    }
    kept = tmp_path / "baseline/doctor_ui_states/browser-diagnostics.jsonl"
    assert "ERR_NO_BUFFER_SPACE" in kept.read_text(encoding="utf-8")


def test_a_network_change_notification_is_a_host_error(tmp_path, monkeypatch):
    scripts, retry, calls, _ = run_set(
        tmp_path, monkeypatch, [(0, ""), (1, NETWORK_CHANGED), (0, ""), (0, "")],
    )
    assert len(calls) == 4
    assert retry["first_failures"][0]["error"] == "net::ERR_NETWORK_CHANGED"
    assert all(item["exit_code"] == 0 for item in scripts)


def test_a_failure_in_the_rerun_still_fails(tmp_path, monkeypatch):
    scripts, retry, calls, _ = run_set(
        tmp_path, monkeypatch, [(1, NO_BUFFER), (0, ""), (1, NO_BUFFER), (0, "")],
    )
    assert len(calls) == 4
    assert scripts[0]["exit_code"] == 1
    assert retry is not None


def test_any_other_failure_is_not_rerun(tmp_path, monkeypatch):
    scripts, retry, calls, servers = run_set(
        tmp_path, monkeypatch, [(1, TEST_FAULT), (0, "")],
    )
    assert (len(calls), len(servers), retry) == (2, 1, None)
    assert scripts[0] == {"script": "doctor_ui_states", "exit_code": 1}


def test_a_host_error_beside_another_failure_is_not_rerun(tmp_path, monkeypatch):
    scripts, retry, calls, _ = run_set(
        tmp_path, monkeypatch, [(1, NO_BUFFER), (1, TEST_FAULT)],
    )
    assert (len(calls), retry) == (2, None)
    assert [item["exit_code"] for item in scripts] == [1, 1]


def test_a_passing_set_with_a_recovered_host_error_is_not_rerun(tmp_path, monkeypatch):
    scripts, retry, calls, _ = run_set(tmp_path, monkeypatch, [(0, NO_BUFFER), (0, "")])
    assert (len(calls), retry) == (2, None)
