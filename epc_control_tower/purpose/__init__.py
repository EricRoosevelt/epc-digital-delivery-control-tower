"""Loading and fail-closed composition of Purpose Packs and Project Overlays.

This package reads two kinds of file — ``purpose-packs/<pack_id>/pack.toml``
and the ``[overlay]`` table of a ``projects/<id>/project.toml`` — and produces
one validated :class:`~.model.ComposedPurposeInputs` for a project, or refuses.

**It is not a pipeline component.** It is not a ``Checker``, a
``GroupingPolicy``, or an ``Exporter``; it does not appear in
``default_registry``; ``epc-ct run`` never invokes it; and it writes nothing to
``data/processed/``, ``reports/``, or ``ids/``. `AGENTS.md` settles why: a
purpose assessment is approved between ``check`` and the compatible group, and
registering an approval step as a pipeline component would put a decision
inside a projection. This package is the *input* half of that step — the
evaluator that would consume its output does not exist yet.

**What it produces cannot express readiness.** No verdict, no evidence outcome,
no reading, no subscope, no resolving assignment, no risk acceptance. See
:mod:`~.model` for why each of those absences is load-bearing.

Everything here is deterministic: no clock, no unordered iteration, no
dependence on filesystem order, and the one identifier it mints hashes parsed
sorted structure rather than file bytes.
"""

from __future__ import annotations

from .composition import build_composition_digest, compose_purpose_inputs
from .errors import PurposeCompositionError, PurposeError, PurposePackError
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
    "PurposeCompositionError",
    "PurposeError",
    "PurposePack",
    "PurposePackError",
    "ResolutionRoute",
    "RiskAuthorisation",
    "TeamMapping",
    "build_composition_digest",
    "compose_purpose_inputs",
    "discover_purpose_packs",
    "load_project_overlay",
    "load_purpose_pack",
    "load_purpose_packs",
    "read_overlay_table",
]
