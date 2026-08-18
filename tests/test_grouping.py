"""Grouping findings into issues, and the history that opens them.

The point of interest is what is *no longer* asserted. The previous
implementation required exactly three topics of exactly two findings each, and
would have failed the pipeline rather than the data if a fourth model arrived
or a duct segment were fixed. The counts live here now, in a characterization
test, where refreshing them is a deliberate act; what the production code
enforces is the invariant, not the census.
"""

from __future__ import annotations

import unittest

from epc_control_tower.domain import (
    Finding,
    FindingStatus,
    IssueState,
    Severity,
    TopicCreatedPayload,
    derive_lifecycle_state,
)
from epc_control_tower.grouping.element import ElementGroupingPolicy
from epc_control_tower.identity import build_finding_key, build_issue_key
from epc_control_tower.registry import Registry
from epc_control_tower.stages.group import group
from helpers import shipped_pipeline_result

RUN_ID = "ids-v0.1-test"
AS_OF = "2026-08-13T00:00:00Z"


def make_finding(element_key: str, requirement_key: str, *, fails: bool = True) -> Finding:
    model_key = element_key.split("::")[0] if element_key else "demo.a"
    status = FindingStatus.FAIL if fails else FindingStatus.PASS
    return Finding(
        finding_key=build_finding_key(
            validation_run_id=RUN_ID,
            model_key=model_key,
            requirement_key=requirement_key,
            element_key=element_key,
        ),
        validation_run_id=RUN_ID,
        project_id="demo",
        model_key=model_key,
        element_key=element_key,
        requirement_key=requirement_key,
        status=status,
        severity=Severity.WARNING if fails else Severity.INFO,
        is_applicable=True,
        is_issue=fails,
    )


class ElementGroupingTests(unittest.TestCase):
    def setUp(self):
        self.policy = ElementGroupingPolicy()

    def test_findings_on_one_element_become_one_issue(self):
        findings = [
            make_finding("demo.a::E1", "req-1"),
            make_finding("demo.a::E1", "req-2"),
            make_finding("demo.a::E2", "req-1"),
        ]
        issues, events = self.policy.group(
            findings, validation_run_id=RUN_ID, as_of=AS_OF
        )
        self.assertEqual([i.element_key for i in issues], ["demo.a::E1", "demo.a::E2"])
        self.assertEqual([len(i.finding_keys) for i in issues], [2, 1])
        self.assertEqual(len(events), 2)

    def test_only_issue_bearing_findings_are_grouped(self):
        findings = [
            make_finding("demo.a::E1", "req-1", fails=False),
            make_finding("demo.a::E2", "req-1", fails=True),
        ]
        issues, _ = self.policy.group(findings, validation_run_id=RUN_ID, as_of=AS_OF)
        self.assertEqual([i.element_key for i in issues], ["demo.a::E2"])

    def test_no_issues_is_a_valid_outcome_not_an_error(self):
        # The previous implementation raised unless it found exactly six
        # failures, so a project that had fixed everything could not be run.
        issues, events = self.policy.group([], validation_run_id=RUN_ID, as_of=AS_OF)
        self.assertEqual(issues, ())
        self.assertEqual(events, ())

    def test_an_arbitrary_number_of_findings_per_element_is_accepted(self):
        findings = [make_finding("demo.a::E1", f"req-{n}") for n in range(7)]
        issues, _ = self.policy.group(findings, validation_run_id=RUN_ID, as_of=AS_OF)
        self.assertEqual(len(issues), 1)
        self.assertEqual(len(issues[0].finding_keys), 7)

    def test_the_opening_event_is_a_typed_state_transition(self):
        issues, events = self.policy.group(
            [make_finding("demo.a::E1", "req-1")], validation_run_id=RUN_ID, as_of=AS_OF
        )
        event = events[0]
        self.assertEqual(event.sequence, 1)
        self.assertIsNone(event.from_state)
        self.assertIs(event.to_state, IssueState.OPEN)
        self.assertEqual(event.event_type, "topic_created")
        self.assertIsInstance(event.typed_payload, TopicCreatedPayload)
        self.assertEqual(event.typed_payload.finding_count, 1)
        self.assertEqual(event.occurred_at, AS_OF)
        self.assertEqual(event.issue_key, issues[0].issue_key)

    def test_lifecycle_state_is_derived_from_the_history_not_asserted(self):
        issues, events = self.policy.group(
            [make_finding("demo.a::E1", "req-1")], validation_run_id=RUN_ID, as_of=AS_OF
        )
        self.assertIs(
            issues[0].lifecycle_state, derive_lifecycle_state(list(events))
        )

    def test_issue_keys_are_reproducible_from_their_inputs(self):
        issues, _ = self.policy.group(
            [make_finding("demo.a::E1", "req-1")], validation_run_id=RUN_ID, as_of=AS_OF
        )
        self.assertEqual(
            issues[0].issue_key,
            build_issue_key(
                validation_run_id=RUN_ID,
                grouping_policy="element",
                group_ref="demo.a::E1",
            ),
        )

    def test_the_policy_id_separates_issues_two_policies_grouped_alike(self):
        issue_key = build_issue_key(
            validation_run_id=RUN_ID, grouping_policy="element", group_ref="X"
        )
        other = build_issue_key(
            validation_run_id=RUN_ID, grouping_policy="requirement", group_ref="X"
        )
        self.assertNotEqual(issue_key, other)


class GroupStageTests(unittest.TestCase):
    class InconsistentPolicy:
        id = "inconsistent"

        def group(self, findings, *, validation_run_id, as_of):
            policy = ElementGroupingPolicy()
            issues, events = policy.group(
                findings, validation_run_id=validation_run_id, as_of=as_of
            )
            import dataclasses

            lying = tuple(
                dataclasses.replace(issue, lifecycle_state=IssueState.CLOSED)
                for issue in issues
            )
            return lying, events

    def test_a_state_that_does_not_fold_out_of_its_own_history_is_rejected(self):
        registry = Registry()
        registry.register_grouping_policy(self.InconsistentPolicy())
        with self.assertRaisesRegex(ValueError, "claims Closed but its history derives Open"):
            group(
                [make_finding("demo.a::E1", "req-1")],
                registry=registry,
                policy_id="inconsistent",
                validation_run_id=RUN_ID,
                as_of=AS_OF,
            )

    def test_an_unregistered_policy_is_rejected_by_name(self):
        with self.assertRaisesRegex(KeyError, "Unknown grouping policy"):
            group(
                [],
                registry=Registry(),
                policy_id="nope",
                validation_run_id=RUN_ID,
                as_of=AS_OF,
            )


class ShippedFixtureGroupingTests(unittest.TestCase):
    """Characterization: what the shipped fixture actually groups into."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle

    def test_the_shipped_fixture_produces_21_issues_over_24_findings(self):
        self.assertEqual(len(self.bundle.issues), 21)
        self.assertEqual(
            sum(len(issue.finding_keys) for issue in self.bundle.issues), 24
        )
        # Two sizes now, where the previous implementation *required* exactly
        # two findings per topic and raised otherwise. Three duct segments each
        # miss two EPC properties; the fifteen new failures are one requirement
        # each. This is the census the old code mistook for a law.
        self.assertEqual(
            sorted(len(i.finding_keys) for i in self.bundle.issues),
            [1] * 18 + [2] * 3,
        )

    def test_every_issue_is_open_with_one_opening_event(self):
        self.assertEqual(len(self.bundle.issue_events), 21)
        for issue in self.bundle.issues:
            with self.subTest(issue=issue.issue_key):
                history = self.bundle.events_for(issue.issue_key)
                self.assertEqual(len(history), 1)
                self.assertIs(issue.lifecycle_state, IssueState.OPEN)

    def test_every_grouped_finding_is_an_issue_bearing_one(self):
        grouped = {
            key for issue in self.bundle.issues for key in issue.finding_keys
        }
        failing = {f.finding_key for f in self.bundle.findings if f.is_issue}
        self.assertEqual(grouped, failing)

    def test_issues_now_span_every_model_in_both_projects(self):
        # A fact about this fixture, not a rule the code enforces — and the
        # clearest illustration of why it must not be one. The previous
        # implementation raised unless every failure was in Building-Hvac.ifc.
        # Failures are in four models across two projects now, and the only
        # thing that had to change for that to be allowed was this expectation.
        self.assertEqual(
            {issue.model_key for issue in self.bundle.issues},
            {
                "architecture",
                "hvac",
                "iso-reference-view.architecture",
                "iso-reference-view.plumbing",
                "iso-reference-view.structural",
                "structural",
            },
        )
        # Three of them name no element at all. An issue about a model that
        # carries no shared setout reference has nothing to point at inside
        # that model, and grouping had to learn that before those failures
        # could reach an issue rather than being dropped.
        self.assertEqual(
            sum(1 for issue in self.bundle.issues if not issue.element_key), 3
        )


if __name__ == "__main__":
    unittest.main()
