# 0002 — Minimal Purpose Pack + Project Overlay: representation and ownership

- **Status:** Proposed. This is a data-design decision for review, not an
  implementation. No code, rule, checker, test, schema, configuration file,
  CLI, loader, or generated artifact is added or changed by this document.
- **Date:** 2026-08-27.
- **Revision:** supersedes the version at `bc4a142` (2026-08-26), which
  technical-director review **REJECTED** for six reasons: it treated an
  activity's necessary evidence as identical to an existing validation
  requirement, so `ceiling-and-bulkhead-geometry`'s alignment confirmation and
  `builders-work-openings`'s penetration/opening evidence had nowhere to be
  written down and openings ended up with no evidence entry at all,
  contradicting Checkpoint B's own UNKNOWN reasoning; it hard-coded R-005's
  `requirement_key`s into Pack core instead of the Overlay; it deferred
  verdict/blocker decision logic entirely to Checkpoint D instead of fixing a
  data shape now; it invented a single "Framework version" compatibility
  field where three distinct compatibilities exist and one of them is not yet
  nameable; it used a singular `overlay.uses_pack` while also discussing
  multi-Pack activity collisions, and left Pack/Overlay cardinality otherwise
  unsettled; and its fourth changed-input counterfactual added a whole new
  project and then excused that project's own new rows from the zero-byte
  claim. Every one of those six is closed below, each marked **(closes gap
  N)** at the point it is closed, and every rejected conclusion listed in the
  commissioning prompt has been removed, not merely qualified.
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
approving a tidy schema before the object is earned. What Checkpoint C **does**
owe is a data shape a future evaluator could walk without redesigning the
Pack format — that is the standard the rejected revision fell short of, and
the standard §3 is now held to.

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

Owns:

- Purpose identity, Pack file/schema format version, Pack content version,
  maturity, citations (§3.4).
- Direction (e.g. MEP → Architecture) — never derivable from
  `discipline_scope`, which stays applicability-only (`AGENTS.md`).
- The production activities at stake for this purpose, each naming the
  **evidence requirements** it needs a decision — never a validation
  requirement directly (§3.2, §3.8; **closes gap 1**).
- What each evidence requirement means, what would satisfy it, and — for a
  reusable, non-project-specific question — how it binds to existing
  validation data by `ruleset_id` + `ruleset_version` + `requirement_key`
  (§3.3). A project-specific evidence requirement (e.g. asset identity) is
  declared here only as a *question*; **which validation data answers it for
  a given project is Overlay data, never Pack data** (§3.5; **closes gap 2**).
- Verdict / blocker decision logic for this purpose, expressed as a closed
  decision tree over evidence-requirement outcomes, entirely **within** the
  Framework's four states — `CONDITIONAL` is categorically excluded as a leaf
  (§3.8; **closes gap 3**).
- Reusable consequence *kinds* (work cannot start; rework risk; re-issue risk;
  work suspended) — never a magnitude, which no Pack has evidence for.
- Default responsibility policy, keyed by the same `failure_kind` the
  decision tree names — which role answers for a kind of failure, in the
  abstract (Checkpoint B §5 row 8a).
- Source-fix guidance and recheck conditions.

### Project Overlay (one per project)

Owns:

- Which Pack(s) this project uses, and at which pinned content version
  (§3.5, §5 cardinality; **closes gap 5**).
- For every Pack evidence requirement whose binding is project-specific: the
  actual `ruleset_id` + `ruleset_version` + `requirement_key`(s) that satisfy
  it here. R-005's `EPC_Delivery.AssetTag` / `SystemCode` binding is the
  worked example, and it never appears in the Pack (§3.5; **closes gap 2**).
- For every Pack evidence requirement that is satisfied only by evidence
  produced at assessment time (an alignment confirmation, a coordination-
  review determination): which method(s) this project accepts as meeting it.
- Team and role mappings that turn a Pack's abstract responsibility policy
  into this project's actual assignee (row 8b).
- Risk-authorisation policy: who may accept what, for `CONDITIONAL`.
- Cost parameters, for the *magnitude* half of a business consequence a Pack
  can only name the kind of.
- Project conventions and assumptions that are one project's agreement, not a
  universal truth.
- Contract assumptions and explicitly permitted overrides against Pack
  defaults, drawn from a closed list (§3.6).

The Overlay never owns base verdict semantics. It parameterises decisions the
Framework and Pack have already shaped; it does not get a vote on what
`CONDITIONAL` means.

### Runtime assessment (Checkpoint D — not designed here)

Owns everything that is true of one assessment of one pair of model versions
and nothing else: actual model versions and the handover event, evidence
produced or the named absence of it, the verdict actually reached by walking
a Pack's decision tree, the blocker actually found, the resolving role/team
actually assigned (row 8c, derived from 8a through 8b), the actual actor (row
8d, alongside 8c, never instead of it), any risk acceptance actually given —
which is the only thing that may promote a tree's `BLOCKED`/`UNKNOWN` result
to `CONDITIONAL` (§3.8) — and exit/recheck status.

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
package"), and a project has exactly one Overlay (§5). Inventing a second
discovery mechanism and a second file a maintainer has to remember to add when
they add a project multiplies the surface for no gain — the same "measure
what doing nothing costs" instinct in `AGENTS.md` rule 6 argues for fusing
rather than duplicating a per-project file.

### Option B — Pack as an independent file, Overlay embedded in the project manifest

A Purpose Pack is its own file, `purpose-packs/<pack_id>/pack.toml`, one file
per Pack, discovered by glob exactly as `rules/<ruleset>/*.toml` is today. An
Overlay is a new, optional, **singular** `[overlay]` table inside the
*existing* `projects/<id>/project.toml` — one table per project, containing
**arrays** for however many Packs, evidence bindings, and accepted-evidence
methods that project actually has (§3.5, §5). There is no per-Pack overlay
file and no `[[overlay]]` array-of-tables at the top level: a project has one
Overlay, and that Overlay may reference several Packs.

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
  own rule.** A project's Overlay names the Pack(s) it uses; each Pack is
  loaded first (it has no dependency on any project), the Overlay second (it
  depends on the named Packs existing), and there is exactly one place — the
  Overlay's own `packs` list — where that dependency is declared.
- **A Python constants dict was rejected** for the reason `AGENTS.md` already
  gives for constants generally: "what a project contains" belongs in a
  manifest, not in code, and a Pack that lived as a Python module would need a
  code change — and a PR against this package — to add a purpose, which is
  precisely the seam `AGENTS.md` says a fork should not have to touch.
- **Nothing here is a plugin.** No entry points, no registry marketplace, no
  dynamic import. A Pack file that is not on disk under `purpose-packs/` does
  not exist for this repository, exactly as a rule file that is not under
  `rules/` does not exist.
- **Why not go smaller still (fold the Pack into the Overlay, one file per
  project)?** Rejected because it would destroy the one property that
  motivated a Pack at all: a *reusable* purpose question (which activities,
  which evidence requirements, which decision tree) is a different fact from
  a *project's* policy answer (which team, which cost, which bindings) —
  folding them into one file per project would mean every project re-authors
  the MEP → Architecture question from scratch.

---

## 3. Minimal fields and composition rules

Every fragment below is a **design illustration**, not a real artifact. No
`purpose-packs/` directory and no `[overlay]` table are created by this
document, and no example below states a cost, an authorisation, an alignment
confirmation, a handover, or a verdict as if it had happened — every
runtime-shaped value in the fragments is marked `# EXAMPLE, not a live
record`.

### 3.1 Field-level ownership matrix

| Field | Owner | Type shape | Notes |
|---|---|---|---|
| `pack_id` | Pack | slug | Must match its directory name. |
| `pack_schema_version` | Pack | slug | Version of the **file format** — which tables/fields this document uses (§3.4a). |
| `pack_version` | Pack | opaque slug | Version of this Pack's **content**; pinned by exact match, never a range (§3.4b). |
| `maturity` | Pack | enum (`draft`/`reviewed`/`stable`) | Pack metadata only; never read by the Framework. |
| `citations` | Pack | list of strings | Free text, provenance for the Pack author's claims. |
| `direction` | Pack | `{ from: discipline, to: discipline }` | Never derived from `discipline_scope`. |
| `activities[]` | Pack | list of `{ activity_id, label, evidence_requirement_ids[], decision_root_node }` | `activity_id` is **Pack-local**, not global (§5; **closes gap 5**). |
| `evidence_requirements[]` | Pack | list of `{ evidence_requirement_id, answers, binding_source, acceptance_condition, outcomes[], pack_binding?, insufficient_evidence[]? }` | The evidence layer, distinct from validation requirements (§3.2; **closes gap 1**). `evidence_requirement_id` is Pack-local. |
| `evidence_requirements[].pack_binding` | Pack | `{ ruleset_id, ruleset_version, requirement_keys[] }` | Present only when `binding_source = "pack"` — a general validation requirement the Pack may reference directly (§3.3). |
| `evidence_requirements[].insufficient_evidence[]` | Pack | list of `{ ruleset_id, ruleset_version, requirement_key, cannot_answer }` | Records a *related but insufficient* validation pass, e.g. R-010 for `cross-model-alignment` (§3.2, §5). |
| `decision_nodes[]` | Pack | list of `{ node_id, evidence_requirement_id, branches[] }` | Closed decision tree per activity (§3.8; **closes gap 3**). |
| `decision_nodes[].branches[]` | Pack | list of `{ outcome, verdict? , failure_kind?, next_node? }` | Exactly one of `verdict`/`next_node` per branch; every declared `outcome` covered exactly once, checked at Pack load time. |
| `consequence_kinds[]` | Pack | list of `{ activity_id, kinds[] }` | Kind only; no magnitude field exists on a Pack. |
| `default_responsibility[]` | Pack | list of `{ failure_kind, role }` | Keyed by the same `failure_kind` a decision-tree `BLOCKED` leaf names. |
| `source_fix_guidance[]` | Pack | list of `{ evidence_requirement_id, guidance }` | Free text, tool-specific advice as in Checkpoint B's cases. |
| `recheck_conditions[]` | Pack | list of `{ activity_id, condition }` | What evidence would end a block/unknown, stated in advance. |
| `project_id` | Overlay | slug | Already exists on `project.toml`. |
| `overlay.packs[]` | Overlay | list of `{ pack_id, pack_version }` | **Plural** — a project may use several Packs (§5; **closes gap 5**). |
| `overlay.evidence_bindings[]` | Overlay | list of `{ pack_id, evidence_requirement_id, ruleset_id, ruleset_version, requirement_keys[] }` | Satisfies `binding_source = "overlay"` evidence requirements — R-005 lives only here (§3.5; **closes gap 2**). |
| `overlay.accepted_evidence_methods[]` | Overlay | list of `{ pack_id, evidence_requirement_id, method_id, description }` | Satisfies `binding_source = "assessment"` evidence requirements. |
| `overlay.team_mapping[]` | Overlay | list of `{ role, team_or_person }` | Project-wide; roles are shared vocabulary across Packs, not Pack-scoped. |
| `overlay.risk_authorisation` | Overlay | `{ may_authorise: [role...] }` | Who *may* accept a `CONDITIONAL` risk here — not a specific acceptance. |
| `overlay.cost_parameters` | Overlay | project-defined key/value | Magnitude inputs a future runtime step may read; no cost figure is fabricated by this document. |
| `overlay.conventions[]` | Overlay | list of `{ ruleset_id, ruleset_version, requirement_key, note }` | Optional narrative about a project-specific convention (§3.5). |
| `overlay.overrides[]` | Overlay | list of `{ target, permitted_change, note }` | `target` is `<pack_id>::<activity_id or evidence_requirement_id>.<field>`; drawn from a closed enumeration (§3.6). |

Nothing in either table carries a model version, a finding key, an actual
verdict, an actual authoriser, an actual cost, or an actual assignee. Those
stay off both files by construction.

### 3.2 Pack skeleton — design illustration only

```toml
# purpose-packs/mep-to-architecture-coordination/pack.toml
# EXAMPLE, not a live artifact — no such file exists yet.

pack_id = "mep-to-architecture-coordination"
pack_schema_version = "1"
pack_version = "0.1.0"
maturity = "draft"
citations = ["docs/product/interdisciplinary-coordination-readiness-mep-to-architecture.md"]

[direction]
from = "MEP"
to = "Architecture"

# --- Evidence requirements: what an activity needs to know, not who answers it. (closes gap 1) ---

[[evidence_requirements]]
evidence_requirement_id = "asset-identity"
answers = "each equipment element in the assessed scope carries the project's asset identity"
binding_source = "overlay"   # project-specific: the Pack asks the question, the Overlay supplies the answer (closes gap 2)
acceptance_condition = "every requirement_key an Overlay binds to this evidence requirement evaluates PASS, for every applicable element in the assessed scope"
outcomes = ["satisfied", "unmet"]

[[evidence_requirements]]
evidence_requirement_id = "in-model-position"
answers = "each MEP element in the assessed scope is assigned to a storey Architecture also models"
binding_source = "pack"      # a general coordination requirement, not a project convention
acceptance_condition = "every bound requirement_key evaluates PASS for every applicable element in the assessed scope"
outcomes = ["satisfied", "unmet"]

  [evidence_requirements.pack_binding]
  ruleset_id = "epc-delivery"
  ruleset_version = "2.2"
  requirement_keys = [
    "491a4a0b-9b4a-5f77-b90d-31a7dc8beb44",  # R-004A, EXAMPLE citation
    "2ead0930-568e-5d49-9708-716c5c740846",  # R-004B, EXAMPLE citation
  ]

[[evidence_requirements]]
evidence_requirement_id = "cross-model-alignment"
answers = "the producing and consuming models sit on a common, agreed datum"
binding_source = "assessment"   # no validation requirement in rule set 2.2 answers this
acceptance_condition = "a recorded alignment confirmation exists for the named model versions, produced by a method the project's Overlay accepts, and it is affirmative"
outcomes = ["confirmed", "not-yet-confirmed"]

  [[evidence_requirements.insufficient_evidence]]
  ruleset_id = "epc-delivery"
  ruleset_version = "2.2"
  requirement_key = "acb11f11-bf18-5516-a6f2-21e451a6e410"  # R-010, EXAMPLE citation
  cannot_answer = "R-010 witnesses a shared marker (name + cross-model GlobalId) only; a PASS is not alignment evidence and must never be read as satisfying this evidence requirement."

[[evidence_requirements]]
evidence_requirement_id = "penetration-determination"
answers = "whether an MEP element penetrates architectural fabric, and if so which architectural element"
binding_source = "assessment"
acceptance_condition = "a recorded coordination-review determination exists for the named model versions, either naming no penetration or naming the architectural element penetrated"
outcomes = ["no-penetration", "penetration-confirmed", "not-yet-determined"]

[[evidence_requirements]]
evidence_requirement_id = "opening-status"
answers = "whether a corresponding architectural opening exists and is inspectably linked to the penetrating element"
binding_source = "assessment"
acceptance_condition = "the opening is modelled and a recorded cross-reference to the penetrating element exists"
outcomes = ["cross-referenced", "modelled-not-cross-referenced", "not-modelled"]

# --- Activities: which evidence requirements each one needs, and where its decision tree starts. ---

[[activities]]
activity_id = "schedules-and-room-data-sheets"
label = "Room data sheets and equipment schedules"
evidence_requirement_ids = ["asset-identity"]
decision_root_node = "asset-identity-node"

[[activities]]
activity_id = "ceiling-and-bulkhead-geometry"
label = "Reflected ceiling and bulkhead layout"
evidence_requirement_ids = ["in-model-position", "cross-model-alignment"]
decision_root_node = "in-model-position-node"

[[activities]]
activity_id = "builders-work-openings"
label = "Builder's-work openings"
evidence_requirement_ids = ["penetration-determination", "opening-status"]
decision_root_node = "penetration-determination-node"

# --- Decision trees are §3.8. Consequence kinds and responsibility follow. ---

[[consequence_kinds]]
activity_id = "schedules-and-room-data-sheets"
kinds = ["work-cannot-start", "re-identification-and-reissue-risk"]

[[consequence_kinds]]
activity_id = "ceiling-and-bulkhead-geometry"
kinds = ["work-suspended", "rework-risk"]

[[consequence_kinds]]
activity_id = "builders-work-openings"
kinds = ["work-suspended"]

[[default_responsibility]]
failure_kind = "missing-project-asset-identity"
role = "model-coordination"

[[default_responsibility]]
failure_kind = "mep-element-not-spatially-assigned"
role = "mep-lead"

[[default_responsibility]]
failure_kind = "opening-not-verifiably-linked"
role = "model-coordination"

[[default_responsibility]]
failure_kind = "missing-corresponding-opening"
role = "model-coordination"
```

Note what changed from the rejected draft, plainly: there is no
`activities.evidence[].rule_ref` field any more, and no direct pointer from
`builders-work-openings` to nothing. **Openings now names two evidence
requirements**, exactly matching Checkpoint B case 4's two live gaps, and
neither is satisfiable by rule set 2.2 today — which is exactly why the
live verdict stays UNKNOWN under §3.8's tree rather than the previous draft's
unrepresentable silence.

### 3.3 Referencing an existing rule/requirement: the binding triple

Two candidates were compared for how a `pack_binding` or an Overlay
`evidence_bindings` row points at existing validation data:

- **`rule_id`** (e.g. `"R-005A"`) — human-readable, but not what contract 1.6
  actually keys on, and R-005A alone keys two requirements (`AssetTag`,
  `SystemCode`), so it cannot disambiguate within a rule without a second
  field that duplicates `requirement_id`.
- **`requirement_key`** — the actual UUIDv5 published in `findings.csv` and
  `requirements.csv`, built by `build_requirement_key(rule_id,
  requirement_id)` (`epc_control_tower/identity.py:99`) from exactly those
  two stable inputs. It already disambiguates within a multi-requirement rule
  and is the key a runtime assessment would actually join against.

**Chosen: `requirement_key` as the join key, always accompanied by
`ruleset_id` and `ruleset_version`** — never `requirement_key` alone. This is
a correction from the rejected draft, which treated `requirement_key` as
sufficient on its own. It is not, and the reason is exact: `requirement_key`
is built **only** from `(rule_id, requirement_id)`
(`identity.py:99–106`). `build_ruleset_normalized_digest`
(`identity.py:109–164`), by contrast, hashes the requirement's `severity`,
`owner_role`, `stage`, `discipline_scope`, `citation`, `priority`, `labels`,
and `checker` — every field that gives the requirement its actual meaning —
alongside `rule_id` and `requirement_id`. A rule author can therefore change
what R-005A *means* — its severity, its owning discipline, its checker —
without moving its `requirement_key` at all, and that change **does** move
`ruleset_normalized_digest` and every `validation_run_id` built from it
(§4). **`requirement_key` proves you found the right row; it does not prove
the row still means what a Pack or Overlay author assumed it meant.** That is
exactly why every binding in this design — Pack-owned or Overlay-owned —
carries `ruleset_id` and `ruleset_version` alongside the key, and why
composition checks all three together and fails closed on a mismatch (§3.7):
a binding pinned to `epc-delivery` version `2.2` does not silently keep
resolving against a `2.3` in which the same `requirement_key` survived but
its severity or applicability changed underneath it.

### 3.4 Three separate compatibilities, not one (closes gap 4)

The rejected draft's `compatible_framework = ">=1.6,<2.0"` conflated three
different questions into one field that named a compatibility surface —
"Framework version" — that does not exist as a published, versioned machine
contract today. `contract 1.6` is the *data contract's* identity, and rule
set `2.2` is the *ruleset's* identity; neither is "the Framework's version" in
the sense a Pack could declare compatibility against, and calling one of them
that was the error. Three genuinely separate compatibilities replace it:

**a) Pack file/schema format version — `pack_schema_version`.** Names the
*shape* this `pack.toml` file is written against: which tables and fields a
loader must understand to parse it at all (e.g. whether `evidence_requirements`
and `decision_nodes` exist as described here, or a later, differently-shaped
revision of the format). It changes only when the Pack *file format* changes,
never when one Pack's content changes. A future loader that does not
implement a given `pack_schema_version` refuses the file (§3.7).

**b) Pack content version — `pack_version`.** An author-declared **opaque
slug**, not strict semver, validated the same way `ruleset_version` already
is — by `_require_slug` in `identity.py:87–90` (accepts `[A-Za-z0-9][A-Za-z0-9._-]*`,
never parsed into numeric segments or compared with `<`/`>=`). Bumped by the
Pack author whenever activities, evidence requirements, or decision trees
change. An Overlay pins one exact `pack_version` string per `pack_id`
(§3.5), and composition fails closed on any mismatch — never a range match.
Slug-and-exact-match was chosen over strict semver because nothing else in
this codebase parses or compares version ranges, and every consumer of
`pack_version` in this design (the Overlay's own pin) checks it by equality;
introducing range-comparison machinery for a value nothing ever compares as a
range would be new complexity with no consumer, the same judgement `AGENTS.md`
already applies to `ruleset_version`.

**c) Ruleset compatibility — per binding, not per Pack.** Every place a Pack
or an Overlay references existing validation data — an `evidence_requirements
[].pack_binding`, an `insufficient_evidence[]` entry, or an Overlay
`evidence_bindings[]` row — carries its own `{ruleset_id, ruleset_version,
requirement_keys[]}` (§3.3), checked independently at composition. There is
no single Pack-wide "compatible ruleset" field, because a Pack's different
evidence requirements may legitimately have been authored against different
ruleset versions — a Pack revised after rule set 2.3 ships may still
correctly reference a `requirement_key` minted under 2.2, provided that
requirement still exists unchanged in 2.3, a distinction a single Pack-wide
version field would erase.

**d) Framework machine-contract compatibility — explicitly deferred, not
faked.** `README.md`'s "Not implemented" section and `AGENTS.md` both treat a
stable, published Framework machine contract as future work, and the
technical director's routing places that surface at **Checkpoint E**, not C.
This document therefore names **no** Framework-compatibility field at all —
not a version string, not a range, not a placeholder. When Checkpoint E
defines what a Framework machine contract's own identity looks like, a
Pack-level compatibility field against *that* becomes designable; inventing
its shape now, or approximating it with contract 1.6's own version number,
would be guessing at a checkpoint's output before that checkpoint runs —
exactly the anti-pattern `Agent-product-manager.md` names for
`AssessmentRun`-shaped objects, applied here to a compatibility field instead
of a runtime type.

### 3.5 Overlay: pointing at Pack(s), project, and R-005 as the worked binding (closes gap 2)

```toml
# projects/pcert-sample/project.toml — EXCERPT, illustrative addition only.
# EXAMPLE, not a live edit — this document changes no tracked file.

[overlay]
project_id = "pcert-sample"

[[overlay.packs]]
pack_id = "mep-to-architecture-coordination"
pack_version = "0.1.0"

# --- Satisfies the Pack's "asset-identity" evidence requirement. This binding,
#     and only this binding, is where R-005 enters the design — never in the
#     Pack file. Exactly the four requirement_keys R-005A/B key, not the six
#     findings a run against them happens to produce today. ---

[[overlay.evidence_bindings]]
pack_id = "mep-to-architecture-coordination"
evidence_requirement_id = "asset-identity"
ruleset_id = "epc-delivery"
ruleset_version = "2.2"
requirement_keys = [
  "842a37c7-3183-5fce-ab45-b93c37ec7a08",  # R-005A AssetTag
  "9321298b-4a9f-5a3e-9d10-6668b736d465",  # R-005A SystemCode
  "a1402559-dcfc-5af4-a222-3a13eaf2b161",  # R-005B AssetTag
  "fd49c300-7ef6-5a8d-825f-53210dd579fe",  # R-005B SystemCode
]

# --- Satisfies the Pack's "cross-model-alignment" evidence requirement,
#     which no validation requirement can ever answer. ---

[[overlay.accepted_evidence_methods]]
pack_id = "mep-to-architecture-coordination"
evidence_requirement_id = "cross-model-alignment"
method_id = "overlay-comparison"
description = "Placements from both models overlaid in a common viewer and visually confirmed by model-coordination."

[[overlay.team_mapping]]
role = "model-coordination"
team_or_person = "coordination-team"  # EXAMPLE — no real assignment exists

[[overlay.conventions]]
ruleset_id = "epc-delivery"
ruleset_version = "2.2"
requirement_key = "842a37c7-3183-5fce-ab45-b93c37ec7a08"  # EXAMPLE
note = "EPC_Delivery.AssetTag is pcert-sample's own convention, not a general obligation."
```

Why this closes the gap: the Pack's `asset-identity` evidence requirement
(§3.2) asserts only that the activity needs *an* asset identity — it never
names `EPC_Delivery`, `AssetTag`, or any `requirement_key`. The fact that this
particular property is a project-specific assumption is asserted once, in the
rule file itself (`rules/epc-delivery/R-005A.toml`'s own
`labels = ["IDS", "ProjectAssumption"]`), which is rule data, not new Pack
data. What the Overlay adds is the actual binding — a second project could
bind `asset-identity` to its own, entirely different rule keys (or to a
different ruleset altogether) and the Pack file would not change by one byte.
**A project whose Overlay omits this binding entirely has an
`asset-identity`-requiring activity that fails closed for that project**
(§3.7) — it does not fall back to R-005 by default, because there is no
default: the Pack does not know R-005 exists.

**Overlay → future runtime assignment (rows 8a–8c)** composes exactly as
before: the Pack's `default_responsibility` names an abstract role for a
`failure_kind`; the Overlay's `team_mapping` names this project's actual
team for that role; a future runtime step composes the two into an actual
assignment, which is a runtime fact (row 8c) recorded nowhere in either file.

### 3.6 Overrides: explicit and enumerated, never a general patch

`overlay.overrides[]` is a **closed list of named override kinds**, each
naming exactly which Pack field it may change and how. A `target` now
disambiguates which Pack the override applies against, since a project may
use several:

```toml
[[overlay.overrides]]
target = "mep-to-architecture-coordination::ceiling-and-bulkhead-geometry.recheck_condition"
permitted_change = "narrow-scope"   # a named, enumerated kind — not free text
note = "This project recheck's alignment confirmation only for ground-floor zones."
```

An override kind is drawn from a fixed enumeration the Pack format defines
(e.g. `narrow-scope`, `add-accepted-evidence-method`) — never an arbitrary
key/value patch, and never a target inside `decision_nodes`, `direction`, or
any Framework-facing field.

**What an Overlay can never override, stated affirmatively:** the Framework's
four verdict words and their six invariants (§1); a Pack's `direction`; a
Pack's decision tree (§3.8), including which evidence requirement any node
tests; and anything in the runtime-assessment column of Checkpoint B §5's
table. An Overlay may *add* an evidence binding or an accepted method where a
Pack requires one (`binding_source = "overlay"` / `"assessment"`); it may
never *redirect* a `binding_source = "pack"` evidence requirement's own
`pack_binding` to different `requirement_key`s. An override attempting any of
those is a composition error under §3.7, not a permitted override.

### 3.7 Composition and fail-closed behaviour

Composition order is fixed by the file layout chosen in §2: load every Pack
named by `overlay.packs[]`, then load the Overlay, then check the whole set
together. Every case below fails closed rather than silently substituting a
default, mirroring `AGENTS.md`'s "a delivery requirement the pipeline
silently declines to evaluate is the worst outcome available":

| Situation | Behaviour |
|---|---|
| `overlay.packs[].pack_id` names a Pack not present under `purpose-packs/` | Fail closed. No Pack is substituted. |
| `overlay.packs[].pack_version` does not match the named Pack's declared `pack_version` | Fail closed — exact match only, never a range (§3.4b). |
| A Pack's `pack_schema_version` is not one a future loader implements | Fail closed at load, before any project is even considered. |
| A `pack_binding` or an Overlay `evidence_bindings[]` row names a `{ruleset_id, ruleset_version}` that does not match the ruleset actually loaded | Fail closed (§3.3, §3.4c) — this replaces the rejected draft's single `compatible_framework` check. |
| A binding's `requirement_keys[]` contains a key absent from the loaded, matching-version ruleset | Fail closed. |
| An evidence requirement declares `binding_source = "overlay"` and the project's Overlay has no `evidence_bindings[]` entry naming the same `pack_id` + `evidence_requirement_id` | Fail closed for any activity that needs it (**closes gap 2** — the exact case R-005 exercises when a project opts in with no binding). |
| An evidence requirement declares `binding_source = "assessment"` and the Overlay has no matching `accepted_evidence_methods[]` entry | Fail closed, for the same reason. |
| Two entries in `overlay.packs[]` name the same `pack_id` | Fail closed as a duplicate. |
| **Two different Packs used by one project's Overlay declare the same local `activity_id` or `evidence_requirement_id`** | **Not an error.** `activity_id` and `evidence_requirement_id` are Pack-local; the actually-unique reference is the compound `pack_id::activity_id` (or `::evidence_requirement_id`), which cannot collide once `pack_id` itself is unique — the same relationship `model_id`/`model_key` already have (`AGENTS.md`, "Adding a project should not touch this package"). This is a correction of the rejected draft, which asserted a collision rule it never actually needed (**closes gap 5**). |
| A decision node's `branches[]` does not cover every `outcome` its `evidence_requirement_id` declares, covers one twice, or a branch carries both `verdict` and `next_node` | Fail closed **at Pack load time**, before any project ever uses it — stronger than a runtime check (**closes gap 3**). |
| A decision node's branch names `verdict = "CONDITIONAL"` | Fail closed at Pack load time. `CONDITIONAL` is not a legal leaf value anywhere in a decision tree (§3.8). |
| `overlay.overrides[].target` names a field not on the closed override enumeration, or a field listed under "never overridable" (§3.6) | Fail closed as an illegal override, not applied and not ignored. |
| **A project's `project.toml` has no `[overlay]` table at all** | **Not an error.** The project simply has no purpose assessment available. `epc-ct run`, `check`, `group`, and every exporter are completely unaffected, because nothing in the current pipeline reads `[overlay]` (**closes gap 5**). |
| **A purpose assessment is explicitly requested for a `pack_id` the project's Overlay does not list under `overlay.packs[]`** | **Fail closed for that request only.** The project's existing contract 1.6 pipeline continues to run normally; only the specific unbound purpose-assessment request is refused (**closes gap 5**). |

No situation above resolves by picking a default, by taking the first match
in an unordered collection, or by reading anything time-dependent — composing
Pack and Overlay is required to be as deterministic as everything else this
repository publishes (`AGENTS.md` rule 1).

### 3.8 Verdict / blocker decision logic: a closed decision tree (closes gap 3)

The rejected draft named a `table_id` and deferred the actual shape to
Checkpoint D. That is corrected here: this section fixes the **data
structure** a Pack's verdict logic takes. No evaluator that walks it is
implemented — only the shape a future evaluator would read.

**Shape.** Each activity names one `decision_root_node`. A decision node
names one `evidence_requirement_id` and a set of `branches`, one per outcome
that evidence requirement declares (§3.1, §3.2). A branch is a leaf —
`{ outcome, verdict, failure_kind? }`, where `verdict` is restricted to
`READY`, `BLOCKED`, or `UNKNOWN` and `failure_kind` is present only when
`verdict = "BLOCKED"` and must match a `default_responsibility[].failure_kind`
— or an interior branch — `{ outcome, next_node }`, pointing at another node
that tests a different evidence requirement. A branch never carries both
`verdict` and `next_node`. This is a labelled decision tree: closed,
enumerable, no wildcard, no default branch, no expression language — every
branch is one outcome value mapping to exactly one leaf or one deeper node,
checked exhaustively against the evidence requirement's own declared
`outcomes[]` at Pack-load time (§3.7).

This structure was chosen over a flat table of `(evidence outcome
combinations) → verdict` rows because a flat table cannot express "evaluate
`opening-status` only when `penetration-determination = penetration-confirmed`"
without either a wildcard for the outcomes that don't matter (banned) or an
exhaustive cross-product that manufactures meaningless rows for combinations
that can never be asked (e.g. an opening's cross-reference status when no
penetration exists). A tree expresses conditional relevance structurally: a
node for `opening-status` is only reachable down the branch where
`penetration-determination = "penetration-confirmed"`, so it is never asked,
and never needs an answer, on the other two branches.

`decision_nodes` is a **Pack-top-level array**, not nested inside
`activities` — a node is reached only by `activity.decision_root_node` or by
another node's `next_node`, so nothing about tree membership needs a TOML
parent/child nesting, and nesting it under a repeated `[[activities]]` array
would in any case bind ambiguously to whichever activity table TOML last saw,
not to the one a reader intends. `node_id` is unique within the Pack file,
checked the same way `activity_id` and `evidence_requirement_id` are (§3.7).

```toml
# purpose-packs/mep-to-architecture-coordination/pack.toml — continued.
# EXAMPLE, not a live artifact.

[[decision_nodes]]
node_id = "asset-identity-node"
evidence_requirement_id = "asset-identity"

  [[decision_nodes.branches]]
  outcome = "satisfied"
  verdict = "READY"

  [[decision_nodes.branches]]
  outcome = "unmet"
  verdict = "BLOCKED"
  failure_kind = "missing-project-asset-identity"

[[decision_nodes]]
node_id = "in-model-position-node"
evidence_requirement_id = "in-model-position"

  [[decision_nodes.branches]]
  outcome = "satisfied"
  next_node = "cross-model-alignment-node"

  [[decision_nodes.branches]]
  outcome = "unmet"
  verdict = "BLOCKED"
  failure_kind = "mep-element-not-spatially-assigned"

[[decision_nodes]]
node_id = "cross-model-alignment-node"
evidence_requirement_id = "cross-model-alignment"

  [[decision_nodes.branches]]
  outcome = "confirmed"
  verdict = "READY"

  [[decision_nodes.branches]]
  outcome = "not-yet-confirmed"
  verdict = "UNKNOWN"

[[decision_nodes]]
node_id = "penetration-determination-node"
evidence_requirement_id = "penetration-determination"

  [[decision_nodes.branches]]
  outcome = "no-penetration"
  verdict = "READY"

  [[decision_nodes.branches]]
  outcome = "not-yet-determined"
  verdict = "UNKNOWN"

  [[decision_nodes.branches]]
  outcome = "penetration-confirmed"
  next_node = "opening-status-node"

[[decision_nodes]]
node_id = "opening-status-node"
evidence_requirement_id = "opening-status"

  [[decision_nodes.branches]]
  outcome = "cross-referenced"
  verdict = "READY"

  [[decision_nodes.branches]]
  outcome = "modelled-not-cross-referenced"
  verdict = "BLOCKED"
  failure_kind = "opening-not-verifiably-linked"

  [[decision_nodes.branches]]
  outcome = "not-modelled"
  verdict = "BLOCKED"
  failure_kind = "missing-corresponding-opening"
```

Every leaf in the three trees above reproduces a verdict Checkpoint B already
worked out by hand: `asset-identity → unmet` is case 2's live BLOCKED;
`in-model-position → satisfied, cross-model-alignment → not-yet-confirmed` is
case 3's live UNKNOWN; `penetration-determination → not-yet-determined` is
case 4's live UNKNOWN. The remaining leaves are case 3 and case 4's own
counterfactuals — an alignment confirmed, a penetration ruled out, an opening
found and cross-referenced, or found and not — none of which is live evidence
today, and none of which this document asserts as having happened.

**`CONDITIONAL` is structurally excluded, not merely discouraged.** No branch
in any tree may set `verdict = "CONDITIONAL"` (§3.7), because a tree only ever
consumes evidence-requirement outcomes, and Checkpoint B's invariant 6 is that
`CONDITIONAL` must originate in a named authorisation event — a fact no
evidence outcome can encode. What a future runtime step may do instead is
**promote** a tree's `BLOCKED` or `UNKNOWN` result to `CONDITIONAL` for one
specific assessment, citing the named authoriser, the accepted risk, the
release scope, and the voiding condition — a runtime record layered on top of
the tree's result, never a change to the tree, and never derived from the
tree alone.

---

## 4. Identity and determinism

Fixed boundaries, checked against the actual identity code rather than
asserted from memory:

- **`validation_run_id`** is built by `build_validation_run_id(...)`
  (`epc_control_tower/identity.py:167`) from **six** input categories —
  `ruleset_id`, `ruleset_version`, `ruleset_normalized_digest`, `models`,
  `checkers`, and `as_of` (correcting the rejected draft's count of five).
  None of the six is Pack or Overlay data; a Pack or Overlay file existing,
  changing, or being deleted cannot move this value.
- **`requirement_key`** is built by `build_requirement_key(rule_id,
  requirement_id)` (`identity.py:99`) — again, no Pack/Overlay input, and, as
  §3.3 establishes, **not by itself proof that a bound requirement still
  means what a Pack or Overlay author assumed** — only `ruleset_id` +
  `ruleset_version`, checked alongside the key at composition, close that
  gap.
- **`finding_key`**, `Issue`/legacy identity, and every downstream contract
  1.6 artifact are derived transitively from the same rule-set and model
  data, never from Pack or Overlay content. Nothing in §3.1's field list is
  consumed by `build_ruleset_normalized_digest` (`identity.py:109`), which
  enumerates exactly the `Requirement` fields it hashes and does not include
  a Pack or Overlay reference among them.
- **No clock, no unordered iteration, no machine-dependent path.** Every
  composition rule in §3.7 is a lookup or a membership check, and the field
  list in §3.1 contains nothing that reads `datetime.now()` or a filesystem
  ordering. A future Pack/Overlay content-identity value (if one is ever
  minted, e.g. a `pack_content_sha256` analogous to
  `ruleset_normalized_digest`) must be built the same way that digest is: a
  deterministic hash of parsed, sorted structure — never of raw file bytes.
  This document does not mint that value; it only fixes the constraint it
  must satisfy when Checkpoint D or a later checkpoint does.
- **Runtime/assessment identity is explicitly deferred.** Nothing here names
  an `AssessmentRun` id, a verdict id, or any other runtime-scoped
  identifier. That is Checkpoint D's decision.

### Changed-input counterfactuals a future implementation must run

Four tests, stated now so Checkpoint D's implementation is judged against a
commitment made before the code exists. **All four require the entire
published output tree — `data/processed/`, `reports/`, and the
`contract-1.6.json` manifest — to be byte-for-byte unchanged, with no
exception carved out for any case, correcting the rejected draft's fourth
test, which excused a new project's own rows.**

1. **Change only a Purpose** — edit a Pack's `evidence_requirements`,
   `decision_nodes`, or `default_responsibility` (anything in §3.1's Pack
   column); touch no project. Expected: `git diff --exit-code -- data/processed
   reports` passes; `epc-ct snapshot` reports no drift; every
   `validation_run_id`, `requirement_key`, and `finding_key` in
   `data/processed/canonical/` is byte-identical; `contract-1.6.json`'s
   recorded file list and SHA-256s are unchanged.
2. **Change only an Overlay** — edit `pcert-sample`'s `[overlay]` table
   (`evidence_bindings`, `team_mapping`, `cost_parameters`, `conventions` —
   anything in §3.1's Overlay column); touch no model, ruleset, or
   programme. Expected: identical to (1), for **the entire published output
   tree of both projects**, not merely "the other project's rows" — nothing
   in the pipeline reads `[overlay]` today, so neither project's published
   bytes may move by even one row.
3. **Add a second Pack** — a new file under `purpose-packs/`, referenced by
   no project's `overlay.packs[]`. Expected: identical to (1) — an
   unreferenced Pack on disk must not appear in any published artifact,
   count, or manifest.
4. **Add a second Overlay/Pack binding to the existing `iso-reference-view`
   project** — edit `projects/iso-reference-view/project.toml` to add an
   `[overlay]` table binding it to a Pack (the same one or a different one);
   add **no new project directory, no new model file, no ruleset or
   programme change**. Expected: identical to (1) and (2) — the entire
   published output tree for **both** `pcert-sample` and `iso-reference-view`
   is byte-identical. There is no exception for "the edited project's own
   new rows," because an Overlay addition, by construction, produces no new
   row in any contract 1.6 output today. (Adding an *entirely new project*
   is already `AGENTS.md`'s own, separate counterfactual — "Adding a second
   project, with no scope on the legacy writers" — and is not repeated here;
   this test is Overlay-only, on a project that already exists.)

What the future test plan must actually diff, named precisely so it is not
re-litigated per-run: the full set of `requirement_key`, `finding_key`,
`issue_key`, and `validation_run_id` values present in
`data/processed/canonical/{requirements,findings,issues}.csv`; the row counts
of every published CSV; the byte count and SHA-256 of every file under
`data/processed/` and `reports/`; and the `contract-1.6.json` manifest's
recorded file list. **All four counterfactuals above must leave every one of
those values completely unchanged — no case is exempted.**

---

## 5. Composition cardinality, settled (closes gap 5)

Stated affirmatively, once, so no later section can drift from it:

- **A project may use more than one Purpose Pack.** `overlay.packs[]` is a
  list (§3.1, §3.5).
- **A project has exactly one Overlay** — the singular `[overlay]` table in
  its `project.toml` — which contains the arrays needed to bind however many
  Packs the project actually uses. There is no per-Pack overlay file and no
  `[overlay.<pack_id>]` nesting; every list inside `[overlay]` tags its own
  rows with `pack_id` where disambiguation is needed (`evidence_bindings`,
  `accepted_evidence_methods`), and leaves rows that are naturally
  project-wide untagged (`team_mapping`, `cost_parameters`).
- **`activity_id` and `evidence_requirement_id` are Pack-local identities.**
  Two different Packs may freely reuse the same local name — `schedules`, say
  — with no collision, because the identity that must be unique is the
  compound `pack_id::activity_id`, and `pack_id` is already required unique.
  This mirrors `model_id` (project-scoped, human-chosen) versus `model_key`
  (`project_id::model_id`, the actually-unique join identity) exactly as
  `AGENTS.md` already draws that line for models.
- **A project with no `[overlay]` table has no purpose assessment, and the
  existing contract 1.6 pipeline is entirely unaffected** — `epc-ct run`,
  `check`, `group`, and every exporter read nothing under `[overlay]` today,
  so its absence changes nothing they do (§3.7).
- **A purpose-assessment request for a Pack the project's Overlay does not
  bind fails closed for that request only** — it never falls through to the
  pipeline failing, and it never silently produces a verdict from an
  unbound Pack (§3.7).

---

## 6. Scenario mapping — Checkpoint B's three activities

Proving §3's shape is sufficient, without designing runtime behaviour:

| Checkpoint B activity | `activity_id` (illustrative) | Evidence requirements | Binding | Live verdict (runtime fact, unaffected by this design) |
|---|---|---|---|---|
| Room data sheets / equipment schedules | `schedules-and-room-data-sheets` | `asset-identity` | Overlay-bound to R-005A/B's four `requirement_key`s (§3.5) | **BLOCKED** (case 2) |
| Ceiling / bulkhead geometry | `ceiling-and-bulkhead-geometry` | `in-model-position`, `cross-model-alignment` | Pack-bound to R-004A/B for the first; `assessment` for the second, with R-010 named only as insufficient evidence | **UNKNOWN** (case 3) |
| Builder's-work openings | `builders-work-openings` | `penetration-determination`, `opening-status` | `assessment` for both — no validation requirement in rule set 2.2 answers either | **UNKNOWN** (case 4) |

**Openings is no longer represented with zero evidence entries.** It names
exactly the two evidence requirements Checkpoint B case 4 describes, both
currently unsatisfiable by rule set 2.2's evidence — which is why the live
verdict stays UNKNOWN and is now *representable* as UNKNOWN, rather than
silently indistinguishable from an activity with no evidence model at all.

Confirmed, restated as constraints this design satisfies rather than data it
asserts:

- The live verdicts (`BLOCKED`, `UNKNOWN`, `UNKNOWN`) are **runtime
  observations**. No field in §3.1's Pack or Overlay columns can hold a
  verdict; §3.2 and §3.8's skeletons contain none as a live fact.
- **R-010 is represented only as a name-plus-cross-model-GlobalId
  shared-marker witness**, listed under `cross-model-alignment`'s
  `insufficient_evidence[]` with its limit stated in the same entry — never
  promoted to alignment evidence by anything in this design.
- **R-010's applicability/checker divergence is out of scope here**,
  unchanged from the prior revision: this document changes nothing about
  `rules/epc-delivery/R-010.toml` or the `completeness` checker and does not
  depend on that divergence being fixed.
- **`discipline_scope` remains validation applicability only.** §3.2's
  `direction` table is new Pack data, never a reinterpretation of
  `discipline_scope`.

---

## 7. Future pipeline boundary (recorded, not built)

Restating the seam from `AGENTS.md` and Checkpoint B §5, unchanged:

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
types, does not implement an evaluator for the decision trees in §3.8, and
does not schedule any of it. It only confirms that the Pack/Overlay shape
designed in §§2–5 is data such a stage could read without requiring any
change to §1's ownership boundary.

---

## 8. Explicitly out of scope for this document

No `AssessmentRun`, `AssessmentItem`, `EvidenceGap`, `BlockerCandidate`, or
other runtime assessment object is created, named as approved, or implied to
be forthcoming in a particular shape. No evaluator that walks a decision tree
or resolves an evidence binding is implemented. No code, rule, checker, test,
README, CHANGELOG, or Checkpoint B document is modified. No actual Pack or
Overlay configuration file is added — every fragment in §3 is illustrative
and explicitly marked as such. `data/processed/`, `reports/`, any snapshot,
and contract 1.6 are untouched. No Doctor, Registry, exporter, database, AI
agent, knowledge graph, automatic IFC patching, or cross-run ledger is
designed. Nothing is merged, tagged, or released. Checkpoint D is not
started.

## Consequences

This document commits a future implementation to: two file locations
(`purpose-packs/<pack_id>/pack.toml`, `projects/<id>/project.toml`'s
singular `[overlay]` table, which may bind several Packs); a two-layer
evidence design in which an activity names Pack-owned **evidence
requirements**, never a validation requirement directly, and each evidence
requirement is satisfied by a Pack-owned binding (general validation data), an
Overlay-owned binding (project-specific validation data — R-005's only
correct home), or an Overlay-declared accepted method (evidence produced at
assessment time, never by a validation requirement); `requirement_key`
always paired with `ruleset_id` and `ruleset_version` as the only legal way
anything in this design references existing rule data, because the key alone
proves identity but not semantic version; a closed decision tree, not a flat
table or an expression language, as the shape of verdict/blocker logic,
restricted to `READY`/`BLOCKED`/`UNKNOWN` leaves with `CONDITIONAL` reachable
only as a runtime promotion; three independent compatibility axes — Pack
schema format, Pack content version, and per-binding ruleset identity — with
Framework machine-contract compatibility named as not yet nameable rather
than fabricated; a project that may use multiple Packs through one Overlay,
with Pack-local `activity_id`/`evidence_requirement_id` disambiguated only by
`pack_id`; fail-closed composition with no silent defaults, including a
project with no Overlay leaving the existing pipeline untouched; and the four
changed-input counterfactuals in §4 — all of them, with no exception — as the
acceptance test for Checkpoint D's identity claims. It commits nothing about
how a decision tree is actually evaluated at runtime, how `AssessmentRun`-
shaped state (if any) is named, or when Checkpoint D begins — those remain
open, and deliberately so.
