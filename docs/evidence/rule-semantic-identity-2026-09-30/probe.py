"""Measurements for ADR 0005 — rule semantic identity and evidence carry-over.

Run with a *disposable* checkout as the working directory; everything imported
comes from that checkout (``epc_control_tower`` and the test fixtures under
``tests/``), so a patch applied there is what gets measured. Scratch output goes
to ``$PROBE_SCRATCH``, which must be outside the checkout.

Commands::

    python probe.py digests                 # normalized digest under every edit
    python probe.py bundle <edit>           # finding keys and statuses, before/after
    python probe.py recheck <edit>          # the real assess -> recheck chain
    python probe.py compose                 # does the fixture Overlay compose?
    python probe.py guard [<edit>]          # the snapshot's version guard
    python probe.py guard-record            # record the current digest (synthetic)
    python probe.py published <pristine>    # generated tree vs a pristine copy
"""

from __future__ import annotations

import csv
import io
import json
import os
import sys
import uuid
import zipfile
from pathlib import Path

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / "tests"), str(HERE)]

import patches  # noqa: E402

SCRATCH = Path(os.environ["PROBE_SCRATCH"])
ALL_ACTIVITIES = (
    "schedules-and-room-data-sheets",
    "ceiling-and-bulkhead-geometry",
    "builders-work-openings",
)
PROJECT = "pcert-sample"


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------


def build(tag: str):
    """A fresh run: fresh config, fresh registry, reports outside the checkout."""

    from epc_control_tower.config import load_run_config
    from epc_control_tower.pipeline import build_bundle

    reports = SCRATCH / f"reports-{tag}-{uuid.uuid4().hex[:8]}"
    reports.mkdir(parents=True)
    return build_bundle(load_run_config(ROOT), reports_dir=reports).bundle


def with_edit(edit: str, tag: str):
    undo = patches.apply(edit, ROOT)
    try:
        return build(tag)
    finally:
        patches.restore(undo)


def rule_definition_digests(edit: str = "") -> dict[str, str]:
    """``rule_id -> sha256`` of each parsed rule definition, as declared.

    Probe-side only: this is what the rule *says*, read straight from the rule
    files, so a citation can be checked against it without trusting any digest
    the code under test computes.
    """

    import dataclasses
    import hashlib

    from epc_control_tower.rule_definitions import load_rule_definitions

    undo = patches.apply(edit, ROOT) if edit else []
    try:
        definition = load_rule_definitions(ROOT / "rules" / "epc-delivery")
    finally:
        patches.restore(undo)
    return {
        rule.rule_id: hashlib.sha256(
            json.dumps(dataclasses.asdict(rule), sort_keys=True, default=str).encode()
        ).hexdigest()
        for rule in definition.rules
    }


def labels(bundle) -> dict[str, str]:
    return {
        r.requirement_key: f"{r.rule_id}/{r.requirement_id}"
        for r in bundle.ruleset.requirements
    }


def by_slot(bundle) -> dict[tuple[str, str, str], object]:
    return {(f.model_key, f.element_key, f.requirement_key): f for f in bundle.findings}


def compose(bundle):
    import assessment_fixtures as fx
    from epc_control_tower.purpose import (
        compose_purpose_inputs,
        load_purpose_pack,
        read_overlay_table,
    )

    keys = {
        (bundle.ruleset.ruleset_id, bundle.ruleset.version): frozenset(
            r.requirement_key for r in bundle.ruleset.requirements
        )
    }
    overlay = read_overlay_table(fx.fixture_overlay_document(), Path(fx.__file__))
    return compose_purpose_inputs(
        project_id=PROJECT,
        overlay=overlay,
        packs=(load_purpose_pack(fx.PACK_PATH),),
        requirement_keys_by_ruleset=keys,
    )


def short(activity_ref: str) -> str:
    return activity_ref.split("::", 1)[1]


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_digests() -> None:
    from epc_control_tower.rules import load_ruleset

    frozen = load_ruleset(ROOT / "ids" / "epc_delivery_requirements_v0.1.ids")
    print(
        f"frozen legacy rule set v{frozen.version} normalized_digest {frozen.normalized_digest}"
    )
    path = ROOT / "rules" / "epc-delivery"
    base = load_ruleset(path)
    print(f"base normalized_digest {base.normalized_digest}")
    print(f"base source_blob_sha256 {base.source_blob_sha256!r}")
    for edit in patches.EDITS:
        undo = patches.apply(edit, ROOT)
        try:
            digest = load_ruleset(path).normalized_digest
        finally:
            patches.restore(undo)
        verdict = "SAME" if digest == base.normalized_digest else "moves"
        print(f"  {edit:<20} {verdict:<6} {digest[:16]}")


def cmd_bundle(edit: str) -> None:
    before = build("before")
    after = with_edit(edit, "after")
    names = labels(before)
    print(f"edit: {edit}")
    print(f"validation_run_id  {before.run.validation_run_id} -> {after.run.validation_run_id}")
    print(
        f"normalized_digest  {before.ruleset.normalized_digest[:16]} -> "
        f"{after.ruleset.normalized_digest[:16]}"
    )
    a, b = by_slot(before), by_slot(after)
    common = sorted(set(a) & set(b))
    kept = sum(1 for s in common if a[s].finding_key == b[s].finding_key)
    print(
        f"findings {len(a)} -> {len(b)}; slots in both {len(common)}; "
        f"finding_key identical {kept}/{len(common)}"
    )
    flipped = [s for s in common if a[s].status != b[s].status]
    reworded = [
        s
        for s in common
        if a[s].status == b[s].status
        and (a[s].expected, a[s].actual, a[s].reason)
        != (b[s].expected, b[s].actual, b[s].reason)
    ]
    print(
        f"same slot, status changed: {len(flipped)}; status same, text changed: {len(reworded)}"
    )
    for s in flipped:
        same = "same key" if a[s].finding_key == b[s].finding_key else "NEW key"
        print(
            f"  {a[s].finding_key} {same} {s[1] or '(model)':<40} {names[s[2]]:<40} "
            f"{a[s].status} -> {b[s].status}"
        )
    gone = sorted(set(a) - set(b))
    new = sorted(set(b) - set(a))
    if gone or new:
        print(f"slots only before: {len(gone)}; only after: {len(new)}")


def _statuses(bundle) -> dict[str, object]:
    return {f.finding_key: f for f in bundle.findings if f.project_id == PROJECT}


def cmd_recheck(edit: str) -> None:
    import assessment_fixtures as fx
    from epc_control_tower.purpose import (
        PurposeError,
        assess_purpose,
        facts_from_bundle,
        recheck_purpose,
    )

    b0 = build("before")
    f0 = facts_from_bundle(b0, PROJECT)
    prior = assess_purpose(
        request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=f0),
        composed=compose(b0),
        facts=f0,
        determinations=fx.fixture_determinations(facts=f0),
    )
    b1 = with_edit(edit, "after")
    f1 = facts_from_bundle(b1, PROJECT)
    versions1 = [(m.model_key, m.content_id) for m in f1.models]
    names = labels(b0)
    rules_of = {r.requirement_key: r.rule_id for r in b0.ruleset.requirements}
    r0, r1 = rule_definition_digests(), rule_definition_digests(edit)
    s0, s1 = _statuses(b0), _statuses(b1)

    print(f"edit: {edit}")
    print(f"validation_run_id  {b0.run.validation_run_id} -> {b1.run.validation_run_id}")
    print(
        f"ruleset            {b0.ruleset.ruleset_id} v{b0.ruleset.version} -> "
        f"{b1.ruleset.ruleset_id} v{b1.ruleset.version}"
    )
    print(
        f"normalized_digest  {b0.ruleset.normalized_digest[:16]} -> "
        f"{b1.ruleset.normalized_digest[:16]}"
    )
    print(
        "producing/consuming content ids unchanged: "
        f"{[(m.model_key, m.content_id) for m in f0.models] == versions1}"
    )
    print(f"prior record assessment_digest {prior.assessment_digest}")

    try:
        composed1 = compose(b1)
    except PurposeError as error:
        print(f"composition after the edit REFUSED: [{error.code}]")
        return
    succeeds = tuple(
        (activity.activity_ref, subscope.ordinal)
        for activity in prior.activities
        for subscope in activity.subscopes
    )
    try:
        record = recheck_purpose(
            prior=prior,
            request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=f1),
            composed=composed1,
            facts=f1,
            determinations=fx.fixture_determinations(facts=f1),
            succeeds=succeeds,
        )
    except PurposeError as error:
        print(f"recheck REFUSED: [{error.code}]")
        return
    print(f"successor record assessment_digest {record.assessment_digest}")
    print(f"context is_current: {record.successor.context.is_current}")

    carried_but_changed = 0
    carried_rule_changed = 0
    finding_rows = 0
    for outcome in record.successor.outcomes:
        print(
            f"\n  {short(outcome.activity_ref)} #{outcome.subscope_ordinal}: prior "
            f"{outcome.prior_verdict} {outcome.prior_resolution_kind or '-'}; "
            f"correspondence {outcome.correspondence}; condition {outcome.condition_status}"
        )
        for d in outcome.dispositions:
            print(
                f"    member {list(d.member.keys)} {d.disposition} "
                f"now {list(d.current_verdicts)}"
            )
        for row in outcome.carry_over:
            if row.citation_kind != "finding":
                print(f"    determination {row.citation} -> {row.reason}")
                continue
            finding_rows += 1
            was = s0.get(row.citation)
            now = s1.get(row.citation)
            before = was.status if was else "?"
            after = now.status if now else "(absent)"
            element = was.element_key if was else "?"
            rule = names.get(was.requirement_key, "?") if was else "?"
            flag = ""
            if (
                row.reason == "carried"
                and now is not None
                and was is not None
                and (
                    was.status,
                    was.expected,
                    was.actual,
                    was.reason,
                )
                != (now.status, now.expected, now.actual, now.reason)
            ):
                carried_but_changed += 1
                flag = "   <-- carried, but the finding behind this key changed"
            elif (
                row.reason == "carried"
                and was is not None
                and (r0[rules_of[was.requirement_key]] != r1[rules_of[was.requirement_key]])
            ):
                carried_rule_changed += 1
                flag = (
                    "   <-- carried; finding bytes identical, the rule that produced it changed"
                )
            print(
                f"    finding {row.citation} {element} {rule}: {before} -> {after}; "
                f"{row.reason}{flag}"
            )
    print(
        f"\nfinding carry-over rows: {finding_rows}; recorded 'carried' although the "
        f"finding behind the key changed: {carried_but_changed}; recorded 'carried' with "
        "identical finding bytes although its rule's definition changed: "
        f"{carried_rule_changed}"
    )


def cmd_compose() -> None:
    from epc_control_tower.purpose import PurposeError

    bundle = build("compose")
    try:
        composed = compose(bundle)
        print(
            f"fixture Overlay composes: composition_digest {composed.composition_digest[:16]}"
        )
    except PurposeError as error:
        print(f"fixture Overlay REFUSED: [{error.code}] {str(error)[:160]}")


PROBE_RECORD = "docs/contracts/contract-9.9-probe.json"


def cmd_guard_record() -> None:
    """Write a synthetic snapshot record of the current rule set.

    Stands in for the record a real ``--refresh`` would write after a fix, so the
    guard can be asked what it does with the *next* facet edit. Lives only in the
    disposable checkout and is removed by the scenario's ``git clean``.
    """

    bundle = build("record")
    (ROOT / PROBE_RECORD).write_text(
        json.dumps(
            {
                "ruleset": {
                    "id": bundle.ruleset.ruleset_id,
                    "version": bundle.ruleset.version,
                    "normalized_digest": bundle.ruleset.normalized_digest,
                    "requirements": len(bundle.ruleset.requirements),
                }
            }
        ),
        encoding="utf-8",
    )
    print(
        f"wrote {PROBE_RECORD}: v{bundle.ruleset.version} "
        f"{bundle.ruleset.normalized_digest[:16]}"
    )


def cmd_guard(edit: str = "") -> None:
    from epc_control_tower.snapshots import ruleset_version_conflicts

    bundle = with_edit(edit, "guard") if edit else build("guard")
    if edit:
        print(f"edit: {edit}")
    current = {
        "ruleset": {
            "id": bundle.ruleset.ruleset_id,
            "version": bundle.ruleset.version,
            "normalized_digest": bundle.ruleset.normalized_digest,
            "requirements": len(bundle.ruleset.requirements),
        }
    }
    conflicts = ruleset_version_conflicts(ROOT, current)
    print(
        f"ruleset {bundle.ruleset.ruleset_id} v{bundle.ruleset.version} digest "
        f"{bundle.ruleset.normalized_digest[:16]}; version-guard conflicts: {len(conflicts)}"
    )
    for line in conflicts:
        print(f"  {line}")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _zip(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def cmd_published(pristine: str) -> None:
    old = Path(pristine)
    changed: list[str] = []
    for base in ("data/processed", "reports", "ids"):
        names = {
            p.relative_to(old).as_posix() for p in (old / base).rglob("*") if p.is_file()
        } | {p.relative_to(ROOT).as_posix() for p in (ROOT / base).rglob("*") if p.is_file()}
        for name in sorted(names):
            a, b = old / name, ROOT / name
            if not a.exists():
                changed.append(f"+ {name}")
            elif not b.exists():
                changed.append(f"- {name}")
            elif a.read_bytes() != b.read_bytes():
                changed.append(f"M {name}")
    legacy = {
        "data/processed/ids_findings.csv",
        "data/processed/models.csv",
        "data/processed/model_inventory.csv",
        "reports/bcf/ids_failures.bcf",
        "reports/bcf/run_manifest.json",
    } | {
        f"data/processed/bcf_{n}.csv"
        for n in (
            "topics",
            "topic_events",
            "topic_findings",
            "viewpoints",
            "viewpoint_components",
        )
    }
    moved_legacy = [c for c in changed if c[2:] in legacy]
    print(
        f"generated files changed: {len(changed)} "
        f"(legacy frozen among them: {len(moved_legacy)})"
    )
    for line in changed:
        print(f"  {line}")

    run0 = json.loads((old / "data/processed/canonical/run.json").read_text("utf-8"))
    run1 = json.loads((ROOT / "data/processed/canonical/run.json").read_text("utf-8"))
    print(
        f"validation_run_id {run0['run']['validation_run_id']} -> "
        f"{run1['run']['validation_run_id']}"
    )
    m0 = json.loads((old / "reports/artifact_manifest.json").read_text("utf-8"))
    m1 = json.loads((ROOT / "reports/artifact_manifest.json").read_text("utf-8"))
    print(
        f"artifact_bundle_id {m0.get('artifact_bundle_id')} -> {m1.get('artifact_bundle_id')}"
    )
    l0 = json.loads((old / "reports/bcf/run_manifest.json").read_text("utf-8"))
    l1 = json.loads((ROOT / "reports/bcf/run_manifest.json").read_text("utf-8"))
    print(f"legacy run_id {l0.get('run_id')} -> {l1.get('run_id')}")

    f0 = {
        (r["model_key"], r["element_key"], r["requirement_key"]): r
        for r in _rows(old / "data/processed/canonical/findings.csv")
    }
    f1 = {
        (r["model_key"], r["element_key"], r["requirement_key"]): r
        for r in _rows(ROOT / "data/processed/canonical/findings.csv")
    }
    common = set(f0) & set(f1)
    kept = sum(1 for s in common if f0[s]["finding_key"] == f1[s]["finding_key"])
    same_content = sum(
        1
        for s in common
        if all(f0[s][c] == f1[s][c] for c in ("status", "expected", "actual", "reason"))
    )
    print(
        f"canonical findings {len(f0)} -> {len(f1)}; finding_key survives "
        f"{kept}/{len(common)}; content identical {same_content}/{len(common)}"
    )
    i0 = {r["issue_key"] for r in _rows(old / "data/processed/canonical/issues.csv")}
    i1 = {r["issue_key"] for r in _rows(ROOT / "data/processed/canonical/issues.csv")}
    print(f"issues {len(i0)} -> {len(i1)}; issue_key survives {len(i0 & i1)}/{len(i0)}")
    z0, z1 = _zip(old / "reports/bcf/issues.bcf"), _zip(ROOT / "reports/bcf/issues.bcf")
    t0 = {n.split("/")[0] for n in z0 if n.endswith("/markup.bcf")}
    t1 = {n.split("/")[0] for n in z1 if n.endswith("/markup.bcf")}
    markups = sum(1 for t in t0 & t1 if z0[f"{t}/markup.bcf"] != z1[f"{t}/markup.bcf"])
    print(f"BCF topics survive {len(t0 & t1)}/{len(t0)}; markup bytes changed {markups}")


def main(argv: list[str]) -> None:
    command, *rest = argv
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
    {
        "digests": cmd_digests,
        "bundle": cmd_bundle,
        "recheck": cmd_recheck,
        "compose": cmd_compose,
        "guard": cmd_guard,
        "guard-record": cmd_guard_record,
        "published": cmd_published,
    }[command](*rest)
    sys.stdout.flush()


if __name__ == "__main__":
    main(sys.argv[1:])
