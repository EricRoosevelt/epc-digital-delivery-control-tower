"""Characterization snapshots, and the ceremony required to move one.

Three layers of test guard this pipeline, and they are different kinds of
promise:

*Determinism* — two runs over unchanged inputs produce identical bytes. This is
never updated. If it fails, something reads a clock, iterates an unordered
collection, or depends on the machine, and the answer is always to fix that.

*Invariants* — keys are unique, references resolve, derived values recompute,
an issue's state folds out of its own history. These change rarely, and only
when the domain genuinely gains or loses a law.

*Characterization* — the exact bytes and counts a release published. These
legitimately move: adding a column, correcting a value, changing what a rule
says. What must not happen is that they move *by accident*, or that a red test
is made green by quietly rewriting the expectation.

Hence this module. A snapshot records the contract version, the run identities,
the published counts and a digest per artifact. Verifying it is cheap and runs
in continuous integration. Refreshing it requires saying out loud that the
contract changed, and requires the CHANGELOG to already describe the change —
so the record of what moved exists before the expectation does.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from .determinism import atomic_write_bytes, json_bytes
from .domain import FindingStatus, RunBundle

__all__ = [
    "CHANGELOG_NAME",
    "SNAPSHOT_DIRECTORY",
    "build_snapshot",
    "compare_snapshots",
    "changelog_mentions",
    "load_snapshot",
    "snapshot_path",
    "write_snapshot",
]

SNAPSHOT_DIRECTORY = Path("docs") / "contracts"
CHANGELOG_NAME = "CHANGELOG.md"


def snapshot_path(repository_root: Path, contract_version: str) -> Path:
    return repository_root / SNAPSHOT_DIRECTORY / f"contract-{contract_version}.json"


def build_snapshot(
    bundle: RunBundle,
    *,
    legacy_run_id: str,
    artifact_bundle_id: str,
    artifacts: Mapping[str, str],
) -> dict[str, object]:
    """Describe what this run published, in a form worth comparing.

    Both run identities are recorded. The canonical one moves when a checker's
    version or configuration moves, which is a real change to what a validation
    *is*; the legacy one is what the published keys are built on and must not
    move at all while the adapter exists. Recording only one would hide half of
    what a refresh is agreeing to.
    """

    counts = {str(status): 0 for status in FindingStatus}
    for finding in bundle.findings:
        counts[str(finding.status)] += 1

    return {
        "contract_version": bundle.contract_version,
        "validation_run_id": bundle.run.validation_run_id,
        "legacy_run_id": legacy_run_id,
        "artifact_bundle_id": artifact_bundle_id,
        "as_of": bundle.run.as_of,
        "ruleset": {
            "id": bundle.ruleset.ruleset_id,
            "version": bundle.ruleset.version,
            "normalized_digest": bundle.ruleset.normalized_digest,
            "requirements": len(bundle.ruleset.requirements),
        },
        "counts": {
            "projects": len(bundle.projects),
            "models": len(bundle.models),
            "elements": len(bundle.elements),
            "findings": len(bundle.findings),
            "applicable": sum(1 for f in bundle.findings if f.is_applicable),
            "issues": len(bundle.issues),
            "issue_events": len(bundle.issue_events),
            "by_status": counts,
        },
        "artifacts": dict(sorted(artifacts.items())),
    }


def load_snapshot(path: Path) -> dict[str, object]:
    import json

    if not path.is_file():
        raise FileNotFoundError(f"No recorded snapshot at {path}")
    return json.loads(path.read_text("utf-8"))


def write_snapshot(path: Path, snapshot: Mapping[str, object]) -> None:
    atomic_write_bytes(path, json_bytes(dict(snapshot)))


def compare_snapshots(
    recorded: Mapping[str, object],
    current: Mapping[str, object],
) -> list[str]:
    """Every way the current run differs from what was recorded.

    All of them, not the first: when a contract moves it is far more useful to
    see the shape of the move than its alphabetically earliest instance.
    """

    differences: list[str] = []

    for field in (
        "contract_version",
        "validation_run_id",
        "legacy_run_id",
        "artifact_bundle_id",
        "as_of",
    ):
        if recorded.get(field) != current.get(field):
            differences.append(
                f"{field}: recorded {recorded.get(field)!r}, now {current.get(field)!r}"
            )

    recorded_ruleset = recorded.get("ruleset", {})
    current_ruleset = current.get("ruleset", {})
    for field in sorted(set(recorded_ruleset) | set(current_ruleset)):
        if recorded_ruleset.get(field) != current_ruleset.get(field):
            differences.append(
                f"ruleset.{field}: recorded {recorded_ruleset.get(field)!r}, "
                f"now {current_ruleset.get(field)!r}"
            )

    recorded_counts = recorded.get("counts", {})
    current_counts = current.get("counts", {})
    for field in sorted(set(recorded_counts) | set(current_counts)):
        if recorded_counts.get(field) != current_counts.get(field):
            differences.append(
                f"counts.{field}: recorded {recorded_counts.get(field)!r}, "
                f"now {current_counts.get(field)!r}"
            )

    recorded_artifacts = recorded.get("artifacts", {})
    current_artifacts = current.get("artifacts", {})
    for path in sorted(set(recorded_artifacts) | set(current_artifacts)):
        was = recorded_artifacts.get(path)
        now = current_artifacts.get(path)
        if was == now:
            continue
        if was is None:
            differences.append(f"artifact added: {path}")
        elif now is None:
            differences.append(f"artifact no longer produced: {path}")
        else:
            differences.append(f"artifact changed: {path} ({was[:12]} -> {now[:12]})")

    return differences


def changelog_mentions(repository_root: Path, contract_version: str) -> bool:
    """Whether the CHANGELOG already describes this contract version.

    Checked before a refresh, not after, so that the record of *what* moved
    exists before the expectation that says it did.
    """

    path = repository_root / CHANGELOG_NAME
    if not path.is_file():
        return False
    return f"contract {contract_version}" in path.read_text("utf-8").lower()
