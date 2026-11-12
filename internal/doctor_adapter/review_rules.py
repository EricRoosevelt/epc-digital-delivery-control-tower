"""Workbench projection of the existing product rule library and IDS evaluator.

The legacy IdsChecker already compiles these definitions and calls IfcTester.
The workbench uses that same compiler/evaluator without writing its IDS/report
build products. This module owns projection and provenance, not a second rule.
"""

from __future__ import annotations

from dataclasses import replace
from importlib.metadata import version
from pathlib import Path

from epc_control_tower.checkers.ids_checker import IdsChecker
from epc_control_tower.coverage import rule_definitions_digest
from epc_control_tower.rule_definitions import compile_document, load_rule_definitions

PREDICATE_VERSION = "2"


class ProductValidation:
    """Freeze PV-001's source, then evaluate it once per opened model."""

    def __init__(self, library_path: Path):
        definition = load_rule_definitions(library_path)
        rule = next(item for item in definition.rules if item.rule_id == "PV-001")
        if rule.checker != "ids" or len(rule.requirements) != 1:
            raise ValueError(
                "Workbench PV-001 expects one IDS requirement in the source library."
            )
        self.definition = replace(definition, rules=(rule,))
        document, ruleset, expectations = compile_document(self.definition)
        requirement = ruleset.requirements[0]
        self.snapshot = {
            "rule_id": rule.rule_id,
            "predicate_version": PREDICATE_VERSION,
            "severity": rule.severity.value,
            "title": rule.title,
            "expected": expectations[requirement.requirement_key],
            "citation": rule.citation,
            "scope": "; ".join(
                f.to_string("applicability") for f in document.specifications[0].applicability
            ),
            "checker": rule.checker,
            "checker_version": IdsChecker.version,
            "engine": "ifctester",
            "engine_version": version("ifctester"),
            "ruleset_id": ruleset.ruleset_id,
            "ruleset_version": ruleset.version,
            "ruleset_digest": ruleset.normalized_digest,
            "source_definitions_digest": rule_definitions_digest(library_path),
            "requirement_key": requirement.requirement_key,
            "semantics_digest": requirement.semantics_digest,
            "declared_ifc_versions": list(rule.ifc_version),
            "pipeline_ifc_schemas": list(IdsChecker.capabilities.ifc_schemas),
            # Direct workbench inspection intentionally also permits schemas
            # outside the registry's supported pipeline plan. The actual IFC
            # schema is frozen separately on each report.models entry.
            "filters_declared_ifc_versions": False,
        }

    def evaluate(self, model) -> dict[int, str]:
        # IfcTester stores validation state on specifications/facets. Compile a
        # fresh document for each model, as the legacy checker reopens its XML.
        document, _, _ = compile_document(self.definition)
        document.validate(model)
        specification = document.specifications[0]
        passed = {entity.id() for entity in specification.requirements[0].passed_entities}
        return {
            entity.id(): "PASS" if entity.id() in passed else "FAIL"
            for entity in specification.applicable_entities
        }
