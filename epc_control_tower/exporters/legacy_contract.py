"""The published data contract, frozen.

**Do not extend or improve anything here.** Every name in this module exists to
reproduce artifacts that were already published, byte for byte, so that the
tracked Power BI project and the committed evidence keep matching what the
pipeline generates. It retires together with the legacy adapters.

Column order is expressed as field order on a dataclass rather than as a list
of strings. That is the same discipline the canonical exporters use, applied to
the frozen shape: the published order is a property of the row type, so there
is no second list anywhere that could fall out of step with it. It is also the
precise fix for how these files went wrong before — the finding columns were
declared as a twenty-item list in one module and an eleven-item set in another.

The constants below were module-level globals in three different scripts. They
are values of the *legacy* contract, not settings: the assignee is an address
because BCF wanted one and there was nowhere to record a role, and the
timestamp is a constant because run identity had nowhere to put time. Both are
answered properly elsewhere now — a role on the issue, a logical ``as_of`` on
the run — and both are reproduced here only because the published bytes contain
them.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from ..identity import build_requirement_key, uuid5_from_values
from ..legacy_identity import legacy_finding_key

__all__ = [
    "ASSIGNEE",
    "BCF_VERSION",
    "CREATION_AUTHOR",
    "FINDING_URN_PREFIX",
    "FIXED_TIMESTAMP",
    "PROJECT_GUID",
    "PROJECT_NAME",
    "TOPIC_LABELS",
    "TOPIC_PRIORITY",
    "TOPIC_STAGE",
    "TOPIC_STATUS",
    "TOPIC_TYPE",
    "UUID_PATTERN",
    "LegacyComponentRow",
    "LegacyEventRow",
    "LegacyFindingRow",
    "LegacyInventoryRow",
    "LegacyModelRow",
    "LegacyTopicFindingRow",
    "LegacyTopicRow",
    "LegacyViewpointRow",
    "enrich_finding_identity",
    "split_specification",
]

#: The logical date every published artifact is stamped with. Superseded by
#: ``RunConfig.as_of``; kept because the published bytes contain this value.
FIXED_TIMESTAMP = "2026-08-13T00:00:00Z"

BCF_VERSION = "3.0"
PROJECT_NAME = "EPC Digital Delivery Control Tower"
PROJECT_GUID = uuid5_from_values("bcf-project", [PROJECT_NAME])
CREATION_AUTHOR = "control-tower@example.invalid"
ASSIGNEE = "model-coordination@example.invalid"
FINDING_URN_PREFIX = "urn:epc-digital-delivery:finding:"

TOPIC_TYPE = "Issue"
TOPIC_STATUS = "Open"
TOPIC_PRIORITY = "Medium"
TOPIC_STAGE = "Coordination"
TOPIC_LABELS = ("HVAC", "IDS", "ProjectAssumption")

ORIGINATING_SYSTEM = PROJECT_NAME
EVENT_SOURCE = "ANALYTICS_SIDECAR"
EVENT_TYPE_CREATED = "topic_created"

UUID_PATTERN = re.compile(
    r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
)


# ---------------------------------------------------------------------------
# Row shapes. Field order is column order.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LegacyModelRow:
    model_id: str
    filename: str
    discipline: str
    ifc_project_guid: str
    ifc_schema: str
    content_sha256: str
    source_url: str
    license: str


@dataclass(frozen=True, slots=True)
class LegacyInventoryRow:
    model_id: str
    source_model: str
    discipline: str
    element_key: str
    global_id: str
    ifc_class: str
    name: str
    storey: str
    pset_count: int


@dataclass(frozen=True, slots=True)
class LegacyFindingRow:
    finding_key: str
    run_id: str
    model_id: str
    element_key: str
    global_id: str
    ids_version: str
    specification_id: str
    specification: str
    requirement_id: str
    requirement_key: str
    requirement: str
    status: str
    is_applicable: str
    is_issue: str
    severity: str
    ifc_class: str
    element_name: str
    expected: str
    actual: str
    reason: str


@dataclass(frozen=True, slots=True)
class LegacyTopicRow:
    run_id: str
    topic_guid: str
    topic_type: str
    topic_status: str
    title: str
    priority: str
    creation_date: str
    creation_author: str
    assigned_to: str
    stage: str
    model_id: str
    element_key: str
    global_id: str
    ifc_class: str
    element_name: str
    finding_count: int


@dataclass(frozen=True, slots=True)
class LegacyTopicFindingRow:
    run_id: str
    topic_guid: str
    finding_key: str
    requirement_key: str
    specification_id: str
    requirement_id: str
    specification: str
    requirement: str
    severity: str
    model_id: str
    element_key: str
    global_id: str


@dataclass(frozen=True, slots=True)
class LegacyViewpointRow:
    run_id: str
    viewpoint_guid: str
    topic_guid: str
    viewpoint_filename: str
    model_id: str
    element_key: str
    global_id: str
    aabb_min_x: str
    aabb_min_y: str
    aabb_min_z: str
    aabb_max_x: str
    aabb_max_y: str
    aabb_max_z: str
    target_x: str
    target_y: str
    target_z: str
    camera_view_point_x: str
    camera_view_point_y: str
    camera_view_point_z: str
    camera_direction_x: str
    camera_direction_y: str
    camera_direction_z: str
    camera_up_x: str
    camera_up_y: str
    camera_up_z: str
    field_of_view: str
    aspect_ratio: str


@dataclass(frozen=True, slots=True)
class LegacyComponentRow:
    run_id: str
    viewpoint_guid: str
    topic_guid: str
    component_index: int
    model_id: str
    element_key: str
    global_id: str
    originating_system: str
    authoring_tool_id: str


@dataclass(frozen=True, slots=True)
class LegacyEventRow:
    run_id: str
    event_id: str
    topic_guid: str
    event_type: str
    event_date: str
    event_author: str
    value: str
    source: str


# ---------------------------------------------------------------------------
# Reading the published shape back
# ---------------------------------------------------------------------------


def split_specification(value: str) -> tuple[str, str]:
    """Split ``R-001: title`` into its stable identifier and title."""

    identifier, separator, title = value.partition(":")
    if not separator or not identifier.strip() or not title.strip():
        raise ValueError(f"Invalid specification label: {value!r}")
    return identifier.strip(), title.strip()


def enrich_finding_identity(row: Mapping[str, str]) -> dict[str, str]:
    """Return a published finding row with its keys checked, not trusted.

    Every key in a published row is a UUIDv5 over stated inputs, so it can be
    recomputed and compared. A row whose ``finding_key`` does not derive from
    its own payload is rejected rather than carried forward.
    """

    enriched = dict(row)
    label_specification_id, _ = split_specification(enriched["specification"])
    specification_id = enriched.get("specification_id") or label_specification_id
    if specification_id != label_specification_id:
        raise ValueError(
            "specification_id does not match the specification label: "
            f"{specification_id!r}"
        )

    requirement_id = enriched.get("requirement_id") or enriched["requirement"]
    expected_requirement_key = build_requirement_key(specification_id, requirement_id)
    requirement_key = enriched.get("requirement_key") or expected_requirement_key
    if requirement_key != expected_requirement_key:
        raise ValueError(
            "requirement_key does not match its specification/requirement payload: "
            f"{requirement_key!r}"
        )

    expected_finding_key = legacy_finding_key(
        run_id=enriched["run_id"],
        model_id=enriched["model_id"],
        requirement_key=requirement_key,
        element_key=enriched.get("element_key", ""),
    )
    finding_key = enriched.get("finding_key") or expected_finding_key
    if finding_key != expected_finding_key:
        raise ValueError(
            f"finding_key does not match its finding payload: {finding_key!r}"
        )

    if not UUID_PATTERN.fullmatch(requirement_key):
        raise ValueError(f"Invalid requirement_key: {requirement_key!r}")
    if not UUID_PATTERN.fullmatch(finding_key):
        raise ValueError(f"Invalid finding_key: {finding_key!r}")

    enriched["specification_id"] = specification_id
    enriched["requirement_id"] = requirement_id
    enriched["requirement_key"] = requirement_key
    enriched["finding_key"] = finding_key
    return enriched
