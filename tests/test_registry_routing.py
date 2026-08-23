"""Routing and plan validation.

Requirements name the checker that evaluates them, and the registry routes on
that. The point of these tests is that a plan which cannot be carried out is
rejected *before* any model is opened — a typo in a rule definition, a rule
routed to a checker that does not evaluate its facets, or a checker facing a
schema it does not speak.
"""

from __future__ import annotations

import unittest

from epc_control_tower.domain import (
    Model,
    Provenance,
    Requirement,
    Severity,
)
from epc_control_tower.protocols import CheckContext, CheckerCapabilities, CheckOutcome
from epc_control_tower.registry import Registry

SHA = "a" * 64


class FakeChecker:
    def __init__(self, checker_id="ids", version="1.0", capabilities=None, config=""):
        self.id = checker_id
        self.version = version
        self.capabilities = capabilities or CheckerCapabilities()
        self._config = config

    def config_sha256(self) -> str:
        return self._config

    def check(self, context: CheckContext) -> CheckOutcome:  # pragma: no cover
        return CheckOutcome()


class FakeExporter:
    def __init__(self, exporter_id="csv", version="1.0"):
        self.id = exporter_id
        self.version = version

    def config_sha256(self) -> str:
        return ""

    def export(self, bundle, output_root):  # pragma: no cover
        return ()


class FakePolicy:
    id = "element"

    def group(self, findings, *, validation_run_id, as_of):  # pragma: no cover
        return (), ()


def make_requirement(rule_id="R-001", checker="ids", facet_kinds=()):
    return Requirement(
        requirement_key=f"key-{rule_id}",
        rule_id=rule_id,
        requirement_id="Name",
        specification_label=f"{rule_id}: x",
        requirement_label="Name",
        checker=checker,
        facet_kinds=facet_kinds,
        severity=Severity.ERROR,
    )


def make_model(schema="IFC4", model_key="architecture"):
    return Model(
        model_key=model_key,
        model_id=model_key,
        project_id="demo",
        discipline="Architecture",
        filename="A.ifc",
        provenance=Provenance("u", "CC BY 4.0", SHA),
        ifc_schema=schema,
        ifc_project_guid="guid",
    )


class RegistrationTests(unittest.TestCase):
    def test_unknown_checker_names_what_is_registered(self):
        registry = Registry()
        registry.register_checker(FakeChecker("ids"))
        with self.assertRaisesRegex(KeyError, r"Unknown checker 'nope'.*\['ids'\]"):
            registry.checker("nope")

    def test_unknown_grouping_policy_is_rejected(self):
        with self.assertRaisesRegex(KeyError, "Unknown grouping policy"):
            Registry().grouping_policy("nope")

    def test_unknown_exporter_is_rejected(self):
        with self.assertRaisesRegex(KeyError, "Unknown exporter"):
            Registry().exporter("nope")

    def test_registering_the_same_id_twice_is_rejected(self):
        registry = Registry()
        registry.register_checker(FakeChecker("ids"))
        with self.assertRaisesRegex(ValueError, "already registered"):
            registry.register_checker(FakeChecker("ids"))

    def test_policies_and_exporters_also_reject_duplicates(self):
        registry = Registry()
        registry.register_grouping_policy(FakePolicy())
        registry.register_exporter(FakeExporter())
        with self.assertRaisesRegex(ValueError, "already registered"):
            registry.register_grouping_policy(FakePolicy())
        with self.assertRaisesRegex(ValueError, "already registered"):
            registry.register_exporter(FakeExporter())


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.registry = Registry()
        self.registry.register_checker(FakeChecker("ids"))
        self.registry.register_checker(FakeChecker("federation"))

    def test_requirements_are_grouped_by_their_checker(self):
        routed = self.registry.route(
            [
                make_requirement("R-001", checker="ids"),
                make_requirement("R-002", checker="federation"),
                make_requirement("R-003", checker="ids"),
            ]
        )
        self.assertEqual(sorted(routed), ["federation", "ids"])
        self.assertEqual([r.rule_id for r in routed["ids"]], ["R-001", "R-003"])

    def test_a_typo_in_a_rule_s_checker_fails_before_any_model_is_opened(self):
        with self.assertRaisesRegex(KeyError, "Unknown checker 'idz'"):
            self.registry.route([make_requirement(checker="idz")])

    def test_routing_is_ordered(self):
        routed = self.registry.route(
            [
                make_requirement("R-002", checker="ids"),
                make_requirement("R-001", checker="federation"),
            ]
        )
        self.assertEqual(list(routed), ["federation", "ids"])


class PlanValidationTests(unittest.TestCase):
    def test_a_checker_that_cannot_read_the_schema_is_rejected(self):
        registry = Registry()
        registry.register_checker(
            FakeChecker(capabilities=CheckerCapabilities(ifc_schemas=("IFC4",)))
        )
        routed = registry.route([make_requirement()])
        with self.assertRaisesRegex(ValueError, "does not support IFC schema"):
            registry.validate_plan(routed, [make_model(schema="IFC2X3")])

    def test_a_requirement_needing_an_unsupported_facet_is_rejected(self):
        registry = Registry()
        registry.register_checker(
            FakeChecker(capabilities=CheckerCapabilities(facets=("property", "attribute")))
        )
        routed = registry.route([make_requirement(facet_kinds=("classification",))])
        with self.assertRaisesRegex(ValueError, "needs facet.*classification"):
            registry.validate_plan(routed, [make_model()])

    def test_supported_facets_and_schemas_pass(self):
        registry = Registry()
        registry.register_checker(
            FakeChecker(
                capabilities=CheckerCapabilities(
                    facets=("property", "attribute"), ifc_schemas=("IFC4",)
                )
            )
        )
        routed = registry.route([make_requirement(facet_kinds=("property",))])
        registry.validate_plan(routed, [make_model()])

    def test_a_checker_declaring_nothing_makes_no_claim_and_is_not_second_guessed(self):
        registry = Registry()
        registry.register_checker(FakeChecker())
        routed = registry.route([make_requirement(facet_kinds=("anything",))])
        registry.validate_plan(routed, [make_model(schema="IFC4X3")])


class FingerprintTests(unittest.TestCase):
    def test_checker_fingerprints_are_sorted_and_carry_configuration(self):
        registry = Registry()
        registry.register_checker(FakeChecker("ids", "0.8.5", config=SHA))
        registry.register_checker(FakeChecker("federation", "1.0"))
        fingerprints = registry.fingerprints(["ids", "federation"])
        self.assertEqual(
            [f.component_id for f in fingerprints], ["federation", "ids"]
        )
        self.assertEqual(fingerprints[1].config_sha256, SHA)

    def test_exporter_fingerprints_are_sorted(self):
        registry = Registry()
        registry.register_exporter(FakeExporter("legacy-pbip"))
        registry.register_exporter(FakeExporter("csv"))
        self.assertEqual(
            [f.component_id for f in registry.exporter_fingerprints(["legacy-pbip", "csv"])],
            ["csv", "legacy-pbip"],
        )


if __name__ == "__main__":
    unittest.main()
