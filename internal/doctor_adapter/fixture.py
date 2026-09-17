"""The fixture entry: the test suite's declared policy, through the same evaluator.

Fixture policy has exactly one source, ``tests/assessment_fixtures.py``, and this
module reuses its builders rather than restating any of them — the Overlay with
two of its three policy tables decided, the determinations nobody has ever made
for ``pcert-sample``, and the request declaration. Two copies would drift apart
silently. What this module adds is only the call: composing through the real
composer and assessing through the real entry point, against the validated facts
of :mod:`.validated` instead of the test helper's run, whose rule compilation
writes into this checkout's ``ids/``.

Its envelopes are always ``mode = "fixture"``.
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
    load_purpose_pack,
    read_overlay_table,
    recheck_purpose,
)

from .envelope import FIXTURE, PROJECT_ROOT, build_envelope
from .validated import requirement_keys_by_ruleset, validated_facts

__all__ = [
    "declared_request",
    "first_record_envelope",
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
