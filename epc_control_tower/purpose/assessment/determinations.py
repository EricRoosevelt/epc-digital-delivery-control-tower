"""Determinations arrive by reference; the assessment admits or declines them.

ADR 0003 §1.2 item 4 fixes the discipline and this module is the only place it
is enforced: *a determination is admitted or found inadmissible, never decided.*
There is no function here that looks at a model, a finding, or a geometry and
concludes that two models are aligned or that a chimney penetrates a slab.
Producing a determination is somebody's job outside this package; reading one is
this package's job, and the two must not meet.

A determination is admissible only when three things about it can be
**checked**, and each has its own failure:

* **Policy.** The ``method_id`` it cites resolves to an
  ``overlay.accepted_evidence_methods[]`` row whose ``decision_basis`` is
  ``project-decision``. A row that is missing means the project never accepted
  that method, so the determination is not evidence *here* and the subject reads
  ``not-yet-*``. A row that exists but reads ``illustrative`` is different in
  kind: it states the shape of an acceptance nobody decided, so consuming its
  output would put a decision nobody made inside a record, and the request is
  **refused**.
* **Version attribution.** It says which model versions it was made against —
  both ``model_key`` values *and* both content identifiers — and every one of
  the four is compared against the request's model-version context. A
  determination about an earlier version of either model does not silently
  become a determination about this one. This is a **separate** check from
  ``context-model-version-mismatch``, which asks whether the request's own
  context agrees with the validated facts; the two can fail independently and
  say different things.
* **Content consistency.** One ``reference`` names one document, so the same
  reference offered twice with different content is a store this assessment
  cannot trust. And two admissible determinations about the same fact that
  disagree are not evidence for either answer.

**Where two admissible determinations disagree, the request is refused.** §4.5
faces the neighbouring problem for a ``CONDITIONAL`` continuation and reduces by
*maximum over the enumerated set* — deliberately not a pick, so the answer does
not depend on citation order or on which one was found first. The reasoning
carries: selecting between contradictory determinations by reference name, by
sort order, or by arrival order would make a verdict a function of how the
evidence happened to be handed in. The *remedy* differs because the product
asked for a different one — §4.5 takes the most adverse reading and continues,
while here the request stops and says which references conflict. Both refuse to
choose; only one of them has a safe value to fall back to, because "most adverse
alignment outcome" is not a thing an assessment is entitled to invent.

**Refusing and declining are two different fail-closed directions**, and which
one applies turns on whether the defect is in the *request* or in the
*evidence*:

* **Declined** — the determination is correctly keyed onto a subject, and its
  content fails an acceptance condition: it is unattributable (no determiner, no
  basis), its outcome is not one the requirement declares, or it is a
  ``penetration-confirmed`` naming no architectural element, or naming one
  absent from the consuming model version. The subject reads ``not-yet-*`` and
  routes to ``UNKNOWN``, no pair is refined from it, and no verdict moves. This
  is "no admissible evidence yet", which is a fact about the handover.
* **Refused** — the determination cannot be keyed or trusted at all: its
  ``subject`` has the wrong arity for the declared grain, so which subject it is
  about cannot be established; or it rests on illustrative policy; or it is
  attributed to other model versions; or the offered set contradicts itself.
  None of these is a gap in the evidence — each is a defect in what was handed
  in, and §7.1 catches those before any subscope is assessed.

This shape is a v1 internal boundary. It is not published as a machine contract,
and nothing outside this package depends on its field names.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..errors import PurposeAssessmentError
from ..model import PROJECT_DECISION, EvidenceRequirement

__all__ = [
    "Admissibility",
    "DeterminedAgainst",
    "Determination",
    "DeterminationLedger",
    "PENETRATION_CONFIRMED",
]

#: The one outcome whose admissibility depends on more than its own shape.
PENETRATION_CONFIRMED = "penetration-confirmed"


@dataclass(frozen=True, slots=True)
class DeterminedAgainst:
    """The exact model versions a determination was made against.

    Both keys and both content identifiers, because a ``model_key`` alone says
    *which model* and not *which version of it*, and the whole point of the check
    is that a determination about last week's export is not a determination
    about this one. Compared value by value against the request's
    model-version context; nothing here is inferred, defaulted, or ranged over.
    """

    producing_model_key: str
    producing_content_id: str
    consuming_model_key: str
    consuming_content_id: str

    def as_tuple(self) -> tuple[str, str, str, str]:
        return (
            self.producing_model_key,
            self.producing_content_id,
            self.consuming_model_key,
            self.consuming_content_id,
        )


@dataclass(frozen=True, slots=True)
class Determination:
    """One recorded determination, cited rather than produced.

    ``reference`` is the handle the record cites; its resolution and storage are
    somebody else's problem by design. ``determiner`` and ``basis`` are what make
    the outcome attributable — an unattributable assertion is not evidence, and
    a determination missing either is read as absent rather than as its outcome.

    ``subject`` keys the determination onto an observation subject and its shape
    follows the evidence requirement's declared grain: the *(producing,
    consuming)* ``model_key`` pair for ``whole-scope``, one ``element_key`` for
    ``per-subject``, and the *(penetrating, penetrated)* pair for
    ``per-subject-pair``.

    A ``whole-scope`` determination naming the model pair rather than nothing is
    what stops an alignment confirmation produced for one pair of models from
    being read as a confirmation about another. ``determined_against`` carries
    the same discipline down to the version: a verdict is only ever true of the
    exact versions named, and the evidence under it has to name them too.
    """

    reference: str
    evidence_requirement_id: str
    method_id: str
    determiner: str
    basis: str
    outcome: str
    subject: tuple[str, ...] = ()
    #: The architectural element keys a ``penetration-confirmed`` determination
    #: named. Empty for every other outcome, and its emptiness *under* that
    #: outcome is what makes the determination inadmissible.
    penetrated_element_keys: tuple[str, ...] = ()
    #: Which model versions this determination was made against. Absent is not a
    #: neutral default — an unattributed determination cannot be shown to be
    #: about this request's versions, so the request is refused.
    determined_against: DeterminedAgainst | None = None

    @property
    def content(self) -> tuple:
        """Everything this determination *says*, for equality between references.

        Excludes ``reference`` itself, so that two offerings under one reference
        can be compared for having the same content. Includes
        ``penetrated_element_keys``, because two ``penetration-confirmed``
        determinations naming different architectural elements disagree about
        which pairs exist even though their outcomes match.
        """

        return (
            self.evidence_requirement_id,
            self.method_id,
            self.determiner,
            self.basis,
            self.outcome,
            tuple(self.subject),
            tuple(sorted(self.penetrated_element_keys)),
            self.determined_against.as_tuple() if self.determined_against else (),
        )

    @property
    def claim(self) -> tuple:
        """What this determination concludes, for detecting contradiction.

        Narrower than :attr:`content`: two determinations by different people on
        different bases that reach the same conclusion about the same subject
        corroborate each other and are not a conflict. What may not differ is
        the conclusion — the outcome, and the architectural elements a confirmed
        penetration named, since those decide which pairs the walk refines into.
        """

        return (self.outcome, tuple(sorted(self.penetrated_element_keys)))


@dataclass(frozen=True, slots=True)
class Admissibility:
    """Whether one determination may be relied on, and why not when it may not.

    ``reason`` is recorded on the reading, so a subject that reads ``not-yet-*``
    because a determination was declined says so, rather than looking identical
    to a subject nobody ever determined anything about.
    """

    admitted: bool
    reason: str = ""


#: How many keys a determination's ``subject`` carries at each declared grain.
#: ``whole-scope`` is 2 rather than 0 because its one fact is about the model
#: *pair*, and a fact about a pair has to say which pair.
_GRAIN_ARITY = {"whole-scope": 2, "per-subject": 1, "per-subject-pair": 2}


def _refuse(code: str, message: str) -> None:
    raise PurposeAssessmentError(code, message)


class DeterminationLedger:
    """The determinations one assessment was offered, indexed by subject.

    Construction indexes; :meth:`validate` checks everything that is a defect in
    what was handed in, once, before any subscope is assessed; :meth:`resolve`
    then reads. Splitting it that way is what lets a conflict be a refusal in
    §7.1's sense rather than something discovered halfway down a decision tree.
    """

    def __init__(
        self,
        determinations: Sequence[Determination],
        *,
        method_policy: dict[str, dict[str, str]],
        consuming_element_keys: frozenset[str],
        determined_against: DeterminedAgainst,
    ) -> None:
        self._policy = method_policy
        self._consuming = consuming_element_keys
        self._context = determined_against
        self._offered = tuple(determinations)
        indexed: dict[tuple[str, tuple[str, ...]], list[Determination]] = {}
        for determination in self._offered:
            indexed.setdefault(
                (determination.evidence_requirement_id, tuple(determination.subject)), []
            ).append(determination)
        # Sorted by reference so that two ledgers built from the same
        # determinations in different orders read identically.
        self._by_subject = {
            key: tuple(sorted(value, key=lambda item: item.reference))
            for key, value in indexed.items()
        }

    # -- checks that refuse -------------------------------------------------

    def validate(self, requirements: Sequence[EvidenceRequirement]) -> None:
        """Refuse every defect in the offered set, before anything is assessed.

        ``requirements`` are the evidence requirements the requested activities
        will actually read. A determination offered for a requirement outside
        that set is not consumed by this request and is not checked here — the
        request is refused for what it relies on, not for what it carries past.
        """

        consumed = {item.evidence_requirement_id: item for item in requirements}
        self._check_references_are_unique()
        for determination in sorted(self._offered, key=lambda item: item.reference):
            requirement = consumed.get(determination.evidence_requirement_id)
            if requirement is None:
                continue
            self._check_grain(determination, requirement)
            self._check_method_policy(determination, requirement)
            self._check_version_attribution(determination)
        self._check_no_contradiction(consumed)

    def _check_references_are_unique(self) -> None:
        """One reference names one document, so one reference has one content."""

        by_reference: dict[str, list[Determination]] = {}
        for determination in self._offered:
            by_reference.setdefault(determination.reference, []).append(determination)
        for reference in sorted(by_reference):
            contents = {item.content for item in by_reference[reference]}
            if len(contents) > 1:
                _refuse(
                    "determination-reference-not-unique",
                    f"reference {reference!r} was offered {len(by_reference[reference])} "
                    f"times with {len(contents)} different contents. A reference names one "
                    "determination; two documents under one handle mean the assessment "
                    "cannot say which one it read, and it will not pick",
                )

    def _check_grain(
        self, determination: Determination, requirement: EvidenceRequirement
    ) -> None:
        """A determination whose subject cannot be interpreted is not evidence.

        Refused rather than declined, and the distinction is not cosmetic: a
        declined determination says "no admissible evidence for *this subject*
        yet", which presupposes that the subject is known. A wrong-arity subject
        means it is not.
        """

        arity = _GRAIN_ARITY[requirement.subject_grain]
        if len(determination.subject) != arity:
            _refuse(
                "determination-grain-mismatch",
                f"determination {determination.reference!r} for "
                f"{requirement.evidence_requirement_id!r} names "
                f"{len(determination.subject)} subject key(s), and the declared grain "
                f"{requirement.subject_grain!r} keys on {arity}; which subject this is "
                "about cannot be established, so it is not evidence about anything",
            )

    def _check_method_policy(
        self, determination: Determination, requirement: EvidenceRequirement
    ) -> None:
        """A consumed method row must record an acceptance the project took.

        A **missing** row is not checked here: it means the project never
        accepted that method, which makes the determination inadmissible rather
        than the request defective, and :meth:`admissibility` declines it. A row
        that exists and reads ``illustrative`` is the case this refuses — the
        same family as the ``team_mapping`` gate of §4.3 and deliberately a
        different refusal, because the row a maintainer must edit is a different
        row in a different table.
        """

        policy = self._policy.get(requirement.evidence_requirement_id, {})
        basis = policy.get(determination.method_id)
        if basis is None or basis == PROJECT_DECISION:
            return
        _refuse(
            "accepted-method-decision-basis-illustrative",
            f"determination {determination.reference!r} cites method_id "
            f"{determination.method_id!r} for "
            f"{requirement.evidence_requirement_id!r}, whose "
            f"overlay.accepted_evidence_methods row has decision_basis {basis!r}. "
            "Consuming its output would claim this project accepts a method it never "
            "decided to accept; the row exists, so this is not the missing-row case",
        )

    def _check_version_attribution(self, determination: Determination) -> None:
        """The determination names this request's model versions, value for value.

        Separate from ``context-model-version-mismatch``, which asks whether the
        request's own context matches the validated facts. That check can pass
        while this one fails — a perfectly consistent request, handed evidence
        produced against last week's export.
        """

        attribution = determination.determined_against
        if attribution is None:
            _refuse(
                "determination-model-version-unattributed",
                f"determination {determination.reference!r} does not say which model "
                "versions it was made against, so it cannot be shown to be about the "
                "ones this request names. Absence is not agreement",
            )
            raise AssertionError("unreachable")
        if attribution.as_tuple() != self._context.as_tuple():
            _refuse(
                "determination-model-version-mismatch",
                f"determination {determination.reference!r} was made against "
                f"{attribution.as_tuple()} and this request's model-version context is "
                f"{self._context.as_tuple()}. A determination about one version of "
                "either model never becomes a determination about another",
            )

    def _check_no_contradiction(
        self, consumed: dict[str, EvidenceRequirement]
    ) -> None:
        """Two admissible determinations about one fact must reach one conclusion.

        Corroboration is fine: two reviewers, two bases, the same conclusion
        about the same subject are two references and no conflict. What is
        refused is disagreement, and it is refused rather than reduced because
        picking one — by reference name, by sort order, by arrival order — would
        make the verdict a function of how the evidence was handed in, and there
        is no "most adverse" alignment outcome an assessment is entitled to
        substitute (§4.5 reduces where such a value exists; here none does).
        """

        for (requirement_id, subject), offered in sorted(self._by_subject.items()):
            requirement = consumed.get(requirement_id)
            if requirement is None:
                continue
            admissible = [
                item
                for item in offered
                if self.admissibility(item, requirement).admitted
            ]
            claims = {item.claim for item in admissible}
            if len(claims) > 1:
                references = sorted(item.reference for item in admissible)
                rendered = "; ".join(
                    f"{item.reference!r} -> {item.claim[0]!r}"
                    + (
                        f" naming {list(item.claim[1])}"
                        if item.claim[1]
                        else ""
                    )
                    for item in sorted(admissible, key=lambda x: x.reference)
                )
                _refuse(
                    "determination-conflict",
                    f"{len(admissible)} admissible determinations about "
                    f"{requirement_id!r} for subject {list(subject)} reach "
                    f"{len(claims)} different conclusions: {rendered}. The assessment "
                    "will not choose between them by reference name, sort order, or the "
                    f"order they arrived in; conflicting references: {references}",
                )

    # -- checks that decline ------------------------------------------------

    def admissibility(
        self, determination: Determination, requirement: EvidenceRequirement
    ) -> Admissibility:
        """May this assessment rely on this determination for this requirement?

        Every check here **declines**: the determination is keyed onto a known
        subject and its content is what fails, so the subject reads ``not-yet-*``
        and routes to ``UNKNOWN``. The checks that refuse live in
        :meth:`validate` and have already run by the time this is called during
        a walk. Checked in a fixed order so the recorded reason is stable, and
        every check is a membership test or a comparison of frozen strings.
        """

        if not determination.reference:
            return Admissibility(False, "determination-unreferenced")
        if not determination.determiner:
            return Admissibility(False, "determination-unattributed")
        if not determination.basis:
            return Admissibility(False, "determination-without-basis")
        if determination.outcome not in requirement.outcomes:
            return Admissibility(
                False,
                "determination-outcome-not-declared: "
                f"{determination.outcome!r} is not one of "
                f"{list(requirement.outcomes)}",
            )
        policy = self._policy.get(requirement.evidence_requirement_id, {})
        if determination.method_id not in policy:
            return Admissibility(
                False,
                "determination-method-not-accepted: "
                f"{determination.method_id!r} is not an accepted_evidence_methods "
                f"method for {requirement.evidence_requirement_id!r}",
            )
        if determination.outcome == PENETRATION_CONFIRMED:
            return self._penetration_admissibility(determination)
        if determination.penetrated_element_keys:
            return Admissibility(
                False,
                "determination-names-penetrated-elements-without-confirming: "
                f"outcome {determination.outcome!r} names architectural elements",
            )
        return Admissibility(True)

    def _penetration_admissibility(self, determination: Determination) -> Admissibility:
        """A confirmed penetration names its architectural elements, or is not one.

        The Pack's ``acceptance_condition`` requires every penetrated element as
        an ``element_key`` of the consuming model version. Both failures below
        read as the absent state rather than as a negative outcome: a claim
        nobody can inspect is not evidence that a penetration exists, and it is
        certainly not evidence that one does not. Declining also means no pair is
        refined from it, so an unusable claim moves no verdict and creates no
        subject.
        """

        if not determination.penetrated_element_keys:
            return Admissibility(
                False,
                "penetration-confirmed-names-no-architectural-element",
            )
        unknown = sorted(
            key
            for key in determination.penetrated_element_keys
            if key not in self._consuming
        )
        if unknown:
            return Admissibility(
                False,
                "penetration-confirmed-names-absent-element: "
                f"{unknown} not in the consuming model version",
            )
        return Admissibility(True)

    # -- reading ------------------------------------------------------------

    def resolve(
        self, requirement: EvidenceRequirement, subject: tuple[str, ...]
    ) -> tuple[tuple[Determination, ...], str]:
        """Every admissible determination for one subject, or why there are none.

        Returns ``(determinations, declined reason)``. An empty tuple with an
        empty reason means nothing was offered at all; an empty tuple with a
        reason means something was offered and declined. Both read as the
        requirement's ``not-yet-*`` outcome, and the record keeps them apart.

        When the tuple is non-empty every member reaches the same conclusion:
        :meth:`validate` has already refused the request otherwise. So the
        reading cites all of them and selects between none of them.
        """

        offered = self._by_subject.get(
            (requirement.evidence_requirement_id, tuple(subject)), ()
        )
        if not offered:
            return (), ""
        admissible: list[Determination] = []
        declined: list[str] = []
        for determination in offered:
            verdict = self.admissibility(determination, requirement)
            if verdict.admitted:
                admissible.append(determination)
            else:
                declined.append(f"{determination.reference}: {verdict.reason}")
        if admissible:
            return tuple(admissible), ""
        return (), "; ".join(declined)

    def counterparts(
        self,
        *,
        source_evidence_requirement_id: str,
        on_outcome: str,
        element_key: str,
        requirement: EvidenceRequirement,
    ) -> tuple[str, ...]:
        """The counterpart keys a ``pair_source`` determination named, in order.

        The source requirement is passed in from the Pack's own ``pair_source``
        rather than named by a literal here, so a Pack sourcing its pairs from
        some other requirement refines correctly without this module knowing its
        names. Only **admissible** determinations are read, which is what makes
        a declined penetration claim create no pair at all.
        """

        offered = self._by_subject.get(
            (source_evidence_requirement_id, (element_key,)), ()
        )
        for determination in offered:
            if determination.outcome != on_outcome:
                continue
            if not self.admissibility(determination, requirement).admitted:
                continue
            return tuple(sorted(determination.penetrated_element_keys))
        return ()
