"""Validate the deterministic BCF 3.0 package and its analytical sidecars."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import ifcopenshell

from bcf_common import (
    ASSIGNEE,
    BCF_VERSION,
    CREATION_AUTHOR,
    FINDING_URN_PREFIX,
    FIXED_TIMESTAMP,
    IFC_GUID_PATTERN,
    OFFICIAL_SCHEMA_COMMIT,
    OFFICIAL_SCHEMA_SHA256,
    PROJECT_GUID,
    PROJECT_ROOT,
    SCHEMA_DIR,
    UUID_PATTERN,
    Aabb,
    Camera,
    calculate_sha256,
    camera_for_aabb,
    enrich_finding_identity,
    format_float,
    parse_xml,
    read_csv_rows,
    read_safe_zip,
    repo_relative,
    validate_xml_schemas,
    verify_camera_frames_aabb,
    verify_schema_bundle,
    world_coordinate_aabb,
)
from identity import uuid5_from_values


FINDINGS_PATH = PROJECT_ROOT / "data" / "processed" / "ids_findings.csv"
MODELS_PATH = PROJECT_ROOT / "data" / "processed" / "models.csv"
INVENTORY_PATH = PROJECT_ROOT / "data" / "processed" / "model_inventory.csv"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
IDS_PATH = PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"
BCF_PATH = PROJECT_ROOT / "reports" / "bcf" / "ids_failures.bcf"
MANIFEST_PATH = PROJECT_ROOT / "reports" / "bcf" / "run_manifest.json"
SIDECAR_DIR = PROJECT_ROOT / "data" / "processed"

EXPECTED_SIDECAR_COLUMNS = {
    "bcf_topics.csv": [
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
    ],
    "bcf_topic_findings.csv": [
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
    ],
    "bcf_viewpoints.csv": [
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
    ],
    "bcf_viewpoint_components.csv": [
        "run_id",
        "viewpoint_guid",
        "topic_guid",
        "component_index",
        "model_id",
        "element_key",
        "global_id",
        "originating_system",
        "authoring_tool_id",
    ],
    "bcf_topic_events.csv": [
        "run_id",
        "event_id",
        "topic_guid",
        "event_type",
        "event_date",
        "event_author",
        "value",
        "source",
    ],
}

EXPECTED_COUNTS = {
    "bcf_topics.csv": 3,
    "bcf_topic_findings.csv": 6,
    "bcf_viewpoints.csv": 3,
    "bcf_viewpoint_components.csv": 3,
    "bcf_topic_events.csv": 3,
}


def _required_text(parent: ET.Element, path: str, source: str) -> str:
    node = parent.find(path)
    if node is None or node.text is None or not node.text.strip():
        raise ValueError(f"Missing {path} in {source}")
    return node.text.strip()


def _parse_vector(parent: ET.Element, path: str, source: str) -> tuple[float, float, float]:
    node = parent.find(path)
    if node is None:
        raise ValueError(f"Missing {path} in {source}")
    values = tuple(float(_required_text(node, axis, source)) for axis in ("X", "Y", "Z"))
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"Non-finite vector in {source}: {path}")
    return values


def load_bcf_package(
    bcf_path: Path,
    schema_dir: Path = SCHEMA_DIR,
) -> dict[str, Any]:
    """Securely reload a BCF package, run XSD validation, and extract semantics."""

    entries = read_safe_zip(bcf_path)
    validate_xml_schemas(entries, schema_dir)
    for required in ("bcf.version", "extensions.xml", "project.bcfp"):
        if required not in entries:
            raise ValueError(f"Missing required BCF entry: {required}")

    version_root = parse_xml(entries["bcf.version"], "bcf.version")
    if version_root.tag != "Version" or version_root.get("VersionId") != BCF_VERSION:
        raise ValueError("The archive is not BCF XML 3.0")

    project_root = parse_xml(entries["project.bcfp"], "project.bcfp")
    project = project_root.find("Project")
    if (
        project_root.tag != "ProjectInfo"
        or project is None
        or project.get("ProjectId") != PROJECT_GUID
    ):
        raise ValueError("Unexpected BCF project identity")

    extensions = parse_xml(entries["extensions.xml"], "extensions.xml")
    if extensions.tag != "Extensions":
        raise ValueError("Invalid extensions.xml root")
    expected_extensions = {
        "TopicTypes/TopicType": ["Issue"],
        "TopicStatuses/TopicStatus": ["Open"],
        "Priorities/Priority": ["Medium"],
        "TopicLabels/TopicLabel": ["HVAC", "IDS", "ProjectAssumption"],
        "Users/User": [ASSIGNEE, CREATION_AUTHOR],
        "Stages/Stage": ["Coordination"],
    }
    for path, expected in expected_extensions.items():
        actual = [node.text for node in extensions.findall(path)]
        if actual != expected:
            raise ValueError(f"Unexpected BCF extension values for {path}: {actual}")

    directory_names = {
        name[:-1] for name in entries if name.endswith("/")
    }
    markup_names = sorted(
        name for name in entries if name.endswith("/markup.bcf")
    )
    if len(directory_names) != 3 or len(markup_names) != 3:
        raise ValueError("Expected exactly 3 explicit topic directories and markups")

    topics: dict[str, dict[str, Any]] = {}
    recognized = {"bcf.version", "extensions.xml", "project.bcfp"}
    recognized.update(f"{name}/" for name in directory_names)
    for markup_name in markup_names:
        topic_dir = markup_name.split("/", 1)[0]
        if topic_dir not in directory_names or not UUID_PATTERN.fullmatch(topic_dir):
            raise ValueError(f"Invalid or implicit BCF topic directory: {topic_dir}")
        root = parse_xml(entries[markup_name], markup_name)
        if root.tag != "Markup":
            raise ValueError(f"Invalid markup root: {markup_name}")
        header_files = root.findall("Header/Files/File")
        if len(header_files) != 1:
            raise ValueError(f"Topic must have exactly one Header File: {topic_dir}")
        header_file = header_files[0]
        reference_node = header_file.find("Reference")
        if reference_node is not None:
            raise ValueError(f"BCF Header Reference must be omitted: {topic_dir}")
        header = {
            "ifc_project_guid": header_file.get("IfcProject"),
            "is_external": header_file.get("IsExternal"),
            "filename": _required_text(header_file, "Filename", markup_name),
            "date": _required_text(header_file, "Date", markup_name),
            "reference": None,
        }
        topic = root.find("Topic")
        if topic is None or topic.get("Guid") != topic_dir:
            raise ValueError(f"Topic Guid does not match its directory: {topic_dir}")
        if topic.get("TopicType") != "Issue" or topic.get("TopicStatus") != "Open":
            raise ValueError(f"Unexpected topic type/status: {topic_dir}")
        if _required_text(topic, "CreationDate", markup_name) != FIXED_TIMESTAMP:
            raise ValueError(f"Non-deterministic topic timestamp: {topic_dir}")
        if _required_text(topic, "CreationAuthor", markup_name) != CREATION_AUTHOR:
            raise ValueError(f"Unexpected topic author: {topic_dir}")
        description = _required_text(topic, "Description", markup_name)
        if not description.startswith("Project-assumed information requirement unmet"):
            raise ValueError(f"Topic description overstates model noncompliance: {topic_dir}")

        links = [
            node.text.strip()
            for node in topic.findall("ReferenceLinks/ReferenceLink")
            if node.text
        ]
        if len(links) != 2 or len(set(links)) != 2:
            raise ValueError(f"Topic must have exactly 2 unique finding links: {topic_dir}")
        for link in links:
            if not link.startswith(FINDING_URN_PREFIX) or not UUID_PATTERN.fullmatch(
                link.removeprefix(FINDING_URN_PREFIX)
            ):
                raise ValueError(f"Invalid finding lineage link: {link}")

        viewpoint_refs = topic.findall("Viewpoints/ViewPoint")
        if len(viewpoint_refs) != 1:
            raise ValueError(f"Topic must have exactly 1 viewpoint: {topic_dir}")
        viewpoint_ref = viewpoint_refs[0]
        viewpoint_guid = viewpoint_ref.get("Guid") or ""
        viewpoint_filename = _required_text(
            viewpoint_ref,
            "Viewpoint",
            markup_name,
        )
        if (
            not UUID_PATTERN.fullmatch(viewpoint_guid)
            or viewpoint_filename != f"{viewpoint_guid}.bcfv"
            or viewpoint_ref.find("Snapshot") is not None
        ):
            raise ValueError(f"Invalid viewpoint reference: {topic_dir}")
        viewpoint_path = f"{topic_dir}/{viewpoint_filename}"
        if viewpoint_path not in entries:
            raise ValueError(f"Missing viewpoint payload: {viewpoint_path}")
        viewpoint_root = parse_xml(entries[viewpoint_path], viewpoint_path)
        if (
            viewpoint_root.tag != "VisualizationInfo"
            or viewpoint_root.get("Guid") != viewpoint_guid
        ):
            raise ValueError(f"Viewpoint Guid mismatch: {viewpoint_path}")
        components = viewpoint_root.findall("Components/Selection/Component")
        if len(components) != 1:
            raise ValueError(f"Viewpoint must select exactly 1 component: {viewpoint_path}")
        global_id = components[0].get("IfcGuid") or ""
        if not IFC_GUID_PATTERN.fullmatch(global_id):
            raise ValueError(f"Invalid BCF component IFC Guid: {global_id!r}")
        visibility = viewpoint_root.find("Components/Visibility")
        if visibility is None or visibility.get("DefaultVisibility") != "true":
            raise ValueError(f"Unexpected component visibility: {viewpoint_path}")
        camera_node = viewpoint_root.find("PerspectiveCamera")
        if camera_node is None or viewpoint_root.find("OrthogonalCamera") is not None:
            raise ValueError(f"Expected one perspective camera: {viewpoint_path}")
        camera = Camera(
            position=_parse_vector(camera_node, "CameraViewPoint", viewpoint_path),
            direction=_parse_vector(camera_node, "CameraDirection", viewpoint_path),
            up=_parse_vector(camera_node, "CameraUpVector", viewpoint_path),
            target=(0.0, 0.0, 0.0),
            field_of_view=float(
                _required_text(camera_node, "FieldOfView", viewpoint_path)
            ),
            aspect_ratio=float(
                _required_text(camera_node, "AspectRatio", viewpoint_path)
            ),
        )
        if not 0 < camera.field_of_view < 180 or camera.aspect_ratio <= 0:
            raise ValueError(f"Invalid perspective camera values: {viewpoint_path}")

        topics[topic_dir] = {
            "topic_guid": topic_dir,
            "topic_type": topic.get("TopicType"),
            "topic_status": topic.get("TopicStatus"),
            "title": _required_text(topic, "Title", markup_name),
            "priority": _required_text(topic, "Priority", markup_name),
            "creation_date": _required_text(topic, "CreationDate", markup_name),
            "creation_author": _required_text(topic, "CreationAuthor", markup_name),
            "assigned_to": _required_text(topic, "AssignedTo", markup_name),
            "stage": _required_text(topic, "Stage", markup_name),
            "description": description,
            "header": header,
            "finding_keys": [
                link.removeprefix(FINDING_URN_PREFIX) for link in links
            ],
            "viewpoint_guid": viewpoint_guid,
            "viewpoint_filename": viewpoint_filename,
            "global_id": global_id,
            "originating_system": _required_text(
                components[0], "OriginatingSystem", viewpoint_path
            ),
            "authoring_tool_id": _required_text(
                components[0], "AuthoringToolId", viewpoint_path
            ),
            "camera": camera,
        }
        recognized.update({markup_name, viewpoint_path})

    unexpected = set(entries) - recognized
    if unexpected:
        raise ValueError(f"Unexpected BCF archive entries: {sorted(unexpected)}")
    return {
        "version": BCF_VERSION,
        "project_guid": PROJECT_GUID,
        "topics": topics,
        "entries": entries,
    }


def _read_sidecar(path: Path, expected_columns: list[str]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != expected_columns:
            raise ValueError(
                f"Unexpected columns in {path.name}: {reader.fieldnames}"
            )
        rows = list(reader)
    return rows


def _load_sidecars(sidecar_dir: Path) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    for name, columns in EXPECTED_SIDECAR_COLUMNS.items():
        rows = _read_sidecar(sidecar_dir / name, columns)
        if len(rows) != EXPECTED_COUNTS[name]:
            raise ValueError(
                f"Expected {EXPECTED_COUNTS[name]} rows in {name}, found {len(rows)}"
            )
        if rows != sorted(
            rows,
            key=lambda row: tuple(row[column] for column in columns),
        ):
            raise ValueError(f"Sidecar rows are not deterministically ordered: {name}")
        result[name] = rows
    return result


def _json_without_duplicate_keys(path: Path) -> dict[str, Any]:
    def reject_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key in manifest: {key}")
            result[key] = value
        return result

    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicates,
        )
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid run manifest: {error}") from error


def _validate_manifest(
    manifest_path: Path,
    bcf_path: Path,
    sidecar_dir: Path,
    findings_path: Path,
    models_path: Path,
    inventory_path: Path,
    raw_data_dir: Path,
    ids_path: Path,
    schema_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    manifest = _json_without_duplicate_keys(manifest_path)
    if manifest.get("run_id") != run_id or manifest.get("bcf_version") != BCF_VERSION:
        raise ValueError("Manifest run/version does not match the BCF workflow")
    if manifest.get("generated_at") != FIXED_TIMESTAMP:
        raise ValueError("Manifest timestamp is not deterministic")
    if manifest.get("project_guid") != PROJECT_GUID:
        raise ValueError("Manifest project Guid mismatch")

    bundle = manifest.get("schema_bundle", {})
    if (
        bundle.get("commit") != OFFICIAL_SCHEMA_COMMIT
        or bundle.get("files") != OFFICIAL_SCHEMA_SHA256
        or bundle.get("path") != repo_relative(schema_dir)
    ):
        raise ValueError("Manifest does not identify the pinned BCF XSD bundle")

    hvac_model = next(
        row for row in read_csv_rows(models_path) if row["model_id"] == "hvac"
    )
    expected_inputs = {
        repo_relative(path): path
        for path in (
            findings_path,
            models_path,
            inventory_path,
            ids_path,
            raw_data_dir / hvac_model["filename"],
        )
    }
    input_records = manifest.get("inputs")
    if not isinstance(input_records, list):
        raise ValueError("Manifest inputs must be a list")
    actual_inputs = {record.get("path"): record for record in input_records}
    if len(actual_inputs) != len(input_records) or set(actual_inputs) != set(expected_inputs):
        raise ValueError("Manifest input paths do not match the workflow inputs")
    for relative_path, path in expected_inputs.items():
        if actual_inputs[relative_path].get("sha256") != calculate_sha256(path):
            raise ValueError(f"Manifest input hash mismatch: {relative_path}")

    expected_outputs = {
        repo_relative(path): path
        for path in (
            bcf_path,
            *(sidecar_dir / name for name in EXPECTED_SIDECAR_COLUMNS),
        )
    }
    output_records = manifest.get("outputs")
    if not isinstance(output_records, list):
        raise ValueError("Manifest outputs must be a list")
    actual_outputs = {record.get("path"): record for record in output_records}
    if repo_relative(manifest_path) in actual_outputs:
        raise ValueError("Manifest must not contain its own SHA-256")
    if len(actual_outputs) != len(output_records) or set(actual_outputs) != set(expected_outputs):
        raise ValueError("Manifest output paths do not match generated artifacts")
    for relative_path, path in expected_outputs.items():
        record = actual_outputs[relative_path]
        if record.get("sha256") != calculate_sha256(path):
            raise ValueError(f"Manifest output hash mismatch: {relative_path}")
        if record.get("bytes") != path.stat().st_size:
            raise ValueError(f"Manifest output size mismatch: {relative_path}")
        if path.suffix.lower() == ".csv":
            expected_rows = EXPECTED_COUNTS[path.name]
            if record.get("rows") != expected_rows:
                raise ValueError(f"Manifest output row count mismatch: {relative_path}")

    if manifest.get("counts") != {
        "topics": 3,
        "topic_findings": 6,
        "viewpoints": 3,
        "viewpoint_components": 3,
        "topic_events": 3,
    }:
        raise ValueError("Manifest counts do not match the required workflow")
    return manifest


def _float_tuple(row: dict[str, str], prefix: str) -> tuple[float, float, float]:
    values = tuple(float(row[f"{prefix}_{axis}"]) for axis in ("x", "y", "z"))
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"Non-finite sidecar vector: {prefix}")
    return values


def validate_bcf_workflow(
    bcf_path: Path = BCF_PATH,
    findings_path: Path = FINDINGS_PATH,
    models_path: Path = MODELS_PATH,
    inventory_path: Path = INVENTORY_PATH,
    raw_data_dir: Path = RAW_DATA_DIR,
    sidecar_dir: Path = SIDECAR_DIR,
    manifest_path: Path = MANIFEST_PATH,
    ids_path: Path = IDS_PATH,
    schema_dir: Path = SCHEMA_DIR,
) -> dict[str, Any]:
    """Validate BCF/XSD semantics, lineage, IFC geometry, sidecars, and hashes."""

    verify_schema_bundle(schema_dir)
    package = load_bcf_package(bcf_path, schema_dir)
    sidecars = _load_sidecars(sidecar_dir)
    source_findings = read_csv_rows(findings_path)
    if len(source_findings) != 47:
        raise ValueError(
            f"Expected 47 source IDS findings, found {len(source_findings)}"
        )
    status_counts = Counter(row.get("status") for row in source_findings)
    if status_counts != Counter({"PASS": 25, "N/A": 16, "FAIL": 6}):
        raise ValueError(f"Unexpected source IDS status counts: {status_counts}")
    applicable_count = sum(
        row.get("is_applicable") == "true"
        if "is_applicable" in row
        else row.get("status") != "N/A"
        for row in source_findings
    )
    if applicable_count != 31:
        raise ValueError(
            f"Expected 31 applicable IDS checks, found {applicable_count}"
        )
    fail_findings = [
        enrich_finding_identity(row)
        for row in source_findings
        if row.get("status") == "FAIL"
    ]
    if len(fail_findings) != 6:
        raise ValueError("Source findings no longer contain exactly 6 FAIL rows")
    run_ids = {row["run_id"] for row in fail_findings}
    if len(run_ids) != 1:
        raise ValueError("FAIL findings span multiple IDS runs")
    run_id = next(iter(run_ids))
    if any(
        row["run_id"] != run_id
        for rows in sidecars.values()
        for row in rows
    ):
        raise ValueError("A BCF sidecar has the wrong run_id")

    model_rows = read_csv_rows(models_path)
    inventory_rows = read_csv_rows(inventory_path)
    if len(model_rows) != 3 or len({row["model_id"] for row in model_rows}) != 3:
        raise ValueError("Expected exactly 3 uniquely identified source models")
    if (
        len(inventory_rows) != 39
        or len({row["element_key"] for row in inventory_rows}) != 39
    ):
        raise ValueError("Expected exactly 39 uniquely identified inventory elements")
    models = {row["model_id"]: row for row in model_rows}
    inventory = {row["element_key"]: row for row in inventory_rows}
    topics = {row["topic_guid"]: row for row in sidecars["bcf_topics.csv"]}
    topic_findings = sidecars["bcf_topic_findings.csv"]
    viewpoints = {
        row["viewpoint_guid"]: row
        for row in sidecars["bcf_viewpoints.csv"]
    }
    components = sidecars["bcf_viewpoint_components.csv"]
    events = sidecars["bcf_topic_events.csv"]

    if set(topics) != set(package["topics"]):
        raise ValueError("BCF topic GUIDs and topic sidecar GUIDs differ")
    source_by_key = {row["finding_key"]: row for row in fail_findings}
    if len(source_by_key) != 6:
        raise ValueError("Source FAIL finding keys are not unique")
    sidecar_by_key = {row["finding_key"]: row for row in topic_findings}
    if set(sidecar_by_key) != set(source_by_key):
        raise ValueError("Topic/finding bridge does not cover all 6 FAIL findings")

    ifc_cache: dict[str, ifcopenshell.file] = {}
    for topic_guid, topic_row in topics.items():
        element_key = topic_row["element_key"]
        element = inventory.get(element_key)
        if element is None:
            raise ValueError(f"Topic refers to unknown element: {element_key}")
        expected_topic_guid = uuid5_from_values("bcf-topic", [element_key])
        expected_viewpoint_guid = uuid5_from_values(
            "bcf-viewpoint",
            [expected_topic_guid],
        )
        if topic_guid != expected_topic_guid:
            raise ValueError(f"Topic Guid is not the expected UUIDv5: {topic_guid}")
        native_topic = package["topics"][topic_guid]
        for key in (
            "topic_type",
            "topic_status",
            "title",
            "priority",
            "creation_date",
            "creation_author",
            "assigned_to",
            "stage",
        ):
            if topic_row[key] != native_topic[key]:
                raise ValueError(f"Topic sidecar/native mismatch for {topic_guid}: {key}")
        if topic_row["finding_count"] != "2":
            raise ValueError(f"Topic finding_count is not 2: {topic_guid}")
        bridged = [row for row in topic_findings if row["topic_guid"] == topic_guid]
        if len(bridged) != 2:
            raise ValueError(f"Topic does not bridge exactly 2 findings: {topic_guid}")
        if {row["finding_key"] for row in bridged} != set(
            native_topic["finding_keys"]
        ):
            raise ValueError(f"Native BCF finding links disagree with sidecar: {topic_guid}")
        for bridge in bridged:
            source = source_by_key[bridge["finding_key"]]
            for key in (
                "run_id",
                "requirement_key",
                "specification_id",
                "requirement_id",
                "specification",
                "requirement",
                "severity",
                "model_id",
                "element_key",
                "global_id",
            ):
                if bridge[key] != source[key]:
                    raise ValueError(
                        f"Finding lineage mismatch for {bridge['finding_key']}: {key}"
                    )

        ordered_requirements = ", ".join(
            source_by_key[key]["requirement"]
            for key in native_topic["finding_keys"]
        )
        expected_description = (
            "Project-assumed information requirement unmet for "
            f"{element_key}. Required checks: {ordered_requirements}. "
            "This workflow classification does not assert a defect in the source model."
        )
        if native_topic["description"] != expected_description:
            raise ValueError(f"Unexpected project-assumption wording: {topic_guid}")

        viewpoint_guid = native_topic["viewpoint_guid"]
        if viewpoint_guid != expected_viewpoint_guid or viewpoint_guid not in viewpoints:
            raise ValueError(f"Missing deterministic viewpoint: {topic_guid}")
        viewpoint = viewpoints[viewpoint_guid]
        component_rows = [
            row for row in components if row["viewpoint_guid"] == viewpoint_guid
        ]
        if len(component_rows) != 1 or component_rows[0]["component_index"] != "1":
            raise ValueError(f"Expected one indexed component: {viewpoint_guid}")
        component = component_rows[0]
        for key in ("topic_guid", "model_id", "element_key", "global_id"):
            if component[key] != topic_row[key] or viewpoint[key] != topic_row[key]:
                raise ValueError(f"Viewpoint/component foreign key mismatch: {key}")
        if native_topic["global_id"] != element["global_id"]:
            raise ValueError(f"BCF component does not select its topic element: {topic_guid}")
        if component["global_id"] != native_topic["global_id"]:
            raise ValueError(f"Component sidecar/native mismatch: {viewpoint_guid}")
        if (
            component["originating_system"] != native_topic["originating_system"]
            or component["authoring_tool_id"] != native_topic["authoring_tool_id"]
        ):
            raise ValueError(f"Component metadata mismatch: {viewpoint_guid}")

        model_id = element["model_id"]
        model_row = models.get(model_id)
        if model_row is None:
            raise ValueError(f"Unknown model for BCF component: {model_id}")
        if native_topic["header"] != {
            "ifc_project_guid": model_row["ifc_project_guid"],
            "is_external": "true",
            "filename": model_row["filename"],
            "date": FIXED_TIMESTAMP,
            "reference": None,
        }:
            raise ValueError(f"BCF Header does not reference its IFC model: {topic_guid}")
        ifc_path = raw_data_dir / model_row["filename"]
        if calculate_sha256(ifc_path) != model_row["content_sha256"]:
            raise ValueError(f"IFC content hash mismatch: {ifc_path}")
        model = ifc_cache.setdefault(model_id, ifcopenshell.open(str(ifc_path)))
        aabb = world_coordinate_aabb(model, element["global_id"])
        expected_camera = camera_for_aabb(aabb)

        expected_sidecar_values = {}
        for prefix, values in (
            ("aabb_min", aabb.minimum),
            ("aabb_max", aabb.maximum),
            ("target", expected_camera.target),
            ("camera_view_point", expected_camera.position),
            ("camera_direction", expected_camera.direction),
            ("camera_up", expected_camera.up),
        ):
            for axis, value in zip(("x", "y", "z"), values, strict=True):
                expected_sidecar_values[f"{prefix}_{axis}"] = format_float(value)
        expected_sidecar_values["field_of_view"] = format_float(
            expected_camera.field_of_view
        )
        expected_sidecar_values["aspect_ratio"] = format_float(
            expected_camera.aspect_ratio
        )
        for key, expected in expected_sidecar_values.items():
            if viewpoint[key] != expected:
                raise ValueError(f"Viewpoint geometry mismatch for {viewpoint_guid}: {key}")

        native_camera = native_topic["camera"]
        serialized_camera = Camera(
            position=_float_tuple(viewpoint, "camera_view_point"),
            direction=_float_tuple(viewpoint, "camera_direction"),
            up=_float_tuple(viewpoint, "camera_up"),
            target=_float_tuple(viewpoint, "target"),
            field_of_view=float(viewpoint["field_of_view"]),
            aspect_ratio=float(viewpoint["aspect_ratio"]),
        )
        for left, right in (
            (native_camera.position, serialized_camera.position),
            (native_camera.direction, serialized_camera.direction),
            (native_camera.up, serialized_camera.up),
        ):
            if any(abs(a - b) > 1e-9 for a, b in zip(left, right, strict=True)):
                raise ValueError(f"Native/sidecar camera mismatch: {viewpoint_guid}")
        if (
            abs(native_camera.field_of_view - serialized_camera.field_of_view) > 1e-9
            or abs(native_camera.aspect_ratio - serialized_camera.aspect_ratio) > 1e-9
        ):
            raise ValueError(f"Native/sidecar camera lens mismatch: {viewpoint_guid}")
        serialized_aabb = Aabb(
            minimum=_float_tuple(viewpoint, "aabb_min"),
            maximum=_float_tuple(viewpoint, "aabb_max"),
        )
        verify_camera_frames_aabb(serialized_aabb, serialized_camera)
        aim = tuple(
            target - origin
            for target, origin in zip(
                serialized_camera.target,
                serialized_camera.position,
                strict=True,
            )
        )
        aim_length = math.sqrt(sum(value * value for value in aim))
        aim_unit = tuple(value / aim_length for value in aim)
        if any(
            abs(a - b) > 2e-6
            for a, b in zip(
                aim_unit,
                serialized_camera.direction,
                strict=True,
            )
        ):
            raise ValueError(f"Camera does not aim at AABB centre: {viewpoint_guid}")

        topic_events = [row for row in events if row["topic_guid"] == topic_guid]
        if len(topic_events) != 1:
            raise ValueError(f"Expected one topic_created sidecar event: {topic_guid}")
        event = topic_events[0]
        if event != {
            "run_id": run_id,
            "event_id": uuid5_from_values("bcf-topic-event", [topic_guid, "created"]),
            "topic_guid": topic_guid,
            "event_type": "topic_created",
            "event_date": FIXED_TIMESTAMP,
            "event_author": CREATION_AUTHOR,
            "value": "",
            "source": "ANALYTICS_SIDECAR",
        }:
            raise ValueError(f"Invalid analytical topic event: {topic_guid}")

    manifest = _validate_manifest(
        manifest_path,
        bcf_path,
        sidecar_dir,
        findings_path,
        models_path,
        inventory_path,
        raw_data_dir,
        ids_path,
        schema_dir,
        run_id,
    )
    return {
        "bcf_version": package["version"],
        "run_id": run_id,
        "topics": len(topics),
        "viewpoints": len(viewpoints),
        "components": len(components),
        "finding_links": len(topic_findings),
        "manifest": manifest,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bcf", type=Path, default=BCF_PATH)
    parser.add_argument("--findings", type=Path, default=FINDINGS_PATH)
    parser.add_argument("--models", type=Path, default=MODELS_PATH)
    parser.add_argument("--inventory", type=Path, default=INVENTORY_PATH)
    parser.add_argument("--raw-data-dir", type=Path, default=RAW_DATA_DIR)
    parser.add_argument("--sidecar-dir", type=Path, default=SIDECAR_DIR)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--ids", type=Path, default=IDS_PATH)
    parser.add_argument("--schema-dir", type=Path, default=SCHEMA_DIR)
    arguments = parser.parse_args()
    result = validate_bcf_workflow(
        bcf_path=arguments.bcf,
        findings_path=arguments.findings,
        models_path=arguments.models,
        inventory_path=arguments.inventory,
        raw_data_dir=arguments.raw_data_dir,
        sidecar_dir=arguments.sidecar_dir,
        manifest_path=arguments.manifest,
        ids_path=arguments.ids,
        schema_dir=arguments.schema_dir,
    )
    print(
        "Validated BCF 3.0: "
        f"{result['topics']} topics, "
        f"{result['viewpoints']} viewpoints, "
        f"{result['components']} components, "
        f"{result['finding_links']} finding links"
    )
    print(f"BCF SHA-256: {calculate_sha256(arguments.bcf)}")


if __name__ == "__main__":
    main()
