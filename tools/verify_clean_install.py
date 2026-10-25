"""Clone a frozen Git HEAD, create a new venv, install editable, and run Phase 2 smoke.

The harness may live outside the clone; no uncommitted application source is copied.
All environments, logs and evidence are outside the source checkout.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile

from phase2_smoke import clean_environment

ROOT = Path(__file__).resolve().parents[1]


def verify(source: Path, output: Path, expected_sha: str | None = None):
    source, output = source.resolve(), output.resolve()
    if output.is_relative_to(source) or any((p / ".git").exists() for p in output.parents):
        raise ValueError("Clean-install environments and evidence must be outside checkouts")
    output.mkdir(parents=True, exist_ok=False)
    evidence = output / "evidence"
    evidence.mkdir()
    git = shutil.which("git")
    if not git:
        raise RuntimeError("Git is required to create an exact clean source checkout")
    env = clean_environment(output / "isolated-user")
    env["PATH"] = str(Path(git).parent) + os.pathsep + env["PATH"]
    checkout, venv = output / "checkout", output / "venv"
    metadata = {
        "schema_version": 1,
        "status": "running",
        "steps": [],
        "harness_sha256": {},
        "scope": "Exact source HEAD + new isolated editable install",
    }
    import hashlib

    for path in (Path(__file__), Path(__file__).with_name("phase2_smoke.py")):
        metadata["harness_sha256"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()

    def run(name, args, *, cwd=source, capture=False):
        start = time.monotonic()
        result = subprocess.run(
            args,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        (evidence / f"{name}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        metadata["steps"].append(
            {
                "name": name,
                "returncode": result.returncode,
                "wall_seconds": time.monotonic() - start,
            }
        )
        if result.returncode:
            raise RuntimeError(f"{name} failed; see the corresponding evidence log")
        return result.stdout.strip() if capture else None

    try:
        run("clone", [git, "clone", "--local", "--no-hardlinks", str(source), str(checkout)])
        sha = run("source-sha", [git, "rev-parse", "HEAD"], cwd=checkout, capture=True)
        metadata["source_sha"] = sha
        if expected_sha is not None and sha != expected_sha:
            raise RuntimeError("Clean checkout does not match the expected source SHA")
        status = run(
            "initial-checkout-status",
            [git, "status", "--porcelain"],
            cwd=checkout,
            capture=True,
        )
        if status:
            raise RuntimeError("The new clone was not clean before installation")
        metadata["initial_checkout_clean"] = True
        run("create-venv", [sys.executable, "-m", "venv", str(venv)])
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        configuration = (venv / "pyvenv.cfg").read_text(encoding="utf-8")
        metadata["system_site_packages"] = (
            "include-system-site-packages = true" in configuration.lower()
        )
        if metadata["system_site_packages"]:
            raise RuntimeError("The new venv inherited system packages")
        run(
            "editable-install",
            [str(python), "-m", "pip", "--isolated", "install", "-e", "."],
            cwd=checkout,
        )
        run("pip-check", [str(python), "-m", "pip", "check"], cwd=checkout)
        run(
            "project-wheel",
            [
                str(python),
                "-m",
                "pip",
                "--isolated",
                "wheel",
                "--no-deps",
                "--wheel-dir",
                str(evidence / "wheel"),
                ".",
            ],
            cwd=checkout,
        )
        probe = run(
            "environment",
            [
                str(python),
                "-I",
                "-c",
                (
                    "import json,platform,sys,site;from importlib.metadata import distribution;"
                    "names=['epc-digital-delivery-control-tower','ifcopenshell','ifctester','pandas','xmlschema'];"
                    "print(json.dumps({'system':platform.system(),'python':platform.python_version(),"
                    "'venv':sys.prefix!=sys.base_prefix,'user_site_enabled':site.ENABLE_USER_SITE,"
                    "'packages':{n:{'version':distribution(n).version,"
                    "'requires_python':distribution(n).metadata.get('Requires-Python')} "
                    "for n in names}}))"
                ),
            ],
            cwd=output,
            capture=True,
        )
        metadata["environment"] = json.loads(probe)
        if not metadata["environment"]["venv"] or metadata["environment"]["user_site_enabled"]:
            raise RuntimeError("The installed smoke interpreter is not isolated")
        wheel = next((evidence / "wheel").glob("*.whl"))
        with zipfile.ZipFile(wheel) as archive:
            metadata["wheel"] = {
                "filename": wheel.name,
                "contains_doctor_webapp": any(
                    n.startswith("doctor/") for n in archive.namelist()
                ),
                "scope": "Core CLI distribution; Doctor is source-checkout only",
            }
        run(
            "phase2-smoke",
            [
                str(python),
                "-I",
                str(Path(__file__).with_name("phase2_smoke.py")),
                "--checkout",
                str(checkout),
                "--output",
                str(evidence / "smoke.json"),
            ],
            cwd=checkout,
        )
        run("final-tracked-source-status", [git, "diff", "--exit-code"], cwd=checkout)
        metadata["untracked_after_install"] = run(
            "final-untracked-status",
            [git, "ls-files", "--others", "--exclude-standard"],
            cwd=checkout,
            capture=True,
        ).splitlines()
        if metadata["untracked_after_install"]:
            raise RuntimeError(
                "Clean install left untracked files; inspect final-untracked-status.log"
            )
        metadata["status"] = "passed"
    except Exception as error:
        metadata["status"] = "failed"
        metadata["failure"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        (evidence / "clean-install.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-sha", help="Optional exact source SHA guard, used by CI")
    args = parser.parse_args()
    result = verify(args.source, args.output, args.expected_sha)
    print(
        json.dumps(
            {
                "status": result["status"],
                "source_sha": result["source_sha"],
                "steps": len(result["steps"]),
                "environment": result["environment"],
            }
        )
    )


if __name__ == "__main__":
    main()
