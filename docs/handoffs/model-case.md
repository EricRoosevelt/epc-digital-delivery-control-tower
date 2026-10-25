# Authorized model case

An existing authorized local case was found outside the public checkout. The
original source, historical working copies, exported IFC files, recorded BIM
choice, source-edit screenshots, export configuration and Revit journal remain
in the private asset area. No model, source path, case identifier, object
identifier, screenshot, raw log or file fingerprint belongs in this handoff.

## Source evidence reused

The source operation took place on **2026-10-02** in a Revit working copy. The
current product replay uses the resulting IFC exports; it is not presented as a
new Revit edit or as an IFC field patch disguised as source export.

The recorded BIM choice selected LOUVRE for one assigned air-terminal
type, affecting both of its instances. It considered the system, orientation,
position and available construction evidence, including contrary evidence and
uncertainties. This was a recorded exercise-specific BIM classification choice,
not an original-project requirement or a machine deduction from an object's name.
There is no named human engineering sign-off. The record names a review role,
not a project engineer, and does not establish project engineering acceptance.
Actual classification and acceptance remain for a person with the project context.

The historical source change added a type parameter definition for the relevant
category and populated it only on the selected type. The recorded export used
the same built-in IFC4 Reference View configuration. Journal events establish
type-value editing, saving, then IFC export. The exported files' internal
timestamps agree with that order. The saved source backup matches the clean
baseline source file, and the original source hash matches both historical
preservation manifests. These are corroborating source records, not a claim
that the current session re-performed those UI operations.

Independent file checks in this session established:

- Both exports contain **2,055 IfcElement instances and 96 air terminals**.
- The two selected instances retain their GlobalIds and IFC classes; their raw
  instance enums, assigned-type enums and effective values change from
  NOTDEFINED to LOUVRE.
- The other **94 air terminals retain their previous effective values**.
- No IfcElement is added, removed or reclassified between the real source exports.
- The selected instances' tessellated geometry hashes are unchanged.

The four-value product rule checks a particular information predicate. Its PASS
does not establish physical classification correctness, openings, alignment,
clash freedom, statutory compliance or overall model acceptance.

## Current native-tool feasibility

Revit and its existing IFC export UI are installed, and the historical journal
contains the actual source-edit/export method. One current Computer Use launch
attempt returned **“Computer Use app approval timed out.”** It did not reach the
source UI. There was no explicit automatic-approval rejection or license error,
so the current license state was not established. The attempt was not repeated
during performance measurement. Existing valid source evidence is reused.

## Controlled comparison probes

Separate private working-copy IFC probes remove a selected instance or reclassify
its assigned-type group. They are deliberately constructed software checks, **not Revit
exports, project changes or engineering repairs**. They must remain separate from
the real source-export pair: deletion should produce missing evidence, while
class change should prevent a repair claim. The originals and historical source
files remain untouched.

Native reopening and the current ReviewStore evaluator verified these PV-001
comparison results:

| Input pair | Result | Actual object change |
| --- | --- | --- |
| Real source-export pair | 2 resolved, 94 remaining | No addition, removal or class change |
| Controlled deletion copy | 1 missing, 95 remaining, 0 resolved | One instance removed |
| Controlled class-change copy | 2 not comparable (`class_changed`), 94 remaining, 0 resolved | The shared-type classification change affected two instances |

Only `_mesh` was deliberately skipped in this evaluator run. These results are
comparison checks, **not 3D, performance or source-export evidence**. The real
pair's source-export evidence remains the independently verified historical
Revit records described above. The controlled copies are not engineering fixes.

## Current product replay

The same before/after IFC payloads were imported through the actual browser file
input under the final shared PV-001 v2 implementation. Both contain **2,055 real
meshes, 546,302 vertices and 1,073,546 triangles**. Each changed instance was
selected by its verified GlobalId, matched to its actual mesh, focused and
isolated. Both versions were saved under one project and one stable model slot.

The actual project comparison reports **2 resolved, 94 remaining**, with zero
new, missing, not-applicable or not-comparable changes. Each resolved row has a
unique retained GlobalId, unchanged IFC class and checking basis, and an observed
NOTDEFINED/FAIL to LOUVRE/PASS transition. Manual ready-for-recheck on the before
revision leaves its machine FAIL untouched. An in-progress record on a still
failing after object also leaves FAIL untouched. The downloaded latest-revision
Markdown brief includes that current follow-up and separates it from the machine
comparison. Chinese reopening and the actual saved target geometry were exercised.

The server process was then terminated and replaced by a new process using the
same external SQLite directory. Without reimporting IFC, the browser reopened
both saved revisions, restored the selected finding and actual geometry, verified
the exact before/after follow-up records, recomputed the same 2/94 comparison,
and downloaded the latest brief again. The restart verification completed with
no page errors. This is a process restart, not just a page reload.

The independent legacy loader/registry/check/IdsChecker path also processed both
exact IFC payloads outside the checkout: **192 applicable observations, zero
status differences**, with all 1,959 non-applicable projections matching in each
revision. See [rule parity](rule-parity.md) for its scope and reporting differences.

## Historical synchronous-import measurements

Measurement host: Windows 11 (10.0.26200), Intel i7-10700 (8 cores/16 logical
processors), 15.9 GiB system RAM, NVIDIA RTX 3080 via ANGLE D3D11. Browser:
headless Edge 156.0.4314.42 at 1440 by 1000. Measurements use the actual UI,
test-only WebGL draw observation, resource timing and 50 ms server RSS sampling.
No private evidence was sent to an AI provider.

| Operation | Before, cached content | After, previously uncached content on warm process |
| --- | ---: | ---: |
| IFC bytes | 12,039,032 | 12,039,024 |
| POST upload, parse, checks and tessellation | 0.389 s | 177.193 s |
| Geometry GET | 1.459 s | 1.512 s |
| Upload to usable UI | 2.610 s | 179.483 s |
| Upload to first triangle submission / next animation frame | 2.350 / 2.513 s | 179.236 / 179.391 s |
| Server baseline RSS | 267.73 MiB | 295.50 MiB |
| Upload through viewer-ready sampled peak RSS | 353.49 MiB | 528.32 MiB |
| Save-snapshot sampled peak RSS | 623.41 MiB | 782.52 MiB |
| OS process-lifetime peak RSS | 655.44 MiB | 816.37 MiB |
| Browser JS heap at viewer-ready | 75.01 MiB | 63.40 MiB |

After import, rotate and zoom controls each had five measured click-to-next-frame
samples: p95 **23.3 ms** and **19.8 ms**. The two target selections took 17.5/18.5 ms,
focus 14.7/15.2 ms and isolate 14.9/14.8 ms, with one sample per target/action.
The first after screenshot completed at 179.566 s. A triangle submission followed
by an animation frame is not GPU presentation time; these control samples do not
establish sustained FPS. JS heap excludes browser native/GPU allocations. Server
private-byte peak was approximately 1,244 MiB; it is distinct from RSS. Sampling
can miss short peaks, while the OS peak spans the process lifetime.

This establishes a completed workflow for the measured **single-file 2,055-object,
1.07-million-triangle case on this host**, not a larger-model or concurrency SLA.
The 177.193 s POST was close to that version's 180 s request timeout. The upload cap
is not a validated model-size capacity, and there is insufficient margin to
promise larger inputs or slower machines.

One earlier cold-process attempt completed checking but the viewport failed.
Its original caught error was hidden by the old UI, so its underlying cause is
unresolved; cached diagnostic reopening succeeded. It is retained as a limitation,
not recast as a successful cold 3D test. An earlier measurement-tool failure from
DevTools response-body eviction is separately retained and excluded from product
capacity conclusions. The final tool observes the product's existing JSON parse
instead of reading the large body through the inspector cache.

The observed UI errors were corrected: geometry failure no longer reports Model
loaded, renderable objects are not mislabeled as having no IFC geometry, and JSON
parse failures retain their original exception. Regression coverage injects both
HTTP 503 and malformed successful JSON and verifies visible error details,
readable checks and successful explicit retry. It does not claim to fix the
unreproduced underlying cold-load error.

Overview inspection also found washed-out thin MEP geometry. Analysis of saved
vertices established a real 220.21 by 68.58 by 8.26 metre envelope; all 2,055
meshes were in the existing initial spatial cluster. This was not an origin
outlier or camera-cropping issue. The renderer now interprets palette channels
as sRGB, lowers the lights and quiets the grid. Source vertices, camera bounds,
palette values and visible-object count are preserved. Small terminals still
require focus/isolation at this floor-wide scale. The timing table precedes this
display-only lighting adjustment; subsequent cached visual checks do not create
a new uncached-import timing claim.

Subsequent hardening replaces the synchronous browser import with observable
worker jobs, process-tree cancellation and a server deadline. The measurements
above remain evidence for the earlier implementation. The current cache retains
at most 16 serialized payloads / 64 MiB; project operations that need only reports
do not restore geometry. Current same-SHA browser CI includes project drafts,
geometry failure/retry, deep selection and import-job recovery. These changes do
not retroactively identify the earlier cold viewport error.

## Verification

Full Python verification: **1,476 passed and 11,871 subtests passed**, with the
required IDS audit enabled. Ruff, dependency consistency, shipped pipeline
regeneration, dashboard core and PBIP checks passed. Snapshot verification found
**20 published artifacts unchanged**, without refreshing expected bytes. The
public bilingual UI and project browser regressions passed; a first project
navigation wait timed out, then independent same-route inspection and the
unchanged full test rerun passed. Raw observations remain separate.
The final review browser regression passed after the renderer adjustment,
including English desktop, Chinese 390 px, actual picking/focus/isolation,
information-only and geometry-less inputs, failed-load preservation, both
geometry-error branches and retry recovery. Page errors were empty. Saved real
case screenshots were also inspected; the display adjustment leaves all 2,055
meshes visible.

The saved after result exposed another UI issue: its selected PV-001 PASS was
beyond the first 100 of 6,167 passing findings. The selected matching result is
now pinned into the current window without increasing its row count or injecting
an out-of-filter result. A public synthetic 150-element/450-PASS browser
regression passed in English and Chinese, covering the saved deep link, exact
selection, 100-row limit, result/name filters and clear. The actual saved target
was then inspected with the selected first row, matching PASS evidence and real
isolated mesh together. This synthetic test is selection coverage, not a capacity
measurement or a replacement for the real case.
