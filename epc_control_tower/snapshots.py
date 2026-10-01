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

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from .determinism import atomic_write_bytes, json_bytes
from .domain import FindingStatus, RunBundle
from .identity import (
    KNOWN_NORMALIZED_DIGEST_DERIVATIONS,
    NORMALIZED_DIGEST_DERIVATION,
)

__all__ = [
    "CHANGELOG_NAME",
    "DERIVATION_LEDGER_NAME",
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

#: The data file that says how to read a snapshot recorded before the normalized
#: digest's derivation was written down, and which cross-derivation pairs have
#: been shown to name the same rules. It lives beside the snapshots rather than
#: in this module because both of its lists are facts about what this repository
#: recorded, not about what the code does (AGENTS.md, "constants have three
#: different homes"). Its name does not match ``contract-*.json``, so it is never
#: read as a snapshot.
DERIVATION_LEDGER_NAME = "ruleset-digest-derivations.json"

#: The field a snapshot's ``ruleset`` block records its derivation in.
DERIVATION_FIELD = "normalized_digest_derivation"


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
            # Which derivation produced the digest above. A digest is only ever
            # compared with another of the same derivation (ADR 0005 §5.5).
            DERIVATION_FIELD: NORMALIZED_DIGEST_DERIVATION,
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
    *,
    rule_definitions_digest: str | None,
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

    **Derivations (ADR 0005 §5.5).** Two digests say the same thing only if they
    were derived the same way, and derivation 1 could not see a single facet
    parameter. So every snapshot's derivation is established before any digest is
    compared, and each step refuses rather than guesses:

    * a snapshot records its derivation in ``ruleset.normalized_digest_derivation``,
      and a value outside :data:`~.identity.KNOWN_NORMALIZED_DIGEST_DERIVATIONS`
      is refused (``unknown-derivation``);
    * a snapshot without the field is read as derivation 1 **only** if it is on
      the ledger's closed list by name and SHA-256 (``snapshot-derivation-missing``
      otherwise; ``historical-snapshot-altered`` when a listed file's bytes moved;
      ``historical-snapshot-missing`` when a listed file is gone);
    * under one derivation, the digests must be equal (``version-reused``);
    * across derivations **no rule lets a difference pass**. A ledger migration
      entry must name both sides exactly — id, version, both derivations, both
      digests — the derivation-1 side must be the entry's named baseline snapshot
      byte for byte, and the rules this refresh ran against must still have the
      declared-definitions digest the entry recorded
      (``derivation-migration-missing``, ``migration-evidence-mismatch``).

    ``rule_definitions_digest`` is that last value, from
    :func:`~.coverage.rule_definitions_digest`. It has no default: ``None`` says
    it could not be computed, and no migration entry is then accepted.

    Every problem is returned, each prefixed with its code, and any one of them
    refuses the refresh.
    """

    problems: list[str] = []
    ledger = _read_derivation_ledger(repository_root, problems)
    if ledger is None:
        return problems
    listed = {
        entry["name"]: entry["sha256"] for entry in ledger["derivation_1_snapshots"]
    }

    directory = repository_root / SNAPSHOT_DIRECTORY
    recorded: list[tuple[str, str, Mapping[str, object], int | None]] = []
    paths = sorted(directory.glob("contract-*.json")) if directory.is_dir() else []
    for path in paths:
        raw = path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        document = json.loads(raw.decode("utf-8"))
        derivation = _derivation_of(
            document,
            label=path.name,
            name=path.name,
            sha=sha,
            listed=listed,
            problems=problems,
        )
        recorded.append((path.name, sha, document, derivation))
    present = {name for name, *_ in recorded}
    for name in sorted(set(listed) - present):
        problems.append(
            f"[historical-snapshot-missing] {name} is on the ledger's closed list of "
            "snapshots recorded before derivations were written down, and it is not "
            "in the snapshot directory; a record of what was published is never "
            "deleted to get a refresh through"
        )

    current_sha = hashlib.sha256(json_bytes(dict(current))).hexdigest()
    current_derivation = _derivation_of(
        current,
        label="the current run",
        name=None,
        sha=current_sha,
        listed=listed,
        problems=problems,
    )

    ruleset = _ruleset_block(current)
    ruleset_id = ruleset.get("id")
    version = ruleset.get("version")
    digest = ruleset.get("normalized_digest")
    for name, sha, document, derivation in recorded:
        was = _ruleset_block(document)
        if was.get("id") != ruleset_id or was.get("version") != version:
            continue
        if derivation is None or current_derivation is None:
            # Already refused above: a digest whose derivation is not
            # established is never compared, in either direction.
            continue
        if derivation == current_derivation:
            if was.get("normalized_digest") == digest:
                continue
            problems.append(
                f"[version-reused] {name} already records {ruleset_id} v{version} "
                f"with a different rule set ({was.get('requirements')} requirements, "
                f"digest {str(was.get('normalized_digest'))[:12]}…; now "
                f"{ruleset.get('requirements')} requirements, digest "
                f"{str(digest)[:12]}…)"
            )
            continue
        problem = _cross_derivation_problem(
            ledger,
            ruleset_id=ruleset_id,
            version=version,
            recorded=(name, sha, derivation, was.get("normalized_digest")),
            current=(current_sha, current_derivation, digest),
            rule_definitions_digest=rule_definitions_digest,
        )
        if problem:
            problems.append(problem)
    return problems


def _ruleset_block(document: Mapping[str, object]) -> Mapping[str, object]:
    block = document.get("ruleset", {})
    return block if isinstance(block, Mapping) else {}


def _derivation_of(
    document: Mapping[str, object],
    *,
    label: str,
    name: str | None,
    sha: str,
    listed: Mapping[str, str],
    problems: list[str],
) -> int | None:
    """The derivation a snapshot's digest was computed under, or ``None``.

    ``None`` always comes with a problem appended: an unresolved derivation is a
    refusal, never a default. ``name`` is ``None`` for the snapshot a refresh is
    about to write, which has no file yet; it is recognised as a listed
    historical snapshot only by the SHA-256 of the bytes it would be written as.
    """

    if name is not None and name in listed and sha != listed[name]:
        problems.append(
            f"[historical-snapshot-altered] {name} is on the ledger's closed list with "
            f"SHA-256 {listed[name][:12]}… and its bytes now hash to {sha[:12]}…; a "
            "historical snapshot is read as derivation 1 only while it is the file "
            "that was recorded"
        )
        return None
    ruleset = _ruleset_block(document)
    if DERIVATION_FIELD in ruleset:
        value = ruleset[DERIVATION_FIELD]
        if type(value) is not int or value not in KNOWN_NORMALIZED_DIGEST_DERIVATIONS:
            problems.append(
                f"[unknown-derivation] {label} records {DERIVATION_FIELD} {value!r}; "
                f"this package knows {sorted(KNOWN_NORMALIZED_DIGEST_DERIVATIONS)}, "
                "and a digest whose derivation it does not know is compared with "
                "nothing"
            )
            return None
        return value
    if (name is not None and name in listed) or (
        name is None and sha in set(listed.values())
    ):
        return 1
    problems.append(
        f"[snapshot-derivation-missing] {label} records no {DERIVATION_FIELD} and is "
        f"not on the closed list of historical snapshots in {DERIVATION_LEDGER_NAME}; "
        "a missing derivation is not assumed to be any particular one"
    )
    return None


def _cross_derivation_problem(
    ledger: Mapping[str, object],
    *,
    ruleset_id: object,
    version: object,
    recorded: tuple[str, str, int, object],
    current: tuple[str, int, object],
    rule_definitions_digest: str | None,
) -> str:
    """Why a cross-derivation pair fails, or ``""`` when an entry proves it.

    This is the only way through. An entry proves nothing about a pair it does
    not name exactly, and it proves nothing unless the rules this refresh ran
    against are still the rules the entry was written for.
    """

    name, recorded_sha, recorded_derivation, recorded_digest = recorded
    current_sha, current_derivation, current_digest = current
    pair = {
        (recorded_derivation, recorded_digest),
        (current_derivation, current_digest),
    }
    sides = {recorded_derivation: recorded_sha, current_derivation: current_sha}
    for entry in ledger["migrations"]:
        if entry["ruleset_id"] != ruleset_id or entry["version"] != version:
            continue
        before, after = entry["from"], entry["to"]
        named = {
            (before["derivation"], before["normalized_digest"]),
            (after["derivation"], after["normalized_digest"]),
        }
        if named != pair:
            continue
        baseline = entry["baseline"]
        if sides[before["derivation"]] != baseline["sha256"]:
            return (
                f"[migration-evidence-mismatch] the ledger entry for {ruleset_id} "
                f"v{version} names baseline {baseline['snapshot']} "
                f"({baseline['sha256'][:12]}…), and the derivation-"
                f"{before['derivation']} side of this comparison is not that file"
            )
        expected = entry["evidence"]["rule_definitions_digest"]
        if rule_definitions_digest != expected:
            now = (
                f"digest to {rule_definitions_digest[:12]}…"
                if rule_definitions_digest
                else "have no definitions digest"
            )
            return (
                f"[migration-evidence-mismatch] the ledger entry for {ruleset_id} "
                f"v{version} was written for rules whose declared definitions digest "
                f"to {expected[:12]}…, and the rules this refresh ran against {now}; "
                "the entry says two derivations describe the same rules, and these "
                "are not those rules"
            )
        return ""
    return (
        f"[derivation-migration-missing] {name} records {ruleset_id} v{version} "
        f"under derivation {recorded_derivation} (digest "
        f"{str(recorded_digest)[:12]}…) and this run is derivation "
        f"{current_derivation} (digest {str(current_digest)[:12]}…); digests of "
        f"different derivations are never comparable by themselves, and "
        f"{DERIVATION_LEDGER_NAME} has no migration entry naming exactly this pair"
    )


_HEX = frozenset("0123456789abcdef")


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= _HEX


def _read_derivation_ledger(
    repository_root: Path, problems: list[str]
) -> Mapping[str, object] | None:
    """The ledger, checked for shape, or ``None`` with the reason appended.

    Checked strictly because every answer the guard gives depends on it: a
    malformed entry that was skipped rather than refused would be a way to make
    a historical snapshot, or a migration, quietly drop out of consideration.
    """

    path = repository_root / SNAPSHOT_DIRECTORY / DERIVATION_LEDGER_NAME
    if not path.is_file():
        problems.append(
            f"[derivation-ledger-missing] no {DERIVATION_LEDGER_NAME} beside the "
            "snapshots, so no snapshot recorded without a derivation can be read and "
            "no cross-derivation pair can be proved"
        )
        return None

    def invalid(reason: str) -> None:
        problems.append(
            f"[derivation-ledger-invalid] {DERIVATION_LEDGER_NAME}: {reason}"
        )

    try:
        ledger = json.loads(path.read_bytes().decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        invalid(f"not JSON ({exc})")
        return None
    if not isinstance(ledger, dict) or set(ledger) != {
        "note",
        "derivation_1_snapshots",
        "migrations",
    }:
        invalid("expected exactly the keys note, derivation_1_snapshots, migrations")
        return None

    listed = ledger["derivation_1_snapshots"]
    if not isinstance(listed, list):
        invalid("derivation_1_snapshots is not a list")
        return None
    names: set[str] = set()
    for entry in listed:
        if (
            not isinstance(entry, dict)
            or set(entry) != {"name", "sha256"}
            or not isinstance(entry["name"], str)
            or not entry["name"].startswith("contract-")
            or not entry["name"].endswith(".json")
            or not _is_sha256(entry["sha256"])
            or entry["name"] in names
        ):
            invalid(f"malformed or repeated derivation_1_snapshots entry {entry!r}")
            return None
        names.add(entry["name"])

    migrations = ledger["migrations"]
    if not isinstance(migrations, list):
        invalid("migrations is not a list")
        return None
    seen: set[tuple[str, str]] = set()
    for entry in migrations:
        if not _valid_migration(entry):
            invalid(f"malformed migration entry {entry!r}")
            return None
        for side in (entry["from"], entry["to"]):
            if side["derivation"] not in KNOWN_NORMALIZED_DIGEST_DERIVATIONS:
                problems.append(
                    f"[unknown-derivation] {DERIVATION_LEDGER_NAME} has a migration "
                    f"entry for {entry['ruleset_id']} v{entry['version']} naming "
                    f"derivation {side['derivation']!r}"
                )
                return None
        key = (entry["ruleset_id"], entry["version"])
        if key in seen:
            invalid(
                f"two migration entries for {entry['ruleset_id']} v{entry['version']}; "
                "one rule set version is migrated once"
            )
            return None
        seen.add(key)
    return ledger


def _valid_migration(entry: object) -> bool:
    if not isinstance(entry, dict) or set(entry) != {
        "ruleset_id",
        "version",
        "from",
        "to",
        "baseline",
        "evidence",
    }:
        return False
    if not isinstance(entry["ruleset_id"], str) or not isinstance(entry["version"], str):
        return False
    for side in (entry["from"], entry["to"]):
        if (
            not isinstance(side, dict)
            or set(side) != {"derivation", "normalized_digest"}
            or type(side["derivation"]) is not int
            or not _is_sha256(side["normalized_digest"])
        ):
            return False
    if entry["from"]["derivation"] == entry["to"]["derivation"]:
        return False
    baseline = entry["baseline"]
    if (
        not isinstance(baseline, dict)
        or set(baseline) != {"snapshot", "sha256", "commit"}
        or not isinstance(baseline["snapshot"], str)
        or not _is_sha256(baseline["sha256"])
        or not isinstance(baseline["commit"], str)
    ):
        return False
    evidence = entry["evidence"]
    if (
        not isinstance(evidence, dict)
        or set(evidence) != {"rule_definitions_digest", "rules_git_tree"}
        or not _is_sha256(evidence["rule_definitions_digest"])
        or not isinstance(evidence["rules_git_tree"], dict)
    ):
        return False
    tree = evidence["rules_git_tree"]
    return (
        set(tree) == {"path", "tree", "measured_at"}
        and isinstance(tree["path"], str)
        and isinstance(tree["tree"], str)
        and isinstance(tree["measured_at"], list)
        and all(isinstance(item, str) for item in tree["measured_at"])
    )


def changelog_mentions(repository_root: Path, contract_version: str) -> bool:
    """Whether the CHANGELOG already describes this contract version.

    Checked before a refresh, not after, so that the record of *what* moved
    exists before the expectation that says it did.
    """

    path = repository_root / CHANGELOG_NAME
    if not path.is_file():
        return False
    return f"contract {contract_version}" in path.read_text("utf-8").lower()
