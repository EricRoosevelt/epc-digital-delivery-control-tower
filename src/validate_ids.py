"""Normalize an IfcTester report into the published findings table.

Compatibility shim over :mod:`epc_control_tower`. Running the validation is now
``epc-ct run``: it opens the models, evaluates the rules, writes the reports and
produces every published artifact in one pass, from the canonical domain model.
``main`` here delegates to it and writes only ``ids_findings.csv``, which is
what this script always produced.

What is *not* delegated is :func:`normalize_report`. It turns one IfcTester
report dictionary into published rows, and it is the seam the pre-existing
tests exercise directly with hand-built reports. The package's IDS checker does
the same job against real models but does not take a report dictionary, so this
remains the legacy shape and retires with the legacy adapters.

Three behaviours are unchanged and deliberate:

* A specification with zero applicable elements becomes ``N/A``, not ``PASS``.
  IfcTester reports it as passing; counting that as compliance is what would
  inflate every published pass rate.
* ``actual`` stays empty. IfcTester does not stably report the value it
  observed, and an invented one would be worse than none.
* Severity is a property of the rule, not of the outcome: the R-005 family
  states a requirement this project assumes rather than a defect in a supplied
  model, so its failures are warnings.

The finding column list is no longer written out by hand. It comes from the row
type, which is the direct fix for these columns having been declared twice — as
a twenty-item list here and an eleven-item set elsewhere — and drifting apart.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from epc_control_tower.determinism import (  # noqa: E402
    atomic_write_bytes,
    sha256_file as calculate_sha256,
    write_csv_bytes,
)
from epc_control_tower.domain import field_names  # noqa: E402
from epc_control_tower.exporters.legacy_contract import LegacyFindingRow  # noqa: E402

try:
    from .identity import build_finding_key, build_requirement_key
except ImportError:  # pragma: no cover - the bare-import route
    from identity import build_finding_key, build_requirement_key

IDS_PATH = PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"
MODELS_PATH = PROJECT_ROOT / "data" / "processed" / "models.csv"
INVENTORY_PATH = PROJECT_ROOT / "data" / "processed" / "model_inventory.csv"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "reports" / "ids"
FINDINGS_OUTPUT = PROJECT_ROOT / "data" / "processed" / "ids_findings.csv"

#: Column order, taken from the row type rather than restated.
FINDING_COLUMNS = list(field_names(LegacyFindingRow))

IDS_NAMESPACE = {"ids": "http://standards.buildingsmart.org/IDS"}

_PASS_REASON = "Requirement satisfied."
_FAIL_REASON = "Requirement not satisfied."
_NOT_APPLICABLE_REASON = "No applicable elements exist in this model."


def get_specification_status(specification_report):
    """Turn IfcTester's outcome into ``PASS``, ``FAIL`` or ``N/A``.

    IfcTester reports zero applicable elements as passing. That is normalised
    to ``N/A`` and excluded from the applicable denominator, because reporting
    it as compliance would inflate every pass rate this project publishes.
    """

    total_applicable = int(specification_report.get("total_applicable", 0) or 0)
    if specification_report.get("is_skipped") or total_applicable == 0:
        return "N/A"
    return "PASS" if specification_report.get("status") else "FAIL"


def get_severity(identifier, status):
    """Severity of one outcome.

    R-005 states a requirement this project assumes rather than a defect in a
    supplied model, so failing it is a warning. Anything that is not a failure
    is not a problem and carries INFO.
    """

    if status != "FAIL":
        return "INFO"
    return "WARNING" if identifier.startswith("R-005") else "ERROR"


def get_requirement_id(requirement):
    """Return the canonical requirement label emitted by IfcTester."""

    requirement_id = requirement.get("label")
    if not requirement_id:
        raise ValueError("An IDS requirement has no canonical label")
    return str(requirement_id)


def _row(**values) -> dict[str, str]:
    return {column: values.get(column, "") for column in FINDING_COLUMNS}


def add_na_findings(
    findings,
    run_id,
    model_id,
    ids_version,
    identifier,
    specification_name,
    requirements,
):
    """Emit one specification-level ``N/A`` row per requirement.

    No element is applicable, so no element is named: an N/A finding that
    pointed at a component would be claiming something was checked.
    """

    for requirement in requirements:
        requirement_id = get_requirement_id(requirement)
        requirement_key = build_requirement_key(identifier, requirement_id)
        findings.append(
            _row(
                finding_key=build_finding_key(run_id, model_id, requirement_key, ""),
                run_id=run_id,
                model_id=model_id,
                ids_version=ids_version,
                specification_id=identifier,
                specification=f"{identifier}: {specification_name}",
                requirement_id=requirement_id,
                requirement_key=requirement_key,
                requirement=requirement_id,
                status="N/A",
                is_applicable="false",
                is_issue="false",
                severity="INFO",
                expected=requirement.get("description") or requirement_id,
                reason=_NOT_APPLICABLE_REASON,
            )
        )


def add_entity_findings(
    findings,
    entities,
    status,
    run_id,
    model_id,
    ids_version,
    identifier,
    specification_name,
    requirement,
    element_lookup,
):
    """Flatten one requirement's passing or failing elements into rows."""

    requirement_id = get_requirement_id(requirement)
    requirement_key = build_requirement_key(identifier, requirement_id)
    expected = requirement.get("description") or requirement_id

    for entity in entities:
        global_id = entity.get("global_id")
        if not global_id:
            raise ValueError("A non-N/A finding has no GlobalId")

        element_key = element_lookup.get((model_id, global_id))
        if not element_key:
            raise ValueError(
                f"Validation element not found in inventory: {(model_id, global_id)}"
            )

        findings.append(
            _row(
                finding_key=build_finding_key(
                    run_id, model_id, requirement_key, element_key
                ),
                run_id=run_id,
                model_id=model_id,
                element_key=element_key,
                global_id=global_id,
                ids_version=ids_version,
                specification_id=identifier,
                specification=f"{identifier}: {specification_name}",
                requirement_id=requirement_id,
                requirement_key=requirement_key,
                requirement=requirement_id,
                status=status,
                is_applicable="true",
                is_issue="true" if status == "FAIL" else "false",
                severity=get_severity(identifier, status),
                ifc_class=entity.get("class") or "",
                element_name=entity.get("name") or "",
                expected=expected,
                # IfcTester does not stably report the observed value, and
                # inventing one would be worse than leaving it out.
                actual="",
                reason=(
                    _PASS_REASON
                    if status == "PASS"
                    else (entity.get("reason") or _FAIL_REASON)
                ),
            )
        )


def normalize_report(
    report_data,
    model_id,
    run_id,
    ids_version,
    specification_ids,
    element_lookup,
):
    """Turn one model's nested IfcTester report into published rows."""

    findings: list[dict[str, str]] = []

    for specification in report_data["specifications"]:
        specification_name = specification["name"]
        identifier = specification_ids.get(specification_name)
        if not identifier:
            raise ValueError(
                f"Specification name not found in IDS XML: {specification_name}"
            )

        requirements = specification.get("requirements", [])
        requirement_ids = [get_requirement_id(item) for item in requirements]
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValueError(
                f"Duplicate requirement label in IDS specification: {identifier}"
            )

        status = get_specification_status(specification)
        if status == "N/A":
            add_na_findings(
                findings=findings,
                run_id=run_id,
                model_id=model_id,
                ids_version=ids_version,
                identifier=identifier,
                specification_name=specification_name,
                requirements=requirements,
            )
            continue

        for requirement in requirements:
            passed = requirement.get("passed_entities", []) or []
            failed = requirement.get("failed_entities", []) or []
            total_applicable = int(requirement.get("total_applicable", 0) or 0)
            if len(passed) + len(failed) != total_applicable:
                raise ValueError(
                    "Requirement entity counts do not reconcile: "
                    f"{identifier} {requirement.get('label')}"
                )

            for entities, entity_status in ((passed, "PASS"), (failed, "FAIL")):
                add_entity_findings(
                    findings=findings,
                    entities=entities,
                    status=entity_status,
                    run_id=run_id,
                    model_id=model_id,
                    ids_version=ids_version,
                    identifier=identifier,
                    specification_name=specification_name,
                    requirement=requirement,
                    element_lookup=element_lookup,
                )

    return findings


def main() -> None:
    """Validate every configured project and write the published findings."""

    from epc_control_tower.config import load_run_config
    from epc_control_tower.exporters.legacy_projection import project_bundle
    from epc_control_tower.pipeline import build_bundle

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=FINDINGS_OUTPUT)
    arguments = parser.parse_args()

    config = load_run_config(PROJECT_ROOT)
    result = build_bundle(config)
    projection = project_bundle(result.bundle)

    print(f"Validation run: {projection.run_id}")
    atomic_write_bytes(
        arguments.output,
        write_csv_bytes(
            [
                {column: getattr(row, column) for column in FINDING_COLUMNS}
                for row in projection.findings
            ],
            FINDING_COLUMNS,
        ),
    )
    print(f"Wrote {len(projection.findings)} findings to {arguments.output}")
    print(f"Findings SHA-256: {calculate_sha256(arguments.output)}")


if __name__ == "__main__":
    main()
