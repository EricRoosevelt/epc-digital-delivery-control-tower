"""Compose a project's Pack(s) and Overlay, or refuse.

Composition is where the two halves meet, and where every question ADR 0002
§3.7 says must be answered before an activity can be assessed is answered. The
shape of every answer is the same: **refuse**. Not a warning, not a default, not
a composed object with a "degraded" flag — a project's Overlay either supplies
what its Packs require or the composition raises.

Three refusals are worth naming here rather than leaving to the table below,
because each has an obvious and wrong fallback:

* **A missing ``evidence_bindings`` row does not fall back to R-005.** The Pack
  does not know R-005 exists; "there is no default" is the whole point of
  putting a project's binding in the project's file.
* **A missing ``team_mapping`` row does not fall back to the bound rule's
  ``owner_role``.** ``owner_role`` is the role a *rule author* expected to
  answer for the rule. That is an input to an assignment and not an assignment,
  and reading it here would quietly turn one into the other.
* **``pack_version`` is matched by exact equality, never by range.** Nothing in
  this codebase compares version ranges, and a Pack pinned "compatibly" is a
  Pack whose content can move underneath a project that pinned it.

What composition does **not** do is as load-bearing as what it does. It
resolves ``default_role`` through ``team_mapping`` only to check that the
mapping *exists*; it never produces the resolved assignment. Checkpoint B
separated the Pack's default responsibility policy, the project's role mapping,
and the assignment an assessment makes, and a configuration object that carried
the third would be asserting a decision nobody has made against model versions
nobody has named.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from pathlib import Path

from ..determinism import canonical_json_document
from .errors import PurposeCompositionError
from .model import ComposedPurposeInputs, ProjectOverlay, PurposePack

__all__ = ["build_composition_digest", "compose_purpose_inputs"]


def _fail(code: str, message: str, source: Path | None = None) -> None:
    raise PurposeCompositionError(code, message, source=source)


def compose_purpose_inputs(
    *,
    project_id: str,
    overlay: ProjectOverlay | None,
    packs: Sequence[PurposePack],
    requirement_keys_by_ruleset: Mapping[tuple[str, str], frozenset[str]],
    source: Path | None = None,
) -> ComposedPurposeInputs:
    """Check one project's Overlay against the Packs it binds, or refuse.

    ``packs`` is the Pack library that was actually loaded, and
    ``requirement_keys_by_ruleset`` is the requirement key set of every ruleset
    that was actually loaded, keyed by ``(ruleset_id, ruleset_version)``. Both
    are passed in rather than discovered here, because "does this binding match
    the ruleset actually loaded" is a question about the caller's world, and a
    composer that went and loaded its own ruleset could answer it about a
    different one.
    """

    if overlay is None:
        _fail(
            "overlay-missing",
            f"project {project_id!r} has no [overlay] table, so it has no purpose "
            "assessment available; this is not a pipeline error",
            source,
        )
        raise AssertionError("unreachable")

    available = {pack.pack_id: pack for pack in packs}
    bound: list[PurposePack] = []
    for reference in overlay.packs:
        pack = available.get(reference.pack_id)
        if pack is None:
            _fail(
                "overlay-pack-not-found",
                f"overlay.packs names pack_id {reference.pack_id!r}, which is not present "
                "in the loaded Pack library",
                source,
            )
            raise AssertionError("unreachable")
        if pack.pack_version != reference.pack_version:
            _fail(
                "pack-version-mismatch",
                f"overlay.packs pins {reference.pack_id!r} at pack_version "
                f"{reference.pack_version!r}, but the Pack declares "
                f"{pack.pack_version!r}; the pin is exact and never a range",
                source,
            )
        bound.append(pack)

    _check_bindings_resolve(bound, overlay, requirement_keys_by_ruleset, source)
    _check_every_reachable_role_is_mapped(bound, overlay, source)
    _check_risk_authorisations_resolve(bound, overlay, source)

    ordered = tuple(sorted(bound, key=lambda item: item.pack_id))
    return ComposedPurposeInputs(
        project_id=project_id,
        packs=ordered,
        overlay=overlay,
        composition_digest=build_composition_digest(
            project_id=project_id, packs=ordered, overlay=overlay
        ),
    )


def _check_bindings_resolve(
    packs: Sequence[PurposePack],
    overlay: ProjectOverlay,
    requirement_keys_by_ruleset: Mapping[tuple[str, str], frozenset[str]],
    source: Path | None,
) -> None:
    """Every evidence requirement of every bound Pack can actually be answered.

    ``pack_binding`` and ``insufficient_evidence`` get the identical existence
    and version check, which is exactly why they are separate types: the check
    being the same is what tempts an implementation to make the *references*
    the same, and then nothing downstream can tell a rule that answers the
    question from one that explicitly cannot.
    """

    methods = {
        (item.pack_id, item.evidence_requirement_id)
        for item in overlay.accepted_evidence_methods
    }
    bindings = {
        (item.pack_id, item.evidence_requirement_id): item
        for item in overlay.evidence_bindings
    }

    for pack in packs:
        for requirement in pack.evidence_requirements:
            address = (pack.pack_id, requirement.evidence_requirement_id)
            label = f"{pack.pack_id}::{requirement.evidence_requirement_id}"

            if requirement.binding_source == "pack":
                binding = requirement.pack_binding
                assert binding is not None  # guaranteed by the Pack loader
                _check_requirement_keys(
                    label=f"{label} pack_binding",
                    ruleset_id=binding.ruleset_id,
                    ruleset_version=binding.ruleset_version,
                    keys=binding.requirement_keys,
                    requirement_keys_by_ruleset=requirement_keys_by_ruleset,
                    source=source,
                )
            elif requirement.binding_source == "overlay":
                overlay_binding = bindings.get(address)
                if overlay_binding is None:
                    _fail(
                        "evidence-binding-missing",
                        f"{label} declares binding_source = 'overlay' and this project's "
                        "Overlay has no evidence_bindings row for it. There is no default: "
                        "the Pack does not know which of this project's rules answer the "
                        "question, and falling back to any of them would be inventing one",
                        source,
                    )
                    raise AssertionError("unreachable")
                _check_requirement_keys(
                    label=f"{label} evidence_binding",
                    ruleset_id=overlay_binding.ruleset_id,
                    ruleset_version=overlay_binding.ruleset_version,
                    keys=overlay_binding.requirement_keys,
                    requirement_keys_by_ruleset=requirement_keys_by_ruleset,
                    source=source,
                )
            elif address not in methods:
                _fail(
                    "accepted-method-missing",
                    f"{label} declares binding_source = 'assessment' and this project's "
                    "Overlay has no accepted_evidence_methods row for it",
                    source,
                )

            # An insufficient-evidence reference is checked exactly as hard as
            # a binding, and stays a different thing.
            for reference in requirement.insufficient_evidence:
                _check_requirement_keys(
                    label=f"{label} insufficient_evidence",
                    ruleset_id=reference.ruleset_id,
                    ruleset_version=reference.ruleset_version,
                    keys=(reference.requirement_key,),
                    requirement_keys_by_ruleset=requirement_keys_by_ruleset,
                    source=source,
                )

    known_requirements = {
        (pack.pack_id, requirement.evidence_requirement_id)
        for pack in packs
        for requirement in pack.evidence_requirements
    }
    for item in overlay.evidence_bindings:
        if (item.pack_id, item.evidence_requirement_id) not in known_requirements:
            _fail(
                "evidence-binding-unresolved",
                f"overlay.evidence_bindings addresses "
                f"{item.pack_id}::{item.evidence_requirement_id}, which no bound Pack declares",
                source,
            )
    for item in overlay.accepted_evidence_methods:
        if (item.pack_id, item.evidence_requirement_id) not in known_requirements:
            _fail(
                "accepted-method-unresolved",
                f"overlay.accepted_evidence_methods addresses "
                f"{item.pack_id}::{item.evidence_requirement_id}, which no bound Pack declares",
                source,
            )


def _check_requirement_keys(
    *,
    label: str,
    ruleset_id: str,
    ruleset_version: str,
    keys: Sequence[str],
    requirement_keys_by_ruleset: Mapping[tuple[str, str], frozenset[str]],
    source: Path | None,
) -> None:
    """A reference resolves against the ruleset that was actually loaded.

    Both halves matter. ``requirement_key`` proves the row was found;
    ``(ruleset_id, ruleset_version)`` proves the row still means what the
    author assumed, because severity, applicability, owner role and checker can
    all move underneath a key that never changes.
    """

    address = (ruleset_id, ruleset_version)
    known = requirement_keys_by_ruleset.get(address)
    if known is None:
        _fail(
            "binding-ruleset-mismatch",
            f"{label} names ruleset {ruleset_id!r} version {ruleset_version!r}, which is "
            "not the ruleset actually loaded",
            source,
        )
        raise AssertionError("unreachable")
    missing = sorted(key for key in keys if key not in known)
    if missing:
        _fail(
            "binding-requirement-key-unknown",
            f"{label} references requirement_key(s) {missing}, absent from the loaded "
            f"{ruleset_id} {ruleset_version} rule set",
            source,
        )


def _check_every_reachable_role_is_mapped(
    packs: Sequence[PurposePack], overlay: ProjectOverlay, source: Path | None
) -> None:
    """Every default role a non-READY leaf can name resolves to exactly one team.

    This is a **configuration validity check and nothing else**. It asks "does
    this mapping exist", and deliberately does not produce, cache, or return
    the resolved value: the resolved role or team for an assessment is a
    decision made against particular model versions, and this object has no
    model versions and makes no decisions.
    """

    mapped = {item.role for item in overlay.team_mapping}
    for pack in packs:
        needed: dict[str, str] = {}
        for node in pack.decision_nodes:
            for branch in node.branches:
                if branch.resolution_kind:
                    needed[branch.resolution_kind] = node.node_id
        for resolution_kind, node_id in sorted(needed.items()):
            route = pack.route(resolution_kind)
            if route.default_role not in mapped:
                _fail(
                    "team-mapping-role-missing",
                    f"{pack.pack_id}: the non-READY leaf at node {node_id!r} resolves "
                    f"through {resolution_kind!r} to default_role {route.default_role!r}, "
                    "which this project's overlay.team_mapping does not staff. This is not "
                    "resolved by reading the bound rule's owner_role, and the bare "
                    "default_role string is never reported as though it were an assignee",
                    source,
                )


def _check_risk_authorisations_resolve(
    packs: Sequence[PurposePack], overlay: ProjectOverlay, source: Path | None
) -> None:
    """Every authorisation row addresses a resolution_kind some Pack can produce.

    Note what is *not* checked: that every ``resolution_kind`` has an
    authorisation row. A kind with no row simply has no path to
    ``CONDITIONAL`` in this project, which is a complete and intended state —
    "no authorisation path" is an answer, not a gap.
    """

    kinds = {
        (pack.pack_id, route.resolution_kind)
        for pack in packs
        for route in pack.resolution_routes
    }
    bound_pack_ids = {pack.pack_id for pack in packs}
    for authorisation in overlay.risk_authorisations:
        if authorisation.pack_id not in bound_pack_ids:
            _fail(
                "risk-authorisation-pack-unresolved",
                f"overlay.risk_authorisations addresses pack_id "
                f"{authorisation.pack_id!r}, which this project does not bind",
                source,
            )
        if (authorisation.pack_id, authorisation.resolution_kind) not in kinds:
            _fail(
                "risk-authorisation-kind-unresolved",
                f"overlay.risk_authorisations addresses "
                f"{authorisation.pack_id}::{authorisation.resolution_kind}, which is not a "
                "resolution_kind that Pack declares",
                source,
            )


def build_composition_digest(
    *, project_id: str, packs: Sequence[PurposePack], overlay: ProjectOverlay
) -> str:
    """Identify one composed configuration, deterministically.

    A hash of the **parsed, totally ordered structure** — never of file bytes,
    filenames, mtimes, or filesystem order. Reformatting a Pack must not change
    what the composition is, exactly as reformatting a rule must not re-key a
    finding (``build_ruleset_normalized_digest``).

    It is never an input to ``validation_run_id``, ``requirement_key``,
    ``finding_key``, ``issue_key``, ``group_ref``, any legacy identity, or any
    value under ``data/processed/``, ``reports/`` or ``ids/``. The dependency
    points one way: this cites frozen identities; nothing frozen cites this.
    """

    document = {
        "project_id": project_id,
        "packs": [
            {
                "pack_id": pack.pack_id,
                "pack_schema_version": pack.pack_schema_version,
                "pack_version": pack.pack_version,
                "directions": [
                    {
                        "direction_id": item.direction_id,
                        "from": item.from_discipline,
                        "to": item.to_discipline,
                    }
                    for item in sorted(pack.directions, key=lambda item: item.direction_id)
                ],
                "evidence_requirements": [
                    {
                        "evidence_requirement_id": item.evidence_requirement_id,
                        "binding_source": item.binding_source,
                        "subject_grain": item.subject_grain,
                        "acceptance_condition": item.acceptance_condition,
                        "outcomes": list(item.outcomes),
                        "pack_binding": (
                            {
                                "ruleset_id": item.pack_binding.ruleset_id,
                                "ruleset_version": item.pack_binding.ruleset_version,
                                "requirement_keys": sorted(item.pack_binding.requirement_keys),
                            }
                            if item.pack_binding is not None
                            else None
                        ),
                        "insufficient_evidence": [
                            {
                                "ruleset_id": reference.ruleset_id,
                                "ruleset_version": reference.ruleset_version,
                                "requirement_key": reference.requirement_key,
                                "cannot_answer": reference.cannot_answer,
                            }
                            for reference in sorted(
                                item.insufficient_evidence,
                                key=lambda entry: entry.requirement_key,
                            )
                        ],
                        "pair_source": (
                            {
                                "from_evidence_requirement_id": (
                                    item.pair_source.from_evidence_requirement_id
                                ),
                                "on_outcome": item.pair_source.on_outcome,
                            }
                            if item.pair_source is not None
                            else None
                        ),
                    }
                    for item in sorted(
                        pack.evidence_requirements,
                        key=lambda item: item.evidence_requirement_id,
                    )
                ],
                "activities": [
                    {
                        "activity_id": item.activity_id,
                        "direction_id": item.direction_id,
                        "subject_classes": sorted(item.subject_classes),
                        "evidence_requirement_ids": sorted(item.evidence_requirement_ids),
                        "decision_root_node": item.decision_root_node,
                    }
                    for item in sorted(pack.activities, key=lambda item: item.activity_id)
                ],
                "resolution_routes": [
                    {
                        "resolution_kind": item.resolution_kind,
                        "default_role": item.default_role,
                        "consequence_kinds": sorted(item.consequence_kinds),
                        "next_action": item.next_action,
                        "recheck_condition": item.recheck_condition,
                    }
                    for item in sorted(
                        pack.resolution_routes, key=lambda item: item.resolution_kind
                    )
                ],
                "decision_nodes": [
                    {
                        "node_id": node.node_id,
                        "evidence_requirement_id": node.evidence_requirement_id,
                        "branches": [
                            {
                                "outcome": branch.outcome,
                                "verdict": branch.verdict,
                                "failure_kind": branch.failure_kind,
                                "gap_kind": branch.gap_kind,
                                "next_node": branch.next_node,
                                "renders_inapplicable": sorted(branch.renders_inapplicable),
                            }
                            for branch in sorted(node.branches, key=lambda item: item.outcome)
                        ],
                    }
                    for node in sorted(pack.decision_nodes, key=lambda item: item.node_id)
                ],
            }
            for pack in sorted(packs, key=lambda item: item.pack_id)
        ],
        "overlay": {
            "packs": [
                {"pack_id": item.pack_id, "pack_version": item.pack_version}
                for item in sorted(overlay.packs, key=lambda item: item.pack_id)
            ],
            "evidence_bindings": [
                {
                    "pack_id": item.pack_id,
                    "evidence_requirement_id": item.evidence_requirement_id,
                    "ruleset_id": item.ruleset_id,
                    "ruleset_version": item.ruleset_version,
                    "requirement_keys": sorted(item.requirement_keys),
                }
                for item in sorted(
                    overlay.evidence_bindings,
                    key=lambda item: (item.pack_id, item.evidence_requirement_id),
                )
            ],
            "accepted_evidence_methods": [
                {
                    "pack_id": item.pack_id,
                    "evidence_requirement_id": item.evidence_requirement_id,
                    "method_id": item.method_id,
                    "decision_basis": item.decision_basis,
                }
                for item in sorted(
                    overlay.accepted_evidence_methods,
                    key=lambda item: (item.pack_id, item.evidence_requirement_id),
                )
            ],
            "team_mapping": [
                {
                    "role": item.role,
                    "team_or_person": item.team_or_person,
                    "decision_basis": item.decision_basis,
                }
                for item in sorted(overlay.team_mapping, key=lambda item: item.role)
            ],
            "risk_authorisations": [
                {
                    "pack_id": item.pack_id,
                    "resolution_kind": item.resolution_kind,
                    "may_authorise_roles": sorted(item.may_authorise_roles),
                    "decision_basis": item.decision_basis,
                }
                for item in sorted(
                    overlay.risk_authorisations,
                    key=lambda item: (item.pack_id, item.resolution_kind),
                )
            ],
            "conventions": [
                {
                    "ruleset_id": item.ruleset_id,
                    "ruleset_version": item.ruleset_version,
                    "requirement_key": item.requirement_key,
                    "note": item.note,
                }
                for item in sorted(
                    overlay.conventions,
                    key=lambda item: (
                        item.ruleset_id,
                        item.ruleset_version,
                        item.requirement_key,
                    ),
                )
            ],
            "cost_parameters": dict(sorted(overlay.cost_parameters.items())),
        },
    }
    return hashlib.sha256(canonical_json_document(document).encode("utf-8")).hexdigest()
