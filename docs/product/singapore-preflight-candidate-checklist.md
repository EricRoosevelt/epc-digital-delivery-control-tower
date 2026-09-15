# Singapore preflight candidates — not executable requirements

Date: 2026-09-16. All 13 candidates await BIM disposition. Identifiers below
are research row labels, not rule IDs, outcomes or a new machine contract.
Sources refer to the [source register](singapore-preflight-source-register.md).
None is claimed to be implemented merely by appearing here.

| Candidate | Question and basis | Required evidence / possible route | Limitation and corrective direction |
| --- | --- | --- | --- |
| C01 | Which submission route and stage actually apply? S01/S06, process applicability | Project type, area definition, submission history and dates; human confirmation | Do not infer from model area alone. Confirm project brief and applicable circular. |
| C02 | What is included in this handoff? Product requirement, not legislation | Declared disciplines, models, versions and expected scope; compare supplied inventory | Cannot detect undeclared intent. Manager confirms scope; missing models are not silently excluded. |
| C03 | Can the supplied IFC be read and does it satisfy the selected schema checks? S07 | File, declared schema, named validator and supported checks | Parser success is not schema compliance. Separate unsupported/unperformed validation from a pass; correct export settings. |
| C04 | Are identifiers usable and unambiguous within the intended identity scope? S05 plus product identity requirement | Entity identifiers, model/version namespace; scan and source mapping | Do not treat equal identifiers across different models as automatically wrong. BIM must confirm the precise rule; correct source/export workflow. |
| C05 | Is the required spatial structure represented? S04 | Site/building/storey/space relationships; targeted relationship inspection | Required structure depends on applicability. Empty counts alone cannot identify missing required spaces; correct Revit spatial organisation. |
| C06 | Do storey assignments and names match the chosen submission convention? S04 | Containment, levels and a confirmed convention | No invented naming regex or assumption that every element belongs to a storey. Correct level assignment or document an exception. |
| C07 | Are in-scope objects mapped to the appropriate IFC entity? S02/S03/S04 | Reviewed mapping/glossary rows and source category/export mapping | IFC class alone cannot prove the object was classified correctly. Include ambiguous/manual cases; correct source mapping. |
| C08 | Are predefined types and user-defined descriptions appropriate? S02/S04 | Entity-specific allowed values and relevant descriptions | No universal enum or blanket USERDEFINED prohibition. Confirm exact source row before implementing; correct type/export configuration. |
| C09 | Are required IFC-SG property sets present on applicable objects? S02 | Reviewed workbook rows, stage and entity applicability | Not every property set applies everywhere. Distinguish absent object from absent data; correct source shared parameters/export mapping. |
| C10 | Are required properties populated with the right data types? S02 | Reviewed property obligations, type and admissible empty-value rules | Presence alone does not prove truthful content. Do not treat zero as blank; correct source parameter values. |
| C11 | Do controlled values match the applicable vocabulary? S02 | Versioned enumerations and explicit applicability | Unknown enumeration is not a pass; do not silently normalise meaning. Correct source values after reviewer confirms the dictionary. |
| C12 | Is cross-model alignment supported by adequate evidence? S04 and existing product boundary | Named versions, coordinate context and accepted confirmation method | Shared marker/name/GlobalId and R-010 PASS are not alignment proof. Route to coordination confirmation, not automatic readiness. |
| C13 | Can an issue be traced back to the correct source element and revision? S05 export context; product traceability requirement | Revit version, export configuration and tested IFC-to-source identifier mapping | No name-based guessed match or promised Revit navigation. Verify mapping in an intake spike; fix export configuration if traceability fails. |

## Domain review and initial selection

For every retained candidate, BIM specifies exact source section or workbook
row, applicable stage/entities, exemptions, input evidence, failure example and
false-positive counterexample. Classify as initial automation, human review,
defer or reject. These are backlog dispositions, not evaluation verdicts.

The initial automated subset should be small enough to demonstrate one complete
source-fix/recheck loop. Select it after examining the actual model and source
editions; do not promise all 13 checks. C01/C02 remain human-confirmed inputs.
C07/C12 can require evidence beyond model data. C13 needs a real export probe.

## Acceptance before a candidate becomes a rule

- A licensed, version-specific source supports the precise claim; distinguish
  law, submission requirement, recommendation and project/product convention.
- Applicability is explicit. Missing required input is not PASS; excluded and
  unassessed scope remain visible rather than disappearing from totals.
- Framework can actually perform the named test; unsupported tests are not
  made green by a UI label or an IFC file successfully opening.
- At least one failing case, one valid case and one exemption/ambiguity case
  are reviewable. The fixing action points to the durable source model.
- Mapping a validation failure to a Purpose verdict is a separate reviewed
  decision. No automatic equation of a failed check with a delivery blocker.

Customer-supplied conventions can later enter through a reviewed configuration
workflow. This draft does not authorise an arbitrary rule builder, automatic
document-to-rule conversion, Pack overrides or a marketplace.
