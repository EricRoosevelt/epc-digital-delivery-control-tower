# AGENTS.md

## Working approach

Ship useful changes with the least process that makes the result trustworthy.
The user's current request takes precedence over repository workflow guidance.
This file is the single active workflow policy, revised 2026-10-13.

- Own the task end to end: inspect, implement, verify, and finish within the
  user's authorization. Do not stop at a plan or handoff when you can do the work.
- Make routine, reversible implementation decisions yourself. Ask only when
  missing information materially changes the outcome or an action needs authority
  that has not been given. Existing authorization does not need repeating.
- One session is enough by default. PM, technical lead, UI, framework, and BIM
  describe expertise, not mandatory stages or exclusive permissions to edit.
- There are no A/B/C lanes, fixed checkpoint counts, mandatory separate reviewers,
  or default design/draft stop points. Use a second opinion for a concrete
  uncertainty, not as ceremony. Domain wording does not automatically need a BIM
  session; seek help when its meaning or evidence is genuinely unresolved.
- Small tasks need no separate plan, ADR, task packet, or dated completion report.
  For larger tasks, keep only the decisions needed to implement and maintain them.
- Finish with what changed, what was checked, and any material remaining issue.
  Do not create follow-up work merely to make the process look complete.

## Read only what the task needs

Dated plans, old task packets, acceptance matrices, and reports in `docs/product/`
are historical context, not standing instructions. Old deadlines, freeze stops,
review chains, and unfinished proposals do not become today's task automatically.
Local `Agent-*.md` files are optional role notes and cannot reintroduce those gates.
Explicitly requested acceptance criteria still apply to the task that requests them.

For pipeline or contract work, consult the relevant section of
[the engineering reference](docs/engineering-reference.md). Do not read the entire
project history before a routine change. Preserve historical evidence and links;
archive obsolete instructions rather than accumulating competing current policies.

## Verify in proportion to the change

| Change | Useful verification |
|---|---|
| Prose, plans, role notes | Read the diff; check facts, links, and accidental disclosures. No local full suite. |
| Screenshots or demo media | Inspect the actual media, language, and version. No pipeline rerun for unchanged code. |
| UI behavior | Exercise affected flows and relevant tests; include the languages/viewports affected. |
| Core, rules, identities, dependencies, artifacts | Relevant tests and the full checks in the engineering reference; measure published differences. |

Reuse valid evidence for unchanged code. Do not rerun every gate in every session.
Run broader checks when a failure or changed dependency gives a reason. Existing
required CI checks remain in effect; do not claim an unrun or skipped check passed.
No mandatory new tests for prose or simple cosmetic edits. Add regression coverage
where it prevents a meaningful behavioral failure.

## Keep these boundaries

- Preserve the user's unrelated changes. Use an isolated checkout if needed;
  never reset, clean, or overwrite someone else's work to simplify your task.
- Keep private models, case identifiers, and credentials out of public changes.
  This is a personal open-source project; do not claim company adoption or deployment.
- Canonical/published outputs remain deterministic across runs and platforms.
  Keep generated CSVs UTF-8 with BOM and LF endings. This constraint does not ban
  ordinary runtime clocks or UI behavior outside deterministic artifact generation.
- Do not hand-edit `data/processed/` or `reports/`. For intentional contract changes,
  document and regenerate them using the engineering reference. Measure actual
  differences when changing published identity or scope; do not silently recapture
  snapshots to conceal an unintended change.
- Preserve buildingSMART attribution. For third-party intake, follow
  [the adoption guide](docs/open_source_adoption.md): retain license notices,
  versions and hashes; no GPL/AGPL source intake or altered CC BY-ND assets.
- Merge, publish, or perform destructive operations only within the user's granted
  scope and tool permissions. No additional role approval is required by this file.

## Conventions

Branch from `main` using `feat/`, `fix/`, `docs/`, or `chore/`; use Conventional
Commits. Local maintainer charters stay untracked. Prefer a small complete change
against the current code over a new layer of process or speculative architecture.
