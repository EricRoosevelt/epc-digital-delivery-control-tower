# Changelog

Notable changes to this project, and in particular to the **published data
contract**: the column shapes, the identity derivations, and the exact bytes of
the artifacts under `data/processed/` and `reports/`.

A contract version has a recorded snapshot under `docs/contracts/`. Changing
what a run publishes means bumping the contract version, describing the change
here, and then refreshing the snapshot:

```bash
epc-ct snapshot --refresh --contract-changed
```

The refresh refuses to run until this file describes the version, so the record
of what moved exists before the expectation that says it did.

## Unreleased

### Two decisions recorded before the work that depends on them

Both are written down first on purpose. One is a criterion that becomes
worthless the moment it is chosen after seeing the result it judges; the other
is a finding that would read as an excuse if it appeared only after the feature
it rules out.

#### What makes a field on a rule legitimate

Phase 4 replaces `LegacyBcfExporter` with a pure one, and the published archive
`b3c6f51abc96…` may not move. Measured against the live bundle, the metadata
cannot currently produce it: `Issue.priority`, `Issue.stage` and `Issue.due` are
all empty, `assignee_role` comes from a constant on the grouping policy rather
than from any rule, and there is no priority field anywhere in the rule schema.

The obvious repair — add whatever fields make the bytes match — would move the
hardcoding rather than remove it, and would be indistinguishable from having
removed it once the hash goes green. So the test is fixed now, before the
comparison is run:

> **A field on a rule is legitimate if and only if somebody forking this
> project, writing their own rules for their own building, would set it for
> their own reasons. If its only use is to reproduce one archive in this
> repository, it is padding.**

Applied to the constants currently in `legacy_contract.py`, before any hash was
computed:

| Constant | Verdict | Home |
|---|---|---|
| `Priority` `"Medium"` | legitimate | rule metadata — every delivery ranks its requirements, and severity is not priority: an ERROR nobody will fix this month outranks nothing |
| `Stage` `"Coordination"` | legitimate | already on the rule; needs carrying onto the issue |
| `AssignedTo` | legitimate as a **role** | already on the rule as `owner_role`; the `@example.invalid` address is a rendering, not a fact |
| `Labels` `("HVAC","IDS","ProjectAssumption")` | legitimate | rule metadata — a fork labels its own topics; `HVAC` is already `discipline_scope` |
| `TopicType` `"Issue"` | not rule metadata | run configuration — a property of how this project files issues, identical for every rule |
| `CreationAuthor` | not rule metadata | run configuration — who is writing the archive |
| BCF project name and GUID | not rule metadata | run configuration — the published archive names the *tool*, not the project, and no `Project` in any manifest is called `EPC Digital Delivery Control Tower` |
| The topic description prose | **undecided until measured** | it is R-005-family wording; whether a rule field for it is legitimate or padding is exactly the question the criterion above will have to answer |

The last row is left open deliberately. Naming the doubtful case in advance is
what stops the criterion from being applied only to the easy ones.

#### Why a cross-run issue ledger is a phase, not a feature

`ageing`, `overdue` and `burndown` were listed together as things Phase 4
unlocks. Only one of them is reachable, and the reason the other two are not is
worth more than the feature would have been.

Measured on the shipped run: 21 issues, 21 events, **one** distinct timestamp,
**one** event type. Ageing is `as_of − opened_at`, and both are the same logical
instant, so ageing is identically zero for every issue and always will be from a
single run. Burndown needs a series and there is one point. `overdue` is
different in kind — it needs a `due`, which is a deterministic function of
`as_of` and rule metadata — so `due` and `overdue` land in Phase 4 and the other
two do not.

The obvious fix is to persist issue state across runs and key it on `issue_key`.
That does not work, and the measurement says so:

| | shipped run | one inert rule added |
|---|---:|---:|
| issues | 21 | 21 |
| failing findings | 24 | 24 |
| subjects `(project, model, element)` | identical | identical |
| **`issue_key`s surviving** | — | **0 of 21** |

The added rule fails nothing and fixes nothing — every window in the fixture
already declares `IsExternal` — so not one answer changed. Every key changed
anyway, because `build_issue_key` takes `validation_run_id`, and that folds in
the rule set.

So a ledger keyed on `issue_key` would treat every issue as brand new on the day
a rule is added. Rule sets grow — that is what the whole of Phase 3 was about —
and an ageing figure that resets whenever the rule library moves fails precisely
in the situation it exists to describe: a long-running project whose
requirements are still being written.

**What the ledger phase actually needs is therefore not persistence but a
run-free identity for the subject of an issue** — something like
`(project_id, element_key, requirement_key)`, which the measurement above shows
is stable across exactly the change that destroys `issue_key`. That is a
question for the identity model, of the same kind as the three-way split in
Phase 1, and it has consequences that a storage feature does not: a second key
space to keep unique, a decision about what happens when an element is remodelled
and its `GlobalId` changes, and a rule for what a subject means once the
requirement it names is deleted from the library.

Pinned as `IssueIdentityStabilityTests` in `tests/test_grouping.py`, so the
finding stays true rather than merely having been observed once.

### Data contract 1.4 — the rule set gets a version that means something

`rules/epc-delivery/ruleset.toml` said `version = "1.0"` for three contracts
while the rules went from seven to twelve. The repository's own record is the
measurement:

| snapshot | rule set | requirements | normalized digest |
|---|---|---:|---|
| `contract-1.1.json` | `epc-delivery` **v1.0** | 9 | `93e3354b…` |
| `contract-1.2.json` | `epc-delivery` **v1.0** | 13 | `7b5bb6d4…` |
| `contract-1.3.json` | `epc-delivery` **v1.0** | 14 | `8a5585c3…` |

One name, three rule sets. And `ids/epc-delivery_v1.0.ids` — the compiled
document a delivery would archive — held three different byte sequences under
that one filename.

**Nothing was broken by it**, and that is worth stating plainly before the fix,
because it is the reason nobody noticed. Two measurements:

- Adding five rules with the tag unchanged moves the normalized digest
  (`93e3354b…` → `8a5585c3…`) and therefore every finding key. Identity was
  never at risk. The digest was doing its job the whole time.
- Bumping the tag alone, changing no rule, re-keys **all 121 canonical
  findings**. A version bump costs exactly as much as a rule change.

So the tag is not carrying identity, and raising it is not free. Which is
precisely why "leave it to the author's discretion" was the wrong answer: it
would make a field that re-keys every published artifact a matter of taste.

### What the version is for, given the digest already exists

The digest identifies; the version *names*. Nobody writes "we validated against
`8a5585c3efc9c774…`" in a delivery plan, and no two digests can be compared for
which came first. A rule set version is the readable handle for the thing the
digest identifies — and a handle that points at three different things is worse
than no handle at all.

It also is not a duplicate of the contract version. The contract version says
what this project **publishes**; the rule set version says what it **asked
for**. Different questions, different audiences, and the second is the one a
project hands to a supplier.

### The rule, and where it is enforced

> **A `(ruleset_id, version)` pair names exactly one set of rules.**

Raise the **major** part when the rule set can reject something it used to
accept — a rule added, or an existing one tightened — because a model that
passed before can fail now. Raise the **minor** part for anything else that
moves the digest: wording, ownership metadata, a rule removed or relaxed.

The rule set is therefore **2.0**, not 1.1. Five rules were added, two of which
fail elements in the shipped fixture; a model that passed the seven-rule set can
fail the twelve-rule one. That is not a point release.

No second ceremony was created for it. `epc-ct snapshot --refresh` already is
the moment somebody says out loud what moved, so the check rides on that: the
refresh now refuses when the incoming rule set reuses a version tag that a
recorded snapshot already pairs with different rules. Checked against every
snapshot on record, not only the previous one, so reverting a tag to reuse an
old number is caught too.

Only the mechanical half is machine-checkable. Whether a change was major or
minor is a judgement, and `ruleset.toml` now states the rule that judgement is
made against, which is the most that can honestly be automated.

**The counterfactual is pinned as a test.** `ruleset_version_conflicts` is run
against the snapshots for contracts 1.2 and 1.3 and must refuse both — the two
refreshes that actually happened and should not have. Those snapshots are left
exactly as they were recorded: they are the account of what this repository did,
and rewriting them to make a new rule look retroactively obeyed would be the
same class of dishonesty the ceremony exists to prevent.

### Unchanged

The eight published CSVs and the BCF archive are byte-identical, and
`run_id ids-v0.1-8706ef58303bfd11` still resolves — the legacy projection is
scoped to the frozen v0.1 document, which this does not touch. Canonical keys
all move, because the rule set version is part of the validation identity, which
is the whole point.

`ids/epc-delivery_v1.0.ids` is replaced by `ids/epc-delivery_v2.0.ids`. The
filename carries the version for exactly this reason, and now it tells the
truth.

Snapshot: `docs/contracts/contract-1.4.json`.

### Data contract 1.3 — a second checker, and what a finding points at

`Checker` has been a protocol since Phase 1 with exactly one implementation,
which is another way of saying it had not been shown to be a seam. There are two
now, and the second was chosen to be a rule IDS **cannot state at all** rather
than one it states awkwardly.

IDS validates one model against one document. Every facet it has asks a question
about an element and answers it from that element's own file; there is no
construct for "and the same must be true over there", because the document never
sees a second model. `CheckerCapabilities.requires_federated_context` was
declared in Phase 1 for exactly this and had never been used.

**R-010** — every discipline model must carry at least one coordination
reference that a sibling model also carries. It is the precondition of
federation: models with no common point cannot be overlaid, and clash detection
over them means nothing. The shipped fixture answers differently per project and
both answers are true. The PCERT models share an `origin` and a `geo-reference`
proxy, so they federate — three passes, each naming the shared element it found.
The ISO reference-view models are three unrelated buildingSMART samples that
happen to share a directory, and they share nothing — three failures.

### The decision: what `element_key` is for a finding about a missing thing

Made explicitly, because the alternative was for a default to establish itself
by accident. The rule:

> **A finding names the smallest thing that exists and that a person can go and
> look at.**

Usually that is an element, *including* when the finding is about an absence:
"this space has no terminal" points at the space, which exists, is already in the
element register, and is where a coordinator would actually go. Some absences
have no such context — "this model carries no shared setout reference" — and
there the smallest existing thing is the model. `element_key` is then empty.

`Finding` therefore has a fourth legal shape: `FAIL`, applicable, an issue, and
no element. What was rejected, and why:

- **Mint a key for the element that should have been there.** Keeps the table at
  three shapes and every join unconditional, and puts a row in the element
  register for something that does not exist. This is the same fabrication the
  project already refuses when it publishes `actual` empty rather than guessing
  at a value it cannot observe. A missing wall with a UUID is worse than an
  honest blank.
- **Report it as N/A.** Silently downgrades "what this required is not here" to
  "this did not apply". That was not a hypothetical: it is the bug the previous
  entry recorded.

`PASS` stays strict, and by decision rather than omission: a pass says a specific
thing was checked and was correct, so there is always something to name. Only a
failure can be about nothing. R-010 shows both halves — its passes name the
shared element, its failures name only the model.

Three things had to learn the new shape, and each is a place the old one was
assumed rather than stated:

- **Grouping.** `ElementGroupingPolicy` refused to group an issue with no
  element. It now groups by *subject*: the element when there is one, the model
  otherwise. Element keys always begin with their model key and a separator, so
  the two can never collide. Without this, three real failures would have
  reached no issue at all, and a failure nobody is told about is the worst
  outcome available.
- **Geometry.** Nothing to tessellate, no viewpoint to frame; the pipeline
  filters element-less issues out rather than teaching that stage about blanks.
- **The rule library.** It served one checker. `compile_document` now compiles
  only IDS rules into the IDS document — writing a completeness rule into one
  would be a sentence in a language that cannot hold it — while the rule set
  still covers every rule. A rule naming a checker the library does not know is
  rejected when it loads, because a rule that cannot be routed would otherwise
  be silently skipped.

### The N/A normalization is fixed, and conformance rises to 98.08%

The previous entry recorded a divergence of ours and deferred it, on the grounds
that the fix was a modelling decision rather than a status mapping. The decision
is above, so: `_specification_status` now consults the specification's
cardinality. Applicability that is *required* and matched nothing is a failure,
not an N/A.

**256 of 261** buildingSMART cases now agree with the standard, and all five
remaining divergences are IfcTester's.

Nothing this repository publishes moves because of it — `compile_document` emits
`minOccurs=0` for every specification, so this project's own applicability is
always optional, and a test says so. It matters for the rule set somebody forking
this project brings with them.

The conformance file's third claim has now been asserted three times and meant
something different each time. First: our normalization changes no verdict —
true, but only because the corpus was four facet kinds wide and no case reached
the rule. Then: it changes one, and that one is wrong. Now: it changes none
again, resting on something entirely different. What the corpus still cannot say
is whether the rule is *right*, only that it is not wrong here; the case it
exists for — optional applicability matching nothing, which IfcTester calls a
pass — is not in the corpus at all.

### Unchanged

The eight published CSVs and the BCF archive are byte-identical, and
`run_id ids-v0.1-8706ef58303bfd11` still resolves. A second checker, a fourth
finding shape, and a change to how issues are grouped, and not one of the
forty-seven published finding keys moved.

Snapshot: `docs/contracts/contract-1.3.json`.

### Data contract 1.2 — the rule library gains four rules and three facet kinds

The library was built in the previous entry. This is the first time it was
*used*, and the measure of whether it worked is what had to be edited to add a
rule.

**Four new rules are four new TOML files.** No rule-handling code was written:
nothing parses them specially, nothing routes them specially, no test knows
their identifiers. Two other things did have to change, and neither is rule
plumbing:

- one line in `IdsChecker.capabilities`, because the checker had been
  under-claiming what it can evaluate — see below, it is a finding in its own
  right;
- the characterization counts, in six test files. Those are supposed to move
  when what the pipeline publishes moves. Moving them deliberately, with the
  contract bumped and this entry written first, is the ceremony working, not a
  hole in the claim.

| | before | after |
|---|---:|---:|
| rules | 7 | 11 |
| IDS facet kinds evaluated | 3 | 6 of 6 |
| value restrictions used | none | enumeration, pattern |
| findings, PCERT project | 47 | 76 |
| findings, ISO reference-view project | 27 | 39 |
| ISO reference-view: applicable, not N/A | 2 | 5 |
| issues | 3 | 18 |

The four:

- **R-006** — walls must declare a material. The first `material` facet. It
  passes in both projects, which is the point: the second project could
  previously only demonstrate that the pipeline ran over it, because every rule
  that had anything to say was about ducts, beams, or property sets its three
  samples do not contain.
- **R-007** — columns must declare a predefined type of `COLUMN` or `PILASTER`.
  The first `entity` facet in requirement position, and the first value
  restriction: an enumeration, because `IfcColumnTypeEnum` also admits
  `NOTDEFINED` and `USERDEFINED` and both are ways of not answering.
- **R-008** — beams must likewise declare theirs. Six PCERT beams fail it. They
  are named `girder` and carry no predefined type, so nothing downstream can
  tell a girder from a lintel; the name string is for a human reading a model
  tree, not for a schedule.
- **R-009** — walls must carry an element-level classification reference. The
  first `classification` facet and the first `pattern` restriction. Declared
  `WARNING`, for the same reason R-005 is: both sample projects do classify,
  but on `IfcBuilding`, and element-level classification is what an asset
  register or a CAFM handover consumes. An EPC project asks for it;
  buildingSMART never promised it, so failing this is not a defect in the
  supplied model. The rule file says so.

### The capability tuple was an inventory, not a claim

`IdsChecker.capabilities.facets` listed three facet kinds. That was never a
statement about the checker — IfcTester has implemented all six all along — it
was a list of what the rule library happened to use. The distinction is not
cosmetic: the registry refuses to route a requirement whose facet a checker does
not claim, so writing R-006 failed with *"needs facet(s) `['material']`, which
checker `'ids'` does not evaluate"*. An under-claimed capability does not
mislead a reader; it blocks a rule that would have worked.

It now lists all six, and the claim is evidenced rather than asserted: the
vendored buildingSMART corpus was widened from four facet directories to six —
one per facet kind — and all 261 cases run on every test run.

### What widening the corpus found

**255 of 261 conform: 97.70%**, and the sixth divergence is ours.

`IdsChecker._specification_status` maps zero applicable elements to `N/A`
unconditionally. That is right for a specification whose applicability is
optional, and it is the rule that keeps this project from reporting "nothing to
check" as compliance. It is wrong for a specification whose applicability is
*required*: `entity/fail-in_ifc2x3_there_must_be_an_airterminal…` says an
IfcAirTerminal must exist, the model has none, IfcTester fails it, and we report
`N/A`. A rule about something that should be there and is not is silently
downgraded to "does not apply".

It is recorded and left standing rather than hot-fixed, because the fix is not a
status mapping. A `FAIL` carries an `element_key` — `domain.Finding` enforces it
— and there is no element to point at when the finding is that an element is
absent. That is the same modelling decision the cross-model completeness checker
needs, and it is made once, there, rather than twice.

No rule in this repository can reach it: `compile_document` emits `minOccurs=0`
for every specification, so their applicability is optional and `N/A` is the
correct reading of every one. A test asserts that, so the exemption stops
holding the moment it stops being true.

The first version of the conformance file asserted the opposite of all this —
that our normalization changed no verdict anywhere. It was true only because the
corpus was then four facet kinds wide and none of them reached the rule. The
claim survived exactly as long as the evidence was too narrow to test it.

### Unchanged

The eight published CSVs and the BCF archive are byte-identical, and
`run_id ids-v0.1-8706ef58303bfd11` still resolves. Four new rules, and not one
of the forty-seven published finding keys moved — which is what the rule set
scope introduced two entries ago exists to guarantee, now demonstrated rather
than measured on a synthetic eighth rule.

Snapshot: `docs/contracts/contract-1.2.json`.

### An IDS document read by something that did not write it

Both rule documents are now audited by
[`ids-tool`](https://github.com/buildingSMART/IDS-Audit-tool) 1.0.124, a
separate buildingSMART implementation in another language, on every CI run on
both platforms. Until now an IDS document here was only ever read by IfcTester,
which also wrote one of them — a closed loop that proves the two agree and
nothing more.

The conformance corpus had already shown what the loop misses. Three of its five
divergences are documents whose value literal contradicts its declared data type
— `42.0` where the type says IFCINTEGER — and IfcTester casts and reports a
pass. `ids-tool` rejects all three with error 305. The two gates are
complementary and neither substitutes for the other: one asks whether the
document is valid, the other whether the answer about a model is right.

Both of this project's documents pass clean. The tool is installed from NuGet at
a pinned version and invoked as an external process; no code is copied.

Locally the audit skips when `ids-tool` is absent, because not every contributor
has a .NET SDK. In CI it may not: `EPC_REQUIRE_IDS_AUDIT=1` turns the skip into
a failure, so an install that silently broke cannot leave the gate switched off
while the build stays green. A test also runs the tool against a document known
to be bad, so the gate is never merely assumed to work.

Nothing published moves. The data contract stays at 1.1.

### Conformance against buildingSMART's own IDS test cases

Every gate this project had was self-referential. Determinism tests assert that
two runs agree with each other; characterization tests assert that a run agrees
with what a run produced last time. Neither can tell you whether the
interpretation being frozen so carefully is the right one.

199 `.ids`/`.ifc` pairs are now vendored from buildingSMART's implementer test
cases — the `attribute`, `classification`, `partof` and `property` subsets — and
run on every test run. **194 of 199 agree with the outcome the standard
declares: 97.49%.**

The five that do not are listed by name in `tests/test_ids_conformance.py`, each
with the behaviour responsible. All five are IfcTester's, not this project's:
three are lenient casting of an IDS value literal against its declared data type
(`42.0` accepted where the standard says an IFCINTEGER value written with a
decimal point makes the specification invalid), one is `cardinality="optional"`
not covering an attribute that is present but null, and one is a crash reading
IFC2X3 `IfcExtendedMaterialProperties`. On every case in the corpus this
project's verdict is identical to the raw verdict IfcTester reported.

Two limits are recorded as tests rather than left to be assumed. No case in the
corpus has zero applicable elements, so the single normalization this project
applies to a specification outcome — reporting "nothing to check" as N/A instead
of as a pass — is never exercised, and the 97.49% says nothing about it. And a
part of the corpus was generated from IfcTester's own expectations, so agreement
on those cases is weaker evidence than agreement on the rest.

The corpus is CC BY-ND 4.0 and is vendored verbatim under
`third_party/buildingsmart/ids/1.0/`, with per-file digests in `SHA256SUMS`
checked on every run and `.gitattributes` disabling text normalization for the
directory. Every file was verified against its upstream Git blob hash at the
pinned revision before being committed.

These are conformance fixtures, not project fixtures. They live under
`third_party/` so that project discovery, which globs `projects/*/project.toml`,
cannot reach them; a test asserts it.

Nothing published moves. The data contract stays at 1.1.

### Data contract 1.1 — rules become data

A rule used to be a function call. `generate_ids.py` declared its seven
specifications as module-level calls and then asserted that the document it had
just written contained a literal list of seven identifiers, so adding a rule
meant editing Python in two places. A rule's severity was a prefix match on its
identifier. And the metadata a delivery requirement actually carries — who owns
it, at which stage it applies, which disciplines it binds, what it cites — had
nowhere to live at all.

Rules are now TOML files under `rules/epc-delivery/`, one per rule, each
carrying its own metadata. Two things are derived from them: the `RuleSet` the
registry routes on, and the IDS document IfcTester executes. The document is a
build product — regenerated by every run, covered by the same
`git diff --exit-code` gate as the CSVs — not a source.

**Adding a rule now touches no package file and no test.** It is one new TOML
file.

The requirement identifier is computed rather than declared: IfcTester labels a
requirement by its facet, and every published `requirement_key` is a UUIDv5
over that label, so letting an author type it by hand would let a typo silently
re-key a published requirement.

Canonical outputs move because the rule set has a new id and version, so
`validation_run_id` becomes `epc-delivery-v1.0-…`. The eight published CSVs and
the BCF archive are unaffected — they are scoped to the frozen rule set, which
is what the previous entry was for.

Snapshot: `docs/contracts/contract-1.1.json`.

### Removed

- The severity prefix hack. `if identifier.startswith("R-005")` is gone;
  R-005A and R-005B declare `severity = "WARNING"` because that is a property
  of those rules — they state a requirement this project assumes rather than a
  defect in a supplied model — and the rule file says so in words.

### Scope of the legacy projection, part two — the rule set

The published files were already scoped to one project. They are now also
scoped to one **rule set version**, and the reason was measured before the
decision was made.

Adding a single rule to the current document, changing nothing else:

| | without the scope | with it |
|---|---|---|
| published `finding_key`s still valid | **0 of 47** | 47 of 47 |
| published artifacts rewritten | **7 of 9** | 0 of 9 |
| `run_id` | `ids-v0.1-d039d40a90203cf4` | `ids-v0.1-8706ef58303bfd11` |

Not *some* keys — all of them. The published `run_id` is a digest of the rule
document's bytes, so any rule anywhere re-keys every finding everywhere.

What makes that fatal rather than untidy is what it takes down with it:
`docs/evidence/stage_3b/acceptance_manifest.json` pins those digests, and
regenerating it means re-capturing five screenshots by hand in Power BI
Desktop with Speckle credentials — a task explicitly deferred to Phase 5. So
growing the rule library would have been blocked on a Phase 5 prerequisite.

The published files therefore mean *what rule set 0.1 said about the PCERT
project*. New rules go into a new version of the document and reach the
canonical outputs only. Configured as `legacy_ruleset_path`, alongside
`legacy_project_id`; both retire with the adapters.

Two details worth recording. The scope **filters rather than re-evaluates** —
the requirements it keeps were evaluated by the same run against the same
models, so a rule whose *meaning* changed would still break byte equality
loudly, which is the behaviour worth having. And published rows now take their
metadata, including severity, from the frozen rule rather than the current one,
so reclassifying a rule later cannot rewrite what an earlier version published.

Alternatives considered and rejected: running the pipeline twice, once per rule
set, splits the artifact manifest so it no longer describes *the* run; carrying
several rule sets in one bundle is probably where this ends up eventually, but
it restructures the domain, identity and validation layers, and Phase 3's
subject is the rule library, not the identity model.

### Data contract 1.0

**The canonical contract moved; the published legacy contract did not.**

A second project joined the repository, so the canonical tables now describe
two. The validation covers six models instead of three, which changes
`validation_run_id`, and through it every canonical finding, issue and event
key. `data/processed/canonical/` and `reports/artifact_manifest.json` all move.
Snapshot: `docs/contracts/contract-1.0.json`.

The eight files under `data/processed/` and the BCF archive under `reports/`
are byte-identical to contract 0.1, including the published `run_id`
`ids-v0.1-8706ef58303bfd11`, `ids_findings.csv` at `ea7d2fa2cd1690eb…` and
`ids_failures.bcf` at `b3c6f51abc9647ef…`.

#### Scope of the legacy projection — an explicit decision

Those eight files describe **exactly one project**, and with two projects
present something had to say which. The answer is a run-configuration setting,
`legacy_project_id`, and it is deliberate rather than incidental:

- **Emitting every project was measured, not assumed.** It changes all eight
  CSV files, the BCF archive and the published `run_id` — and every exporter
  still reports success. A contract that widens silently is worse than one that
  refuses.
- **The published contract is single-project by construction.** The tracked
  Power BI project asserts three models and thirty-nine elements, and the
  committed acceptance evidence was captured against those numbers. Making the
  legacy files describe more than one project is Phase 5 work, not a side
  effect of adding a fixture.
- **It fails closed.** With one project the setting may be omitted. With
  several and no setting, the legacy writers refuse and name the projects they
  found, rather than guessing.
- The narrowed projection keeps the run's own identity intact: the validation
  genuinely covered every model, and rewriting that to match the projection
  would publish an identity that never happened.

This setting retires with the legacy adapters in Phase 5.

### Added

- A second project, `iso-reference-view`: three unmodified IFC4 samples from
  the buildingSMART ISO Spec Reference View 1.2 set, pinned at commit
  `cecf656`. Its models are deliberately called `architecture` and `structural`
  — the same business codes the PCERT project uses — so that the
  `model_key`/`model_id` split is exercised rather than merely described. Their
  global keys become `iso-reference-view.architecture` and
  `iso-reference-view.structural`, which cannot collide with PCERT's pinned
  `architecture` and `structural`.
- `control-tower.toml`, which had not been needed until a run had a choice to
  make.

### Data contract 0.1

Unchanged. The rearrangement into `epc_control_tower/` is a move of code, not
of bytes: all eight published CSV files, the BCF 3.0 archive and its run
manifest are reproduced byte for byte from the canonical domain model, and a
characterization test asserts it.

### Changed

- The pipeline runs as one program (`epc-ct run`) instead of five scripts
  invoked in a documented order, two of which did their work at import time.
- Run identity is split three ways. `validation_run_id` covers only what can
  change the findings and now folds in each checker's version and
  configuration, so it differs from the single pre-split `run_id`.
  `execution_id` carries the wall clock and is unreachable from anything a run
  publishes. `artifact_bundle_id` identifies a set of outputs.
- A rule set's identity is derived from its parsed requirements rather than
  from its source file's bytes, so reformatting a rule document no longer
  re-keys every finding. The file's hash is still recorded, as provenance.
- The IDS reports under `reports/ids/` are reproducible for the first time.
  They previously embedded `datetime.now()` and listed elements in Python set
  iteration order; both are now pinned to the run's logical `as_of` and to a
  stable ordering. This changed their bytes once.

### Added

- Canonical exports under `data/processed/canonical/`, whose columns are
  derived from the domain types rather than restated as string lists.
- `reports/artifact_manifest.json`, recording the identity of a run's output
  set together with every artifact's digest.
- Issues carry a typed, versioned event history, and their lifecycle state is
  folded out of it rather than asserted alongside it.

### Removed

- The cardinality assertions taken from the shipped fixture — exactly six
  failures, exactly three topics of two findings each. They would have failed
  the pipeline rather than the data the first time a model was added or a duct
  segment fixed. The counts live in characterization tests instead.
