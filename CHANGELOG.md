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
