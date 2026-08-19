"""Domain model — the single source of truth for what this system talks about.

Every tabular product downstream derives its columns from these types rather
than restating them as string lists. That is deliberate: the previous layout
declared ``FINDING_COLUMNS`` twice, as a 20-item list in one module and an
11-item set in another, and the two drifted apart unnoticed.

The types here enforce their own invariants in ``__post_init__``. A dataclass
that merely holds fields is not a source of truth — it is a container that
happens to be typed, and it will cheerfully hold a ``PASS`` finding flagged as
an issue, or an element whose key does not match its own model and GlobalId.
Invariants that span entities (referential integrity, an issue's state against
its own history) cannot be checked from inside a single object and live in
:mod:`~.validation` instead.

Entities are normalised. Denormalisation — folding element and requirement
attributes into a finding row, say — belongs to exporters, because different
outputs want different shapes.

This module deliberately imports nothing else from the package, so that it can
sit at the bottom of the dependency order.
"""

from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar

__all__ = [
    "ELEMENT_KEY_SEPARATOR",
    "ComponentFingerprint",
    "Element",
    "ElementGeometry",
    "Execution",
    "Finding",
    "FindingStatus",
    "Issue",
    "IssueEvent",
    "IssueEventPayload",
    "IssueState",
    "Model",
    "Project",
    "Provenance",
    "Requirement",
    "RuleSet",
    "RunBundle",
    "Severity",
    "StateChangedPayload",
    "TopicCreatedPayload",
    "ValidationRun",
    "derive_lifecycle_state",
    "derive_model_key",
    "field_names",
    "make_element_key",
]

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def field_names(row_type: type) -> tuple[str, ...]:
    """Return a dataclass's field names in declaration order.

    Row types declare their fields in the order the corresponding columns must
    appear, so column order is a property of the type instead of a separate
    list that can fall out of step with it.
    """

    return tuple(f.name for f in dataclasses.fields(row_type))


def _require_text(value: str, label: str) -> None:
    if not value:
        raise ValueError(f"{label} must not be empty")


def _require_slug(value: str, label: str) -> None:
    if not _SLUG.match(value):
        raise ValueError(f"{label} must be a slug, got {value!r}")


def _require_sha256(value: str, label: str, *, allow_empty: bool = False) -> None:
    if allow_empty and not value:
        return
    if not _SHA256.match(value):
        raise ValueError(f"{label} must be 64 lowercase hex characters, got {value!r}")


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class FindingStatus(StrEnum):
    """Normalised outcome of one requirement against one element.

    ``NOT_APPLICABLE`` exists because IfcTester reports a specification with
    zero applicable elements as passing. Counting that as compliance would
    inflate every pass rate, so it is normalised to its own status and excluded
    from the applicable denominator.
    """

    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "N/A"


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class IssueState(StrEnum):
    OPEN = "Open"
    IN_PROGRESS = "InProgress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


# ---------------------------------------------------------------------------
# Component identity
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ComponentFingerprint:
    """What a checker or exporter contributes to an identity.

    Configuration is folded in as a digest rather than as its literal contents:
    two runs of the same checker configured differently must produce different
    identities, but the configuration itself does not belong in a key.
    """

    component_id: str
    version: str
    config_sha256: str = ""

    def __post_init__(self) -> None:
        _require_text(self.component_id, "component_id")
        _require_text(self.version, "version")
        _require_sha256(self.config_sha256, "config_sha256", allow_empty=True)

    def as_document(self) -> dict[str, str]:
        return {
            "id": self.component_id,
            "version": self.version,
            "config_sha256": self.config_sha256,
        }


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Project:
    project_id: str
    name: str
    stage: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        _require_slug(self.project_id, "project_id")
        _require_text(self.name, "project name")


@dataclass(frozen=True, slots=True)
class Provenance:
    """Where a source model came from and how to prove it has not changed."""

    source_url: str
    license: str
    content_sha256: str

    def __post_init__(self) -> None:
        _require_sha256(self.content_sha256, "content_sha256")


ELEMENT_KEY_SEPARATOR = "::"


def derive_model_key(project_id: str, model_id: str) -> str:
    """Derive a globally unique model key from a project-scoped business code.

    Used when a manifest does not declare ``model_key`` explicitly. Falling
    back to the bare ``model_id`` would collide the moment a second project
    also had an ``architecture`` model — and since ``element_key`` is built
    from ``model_key``, that collision would silently merge two projects'
    elements rather than raise.
    """

    _require_slug(project_id, "project_id")
    _require_slug(model_id, "model_id")
    return f"{project_id}.{model_id}"


def make_element_key(model_key: str, global_id: str) -> str:
    """Build the federated element key.

    A bare IFC ``GlobalId`` is not unique across discipline files describing the
    same building, so it is never used on its own as a join key.
    """

    _require_text(model_key, "model_key")
    _require_text(global_id, "global_id")
    if ELEMENT_KEY_SEPARATOR in model_key:
        raise ValueError(
            f"model_key must not contain {ELEMENT_KEY_SEPARATOR!r}: {model_key!r}"
        )
    return f"{model_key}{ELEMENT_KEY_SEPARATOR}{global_id}"


@dataclass(frozen=True, slots=True)
class Model:
    """One source IFC file.

    ``model_key`` and ``model_id`` are deliberately separate. ``model_key`` is a
    globally stable identity that joins never change; ``model_id`` is a
    project-scoped business code that humans read and that two different
    projects may both use. Merging them would force every fork to namespace its
    business codes by hand.
    """

    model_key: str
    model_id: str
    project_id: str
    discipline: str
    filename: str
    provenance: Provenance
    ifc_schema: str
    ifc_project_guid: str

    def __post_init__(self) -> None:
        _require_text(self.model_key, "model_key")
        _require_text(self.model_id, "model_id")
        _require_slug(self.project_id, "project_id")
        _require_text(self.filename, "filename")
        if ELEMENT_KEY_SEPARATOR in self.model_key:
            raise ValueError(
                f"model_key must not contain {ELEMENT_KEY_SEPARATOR!r}: {self.model_key!r}"
            )


@dataclass(frozen=True, slots=True)
class Element:
    element_key: str
    model_key: str
    global_id: str
    ifc_class: str
    name: str
    storey: str
    pset_count: int

    def __post_init__(self) -> None:
        expected = make_element_key(self.model_key, self.global_id)
        if self.element_key != expected:
            raise ValueError(
                f"element_key {self.element_key!r} does not match its own "
                f"model_key and global_id (expected {expected!r})"
            )
        _require_text(self.ifc_class, "ifc_class")
        if self.pset_count < 0:
            raise ValueError(f"pset_count must not be negative: {self.pset_count}")


@dataclass(frozen=True, slots=True)
class ElementGeometry:
    """Where an element is, as a world-coordinate bounding box in metres.

    A separate entity rather than fields on :class:`Element` because it is
    expensive to obtain — it means tessellating the element — and because most
    of what this system does never needs it. Keeping it separate lets a run
    compute geometry only for the elements something is going to point a
    viewpoint at.

    It is in the domain at all because an exporter that needed to reopen an IFC
    file to place a camera would be reaching around the bundle boundary, and
    the boundary is what makes exports reproducible.
    """

    element_key: str
    aabb_min: tuple[float, float, float]
    aabb_max: tuple[float, float, float]

    def __post_init__(self) -> None:
        _require_text(self.element_key, "element_key")
        if len(self.aabb_min) != 3 or len(self.aabb_max) != 3:
            raise ValueError(f"{self.element_key}: an AABB needs three axes")
        for axis, (lower, upper) in enumerate(
            zip(self.aabb_min, self.aabb_max, strict=True)
        ):
            if upper < lower:
                raise ValueError(
                    f"{self.element_key}: AABB axis {axis} is inverted "
                    f"({lower} > {upper})"
                )


# ---------------------------------------------------------------------------
# Requirements
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Requirement:
    """One checkable information requirement.

    ``checker`` names the implementation that evaluates this requirement; the
    registry routes on it. Keeping the target on the requirement is what stops
    the pipeline from being IDS-shaped: IDS compilation is then an internal
    detail of the IDS checker rather than a stage everything must pass through.

    ``facet_kinds`` declares which kinds of facet the requirement uses, so the
    registry can reject a requirement routed to a checker that cannot evaluate
    it — at planning time, before a model is opened. The facets' actual content
    still lives in the checker's own source artifact (the IDS document) rather
    than here; lifting it into a typed, checker-independent payload belongs
    with declarative rule definitions, not with this refactor.

    ``severity``, ``owner_role`` and ``stage`` live here rather than in global
    configuration because they are properties of the rule. Deriving issue
    priority and assignment from them is what will let the BCF exporter stop
    knowing about any particular rule id.
    """

    requirement_key: str
    rule_id: str
    requirement_id: str
    specification_label: str
    requirement_label: str
    checker: str = "ids"
    facet_kinds: tuple[str, ...] = ()
    severity: Severity = Severity.ERROR
    owner_role: str = ""
    stage: str = ""
    discipline_scope: tuple[str, ...] = ()
    citation: str = ""
    #: How urgently a failure of this rule should be worked, which is not
    #: the same question as ``severity``. Severity says how wrong the model
    #: is; priority says when somebody will get to it. An ERROR nobody will
    #: reach until handover outranks nothing, and a WARNING blocking a
    #: coordination meeting on Friday outranks a great deal.
    priority: str = ""
    #: Free labels the issue inherits. A project files its own topics its
    #: own way, so this is the rule author's, not a vocabulary this package
    #: defines.
    labels: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.requirement_key, "requirement_key")
        _require_text(self.rule_id, "rule_id")
        _require_text(self.requirement_id, "requirement_id")
        _require_text(self.checker, "checker")
        if self.severity is Severity.INFO:
            raise ValueError(
                f"{self.rule_id}: severity is the severity of a FAILURE, so INFO "
                "is not meaningful; use WARNING or ERROR"
            )


@dataclass(frozen=True, slots=True)
class RuleSet:
    """A versioned collection of requirements.

    Two digests, for two different questions.

    ``source_blob_sha256`` answers *which exact file did we read?* It is
    provenance: it pins the artifact on disk so a swapped or edited source is
    detectable. It deliberately takes no part in the validation identity.

    ``normalized_digest`` answers *what do these rules say?* It is computed
    from the parsed requirements, so it is independent of the source format and
    of how that source happened to be written — reindenting a document, or
    switching its line endings, leaves it unchanged. This is what
    ``validation_run_id`` derives from.

    Conflating the two is a real trap, and this project fell into it once: the
    published v1.0.0 run identity hashes the IDS file's raw bytes, so the same
    rules checked out with different line endings produced a different run id
    and therefore different finding keys. Rule identity has to survive
    reformatting; file identity has to not.

    The digest is recomputed and checked in :func:`~.validation.validate_bundle`
    rather than here, because computing it needs the identity layer, which in
    turn is built on these types.
    """

    ruleset_id: str
    version: str
    normalized_digest: str
    source_blob_sha256: str = ""
    requirements: tuple[Requirement, ...] = ()
    #: When each delivery stage's information is due, as ``(stage, date)``
    #: pairs. A *programme date*, not an offset from when a run happened.
    #:
    #: That distinction is the whole reason `overdue` can be answered at
    #: all. An offset from the opening event would put every due date in the
    #: future of the only moment this system has, so nothing could ever be
    #: overdue. A programme says coordination information was due on a date,
    #: and the logical `as_of` is either past it or not.
    milestones: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _require_slug(self.ruleset_id, "ruleset_id")
        _require_slug(self.version, "ruleset version")
        _require_sha256(self.normalized_digest, "ruleset normalized_digest")
        _require_sha256(
            self.source_blob_sha256, "ruleset source_blob_sha256", allow_empty=True
        )
        keys = [requirement.requirement_key for requirement in self.requirements]
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        if duplicates:
            raise ValueError(f"Duplicate requirement_key values: {duplicates}")

    def milestone_for(self, stage: str) -> str:
        """When this stage's information is due, or empty if unstated."""

        for name, date in self.milestones:
            if name == stage:
                return date
        return ""

    def by_key(self, requirement_key: str) -> Requirement:
        for requirement in self.requirements:
            if requirement.requirement_key == requirement_key:
                return requirement
        raise KeyError(f"Unknown requirement_key: {requirement_key}")

    def checker_ids(self) -> tuple[str, ...]:
        return tuple(sorted({requirement.checker for requirement in self.requirements}))


# ---------------------------------------------------------------------------
# Run identity
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ValidationRun:
    """Deterministic identity of a validation, plus the inputs that produced it.

    The inputs are carried here, not just the resulting id, so that
    ``validation_run_id`` can be recomputed from a published bundle and checked
    against the value it claims. An identity you cannot independently verify is
    only a label.

    Depends solely on things that can change the findings: model content, rule
    content, participating checker versions and configuration, and a logical
    ``as_of``. Wall-clock time is not among them.
    """

    validation_run_id: str
    ruleset_id: str
    ruleset_version: str
    ruleset_normalized_digest: str
    as_of: str
    ruleset_source_blob_sha256: str = ""
    model_inputs: tuple[tuple[str, str], ...] = ()
    checker_fingerprints: tuple[ComponentFingerprint, ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.validation_run_id, "validation_run_id")
        _require_sha256(self.ruleset_normalized_digest, "ruleset_normalized_digest")
        # Recorded for audit, not for identity: which file was read is worth
        # knowing, but reformatting it must not re-key the validation.
        _require_sha256(
            self.ruleset_source_blob_sha256,
            "ruleset_source_blob_sha256",
            allow_empty=True,
        )
        for model_key, content_sha256 in self.model_inputs:
            _require_text(model_key, "model_inputs model_key")
            _require_sha256(content_sha256, f"model_inputs[{model_key}] content_sha256")

    @property
    def model_keys(self) -> tuple[str, ...]:
        return tuple(model_key for model_key, _ in self.model_inputs)


@dataclass(frozen=True, slots=True)
class Execution:
    """Identity of one concrete execution.

    Audit only. This type is deliberately *not* reachable from
    :class:`RunBundle`: an exporter that could see a wall-clock timestamp would
    sooner or later write one, and the determinism guarantee would quietly stop
    holding. Execution records are written by a separate audit path.
    """

    execution_id: str
    started_at: str
    platform: str
    tool_version: str
    nonce: str

    def __post_init__(self) -> None:
        _require_text(self.execution_id, "execution_id")
        _require_text(self.started_at, "started_at")
        _require_text(self.nonce, "nonce")


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Finding:
    """One requirement outcome — the pivot type of the whole system.

    Only four shapes are meaningful, and they are enforced rather than
    assumed:

    ===================  ==============  ==========  ===========  ===========
    status               is_applicable   is_issue    severity     element_key
    ===================  ==============  ==========  ===========  ===========
    ``PASS``             True            False       ``INFO``     set
    ``FAIL``             True            True        not ``INFO`` set
    ``FAIL``             True            True        not ``INFO`` empty
    ``N/A``              False           False       ``INFO``     empty
    ===================  ==============  ==========  ===========  ===========

    The ``N/A`` row is specification-level: no element was applicable, so there
    is no element to point at.

    The second ``FAIL`` row is a finding about something that is **not there**,
    and the rule governing it is this:

        A finding names the smallest thing that exists and that a person can go
        and look at.

    Usually that is an element, including when the finding is about an absence:
    "this space has no terminal" points at the space, which exists, is already
    in the element register, and is where a coordinator would go. But some
    absences have no such context — "this model carries no setout reference
    shared with its siblings", or an IDS specification whose applicability is
    required and matched nothing at all. There the smallest existing thing is
    the model, and ``element_key`` is empty.

    The alternative was to mint a key for the element that should have been
    there. It would have kept the table at three rows and every join
    unconditional, and it would have put a row in the element register for a
    thing that does not exist — the same fabrication this project refuses when
    it publishes ``actual`` empty rather than guessing at a value it cannot
    observe. A missing wall with a UUID is worse than an honest blank.

    ``PASS`` stays strict, and not by omission: a pass is a statement that some
    specific thing was checked and was correct, so there is always something to
    name. Only a failure can be about nothing.
    """

    finding_key: str
    validation_run_id: str
    project_id: str
    model_key: str
    element_key: str
    requirement_key: str
    status: FindingStatus
    severity: Severity
    is_applicable: bool
    is_issue: bool
    expected: str = ""
    actual: str = ""
    reason: str = ""

    def __post_init__(self) -> None:
        _require_text(self.finding_key, "finding_key")
        _require_text(self.validation_run_id, "validation_run_id")
        _require_text(self.model_key, "model_key")
        _require_text(self.requirement_key, "requirement_key")

        applicable = self.status is not FindingStatus.NOT_APPLICABLE
        if self.is_applicable != applicable:
            raise ValueError(
                f"{self.finding_key}: status {self.status} implies "
                f"is_applicable={applicable}, got {self.is_applicable}"
            )

        should_be_issue = self.status is FindingStatus.FAIL
        if self.is_issue != should_be_issue:
            raise ValueError(
                f"{self.finding_key}: only a FAIL is an issue; status "
                f"{self.status} with is_issue={self.is_issue}"
            )

        if should_be_issue and self.severity is Severity.INFO:
            raise ValueError(
                f"{self.finding_key}: a FAIL must carry a severity above INFO"
            )
        if not should_be_issue and self.severity is not Severity.INFO:
            raise ValueError(
                f"{self.finding_key}: status {self.status} must be INFO, "
                f"got {self.severity}"
            )

        if applicable and not self.element_key and not should_be_issue:
            raise ValueError(
                f"{self.finding_key}: a passing finding must name the element it "
                f"checked; only a failure can be about something that is absent"
            )
        if not applicable and self.element_key:
            raise ValueError(
                f"{self.finding_key}: an N/A finding is specification-level and "
                f"must not name an element, got {self.element_key!r}"
            )
        if self.element_key and not self.element_key.startswith(
            f"{self.model_key}{ELEMENT_KEY_SEPARATOR}"
        ):
            raise ValueError(
                f"{self.finding_key}: element_key {self.element_key!r} does not "
                f"belong to model {self.model_key!r}"
            )


# ---------------------------------------------------------------------------
# Issues and their event history
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TopicCreatedPayload:
    event_type: ClassVar[str] = "topic_created"
    finding_count: int
    title: str

    def __post_init__(self) -> None:
        if self.finding_count < 1:
            raise ValueError("A created topic must cover at least one finding")


@dataclass(frozen=True, slots=True)
class StateChangedPayload:
    event_type: ClassVar[str] = "state_changed"
    note: str = ""


#: Closed union of event payloads. Deliberately not an open ``dict``: an
#: unbounded metadata bag cannot be validated, cannot be versioned, and leaks
#: whatever the caller happened to have in scope into a published product.
IssueEventPayload = TopicCreatedPayload | StateChangedPayload


@dataclass(frozen=True, slots=True)
class IssueEvent:
    """One entry in an issue's history.

    The history is the record; :attr:`Issue.lifecycle_state` is a snapshot
    derived from it and checked against it.
    """

    event_key: str
    issue_key: str
    sequence: int
    occurred_at: str
    event_type: str
    from_state: IssueState | None
    to_state: IssueState | None
    actor_role: str
    payload_version: int
    typed_payload: IssueEventPayload
    actor_ref: str = ""

    def __post_init__(self) -> None:
        _require_text(self.event_key, "event_key")
        _require_text(self.issue_key, "issue_key")
        _require_text(self.occurred_at, "occurred_at")
        _require_text(self.actor_role, "actor_role")
        if self.sequence < 1:
            raise ValueError(f"{self.event_key}: sequence starts at 1, got {self.sequence}")
        if self.payload_version < 1:
            raise ValueError(f"{self.event_key}: payload_version starts at 1")
        if self.event_type != self.typed_payload.event_type:
            raise ValueError(
                f"{self.event_key}: event_type {self.event_type!r} disagrees with "
                f"its payload {self.typed_payload.event_type!r}"
            )
        if self.to_state is None:
            raise ValueError(f"{self.event_key}: an event must land in some state")
        if self.from_state == self.to_state:
            raise ValueError(
                f"{self.event_key}: an event must change state, both are "
                f"{self.to_state}"
            )


@dataclass(frozen=True, slots=True)
class Issue:
    """An actionable grouping of findings.

    ``assignee_role`` is a role, not a person. Roles come from rule metadata, so
    no party or directory table is needed to make an issue actionable.
    """

    issue_key: str
    validation_run_id: str
    project_id: str
    model_key: str
    element_key: str
    grouping_policy: str
    finding_keys: tuple[str, ...]
    lifecycle_state: IssueState
    assignee_role: str = ""
    priority: str = ""
    stage: str = ""
    due: str = ""
    labels: tuple[str, ...] = ()
    #: Derived from ``due`` and the run's logical ``as_of``, the same way
    #: ``lifecycle_state`` is derived from the event stream: recorded so a
    #: dashboard does not have to recompute it, and checked against its
    #: inputs so it cannot drift from them.
    is_overdue: bool = False

    def __post_init__(self) -> None:
        _require_text(self.issue_key, "issue_key")
        _require_text(self.grouping_policy, "grouping_policy")
        if not self.finding_keys:
            raise ValueError(f"{self.issue_key}: an issue must cover at least one finding")
        duplicates = sorted(
            {key for key in self.finding_keys if self.finding_keys.count(key) > 1}
        )
        if duplicates:
            raise ValueError(f"{self.issue_key}: duplicate finding_keys {duplicates}")


def derive_lifecycle_state(
    events: list[IssueEvent] | tuple[IssueEvent, ...],
) -> IssueState:
    """Fold one issue's event stream into its current state.

    Raises unless the stream is a well-formed history for a *single* issue:
    sequences start at 1 and increase by 1, and each event's ``from_state``
    matches the state its predecessors left behind.
    """

    if not events:
        raise ValueError("An issue must have at least one event")

    issue_keys = {event.issue_key for event in events}
    if len(issue_keys) != 1:
        raise ValueError(
            f"An event stream must belong to one issue, got {sorted(issue_keys)}"
        )

    ordered = sorted(events, key=lambda event: event.sequence)
    state: IssueState | None = None
    for position, event in enumerate(ordered, start=1):
        if event.sequence != position:
            raise ValueError(
                f"Issue {event.issue_key} has a gap or duplicate at sequence "
                f"{event.sequence}"
            )
        if event.from_state != state:
            raise ValueError(
                f"Issue {event.issue_key} event {event.sequence} starts from "
                f"{event.from_state!r} but the stream is at {state!r}"
            )
        state = event.to_state

    if state is None:  # pragma: no cover - IssueEvent forbids a null to_state
        raise ValueError(f"Issue {ordered[0].issue_key} ends in no state")
    return state


# ---------------------------------------------------------------------------
# The bundle exporters consume
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RunBundle:
    """Everything one run produced, in normalised form.

    This is the exporter boundary. An exporter receives a bundle and writes
    artifacts; it never reopens IFC files, consults checkers, or branches on
    rule ids.

    There is no :class:`Execution` here on purpose — see that type's docstring.
    Everything reachable from a bundle is a function of the inputs, so two runs
    over unchanged inputs export identical bytes.
    """

    contract_version: str
    run: ValidationRun
    ruleset: RuleSet
    projects: tuple[Project, ...] = ()
    models: tuple[Model, ...] = ()
    elements: tuple[Element, ...] = ()
    findings: tuple[Finding, ...] = ()
    issues: tuple[Issue, ...] = ()
    issue_events: tuple[IssueEvent, ...] = ()
    #: Bounding boxes, for the elements a run actually needed them for. Sparse
    #: by design: geometry costs a tessellation each, and most elements never
    #: get pointed at.
    geometry: tuple[ElementGeometry, ...] = ()

    def project_by_id(self, project_id: str) -> Project:
        for project in self.projects:
            if project.project_id == project_id:
                return project
        raise KeyError(f"Unknown project_id: {project_id}")

    def model_by_key(self, model_key: str) -> Model:
        for model in self.models:
            if model.model_key == model_key:
                return model
        raise KeyError(f"Unknown model_key: {model_key}")

    def element_by_key(self, element_key: str) -> Element:
        for element in self.elements:
            if element.element_key == element_key:
                return element
        raise KeyError(f"Unknown element_key: {element_key}")

    def events_for(self, issue_key: str) -> tuple[IssueEvent, ...]:
        return tuple(event for event in self.issue_events if event.issue_key == issue_key)

    def geometry_for(self, element_key: str) -> ElementGeometry:
        for geometry in self.geometry:
            if geometry.element_key == element_key:
                return geometry
        raise KeyError(f"No geometry was computed for element: {element_key}")
