"""How one subject's evidence collapses to exactly one outcome.

Three rules live here, and each exists because getting it wrong turns a state
this design distinguishes into one it does not.

**1. ``N/A`` is not ``satisfied``.** ADR 0002 §3.2's own summary of the third
state reads "the unit has at least one finding and none is ``FAIL``", and an
implementation written from that sentence folds a ``N/A`` into a pass — which is
reading an absence as a success. ADR 0003 §3.1 supersedes it with a three-level
precedence, ``FAIL`` > not-covered > ``PASS``, and this module implements that
one. ``N/A`` *is* the not-covered level: it says the specification applied to
nothing, which is the opposite of the claim that this element was checked and
was correct. Every status is matched explicitly and an unrecognised one refuses,
so ``N/A`` can never reach a default branch — the branch it would otherwise
reach is ``satisfied``.

**2. A reading joins on the subject as well as the key.** See
:meth:`~.facts.AssessmentFacts.findings_for`. This repository's own canonical
output carries 57 model-level ``N/A`` findings on the very ``requirement_key``
values ``pcert-sample`` binds to ``asset-identity``.

**3. ``insufficient_evidence`` and ``pack_binding`` stay two code paths.** They
are already two types at composition; here they are two functions with two
return types. :func:`bound_requirement_keys` returns the keys a reading may
reduce, and never sees an ``insufficient_evidence`` reference.
:func:`insufficient_evidence_context` returns citation strings and **cannot**
return an outcome, because its return type has no outcome in it. R-010's ``PASS``
therefore has no route to ``confirmed`` that does not go through editing this
file: one shared lookup is exactly how Checkpoint B case 3's ``UNKNOWN`` would
become a ``READY``.
"""

from __future__ import annotations

from .facts import AssessmentFacts
from ..model import EvidenceRequirement, ProjectOverlay

__all__ = [
    "NOT_COVERED_ABSENCE",
    "NO_FINDING_ABSENCE",
    "UNRESOLVED_OUTCOMES",
    "VALIDATION_BACKED_OUTCOMES",
    "bound_requirement_keys",
    "finding_backed_reading",
    "insufficient_evidence_context",
    "unresolved_outcome",
]

#: The three names ADR 0002 §3.2 fixes for validation-backed evidence, in
#: precedence order: a ``FAIL`` anywhere, then not-covered, then ``PASS``.
VALIDATION_BACKED_OUTCOMES = ("unmet", "not-yet-evaluated", "satisfied")

#: The closed set of names ADR 0002 §3.2 gives the "binding exists, no
#: admissible result yet" state. A Pack that declares none of them, or more than
#: one, has no unambiguous absent state and the assessment refuses rather than
#: guessing which of its outcomes means "not yet".
UNRESOLVED_OUTCOMES = ("not-yet-confirmed", "not-yet-determined", "not-yet-evaluated")

#: No finding exists for this subject under this binding at all — Checkpoint B
#: case 4's chimney.
NO_FINDING_ABSENCE = "no-finding"

#: A finding exists and reports ``N/A``: the specification applied to nothing,
#: so the subject was not covered. Recorded distinctly from ``no-finding``
#: because "nobody looked" and "the look did not apply" are different facts.
NOT_COVERED_ABSENCE = "not-applicable-finding"


def bound_requirement_keys(
    requirement: EvidenceRequirement,
    overlay: ProjectOverlay,
    pack_id: str,
) -> tuple[frozenset[str], str]:
    """The ``requirement_key`` values a reading of this requirement may reduce.

    Returns ``(keys, binding_label)``. Reads ``pack_binding`` for a
    ``binding_source = "pack"`` requirement and the Overlay's
    ``evidence_bindings`` row for an ``"overlay"`` one. It does **not** read
    ``insufficient_evidence``, and there is no branch here that could: a
    reference that says a rule *cannot* answer the question has no business in
    the set of keys that answer it.
    """

    if requirement.binding_source == "pack":
        binding = requirement.pack_binding
        if binding is None:  # pragma: no cover - the Pack loader guarantees it
            raise ValueError(
                f"{requirement.evidence_requirement_id}: binding_source 'pack' with "
                "no pack_binding"
            )
        return (
            frozenset(binding.requirement_keys),
            f"{binding.ruleset_id} {binding.ruleset_version} pack_binding",
        )
    if requirement.binding_source == "overlay":
        for row in overlay.evidence_bindings:
            if (
                row.pack_id == pack_id
                and row.evidence_requirement_id == requirement.evidence_requirement_id
            ):
                return (
                    frozenset(row.requirement_keys),
                    f"{row.ruleset_id} {row.ruleset_version} evidence_binding",
                )
        raise ValueError(
            f"{pack_id}::{requirement.evidence_requirement_id}: no evidence_bindings row"
        )
    raise ValueError(
        f"{requirement.evidence_requirement_id}: binding_source "
        f"{requirement.binding_source!r} is not finding-backed"
    )


def insufficient_evidence_context(
    requirement: EvidenceRequirement, facts: AssessmentFacts
) -> tuple[str, ...]:
    """Citations for the rules declared unable to answer this requirement.

    Returns strings. Not an outcome, not a status, not a set of keys a reading
    could reduce — strings, so that the only thing a caller can do with R-010's
    ``PASS`` is record that it was seen and set aside. The ``cannot_answer``
    sentence travels with the citation, because the reason a pass is not
    evidence is the part a later reader needs.
    """

    citations: list[str] = []
    for reference in requirement.insufficient_evidence:
        observed = sorted(
            finding.finding_key
            for finding in facts.findings
            if finding.requirement_key == reference.requirement_key
        )
        citations.append(
            f"insufficient_evidence {reference.ruleset_id} {reference.ruleset_version} "
            f"{reference.requirement_key} observed={observed} "
            f"context-only: {reference.cannot_answer}"
        )
    return tuple(citations)


def unresolved_outcome(requirement: EvidenceRequirement) -> str:
    """This requirement's "no admissible result yet" outcome.

    Fails closed rather than defaulting. A Pack whose ``outcomes[]`` names none
    of the three unresolved states, or more than one of them, gives the
    assessment no way to say "not yet" without choosing on the Pack author's
    behalf, and choosing is what turns an ``UNKNOWN`` into something else.
    """

    candidates = [name for name in requirement.outcomes if name in UNRESOLVED_OUTCOMES]
    if len(candidates) != 1:
        raise ValueError(
            f"{requirement.evidence_requirement_id}: outcomes {list(requirement.outcomes)} "
            f"name {len(candidates)} unresolved states {UNRESOLVED_OUTCOMES}; exactly "
            "one is required and there is no default"
        )
    return candidates[0]


def finding_backed_reading(
    *,
    element_key: str,
    requirement_keys: frozenset[str],
    facts: AssessmentFacts,
) -> tuple[str, tuple[str, ...], str]:
    """Collapse one subject's findings to one outcome, by explicit precedence.

    Returns ``(outcome, cited finding_keys, absence marker)``. The order below is
    ADR 0003 §3.1's ``FAIL`` > not-covered > ``PASS``, and every status is named:
    an unrecognised one raises rather than falling through, because the branch a
    silent fall-through would reach is ``satisfied``, and reporting an unknown
    status as a pass is the worst outcome available.
    """

    findings = facts.findings_for(element_key, requirement_keys)
    if not findings:
        return "not-yet-evaluated", (), NO_FINDING_ABSENCE

    failed: list[str] = []
    not_applicable: list[str] = []
    passed: list[str] = []
    for finding in findings:
        if finding.status == "FAIL":
            failed.append(finding.finding_key)
        elif finding.status == "N/A":
            not_applicable.append(finding.finding_key)
        elif finding.status == "PASS":
            passed.append(finding.finding_key)
        else:
            raise ValueError(
                f"{finding.finding_key}: status {finding.status!r} is not one of "
                "PASS / FAIL / N/A, and there is no default reading for it"
            )

    if failed:
        return "unmet", tuple(sorted(failed)), ""
    if not_applicable:
        # A specification that applied to nothing did not check this element.
        # Not covered is never satisfied, and this is the branch that says so.
        return "not-yet-evaluated", tuple(sorted(not_applicable)), NOT_COVERED_ABSENCE
    return "satisfied", tuple(sorted(passed)), ""
