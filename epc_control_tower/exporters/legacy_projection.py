"""Projecting the canonical model back onto the published shape.

This is the anti-fork guarantee made concrete. Everything the Power BI project
and the committed BCF archive read is computed *here*, from the canonical
bundle and from nothing else, so the published contract cannot quietly drift
away from the model that now drives it. If the projection stops reproducing the
committed bytes, the characterization test says so, and that test is the only
licence this whole legacy path has to exist.

Two identities are deliberately taken from the frozen pre-split derivations
rather than from the current ones. ``run_id`` is the old single identity, and
``finding_key`` keys on it and on ``model_id``. Neither *derivation* changed
when identity was split three ways — ``build_finding_key`` and
``legacy_finding_key`` compute the same function — but the run identity they
consume did, because it now folds in each checker's version and configuration.
So the published keys survive by feeding the old run identity back in, not by
keeping a second key algorithm around.

Columns the canonical model has and the published shape does not — ``project_id``
above all — are dropped here. That is what lets the canonical model grow a
dimension without the dashboard noticing.

Both legacy writers share this module so there is exactly one projection. A
second copy is how the BCF sidecars and the BCF archive would come to disagree.
"""

from __future__ import annotations

from collections.abc import Sequence
import dataclasses
from dataclasses import dataclass

from ..bcf.geometry import Aabb, Camera, camera_for_aabb
from ..determinism import format_float
from ..domain import (
    Element,
    Finding,
    Model,
    Requirement,
    RuleSet,
    RunBundle,
    Severity,
)
from ..legacy_identity import (
    legacy_finding_key,
    legacy_run_id,
    legacy_topic_event_id,
    legacy_topic_guid,
    legacy_viewpoint_guid,
)
from .legacy_contract import (
    ASSIGNEE,
    CREATION_AUTHOR,
    EVENT_SOURCE,
    EVENT_TYPE_CREATED,
    ORIGINATING_SYSTEM,
    TOPIC_PRIORITY,
    TOPIC_STAGE,
    TOPIC_STATUS,
    TOPIC_TYPE,
    LegacyComponentRow,
    LegacyEventRow,
    LegacyFindingRow,
    LegacyInventoryRow,
    LegacyModelRow,
    LegacyTopicFindingRow,
    LegacyTopicRow,
    LegacyViewpointRow,
)

__all__ = [
    "LegacyProjection",
    "LegacyTopic",
    "issue_element_keys",
    "narrow_to_project",
    "narrow_to_ruleset",
    "project_bundle",
    "project_register",
    "viewpoint_row",
]

#: A published title is truncated rather than rejected: BCF constrains the
#: field, and losing the tail of a name is better than losing the topic.
TITLE_LIMIT = 128


def _boolean(value: bool) -> str:
    return "true" if value else "false"


@dataclass(frozen=True, slots=True)
class LegacyTopic:
    """One published BCF topic, with everything both writers need.

    The archive needs the markup and the camera; the sidecars need the same
    values as rows. They are computed once, here, so the two cannot disagree.
    """

    element_key: str
    topic_guid: str
    viewpoint_guid: str
    model: Model
    element: Element
    findings: tuple[LegacyFindingRow, ...]
    aabb: Aabb
    camera: Camera

    @property
    def title(self) -> str:
        return f"IDS metadata action: {self.element.name or self.element.ifc_class}"[
            :TITLE_LIMIT
        ]

    @property
    def viewpoint_filename(self) -> str:
        return f"{self.viewpoint_guid}.bcfv"


@dataclass(frozen=True, slots=True)
class LegacyProjection:
    run_id: str
    ids_version: str
    as_of: str
    models: tuple[LegacyModelRow, ...]
    inventory: tuple[LegacyInventoryRow, ...]
    findings: tuple[LegacyFindingRow, ...]
    topics: tuple[LegacyTopic, ...]
    topic_rows: tuple[LegacyTopicRow, ...]
    topic_finding_rows: tuple[LegacyTopicFindingRow, ...]
    viewpoint_rows: tuple[LegacyViewpointRow, ...]
    component_rows: tuple[LegacyComponentRow, ...]
    event_rows: tuple[LegacyEventRow, ...]


def _finding_row(
    *,
    finding: Finding,
    requirement: Requirement,
    model: Model,
    element: Element | None,
    run_id: str,
    ids_version: str,
) -> LegacyFindingRow:
    return LegacyFindingRow(
        finding_key=legacy_finding_key(
            run_id=run_id,
            model_id=model.model_id,
            requirement_key=finding.requirement_key,
            element_key=finding.element_key,
        ),
        run_id=run_id,
        model_id=model.model_id,
        element_key=finding.element_key,
        global_id=element.global_id if element is not None else "",
        ids_version=ids_version,
        specification_id=requirement.rule_id,
        specification=requirement.specification_label,
        requirement_id=requirement.requirement_id,
        requirement_key=finding.requirement_key,
        requirement=requirement.requirement_label,
        status=str(finding.status),
        is_applicable=_boolean(finding.is_applicable),
        is_issue=_boolean(finding.is_issue),
        # From the frozen rule, not from the finding. The finding carries the
        # severity the *current* rule set assigns; the published file has to
        # keep saying what rule set 0.1 said, even if a later version
        # reclassifies the same rule.
        severity=str(requirement.severity if finding.is_issue else Severity.INFO),
        ifc_class=element.ifc_class if element is not None else "",
        element_name=element.name if element is not None else "",
        expected=finding.expected,
        actual=finding.actual,
        reason=finding.reason,
    )


def viewpoint_row(topic: LegacyTopic, run_id: str) -> LegacyViewpointRow:
    axes = {}
    for prefix, values in (
        ("aabb_min", topic.aabb.minimum),
        ("aabb_max", topic.aabb.maximum),
        ("target", topic.camera.target),
        ("camera_view_point", topic.camera.position),
        ("camera_direction", topic.camera.direction),
        ("camera_up", topic.camera.up),
    ):
        for axis, value in zip(("x", "y", "z"), values, strict=True):
            axes[f"{prefix}_{axis}"] = format_float(value)

    return LegacyViewpointRow(
        run_id=run_id,
        viewpoint_guid=topic.viewpoint_guid,
        topic_guid=topic.topic_guid,
        viewpoint_filename=topic.viewpoint_filename,
        model_id=topic.model.model_id,
        element_key=topic.element_key,
        global_id=topic.element.global_id,
        field_of_view=format_float(topic.camera.field_of_view),
        aspect_ratio=format_float(topic.camera.aspect_ratio),
        **axes,
    )


def project_register(
    models: Sequence[Model],
    elements: Sequence[Element],
) -> tuple[tuple[LegacyModelRow, ...], tuple[LegacyInventoryRow, ...]]:
    """Project the model and element registers onto their published shape.

    Split out from :func:`project_bundle` because these two tables need only
    ingest and inventory — no rules, no findings — and the legacy extraction
    script rebuilds exactly them.
    """

    models_by_key = {model.model_key: model for model in models}

    model_rows = tuple(
        sorted(
            (
                LegacyModelRow(
                    model_id=model.model_id,
                    filename=model.filename,
                    discipline=model.discipline,
                    ifc_project_guid=model.ifc_project_guid,
                    ifc_schema=model.ifc_schema,
                    content_sha256=model.provenance.content_sha256,
                    source_url=model.provenance.source_url,
                    license=model.provenance.license,
                )
                for model in models
            ),
            key=lambda row: row.model_id,
        )
    )

    inventory_rows = tuple(
        sorted(
            (
                LegacyInventoryRow(
                    model_id=models_by_key[element.model_key].model_id,
                    source_model=models_by_key[element.model_key].filename,
                    discipline=models_by_key[element.model_key].discipline,
                    element_key=element.element_key,
                    global_id=element.global_id,
                    ifc_class=element.ifc_class,
                    name=element.name,
                    storey=element.storey,
                    pset_count=element.pset_count,
                )
                for element in elements
            ),
            key=lambda row: (row.model_id, row.element_key),
        )
    )

    return model_rows, inventory_rows


def narrow_to_project(bundle: RunBundle, project_id: str) -> RunBundle:
    """Restrict a run to the one project the published contract describes.

    **This is the scope decision, and it is deliberate rather than incidental.**

    The eight published CSV files describe exactly one project. That is not a
    coincidence to be generalised away: the Power BI project's nine TMDL tables
    assert three models and thirty-nine elements, the committed acceptance
    evidence was captured against those numbers, and neither is in scope to
    change before Phase 5.

    So when a run covers more than one project, the legacy writers publish one
    of them and say which. The alternative — emitting everything — is not a
    wider contract, it is a broken one: it was measured, and it changed all
    eight CSV files, the BCF archive, and the published ``run_id``, while every
    exporter still reported success. A contract that widens silently is worse
    than one that refuses.

    The narrowed bundle keeps its :class:`~..domain.ValidationRun` intact. The
    validation genuinely covered every model, and rewriting the run to pretend
    otherwise would mean publishing an identity that never happened. Only the
    *projection* is narrowed; what was validated is still what was validated.
    """

    if not any(project.project_id == project_id for project in bundle.projects):
        raise KeyError(
            f"Legacy projection is scoped to project {project_id!r}, which this "
            f"run does not contain; it has "
            f"{sorted(p.project_id for p in bundle.projects)}"
        )

    model_keys = {
        model.model_key for model in bundle.models if model.project_id == project_id
    }
    element_keys = {
        element.element_key
        for element in bundle.elements
        if element.model_key in model_keys
    }
    findings = tuple(
        finding for finding in bundle.findings if finding.project_id == project_id
    )
    finding_keys = {finding.finding_key for finding in findings}
    issues = tuple(
        issue for issue in bundle.issues if issue.project_id == project_id
    )
    issue_keys = {issue.issue_key for issue in issues}

    return dataclasses.replace(
        bundle,
        projects=tuple(
            project for project in bundle.projects if project.project_id == project_id
        ),
        models=tuple(
            model for model in bundle.models if model.model_key in model_keys
        ),
        elements=tuple(
            element for element in bundle.elements if element.element_key in element_keys
        ),
        findings=findings,
        issues=tuple(
            dataclasses.replace(
                issue,
                finding_keys=tuple(
                    key for key in issue.finding_keys if key in finding_keys
                ),
            )
            for issue in issues
        ),
        issue_events=tuple(
            event for event in bundle.issue_events if event.issue_key in issue_keys
        ),
        geometry=tuple(
            geometry
            for geometry in bundle.geometry
            if geometry.element_key in element_keys
        ),
    )


def narrow_to_ruleset(bundle: RunBundle, frozen: RuleSet) -> RunBundle:
    """Restrict a run to the rules the published contract was built from.

    **The second half of the scope decision, and it was measured before it was
    made.** Adding a single rule to the document, changing nothing else,
    destroys all forty-seven published ``finding_key`` values — not some of
    them, all of them — and rewrites seven of the nine published artifacts. The
    published ``run_id`` is a digest of the rule document's bytes, so any rule
    anywhere re-keys every finding everywhere.

    What makes that fatal rather than merely inconvenient is what it takes down
    with it: ``docs/evidence/stage_3b/acceptance_manifest.json`` pins those
    digests, and regenerating it means re-capturing screenshots by hand in
    Power BI Desktop. Growing the rule library would therefore have been
    blocked on a task explicitly deferred to Phase 5.

    So the published files mean *what rule set 0.1 said about one project*.
    Both halves are scope. New rules go into a new version of the document and
    reach the canonical outputs only; the frozen document keeps publishing what
    it always published.

    This filters rather than re-evaluates. The requirements it keeps were
    evaluated by the same run as everything else, against the same models —
    ``requirement_key`` depends only on the rule and requirement identifiers,
    so a rule set that still contains rule 0.1's rules still produces rule
    0.1's findings. A rule whose *meaning* changed would produce a different
    finding for the same key, and the byte-equality test would say so loudly,
    which is the behaviour worth having.
    """

    frozen_keys = {requirement.requirement_key for requirement in frozen.requirements}
    missing = sorted(
        requirement.rule_id
        for requirement in frozen.requirements
        if requirement.requirement_key
        not in {r.requirement_key for r in bundle.ruleset.requirements}
    )
    if missing:
        raise ValueError(
            "The published contract is built from rule set "
            f"{frozen.ruleset_id} {frozen.version}, but this run's rule set no "
            f"longer contains {sorted(set(missing))}. A published rule cannot be "
            "removed or renamed while the legacy adapters exist."
        )

    findings = tuple(
        finding
        for finding in bundle.findings
        if finding.requirement_key in frozen_keys
    )
    finding_keys = {finding.finding_key for finding in findings}
    issues = tuple(
        dataclasses.replace(
            issue,
            finding_keys=tuple(
                key for key in issue.finding_keys if key in finding_keys
            ),
        )
        for issue in bundle.issues
        if any(key in finding_keys for key in issue.finding_keys)
    )
    issue_keys = {issue.issue_key for issue in issues}

    return dataclasses.replace(
        bundle,
        ruleset=frozen,
        findings=findings,
        issues=issues,
        issue_events=tuple(
            event for event in bundle.issue_events if event.issue_key in issue_keys
        ),
    )


def project_bundle(
    bundle: RunBundle,
    *,
    project_id: str | None = None,
    frozen_ruleset: RuleSet | None = None,
) -> LegacyProjection:
    """Project a canonical bundle onto the published contract.

    ``project_id`` names the single project the published files describe, and
    ``frozen_ruleset`` the single rule set version they were built from. Both
    may be omitted only when the run offers no choice; with a choice available,
    guessing would silently republish a different contract.
    """

    if project_id is not None:
        bundle = narrow_to_project(bundle, project_id)
    elif len(bundle.projects) > 1:
        raise ValueError(
            "The published contract describes one project, but this run covers "
            f"{sorted(p.project_id for p in bundle.projects)}. Set "
            "`legacy_project_id` in control-tower.toml to say which one the "
            "legacy writers should publish."
        )

    if frozen_ruleset is not None:
        bundle = narrow_to_ruleset(bundle, frozen_ruleset)

    ids_version = bundle.ruleset.version
    run_id = legacy_run_id(
        ids_version=ids_version,
        # The frozen document's own bytes. Deriving this from the run's current
        # rule set is what made every published key hostage to every new rule.
        ids_sha256=bundle.ruleset.source_blob_sha256,
        models=[
            (model.model_id, model.provenance.content_sha256) for model in bundle.models
        ],
    )

    models_by_key = {model.model_key: model for model in bundle.models}
    elements_by_key = {element.element_key: element for element in bundle.elements}

    model_rows, inventory_rows = project_register(bundle.models, bundle.elements)

    finding_rows = [
        _finding_row(
            finding=finding,
            requirement=bundle.ruleset.by_key(finding.requirement_key),
            model=models_by_key[finding.model_key],
            element=elements_by_key.get(finding.element_key)
            if finding.element_key
            else None,
            run_id=run_id,
            ids_version=ids_version,
        )
        for finding in bundle.findings
    ]
    # The published order, reproduced exactly. No two rows can tie on all five
    # columns without being a duplicate finding, which is rejected upstream, so
    # this ordering is total.
    finding_rows.sort(
        key=lambda row: (
            row.model_id,
            row.specification_id,
            row.requirement_id,
            row.element_key,
            row.status,
        )
    )

    rows_by_finding_key = {
        (row.model_id, row.requirement_key, row.element_key): row
        for row in finding_rows
    }

    topics = _project_topics(
        bundle=bundle,
        models_by_key=models_by_key,
        elements_by_key=elements_by_key,
        rows_by_finding_key=rows_by_finding_key,
    )

    topic_rows = tuple(
        LegacyTopicRow(
            run_id=run_id,
            topic_guid=topic.topic_guid,
            topic_type=TOPIC_TYPE,
            topic_status=TOPIC_STATUS,
            title=topic.title,
            priority=TOPIC_PRIORITY,
            creation_date=bundle.run.as_of,
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
        for topic in topics
    )

    topic_finding_rows = tuple(
        LegacyTopicFindingRow(
            run_id=run_id,
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
        for topic in topics
        for row in topic.findings
    )

    viewpoint_rows = tuple(viewpoint_row(topic, run_id) for topic in topics)

    component_rows = tuple(
        LegacyComponentRow(
            run_id=run_id,
            viewpoint_guid=topic.viewpoint_guid,
            topic_guid=topic.topic_guid,
            component_index=1,
            model_id=topic.model.model_id,
            element_key=topic.element_key,
            global_id=topic.element.global_id,
            originating_system=ORIGINATING_SYSTEM,
            authoring_tool_id=topic.element.global_id,
        )
        for topic in topics
    )

    event_rows = tuple(
        LegacyEventRow(
            run_id=run_id,
            event_id=legacy_topic_event_id(topic.topic_guid),
            topic_guid=topic.topic_guid,
            event_type=EVENT_TYPE_CREATED,
            event_date=bundle.run.as_of,
            event_author=CREATION_AUTHOR,
            value="",
            source=EVENT_SOURCE,
        )
        for topic in topics
    )

    return LegacyProjection(
        run_id=run_id,
        ids_version=ids_version,
        as_of=bundle.run.as_of,
        models=model_rows,
        inventory=inventory_rows,
        findings=tuple(finding_rows),
        topics=topics,
        topic_rows=topic_rows,
        topic_finding_rows=topic_finding_rows,
        viewpoint_rows=viewpoint_rows,
        component_rows=component_rows,
        event_rows=event_rows,
    )


def _project_topics(
    *,
    bundle: RunBundle,
    models_by_key: dict[str, Model],
    elements_by_key: dict[str, Element],
    rows_by_finding_key: dict[tuple[str, str, str], LegacyFindingRow],
) -> tuple[LegacyTopic, ...]:
    topics: list[LegacyTopic] = []

    for issue in sorted(bundle.issues, key=lambda item: item.element_key):
        element = elements_by_key[issue.element_key]
        model = models_by_key[issue.model_key]

        rows = [
            rows_by_finding_key[(model.model_id, finding.requirement_key, finding.element_key)]
            for finding in bundle.findings
            if finding.finding_key in set(issue.finding_keys)
        ]
        # Ordered by the published key, which is what the archive's reference
        # links and the description's requirement list are ordered by.
        rows.sort(key=lambda row: row.finding_key)

        geometry = bundle.geometry_for(issue.element_key)
        aabb = Aabb(minimum=geometry.aabb_min, maximum=geometry.aabb_max)
        topic_guid = legacy_topic_guid(issue.element_key)

        topics.append(
            LegacyTopic(
                element_key=issue.element_key,
                topic_guid=topic_guid,
                viewpoint_guid=legacy_viewpoint_guid(topic_guid),
                model=model,
                element=element,
                findings=tuple(rows),
                aabb=aabb,
                camera=camera_for_aabb(aabb),
            )
        )

    return tuple(topics)


def issue_element_keys(bundle: RunBundle) -> tuple[str, ...]:
    """Element keys the legacy writers will need geometry for."""

    return tuple(sorted({issue.element_key for issue in bundle.issues}))
