# Second product increment: PM integration

2026-10-25, Singapore. Base: `5fd1d40`, continuing the existing isolated product
branch. The user's instruction was to proceed to the next stage under the same
PM/programming/UI/BIM collaboration model.

## Product outcome

The 3D workspace now connects to durable local projects and model revisions.
An engineer can save the actual report and geometry, record a person/team,
work status and note, import a new IFC into the same logical model, and compare
the saved evidence. A manager can download a bilingual Markdown work brief.
Opening a saved revision after a restart restores its geometry and advice path.

SQLite lives beneath the server's external checks directory, not in this
repository. The source IFC bytes are not archived by this project library.
Revisions and their rule snapshots are immutable; editable follow-up text belongs
to a specific revision/finding. Names remain labels, while IDs establish identity.
Same-name projects are allowed; revision-save retries are transactionally
idempotent and do not invent another model or revision.

Engineering, UI and BIM continued their existing sub-sessions, submitting
[engineering](phase2-engineering.md), [UI](phase2-ui.md) and [BIM](phase2-bim.md)
handoffs. PM implemented the work brief, reviewed the code and actual captures,
integrated endpoints, exercised the complete paths and performed final checks.

## Integration decisions and corrections

- A stable model slot establishes revision context. A content-derived runtime
  element key cannot join two revisions; matching uses a valid unique GlobalId
  and the frozen rule predicate. Rule/schema/class changes remain explicit.
- The six categories distinguish a passed check, remaining/new findings,
  disappearance, loss of applicability and an unavailable comparison. Manual
  ready-for-recheck never turns FAIL into PASS.
- The public multi-file federation can be saved/reopened, but cross-revision
  pairing is limited to single-file models. Unpaired lists contain failed
  observations only; they do not turn every PASS/N/A into a warning. The scope
  note explains the boundary and counts are labelled as comparison records.
- Work briefs use the latest revision by saved number, split information prompts
  from rule checks, retain old evidence for vanished elements and keep manual
  progress separate. INFO wording identifies tool defaults requiring project
  judgment rather than claiming a client-approved requirement.
- Comparison deep links now restore after the form is mounted. Fresh model loads
  clear the previous finding selection only after success; explicit revision and
  language links preserve the requested finding. Failed loads keep old results.
- A legacy desktop focus assertion sampled a visible old filter before the
  asynchronous route handed focus back. Instrumented early/settled observations
  established the test race. Its wait now targets the actual selected-row focus;
  exact name/query/aria assertions remain, and the old product code was unchanged.

## Verification

- Final full Python run with `EPC_REQUIRE_IDS_AUDIT=1`: **1427 passed,
  11870 subtests passed in 158.76s**, no skips or failures.
- `ruff check .` and authored `git diff --check`: passed.
- Pipeline run, contract snapshot, dashboard core validator, PBIP static
  contract/evidence validator and dependency check: passed. Snapshot reports
  **20 published artifacts unchanged**; no generated snapshot was recaptured.
- New `doctor_projects.browser.cjs`, existing `doctor_review.browser.cjs` and
  legacy `doctor_ui.browser.cjs`: passed against the actual running service.
  They cover saved revisions and work records, import/retry, precise revision
  links, six comparison categories, Chinese/English, mobile and retained 3D flows.
- An actual server process stop/start restored the saved public-model revision:
  **39 elements, 32 meshes, exact multiline note, manual ready-for-recheck plus
  machine FAIL**, local guidance, comparison summary and Markdown download.
- PM inspected desktop comparison/saved-follow-up and mobile comparison/evidence
  captures. BIM independently walked the old/current revision links and checked
  that missing objects and classification changes were not shown as repairs.

The first full Python run had one legacy Windows loopback connection abort
(`test_only_this_machines_own_pages_may_ask`). Its isolated rerun passed, then
the complete confirmation run above passed unchanged. No generic retry layer,
weakened assertion or unrelated server behavior was added for it.

Evidence and source distinctions are in
[`docs/evidence/product-phase2/README.md`](../evidence/product-phase2/README.md).
Recheck transitions use explicitly synthetic, test-owned IFCs. Public geometry
uses unmodified attributed buildingSMART models; no private engineering job or
actual team assignment is represented.

## Remaining product limits

The checking scope remains the existing four information-review rules. The
project flow is local, with per-revision follow-up rather than authenticated
collaboration or notifications. Federation object pairing and automated source
repair are not implemented. The project library keeps the inspected snapshot,
not a complete source-file archive.

OpenAI is still the selected provider and saved findings restore into the trusted
advice API. No API key was configured, so no live generated-answer evaluation
was performed. The next increment should prioritize representative real project
requirements and a configured-provider engineering evaluation before broadening
claims about advice. Existing local guidance remains usable in this state.
