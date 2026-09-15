"""Run one purpose assessment against validated facts, and seal what it found.

This is the demand-driven operation ``AGENTS.md`` places between ``check`` and
the compatible group, and ADR 0003 fixes its shape. It is **not** a pipeline
stage: not a ``Checker``, not a ``GroupingPolicy``, not an ``Exporter``, absent
from ``default_registry``, never invoked by ``epc-ct run``, and it writes no
file. Whether or not an assessment is ever requested, ``check → group →
export``, the snapshot and both ``Legacy…`` writers produce byte-identical
output.

The modules divide along the lines the design already draws:

======================  ====================================================
:mod:`.request`         what a caller must declare — scope and model versions
:mod:`.facts`           the validated facts an assessment may read, and only
                        those; the projection is what makes §3.4 structural
:mod:`.determinations`  determinations arrive by reference and are admitted or
                        declined, never decided
:mod:`.authorisation`   whether this project's policy authorises one promotion,
                        asked when a promotion would consume it and never before
:mod:`.reading`         how one subject's evidence collapses to one outcome
:mod:`.evaluator`       the tree walk, the partition, the routes, the refusals
:mod:`.recheck`         succeeding a sealed record: member correspondence,
                        evidence carry-over, and what could be established
                        about a recheck condition
:mod:`.record`          the carrier, the path, the leaf, and the seal
======================  ====================================================

What this package does **not** build, and where the absence is deliberate rather
than unfinished: no ``CONDITIONAL`` promotion and no ``authorisation`` successor,
no public machine contract, no CLI, no Doctor, and no storage layer — a record is
returned sealed, and where it is put is a later decision. The ``recheck``
successor is built; the ``authorisation`` one is named in the closed vocabulary
and nothing more.

:mod:`.authorisation` is not an exception to that. It answers the single policy
question ADR 0003 §4.4 field 5 says a promotion must be able to prove — whether
this project's Overlay authorises the cited role for that exact
``pack_id::resolution_kind`` — and builds no promotion around it: none of §4.4's
nine fields, none of §4.5's continuation checks, no successor, no store. Nothing
in the walk imports it, because until a promotion exists there is nothing to
consume it, and §7.2's opening is what makes that the right shape: every refusal
it raises is promotion-scoped, so the leaf stands and the request is unaffected.
"""

from __future__ import annotations

from ..errors import PurposeAssessmentError
from .authorisation import (
    AUTHORISED,
    NO_AUTHORISATION_PATH,
    RISK_AUTHORISATION_ANSWERS,
    ROLE_NOT_AUTHORISED,
    AuthorisationCitation,
    RiskAuthorisationDecision,
    resolve_risk_authorisation,
)
from .determinations import (
    Admissibility,
    Determination,
    DeterminationLedger,
    DeterminedAgainst,
)
from .evaluator import assess_purpose, derive_assessment
from .facts import (
    AssessmentFacts,
    ElementFact,
    FindingFact,
    ModelVersionFact,
    facts_from_bundle,
)
from .reading import (
    NOT_COVERED_ABSENCE,
    NO_FINDING_ABSENCE,
    UNRESOLVED_OUTCOMES,
    VALIDATION_BACKED_OUTCOMES,
)
from .recheck import machine_checkable_outcome, recheck_purpose
from .record import (
    CARRY_OVER_REASONS,
    MEMBER_DISPOSITIONS,
    RECHECK_CONDITION_STATES,
    SUCCESSOR_KINDS,
    ActivityResult,
    AssessmentRecord,
    CitedDetermination,
    ContextComparison,
    EvidenceCarryOver,
    MemberDisposition,
    OutOfClassKey,
    PathStep,
    Reading,
    RecheckOutcome,
    ResolvedRoute,
    ResolvingAssignment,
    Subject,
    SubscopeResult,
    SuccessorSection,
    build_assessment_digest,
)
from .request import (
    AssessedScope,
    AssessmentRequest,
    HandoverEvent,
    ModelVersion,
    ModelVersionContext,
)

__all__ = [
    "AUTHORISED",
    "CARRY_OVER_REASONS",
    "MEMBER_DISPOSITIONS",
    "NOT_COVERED_ABSENCE",
    "NO_AUTHORISATION_PATH",
    "NO_FINDING_ABSENCE",
    "RECHECK_CONDITION_STATES",
    "RISK_AUTHORISATION_ANSWERS",
    "ROLE_NOT_AUTHORISED",
    "SUCCESSOR_KINDS",
    "UNRESOLVED_OUTCOMES",
    "VALIDATION_BACKED_OUTCOMES",
    "ActivityResult",
    "Admissibility",
    "AssessedScope",
    "AssessmentFacts",
    "AssessmentRecord",
    "AssessmentRequest",
    "AuthorisationCitation",
    "CitedDetermination",
    "ContextComparison",
    "Determination",
    "DeterminationLedger",
    "DeterminedAgainst",
    "ElementFact",
    "EvidenceCarryOver",
    "FindingFact",
    "HandoverEvent",
    "MemberDisposition",
    "ModelVersion",
    "ModelVersionContext",
    "ModelVersionFact",
    "OutOfClassKey",
    "PathStep",
    "PurposeAssessmentError",
    "Reading",
    "RecheckOutcome",
    "ResolvedRoute",
    "RiskAuthorisationDecision",
    "ResolvingAssignment",
    "Subject",
    "SubscopeResult",
    "SuccessorSection",
    "assess_purpose",
    "build_assessment_digest",
    "derive_assessment",
    "facts_from_bundle",
    "machine_checkable_outcome",
    "recheck_purpose",
    "resolve_risk_authorisation",
]
