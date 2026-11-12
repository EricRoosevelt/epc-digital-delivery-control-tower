# Phase 1 · real IFC review workspace

Implemented in the isolated `doctor-product-phase1` worktree. The original dirty checkout was not edited. This handoff records actual UI implementation and verification, not a project deployment claim.

## Product decisions

- `/review.html?lang=zh|en` is a real three-column engineering workbench. The homepage recommends it and retains the existing simulated examples and local-check paths.
- The large central model stage is the defining visual. Shared light/teal tokens and local Segoe/CJK fonts come from `doctor.css`; `review.css` contains the named operational layout variant. At 1440px the columns are 270px/flexible/330px. Phone order is model, issues, then naturally growing evidence/actions.
- Source geometry remains world metres/Z-up. Initial camera framing rejects spatial outliers using the IQR of mesh-center distances; public origin/georeference helper objects remain unchanged and Show all frames their full extents. Real demo: 39 elements, 32 renderable meshes, 7 without geometry.
- Camera supports orbit/pan/zoom, direct element picking, list/detail selection, focus, isolate/undo, full extents, reset, top/isometric and named zoom/rotate buttons. Selection and visibility use model-qualified `element_key`, never GlobalId alone.
- Default results prefer Needs review (ERROR + FAIL), then Information, then PASS. The public example has 2 Needs review results and 19 information results. INFO receives neutral treatment in every list/detail/rule-select surface.
- Actions and verification appear before detailed check evidence. Class/storey remain visible; GlobalId/Tag and repeated known facts fold. Missing geometry keeps all results and guidance readable, with geometric focus/isolation disabled.
- AI configuration is labelled configured, never connected. Without a key the page presents actual local rule guidance. AI is an explicit button when configured and the returned `mode` determines its label. The visible notice says only minimal text evidence is sent, not IFC/geometry. No AI response or completed repair is fabricated.
- Loads are duplicate-disabled, cancellable and bounded to 180 seconds by `AbortSignal.timeout`; failures preserve existing results. Geometry/WebGL failure leaves checks usable and offers retry. Selecting another issue aborts stale advice. Search is transient/local and IME-aware, with a clear button restoring focus.

## Files

- `doctor/static/review.html`, `review.js`, `review-viewer.js`, `review-words.js`, `review.css`: page, state/data/advice, Three renderer, registered Chinese/English copy, and layout.
- `doctor/static/shell.js`, `ui-words.js`, `screens.js`, `doctor.css`: visible navigation/home entry and existing primary-link styling.
- `DESIGN.md`, `UX-CONTRACT.md`: ownership, token/layout variant, selection/loading/localization behavior.
- `tests/doctor_review.browser.cjs`: reproducible real-server browser integration. `tests/test_doctor_recheck_screens.py` retains action-order/old-entry assertions for the new recommended action. The exact permitted static entry list in `test_doctor_preview.py` was updated by engineering; restrictions on bundled result data, hashes, fake element IDs and unsafe markup remain.
- Existing English wording record contains the three new homepage/navigation phrases; prior wording was preserved.

Three.js bytes/provenance and backend/AI implementation belong to PM/engineering. UI imports the vendored `three`/OrbitControls files and does not modify them.

## Verification

Executed using the project's existing Python environment:

```powershell
& '<project>/.venv/Scripts/python.exe' -m pytest -p no:cacheprovider tests/test_doctor_english.py tests/test_doctor_recheck_screens.py tests/test_doctor_preview.py -q
```

Result: **136 passed, 5083 subtests passed**. Restricted-shell temporary-directory errors were resolved by rerunning with normal temporary-directory access; they were not hidden or counted as product passes.

The frontend premium strict audit returned **0 findings/errors/warnings**; output is `docs/evidence/product-phase1/premium-audit.json`. JS module syntax was checked. Changed review files contain no browser native dialogs, `innerHTML`, fake links or embedded result records.

The browser integration runs against the actual local Doctor server with external Playwright, not mocked IFC results:

```powershell
$env:NODE_PATH = '<external-runtime>/dependencies/node/node_modules'
node tests/doctor_review.browser.cjs http://127.0.0.1:8774 docs/evidence/product-phase1
```

PM executed the final script successfully, with `errors=[]`, including the information-only Architecture import. It covers real three-model loading, counts, list selection, canvas picking, focus, isolate/reset, full extents, INFO semantics, search/no-results/clear-focus, no-geometry evidence, model filter, deliberately injected 503 preservation/retry, raw HVAC and Architecture IFC imports, Chinese 390px rendering, language reload and reduced motion. Architecture starts with non-empty INFO results and an in-filter selection. The pre-existing `doctor_ui.browser.cjs` also passed. PM's final full Python verification with required audit enabled returned **1363 passed, 11725 subtests passed**, with no failures or skips (155.43s).

IAB was also used to inspect the actual 1440px overview, selected model geometry, the reopened native result-filter popup, and neutral INFO evidence. The first overview made the building too small due to real source helper objects; the main-cluster camera change corrected it. The second review exposed buried actions; the final hierarchy visibly places summary and first actions in the 1000px-high desktop viewport.

## Screenshot evidence

All new screenshots are under `docs/evidence/product-phase1/`; historical evidence was not overwritten.

- `review-en-1440.png`: real full workbench, visible selected cap, action-first right rail.
- `review-en-isolated.png`: one selected real mesh isolated.
- `review-en-no-geometry.png`: no-geometry element remains readable.
- `review-en-information-only-import.png`: final information-only initial filter regression.
- `review-zh-390-top.png`, `review-zh-390-viewport.png`, `review-zh-390-advice.png`: phone load controls, operable model stage and readable engineering advice.
- `review-browser.json`: integration observations and captured page errors.

## Remaining limits

No configured external AI provider was available for a live provider call; local guidance and the provider-independent HTTP path were exercised by the integrated team. Browser evidence covers Edge/Chromium desktop and a narrow emulated viewport, not physical touch devices, a screen-reader audit or a complete WCAG certification. IFC repair/writeback, issue assignment and automatic revision comparison are not implemented or claimed.
