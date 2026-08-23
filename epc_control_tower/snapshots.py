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
    "recorded_snapshots",
    "ruleset_version_conflicts",
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


def recorded_snapshots(repository_root: Path) -> list[tuple[Path, Mapping[str, object]]]:
    """Every contract snapshot this repository has kept, oldest first by name."""

    directory = repository_root / SNAPSHOT_DIRECTORY
    if not directory.is_dir():
        return []
    return [
        (path, load_snapshot(path)) for path in sorted(directory.glob("contract-*.json"))
    ]


def ruleset_version_conflicts(
    repository_root: Path,
    current: Mapping[str, object],
) -> list[str]:
    """Where the incoming rule set reuses a version tag for different rules.

    The rule being enforced is one sentence:

        **A ``(ruleset_id, version)`` pair names exactly one set of rules.**

    It is not a restatement of the contract ceremony. The contract version says
    what this project *publishes*; the rule set version says what it *asked
    for*, and those are different questions with different audiences. A delivery
    keeps the rule set it was validated against, and keeps it by name.

    Nor is the version redundant with the normalized digest, though it is easy
    to think so. The digest already carries identity — add a rule and every key
    moves whether or not the tag does, which is exactly why nothing broke while
    the tag stood still. What the digest cannot do is *be quoted*. Nobody
    writes "we validated against 8a5585c3efc9c774…" in a delivery plan, and no
    two digests can be compared for which came first. The tag is the readable
    name for the thing the digest identifies, and a name that points at three
    different things is worse than no name.

    Checked against every recorded snapshot rather than only the previous one,
    so that reverting a tag to reuse an old number is caught too.
    """

    ruleset = current.get("ruleset", {})
    ruleset_id = ruleset.get("id")
    version = ruleset.get("version")
    digest = ruleset.get("normalized_digest")

    conflicts = []
    for path, recorded in recorded_snapshots(repository_root):
        was = recorded.get("ruleset", {})
        if was.get("id") != ruleset_id or was.get("version") != version:
            continue
        if was.get("normalized_digest") == digest:
            continue
        conflicts.append(
            f"{path.name} already records {ruleset_id} v{version} with a "
            f"different rule set ({was.get('requirements')} requirements, "
            f"digest {str(was.get('normalized_digest'))[:12]}…; now "
            f"{ruleset.get('requirements')} requirements, digest "
            f"{str(digest)[:12]}…)"
        )
    return conflicts


def changelog_mentions(repository_root: Path, contract_version: str) -> bool:
    """Whether the CHANGELOG already describes this contract version.

    Checked before a refresh, not after, so that the record of *what* moved
    exists before the expectation that says it did.
    """

    path = repository_root / CHANGELOG_NAME
    if not path.is_file():
        return False
    return f"contract {contract_version}" in path.read_text("utf-8").lower()
