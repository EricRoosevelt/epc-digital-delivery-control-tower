# 0002 — Minimal Purpose Pack + Project Overlay: representation and ownership

- **Status:** Proposed. This is a data-design decision for review, not an
  implementation. No code, rule, checker, test, schema, configuration file,
  CLI, loader, or generated artifact is added or changed by this document.
- **Date:** 2026-08-26.
- **Scope:** Checkpoint C only — the representation, ownership and identity
  boundary of a Purpose Pack and a Project Overlay. It does not design or
  execute runtime assessment (Checkpoint D), does not touch contract 1.6, and
  does not change validation, requirement, finding, or legacy identity.
- **Depends on:** the product claim and the four worked decisions in
  [`docs/product/interdisciplinary-coordination-readiness-mep-to-architecture.md`](../product/interdisciplinary-coordination-readiness-mep-to-architecture.md)
  (Checkpoint B, product ALIGNED / technical APPROVED), and the correctness and
  identity guarantees fixed in
  [`0001-phase4-correctness-and-identity.md`](0001-phase4-correctness-and-identity.md).
- **Governs:** the boundary in `AGENTS.md` — "A purpose assessment, if it is
  ever built, is approved between `check` and the compatible group" — and the
  "Not implemented" section of `README.md`, neither of which this document
  moves.

## Why this document exists

Checkpoint B walked one real handover four times and wrote down what each
decision needed (`interdisciplinary-coordination-readiness-mep-to-architecture.md`
§5). It deliberately left open *how any of it is represented*. This document
answers that question, and only that question: what a Purpose Pack is, what a
Project Overlay is, what file shape they take, how they compose, what fails
closed, and how their existence never disturbs a published byte. It does not
decide how a verdict is computed at runtime — that is Checkpoint D, and naming
`AssessmentRun`, `AssessmentItem`, `EvidenceGap` or `BlockerCandidate` here
would be exactly the mistake `Agent-product-manager.md` warns against:
approving a tidy schema before the object is earned.

---

## 1. Four-layer ownership

Restating Checkpoint B §5's table as a decision rather than an observation.
Each fact below has exactly one owner; a fact appearing in two rows is the
failure mode this section exists to prevent.

### Framework

Owns the base semantics of `READY` / `CONDITIONAL` / `BLOCKED` / `UNKNOWN` and
the six invariants fixed in Checkpoint B §5:

1. Exactly one verdict per activity × assessed scope × model-version context.
2. The four verdicts are mutually exclusive.
3. `READY` permits no unresolved blocker and no evidence gap.
4. `BLOCKED` means a known unmet requirement prevents the activity.
5. `UNKNOWN` means an evidence gap makes the activity undecidable.
6. `CONDITIONAL` must originate in a named authorisation event, never derived
   automatically from findings.

No Pack and no Overlay may redefine what any of the four words mean or narrow
the set of legal transitions between them. A Pack that shipped its own meaning
for `READY` would not be a different purpose; it would be a different
framework wearing a purpose's name — the same sentence Checkpoint B used, and
still true here.

### Purpose Pack (reusable across projects)

Owns, per Checkpoint B §5's rightmost-but-one column:

- Purpose identity, version, maturity, citations, and compatibility.
- Direction (e.g. MEP → Architecture) — never derivable from
  `discipline_scope`, which stays applicability-only (`AGENTS.md`).
- The production activities at stake for this purpose.
- Which requirements bear on which activity, **and what a requirement cannot
  answer** (R-010 witnesses a shared marker, not alignment — that limit is
  Pack data too, or a Pack could silently upgrade a witness into evidence it
  never was).
- Verdict / blocker decision logic for this purpose, expressed **within** the
  Framework's four states and never outside them.
- Reusable consequence *kinds* (work cannot start; rework risk; re-issue risk;
  work suspended) — never a magnitude, which no Pack has evidence for.
- Default responsibility policy — which role answers for a kind of failure, in
  the abstract (Checkpoint B §5 row 8a).
- Source-fix guidance and recheck conditions.

### Project Overlay (one per project)

Owns:

- Project conventions and assumptions that are one project's agreement, not a
  universal truth — R-005's `EPC_Delivery.AssetTag` / `SystemCode` is the
  worked example (Checkpoint B §2, §5).
- Team and role mappings that turn a Pack's abstract responsibility policy
  into this project's actual assignee (row 8b).
- Risk-authorisation policy: who may accept what, for `CONDITIONAL`.
- Cost parameters, for the *magnitude* half of a business consequence a Pack
  can only name the kind of.
- Accepted evidence methods — e.g. what counts as an alignment confirmation
  for case 3 — as a project policy statement, never the confirmation itself.
- Contract assumptions and explicitly permitted overrides against Pack
  defaults.

The Overlay never owns base verdict semantics. It parameterises decisions the
Framework and Pack have already shaped; it does not get a vote on what
`CONDITIONAL` means.

### Runtime assessment (Checkpoint D — not designed here)

Owns everything that is true of one assessment of one pair of model versions
and nothing else: actual model versions and the handover event, evidence
produced or the named absence of it, the verdict actually reached, the
blocker actually found, the resolving role/team actually assigned (row 8c,
derived from 8a through 8b), the actual actor (row 8d, alongside 8c, never
instead of it), any risk acceptance actually given, and exit/recheck status.

**Nothing in this list may live in a Pack or an Overlay file.** A Pack and an
Overlay are read many times and written once; runtime evidence is produced
once per handover and is only true of the versions it was produced against.
Checkpoint B's closing warning about this is the operative test for every
field proposed below: would filing it as Pack/Overlay configuration make a
statement about two specific model versions look like a standing project
setting? If yes, it is runtime, and it does not belong here.

---

## 2. Minimal representation: two options compared

### Option A — independent declarative files, considered and rejected as posed

A `purpose-packs/<pack_id>/pack.toml` per Pack, and a
`projects/<project_id>/overlay.toml` per project, both hand-authored TOML,
discovered by directory glob (mirroring how `projects/` and `rules/` already
work). Pack and Overlay are fully separate files with no relationship to the
existing `project.toml`.

Rejected as a *separate third manifest*, for one reason: `project.toml`
already exists as the one place a project's own facts live, discovery for it
is already a glob (`AGENTS.md`, "Adding a project should not touch this
package"), and a project has exactly one Overlay. Inventing a second discovery
mechanism and a second file a maintainer has to remember to add when they add
a project multiplies the surface for no gain — the same "measure what doing
nothing costs" instinct in `AGENTS.md` rule 6 argues for fusing rather than
duplicating a per-project file.

### Option B — Pack as an independent file, Overlay embedded in the project manifest

A Purpose Pack is its own file, `purpose-packs/<pack_id>/pack.toml`, one file
per Pack, discovered by glob exactly as `rules/<ruleset>/*.toml` is today. An
Overlay is a new, optional table inside the *existing* `projects/<id>/project.toml`
— `[[overlay]]` (or a nested `[overlay.<pack_id>]` block, settled in §3) —
because an Overlay is inescapably project data, and `project.toml` is already
the project's one file.

**Chosen.** Reasons, weighed against Option A and against a still-smaller
"just a constants dict in Python" option that was also considered and
discarded:

- **A Pack is reusable across projects; an Overlay is not reusable at all.**
  That asymmetry is exactly what "independent Pack, project carries its own
  Overlay" expresses structurally: two projects reference the same Pack file
  and never touch each other's overlay data, and a Pack can be authored,
  reviewed, and versioned with no project in scope at all — the same way a
  rule file in `rules/` is authored with no project in scope.
- **No new discovery mechanism.** `project.toml` is already found by the
  existing project glob; the Overlay rides along. A Pack is found the same way
  a ruleset is: a glob over a fixed directory, `purpose-packs/*/pack.toml`,
  with no registry, no entry points, no plugin loader — the same
  registration-is-explicit-and-in-tree posture `AGENTS.md` states for
  checkers, grouping policies and exporters.
- **Composition order falls out of the file layout rather than needing its
  own rule.** A project's Overlay names the Pack(s) it uses; the Pack is
  loaded first (it has no dependency on any project), the Overlay second (it
  depends on the Pack existing), and there is exactly one place — the
  Overlay's own table — where that dependency is declared. There is no third
  file whose precedence relative to the other two would need a separate
  convention.
- **A Python constants dict was rejected** for the reason `AGENTS.md` already
  gives for constants generally: "what a project contains" belongs in a
  manifest, not in code, and a Pack that lived as a Python module would need a
  code change — and a PR against this package — to add a purpose, which is
  precisely the seam `AGENTS.md` says a fork should not have to touch.
- **Nothing here is a plugin.** No entry points, no registry marketplace, no
  dynamic import. A Pack file that is not on disk under `purpose-packs/` does
  not exist for this repository, exactly as a rule file that is not under
  `rules/` does not exist. This mirrors the existing rule/checker registration
  discipline and introduces no new extensibility axis.
- **Why not go smaller still (fold the Pack into the Overlay, one file per
  project)?** Rejected because it would destroy the one property that
  motivated a Pack at all: Checkpoint B's central finding is that a
  *reusable* purpose question (which activities, which requirements, which
  verdict logic) is a different fact from a *project's* policy answer (which
  team, which cost, which accepted evidence methods) — folding them into one
  file per project would mean every project re-authors the MEP → Architecture
  question from scratch, and a correction to that question would have to be
  copied by hand into every project file that uses it. That is the drift this
  whole checkpoint exists to avoid.

---

## 3. Minimal fields and composition rules

Every fragment below is a **design illustration**, not a real artifact. No
`purpose-packs/` directory and no `[overlay]` table are created by this
document, and no example below states a cost, an authorisation, an alignment
confirmation, a handover, or a verdict as if it had happened — every runtime-
shaped value in the fragments is marked `# EXAMPLE, not a live record`.

### 3.1 Field-level ownership matrix

| Field | Owner | Type shape | Notes |
|---|---|---|---|
| `pack_id` | Pack | slug | Identity anchor; see §3.4. |
| `pack_version` | Pack | semver-like string | Author-declared, not derived from a clock. |
| `compatible_framework` | Pack | version range string | The Framework version(s) this Pack's activity/requirement mapping assumes; see §3.4. |
| `maturity` | Pack | enum (`draft`/`reviewed`/`stable`) | Pack metadata only; never read by the Framework. |
| `citations` | Pack | list of strings | Free text, provenance for the Pack author's claims. |
| `direction` | Pack | `{ from: discipline, to: discipline }` | Never derived from `discipline_scope`. |
| `activities[]` | Pack | list of `{ activity_id, label }` | The production questions at stake, e.g. Checkpoint B's three. |
| `activities[].evidence[]` | Pack | list of `{ rule_ref, answers, cannot_answer? }` | See §3.3 for `rule_ref`. `cannot_answer` records a limit like R-010's, in the Pack's own words. |
| `verdict_logic` | Pack | reference to a named, enumerated decision table | Maps (evidence outcome) → one of the Framework's four words only; see §3.2. |
| `consequence_kinds[]` | Pack | list of labels | Kind only, e.g. `work-cannot-start`, `rework-risk`; no magnitude field exists on a Pack. |
| `default_responsibility[]` | Pack | list of `{ failure_kind, role }` | Abstract role name, e.g. `model-coordination`; not a person or team. |
| `source_fix_guidance[]` | Pack | list of `{ rule_ref, guidance }` | Free text, tool-specific advice as in Checkpoint B's cases. |
| `recheck_conditions[]` | Pack | list of `{ activity_id, condition }` | What evidence would end a block/unknown, stated in advance. |
| `project_id` | Overlay | slug | Already exists on `project.toml`; the Overlay is a table within it. |
| `overlay.uses_pack` | Overlay | `{ pack_id, pack_version }` | Pins the exact Pack version this project's Overlay was written against. |
| `overlay.team_mapping[]` | Overlay | list of `{ role, team_or_person }` | Realises Pack `default_responsibility` for this project. |
| `overlay.risk_authorisation` | Overlay | `{ may_authorise: [role...] }` | Who *may* accept a `CONDITIONAL` risk here — not a specific acceptance. |
| `overlay.cost_parameters` | Overlay | project-defined key/value | Magnitude inputs a future runtime step may read; no cost figure is fabricated by this document. |
| `overlay.accepted_evidence_methods[]` | Overlay | list of `{ activity_id, method_id, description }` | What counts as, e.g., an alignment confirmation for *this* project. |
| `overlay.conventions[]` | Overlay | list of `{ rule_ref, note }` | R-005-shaped project assumptions; see §3.5. |
| `overlay.overrides[]` | Overlay | list of `{ target, permitted_change }` | Explicitly enumerated, never a general patch; see §3.6. |

Nothing in either table carries a model version, a finding key, an actual
verdict, an actual authoriser, an actual cost, or an actual assignee. Those
stay off both files by construction — there is no field here that names a
runtime fact, which is the property being designed for, not merely stated.

### 3.2 Pack skeleton — design illustration only

```toml
# purpose-packs/mep-to-architecture-coordination/pack.toml
# EXAMPLE, not a live artifact — no such file exists yet.

pack_id = "mep-to-architecture-coordination"
pack_version = "0.1.0"
compatible_framework = ">=1.6,<2.0"
maturity = "draft"
citations = ["docs/product/interdisciplinary-coordination-readiness-mep-to-architecture.md"]

[direction]
from = "MEP"
to = "Architecture"

[[activities]]
activity_id = "schedules-and-room-data-sheets"
label = "Room data sheets and equipment schedules"

  [[activities.evidence]]
  rule_ref = { requirement_key = "842a37c7-3183-5fce-ab45-b93c37ec7a08" }  # EXAMPLE
  answers = "asset identity (AssetTag)"

[[activities]]
activity_id = "ceiling-and-bulkhead-geometry"
label = "Reflected ceiling and bulkhead layout"

  [[activities.evidence]]
  rule_ref = { requirement_key = "491a4a0b-9b4a-5f77-b90d-31a7dc8beb44" }  # EXAMPLE
  answers = "in-model position (storey assignment)"

  [[activities.evidence]]
  rule_ref = { requirement_key = "acb11f11-bf18-5516-a6f2-21e451a6e410" }  # EXAMPLE
  answers = "shared-marker witness (name + cross-model GlobalId)"
  cannot_answer = "cross-model alignment/placement; a PASS is not alignment evidence"

[verdict_logic]
table_id = "mep-to-architecture-coordination.v1"  # enumerated elsewhere in the Pack, not shown here

[[consequence_kinds]]
activity_id = "schedules-and-room-data-sheets"
kinds = ["work-cannot-start", "re-identification-and-reissue-risk"]

[[default_responsibility]]
failure_kind = "missing-project-asset-identity"
role = "model-coordination"
```

`verdict_logic` is deliberately not expanded into an executable rule DSL here.
It names a table the Pack document itself must enumerate exhaustively —
(evidence outcome combination) → (one Framework word) — with no wildcard
branch and no fallback default; §3.7 covers what happens when a case is
missing. Whether that table is literal TOML rows or a small closed enum is
left to the Checkpoint D design; this document fixes only that it must be
**closed, declarative, and refuse an unenumerated case** rather than a
general-purpose rules engine, which the product charter rules out
(`Agent-product-manager.md`, "Drift control").

### 3.3 Referencing an existing rule/requirement: `rule_id` vs `requirement_key`

Two candidates, compared:

- **`rule_id`** (e.g. `"R-005A"`) — stable across a rule's lifetime by
  authoring convention, human-readable, but **not what contract 1.6
  actually keys on**. Nothing prevents two different `requirement_id`s within
  one rule file (R-005A alone keys two requirements today — `AssetTag` and
  `SystemCode`), so a Pack referencing only `rule_id` cannot say *which*
  requirement within the rule it means without inventing a second field that
  duplicates `requirement_id`.
- **`requirement_key`** (e.g. `842a37c7-3183-5fce-ab45-b93c37ec7a08`) — the
  actual UUIDv5 published in `findings.csv` and `requirements.csv`, derived
  by `build_requirement_key(rule_id, requirement_id)`
  (`epc_control_tower/identity.py:99`) from exactly those two stable inputs.
  It already disambiguates within a multi-requirement rule and is the key a
  runtime assessment would actually join against.

**Chosen: `requirement_key`**, exactly as published, with `rule_id` carried
alongside in the Pack purely as a human-readable comment/label (as in the
skeleton above) — never as the join key. Identity/version consequence: a
`requirement_key` is stable "across runs, contract versions, and model
changes" by its own docstring, because it is derived only from
`(rule_id, requirement_id)` and not from severity, stage, or any other field
that might legitimately change on a rule. A Pack that pins a
`requirement_key` therefore survives a rule's severity or stage being edited,
and only breaks — loudly, at load time (§3.7) — if the rule's `rule_id` or
`requirement_id` themselves change, which is already the condition under
which contract 1.6 considers it a *different* requirement. This is the
correct failure mode: a Pack should not silently keep pointing at "whatever
R-005A now means" if R-005A is renamed or split.

### 3.4 Pack identity, version, compatibility

- `pack_id`: an author-chosen slug, unique within `purpose-packs/`, checked
  the same way `rule_id`/`ruleset_id` uniqueness is checked today —
  statically, at load time, by directory structure (one directory per Pack)
  plus a declared field that must match its directory name. No UUID is
  minted for Pack identity; a Pack is authored, reviewed and named by a
  person, unlike a `requirement_key`, which exists precisely so that no
  person has to hand-assign an identifier.
- `pack_version`: an author-declared string (semver-shaped, not enforced
  beyond being a slug-safe string), bumped by the Pack's author whenever its
  activities, evidence mapping, or verdict logic change. This is a
  *declaration*, not a derived digest — unlike `requirement_key` or
  `validation_run_id`, nothing about a Pack's version needs to be
  tamper-evident against the model data, because a Pack never touches
  contract 1.6 identity (§4).
- `compatible_framework`: a version-range string against the Framework's own
  release identity (today, contract 1.6 / rule set 2.2). This is the field
  that lets a Pack say "I was written assuming R-010's `discipline_scope`
  values and R-004/R-005's `requirement_key`s existed with these meanings" —
  and lets composition (§3.7) refuse to load a Pack against an incompatible
  Framework rather than silently misreading it.

### 3.5 Overlay: pointing at Pack, project, and permitted overrides — R-005 as the worked case

```toml
# projects/pcert-sample/project.toml — EXCERPT, illustrative addition only.
# EXAMPLE, not a live edit — this document changes no tracked file.

[overlay]
project_id = "pcert-sample"

[overlay.uses_pack]
pack_id = "mep-to-architecture-coordination"
pack_version = "0.1.0"

[[overlay.team_mapping]]
role = "model-coordination"
team_or_person = "coordination-team"  # EXAMPLE — no real assignment exists

[[overlay.conventions]]
rule_ref = { requirement_key = "842a37c7-3183-5fce-ab45-b93c37ec7a08" }  # EXAMPLE
note = "EPC_Delivery.AssetTag is pcert-sample's own convention, not a general obligation."

[[overlay.accepted_evidence_methods]]
activity_id = "ceiling-and-bulkhead-geometry"
method_id = "overlay-comparison"
description = "Placements from both models overlaid in a common viewer and visually confirmed by model-coordination."
```

Why this satisfies "R-005-like project conventions live in the Overlay
without polluting the Pack core": the Pack's `activities.evidence` entry for
schedules (§3.2) says only that `requirement_key
842a37c7-…` answers "asset identity" for that activity — it never asserts
that `AssetTag` is a universal delivery obligation. The *fact* that this
particular requirement is a project-specific assumption is asserted once, in
the rule file itself (`rules/epc-delivery/R-005A.toml`'s own
`labels = ["IDS", "ProjectAssumption"]`), which is Framework/rule data
already, not new Pack data. What the Overlay adds is a project's own note
about *why it opted into this convention*, which is optional narrative, not a
Pack-core assertion — a second project's Overlay simply omits it or writes a
different note, and the Pack file is untouched either way.

**Overlay → future runtime assignment (rows 8a–8c).** The Pack's
`default_responsibility` says "missing project asset identity → role
`model-coordination`" in the abstract. The Overlay's `team_mapping` says
"`model-coordination` → `coordination-team`" for this project. Composing the
two (a lookup, not a computation) is what a future runtime step would use to
produce the actual resolving role/team for one assessment — and that
composed result is a runtime fact (row 8c), never written into either file.

### 3.6 Overrides: explicit and enumerated, never a general patch

`overlay.overrides[]` is a **closed list of named override kinds**, each
naming exactly which Pack field it may change and how, e.g.:

```toml
[[overlay.overrides]]
target = "activities.ceiling-and-bulkhead-geometry.recheck_condition"
permitted_change = "narrow-scope"   # a named, enumerated kind — not free text
note = "This project recheck's alignment confirmation only for ground-floor zones."
```

An override kind is drawn from a fixed enumeration the Pack format defines
(e.g. `narrow-scope`, `add-accepted-evidence-method`) — never an arbitrary
key/value patch against the Pack document, and never a target inside
`verdict_logic`, `direction`, or any Framework-facing field. This is the
same "no general rule DSL" boundary as §3.2: an override is data selected
from a closed list, not code.

**What an Overlay can never override, stated affirmatively:** the Framework's
four verdict words and their six invariants (§1); a Pack's `direction`;
which `requirement_key` an activity's evidence entry points at (an Overlay
may *add* an accepted evidence *method*, never *remove or redirect* a Pack's
evidence mapping); and anything in the runtime-assessment column of
Checkpoint B §5's table. An override attempting any of those is a composition
error under §3.7, not a permitted override.

### 3.7 Composition and fail-closed behaviour

Composition order is fixed by the file layout chosen in §2: load the Pack(s)
named by `overlay.uses_pack`, then load the Overlay, then check the pair
together. Every case below fails closed — refuses to produce a usable
Pack+Overlay pair — rather than silently substituting a default, mirroring
`AGENTS.md`'s "a delivery requirement the pipeline silently declines to
evaluate is the worst outcome available" for rules:

| Situation | Behaviour |
|---|---|
| `overlay.uses_pack.pack_id` names a Pack not present under `purpose-packs/` | Fail closed. No Pack is substituted. |
| `overlay.uses_pack.pack_version` does not match the Pack's declared `pack_version` | Fail closed. An Overlay pinned to `0.1.0` does not silently load `0.2.0`. |
| Pack's `compatible_framework` does not cover the running Framework version | Fail closed at load, before any activity is evaluated — the same "rejected while planning, before any model is opened" posture `AGENTS.md` describes for a rule naming an unknown checker. |
| An `activities.evidence[].rule_ref.requirement_key` names a `requirement_key` absent from the loaded rule set | Fail closed. A Pack referencing a retired or renamed requirement is an error, not a silently-skipped evidence entry. |
| Two entries in a Pack declare the same `activity_id`, or two Packs used by one Overlay declare the same `activity_id` | Fail closed as a duplicate — mirrors the existing duplicate-`requirement_key` rejection in `RuleSet` (`domain.py:496`). |
| `overlay.overrides[].target` names a field not on the closed override enumeration, or a field listed under "never overridable" (§3.6) | Fail closed as an illegal override, not applied and not ignored. |
| `overlay.team_mapping` has no entry for a role a Pack's `default_responsibility` names | Fail closed **only when that responsibility is actually needed** — i.e. this is a runtime-time check (Checkpoint D), not a load-time one, because whether a given project ever encounters that failure kind is a runtime question. Recorded here so Checkpoint D does not invent a silent default team. |
| An Overlay's `uses_pack` is entirely absent | Fail closed — a project with no Pack has no purpose assessment available, which is the correct state (today's actual state), not an error to paper over with an implicit default Pack. |

No situation above resolves by picking a default, by taking the first match
in an unordered collection, or by reading anything time-dependent — composing
Pack and Overlay is required to be as deterministic as everything else this
repository publishes (`AGENTS.md` rule 1), which is why every check in this
table is phrased as "fail closed", not "warn and continue".

---

## 4. Identity and determinism

Fixed boundaries, checked against the actual identity code rather than
asserted from memory:

- **`validation_run_id`** is built by `build_validation_run_id(...)`
  (`epc_control_tower/identity.py:167`) from `ruleset_id`,
  `ruleset_version`, `ruleset_normalized_digest`, `models`, `checkers`, and
  `as_of`. None of those five inputs is Pack or Overlay data; a Pack or
  Overlay file existing, changing, or being deleted cannot move this value.
- **`requirement_key`** is built by `build_requirement_key(rule_id,
  requirement_id)` (`identity.py:99`) — again, no Pack/Overlay input.
- **`finding_key`**, `Issue`/legacy identity, and every downstream contract
  1.6 artifact are derived transitively from the same rule-set and model
  data, never from Pack or Overlay content. Nothing in §3's field list is
  consumed by `build_ruleset_normalized_digest` (`identity.py:109`), which
  enumerates exactly the `Requirement` fields it hashes and does not include
  a Pack or Overlay reference among them.
- **No clock, no unordered iteration, no machine-dependent path.** Every
  composition rule in §3.7 is a lookup or a membership check, and the field
  list in §3.1 contains nothing that reads `datetime.now()` or a filesystem
  ordering. A future Pack/Overlay content-identity value (if one is ever
  minted, e.g. a `pack_content_sha256` analogous to
  `ruleset_normalized_digest`) must be built the same way that digest is: a
  deterministic hash of parsed, sorted structure — never of raw file bytes,
  for the same reason `build_ruleset_normalized_digest`'s docstring gives
  (survives reformatting; only real content changes move it). This document
  does not mint that value; it only fixes the constraint it must satisfy
  when Checkpoint D or a later checkpoint does.
- **Runtime/assessment identity is explicitly deferred.** Nothing here names
  an `AssessmentRun` id, a verdict id, or any other runtime-scoped
  identifier. That is Checkpoint D's decision.

### Changed-input counterfactuals a future implementation must run

Four tests, stated now so Checkpoint D's implementation is judged against a
commitment made before the code exists — the same discipline `AGENTS.md`
rule 6 describes ("pin the counterfactual as a test afterwards, so the
decision keeps being true rather than merely having been made once"):

1. **Change only a Purpose** (edit a Pack's `activities`, `verdict_logic`, or
   `source_fix_guidance` — anything in §3.1's Pack column) and re-run
   `epc-ct run`. Expected: `git diff --exit-code -- data/processed reports`
   passes; `epc-ct snapshot` reports no drift; every `validation_run_id`,
   `requirement_key`, and `finding_key` in `data/processed/canonical/` is
   byte-identical; the contract 1.6 manifest's recorded file list and its
   SHA-256s are unchanged.
2. **Change only an Overlay** (edit `overlay.team_mapping`,
   `overlay.cost_parameters`, or `overlay.conventions` for one project) and
   re-run. Expected: identical to (1) — additionally, the *other* project's
   published rows in every shared CSV (e.g. `models.csv`) are byte-identical,
   proving one project's Overlay cannot leak into a sibling project's
   published data, which is the exact failure `AGENTS.md` rule 6 already
   measured once for a different change ("Adding a second project... all
   eight published CSVs changed").
3. **Add a second Pack** (a new file under `purpose-packs/`, unused by any
   Overlay) and re-run. Expected: identical to (1) — an unreferenced Pack on
   disk must not appear in any published artifact, count, or manifest, the
   same way an unused rule file outside `rules/<ruleset>/` does not today.
4. **Add a second project's Overlay** (a new project directory whose
   `project.toml` carries an `[overlay]` table pointing at an existing Pack)
   and re-run. Expected: the first project's published rows, counts, and keys
   are unchanged; only the new project's own rows appear, mirroring the
   existing "adding a project should not touch this package" guarantee in
   `AGENTS.md`.

What the future test plan must actually diff, named precisely so it is not
re-litigated per-run: the full set of `requirement_key`, `finding_key`,
`issue_key`, and `validation_run_id` values present in
`data/processed/canonical/{requirements,findings,issues}.csv`; the row counts
of every published CSV; the byte count and SHA-256 of every file under
`data/processed/` and `reports/`; and the `contract-1.6.json` manifest's
recorded file list. All four counterfactuals above must leave every one of
those unchanged except case 4's expected new rows in the new project's own
files.

---

## 5. Scenario mapping — Checkpoint B's three activities

Proving §3's shape is sufficient, without designing runtime behaviour:

| Checkpoint B activity | Pack `activity_id` (illustrative) | Evidence entries (illustrative) | Live verdict (runtime fact, unaffected by this design) |
|---|---|---|---|
| Room data sheets / equipment schedules | `schedules-and-room-data-sheets` | R-005A/B `requirement_key`s, `answers = "asset identity"` | **BLOCKED** (case 2) — stays a runtime observation; no Pack/Overlay field asserts it |
| Ceiling / bulkhead geometry | `ceiling-and-bulkhead-geometry` | R-004A/B `requirement_key`s (`answers = "in-model position"`); R-010 `requirement_key` (`answers = "shared-marker witness"`, `cannot_answer = "cross-model alignment"`) | **UNKNOWN** (case 3) — likewise unaffected |
| Builder's-work openings | `builders-work-openings` | *(no evidence entry — R-010's Pack entry above does not double as openings evidence)* | **UNKNOWN** (case 4) — likewise unaffected |

Confirmed, restated as constraints this design satisfies rather than data it
asserts:

- The live verdicts (`BLOCKED`, `UNKNOWN`, `UNKNOWN`) are **runtime
  observations**. No field in §3.1's Pack or Overlay columns can hold a
  verdict; §3.2 and §3.5's skeletons contain none.
- **R-010 is represented in the Pack only as a name-plus-cross-model-GlobalId
  shared-marker witness**, with its limit (`cannot_answer`) stated in the
  same entry — never promoted to alignment evidence by anything in this
  design. This is why §3.2's example entry carries a `cannot_answer` field at
  all: the Pack format has to be able to say what a passing rule does *not*
  establish, or a Pack author could quietly upgrade R-010's witness into
  proof of alignment, exactly the mistake Checkpoint B case 3 exists to name.
- **R-010's applicability/checker divergence is out of scope here.**
  Checkpoint B already registered it as "separate technical debt and
  nothing more... not Checkpoint C scope"; this document changes nothing
  about `rules/epc-delivery/R-010.toml` or the `completeness` checker and
  does not depend on that divergence being fixed.
- **`discipline_scope` remains validation applicability only.** §3.2's
  `direction` table is new Pack data, never a reinterpretation of
  `discipline_scope`, which stays exactly what `AGENTS.md` and Checkpoint B
  both already fix it as.

---

## 6. Future pipeline boundary (recorded, not built)

Restating the seam from `AGENTS.md` and Checkpoint B §5, unchanged, because
this document's field design must remain consistent with it rather than
quietly widen it:

```text
check → purpose assessment → compatible group
```

A future purpose assessment stage, if built:

- is **not** a `Checker` — it does not evaluate a requirement against a
  model;
- is **not** a `GroupingPolicy` — it does not decide what counts as one
  actionable issue;
- is **not** an `Exporter` — it does not move results anywhere;
- does **not** enter `default_registry`.

This document does not implement that stage, does not name its runtime
types, and does not schedule it. It only confirms that the Pack/Overlay
shape designed in §§2–3 is data such a stage could read without requiring
any change to §1's ownership boundary — the test being that nothing in §3.1
needs a runtime type to exist before it can be authored.

---

## 7. Explicitly out of scope for this document

No `AssessmentRun`, `AssessmentItem`, `EvidenceGap`, `BlockerCandidate`, or
other runtime assessment object is created, named as approved, or implied to
be forthcoming in a particular shape. No code, rule, checker, test, README,
CHANGELOG, or Checkpoint B document is modified. No actual Pack or Overlay
configuration file is added — every fragment in §3 is illustrative and
explicitly marked as such. `data/processed/`, `reports/`, any snapshot, and
contract 1.6 are untouched. No Doctor, Registry, exporter, database, AI
agent, knowledge graph, automatic IFC patching, or cross-run ledger is
designed. Nothing is merged, tagged, or released. Checkpoint D is not
started.

## Consequences

This document commits a future implementation to: two file locations
(`purpose-packs/<pack_id>/pack.toml`, `projects/<id>/project.toml`'s
`[overlay]` table); `requirement_key` as the only legal way a Pack references
existing rule data; a closed, enumerated override list rather than a general
patch mechanism; fail-closed composition with no silent defaults; and the
four changed-input counterfactuals in §4 as the acceptance test for
Checkpoint D's identity claims. It commits nothing about how a verdict is
computed at runtime, how `AssessmentRun`-shaped state (if any) is named, or
when Checkpoint D begins — those remain open, and deliberately so.
