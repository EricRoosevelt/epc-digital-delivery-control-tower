"""Purpose Packs and Project Overlays: loading them, and assessing against them.

Two halves, and the split is the design rather than a filing convention:

* this package's own modules read two kinds of file —
  ``purpose-packs/<pack_id>/pack.toml`` and the ``[overlay]`` table of a
  ``projects/<id>/project.toml`` — and produce one validated
  :class:`~.model.ComposedPurposeInputs` for a project, or refuse;
* :mod:`~.assessment` consumes that configuration, walks a Pack's decision tree
  over validated facts for one declared scope and one model-version context, and
  returns one sealed assessment record, or refuses.

**Neither is a pipeline component.** Not a ``Checker``, a ``GroupingPolicy``, or
an ``Exporter``; absent from ``default_registry``; never invoked by ``epc-ct
run``; and nothing here writes to ``data/processed/``, ``reports/``, or
``ids/``. `AGENTS.md` settles why: a purpose assessment is approved between
``check`` and the compatible group, and registering an approval step as a
pipeline component would put a decision inside a projection.

**Configuration still cannot express readiness.** What the composition produces
has no verdict, no evidence outcome, no reading, no subscope, no resolving
assignment and no risk acceptance — not as a field, not as a cached value. Those
are runtime facts about one assessment of two specific model versions, and they
live in a record, never in a project setting. See :mod:`~.model` for why each of
those absences is load-bearing.

Everything here is deterministic: no clock, no unordered iteration, no
dependence on filesystem order, and the one identifier it mints hashes parsed
sorted structure rather than file bytes.
"""

from __future__ import annotations

from .assessment import (
    AssessedScope,
    AssessmentFacts,
    AssessmentRecord,
    AssessmentRequest,
    Determination,
    HandoverEvent,
    ModelVersion,
    ModelVersionContext,
    assess_purpose,
    facts_from_bundle,
)
from .composition import build_composition_digest, compose_purpose_inputs
from .errors import (
    PurposeAssessmentError,
    PurposeCompositionError,
    PurposeError,
    PurposePackError,
)
from .model import (
    BINDING_SOURCES,
    DECISION_BASES,
    SUBJECT_GRAINS,
    VERDICTS,
    AcceptedEvidenceMethod,
    Activity,
    Branch,
    ComposedPurposeInputs,
    Convention,
    DecisionNode,
    Direction,
    EvidenceBinding,
    EvidenceRequirement,
    InsufficientEvidence,
    OverlayPackRef,
    PackBinding,
    PairSource,
    ProjectOverlay,
    PurposePack,
    ResolutionRoute,
    RiskAuthorisation,
    TeamMapping,
)
from .overlay import load_project_overlay, read_overlay_table
from .pack import (
    SUPPORTED_PACK_SCHEMA_VERSIONS,
    discover_purpose_packs,
    load_purpose_pack,
    load_purpose_packs,
)

__all__ = [
    "BINDING_SOURCES",
    "DECISION_BASES",
    "SUBJECT_GRAINS",
    "SUPPORTED_PACK_SCHEMA_VERSIONS",
    "VERDICTS",
    "AcceptedEvidenceMethod",
    "Activity",
    "AssessedScope",
    "AssessmentFacts",
    "AssessmentRecord",
    "AssessmentRequest",
    "Branch",
    "ComposedPurposeInputs",
    "Convention",
    "DecisionNode",
    "Determination",
    "Direction",
    "EvidenceBinding",
    "EvidenceRequirement",
    "HandoverEvent",
    "InsufficientEvidence",
    "ModelVersion",
    "ModelVersionContext",
    "OverlayPackRef",
    "PackBinding",
    "PairSource",
    "ProjectOverlay",
    "PurposeAssessmentError",
    "PurposeCompositionError",
    "PurposeError",
    "PurposePack",
    "PurposePackError",
    "ResolutionRoute",
    "RiskAuthorisation",
    "TeamMapping",
    "assess_purpose",
    "build_composition_digest",
    "compose_purpose_inputs",
    "discover_purpose_packs",
    "facts_from_bundle",
    "load_project_overlay",
    "load_purpose_pack",
    "load_purpose_packs",
    "read_overlay_table",
]
