# 0003 — Runtime purpose assessment: request scope, subscopes, record shape, and identity boundary

- **Status:** Proposed. This is a runtime-design decision for review, not an
  implementation. No code, rule, checker, test, schema, configuration file,
  CLI, loader, evaluator, or generated artifact is added or changed by this
  document. It fixes the *shape* of a runtime purpose assessment — what a
  request is bounded by, how underlying observations become
  outcome-homogeneous subscopes, what one assessment records, how a
  `CONDITIONAL` promotion is recorded, and whether a runtime fact ever mints
  an identity — so that a future implementation can walk the Purpose Pack and
  Project Overlay shape fixed in
  [`0002-minimal-purpose-pack-project-overlay.md`](0002-minimal-purpose-pack-project-overlay.md)
  without redesigning that format, and so that running an assessment is
  structurally incapable of moving a published byte.
- **Date:** 2026-09-03.
- **Scope:** Checkpoint D runtime design only — the request boundary, the
  subscope construction rule ADR 0002 §3.2 explicitly left here, the
  assessment record shape, the runtime identity boundary, and the
  fail-closed behaviour of the assessment step itself when a composed
  Pack/Overlay input is incomplete. It does **not** implement an evaluator, a
  Pack/Overlay loader, fail-closed *composition* logic, a machine contract, a
  CLI, BIM Doctor, a second Pack, or a Registry. It does not touch contract
  1.6, and it does not change validation, requirement, finding, or legacy
  identity.
- **Depends on:**
  - the four-layer ownership boundary, the field shapes, the closed decision
    tree and its fifteen structural invariants, the ten `resolution_routes[]`,
    the per-`pack_id::resolution_kind` risk-authorisation table, and the four
    changed-input counterfactuals fixed in
    [`0002-minimal-purpose-pack-project-overlay.md`](0002-minimal-purpose-pack-project-overlay.md)
    (Checkpoint C);
  - the four worked decisions, the four verdict definitions, and the six
    Framework invariants in
    [`docs/product/interdisciplinary-coordination-readiness-mep-to-architecture.md`](../product/interdisciplinary-coordination-readiness-mep-to-architecture.md)
    (Checkpoint B);
  - the correctness and identity guarantees fixed in
    [`0001-phase4-correctness-and-identity.md`](0001-phase4-correctness-and-identity.md)
    and implemented in contract 1.6.
- **Governs:** the runtime shape of the seam already recorded in `AGENTS.md`
  ("A purpose assessment, if it is ever built, is approved between `check` and
  the compatible group") and in ADR 0002 §7 (`check → purpose assessment →
  compatible group`). It moves neither document, and it adds nothing to
  `default_registry`.
- **Does not decide:** how the decision tree is evaluated in code; how the
  composed Pack/Overlay is loaded or composition-validated (the next route
  item); where an assessment record is physically stored; any machine
  contract, CLI surface, or Doctor experience; product semantics, the verdict
  vocabulary, the attribution boundary, or any contract move — all of which
  are owned elsewhere and are not this document's to touch.

## What this document fixes, and where

| # | Question this checkpoint must answer | Section |
|---|---|---|
| 1 | The assessed scope: its definition, its source, and its relationship to the model-version context | §2 |
| 2 | How a subscope is constructed, identified, and recorded (ADR 0002 §3.2 left this here) | §3 |
| 3 | Where the assessment step sits in the pipeline, and its input/output boundary | §1 |
| 4 | What one assessment records, including every field a `CONDITIONAL` promotion must carry | §4 |
| 5 | Whether any runtime identity is minted, and the constraints on it | §5 |
| 6 | How several subscopes of one activity with different verdicts are presented, under Framework invariant 1 | §6 |
| 7 | How every missing input (evidence, binding, role, authorisation, method) fails closed, mapped row-by-row to ADR 0002 §3.7 | §7 |
| — | The four ADR 0002 §4 changed-input counterfactuals, restated as this design's acceptance commitments | §8 |

Every fragment below is a **design illustration**. No assessment record, no
request payload, and no runtime object is created by this document, and no
example states a verdict, an authorisation, a cost, an alignment
confirmation, or a handover as if it had happened.

---

## 1. What a runtime purpose assessment is, and where it sits

### 1.1 It is a demand-driven, read-only branch off the validated facts

**Answer (position).** A runtime purpose assessment is **not** a pipeline
stage. It is a separate, demand-driven operation that runs *on request* for
one `{project, pack, direction, activities, assessed scope, model-version
context}` tuple. It reads the facts that already exist after `check` and
before `group`, walks a Pack's decision tree (§3.8 of ADR 0002) over them,
and writes exactly one **assessment record**. It is:

- **not a `Checker`** — it evaluates no requirement against a model, and mints
  no `Finding`;
- **not a `GroupingPolicy`** — it decides nothing about what counts as one
  actionable `Issue`, and computes no `group_ref` or `issue_key`;
- **not an `Exporter`** — it moves no results into `data/processed/`,
  `reports/`, `ids/`, BCF, or PBIP;
- **not registered.** It does not appear in `default_registry`, and `epc-ct
  run` does not invoke it. Registering an approval step as a pipeline
  component would put a decision inside a projection — exactly what `AGENTS.md`
  forbids.

The logical ordering `check → purpose assessment → compatible group` in
`AGENTS.md` and ADR 0002 §7 is a statement about *what reads what*: the
assessment consumes validated `Finding`s (not `Issue`s), so it runs after
`check`; it emits nothing into the grouping path, so `group` and every
exporter are strictly downstream and wholly independent of it. Whether or not
an assessment is ever requested, `check → group → export`, the snapshot, and
both `Legacy…` writers produce byte-identical output.

### 1.2 Input boundary — everything read, nothing mutated

An assessment reads, and only reads:

1. **The validated facts for the project**, as they stand after `check` and
   before `group`: the `Requirement` set, the `Finding` set (each with its
   `status`, and its `is_issue` **as the contract 1.6 validation fact it is —
   never reinterpreted as a readiness outcome**; see §3.4), the project's
   model element inventory, the project programme / milestone dates, and the
   `validation_run_id`, `ruleset_id`, and `ruleset_version` of that run.
2. **The composed Pack(s) and Overlay for the project** — produced and
   fail-closed-validated by the loading/composition route item that follows
   this one. This document *consumes* that composed structure; it does not
   design its loader or its composition checks. Where §7 says the assessment
   "fails closed", it means the assessment refuses to produce a verdict when
   the composed input it was handed cannot support one — not that the
   assessment re-runs composition validation.
3. **The assessment request**:
   `{ project_id, pack_id, pack_version, direction_id, activity_ids[],
   assessed_scope, model_version_context }` (§2).
4. **Recorded determinations for assessment-bound evidence** — the outputs of
   the `overlay.accepted_evidence_methods[]` methods (an alignment
   confirmation, a coordination-review determination, an opening
   cross-reference check). These are runtime evidence; their production and
   storage are not designed here. The assessment reads them **by reference**
   and records which references it read (§4).

### 1.3 Output boundary — one record, outside the published tree

An assessment writes exactly one **assessment record** (§4). That record:

- lives **outside** `data/processed/`, `reports/`, `ids/`, and the contract
  snapshot. Its physical storage medium and location are a later decision;
  this document fixes only that it is not any published-contract path and its
  presence or absence moves zero published bytes (§8).
- is **never read back** by `group`, any `Exporter`, `epc-ct run`, `epc-ct
  snapshot`, `LegacyBcfExporter`, `LegacyPbipAdapter`, `test_determinism.py`,
  or `test_contract_snapshot.py`.
- mutates nothing. No `Finding`, `Requirement`, `Issue`, `RunBundle`, CSV,
  archive, manifest, or identity is created or changed by an assessment.

The dependency arrow points one way: an assessment **cites** frozen
identities (`validation_run_id`, `requirement_key`, `finding_key`,
`model_key`, `element_key`); nothing frozen ever cites an assessment (§5).

---

## 2. The assessment request: assessed scope and model-version context

### 2.1 The assessed scope

**Answer (definition).** The **assessed scope** is the caller's explicit
declaration of *which labour the verdict is a statement about*: a
deterministically ordered set of `element_key`s and/or `model_key`s, drawn
from the model versions named in the model-version context, over which the
assessment's verdict for each requested activity ranges. It is the middle
coordinate of Framework invariant 1 — "exactly one verdict per **activity ×
assessed scope × model-version context**" — and it is the scope every
Checkpoint B verdict was a statement about ("READY would cover the assessed
scope of those three elements, not the model").

**Answer (source).** The assessed scope is a **required input to the
request**. It is:

- **not** derived from which `Finding`s happen to exist. Letting coverage
  define scope is precisely the Checkpoint B case-4 trap: an `IfcChimney` that
  no rule reaches would silently leave the scope instead of surfacing as an
  unevaluated element.
- **not** owned by the Pack or the Overlay. A Pack owns which activities exist
  and which evidence they need; it does not own which elements a given
  project's given handover is deciding about.
- **not** implied by the `direction_id` or the activity. Direction is a fact
  about the handover's orientation, not an element set.

A caller may declare the scope as narrowly as a single `element_key` or as
broadly as a whole `model_key`. A `model_key` in the scope means *every
element in that model version*, expanded deterministically from the model's
element inventory — which is what makes an unevaluated element appear as a
`not-yet-evaluated` subscope (§3) rather than vanish. The request records the
scope exactly as declared; the assessment resolves coverage *within* it and
never widens or narrows it silently.

The **release scope** of a future `CONDITIONAL` promotion (§4.4) is a
separate, possibly narrower, named scope — "ground-floor ceiling zones only"
in Checkpoint B case 3's counterfactual. It is never the assessed scope by
default and is recorded independently.

### 2.2 The model-version context

**Answer (definition).** The **model-version context** names the exact
artefacts the verdict is true of:

- the **producing** model: `model_key` + its content identifier (the
  content hash `models.csv` already carries; there is no issue status,
  revision, or suitability code in contract 1.6, and none is invented here);
- the **consuming** model: `model_key` + content identifier;
- the **handover event**: which role issued to which role, at which
  milestone, on which date. This is runtime data absent from the repository
  today; the assessment records it as supplied in the request and derives
  none of it.

### 2.3 How the two relate

- The assessed-scope keys are resolved **relative to** the producing model
  version. Evidence requirements that span both models (`cross-model-alignment`,
  `opening-status`) additionally range over the consuming model version in
  the same context.
- The pair *(assessed scope, model-version context)*, together with one
  activity, is one Framework-invariant-1 cell. The **same** `element_key`
  list against a **different** model-version context is a different cell and a
  different assessment — never an update of an existing verdict.
- The model-version context must be **consistent with the cited
  `validation_run_id`**: that run must have validated exactly the producing
  and consuming model versions in the context. A context naming a model
  version the cited run did not cover fails closed (§7) — the assessment has
  no validated facts it may honestly attribute to those versions.
- A verdict is only ever true of the exact versions named. Re-issuing either
  model makes every prior verdict for that context **stale**, requiring a
  fresh assessment; a recheck (§4.5) re-confirms both that the underlying
  evidence still reads as before **and** that the context is still current,
  by comparing content identifiers — a value comparison, never a clock read.
- The validation run's logical `as_of` is configuration
  (`AGENTS.md` rule 1) and part of `validation_run_id`; it is provenance of
  the context, not itself a model version, and the assessment reads no other
  clock.

---

## 3. Observation subjects, readings, and outcome-homogeneous subscopes

ADR 0002 §3.2 fixed the *constraint* — "an assessed scope may never be forced
through the decision tree as a single unit when its own underlying
observations disagree on the named outcome, whether or not those outcomes
share a Framework class" — and explicitly left construction, identification,
recording, and any roll-up "to Checkpoint D". This section fixes them, and
separates the *carrier* of a split from the *readings* hung on it (D-1 of the
technical-director review).

### 3.1 Observation subjects, readings, and grain

Three terms, kept distinct:

- An **observation subject** is the thing a subscope's membership is a *set
  of*, and the only thing that is split, ordered, and recorded as a
  subscope's members. It is always a key that actually exists: an
  `element_key`, or — for an activity whose every evidence requirement is
  `whole-scope` (below) — the single model-pair subject
  `(producing model_key, consuming model_key)`. An activity's observation
  subjects are its assessed scope (§2.1), resolved against the producing
  model version, to the finest grain any of its evidence requirements reads
  at. In this worked Pack every activity's subjects are `element_key`s.
- A **reading** is one evidence requirement's outcome for one subject: the
  subject paired with one binding of that evidence requirement — a
  `requirement_key`, or an accepted `method_id` — reducing to exactly one of
  the evidence requirement's declared `outcomes[]`. A reading is what ADR
  0002 §3.2 calls an *atomic observation unit*; it is hung on a subject,
  never a subject itself.
- A **grain** is how an evidence requirement's readings relate to subjects:

| Grain | Meaning | This Pack |
|---|---|---|
| `per-subject` | one reading per observation subject | `asset-identity`, `in-model-position` (subject × each bound `requirement_key` that applies to it); `penetration-determination` (the penetrating `element_key`); `opening-status` (the penetrating `element_key` — any corresponding opening is an *attribute* of that subject's determination, present or a named absence, never a second key) |
| `whole-scope` | exactly one reading for the entire assessed scope, hung identically on every subject that reaches the node | `cross-model-alignment` (one fact about the model pair) |

A `whole-scope` evidence requirement contributes **no subject of its own**
and, by definition, cannot be heterogeneous across subjects. A future Pack
that needs a finer alignment fact — per storey, say — declares it
`per-subject` at that grain, and it then splits like any other. A grain is
never finer than the subject and never introduces a key that might not
exist — which is why `opening-status` is keyed by the penetrating element and
not by a penetration/opening pair whose second member is absent exactly when
the outcome is `not-modelled`.

**Within-subject reading rule** (from ADR 0002 §3.2, restated): for a
`per-subject` finding-backed evidence requirement, take every finding for the
subject under every bound `requirement_key` that applies to it; if there is
no such finding at all the reading is `not-yet-evaluated` (the named
absence — recorded, §3.3); otherwise the findings collapse to one outcome by
the precedence `FAIL` > not-covered > `PASS` — extended across the subject's
several applicable `requirement_key`s the same way, so that every subject has
exactly one reading per evidence requirement and the carrier of a split is
always a whole subject, never a subject/key fragment. This is the
construction ADR 0002 §3.2 delegates here: it refines §3.2's "subscopes …
carrying the units that read [an outcome]" to *subjects*, and is monotone
with §3.2's precedence — a `FAIL` under any applicable key still dominates.
The precedence is **only** a within-subject rule and never a cross-subject
selector. For a `per-subject` assessment-backed evidence requirement the
reading is the recorded determination for that subject, or its `not-yet-*`
outcome when none exists.

An `insufficient_evidence[]` entry (R-010 under `cross-model-alignment`) is
**never** a reading: its `PASS` is recorded as context only and produces none
of the outcomes, exactly as ADR 0002 §3.2 states.

### 3.2 Construction — split subjects incrementally down the tree

**Answer (construction).** For one activity, one assessed scope, one
model-version context:

1. **Resolve the observation subjects** (§3.1) and put them in `element_key`
   lexicographic order (equivalently `(model_key, ifc_guid)` ascending) — a
   frozen string key, so the order is deterministic with no clock, no set
   iteration, and no filesystem ordering (`AGENTS.md` rule 1). An activity
   with a single model-pair subject needs no ordering. `whole-scope` evidence
   requirements contribute nothing to this order; their one reading is
   recorded on the path (§3.3), not as a subject.
2. **Walk the decision tree from `activities[].decision_root_node`, carrying
   a current subgroup of subjects — initially all of them.** At each node:
   - **`per-subject` evidence requirement:** read every subject in the
     subgroup (§3.1's within-subject rule, or its recorded determination).
     Subjects that read the **same** outcome stay one subgroup and follow
     that outcome's branch; subjects that read **different** outcomes
     **split** into sibling subgroups, one per distinct outcome actually
     observed, each continuing independently down its own branch or to its
     own leaf.
   - **`whole-scope` evidence requirement:** there is exactly one reading;
     every subject in the subgroup takes it and follows the same branch —
     **the subgroup never splits at a `whole-scope` node.** If the subgroup
     already split at an earlier `per-subject` node, the one `whole-scope`
     reading rides along identically with every surviving subgroup that
     reaches this node.
   - a subject the branch structure never routes to a node — an element
     whose `penetration-determination = no-penetration` branch carries
     `renders_inapplicable = ["opening-status"]` and terminates at `READY` —
     produces no reading for that node's evidence requirement at all. "The
     pair's second member does not exist" never arises: an absent opening is
     an attribute of the penetrating subject's determination (a named
     absence, §3.3), just as an absent finding is.
3. **A subscope is a subgroup that has reached a terminal leaf:** the
   maximal set of observation subjects that traversed the **identical
   ordered path** of `(node_id, outcome)` pairs from the root to that leaf.
   The partition of the activity's assessed scope is the set of these
   leaf-terminal subscopes.

**Splitting is incremental, down the tree — never an up-front cross-product
of every evidence requirement's outcome vocabulary.** A subgroup splits only
at the node that actually distinguishes its subjects, into the outcomes
actually seen there. This is the reason ADR 0002 §3.8 gives for choosing a
decision tree over "a flat table of `(evidence outcome combinations) →
verdict` rows": a cross-product "manufactures meaningless rows for
combinations that can never be asked (e.g. an opening's cross-reference
status when no penetration exists)". Partitioning the assessed scope up front
by the cross-product of every evidence requirement's outcomes would
manufacture exactly those subscopes — a part for "no penetration × opening
not modelled" that the tree can never reach. Incremental splitting visits
`opening-status` only for the subgroup that reached `penetration-confirmed`,
so a subject is asked for an opening determination only where its own
penetration makes the question real — the structural conditional relevance
§3.8 credits the tree with, preserved in the partition.

When every subject reads the same outcome at every node, the partition has
exactly **one** part — the whole assessed scope — which is the live
situation throughout ADR 0002 §6, where no case exercises splitting. When
subjects disagree at some node, the partition has ≥2 parts, each
outcome-homogeneous by construction, each reaching its own leaf and its own
verdict — exactly ADR 0002 §3.2's worked illustration (three `unmet`
elements → `BLOCKED`; one `not-yet-evaluated` element → `UNKNOWN`; the
coverage gap its own subscope, never folded into the blocker).

Nothing here reintroduces a priority rule: `BLOCKED > UNKNOWN > READY` orders
Framework *classes*, never selects a named outcome for a heterogeneous scope
(ADR 0002 §3.2). No text order, alphabetic order, or default ever collapses a
split.

### 3.3 Identification and recording

**Answer (identification).** Within one assessment record, a subscope is
identified by its **ordinal** in the canonical ordering of that activity's
partition: by the subscope's root-to-leaf outcome sequence (lexicographic
over outcome names), then by its smallest member subject key. The ordinal,
together with the record's `assessment_digest` (§5) and the
`pack_id::activity_id`, is the handle a resolving assignment (§4.3), a
`CONDITIONAL` promotion (§4.4), and a later recheck (§4.5) point at.

**Answer (recording — the carrier and the readings hung on it, kept
separate).** Per requested activity, the record carries an ordered list of
subscope entries. Each entry separates:

- **the carrier** — `members`: the ordered observation subjects in the
  subscope (`element_key`s, or the lone model-pair subject). This is the set
  the subscope *is*.
- **the path** — the ordered `(node_id, evidence_requirement_id, grain,
  outcome)` quadruples from root to leaf, and for each node:
  - a `per-subject` node: the per-subject readings — for each member
    subject, `(requirement_key | method_id, outcome, finding_key[] |
    determination reference | named-absence marker)`;
  - a `whole-scope` node: the single reading shared by every member —
    `(method_id, outcome, determination reference | named-absence marker)`.
- **the leaf** — `verdict` (`READY` / `BLOCKED` / `UNKNOWN` only; an outcome
  is never itself a verdict, per ADR 0002 §3.8); `resolution_kind` iff
  `verdict ≠ READY` (the leaf's `failure_kind` or `gap_kind`); the resolved
  `resolution_routes[]` row for that `resolution_kind` (`consequence_kinds[]`,
  `default_role`, `next_action`, `recheck_condition`); and the resolving
  assignment (§4.3).

A subscope has **no identity that outlives its assessment record**. A recheck
names the prior record's `assessment_digest` + activity + subscope ordinal,
then re-derives subscope membership from the current evidence to compare — it
does not assume the partition is stable across records.

### 3.4 What the assessment must never do with validation metadata

Reading a `Finding` is reading a validation fact. The assessment:

- reads `status` (`PASS`/`FAIL`) and the presence/absence of a finding, and
  nothing else, to reduce a reading (§3.1);
- **never** reads `Finding.is_issue`, `Issue`, or a `Requirement`'s
  `owner_role`, `severity`, `stage`, `priority`, or `labels` as a readiness
  concept. `is_issue` means "this check failed in a way that warrants a
  topic"; the readiness verdict is a function of *(evidence outcome, decision
  tree)* and is new information owned by the Pack (Checkpoint B §4;
  `AGENTS.md`). In particular a `WARNING`-severity `FAIL` still reads as
  `unmet` — severity does not soften a verdict, exactly as Checkpoint B case 2
  states.
- **never** reads a bound rule's `owner_role` to fill a missing
  `overlay.team_mapping` entry (§7).

---

## 4. What one assessment records

**Answer.** An assessment record carries the following. Every field is either
a citation of an existing frozen identity or a runtime fact about this one
assessment; none is written back into a Pack or an Overlay.

### 4.1 Request and provenance

- `project_id`; `pack_id`; `pack_version` (must equal the Overlay's pin —
  §7); `pack_schema_version` of the composed Pack; `direction_id`;
- the requested `activity_ids[]` (each `pack_id::activity_id`);
- the assessed scope exactly as declared (§2.1);
- the model-version context exactly as declared (§2.2), including the
  handover event;
- the cited `validation_run_id`, `ruleset_id`, and `ruleset_version` the
  bindings resolved against (§3.3 of ADR 0002: `requirement_key` proves the
  row was found, `ruleset_id` + `ruleset_version` prove it still means what
  the binding assumed);
- `assessment_digest` (§5) — a digest of this whole completed record, request
  and resolved result together, not of the request alone; logically the last
  thing written.

### 4.2 Per activity, per subscope

Everything in §3.3: `members`, `path`, `verdict`, `resolution_kind`, the
resolved `resolution_routes[]` chain, the evidence citations and
named-absence markers.

### 4.3 The resolving assignment (Checkpoint B §5 rows 8a–8d)

For every non-`READY` subscope, recorded in one direction only:

- `default_role` — from the Pack's `resolution_routes[]` row for the
  subscope's `resolution_kind` (row 8a, a Pack default);
- `assigned_team_or_person` — `default_role` mapped through
  `overlay.team_mapping[]` (row 8c, this assessment's assignment). If no
  `team_mapping` row names `default_role`, the request **fails closed** for
  that activity (§7); the record is not written with a partial assignment,
  and the bare `default_role` string is never recorded as though it were an
  assignee (ADR 0002 §3.5).
- `actual_actor` — an execution fact, recorded **in addition to**
  `assigned_team_or_person` if and when someone acts (row 8d), never instead
  of it. Its absence is the legible state "assigned, not yet started".

### 4.4 A `CONDITIONAL` promotion

`CONDITIONAL` is never a decision-tree leaf (ADR 0002 §3.8 forbids it
structurally). It exists only as a **promotion** of one subscope's `BLOCKED`
or `UNKNOWN` result, for one assessment, and the promotion record must carry
**all nine** fields ADR 0002 §3.8 and its Consequences enumerate:

1. the promoted subscope's **original verdict** (`BLOCKED` or `UNKNOWN`);
2. its **`resolution_kind`**;
3. the **underlying evidence gap or blocker** the leaf named (the `path`'s
   terminal outcome and the affected `members`);
4. a **named authoriser** — the actual person;
5. the **Overlay authorisation role** that authoriser acted under — the
   specific `may_authorise_roles` entry from the `overlay.risk_authorisations[]`
   row whose `{pack_id, resolution_kind}` matches this subscope exactly. A
   promotion citing a role **not** listed for this exact
   `pack_id::resolution_kind` is not a `CONDITIONAL` — it is an unauthorised
   release, and the assessment refuses to record it as `CONDITIONAL` (§7);
6. the **named model versions** the promotion applies to (from the
   model-version context);
7. the **accepted risk**;
8. the **release scope** — a named scope, which may be the subscope or
   narrower, never wider, and never defaulted to the assessed scope (§2.1);
9. the **voiding / failure condition** that would end the release.

The promotion is **additive, never substitutive**: the subscope's original
`verdict`, `resolution_kind`, and underlying blocker or gap remain in the
record unchanged, with the `CONDITIONAL` layered on top. `CONDITIONAL` never
becomes `READY` and never erases the deficiency it was promoted from — it
records that a named person accepted a named risk against a named scope, not
that the evidence changed (ADR 0002 §1, Checkpoint B §1). A `CONDITIONAL`
release with no recorded blocker or gap beneath it would be indistinguishable
from a fabricated `READY`, and is not a state this shape can express.

### 4.5 Exit / recheck status

- The `recheck_condition` for every non-`READY` subscope, copied from the
  pinned Pack's route (so a later reader is not renegotiating it —
  Checkpoint B §5 item 9);
- for a recheck assessment: the prior **record's** `assessment_digest` +
  activity + subscope ordinal it re-examines, and whether that subscope's
  `recheck_condition` is now met **and** the model-version context is still
  current (§2.3). A recheck is a new record with its own `assessment_digest`
  (§5); the prior record is unchanged.

**A recheck does not inherit a prior record's `CONDITIONAL` promotion
(D-4).** A `CONDITIONAL` is a record that a named person accepted a named
risk against a named scope *at one point in time* (ADR 0002 §3.8; §1
invariant 6). On a recheck — even against the identical model-version
context — if the deficiency has cleared, the subscope reaches `READY` /
`BLOCKED` / `UNKNOWN` on its own current evidence and no `CONDITIONAL` is
written. If the deficiency persists and the release is to continue, the
recheck record must carry its **own** `CONDITIONAL` promotion, with a current
authoriser, the currently accepted risk, and the still-applicable voiding
condition re-stated — never carried forward silently. Letting an acceptance
roll over untouched would let it outlive the authoriser's knowledge of the
current state, one step removed from the "knowing a risk exists is not the
same as someone having accepted it" trap Checkpoint B §1 names.

### 4.6 Consequence magnitude is cited, never computed

A `resolution_routes[]` row names the consequence **kind**. Its **magnitude**
— money, duration, effort — is `overlay.cost_parameters` plus the project's
milestone dates, both of which the record *cites*; the assessment computes no
new cost, duration, or temporal fact and fabricates none (Checkpoint B §3,
repeatedly: "no magnitudes").

---

## 5. Runtime identity: what is minted, what is forbidden

**Answer (does it mint identity).** A runtime assessment mints **exactly
one** identifier — here called `assessment_digest`; the final name is
Checkpoint D's to choose — and mints nothing else. Subscopes are referenced
by ordinal within a record (§3.3), not by a minted key; no `AssessmentRun`
id, verdict id, subscope id, or promotion id is created. Naming a tidy
runtime object here is exactly the mistake `Agent-product-manager.md` warns
against.

**Answer (what it identifies — the completed record, not the request).** The
technical-director review (D-2) is right that a digest used to reference one
prior record must identify *that record*, not the request that could produce
many. After an alignment determination is performed, the models, the
ruleset, the `as_of`, the `validation_run_id`, and the request are all
unchanged, yet the subscope's verdict moves from `UNKNOWN` to `READY` — two
records a request-only digest could not tell apart, though §3.3 and §4.5 use
the digest precisely to tell them apart. So `assessment_digest` is a
**deterministic hash of the fully resolved assessment record**, computed once
the record is complete, over its canonically-ordered content:

- the request and provenance of §4.1 — `pack_id`, `pack_version`,
  `pack_schema_version`, `direction_id`, the sorted `activity_ids[]`, the
  sorted assessed-scope keys, the model-version context (both `model_key`s,
  both content identifiers, the handover event fields), and the **cited**
  `ruleset_id`, `ruleset_version`, `validation_run_id`;
- the resolved result — for every requested activity, the ordered
  observation subjects, and every subscope's `path` (with its per-subject and
  `whole-scope` readings, each carrying its cited `finding_key`s /
  determination references / named-absence markers), `verdict`,
  `resolution_kind`, resolved route, and assignment;
- any `CONDITIONAL` promotion (§4.4), with all nine of its fields;
- for a recheck, the prior record's `assessment_digest` it re-examines
  (§4.5) — already final, so no cycle.

It changes whenever the evidence read or a verdict reached changes — which is
exactly when §3.3 and §4.5 need a different handle — and is identical for two
byte-identical records (§8, determinism paragraph).

**Answer (constraints, unchanged in force).** `assessment_digest`:

- **Parsed, sorted structure only — never raw bytes.** It hashes the
  resolved record after parsing and total ordering — the discipline
  `build_ruleset_normalized_digest` (`identity.py:109`) already applies and
  ADR 0002 §4 pre-commits any future Pack/Overlay content identity to. It
  never hashes TOML or CSV file bytes, file names, mtimes, or filesystem
  ordering, and it reads no clock (`AGENTS.md` rule 1).
- **Never an input to frozen identity.** It is never fed into
  `validation_run_id` (`identity.py:167`, six inputs — none a Pack, Overlay,
  or assessment value), `requirement_key` (`identity.py:99`, `rule_id` +
  `requirement_id` only), `finding_key`, `ruleset_normalized_digest`,
  `issue_key`, `group_ref`, any legacy identity, `contract-1.6.json`, or
  anything under `data/processed/`, `reports/`, or `ids/`. The dependency is
  one-way: the record cites those; none of them cites the record. That the
  digest now also covers cited `finding_key`s and determination outcomes
  does not change this — a cited value flowing *into* the digest never makes
  the digest flow *out* into what it cited.
- **Confined to the record.** It appears only in the assessment record and in
  the recheck references between records (§4.5). It is never exported,
  snapshotted, or joined against a published CSV.

A subscope-level digest is not minted; the ordinal (§3.3) is the within-record
handle. If one were ever added it would obey every rule above and stay inside
the record.

---

## 6. Several subscopes of one activity with different verdicts

**Answer.** They are **not rolled up into one verdict.** The
*(activity × requested assessed scope × model-version context)* result is
presented as the **ordered set of `(subscope ordinal → verdict)` pairs** from
§3.3. Each subscope is itself an outcome-homogeneous assessed scope with
exactly one verdict, so:

- Framework **invariant 1** holds for every
  *(activity × subscope × model-version context)* triple — the granularity
  invariant 1 actually ranges over. ADR 0002 §3.2's worked illustration says
  so directly: "Two subscopes, two verdicts, each satisfying Framework
  invariant 1 … for its own scope."
- A **heterogeneous requested assessed scope has no single verdict**, and
  this is a design decision with its own reasons, not a limit forced by ADR
  0002:
  1. Invariant 1 attaches a verdict to an outcome-homogeneous
     *(activity × scope × model-version)* cell. A heterogeneous requested
     scope is not one cell; its subscopes are. An authoritative single
     verdict for the heterogeneous scope would be a **new Framework
     object** — "the verdict of a scope whose own evidence disagrees" —
     needing its own semantics (what does `BLOCKED` beside `UNKNOWN` beside
     `READY` reduce to?), its own invariants, and its own place in the
     four-state vocabulary. That vocabulary is the Framework's, owned by
     Checkpoint B and ADR 0002 §1; this checkpoint's scope explicitly
     excludes changing it.
  2. Any reduced value also **discards what the partition is for**: which
     subjects are `BLOCKED` under which `resolution_kind`, which are only
     `UNKNOWN`, which are `READY` and could proceed now. Checkpoint B §1 ("a
     single 'is the MEP model good?' verdict would be useless here") is the
     whole argument that the partial answer is the useful one; a roll-up
     re-collapses precisely what the partition exists to hold apart.
  3. ADR 0002 §3.2 left an activity-level roll-up "to Checkpoint D … if ever
     needed". This document finds it is not needed and declines to mint the
     Framework object it would require. Asking "the verdict of the whole
     requested scope" returns the partition.
- When the partition is trivial (one part — the live case throughout ADR
  0002 §6), there is exactly one subscope = the whole assessed scope = one
  verdict, and presentation is identical to an un-partitioned assessment.

**A non-authoritative human summary** may be shown alongside the partition —
counts per verdict class, the most severe class present. It is a rendering
*of* the partition: it states nothing the partition does not already state,
carries no verdict of its own, is never stored as one, and is never an input
to the resolving assignment (§4.3), a `CONDITIONAL` promotion (§4.4), a
recheck (§4.5), or anything downstream. Summarising verdict classes across
subscopes is a different act from selecting a named outcome inside one
evidence requirement — the latter is what ADR 0002 §3.2 forbids, and this
summary does not do it. There is no authoritative activity-level verdict
above the subscope.

---

## 7. Every missing input fails closed — mapped to ADR 0002 §3.7

**Answer.** Two failure kinds, kept distinct exactly as ADR 0002 §3.2 draws
the line:

- a **composition / request defect** — a binding, method, role,
  authorisation row, or Pack reference that does not exist — is caught
  **before any subscope is assessed**, and the assessment **refuses** (no
  record with a partial verdict is written);
- an **unresolved outcome** — a binding that exists but has produced no
  admissible result for *this* assessment yet — is **not** a failure: it is
  the `not-yet-evaluated` / `not-yet-confirmed` / `not-yet-determined`
  outcome, which the decision tree turns into an `UNKNOWN` leaf carrying a
  `gap_kind`, resolved through `resolution_routes[]` to a role, a
  consequence, a next action, and a recheck.

No case below resolves by picking a default, taking the first match in an
unordered collection, or reading anything time-dependent (`AGENTS.md` rule 1;
ADR 0002 §3.7 closing paragraph).

### 7.1 Composition / request defects — the assessment refuses

| Missing / wrong input | Assessment behaviour | ADR 0002 §3.7 row |
|---|---|---|
| Request names a `pack_id` the project's `overlay.packs[]` does not list | Refuse this request only; contract 1.6 pipeline and every other activity/Pack unaffected | "A purpose assessment is explicitly requested for a `pack_id` the project's Overlay does not list under `overlay.packs[]`" |
| Project's `project.toml` has no `[overlay]` table | Refuse this request only; the project simply has no purpose assessment available; `epc-ct run/check/group`/exporters unaffected | "A project's `project.toml` has no `[overlay]` table at all" |
| `pack_version` in the request (or the Overlay pin) ≠ the composed Pack's declared `pack_version` | Refuse — exact match only, never a range | "`overlay.packs[].pack_version` does not match the named Pack's declared `pack_version`" |
| Composed Pack's `pack_schema_version` is not one the (future) loader implements | Composition already failed closed; the assessment has no Pack to walk and refuses | "A Pack's `pack_schema_version` is not one a future loader implements" |
| A resolved binding's `{ruleset_id, ruleset_version}` ≠ the ruleset the cited `validation_run_id` was computed over | Refuse — the assessment may not attribute facts from one ruleset version to a binding pinned to another (§2.3; ADR 0002 §3.3, §3.4c) | "A `pack_binding` or an Overlay `evidence_bindings[]` row names a `{ruleset_id, ruleset_version}` that does not match the ruleset actually loaded" |
| A binding's `requirement_keys[]` contains a key absent from that ruleset | Refuse | "A binding's `requirement_keys[]` contains a key absent from the loaded, matching-version ruleset" |
| A requested activity's evidence requirement has `binding_source = "overlay"` and no `overlay.evidence_bindings[]` row names the same `pack_id` + `evidence_requirement_id` (the R-005 case) | Refuse for any activity that needs it — **never** fall back to R-005 or any rule's `owner_role`; there is no default because the Pack does not know R-005 exists | "An evidence requirement declares `binding_source = "overlay"` and the project's Overlay has no `evidence_bindings[]` entry naming the same `pack_id` + `evidence_requirement_id`" |
| A requested activity's evidence requirement has `binding_source = "assessment"` and no matching `overlay.accepted_evidence_methods[]` row | Refuse for that activity | "An evidence requirement declares `binding_source = "assessment"` and the Overlay has no matching `accepted_evidence_methods[]` entry" |
| A requested activity has a reachable non-`READY` leaf whose `resolution_routes[].default_role` has no `overlay.team_mapping[]` row | Refuse this request only; contract 1.6 pipeline and any fully-bound activity unaffected; never read the bound rule's `owner_role`; never record the bare `default_role` string as an assignment | "A purpose assessment is requested for an activity whose reachable non-`READY` leaves name a default role with no matching `overlay.team_mapping[]` entry" |
| The request omits the assessed scope | Refuse — scope is a required input, never defaulted to "whatever has findings" (§2.1) | (new to this checkpoint; consistent with ADR 0002 §3.2's coverage-is-not-scope rule and `AGENTS.md`'s "worst outcome available" principle) |
| No `validation_run_id` exists for the project / the model versions in the context, or the cited run did not validate those versions | Refuse — there are no validated facts the assessment may honestly cite (§2.3) | (new to this checkpoint; the assessment reads post-`check` facts and cannot run without them) |
| Any Pack-load structural invariant fails (dangling node, cycle, uncovered `outcome`, `CONDITIONAL` leaf, orphaned/duplicate `resolution_kind`, out-of-scope `next_node`, `renders_inapplicable` violation, unresolved `direction_id`, …) | Composition already failed closed at Pack load; the assessment has no valid tree and refuses | the fifteen Pack-load rows and the `resolution_routes[]` / `directions[]` / `decision_nodes[]` rows of ADR 0002 §3.7 |

### 7.2 `CONDITIONAL` promotion defects — the promotion refuses, the leaf stands

| Missing / wrong input | Assessment behaviour | ADR 0002 §3.7 row |
|---|---|---|
| A `CONDITIONAL` promotion is attempted for a `resolution_kind` with no `overlay.risk_authorisations[]` row for that `pack_id` | Refuse the promotion only; the subscope's verdict stays `BLOCKED`/`UNKNOWN`; `CONDITIONAL` is simply unavailable for that `resolution_kind` in this project — never a default authoriser, never `resolution_routes[].default_role` standing in | "A `CONDITIONAL` promotion is attempted for a `resolution_kind` with no matching `overlay.risk_authorisations[]` entry" |
| The promotion cites an authoriser role not in `may_authorise_roles` for that exact `pack_id::resolution_kind` | Refuse to record it as `CONDITIONAL` — it is an unauthorised release, not a promotion | ADR 0002 §3.8: "a promotion citing a role not listed for this `resolution_kind` is not a `CONDITIONAL`, it is an unauthorised release" |
| The promotion omits any of the nine §4.4 fields | Refuse — an additive promotion that cannot name its original verdict, blocker/gap, authoriser, role, versions, risk, release scope, and voiding condition is indistinguishable from a fabricated `READY` | ADR 0002 §3.8 promotion field list; §1 invariant 6 |
| `overlay.risk_authorisations[].may_authorise_roles` is empty or contains a wildcard / `"all"` | Composition already failed closed; no promotion is possible | "An `overlay.risk_authorisations[].may_authorise_roles` is empty, or contains a wildcard, `"all"`, or any similarly unbounded value" |

### 7.3 Unresolved outcomes — not failures, routed as `UNKNOWN`

| Situation | Assessment behaviour | Basis |
|---|---|---|
| A validation-backed reading (subject × bound `requirement_key`) has **no finding at all** (an absent finding — the chimney; or `check` has not evaluated this handover) | The subject reads `not-yet-evaluated` for that evidence requirement; its subscope reaches the `UNKNOWN` leaf carrying the `gap_kind`; the named absence is recorded (§3.3, §4.2) | ADR 0002 §3.2: "`not-yet-evaluated` … describe a binding that exists but has not yet produced an admissible result … never a missing binding" |
| An assessment-bound evidence requirement has a method in the Overlay but **no recorded determination** for these model versions yet | Unit reads `not-yet-confirmed` / `not-yet-determined`; subscope reaches the `UNKNOWN` leaf with its `gap_kind` | ADR 0002 §3.2; the `no-penetration` vs `not-yet-determined` distinction |
| An R-010 `PASS` exists but no accepted `cross-model-alignment` method has produced a determination | `cross-model-alignment` stays `not-yet-confirmed`; the R-010 `PASS` is recorded as context only and never read as any of the three outcomes | ADR 0002 §3.2 `insufficient_evidence[]` entry: "a `PASS` is not alignment evidence" |
| A subgroup's subjects disagree on the named outcome at a node | Split into outcome-homogeneous child subgroups (§3.2) — not a failure, and never collapsed by priority | ADR 0002 §3.2 partitioning rule |

### 7.4 Not errors — the pipeline is untouched

| Situation | Assessment behaviour | ADR 0002 §3.7 row |
|---|---|---|
| Two different Packs bound by one project reuse a local `activity_id` / `evidence_requirement_id` / `direction_id` | Not an error — the unique reference is the compound `pack_id::…`; the assessment addresses activities by compound key throughout | "Two different Packs used by one project's Overlay declare the same local `activity_id` or `evidence_requirement_id`" |
| A project has an `[overlay]` but the assessment is never requested | Nothing runs; `epc-ct run/check/group`/exporters/snapshot unaffected | "A project's `project.toml` has no `[overlay]` table at all" / §3.7 closing rows |

---

## 8. Determinism and the changed-input acceptance commitments

The assessment step is bound by `AGENTS.md` rule 1: every subscope is an
equivalence class over a total order of frozen string keys; every §7 check is
a lookup or a membership test; `assessment_digest` hashes resolved sorted
structure; no `datetime.now()`, no unordered iteration, no machine-dependent
path. Two assessments of the same request against the same validated facts
produce byte-identical records.

**The four ADR 0002 §4 changed-input counterfactuals apply in full, with no
exemption, and are restated here as this design's acceptance commitments — a
future Checkpoint D implementation is judged against them:**

1. **Change only a Purpose** — edit a Pack's `evidence_requirements`,
   `decision_nodes`, `directions[]`, or `resolution_routes[]`; touch no
   project. `git diff --exit-code -- data/processed reports` passes; `epc-ct
   snapshot` reports no drift; every `validation_run_id`, `requirement_key`,
   and `finding_key` in `data/processed/canonical/` is byte-identical;
   `contract-1.6.json`'s file list and SHA-256s are unchanged.
2. **Change only an Overlay** — edit `pcert-sample`'s `[overlay]` table
   (`evidence_bindings`, `team_mapping`, `risk_authorisations`,
   `cost_parameters`, `conventions`); touch no model, ruleset, or programme.
   Identical to (1), for **the entire published output tree of both
   projects** — nothing in the pipeline reads `[overlay]`.
3. **Add a second Pack** — a new file under `purpose-packs/`, referenced by no
   project. Identical to (1) — an unreferenced Pack must appear in no
   published artifact, count, or manifest.
4. **Add an `[overlay]` to the existing `iso-reference-view` project** —
   binding it to a Pack; add no new project directory, model file, ruleset,
   or programme change. Identical to (1) and (2) — the entire published
   output tree for **both** projects is byte-identical, with **no exception
   for the edited project's own rows**.

**This checkpoint adds two commitments of the same kind:**

5. **Run an assessment, store an assessment record, or promote a
   `CONDITIONAL`** — for any project, any Pack, any request. Identical to (1):
   the assessment record lives outside `data/processed/`, `reports/`, `ids/`,
   and the contract snapshot; `epc-ct run`, `check`, `group`, every exporter,
   the snapshot, and both `Legacy…` writers never read it; every published
   byte, count, and SHA-256 is unchanged, and `epc-ct snapshot` reports no
   drift.
6. **Mint or change an `assessment_digest`** — by any change to the request,
   the Pack version, the cited run, the evidence read, or a verdict reached
   (§5: the digest is over the whole resolved record). No `validation_run_id`,
   `requirement_key`, `finding_key`, `issue_key`, `group_ref`,
   `ruleset_normalized_digest`, legacy identity, or `contract-1.6.json` value
   moves, because none of them takes an assessment value as input
   (`identity.py:99`, `:109`, `:167`; §5).

What a future test plan must diff is exactly ADR 0002 §4's list — the full
set of `requirement_key`, `finding_key`, `issue_key`, and `validation_run_id`
in `data/processed/canonical/{requirements,findings,issues}.csv`; every
published CSV's row count; every file's byte count and SHA-256 under
`data/processed/` and `reports/`; and `contract-1.6.json`'s recorded file
list — all unchanged under every one of the six counterfactuals above.

---

## 9. Explicitly out of scope for this document

No evaluator that walks a decision tree, resolves a binding, or reduces a
reading is implemented. No Pack/Overlay loader and no
fail-closed *composition* logic is implemented — that is the next route item;
§7 fixes only how the assessment step behaves when handed an incomplete
composed input. No `AssessmentRun`, `AssessmentItem`, `EvidenceGap`,
`BlockerCandidate`, `Subscope`, or promotion object is created or named as
approved; `assessment_digest` is the one identifier this document
contemplates, and only under the §5 constraints. No project override
capability is implemented or assumed — ADR 0002 §3.6 defers the entire
mechanism, and this document designs around no such capability existing. No
machine contract, CLI, BIM Doctor experience, second Purpose Pack, or
Registry is designed. No code, rule, checker, test, README, CHANGELOG,
contract, `identity.py` derivation, `rules/` file, `projects/` file,
`data/processed/` artifact, `reports/` artifact, `ids/` document, or Pack /
Overlay example file is added or modified. `data/processed/`, `reports/`, any
snapshot, and contract 1.6 are untouched. Nothing is merged, tagged, or
released. Implementation of Checkpoint D is not started.

## Consequences

This document commits a future Checkpoint D implementation to: a
**demand-driven, unregistered, read-only** assessment operation that
consumes post-`check` / pre-`group` validated facts and a composed
Pack/Overlay, and writes one assessment record outside every published-
contract path; an **assessed scope that is a required, explicit request
input** — an ordered set of `element_key`/`model_key` values resolved
against, and paired with, an explicit **model-version context**, together
forming one Framework-invariant-1 cell, never inferred from which findings
exist and never owned by Pack, Overlay, or direction; **subscopes constructed
as equivalence classes of observation subjects** — the existing keys a
subscope is a set of — **split incrementally down the decision tree** (never
an up-front cross-product), with each evidence requirement's readings hung on
the subjects at its declared grain (`per-subject` or `whole-scope`),
identified by ordinal within a record, and recorded with the carrier
(`members`) and the per-node readings kept separate; an assessment record
that **cites** frozen identities and is cited by none; **exactly one minted
identifier, `assessment_digest`**, a deterministic hash of the whole resolved
assessment record (request, evidence readings, verdicts, any promotion) —
never of raw bytes, never an input to `validation_run_id` / `requirement_key`
/ `finding_key` or any published-contract value; a **`CONDITIONAL` that
exists only as an additive promotion** carrying all nine ADR 0002 §3.8
fields, refusing to record without an authoriser role listed for the exact
`pack_id::resolution_kind`, never becoming `READY` or erasing its deficiency,
and **never inherited by a recheck** — a continued release is re-authorised
in the recheck record or it lapses; **no roll-up above the subscope** — a
heterogeneous assessed scope is presented as its partition of
`(subscope → verdict)` pairs, each satisfying invariant 1 for its own scope,
the decision not to define an activity-level verdict being this checkpoint's
to make (ADR 0002 §3.2), with only a non-authoritative human summary
permitted alongside; **every missing binding, method, role, or authorisation
failing closed** per §7, mapped row-by-row to ADR 0002 §3.7, with a missing
*binding* refusing the request and a missing *result* routed as `UNKNOWN`;
and **the six changed-input counterfactuals in §8 — the four
from ADR 0002 §4 with no exemption, plus running an assessment and minting an
`assessment_digest` — as the acceptance test for Checkpoint D's identity and
determinism claims.** It commits nothing about how the tree is evaluated in
code, how the composed Pack/Overlay is loaded, where a record is stored, or
when Checkpoint D begins — those remain open, and deliberately so.
