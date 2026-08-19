"""Stable identity for everything this system publishes.

The important idea here is that *one* run identity is not enough. The previous
design derived a single ``run_id`` from the rules and the model hashes and then
used it for three unrelated jobs: naming the validation, stamping the
execution, and keying the outputs. That conflation is why a wall-clock
timestamp had to be frozen to a constant — time had nowhere to live that was
not also an input to determinism.

Three identities, with three different jobs:

``validation_run_id``
    Depends only on what can change the findings: model content, rule content,
    the version and configuration of each participating checker, and a logical
    ``as_of`` where a rule genuinely depends on a date. Never the wall clock,
    never the output contract, never the exporters.

``execution_id``
    Identifies one concrete execution — when it ran, where, with which tool
    version. Recorded for audit and kept out of every deterministic artifact.

``artifact_bundle_id``
    Identifies a set of outputs: the validation plus the output contract
    version plus each exporter's version and configuration. Two bundles can
    share a validation and still differ because an exporter changed.

The consequence worth stating: identical inputs give an identical
``validation_run_id``, identical findings, an identical ``artifact_bundle_id``,
and therefore byte-identical artifacts, while ``execution_id`` differs on every
run and touches nothing.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from collections.abc import Iterable

from .determinism import canonical_json_document, canonical_json_sequence
from .domain import ComponentFingerprint, Requirement

__all__ = [
    "IDENTITY_NAMESPACE",
    "ComponentFingerprint",
    "build_artifact_bundle_id",
    "build_execution_id",
    "build_finding_key",
    "build_issue_event_key",
    "build_issue_key",
    "build_requirement_key",
    "build_ruleset_normalized_digest",
    "build_validation_run_id",
    "new_execution_nonce",
    "uuid5_from_values",
]

# ``ComponentFingerprint`` is defined in :mod:`~.domain` — it is a domain
# concept — but is imported and re-exported here because every caller that
# builds one is already reaching for this module.

#: Project-private UUIDv5 namespace. Changing this value would re-key every
#: published artifact, so it is fixed for the lifetime of the project.
IDENTITY_NAMESPACE = uuid.UUID("7611c2a0-c29a-50fa-b00d-5058d25a41d3")

_SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def uuid5_from_values(
    identity_type: str,
    values: Iterable[object],
    version: int = 1,
) -> str:
    """Build a stable lowercase UUIDv5 from a typed, ordered payload.

    The type prefix keeps different kinds of key in separate spaces, so a
    requirement and a finding built from the same strings cannot collide. The
    version lets a derivation change without silently reusing old keys.
    """

    name = f"{identity_type}:v{version}:{canonical_json_sequence(values)}"
    return str(uuid.uuid5(IDENTITY_NAMESPACE, name))


def _require_slug(value: str, label: str) -> str:
    if not _SLUG.match(value):
        raise ValueError(f"{label} must be a slug, got {value!r}")
    return value


def _require_text(value: str, label: str) -> str:
    if not value:
        raise ValueError(f"{label} must not be empty")
    return value


def build_requirement_key(rule_id: str, requirement_id: str) -> str:
    """Return the stable key for one requirement within a rule.

    Depends only on the rule's own identity, so a requirement keeps its key
    across runs, contract versions, and model changes.
    """

    return uuid5_from_values("requirement", [rule_id, requirement_id])


def build_ruleset_normalized_digest(
    *,
    ruleset_id: str,
    version: str,
    requirements: Iterable[Requirement],
    milestones: Iterable[tuple[str, str]] = (),
) -> str:
    """Digest what a rule set *says*, independent of how it was written.

    Computed from the parsed requirements rather than from the source file, so
    it survives reformatting, re-indentation and a change of line endings, and
    so rule sets loaded from different source formats stay comparable. Only a
    change to the rules themselves moves it.

    This is the digest that feeds :func:`build_validation_run_id`. The raw
    bytes of the source artifact are recorded separately as provenance and take
    no part in identity — hashing them would mean a whitespace edit re-keyed
    every finding.
    """

    _require_slug(ruleset_id, "ruleset_id")
    _require_slug(version, "ruleset version")

    document = {
        "ruleset_id": ruleset_id,
        "version": version,
        "milestones": [
            {"stage": stage, "due": due} for stage, due in sorted(milestones)
        ],
        "requirements": [
            {
                "rule_id": requirement.rule_id,
                "requirement_id": requirement.requirement_id,
                "requirement_key": requirement.requirement_key,
                "specification_label": requirement.specification_label,
                "requirement_label": requirement.requirement_label,
                "checker": requirement.checker,
                "facet_kinds": sorted(requirement.facet_kinds),
                "severity": str(requirement.severity),
                "owner_role": requirement.owner_role,
                "stage": requirement.stage,
                "discipline_scope": sorted(requirement.discipline_scope),
                "citation": requirement.citation,
                "priority": requirement.priority,
                "labels": list(requirement.labels),
            }
            for requirement in sorted(
                requirements, key=lambda item: (item.rule_id, item.requirement_id)
            )
        ],
    }
    return hashlib.sha256(
        canonical_json_document(document).encode("utf-8")
    ).hexdigest()


def build_validation_run_id(
    *,
    ruleset_id: str,
    ruleset_version: str,
    ruleset_normalized_digest: str,
    models: Iterable[tuple[str, str]],
    checkers: Iterable[ComponentFingerprint],
    as_of: str,
) -> str:
    """Derive the deterministic identity of a validation.

    ``models`` is an iterable of ``(model_key, content_sha256)``. Both it and
    ``checkers`` are sorted here, so the caller's ordering cannot leak into the
    identity.

    ``ruleset_normalized_digest`` is the *semantic* digest from
    :func:`build_ruleset_normalized_digest`, not a hash of the source file.
    Reformatting a rule document must not change what a validation is.

    ``as_of`` is a *logical* date. It belongs in the identity because a rule
    that depends on a date genuinely produces different findings on different
    dates. It is not the wall clock, and it must not be read from one.
    """

    _require_slug(ruleset_id, "ruleset_id")
    _require_slug(ruleset_version, "ruleset_version")

    document = {
        "as_of": as_of,
        "checkers": [
            fingerprint.as_document()
            for fingerprint in sorted(checkers, key=lambda item: item.component_id)
        ],
        "models": [
            {"model_key": model_key, "content_sha256": content_sha256}
            for model_key, content_sha256 in sorted(models)
        ],
        "ruleset": {
            "id": ruleset_id,
            "version": ruleset_version,
            "normalized_digest": ruleset_normalized_digest,
        },
    }
    digest = hashlib.sha256(
        canonical_json_document(document).encode("utf-8")
    ).hexdigest()
    return f"{ruleset_id}-v{ruleset_version}-{digest[:16]}"


def new_execution_nonce() -> str:
    """Fresh randomness distinguishing executions that share a clock reading."""

    return uuid.uuid4().hex


def build_execution_id(
    *,
    started_at: str,
    platform: str,
    tool_version: str,
    nonce: str,
) -> str:
    """Identify one concrete execution.

    The nonce is required rather than optional: timestamps have finite
    resolution, and two runs started inside the same tick on the same host with
    the same tool version would otherwise share an id and quietly collapse into
    one audit record. Use :func:`new_execution_nonce` unless you are replaying
    a recorded execution, in which case pass the recorded nonce back.

    This value changes on every run by design, and nothing deterministic may
    consume it.
    """

    _require_text(nonce, "nonce")
    return uuid5_from_values("execution", [started_at, platform, tool_version, nonce])


def build_artifact_bundle_id(
    *,
    validation_run_id: str,
    contract_version: str,
    exporters: Iterable[ComponentFingerprint],
) -> str:
    """Identify one set of exported artifacts."""

    document = {
        "contract_version": contract_version,
        "exporters": [
            fingerprint.as_document()
            for fingerprint in sorted(exporters, key=lambda item: item.component_id)
        ],
        "validation_run_id": validation_run_id,
    }
    digest = hashlib.sha256(
        canonical_json_document(document).encode("utf-8")
    ).hexdigest()
    return f"bundle-{digest[:16]}"


def build_finding_key(
    *,
    validation_run_id: str,
    model_key: str,
    requirement_key: str,
    element_key: str,
) -> str:
    """Return the stable key for one normalised finding.

    ``element_key`` is empty for a specification-level ``N/A``; it is
    normalised to ``""`` rather than omitted so that the payload keeps a fixed
    arity.
    """

    return uuid5_from_values(
        "finding",
        [validation_run_id, model_key, requirement_key, element_key or ""],
    )


def build_issue_key(
    *,
    validation_run_id: str,
    grouping_policy: str,
    group_ref: str,
) -> str:
    """Return the stable key for one grouped issue.

    ``group_ref`` is whatever the policy grouped on — an element key, a
    requirement key, a model key. Including the policy id means two policies
    that happen to group on the same value still produce distinct issues.
    """

    return uuid5_from_values(
        "issue",
        [validation_run_id, grouping_policy, group_ref],
    )


def build_issue_event_key(
    *,
    issue_key: str,
    sequence: int,
    event_type: str,
) -> str:
    """Return the stable key for one entry in an issue's history."""

    return uuid5_from_values("issue-event", [issue_key, str(sequence), event_type])
