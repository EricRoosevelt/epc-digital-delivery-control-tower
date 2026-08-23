"""Group: findings become actionable issues and the history that opened them.

Thin on purpose. The decision this stage embodies — what counts as one issue —
belongs to a :class:`~..protocols.GroupingPolicy`, and the stage's whole job is
to look one up by the id the run configuration names and hand it the findings.

What it does add is a consistency check on the way out: an issue's stated
lifecycle state has to fold out of its own events. Doing it here means a policy
that emits a history and a state that disagree fails immediately, at the point
the mistake was made, rather than in a downstream exporter or, worse, in a
published artifact.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from ..domain import (
    Finding,
    Issue,
    IssueEvent,
    Requirement,
    derive_lifecycle_state,
)
from ..registry import Registry

__all__ = ["GroupResult", "group"]


@dataclass(frozen=True, slots=True)
class GroupResult:
    issues: tuple[Issue, ...] = ()
    events: tuple[IssueEvent, ...] = ()


def group(
    findings: Sequence[Finding],
    *,
    registry: Registry,
    policy_id: str,
    validation_run_id: str,
    as_of: str,
    requirements: Sequence[Requirement] = (),
    programmes: Mapping[str, Mapping[str, str]] | None = None,
) -> GroupResult:
    policy = registry.grouping_policy(policy_id)
    # A policy that wants rule metadata or a project's programme is handed both;
    # one that does not can ignore them. Passing them in rather than letting the
    # policy load them keeps grouping a pure function of the bundle it is given.
    issues, events = policy.group(
        findings,
        validation_run_id=validation_run_id,
        as_of=as_of,
        requirements={
            requirement.requirement_key: requirement for requirement in requirements
        },
        programmes=programmes or {},
    )

    events_by_issue: dict[str, list[IssueEvent]] = {}
    for event in events:
        events_by_issue.setdefault(event.issue_key, []).append(event)

    for issue in issues:
        history = events_by_issue.get(issue.issue_key)
        if not history:
            raise ValueError(
                f"Policy {policy_id!r} produced issue {issue.issue_key} with no history"
            )
        derived = derive_lifecycle_state(history)
        if derived is not issue.lifecycle_state:
            raise ValueError(
                f"Policy {policy_id!r}: issue {issue.issue_key} claims "
                f"{issue.lifecycle_state} but its history derives {derived}"
            )

    issue_keys = {issue.issue_key for issue in issues}
    orphans = sorted(set(events_by_issue) - issue_keys)
    if orphans:
        raise ValueError(f"Policy {policy_id!r} produced events for no issue: {orphans}")

    return GroupResult(
        issues=tuple(sorted(issues, key=lambda item: item.issue_key)),
        events=tuple(
            sorted(events, key=lambda item: (item.issue_key, item.sequence))
        ),
    )
