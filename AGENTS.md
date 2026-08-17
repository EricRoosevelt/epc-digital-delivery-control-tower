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

2. **Golden baselines move together.** Changing anything under
   `data/processed/` or `reports/` means updating the matching baselines in
   `tests/` and the SHA-256 values in `README.md` in the same commit. A green
   `pytest` run is the gate; a red suite is never "expected".

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

Prefer adding to a seam over editing pipeline internals:

- **Rules** — add a rule definition rather than editing the IDS generator.
- **Configuration** — model registration, severity policy, BCF metadata, and
  expected baselines are inputs, not logic.
- **Outputs** — add a writer; leave the existing data contracts intact.

Today several of these values are still frozen constants inside `src/`
(model whitelists, expected counts, severity prefixes, BCF identities). Moving
them into configuration is the current direction of travel. So: if a change
forces you to edit a frozen constant in `src/`, that constant probably belongs
in configuration — move it there and keep its default value identical.

## Conventions

- Branch from `main`: `feat/`, `fix/`, `docs/`, `chore/`.
- Conventional Commits (`feat:`, `fix:`, `docs:`, `ci:`).
- Data contract changes are documented in `docs/data_contract.md` or
  `docs/bcf_data_contract.md`.

Everything else — structure, naming, style, how you split commits — is your call.
