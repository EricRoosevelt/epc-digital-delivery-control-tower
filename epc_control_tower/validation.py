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

from collections.abc import Iterable, Mapping

from .domain import (
    Requirement,
    RunBundle,
    derive_is_overdue,
    derive_lifecycle_state,
)
from .identity import (
    build_finding_key,
    build_issue_event_key,
    build_issue_key,
    build_ruleset_normalized_digest,
    build_topic_guid,
    build_validation_run_id,
)

__all__ = [
    "BundleInvariantError",
    "programme_coverage_gaps",
    "validate_bundle",
]


def programme_coverage_gaps(
    requirements: Iterable[Requirement],
    project_ids: Iterable[str],
    programmes: Mapping[str, Mapping[str, str]],
) -> list[str]:
    """Where a project's programme fails to date a stage a rule uses.

    Every non-empty ``Requirement.stage`` must be a *present* key in every
    project's programme — present, not merely truthy, so a stage stated with an
    empty ``due`` counts as covered while a stage nobody stated is a gap. The
    result is the list of gaps, empty when coverage is complete, so a caller can
    fail closed with all of them named at once.
    """

    needed = sorted({requirement.stage for requirement in requirements if requirement.stage})
    gaps: list[str] = []
    for project_id in sorted(set(project_ids)):
        stated = programmes.get(project_id, {})
        for stage in needed:
            if stage not in stated:
                gaps.append(
                    f"project {project_id!r} has no milestone for stage {stage!r}"
                )
    return gaps


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

    # Two issues that project to the same BCF topic GUID would overwrite one
    # another in the archive, so the collision is rejected here — before any
    # exporter runs — as well as in the exporter itself. The GUID is run-free
    # (policy, project, group_ref), so this is the structural guarantee that a
    # finer grouping policy cannot silently merge two subjects onto one topic.
    topic_guids: dict[str, str] = {}
    for issue in bundle.issues:
        guid = build_topic_guid(
            grouping_policy=issue.grouping_policy,
            project_id=issue.project_id,
            group_ref=issue.group_ref,
        )
        if guid in topic_guids:
            violations.append(
                f"topic GUID collision: issues {topic_guids[guid]!r} and "
                f"{issue.issue_key!r} both derive {guid}"
            )
        else:
            topic_guids[guid] = issue.issue_key

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

    # -- programme is well-formed and covers every rule stage ---------------

    milestone_seen: set[tuple[str, str]] = set()
    programmes: dict[str, dict[str, str]] = {}
    for milestone in bundle.project_milestones:
        pair = (milestone.project_id, milestone.stage)
        if pair in milestone_seen:
            violations.append(
                f"duplicate milestone for project {milestone.project_id!r} stage "
                f"{milestone.stage!r}"
            )
        milestone_seen.add(pair)
        if milestone.project_id not in project_ids:
            violations.append(
                f"milestone names unknown project_id {milestone.project_id!r}"
            )
        programmes.setdefault(milestone.project_id, {})[milestone.stage] = milestone.due

    for gap in programme_coverage_gaps(
        bundle.ruleset.requirements,
        [project.project_id for project in bundle.projects],
        programmes,
    ):
        violations.append(gap)

    for issue in bundle.issues:
        # `due` and `is_overdue` are both derived, so they are recomputed here
        # rather than trusted. `due` is looked up from the project's programme
        # by the issue's stage — not read off the issue — so erasing the field
        # cannot forge "no deadline": the programme still says one is due. An
        # empty stage means no deadline and is the only way `due` is legitimately
        # empty. A stage the programme does not cover is caught above.
        stated = programmes.get(issue.project_id, {})
        if not issue.stage:
            expected_due = ""
        elif issue.stage in stated:
            expected_due = stated[issue.stage]
        else:
            # The coverage check above already recorded the gap; skip the
            # per-issue derivation rather than pile on a second message.
            continue
        if issue.due != expected_due:
            violations.append(
                f"issue {issue.issue_key}: due {issue.due!r} does not match its "
                f"programme (project {issue.project_id!r} stage {issue.stage!r} is "
                f"due {expected_due!r})"
            )
            continue
        expected_overdue = derive_is_overdue(
            as_of=bundle.run.as_of,
            due=expected_due,
            lifecycle_state=issue.lifecycle_state,
        )
        if issue.is_overdue != expected_overdue:
            violations.append(
                f"issue {issue.issue_key}: is_overdue={issue.is_overdue} but "
                f"as_of {bundle.run.as_of!r} against due {expected_due!r} in state "
                f"{issue.lifecycle_state} derives {expected_overdue}"
            )

    if recompute_identity:
        # The rule set's semantic digest is recomputed from the requirements it
        # actually carries, so a bundle cannot claim rules it does not contain.
        expected_digest = build_ruleset_normalized_digest(
            ruleset_id=bundle.ruleset.ruleset_id,
            version=bundle.ruleset.version,
            requirements=bundle.ruleset.requirements,
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

        for issue in bundle.issues:
            # The issue key folds the run, the grouping policy and the run-free
            # group reference. Recomputing it here is what makes the persisted
            # `group_ref` trustworthy: a forged reference no longer keys the
            # issue it claims to.
            expected_issue = build_issue_key(
                validation_run_id=issue.validation_run_id,
                grouping_policy=issue.grouping_policy,
                group_ref=issue.group_ref,
            )
            if expected_issue != issue.issue_key:
                violations.append(
                    f"issue_key {issue.issue_key!r} does not recompute from its "
                    f"policy {issue.grouping_policy!r} and group_ref "
                    f"{issue.group_ref!r} (expected {expected_issue!r})"
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
