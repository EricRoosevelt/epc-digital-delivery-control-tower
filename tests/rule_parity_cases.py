"""Public synthetic cases run through both pre-existing PV-001 entry points.

Run directly to print a reproducible observation summary. All legacy compilation
and reporting happens outside the checkout, using a copy of the rule library.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from importlib.metadata import version
import json
import hashlib
from pathlib import Path
import shutil
import sys

import ifcopenshell

from epc_control_tower.config import load_project_manifests
from epc_control_tower.protocols import CheckContext
from epc_control_tower.registry import default_registry
from epc_control_tower.rules import load_ruleset
from epc_control_tower.stages.check import check
from epc_control_tower.stages.ingest import ingest
from epc_control_tower.stages.inventory import inventory
from helpers import PROJECT_ROOT, outside_repository_directory, shipped_run_config
from internal.doctor_adapter.review import ReviewStore


@dataclass(frozen=True)
class Case:
    name: str
    predefined: str | None = "NOTDEFINED"
    object_type: str | None = None
    assigned: bool = False
    type_predefined: str | None = None
    element_type: str | None = None
    ifc_class: str = "IfcAirTerminal"
    schema: str = "IFC4"
    malformed: bool = False
    empty: bool = False


CASES = [
    *[
        Case("enum-" + value.lower(), predefined=value)
        for value in ("DIFFUSER", "GRILLE", "LOUVRE", "REGISTER")
    ],
    Case("occurrence-notdefined"),
    Case("occurrence-unset", predefined=None),
    Case("occurrence-userdefined-supported", predefined="USERDEFINED", object_type="GRILLE"),
    Case("occurrence-userdefined-custom", predefined="USERDEFINED", object_type="SPECIAL"),
    Case("occurrence-userdefined-blank", predefined="USERDEFINED", object_type=""),
    Case("occurrence-userdefined-missing", predefined="USERDEFINED"),
    Case("occurrence-userdefined-case", predefined="USERDEFINED", object_type="grille"),
    Case("occurrence-userdefined-padded", predefined="USERDEFINED", object_type=" GRILLE "),
    Case("unset-enum-free-text", predefined=None, object_type="LOUVRE"),
    Case("type-only", predefined=None, assigned=True, type_predefined="LOUVRE"),
    Case("type-over-notdefined", assigned=True, type_predefined="LOUVRE"),
    Case(
        "type-notdefined-fallback",
        predefined="LOUVRE",
        assigned=True,
        type_predefined="NOTDEFINED",
    ),
    Case(
        "type-custom-overrides-instance",
        predefined="LOUVRE",
        assigned=True,
        type_predefined="USERDEFINED",
        element_type="SPECIAL",
    ),
    Case(
        "type-userdefined-missing-fallback",
        predefined="LOUVRE",
        assigned=True,
        type_predefined="USERDEFINED",
    ),
    Case(
        "type-userdefined-blank-fallback",
        predefined="LOUVRE",
        assigned=True,
        type_predefined="USERDEFINED",
        element_type="",
    ),
    Case(
        "type-userdefined-whitespace",
        predefined="LOUVRE",
        assigned=True,
        type_predefined="USERDEFINED",
        element_type=" ",
    ),
    Case(
        "type-userdefined-supported",
        assigned=True,
        type_predefined="USERDEFINED",
        element_type="GRILLE",
    ),
    Case("type-unset-free-text", assigned=True, element_type="GRILLE"),
    Case("type-unset-fallback", predefined="REGISTER", assigned=True),
    Case(
        "type-enum-overrides-instance-text",
        predefined="USERDEFINED",
        object_type="SPECIAL",
        assigned=True,
        type_predefined="DIFFUSER",
    ),
    Case("malformed-enum", malformed=True),
    Case("malformed-enum-with-object-text", malformed=True, object_type="LOUVRE"),
    Case("wall-subclass-not-applicable", ifc_class="IfcWallStandardCase"),
    Case(
        "base-class-not-applicable",
        ifc_class="IfcFlowTerminal",
        assigned=True,
        type_predefined="DIFFUSER",
    ),
    Case(
        "sibling-class-not-applicable",
        ifc_class="IfcAirTerminalBox",
        assigned=True,
        type_predefined="DIFFUSER",
    ),
    Case("zero-elements", empty=True),
    Case(
        "ifc2x3-type-mapping",
        ifc_class="IfcFlowTerminal",
        schema="IFC2X3",
        assigned=True,
        type_predefined="DIFFUSER",
    ),
    Case(
        "ifc2x3-other-class-type-mapping",
        ifc_class="IfcFurnishingElement",
        schema="IFC2X3",
        assigned=True,
        type_predefined="DIFFUSER",
    ),
    Case("ifc2x3-no-type", ifc_class="IfcFlowTerminal", schema="IFC2X3"),
    Case("ifc4x3-terminal", schema="IFC4X3", predefined="DIFFUSER"),
]


def model_bytes(case: Case):
    model = ifcopenshell.file(schema=case.schema)
    guid = ifcopenshell.guid.compress("0123456789abcdef0123456789abcdef")
    model.create_entity(
        "IfcProject", GlobalId=ifcopenshell.guid.compress("1123456789abcdef0123456789abcdef")
    )
    if case.empty:
        return model.to_string().encode(), None
    entity = model.create_entity(
        case.ifc_class, GlobalId=guid, Name=case.name, ObjectType=case.object_type
    )
    if hasattr(entity, "PredefinedType"):
        entity.PredefinedType = case.predefined
    if case.assigned:
        assigned = model.create_entity(
            "IfcAirTerminalType",
            GlobalId=ifcopenshell.guid.new(),
            ElementType=case.element_type,
        )
        if case.type_predefined is not None:
            assigned.PredefinedType = case.type_predefined
        model.create_entity(
            "IfcRelDefinesByType",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[entity],
            RelatingType=assigned,
        )
    text = model.to_string()
    if case.malformed:
        text = "\n".join(
            line.replace(".NOTDEFINED.", ".BOGUS.") if guid in line else line
            for line in text.splitlines()
        )
    return text.encode(), guid


def measure(case: Case):
    body, guid = model_bytes(case)
    with outside_repository_directory("rule-parity") as scratch:
        rules = scratch / "rules/product-validation"
        shutil.copytree(PROJECT_ROOT / "rules/product-validation", rules)
        project = scratch / "projects/case"
        project.mkdir(parents=True)
        (project / "case.ifc").write_bytes(body)
        (project / "project.toml").write_text(
            '[project]\nproject_id="case"\nname="Public synthetic case"\n'
            '[[models]]\nmodel_id="mep"\ndiscipline="MEP"\nfilename="case.ifc"\n',
            encoding="utf-8",
        )
        config = replace(
            shipped_run_config(), ruleset_path=rules, reports_dir=scratch / "reports"
        )
        registry = default_registry(config)
        ruleset = load_ruleset(rules)
        manifests = load_project_manifests([project / "project.toml"], repository_root=scratch)
        ingested = ingest(manifests)
        elements = inventory(ingested.models, {"case.mep": project / "case.ifc"})
        args = dict(
            registry=registry,
            ruleset=ruleset,
            manifests=manifests,
            projects=ingested.projects,
            models=ingested.models,
            elements=elements,
            validation_run_id="public-rule-parity",
            as_of=config.as_of,
            reports_dir=config.reports_dir,
        )
        try:
            checked = check(**args)
            pipeline_status = "executed"
        except ValueError as error:
            if "does not support IFC schema" not in str(error):
                raise
            pipeline_status = "unsupported_schema"
            # Characterize the underlying real checker separately, without
            # pretending that bypassing the registry makes the schema supported.
            checked = registry.checker("ids").check(
                CheckContext(
                    validation_run_id="public-rule-parity",
                    as_of=config.as_of,
                    project=ingested.projects[0],
                    models=tuple(ingested.models),
                    elements=tuple(elements),
                    requirements=ruleset.requirements,
                    raw_data_dir=project,
                    reports_dir=config.reports_dir,
                )
            )
        if checked.failures:
            raise AssertionError(checked.failures)
        legacy = [
            {"status": f.status.value, "actual": f.actual, "element_scope": bool(f.element_key)}
            for f in checked.findings
        ]
        review = ReviewStore().create("case.ifc", body)
        runtime = [f for f in review["findings"] if f["rule_id"] == "PV-001"]
        assert len(runtime) == (0 if case.empty else 1)
        return {
            "case": case.name,
            "schema": ingested.models[0].ifc_schema,
            "pipeline": pipeline_status,
            "legacy": legacy,
            "runtime": [{"status": f["status"], "actual": f["actual"]} for f in runtime],
        }


def summary():
    measured = {
        "format_version": 1,
        "baseline_commit": "996fc7d",
        "ifctester_version": version("ifctester"),
        "cases": [measure(case) for case in CASES],
        "implementation": "Shared rule compiler and IfcTester validation; runtime PV-001 v2",
        "runtime_rules": ReviewStore().create("case.ifc", model_bytes(CASES[0])[0])["rules"],
    }
    baseline = json.loads(
        (PROJECT_ROOT / "docs/handoffs/rule-parity-baseline.json").read_text(encoding="utf-8")
    )
    old = {item["case"]: item for item in baseline["cases"]}
    measured["status_changes_from_original_runtime"] = [
        {"case": case["case"], "before": old[case["case"]]["runtime"], "after": case["runtime"]}
        for case in measured["cases"]
        if case["runtime"] != old[case["case"]]["runtime"]
    ]
    measured["legacy_common_schema_status_mismatches"] = [
        case["case"]
        for case in measured["cases"]
        if case["pipeline"] == "executed"
        and case["runtime"]
        and (case["legacy"][0]["status"], case["runtime"][0]["status"])
        not in (("PASS", "PASS"), ("FAIL", "FAIL"), ("N/A", "NOT_APPLICABLE"))
    ]
    contract = json.loads(
        (PROJECT_ROOT / "docs/contracts/contract-1.7.json").read_text(encoding="utf-8")
    )
    mismatches = [
        name
        for name, digest in contract["artifacts"].items()
        if hashlib.sha256((PROJECT_ROOT / name).read_bytes()).hexdigest() != digest
    ]
    measured["published_artifacts"] = {
        "contract_version": "1.7",
        "checked": len(contract["artifacts"]),
        "mismatches": mismatches,
    }
    return measured


if __name__ == "__main__":
    encoded = json.dumps(summary(), ensure_ascii=False, indent=2) + "\n"
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(encoded, encoding="utf-8", newline="\n")
    else:
        print(encoded)
