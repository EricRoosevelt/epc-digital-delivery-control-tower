"""Fail-closed static validation for the committed Power BI Project definitions."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter, deque
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
DEFAULT_PROJECT_NAME = "EPCDeliveryControlTower"
DEFAULT_ACCEPTANCE_MANIFEST = (
    PROJECT_ROOT / "docs" / "evidence" / "stage_3b" / "acceptance_manifest.json"
)
EXPECTED_RUN_ID = "ids-v0.1-8706ef58303bfd11"
DATA_SNAPSHOT_PATHS = {
    "ids_findings_sha256": PROJECT_ROOT / "data" / "processed" / "ids_findings.csv",
    "bcf_sha256": PROJECT_ROOT / "reports" / "bcf" / "ids_failures.bcf",
    "bcf_run_manifest_sha256": PROJECT_ROOT / "reports" / "bcf" / "run_manifest.json",
}

EXPECTED_TABLES = (
    "DimModel",
    "DimElement",
    "DimRequirement",
    "DimRun",
    "FactIDSCheck",
    "FactRequirementCoverage",
    "DimTopic",
    "BridgeTopicFinding",
    "BridgeViewpointComponent",
)
BRIDGE_TABLES = frozenset({"BridgeTopicFinding", "BridgeViewpointComponent"})

EXPECTED_RELATIONSHIPS = {
    "DimModel_DimElement": (
        "DimElement.model_id",
        "DimModel.model_id",
        "oneDirection",
    ),
    "DimModel_FactRequirementCoverage": (
        "FactRequirementCoverage.model_id",
        "DimModel.model_id",
        "oneDirection",
    ),
    "DimRun_FactIDSCheck": (
        "FactIDSCheck.run_id",
        "DimRun.run_id",
        "oneDirection",
    ),
    "DimRun_FactRequirementCoverage": (
        "FactRequirementCoverage.run_id",
        "DimRun.run_id",
        "oneDirection",
    ),
    "DimRequirement_FactIDSCheck": (
        "FactIDSCheck.requirement_key",
        "DimRequirement.requirement_key",
        "oneDirection",
    ),
    "DimRequirement_FactRequirementCoverage": (
        "FactRequirementCoverage.requirement_key",
        "DimRequirement.requirement_key",
        "oneDirection",
    ),
    "DimElement_FactIDSCheck": (
        "FactIDSCheck.element_key",
        "DimElement.element_key",
        "bothDirections",
    ),
    "DimElement_DimTopic": (
        "DimTopic.element_key",
        "DimElement.element_key",
        "bothDirections",
    ),
}

EXPECTED_KPI_SIGNATURES = {
    "Total Elements": ("DISTINCTCOUNT", "DimElement[element_key]"),
    "Evaluated Elements": ("DISTINCTCOUNT", "FactIDSCheck[element_key]"),
    "Applicable Check Pass Rate": (
        "DIVIDE",
        "COALESCE",
        "[Passed Checks]",
        "[Applicable Checks]",
    ),
    "Failed Checks": (
        "CALCULATE",
        "COUNTROWS",
        "FactIDSCheck",
        "FactIDSCheck[status]",
        '"FAIL"',
    ),
    "Noncompliant Elements": (
        "CALCULATE",
        "DISTINCTCOUNT",
        "FactIDSCheck[element_key]",
        "FactIDSCheck[status]",
        '"FAIL"',
    ),
    "BCF Lineage Coverage": (
        "DIVIDE",
        "[BCF Linked Findings]",
        "[Failed Checks]",
    ),
    "Open Topics": (
        "CALCULATE",
        "DISTINCTCOUNT",
        "DimTopic[topic_guid]",
        "DimTopic[topic_status]",
        '"Open"',
    ),
}

EXPECTED_VISUAL_COUNTS = Counter(
    {
        "cardVisual": 7,
        "clusteredColumnChart": 2,
        "tableEx": 2,
        "slicer": 4,
        "specklePowerBiVisual": 1,
    }
)
EXPECTED_SLICER_BINDINGS = {
    ("DimModel", "discipline_label"): "Discipline",
    ("DimRequirement", "specification_id"): "Rule",
    ("DimTopic", "priority"): "Priority",
    ("DimTopic", "assigned_to"): "Assignee",
}
EXPECTED_TOPIC_TABLE_BINDINGS = {
    ("DimTopic", "title"),
    ("DimTopic", "ifc_class"),
    ("DimTopic", "element_name"),
    ("DimTopic", "priority"),
    ("DimTopic", "assigned_to"),
}
EXPECTED_QUERY_ORDER = (
    "RepositoryRoot",
    "LoadProjectCsv",
    "SpeckleConnectionManifest",
    "GetSpeckleModelUrl",
    "NormalizeSpeckleModel",
    "SpeckleElementStage",
    "DimModel",
    "DimElement",
    "DimRequirement",
    "DimRun",
    "FactIDSCheck",
    "FactRequirementCoverage",
    "DimTopic",
    "BridgeTopicFinding",
    "BridgeViewpointComponent",
)
EXPECTED_TOPIC_MAPPINGS = {
    "7fe29ad3-674a-57fe-aa74-325e34053ffc": "hvac::34Y6EIt3nDCAS1k$kPGOKm",
    "be0ef29b-2855-5f97-b60e-466abc66252d": "hvac::38WbwIGD90nB_3T2BTU5Ed",
    "dbfa5125-2ea0-5587-ab5b-947a02c3ba49": "hvac::23uPJWDfXEcwHH3kdFgV9c",
}
AUTODETECT_SCREENSHOT_ID = "autodetect-settings"
OVERVIEW_SCREENSHOT_ID = "final-overview"
EXPECTED_SCREENSHOT_IDS = {
    AUTODETECT_SCREENSHOT_ID,
    OVERVIEW_SCREENSHOT_ID,
    *(f"topic-{topic_guid}" for topic_guid in EXPECTED_TOPIC_MAPPINGS),
}
EXPECTED_SCREENSHOT_FILENAMES = {
    AUTODETECT_SCREENSHOT_ID: "relationship-autodetect-disabled.png",
    OVERVIEW_SCREENSHOT_ID: "overview-final.png",
    **{
        f"topic-{topic_guid}": f"topic-{topic_guid}.png"
        for topic_guid in EXPECTED_TOPIC_MAPPINGS
    },
}
RETIRED_MAPPING_QA_HASHES = {
    "434d80ca151ce8995c1d6edb57eda783d8ce0b4bd9cc200679c000527a42cafe",
    "00111b3b69d59f489e65f4c563f47fcb3938a0bd97d3eff70c9c5d6f6c73e4ab",
    "ba49f3b55f48f73a0d0d5f3be1aba0119cef0b3758e916909e7870ffb8ef3d79",
}
EXPECTED_LIFECYCLE_KEYS = {
    "refreshed",
    "saved",
    "closed",
    "reopened",
    "post_reopen_refreshed",
}
EXPECTED_FILTER_INTERACTION_KEYS = {
    f"{filter_name}_{claim}"
    for filter_name in ("rule", "topic", "priority", "assignee")
    for claim in ("filters_dim_element", "drives_speckle_visual")
}
EXPECTED_PRIVACY_KEYS = {
    "no_real_speckle_url",
    "no_account_identity",
    "no_token_or_credentials",
    "no_private_speckle_object_id",
    "no_local_absolute_path",
}
EXPECTED_OVERVIEW_RESULTS = {
    "total_elements": 39,
    "evaluated_elements": 17,
    "applicable_check_pass_rate": "80.65%",
    "failed_checks": 6,
    "noncompliant_elements": 3,
    "bcf_lineage_coverage": "100%",
    "open_topics": 3,
    "semantic_identity_mapped": 39,
    "renderable_elements": 32,
    "non_renderable_elements": 7,
    "architecture_pass_checks": 8,
    "architecture_applicable_checks": 8,
    "structural_pass_checks": 14,
    "structural_applicable_checks": 14,
    "hvac_pass_checks": 3,
    "hvac_applicable_checks": 9,
    "hvac_failed_checks": 6,
}
EXPECTED_FILTER_RESULTS = {
    "rule_r_005a": {
        "specification_id": "R-005A",
        "element_count": 1,
        "failed_check_count": 2,
    },
    "rule_r_005b": {
        "specification_id": "R-005B",
        "element_count": 2,
        "failed_check_count": 4,
    },
    "priority": {"value": "Medium", "issue_element_count": 3},
    "assignee": {
        "value": "model-coordination@example.invalid",
        "issue_element_count": 3,
    },
}

PAGE_NAME = "EPC Delivery Control Tower"
PAGE_WIDTH = 1280
PAGE_HEIGHT = 720
LOWER_HEX_ID = re.compile(r"^[0-9a-f]{20}$")
LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")
DESKTOP_VERSION = re.compile(r"^\d+(?:\.\d+){3}$")
RFC3339_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
CJK_TEXT = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
SENSITIVE_WORD = re.compile(
    r"\b(?:authorization|bearer|cookie|credential|oauth|password|secret|token)\b",
    re.IGNORECASE,
)
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
SPECKLE_URL = re.compile(r"https?://[^\s\"'<>]*speckle[^\s\"'<>]*", re.IGNORECASE)
SPECKLE_ROUTE_URL = re.compile(
    r"https?://[^\s\"'<>]+/projects/[^/\s\"'<>]+/models/[^\s\"'<>]+",
    re.IGNORECASE,
)
PINNED_VERSION_FRAGMENT = re.compile(r"@[0-9a-f]{6,64}\b", re.IGNORECASE)
HEX_LITERAL = re.compile(r"^[0-9a-f]{10,64}$", re.IGNORECASE)
QUOTED_HEX_LITERAL = re.compile(r"(?:\"([0-9a-f]{10,64})\"|'([0-9a-f]{10,64})')", re.IGNORECASE)
WINDOWS_ABSOLUTE_PATH = re.compile(r"\b[A-Z]:\\{1,2}[^\"'\r\n]+", re.IGNORECASE)
POSIX_USER_PATH = re.compile(r"/(?:Users|home)/[^/\s\"']+", re.IGNORECASE)


class PbipValidationError(ValueError):
    """Raised when a static PBIP/PBIR/TMDL invariant is violated."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PbipValidationError(message)


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise PbipValidationError(f"Required PBIP definition file is missing: {path}")
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise PbipValidationError(f"Cannot read PBIP definition text: {path}") from exc


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in pairs:
        if key in document:
            raise PbipValidationError(f"Duplicate JSON key is forbidden: {key}")
        document[key] = value
    return document


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            _read_text(path),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
    except json.JSONDecodeError as exc:
        raise PbipValidationError(f"Invalid JSON definition: {path}") from exc
    _require(isinstance(value, dict), f"JSON definition must be an object: {path}")
    return value


def _unquote_tmdl_name(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def _one_match(pattern: str, text: str, label: str) -> str:
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    _require(len(matches) == 1, f"Expected exactly one {label}, got {len(matches)}")
    return matches[0].strip()


def _definition_text_files(*definition_dirs: Path) -> list[Path]:
    files: list[Path] = []
    for definition_dir in definition_dirs:
        _require(definition_dir.is_dir(), f"Definition directory is missing: {definition_dir}")
        for path in sorted(item for item in definition_dir.rglob("*") if item.is_file()):
            _require(
                path.suffix.lower() in {".json", ".tmdl"},
                f"Unexpected non-text artifact under definition/**: {path}",
            )
            files.append(path)
    return files


def _validate_project_links(dashboard_dir: Path, project_name: str) -> tuple[Path, Path]:
    project_path = dashboard_dir / f"{project_name}.pbip"
    report_dir = dashboard_dir / f"{project_name}.Report"
    model_dir = dashboard_dir / f"{project_name}.SemanticModel"
    project = _read_json(project_path)
    _require(
        project.get("artifacts") == [{"report": {"path": report_dir.name}}],
        "PBIP must reference exactly the expected report by relative path",
    )
    report_pointer = _read_json(report_dir / "definition.pbir")
    expected_model_path = f"../{model_dir.name}"
    actual_model_path = (
        report_pointer.get("datasetReference", {}).get("byPath", {}).get("path")
    )
    _require(
        actual_model_path == expected_model_path,
        "PBIR must reference exactly the expected semantic model by relative path",
    )
    _read_json(model_dir / "definition.pbism")
    return report_dir, model_dir


def _validate_editor_settings(model_dir: Path) -> bool:
    settings_path = model_dir / ".pbi" / "editorSettings.json"
    settings = _read_json(settings_path)
    if "autodetectRelationships" not in settings:
        return False
    _require(
        settings["autodetectRelationships"] is False,
        "Power BI automatic relationship detection must be the boolean false",
    )
    return True


def _validate_tables(model_definition: Path) -> dict[str, str]:
    tables_dir = model_definition / "tables"
    _require(tables_dir.is_dir(), f"TMDL tables directory is missing: {tables_dir}")
    direct_files = sorted(tables_dir.glob("*.tmdl"))
    recursive_files = sorted(tables_dir.rglob("*.tmdl"))
    _require(
        direct_files == recursive_files,
        "All TMDL table files must be direct children of definition/tables",
    )
    _require(
        len(direct_files) == 9,
        f"Expected exactly 9 TMDL table files, got {len(direct_files)}",
    )
    _require(
        {path.stem for path in direct_files} == set(EXPECTED_TABLES),
        "TMDL table filename contract drift detected",
    )

    table_texts: dict[str, str] = {}
    for path in direct_files:
        text = _read_text(path)
        declarations = re.findall(r"^table\s+(.+?)\s*$", text, flags=re.MULTILINE)
        _require(
            len(declarations) == 1,
            f"Each table file must declare exactly one table: {path}",
        )
        table_name = _unquote_tmdl_name(declarations[0])
        _require(table_name == path.stem, f"Table declaration/filename mismatch: {path}")
        _require(
            len(re.findall(r"^\s+partition\s+", text, flags=re.MULTILINE)) == 1,
            f"Table must have exactly one partition: {table_name}",
        )
        table_texts[table_name] = text

    model_path = model_definition / "model.tmdl"
    model_text = _read_text(model_path)
    refs = [
        _unquote_tmdl_name(value)
        for value in re.findall(r"^\s*ref table\s+(.+?)\s*$", model_text, flags=re.MULTILINE)
    ]
    _require(len(refs) == 9, f"Expected exactly 9 TMDL table refs, got {len(refs)}")
    _require(len(refs) == len(set(refs)), "Duplicate TMDL table ref detected")
    _require(set(refs) == set(EXPECTED_TABLES), "TMDL table ref contract drift detected")

    for path in model_definition.rglob("*.tmdl"):
        if path.parent != tables_dir:
            _require(
                not re.search(r"^table\s+", _read_text(path), flags=re.MULTILINE),
                f"Table declaration found outside definition/tables: {path}",
            )
    return table_texts


def _parse_relationships(text: str) -> dict[str, tuple[str, str, str]]:
    headers = list(re.finditer(r"^relationship\s+(.+?)\s*$", text, flags=re.MULTILINE))
    relationships: dict[str, tuple[str, str, str]] = {}
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        block = text[header.end() : end]
        name = _unquote_tmdl_name(header.group(1))
        _require(name not in relationships, f"Duplicate relationship name: {name}")
        from_column = _one_match(r"^\s+fromColumn:\s*(.+?)\s*$", block, f"fromColumn for {name}")
        to_column = _one_match(r"^\s+toColumn:\s*(.+?)\s*$", block, f"toColumn for {name}")
        directions = re.findall(
            r"^\s+crossFilteringBehavior:\s*(\S+)\s*$",
            block,
            flags=re.MULTILINE,
        )
        _require(len(directions) <= 1, f"Duplicate cross-filter setting: {name}")
        direction = directions[0] if directions else "oneDirection"
        active_values = re.findall(r"^\s+isActive:\s*(\S+)\s*$", block, flags=re.MULTILINE)
        _require(len(active_values) <= 1, f"Duplicate active setting: {name}")
        _require(
            not active_values or active_values[0].lower() == "true",
            f"Relationship must be active: {name}",
        )
        relationships[name] = (from_column, to_column, direction)
    return relationships


def _relationship_table(column_ref: str) -> str:
    table_name, separator, _ = column_ref.partition(".")
    _require(bool(separator and table_name), f"Invalid relationship endpoint: {column_ref}")
    return _unquote_tmdl_name(table_name)


def _filter_path(
    relationships: dict[str, tuple[str, str, str]],
    source_table: str,
    target_table: str,
) -> list[str]:
    graph: dict[str, set[str]] = {}
    for from_column, to_column, direction in relationships.values():
        from_table = _relationship_table(from_column)
        to_table = _relationship_table(to_column)
        graph.setdefault(to_table, set()).add(from_table)
        if direction == "bothDirections":
            graph.setdefault(from_table, set()).add(to_table)

    queue: deque[list[str]] = deque([[source_table]])
    visited = {source_table}
    while queue:
        path = queue.popleft()
        if path[-1] == target_table:
            return path
        for next_table in sorted(graph.get(path[-1], set())):
            if next_table not in visited:
                visited.add(next_table)
                queue.append([*path, next_table])
    return []


def _validate_filter_paths(
    relationships: dict[str, tuple[str, str, str]],
) -> dict[str, list[str]]:
    paths: dict[str, list[str]] = {}
    for filter_name, source_table in {
        "Rule": "DimRequirement",
        "Topic": "DimTopic",
        "Priority": "DimTopic",
        "Assignee": "DimTopic",
    }.items():
        path = _filter_path(relationships, source_table, "DimElement")
        _require(
            bool(path),
            f"{filter_name} has no active filter path to DimElement",
        )
        paths[filter_name] = path
    return paths


def _validate_relationships(
    model_definition: Path,
    table_texts: dict[str, str],
) -> tuple[dict[str, tuple[str, str, str]], dict[str, list[str]]]:
    relationship_path = model_definition / "relationships.tmdl"
    relationships = _parse_relationships(_read_text(relationship_path))
    _require(
        len(relationships) == 8,
        f"Expected exactly 8 relationships, got {len(relationships)}",
    )
    filter_paths = _validate_filter_paths(relationships)
    _require(relationships == EXPECTED_RELATIONSHIPS, "Relationship contract drift detected")
    _require(
        sum(value[2] == "bothDirections" for value in relationships.values()) == 2,
        "Exactly two relationships must use bothDirections",
    )

    for path in model_definition.rglob("*.tmdl"):
        if path != relationship_path:
            _require(
                not re.search(r"^relationship\s+", _read_text(path), flags=re.MULTILINE),
                f"Relationship declaration found outside relationships.tmdl: {path}",
            )

    endpoints = "\n".join(
        f"{from_column}\n{to_column}"
        for from_column, to_column, _ in relationships.values()
    )
    for bridge in BRIDGE_TABLES:
        header = re.split(
            r"^\s+(?:column|measure|partition|hierarchy|annotation)\b",
            table_texts[bridge],
            maxsplit=1,
            flags=re.MULTILINE,
        )[0]
        _require(
            re.search(r"^\s+isHidden(?:\s*:\s*true)?\s*$", header, flags=re.MULTILINE)
            is not None,
            f"Bridge table must be hidden: {bridge}",
        )
        _require(bridge not in endpoints, f"Bridge table must be disconnected: {bridge}")
    return relationships, filter_paths


def _column_block(table_text: str, column_name: str) -> str:
    headers = list(
        re.finditer(
            r"^\s+column\s+(.+?)\s*$",
            table_text,
            flags=re.MULTILINE,
        )
    )
    matches: list[str] = []
    for index, header in enumerate(headers):
        name = _unquote_tmdl_name(header.group(1))
        end = headers[index + 1].start() if index + 1 < len(headers) else len(table_text)
        boundary = re.search(
            r"^\s+(?:measure|partition|hierarchy|annotation)\s+",
            table_text[header.end() : end],
            flags=re.MULTILINE,
        )
        if boundary:
            end = min(end, header.end() + boundary.start())
        if name == column_name:
            matches.append(table_text[header.end() : end])
    _require(
        len(matches) == 1,
        f"Expected exactly one TMDL column {column_name}, got {len(matches)}",
    )
    return matches[0]


def _validate_filter_source_columns(table_texts: dict[str, str]) -> None:
    required_columns = {
        *EXPECTED_SLICER_BINDINGS,
        ("DimTopic", "title"),
    }
    for table_name, column_name in sorted(required_columns):
        block = _column_block(table_texts[table_name], column_name)
        _require(
            re.search(r"^\s+isHidden(?:\s*:\s*true)?\s*$", block, flags=re.MULTILINE)
            is None,
            f"Filter source column must be visible: {table_name}[{column_name}]",
        )


def _validate_speckle_query_route(model_definition: Path) -> dict[str, Any]:
    expressions = _read_text(model_definition / "expressions.tmdl")
    model = _read_text(model_definition / "model.tmdl")
    combined = f"{expressions}\n{model}"
    _require(
        "SpeckleFederationStage" not in combined,
        "Unused SpeckleFederationStage must not be declared or queried",
    )
    _require(
        "federation_url" not in expressions.casefold(),
        "The semantic model must not consume a prebuilt federation URL",
    )
    for token in (
        'Record.Field(_, "upload_route")',
        'UploadRoute <> "direct_ifc"',
        'Record.Field(_, "source_filename")',
        'Record.Field(_, "ifc_sha256")',
        'Text.Select(IfcSha256, {"0".."9", "a".."f"})',
        'Record.Field([data], "properties")',
        'Record.Field([_raw_properties], "IFC GUID")',
        'Record.Field([_raw_properties], "IFC Attributes")',
        'Record.Field([_raw_properties], "Attributes")',
        'Record.Field([properties], "GlobalId")',
        'Record.Field([data], "ifcType")',
        'List.Count([_identity_evidence]) < 2',
        'List.Count(List.Distinct([_identity_evidence])) <> 1',
        'Connector IFC identity evidence fields disagree or fewer than two are present',
    ):
        _require(token in expressions, f"Direct IFC manifest validation is missing: {token}")

    compact = re.sub(r"\s+", "", expressions)
    _require(
        (
            "IfcIdentityCandidates=Table.SelectRows("
            "WithIfcGuid,eachList.Count([_identity_evidence])>0)"
        ) in compact,
        "Speckle hierarchy container-row filter is missing or has drifted",
    )
    _require(
        "Table.SelectRows(IfcIdentityCandidates,each"
        "List.Count([_identity_evidence])<2or"
        "List.Count(List.Distinct([_identity_evidence]))<>1)" in compact,
        "Speckle IFC identity candidate validation is missing or has drifted",
    )
    _require(
        "applicationid" not in expressions.casefold(),
        "Speckle applicationId must not be used as IFC identity evidence",
    )
    _require(
        compact.count("Speckle.GetByUrl(ModelVersionUrl,false)") == 1,
        "Each source model must be received only through the version-pinned direct query",
    )
    expected_calls = (
        'Architecture=NormalizeSpeckleModel("architecture",GetSpeckleModelUrl("architecture"))',
        'Structural=NormalizeSpeckleModel("structural",GetSpeckleModelUrl("structural"))',
        'Hvac=NormalizeSpeckleModel("hvac",GetSpeckleModelUrl("hvac"))',
    )
    for call in expected_calls:
        _require(call in compact, f"Missing fixed Direct IFC model query: {call}")
    _require(
        compact.count("Speckle.Models.Federate({Architecture,Structural,Hvac},false)") == 1,
        "The three Direct IFC model queries must feed exactly one Speckle.Models.Federate call",
    )
    _require("revit" not in expressions.casefold(), "Revit must not be a Stage 3B source route")

    query_order_matches = re.findall(
        r"^annotation PBI_QueryOrder\s*=\s*(\[.*\])\s*$",
        model,
        flags=re.MULTILINE,
    )
    _require(len(query_order_matches) == 1, "Expected exactly one PBI_QueryOrder annotation")
    try:
        query_order = json.loads(query_order_matches[0])
    except json.JSONDecodeError as exc:
        raise PbipValidationError("PBI_QueryOrder must be valid JSON") from exc
    _require(
        tuple(query_order) == EXPECTED_QUERY_ORDER,
        "PBI_QueryOrder must contain only the fixed Direct IFC federation pipeline",
    )
    return {
        "upload_route": "direct_ifc",
        "version_pinned_model_queries": 3,
        "federation_function": "Speckle.Models.Federate",
    }


def _parse_measures(table_texts: dict[str, str]) -> dict[str, tuple[str, str]]:
    measures: dict[str, tuple[str, str]] = {}
    header_pattern = re.compile(
        r"^\s*measure\s+('(?:[^']|'')+'|[^=]+?)\s*=\s*(.*)$",
        flags=re.MULTILINE,
    )
    for table_name, text in table_texts.items():
        headers = list(header_pattern.finditer(text))
        for index, header in enumerate(headers):
            end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
            for boundary in re.finditer(
                r"^\s+(?:column|partition|hierarchy)\s+",
                text[header.end() : end],
                flags=re.MULTILINE,
            ):
                end = min(end, header.end() + boundary.start())
                break
            name = _unquote_tmdl_name(header.group(1))
            _require(name not in measures, f"Duplicate measure name: {name}")
            expression = header.group(2) + text[header.end() : end]
            metadata = re.search(
                r"^\s+(?:dataCategory|description|displayFolder|formatString|lineageTag)\s*:",
                expression,
                flags=re.MULTILINE,
            )
            if metadata:
                expression = expression[: metadata.start()]
            measures[name] = (table_name, expression.strip())
    return measures


def _strip_dax_comments(expression: str) -> str:
    expression = re.sub(r"/\*.*?\*/", " ", expression, flags=re.DOTALL)
    return re.sub(r"//.*$", " ", expression, flags=re.MULTILINE)


def _validate_kpis(table_texts: dict[str, str]) -> None:
    measures = _parse_measures(table_texts)
    missing = sorted(set(EXPECTED_KPI_SIGNATURES) - set(measures))
    _require(not missing, f"Missing fixed KPI measures: {', '.join(missing)}")
    for name, required_tokens in EXPECTED_KPI_SIGNATURES.items():
        table_name, raw_expression = measures[name]
        _require(table_name == "DimRun", f"Fixed KPI measure must belong to DimRun: {name}")
        expression = _strip_dax_comments(raw_expression)
        normalized = re.sub(r"\s+", "", expression).casefold()
        _require(bool(normalized), f"KPI measure has no expression: {name}")
        for token in required_tokens:
            _require(
                re.sub(r"\s+", "", token).casefold() in normalized,
                f"KPI measure formula drift detected: {name}",
            )
        without_strings = re.sub(r'"(?:[^\"]|\"\")*"', "", expression)
        numeric_literals = re.findall(
            r"(?<![A-Za-z0-9_])\d+(?:\.\d+)?(?![A-Za-z0-9_])",
            without_strings,
        )
        allowed_literals = ["0"] if name == "Applicable Check Pass Rate" else []
        _require(
            numeric_literals == allowed_literals,
            f"KPI measure must not contain hard-coded numeric values: {name}",
        )

    topic_count = measures.get("Selected Topic Linked Findings")
    _require(topic_count is not None, "Selected Topic Linked Findings measure is missing")
    normalized_topic_count = re.sub(r"\s+", " ", topic_count[1])
    for signature in (
        "SELECTEDVALUE ( DimTopic[topic_guid] )",
        "ISBLANK ( SelectedTopicGuid )",
        "TREATAS ( { SelectedTopicGuid }, BridgeTopicFinding[topic_guid] )",
    ):
        _require(
            signature in normalized_topic_count,
            f"Selected Topic Linked Findings is missing formula signature {signature}",
        )

    topic_detail = measures.get("Selected Topic Finding Details")
    _require(topic_detail is not None, "Selected Topic Finding Details measure is missing")
    normalized_topic_detail = re.sub(r"\s+", " ", topic_detail[1])
    for signature in (
        "CONCATENATEX",
        "TREATAS",
        'FactIDSCheck[requirement_id] & " - " & FactIDSCheck[requirement]',
        "FactIDSCheck[actual]",
    ):
        _require(
            signature in normalized_topic_detail,
            f"Selected Topic Finding Details is missing formula signature {signature}",
        )


def _source_property(field: Any) -> tuple[str, str]:
    _require(isinstance(field, dict), "Visual projection field must be an object")
    current = field
    if "Aggregation" in current:
        aggregation = current["Aggregation"]
        _require(isinstance(aggregation, dict), "Visual aggregation must be an object")
        current = aggregation.get("Expression")
        _require(isinstance(current, dict), "Visual aggregation expression is missing")
    column = current.get("Column") if isinstance(current, dict) else None
    _require(isinstance(column, dict), "Visual projection must resolve to a column")
    source_ref = column.get("Expression", {}).get("SourceRef", {})
    return source_ref.get("Entity"), column.get("Property")


def _single_role_projection(query_state: dict[str, Any], role: str) -> dict[str, Any]:
    role_state = query_state.get(role)
    _require(isinstance(role_state, dict), f"Speckle visual role is missing: {role}")
    projections = role_state.get("projections")
    _require(
        isinstance(projections, list) and len(projections) == 1,
        f"Speckle visual role must have exactly one projection: {role}",
    )
    _require(isinstance(projections[0], dict), f"Invalid Speckle projection: {role}")
    return projections[0]


def _walk_json(value: Any, *, parent_key: str | None = None) -> Iterable[tuple[str | None, Any]]:
    yield parent_key, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk_json(child, parent_key=str(key))
    elif isinstance(value, list):
        for child in value:
            yield from _walk_json(child, parent_key=parent_key)


def _validate_speckle_visual(document: dict[str, Any]) -> None:
    visual = document.get("visual")
    _require(isinstance(visual, dict), "Speckle visual payload is missing")
    query_state = visual.get("query", {}).get("queryState", {})
    _require(isinstance(query_state, dict), "Speckle visual queryState is missing")

    model_info = _single_role_projection(query_state, "rootObjectId")
    object_ids = _single_role_projection(query_state, "objectIds")
    tooltip_data = _single_role_projection(query_state, "tooltipData")
    _require(
        _source_property(model_info.get("field")) == ("DimElement", "Model Info"),
        "Speckle Model Info must bind exactly to DimElement[Model Info]",
    )
    _require(
        _source_property(object_ids.get("field")) == ("DimElement", "Object IDs"),
        "Speckle Object IDs must bind exactly to DimElement[Object IDs]",
    )
    _require(
        _source_property(tooltip_data.get("field")) == ("DimElement", "element_key"),
        "Speckle tooltip must bind exactly to DimElement[element_key]",
    )

    for key, value in _walk_json(document):
        key_text = (key or "").casefold()
        string_value = value.casefold() if isinstance(value, str) else ""
        _require(
            key_text not in {"storeddata", "receiveinfo"}
            and "storeddata" not in string_value
            and "receiveinfo" not in string_value,
            "Speckle visual contains forbidden storedData/receiveInfo state",
        )
        _require(
            "token" not in key_text and not re.search(r"\btoken\b", string_value),
            "Speckle visual contains forbidden token state",
        )


def _validate_number(value: Any, label: str) -> float:
    _require(
        isinstance(value, (int, float)) and not isinstance(value, bool),
        f"Visual {label} must be numeric",
    )
    result = float(value)
    _require(math.isfinite(result), f"Visual {label} must be finite")
    return result


def _card_measure(document: dict[str, Any]) -> tuple[str, str]:
    query_state = document.get("visual", {}).get("query", {}).get("queryState", {})
    _require(isinstance(query_state, dict), "Card queryState is missing")
    projection = _single_role_projection(query_state, "Data")
    field = projection.get("field", {})
    measure = field.get("Measure") if isinstance(field, dict) else None
    _require(isinstance(measure, dict), "Card must bind to exactly one measure")
    source = measure.get("Expression", {}).get("SourceRef", {}).get("Entity")
    property_name = measure.get("Property")
    _require(isinstance(source, str) and isinstance(property_name, str), "Invalid card measure")
    return source, property_name


def _power_bi_literal_value(value: Any, label: str) -> str:
    _require(isinstance(value, str), f"{label} must be a Power BI text literal")
    _require(
        len(value) >= 2 and value[0] == value[-1] == "'",
        f"{label} must be enclosed in single quotes",
    )
    return value[1:-1].replace("''", "'")


def _visual_title(document: dict[str, Any]) -> str:
    title_objects = (
        document.get("visual", {}).get("visualContainerObjects", {}).get("title")
    )
    _require(
        isinstance(title_objects, list) and len(title_objects) == 1,
        "Interactive visual must have exactly one title object",
    )
    properties = title_objects[0].get("properties", {})
    show = properties.get("show", {}).get("expr", {}).get("Literal", {}).get("Value")
    _require(show == "true", "Interactive visual title must be shown")
    value = properties.get("text", {}).get("expr", {}).get("Literal", {}).get("Value")
    return _power_bi_literal_value(value, "Interactive visual title")


def _slicer_binding(document: dict[str, Any]) -> tuple[tuple[str, str], str]:
    visual = document.get("visual", {})
    query_state = visual.get("query", {}).get("queryState", {})
    _require(isinstance(query_state, dict), "Slicer queryState is missing")
    projection = _single_role_projection(query_state, "Values")
    _require(projection.get("active") is True, "Slicer projection must be active")
    binding = _source_property(projection.get("field"))
    expected_query_ref = f"{binding[0]}.{binding[1]}"
    _require(
        projection.get("queryRef") == expected_query_ref,
        f"Slicer queryRef must be {expected_query_ref}",
    )
    title = _visual_title(document)
    _require(
        projection.get("nativeQueryRef") == title,
        "Slicer nativeQueryRef must match its visible title",
    )
    _require(
        visual.get("drillFilterOtherVisuals") is True,
        f"Slicer must filter other visuals: {title}",
    )
    return binding, title


def _column_projection_bindings(document: dict[str, Any]) -> list[tuple[str, str]]:
    query_state = document.get("visual", {}).get("query", {}).get("queryState", {})
    _require(isinstance(query_state, dict), "Table queryState is missing")
    bindings: list[tuple[str, str]] = []
    for role_state in query_state.values():
        if not isinstance(role_state, dict):
            continue
        projections = role_state.get("projections", [])
        if not isinstance(projections, list):
            continue
        for projection in projections:
            field = projection.get("field") if isinstance(projection, dict) else None
            if isinstance(field, dict) and ("Column" in field or "Aggregation" in field):
                bindings.append(_source_property(field))
    return bindings


def _validate_report(
    report_definition: Path,
) -> tuple[dict[str, int], set[str], dict[str, tuple[str, str]]]:
    pages_root = report_definition / "pages"
    pages_metadata = _read_json(pages_root / "pages.json")
    page_order = pages_metadata.get("pageOrder")
    _require(isinstance(page_order, list) and len(page_order) == 1, "Report must have one page")
    page_id = page_order[0]
    _require(isinstance(page_id, str), "Report page ID must be text")
    _require(
        LOWER_HEX_ID.fullmatch(page_id) is not None,
        f"Page ID must be 20 lowercase hex characters: {page_id}",
    )
    _require(
        pages_metadata.get("activePageName") == page_id,
        "The single report page must be active",
    )
    page_dirs = sorted(path for path in pages_root.iterdir() if path.is_dir())
    _require(
        [path.name for path in page_dirs] == [page_id],
        "Page directory/pageOrder contract drift detected",
    )
    page_dir = page_dirs[0]
    page = _read_json(page_dir / "page.json")
    _require(page.get("name") == page_id, "Page directory/JSON name mismatch")
    _require(page.get("displayName") == PAGE_NAME, "Report page name must be English and fixed")
    _require(page.get("width") == PAGE_WIDTH, f"Report page width must be {PAGE_WIDTH}")
    _require(page.get("height") == PAGE_HEIGHT, f"Report page height must be {PAGE_HEIGHT}")

    visuals_dir = page_dir / "visuals"
    _require(visuals_dir.is_dir(), "Visuals directory is missing")
    visual_entries = sorted(visuals_dir.iterdir())
    _require(
        all(path.is_dir() for path in visual_entries),
        "The visual collection must contain ID directories only",
    )
    visual_dirs = visual_entries
    _require(len(visual_dirs) == 16, f"Expected exactly 16 visuals, got {len(visual_dirs)}")
    visual_counts: Counter[str] = Counter()
    card_measures: list[tuple[str, str]] = []
    speckle_documents: list[dict[str, Any]] = []
    slicer_documents: list[dict[str, Any]] = []
    table_documents: list[dict[str, Any]] = []
    for visual_dir in visual_dirs:
        visual_id = visual_dir.name
        _require(
            LOWER_HEX_ID.fullmatch(visual_id) is not None,
            f"Visual ID must be 20 lowercase hex characters: {visual_id}",
        )
        visual_path = visual_dir / "visual.json"
        _require(
            {path.name for path in visual_dir.iterdir()} == {"visual.json"},
            f"Visual directory must contain only visual.json: {visual_id}",
        )
        document = _read_json(visual_path)
        _require(document.get("name") == visual_id, f"Visual directory/JSON name mismatch: {visual_id}")
        visual = document.get("visual")
        _require(isinstance(visual, dict), f"Visual payload is missing: {visual_id}")
        visual_type = visual.get("visualType")
        _require(isinstance(visual_type, str), f"Visual type is missing: {visual_id}")
        visual_counts[visual_type] += 1

        position = document.get("position")
        _require(isinstance(position, dict), f"Visual position is missing: {visual_id}")
        x = _validate_number(position.get("x"), "x")
        y = _validate_number(position.get("y"), "y")
        width = _validate_number(position.get("width"), "width")
        height = _validate_number(position.get("height"), "height")
        _require(x >= 0 and y >= 0, f"Visual starts outside the page: {visual_id}")
        _require(width > 0 and height > 0, f"Visual has non-positive size: {visual_id}")
        _require(
            x + width <= PAGE_WIDTH and y + height <= PAGE_HEIGHT,
            f"Visual exceeds the 1280x720 page bounds: {visual_id}",
        )

        if visual_type == "cardVisual":
            card_measures.append(_card_measure(document))
        elif visual_type == "specklePowerBiVisual":
            speckle_documents.append(document)
        elif visual_type == "slicer":
            slicer_documents.append(document)
        elif visual_type == "tableEx":
            table_documents.append(document)

    _require(visual_counts == EXPECTED_VISUAL_COUNTS, f"Visual type contract drift: {visual_counts}")
    _require(
        set(card_measures) == {("DimRun", name) for name in EXPECTED_KPI_SIGNATURES}
        and len(card_measures) == len(EXPECTED_KPI_SIGNATURES),
        "Seven KPI cards must bind one-to-one to the fixed DimRun KPI measures",
    )
    _require(len(speckle_documents) == 1, "Expected exactly one Speckle visual")
    _validate_speckle_visual(speckle_documents[0])

    slicer_bindings: dict[tuple[str, str], str] = {}
    for document in slicer_documents:
        binding, title = _slicer_binding(document)
        _require(binding not in slicer_bindings, f"Duplicate slicer binding: {binding}")
        slicer_bindings[binding] = title
    _require(
        slicer_bindings == EXPECTED_SLICER_BINDINGS,
        f"Rule/Priority/Assignee/Discipline slicer contract drift: {slicer_bindings}",
    )

    topic_tables = []
    for document in table_documents:
        bindings = _column_projection_bindings(document)
        if ("DimTopic", "title") in bindings:
            topic_tables.append((document, bindings))
    _require(len(topic_tables) == 1, "Expected exactly one Topic selector table")
    topic_document, topic_bindings = topic_tables[0]
    _require(
        len(topic_bindings) == len(EXPECTED_TOPIC_TABLE_BINDINGS)
        and set(topic_bindings) == EXPECTED_TOPIC_TABLE_BINDINGS,
        "Topic selector table binding contract drift detected",
    )
    _require(
        _visual_title(topic_document) == "Open BCF Topics — select one row",
        "Topic selector table title contract drift detected",
    )
    _require(
        topic_document.get("visual", {}).get("drillFilterOtherVisuals") is True,
        "Topic selector table must filter other visuals",
    )

    report_text = "\n".join(
        _read_text(path)
        for path in sorted(report_definition.rglob("*.json"))
    )
    _require(CJK_TEXT.search(report_text) is None, "Report definition contains non-English CJK text")
    structural_ids = {page_id, *(path.name for path in visual_dirs)}
    filter_bindings = {
        title: binding
        for binding, title in sorted(slicer_bindings.items(), key=lambda item: item[1])
    }
    filter_bindings["Topic"] = ("DimTopic", "title")
    return dict(sorted(visual_counts.items())), structural_ids, filter_bindings


def _validate_json_hex_literals(
    path: Path,
    document: dict[str, Any],
    allowed_structural_ids: set[str],
) -> None:
    allowed_keys = {"activePageName", "name", "pageOrder"}
    for parent_key, value in _walk_json(document):
        if not isinstance(value, str) or HEX_LITERAL.fullmatch(value) is None:
            continue
        _require(
            parent_key in allowed_keys and value in allowed_structural_ids,
            f"Potential real Speckle ID/version found in definition: {path}",
        )


def _validate_definition_security(
    paths: Iterable[Path],
    allowed_structural_ids: set[str],
) -> None:
    for path in paths:
        text = _read_text(path)
        _require(SPECKLE_URL.search(text) is None, f"Real Speckle URL found in definition: {path}")
        _require(
            SPECKLE_ROUTE_URL.search(text) is None,
            f"Real Speckle route URL found in definition: {path}",
        )
        _require(
            PINNED_VERSION_FRAGMENT.search(text) is None,
            f"Real Speckle version fragment found in definition: {path}",
        )
        _require(EMAIL.search(text) is None, f"Email address found in definition: {path}")
        _require(
            SENSITIVE_WORD.search(text) is None,
            f"Credential/token/cookie material found in definition: {path}",
        )
        _require(
            POSIX_USER_PATH.search(text) is None,
            f"Username-specific absolute path found in definition: {path}",
        )
        for match in WINDOWS_ABSOLUTE_PATH.finditer(text):
            normalized = match.group(0).replace("\\\\", "\\")
            _require(
                normalized.startswith(r"C:\REPLACE_WITH_LOCAL_REPOSITORY"),
                f"Non-placeholder Windows absolute path found in definition: {path}",
            )
        if path.suffix.lower() == ".tmdl":
            _require(
                QUOTED_HEX_LITERAL.search(text) is None,
                f"Potential real Speckle ID/version found in definition: {path}",
            )
        else:
            _validate_json_hex_literals(path, _read_json(path), allowed_structural_ids)


def _sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise PbipValidationError(f"Cannot hash acceptance artifact: {path}") from exc


def definition_tree_sha256(
    dashboard_dir: Path,
    report_definition: Path,
    model_definition: Path,
) -> str:
    digest = hashlib.sha256()
    paths = sorted(
        [
            *(path for path in report_definition.rglob("*") if path.is_file()),
            *(path for path in model_definition.rglob("*") if path.is_file()),
        ],
        key=lambda path: path.relative_to(dashboard_dir).as_posix(),
    )
    _require(bool(paths), "Definition tree must contain files before it can be hashed")
    for path in paths:
        relative_path = path.relative_to(dashboard_dir).as_posix()
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(_sha256_file(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _require_exact_keys(document: Any, expected: set[str], label: str) -> dict[str, Any]:
    _require(isinstance(document, dict), f"{label} must be a JSON object")
    actual = set(document)
    _require(
        actual == expected,
        f"{label} keys must be exactly {sorted(expected)}; got {sorted(actual)}",
    )
    return document


def _require_true_flags(document: Any, expected: set[str], label: str) -> None:
    values = _require_exact_keys(document, expected, label)
    for key in sorted(expected):
        _require(values[key] is True, f"{label}.{key} must be the boolean true")


def _require_sha256(value: Any, label: str) -> str:
    _require(
        isinstance(value, str) and LOWER_SHA256.fullmatch(value) is not None,
        f"{label} must be a lowercase SHA-256",
    )
    return value


def _validate_capture_metadata(manifest: dict[str, Any]) -> tuple[str, str]:
    desktop_version = manifest["desktop_version"]
    _require(
        isinstance(desktop_version, str)
        and DESKTOP_VERSION.fullmatch(desktop_version) is not None,
        "desktop_version must be a four-part numeric Desktop version",
    )
    captured_at = manifest["captured_at"]
    _require(
        isinstance(captured_at, str)
        and RFC3339_TIMESTAMP.fullmatch(captured_at) is not None,
        "captured_at must be an RFC 3339 timestamp with an explicit UTC offset",
    )
    try:
        parsed = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PbipValidationError("captured_at is not a valid timestamp") from exc
    _require(
        parsed.tzinfo is not None and parsed.utcoffset() is not None,
        "captured_at must include an explicit UTC offset",
    )
    return desktop_version, captured_at


def _validate_data_snapshot(value: Any) -> dict[str, str]:
    snapshot = _require_exact_keys(value, set(DATA_SNAPSHOT_PATHS), "data_snapshot")
    validated: dict[str, str] = {}
    for key, path in DATA_SNAPSHOT_PATHS.items():
        expected = _require_sha256(snapshot[key], f"data_snapshot.{key}")
        _require(path.is_file(), f"Data snapshot source is missing: {path}")
        actual = _sha256_file(path)
        _require(expected == actual, f"Data snapshot SHA-256 is stale: {key}")
        validated[key] = actual
    return validated


def _manifest_display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def _validate_acceptance_screenshots(
    screenshots: Any,
    manifest_path: Path,
) -> dict[str, dict[str, Any]]:
    _require(
        isinstance(screenshots, list) and len(screenshots) == 5,
        "Acceptance manifest must reference exactly five screenshots",
    )
    by_id: dict[str, dict[str, Any]] = {}
    used_paths: set[Path] = set()
    evidence_dir = manifest_path.parent.resolve()
    for index, raw_screenshot in enumerate(screenshots):
        screenshot = _require_exact_keys(
            raw_screenshot,
            {"id", "path", "sha256"},
            f"screenshots[{index}]",
        )
        screenshot_id = screenshot["id"]
        _require(isinstance(screenshot_id, str), f"screenshots[{index}].id must be text")
        _require(screenshot_id not in by_id, f"Duplicate screenshot id: {screenshot_id}")

        relative_value = screenshot["path"]
        _require(
            isinstance(relative_value, str) and bool(relative_value),
            f"Screenshot path must be non-empty text: {screenshot_id}",
        )
        relative_path = Path(relative_value)
        _require(
            not relative_path.is_absolute()
            and len(relative_path.parts) == 1
            and relative_path.name == relative_value
            and relative_path.suffix.casefold() == ".png",
            f"Screenshot must be a direct relative PNG path: {screenshot_id}",
        )
        _require(
            relative_value == EXPECTED_SCREENSHOT_FILENAMES.get(screenshot_id),
            f"Screenshot filename is not the fixed acceptance filename: {screenshot_id}",
        )
        screenshot_path = manifest_path.parent / relative_path
        resolved_path = screenshot_path.resolve()
        _require(
            resolved_path.parent == evidence_dir and not screenshot_path.is_symlink(),
            f"Screenshot path escapes the evidence directory: {screenshot_id}",
        )
        _require(screenshot_path.is_file(), f"Acceptance screenshot is missing: {relative_value}")
        _require(resolved_path not in used_paths, f"Duplicate screenshot path: {relative_value}")
        used_paths.add(resolved_path)
        try:
            png_signature = screenshot_path.read_bytes()[:8]
        except OSError as exc:
            raise PbipValidationError(f"Cannot read acceptance screenshot: {relative_value}") from exc
        _require(
            png_signature == b"\x89PNG\r\n\x1a\n",
            f"Acceptance screenshot is not a PNG: {relative_value}",
        )
        expected_sha256 = _require_sha256(
            screenshot["sha256"],
            f"screenshots[{index}].sha256",
        )
        _require(
            expected_sha256 not in RETIRED_MAPPING_QA_HASHES,
            f"Retired Mapping QA screenshot cannot be reused: {relative_value}",
        )
        _require(
            _sha256_file(screenshot_path) == expected_sha256,
            f"Acceptance screenshot SHA-256 mismatch: {relative_value}",
        )
        by_id[screenshot_id] = screenshot
    _require(
        set(by_id) == EXPECTED_SCREENSHOT_IDS,
        f"Acceptance screenshot IDs must be exactly {sorted(EXPECTED_SCREENSHOT_IDS)}",
    )
    actual_png_paths = {
        path.resolve()
        for path in evidence_dir.iterdir()
        if path.is_file() and path.suffix.casefold() == ".png"
    }
    _require(
        actual_png_paths == used_paths,
        "Evidence directory PNG files must exactly match the five manifest screenshots",
    )
    return by_id


def _validate_acceptance_topics(
    topics: Any,
    screenshots_by_id: dict[str, dict[str, Any]],
) -> None:
    _require(
        isinstance(topics, list) and len(topics) == 3,
        "Acceptance manifest must contain exactly three Topic mappings",
    )
    actual: dict[str, str] = {}
    for index, raw_topic in enumerate(topics):
        topic = _require_exact_keys(
            raw_topic,
            {
                "topic_guid",
                "element_key",
                "selected_element_count",
                "linked_finding_count",
                "highlighted_element_count",
                "screenshot_id",
            },
            f"topics[{index}]",
        )
        topic_guid = topic["topic_guid"]
        element_key = topic["element_key"]
        _require(
            isinstance(topic_guid, str) and isinstance(element_key, str),
            f"Topic mapping identity must be text: topics[{index}]",
        )
        _require(topic_guid not in actual, f"Duplicate Topic mapping: {topic_guid}")
        actual[topic_guid] = element_key
        for count_name, expected in {
            "selected_element_count": 1,
            "linked_finding_count": 2,
            "highlighted_element_count": 1,
        }.items():
            _require(
                type(topic[count_name]) is int and topic[count_name] == expected,
                f"topics[{index}].{count_name} must be the integer {expected}",
            )
        expected_screenshot_id = f"topic-{topic_guid}"
        _require(
            topic["screenshot_id"] == expected_screenshot_id
            and expected_screenshot_id in screenshots_by_id,
            f"Topic screenshot mapping is invalid: {topic_guid}",
        )
    _require(actual == EXPECTED_TOPIC_MAPPINGS, "Topic-to-element acceptance mapping drift detected")


def _validate_acceptance_manifest(
    manifest_path: Path,
    *,
    project_name: str,
    editor_settings_field_serialized: bool,
    tracked_definition_tree_sha256: str,
    relationships_sha256: str,
) -> dict[str, Any]:
    _require(manifest_path.is_file(), f"Acceptance manifest is missing: {manifest_path}")
    manifest = _require_exact_keys(
        _read_json(manifest_path),
        {
            "manifest_version",
            "project",
            "run_id",
            "desktop_version",
            "captured_at",
            "tracked_definition_tree_sha256",
            "post_reopen_relationships_sha256",
            "post_reopen_relationship_count",
            "data_snapshot",
            "autodetect_relationships",
            "lifecycle",
            "filter_interactions",
            "overview_results",
            "filter_results",
            "topics",
            "screenshots",
            "privacy_review",
        },
        "Acceptance manifest",
    )
    _require(manifest["manifest_version"] == "0.1", "Acceptance manifest version must be 0.1")
    _require(manifest["project"] == project_name, "Acceptance manifest project mismatch")
    _require(manifest["run_id"] == EXPECTED_RUN_ID, "Acceptance manifest run_id mismatch")
    desktop_version, captured_at = _validate_capture_metadata(manifest)
    data_snapshot = _validate_data_snapshot(manifest["data_snapshot"])
    manifest_tree_sha256 = _require_sha256(
        manifest["tracked_definition_tree_sha256"],
        "tracked_definition_tree_sha256",
    )
    _require(
        manifest_tree_sha256 == tracked_definition_tree_sha256,
        "Acceptance manifest definition tree SHA-256 is stale",
    )
    manifest_relationships_sha256 = _require_sha256(
        manifest["post_reopen_relationships_sha256"],
        "post_reopen_relationships_sha256",
    )
    _require(
        manifest_relationships_sha256 == relationships_sha256,
        "Post-reopen relationships SHA-256 does not match the tracked model",
    )
    _require(
        type(manifest["post_reopen_relationship_count"]) is int
        and manifest["post_reopen_relationship_count"] == len(EXPECTED_RELATIONSHIPS),
        "Post-reopen relationship count must be the integer 8",
    )

    autodetect = _require_exact_keys(
        manifest["autodetect_relationships"],
        {
            "editor_settings_field_serialized",
            "verification",
            "disabled_in_desktop",
            "screenshot_id",
        },
        "autodetect_relationships",
    )
    _require(
        autodetect["editor_settings_field_serialized"] is editor_settings_field_serialized,
        "Acceptance manifest editorSettings serialization claim is incorrect",
    )
    expected_verification = (
        "editor_settings_serialized_false"
        if editor_settings_field_serialized
        else "manual_unserialized"
    )
    _require(
        autodetect["verification"] == expected_verification,
        f"Autodetect verification must be {expected_verification}",
    )
    _require(
        autodetect["disabled_in_desktop"] is True,
        "Autodetect must be manually verified as disabled in Desktop",
    )
    _require(
        autodetect["screenshot_id"] == AUTODETECT_SCREENSHOT_ID,
        "Autodetect acceptance must reference the settings screenshot",
    )

    _require_true_flags(manifest["lifecycle"], EXPECTED_LIFECYCLE_KEYS, "lifecycle")
    _require_true_flags(
        manifest["filter_interactions"],
        EXPECTED_FILTER_INTERACTION_KEYS,
        "filter_interactions",
    )
    _require(
        manifest["overview_results"] == EXPECTED_OVERVIEW_RESULTS,
        "Overview acceptance results do not match the fixed Stage 3B values",
    )
    _require(
        manifest["filter_results"] == EXPECTED_FILTER_RESULTS,
        "Rule/Priority/Assignee acceptance results do not match the fixed Stage 3B values",
    )
    _require_true_flags(manifest["privacy_review"], EXPECTED_PRIVACY_KEYS, "privacy_review")
    screenshots_by_id = _validate_acceptance_screenshots(manifest["screenshots"], manifest_path)
    _validate_acceptance_topics(manifest["topics"], screenshots_by_id)

    return {
        "path": _manifest_display_path(manifest_path),
        "manifest_version": "0.1",
        "desktop_version": desktop_version,
        "captured_at": captured_at,
        "data_snapshot": data_snapshot,
        "definition_tree_sha256": tracked_definition_tree_sha256,
        "relationships_sha256": relationships_sha256,
        "screenshots": len(screenshots_by_id),
        "topics": len(EXPECTED_TOPIC_MAPPINGS),
        "lifecycle_verified": True,
        "filter_interactions_verified": True,
        "overview_results_verified": True,
        "filter_results_verified": True,
        "privacy_reviewed": True,
    }


def validate_pbip(
    dashboard_dir: Path = DEFAULT_DASHBOARD_DIR,
    project_name: str = DEFAULT_PROJECT_NAME,
    acceptance_manifest_path: Path = DEFAULT_ACCEPTANCE_MANIFEST,
) -> dict[str, Any]:
    dashboard_dir = dashboard_dir.resolve()
    _require(
        isinstance(acceptance_manifest_path, Path),
        "An acceptance manifest path is required; validation cannot be skipped",
    )
    acceptance_manifest_path = acceptance_manifest_path.resolve()
    report_dir, model_dir = _validate_project_links(dashboard_dir, project_name)
    report_definition = report_dir / "definition"
    model_definition = model_dir / "definition"
    definition_files = _definition_text_files(report_definition, model_definition)

    editor_settings_field_serialized = _validate_editor_settings(model_dir)
    table_texts = _validate_tables(model_definition)
    relationships, filter_paths = _validate_relationships(model_definition, table_texts)
    _validate_filter_source_columns(table_texts)
    _validate_kpis(table_texts)
    speckle_route = _validate_speckle_query_route(model_definition)
    visual_counts, structural_ids, filter_bindings = _validate_report(report_definition)
    _validate_definition_security(definition_files, structural_ids)
    tree_sha256 = definition_tree_sha256(
        dashboard_dir,
        report_definition,
        model_definition,
    )
    relationships_sha256 = _sha256_file(model_definition / "relationships.tmdl")
    acceptance_manifest = _validate_acceptance_manifest(
        acceptance_manifest_path,
        project_name=project_name,
        editor_settings_field_serialized=editor_settings_field_serialized,
        tracked_definition_tree_sha256=tree_sha256,
        relationships_sha256=relationships_sha256,
    )
    return {
        "acceptance": "PBIP_STATIC_CONTRACT_AND_EVIDENCE_INTEGRITY_PASSED",
        "project": project_name,
        "tables": len(EXPECTED_TABLES),
        "relationships": len(relationships),
        "bidirectional_relationships": 2,
        "automatic_relationship_detection": {
            "disabled": True,
            "verification": (
                "editor_settings_serialized_false"
                if editor_settings_field_serialized
                else "manual_unserialized"
            ),
            "field_serialized": editor_settings_field_serialized,
        },
        "fixed_kpi_measures": len(EXPECTED_KPI_SIGNATURES),
        "pages": 1,
        "visuals": sum(visual_counts.values()),
        "visual_counts": visual_counts,
        "filter_bindings": {
            name: f"{binding[0]}[{binding[1]}]"
            for name, binding in sorted(filter_bindings.items())
        },
        "filter_paths_to_dim_element": filter_paths,
        "speckle_route": speckle_route,
        "acceptance_manifest": acceptance_manifest,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dashboard-dir", type=Path, default=DEFAULT_DASHBOARD_DIR)
    parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)
    parser.add_argument(
        "--acceptance-manifest",
        type=Path,
        default=DEFAULT_ACCEPTANCE_MANIFEST,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        result = validate_pbip(
            args.dashboard_dir,
            args.project_name,
            args.acceptance_manifest,
        )
    except PbipValidationError as exc:
        print(f"PBIP static validation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
