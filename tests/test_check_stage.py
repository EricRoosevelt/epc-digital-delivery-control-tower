"""The check stage routes and collects; it evaluates nothing itself.

Two properties are worth pinning. A checker that blows up must produce a
diagnosable result rather than an opaque traceback from the middle of a run —
while still failing the run closed, because a validation that quietly dropped
half its rules is worse than one that stopped. And the order of the findings
must be a property of the findings, not of which checker happened to be
registered first.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from epc_control_tower.domain import (
    Element,
    Finding,
    FindingStatus,
    Model,
    Project,
    Provenance,
    Requirement,
    RuleSet,
    Severity,
    make_element_key,
)
from epc_control_tower.config import ManifestModel, ProjectManifest
from epc_control_tower.protocols import (
    CheckContext,
    CheckerCapabilities,
    CheckerFailure,
    CheckOutcome,
)
from epc_control_tower.registry import Registry
from epc_control_tower.stages.check import CheckStageError, check
from epc_control_tower.identity import build_requirement_key

SHA = "b" * 64
RUN_ID = "ids-v0.1-test"


def make_requirement(rule_id: str, checker: str = "ids") -> Requirement:
    return Requirement(
        requirement_key=build_requirement_key(rule_id, "Name"),
        rule_id=rule_id,
        requirement_id="Name",
        specification_label=f"{rule_id}: demo",
        requirement_label="Name",
        checker=checker,
        facet_kinds=("attribute",),
        severity=Severity.ERROR,
    )


def make_ruleset(*requirements: Requirement) -> RuleSet:
    from epc_control_tower.identity import build_ruleset_normalized_digest

    return RuleSet(
        ruleset_id="demo",
        version="1",
        normalized_digest=build_ruleset_normalized_digest(
            ruleset_id="demo", version="1", requirements=requirements
        ),
        requirements=requirements,
    )


PROJECT = Project(project_id="demo", name="Demo")
MODEL = Model(
    model_key="demo.a",
    model_id="a",
    project_id="demo",
    discipline="Architecture",
    filename="A.ifc",
    provenance=Provenance("u", "CC BY 4.0", SHA),
    ifc_schema="IFC4",
    ifc_project_guid="guid",
)
ELEMENT = Element(
    element_key=make_element_key("demo.a", "0abc"),
    model_key="demo.a",
    global_id="0abc",
    ifc_class="IfcWall",
    name="wall",
    storey="L0",
    pset_count=1,
)
MANIFEST = ProjectManifest(
    project=PROJECT,
    models=(
        ManifestModel(
            model_id="a", discipline="Architecture", filename="A.ifc", model_key="demo.a"
        ),
    ),
    raw_data_dir=Path("."),
)


class RecordingChecker:
    capabilities = CheckerCapabilities()

    def __init__(self, checker_id: str, findings=(), failures=()):
        self.id = checker_id
        self.version = "1.0"
        self._findings = tuple(findings)
        self._failures = tuple(failures)
        self.contexts: list[CheckContext] = []

    def config_sha256(self) -> str:
        return ""

    def check(self, context: CheckContext) -> CheckOutcome:
        self.contexts.append(context)
        return CheckOutcome(findings=self._findings, failures=self._failures)


def make_finding(requirement: Requirement, element_key: str = "") -> Finding:
    from epc_control_tower.identity import build_finding_key

    status = FindingStatus.PASS if element_key else FindingStatus.NOT_APPLICABLE
    return Finding(
        finding_key=build_finding_key(
            validation_run_id=RUN_ID,
            model_key="demo.a",
            requirement_key=requirement.requirement_key,
            element_key=element_key,
        ),
        validation_run_id=RUN_ID,
        project_id="demo",
        model_key="demo.a",
        element_key=element_key,
        requirement_key=requirement.requirement_key,
        status=status,
        severity=Severity.INFO,
        is_applicable=bool(element_key),
        is_issue=False,
    )


def run_check(registry: Registry, ruleset: RuleSet):
    return check(
        registry=registry,
        ruleset=ruleset,
        manifests=[MANIFEST],
        projects=[PROJECT],
        models=[MODEL],
        elements=[ELEMENT],
        validation_run_id=RUN_ID,
        as_of="2026-08-13T00:00:00Z",
        reports_dir=Path("."),
    )


class FailureHandlingTests(unittest.TestCase):
    def test_a_checker_failure_is_reported_rather_than_raised_from_inside(self):
        failure = CheckerFailure(
            checker_id="ids",
            project_id="demo",
            model_key="demo.a",
            message="IFC content hash changed",
        )
        registry = Registry()
        registry.register_checker(RecordingChecker("ids", failures=(failure,)))

        result = run_check(registry, make_ruleset(make_requirement("R-001")))
        self.assertEqual(len(result.failures), 1)
        self.assertIn("demo/demo.a", result.failures[0].describe())

    def test_the_stage_still_fails_closed(self):
        failure = CheckerFailure(checker_id="ids", project_id="demo", message="boom")
        registry = Registry()
        registry.register_checker(RecordingChecker("ids", failures=(failure,)))

        result = run_check(registry, make_ruleset(make_requirement("R-001")))
        with self.assertRaisesRegex(CheckStageError, "1 checker failure"):
            result.raise_for_failures()

    def test_every_failure_is_reported_not_only_the_first(self):
        failures = (
            CheckerFailure(checker_id="ids", project_id="demo", message="one"),
            CheckerFailure(checker_id="ids", project_id="demo", message="two"),
        )
        registry = Registry()
        registry.register_checker(RecordingChecker("ids", failures=failures))

        result = run_check(registry, make_ruleset(make_requirement("R-001")))
        with self.assertRaises(CheckStageError) as raised:
            result.raise_for_failures()
        self.assertIn("one", str(raised.exception))
        self.assertIn("two", str(raised.exception))


class RoutingTests(unittest.TestCase):
    def test_a_rule_naming_an_unregistered_checker_stops_before_any_model_opens(self):
        registry = Registry()
        registry.register_checker(RecordingChecker("ids"))
        ruleset = make_ruleset(make_requirement("R-001", checker="typo"))
        with self.assertRaisesRegex(KeyError, "Unknown checker 'typo'"):
            run_check(registry, ruleset)

    def test_each_checker_sees_only_the_requirements_routed_to_it(self):
        ids_checker = RecordingChecker("ids")
        other = RecordingChecker("federation")
        registry = Registry()
        registry.register_checker(ids_checker)
        registry.register_checker(other)

        run_check(
            registry,
            make_ruleset(
                make_requirement("R-001", checker="ids"),
                make_requirement("R-900", checker="federation"),
            ),
        )
        self.assertEqual(
            [r.rule_id for r in ids_checker.contexts[0].requirements], ["R-001"]
        )
        self.assertEqual(
            [r.rule_id for r in other.contexts[0].requirements], ["R-900"]
        )

    def test_a_checker_sees_only_its_own_project_s_models_and_elements(self):
        checker = RecordingChecker("ids")
        registry = Registry()
        registry.register_checker(checker)
        run_check(registry, make_ruleset(make_requirement("R-001")))

        context = checker.contexts[0]
        self.assertEqual([m.model_key for m in context.models], ["demo.a"])
        self.assertEqual(context.elements_for("demo.a"), (ELEMENT,))
        self.assertEqual(context.raw_data_dir, MANIFEST.raw_data_dir)


class OrderingTests(unittest.TestCase):
    def test_finding_order_does_not_depend_on_registration_order(self):
        first = make_requirement("R-001", checker="alpha")
        second = make_requirement("R-002", checker="omega")
        ruleset = make_ruleset(first, second)
        findings = {
            "alpha": (make_finding(first, ELEMENT.element_key),),
            "omega": (make_finding(second, ELEMENT.element_key),),
        }

        orders = []
        for registration in (("alpha", "omega"), ("omega", "alpha")):
            registry = Registry()
            for checker_id in registration:
                registry.register_checker(
                    RecordingChecker(checker_id, findings=findings[checker_id])
                )
            orders.append([f.finding_key for f in run_check(registry, ruleset).findings])

        self.assertEqual(orders[0], orders[1])
        self.assertEqual(len(orders[0]), 2)


if __name__ == "__main__":
    unittest.main()
