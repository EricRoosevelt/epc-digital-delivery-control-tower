"""Check: elements and requirements become findings.

The stage itself evaluates nothing. It routes each requirement to the checker
that requirement names, hands that checker a context, and collects what comes
back. Adding a second kind of check — cross-model completeness, a threshold, a
deliverable-set audit — therefore means registering an implementation, not
editing this file.

Failures are structured rather than fatal-on-the-spot: a checker that raises
produces a :class:`~..protocols.CheckerFailure` naming the checker, the project
and the model. The stage still fails closed, it just fails legibly, and it can
report every failure instead of only the first one to blow up.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from ..config import ProjectManifest
from ..domain import Element, Finding, Model, Project, RuleSet
from ..protocols import CheckContext, CheckerFailure
from ..registry import Registry

__all__ = ["CheckStageError", "CheckResult", "check"]


class CheckStageError(RuntimeError):
    """One or more checkers could not complete."""

    def __init__(self, failures: Sequence[CheckerFailure]) -> None:
        self.failures = list(failures)
        joined = "\n  - ".join(failure.describe() for failure in self.failures)
        super().__init__(f"{len(self.failures)} checker failure(s):\n  - {joined}")


@dataclass(frozen=True, slots=True)
class CheckResult:
    findings: tuple[Finding, ...] = ()
    failures: tuple[CheckerFailure, ...] = ()

    def raise_for_failures(self) -> None:
        if self.failures:
            raise CheckStageError(self.failures)


def check(
    *,
    registry: Registry,
    ruleset: RuleSet,
    manifests: Sequence[ProjectManifest],
    projects: Sequence[Project],
    models: Sequence[Model],
    elements: Sequence[Element],
    validation_run_id: str,
    as_of: str,
    reports_dir: Path,
) -> CheckResult:
    """Evaluate every requirement against every project's models.

    Routing and plan validation both happen before a single model is opened, so
    a rule pointed at a checker that does not exist — or at one that cannot
    evaluate its facets, or read its schema — fails immediately and says so.
    """

    routed = registry.route(ruleset.requirements)
    registry.validate_plan(routed, models)

    raw_data_dirs = {
        manifest.project.project_id: manifest.raw_data_dir for manifest in manifests
    }

    findings: list[Finding] = []
    failures: list[CheckerFailure] = []

    for project in sorted(projects, key=lambda item: item.project_id):
        project_models = tuple(
            model for model in models if model.project_id == project.project_id
        )
        if not project_models:
            continue
        project_model_keys = {model.model_key for model in project_models}
        project_elements = tuple(
            element for element in elements if element.model_key in project_model_keys
        )

        raw_data_dir = raw_data_dirs.get(project.project_id)
        if raw_data_dir is None:
            raise KeyError(f"No manifest supplied for project {project.project_id!r}")

        for checker_id, requirements in routed.items():
            context = CheckContext(
                validation_run_id=validation_run_id,
                as_of=as_of,
                project=project,
                models=project_models,
                elements=project_elements,
                requirements=requirements,
                raw_data_dir=raw_data_dir,
                reports_dir=reports_dir,
            )
            outcome = registry.checker(checker_id).check(context)
            findings.extend(outcome.findings)
            failures.extend(outcome.failures)

    # Sorted here rather than trusted from the checkers: two checkers running
    # over the same models must not be able to make the finding order depend on
    # which of them was registered first.
    findings.sort(
        key=lambda finding: (
            finding.project_id,
            finding.model_key,
            finding.requirement_key,
            finding.element_key,
            finding.status,
        )
    )

    return CheckResult(findings=tuple(findings), failures=tuple(failures))
