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
