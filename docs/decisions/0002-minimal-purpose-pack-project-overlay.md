# 0002 — Minimal Purpose Pack + Project Overlay: representation and ownership

- **Status:** Proposed. This is a data-design decision for review, not an
  implementation. No code, rule, checker, test, schema, configuration file,
  CLI, loader, or generated artifact is added or changed by this document.
- **Date:** 2026-08-27.
- **Revision history:**
  - Supersedes the version at `bc4a142` (2026-08-26), which technical-director
    review **REJECTED** for six reasons: it treated an activity's necessary
    evidence as identical to an existing validation requirement, so
    `ceiling-and-bulkhead-geometry`'s alignment confirmation and
    `builders-work-openings`'s penetration/opening evidence had nowhere to be
    written down and openings ended up with no evidence entry at all,
    contradicting Checkpoint B's own UNKNOWN reasoning; it hard-coded R-005's
    `requirement_key`s into Pack core instead of the Overlay; it deferred
    verdict/blocker decision logic entirely to Checkpoint D instead of fixing
    a data shape now; it invented a single "Framework version" compatibility
    field where three distinct compatibilities exist and one of them is not
    yet nameable; it used a singular `overlay.uses_pack` while also discussing
    multi-Pack activity collisions, and left Pack/Overlay cardinality
    otherwise unsettled; and its fourth changed-input counterfactual added a
    whole new project and then excused that project's own new rows from the
    zero-byte claim. All six were closed at `955ddad`, each marked **(closes
    gap N)**.
  - Supersedes the version at `955ddad` (2026-08-27), which technical-director
    review **REJECTED again** for six further reasons: the evidence outcome
    vocabularies for `cross-model-alignment` and `opening-status` omitted a
    "the method was run and came back negative" state, so a real misalignment
    or a confirmed-absent opening had no way to reach `BLOCKED` and every
    non-`READY` result silently read as `UNKNOWN`; only `BLOCKED` leaves
    carried a responsibility key, so an `UNKNOWN` leaf could never resolve to
    an assignable role; the illustrative Overlay supplied an accepted evidence
    method for only one of the three assessment-bound evidence requirements,
    so the worked example could not actually compose all three activities; the
    Overlay carried its own `project_id` duplicating `[project].project_id`
    in the same file; the decision tree's structural soundness rested only on
    branch-outcome completeness, with no stated check for dangling nodes,
    cycles, unreachable roots, or a node testing an evidence requirement its
    activity never declared; and the one override example's `target` string
    did not correspond to any real field path, since `recheck_conditions[]`
    is a top-level array, not a field nested on an activity. All six were
    closed at `2cc54e5`, each marked **(closes R2 gap N)**.
  - Supersedes the version at `2cc54e5` (2026-08-27), which technical-director
    review **REJECTED a third time** for three further reasons: the
    validation-backed evidence definitions let one assessed scope satisfy
    `unmet` and `not-yet-evaluated` simultaneously whenever it contained both
    a `FAIL` and an uncovered element, so a single evidence requirement could
    reach two outcomes at once, and the assessment-bound evidence
    requirements never said how a multi-element or multi-zone scope collapses
    to one outcome either; only five of the ten `resolution_kind` entries had
    a real project team mapping (`model-coordination`, never `mep-lead`), so
    the worked Overlay could not actually compose a full assignment for the
    two `mep-lead`-owned leaves; and the claim that acyclicity alone gives
    every node "exactly one parent chain back to its activity's root" was
    false — an acyclic graph can still merge branches into a shared
    downstream node — which meant invariant 8 (a node exists somewhere in the
    tree) was never actually sufficient to prove a `READY` path tests every
    evidence requirement it needs, only that a node for it exists *somewhere*
    in the Pack. All three were closed at `8b82820`, each marked **(closes
    R3 gap N)**.
  - Refines the version at `8b82820` (2026-08-27), which technical-director
    review returned **CONDITIONAL**, not yet cleared to land, for two
    remaining closures: the claim that verdict-class priority
    (`BLOCKED > UNKNOWN > READY`) was a *complete* deterministic aggregation
    function for any assessed scope was too strong — class priority decides
    which Framework class a scope's result falls into, not which *named*
    outcome to pick when a scope's underlying observations disagree across
    two distinct named outcomes that carry different `failure_kind`/
    `gap_kind`/`next_node`/`renders_inapplicable` semantics, whether or not
    those outcomes share a class; and `renders_inapplicable`'s own structural
    rules were incomplete — nothing yet forbade duplicate entries, a branch
    naming its own tested evidence requirement inapplicable, or a descendant
    node retesting evidence an ancestor had already ruled out. Both are
    closed below, each marked **(closes R4 gap N)**.
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
  (§3.8; **closes gap 3**). Every `READY` path is checked, node by node, to
  either test or structurally rule out every evidence requirement the
  activity declares — an outcome that merely *exists* in the tree is not
  enough (§3.8, invariant 12; **closes R3 gap 3**).
- Reusable consequence *kinds* (work cannot start; rework risk; re-issue risk;
  work suspended) — never a magnitude, which no Pack has evidence for.
- Default responsibility policy, keyed by the same `resolution_kind` a
  decision-tree leaf names — a `BLOCKED` leaf's `failure_kind` or an
  `UNKNOWN` leaf's `gap_kind`, both drawn from one shared namespace — which
  role answers for a kind of failure *or* a kind of unresolved gap, in the
  abstract (Checkpoint B §5 row 8a; §3.8; **closes R2 gap 2**). `UNKNOWN` is
  not exempt from this: not knowing something still needs a role tasked with
  finding out.
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
  into this project's actual assignee (row 8b) — covering every role a
  requested activity's reachable `BLOCKED` or `UNKNOWN` leaves can name, not
  only `BLOCKED` ones, and never substituting the bound rule's `owner_role`
  or the bare Pack role name when a mapping is missing (§3.5; **closes R3
  gap 2**).
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
a Pack's decision tree, the blocker or gap actually found, the resolving
role/team actually assigned from whichever `resolution_kind` the reached leaf
carries — `BLOCKED`'s `failure_kind` or `UNKNOWN`'s `gap_kind`, composed
through the same 8a-through-8b chain either way (row 8c) — the actual actor
(row 8d, alongside 8c, never instead of it), any risk acceptance actually
given — which is the only thing that may **promote** a tree's `BLOCKED` or
`UNKNOWN` result to `CONDITIONAL`, and which must carry the promoted leaf's
original verdict, its `resolution_kind`, the accepted risk, and the
underlying evidence gap or blocker forward rather than replacing them (§3.8)
— and exit/recheck status.

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
| `decision_nodes[]` | Pack | list of `{ node_id, evidence_requirement_id, branches[] }` | Closed decision tree per activity (§3.8; **closes gap 3**, **closes R2 gap 5**). |
| `decision_nodes[].branches[]` | Pack | list of `{ outcome, verdict?, failure_kind?, gap_kind?, next_node?, renders_inapplicable? }` | Exactly one of `verdict`/`next_node` per branch; `verdict = "BLOCKED"` requires `failure_kind`, `verdict = "UNKNOWN"` requires `gap_kind`, `verdict = "READY"` requires neither; every declared `outcome` covered exactly once, checked at Pack load time (**closes R2 gap 1, gap 2**). `renders_inapplicable[]` names sibling `evidence_requirement_id`s this outcome structurally rules out further down the path — duplicate-free, never the branch's own `evidence_requirement_id`, and never retested by any later node on the same path (§3.8 invariants 12–15; **closes R3 gap 3, closes R4 gap 2**). |
| `consequence_kinds[]` | Pack | list of `{ activity_id, kinds[] }` | Kind only; no magnitude field exists on a Pack. |
| `default_responsibility[]` | Pack | list of `{ resolution_kind, role }` | One shared namespace: `resolution_kind` matches either a `BLOCKED` leaf's `failure_kind` or an `UNKNOWN` leaf's `gap_kind` — every leaf of either verdict resolves to a role this way (**closes R2 gap 2**). `resolution_kind` is unique across the list, so every leaf resolves to *exactly* one entry (**closes R3 gap 2**). |
| `source_fix_guidance[]` | Pack | list of `{ evidence_requirement_id, guidance }` | Free text, tool-specific advice as in Checkpoint B's cases. |
| `recheck_conditions[]` | Pack | list of `{ activity_id, condition }` | What evidence would end a block/unknown, stated in advance; the only field an override's `field = "recheck_condition"` addresses (§3.6; **closes R2 gap 6**). |
| `overlay.packs[]` | Overlay | list of `{ pack_id, pack_version }` | **Plural** — a project may use several Packs (§5; **closes gap 5**). |
| `overlay.evidence_bindings[]` | Overlay | list of `{ pack_id, evidence_requirement_id, ruleset_id, ruleset_version, requirement_keys[] }` | Satisfies `binding_source = "overlay"` evidence requirements — R-005 lives only here (§3.5; **closes gap 2**). |
| `overlay.accepted_evidence_methods[]` | Overlay | list of `{ pack_id, evidence_requirement_id, method_id, description }` | Satisfies `binding_source = "assessment"` evidence requirements. |
| `overlay.team_mapping[]` | Overlay | list of `{ role, team_or_person }` | Project-wide; roles are shared vocabulary across Packs, not Pack-scoped. `role` is unique across the list — every default role a requested activity's reachable non-`READY` leaves might need resolves to exactly one `team_or_person`, or the specific request fails closed (§3.7; **closes R3 gap 2**). |
| `overlay.risk_authorisation` | Overlay | `{ may_authorise: [role...] }` | Who *may* accept a `CONDITIONAL` risk here — not a specific acceptance. |
| `overlay.cost_parameters` | Overlay | project-defined key/value | Magnitude inputs a future runtime step may read; no cost figure is fabricated by this document. |
| `overlay.conventions[]` | Overlay | list of `{ ruleset_id, ruleset_version, requirement_key, note }` | Optional narrative about a project-specific convention (§3.5). |
| `overlay.overrides[]` | Overlay | list of `{ pack_id, activity_id, field, permitted_change, note }` | `field` is drawn from a closed enumeration of real Pack sub-fields, addressed structurally, not by a dotted string (§3.6; **closes R2 gap 6**). |

Nothing in either table carries a model version, a finding key, an actual
verdict, an actual authoriser, an actual cost, or an actual assignee. Those
stay off both files by construction.

**The Overlay has no `project_id` field of its own (closes R2 gap 4).** It is
a table nested inside the same `project.toml` that already declares
`[project].project_id`, and there is exactly one Overlay per project (§5), so
an Overlay's project identity is simply *the project whose file it is in* —
inherited by nesting, never restated. The rejected round-2 draft's
`overlay.project_id = "pcert-sample"` line duplicated an identity that already
exists one table up in the same file. The fix is to delete the field, not to
add a rule checking the two agree: a field that cannot exist cannot drift out
of sync with the one it would have duplicated, which is a stronger guarantee
than a consistency check on two copies would have been.

### 3.2 Pack skeleton — design illustration only

**Every evidence requirement's `outcomes[]` must partition into exactly the
three states the Framework's own verdict semantics already distinguish (§1;
closes R2 gap 1):**

- an outcome meaning evidence was produced **and satisfies its
  `acceptance_condition`**, with nothing yet found to block or leave
  undecided *from this evidence requirement alone*;
- an outcome meaning evidence was produced **but fails its
  `acceptance_condition`** — a method was run and came back negative, a
  requirement was evaluated and failed;
- an outcome meaning **no admissible evidence exists yet** — the method was
  never run, produced no result for this assessment, or the pipeline never
  evaluated the applicable scope at all.

**An evidence outcome is not itself a Framework verdict (closes R3 gap 1).**
The three states above name what a decision-tree *branch* does with an
outcome, not what the outcome *is*: the first state's branch is either a
`READY` leaf, if this was the last evidence requirement on the activity's
path, or a `next_node` continuing to a further node that tests a different
evidence requirement the same activity also needs (§3.8) — `in-model-position`'s
own `satisfied` outcome is exactly this case, routing to
`cross-model-alignment-node` rather than to `READY`. The second and third
states' branches are always leaves (`BLOCKED` and `UNKNOWN` respectively),
because a failed or absent piece of evidence can never be rescued by a later
node. **Only a decision-tree terminal leaf is the activity's verdict; an
evidence outcome by itself never is.**

The rejected round-2 draft's `cross-model-alignment` and `opening-status`
vocabularies were incomplete on exactly this point: `cross-model-alignment`
had no outcome for "the alignment was checked and the models do not agree,"
and `opening-status` conflated "checked and the opening isn't there" with
"never checked," both of which silently collapsed the middle, `BLOCKED`,
state into `UNKNOWN`. Every `outcomes[]` list below now names all three
states explicitly.

**This is separate from, and must never be confused with, a
composition-time failure.** An evidence requirement whose `binding_source`
names a binding the Overlay never supplied never reaches an outcome at all —
Pack+Overlay composition fails closed before any activity is assessed
(§3.7). An outcome value is only ever produced once a binding exists *and*
an assessment actually runs against it: **`not-yet-evaluated` /
`not-yet-confirmed` / `not-yet-determined` describe a binding that exists
but has not yet produced an admissible result for this particular
assessment — never a missing binding.** A missing binding is a Pack+Overlay
authoring error, caught before anything is assessed; an unresolved outcome
is a fact about one assessment of one pair of model versions, exactly as
undecided today as it may be resolved tomorrow.

**For validation-backed evidence — `asset-identity`, `in-model-position` —
the same three states read off `PASS`/`FAIL`/coverage directly, and Checkpoint
B case 4's own warning governs the third. A fixed, deterministic priority
order makes the three states mutually exclusive and jointly exhaustive
(closes R3 gap 1):**

1. **`unmet`** — at least one element in the assessed scope that a bound
   `requirement_key` applies to evaluates `FAIL`. Checked **first, and
   unconditionally**: a known unmet requirement makes the evidence
   requirement `unmet` regardless of whether some other element in the same
   scope also happens to be uncovered.
2. **`not-yet-evaluated`** — reached only when no element evaluates `FAIL`,
   and at least one element in the assessed scope is **not covered by any
   evaluation** under the bound `requirement_key`(s) — either because the
   rule's applicability never reaches it at all (an absent finding, exactly
   Checkpoint B case 4's chimney: "the absence of a finding is invisible in
   every count the system reports"), or because this assessment has not yet
   run the evaluation for this handover.
3. **`satisfied`** — reached only when no element evaluates `FAIL` and every
   element in the assessed scope is covered (which, having ruled out `FAIL`,
   means every covered element evaluates `PASS`).

This ordering — a known failure always dominates a mere coverage gap — is
the general rule this design applies for `asset-identity` and
`in-model-position`, and it is safe to use as a **complete outcome
selector**, not merely a class selector, for exactly one reason: each of
these two evidence requirements has **exactly one named outcome per
Framework class** — `unmet` is the only `BLOCKED`-shaped outcome,
`not-yet-evaluated` the only `UNKNOWN`-shaped one, `satisfied` the only
`READY`/continuing one — so picking the dominant class and picking the
dominant named outcome are the same operation here. §3.5's worked Overlay
and every live case in §6 use it this way. **A single verdict does not mean
discarding the other facts a mixed scope contains.** Suppose, purely
illustratively, `asset-identity`'s live scope (Checkpoint B case 2's three
HVAC elements, six `FAIL` findings) also included a fourth element never
evaluated under R-005 — `hvac::EXAMPLE`, not a live element. The priority
order still selects exactly one outcome, `unmet`, because the three live
`FAIL`s are checked first and already decide it; the fourth element's
coverage gap never gets a chance to compete for the outcome, and the
evidence requirement never reaches two outcomes at once. Framework invariant
1 (§1) requires exactly one verdict per activity × scope × model-version —
it does not require forgetting that `hvac::EXAMPLE` was also never checked.
Recording that alongside a `BLOCKED` verdict is a legitimate, separate
runtime fact a future assessment step may keep (Checkpoint D); it is
additional detail under one verdict, not evidence of two.

**Verdict-class priority is not, by itself, a complete outcome selector for
every evidence requirement — correcting an overclaim in the previous
revision (closes R4 gap 1).** `BLOCKED > UNKNOWN > READY` decides which
*Framework class* an assessed scope's result falls into; it says nothing
about which *named outcome* to pick when more than one distinct outcome
exists within, or leads into, that class — and several of this Pack's own
evidence requirements have exactly that shape. `opening-status` alone has
**two** distinct `BLOCKED` outcomes, `modelled-not-cross-referenced` and
`not-modelled`, each with its own `failure_kind`; `penetration-determination`'s
`no-penetration` (a `READY` leaf carrying `renders_inapplicable`) and
`penetration-confirmed` (a `next_node` continuing to `opening-status`) are
two distinct outcomes that are not even in the same class. Class priority
cannot choose between two tied-class `BLOCKED` outcomes, and must never be
asked to choose between a terminal `READY` outcome and a continuation —
those lead to structurally different trees.

**The rule, stated precisely:**

- If every underlying observation in an assessed scope reduces to the
  **same named outcome**, that outcome is simply the evidence requirement's
  outcome — plain aggregation, not a choice, and no priority rule is needed
  at all.
- If an assessed scope's underlying observations reduce to **two or more
  different named outcomes** — whether or not they share a Framework class —
  the evidence requirement **must not** pick one by any priority, any text
  or alphabetic ordering, or any silent default. **The assessed scope must
  instead be partitioned into outcome-homogeneous subscopes before the
  decision tree runs at all**, one subscope per distinct named outcome
  actually observed; each subscope then carries exactly one outcome, by
  construction, and follows its own path through the tree — potentially
  reaching its own distinct verdict.

**Two counterexamples, grounded in this Pack's own vocabulary, that a naive
class-priority collapse would get wrong:**

1. **Two penetrations, two distinct `BLOCKED` outcomes — must not be folded
   into one.** Suppose, purely illustratively, `builders-work-openings`'s
   assessed scope contained two confirmed penetrations: `hvac::EXAMPLE-A`,
   whose opening is not modelled at all, and `hvac::EXAMPLE-B`, whose
   opening is modelled but not cross-referenced. Both outcomes are
   `BLOCKED`-class, so class priority is silent on which "wins" — and
   picking either would discard a real, distinct blocker:
   `missing-corresponding-opening` for A is not the same defect as
   `opening-not-verifiably-linked` for B, and the two need different source
   fixes (model the opening at all, versus link the one that already
   exists). The correct handling is two subscopes — `{hvac::EXAMPLE-A}` and
   `{hvac::EXAMPLE-B}` — each independently reaching `opening-status =
   not-modelled` and `opening-status = modelled-not-cross-referenced`, each
   with its own `BLOCKED` verdict and its own `failure_kind`. Folding them
   into one `BLOCKED` outcome would report only one blocker and silently
   drop the other.
2. **One no-penetration, one penetration-confirmed — must not let one
   render the other's evidence inapplicable.** Suppose the same scope
   instead contained `hvac::EXAMPLE-A` with no penetration and
   `hvac::EXAMPLE-C` with a confirmed penetration. These outcomes are not
   even in the same class — `no-penetration` is `READY`-shaped, with
   `opening-status` rendered inapplicable *for that element*;
   `penetration-confirmed` is a continuation that still needs
   `opening-status` tested *for that element*. Aggregating to one outcome
   for the whole scope would either wrongly apply
   `renders_inapplicable = ["opening-status"]` to `hvac::EXAMPLE-C`,
   silently skipping evidence its own penetration still requires, or wrongly
   force `hvac::EXAMPLE-A` through the `opening-status` node it structurally
   cannot need. The correct handling is again two subscopes, evaluated
   independently, each following its own path through
   `builders-work-openings`'s tree.

**Checkpoint D owns how subscopes are actually constructed, identified,
recorded, and — if ever needed — rolled up into a higher-level summary of
the activity; no `Subscope`-shaped runtime object, identity, or aggregation
type is created or named here.** What this document fixes, and only this,
is the constraint any future partitioning must satisfy: an assessed scope
may never be forced through the decision tree as a single unit when its own
underlying observations disagree on the named outcome, whether or not those
outcomes share a Framework class. `asset-identity` and `in-model-position`
need no partitioning, because each has only one named outcome per class to
begin with (above); the assessment-bound evidence requirements in this
Pack — `cross-model-alignment`, `penetration-determination`, `opening-status`
— each describe a single fact about the assessed scope as a whole in this
worked Pack (whether the two models share a datum; whether one penetrating
element penetrates; whether one opening is cross-referenced), so no live
case in §6 exercises partitioning either; a future Pack whose assessed scope
genuinely spans several such facts is exactly where the two counterexamples
above would first bite.

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
acceptance_condition = "every element in the assessed scope that a bound requirement_key applies to evaluates PASS, and every such element is covered by an evaluation at all -- an element with no finding under the binding is not covered, and not-covered is never read as satisfied"
outcomes = ["satisfied", "unmet", "not-yet-evaluated"]

[[evidence_requirements]]
evidence_requirement_id = "in-model-position"
answers = "each MEP element in the assessed scope is assigned to a storey Architecture also models"
binding_source = "pack"      # a general coordination requirement, not a project convention
acceptance_condition = "every element in the assessed scope that a bound requirement_key applies to evaluates PASS, and every such element is covered by an evaluation at all"
outcomes = ["satisfied", "unmet", "not-yet-evaluated"]

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
acceptance_condition = "a recorded alignment confirmation exists for the named model versions, produced by a method the project's Overlay accepts, and it reports the models aligned"
outcomes = ["confirmed", "misaligned", "not-yet-confirmed"]

  [[evidence_requirements.insufficient_evidence]]
  ruleset_id = "epc-delivery"
  ruleset_version = "2.2"
  requirement_key = "acb11f11-bf18-5516-a6f2-21e451a6e410"  # R-010, EXAMPLE citation
  cannot_answer = "R-010 witnesses a shared marker (name + cross-model GlobalId) only; a PASS is not alignment evidence and must never be read as satisfying this evidence requirement, in any of its three outcomes."

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
outcomes = ["cross-referenced", "modelled-not-cross-referenced", "not-modelled", "not-yet-determined"]

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

# default_responsibility is keyed by `resolution_kind`, a single shared
# namespace: every BLOCKED leaf's `failure_kind` and every UNKNOWN leaf's
# `gap_kind` (§3.8) must match exactly one entry here (closes R2 gap 2).
# Not knowing something still needs a role tasked with finding out, so the
# five gap_kind entries below are not optional extras.

[[default_responsibility]]
resolution_kind = "missing-project-asset-identity"   # BLOCKED, asset-identity
role = "model-coordination"

[[default_responsibility]]
resolution_kind = "asset-identity-not-evaluated"      # UNKNOWN, asset-identity
role = "model-coordination"

[[default_responsibility]]
resolution_kind = "mep-element-not-spatially-assigned"   # BLOCKED, in-model-position
role = "mep-lead"

[[default_responsibility]]
resolution_kind = "in-model-position-not-evaluated"      # UNKNOWN, in-model-position
role = "mep-lead"

[[default_responsibility]]
resolution_kind = "cross-model-misalignment"          # BLOCKED, cross-model-alignment
role = "model-coordination"

[[default_responsibility]]
resolution_kind = "cross-model-alignment-not-confirmed"   # UNKNOWN, cross-model-alignment
role = "model-coordination"

[[default_responsibility]]
resolution_kind = "penetration-not-determined"        # UNKNOWN, penetration-determination
role = "model-coordination"

[[default_responsibility]]
resolution_kind = "opening-not-verifiably-linked"     # BLOCKED, opening-status
role = "model-coordination"

[[default_responsibility]]
resolution_kind = "missing-corresponding-opening"     # BLOCKED, opening-status
role = "model-coordination"

[[default_responsibility]]
resolution_kind = "opening-status-not-determined"     # UNKNOWN, opening-status
role = "model-coordination"
```

Ten entries, not four: every `BLOCKED` leaf's `failure_kind` (five of them)
and every `UNKNOWN` leaf's `gap_kind` (five of them) across all three
activities' trees resolves to exactly one role here — the rejected round-2
draft supplied only the five `failure_kind` entries and left every `UNKNOWN`
leaf with nothing to compose a resolving assignment from at all.

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
# No project_id field: this table is nested inside pcert-sample's own
# project.toml, which already declares [project].project_id = "pcert-sample"
# one table up. An Overlay's project identity is inherited by nesting, never
# restated (closes R2 gap 4).

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

# --- Satisfies the three evidence requirements no validation requirement can
#     ever answer. This is policy only -- which method this project would
#     accept as producing each outcome vocabulary in §3.2 -- never a claim
#     that any method has been run, that either model is aligned, that a
#     penetration or an opening has been determined, or that any of these
#     three activities has reached a live verdict other than the one §6
#     already records. (closes R2 gap 3) ---

[[overlay.accepted_evidence_methods]]
pack_id = "mep-to-architecture-coordination"
evidence_requirement_id = "cross-model-alignment"
method_id = "overlay-comparison"
description = "Placements from both models overlaid in a common viewer and visually confirmed by model-coordination; reports confirmed, misaligned, or is simply not yet performed."

[[overlay.accepted_evidence_methods]]
pack_id = "mep-to-architecture-coordination"
evidence_requirement_id = "penetration-determination"
method_id = "coordination-review-determination"
description = "A recorded decision from a joint MEP/Architecture coordination review, naming either no penetration or the specific architectural element penetrated."

[[overlay.accepted_evidence_methods]]
pack_id = "mep-to-architecture-coordination"
evidence_requirement_id = "opening-status"
method_id = "opening-cross-reference-check"
description = "A recorded check that a modelled architectural opening carries a reference back to the penetrating MEP element it was cut for."

[[overlay.team_mapping]]
role = "model-coordination"
team_or_person = "coordination-team"  # EXAMPLE — no real assignment exists

[[overlay.team_mapping]]
role = "mep-lead"
team_or_person = "mep-design-team"  # EXAMPLE — no real assignment exists

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
before, for both verdict shapes: the Pack's `default_responsibility` names an
abstract role for a `resolution_kind` — a `BLOCKED` leaf's `failure_kind` or
an `UNKNOWN` leaf's `gap_kind` alike; the Overlay's `team_mapping` names this
project's actual team for that role; a future runtime step composes the two
into an actual assignment, which is a runtime fact (row 8c) recorded nowhere
in either file.

**This worked Overlay now composes all three Checkpoint B activities, not
one.** `asset-identity` binds to R-005A/B (`evidence_bindings`);
`in-model-position` binds to R-004A/B directly in the Pack (§3.2);
`cross-model-alignment`, `penetration-determination`, and `opening-status`
each have an accepted method above. A project that omitted any one of the
three `accepted_evidence_methods` entries would still load — nothing in this
design requires a project to enable every activity a Pack offers — but
`ceiling-and-bulkhead-geometry` or `builders-work-openings` would fail closed
the moment its unmet evidence requirement was actually assessed (§3.7),
exactly like `asset-identity` without an `evidence_bindings` entry.

**This worked Overlay now closes the full assignment chain for every
`BLOCKED`/`UNKNOWN` leaf the Pack's three trees can reach, not only the
`model-coordination` ones (closes R3 gap 2).** The rejected round-2 draft's
`team_mapping` mapped only `model-coordination`, so the two
`mep-lead`-owned leaves (`mep-element-not-spatially-assigned`,
`in-model-position-not-evaluated`) had a Pack default role with nowhere to
resolve in this project. The two roles the Pack's ten `default_responsibility`
entries actually use are exactly the two `team_mapping` entries above:

| Pack `role` | Used by `resolution_kind`(s) | Overlay `team_or_person` (illustrative) |
|---|---|---|
| `model-coordination` | `missing-project-asset-identity`, `asset-identity-not-evaluated`, `cross-model-misalignment`, `cross-model-alignment-not-confirmed`, `penetration-not-determined`, `opening-not-verifiably-linked`, `missing-corresponding-opening`, `opening-status-not-determined` | `coordination-team` |
| `mep-lead` | `mep-element-not-spatially-assigned`, `in-model-position-not-evaluated` | `mep-design-team` |

This is **project policy for how a role would be staffed, stated in
advance** — it is not this run's assignment, not an actor, and not a claim
that anyone has been tasked with anything. The runtime composition it
enables (rows 8a–8c) still does not exist until Checkpoint D produces one.

**Two things this composition must never do, stated affirmatively:**

- **Never silently fall back to the underlying validation rule's
  `owner_role`.** `AGENTS.md` and Checkpoint B §5 row 8a both already settle
  this: `owner_role` is the role a *rule author* expects to answer for the
  rule — an input a Pack's `default_responsibility` may have been informed
  by, never a substitute for it, and never a substitute for the Overlay's own
  `team_mapping` when that mapping happens to be missing. A missing
  `team_mapping` entry is a fail-closed condition (§3.7), not a cue to read
  `Requirement.owner_role` off the bound rule instead.
- **Never let the abstract Pack `role` string stand in for a project
  assignment.** `role = "mep-lead"` names a category of responsibility, not a
  person or a team; only `overlay.team_mapping`'s `team_or_person` value
  turns it into something a runtime assessment could actually assign work
  to. Reporting `"mep-lead"` itself as though it were an assignee would be
  reporting a Pack default as if it were a project decision.

### 3.6 Overrides: explicit and enumerated, never a general patch (closes R2 gap 6)

`overlay.overrides[]` is a **closed list of named override kinds**, each
naming exactly which Pack field it may change and how. The rejected
round-2 draft addressed a target with a single dotted string —
`"pack_id::activity_id.recheck_condition"` — that did not correspond to any
real field path: `recheck_conditions[]` is a **top-level** Pack array of
`{activity_id, condition}` rows, not a field nested on the `activity` object
itself, so `activity_id.recheck_condition` named a location that does not
exist in §3.1's actual field shapes.

**The fix is structured fields, not a better string grammar.** An override
target is addressed exactly the way the real data is addressed — by walking
the same keys a loader would — rather than through a parser for a path
syntax invented solely for overrides:

```toml
[[overlay.overrides]]
pack_id = "mep-to-architecture-coordination"
activity_id = "ceiling-and-bulkhead-geometry"
field = "recheck_condition"          # closed enum; matches a real Pack array
permitted_change = "narrow-scope"    # a named, enumerated kind — not free text
note = "This project recheck's alignment confirmation only for ground-floor zones."
```

`field` is drawn from a **closed enumeration of real Pack sub-fields**
(today: `"recheck_condition"`, addressing the `condition` of the
`recheck_conditions[]` row whose `activity_id` matches — the only field this
design currently permits an Overlay to narrow). Composition checks, in
order: `pack_id` names a Pack the Overlay actually uses
(`overlay.packs[]`); `activity_id` names a real `pack_id::activity_id`
compound (§5); a `recheck_conditions[]` row with that exact `activity_id`
exists in the named Pack; and `field` is on the closed enum. Any failure
fails closed as an illegal or inapplicable override (§3.7) — never applied,
never ignored. This is not an arbitrary key/value patch mechanism: adding a
second overridable field means extending the closed enum and stating what it
addresses, the same discipline `AGENTS.md` already applies to a checker's own
parameters staying in the rule file rather than becoming a generic payload
every checker must agree on the shape of.

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
| A `BLOCKED` branch has no `failure_kind`, an `UNKNOWN` branch has no `gap_kind`, or a `READY` branch carries either | Fail closed at Pack load time (**closes R2 gap 2**). |
| A branch's `failure_kind` or `gap_kind` does not match **exactly one** `default_responsibility[].resolution_kind` | Fail closed at Pack load time — every `BLOCKED`/`UNKNOWN` leaf must resolve to a role, not just exist (**closes R2 gap 2**). |
| `default_responsibility[]` contains two entries with the same `resolution_kind` | Fail closed at Pack load time as a duplicate — the "exactly one" match above depends on this (**closes R3 gap 2**). |
| `overlay.team_mapping[]` contains two entries with the same `role` | Fail closed at composition time as a duplicate (**closes R3 gap 2**). |
| **A purpose assessment is requested for an activity whose reachable non-`READY` leaves name a default `role` with no matching `overlay.team_mapping[]` entry** | **Fail closed for that request only.** The project's existing contract 1.6 pipeline, and any other activity or Pack this Overlay does bind completely, are unaffected. Never resolved by reading the bound rule's `owner_role` instead, and never reported as though the bare Pack `role` string were itself an assignment (§3.5; **closes R3 gap 2**). |
| A decision node's branch names `verdict = "CONDITIONAL"` | Fail closed at Pack load time. `CONDITIONAL` is not a legal leaf value anywhere in a decision tree (§3.8). |
| `activities[].decision_root_node` does not name an existing `decision_nodes[].node_id` | Fail closed at Pack load time (**closes R2 gap 5**). |
| A branch's `next_node` does not name an existing `decision_nodes[].node_id` | Fail closed at Pack load time (**closes R2 gap 5**). |
| Two `decision_nodes[]` entries share the same `node_id` | Fail closed as a duplicate, at Pack load time (**closes R2 gap 5**). |
| A `decision_nodes[]` entry names an `evidence_requirement_id` that does not exist among the Pack's `evidence_requirements[]` | Fail closed at Pack load time (**closes R2 gap 5**). |
| A node reachable from some activity's `decision_root_node` tests an `evidence_requirement_id` that activity's own `evidence_requirement_ids[]` does not list | Fail closed at Pack load time — a tree may not silently consult evidence its own activity never declared needing (**closes R2 gap 5**). |
| Following `next_node` edges from any activity's `decision_root_node` revisits a `node_id` already on the path | Fail closed at Pack load time as a cycle — no node may be its own ancestor (**closes R2 gap 5**). |
| A `decision_nodes[]` entry is not reachable from any activity's `decision_root_node` | Fail closed at Pack load time as a dangling node (**closes R2 gap 5**). |
| An activity's `evidence_requirement_ids[]` names an `evidence_requirement_id` that is not the `evidence_requirement_id` of any node reachable from that activity's `decision_root_node` | Fail closed at Pack load time — a declared-but-untested evidence requirement; necessary but not sufficient for `READY`-path closure (invariant 8; see the next two rows for the sufficient condition) (**closes R2 gap 5**). |
| A non-root node reachable from an activity's root has zero or more than one incoming `next_node` edge | Fail closed at Pack load time (invariant 10) — every activity's `decision_nodes` must form a genuine tree, not a DAG with merged branches (**closes R3 gap 3**). |
| A `decision_nodes[]` entry is the `decision_root_node` of, or receives a `next_node` edge from, more than one activity | Fail closed at Pack load time (invariant 11) — no node may be shared between two activities' trees (**closes R3 gap 3**). |
| Some root-to-`READY`-leaf path in an activity's tree omits a declared `evidence_requirement_id` that is neither tested by a node on that path nor named in a `renders_inapplicable` list on that same path | Fail closed at Pack load time (invariant 12) — the actual sufficient condition for `READY`-path closure, distinct from and stronger than invariant 8 (**closes R3 gap 3**). |
| On some root-to-`READY`-leaf path, an `evidence_requirement_id` is both tested by a node on the path and named in a `renders_inapplicable` list on that same path | Fail closed at Pack load time (invariant 12) — tested and inapplicable must be disjoint, not merely jointly cover the declared set (**closes R4 gap 2**). |
| A branch's `renders_inapplicable[]` contains the same `evidence_requirement_id` twice | Fail closed at Pack load time (invariant 13; **closes R4 gap 2**). |
| A branch's `renders_inapplicable[]` names the `evidence_requirement_id` of the node the branch itself belongs to | Fail closed at Pack load time (invariant 14) — a branch cannot render its own just-tested requirement inapplicable (**closes R4 gap 2**). |
| A node testing `evidence_requirement_id` X appears on any path descending from a branch that already rendered X inapplicable, regardless of what verdict that path eventually reaches | Fail closed at Pack load time (invariant 15) — checked over every path prefix, not only `READY`-terminating ones (**closes R4 gap 2**). |
| A branch's `renders_inapplicable[]` names an `evidence_requirement_id` the branch's own activity does not declare | Fail closed at Pack load time, the same way an out-of-scope `next_node` target would be (**closes R3 gap 3**). |
| `overlay.overrides[].field` is not on the closed override enumeration, or no `recheck_conditions[]` row exists in the named `pack_id` for the named `activity_id` | Fail closed as an illegal or inapplicable override, not applied and not ignored (§3.6; **closes R2 gap 6**). |
| **A project's `project.toml` has no `[overlay]` table at all** | **Not an error.** The project simply has no purpose assessment available. `epc-ct run`, `check`, `group`, and every exporter are completely unaffected, because nothing in the current pipeline reads `[overlay]` (**closes gap 5**). |
| **A purpose assessment is explicitly requested for a `pack_id` the project's Overlay does not list under `overlay.packs[]`** | **Fail closed for that request only.** The project's existing contract 1.6 pipeline continues to run normally; only the specific unbound purpose-assessment request is refused (**closes gap 5**). |

No situation above resolves by picking a default, by taking the first match
in an unordered collection, or by reading anything time-dependent — composing
Pack and Overlay is required to be as deterministic as everything else this
repository publishes (`AGENTS.md` rule 1).

### 3.8 Verdict / blocker decision logic: a closed decision tree (closes gap 3, closes R2 gap 1, gap 2, gap 5, closes R3 gap 1, gap 3)

The rejected draft named a `table_id` and deferred the actual shape to
Checkpoint D. That is corrected here: this section fixes the **data
structure** a Pack's verdict logic takes. No evaluator that walks it is
implemented — only the shape a future evaluator would read.

**Shape.** Each activity names one `decision_root_node`. A decision node
names one `evidence_requirement_id` and a set of `branches`, one per outcome
that evidence requirement declares (§3.1, §3.2). A branch is a leaf —
`{ outcome, verdict, failure_kind?, gap_kind?, renders_inapplicable? }`,
where `verdict` is restricted to `READY`, `BLOCKED`, or `UNKNOWN`;
`verdict = "BLOCKED"` requires `failure_kind` and forbids `gap_kind`;
`verdict = "UNKNOWN"` requires `gap_kind` and forbids `failure_kind`;
`verdict = "READY"` forbids both. Both `failure_kind` and `gap_kind` draw
from the same shared `resolution_kind` namespace and must match a
`default_responsibility[].resolution_kind` (§3.1; **closes R2 gap 2**) — or
a leaf is instead an interior branch — `{ outcome, next_node,
renders_inapplicable? }`, pointing at another node that tests a different
evidence requirement. A branch never carries `verdict` alongside
`next_node`. **An outcome is never itself a verdict (§3.2; closes R3 gap
1): only a leaf's `verdict` field is the activity's verdict, and taking a
`next_node` branch defers the verdict to whatever leaf the path eventually
reaches.** `renders_inapplicable` is an optional list of this activity's own
`evidence_requirement_ids` that this branch's outcome structurally rules out
of needing to be tested further along this path (§3.8's invariant 12,
below) — never free text, never a wildcard, and checked against the
activity's declared set the same way `next_node` is checked against
`node_id`s. This is a labelled decision tree: closed, enumerable, no
wildcard, no default branch, no expression language — every branch is one
outcome value mapping to exactly one leaf or one deeper node, checked
exhaustively against the evidence requirement's own declared `outcomes[]` at
Pack-load time (§3.7).

**Structural invariants, checked at Pack load time, before any project ever
uses the file (closes R2 gap 5, closes R3 gap 3, closes R4 gap 2):**

1. Every `activities[].decision_root_node` names an existing `node_id`.
2. Every branch's `next_node` names an existing `node_id`.
3. `node_id` is unique across the Pack.
4. Every node's `evidence_requirement_id` names an existing entry in
   `evidence_requirements[]`.
5. Following `next_node` edges from any activity's root never revisits a
   node already on the path — the graph reachable from each root is acyclic.
6. A node reachable from an activity's root tests only an
   `evidence_requirement_id` that activity's own `evidence_requirement_ids[]`
   lists — a tree may not silently consult evidence its activity never
   declared needing.
7. No `decision_nodes[]` entry is dangling: every node is reachable from
   exactly one activity's root (invariant 11 is what makes "at least one"
   and "exactly one" coincide here).
8. Every `evidence_requirement_id` an activity declares is tested by at
   least one node reachable from that activity's root — a declared-but-
   untested evidence requirement is a Pack authoring error. **This is
   necessary but not sufficient for `READY`-path closure; invariant 12 is
   the sufficient condition.**
9. No branch sets `verdict = "CONDITIONAL"` anywhere in any tree.
10. **Every non-root node reachable from an activity's root has exactly one
    incoming `next_node` edge, sourced from another node reachable from
    (and belonging to) that same activity's root** — this design uses true
    per-activity trees, not general DAGs with branches that merge back
    together.
11. **No `decision_nodes[]` entry is the `decision_root_node` of, or
    receives a `next_node` edge from, more than one activity** — an
    activity's tree is disjoint from every other activity's tree; no node
    is shared across two activities' trees.
12. **For every root-to-`READY`-leaf path in every activity's tree, the set
    of evidence requirements *tested* on that path and the set *rendered
    inapplicable* on that path are disjoint, and their union exactly equals
    the activity's declared `evidence_requirement_ids`** (both accumulated
    from the root down to the leaf, over every branch actually taken along
    the way; **tightened from a one-directional "union covers declared" to
    an exact, disjoint partition — closes R4 gap 2**). Checked exhaustively
    over every such path, of which there are finitely many since the tree is
    finite and acyclic. Every value inside a `renders_inapplicable` list
    must itself be an `evidence_requirement_id` the same activity declares.
13. **A branch's `renders_inapplicable[]` contains no duplicate entries**
    (**closes R4 gap 2**).
14. **A branch's `renders_inapplicable[]` never names the
    `evidence_requirement_id` of the node the branch itself belongs to** —
    a branch exists because its own node's evidence requirement was just
    tested, so marking that same requirement inapplicable in the same
    outcome is a direct contradiction, and is checked locally per branch
    rather than only through the whole-path disjointness in invariant 12
    (**closes R4 gap 2**).
15. **Once a branch renders an `evidence_requirement_id` inapplicable, no
    node testing that same `evidence_requirement_id` may appear on any path
    descending from that branch** — checked over every path *prefix* in the
    tree, regardless of what verdict that path eventually reaches, so a
    `BLOCKED`- or `UNKNOWN`-terminating path cannot silently retest evidence
    an ancestor already ruled out any more than a `READY`-terminating one
    could, which invariant 12 alone — scoped only to `READY`-leaf paths —
    would not catch (**closes R4 gap 2**).

**Invariants 13–15 close three narrower gaps `renders_inapplicable` itself
could otherwise open.** A duplicate entry (13) is inert but marks an
authoring mistake worth catching rather than silently accepting. A branch
marking its own just-tested requirement inapplicable (14) is a direct
contradiction, catchable without walking any path at all — a cheap, local
rejection ahead of the more expensive whole-path checks invariant 12 needs.
And because invariant 12 as stated examines only paths that terminate in
`READY`, a `renders_inapplicable` declaration followed by a later retest of
the same requirement on a path that instead terminates in `BLOCKED` or
`UNKNOWN` would escape it entirely; invariant 15 is scoped to every path
prefix in the tree for exactly that reason, independent of how the path
eventually ends. None of the three is exercised by this Pack's one
`renders_inapplicable` declaration — `no-penetration`'s — which names
`opening-status`, a requirement `penetration-determination-node` itself does
not test, appearing nowhere else in `builders-work-openings`'s tree; the
verification run accompanying this revision constructs each violation
directly, off the worked Pack, to prove all three fail closed.

**Invariants 10 and 11 correct a false claim in the previous revision.**
Acyclicity (invariant 5) alone does not give every node "exactly one parent
chain back to its activity's root" — an acyclic graph can still merge two
branches into one shared downstream node, and a merged node could let two
different paths silently disagree about whether an ancestor's outcome had
already tested some evidence requirement. Invariants 10 and 11 close that
gap directly: every non-root node has exactly one incoming edge, and no node
is shared between two activities, so each activity's `decision_nodes` really
are a tree, and every reachable node has one unique path back to its root.

**Even with a genuine tree, invariant 8 alone was never sufficient to prove
a `READY` path never bypasses applicable evidence — only that a node for
each declared evidence requirement exists *somewhere* in the tree, not that
every path to a `READY` leaf passes through it.** `builders-work-openings`'s
own `no-penetration → READY` branch is the exact counterexample that
motivated this fix: it is a one-node path testing only
`penetration-determination`, and `opening-status`'s node exists elsewhere in
the same tree — reachable only via the `penetration-confirmed` branch —
without ever being reached from this particular `READY` leaf. Invariant 8
alone would accept this silently, because a node for `opening-status` does
exist in the Pack. **Invariant 12 is the actual sufficient condition:** it
walks every root-to-`READY`-leaf path and requires each declared evidence
requirement to be either tested on that specific path, or explicitly ruled
inapplicable by an earlier branch on that same path via
`renders_inapplicable` — a structured, enumerable field, never a free-text
waiver, a wildcard, or a default branch. The `no-penetration` branch below
carries `renders_inapplicable = ["opening-status"]`, which is the one and
only inapplicability declaration this Pack needs; every other
root-to-`READY`-leaf path in this Pack already tests every evidence
requirement its activity declares directly, with nothing to mark
inapplicable.

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

  [[decision_nodes.branches]]
  outcome = "not-yet-evaluated"
  verdict = "UNKNOWN"
  gap_kind = "asset-identity-not-evaluated"

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

  [[decision_nodes.branches]]
  outcome = "not-yet-evaluated"
  verdict = "UNKNOWN"
  gap_kind = "in-model-position-not-evaluated"

[[decision_nodes]]
node_id = "cross-model-alignment-node"
evidence_requirement_id = "cross-model-alignment"

  [[decision_nodes.branches]]
  outcome = "confirmed"
  verdict = "READY"

  [[decision_nodes.branches]]
  outcome = "misaligned"
  verdict = "BLOCKED"
  failure_kind = "cross-model-misalignment"

  [[decision_nodes.branches]]
  outcome = "not-yet-confirmed"
  verdict = "UNKNOWN"
  gap_kind = "cross-model-alignment-not-confirmed"

[[decision_nodes]]
node_id = "penetration-determination-node"
evidence_requirement_id = "penetration-determination"

  [[decision_nodes.branches]]
  outcome = "no-penetration"
  verdict = "READY"
  renders_inapplicable = ["opening-status"]   # the one inapplicability declaration this Pack needs

  [[decision_nodes.branches]]
  outcome = "not-yet-determined"
  verdict = "UNKNOWN"
  gap_kind = "penetration-not-determined"

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

  [[decision_nodes.branches]]
  outcome = "not-yet-determined"
  verdict = "UNKNOWN"
  gap_kind = "opening-status-not-determined"
```

Every leaf in the three trees above reproduces a verdict Checkpoint B already
worked out by hand: `asset-identity → unmet` is case 2's live BLOCKED;
`in-model-position → satisfied, cross-model-alignment → not-yet-confirmed` is
case 3's live UNKNOWN; `penetration-determination → not-yet-determined` is
case 4's live UNKNOWN. The remaining leaves are case 3 and case 4's own
counterfactuals — an alignment confirmed or found misaligned, a penetration
ruled out, an opening found and cross-referenced or found and not — none of
which is live evidence today, and none of which this document asserts as
having happened. Every `BLOCKED` leaf now carries a `failure_kind` and every
`UNKNOWN` leaf a `gap_kind`, each matching one of the ten
`default_responsibility` entries in §3.2 — the rejected round-2 draft left
five `UNKNOWN` leaves with no resolution key at all. The `no-penetration`
branch's `renders_inapplicable = ["opening-status"]` is the only structural
inapplicability declaration any path in these three trees needs (§3.8's
invariant 12) — every other `READY` leaf's path already tests every
evidence requirement its own activity declares, with nothing left to
exempt.

**`CONDITIONAL` is structurally excluded, not merely discouraged.** No branch
in any tree may set `verdict = "CONDITIONAL"` (§3.7), because a tree only ever
consumes evidence-requirement outcomes, and Checkpoint B's invariant 6 is that
`CONDITIONAL` must originate in a named authorisation event — a fact no
evidence outcome can encode. What a future runtime step may do instead is
**promote** a tree's `BLOCKED` or `UNKNOWN` result to `CONDITIONAL` for one
specific assessment, citing the named authoriser, the accepted risk, the
release scope, and the voiding condition. That promotion is additive, never
substitutive: the runtime record must retain the leaf's original verdict
(`BLOCKED` or `UNKNOWN`), its `resolution_kind`, the risk actually accepted,
and the underlying evidence gap or blocker the leaf named — a `CONDITIONAL`
release with no recorded blocker or gap underneath it would be indistinguishable
from a fabricated `READY`, exactly the collapse Checkpoint B's invariant 6
exists to prevent. The promotion is a runtime record layered on top of the
tree's result, never a change to the tree, and never derived from the tree
alone.

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

**The completed outcome → verdict → resolution-kind/role state space
(§3.8), for all three activities, with the live path in each tree marked:**

| Activity | Evidence requirement | Outcome | Verdict | `resolution_kind` | Default role |
|---|---|---|---|---|---|
| Schedules | `asset-identity` | satisfied | READY | — | — |
| Schedules | `asset-identity` | **unmet (live)** | **BLOCKED** | `missing-project-asset-identity` | `model-coordination` |
| Schedules | `asset-identity` | not-yet-evaluated | UNKNOWN | `asset-identity-not-evaluated` | `model-coordination` |
| Ceiling | `in-model-position` | **satisfied (live)** | *(→ cross-model-alignment)* | — | — |
| Ceiling | `in-model-position` | unmet | BLOCKED | `mep-element-not-spatially-assigned` | `mep-lead` |
| Ceiling | `in-model-position` | not-yet-evaluated | UNKNOWN | `in-model-position-not-evaluated` | `mep-lead` |
| Ceiling | `cross-model-alignment` | confirmed | READY | — | — |
| Ceiling | `cross-model-alignment` | misaligned | BLOCKED | `cross-model-misalignment` | `model-coordination` |
| Ceiling | `cross-model-alignment` | **not-yet-confirmed (live)** | **UNKNOWN** | `cross-model-alignment-not-confirmed` | `model-coordination` |
| Openings | `penetration-determination` | no-penetration | READY | — | — |
| Openings | `penetration-determination` | **not-yet-determined (live)** | **UNKNOWN** | `penetration-not-determined` | `model-coordination` |
| Openings | `penetration-determination` | penetration-confirmed | *(→ opening-status)* | — | — |
| Openings | `opening-status` | cross-referenced | READY | — | — |
| Openings | `opening-status` | modelled-not-cross-referenced | BLOCKED | `opening-not-verifiably-linked` | `model-coordination` |
| Openings | `opening-status` | not-modelled | BLOCKED | `missing-corresponding-opening` | `model-coordination` |
| Openings | `opening-status` | not-yet-determined | UNKNOWN | `opening-status-not-determined` | `model-coordination` |

The three live rows compose to the same **BLOCKED / UNKNOWN / UNKNOWN** this
design has stated since the first revision — none of the six fixes in this
round changed a single live verdict, only completed the paths this run's
evidence never travels down. Round 3 changed nothing in this table; it
tightened the evidence-outcome priority order and the responsibility chain
around it (§3.2, §3.5), and the tree's structural guarantees (§3.8), neither
of which moves a live outcome. Round 4 changed nothing here either: it
corrected the *general* claim about aggregating multiple underlying
observations into one outcome (§3.2), and tightened `renders_inapplicable`'s
own structural rules (§3.8, invariants 12–15) — neither is exercised by this
Pack's single live scope per evidence requirement, so no live path, verdict,
or `resolution_kind` moves.

**Every root-to-`READY`-leaf path in all three trees (§3.8, invariants
12–15): tested and inapplicable evidence are disjoint, and their union
exactly equals the declared set:**

| Activity | Path (outcomes taken) | Tested | Inapplicable | Disjoint? | Tested ∪ inapplicable = declared? |
|---|---|---|---|---|---|
| Schedules | `asset-identity = satisfied` | {`asset-identity`} | {} | Yes | Yes — declared = {`asset-identity`} |
| Ceiling | `in-model-position = satisfied` → `cross-model-alignment = confirmed` | {`in-model-position`, `cross-model-alignment`} | {} | Yes | Yes — declared = {`in-model-position`, `cross-model-alignment`} |
| Openings | `penetration-determination = no-penetration` | {`penetration-determination`} | {`opening-status`} (via this branch's `renders_inapplicable`) | Yes — the two sets share no member | Yes — declared = {`penetration-determination`, `opening-status`} = tested ∪ inapplicable |
| Openings | `penetration-determination = penetration-confirmed` → `opening-status = cross-referenced` | {`penetration-determination`, `opening-status`} | {} | Yes | Yes — declared = {`penetration-determination`, `opening-status`} |

Four `READY` paths total across the three trees, and every one accounts for
its activity's full declared evidence set — the openings activity has two
`READY` paths precisely because `penetration-determination`'s
`no-penetration` and `penetration-confirmed` outcomes lead to different
onward requirements, and `renders_inapplicable` is what lets the shorter
path close without a spurious node testing evidence the no-penetration
determination has already made moot.

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
table or an expression language, as the shape of verdict/blocker logic, with
every evidence requirement's outcome vocabulary partitioned into exactly
`READY`/`BLOCKED`/`UNKNOWN`-mapping states, with an outcome itself never
standing in for a verdict, since only a tree's terminal leaf is one; a
verdict-class priority (a known failure always dominates a mere coverage
gap) that is a complete outcome selector only where an evidence requirement
has exactly one named outcome per class — as this Pack's two
validation-backed evidence requirements both do — and that must never be
used to pick among two or more distinct named outcomes an assessed scope's
underlying observations disagree on, whether or not those outcomes share a
class; in that case the assessed scope must instead be partitioned into
outcome-homogeneous subscopes before the tree runs, each producing its own
verdict, with subscope construction, identity, and recording left to
Checkpoint D; `CONDITIONAL` reachable only as a runtime promotion that must
retain the promoted leaf's original verdict, resolution kind, and evidence;
a single `resolution_kind` namespace shared by `BLOCKED`'s `failure_kind`
and `UNKNOWN`'s `gap_kind`, each unique within a Pack and each resolved by
an Overlay `team_mapping` entry that is itself unique per `role`, so every
role a requested activity's reachable non-`READY` leaves can name — not
only `BLOCKED` ones — composes to exactly one project assignee or fails
closed for that request alone, never by falling back to a rule's
`owner_role` or reporting a bare Pack role as though it were an assignment;
fifteen structural invariants a Pack's decision trees must satisfy at load
time, covering root/edge existence, uniqueness, true per-activity tree
shape (not a DAG with merged branches), the sufficient condition for
`READY`-path closure — that every root-to-`READY`-leaf path tests and
structurally rules inapplicable, via a closed, duplicate-free, non-
self-referential `renders_inapplicable` field, a disjoint and exactly
covering partition of every evidence requirement its activity declares —
and that no node may retest evidence any ancestor already ruled
inapplicable, on any path regardless of that path's eventual verdict; three
independent compatibility axes — Pack schema format, Pack content version,
and per-binding ruleset identity — with
Framework machine-contract compatibility named as not yet nameable rather
than fabricated; a project that may use multiple Packs through one Overlay,
with Pack-local `activity_id`/`evidence_requirement_id` disambiguated only by
`pack_id`, and no Overlay-owned project identity duplicating
`[project].project_id`; an override addressed by structured
`{pack_id, activity_id, field}` fields matching the real Pack schema rather
than a dotted string grammar; fail-closed composition with no silent
defaults, including a project with no Overlay leaving the existing pipeline
untouched; and the four changed-input counterfactuals in §4 — all of them,
with no exception — as the acceptance test for Checkpoint D's identity
claims. It commits nothing about how a decision tree is actually evaluated
at runtime, how `AssessmentRun`-shaped state (if any) is named, or when
Checkpoint D begins — those remain open, and deliberately so.
