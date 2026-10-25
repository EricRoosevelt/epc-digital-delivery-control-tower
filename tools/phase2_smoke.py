"""Exercise the source-checkout Doctor with public IFCs and fresh local user state.

Run with the installed environment's Python. This is an HTTP/persistence smoke,
not a browser, GPU, capacity or regulatory-compliance test.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
from importlib.metadata import version
import json
import math
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def clean_environment(home: Path):
    """An allowlist deliberately excludes provider keys, PYTHONPATH and Node config."""
    home.mkdir(parents=True, exist_ok=True)
    env = {
        key: os.environ[key]
        for key in ("SystemRoot", "WINDIR", "COMSPEC", "PATHEXT")
        if key in os.environ
    }
    env.update(
        {
            "PATH": str(Path(sys.executable).parent) + os.pathsep + os.defpath,
            "HOME": str(home),
            "USERPROFILE": str(home),
            "LOCALAPPDATA": str(home / "local"),
            "APPDATA": str(home / "roaming"),
            "XDG_CONFIG_HOME": str(home / "config"),
            "XDG_STATE_HOME": str(home / "state"),
            "TMP": str(home / "tmp"),
            "TEMP": str(home / "tmp"),
            "TMPDIR": str(home / "tmp"),
            "PYTHONUTF8": "1",
            "PYTHONNOUSERSITE": "1",
            "PIP_CONFIG_FILE": os.devnull,
            "PIP_NO_INPUT": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
        }
    )
    (home / "tmp").mkdir(exist_ok=True)
    return env


def request(base, path, body=None):
    headers = {}
    if isinstance(body, dict):
        body = json.dumps(body, ensure_ascii=False).encode()
        headers["Content-Type"] = "application/json"
    elif body is not None:
        headers["Content-Type"] = "application/octet-stream"
    with urlopen(Request(base + path, data=body, headers=headers), timeout=60) as response:
        raw = response.read()
        if response.headers.get("Content-Type", "").startswith("application/json"):
            return json.loads(raw)
        return raw


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def verify_meshes(report, geometry):
    keys = {row["element_key"] for row in report["elements"]}
    require(bool(geometry["meshes"]), "No real geometry was returned")
    triangles = 0
    for mesh in geometry["meshes"]:
        vertices, indices = mesh["positions"], mesh["indices"]
        require(mesh["element_key"] in keys, "Mesh has no report binding")
        require(
            vertices and indices and len(vertices) % 3 == len(indices) % 3 == 0,
            "Invalid triangle mesh arrays",
        )
        require(all(math.isfinite(v) for v in vertices), "Non-finite mesh coordinates")
        require(min(indices) >= 0 and max(indices) < len(vertices) // 3, "Invalid mesh indices")
        triangles += len(indices) // 3
    return {"elements": len(keys), "meshes": len(geometry["meshes"]), "triangles": triangles}


@contextmanager
def server(checkout, state, home, log_path):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-I",
                "-u",
                str(checkout / "doctor/serve.py"),
                "--port",
                str(port),
                "--checks-dir",
                str(state),
            ],
            cwd=checkout,
            env=clean_environment(home),
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        try:
            deadline = time.monotonic() + 30
            while True:
                require(
                    process.poll() is None, "Doctor exited before becoming ready; inspect log"
                )
                try:
                    request(base, "/api/projects")
                    break
                except (URLError, TimeoutError):
                    require(time.monotonic() < deadline, "Doctor startup timed out")
                    time.sleep(0.1)
            yield base, process.pid
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)


def artifact_hashes(checkout):
    contract = json.loads(
        (checkout / "docs/contracts/contract-1.7.json").read_text(encoding="utf-8")
    )
    actual = {
        name: hashlib.sha256((checkout / name).read_bytes()).hexdigest()
        for name in contract["artifacts"]
    }
    require(actual == contract["artifacts"], "Published contract hashes do not match")
    return actual


def exercise(checkout: Path, output: Path):
    import ifcopenshell
    import ifcopenshell.util.element

    checkout, output = checkout.resolve(), output.resolve()
    require(not output.is_relative_to(checkout), "Smoke evidence must be outside checkout")
    output.parent.mkdir(parents=True, exist_ok=True)
    sha = subprocess.check_output(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    result = {
        "schema_version": 1,
        "source_sha": sha,
        "status": "running",
        "steps": [],
        "environment": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "packages": {
                name: version(name)
                for name in (
                    "epc-digital-delivery-control-tower",
                    "ifcopenshell",
                    "ifctester",
                    "pandas",
                    "xmlschema",
                )
            },
        },
        "scope": "Public IFC geometry, HTTP and restart persistence; no GPU claim",
    }

    def step(name, details=None):
        result["steps"].append({"name": name, "status": "passed", "details": details or {}})

    try:
        before_hashes = artifact_hashes(checkout)
        step("published_artifacts_before", {"count": len(before_hashes)})
        with tempfile.TemporaryDirectory(prefix="epc-phase2-smoke-") as scratch:
            scratch = Path(scratch)
            state, home = scratch / "checks", scratch / "user"
            with server(checkout, state, home, output.parent / "smoke-first-server.log") as (
                base,
                pid,
            ):
                require(
                    not request(base, "/api/review/ai")["configured"],
                    "Provider key leaked into smoke",
                )
                require(
                    request(base, "/api/projects") == {"projects": []},
                    "User state was not empty",
                )
                for path in ("/review.html", "/projects.html"):
                    require(
                        b"<!doctype html" in request(base, path).lower(),
                        "Missing source UI page",
                    )
                provenance = json.loads(
                    (checkout / "third_party/three/0.186.1/provenance.json").read_text()
                )
                for item in provenance["files"]:
                    raw = request(base, "/vendor/three/" + item["vendored_path"])
                    require(
                        hashlib.sha256(raw).hexdigest() == item["sha256"],
                        "Vendored JS hash mismatch",
                    )
                step(
                    "fresh_server_and_static_assets", {"pid": pid, "provider_configured": False}
                )
                demo = request(base, "/api/review/demo")
                demo_geometry = request(
                    base, "/api/review/geometry?review=" + demo["review_id"]
                )
                require(
                    "buildingSMART" in demo["source"]["attribution"], "Demo lost attribution"
                )
                step("public_federated_geometry", verify_meshes(demo, demo_geometry))
                source = checkout / "data/raw/Building-Hvac.ifc"
                before = request(
                    base, "/api/review/models?filename=public-before.ifc", source.read_bytes()
                )
                geometry = request(base, "/api/review/geometry?review=" + before["review_id"])
                geometry_counts = verify_meshes(before, geometry)
                failing = next(
                    f
                    for f in before["findings"]
                    if f["rule_id"] == "PV-001" and f["status"] == "FAIL"
                )
                target = next(
                    e for e in before["elements"] if e["element_key"] == failing["element_key"]
                )
                project = request(base, "/api/projects", {"name": "Phase2 public smoke"})
                saved_before = request(
                    base,
                    "/api/projects/revisions",
                    {
                        "project_id": project["project_id"],
                        "review_id": before["review_id"],
                        "model_name": "Public HVAC",
                        "label": "Before",
                    },
                )
                followup = request(
                    base,
                    "/api/projects/followup",
                    {
                        "revision_id": saved_before["revision"]["revision_id"],
                        "finding_id": failing["finding_id"],
                        "status": "ready_for_recheck",
                        "owner": "公开样例工程师",
                        "note": "Recorded action is not a check pass.",
                    },
                )
                require(saved_before["report"] == before, "Saving modified the report")
                step("public_model_saved_with_followup", geometry_counts)
                model = ifcopenshell.open(source)
                terminal = model.by_guid(target["global_id"])
                assigned = ifcopenshell.util.element.get_type(terminal)
                (assigned or terminal).PredefinedType = "LOUVRE"
                after = request(
                    base,
                    "/api/review/models?filename=public-renamed-after.ifc",
                    model.to_string().encode(),
                )
                saved_after = request(
                    base,
                    "/api/projects/revisions",
                    {
                        "project_id": project["project_id"],
                        "model_id": saved_before["revision"]["model_id"],
                        "review_id": after["review_id"],
                        "label": "After",
                    },
                )
                a, b = (
                    saved_before["revision"]["revision_id"],
                    saved_after["revision"]["revision_id"],
                )
                compare_path = f"/api/projects/compare?before={a}&after={b}"
                comparison = request(base, compare_path)
                require(
                    any(
                        row["global_id"] == target["global_id"]
                        and row["rule_id"] == "PV-001"
                        and row["change"] == "resolved"
                        for row in comparison["rows"]
                    ),
                    "Real exported revision did not produce the expected recheck",
                )
                brief_path = "/api/projects/brief?project=" + project["project_id"]
                brief = request(base, brief_path)
                require(b"Phase2 public smoke" in brief, "Project brief was not exported")
                require(
                    saved_after["revision"]["model_id"] == saved_before["revision"]["model_id"],
                    "Filename change replaced the stable model slot",
                )
                step(
                    "source_revision_recheck_compare_and_brief",
                    {"errors": comparison["summary"]["errors"]},
                )
            step("first_process_stopped")
            with server(checkout, state, home, output.parent / "smoke-reopened-server.log") as (
                base,
                new_pid,
            ):
                require(new_pid != pid, "The smoke did not start a new process")
                try:
                    request(base, "/api/review/report?review=" + before["review_id"])
                    raise AssertionError("New process unexpectedly inherited review cache")
                except HTTPError as missing:
                    require(
                        missing.code == 404,
                        "Expected missing review before library re-admission",
                    )
                reopened_before = request(base, "/api/projects/revision?revision=" + a)
                reopened_after = request(base, "/api/projects/revision?revision=" + b)
                require(
                    reopened_before["report"] == before and reopened_after["report"] == after,
                    "Frozen revision report changed after restart",
                )
                require(
                    reopened_before["followups"] == [followup],
                    "Followup did not survive restart",
                )
                require(
                    next(
                        f
                        for f in reopened_before["report"]["findings"]
                        if f["finding_id"] == failing["finding_id"]
                    )["status"]
                    == "FAIL",
                    "A manual record changed the frozen machine status",
                )
                reopened_geometry = request(
                    base, "/api/review/geometry?review=" + before["review_id"]
                )
                require(
                    digest(reopened_geometry) == digest(geometry),
                    "Real geometry changed after restart",
                )
                require(
                    request(base, compare_path) == comparison,
                    "Comparison changed after restart",
                )
                require(request(base, brief_path) == brief, "Brief changed after restart")
                advice = request(
                    base,
                    "/api/review/advice",
                    {
                        "review_id": before["review_id"],
                        "finding_id": failing["finding_id"],
                        "use_ai": False,
                    },
                )
                require(advice["mode"] == "guidance", "Local guidance failed after restart")
                step(
                    "new_process_reopens_evidence",
                    {"pid": new_pid, **geometry_counts, "geometry_sha256": digest(geometry)},
                )
        require(artifact_hashes(checkout) == before_hashes, "Smoke changed published artifacts")
        step("published_artifacts_after", {"count": len(before_hashes), "mismatches": 0})
        result["status"] = "passed"
    except Exception as error:
        result["status"] = "failed"
        result["failure"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = exercise(args.checkout, args.output)
    print(
        json.dumps(
            {
                "status": result["status"],
                "source_sha": result["source_sha"],
                "steps": len(result["steps"]),
            }
        )
    )


if __name__ == "__main__":
    main()
