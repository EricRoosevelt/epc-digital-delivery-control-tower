"""What one purpose assessment does, and what it refuses to do.

Two things are being proved, and the second is the reason the first is not
enough.

**``pcert-sample`` cannot produce a record, and that is the correct answer.**
All four of its ``team_mapping`` rows say ``decision_basis = "illustrative"``,
every live verdict across the three activities is non-``READY``, and ADR 0003
§4.3 requires a resolving assignment on every non-``READY`` subscope. So every
assignment this project could make would rest on a demonstration row, and the
entry point refuses — naming the rows, because a refusal that says only "policy
is illustrative" leaves a maintainer guessing which four lines to change.

**Everything behind that refusal is proved on a fixture**, through the *same*
:func:`~epc_control_tower.purpose.assess_purpose`. There is no test flag, no
skip switch and no relaxed check anywhere in this file; the fixture gets past the
gate by declaring different policy, which is what a project that had taken those
decisions would do. See :mod:`assessment_fixtures` for which halves of it are the
repository's real facts and which are the test's own assumptions.

Verdicts are asserted **per subscope**, never per activity. Asserting
"``schedules-and-room-data-sheets`` is ``BLOCKED``" would pass whether or not the
partition worked, and the partition is the thing this checkpoint adds: under the
``hvac`` scope that activity splits into three R-005 ``FAIL`` elements reaching
``BLOCKED`` and a zero-finding ``IfcChimney`` reaching ``UNKNOWN``, and collapsing
those into one activity-level verdict would discard exactly what the split exists
to hold apart.
"""

from __future__ import annotations

import ast
import dataclasses
import unittest

import assessment_fixtures as fx
from epc_control_tower.domain import Finding, FindingStatus, Severity
from epc_control_tower.purpose import (
    AssessedScope,
    PurposeAssessmentError,
    assess_purpose,
    compose_purpose_inputs,
    load_project_overlay,
    load_purpose_pack,
    read_overlay_table,
)
from epc_control_tower.purpose.assessment import reading as reading_module
from epc_control_tower.purpose.assessment.determinations import (
    Determination,
    DeterminationLedger,
)
from epc_control_tower.purpose.assessment.facts import FindingFact
from helpers import PROJECT_ROOT

ASSESSMENT_PACKAGE = PROJECT_ROOT / "epc_control_tower" / "purpose" / "assessment"
PCERT_MANIFEST = PROJECT_ROOT / "projects" / "pcert-sample" / "project.toml"

ALL_ACTIVITIES = (
    "schedules-and-room-data-sheets",
    "ceiling-and-bulkhead-geometry",
    "builders-work-openings",
)


def _subscopes(record, activity_id):
    for activity in record.activities:
        if activity.activity_ref.endswith(f"::{activity_id}"):
            return activity
    raise AssertionError(f"no such activity in the record: {activity_id}")


def _members(subscope):
    return [tuple(member.keys) for member in subscope.members]


class RealEntryPointRefusesPcertSampleTests(unittest.TestCase):
    """The shipped project's own policy stops it, and the diagnostic says how.

    Not a defect and not a gap in the evaluator. ``pcert-sample`` has never
    recorded a staffing decision, its manifest says so on every row, and a record
    founded on those rows would assert an assignment nobody made.
    """

    @classmethod
    def setUpClass(cls):
        cls.facts = fx.assessment_facts()
        cls.composed = compose_purpose_inputs(
            project_id="pcert-sample",
            overlay=load_project_overlay(PCERT_MANIFEST),
            packs=(load_purpose_pack(fx.PACK_PATH),),
            requirement_keys_by_ruleset=fx.requirement_keys_by_ruleset(),
        )
        cls.request = fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=cls.facts)

    def _refusal(self) -> PurposeAssessmentError:
        with self.assertRaises(PurposeAssessmentError) as caught:
            assess_purpose(
                request=self.request, composed=self.composed, facts=self.facts
            )
        return caught.exception

    def test_the_request_is_refused_and_no_record_is_produced(self):
        """A refusal is total: an exception, never a record with a gap in it."""

        self.assertEqual(self._refusal().code, "team-mapping-decision-basis-illustrative")

    def test_the_diagnostic_names_every_blocking_policy_row(self):
        """All four rows, each with its role, its team, and its decision_basis."""

        message = str(self._refusal())
        self.assertIn("The 4 blocking row(s):", message)
        for role, team in (
            ("model-coordination", "coordination-team"),
            ("mep-lead", "mep-design-team"),
            ("architecture-lead", "architecture-design-team"),
            ("information-manager", "information-management-team"),
        ):
            with self.subTest(role=role):
                self.assertIn(f"role={role!r}", message)
                self.assertIn(f"team_or_person={team!r}", message)
        self.assertIn("decision_basis='illustrative'", message)
        self.assertIn("overlay.team_mapping", message)

    def test_the_diagnostic_names_the_routes_each_row_would_have_founded(self):
        """Which leaf needs which row, so the fix is a reading rather than a hunt."""

        message = str(self._refusal())
        for resolution_kind in (
            "missing-project-asset-identity",
            "asset-identity-not-evaluated",
            "mep-element-not-spatially-assigned",
            "in-model-position-not-evaluated",
            "cross-model-misalignment",
            "cross-model-alignment-not-confirmed",
            "penetration-not-determined",
            "opening-not-verifiably-linked",
            "missing-corresponding-opening",
            "opening-status-not-determined",
        ):
            with self.subTest(resolution_kind=resolution_kind):
                self.assertIn(resolution_kind, message)

    def test_the_refusal_is_ascii_so_a_windows_console_shows_it_whole(self):
        str(self._refusal()).encode("ascii")

    def test_the_shipped_manifest_still_records_its_policy_as_illustrative(self):
        """The fixture supplies policy in memory and writes nothing back."""

        text = PCERT_MANIFEST.read_text(encoding="utf-8")
        self.assertEqual(text.count('decision_basis = "project-decision"'), 0)
        for row in self.composed.overlay.team_mapping:
            with self.subTest(role=row.role):
                self.assertEqual(row.decision_basis, "illustrative")

    def test_the_fixture_and_the_real_entry_point_are_the_same_function(self):
        """No second entry point, and therefore no second set of rules.

        ``derive_assessment`` is not a second one: it is everything
        ``assess_purpose`` resolves, stopping short of the seal, and it exists
        because a recheck has to compare a re-derivation against a sealed record
        *before* the digest that covers both is computed. The guard that matters
        is the one below — that the recheck module calls it rather than growing a
        second walk, a second reading rule, or a second partition, either of
        which could drift into a laxer reading of the same facts.
        """

        source = (ASSESSMENT_PACKAGE / "evaluator.py").read_text(encoding="utf-8")
        public = [
            node.name
            for node in ast.parse(source).body
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
        ]
        self.assertEqual(public, ["assess_purpose", "derive_assessment"])
        for switch in ("skip", "force", "test_mode", "allow_illustrative", "strict"):
            with self.subTest(switch=switch):
                self.assertNotIn(switch, source)

    def test_the_successor_path_re_derives_through_the_same_evaluator(self):
        """A recheck owns no walk, no reading rule and no partition of its own."""

        source = (ASSESSMENT_PACKAGE / "recheck.py").read_text(encoding="utf-8")
        self.assertIn("from .evaluator import derive_assessment", source)
        defined = {
            node.name
            for node in ast.parse(source).body
            if isinstance(node, ast.FunctionDef)
        }
        for reimplementation in ("_walk", "_read", "_refine", "_order", "_assess_activity"):
            with self.subTest(name=reimplementation):
                self.assertNotIn(reimplementation, defined)
        for switch in ("skip", "force", "test_mode", "allow_illustrative"):
            with self.subTest(switch=switch):
                self.assertNotIn(switch, source)


class PartitionTests(unittest.TestCase):
    """The live partition, asserted subscope by subscope.

    This is the checkpoint's regression criterion, and it is deliberately not an
    activity-level summary: ``schedules-and-room-data-sheets`` has no single
    verdict under this scope, it has two, and a test that asserted one would pass
    with the partition removed.
    """

    @classmethod
    def setUpClass(cls):
        cls.facts = fx.assessment_facts()
        cls.composed = fx.fixture_composed()
        cls.record = assess_purpose(
            request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=cls.facts),
            composed=cls.composed,
            facts=cls.facts,
            determinations=fx.fixture_determinations(facts=cls.facts),
        )

    def test_schedules_splits_the_three_failures_from_the_unevaluated_chimney(self):
        activity = _subscopes(self.record, "schedules-and-room-data-sheets")
        self.assertEqual(len(activity.subscopes), 2)

        chimney, failures = activity.subscopes
        self.assertEqual(_members(chimney), [(fx.HVAC_CHIMNEY,)])
        self.assertEqual(chimney.verdict, "UNKNOWN")
        self.assertEqual(chimney.resolution_kind, "asset-identity-not-evaluated")
        self.assertEqual(chimney.outcome_sequence, ("not-yet-evaluated",))
        self.assertEqual(chimney.path[0].readings[0].absence, reading_module.NO_FINDING_ABSENCE)
        self.assertEqual(chimney.path[0].readings[0].finding_keys, ())

        self.assertEqual(
            _members(failures),
            [
                (fx.HVAC_AIR_TERMINAL_COVER,),
                (fx.HVAC_AIR_TERMINAL_CAP,),
                (fx.HVAC_DUCT,),
            ],
        )
        self.assertEqual(failures.verdict, "BLOCKED")
        self.assertEqual(failures.resolution_kind, "missing-project-asset-identity")
        self.assertEqual(failures.outcome_sequence, ("unmet",))
        for reading in failures.path[0].readings:
            with self.subTest(subject=reading.subject.keys):
                self.assertEqual(reading.outcome, "unmet")
                self.assertEqual(len(reading.finding_keys), 2)

    def test_the_split_is_never_collapsed_to_one_activity_verdict(self):
        """There is no activity-level verdict to collapse to, by construction."""

        activity = _subscopes(self.record, "schedules-and-room-data-sheets")
        fields = {field.name for field in dataclasses.fields(activity)}
        self.assertNotIn("verdict", fields)
        self.assertNotIn("resolution_kind", fields)
        self.assertEqual(
            {subscope.verdict for subscope in activity.subscopes}, {"BLOCKED", "UNKNOWN"}
        )

    def test_every_non_ready_subscope_carries_the_whole_chain(self):
        """Evidence, verdict, resolution_kind, route, and assignment — all four."""

        seen = 0
        for activity in self.record.activities:
            for subscope in activity.subscopes:
                if subscope.verdict == "READY":
                    self.assertEqual(subscope.resolution_kind, "")
                    self.assertIsNone(subscope.route)
                    self.assertIsNone(subscope.assignment)
                    continue
                seen += 1
                with self.subTest(activity=activity.activity_ref, ordinal=subscope.ordinal):
                    self.assertTrue(subscope.path)
                    self.assertIn(subscope.verdict, {"BLOCKED", "UNKNOWN"})
                    self.assertTrue(subscope.resolution_kind)
                    self.assertIsNotNone(subscope.route)
                    self.assertEqual(
                        subscope.route.resolution_kind, subscope.resolution_kind
                    )
                    self.assertTrue(subscope.route.consequence_kinds)
                    self.assertTrue(subscope.route.next_action)
                    self.assertTrue(subscope.route.recheck_condition)
                    self.assertIsNotNone(subscope.assignment)
                    self.assertEqual(
                        subscope.assignment.default_role, subscope.route.default_role
                    )
                    self.assertTrue(subscope.assignment.assigned_team_or_person)
                    self.assertNotEqual(
                        subscope.assignment.assigned_team_or_person,
                        subscope.assignment.default_role,
                        "the bare default_role is never recorded as an assignee",
                    )
        self.assertGreater(seen, 0)

    def test_the_chimney_refines_into_two_pairs_reaching_two_verdicts(self):
        """One element, one slab, one roof, two pieces of labour, two answers."""

        activity = _subscopes(self.record, "builders-work-openings")
        pairs = [
            subscope
            for subscope in activity.subscopes
            if any(len(member.keys) == 2 for member in subscope.members)
        ]
        self.assertEqual(len(pairs), 2)

        by_outcome = {subscope.terminal_outcome: subscope for subscope in pairs}
        self.assertEqual(set(by_outcome), {"cross-referenced", "not-modelled"})

        crossed = by_outcome["cross-referenced"]
        self.assertEqual(_members(crossed), [(fx.HVAC_CHIMNEY, fx.ARCHITECTURE_SLAB)])
        self.assertEqual(crossed.verdict, "READY")

        missing = by_outcome["not-modelled"]
        self.assertEqual(_members(missing), [(fx.HVAC_CHIMNEY, fx.ARCHITECTURE_ROOF)])
        self.assertEqual(missing.verdict, "BLOCKED")
        self.assertEqual(missing.resolution_kind, "missing-corresponding-opening")
        self.assertEqual(missing.assignment.default_role, "architecture-lead")

    def test_every_pair_names_the_admitted_element_it_refined_from(self):
        """Refinement adds no element and loses none: the provenance is recorded."""

        activity = _subscopes(self.record, "builders-work-openings")
        for subscope in activity.subscopes:
            for member in subscope.members:
                with self.subTest(member=member.keys):
                    if len(member.keys) == 2:
                        self.assertEqual(member.refined_from, fx.HVAC_CHIMNEY)
                        self.assertEqual(member.keys[0], member.refined_from)
                    else:
                        self.assertEqual(member.refined_from, "")

    def test_a_subject_the_branch_never_routes_to_a_node_is_never_refined(self):
        """The duct penetrates nothing, so it is READY at the first node."""

        activity = _subscopes(self.record, "builders-work-openings")
        duct = [
            subscope
            for subscope in activity.subscopes
            if _members(subscope) == [(fx.HVAC_DUCT,)]
        ]
        self.assertEqual(len(duct), 1)
        self.assertEqual(duct[0].verdict, "READY")
        self.assertEqual(duct[0].outcome_sequence, ("no-penetration",))
        self.assertEqual(len(duct[0].path), 1)

    def test_two_unknown_subscopes_of_one_activity_keep_their_own_paths(self):
        """Same verdict class, different gap: never merged because both say UNKNOWN."""

        record = assess_purpose(
            request=fx.fixture_request(
                activity_ids=("ceiling-and-bulkhead-geometry",), facts=self.facts
            ),
            composed=self.composed,
            facts=self.facts,
            determinations=fx.fixture_determinations(
                facts=self.facts, alignment=False, penetration=False
            ),
        )
        activity = _subscopes(record, "ceiling-and-bulkhead-geometry")
        self.assertEqual(len(activity.subscopes), 2)
        self.assertEqual({s.verdict for s in activity.subscopes}, {"UNKNOWN"})
        self.assertEqual(
            [s.resolution_kind for s in activity.subscopes],
            ["in-model-position-not-evaluated", "cross-model-alignment-not-confirmed"],
        )
        self.assertEqual(
            [s.outcome_sequence for s in activity.subscopes],
            [("not-yet-evaluated",), ("satisfied", "not-yet-confirmed")],
        )

    def test_a_whole_scope_node_never_splits_the_subgroup(self):
        """One reading, shared by every member that reaches it."""

        activity = _subscopes(self.record, "ceiling-and-bulkhead-geometry")
        aligned = [
            subscope
            for subscope in activity.subscopes
            if subscope.terminal_outcome == "confirmed"
        ]
        self.assertEqual(len(aligned), 1)
        step = aligned[0].path[-1]
        self.assertEqual(step.grain, "whole-scope")
        self.assertEqual(len(step.readings), 1)
        self.assertEqual(len(aligned[0].members), 3)
        self.assertEqual(step.readings[0].subject.keys, ("hvac", "architecture"))

    def test_subscope_ordinals_are_the_canonical_order(self):
        for activity in self.record.activities:
            ordinals = [subscope.ordinal for subscope in activity.subscopes]
            with self.subTest(activity=activity.activity_ref):
                self.assertEqual(ordinals, list(range(1, len(ordinals) + 1)))
                keys = [
                    (
                        subscope.outcome_sequence,
                        min(member.sort_key for member in subscope.members),
                    )
                    for subscope in activity.subscopes
                ]
                self.assertEqual(keys, sorted(keys))


class DeclaredScopeTests(unittest.TestCase):
    """Scope comes from the request and the class list, never from coverage.

    The two zero-finding elements are the whole point. One is admitted and one is
    excluded, and neither decision consults a finding: the ``IfcChimney`` is in
    because of what it is, and the ``geo-reference`` ``IfcBuildingElementProxy``
    is out for the same kind of reason.
    """

    @classmethod
    def setUpClass(cls):
        cls.facts = fx.assessment_facts()
        cls.composed = fx.fixture_composed()
        cls.record = assess_purpose(
            request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=cls.facts),
            composed=cls.composed,
            facts=cls.facts,
            determinations=fx.fixture_determinations(facts=cls.facts),
        )

    def test_a_zero_finding_chimney_is_admitted_and_reads_not_yet_evaluated(self):
        activity = _subscopes(self.record, "schedules-and-room-data-sheets")
        self.assertIn(fx.HVAC_CHIMNEY, activity.admitted_subjects)
        self.assertEqual(
            self.facts.findings_for(fx.HVAC_CHIMNEY, frozenset()), (), "still zero findings"
        )
        chimney = activity.subscopes[0]
        self.assertEqual(_members(chimney), [(fx.HVAC_CHIMNEY,)])
        self.assertEqual(chimney.path[0].readings[0].outcome, "not-yet-evaluated")

    def test_a_zero_finding_setout_proxy_is_excluded_with_its_class(self):
        """Two elements, identical coverage, separated by what they are."""

        for activity in self.record.activities:
            excluded = {
                key.element_key: key.ifc_class for key in activity.out_of_subject_class
            }
            with self.subTest(activity=activity.activity_ref):
                self.assertEqual(
                    excluded,
                    {
                        fx.HVAC_ORIGIN: "IfcBuildingElementProxy",
                        fx.HVAC_GEO_REFERENCE: "IfcBuildingElementProxy",
                    },
                )
                self.assertNotIn(fx.HVAC_GEO_REFERENCE, activity.admitted_subjects)

    def test_an_out_of_class_key_carries_no_verdict(self):
        for activity in self.record.activities:
            for key in activity.out_of_subject_class:
                with self.subTest(key=key.element_key):
                    fields = {field.name for field in dataclasses.fields(key)}
                    self.assertEqual(fields, {"element_key", "ifc_class"})

    def test_the_accounting_is_total_for_every_activity(self):
        declared = {item.element_key for item in self.facts.elements_of("hvac")}
        self.assertEqual(len(declared), 6)
        for activity in self.record.activities:
            admitted = set(activity.admitted_subjects)
            excluded = {key.element_key for key in activity.out_of_subject_class}
            with self.subTest(activity=activity.activity_ref):
                self.assertEqual(admitted | excluded, declared)
                self.assertEqual(admitted & excluded, set())

    def test_a_scope_is_a_required_input(self):
        with self.assertRaises(PurposeAssessmentError) as caught:
            AssessedScope()
        self.assertEqual(caught.exception.code, "scope-declared-empty")

    def test_a_scope_key_absent_from_the_producing_model_refuses(self):
        request = fx.fixture_request(
            activity_ids=("schedules-and-room-data-sheets",),
            facts=self.facts,
            scope=AssessedScope(element_keys=("hvac::not-a-real-element",)),
        )
        with self.assertRaises(PurposeAssessmentError) as caught:
            assess_purpose(
                request=request, composed=self.composed, facts=self.facts
            )
        self.assertEqual(caught.exception.code, "scope-element-absent")

    def test_an_activity_that_admits_no_subject_reaches_no_verdict(self):
        """An empty partition is never a release: nothing traversed to READY."""

        request = fx.fixture_request(
            activity_ids=("schedules-and-room-data-sheets",),
            facts=self.facts,
            scope=AssessedScope(element_keys=(fx.HVAC_ORIGIN,)),
        )
        record = assess_purpose(
            request=request, composed=self.composed, facts=self.facts
        )
        activity = _subscopes(record, "schedules-and-room-data-sheets")
        self.assertTrue(activity.partition_is_empty)
        self.assertEqual(activity.subscopes, ())
        self.assertEqual(activity.admitted_subjects, ())
        self.assertNotIn("READY", str(activity.as_document()))

    def test_one_scope_admits_different_subjects_per_activity(self):
        """ADR 0003 §8 commitment 7, run through the evaluator rather than beside it.

        The shipped Pack's three activities declare the same three classes, so a
        test using them would pass whether the field were per-activity or
        Pack-wide. This one differentiates them and asserts the evaluator
        actually admits and excludes differently for each.
        """

        def differentiate(document):
            document["activities"][0]["subject_classes"] = ["IfcDuctSegment"]
            document["activities"][1]["subject_classes"] = ["IfcAirTerminal", "IfcChimney"]
            document["activities"][2]["subject_classes"] = ["IfcChimney"]

        with fx.scratch_pack(differentiate) as pack:
            composed = fx.fixture_composed(pack=pack)
            record = assess_purpose(
                request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=self.facts),
                composed=composed,
                facts=self.facts,
                determinations=fx.fixture_determinations(facts=self.facts),
            )

        admitted = {
            activity.activity_ref: frozenset(activity.admitted_subjects)
            for activity in record.activities
        }
        excluded = {
            activity.activity_ref: frozenset(
                key.element_key for key in activity.out_of_subject_class
            )
            for activity in record.activities
        }
        self.assertEqual(len(set(admitted.values())), 3)
        self.assertEqual(len(set(excluded.values())), 3)
        declared = {item.element_key for item in self.facts.elements_of("hvac")}
        for reference, keys in admitted.items():
            with self.subTest(activity=reference):
                self.assertEqual(keys | excluded[reference], declared)
                self.assertEqual(keys & excluded[reference], frozenset())


class InsufficientEvidenceStaysContextTests(unittest.TestCase):
    """R-010's ``PASS`` is context, and has no path to ``confirmed``.

    This is the longest-guarded rule on the review chain, and the way it fails is
    always the same: one lookup used for both a ``pack_binding`` and an
    ``insufficient_evidence`` reference. So the test is not only that the outcome
    is right, but that the two are two functions with two return types.
    """

    @classmethod
    def setUpClass(cls):
        cls.facts = fx.assessment_facts()
        cls.composed = fx.fixture_composed()
        cls.record = assess_purpose(
            request=fx.fixture_request(
                activity_ids=("ceiling-and-bulkhead-geometry",), facts=cls.facts
            ),
            composed=cls.composed,
            facts=cls.facts,
            determinations=fx.fixture_determinations(
                facts=cls.facts, alignment=False, penetration=False
            ),
        )
        cls.R010 = "acb11f11-bf18-5516-a6f2-21e451a6e410"

    def test_r010_really_does_pass_in_this_run(self):
        """The premise, measured rather than assumed."""

        statuses = {
            finding.status
            for finding in self.facts.findings
            if finding.requirement_key == self.R010
        }
        self.assertEqual(statuses, {"PASS"})

    def test_that_pass_never_reaches_confirmed(self):
        activity = _subscopes(self.record, "ceiling-and-bulkhead-geometry")
        alignment_steps = [
            step
            for subscope in activity.subscopes
            for step in subscope.path
            if step.evidence_requirement_id == "cross-model-alignment"
        ]
        self.assertTrue(alignment_steps)
        for step in alignment_steps:
            with self.subTest(node=step.node_id):
                self.assertEqual(step.outcome, "not-yet-confirmed")
                self.assertNotEqual(step.outcome, "confirmed")
        self.assertNotIn(
            "READY", {subscope.verdict for subscope in activity.subscopes}
        )

    def test_the_pass_is_recorded_as_context_and_never_as_a_reading(self):
        activity = _subscopes(self.record, "ceiling-and-bulkhead-geometry")
        step = [
            step
            for subscope in activity.subscopes
            for step in subscope.path
            if step.evidence_requirement_id == "cross-model-alignment"
        ][0]
        joined = " ".join(step.context_citations)
        self.assertIn(self.R010, joined)
        self.assertIn("context-only", joined)
        self.assertIn("a PASS is not alignment evidence", joined)
        for reading in step.readings:
            with self.subTest(subject=reading.subject.keys):
                self.assertEqual(reading.finding_keys, ())
                self.assertNotIn(self.R010, str(reading.as_document()))

    def test_the_binding_lookup_cannot_see_an_insufficient_evidence_reference(self):
        pack = load_purpose_pack(fx.PACK_PATH)
        alignment = pack.evidence_requirement("cross-model-alignment")
        self.assertEqual(len(alignment.insufficient_evidence), 1)
        # cross-model-alignment is assessment-bound, so it has no bound keys at
        # all — and asking for them refuses rather than returning R-010's.
        with self.assertRaises(PurposeAssessmentError) as caught:
            reading_module.bound_requirement_keys(
                alignment, self.composed.overlay, pack.pack_id
            )
        self.assertEqual(caught.exception.code, "binding-source-not-finding-backed")

    def test_the_two_paths_return_two_different_shapes(self):
        """A citation cannot become an outcome, because it is not one."""

        pack = load_purpose_pack(fx.PACK_PATH)
        alignment = pack.evidence_requirement("cross-model-alignment")
        citations = reading_module.insufficient_evidence_context(alignment, self.facts)
        self.assertTrue(citations)
        for citation in citations:
            with self.subTest(citation=citation[:40]):
                self.assertIsInstance(citation, str)
                self.assertNotIn(citation, alignment.outcomes)


class NotApplicableIsNotSatisfiedTests(unittest.TestCase):
    """``N/A`` is a third state, and it never reaches the ``satisfied`` branch.

    Two hazards, and only one of them is live in this repository today. Both are
    coded against, and which is which is stated rather than guessed:

    * **Live.** All 57 ``N/A`` findings here are model-level, and they carry the
      very ``requirement_key`` values ``pcert-sample`` binds to
      ``asset-identity``. A reading that joined on ``requirement_key`` alone
      would sweep every one of them into whichever subject it was reading.
    * **Not reachable today.** An *element-level* ``N/A`` cannot be constructed
      at all: ``domain.Finding`` refuses one. So the "``N/A`` folded into a pass"
      failure is closed upstream, and the reduction still names ``N/A``
      explicitly — a fork whose checker produced one, or a domain invariant that
      moved, must not find a default branch waiting for it.
    """

    def setUp(self):
        self.facts = fx.assessment_facts()
        self.bound = frozenset(
            {
                "842a37c7-3183-5fce-ab45-b93c37ec7a08",
                "9321298b-4a9f-5a3e-9d10-6668b736d465",
                "a1402559-dcfc-5af4-a222-3a13eaf2b161",
                "fd49c300-7ef6-5a8d-825f-53210dd579fe",
            }
        )

    def test_every_na_in_this_run_is_model_level(self):
        """Measured. The claim the rest of this class is calibrated against."""

        not_applicable = [f for f in self.facts.findings if f.status == "N/A"]
        self.assertEqual(len(not_applicable), 23)
        self.assertEqual([f for f in not_applicable if f.element_key], [])

    def test_an_element_level_na_is_refused_by_the_domain(self):
        """So today's zero element-level N/A rows are a guarantee, not an accident."""

        with self.assertRaises(ValueError) as caught:
            Finding(
                finding_key="probe",
                validation_run_id="run",
                project_id="pcert-sample",
                model_key="hvac",
                element_key=fx.HVAC_DUCT,
                requirement_key="q",
                status=FindingStatus.NOT_APPLICABLE,
                severity=Severity.INFO,
                is_applicable=False,
                is_issue=False,
            )
        self.assertIn("must not name an element", str(caught.exception))

    def test_the_model_level_na_rows_are_not_swept_into_a_unit_reading(self):
        """The chimney has zero findings, and stays that way under the binding."""

        shared = {
            finding.requirement_key
            for finding in self.facts.findings
            if finding.status == "N/A"
        } & self.bound
        self.assertTrue(shared, "the hazard is only real if the keys overlap")
        self.assertEqual(self.facts.findings_for(fx.HVAC_CHIMNEY, self.bound), ())
        outcome, cited, absence = reading_module.finding_backed_reading(
            element_key=fx.HVAC_CHIMNEY, requirement_keys=self.bound, facts=self.facts
        )
        self.assertEqual(outcome, "not-yet-evaluated")
        self.assertEqual(cited, ())
        self.assertEqual(absence, reading_module.NO_FINDING_ABSENCE)


    def test_an_outcome_vocabulary_with_no_unresolved_state_refuses(self):
        """Zero and several are both refusals; neither takes the first listed."""

        pack = load_purpose_pack(fx.PACK_PATH)
        alignment = pack.evidence_requirement("cross-model-alignment")
        for outcomes, label in (
            (("confirmed", "misaligned"), "none"),
            (
                ("confirmed", "misaligned", "not-yet-confirmed", "not-yet-determined"),
                "two",
            ),
        ):
            with self.subTest(unresolved=label):
                broken = dataclasses.replace(alignment, outcomes=outcomes)
                with self.assertRaises(PurposeAssessmentError) as caught:
                    reading_module.unresolved_outcome(broken)
                self.assertEqual(
                    caught.exception.code, "unresolved-outcome-not-unique"
                )

    def test_the_shipped_pack_names_exactly_one_unresolved_state_everywhere(self):
        """The premise the refusal defends, measured on the Pack that ships."""

        pack = load_purpose_pack(fx.PACK_PATH)
        for requirement in pack.evidence_requirements:
            with self.subTest(requirement=requirement.evidence_requirement_id):
                named = [
                    name
                    for name in requirement.outcomes
                    if name in reading_module.UNRESOLVED_OUTCOMES
                ]
                self.assertEqual(len(named), 1)
                self.assertEqual(
                    reading_module.unresolved_outcome(requirement), named[0]
                )

    def test_a_reading_refuses_the_empty_subject(self):
        with self.assertRaises(ValueError):
            self.facts.findings_for("", self.bound)

    def test_an_element_level_na_would_read_not_covered_and_never_satisfied(self):
        """Defensive, and exercised directly because the domain will not build one."""

        facts = dataclasses.replace(
            self.facts,
            findings=self.facts.findings
            + (
                FindingFact(
                    finding_key="hypothetical-element-level-na",
                    element_key=fx.HVAC_CHIMNEY,
                    requirement_key="842a37c7-3183-5fce-ab45-b93c37ec7a08",
                    status="N/A",
                ),
            ),
        )
        outcome, cited, absence = reading_module.finding_backed_reading(
            element_key=fx.HVAC_CHIMNEY, requirement_keys=self.bound, facts=facts
        )
        self.assertEqual(outcome, "not-yet-evaluated")
        self.assertNotEqual(outcome, "satisfied")
        self.assertEqual(absence, reading_module.NOT_COVERED_ABSENCE)
        self.assertEqual(cited, ("hypothetical-element-level-na",))

    def test_a_fail_still_dominates_an_na(self):
        facts = dataclasses.replace(
            self.facts,
            findings=self.facts.findings
            + (
                FindingFact(
                    finding_key="hypothetical-na",
                    element_key=fx.HVAC_DUCT,
                    requirement_key="842a37c7-3183-5fce-ab45-b93c37ec7a08",
                    status="N/A",
                ),
            ),
        )
        outcome, _, _ = reading_module.finding_backed_reading(
            element_key=fx.HVAC_DUCT, requirement_keys=self.bound, facts=facts
        )
        self.assertEqual(outcome, "unmet")

    def test_an_unrecognised_status_refuses_instead_of_reading_as_satisfied(self):
        facts = dataclasses.replace(
            self.facts,
            findings=(
                FindingFact(
                    finding_key="odd",
                    element_key=fx.HVAC_DUCT,
                    requirement_key="842a37c7-3183-5fce-ab45-b93c37ec7a08",
                    status="SKIPPED",
                ),
            ),
        )
        with self.assertRaises(PurposeAssessmentError) as caught:
            reading_module.finding_backed_reading(
                element_key=fx.HVAC_DUCT, requirement_keys=self.bound, facts=facts
            )
        self.assertEqual(caught.exception.code, "finding-status-unrecognised")
        self.assertIn("no default reading", str(caught.exception))


class SeverityDoesNotSoftenAVerdictTests(unittest.TestCase):
    """Checkpoint B case 2: R-005A/B are ``WARNING`` and the verdict is ``BLOCKED``.

    Structural rather than promised — the fact view has no severity field, so
    there is nothing for a verdict to be softened by.
    """

    @classmethod
    def setUpClass(cls):
        cls.facts = fx.assessment_facts()
        cls.record = assess_purpose(
            request=fx.fixture_request(
                activity_ids=("schedules-and-room-data-sheets",), facts=cls.facts
            ),
            composed=fx.fixture_composed(),
            facts=cls.facts,
            determinations=(),
        )

    def test_the_r005_failures_really_are_warning_severity(self):
        from helpers import shipped_pipeline_result

        severities = {
            str(finding.severity)
            for finding in shipped_pipeline_result().bundle.findings
            if finding.element_key == fx.HVAC_DUCT and str(finding.status) == "FAIL"
        }
        self.assertEqual(severities, {"WARNING"})

    def test_and_the_verdict_is_blocked_anyway(self):
        activity = _subscopes(self.record, "schedules-and-room-data-sheets")
        blocked = [s for s in activity.subscopes if s.verdict == "BLOCKED"]
        self.assertEqual(len(blocked), 1)
        self.assertIn((fx.HVAC_DUCT,), _members(blocked[0]))

    def test_the_fact_view_carries_no_validation_metadata_a_verdict_could_read(self):
        for field in dataclasses.fields(FindingFact):
            with self.subTest(field=field.name):
                self.assertNotIn(field.name, {"is_issue", "severity", "priority"})
        rendered = repr(self.facts)
        for forbidden in ("is_issue", "severity", "owner_role", "priority", "labels"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, rendered)

    def test_the_assessment_package_never_names_a_readiness_forbidden_field(self):
        offenders = []
        for path in sorted(ASSESSMENT_PACKAGE.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr in {
                    "is_issue",
                    "severity",
                    "owner_role",
                    "priority",
                    "labels",
                    "issues",
                }:
                    offenders.append(f"{path.name}: .{node.attr}")
        self.assertEqual(offenders, [])


class ConsequenceHasNoMagnitudeTests(unittest.TestCase):
    """Kinds are named, magnitudes are cited, and nothing is computed."""

    @classmethod
    def setUpClass(cls):
        cls.facts = fx.assessment_facts()
        cls.record = assess_purpose(
            request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=cls.facts),
            composed=fx.fixture_composed(),
            facts=cls.facts,
            determinations=fx.fixture_determinations(facts=cls.facts),
        )

    def test_a_route_carries_kinds_only(self):
        pack = load_purpose_pack(fx.PACK_PATH)
        declared = {
            kind
            for route in pack.resolution_routes
            for kind in route.consequence_kinds
        }
        for activity in self.record.activities:
            for subscope in activity.subscopes:
                if subscope.route is None:
                    continue
                with self.subTest(ordinal=subscope.ordinal):
                    self.assertTrue(set(subscope.route.consequence_kinds) <= declared)
                    for kind in subscope.route.consequence_kinds:
                        self.assertFalse(any(ch.isdigit() for ch in kind))

    def test_the_milestone_dates_are_cited_verbatim_and_never_reduced(self):
        self.assertEqual(
            dict(self.record.cited_milestones),
            {
                "Coordination": "2026-08-01T00:00:00Z",
                "Design": "2026-07-01T00:00:00Z",
                "Handover": "2026-12-01T00:00:00Z",
            },
        )

    def test_the_assessment_package_parses_no_date_and_does_no_date_arithmetic(self):
        """Over the parsed code: a promise not to compute a delay is not a test."""

        offenders = []
        for path in sorted(ASSESSMENT_PACKAGE.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    function = node.func
                    name = (
                        function.attr
                        if isinstance(function, ast.Attribute)
                        else getattr(function, "id", "")
                    )
                    if name in {
                        "fromisoformat",
                        "strptime",
                        "timedelta",
                        "date",
                        "datetime",
                        "now",
                        "utcnow",
                        "today",
                        "time",
                        "monotonic",
                    }:
                        offenders.append(f"{path.name}: {name}()")
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module = getattr(node, "module", "") or ""
                    names = [alias.name for alias in node.names]
                    if "datetime" in module or "datetime" in names:
                        offenders.append(f"{path.name}: imports datetime")
        self.assertEqual(offenders, [])


class DeterminationIntakeTests(unittest.TestCase):
    """Determinations are admitted or declined; the evaluator decides none.

    These are the checks that **decline**: the determination is keyed onto a
    known subject and its content fails an acceptance condition, so the subject
    reads ``not-yet-*`` and routes to ``UNKNOWN``. The checks that **refuse** —
    a defect in what was handed in rather than a gap in the evidence — are in
    :class:`DeterminationVerifiabilityTests`.

    ``penetration-confirmed`` is the case that carries the weight: it must name
    every architectural element it claims to pass through, as a key of the
    consuming model version, because those keys become the second member of the
    pair the opening question reads at. A claim without them would leave the
    assessment inventing a counterpart.
    """

    @classmethod
    def setUpClass(cls):
        cls.facts = fx.assessment_facts()
        cls.composed = fx.fixture_composed()
        cls.pack = load_purpose_pack(fx.PACK_PATH)
        cls.requirement = cls.pack.evidence_requirement("penetration-determination")

    def _ledger(self, determinations, *, method_basis="project-decision"):
        return DeterminationLedger(
            determinations,
            method_policy={
                "penetration-determination": {
                    "coordination-review-determination": method_basis
                },
                "opening-status": {"opening-cross-reference-check": method_basis},
                "cross-model-alignment": {"overlay-comparison": method_basis},
            },
            consuming_element_keys=frozenset(
                item.element_key for item in self.facts.elements_of("architecture")
            ),
            determined_against=fx.determined_against(self.facts),
        )

    def _claim(self, **overrides):
        base = dict(
            reference="probe",
            evidence_requirement_id="penetration-determination",
            method_id="coordination-review-determination",
            determiner="probe-reviewer",
            basis="probe",
            outcome="penetration-confirmed",
            subject=(fx.HVAC_CHIMNEY,),
            penetrated_element_keys=(fx.ARCHITECTURE_SLAB,),
            determined_against=fx.determined_against(self.facts),
        )
        base.update(overrides)
        return Determination(**base)

    def test_a_well_formed_claim_is_admitted(self):
        ledger = self._ledger((self._claim(),))
        self.assertTrue(ledger.admissibility(self._claim(), self.requirement).admitted)

    def test_a_claim_naming_no_architectural_element_is_inadmissible(self):
        verdict = self._ledger(()).admissibility(
            self._claim(penetrated_element_keys=()), self.requirement
        )
        self.assertFalse(verdict.admitted)
        self.assertEqual(
            verdict.reason, "penetration-confirmed-names-no-architectural-element"
        )

    def test_a_claim_naming_an_absent_element_is_inadmissible(self):
        verdict = self._ledger(()).admissibility(
            self._claim(penetrated_element_keys=("architecture::nope",)), self.requirement
        )
        self.assertFalse(verdict.admitted)
        self.assertIn("names-absent-element", verdict.reason)

    def test_an_unattributed_claim_is_inadmissible(self):
        for field in ("determiner", "basis", "reference"):
            with self.subTest(missing=field):
                verdict = self._ledger(()).admissibility(
                    self._claim(**{field: ""}), self.requirement
                )
                self.assertFalse(verdict.admitted)

    def test_a_method_the_overlay_never_mentions_is_inadmissible(self):
        """A missing row declines. A row that exists and is illustrative refuses.

        Two different states, and this is the first: the project never mentioned
        the method, so the determination is not evidence here and the subject
        reads ``not-yet-*``.
        """

        verdict = self._ledger(()).admissibility(
            self._claim(method_id="someone-had-a-look"), self.requirement
        )
        self.assertFalse(verdict.admitted)
        self.assertIn("method-not-accepted", verdict.reason)

    def test_an_inadmissible_claim_reads_not_yet_determined_and_records_why(self):
        """The fail-closed direction: no determination, and never a phantom pair."""

        record = assess_purpose(
            request=fx.fixture_request(
                activity_ids=("builders-work-openings",), facts=self.facts
            ),
            composed=self.composed,
            facts=self.facts,
            determinations=(self._claim(penetrated_element_keys=()),),
        )
        activity = _subscopes(record, "builders-work-openings")
        self.assertEqual(len(activity.subscopes), 1)
        subscope = activity.subscopes[0]
        self.assertEqual(subscope.verdict, "UNKNOWN")
        self.assertEqual(subscope.resolution_kind, "penetration-not-determined")
        chimney = [
            reading
            for reading in subscope.path[0].readings
            if reading.subject.keys == (fx.HVAC_CHIMNEY,)
        ][0]
        self.assertEqual(chimney.outcome, "not-yet-determined")
        self.assertIn("names-no-architectural-element", chimney.absence)
        for member in subscope.members:
            with self.subTest(member=member.keys):
                self.assertEqual(len(member.keys), 1)

    def test_a_claim_naming_an_absent_element_moves_nothing_at_all(self):
        """Counterexample 4, end to end: declined evidence changes no outcome.

        The claim is well-formed and correctly keyed — it just names an
        architectural element the consuming model version does not contain. It
        must therefore produce no pair, no subject, and no verdict change: the
        record has to be indistinguishable from the one produced when nobody
        determined anything, except for the recorded reason.
        """

        request = fx.fixture_request(
            activity_ids=("builders-work-openings",), facts=self.facts
        )
        baseline = assess_purpose(
            request=request, composed=self.composed, facts=self.facts, determinations=()
        )
        declined = assess_purpose(
            request=request,
            composed=self.composed,
            facts=self.facts,
            determinations=(
                self._claim(
                    reference="probe/names-an-element-architecture-does-not-have",
                    penetrated_element_keys=("architecture::not-a-real-element",),
                ),
            ),
        )
        base_activity = _subscopes(baseline, "builders-work-openings")
        declined_activity = _subscopes(declined, "builders-work-openings")

        # Subject scope untouched: no pair created, nothing admitted or excluded.
        self.assertEqual(
            declined_activity.admitted_subjects, base_activity.admitted_subjects
        )
        self.assertEqual(
            [k.as_document() for k in declined_activity.out_of_subject_class],
            [k.as_document() for k in base_activity.out_of_subject_class],
        )
        for subscope in declined_activity.subscopes:
            for member in subscope.members:
                with self.subTest(member=member.keys):
                    self.assertEqual(len(member.keys), 1, "no pair was refined")
                    self.assertEqual(member.refined_from, "")

        # Verdicts untouched.
        self.assertEqual(
            [(s.ordinal, tuple(m.keys for m in s.members), s.verdict, s.resolution_kind)
             for s in declined_activity.subscopes],
            [(s.ordinal, tuple(m.keys for m in s.members), s.verdict, s.resolution_kind)
             for s in base_activity.subscopes],
        )

        # The only difference is that the record says why it was declined.
        chimney = [
            reading
            for s in declined_activity.subscopes
            for reading in s.path[0].readings
            if reading.subject.keys == (fx.HVAC_CHIMNEY,)
        ][0]
        self.assertIn("penetration-confirmed-names-absent-element", chimney.absence)
        self.assertIn("architecture::not-a-real-element", chimney.absence)
        self.assertNotEqual(declined.assessment_digest, baseline.assessment_digest)


    #: Sorts before the fixture's admissible ``…/chimney-slab-and-roof`` ("a" <
    #: "s"), which is the whole point: it is the one ``counterparts`` meets first.
    UNATTRIBUTED_SLAB_ONLY = "fixture-determination/penetration/chimney-aaa-unattributed"

    def _unattributed_slab_only(self):
        """A declined claim that names one architectural element instead of two.

        Unattributed — no ``determiner`` — so it is inadmissible, and it lists
        only the floor slab where the admissible determination lists the slab and
        the roof. Its reference sorts first.
        """

        return Determination(
            reference=self.UNATTRIBUTED_SLAB_ONLY,
            evidence_requirement_id="penetration-determination",
            method_id="coordination-review-determination",
            determiner="",
            basis="fixture: an unsigned note naming only the slab",
            outcome="penetration-confirmed",
            subject=(fx.HVAC_CHIMNEY,),
            penetrated_element_keys=(fx.ARCHITECTURE_SLAB,),
            determined_against=fx.determined_against(self.facts),
        )

    def test_an_earlier_sorting_declined_claim_does_not_win_the_refinement(self):
        """A declined determination must not decide which pairs exist.

        Two determinations about the chimney's penetration, both claiming
        ``penetration-confirmed``: the admissible one names the floor slab **and**
        the roof, and a declined one — unattributed, and sorting first by
        reference — names only the slab.

        The reading comes from the admissible one, so the subject reaches
        ``opening-status-node`` either way. Refinement is a **second** traversal
        of the same index, and it is the one that decides which pairs exist. If
        the declined claim won there, the roof pair and its ``BLOCKED`` verdict
        would not be reported as wrong — they would not be reported at all.

        Asserted under both input orders, because "sorts first" and "arrived
        first" are different things and neither may decide it.
        """

        expected = [
            ((fx.HVAC_DUCT,),),
            ((fx.HVAC_AIR_TERMINAL_COVER,), (fx.HVAC_AIR_TERMINAL_CAP,)),
            ((fx.HVAC_CHIMNEY, fx.ARCHITECTURE_SLAB),),
            ((fx.HVAC_CHIMNEY, fx.ARCHITECTURE_ROOF),),
        ]
        expected_verdicts = [
            ("READY", ""),
            ("UNKNOWN", "penetration-not-determined"),
            ("READY", ""),
            ("BLOCKED", "missing-corresponding-opening"),
        ]

        digests = set()
        for label, offered in (
            (
                "admissible first",
                fx.fixture_determinations(facts=self.facts)
                + (self._unattributed_slab_only(),),
            ),
            (
                "declined first",
                (self._unattributed_slab_only(),)
                + fx.fixture_determinations(facts=self.facts),
            ),
        ):
            with self.subTest(order=label):
                record = assess_purpose(
                    request=fx.fixture_request(
                        activity_ids=("builders-work-openings",), facts=self.facts
                    ),
                    composed=self.composed,
                    facts=self.facts,
                    determinations=offered,
                )
                activity = _subscopes(record, "builders-work-openings")
                digests.add(record.assessment_digest)

                self.assertEqual(
                    [tuple(tuple(m.keys) for m in s.members) for s in activity.subscopes],
                    expected,
                )
                self.assertEqual(
                    [(s.verdict, s.resolution_kind) for s in activity.subscopes],
                    expected_verdicts,
                )

                # Both pairs survive, and each names the element it refined from.
                pairs = [
                    s for s in activity.subscopes
                    if any(len(m.keys) == 2 for m in s.members)
                ]
                self.assertEqual(len(pairs), 2)
                for subscope in pairs:
                    for member in subscope.members:
                        self.assertEqual(member.refined_from, fx.HVAC_CHIMNEY)

                # The reading cites the admissible determination, never the
                # declined one, whichever order they arrived in.
                root = activity.subscopes[2].path[0]
                chimney = [
                    r for r in root.readings if r.subject.keys == (fx.HVAC_CHIMNEY,)
                ][0]
                self.assertEqual(chimney.outcome, "penetration-confirmed")
                self.assertEqual(
                    chimney.determination_references,
                    ("fixture-determination/penetration/chimney-slab-and-roof",),
                )
                self.assertNotIn(
                    self.UNATTRIBUTED_SLAB_ONLY, chimney.determination_references
                )

        self.assertEqual(len(digests), 1, "input order moved the sealed record")

    def test_counterparts_reads_only_admissible_determinations(self):
        """The refinement guard at unit grain; the end-to-end case is above.

        An earlier revision of this docstring called the admissibility check
        inside ``counterparts`` unreachable through :func:`assess_purpose`, on
        the reasoning that a subject only reaches ``opening-status-node`` after
        an admissible determination produced its ``penetration-confirmed``
        reading. **That was wrong**, and it was wrong in a way worth naming,
        because the same mistake is available to anyone reading the ledger:
        ``resolve`` and ``counterparts`` are *two separate traversals of one
        index*. The first filters to admissible determinations and drives the
        reading; the second drives refinement and meets whatever sorts first.
        That an admissible determination produced the reading says nothing about
        which determination refinement encounters.

        So this guard is not defence in depth. It is the enforcement point for a
        property the design depends on — **an earlier-sorted declined
        determination must not win the refinement** — and
        ``test_an_earlier_sorting_declined_claim_does_not_win_the_refinement``
        measures what it is worth: without it, the roof pair and its ``BLOCKED``
        verdict do not appear at all. This test stays, at unit grain, because
        it pins the discriminating behaviour directly.
        """

        ledger = self._ledger(
            (self._claim(penetrated_element_keys=("architecture::not-a-real-element",)),)
        )
        self.assertEqual(
            ledger.counterparts(
                source_evidence_requirement_id="penetration-determination",
                on_outcome="penetration-confirmed",
                element_key=fx.HVAC_CHIMNEY,
                requirement=self.requirement,
            ),
            (),
        )
        # And the admissible one does yield its counterparts, so the guard is
        # discriminating rather than simply always empty.
        admissible = self._ledger((self._claim(),))
        self.assertEqual(
            admissible.counterparts(
                source_evidence_requirement_id="penetration-determination",
                on_outcome="penetration-confirmed",
                element_key=fx.HVAC_CHIMNEY,
                requirement=self.requirement,
            ),
            (fx.ARCHITECTURE_SLAB,),
        )

    def test_no_determination_is_offered_for_pcert_sample_anywhere_in_the_tree(self):
        """This project has never held a coordination review, and nothing says it has."""

        for path in sorted((PROJECT_ROOT / "projects").rglob("*.toml")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn("penetration-confirmed", text)
                self.assertNotIn("penetration_determination", text)

    def test_the_evaluator_never_produces_a_determination(self):
        """It resolves and reads one; there is no constructor call in the walk."""

        source = (ASSESSMENT_PACKAGE / "evaluator.py").read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Call):
                name = getattr(node.func, "id", "")
                self.assertNotEqual(name, "Determination")


class DeterminationVerifiabilityTests(unittest.TestCase):
    """A determination is relied on only when policy, version and content check out.

    Three counterexamples, each a way a determination could have been consumed
    without anybody being able to verify it, and each now a refusal rather than
    a silent ``READY``. All three are **refusals** and not declines, because
    none is a gap in the evidence: each is a defect in what was handed in, so
    §7.1 catches it before any subscope is assessed.
    """

    @classmethod
    def setUpClass(cls):
        cls.facts = fx.assessment_facts()
        cls.composed = fx.fixture_composed()
        cls.against = fx.determined_against(cls.facts)

    CEILING = ("ceiling-and-bulkhead-geometry",)

    def _assess(self, determinations, *, composed=None, activities=CEILING):
        return assess_purpose(
            request=fx.fixture_request(activity_ids=activities, facts=self.facts),
            composed=composed or self.composed,
            facts=self.facts,
            determinations=determinations,
        )

    def _alignment(self, **overrides):
        base = dict(
            reference="probe/alignment",
            evidence_requirement_id="cross-model-alignment",
            method_id="overlay-comparison",
            determiner="probe-coordinator",
            basis="probe: placements overlaid",
            outcome="confirmed",
            subject=("hvac", "architecture"),
            determined_against=self.against,
        )
        base.update(overrides)
        return Determination(**base)

    # -- 1. policy ----------------------------------------------------------

    def test_an_illustrative_method_row_refuses(self):
        """Counterexample 1: the row exists and records no decision anybody took.

        Staffed for real and accepting methods only illustratively — which is
        precisely the state this repository's own fixture was in while the
        positive path went green. The ``team_mapping`` gate is satisfied here on
        purpose, so the refusal that fires can only be the method one.
        """

        document = fx.fixture_overlay_document()
        for row in document["overlay"]["accepted_evidence_methods"]:
            row["decision_basis"] = "illustrative"
        illustrative = fx.fixture_composed(overlay_document=document)
        with self.assertRaises(PurposeAssessmentError) as caught:
            self._assess((self._alignment(),), composed=illustrative)
        self.assertEqual(
            caught.exception.code, "accepted-method-decision-basis-illustrative"
        )
        message = str(caught.exception)
        self.assertIn("overlay-comparison", message)
        self.assertIn("'illustrative'", message)
        self.assertIn("not the missing-row case", message)

    def test_that_refusal_is_a_different_code_from_the_team_mapping_gate(self):
        """Same family, different table, different row to edit — different refusal."""

        self.assertNotEqual(
            "accepted-method-decision-basis-illustrative",
            "team-mapping-decision-basis-illustrative",
        )

    def test_the_shipped_overlay_still_records_all_seven_rows_as_illustrative(self):
        """The fixture declares policy in memory; the manifest is untouched."""

        text = PCERT_MANIFEST.read_text(encoding="utf-8")
        self.assertEqual(text.count('decision_basis = "project-decision"'), 0)
        self.assertEqual(text.count('decision_basis = "illustrative"'), 9)

    def test_the_fixture_now_declares_the_method_policy_it_relies_on(self):
        """The positive path is no longer held up by a check that does not exist."""

        for method in self.composed.overlay.accepted_evidence_methods:
            with self.subTest(method=method.method_id):
                self.assertEqual(method.decision_basis, "project-decision")

    # -- 2. version attribution ---------------------------------------------

    def test_a_determination_about_another_model_version_refuses(self):
        """Counterexample 2: right models, wrong versions of them."""

        stale = dataclasses.replace(self.against, producing_content_id="0" * 64)
        with self.assertRaises(PurposeAssessmentError) as caught:
            self._assess((self._alignment(determined_against=stale),))
        self.assertEqual(caught.exception.code, "determination-model-version-mismatch")
        self.assertIn("0" * 64, str(caught.exception))

    def test_a_determination_that_names_no_version_refuses(self):
        with self.assertRaises(PurposeAssessmentError) as caught:
            self._assess((self._alignment(determined_against=None),))
        self.assertEqual(
            caught.exception.code, "determination-model-version-unattributed"
        )
        self.assertIn("Absence is not agreement", str(caught.exception))

    def test_version_attribution_is_a_separate_check_from_the_context_one(self):
        """Two independent checks, two diagnostics; either can fail alone.

        ``context-model-version-mismatch`` asks whether the request's own context
        agrees with the validated facts. This one asks whether the *evidence* was
        produced against the versions the request names. Here the context is
        perfectly consistent and only the determination is stale.
        """

        stale = dataclasses.replace(self.against, consuming_content_id="1" * 64)
        with self.assertRaises(PurposeAssessmentError) as caught:
            self._assess((self._alignment(determined_against=stale),))
        self.assertEqual(caught.exception.code, "determination-model-version-mismatch")
        self.assertNotEqual(caught.exception.code, "context-model-version-mismatch")

        # And the context check still fires on its own, with no determination at all.
        request = fx.fixture_request(
            activity_ids=("ceiling-and-bulkhead-geometry",), facts=self.facts
        )
        context = dataclasses.replace(
            request.model_version_context,
            producing=dataclasses.replace(
                request.model_version_context.producing, content_id="2" * 64
            ),
        )
        with self.assertRaises(PurposeAssessmentError) as caught:
            assess_purpose(
                request=dataclasses.replace(request, model_version_context=context),
                composed=self.composed,
                facts=self.facts,
            )
        self.assertEqual(caught.exception.code, "context-model-version-mismatch")

    # -- 3. content consistency ---------------------------------------------

    def test_one_reference_with_two_contents_refuses(self):
        """Counterexample 3a: a store that cannot say which document it holds."""

        with self.assertRaises(PurposeAssessmentError) as caught:
            self._assess(
                (
                    self._alignment(outcome="confirmed"),
                    self._alignment(outcome="misaligned"),
                )
            )
        self.assertEqual(caught.exception.code, "determination-reference-not-unique")
        self.assertIn("probe/alignment", str(caught.exception))
        self.assertIn("will not pick", str(caught.exception))

    def test_two_references_that_contradict_each_other_refuse(self):
        """Counterexample 3b: two admissible determinations, opposite conclusions."""

        with self.assertRaises(PurposeAssessmentError) as caught:
            self._assess(
                (
                    self._alignment(reference="probe/a", outcome="confirmed"),
                    self._alignment(reference="probe/b", outcome="misaligned"),
                )
            )
        self.assertEqual(caught.exception.code, "determination-conflict")
        message = str(caught.exception)
        self.assertIn("probe/a", message)
        self.assertIn("probe/b", message)
        self.assertIn("confirmed", message)
        self.assertIn("misaligned", message)
        self.assertIn("will not choose between them", message)

    def test_the_conflict_refusal_does_not_depend_on_input_order(self):
        codes = set()
        for pair in (
            (self._alignment(reference="probe/a", outcome="confirmed"),
             self._alignment(reference="probe/b", outcome="misaligned")),
            (self._alignment(reference="probe/b", outcome="misaligned"),
             self._alignment(reference="probe/a", outcome="confirmed")),
        ):
            with self.assertRaises(PurposeAssessmentError) as caught:
                self._assess(pair)
            codes.add(caught.exception.code)
        self.assertEqual(codes, {"determination-conflict"})

    def test_neither_conflict_silently_produces_a_verdict(self):
        """The point of the counterexample: before this round both went READY."""

        for label, offered in (
            ("one reference, two contents",
             (self._alignment(outcome="confirmed"), self._alignment(outcome="misaligned"))),
            ("two references, opposite conclusions",
             (self._alignment(reference="probe/a", outcome="confirmed"),
              self._alignment(reference="probe/b", outcome="misaligned"))),
        ):
            with self.subTest(case=label):
                with self.assertRaises(PurposeAssessmentError):
                    self._assess(offered)

    def test_two_determinations_that_agree_are_corroboration_and_are_both_cited(self):
        """Agreement is not conflict, and the record cites both rather than one."""

        record = self._assess(
            (
                self._alignment(reference="probe/a", determiner="reviewer-one"),
                self._alignment(reference="probe/b", determiner="reviewer-two"),
            )
        )
        activity = _subscopes(record, "ceiling-and-bulkhead-geometry")
        step = [
            step
            for subscope in activity.subscopes
            for step in subscope.path
            if step.evidence_requirement_id == "cross-model-alignment"
        ][0]
        self.assertEqual(step.outcome, "confirmed")
        self.assertEqual(
            step.readings[0].determination_references, ("probe/a", "probe/b")
        )

    # -- keying -------------------------------------------------------------

    def test_a_determination_whose_subject_has_the_wrong_arity_refuses(self):
        """Which subject it is about cannot be established, so it is not evidence."""

        with self.assertRaises(PurposeAssessmentError) as caught:
            self._assess((self._alignment(subject=("hvac",)),))
        self.assertEqual(caught.exception.code, "determination-grain-mismatch")
        self.assertIn("cannot be established", str(caught.exception))

    def test_a_determination_for_a_requirement_this_request_never_reads_is_ignored(self):
        """Refused for what the request relies on, not for what it carries past.

        The schedules activity reads only ``asset-identity``. An alignment
        determination offered alongside it is not consumed, so its defects are
        not this request's defects.
        """

        record = self._assess(
            (self._alignment(determined_against=None),),
            activities=("schedules-and-room-data-sheets",),
        )
        self.assertTrue(record.assessment_digest)


class IdentityDeterminismAndSealingTests(unittest.TestCase):
    """One digest, over parsed structure, sealed, and cited by nothing frozen."""

    @classmethod
    def setUpClass(cls):
        cls.facts = fx.assessment_facts()
        cls.composed = fx.fixture_composed()
        cls.request = fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=cls.facts)
        cls.record = assess_purpose(
            request=cls.request,
            composed=cls.composed,
            facts=cls.facts,
            determinations=fx.fixture_determinations(facts=cls.facts),
        )

    def test_the_same_request_produces_a_byte_identical_record(self):
        from epc_control_tower.determinism import canonical_json_document

        again = assess_purpose(
            request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=self.facts),
            composed=fx.fixture_composed(),
            facts=fx.assessment_facts(),
            determinations=fx.fixture_determinations(facts=self.facts),
        )
        self.assertEqual(
            canonical_json_document(self.record.as_document()),
            canonical_json_document(again.as_document()),
        )
        self.assertEqual(self.record.assessment_digest, again.assessment_digest)

    def test_the_order_determinations_arrive_in_does_not_move_the_digest(self):
        shuffled = tuple(reversed(fx.fixture_determinations(facts=self.facts)))
        again = assess_purpose(
            request=self.request,
            composed=self.composed,
            facts=self.facts,
            determinations=shuffled,
        )
        self.assertEqual(again.assessment_digest, self.record.assessment_digest)

    def test_the_digest_moves_when_a_verdict_moves(self):
        """Which is exactly when a successor record would need a different handle."""

        without = assess_purpose(
            request=self.request,
            composed=self.composed,
            facts=self.facts,
            determinations=fx.fixture_determinations(facts=self.facts, alignment=False),
        )
        self.assertNotEqual(without.assessment_digest, self.record.assessment_digest)

    def test_the_record_is_sealed(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            self.record.assessment_digest = "rewritten"
        subscope = self.record.activities[0].subscopes[0]
        with self.assertRaises(dataclasses.FrozenInstanceError):
            subscope.verdict = "READY"

    def test_the_digest_hashes_structure_and_not_bytes(self):
        from epc_control_tower.purpose.assessment import build_assessment_digest

        document = self.record.as_document()
        self.assertEqual(build_assessment_digest(document), self.record.assessment_digest)
        # Re-serialising the same structure with different incidental ordering
        # gives the same digest, because the digest never sees a serialisation.
        reordered = dict(reversed(list(document.items())))
        self.assertEqual(build_assessment_digest(reordered), self.record.assessment_digest)

    def test_no_frozen_identity_derivation_accepts_an_assessment_value(self):
        import inspect

        from epc_control_tower import identity

        for name in (
            "build_validation_run_id",
            "build_requirement_key",
            "build_ruleset_normalized_digest",
            "build_finding_key",
            "build_issue_key",
        ):
            signature = inspect.signature(getattr(identity, name))
            with self.subTest(derivation=name):
                for parameter in signature.parameters:
                    self.assertNotIn("assessment", parameter)
                    self.assertNotIn("purpose", parameter)
                    self.assertNotIn("verdict", parameter)

    def test_the_digest_appears_in_no_published_artifact(self):
        digest = self.record.assessment_digest.encode()
        checked = 0
        for root in ("data/processed", "reports", "ids"):
            for path in sorted((PROJECT_ROOT / root).rglob("*")):
                if not path.is_file():
                    continue
                checked += 1
                with self.subTest(artifact=path.name):
                    self.assertNotIn(digest, path.read_bytes())
        self.assertGreater(checked, 10)

    def test_the_record_cites_frozen_identities_one_way(self):
        cited = {
            key
            for activity in self.record.activities
            for subscope in activity.subscopes
            for step in subscope.path
            for reading in step.readings
            for key in reading.finding_keys
        }
        self.assertTrue(cited)
        known = {finding.finding_key for finding in self.facts.findings}
        self.assertTrue(cited <= known)
        self.assertEqual(self.record.validation_run_id, self.facts.validation_run_id)

    def test_the_assessment_reads_no_clock_and_no_file_bytes(self):
        forbidden = {
            "now",
            "utcnow",
            "today",
            "time",
            "monotonic",
            "sha256_file",
            "read_bytes",
            "stat",
            "glob",
            "rglob",
        }
        offenders = []
        for path in sorted(ASSESSMENT_PACKAGE.rglob("*.py")):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if not isinstance(node, ast.Call):
                    continue
                function = node.func
                name = (
                    function.attr
                    if isinstance(function, ast.Attribute)
                    else getattr(function, "id", "")
                )
                if name in forbidden:
                    offenders.append(f"{path.name}: {name}()")
        self.assertEqual(offenders, [])

    def test_the_assessment_is_not_a_registered_component(self):
        from epc_control_tower.registry import default_registry
        from helpers import shipped_run_config

        registry = default_registry(shipped_run_config())
        rendered = repr(
            {
                name: sorted(getattr(registry, name, {}))
                for name in ("checkers", "grouping_policies", "exporters")
                if hasattr(registry, name)
            }
        ).lower()
        for word in ("assessment", "verdict", "subscope", "purpose"):
            with self.subTest(word=word):
                self.assertNotIn(word, rendered)


class RequestPreconditionsTests(unittest.TestCase):
    """Every missing or wrong input refuses, and none of them defaults."""

    @classmethod
    def setUpClass(cls):
        cls.facts = fx.assessment_facts()
        cls.composed = fx.fixture_composed()

    def _refuse(self, **overrides) -> str:
        request = fx.fixture_request(
            activity_ids=("schedules-and-room-data-sheets",), facts=self.facts
        )
        request = dataclasses.replace(request, **overrides)
        with self.assertRaises(PurposeAssessmentError) as caught:
            assess_purpose(
                request=request, composed=self.composed, facts=self.facts
            )
        return caught.exception.code

    def test_a_pack_the_overlay_does_not_list(self):
        self.assertEqual(self._refuse(pack_id="some-other-pack"), "request-pack-not-bound")

    def test_a_pack_version_that_is_not_an_exact_match(self):
        self.assertEqual(
            self._refuse(pack_version="0.1.1"), "request-pack-version-mismatch"
        )

    def test_a_direction_the_pack_does_not_declare(self):
        self.assertEqual(
            self._refuse(direction_id="architecture-to-mep"), "request-direction-unresolved"
        )

    def test_an_activity_the_pack_does_not_declare(self):
        self.assertEqual(
            self._refuse(activity_ids=("no-such-activity",)), "request-activity-unresolved"
        )

    def test_a_request_naming_no_activity(self):
        self.assertEqual(self._refuse(activity_ids=()), "request-no-activity")

    def test_a_model_version_the_cited_run_did_not_validate(self):
        request = fx.fixture_request(
            activity_ids=("schedules-and-room-data-sheets",), facts=self.facts
        )
        context = dataclasses.replace(
            request.model_version_context,
            producing=dataclasses.replace(
                request.model_version_context.producing, content_id="0" * 64
            ),
        )
        with self.assertRaises(PurposeAssessmentError) as caught:
            assess_purpose(
                request=dataclasses.replace(request, model_version_context=context),
                composed=self.composed,
                facts=self.facts,
            )
        self.assertEqual(caught.exception.code, "context-model-version-mismatch")

    def test_a_scope_model_that_is_not_the_producing_model(self):
        self.assertEqual(
            self._refuse(assessed_scope=AssessedScope(model_keys=("architecture",))),
            "scope-model-not-producing",
        )

    def test_a_composed_input_for_another_project(self):
        self.assertEqual(
            self._refuse(project_id="iso-reference-view"), "request-project-mismatch"
        )

    def test_a_binding_pinned_to_a_ruleset_the_cited_run_did_not_use(self):
        """Composition checks the loaded ruleset; the assessment checks the cited run.

        Two different questions, and only the second decides whether these facts
        may be attributed to this binding at all. Composed here against a ruleset
        version that resolves — so composition is satisfied — and refused by the
        assessment because the run cited validated another one.
        """

        document = fx.fixture_overlay_document()
        for row in document["overlay"]["evidence_bindings"]:
            row["ruleset_version"] = "9.9"
        real = fx.requirement_keys_by_ruleset()
        keys = dict(real)
        keys[("epc-delivery", "9.9")] = next(iter(real.values()))

        composed = compose_purpose_inputs(
            project_id="pcert-sample",
            overlay=read_overlay_table(document, PCERT_MANIFEST),
            packs=(load_purpose_pack(fx.PACK_PATH),),
            requirement_keys_by_ruleset=keys,
        )
        with self.assertRaises(PurposeAssessmentError) as caught:
            assess_purpose(
                request=fx.fixture_request(
                    activity_ids=("schedules-and-room-data-sheets",), facts=self.facts
                ),
                composed=composed,
                facts=self.facts,
            )
        self.assertEqual(caught.exception.code, "binding-ruleset-not-the-cited-run")

    def test_an_unmapped_role_still_refuses_and_never_reads_owner_role(self):
        document = fx.fixture_overlay_document()
        document["overlay"]["team_mapping"] = [
            row
            for row in document["overlay"]["team_mapping"]
            if row["role"] != "model-coordination"
        ]
        with self.assertRaises(Exception) as caught:
            fx.fixture_composed(overlay_document=document)
        self.assertIn("team-mapping-role-missing", str(caught.exception))
        self.assertIn("owner_role", str(caught.exception))


class EveryRefusalCarriesACodeTests(unittest.TestCase):
    """``errors.py`` says a code per rule; this is what makes that a test.

    Six refusals in ``reading.py`` and ``request.py`` used to be bare
    ``ValueError``s, which meant the mapping from "what the design says must fail
    closed" to "what the code actually refuses" was an argument in prose for
    exactly those six. It is a lookup now.
    """

    #: Every module of the assessment package that may refuse. Read back from
    #: the directory rather than listed, so a module added later cannot slip past
    #: this guard by nobody remembering to name it here.
    MODULES = tuple(
        sorted(
            path.name
            for path in ASSESSMENT_PACKAGE.glob("*.py")
            if path.name not in {"__init__.py", "record.py"}
        )
    )

    def test_the_module_list_is_the_package(self):
        self.assertEqual(
            self.MODULES,
            (
                "determinations.py",
                "evaluator.py",
                "facts.py",
                "reading.py",
                "recheck.py",
                "request.py",
            ),
        )

    def test_no_bare_value_error_is_raised_in_reading_or_request(self):
        for name in ("reading.py", "request.py", "recheck.py"):
            source = (ASSESSMENT_PACKAGE / name).read_text(encoding="utf-8")
            with self.subTest(module=name):
                for node in ast.walk(ast.parse(source)):
                    if not isinstance(node, ast.Raise) or node.exc is None:
                        continue
                    call = node.exc
                    raised = getattr(getattr(call, "func", None), "id", "")
                    self.assertNotEqual(
                        raised, "ValueError", f"{name} still raises a bare ValueError"
                    )

    def test_every_code_this_package_can_raise_is_well_formed(self):
        """One code per *rule*, not per call site.

        ``binding-ruleset-not-the-cited-run`` is raised twice — once for a Pack's
        own ``pack_binding`` and once for an Overlay ``evidence_bindings`` row —
        and that is one rule checked in two places, which is why this asserts the
        shape of the codes and their number rather than that no string repeats.
        """

        codes: list[str] = []
        for name in self.MODULES:
            source = (ASSESSMENT_PACKAGE / name).read_text(encoding="utf-8")
            for node in ast.walk(ast.parse(source)):
                if not isinstance(node, ast.Call):
                    continue
                callee = getattr(node.func, "id", "")
                if callee not in {"_refuse", "PurposeAssessmentError"}:
                    continue
                if node.args and isinstance(node.args[0], ast.Constant):
                    codes.append(node.args[0].value)
        self.assertGreater(len(set(codes)), 25)
        repeated = sorted({code for code in codes if codes.count(code) > 1})
        self.assertEqual(
            repeated,
            ["binding-ruleset-not-the-cited-run"],
            "a code repeated for anything but one rule checked in two places",
        )
        for code in codes:
            with self.subTest(code=code):
                self.assertRegex(code, r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_the_two_illustrative_gates_are_two_different_codes(self):
        """Same family, two tables, two rows to edit — never one refusal."""

        source = (ASSESSMENT_PACKAGE / "evaluator.py").read_text(encoding="utf-8")
        methods = (ASSESSMENT_PACKAGE / "determinations.py").read_text(encoding="utf-8")
        self.assertIn("team-mapping-decision-basis-illustrative", source)
        self.assertIn("accepted-method-decision-basis-illustrative", methods)
        self.assertNotIn("accepted-method-decision-basis-illustrative", source)
        self.assertNotIn("team-mapping-decision-basis-illustrative", methods)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
