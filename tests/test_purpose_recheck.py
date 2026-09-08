"""Succeeding a sealed record: what carries, what vanished, and what was shown.

One claim is under test. **A recheck lets a production owner trace whether a
recorded blockage has cleared, with every conclusion evidence-backed and the
sealed record untouched.** Everything below exists to stop one of the four ways
that claim could be true in name and false in substance:

* a verdict that moved to ``READY`` reported as the recheck condition having been
  met, when the two are different sentences and this Pack carries a live case
  where they diverge;
* a universally quantified condition reported as met on a set that lost the very
  member that falsified it;
* a member, or a pair, that disappeared reported as resolved;
* the evaluator reading a Pack author's prose and deciding for itself that a
  condition holds.

Two chains are driven end to end. **Across a re-issue**: the first record's
blockers are acted on, the HVAC model is reissued and re-validated, and every
determination made against the earlier versions stops being admissible — so
``builders-work-openings`` retreats wholesale to ``penetration-not-determined``
and the ceiling activity's alignment retreats to ``not-yet-confirmed``. That is
the correct answer, and what this module insists on is that the record *says why*
rather than showing a bare ``UNKNOWN``. **Within one context**: a coordination
review is re-held and reports the chimney penetrating nothing, which sends it to
``READY`` down the ``no-penetration`` branch whose ``renders_inapplicable`` ends
the path — the openings activity is ``READY`` while no opening was modelled and no
cross-reference was added, and the record has to be able to say both.
"""

from __future__ import annotations

import ast
import copy
import dataclasses
import unittest

import assessment_fixtures as fx
from epc_control_tower.purpose import (
    AssessedScope,
    PurposeAssessmentError,
    assess_purpose,
    load_purpose_pack,
    machine_checkable_outcome,
    recheck_purpose,
)
from helpers import PROJECT_ROOT

ASSESSMENT_PACKAGE = PROJECT_ROOT / "epc_control_tower" / "purpose" / "assessment"

ALL_ACTIVITIES = (
    "schedules-and-room-data-sheets",
    "ceiling-and-bulkhead-geometry",
    "builders-work-openings",
)
OPENINGS = "interdisciplinary-coordination-readiness::builders-work-openings"
CEILING = "interdisciplinary-coordination-readiness::ceiling-and-bulkhead-geometry"
SCHEDULES = "interdisciplinary-coordination-readiness::schedules-and-room-data-sheets"

#: The sealed subscopes the chains below succeed. Read off the first record in
#: :meth:`_ChainCase.setUpClass` rather than restated, because an ordinal is a
#: within-record handle and hard-coding one would be asserting that a partition
#: is stable across records — the exact thing ADR 0003 §3.3 says it is not.
ROOF_PAIR_BLOCKER = "missing-corresponding-opening"


def _subscopes(record, activity_ref):
    for activity in record.activities:
        if activity.activity_ref == activity_ref:
            return activity
    raise AssertionError(f"no such activity in the record: {activity_ref}")


def _ordinal_of(record, activity_ref, resolution_kind, member_keys=None):
    """The ordinal of the one subscope with this kind, and optionally this member."""

    found = [
        subscope
        for subscope in _subscopes(record, activity_ref).subscopes
        if subscope.resolution_kind == resolution_kind
        and (
            member_keys is None
            or any(tuple(item.keys) == member_keys for item in subscope.members)
        )
    ]
    if len(found) != 1:
        raise AssertionError(
            f"expected one {resolution_kind!r} subscope in {activity_ref}, "
            f"found {[item.ordinal for item in found]}"
        )
    return found[0].ordinal


def _outcome_for(record, activity_ref, ordinal):
    for outcome in record.successor.outcomes:
        if outcome.activity_ref == activity_ref and outcome.subscope_ordinal == ordinal:
            return outcome
    raise AssertionError(f"the record answers for no {activity_ref} #{ordinal}")


class _ChainCase(unittest.TestCase):
    """One sealed first record, shared by every chain below.

    The first record is the repository's real facts read through the fixture's
    declared policy: three R-005 ``FAIL`` elements ``BLOCKED``, a zero-finding
    chimney ``UNKNOWN``, and the chimney refined into a slab pair that is
    ``READY`` and a roof pair that is ``BLOCKED`` on a missing opening. It is
    never mutated by anything in this file.
    """

    @classmethod
    def setUpClass(cls):
        cls.composed = fx.fixture_composed()
        cls.facts = fx.assessment_facts()
        cls.request = fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=cls.facts)
        cls.prior = assess_purpose(
            request=cls.request,
            composed=cls.composed,
            facts=cls.facts,
            determinations=fx.fixture_determinations(facts=cls.facts),
        )
        cls.roof_ordinal = _ordinal_of(
            cls.prior,
            OPENINGS,
            ROOF_PAIR_BLOCKER,
            member_keys=(fx.HVAC_CHIMNEY, fx.ARCHITECTURE_ROOF),
        )
        cls.asset_ordinal = _ordinal_of(
            cls.prior, SCHEDULES, "missing-project-asset-identity"
        )
        cls.chimney_gap_ordinal = _ordinal_of(
            cls.prior, SCHEDULES, "asset-identity-not-evaluated"
        )


class AcrossAModelReissueTests(_ChainCase):
    """A recheck may cross a re-issue, and the retreat has to be explained.

    ADR 0003 §2.3's "the context is still current" sentence was written for an
    ``authorisation`` successor and a continued ``CONDITIONAL``, both of which
    claim that nothing changed. A ``recheck`` claims the opposite: it exists to
    read the evidence again, and three of this Pack's own recheck conditions say
    "on the reissued model" in so many words. So a changed context is a
    **recorded, consequential fact** here rather than a bar to running at all.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reissued_facts = fx.fixture_reissued_facts()
        cls.record = recheck_purpose(
            prior=cls.prior,
            request=fx.fixture_reissued_request(
                activity_ids=ALL_ACTIVITIES, facts=cls.reissued_facts
            ),
            composed=cls.composed,
            facts=cls.reissued_facts,
            determinations=(),
            succeeds=(
                (OPENINGS, cls.roof_ordinal),
                (CEILING, _ordinal_of(cls.prior, CEILING, "")),
                (SCHEDULES, cls.asset_ordinal),
            ),
        )

    def test_the_context_comparison_names_the_one_model_that_moved(self):
        """A value comparison of content identifiers, and never a clock read."""

        context = self.record.successor.context
        self.assertFalse(context.is_current)
        self.assertEqual(context.changed_models, ("hvac",))
        self.assertEqual(context.prior_consuming, context.consuming)
        self.assertEqual(context.producing[1], fx.REISSUED_HVAC_CONTENT_ID)

    def test_the_openings_activity_retreats_whole_to_penetration_not_determined(self):
        """Every admitted subject, one subscope, one UNKNOWN — not a rolled-up one.

        The two pairs the first record derived are gone because the determination
        that named them is not attributable here, and the four admitted elements
        all read ``not-yet-determined`` for the same reason. They land in one
        subscope because they *agree*, which is the partition rule working, not a
        roll-up.
        """

        subscopes = _subscopes(self.record, OPENINGS).subscopes
        self.assertEqual(len(subscopes), 1)
        self.assertEqual(subscopes[0].verdict, "UNKNOWN")
        self.assertEqual(subscopes[0].resolution_kind, "penetration-not-determined")
        self.assertEqual(
            [tuple(item.keys) for item in subscopes[0].members],
            [
                (fx.HVAC_AIR_TERMINAL_COVER,),
                (fx.HVAC_AIR_TERMINAL_CAP,),
                (fx.HVAC_DUCT,),
                (fx.HVAC_CHIMNEY,),
            ],
        )

    def test_the_ceiling_alignment_retreats_to_not_yet_confirmed(self):
        """R-010 still passes and is still not alignment evidence."""

        kinds = {
            subscope.resolution_kind
            for subscope in _subscopes(self.record, CEILING).subscopes
        }
        self.assertIn("cross-model-alignment-not-confirmed", kinds)

    def test_the_record_says_the_retreat_is_a_version_attribution_failure(self):
        """Not a bare UNKNOWN: the reason each prior citation stopped carrying.

        This is the whole difference between a recheck that is useful and one
        that is not. "The openings activity is UNKNOWN again" tells a production
        owner nothing about what to do; "the determinations this record would have
        needed were made against a model version that no longer exists" tells them
        to re-hold the coordination review.
        """

        outcome = _outcome_for(self.record, OPENINGS, self.roof_ordinal)
        self.assertEqual(
            [(item.citation, item.reason) for item in outcome.carry_over],
            [
                (
                    "fixture-determination/opening/chimney-roof-not-modelled",
                    "determination-not-attributable-to-this-context",
                ),
                (
                    "fixture-determination/penetration/chimney-slab-and-roof",
                    "determination-not-attributable-to-this-context",
                ),
            ],
        )
        self.assertFalse(any(item.carried for item in outcome.carry_over))

    def test_that_reason_is_the_standing_rule_read_across_the_seal(self):
        """Offering the prior determinations here is refused, by the same rule.

        The carry-over row is not a second, softer version of
        ``determination-model-version-mismatch``. It is the *consequence* of it,
        recorded about a sealed record; the rule itself is unchanged and still
        refuses a request that tries to consume evidence attributed elsewhere.
        """

        with self.assertRaises(PurposeAssessmentError) as caught:
            recheck_purpose(
                prior=self.prior,
                request=fx.fixture_reissued_request(
                    activity_ids=ALL_ACTIVITIES, facts=self.reissued_facts
                ),
                composed=self.composed,
                facts=self.reissued_facts,
                determinations=fx.fixture_determinations(facts=self.facts),
                succeeds=((OPENINGS, self.roof_ordinal),),
            )
        self.assertEqual(caught.exception.code, "determination-model-version-mismatch")

    def test_the_roof_pair_is_classified_gone_and_never_resolved(self):
        outcome = _outcome_for(self.record, OPENINGS, self.roof_ordinal)
        self.assertEqual(outcome.correspondence, "incomplete")
        self.assertEqual(
            [item.disposition for item in outcome.dispositions],
            ["pairing-no-longer-derived"],
        )
        self.assertEqual(outcome.condition_status, "not-comparable")
        self.assertIn(
            "a member that disappeared is not a member that was fixed",
            outcome.condition_basis,
        )

    def test_a_repaired_blocker_moves_the_verdict_without_claiming_the_condition(self):
        """READY on every member, and the condition still not shown to be met.

        The asset-identity blocker really did clear: the three R-005 elements now
        read ``satisfied`` and reach ``READY``. But its ``recheck_condition`` —
        "every requirement_key ... evaluates PASS for every element in the
        assessed scope, with no element left uncovered, on the reissued model" —
        names none of ``asset-identity``'s declared outcomes, so there is nothing
        here entitled to say it was met. The record reports the movement and
        declines the sentence, which are two statements and not one.
        """

        outcome = _outcome_for(self.record, SCHEDULES, self.asset_ordinal)
        self.assertEqual(outcome.prior_verdict, "BLOCKED")
        self.assertEqual(outcome.correspondence, "complete")
        self.assertEqual(
            sorted({item.current_verdicts for item in outcome.dispositions}),
            [("READY",)],
        )
        self.assertEqual(outcome.condition_status, "no-machine-checkable-part")
        self.assertEqual(outcome.named_outcome, "")
        self.assertIn("adjudicates no prose", outcome.condition_basis)

    def test_the_repaired_findings_are_new_keys_and_the_old_ones_do_not_carry(self):
        """A re-validated model produces new finding keys; the sealed ones are gone."""

        outcome = _outcome_for(self.record, SCHEDULES, self.asset_ordinal)
        self.assertTrue(outcome.carry_over)
        self.assertEqual(
            {item.reason for item in outcome.carry_over},
            {"finding-absent-from-the-cited-run"},
        )
        self.assertEqual(
            {item.citation_kind for item in outcome.carry_over}, {"finding"}
        )

    def test_a_ready_subscope_is_answered_for_without_inventing_a_condition(self):
        """READY carries no route, so there is no condition — said, not implied."""

        outcome = _outcome_for(
            self.record, CEILING, _ordinal_of(self.prior, CEILING, "")
        )
        self.assertEqual(outcome.prior_verdict, "READY")
        self.assertEqual(outcome.prior_recheck_condition, "")
        self.assertEqual(outcome.condition_status, "no-recheck-condition")
        self.assertEqual(
            sorted({item.current_verdicts for item in outcome.dispositions}),
            [("UNKNOWN",)],
        )


class TheConditionIsNotTheVerdictTests(_ChainCase):
    """The live counterexample: ``READY`` while the work was never done.

    ``(chimney, roof)`` is ``BLOCKED`` / ``missing-corresponding-opening``, and
    that route's ``recheck_condition`` names ``outcome = cross-referenced``. A
    later coordination review reports the chimney penetrating nothing. The
    chimney takes ``no-penetration`` to ``READY``, whose ``renders_inapplicable``
    ends the path before ``opening-status`` is asked — so the openings activity is
    ``READY`` for the chimney, and **no opening was modelled and no
    cross-reference was added**.

    Nothing about the models changed, so this is not a re-issue: a review can be
    re-held and correct itself, and each record cites the review it read.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = recheck_purpose(
            prior=cls.prior,
            request=cls.request,
            composed=cls.composed,
            facts=cls.facts,
            determinations=fx.fixture_superseding_determinations(facts=cls.facts),
            succeeds=((OPENINGS, cls.roof_ordinal),),
        )
        cls.outcome = _outcome_for(cls.record, OPENINGS, cls.roof_ordinal)

    def test_the_chimney_now_reaches_ready_through_no_penetration(self):
        ready = [
            subscope
            for subscope in _subscopes(self.record, OPENINGS).subscopes
            if subscope.verdict == "READY"
        ]
        self.assertEqual(len(ready), 1)
        self.assertIn((fx.HVAC_CHIMNEY,), [tuple(item.keys) for item in ready[0].members])
        self.assertEqual(ready[0].path[-1].outcome, "no-penetration")

    def test_no_subscope_of_the_activity_is_blocked_any_more(self):
        self.assertEqual(
            {
                subscope.verdict
                for subscope in _subscopes(self.record, OPENINGS).subscopes
            },
            {"READY", "UNKNOWN"},
        )

    def test_and_the_record_does_not_say_the_recheck_condition_was_met(self):
        """The two sentences, side by side, saying different things.

        This is the assertion the whole shape exists for. A design that recorded
        only "the activity is READY now" would report a chimney with an
        unmodelled roof opening as work completed.
        """

        self.assertEqual(self.outcome.prior_resolution_kind, ROOF_PAIR_BLOCKER)
        self.assertIn("outcome = cross-referenced", self.outcome.prior_recheck_condition)
        self.assertEqual(self.outcome.condition_status, "not-comparable")
        self.assertEqual(
            [item.disposition for item in self.outcome.dispositions],
            ["pairing-no-longer-derived"],
        )

    def test_the_cause_quotes_this_records_own_reading(self):
        """Evidence, not a story about a document the record cannot see."""

        cause = self.outcome.dispositions[0].cause
        self.assertIn("penetration-determination now reads 'no-penetration'", cause)
        self.assertIn("Counterparts derived now: []", cause)

    def test_the_superseded_determinations_are_not_blamed_on_the_context(self):
        """The context did not move, so the citations lapsed for the other reason."""

        self.assertTrue(self.record.successor.context.is_current)
        self.assertEqual(
            {item.reason for item in self.outcome.carry_over},
            {"determination-not-cited-by-this-record"},
        )

    def test_the_first_record_still_says_the_roof_opening_was_missing(self):
        """Half the value of a recheck is that what we knew then stays readable."""

        subscope = [
            item
            for item in _subscopes(self.prior, OPENINGS).subscopes
            if item.ordinal == self.roof_ordinal
        ][0]
        self.assertEqual(subscope.verdict, "BLOCKED")
        self.assertEqual(subscope.resolution_kind, ROOF_PAIR_BLOCKER)
        self.assertEqual(subscope.path[-1].outcome, "not-modelled")
        self.assertEqual(
            [tuple(item.keys) for item in subscope.members],
            [(fx.HVAC_CHIMNEY, fx.ARCHITECTURE_ROOF)],
        )


class TheConditionsMachineCheckablePartTests(_ChainCase):
    """Three of ten conditions name one outcome; the other seven are for people."""

    def test_exactly_three_of_the_shipped_packs_conditions_are_comparable(self):
        """A membership test over a closed vocabulary, and a census of the result.

        ``alignment-confirmation`` is one token and never matches ``confirmed``;
        ``opening-cross-reference-check`` never matches ``cross-referenced``; and
        ``opening-status-not-determined``'s three-outcome disjunction resolves to
        nothing at all, because picking one of three would be the evaluator
        deciding which half of a sentence it meant.
        """

        pack = load_purpose_pack(fx.PACK_PATH)
        leaf_requirement = {}
        for node in pack.decision_nodes:
            for branch in node.branches:
                if branch.resolution_kind:
                    leaf_requirement[branch.resolution_kind] = (
                        pack.evidence_requirement(node.evidence_requirement_id)
                    )
        named = {
            route.resolution_kind: machine_checkable_outcome(
                route.recheck_condition, leaf_requirement[route.resolution_kind]
            )
            for route in pack.resolution_routes
        }
        self.assertEqual(len(named), 10)
        self.assertEqual(
            {kind: value for kind, value in named.items() if value},
            {
                "missing-corresponding-opening": "cross-referenced",
                "opening-not-verifiably-linked": "cross-referenced",
                "cross-model-misalignment": "confirmed",
            },
        )

    def test_three_conditions_speak_of_a_reissued_model_in_so_many_words(self):
        """The Pack itself expects a recheck to cross a re-issue.

        This is the textual evidence behind the §2.3 narrowing: a design in which
        a successor may never cross a re-issue would make three of this Pack's own
        ten recheck conditions unreachable.
        """

        pack = load_purpose_pack(fx.PACK_PATH)
        reissue = sorted(
            route.resolution_kind
            for route in pack.resolution_routes
            if "reissued model" in route.recheck_condition
        )
        self.assertEqual(
            reissue,
            [
                "cross-model-misalignment",
                "mep-element-not-spatially-assigned",
                "missing-project-asset-identity",
            ],
        )

    def test_the_named_outcome_observed_is_reached_when_the_opening_is_cut(self):
        """The positive path: the architect cuts the opening and cross-references it.

        The consuming model is reissued, a fresh review is held against the new
        pair of versions, and the roof pair reads ``cross-referenced`` — which is
        the outcome the sealed condition names. The status says exactly that, and
        by its name claims nothing about the rest of the sentence.
        """

        facts = fx.fixture_reissued_facts(
            reissued_model_key="architecture", asset_identity_fixed=False
        )
        record = recheck_purpose(
            prior=self.prior,
            request=fx.fixture_reissued_request(
                activity_ids=ALL_ACTIVITIES, facts=facts
            ),
            composed=self.composed,
            facts=facts,
            determinations=fx.fixture_determinations(
                facts=facts, roof_opening="cross-referenced"
            ),
            succeeds=((OPENINGS, self.roof_ordinal),),
        )
        outcome = _outcome_for(record, OPENINGS, self.roof_ordinal)
        self.assertEqual(outcome.correspondence, "complete")
        self.assertEqual(outcome.named_outcome, "cross-referenced")
        self.assertEqual(outcome.condition_status, "named-outcome-observed")
        self.assertEqual(
            [item.current_verdicts for item in outcome.dispositions], [("READY",)]
        )
        self.assertIn("the rest of the sentence was not read", outcome.condition_basis)

    def test_a_different_deficiency_is_not_the_named_outcome(self):
        """The opening is cut but never cross-referenced: moved, and not met.

        The verdict is still ``BLOCKED`` and the ``resolution_kind`` is now
        ``opening-not-verifiably-linked`` — a different fix, a different role. The
        condition status says the named outcome was not observed rather than
        anything about the new blocker, because a recheck answers for the sealed
        subscope's own sentence.
        """

        facts = fx.fixture_reissued_facts(
            reissued_model_key="architecture", asset_identity_fixed=False
        )
        record = recheck_purpose(
            prior=self.prior,
            request=fx.fixture_reissued_request(
                activity_ids=ALL_ACTIVITIES, facts=facts
            ),
            composed=self.composed,
            facts=facts,
            determinations=fx.fixture_determinations(
                facts=facts, roof_opening="modelled-not-cross-referenced"
            ),
            succeeds=((OPENINGS, self.roof_ordinal),),
        )
        outcome = _outcome_for(record, OPENINGS, self.roof_ordinal)
        self.assertEqual(outcome.condition_status, "named-outcome-not-observed")
        self.assertEqual(
            [item.current_verdicts for item in outcome.dispositions], [("BLOCKED",)]
        )
        self.assertIn("modelled-not-cross-referenced", outcome.condition_basis)

    def test_the_evaluator_reads_no_prose_and_owns_no_condition_vocabulary(self):
        """No sentiment analysis, no keyword list, no per-Pack special case.

        The only thing the module compares a condition against is the evidence
        requirement's own ``outcomes[]``. If it held a vocabulary of its own,
        a Pack author's sentence could mean something the Pack never declared.
        """

        source = (ASSESSMENT_PACKAGE / "recheck.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        # The module docstring names this Pack's kinds as worked examples, which
        # is exactly where a worked example belongs; what must not exist is a
        # Pack's vocabulary in the *code*, so the constants are collected from the
        # syntax tree with the docstrings dropped.
        literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        } - {
            node.value.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        }
        pack = load_purpose_pack(fx.PACK_PATH)
        vocabulary = {
            outcome
            for requirement in pack.evidence_requirements
            for outcome in requirement.outcomes
        } | {route.resolution_kind for route in pack.resolution_routes}
        self.assertEqual(literals & vocabulary, set())
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "machine_checkable_outcome"
        )
        calls = {
            node.func.attr
            for node in ast.walk(function)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertEqual(calls, {"findall"})


class WhatBecameOfEveryMemberTests(_ChainCase):
    """Four ways a subject leaves, and none of them is "resolved"."""

    def _recheck(self, *, facts=None, scope=None, succeeds=None):
        facts = facts if facts is not None else self.facts
        return recheck_purpose(
            prior=self.prior,
            request=fx.fixture_request(
                activity_ids=ALL_ACTIVITIES, facts=facts, scope=scope
            ),
            composed=self.composed,
            facts=facts,
            determinations=(),
            succeeds=succeeds or ((SCHEDULES, self.chimney_gap_ordinal),),
        )

    def test_a_deleted_element(self):
        facts = fx.fixture_reissued_facts(delete_chimney=True)
        outcome = _outcome_for(
            self._recheck(facts=facts), SCHEDULES, self.chimney_gap_ordinal
        )
        self.assertEqual(
            [item.disposition for item in outcome.dispositions],
            ["element-deleted-in-reissued-model"],
        )
        self.assertIn("absent from the element inventory", outcome.dispositions[0].cause)

    def test_an_element_whose_class_moved_out_of_the_activitys_subject_classes(self):
        """An export-mapping change, not a model repair.

        The chimney is still in the model and still in the declared scope. What
        moved is what the exporter called it, and the activity is now not about
        it — which is a different fact from the blocker having cleared, and has to
        be recorded as one.
        """

        facts = fx.fixture_reissued_facts(chimney_ifc_class="IfcBuildingElementProxy")
        outcome = _outcome_for(
            self._recheck(facts=facts), SCHEDULES, self.chimney_gap_ordinal
        )
        self.assertEqual(
            [item.disposition for item in outcome.dispositions],
            ["element-out-of-subject-class"],
        )
        self.assertIn("IfcBuildingElementProxy", outcome.dispositions[0].cause)

    def test_a_pair_the_current_determination_no_longer_names(self):
        """The cross-record case the within-record guard structurally cannot see.

        ``DeterminationLedger.counterparts`` already stops a declined claim that
        sorts first from silently deciding which pairs exist *inside* one record.
        It never looks at an earlier record, so a pair that existed there and does
        not exist here would simply be absent — not reported wrongly, not reported
        at all. This is the branch that reports it.
        """

        record = recheck_purpose(
            prior=self.prior,
            request=self.request,
            composed=self.composed,
            facts=self.facts,
            determinations=fx.fixture_superseding_determinations(facts=self.facts),
            succeeds=((OPENINGS, self.roof_ordinal),),
        )
        outcome = _outcome_for(record, OPENINGS, self.roof_ordinal)
        self.assertEqual(
            [item.disposition for item in outcome.dispositions],
            ["pairing-no-longer-derived"],
        )

    def test_a_pair_lost_while_the_element_stays_paired_with_somebody_else(self):
        """The same case in the shape where the element gives no hint at all.

        The re-held review keeps the slab penetration and drops the roof one. The
        chimney is still penetrating, still refines, still reaches a pair verdict
        — so a comparison that asked "is the penetrating element still a subject?"
        would answer yes and lose the roof pair without a word. The disposition
        catches it, and the cause quotes both what the pair source now reads and
        which counterparts survived.
        """

        record = recheck_purpose(
            prior=self.prior,
            request=self.request,
            composed=self.composed,
            facts=self.facts,
            determinations=fx.fixture_narrowed_penetration_determinations(
                facts=self.facts
            ),
            succeeds=((OPENINGS, self.roof_ordinal),),
        )
        outcome = _outcome_for(record, OPENINGS, self.roof_ordinal)
        self.assertEqual(
            [item.disposition for item in outcome.dispositions],
            ["pairing-no-longer-derived"],
        )
        cause = outcome.dispositions[0].cause
        self.assertIn(
            "penetration-determination now reads 'penetration-confirmed'", cause
        )
        self.assertIn(f"Counterparts derived now: ['{fx.ARCHITECTURE_SLAB}']", cause)
        self.assertEqual(outcome.condition_status, "not-comparable")
        # And the slab pair, which nothing happened to, is still READY.
        self.assertIn(
            (fx.HVAC_CHIMNEY, fx.ARCHITECTURE_SLAB),
            [
                tuple(member.keys)
                for subscope in _subscopes(record, OPENINGS).subscopes
                if subscope.verdict == "READY"
                for member in subscope.members
            ],
        )

    def test_a_key_this_requests_own_scope_no_longer_declares(self):
        """The scope shrank. Nothing about the deficiency did."""

        scope = AssessedScope(
            element_keys=(
                fx.HVAC_DUCT,
                fx.HVAC_AIR_TERMINAL_COVER,
                fx.HVAC_AIR_TERMINAL_CAP,
            )
        )
        outcome = _outcome_for(
            self._recheck(scope=scope), SCHEDULES, self.chimney_gap_ordinal
        )
        self.assertEqual(
            [item.disposition for item in outcome.dispositions],
            ["outside-declared-scope"],
        )
        self.assertIn("declared assessed scope", outcome.dispositions[0].cause)

    def test_none_of_the_four_is_ever_reported_as_resolved(self):
        """A census over the vocabulary itself, not over one worked case."""

        from epc_control_tower.purpose.assessment import MEMBER_DISPOSITIONS

        self.assertEqual(len(MEMBER_DISPOSITIONS), 5)
        self.assertEqual(
            [name for name in MEMBER_DISPOSITIONS if name != "present"],
            [
                "element-deleted-in-reissued-model",
                "element-out-of-subject-class",
                "pairing-no-longer-derived",
                "outside-declared-scope",
            ],
        )
        for name in MEMBER_DISPOSITIONS:
            with self.subTest(name=name):
                self.assertNotIn("resolv", name)
                self.assertNotIn("clear", name)
                self.assertNotIn("fixed", name)

    def test_a_split_subject_is_present_in_every_pair_it_refined_into(self):
        """Refinement is not disappearance, and it is the one many-to-one case.

        The first record here is one where no coordination review had been held,
        so every subject of ``builders-work-openings`` is a bare element sitting
        in one ``penetration-not-determined`` gap. The review is then held and the
        chimney becomes two pairs with two verdicts. Reporting that as "gone"
        would be as wrong as reporting it as resolved — the subject is present
        twice, and the disposition carries both landings.
        """

        undetermined = assess_purpose(
            request=self.request,
            composed=self.composed,
            facts=self.facts,
            determinations=fx.fixture_determinations(
                facts=self.facts, penetration=False
            ),
        )
        ordinal = _ordinal_of(undetermined, OPENINGS, "penetration-not-determined")
        record = recheck_purpose(
            prior=undetermined,
            request=self.request,
            composed=self.composed,
            facts=self.facts,
            determinations=fx.fixture_determinations(facts=self.facts),
            succeeds=((OPENINGS, ordinal),),
        )
        outcome = _outcome_for(record, OPENINGS, ordinal)
        self.assertEqual(
            {item.disposition for item in outcome.dispositions}, {"present"}
        )
        chimney = [
            item
            for item in outcome.dispositions
            if tuple(item.member.keys) == (fx.HVAC_CHIMNEY,)
        ]
        self.assertEqual(len(chimney), 1)
        self.assertEqual(len(chimney[0].current_ordinals), 2)
        self.assertEqual(sorted(chimney[0].current_verdicts), ["BLOCKED", "READY"])


class AShrunkenSetIsNotASatisfiedConditionTests(_ChainCase):
    """A universally quantified condition, and the set that lost its counterexample.

    ``asset-identity-not-evaluated`` reads "Every element in the assessed scope
    is covered by an evaluation under the bound requirement_key(s) — no element
    is left with no finding at all." The only element it is false of is the
    zero-finding chimney. Delete the chimney and the sentence is **literally
    true** over what remains, which is the trap: comparability has to be
    established before the condition is looked at, or a deletion reads as a fix.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.facts_without_chimney = fx.fixture_reissued_facts(delete_chimney=True)
        cls.record = recheck_purpose(
            prior=cls.prior,
            request=fx.fixture_reissued_request(
                activity_ids=ALL_ACTIVITIES, facts=cls.facts_without_chimney
            ),
            composed=cls.composed,
            facts=cls.facts_without_chimney,
            determinations=(),
            succeeds=((SCHEDULES, cls.chimney_gap_ordinal),),
        )
        cls.outcome = _outcome_for(cls.record, SCHEDULES, cls.chimney_gap_ordinal)

    def test_the_sentence_really_would_go_true_over_what_is_left(self):
        """The trap is real, and this asserts it rather than assuming it.

        Every element the activity still admits carries at least one finding under
        the bound keys, so "no element is left with no finding at all" holds of
        the surviving set. A design that evaluated the condition first would
        report the blocker cleared.
        """

        bound = fx.asset_identity_requirement_keys()
        admitted = _subscopes(self.record, SCHEDULES).admitted_subjects
        self.assertNotIn(fx.HVAC_CHIMNEY, admitted)
        self.assertTrue(admitted)
        for element_key in admitted:
            with self.subTest(element_key=element_key):
                self.assertTrue(
                    self.facts_without_chimney.findings_for(element_key, bound)
                )

    def test_and_the_record_reports_not_comparable_instead(self):
        self.assertEqual(self.outcome.condition_status, "not-comparable")
        self.assertEqual(self.outcome.correspondence, "incomplete")
        self.assertIn(
            "no longer subjects of this record's partition",
            self.outcome.condition_basis,
        )

    def test_comparability_is_established_before_the_condition_is_read(self):
        """With the same element present, the same condition reaches a different state.

        Not ``named-outcome-observed`` either — that condition names none of
        ``asset-identity``'s outcomes. The point is that the two runs differ *only*
        in whether the member survived, and the status changes, which is what makes
        the ordering observable rather than asserted.
        """

        present = fx.fixture_reissued_facts(delete_chimney=False)
        record = recheck_purpose(
            prior=self.prior,
            request=fx.fixture_reissued_request(
                activity_ids=ALL_ACTIVITIES, facts=present
            ),
            composed=self.composed,
            facts=present,
            determinations=(),
            succeeds=((SCHEDULES, self.chimney_gap_ordinal),),
        )
        outcome = _outcome_for(record, SCHEDULES, self.chimney_gap_ordinal)
        self.assertEqual(outcome.correspondence, "complete")
        self.assertEqual(outcome.condition_status, "no-machine-checkable-part")

    def test_the_other_coverage_condition_behaves_the_same_way(self):
        """``in-model-position-not-evaluated`` is the same sentence about R-004."""

        ordinal = _ordinal_of(self.prior, CEILING, "in-model-position-not-evaluated")
        record = recheck_purpose(
            prior=self.prior,
            request=fx.fixture_reissued_request(
                activity_ids=ALL_ACTIVITIES, facts=self.facts_without_chimney
            ),
            composed=self.composed,
            facts=self.facts_without_chimney,
            determinations=(),
            succeeds=((CEILING, ordinal),),
        )
        outcome = _outcome_for(record, CEILING, ordinal)
        self.assertEqual(outcome.condition_status, "not-comparable")


class SealingAndDeterminismTests(_ChainCase):
    """The prior record is untouched, and two rechecks are the same record."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.facts_after = fx.fixture_reissued_facts()
        cls.arguments = dict(
            prior=cls.prior,
            request=fx.fixture_reissued_request(
                activity_ids=ALL_ACTIVITIES, facts=cls.facts_after
            ),
            composed=cls.composed,
            facts=cls.facts_after,
            determinations=(),
            succeeds=((OPENINGS, cls.roof_ordinal),),
        )

    def test_the_same_recheck_produces_a_byte_identical_record(self):
        first = recheck_purpose(**self.arguments)
        second = recheck_purpose(**self.arguments)
        self.assertEqual(first.as_document(), second.as_document())
        self.assertEqual(first.assessment_digest, second.assessment_digest)

    def test_the_prior_record_is_not_touched_by_being_succeeded(self):
        """Byte for byte the same document, and the same digest, afterwards."""

        before = copy.deepcopy(self.prior.as_document())
        digest = self.prior.assessment_digest
        recheck_purpose(**self.arguments)
        self.assertEqual(self.prior.as_document(), before)
        self.assertEqual(self.prior.assessment_digest, digest)

    def test_an_originating_record_carries_no_successor_section(self):
        """So adding successors moved no originating record's digest by a byte."""

        self.assertIsNone(self.prior.successor)
        self.assertNotIn("successor", self.prior.as_document())

    def test_the_successor_section_is_inside_the_digest(self):
        """A record that says a blockage cleared and one that says it did not
        cannot share a digest."""

        record = recheck_purpose(**self.arguments)
        stripped = dict(record.as_document())
        stripped.pop("successor")
        self.assertNotEqual(
            record.assessment_digest,
            __import__(
                "epc_control_tower.purpose.assessment.record", fromlist=["x"]
            ).build_assessment_digest(stripped),
        )

    def test_a_successor_of_a_broken_seal_is_refused(self):
        """A record edited after it was sealed no longer hashes to what it says."""

        tampered = dataclasses.replace(self.prior, validation_run_id="tampered")
        with self.assertRaises(PurposeAssessmentError) as caught:
            recheck_purpose(**{**self.arguments, "prior": tampered})
        self.assertEqual(caught.exception.code, "recheck-prior-record-seal-broken")

    def test_the_recheck_reads_no_clock_and_no_file_bytes(self):
        source = (ASSESSMENT_PACKAGE / "recheck.py").read_text(encoding="utf-8")
        for forbidden in (
            "datetime",
            "time.",
            "now(",
            "read_bytes",
            "read_text",
            "open(",
            "glob",
            "iterdir",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


class RecheckPreconditionsTests(_ChainCase):
    """Every refusal, and none of them a default."""

    def _refuse(self, **overrides):
        arguments = dict(
            prior=self.prior,
            request=self.request,
            composed=self.composed,
            facts=self.facts,
            determinations=fx.fixture_determinations(facts=self.facts),
            succeeds=((OPENINGS, self.roof_ordinal),),
        )
        arguments.update(overrides)
        with self.assertRaises(PurposeAssessmentError) as caught:
            recheck_purpose(**arguments)
        return caught.exception

    def test_a_recheck_that_names_no_sealed_subscope(self):
        self.assertEqual(self._refuse(succeeds=()).code, "recheck-cites-no-subscope")

    def test_an_ordinal_the_prior_record_does_not_carry(self):
        self.assertEqual(
            self._refuse(succeeds=((OPENINGS, 99),)).code, "recheck-subscope-unresolved"
        )

    def test_an_activity_the_prior_record_does_not_carry(self):
        self.assertEqual(
            self._refuse(succeeds=(("no-such-pack::no-such-activity", 1),)).code,
            "recheck-activity-unresolved",
        )

    def test_an_activity_this_request_does_not_ask_about(self):
        """A recheck that assesses nothing reports nothing."""

        exception = self._refuse(
            request=fx.fixture_request(
                activity_ids=("schedules-and-room-data-sheets",), facts=self.facts
            )
        )
        self.assertEqual(exception.code, "recheck-activity-not-requested")

    def test_a_different_question(self):
        request = dataclasses.replace(self.request, direction_id="other-direction")
        self.assertEqual(self._refuse(request=request).code, "recheck-not-the-same-question")

    def test_a_pack_version_that_moved_under_the_sealed_condition(self):
        """The routes, the conditions and the outcome vocabularies may all differ.

        Comparing a sealed sentence with a re-derived reading across a
        ``pack_version`` move would compare two different sentences and report one
        answer. The same reasoning already stands behind ADR 0003 §4.5's check 6
        for a continued promotion.
        """

        overlay = fx.fixture_overlay_document()
        overlay["overlay"]["packs"][0]["pack_version"] = "0.2.0"
        with fx.scratch_pack(
            lambda document: document.update(pack_version="0.2.0")
        ) as pack:
            composed = fx.fixture_composed(overlay_document=overlay, pack=pack)
            request = dataclasses.replace(self.request, pack_version="0.2.0")
            exception = self._refuse(composed=composed, request=request)
        self.assertEqual(exception.code, "recheck-pack-version-moved")


class InheritedProhibitionsTests(_ChainCase):
    """Severity, priority and magnitude are exactly as forbidden as before."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        facts = fx.fixture_reissued_facts(asset_identity_fixed=False)
        cls.record = recheck_purpose(
            prior=cls.prior,
            request=fx.fixture_reissued_request(
                activity_ids=ALL_ACTIVITIES, facts=facts
            ),
            composed=cls.composed,
            facts=facts,
            determinations=(),
            succeeds=((SCHEDULES, cls.asset_ordinal),),
        )

    def test_r005_is_still_warning_and_the_verdict_is_still_blocked(self):
        """A recheck is not a second, gentler reading of the same failure."""

        blocked = [
            subscope
            for subscope in _subscopes(self.record, SCHEDULES).subscopes
            if subscope.verdict == "BLOCKED"
        ]
        self.assertEqual(len(blocked), 1)
        self.assertEqual(blocked[0].resolution_kind, "missing-project-asset-identity")

    def test_the_recheck_names_no_validation_metadata_a_verdict_could_read(self):
        source = (ASSESSMENT_PACKAGE / "recheck.py").read_text(encoding="utf-8")
        code = "\n".join(
            line for line in source.splitlines() if not line.strip().startswith("#")
        )
        body = code.split('"""', 2)[-1]
        for forbidden in ("is_issue", "owner_role", "priority", "labels"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, body)

    def test_a_consequence_still_carries_kinds_and_no_magnitude(self):
        for activity in self.record.activities:
            for subscope in activity.subscopes:
                if subscope.route is None:
                    continue
                with self.subTest(ordinal=subscope.ordinal):
                    self.assertTrue(subscope.route.consequence_kinds)
                    self.assertEqual(
                        set(dataclasses.asdict(subscope.route)) - {"resolution_kind"},
                        {
                            "consequence_kinds",
                            "default_role",
                            "next_action",
                            "recheck_condition",
                        },
                    )

    def test_the_milestones_are_still_cited_verbatim(self):
        self.assertEqual(
            dict(self.record.cited_milestones), dict(self.prior.cited_milestones)
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
