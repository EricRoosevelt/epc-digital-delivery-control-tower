# Interdisciplinary coordination readiness: MEP → Architecture

**Status:** design evidence for Checkpoint B. Nothing here is implemented, and
nothing here is a schema. No code, rule, artifact or contract changes with this
document.

**What it is for.** One product claim is worth proving before anything is built:

> A project team can decide, from stated evidence, whether the MEP →
> Architecture coordination handover is fit for Architecture to keep producing
> against — and when it is not, they know what is blocking it, what that costs,
> who owns the fix, where in the authoring model to make it, and what would end
> the block.

The way to test that claim is to walk a real decision and see whether the
evidence this repository already produces can carry it. So this note starts at
the decision, not at an object model. There is no `AssessmentRun`,
`AssessmentItem`, `EvidenceGap` or `BlockerCandidate` here, and inventing them
first is exactly the mistake being avoided: every one of those names is an
answer, and the question has not been asked yet.

Everything cited below is real. Every `requirement_key`, `finding_key`,
`issue_key` and `element_key` in this document was read out of
`data/processed/canonical/` at contract 1.6 (rule set 2.2, tag `contract-1.6`),
and the counts match that run. Where the system has no evidence, this document
says so rather than inventing a plausible field.

---

## 1. The decision

### Who hands what to whom

The **MEP lead** issues the HVAC model to the **Architecture lead** at the
project's **Coordination** milestone. In this repository's worked example that
is:

| | |
|---|---|
| Project | `pcert-sample` — *PCERT Sample Scene* |
| Producing model | `hvac` (HVAC, 6 elements) |
| Consuming model | `architecture` (Architecture, 15 elements) |
| Milestone | Coordination, due `2026-08-01T00:00:00Z` |
| Run `as_of` | `2026-08-13T00:00:00Z` — twelve days past the milestone |

The sibling `structural` model (18 elements) is in the same project but is not
the subject of this handover.

### What Architecture does next with it

Architecture is not receiving the MEP model to admire it. Three pieces of
downstream production depend on it, and they depend on *different* parts of it:

1. **Reflected ceiling and bulkhead layout** — needs to know where MEP
   equipment physically is, in which storey, so ceiling zones and bulkheads can
   be drawn around it.
2. **Builder's work openings** — needs to know where MEP penetrates
   architectural fabric, so openings can be cut in walls, floors and roof.
3. **Room data sheets and equipment schedules** — needs each piece of equipment
   to carry the project's asset identity, so a schedule can be keyed to it.

These are three different questions, and each gets its own separately-reasoned
answer. A single "is the MEP model good?" verdict would be useless here, because
the same model can be refused for (3) on a known unmet requirement while (1) and
(2) are undecidable for two unrelated reasons — all at once. Each activity is
decided in exactly one place, on the evidence that bears on *it*; evidence
answering one question is never spent releasing another. This is the central
production observation of the whole scenario, and section 3 shows it happening.

### What a manager actually approves or refuses

The information manager chairing the coordination review is not approving a
model. They are approving, refusing or qualifying **a release of Architecture's
own labour**:

- *Approve* — Architecture starts the work on this MEP issue.
- *Refuse* — Architecture does not start; the MEP lead re-issues; the
  Architecture team is redeployed and the programme absorbs whatever that costs.
- *Qualify* — Architecture starts the parts that are safe and explicitly does
  not start the parts that are not, with the exclusions written down so nobody
  later assumes they were done. Qualifying is an act with an author: someone
  puts their name to the residual risk. That is what separates a qualified
  release from a team quietly hoping, and section 3 turns on the difference.

That third option is the one that matters commercially and the one a pass/fail
gate cannot express. A system that only says PASS or FAIL forces the manager to
either stop work that could have proceeded or start work that will be redone.

### The four verdicts, defined once

These four words are used in exactly this sense everywhere below, and nowhere in
a looser one. Each is a statement about **one activity**, in an **assessed
scope**, against a **named model version**.

| Verdict | Definition |
|---|---|
| **READY** | Every piece of evidence the assessed scope requires is present. The activity can start. |
| **CONDITIONAL** | The activity is released within a **named release scope**, because a **named authoriser** has accepted the remaining risk against a **named model version**. The accepted risk, the release scope and the conditions that void the release are all recorded. |
| **BLOCKED** | A known unmet requirement prevents the activity. |
| **UNKNOWN** | An evidence gap makes the activity undecidable — the evidence needed to answer the question was never produced, so neither release nor refusal can be justified. |

One consequence of the CONDITIONAL definition governs the whole document and is
the easiest thing here to get wrong: **knowing a risk exists is not the same as
someone having accepted it.** A team that is aware of an unconfirmed assumption,
proceeds anyway, and has no named authoriser, no named release scope and no
recorded voiding condition has not produced a CONDITIONAL. It has an UNKNOWN it
is working through. CONDITIONAL is a record of an authorisation event; where no
such event exists, none may be written down as though it did.

BLOCKED and UNKNOWN are also distinct, and the distinction is not severity.
BLOCKED means the system asked a question and got an unacceptable answer.
UNKNOWN means the question was never asked, or was asked of evidence that cannot
answer it.

### Direction

The handover is **directional: MEP → Architecture.** Architecture → MEP is a
different handover with different requirements, different consequences and a
different owner, and it is not this one.

**Direction is not core data, now or later.** Nothing in contract 1.6 carries
it. In particular `discipline_scope` does not: on requirement
`491a4a0b-9b4a-5f77-b90d-31a7dc8beb44` it reads `HVAC`, which says *this
requirement is evaluated against HVAC models* — an applicability set, with no
from and no to. Reading that tuple as an arrow would be wrong, and widening it
into a from/to pair would re-key every requirement that carries it. When
direction is eventually expressed, it belongs to **Pack data**, alongside the
purpose it serves. This document names a direction because the decision has
one; it does not propose putting one in the core.

---

## 2. Requirements and evidence

### What the system already knows

**Five rules in rule set 2.2 produce the seven requirements** that bear on this
handover — R-004A, R-004B, R-005A, R-005B and R-010, of which R-005A and R-005B
each declare two properties and therefore key two requirements apiece. All seven
are real and current:

| `requirement_key` | Rule | What it requires | Severity | `owner_role` | `stage` | `discipline_scope` |
|---|---|---|---|---|---|---|
| `491a4a0b-9b4a-5f77-b90d-31a7dc8beb44` | R-004A | `IfcDuctSegment` has a spatial assignment | ERROR | `mep-lead` | Coordination | HVAC |
| `2ead0930-568e-5d49-9708-716c5c740846` | R-004B | `IfcAirTerminal` has a spatial assignment | ERROR | `mep-lead` | Coordination | HVAC |
| `842a37c7-3183-5fce-ab45-b93c37ec7a08` | R-005A | Duct carries `EPC_Delivery.AssetTag` | WARNING | `model-coordination` | Coordination | HVAC |
| `9321298b-4a9f-5a3e-9d10-6668b736d465` | R-005A | Duct carries `EPC_Delivery.SystemCode` | WARNING | `model-coordination` | Coordination | HVAC |
| `a1402559-dcfc-5af4-a222-3a13eaf2b161` | R-005B | Air terminal carries `EPC_Delivery.AssetTag` | WARNING | `model-coordination` | Coordination | HVAC |
| `fd49c300-7ef6-5a8d-825f-53210dd579fe` | R-005B | Air terminal carries `EPC_Delivery.SystemCode` | WARNING | `model-coordination` | Coordination | HVAC |
| `acb11f11-bf18-5516-a6f2-21e451a6e410` | R-010 | Model shares a coordination reference with a sibling | ERROR | `model-coordination` | Coordination | Architecture;Structural;HVAC;Plumbing |

R-005A/B are marked `priority = Medium` and `labels = IDS;ProjectAssumption`.
That label is doing real work and is honoured throughout this document: **R-005
is a project assumption, not a general delivery requirement.** An EPC asset tag
is something a particular project agrees to; it is not a property the IFC
schema or buildingSMART obliges anybody to provide. It therefore belongs to a
future **Project Overlay** — the layer where one project's own agreements sit —
and must never be written into a Pack core. A Pack core that shipped
`EPC_Delivery.AssetTag` would be asserting one client's naming convention as a
universal truth about coordination.

### What the system does not know

The three production questions in section 1 need evidence this system does not
collect. Naming the gaps precisely is more useful than pretending the coverage
is complete:

| Evidence the decision needs | Present at contract 1.6? |
|---|---|
| Which storey an MEP element sits in | **Yes** — `elements.csv` carries `storey`, e.g. `00 groundfloor` |
| That an MEP element is spatially assigned at all | **Yes** — R-004A/B |
| Project asset identity on equipment | **Yes**, as a project assumption — R-005A/B |
| That a shared setout marker is present in every model | **Yes** — R-010, by exact name match plus a GlobalId reused across siblings |
| That the models are actually *aligned* to a common datum | **No.** R-010 compares names and GlobalIds, never coordinates or placements. A pass establishes a shared reference exists, not that the models overlay. |
| Whether MEP geometry clashes with architectural fabric | **No.** `ElementGeometry` (`domain.py:362`) holds a world-coordinate bounding box, but it is computed only for elements a BCF viewpoint must point at, is not exported to `elements.csv`, and nothing compares two elements' boxes. There is no clash or clearance evaluation anywhere in the pipeline. |
| Whether a penetration has a matching architectural opening | **No.** No requirement relates an MEP element to an architectural one. |
| Whether the MEP model was *issued* for coordination or is work in progress | **No.** `models.csv` records identity and a content hash. There is no issue status, revision, or suitability code. |
| Whether the receiving discipline accepted a previous issue | **No.** Issue history is per finding-group, not per handover. |
| Ceiling void depth allocated to each discipline | **No.** Not modelled anywhere. |

The right response to that list is *not* to go and build ten checkers. It is to
notice which gaps actually changed a decision in section 3, and carry only
those into Checkpoint C.

---

## 3. Four decisions on real evidence

Each case below is one production question, decided on findings that exist in
the current run, using the verdict definitions fixed in section 1. One question
gets one verdict: no case releases or refuses an activity that another case
decides, and where a case's evidence is silent about another activity that
silence is recorded rather than spent.

**The live verdicts for `pcert-sample`, `hvac` → `architecture`, are these
three:**

| Activity | Verdict | Reason |
|---|---|---|
| MEP equipment references in room data sheets / schedules | **BLOCKED** | The R-005 `AssetTag` / `SystemCode` requirements are known to FAIL; the identity the activity needs does not exist. Case 2. |
| Ceiling / bulkhead geometry | **UNKNOWN** | No alignment confirmation exists between `hvac` and `architecture`, and no rule produces one. Case 3. |
| Builder's-work openings | **UNKNOWN** | No penetration relationship and no corresponding opening evidence exists. Case 4. |

**No activity in this handover is live READY, and none is live CONDITIONAL.**
Where READY or CONDITIONAL appear below they describe evidence that would have
to be produced first, and each is labelled as the counterfactual it is. In
particular, no CONDITIONAL is available anywhere in this scenario, because a
CONDITIONAL requires a named authoriser accepting a named risk against a named
model version and **this repository contains no such record**. Writing one would
be inventing an authorisation nobody gave.

Case 1 walks the BLOCKED shape on cross-model position using the *other*
project's evidence, because `pcert-sample` does not fail R-010 and a verdict
with no worked example is an assertion.

---

### Case 1 — BLOCKED *(external counterfactual, not this project's state)*

*Can Architecture position the MEP model in the federated model at all?*

**Read this case as borrowed evidence.** In the main scenario —
`pcert-sample`, `hvac` → `architecture` — this particular blocker is absent:
R-010 **passes** on all three models, so no model in that project is missing a
shared setout reference. That is the whole of what the pass establishes. It is
not a confirmation that the models are aligned, and case 3 is where that
distinction does its work. Nothing below should be read as a live `pcert-sample`
fact, a current consequence for this Architecture team, or an action anyone on
this handover owes.

The BLOCKED shape is nevertheless worth walking here, because the four verdicts
must be distinguishable and a verdict with no worked example is an assertion.
`pcert-sample` does supply a live BLOCKED — case 2, on identity — but none for
*cross-model position*, and that is the failure whose blast radius is worth
seeing. The one available instance of it lives
in the *other* project in the repository, `iso-reference-view`, which is a set of
three unrelated buildingSMART sample files that share nothing. It is a genuine
run result, and it is genuinely not this project's. Where the text below says
what a team would do, it means *would*, in the counterfactual.

**Requirement and evidence.** R-010, `acb11f11-bf18-5516-a6f2-21e451a6e410`,
evaluated by the `completeness` checker. In `iso-reference-view` — the external
project, not the scenario's — it fails at model level:

- `finding_key` `2e5d3a0b-02ca-54ac-9eb9-04ab46c02948`
- `model_key` `iso-reference-view.plumbing`, `element_key` **empty** — the
  finding is about the model, because no element can stand for the absence
- status `FAIL`, severity `ERROR`, `is_issue = true`
- expected: *Carry the project's agreed setout references in every discipline
  model.*
- reason: *This model carries no coordination reference that any sibling model
  also carries, so the project's models cannot be federated.*
- grouped as issue `fedca7c7-e0f2-52ad-bb4a-d8ebcb883a82`, assignee role
  `model-coordination`, stage Coordination, due `2026-08-01T00:00:00Z`,
  `is_overdue = true`

**Purpose impact — in the counterfactual, and only where it reaches.** This
failure blocks the activities that **depend on cross-model position**, and only
those:

- **Ceiling / bulkhead geometry** — blocked. The MEP model cannot be placed
  beside the architectural one at all, so there is nothing to set ceiling zones
  out around.
- **Builder's-work openings** — blocked, for the same reason: where a
  penetration falls in architectural fabric is a cross-model question, and no
  common reference exists to ask it in.

**Schedules and room data sheets are not blocked by this failure.** They are
keyed by asset identity, which is a property carried on each element in its own
file; whether two models share a setout reference has no bearing on whether a
duct carries an `AssetTag`. Where schedules are blocked in this document — case
2, in the live project — the blocker is the R-005 identity failure and never
R-010. Confusing the two would let a shared-marker gate stand in for an identity
gate, which is exactly the single-verdict collapse this scenario exists to
prevent.

Note the *other two* models in that project fail the same rule (`cb599b72-…`
architecture, `85360128-…` structural): it is a project-wide shared-reference
failure there, not one discipline's mistake.

**Decision. BLOCKED** — for `iso-reference-view`, on the two position-dependent
activities. The corresponding activity in this scenario's handover, ceiling
geometry, is **not blocked by R-010**; `pcert-sample` passes it. It is UNKNOWN
for a different reason, and case 3 is where that is decided.

**Blocker.** No coordination reference shared with any sibling model.

**Business consequence — the kind of consequence, were this the project.** Two
kinds, both stated without a magnitude, because no cost, duration or effort data
exists anywhere in this repository and none may be invented: position-dependent
work **cannot start**, and coordination geometry produced meanwhile against an
assumed origin **carries rework risk** when the true setout arrives. What either
would cost this project in money or programme is a question for the Overlay cost
parameters of section 5 and for runtime data, neither of which exists. The one
timing fact that *is* evidenced: the `iso-reference-view` Coordination milestone
is `2026-08-01T00:00:00Z` and its issue is flagged `is_overdue = true` at the
run's `as_of`. None of this is a consequence being carried by `pcert-sample`.

**Responsible role.** `model-coordination` — carried on both the requirement and
the derived issue. Correctly so: no single discipline lead can fix this, because
the reference must be *agreed* before it can be inserted. The MEP lead executes
their part once the agreement exists.

**What the checker can actually see.** This has to be stated before any
authoring advice, because the fix must produce the evidence the gate reads
rather than the evidence a coordinator would intuitively supply.
`rules/epc-delivery/R-010.toml` declares two facets: an applicability facet
`entity = IFCBUILDINGELEMENTPROXY`, and a `shared-across-models` requirement
facet with `name_pattern = "^(origin|geo-reference)$"`. **Only the second is
executed.** The `completeness` checker walks every element of every model in the
project, keeps those whose **name matches that pattern** — `origin` or
`geo-reference`, nothing else — and passes a model when one of them carries a
**`global_id` that also occurs in at least one sibling model**. It never reads
`ifc_class`: declared applicability is compiled into an IDS document only for
IDS-checked rules, and R-010 is checked by `completeness`, so an element of any
class named `origin` would witness the pass identically. The witness the gate
actually reads is *a matching name carrying a shared GlobalId*.

That divergence between what the rule file declares and what the checker
executes is **registered as separate technical debt and nothing more.** It is
not Checkpoint C scope, not on any list of things Checkpoint C implements or
fixes, and not a dependency of anything in section 5; it is a standalone
follow-up against R-010, to be scheduled on its own terms. Nothing in this
branch changes the checker, the rules, the tests, contract 1.6 or any generated
artifact. It is stated here for one reason only: the honest reading of an R-010
pass depends on it. The evidence a pass carries is **a name plus a cross-model
GlobalId — a shared-marker witness — and that is its only admissible reading.**
It is not alignment evidence, and calling the witness "a named proxy" describes
what this project happens to have modelled rather than what was checked.

That is what `pcert-sample` carries. Two proxies satisfy it in all three
models: `2F44QMqSH3TOkM$SZoqCBe` named `origin` and `3Fit2Fad92zf2f6aWdJtF5`
named `geo-reference`. The published passes name the first by key —
`ddef6755-…` (hvac), `a02a738f-…` (architecture), `21999183-…` (structural).

**What the checker does not see, and must not be assumed to.** It compares
names and GlobalIds. It **does not compare coordinates, placements or
transforms**, and it never opens the geometry: `ElementGeometry` is computed only
for BCF viewpoint placement and is not consulted here. So an R-010 `PASS` proves
that a shared, identically-identified setout marker is present in the models —
not that those models are actually aligned. Two exports could each carry a proxy
named `origin` with the same GlobalId and still be placed kilometres apart, and
this rule would pass both. **Real shared-coordinate alignment remains a separate
confirmation**, done by overlaying the models or comparing the exported placement
against the agreed datum, and R-010 passing must never be reported as having
established it.

**Where to fix it at source.** Two things must both come out of the authoring
tool: the true coordinate alignment, and the witness that lets the gate see it.

*Alignment.* In Revit, acquire the project's survey point from the agreed
coordination file (*Manage → Coordinates → Acquire Coordinates*) and confirm the
project base point and true north match the coordination datum, then export IFC
with placement referencing that shared origin rather than the internal origin. In
Tekla Structures, set the model's base point to the agreed coordination base
point (*File → Project properties → Base points*) and mark it the IFC export
origin. The failure mode to avoid in both is "fixing" it by moving geometry: that
shifts the model without giving it a shared reference.

*Witness.* Alignment alone will not clear R-010, because nothing about acquiring
coordinates creates a named marker. Each discipline model must also **export the
agreed setout markers under the exact name `origin` and/or `geo-reference` —
`IfcBuildingElementProxy` being the entity this project models them as and the
rule file declares — carrying the same IFC GlobalId in every discipline
export.** The advice worth giving is about the required export outcome, because
that is what can be rechecked:

1. **The exported name matches exactly.** The pattern is anchored, so any
   prefix, suffix or type-name substitution introduced by the export mapping
   breaks the match.
2. **The exported GlobalId is the agreed one, in every discipline file.** This
   is the part most likely to go wrong: a marker re-drawn per model yields the
   right name and a fresh GlobalId, which the checker cannot see and which is
   the most common way a well-intentioned fix still fails.

How a given tool produces (2) belongs to that tool's export configuration, and
this document does not assert that any particular authoring workflow preserves
identity through export. Revit does expose an `IfcGUID` parameter and IFC export
mapping through which a chosen GlobalId and entity/name can be emitted, and
other authoring tools have their own mechanism; the mechanism used must be one
whose output has been verified, not one assumed to carry identity because the
object was copied, linked or monitored rather than re-drawn. **Verify per file
after export:** open each discipline IFC and confirm the marker's exported name
and that its GlobalId string is identical across the files. That identity — not
the marker's presence, and not the route it took through the authoring tool — is
what the gate reads.

**Recheck: what evidence would end the block.** R-010 returning `PASS` for
`iso-reference-view.plumbing` — a name-matching proxy whose GlobalId also occurs
in a sibling model. Since all three models in that project fail, the exit
condition applies to all three: the shared marker must appear in at least two
sibling models before any of them clears, because a GlobalId occurring once
cannot be shared with anything.

And the recheck does not stop at the gate. Because R-010 cannot see placement, a
`PASS` must be accompanied by the separate alignment confirmation described
above before anyone reports that the models federate correctly. The gate
establishes that a shared reference exists; a human still establishes that the
models sit on top of each other.

---

### Case 2 — BLOCKED *(live)*

*Can Architecture build room data sheets and equipment schedules from this
model?*

**Requirement and evidence.** R-005A/B, the project's assumed EPC asset
identity. Six failures across three HVAC elements, all `FAIL` / `WARNING` /
`is_issue = true`:

| `finding_key` | Element | Missing |
|---|---|---|
| `d0bdd588-2a41-5ddd-ab44-d7e59f99ed35` | `hvac::38WbwIGD90nB_3T2BTU5Ed` (`IfcDuctSegment`, *building element*) | `AssetTag` |
| `5454a69b-d62a-57a2-a9e7-a96a4c4a364a` | same duct | `SystemCode` |
| `31f9255b-fa9d-522b-8af2-e45bd33bb216` | `hvac::23uPJWDfXEcwHH3kdFgV9c` (`IfcAirTerminal`, *chimney cover*) | `AssetTag` |
| `9b6e100b-f05d-51cd-93cd-36f6b2597c70` | same air terminal | `SystemCode` |
| `90ea1aba-c7f0-5142-a123-f12e3c7c54f5` | `hvac::34Y6EIt3nDCAS1k$kPGOKm` (`IfcAirTerminal`, *house fireplace cap*) | `AssetTag` |
| `366d684e-8e45-53c7-8993-5299a27c6d39` | same air terminal | `SystemCode` |

Every one reports `actual` empty with reason *The required property set does not
exist* — the `EPC_Delivery` property set is absent altogether, not present and
blank. Grouped into three element-level issues
(`4461773b-4107-5a22-9c10-c9734cff0ecc`,
`b9692cb8-b7d4-5dd1-93a9-3e3835335337`,
`f26a49a6-cf44-59d5-9c66-ec58112a16fe`), each `model-coordination`, priority
`Medium`, stage Coordination, all `is_overdue = true`.

**Purpose impact.** Precisely bounded, and bounded to *one* activity. Room data
sheets and equipment schedules need *identity*, which is absent on three of the
six HVAC elements. Nothing about the geometry is in doubt, so this evidence says
nothing against ceiling layout or openings — and it does not release them
either. Ceiling layout is decided in case 3 on its own evidence and openings in
case 4 on theirs; identity evidence cannot stand in for position evidence, and a
case that spent this finding on all three activities would be the single
model-level verdict the scenario exists to avoid.

**Decision. BLOCKED** — for schedules and room data sheets, and for nothing
else. This is the definition applying exactly: a known unmet requirement — six
FAIL findings against R-005A/B — prevents the activity, because the identity the
activity is keyed on does not exist in the model. Architecture does **not**
start schedules or room data sheets keyed to MEP equipment, and the exclusion is
minuted so that a later reader does not assume the schedules exist and are empty
by choice. What Architecture *does* start is not settled by this case.

Two things this verdict is deliberately not. It is **not CONDITIONAL**: nobody
has accepted the risk of scheduling against absent identity, no release scope has
been named and no authoriser recorded, so there is nothing to write down as an
authorisation. And it is **not UNKNOWN**: the question was asked, the checker
answered it, and the answer is unacceptable. The severity on these requirements
is `WARNING`, which does not soften the verdict — as section 4 sets out,
`severity` is rule metadata and the activity verdict is a function of (evidence,
purpose). A schedule cannot be keyed to a tag that is not there, whatever the
rule author graded the rule.

**Blocker.** Missing `EPC_Delivery` property set on three MEP elements —
blocking for schedule production only.

**Business consequence.** Two kinds, no magnitudes — this repository holds no
cost, rate or duration data, and none is invented here. **Schedule and reference
work cannot start** while identity is absent. And if it is started anyway on
placeholder keys, there is **downstream re-identification and re-issue risk**:
rows keyed to something other than the asset tag have to be re-identified when
tags arrive, and any document quoting them re-issued. How many rows, how long
that takes and what it costs this project are runtime and Overlay questions
(section 5) and are not answerable from anything published today.

**Responsible role.** `model-coordination`, from the requirement metadata — the
right call, because the tag values come from the project's asset register rather
than from the MEP designer's head. The MEP lead applies them; they do not
originate them. Note this is what `owner_role` means: the role a *rule author*
expects to answer for the rule. It is an input to the manager's decision about
who acts, not the decision itself.

**Where to fix it at source.** In Revit, add a shared-parameter group named
`EPC_Delivery` containing `AssetTag` and `SystemCode` as instance text
parameters bound to Duct Accessories / Air Terminals / Duct Curves, populate
them from the project asset register (a schedule view is the practical bulk
path), and confirm the IFC export mapping emits them as an `EPC_Delivery`
property set rather than folding them into `Pset_ManufacturerTypeInformation` —
the current findings show the property set missing entirely, which is the
signature of an export mapping that was never configured. In Tekla, the
equivalent is a user-defined attribute set exported through the IFC export
additional-property-set definition.

**Exit condition.** All six findings returning `PASS` — that is, `EPC_Delivery`
present on all three elements with both properties non-empty — would lift the
block and make this activity READY. That is a future, not the current state.
Partial delivery is legible and useful here: were the duct to clear while the two
air terminals did not, the block would narrow to terminal-keyed schedules rather
than lifting, and duct-keyed schedule work would be READY on that scope alone.

---

### Case 3 — UNKNOWN *(live)*

*Can Architecture lay out ceilings and bulkheads around the MEP equipment?*

**Requirement and evidence.** R-004A and R-004B, spatial assignment, ERROR
severity, owned by `mep-lead`. All three evaluated HVAC elements pass:

| `finding_key` | Rule | Element | Storey |
|---|---|---|---|
| `4cd5d234-8820-5068-b957-c7c04f4f296b` | R-004A | `hvac::38WbwIGD90nB_3T2BTU5Ed` (`IfcDuctSegment`) | `00 groundfloor` |
| `12dc1e52-b4a8-5fd8-b650-222c2cf3060b` | R-004B | `hvac::23uPJWDfXEcwHH3kdFgV9c` (`IfcAirTerminal`) | `00 groundfloor` |
| `9b1eafbf-e3df-5c5d-9096-83ffbd2e4805` | R-004B | `hvac::34Y6EIt3nDCAS1k$kPGOKm` (`IfcAirTerminal`) | `00 groundfloor` |

All `PASS` / `INFO` / `is_issue = false`, reason *Requirement satisfied*.

**What that evidence carries, and what it does not.** It carries *in-model
position*: each of the three elements is assigned to a storey that Architecture
also models, so Architecture knows which storey to look in. It does not carry
*cross-model position*. Drawing a ceiling zone around a duct means placing
architectural geometry relative to MEP geometry, and that is only sound if the
two models sit on a common datum. The only evidence in this repository bearing
on that is R-010, and an R-010 pass establishes the shared marker witness
described in case 1 — a matching name carrying a GlobalId that also occurs in a
sibling model — and nothing about placement, coordinates or transforms. That
limit is stated in case 1 and it applies here: **this repository holds no
alignment confirmation for `pcert-sample`**, and the three passing R-010
findings must not be reported as one.

**Purpose impact.** The in-model position question is answered affirmatively for
the elements the rules reach. The cross-model position question underneath it is
answered by no current evidence — not favourably, not unfavourably, not at all.

**Decision. UNKNOWN** — for ceiling and bulkhead layout. This is the definition
applying exactly: the evidence needed to decide was never produced. No rule in
rule set 2.2 asks whether `hvac` and `architecture` sit on a common datum, so no
finding can answer it, and the passing R-004 and R-010 findings answer different
questions. Architecture cannot tell from anything published whether the models
overlay correctly or are metres apart, and neither release nor refusal can be
justified on that.

**Why this is not CONDITIONAL, which is the tempting mistake.** It would be easy
to write "start layout, conditional on alignment being confirmed later", and that
sentence *sounds* like a managed risk. Under the definition in section 1 it is
not one. A CONDITIONAL requires a named authoriser who accepted a named risk
against a named model version, with a release scope and a voiding condition
recorded. **This repository contains no risk acceptance, no authoriser and no
handover record.** Knowing the assumption is unverified is not the same as
someone having taken responsibility for it, and writing CONDITIONAL here would
manufacture an authorisation event that never happened. Until such a record
exists, the honest verdict is UNKNOWN.

**How it would become CONDITIONAL — counterfactual, not live.** A named
authoriser (the information manager, in this fixture's role vocabulary) accepts
the misalignment risk for a named release scope — say, ground-floor ceiling
zones only — against the named `hvac` and `architecture` versions issued, and
records the condition that voids the release: either model being re-issued, or
the alignment check coming back negative. All four of those are runtime records.
**None of them exists here, and none is invented.**

**How it would become READY — counterfactual, not live.** The R-004 passes above
joined by **a recorded alignment confirmation**: the two models overlaid, or
their exported placements compared against the agreed coordination datum, with
the confirming role and both model versions named. That is the only route from
UNKNOWN to READY for this activity. **That evidence does not exist in this
repository**, nothing in the current run may be cited as having supplied it, and
this paragraph is a description of absent evidence rather than of current state.

**Blocker.** None — and that is the point of the verdict. No requirement that
reaches this activity is unmet; the three that do reach it pass. What is missing
is an *evidence method nobody has run*, which is an UNKNOWN and not a BLOCKED.

**Business consequence.** Two kinds, no magnitudes. Ceiling and bulkhead layout
**remains suspended pending alignment evidence** — it is not released, so it is
not producing. And any layout done regardless **carries rework risk if alignment
later fails**: geometry set out against MEP positions that turn out to be
displaced has to be redone. How much geometry, how much time and what it costs
this project cannot be stated — no cost, rate or duration data exists in this
repository, and section 5 places those in Overlay cost parameters and runtime
data, neither of which is available. A team that recorded "R-010 passes" as
clearance would carry that same rework exposure without having noticed it.

**Responsible role.** `model-coordination` for producing the alignment
confirmation — the role R-010 itself carries, and for the same reason: a datum
is agreed between disciplines, not owned by one. Should the spatial assignments
regress, `owner_role` on R-004A/B is `mep-lead`. Note that whoever *produces* the
confirmation and whoever would *authorise* a release without it are two different
roles, and this repository names neither for this handover.

**Where to fix it at source.** Nothing to fix in the MEP model for R-004.
Preventatively: the passing condition is that every MEP element is assigned to a
level and space before export, which in Revit means avoiding unhosted or
unlevelled components in the MEP model. What ends the UNKNOWN is not a model fix
at all but an evidence method being run — the alignment confirmation — and the
source-side actions that make it come out right are case 1's: acquire the agreed
coordinates and export placement against them.

**Recheck.** Two things, on the next MEP issue: the three R-004 findings still
pass, *and* the alignment confirmation exists and is current for the versions
issued. Any verdict here is a statement about one version of two models and
expires when either is re-issued — this is the case most likely to be silently
assumed to persist.

**The honest limit.** The R-004 evidence covers *the three elements the rules
evaluate*, not the model. Case 4 is what that qualification is hiding.

---

### Case 4 — UNKNOWN *(live)*

*Can Architecture cut builder's work openings for MEP penetrations?*

This is not a fallback verdict. There is a specific element, with a specific
production consequence, on which the system says nothing at all. It shares its
verdict word with case 3 and not its evidence: case 3 is undecidable because an
evidence method was never run, this one because the rule set never asks the
question of the element that matters.

**The evidence gap.** The `hvac` model contains six elements. One of them is:

- `element_key` `hvac::3dkFAzOGrAIuOzY_RdrdVv`
- `ifc_class` **`IfcChimney`**, name *house - chimney*, storey `00 groundfloor`

That element produces **zero findings**. Not `N/A`, not `PASS` — it appears
nowhere in `findings.csv`. The reason is exact: R-004A is scoped to
`IfcDuctSegment` and R-004B to `IfcAirTerminal`, and no requirement in rule set
2.2 is scoped to `IfcChimney`. The element is present in `elements.csv`, so the
system knows it exists; nothing evaluates it.

A chimney is precisely an element that penetrates floors and roof. It is the
clearest builder's-work case in the model, and it is the one element the rules
do not reach.

Two further silences compound it, and both are real:

- Nothing anywhere relates an MEP element to an architectural one. Even for the
  ducts and terminals that *do* pass, no evidence says whether a penetration
  aligns with an architectural opening. `ElementGeometry` exists but is computed
  only for BCF viewpoint placement and is not exported or compared.
- The same shape appears in the sibling project:
  `iso-reference-view.plumbing::0Zk2_ch2P32wrl1QuECi58` (`IfcSanitaryTerminal`,
  unnamed, no storey) also produces zero findings.

**Purpose impact.** Unknown, and the unknown is the problem. Architecture cannot
tell the difference between "the chimney needs no opening" and "the chimney
needs an opening and nobody has checked". Both look identical in every current
output: a clean run with no finding.

**Decision. UNKNOWN** — openings work is neither released nor refused. It is
suspended pending evidence, and the suspension is recorded rather than resolved
by assumption. This is the only case that decides openings: no passing position
or identity evidence elsewhere in this handover releases them, because none of
it answers the openings question.

**Business consequence.** One kind, no magnitude: **openings work remains
suspended pending relationship evidence.** It is not released, so it is not
producing, and the suspension holds until the penetration question is answered
rather than until someone tires of waiting. What the suspension costs this
project in programme or effort is not stated, because no such data exists here.

**Which evidence is missing, exactly.** Three items, in priority order:

1. Whether `hvac::3dkFAzOGrAIuOzY_RdrdVv` is spatially assigned — the R-004
   question, never asked of this element because no rule is scoped to
   `IfcChimney`.
2. Whether the chimney penetrates an architectural element, and if so which one.
   No requirement in the rule set expresses a cross-model geometric
   relationship.
3. Whether a corresponding opening exists in the `architecture` model. Its 15
   elements are not checked for openings matching MEP penetrations.

**Who supplies each.** (1) is a rule-authoring action — the information manager
extends the rule set so `IfcChimney` is in scope; no model changes. (2) and (3)
need the MEP lead and Architecture lead together in a coordination review, since
neither model alone contains the answer.

**Scope of the unknown.** Bounded, not general: one element
(`hvac::3dkFAzOGrAIuOzY_RdrdVv`) in one model (`hvac`) in one project
(`pcert-sample`), plus the openings question for the two air terminals and one
duct that pass R-004 but have never been compared against architectural fabric.
**This** UNKNOWN does not extend to ceiling layout or to schedules: case 3
reaches its own UNKNOWN on entirely different evidence, and case 2 reaches
BLOCKED on evidence that has nothing to do with penetrations. Scope matters: an
unbounded UNKNOWN is indistinguishable from an excuse, and would let a team defer
everything behind one word.

**What ends the UNKNOWN.** The production question is *can Architecture cut the
builder's work openings*, so only evidence that answers **that** question ends
it. The three gaps are not interchangeable, and closing one does not close the
verdict:

- **Gap 1 alone is not an exit.** A requirement scoped to `IfcChimney` would
  make the chimney's spatial assignment inspectable, and that is worth having —
  it tells Architecture which storey to look in. But a `PASS` on spatial
  assignment says the element is assigned to a storey; it says nothing about
  whether it penetrates architectural fabric or whether an opening exists. A
  team that treated that `PASS` as a release would be cutting no openings on the
  strength of evidence about something else. Closing gap 1 narrows the UNKNOWN;
  it does not end it.
- **Either of these two answers does end it**, because either one answers the
  openings question:
  - **No penetration.** A recorded coordination-review determination that the
    chimney passes through no architectural element and requires no opening,
    with the reviewing roles named and the version of both models it was
    determined against. No model changes; the evidence is the decision. The
    verdict would then become READY for openings on this element.
  - **Penetration confirmed, with opening status.** The penetration relationship
    is established — which architectural element the chimney passes through —
    *and* the state of the corresponding opening is known. Opening modelled and
    cross-referenced → READY. Penetration confirmed with no opening → this
    ceases to be UNKNOWN and becomes BLOCKED with a named owner; it could become
    CONDITIONAL only if a named authoriser then accepted the risk for a named
    release scope against the named model versions. Either is a better outcome
    than not knowing.

Both of these are futures. Neither is the current state, and no evidence in the
present run stands in for either.

Note that the second path subsumes gaps 2 and 3 together: knowing there is a
penetration without knowing the opening's state leaves the production question
just as unanswerable as before, so partial closure there is not an exit either.

**Where to fix it at source.** Two separable actions. *For gap 1* — extend the
rule set to cover `IfcChimney`; a rule-authoring change, no model edit. If that
rule then fails, the model-side fix in Revit is to host the element to the
correct level so it reports an `IFCRELCONTAINEDINSPATIALSTRUCTURE` relationship
on export. *For gap 3* — model the opening in the **architectural** model as a
hosted opening or shaft against each storey the chimney passes through, rather
than as a void carried in the MEP model, so it exists in the discipline that
owns the fabric and can be pointed at.

**Recheck.** The recheck must cover **every gap still preventing the
judgement**, not whichever one was most convenient to close:

1. If the rule set was extended: the chimney now produces a spatial-assignment
   finding, and that finding passes. *(Necessary for confidence in the storey,
   not sufficient for openings.)*
2. The penetration question is answered — either a recorded determination of no
   penetration, or an established relationship naming the architectural element
   penetrated.
3. Where a penetration exists: the corresponding architectural opening is
   present and inspectably linked to the chimney.

Only when the set of open gaps is empty does the openings verdict leave UNKNOWN.
If (2) is answered "no penetration", (3) is closed with it and (1) remains
merely desirable; in every other combination all three must land.

**Why this is easy to get wrong.** The absence of a finding is invisible in every
count the system reports — 121 findings across 44 elements looks complete until
you notice which elements are missing from it. The tempting shortcut is to treat
the *appearance* of any finding on the chimney as the resolution, because it
makes the gap visible and visibly closed. It is not the resolution: a finding
appearing changes what the system can see, while the verdict depends on what the
team now knows about penetrations and openings. Making a gap visible and
answering the question are different achievements, and only the second releases
work.

---

## 4. Counterfactual: the same finding, a different purpose

Take one finding: `d0bdd588-2a41-5ddd-ab44-d7e59f99ed35`, R-005A `AssetTag`
missing on the duct `hvac::38WbwIGD90nB_3T2BTU5Ed`. It carries
`is_issue = true`, severity `WARNING`.

In **this** coordination purpose it is a real constraint: it is part of why case
2 is BLOCKED rather than READY — the identity a schedule is keyed on is not
there.

Now change the purpose without changing anything else. **Quantity take-off at
L1** asks a different question of the same model: how much duct is there, of
what material, to what dimension. The asset tag contributes nothing to that
answer. The identical finding, with the identical `is_issue = true`, is
**irrelevant** for quantity take-off — or at most a constraint on one slice of
it, if the project's cost breakdown structure happens to be keyed by system
code.

Two conclusions follow, and the second is the one that matters:

1. **`Finding.is_issue` must not be redefined as a global Purpose blocker.** It
   is a contract 1.6 validation fact meaning *this check failed in a way that
   warrants a topic*. It is already published, already load-bearing for the
   frozen legacy identity, and re-pointing it at a purpose verdict would move
   every number that depends on it — the failure mode AGENTS.md rule 6 exists to
   stop. The same argument applies to `severity`, `priority`, `stage`,
   `owner_role` and `labels`: all of them are rule metadata, none is a purpose
   consequence.
2. **The blocker verdict is a function of (finding, purpose), not a property of
   the finding.** It is new information that lives with the purpose. This is the
   single most important structural observation in this document — and it is an
   observation, not a design.

**No QTO Pack is designed here.** Quantity take-off appears only to prove that
one verdict per finding is insufficient. What a QTO purpose would require is out
of scope, unapproved, and not to be inferred from this paragraph.

---

## 5. Input to Checkpoint C

What the four cases actually needed, and nothing more. This is a list of
observations from walking one decision, not a schema, not a class model, not a
registry, and not a platform.

### The minimum that had to be recorded

1. **The purpose being served** — "MEP → Architecture coordination handover at
   Coordination". Every verdict above was meaningless without it; case 2 and
   case 4 differ only by which question was asked.
2. **The direction** — MEP → Architecture. Not derivable from any existing
   field. `discipline_scope` is applicability and carries no arrow.
3. **The production activities at stake** — ceiling layout, builder's work
   openings, schedules. Three, not one. Without these the verdict cannot be
   partial, and every real answer above was partial.
4. **Which requirements bear on which activity** — R-004A/B on in-model
   position, R-005A/B on identity, R-010 on the presence of a shared setout
   marker. Today this mapping exists only in this document's prose. Note that
   the mapping must also record what a requirement *cannot* answer: R-010
   witnesses a shared marker — a name plus a cross-model GlobalId — and is not
   evidence of alignment. Treating it as though it were is exactly how case 3's
   UNKNOWN would be talked up into a READY.
5. **A verdict per activity, and exactly one** — BLOCKED / CONDITIONAL / READY /
   UNKNOWN, with the meanings fixed in section 1. Three things this scenario
   demonstrates about that vocabulary. **UNKNOWN must be first-class**,
   distinguishable from READY, because case 4's silence currently looks exactly
   like success. **Neither READY nor CONDITIONAL is reached anywhere in this
   handover on current evidence** — the live verdicts are BLOCKED, UNKNOWN,
   UNKNOWN — and a vocabulary whose releasing verdicts are unreachable from the
   evidence at hand is telling you precisely what evidence is missing. And
   **CONDITIONAL cannot be computed from findings at all**: it requires a named
   authoriser, a named risk acceptance, a release scope and a voiding condition,
   which are records of a human decision and not derivations from a rule result.
6. **What the verdict rests on** — the specific `finding_key`s cited, *and* the
   named absence of a finding where one was expected. An absence has to be
   recordable, or case 4 cannot be expressed at all.
7. **The consequence of the verdict** — what Architecture stops or continues.
   Note carefully what this document could and could not say: the *kind* of
   consequence was always statable (work cannot start; re-identification and
   re-issue risk; rework risk if alignment later fails; work suspended pending
   evidence), and the *magnitude* never was. No money, duration or effort figure
   appears in any of the four cases, because none exists in this repository and
   inventing one would have been the easiest and least visible fabrication in
   the document.
8. **The role that acts** — distinct from the rule's `owner_role`, which is what
   a rule author expected rather than who this project tasks. Case 3 adds a
   second distinction: the role that *produces* a missing piece of evidence and
   the role that could *authorise* releasing work without it are not the same
   role, and a CONDITIONAL names the second.
9. **The exit condition** — what evidence ends the block, stated before the work
   starts so the recheck is not renegotiated afterwards.
10. **What the verdict was about** — named model versions. Case 3's verdict is
    true of one issue of `hvac` against one issue of `architecture` and expires
    when either is re-issued, and the alignment confirmation it waits on would
    have to cite both. Nothing today records that a handover happened, of what,
    on what date.
11. **The absence of an authorisation, as distinct from a refusal.** Case 3 is
    UNKNOWN and not CONDITIONAL for exactly one reason: no risk acceptance
    exists. Whatever eventually represents a verdict has to be able to say "no
    one has accepted this" without that collapsing into "someone said no".

### Where each item would come from

Walking the four cases separated three kinds of thing that are easy to conflate,
and the third is the one this document previously got wrong. **Reusable
question** belongs to a Purpose Pack. **Project policy and convention** belongs
to Project Overlay *configuration*. **What actually happened on a particular
assessment of particular models** belongs to neither: it is runtime assessment
evidence and decision, produced by a run, not configured in advance.

The distinction matters because Overlay configuration is written once and read
many times, while runtime evidence is produced per handover and is only true of
the versions it was produced against. Filing an alignment confirmation or a risk
acceptance as Overlay configuration would make a statement about two specific
model versions look like a standing project setting — which is how case 3's
UNKNOWN would quietly turn back into a CONDITIONAL nobody authorised.

| # | Item | Contract 1.6 today | Purpose Pack (reusable) | Overlay *configuration* | Runtime assessment evidence / decision |
|---|---|---|---|---|---|
| 1 | Purpose identity | — | ✔ | — | — |
| 2 | Direction (MEP → Architecture) | — | ✔ | — | — |
| 3 | Production activities at stake | — | ✔ | — | — |
| 4 | How requirements and evidence bear on an activity, including what a requirement *cannot* answer | — | ✔ | — | — |
| 5 | Verdict semantics (READY / CONDITIONAL / BLOCKED / UNKNOWN) | — | ✔ | — | — |
| — | Reusable consequence *kinds* | — | ✔ | — | — |
| — | Default responsibility policy | — | ✔ | — | — |
| — | Source-fix and recheck guidance | — | ✔ | — | — |
| 6a | Findings and their status | ✔ `finding_key`, `status`, `severity`, `is_issue` | — | — | which findings a given assessment actually cited |
| 6b | A *named absence* being admissible evidence | — | ✔ (that it counts) | — | the absence actually observed in a run |
| 7 | Business consequence | — | ✔ (kind) | ✔ (cost parameters) | the impact actually recorded |
| 8 | Acting role | partly — `owner_role` is an input | ✔ (default policy) | ✔ (team / role mappings) | who actually acted |
| 9 | Exit condition | partly — a requirement passing is expressible | ✔ (what would end it) | ✔ (evidence methods this project accepts) | whether the exit was actually met |
| 10 | Model versions and the handover issue/event | partly — `models.csv` has a content hash | — | — | ✔ the versions actually issued, and when |
| 11 | Risk authorisation | — | — | ✔ (who may accept what, and how) | ✔ the risk acceptance actually given, by whom, over what scope |
| — | The alignment confirmation | — | — | ✔ (what method counts as one) | ✔ the confirmation actually performed |
| — | The verdict, blocker, authoriser and exit status | — | — | — | ✔ all of it |
| — | R-005 asset-tag convention and any permitted overrides | ✔ as a rule today | **never** | ✔ belongs here | — |
| — | Milestone dates | ✔ `project_milestones.csv` | — | — | — |

Four things this table is asserting, each of which the audit should test:

- **The core does not move.** Every contract 1.6 column above is read, never
  redefined. No new meaning is attached to `is_issue`, `severity`, `priority`,
  `stage`, `owner_role`, `labels` or `discipline_scope`.
- **Project-specific agreements go to the Overlay.** R-005's `EPC_Delivery`
  properties are one project's convention, along with whatever overrides the
  project permits against them. A Pack core carrying them would export one
  client's naming as a universal coordination truth.
- **The Pack carries the reusable question; the Overlay carries the project's
  policy; neither carries the run's answer.** Which activities depend on which
  requirements generalises and is Pack data. This project's rates, its role
  mappings, which evidence methods it accepts and who may accept risk are
  policy, written in advance, and are Overlay configuration. The alignment
  confirmation that was actually done, the risk that was actually accepted, the
  versions actually issued and the verdict actually reached are none of those —
  they are outputs of an assessment.
- **Runtime assessment evidence and decisions are not Overlay configuration.**
  This is the correction: an earlier reading of this document filed the actual
  cost, the actual acting role and the actual handover event under Overlay,
  which would have made a per-run result look like a project setting.

**The rightmost column is an observation, not a design.** It records what the
four cases turned out to need; it does not define a class, a schema, a table or
a candidate assessment object, and nothing in it may be read as proposing one.
Naming those is Checkpoint C's decision to make or to refuse.

### Deliberately not decided here

How any of this is represented; what is a table, a file or a type; how a Pack is
identified, versioned, discovered or validated; how an Overlay composes with a
Pack; how a verdict is computed, exported or rechecked; whether any of it enters
`default_registry`. Those are Checkpoint C's questions and later.

One boundary is worth restating because it is already settled and easy to erode:
if a purpose assessment is ever built, it is approved **between `check` and the
compatible group** — after facts are validated, before findings become issues —
and it is not a `Checker`, a `GroupingPolicy` or an `Exporter`. See the seam
discussion in `AGENTS.md`.

---

## Provenance

Every identifier in this document was read from `data/processed/canonical/` at
contract 1.6 (rule set 2.2), the state tagged `contract-1.6`: 2 projects,
6 models, 44 elements, 121 findings, 21 issues. The `hvac` model's six elements,
the three zero-finding elements, and every `finding_key`, `issue_key` and
`requirement_key` cited are current as of that run and can be checked against it
directly.

This is a design scenario written against this repository's public
buildingSMART worked example. The role names are the fixture's; the production
consequences are the author's reasoning about how such a handover is decided.
