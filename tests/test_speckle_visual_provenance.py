import hashlib
import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_DIR = (
    PROJECT_ROOT / "third_party" / "speckle" / "powerbi-visual" / "2026.6.0"
)
EXPECTED_LICENSE_SHA256 = (
    "9fa2ad3ad22e8c41326829c50b396f676410dff7b208aac28daff7470a992db4"
)


def test_external_visual_provenance_and_license_are_pinned():
    provenance = json.loads(
        (PROVENANCE_DIR / "provenance.json").read_text(encoding="utf-8")
    )
    license_sha256 = hashlib.sha256((PROVENANCE_DIR / "LICENSE").read_bytes()).hexdigest()

    assert provenance["component"] == "specklePowerBiVisual"
    assert provenance["version"] == "2026.6.0"
    assert provenance["upstream"]["tag"] == "v2026.6.0"
    assert provenance["upstream"]["commit"] == (
        "3d6a9391b3b5576b0e49ef9e844763681695a299"
    )
    assert provenance["license"]["spdx"] == "Apache-2.0"
    assert provenance["license"]["notice_present_upstream"] is False
    assert provenance["license"]["package_json_metadata_license"] == "MIT"
    assert provenance["license"]["sha256"] == EXPECTED_LICENSE_SHA256
    assert license_sha256 == EXPECTED_LICENSE_SHA256
    assert provenance["repository_policy"] == {
        "custom_visual_bundle_committed": False,
        "custom_visual_ignore_pattern": "dashboard/*.Report/CustomVisuals/",
        "manual_import_required": True,
    }


def test_custom_visual_bundle_is_not_tracked():
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8").split("\0")
    assert not [path for path in tracked if "/CustomVisuals/" in path]
    assert "dashboard/*.Report/CustomVisuals/" in (
        PROJECT_ROOT / ".gitignore"
    ).read_text(encoding="utf-8")
