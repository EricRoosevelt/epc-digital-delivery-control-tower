"""A checker that is not IDS, and could not be.

The `Checker` protocol has existed since Phase 1 with exactly one
implementation, which is another way of saying it had not yet been shown to be
a seam rather than a decoration. This is the second one, and it is deliberately
a rule IDS 1.0 cannot state at all rather than one it states awkwardly.

IDS validates **one model against one document**. Every facet it has —
attribute, property, entity, material, classification, partOf — asks a question
about an element and answers it from that element's own file. There is no
construct for "and the same thing must also be true over there", because there
is no *over there*: the document never sees a second model. That ceiling is the
reason `CheckerCapabilities.requires_federated_context` was declared in Phase 1
and why nothing had used it until now.

What this checker asks is a question about a *set* of models:

    Every discipline model in a project must carry at least one coordination
    reference that its sibling models also carry.

It is the most basic precondition of federation. Three models that share no
common point cannot be overlaid, and a clash detection run over them is
meaningless. In the shipped fixture the answer differs by project, and both
answers are true: the PCERT models carry a shared `origin` and `geo-reference`
proxy, so they federate; the ISO reference-view models are three unrelated
sample files that happen to sit in one directory, and they share nothing.

Findings about something that is not there
------------------------------------------

A finding here has no element to point at when it fails, and that is the
modelling decision recorded in :class:`~..domain.Finding`: a finding names the
smallest thing that exists and that a person can go and look at. A model with no
shared reference has no element that *is* the problem — the problem is the
model. So the failure names the model and leaves ``element_key`` blank, rather
than minting a key for a reference that was never modelled.

The pass is the other half of the same rule and shows why it is not simply
"blank when convenient": a model that does carry a shared reference has one
specific element that demonstrates it, and that element is what the finding
names. A pass always has something to point at. Only a failure can be about
nothing.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from pathlib import Path

from ..determinism import canonical_json_document
from ..domain import Element, Finding, FindingStatus, Requirement, Severity
from ..identity import build_finding_key
from ..protocols import CheckContext, CheckerCapabilities, CheckerFailure, CheckOutcome

__all__ = ["CompletenessChecker", "SHARED_ACROSS_MODELS"]

#: The one requirement kind this checker understands. Declared as a constant
#: rather than accepted as free text so that a rule naming something else is
#: rejected when the rule library loads, not silently ignored at check time.
SHARED_ACROSS_MODELS = "shared-across-models"

_PASS_REASON = "A coordination reference shared with a sibling model is present."
_FAIL_REASON = (
    "This model carries no coordination reference that any sibling model also "
    "carries, so the project's models cannot be federated."
)
_NOT_APPLICABLE_REASON = "This project has only one model, so nothing is shared."


class CompletenessChecker:
    """Evaluates requirements that need more than one model to answer."""

    id = "completeness"

    version = "1.0.0"

    capabilities = CheckerCapabilities(
        # Not IDS facets. This checker reads the federated element register,
        # which is schema-independent, so it claims no facet vocabulary and no
        # IFC schema; the registry reads an empty tuple as "no constraint".
        facets=(SHARED_ACROSS_MODELS,),
        ifc_schemas=(),
        # The reason this flag was defined in Phase 1, finally used.
        requires_federated_context=True,
    )

    def __init__(self, ruleset_path: Path) -> None:
        self._ruleset_path = Path(ruleset_path)
        self._parameters: dict[str, dict] | None = None

    def config_sha256(self) -> str:
        """Digest of this checker's own configuration, which is empty.

        Not a digest of the rules: what the rules *say* reaches the validation
        identity through the rule set's normalized digest, and counting it twice
        would only make the identity harder to reason about. Same reasoning as
        the IDS checker, and the same constant for the same reason.
        """

        return hashlib.sha256(
            canonical_json_document({}).encode("utf-8")
        ).hexdigest()

    def parameters(self) -> dict[str, dict]:
        """Each completeness requirement's parameters, read from the rules.

        A `Requirement` carries identity and metadata, not a checker-specific
        payload — otherwise every checker would have to agree on the shape of a
        field only one of them uses. So this reads the rule files back, exactly
        as the IDS checker re-reads the document it compiled. A rule directory
        is this checker's source artifact too.
        """

        if self._parameters is None:
            from ..identity import build_requirement_key
            from ..rule_definitions import load_rule_definitions

            found: dict[str, dict] = {}
            if self._ruleset_path.is_dir():
                for rule in load_rule_definitions(self._ruleset_path).rules:
                    if rule.checker != self.id:
                        continue
                    for facet in rule.requirements:
                        found[build_requirement_key(rule.rule_id, facet.kind)] = dict(
                            facet.values
                        )
            self._parameters = found
        return self._parameters

    # -- checking ----------------------------------------------------------

    def check(self, context: CheckContext) -> CheckOutcome:
        findings: list[Finding] = []
        failures: list[CheckerFailure] = []

        for requirement in sorted(
            context.requirements, key=lambda item: item.requirement_key
        ):
            if requirement.requirement_id != SHARED_ACROSS_MODELS:
                failures.append(
                    CheckerFailure(
                        checker_id=self.id,
                        project_id=context.project.project_id,
                        model_key="",
                        message=(
                            f"{requirement.rule_id}: unknown completeness "
                            f"requirement {requirement.requirement_id!r}"
                        ),
                        detail="UnknownRequirement",
                    )
                )
                continue
            parameters = self.parameters().get(requirement.requirement_key)
            if parameters is None:
                failures.append(
                    CheckerFailure(
                        checker_id=self.id,
                        project_id=context.project.project_id,
                        model_key="",
                        message=(
                            f"{requirement.rule_id}: no completeness rule declares "
                            f"requirement {requirement.requirement_id!r}"
                        ),
                        detail="MissingParameters",
                    )
                )
                continue
            findings.extend(
                self._shared_across_models(requirement, parameters, context)
            )

        return CheckOutcome(findings=tuple(findings), failures=tuple(failures))

    # -- internals ---------------------------------------------------------

    def _shared_across_models(
        self,
        requirement: Requirement,
        parameters: dict,
        context: CheckContext,
    ) -> list[Finding]:
        pattern = re.compile(str(parameters.get("name_pattern") or ".*"))
        models = sorted(model.model_key for model in context.models)

        # Which models each candidate GlobalId occurs in. A GlobalId is unique
        # within a file but deliberately reused across discipline exports of the
        # same object, which is exactly the signal being read here.
        occurrences: dict[str, dict[str, Element]] = defaultdict(dict)
        for model_key in models:
            for element in context.elements_for(model_key):
                if pattern.search(element.name):
                    occurrences[element.global_id][model_key] = element

        shared: dict[str, list[Element]] = defaultdict(list)
        for by_model in occurrences.values():
            if len(by_model) < 2:
                continue
            for model_key, element in by_model.items():
                shared[model_key].append(element)

        findings: list[Finding] = []
        for model_key in models:
            witnesses = sorted(shared.get(model_key, ()), key=lambda e: e.element_key)
            if len(models) < 2:
                # One model cannot share anything with a sibling it does not
                # have. Reporting that as a failure would blame a project for
                # the shape of its own scope.
                findings.append(
                    self._finding(
                        context=context,
                        requirement=requirement,
                        model_key=model_key,
                        element=None,
                        status=FindingStatus.NOT_APPLICABLE,
                        reason=_NOT_APPLICABLE_REASON,
                    )
                )
            elif witnesses:
                findings.append(
                    self._finding(
                        context=context,
                        requirement=requirement,
                        model_key=model_key,
                        # The first by key, not an arbitrary one: a finding that
                        # named a different witness on each run would make the
                        # published bytes depend on dictionary order.
                        element=witnesses[0],
                        status=FindingStatus.PASS,
                        reason=_PASS_REASON,
                    )
                )
            else:
                findings.append(
                    self._finding(
                        context=context,
                        requirement=requirement,
                        model_key=model_key,
                        element=None,
                        status=FindingStatus.FAIL,
                        reason=_FAIL_REASON,
                    )
                )
        return findings

    def _finding(
        self,
        *,
        context: CheckContext,
        requirement: Requirement,
        model_key: str,
        element: Element | None,
        status: FindingStatus,
        reason: str,
    ) -> Finding:
        element_key = element.element_key if element is not None else ""
        return Finding(
            finding_key=build_finding_key(
                validation_run_id=context.validation_run_id,
                model_key=model_key,
                requirement_key=requirement.requirement_key,
                element_key=element_key,
            ),
            validation_run_id=context.validation_run_id,
            project_id=context.project.project_id,
            model_key=model_key,
            element_key=element_key,
            requirement_key=requirement.requirement_key,
            status=status,
            severity=(
                requirement.severity if status is FindingStatus.FAIL else Severity.INFO
            ),
            is_applicable=status is not FindingStatus.NOT_APPLICABLE,
            is_issue=status is FindingStatus.FAIL,
            expected=requirement.requirement_label,
            # Consistent with the IDS checker, and for the same reason: the
            # observed value of "a reference this model shares with a sibling"
            # is either the element already named above or nothing at all.
            actual="",
            reason=reason,
        )
