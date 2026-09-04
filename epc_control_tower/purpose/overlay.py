"""Read a project's ``[overlay]`` table.

The Overlay lives inside the same ``project.toml`` the pipeline already reads,
and this module reads it *separately*. That separation is the point: nothing in
the run path looks at ``[overlay]``, so a project can grow one without moving a
published byte, and this reader can refuse an Overlay without a run ever
noticing.

An Overlay declares no ``project_id``. It is a table nested inside a manifest
that already declares one, so its project identity is inherited by nesting — a
field that cannot exist cannot drift out of step with the one it would have
duplicated.
"""

from __future__ import annotations

import tomllib
from collections.abc import Iterable, Mapping
from pathlib import Path
from types import MappingProxyType

from .errors import PurposeCompositionError
from .model import (
    DECISION_BASES,
    AcceptedEvidenceMethod,
    Convention,
    EvidenceBinding,
    OverlayPackRef,
    ProjectOverlay,
    RiskAuthorisation,
    TeamMapping,
)

__all__ = ["load_project_overlay", "read_overlay_table"]

_UNBOUNDED = frozenset({"*", "all", "any", "ALL", "ANY", "All", "Any"})


def _fail(code: str, message: str, source: Path) -> None:
    raise PurposeCompositionError(code, message, source=source)


def _rows(document: Mapping[str, object], key: str, source: Path) -> list[dict]:
    raw = document.get(key, [])
    if not isinstance(raw, list):
        _fail("overlay-field-invalid", f"overlay.{key} must be an array of tables", source)
    for entry in raw:
        if not isinstance(entry, dict):
            _fail("overlay-field-invalid", f"each overlay.{key} entry must be a table", source)
    return list(raw)  # type: ignore[arg-type]


def _text(entry: Mapping[str, object], key: str, label: str, source: Path) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value:
        _fail("overlay-field-missing", f"{label} requires a non-empty {key}", source)
    return str(value)


def _string_tuple(
    entry: Mapping[str, object], key: str, label: str, source: Path
) -> tuple[str, ...]:
    raw = entry.get(key, [])
    if not isinstance(raw, list):
        _fail("overlay-field-invalid", f"{label}: {key} must be an array", source)
    values: list[str] = []
    for item in raw:  # type: ignore[union-attr]
        if not isinstance(item, str) or not item:
            _fail(
                "overlay-field-invalid",
                f"{label}: {key} entries must be non-empty strings",
                source,
            )
        values.append(str(item))
    return tuple(values)


def _decision_basis(entry: Mapping[str, object], label: str, source: Path) -> str:
    """Read the required ``decision_basis``, refusing absence and anything else.

    No default, deliberately. A policy row whose standing is unstated is
    exactly the row a reader takes for a decision, and this is the field that
    keeps a demonstration value from being mistaken for one.
    """

    value = entry.get("decision_basis")
    if value is None:
        _fail(
            "decision-basis-missing",
            f"{label}: decision_basis is required and has no default -- state whether this "
            f"row records a decision this project took ('project-decision') or a value "
            f"written to demonstrate the shape ('illustrative')",
            source,
        )
    if not isinstance(value, str) or value not in DECISION_BASES:
        _fail(
            "decision-basis-invalid",
            f"{label}: decision_basis {value!r} is not one of {list(DECISION_BASES)}",
            source,
        )
    return str(value)


def _duplicates(values: Iterable[tuple[str, ...] | str]) -> list:
    seen: set = set()
    repeated: set = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def read_overlay_table(document: Mapping[str, object], source: Path) -> ProjectOverlay | None:
    """Read ``[overlay]`` from an already-parsed manifest, or ``None`` if absent.

    A project with no ``[overlay]`` has no purpose assessment available, and
    that is **not an error** — the contract 1.6 pipeline is entirely unaffected
    by its absence, because nothing in the pipeline reads this table.
    """

    raw = document.get("overlay")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        _fail("overlay-field-invalid", "[overlay] must be a table", source)

    packs = tuple(
        OverlayPackRef(
            pack_id=_text(entry, "pack_id", "overlay.packs", source),
            pack_version=_text(entry, "pack_version", "overlay.packs", source),
        )
        for entry in _rows(raw, "packs", source)
    )
    repeated = _duplicates(item.pack_id for item in packs)
    if repeated:
        _fail(
            "overlay-pack-duplicate",
            f"overlay.packs names {repeated} more than once",
            source,
        )

    bindings = tuple(
        EvidenceBinding(
            pack_id=_text(entry, "pack_id", "overlay.evidence_bindings", source),
            evidence_requirement_id=_text(
                entry, "evidence_requirement_id", "overlay.evidence_bindings", source
            ),
            ruleset_id=_text(entry, "ruleset_id", "overlay.evidence_bindings", source),
            ruleset_version=_text(
                entry, "ruleset_version", "overlay.evidence_bindings", source
            ),
            requirement_keys=_string_tuple(
                entry, "requirement_keys", "overlay.evidence_bindings", source
            ),
        )
        for entry in _rows(raw, "evidence_bindings", source)
    )
    for binding in bindings:
        if not binding.requirement_keys:
            _fail(
                "evidence-binding-empty",
                f"overlay.evidence_bindings for {binding.evidence_requirement_id!r} "
                "declares no requirement_keys",
                source,
            )
    repeated = _duplicates(
        (item.pack_id, item.evidence_requirement_id) for item in bindings
    )
    if repeated:
        _fail(
            "evidence-binding-duplicate",
            f"overlay.evidence_bindings names {repeated} more than once",
            source,
        )

    methods = tuple(
        AcceptedEvidenceMethod(
            pack_id=_text(entry, "pack_id", "overlay.accepted_evidence_methods", source),
            evidence_requirement_id=_text(
                entry, "evidence_requirement_id", "overlay.accepted_evidence_methods", source
            ),
            method_id=_text(entry, "method_id", "overlay.accepted_evidence_methods", source),
            description=_text(
                entry, "description", "overlay.accepted_evidence_methods", source
            ),
            decision_basis=_decision_basis(
                entry,
                f"overlay.accepted_evidence_methods "
                f"{entry.get('method_id', '<unnamed>')!r}",
                source,
            ),
        )
        for entry in _rows(raw, "accepted_evidence_methods", source)
    )
    repeated = _duplicates(
        (item.pack_id, item.evidence_requirement_id) for item in methods
    )
    if repeated:
        _fail(
            "accepted-method-duplicate",
            f"overlay.accepted_evidence_methods names {repeated} more than once",
            source,
        )

    mappings = tuple(
        TeamMapping(
            role=_text(entry, "role", "overlay.team_mapping", source),
            team_or_person=_text(entry, "team_or_person", "overlay.team_mapping", source),
            decision_basis=_decision_basis(
                entry, f"overlay.team_mapping {entry.get('role', '<unnamed>')!r}", source
            ),
        )
        for entry in _rows(raw, "team_mapping", source)
    )
    repeated = _duplicates(item.role for item in mappings)
    if repeated:
        _fail(
            "team-mapping-role-duplicate",
            f"overlay.team_mapping declares role {repeated} more than once; every default "
            "role must resolve to exactly one team_or_person",
            source,
        )

    authorisations = tuple(
        RiskAuthorisation(
            pack_id=_text(entry, "pack_id", "overlay.risk_authorisations", source),
            resolution_kind=_text(
                entry, "resolution_kind", "overlay.risk_authorisations", source
            ),
            may_authorise_roles=_string_tuple(
                entry, "may_authorise_roles", "overlay.risk_authorisations", source
            ),
            decision_basis=_decision_basis(
                entry,
                f"overlay.risk_authorisations "
                f"{entry.get('resolution_kind', '<unnamed>')!r}",
                source,
            ),
        )
        for entry in _rows(raw, "risk_authorisations", source)
    )
    for authorisation in authorisations:
        if not authorisation.may_authorise_roles:
            _fail(
                "risk-authorisation-roles-unbounded",
                f"overlay.risk_authorisations for {authorisation.resolution_kind!r} lists no "
                "role; an empty list is not 'anyone may', it is a row that cannot authorise",
                source,
            )
        for role in authorisation.may_authorise_roles:
            if role in _UNBOUNDED:
                _fail(
                    "risk-authorisation-roles-unbounded",
                    f"overlay.risk_authorisations for "
                    f"{authorisation.resolution_kind!r} lists {role!r}; there is no "
                    "wildcard and no blanket authorisation in this design",
                    source,
                )
    repeated = _duplicates(
        (item.pack_id, item.resolution_kind) for item in authorisations
    )
    if repeated:
        _fail(
            "risk-authorisation-duplicate",
            f"overlay.risk_authorisations names {repeated} more than once",
            source,
        )

    conventions = tuple(
        Convention(
            ruleset_id=_text(entry, "ruleset_id", "overlay.conventions", source),
            ruleset_version=_text(entry, "ruleset_version", "overlay.conventions", source),
            requirement_key=_text(entry, "requirement_key", "overlay.conventions", source),
            note=_text(entry, "note", "overlay.conventions", source),
        )
        for entry in _rows(raw, "conventions", source)
    )

    cost_parameters = raw.get("cost_parameters", {})
    if not isinstance(cost_parameters, dict):
        _fail("overlay-field-invalid", "overlay.cost_parameters must be a table", source)

    return ProjectOverlay(
        packs=packs,
        evidence_bindings=bindings,
        accepted_evidence_methods=methods,
        team_mapping=mappings,
        risk_authorisations=authorisations,
        conventions=conventions,
        cost_parameters=MappingProxyType(dict(cost_parameters)),
    )


def load_project_overlay(path: Path) -> ProjectOverlay | None:
    """Read the ``[overlay]`` table of one ``project.toml``, if it has one."""

    path = Path(path)
    with path.open("rb") as stream:
        document = tomllib.load(stream)
    return read_overlay_table(document, path)
