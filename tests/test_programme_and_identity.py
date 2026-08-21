"""Programme ownership, aware time, and run-free issue identity.

The counterexamples this checkpoint exists to pin. Each varies the input
dimension that exposed a defect rather than asserting the current fixture:

- a programme is a *project's* schedule, so two projects reach the same stage on
  different dates;
- ``due`` is recomputed from that programme by the validator, so erasing the
  field cannot forge "no deadline";
- when several rules fail on one element the *earliest deadline* decides, so a
  future high-severity rule cannot hide an already-overdue lower-severity one;
- overdue is an offset-aware instant comparison and is never true for a resolved
  or closed issue;
- moving a project's programme leaves ``validation_run_id`` and every finding
  key untouched, because programme is not a validation input;
- a stage a rule uses but a project's programme omits fails the run closed.
"""

from __future__ import annotations

import dataclasses
import unittest

from epc_control_tower.domain import (
    Finding,
    FindingStatus,
    IssueEvent,
    IssueState,
    ProjectMilestone,
    Requirement,
    Severity,
    StateChangedPayload,
    ValidationRun,
    derive_is_overdue,
    parse_instant,
)
from epc_control_tower.grouping.element import ElementGroupingPolicy
from epc_control_tower.identity import build_finding_key, build_issue_event_key, build_issue_key
from epc_control_tower.validation import (
    BundleInvariantError,
    programme_coverage_gaps,
    validate_bundle,
)
from helpers import shipped_pipeline_result, shipped_run_config

AS_OF = "2026-08-13T00:00:00Z"


def _requirement(
    rule_id: str,
    *,
    severity: Severity,
    stage: str,
    key: str | None = None,
    discipline_scope: tuple[str, ...] = (),
    labels: tuple[str, ...] = (),
) -> Requirement:
    return Requirement(
        requirement_key=key or f"key-{rule_id}",
        rule_id=rule_id,
        requirement_id=f"{rule_id}.req",
        specification_label=f"{rule_id}: spec",
        requirement_label=f"{rule_id}.req",
        severity=severity,
        stage=stage,
        owner_role=f"owner-{rule_id}",
        priority=f"prio-{rule_id}",
        discipline_scope=discipline_scope,
        labels=labels,
    )


def _finding(element_key: str, requirement: Requirement, *, project_id: str) -> Finding:
    model_key = element_key.split("::")[0]
    return Finding(
        finding_key=build_finding_key(
            validation_run_id="run",
            model_key=model_key,
            requirement_key=requirement.requirement_key,
            element_key=element_key,
        ),
        validation_run_id="run",
        project_id=project_id,
        model_key=model_key,
        element_key=element_key,
        requirement_key=requirement.requirement_key,
        status=FindingStatus.FAIL,
        severity=requirement.severity,
        is_applicable=True,
        is_issue=True,
    )


class TwoProjectsSameStageDifferentDue(unittest.TestCase):
    """Same stage, two projects, two deadlines — the whole reason programme is
    project data and not a stage-keyed table on the rule set."""

    def test_each_project_dates_its_own_deadline(self):
        req = _requirement("R-1", severity=Severity.ERROR, stage="Coordination")
        findings = [
            _finding("a.m::E1", req, project_id="alpha"),
            _finding("b.m::E1", req, project_id="beta"),
        ]
        issues, _ = ElementGroupingPolicy().group(
            findings,
            validation_run_id="run",
            as_of=AS_OF,
            requirements={req.requirement_key: req},
            programmes={
                "alpha": {"Coordination": "2026-08-01T00:00:00Z"},  # past as_of
                "beta": {"Coordination": "2027-08-01T00:00:00Z"},  # future
            },
        )
        by_project = {issue.project_id: issue for issue in issues}
        self.assertEqual(by_project["alpha"].due, "2026-08-01T00:00:00Z")
        self.assertEqual(by_project["beta"].due, "2027-08-01T00:00:00Z")
        self.assertTrue(by_project["alpha"].is_overdue)
        self.assertFalse(by_project["beta"].is_overdue)


class EarliestDeadlineDecides(unittest.TestCase):
    """A future high-severity rule must not hide an overdue lower-severity one."""

    def test_the_overdue_warning_is_not_shadowed_by_a_future_error(self):
        warning = _requirement("R-W", severity=Severity.WARNING, stage="Coordination")
        error = _requirement("R-E", severity=Severity.ERROR, stage="Handover")
        findings = [
            _finding("p.m::E1", warning, project_id="proj"),
            _finding("p.m::E1", error, project_id="proj"),
        ]
        issues, _ = ElementGroupingPolicy().group(
            findings,
            validation_run_id="run",
            as_of=AS_OF,
            requirements={
                warning.requirement_key: warning,
                error.requirement_key: error,
            },
            programmes={
                "proj": {
                    "Coordination": "2026-08-01T00:00:00Z",  # past — the WARNING
                    "Handover": "2026-12-01T00:00:00Z",  # future — the ERROR
                }
            },
        )
        (issue,) = issues
        # Earliest deadline (the overdue Coordination warning) decides, not the
        # more severe but not-yet-due error.
        self.assertEqual(issue.due, "2026-08-01T00:00:00Z")
        self.assertEqual(issue.stage, "Coordination")
        self.assertTrue(issue.is_overdue)
        self.assertEqual(issue.priority, "prio-R-W")
        self.assertEqual(issue.assignee_role, "owner-R-W")
        # Labels are the union of every member rule, not only the deciding one.
        self.assertEqual(len(issue.finding_keys), 2)

    def test_all_deadline_free_falls_back_to_severity(self):
        warning = _requirement("R-W", severity=Severity.WARNING, stage="")
        error = _requirement("R-E", severity=Severity.ERROR, stage="")
        findings = [
            _finding("p.m::E1", warning, project_id="proj"),
            _finding("p.m::E1", error, project_id="proj"),
        ]
        issues, _ = ElementGroupingPolicy().group(
            findings,
            validation_run_id="run",
            as_of=AS_OF,
            requirements={
                warning.requirement_key: warning,
                error.requirement_key: error,
            },
            programmes={"proj": {}},
        )
        (issue,) = issues
        self.assertEqual(issue.due, "")
        self.assertFalse(issue.is_overdue)
        # With no deadline to protect, the worst thing wrong leads.
        self.assertEqual(issue.priority, "prio-R-E")


class OverdueSemantics(unittest.TestCase):
    """The offset-aware instant comparison and the lifecycle rule."""

    def test_z_and_plus_zero_offset_are_the_same_instant(self):
        # String comparison disagreed on these; instant comparison must not.
        self.assertFalse(
            derive_is_overdue(
                as_of="2026-08-01T00:00:00Z",
                due="2026-08-01T00:00:00+00:00",
                lifecycle_state=IssueState.OPEN,
            )
        )

    def test_an_offset_deadline_already_past_reads_as_overdue(self):
        # due 2026-08-01T01:00:00+02:00 == 2026-07-31T23:00:00Z, already past.
        self.assertTrue(
            derive_is_overdue(
                as_of="2026-08-01T00:00:00Z",
                due="2026-08-01T01:00:00+02:00",
                lifecycle_state=IssueState.OPEN,
            )
        )

    def test_resolved_and_closed_are_never_overdue(self):
        for state in (IssueState.RESOLVED, IssueState.CLOSED):
            with self.subTest(state=state):
                self.assertFalse(
                    derive_is_overdue(
                        as_of="2027-01-01T00:00:00Z",
                        due="2026-08-01T00:00:00Z",
                        lifecycle_state=state,
                    )
                )

    def test_no_deadline_is_never_overdue(self):
        self.assertFalse(
            derive_is_overdue(as_of=AS_OF, due="", lifecycle_state=IssueState.OPEN)
        )


class AwareDateTimeParser(unittest.TestCase):
    """One parser, and it refuses a naive datetime everywhere it is used."""

    def test_a_naive_datetime_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "xs:dateTime"):
            parse_instant("2026-08-01T00:00:00", "as_of")

    def test_a_naive_milestone_due_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "xs:dateTime"):
            ProjectMilestone(project_id="p", stage="Design", due="2026-07-01T00:00:00")

    def test_a_naive_as_of_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "xs:dateTime"):
            ValidationRun(
                validation_run_id="r",
                ruleset_id="rs",
                ruleset_version="0.1",
                ruleset_normalized_digest="a" * 64,
                as_of="2026-08-13T00:00:00",
            )

    def test_an_empty_milestone_due_is_allowed(self):
        # A stated stage with no deadline is legal; only a present, malformed
        # value is not.
        milestone = ProjectMilestone(project_id="p", stage="Design")
        self.assertEqual(milestone.due, "")


class CoverageFailsClosed(unittest.TestCase):
    """A stage a rule uses but a project's programme omits is a gap, not a
    silent 'no deadline'."""

    def test_the_gap_function_names_each_missing_pair(self):
        req = _requirement("R-1", severity=Severity.ERROR, stage="Coordination")
        gaps = programme_coverage_gaps(
            [req],
            ["alpha", "beta"],
            {"alpha": {"Coordination": "2026-08-01T00:00:00Z"}, "beta": {}},
        )
        self.assertEqual(gaps, ["project 'beta' has no milestone for stage 'Coordination'"])

    def test_a_present_but_empty_due_is_not_a_gap(self):
        req = _requirement("R-1", severity=Severity.ERROR, stage="Coordination")
        gaps = programme_coverage_gaps(
            [req], ["alpha"], {"alpha": {"Coordination": ""}}
        )
        self.assertEqual(gaps, [])

    def test_the_pipeline_refuses_a_manifest_missing_a_stage(self):
        # The planning-stage gate, on real inputs: drop Coordination from one
        # project's programme and the run stops before producing findings.
        from epc_control_tower.pipeline import build_bundle, load_manifests

        config = shipped_run_config()
        manifests = load_manifests(config)
        trimmed = tuple(
            dataclasses.replace(
                manifest,
                milestones=tuple(
                    milestone
                    for milestone in manifest.milestones
                    if milestone.stage != "Coordination"
                ),
            )
            if manifest.project.project_id == "pcert-sample"
            else manifest
            for manifest in manifests
        )
        with self.assertRaisesRegex(ValueError, "does not cover every rule stage"):
            build_bundle(config, manifests=trimmed)


class ProgrammeIsNotAValidationInput(unittest.TestCase):
    """Moving a project's programme changes issues, never identity."""

    @classmethod
    def setUpClass(cls):
        from epc_control_tower.pipeline import build_bundle, load_manifests

        cls.shipped = shipped_pipeline_result().bundle
        config = shipped_run_config()
        manifests = load_manifests(config)
        # Push pcert's Coordination deadline far into the future, changing which
        # issues are overdue while touching nothing a finding depends on.
        moved = tuple(
            dataclasses.replace(
                manifest,
                milestones=tuple(
                    dataclasses.replace(milestone, due="2099-01-01T00:00:00Z")
                    if milestone.stage == "Coordination"
                    else milestone
                    for milestone in manifest.milestones
                ),
            )
            if manifest.project.project_id == "pcert-sample"
            else manifest
            for manifest in manifests
        )
        cls.moved = build_bundle(config, manifests=moved).bundle

    def test_validation_run_id_and_finding_keys_do_not_move(self):
        self.assertEqual(
            self.shipped.run.validation_run_id, self.moved.run.validation_run_id
        )
        self.assertEqual(
            {f.finding_key for f in self.shipped.findings},
            {f.finding_key for f in self.moved.findings},
        )
        self.assertEqual(
            self.shipped.ruleset.normalized_digest,
            self.moved.ruleset.normalized_digest,
        )

    def test_but_the_programme_actually_took_effect(self):
        # Same subjects, but the moved programme un-overdues pcert's Coordination
        # issues — proof the change was real and not a no-op.
        def overdue_subjects(bundle):
            return {
                issue.group_ref
                for issue in bundle.issues
                if issue.project_id == "pcert-sample" and issue.is_overdue
            }

        self.assertNotEqual(overdue_subjects(self.shipped), overdue_subjects(self.moved))


class DueCannotBeForged(unittest.TestCase):
    """The validator recomputes ``due`` from the programme, so erasing the field
    does not forge a missing deadline; and it recomputes ``issue_key`` from the
    persisted ``group_ref``."""

    def setUp(self):
        self.bundle = shipped_pipeline_result().bundle

    def test_erasing_due_and_clearing_overdue_is_rejected(self):
        victim = next(issue for issue in self.bundle.issues if issue.is_overdue)
        forged = tuple(
            dataclasses.replace(issue, due="", is_overdue=False)
            if issue.issue_key == victim.issue_key
            else issue
            for issue in self.bundle.issues
        )
        with self.assertRaises(BundleInvariantError) as caught:
            validate_bundle(dataclasses.replace(self.bundle, issues=forged))
        self.assertRegex(
            "\n".join(caught.exception.violations), "does not match its programme"
        )

    def test_a_forged_group_ref_no_longer_keys_its_issue(self):
        victim = self.bundle.issues[0]
        forged = tuple(
            dataclasses.replace(issue, group_ref="tampered::subject")
            if issue.issue_key == victim.issue_key
            else issue
            for issue in self.bundle.issues
        )
        with self.assertRaises(BundleInvariantError) as caught:
            validate_bundle(dataclasses.replace(self.bundle, issues=forged))
        self.assertRegex(
            "\n".join(caught.exception.violations), "does not recompute from its"
        )


class IllegalDateTimeLexicalForms(unittest.TestCase):
    """The lexical space of ``xs:dateTime``, policed — ``fromisoformat`` alone
    is too lenient to trust with what reaches a BCF ``xs:dateTime`` field."""

    def test_lenient_and_invalid_spellings_are_all_rejected(self):
        for bad in (
            "2026-08-01 00:00:00+00:00",  # space instead of T
            "2026-08-01T00:00:00",  # no timezone
            "2026-08-01",  # date only
            "2026-08-01T00:00Z",  # missing seconds
            "2026-08-01T00:00:00+0000",  # offset without a colon
            "2026-08-01T00:00:00+00",  # bare-hour offset
            "20260801T000000Z",  # basic format, no separators
            "not-a-date",
        ):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    parse_instant(bad, "value")

    def test_an_out_of_range_field_is_rejected(self):
        # The pattern admits the shape; the calendar rejects the value.
        for bad in ("2026-13-01T00:00:00Z", "2026-08-32T00:00:00Z", "2026-08-01T25:00:00Z"):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    parse_instant(bad, "value")

    def test_a_timezone_offset_beyond_14_00_is_rejected(self):
        # xs:dateTime bounds the timezone at ±14:00; Python's datetime would
        # otherwise accept anything under ±24:00.
        for bad in (
            "2026-08-01T00:00:00+14:01",
            "2026-08-01T00:00:00+15:00",
            "2026-08-01T00:00:00+23:59",
            "2026-08-01T00:00:00-14:01",
        ):
            with self.subTest(value=bad):
                with self.assertRaisesRegex(ValueError, "out of range"):
                    parse_instant(bad, "value")

    def test_a_well_formed_offset_and_z_both_pass(self):
        parse_instant("2026-08-01T00:00:00Z", "value")
        parse_instant("2026-08-01T00:00:00.5+02:00", "value")
        # The boundary itself is legal, both signs.
        parse_instant("2026-08-01T00:00:00+14:00", "value")
        parse_instant("2026-08-01T00:00:00-14:00", "value")


class NaiveIssueEventIsRejected(unittest.TestCase):
    def test_a_naive_occurred_at_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "xs:dateTime"):
            IssueEvent(
                event_key="e",
                issue_key="i",
                sequence=1,
                occurred_at="2026-08-13T00:00:00",  # no offset
                event_type="topic_created",
                from_state=None,
                to_state=IssueState.OPEN,
                actor_role="role",
                payload_version=1,
                typed_payload=StateChangedPayload(note="x"),
            )


class ProgrammeWellFormedness(unittest.TestCase):
    """Duplicate, unknown-project, and typo'd programme rows, via the validator
    on a real bundle."""

    def setUp(self):
        self.bundle = shipped_pipeline_result().bundle

    def _expect(self, project_milestones, pattern):
        broken = dataclasses.replace(self.bundle, project_milestones=project_milestones)
        with self.assertRaises(BundleInvariantError) as caught:
            validate_bundle(broken)
        self.assertRegex("\n".join(caught.exception.violations), pattern)

    def test_a_duplicate_project_stage_is_rejected(self):
        dup = self.bundle.project_milestones + (
            ProjectMilestone(
                project_id="pcert-sample", stage="Design", due="2020-01-01T00:00:00Z"
            ),
        )
        self._expect(dup, "duplicate milestone for project 'pcert-sample' stage 'Design'")

    def test_a_milestone_for_an_unknown_project_is_rejected(self):
        stray = self.bundle.project_milestones + (
            ProjectMilestone(project_id="ghost", stage="Design", due=""),
        )
        self._expect(stray, "unknown project_id 'ghost'")

    def test_a_stage_typo_is_a_coverage_gap(self):
        # A programme that spells a stage 'Coordinaton' does not cover the rules
        # whose stage is 'Coordination'; the gap is named, not masked.
        typoed = tuple(
            ProjectMilestone(
                project_id=m.project_id,
                stage="Coordinaton" if m.stage == "Coordination" else m.stage,
                due=m.due,
            )
            for m in self.bundle.project_milestones
        )
        self._expect(typoed, "has no milestone for stage 'Coordination'")


class PreIngestCoverageGate(unittest.TestCase):
    """Coverage fails before any IFC file is opened."""

    def test_a_missing_stage_is_caught_before_a_broken_model_is_read(self):
        # The manifest points a model at a file that does not exist *and* omits a
        # required stage. If coverage runs first the error names the stage; if
        # ingest ran first it would be a FileNotFoundError about the model. The
        # coverage message is what proves the ordering.
        from epc_control_tower.pipeline import build_bundle, load_manifests

        config = shipped_run_config()
        manifests = load_manifests(config)
        broken = tuple(
            dataclasses.replace(
                manifest,
                milestones=tuple(
                    m for m in manifest.milestones if m.stage != "Coordination"
                ),
                models=(
                    dataclasses.replace(
                        manifest.models[0],
                        filename="does-not-exist.ifc",
                        content_sha256="",
                    ),
                )
                + manifest.models[1:],
            )
            if manifest.project.project_id == "pcert-sample"
            else manifest
            for manifest in manifests
        )
        with self.assertRaises(ValueError) as caught:
            build_bundle(config, manifests=broken)
        self.assertIn("does not cover every rule stage", str(caught.exception))
        self.assertNotIn("does-not-exist.ifc", str(caught.exception))


class DeadlineTieBreaks(unittest.TestCase):
    """When two rules share the earliest instant, severity then key decide; and
    a missing programme is never read as 'no deadline'."""

    def _decide_same_instant(self, a: Requirement, b: Requirement) -> str:
        due = "2026-08-01T00:00:00Z"
        findings = [
            _finding("p.m::E1", a, project_id="proj"),
            _finding("p.m::E1", b, project_id="proj"),
        ]
        issues, _ = ElementGroupingPolicy().group(
            findings,
            validation_run_id="run",
            as_of=AS_OF,
            requirements={a.requirement_key: a, b.requirement_key: b},
            programmes={"proj": {"Coordination": due}},
        )
        return issues[0].priority

    def test_at_the_same_instant_severity_outranks_the_key(self):
        # The ERROR carries the *higher* key, so if the key won it would lose.
        # It wins, which isolates severity as the first tiebreaker.
        warning = _requirement(
            "R-W", severity=Severity.WARNING, stage="Coordination", key="key-a"
        )
        error = _requirement(
            "R-E", severity=Severity.ERROR, stage="Coordination", key="key-z"
        )
        self.assertEqual(self._decide_same_instant(warning, error), "prio-R-E")

    def test_at_the_same_instant_and_severity_the_lower_key_decides(self):
        # Identical severity removes the first tiebreaker, so the requirement key
        # alone decides — the lower one wins.
        low = _requirement(
            "R-A", severity=Severity.ERROR, stage="Coordination", key="key-a"
        )
        high = _requirement(
            "R-B", severity=Severity.ERROR, stage="Coordination", key="key-b"
        )
        self.assertEqual(self._decide_same_instant(high, low), "prio-R-A")

    def test_a_missing_project_programme_with_a_dated_stage_fails_closed(self):
        req = _requirement("R-1", severity=Severity.ERROR, stage="Coordination")
        findings = [_finding("p.m::E1", req, project_id="proj")]
        with self.assertRaisesRegex(ValueError, "no milestone for stage 'Coordination'"):
            ElementGroupingPolicy().group(
                findings,
                validation_run_id="run",
                as_of=AS_OF,
                requirements={req.requirement_key: req},
                programmes={},  # no programme for 'proj' — a non-empty stage is a gap
            )


class LabelsAreAUnion(unittest.TestCase):
    def test_an_issue_carries_every_member_rules_labels(self):
        a = _requirement(
            "R-A",
            severity=Severity.WARNING,
            stage="Coordination",
            key="key-a",
            discipline_scope=("HVAC",),
            labels=("IDS",),
        )
        b = _requirement(
            "R-B",
            severity=Severity.ERROR,
            stage="Coordination",
            key="key-b",
            discipline_scope=("Structural",),
            labels=("Handover",),
        )
        findings = [
            _finding("p.m::E1", a, project_id="proj"),
            _finding("p.m::E1", b, project_id="proj"),
        ]
        issues, _ = ElementGroupingPolicy().group(
            findings,
            validation_run_id="run",
            as_of=AS_OF,
            requirements={a.requirement_key: a, b.requirement_key: b},
            programmes={"proj": {"Coordination": "2026-08-01T00:00:00Z"}},
        )
        # Every member rule's disciplines and labels, in a fixed order: by
        # requirement key ascending (key-a before key-b), then each rule's
        # discipline_scope before its labels, first appearance kept. The exact
        # tuple pins that this is deterministic, not merely a set.
        self.assertEqual(
            issues[0].labels, ("HVAC", "IDS", "Structural", "Handover")
        )


class ReopenAndCustomGroupRef(unittest.TestCase):
    """Overdue follows the *current* lifecycle state, and ``group_ref`` need not
    be an element key."""

    def test_a_reopened_issue_is_overdue_again(self):
        past_due = "2026-08-01T00:00:00Z"
        # Resolved: the work is done, not overdue.
        self.assertFalse(
            derive_is_overdue(as_of=AS_OF, due=past_due, lifecycle_state=IssueState.RESOLVED)
        )
        # Reopened to Open: the past deadline is live again.
        self.assertTrue(
            derive_is_overdue(as_of=AS_OF, due=past_due, lifecycle_state=IssueState.OPEN)
        )

    def test_the_validator_recomputes_overdue_from_a_reopened_history(self):
        # A shipped overdue issue, given a Resolved→Open reopen history: its
        # state folds back to Open, so is_overdue must stay True and validate.
        bundle = shipped_pipeline_result().bundle
        victim = next(i for i in bundle.issues if i.is_overdue)
        base = bundle.events_for(victim.issue_key)[0]
        reopen = (
            base,
            IssueEvent(
                event_key=build_issue_event_key(
                    issue_key=victim.issue_key, sequence=2, event_type="state_changed"
                ),
                issue_key=victim.issue_key,
                sequence=2,
                occurred_at=bundle.run.as_of,
                event_type="state_changed",
                from_state=IssueState.OPEN,
                to_state=IssueState.RESOLVED,
                actor_role="model-coordination",
                payload_version=1,
                typed_payload=StateChangedPayload(note="resolved"),
            ),
            IssueEvent(
                event_key=build_issue_event_key(
                    issue_key=victim.issue_key, sequence=3, event_type="state_changed"
                ),
                issue_key=victim.issue_key,
                sequence=3,
                occurred_at=bundle.run.as_of,
                event_type="state_changed",
                from_state=IssueState.RESOLVED,
                to_state=IssueState.OPEN,
                actor_role="model-coordination",
                payload_version=1,
                typed_payload=StateChangedPayload(note="reopened"),
            ),
        )
        other_events = tuple(
            e for e in bundle.issue_events if e.issue_key != victim.issue_key
        )
        rebuilt = dataclasses.replace(
            bundle, issue_events=other_events + reopen
        )
        # Still Open, still overdue — the derivation follows the current state.
        validate_bundle(rebuilt)

    def test_a_custom_non_element_group_ref_is_accepted_when_it_keys_the_issue(self):
        # group_ref is the policy's business; the validator only asks that the
        # issue key recompute from it. Re-key one issue on a requirement-style
        # group_ref and it validates.
        bundle = shipped_pipeline_result().bundle
        victim = bundle.issues[0]
        custom_ref = f"requirement::{victim.model_key}"
        new_key = build_issue_key(
            validation_run_id=victim.validation_run_id,
            grouping_policy=victim.grouping_policy,
            group_ref=custom_ref,
        )
        rekeyed_issue = dataclasses.replace(
            victim, group_ref=custom_ref, issue_key=new_key
        )
        base_event = bundle.events_for(victim.issue_key)[0]
        rekeyed_event = dataclasses.replace(
            base_event,
            issue_key=new_key,
            event_key=build_issue_event_key(
                issue_key=new_key, sequence=1, event_type=base_event.event_type
            ),
        )
        issues = (rekeyed_issue,) + bundle.issues[1:]
        events = (rekeyed_event,) + tuple(
            e for e in bundle.issue_events if e.issue_key != victim.issue_key
        )
        validate_bundle(dataclasses.replace(bundle, issues=issues, issue_events=events))


if __name__ == "__main__":
    unittest.main()
