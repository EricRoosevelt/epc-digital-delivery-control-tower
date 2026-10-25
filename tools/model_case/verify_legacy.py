"""Compare one external IFC with its saved workbench report using the real legacy check stage.

This tool never reruns workbench parsing/tessellation. Raw IFC copies, generated
IDS/HTML/JSON reports, identities and detailed mismatches stay outside checkout.
Only aggregate counts are written to stdout. Run after browser sampling ends.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def external(path: Path) -> Path:
    path = Path(path).resolve()
    if (
        path == ROOT
        or ROOT in path.parents
        or any((parent / ".git").exists() for parent in (path, *path.parents))
    ):
        raise ValueError("Case inputs and raw evidence must remain outside checkout.")
    return path


def compare_findings(report, elements, legacy_findings):
    """Return aggregate counts plus private mismatch details; no geometry is loaded."""
    runtime_elements = {row["element_key"]: row for row in report["elements"]}
    if len(runtime_elements) != len(report["elements"]):
        raise ValueError("The saved report has duplicate element keys.")
    runtime = {}
    for finding in report["findings"]:
        if finding["rule_id"] != "PV-001":
            continue
        element = runtime_elements[finding["element_key"]]
        guid = element["global_id"]
        if guid in runtime:
            raise ValueError("The saved report has an ambiguous PV-001 GlobalId.")
        runtime[guid] = finding["status"]
    inventory_ids = {e.global_id for e in elements}
    if len(inventory_ids) != len(elements):
        raise ValueError("The legacy inventory has duplicate GlobalIds.")
    legacy_by_key = {e.element_key: e.global_id for e in elements}
    legacy = {
        legacy_by_key[f.element_key]: f.status.value for f in legacy_findings if f.element_key
    }
    if len(legacy) != sum(bool(f.element_key) for f in legacy_findings):
        raise ValueError("The legacy checker returned ambiguous element findings.")
    if any(status not in {"PASS", "FAIL"} for status in legacy.values()):
        raise ValueError("Unexpected element-level legacy status.")
    if any(status not in {"PASS", "FAIL", "NOT_APPLICABLE"} for status in runtime.values()):
        raise ValueError("Unexpected workbench PV-001 status.")
    runtime_applicable = {
        guid: status for guid, status in runtime.items() if status != "NOT_APPLICABLE"
    }
    common = set(legacy) & set(runtime_applicable)
    expected_na = inventory_ids - set(legacy)
    actual_na = {guid for guid, status in runtime.items() if status == "NOT_APPLICABLE"}
    details = {
        "status_mismatches": [
            {"global_id": guid, "legacy": legacy[guid], "workbench": runtime_applicable[guid]}
            for guid in sorted(common)
            if legacy[guid] != runtime_applicable[guid]
        ],
        "legacy_only_applicable": sorted(set(legacy) - set(runtime_applicable)),
        "workbench_only_applicable": sorted(set(runtime_applicable) - set(legacy)),
        "missing_workbench_elements": sorted(inventory_ids - set(runtime)),
        "extra_workbench_elements": sorted(set(runtime) - inventory_ids),
        "missing_na_projection": sorted(expected_na - actual_na),
        "extra_na_projection": sorted(actual_na - expected_na),
    }
    model_na = sum(not f.element_key and f.status.value == "N/A" for f in legacy_findings)
    counts = {
        "elements": len(elements),
        "legacy_applicable": len(legacy),
        "workbench_applicable": len(runtime_applicable),
        "common_applicable": len(common),
        "legacy_status": dict(Counter(legacy.values())),
        "workbench_applicable_status": dict(Counter(runtime_applicable.values())),
        "workbench_not_applicable": len(actual_na),
        "legacy_model_not_applicable": model_na,
        **{key: len(value) for key, value in details.items()},
    }
    counts["na_projection_matches"] = (
        not details["missing_na_projection"]
        and not details["extra_na_projection"]
        and model_na == int(not legacy)
    )
    counts["matched"] = not any(details.values()) and counts["na_projection_matches"]
    return counts, details


def verify(
    source: Path, saved_report: Path, output: Path, expected_applicable: int | None = None
):
    """Run the existing loader/registry/checker path in a new external workspace."""
    from epc_control_tower.config import load_project_manifests, load_run_config
    from epc_control_tower.registry import default_registry
    from epc_control_tower.rules import load_ruleset
    from epc_control_tower.stages.check import check
    from epc_control_tower.stages.ingest import ingest
    from epc_control_tower.stages.inventory import inventory

    source, saved_report, output = external(source), external(saved_report), external(output)
    if expected_applicable is not None and expected_applicable < 0:
        raise ValueError("Expected applicable count must not be negative.")
    report = json.loads(saved_report.read_text(encoding="utf-8"))
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if report["source"]["sha256"] != digest or len(report["models"]) != 1:
        raise ValueError("The saved report must describe exactly this single IFC payload.")
    if report["models"][0]["sha256"] != digest:
        raise ValueError("The saved model fingerprint differs from the source bytes.")
    output.mkdir(parents=True, exist_ok=True)
    workspace = output / "legacy-workspace"
    if workspace.exists() or (output / "legacy-parity.json").exists():
        raise ValueError(
            "Choose a new evidence directory; previous observations are not overwritten."
        )
    workspace.mkdir()
    with (output / "legacy-check.log").open("w", encoding="utf-8") as log:
        with redirect_stdout(log), redirect_stderr(log):
            rules = workspace / "rules/product-validation"
            shutil.copytree(ROOT / "rules/product-validation", rules)
            project = workspace / "projects/case"
            project.mkdir(parents=True)
            shutil.copyfile(source, project / "model.ifc")
            (project / "project.toml").write_text(
                '[project]\nproject_id="case"\nname="Local isolated verification"\n'
                '[[models]]\nmodel_id="mep"\ndiscipline="MEP"\nfilename="model.ifc"\n',
                encoding="utf-8",
            )
            config = replace(
                load_run_config(ROOT),
                ruleset_path=rules,
                reports_dir=workspace / "reports",
                processed_data_dir=workspace / "data/processed",
            )
            registry = default_registry(config)
            ruleset = load_ruleset(rules)
            pv = [item for item in ruleset.requirements if item.rule_id == "PV-001"]
            if len(pv) != 1:
                raise ValueError("Exactly one source PV-001 requirement is required.")
            snapshot = next(item for item in report["rules"] if item["rule_id"] == "PV-001")
            if snapshot.get("semantics_digest") != pv[0].semantics_digest:
                raise ValueError(
                    "The saved PV-001 predicate does not match the loaded rule source."
                )
            manifests = load_project_manifests(
                [project / "project.toml"], repository_root=workspace
            )
            ingested = ingest(manifests)
            if ingested.models[0].provenance.content_sha256 != digest:
                raise ValueError("The copied source payload changed during verification.")
            elements = inventory(ingested.models, {"case.mep": project / "model.ifc"})
            checked = check(
                registry=registry,
                ruleset=ruleset,
                manifests=manifests,
                projects=ingested.projects,
                models=ingested.models,
                elements=elements,
                validation_run_id="local-legacy-parity",
                as_of=config.as_of,
                reports_dir=config.reports_dir,
            )
            checked.raise_for_failures()
    pv_findings = [f for f in checked.findings if f.requirement_key == pv[0].requirement_key]
    counts, details = compare_findings(report, elements, pv_findings)
    counts["expected_applicable_matches"] = (
        expected_applicable is None or counts["common_applicable"] == expected_applicable
    )
    counts["matched"] = counts["matched"] and counts["expected_applicable_matches"]
    evidence = {
        "schema_version": 1,
        "source_path": str(source),
        "source_sha256": digest,
        "saved_report": str(saved_report),
        "review_id": report["review_id"],
        "legacy_schema": ingested.models[0].ifc_schema,
        "ruleset_id": ruleset.ruleset_id,
        "ruleset_version": ruleset.version,
        "predicate_semantics_digest": pv[0].semantics_digest,
        "workbench_predicate_snapshot": snapshot,
        "expected_applicable": expected_applicable,
        "counts": counts,
        "details": details,
        "scope": "Real legacy loader/registry/check/IdsChecker; no geometry rerun.",
    }
    (output / "legacy-parity.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ifc", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-applicable", type=int)
    args = parser.parse_args(argv)
    try:
        counts = verify(args.ifc, args.report, args.output_dir, args.expected_applicable)
    except Exception as error:
        # Detailed exceptions may contain source identities; keep them external.
        try:
            output = external(args.output_dir)
            output.mkdir(parents=True, exist_ok=True)
            (output / "legacy-parity-error.json").write_text(
                json.dumps(
                    {"error_type": type(error).__name__, "error": str(error)},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        except (ValueError, OSError):
            pass
        print(json.dumps({"matched": False, "verification_failed": True}))
        return 2
    print(json.dumps(counts, ensure_ascii=False))
    return 0 if counts["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
