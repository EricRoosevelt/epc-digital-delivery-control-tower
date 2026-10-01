"""The fixture entry: the test suite's declared policy, through the same evaluator.

Fixture policy has exactly one source, ``tests/assessment_fixtures.py``, and this
module reuses its builders rather than restating any of them — the Overlay with
two of its three policy tables decided, the determinations nobody has ever made
for ``pcert-sample``, the request declaration, and the second sets of facts a
recheck is asked about. Two copies would drift apart silently. What this module
adds is only the call: composing through the real composer, assessing through the
real entry point and rechecking through the real one, against the validated facts
of :mod:`.validated` instead of the test helper's run, whose rule compilation
writes into this checkout's ``ids/``.

Its envelopes are always ``mode = "fixture"``.

The recheck scenarios
---------------------

Each one succeeds the same first record — or, for one of them, that record in
the shape a record sealed before contract 1.7 has — and answers for **every**
subscope it sealed. They differ only in the evidence the recheck is given, and
no state, reason or changed aspect is chosen here: each is whatever
:func:`~epc_control_tower.purpose.recheck_purpose` recorded.

Three of them ask what a rule edit moves. The edit is one of the named edits in
``tests/rule_edits.py``, applied to the scratch copy of the rule library that
:func:`.validated.scratch_bundle` makes *outside* this checkout, and the shipped
models are then validated against that copy by the real pipeline. ``rules/`` is
never written: R-001 to R-005B are the frozen v0.1 rule set's rules (ADR 0005
§5.7, B-1).

**Everything a recheck scenario was given that the shipped run did not produce
carries the fixture marker**, through
:func:`assessment_fixtures.fixture_revalidated_facts`: the run identifier, every
finding key of the second run, and every content identifier of a model that was
"reissued". That holds for the edited-rule runs too — the checker really ran
there, but over a rule set nobody published, so its findings are not the output
of a published validation run and must not be labelled as one.
"""

from __future__ import annotations

import functools
import sys
from pathlib import Path

from epc_control_tower.purpose import (
    AssessmentRecord,
    AssessmentRequest,
    assess_purpose,
    compose_purpose_inputs,
    facts_from_bundle,
    load_purpose_pack,
    read_overlay_table,
    recheck_purpose,
)

from .envelope import FIXTURE, PROJECT_ROOT, build_envelope
from .validated import requirement_keys_by_ruleset, scratch_bundle, validated_facts

__all__ = [
    "RECHECK_SCENARIOS",
    "declared_request",
    "first_record_envelope",
    "recheck_scenario_envelope",
    "superseding_recheck_envelope",
]

PROJECT_ID = "pcert-sample"


def _fixtures():
    """``tests/assessment_fixtures.py``, imported where it lives."""

    tests = str(PROJECT_ROOT / "tests")
    if tests not in sys.path:
        sys.path.append(tests)
    import assessment_fixtures

    return assessment_fixtures


def declared_request(facts) -> AssessmentRequest:
    """The request the assessment tests declare: every activity of the Pack, over ``hvac``.

    A request is a caller's declaration rather than policy, and it is the same
    declaration whichever entry it is handed to.
    """

    fx = _fixtures()
    pack = load_purpose_pack(fx.PACK_PATH)
    return fx.fixture_request(
        activity_ids=tuple(activity.activity_id for activity in pack.activities),
        facts=facts,
    )


@functools.cache
def _inputs():
    fx = _fixtures()
    facts = validated_facts(PROJECT_ID)
    composed = compose_purpose_inputs(
        project_id=PROJECT_ID,
        # Named as the source, as the fixture itself does: that module is where
        # this policy was written, and pcert-sample's manifest is never edited.
        overlay=read_overlay_table(fx.fixture_overlay_document(), Path(fx.__file__)),
        packs=(load_purpose_pack(fx.PACK_PATH),),
        requirement_keys_by_ruleset=requirement_keys_by_ruleset(),
    )
    return fx, facts, composed, declared_request(facts)


def _first_record() -> AssessmentRecord:
    fx, facts, composed, request = _inputs()
    return assess_purpose(
        request=request,
        composed=composed,
        facts=facts,
        determinations=fx.fixture_determinations(facts=facts),
    )


def first_record_envelope() -> dict[str, object]:
    """The sealed record in which the chimney refines into a slab pair and a roof pair."""

    return build_envelope(FIXTURE, _first_record)


def superseding_recheck_envelope() -> dict[str, object]:
    """The successor to that record's ``(chimney, roof)`` subscope, after a re-held review.

    Which sealed subscope to recheck is the caller's selection, and it is made the
    way a person would make it: by the member the subscope holds, never by its
    verdict or resolution kind. What became of that member, and what could be
    established about the old recheck condition, are the Framework's answers.
    """

    def produce() -> AssessmentRecord:
        fx, facts, composed, request = _inputs()
        prior = _first_record()
        activity_ref = f"{fx.PACK_ID}::builders-work-openings"
        member = (fx.HVAC_CHIMNEY, fx.ARCHITECTURE_ROOF)
        ordinals = [
            subscope.ordinal
            for activity in prior.activities
            if activity.activity_ref == activity_ref
            for subscope in activity.subscopes
            if any(tuple(item.keys) == member for item in subscope.members)
        ]
        if len(ordinals) != 1:
            raise LookupError(
                f"expected one sealed {activity_ref} subscope holding {member}, "
                f"found ordinals {ordinals}"
            )
        return recheck_purpose(
            prior=prior,
            request=request,
            composed=composed,
            facts=facts,
            determinations=fx.fixture_superseding_determinations(facts=facts),
            succeeds=((activity_ref, ordinals[0]),),
        )

    return build_envelope(FIXTURE, produce)


# ---------------------------------------------------------------------------
# The recheck scenarios
# ---------------------------------------------------------------------------


@functools.cache
def _facts_under_edited_rules(edit: str):
    """The shipped models validated against a scratch copy of the rules, edited.

    A real run of the real pipeline; the only thing a fixture supplied is the
    edit. Marked as a re-validation nobody published before anything reads it.
    """

    fx = _fixtures()
    import rule_edits

    bundle = scratch_bundle(lambda rules: rule_edits.apply_edit(rules, edit))
    return fx.fixture_revalidated_facts(
        facts_from_bundle(bundle, PROJECT_ID), label=f"rules-edited-{edit}"
    )


def _reissued(label: str, *model_keys: str, **changes):
    """The shipped facts re-validated after ``model_keys`` were reissued."""

    fx, facts, _composed, _request = _inputs()
    return fx.fixture_revalidated_facts(
        facts, label=label, reissued_model_keys=model_keys, **changes
    )


def _same_review(facts):
    """The first record's determinations, which name the model versions it named."""

    return _fixtures().fixture_determinations(facts=facts)


def _no_review(_facts):
    """Nothing is offered: no review has been re-held against a reissued model."""

    return ()


def _unchanged(record: AssessmentRecord) -> AssessmentRecord:
    return record


def _without_basis(record: AssessmentRecord) -> AssessmentRecord:
    return _fixtures().fixture_record_without_comparison_basis(record)


#: ``name -> (the prior record to succeed, the facts to recheck against, the
#: determinations offered with them)``. Three callables per scenario, and nothing
#: else varies: the request is the declared one for those facts, the composition
#: is the fixture's, and every sealed subscope is answered for.
RECHECK_SCENARIOS = {
    # Model versions unchanged. An unrelated rule (R-002) was edited, so the run
    # identity and every finding key moved while nothing this record cites did.
    "recheck-key-change-only": (
        _unchanged,
        lambda: _facts_under_edited_rules("r002-datatype"),
        _same_review,
    ),
    # Model versions unchanged. R-005A's data type was edited: the predicate
    # moved and every finding reads exactly what it read.
    "recheck-semantics-changed": (
        _unchanged,
        lambda: _facts_under_edited_rules("r005a-datatype"),
        _same_review,
    ),
    # Model versions unchanged. R-005A was relaxed from required to optional:
    # the predicate moved and so did what its findings say.
    "recheck-requirement-relaxed": (
        _unchanged,
        lambda: _facts_under_edited_rules("r005a-optional"),
        _same_review,
    ),
    # Model versions unchanged, and so is the run. The prior record is in the
    # shape of one sealed before contract 1.7: finding keys and no basis.
    "recheck-prior-without-basis": (
        _without_basis,
        lambda: _inputs()[1],
        _same_review,
    ),
    # Only the producing model reissued; every finding reads what it read.
    "recheck-producing-reissued": (
        _unchanged,
        lambda: _reissued("producing-reissued", "hvac"),
        _no_review,
    ),
    # Only the producing model reissued, and the R-005 failures now pass.
    "recheck-producing-reissued-content-changed": (
        _unchanged,
        lambda: _reissued(
            "producing-reissued-content-changed", "hvac", asset_identity_fixed=True
        ),
        _no_review,
    ),
    # Only the consuming model reissued.
    "recheck-consuming-reissued": (
        _unchanged,
        lambda: _reissued("consuming-reissued", "architecture"),
        _no_review,
    ),
    # Both reissued at once.
    "recheck-both-reissued": (
        _unchanged,
        lambda: _reissued("both-reissued", "hvac", "architecture"),
        _no_review,
    ),
    # The producing model reissued with the duct deleted from it.
    "recheck-member-gone": (
        _unchanged,
        lambda: _reissued(
            "producing-reissued-duct-deleted", "hvac", delete=_fixtures().HVAC_DUCT
        ),
        _no_review,
    ),
}


def recheck_scenario_envelope(name: str) -> dict[str, object]:
    """The successor record for one entry of :data:`RECHECK_SCENARIOS`."""

    prior_of, facts_of, determinations_of = RECHECK_SCENARIOS[name]

    def produce() -> AssessmentRecord:
        _fx, _facts, composed, _request = _inputs()
        prior = prior_of(_first_record())
        facts = facts_of()
        return recheck_purpose(
            prior=prior,
            request=declared_request(facts),
            composed=composed,
            facts=facts,
            determinations=determinations_of(facts),
            succeeds=tuple(
                (activity.activity_ref, subscope.ordinal)
                for activity in prior.activities
                for subscope in activity.subscopes
            ),
        )

    return build_envelope(FIXTURE, produce)
