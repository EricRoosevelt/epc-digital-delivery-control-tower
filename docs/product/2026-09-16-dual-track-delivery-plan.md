# Product commission: Framework + BIM Doctor

Decision date: 2026-09-16. Owner: Product Manager.
Approved direction: parallel product experience and engineering, not parallel
sources of domain truth. This document issues original product requirements;
the Technical Director still owns implementation packets and exact bases.

## Baseline and user

PR #10, E1, merged at `f06bab01939906d9231a56a7157de7136fe7b1ce`.
The reviewed head was `017738bf6ddb68a6974972f97d88ebaa7c7a58c8`.
The policy resolver exists; promotion consumption does not. Shipped pcert-sample
still has nine illustrative policy rows and cannot produce a real assessment.
Lifting its staffing gate alone does not guarantee evaluation: consuming a
determination can encounter the separate method-policy gate. The authorisation
gate has no runtime consumer before E2. These are different limitations.

Our first user is a BIM subcontractor's BIM manager using Revit. The decision
is: what needs attention before this specified model handoff, why, where should
the team correct it, and what changed after resubmission? The initial experience
is a visible preflight workbench, not a CLI and not a compliance certificate.
No target-company deployment, model, policy or customer validation is claimed.

The user can later supply a complete Revit model from another source. Its
licence, confidentiality, links and version still need intake review. We have
no client checklist. Singapore sources seed a candidate checklist, not an
assertion that a particular project must satisfy every item.

## Working agreement

- PM original requirement -> BIM domain constraints -> Tech packet -> engineer
  -> Tech audit -> BIM domain audit through the user -> PM closure.
- One Technical Director integrates both tracks. Maximum implementation WIP:
  one core checkpoint plus one UI checkpoint, in separate worktrees.
- Add one Product/UI Engineer; no additional research or architecture agent.
  PM prepares sources, BIM checks their domain applicability.
- UI design need not wait for CONDITIONAL, storage, CLI or public contracts.
  A thin, explicitly internal adapter is permitted after Tech approval;
  Framework Engineer owns it. No public compatibility promise is implied.
- UI owns presentation only. Existing Framework results remain authoritative.
  Ordinary visual changes need proportionate review, not repeated full domain
  design rounds. Changes to scope, evidence or verdict meaning do need BIM.
- Preserve published artifacts and illustrative project policies. Neither a
  attractive demo nor an adapter justifies changing their meaning.

## S1 — Singapore source and candidate-checklist review, open now

Purpose: let the manager understand what a proposed preflight covers and what
it cannot establish. PM owns the initial [source register](singapore-preflight-source-register.md)
and [13-item candidate checklist](singapore-preflight-candidate-checklist.md).

BIM returns a disposition for each candidate: suitable for initial automation,
human review, defer, or reject, with a source section and applicability rationale.
These are research dispositions, not new runtime outcomes. Review the actual
downloaded edition before accepting a property, enumeration, threshold or schema
rule. Public access is not a redistribution licence. Do not copy third-party
assets into the repository outside its intake gate.

Acceptance: every retained check has a specific source/version, applicability,
required input, observable failure and false-positive counterexample, source-fix
route and review owner. Clearly separate legislation, submission requirements,
recommended modelling practice, and our own product checks. No claim of complete
Singapore coverage. Stop at a reviewed shortlist; machine rules and a new Pack
require the next explicit commission. Do not force a new purpose into the
existing coordination Pack merely to reuse its name.

## D1 — Doctor user-flow design, open now

Original requirement: a non-programmer can select a model version, declare the
scope and intended handoff, inspect blockers or evidence gaps, understand the
source correction, and compare a recheck without reading JSON or using a CLI.

Deliver a compact screen-flow proposal, key states, and the data needed from
Framework. Layout and decomposition are the UI engineer's choice. Cover:

1. Model/version, explicit scope, purpose and checklist selection.
2. Results with affected members, evidence, excluded scope and unassessed work.
3. Detail with source reference, corrective action and recheck expectation.
4. Revision comparison distinguishing a better verdict from a proved discharge
   of an old recheck condition; explain evidence invalidated by model reissue.

Acceptance scenarios: navigate from a scoped result to its evidence and fix;
find a zero-finding member that still needs evaluation; distinguish refusal
from an empty successful run; observe a model-reissue evidence gap. A manager
must be able to explain what was and was not checked from the screens alone.
Internal role-play is useful but is not target-user validation.

Keep two clearly separated experiences: labelled fixture demonstration of
implemented Framework behaviour, and real input with its actual refusals.
Candidate Singapore checks are visibly unimplemented until integrated and tested.
Simulated policies must not become formal project decisions or exportable real
assessment records. Do not silently switch a refused real run to fixture mode.
No aggregate readiness score, invented assignee, or regulatory approval badge.

Stop at design review by Tech, BIM and PM before a retained UI implementation.
Tech may investigate the smallest internal adapter alongside this design; report
its data source and unsupported states. Do not make the UI recompute verdicts.
The full public machine contract is not a prerequisite for this prototype.

## F-next — E2 design adjudication, open now; implementation not yet open

Original requirement: define the smallest trustworthy first risk-authorisation
event on an existing assessment, without confusing a role-policy match with a
real person's authority or changing the underlying evidence-based verdict.

BIM supplies domain input first. Tech returns one recommendation plus unresolved
product choices, using the existing E2 numbering rather than renaming later work.
Resolve or explicitly block on: party identity and authority evidence; what
proves evidence unchanged for authorisation versus recheck; exact member-pair
release scope; the boundary between a first promotion and later continuation,
terminal invalidation and exhaustive enumeration. Preserve the existing
rejection behaviour unless a separate product decision approves a change.

Account for the inherited alignment-signatory fixture convention before using
it as proof of legitimate authority. Show that an unsuccessful promotion cannot
erase an independently valid ordinary assessment. Update the stale ADR 0003
section 10.1 item 1 account of E1 without claiming that E2 already exists.

Acceptance: a reviewable event example and counterexamples for changed evidence,
wrong party, partial pair scope and failed policy consumption; explicit mapping
of prerequisites to E2/E2.5/E3/E4. A fixture can demonstrate mechanics, never a
real coordination decision. No identity platform, storage subsystem, public API
or full authorisation lifecycle is commissioned here. Stop for PM adjudication.

## Next integration stop and forecast

Forecasts from 2026-09-16, conditional on agent availability and review:

| Target | Deliverable | Owner / dependency |
| --- | --- | --- |
| September 18 | S1 domain shortlist; D1 screen flow; E2 design choices | BIM / UI / Tech, parallel |
| September 23 | First clickable internal Doctor prototype | Separate commission after D1 and adapter approval |
| September 30 | One source-fix/recheck demo using an admitted model | Model intake, supported checks and mapping spike must pass first |

The user need not provide the Revit model for D1. Request it at the next model
intake/integration checkpoint, with Revit version, linked-file inventory and
permission to process it. First investigate Revit export to IFC plus reliable
version-bound source-element mapping. No native RVT ingestion, clickable Revit
navigation, automatic writeback or cloud upload is promised before that probe.
ACC, Navisworks and other connectors remain deferred until the actual receiving
workflow is known. A missing model postpones real-data validation, not UI design.

At the next PM review, judge visible usability and verified technical meaning
together. Keep an explicit list of simulated, implemented and unimplemented
capabilities. E2.5/E3/E4 remain closed; these dates do not authorise them.
