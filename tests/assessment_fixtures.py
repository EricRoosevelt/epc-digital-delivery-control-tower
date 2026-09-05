"""Scaffolding for the purpose-assessment tests.

Not a test module — it defines no tests and pytest does not collect it.

Everything here divides into two halves, and keeping the halves visibly apart is
this module's main job:

**Original facts, reused unchanged.** The elements, the findings, the ruleset,
the shipped Purpose Pack and ``pcert-sample``'s ``evidence_bindings`` are the
repository's own. Their validation value is precisely that they are real: the
three R-005 ``FAIL`` findings really are ``WARNING``, the ``IfcChimney`` really
has zero findings, the two ``IfcBuildingElementProxy`` setout markers really are
setout markers, and R-010's ``PASS`` really is a pass. A fixture that invented
any of them would prove the evaluator handles a situation nobody has.

**Policy and determinations supplied by the test.** Every function below whose
name begins ``fixture_`` returns something this repository has *not* decided: a
staffing basis, a coordination-review determination, an alignment confirmation.
They exist so an assessment can be driven past the point where ``pcert-sample``'s
own policy stops it, and they are:

* never written back to ``projects/pcert-sample/project.toml`` or any other
  tracked manifest — they are built in memory from a parsed copy;
* never published as a project assessment — no test stores a record anywhere the
  repository ships;
* passed to the **same** :func:`~epc_control_tower.purpose.assess_purpose` the
  real entry point uses, with no skip flag, no test mode, and no relaxed check.
  The fixture gets past the policy gate by *declaring different policy*, which is
  what a project that had taken these decisions would do.

The distinction matters because the alternative — a switch that lets tests skip
the gate — would make the gate untested exactly where it is load bearing.
"""

from __future__ import annotations

import copy
import shutil
import uuid
from pathlib import Path

from epc_control_tower.purpose import (
    AssessedScope,
    AssessmentRequest,
    Determination,
    HandoverEvent,
    ModelVersion,
    ModelVersionContext,
    compose_purpose_inputs,
    facts_from_bundle,
    load_purpose_pack,
    read_overlay_table,
)
from helpers import PROJECT_ROOT, shipped_pipeline_result
from purpose_fixtures import (
    base_overlay_document,
    base_pack_document,
    mutated,
    write_pack,
)

__all__ = [
    "ALIGNMENT_CONFIRMED",
    "ARCHITECTURE_ROOF",
    "ARCHITECTURE_SLAB",
    "HVAC_AIR_TERMINAL_CAP",
    "HVAC_AIR_TERMINAL_COVER",
    "HVAC_CHIMNEY",
    "HVAC_DUCT",
    "HVAC_GEO_REFERENCE",
    "HVAC_ORIGIN",
    "PACK_ID",
    "assessment_facts",
    "fixture_composed",
    "fixture_determinations",
    "fixture_overlay_document",
    "fixture_request",
    "requirement_keys_by_ruleset",
    "scratch_pack",
]

PACK_ID = "interdisciplinary-coordination-readiness"
PACK_PATH = PROJECT_ROOT / "purpose-packs" / PACK_ID / "pack.toml"

# --- Original facts: real element keys from data/processed/canonical/elements.csv.
HVAC_DUCT = "hvac::38WbwIGD90nB_3T2BTU5Ed"  # IfcDuctSegment
HVAC_AIR_TERMINAL_COVER = "hvac::23uPJWDfXEcwHH3kdFgV9c"  # IfcAirTerminal
HVAC_AIR_TERMINAL_CAP = "hvac::34Y6EIt3nDCAS1k$kPGOKm"  # IfcAirTerminal
HVAC_CHIMNEY = "hvac::3dkFAzOGrAIuOzY_RdrdVv"  # IfcChimney, zero findings
HVAC_ORIGIN = "hvac::2F44QMqSH3TOkM$SZoqCBe"  # IfcBuildingElementProxy setout marker
HVAC_GEO_REFERENCE = "hvac::3Fit2Fad92zf2f6aWdJtF5"  # IfcBuildingElementProxy, zero findings
ARCHITECTURE_SLAB = "architecture::3zR0BOEcLADRKln4HYporH"  # IfcSlab, ground floor
ARCHITECTURE_ROOF = "architecture::2iPwJwpPDCSgMheXwk9cBT"  # IfcRoof

#: A test-supplied alignment confirmation. Named so that no reader mistakes it
#: for a claim that pcert-sample's models have been confirmed aligned.
ALIGNMENT_CONFIRMED = "fixture-determination/alignment/confirmed"


def assessment_facts(project_id: str = "pcert-sample"):
    """The shipped run's validated facts, narrowed and otherwise untouched."""

    return facts_from_bundle(shipped_pipeline_result().bundle, project_id)


def requirement_keys_by_ruleset() -> dict[tuple[str, str], frozenset[str]]:
    ruleset = shipped_pipeline_result().bundle.ruleset
    return {
        (ruleset.ruleset_id, ruleset.version): frozenset(
            requirement.requirement_key for requirement in ruleset.requirements
        )
    }


def fixture_overlay_document() -> dict:
    """``pcert-sample``'s Overlay with its staffing recorded as decided.

    The only edit is ``decision_basis``: every ``team_mapping`` row moves from
    ``illustrative`` to ``project-decision``. Nothing else changes — the same
    four roles, the same four teams, the same real ``evidence_bindings`` naming
    the same four R-005 ``requirement_key`` values.

    This is a **test setting**, not a correction. ``pcert-sample`` has never
    staffed anybody, which is why its own manifest says so and why the real
    entry point refuses it. What this fixture supplies is the one input that
    refusal is about, so that everything behind the gate can be exercised.
    """

    document = copy.deepcopy(base_overlay_document())
    for row in document["overlay"]["team_mapping"]:
        row["decision_basis"] = "project-decision"
    return document


def fixture_composed(*, overlay_document: dict | None = None, pack=None):
    """Compose the real Pack against the fixture's Overlay, through the real composer."""

    document = overlay_document or fixture_overlay_document()
    # The source path a refusal would name is this module, because this module
    # is where the fixture's policy was written — not pcert-sample's manifest,
    # which the fixture never edits.
    overlay = read_overlay_table(document, Path(__file__))
    return compose_purpose_inputs(
        project_id="pcert-sample",
        overlay=overlay,
        packs=(pack or load_purpose_pack(PACK_PATH),),
        requirement_keys_by_ruleset=requirement_keys_by_ruleset(),
    )


def fixture_request(
    *,
    activity_ids: tuple[str, ...],
    facts,
    scope: AssessedScope | None = None,
    pack_id: str = PACK_ID,
) -> AssessmentRequest:
    """One request over the whole ``hvac`` model version, declared explicitly.

    The scope is the model, not the elements that have findings. That is the
    point of declaring it: expanding a ``model_key`` sweeps in the ``IfcChimney``
    no rule reached and both setout markers, and the assessment then has to say
    what became of each.
    """

    models = {model.model_key: model.content_id for model in facts.models}
    return AssessmentRequest(
        project_id="pcert-sample",
        pack_id=pack_id,
        pack_version="0.1.0",
        direction_id="mep-to-architecture",
        activity_ids=activity_ids,
        assessed_scope=scope or AssessedScope(model_keys=("hvac",)),
        model_version_context=ModelVersionContext(
            producing=ModelVersion("hvac", models["hvac"]),
            consuming=ModelVersion("architecture", models["architecture"]),
            handover=HandoverEvent(
                from_role="MEP",
                to_role="Architecture",
                milestone="Coordination",
                date="2026-08-01T00:00:00Z",
            ),
        ),
    )


def fixture_determinations(
    *, alignment: bool = True, penetration: bool = True
) -> tuple[Determination, ...]:
    """Determinations a coordination review would have produced, had one been held.

    None of these has been held for ``pcert-sample``. They are written here so
    the evaluator can be driven through the paths only a determination opens,
    and in particular through the one this checkpoint has to prove: the chimney
    passes through a floor slab whose opening is cross-referenced and a roof
    whose opening is not modelled, so one admitted element refines into two
    pairs that reach two different verdicts.

    ``alignment=False`` leaves ``cross-model-alignment`` undetermined while
    R-010's ``PASS`` stays exactly where it is, which is how the test that a
    ``PASS`` is not a confirmation is set up.
    """

    determinations: list[Determination] = []
    if alignment:
        determinations.append(
            Determination(
                reference=ALIGNMENT_CONFIRMED,
                evidence_requirement_id="cross-model-alignment",
                method_id="overlay-comparison",
                determiner="fixture-model-coordination",
                basis="fixture: placements overlaid in a common viewer",
                outcome="confirmed",
                # The model pair this confirmation is about. A whole-scope
                # determination names its pair, so a confirmation produced for
                # some other pair of models can never be read as this one.
                subject=("hvac", "architecture"),
            )
        )
    if not penetration:
        return tuple(determinations)

    determinations.extend(
        [
            # The duct penetrates nothing, so opening-status is structurally
            # ruled out along its path and it reaches READY at the first node.
            Determination(
                reference="fixture-determination/penetration/duct-none",
                evidence_requirement_id="penetration-determination",
                method_id="coordination-review-determination",
                determiner="fixture-coordination-review",
                basis="fixture: reviewed, no fabric penetrated",
                outcome="no-penetration",
                subject=(HVAC_DUCT,),
            ),
            # The chimney passes through two architectural elements, both named
            # as element_key values of the consuming model version.
            Determination(
                reference="fixture-determination/penetration/chimney-slab-and-roof",
                evidence_requirement_id="penetration-determination",
                method_id="coordination-review-determination",
                determiner="fixture-coordination-review",
                basis="fixture: reviewed, chimney rises through the floor slab and the roof",
                outcome="penetration-confirmed",
                subject=(HVAC_CHIMNEY,),
                penetrated_element_keys=(ARCHITECTURE_SLAB, ARCHITECTURE_ROOF),
            ),
            # One pair's opening is modelled and cross-referenced; the other's is
            # not modelled at all. Two readings, two verdicts, one chimney.
            Determination(
                reference="fixture-determination/opening/chimney-slab-cross-referenced",
                evidence_requirement_id="opening-status",
                method_id="opening-cross-reference-check",
                determiner="fixture-architecture-lead",
                basis="fixture: opening carries a reference back to the chimney",
                outcome="cross-referenced",
                subject=(HVAC_CHIMNEY, ARCHITECTURE_SLAB),
            ),
            Determination(
                reference="fixture-determination/opening/chimney-roof-not-modelled",
                evidence_requirement_id="opening-status",
                method_id="opening-cross-reference-check",
                determiner="fixture-architecture-lead",
                basis="fixture: no opening modelled in the roof",
                outcome="not-modelled",
                subject=(HVAC_CHIMNEY, ARCHITECTURE_ROOF),
            ),
        ]
    )
    return tuple(determinations)


class scratch_pack:
    """Write a mutated Pack document to a throwaway directory and load it.

    A context manager because a Pack is loaded from a path, and leaving a
    fixture Pack in ``purpose-packs/`` would put a Pack this repository does not
    ship into the tree the working-directory gate reads.
    """

    def __init__(self, mutate) -> None:
        self._mutate = mutate
        self._path: Path | None = None

    def __enter__(self):
        document = mutated(base_pack_document())
        self._mutate(document)
        self._path = PROJECT_ROOT / "tests" / f".assessment-pack-{uuid.uuid4().hex}"
        self._path.mkdir(mode=0o777)
        return load_purpose_pack(write_pack(self._path, document))

    def __exit__(self, *exception) -> None:
        if self._path is not None:
            shutil.rmtree(self._path, ignore_errors=True)
        return None
