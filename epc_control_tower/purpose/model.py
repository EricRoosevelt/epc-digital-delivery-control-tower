"""The shapes a Purpose Pack, a Project Overlay, and their composition take.

Read this module as the answer to one question: *what can this object say?*
Because the answer bounds what any consumer can do with it, and two things it
must not be able to say are load-bearing.

**It cannot express readiness.** There is no verdict here, no evidence outcome,
no reading, no subscope, no resolving assignment, no risk acceptance — not as a
field, not as a cached property, not as a method. A Pack states the question a
purpose asks; an Overlay states what one project supplies to it; the answer is
a runtime fact about one assessment of two specific model versions, and it
lives in the assessment record :mod:`~.assessment` builds and seals. Giving the
composed object somewhere to put an answer is how a per-run result quietly
becomes a project setting.

**It cannot collapse the assignment chain.** Checkpoint B separated three
things: a Pack's default responsibility policy (8a), a project's role-to-team
mapping (8b), and *the resolving role or team this assessment assigned* (8c).
Composition checks that 8a resolves through 8b — that the mapping exists — and
stops there. It does not produce 8c. An assignment is a decision an assessment
makes against particular model versions, and a composed configuration object
that carried one would be asserting a decision nobody has made.

A third distinction is structural rather than a prohibition.
:class:`PackBinding` and :class:`InsufficientEvidence` are separate types even
though both are "a reference to validation data, with its ruleset pinned", and
both get the identical existence-and-version check at composition. That is
exactly why they would collapse into one list of requirement keys if anything
were left to convenience — and then nothing downstream could tell *this rule
answers the question* from *this rule explicitly cannot answer it*. R-010's
PASS is never alignment evidence, and the sentence saying so travels with the
reference that says it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

__all__ = [
    "BINDING_SOURCES",
    "DECISION_BASES",
    "SUBJECT_GRAINS",
    "VERDICTS",
    "AcceptedEvidenceMethod",
    "Activity",
    "Branch",
    "ComposedPurposeInputs",
    "Convention",
    "DecisionNode",
    "Direction",
    "EvidenceBinding",
    "EvidenceRequirement",
    "InsufficientEvidence",
    "OverlayPackRef",
    "PackBinding",
    "PairSource",
    "ProjectOverlay",
    "PurposePack",
    "ResolutionRoute",
    "RiskAuthorisation",
    "TeamMapping",
]

#: Where an evidence requirement's binding comes from. Closed, no default.
BINDING_SOURCES = ("pack", "overlay", "assessment")

#: How an evidence requirement's readings key onto observation subjects.
SUBJECT_GRAINS = ("whole-scope", "per-subject", "per-subject-pair")

#: The verdicts a decision-tree *leaf* may carry. ``CONDITIONAL`` is absent by
#: construction: it must originate in a named authorisation event, which no
#: evidence outcome can encode, so no tree may reach it.
VERDICTS = ("READY", "BLOCKED", "UNKNOWN")

#: Whether an Overlay policy row records a decision the project actually took,
#: or a value written to demonstrate the shape. Required on every row of the
#: three policy tables; there is no default, because a policy row whose
#: standing is unstated is exactly the row a reader takes for a decision.
DECISION_BASES = ("project-decision", "illustrative")


# --------------------------------------------------------------------------
# Purpose Pack
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Direction:
    """One directional handoff this Pack's flagship purpose can carry.

    Never derived from a rule's ``discipline_scope``, which says which models a
    rule is evaluated against and carries no arrow.
    """

    direction_id: str
    from_discipline: str
    to_discipline: str


@dataclass(frozen=True, slots=True)
class PackBinding:
    """Validation data a Pack may reference directly, because it generalises.

    The ruleset identity travels with the keys. A ``requirement_key`` proves
    the row was found; it does not prove the row still means what the Pack
    author assumed, because severity, owner role, applicability and checker can
    all move underneath a key that never changes.
    """

    ruleset_id: str
    ruleset_version: str
    requirement_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class InsufficientEvidence:
    """A rule that is adjacent to the question and cannot answer it.

    Deliberately not a :class:`PackBinding`. Same existence check, same version
    check, opposite meaning — and ``cannot_answer`` is the sentence that says
    so, carried with the reference rather than left in a comment.
    """

    ruleset_id: str
    ruleset_version: str
    requirement_key: str
    cannot_answer: str


@dataclass(frozen=True, slots=True)
class PairSource:
    """Where a ``per-subject-pair`` requirement's counterpart keys come from.

    The counterparts are named by another evidence requirement's determination,
    under one named outcome — so both members of a pair exist whenever the pair
    does, and the assessment invents neither.
    """

    from_evidence_requirement_id: str
    on_outcome: str
    counterpart_description: str


@dataclass(frozen=True, slots=True)
class EvidenceRequirement:
    """What an activity needs to know, which is not a validation requirement."""

    evidence_requirement_id: str
    answers: str
    binding_source: str
    subject_grain: str
    acceptance_condition: str
    outcomes: tuple[str, ...]
    pack_binding: PackBinding | None = None
    insufficient_evidence: tuple[InsufficientEvidence, ...] = ()
    pair_source: PairSource | None = None


@dataclass(frozen=True, slots=True)
class Branch:
    """One outcome of one decision node: a leaf, or an edge to a deeper node.

    Exactly one of ``verdict`` and ``next_node`` is set. A ``BLOCKED`` leaf
    carries ``failure_kind`` and no ``gap_kind``; an ``UNKNOWN`` leaf the
    reverse; a ``READY`` leaf neither.
    """

    outcome: str
    verdict: str = ""
    failure_kind: str = ""
    gap_kind: str = ""
    next_node: str = ""
    renders_inapplicable: tuple[str, ...] = ()

    @property
    def is_leaf(self) -> bool:
        return bool(self.verdict)

    @property
    def resolution_kind(self) -> str:
        """The route key this leaf resolves through, or ``""`` for READY/edges.

        ``failure_kind`` and ``gap_kind`` draw from one shared namespace, which
        is why they reduce to a single value here.
        """

        return self.failure_kind or self.gap_kind


@dataclass(frozen=True, slots=True)
class DecisionNode:
    node_id: str
    evidence_requirement_id: str
    branches: tuple[Branch, ...]


@dataclass(frozen=True, slots=True)
class Activity:
    """One production activity at stake in a handover.

    ``subject_classes`` is declarative object-class data: which kinds of model
    object this activity's labour is about. It is never a filter on which
    elements happen to carry a finding — an element of a declared class with
    zero findings is precisely what the list exists to keep in view.
    """

    activity_id: str
    label: str
    direction_id: str
    subject_classes: tuple[str, ...]
    evidence_requirement_ids: tuple[str, ...]
    decision_root_node: str


@dataclass(frozen=True, slots=True)
class ResolutionRoute:
    """The one canonical chain from a non-READY leaf to what happens next.

    ``default_role`` is a Pack default and an *input* to an assignment, never
    an assignment. Only an Overlay's ``team_mapping`` turns it into something a
    runtime could task, and a missing mapping fails closed rather than falling
    back to the bound rule's ``owner_role``.
    """

    resolution_kind: str
    default_role: str
    consequence_kinds: tuple[str, ...]
    next_action: str
    recheck_condition: str


@dataclass(frozen=True, slots=True)
class PurposePack:
    """One loaded, structurally validated Pack.

    Reaching this type means every §3.8 invariant held. Nothing here is a
    verdict and nothing here is about any project.
    """

    pack_id: str
    pack_schema_version: str
    pack_version: str
    maturity: str
    citations: tuple[str, ...]
    directions: tuple[Direction, ...]
    evidence_requirements: tuple[EvidenceRequirement, ...]
    activities: tuple[Activity, ...]
    resolution_routes: tuple[ResolutionRoute, ...]
    decision_nodes: tuple[DecisionNode, ...]

    def evidence_requirement(self, evidence_requirement_id: str) -> EvidenceRequirement:
        for requirement in self.evidence_requirements:
            if requirement.evidence_requirement_id == evidence_requirement_id:
                return requirement
        raise KeyError(evidence_requirement_id)

    def node(self, node_id: str) -> DecisionNode:
        for node in self.decision_nodes:
            if node.node_id == node_id:
                return node
        raise KeyError(node_id)

    def route(self, resolution_kind: str) -> ResolutionRoute:
        for route in self.resolution_routes:
            if route.resolution_kind == resolution_kind:
                return route
        raise KeyError(resolution_kind)


# --------------------------------------------------------------------------
# Project Overlay
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class OverlayPackRef:
    """A Pack this project uses, at one exactly-pinned content version."""

    pack_id: str
    pack_version: str


@dataclass(frozen=True, slots=True)
class EvidenceBinding:
    """Which of this project's validation data answers a Pack question.

    Carries no ``decision_basis``: naming the rules that answer a question is a
    fact about a rule set, not a policy decision anyone had to take.
    """

    pack_id: str
    evidence_requirement_id: str
    ruleset_id: str
    ruleset_version: str
    requirement_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AcceptedEvidenceMethod:
    """A method this project accepts as producing an evidence outcome.

    Declaring a method is not a claim that it has been run, and
    ``decision_basis`` is what keeps a demonstration value from reading as a
    project's accepted practice.
    """

    pack_id: str
    evidence_requirement_id: str
    method_id: str
    description: str
    decision_basis: str


@dataclass(frozen=True, slots=True)
class TeamMapping:
    """How this project would staff one Pack ``default_role``.

    Project policy written in advance — not this run's assignment, not an
    actor, and not a claim that anyone has been tasked with anything.
    """

    role: str
    team_or_person: str
    decision_basis: str


@dataclass(frozen=True, slots=True)
class RiskAuthorisation:
    """Which roles may authorise a promotion, per ``pack_id::resolution_kind``.

    States who *may* act, never that anyone has. A ``resolution_kind`` with no
    row here has no authorisation path in this project at all — not a default
    one.
    """

    pack_id: str
    resolution_kind: str
    may_authorise_roles: tuple[str, ...]
    decision_basis: str


@dataclass(frozen=True, slots=True)
class Convention:
    """Narrative about a project-specific convention behind a bound rule."""

    ruleset_id: str
    ruleset_version: str
    requirement_key: str
    note: str


@dataclass(frozen=True, slots=True)
class ProjectOverlay:
    """One project's policy against the Pack(s) it uses.

    Its project identity is inherited by nesting — the Overlay is a table
    inside a ``project.toml`` that already declares ``project_id`` — so there
    is no ``project_id`` field here to drift out of step with that one.
    """

    packs: tuple[OverlayPackRef, ...] = ()
    evidence_bindings: tuple[EvidenceBinding, ...] = ()
    accepted_evidence_methods: tuple[AcceptedEvidenceMethod, ...] = ()
    team_mapping: tuple[TeamMapping, ...] = ()
    risk_authorisations: tuple[RiskAuthorisation, ...] = ()
    conventions: tuple[Convention, ...] = ()
    cost_parameters: Mapping[str, object] = field(
        default_factory=lambda: MappingProxyType({})
    )


# --------------------------------------------------------------------------
# The composed object
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ComposedPurposeInputs:
    """A project's Pack(s) and Overlay, validated together.

    This is what a future purpose assessment consumes. It is configuration that
    has been checked, and nothing more: every question the design says must be
    answered before an activity can be assessed has been answered, and no
    question the design says belongs to a runtime has been touched.

    ``composition_digest`` identifies *this composed configuration*. It is a
    deterministic hash of the parsed, totally ordered structure — never of file
    bytes, filenames, mtimes, or filesystem order — and it is never an input to
    ``validation_run_id``, ``requirement_key``, ``finding_key``, or any other
    published-contract value. The dependency points one way: an assessment may
    cite frozen identities; nothing frozen cites this.
    """

    project_id: str
    packs: tuple[PurposePack, ...]
    overlay: ProjectOverlay
    composition_digest: str

    def pack(self, pack_id: str) -> PurposePack:
        for pack in self.packs:
            if pack.pack_id == pack_id:
                return pack
        raise KeyError(pack_id)
