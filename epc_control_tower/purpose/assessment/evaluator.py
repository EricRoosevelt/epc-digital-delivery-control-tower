"""Walk a Pack's decision tree over validated facts, or refuse.

One entry point, :func:`assess_purpose`, and one claim: given a project, a Pack,
some activities, an explicitly declared assessed scope and a model-version
context, it either refuses or returns one sealed record in which every subscope
carries the whole chain from evidence, through a verdict, to a
``resolution_kind``, to the route that kind resolves through — consequence kinds,
default role, next action, recheck condition — and to the team this project
staffs that role with.

**It is not a pipeline component.** Not a ``Checker``, not a ``GroupingPolicy``,
not an ``Exporter``; absent from ``default_registry``; never invoked by ``epc-ct
run``. It writes no file at all — where a record is stored is a later decision,
and the record is returned rather than persisted so that this module has no way
to move a published byte even by accident.

Three things it deliberately cannot do:

* **It cannot roll a partition up.** A requested scope whose evidence disagrees
  has no single verdict, only the ordered partition. The chimney splitting away
  from the three ``FAIL`` elements is the mechanism working, not a defect to be
  smoothed over.
* **It cannot promote a ``CONDITIONAL``.** A promotion needs a named authoriser
  accepting a named risk, which no evidence outcome encodes; it is out of this
  checkpoint's scope and there is no field for it here.
* **It cannot compute a magnitude.** Routes name consequence *kinds*. The
  project's milestone dates are cited verbatim on the record's provenance and
  are never parsed, subtracted, or compared with a handover date.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..errors import PurposeAssessmentError
from ..model import Activity, ComposedPurposeInputs, EvidenceRequirement, PurposePack
from .determinations import Determination, DeterminationLedger
from .facts import AssessmentFacts
from .reading import (
    VALIDATION_BACKED_OUTCOMES,
    bound_requirement_keys,
    finding_backed_reading,
    insufficient_evidence_context,
    unresolved_outcome,
)
from .record import (
    ActivityResult,
    AssessmentRecord,
    OutOfClassKey,
    PathStep,
    Reading,
    ResolvedRoute,
    ResolvingAssignment,
    Subject,
    SubscopeResult,
    build_assessment_digest,
    resolved_document,
)
from .request import AssessmentRequest

__all__ = ["assess_purpose"]

#: The ``decision_basis`` a policy row must carry before this assessment will
#: found an assignment on it. See :func:`_check_policy_can_found_an_assignment`.
PROJECT_DECISION = "project-decision"

#: No determination was offered for this subject at all. Distinct from the
#: reason string a *declined* determination leaves, because "nobody determined
#: anything" and "somebody did and it was not admissible" are different facts
#: and only one of them names a document a reader could go and look at.
NO_DETERMINATION_ABSENCE = "no-determination"


def _refuse(code: str, message: str) -> None:
    raise PurposeAssessmentError(code, message)


def assess_purpose(
    *,
    request: AssessmentRequest,
    composed: ComposedPurposeInputs,
    facts: AssessmentFacts,
    determinations: Sequence[Determination] = (),
) -> AssessmentRecord:
    """Assess one request against one composed configuration, or refuse.

    ``determinations`` are offered by reference and are admitted or declined
    (see :mod:`.determinations`); none is ever derived here. Offering none is
    normal and is not an error — it produces ``not-yet-*`` readings and
    ``UNKNOWN`` leaves, which is a fact about this assessment rather than a
    defect in it.
    """

    pack = _resolve_pack(request, composed)
    activities = _resolve_activities(request, pack)
    _check_model_version_context(request, facts)
    scope_keys = _resolve_scope(request, facts)
    _check_bindings_match_the_cited_run(pack, composed, facts)
    _check_policy_can_found_an_assignment(pack, activities, composed)

    ledger = DeterminationLedger(
        determinations,
        accepted_method_ids=_accepted_method_ids(composed, pack.pack_id),
        consuming_element_keys=frozenset(
            item.element_key
            for item in facts.elements_of(request.model_version_context.consuming.model_key)
        ),
    )

    results = tuple(
        _assess_activity(
            pack=pack,
            activity=activity,
            composed=composed,
            facts=facts,
            scope_keys=scope_keys,
            ledger=ledger,
            request=request,
        )
        for activity in activities
    )

    # Sealing. The digest is computed over the resolved content *before* the
    # record exists, so the record is constructed exactly once, already sealed —
    # rather than built, hashed, and rebuilt, which would make "sealed when the
    # digest is computed" something a reader has to take on trust. The document
    # carries no digest field, so nothing here is an input to the value that
    # names it, and a record edited afterwards no longer hashes to what it says.
    fields = dict(
        request=request,
        pack_schema_version=pack.pack_schema_version,
        composition_digest=composed.composition_digest,
        validation_run_id=facts.validation_run_id,
        ruleset_id=facts.ruleset_id,
        ruleset_version=facts.ruleset_version,
        activities=results,
        cited_milestones=facts.milestones,
        cited_cost_parameter_names=tuple(sorted(composed.overlay.cost_parameters)),
    )
    return AssessmentRecord(
        **fields,
        assessment_digest=build_assessment_digest(resolved_document(**fields)),
    )


# ---------------------------------------------------------------------------
# Preconditions — ADR 0003 §7.1, every one a refusal and never a default
# ---------------------------------------------------------------------------


def _resolve_pack(
    request: AssessmentRequest, composed: ComposedPurposeInputs
) -> PurposePack:
    if composed.project_id != request.project_id:
        _refuse(
            "request-project-mismatch",
            f"the request names project {request.project_id!r} and the composed inputs "
            f"are for {composed.project_id!r}",
        )
    try:
        pack = composed.pack(request.pack_id)
    except KeyError:
        _refuse(
            "request-pack-not-bound",
            f"the request names pack_id {request.pack_id!r}, which this project's "
            "overlay.packs does not list; there is no other Pack to fall back to",
        )
        raise AssertionError("unreachable")
    if pack.pack_version != request.pack_version:
        _refuse(
            "request-pack-version-mismatch",
            f"the request pins {request.pack_id!r} at pack_version "
            f"{request.pack_version!r} and the composed Pack declares "
            f"{pack.pack_version!r}; the match is exact and never a range",
        )
    if request.direction_id not in {item.direction_id for item in pack.directions}:
        _refuse(
            "request-direction-unresolved",
            f"the request names direction_id {request.direction_id!r}, which "
            f"{pack.pack_id!r} does not declare",
        )
    return pack


def _resolve_activities(
    request: AssessmentRequest, pack: PurposePack
) -> tuple[Activity, ...]:
    if not request.activity_ids:
        _refuse(
            "request-no-activity",
            "the request names no activity, so there is nothing a verdict could be "
            "a statement about",
        )
    by_id = {activity.activity_id: activity for activity in pack.activities}
    resolved: list[Activity] = []
    for activity_id in sorted(set(request.activity_ids)):
        activity = by_id.get(activity_id)
        if activity is None:
            _refuse(
                "request-activity-unresolved",
                f"the request names activity_id {activity_id!r}, which "
                f"{pack.pack_id!r} does not declare",
            )
            raise AssertionError("unreachable")
        if activity.direction_id != request.direction_id:
            _refuse(
                "request-activity-wrong-direction",
                f"activity {activity_id!r} serves direction "
                f"{activity.direction_id!r}, and the request asks about "
                f"{request.direction_id!r}",
            )
        resolved.append(activity)
    return tuple(resolved)


def _check_model_version_context(
    request: AssessmentRequest, facts: AssessmentFacts
) -> None:
    """The cited run validated exactly the versions the context names.

    A context naming a model version the cited run did not cover has no
    validated facts the assessment may honestly attribute to it, so it refuses
    rather than assessing against whatever the run did cover.
    """

    context = request.model_version_context
    for role, version in (("producing", context.producing), ("consuming", context.consuming)):
        known = facts.model(version.model_key)
        if known is None:
            _refuse(
                "context-model-not-validated",
                f"the {role} model {version.model_key!r} was not validated by the cited "
                f"run {facts.validation_run_id!r}",
            )
            raise AssertionError("unreachable")
        if known.content_id != version.content_id:
            _refuse(
                "context-model-version-mismatch",
                f"the {role} model {version.model_key!r} is named at content "
                f"{version.content_id!r} and the cited run validated "
                f"{known.content_id!r}; a verdict is only ever true of the exact "
                "version named",
            )


def _resolve_scope(
    request: AssessmentRequest, facts: AssessmentFacts
) -> tuple[str, ...]:
    """Expand the declared scope against the producing model version.

    A ``model_key`` expands to every element of that model, including elements no
    rule ever reached — which is the whole reason coverage may not define scope.
    A declared ``element_key`` the producing model version does not contain
    refuses: a key with no ``ifc_class`` can be neither admitted nor excluded, so
    the total accounting could not be produced for it, and dropping it silently
    is the failure this scope rule exists to prevent.
    """

    producing = request.model_version_context.producing.model_key
    resolved: set[str] = set()
    for model_key in request.assessed_scope.model_keys:
        if model_key != producing:
            _refuse(
                "scope-model-not-producing",
                f"the assessed scope names model_key {model_key!r}; scope keys resolve "
                f"against the producing model version {producing!r}",
            )
        resolved.update(item.element_key for item in facts.elements_of(model_key))
    inventory = {item.element_key for item in facts.elements_of(producing)}
    for element_key in request.assessed_scope.element_keys:
        if element_key not in inventory:
            _refuse(
                "scope-element-absent",
                f"the assessed scope names element_key {element_key!r}, absent from the "
                f"producing model version {producing!r}",
            )
        resolved.add(element_key)
    if not resolved:
        _refuse(
            "scope-empty",
            "the declared assessed scope resolved to no element of the producing model "
            "version",
        )
    return tuple(sorted(resolved))


def _check_bindings_match_the_cited_run(
    pack: PurposePack, composed: ComposedPurposeInputs, facts: AssessmentFacts
) -> None:
    """Every binding is pinned to the ruleset the cited run was computed over.

    Composition already checked each binding against the ruleset that was
    *loaded*; this checks it against the ruleset the cited ``validation_run_id``
    was computed over, which is a different question and the one that decides
    whether these facts may be attributed to these bindings at all.
    """

    expected = (facts.ruleset_id, facts.ruleset_version)
    for requirement in pack.evidence_requirements:
        binding = requirement.pack_binding
        if binding is not None and (binding.ruleset_id, binding.ruleset_version) != expected:
            _refuse(
                "binding-ruleset-not-the-cited-run",
                f"{pack.pack_id}::{requirement.evidence_requirement_id} pack_binding is "
                f"pinned to {binding.ruleset_id} {binding.ruleset_version} and the cited "
                f"run validated {expected[0]} {expected[1]}",
            )
        for reference in requirement.insufficient_evidence:
            if (reference.ruleset_id, reference.ruleset_version) != expected:
                _refuse(
                    "insufficient-evidence-ruleset-not-the-cited-run",
                    f"{pack.pack_id}::{requirement.evidence_requirement_id} "
                    f"insufficient_evidence is pinned to {reference.ruleset_id} "
                    f"{reference.ruleset_version} and the cited run validated "
                    f"{expected[0]} {expected[1]}",
                )
    for row in composed.overlay.evidence_bindings:
        if row.pack_id != pack.pack_id:
            continue
        if (row.ruleset_id, row.ruleset_version) != expected:
            _refuse(
                "binding-ruleset-not-the-cited-run",
                f"{row.pack_id}::{row.evidence_requirement_id} evidence_binding is pinned "
                f"to {row.ruleset_id} {row.ruleset_version} and the cited run validated "
                f"{expected[0]} {expected[1]}",
            )


def _reachable_non_ready_leaves(
    pack: PurposePack, activity: Activity
) -> tuple[tuple[str, str], ...]:
    """``(node_id, resolution_kind)`` for every non-READY leaf this tree can reach.

    Structural, over the tree, not over the evidence — the same reading ADR 0003
    §7.1 gives "a requested activity has a *reachable* non-``READY`` leaf". A
    policy defect is a property of the request, so it is found before any
    subscope is assessed rather than discovered halfway through one.
    """

    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    frontier = [activity.decision_root_node]
    while frontier:
        node_id = frontier.pop()
        if node_id in seen:
            continue
        seen.add(node_id)
        for branch in pack.node(node_id).branches:
            if branch.is_leaf:
                if branch.resolution_kind:
                    found.append((node_id, branch.resolution_kind))
            elif branch.next_node:
                frontier.append(branch.next_node)
    return tuple(sorted(set(found)))


def _check_policy_can_found_an_assignment(
    pack: PurposePack, activities: Sequence[Activity], composed: ComposedPurposeInputs
) -> None:
    """Every reachable non-READY leaf resolves to a staffing decision this project took.

    ADR 0003 §4.3 requires a resolving assignment on every non-``READY`` subscope
    and forbids recording the bare ``default_role`` as though it were an
    assignee. Composition already refuses when no ``team_mapping`` row names the
    role at all. This adds the question composition cannot ask, because it is
    about what a record would *claim*: a row whose ``decision_basis`` is
    ``illustrative`` states the shape of a staffing decision, not one anybody
    took, so founding a real project's assignment on it would publish an
    assignment nobody made.

    ``pcert-sample`` is the worked case and its refusal is the correct result,
    not a gap: all four of its ``team_mapping`` rows are ``illustrative``, so
    every leaf these activities can reach lands on a demonstration row. The
    diagnostic names those rows, because "policy is illustrative" without saying
    which rows would leave a maintainer guessing at which four lines to change.
    """

    rows = {row.role: row for row in composed.overlay.team_mapping}
    blocked: dict[str, list[str]] = {}
    unmapped: list[str] = []
    for activity in activities:
        for node_id, resolution_kind in _reachable_non_ready_leaves(pack, activity):
            role = pack.route(resolution_kind).default_role
            row = rows.get(role)
            if row is None:
                unmapped.append(
                    f"{pack.pack_id}::{activity.activity_id} node {node_id} "
                    f"-> {resolution_kind} -> default_role {role!r}"
                )
                continue
            if row.decision_basis != PROJECT_DECISION:
                blocked.setdefault(role, []).append(
                    f"{pack.pack_id}::{activity.activity_id} node {node_id} "
                    f"-> {resolution_kind}"
                )

    if unmapped:
        _refuse(
            "team-mapping-role-missing",
            "no overlay.team_mapping row staffs the default_role of: "
            + "; ".join(sorted(unmapped))
            + ". This is never resolved by reading the bound rule's owner_role, and "
            "the bare default_role string is never recorded as an assignee",
        )
    if blocked:
        lines = []
        for role in sorted(blocked):
            row = rows[role]
            routes = "; ".join(sorted(blocked[role]))
            # ASCII only, and deliberately: this is the message a maintainer
            # reads on a Windows console, where a stray em dash arrives as a
            # replacement character and makes the line look corrupted.
            lines.append(
                f"  overlay.team_mapping role={row.role!r} "
                f"team_or_person={row.team_or_person!r} "
                f"decision_basis={row.decision_basis!r} "
                f"would found the assignment for: {routes}"
            )
        _refuse(
            "team-mapping-decision-basis-illustrative",
            f"project {composed.project_id!r} cannot produce an assessment record for "
            f"pack {pack.pack_id!r}: every non-READY leaf the requested activities can "
            "reach resolves to a default_role staffed only by a team_mapping row whose "
            f"decision_basis is not {PROJECT_DECISION!r}. An assignment founded on a "
            "demonstration row would claim a staffing decision this project never took. "
            f"The {len(lines)} blocking row(s):\n" + "\n".join(lines),
        )


def _accepted_method_ids(
    composed: ComposedPurposeInputs, pack_id: str
) -> dict[str, frozenset[str]]:
    accepted: dict[str, set[str]] = {}
    for method in composed.overlay.accepted_evidence_methods:
        if method.pack_id != pack_id:
            continue
        accepted.setdefault(method.evidence_requirement_id, set()).add(method.method_id)
    return {key: frozenset(value) for key, value in accepted.items()}


# ---------------------------------------------------------------------------
# One activity: admit subjects, walk, partition
# ---------------------------------------------------------------------------


def _assess_activity(
    *,
    pack: PurposePack,
    activity: Activity,
    composed: ComposedPurposeInputs,
    facts: AssessmentFacts,
    scope_keys: Sequence[str],
    ledger: DeterminationLedger,
    request: AssessmentRequest,
) -> ActivityResult:
    """Admit this activity's subjects by class, then partition them by outcome.

    Admission reads ``ifc_class`` and only ``ifc_class``: never a finding, never
    a binding, never an applicability set. That is why an ``IfcChimney`` with
    zero findings is admitted and reaches ``not-yet-evaluated``, while an
    ``IfcBuildingElementProxy`` setout marker with zero findings is excluded —
    two elements with identical coverage, separated by what they *are*.
    """

    declared = set(activity.subject_classes)
    admitted: list[str] = []
    out_of_class: list[OutOfClassKey] = []
    for element_key in sorted(scope_keys):
        element = facts.element(element_key)
        if element is None:  # pragma: no cover - _resolve_scope refuses first
            raise AssertionError(f"unresolved scope key {element_key!r}")
        if element.ifc_class in declared:
            admitted.append(element_key)
        else:
            out_of_class.append(
                OutOfClassKey(element_key=element_key, ifc_class=element.ifc_class)
            )

    subscopes: tuple[SubscopeResult, ...] = ()
    if admitted:
        parts = _walk(
            pack=pack,
            composed=composed,
            facts=facts,
            ledger=ledger,
            request=request,
            node_id=activity.decision_root_node,
            subjects=tuple(Subject(keys=(key,)) for key in admitted),
            path=(),
        )
        subscopes = _order(parts, pack=pack, composed=composed)

    return ActivityResult(
        activity_ref=f"{pack.pack_id}::{activity.activity_id}",
        subject_classes=tuple(activity.subject_classes),
        admitted_subjects=tuple(admitted),
        subscopes=subscopes,
        out_of_subject_class=tuple(out_of_class),
    )


def _walk(
    *,
    pack: PurposePack,
    composed: ComposedPurposeInputs,
    facts: AssessmentFacts,
    ledger: DeterminationLedger,
    request: AssessmentRequest,
    node_id: str,
    subjects: tuple[Subject, ...],
    path: tuple[PathStep, ...],
) -> list[tuple[tuple[Subject, ...], tuple[PathStep, ...], str, str]]:
    """Carry one subgroup down the tree, splitting only where it disagrees.

    Splitting is incremental. A subgroup splits at the node that actually
    distinguishes its subjects, into the outcomes actually seen there — never by
    an up-front cross-product, which would manufacture parts the tree can never
    reach, such as an opening's cross-reference status for an element that
    penetrates nothing.

    Returns ``(members, path, verdict, resolution_kind)`` per terminal leaf.
    """

    node = pack.node(node_id)
    requirement = pack.evidence_requirement(node.evidence_requirement_id)
    grain = requirement.subject_grain

    if grain == "per-subject-pair":
        subjects = _refine(requirement, subjects, ledger)
        if not subjects:
            # Unreachable while the admissibility rule holds: this branch is taken
            # only by subjects whose pair_source determination was admitted, and a
            # determination naming no counterpart is inadmissible. Refusing rather
            # than returning nothing keeps that a checked fact — dropping the
            # subgroup here would break the total accounting silently.
            _refuse(
                "pair-refinement-produced-no-subject",
                f"node {node_id!r} refined {len(subjects)} subject(s) into no pair; an "
                "admitted pair_source determination always names at least one counterpart",
            )

    readings = _read(
        requirement=requirement,
        subjects=subjects,
        pack=pack,
        composed=composed,
        facts=facts,
        ledger=ledger,
        request=request,
        grain=grain,
    )
    context = insufficient_evidence_context(requirement, facts)

    by_outcome: dict[str, list[Reading]] = {}
    for reading in readings:
        by_outcome.setdefault(reading.outcome, []).append(reading)

    branches = {branch.outcome: branch for branch in node.branches}
    results: list[tuple[tuple[Subject, ...], tuple[PathStep, ...], str, str]] = []
    for outcome in sorted(by_outcome):
        branch = branches.get(outcome)
        if branch is None:
            _refuse(
                "node-outcome-uncovered",
                f"node {node_id!r} has no branch for outcome {outcome!r}; the Pack "
                "loader's exhaustiveness invariant should have caught this",
            )
            raise AssertionError("unreachable")
        group = by_outcome[outcome]
        members = tuple(sorted((item.subject for item in group), key=lambda s: s.sort_key))
        if grain == "whole-scope":
            members = subjects
        step = PathStep(
            node_id=node_id,
            evidence_requirement_id=requirement.evidence_requirement_id,
            grain=grain,
            outcome=outcome,
            readings=tuple(sorted(group, key=lambda item: item.subject.sort_key)),
            context_citations=context,
        )
        extended = path + (step,)
        if branch.is_leaf:
            results.append((members, extended, branch.verdict, branch.resolution_kind))
        else:
            results.extend(
                _walk(
                    pack=pack,
                    composed=composed,
                    facts=facts,
                    ledger=ledger,
                    request=request,
                    node_id=branch.next_node,
                    subjects=members,
                    path=extended,
                )
            )
    return results


def _refine(
    requirement: EvidenceRequirement,
    subjects: tuple[Subject, ...],
    ledger: DeterminationLedger,
) -> tuple[Subject, ...]:
    """Replace each subject with one pair per counterpart its determination named.

    Refinement changes the grain of the carrier and nothing else: it adds no
    element to the assessed scope, removes none, and every refined subject
    records the admitted ``element_key`` it came from. One chimney through a
    floor slab and then the roof becomes two pairs, which is why its slab opening
    and its roof opening can reach two different verdicts instead of collapsing
    into one.
    """

    source = requirement.pair_source
    if source is None:  # pragma: no cover - the Pack loader guarantees it
        raise ValueError(
            f"{requirement.evidence_requirement_id}: per-subject-pair with no pair_source"
        )
    refined: list[Subject] = []
    for subject in subjects:
        origin = subject.keys[0]
        for counterpart in ledger.counterparts(
            source_evidence_requirement_id=source.from_evidence_requirement_id,
            on_outcome=source.on_outcome,
            element_key=origin,
        ):
            refined.append(Subject(keys=(origin, counterpart), refined_from=origin))
    return tuple(sorted(refined, key=lambda item: item.sort_key))


def _read(
    *,
    requirement: EvidenceRequirement,
    subjects: tuple[Subject, ...],
    pack: PurposePack,
    composed: ComposedPurposeInputs,
    facts: AssessmentFacts,
    ledger: DeterminationLedger,
    request: AssessmentRequest,
    grain: str,
) -> tuple[Reading, ...]:
    """One reading per subject, or the single reading a whole-scope node shares."""

    if grain == "whole-scope":
        context = request.model_version_context
        model_pair = Subject(
            keys=(context.producing.model_key, context.consuming.model_key)
        )
        return (_determination_reading(requirement, model_pair, ledger),)

    if requirement.binding_source == "assessment":
        return tuple(
            _determination_reading(requirement, subject, ledger) for subject in subjects
        )

    keys, label = bound_requirement_keys(requirement, composed.overlay, pack.pack_id)
    _check_validation_backed_vocabulary(requirement)
    readings: list[Reading] = []
    for subject in subjects:
        outcome, finding_keys, absence = finding_backed_reading(
            element_key=subject.keys[0], requirement_keys=keys, facts=facts
        )
        readings.append(
            Reading(
                subject=subject,
                outcome=outcome,
                binding=label,
                finding_keys=finding_keys,
                absence=absence,
            )
        )
    return tuple(readings)


def _check_validation_backed_vocabulary(requirement: EvidenceRequirement) -> None:
    """A finding-backed requirement declares the three names ADR 0002 §3.2 fixes.

    Refuses rather than mapping ``PASS`` onto whatever the Pack happens to have
    listed first. The reduction has three levels and needs three names for them;
    a Pack that gives it two would have to be guessed at.
    """

    missing = sorted(set(VALIDATION_BACKED_OUTCOMES) - set(requirement.outcomes))
    if missing:
        _refuse(
            "validation-backed-outcomes-incomplete",
            f"{requirement.evidence_requirement_id} is finding-backed and its outcomes "
            f"{list(requirement.outcomes)} omit {missing}; the FAIL > not-covered > PASS "
            "reduction has no name to reduce to",
        )


def _determination_reading(
    requirement: EvidenceRequirement,
    subject: Subject,
    ledger: DeterminationLedger,
) -> Reading:
    """Read one recorded determination, or the requirement's absent outcome.

    The assessment adjudicates nothing. A determination is admitted and its
    outcome read, or it is declined and the subject reads ``not-yet-*`` — and a
    declined determination is recorded with the reason it was declined, so it
    never looks like a subject nobody determined anything about.
    """

    determination, declined = ledger.resolve(requirement, subject.keys)
    if determination is None:
        return Reading(
            subject=subject,
            outcome=unresolved_outcome(requirement),
            absence=declined or NO_DETERMINATION_ABSENCE,
        )
    return Reading(
        subject=subject,
        outcome=determination.outcome,
        binding=determination.method_id,
        determination_reference=determination.reference,
    )


def _order(
    parts: Sequence[tuple[tuple[Subject, ...], tuple[PathStep, ...], str, str]],
    *,
    pack: PurposePack,
    composed: ComposedPurposeInputs,
) -> tuple[SubscopeResult, ...]:
    """Canonically order the partition and hang a route and an assignment on it.

    Ordered by the root-to-leaf outcome sequence, then by the smallest member
    subject key — both totally ordered frozen strings, so the ordinal is stable
    across runs, machines and operating systems with no clock and no set
    iteration.
    """

    ordered = sorted(
        parts,
        key=lambda part: (
            tuple(step.outcome for step in part[1]),
            min(subject.sort_key for subject in part[0]) if part[0] else (),
        ),
    )
    rows = {row.role: row for row in composed.overlay.team_mapping}
    results: list[SubscopeResult] = []
    for ordinal, (members, path, verdict, resolution_kind) in enumerate(ordered, start=1):
        route = None
        assignment = None
        if verdict != "READY":
            declared = pack.route(resolution_kind)
            route = ResolvedRoute(
                resolution_kind=declared.resolution_kind,
                consequence_kinds=tuple(declared.consequence_kinds),
                default_role=declared.default_role,
                next_action=declared.next_action,
                recheck_condition=declared.recheck_condition,
            )
            row = rows[declared.default_role]
            assignment = ResolvingAssignment(
                default_role=declared.default_role,
                assigned_team_or_person=row.team_or_person,
                decision_basis=row.decision_basis,
            )
        results.append(
            SubscopeResult(
                ordinal=ordinal,
                members=members,
                path=path,
                verdict=verdict,
                resolution_kind=resolution_kind,
                route=route,
                assignment=assignment,
            )
        )
    return tuple(results)
