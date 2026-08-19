"""BCF 3.0, written from issues and their history and nothing else.

The exporter it replaces is named ``LegacyBcfExporter`` because it knew things a
BCF writer has no business knowing: that the failures it converted belonged to
the R-005 family, that they lived in the HVAC model, and that their priority,
stage, assignee and labels were four constants in a module. It refused to run on
anything else, which was the honest thing to do given those constants — topics
for other rules would have carried metadata that was simply wrong.

This one has no rule ids in it, no filenames, and no counts. It reads an
:class:`~..domain.Issue`, which now carries the metadata the rules state, and
renders it. What it still has is a *scope*, and the distinction matters:

    **Scope is not rule-awareness.** ``LegacyBcfExporter`` asked "is this rule
    R-005A?" and refused otherwise. This one asks "is this issue inside the
    published projection?" — one project, one frozen rule set version — which is
    a statement about which slice of the run is published, not about what any
    rule says. The published archive means *what rule set 0.1 said about the
    PCERT project*, and it goes on meaning that however many rules the current
    library grows.

Two things are deliberately absent.

There is no viewpoint on a topic whose issue names no element. BCF 3.0 makes
``Viewpoints`` optional (``markup.xsd``, ``minOccurs="0"``) while making a
camera *required* inside a ``VisualizationInfo`` — so a viewpoint must point
somewhere, and an issue about something that is not modelled has nowhere to
point. Framing the whole model instead would aim a camera at a place where
nothing is wrong; dropping the topic would drop a real failure from the
deliverable. The topic stays, without a view.

And no IFC file is opened. Bounding boxes arrive in the bundle from their own
stage, because an exporter that reached back to the source models could not be
trusted to produce the same bytes twice.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from xml.etree import ElementTree as ET

from ..bcf.archive import build_deterministic_zip
from ..bcf.geometry import Aabb, camera_for_aabb
from ..bcf.schema import validate_xml_schemas, verify_schema_bundle, xml_bytes
from ..determinism import atomic_write_bytes, format_float, sha256_bytes
from ..domain import (
    Element,
    Finding,
    Issue,
    Requirement,
    RuleSet,
    RunBundle,
)
from ..identity import uuid5_from_values
from ..protocols import Artifact

__all__ = ["BCF_FILENAME", "BcfExporter"]

BCF_FILENAME = "issues.bcf"

BCF_VERSION = "3.0"

#: The URN each topic uses to reference the findings behind it. A topic is an
#: actionable grouping; the findings are the evidence, and BCF's
#: ``ReferenceLink`` is where evidence that lives outside the archive goes.
FINDING_URN_PREFIX = "urn:epc-digital-delivery:finding:"


def _child(parent: ET.Element, tag: str, text: object) -> ET.Element:
    child = ET.SubElement(parent, tag)
    child.text = str(text)
    return child


def _vector(parent: ET.Element, tag: str, values: tuple[float, float, float]) -> None:
    vector = ET.SubElement(parent, tag)
    for axis, value in zip(("X", "Y", "Z"), values, strict=True):
        _child(vector, axis, format_float(value))


class BcfExporter:
    """Writes a BCF 3.0 archive from a run's issues."""

    id = "bcf"
    version = "1.0.0"
    output_root_key = "reports"

    def __init__(
        self,
        *,
        schema_dir: Path,
        subdirectory: str = "bcf",
        filename: str = BCF_FILENAME,
        project_name: str = "EPC Digital Delivery Control Tower",
        creation_author: str = "control-tower@example.invalid",
        topic_type: str = "Issue",
        role_domain: str = "example.invalid",
        project_id: str | None = None,
        frozen_ruleset: RuleSet | None = None,
    ) -> None:
        self._schema_dir = Path(schema_dir)
        self._subdirectory = subdirectory
        self._filename = filename
        self._project_name = project_name
        self._creation_author = creation_author
        self._topic_type = topic_type
        self._role_domain = role_domain
        # Projection scope, not rule-awareness. See the module docstring.
        self._project_id = project_id
        self._frozen_ruleset = frozen_ruleset

    def config_sha256(self) -> str:
        return ""

    # -- export ------------------------------------------------------------

    def export(self, bundle: RunBundle, output_root: Path) -> tuple[Artifact, ...]:
        data = self.build_archive(bundle)
        path = output_root / self._subdirectory / self._filename
        atomic_write_bytes(path, data)
        return (
            Artifact(
                path=path,
                sha256=sha256_bytes(data),
                byte_count=len(data),
                exporter_id=self.id,
            ),
        )

    # -- scope -------------------------------------------------------------

    def _published_issues(self, bundle: RunBundle) -> tuple[Issue, ...]:
        """The slice of the run this archive publishes.

        Two narrowings, both about *which results are published* rather than
        about what any rule means: one project, and one rule set version. Adding
        a rule to the current library must not rewrite an archive that says what
        an earlier rule set found.
        """

        keys: set[str] | None = None
        if self._frozen_ruleset is not None:
            keys = {
                requirement.requirement_key
                for requirement in self._frozen_ruleset.requirements
            }

        findings = {finding.finding_key: finding for finding in bundle.findings}
        published: list[Issue] = []
        for issue in bundle.issues:
            if self._project_id is not None and issue.project_id != self._project_id:
                continue
            if keys is not None:
                members = [findings[key] for key in issue.finding_keys if key in findings]
                if not members or any(
                    member.requirement_key not in keys for member in members
                ):
                    continue
            published.append(issue)
        return tuple(sorted(published, key=lambda issue: issue.issue_key))

    # -- archive -----------------------------------------------------------

    def build_archive(self, bundle: RunBundle) -> bytes:
        """Build the archive bytes without writing anything."""

        verify_schema_bundle(self._schema_dir)

        issues = self._published_issues(bundle)
        findings = {finding.finding_key: finding for finding in bundle.findings}
        requirements = {
            requirement.requirement_key: requirement
            for requirement in bundle.ruleset.requirements
        }
        elements = {element.element_key: element for element in bundle.elements}
        models = {model.model_key: model for model in bundle.models}

        entries = self.root_entries(issues)
        for issue in issues:
            members = [findings[key] for key in issue.finding_keys if key in findings]
            topic_guid = self._topic_guid(issue)
            entries[f"{topic_guid}/"] = b""
            entries[f"{topic_guid}/markup.bcf"] = self.markup(
                issue=issue,
                topic_guid=topic_guid,
                members=members,
                requirements=requirements,
                model=models[issue.model_key],
                as_of=bundle.run.as_of,
            )
            if issue.element_key:
                viewpoint_guid = self._viewpoint_guid(topic_guid)
                entries[f"{topic_guid}/viewpoint.bcfv"] = self.viewpoint(
                    viewpoint_guid=viewpoint_guid,
                    element=elements[issue.element_key],
                    bundle=bundle,
                )

        validate_xml_schemas(entries, self._schema_dir)
        return build_deterministic_zip(entries)

    # -- identity ----------------------------------------------------------

    @staticmethod
    def _topic_guid(issue: Issue) -> str:
        """A topic's GUID, derived from what the topic is about.

        From the subject rather than from ``issue_key`` on purpose: the same
        element with the same problem should be the same topic to whoever opens
        the archive, and ``issue_key`` folds in the validation run.
        """

        return uuid5_from_values("bcf-topic", [issue.element_key or issue.model_key])

    @staticmethod
    def _viewpoint_guid(topic_guid: str) -> str:
        return uuid5_from_values("bcf-viewpoint", [topic_guid])

    def _address(self, role: str) -> str:
        return f"{role}@{self._role_domain}" if role else ""

    # -- XML ---------------------------------------------------------------

    def root_entries(self, issues: Sequence[Issue]) -> dict[str, bytes]:
        """The archive-level files, with extensions built from what is present.

        The previous implementation listed one priority, one stage and two users
        because those were the constants it emitted. Here the vocabulary is
        whatever the issues actually use, which is the only version of this file
        that stays correct as rules are added.
        """

        version_root = ET.Element("Version", {"VersionId": BCF_VERSION})

        project_root = ET.Element("ProjectInfo")
        project = ET.SubElement(
            project_root,
            "Project",
            {"ProjectId": uuid5_from_values("bcf-project", [self._project_name])},
        )
        _child(project, "Name", self._project_name)

        priorities = sorted({issue.priority for issue in issues if issue.priority})
        stages = sorted({issue.stage for issue in issues if issue.stage})
        labels = sorted({label for issue in issues for label in issue.labels})
        # Assignees first, then whoever wrote the archive — the people who
        # receive work ahead of the tool that filed it.
        assignees = sorted(
            {self._address(issue.assignee_role) for issue in issues if issue.assignee_role}
        )
        users = [
            *assignees,
            *([self._creation_author] if self._creation_author not in assignees else []),
        ]
        statuses = sorted({str(issue.lifecycle_state) for issue in issues})

        extensions_root = ET.Element("Extensions")
        for group_name, item_name, values in (
            ("TopicTypes", "TopicType", [self._topic_type]),
            ("TopicStatuses", "TopicStatus", statuses),
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

    def markup(
        self,
        *,
        issue: Issue,
        topic_guid: str,
        members: Sequence[Finding],
        requirements: Mapping[str, Requirement],
        model,
        as_of: str,
    ) -> bytes:
        root = ET.Element("Markup")
        header = ET.SubElement(root, "Header")
        files = ET.SubElement(header, "Files")
        file_node = ET.SubElement(
            files,
            "File",
            {"IfcProject": model.ifc_project_guid, "IsExternal": "true"},
        )
        _child(file_node, "Filename", model.filename)
        _child(file_node, "Date", as_of)

        markup_topic = ET.SubElement(
            root,
            "Topic",
            {
                "Guid": topic_guid,
                "TopicType": self._topic_type,
                "TopicStatus": str(issue.lifecycle_state),
            },
        )
        links = ET.SubElement(markup_topic, "ReferenceLinks")
        for finding in sorted(members, key=lambda item: item.finding_key):
            _child(links, "ReferenceLink", FINDING_URN_PREFIX + finding.finding_key)

        _child(markup_topic, "Title", self._title(issue, members, requirements))
        if issue.priority:
            _child(markup_topic, "Priority", issue.priority)
        if issue.labels:
            labels = ET.SubElement(markup_topic, "Labels")
            for label in issue.labels:
                _child(labels, "Label", label)
        _child(markup_topic, "CreationDate", as_of)
        _child(markup_topic, "CreationAuthor", self._creation_author)
        # Order is the schema's, not ours: markup.xsd sequences DueDate before
        # AssignedTo before Stage, and a sequence is a sequence.
        if issue.due:
            _child(markup_topic, "DueDate", issue.due)
        if issue.assignee_role:
            _child(markup_topic, "AssignedTo", self._address(issue.assignee_role))
        if issue.stage:
            _child(markup_topic, "Stage", issue.stage)
        _child(
            markup_topic,
            "Description",
            self._description(issue, members, requirements),
        )

        if issue.element_key:
            viewpoints = ET.SubElement(markup_topic, "Viewpoints")
            viewpoint = ET.SubElement(
                viewpoints, "ViewPoint", {"Guid": self._viewpoint_guid(topic_guid)}
            )
            _child(viewpoint, "Viewpoint", "viewpoint.bcfv")
        return xml_bytes(root)

    @staticmethod
    def _title(
        issue: Issue,
        members: Sequence[Finding],
        requirements: Mapping[str, Requirement],
    ) -> str:
        return issue.element_key or issue.model_key

    @staticmethod
    def _description(
        issue: Issue,
        members: Sequence[Finding],
        requirements: Mapping[str, Requirement],
    ) -> str:
        """What the topic says, assembled from the rules behind it.

        Deliberately not a sentence written for one rule family. The subject,
        the requirements that were not met, and each rule's own citation — which
        is where a rule states why it is asking, including when what it asks is
        an assumption the project makes rather than an obligation the model
        broke.
        """

        subject = issue.element_key or issue.model_key
        labels = ", ".join(
            sorted(
                {
                    requirements[finding.requirement_key].requirement_label
                    for finding in members
                    if finding.requirement_key in requirements
                }
            )
        )
        citations = sorted(
            {
                requirements[finding.requirement_key].citation
                for finding in members
                if finding.requirement_key in requirements
                and requirements[finding.requirement_key].citation
            }
        )
        sentences = [f"Requirements not satisfied for {subject}: {labels}."]
        sentences.extend(citations)
        return " ".join(sentences)

    def viewpoint(
        self,
        *,
        viewpoint_guid: str,
        element: Element,
        bundle: RunBundle,
    ) -> bytes:
        geometry = bundle.geometry_for(element.element_key)
        camera = camera_for_aabb(
            Aabb(minimum=geometry.aabb_min, maximum=geometry.aabb_max)
        )

        root = ET.Element("VisualizationInfo", {"Guid": viewpoint_guid})
        components = ET.SubElement(root, "Components")
        selection = ET.SubElement(components, "Selection")
        component = ET.SubElement(
            selection, "Component", {"IfcGuid": element.global_id}
        )
        _child(component, "OriginatingSystem", self._project_name)
        _child(component, "AuthoringToolId", element.global_id)
        ET.SubElement(components, "Visibility", {"DefaultVisibility": "true"})

        perspective = ET.SubElement(root, "PerspectiveCamera")
        _vector(perspective, "CameraViewPoint", camera.position)
        _vector(perspective, "CameraDirection", camera.direction)
        _vector(perspective, "CameraUpVector", camera.up)
        _child(perspective, "FieldOfView", format_float(camera.field_of_view))
        _child(perspective, "AspectRatio", format_float(camera.aspect_ratio))
        return xml_bytes(root)
