"""Run public browser regressions with fresh state; optionally prove mutation detection.

python tools/run_browser_qa.py --output <new-external-directory> [--mutations]
Requires this checkout's npm-ci Playwright and installed Chromium. No running
preview server, private model, external NODE_PATH or user database is reused.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from phase2_smoke import server

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    "doctor_projects", "doctor_review", "doctor_review_large_selection", "doctor_ui",
    "doctor_review_import_jobs",
)


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
            status = command(args, evidence, env=env)
            results.append({"script": name, "exit_code": status})
    return results


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
    }
    try:
        result["scripts"] = run_scripts(ROOT, output / "baseline", SCRIPTS)
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
