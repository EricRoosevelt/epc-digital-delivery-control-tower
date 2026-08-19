"""Generate deterministic BCF 3.0 issues from the published findings CSV.

Compatibility shim over :mod:`epc_control_tower`. Everything that decides what
the archive *contains* — the markup and viewpoint XML, the camera solve, the
reproducible ZIP, the sidecar row shapes, the frozen identity derivations —
lives in the package now and is reused verbatim here. What remains is the
legacy front end: this script starts from the published CSV files rather than
from a validation, and it checks them hard before believing them.

That front end is why this is not a two-line delegation. `epc-ct run` produces
the same artifacts from the canonical model in one pass; this path exists so
that somebody holding only the published CSVs can still rebuild the archive,
and so that the fail-closed checks on those files keep being exercised.

Two assertions the previous version made are gone: that there were exactly six
failures, and exactly three topics of two findings each. They were counts taken
from a fixture and would have failed the pipeline rather than the data. The
scope this converter really depends on — the R-005 rule family, the HVAC model —
is still asserted, by the exporter that owns it.

Retires with the legacy adapters.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path

import ifcopenshell

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for _entry in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    # Importable both as ``src.generate_bcf`` and, with ``src/`` already on the
    # path, as a bare ``generate_bcf``. The previous version only supported the
    # second, so importing it the dotted way failed on its own sibling import.
    if str(_entry) not in sys.path:
        sys.path.insert(0, str(_entry))

from bcf_common import (  # noqa: E402
    SCHEMA_DIR,
    build_deterministic_zip,
    calculate_sha256,
    camera_for_aabb,
    enrich_finding_identity,
    read_csv_rows,
    repo_relative,
    validate_xml_schemas,
    verify_schema_bundle,
    world_coordinate_aabb,
)
from epc_control_tower.determinism import atomic_write_bytes, json_bytes  # noqa: E402
from epc_control_tower.domain import (  # noqa: E402
    Element,
    Model,
    Provenance,
    field_names,
)
from epc_control_tower.exporters.legacy_bcf import BCF_FILENAME, LegacyBcfExporter  # noqa: E402
from epc_control_tower.exporters.legacy_contract import (  # noqa: E402
    ASSIGNEE,
    ASSIGNEE_ROLE,
    CREATION_AUTHOR,
    EVENT_SOURCE,
    EVENT_TYPE_CREATED,
    FIXED_TIMESTAMP,
    ORIGINATING_SYSTEM,
    TOPIC_LABELS,
    TOPIC_PRIORITY,
    TOPIC_STAGE,
    TOPIC_STATUS,
    TOPIC_TYPE,
    LegacyComponentRow,
    LegacyEventRow,
    LegacyFindingRow,
    LegacyTopicFindingRow,
    LegacyTopicRow,
    LegacyViewpointRow,
)
from epc_control_tower.exporters.legacy_manifest import (  # noqa: E402
    MANIFEST_FILENAME,
    build_legacy_manifest,
)
from epc_control_tower.exporters.legacy_projection import (  # noqa: E402
    LegacyTopic,
    viewpoint_row,
)
from epc_control_tower.legacy_identity import (  # noqa: E402
    legacy_topic_event_id,
    legacy_topic_guid,
    legacy_viewpoint_guid,
)

FINDINGS_PATH = PROJECT_ROOT / "data" / "processed" / "ids_findings.csv"
MODELS_PATH = PROJECT_ROOT / "data" / "processed" / "models.csv"
INVENTORY_PATH = PROJECT_ROOT / "data" / "processed" / "model_inventory.csv"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
IDS_PATH = PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"
BCF_OUTPUT = PROJECT_ROOT / "reports" / "bcf" / BCF_FILENAME
MANIFEST_OUTPUT = PROJECT_ROOT / "reports" / "bcf" / MANIFEST_FILENAME
SIDECAR_DIR = PROJECT_ROOT / "data" / "processed"

#: Column order comes from the row types, so it cannot drift from them.
SIDECAR_COLUMNS = {
    "bcf_topics.csv": list(field_names(LegacyTopicRow)),
    "bcf_topic_findings.csv": list(field_names(LegacyTopicFindingRow)),
    "bcf_viewpoints.csv": list(field_names(LegacyViewpointRow)),
    "bcf_viewpoint_components.csv": list(field_names(LegacyComponentRow)),
    "bcf_topic_events.csv": list(field_names(LegacyEventRow)),
}

#: The project identifier the published contract does not carry. Required by
#: the domain types, dropped again on the way out.
_LEGACY_PROJECT_ID = "legacy"


@dataclasses.dataclass(frozen=True)
class WorkflowArtifacts:
    """All deterministic in-memory products of one BCF conversion run."""

    source_run_id: str
    bcf_entries: dict[str, bytes]
    bcf_bytes: bytes
    sidecar_rows: dict[str, list[dict[str, object]]]
    sidecar_bytes: dict[str, bytes]


def _require_unique(rows: list[dict[str, str]], column: str, label: str) -> None:
    values = [row[column] for row in rows]
    if any(not value for value in values) or len(values) != len(set(values)):
        raise ValueError(f"{label} must contain unique non-empty {column} values")


def _finding_row(row: dict[str, str]) -> LegacyFindingRow:
    return LegacyFindingRow(**{name: row[name] for name in field_names(LegacyFindingRow)})


def _model(row: dict[str, str]) -> Model:
    return Model(
        model_key=row["model_id"],
        model_id=row["model_id"],
        project_id=_LEGACY_PROJECT_ID,
        discipline=row["discipline"],
        filename=row["filename"],
        provenance=Provenance(
            source_url=row["source_url"],
            license=row["license"],
            content_sha256=row["content_sha256"],
        ),
        ifc_schema=row["ifc_schema"],
        ifc_project_guid=row["ifc_project_guid"],
    )


def _element(row: dict[str, str]) -> Element:
    return Element(
        element_key=row["element_key"],
        model_key=row["model_id"],
        global_id=row["global_id"],
        ifc_class=row["ifc_class"],
        name=row["name"],
        storey=row["storey"],
        pset_count=int(row["pset_count"]),
    )


def build_workflow_artifacts(
    findings_path: Path = FINDINGS_PATH,
    models_path: Path = MODELS_PATH,
    inventory_path: Path = INVENTORY_PATH,
    raw_data_dir: Path = RAW_DATA_DIR,
    schema_dir: Path = SCHEMA_DIR,
) -> WorkflowArtifacts:
    """Build but do not write the BCF and analytical sidecars."""

    verify_schema_bundle(schema_dir)

    findings = [
        enrich_finding_identity(row)
        for row in read_csv_rows(findings_path)
        if row.get("status") == "FAIL"
    ]
    if not findings:
        raise ValueError("No FAIL findings to convert")

    source_run_ids = {row["run_id"] for row in findings}
    if len(source_run_ids) != 1:
        raise ValueError("FAIL findings must belong to exactly one IDS run")
    source_run_id = next(iter(source_run_ids))

    finding_keys = [row["finding_key"] for row in findings]
    if len(finding_keys) != len(set(finding_keys)):
        raise ValueError("FAIL finding_key values are not unique")
    for finding in findings:
        if finding.get("is_applicable", "true") != "true":
            raise ValueError("A FAIL finding must be applicable")
        if finding.get("is_issue", "true") != "true":
            raise ValueError("A FAIL finding must be flagged as an issue")

    model_records = read_csv_rows(models_path)
    inventory_records = read_csv_rows(inventory_path)
    _require_unique(model_records, "model_id", "models.csv")
    _require_unique(inventory_records, "element_key", "model_inventory.csv")
    models = {row["model_id"]: _model(row) for row in model_records}
    elements = {row["element_key"]: _element(row) for row in inventory_records}

    groups: dict[str, list[dict[str, str]]] = {}
    for finding in findings:
        element_key = finding["element_key"]
        if not element_key or element_key not in elements:
            raise ValueError(f"FAIL finding has an unknown element_key: {element_key}")
        element = elements[element_key]
        for column, observed in (
            ("model_id", element.model_key),
            ("global_id", element.global_id),
            ("ifc_class", element.ifc_class),
        ):
            if finding[column] != observed:
                raise ValueError(
                    f"Finding/inventory mismatch for {element_key}: {column}"
                )
        groups.setdefault(element_key, []).append(finding)

    topics: list[LegacyTopic] = []
    opened: dict[str, ifcopenshell.file] = {}
    for element_key in sorted(groups):
        element = elements[element_key]
        model = models.get(element.model_key)
        if model is None:
            raise ValueError(f"Inventory refers to unknown model_id: {element.model_key}")

        ifc_path = raw_data_dir / model.filename
        if calculate_sha256(ifc_path) != model.provenance.content_sha256:
            raise ValueError(f"IFC content hash mismatch: {ifc_path}")
        if model.model_key not in opened:
            opened[model.model_key] = ifcopenshell.open(str(ifc_path))
        ifc_element = opened[model.model_key].by_guid(element.global_id)
        if ifc_element is None or ifc_element.is_a() != element.ifc_class:
            raise ValueError(f"Inventory element not found in IFC: {element_key}")

        aabb = world_coordinate_aabb(opened[model.model_key], element.global_id)
        topic_guid = legacy_topic_guid(element_key)
        rows = sorted(
            (_finding_row(finding) for finding in groups[element_key]),
            key=lambda row: row.finding_key,
        )
        topics.append(
            LegacyTopic(
                element_key=element_key,
                topic_guid=topic_guid,
                viewpoint_guid=legacy_viewpoint_guid(topic_guid),
                model=model,
                element=element,
                findings=tuple(rows),
                aabb=aabb,
                camera=camera_for_aabb(aabb),
                # Stated here because this path has no rules to read them from:
                # it builds topics straight from the published CSVs, against the
                # frozen `.ids` document, and IDS 1.0 has nowhere to record a
                # priority, a stage, an owner or a label. The package pipeline
                # takes all four from rule metadata.
                assignee_role=ASSIGNEE_ROLE,
                priority=TOPIC_PRIORITY,
                stage=TOPIC_STAGE,
                labels=TOPIC_LABELS,
            )
        )

    exporter = LegacyBcfExporter(schema_dir=schema_dir)
    entries = exporter.root_entries(topics)
    sidecar_rows: dict[str, list[dict[str, object]]] = {
        name: [] for name in SIDECAR_COLUMNS
    }

    for topic in topics:
        entries[f"{topic.topic_guid}/"] = b""
        entries[f"{topic.topic_guid}/markup.bcf"] = exporter.markup(
            topic, FIXED_TIMESTAMP
        )
        entries[f"{topic.topic_guid}/{topic.viewpoint_filename}"] = exporter.viewpoint(
            topic
        )

        sidecar_rows["bcf_topics.csv"].append(
            dataclasses.asdict(
                LegacyTopicRow(
                    run_id=source_run_id,
                    topic_guid=topic.topic_guid,
                    topic_type=TOPIC_TYPE,
                    topic_status=TOPIC_STATUS,
                    title=topic.title,
                    priority=TOPIC_PRIORITY,
                    creation_date=FIXED_TIMESTAMP,
                    creation_author=CREATION_AUTHOR,
                    assigned_to=ASSIGNEE,
                    stage=TOPIC_STAGE,
                    model_id=topic.model.model_id,
                    element_key=topic.element_key,
                    global_id=topic.element.global_id,
                    ifc_class=topic.element.ifc_class,
                    element_name=topic.element.name,
                    finding_count=len(topic.findings),
                )
            )
        )
        for row in topic.findings:
            sidecar_rows["bcf_topic_findings.csv"].append(
                dataclasses.asdict(
                    LegacyTopicFindingRow(
                        run_id=source_run_id,
                        topic_guid=topic.topic_guid,
                        finding_key=row.finding_key,
                        requirement_key=row.requirement_key,
                        specification_id=row.specification_id,
                        requirement_id=row.requirement_id,
                        specification=row.specification,
                        requirement=row.requirement,
                        severity=row.severity,
                        model_id=topic.model.model_id,
                        element_key=topic.element_key,
                        global_id=topic.element.global_id,
                    )
                )
            )
        sidecar_rows["bcf_viewpoints.csv"].append(
            dataclasses.asdict(viewpoint_row(topic, source_run_id))
        )
        sidecar_rows["bcf_viewpoint_components.csv"].append(
            dataclasses.asdict(
                LegacyComponentRow(
                    run_id=source_run_id,
                    viewpoint_guid=topic.viewpoint_guid,
                    topic_guid=topic.topic_guid,
                    component_index=1,
                    model_id=topic.model.model_id,
                    element_key=topic.element_key,
                    global_id=topic.element.global_id,
                    originating_system=ORIGINATING_SYSTEM,
                    authoring_tool_id=topic.element.global_id,
                )
            )
        )
        sidecar_rows["bcf_topic_events.csv"].append(
            dataclasses.asdict(
                LegacyEventRow(
                    run_id=source_run_id,
                    event_id=legacy_topic_event_id(topic.topic_guid),
                    topic_guid=topic.topic_guid,
                    event_type=EVENT_TYPE_CREATED,
                    event_date=FIXED_TIMESTAMP,
                    event_author=CREATION_AUTHOR,
                    value="",
                    source=EVENT_SOURCE,
                )
            )
        )

    for name, rows in sidecar_rows.items():
        columns = SIDECAR_COLUMNS[name]
        rows.sort(key=lambda row: tuple(str(row[column]) for column in columns))

    validate_xml_schemas(entries, schema_dir)

    from bcf_common import write_csv_bytes

    return WorkflowArtifacts(
        source_run_id=source_run_id,
        bcf_entries=entries,
        bcf_bytes=build_deterministic_zip(entries),
        sidecar_rows=sidecar_rows,
        sidecar_bytes={
            name: write_csv_bytes(sidecar_rows[name], columns)
            for name, columns in SIDECAR_COLUMNS.items()
        },
    )


def write_workflow_outputs(
    artifacts: WorkflowArtifacts,
    bcf_output: Path = BCF_OUTPUT,
    sidecar_dir: Path = SIDECAR_DIR,
    manifest_output: Path = MANIFEST_OUTPUT,
    findings_path: Path = FINDINGS_PATH,
    models_path: Path = MODELS_PATH,
    inventory_path: Path = INVENTORY_PATH,
    raw_data_dir: Path = RAW_DATA_DIR,
    ids_path: Path = IDS_PATH,
    schema_dir: Path = SCHEMA_DIR,
) -> dict[str, object]:
    """Write all artifacts atomically and return the manifest payload."""

    for path in [bcf_output, manifest_output, *(sidecar_dir / n for n in SIDECAR_COLUMNS)]:
        repo_relative(path)

    atomic_write_bytes(bcf_output, artifacts.bcf_bytes)
    for filename, data in artifacts.sidecar_bytes.items():
        atomic_write_bytes(sidecar_dir / filename, data)

    projection = _projection_view(artifacts)
    hvac = next(row for row in projection.models if row.model_id == "hvac")
    manifest = build_legacy_manifest(
        projection,
        repository_root=PROJECT_ROOT,
        input_paths=[
            findings_path,
            models_path,
            inventory_path,
            ids_path,
            raw_data_dir / hvac.filename,
        ],
        sidecar_dir=sidecar_dir,
        bcf_path=bcf_output,
        schema_dir=schema_dir,
    )
    atomic_write_bytes(manifest_output, json_bytes(manifest))
    return manifest


@dataclasses.dataclass(frozen=True)
class _ProjectionView:
    """Just enough of a projection for the manifest builder to describe."""

    run_id: str
    as_of: str
    models: tuple
    topic_rows: tuple
    topic_finding_rows: tuple
    viewpoint_rows: tuple
    component_rows: tuple
    event_rows: tuple


def _projection_view(artifacts: WorkflowArtifacts) -> _ProjectionView:
    return _ProjectionView(
        run_id=artifacts.source_run_id,
        as_of=FIXED_TIMESTAMP,
        models=_manifest_models(),
        topic_rows=tuple(artifacts.sidecar_rows["bcf_topics.csv"]),
        topic_finding_rows=tuple(artifacts.sidecar_rows["bcf_topic_findings.csv"]),
        viewpoint_rows=tuple(artifacts.sidecar_rows["bcf_viewpoints.csv"]),
        component_rows=tuple(artifacts.sidecar_rows["bcf_viewpoint_components.csv"]),
        event_rows=tuple(artifacts.sidecar_rows["bcf_topic_events.csv"]),
    )


def _manifest_models() -> tuple:
    from epc_control_tower.exporters.legacy_contract import LegacyModelRow

    return tuple(
        LegacyModelRow(**{name: row[name] for name in field_names(LegacyModelRow)})
        for row in read_csv_rows(MODELS_PATH)
    )


def generate_bcf_workflow(
    findings_path: Path = FINDINGS_PATH,
    models_path: Path = MODELS_PATH,
    inventory_path: Path = INVENTORY_PATH,
    raw_data_dir: Path = RAW_DATA_DIR,
    bcf_output: Path = BCF_OUTPUT,
    sidecar_dir: Path = SIDECAR_DIR,
    manifest_output: Path = MANIFEST_OUTPUT,
    ids_path: Path = IDS_PATH,
    schema_dir: Path = SCHEMA_DIR,
    validate_after_write: bool = True,
) -> dict[str, object]:
    """Build, write, reload, and validate the complete BCF workflow."""

    artifacts = build_workflow_artifacts(
        findings_path=findings_path,
        models_path=models_path,
        inventory_path=inventory_path,
        raw_data_dir=raw_data_dir,
        schema_dir=schema_dir,
    )
    manifest = write_workflow_outputs(
        artifacts,
        bcf_output=bcf_output,
        sidecar_dir=sidecar_dir,
        manifest_output=manifest_output,
        findings_path=findings_path,
        models_path=models_path,
        inventory_path=inventory_path,
        raw_data_dir=raw_data_dir,
        ids_path=ids_path,
        schema_dir=schema_dir,
    )
    if validate_after_write:
        from validate_bcf import validate_bcf_workflow

        validate_bcf_workflow(
            bcf_path=bcf_output,
            findings_path=findings_path,
            models_path=models_path,
            inventory_path=inventory_path,
            raw_data_dir=raw_data_dir,
            sidecar_dir=sidecar_dir,
            manifest_path=manifest_output,
            schema_dir=schema_dir,
        )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--findings", type=Path, default=FINDINGS_PATH)
    parser.add_argument("--models", type=Path, default=MODELS_PATH)
    parser.add_argument("--inventory", type=Path, default=INVENTORY_PATH)
    parser.add_argument("--raw-data-dir", type=Path, default=RAW_DATA_DIR)
    parser.add_argument("--output", type=Path, default=BCF_OUTPUT)
    parser.add_argument("--sidecar-dir", type=Path, default=SIDECAR_DIR)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_OUTPUT)
    parser.add_argument("--ids", type=Path, default=IDS_PATH)
    parser.add_argument("--schema-dir", type=Path, default=SCHEMA_DIR)
    arguments = parser.parse_args()
    manifest = generate_bcf_workflow(
        findings_path=arguments.findings,
        models_path=arguments.models,
        inventory_path=arguments.inventory,
        raw_data_dir=arguments.raw_data_dir,
        bcf_output=arguments.output,
        sidecar_dir=arguments.sidecar_dir,
        manifest_output=arguments.manifest,
        ids_path=arguments.ids,
        schema_dir=arguments.schema_dir,
    )
    counts = manifest["counts"]
    print(
        "Generated and validated BCF 3.0: "
        f"{counts['topics']} topics, "
        f"{counts['viewpoints']} viewpoints, "
        f"{counts['viewpoint_components']} components, "
        f"{counts['topic_findings']} finding links"
    )
    print(f"BCF SHA-256: {calculate_sha256(arguments.output)}")


if __name__ == "__main__":
    main()
