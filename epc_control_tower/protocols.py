"""The three extension points.

A fork adapting this project should be adding a checker, a grouping policy, or
an exporter — not editing the pipeline. These protocols are the seams that make
that possible, and each corresponds to a question somebody will want to answer
differently:

``Checker``
    *How is a requirement evaluated?* IDS is the built-in answer, but IDS 1.0
    cannot express a good deal of what real delivery requirements ask for —
    cross-model completeness, thresholds, whether a deliverable set is whole.
    Without this seam the project's ceiling is whatever IDS can say.

``GroupingPolicy``
    *What counts as one actionable issue?* Per element, per requirement, per
    model, per discipline — the answer is a project decision, not a property of
    the pipeline.

``Exporter``
    *Where do results go?* CSV, JSON, BCF, a dashboard's input contract.

Deliberately not here yet: dynamic discovery, a plugin API version separate
from the package version, and any third-party packaging contract. Those are
promises to outside code, and making them before there is outside code to keep
them for would fix the wrong details. Registration is explicit and in-tree for
now; see :mod:`~.registry`.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .domain import (
    Element,
    Finding,
    Issue,
    IssueEvent,
    Model,
    Project,
    Requirement,
    RunBundle,
)

__all__ = [
    "Artifact",
    "CheckContext",
    "CheckOutcome",
    "Checker",
    "CheckerCapabilities",
    "CheckerFailure",
    "Exporter",
    "GroupingPolicy",
]


@dataclass(frozen=True, slots=True)
class CheckerCapabilities:
    """What a checker can and cannot do.

    Declared rather than discovered so that routing a requirement to a checker
    that cannot evaluate it fails at planning time with a clear message,
    instead of part-way through a run with a confusing one.
    """

    #: Facet kinds this checker understands, e.g. ``("property", "attribute")``.
    facets: tuple[str, ...] = ()
    #: IFC schema names this checker supports, e.g. ``("IFC4",)``.
    ifc_schemas: tuple[str, ...] = ()
    #: True when the checker needs every model at once rather than one at a
    #: time — cross-model completeness rules do.
    requires_federated_context: bool = False


@dataclass(frozen=True, slots=True)
class CheckContext:
    """Everything a checker is allowed to see.

    Passing a context rather than letting checkers reach for module globals is
    what keeps them independently testable, and what stops one checker's
    configuration from leaking into another's results.
    """

    validation_run_id: str
    as_of: str
    project: Project
    models: tuple[Model, ...]
    elements: tuple[Element, ...]
    requirements: tuple[Requirement, ...]
    raw_data_dir: Path
    reports_dir: Path

    def elements_for(self, model_key: str) -> tuple[Element, ...]:
        return tuple(
            element for element in self.elements if element.model_key == model_key
        )


@dataclass(frozen=True, slots=True)
class CheckerFailure:
    """A checker could not complete.

    This exists so that a checker blowing up produces a structured, reportable
    result rather than an opaque traceback from the middle of a run. The stage
    still fails closed — a failure is not quietly tolerated — but it can say
    which checker, on which model, and why.
    """

    checker_id: str
    project_id: str
    message: str
    model_key: str = ""
    detail: str = ""

    def describe(self) -> str:
        location = f"{self.project_id}"
        if self.model_key:
            location = f"{location}/{self.model_key}"
        return f"[{self.checker_id}] {location}: {self.message}"


@dataclass(frozen=True, slots=True)
class CheckOutcome:
    findings: tuple[Finding, ...] = ()
    failures: tuple[CheckerFailure, ...] = ()


@dataclass(frozen=True, slots=True)
class Artifact:
    """One file an exporter produced."""

    path: Path
    sha256: str
    byte_count: int
    exporter_id: str = ""


class Checker(Protocol):
    """Evaluates requirements against a project's models."""

    id: str
    version: str
    capabilities: CheckerCapabilities

    def config_sha256(self) -> str:
        """Digest of this checker's configuration.

        Folded into ``validation_run_id``: reconfiguring a checker must change
        the validation identity, because it can change the findings.
        """
        ...

    def check(self, context: CheckContext) -> CheckOutcome: ...


class GroupingPolicy(Protocol):
    """Turns findings into actionable issues and their opening history."""

    id: str

    def group(
        self,
        findings: Sequence[Finding],
        *,
        validation_run_id: str,
        as_of: str,
    ) -> tuple[tuple[Issue, ...], tuple[IssueEvent, ...]]: ...


class Exporter(Protocol):
    """Writes a run's results somewhere.

    An exporter receives a :class:`~.domain.RunBundle` and nothing else. It
    does not reopen IFC files, consult checkers, or branch on rule ids — if one
    needs to, that is a sign the information belongs in the domain model.
    """

    id: str
    version: str

    def config_sha256(self) -> str: ...

    def export(self, bundle: RunBundle, output_root: Path) -> Iterable[Artifact]: ...
