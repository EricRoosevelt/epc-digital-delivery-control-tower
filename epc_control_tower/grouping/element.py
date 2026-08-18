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

from collections.abc import Sequence

from ..domain import (
    Finding,
    Issue,
    IssueEvent,
    IssueState,
    TopicCreatedPayload,
    derive_lifecycle_state,
)
from ..identity import build_issue_event_key, build_issue_key

__all__ = ["ElementGroupingPolicy"]

#: Version of the opening event's payload shape. Payloads are typed and
#: versioned rather than a free-form metadata bag, so a consumer can tell what
#: it is reading and a producer cannot leak whatever it had in scope.
TOPIC_CREATED_PAYLOAD_VERSION = 1


class ElementGroupingPolicy:
    """One issue per subject carrying at least one issue-bearing finding.

    The id stays ``element`` because it is published: it is written into every
    issue row and into the issue key itself, so renaming it would move keys
    that name nothing new.
    """

    id = "element"

    #: The role accountable for an issue this policy raises.
    #:
    #: A role, not a person: roles are what rule metadata can carry, and a
    #: directory of parties is a whole dimension this project does not need in
    #: order to make an issue actionable. It is a constant here only because
    #: IDS 1.0 has nowhere to state it; when declarative rules land it comes
    #: from the rule.
    default_actor_role = "model-coordination"

    def group(
        self,
        findings: Sequence[Finding],
        *,
        validation_run_id: str,
        as_of: str,
    ) -> tuple[tuple[Issue, ...], tuple[IssueEvent, ...]]:
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
                actor_role=self.default_actor_role,
                payload_version=TOPIC_CREATED_PAYLOAD_VERSION,
                typed_payload=TopicCreatedPayload(
                    finding_count=len(members),
                    title=subject,
                ),
            )
            events.append(event)

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
                    finding_keys=tuple(item.finding_key for item in members),
                    # Derived from the history just built, never asserted
                    # independently of it.
                    lifecycle_state=derive_lifecycle_state([event]),
                    assignee_role=self.default_actor_role,
                )
            )

        return tuple(issues), tuple(events)
