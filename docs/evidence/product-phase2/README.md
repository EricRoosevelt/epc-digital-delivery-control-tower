# Projects and rechecks: actual browser evidence

Captured on 2026-10-25 from the running local application. Public geometry is the
unmodified buildingSMART PCERT example (CC BY 4.0, buildingSMART International
Ltd.). Recheck transitions use separately created, clearly labelled SYNTHETIC
IFC files, not edited public models or claims about an actual engineering job.
Names and work notes entered by the browser tests are fictional test records.

`tests/doctor_projects_fixture.py` creates the two test-owned IFC revisions
through the real HTTP import/save endpoints. `synthetic-fixture.json` identifies
those saved revisions and their expected comparison counts. The synthetic
objects intentionally have no representations; their screenshots show the
working evidence path and do not manufacture geometry.

`tests/doctor_projects.browser.cjs` exercises real project creation, public-model
revision saving, follow-up notes, language switching, a new revision, comparison
deep links and the Markdown download. `projects-browser.json` records its actual
observations and page errors. One deliberate HTTP 503 exercises failed-save
recovery; regular model/check/report data is real.

| Capture | Evidence |
| --- | --- |
| `projects-en-empty-project.png` | Creating a project and finding the next model action. |
| `review-en-save-revision.png` | Explicit new/existing model destination and revision label. |
| `projects-en-model-revisions.png` | Actual saved model revisions with reopen/new-revision controls. |
| `review-zh-saved-followup.png` | Public model and saved owner/work status alongside unchanged check results. |
| `review-en-unsaved-draft.png` | Unsaved follow-up warning with an explicit keep-editing choice. |
| `projects-en-comparison.png` | Six comparison categories, rule/information record groups and actual before/after readings. |
| `projects-en-missing-not-repaired.png` | A vanished object is distinct from a passed recheck and links to old evidence. |
| `projects-zh-390-comparison.png` | Readable Chinese comparison categories and revision links on a narrow viewport. |
| `projects-zh-390-revisions.png` | Project model history at 390px. |
| `review-zh-390-revision-evidence.png` | Correct revision/finding reopens on a phone with usable guidance. |

PM inspected the desktop comparison, saved follow-up, mobile comparison and
mobile revision evidence screenshots. This review corrected a group label that
could imply every comparison record was still an outstanding problem. BIM also
walked current/previous evidence links in both languages and identified the
comparison deep-link initialization issue, which was fixed before final capture.

`restart-check.json` records an actual stop/start of the server process without
clearing its database. It confirms the public saved revision restored 39
elements, 32 meshes, the exact multiline note, its manual ready-for-recheck
status and its separate FAIL finding. Local advice, comparison counts and the
brief download also survived. Automated persistence tests separately cover
opening the database with a fresh ReviewStore/ProjectLibrary.

`premium-audit.json` is a static design-context check, not proof of runtime
accessibility. Screenshots cover desktop Chromium/Edge and an emulated 390px
viewport; physical-device and screen-reader certification were not performed.
No live OpenAI response is represented in these captures.
