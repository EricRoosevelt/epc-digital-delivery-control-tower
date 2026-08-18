"""The second checker, and the modelling decision it forced.

Two things are being tested, and the second is the more important one.

The first is that the `Checker` protocol is a seam. Until now it had one
implementation, which proves nothing: any interface with one implementation is
just that implementation with extra words. `CompletenessChecker` answers a
question IDS 1.0 cannot ask — whether a set of models share anything — and it
does so without either checker knowing the other exists.

The second is what a finding points at when the finding is that something is
*not there*. `Finding` gained a fourth legal shape for it, and the tests below
pin both halves of the rule that governs it: a failure may name only its model,
and a pass may not.
"""

from __future__ import annotations

import unittest

from epc_control_tower.checkers.completeness import (
    SHARED_ACROSS_MODELS,
    CompletenessChecker,
)
from epc_control_tower.domain import FindingStatus
from helpers import LEGACY_PROJECT_ID, PROJECT_ROOT, shipped_pipeline_result

SECOND_PROJECT_ID = "iso-reference-view"
RULES = PROJECT_ROOT / "rules" / "epc-delivery"


class CapabilityTests(unittest.TestCase):
    def test_it_declares_the_flag_that_had_never_been_used(self):
        # Declared in Phase 1 for a checker that did not exist yet. A capability
        # nothing has ever set is indistinguishable from one that does not work.
        self.assertTrue(CompletenessChecker.capabilities.requires_federated_context)

    def test_it_claims_no_ifc_schema_and_no_ids_facet(self):
        # It reads the federated element register, which is schema-independent,
        # and its requirement vocabulary is its own. Claiming IDS facets it
        # cannot evaluate would let the registry route IDS work to it.
        capabilities = CompletenessChecker.capabilities
        self.assertEqual(capabilities.ifc_schemas, ())
        self.assertEqual(capabilities.facets, (SHARED_ACROSS_MODELS,))

    def test_the_registry_holds_two_checkers_that_do_not_know_each_other(self):
        from epc_control_tower.registry import default_registry
        from helpers import shipped_run_config

        registry = default_registry(shipped_run_config())
        self.assertEqual(sorted(registry.checkers), ["completeness", "ids"])

    def test_a_rule_naming_an_unknown_checker_is_refused_when_it_loads(self):
        # Not at check time, and not by being skipped. A delivery requirement
        # the pipeline quietly declines to evaluate is the failure mode this
        # whole routing arrangement exists to prevent.
        import shutil

        from epc_control_tower.rule_definitions import load_rule_definitions
        from helpers import writable_test_directory

        with writable_test_directory("rule-bad-checker") as scratch:
            target = scratch / "epc-delivery"
            shutil.copytree(RULES, target)
            (target / "R-904.toml").write_text(
                'rule_id = "R-904"\ntitle = "t"\nchecker = "clairvoyance"\n\n'
                '[[applicability]]\nfacet = "entity"\nname = "IFCWALL"\n\n'
                '[[requirements]]\nfacet = "attribute"\nname = "Name"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "clairvoyance"):
                load_rule_definitions(target)


class ShippedFixtureTests(unittest.TestCase):
    """What R-010 finds, and why both answers are true."""

    @classmethod
    def setUpClass(cls):
        bundle = shipped_pipeline_result().bundle
        keys = {
            requirement.requirement_key
            for requirement in bundle.ruleset.requirements
            if requirement.rule_id == "R-010"
        }
        cls.findings = [f for f in bundle.findings if f.requirement_key in keys]
        cls.bundle = bundle

    def test_it_is_routed_to_the_completeness_checker_not_to_ids(self):
        routed = {
            requirement.checker
            for requirement in self.bundle.ruleset.requirements
            if requirement.rule_id == "R-010"
        }
        self.assertEqual(routed, {"completeness"})

    def test_the_rule_never_reaches_the_compiled_ids_document(self):
        # A completeness rule in an IDS document would be a sentence in a
        # language that cannot hold it, and IfcTester would then evaluate a
        # specification nobody meant it to see.
        document = (PROJECT_ROOT / "ids" / "epc-delivery_v1.0.ids").read_text("utf-8")
        self.assertNotIn("R-010", document)
        self.assertIn("R-009", document)

    def test_the_pcert_models_federate_and_each_pass_names_its_witness(self):
        passing = [
            f
            for f in self.findings
            if f.project_id == LEGACY_PROJECT_ID and f.status is FindingStatus.PASS
        ]
        self.assertEqual(len(passing), 3)
        for finding in passing:
            with self.subTest(model=finding.model_key):
                # A pass always has something to point at, and it points at a
                # real element of its own model.
                self.assertTrue(finding.element_key)
                self.assertTrue(finding.element_key.startswith(f"{finding.model_key}::"))

    def test_the_reference_view_models_do_not_federate(self):
        # Three unrelated buildingSMART samples that happen to share a
        # directory. They have no setout reference in common, so as a federated
        # set they cannot be overlaid. That is a true statement about the
        # fixture, not a rule bent to produce a failure.
        failing = [
            f
            for f in self.findings
            if f.project_id == SECOND_PROJECT_ID and f.status is FindingStatus.FAIL
        ]
        self.assertEqual(len(failing), 3)

    def test_a_failure_about_an_absence_names_only_its_model(self):
        # The modelling decision, as an assertion. There is no element in these
        # models that *is* the problem — the problem is the model — so nothing
        # is invented to point at.
        for finding in self.findings:
            with self.subTest(model=finding.model_key):
                if finding.status is not FindingStatus.FAIL:
                    continue
                self.assertEqual(finding.element_key, "")
                self.assertTrue(finding.model_key)
                self.assertTrue(finding.is_applicable)
                self.assertTrue(finding.is_issue)

    def test_no_element_key_is_invented_for_a_thing_that_does_not_exist(self):
        # The alternative that was rejected, pinned so it cannot creep back in:
        # every element key any finding names resolves to a row in the register.
        registered = {element.element_key for element in self.bundle.elements}
        for finding in self.bundle.findings:
            with self.subTest(finding=finding.finding_key):
                if finding.element_key:
                    self.assertIn(finding.element_key, registered)


class GroupingTests(unittest.TestCase):
    """A failure that reaches no issue is a failure nobody is told about."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle

    def test_every_failing_finding_still_reaches_exactly_one_issue(self):
        grouped = [key for issue in self.bundle.issues for key in issue.finding_keys]
        failing = {f.finding_key for f in self.bundle.findings if f.is_issue}
        self.assertEqual(sorted(grouped), sorted(failing))
        self.assertEqual(len(grouped), len(set(grouped)))

    def test_a_model_level_issue_carries_the_blank_through(self):
        model_level = [issue for issue in self.bundle.issues if not issue.element_key]
        self.assertEqual(len(model_level), 3)
        for issue in model_level:
            with self.subTest(issue=issue.issue_key):
                self.assertTrue(issue.model_key)
                # And it is a real model of a real project, not a placeholder.
                self.assertIn(
                    issue.model_key, {m.model_key for m in self.bundle.models}
                )

    def test_an_element_issue_and_a_model_issue_cannot_collide(self):
        # Grouping keys on the element when there is one and the model when
        # there is not. Element keys always begin with their model key and a
        # separator, so no element key is ever equal to a bare model key.
        model_keys = {model.model_key for model in self.bundle.models}
        for element in self.bundle.elements:
            with self.subTest(element=element.element_key):
                self.assertNotIn(element.element_key, model_keys)


class ParameterTests(unittest.TestCase):
    """The checker reads its own parameters, as the IDS checker reads its own."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle

    def test_the_name_pattern_comes_from_the_rule_not_the_package(self):
        checker = CompletenessChecker(RULES)
        parameters = list(checker.parameters().values())
        self.assertEqual(len(parameters), 1)
        self.assertEqual(parameters[0]["name_pattern"], "^(origin|geo-reference)$")

    def test_changing_the_pattern_changes_the_answer_and_touches_no_code(self):
        # The property, demonstrated rather than asserted about the source. A
        # different project will have agreed on different names for its setout
        # references, and saying so must be an edit to a rule file. Narrowing
        # the pattern to a name nothing carries turns three passes into three
        # failures, with nothing in the package changed.
        import shutil

        from helpers import writable_test_directory

        with writable_test_directory("completeness-pattern") as scratch:
            target = scratch / "epc-delivery"
            shutil.copytree(RULES, target)
            rule = target / "R-010.toml"
            rule.write_text(
                rule.read_text(encoding="utf-8").replace(
                    '"^(origin|geo-reference)$"', '"^(no-such-reference)$"'
                ),
                encoding="utf-8",
            )
            narrowed = CompletenessChecker(target)
            self.assertEqual(
                [p["name_pattern"] for p in narrowed.parameters().values()],
                ["^(no-such-reference)$"],
            )

            from epc_control_tower.protocols import CheckContext
            from epc_control_tower.rules import load_ruleset

            ruleset = load_ruleset(target)
            wanted = [
                requirement
                for requirement in ruleset.requirements
                if requirement.rule_id == "R-010"
            ]
            bundle = self.bundle
            outcome = narrowed.check(
                CheckContext(
                    validation_run_id=bundle.run.validation_run_id,
                    as_of=bundle.run.as_of,
                    project=next(
                        p for p in bundle.projects if p.project_id == LEGACY_PROJECT_ID
                    ),
                    models=tuple(
                        m for m in bundle.models if m.project_id == LEGACY_PROJECT_ID
                    ),
                    elements=bundle.elements,
                    requirements=tuple(wanted),
                    raw_data_dir=PROJECT_ROOT / "data" / "raw",
                    reports_dir=scratch,
                )
            )

        self.assertEqual(outcome.failures, ())
        self.assertEqual(len(outcome.findings), 3)
        for finding in outcome.findings:
            with self.subTest(model=finding.model_key):
                self.assertIs(finding.status, FindingStatus.FAIL)
                self.assertEqual(finding.element_key, "")


if __name__ == "__main__":
    unittest.main()
