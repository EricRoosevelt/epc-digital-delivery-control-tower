"""Grouping by subject: one issue per thing that has something wrong with it.

What counts as *one actionable issue* is a project decision, not a property of
the pipeline. Per element is the answer this project has always used — somebody
walks up to a duct segment and fixes everything wrong with it at once — but per
requirement, per model or per discipline are all defensible, which is why this
is a policy behind a protocol rather than a loop in the exporter.

"Per element" is now stated more exactly as *per subject*: the element a
finding names, or the model, when the finding is that something is absent and
there is no element to name. See :class:`~..domain.Finding` for why such a
finding exists at all. Grouping by element alone would have left those failures
in no issue, and a failure that reaches no issue is a failure nobody is told
about — which is a far worse outcome than a slightly wider policy.

Two things the previous implementation did are deliberately not reproduced.

It asserted that grouping produced exactly three topics of exactly two findings
each. That assertion was written against a fixture, and a fourth model or a
fixed duct segment would have failed the pipeline rather than the data. The
invariant worth keeping is that every issue covers at least one finding and
that every finding it names is an issue-bearing one; the counts belong in the
characterization tests, where they can be refreshed deliberately.

It also had no notion of history. An issue's state was a constant string. Here
grouping emits the opening event, and :attr:`~..domain.Issue.lifecycle_state`
is derived from the event stream and checked against it — which is what makes
ageing, overdue and burndown answerable later instead of unrepresentable.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from ..domain import (
    Finding,
    Issue,
    IssueEvent,
    IssueState,
    Requirement,
    Severity,
    TopicCreatedPayload,
    derive_is_overdue,
    derive_lifecycle_state,
    parse_instant,
)
from ..identity import build_issue_event_key, build_issue_key

__all__ = ["ElementGroupingPolicy"]

#: Version of the opening event's payload shape. Payloads are typed and
#: versioned rather than a free-form metadata bag, so a consumer can tell what
#: it is reading and a producer cannot leak whatever it had in scope.
TOPIC_CREATED_PAYLOAD_VERSION = 1

#: Worst first. `Severity` is a `StrEnum`, so its members sort
#: alphabetically — ERROR before WARNING by luck rather than by meaning —
#: and relying on that would put INFO between them the moment a fourth level
#: appeared.
_SEVERITY_RANK = {
    Severity.ERROR: 3,
    Severity.WARNING: 2,
    Severity.INFO: 1,
}


def _labels(requirements: Sequence[Requirement]) -> tuple[str, ...]:
    """The deterministic union of every member rule's labels.

    Disciplines a rule binds, then the labels it declares, across *all* the
    rules that failed on this subject — not only the one whose metadata decides
    priority. A coordinator triaging by the worst thing wrong still wants to see
    that the same element also tripped an architecture rule, so an issue's
    labels are the union, ordered by requirement key then by first appearance so
    the result is the same on every run.
    """

    seen: list[str] = []
    for requirement in sorted(requirements, key=lambda item: item.requirement_key):
        for label in (*requirement.discipline_scope, *requirement.labels):
            if label and label not in seen:
                seen.append(label)
    return tuple(seen)


class ElementGroupingPolicy:
    """One issue per subject carrying at least one issue-bearing finding.

    The id stays ``element`` because it is published: it is written into every
    issue row and into the issue key itself, so renaming it would move keys
    that name nothing new.
    """

    id = "element"
    version = "1.0.0"

    def config_sha256(self) -> str:
        # This policy has no configuration: what it groups on and how it decides
        # are fixed. An empty digest says exactly that, and folds into the
        # artifact identity the same way a checker's does.
        return ""

    #: Used only when a finding's requirement names no owner. A role, not a
    #: person: roles are what rule metadata carries, and a directory of
    #: parties is a whole dimension this project does not need in order to
    #: make an issue actionable.
    #:
    #: It was the *only* source of an assignee until the rules could state
    #: one. Every issue in the shipped fixture took its value from here,
    #: which meant the published BCF archive's AssignedTo was a constant in
    #: this file wearing the costume of a derivation.
    default_actor_role = "model-coordination"

    @staticmethod
    def _deciding(
        members: Sequence[Finding],
        requirements: Mapping[str, Requirement],
        due_of,
    ) -> tuple[Requirement | None, str]:
        """Which requirement's metadata an issue takes, and its deadline.

        An issue can gather failures of several rules against one element, and
        they may disagree about who owns it, how urgent it is, and — the reason
        this is not a tie-break formality — *when it is due*. Choosing by
        severity alone lets a future-dated high-severity rule hide a
        lower-severity rule that is already overdue on the same element, which
        is exactly the deadline a coordinator must not miss.

        So the order is:

        1. Among the rules that carry a deadline, the **earliest due** decides.
           A ties on the same instant are broken by severity descending, then
           requirement key ascending.
        2. Only when *every* member rule is deadline-free does the old order
           apply — severity descending, then requirement key — because there is
           then no deadline to protect and the worst thing wrong should lead.

        Returns the deciding requirement and the issue's ``due`` (the earliest
        deadline, or empty when all members are deadline-free).
        """

        ranked = [
            requirement
            for requirement in (
                requirements.get(member.requirement_key) for member in members
            )
            if requirement is not None
        ]
        if not ranked:
            return None, ""

        with_deadline = [
            (requirement, due_of(requirement.stage))
            for requirement in ranked
        ]
        dated = [(r, due) for (r, due) in with_deadline if due]
        if dated:
            deciding, due = min(
                dated,
                key=lambda item: (
                    parse_instant(item[1], "due"),
                    -_SEVERITY_RANK.get(item[0].severity, 0),
                    item[0].requirement_key,
                ),
            )
            return deciding, due

        deciding = min(
            ranked,
            key=lambda item: (-_SEVERITY_RANK.get(item.severity, 0), item.requirement_key),
        )
        return deciding, ""

    def group(
        self,
        findings: Sequence[Finding],
        *,
        validation_run_id: str,
        as_of: str,
        requirements: Mapping[str, Requirement] | None = None,
        programmes: Mapping[str, Mapping[str, str]] | None = None,
    ) -> tuple[tuple[Issue, ...], tuple[IssueEvent, ...]]:
        by_key = dict(requirements or {})
        programme_by_project = {
            project_id: dict(stages) for project_id, stages in (programmes or {}).items()
        }
        grouped: dict[str, list[Finding]] = {}
        for finding in findings:
            if not finding.is_issue:
                continue
            # The element when there is one, the model when the finding is that
            # something is missing and no element can stand for it. The two can
            # never collide: an element_key always begins with its model_key and
            # a separator, so it is never equal to a bare model_key.
            grouped.setdefault(finding.element_key or finding.model_key, []).append(
                finding
            )

        issues: list[Issue] = []
        events: list[IssueEvent] = []

        for subject in sorted(grouped):
            members = sorted(grouped[subject], key=lambda item: item.finding_key)
            first = members[0]

            # A stage's deadline comes from the project that owns this subject,
            # never a global table. Only an *empty* stage means "no deadline". A
            # non-empty stage the project's programme does not date — whether
            # because the whole programme is missing or only that stage is — is a
            # coverage gap, and it fails closed here rather than silently reading
            # as "not due". The pipeline validates coverage before grouping, so
            # this is a backstop that should never fire in a whole run.
            def due_of(stage: str, project_id: str = first.project_id) -> str:
                if not stage:
                    return ""
                stated = programme_by_project.get(project_id, {})
                if stage in stated:
                    return stated[stage]
                raise ValueError(
                    f"grouping: project {project_id!r} has no milestone for stage "
                    f"{stage!r}; programme coverage must be validated before grouping"
                )

            deciding, due = self._deciding(members, by_key, due_of)
            member_requirements = [
                by_key[member.requirement_key]
                for member in members
                if member.requirement_key in by_key
            ]
            issue_key = build_issue_key(
                validation_run_id=validation_run_id,
                grouping_policy=self.id,
                group_ref=subject,
            )

            event = IssueEvent(
                event_key=build_issue_event_key(
                    issue_key=issue_key,
                    sequence=1,
                    event_type=TopicCreatedPayload.event_type,
                ),
                issue_key=issue_key,
                sequence=1,
                occurred_at=as_of,
                event_type=TopicCreatedPayload.event_type,
                from_state=None,
                to_state=IssueState.OPEN,
                actor_role=(
                    deciding.owner_role
                    if deciding is not None and deciding.owner_role
                    else self.default_actor_role
                ),
                payload_version=TOPIC_CREATED_PAYLOAD_VERSION,
                typed_payload=TopicCreatedPayload(
                    finding_count=len(members),
                    title=subject,
                ),
            )
            events.append(event)

            lifecycle_state = derive_lifecycle_state([event])
            issues.append(
                Issue(
                    issue_key=issue_key,
                    validation_run_id=validation_run_id,
                    project_id=first.project_id,
                    model_key=first.model_key,
                    # Empty for a model-level issue, which is the same blank the
                    # findings carry and means the same thing: there is no
                    # element, not that one was omitted.
                    element_key=first.element_key,
                    grouping_policy=self.id,
                    # The run-free subject this policy grouped on: the element,
                    # or the model when there is no element. Persisted so
                    # `issue_key` and the topic identity can be recomputed.
                    group_ref=subject,
                    finding_keys=tuple(item.finding_key for item in members),
                    # Derived from the history just built, never asserted
                    # independently of it.
                    lifecycle_state=lifecycle_state,
                    # From the rule now, not from a constant on this class.
                    assignee_role=(
                        deciding.owner_role
                        if deciding is not None and deciding.owner_role
                        else self.default_actor_role
                    ),
                    priority=deciding.priority if deciding is not None else "",
                    stage=deciding.stage if deciding is not None else "",
                    due=due,
                    # Not a clock reading, and offset-aware: `as_of` is the run's
                    # logical date and `due` a programme date, compared as
                    # instants and never as strings. A resolved or closed issue
                    # is never overdue.
                    is_overdue=derive_is_overdue(
                        as_of=as_of, due=due, lifecycle_state=lifecycle_state
                    ),
                    # The union of every member rule's labels, not only the
                    # deciding rule's — the other rules failed on this subject
                    # too and a coordinator wants to see them.
                    labels=_labels(member_requirements),
                )
            )

        return tuple(issues), tuple(events)
