"""The BCF 3.0 exporter as it exists today — legacy, and named so.

The name is not modesty. This implementation still knows things a BCF exporter
had no business knowing: which rule family the failures it converts belong to,
and which model they are in. Those checks are reproduced from
the previous implementation deliberately, because the published archive is what
they produced and Phase 1's job is to move code without moving bytes. A pure
``BcfExporter`` that consumes issues and events and has no opinion about rule
ids replaces this one; naming it honestly now is what stops that replacement
from being quietly forgotten.

Two assertions from the previous implementation are *not* reproduced: that
there were exactly six failures, and exactly three topics of two findings each.
Those were counts taken from a fixture, and they would have failed the pipeline
rather than the data the first time a model was added or a duct segment fixed.
Grouping enforces the invariant instead.

The exporter opens no IFC file. Bounding boxes arrive in the bundle, computed
by their own stage, because an exporter that reached back to the source models
could not be trusted to produce the same bytes twice.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from xml.etree import ElementTree as ET

from ..bcf.archive import build_deterministic_zip
from ..bcf.schema import validate_xml_schemas, verify_schema_bundle, xml_bytes
from ..determinism import atomic_write_bytes, format_float, sha256_bytes
from ..domain import RuleSet, RunBundle
from ..protocols import Artifact
from .legacy_contract import (
    BCF_VERSION,
    CREATION_AUTHOR,
    FINDING_URN_PREFIX,
    PROJECT_GUID,
    PROJECT_NAME,
    ROLE_DOMAIN,
    TOPIC_STATUS,
    TOPIC_TYPE,
)
from .legacy_projection import LegacyProjection, LegacyTopic, project_bundle

__all__ = ["BCF_FILENAME", "LegacyBcfExporter"]

BCF_FILENAME = "ids_failures.bcf"


def _address(role: str) -> str:
    """Render a role as the address BCF insists on.

    ``.invalid`` is reserved by RFC 2606 precisely so that it cannot resolve,
    which is the point: BCF wants a mailbox and this project has a role.
    """

    return f"{role}@{ROLE_DOMAIN}" if role else ""


def _child(parent: ET.Element, tag: str, text: object) -> ET.Element:
    child = ET.SubElement(parent, tag)
    child.text = str(text)
    return child


def _vector(parent: ET.Element, tag: str, values: tuple[float, float, float]) -> None:
    vector = ET.SubElement(parent, tag)
    for axis, value in zip(("X", "Y", "Z"), values, strict=True):
        _child(vector, axis, format_float(value))


class LegacyBcfExporter:
    """Writes the published ``ids_failures.bcf`` archive."""

    id = "legacy-bcf"
    version = "1.0.0"
    output_root_key = "reports"

    def __init__(
        self,
        *,
        schema_dir: Path,
        subdirectory: str = "bcf",
        project_id: str | None = None,
        frozen_ruleset: RuleSet | None = None,
    ) -> None:
        self._schema_dir = Path(schema_dir)
        self._subdirectory = subdirectory
        #: The single project this archive covers, for the same reason the CSV
        #: adapter has one. The topic GUIDs are derived from element keys, so an
        #: archive spanning two projects would not merely gain topics — it would
        #: republish the existing ones under a different run identity.
        self._project_id = project_id
        self._frozen_ruleset = frozen_ruleset

    def config_sha256(self) -> str:
        return ""

    # -- export ------------------------------------------------------------

    def export(self, bundle: RunBundle, output_root: Path) -> tuple[Artifact, ...]:
        projection = self._project(bundle)
        data = self.build_archive(bundle, projection)
        path = output_root / self._subdirectory / BCF_FILENAME
        atomic_write_bytes(path, data)
        return (
            Artifact(
                path=path,
                sha256=sha256_bytes(data),
                byte_count=len(data),
                exporter_id=self.id,
            ),
        )

    def build_archive(
        self, bundle: RunBundle, projection: LegacyProjection | None = None
    ) -> bytes:
        """Build the archive bytes without writing anything."""

        verify_schema_bundle(self._schema_dir)
        projection = projection or self._project(bundle)

        entries = self.root_entries(projection.topics)
        for topic in projection.topics:
            entries[f"{topic.topic_guid}/"] = b""
            entries[f"{topic.topic_guid}/markup.bcf"] = self.markup(topic, bundle.run.as_of)
            entries[f"{topic.topic_guid}/{topic.viewpoint_filename}"] = self.viewpoint(
                topic
            )

        validate_xml_schemas(entries, self._schema_dir)
        return build_deterministic_zip(entries)

    def _project(self, bundle: RunBundle) -> LegacyProjection:
        return project_bundle(
            bundle,
            project_id=self._project_id,
            frozen_ruleset=self._frozen_ruleset,
        )

    # -- XML ---------------------------------------------------------------

    @staticmethod
    def root_entries(topics: Sequence[LegacyTopic] = ()) -> dict[str, bytes]:
        """The archive-level files.

        The extension vocabulary is collected from the topics rather than
        listed as constants. It produces the same three lists for the
        published archive — measured, not assumed — and it is the only
        version that stays correct when a rule declares a different
        priority or label.
        """

        version_root = ET.Element("Version", {"VersionId": BCF_VERSION})

        project_root = ET.Element("ProjectInfo")
        project = ET.SubElement(project_root, "Project", {"ProjectId": PROJECT_GUID})
        _child(project, "Name", PROJECT_NAME)

        priorities = sorted({t.priority for t in topics if t.priority})
        stages = sorted({t.stage for t in topics if t.stage})
        labels = sorted({label for t in topics for label in t.labels})
        # Assignees first, then whoever wrote the archive. Not alphabetical:
        # the published order puts the people who receive work ahead of the
        # tool that filed it, which is the more useful reading and is what this
        # list has always meant. (Noted plainly: alphabetical was tried first
        # and the diff against the published archive is what revealed the
        # convention.)
        assignees = sorted({_address(t.assignee_role) for t in topics if t.assignee_role})
        users = [*assignees, *([CREATION_AUTHOR] if CREATION_AUTHOR not in assignees else [])]

        extensions_root = ET.Element("Extensions")
        for group_name, item_name, values in (
            ("TopicTypes", "TopicType", [TOPIC_TYPE]),
            ("TopicStatuses", "TopicStatus", [TOPIC_STATUS]),
            ("Priorities", "Priority", priorities),
            ("TopicLabels", "TopicLabel", labels),
            ("Users", "User", users),
            ("Stages", "Stage", stages),
        ):
            group = ET.SubElement(extensions_root, group_name)
            for value in values:
                _child(group, item_name, value)

        return {
            "bcf.version": xml_bytes(version_root),
            "extensions.xml": xml_bytes(extensions_root),
            "project.bcfp": xml_bytes(project_root),
        }

    @staticmethod
    def markup(topic: LegacyTopic, as_of: str) -> bytes:
        root = ET.Element("Markup")
        header = ET.SubElement(root, "Header")
        files = ET.SubElement(header, "Files")
        file_node = ET.SubElement(
            files,
            "File",
            {"IfcProject": topic.model.ifc_project_guid, "IsExternal": "true"},
        )
        _child(file_node, "Filename", topic.model.filename)
        _child(file_node, "Date", as_of)

        markup_topic = ET.SubElement(
            root,
            "Topic",
            {
                "Guid": topic.topic_guid,
                "TopicType": TOPIC_TYPE,
                "TopicStatus": TOPIC_STATUS,
            },
        )
        links = ET.SubElement(markup_topic, "ReferenceLinks")
        for row in topic.findings:
            _child(links, "ReferenceLink", FINDING_URN_PREFIX + row.finding_key)

        _child(markup_topic, "Title", topic.title)
        # Every one of these is `minOccurs="0"` and typed `NonEmptyOrBlankString`,
        # so an absent value is omitted rather than written empty. It matters for
        # more than tidiness: a rule set read from a bare `.ids` document carries
        # no priority, stage or labels at all — IDS 1.0 has nowhere to put them —
        # and writing empty elements makes an archive the schema rejects.
        if topic.priority:
            _child(markup_topic, "Priority", topic.priority)
        if topic.labels:
            labels = ET.SubElement(markup_topic, "Labels")
            for label in topic.labels:
                _child(labels, "Label", label)
        _child(markup_topic, "CreationDate", as_of)
        _child(markup_topic, "CreationAuthor", CREATION_AUTHOR)
        if topic.assignee_role:
            _child(markup_topic, "AssignedTo", _address(topic.assignee_role))
        if topic.stage:
            _child(markup_topic, "Stage", topic.stage)

        requirements = ", ".join(row.requirement for row in topic.findings)
        _child(
            markup_topic,
            "Description",
            (
                "Project-assumed information requirement unmet for "
                f"{topic.element_key}. Required checks: {requirements}. "
                "This workflow classification does not assert a defect in the "
                "source model."
            ),
        )

        viewpoints = ET.SubElement(markup_topic, "Viewpoints")
        viewpoint = ET.SubElement(
            viewpoints, "ViewPoint", {"Guid": topic.viewpoint_guid}
        )
        _child(viewpoint, "Viewpoint", topic.viewpoint_filename)
        return xml_bytes(root)

    @staticmethod
    def viewpoint(topic: LegacyTopic) -> bytes:
        root = ET.Element("VisualizationInfo", {"Guid": topic.viewpoint_guid})
        components = ET.SubElement(root, "Components")
        selection = ET.SubElement(components, "Selection")
        component = ET.SubElement(
            selection, "Component", {"IfcGuid": topic.element.global_id}
        )
        _child(component, "OriginatingSystem", PROJECT_NAME)
        _child(component, "AuthoringToolId", topic.element.global_id)
        ET.SubElement(components, "Visibility", {"DefaultVisibility": "true"})

        perspective = ET.SubElement(root, "PerspectiveCamera")
        _vector(perspective, "CameraViewPoint", topic.camera.position)
        _vector(perspective, "CameraDirection", topic.camera.direction)
        _vector(perspective, "CameraUpVector", topic.camera.up)
        _child(perspective, "FieldOfView", format_float(topic.camera.field_of_view))
        _child(perspective, "AspectRatio", format_float(topic.camera.aspect_ratio))
        return xml_bytes(root)
