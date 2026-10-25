# Workbench and pipeline rule parity

PV-001 now has one source definition and one predicate implementation: the existing `rules/product-validation/PV-001.toml`, compiled by `epc_control_tower.rule_definitions.compile_document`, executed by the installed IfcTester. The workbench adapter no longer declares a separate four-value enumeration or performs its own class/type applicability test. The three INFO/ID checks remain explicit workbench information/identity checks; they have no claimed legacy equivalent.

## Measure first, then share

The untouched paths were characterized before refactoring at baseline 996fc7d. [rule-parity-baseline.json](rule-parity-baseline.json) records 34 public synthetic cases and the original runtime rule snapshots. Each case uses the exact same IFC bytes for the workbench and a real legacy path: a copied rule library in an external temporary workspace, `load_ruleset`, real registry/check stage and IdsChecker, actual compiled IDS and reports. This is not a comparison of two calls to the newly shared function.

Thirty IFC4 cases executed through the full check stage. Applicable status differences were **zero**. Cases include all four accepted enumerations, NOTDEFINED/unset values, assigned-type precedence, missing/blank/whitespace type text, fallback from NOTDEFINED and missing type values, USERDEFINED ObjectType/ElementType, case/padding, malformed enumeration parsing, base/sibling classes, an IfcWallStandardCase subclass, and zero applicable elements. Unsupported schemas were also measured: three IFC2x3 cases and one IFC4x3 case. The registry explicitly rejects these schemas because IdsChecker declares IFC4 support only. Their separately recorded underlying IdsChecker output is characterization, not a claim of supported pipeline execution.

One actual predicate difference was found outside that shared supported scope: an IFC2x3 IfcFurnishingElement synthetically assigned an IfcAirTerminalType was included by IfcTester's type fallback, while the old workbench required an IfcFlowTerminal. The shared evaluator now follows IfcTester and reports PASS for that synthetic effective-DIFFUSER case. This fixture demonstrates dispatch behavior; it is not advice to export that class/type combination. The normal IFC2x3 IfcFlowTerminal mapping already agreed. [rule-parity-shared.json](rule-parity-shared.json) records the post-extraction run, the single original-runtime status change and zero common-schema status mismatches.

## Shared implementation and frozen evidence

`internal/doctor_adapter/review_rules.py` loads the existing product rule definitions and projects PV-001's title, severity, citation, expected text and provenance from them. It compiles a fresh in-memory IDS document per model and calls `document.validate(model)` once. The legacy checker independently serializes/reopens the same compiler's document and uses the same IfcTester evaluator. There is no new PV-specific branch in the generic checker, no new rule framework, and no generated IDS/report write in the workbench.

Workbench status is read from the compiled specification's applicable/passed entities, indexed by STEP entity ID. Independently reading the effective predefined type supplies UI evidence only; it does not decide PASS. Fresh document state prevents one model's result leaking into another. A synthetic copy of the source rule with REGISTER removed changes the real workbench result to FAIL, proving the displayed rule is not backed by a copied enum.

Only the runtime PV-001 `predicate_version` advances from 1 to 2. The declarative product-validation ruleset remains version 1.0 with unchanged content and digest. INFO-001, INFO-002 and ID-001 remain runtime version 1. Each new PV snapshot freezes its canonical requirement semantics digest, rule-library version/digest, source-definition digest, requirement key, checker/engine versions, declared IFC versions and the pipeline's supported schemas. The actual evaluated schema stays on each model entry. These extra schema evaluations do not expand the legacy registry's supported schemas.

Revision comparison includes predicate version/semantics as before and now also includes checker_version, engine and engine_version. A changed engine cannot masquerade as a source-model repair. Unrelated overall library digests are deliberately excluded from the per-rule comparison signature. Existing saved runtime v1 reports are not rewritten; their PV results compare with v2 as `not_comparable/rule_changed`. To evaluate a new real repair, rerun both model revisions under the final v2 service. A fresh v2 FAIL to v2 PASS remains comparable, while manual ready_for_recheck never changes machine status.

## Intentional projection differences

- Legacy `Finding.actual` remains empty because its normalized reporter contract provides no stable observed-value field. Workbench `actual` shows the independently read effective value (or its explicit missing-value placeholder). No canonical field is recaptured or changed.
- When no elements match, legacy emits one model-level `N/A` finding per requirement, with no element key. Workbench emits `NOT_APPLICABLE` on each displayed nonmatching element. A truly empty model has no invented element/finding in the workbench. These are different coverage projections, not positive passes.
- Legacy uses INFO severity on non-failing outcomes; the workbench preserves each rule's configured severity alongside its status. Failures still use the source rule severity. Counts and scopes must be interpreted in their respective envelope.
- Shared predicates inspect effective type text; they do not validate every IFC schema obligation or the object's engineering function. Malformed/unset enums can be parsed as absent and fall back to ObjectType, and USERDEFINED supported free text can pass. A predicate pass is not proof of schema validity or correct classification.

## Legacy STEP character compatibility

During real UI intake, UTF-8-only decoding blocked a native-readable legacy export. A public synthetic STEP containing a single-byte 0xB5 reproduces the failure. For non-UTF-8 bytes the adapter now delegates exact original bytes to IfcOpenShell's native file reader using an external short-lived temporary file, removed immediately after parsing. It does not guess a code page, replace characters, mutate the source or change the original SHA-256. ASCII/UTF-8-compatible input retains the in-memory path. The regression compares native-observed text, verifies original hashes and source bytes, and checks no temporary file remains. Native parsing is not a complete schema-validity assessment. No private model or identifier appears in fixtures or these reports.

## Verification

- Final affected rule/legacy/comparison/guidance/advice command: `pytest -p no:cacheprovider tests/test_doctor_rule_parity.py tests/test_product_validation_ruleset.py tests/test_doctor_revision_compare.py tests/test_doctor_guidance.py tests/test_doctor_advice.py -q --tb=short` → **154 passed, 64 subtests passed**. The original two comparison-fixture assumptions were corrected: changed-version input must differ from current v2, and an unversioned snapshot must remove all recognized predicate/semantics/version tokens.
- Workbench parity/review/project regression run after extraction → **75 passed**; this includes the source-character cleanup test and persistent report/advice semantics. The later engine-signature regression is included in the final 154-test run.
- The legacy product-rule suite actually executes isolated shipped pipeline copies and checks produced bytes against committed outputs, not merely against each other.
- All **20** contract-1.7 published artifact hashes were measured against the unchanged committed snapshot: **zero mismatches**, also recorded in the machine summary. `git diff --exit-code -- data/processed reports ids rules` passed. No snapshot refresh, rule-library version edit or canonical recapture was used.
- Unified gate: **1,476 passed, 11,871 subtests passed**, with
  `EPC_REQUIRE_IDS_AUDIT=1`; full Ruff and `pip check` passed. The shipped pipeline
  regenerated successfully, snapshot confirmed **20 unchanged artifacts**, and
  dashboard core/PBIP validation passed. No snapshot refresh was used. Private
  external-case UI/performance outcomes are recorded separately in
  [the model case](model-case.md).

To reproduce current public measurements without overwriting the historical baseline, set `PYTHONPATH` to the repository root and run `python tests/rule_parity_cases.py <new-summary.json>`. Test fixtures and all legacy compiler/report outputs are public synthetic data in removable external scratch workspaces.

## Saved-report real-case verifier

`tools/model_case/verify_legacy.py` prepares the same legacy rule-copy/loader/registry/check/IdsChecker path for an authorized real IFC, compared against an already saved workbench report. It never calls ReviewStore or tessellation. Wait until UI timing and memory sampling has ended before running the actual case.

Usage: `python tools/model_case/verify_legacy.py --ifc <external-source.ifc> --report <external-saved-report.json> --output-dir <new-external-evidence-dir> --expected-applicable 96`.

Inputs and raw outputs must be outside a checkout; output paths are resolved and every ancestor is checked for a Git checkout marker. The exact source SHA-256 must match the saved single-model report and the copied legacy input. The saved PV-001 semantics digest must match the loaded source rule. Unknown/duplicate identities and unexpected statuses do not silently disappear from comparison. All common PV-001 PASS/FAIL results are joined by GlobalId; the remaining displayed elements are verified as the intentional per-element NOT_APPLICABLE projection, including the legacy model-level N/A case when nothing applies.

Stdout contains only aggregate counts and booleans. Raw source copies, compiled IDS, real legacy HTML/JSON reports, detailed mismatches and failure diagnostics remain in the external evidence directory. An existing evidence workspace is not overwritten. Exit 0 means all comparisons and the optional expected count matched; 1 means a measured mismatch; 2 means verification could not complete.

Preparation verification used tiny public synthetic IFCs only: **6 passed**, including a guard that makes both workbench import and tessellation raise if called. It also covers zero-applicable projection, safe aggregate output, wrong source fingerprints, a real status mismatch and checkout-output rejection. No private real-model legacy computation was run during preparation.

## Completed real-model same-input legacy comparison

The authorized real source exports were compared after UI sampling ended, using their existing v2 workbench report snapshots. The verifier independently ran each exact IFC payload through the copied declarative rule library, actual registry/check stage and IdsChecker. It did not call the workbench import or regenerate geometry. Source SHA-256 and PV-001 semantics matched before comparison; raw files, model identities, reports and logs remain outside the checkout.

| Export | IFC elements | Common PV-001 observations | Legacy result | Workbench result | Status differences | Non-applicable projection |
| --- | ---: | ---: | --- | --- | ---: | --- |
| Before | 2055 | 96 | 96 FAIL | 96 FAIL | 0 | 1959 matched |
| After | 2055 | 96 | 94 FAIL, 2 PASS | 94 FAIL, 2 PASS | 0 | 1959 matched |

Both verifier runs exited 0. Across the two revisions, **192 applicable observations had zero status differences**. Each revision also had zero missing/extra applicable objects, zero missing/extra displayed elements, and an exact match for all **1959 per-element NOT_APPLICABLE projections**. These are two observations per corresponding object, not 192 distinct objects. The remaining 94 FAIL results are retained; two PV-001 passes do not establish overall model acceptance.

The before comparison used the earlier same-byte, same-v2 saved report; this check alone does not certify the later cold 3D attempt. The after comparison used the saved report from the completed uncached UI import. Legacy result parity is separate from browser rendering success and performance measurements, which are recorded by the main case investigation. No source names, identifiers, hashes or private screenshots are copied into this public handoff.
