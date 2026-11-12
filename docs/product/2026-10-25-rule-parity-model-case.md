# Shared check semantics and one representative correction case

## Requested outcome

Continue from `996fc7d` with two concrete deliverables before extending the rule
catalog: characterize and align the shared PV-001 rule across the framework and
3D workspace; verify the complete correction/recheck path on one representative
editable model, including measured import and interaction performance.

The user has authorized the existing programming, UI and BIM sub-sessions. Keep
the change small and preserve published outputs. This is an implementation record,
not an additional review or approval workflow.

## Rule consistency

First record same-input results from the original workspace predicate and the
actual rule-loader/IdsChecker path. Include assigned types, inheritance,
USERDEFINED free text, NOTDEFINED/fallback, not-applicable and schema boundaries.
Then remove duplicate PV-001 policy/evaluation from the workspace by reusing the
existing rule definition and evaluator. Do not add a PV-specific branch to the
generic checker or rewrite the pipeline.

Common supported inputs must agree on status. Preserve and test deliberate
projection differences: framework model-level N/A versus per-element workspace
not-applicable records, the framework's unavailable observed value versus the
workspace's directly read value, and an empty model without invented elements.
The framework's supported schema and a lower-level parser's capabilities are
different claims. Version any actual runtime predicate change without rewriting
earlier revision evidence or frozen rule contracts.

## Representative case and confidentiality

The user's existing private model area contains a source-authoring case with
original/working RVT files, clean before/after IFC exports, a recorded BIM-role
classification choice for the exercise, source-operation captures and
export/provenance records. This is not a named engineer's project sign-off. BIM has
verified the two relevant IFC hashes against those records. Both versions contain
2055 elements and 96 air terminals, with two type expressions changed and the
other 94 unchanged.

Use those same model versions throughout the current product replay. Historical
source editing and re-export evidence must be dated honestly, not presented as a
new source operation. If a safe current authoring replay is practical, use a new
working copy and the recorded exercise choice; never patch an IFC value and
call it a Revit re-export. Actual engineering classification and acceptance
remain decisions for a person with the necessary project context.

All model files, identifiers, source paths, screenshots, raw measurements and
case database stay outside the public checkout. Public scripts are generic;
public reports contain only anonymized aggregate results. No private model text
is sent to an AI provider. Public buildingSMART inputs remain unchanged.

## Complete-path evidence

Use a separate loopback server/data directory. Demonstrate import/check,
selection of actual geometry, the source-decision/export chain, same-model-slot
revision save, comparison, real process restart, restored selected evidence and
downloaded work brief. Explain why each reported change is justified. Any
controlled deletion or reclassification probes use additional working copies
and are explicitly distinct from the real correction pair.

Measure source bytes, element/applicable-check/mesh/triangle counts, upload plus
parse/check wall time, geometry response time, first actual mesh draw, selection,
orbit/zoom/isolation, server RSS baseline and sampled peak, and browser heap when
available. Record the hardware/browser/measurement method. State only the model
scale actually sustained, with observed limits; do not infer an enterprise limit
from a small fixture or an arbitrary upload cap.

Initial real intake exposed a UTF-8-only decode assumption in the workspace;
IfcOpenShell's native reader can read the unchanged source. Fix and regress the
actual input seam before judging model scale. The final case replay and timing
must use the final shared-check implementation.
