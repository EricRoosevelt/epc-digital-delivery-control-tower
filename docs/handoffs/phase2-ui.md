# Phase 2 · projects, revisions and evidence-based rechecks

Implemented in the existing isolated `doctor-product-phase1` worktree, after Phase 1 commit `5fd1d40`. The original dirty checkout and published pipeline outputs were not edited by this UI work. PM owns the final integration commit and full verification.

## Delivered workflow

1. Create a project at `/projects.html?lang=zh|en`.
2. Open its 3D workspace, load the unchanged buildingSMART public example or import one IFC, then save the check results and 3D snapshot as a model revision. The save form clearly chooses a new model or an existing model's next revision; it does not promise to retain original IFC source bytes.
3. Open saved revisions directly from the project register. URLs preserve revision and selected finding across language changes, and the revision endpoint restores geometry/advice sessions after a service restart.
4. Record an owner, manual work status and multiline note for the exact revision/finding. Status is Open / In progress / Ready for recheck. It never changes the IFC check verdict.
5. Import a new IFC and save it under the existing logical model, even when its filename changes.
6. Compare two revisions of that model. Six outcomes stay separate: rule recheck passed, still needs review, new failed check, missing, no longer applicable and not comparable. Group counts are labelled **Rule check records / Information prompt records**, because they include resolved and missing observations and are not current open-issue counts.
7. Inspect each before/after observation and localized reason, or follow its exact finding link. Missing rows open the earlier revision; current evidence opens the later revision. Download the project's Markdown work brief from the explicit project action.

## Design and behavior

The shared pale engineering stage, teal controls, typography, borders and focus language remain unchanged. `projects.css` extends the existing tokens. The project page uses a finite project register beside model revision sections; the comparison is an evidence register with six selectable category counts. On 390px screens the sections stack with all actions available and no horizontal overflow.

The existing 3D page adds a compact saved/unsaved context bar, an explicit project/model/revision save panel, and a follow-up disclosure with a visible manual status and owner. The source evidence and advice remain readable. Notes auto-grow and then scroll; their contents are not truncated into a card title.

Save requests are pessimistic, duplicate-disabled and bounded by the shared JSON client. Existing fields remain after a failure. Model choices must finish loading before a revision save is enabled. Same-model/same-review retries use the service's idempotency behavior. No project, owner or note enters localStorage.

Follow-up drafts live in page memory, keyed by revision/finding. Switching findings preserves the draft. A navigation or language action that would lose a dirty follow-up opens an app-owned native HTML dialog with Keep editing initially focused; Escape and focus restoration use native dialog semantics. Browser unload has the narrow lifecycle safeguard. Successful saves clear the dirty state; a failed save leaves editable input and an enabled retry/save action.

Comparison requests ignore stale responses. Before/after deep links restore the comparison after its form is mounted. Same-revision pairs are refused locally; model selectors contain only that model's revisions. The server's actual scope note appears before the category statistics, including multi-file or ambiguous-identity limitations. No client-side GlobalId matching or artificial closure is added. Missing and not-comparable rows do not receive a success treatment. INFO uses prompt language rather than implying project-required information.

Loading a new source and reopening an existing record have explicit selection semantics. A successful Load public example / Import IFC clears the prior finding/revision choice and selects the appropriate initial filter, while preserving the intended project/model save destination. Revision deep links and language reload restore the selected finding. A failed new-source request preserves the earlier report and URL. This distinction was verified against the existing Phase 1 browser regression, which exposed that keeping an old N/A finding during a fresh demo load incorrectly showed 37 N/A rows instead of the initial 2 Needs review rows; the old test assertion was retained.

## Ownership and files

- `doctor/static/projects.html`, `projects.js`: project creation/list/detail, model revision register and entry links.
- `projects-compare.js`: same-model pair selection, comparison deep links, six categories and row evidence.
- `projects-review.js`: review save context/form, persisted revision and follow-up state, retained drafts and navigation protection.
- `projects-words.js`: registered Chinese/English project UI messages; `projects-api.js`: shared bounded JSON request boundary.
- `projects.css`: project/review persistence layout variant using existing shared tokens.
- `review.js`, `review.html`: project integration, saved revision reopening and finding deep links. AI configuration updates no longer rebuild an active follow-up form.
- `shell.js`, `screens.js`, `ui-words.js`: project navigation/home entry. The existing English wording record has the new navigation phrase.
- `DESIGN.md`, `UX-CONTRACT.md`: durable design, canonical owners and state behavior.
- `tests/test_doctor_preview.py`: explicit permitted HTML/CSS entry lists now include projects; checks against embedded results, hashes, fake model keys and unsafe markup remain.
- `tests/test_doctor_project_words.py`: actual module parity, no Chinese fallback in English, and regression checks for honest snapshot/manual/comparison wording.

Backend persistence, comparison policy and Markdown brief generation belong to engineering/BIM/PM; this UI does not rewrite their results.

## Reproducible verification

Use the existing project Python environment with IfcOpenShell. Create an explicitly synthetic pair through the actual HTTP API:

```powershell
python tests/doctor_projects_fixture.py http://127.0.0.1:8774 --output docs/evidence/product-phase2/synthetic-fixture.json
```

This generates minimal IFC entities with stable valid GlobalIds and no invented geometry. It covers FAIL→PASS, persistent failure, new failures, disappearance and class change. Public IFC samples and historical screenshots are not modified. The output records opaque project/model/revision IDs and the comparison link, so the same records can be reopened after a server restart.

Run the full real-server browser workflow with externally available Playwright:

```powershell
$env:NODE_PATH = '<external-runtime>/dependencies/node/node_modules'
node tests/doctor_projects.browser.cjs http://127.0.0.1:8774 docs/evidence/product-phase2 docs/evidence/product-phase2/synthetic-fixture.json
```

PM executed this integration successfully with `errors=[]`. It exercises actual UI project creation/validation, real public IFC save, owner/manual status/multiline note, finding-to-finding retained drafts, the unsaved-change dialog/focus, a deliberately failed follow-up save and retry, Chinese language reopening, a raw IFC saved into the same model as a new revision, Markdown brief, automatic comparison deep links, all six category controls, exact current/previous finding links and Chinese 390px/reduced-motion behavior.

PM verified an actual process stop/restart against the same persisted IDs without clearing the database. `restart-check.json` records a pass: all 39 elements and 32 meshes restored; the exact multiline note and Ready for recheck status survived while the machine verdict remained FAIL; local guidance, the comparison summary and the Markdown attachment also restored. The final projects and Phase 1 review browser targets passed after the record-label and fresh-selection corrections. The legacy UI browser matrix also passed after the evidence-based test synchronization correction below.

The legacy return-focus check had an existing desktop race: the filter was already visible in the detail view, so waiting for it did not wait for hash-route rendering. A temporary diagnostic running the actual browser captured both 1280px language cases with early focus on Back to results / 返回结果列表, followed by actual focus on `house fireplace cap` with `aria-current=true`. The 375px cases had already completed before sampling. `tests/doctor_ui.browser.cjs` now waits for the active element to match `.c-name a[aria-current="true"]`, then performs the same exact query/name/ARIA assertions. No sleep, weakened focus requirement or legacy product change was introduced. The temporary probe was removed; `legacy-focus-race.json` retains the observations, and the complete corrected matrix passed.

Actual local verification:

- Changed wording/static/English tests: **51 passed, 4311 subtests passed**.
- Final project wording test: **1 passed, 120 subtests passed**.
- Ruff for `doctor_projects_fixture.py` and `test_doctor_project_words.py`: passed.
- JavaScript syntax checks for projects modules and review integration: passed.
- Frontend premium strict audit: **zero findings/errors/warnings**, saved at `docs/evidence/product-phase2/premium-audit.json`.
- PM's old UI regression set: **136 passed, 5106 subtests passed** before the final wording-only adjustment.

## Actual visual inspection

CUA Chrome was used to inspect the real project overview, comparison page, and review save panel including the new/existing-model selector. BIM independently inspected Chinese/English comparison → current/previous finding paths and language preservation. Their concrete deep-link report exposed a detached-form restoration bug; that was fixed by mounting the form before requesting comparison, and BIM verified the corrected link without extra clicks.

New browser screenshots and machine-readable observations live under `docs/evidence/product-phase2/`:

- `projects-en-empty-project.png`, `projects-en-model-revisions.png`: creation/continuation and actual saved revisions.
- `review-en-save-revision.png`, `review-zh-saved-followup.png`: explicit save destination and manual follow-up beside unchanged check evidence.
- `review-en-unsaved-draft.png`: app-owned draft protection and focus.
- `projects-en-comparison.png`, `projects-en-missing-not-repaired.png`: six categories and disappearance semantics.
- `projects-zh-390-comparison.png`, `projects-zh-390-revisions.png`, `review-zh-390-revision-evidence.png`: phone comparison and record reopening.
- `projects-browser.json`, `synthetic-fixture.json`: observed workflow and persisted test identities.
- `restart-check.json`: actual process restart with restored geometry, work note/status, unchanged machine verdict, guidance, comparison and brief.
- `legacy-focus-race.json`, `legacy-ui/`: observed desktop focus timing and the passing legacy browser matrix.

The 390px comparison screenshot was visually inspected: category counts fit in two columns; actual FAIL→PASS observations and precise revision links remain readable. Final group wording is record-based, not an outstanding-issue claim.

## Remaining limits

This iteration does not add source-model writeback, downloadable original IFC archives, team authentication, issue assignment notifications or automatic claims of project readiness. Browser evidence is desktop Chromium/Edge and an emulated narrow viewport, not physical touch or screen-reader certification. External live AI-provider verification remains outside this project's UI persistence changes. The original evidence/check semantics remain server-owned.
