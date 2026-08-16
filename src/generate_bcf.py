"""Generate deterministic BCF 3.0 issues from normalized IDS failures."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from xml.etree import ElementTree as ET

import ifcopenshell

from bcf_common import (
    ASSIGNEE,
    BCF_VERSION,
    CREATION_AUTHOR,
    FINDING_URN_PREFIX,
    FIXED_TIMESTAMP,
    OFFICIAL_SCHEMA_COMMIT,
    PROJECT_GUID,
    PROJECT_NAME,
    PROJECT_ROOT,
    SCHEMA_DIR,
    build_deterministic_zip,
    bytes_sha256,
    calculate_sha256,
    camera_for_aabb,
    enrich_finding_identity,
    format_float,
    read_csv_rows,
    repo_relative,
    validate_xml_schemas,
    verify_schema_bundle,
    world_coordinate_aabb,
    write_csv_bytes,
    xml_bytes,
)
from identity import uuid5_from_values


FINDINGS_PATH = PROJECT_ROOT / "data" / "processed" / "ids_findings.csv"
MODELS_PATH = PROJECT_ROOT / "data" / "processed" / "models.csv"
INVENTORY_PATH = PROJECT_ROOT / "data" / "processed" / "model_inventory.csv"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
IDS_PATH = PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"
BCF_OUTPUT = PROJECT_ROOT / "reports" / "bcf" / "ids_failures.bcf"
MANIFEST_OUTPUT = PROJECT_ROOT / "reports" / "bcf" / "run_manifest.json"
SIDECAR_DIR = PROJECT_ROOT / "data" / "processed"

TOPIC_COLUMNS = [
    "run_id",
    "topic_guid",
    "topic_type",
    "topic_status",
    "title",
    "priority",
    "creation_date",
    "creation_author",
    "assigned_to",
    "stage",
    "model_id",
    "element_key",
    "global_id",
    "ifc_class",
    "element_name",
    "finding_count",
]

TOPIC_FINDING_COLUMNS = [
    "run_id",
    "topic_guid",
    "finding_key",
    "requirement_key",
    "specification_id",
    "requirement_id",
    "specification",
    "requirement",
    "severity",
    "model_id",
    "element_key",
    "global_id",
]

VIEWPOINT_COLUMNS = [
    "run_id",
    "viewpoint_guid",
    "topic_guid",
    "viewpoint_filename",
    "model_id",
    "element_key",
    "global_id",
    "aabb_min_x",
    "aabb_min_y",
    "aabb_min_z",
    "aabb_max_x",
    "aabb_max_y",
    "aabb_max_z",
    "target_x",
    "target_y",
    "target_z",
    "camera_view_point_x",
    "camera_view_point_y",
    "camera_view_point_z",
    "camera_direction_x",
    "camera_direction_y",
    "camera_direction_z",
    "camera_up_x",
    "camera_up_y",
    "camera_up_z",
    "field_of_view",
    "aspect_ratio",
]

COMPONENT_COLUMNS = [
    "run_id",
    "viewpoint_guid",
    "topic_guid",
    "component_index",
    "model_id",
    "element_key",
    "global_id",
    "originating_system",
    "authoring_tool_id",
]

EVENT_COLUMNS = [
    "run_id",
    "event_id",
    "topic_guid",
    "event_type",
    "event_date",
    "event_author",
    "value",
    "source",
]

SIDECAR_COLUMNS = {
    "bcf_topics.csv": TOPIC_COLUMNS,
    "bcf_topic_findings.csv": TOPIC_FINDING_COLUMNS,
    "bcf_viewpoints.csv": VIEWPOINT_COLUMNS,
    "bcf_viewpoint_components.csv": COMPONENT_COLUMNS,
    "bcf_topic_events.csv": EVENT_COLUMNS,
}


@dataclass(frozen=True)
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


def _child(parent: ET.Element, tag: str, text: object) -> ET.Element:
    child = ET.SubElement(parent, tag)
    child.text = str(text)
    return child


def _vector(parent: ET.Element, tag: str, values: tuple[float, float, float]) -> None:
    vector = ET.SubElement(parent, tag)
    for axis, value in zip(("X", "Y", "Z"), values, strict=True):
        _child(vector, axis, format_float(value))


def _build_root_entries() -> dict[str, bytes]:
    version_root = ET.Element("Version", {"VersionId": BCF_VERSION})

    project_root = ET.Element("ProjectInfo")
    project = ET.SubElement(project_root, "Project", {"ProjectId": PROJECT_GUID})
    _child(project, "Name", PROJECT_NAME)

    extensions_root = ET.Element("Extensions")
    extension_values = (
        ("TopicTypes", "TopicType", ["Issue"]),
        ("TopicStatuses", "TopicStatus", ["Open"]),
        ("Priorities", "Priority", ["Medium"]),
        (
            "TopicLabels",
            "TopicLabel",
            ["HVAC", "IDS", "ProjectAssumption"],
        ),
        ("Users", "User", [ASSIGNEE, CREATION_AUTHOR]),
        ("Stages", "Stage", ["Coordination"]),
    )
    for group_name, item_name, values in extension_values:
        group = ET.SubElement(extensions_root, group_name)
        for value in values:
            _child(group, item_name, value)

    return {
        "bcf.version": xml_bytes(version_root),
        "extensions.xml": xml_bytes(extensions_root),
        "project.bcfp": xml_bytes(project_root),
    }


def _build_markup(
    topic_guid: str,
    viewpoint_guid: str,
    model_row: dict[str, str],
    element_row: dict[str, str],
    findings: list[dict[str, str]],
) -> bytes:
    root = ET.Element("Markup")
    header = ET.SubElement(root, "Header")
    files = ET.SubElement(header, "Files")
    file_node = ET.SubElement(
        files,
        "File",
        {
            "IfcProject": model_row["ifc_project_guid"],
            "IsExternal": "true",
        },
    )
    _child(file_node, "Filename", model_row["filename"])
    _child(file_node, "Date", FIXED_TIMESTAMP)

    topic = ET.SubElement(
        root,
        "Topic",
        {
            "Guid": topic_guid,
            "TopicType": "Issue",
            "TopicStatus": "Open",
        },
    )
    links = ET.SubElement(topic, "ReferenceLinks")
    for finding in findings:
        _child(links, "ReferenceLink", FINDING_URN_PREFIX + finding["finding_key"])

    element_name = element_row.get("name") or element_row["ifc_class"]
    title = f"IDS metadata action: {element_name}"[:128]
    _child(topic, "Title", title)
    _child(topic, "Priority", "Medium")
    labels = ET.SubElement(topic, "Labels")
    for label in ("HVAC", "IDS", "ProjectAssumption"):
        _child(labels, "Label", label)
    _child(topic, "CreationDate", FIXED_TIMESTAMP)
    _child(topic, "CreationAuthor", CREATION_AUTHOR)
    _child(topic, "AssignedTo", ASSIGNEE)
    _child(topic, "Stage", "Coordination")
    requirements = ", ".join(finding["requirement"] for finding in findings)
    _child(
        topic,
        "Description",
        (
            "Project-assumed information requirement unmet for "
            f"{element_row['element_key']}. Required checks: {requirements}. "
            "This workflow classification does not assert a defect in the source model."
        ),
    )
    viewpoints = ET.SubElement(topic, "Viewpoints")
    viewpoint = ET.SubElement(viewpoints, "ViewPoint", {"Guid": viewpoint_guid})
    _child(viewpoint, "Viewpoint", f"{viewpoint_guid}.bcfv")
    return xml_bytes(root)


def _build_viewpoint(
    viewpoint_guid: str,
    global_id: str,
    camera,
) -> bytes:
    root = ET.Element("VisualizationInfo", {"Guid": viewpoint_guid})
    components = ET.SubElement(root, "Components")
    selection = ET.SubElement(components, "Selection")
    component = ET.SubElement(selection, "Component", {"IfcGuid": global_id})
    _child(component, "OriginatingSystem", "EPC Digital Delivery Control Tower")
    _child(component, "AuthoringToolId", global_id)
    ET.SubElement(components, "Visibility", {"DefaultVisibility": "true"})

    perspective = ET.SubElement(root, "PerspectiveCamera")
    _vector(perspective, "CameraViewPoint", camera.position)
    _vector(perspective, "CameraDirection", camera.direction)
    _vector(perspective, "CameraUpVector", camera.up)
    _child(perspective, "FieldOfView", format_float(camera.field_of_view))
    _child(perspective, "AspectRatio", format_float(camera.aspect_ratio))
    return xml_bytes(root)


def _viewpoint_row(
    run_id: str,
    viewpoint_guid: str,
    topic_guid: str,
    model_id: str,
    element_key: str,
    global_id: str,
    aabb,
    camera,
) -> dict[str, object]:
    row: dict[str, object] = {
        "run_id": run_id,
        "viewpoint_guid": viewpoint_guid,
        "topic_guid": topic_guid,
        "viewpoint_filename": f"{viewpoint_guid}.bcfv",
        "model_id": model_id,
        "element_key": element_key,
        "global_id": global_id,
        "field_of_view": format_float(camera.field_of_view),
        "aspect_ratio": format_float(camera.aspect_ratio),
    }
    for prefix, values in (
        ("aabb_min", aabb.minimum),
        ("aabb_max", aabb.maximum),
        ("target", camera.target),
        ("camera_view_point", camera.position),
        ("camera_direction", camera.direction),
        ("camera_up", camera.up),
    ):
        for axis, value in zip(("x", "y", "z"), values, strict=True):
            row[f"{prefix}_{axis}"] = format_float(value)
    return row


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
    if len(findings) != 6:
        raise ValueError(f"Expected 6 FAIL findings, found {len(findings)}")
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
        if finding["specification_id"] not in {"R-005A", "R-005B"}:
            raise ValueError("BCF conversion only accepts project-assumed R-005 failures")

    models = read_csv_rows(models_path)
    inventory = read_csv_rows(inventory_path)
    _require_unique(models, "model_id", "models.csv")
    _require_unique(inventory, "element_key", "model_inventory.csv")
    model_lookup = {row["model_id"]: row for row in models}
    element_lookup = {row["element_key"]: row for row in inventory}

    groups: dict[str, list[dict[str, str]]] = {}
    for finding in findings:
        element_key = finding["element_key"]
        if not element_key or element_key not in element_lookup:
            raise ValueError(f"FAIL finding has an unknown element_key: {element_key}")
        element = element_lookup[element_key]
        for column in ("model_id", "global_id", "ifc_class"):
            if finding[column] != element[column]:
                raise ValueError(
                    f"Finding/inventory mismatch for {element_key}: {column}"
                )
        groups.setdefault(element_key, []).append(finding)
    if len(groups) != 3 or any(len(rows) != 2 for rows in groups.values()):
        raise ValueError("Expected 3 element topics with exactly 2 findings each")

    entries = _build_root_entries()
    sidecar_rows: dict[str, list[dict[str, object]]] = {
        name: [] for name in SIDECAR_COLUMNS
    }
    model_cache: dict[str, ifcopenshell.file] = {}

    for element_key in sorted(groups):
        group = sorted(groups[element_key], key=lambda row: row["finding_key"])
        element = element_lookup[element_key]
        model_id = element["model_id"]
        model_row = model_lookup.get(model_id)
        if model_row is None:
            raise ValueError(f"Inventory refers to unknown model_id: {model_id}")
        if model_id != "hvac" or model_row["filename"] != "Building-Hvac.ifc":
            raise ValueError("BCF FAIL workflow is expected to target Building-Hvac.ifc")

        ifc_path = raw_data_dir / model_row["filename"]
        if calculate_sha256(ifc_path) != model_row["content_sha256"]:
            raise ValueError(f"IFC content hash mismatch: {ifc_path}")
        model = model_cache.setdefault(model_id, ifcopenshell.open(str(ifc_path)))
        ifc_element = model.by_guid(element["global_id"])
        if ifc_element is None or ifc_element.is_a() != element["ifc_class"]:
            raise ValueError(f"Inventory element not found in IFC: {element_key}")

        aabb = world_coordinate_aabb(model, element["global_id"])
        camera = camera_for_aabb(aabb)
        topic_guid = uuid5_from_values("bcf-topic", [element_key])
        viewpoint_guid = uuid5_from_values("bcf-viewpoint", [topic_guid])
        markup_name = f"{topic_guid}/markup.bcf"
        viewpoint_name = f"{topic_guid}/{viewpoint_guid}.bcfv"
        entries[f"{topic_guid}/"] = b""
        entries[markup_name] = _build_markup(
            topic_guid,
            viewpoint_guid,
            model_row,
            element,
            group,
        )
        entries[viewpoint_name] = _build_viewpoint(
            viewpoint_guid,
            element["global_id"],
            camera,
        )

        element_name = element.get("name") or element["ifc_class"]
        sidecar_rows["bcf_topics.csv"].append(
            {
                "run_id": source_run_id,
                "topic_guid": topic_guid,
                "topic_type": "Issue",
                "topic_status": "Open",
                "title": f"IDS metadata action: {element_name}"[:128],
                "priority": "Medium",
                "creation_date": FIXED_TIMESTAMP,
                "creation_author": CREATION_AUTHOR,
                "assigned_to": ASSIGNEE,
                "stage": "Coordination",
                "model_id": model_id,
                "element_key": element_key,
                "global_id": element["global_id"],
                "ifc_class": element["ifc_class"],
                "element_name": element.get("name", ""),
                "finding_count": len(group),
            }
        )
        for finding in group:
            sidecar_rows["bcf_topic_findings.csv"].append(
                {
                    "run_id": source_run_id,
                    "topic_guid": topic_guid,
                    "finding_key": finding["finding_key"],
                    "requirement_key": finding["requirement_key"],
                    "specification_id": finding["specification_id"],
                    "requirement_id": finding["requirement_id"],
                    "specification": finding["specification"],
                    "requirement": finding["requirement"],
                    "severity": finding["severity"],
                    "model_id": model_id,
                    "element_key": element_key,
                    "global_id": element["global_id"],
                }
            )
        sidecar_rows["bcf_viewpoints.csv"].append(
            _viewpoint_row(
                source_run_id,
                viewpoint_guid,
                topic_guid,
                model_id,
                element_key,
                element["global_id"],
                aabb,
                camera,
            )
        )
        sidecar_rows["bcf_viewpoint_components.csv"].append(
            {
                "run_id": source_run_id,
                "viewpoint_guid": viewpoint_guid,
                "topic_guid": topic_guid,
                "component_index": 1,
                "model_id": model_id,
                "element_key": element_key,
                "global_id": element["global_id"],
                "originating_system": "EPC Digital Delivery Control Tower",
                "authoring_tool_id": element["global_id"],
            }
        )
        sidecar_rows["bcf_topic_events.csv"].append(
            {
                "run_id": source_run_id,
                "event_id": uuid5_from_values("bcf-topic-event", [topic_guid, "created"]),
                "topic_guid": topic_guid,
                "event_type": "topic_created",
                "event_date": FIXED_TIMESTAMP,
                "event_author": CREATION_AUTHOR,
                "value": "",
                "source": "ANALYTICS_SIDECAR",
            }
        )

    for name, rows in sidecar_rows.items():
        columns = SIDECAR_COLUMNS[name]
        rows.sort(key=lambda row: tuple(str(row[column]) for column in columns))

    validate_xml_schemas(entries, schema_dir)
    bcf_bytes = build_deterministic_zip(entries)
    sidecar_bytes = {
        name: write_csv_bytes(sidecar_rows[name], columns)
        for name, columns in SIDECAR_COLUMNS.items()
    }
    return WorkflowArtifacts(
        source_run_id=source_run_id,
        bcf_entries=entries,
        bcf_bytes=bcf_bytes,
        sidecar_rows=sidecar_rows,
        sidecar_bytes=sidecar_bytes,
    )


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unknown"


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

    output_paths = {
        "ids_failures.bcf": bcf_output,
        **{
            filename: sidecar_dir / filename
            for filename in SIDECAR_COLUMNS
        },
    }
    for path in [*output_paths.values(), manifest_output]:
        repo_relative(path)

    _atomic_write(bcf_output, artifacts.bcf_bytes)
    for filename, data in artifacts.sidecar_bytes.items():
        _atomic_write(sidecar_dir / filename, data)

    hvac_model = next(
        row for row in read_csv_rows(models_path) if row["model_id"] == "hvac"
    )
    input_paths = [
        findings_path,
        models_path,
        inventory_path,
        ids_path,
        raw_data_dir / hvac_model["filename"],
    ]
    manifest: dict[str, object] = {
        "manifest_version": "0.1",
        "pipeline": "ids-failures-to-bcf-3.0",
        "run_id": artifacts.source_run_id,
        "generated_at": FIXED_TIMESTAMP,
        "bcf_version": BCF_VERSION,
        "project_guid": PROJECT_GUID,
        "generator": "stdlib-xml-zipfile",
        "dependencies": {
            "ifcopenshell": _package_version("ifcopenshell"),
            "xmlschema": _package_version("xmlschema"),
        },
        "schema_bundle": {
            "repository": "buildingSMART/BCF-XML",
            "commit": OFFICIAL_SCHEMA_COMMIT,
            "path": repo_relative(schema_dir),
            "files": verify_schema_bundle(schema_dir),
        },
        "counts": {
            "topics": len(artifacts.sidecar_rows["bcf_topics.csv"]),
            "topic_findings": len(
                artifacts.sidecar_rows["bcf_topic_findings.csv"]
            ),
            "viewpoints": len(artifacts.sidecar_rows["bcf_viewpoints.csv"]),
            "viewpoint_components": len(
                artifacts.sidecar_rows["bcf_viewpoint_components.csv"]
            ),
            "topic_events": len(artifacts.sidecar_rows["bcf_topic_events.csv"]),
        },
        "inputs": [
            {
                "path": repo_relative(path),
                "sha256": calculate_sha256(path),
                **(
                    {"rows": len(read_csv_rows(path))}
                    if path.suffix.lower() == ".csv"
                    else {}
                ),
            }
            for path in input_paths
        ],
        "outputs": [
            {
                "path": repo_relative(path),
                "sha256": calculate_sha256(path),
                "bytes": path.stat().st_size,
                **(
                    {"rows": len(artifacts.sidecar_rows[path.name])}
                    if path.suffix.lower() == ".csv"
                    else {}
                ),
            }
            for path in output_paths.values()
        ],
    }
    manifest_bytes = (
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    _atomic_write(manifest_output, manifest_bytes)
    return manifest


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
