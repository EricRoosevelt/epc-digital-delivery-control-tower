# First product increment: PM integration

2026-10-24, Singapore. Base: `2732b4b` (`origin/main` when work began).

## Delivered

The first stage is a working local model-review product path: load real IFC,
read measured review results, locate a finding in actual 3D geometry, and obtain
specific evidence-grounded next actions. The workbench is `/review.html?lang=en`
or `?lang=zh`; the existing homepage now recommends it and retains the earlier
example, local-check and recheck experiences.

Engineering, UI and BIM workers implemented their parts in one isolated worktree
and submitted [engineering](phase1-engineering.md), [UI](phase1-ui.md) and
[BIM](phase1-bim.md) handoffs. PM integrated the interfaces and OpenAI service,
reviewed the actual source and screenshots, and sent concrete corrections back.
The user selected OpenAI API for this phase.

Integration corrections included separating INFO prompts from errors in every
view; keeping the IFC adapter network-free by placing provider transport in
`doctor/advice.py`; making PASS advice preserve evidence without inventing repair
work; framing the building instead of distant source helpers while retaining
Show all; moving actions ahead of long identifiers/evidence; and selecting INFO
initially when a file has no error-level findings.

## Evidence

- Full Python suite with `EPC_REQUIRE_IDS_AUDIT=1`:
  **1363 passed, 11725 subtests passed in 155.43s**, no failures or skips.
- `ruff check .` and the authored-source whitespace check: passed. The vendored
  Three.js source retains its upstream indentation, including one whitespace
  warning in `three.core.js`; modifying it would break the pinned file digest.
- `epc_control_tower.cli run`: completed at the existing run/bundle identity.
  `snapshot`: **contract-1.7.json matches, 20 artifacts unchanged**.
  `git diff --exit-code -- data/processed reports`: empty; no untracked outputs.
- Dashboard core validator, PBIP static contract/evidence validator and
  `pip check`: passed. These are the existing validators, not new live Power BI
  interaction or production compliance claims.
- Real-browser `doctor_review.browser.cjs`: passed on the final UI, with no page
  errors. Exercises demo counts, linked list/mesh selection, focus/isolation,
  reset/full extents, filters/search, no geometry, failed-load recovery, real
  HVAC/Architecture imports, Chinese 390px layout, locale reload and reduced motion.
- Existing `doctor_ui.browser.cjs`: passed, including the 375/1280px local
  query/detail/language/back flow and example-item language continuity.
- Three.js tarball and all three unmodified runtime files match their pre-existing
  recorded SHA-256 values. License and attribution remain intact.

The first integration run exposed obsolete single-entry/static-order wording
assumptions and the misplaced network module; these were corrected without
weakening the network-free adapter guarantee or changing published snapshots.
One Windows temporary-file rename failed once, then passed in a focused rerun
and the final complete suite; no pipeline retry or unrelated code was added.

## Product boundaries and next stage

The public demo has 39 elements, 32 renderable shapes, 2 air-terminal findings
requiring review and 19 storey information prompts. It is a real data inspection
over public examples; the four checks do not assess clashes or project acceptance.

OpenAI request construction, trusted finding selection, structured output parsing,
minimal evidence and failures have automated transport tests. No API key was
configured, so no live paid provider call or engineering-quality evaluation of a
generated answer was performed. The UI labels local guidance honestly; setup is
in [the Doctor readme](../../doctor/README.md#openai-setup).

Review state is memory-only for this server session. Importing a fresh IFC reruns
the checks, but the new workspace does not yet store issue handling or compare
revisions. The next product increment should connect persistent project/revision
records and explicit recheck comparison, then evaluate actual generated advice
with representative engineer cases and a configured API account. These are
product needs exposed by this increment, not an additional approval chain.

The isolated worktree is retained for the user's preview and subsequent stages.
The original checkout's unrelated local edits were not changed.
