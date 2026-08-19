"""Cross-entity invariants for a run bundle.

:mod:`~.domain` enforces what a single object can know about itself. This
module enforces what only the whole picture can show: that references resolve,
that keys are what they claim to be, and that an issue's stated lifecycle
matches its own history.

The distinction matters for identity in particular. A ``finding_key`` is a
UUIDv5 over its inputs, so it can be recomputed and compared rather than
trusted — and the same goes for ``validation_run_id``, which is why
:class:`~.domain.ValidationRun` carries the inputs that produced it. An
identity nobody ever recomputes is just a label that happens to look like a
hash.
"""

from __future__ import annotations

from collections.abc import Iterable

from .domain import (
    RunBundle,
    derive_lifecycle_state,
)
from .identity import (
    build_finding_key,
    build_issue_event_key,
    build_ruleset_normalized_digest,
    build_validation_run_id,
)

__all__ = ["BundleInvariantError", "validate_bundle"]


class BundleInvariantError(ValueError):
    """A run bundle violated one or more cross-entity invariants.

    Carries every violation rather than only the first, because when a
    refactor breaks something it is usually more useful to see the shape of the
    breakage than its alphabetically earliest instance.
    """

    def __init__(self, violations: Iterable[str]) -> None:
        self.violations = list(violations)
        joined = "\n  - ".join(self.violations)
        super().__init__(f"{len(self.violations)} bundle invariant violation(s):\n  - {joined}")


def _duplicates(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def validate_bundle(bundle: RunBundle, *, recompute_identity: bool = True) -> None:
    """Check every cross-entity invariant, raising once with all violations.

    ``recompute_identity`` exists for the legacy adapters, whose keys come from
    frozen pre-split derivations and therefore will not match the current ones.
    Everything structural is still checked for them.
    """

    violations: list[str] = []

    # -- uniqueness --------------------------------------------------------

    for label, values in (
        ("project_id", [p.project_id for p in bundle.projects]),
        ("model_key", [m.model_key for m in bundle.models]),
        ("element_key", [e.element_key for e in bundle.elements]),
        ("finding_key", [f.finding_key for f in bundle.findings]),
        ("issue_key", [i.issue_key for i in bundle.issues]),
        ("event_key", [e.event_key for e in bundle.issue_events]),
        ("geometry element_key", [g.element_key for g in bundle.geometry]),
    ):
        repeated = _duplicates(values)
        if repeated:
            violations.append(f"duplicate {label} values: {repeated}")

    # A model_id only has to be unique inside its own project; a model_key has
    # to be unique everywhere. That asymmetry is the whole point of the split,
    # so it is worth checking rather than assuming.
    for project in bundle.projects:
        scoped = [
            m.model_id for m in bundle.models if m.project_id == project.project_id
        ]
        repeated = _duplicates(scoped)
        if repeated:
            violations.append(
                f"project {project.project_id}: duplicate model_id values {repeated}"
            )

    project_ids = {p.project_id for p in bundle.projects}
    model_keys = {m.model_key for m in bundle.models}
    element_keys = {e.element_key for e in bundle.elements}
    finding_keys = {f.finding_key for f in bundle.findings}
    issue_keys = {i.issue_key for i in bundle.issues}
    requirement_keys = {r.requirement_key for r in bundle.ruleset.requirements}

    # -- referential integrity --------------------------------------------

    for model in bundle.models:
        if model.project_id not in project_ids:
            violations.append(
                f"model {model.model_key}: unknown project_id {model.project_id!r}"
            )

    for element in bundle.elements:
        if element.model_key not in model_keys:
            violations.append(
                f"element {element.element_key}: unknown model_key {element.model_key!r}"
            )

    for finding in bundle.findings:
        if finding.project_id not in project_ids:
            violations.append(
                f"finding {finding.finding_key}: unknown project_id {finding.project_id!r}"
            )
        if finding.model_key not in model_keys:
            violations.append(
                f"finding {finding.finding_key}: unknown model_key {finding.model_key!r}"
            )
        if finding.element_key and finding.element_key not in element_keys:
            violations.append(
                f"finding {finding.finding_key}: unknown element_key {finding.element_key!r}"
            )
        if finding.requirement_key not in requirement_keys:
            violations.append(
                f"finding {finding.finding_key}: unknown requirement_key "
                f"{finding.requirement_key!r}"
            )
        if finding.validation_run_id != bundle.run.validation_run_id:
            violations.append(
                f"finding {finding.finding_key}: belongs to run "
                f"{finding.validation_run_id!r}, bundle is "
                f"{bundle.run.validation_run_id!r}"
            )

    for issue in bundle.issues:
        if issue.model_key not in model_keys:
            violations.append(f"issue {issue.issue_key}: unknown model_key {issue.model_key!r}")
        unknown = sorted(set(issue.finding_keys) - finding_keys)
        if unknown:
            violations.append(f"issue {issue.issue_key}: unknown finding_keys {unknown}")
        if issue.validation_run_id != bundle.run.validation_run_id:
            violations.append(
                f"issue {issue.issue_key}: belongs to run {issue.validation_run_id!r}, "
                f"bundle is {bundle.run.validation_run_id!r}"
            )

    for event in bundle.issue_events:
        if event.issue_key not in issue_keys:
            violations.append(
                f"event {event.event_key}: orphaned, no issue {event.issue_key!r}"
            )

    # Geometry is sparse by design, so its absence says nothing. Geometry for
    # an element the bundle does not contain, on the other hand, means a camera
    # was placed by looking somewhere the register never went.
    for geometry in bundle.geometry:
        if geometry.element_key not in element_keys:
            violations.append(
                f"geometry: unknown element_key {geometry.element_key!r}"
            )

    # -- lifecycle state is derived, not asserted --------------------------

    for issue in bundle.issues:
        events = bundle.events_for(issue.issue_key)
        if not events:
            violations.append(f"issue {issue.issue_key}: has no events")
            continue
        try:
            derived = derive_lifecycle_state(events)
        except ValueError as exc:
            violations.append(f"issue {issue.issue_key}: malformed history: {exc}")
            continue
        if derived is not issue.lifecycle_state:
            violations.append(
                f"issue {issue.issue_key}: lifecycle_state is {issue.lifecycle_state} "
                f"but its history derives {derived}"
            )

    # -- identity is recomputed, not trusted -------------------------------

    for issue in bundle.issues:
        # `is_overdue` is derived, so it is checked against its inputs rather
        # than trusted — the same treatment `lifecycle_state` gets, and for the
        # same reason: a recorded derivation nobody re-checks is a second source
        # of truth waiting to disagree with the first.
        expected_overdue = bool(issue.due) and bundle.run.as_of > issue.due
        if issue.is_overdue != expected_overdue:
            violations.append(
                f"issue {issue.issue_key}: is_overdue={issue.is_overdue} but "
                f"as_of {bundle.run.as_of!r} against due {issue.due!r} derives "
                f"{expected_overdue}"
            )

    if recompute_identity:
        # The rule set's semantic digest is recomputed from the requirements it
        # actually carries, so a bundle cannot claim rules it does not contain.
        expected_digest = build_ruleset_normalized_digest(
            ruleset_id=bundle.ruleset.ruleset_id,
            version=bundle.ruleset.version,
            requirements=bundle.ruleset.requirements,
            milestones=bundle.ruleset.milestones,
        )
        if expected_digest != bundle.ruleset.normalized_digest:
            violations.append(
                f"ruleset normalized_digest {bundle.ruleset.normalized_digest!r} "
                f"does not recompute from its own requirements "
                f"(expected {expected_digest!r})"
            )
        if bundle.run.ruleset_normalized_digest != bundle.ruleset.normalized_digest:
            violations.append(
                "the run's ruleset digest "
                f"{bundle.run.ruleset_normalized_digest!r} disagrees with the "
                f"bundle's rule set {bundle.ruleset.normalized_digest!r}"
            )

        expected_run_id = build_validation_run_id(
            ruleset_id=bundle.run.ruleset_id,
            ruleset_version=bundle.run.ruleset_version,
            ruleset_normalized_digest=bundle.run.ruleset_normalized_digest,
            models=bundle.run.model_inputs,
            checkers=bundle.run.checker_fingerprints,
            as_of=bundle.run.as_of,
        )
        if expected_run_id != bundle.run.validation_run_id:
            violations.append(
                f"validation_run_id {bundle.run.validation_run_id!r} does not "
                f"recompute from its own recorded inputs (expected {expected_run_id!r})"
            )

        for finding in bundle.findings:
            expected = build_finding_key(
                validation_run_id=finding.validation_run_id,
                model_key=finding.model_key,
                requirement_key=finding.requirement_key,
                element_key=finding.element_key,
            )
            if expected != finding.finding_key:
                violations.append(
                    f"finding_key {finding.finding_key!r} does not recompute "
                    f"(expected {expected!r})"
                )

        for event in bundle.issue_events:
            expected = build_issue_event_key(
                issue_key=event.issue_key,
                sequence=event.sequence,
                event_type=event.event_type,
            )
            if expected != event.event_key:
                violations.append(
                    f"event_key {event.event_key!r} does not recompute "
                    f"(expected {expected!r})"
                )

    # -- run inputs must describe the models actually present --------------

    recorded_inputs = dict(bundle.run.model_inputs)
    for model in bundle.models:
        recorded = recorded_inputs.get(model.model_key)
        if recorded is None:
            violations.append(
                f"model {model.model_key}: not recorded in the run's model inputs, "
                "so the validation identity does not cover it"
            )
        elif recorded != model.provenance.content_sha256:
            violations.append(
                f"model {model.model_key}: run input hash {recorded!r} disagrees "
                f"with its provenance {model.provenance.content_sha256!r}"
            )

    if violations:
        raise BundleInvariantError(violations)
