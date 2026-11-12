"""Run public browser regressions with fresh state; optionally prove mutation detection.

python tools/run_browser_qa.py --output <new-external-directory> [--mutations]
Requires this checkout's npm-ci Playwright and installed Chromium. No running
preview server, private model, external NODE_PATH or user database is reused.
"""

from __future__ import annotations

import argparse
from collections import Counter
import contextlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time

from phase2_smoke import server

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    "doctor_projects", "doctor_review", "doctor_review_large_selection", "doctor_ui",
    "doctor_review_import_jobs",
    "doctor_enterprise",
)
EXTENDED_SCRIPTS = (
    "doctor_startup", "doctor_mobile_search", "doctor_ui_states",
    "doctor_ui_resilience", "doctor_ui_layout",
)
# Errors Chromium's network stack raises from the host, even for 127.0.0.1: a
# Windows socket error (WSAENOBUFS, seen on hosted Windows runners) and an OS
# network-change notification (seen on a developer machine). No application route
# and no test fault produces them; tests inject only reset/disconnected errors.
HOST_NETWORK_ERRORS = ("net::ERR_NO_BUFFER_SPACE", "net::ERR_NETWORK_CHANGED")
HOST_NETWORK_COMMANDS = (
    ("netsh", "int", "ipv4", "show", "dynamicport", "tcp"),
    ("netsh", "int", "ipv4", "show", "excludedportrange", "protocol=tcp"),
)


@contextlib.contextmanager
def socket_states(output):
    """On Windows, record the port configuration and TCP state counts every two seconds."""

    if os.name != "nt":
        yield
        return

    def text(args):
        # Console tools write UTF-8 or the OEM code page; only ASCII fields are parsed.
        output = subprocess.run(args, capture_output=True, timeout=30).stdout
        try:
            return output.decode("utf-8")
        except UnicodeDecodeError:
            return output.decode("oem", errors="replace")

    with (output / "host-network.txt").open("w", encoding="utf-8") as stream:
        for args in HOST_NETWORK_COMMANDS:
            try:
                stream.write("$ " + " ".join(args) + "\n" + text(args))
            except (OSError, subprocess.SubprocessError) as error:
                stream.write(f"unavailable: {error}\n")
    stop = threading.Event()

    def sample():
        start = time.monotonic()
        with (output / "socket-states.jsonl").open("w", encoding="utf-8") as stream:
            while not stop.wait(2):
                try:
                    lines = text(["netstat", "-an", "-p", "tcp"]).splitlines()
                except (OSError, subprocess.SubprocessError) as error:
                    stream.write(json.dumps({"error": str(error)}) + "\n")
                    continue
                states = Counter(line.split()[-1] for line in lines
                                 if line.strip().startswith("TCP") and len(line.split()) >= 4)
                row = {"s": round(time.monotonic() - start), **states}
                stream.write(json.dumps(row) + "\n")
                stream.flush()

    thread = threading.Thread(target=sample, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(40)


def host_network_error(evidence):
    for path in sorted(evidence.rglob("*.jsonl")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for error in HOST_NETWORK_ERRORS:
            if error in text:
                return error
    return None


def command(args, directory, *, env=None, cwd=ROOT):
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "process.log").open("w", encoding="utf-8") as log:
        try:
            result = subprocess.run(
                args, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=180,
            )
        except subprocess.TimeoutExpired:
            log.write("\nQA process exceeded its 180-second public-fixture limit.\n")
            return 124
    return result.returncode


def run_scripts(checkout, directory, names):
    directory.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, BROWSER_CHANNEL="chromium")
    env.pop("NODE_PATH", None)
    results = []
    with server(
        checkout, directory / "checks", directory / "user", directory / "server.log",
    ) as (
        base, _pid,
    ):
        fixture = directory / "public-comparison-fixture.json"
        fixture_status = command(
            [sys.executable, str(ROOT / "tests/doctor_projects_fixture.py"), base,
             "--output", str(fixture)], directory / "fixture",
        )
        if fixture_status:
            raise RuntimeError("Public fixture creation failed; inspect fixture/process.log")
        for name in names:
            evidence = directory / name
            args = ["node", str(ROOT / f"tests/{name}.browser.cjs"), base, str(evidence)]
            if name == "doctor_projects":
                args.append(str(fixture))
            if name == "doctor_enterprise":
                public = directory / "enterprise-public-fixtures"
                if command([sys.executable, str(ROOT / "tests/doctor_enterprise_fixture.py"),
                            "--output-dir", str(public)], directory / "enterprise-fixture"):
                    raise RuntimeError("Enterprise public fixture export failed")
                args.append(str(public))
            if name == "doctor_ui_states":
                synthetic = directory / "synthetic-long-layout.ifc"
                if command([sys.executable, str(ROOT / "tests/doctor_ui_stress_fixture.py"),
                            str(synthetic)], directory / "layout-fixture"):
                    raise RuntimeError("Public long-field fixture export failed")
                args.append(str(synthetic))
            status = command(args, evidence, env=env)
            results.append({"script": name, "exit_code": status})
    return results


def run_with_host_retry(checkout, output, names):
    """Run the set; rerun all of it once only if every failure was a host network error.

    Later suites read state earlier ones create, so a rerun is the whole set on a new
    server and state. The first attempt's evidence stays in ``baseline``.
    """

    baseline = output / "baseline"
    scripts = run_scripts(checkout, baseline, names)
    failures = [
        {"script": item["script"], "error": host_network_error(baseline / item["script"])}
        for item in scripts if item["exit_code"]
    ]
    if not failures or not all(item["error"] for item in failures):
        return scripts, None
    print("Host network error in " + ", ".join(item["script"] for item in failures)
          + "; rerunning the browser set once with fresh state", flush=True)
    rerun = run_scripts(checkout, output / "host-network-rerun", names)
    return rerun, {"first_failures": failures, "rerun_evidence": "host-network-rerun"}


def mutation_copy(destination):
    names = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
    ).decode("utf-8").split("\0")
    for name in sorted(set(filter(None, names))):
        source = ROOT / name
        if source.is_file():
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)


def mutations(output):
    probes = (
        ("draft-retention", "doctor/static/projects-review.js", "if (!drafts.has(key))",
         "if (true)", "doctor_projects", "switching findings preserves the draft"),
        ("geometry-json-recovery", "doctor/static/projects-api.js",
         'error.responsePhase = "decode"; throw error;',
         'error.responsePhase = "decode"; body = {};', "doctor_review",
         "geometry failure must stay recoverable rather than report Model loaded"),
        ("selected-finding-pin", "doctor/static/review.js",
         "if (selectedIndex >= state.limit)", "if (false)", "doctor_review_large_selection",
         "deep-linked finding must be pinned inside the finite result window"),
    )
    results = []
    for name, relative, original, replacement, script, assertion in probes:
        with tempfile.TemporaryDirectory(prefix="bim-doctor-browser-mutation-") as temporary:
            checkout = Path(temporary).resolve()
            mutation_copy(checkout)
            target = checkout / relative
            text = target.read_text(encoding="utf-8")
            if text.count(original) != 1:
                raise RuntimeError(f"Mutation target is no longer unique: {name}")
            target.write_text(text.replace(original, replacement), encoding="utf-8")
            result = run_scripts(checkout, output / name, (script,))[0]
            log = (output / name / script / "process.log").read_text(encoding="utf-8")
            result.update({
                "mutation": name, "file": relative, "assertion": assertion,
                "detected": result["exit_code"] != 0 and assertion in log,
            })
            results.append(result)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mutations", action="store_true")
    parser.add_argument(
        "--extended", action="store_true",
        help="Also run startup, legacy mobile search/state/recovery/layout checks",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(ROOT) or output.exists():
        raise ValueError("Supply a new evidence directory outside this checkout")
    output.mkdir(parents=True)
    result = {
        "source_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        ).strip(),
        "status": "running", "browser_channel": "chromium", "scripts": [], "mutations": [],
        "source_tree_clean": not subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ROOT, text=True,
        ).strip(),
    }
    try:
        names = SCRIPTS + EXTENDED_SCRIPTS if args.extended else SCRIPTS
        with socket_states(output):
            result["scripts"], retry = run_with_host_retry(ROOT, output, names)
        if retry:
            result["host_network_retry"] = retry
        if any(item["exit_code"] for item in result["scripts"]):
            raise RuntimeError(
                "A browser regression failed; inspect its process.log and screenshot",
            )
        if args.mutations:
            result["mutations"] = mutations(output / "mutations")
            if not all(item["detected"] for item in result["mutations"]):
                raise RuntimeError(
                    "A deliberate mutation escaped the existing browser assertions",
                )
        result["status"] = "passed"
    except Exception as error:
        result["status"] = "failed"
        result["error"] = str(error)
        raise
    finally:
        (output / "browser-qa.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8",
        )
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
