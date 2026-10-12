# BIM Doctor main-path UX contract

Visual ownership: [DESIGN.md](DESIGN.md), runtime `doctor/static/doctor.css`. This is the user-approved direction implemented for independent candidate review, not evidence of review completion.

## Business-context sources

| Concern | Source |
|---|---|
| Approved implementation scope and continuity | PM implementation decision dated 2026-10-12; implementation plan under docs/product |
| Validation versus readiness, missing objects and public bytes | AGENTS.md; existing domain contracts and adapter/envelope shapes |
| Result limits, source-edit mapping and scoped READY | Existing vocabulary/local wording tables; same-day BIM preview review; candidate's incremental wording report |
| Check submission/refusal/storage behavior | Existing `local-check.js`, Doctor loopback APIs and local-check tests |

The maintainer's PM/UX/BIM input files are local review evidence; they are not copied into runtime data. No permissions, billing, assignment, deletion or authentication flow is added.

## Canonical UI Map

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Table Selection | workspace-screens.js + app.js focusMain | Existing finding routes and this contract | Single result; local compact name/status versus full workspace/compare columns | Browser list/detail/return/filter matrix |
| Select/Listbox | local-check.js native select | Existing declared-discipline choices | Native OS popup; existing rule-set select | Actual selection/popup and check flow |
| Form | local-check.js sections and labelled native controls | Existing stage/plan/check APIs | File input, explicit scope/check buttons; no form validation popup | Real multi-file, refusal and recovery |
| Scrollbar | doctor.css global baseline | DESIGN.md | Document vertical scrolling; natural table horizontal overflow | Computed styles, no internal vertical overflow, phone |

Date, Toast and CRUD capability systems are not introduced. Existing local check creation is the existing explicit submission flow, not a new generic CRUD framework. No form element or browser reportValidity/confirmation dialog is used.

## State and navigation

Actual routes and IDs remain canonical. Example items stay independent routes/deep links; same-item recheck keeps existing correspondence rules. Language reload changes only lang, retains route/object, and restores same-check local query/status/selection through a one-use tab-local handoff consumed and removed before rendering. Ordinary typing writes nothing to storage. No query enters shareable URLs, localStorage or a durable session record, and ordinary refresh restoration is not promised. Another check/run resets the view.

Local phone finding routes show detail alone at <=700px. Visible Back and browser Back return to the list; query/selection remain for the same check. Selected row's name link gets visible focus; if filtered out, focus goes to search. The document scrolls to that target, not to a promised prior pixel coordinate. New objects focus their own heading. Locate/skip/results jumps do not replace router hashes.

## Lists and results

Returned finite adapter datasets render in full; this task does not add paging or remote search. Status filtering and name/Tag/GlobalId local search change visible rows only. Empty filtered rows are not model-level N/A or a pass. A labelled explicit Clear restores all query matches and input focus, preserving the independently chosen status filter. Composition input waits for compositionend. A retained desktop detail outside its filter is labelled as such.

Example registers preserve source/absence provenance and work/verdict together. The complete unit/count explanation is in the existing reading disclosure; the open statement next to counts says items are not defects. Quiet records remain reachable with each record's scoped READY/source limits. Returning to a quiet record opens that disclosure so focus stays visible. Record model-version context is available as actual recorded fields, never derived from software version.

## Reading limits and trace

FAIL is only the actual requirement's result. PASS retains what it proves/does not and never exposes an invented observed value. Model-level N/A names the actual model and is not a pass. Missing or unknown fields stay explicit. Actual selected finding's model supplies filename/class/storey/Tag/GlobalId and run trace; no first-model or PV-001 assumption is introduced.

For known local PV-001 FAIL, checker-read explanation and raw observations may fold. Modification-before-object-check, source mapping unknown, type-instance impact, undecided value/actor and recheck instruction remain open. Other statuses/rules keep their existing explanation branches. Mobile finding view may hide repetitive list title/exercise/summary; local mode, input identity and per-result limitations remain in the detail itself.

## Submission and failures

Existing stage/plan/check requests remain pessimistic, labelled and duplicate-disabled. Refusals and program faults remain separate; no success claim before an actual server result. No upload cancellation, offline queue, retry policy, security permission or dependency change is added. Existing input values/recovery remain; the shared shell does not redefine lifecycle behavior.

## Verification

Use the project venv and mandatory pinned IDS audit for all AGENTS gates. Explicit browser commands require externally available Playwright/browser and an isolated server/checks directory; they are not silently substituted by static audits. `doctor_ui.browser.cjs`, `doctor_mobile_search.browser.cjs`, state-matrix browser evidence and `test_doctor_view_state.py` cover navigation/continuity. Full TD/UX/BIM review, real-device/IME/screen-reader and full WCAG claims require their own evidence.
