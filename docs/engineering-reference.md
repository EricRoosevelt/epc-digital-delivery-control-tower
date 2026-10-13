# Engineering reference

Read the relevant section when changing the pipeline, rules, or published artifacts.
This is technical context, not an approval workflow. AGENTS.md defines how work proceeds.

## Where to extend

The pipeline has three seams, and a fork should be adding an implementation to
one of them rather than editing stages. They are protocols in
`epc_control_tower/protocols.py`, and the one place implementations are
registered is `default_registry` in `epc_control_tower/registry.py`.

| You want to change | Implement | Register as |
|---|---|---|
| *How a requirement is evaluated* | `Checker` | a checker |
| *What counts as one actionable issue* | `GroupingPolicy` | a grouping policy |
| *Where results go* | `Exporter` | an exporter |

Each `Requirement` names the checker that evaluates it, and the registry routes
on that name. A rule pointed at a checker that does not exist — or at one that
cannot evaluate its facets, or read its IFC schema — is rejected while planning,
before any model is opened.

**These three seams are extension points, not a list of the product's phases.**
They describe the shapes the current pipeline can absorb without being edited.
Work that is not one of those shapes does not become one by being forced through
the nearest seam, and the table above is not a roadmap. Two consequences worth
stating, because both have been guessed wrong already:

- **A purpose assessment, if it is ever built, is approved between `check` and
  the compatible group** — after requirements and facts have been validated,
  before findings are grouped into issues. It is not a `Checker` (it does not
  evaluate a requirement against a model), not a `GroupingPolicy` (it does not
  decide what counts as one actionable issue), not an `Exporter` (it does not
  move results anywhere), and it does not belong in `default_registry`.
  Registering it as one of the three would make an approval step look like a
  pipeline component and put a decision inside a projection.
- **`Finding.is_issue`, `Issue`, and the `Requirement` metadata fields
  (`owner_role`, `severity`, `stage`, `priority`, `labels`) are contract 1.6
  validation and legacy-compatibility concepts, and stay that way.** `is_issue`
  records that a check failed in a way that warrants a topic; `Issue` is the
  grouping of such findings; the `Requirement` fields carry what a rule means
  and are what lets the frozen legacy archive be rebuilt byte for byte from rule
  metadata. Specifically, none of them is:
  - a Purpose readiness verdict — nothing here says a deliverable is fit for a
    purpose;
  - a blocker consequence — `priority` says when somebody will get to a failure,
    not what that failure stops;
  - a final responsible-role decision — `owner_role` is the role a *rule author*
    expects to answer for the rule, which is an input to such a decision and not
    the decision.

  Reusing any of them as one would silently redefine every published number that
  currently depends on them — a published-contract change that needs measured comparison.
- **`discipline_scope` expresses validation applicability only.** It is meant to
  say which disciplines a requirement is evaluated against — which models the
  rule applies to at all.
  - *Today:* nothing that evaluates a requirement reads it. It reaches the rule
    set digest, issue labels and the legacy projection, and nothing else; a rule
    is evaluated against every model whose elements match its applicability
    facet. `pcert-sample`'s structural walls are evaluated by R-001 and R-002,
    both scoped to Architecture, and the eight PASS findings that produces are
    published.
  - *Target:* enforcement is deliberately not switched on. A model declares one
    discipline string, so a merged model cannot say it is more than one, and
    enforcing that single value silently drops whole rule families (measured in
    ADR 0004 §4.3). It waits for an explicit multi-discipline declaration and a
    coverage record that names every requirement not evaluated, and why.

  It does not express a *directional handoff*: "MEP hands this to
  Architecture" is a statement about who gives what to whom, and no field in
  this package carries it today. Direction is Pack data when Packs exist. Do not
  read a scope tuple as an arrow, and do not overload it into one; a set of
  disciplines that quietly becomes a from/to pair is unreviewable and would
  re-key every requirement that carries it.

Registration is explicit and in-tree. Dynamic discovery is deliberately absent:
an entry-point mechanism is a promise to third-party packages about names,
versions and compatibility, and making that promise before anything outside this
repository depends on it would fix the wrong details.

Some rules of thumb that follow from the shape:

- **An exporter receives a `RunBundle` and nothing else.** If yours needs to
  reopen an IFC file, consult a checker, or branch on a rule id, the information
  it wants belongs in the domain model. Bounding boxes went that way already —
  they are a stage and an entity, not something the BCF exporter fetches.
- **A checker's own source format is its business.** Compiling IDS is an
  internal detail of `IdsChecker`, not a stage. Making it a stage is what put
  the project's ceiling at whatever IDS 1.0 can express.
- **Constants have three different homes**, and picking the wrong one is how a
  settings file becomes a bag nobody can reason about:
  - what a *project* contains → its manifest, `projects/<id>/project.toml`
  - what a *rule* means (severity, owner role, stage) → the rule
  - what the *fixture happens to contain* (counts, digests) → tests and
    `docs/contracts/`, never production code
  Genuine runtime knobs — output locations, which exporters run, which grouping
  policy, the logical `as_of`, and which project the legacy writers publish —
  go in `control-tower.toml` at the repository root. There are a handful, and
  keeping it that small is the point: a settings file that accepts everything
  explains nothing.

**Adding a rule should not touch this package either.** A rule is one TOML file
under `rules/<ruleset>/`, carrying its own severity, owner role, stage,
discipline scope and citation. `checker = "ids"` compiles it into the IDS
document that `ids/` holds as a build product; `checker = "completeness"` routes
it to the cross-model checker instead and never reaches that document. A rule
naming a checker the library does not know is rejected when the library loads,
because a delivery requirement the pipeline silently declines to evaluate is the
worst outcome available.

A checker-specific parameter — `CompletenessChecker`'s `name_pattern`, say —
stays in the rule file, and the checker reads it back from there. A
`Requirement` carries identity and metadata, not a payload every checker would
have to agree on the shape of.

**A finding may be about something that is not there**, and what it names then
is a decision, not a default. The rule: *a finding names the smallest thing that
exists and that a person can go and look at.* Usually an element, including for
an absence — "this space has no terminal" points at the space. When no element
can stand for it, the model: `element_key` is empty and the finding is
model-level. Nothing is ever minted for a thing that was not modelled. A pass is
stricter and stays so: it says a specific thing was checked and was correct, so
it always names that thing. See `domain.Finding` for the four legal shapes.

**Adding a project should not touch this package.** Drop a directory under
`projects/` with a `project.toml` and the models beside it; discovery is a glob.
Give each model a `model_id` that means something inside the project — two
projects may both have an `architecture` — and leave `model_key` alone unless
you are pinning a published identity, because it is derived as
`<project_id>.<model_id>` and is what every join and every `element_key` is
built from.

That is true of the package, not of the published identities:

- *Today:* every project under `projects/` joins one shared run, and
  `validation_run_id` digests every model in it, so adding a project re-keys
  every other project. Measured in ADR 0004 §3: the other projects' findings
  stay content-identical, but 0 of 121 finding keys and 0 of 21 issue keys
  survive and all 21 BCF markups change — and a run that stays under the BCF
  cap still exits 0. In this repository the diff gate catches it; in a local
  run nothing does. A project
  that is not part of the published contract runs in its own workspace
  (`epc-ct --repository-root <workspace> run`), which changes no published byte.
- *Target:* adding a project to the shared published run stays a contract
  change until project-scoped identity exists; that migration is deferred
  (ADR 0004 §5.3).

Two exporters are named `Legacy…`, and the reason is now the same for both:
they reproduce **frozen identity derivations**. `LegacyPbipAdapter` always did.
`LegacyBcfExporter` used to also know the R-005 rule family and the HVAC model,
and no longer does — priority, stage, labels and the assignee's role come from
rule metadata, and the published archive is rebuilt from that metadata byte for
byte. What keeps it is that the published archive's `ReferenceLink`s carry
legacy finding keys, which no amount of metadata can produce.

`BcfExporter` is the general one: issues and their history in, BCF out, no rule
ids and no filenames. Both are pure projections of the canonical model, both
are pinned by byte-equality tests, and both `Legacy…` writers retire together
in Phase 5. Do not extend them; add alongside.

A **scope** on an exporter is not the same thing as rule-awareness, and the
distinction is worth keeping straight when you read those two. Narrowing to one
project and one frozen rule set version says *which slice of the run is
published*; asking "is this rule R-005A?" says what a rule means. The first is
legitimate and stays; the second is what Phase 4 removed.

### Running it

```bash
epc-ct run          # every stage, then every enabled exporter
epc-ct check        # validate and report; see below for what it writes today
epc-ct components   # what is registered
epc-ct snapshot     # does the published contract still match its record?
```

`check` does not yet keep the promise its help text makes:

- *Today:* it writes files. It rewrites every checker report under
  `reports/ids/` and recompiles `ids/<ruleset>_v<version>.ids` — thirteen tracked
  files on the shipped fixture, none of them listed in `artifact_manifest.json`.
  `--reports-dir` moves the reports elsewhere but the compiled rule document is
  still rewritten, and a new project's reports are added to the tree. Do not run
  it on a model whose name should not reach this repository; use a workspace.
- *Target:* by default `check` changes no persistent file of the user's and no
  repository artifact; asking for reports explicitly is the visible exception,
  and `run`'s published bytes are verified separately (ADR 0004, P5).

Without installing the package, `python -m epc_control_tower.cli …` does the
same. The scripts under `src/` are shims kept for the published entry points
and retire with the legacy adapters; new work goes in the package.

One test needs a tool the test suite does not install. `tests/test_ids_syntax_audit.py`
runs buildingSMART's `ids-tool` over the rule documents, and skips with
instructions when it is absent:

```bash
dotnet tool install --global ids-tool.CommandLine --version 1.0.124
```

CI installs it and sets `EPC_REQUIRE_IDS_AUDIT=1`, which turns that skip into a
failure — a gate that disappears when its tool is missing is not a gate.

## Full verification when needed

Use the project's `.venv`. CI already runs the full suite; do not repeat a
successful run on the same code just because another role is reviewing it.
For pipeline, identity, rule, dependency, or published-contract changes, use:

```powershell
python -m ruff check .
$env:EPC_REQUIRE_IDS_AUDIT = "1"
python -m pytest -p no:cacheprovider tests -q
python -m epc_control_tower.cli run
git diff --exit-code -- data/processed reports
git status --porcelain --untracked-files=all
python -m epc_control_tower.cli snapshot
python src/validate_dashboard.py --mode core
python src/validate_pbip.py
python -m pip check
```

Report failures and skipped checks accurately. The IDS audit is required when
claiming the full gate passed. Local untracked role notes are not generated
artifacts and need not be removed to obtain an empty status.

For intentional published-contract changes, document the version in CHANGELOG.md
and the relevant data contract, regenerate, then run
`epc-ct snapshot --refresh --contract-changed`. Do not weaken determinism tests
to hide a regression. Snapshot expectations and domain invariants make different
promises; update only the promise that deliberately changed.
