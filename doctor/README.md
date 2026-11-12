# BIM Doctor — local model review

## 3D review workspace

Start the server from the repository root and open the workspace:

```powershell
.\.venv\Scripts\python.exe doctor/serve.py
# English: http://127.0.0.1:8765/review.html?lang=en
# 中文:   http://127.0.0.1:8765/review.html?lang=zh
```

Load the public buildingSMART example or import one `.ifc` file (up to 50 MB).
Select a result to highlight its exact element, focus or isolate it, and inspect
the rule, observed value and next steps. You can also click a visible element and
read its checks. Models are positioned using IFC world coordinates in metres;
no geometry is invented for objects without a representation. Missing geometry
does not erase an element's check results.

IFC imports run as worker jobs with real stage and processed-element progress.
Cancel keeps the current report and 3D view and waits for the server to confirm
the worker stopped. Leaving the page, including a language change, sends a
keepalive cancellation for only that page's active job; it cannot promise delivery
after a hard close. The server's 600-second job deadline is the fallback. Returning
opens the previous report or saved revision; it does not silently re-upload IFC.

The four runtime review checks are PV-001 (the existing four-value air-terminal
type convention), INFO-001 (non-blank instance Name), INFO-002 (resolvable storey)
and ID-001 (valid, model-local unique GlobalId). Name and storey results are
information prompts: site-level or multi-storey containment can be intentional.
The public sample produces 39 elements, 32 renderable shapes, 2 type failures and
19 storey prompts. These are review counts, not a defect or compliance score.

PV-001 reads the existing product-validation rule definition and uses the same
compiler and IfcTester predicate as the pipeline. The workbench records the
rule semantics and engine versions with each revision. Its PV-001 runtime
predicate is now v2; comparison with an older v1 result reports a changed rule
basis, so rerun both source versions under v2 to assess a repair. Supported-scope
parity and deliberate reporting differences are recorded in the
[rule parity evidence](../docs/handoffs/rule-parity.md).

The browser uploads a selected file only to this loopback server. The in-memory
JSON cache is bounded to 16 payloads / 64 MiB. Completed unsaved imports have a
temporary spool capped at four results / 256 MiB per running server, including
original uploaded IFC bytes; job metadata
retains at most 16 jobs. Unsaved data can expire before the server exits. A forced
server termination can leave task directories in `<checks-dir>/import-jobs`;
these are not restored or counted by a later server. Remove those scratch files
only after all server/worker processes have stopped. Use **Save to project** to retain a report,
its 3D snapshot and follow-up records across restarts. The established example
and recheck experiences remain available from **Records & checks**.

## Projects and revision rechecks

Open **[Projects & rechecks](http://127.0.0.1:8765/projects.html?lang=en)**
([中文](http://127.0.0.1:8765/projects.html?lang=zh)).

1. Create a project, then load the public example or your own IFC in the workspace.
2. Choose **Save to project**, name the model and its first revision. The saved
   record includes the actual report, rule snapshot and triangle geometry.
3. On an individual result, record an owner, work status and note. Work status
   can be Open, In progress or Ready for recheck; it does not change PASS/FAIL.
4. From the model's project card, choose **Import new revision**. Upload the
   newly exported IFC and save it under the existing model. A renamed file still
   belongs to the same model when you select it explicitly.
5. Compare two revisions and open an individual result in the appropriate saved
   3D revision. Download a Markdown work brief from the project when useful.

Recheck results distinguish a passed rule, a remaining finding, a new finding,
an element not found now, a check no longer applicable, and an unavailable
comparison. Optional information prompts are counted separately. Single-file
comparison uses valid GlobalIds proven unique in that file and the same frozen
rule predicate; it exposes changes of class, schema or rule basis. A vanished
object or an empty check result is not evidence of a successful fix.

The public three-file federation can be saved and reopened. Cross-revision
object pairing currently supports single-file models; a federation comparison
states that limit and keeps the two revisions' failed observations separate.
Names, tags and STEP IDs are never used to guess identity across versions.

The SQLite project library is at `<checks-dir>/projects/library.sqlite3`.
The server prints its actual location on startup. `--checks-dir` or the existing
`EPC_DOCTOR_CHECKS_DIR` setting chooses the external data directory. Saved revisions
are immutable; follow-up text is updated for its own revision/finding. Opening a
saved revision restores the report; its geometry is loaded when requested by the
workspace. Saving notes, comparing revisions and generating briefs do not load
geometry. Evicted saved payloads are restored from SQLite, including after a
restart. Saving a new single-IFC revision offers an unchecked **Permanently retain
this original IFC…** choice. With consent, source and revision are saved in one
SQLite transaction for later enterprise-rule checks, outside the geometry cache.
The exact revision's purpose form opens after saving; no second upload is
needed. A project without adopted rules first opens rule preparation with this
revision context. A save without consent preserves only the report and geometry. **Attach
exact revision source IFC** appears only for records missing a source. API
credentials are not stored. Unrelated older local-check
entries retain their original storage behavior.
For non-UTF-8 STEP exports, parsing uses an external temporary file containing
the exact uploaded bytes; that parser scratch file is removed after native parsing.
The original upload remains in the bounded job spool until eviction or shutdown.

Project records are local to this computer. An owner is a recorded person/team,
not an authenticated assignment or notification. The downloaded brief uses the
latest saved revision per model and its immediate predecessor, while keeping
manual follow-up and machine results separate. Preserve your source IFC files
and include the complete external project directory in your own backup routine.

## Enterprise rules and purpose review

Follow **Project → Project rules → Model revisions → Purpose review**. In a project,
**Project rules** accepts one ZIP with `manifest.json`,
`rules/ruleset.toml` and native `rules/*.toml`. Download the public template there,
or generate it with `python tools/enterprise_rules_example.py <output.zip>`.
The manifest describes source, version, delivery purposes and evidence needs;
TOML rules compile through the existing rule compiler and IfcTester. Preview
parsing is not execution. Adoption requires a named confirmer and responsible
reviewer/team and freezes that exact content. Unsupported fields/checks remain
visible and cannot become successful observations. Excel, Word and PDF are not
executable inputs in this version.

**Purpose review** selects an adopted package, model revision, explicit object
scope and, where required, a real counterpart revision. Attach the exact source
IFC once if it was not retained previously. The check-only worker reuses existing
geometry and supports confirmed cancellation and a hard deadline. It saves a new
assessment rather than changing a model revision or its base four-rule report.

The existing Purpose engine produces sealed evidence partitions. The interface
shows BLOCKED or UNKNOWN whenever required observations fail, coverage is missing,
an operation is unsupported or evidence is absent. Empty scope is UNKNOWN.
READY is qualified to the listed purpose, evidence, version and scope, never a
general project acceptance or an authenticated engineering signature.

Problem cards show the element, requirement, observed result and next action
before folded technical data. Counts distinguish objects from evidence
observations. Machine failures, human evidence gaps and unexecuted checks have
separate labels. Blockers link to actual rules and the exact saved 3D element.
Non-geometric subjects retain their evidence. Human evidence needs an accepted
method, recorder, reference and basis tied to the current model/scope; progress
notes do not count. Saving a judgment leaves the old conclusion unchanged until
an explicit successor review. Rechecks distinguish source-model changes,
predicate/configuration changes, scope changes and new human evidence; deletion,
reclassification or exclusion is not a repair. Candidate causes stay unverified.
The purpose brief exports this same chain.

See [the package contract and API](../docs/product/enterprise-purpose.md).

One authorized source-backed case has exercised exact 3D selection, same-model
revision comparison, a real server restart and brief download with 2,055 meshes
and 1.07 million triangles. Under the earlier synchronous API, new uncached
content took 179.5 seconds to become usable on the recorded host. Imports now run
as separate jobs, with 30-second individual requests and a configurable hard
deadline (`--import-timeout-seconds`, default 600). Full regression reproduced a
network-change interruption during entry dependency loading and a failed viewer
module that remains failed on same-page retry. A standalone startup notice survives
missing modules/styles; failed viewer modules offer **Reload page** with the same
record URL. Geometry request/JSON failures retain in-place retry. Technical details
separate request, decode, viewer module, initialization and geometry loading phases.
The earlier cold viewport record lacks evidence to establish the same cause. This
is a measured case, not a larger-model capacity guarantee or engineering sign-off.
See the [case evidence and limitations](../docs/handoffs/model-case.md).

### OpenAI setup

Local rule guidance is available immediately. To enable optional generated advice,
set `OPENAI_API_KEY` in the terminal that starts the server; use your operating
system's secret/environment settings or a masked prompt. For example, PowerShell:

```powershell
$doctorKey = Read-Host 'OpenAI API key' -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new('', $doctorKey).Password
$env:OPENAI_MODEL = 'gpt-4.1-mini' # optional; this is the default
.\.venv\Scripts\python.exe doctor/serve.py
# When finished, stop with Ctrl+C and clear this terminal's key:
Remove-Item Env:OPENAI_API_KEY
```

Then click **Generate AI advice** on a selected result. The server calls the
OpenAI Responses API using the selected rule, actual/expected values, element
name/class/storey/tag and local engineering guidance. It sends no IFC bytes, mesh
arrays, file path or other findings. Facts and citation labels remain copied
from the local result; the generated summary/actions are suggestions. The request
sets `store: false`; this is not a promise about the provider's broader data
retention policy. Calls use the user's API account and may incur charges.

The key is never returned to the browser. A missing key leaves **Rule guidance**
available; a timeout, provider refusal or quota error is reported without claiming
that AI generated advice. Malformed provider output is a retryable service error,
not a missing-selection result; local evidence and guidance remain readable.
There is no automatic model edit or status change.
Transport and selection are covered by offline tests; evaluating a live model
requires a configured account and representative project examples.

Implementation notes and worker handoffs are in
[phase one](../docs/product/2026-10-24-product-phase1.md) and
[phase two](../docs/product/2026-10-25-product-phase2.md).

## Established example preview

A local, clickable preview of the D1 screen flow
([design](../docs/product/2026-09-16-doctor-d1-screen-flow.md), PR #11) for a
BIM manager who should not have to read JSON or use a CLI. It is an internal
prototype: not a release, not a public interface, not a compliance tool.

```bash
python doctor/serve.py        # then open http://127.0.0.1:8765/
```

## What it is

- **Presentation only.** The screens select, name and lay out what the internal
  adapter (A1) returns. They do not compute a verdict, member disposition,
  evidence carry-over, condition status or coverage reading. Where the
  Framework records no correspondence — a recheck disposition with no current
  subscope, because the pair no longer exists — the screens do not construct
  one, by key or otherwise.
- **One seam.** `serve.py` hands the browser A1's envelope unchanged:
  `mode`, `outcome`, `record` + `assessment_digest` or `refusal`, `elements`,
  and — beside a record only — `finding_details`. The envelope keys are fixed
  by the technical director. The runs a
  mode offers come from the adapter's `scenario_index()`, which runs nothing;
  the envelope's own `mode` is still checked against the chosen one before
  anything is rendered.
- **Provenance decided per citation.** Whether a label is true is a property of
  the one citation it sits beside, so the criterion is too: a fixture value is
  machine-visibly untrue and carries the fixture marker (`fixture/finding/…`,
  `fixture-determination/…`), and everything else does not. The envelope's mode
  is never consulted. One record can mix the two on a page — the model-reissue
  scenario cites six fixture-minted finding keys beside three real ones — and a
  per-envelope rule would call those six real validation output. Full sentences
  are in a legend on the same page, never hover-only. A policy `decision_basis`
  is not a citation and carries no marker, so the row says the source is not in
  the envelope rather than guessing whose decision it was.
- **A recheck is read, not re-derived.** The recheck screens answer what
  changed, what is still open and what to do next, in that order, with the
  evidence details behind a fold. The four carry-over states, their reasons, the
  changed aspects and the member dispositions are the record's; which side was
  re-issued is `changed_models` looked up against the same comparison's
  `producing` / `consuming`, and the role names are the request's handover. The
  wording lives in `static/recheck-model.js`, which has no DOM in it, and
  `tests/test_doctor_recheck_screens.py` runs it under Node (a missing Node
  skips locally and fails under `CI`). A value the page does not know is shown
  as it came and marked unrecognised. Check results and determinations are counted
  apart and never added together. Words: [recheck vocabulary](../docs/product/2026-10-02-doctor-recheck-vocabulary.md).
- **What a cited finding required comes from the run that record cites.**
  `finding_details` maps a `finding_key` to `rule_id`, `requirement_id`,
  `labels`, `citation`, `expected`, `actual`, `reason` and `status`, copied
  unchanged from the validation run the citing record names — the requirement
  that assessment was made against, never today's rule file. A citation has an
  entry only if its record names that run and the predicate and content it
  sealed are the run's; otherwise it has none, and no `null`. So every
  `fixture/finding/…` citation is without one, and after a rule edit the
  findings under the edited requirement are without one too, while the sealed
  citations of the first assessment keep theirs. An entry carries no
  `owner_role`, `severity` or `priority`: those are a rule author's metadata,
  not the project's assignment. It also carries no required value, data type
  or Revit parameter mapping; the run does not hold them. A first-check
  item lists the entry of each check result its conclusion cites; a recheck
  row lists its old citation's entry as the earlier run's words and says that
  having them does not make the row comparable.
- **An omitted key is words.** A key the envelope does not carry reads
  "记录未携带" — never `null`, `""`, `0`, `false` or a dash. A key carried as an
  empty string is a different fact: an empty `storey` is "无楼层归属", because
  the element has no storey assignment.
- **No bundled data.** Nothing under `doctor/` is a record, digest or refusal.
  Without the adapter the preview reports that input is unavailable.
- **No third-party code.** Python standard library (`http.server`) and plain
  HTML, CSS and ES modules; no build step, no `package.json`.
- **Loopback only, reads no clock, and writes nothing in this checkout.** The
  server itself writes no file; a local check (below) writes only under its
  checks directory. The adapter it calls does write, outside the
  checkout: each validation run copies the rule library into a scratch
  directory under the system temporary directory, puts the run's by-products
  there, and removes the directory when the run ends. The rule-edit recheck
  scenarios edit that scratch copy; `rules/` is never written.

## Two entries, kept apart

`fixture` is shown to the manager as **模拟示例**: simulated policy and
determinations, said so on every screen; it cannot be used for a project
decision and offers no export. `real` is shown as **随附项目的检查尝试** — not
"real input", because nothing can be imported: it runs the shipped project's own
policy and shows why that attempt did not start. Choosing or switching an entry
clears the result; a refused attempt is never shown as an example.

A refusal and a fault are different screens. A refusal is the system's answer
about the request's conditions and arrives as a result, worded from its code. An
exception or a missing adapter never reaches that screen: it is shown as a fault
of the program, with the technical message and no statement about a project.

## The path a manager walks

One path is carried end to end
([first-check path](../docs/product/2026-10-02-doctor-first-check-path.md)):
an ordinary first check, the items that need doing grouped by the team the
record assigns, one item with its elements, what to do, who handles it and what
a recheck must show — and then the same item in a recheck of that record. The
first-check screens are worded from `static/first-check-model.js`, which like
`recheck-model.js` has no DOM in it and is exercised under Node.

What qualifies a conclusion sits beside it and only where it applies: that its
evidence is simulated (decided per citation, as before), what a "can start"
covers, that "cannot be decided" is not a clean bill, that a team is an entry in
the record. General reading rules, identifiers and the Pack's English are one
fold away. The Chinese action sentences hold for one Pack version; a record
under any other is shown the Pack's own English. What a failing requirement asks
for is read only from the returned data's `finding_details`; the preview reads no
rule file. The record, activity and member screens were not revised and still
use internal terms.

## A third entry: a workspace run

```bash
python doctor/serve.py --workspace <dir> [--prior <dir>]
python -m internal.doctor_adapter --workspace <dir> [--prior <dir>]
```

`<dir>` is a workspace outside this checkout in which `epc-ct run` finished —
it holds `data/processed/canonical/run.json` and the
`reports/artifact_manifest.json` that vouches for it. The workspace is named
when the server is started and at no other time: nothing is uploaded, no
directory is searched for runs, and without `--workspace` the mode offers none.
`--prior` names an earlier run of the same scope, laid out the same way.

The adapter answers `GET /api/envelope?mode=workspace&run=workspace` with a
different envelope from the two above, and the tables below are the seam the
workspace screens are built against.

**The screens** (`static/workspace-screens.js`; counting and lookups in the
DOM-free `static/workspace-model.js`, exercised under Node by
`tests/test_doctor_workspace_screens.py`; every sentence in `static/vocabulary.js`):

- The home screen asks `/api/runs?mode=workspace` and shows a card only when the
  server offers a run. A failed question is said as one, not as "no workspace".
- `#/workspace/workspace` — the result: counts per status, which requirement was
  checked and where it comes from (the requirement's own `labels` and
  `citation`, never asserted by the page), and every result in a list that
  filters by status and by IFC Tag, name or GlobalId, with one result's detail
  beside it (`…/finding/<finding_key>`). The detail says where to go back to
  in the authoring tool (IFC Tag first, `tag_source` when there is none), what
  the requirement asked, the reason as the check wrote it, and — beside a pass —
  what a pass proves and does not. A passing finding carries no observed value,
  and no page says what one read.
- `…/compare` — both run ids, which one the server was told is earlier, the
  adapter's pairs grouped by their two statuses and counted, the rows only one
  run has counted apart, and the models the adapter lists as changed. Nothing
  here pairs two findings, and no word says a thing was fixed.
- A refused comparison has its own screen, worded per reason code with the
  adapter's text one fold away; a run that cannot be read is a program fault,
  on the fault screen.

No screen here says a verdict, a team or that work can start: no handover
assessment was made. The result words are the check's own — 通过、不通过、不适用.
The Chinese notes about one rule (`RULE_NOTES`) are used only under the rule set
identifier and version they were written for; any other rule set shows the
rule's English.

| Key | What it holds |
|---|---|
| `mode`, `outcome` | `"workspace"`, `"validation"`. No `record` and no `assessment_digest`: no handover assessment was made |
| `run` | `validation_run_id`, `as_of`, `ruleset` (`id`, `version`, `normalized_digest`), `checkers`, and `models` — each with `model_key`, `project_id`, `model_id`, `discipline`, `filename`, `content_sha256`, `tag_source` |
| `findings` | every finding of the run: `model_key`, `element_key`, `requirement_key`, `finding_key`, `status`, `expected`, `actual`, `reason`. An empty `element_key` is a model-level finding |
| `requirements` | `requirement_key` → `rule_id`, `requirement_id`, `specification_label`, `requirement_label`, `checker`, `labels`, `discipline_scope`, `citation`, `semantics_digest`. No `owner_role`, `severity`, `priority` or `stage` |
| `elements` | `element_key` → `name`, `ifc_class`, `storey`, `global_id`, `model_key`, and `tag` where one could be read |
| `comparison` | only with `--prior`; below |

`tag` is the element's IFC `Tag` attribute, read from the model file the
workspace's project manifest names — and only when that file's SHA-256 is the
content digest the run recorded. It is for finding the element in its authoring
tool and takes part in no key. An element whose file states no tag has no `tag`
key; a model whose file is missing or is a different version says so in
`tag_source` (`model-file`, `model-file-not-located`, `model-file-differs`) and
none of its elements has one.

`comparison` is made by the adapter, never by a screen:

| Key | What it holds |
|---|---|
| `prior_run` | the earlier run, in the shape of `run` |
| `changed_models` | `model_key`, `prior_content_sha256`, `current_content_sha256` for each model whose content digest differs |
| `pairs` | one row per element × requirement both runs evaluated: `model_key`, `element_key`, `requirement_key`, and `prior` and `current`, each the finding's `finding_key`, `status`, `expected`, `actual`, `reason` |
| `not_re_evaluated` | rows only the earlier run has: `prior`, and `element_in_current_run` |
| `newly_appearing` | rows only the current run has: `current`, and `element_in_prior_run` |
| `prior_elements` | display rows for elements the current inventory no longer holds |

A row on one side only is never a pass and never a correction. The adapter says
nothing was fixed, resolved or improved anywhere: it gives two statuses.
`element_in_…_run` is `null` for a model-level row, which names no element.

Which run is the earlier one is whatever the caller named; the adapter reads no
clock and has no way to know.

When the two runs did not ask the same question of the same models, the whole
request is refused — `outcome: "refusal"`, `refusal: {code, text, reasons}`, and
nothing else: neither run's findings and no comparison. `reasons` lists every
failed precondition, `code` is the first.

| Code | The two runs differ in |
|---|---|
| `ruleset-id-differs`, `ruleset-version-differs`, `ruleset-digest-differs` | the rule set's identifier, version or normalized digest |
| `requirement-set-differs` | which requirements were evaluated |
| `requirement-semantics-not-recorded` | nothing provable: a run recorded no predicate digest for a requirement |
| `requirement-semantics-differs` | a requirement's predicate digest |
| `checker-differs` | the checkers, their versions or configuration |
| `as-of-differs` | the run's logical date |
| `model-set-differs` | the set of models |

A directory that holds no finished run, or a run document that is not the one
its manifest describes, is a fault and is reported as one — never as a refusal
and never as a result.

## Interface language

The viewer chooses Chinese or English on every screen. The choice is read when
the page loads (`?lang=en`, then what this browser chose before, then Chinese)
and changing it reloads the same `#/…` route: the run, the record, the mode and
the element shown do not change, only the words.

English is a second wording table, never a second page:

- `static/vocabulary.js` holds the Chinese tables and `static/vocabulary-en.js`
  the English ones, key for key; `static/words.js` hands every screen the table
  for the chosen language. A table with no English yet is Chinese in both.
- In English, a screen whose words are not all translated is not drawn. It says
  "This page has not been translated yet" and offers the same page in Chinese.
  `TRANSLATED` in `static/app.js` lists the screens drawn in English.
- Where the record, the Pack or this repository's product documents already say
  it in English — what to do, what a recheck must show, an activity's name, what
  a verdict means — the English page shows that text, not a translation of the
  Chinese gloss. What the record carries is read from the record.
- A wording that carries a count has a form for one and for more (`one`,
  `other`) in both tables, read with `plural()`; a wording whose placeholders
  are page pieces rather than text is filled with `compose()`, so each language
  keeps its own punctuation. Both are in `static/i18n.js`.
- A module that adds a page can keep its own two tables and register them with
  `bilingual(name, zh, en)` from `static/i18n.js`, as `static/language.js`
  does; it does not have to add to the central tables. The parity tests in
  `tests/test_doctor_english.py` read every registered pair.

The English entries, which of them are quoted originals and which carry domain
meaning, are listed in `docs/product/2026-10-03-doctor-english-vocabulary.md`.

## A fourth entry: a local check of your own IFC

```bash
python doctor/serve.py [--checks-dir <dir>] [--max-model-bytes <n>]
```

A user's own IFC4 files, checked in a workspace made for that one check, against
the one rule set the local check offers: `product-validation` 1.0, a product
validation exercise (one rule, PV-001: applicable air terminals declare one of
four predefined types). It is not a general BIM quality, IFC compliance or
delivery check; a FAIL does not mean your model has a delivery defect, and a model with
nothing applicable says so and is never shown as a pass. The shipped
`epc-delivery` rule set stays in the checkout and the bundled example and is not
offered here (product decision of 2026-10-03,
`docs/product/2026-10-03-pm-local-ifc-scope-decision.md`, §1; offered set:
`OFFERED_RULESETS`). Code: `internal/doctor_adapter/local_check.py`; tests:
`tests/test_doctor_local_check.py`.

**On the page.** The home page's card leads to `#/local`, which says, before
anything is chosen, what is checked and only that, where the requirement comes
from, how to read FAIL, PASS and nothing-applicable, and what this computer keeps,
where, and how to clean it up. Then: choose `.ifc` files (each is copied to the
server as it is chosen), declare each file's discipline, confirm the rule set,
see the scope the server plans, run. A finished check is `#/local/<check_id>`:
first the exercise and any model with nothing applicable, then the summary and
the workspace screens' result list and details, then the rule in full, the scope
it ran with (including the programme the check filled in, with no due date), and
its directory. A result's detail gives the result and its reading limits, then
what to change (pointing at the Revit check), then where to find the object and
the rule's own words. Earlier checks are
listed on `#/local`. The words are `static/local-words.js`, registered in both
languages with `bilingual()`; the screens are `static/local-check.js`.

**Starting it so the records can be found.** From the repository directory, in
your own terminal:

```bash
python doctor/serve.py --checks-dir "%USERPROFILE%\Documents\BIM Doctor checks"
```

A folder outside `AppData` is recommended. A server started from inside a
packaged (MSIX) app — the Claude desktop app's terminal, for one — has its
writes under `%LOCALAPPDATA%` redirected by Windows into the package's own
folder (measured: `AppData\Local\Packages\Claude_…\LocalCache\Local\…`), where
File Explorer, looking for the printed path, finds nothing. Writes under the user
profile (`Documents`, the profile itself) and other drives are not redirected.
The server cannot tell before the directory exists; once the first file is
kept, `GET /api/local` reports `checks_dir_on_disk` (the directory's real
path), and the page shows it, with this explanation, wherever it differs from
the name.

**Where it writes.** Everything — the files a user hands over and every check
run on them — is kept under the *checks directory*: `--checks-dir`, else
`$EPC_DOCTOR_CHECKS_DIR`, else `epc-control-tower/doctor-checks` in the user's
state directory (`%LOCALAPPDATA%`, or `$XDG_STATE_HOME` /
`~/.local/state`). It is refused inside any checkout, printed when the server
starts, and returned by `GET /api/local` and with every check. Nothing is
written in this checkout and nothing anywhere else; the tests count every write
a check attempts. Nothing is deleted for the user either: a check stays until
its directory is removed.

```
<checks dir>/uploads/<sha256>.ifc          a file as it arrived, named by its content
<checks dir>/checks/<check_id>/
    check.json                              the scope the check ran with (written last)
    control-tower.toml, projects/local/     the workspace: the models and their manifest
    rules/<rule set>/, ids/                 a copy of the rule set, and what it compiled to
    data/processed/canonical/run.json       the run the workspace entry reads
    reports/artifact_manifest.json, reports/ids/
    coverage/                               the run's coverage record, beside it
```

Why it is laid out like this was measured before it was designed: a model
dropped into `projects/` re-keyed every published canonical finding; a workspace
naming the checkout's `rules/` rewrote `ids/` in the checkout; the default
exporters reach the BCF archive's entry limit on a real model; `epc-ct run`
kept a coverage record in the state directory without saying so. So the rule set
is copied (its identity is of parsed content, not of a path — the copy's
digests are the recorded ones), only the JSON exporter runs, and the coverage
record is kept in the check's own directory.

**A check is named by what it checked**: its `check_id` digests the rule set
(identifier, version, normalized digest, definitions digest), the logical date
and each model's name, discipline and content digest. Asking again for the same
check runs it again into the same directory and gives the same bytes. A model's
`model_id` is spelled from its file name (or, for a name with nothing a code can
be spelled from, from the name's digest), all in project `local`, so two checks
of one file name have the same model key and can be compared.

| Endpoint | Body | Answer |
|---|---|---|
| `GET /api/local` | — | `checks_dir`, `checks_dir_on_disk` (its real path once it exists, else `null`), `kept` (`uploads`, `checks`: what is there now), `as_of`, `max_model_bytes`, `rulesets` (the offered ones only, each `name`, `id`, `version`, `normalized_digest`, `definitions_digest`, `title`, `description`, `requirements` as in the plan), `disciplines` (every discipline any rule set here names) |
| `POST /api/local/models?filename=<name>` | the file, `application/octet-stream` | `{outcome: "staged", model: {upload, filename, byte_count, ifc_schema}}` or a refusal |
| `POST /api/local/plan` | `{ruleset, models: [{upload, filename, discipline}]}`, `application/json` | `{outcome: "plan", plan}` or a refusal |
| `POST /api/local/checks` | the same request | `{outcome: "finished", check: {check_id, location, scope}}` or a refusal |
| `GET /api/local/checks` | — | `{checks: [{check_id, location, scope}]}`, every finished check by identifier |
| `GET /api/local/envelope?run=<check_id>[&prior=<check_id>]` | — | the workspace entry's envelope for that check, unchanged — including its comparison refusals |

`plan` (and a check's `scope`, which is the plan without `location`):

| Key | What it holds |
|---|---|
| `check_id`, `location` | the check's name, and the directory its result will be kept in |
| `ruleset` | as in `GET /api/local` |
| `requirements` | `requirement_key` → `rule_id`, `requirement_id`, `specification_label`, `requirement_label`, `checker`, `labels`, `discipline_scope`, `citation` — the workspace entry's requirement without its `semantics_digest`; no `owner_role`, `severity`, `priority` or `stage` |
| `models` | `model_id`, `model_key`, `filename`, `discipline`, `content_sha256`, `byte_count`, `ifc_schema`, by `model_key` |
| `as_of` | the logical date, from this checkout's configuration |
| `programme` | the stages the rule set's rules name, each with an empty `due`: a user's model brings no programme, and the pipeline needs one that covers every rule stage |
| `exporters` | `["json"]` |
| `geometry` | `false`: no bounding box is computed (`execute(..., with_geometry=False)`). The JSON document carries none, and an element IFC allows to have no shape used to end the whole check with `RuntimeError: Representation is NULL`; its result, Tag and GlobalId are now read like any other |

The run's own identity in the envelope says what the plan said — rule set,
models, date — and the tests hold the two equal.

**A refusal is a result** in the workspace entry's shape — `outcome:
"refusal"`, `refusal: {code, text, reasons}`, every reason listed, `code` the
first — and each reason's text says what to do next. A reason about one file
names it as `filename`. The screens word it from the code.

| Code | When |
|---|---|
| `busy` | another check is running; one runs at a time |
| `no-model` | no file was chosen |
| `model-too-large`, `model-incomplete` | the file is over `max_model_bytes` (refused unread), or arrived short |
| `not-an-ifc` | the file does not begin with an IFC-SPF header naming a schema |
| `model-name-invalid` | the name is not a plain file name ending in `.ifc` |
| `unknown-model` | the request names a file the server does not hold |
| `duplicate-model` | the same file, file name or model code chosen twice |
| `unknown-ruleset` | not a rule set the local check offers (`product-validation` 1.0 only) |
| `discipline-not-declared`, `unknown-discipline` | a file's discipline is missing, or not one any rule set here names |
| `unsupported-schema` | a checker of the chosen rule set does not read the file's schema — IFC2x3 for the IDS checker — decided from the same registry before any model is opened, and the reason the pipeline would give |

A request of the wrong shape is `400`; a check that fails while it runs is a
fault (`500`, with the message), and its directory is removed first, so a
failed check leaves nothing behind and is not listed.

**Nothing applicable is not a pass.** A model with no object a rule applies to
gets one model-level `N/A` finding per requirement and no `PASS`; the envelope
carries exactly that.

**Only this machine's own pages may ask.** The server listens on 127.0.0.1.
Every `/api/` request must name it as its `Host` (`127.0.0.1`, `localhost` or
`[::1]` with its port), which stops a rebound DNS name; a request that sends
something must carry the endpoint's JSON or binary type, which a page on another
site cannot send without a preflight nothing here answers, and an `Origin`, if
given, must be this server's.

## Not in this preview

Starting a recheck, marking an item resolved, assigning or notifying anyone and
exporting a recheck record (the recheck screens say so and carry no button for
them); model/version, Pack and activity selection catalogues (F2), exhaustive refusal
diagnostics (F4), Revit navigation and determination originals (F5), condition
discharge and risk authorisation (F6, E2), comparing two local checks on the
page and deleting a local check from the page (both are files on disk, removed by
hand), separated refusal message text (F8), and the Singapore research view.
