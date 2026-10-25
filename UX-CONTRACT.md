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

## Real IFC review workspace

The authorized 2026-10-24 product scope adds `/review.html` and the `ReviewStore` HTTP contract under `/api/review/`. This is a named operational variant, with the existing record/check paths preserved. The homepage recommends the new workbench and keeps both prior paths reachable.

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Table Selection | review.js selected finding and element state | ReviewStore element_key/finding_id | Single finding; direct 3D selection chooses its relevant finding | doctor_review.browser.cjs list/pick/detail |
| Select/Listbox | review.js native select controls | ReviewStore models/status/severity | OS popup accepted, labelled model/result/per-element rule | Browser selectOption, keyboard/native popup |
| Form | review.js file input and load actions | POST /api/review/imports raw IFC, client job ID and short status polls | One .ifc up to server limit; explicit picker; duplicate-disabled | Real Building-Hvac.ifc upload and confirmed job cancellation |
| Scrollbar | doctor.css global baseline | DESIGN.md | Bounded issue register; naturally growing detail and document | Desktop/390px overflow inspection |

Search is local and IME-safe, with an explicit clear that restores input focus. Search and filters remain transient in memory and do not put private object names into URLs/storage. Review/revision/finding IDs are retained in the URL for language reload and record reopening. A requested finding chooses its corresponding result filter; otherwise reload starts from the first relevant issue. The register renders 100 results initially and explicitly loads the next 100, with a visible total. Initial results prefer severity ERROR + FAIL, labelled Needs review; when none exist, they show INFO + FAIL, then PASS, or all results when neither applies. Selection starts inside that initial filter. Information is labelled neutrally throughout list, per-element rule select and evidence. The stored rule status remains evidence, not an overall release conclusion.

The list and 3D stage use model-qualified element_key. Selecting another element cancels prior advice; late results cannot replace the current selection's advice. Model filters hide meshes without changing source geometry or report records. A selected item outside a filter retains readable detail and an explicit notice. Geometry-less elements retain identity, every result and advice, with focus/isolation disabled. Camera buttons offer a non-drag alternative to orbit/zoom. Display all includes source reference helpers; reset returns to the main spatial cluster.

Requests are pessimistic, duplicate-disabled, abortable and time-bounded. Failed model loads preserve the prior report. Failed geometry/WebGL leaves result reading available and offers retry. No estimated percentage or fabricated geometry appears. Advice labels the server-returned mode, renders all evidence as text and has a retry state. Local guidance sends no AI request. The explicit AI action sends the current finding's minimal evidence through the server, with the visible notice that IFC/geometry are not sent. API configuration is not presented as a successful provider connection.

IFC uploads use server jobs with a client-generated ID known before submission. A cancel request remains pending until the server reports a terminal state; prior report and mesh stay readable. Stage names and tessellated-element counts come from the job descriptor, including elements without geometry. Lost submit/status responses can resume the known ID; terminal failure/timeout retries create a fresh ID. Late results from superseded loads cannot replace the current view. Individual HTTP requests have a 30-second deadline; native import duration is controlled by the worker job, not a long browser POST.

Page departure and language reload send a best-effort keepalive cancel only for this page's active job. They do not claim confirmation, cancel another page's task or re-upload on return; the server hard deadline bounds undelivered cancellations.

A geometry/viewer failure does not display Model loaded as the final status and does not relabel a server-renderable element as geometry-less. The original exception, request ID, request/decode/initialize/load phase and observed WebGL context events are retained in an expandable technical detail and local console for diagnosis. Successful HTTP responses with unreadable JSON propagate their parse error instead of silently becoming an empty result. The existing browser regression exercises HTTP geometry failure, malformed JSON and actual retry recovery.

`tests/doctor_review.browser.cjs` is the real-server integration check, including deliberately failed transport recovery. It stores new evidence under `docs/evidence/product-phase1/` without recapturing historical snapshots.

## Persistent project and revision workflow

The 2026-10-25 product scope adds the `ProjectLibrary` `/api/projects` contract and the BIM revision comparison response. Saved project/revision/follow-up identities come only from that service. Project names are human labels; project/model/revision IDs identify records. The store persists reports and mesh snapshots, not a downloadable copy of the original IFC bytes. Existing pipeline outputs and public samples are untouched.

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Table Selection | projects.js / projects-compare.js | ProjectLibrary IDs and comparison rows | One project/model revision; independent comparison category/severity | doctor_projects.browser.cjs real records/deep links |
| Select/Listbox | projects-review.js / projects-compare.js native selects | Project/model/revision/status API enums | OS popup accepted; new model versus existing model explicitly named | Desktop/phone keyboard and opened native selects |
| Form | projects-review.js / projects.js | ProjectLibrary create/save/follow-up schemas | Labelled native controls; owned inline errors; novalidate | Blank validation, saved fields, failures and retry |
| Scrollbar | doctor.css global baseline | DESIGN.md | Bounded project/issue registers; natural detail/comparison; auto-growing note | 1440px / 390px overflow checks |
| CRUD | ProjectLibrary routes with projects.js / projects-review.js | Persisted revision/follow-up envelopes | Create project stays on its detail; save revision stays in 3D; save follow-up stays at current finding | Full workflow plus server restart reopening |

New project creation and revision/follow-up save are pessimistic and duplicate-disabled. After a revision save, its returned ID enters the URL and the same model remains visible. A raw new IFC removes the old revision identity while retaining the intended project/model destination. The logical model selection uses its server ID; filename changes do not create a new slot implicitly. Same-slot/same-review retry is idempotent in the service. Errors preserve input and expose a retry action or an enabled save control. Model choices finish loading before save is enabled.

Explicit Load public example and Import IFC start a fresh selection: once the new report succeeds, old finding/revision deep-link choices are removed and the relevant initial result filter is chosen. Opening a revision/finding URL or changing language restores that intentional selection instead. Fresh-load retries retain the fresh intent. A failed new-source request changes neither the previous report nor its URL identity, and project/model save destinations remain available for the next revision.

If an in-filter selected finding would fall beyond the current finite result
window, it replaces the window's final ordinary row and appears first. The
rendered-row limit is unchanged; an out-of-filter finding is never inserted as a
match. The saved/deep-link selection, right detail and 3D identity remain exact.
`doctor_review_large_selection.browser.cjs` covers this with over 100 synthetic
PASS results in both languages; it is a list-selection regression, not evidence
of model or geometry capacity.

Opening a saved revision calls the revision endpoint before geometry/advice, restoring the report and geometry session after a restart. URLs retain revision and selected finding across language changes. Result-list selection and per-element rule selection continue to use finding_id/element_key; comparison links select the exact endpoint-provided finding in the appropriate revision. Missing rows point to the previous revision. No client-side GlobalId guess is made for ambiguous identities.

Manual follow-up statuses are exactly open, in_progress and ready_for_recheck. These do not change a stored check verdict or comparison category. Drafts are keyed by revision/finding in page memory, survive issue selection, and are marked unsaved. Navigation/language changes with unsaved follow-up input use an app-owned native dialog; Keep editing receives initial focus, Escape cancels, and focus returns. Browser unload gets the narrow native lifecycle safeguard. No note/owner/project data is written to localStorage. Saves of another finding cannot overwrite the currently edited form.

Revision comparison selectors contain revisions of one logical model only. Same-revision pairs are refused locally. Linked before/after parameters start comparison only after its form is mounted, so refresh and browser Back restore a concrete result. A new selection aborts stale comparison requests. Six response categories remain separate; resolved means same-object/same-rule FAIL→PASS, and missing/no-longer-applicable/not-comparable are never presented as repaired. ERROR and INFO counts/labels are separate. The server scope note appears before statistics, and each row keeps before/after observations, localized reason, identity disclosure and a precise revision link. The finite result register initially shows 100 rows with explicit load more.

Project brief is an explicit Markdown attachment download. It does not navigate away from the active page or discard drafts. Browser evidence is stored under `docs/evidence/product-phase2/`; `tests/doctor_projects_fixture.py` creates clearly synthetic IFC revisions through the real API, and `tests/doctor_projects.browser.cjs` exercises those alongside the unchanged public example. No static result fallback is shipped.
