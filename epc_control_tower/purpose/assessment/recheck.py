"""Succeed a sealed record: is that blockage cleared, and how do we know?

One entry point, :func:`recheck_purpose`, and one claim. Given a sealed
:class:`~.record.AssessmentRecord` and the subscopes of it a production owner
cares about, it re-derives the whole assessment from *current* evidence and
returns a **new** sealed record that says, for each cited subscope, three things
that are not the same thing:

1. **Where its members are now** — present and at which verdict, or gone and
   under which of four named classifications.
2. **Which of its evidence citations still carry** — and when one does not,
   whether that is because the model-version context moved or because something
   superseded it.
3. **What could be established about its ``recheck_condition``** — and, far more
   often than not, that nothing could be, because the sentence is prose written
   for people and this module does not adjudicate prose.

The prior record is opened, verified against its own digest, and read. It is
never rewritten, appended to, corrected, or deleted (ADR 0003 §4.5). Half the
value of a recheck is that *what we knew at the time* stays readable.

Four things this module deliberately cannot do
----------------------------------------------

**It cannot decide a recheck condition.** Three of this Pack's ten conditions
name exactly one outcome out of their own evidence requirement's declared
vocabulary, and for those the module compares a value. The other seven are
sentences, and for those it records ``no-machine-checkable-part`` and stops.
Judgement re-enters where every other judgement in this design enters: through a
determination, admitted or declined by :mod:`.determinations`, with a determiner
and a cited basis. There is no second, easier route.

**It cannot carry an old determination forward.** A determination is admissible
only for the model versions it names, and :meth:`DeterminationLedger.validate`
refuses one attributed elsewhere. A recheck across a re-issue therefore reads no
determination that the prior record read, and the retreat that follows is the
correct answer rather than a bug to be smoothed over. What this module adds is
that the retreat is *explained*: the record says the prior citations did not
carry because the context moved, instead of showing a bare ``UNKNOWN``.

**It cannot read a disappearance as a fix.** A member that is gone is classified
— deleted from the re-issued model, excluded by a changed ``ifc_class``, a pair
the current determination no longer names, or a key this request's own scope no
longer declares — and none of those four is ``resolved``. Whenever any member is
gone the condition status is ``not-comparable``, computed *before* the condition
is looked at, because "every element in the assessed scope is covered" goes
literally true the moment the uncovered element stops being in the set.

**It cannot compute a magnitude, and it never sees a severity.** It reads the
same :class:`~.facts.AssessmentFacts` projection as the evaluator, which has no
field for ``severity``, ``priority``, ``is_issue``, ``stage`` or ``owner_role``,
and it parses no date. R-005 is still ``WARNING`` and the verdict is still
``BLOCKED``; a milestone is still cited and never subtracted.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from ..errors import PurposeAssessmentError
from ..model import ComposedPurposeInputs, EvidenceRequirement, PurposePack
from .determinations import Determination
from .evaluator import derive_assessment
from .facts import AssessmentFacts
from .record import (
    ActivityResult,
    AssessmentRecord,
    ContextComparison,
    EvidenceCarryOver,
    MemberDisposition,
    RecheckOutcome,
    Subject,
    SubscopeResult,
    SuccessorSection,
    build_assessment_digest,
    resolved_document,
)
from .request import AssessmentRequest

__all__ = ["machine_checkable_outcome", "recheck_purpose"]

#: A maximal run of the characters a Pack's outcome names are built from. Used
#: to split a ``recheck_condition`` into whole tokens, so that
#: ``alignment-confirmation`` is one token and never matches the outcome
#: ``confirmed``, and ``opening-cross-reference-check`` never matches
#: ``cross-referenced``.
_TOKEN = re.compile(r"[A-Za-z0-9-]+")


def _refuse(code: str, message: str) -> None:
    raise PurposeAssessmentError(code, message)


def machine_checkable_outcome(
    condition: str, requirement: EvidenceRequirement
) -> str:
    """The one declared outcome a ``recheck_condition`` names, or ``""``.

    **This is a membership test over a closed vocabulary, not comprehension of
    prose.** The requirement's own ``outcomes[]`` is a short, Pack-declared list
    of frozen strings; the condition is split into whole tokens and intersected
    with it. Nothing else about the sentence is read, and the caller is told so
    by the status name it gets back: ``named-outcome-observed`` says the named
    outcome is what the members read, and claims nothing about the rest of the
    sentence.

    Zero matches or several both return ``""`` and the condition is recorded as
    having no machine-checkable part. Several is the important one: picking among
    them would be the evaluator deciding which half of a Pack author's sentence
    it meant, and the value it picked would be a verdict.

    In the shipped Pack exactly three of ten conditions resolve here —
    ``missing-corresponding-opening`` and ``opening-not-verifiably-linked`` to
    ``cross-referenced``, ``cross-model-misalignment`` to ``confirmed``. The
    other seven are universally quantified sentences about coverage, or name a
    disjunction of three outcomes, and all seven stay for a person to read.
    """

    tokens = set(_TOKEN.findall(condition))
    named = sorted(tokens & set(requirement.outcomes))
    return named[0] if len(named) == 1 else ""


def recheck_purpose(
    *,
    prior: AssessmentRecord,
    request: AssessmentRequest,
    composed: ComposedPurposeInputs,
    facts: AssessmentFacts,
    determinations: Sequence[Determination] = (),
    succeeds: Sequence[tuple[str, int]],
) -> AssessmentRecord:
    """Re-derive the assessment and record what became of the cited subscopes.

    ``succeeds`` names the sealed subscopes this record answers for, as
    ``(activity_ref, ordinal)`` pairs. The ordinal is a within-record handle and
    nothing more (ADR 0003 §3.3): it identifies *which* sealed subscope, and the
    comparison that follows runs over that subscope's recorded **members**, never
    over the ordinal and never over the outcome path — a partition is re-derived
    per record and its ordinals are not stable across records.

    ``determinations`` are the ones offered for *this* request's model versions.
    Handing over the prior record's determinations under a moved context does not
    work and is not meant to: :meth:`.DeterminationLedger.validate` refuses them,
    by the same rule that has always refused evidence attributed elsewhere.
    """

    _check_prior_is_sealed(prior)
    _check_same_question(prior, request)
    pack, fields = derive_assessment(
        request=request,
        composed=composed,
        facts=facts,
        determinations=determinations,
    )
    _check_pack_version_is_unmoved(prior, pack)

    activities: tuple[ActivityResult, ...] = fields["activities"]
    by_ref = {activity.activity_ref: activity for activity in activities}
    context = _compare_contexts(prior, request)

    cited = sorted(set(succeeds))
    if not cited:
        _refuse(
            "recheck-cites-no-subscope",
            "a recheck answers for named sealed subscopes and this one names none; "
            "there is nothing for its conclusions to be about",
        )
    outcomes = tuple(
        _recheck_one(
            prior=prior,
            pack=pack,
            activity_ref=activity_ref,
            ordinal=ordinal,
            current=by_ref,
            context=context,
            facts=facts,
        )
        for activity_ref, ordinal in cited
    )

    fields["successor"] = SuccessorSection(
        kind="recheck",
        prior_assessment_digest=prior.assessment_digest,
        context=context,
        outcomes=outcomes,
    )
    # Sealed exactly the way an originating record is, and by the same call: the
    # comparison is part of the hashed content, so a record that says a blockage
    # cleared and one that says it did not can never share a digest.
    return AssessmentRecord(
        **fields,
        assessment_digest=build_assessment_digest(resolved_document(**fields)),
    )


# ---------------------------------------------------------------------------
# Preconditions — every one a refusal, and none of them a default
# ---------------------------------------------------------------------------


def _check_prior_is_sealed(prior: AssessmentRecord) -> None:
    """The prior record still hashes to the digest it carries.

    Cheap, and the only thing that makes "sealed" a checked property rather than
    a promise. A successor built on a record whose content has moved would cite a
    digest that names something else, and every reference to it downstream would
    be pointing at content nobody can reproduce.
    """

    recomputed = build_assessment_digest(prior.as_document())
    if recomputed != prior.assessment_digest:
        _refuse(
            "recheck-prior-record-seal-broken",
            f"the prior record carries assessment_digest {prior.assessment_digest!r} "
            f"and its own content hashes to {recomputed!r}; a sealed record is never "
            "rewritten, and a successor will not be founded on one that was",
        )


def _check_same_question(prior: AssessmentRecord, request: AssessmentRequest) -> None:
    """A recheck asks the prior record's question again, of newer evidence.

    Project, Pack and direction are the question. A request that moved any of
    them is a different question, and answering it while citing the prior record's
    subscope ordinals would attach conclusions to a sealed record that was never
    about them.
    """

    for label, before, now in (
        ("project_id", prior.request.project_id, request.project_id),
        ("pack_id", prior.request.pack_id, request.pack_id),
        ("direction_id", prior.request.direction_id, request.direction_id),
    ):
        if before != now:
            _refuse(
                "recheck-not-the-same-question",
                f"the prior record's {label} is {before!r} and this request's is "
                f"{now!r}; a recheck re-asks the prior question of newer evidence, and "
                "a different question is a new assessment rather than a successor",
            )


def _check_pack_version_is_unmoved(prior: AssessmentRecord, pack: PurposePack) -> None:
    """The Pack semantics behind the cited conditions have not been renegotiated.

    A ``pack_version`` move may change what a ``resolution_kind`` resolves to —
    different consequence kinds, a different next action, a different
    ``recheck_condition`` — and may change an evidence requirement's declared
    ``outcomes[]``, which is the vocabulary the condition comparison is a
    membership test against. Comparing a sealed condition to a re-derived reading
    across that move would be comparing two different sentences and reporting one
    answer, so this refuses instead. The same reasoning already stands behind
    §4.5's check 6 for a continued promotion.
    """

    if prior.request.pack_version != pack.pack_version:
        _refuse(
            "recheck-pack-version-moved",
            f"the prior record was assessed against pack_version "
            f"{prior.request.pack_version!r} and this one composes "
            f"{pack.pack_version!r}; the routes, the recheck conditions and the "
            "declared outcome vocabularies may all differ across that move, so the "
            "comparison would be between two different sentences",
        )


def _prior_subscope(
    prior: AssessmentRecord, activity_ref: str, ordinal: int
) -> tuple[ActivityResult, SubscopeResult]:
    for activity in prior.activities:
        if activity.activity_ref != activity_ref:
            continue
        for subscope in activity.subscopes:
            if subscope.ordinal == ordinal:
                return activity, subscope
        _refuse(
            "recheck-subscope-unresolved",
            f"the prior record's {activity_ref!r} has no subscope with ordinal "
            f"{ordinal}; it carries "
            f"{[item.ordinal for item in activity.subscopes]}",
        )
    _refuse(
        "recheck-activity-unresolved",
        f"the prior record carries no activity {activity_ref!r}; it carries "
        f"{[item.activity_ref for item in prior.activities]}",
    )
    raise AssertionError("unreachable")


def _compare_contexts(
    prior: AssessmentRecord, request: AssessmentRequest
) -> ContextComparison:
    """Both model versions, before and after, as values.

    ADR 0003 §2.3's comparison, and nothing more: no clock is read, no ordering
    of the two contexts is inferred, and neither is called the later one. A
    re-issue is recorded as *different*, which is the only thing content
    identifiers can honestly say.
    """

    before = prior.request.model_version_context
    now = request.model_version_context
    return ContextComparison(
        prior_producing=(before.producing.model_key, before.producing.content_id),
        producing=(now.producing.model_key, now.producing.content_id),
        prior_consuming=(before.consuming.model_key, before.consuming.content_id),
        consuming=(now.consuming.model_key, now.consuming.content_id),
    )


# ---------------------------------------------------------------------------
# One cited subscope
# ---------------------------------------------------------------------------


def _recheck_one(
    *,
    prior: AssessmentRecord,
    pack: PurposePack,
    activity_ref: str,
    ordinal: int,
    current: dict[str, ActivityResult],
    context: ContextComparison,
    facts: AssessmentFacts,
) -> RecheckOutcome:
    """Compare one sealed subscope with the partition this record derived.

    Member by member, never ordinal by ordinal and never path by path. An ordinal
    identifies the sealed subscope being answered for and stops there; the
    partition is re-derived per record, so the same ordinal in two records is not
    a claim about the same set, and the outcome path is what the comparison is
    *about* rather than a key it could be matched on.
    """

    prior_activity, subscope = _prior_subscope(prior, activity_ref, ordinal)
    activity = current.get(activity_ref)
    if activity is None:
        _refuse(
            "recheck-activity-not-requested",
            f"this request does not ask about {activity_ref!r}, so nothing was "
            "re-derived for the subscope it cites; a recheck that assesses nothing "
            "reports nothing",
        )
        raise AssertionError("unreachable")

    leaf_requirement_id = (
        subscope.path[-1].evidence_requirement_id if subscope.path else ""
    )
    dispositions = tuple(
        _dispose(
            member=member,
            activity=activity,
            prior_activity=prior_activity,
            facts=facts,
            leaf_requirement_id=leaf_requirement_id,
        )
        for member in subscope.members
    )
    carry_over = _carry_over(subscope, activity, context, facts)
    condition = (
        subscope.route.recheck_condition if subscope.route is not None else ""
    )
    named, status, basis = _condition_status(
        condition=condition,
        leaf_requirement_id=leaf_requirement_id,
        dispositions=dispositions,
        pack=pack,
    )
    return RecheckOutcome(
        activity_ref=activity_ref,
        subscope_ordinal=ordinal,
        prior_verdict=subscope.verdict,
        prior_resolution_kind=subscope.resolution_kind,
        prior_recheck_condition=condition,
        prior_leaf_evidence_requirement_id=leaf_requirement_id,
        prior_members=subscope.members,
        dispositions=dispositions,
        carry_over=carry_over,
        correspondence=(
            "complete"
            if all(item.disposition == "present" for item in dispositions)
            else "incomplete"
        ),
        named_outcome=named,
        condition_status=status,
        condition_basis=basis,
    )


def _dispose(
    *,
    member: Subject,
    activity: ActivityResult,
    prior_activity: ActivityResult,
    facts: AssessmentFacts,
    leaf_requirement_id: str,
) -> MemberDisposition:
    """Classify one sealed member against this record's partition.

    The order is fixed and total, and it is the order it is because each test
    presupposes the ones above it. A key that is not in the inventory has no
    ``ifc_class`` to exclude it; a key outside the declared scope was never
    offered to class admission; a pair can only have stopped being derived if its
    penetrating element is still admitted.

    Nothing here can return "resolved". The nearest thing to good news it can
    report is ``present``, and what is good about that has to be read off the
    verdict the member now reaches — which is recorded beside it, as a separate
    field, for exactly that reason.
    """

    origin = member.refined_from or member.keys[0]

    landings = _landings(member, activity, leaf_requirement_id)
    if landings:
        ordinals, verdicts, outcomes = zip(*landings, strict=True)
        return MemberDisposition(
            member=member,
            disposition="present",
            current_ordinals=tuple(ordinals),
            current_verdicts=tuple(verdicts),
            current_leaf_outcomes=tuple(outcomes),
        )

    element = facts.element(origin)
    if element is None:
        return MemberDisposition(
            member=member,
            disposition="element-deleted-in-reissued-model",
            cause=(
                f"{origin} is absent from the element inventory of the producing "
                "model version this record was assessed against"
            ),
        )

    excluded = {item.element_key: item.ifc_class for item in activity.out_of_subject_class}
    if origin in excluded:
        prior_class = {
            item.element_key: item.ifc_class
            for item in prior_activity.out_of_subject_class
        }.get(origin, "")
        return MemberDisposition(
            member=member,
            disposition="element-out-of-subject-class",
            cause=(
                f"{origin} carries ifc_class {excluded[origin]!r}, which "
                f"{activity.activity_ref} does not declare in subject_classes "
                f"{list(activity.subject_classes)}"
                + (f"; the prior record excluded it as {prior_class!r}" if prior_class else "")
            ),
        )

    if origin not in activity.admitted_subjects:
        return MemberDisposition(
            member=member,
            disposition="outside-declared-scope",
            cause=(
                f"{origin} is not among the keys this request's declared assessed "
                "scope resolved to, so this activity was never offered it"
            ),
        )

    if len(member.keys) < 2:
        # Unreachable while the partition is a partition: a bare subject that is
        # admitted lands in exactly one subscope, or in the pairs it refined into,
        # and ``_landings`` finds both. Refusing rather than inventing a fifth
        # disposition keeps that a checked fact; classifying it as one of the four
        # would be reporting a cause nobody established.
        _refuse(
            "recheck-member-unaccounted",
            f"{origin} is admitted by {activity.activity_ref} and appears in none of "
            "its subscopes, so this record cannot say what became of it; the "
            "partition should account for every admitted subject",
        )
    return MemberDisposition(
        member=member,
        disposition="pairing-no-longer-derived",
        cause=_pairing_cause(member, origin, activity),
    )


def _landings(
    member: Subject, activity: ActivityResult, leaf_requirement_id: str
) -> tuple[tuple[int, str, str], ...]:
    """Where this member is in the current partition, as ``(ordinal, verdict, outcome)``.

    A member matches itself, and a bare element also matches every pair refined
    from it — so a subject the prior record carried whole and this one split into
    two pairs is ``present`` twice, with two verdicts, rather than reported gone.
    ``outcome`` is this record's reading of the *prior leaf's* evidence
    requirement, which is empty when the current path never reaches that node.
    """

    found: list[tuple[int, str, str]] = []
    for subscope in activity.subscopes:
        for candidate in subscope.members:
            same = candidate.keys == member.keys
            refined = len(member.keys) == 1 and candidate.refined_from == member.keys[0]
            if not (same or refined):
                continue
            outcome = ""
            for step in subscope.path:
                if step.evidence_requirement_id == leaf_requirement_id:
                    outcome = step.outcome
            found.append((subscope.ordinal, subscope.verdict, outcome))
            break
    return tuple(sorted(found))


def _pairing_cause(member: Subject, origin: str, activity: ActivityResult) -> str:
    """Why a pair whose penetrating element is still admitted is no longer derived.

    Quoted from this record's own readings: the current outcome of the
    ``pair_source`` requirement for the penetrating element, the named absence
    behind it when there is one, and the counterparts that *are* derived now. All
    three are values this record holds, so the explanation is evidence rather
    than a story about a document the record cannot see.

    This is the cross-record twin of the guard in
    :meth:`.DeterminationLedger.counterparts`. That one stops a declined claim
    sorting ahead of an admissible one from silently deciding the pairs *within*
    one record; it cannot see a pair that existed in an earlier record and does
    not exist here, because it never looks at an earlier record. Without this
    branch that pair would simply be absent — not reported wrongly, not reported
    at all.
    """

    still_paired = sorted(
        subject.keys[1]
        for subscope in activity.subscopes
        for subject in subscope.members
        if subject.refined_from == origin and len(subject.keys) == 2
    )
    # Every reading this record made *about the penetrating element itself*,
    # wherever it sits. Keyed on the reading's subject rather than on the
    # subscope's members, because those are two different grains: at the pair
    # node the members are pairs while the pair-source node's readings above it
    # are still keyed on the bare element, and filtering by membership would lose
    # the reading exactly when the element did stay paired with somebody else.
    readings: list[str] = []
    for subscope in activity.subscopes:
        for step in subscope.path:
            for reading in step.readings:
                if reading.subject.keys != (origin,):
                    continue
                readings.append(
                    f"{step.evidence_requirement_id} now reads "
                    f"{reading.outcome!r}"
                    + (f" ({reading.absence})" if reading.absence else "")
                )
    detail = "; ".join(sorted(set(readings))) or (
        "the penetrating element reaches no reading of the pair source"
    )
    return (
        f"the pair ({member.keys[0]}, {member.keys[1]}) is not derived from "
        f"{origin} under this record's evidence: {detail}. Counterparts derived "
        f"now: {still_paired}"
    )


def _carry_over(
    subscope: SubscopeResult,
    activity: ActivityResult,
    context: ContextComparison,
    facts: AssessmentFacts,
) -> tuple[EvidenceCarryOver, ...]:
    """Which citations of the sealed path this record still makes, and why not.

    The classification is over two facts this record holds — whether the citation
    appears in its own readings, and whether the model-version context moved — and
    it exists so that a retreat has a *reason* on the record. A subscope that fell
    back to ``UNKNOWN`` because the determinations behind it stopped being
    attributable, and one that fell back because a review reversed itself, are
    different situations for the team reading them, and a bare ``UNKNOWN`` tells
    them apart from neither.

    A ``finding_key`` is checked against the facts directly, which is the
    honest question for validation evidence: a re-validated model produces new
    finding keys, and the old ones do not survive it.
    """

    cited_now = {
        reference
        for item in activity.subscopes
        for step in item.path
        for reading in step.readings
        for reference in reading.determination_references
    }
    rows: list[EvidenceCarryOver] = []
    seen: set[tuple[str, str]] = set()
    for step in subscope.path:
        for reading in step.readings:
            for finding_key in reading.finding_keys:
                if ("finding", finding_key) in seen:
                    continue
                seen.add(("finding", finding_key))
                present = any(
                    fact.finding_key == finding_key for fact in facts.findings
                )
                rows.append(
                    EvidenceCarryOver(
                        citation=finding_key,
                        citation_kind="finding",
                        reason=(
                            "carried" if present else "finding-absent-from-the-cited-run"
                        ),
                    )
                )
            for reference in reading.determination_references:
                if ("determination", reference) in seen:
                    continue
                seen.add(("determination", reference))
                if reference in cited_now:
                    reason = "carried"
                elif context.is_current:
                    reason = "determination-not-cited-by-this-record"
                else:
                    reason = "determination-not-attributable-to-this-context"
                rows.append(
                    EvidenceCarryOver(
                        citation=reference,
                        citation_kind="determination",
                        reason=reason,
                    )
                )
    return tuple(sorted(rows, key=lambda item: (item.citation_kind, item.citation)))


def _condition_status(
    *,
    condition: str,
    leaf_requirement_id: str,
    dispositions: tuple[MemberDisposition, ...],
    pack: PurposePack,
) -> tuple[str, str, str]:
    """``(named outcome, status, basis)`` for the cited ``recheck_condition``.

    **The comparability test runs first, and that ordering is the point.** Both
    of this Pack's coverage conditions — ``asset-identity-not-evaluated`` and
    ``in-model-position-not-evaluated`` — say "every element in the assessed
    scope is covered". Delete the one element that was not covered, or let an
    export mapping move its ``ifc_class`` out of the activity's
    ``subject_classes``, and the sentence is *literally true* over what is left,
    because the counterexample fell out of the set. Establishing that the set no
    longer corresponds is a different answer from establishing that the condition
    holds, and it has to be reached first or it is never reached at all.
    """

    if not condition or not leaf_requirement_id:
        return "", "no-recheck-condition", (
            "the cited subscope is READY and carries no resolution route, so there "
            "is no recheck condition to establish anything about; whether its "
            "members still reach READY is the separate statement recorded beside "
            "each of them"
        )

    gone = [item for item in dispositions if item.disposition != "present"]
    if gone:
        rendered = "; ".join(
            f"{list(item.member.keys)} -> {item.disposition}" for item in gone
        )
        return "", "not-comparable", (
            f"{len(gone)} of {len(dispositions)} sealed member(s) are no longer "
            f"subjects of this record's partition: {rendered}. A condition "
            "quantified over a set cannot be evaluated on a set that lost members, "
            "and a member that disappeared is not a member that was fixed"
        )

    requirement = pack.evidence_requirement(leaf_requirement_id)
    named = machine_checkable_outcome(condition, requirement)
    if not named:
        matched = sorted(set(_TOKEN.findall(condition)) & set(requirement.outcomes))
        return "", "no-machine-checkable-part", (
            f"the condition names {len(matched)} of "
            f"{leaf_requirement_id}'s declared outcomes {list(requirement.outcomes)}"
            + (f" ({matched})" if matched else "")
            + ". Exactly one is required for a value comparison; the sentence is "
            "otherwise prose for a person, and this record adjudicates no prose. "
            "Any judgement about it re-enters as a determination, with a determiner "
            "and a cited basis, like every other judgement here"
        )

    observed = sorted(
        {
            outcome
            for item in dispositions
            for outcome in item.current_leaf_outcomes
        }
    )
    if "" in observed:
        return named, "not-comparable", (
            f"the condition names outcome {named!r} of {leaf_requirement_id}, and at "
            "least one member's current path never reaches that evidence "
            "requirement, so there is no reading of it to compare"
        )
    if observed == [named]:
        return named, "named-outcome-observed", (
            f"every corresponding member now reads {named!r} for "
            f"{leaf_requirement_id}. Only the outcome the condition names was "
            "compared; the rest of the sentence was not read"
        )
    return named, "named-outcome-not-observed", (
        f"the condition names outcome {named!r} of {leaf_requirement_id} and the "
        f"corresponding members now read {observed}"
    )
