# 0001 — Phase 4 correctness, project-scoped programme, and persisted run-free group reference and topic identity

- **Status:** Planned / accepted for implementation. This note records decisions
  before the code that implements them exists. Until the implementation commit
  lands and refreshes the snapshot, the code and every published artifact remain
  at **contract 1.5**; see the `## Unreleased` → *Data contract 1.6 (PLANNED)*
  entry in [`CHANGELOG.md`](../../CHANGELOG.md).
- **Date:** 2026-08-20.
- **Scope:** Phase 4 correctness only. No PBIP/TMDL, no forensic screenshots, no
  `data/raw`, no `third_party`. The six protected tests are not modified.
- **Supersedes:** the second design proposal, on the eight points below.

## Context

An audit reproduced ten correctness defects against the live pipeline (listed in
the CHANGELOG 1.6 entry, each pinned as a counterfactual test by the
implementation commit). They cluster into four themes: a *general* BCF exporter
that is not general, a *frozen* legacy projection that reads a *current*
snapshot, an *artifact identity* blind to things that change the bytes, and an
*overdue* comparison that neither parses time nor resists forgery. The decisions
below are the corrected design. They are mandatory; the implementation commit is
green only if all of them hold together.

## Decisions

### 1. `group_ref` stays a general `GroupingPolicy` concept

- Delete the global invariant "`group_ref == element_key else model_key`". That
  is `ElementGroupingPolicy`'s *policy-level* rule, not a law of the domain;
  another policy may compute its own stable, run-free `group_ref`.
- The general `validate_bundle` checks only: `group_ref` non-empty; `issue_key`
  recomputes from `(validation_run_id, grouping_policy, group_ref)`; topic GUIDs
  do not collide.
- `GroupingPolicy` formally requires `id`, `version`, and `config_sha256()`. The
  protocol note and the `FakePolicy` test that implied `requirements`/
  `programmes` kwargs were optional-to-omit are corrected: a conforming policy
  accepts both keyword arguments.

### 2. Programme fails closed for real

- `(project_id, stage)` uniqueness is checked in the manifest/planning path
  **and** in `validate_bundle` — a hand-built bundle passed straight to the
  validator is rejected too, not only a bundle the loader produced.
- "stage present with `due=''`" and "stage absent" are distinct states.
  Resolution never uses `.get(stage, '')`, which would mask an absent stage as
  an empty deadline; a missing mapping raises.
- Every non-empty `Requirement.stage` must appear explicitly in every project's
  programme, checked at planning time (before any model opens) and re-checked in
  `validate_bundle`.
- `stage == ''` forces `due == ''`.
- One shared aware-`xs:dateTime` parser validates `ValidationRun.as_of`, every
  non-empty `ProjectMilestone.due`, and `IssueEvent.occurred_at`. Parsing is not
  incidental to the `overdue == true` branch; a naive datetime anywhere fails.

### 3. Deadline shadowing across several rules on one subject is fixed

The "highest severity decides stage/due" rule lets a future ERROR hide an
already-overdue WARNING. For one issue, `ElementGroupingPolicy` instead:

- picks, among all member requirements, the one whose project milestone `due` is
  the **earliest non-empty** deadline;
- breaks ties at the same instant by severity descending, then `requirement_key`
  ascending;
- takes `stage`/`due`/`priority`/`assignee_role` from that requirement;
- falls back to the original severity-then-`requirement_key` order only when
  **every** member is explicitly deadline-free;
- sets `labels` to the deterministic union of all member rules' labels, not only
  the deciding rule's;
- computes `is_overdue` from that earliest `due` for OPEN/IN_PROGRESS, and never
  for RESOLVED/CLOSED.

A "high-severity future + low-severity already-overdue" counterexample test is
added.

### 4. Legacy compatibility is keyed by requirement, not by today's topics

The compatibility JSON stores **frozen requirement metadata keyed by
`requirement_key`**, not a list of topics keyed by the current `element_key`.
Keying on today's topics would leave a newly-surfaced failure of an *old* rule
with no metadata.

- Schema, version, and SHA-256 are pinned explicitly (in `control-tower.toml`
  and asserted by a test).
- The compatibility requirement set must match the frozen rule set exactly:
  missing, extra, or duplicate keys all fail.
- The legacy projection regroups the **frozen findings** with its own fixed
  element-grouping algorithm and reads metadata from this document; it reads
  neither `bundle.issues` nor the current `GroupingPolicy`.
- The old R-005 "Project-assumed…" prose is documented as belonging to frozen
  rule set v0.1 only; its exact bytes are preserved, and the over-claim that the
  exporter "supports arbitrary rules" is removed along with the test that
  asserted it.
- The registry loads and validates this file into a typed compatibility object
  and hands that to `LegacyBcfExporter`.

### 5. The general `BcfExporter` is actually general

- `default_registry` no longer passes `legacy_project_id`/`frozen_ruleset` to
  it.
- Those two legacy-scope parameters are removed from `BcfExporter`; a scoped BCF,
  if ever needed, is a separate exporter.
- The `_published_issues` path that dropped a whole mixed frozen/current issue is
  deleted.
- Legacy scope lives only in `LegacyBcfExporter` and `LegacyPbipAdapter`.

### 6. Exporter config identity covers every output-affecting parameter

- `BcfExporter.config_sha256` includes at least: `subdirectory`, `filename`,
  `project_name`, `creation_author`, `topic_type`, `role_domain`.
- The legacy exporter's includes: `subdirectory`, `project_id`, the full frozen
  rule-set identity, and the compatibility SHA-256.
- No constructor parameter that affects a file path or archive bytes is omitted.

### 7. BCF history semantics, stated exactly

- The `sequence == 1` `topic_created` event supplies `CreationDate`/
  `CreationAuthor`.
- When later events exist, the highest-`sequence` event supplies
  `ModifiedDate`/`ModifiedAuthor`; with only a creation event, no `Modified*` is
  fabricated.
- Author resolution is fixed: `actor_ref` if non-empty, else
  `actor_role@role_domain`, else the configured fallback.
- No fictitious `Comment` is emitted.
- A change to an event's time or actor must change the general BCF bytes.
- The exporter rejects a duplicate topic GUID before writing the entry dict; it
  does not rely on the upstream validator alone.

### 8. Three confirmed P2s cleaned up in the same round

- The general/legacy BCF pure-projection modules must import without
  IfcOpenShell installed; separate pure camera math from IFC intake, or defer the
  heavy import.
- The `GroupingPolicy` kwargs protocol regression and the `FakePolicy` coverage
  test are fixed (see decision 1).
- The fixture-count numbers are removed from `inventory.py`'s production
  docstring.

### 9. Commit sequencing

- **Commit A (this one, `docs:`):** only the CHANGELOG 1.6 entry marked *planned*
  and this decision note, also marked planned. The current authoritative
  `docs/data_contract.md` and `docs/bcf_data_contract.md` are **not** rewritten
  to claim 1.6 is implemented — doing so would make A's code (still 1.5) and its
  docs disagree, so A would not be independently consistent.
- **Commit B (`feat:`, later):** the code, the counterfactual tests, the
  regenerated artifacts from one `epc-ct run`, and `contract-1.6.json` from
  `epc-ct snapshot --refresh --contract-changed`. Not started, not pushed, and
  awaiting audit of Commit A.

## Consequences

Commit A moves no bytes: `epc-ct run` stays diff-clean, `epc-ct snapshot` still
matches contract 1.5, and the full suite is unchanged, because A touches only
prose. The design is now recorded before the change, which is what lets the
snapshot refresh in Commit B be permitted and reviewable.
