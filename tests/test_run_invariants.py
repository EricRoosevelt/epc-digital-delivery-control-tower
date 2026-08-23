"""Layer two: laws of the domain, checked on a real bundle.

These are the assertions that stay true as the data grows, and they are what
the counts taken from the shipped fixture should always have been. "There are
exactly 39 elements" fails the pipeline the day a fourth model arrives. "Every
element key is unique, every finding resolves to a requirement that exists, and
every issue's stated state folds out of its own history" keeps its meaning at
any size, and is the assertion that would actually have caught a mistake.

Each violation is provoked deliberately rather than merely described, because
an invariant nobody has ever seen fail is an invariant nobody knows is checked.
"""

from __future__ import annotations

import dataclasses
import unittest

from epc_control_tower.domain import (
    ElementGeometry,
    FindingStatus,
    IssueState,
    Severity,
    derive_lifecycle_state,
    make_element_key,
)
from epc_control_tower.validation import BundleInvariantError, validate_bundle
from helpers import shipped_pipeline_result


class ShippedBundleInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle

    def test_the_shipped_bundle_satisfies_every_invariant(self):
        validate_bundle(self.bundle)

    def test_keys_are_unique_where_they_claim_to_be(self):
        for label, values in (
            ("model_key", [m.model_key for m in self.bundle.models]),
            ("element_key", [e.element_key for e in self.bundle.elements]),
            ("finding_key", [f.finding_key for f in self.bundle.findings]),
            ("issue_key", [i.issue_key for i in self.bundle.issues]),
        ):
            with self.subTest(key=label):
                self.assertEqual(len(values), len(set(values)))

    def test_a_bare_global_id_is_not_unique_and_element_key_is(self):
        # 39 occurrences over 32 distinct GlobalIds: joining on GlobalId would
        # silently merge unrelated elements from different discipline files.
        global_ids = [element.global_id for element in self.bundle.elements]
        self.assertLess(len(set(global_ids)), len(global_ids))
        self.assertEqual(
            len({e.element_key for e in self.bundle.elements}), len(global_ids)
        )

    def test_every_element_key_agrees_with_its_own_model_and_global_id(self):
        for element in self.bundle.elements:
            with self.subTest(element=element.element_key):
                self.assertEqual(
                    element.element_key,
                    make_element_key(element.model_key, element.global_id),
                )

    def test_every_finding_resolves_to_things_that_exist(self):
        model_keys = {m.model_key for m in self.bundle.models}
        element_keys = {e.element_key for e in self.bundle.elements}
        requirement_keys = {r.requirement_key for r in self.bundle.ruleset.requirements}
        for finding in self.bundle.findings:
            with self.subTest(finding=finding.finding_key):
                self.assertIn(finding.model_key, model_keys)
                self.assertIn(finding.requirement_key, requirement_keys)
                if finding.element_key:
                    self.assertIn(finding.element_key, element_keys)

    def test_a_finding_only_takes_one_of_four_shapes(self):
        for finding in self.bundle.findings:
            with self.subTest(finding=finding.finding_key):
                if finding.status is FindingStatus.NOT_APPLICABLE:
                    self.assertFalse(finding.is_applicable)
                    self.assertFalse(finding.is_issue)
                    self.assertIs(finding.severity, Severity.INFO)
                    self.assertEqual(finding.element_key, "")
                elif finding.status is FindingStatus.PASS:
                    self.assertTrue(finding.is_applicable)
                    self.assertFalse(finding.is_issue)
                    self.assertIs(finding.severity, Severity.INFO)
                    self.assertTrue(finding.element_key)
                else:
                    self.assertTrue(finding.is_applicable)
                    self.assertTrue(finding.is_issue)
                    self.assertIsNot(finding.severity, Severity.INFO)
                    # A failure may name an element or, when it is about
                    # something that is not there, only its model. Both are
                    # legal; a failure with neither is not.
                    self.assertTrue(finding.model_key)

    def test_every_issue_state_folds_out_of_its_own_history(self):
        for issue in self.bundle.issues:
            with self.subTest(issue=issue.issue_key):
                events = self.bundle.events_for(issue.issue_key)
                self.assertTrue(events)
                self.assertIs(issue.lifecycle_state, derive_lifecycle_state(events))

    def test_geometry_may_be_sparse_but_never_dangling(self):
        element_keys = {e.element_key for e in self.bundle.elements}
        self.assertLess(len(self.bundle.geometry), len(element_keys))
        for geometry in self.bundle.geometry:
            with self.subTest(element=geometry.element_key):
                self.assertIn(geometry.element_key, element_keys)

    def test_run_identity_recomputes_from_the_inputs_it_records(self):
        # An identity nobody ever recomputes is a label that happens to look
        # like a hash.
        validate_bundle(self.bundle, recompute_identity=True)


class ProvokedViolationTests(unittest.TestCase):
    """Each invariant, actually broken."""

    def setUp(self):
        self.bundle = shipped_pipeline_result().bundle

    def _expect(self, bundle, pattern):
        with self.assertRaises(BundleInvariantError) as raised:
            validate_bundle(bundle)
        self.assertRegex(str(raised.exception), pattern)

    def test_a_duplicated_element_is_caught(self):
        broken = dataclasses.replace(
            self.bundle, elements=self.bundle.elements + (self.bundle.elements[0],)
        )
        self._expect(broken, "duplicate element_key")

    def test_a_finding_pointing_at_a_missing_element_is_caught(self):
        applicable = next(f for f in self.bundle.findings if f.element_key)
        broken = dataclasses.replace(
            self.bundle,
            elements=tuple(
                e for e in self.bundle.elements if e.element_key != applicable.element_key
            ),
        )
        self._expect(broken, "unknown element_key")

    def test_a_finding_from_another_run_is_caught(self):
        broken = dataclasses.replace(
            self.bundle,
            findings=(
                dataclasses.replace(self.bundle.findings[0], validation_run_id="other"),
            )
            + self.bundle.findings[1:],
        )
        self._expect(broken, "belongs to run")

    def test_a_lifecycle_state_that_contradicts_its_history_is_caught(self):
        broken = dataclasses.replace(
            self.bundle,
            issues=(
                dataclasses.replace(
                    self.bundle.issues[0], lifecycle_state=IssueState.CLOSED
                ),
            )
            + self.bundle.issues[1:],
        )
        self._expect(broken, "but its history derives")

    def test_an_orphaned_event_is_caught(self):
        broken = dataclasses.replace(self.bundle, issues=())
        self._expect(broken, "orphaned")

    def test_geometry_for_an_element_that_is_not_in_the_register_is_caught(self):
        broken = dataclasses.replace(
            self.bundle,
            geometry=self.bundle.geometry
            + (
                ElementGeometry(
                    element_key="ghost::0000", aabb_min=(0, 0, 0), aabb_max=(1, 1, 1)
                ),
            ),
        )
        self._expect(broken, "geometry: unknown element_key")

    def test_a_ruleset_claiming_rules_it_does_not_carry_is_caught(self):
        broken = dataclasses.replace(
            self.bundle,
            ruleset=dataclasses.replace(
                self.bundle.ruleset,
                requirements=self.bundle.ruleset.requirements[:-1],
            ),
        )
        self._expect(broken, "does not recompute from its own requirements")

    def test_a_model_the_run_identity_does_not_cover_is_caught(self):
        broken = dataclasses.replace(
            self.bundle,
            run=dataclasses.replace(self.bundle.run, model_inputs=()),
        )
        self._expect(broken, "not recorded in the run's model inputs")

    def test_every_violation_is_reported_not_just_the_first(self):
        broken = dataclasses.replace(
            self.bundle,
            elements=self.bundle.elements + (self.bundle.elements[0],),
            issues=(),
        )
        with self.assertRaises(BundleInvariantError) as raised:
            validate_bundle(broken)
        self.assertGreater(len(raised.exception.violations), 1)


if __name__ == "__main__":
    unittest.main()
