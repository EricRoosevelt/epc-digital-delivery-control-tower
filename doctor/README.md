# BIM Doctor — D1 internal preview

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

## A fourth entry: a local check (no screen yet)

```bash
python doctor/serve.py [--checks-dir <dir>] [--max-model-bytes <n>]
```

A user's own IFC files, checked against one of the rule sets this checkout
carries (`rules/*/`), in a workspace made for that one check. The server has
the endpoints; the screens come in a later packet and build against the tables
below. Code: `internal/doctor_adapter/local_check.py`; tests:
`tests/test_doctor_local_check.py`.

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
| `GET /api/local` | — | `checks_dir`, `as_of`, `max_model_bytes`, `rulesets` (each `name`, `id`, `version`, `normalized_digest`, `definitions_digest`, `title`, `description`), `disciplines` |
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

The run's own identity in the envelope says what the plan said — rule set,
models, date — and the tests hold the two equal.

**A refusal is a result** in the workspace entry's shape — `outcome:
"refusal"`, `refusal: {code, text, reasons}`, every reason listed, `code` the
first — and each reason's text says what to do next. The screens word it from
the code.

| Code | When |
|---|---|
| `busy` | another check is running; one runs at a time |
| `no-model` | no file was chosen |
| `model-too-large`, `model-incomplete` | the file is over `max_model_bytes` (refused unread), or arrived short |
| `not-an-ifc` | the file does not begin with an IFC-SPF header naming a schema |
| `model-name-invalid` | the name is not a plain file name ending in `.ifc` |
| `unknown-model` | the request names a file the server does not hold |
| `duplicate-model` | the same file, file name or model code chosen twice |
| `unknown-ruleset` | not a rule set this checkout carries |
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
discharge and risk authorisation (F6, E2), screens for the local check above,
separated refusal message text (F8), and the Singapore research view.
