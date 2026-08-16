"""Fail-closed, offline validation for the Power BI Control Tower contract."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_PATH = PROJECT_ROOT / "dashboard" / "spec" / "model_contract.json"
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DEFAULT_MAPPING_PATH = PROJECT_ROOT / "dashboard" / "local" / "speckle_mapping.csv"
DEFAULT_CONNECTIONS_PATH = (
    PROJECT_ROOT / "dashboard" / "local" / "speckle_connections.json"
)

SPECKLE_IFC_GUID_COLUMN = "speckle_ifc_guid"
INVENTORY_GLOBAL_ID_COLUMN = "inventory_global_id"

EXPECTED_SPECKLE_ROWS_BY_MODEL = {
    "architecture": 15,
    "structural": 18,
    "hvac": 6,
}
EXPECTED_RENDERABLE_BY_MODEL = {
    "architecture": 11,
    "structural": 16,
    "hvac": 5,
}
EXPECTED_NON_RENDERABLE_BY_MODEL = {
    "architecture": 4,
    "structural": 2,
    "hvac": 1,
}

EXPECTED_TABLE_ROWS = {
    "DimModel": 3,
    "DimElement": 39,
    "DimRequirement": 9,
    "DimRun": 1,
    "FactIDSCheck": 31,
    "FactRequirementCoverage": 27,
    "DimTopic": 3,
    "BridgeTopicFinding": 6,
    "BridgeViewpointComponent": 3,
}

EXPECTED_KPIS = {
    "total_elements": 39,
    "evaluated_elements": 17,
    "applicable_pass_numerator": 25,
    "applicable_pass_denominator": 31,
    "failed_checks": 6,
    "noncompliant_elements": 3,
    "bcf_lineage_numerator": 6,
    "bcf_lineage_denominator": 6,
    "open_topics": 3,
}

EXPECTED_DISCIPLINE_ACCEPTANCE = {
    "Architecture": {
        "pass": 8,
        "applicable": 8,
        "fail": 0,
        "noncompliant_elements": 0,
    },
    "Structural": {
        "pass": 14,
        "applicable": 14,
        "fail": 0,
        "noncompliant_elements": 0,
    },
    "HVAC": {
        "pass": 3,
        "applicable": 9,
        "fail": 6,
        "noncompliant_elements": 3,
    },
}

EXPECTED_SPECKLE_MAPPING_CONTRACT = {
    "local_path": "dashboard/local/speckle_mapping.csv",
    "business_key": ["model_id", SPECKLE_IFC_GUID_COLUMN],
    "cross_check": INVENTORY_GLOBAL_ID_COLUMN,
    "connector_identity_fields": {
        "modern": {
            "primary": 'data.properties["IFC GUID"]',
            "cross_check": 'data.properties["IFC Attributes"]["GlobalId"]',
        },
        "legacy_direct_ifc": {
            "primary": 'data.properties["Attributes"]["GlobalId"]',
            "cross_check": 'properties["GlobalId"]',
        },
        "minimum_agreeing_evidence": 2,
        "forbidden_identity": "data.applicationId",
    },
    "forbidden_business_keys": [
        "applicationId",
        "speckle_object_id",
        "bare_speckle_ifc_guid",
    ],
    "expected": {
        "semantic_rows": 39,
        "semantic_rows_by_model": EXPECTED_SPECKLE_ROWS_BY_MODEL,
        "missing": 0,
        "ambiguous": 0,
        "duplicate": 0,
        "unique_speckle_object_ids": 39,
        "renderable": 32,
        "renderable_by_model": EXPECTED_RENDERABLE_BY_MODEL,
        "non_renderable": 7,
        "non_renderable_by_model": EXPECTED_NON_RENDERABLE_BY_MODEL,
        "issue_mapped_renderable_highlighted": 3,
        "fixed_model_version_urls": 3,
    },
}

EXPECTED_SPECKLE_CONNECTIONS_CONTRACT = {
    "local_path": "dashboard/local/speckle_connections.json",
    "required_fields": ["federation_url", "models"],
    "federation_url_role": "audit_only",
    "model_entry_fields": [
        "model_id",
        "model_version_url",
        "source_filename",
        "ifc_sha256",
        "upload_route",
    ],
    "model_ids": ["architecture", "structural", "hvac"],
    "model_count": 3,
    "required_upload_route": "direct_ifc",
    "reconcile_with": {
        "path": "data/processed/models.csv",
        "source_filename": "filename",
        "ifc_sha256": "content_sha256",
    },
}

EXPECTED_RELATIONSHIPS = {
    (
        "DimModel_DimElement",
        "DimModel.model_id",
        "DimElement.model_id",
        "single",
        True,
    ),
    (
        "DimModel_FactRequirementCoverage",
        "DimModel.model_id",
        "FactRequirementCoverage.model_id",
        "single",
        True,
    ),
    (
        "DimRun_FactIDSCheck",
        "DimRun.run_id",
        "FactIDSCheck.run_id",
        "single",
        True,
    ),
    (
        "DimRun_FactRequirementCoverage",
        "DimRun.run_id",
        "FactRequirementCoverage.run_id",
        "single",
        True,
    ),
    (
        "DimRequirement_FactIDSCheck",
        "DimRequirement.requirement_key",
        "FactIDSCheck.requirement_key",
        "single",
        True,
    ),
    (
        "DimRequirement_FactRequirementCoverage",
        "DimRequirement.requirement_key",
        "FactRequirementCoverage.requirement_key",
        "single",
        True,
    ),
    (
        "DimElement_FactIDSCheck",
        "DimElement.element_key",
        "FactIDSCheck.element_key",
        "both",
        True,
    ),
    (
        "DimElement_DimTopic",
        "DimElement.element_key",
        "DimTopic.element_key",
        "both",
        True,
    ),
}

MODEL_COLUMNS = {
    "model_id",
    "filename",
    "discipline",
    "content_sha256",
}
ELEMENT_COLUMNS = {
    "model_id",
    "element_key",
    "global_id",
    "discipline",
}
FINDING_COLUMNS = {
    "finding_key",
    "run_id",
    "model_id",
    "element_key",
    "global_id",
    "specification_id",
    "requirement_id",
    "requirement_key",
    "status",
    "is_applicable",
    "is_issue",
}
TOPIC_COLUMNS = {
    "run_id",
    "topic_guid",
    "topic_status",
    "model_id",
    "element_key",
    "global_id",
    "finding_count",
}
TOPIC_FINDING_COLUMNS = {
    "run_id",
    "topic_guid",
    "finding_key",
    "requirement_key",
    "model_id",
    "element_key",
    "global_id",
}
VIEWPOINT_COLUMNS = {
    "run_id",
    "viewpoint_guid",
    "topic_guid",
    "model_id",
    "element_key",
    "global_id",
}
COMPONENT_COLUMNS = {
    "run_id",
    "viewpoint_guid",
    "topic_guid",
    "component_index",
    "model_id",
    "element_key",
    "global_id",
}
MAPPING_COLUMNS = {
    "model_id",
    SPECKLE_IFC_GUID_COLUMN,
    INVENTORY_GLOBAL_ID_COLUMN,
    "speckle_object_id",
    "speckle_model_version_url",
    "has_representation",
    "highlight_verified",
}


class DashboardValidationError(ValueError):
    """Raised when a dashboard acceptance invariant is violated."""


@dataclass(frozen=True)
class CoreData:
    models: list[dict[str, str]]
    elements: list[dict[str, str]]
    findings: list[dict[str, str]]
    models_by_id: dict[str, dict[str, str]]
    elements_by_key: dict[str, dict[str, str]]
    elements_by_business_key: dict[tuple[str, str], dict[str, str]]
    findings_by_key: dict[str, dict[str, str]]
    issue_findings: list[dict[str, str]]
    issue_element_keys: frozenset[str]
    run_id: str
    summary: dict[str, Any]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DashboardValidationError(message)


def _read_csv(
    path: Path,
    required_columns: set[str],
    *,
    exact_columns: bool = False,
) -> list[dict[str, str]]:
    if not path.is_file():
        raise DashboardValidationError(f"Required CSV is missing: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        _require(len(fieldnames) == len(set(fieldnames)), f"Duplicate CSV header: {path}")
        missing = sorted(required_columns - set(fieldnames))
        _require(not missing, f"Missing columns in {path.name}: {', '.join(missing)}")
        if exact_columns:
            unexpected = sorted(set(fieldnames) - required_columns)
            _require(
                not unexpected,
                f"Unexpected columns in {path.name}: {', '.join(unexpected)}",
            )
        return [
            {key: "" if value is None else value for key, value in row.items()}
            for row in reader
        ]


def _parse_bool(value: str, label: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise DashboardValidationError(f"{label} must be true or false, got {value!r}")


def _require_unique(rows: Iterable[dict[str, str]], columns: tuple[str, ...], label: str) -> None:
    keys = [tuple(row[column] for column in columns) for row in rows]
    duplicates = [key for key, count in Counter(keys).items() if count > 1]
    _require(not duplicates, f"Duplicate {label}: {duplicates[:3]}")


def _require_lower_uuid(value: str, label: str) -> None:
    try:
        parsed = uuid.UUID(value)
    except ValueError as exc:
        raise DashboardValidationError(f"Invalid {label}: {value!r}") from exc
    _require(str(parsed) == value, f"{label} must be a canonical lowercase UUID: {value}")


def validate_contract(path: Path = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    if not path.is_file():
        raise DashboardValidationError(f"Dashboard contract is missing: {path}")
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DashboardValidationError(f"Cannot read dashboard contract: {path}") from exc

    _require(contract.get("contract_version") == "0.1", "Contract version drift detected")
    _require(
        contract.get("artifact_type") == "implementation-specification-only",
        "Contract must remain an implementation specification only",
    )
    _require(contract.get("not_a_pbip") is True, "Contract must declare not_a_pbip=true")
    semantic = contract.get("semantic_model", {})
    _require(
        semantic.get("auto_detect_relationships") is False,
        "Relationship auto-detection must be disabled",
    )
    _require(
        semantic.get("tables") == EXPECTED_TABLE_ROWS,
        "The semantic model must contain the locked nine-table row contract",
    )

    relationships = {
        (
            item.get("name"),
            item.get("one"),
            item.get("many"),
            item.get("cross_filter"),
            item.get("active"),
        )
        for item in semantic.get("relationships", [])
    }
    _require(relationships == EXPECTED_RELATIONSHIPS, "Relationship contract drift detected")
    _require(
        sorted(semantic.get("disconnected_hidden_tables", []))
        == ["BridgeTopicFinding", "BridgeViewpointComponent"],
        "Both bridge tables must be hidden and disconnected",
    )

    _require(
        contract.get("speckle_mapping") == EXPECTED_SPECKLE_MAPPING_CONTRACT,
        "Speckle mapping contract drift detected",
    )
    _require(
        contract.get("speckle_connections")
        == EXPECTED_SPECKLE_CONNECTIONS_CONTRACT,
        "Speckle connections contract drift detected",
    )
    _require(contract.get("kpis") == EXPECTED_KPIS, "KPI contract drift detected")
    _require(
        contract.get("discipline_acceptance") == EXPECTED_DISCIPLINE_ACCEPTANCE,
        "Discipline acceptance contract drift detected",
    )
    return contract


def validate_core(processed_dir: Path = DEFAULT_PROCESSED_DIR) -> CoreData:
    models = _read_csv(processed_dir / "models.csv", MODEL_COLUMNS)
    elements = _read_csv(processed_dir / "model_inventory.csv", ELEMENT_COLUMNS)
    findings = _read_csv(processed_dir / "ids_findings.csv", FINDING_COLUMNS)

    _require(len(models) == 3, f"DimModel must have 3 rows, got {len(models)}")
    _require_unique(models, ("model_id",), "model_id")
    models_by_id = {row["model_id"]: row for row in models}
    _require(
        set(models_by_id) == {"architecture", "structural", "hvac"},
        "Expected architecture, structural, and hvac model_id values",
    )

    _require(len(elements) == 39, f"DimElement must have 39 rows, got {len(elements)}")
    _require_unique(elements, ("element_key",), "element_key")
    _require_unique(elements, ("model_id", "global_id"), "federated element identity")
    elements_by_key: dict[str, dict[str, str]] = {}
    elements_by_business_key: dict[tuple[str, str], dict[str, str]] = {}
    for row in elements:
        _require(row["model_id"] in models_by_id, f"Unknown inventory model_id: {row['model_id']}")
        expected_key = f"{row['model_id']}::{row['global_id']}"
        _require(row["element_key"] == expected_key, f"Invalid element_key: {row['element_key']}")
        elements_by_key[row["element_key"]] = row
        elements_by_business_key[(row["model_id"], row["global_id"])] = row
    _require(
        len({row["global_id"] for row in elements}) == 32,
        "Bare IFC GUID cardinality must remain 32; it is not a federated key",
    )

    _require(len(findings) == 47, f"IDS findings must have 47 rows, got {len(findings)}")
    _require_unique(findings, ("finding_key",), "finding_key")
    findings_by_key = {row["finding_key"]: row for row in findings}
    run_ids = {row["run_id"] for row in findings}
    _require(len(run_ids) == 1, f"DimRun must have 1 row, got {len(run_ids)}")
    run_id = next(iter(run_ids))

    requirement_identity: dict[str, tuple[str, str]] = {}
    status_counts = Counter(row["status"] for row in findings)
    _require(
        status_counts == Counter({"PASS": 25, "FAIL": 6, "N/A": 16}),
        f"IDS status counts changed: {dict(status_counts)}",
    )
    for row in findings:
        _require(row["model_id"] in models_by_id, f"Unknown finding model_id: {row['model_id']}")
        applicable = _parse_bool(row["is_applicable"], "is_applicable")
        issue = _parse_bool(row["is_issue"], "is_issue")
        _require(
            applicable == (row["status"] in {"PASS", "FAIL"}),
            f"is_applicable conflicts with status for {row['finding_key']}",
        )
        _require(
            issue == (row["status"] == "FAIL"),
            f"is_issue conflicts with status for {row['finding_key']}",
        )
        identity = (row["specification_id"], row["requirement_id"])
        previous = requirement_identity.setdefault(row["requirement_key"], identity)
        _require(previous == identity, f"Ambiguous requirement_key: {row['requirement_key']}")
        if applicable:
            element = elements_by_key.get(row["element_key"])
            _require(element is not None, f"Finding references unknown element: {row['element_key']}")
            _require(element["model_id"] == row["model_id"], "Finding model identity conflict")
            _require(element["global_id"] == row["global_id"], "Finding IFC GUID conflict")
        else:
            _require(not row["element_key"] and not row["global_id"], "N/A finding has element identity")

    applicable_findings = [row for row in findings if row["status"] in {"PASS", "FAIL"}]
    issue_findings = [row for row in findings if row["status"] == "FAIL"]
    issue_element_keys = frozenset(row["element_key"] for row in issue_findings)
    coverage_keys = {
        (row["run_id"], row["model_id"], row["requirement_key"])
        for row in findings
    }
    _require(len(requirement_identity) == 9, "DimRequirement must have 9 rows")
    _require(len(applicable_findings) == 31, "FactIDSCheck must have 31 applicable rows")
    _require(len(coverage_keys) == 27, "FactRequirementCoverage must have 27 rows")
    _require(
        len({row["element_key"] for row in applicable_findings}) == 17,
        "Evaluated Elements must equal 17",
    )
    _require(len(issue_element_keys) == 3, "Noncompliant Elements must equal 3")

    discipline_acceptance: dict[str, dict[str, int]] = {}
    for discipline in ("Architecture", "Structural", "HVAC"):
        rows = [
            row
            for row in applicable_findings
            if models_by_id[row["model_id"]]["discipline"] == discipline
        ]
        failed = [row for row in rows if row["status"] == "FAIL"]
        discipline_acceptance[discipline] = {
            "pass": sum(row["status"] == "PASS" for row in rows),
            "applicable": len(rows),
            "fail": len(failed),
            "noncompliant_elements": len({row["element_key"] for row in failed}),
        }
    _require(
        discipline_acceptance == EXPECTED_DISCIPLINE_ACCEPTANCE,
        f"Discipline acceptance changed: {discipline_acceptance}",
    )

    summary = {
        "table_rows": {
            "DimModel": len(models),
            "DimElement": len(elements),
            "DimRequirement": len(requirement_identity),
            "DimRun": len(run_ids),
            "FactIDSCheck": len(applicable_findings),
            "FactRequirementCoverage": len(coverage_keys),
        },
        "kpis": {
            "total_elements": len(elements),
            "evaluated_elements": len({row["element_key"] for row in applicable_findings}),
            "applicable_pass_numerator": status_counts["PASS"],
            "applicable_pass_denominator": len(applicable_findings),
            "applicable_pass_rate": status_counts["PASS"] / len(applicable_findings),
            "failed_checks": status_counts["FAIL"],
            "noncompliant_elements": len(issue_element_keys),
        },
        "discipline_acceptance": discipline_acceptance,
    }
    return CoreData(
        models=models,
        elements=elements,
        findings=findings,
        models_by_id=models_by_id,
        elements_by_key=elements_by_key,
        elements_by_business_key=elements_by_business_key,
        findings_by_key=findings_by_key,
        issue_findings=issue_findings,
        issue_element_keys=issue_element_keys,
        run_id=run_id,
        summary=summary,
    )


def validate_bcf_sidecars(core: CoreData, processed_dir: Path) -> dict[str, Any]:
    topics = _read_csv(processed_dir / "bcf_topics.csv", TOPIC_COLUMNS)
    links = _read_csv(processed_dir / "bcf_topic_findings.csv", TOPIC_FINDING_COLUMNS)
    viewpoints = _read_csv(processed_dir / "bcf_viewpoints.csv", VIEWPOINT_COLUMNS)
    components = _read_csv(
        processed_dir / "bcf_viewpoint_components.csv",
        COMPONENT_COLUMNS,
    )
    _require(len(topics) == 3, f"DimTopic must have 3 rows, got {len(topics)}")
    _require(len(links) == 6, f"BridgeTopicFinding must have 6 rows, got {len(links)}")
    _require(len(viewpoints) == 3, f"Expected 3 viewpoints, got {len(viewpoints)}")
    _require(
        len(components) == 3,
        f"BridgeViewpointComponent must have 3 rows, got {len(components)}",
    )
    _require_unique(topics, ("topic_guid",), "topic_guid")
    _require_unique(topics, ("element_key",), "topic element_key")
    _require_unique(links, ("topic_guid", "finding_key"), "topic finding link")
    _require_unique(viewpoints, ("viewpoint_guid",), "viewpoint_guid")
    _require_unique(viewpoints, ("topic_guid",), "topic viewpoint")
    _require_unique(components, ("viewpoint_guid", "component_index"), "viewpoint component")

    topics_by_guid: dict[str, dict[str, str]] = {}
    for topic in topics:
        _require_lower_uuid(topic["topic_guid"], "topic_guid")
        _require(topic["run_id"] == core.run_id, "Topic run_id conflicts with IDS run")
        _require(topic["topic_status"] == "Open", "All three dashboard topics must be Open")
        _require(topic["element_key"] in core.issue_element_keys, "Topic is not an issue element")
        element = core.elements_by_key[topic["element_key"]]
        _require(topic["model_id"] == element["model_id"], "Topic model identity conflict")
        _require(topic["global_id"] == element["global_id"], "Topic IFC GUID conflict")
        try:
            finding_count = int(topic["finding_count"])
        except ValueError as exc:
            raise DashboardValidationError("Topic finding_count must be an integer") from exc
        _require(finding_count == 2, "Each topic must declare exactly two findings")
        topics_by_guid[topic["topic_guid"]] = topic
    _require(
        {topic["element_key"] for topic in topics} == set(core.issue_element_keys),
        "Topics must cover exactly the three noncompliant elements",
    )

    expected_finding_keys = {row["finding_key"] for row in core.issue_findings}
    linked_finding_keys: set[str] = set()
    links_by_topic: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for link in links:
        topic = topics_by_guid.get(link["topic_guid"])
        _require(topic is not None, f"Link references unknown topic: {link['topic_guid']}")
        finding = core.findings_by_key.get(link["finding_key"])
        _require(finding is not None and finding["status"] == "FAIL", "Link is not a FAIL finding")
        for column in ("run_id", "model_id", "element_key", "global_id", "requirement_key"):
            _require(link[column] == finding[column], f"Link {column} conflicts with finding")
        _require(link["element_key"] == topic["element_key"], "Link conflicts with topic element")
        linked_finding_keys.add(link["finding_key"])
        links_by_topic[link["topic_guid"]].append(link)
    _require(linked_finding_keys == expected_finding_keys, "BCF lineage must cover all 6 FAIL findings")
    _require(
        all(len(topic_links) == 2 for topic_links in links_by_topic.values())
        and set(links_by_topic) == set(topics_by_guid),
        "Each topic must link exactly two findings",
    )

    viewpoints_by_guid: dict[str, dict[str, str]] = {}
    for viewpoint in viewpoints:
        _require_lower_uuid(viewpoint["viewpoint_guid"], "viewpoint_guid")
        topic = topics_by_guid.get(viewpoint["topic_guid"])
        _require(topic is not None, "Viewpoint references unknown topic")
        for column in ("run_id", "model_id", "element_key", "global_id"):
            _require(viewpoint[column] == topic[column], f"Viewpoint {column} conflicts with topic")
        viewpoints_by_guid[viewpoint["viewpoint_guid"]] = viewpoint

    component_count_by_viewpoint: Counter[str] = Counter()
    for component in components:
        viewpoint = viewpoints_by_guid.get(component["viewpoint_guid"])
        _require(viewpoint is not None, "Component references unknown viewpoint")
        _require(component["topic_guid"] == viewpoint["topic_guid"], "Component topic conflict")
        for column in ("run_id", "model_id", "element_key", "global_id"):
            _require(component[column] == viewpoint[column], f"Component {column} conflict")
        _require(component["component_index"] == "1", "Each viewpoint must select one component")
        component_count_by_viewpoint[component["viewpoint_guid"]] += 1
    _require(
        set(component_count_by_viewpoint) == set(viewpoints_by_guid)
        and all(count == 1 for count in component_count_by_viewpoint.values()),
        "Each viewpoint must contain exactly one component",
    )

    return {
        "table_rows": {
            "DimTopic": len(topics),
            "BridgeTopicFinding": len(links),
            "BridgeViewpointComponent": len(components),
        },
        "open_topics": sum(topic["topic_status"] == "Open" for topic in topics),
        "bcf_lineage_numerator": len(linked_finding_keys),
        "bcf_lineage_denominator": len(expected_finding_keys),
        "topic_linked_finding_counts": {
            topic_guid: len(topic_links)
            for topic_guid, topic_links in sorted(links_by_topic.items())
        },
    }


def _validate_absolute_nonplaceholder_https_url(value: Any, label: str) -> str:
    _require(isinstance(value, str), f"{label} must be a string")
    _require(value == value.strip() and bool(value), f"{label} must not be blank or padded")
    parsed = urlparse(value)
    _require(
        parsed.scheme == "https" and bool(parsed.netloc),
        f"{label} must be an absolute HTTPS URL: {value!r}",
    )
    hostname = (parsed.hostname or "").lower()
    reserved_hostname = (
        hostname in {"localhost", "example.com", "example.net", "example.org"}
        or hostname.endswith((".localhost", ".example", ".invalid", ".test"))
    )
    lowered = value.lower()
    _require(
        not reserved_hostname
        and not any(token in lowered for token in ("replace", "placeholder", "<", ">")),
        f"{label} cannot use a placeholder URL: {value!r}",
    )
    return value


def _validate_model_version_url(value: str) -> None:
    _validate_absolute_nonplaceholder_https_url(value, "Speckle model/version URL")
    parsed = urlparse(value)
    _require("/models/" in parsed.path and "@" in parsed.path, f"URL is not version-pinned: {value}")


def _validate_sha256(value: Any, label: str) -> str:
    _require(isinstance(value, str), f"{label} must be a string")
    _require(
        re.fullmatch(r"[0-9a-f]{64}", value) is not None,
        f"{label} must be a lowercase 64-character SHA-256 digest",
    )
    return value


def validate_speckle_mapping(core: CoreData, mapping_path: Path) -> dict[str, Any]:
    rows = _read_csv(
        mapping_path,
        MAPPING_COLUMNS,
        exact_columns=True,
    )
    _require(len(rows) == 39, f"Semantic identity mapping must have 39 rows, got {len(rows)}")

    business_keys = [
        (row["model_id"], row[SPECKLE_IFC_GUID_COLUMN])
        for row in rows
    ]
    duplicate_business_keys = [key for key, count in Counter(business_keys).items() if count > 1]
    _require(not duplicate_business_keys, f"Duplicate/ambiguous Speckle business keys: {duplicate_business_keys[:3]}")
    _require_unique(rows, ("speckle_object_id",), "Speckle object ID")

    rows_by_model = Counter(row["model_id"] for row in rows)
    _require(
        dict(rows_by_model) == EXPECTED_SPECKLE_ROWS_BY_MODEL,
        "Speckle semantic row distribution must be "
        "architecture=15, structural=18, hvac=6; "
        f"got {dict(rows_by_model)}",
    )

    expected_keys = set(core.elements_by_business_key)
    actual_keys = set(business_keys)
    missing = sorted(expected_keys - actual_keys)
    unexpected = sorted(actual_keys - expected_keys)
    _require(not missing, f"Missing Speckle semantic mappings: {missing[:3]}")
    _require(not unexpected, f"Unknown Speckle semantic mappings: {unexpected[:3]}")

    urls_by_model: defaultdict[str, set[str]] = defaultdict(set)
    renderable_by_model: Counter[str] = Counter()
    non_renderable_by_model: Counter[str] = Counter()
    highlighted_elements: set[str] = set()
    highlighted_issue_elements: set[str] = set()
    for row in rows:
        model_id = row["model_id"]
        ifc_guid = row[SPECKLE_IFC_GUID_COLUMN]
        _require(ifc_guid, "speckle_ifc_guid must not be empty")
        _require(
            ifc_guid == row[INVENTORY_GLOBAL_ID_COLUMN],
            f"IFC GUID cross-check failed for ({model_id}, {ifc_guid})",
        )
        _require(row["speckle_object_id"], "speckle_object_id must not be empty")
        element = core.elements_by_business_key[(model_id, ifc_guid)]
        _require(
            row[INVENTORY_GLOBAL_ID_COLUMN] == element["global_id"],
            f"Inventory GlobalId conflict for {element['element_key']}",
        )
        has_representation = _parse_bool(row["has_representation"], "has_representation")
        highlight_verified = _parse_bool(row["highlight_verified"], "highlight_verified")
        if has_representation:
            renderable_by_model[model_id] += 1
        else:
            non_renderable_by_model[model_id] += 1
        _require(
            not highlight_verified or has_representation,
            f"Non-renderable element cannot be marked highlighted: {element['element_key']}",
        )
        if highlight_verified:
            highlighted_elements.add(element["element_key"])
        if element["element_key"] in core.issue_element_keys:
            _require(has_representation, f"Issue element is not renderable: {element['element_key']}")
            _require(highlight_verified, f"Issue element highlight is not verified: {element['element_key']}")
            highlighted_issue_elements.add(element["element_key"])
        url = row["speckle_model_version_url"]
        _validate_model_version_url(url)
        urls_by_model[model_id].add(url)

    _require(
        dict(renderable_by_model) == EXPECTED_RENDERABLE_BY_MODEL,
        "Renderable mapping distribution must be "
        "architecture=11, structural=16, hvac=5; "
        f"got {dict(renderable_by_model)}",
    )
    _require(
        dict(non_renderable_by_model) == EXPECTED_NON_RENDERABLE_BY_MODEL,
        "Non-renderable mapping distribution must be "
        "architecture=4, structural=2, hvac=1; "
        f"got {dict(non_renderable_by_model)}",
    )
    _require(
        set(urls_by_model) == set(core.models_by_id)
        and all(len(urls) == 1 for urls in urls_by_model.values()),
        "Each model_id must map to exactly one fixed Speckle model/version URL",
    )
    fixed_urls = {next(iter(urls)) for urls in urls_by_model.values()}
    _require(len(fixed_urls) == 3, "The three model_id values must use three distinct version URLs")
    _require(
        highlighted_issue_elements == set(core.issue_element_keys),
        "Issue workflow mapping must be 3/3 mapped, renderable, and highlighted",
    )
    _require(
        highlighted_elements == set(core.issue_element_keys),
        "Exactly the three issue elements must have highlight_verified=true",
    )
    renderable = sum(renderable_by_model.values())
    non_renderable = sum(non_renderable_by_model.values())
    return {
        "semantic_identity": {
            "mapped": len(rows),
            "expected": 39,
            "mapped_by_model": dict(sorted(rows_by_model.items())),
            "missing": 0,
            "ambiguous": 0,
            "duplicate": 0,
            "unique_speckle_object_ids": len(
                {row["speckle_object_id"] for row in rows}
            ),
        },
        "render_mapping": {
            "renderable": renderable,
            "expected_renderable": 32,
            "renderable_by_model": dict(sorted(renderable_by_model.items())),
            "non_renderable": non_renderable,
            "non_renderable_by_model": dict(
                sorted(non_renderable_by_model.items())
            ),
        },
        "issue_workflow": {
            "mapped_renderable_highlighted": len(highlighted_issue_elements),
            "expected": 3,
        },
        "fixed_model_version_urls": len(fixed_urls),
        "model_version_urls": {
            model_id: next(iter(urls))
            for model_id, urls in sorted(urls_by_model.items())
        },
    }


def validate_speckle_connections(
    core: CoreData,
    mapping: dict[str, Any],
    connections_path: Path,
) -> dict[str, Any]:
    if not connections_path.is_file():
        raise DashboardValidationError(
            f"Speckle connections JSON is missing: {connections_path}"
        )
    try:
        connections = json.loads(connections_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DashboardValidationError(
            f"Cannot read Speckle connections JSON: {connections_path}"
        ) from exc

    _require(isinstance(connections, dict), "Speckle connections must be a JSON object")
    _require(
        set(connections) == {"federation_url", "models"},
        "Speckle connections must contain exactly federation_url and models",
    )
    federation_url = _validate_absolute_nonplaceholder_https_url(
        connections["federation_url"],
        "Speckle federation_url",
    )
    models = connections["models"]
    _require(isinstance(models, list), "Speckle connections models must be an array")
    _require(len(models) == 3, f"Speckle connections must contain 3 models, got {len(models)}")

    urls_by_model: dict[str, str] = {}
    source_filenames_by_model: dict[str, str] = {}
    ifc_sha256_by_model: dict[str, str] = {}
    upload_routes_by_model: dict[str, str] = {}
    expected_entry_fields = set(
        EXPECTED_SPECKLE_CONNECTIONS_CONTRACT["model_entry_fields"]
    )
    for index, model in enumerate(models):
        _require(isinstance(model, dict), f"Speckle model entry {index} must be an object")
        _require(
            set(model) == expected_entry_fields,
            f"Speckle model entry {index} has contract drift",
        )
        model_id = model["model_id"]
        _require(isinstance(model_id, str), f"Speckle model entry {index} model_id must be text")
        _require(model_id not in urls_by_model, f"Duplicate Speckle connection model_id: {model_id}")
        _require(
            model_id in core.models_by_id,
            f"Unknown Speckle connection model_id: {model_id}",
        )
        model_url = model["model_version_url"]
        _validate_model_version_url(model_url)
        source_filename = model["source_filename"]
        _require(
            isinstance(source_filename, str)
            and source_filename == source_filename.strip()
            and bool(source_filename),
            f"Speckle source_filename for {model_id} must be non-blank, unpadded text",
        )
        ifc_sha256 = _validate_sha256(
            model["ifc_sha256"],
            f"Speckle ifc_sha256 for {model_id}",
        )
        upload_route = model["upload_route"]
        _require(
            upload_route == "direct_ifc",
            f"Speckle upload_route for {model_id} must be direct_ifc",
        )

        source_model = core.models_by_id[model_id]
        _require(
            source_filename == source_model["filename"],
            f"Speckle source_filename for {model_id} must exactly match models.csv filename",
        )
        _validate_sha256(
            source_model["content_sha256"],
            f"models.csv content_sha256 for {model_id}",
        )
        _require(
            ifc_sha256 == source_model["content_sha256"],
            f"Speckle ifc_sha256 for {model_id} must exactly match models.csv content_sha256",
        )
        urls_by_model[model_id] = model_url
        source_filenames_by_model[model_id] = source_filename
        ifc_sha256_by_model[model_id] = ifc_sha256
        upload_routes_by_model[model_id] = upload_route

    expected_urls = mapping["model_version_urls"]
    _require(
        set(urls_by_model) == {"architecture", "structural", "hvac"},
        "Speckle connections must map architecture, structural, and hvac one-to-one",
    )
    _require(
        urls_by_model == expected_urls,
        "Speckle connection model/version URLs must exactly match the mapping CSV",
    )
    _require(
        federation_url not in set(urls_by_model.values()),
        "Speckle federation_url must be distinct from the three source model/version URLs",
    )
    return {
        "federation_url": federation_url,
        "federation_url_role": "audit_only",
        "model_count": len(urls_by_model),
        "model_version_urls": dict(sorted(urls_by_model.items())),
        "source_filenames": dict(sorted(source_filenames_by_model.items())),
        "ifc_sha256": dict(sorted(ifc_sha256_by_model.items())),
        "upload_routes": dict(sorted(upload_routes_by_model.items())),
    }


def validate_dashboard(
    *,
    processed_dir: Path = DEFAULT_PROCESSED_DIR,
    mapping_path: Path = DEFAULT_MAPPING_PATH,
    connections_path: Path = DEFAULT_CONNECTIONS_PATH,
    contract_path: Path = DEFAULT_CONTRACT_PATH,
    mode: str = "full",
) -> dict[str, Any]:
    _require(mode in {"core", "full"}, f"Unknown validation mode: {mode}")
    validate_contract(contract_path)
    core = validate_core(processed_dir)
    result: dict[str, Any] = {
        "contract_version": "0.1",
        "mode": mode,
        "table_rows": dict(core.summary["table_rows"]),
        "kpis": dict(core.summary["kpis"]),
        "discipline_acceptance": core.summary["discipline_acceptance"],
    }
    if mode == "core":
        result["acceptance"] = "CORE_ONLY_NOT_STAGE_3B_COMPLETE"
        return result

    bcf = validate_bcf_sidecars(core, processed_dir)
    mapping = validate_speckle_mapping(core, mapping_path)
    connections = validate_speckle_connections(core, mapping, connections_path)
    result["table_rows"].update(bcf["table_rows"])
    _require(result["table_rows"] == EXPECTED_TABLE_ROWS, "Nine-table row contract failed")
    result["kpis"].update(
        {
            "bcf_lineage_numerator": bcf["bcf_lineage_numerator"],
            "bcf_lineage_denominator": bcf["bcf_lineage_denominator"],
            "bcf_lineage_coverage": (
                bcf["bcf_lineage_numerator"] / bcf["bcf_lineage_denominator"]
            ),
            "open_topics": bcf["open_topics"],
        }
    )
    _require(result["kpis"]["open_topics"] == 3, "Open Topics must equal 3")
    _require(result["kpis"]["bcf_lineage_coverage"] == 1.0, "BCF lineage must be 6/6")
    result["topic_linked_finding_counts"] = bcf["topic_linked_finding_counts"]
    result["speckle_mapping"] = mapping
    result["speckle_connections"] = connections
    result["acceptance"] = "OFFLINE_DATA_CONTRACT_PASSED"
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("core", "full"),
        default="full",
        help="core validates repository data only; full is the fail-closed Stage 3B gate",
    )
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING_PATH)
    parser.add_argument("--connections", type=Path, default=DEFAULT_CONNECTIONS_PATH)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        result = validate_dashboard(
            processed_dir=args.processed_dir.resolve(),
            mapping_path=args.mapping.resolve(),
            connections_path=args.connections.resolve(),
            contract_path=args.contract.resolve(),
            mode=args.mode,
        )
    except DashboardValidationError as exc:
        print(f"Dashboard validation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
