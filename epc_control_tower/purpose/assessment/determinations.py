"""Determinations arrive by reference; the assessment admits or declines them.

ADR 0003 §1.2 item 4 fixes the discipline and this module is the only place it
is enforced: *a determination is admitted or found inadmissible, never decided.*
There is no function here that looks at a model, a finding, or a geometry and
concludes that two models are aligned or that a chimney penetrates a slab.
Producing a determination is somebody's job outside this package; reading one is
this package's job, and the two must not meet.

The entry point is deliberately narrow. :class:`Determination` is a reference
with an attributable outcome hung on it — who determined it, on what basis, what
it says, and which subject it says it about. :func:`admit` answers one question,
"may this assessment rely on this?", and returns a reason when the answer is no.
An inadmissible determination is **no determination**: the subject reads its
evidence requirement's ``not-yet-*`` outcome and routes to ``UNKNOWN``. That is
the fail-closed direction, and it is not the same as reading a negative outcome.

One admissibility rule carries more weight than the others.
``penetration-confirmed`` must name every architectural element the penetrating
element passes through, each as an ``element_key`` of the **consuming** model
version. A determination that claims a penetration and lists no element is not
admissible — the Pack's own ``acceptance_condition`` says so — because the pair
grain the opening question reads at has that named element as its second member.
Admitting the claim without the elements would leave the assessment inventing a
counterpart, and a phantom key is exactly what the pair grain was chosen to
avoid.

This shape is a v1 internal boundary. It is not published as a machine contract,
and nothing outside this package depends on its field names.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..model import EvidenceRequirement

__all__ = [
    "Admissibility",
    "Determination",
    "DeterminationLedger",
    "PENETRATION_CONFIRMED",
]

#: The one outcome whose admissibility depends on more than its own shape.
PENETRATION_CONFIRMED = "penetration-confirmed"


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
    being read as a confirmation about another. A verdict is only ever true of
    the exact versions named, and the same has to hold of the evidence under it.
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


class DeterminationLedger:
    """The determinations one assessment was offered, indexed by subject.

    Construction is a pure indexing step. Every admissibility question is asked
    at read time against the evidence requirement that declares the grain and
    the outcome vocabulary, because the same reference means different things to
    two requirements and only the requirement knows which.
    """

    def __init__(
        self,
        determinations: Sequence[Determination],
        *,
        accepted_method_ids: dict[str, frozenset[str]],
        consuming_element_keys: frozenset[str],
    ) -> None:
        self._accepted = accepted_method_ids
        self._consuming = consuming_element_keys
        indexed: dict[tuple[str, tuple[str, ...]], list[Determination]] = {}
        for determination in determinations:
            indexed.setdefault(
                (determination.evidence_requirement_id, tuple(determination.subject)), []
            ).append(determination)
        # Sorted by reference so that two ledgers built from the same
        # determinations in different orders read identically.
        self._by_subject = {
            key: tuple(sorted(value, key=lambda item: item.reference))
            for key, value in indexed.items()
        }

    def admissibility(
        self, determination: Determination, requirement: EvidenceRequirement
    ) -> Admissibility:
        """May this assessment rely on this determination for this requirement?

        Checked in a fixed order so the recorded reason is stable, and every
        check is a membership test or a comparison of frozen strings.
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
        accepted = self._accepted.get(requirement.evidence_requirement_id, frozenset())
        if determination.method_id not in accepted:
            return Admissibility(
                False,
                "determination-method-not-accepted: "
                f"{determination.method_id!r} is not an accepted_evidence_methods "
                f"method for {requirement.evidence_requirement_id!r}",
            )
        arity = _GRAIN_ARITY[requirement.subject_grain]
        if len(determination.subject) != arity:
            return Admissibility(
                False,
                "determination-grain-mismatch: "
                f"{requirement.subject_grain!r} keys on {arity} key(s), "
                f"determination names {len(determination.subject)}",
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
        certainly not evidence that one does not.
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

    def resolve(
        self, requirement: EvidenceRequirement, subject: tuple[str, ...]
    ) -> tuple[Determination | None, str]:
        """The admissible determination for one subject, or why there is none.

        Returns ``(determination, reason)``. A ``None`` determination with an
        empty reason means nothing was offered at all; a ``None`` with a reason
        means something was offered and declined. Both read as the requirement's
        ``not-yet-*`` outcome, and the record keeps them apart.
        """

        offered = self._by_subject.get(
            (requirement.evidence_requirement_id, tuple(subject)), ()
        )
        if not offered:
            return None, ""
        declined: list[str] = []
        for determination in offered:
            verdict = self.admissibility(determination, requirement)
            if verdict.admitted:
                return determination, ""
            declined.append(f"{determination.reference}: {verdict.reason}")
        return None, "; ".join(declined)

    def counterparts(
        self,
        *,
        source_evidence_requirement_id: str,
        on_outcome: str,
        element_key: str,
    ) -> tuple[str, ...]:
        """The counterpart keys a ``pair_source`` determination named, in order.

        Both arguments come from the Pack's own ``pair_source`` rather than from
        a literal here, so a Pack that sources its pairs from some other
        requirement refines correctly without this module knowing its names.
        Used only to refine a subject into pairs: it reads the determination the
        assessment already admitted, and never searches for one.
        """

        offered = self._by_subject.get(
            (source_evidence_requirement_id, (element_key,)), ()
        )
        for determination in offered:
            if determination.outcome == on_outcome:
                return tuple(sorted(determination.penetrated_element_keys))
        return ()
