# BIM Doctor approved UI implementation plan

> Execution: the assigned sole implementer uses superpowers:executing-plans. The user has already approved the direction and requested execution; no additional style or plan approval is required. Independent TD/UX/BIM review follows the reviewable candidate.

**Goal:** Implement the approved light workspace across the complete existing main path with real adapter data and routes, preserving reading limits and returning to the current object.

**Architecture:** Keep native JS/CSS and the existing envelope boundary. Extend the shared shell, presentation components and route focus behavior; keep checker/domain/identity code unchanged. Local list/detail uses its existing finding route; example items keep their independent routes.

**Tech stack:** Existing Python server, native ES modules, CSS, existing externally available browser tooling. No new product dependency, framework, font download or 3D library.

**Spec:** PM's 2026-10-12 implementation decision; approved v2 spacing; same-day UX, BIM and technical estimate reports. These supplied inputs remain in the shared maintainer docs and are not rewritten by this task.

## Prerequisite and global constraints

- Verify remote main contains the TD merge of #63, including `tr:not([hidden])`. Only then create a new managed worktree and `feat/doctor-approved-ui` branch from that exact main SHA. Do not reuse or switch the old shared checkout or merge #63 as implementer.
- Direction is already approved. Use the v2 spacing and recommended type treatment; do not reduce readable body text to meet a viewport target. Maintain CJK fallbacks and full long-value access.
- Only the two real main paths in navigation. Preserve directory, item/recheck deep links, local upload/discipline/scope and all existing refusal/error routes.
- Both 375×812 home primary buttons must be fully visible before the long recommended-card explanation. Add a results jump near the example summary without hiding required limitations.
- Preserve same-check query, status filter and selected object on return and language switch. Keep model-name/Tag/GlobalId query out of shareable URLs and permanent storage. No general refresh persistence feature.
- Switching objects focuses and scrolls the new object's title/conclusion; location jumps never replace the router hash. Return goes to the visible selected row, or search if that row is filtered out; no pixel-exact restoration promise.
- Preserve FAIL, PASS, model-level N/A, multiple models, empty/missing values, unknown requirements, loading/refusal/fault recovery and #58/#60 counterexamples. Data, rules, Pack and generated contracts remain unchanged.
- Local details retain local mode and input model identity from the actual finding/model. Do not label arbitrary user files as public samples; do not substitute software SHA for model versions.

## Canonical owner map

| Capability | Existing owner and planned extension | Required evidence |
|---|---|---|
| App identity/main navigation | `index.html`, `app.js`, `language.js`; one shared shell and registered bilingual UI labels | Home/directory/item/recheck/local/refusal/loading/fault smoke, active navigation |
| Visual tokens, controls, scrollbars | `doctor.css`; root `DESIGN.md` mirrors this canonical CSS token source (model B) | Computed font sizes, focus, contrast, token drift, natural document scrolling |
| Example summary/team/item projection | `screens.js`, unchanged `first-check-model.js` | Real 13/8/6, eight actionable items and five quiet records accessible, row-specific provenance and READY limits |
| Example object/return/recheck | Existing `firstItem`, `recheckItem`, `data-return-focus`, app router | Object/deep link stays on locale switch, return focus and same-item recheck; #58/#60 evidence |
| Local list/selection/detail | `workspace-screens.js`, unchanged `workspace-model.js`; local compact list variant, existing finding route | Name-priority desktop, nowrap status, mobile single list/detail, real selection/filter counts |
| Transient same-check UI state | New focused `view-state.js`; ordinary state remains in memory; one-use language handoff consumed and removed on next load | Same-query/object across locale; no query in URL/permanent storage; another check resets state |
| Focus and in-page jump | App `focusMain` and shared DOM helper; preserve existing route format | New object heading in viewport after location jump; selected row focused on return; skip link works without changing route |
| Native selects/file controls | Existing `local-check.js` controls and server APIs | Existing native discipline popup, multi-file selection, confirmation, refusals/recovery and real check |
| Local limits and trace | Existing finding status branches, `ruleNotes`, `runIdentity`, `recordsBlock`, scope/model data | PASS/N/A stay distinct; real model identity and versions; no fabricated observed value |
| Locale copy | Existing bilingual registry; new UI labels kept separate from domain tables and added to vocabulary review record | Key/placeholder parity, English record completeness, explicit changed/moved/folded inventory |

## Task 1: coherent shell and controls

Files: `doctor/static/index.html`, `app.js`, `language.js`, `doctor.css`, a focused shell/UI wording module; root `DESIGN.md`, `UX-CONTRACT.md`.

- [ ] Write browser regression for full home CTA bounds (`bottom <= 812`, `left >= 0`, `right <= 375`), primary-before-description order, visible keyboard focus and shell presence on existing sibling routes. Run the baseline and record actual failures/passes.
- [ ] Implement approved tokens and shell once; reshape home to two real primary paths while keeping optional existing workspace/attempt routes reachable. Keep current source and mode declarations, rather than the static preview's no-checks claim.
- [ ] Verify all main-path pages inherit the same controls/typography. Check native discipline popup and long labels at 375; record the token/typography mapping in DESIGN.md and canonical ownership/behavior in UX-CONTRACT.md.

## Task 2: compact example register, existing item routes

Files: `screens.js`, `doctor.css`, UI labels, browser regression; no changes to model projections or envelope data.

- [ ] Assert real counts 13 items, 8 with actions, 6 distinct elements; all eight item links retain independent routes and all five quiet records remain reachable with per-row provenance and scoped READY limitations.
- [ ] Arrange team items as a compact scanable register. Keep source qualification and the audited items-are-not-defects sentence open next to counts; put the complete unit/count definition in the existing reading disclosure, and the five quiet records in the approved disclosure. Keep record/model version tracing reachable.
- [ ] Add a focus-moving results jump near the summary; preserve first-item/recheck routes, same-item correspondence and all existing exception wording. Test direct deep links, actual language switch from an item and return focus; smoke the two recheck counterexample scenarios without changing their conclusions.

## Task 3: real local workspace and navigation continuity

Files: `workspace-screens.js`, `local-check.js`, `app.js`, `i18n.js`, new `view-state.js`, shared DOM focus helper, CSS; existing adapters/APIs unchanged.

- [ ] Write and run failing browser cases for same-query/object across language switch, selected-row focus on return, single mobile detail, desktop natural-height detail, and selecting a new object after a locate jump. Characterize existing production behavior separately from preview-only F-01/F-02; do not invent a baseline failure.
- [ ] Implement local name-priority compact rows with real class/model/storey/Tag values; keep full existing workspace/compare columns for their sibling workflows. Preserve 0/1/2 visible-row behavior from #63 and provide localized explicit clearing.
- [ ] Keep query in memory; transfer only current same-check UI state for a language reload and immediately consume/delete that handoff. Do not write the query into URL, localStorage, logs or long-lived session storage. Preserve existing selected-file storage semantics.
- [ ] Use the actual finding route for phone detail, a visible Back link and focus on the chosen row. Use focus/scroll for locate jumps without introducing a second hash anchor. Reset state on a different run.
- [ ] Fold checker-read text only for the already-reviewed PV-001 local FAIL with known notes; keep source-edit location, type-instance impact, undecided value/actor and modification-before-object-check open. Keep PASS, N/A and unknown-rule reading branches and true trace/model fields intact.
- [ ] Run public HVAC and Architecture checks through the actual file/discipline/scope/check path, plus multi-file and a clearly labelled local synthetic PASS/long-name stress fixture. Test missing/unknown values with isolated test inputs, never as purported real results.

## Task 4: candidate evidence and PR

- [ ] Capture both languages at 1280×900 and 375×812 on real home, directory, result, item, recheck, local upload/scope/list/detail and refusal/recovery pages. Exercise zero/single/clear search, locale/object continuity, keyboard, natural scrolling, long fields and disclosures.
- [ ] Run the existing mobile search browser regression, new behavior regression and required semantic/locale tests. Run premium strict audit, existing DESIGN lint if available and token drift checks; report unavailable tooling honestly without introducing a dependency.
- [ ] Run every AGENTS gate in CI order with the project's existing venv and pinned IDS audit mandatory, to the end. Measure all generated files/status before and after the pipeline; do not refresh contracts or edit generated files.
- [ ] Commit a coherent reviewable candidate, push/create PR and attach it. Verify exact-head CI step outcomes. Write `docs/product/2026-10-12-ui-implementation.md` with SHA/PR, screenshots, actual gate results, complete wording/moving/folding delta, prototype/production differences and unmet review items. Independent TD/UX/BIM/PM assessment follows; no self-approval or merge.

## Review focus and implementation ledger

The five main risk classes are: a selected row excluded by its filter (return focuses search rather than a hidden link); locale reload while on a detail (same object/query); switching objects after a deep locate scroll (new title visible); PASS/model-level N/A or missing metadata (no borrowed FAIL/action/source assumption); and model version/source tracing (actual selected model and record, never `models[0]` or software SHA). Task 3 owns the first four browser cases; Task 2/3 tracing tests cover the fifth.

2026-10-12 preparation: read-only source/prototype/UX/BIM/technical review completed. Remote main remains `4904192ab3510b501a6ce906819a42a395de36d8`; #63 is OPEN at `8dfbf628c2f533b4c7d93700606bb32cae604a81`. TD reports automatic approval rejected its attempted merge and requires direct human confirmation. No new product branch or implementation has started. This plan is ready to copy into the new isolated checkout once that prerequisite is satisfied.

2026-10-13 execution update: prerequisite verified at merged main c62df8c; Tasks 1–3 implemented in d79b578. All AGENTS and five browser gates passed, two internal P2 layout findings RED→GREEN. PR #64 is open for designated TD/UX/BIM/PM acceptance; final CI status is recorded on its exact head. Historical preparation note above is superseded.
