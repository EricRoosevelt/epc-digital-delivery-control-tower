"""The BCF 3.0 exporter as it exists today — legacy, and named so.

The name is not modesty. This implementation still knows things a BCF exporter
has no business knowing: that the failures it converts belong to the R-005
family, and that they are in the HVAC model. Those checks are reproduced from
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

from pathlib import Path
from xml.etree import ElementTree as ET

from ..bcf.archive import build_deterministic_zip
from ..bcf.schema import validate_xml_schemas, verify_schema_bundle, xml_bytes
from ..determinism import atomic_write_bytes, format_float, sha256_bytes
from ..domain import RunBundle
from ..protocols import Artifact
from .legacy_contract import (
    ASSIGNEE,
    BCF_VERSION,
    CREATION_AUTHOR,
    FINDING_URN_PREFIX,
    PROJECT_GUID,
    PROJECT_NAME,
    TOPIC_LABELS,
    TOPIC_PRIORITY,
    TOPIC_STAGE,
    TOPIC_STATUS,
    TOPIC_TYPE,
)
from .legacy_projection import LegacyProjection, LegacyTopic, project_bundle

__all__ = ["BCF_FILENAME", "LegacyBcfExporter"]

BCF_FILENAME = "ids_failures.bcf"

#: Rule families this converter is prepared to turn into topics.
#:
#: A pure BCF exporter would not have this list; it would take whatever issues
#: grouping handed it. It is retained because the published archive's contents
#: depend on it, and it goes when the issue lifecycle can carry the priority and
#: labels that are currently constants below.
LEGACY_RULE_SCOPE = frozenset({"R-005A", "R-005B"})

#: The one model the published archive covers.
LEGACY_MODEL_SCOPE = ("hvac", "Building-Hvac.ifc")


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
    ) -> None:
        self._schema_dir = Path(schema_dir)
        self._subdirectory = subdirectory
        #: The single project this archive covers, for the same reason the CSV
        #: adapter has one. The topic GUIDs are derived from element keys, so an
        #: archive spanning two projects would not merely gain topics — it would
        #: republish the existing ones under a different run identity.
        self._project_id = project_id

    def config_sha256(self) -> str:
        return ""

    # -- export ------------------------------------------------------------

    def export(self, bundle: RunBundle, output_root: Path) -> tuple[Artifact, ...]:
        projection = project_bundle(bundle, project_id=self._project_id)
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
        projection = projection or project_bundle(bundle, project_id=self._project_id)
        self._assert_legacy_scope(projection)

        entries = self.root_entries()
        for topic in projection.topics:
            entries[f"{topic.topic_guid}/"] = b""
            entries[f"{topic.topic_guid}/markup.bcf"] = self.markup(topic, bundle.run.as_of)
            entries[f"{topic.topic_guid}/{topic.viewpoint_filename}"] = self.viewpoint(
                topic
            )

        validate_xml_schemas(entries, self._schema_dir)
        return build_deterministic_zip(entries)

    # -- legacy scope ------------------------------------------------------

    def _assert_legacy_scope(self, projection: LegacyProjection) -> None:
        """Refuse work this converter was never written to do.

        Rule-aware and model-aware, and that is the point of the name. The
        published archive's labels, priority and stage are constants chosen for
        one rule family in one discipline, so converting anything else would
        produce topics whose metadata is simply wrong. Better to say so than to
        emit them.

        This is what Phase 4 removes: once priority, stage and assignee come
        from rule metadata, there is nothing left here to be specific about.
        """

        for topic in projection.topics:
            outside = sorted(
                {
                    row.specification_id
                    for row in topic.findings
                    if row.specification_id not in LEGACY_RULE_SCOPE
                }
            )
            if outside:
                raise ValueError(
                    f"{self.id} only converts project-assumed "
                    f"{sorted(LEGACY_RULE_SCOPE)} failures, got {outside}"
                )

            model_id, filename = LEGACY_MODEL_SCOPE
            if topic.model.model_id != model_id or topic.model.filename != filename:
                raise ValueError(
                    f"{self.id} is scoped to {model_id}/{filename}, got "
                    f"{topic.model.model_id}/{topic.model.filename}"
                )

    # -- XML ---------------------------------------------------------------

    @staticmethod
    def root_entries() -> dict[str, bytes]:
        version_root = ET.Element("Version", {"VersionId": BCF_VERSION})

        project_root = ET.Element("ProjectInfo")
        project = ET.SubElement(project_root, "Project", {"ProjectId": PROJECT_GUID})
        _child(project, "Name", PROJECT_NAME)

        extensions_root = ET.Element("Extensions")
        for group_name, item_name, values in (
            ("TopicTypes", "TopicType", [TOPIC_TYPE]),
            ("TopicStatuses", "TopicStatus", [TOPIC_STATUS]),
            ("Priorities", "Priority", [TOPIC_PRIORITY]),
            ("TopicLabels", "TopicLabel", list(TOPIC_LABELS)),
            ("Users", "User", [ASSIGNEE, CREATION_AUTHOR]),
            ("Stages", "Stage", [TOPIC_STAGE]),
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
        _child(markup_topic, "Priority", TOPIC_PRIORITY)
        labels = ET.SubElement(markup_topic, "Labels")
        for label in TOPIC_LABELS:
            _child(labels, "Label", label)
        _child(markup_topic, "CreationDate", as_of)
        _child(markup_topic, "CreationAuthor", CREATION_AUTHOR)
        _child(markup_topic, "AssignedTo", ASSIGNEE)
        _child(markup_topic, "Stage", TOPIC_STAGE)

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
