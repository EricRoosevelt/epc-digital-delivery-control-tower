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
- **Revision history:**
  - Refines the version at `954fee6` (2026-09-03), which **BIM domain review
    returned AT RISK** on the composed Checkpoint C + D design, for four
    reasons, all four re-checked against `data/processed/canonical/` and
    against Checkpoint B's text before being accepted. Two of the four are
    Checkpoint C data-shape questions and are closed in
    [`0002-minimal-purpose-pack-project-overlay.md`](0002-minimal-purpose-pack-project-overlay.md)
    (E-1, resolving roles; E-2's Pack fields); this document takes their
    runtime consequences and closes three further items of its own. **E-2** —
    `opening-status` read exactly one outcome per penetrating element, so a
    chimney needing a slab opening and a roof opening in different states, and
    a shared shaft opening serving several MEP lines, were both
    inexpressible; the grain is now Pack-declared and `opening-status` reads
    at a *(penetrating element, penetrated architectural element)* pair, both
    members of which exist whenever the pair does, so D-1's no-phantom-key rule
    is satisfied rather than relaxed. **E-3** — §2.1/§3.1 expanded a
    `model_key` in scope to every element of that model and handed all of them
    to every requested activity, which made `pcert-sample`'s two
    `IfcBuildingElementProxy` setout markers subjects of the ceiling activity
    and produced an `UNKNOWN` about a survey marker; subjects are now admitted
    by the activity's declared `subject_classes`, never by which elements carry
    findings, and every excluded key is recorded per activity so nothing in a
    declared scope disappears. **E-4 supersedes D-4, at the technical
    director's direction**: a `CONDITIONAL` promotion now continues with the
    record while its own voiding condition **remains unmet** and the
    model-version context is unchanged, and lapses — recorded, never
    silently — on any change; §4.5
    states why, and states that the rule is negotiable in a later product
    round. **E-5** — the document defined only a `recheck` successor, and the
    real sequence is an `UNKNOWN` record signed off in the coordination review
    that reads it; §4.5 adds the `authorisation` successor kind, whose claim
    of unchanged evidence is proved by re-derivation rather than asserted, and
    fixes that a record is sealed once its `assessment_digest` is computed and
    is never rewritten. Accepted unchanged and carried forward: the pipeline
    position and input/output boundary, the subject/reading/grain trichotomy,
    the within-subject-only `FAIL` precedence, `BLOCKED`/`UNKNOWN` as distinct
    states, `CONDITIONAL` as additive-never-substitutive, R-010's `PASS` as
    `insufficient_evidence[]` context only, no roll-up above the subscope, the
    §7 fail-closed map (added to, never altered), the six §8 counterfactuals,
    and the one-way identity dependency.
  - Refines the version at `849a55c` (2026-09-03), which **product audit
    returned AT RISK** on one remaining item. The continuation policy itself
    was approved — a `CONDITIONAL` promotion re-authorised on substantial
    change rather than on every query — and what was not approved was that the
    policy, as written, could not be *proved*: §4.5 said a promotion continues
    while its voiding condition remains unmet without saying how anyone knows
    that, which left it satisfiable either by an evaluator forming its own
    opinion of a prose condition or by nobody forming one at all and the
    release carrying on unmentioned. **E-6** closes it. A continuation is now
    written only when four things are proved on the record that carries it: a
    recorded, attributable **voiding-condition determination** reading `unmet`;
    an unchanged model-version context; the promotion's cited authorisation
    role **still listed** in the Overlay composed for this record — a check
    that was genuinely absent, so an Overlay that dropped a role would have
    gone on carrying releases authorised under it; and coverage not widened.
    The assessment never interprets field 9 itself — it cites a determination
    about it, the same discipline §1.2 item 4 already fixes for
    `accepted_evidence_methods[]` outputs. No determination, an
    `undeterminable` determination, and a `met` determination are three
    distinct states, none of them continuing, each recorded with its reason;
    and every successor record must state exactly one of continuation, lapse
    with reason, or no-longer-applicable, so that silence neither continues a
    release nor ends one. §7.2 gains six rows, adding to the fail-closed map
    and altering none of it. Two lines that read against §4.5's own body —
    "while its own voiding condition holds", in this revision history and in
    the Consequences — are corrected to "remains unmet"; §4.5's rule keeps its
    wording. This round also records three product decisions once each: the
    `subject_classes` matching rule in
    [`0002`](0002-minimal-purpose-pack-project-overlay.md) §3.2 where the field
    is defined; the per-activity object-scope test obligation as §8's seventh
    acceptance commitment, which leaves §8's six counterfactuals exactly six;
    and the independence of the resolving assignment from the authorisation in
    §4.4, including that this document does not require them to be different
    people and that separation of duties is recorded as not implemented.
    Unchanged: the continuation policy, the four non-relaxations, the
    `subject_classes` class-data semantics, the pair grain and invariants
    16–18, the decision tree and the ten routes' correspondence with the ten
    non-`READY` leaves, the six §8 counterfactuals, sealing, and the two
    successor kinds. No Pack, loader, or runtime is implemented.
  - Refines the version at `d290245` (2026-09-04), which technical-director
    review returned **CONDITIONAL** — E-6's substance accepted in full (the
    four proofs and their table, the three non-`unmet` states each lapsing with
    a recorded reason, the exactly-one-of-three rule against silence, and the
    newly added check 3 on the authorisation role) — for **one** item, **D-5**:
    the voiding-condition determination's fourth field, "the
    `assessment_digest` of the record that carries it", was not computable.
    Under §5's own enumeration that digest covered all four fields, so the
    fourth was an input to the value it named; and it could not be re-read as
    pointing at an earlier record either, since a promotion has nothing to
    determine when it is granted, the moment needing a determination is the
    continuation itself, and §4.5 admits exactly two successor kinds with no
    third whose job is to carry one. The review also found the document saying
    two incompatible things about where a determination lives: §4.5 check 1
    called it "cited by reference" (§1.2 item 4's external model) while §5 and
    §7.2 treated it as record-internal content. **The external model is
    adopted**, because it is what every other determination in this design
    already does and what E-6 asked for: a determination is produced outside
    the assessment, carries its own reference identity, and the record cites
    that reference and records the outcome read — nothing about a record is an
    input to a determination it cites, so the fixed point is gone. The fourth
    field becomes **which promotion the determination judges** — the *sealed*
    prior record's `assessment_digest`, activity and subscope ordinal, plus the
    model-version context — which is computable at the only moment it is
    needed, since that record was sealed before any continuation of it could be
    attempted. Field 4 names the record in which the promotion was **granted**,
    not the immediately preceding one, so a promotion continued more than once
    has one stable anchor for every determination along the chain; a
    continuation therefore records the promotion's **origin reference**
    alongside §4.1's successor reference, as continuation bookkeeping and not
    as a tenth promotion field — §4.4's nine are still nine and still all
    restated. "Missing attribution is not a determination, and lapses" is
    preserved and widened: an unresolvable reference, a missing determiner,
    basis or outcome, **or** a determination naming a different promotion or
    context is read as the absent state and lapses. §5's enumeration now covers
    the reference and the outcome rather than four fields, §7.2's attribution
    row is corrected and one row is added for a determination that names
    another promotion or context, and §1.2 item 4 names the voiding-condition
    determination alongside the three `accepted_evidence_methods[]` outputs,
    noting the one respect in which it differs — no Pack or Overlay declares a
    method for it, because which role may make one is deliberately not fixed.
    One consequence is stated rather than left implicit: because field 4 pins a
    determination to one promotion and one context, **one determination may
    support more than one continuation** while both still hold, which is
    deliberate — requiring a fresh one per record would put the determiner's
    signature back on the per-query footing E-4 removed. Unchanged: the four
    proofs and their table, the three non-`unmet` states, the
    exactly-one-of-three rule, check 3, sealing, the two successor kinds, §8's
    six counterfactuals and its seventh commitment, and the recording places of
    the three product decisions.
  - Supersedes the version at `e2126fd` (2026-09-04), which **BIM domain review
    returned AT RISK** on three counts and technical-director review
    **REJECTED**. E-6 and D-5's results stand and are not reopened —
    determinations external and read by reference, the fourth field anchored to
    the granting record, the origin reference along a chain, check 3, the three
    non-`unmet` states, the four requisites of a determination, the silence
    rule, the corrected "remains unmet" wording, and the recording places of the
    three product decisions. What was violated is a premise none of the four
    proofs constrained: **a promotion accepts one named risk of one named
    kind** — field 7 read through field 2 — and a continuation that compares
    only identities and cites one prose determination cannot notice that the
    accepted risk has become a *different* risk. **E-7** closes it in three
    parts.
    **(a)** A continuation now requires the currently re-derived
    `resolution_kind` to be the promotion's field 2 (check 5); a different kind
    lapses the promotion, recorded as the risk having changed kind and
    explicitly **not** as "no longer applicable", since the deficiency did not
    clear but became another one. This Pack contains the case: `misaligned` and
    `not-yet-confirmed` hang on the same `cross-model-alignment-node`,
    performing the alignment check edits no model so no content identifier
    moves, and ADR 0002 §3.5's worked Overlay authorises nobody for
    `cross-model-misalignment` — so under the old four checks the release
    continued, and now it stops at a lapse that §7.2's first row will not let
    anyone re-authorise in that project. It is also stated which kind check 3
    tests — the promotion's field 2 — an ambiguity that was itself what hid the
    hole.
    **(b)** A determination is now decisive rather than merely citable. Every
    admissible determination naming the promotion's origin reference and the
    context is enumerated and cited, and the outcome is the **maximum** of that
    set under the fixed order `met` > `undeterminable` > `unmet` — a maximum
    over a set rather than a pick, so no clock is read and the result does not
    depend on which determination a record cited; a store that cannot be
    enumerated exhaustively cannot prove check 1. A **lapse is terminal** for
    the promotion it ends: no later record may continue it, and re-releasing
    requires a new promotion with all nine fields. And the silence rule's
    trigger moves from "the cited record carried a promotion" to "this
    subscope's **promotion chain is non-empty**", which closes the hole where
    the record that lapses a promotion neither grants nor continues one, so
    every record after it fell silent about it.
    **(c)** `pack_version` joins the preconditions (check 6): an Overlay pins it
    by exact match so a bump is a deliberate edit, and across one the same
    `resolution_kind` may carry a different consequence set, role, next action
    and recheck condition. Ruleset identity is argued *not* to need its own
    check, because its material effect arrives through check 5.
    The claim that four checks were "the complete set of preconditions" is
    **retracted**. The seven are instead derived from the promotion's own nine
    fields, with a field-by-check table, and the two fields no design here can
    check — the named authoriser's continued willingness, and the accepted
    risk's magnitude — are named as uncheckable rather than assumed away.
    §7.2 gains six rows and changes none; two earlier rows are left
    byte-identical on purpose, with a note saying how to read them. Unchanged
    besides the above: sealing, the two successor kinds, §4.4's nine fields
    still nine, §8's six counterfactuals and its seventh commitment. No Pack,
    loader, or runtime is implemented.
  - Refines the version at `3cea316` (2026-09-04), which technical-director
    review returned **CONDITIONAL** — E-7a, E-7b and E-7c all accepted and not
    reopened (checks 5, 6 and 7, check 1's maximum over the enumerated
    determinations, the terminal lapse, the widened silence trigger, the
    nine-field derivation table's structure, and the honest statement of what
    cannot be checked) — for **one** item, **D-6**: the derivation table
    justified field 1 as covered "via 5" on the lemma that "each
    `resolution_kind` belongs to exactly one leaf (ADR 0002 §3.2)". **ADR 0002
    guarantees no such thing, and the citation pointed at a section saying
    something else.** What §3.2 fixes runs one way: every leaf's
    `failure_kind`/`gap_kind` matches *exactly one* route row, and every row is
    used by *at least one* leaf. At-most-one is never required — §3.2 states
    that "two leaves can only ever share a `resolution_kind` by sharing the
    identical route behind it", the Consequences record "reuse of one
    `resolution_kind` across leaves only ever meaning identical treatment", and
    §3.8 puts `failure_kind` and `gap_kind` in one shared namespace. So a legal
    Pack may carry one kind on a `BLOCKED` leaf and an `UNKNOWN` leaf at once,
    and a kind-only check 5 would pass while the verdict flipped from `UNKNOWN`
    to `BLOCKED` — E-7's own failure mode re-entering through the weakest row of
    the table meant to justify it. ADR 0002's worked Pack does not exercise it
    (ten routes, ten non-`READY` leaves, one-to-one), but both documents are
    general designs. **Check 5 is widened rather than a new invariant being
    imposed on Packs:** it now compares the re-derived **verdict**,
    **`resolution_kind`** and **terminal outcome** against the promotion's
    fields 1, 2 and 3 — three values the promotion already records — so it means
    "the leaf is the leaf that was authorised". The alternative, making
    "one kind, at most one leaf" an explicit precondition enforced by a
    nineteenth ADR 0002 §3.8 Pack-load invariant, is recorded as considered and
    declined: it narrows what Pack authors may write, in a merged document, to
    spare a continuation three comparisons against values it already holds. The
    derivation table's field 1, 3 and 7 rows are re-grounded accordingly — 1, 2
    and 3 each compared directly rather than inferred from one another, field 7
    pinned only as far as its kind is pinned — and field 7's prose statement
    joins field 4 and field 7's magnitude among the things named as uncheckable.
    §7.2 gains one row for a re-derived verdict or terminal outcome that is not
    the one authorised. The previous round's "add rows, change none" instruction
    is lifted for exactly two rows, which are brought into line with the text
    around them: the E-4 row's list of lapse causes and the E-6 silence row's
    count of proofs — neither rule changed, both rows had been left behind by
    later rounds — and the §7 paragraph explaining how to read the stale wording
    is deleted. No other §7.2 row is added, changed, or removed. Unchanged:
    checks 1–4, 6 and 7, determinations external with their four requisites, the
    origin reference, the terminal lapse, the silence rule, sealing, the two
    successor kinds, §4.4's nine fields, §8's six counterfactuals and its
    seventh commitment, and the recording places of the three product decisions.
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
    tree and its eighteen structural invariants, the ten `resolution_routes[]`,
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
| 4 | What one assessment records, including every field a `CONDITIONAL` promotion must carry, and the total accounting of the declared scope | §4, §3.3 |
| 4a | How a record is sealed, what a successor record is, and how a `CONDITIONAL` promotion continues, is proved to continue, or lapses across records | §4.5 |
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
   model element inventory **including each element's published `ifc_class`**
   (`elements.csv`), the project programme / milestone dates, and the
   `validation_run_id`, `ruleset_id`, and `ruleset_version` of that run.
   `ifc_class` is read for one purpose only — admitting an element as an
   observation subject of an activity whose `subject_classes` name that class
   (§3.1) — and is never read as a readiness signal, an applicability
   substitute, or a proxy for whether a rule reached the element.
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
4. **Recorded determinations** — the outputs of the
   `overlay.accepted_evidence_methods[]` methods (an alignment confirmation, a
   coordination-review determination, an opening cross-reference check), and
   the **voiding-condition determination** a `CONDITIONAL` continuation rests
   on (§4.5). These are runtime evidence; their production and storage are not
   designed here. The assessment reads them **by reference** and records which
   references it read, together with the outcome each one reported (§4). It
   adjudicates none of them: a determination is admitted or found
   inadmissible, never decided. The voiding-condition determination differs
   from the other three in one respect only — no Pack or Overlay declares a
   method for it, because which role may make one is deliberately not fixed
   (§4.5) — and in every other respect it is read exactly like them.

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

**The declared scope is one thing; which of its elements a given activity is
*about* is another, and the second is Pack data (closes E-3).** Expanding a
`model_key` and then handing every element to every requested activity was
the shape this design previously had, and `pcert-sample`'s own `hvac` model
shows what it produces: the two `IfcBuildingElementProxy` setout markers
`origin` and `geo-reference` — no storey, outside R-004's and R-005's
applicability, `geo-reference` with no finding of any kind — would become
subjects of the ceiling activity and yield an `UNKNOWN` *about a survey
marker*, routed to an action that extends the rule set until a setout marker
reports a storey. The verdict would be correct about the evidence and about
the wrong object.

Each requested activity therefore admits subjects from the declared scope by
the activity's own `subject_classes` (ADR 0002 §3.2), and by nothing else
(§3.1). Two properties of that rule matter more than the mechanism:

- **It is class data, never coverage data.** Admission never consults whether
  an element has a finding, an applicable requirement, or a binding. Letting
  coverage decide is the case-4 trap in a second costume: the `IfcChimney`
  `hvac::3dkFAzOGrAIuOzY_RdrdVv` produces **zero** findings, is admitted by
  every one of this Pack's three activities because it is an `IfcChimney`,
  and reaches the `not-yet-evaluated` reading it should. The two proxies are
  excluded because of what they *are*, not because of what the rules did or
  did not do to them.
- **Nothing declared silently disappears.** For every requested activity, every
  declared scope key is accounted for as either an admitted subject or an
  explicitly listed out-of-class key carrying the `ifc_class` that excluded it
  (§3.3). A key outside *every* requested activity's classes is therefore
  listed under every one of them; the request-level statement "this key was in
  your scope and no requested activity was about it" is a rendering of those
  per-activity lists, not a separate fact. A mistyped class name in a Pack
  surfaces here as elements the activity declined to be about — visibly — and
  never as a scope that quietly shrank.

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
  fresh assessment; a successor record (§4.5) re-confirms both that the
  underlying evidence still reads as before **and** that the context is still
  current, by comparing content identifiers — a value comparison, never a
  clock read. That same comparison is what an `authorisation` successor must
  pass identically, and what a continued `CONDITIONAL` promotion lapses on
  when it fails.
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

Three terms, kept distinct. The trichotomy is unchanged; what changed this
round is that **grain is now read from the Pack rather than assigned here**
(ADR 0002 §3.1, `evidence_requirements[].subject_grain`), and that a subject
may be a pair (closes E-2):

- An **observation subject** is the thing a subscope's membership is a *set
  of*, and the only thing that is split, ordered, and recorded as a
  subscope's members. It is always a key, or a tuple of keys, **every member
  of which actually exists**:
  - an `element_key`;
  - a **penetration pair** `(penetrating element_key, penetrated
    architectural element_key)` — the subject a `per-subject-pair` evidence
    requirement reads at (below);
  - or — for an activity whose every evidence requirement is `whole-scope` —
    the single model-pair subject `(producing model_key, consuming
    model_key)`.

  An activity's observation subjects are derived from the assessed scope
  (§2.1) in two declarative steps, in this order:

  1. **Class admission.** Each `element_key` the declared scope resolves to,
     against the producing model version, is admitted as a subject of this
     activity **iff** its published `ifc_class` is one of the activity's
     `subject_classes` (ADR 0002 §3.2), compared by exact string equality.
     Admission reads class and only class: never a finding, never a binding,
     never an applicability set. For `pcert-sample`'s `hvac` model and this
     Pack's three activities, that admits the duct, the two air terminals and
     the `IfcChimney` — including the chimney's **zero** findings, which is
     the entire point — and excludes the `origin` and `geo-reference`
     `IfcBuildingElementProxy` setout markers. An activity whose every
     evidence requirement is `whole-scope` declares no `subject_classes`,
     admits no element subject, and has the model-pair subject instead.
  2. **Refinement.** A subject is refined into finer subjects at, and only at,
     a node whose evidence requirement declares a finer grain than the
     subject currently carries (§3.2 step 2). In this Pack that happens
     exactly once: at `opening-status-node`, an admitted `element_key` whose
     `penetration-determination` reading was `penetration-confirmed` refines
     into one penetration pair per architectural element that determination
     named. Refinement never adds an element to the scope and never removes
     one: every refined subject carries the admitted `element_key` it came
     from, and that provenance is recorded (§3.3).

- A **reading** is one evidence requirement's outcome for one subject: the
  subject paired with one binding of that evidence requirement — a
  `requirement_key`, or an accepted `method_id` — reducing to exactly one of
  the evidence requirement's declared `outcomes[]`. A reading is what ADR
  0002 §3.2 calls an *atomic observation unit*; it is hung on a subject,
  never a subject itself. **A reading reduces to exactly one outcome, and
  this is why the pair grain was needed rather than a list-valued reading:** a
  reading holding two outcomes at once would put the disagreement inside the
  atom, where the partitioning rule has no carrier to split on.
- A **grain** is declared by the Pack on each evidence requirement and says
  how that requirement's readings key onto subjects:

| Grain (Pack-declared) | Meaning | This Pack |
|---|---|---|
| `whole-scope` | exactly one reading for the entire assessed scope, hung identically on every subject that reaches the node | `cross-model-alignment` (one fact about the model pair) |
| `per-subject` | one reading per observation subject | `asset-identity`, `in-model-position` (subject × each bound `requirement_key` that applies to it); `penetration-determination` (the penetrating `element_key`) |
| `per-subject-pair` | one reading per *(subject, counterpart)* pair, the counterparts named by the determination the requirement's `pair_source` points at | `opening-status` (one reading per *(penetrating element, penetrated architectural element)*; the opening itself is an **attribute** of that pair's determination — present, or a named absence — never a key) |

A `whole-scope` evidence requirement contributes **no subject of its own**
and, by definition, cannot be heterogeneous across subjects. A future Pack
that needs a finer alignment fact — per storey, say — declares it
`per-subject` at that grain, and it then splits like any other.

**No grain ever introduces a key that might not exist.** The previous
revision kept `opening-status` at `per-subject` for exactly this reason — an
opening/penetration pair whose second member is absent precisely when the
outcome is `not-modelled` would be a phantom key — and that rule is not
relaxed, it is satisfied by a different pair. The `per-subject-pair` grain's
second member is the **penetrated architectural element**, which exists
whether or not anyone has cut an opening in it, and which the
`penetration-confirmed` determination named as an `element_key` of the
consuming model version. So both members exist whenever the pair does, the
assessment invents neither, and the thing that may be absent — the opening —
stays where D-1 put it: an attribute of the reading, recorded as a named
absence.

**A `penetration-confirmed` determination that names no architectural
element, or names a key absent from the consuming model version in the
model-version context, is not admissible evidence.** It produces no
`penetration-confirmed` reading; the subject reads `not-yet-determined` and
routes to `UNKNOWN` / `penetration-not-determined` (§7.3). This is the
fail-closed direction: an inadmissible determination is no determination, and
never a pair with a member the assessment had to invent.

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
selector. For a `per-subject` or `per-subject-pair` assessment-backed evidence
requirement the reading is the recorded determination for that subject — for a
pair, the determination about *that* opening — or its `not-yet-*` outcome when
none exists. No finding-backed evidence requirement in this Pack reads at pair
grain, and none has to: the rule above is stated over subjects, and a pair is
a subject.

An `insufficient_evidence[]` entry (R-010 under `cross-model-alignment`) is
**never** a reading: its `PASS` is recorded as context only and produces none
of the outcomes, exactly as ADR 0002 §3.2 states.

### 3.2 Construction — split subjects incrementally down the tree

**Answer (construction).** For one activity, one assessed scope, one
model-version context:

1. **Admit the observation subjects** (§3.1 step 1) — the declared scope's
   `element_key`s whose published `ifc_class` is one of the activity's
   `subject_classes` — and put them in `element_key` lexicographic order
   (equivalently `(model_key, ifc_guid)` ascending): a frozen string key, so
   the order is deterministic with no clock, no set iteration, and no
   filesystem ordering (`AGENTS.md` rule 1). Every declared key the class
   admission excluded is recorded, for this activity, with the `ifc_class`
   that excluded it (§3.3) — the accounting is total, and this step is the
   only place an element leaves an activity's reckoning. An activity with a
   single model-pair subject needs no ordering. `whole-scope` evidence
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
   - **`per-subject-pair` evidence requirement: refine first, then read.**
     Before the node is read, each subject in the subgroup is replaced by one
     pair subject per counterpart the `pair_source` determination named for
     it — for `opening-status`, one `(penetrating element, penetrated
     architectural element)` pair per architectural element the
     `penetration-confirmed` determination listed. The node is then read
     exactly like any other `per-subject` node, over the refined subjects:
     pairs reading the same outcome stay one subgroup, pairs reading
     different outcomes split. Refinement is why a chimney through a floor
     slab and then the roof can reach `cross-referenced` for one pair and
     `not-modelled` for the other instead of collapsing to one of them, and
     why one shared shaft opening serving three MEP lines is three pairs
     naming the same counterpart, each asking whether that opening is
     inspectably linked to *its own* penetrating element. Refinement changes
     the grain of the carrier and nothing else: it adds no element to the
     assessed scope, removes none, and every refined subject records the
     admitted `element_key` it came from (§3.3). A subject refines at most
     once on any path, because invariant 17 makes a pair-grained node
     reachable only below its own `pair_source` branch and invariant 15
     forbids retesting an evidence requirement an ancestor already ruled out.
   - a subject the branch structure never routes to a node — an element
     whose `penetration-determination = no-penetration` branch carries
     `renders_inapplicable = ["opening-status"]` and terminates at `READY` —
     produces no reading for that node's evidence requirement at all, and is
     never refined, since refinement happens only at the node that declares
     the finer grain. "The pair's second member does not exist" never arises:
     both members of a penetration pair are elements the determination named
     or the scope declared, and the thing that may be absent — the opening —
     is an attribute of the pair's determination (a named absence, §3.3),
     just as an absent finding is.
3. **A subscope is a subgroup that has reached a terminal leaf:** the
   maximal set of observation subjects — *as they stand at that leaf*, refined
   or not — that traversed the **identical ordered path** of
   `(node_id, outcome)` pairs from the root to that leaf. The partition of the
   activity's admitted scope is the set of these leaf-terminal subscopes.

   **Refinement means one admitted element may appear in more than one
   subscope, and that is the design, not a violation of Framework invariant
   1.** A penetration pair is not the element it refined from; it is one
   opening to cut, which is the unit of labour `builders-work-openings`
   decides about — Checkpoint B's question is "can Architecture cut the
   builder's work openings", not "is this chimney good". Invariant 1 attaches
   one verdict to one *(activity × assessed scope × model-version context)*
   cell, and each subscope is its own such cell (§6); a chimney whose slab
   opening is cross-referenced and whose roof opening is not modelled has two
   pieces of labour in two states, and reporting one verdict for it would
   discard exactly the distinction the partition exists to hold. Every pair
   still names its admitted element, so nothing about which elements the
   verdicts concern is lost.

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
over outcome names), then by its smallest member subject key. A pair
subject's key orders as the tuple *(penetrating `element_key`, counterpart
`element_key`)*, both frozen strings, so the ordering is total and clock-free
whatever grain the leaf's members carry; within one leaf every member has the
same grain by construction, since refinement applies to a whole subgroup. The ordinal,
together with the record's `assessment_digest` (§5) and the
`pack_id::activity_id`, is the handle a resolving assignment (§4.3), a
`CONDITIONAL` promotion (§4.4), and a later successor record of either kind
(§4.5) point at.

**Answer (recording — the carrier and the readings hung on it, kept
separate).** Per requested activity, the record carries an ordered list of
subscope entries. Each entry separates:

- **the carrier** — `members`: the ordered observation subjects in the
  subscope (`element_key`s, penetration pairs, or the lone model-pair
  subject). This is the set the subscope *is*. A pair member records both its
  keys **and** the admitted `element_key` it refined from, so a reader can go
  from any verdict back to the element in the declared scope that it concerns
  without re-deriving the partition.
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

**Answer (recording — the total accounting of the declared scope, closes
E-3).** Alongside the partition, each requested activity records
`out_of_subject_class[]`: the declared assessed-scope keys the activity's
class admission excluded, each with the `ifc_class` that excluded it, in the
same `element_key` lexicographic order. It carries **no verdict, no
`resolution_kind`, no route, and no assignment**, and it is not a subscope:
an out-of-class key is not an *(activity × scope × model-version)* cell, and
minting a verdict for it would invent a Framework object for "the readiness of
something this activity is not about". What it is, is a completeness
statement, and the property it makes checkable is total accounting:

> For every requested activity, every key the declared assessed scope resolves
> to appears **exactly once** in either that activity's admitted subjects — at
> its coarsest form, before any refinement — or that activity's
> `out_of_subject_class[]`, and never in both.

The request-level observation a caller usually wants — "these keys were in my
scope and none of the activities I asked about was about them" — is the
intersection of those per-activity lists, and is a **rendering** of them in
exactly the sense §6's human summary is a rendering of the partition: it
states nothing the record does not already state, carries no verdict, and is
never an input to anything.

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
- the **successor reference**, when this record is one (§4.5): its `kind`
  (`recheck` or `authorisation`), and the prior record's `assessment_digest`,
  activity, and subscope ordinal it succeeds. Absent on an originating
  record;
- `assessment_digest` (§5) — a digest of this whole completed record, request
  and resolved result together, not of the request alone; logically the last
  thing written, and the point at which the record is **sealed** (§4.5).

### 4.2 Per activity, per subscope

Everything in §3.3: `members` (with each pair member's originating
`element_key`), `path`, `verdict`, `resolution_kind`, the resolved
`resolution_routes[]` chain, the evidence citations and named-absence
markers.

**Per activity, additionally:** `out_of_subject_class[]` (§3.3) — the declared
scope keys this activity's class admission excluded, each with its
`ifc_class`, carrying no verdict. An activity whose admitted subject set is
**empty** — every declared key out of class — records that partition as empty
and reaches **no verdict at all**: there is no cell for a verdict to attach
to. The absence is stated in the record rather than left to inference, and
**nothing downstream may read an empty partition as a release**; `READY` is
reached only by a subject traversing a path to a `READY` leaf, and an activity
with no subjects has no such traversal.

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
  `assigned_team_or_person` (row 8d), never instead of it. Its absence is the
  legible state "assigned, not yet started". Because a record is sealed at
  §4.5, an actor who acts after this record was written is not patched into
  it: the actor is carried by whichever successor record is written next, and
  this record keeps saying what was true when it was written.

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

**The resolver and the authoriser are two records, and neither is derived from
the other (product decision, recorded once, here).** §4.3's
`assigned_team_or_person` — `default_role` resolved through
`overlay.team_mapping[]` — is who this assessment tasks with *resolving* the
leaf. Fields 4 and 5 above are who *accepted the risk* of releasing despite it
and the Overlay role they acted under. Each is recorded independently and in
full; neither is ever computed from the other, and neither stands in for the
other when it is missing — a missing assignment fails the request closed
(§4.3), a missing or unlisted authoriser refuses the promotion (§7.2). ADR
0002 §3.5 settles the same separation on the configuration side, for
`team_mapping` against `risk_authorisations[]`; this is its runtime-record
counterpart and the two statements are not restatements of each other.

**This document does not require the two to be different people.** A project
where the person who would resolve a leaf is also trusted to authorise a
release against it is expressible today and is not an error here — ADR 0002
§3.5 already allows a role to appear in both tables as two independently
declared facts. Whether separation of duties should be *enforced* is a
governance question that would belong to Overlay policy, and it is **recorded
as not implemented**: no field expresses it, nothing in this design infers it,
and Checkpoint D must not assume one exists — the same treatment ADR 0002 §3.6
gives the deferred override capability.

### 4.5 Exit status, successor records, sealing, and how a promotion continues

- The `recheck_condition` for every non-`READY` subscope, copied from the
  pinned Pack's route (so a later reader is not renegotiating it —
  Checkpoint B §5 item 9).

**A record is sealed when its `assessment_digest` is computed (closes E-5).**
No field of a sealed record is ever rewritten, corrected, appended to, or
deleted — not a verdict later shown wrong, not an assignment later
reassigned, not an actor who acted afterwards, not a promotion that later
lapses. Every later fact about the same assessment is a **new record citing
the sealed one**. The digest is what makes this checkable rather than merely
promised: it is a hash of the whole resolved record (§5), so a rewritten
record no longer matches its own digest, and the references other records
hold to it break loudly instead of silently pointing at changed content.
This is the same discipline the published contract already runs on, applied
to a tree the contract does not cover.

**Two kinds of successor record, and no others.** Each carries the successor
reference of §4.1 — `kind`, plus the prior record's `assessment_digest`,
activity, and subscope ordinal — and each is a full new record with its own
`assessment_digest`. The prior record is untouched in both cases.

**`kind = "recheck"` — the evidence is read again.** It re-derives subscope
membership and every reading from the current evidence, and records whether
the cited subscope's `recheck_condition` is now met **and** whether the
model-version context is still current (§2.3), by comparing content
identifiers. Its verdict may differ from the cited record's; that is what it
is for.

**`kind = "authorisation"` — the evidence is unchanged and an authorisation
is what is new (closes E-5).** This is the shape the real sequence needs and
the previous revision had no way to express: an assessment produces `UNKNOWN`,
the coordination review that reads it accepts the risk in the room, and the
minutes cite a record that carries the signature. Writing that as a
`recheck` would misdescribe it — nothing was rechecked — and patching it into
the `UNKNOWN` record is forbidden by sealing. So it is its own kind, and its
defining constraint is that its claim of "evidence unchanged" is **proved,
never asserted**:

- it re-derives the cited subscope exactly as a recheck does, and **requires**
  the re-derived membership, path, every reading with its citations, the
  verdict, and the `resolution_kind` to be identical to the cited record's;
- it requires the model-version context, the cited `validation_run_id`,
  `ruleset_id`, `ruleset_version`, and the composed Pack's `pack_version` to
  be identical too;
- if **anything** differs, it is not an authorisation record. The assessment
  refuses to write it as one and says which comparison failed; what the
  situation actually calls for is a `recheck`, which may then carry its own
  promotion. There is no "assume unchanged" path, and no partial write.

An authorisation record carries the `CONDITIONAL` promotion of §4.4 with all
nine fields, and may carry an `actual_actor` (§4.3). It changes no verdict:
the subscope's original verdict, `resolution_kind`, and underlying blocker or
gap are re-derived identically and stand, with the promotion layered on top,
exactly as §4.4 requires.

**How a `CONDITIONAL` promotion continues across records (closes E-4; this
supersedes the D-4 ruling the previous revision recorded, at the technical
director's direction).** The earlier rule was that a promotion is never
inherited and must be re-authorised in every successor record. The rule is
now:

> A promotion **continues with the record** — carried forward and restated in
> full, never silently — for as long as **both** of the following hold: its
> own recorded voiding / failure condition (field 9) has not been met, and
> the model-version context is unchanged. If **either** changes, the
> promotion **lapses**, and continuing the release requires a fresh
> authorisation.

**What "both of the following hold" has to be, before a continuation may be
written (closes E-6).** The rule above says when a promotion continues; it did
not say how anyone knows. As written it could be satisfied by an evaluator
forming its own opinion of a prose voiding condition, or by nobody forming one
at all and the promotion carrying on because no one said otherwise. Neither is
a thing this design may express. **A continuation is written only when all
four of the following are proved on the record that carries it, and it is
never the default:**

| # | What must be proved | How it is proved | If it is not proved |
|---|---|---|---|
| 1 | the promotion's **voiding / failure condition (field 9) remains unmet** | a recorded **voiding-condition determination** reading `unmet`, cited by reference (below) — never the evaluator's own reading of field 9 | the promotion **lapses**; the reason is recorded |
| 2 | the **model-version context is unchanged** | value comparison of both models' content identifiers against the promotion's field 6 (§2.3) — a comparison, never a clock read | the promotion **lapses**; the reason is recorded |
| 3 | the promotion's cited **authorisation role is still listed** in the composed Overlay's `may_authorise_roles` for that exact `pack_id::resolution_kind` | membership test against the Overlay composed for *this* record, not the one composed when the promotion was granted | the promotion **lapses**; the reason is recorded |
| 4 | **coverage has not widened** | every member the continuation covers is inside the promotion's recorded release scope (field 8) **and** among the members it was granted over | the continuation does not extend to the uncovered member; that member has no promotion |
| 5 | the **re-derived subscope reaches the leaf the promotion was granted against** — its `verdict`, its `resolution_kind`, and its terminal outcome are the promotion's fields 1, 2 and 3 | the subscope is re-derived from current evidence like any other, and all three are compared as values against what the promotion recorded | the promotion **lapses**; the reason is recorded — **the risk changed** (closes E-7a; widened to fields 1 and 3, closes D-6) |
| 6 | the composed Pack's **`pack_version` is the one the granting record recorded** | value comparison against the granting record's §4.1 provenance | the promotion **lapses**; the reason is recorded (closes E-7c) |
| 7 | **no sealed record in this promotion's chain has already recorded its lapse** | walk the chain by the origin reference; a lapse anywhere in it is terminal | there is no continuation to write: the promotion is **already ended**, and only a new promotion can release the work (closes E-7b) |

**Check 5 is what the other six presuppose, and it is evaluated first.** Until
the currently re-derived `resolution_kind` is known to be the one the promotion
names, "that exact `pack_id::resolution_kind`" in check 3 is ambiguous between
two different kinds, and it was that ambiguity — not any missing row — that hid
the hole E-7 names. **Check 3 tests the promotion's field 2 kind: the kind the
authorisation was actually given for.** Check 5 makes that the same value as the
currently re-derived one, so the two can no longer diverge without the
continuation stopping.

**Check 5 compares three values, not one, and the reason is that a
`resolution_kind` does not identify a leaf (closes D-6).** An earlier revision
compared the kind alone, on the stated ground that "each `resolution_kind`
belongs to exactly one leaf". **ADR 0002 gives no such guarantee, and that
lemma is withdrawn.** What it actually fixes runs one way only: every
`BLOCKED` leaf's `failure_kind` and every `UNKNOWN` leaf's `gap_kind` must
match **exactly one** `resolution_routes[]` row, and every row must be used by
**at least one** leaf (§3.2). At-most-one is nowhere required — ADR 0002 §3.2
says in terms that "two leaves can only ever share a `resolution_kind` by
sharing the identical route behind it", and its Consequences record "reuse of
one `resolution_kind` across leaves only ever meaning identical treatment, by
construction". `failure_kind` and `gap_kind` also draw from **one shared
namespace** (§3.8). Put together, a perfectly legal Pack may carry one
`resolution_kind` on a `BLOCKED` leaf and on an `UNKNOWN` leaf at once,
provided the single route behind it fits both — and then a kind-only check 5
would pass while the verdict flipped from `UNKNOWN` to `BLOCKED`. That is
exactly the failure E-7 exists to stop, re-entering through the weakest row of
the derivation table below. ADR 0002's own worked Pack does not exercise it —
its ten routes and ten non-`READY` leaves are one-to-one (§6) — but ADR 0002 is
a general design and this document is a general design over it.

Comparing `verdict`, `resolution_kind` and terminal outcome together is what
makes check 5 mean *"the leaf is the leaf that was authorised"*, which is what
it was always supposed to mean: those three are precisely what the promotion's
fields 1, 2 and 3 already record about the leaf, so the check compares recorded
values and needs nothing new to be written down.

**The alternative was considered and not taken.** One could instead make
"a `resolution_kind` is used by at most one leaf" an explicit precondition this
design places on a Pack, and require a loader to enforce it — a nineteenth
Pack-load structural invariant in ADR 0002 §3.8. It would work, but it buys
the runtime nothing it cannot get for itself: it narrows what Pack authors may
write, in a merged document, to spare a continuation three value comparisons
against fields it already holds. The cheaper correction is the one that changes
no Pack's vocabulary.

**Why the risk changing kind is not covered by any of checks 1–4, and what it
looks like in this Pack.** A promotion accepts **one named risk of one named
kind** — field 7 read through field 2. Checks 1–4 compare identities and cite a
prose determination; none of them notices that the deficiency underneath has
become a *different* deficiency. This Pack has the case built into it:

- `cross-model-alignment-node` carries `misaligned` → `BLOCKED` /
  `cross-model-misalignment` and `not-yet-confirmed` → `UNKNOWN` /
  `cross-model-alignment-not-confirmed` **on the same node** (ADR 0002 §3.8).
- Suppose a promotion is granted on `cross-model-alignment-not-confirmed` — the
  accepted risk being that alignment has not been confirmed. Later somebody
  performs the `overlay-comparison` method and it reports the models
  **misaligned**.
- **Performing a check edits no model**, so both content identifiers are
  unchanged and check 2 passes. Members are unchanged, so check 4 passes.
  `information-manager` is still listed for
  `cross-model-alignment-not-confirmed`, so check 3 passes. A determination
  written before the comparison could still read `unmet`, so check 1 passes.
- Under checks 1–4 alone the release **continues** — while the accepted risk
  has changed from "nobody has confirmed alignment" into "the models are known
  to be misaligned", a different kind, a different verdict class, a different
  route, a different fix. And ADR 0002 §3.5's worked Overlay authorises
  **nobody** for `cross-model-misalignment`: it has no
  `risk_authorisations[]` row at all.
- With check 5 the re-derived leaf is a different leaf: the kind is
  `cross-model-misalignment` rather than field 2's
  `cross-model-alignment-not-confirmed`, the verdict is `BLOCKED` rather than
  field 1's `UNKNOWN`, and the terminal outcome is `misaligned` rather than
  field 3's `not-yet-confirmed`. All three disagree, and any one of them is
  enough: the promotion **lapses** and — by check 7 — lapses terminally.
  Re-releasing would need a **new** promotion for `cross-model-misalignment`,
  which §7.2's first row refuses in this project because no role may authorise
  that kind here. **The path stops at the lapse**, which is the only correct
  end for it.

**This is a lapse, not "no longer applicable".** The deficiency did not clear;
it became a different deficiency. Recording it as no-longer-applicable would
say the opposite of what happened, and would leave a `BLOCKED` subscope looking
like a released one.

**Check 3, restated with the ambiguity removed:** §4.4 requires the
authorisation role to be listed at the moment a promotion is granted, and
nothing re-examined it afterwards, so a project that removed a role from
`overlay.risk_authorisations[].may_authorise_roles` would have gone on carrying
releases authorised under a role it no longer permits anyone to authorise
under. It tests **field 2's** kind, and an Overlay change of that kind is
exactly a substantial change; it ends the release the same way a model re-issue
does.

**Check 6, and why `pack_version` belongs here.** An Overlay pins
`pack_version` by exact match, so moving it is a deliberate edit (ADR 0002
§3.4b). Across that edit the *same* `resolution_kind` may resolve to a
different `resolution_routes[]` row — different `consequence_kinds`, a
different `default_role`, a different `next_action`, a different
`recheck_condition`. A promotion authorised under the old row's meaning would
otherwise go on being carried under the new one, which is the same class of
substantial change as revoking the authorising role. **Ruleset identity is not
added as an eighth check**, and the reason is that its material effect arrives
through check 5: a `ruleset_version` move that changes what a bound requirement
means changes the readings, which changes the leaf, which changes the
`resolution_kind` — and one that changes none of those has not changed what the
promotion accepted.

**Where this set comes from, and where it stops (retracting an earlier
claim).** The previous revision called four checks "the complete set of
preconditions", which is no longer true and was too strong even then. The set
is not assembled by inspection; it is **derived from the nine fields a
promotion must carry** (§4.4), on the principle that a continuation must show
that each thing the authorisation was given against still names what it named:

| Promotion field | What still has to hold | Check |
|---|---|---|
| 1 original verdict | the re-derived verdict is compared, as a value, to this field | **5** |
| 2 `resolution_kind` | the re-derived kind is compared, as a value, to this field | **5** |
| 3 underlying blocker/gap | its terminal outcome is compared to this field's; its affected members are covered by the coverage check | **5** and **4** |
| 4 named authoriser | **not checkable** — see below | — |
| 5 authorisation role | still listed for field 2's kind | **3** |
| 6 named model versions | both content identifiers unchanged | **2** |
| 7 accepted risk | pinned only as far as its **kind** is pinned, which check 5 does directly by comparing field 2; the prose statement is not re-read and the magnitude is never computed at all (§4.6) | **5**, partially — see below |
| 8 release scope | coverage not widened | **4** |
| 9 voiding condition | reduced to `unmet` over every enumerated determination | **1** |
| — the Pack semantics fields 2 and 3 resolve through | `pack_version` unchanged | **6** |
| — monotonicity | no prior lapse of this promotion | **7** |

**No row in this table now leans on a property ADR 0002 does not guarantee.**
Fields 1, 2 and 3 are each compared directly against a re-derived value rather
than inferred from one another, which is the correction D-6 required: the
previous version derived fields 1, 3 and 7 from field 2 through a lemma about
leaves that ADR 0002 does not supply.

**What this design cannot check, stated rather than papered over.** Field 4 is
a **named person**, and nothing here observes whether that person is still in
the role, still employed, or would still accept today; the design records who
accepted and bounds the acceptance by fields 8 and 9, and that is the whole of
what it can do. Field 7 is **prose**: its kind is pinned by check 5, but the
sentence a person wrote about the risk they accepted is not re-read against the
world, and its **magnitude** is never computed at all (§4.6). So the
honest claim is not that the set is complete against every risk, but that it is
**complete against the nine fields, by construction** — every field is either
checked, derived from a checked one, or named above as uncheckable. A future
round that adds a promotion field must add its check here or record why none is
possible.

**The voiding-condition determination (closes E-6; its location and its fourth
field corrected, closes D-5).** Field 9 is prose, written by a person for
people. **The assessment does not parse it, interpret it, or decide it.** It
reads a *determination about* it, by reference, and records which reference it
read — the identical discipline §1.2 item 4 already fixes for every
`overlay.accepted_evidence_methods[]` output: the assessment cites a
coordination-review determination rather than deciding a penetration itself,
and it cites a voiding-condition determination rather than deciding a voiding
condition itself.

**A voiding-condition determination lives outside the assessment record, and
this document previously said two incompatible things about that.** Check 1
above calls it "cited by reference", which is the external model; §5 and §7.2
described it as content the record carries; and its fourth field named "the
`assessment_digest` of the record that carries it", which under §5's own
enumeration would have been part of the input to the digest it names — a
value that cannot be computed, since it would have to be known before it could
be produced. Nor could it be read as living in some earlier record: at the
moment a promotion is *granted* there is nothing yet to determine, the moment
that needs a determination is the continuation itself, and §4.5 admits exactly
two kinds of successor record with no third kind whose purpose is to carry a
determination. **The external model is the correct one and is the one adopted
here**, for the same reason every other determination in this design is
external: it is made by people, in a process this document does not design,
and the assessment's whole discipline toward it is to cite rather than
adjudicate.

So: **the determination is produced outside the assessment and carries its own
reference identity. The record cites that reference and records the outcome it
read, and nothing else about it** — exactly the shape §3.3 already uses for
every other determination reading, `(reference, outcome)`. Nothing about a
record is an input to a determination the record cites, so no value depends on
itself.

**What the determination must itself carry for the assessment to admit it**,
checked when it is read, and failing any of which it **is not a determination**
at all:

1. the **determiner** — a named person, and the role they acted under, both
   stated in the determination and neither derived from anything;
2. the **basis** — what was actually examined, cited by reference: other
   determination references, `finding_key`s, model content identifiers, and
   the promotion's own field 9 as the thing being judged. A conclusion with no
   cited basis is not a basis;
3. the **outcome** — exactly one of `unmet`, `met`, or `undeterminable`
   (below);
4. **which promotion it judges** — the `assessment_digest` of the **sealed
   record in which that promotion was granted**, plus the activity and
   subscope ordinal, **and** the model-version context it was made against
   (both content identifiers). This is what the fourth field should have been.
   It is computable at the only moment it is needed: the granting record was
   sealed before any continuation of it could be attempted, so its digest
   already exists when a determiner writes one down. And it is what makes the
   determination *this* continuation's rather than a free-floating opinion —
   the assessment admits it only when the promotion and the context it names
   are exactly the ones being continued (§7.2).

**The granting record, not the immediately preceding one, is what field 4
names**, and the difference shows up as soon as a promotion is continued more
than once. In a chain — record A grants, B continues, C continues — both A and
B carry the promotion, so "the record that carries it" would have been
ambiguous at C. A promotion has one origin, so its origin is the stable anchor:
every determination along the chain names A. For C to be able to name A, a
record that continues a promotion records the promotion's **origin reference**
(A's `assessment_digest`, activity, subscope ordinal) alongside the successor
reference of §4.1, which points at the immediately prior record and is a
different thing. The origin reference is continuation bookkeeping carried
forward unchanged along the chain; it is **not** a tenth promotion field, and
§4.4's nine are still nine and still all restated.

This is the same admissibility discipline §3.1 already applies to a
`penetration-confirmed` determination that names no architectural element: an
inadmissible determination is no determination, and the direction it falls is
closed.

**Check 1 is a reduction over every admissible determination, not a lookup of
one (closes E-7b).** More than one determination may name the same promotion
and the same model-version context — a first one reading `unmet`, a later one
reading `met` once somebody looked harder. If the outcome depended on *which*
one a record happened to cite, a continuation would be a matter of choosing a
citation, and check 1 would prove nothing. So:

- **The assessment reads every admissible determination naming this
  promotion's origin reference and this model-version context, and the record
  cites all of them.** This is a requirement on wherever determinations are
  kept: it must be enumerable by that key. Where exhaustive enumeration cannot
  be established, check 1 is **not proved** and the promotion lapses — the
  design does not assume a store it has not been given (§7.2).
- **The reduced outcome is the maximum of the enumerated set under one fixed
  order:** `met` > `undeterminable` > `unmet`. A continuation requires the
  maximum to be `unmet`, which is to say **every** determination reads `unmet`;
  a single `met` or `undeterminable` anywhere in the set lapses the promotion,
  and the reason recorded is that maximum.

The order is total over a three-value vocabulary, so the reduction is a
**maximum over a set, not a pick**: it is independent of citation order, of
which determination the record found first, and of how many there are. It reads
no clock — "later" plays no part, and does not need to, because the thing that
dominates is the more adverse reading rather than the more recent one. Two
determinations disagreeing is exactly the case where the release should stop.

This reduction is **not** §3.1's within-subject `FAIL` precedence and does not
touch it: that rule collapses findings for one subject under one evidence
requirement, and is forbidden from acting across subjects (§3.2). This one
reduces determinations about **one promotion** — there is no scope to
partition and no subject to select between.

**A lapse is terminal for the promotion it ends (closes E-7b).** Once any
sealed record has recorded that a promotion lapsed, no later record may
continue that same promotion — identified by its origin reference — for any
reason, including a determination reading `unmet` that predates the lapse.
Continuing to release the work then requires **a new promotion**: a fresh grant
with all nine §4.4 fields, its own named authoriser, its own authorisation role
listed for the *current* `resolution_kind`, and its own origin. This is what
makes the enumeration above safe rather than merely thorough — a lapse cannot
be undone by finding an older, friendlier determination, because lapse is a
one-way state of the promotion and not a property of a record's citations. It
is also what makes check 5's worked case end where it should: the promotion
lapses, and re-release has to pass §7.2's first row, which in ADR 0002 §3.5's
worked Overlay refuses `cross-model-misalignment` outright.

**One determination may support more than one continuation, and only while
what it names still holds.** Because field 4 pins it to one promotion and one
model-version context, a determination reading `unmet` supports continuations
of that promotion under that context and nothing else; re-issue either model
and it no longer names the context being continued, so it can support nothing.
This is deliberate rather than a gap left open: requiring a *fresh*
determination on every successor record would put the determiner's signature
back on a per-query footing, which is exactly the incentive the E-4 reversal
removed. What bounds the release is the promotion's own field 9 and the four
checks, not how often somebody is made to sign.

This document does **not** fix which role is entitled to make such a
determination. That is a governance question, it would be Overlay policy if it
were answered, and it is **recorded as not implemented** — no field expresses
it and Checkpoint D must not assume one exists. What makes the gap safe to
leave open is the direction the missing case falls: an absent determination
does not permit a continuation, so nothing can be released by nobody having
been entitled to say anything.

**Three states that are not `unmet`, kept distinct, none of them continuing.**
The distinction matters because the three have different next actions, and
collapsing them would hide which one a team is actually in:

| State | What it means | Continuation | What the record says |
|---|---|---|---|
| **no determination** | none the record can cite names this promotion and this context — nobody looked | never | the promotion **lapses**, reason: no voiding-condition determination |
| **`undeterminable`** | one was made and could not decide: the basis was insufficient, **or** field 9 is written so that no evidence could decide it | never | the promotion **lapses**, reason: undeterminable, citing the determination — whose determiner and basis show *which* of the two it was |
| **`met`** | the condition has occurred | never | the promotion **lapses**, reason: voiding condition met |

A determination the record cannot cite by a resolvable reference, or one
missing any of the four things above, is read as **no determination** and
lapses under the first row — attributability is not a formality here, it is
the whole of what distinguishes a determination from an assertion, and a
determination that names no promotion is not attributable to the release it
would extend. And an
`undeterminable` outcome caused by an undecidable field 9 is worth stating
separately from an insufficient basis because the fixes differ: one is
gathering evidence, the other is that the release was authorised against a
condition that could never end it, which is a fact about the promotion rather
than about the world.

**Silence is neither continuation nor lapse (closes E-6).**

> For every subscope whose **promotion chain is non-empty** — that is, some
> sealed record reachable through this subscope's successor chain granted a
> promotion, continued one, or recorded one's lapse — a successor record must
> record **exactly one** of: a continuation with every check of the table
> above proved; a **lapse**, with its reason; or that the promotion is **no
> longer applicable** because the deficiency it was granted against has
> cleared. A successor record that records none of the three is not a legal
> record and is refused (§7.2).

**The trigger is the promotion, not the record that happens to be cited
(closes E-7b).** The previous wording fired only when *the cited record*
carried a promotion, and that left a hole the terminal-lapse rule would
otherwise not close: the record that lapses a promotion neither grants one nor
continues one, so a later record citing it — or citing the granting record
directly — was under no obligation to say anything about it at all. Keying the
obligation to the promotion's origin reference, reachable through the chain,
closes it: once a promotion exists anywhere behind this subscope, every
successor keeps answering for it, including the successors that come after it
has ended. After a terminal lapse the only legal answers are a lapse restated
with its reason, or that the deficiency has since cleared; a continuation is
not among them.

A promotion therefore never ends by going unmentioned, and never survives by
going unmentioned either. Which of the three a record reached, every lapse and
its reason, every continuation with the seven proofs behind it, and the
references and reduced outcome of the voiding-condition determinations it read
are all part of the record and so are covered by its `assessment_digest` (§5). The
determination's own content is not: it lives outside the record, at the
reference the record cites, and is audited there.

Four things that rule does not relax. A continued promotion is still
**additive**: the subscope's own current verdict, `resolution_kind`, and
underlying blocker or gap are re-derived and recorded, with the promotion on
top — it never becomes `READY` and never erases the deficiency. It is still
carried **in full**: all nine §4.4 fields are restated in the successor
record, and a successor that cannot restate them all does not carry the
promotion. It is still **bounded by its release scope**: continuation covers
only members inside the promotion's recorded release scope and among the
members it was granted over — a subject that appears in the subscope for the
first time on a later record is not covered, and gets no promotion. And it
still requires an **authorisation role listed for this exact
`pack_id::resolution_kind`**; nothing about continuation creates one.

Two of those four are checks 3 and 4 of the table above, and they are the
same statement read from the other end: what a continuation must prove is what
the rule refuses to relax. The third of the three legal outcomes is the easy
one — when the deficiency has cleared there is nothing to continue, the
subscope reaches its own verdict on current evidence, and the record states
that the promotion is no longer applicable.

**Why the reversal, stated plainly, because the earlier reasoning was not
wrong about the risk it named.** The concern was that an acceptance could
outlive the authoriser's knowledge of the current state. But the ninth field
exists precisely to bound that: a promotion that must name the condition that
would end it is an authorisation that expires on its own terms, and requiring
a fresh signature at every recheck as well ties **signing frequency to query
frequency**. That is the perverse incentive: a team that rechecks weekly
needs a weekly signature, and the cheapest way to reduce signatures is to
recheck less often — which suppresses exactly the activity that would surface
the change that should void the promotion. Continuation on stated conditions
keeps the acceptance bounded and makes rechecking free.

**This rule is negotiable and is flagged as such.** It trades a re-signature
per query against a re-signature per material change, and which of those a
project wants is a product question about how authorisation is governed, not
a structural property of the record. A later product round may move it; what
must not move with it is any of the four non-relaxations above — additive,
carried in full, bounded by release scope, authorised for this exact
`pack_id::resolution_kind` — since each of those is a consequence of Framework
invariant 6 rather than a policy choice.

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
- the resolved result — for every requested activity, the ordered admitted
  observation subjects, that activity's ordered `out_of_subject_class[]` with
  each key's `ifc_class` (§3.3), and every subscope's `path` (with its
  `whole-scope`, `per-subject` and `per-subject-pair` readings, each pair
  member carrying both its keys and the admitted `element_key` it refined
  from, and each reading carrying its cited `finding_key`s / determination
  references / named-absence markers), `verdict`, `resolution_kind`, resolved
  route, and assignment;
- any `CONDITIONAL` promotion (§4.4), with all nine of its fields, whether
  first granted in this record or continued into it (§4.5) — a continued
  promotion is hashed as the content it is, so a record that carries one is
  never byte-identical to the same record without it;
- for every subscope whose promotion chain is non-empty, which of the three
  legal outcomes this record reached (§4.5) — a continuation with its seven
  proofs, a lapse with its reason, or no-longer-applicable — together
  together with, for a continuation or a determination-driven lapse, the
  promotion's **origin reference**, the **references of every
  voiding-condition determination** the record enumerated for that promotion
  and context, the **reduced outcome** those yielded, the **verdict,
  `resolution_kind` and terminal outcome re-derived for the subscope** and the
  **`pack_version`**, each compared against what the granting record holds, and
  whether a prior lapse of this promotion was found in the chain (§4.5) — the reference and the outcome, not the
  determination's own content, which lives outside the record and is not an
  input to this digest. A record that continues a promotion and one that
  lapses it therefore hash differently, which is what makes a lapse checkable
  rather than merely stated;
- for a successor record, its `kind` and the prior record's
  `assessment_digest`, activity, and subscope ordinal it succeeds (§4.5) —
  already final, so no cycle.

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
  the successor references between records (§4.5). It is never exported,
  snapshotted, or joined against a published CSV.
- **The seal.** Because it covers the whole resolved record, it is also what
  makes §4.5's no-rewrite rule checkable: a record edited after its digest was
  computed no longer hashes to the digest other records cite. Sealing is not a
  new mechanism, it is this one read as a guarantee.

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
  0002 §6), there is exactly one subscope = the whole admitted scope = one
  verdict, and presentation is identical to an un-partitioned assessment.
- When the partition is **empty** — no declared scope key was admitted by the
  activity's `subject_classes` (§3.1) — there is no cell, and therefore **no
  verdict**. The record says so explicitly, alongside the
  `out_of_subject_class[]` list that explains it (§4.2). An empty partition is
  read as "this activity is about none of what you asked about", never as
  `READY`: nothing traversed a path to a `READY` leaf, and an absence of
  blockers among zero subjects is not the absence of blockers invariant 3
  means.

**A non-authoritative human summary** may be shown alongside the partition —
counts per verdict class, the most severe class present. It is a rendering
*of* the partition: it states nothing the partition does not already state,
carries no verdict of its own, is never stored as one, and is never an input
to the resolving assignment (§4.3), a `CONDITIONAL` promotion (§4.4), a
successor record (§4.5), or anything downstream. Summarising verdict classes across
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

**Every row a previous revision carried is unchanged, row for row, in wording
and in its mapping to ADR 0002 §3.7.** Each round adds rows and removes none.
The E-2/E-3/E-4/E-5 round added five in §7.1 for the request-side consequences
of a declared object scope and a Pack-declared grain, one in §7.2 for a
promotion whose continuation is not covered, and one in §7.3 for an
inadmissible penetration determination. The E-7 round added six to §7.2 — the
re-derived kind, `pack_version`, the reduction over several determinations, a
store that cannot be enumerated exhaustively, the terminal lapse, and the
widened silence trigger. This round adds one more, for a re-derived verdict or
terminal outcome that is not the one authorised, and brings **two** earlier
rows into line with the text around them: the E-4 row's list of lapse causes,
and the E-6 silence row's count of the proofs a continuation must carry.
Neither rule changed — every cause the E-4 row named still lapses a promotion,
and silence is still refused — the rows had simply been left behind by rounds
that added causes and proofs above them.

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
| The request's assessed scope names an `element_key` absent from the producing model version's element inventory | Refuse — a key with no `ifc_class` cannot be admitted or excluded, so the total accounting of §3.3 could not be produced for it, and silently dropping it is the failure mode this checkpoint's whole scope rule exists to prevent | (new to this round; follows from the class admission in §3.1 and from ADR 0002 §3.2's coverage-is-not-scope rule) |
| A requested activity declares element-grained evidence and the composed Pack gives it no `subject_classes` (or gives an empty, duplicated, or wildcard list) | Composition already failed closed at Pack load; the assessment has no admissible subject rule and refuses | ADR 0002 §3.7's two `subject_classes` rows (**closes E-3**) |
| An evidence requirement of a requested activity carries no `subject_grain`, or a `per-subject-pair` grain with no `pair_source` (or the reverse) | Composition already failed closed at Pack load; the assessment cannot key the requirement's readings and refuses | ADR 0002 §3.7's `subject_grain` / `pair_source` rows, and invariant 16 (**closes E-2**) |
| A successor record with `kind = "authorisation"` re-derives evidence that differs from the record it cites — in membership, path, any reading, verdict, `resolution_kind`, model-version context, cited run, ruleset, or `pack_version` | Refuse to write it as an authorisation, naming which comparison failed; the correct successor is a `recheck`, which may carry its own promotion. Never written as a partial record, and never with "unchanged" asserted rather than proved (§4.5) | (new to this round; **closes E-5**) |
| Any write is attempted against a record whose `assessment_digest` has been computed | Refuse — a sealed record is never rewritten, corrected, appended to, or deleted; every later fact is a new record citing it (§4.5) | (new to this round; **closes E-5**) |
| Any Pack-load structural invariant fails (dangling node, cycle, uncovered `outcome`, `CONDITIONAL` leaf, orphaned/duplicate `resolution_kind`, out-of-scope `next_node`, `renders_inapplicable` violation, unresolved `direction_id`, `pair_source` violation, …) | Composition already failed closed at Pack load; the assessment has no valid tree and refuses | the eighteen Pack-load invariant rows and the `resolution_routes[]` / `directions[]` / `decision_nodes[]` rows of ADR 0002 §3.7 |

### 7.2 `CONDITIONAL` promotion defects — the promotion refuses, the leaf stands

| Missing / wrong input | Assessment behaviour | ADR 0002 §3.7 row |
|---|---|---|
| A `CONDITIONAL` promotion is attempted for a `resolution_kind` with no `overlay.risk_authorisations[]` row for that `pack_id` | Refuse the promotion only; the subscope's verdict stays `BLOCKED`/`UNKNOWN`; `CONDITIONAL` is simply unavailable for that `resolution_kind` in this project — never a default authoriser, never `resolution_routes[].default_role` standing in | "A `CONDITIONAL` promotion is attempted for a `resolution_kind` with no matching `overlay.risk_authorisations[]` entry" |
| The promotion cites an authoriser role not in `may_authorise_roles` for that exact `pack_id::resolution_kind` | Refuse to record it as `CONDITIONAL` — it is an unauthorised release, not a promotion | ADR 0002 §3.8: "a promotion citing a role not listed for this `resolution_kind` is not a `CONDITIONAL`, it is an unauthorised release" |
| The promotion omits any of the nine §4.4 fields | Refuse — an additive promotion that cannot name its original verdict, blocker/gap, authoriser, role, versions, risk, release scope, and voiding condition is indistinguishable from a fabricated `READY` | ADR 0002 §3.8 promotion field list; §1 invariant 6 |
| `overlay.risk_authorisations[].may_authorise_roles` is empty or contains a wildcard / `"all"` | Composition already failed closed; no promotion is possible | "An `overlay.risk_authorisations[].may_authorise_roles` is empty, or contains a wildcard, `"all"`, or any similarly unbounded value" |
| A successor record would continue a promotion when any of §4.5's seven checks is not proved — the enumerated determinations do not reduce to `unmet`, the model-version context has changed, the authorisation role is no longer listed, the re-derived leaf is not the one authorised, `pack_version` has moved, a prior lapse stands, or a member lies outside the recorded release scope or the members it was granted over | The promotion **lapses**, or does not extend to that member; the record states the lapse and its reason and shows the subscope's own verdict standing alone. Never continued silently, and never widened to cover a member it was not granted over (§4.5) | (**closes E-4**, causes since widened by E-6 and E-7; ADR 0002 §3.8 promotion field list) |
| A continuation is attempted and the record cites **no voiding-condition determination** | The promotion **lapses**; the reason (no determination) is recorded. The assessment never forms its own reading of field 9 to fill the gap, and an unexamined condition is never treated as unmet (§4.5) | (**closes E-6**; the same discipline §1.2 item 4 fixes for `accepted_evidence_methods[]` outputs — cite a determination, never adjudicate) |
| The cited voiding-condition determination cannot be resolved from its reference, or is missing its determiner, its cited basis, or its outcome | It **is not a determination**: it is read as the absent state and the promotion lapses under the row above. An unattributable assertion is not evidence that a condition remains unmet (§4.5) | (**closes E-6**; corrected shape, **closes D-5**) |
| The cited voiding-condition determination names a different promotion — a granting record `assessment_digest`, activity, or subscope ordinal other than this promotion's origin reference — or a model-version context other than the one being continued | It is not a determination **about this continuation**: it is read as the absent state and the promotion lapses under the row above. A determination is never widened to a promotion or a context it did not name (§4.5, field 4) | (**closes D-5**) |
| A voiding-condition determination reads **`undeterminable`** — the basis was insufficient, or field 9 is written so that no evidence could decide it | The promotion **lapses**; the reason and the determination's reference are recorded, and the determination's own determiner and basis show which of the two causes it was. `undeterminable` is never read as `unmet` (§4.5) | (**closes E-6**) |
| A voiding-condition determination reads **`met`** | The promotion **lapses**; the reason is recorded and the subscope's own verdict stands alone (§4.5) | (**closes E-6**; ADR 0002 §3.8 promotion field 9) |
| A continuation is attempted and the promotion's cited authorisation role is **no longer listed** in the Overlay composed for this record, under `may_authorise_roles` for that exact `pack_id::resolution_kind` | The promotion **lapses**; the reason is recorded. The role listed when the promotion was granted is not re-used, and no other listed role is substituted for it (§4.5, check 3) | (**closes E-6**; ADR 0002 §3.5's per-`pack_id::resolution_kind` authorisation table, §3.8's promotion field 5) |
| A continuation is attempted and the subscope's **currently re-derived `resolution_kind` is not the promotion's field 2** | The promotion **lapses**; the reason recorded is that the risk changed kind, and it is **not** recorded as "no longer applicable" — the deficiency did not clear, it became a different deficiency. Re-releasing needs a new promotion for the new kind, which must pass this table's first row (§4.5, check 5) | (**closes E-7a**; ADR 0002 §3.8's promotion field 2, §3.2's one-`resolution_kind`-per-leaf rule) |
| A continuation is attempted and the subscope's re-derived **verdict is not the promotion's field 1**, or its **terminal outcome is not the promotion's field 3** | The promotion **lapses**, recorded as the risk having changed, exactly as a changed `resolution_kind` is. Necessary because ADR 0002 permits one `resolution_kind` on more than one leaf, including a `BLOCKED` and an `UNKNOWN` one, so the kind alone does not identify the leaf that was authorised (§4.5, check 5) | (**closes D-6**; ADR 0002 §3.2's at-least-one-leaf-per-route rule and its Consequences on reuse, §3.8's shared `failure_kind`/`gap_kind` namespace) |
| A continuation is attempted and the composed Pack's `pack_version` differs from the one the granting record recorded | The promotion **lapses**; the reason is recorded. The same `resolution_kind` may resolve to a different route across a version bump, and an Overlay pins `pack_version` by exact match, so the bump is a deliberate edit (§4.5, check 6) | (**closes E-7c**; ADR 0002 §3.4b, §3.2's `resolution_routes[]`) |
| Two or more admissible voiding-condition determinations name this promotion and context, and at least one reads `met` or `undeterminable` | The reduction yields that value under the fixed order `met` > `undeterminable` > `unmet`, so the promotion **lapses** with that reason. The outcome is a maximum over the enumerated set, never a function of which determination the record cited first or at all (§4.5, check 1) | (**closes E-7b**) |
| The determinations naming this promotion and context cannot be **exhaustively enumerated** | Check 1 is **not proved** and the promotion lapses. A store that cannot answer "every determination for this promotion and context" cannot support a continuation, and the assessment never assumes the one it was handed is the only one (§4.5, check 1) | (**closes E-7b**) |
| A continuation is attempted for a promotion whose lapse any sealed record in its chain has already recorded | **No continuation is possible.** The lapse is terminal for that promotion; releasing the work again requires a **new** promotion with all nine §4.4 fields, its own authoriser, and a role listed for the *current* `resolution_kind` (§4.5, check 7) | (**closes E-7b**; §1 invariant 6) |
| A successor record whose subscope's **promotion chain is non-empty** — some sealed record in it granted, continued, or lapsed a promotion — records none of the three legal outcomes | **Refuse the record.** This is the widened trigger: the record that lapses a promotion neither grants nor continues one, so keying the obligation to "the cited record carried a promotion" let every record after a lapse fall silent about it (§4.5) | (**closes E-7b**; extends, and does not replace, the row below) |
| A successor record cites a record that carried a promotion over members of this subscope, and records **none** of: a continuation with every check of §4.5's table proved, a lapse with its reason, or that the promotion is no longer applicable | **Refuse the record.** Silence neither continues a promotion nor ends one, and a record that leaves a release's status unstated is not a legal record (§4.5) | (**closes E-6**, trigger since widened by E-7b to the promotion chain; §1 invariant 6 — an acceptance that nobody restated and nobody ended is indistinguishable from one nobody gave) |

### 7.3 Unresolved outcomes — not failures, routed as `UNKNOWN`

| Situation | Assessment behaviour | Basis |
|---|---|---|
| A validation-backed reading (subject × bound `requirement_key`) has **no finding at all** (an absent finding — the chimney; or `check` has not evaluated this handover) | The subject reads `not-yet-evaluated` for that evidence requirement; its subscope reaches the `UNKNOWN` leaf carrying the `gap_kind`; the named absence is recorded (§3.3, §4.2) | ADR 0002 §3.2: "`not-yet-evaluated` … describe a binding that exists but has not yet produced an admissible result … never a missing binding" |
| An assessment-bound evidence requirement has a method in the Overlay but **no recorded determination** for these model versions yet | Unit reads `not-yet-confirmed` / `not-yet-determined`; subscope reaches the `UNKNOWN` leaf with its `gap_kind` | ADR 0002 §3.2; the `no-penetration` vs `not-yet-determined` distinction |
| An R-010 `PASS` exists but no accepted `cross-model-alignment` method has produced a determination | `cross-model-alignment` stays `not-yet-confirmed`; the R-010 `PASS` is recorded as context only and never read as any of the three outcomes | ADR 0002 §3.2 `insufficient_evidence[]` entry: "a `PASS` is not alignment evidence" |
| A recorded `penetration-confirmed` determination names no architectural element, or names a key absent from the consuming model version in the context | Not admissible evidence, so it produces no `penetration-confirmed` reading: the subject reads `not-yet-determined` and reaches `UNKNOWN` / `penetration-not-determined`. The assessment never invents a counterpart to make a pair (§3.1) | ADR 0002 §3.2's `acceptance_condition` for `penetration-determination` (**closes E-2**) |
| A subgroup's subjects disagree on the named outcome at a node, before or after refinement | Split into outcome-homogeneous child subgroups (§3.2) — not a failure, and never collapsed by priority. A chimney whose slab opening is cross-referenced and whose roof opening is not modelled splits into two pair subscopes with two verdicts | ADR 0002 §3.2 partitioning rule |

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
   `CONDITIONAL`** — for any project, any Pack, any request, including a
   successor record of either kind (§4.5), a continued promotion, and every
   `out_of_subject_class[]` list (§3.3). Identical to (1):
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

**One further acceptance commitment, of a different kind — a test obligation
rather than a byte-invariance counterfactual, so the six above remain exactly
six:**

7. **Prove that an activity's object scope is genuinely per-activity.** All
   three activities in ADR 0002's worked Pack declare the same three
   `subject_classes`, and ADR 0002 §6 already records that this is a fact
   about this Pack — MEP work products handed to Architecture — and not a
   property of the design. A future machine test must therefore not take those
   three identical lists as its evidence, because a test in which every
   activity is about the same classes would pass whether the field were
   per-activity or Pack-wide, and so would prove nothing about the thing it
   exists to test. It must exercise **activities whose `subject_classes`
   differ from one another**, and assert that one and the same declared
   assessed scope admits **different subjects per activity** and produces a
   **different `out_of_subject_class[]` per activity**.

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
`BlockerCandidate`, `Subscope`, penetration-pair, out-of-class-ledger, or
promotion object is created or named as approved — the pair subject and the
out-of-class list are described shapes inside a record, not runtime types with
identities of their own; `assessment_digest` is the one identifier this document
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
exist and never owned by Pack, Overlay, or direction; **observation subjects admitted from that
scope by the activity's Pack-declared `subject_classes`** — object-class data,
never a filter on which elements carry findings, with every excluded key
recorded per activity so that the accounting of a declared scope is total;
**subscopes constructed as equivalence classes of observation subjects** — the
existing keys, or tuples of existing keys, a subscope is a set of — **split
incrementally down the decision tree** (never an up-front cross-product), with
each evidence requirement's readings hung on the subjects at the grain the
Pack declares (`whole-scope`, `per-subject`, or `per-subject-pair`, the last
refining a subject into one *(penetrating element, penetrated architectural
element)* pair per counterpart an earlier determination named — both members
existing whenever the pair does, the opening remaining an attribute and never
a key), identified by ordinal within a record, and recorded with the carrier
(`members`, each pair member naming the admitted element it refined from) and
the per-node readings kept separate; an assessment record
that **cites** frozen identities and is cited by none; **exactly one minted
identifier, `assessment_digest`**, a deterministic hash of the whole resolved
assessment record (request, evidence readings, verdicts, any promotion) —
never of raw bytes, never an input to `validation_run_id` / `requirement_key`
/ `finding_key` or any published-contract value; a **`CONDITIONAL` that
exists only as an additive promotion** carrying all nine ADR 0002 §3.8
fields, refusing to record without an authoriser role listed for the exact
`pack_id::resolution_kind`, never becoming `READY` or erasing its deficiency,
and **continuing with the record while its own voiding condition remains unmet
and the model-version context is unchanged, lapsing recorded on any change** —
carried forward in full and bounded by its release scope, never silently, and
never extended to a member it was not granted over; **a continuation proved,
never assumed**, on seven checks per record, derived from the promotion's own
nine fields rather than assembled by inspection — every enumerated
voiding-condition determination reducing to `unmet` under the fixed order
`met` > `undeterminable` > `unmet`, an unchanged model-version context, the
cited authorisation role still listed for the promotion's **field 2**
`resolution_kind`, coverage not widened, the **re-derived subscope still reaching
the leaf the promotion was granted against** — its verdict, its
`resolution_kind` and its terminal outcome all compared against fields 1, 2 and
3, because ADR 0002 permits one `resolution_kind` on more than one leaf and the
kind alone therefore does not identify one — so that a risk which has become a
different risk ends the release instead of inheriting its authorisation, an unchanged `pack_version`, and no prior lapse of this
promotion anywhere in its chain — with a **lapse terminal**, so that
re-releasing requires a new promotion with all nine fields rather than an older
and friendlier determination, and with the two fields no design here can
check — the named authoriser's continued willingness, and the accepted risk's
magnitude — named as uncheckable rather than assumed away — with that determination
**produced outside the record and read by reference**, like every other
determination in this design, carrying its own determiner, cited basis,
outcome, and the sealed record's `assessment_digest` plus activity, subscope
ordinal and model-version context naming **which promotion it judges**, so
that the record cites a reference and an outcome and no value is ever an input
to itself; with the assessment never itself interpreting a prose voiding
condition, with no determination, an
undeterminable one, and a `met` one kept distinct and none of them continuing,
and with exactly one of continuation, lapse-with-reason, or
no-longer-applicable required on every successor record so that silence
neither continues nor ends a release; **records sealed at their
digest and never rewritten**, with every later fact — an authorisation, a
recheck, an actor, a lapse — arriving as one of exactly two kinds of successor
record, the `authorisation` kind proving rather than asserting that the
evidence it cites is unchanged; **no roll-up above the subscope** — a
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
