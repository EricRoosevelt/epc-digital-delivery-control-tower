# Phase 2: revision comparison

Implemented `internal/doctor_adapter/revision_compare.py` with the pure function
`compare_revisions(before, after)`. Each input is the library envelope containing
`revision`, frozen `report` and `followups`. The function also verifies matching
project and stable model slot, independently of the library's scope validation.
Manual follow-ups are never read to determine the comparison result.

## Identity and checking basis

Single-file revisions join only by legal, unique GlobalId and rule ID within the
stable slot. The upload model key, file hash/name, element/finding IDs, Name, Tag
and STEP ID do not establish cross-revision identity. `global_id_count` covers all
IfcRoot objects in the IFC, including types and relationships. For historical
reports without that count, a single frozen PASS for ID-001 can establish this
limited identity evidence; otherwise comparison remains conservative.

Both frozen rule snapshots need a predicate version or semantic digest. Changes
in expected values, scope/applicability, version, checker or severity prevent a
repair claim. Effective finding expected values are compared too. Display-only
title/citation edits do not change the predicate. IFC schema and class changes
are exposed separately. A class change cannot turn an old failure into a claimed
repair, even if the new class is outside the rule's applicability.

Invalid/duplicate identities remain separate observations from each revision.
Public three-file federations can be saved and reopened, but this phase does not
pair their elements across revisions. Changed bundle rosters yield
`scope_changed`; an unchanged multi-file scope yields `federated_report`. These
cases show only failed observations in the attention list. For the real public
demo, this is 42 observations across the two revisions, rather than flagging all
312 PASS/FAIL/N/A observations. Full evidence remains in each saved report.

## Result contract and display meaning

The result contains `before_revision`, `after_revision`, `summary`, `rows`,
`basis_change`, `scope_note` and `scope_note_zh`. The two scope notes explain the
comparison boundary without presenting unsupported pairing as disappearance.

| Change | Meaning | Suggested Chinese / English |
| --- | --- | --- |
| resolved | Same object, unchanged rule/class/schema, FAIL to PASS | 本规则复查通过 / Rule recheck passed |
| remaining | Same rule still FAIL | 仍需核对 / Still needs review |
| new | Current FAIL without earlier FAIL | 新增未通过 / New failed check |
| missing | Previously failing GlobalId absent from current model | 当前版本未找到 / Not found in current revision |
| not_applicable | Prior FAIL now N/A with unchanged rule/class | 当前不适用 / No longer applicable |
| not_comparable | Ambiguous identity, missing findings, changed rule/class/schema or unsupported scope | 无法比较 / Not comparable |

For INFO results use “提示已满足 / Prompt satisfied”, “仍有提示 / Information prompt
remains”, and “新增提示 / New information prompt”. Optional storey/name prompts are
not hard model defects. Missing, N/A and manual ready-for-recheck are not resolved.
A passed rule recheck does not establish overall model acceptance.

`summary` contains each of the six total counts plus `errors` and `information`,
each itself a dictionary of the same six counts. These are comparison-record
counts, not a total of current defects or paired objects. In particular,
unpairable observations are counted independently from each revision.

Each row carries:

- `key`, `global_id`, `rule_id`, `change`, `severity`, `title`;
- `reason_code`, English `reason`, Chinese `reason_zh`;
- `before_` / `after_` finding ID, element key, status, class, name, actual,
  expected, citation, predicate snapshot and finding count.

Absent-side values are null. Missing rows point to the earlier revision's
element; ordinary current rows point to the later one. Class/rule changes retain
both sides' facts. Unchanged non-failing checks are omitted from the attention
list, and the absence of findings never implies PASS.

## Validation performed

- **30 comparison tests passed**, using actual minimal IFC bytes and ReviewStore
  results. Cases include re-exported PV FAIL to PASS; retained failure; new
  failure; deletion; changed IFC class/schema; type-first USERDEFINED free-text
  semantics; duplicate/invalid GlobalIds; a GlobalId collision with a type;
  renamed objects/files/hashes; same Name/Tag/STEP ID with different GlobalIds;
  changed/missing/unversioned predicates; absent/duplicate findings; ignored
  manual ready-for-recheck; cross-slot rejection; public federation boundaries;
  deterministic output and input purity.
- Comparison plus project-library integration suite: **51 passed** before the
  final attention-filter and unversioned-history edge-case additions. Root PM
  owns the final combined verification run.
- Ruff on the two owned Python files passed after the final edits.
- Actual HTTP round trip on the local phase-2 server: uploaded two synthetic IFCs,
  saved them in one slot, recorded manual ready-for-recheck, fetched comparison,
  reopened revisions and read English/Chinese Markdown briefs. PV returned one
  resolved, remaining, new, missing and class-changed observation each. Current
  hard failures stayed at two after a manual ready-for-recheck record.
- Actual browser paths in Chinese and English: comparison missing row opened the
  correct old object/finding; remaining row opened the current failed object with
  its separate ready-for-recheck record. Language switching retained the revision
  and selected finding. The UI worker fixed a detached-form comparison deep-link
  restoration bug found during this check; reopening the English deep link then
  automatically displayed the correct direction and comparison results.

The synthetic models used for this evidence have no geometry representations;
the workspace correctly retains their check evidence and says no renderable
geometry is available. Real public demo meshes and restart persistence are
covered by the project-library integration tests. No canonical rules or published
artifacts were changed by the comparison implementation.
