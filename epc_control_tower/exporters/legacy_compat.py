"""Frozen metadata for the legacy projection, keyed by requirement.

The published BCF archive and the Power BI sidecars carry priority, stage,
labels and an assignee. Those came, once, from four constants in a module; then
from the *current* rules' metadata, which meant editing a live rule moved a
frozen published byte. This file is the fix: a pinned document that states what
rule set 0.1 meant, so the legacy projection reads its metadata from here and
never from ``bundle.issues`` or the current grouping policy.

It is keyed by ``requirement_key`` on purpose, not by today's topics or
elements. A topic is a thing the current run happened to produce; a requirement
is what the frozen rule set actually froze. Keying on topics would leave a
newly-surfaced failure of an *old* rule with no metadata to render.

Schema, version and SHA-256 are pinned. The requirement set is checked for exact
equality against the frozen rule set — missing, extra and duplicate keys all
fail — because a compatibility document that has drifted from the rules it
claims to freeze is worse than none.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from ..domain import RuleSet, Severity

__all__ = [
    "COMPAT_SCHEMA_VERSION",
    "FrozenRequirementMeta",
    "LegacyCompatibility",
    "legacy_config_sha256",
    "load_legacy_compatibility",
]

#: The one schema version this loader understands. A document declaring another
#: is rejected rather than guessed at.
COMPAT_SCHEMA_VERSION = "1"


@dataclass(frozen=True, slots=True)
class FrozenRequirementMeta:
    """The frozen metadata one requirement contributes to a legacy topic."""

    requirement_key: str
    rule_id: str
    requirement_id: str
    severity: Severity
    priority: str
    stage: str
    owner_role: str
    discipline_scope: tuple[str, ...]
    labels: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LegacyCompatibility:
    """A parsed, verified legacy compatibility document.

    ``source_sha256`` is the SHA-256 of the exact bytes this was loaded from —
    the value ``control-tower.toml`` pins and the loader checks. It is what the
    legacy exporters fold into their configuration identity, deliberately in
    place of a digest recomputed from the parsed content: a rebuilt semantic
    digest can miss a field the parser drops, or stay put when the file is
    reformatted, and the whole point is that the pinned bytes move the identity.
    """

    schema_version: str
    ruleset_id: str
    ruleset_version: str
    requirements: dict[str, FrozenRequirementMeta]
    source_sha256: str

    def by_key(self, requirement_key: str) -> FrozenRequirementMeta:
        return self.requirements[requirement_key]

    def validate_against_ruleset(self, frozen: RuleSet) -> None:
        """Fail unless this document freezes exactly the frozen rule set.

        Three ways to be wrong, all fatal: a requirement the rules have and the
        document does not (missing), one the document has and the rules do not
        (extra), and a key the document lists twice (duplicate — caught at load).
        The published archive is reproduced from this metadata, so a set that
        does not match the rules it claims to freeze would reproduce the wrong
        thing silently.
        """

        if self.ruleset_id != frozen.ruleset_id or self.ruleset_version != frozen.version:
            raise ValueError(
                f"legacy compatibility is for rule set {self.ruleset_id} "
                f"{self.ruleset_version}, but the frozen rule set is "
                f"{frozen.ruleset_id} {frozen.version}"
            )
        have = set(self.requirements)
        want = {requirement.requirement_key for requirement in frozen.requirements}
        missing = sorted(want - have)
        extra = sorted(have - want)
        if missing or extra:
            raise ValueError(
                "legacy compatibility requirement set does not match the frozen "
                f"rule set: missing {missing}, extra {extra}"
            )


def legacy_config_sha256(
    *,
    subdirectory: str,
    project_id: str | None,
    frozen_ruleset: RuleSet | None,
    compat: "LegacyCompatibility | None",
) -> str:
    """Configuration identity for a legacy exporter.

    Covers every construction parameter that changes where the archive is
    written or what bytes it contains: the output subdirectory, the project the
    projection is scoped to, the full frozen rule-set identity, and the frozen
    compatibility metadata. Folded into ``artifact_bundle_id`` so that
    re-scoping or re-freezing the legacy projection moves the bundle id.
    """

    from ..determinism import canonical_json_document

    document = {
        "subdirectory": subdirectory,
        "project_id": project_id or "",
        "frozen_ruleset": (
            {
                "id": frozen_ruleset.ruleset_id,
                "version": frozen_ruleset.version,
                "normalized_digest": frozen_ruleset.normalized_digest,
                "source_blob_sha256": frozen_ruleset.source_blob_sha256,
            }
            if frozen_ruleset is not None
            else None
        ),
        "compat_sha256": compat.source_sha256 if compat is not None else "",
    }
    return hashlib.sha256(
        canonical_json_document(document).encode("utf-8")
    ).hexdigest()


def load_legacy_compatibility(
    path: Path, *, expected_sha256: str = ""
) -> LegacyCompatibility:
    """Read and verify the compatibility document at ``path``.

    When ``expected_sha256`` is given the raw bytes must hash to it, so a swapped
    or edited document is caught before any published byte is built from it.
    """

    raw = Path(path).read_bytes()
    source_sha256 = hashlib.sha256(raw).hexdigest()
    if expected_sha256 and source_sha256 != expected_sha256:
        raise ValueError(
            f"legacy compatibility {path} has sha256 {source_sha256}, expected "
            f"{expected_sha256}"
        )

    document = json.loads(raw.decode("utf-8"))
    schema_version = str(document.get("schema_version", ""))
    if schema_version != COMPAT_SCHEMA_VERSION:
        raise ValueError(
            f"legacy compatibility {path} declares schema_version "
            f"{schema_version!r}; this loader understands {COMPAT_SCHEMA_VERSION!r}"
        )

    ruleset = document.get("ruleset", {})
    raw_requirements = document.get("requirements", {})
    if not isinstance(raw_requirements, dict):
        raise ValueError(f"{path}: requirements must be an object keyed by requirement_key")

    # JSON objects cannot express a duplicate key to this point — the parser
    # keeps the last — so duplicate detection is done on the raw text, where a
    # repeated key is still visible.
    _reject_duplicate_keys(raw, path)

    requirements: dict[str, FrozenRequirementMeta] = {}
    for requirement_key, meta in raw_requirements.items():
        severity_name = str(meta.get("severity", "")).upper()
        try:
            severity = Severity[severity_name]
        except KeyError:
            raise ValueError(
                f"{path}: requirement {requirement_key} has severity "
                f"{severity_name!r}, not one of {[s.name for s in Severity]}"
            ) from None
        requirements[requirement_key] = FrozenRequirementMeta(
            requirement_key=requirement_key,
            rule_id=str(meta.get("rule_id", "")),
            requirement_id=str(meta.get("requirement_id", "")),
            severity=severity,
            priority=str(meta.get("priority", "")),
            stage=str(meta.get("stage", "")),
            owner_role=str(meta.get("owner_role", "")),
            discipline_scope=tuple(str(item) for item in meta.get("discipline_scope", [])),
            labels=tuple(str(item) for item in meta.get("labels", [])),
        )

    return LegacyCompatibility(
        schema_version=schema_version,
        ruleset_id=str(ruleset.get("id", "")),
        ruleset_version=str(ruleset.get("version", "")),
        requirements=requirements,
        source_sha256=source_sha256,
    )


def _reject_duplicate_keys(raw: bytes, path: Path) -> None:
    """Fail if any requirement_key appears twice in the raw document.

    ``json.loads`` silently keeps the last value for a repeated key, so a
    duplicate would otherwise pass unnoticed. ``object_pairs_hook`` sees the
    pairs before they are collapsed.
    """

    def _hook(pairs):
        seen: set[str] = set()
        for key, _ in pairs:
            if key in seen:
                raise ValueError(f"{path}: duplicate key {key!r}")
            seen.add(key)
        return dict(pairs)

    json.loads(raw.decode("utf-8"), object_pairs_hook=_hook)
