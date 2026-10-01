"""Recheck envelopes the Doctor screens have to word correctly, built for tests.

Not a test module, and **not adapter scenarios**: nothing here is evaluated. Each
case is the adapter's own ``recheck-comparison`` envelope with its successor
section replaced by one assembled through the Framework's record types
(:class:`EvidenceCarryOver`, :class:`MemberDisposition`,
:class:`ContextComparison`, :class:`RecheckOutcome`). Going through those
constructors is the point: a state paired with a reason it does not belong to,
or ``changed_aspects`` on a row that may not carry them, is refused here rather
than rendered, so the shapes below cannot drift from what a record can hold.

What these cases are for is the presentation: does the page say the right
sentence for a state, a reason, a changed aspect and a re-issued side. Whether
the Framework *produces* such a row for a given edit is the Framework's own
suite (``test_purpose_recheck.py``), and the adapter's scenarios when it has
them.

Every citation minted here carries the fixture marker, as the fixture discipline
requires of any value that is not real validation output.
"""

from __future__ import annotations

import copy
import functools

from epc_control_tower.purpose.assessment.record import (
    ContextComparison,
    EvidenceCarryOver,
    MemberDisposition,
    RecheckOutcome,
    Subject,
)

__all__ = ["HANDOVER", "REISSUE_SIDES", "recheck_cases"]

MARKER = "fixture"

#: Role names no Pack uses, so a screen that hardcoded a discipline shows it.
HANDOVER = {"from_role": "交出角色甲", "to_role": "接收角色乙"}

#: ``case name -> which sides get a new content id``.
REISSUE_SIDES = {
    "reissue-none": (False, False),
    "reissue-producing": (True, False),
    "reissue-consuming": (False, True),
    "reissue-both": (True, True),
}


def _finding(name: str) -> str:
    return f"{MARKER}/finding/{name}"


def _determination(name: str) -> str:
    return f"{MARKER}-determination/{name}"


def _digest(letter: str) -> str:
    return letter * 64


@functools.cache
def _base() -> dict[str, object]:
    from internal.doctor_adapter import scenario_envelope

    return scenario_envelope("recheck-comparison")


def _comparison(base: dict[str, object], producing: bool, consuming: bool) -> ContextComparison:
    context = base["record"]["request"]["model_version_context"]
    prior_producing = (context["producing"]["model_key"], context["producing"]["content_id"])
    prior_consuming = (context["consuming"]["model_key"], context["consuming"]["content_id"])

    def reissued(version: tuple[str, str]) -> tuple[str, str]:
        return (version[0], f"{MARKER}-content/{version[0]}-reissued-not-a-real-export")

    return ContextComparison(
        prior_producing=prior_producing,
        producing=reissued(prior_producing) if producing else prior_producing,
        prior_consuming=prior_consuming,
        consuming=reissued(prior_consuming) if consuming else prior_consuming,
    )


def _present_target(base: dict[str, object]) -> tuple[str, int, str, tuple[str, ...]]:
    """A current subscope that carries a route, and its first member."""

    for activity in base["record"]["activities"]:
        for subscope in activity["subscopes"]:
            if "route" in subscope:
                return (
                    activity["activity_ref"],
                    subscope["ordinal"],
                    subscope["verdict"],
                    tuple(subscope["members"][0]["keys"]),
                )
    raise LookupError("the base record has no subscope with a route")


def _outcome(
    base: dict[str, object],
    *,
    carry_over: tuple[EvidenceCarryOver, ...],
    dispositions: tuple[MemberDisposition, ...] | None = None,
    condition_status: str = "named-outcome-not-observed",
) -> RecheckOutcome:
    activity_ref, ordinal, verdict, keys = _present_target(base)
    member = Subject(keys=keys)
    if dispositions is None:
        dispositions = (
            MemberDisposition(
                member=member,
                disposition="present",
                current_ordinals=(ordinal,),
                current_verdicts=(verdict,),
                current_leaf_outcomes=("not-yet-determined",),
            ),
        )
    return RecheckOutcome(
        activity_ref=activity_ref,
        subscope_ordinal=7,
        prior_verdict="BLOCKED",
        prior_resolution_kind="fixture-prior-resolution-kind",
        prior_recheck_condition="Fixture condition: the named outcome is reported.",
        prior_leaf_evidence_requirement_id="fixture-leaf-requirement",
        prior_members=tuple(item.member for item in dispositions),
        dispositions=dispositions,
        carry_over=carry_over,
        correspondence="complete",
        named_outcome="fixture-outcome",
        condition_status=condition_status,
        condition_basis="Fixture basis: what the record read, quoted as the record would.",
    )


def _case(
    *,
    carry_over: tuple[EvidenceCarryOver, ...],
    reissued: tuple[bool, bool] = (False, False),
    dispositions: tuple[MemberDisposition, ...] | None = None,
    condition_status: str = "named-outcome-not-observed",
) -> dict[str, object]:
    envelope = copy.deepcopy(_base())
    record = envelope["record"]
    record["request"]["model_version_context"]["handover"].update(HANDOVER)
    record["successor"]["model_version_context_comparison"] = _comparison(
        _base(), *reissued
    ).as_document()
    record["successor"]["subscopes"] = [
        _outcome(
            _base(),
            carry_over=carry_over,
            dispositions=dispositions,
            condition_status=condition_status,
        ).as_document()
    ]
    return envelope


def _finding_row(name: str, state: str, reason: str, **more: object) -> EvidenceCarryOver:
    return EvidenceCarryOver(
        citation=_finding(f"sealed-{name}"),
        citation_kind="finding",
        state=state,
        reason=reason,
        **more,
    )


def _changed(name: str, *aspects: str, key_changed: str = "yes") -> EvidenceCarryOver:
    return _finding_row(
        name,
        "changed",
        "finding-changed",
        current_citation=_finding(f"{'current' if key_changed == 'yes' else 'sealed'}-{name}"),
        key_changed=key_changed,
        changed_aspects=tuple(sorted(aspects)),
    )


@functools.cache
def recheck_cases() -> dict[str, dict[str, object]]:
    """``name -> envelope``. Callers must not mutate what they are handed."""

    equivalent_rekeyed = _finding_row(
        "rekeyed",
        "equivalent",
        "finding-equivalent",
        current_citation=_finding("current-rekeyed"),
        key_changed="yes",
    )
    cases = {
        # One row per state, on one page.
        "four-states": _case(
            carry_over=(
                equivalent_rekeyed,
                _changed("relaxed", "finding-content", "requirement-semantics"),
                _finding_row("gone", "no-counterpart", "no-counterpart-in-the-cited-run"),
                _finding_row(
                    "pre-1.7", "not-provable", "sealed-citation-has-no-comparison-basis"
                ),
            )
        ),
        # Every citation got a new key and nothing else moved.
        "only-rekeyed": _case(
            carry_over=(
                equivalent_rekeyed,
                _finding_row(
                    "same-key",
                    "equivalent",
                    "finding-equivalent",
                    current_citation=_finding("sealed-same-key"),
                    key_changed="no",
                ),
                EvidenceCarryOver(
                    citation=_determination("same-document"),
                    citation_kind="determination",
                    state="equivalent",
                    reason="determination-same-reference-same-content",
                    sealed_content_digest=_digest("a"),
                    current_content_digest=_digest("a"),
                ),
            )
        ),
        # The rule's predicate was edited and the finding reads the same.
        "semantics-same-outcome": _case(
            carry_over=(_changed("retyped", "requirement-semantics"),)
        ),
        "checker-changed": _case(
            carry_over=(_changed("upgraded", "checker", key_changed="no"),)
        ),
        "determination-states": _case(
            carry_over=(
                EvidenceCarryOver(
                    citation=_determination("re-decided"),
                    citation_kind="determination",
                    state="changed",
                    reason="determination-content-changed-under-the-same-reference",
                    sealed_content_digest=_digest("a"),
                    current_content_digest=_digest("b"),
                ),
                EvidenceCarryOver(
                    citation=_determination("superseded"),
                    citation_kind="determination",
                    state="no-counterpart",
                    reason="determination-not-cited-by-this-record",
                    sealed_content_digest=_digest("c"),
                ),
            )
        ),
        "not-provable-reasons": _case(
            carry_over=(
                _finding_row(
                    "pre-1.7", "not-provable", "sealed-citation-has-no-comparison-basis"
                ),
                _finding_row(
                    "future-basis",
                    "not-provable",
                    "comparison-basis-version-unknown",
                    cause="basis_version 99",
                ),
                _finding_row(
                    "subject-gone",
                    "not-provable",
                    "subject-not-present",
                    cause="element-deleted-in-reissued-model",
                ),
                _finding_row(
                    "ambiguous",
                    "not-provable",
                    "counterpart-not-unique",
                    cause=",".join((_finding("candidate-1"), _finding("candidate-2"))),
                ),
                _finding_row(
                    "no-semantics", "not-provable", "requirement-semantics-basis-unavailable"
                ),
                _finding_row("partial-basis", "not-provable", "comparison-basis-incomplete"),
                _finding_row(
                    "uncited",
                    "no-counterpart",
                    "counterpart-not-cited-under-the-current-binding",
                ),
            )
        ),
    }
    # The four re-issue situations. On a re-issue the finding rows read the same
    # and are `changed` by model version alone; the sealed determination is not
    # attributable to the new context.
    for name, sides in REISSUE_SIDES.items():
        moved = any(sides)
        cases[name] = _case(
            reissued=sides,
            carry_over=(
                # The cited finding is about the producing model: its model
                # version moves only when that side was re-issued.
                _changed("reissued", "model-version") if sides[0] else equivalent_rekeyed,
                EvidenceCarryOver(
                    citation=_determination("prior-context"),
                    citation_kind="determination",
                    state="no-counterpart",
                    reason=(
                        "determination-not-attributable-to-this-context"
                        if moved
                        else "determination-not-cited-by-this-record"
                    ),
                    sealed_content_digest=_digest("d"),
                ),
            ),
        )
    # A member the re-issued model no longer holds, beside one that stayed.
    _ref, ordinal, verdict, keys = _present_target(_base())
    cases["member-deleted"] = _case(
        reissued=(True, False),
        condition_status="not-comparable",
        dispositions=(
            MemberDisposition(
                member=Subject(keys=keys),
                disposition="present",
                current_ordinals=(ordinal,),
                current_verdicts=(verdict,),
                current_leaf_outcomes=("not-yet-determined",),
            ),
            MemberDisposition(
                member=Subject(keys=(f"{keys[0].split('::')[0]}::{MARKER}-deleted-element",)),
                disposition="element-deleted-in-reissued-model",
                cause="Fixture cause: the element is absent from the re-issued inventory.",
            ),
        ),
        carry_over=(
            _changed("stayed", "model-version"),
            _finding_row(
                "of-the-deleted",
                "not-provable",
                "subject-not-present",
                cause="element-deleted-in-reissued-model",
            ),
        ),
    )
    # Values no record type would accept, written straight into the document: a
    # later Framework may emit them, and the page must show them as they came.
    unknown = _case(carry_over=(equivalent_rekeyed,))
    successor = unknown["record"]["successor"]
    subscope = successor["subscopes"][0]
    subscope["evidence_carry_over"] = [
        {
            "citation": _finding("sealed-unknown-state"),
            "citation_kind": "finding",
            "state": "superseded-by-policy",
            "reason": "a-reason-from-a-later-contract",
        },
        {
            "citation": _finding("sealed-unknown-aspect"),
            "citation_kind": "finding",
            "state": "changed",
            "reason": "finding-changed",
            "current_citation": _finding("current-unknown-aspect"),
            "key_changed": "maybe",
            "changed_aspects": ["geometry", "model-version"],
        },
        {
            "citation": f"{MARKER}-attestation/unknown-kind",
            "citation_kind": "attestation",
            "state": "equivalent",
            "reason": "finding-equivalent",
        },
    ]
    subscope["dispositions"][0]["disposition"] = "merged-into-another-member"
    del subscope["dispositions"][0]["current_ordinals"]
    subscope["condition_status"] = "partly-observed"
    successor["model_version_context_comparison"]["changed_models"] = ["a-third-model"]
    successor["model_version_context_comparison"]["is_current"] = False
    cases["unrecognised-values"] = unknown

    # Keys a row must carry, left out: shown as not carried, never as a state.
    bare = _case(carry_over=(equivalent_rekeyed,))
    bare["record"]["successor"]["subscopes"][0]["evidence_carry_over"] = [
        {"citation": _finding("sealed-bare"), "citation_kind": "finding"}
    ]
    del bare["record"]["successor"]["subscopes"][0]["condition_status"]
    del bare["record"]["successor"]["subscopes"][0]["dispositions"][0]["disposition"]
    cases["keys-not-carried"] = bare

    contradiction = _case(carry_over=(equivalent_rekeyed,))
    contradiction["record"]["successor"]["model_version_context_comparison"]["is_current"] = (
        False
    )
    cases["reissue-contradiction"] = contradiction

    other_kind = _case(carry_over=(equivalent_rekeyed,))
    other_kind["record"]["successor"]["kind"] = "authorisation"
    cases["successor-not-a-recheck"] = other_kind
    return cases
