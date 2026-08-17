# AGENTS.md

Guidance for humans and coding agents working in this repository.

This project is meant to be forked and adapted. Most decisions are yours. The
rules below are the few that will silently break it if ignored.

## Hard rules

1. **Determinism.** Outputs must be byte-identical across runs, machines, and
   operating systems. Never read the clock, iterate an unordered collection,
   compress a ZIP archive, or emit platform-dependent line endings. Generated
   CSVs stay `utf-8-sig` with `lineterminator="\n"`. If you need a timestamp,
   take it from configuration, not from `datetime.now()`.

2. **Published artifacts move deliberately.** Everything under
   `data/processed/` and `reports/` is generated: `epc-ct run` rewrites it, and
   CI fails if a run changes anything. Do not hand-edit those files.

   If a change genuinely moves the contract, say so in `CHANGELOG.md` and then
   refresh its record with
   `epc-ct snapshot --refresh --contract-changed`. The refresh refuses until
   the CHANGELOG describes the version, so the account of what moved exists
   before the expectation that says it did.

   The three test layers are different promises, and the difference matters:

   | Layer | Asserts | Updated |
   |---|---|---|
   | `test_determinism.py` | two runs give identical bytes | **never** |
   | `test_run_invariants.py` | laws of the domain | rarely, when the domain changes |
   | `test_contract_snapshot.py`, `test_legacy_pbip_contract.py` | exact bytes and counts | by the ceremony above |

   A red determinism test is never fixed by changing the test. It means
   something read a clock, iterated an unordered collection, or depended on the
   machine.

3. **Third-party intake.** Follow the Review Gate in
   `docs/open_source_adoption.md`. In short: GPL/AGPL code never enters the
   source tree; CC BY-ND assets are vendored byte-for-byte and never
   reformatted; every addition pins a version, records a SHA-256, and updates
   both `docs/open_source_adoption.md` and `THIRD_PARTY_NOTICES.md`.

4. **Attribution.** The buildingSMART CC BY 4.0 attribution blocks must survive
   every refactor.

5. **Claims.** This is a personal open-source project. Never state or imply in
   code, documentation, or commit messages that it has been deployed,
   commissioned, or adopted by any company or client. Describing the problem as
   coming from real EPC delivery experience is fine.

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
  policy, the logical `as_of` — go in an optional `control-tower.toml` at the
  repository root. There are a handful, and keeping it that small is the point:
  a settings file that accepts everything explains nothing.

Two exporters are named `Legacy…` because they still know things a general
implementation should not: `LegacyBcfExporter` knows the R-005 rule family and
the HVAC model, and `LegacyPbipAdapter` reproduces frozen identity derivations.
Both are pure projections of the canonical model, both are pinned by
byte-equality tests, and both retire on schedule. Do not extend them; add
alongside.

### Running it

```bash
epc-ct run          # every stage, then every enabled exporter
epc-ct check        # validate without writing anything
epc-ct components   # what is registered
epc-ct snapshot     # does the published contract still match its record?
```

Without installing the package, `python -m epc_control_tower.cli …` does the
same. The scripts under `src/` are shims kept for the published entry points
and retire with the legacy adapters; new work goes in the package.

## Conventions

- Branch from `main`: `feat/`, `fix/`, `docs/`, `chore/`.
- Conventional Commits (`feat:`, `fix:`, `docs:`, `ci:`).
- Data contract changes are documented in `docs/data_contract.md` or
  `docs/bcf_data_contract.md`.

Everything else — structure, naming, style, how you split commits — is your call.
