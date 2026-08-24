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
the same model can be usable for (1) subject to one named condition, unusable
for (3) for an entirely unrelated reason, and unassessed for (2) — all at once.
Each activity is decided in exactly one place, on the evidence that bears on
*it*; evidence answering one question is never spent releasing another. This is
the central production observation of the whole scenario, and section 3 shows it
happening.

### What a manager actually approves or refuses

The information manager chairing the coordination review is not approving a
model. They are approving, refusing or qualifying **a release of Architecture's
own labour**:

- *Approve* — Architecture starts ceiling layout on this MEP issue, and accepts
  the rework risk if the MEP model later moves.
- *Refuse* — Architecture does not start; the MEP lead re-issues; the
  Architecture team is redeployed this week and the programme absorbs it.
- *Qualify* — Architecture starts the parts that are safe and explicitly does
  not start the parts that are not, with the exclusions written down so nobody
  later assumes they were done.

That third option is the one that matters commercially and the one a pass/fail
gate cannot express. A system that only says PASS or FAIL forces the manager to
either stop work that could have proceeded or start work that will be redone.

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

Five requirements in rule set 2.2 bear on this handover. All five are real and
current:

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
the current run. One question gets one verdict: no case releases or refuses an
activity that another case decides, and where a case's evidence is silent about
another activity that silence is recorded rather than spent.

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

The BLOCKED shape is nevertheless worth walking, because the whole point of the
scenario is that the four verdicts must be distinguishable, and a verdict with no
worked example is an assertion. The one available instance of this failure lives
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

**Purpose impact — in the counterfactual.** Total. Every one of the three
downstream activities assumes the MEP model can be placed next to the
architectural one. Without a shared setout reference it cannot be placed at all,
so ceiling layout, openings and schedules would all be unreachable. Note the
*other two* models in that project fail the same rule (`cb599b72-…`
architecture, `85360128-…` structural): it is a project-wide federation failure
there, not one discipline's mistake.

**Decision. BLOCKED** — for `iso-reference-view`. The corresponding decision for
this scenario's handover is *not blocked*; see case 3.

**Blocker.** No coordination reference shared with any sibling model.

**Business consequence — what it would cost, were this the project.** An
Architecture team allocated to ceiling layout would have no work it could safely
start. Coordination geometry produced against an assumed origin would be
discarded when the true setout arrived — rework created by proceeding rather
than by waiting. The `iso-reference-view` Coordination milestone is also
`2026-08-01T00:00:00Z` and its issue is flagged `is_overdue = true` at the run's
`as_of`, so in that project the block is consuming float that has already run
out. None of this is a cost being carried by `pcert-sample` today.

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
executes is **recorded here and not acted on.** It is an observation about the
strength of R-010's evidence, carried into Checkpoint C as one; nothing in this
branch changes code, rules or schema, and contract 1.6 is not reopened. It is
stated because the honest reading of a pass depends on it — calling the witness
"a named proxy" describes what the project happens to have modelled, not what
was checked.

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

### Case 2 — CONDITIONAL

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

**Purpose impact.** Partial, precisely bounded, and bounded to *one* activity.
Room data sheets and equipment schedules need *identity*, which is absent on
three of the six HVAC elements. Nothing about the geometry is in doubt, so this
evidence says nothing against ceiling layout or openings — but it does not
release them either. Ceiling layout is decided in case 3 on its own evidence and
openings in case 4 on theirs; identity evidence cannot stand in for position
evidence, and a case that spent this finding on all three activities would be
the single model-level verdict the scenario exists to avoid.

**Decision. CONDITIONAL** — for schedules and room data sheets, and for nothing
else. Architecture does **not** start schedules or room data sheets keyed to MEP
equipment, and the exclusion is minuted so that a later reader does not assume
the schedules exist and are empty by choice. What Architecture *does* start is
not settled by this case.

**Blocker.** Missing `EPC_Delivery` property set on three MEP elements —
blocking for schedule production only.

**Business consequence.** Contained if the condition is honoured, expensive if
it is not. A schedule built now would key rows to element GUIDs; when asset tags
arrive, every row must be re-keyed by hand and any downstream document quoting
those rows re-issued. Deferring the schedule costs the days between now and the
tag delivery. Starting it costs those days *plus* the re-key, and risks a
document going out with placeholder identities.

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
present on all three elements with both properties non-empty. Partial delivery
is legible and useful here: if the duct clears and the two air terminals do not,
the condition narrows to terminal-keyed schedules rather than lifting.

---

### Case 3 — CONDITIONAL

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

**Purpose impact.** The position question is answered affirmatively for the
elements the rules reach. The federation question underneath it is answered by
no current evidence.

**Decision. CONDITIONAL** — for ceiling and bulkhead layout, on these three
elements. Architecture starts layout on the explicit condition that the
shared-coordinate alignment of `hvac` and `architecture` is confirmed
separately, by the overlay-or-datum check case 1 describes, naming the confirming
role and the model versions it was made against. Until that confirmation is
recorded, the layout proceeds on an unverified assumption, and the assumption is
minuted with the work rather than absorbed into it.

**The READY case, as an evidence-qualified counterfactual.** This activity is
the nearest thing in the scenario to a READY, which is exactly why the missing
evidence is worth naming instead of rounding away. It would become READY when
the R-004 passes above are joined by **a recorded alignment confirmation**: the
two models overlaid, or their exported placements compared against the agreed
coordination datum, with the confirming role and both model versions named.
**That evidence does not exist in this repository.** The paragraph describes what
is absent, not what is in hand, and nothing in the current run may be cited as
having supplied it.

**Blocker.** None outstanding against the issued MEP model — the three
requirements that reach it pass. The condition rests on a piece of evidence that
has not been produced, not on a defect to be fixed.

**Business consequence.** Architecture starts ceiling layout this week rather
than idling, which is the value of splitting the verdict: refusing the whole
handover because R-005 fails would have stopped this work for a reason that has
nothing to do with it. The cost of the condition failing is bounded and
knowable — if the models prove misaligned, the ceiling geometry set out this
week is set out against the wrong MEP positions and is redone. Minuting the
condition is what makes that a managed risk; a team that recorded "R-010 passes"
as clearance would carry the identical exposure without knowing it had.

**Responsible role.** `model-coordination` for the alignment confirmation — the
role R-010 itself carries, and for the same reason: a datum is agreed between
disciplines, not owned by one. Should the spatial assignments regress,
`owner_role` on R-004A/B is `mep-lead`.

**Where to fix it at source.** Nothing to fix in the MEP model for R-004.
Preventatively: the passing condition is that every MEP element is assigned to a
level and space before export, which in Revit means avoiding unhosted or
unlevelled components in the MEP model. For the alignment condition the
source-side actions are case 1's — acquire the agreed coordinates and export
placement against them.

**Recheck.** Two things, on the next MEP issue: the three R-004 findings still
pass, *and* the alignment confirmation is current for the version issued. Any
verdict here is a statement about one version of one model and expires when the
model is re-issued — this is the case most likely to be silently assumed to
persist.

**The honest limit.** The R-004 evidence covers *the three elements the rules
evaluate*, not the model. Case 4 is what that qualification is hiding.

---

### Case 4 — UNKNOWN

*Can Architecture cut builder's work openings for MEP penetrations?*

This is not a fallback verdict. There is a specific element, with a specific
production consequence, on which the system says nothing at all.

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
The UNKNOWN does not extend to ceiling layout, which case 3 decides, nor to
schedules, which case 2 decides. Scope matters: an unbounded UNKNOWN is
indistinguishable from an excuse, and would let a team defer everything.

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
    determined against. No model changes; the evidence is the decision. Verdict
    becomes READY for openings on this element.
  - **Penetration confirmed, with opening status.** The penetration relationship
    is established — which architectural element the chimney passes through —
    *and* the state of the corresponding opening is known. Opening modelled and
    cross-referenced → READY. Penetration confirmed with no opening → this
    ceases to be UNKNOWN and becomes a BLOCKED or CONDITIONAL case with a named
    owner, which is a better outcome than not knowing.

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

In **this** coordination purpose it is a real constraint: it is why case 2 is
CONDITIONAL rather than READY, and if the project's schedule production were on
the critical path it would be blocking rather than qualifying.

Now change the purpose without changing anything else. **Quantity take-off at
L1** asks a different question of the same model: how much duct is there, of
what material, to what dimension. The asset tag contributes nothing to that
answer. The identical finding, with the identical `is_issue = true`, is
**irrelevant** for quantity take-off — or at most conditional, if the project's
cost breakdown structure happens to be keyed by system code.

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
   witnesses a shared marker and is not evidence of alignment, and treating it
   as though it were is how a CONDITIONAL silently becomes a READY.
5. **A verdict per activity, and exactly one** — BLOCKED / CONDITIONAL / READY /
   UNKNOWN. Two things this scenario demonstrates about that vocabulary.
   **UNKNOWN must be first-class**, distinguishable from READY, because case 4's
   silence currently looks exactly like success. And **READY is not awarded
   anywhere in this handover on current evidence**: ceiling layout comes closest
   and still lands CONDITIONAL, because the alignment confirmation it would rest
   on does not exist in this repository. A vocabulary whose top verdict is never
   reachable from the evidence at hand is telling you what evidence is missing.
6. **What the verdict rests on** — the specific `finding_key`s cited, *and* the
   named absence of a finding where one was expected. An absence has to be
   recordable, or case 4 cannot be expressed at all.
7. **The consequence of the verdict** — what Architecture stops or continues,
   and the cost of getting it wrong. This is the manager's actual input and
   appears nowhere in the system today.
8. **The role that acts** — distinct from the rule's `owner_role`, which is what
   a rule author expected rather than who this project tasks.
9. **The exit condition** — what evidence ends the block, stated before the work
   starts so the recheck is not renegotiated afterwards.
10. **What the verdict was about** — a named model version. Case 3's verdict is
    true of one issue of `hvac` and expires when it is re-issued, and the
    alignment confirmation its condition names would have to cite the versions
    of *both* models it was made against. Nothing today records that a handover
    happened, of what, on what date.

### Where each item would come from

| # | Item | Existing `Finding` / contract 1.6 | Future Purpose Pack | Future Project Overlay |
|---|---|---|---|---|
| 1 | Purpose identity | — | ✔ | — |
| 2 | Direction (MEP → Architecture) | — | ✔ | — |
| 3 | Production activities at stake | — | ✔ | — |
| 4 | Requirement → activity mapping | — | ✔ | — |
| 5 | Verdict per activity | — | ✔ (rules) | — |
| 6a | Evidence: findings cited | ✔ `finding_key`, `status`, `severity`, `is_issue` | — | — |
| 6b | Evidence: a *named absence* | — | ✔ | — |
| 7 | Business consequence | — | ✔ (kind) | ✔ (this project's cost) |
| 8 | Acting role | partly — `owner_role` is an input | ✔ (default) | ✔ (project's actual assignment) |
| 9 | Exit condition | partly — a requirement passing is expressible | ✔ | — |
| 10 | Model version / handover event | partly — `models.csv` has a content hash | — | ✔ |
| — | R-005 asset-tag requirement itself | ✔ as a rule today | **never** | ✔ belongs here |
| — | Milestone dates | ✔ `project_milestones.csv` (contract 1.6) | — | — |

Three things this table is asserting, each of which the audit should test:

- **The core does not move.** Every contract 1.6 column above is read, never
  redefined. No new meaning is attached to `is_issue`, `severity`, `priority`,
  `stage`, `owner_role`, `labels` or `discipline_scope`.
- **Project-specific agreements go to the Overlay.** R-005's `EPC_Delivery`
  properties are one project's convention. A Pack core carrying them would
  export one client's naming as a universal coordination truth.
- **The Pack carries the question; the Overlay carries the project's answer.**
  Which activities depend on which requirements is a property of the *purpose*
  and generalises. What it costs this project when they are not met, and who
  this project tasks with fixing it, does not.

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
