"""Round 2 measurements for ADR 0005 (2026-10-01).

Same rules as round 1's ``probe.py``: run with a disposable checkout as the
working directory, scratch output under ``$PROBE_SCRATCH``. Round 1's scripts
are left exactly as audited; this module reuses their building blocks.

Commands::

    python probe_r2.py digests               # status quo digest under every edit
    python probe_r2.py bundle <edit>         # round 1's finding diff, new edits
    python probe_r2.py semantics <edit>      # which semantics digests move (O1b)
    python probe_r2.py carry <scenario>      # the four-state comparison (O1b + C)
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]

import patches  # noqa: E402
import patches_r2  # noqa: E402
import probe  # noqa: E402

# Round 1's building blocks look edits up in ``patches.EDITS``; widen it for
# this process only. Round 1's module on disk is untouched.
patches.EDITS.update(patches_r2.EDITS2)

ROOT = probe.ROOT
PROJECT = probe.PROJECT
ALL_ACTIVITIES = probe.ALL_ACTIVITIES
SCENARIOS = (
    "relax",
    "retype",
    "unrelated",
    "pre-1.7-record",
    "reissue",
    "reissue-deleted",
    "ambiguous",
)


def cmd_digests() -> None:
    probe.cmd_digests()


def cmd_bundle(edit: str) -> None:
    probe.cmd_bundle(edit)


def cmd_semantics(edit: str) -> None:
    from epc_control_tower.rules import load_ruleset

    path = ROOT / "rules" / "epc-delivery"
    before = load_ruleset(path)
    undo = patches.apply(edit, ROOT)
    try:
        after = load_ruleset(path)
    finally:
        patches.restore(undo)
    a = {r.requirement_key: r for r in before.requirements}
    b = {r.requirement_key: r for r in after.requirements}
    moved = sorted(
        f"{a[k].rule_id}/{a[k].requirement_id}"
        for k in a.keys() & b.keys()
        if getattr(a[k], "semantics_digest", "") != getattr(b[k], "semantics_digest", "")
    )
    keys = "same" if a.keys() == b.keys() else "requirement keys differ"
    digest = "moves" if before.normalized_digest != after.normalized_digest else "SAME"
    print(
        f"{edit:<20} normalized {digest:<6} {keys}; semantics_digest moved on "
        f"{len(moved)}: {moved}"
    )


# ---------------------------------------------------------------------------
# The comparison scenarios
# ---------------------------------------------------------------------------


def _reseal_without_basis(record):
    """The same record as an earlier build would have sealed it: no basis.

    Every reading keeps its ``finding_keys`` and loses ``cited_findings``; the
    record is then sealed again by the real digest function, so it passes the
    recheck's seal check exactly as a genuine pre-1.7 record would.
    """

    from epc_control_tower.purpose.assessment.record import (
        AssessmentRecord,
        build_assessment_digest,
        resolved_document,
    )

    def strip_step(step):
        return dataclasses.replace(
            step,
            readings=tuple(
                dataclasses.replace(reading, cited_findings=()) for reading in step.readings
            ),
        )

    activities = tuple(
        dataclasses.replace(
            activity,
            subscopes=tuple(
                dataclasses.replace(
                    subscope, path=tuple(strip_step(step) for step in subscope.path)
                )
                for subscope in activity.subscopes
            ),
        )
        for activity in record.activities
    )
    fields = {
        "request": record.request,
        "pack_schema_version": record.pack_schema_version,
        "composition_digest": record.composition_digest,
        "validation_run_id": record.validation_run_id,
        "ruleset_id": record.ruleset_id,
        "ruleset_version": record.ruleset_version,
        "activities": activities,
        "cited_milestones": record.cited_milestones,
        "cited_cost_parameter_names": record.cited_cost_parameter_names,
    }
    return AssessmentRecord(
        **fields, assessment_digest=build_assessment_digest(resolved_document(**fields))
    )


def _reissued(facts, *, delete: str = ""):
    """``facts`` with the HVAC model reissued: new content id, every HVAC key new.

    The findings read exactly what they read before — same element, same
    requirement, same status and text — which is the case the ADR has to decide:
    identical evidence about a *different* model version. ``delete`` removes one
    element and its findings as well.
    """

    from epc_control_tower.purpose.assessment.facts import ModelVersionFact

    marker = "fixture-content/hvac-reissued-not-a-real-export"
    models = tuple(
        ModelVersionFact(m.model_key, marker if m.model_key == "hvac" else m.content_id)
        for m in facts.models
    )
    findings = tuple(
        dataclasses.replace(f, finding_key=f"fixture-reissued/{f.finding_key}")
        if f.model_key == "hvac"
        else f
        for f in facts.findings
        if f.element_key != delete
    )
    elements = tuple(e for e in facts.elements if e.element_key != delete)
    return dataclasses.replace(
        facts,
        validation_run_id="fixture-validation-run/hvac-reissued-not-a-real-run",
        models=models,
        findings=findings,
        elements=elements,
    )


def _ambiguous(facts, element: str, requirement_key: str):
    """``facts`` plus a second finding for one (element, requirement) slot."""

    original = next(
        f
        for f in facts.findings
        if f.element_key == element and f.requirement_key == requirement_key
    )
    twin = dataclasses.replace(original, finding_key=f"fixture-twin/{original.finding_key}")
    return dataclasses.replace(
        facts,
        findings=tuple(
            sorted(
                facts.findings + (twin,),
                key=lambda f: (f.element_key, f.requirement_key, f.finding_key),
            )
        ),
    )


def cmd_carry(scenario: str) -> None:
    import assessment_fixtures as fx
    from epc_control_tower.purpose import assess_purpose, facts_from_bundle, recheck_purpose

    duct = fx.HVAC_DUCT
    b0 = probe.build("before")
    f0 = facts_from_bundle(b0, PROJECT)
    names = probe.labels(b0)
    prior = assess_purpose(
        request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=f0),
        composed=probe.compose(b0),
        facts=f0,
        determinations=fx.fixture_determinations(facts=f0),
    )
    determinations = fx.fixture_determinations
    edit = {
        "relax": "r005a-optional",
        "retype": "r005a-datatype",
        "unrelated": "r002-datatype",
        "pre-1.7-record": "r002-datatype",
    }.get(scenario, "")
    if edit:
        b1 = probe.with_edit(edit, "after")
        f1 = facts_from_bundle(b1, PROJECT)
        composed = probe.compose(b1)
    else:
        f1, composed = f0, probe.compose(b0)
    if scenario == "pre-1.7-record":
        prior = _reseal_without_basis(prior)
    if scenario == "reissue":
        f1 = _reissued(f0)
    if scenario == "reissue-deleted":
        f1 = _reissued(f0, delete=duct)
    if scenario == "ambiguous":
        key = next(
            r.requirement_key
            for r in b0.ruleset.requirements
            if r.rule_id == "R-005A" and r.requirement_id.endswith("AssetTag")
        )
        f1 = _ambiguous(f0, duct, key)
    offered = () if scenario.startswith("reissue") else determinations(facts=f1)

    succeeds = tuple(
        (activity.activity_ref, subscope.ordinal)
        for activity in prior.activities
        for subscope in activity.subscopes
    )
    record = recheck_purpose(
        prior=prior,
        request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=f1),
        composed=composed,
        facts=f1,
        determinations=offered,
        succeeds=succeeds,
    )
    s0 = {f.finding_key: f for f in f0.findings}
    print(f"scenario: {scenario}" + (f" (edit {edit})" if edit else ""))
    print(f"context is_current: {record.successor.context.is_current}")
    counts: dict[str, int] = {}
    for outcome in record.successor.outcomes:
        for row in outcome.carry_over:
            counts[f"{row.citation_kind}:{row.state}"] = (
                counts.get(f"{row.citation_kind}:{row.state}", 0) + 1
            )
            if row.citation_kind != "finding":
                continue
            was = s0.get(row.citation)
            label = names.get(was.requirement_key, "?") if was else "?"
            element = was.element_key if was else "?"
            extra = []
            if row.key_changed:
                extra.append(f"key_changed={row.key_changed}")
            if row.changed_aspects:
                extra.append(f"aspects={list(row.changed_aspects)}")
            if row.cause:
                extra.append(f"cause={row.cause[:60]}")
            print(
                f"  {probe.short(outcome.activity_ref)} #{outcome.subscope_ordinal} "
                f"{row.citation[:8]} {element} {label}: {row.state} / {row.reason}"
                + (f" [{'; '.join(extra)}]" if extra else "")
            )
    print(f"totals: {dict(sorted(counts.items()))}")
    any_carried = any(
        "carried" in row.as_document()
        for outcome in record.successor.outcomes
        for row in outcome.carry_over
    )
    print(f"any row still carries a boolean 'carried': {any_carried}")


def main(argv: list[str]) -> None:
    command, *rest = argv
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
    {
        "digests": cmd_digests,
        "bundle": cmd_bundle,
        "semantics": cmd_semantics,
        "carry": cmd_carry,
    }[command](*rest)
    sys.stdout.flush()


if __name__ == "__main__":
    main(sys.argv[1:])
