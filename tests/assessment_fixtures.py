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

**A second set of validated facts, for the recheck chain.**
:func:`fixture_reissued_facts` is the same shipped facts with the HVAC model
version moved and the R-005 failures repaired — the state a production owner
would be in *after* acting on a blocker. It has to exist because the chain a
recheck serves is *initial assessment, fix, re-validation, recheck*, and a fix
that changes no model version is not a fix. It belongs to the second half above,
not the first: every value it mints carries :data:`FIXTURE_MARKER`, so "this is
not a real run, and pcert-sample's HVAC model has not been reissued" is a
property a test can assert rather than a convention a reader has to know, and
:mod:`test_purpose_isolation` asserts exactly that against the published tree.
"""

from __future__ import annotations

import copy
import shutil
import uuid
from pathlib import Path

from epc_control_tower.purpose import (
    AssessedScope,
    AssessmentFacts,
    AssessmentRequest,
    Determination,
    DeterminedAgainst,
    HandoverEvent,
    ModelVersion,
    ModelVersionContext,
    compose_purpose_inputs,
    facts_from_bundle,
    load_purpose_pack,
    read_overlay_table,
)
from epc_control_tower.purpose.assessment.facts import (
    ElementFact,
    FindingFact,
    ModelVersionFact,
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
    "ALIGNMENT_VARIANTS",
    "FIXTURE_MARKER",
    "asset_identity_requirement_keys",
    "determined_against",
    "ARCHITECTURE_ROOF",
    "ARCHITECTURE_SLAB",
    "HVAC_AIR_TERMINAL_CAP",
    "HVAC_AIR_TERMINAL_COVER",
    "HVAC_CHIMNEY",
    "HVAC_DUCT",
    "HVAC_GEO_REFERENCE",
    "HVAC_ORIGIN",
    "PACK_ID",
    "REISSUED_HVAC_CONTENT_ID",
    "REISSUED_VALIDATION_RUN_ID",
    "ROOF_OPENING_BASIS",
    "reissued_content_id",
    "assessment_facts",
    "fixture_alignment_variants",
    "fixture_composed",
    "fixture_determinations",
    "fixture_narrowed_penetration_determinations",
    "fixture_overlay_document",
    "fixture_reissued_facts",
    "fixture_reissued_request",
    "fixture_request",
    "fixture_superseding_determinations",
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

#: What an opening review would have written down, per outcome it could reach for
#: the chimney's roof pair. Three of ``opening-status``'s four declared outcomes;
#: the fourth, ``not-yet-determined``, is what you get by offering no
#: determination at all, which needs no basis because nobody wrote one.
ROOF_OPENING_BASIS = {
    "not-modelled": "fixture: no opening modelled in the roof",
    "modelled-not-cross-referenced": (
        "fixture: an opening is now cut in the roof and carries no reference back "
        "to the chimney"
    ),
    "cross-referenced": (
        "fixture: the roof opening is modelled and carries a reference back to the "
        "chimney"
    ),
}

#: The prefix every value this module mints carries, so that "not a real value"
#: is a property a machine can test rather than a convention a reader has to
#: know. A content identifier in this repository is a SHA-256 and a
#: ``validation_run_id`` is a derived digest; neither can begin with a word.
FIXTURE_MARKER = "fixture"


def reissued_content_id(model_key: str) -> str:
    """The content identifier the second set of facts gives a reissued model.

    Deliberately **not** a hash. A content identifier in this repository is a
    SHA-256, so a plausible-looking hex string here would be a claim that
    ``pcert-sample``'s model was reissued — and none of them ever has been. This
    value cannot be mistaken for one, and cannot be matched by anything that
    scans the published tree for real ones.
    """

    return f"{FIXTURE_MARKER}-content/{model_key}-reissued-not-a-real-export"


#: The producing model version the default second set of facts is about.
REISSUED_HVAC_CONTENT_ID = reissued_content_id("hvac")

#: The run the second set of facts is attributed to. No such run exists; this
#: repository publishes exactly one validation run and it is not this one.
REISSUED_VALIDATION_RUN_ID = (
    f"{FIXTURE_MARKER}-validation-run/reissued-hvac-not-a-real-run"
)


def asset_identity_requirement_keys() -> frozenset[str]:
    """The ``requirement_key`` values ``pcert-sample`` binds to ``asset-identity``.

    Read back from the shipped manifest rather than restated here, so the
    repaired fixture findings below cannot drift away from the real binding and
    quietly stop repairing anything.
    """

    for row in base_overlay_document()["overlay"]["evidence_bindings"]:
        if row["evidence_requirement_id"] == "asset-identity":
            return frozenset(row["requirement_keys"])
    raise AssertionError("pcert-sample no longer binds asset-identity")


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
    """``pcert-sample``'s Overlay with its policy recorded as decided.

    The only edits are ``decision_basis``: every ``team_mapping`` row and every
    ``accepted_evidence_methods`` row moves from ``illustrative`` to
    ``project-decision``. Nothing else changes — the same four roles, the same
    four teams, the same three methods, the same real ``evidence_bindings``
    naming the same four R-005 ``requirement_key`` values.

    **Both tables, and stating that explicitly is the point.** An earlier version
    of this fixture flipped only ``team_mapping``, and the positive path went
    green while the evaluator was consuming an alignment determination produced
    by a method whose row still read ``illustrative``. The green light was being
    held up by a check that did not exist. Declaring the method policy here means
    the fixture asserts what it relies on, and the gate that would otherwise have
    caught it is exercised by its own test rather than by this one's silence.

    This is a **test setting**, not a correction. ``pcert-sample`` has never
    staffed anybody and has never accepted a method, which is why its own
    manifest says so on all seven rows and why the real entry point refuses it.
    """

    document = copy.deepcopy(base_overlay_document())
    for table in ("team_mapping", "accepted_evidence_methods"):
        for row in document["overlay"][table]:
            row["decision_basis"] = "project-decision"
    return document


def determined_against(facts) -> DeterminedAgainst:
    """The model versions this fixture's determinations were made against.

    The real content hashes of the two model versions in play, so a determination
    is attributable to exactly the versions the request names — which is what the
    version-attribution check compares, value for value.
    """

    models = {model.model_key: model.content_id for model in facts.models}
    return DeterminedAgainst(
        producing_model_key="hvac",
        producing_content_id=models["hvac"],
        consuming_model_key="architecture",
        consuming_content_id=models["architecture"],
    )


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
    *,
    facts,
    alignment: bool = True,
    penetration: bool = True,
    roof_opening: str = "not-modelled",
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

    ``roof_opening`` is what a *later* opening review, held after the roof
    opening was cut, would report. It is the only knob a recheck chain needs to
    move: the blocker the first record carried is
    ``missing-corresponding-opening``, whose ``recheck_condition`` names
    ``cross-referenced`` by that name, so the three values here are the three
    answers a recheck can honestly reach about it — the condition's named outcome
    observed, a *different* deficiency, or the same one again.
    """

    against = determined_against(facts)
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
                determined_against=against,
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
                determined_against=against,
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
                determined_against=against,
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
                determined_against=against,
            ),
            Determination(
                reference=(
                    f"fixture-determination/opening/chimney-roof-{roof_opening}"
                ),
                evidence_requirement_id="opening-status",
                method_id="opening-cross-reference-check",
                determiner="fixture-architecture-lead",
                basis=ROOF_OPENING_BASIS[roof_opening],
                outcome=roof_opening,
                subject=(HVAC_CHIMNEY, ARCHITECTURE_ROOF),
                determined_against=against,
            ),
        ]
    )
    return tuple(determinations)


def fixture_reissued_facts(
    *,
    reissued_model_key: str = "hvac",
    asset_identity_fixed: bool = True,
    delete_chimney: bool = False,
    chimney_ifc_class: str | None = None,
):
    """A **second** set of validated facts: one model reissued and re-validated.

    This is the other half of the chain a recheck exists to serve — *initial
    assessment, fix, re-validation, recheck* — and it cannot be told with one set
    of facts, because a fix that changes no model version is not a fix.

    Every value this function mints carries :data:`FIXTURE_MARKER`, and that is
    not decoration. It is the same discipline the Overlay's nine ``illustrative``
    rows and this module's determinations already run on: a fixture value must be
    **machine-visibly untrue**, so that no reader and no test can mistake it for
    a claim about this repository. Concretely, nothing here asserts that
    ``pcert-sample``'s HVAC model has ever been reissued or that any coordination
    review has ever been held. ``projects/pcert-sample/project.toml`` is not
    touched, no file is written, and
    ``test_purpose_isolation`` asserts that none of these values reaches
    ``data/processed/``, ``reports/``, ``ids/``, or the contract snapshot.

    ``reissued_model_key`` chooses which side of the handover moved. ``"hvac"``
    is the producing model — the MEP author fixed their own asset identities;
    ``"architecture"`` is the consuming one — the architect cut the opening the
    first record was blocked on. Both are re-issues and both make every
    determination attributed to the earlier pair inadmissible, which is the point.

    ``asset_identity_fixed`` turns the three real R-005 ``FAIL`` rows into
    ``PASS`` ones under fixture finding keys — the repair a production owner would
    have made between the two records. ``delete_chimney`` and
    ``chimney_ifc_class`` produce the other two ways a subject can leave a scope
    without anything being resolved.
    """

    if reissued_model_key not in {"hvac", "architecture"}:
        raise AssertionError(f"no such model version in this project: {reissued_model_key}")

    original = assessment_facts()
    models = tuple(
        ModelVersionFact(
            model_key=model.model_key,
            content_id=(
                reissued_content_id(model.model_key)
                if model.model_key == reissued_model_key
                else model.content_id
            ),
        )
        for model in original.models
    )

    elements = []
    for element in original.elements:
        if element.element_key == HVAC_CHIMNEY:
            if delete_chimney:
                continue
            if chimney_ifc_class is not None:
                elements.append(
                    ElementFact(
                        element_key=element.element_key,
                        model_key=element.model_key,
                        ifc_class=chimney_ifc_class,
                    )
                )
                continue
        elements.append(element)

    bound = asset_identity_requirement_keys()
    findings = []
    for finding in original.findings:
        repaired = (
            asset_identity_fixed
            and finding.status == "FAIL"
            and finding.requirement_key in bound
        )
        if delete_chimney and finding.element_key == HVAC_CHIMNEY:
            continue
        findings.append(
            FindingFact(
                # A re-validated model produces new finding keys. Minting fixture
                # ones rather than reusing the sealed record's is what makes the
                # carry-over check say something: the prior citations really are
                # gone, exactly as they would be after a real reissue.
                finding_key=(
                    f"{FIXTURE_MARKER}/finding/{finding.finding_key}"
                    if repaired
                    else finding.finding_key
                ),
                element_key=finding.element_key,
                requirement_key=finding.requirement_key,
                status="PASS" if repaired else finding.status,
            )
            if repaired
            else finding
        )

    return AssessmentFacts(
        project_id=original.project_id,
        validation_run_id=REISSUED_VALIDATION_RUN_ID,
        ruleset_id=original.ruleset_id,
        ruleset_version=original.ruleset_version,
        elements=tuple(sorted(elements, key=lambda item: item.element_key)),
        findings=tuple(
            sorted(
                findings,
                key=lambda item: (
                    item.element_key,
                    item.requirement_key,
                    item.finding_key,
                ),
            )
        ),
        milestones=original.milestones,
        models=models,
    )


def fixture_reissued_request(
    *,
    activity_ids: tuple[str, ...],
    facts,
    scope: AssessedScope | None = None,
) -> AssessmentRequest:
    """The same question, asked of the reissued model version.

    Same project, same Pack, same direction, same activities. What moved is the
    producing model's content identifier, which is the whole point: a verdict is
    only ever true of the exact versions named, and this is the request that
    names the other ones.
    """

    return fixture_request(activity_ids=activity_ids, facts=facts, scope=scope)


def fixture_superseding_determinations(*, facts) -> tuple[Determination, ...]:
    """A later coordination review, held against the **same** model versions.

    The earlier review recorded the chimney as penetrating a floor slab and the
    roof. This one, re-held, records that it penetrates nothing. Nothing about
    either model changed — a review can be re-held and correct itself, and each
    record cites the review it read.

    This is the live counterexample the design turns on. Under this
    determination the chimney takes the ``no-penetration`` branch, reaches
    ``READY``, and ``renders_inapplicable`` ends the path before ``opening-status``
    is ever asked. So the openings activity is ``READY`` while **no opening was
    modelled and no cross-reference was added** — and the prior record's
    ``missing-corresponding-opening`` blocker did not clear, its subject stopped
    being derived.
    """

    against = determined_against(facts)
    return (
        Determination(
            reference=ALIGNMENT_CONFIRMED,
            evidence_requirement_id="cross-model-alignment",
            method_id="overlay-comparison",
            determiner="fixture-model-coordination",
            basis="fixture: placements overlaid in a common viewer",
            outcome="confirmed",
            subject=("hvac", "architecture"),
            determined_against=against,
        ),
        Determination(
            reference="fixture-determination/penetration/duct-none",
            evidence_requirement_id="penetration-determination",
            method_id="coordination-review-determination",
            determiner="fixture-coordination-review",
            basis="fixture: reviewed, no fabric penetrated",
            outcome="no-penetration",
            subject=(HVAC_DUCT,),
            determined_against=against,
        ),
        Determination(
            reference="fixture-determination/penetration/chimney-none-on-re-review",
            evidence_requirement_id="penetration-determination",
            method_id="coordination-review-determination",
            determiner="fixture-coordination-review",
            basis="fixture: re-reviewed, the chimney passes through no architectural fabric",
            outcome="no-penetration",
            subject=(HVAC_CHIMNEY,),
            determined_against=against,
        ),
    )


#: The five ways a later record can meet the alignment determination the first
#: one read. Named here rather than built inline in a test, because each is a
#: *store behaviour* somebody has to imagine on this project's behalf — nobody
#: has re-held a coordination review here — and the module docstring's rule is
#: that everything this repository has not decided lives in one place.
ALIGNMENT_VARIANTS = (
    #: Byte for byte the determination the first record read.
    "unchanged",
    #: The same handle, and the review behind it now reports the models
    #: misaligned. The verdict must move to BLOCKED and the carry-over row must
    #: not say the old determination was carried.
    "same-reference-new-conclusion",
    #: The same handle and the same conclusion, re-signed by somebody else on a
    #: different basis. The verdict does not move at all, which is exactly why a
    #: comparison of handles would never have noticed.
    "same-reference-new-determiner",
    #: The same handle, re-attributed to model versions this request does not
    #: name. Already refused by ``determination-model-version-mismatch``; kept
    #: here so that the refusal is a regression rather than a memory.
    "same-reference-other-versions",
    #: A genuinely new document under a new handle, reaching the same conclusion.
    "new-reference",
)


def fixture_alignment_variants(*, facts) -> dict[str, tuple[Determination, ...]]:
    """One full determination set per entry in :data:`ALIGNMENT_VARIANTS`.

    Every set is the same as :func:`fixture_determinations` except for the one
    ``cross-model-alignment`` determination, so a recheck driven by any of them
    differs from the first record in exactly one evidence document — which is
    what makes what the record then says about that document a measurement
    rather than a coincidence.

    None of this has happened. ``pcert-sample`` has never had an alignment
    confirmation, never had one reversed, and never had one re-signed.
    """

    against = determined_against(facts)
    elsewhere = DeterminedAgainst(
        producing_model_key="hvac",
        producing_content_id=reissued_content_id("hvac"),
        consuming_model_key="architecture",
        consuming_content_id=against.consuming_content_id,
    )
    others = tuple(
        determination
        for determination in fixture_determinations(facts=facts)
        if determination.evidence_requirement_id != "cross-model-alignment"
    )

    def alignment(**overrides) -> Determination:
        fields = dict(
            reference=ALIGNMENT_CONFIRMED,
            evidence_requirement_id="cross-model-alignment",
            method_id="overlay-comparison",
            determiner="fixture-model-coordination",
            basis="fixture: placements overlaid in a common viewer",
            outcome="confirmed",
            subject=("hvac", "architecture"),
            determined_against=against,
        )
        fields.update(overrides)
        return Determination(**fields)

    return {
        "unchanged": (alignment(),) + others,
        "same-reference-new-conclusion": (
            alignment(
                outcome="misaligned",
                basis="fixture: overlaid again, the two models do not share a datum",
            ),
        )
        + others,
        "same-reference-new-determiner": (
            alignment(
                determiner="fixture-information-manager",
                basis="fixture: overlay repeated by a second reviewer, same conclusion",
            ),
        )
        + others,
        "same-reference-other-versions": (
            alignment(determined_against=elsewhere),
        )
        + others,
        "new-reference": (
            alignment(reference="fixture-determination/alignment/confirmed-again"),
        )
        + others,
    }


def fixture_narrowed_penetration_determinations(*, facts) -> tuple[Determination, ...]:
    """A later review that keeps the slab penetration and drops the roof one.

    The sharper half of the pair-disappearance case, and the reason it is a
    fixture of its own: the chimney is **still penetrating**, still refines, and
    still reaches a pair verdict. Only the roof counterpart is gone. A comparison
    that asked "is the penetrating element still a subject?" would answer yes and
    lose the roof pair without a word — which is precisely the silent loss the
    cross-record disposition exists to catch, arriving in the one shape where the
    element itself gives no hint that anything went missing.
    """

    against = determined_against(facts)
    kept = tuple(
        determination
        for determination in fixture_determinations(facts=facts)
        if determination.reference
        not in {
            "fixture-determination/penetration/chimney-slab-and-roof",
            "fixture-determination/opening/chimney-roof-not-modelled",
        }
    )
    return kept + (
        Determination(
            reference="fixture-determination/penetration/chimney-slab-only",
            evidence_requirement_id="penetration-determination",
            method_id="coordination-review-determination",
            determiner="fixture-coordination-review",
            basis="fixture: re-reviewed, the chimney passes through the floor slab only",
            outcome="penetration-confirmed",
            subject=(HVAC_CHIMNEY,),
            penetrated_element_keys=(ARCHITECTURE_SLAB,),
            determined_against=against,
        ),
    )


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
