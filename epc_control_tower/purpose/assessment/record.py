"""One assessment record: the carrier, the path, the leaf, and the seal.

ADR 0003 §3.3 asks for one structural separation and this module is built around
it. A subscope entry keeps three things apart:

* **the carrier** — ``members``, the ordered observation subjects the subscope
  *is*. A pair member records both its keys and the admitted ``element_key`` it
  refined from, so a reader can go from any verdict back to the declared element
  it concerns without re-deriving the partition.
* **the path** — every ``(node_id, evidence_requirement_id, grain, outcome)``
  from root to leaf, with the readings hung on each node and each reading's
  citations: ``finding_key`` values, a determination reference, or a named
  absence.
* **the leaf** — the verdict, the ``resolution_kind`` when the verdict is not
  ``READY``, the route that kind resolves through, and the resolving assignment.

Two absences are as deliberate as anything present. There is **no roll-up**: a
requested scope whose evidence disagrees has no single verdict, only the ordered
partition, because reducing it would need a Framework object — "the verdict of a
scope whose own evidence disagrees" — that nothing here is entitled to mint.
And ``out_of_subject_class`` carries no verdict, no ``resolution_kind``, no
route, and no assignment: an out-of-class key is not an *(activity × scope ×
model-version)* cell, and minting a verdict for it would invent readiness for
something the activity is not about.

**Sealing.** ``assessment_digest`` hashes the whole resolved record, and
computing it is what seals the record. The dataclasses are frozen, so the seal is
enforced rather than promised; a record edited afterwards would no longer hash to
the digest anything else cites. The digest hashes **parsed, sorted structure** —
never file bytes, filenames, mtimes, or filesystem order — and it is never an
input to ``validation_run_id``, ``requirement_key``, ``finding_key``,
``issue_key``, ``group_ref``, ``ruleset_normalized_digest``, any legacy identity,
or any value under ``data/processed/``, ``reports/`` or ``ids/``. The dependency
points one way: this record cites frozen identities, and nothing frozen cites it.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass

from ...determinism import canonical_json_document
from .request import AssessmentRequest

__all__ = [
    "ActivityResult",
    "AssessmentRecord",
    "OutOfClassKey",
    "PathStep",
    "Reading",
    "ResolvedRoute",
    "ResolvingAssignment",
    "Subject",
    "SubscopeResult",
    "build_assessment_digest",
    "resolved_document",
]


@dataclass(frozen=True, slots=True)
class Subject:
    """One observation subject: an element, a pair, or the model pair.

    ``keys`` is the subject itself. ``refined_from`` is the admitted
    ``element_key`` a pair came from, empty when the subject was never refined —
    so a pair verdict is always traceable back to the declared element it is
    about, which is what keeps refinement from losing the scope.
    """

    keys: tuple[str, ...]
    refined_from: str = ""

    @property
    def sort_key(self) -> tuple[str, ...]:
        return self.keys

    def as_document(self) -> dict[str, object]:
        document: dict[str, object] = {"keys": list(self.keys)}
        if self.refined_from:
            document["refined_from"] = self.refined_from
        return document


@dataclass(frozen=True, slots=True)
class Reading:
    """One evidence requirement's outcome for one subject, with its citations.

    Exactly one of ``finding_keys`` and ``determination_reference`` is populated,
    and ``absence`` names why neither is when the reading is an absent state.
    The three are kept apart rather than merged into one "evidence" field
    because "no finding exists", "a finding exists and says N/A", and "a
    determination was offered and declined" are three different situations a
    reader has to be able to tell apart.
    """

    subject: Subject
    outcome: str
    binding: str = ""
    finding_keys: tuple[str, ...] = ()
    determination_reference: str = ""
    absence: str = ""

    def as_document(self) -> dict[str, object]:
        document: dict[str, object] = {
            "subject": self.subject.as_document(),
            "outcome": self.outcome,
        }
        if self.binding:
            document["binding"] = self.binding
        if self.finding_keys:
            document["finding_keys"] = list(self.finding_keys)
        if self.determination_reference:
            document["determination_reference"] = self.determination_reference
        if self.absence:
            document["absence"] = self.absence
        return document


@dataclass(frozen=True, slots=True)
class PathStep:
    """One node on the root-to-leaf path, and everything read at it."""

    node_id: str
    evidence_requirement_id: str
    grain: str
    outcome: str
    readings: tuple[Reading, ...]
    #: ``insufficient_evidence`` references consulted at this node, recorded as
    #: context and never as a reading. R-010's ``PASS`` lives here and cannot
    #: reach ``outcome`` — a separate field because it travelled a separate
    #: code path.
    context_citations: tuple[str, ...] = ()

    def as_document(self) -> dict[str, object]:
        document: dict[str, object] = {
            "node_id": self.node_id,
            "evidence_requirement_id": self.evidence_requirement_id,
            "grain": self.grain,
            "outcome": self.outcome,
            "readings": [reading.as_document() for reading in self.readings],
        }
        if self.context_citations:
            document["context_citations"] = list(self.context_citations)
        return document


@dataclass(frozen=True, slots=True)
class ResolvedRoute:
    """The Pack's route for one ``resolution_kind``, copied whole.

    ``consequence_kinds`` are kinds and only kinds. Magnitude is cited — the
    project's milestones travel on the record's provenance — and never computed
    (ADR 0003 §4.6).
    """

    resolution_kind: str
    consequence_kinds: tuple[str, ...]
    default_role: str
    next_action: str
    recheck_condition: str

    def as_document(self) -> dict[str, object]:
        return {
            "resolution_kind": self.resolution_kind,
            "consequence_kinds": list(self.consequence_kinds),
            "default_role": self.default_role,
            "next_action": self.next_action,
            "recheck_condition": self.recheck_condition,
        }


@dataclass(frozen=True, slots=True)
class ResolvingAssignment:
    """Who this assessment tasks with resolving one non-READY leaf.

    ``default_role`` is the Pack's default (Checkpoint B row 8a) and
    ``assigned_team_or_person`` is this assessment's assignment (row 8c),
    resolved through the Overlay's ``team_mapping``. Both are recorded; the bare
    role is never reported as though it were an assignee.

    ``actual_actor`` is row 8d and is absent here by construction: an execution
    fact that arrives after the record is sealed belongs to a successor record,
    which this checkpoint does not build.
    """

    default_role: str
    assigned_team_or_person: str
    decision_basis: str

    def as_document(self) -> dict[str, str]:
        return {
            "default_role": self.default_role,
            "assigned_team_or_person": self.assigned_team_or_person,
            "decision_basis": self.decision_basis,
        }


@dataclass(frozen=True, slots=True)
class SubscopeResult:
    """One outcome-homogeneous part of one activity's admitted scope."""

    ordinal: int
    members: tuple[Subject, ...]
    path: tuple[PathStep, ...]
    verdict: str
    resolution_kind: str = ""
    route: ResolvedRoute | None = None
    assignment: ResolvingAssignment | None = None

    @property
    def outcome_sequence(self) -> tuple[str, ...]:
        return tuple(step.outcome for step in self.path)

    @property
    def terminal_outcome(self) -> str:
        return self.path[-1].outcome if self.path else ""

    def as_document(self) -> dict[str, object]:
        document: dict[str, object] = {
            "ordinal": self.ordinal,
            "members": [member.as_document() for member in self.members],
            "path": [step.as_document() for step in self.path],
            "verdict": self.verdict,
        }
        if self.resolution_kind:
            document["resolution_kind"] = self.resolution_kind
        if self.route is not None:
            document["route"] = self.route.as_document()
        if self.assignment is not None:
            document["assignment"] = self.assignment.as_document()
        return document


@dataclass(frozen=True, slots=True)
class OutOfClassKey:
    """A declared scope key one activity's class admission excluded.

    Carries the ``ifc_class`` that excluded it and nothing else. A mistyped
    class name in a Pack surfaces here as elements the activity declined to be
    about — visibly — and never as a scope that quietly shrank.
    """

    element_key: str
    ifc_class: str

    def as_document(self) -> dict[str, str]:
        return {"element_key": self.element_key, "ifc_class": self.ifc_class}


@dataclass(frozen=True, slots=True)
class ActivityResult:
    """One requested activity's partition, plus the keys it was not about.

    ``partition_is_empty`` is stated rather than left to inference. An activity
    that admitted no subject reaches **no verdict at all**: there is no cell for
    one to attach to, nothing traversed a path to a ``READY`` leaf, and an
    absence of blockers among zero subjects is not the absence of blockers a
    release means.
    """

    activity_ref: str
    subject_classes: tuple[str, ...]
    admitted_subjects: tuple[str, ...]
    subscopes: tuple[SubscopeResult, ...]
    out_of_subject_class: tuple[OutOfClassKey, ...]

    @property
    def partition_is_empty(self) -> bool:
        return not self.admitted_subjects

    def as_document(self) -> dict[str, object]:
        return {
            "activity_ref": self.activity_ref,
            "subject_classes": list(self.subject_classes),
            "admitted_subjects": list(self.admitted_subjects),
            "partition_is_empty": self.partition_is_empty,
            "subscopes": [subscope.as_document() for subscope in self.subscopes],
            "out_of_subject_class": [
                key.as_document() for key in self.out_of_subject_class
            ],
        }


@dataclass(frozen=True, slots=True)
class AssessmentRecord:
    """One completed, sealed assessment.

    Lives outside ``data/processed/``, ``reports/``, ``ids/`` and the contract
    snapshot. It is never read back by ``group``, any exporter, ``epc-ct run``,
    ``epc-ct snapshot``, or either ``Legacy…`` writer, and it mutates nothing.
    """

    request: AssessmentRequest
    pack_schema_version: str
    composition_digest: str
    validation_run_id: str
    ruleset_id: str
    ruleset_version: str
    activities: tuple[ActivityResult, ...]
    #: The project's programme, cited verbatim so a consequence kind can point
    #: at a date. Nothing here is subtracted from anything.
    cited_milestones: Mapping[str, str]
    #: The Overlay's ``cost_parameters``, cited by name only. No magnitude is
    #: computed from them; ADR 0003 §4.6 admits kinds, never quantities.
    cited_cost_parameter_names: tuple[str, ...]
    assessment_digest: str

    def as_document(self) -> dict[str, object]:
        """The whole resolved record, in a total order, ready to hash or store.

        This is also the storage format as far as this checkpoint fixes one:
        where a record is put is a later decision, and the assessment writes no
        file itself.
        """

        return resolved_document(
            request=self.request,
            pack_schema_version=self.pack_schema_version,
            composition_digest=self.composition_digest,
            validation_run_id=self.validation_run_id,
            ruleset_id=self.ruleset_id,
            ruleset_version=self.ruleset_version,
            activities=self.activities,
            cited_milestones=self.cited_milestones,
            cited_cost_parameter_names=self.cited_cost_parameter_names,
        )


def resolved_document(
    *,
    request: AssessmentRequest,
    pack_schema_version: str,
    composition_digest: str,
    validation_run_id: str,
    ruleset_id: str,
    ruleset_version: str,
    activities: tuple[ActivityResult, ...],
    cited_milestones: Mapping[str, str],
    cited_cost_parameter_names: tuple[str, ...],
) -> dict[str, object]:
    """The canonical document for a resolved assessment, before it has a digest.

    Separated from :class:`AssessmentRecord` so the digest can be computed
    *before* the record is constructed, which lets a record be built exactly once
    with its digest already in it. The alternative — building the record, hashing
    it, then rebuilding it with the digest — makes "sealed when the digest is
    computed" a thing the code does twice and the reader has to trust.

    ``assessment_digest`` is absent by construction, so the digest is never an
    input to the value that names it.
    """

    context = request.model_version_context
    return {
        "request": {
            "project_id": request.project_id,
            "pack_id": request.pack_id,
            "pack_version": request.pack_version,
            "pack_schema_version": pack_schema_version,
            "direction_id": request.direction_id,
            "activity_ids": sorted(request.activity_ids),
            "assessed_scope": request.assessed_scope.as_document(),
            "model_version_context": {
                "producing": {
                    "model_key": context.producing.model_key,
                    "content_id": context.producing.content_id,
                },
                "consuming": {
                    "model_key": context.consuming.model_key,
                    "content_id": context.consuming.content_id,
                },
                "handover": {
                    "from_role": context.handover.from_role,
                    "to_role": context.handover.to_role,
                    "milestone": context.handover.milestone,
                    "date": context.handover.date,
                },
            },
        },
        "provenance": {
            "validation_run_id": validation_run_id,
            "ruleset_id": ruleset_id,
            "ruleset_version": ruleset_version,
            "composition_digest": composition_digest,
            "cited_milestones": dict(sorted(cited_milestones.items())),
            "cited_cost_parameter_names": sorted(cited_cost_parameter_names),
        },
        "activities": [activity.as_document() for activity in activities],
    }


def build_assessment_digest(document: Mapping[str, object]) -> str:
    """Hash one fully resolved record's parsed, totally ordered content.

    Parsed structure only. It never hashes TOML or CSV bytes, file names,
    mtimes, or filesystem ordering, and it reads no clock — the same discipline
    ``build_ruleset_normalized_digest`` already applies, so that reformatting a
    Pack cannot change what an assessment of it *is*.
    """

    return hashlib.sha256(
        canonical_json_document(dict(document)).encode("utf-8")
    ).hexdigest()
