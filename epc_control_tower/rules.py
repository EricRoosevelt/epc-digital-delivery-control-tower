"""Loading a rule set from whatever document declares it.

Loading rules and evaluating them are separate jobs, and keeping them separate
is what stops one rule language from shaping the pipeline. The orchestrator
loads a rule set here — it needs the requirements to compute the validation
identity and to route work — and never learns how any particular checker
evaluates them. A checker that needs its source document again reads it itself.

Dispatch is on the document's extension. There is exactly one format today;
this exists so that adding the declarative rule definitions of the next phase
is a new branch here rather than a change to every caller.
"""

from __future__ import annotations

from pathlib import Path

from .domain import RuleSet

__all__ = ["load_ruleset"]


def load_ruleset(path: Path, *, ruleset_id: str = "ids") -> RuleSet:
    """Read a rule document and return the rule set it declares."""

    suffix = path.suffix.lower()
    if suffix == ".ids":
        from .checkers.ids_checker import load_ids_ruleset

        return load_ids_ruleset(path, ruleset_id=ruleset_id)
    raise ValueError(
        f"No rule loader for {path.name}: unsupported rule document format {suffix!r}"
    )
