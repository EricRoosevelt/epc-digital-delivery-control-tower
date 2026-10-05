import hashlib
import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_DIR = PROJECT_ROOT / "third_party" / "three" / "0.186.1"
EXPECTED_TARBALL_SHA256 = (
    "8cd068708ea44f2c73c944b1cead2ba2f0d5c15c8fc194e5700f4e4f4a033fe7"
)
EXPECTED_LICENSE_SHA256 = (
    "8b378ebe60e2fe500158cb0ac71cb5e8b7d92953c2abcc63a0eb90499653b5bc"
)


def _provenance():
    return json.loads((PROVENANCE_DIR / "provenance.json").read_text(encoding="utf-8"))


def test_three_admission_is_pinned_with_its_license():
    provenance = _provenance()
    license_sha256 = hashlib.sha256((PROVENANCE_DIR / "LICENSE").read_bytes()).hexdigest()

    assert provenance["component"] == "three"
    assert provenance["version"] == "0.186.1"
    assert provenance["upstream"]["tarball_sha256"] == EXPECTED_TARBALL_SHA256
    assert provenance["license"]["spdx"] == "MIT"
    assert provenance["license"]["sha256"] == EXPECTED_LICENSE_SHA256
    assert license_sha256 == EXPECTED_LICENSE_SHA256


def test_vendored_three_files_match_their_recorded_digests():
    # The admission records the bytes before any are committed. Whatever is
    # vendored later is held to these digests, and nothing is vendored while
    # the record says so.
    provenance = _provenance()
    tracked = set(
        subprocess.run(
            ["git", "ls-files", "-z", "--", "third_party/three/0.186.1"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        ).stdout.decode("utf-8").split("\0")
    ) - {""}
    allowed = {
        "third_party/three/0.186.1/LICENSE",
        "third_party/three/0.186.1/provenance.json",
    }
    for entry in provenance["files"]:
        path = f"third_party/three/0.186.1/{entry['vendored_path']}"
        if provenance["repository_policy"]["build_files_committed"]:
            allowed.add(path)
            data = (PROJECT_ROOT / path).read_bytes()
            assert len(data) == entry["size_bytes"]
            assert hashlib.sha256(data).hexdigest() == entry["sha256"]
    assert tracked <= allowed
