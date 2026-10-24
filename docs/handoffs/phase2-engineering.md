# Phase 2 engineering handoff

## Delivery and storage

`internal/doctor_adapter/project_library.py` implements one local SQLite file beneath the existing local checks root: `projects/library.sqlite3`. The server owns one `ProjectLibrary(root, reviews)` instance. SQLite connections are short-lived, foreign keys are enabled, snapshot inserts are transactional, and first-save/model-slot/revision-number decisions run under `BEGIN IMMEDIATE`. No source IFC, API credential, generated canonical CSV, or published report is written by the library.

Projects and model slots have their own stable IDs. Revision number is assigned within the slot and is independent of filenames, display labels, source hashes and runtime element keys. Slot revisions are returned in descending numeric order. A revision freezes its report and geometry; the only mutable follow-up data lives in a separate table keyed by revision and finding ID. It records the latest owner/note/status rather than a general event audit log.

`ReviewStore.admit(report, geometry)` restores saved evidence for the existing geometry and advice endpoints. It validates identity/bindings/JSON validity, copies incoming data, and refuses a conflicting snapshot under an existing session ID. New runtime review IDs include the rule snapshot, preventing a later predicate version from sharing an identity with a historical check of the same file. The four runtime rules carry `predicate_version="1"`; checker algorithm changes must advance that version. Elements now expose `global_id_count` counted across all IfcRoot objects, so revision matching cannot accidentally pair an element whose ID collides with an unseen relation or type object.

## HTTP contract

`make_handler(..., project_factory=None)` adds the project factory as the last optional argument; previous positional factories stay compatible.

- `GET /api/projects` returns `{projects}`; `POST /api/projects {name}` returns the project object directly.
- `GET /api/projects/detail?project=id` returns `{project,models}`. Each model has `model_id,project_id,name,created_at,revisions`. Revision metadata is `revision_id,project_id,model_id,label,review_id,number,created_at,filename,sha256,summary`.
- `POST /api/projects/revisions {project_id,review_id,model_id?,model_name?,label?}` and `GET /api/projects/revision?revision=id` return `{revision,report,followups}` and admit the immutable report/geometry into the session.
- Omit model_id on the first save; pass the stable slot ID for a new version, even if its filename or SHA has changed. Saving the same review in the same slot returns the original revision. Repeated first-save requests for that review/project also reuse the first slot/revision. A changed label on a duplicate save does not rewrite historical metadata.
- `POST /api/projects/followup {revision_id,finding_id,status,owner,note}` returns the saved row, including `updated_at`. Status is `open|in_progress|ready_for_recheck`. Unsaved rows default to open; only explicit saved rows appear in followups.
- `GET /api/projects/compare?before=id&after=id` checks the project/slot, then calls BIM's `compare_revisions(before_envelope,after_envelope)`. Direction is explicit; no label-based sorting is used.
- The PM subsequently owns `doctor/serve.py` and the `/api/projects/brief` text export branch.

Project/model names allow 160 characters, revision labels 120 (blank defaults to Revision N), owners 160, and notes 4000, including Chinese and multiline text. JSON request bodies have the existing 1 MiB bound. Unknown IDs return 404; invalid inputs and damaged snapshots return a readable `{error}` response. Corrupt files are not automatically replaced.

## Verified evidence

Last engineering test command:

`python -m pytest -p no:cacheprovider tests/test_doctor_projects.py tests/test_doctor_revision_compare.py tests/test_doctor_review.py tests/test_review_http.py -q --tb=short`

Result: **69 passed**. This is the actual combined run at handoff, not a claim about a concurrently evolving full suite. Checks cover real public geometry persistence and exact restoration after restart; slot continuity across a renamed/re-exported IFC; duplicate and simultaneous first saves; transaction rollback without orphan slots; Chinese/multiline follow-ups; finding/revision/project scope; stale IDs; corrupt database and mismatched snapshot identity; mutable caller isolation; frozen rule identity; reloaded local advice; and real HTTP create/save/follow-up/reopen/compare.

The saved end-to-end recheck uses a real changed IFC with the same GlobalId: NOTDEFINED fails PV-001 before, DIFFUSER passes after. The comparison marks only that rule resolved. The old ready_for_recheck record stays ready_for_recheck and the old report stays FAIL; the new revision has no invented follow-up status.

`ruff check --no-cache internal/doctor_adapter/project_library.py internal/doctor_adapter/review.py tests/test_doctor_projects.py`: passed. `git diff --exit-code -- data/processed reports`: passed. No pipeline run, canonical regeneration, or snapshot refresh was performed in this task. Root owns full CI gates and final integration.

## Interface review and limits

Reviewed the persisted library, comparison interface, frozen rule signatures and GUI duplicate-submit guards. No false-closure path was found: only a unique valid file-local GlobalId within the same stable slot is joined, rule/schema/class changes are exposed, deletion does not become a pass, and manual states never affect the comparison. The BIM module keeps ERROR and INFO counts separate.

Federated demo reports can be saved and reopened, but revision comparison conservatively reports them as not comparable; it does not invent cross-file correspondence. Individual uploaded IFC files support the revision loop. This is a local single-user project library, with no authentication, source-model editor, deletion/archive flow or general storage migration framework. Follow-ups store the current record, not every edit. Project names are display labels rather than identity rules: distinct projects may intentionally share a name and remain isolated by UUID. The UI blocks duplicate clicks during creation. The PM explicitly confirmed this behavior; no additional name-based idempotency constraint is needed. Revision saves retain the transactional duplicate protection described above.
