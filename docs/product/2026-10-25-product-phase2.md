# BIM Doctor: projects, revisions and evidence-based recheck

## Product increment

Continue from `5fd1d40`. Make the first-stage 3D review useful over successive
working sessions: create a project, save a named model revision, record who is
following up, import an updated IFC into the same model slot, and compare the
new evidence with the earlier revision. A manager can download a work brief.

The user has authorized continuing PM-led programming, UI and BIM sub-sessions.
The existing isolated worktree is clean and retained. Routine implementation
decisions remain delegated; this document is the implementation record, not an
approval stop.

## Approach and interfaces

Use Python's SQLite library for local durable records, under the existing
checks directory's `projects/` folder outside the checkout. Persist the report
and its geometry, sufficient to reopen a revision without reprocessing source
files. Keep the existing plain ES-module UI and server; no new framework,
database service or dependency is needed.

Projects contain stable named model slots. Each slot contains immutable saved
revisions. A slot, not a content hash or filename, tells the product which model
is being revised. Runtime review IDs keep their existing meaning. Opening a
saved revision restores its report and geometry to the review service so the
existing 3D and advice flows remain available after a server restart.

Engineering owns `internal/doctor_adapter/project_library.py`, persistence
tests, the `ReviewStore` restore seam and project HTTP routes. BIM owns
`revision_compare.py` and the comparison's domain cases. UI owns project/revision
navigation, save-to-project, follow-up editing, comparison presentation and
actual browser tests. PM owns the work brief, integration and final evidence.

HTTP: GET/POST `/api/projects`; GET `/api/projects/detail?project=`;
POST `/api/projects/revisions`; GET `/api/projects/revision?revision=`;
POST `/api/projects/followup`; GET `/api/projects/compare?before=&after=`;
GET `/api/projects/brief?project=&language=`.

## Recheck meaning

Compare findings inside the same model slot, using an unambiguous valid GlobalId
and rule ID. Names, tags, STEP IDs and content-derived element keys do not prove
cross-revision correspondence. Duplicate or invalid identities remain visible
without a guessed match. Rule and class changes are exposed.

FAIL to PASS under comparable evidence means that check passed on recheck.
FAIL to FAIL remains to review; a new FAIL needs attention. A vanished element,
missing rule, changed predicate or no-longer-applicable check is a different
result from a repair. INFO prompts stay separate from error-level failures.

People can record `open`, `in_progress` or `ready_for_recheck`, plus an owner
and a note. These are local follow-up records, not authenticated assignments,
notifications or evidence that a source model was fixed. They do not mutate
machine check results. Earlier revision notes remain attributable to that
revision.

## Verification

Verify reopening projects/revisions and geometry after a service restart, model
slot continuity across changed filenames/content, persisted follow-up notes,
and meaningful comparison cases including disappearance and ambiguous identity.
Exercise the full save/reopen/update/compare flow in English and Chinese and
desktop/phone layouts. Use small test-owned IFCs for intentional model edits;
keep public samples unchanged. Run project regression and published-contract
checks in proportion to these changes; never recapture old snapshots.

OpenAI remains the selected provider. A live API key is still absent at this
stage's start. Do not label local rule guidance as generated AI or claim a live
provider evaluation without one. Saved revisions must expose the same trusted
selected evidence to the existing advice path; secret storage is outside this
increment.

Handoffs will be recorded as `docs/handoffs/phase2-*.md`, with actual changes,
verification and any material remaining limit.

Handoffs: [engineering](../handoffs/phase2-engineering.md),
[UI](../handoffs/phase2-ui.md), [BIM](../handoffs/phase2-bim.md),
[PM integration](../handoffs/phase2-pm.md).
