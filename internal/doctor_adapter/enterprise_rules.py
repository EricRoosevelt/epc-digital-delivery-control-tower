"""Enterprise information checks: native TOML/IfcTester, without geometry work."""

from __future__ import annotations

from copy import deepcopy
import hashlib

import ifcopenshell
import ifcopenshell.util.element

from epc_control_tower.checkers.ids_checker import IdsChecker, requirement_label
from epc_control_tower.identity import build_requirement_key
from epc_control_tower.rule_definitions import compile_document

from .enterprise_package import EnterprisePackage, digest, parse_package
from .review import GUID_PATTERN, _open_step

__all__ = ["EnterprisePackage", "parse_package", "evaluate_rules"]


def _ancestors(model, entity):
    declaration = ifcopenshell.ifcopenshell_wrapper.schema_by_name(
        model.schema
    ).declaration_by_name(entity.is_a())
    classes = []
    while declaration is not None:
        classes.append(declaration.name())
        declaration = declaration.supertype()
    return classes


def _actual(entity, facet):
    """Readable source evidence, never a second predicate evaluator."""
    kind = type(facet).__name__
    if kind == "Entity":
        return (
            entity.is_a()
            + " / "
            + str(ifcopenshell.util.element.get_predefined_type(entity) or "Not declared")
        )
    if kind == "Attribute" and isinstance(facet.name, str):
        value = getattr(entity, facet.name, None)
        return str(value) if value is not None else "Not declared"
    if (
        kind == "Property"
        and isinstance(facet.propertySet, str)
        and isinstance(facet.baseName, str)
    ):
        value = ifcopenshell.util.element.get_pset(entity, facet.propertySet, facet.baseName)
        return str(value) if value is not None else "Not declared"
    return "See native checker reason and declared requirement."


def evaluate_rules(
    package: EnterprisePackage, body: bytes, report: dict, model_id: str
) -> dict:
    """Run in the supervised child against exact source; never call tessellation.

    A new document is compiled per execution, since native specifications retain
    mutable validation state. Scope belongs to the purpose observation, not a
    truncated IFC that could change property inheritance or relationship checks.
    """
    if not isinstance(model_id, str) or not model_id or "::" in model_id:
        raise ValueError("A stable project model slot is required.")
    source_sha = hashlib.sha256(body).hexdigest()
    if source_sha != report.get("source", {}).get("sha256"):
        raise ValueError("The source IFC hash does not match the saved model revision.")
    try:
        model = _open_step(body)
        roots = model.by_type("IfcRoot")
    except Exception as error:
        raise ValueError("The source could not be parsed as an IFC STEP model.") from error
    checks = deepcopy(list(package.checks))
    schema_supported = model.schema in IdsChecker.capabilities.ifc_schemas
    declared = {r.rule_id: r.ifc_version for r in package.definition.rules}
    for check in checks:
        if check["support"] == "supported" and (
            not schema_supported or model.schema not in declared[check["rule_id"]]
        ):
            check["support"] = "unsupported"
            check["unsupported_reasons"] = [
                f"IFC schema {model.schema} is not supported by this rule/checker combination."
            ]
    executable = {c["requirement_key"] for c in checks if c["support"] == "supported"}
    document, _, _ = compile_document(package.definition)
    # Keep unsupported schemas out of the engine. They produce coverage gaps,
    # never a successful check or N/A disguised as an execution result.
    document.specifications = [
        s
        for s in document.specifications
        if any(
            build_requirement_key(s.identifier, requirement_label(f)) in executable
            for f in s.requirements
        )
    ]
    if document.specifications:
        document.validate(model)
    from collections import Counter

    counts = Counter(str(getattr(e, "GlobalId", "") or "") for e in roots)
    review_by_step = {e.get("step_id"): e for e in report.get("elements", [])}
    entities = {e.id(): e for e in roots}
    for specification in document.specifications:
        entities.update({e.id(): e for e in specification.applicable_entities})
    elements, by_step = [], {}
    for step_id, entity in sorted(entities.items()):
        guid = str(getattr(entity, "GlobalId", "") or "")
        comparable = bool(GUID_PATTERN.fullmatch(guid)) and counts[guid] == 1
        key = model_id + "::" + (guid or "missing-global-id")
        if not comparable:
            key += f"::step-{step_id}"
        reviewed = review_by_step.get(step_id, {})
        link = (
            reviewed.get("element_key", "")
            if (
                reviewed.get("global_id") == guid and reviewed.get("ifc_class") == entity.is_a()
            )
            else ""
        )
        row = {
            "element_key": key,
            "review_element_key": link,
            "model_key": model_id,
            "global_id": guid,
            "identity_comparable": comparable,
            "ifc_class": entity.is_a(),
            "class_ancestors": _ancestors(model, entity),
            "step_id": step_id,
            "name": str(getattr(entity, "Name", "") or ""),
        }
        elements.append(row)
        by_step[step_id] = row
    findings, coverage = [], []
    by_check = {c["requirement_key"]: c for c in checks}
    native_results = {}
    for specification in document.specifications:
        for facet in specification.requirements:
            key = build_requirement_key(specification.identifier, requirement_label(facet))
            native_results[key] = (specification, facet)
    for check in checks:
        row = {
            "requirement_key": check["requirement_key"],
            "rule_id": check["rule_id"],
            "support": check["support"],
            "reason": "; ".join(check["unsupported_reasons"]),
            "applicable": 0,
            "evaluated": 0,
            "passed": 0,
            "failed": 0,
            "not_applicable": 0,
        }
        coverage.append(row)
        if check["support"] != "supported":
            continue
        specification, facet = native_results[check["requirement_key"]]
        applicable = specification.applicable_entities
        row["applicable"] = len(applicable)
        if not applicable:
            # Native TOML compiler currently emits optional applicability; keep
            # this model-level observation, never invent an absent object.
            required = specification.minOccurs != 0
            status = "FAIL" if required else "N/A"
            reason = (
                "No matching elements exist for required applicability."
                if required
                else "No applicable elements exist in this model."
            )
            findings.append(_finding(check, model_id, source_sha, "", status, "", reason))
            row["failed" if required else "not_applicable"] = 1
            continue
        passed = {e.id() for e in facet.passed_entities}
        failures = {f["element"].id(): f["reason"] for f in facet.failures}
        if passed & failures.keys() or passed | failures.keys() != {e.id() for e in applicable}:
            raise ValueError("Native checker entity outcomes do not reconcile.")
        for entity in sorted(applicable, key=lambda e: e.id()):
            status = "PASS" if entity.id() in passed else "FAIL"
            reason = (
                "Requirement satisfied." if status == "PASS" else str(failures[entity.id()])
            )
            findings.append(
                _finding(
                    by_check[check["requirement_key"]],
                    model_id,
                    source_sha,
                    by_step[entity.id()]["element_key"],
                    status,
                    _actual(entity, facet),
                    reason,
                )
            )
            row["evaluated"] += 1
            row["passed" if status == "PASS" else "failed"] += 1
    return {
        "ruleset": deepcopy(package.preview()["ruleset"]),
        "checks": checks,
        "elements": elements,
        "findings": findings,
        "coverage": coverage,
        "models": [
            {
                "model_key": model_id,
                "content_id": source_sha,
                "sha256": source_sha,
                "schema": model.schema,
                "review_id": report.get("review_id", ""),
            }
        ],
    }


def _finding(check, model_id, source_sha, element_key, status, actual, reason):
    content = {
        "element_key": element_key,
        "model_key": model_id,
        "requirement_key": check["requirement_key"],
        "rule_id": check["rule_id"],
        "status": status,
        "expected": check["expected"],
        "actual": actual,
        "reason": reason,
        "semantics_digest": check["semantics_digest"],
        "checker": deepcopy(check["checker"]),
    }
    return {"finding_key": digest({"model": source_sha, **content}), **content}
