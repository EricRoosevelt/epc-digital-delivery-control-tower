"""One assessment record: the carrier, the path, the leaf, and the seal.

ADR 0003 §3.3 asks for one structural separation and this module is built around
it. A subscope entry keeps three things apart:

* **the carrier** — ``members``, the ordered observation subjects the subscope
  *is*. A pair member records both its keys and the admitted ``element_key`` it
  refined from, so a reader can go from any verdict back to the declared element
  it concerns without re-deriving the partition.
* **the path** — every ``(node_id, evidence_requirement_id, grain, outcome)``
  from root to leaf, with the readings hung on each node and each reading's
  citations: ``finding_key`` values, the determination references behind it, or
  a named absence.
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

**Successors.** Because a sealed record is never rewritten, every later fact
about it arrives as a *new* record citing it, and :class:`SuccessorSection` is
what that citation looks like: the prior record's digest, the model versions
compared value for value, and — per cited subscope — where each of its members
went, which of its evidence citations still carry, and what could be established
about its ``recheck_condition``. The section is present only on a successor, so
an originating record's document, and therefore its digest, is byte-for-byte the
one it had before successors existed.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass

from ...determinism import canonical_json_document
from .request import AssessmentRequest

__all__ = [
    "CARRY_OVER_REASONS",
    "MEMBER_DISPOSITIONS",
    "RECHECK_CONDITION_STATES",
    "SUCCESSOR_KINDS",
    "ActivityResult",
    "AssessmentRecord",
    "ContextComparison",
    "EvidenceCarryOver",
    "MemberDisposition",
    "OutOfClassKey",
    "PathStep",
    "Reading",
    "RecheckOutcome",
    "ResolvedRoute",
    "ResolvingAssignment",
    "Subject",
    "SubscopeResult",
    "SuccessorSection",
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

    Exactly one of ``finding_keys`` and ``determination_references`` is
    populated, and ``absence`` names why neither is when the reading is an absent
    state. The three are kept apart rather than merged into one "evidence" field
    because "no finding exists", "a finding exists and says N/A", and "a
    determination was offered and declined" are three different situations a
    reader has to be able to tell apart.
    """

    subject: Subject
    outcome: str
    binding: str = ""
    finding_keys: tuple[str, ...] = ()
    #: Every admissible determination behind this reading, not one chosen from
    #: among them. Several references here mean several determinations reached
    #: the same conclusion; a set that disagreed would have refused the request
    #: rather than reaching a reading at all.
    determination_references: tuple[str, ...] = ()
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
        if self.determination_references:
            document["determination_references"] = list(self.determination_references)
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


# ---------------------------------------------------------------------------
# Successor records: what a recheck says about a sealed record it succeeds
# ---------------------------------------------------------------------------

#: The two successor kinds ADR 0003 §4.5 admits. Only ``recheck`` is built by
#: this checkpoint; ``authorisation`` is named so the vocabulary is closed and a
#: third kind cannot be invented by passing a new string.
SUCCESSOR_KINDS = ("recheck", "authorisation")

#: What became of one member of a cited prior subscope. A member that is gone is
#: **classified**, never folded into "resolved": the whole reason these four
#: names exist separately is that "the fix landed" and "the thing stopped being
#: derived" look identical from the verdict alone.
MEMBER_DISPOSITIONS = (
    #: The prior member is a subject of this record's partition — itself, or, for
    #: a bare element the current evidence refined, the pairs it refined into.
    "present",
    #: The ``element_key`` is absent from the producing model version's element
    #: inventory in this record's context. It was deleted, and a deletion is not
    #: a fix.
    "element-deleted-in-reissued-model",
    #: Present in the inventory, but its ``ifc_class`` no longer falls in this
    #: activity's ``subject_classes`` — an export-mapping change, say. The
    #: activity is no longer about it; nothing about it was resolved.
    "element-out-of-subject-class",
    #: The penetrating element is still admitted and the pair is not: the current
    #: ``pair_source`` determination does not name this counterpart. This is the
    #: cross-record twin of the within-record guard in
    #: :meth:`~.determinations.DeterminationLedger.counterparts`, and the reason
    #: it needs its own name is that the within-record guard cannot see it.
    "pairing-no-longer-derived",
    #: The declared assessed scope of *this* request never offered the key. The
    #: scope shrank; the deficiency did not.
    "outside-declared-scope",
)

#: Whether one citation the prior subscope's path made is still cited here, and
#: when it is not, which reason applies. Every one is a fact this record holds —
#: never an inference about a document the record cannot see.
CARRY_OVER_REASONS = (
    #: Cited by this record too.
    "carried",
    #: Not cited here, and the model-version context moved. No determination
    #: attributed to the prior context is admissible under this one — the same
    #: rule ``determination-model-version-mismatch`` enforces inside one request,
    #: read across the seal instead of inside it.
    "determination-not-attributable-to-this-context",
    #: Not cited here, and the context did not move: something superseded it.
    "determination-not-cited-by-this-record",
    #: A ``finding_key`` the prior path cited is absent from the facts this
    #: record was assessed against.
    "finding-absent-from-the-cited-run",
)

#: What this record was able to establish about the cited subscope's
#: ``recheck_condition``. Deliberately **not** a two-valued met/unmet: three of
#: this Pack's ten conditions name exactly one declared outcome and are
#: comparable, the other seven are prose written for people, and a member set
#: that shrank is not comparable at all.
RECHECK_CONDITION_STATES = (
    #: The one outcome the condition names, out of the leaf requirement's own
    #: declared vocabulary, is what every corresponding member now reads. The
    #: rest of the sentence is **not** checked, and this name says so rather than
    #: claiming the condition was met.
    "named-outcome-observed",
    #: The named outcome is not what the members read.
    "named-outcome-not-observed",
    #: The condition names no declared outcome, or several. The evaluator
    #: adjudicates nothing: a person reads it, and any judgement they make
    #: re-enters through a determination like every other judgement here.
    "no-machine-checkable-part",
    #: The correspondence is incomplete — a member is gone, or the leaf node is no
    #: longer reached — so there is no set to evaluate the condition over. Checked
    #: **before** the condition, because a universally quantified sentence goes
    #: literally true on a set its counterexample fell out of.
    "not-comparable",
    #: The cited subscope was ``READY`` and so carries no route and no condition.
    #: Recorded distinctly from "the condition has no machine-checkable part",
    #: because there being no sentence and there being a sentence nobody may
    #: adjudicate are different facts about the sealed record.
    "no-recheck-condition",
)


@dataclass(frozen=True, slots=True)
class ContextComparison:
    """The prior record's model versions beside this one's, value for value.

    A comparison, never a clock read (ADR 0003 §2.3). It is recorded whether or
    not anything moved, because "the context is unchanged" is a finding a reader
    needs as much as "the producing model was reissued".
    """

    prior_producing: tuple[str, str]
    producing: tuple[str, str]
    prior_consuming: tuple[str, str]
    consuming: tuple[str, str]

    @property
    def changed_models(self) -> tuple[str, ...]:
        """Which named models moved, in ``model_key`` order."""

        moved = []
        if self.prior_producing != self.producing:
            moved.append(self.producing[0])
        if self.prior_consuming != self.consuming:
            moved.append(self.consuming[0])
        return tuple(sorted(moved))

    @property
    def is_current(self) -> bool:
        return not self.changed_models

    def as_document(self) -> dict[str, object]:
        return {
            "prior_producing": {
                "model_key": self.prior_producing[0],
                "content_id": self.prior_producing[1],
            },
            "producing": {
                "model_key": self.producing[0],
                "content_id": self.producing[1],
            },
            "prior_consuming": {
                "model_key": self.prior_consuming[0],
                "content_id": self.prior_consuming[1],
            },
            "consuming": {
                "model_key": self.consuming[0],
                "content_id": self.consuming[1],
            },
            "is_current": self.is_current,
            "changed_models": list(self.changed_models),
        }


@dataclass(frozen=True, slots=True)
class MemberDisposition:
    """Where one member of the cited prior subscope is now, or why it is not.

    ``current_ordinals`` may hold more than one entry, and that is refinement
    rather than a partition defect: a bare element the prior record carried can
    become several pairs here, each with its own verdict.

    ``cause`` quotes what *this* record read — the current outcome of the
    ``pair_source`` requirement, the ``ifc_class`` that excluded the key — and is
    never an inference about a document this record cannot see.
    """

    member: Subject
    disposition: str
    cause: str = ""
    current_ordinals: tuple[int, ...] = ()
    current_verdicts: tuple[str, ...] = ()
    current_leaf_outcomes: tuple[str, ...] = ()

    def as_document(self) -> dict[str, object]:
        document: dict[str, object] = {
            "member": self.member.as_document(),
            "disposition": self.disposition,
        }
        if self.cause:
            document["cause"] = self.cause
        if self.current_ordinals:
            document["current_ordinals"] = list(self.current_ordinals)
            document["current_verdicts"] = list(self.current_verdicts)
            document["current_leaf_outcomes"] = list(self.current_leaf_outcomes)
        return document


@dataclass(frozen=True, slots=True)
class EvidenceCarryOver:
    """One citation the prior subscope's path made, and whether it carries here.

    Separated from the dispositions because they answer different questions. A
    disposition says what happened to a *subject*; this says what happened to the
    *evidence* — and a subscope can retreat with every member still present,
    purely because the determinations behind it stopped being attributable.
    """

    citation: str
    citation_kind: str
    reason: str

    @property
    def carried(self) -> bool:
        return self.reason == "carried"

    def as_document(self) -> dict[str, object]:
        return {
            "citation": self.citation,
            "citation_kind": self.citation_kind,
            "reason": self.reason,
            "carried": self.carried,
        }


@dataclass(frozen=True, slots=True)
class RecheckOutcome:
    """What one sealed subscope looks like under this record's evidence.

    Two statements, kept apart on purpose, because collapsing them is the whole
    failure this shape exists to prevent:

    * ``current_verdicts`` on the dispositions — **where the labour stands now.**
    * ``condition_status`` — **whether the cited ``recheck_condition`` was shown
      to be met.** It is not the same sentence, and this Pack carries a live case
      where the two diverge: a chimney re-determined as penetrating nothing
      reaches ``READY`` through ``no-penetration``, whose ``renders_inapplicable``
      ends the path — so the openings activity is ``READY`` while no opening was
      ever modelled and no cross-reference was ever added.

    ``prior_recheck_condition`` is copied from the sealed record verbatim, so a
    later reader is not renegotiating it.
    """

    activity_ref: str
    subscope_ordinal: int
    prior_verdict: str
    prior_resolution_kind: str
    prior_recheck_condition: str
    prior_leaf_evidence_requirement_id: str
    prior_members: tuple[Subject, ...]
    dispositions: tuple[MemberDisposition, ...]
    carry_over: tuple[EvidenceCarryOver, ...]
    correspondence: str
    named_outcome: str
    condition_status: str
    condition_basis: str

    def as_document(self) -> dict[str, object]:
        return {
            "activity_ref": self.activity_ref,
            "subscope_ordinal": self.subscope_ordinal,
            "prior_verdict": self.prior_verdict,
            "prior_resolution_kind": self.prior_resolution_kind,
            "prior_recheck_condition": self.prior_recheck_condition,
            "prior_leaf_evidence_requirement_id": (
                self.prior_leaf_evidence_requirement_id
            ),
            "prior_members": [member.as_document() for member in self.prior_members],
            "dispositions": [item.as_document() for item in self.dispositions],
            "evidence_carry_over": [item.as_document() for item in self.carry_over],
            "correspondence": self.correspondence,
            "named_outcome": self.named_outcome,
            "condition_status": self.condition_status,
            "condition_basis": self.condition_basis,
        }


@dataclass(frozen=True, slots=True)
class SuccessorSection:
    """This record's successor reference, and what it found about each subscope.

    One prior record per successor record: every cited subscope names the same
    ``prior_assessment_digest``. The prior record is not amended in any way — it
    is read for what it *recorded*, and its digest is re-computed from its own
    content before anything is read out of it, so a successor can never be built
    on a record whose seal is broken.
    """

    kind: str
    prior_assessment_digest: str
    context: ContextComparison
    outcomes: tuple[RecheckOutcome, ...]

    def as_document(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "prior_assessment_digest": self.prior_assessment_digest,
            "model_version_context_comparison": self.context.as_document(),
            "subscopes": [outcome.as_document() for outcome in self.outcomes],
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
    #: Present when this record succeeds a sealed one (ADR 0003 §4.5, §4.7), and
    #: absent on an originating record — where it is absent from the hashed
    #: document too, so adding the successor shape moved no originating record's
    #: digest by a byte.
    successor: SuccessorSection | None = None

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
            successor=self.successor,
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
    successor: SuccessorSection | None = None,
) -> dict[str, object]:
    """The canonical document for a resolved assessment, before it has a digest.

    Separated from :class:`AssessmentRecord` so the digest can be computed
    *before* the record is constructed, which lets a record be built exactly once
    with its digest already in it. The alternative — building the record, hashing
    it, then rebuilding it with the digest — makes "sealed when the digest is
    computed" a thing the code does twice and the reader has to trust.

    ``assessment_digest`` is absent by construction, so the digest is never an
    input to the value that names it.

    ``successor`` adds a key **only when there is one**. An originating record's
    document is therefore the same document it was before successors existed, and
    its digest the same value — which is what lets a successor cite a record
    sealed by an earlier build of this package.
    """

    context = request.model_version_context
    document: dict[str, object] = {
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
    if successor is not None:
        document["successor"] = successor.as_document()
    return document


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
