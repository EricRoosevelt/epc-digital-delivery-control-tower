"""The independent candidate smoke must isolate credentials and validate real mesh arrays."""

import importlib.util
import math
from pathlib import Path

import pytest

from helpers import PROJECT_ROOT

SPEC = importlib.util.spec_from_file_location(
    "phase2_smoke", PROJECT_ROOT / "tools/phase2_smoke.py"
)
smoke = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(smoke)


def test_fresh_user_environment_does_not_read_provider_or_python_node_overrides(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-leave-parent")
    monkeypatch.setenv("OPENAI_MODEL", "must-not-leave-parent")
    monkeypatch.setenv("PYTHONPATH", "unrelated-package-path")
    monkeypatch.setenv("NODE_PATH", "unrelated-node-runtime")
    monkeypatch.setenv("EPC_DOCTOR_CHECKS_DIR", "old-user-projects")
    env = smoke.clean_environment(tmp_path / "new-user")
    for key in (
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "PYTHONPATH",
        "NODE_PATH",
        "EPC_DOCTOR_CHECKS_DIR",
    ):
        assert key not in env
    assert Path(env["HOME"]).is_relative_to(tmp_path)
    assert Path(env["TMP"]).is_dir()
    assert env["PIP_CONFIG_FILE"]


def test_mesh_verification_requires_finite_bound_triangles():
    report = {"elements": [{"element_key": "public::wall"}]}
    geometry = {
        "meshes": [
            {
                "element_key": "public::wall",
                "positions": [0, 0, 0, 1, 0, 0, 0, 1, 0],
                "indices": [0, 1, 2],
            }
        ]
    }
    assert smoke.verify_meshes(report, geometry) == {"elements": 1, "meshes": 1, "triangles": 1}
    geometry["meshes"][0]["indices"] = [0, 1, 3]
    with pytest.raises(AssertionError, match="indices"):
        smoke.verify_meshes(report, geometry)
    geometry["meshes"][0]["indices"] = [0, 1, 2]
    geometry["meshes"][0]["positions"][0] = math.nan
    with pytest.raises(AssertionError, match="Non-finite"):
        smoke.verify_meshes(report, geometry)
    with pytest.raises(AssertionError, match="No real geometry"):
        smoke.verify_meshes(report, {"meshes": []})
