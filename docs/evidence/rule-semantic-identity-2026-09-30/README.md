# Evidence — rule semantic identity and evidence carry-over (2026-09-30)

Supporting evidence for
[ADR 0005](../../decisions/0005-rule-semantic-identity-and-evidence-carry-over.md).
Everything below is reproducible from files tracked at `4e05c03` (`main`); no
private model is read or named.

## What this is, and what it is not

- **Measurement, not implementation.** `patches.py` edits a *disposable
  checkout* by exact string replacement, with the number of occurrences
  asserted. Its `EDITS` are rule edits whose effect is measured; nobody proposes
  making them. Its `OPTIONS` (`O1`, `O1-instructions`, `O3`) are throwaway
  prototypes of the fixes ADR 0005 compares, so each can be run instead of
  argued. None of them is the implementation, and none is committed as code
  outside this directory.
- **The chain is the real one.** `probe.py recheck` builds the run with
  `build_bundle`, narrows it with `facts_from_bundle`, composes the shipped Pack
  against `tests/assessment_fixtures.py`'s Overlay (the same fixture every
  recheck test uses: two of three policy tables decided, determinations supplied
  by the test), seals a record with `assess_purpose`, edits one rule file,
  re-validates in the same process with a fresh configuration and registry, and
  succeeds **every** sealed subscope with `recheck_purpose`. No function is
  stubbed and no check is skipped.
- **Determinations and policy are nobody's.** They are the test fixture's, as
  in every recheck test; nothing here says a coordination review was held.
- The checkout is restored with `git checkout -- . && git clean -fdq` after
  every scenario and the transcript ends with `dirty/untracked: 0`.

## Reproduce

```bash
git worktree add --detach <throwaway> 4e05c03
CT=<throwaway> PY=<repo>/.venv/Scripts/python.exe PROBE_SCRATCH=<dir outside it> \
  bash docs/evidence/rule-semantic-identity-2026-09-30/run_all.sh
git worktree remove --force <throwaway>
```

About ten minutes on the machine below; four of those are the four full test
suites (`S0`, `O1`, `O2`, `O3`), run with `EPC_REQUIRE_IDS_AUDIT=1`.

## Scenario index

| Id | Question | Transcript section |
|---|---|---|
| S0 | Does a plain run reproduce the published bytes, and is the suite green? | `### S0` |
| D | Which edits move the normalized digest today? | `### D` |
| RB | What an edit does to each finding: key, status, text | `### RB` |
| RP | The real assess → recheck chain across a rule-only edit | `### RP` |
| SQ | What a published `run` does with an edit today | `### SQ` |
| O1 | Facet parameters folded into the normalized digest | `### O1` |
| O1i | The same, with `instructions` counted as semantics | `### O1i` |
| O2 | Version discipline alone: bump 2.2 → 2.3 | `### O2` |
| O1+2.3 | O1 and a bump together | `### O1+2.3` |
| O3 | A content digest beside each cited `finding_key` | `### O3` |

## O1 的第一版（被拒绝的原型）

The first O1 prototype put the facet semantics on the *rule set* — an extra
`rule_semantics` argument to `build_ruleset_normalized_digest`, passed only by
`compile_document`. Every `build_bundle` under it failed:

```text
epc_control_tower.validation.BundleInvariantError: 1 bundle invariant violation(s):
  - ruleset normalized_digest '0ea274c880c38c43e678692ba286047caec36f770e26f9ca80d9a78a4ce52561' does not recompute from its own requirements (expected 'c3be0db4aab74fc87bba53c8e4cf4842ff67a7cfef30fbfaf7aa86ba9d97e729')
```

`validate_bundle` recomputes the digest from the bundle's own `Requirement`
objects, so anything the digest covers has to be on the requirement. The
committed `O1` in `patches.py` is the second version, which puts a
`semantics_digest` on each `Requirement`; that is the one the transcript
measures. The failing pass is not committed: it was also run concurrently with
a second pass against the same checkout, so its output was discarded, the
checkout was reset, and the transcript below is one clean pass from start to
`### END`.

## 补充测量

Two details the ADR quotes that the transcript only counts. Both were measured
on the same base with the same `patches.py`, and the checkout was restored
afterwards.

**Which ten findings change text but not status under `r005a-optional`.** Every
one is an `N/A` row: R-005A's two requirements on the five models that have no
duct segment, with `expected` going from "shall be provided" to "may be
provided":

```text
architecture N/A 'AssetTag data shall be provided in the dataset EPC_Delivery' -> 'AssetTag data may be provided in the dataset EPC_Delivery'
architecture N/A 'SystemCode data shall be provided in the dataset EPC_Delivery' -> 'SystemCode data may be provided in the dataset EPC_Delivery'
iso-reference-view.architecture N/A (the same two)
iso-reference-view.plumbing N/A (the same two)
iso-reference-view.structural N/A (the same two)
structural N/A (the same two)
```

**What the eight legacy files carry after `r002-datatype` + `run`.**
`data/processed/ids_findings.csv` changes 8 rows: the four architecture and four
structural walls of `pcert-sample`, each keeping its legacy `finding_key` under
`run_id` `ids-v0.1-8706ef58303bfd11` while its status moves PASS → FAIL.
`reports/bcf/run_manifest.json` records the frozen archive growing from 3 topics
(6 topic findings) to 11 (14). The legacy projection selects findings by
`requirement_key`, and R-002's key is the same in rule set 0.1 and 2.2, so the
current rule's results appear under the frozen name.

## Transcript

The complete output of one `run_all.sh` execution on 2026-09-30 (Windows 11,
the project's `.venv`, Python 3.14.7, ifcopenshell/IfcTester as pinned in
`requirements.txt`, `ids-tool` 1.0.124 for the enforced audit). Trailing
whitespace has been stripped from each line; nothing else is edited.

```text
### HEAD 4e05c0345c77faad27379cf91e324051f5ada8bd
dirty/untracked: 0

### S0 pristine run
run exit=0
generated files changed: 0
881 passed, 3917 subtests passed in 78.48s (0:01:18)

### D normalized digest under each edit (status quo)
frozen legacy rule set v0.1 normalized_digest ecd1477878548dea29b4187761ecc42ef87df1a28fb1df1c4bb5ce1ec8df256b
base normalized_digest c3be0db4aab74fc87bba53c8e4cf4842ff67a7cfef30fbfaf7aa86ba9d97e729
base source_blob_sha256 ''
  r002-datatype        SAME   c3be0db4aab74fc8
  r001-cardinality     SAME   c3be0db4aab74fc8
  r006-entity          SAME   c3be0db4aab74fc8
  r010-pattern         SAME   c3be0db4aab74fc8
  r005a-optional       SAME   c3be0db4aab74fc8
  r005a-datatype       SAME   c3be0db4aab74fc8
  r005a-instructions   SAME   c3be0db4aab74fc8
  r005a-reformat       SAME   c3be0db4aab74fc8
  version-2.3          moves  bff9fa452256fa04

### RB findings before/after each facet edit (status quo)
edit: r002-datatype
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.2-71d28a7c8bddb4e7
normalized_digest  c3be0db4aab74fc8 -> c3be0db4aab74fc8
findings 121 -> 121; slots in both 121; finding_key identical 121/121
same slot, status changed: 9; status same, text changed: 0
  b3181352-37eb-5f4a-9b0f-a170207386fd same key architecture::0OfZwWc8j9QP5uX8xPTxDH     R-002/Pset_WallCommon.IsExternal         PASS -> FAIL
  d85cfeea-4359-5feb-b224-683b3774961c same key architecture::1AQAupaRP1txwK1AGiN61V     R-002/Pset_WallCommon.IsExternal         PASS -> FAIL
  4b8761b3-446c-50ca-9986-812b31c5c5d9 same key architecture::1uS5vfZPn9R8PlAaVd73on     R-002/Pset_WallCommon.IsExternal         PASS -> FAIL
  7447aee0-5f08-5971-a8d7-0250513d7f36 same key architecture::3wdauVJT5Fx9drrREiDqA$     R-002/Pset_WallCommon.IsExternal         PASS -> FAIL
  1fad5ce6-0dc1-5e24-aae2-e4e48c2842ea same key iso-reference-view.architecture::3ZYW59sxj8lei475l7EhLU R-002/Pset_WallCommon.IsExternal         PASS -> FAIL
  230dd21d-611c-522f-9ddf-88ac3ebc0bfc same key structural::0DyViLJJ175RvWQi1rE7a6       R-002/Pset_WallCommon.IsExternal         PASS -> FAIL
  ac264db3-3199-5db2-a2ca-078ecd1fbda4 same key structural::2gTJhghMT81QThk15l2VwR       R-002/Pset_WallCommon.IsExternal         PASS -> FAIL
  a5333ef7-0f01-5457-b852-385585b0df44 same key structural::3SGBcf7Lv0r80vKtUCgOpf       R-002/Pset_WallCommon.IsExternal         PASS -> FAIL
  b136f406-0130-5c83-b2a0-1cb618de6c88 same key structural::3oNJ9yHi5FJuFnK8yg68Yt       R-002/Pset_WallCommon.IsExternal         PASS -> FAIL

edit: r005a-optional
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.2-71d28a7c8bddb4e7
normalized_digest  c3be0db4aab74fc8 -> c3be0db4aab74fc8
findings 121 -> 121; slots in both 121; finding_key identical 121/121
same slot, status changed: 2; status same, text changed: 10
  d0bdd588-2a41-5ddd-ab44-d7e59f99ed35 same key hvac::38WbwIGD90nB_3T2BTU5Ed             R-005A/EPC_Delivery.AssetTag             FAIL -> PASS
  5454a69b-d62a-57a2-a9e7-a96a4c4a364a same key hvac::38WbwIGD90nB_3T2BTU5Ed             R-005A/EPC_Delivery.SystemCode           FAIL -> PASS

edit: r005a-datatype
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.2-71d28a7c8bddb4e7
normalized_digest  c3be0db4aab74fc8 -> c3be0db4aab74fc8
findings 121 -> 121; slots in both 121; finding_key identical 121/121
same slot, status changed: 0; status same, text changed: 0

### RP the real recheck chain (status quo)
edit: r005a-optional
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.2-71d28a7c8bddb4e7
ruleset            epc-delivery v2.2 -> epc-delivery v2.2
normalized_digest  c3be0db4aab74fc8 -> c3be0db4aab74fc8
producing/consuming content ids unchanged: True
prior record assessment_digest aef0bd066b87a71521c7908cbebe7bc19283781420e6f7435af7fff0d1cb53de
successor record assessment_digest 42aa00aa96ae09b4761bb5ffaf8bda1857266ed543ca21023ce3e4cbd9980994
context is_current: True

  builders-work-openings #1: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/penetration/duct-none -> carried

  builders-work-openings #2: prior UNKNOWN penetration-not-determined; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['UNKNOWN']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['UNKNOWN']

  builders-work-openings #3: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::3zR0BOEcLADRKln4HYporH'] present now ['READY']
    determination fixture-determination/opening/chimney-slab-cross-referenced -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  builders-work-openings #4: prior BLOCKED missing-corresponding-opening; correspondence complete; condition named-outcome-not-observed
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::2iPwJwpPDCSgMheXwk9cBT'] present now ['BLOCKED']
    determination fixture-determination/opening/chimney-roof-not-modelled -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  ceiling-and-bulkhead-geometry #1: prior UNKNOWN in-model-position-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  ceiling-and-bulkhead-geometry #2: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['READY']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['READY']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/alignment/confirmed -> carried
    finding 12dc1e52-b4a8-5fd8-b650-222c2cf3060b hvac::23uPJWDfXEcwHH3kdFgV9c R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried
    finding 4cd5d234-8820-5068-b957-c7c04f4f296b hvac::38WbwIGD90nB_3T2BTU5Ed R-004A/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried
    finding 9b1eafbf-e3df-5c5d-9096-83ffbd2e4805 hvac::34Y6EIt3nDCAS1k$kPGOKm R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried

  schedules-and-room-data-sheets #1: prior UNKNOWN asset-identity-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  schedules-and-room-data-sheets #2: prior BLOCKED missing-project-asset-identity; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['BLOCKED']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['BLOCKED']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    finding 31f9255b-fa9d-522b-8af2-e45bd33bb216 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.AssetTag: FAIL -> FAIL; carried
    finding 366d684e-8e45-53c7-8993-5299a27c6d39 hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.SystemCode: FAIL -> FAIL; carried
    finding 5454a69b-d62a-57a2-a9e7-a96a4c4a364a hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.SystemCode: FAIL -> PASS; carried   <-- carried, but the finding behind this key changed
    finding 90ea1aba-c7f0-5142-a123-f12e3c7c54f5 hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.AssetTag: FAIL -> FAIL; carried
    finding 9b6e100b-f05d-51cd-93cd-36f6b2597c70 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.SystemCode: FAIL -> FAIL; carried
    finding d0bdd588-2a41-5ddd-ab44-d7e59f99ed35 hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.AssetTag: FAIL -> PASS; carried   <-- carried, but the finding behind this key changed

finding carry-over rows: 9; recorded 'carried' although the finding behind the key changed: 2; recorded 'carried' with identical finding bytes although its rule's definition changed: 0

edit: r005a-datatype
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.2-71d28a7c8bddb4e7
ruleset            epc-delivery v2.2 -> epc-delivery v2.2
normalized_digest  c3be0db4aab74fc8 -> c3be0db4aab74fc8
producing/consuming content ids unchanged: True
prior record assessment_digest aef0bd066b87a71521c7908cbebe7bc19283781420e6f7435af7fff0d1cb53de
successor record assessment_digest 00711fa6156514cc8d876ba769a3338bb587242cb177341a504c51afcc33e846
context is_current: True

  builders-work-openings #1: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/penetration/duct-none -> carried

  builders-work-openings #2: prior UNKNOWN penetration-not-determined; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['UNKNOWN']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['UNKNOWN']

  builders-work-openings #3: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::3zR0BOEcLADRKln4HYporH'] present now ['READY']
    determination fixture-determination/opening/chimney-slab-cross-referenced -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  builders-work-openings #4: prior BLOCKED missing-corresponding-opening; correspondence complete; condition named-outcome-not-observed
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::2iPwJwpPDCSgMheXwk9cBT'] present now ['BLOCKED']
    determination fixture-determination/opening/chimney-roof-not-modelled -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  ceiling-and-bulkhead-geometry #1: prior UNKNOWN in-model-position-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  ceiling-and-bulkhead-geometry #2: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['READY']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['READY']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/alignment/confirmed -> carried
    finding 12dc1e52-b4a8-5fd8-b650-222c2cf3060b hvac::23uPJWDfXEcwHH3kdFgV9c R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried
    finding 4cd5d234-8820-5068-b957-c7c04f4f296b hvac::38WbwIGD90nB_3T2BTU5Ed R-004A/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried
    finding 9b1eafbf-e3df-5c5d-9096-83ffbd2e4805 hvac::34Y6EIt3nDCAS1k$kPGOKm R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried

  schedules-and-room-data-sheets #1: prior UNKNOWN asset-identity-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  schedules-and-room-data-sheets #2: prior BLOCKED missing-project-asset-identity; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['BLOCKED']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['BLOCKED']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['BLOCKED']
    finding 31f9255b-fa9d-522b-8af2-e45bd33bb216 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.AssetTag: FAIL -> FAIL; carried
    finding 366d684e-8e45-53c7-8993-5299a27c6d39 hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.SystemCode: FAIL -> FAIL; carried
    finding 5454a69b-d62a-57a2-a9e7-a96a4c4a364a hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.SystemCode: FAIL -> FAIL; carried   <-- carried; finding bytes identical, the rule that produced it changed
    finding 90ea1aba-c7f0-5142-a123-f12e3c7c54f5 hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.AssetTag: FAIL -> FAIL; carried
    finding 9b6e100b-f05d-51cd-93cd-36f6b2597c70 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.SystemCode: FAIL -> FAIL; carried
    finding d0bdd588-2a41-5ddd-ab44-d7e59f99ed35 hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.AssetTag: FAIL -> FAIL; carried   <-- carried; finding bytes identical, the rule that produced it changed

finding carry-over rows: 9; recorded 'carried' although the finding behind the key changed: 0; recorded 'carried' with identical finding bytes although its rule's definition changed: 2

### SQ what a published run does with an edit today
-- r002-datatype
run exit=0
snapshot exit=1
generated files changed: 25 (legacy frozen among them: 8)
  M data/processed/bcf_topic_events.csv
  M data/processed/bcf_topic_findings.csv
  M data/processed/bcf_topics.csv
  M data/processed/bcf_viewpoint_components.csv
  M data/processed/bcf_viewpoints.csv
  M data/processed/canonical/findings.csv
  M data/processed/canonical/issue_events.csv
  M data/processed/canonical/issue_findings.csv
  M data/processed/canonical/issues.csv
  M data/processed/canonical/run.json
  M data/processed/ids_findings.csv
  M reports/artifact_manifest.json
  M reports/bcf/ids_failures.bcf
  M reports/bcf/issues.bcf
  M reports/bcf/run_manifest.json
  M reports/ids/architecture.html
  M reports/ids/architecture.json
  M reports/ids/hvac.json
  M reports/ids/iso-reference-view.architecture.html
  M reports/ids/iso-reference-view.architecture.json
  M reports/ids/iso-reference-view.plumbing.json
  M reports/ids/iso-reference-view.structural.json
  M reports/ids/structural.html
  M reports/ids/structural.json
  M ids/epc-delivery_v2.2.ids
validation_run_id epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.2-71d28a7c8bddb4e7
artifact_bundle_id bundle-a1fd9360e12c71fa -> bundle-a1fd9360e12c71fa
legacy run_id ids-v0.1-8706ef58303bfd11 -> ids-v0.1-8706ef58303bfd11
canonical findings 121 -> 121; finding_key survives 121/121; content identical 112/121
issues 21 -> 21; issue_key survives 21/21
BCF topics survive 21/21; markup bytes changed 9
-- r005a-instructions
run exit=0
snapshot exit=0
generated files changed: 13 (legacy frozen among them: 0)
  M reports/ids/architecture.html
  M reports/ids/architecture.json
  M reports/ids/hvac.html
  M reports/ids/hvac.json
  M reports/ids/iso-reference-view.architecture.html
  M reports/ids/iso-reference-view.architecture.json
  M reports/ids/iso-reference-view.plumbing.html
  M reports/ids/iso-reference-view.plumbing.json
  M reports/ids/iso-reference-view.structural.html
  M reports/ids/iso-reference-view.structural.json
  M reports/ids/structural.html
  M reports/ids/structural.json
  M ids/epc-delivery_v2.2.ids
validation_run_id epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.2-71d28a7c8bddb4e7
artifact_bundle_id bundle-a1fd9360e12c71fa -> bundle-a1fd9360e12c71fa
legacy run_id ids-v0.1-8706ef58303bfd11 -> ids-v0.1-8706ef58303bfd11
canonical findings 121 -> 121; finding_key survives 121/121; content identical 121/121
issues 21 -> 21; issue_key survives 21/21
BCF topics survive 21/21; markup bytes changed 0

### O1 facet parameters folded into the normalized digest (prototype)
frozen legacy rule set v0.1 normalized_digest ecd1477878548dea29b4187761ecc42ef87df1a28fb1df1c4bb5ce1ec8df256b
base normalized_digest ab62d8638b712d3fc670392b07db540aa3f93b523d66d4c6a8ceeb82d25118a0
base source_blob_sha256 ''
  r002-datatype        moves  fa7a9f9414d4db5f
  r001-cardinality     moves  a533a34b9fb1523c
  r006-entity          moves  f04ab8f273f1ee03
  r010-pattern         moves  211981c449edd5e9
  r005a-optional       moves  bf6f6e5132669f55
  r005a-datatype       moves  fae27e4ed12d74b6
  r005a-instructions   SAME   ab62d8638b712d3f
  r005a-reformat       SAME   ab62d8638b712d3f
  version-2.3          moves  aeab896574364421
run exit=0
snapshot exit=1
generated files changed: 8 (legacy frozen among them: 0)
  M data/processed/canonical/findings.csv
  M data/processed/canonical/issue_events.csv
  M data/processed/canonical/issue_findings.csv
  M data/processed/canonical/issues.csv
  M data/processed/canonical/requirements.csv
  M data/processed/canonical/run.json
  M reports/artifact_manifest.json
  M reports/bcf/issues.bcf
validation_run_id epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.2-d4cc6703d427f69d
artifact_bundle_id bundle-a1fd9360e12c71fa -> bundle-8b27f2ea58ac413e
legacy run_id ids-v0.1-8706ef58303bfd11 -> ids-v0.1-8706ef58303bfd11
canonical findings 121 -> 121; finding_key survives 0/121; content identical 121/121
issues 21 -> 21; issue_key survives 0/21
BCF topics survive 21/21; markup bytes changed 21
validate_dashboard exit=0
validate_pbip exit=0
-- version guard against the recorded snapshots
ruleset epc-delivery v2.2 digest ab62d8638b712d3f; version-guard conflicts: 1
  contract-1.6.json already records epc-delivery v2.2 with a different rule set (14 requirements, digest c3be0db4aab7…; now 14 requirements, digest ab62d8638b71…)
-- composition
fixture Overlay composes: composition_digest 2b3d9af14f7b4bb8
-- the recheck chain under O1
edit: r005a-optional
validation_run_id  epc-delivery-v2.2-d4cc6703d427f69d -> epc-delivery-v2.2-8cf3ec716dc476b6
ruleset            epc-delivery v2.2 -> epc-delivery v2.2
normalized_digest  ab62d8638b712d3f -> bf6f6e5132669f55
producing/consuming content ids unchanged: True
prior record assessment_digest 4c5eae80b8087c16fd2e86b28ee80f084f6f653f635b28eaacbc23cb1b241357
successor record assessment_digest 2dca275580b3dbc6612dc603296e7d589bd40b8b7e85a813e4ccf6acbe4ff026
context is_current: True

  builders-work-openings #1: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/penetration/duct-none -> carried

  builders-work-openings #2: prior UNKNOWN penetration-not-determined; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['UNKNOWN']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['UNKNOWN']

  builders-work-openings #3: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::3zR0BOEcLADRKln4HYporH'] present now ['READY']
    determination fixture-determination/opening/chimney-slab-cross-referenced -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  builders-work-openings #4: prior BLOCKED missing-corresponding-opening; correspondence complete; condition named-outcome-not-observed
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::2iPwJwpPDCSgMheXwk9cBT'] present now ['BLOCKED']
    determination fixture-determination/opening/chimney-roof-not-modelled -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  ceiling-and-bulkhead-geometry #1: prior UNKNOWN in-model-position-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  ceiling-and-bulkhead-geometry #2: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['READY']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['READY']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/alignment/confirmed -> carried
    finding 42804dbb-f530-5fd3-b559-11f12598ba5f hvac::34Y6EIt3nDCAS1k$kPGOKm R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> (absent); finding-absent-from-the-cited-run
    finding 64f31840-b607-5b9f-a1a1-9a7da8f2fc9a hvac::38WbwIGD90nB_3T2BTU5Ed R-004A/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> (absent); finding-absent-from-the-cited-run
    finding c161f79b-47bc-5d83-8fce-a52fdf6f0f35 hvac::23uPJWDfXEcwHH3kdFgV9c R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> (absent); finding-absent-from-the-cited-run

  schedules-and-room-data-sheets #1: prior UNKNOWN asset-identity-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  schedules-and-room-data-sheets #2: prior BLOCKED missing-project-asset-identity; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['BLOCKED']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['BLOCKED']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    finding 370416cd-e5af-5245-b260-745990e15814 hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.AssetTag: FAIL -> (absent); finding-absent-from-the-cited-run
    finding 4ad4e685-b673-5e45-a304-7b414218e9c0 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.AssetTag: FAIL -> (absent); finding-absent-from-the-cited-run
    finding 500aef66-9e42-50e3-a8db-6d3787607d21 hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.SystemCode: FAIL -> (absent); finding-absent-from-the-cited-run
    finding dcd1dc72-f345-59ac-9fe4-1cd02d0bea78 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.SystemCode: FAIL -> (absent); finding-absent-from-the-cited-run
    finding ec859939-ecc4-506d-b884-1ae8b26d71d0 hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.SystemCode: FAIL -> (absent); finding-absent-from-the-cited-run
    finding efbb438a-eb71-5ca1-99c6-23cc3be27b2f hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.AssetTag: FAIL -> (absent); finding-absent-from-the-cited-run

finding carry-over rows: 9; recorded 'carried' although the finding behind the key changed: 0; recorded 'carried' with identical finding bytes although its rule's definition changed: 0

edit: r005a-datatype
validation_run_id  epc-delivery-v2.2-d4cc6703d427f69d -> epc-delivery-v2.2-2d3ea46673fc423a
ruleset            epc-delivery v2.2 -> epc-delivery v2.2
normalized_digest  ab62d8638b712d3f -> fae27e4ed12d74b6
producing/consuming content ids unchanged: True
prior record assessment_digest 4c5eae80b8087c16fd2e86b28ee80f084f6f653f635b28eaacbc23cb1b241357
successor record assessment_digest 5b409f3114c284133f634d6f71be1ec9dab44072fafcf9ace07839a5bc2b8665
context is_current: True

  builders-work-openings #1: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/penetration/duct-none -> carried

  builders-work-openings #2: prior UNKNOWN penetration-not-determined; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['UNKNOWN']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['UNKNOWN']

  builders-work-openings #3: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::3zR0BOEcLADRKln4HYporH'] present now ['READY']
    determination fixture-determination/opening/chimney-slab-cross-referenced -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  builders-work-openings #4: prior BLOCKED missing-corresponding-opening; correspondence complete; condition named-outcome-not-observed
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::2iPwJwpPDCSgMheXwk9cBT'] present now ['BLOCKED']
    determination fixture-determination/opening/chimney-roof-not-modelled -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  ceiling-and-bulkhead-geometry #1: prior UNKNOWN in-model-position-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  ceiling-and-bulkhead-geometry #2: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['READY']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['READY']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/alignment/confirmed -> carried
    finding 42804dbb-f530-5fd3-b559-11f12598ba5f hvac::34Y6EIt3nDCAS1k$kPGOKm R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> (absent); finding-absent-from-the-cited-run
    finding 64f31840-b607-5b9f-a1a1-9a7da8f2fc9a hvac::38WbwIGD90nB_3T2BTU5Ed R-004A/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> (absent); finding-absent-from-the-cited-run
    finding c161f79b-47bc-5d83-8fce-a52fdf6f0f35 hvac::23uPJWDfXEcwHH3kdFgV9c R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> (absent); finding-absent-from-the-cited-run

  schedules-and-room-data-sheets #1: prior UNKNOWN asset-identity-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  schedules-and-room-data-sheets #2: prior BLOCKED missing-project-asset-identity; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['BLOCKED']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['BLOCKED']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['BLOCKED']
    finding 370416cd-e5af-5245-b260-745990e15814 hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.AssetTag: FAIL -> (absent); finding-absent-from-the-cited-run
    finding 4ad4e685-b673-5e45-a304-7b414218e9c0 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.AssetTag: FAIL -> (absent); finding-absent-from-the-cited-run
    finding 500aef66-9e42-50e3-a8db-6d3787607d21 hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.SystemCode: FAIL -> (absent); finding-absent-from-the-cited-run
    finding dcd1dc72-f345-59ac-9fe4-1cd02d0bea78 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.SystemCode: FAIL -> (absent); finding-absent-from-the-cited-run
    finding ec859939-ecc4-506d-b884-1ae8b26d71d0 hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.SystemCode: FAIL -> (absent); finding-absent-from-the-cited-run
    finding efbb438a-eb71-5ca1-99c6-23cc3be27b2f hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.AssetTag: FAIL -> (absent); finding-absent-from-the-cited-run

finding carry-over rows: 9; recorded 'carried' although the finding behind the key changed: 0; recorded 'carried' with identical finding bytes although its rule's definition changed: 0
-- the version guard on the next edit, once O1's digest is recorded
wrote docs/contracts/contract-9.9-probe.json: v2.2 ab62d8638b712d3f
edit: r002-datatype
ruleset epc-delivery v2.2 digest fa7a9f9414d4db5f; version-guard conflicts: 2
  contract-1.6.json already records epc-delivery v2.2 with a different rule set (14 requirements, digest c3be0db4aab7…; now 14 requirements, digest fa7a9f9414d4…)
  contract-9.9-probe.json already records epc-delivery v2.2 with a different rule set (14 requirements, digest ab62d8638b71…; now 14 requirements, digest fa7a9f9414d4…)
edit: r005a-datatype
ruleset epc-delivery v2.2 digest fae27e4ed12d74b6; version-guard conflicts: 2
  contract-1.6.json already records epc-delivery v2.2 with a different rule set (14 requirements, digest c3be0db4aab7…; now 14 requirements, digest fae27e4ed12d…)
  contract-9.9-probe.json already records epc-delivery v2.2 with a different rule set (14 requirements, digest ab62d8638b71…; now 14 requirements, digest fae27e4ed12d…)
edit: r005a-instructions
ruleset epc-delivery v2.2 digest ab62d8638b712d3f; version-guard conflicts: 1
  contract-1.6.json already records epc-delivery v2.2 with a different rule set (14 requirements, digest c3be0db4aab7…; now 14 requirements, digest ab62d8638b71…)
edit: r005a-reformat
ruleset epc-delivery v2.2 digest ab62d8638b712d3f; version-guard conflicts: 1
  contract-1.6.json already records epc-delivery v2.2 with a different rule set (14 requirements, digest c3be0db4aab7…; now 14 requirements, digest ab62d8638b71…)
-- test suite under O1 (published tree regenerated)
10 failed, 878 passed, 3911 subtests passed in 78.23s (0:01:18)
      2 FAILED tests/test_contract_snapshot.py
      1 FAILED tests/test_purpose_authorisation.py
      7 SUBFAILED tests/test_contract_snapshot.py

### O1i O1 with instructions counted as semantics
frozen legacy rule set v0.1 normalized_digest ecd1477878548dea29b4187761ecc42ef87df1a28fb1df1c4bb5ce1ec8df256b
base normalized_digest 0cb4c67414556c1d0e55172682fce1b75124eb2f5ec8b695da2e9176f1dd4d26
base source_blob_sha256 ''
  r002-datatype        moves  0ae5d4ebe915e8bd
  r001-cardinality     moves  bd210ef9587d8f47
  r006-entity          moves  a48f3a1981162ac9
  r010-pattern         moves  8645727c1b3f127c
  r005a-optional       moves  ce25263f8c9183e0
  r005a-datatype       moves  8414252857286ee8
  r005a-instructions   moves  56da6df2ea1ffb20
  r005a-reformat       SAME   0cb4c67414556c1d
  version-2.3          moves  c2c9074ae7b66352

### O2 version discipline: bump 2.2 -> 2.3
run exit=0
snapshot exit=1
generated files changed: 8 (legacy frozen among them: 0)
  M data/processed/canonical/findings.csv
  M data/processed/canonical/issue_events.csv
  M data/processed/canonical/issue_findings.csv
  M data/processed/canonical/issues.csv
  M data/processed/canonical/run.json
  M reports/artifact_manifest.json
  M reports/bcf/issues.bcf
  + ids/epc-delivery_v2.3.ids
validation_run_id epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.3-94ae5d15d466e549
artifact_bundle_id bundle-a1fd9360e12c71fa -> bundle-ec0de02a7096f2ee
legacy run_id ids-v0.1-8706ef58303bfd11 -> ids-v0.1-8706ef58303bfd11
canonical findings 121 -> 121; finding_key survives 0/121; content identical 121/121
issues 21 -> 21; issue_key survives 0/21
BCF topics survive 21/21; markup bytes changed 21
ruleset epc-delivery v2.3 digest bff9fa452256fa04; version-guard conflicts: 0
fixture Overlay REFUSED: [binding-ruleset-mismatch] [binding-ruleset-mismatch] interdisciplinary-coordination-readiness::asset-identity evidence_binding names ruleset 'epc-delivery' version '2.2', which is not th
-- test suite with the bump (published tree regenerated)
25 failed, 644 passed, 218 errors, 3545 subtests passed in 81.11s (0:01:21)
     23 ERROR tests/test_doctor_adapter.py
      4 ERROR tests/test_doctor_preview.py
     81 ERROR tests/test_purpose_assessment.py
     29 ERROR tests/test_purpose_authorisation.py
     12 ERROR tests/test_purpose_composition.py
      3 ERROR tests/test_purpose_isolation.py
     66 ERROR tests/test_purpose_recheck.py
      3 FAILED tests/test_contract_snapshot.py
      2 FAILED tests/test_doctor_preview.py
      1 FAILED tests/test_ids_syntax_audit.py
      9 FAILED tests/test_purpose_composition.py
      4 FAILED tests/test_purpose_isolation.py
      6 SUBFAILED tests/test_contract_snapshot.py
-- the recheck chain when the edit carries the bump
edit: r005a-optional+version-2.3
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.3-94ae5d15d466e549
ruleset            epc-delivery v2.2 -> epc-delivery v2.3
normalized_digest  c3be0db4aab74fc8 -> bff9fa452256fa04
producing/consuming content ids unchanged: True
prior record assessment_digest aef0bd066b87a71521c7908cbebe7bc19283781420e6f7435af7fff0d1cb53de
composition after the edit REFUSED: [binding-ruleset-mismatch]

### O1+2.3 O1 and a version bump together
run exit=0
generated files changed: 9 (legacy frozen among them: 0)
  M data/processed/canonical/findings.csv
  M data/processed/canonical/issue_events.csv
  M data/processed/canonical/issue_findings.csv
  M data/processed/canonical/issues.csv
  M data/processed/canonical/requirements.csv
  M data/processed/canonical/run.json
  M reports/artifact_manifest.json
  M reports/bcf/issues.bcf
  + ids/epc-delivery_v2.3.ids
validation_run_id epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.3-4b307de9eab475e8
artifact_bundle_id bundle-a1fd9360e12c71fa -> bundle-d54b1c49896eb1d1
legacy run_id ids-v0.1-8706ef58303bfd11 -> ids-v0.1-8706ef58303bfd11
canonical findings 121 -> 121; finding_key survives 0/121; content identical 121/121
issues 21 -> 21; issue_key survives 0/21
BCF topics survive 21/21; markup bytes changed 21
ruleset epc-delivery v2.3 digest aeab896574364421; version-guard conflicts: 0
fixture Overlay REFUSED: [binding-ruleset-mismatch] [binding-ruleset-mismatch] interdisciplinary-coordination-readiness::asset-identity evidence_binding names ruleset 'epc-delivery' version '2.2', which is not th

### O3 a content digest beside each cited finding_key (prototype)
run exit=0
snapshot exit=0
generated files changed: 0 (legacy frozen among them: 0)
validation_run_id epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.2-71d28a7c8bddb4e7
artifact_bundle_id bundle-a1fd9360e12c71fa -> bundle-a1fd9360e12c71fa
legacy run_id ids-v0.1-8706ef58303bfd11 -> ids-v0.1-8706ef58303bfd11
canonical findings 121 -> 121; finding_key survives 121/121; content identical 121/121
issues 21 -> 21; issue_key survives 21/21
BCF topics survive 21/21; markup bytes changed 0
edit: r005a-optional
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.2-71d28a7c8bddb4e7
ruleset            epc-delivery v2.2 -> epc-delivery v2.2
normalized_digest  c3be0db4aab74fc8 -> c3be0db4aab74fc8
producing/consuming content ids unchanged: True
prior record assessment_digest d5af435ee80aea1be5bb2637d36185ade35f7354706e7ead03def0bf960311a3
successor record assessment_digest e4004289dd330080f49b91f7af994fdd7ce2ee1cc1c0043893b678ea2506b092
context is_current: True

  builders-work-openings #1: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/penetration/duct-none -> carried

  builders-work-openings #2: prior UNKNOWN penetration-not-determined; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['UNKNOWN']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['UNKNOWN']

  builders-work-openings #3: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::3zR0BOEcLADRKln4HYporH'] present now ['READY']
    determination fixture-determination/opening/chimney-slab-cross-referenced -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  builders-work-openings #4: prior BLOCKED missing-corresponding-opening; correspondence complete; condition named-outcome-not-observed
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::2iPwJwpPDCSgMheXwk9cBT'] present now ['BLOCKED']
    determination fixture-determination/opening/chimney-roof-not-modelled -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  ceiling-and-bulkhead-geometry #1: prior UNKNOWN in-model-position-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  ceiling-and-bulkhead-geometry #2: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['READY']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['READY']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/alignment/confirmed -> carried
    finding 12dc1e52-b4a8-5fd8-b650-222c2cf3060b hvac::23uPJWDfXEcwHH3kdFgV9c R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried
    finding 4cd5d234-8820-5068-b957-c7c04f4f296b hvac::38WbwIGD90nB_3T2BTU5Ed R-004A/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried
    finding 9b1eafbf-e3df-5c5d-9096-83ffbd2e4805 hvac::34Y6EIt3nDCAS1k$kPGOKm R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried

  schedules-and-room-data-sheets #1: prior UNKNOWN asset-identity-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  schedules-and-room-data-sheets #2: prior BLOCKED missing-project-asset-identity; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['BLOCKED']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['BLOCKED']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    finding 31f9255b-fa9d-522b-8af2-e45bd33bb216 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.AssetTag: FAIL -> FAIL; carried
    finding 366d684e-8e45-53c7-8993-5299a27c6d39 hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.SystemCode: FAIL -> FAIL; carried
    finding 5454a69b-d62a-57a2-a9e7-a96a4c4a364a hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.SystemCode: FAIL -> PASS; finding-content-changed-under-the-same-key
    finding 90ea1aba-c7f0-5142-a123-f12e3c7c54f5 hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.AssetTag: FAIL -> FAIL; carried
    finding 9b6e100b-f05d-51cd-93cd-36f6b2597c70 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.SystemCode: FAIL -> FAIL; carried
    finding d0bdd588-2a41-5ddd-ab44-d7e59f99ed35 hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.AssetTag: FAIL -> PASS; finding-content-changed-under-the-same-key

finding carry-over rows: 9; recorded 'carried' although the finding behind the key changed: 0; recorded 'carried' with identical finding bytes although its rule's definition changed: 0

edit: r005a-datatype
validation_run_id  epc-delivery-v2.2-71d28a7c8bddb4e7 -> epc-delivery-v2.2-71d28a7c8bddb4e7
ruleset            epc-delivery v2.2 -> epc-delivery v2.2
normalized_digest  c3be0db4aab74fc8 -> c3be0db4aab74fc8
producing/consuming content ids unchanged: True
prior record assessment_digest d5af435ee80aea1be5bb2637d36185ade35f7354706e7ead03def0bf960311a3
successor record assessment_digest 12fbfab8827d7492afb2770dab415e01a7b805468b5c1689d5e5846e9cb4f4eb
context is_current: True

  builders-work-openings #1: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/penetration/duct-none -> carried

  builders-work-openings #2: prior UNKNOWN penetration-not-determined; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['UNKNOWN']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['UNKNOWN']

  builders-work-openings #3: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::3zR0BOEcLADRKln4HYporH'] present now ['READY']
    determination fixture-determination/opening/chimney-slab-cross-referenced -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  builders-work-openings #4: prior BLOCKED missing-corresponding-opening; correspondence complete; condition named-outcome-not-observed
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv', 'architecture::2iPwJwpPDCSgMheXwk9cBT'] present now ['BLOCKED']
    determination fixture-determination/opening/chimney-roof-not-modelled -> carried
    determination fixture-determination/penetration/chimney-slab-and-roof -> carried

  ceiling-and-bulkhead-geometry #1: prior UNKNOWN in-model-position-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  ceiling-and-bulkhead-geometry #2: prior READY -; correspondence complete; condition no-recheck-condition
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['READY']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['READY']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['READY']
    determination fixture-determination/alignment/confirmed -> carried
    finding 12dc1e52-b4a8-5fd8-b650-222c2cf3060b hvac::23uPJWDfXEcwHH3kdFgV9c R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried
    finding 4cd5d234-8820-5068-b957-c7c04f4f296b hvac::38WbwIGD90nB_3T2BTU5Ed R-004A/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried
    finding 9b1eafbf-e3df-5c5d-9096-83ffbd2e4805 hvac::34Y6EIt3nDCAS1k$kPGOKm R-004B/IFCRELCONTAINEDINSPATIALSTRUCTURE: PASS -> PASS; carried

  schedules-and-room-data-sheets #1: prior UNKNOWN asset-identity-not-evaluated; correspondence complete; condition no-machine-checkable-part
    member ['hvac::3dkFAzOGrAIuOzY_RdrdVv'] present now ['UNKNOWN']

  schedules-and-room-data-sheets #2: prior BLOCKED missing-project-asset-identity; correspondence complete; condition no-machine-checkable-part
    member ['hvac::23uPJWDfXEcwHH3kdFgV9c'] present now ['BLOCKED']
    member ['hvac::34Y6EIt3nDCAS1k$kPGOKm'] present now ['BLOCKED']
    member ['hvac::38WbwIGD90nB_3T2BTU5Ed'] present now ['BLOCKED']
    finding 31f9255b-fa9d-522b-8af2-e45bd33bb216 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.AssetTag: FAIL -> FAIL; carried
    finding 366d684e-8e45-53c7-8993-5299a27c6d39 hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.SystemCode: FAIL -> FAIL; carried
    finding 5454a69b-d62a-57a2-a9e7-a96a4c4a364a hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.SystemCode: FAIL -> FAIL; carried   <-- carried; finding bytes identical, the rule that produced it changed
    finding 90ea1aba-c7f0-5142-a123-f12e3c7c54f5 hvac::34Y6EIt3nDCAS1k$kPGOKm R-005B/EPC_Delivery.AssetTag: FAIL -> FAIL; carried
    finding 9b6e100b-f05d-51cd-93cd-36f6b2597c70 hvac::23uPJWDfXEcwHH3kdFgV9c R-005B/EPC_Delivery.SystemCode: FAIL -> FAIL; carried
    finding d0bdd588-2a41-5ddd-ab44-d7e59f99ed35 hvac::38WbwIGD90nB_3T2BTU5Ed R-005A/EPC_Delivery.AssetTag: FAIL -> FAIL; carried   <-- carried; finding bytes identical, the rule that produced it changed

finding carry-over rows: 9; recorded 'carried' although the finding behind the key changed: 0; recorded 'carried' with identical finding bytes although its rule's definition changed: 2
-- test suite under O3
1 failed, 880 passed, 3918 subtests passed in 77.19s (0:01:17)
      1 FAILED tests/test_purpose_authorisation.py

### END
dirty/untracked: 0
```
