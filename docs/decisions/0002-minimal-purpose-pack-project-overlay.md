# 0002 — Minimal Purpose Pack + Project Overlay: representation and ownership

- **Status:** Proposed. This is a data-design decision for review, not an
  implementation. No code, rule, checker, test, schema, configuration file,
  CLI, loader, or generated artifact is added or changed by this document.
  This round corrects Checkpoint C's own fixed inputs — how a Purpose Pack
  and a Project Overlay are shaped — and asserts nothing about a runtime
  having been built.
- **Date:** 2026-09-03 (revised; first written 2026-08-28).
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
    node retesting evidence an ancestor had already ruled out. Both were
    closed at `5982653`, each marked **(closes R4 gap N)**.
  - Refines the version at `5982653` (2026-08-27), which **product review
    returned AT RISK** — Checkpoint C not yet released, Checkpoint D not
    authorised — for three further reasons: the worked Pack was named and
    shaped as a single MEP→Architecture point solution
    (`mep-to-architecture-coordination`, one singular `[direction]` table),
    with no stated path to carrying the flagship *Interdisciplinary
    Coordination Readiness* product beyond that one direction without a
    schema redesign; a `BLOCKED`/`UNKNOWN` leaf's `resolution_kind` resolved
    to a role (`default_responsibility[]`) but a reviewer had to separately
    consult `consequence_kinds[]` (addressed by `activity_id`),
    `source_fix_guidance[]` (addressed by `evidence_requirement_id`), and
    `recheck_conditions[]` (addressed by `activity_id` again) to reconstruct
    what a blocker or gap actually meant for the business, who resolved it,
    what they should do, and what would clear it — three different addressing
    schemes for one causal chain; and `overlay.risk_authorisation` was a
    single project-wide `may_authorise` list with no way to say which
    specific `resolution_kind` a role may authorise, which reads as (and
    would compose as) a blanket "may authorise anything," while
    `overlay.overrides[]` gave Overlay a narrow but genuinely open-ended
    patch mechanism against Pack fields with no stated bound on what future
    override kinds could do to Framework or Pack guarantees. All three are
    closed below, each marked **(closes R5 item N)**.
  - Refines the version merged at `f8fd104` (2026-09-03), which **BIM
    domain review returned AT RISK** on the composed Checkpoint C + D design,
    for four reasons, all four confirmed against this repository's own data and
    against Checkpoint B's text before being accepted: the ten
    `resolution_routes[]` assigned `model-coordination` eight times and
    `mep-lead` twice and Architecture never, although
    `missing-corresponding-opening` and `opening-not-verifiably-linked` both
    describe drawing in the architectural model — Checkpoint B's own fix is to
    model it there "so it exists in the discipline that owns the fabric" —
    while `in-model-position-not-evaluated`, whose action is the rule-authoring
    step Checkpoint B assigns to the information manager, was given to the MEP
    lead; `penetration-determination`'s `acceptance_condition` named "the
    architectural element penetrated" in the singular and `opening-status` read
    exactly one outcome per penetrating element, while the same file's
    `missing-corresponding-opening` fix said to model an opening "against each
    storey the penetrating element passes through", so a chimney needing a slab
    opening and a roof opening in different states — and a shared shaft opening
    serving several MEP lines — were both inexpressible; `activities[]` carried
    no declaration of which class of object an activity is about, so an assessed
    scope declared as a whole `model_key` made `pcert-sample`'s two
    `IfcBuildingElementProxy` setout markers subjects of the ceiling activity and
    produced an `UNKNOWN` about a survey marker together with an action to extend
    the rule set until one reported a storey; and the two remaining items
    (`CONDITIONAL` continuation across records, and the shape of a successor
    record that adds only an authorisation) are runtime-record questions closed
    on the Checkpoint D side in
    [`0003-runtime-purpose-assessment-shape.md`](0003-runtime-purpose-assessment-shape.md).
    The three Checkpoint C items are closed below, each marked **(closes E-N)**;
    the role correction is E-1, the cardinality correction E-2, and the declared
    object scope E-3. No `resolution_kind`, branch, outcome vocabulary, leaf
    verdict, or structural invariant 1–15 moved — §6 re-proves both the ten
    routes' one-to-one correspondence with the ten non-`READY` leaves and the
    four `READY` paths' closure under invariant 12, and the live verdicts remain
    **BLOCKED / UNKNOWN / UNKNOWN**.
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
Pack format — that is the standard every rejected or conditional revision has
fallen short of, and the standard §3 is now held to.

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
still true here. Nothing in this round touches these six invariants, or the
`BLOCKED`/`UNKNOWN`/`READY` semantics of any leaf in the worked Pack. The
decision-tree structural invariants built on top of them (§3.8) go from
fifteen to eighteen: the original fifteen are restated unchanged and
unweakened, and the three added govern the new `subject_grain` /`pair_source`
declaration and nothing else.

### Purpose Pack (reusable across projects, and across directions of one flagship purpose)

Owns:

- Purpose identity, Pack file/schema format version, Pack content version,
  maturity, citations (§3.4).
- **Directions**, plural: a Pack may serve more than one directional handoff
  under one flagship purpose, each declared once and referenced by a stable
  `direction_id` (§3.2; **closes R5 item 1**) — never derivable from
  `discipline_scope`, which stays applicability-only (`AGENTS.md`).
- The production activities at stake for this purpose, each naming **which
  direction it serves**, **which class of model object its labour is about**
  (`subject_classes`, §3.2; **closes E-3**), and the **evidence
  requirements** it needs a decision — never a validation requirement
  directly (§3.2, §3.8; **closes gap 1**). The object-class list is
  declarative Pack data about kinds of thing; it is never a filter on which
  elements happen to carry findings, because an element of a declared class
  with no finding at all is exactly the case Checkpoint B case 4 exists to
  keep visible.
- What each evidence requirement means, what would satisfy it, **at what
  grain its readings are keyed** (`subject_grain`, and `pair_source` where
  that grain is a pair, §3.2; **closes E-2**), and — for a reusable,
  non-project-specific question — how it binds to existing validation data by
  `ruleset_id` + `ruleset_version` + `requirement_key` (§3.3). Grain is Pack
  data for the same reason `outcomes[]` is: how many answers a question has
  is a property of the question, not of a run. A project-specific evidence
  requirement (e.g. asset identity) is declared here only as a *question*;
  **which validation data answers it for a given project is Overlay data,
  never Pack data** (§3.5; **closes gap 2**).
- Verdict / blocker decision logic for this purpose, expressed as a closed
  decision tree over evidence-requirement outcomes, entirely **within** the
  Framework's four states — `CONDITIONAL` is categorically excluded as a leaf
  (§3.8; **closes gap 3**). Every `READY` path is checked, node by node, to
  either test or structurally rule out every evidence requirement the
  activity declares — an outcome that merely *exists* in the tree is not
  enough (§3.8, invariant 12; **closes R3 gap 3**).
- **One canonical `resolution_routes[]` table**, keyed by `resolution_kind`
  — the same shared namespace a `BLOCKED` leaf's `failure_kind` or an
  `UNKNOWN` leaf's `gap_kind` names — carrying, in one row per
  `resolution_kind`: the default resolving role, the consequence kinds this
  blocker or gap credibly implies, the next action (a source-model fix for a
  `BLOCKED` leaf; the evidence-gathering step that would end an `UNKNOWN`
  leaf — never described as a model defect), and the recheck condition that
  would clear it (§3.2; **closes R5 item 2**). `UNKNOWN` is not exempt from
  any of this: not knowing something still needs a role tasked with finding
  out, a credible consequence, a concrete next step, and a stated recheck.
  This table replaces four separately-addressed fields the pre-AT-RISK
  revision kept apart (`consequence_kinds[]` by `activity_id`,
  `default_responsibility[]` by `resolution_kind`,
  `source_fix_guidance[]` by `evidence_requirement_id`,
  `recheck_conditions[]` by `activity_id`), so that a reviewer can walk from
  any non-`READY` leaf's `resolution_kind` to consequence, resolving role,
  next action, and recheck through **one lookup, not three**.

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
- **Per-`resolution_kind` risk-authorisation policy** — which roles *may*
  authorise a `CONDITIONAL` promotion for one specific
  `pack_id::resolution_kind`, never a project-wide blanket list (§3.5, §3.7;
  **closes R5 item 3**). The role that *may authorise* and the role that
  *resolves* a leaf (from `resolution_routes[]` through `team_mapping`) are
  two different things, composed from two different tables, and neither
  substitutes for the other.
- Cost parameters, for the *magnitude* half of a business consequence a Pack
  can only name the kind of.
- Project conventions and assumptions that are one project's agreement, not a
  universal truth.
- **No override capability today.** A future, product-approved override
  policy is a legitimate thing for an Overlay to carry — but this round
  defers its design entirely rather than ship a narrow mechanism with no
  stated bound on what it could do to a Framework or Pack guarantee (§3.6).

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
through `resolution_routes[].default_role` and Overlay `team_mapping` (row
8c) — the actual actor (row 8d, alongside 8c, never instead of it), any risk
acceptance actually given — which is the only thing that may **promote** a
tree's `BLOCKED` or `UNKNOWN` result to `CONDITIONAL`, citing a named
authoriser acting under a role the Overlay's `risk_authorisations[]` actually
lists for that exact `resolution_kind`, and which must carry the promoted
leaf's original verdict, its `resolution_kind`, the accepted risk, and the
underlying evidence gap or blocker forward rather than replacing them (§3.8)
— and exit/recheck status. **`CONDITIONAL` never becomes `READY`, and never
eliminates the blocker or gap it was promoted from** — it records that a
named person accepted a named risk against a named scope, not that the
activity's evidence changed.

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
  motivated a Pack at all: a *reusable* purpose question (which directions,
  which activities, which evidence requirements, which decision tree) is a
  different fact from a *project's* policy answer (which team, which cost,
  which bindings) — folding them into one file per project would mean every
  project re-authors the same coordination-readiness question from scratch.

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
| `pack_schema_version` | Pack | slug | Version of the **file format** — which tables/fields this document uses. This ADR defines the first publishable Pack file format, `"1"` (§3.4a). |
| `pack_version` | Pack | opaque slug | Version of this Pack's **content**; pinned by exact match, never a range (§3.4b). |
| `maturity` | Pack | enum (`draft`/`reviewed`/`stable`) | Pack metadata only; never read by the Framework. |
| `citations` | Pack | list of strings | Free text, provenance for the Pack author's claims. |
| `directions[]` | Pack | list of `{ direction_id, from, to }` | **Plural, replacing the singular `[direction]` table** — a Pack may carry more than one directional handoff under one flagship purpose. `direction_id` unique within the Pack; never derived from `discipline_scope` (§3.2; **closes R5 item 1**). |
| `activities[]` | Pack | list of `{ activity_id, label, direction_id, subject_classes[], evidence_requirement_ids[], decision_root_node }` | `activity_id` is **Pack-local**, not global (§5; **closes gap 5**). `direction_id` must resolve to exactly one `directions[].direction_id`, or the Pack fails to load (**closes R5 item 1**); it does not redefine activity identity, which stays `pack_id::activity_id`. |
| `activities[].subject_classes` | Pack | list of IFC entity names | **Which class of model object this activity's labour is about (closes E-3).** A closed, duplicate-free list of `ifc_class` values, matched by exact string equality against `elements.csv`'s published `ifc_class`; no wildcard, no pattern, no `"all"`. It is **declarative Pack data about object kinds, never a filter on which elements happen to carry a finding** — an element of a declared class with zero findings is exactly the case the list exists to keep visible (Checkpoint B case 4's `IfcChimney`). Required for every activity that declares at least one `per-subject`- or `per-subject-pair`-grained evidence requirement; forbidden for an activity all of whose evidence requirements are `whole-scope` (§3.7). |
| `evidence_requirements[]` | Pack | list of `{ evidence_requirement_id, answers, binding_source, subject_grain, acceptance_condition, outcomes[], pair_source?, pack_binding?, insufficient_evidence[]? }` | The evidence layer, distinct from validation requirements (§3.2; **closes gap 1**). `evidence_requirement_id` is Pack-local. |
| `evidence_requirements[].subject_grain` | Pack | enum (`whole-scope` / `per-subject` / `per-subject-pair`) | **How this evidence requirement's readings are keyed onto observation subjects (closes E-2).** `whole-scope`: exactly one reading for the entire assessed scope. `per-subject`: one reading per element subject. `per-subject-pair`: one reading per *(element subject, counterpart element)* pair named by an earlier determination — the grain that lets one penetrating element need several openings, and one opening serve several penetrating elements. Grain was previously assigned at runtime rather than declared here, which left a Pack's cardinality unstated in the Pack; it is Pack data because it is a property of the question, not of a run. |
| `evidence_requirements[].pair_source` | Pack | `{ from_evidence_requirement_id, on_outcome, counterpart_description }` | Present **iff** `subject_grain = "per-subject-pair"`. Names the evidence requirement whose determination supplies the counterpart keys, and the single outcome of it under which those counterparts exist. `counterpart_description` is narrative, like `answers`, and is never machine-interpreted. Checked at Pack load by invariants 16–18 (§3.8). |
| `evidence_requirements[].pack_binding` | Pack | `{ ruleset_id, ruleset_version, requirement_keys[] }` | Present only when `binding_source = "pack"` — a general validation requirement the Pack may reference directly (§3.3). |
| `evidence_requirements[].insufficient_evidence[]` | Pack | list of `{ ruleset_id, ruleset_version, requirement_key, cannot_answer }` | Records a *related but insufficient* validation pass, e.g. R-010 for `cross-model-alignment` (§3.2, §5). |
| `decision_nodes[]` | Pack | list of `{ node_id, evidence_requirement_id, branches[] }` | Closed decision tree per activity (§3.8; **closes gap 3**, **closes R2 gap 5**). Unchanged this round. |
| `decision_nodes[].branches[]` | Pack | list of `{ outcome, verdict?, failure_kind?, gap_kind?, next_node?, renders_inapplicable? }` | Exactly one of `verdict`/`next_node` per branch; `verdict = "BLOCKED"` requires `failure_kind`, `verdict = "UNKNOWN"` requires `gap_kind`, `verdict = "READY"` requires neither; every declared `outcome` covered exactly once, checked at Pack load time (**closes R2 gap 1, gap 2**). `renders_inapplicable[]` names sibling `evidence_requirement_id`s this outcome structurally rules out further down the path — duplicate-free, never the branch's own `evidence_requirement_id`, and never retested by any later node on the same path (§3.8 invariants 12–15; **closes R3 gap 3, closes R4 gap 2**). Unchanged this round. |
| `resolution_routes[]` | Pack | list of `{ resolution_kind, default_role, consequence_kinds[], next_action, recheck_condition }` | **The single canonical chain from a non-`READY` leaf to consequence, role, action, and recheck (closes R5 item 2)** — replaces `consequence_kinds[]`, `default_responsibility[]`, `source_fix_guidance[]`, and `recheck_conditions[]`. `resolution_kind` is unique across the list; every `BLOCKED` leaf's `failure_kind` and every `UNKNOWN` leaf's `gap_kind` must match **exactly one** row, and every row must be used by at least one leaf — an orphaned route fails the Pack closed the same way a dangling reference would. |
| `overlay.packs[]` | Overlay | list of `{ pack_id, pack_version }` | **Plural** — a project may use several Packs (§5; **closes gap 5**). |
| `overlay.evidence_bindings[]` | Overlay | list of `{ pack_id, evidence_requirement_id, ruleset_id, ruleset_version, requirement_keys[] }` | Satisfies `binding_source = "overlay"` evidence requirements — R-005 lives only here (§3.5; **closes gap 2**). |
| `overlay.accepted_evidence_methods[]` | Overlay | list of `{ pack_id, evidence_requirement_id, method_id, description }` | Satisfies `binding_source = "assessment"` evidence requirements. |
| `overlay.team_mapping[]` | Overlay | list of `{ role, team_or_person }` | Project-wide; roles are shared vocabulary across Packs, not Pack-scoped. `role` is unique across the list — every default role a requested activity's reachable non-`READY` leaves might need resolves to exactly one `team_or_person`, or the specific request fails closed (§3.7; **closes R3 gap 2**). |
| `overlay.risk_authorisations[]` | Overlay | list of `{ pack_id, resolution_kind, may_authorise_roles[] }` | **Replaces the single project-wide `overlay.risk_authorisation` (closes R5 item 3)** — who *may* authorise a `CONDITIONAL` promotion, addressed per `pack_id::resolution_kind`, never a blanket list; no wildcard, no `"all"`, no default. |
| `overlay.cost_parameters` | Overlay | project-defined key/value | Magnitude inputs a future runtime step may read; no cost figure is fabricated by this document. |
| `overlay.conventions[]` | Overlay | list of `{ ruleset_id, ruleset_version, requirement_key, note }` | Optional narrative about a project-specific convention (§3.5). |

Nothing in either table carries a model version, a finding key, an actual
verdict, an actual authoriser, an actual cost, or an actual assignee. Those
stay off both files by construction.

**`overlay.overrides[]` does not appear in this table (closes R5 item 3).**
The previous revision's structured-field override mechanism is deleted, not
merely narrowed further; §3.6 records the decision and what a future one
would have to prove before it could exist.

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

**The worked Pack is renamed `interdisciplinary-coordination-readiness`
(closes R5 item 1).** The previous revisions' `mep-to-architecture-coordination`
named a single direction as though it were the whole Pack. It is not: the
flagship product this Pack demonstrates is *Interdisciplinary Coordination
Readiness*, of which MEP → Architecture is the first worked direction, not
the only one the shape can carry. Renaming the Pack, rather than adding a
second Pack per direction, is the point of this round's fix: a Pack that
could only ever hold one direction would force a new Pack — a new identity,
a new file, a new `pack_id::activity_id` namespace — for every future
direction of the *same* purpose (Architecture → MEP, MEP → Structure), even
though those directions would share the same flagship question, plausibly
overlapping activities, and a family resemblance in their evidence
requirements. §3.2's `directions[]` array is the fix: one Pack, several
directions, each declared once.

**`directions[]` is a Pack-top-level array**, each entry `{ direction_id,
from, to }`. `direction_id` is unique within the Pack — checked the same way
`activity_id` and `evidence_requirement_id` are (§3.7). Every
`activities[]` entry names exactly one `direction_id`, checked to resolve to
a declared direction at Pack load time; an activity naming an undeclared
`direction_id`, or naming none, fails the Pack closed (§3.7). This does
**not** redefine activity identity: an activity is still identified as
`pack_id::activity_id` (§5), exactly as before — `direction_id` says *which
direction this activity serves*, a fact about the activity's content, not a
second identity axis layered on top of it.

**This 0.1.0 worked example declares and implements exactly one direction:**

```text
direction_id = "mep-to-architecture"
from = "MEP"
to = "Architecture"
```

**No Architecture→MEP or MEP→Structure entries are added.** Inventing empty
activities or fabricated evidence for directions this repository has not
worked through would be exactly the mistake Checkpoint B's own prose warns
against — "every one of those names is an answer, and the question has not
been asked yet." What §3.2's shape proves is narrower and load-bearing on
its own: that *when* a future direction is worked through with the same
rigour Checkpoint B gave MEP → Architecture, adding it to this Pack is a
matter of appending one `directions[]` entry and pointing new or existing
activities at its `direction_id` — **no new Pack schema, no second Pack
identity, no change to §3's field shapes.** Direction remains Pack data,
never derived from `discipline_scope` — on requirement
`491a4a0b-9b4a-5f77-b90d-31a7dc8beb44` (R-004A), `discipline_scope` reads
`HVAC`, an applicability set with no from and no to, exactly as `AGENTS.md`
and Checkpoint B §1 already establish; `directions[]` is new Pack data
alongside it, never a reinterpretation of it.

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
the three states read off `PASS`/`FAIL`/coverage directly, one *atomic
observation unit* at a time. An atomic observation unit is one element
paired with one bound `requirement_key`; each unit reads to exactly one of
the three names (closes R3 gap 1):**

1. **`unmet`** — the unit's own findings under that `requirement_key`
   include at least one `FAIL`.
2. **`not-yet-evaluated`** — the unit has no finding at all: the rule's
   applicability never reaches this element (an absent finding, exactly
   Checkpoint B case 4's chimney: "the absence of a finding is invisible in
   every count the system reports"), or this assessment has not yet run the
   evaluation for this handover.
3. **`satisfied`** — the unit has at least one finding and none is `FAIL`
   (so, `FAIL` ruled out, every finding for it is `PASS`).

The precedence `FAIL` > not-covered > `PASS` is **only a within-unit reading
rule** — how a single unit's own findings collapse to one of the three
names if, for instance, a checker emits both a `PASS` and a `FAIL` for the
same element under the same key. It is **not** a way to pick an outcome for
a scope that spans several units. The earlier "checked **first, and
unconditionally**" phrasing applied that precedence to the whole assessed
scope, and that was the overreach this round removes.

**Across units, the evidence requirement's outcome is decided by
aggregation, never by priority — the same rule the partitioning rule below
states for every other evidence requirement (closes R3 gap 1):**

- If every unit in the assessed scope reads the **same** named outcome, that
  is the evidence requirement's outcome — plain aggregation, no choice.
- If the units read **two or more different** named outcomes, the assessed
  scope **must be partitioned into outcome-homogeneous subscopes before the
  decision tree runs** — one subscope per distinct named outcome actually
  observed, each carrying the units that read it — and each subscope then
  follows its own path through the tree. A mixed scope is **never** collapsed
  to one outcome by any priority, any text or alphabetic order, or any
  default; `unmet` does not dominate `not-yet-evaluated` just because a
  `FAIL` reads as worse than a coverage gap.

**Worked illustration.** Suppose, purely illustratively, `asset-identity`'s
live scope (Checkpoint B case 2's three HVAC elements, six `FAIL` findings)
also included a fourth element never evaluated under R-005 —
`hvac::EXAMPLE`, not a live element. The three live elements' units read
`unmet`; `hvac::EXAMPLE`'s unit reads `not-yet-evaluated`. Two distinct
named outcomes, so the scope is partitioned into two subscopes: `{the three
live elements}` carries `unmet` and reaches `BLOCKED`; `{hvac::EXAMPLE}`
carries `not-yet-evaluated` and reaches `UNKNOWN`. Two subscopes, two
verdicts, each satisfying Framework invariant 1 (§1) — exactly one verdict
per activity × scope × model-version — for its own scope. The coverage gap
is neither discarded nor folded into the blocker; it is its own subscope
with its own verdict. `asset-identity` and `in-model-position` are **not**
exempt from partitioning — they simply do not exercise it on this run's
live evidence, where every unit in each activity's live assessed scope
reads the same outcome (§6).

**Verdict-class priority is not, by itself, a complete outcome selector for
every evidence requirement — correcting an overclaim in a previous
revision.** `BLOCKED > UNKNOWN > READY` decides which *Framework class* an
assessed scope's result falls into; it says nothing about which *named
outcome* to pick when more than one distinct outcome exists within, or leads
into, that class — and several of this Pack's own evidence requirements have
exactly that shape. `opening-status` alone has **two** distinct `BLOCKED`
outcomes, `modelled-not-cross-referenced` and `not-modelled`, each with its
own `failure_kind`; `penetration-determination`'s `no-penetration` (a
`READY` leaf carrying `renders_inapplicable`) and `penetration-confirmed` (a
`next_node` continuing to `opening-status`) are two distinct outcomes that
are not even in the same class. Class priority cannot choose between two
tied-class `BLOCKED` outcomes, and must never be asked to choose between a
terminal `READY` outcome and a continuation — those lead to structurally
different trees.

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
are **not exempt** — a scope whose atomic units disagree on the named
outcome (some `unmet`, some `not-yet-evaluated`) is partitioned exactly like
any other, as the worked illustration above shows — but no live case in §6
exercises it, because every unit in each activity's live assessed scope
reads the same outcome; the assessment-bound evidence requirements in this
Pack — `cross-model-alignment`, `penetration-determination`, `opening-status`
— each describe a single fact about the assessed scope as a whole in this
worked Pack (whether the two models share a datum; whether one penetrating
element penetrates; whether one opening is cross-referenced), so no live
case in §6 exercises partitioning either; a future Pack whose assessed scope
genuinely spans several such facts is exactly where the two counterexamples
above would first bite.

**What an activity is *about*, declared rather than inferred (closes E-3).**
Every activity that reads any evidence at element grain declares
`subject_classes` — the closed list of `ifc_class` values its labour concerns.
Without it, an assessed scope declared as a whole `model_key` expands to *every*
element of that model version, and this repository's own fixture shows what that
produces: `pcert-sample`'s `hvac` model carries two `IfcBuildingElementProxy`
setout markers, `origin` and `geo-reference`, both with an empty `storey`, both
outside R-004's and R-005's applicability, and `geo-reference` with no finding of
any kind. Expanded blindly they would become subjects of the ceiling activity and
produce an `UNKNOWN` *about a survey marker*, resolved by a route whose next
action is to extend the rule set until a setout marker reports a storey. That
verdict is not wrong about the evidence; it is about the wrong object.

**The fix is declarative object-class data, and it must not become "whatever
has a finding."** Filtering the scope by which elements happen to carry findings
would re-open exactly the trap Checkpoint B case 4 exists to close —
`hvac::3dkFAzOGrAIuOzY_RdrdVv`, the `IfcChimney`, produces **zero** findings and
is the single most important element in that case. It is an `IfcChimney`, so it
is precisely the class every one of this Pack's three activities is about, and it
stays a subject under this rule while the two proxies do not. The list names
object kinds; findings never enter the question. A class a project's model
happens not to contain is not an error — a Pack is reusable, and a project with
no chimneys simply has no chimney subjects.

**An element the list excludes is not silently dropped.** For each requested
activity the runtime record accounts for every declared scope key as either a
subject of that activity or an explicitly listed out-of-class key, with the
`ifc_class` that placed it there (Checkpoint D,
[`0003`](0003-runtime-purpose-assessment-shape.md) §3.1 and §3.3).
A mistyped class name therefore surfaces as elements the activity declined to be
about, not as a scope that quietly shrank.

**Cardinality: an evidence requirement declares the grain its readings are keyed
at (closes E-2).** `subject_grain` is Pack data for the same reason `outcomes[]`
is: how many answers a question has is a property of the question, not of a run.
Three values, and this Pack uses all three:

| `subject_grain` | One reading per | This Pack |
|---|---|---|
| `whole-scope` | the entire assessed scope | `cross-model-alignment` — one fact about the model pair |
| `per-subject` | one element subject | `asset-identity`, `in-model-position`, `penetration-determination` |
| `per-subject-pair` | one *(element subject, counterpart element)* pair | `opening-status` — one reading per *(penetrating element, penetrated architectural element)* |

**Why `opening-status` needed the third grain, and why the pair is keyed the way
it is.** A previous revision keyed `opening-status` by the penetrating element
alone, one reading each, while `penetration-determination`'s
`acceptance_condition` named "**the** architectural element penetrated" in the
singular — and, in the same file, `missing-corresponding-opening`'s fix said to
model an opening "against **each** storey the penetrating element passes
through." Those cannot all be true at once. A chimney that passes through a floor
slab and then the roof needs **two** openings, and the common live state is that
one of them is modelled and cross-referenced while the other is not modelled at
all; a shared shaft opening serving several MEP lines is the same mismatch
inverted. Neither was expressible.

Four keyings were considered:

- **Keep one reading per penetrating element, and let that reading carry a list
  of per-opening outcomes.** Rejected: a reading must reduce to exactly one of
  the evidence requirement's declared `outcomes[]`. A reading holding two
  outcomes at once is precisely the heterogeneity this section forbids
  collapsing, and it would have no carrier to split on — the disagreement would
  live *inside* an atom.
- **Key by the opening.** Rejected outright: the opening does not exist exactly
  when the outcome is `not-modelled`, so the key would be absent precisely when
  it is most needed. That is the phantom key a previous review round removed,
  and nothing here brings it back.
- **Key by *(penetrating element, storey)*.** Rejected: `storey` is a published
  element attribute that is legitimately empty — both setout proxies above have
  none — an opening is hosted in a fabric element rather than in a storey, and
  Checkpoint B's own source fix is to model it "so it exists in the discipline
  that owns the fabric": the fabric element is what the opening hangs on.
- **Key by *(penetrating element, penetrated architectural element)*.
  Chosen.** Both members exist whenever the pair exists — the penetrating
  element is in the assessed scope, and the penetrated architectural element is
  named by the `penetration-confirmed` determination itself — so the assessment
  invents neither. The pair is the unit of labour the activity is actually
  about, one opening to cut, which is why it carries exactly one verdict.
  Several openings for one penetrating element are several pairs; one shared
  opening serving several penetrating elements is several pairs naming the same
  counterpart, each asking whether that opening is inspectably linked to *its
  own* penetrating element — which is what "inspectably linked" means. And the
  opening stays what it already was: an **attribute** of the pair's
  determination, present or a named absence, never a key.

`penetration-determination`'s `acceptance_condition` is pluralised to match: a
`penetration-confirmed` determination names **every** architectural element the
penetrating element passes through, each an `element_key` of the consuming model
version in the model-version context. A determination that claims a penetration
while naming no such element is not admissible evidence and produces no
`penetration-confirmed` reading — it reads `not-yet-determined`, which is the
fail-closed direction.

**This changes no outcome vocabulary, no branch, and no leaf.** The tree's
shape, its fifteen structural invariants, the ten `resolution_routes[]`, and the
one-to-one correspondence between non-`READY` leaves and routes are re-proved
unchanged in §3.8 and §6; `subject_grain` says how many readings a node
consumes, never what a branch does with one.

**Resolving roles, corrected against Checkpoint B's own text (closes E-1).**
Three of the ten `resolution_routes[]` rows named a role that does not do the
work the row's own `next_action` describes:

- `missing-corresponding-opening` and `opening-not-verifiably-linked` both act
  **in the architectural model** — the first models the opening, the second adds
  the cross-reference the opening carries. Checkpoint B case 4 is explicit about
  why the work lands there: model it in the architectural model "so it exists in
  the discipline that owns the fabric." Both move from `model-coordination` to
  **`architecture-lead`**.
- `in-model-position-not-evaluated`'s `next_action` is the only route in the
  Pack that contains a rule-authoring step — extend the rule set's applicability
  so an element the rules never reach can be asked the position question at all.
  Checkpoint B names the actor in the same breath: "the information manager
  extends the rule set so `IfcChimney` is in scope; no model changes." It moves
  from `mep-lead` to **`information-manager`**.

Both role names are existing repository vocabulary, not new words:
`architecture-lead` is the `owner_role` of R-001, R-002 and R-006, and
`information-manager` of R-009. That they already exist is what makes them
available to a route author; it does not license reading either one *off* a
bound rule, which §3.5 forbids and continues to forbid.

**The other seven rows are unchanged, and the reasons are in their own
`next_action` text.** `asset-identity-not-evaluated` stays `model-coordination`
because, unlike `in-model-position-not-evaluated`, it names no rule-authoring
step: the only act it describes is re-running an evaluation whose binding is the
project's own Overlay convention. `penetration-not-determined` and
`opening-status-not-determined` stay `model-coordination` because Checkpoint B
says their evidence needs "the MEP lead and Architecture lead together in a
coordination review, since neither model alone contains the answer" — convening
that review is the coordination function, and naming either discipline alone as
the resolver would misdescribe a joint determination.
`mep-element-not-spatially-assigned` stays `mep-lead`: hosting an element to its
correct level is work in the MEP model.

```toml
# purpose-packs/interdisciplinary-coordination-readiness/pack.toml
# EXAMPLE, not a live artifact — no such file exists yet.

pack_id = "interdisciplinary-coordination-readiness"
pack_schema_version = "1"
pack_version = "0.1.0"
maturity = "draft"
citations = ["docs/product/interdisciplinary-coordination-readiness-mep-to-architecture.md"]

# --- Directions: this flagship purpose can carry more than one directional
#     handoff. This worked example declares and implements exactly one.
#     Adding Architecture-to-MEP or MEP-to-Structure later is one new
#     directions[] entry plus new activities pointing at it -- no new Pack,
#     no schema change. (closes R5 item 1) ---

[[directions]]
direction_id = "mep-to-architecture"
from = "MEP"
to = "Architecture"

# --- Evidence requirements: what an activity needs to know, not who answers it. (closes gap 1) ---

[[evidence_requirements]]
evidence_requirement_id = "asset-identity"
answers = "each equipment element in the assessed scope carries the project's asset identity"
binding_source = "overlay"   # project-specific: the Pack asks the question, the Overlay supplies the answer (closes gap 2)
subject_grain = "per-subject"
acceptance_condition = "every element in the assessed scope that a bound requirement_key applies to evaluates PASS, and every such element is covered by an evaluation at all -- an element with no finding under the binding is not covered, and not-covered is never read as satisfied"
outcomes = ["satisfied", "unmet", "not-yet-evaluated"]

[[evidence_requirements]]
evidence_requirement_id = "in-model-position"
answers = "each MEP element in the assessed scope is assigned to a storey Architecture also models"
binding_source = "pack"      # a general coordination requirement, not a project convention
subject_grain = "per-subject"
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
subject_grain = "whole-scope"   # one fact about the model pair, not one per element
acceptance_condition = "a recorded alignment confirmation exists for the named model versions, produced by a method the project's Overlay accepts, and it reports the models aligned"
outcomes = ["confirmed", "misaligned", "not-yet-confirmed"]

  [[evidence_requirements.insufficient_evidence]]
  ruleset_id = "epc-delivery"
  ruleset_version = "2.2"
  requirement_key = "acb11f11-bf18-5516-a6f2-21e451a6e410"  # R-010, EXAMPLE citation
  cannot_answer = "R-010 witnesses a shared marker (name + cross-model GlobalId) only; a PASS is not alignment evidence and must never be read as satisfying this evidence requirement, in any of its three outcomes."

[[evidence_requirements]]
evidence_requirement_id = "penetration-determination"
answers = "whether an MEP element penetrates architectural fabric, and if so which architectural elements"
binding_source = "assessment"
subject_grain = "per-subject"
acceptance_condition = "a recorded coordination-review determination exists for the named model versions, either naming no penetration or naming every architectural element the penetrating element passes through, each as an element_key of the consuming model version; a determination claiming a penetration while naming no such element is not admissible and produces no penetration-confirmed reading (closes E-2)"
outcomes = ["no-penetration", "penetration-confirmed", "not-yet-determined"]

[[evidence_requirements]]
evidence_requirement_id = "opening-status"
answers = "for each architectural element an MEP element penetrates, whether the corresponding opening exists and is inspectably linked to that penetrating element"
binding_source = "assessment"
subject_grain = "per-subject-pair"   # one reading per (penetrating element, penetrated architectural element) (closes E-2)
acceptance_condition = "for the pair, the opening is modelled in the penetrated architectural element and a recorded cross-reference to this penetrating element exists"
outcomes = ["cross-referenced", "modelled-not-cross-referenced", "not-modelled", "not-yet-determined"]

  [evidence_requirements.pair_source]
  from_evidence_requirement_id = "penetration-determination"
  on_outcome = "penetration-confirmed"
  counterpart_description = "Each architectural element the determination named as penetrated. Both members of the pair exist whenever the pair does; the opening itself is an attribute of the pair reading -- present, or a named absence -- and is never a key."

# --- Activities: which direction each one serves, which class of model object
#     it is about, which evidence requirements it needs, and where its decision
#     tree starts. direction_id must resolve to a declared direction; it does
#     not change activity identity, which stays pack_id::activity_id.
#     (closes R5 item 1)
#
#     subject_classes is the declared object scope (closes E-3): the ifc_class
#     values this activity's labour concerns, matched by exact string equality
#     against elements.csv. It is never a finding filter. That all three
#     activities of this Pack happen to declare the same three classes is a fact
#     about this Pack -- MEP work products handed to Architecture -- not about
#     the schema: an activity about architectural fabric would declare fabric
#     classes, which is why the list lives on the activity. The two
#     IfcBuildingElementProxy setout markers in pcert-sample's hvac model
#     (origin, geo-reference) are outside all three lists and are therefore
#     subjects of none of these activities; the IfcChimney with zero findings is
#     inside all three and stays a subject of each. ---

[[activities]]
activity_id = "schedules-and-room-data-sheets"
label = "Room data sheets and equipment schedules"
direction_id = "mep-to-architecture"
subject_classes = ["IfcDuctSegment", "IfcAirTerminal", "IfcChimney"]
evidence_requirement_ids = ["asset-identity"]
decision_root_node = "asset-identity-node"

[[activities]]
activity_id = "ceiling-and-bulkhead-geometry"
label = "Reflected ceiling and bulkhead layout"
direction_id = "mep-to-architecture"
subject_classes = ["IfcDuctSegment", "IfcAirTerminal", "IfcChimney"]
evidence_requirement_ids = ["in-model-position", "cross-model-alignment"]
decision_root_node = "in-model-position-node"

[[activities]]
activity_id = "builders-work-openings"
label = "Builder's-work openings"
direction_id = "mep-to-architecture"
subject_classes = ["IfcDuctSegment", "IfcAirTerminal", "IfcChimney"]
evidence_requirement_ids = ["penetration-determination", "opening-status"]
decision_root_node = "penetration-determination-node"

# --- Decision trees are §3.8. Resolution routes -- the single canonical
#     chain from a non-READY leaf's resolution_kind to consequence, default
#     role, next action, and recheck condition -- follow. (closes R5 item 2)
#
#     Ten rows, not a skeleton: every resolution_kind this Pack's three
#     trees can produce has a real, filled-in row. A BLOCKED row's
#     next_action is a source-model fix; an UNKNOWN row's next_action is the
#     evidence-gathering step that would end it -- never described as a
#     known model defect, because it is not one. ---

[[resolution_routes]]
resolution_kind = "missing-project-asset-identity"   # BLOCKED, asset-identity
default_role = "model-coordination"
consequence_kinds = ["work-cannot-start", "re-identification-and-reissue-risk"]
next_action = "Source-model fix: populate or correct the project-required asset-identity values on the affected source elements according to the project's active Overlay binding and convention (§3.5), then re-export the model so the bound requirement_keys can be evaluated. Which properties, authoring-tool fields, and export mapping this requires is project- and convention-specific; the Pack does not name them, because that binding belongs to the Overlay."
recheck_condition = "Every requirement_key bound to asset-identity evaluates PASS for every element in the assessed scope, with no element left uncovered, on the reissued model."

[[resolution_routes]]
resolution_kind = "asset-identity-not-evaluated"      # UNKNOWN, asset-identity
default_role = "model-coordination"
consequence_kinds = ["work-suspended"]
next_action = "Not a model defect: run (or re-run) the asset-identity evaluation over the full assessed scope so every element it covers actually produces a PASS or FAIL result. The gap is missing coverage of the evaluation itself, not a known failure in the model."
recheck_condition = "Every element in the assessed scope is covered by an evaluation under the bound requirement_key(s) -- no element is left with no finding at all."

[[resolution_routes]]
resolution_kind = "mep-element-not-spatially-assigned"   # BLOCKED, in-model-position
default_role = "mep-lead"
consequence_kinds = ["work-suspended"]
next_action = "Source-model fix: host the element to its correct level and space before export, avoiding unhosted or unlevelled MEP components, so the export reports an IFCRELCONTAINEDINSPATIALSTRUCTURE relationship for it."
recheck_condition = "The R-004-bound requirement_key(s) evaluate PASS for the element on the reissued model."

[[resolution_routes]]
resolution_kind = "in-model-position-not-evaluated"      # UNKNOWN, in-model-position
default_role = "information-manager"   # the only route carrying a rule-authoring step (closes E-1)
consequence_kinds = ["work-suspended"]
next_action = "Not a model defect: run the in-model-position evaluation over the full assessed scope; where a specific element still produces no finding at all, extend the rule set's applicability to reach it -- a rule-authoring action, not a model edit -- so the position question can be asked of it."
recheck_condition = "Every element in the assessed scope is covered by a finding under the bound requirement_key(s)."

[[resolution_routes]]
resolution_kind = "cross-model-misalignment"          # BLOCKED, cross-model-alignment
default_role = "model-coordination"
consequence_kinds = ["work-suspended"]
next_action = "Source-model fix: re-acquire the project's shared coordination datum in the authoring tool, re-export placement referencing that shared origin rather than moving geometry directly, and re-perform the accepted alignment-confirmation method. Which authoring-tool command produces the re-acquired datum is project- and tool-specific; the Pack does not name it, the same way the asset-identity route above does not name the properties its own fix touches."
recheck_condition = "The alignment-confirmation method is re-run against the reissued model versions and reports the models aligned (outcome = confirmed)."

[[resolution_routes]]
resolution_kind = "cross-model-alignment-not-confirmed"   # UNKNOWN, cross-model-alignment
default_role = "model-coordination"
consequence_kinds = ["work-suspended", "rework-risk"]
next_action = "Not a model defect: perform the alignment-confirmation method this project's Overlay accepts (e.g. overlaying both models' exported placements in a common viewer) against the named model versions. The gap is that no confirmation has been produced yet, not a known misalignment."
recheck_condition = "The alignment-confirmation method is performed and reports the models aligned, against the specific model versions named."

[[resolution_routes]]
resolution_kind = "penetration-not-determined"        # UNKNOWN, penetration-determination
default_role = "model-coordination"
consequence_kinds = ["work-suspended"]
next_action = "Not a model defect: hold the coordination-review determination this project's Overlay accepts, naming either no penetration or the specific architectural element penetrated. The gap is that the determination has not been made yet, not a known defect."
recheck_condition = "A recorded coordination-review determination exists for the named model versions, naming either no penetration or the architectural element penetrated."

[[resolution_routes]]
resolution_kind = "opening-not-verifiably-linked"     # BLOCKED, opening-status
default_role = "architecture-lead"   # the cross-reference is carried by the opening, in the architectural model (closes E-1)
consequence_kinds = ["work-suspended", "rework-risk"]
next_action = "Source-model fix: add or correct the cross-reference from the modelled architectural opening back to the penetrating MEP element it was cut for, so the link the accepted method checks for actually exists and can be inspected. One such link per (penetrating element, penetrated architectural element) pair: a shared opening serving several penetrating elements needs a cross-reference to each of them."
recheck_condition = "The opening-cross-reference-check method is re-run and reports the opening cross-referenced to the penetrating element, for the pair."

[[resolution_routes]]
resolution_kind = "missing-corresponding-opening"     # BLOCKED, opening-status
default_role = "architecture-lead"   # so it exists in the discipline that owns the fabric (closes E-1)
consequence_kinds = ["work-suspended"]
next_action = "Source-model fix: model the opening in the architectural model, as a hosted opening or shaft in the architectural element this penetration passes through, rather than as a void carried in the MEP model. An element that passes through several architectural elements needs one such opening in each of them -- one per pair."
recheck_condition = "The opening-status evaluation is re-run and reports the opening modelled and cross-referenced (outcome = cross-referenced) for this pair, for the named model versions."

[[resolution_routes]]
resolution_kind = "opening-status-not-determined"     # UNKNOWN, opening-status
default_role = "model-coordination"
consequence_kinds = ["work-suspended"]
next_action = "Not a model defect: complete the opening-status review this project's Overlay accepts -- whether a corresponding opening is modelled and, if so, whether it is inspectably cross-referenced. The gap is that this review has not been completed yet, not a known missing opening."
recheck_condition = "The opening-cross-reference-check method is performed and reports a definite result (cross-referenced, modelled-not-cross-referenced, or not-modelled) for the named model versions."
```

**Ten rows, not four fields:** every `BLOCKED` leaf's `failure_kind` (five of
them) and every `UNKNOWN` leaf's `gap_kind` (five of them) across all three
activities' trees resolves to **exactly one `resolution_routes[]` row**,
and every row is used by at least one leaf — an orphaned route, a duplicate
`resolution_kind`, or a leaf whose `resolution_kind` matches no row all fail
the Pack closed (§3.7). **Because `resolution_kind` is the join key and it
is unique, two leaves can only ever share a `resolution_kind` by sharing the
identical route behind it** — there is no way, structurally, for the same
`resolution_kind` to carry two different roles, consequence sets, actions,
or recheck conditions; reusing a `resolution_kind` across leaves and
diverging on any of those four fields is not a case this design can
express, so leaves that should differ must simply be given different
`resolution_kind`s, exactly as the ten above already are.

**`opening-not-verifiably-linked` and `missing-corresponding-opening` are
the two blockers the product review named specifically, and their routes
are deliberately distinct end to end:** the first's next action *adds a
cross-reference* to an opening that already exists and recheck *re-runs the
link check*; the second's next action *models the opening itself* in
Architecture and recheck *confirms the opening exists and is linked*. Two
different blockers, two different fixes, two different rechecks — nothing
about either route could be satisfied by doing the other.

**No `UNKNOWN` route claims a known model defect.** Every `UNKNOWN`
`next_action` above opens with "not a model defect" and names an
evidence-gathering step — running an evaluation, performing an accepted
method, holding a coordination-review determination — because that is what
Checkpoint B case 3 and case 4 actually established: the question was never
asked, not asked and answered badly.

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
loader must understand to parse it at all. It changes only when the Pack
*file format* changes, never when one Pack's content changes. **This ADR
defines the first publishable Pack file format, `"1"`** — no Pack, Pack
loader, or Pack schema has been published before this document, so there is
no prior format for this one to move from. A rejected or not-yet-released
ADR draft does not consume a schema version, and creates no migration or
compatibility obligation for the format this document actually defines: the
directions/`resolution_routes` shape below is simply what schema `"1"` is,
not a revision of anything a loader would already exist for. A future
loader that does not implement a given, *published* `pack_schema_version`
refuses the file (§3.7).

**b) Pack content version — `pack_version`.** An author-declared **opaque
slug**, not strict semver, validated the same way `ruleset_version` already
is — by `_require_slug` in `identity.py:87–90` (accepts `[A-Za-z0-9][A-Za-z0-9._-]*`,
never parsed into numeric segments or compared with `<`/`>=`). Bumped by the
Pack author whenever activities, evidence requirements, decision trees, or
resolution routes change. An Overlay pins one exact `pack_version` string per
`pack_id` (§3.5), and composition fails closed on any mismatch — never a
range match. Slug-and-exact-match was chosen over strict semver because
nothing else in this codebase parses or compares version ranges, and every
consumer of `pack_version` in this design (the Overlay's own pin) checks it
by equality; introducing range-comparison machinery for a value nothing ever
compares as a range would be new complexity with no consumer, the same
judgement `AGENTS.md` already applies to `ruleset_version`.

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
technical director's approved route places that surface at the
**deterministic machine contract and CLI** route item — several items after
Checkpoint C, and after Checkpoint D and the runtime-evidence work it
depends on. This document therefore names **no** Framework-compatibility
field at all — not a version string, not a range, not a placeholder. When
that route item defines what a Framework machine contract's own identity
looks like, a Pack-level compatibility field against *that* becomes
designable; inventing its shape now, or approximating it with contract
1.6's own version number, would be guessing at a later route item's output
before it runs —
exactly the anti-pattern `Agent-product-manager.md` names for
`AssessmentRun`-shaped objects, applied here to a compatibility field instead
of a runtime type.

### 3.5 Overlay: pointing at Pack(s), project, R-005 as the worked binding, and per-`resolution_kind` risk authorisation (closes gap 2, closes R5 item 3)

```toml
# projects/pcert-sample/project.toml — EXCERPT, illustrative addition only.
# EXAMPLE, not a live edit — this document changes no tracked file.

[overlay]
# No project_id field: this table is nested inside pcert-sample's own
# project.toml, which already declares [project].project_id = "pcert-sample"
# one table up. An Overlay's project identity is inherited by nesting, never
# restated (closes R2 gap 4).

[[overlay.packs]]
pack_id = "interdisciplinary-coordination-readiness"
pack_version = "0.1.0"

# --- Satisfies the Pack's "asset-identity" evidence requirement. This binding,
#     and only this binding, is where R-005 enters the design — never in the
#     Pack file. Exactly the four requirement_keys R-005A/B key, not the six
#     findings a run against them happens to produce today. ---

[[overlay.evidence_bindings]]
pack_id = "interdisciplinary-coordination-readiness"
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
pack_id = "interdisciplinary-coordination-readiness"
evidence_requirement_id = "cross-model-alignment"
method_id = "overlay-comparison"
description = "Placements from both models overlaid in a common viewer and visually confirmed by model-coordination; reports confirmed, misaligned, or is simply not yet performed."

[[overlay.accepted_evidence_methods]]
pack_id = "interdisciplinary-coordination-readiness"
evidence_requirement_id = "penetration-determination"
method_id = "coordination-review-determination"
description = "A recorded decision from a joint MEP/Architecture coordination review, naming either no penetration or the specific architectural element penetrated."

[[overlay.accepted_evidence_methods]]
pack_id = "interdisciplinary-coordination-readiness"
evidence_requirement_id = "opening-status"
method_id = "opening-cross-reference-check"
description = "A recorded check that a modelled architectural opening carries a reference back to the penetrating MEP element it was cut for."

[[overlay.team_mapping]]
role = "model-coordination"
team_or_person = "coordination-team"  # EXAMPLE — no real assignment exists

[[overlay.team_mapping]]
role = "mep-lead"
team_or_person = "mep-design-team"  # EXAMPLE — no real assignment exists

# --- Two further rows, because the corrected routes now reach two further
#     roles (closes E-1). A team_mapping row staffs a *resolving* role only; it
#     never staffs an authoriser, and information-manager appearing both here
#     and in risk_authorisations below stays two independently declared facts,
#     not one inferred from the other. ---

[[overlay.team_mapping]]
role = "architecture-lead"
team_or_person = "architecture-design-team"  # EXAMPLE — no real assignment exists

[[overlay.team_mapping]]
role = "information-manager"
team_or_person = "information-management-team"  # EXAMPLE — no real assignment exists

# --- Risk authorisation: which roles MAY authorise a CONDITIONAL promotion
#     for one specific pack_id::resolution_kind. Never a project-wide list.
#     "information-manager" echoes Checkpoint B's own vocabulary -- the
#     information manager chairing the coordination review is who
#     approves, refuses, or qualifies a release in that scenario.
#     (closes R5 item 3) ---

[[overlay.risk_authorisations]]
pack_id = "interdisciplinary-coordination-readiness"
resolution_kind = "cross-model-alignment-not-confirmed"
may_authorise_roles = ["information-manager"]  # EXAMPLE -- illustrative role, no real acceptance exists

[[overlay.risk_authorisations]]
pack_id = "interdisciplinary-coordination-readiness"
resolution_kind = "missing-project-asset-identity"
may_authorise_roles = ["information-manager"]  # EXAMPLE -- illustrative role, no real acceptance exists

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
before, for both verdict shapes: `resolution_routes[]` names an abstract
`default_role` for a `resolution_kind` — a `BLOCKED` leaf's `failure_kind` or
an `UNKNOWN` leaf's `gap_kind` alike; the Overlay's `team_mapping` names this
project's actual team for that role; a future runtime step composes the two
into an actual assignment, which is a runtime fact (row 8c) recorded nowhere
in either file. The four roles the Pack's ten `resolution_routes[]` entries
actually use are exactly the four `team_mapping` entries above:

| Pack `default_role` | Used by `resolution_kind`(s) | Overlay `team_or_person` (illustrative) |
|---|---|---|
| `model-coordination` | `missing-project-asset-identity`, `asset-identity-not-evaluated`, `cross-model-misalignment`, `cross-model-alignment-not-confirmed`, `penetration-not-determined`, `opening-status-not-determined` | `coordination-team` |
| `mep-lead` | `mep-element-not-spatially-assigned` | `mep-design-team` |
| `architecture-lead` | `opening-not-verifiably-linked`, `missing-corresponding-opening` | `architecture-design-team` |
| `information-manager` | `in-model-position-not-evaluated` | `information-management-team` |

Six, one, two and one: ten `resolution_kind`s, each mapped exactly once, and
every role a reachable non-`READY` leaf can name resolving to exactly one
`team_or_person` — which is what §3.7 requires before an activity may be
assessed at all. **The correction moved roles between rows; it added no row,
removed none, and changed no `resolution_kind`, consequence, action, or
recheck condition.**

This is **project policy for how a role would be staffed, stated in
advance** — it is not this run's assignment, not an actor, and not a claim
that anyone has been tasked with anything. The runtime composition it
enables (rows 8a–8c) still does not exist until Checkpoint D produces one.

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

**Two things this composition must never do, stated affirmatively:**

- **Never silently fall back to the underlying validation rule's
  `owner_role`.** `AGENTS.md` and Checkpoint B §5 row 8a both already settle
  this: `owner_role` is the role a *rule author* expects to answer for the
  rule — an input a Pack's `resolution_routes[]` may have been informed by,
  never a substitute for it, and never a substitute for the Overlay's own
  `team_mapping` when that mapping happens to be missing. A missing
  `team_mapping` entry is a fail-closed condition (§3.7), not a cue to read
  `Requirement.owner_role` off the bound rule instead.
- **Never let the abstract Pack `default_role` string stand in for a project
  assignment.** `default_role = "mep-lead"` names a category of
  responsibility, not a person or a team; only `overlay.team_mapping`'s
  `team_or_person` value turns it into something a runtime assessment could
  actually assign work to. Reporting `"mep-lead"` itself as though it were
  an assignee would be reporting a Pack default as if it were a project
  decision.

**Risk authorisation is a third, separate role from either of these two
(closes R5 item 3).** `resolution_routes[].default_role` and
`overlay.team_mapping` compose to say *who resolves* a leaf.
`overlay.risk_authorisations[]` says *who may accept the risk* of releasing
work despite that leaf — a different question, answered by a different
table, and never derived from the first. `may_authorise_roles` is a
project-declared list of role names, addressed by an explicit
`pack_id::resolution_kind` pair; there is no wildcard value, no `"all"`
sentinel, and no rule anywhere in this design that lets the resolving role
double as the authorising role by default. A project could name the same
role in both places — `model-coordination` could conceivably resolve *and*
be trusted to authorise the same `resolution_kind` — but that would be two
separate, independently-declared facts, not one inferred from the other.
`overlay.risk_authorisations[]` above deliberately covers only two of the
ten `resolution_kind`s: **a resolution_kind with no matching row simply has
no authorisation path — a `BLOCKED` or `UNKNOWN` leaf for it can never be
promoted to `CONDITIONAL` in this project, full stop, not "authorised by a
default role."**

### 3.6 Project override policy: deferred, not designed (closes R5 item 3)

A previous revision gave the Overlay a structured, closed-enum override
mechanism (`{pack_id, activity_id, field, permitted_change, note}`,
narrowing a Pack's `recheck_conditions[]`). Product review is right that
this was the wrong shape to ship even in its narrowed form: the mechanism's
existence, not merely its current single field, is what needed a stated
bound before this design should carry it at all. **This document deletes
`overlay.overrides[]` entirely rather than narrowing it further.**

**What stays true, and is a fact about ownership rather than about any
mechanism:** an Overlay is the right place, in principle, for a project's
own approved policy overrides against Pack defaults to live, the same way
`overlay.evidence_bindings[]` and `overlay.accepted_evidence_methods[]`
already let a project supply data a Pack cannot know in advance. That
ownership claim is not withdrawn. What is withdrawn is any *current* schema
for exercising it: **this round ships no override field, no override table,
and no override TOML example.** Checkpoint D must not implement an override
capability, and must not assume one exists to design around.

**Before any future override design may be proposed, it must be possible to
machine-verify that the specific override it permits satisfies all four of
the following, for every case the override could apply to — not merely
argued to satisfy them in prose:**

1. **It does not weaken a Framework invariant** (§1's six, or the eighteen
   decision-tree structural invariants built on them, §3.8) — the four
   verdict words, their mutual exclusivity, and the tree's own soundness
   stay exactly as strict as an Overlay-free Pack.
2. **It does not weaken a Pack's `acceptance_condition`** for any evidence
   requirement — an override may narrow what a project chooses to assess,
   never loosen what "satisfied" means for what it does assess.
3. **It does not shrink the scope a recheck must still cover** — narrowing
   *which* activity or model version is in scope for a given assessment is
   one thing; narrowing *what evidence a recheck within that scope must
   still show* is the thing no override may do.
4. **It does not skip an unresolved blocker or evidence gap, and does not
   turn anything not actually rechecked into `READY`** — the same
   invariant that already governs `CONDITIONAL` (§1, §3.8) governs any
   future override: recorded acceptance of risk, never a substitute for
   evidence.

This is a monotonicity requirement, not a checklist to satisfy by argument:
a future design earns the right to exist only once these four properties are
themselves expressed in a form a loader could check, the same discipline
this document already holds the decision tree to (§3.7, §3.8). **No
free-text patch, JSON-path expression, or general expression language is an
acceptable substitute for that verification** — replacing one narrow,
checkable mechanism with a more expressive but unverifiable one would be a
regression, not a fix, and is explicitly not the direction this deferral
points toward.

**What an Overlay can never override, regardless of any future mechanism,
stated affirmatively:** the Framework's four verdict words and their six
invariants (§1); a Pack's `directions[]`; a Pack's decision tree (§3.8),
including which evidence requirement any node tests; and anything in the
runtime-assessment column of Checkpoint B §5's table. An Overlay may *add*
an evidence binding, an accepted method, or a risk-authorisation entry where
a Pack requires or a project chooses to supply one; it may never *redirect*
a `binding_source = "pack"` evidence requirement's own `pack_binding` to
different `requirement_key`s, today or under any future override.

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
| Two `directions[]` entries in one Pack share the same `direction_id` | Fail closed as a duplicate, at Pack load time (**closes R5 item 1**). |
| An `activities[].direction_id` does not name an existing `directions[].direction_id` | Fail closed at Pack load time — every activity must resolve to exactly one declared direction (**closes R5 item 1**). |
| A decision node's `branches[]` does not cover every `outcome` its `evidence_requirement_id` declares, covers one twice, or a branch carries both `verdict` and `next_node` | Fail closed **at Pack load time**, before any project ever uses it — stronger than a runtime check (**closes gap 3**). |
| A `BLOCKED` branch has no `failure_kind`, an `UNKNOWN` branch has no `gap_kind`, or a `READY` branch carries either | Fail closed at Pack load time (**closes R2 gap 2**). |
| A branch's `failure_kind` or `gap_kind` does not match **exactly one** `resolution_routes[].resolution_kind` | Fail closed at Pack load time — every `BLOCKED`/`UNKNOWN` leaf must resolve to a full route, not just exist (**closes R2 gap 2, closes R5 item 2**). |
| `resolution_routes[]` contains two entries with the same `resolution_kind` | Fail closed at Pack load time as a duplicate — the "exactly one" match above depends on this (**closes R3 gap 2, closes R5 item 2**). |
| A `resolution_routes[]` entry is missing `resolution_kind`, `default_role`, `consequence_kinds`, `next_action`, or `recheck_condition` | Fail closed at Pack load time as an incomplete route (**closes R5 item 2**). |
| A `resolution_routes[]` entry's `resolution_kind` is not the `failure_kind` or `gap_kind` of any branch in any of the Pack's decision trees | Fail closed at Pack load time as an orphaned route (**closes R5 item 2**). |
| `overlay.team_mapping[]` contains two entries with the same `role` | Fail closed at composition time as a duplicate (**closes R3 gap 2**). |
| **A purpose assessment is requested for an activity whose reachable non-`READY` leaves name a default role with no matching `overlay.team_mapping[]` entry** | **Fail closed for that request only.** The project's existing contract 1.6 pipeline, and any other activity or Pack this Overlay does bind completely, are unaffected. Never resolved by reading the bound rule's `owner_role` instead, and never reported as though the bare Pack `default_role` string were itself an assignment (§3.5; **closes R3 gap 2**). |
| Two `overlay.risk_authorisations[]` entries share the same `{pack_id, resolution_kind}` pair | Fail closed at composition time as a duplicate (**closes R5 item 3**). |
| An `overlay.risk_authorisations[].resolution_kind` does not match a `resolution_routes[].resolution_kind` in the named `pack_id` | Fail closed at composition time as a dangling reference (**closes R5 item 3**). |
| An `overlay.risk_authorisations[].may_authorise_roles` is empty, or contains a wildcard, `"all"`, or any similarly unbounded value | Fail closed at composition time — there is no such thing as blanket authorisation in this design (**closes R5 item 3**). |
| **A `CONDITIONAL` promotion is attempted for a `resolution_kind` with no matching `overlay.risk_authorisations[]` entry** | **Fail closed for that promotion only; the leaf's verdict stays `BLOCKED`/`UNKNOWN`.** `CONDITIONAL` is simply unavailable for that `resolution_kind` in this project — never resolved by falling back to a default role, to `resolution_routes[].default_role`, or to any other role not explicitly listed as an authoriser for that exact `resolution_kind` (§3.5; **closes R5 item 3**). |
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
| An `activities[]` entry declares at least one `per-subject`- or `per-subject-pair`-grained evidence requirement and has no `subject_classes`, or declares only `whole-scope` evidence requirements and has one | Fail closed at Pack load time — an activity that reads element-grained evidence must say which class of object it is about, and one that reads none has no element subjects to declare classes for (**closes E-3**). |
| An `activities[].subject_classes` is empty, contains a duplicate, or contains a wildcard, a pattern, or `"all"` | Fail closed at Pack load time — the list is closed and enumerable, exactly like `renders_inapplicable[]` and every `outcomes[]` list (**closes E-3**). |
| An `evidence_requirements[]` entry has no `subject_grain`, or a `subject_grain` outside `whole-scope` / `per-subject` / `per-subject-pair` | Fail closed at Pack load time (**closes E-2**). |
| An evidence requirement has `subject_grain = "per-subject-pair"` and no `pair_source`, or has a `pair_source` without that grain | Fail closed at Pack load time (invariant 16; **closes E-2**). |
| A `pair_source.from_evidence_requirement_id` is not declared by every activity that declares the pair-grained requirement, or its `on_outcome` is not one of that requirement's declared `outcomes[]` | Fail closed at Pack load time (invariant 16; **closes E-2**). |
| A node testing a `per-subject-pair` evidence requirement is reachable by any path whose prefix does not include the pair source's node taking exactly `on_outcome` | Fail closed at Pack load time (invariant 17) — a pair-keyed reading may never be asked where no pair has been named (**closes E-2**). |
| The pair source's `on_outcome` branch is a leaf rather than a `next_node` branch | Fail closed at Pack load time (invariant 18) — an outcome that names counterparts and then terminates could never have them read (**closes E-2**). |
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
implemented — only the shape a future evaluator would read. **This round
changes the tree's shape not at all: the same five nodes, the same sixteen
branches — fourteen leaves and two `next_node` edges — the same four `READY`
leaves, five `BLOCKED` leaves and five `UNKNOWN` leaves, the same `failure_kind`s and
`gap_kind`s, and the same fifteen structural invariants, every one of which
is restated below unweakened.** What this round adds is three further
invariants, 16–18, which constrain the *new* `subject_grain` /`pair_source`
declaration and nothing else, and which no existing invariant depends on. A
grain says how many readings a node consumes; it never changes what a branch
does with one, so 1–15 are untouched by construction. §6 re-proves the two
properties a reader would reasonably suspect this round of having moved: the
ten `resolution_routes[]` still stand in exact one-to-one correspondence with
the ten non-`READY` leaves, and all four root-to-`READY`-leaf paths still
close under invariant 12.

**Shape.** Each activity names one `decision_root_node`. A decision node
names one `evidence_requirement_id` and a set of `branches`, one per outcome
that evidence requirement declares (§3.1, §3.2). A branch is a leaf —
`{ outcome, verdict, failure_kind?, gap_kind?, renders_inapplicable? }`,
where `verdict` is restricted to `READY`, `BLOCKED`, or `UNKNOWN`;
`verdict = "BLOCKED"` requires `failure_kind` and forbids `gap_kind`;
`verdict = "UNKNOWN"` requires `gap_kind` and forbids `failure_kind`;
`verdict = "READY"` forbids both. Both `failure_kind` and `gap_kind` draw
from the same shared `resolution_kind` namespace and must match a
`resolution_routes[].resolution_kind` (§3.1; **closes R2 gap 2, closes R5
item 2**) — or a leaf is instead an interior branch — `{ outcome, next_node,
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
uses the file (closes R2 gap 5, closes R3 gap 3, closes R4 gap 2) — all
fifteen below unchanged this round, with three further ones added after them
(closes E-2):**

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
    the way). Checked exhaustively over every such path, of which there are
    finitely many since the tree is finite and acyclic. Every value inside a
    `renders_inapplicable` list must itself be an `evidence_requirement_id`
    the same activity declares.
13. **A branch's `renders_inapplicable[]` contains no duplicate entries.**
14. **A branch's `renders_inapplicable[]` never names the
    `evidence_requirement_id` of the node the branch itself belongs to** —
    a branch exists because its own node's evidence requirement was just
    tested, so marking that same requirement inapplicable in the same
    outcome is a direct contradiction, and is checked locally per branch
    rather than only through the whole-path disjointness in invariant 12.
15. **Once a branch renders an `evidence_requirement_id` inapplicable, no
    node testing that same `evidence_requirement_id` may appear on any path
    descending from that branch** — checked over every path *prefix* in the
    tree, regardless of what verdict that path eventually reaches, so a
    `BLOCKED`- or `UNKNOWN`-terminating path cannot silently retest evidence
    an ancestor already ruled out any more than a `READY`-terminating one
    could, which invariant 12 alone — scoped only to `READY`-leaf paths —
    would not catch.

**Three further invariants, added this round, governing `subject_grain` and
`pair_source` only (closes E-2):**

16. An evidence requirement declares `pair_source` **iff** its `subject_grain`
    is `per-subject-pair`. That `pair_source` names a
    `from_evidence_requirement_id` that exists in `evidence_requirements[]`
    and that **every** activity declaring the pair-grained requirement also
    declares, and an `on_outcome` that is one of the named requirement's own
    declared `outcomes[]`.
17. **Every node testing a `per-subject-pair` evidence requirement is
    reachable only along paths whose prefix contains a branch of the pair
    source's node taking exactly `on_outcome`** — checked over every path
    prefix, the same way invariant 15 is. This is what makes the counterpart
    keys exist before anything is keyed by them: a pair-grained reading is
    structurally unaskable until the determination that names its counterparts
    has been taken.
18. **That `on_outcome` branch is a `next_node` branch, never a leaf.** An
    outcome whose whole point is to name counterparts, that then terminated
    the path, could never have those counterparts read, and would make
    invariant 17 vacuously satisfiable by an unreachable node.

In this Pack the three are exercised exactly once, by `opening-status`:
`pair_source` names `penetration-determination` on `penetration-confirmed`
(16); `opening-status-node` is reachable only through that branch (17); and
that branch carries `next_node = "opening-status-node"` rather than a verdict
(18). Nothing about invariants 1–15 is relaxed to make room for them — 16–18
add checks, they remove none, and a Pack that fails any of 1–15 still fails
closed exactly as before.

Invariants 13–15 close three narrower gaps `renders_inapplicable` itself
could otherwise open: a duplicate entry (13) is inert but marks an authoring
mistake worth catching; a branch marking its own just-tested requirement
inapplicable (14) is a direct contradiction, catchable without walking any
path at all; and because invariant 12 examines only paths that terminate in
`READY`, invariant 15 is scoped to every path prefix so a retest on a
`BLOCKED`- or `UNKNOWN`-terminating path cannot escape it. None of the three
is exercised by this Pack's one `renders_inapplicable` declaration —
`no-penetration`'s.

Invariants 10 and 11 correct a false claim from an earlier revision:
acyclicity (invariant 5) alone does not give every node "exactly one parent
chain back to its activity's root" — an acyclic graph can still merge two
branches into one shared downstream node. Invariants 10 and 11 close that
gap directly: every non-root node has exactly one incoming edge, and no node
is shared between two activities, so each activity's `decision_nodes` really
are a tree, and every reachable node has one unique path back to its root.

Even with a genuine tree, invariant 8 alone was never sufficient to prove a
`READY` path never bypasses applicable evidence — only that a node for each
declared evidence requirement exists *somewhere* in the tree, not that every
path to a `READY` leaf passes through it. `builders-work-openings`'s own
`no-penetration → READY` branch is the exact counterexample that motivated
this fix: it is a one-node path testing only `penetration-determination`,
and `opening-status`'s node exists elsewhere in the same tree — reachable
only via the `penetration-confirmed` branch — without ever being reached
from this particular `READY` leaf. **Invariant 12 is the actual sufficient
condition:** it walks every root-to-`READY`-leaf path and requires each
declared evidence requirement to be either tested on that specific path, or
explicitly ruled inapplicable by an earlier branch on that same path via
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
# purpose-packs/interdisciplinary-coordination-readiness/pack.toml — continued.
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
`resolution_routes[]` entries in §3.2. The `no-penetration` branch's
`renders_inapplicable = ["opening-status"]` is the only structural
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
specific assessment. That promotion must cite, and the runtime record must
retain, all of the following (closes R5 item 3):

- the leaf's **original verdict** (`BLOCKED` or `UNKNOWN`);
- its **`resolution_kind`**;
- the **underlying evidence gap or blocker** the leaf named;
- a **named authoriser**;
- the **Overlay authorisation role** that authoriser acted under — the
  specific `may_authorise_roles` entry from the `overlay.risk_authorisations[]`
  row matching this exact `pack_id::resolution_kind` (§3.5, §3.7); a
  promotion citing a role not listed for this `resolution_kind` is not a
  `CONDITIONAL`, it is an unauthorised release;
- the **named model versions** the promotion applies to;
- the **accepted risk**;
- the **release scope**;
- the **voiding or failure condition** that would end the release.

Every one of these is a runtime fact about one assessment; **none of them is
written into a Pack or an Overlay example anywhere in this document** —
`overlay.risk_authorisations[]` states only who *may* act, never that anyone
*has*. The promotion is additive, never substitutive: a `CONDITIONAL`
release with no recorded blocker or gap underneath it would be
indistinguishable from a fabricated `READY`, exactly the collapse
Checkpoint B's invariant 6 exists to prevent. **`CONDITIONAL` never becomes
`READY`, and it never eliminates the original blocker or gap** — it is a
recorded acceptance of risk against a real deficiency, layered on top of
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
   `decision_nodes`, `directions[]`, or `resolution_routes[]` (anything in
   §3.1's Pack column); touch no project. Expected: `git diff --exit-code --
   data/processed reports` passes; `epc-ct snapshot` reports no drift;
   every `validation_run_id`, `requirement_key`, and `finding_key` in
   `data/processed/canonical/` is byte-identical; `contract-1.6.json`'s
   recorded file list and SHA-256s are unchanged.
2. **Change only an Overlay** — edit `pcert-sample`'s `[overlay]` table
   (`evidence_bindings`, `team_mapping`, `risk_authorisations`,
   `cost_parameters`, `conventions` — anything in §3.1's Overlay column);
   touch no model, ruleset, or programme. Expected: identical to (1), for
   **the entire published output tree of both projects**, not merely "the
   other project's rows" — nothing in the pipeline reads `[overlay]` today,
   so neither project's published bytes may move by even one row.
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
- **A Pack may carry more than one direction of its flagship purpose.**
  `directions[]` is a list (§3.2); this worked example declares one.
- **A project has exactly one Overlay** — the singular `[overlay]` table in
  its `project.toml` — which contains the arrays needed to bind however many
  Packs the project actually uses. There is no per-Pack overlay file and no
  `[overlay.<pack_id>]` nesting; every list inside `[overlay]` tags its own
  rows with `pack_id` where disambiguation is needed (`evidence_bindings`,
  `accepted_evidence_methods`, `risk_authorisations`), and leaves rows that
  are naturally project-wide untagged (`team_mapping`, `cost_parameters`).
- **`activity_id` and `evidence_requirement_id` are Pack-local identities,
  and so is `direction_id`.** Two different Packs may freely reuse the same
  local name — `schedules`, say — with no collision, because the identity
  that must be unique is the compound `pack_id::activity_id`, and `pack_id`
  is already required unique. This mirrors `model_id` (project-scoped,
  human-chosen) versus `model_key` (`project_id::model_id`, the
  actually-unique join identity) exactly as `AGENTS.md` already draws that
  line for models. An activity's `direction_id` is a fact about that
  activity's content, not a second identity axis: `pack_id::activity_id`
  remains the whole of an activity's identity.
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

| Checkpoint B activity | `activity_id` (illustrative) | `direction_id` | Evidence requirements | Binding | Live verdict (runtime fact, unaffected by this design) |
|---|---|---|---|---|---|
| Room data sheets / equipment schedules | `schedules-and-room-data-sheets` | `mep-to-architecture` | `asset-identity` | Overlay-bound to R-005A/B's four `requirement_key`s (§3.5) | **BLOCKED** (case 2) |
| Ceiling / bulkhead geometry | `ceiling-and-bulkhead-geometry` | `mep-to-architecture` | `in-model-position`, `cross-model-alignment` | Pack-bound to R-004A/B for the first; `assessment` for the second, with R-010 named only as insufficient evidence | **UNKNOWN** (case 3) |
| Builder's-work openings | `builders-work-openings` | `mep-to-architecture` | `penetration-determination`, `opening-status` | `assessment` for both — no validation requirement in rule set 2.2 answers either | **UNKNOWN** (case 4) |

**All three activities declare the same three `subject_classes`
(`IfcDuctSegment`, `IfcAirTerminal`, `IfcChimney`) — the MEP work products
this direction hands to Architecture.** The coincidence is a fact about this
Pack, not about the schema; an activity about architectural fabric would
declare fabric classes, which is why the list lives on the activity rather
than on the Pack. What it excludes in `pcert-sample` is exactly the two
`IfcBuildingElementProxy` setout markers, `origin` and `geo-reference`; what
it keeps is the `IfcChimney` that carries no finding at all.

**All three activities resolve to the Pack's one declared direction,
`mep-to-architecture` (§3.2; closes R5 item 1).** Nothing about proving §3's
shape sufficient for Checkpoint B's scenario required a second direction to
exist — the point is that the shape does not foreclose one, and §3.2 already
states exactly what adding one would take: a `directions[]` entry and
activities pointing at its `direction_id`, nothing more.

**Openings is no longer represented with zero evidence entries.** It names
exactly the two evidence requirements Checkpoint B case 4 describes, both
currently unsatisfiable by rule set 2.2's evidence — which is why the live
verdict stays UNKNOWN and is now *representable* as UNKNOWN, rather than
silently indistinguishable from an activity with no evidence model at all.

**The full resolution trace, for all ten `resolution_kind`s this Pack's
trees can produce — from `resolution_kind` through verdict class,
consequence, default role, next action, to recheck condition, in one table
(closes R5 item 2):**

| `resolution_kind` | Verdict class | Consequence kinds | Default role | Next action | Recheck condition |
|---|---|---|---|---|---|
| `missing-project-asset-identity` | BLOCKED | work-cannot-start, re-identification-and-reissue-risk | model-coordination | Populate or correct the project-required asset-identity values at source per the Overlay binding and re-export; which properties/fields is project-specific and not named by the Pack | Every bound `requirement_key` evaluates PASS for every element in scope, none uncovered |
| `asset-identity-not-evaluated` | UNKNOWN | work-suspended | model-coordination | *Not a model defect* — run the evaluation over the full assessed scope | Every element in scope is covered by an evaluation, none absent |
| `mep-element-not-spatially-assigned` | BLOCKED | work-suspended | mep-lead | Host the element to its correct level/space before export | The R-004-bound requirement_key(s) evaluate PASS for the element |
| `in-model-position-not-evaluated` | UNKNOWN | work-suspended | **information-manager** | *Not a model defect* — run the evaluation; extend rule applicability if a rule authoring gap is the cause | Every element in scope is covered by a finding |
| `cross-model-misalignment` | BLOCKED | work-suspended | model-coordination | Re-acquire the shared coordination datum and re-export placement against it | The alignment-confirmation method is re-run and reports confirmed |
| `cross-model-alignment-not-confirmed` | UNKNOWN | work-suspended, rework-risk | model-coordination | *Not a model defect* — perform the accepted alignment-confirmation method | The method is performed and reports confirmed, for the named versions |
| `penetration-not-determined` | UNKNOWN | work-suspended | model-coordination | *Not a model defect* — hold the coordination-review determination | A recorded determination exists (no-penetration or the element named) |
| `opening-not-verifiably-linked` | BLOCKED | work-suspended, rework-risk | **architecture-lead** | Add/correct the cross-reference from the modelled opening to the penetrating element, one per pair | The opening-cross-reference-check is re-run and reports cross-referenced, for the pair |
| `missing-corresponding-opening` | BLOCKED | work-suspended | **architecture-lead** | Model the opening in Architecture, hosted in the architectural element this penetration passes through — one per pair | The opening-status evaluation reports cross-referenced for the pair |
| `opening-status-not-determined` | UNKNOWN | work-suspended | model-coordination | *Not a model defect* — complete the opening-status review | The review reports a definite result (cross-referenced, modelled-not-cross-referenced, or not-modelled) |

**A reviewer can now start from any non-`READY` leaf's `resolution_kind`
alone and reach the full chain — consequence, resolving role, next action,
recheck — through one table, not three separately-addressed fields.** The
two blockers product review named specifically stay traceably distinct
end to end: `opening-not-verifiably-linked`'s action *adds a link*, its
recheck *re-checks the link*; `missing-corresponding-opening`'s action
*models the opening*, its recheck *confirms the opening exists and is
linked*.

**The completed outcome → verdict → `resolution_kind`/route state space
(§3.8), for all three activities, with the live path in each tree marked:**

| Activity | Evidence requirement | Outcome | Verdict | `resolution_kind` |
|---|---|---|---|---|
| Schedules | `asset-identity` | satisfied | READY | — |
| Schedules | `asset-identity` | **unmet (live)** | **BLOCKED** | `missing-project-asset-identity` |
| Schedules | `asset-identity` | not-yet-evaluated | UNKNOWN | `asset-identity-not-evaluated` |
| Ceiling | `in-model-position` | **satisfied (live)** | *(→ cross-model-alignment)* | — |
| Ceiling | `in-model-position` | unmet | BLOCKED | `mep-element-not-spatially-assigned` |
| Ceiling | `in-model-position` | not-yet-evaluated | UNKNOWN | `in-model-position-not-evaluated` |
| Ceiling | `cross-model-alignment` | confirmed | READY | — |
| Ceiling | `cross-model-alignment` | misaligned | BLOCKED | `cross-model-misalignment` |
| Ceiling | `cross-model-alignment` | **not-yet-confirmed (live)** | **UNKNOWN** | `cross-model-alignment-not-confirmed` |
| Openings | `penetration-determination` | no-penetration | READY | — |
| Openings | `penetration-determination` | **not-yet-determined (live)** | **UNKNOWN** | `penetration-not-determined` |
| Openings | `penetration-determination` | penetration-confirmed | *(→ opening-status)* | — |
| Openings | `opening-status` | cross-referenced | READY | — |
| Openings | `opening-status` | modelled-not-cross-referenced | BLOCKED | `opening-not-verifiably-linked` |
| Openings | `opening-status` | not-modelled | BLOCKED | `missing-corresponding-opening` |
| Openings | `opening-status` | not-yet-determined | UNKNOWN | `opening-status-not-determined` |

The three live rows compose to the same **BLOCKED / UNKNOWN / UNKNOWN** this
design has stated since the first revision. Renaming the Pack, adding
`directions[]`, consolidating four fields into `resolution_routes[]`,
restructuring risk authorisation, and deferring overrides move none of
them — every fix in this round completes or reorganises the fixed inputs
around this run's evidence; none of it is evidence, and none of it computes
a verdict.

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
its activity's full declared evidence set.

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
  unchanged from every prior revision: this document changes nothing about
  `rules/epc-delivery/R-010.toml` or the `completeness` checker and does not
  depend on that divergence being fixed.
- **`discipline_scope` remains validation applicability only.** §3.2's
  `directions[]` table is new Pack data, never a reinterpretation of
  `discipline_scope`.
- **R-005 enters this design only through `overlay.evidence_bindings[]`**
  (§3.5), never through the Pack, in this or any prior revision.

**Re-proof 1 — the ten `resolution_routes[]` still stand in exact one-to-one
correspondence with the ten non-`READY` leaves.** This round changed three
rows' `default_role` and two rows' `next_action` / `recheck_condition`
wording. It added no route, removed none, renamed no `resolution_kind`, and
touched no branch. Enumerated from §3.8's five nodes:

| Node | `BLOCKED` leaves → `failure_kind` | `UNKNOWN` leaves → `gap_kind` |
|---|---|---|
| `asset-identity-node` | `unmet` → `missing-project-asset-identity` | `not-yet-evaluated` → `asset-identity-not-evaluated` |
| `in-model-position-node` | `unmet` → `mep-element-not-spatially-assigned` | `not-yet-evaluated` → `in-model-position-not-evaluated` |
| `cross-model-alignment-node` | `misaligned` → `cross-model-misalignment` | `not-yet-confirmed` → `cross-model-alignment-not-confirmed` |
| `penetration-determination-node` | — | `not-yet-determined` → `penetration-not-determined` |
| `opening-status-node` | `modelled-not-cross-referenced` → `opening-not-verifiably-linked`; `not-modelled` → `missing-corresponding-opening` | `not-yet-determined` → `opening-status-not-determined` |

Five `failure_kind`s and five `gap_kind`s, ten distinct values, each matching
exactly one of the ten `resolution_routes[]` rows, and every row used by at
least one leaf. Unchanged from the previous revision, value for value.

**Re-proof 2 — all four root-to-`READY`-leaf paths still close under
invariant 12, and the four-path table above still holds line for line.**
`subject_grain`, `pair_source` and `subject_classes` are not evidence
requirements and appear nowhere in a path, so nothing this round touches enters
the tested-versus-inapplicable accounting at all: the same four paths, the same
tested sets, the same one `renders_inapplicable` declaration, the same
disjointness, the same union. Invariants 16–18 add three checks over that same
unchanged structure and relax none of 1–15 — `opening-status` declares
`pair_source` and carries the pair grain (16); `opening-status-node` is
reachable only through the `penetration-confirmed` branch (17); and that branch
is a `next_node` branch rather than a leaf (18).

**Re-proof 3 — the live verdicts are unmoved.** The three rows of §6's
scenario table are still **BLOCKED / UNKNOWN / UNKNOWN**, on the same evidence,
for the assessed scope Checkpoint B walked. Roles say *who resolves* a
non-`READY` leaf and never *which* leaf is reached; `subject_classes` excludes
only the two setout proxies, neither of which is in any Checkpoint B case's
scope; and the pair grain applies only below `penetration-confirmed`, a branch
no live evidence reaches — case 4 is live at `not-yet-determined`, one node
above it.

**What the pair grain and the class list *do* change is what a broader request
can now express, and both are worth stating because both were previously
inexpressible:**

- A request scoping the ceiling activity to the whole `hvac` `model_key` now
  yields two subscopes rather than one confused one: the duct and two air
  terminals, which pass R-004 and continue to `cross-model-alignment =
  not-yet-confirmed` → `UNKNOWN` / `cross-model-alignment-not-confirmed`; and
  the `IfcChimney`, which no R-004 requirement reaches → `UNKNOWN` /
  `in-model-position-not-evaluated`, whose corrected role is now the
  information manager who would extend the rule set. That is Checkpoint B case
  4's gap 1 and case 3, side by side, each with its own gap kind and its own
  resolver — and the two setout proxies are in neither subscope, listed instead
  as out-of-class for the activity.
- A chimney determined to penetrate both a floor slab and the roof yields two
  `opening-status` pair readings. The common live shape — the slab opening
  modelled and cross-referenced, the roof opening not modelled — now partitions
  into one `READY` pair and one `BLOCKED` /`missing-corresponding-opening`
  pair, instead of collapsing into a single reading that could only be one or
  the other. The reverse cardinality is the same mechanism: one shared shaft
  opening serving three MEP lines is three pairs naming the same counterpart,
  each asking whether that opening is inspectably linked to its own penetrating
  element.

Neither bullet asserts live evidence. Both are counterfactuals in exactly the
sense §3.2's two worked counterexamples already are — what the shape can now
carry, stated so a reviewer can check that it can.

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
designed. **No project override capability is implemented or assumed —
§3.6 defers the entire mechanism, not merely narrows it.** Nothing is
merged, tagged, or released. Checkpoint D is not started.

## Consequences

This document commits a future implementation to: two file locations
(`purpose-packs/<pack_id>/pack.toml`, `projects/<id>/project.toml`'s
singular `[overlay]` table, which may bind several Packs); a Pack that names
one flagship purpose and may carry **several directions** of it, each
declared once in `directions[]` and referenced by every activity's
`direction_id` — never redefining activity identity, which stays
`pack_id::activity_id`, and never derived from `discipline_scope`; a
two-layer evidence design in which an activity names Pack-owned **evidence
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
standing in for a verdict, since only a tree's terminal leaf is one; an
atomic observation unit (one element × one bound `requirement_key`) whose
own `FAIL` / not-covered / `PASS` findings collapse to one outcome by a
within-unit reading rule in which a known failure dominates a coverage gap
**only inside that one unit** — never across units, where an assessed scope
whose units disagree on the named outcome is partitioned into
outcome-homogeneous subscopes before the tree runs (no priority, no text
order, no default picks one for it), with subscope construction, identity,
and recording left to Checkpoint D; **a declared object scope per activity**
(`subject_classes`) and **a declared grain per evidence requirement**
(`subject_grain`, with `pair_source` for the pair grain), so that what an
activity is about and how many readings a question has are both Pack data
rather than runtime inference — the class list never a findings filter, the
pair grain keyed on two elements that both exist so no key is ever minted for
an opening that is not there; eighteen structural invariants a Pack's decision
tree must satisfy at load time — the original fifteen unchanged and
unweakened, covering root/edge existence, uniqueness, true per-activity tree
shape, and the sufficient condition for `READY`-path closure, plus three
governing the pair grain and nothing else; **one canonical `resolution_routes[]` table**, keyed
by `resolution_kind` and reachable from any `BLOCKED`/`UNKNOWN` leaf,
carrying default role, consequence kinds, next action, and recheck
condition together — with each row's `default_role` naming the role that does
the work that row's own `next_action` describes, so that openings work in the
architectural model resolves to `architecture-lead` and a rule-authoring gap
to `information-manager` rather than to whichever role happened to be nearby —
replacing four separately-addressed fields, with an
orphaned route, a duplicate `resolution_kind`, an incomplete row, or a leaf
matching no row all failing the Pack closed, and with reuse of one
`resolution_kind` across leaves only ever meaning identical treatment, by
construction; `CONDITIONAL` reachable only as a runtime promotion that must
cite and retain the promoted leaf's original verdict, `resolution_kind`,
underlying blocker or gap, a named authoriser, the specific Overlay
authorisation role that authoriser acted under, named model versions, the
accepted risk, the release scope, and a voiding condition — and that can
never become `READY` or erase the deficiency it was promoted from; a
**per-`pack_id::resolution_kind` risk-authorisation table**, never a
project-wide blanket list, with no wildcard, no `"all"`, and no derivation
of an authoriser from a resolving role — a `resolution_kind` with no
matching authorisation row simply has no path to `CONDITIONAL`, not a
default one; **no project-override capability**, with any future one
required to be machine-verifiably monotone against four named properties
before it may even be proposed, and never a free-text patch or expression
language; three independent compatibility axes — Pack schema format (this
ADR's first publishable format, `"1"`), Pack content version, and per-binding
ruleset
identity — with Framework machine-contract compatibility named as not yet
nameable rather than fabricated; a project that may use multiple Packs
through one Overlay, with Pack-local `activity_id`/`evidence_requirement_id`
/`direction_id` disambiguated only by `pack_id`, and no Overlay-owned
project identity duplicating `[project].project_id`; fail-closed composition
with no silent defaults, including a project with no Overlay leaving the
existing pipeline untouched; and the four changed-input counterfactuals in
§4 — all of them, with no exception — as the acceptance test for Checkpoint
D's identity claims. It commits nothing about how a decision tree is
actually evaluated at runtime, how subscopes or `AssessmentRun`-shaped state
(if any) are named, when a future override capability might be designed, or
when Checkpoint D begins — those remain open, and deliberately so.
