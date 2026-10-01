"""The validated facts an assessment may read, and nothing else.

ADR 0003 §1.2 lists what a runtime purpose assessment reads. ADR 0003 §3.4 lists
what it must never read: ``Finding.is_issue``, ``Issue``, and a ``Requirement``'s
``owner_role``, ``severity``, ``stage``, ``priority`` or ``labels``. Those two
lists are the whole reason this module exists.

The prohibition could have been a rule the evaluator promises to keep. It is
instead a **shape**: :class:`AssessmentFacts` is a narrow projection of a
``RunBundle`` with no field for any of them, so the evaluator cannot read a
severity by mistake, cannot be tempted to soften a verdict with one, and cannot
acquire the habit later. R-005A and R-005B fail at ``WARNING`` and reach
``BLOCKED``; the reason that is not a judgement call here is that severity never
arrives.

The projection is deliberately lossy in one more direction. A finding reduces to
*(element_key, requirement_key, status)* — three frozen strings. ``element_key``
is carried because a reading is about one observation subject, and the 57
model-level ``N/A`` rows in this repository's own canonical output key on the
same ``requirement_key`` values ``pcert-sample``'s Overlay binds to
``asset-identity``; a projection that dropped ``element_key`` would let a join on
``requirement_key`` alone sweep every one of them into a unit reading.
``status`` is carried whole, ``N/A`` included, because ``N/A`` is a third state
and not a missing ``PASS``.

A reading consults only those three. Beside them each finding carries a
comparison basis — model, predicate digest, content digest, checker fingerprint —
that a record seals and a recheck compares, and that no verdict is ever computed
from (:class:`FindingFact`).
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from ...determinism import canonical_json_document
from ...domain import ComponentFingerprint

__all__ = [
    "AssessmentFacts",
    "ElementFact",
    "FindingFact",
    "ModelVersionFact",
    "facts_from_bundle",
    "finding_content_digest",
]

#: Hashed into every ``content_digest``, so the shape of what is compared can
#: change later without two shapes ever being read as one.
CONTENT_BASIS = 1


@dataclass(frozen=True, slots=True)
class ElementFact:
    """One element of one model version, as the element inventory publishes it.

    ``ifc_class`` is here for exactly one purpose — admitting the element as an
    observation subject of an activity whose ``subject_classes`` name that class
    (ADR 0003 §3.1). It is never a readiness signal, and never a stand-in for
    whether a rule reached the element.
    """

    element_key: str
    model_key: str
    ifc_class: str


@dataclass(frozen=True, slots=True)
class FindingFact:
    """One validation outcome, reduced to what a reading may consult.

    ``element_key`` is empty for a model-level finding. That emptiness is load
    bearing: a model-level row belongs to no observation subject, and the
    reading rule joins on ``element_key`` as well as ``requirement_key`` so that
    it can never be read as one.

    ``finding_key`` is carried because a record *cites* it. That citation is the
    whole of the relationship: the digest of an assessment may take a
    ``finding_key`` as input, and no ``finding_key`` ever takes an assessment
    value as one.

    The last four fields are the **comparison basis** a record seals beside each
    finding it cites (ADR 0005 §5.2.2), so that a later recheck can tell the same
    evidence under another key from different evidence under any key. None of
    them is a readiness signal, and none is a field ADR 0003 §3.4 withholds:

    * ``model_key`` — which model version's finding this is;
    * ``semantics_digest`` — the requirement's predicate (empty when the rule
      set was read from an ``.ids`` document, and then not comparable);
    * ``content_digest`` — what the finding *says*: its status, ``expected``,
      ``actual`` and ``reason``;
    * ``checker`` — the fingerprint of the checker that produced it, because a
      checker version that moved changes behaviour no digest above can see.

    They default to empty only so a hand-built fact stays constructible. A record
    built from such a fact seals an empty basis, and a recheck reads an empty
    basis as *not comparable*, never as equal.
    """

    finding_key: str
    element_key: str
    requirement_key: str
    status: str
    model_key: str = ""
    semantics_digest: str = ""
    content_digest: str = ""
    checker: ComponentFingerprint | None = None


@dataclass(frozen=True, slots=True)
class ModelVersionFact:
    """Which model versions the cited validation run actually validated."""

    model_key: str
    content_id: str


@dataclass(frozen=True, slots=True)
class AssessmentFacts:
    """Everything ADR 0003 §1.2 item 1 admits, and nothing it does not.

    Read-only by construction. Nothing here is mutated by an assessment, and
    there is nowhere here to put an answer.
    """

    project_id: str
    validation_run_id: str
    ruleset_id: str
    ruleset_version: str
    elements: tuple[ElementFact, ...]
    findings: tuple[FindingFact, ...]
    #: ``stage -> due``, verbatim from the project's programme. Cited by a
    #: consequence, never converted into a duration or a lateness (ADR 0003
    #: §4.6).
    milestones: Mapping[str, str]
    models: tuple[ModelVersionFact, ...]

    def element(self, element_key: str) -> ElementFact | None:
        for item in self.elements:
            if item.element_key == element_key:
                return item
        return None

    def elements_of(self, model_key: str) -> tuple[ElementFact, ...]:
        """Every element of one model version, in ``element_key`` order.

        This is what a ``model_key`` in a declared scope expands to, and the
        expansion is total: an element no rule ever reached is in it, which is
        what lets an unevaluated element surface as its own subscope instead of
        vanishing.
        """

        return tuple(
            sorted(
                (item for item in self.elements if item.model_key == model_key),
                key=lambda item: item.element_key,
            )
        )

    def model(self, model_key: str) -> ModelVersionFact | None:
        for item in self.models:
            if item.model_key == model_key:
                return item
        return None

    def findings_for(
        self, element_key: str, requirement_keys: frozenset[str]
    ) -> tuple[FindingFact, ...]:
        """Every finding for one subject under one binding's keys.

        Both halves of the join are required, and the ``element_key`` half is
        the one with a live way to go wrong: this repository publishes 57
        model-level ``N/A`` findings, and they key on the same
        ``requirement_key`` values ``pcert-sample``'s Overlay binds to
        ``asset-identity``. Joining on ``requirement_key`` alone would pull all
        57 into whichever subject was being read.
        """

        if not element_key:
            raise ValueError("a reading is about a subject; the empty key is not one")
        return tuple(
            sorted(
                (
                    finding
                    for finding in self.findings
                    if finding.element_key == element_key
                    and finding.requirement_key in requirement_keys
                ),
                key=lambda item: (item.requirement_key, item.finding_key),
            )
        )


def finding_content_digest(finding) -> str:
    """What one finding says, as a SHA-256: status, expected, actual, reason.

    Not its key and not its coordinates: those are what a comparison matches on,
    and the point of this digest is whether two findings that match also *say*
    the same thing. It sees an output that moved when neither the predicate nor
    the model did — a checker library upgrade, say — and it cannot see an
    implementation that changed while its output happened not to (ADR 0005
    §5.2.2, U2).
    """

    document = {
        "basis": CONTENT_BASIS,
        "status": str(finding.status),
        "expected": finding.expected,
        "actual": finding.actual,
        "reason": finding.reason,
    }
    return hashlib.sha256(canonical_json_document(document).encode("utf-8")).hexdigest()


def facts_from_bundle(bundle, project_id: str) -> AssessmentFacts:
    """Narrow one run's ``RunBundle`` to the facts an assessment may read.

    This is the only place the two vocabularies meet, and it is a one-way door.
    ``bundle.issues`` and ``bundle.issue_events`` are not projected at all;
    ``Finding.is_issue`` and ``Finding.severity`` are dropped; the
    ``Requirement`` set is reduced to the keys a binding can name, because a
    binding cites a key and a verdict is never a function of what a rule author
    wrote *about* the rule.

    From each requirement exactly two more things cross: its
    ``semantics_digest`` and the fingerprint of the checker it routes to. Both
    say *which check* produced a finding, never what the finding means for
    readiness, and both are what a recheck needs to tell the same evidence under
    a new key from different evidence (ADR 0005 §5.2.2). ``severity``,
    ``owner_role``, ``stage``, ``priority`` and ``labels`` still do not cross.
    """

    requirements = {item.requirement_key: item for item in bundle.ruleset.requirements}
    checkers = {
        fingerprint.component_id: fingerprint
        for fingerprint in bundle.run.checker_fingerprints
    }

    def fact(finding) -> FindingFact:
        requirement = requirements[finding.requirement_key]
        checker = checkers.get(requirement.checker)
        if checker is None:
            # Unreachable for a bundle the pipeline built: every routed checker
            # is fingerprinted into the validation identity. Refused rather than
            # projected without one, because a missing fingerprint must never
            # read as "the same checker".
            raise ValueError(
                f"{finding.finding_key}: checker {requirement.checker!r} has no "
                "fingerprint in this run"
            )
        return FindingFact(
            finding_key=finding.finding_key,
            element_key=finding.element_key,
            requirement_key=finding.requirement_key,
            status=str(finding.status),
            model_key=finding.model_key,
            semantics_digest=requirement.semantics_digest,
            content_digest=finding_content_digest(finding),
            checker=checker,
        )

    findings = tuple(
        sorted(
            (
                fact(finding)
                for finding in bundle.findings
                if finding.project_id == project_id
            ),
            key=lambda item: (item.element_key, item.requirement_key, item.finding_key),
        )
    )
    models = tuple(
        sorted(
            (
                ModelVersionFact(
                    model_key=model.model_key,
                    content_id=model.provenance.content_sha256,
                )
                for model in bundle.models
                if model.project_id == project_id
            ),
            key=lambda item: item.model_key,
        )
    )
    model_keys = {item.model_key for item in models}
    elements = tuple(
        sorted(
            (
                ElementFact(
                    element_key=element.element_key,
                    model_key=element.model_key,
                    ifc_class=element.ifc_class,
                )
                for element in bundle.elements
                if element.model_key in model_keys
            ),
            key=lambda item: item.element_key,
        )
    )
    return AssessmentFacts(
        project_id=project_id,
        validation_run_id=bundle.run.validation_run_id,
        ruleset_id=bundle.ruleset.ruleset_id,
        ruleset_version=bundle.ruleset.version,
        elements=elements,
        findings=findings,
        milestones=MappingProxyType(dict(bundle.milestones_for(project_id))),
        models=models,
    )
