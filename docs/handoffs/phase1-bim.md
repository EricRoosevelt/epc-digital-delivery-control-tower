# Phase 1 engineering guidance

The local review supports information checks and model navigation. It does not
assess clashes, clearances, fire safety, regulatory compliance or handover fitness.
Rules are evaluated against actual exported IFC data; actions remain proposals
until the source model is changed, re-exported and checked again.

## Rule meaning

| Rule | Applies to | Deterministic result | Practical response |
| --- | --- | --- | --- |
| PV-001 | IfcAirTerminal instances | The effective predefined-type text is one of DIFFUSER, GRILLE, LOUVRE, REGISTER | Verify the object's real function and IFC class mapping before selecting a value. A roof/chimney component may be misclassified as an air terminal. |
| INFO-001 | IfcElement instances | The instance Name contains a non-whitespace character | Confirm the naming convention and source export mapping. A type Name does not supply an instance Name automatically. |
| INFO-002 | IfcElement instances, including nested/hosted elements | A building storey resolves through containment and parent/decomposition relationships | Check whether storey grouping is useful and appropriate. A site/building-level object or multi-storey object may need no model change. |
| ID-001 | Displayed IfcElement instances; duplicate index includes all IfcRoot objects in that file | Compressed GlobalId format is valid and exactly one IfcRoot uses it in that file | Distinguish duplicate exports from distinct objects sharing an ID; preserve unaffected IDs and existing issue references. |

INFO-001 and INFO-002 are information prompts, not IFC defects. The runtime rule
metadata distinguishes their INFO severity from PV-001/ID-001 ERROR severity. A
failed prompt should be shown as something to review, not a mandatory repair.

PV-001 is the repository's product convention, not a project/client or statutory
requirement. IFC permits USERDEFINED and NOTDEFINED too. Existing checker
characterization in `tests/test_product_validation_ruleset.py` establishes
type-first resolution, fallback when the type has no effective value, and
USERDEFINED substitution through ElementType/ObjectType. Consequently, even
USERDEFINED plus the exact free text LOUVRE can pass. This is a text predicate,
not proof that the object's raw enum or engineering classification is correct.

## Source basis and judgment boundaries

- [IFC4 IfcRoot](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifckernel/lexical/ifcroot.htm)
  defines Name as optional and GlobalId uniqueness on rooted objects. Missing
  instance Name alone is not a schema defect.
- [IFC4 IfcBuildingStorey](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2/HTML/schema/ifcproductextension/lexical/ifcbuildingstorey.htm)
  describes storeys within the spatial hierarchy. Storey resolution is not room
  assignment and must not be inferred from geometry coordinates.
- [buildingSMART spatial containment examples](https://technical.buildingsmart.org/projects/2024tunnel/schema/ifcproductextension/lexical/ifcrelcontainedinspatialstructure.htm)
  illustrate why site/building containment can be appropriate. This source
  illustrates the concept; it is not an additional project requirement.
- [buildingSMART IFC GUID guidance](https://github.com/buildingSMART/technical.buildingsmart.org/blob/main/IFC-GUID.md)
  explains compressed identifiers. The local check covers format and uniqueness
  in one file only; cross-model reuse needs federation context, and identity
  continuity across revisions needs a separate comparison.
- The exact four-value policy and IFC4 ADD2 TC1 enumeration attribution are in
  `rules/product-validation/PV-001.toml`; no canonical rule was changed here.

Engineering judgment remains necessary for the correct source classification,
target naming convention, whether storey grouping is required, and whether an ID
collision represents duplicate export or distinct objects. The guidance does not
invent Revit parameter mappings, a responsible team, target values or completion.
A shared type or export-mapping change can affect multiple instances and should
be checked on the next export. Accepting/recording an exception or marking an
action handled does not convert a failed check to PASS.

## Implementation and evidence

`internal/doctor_adapter/guidance.py` exposes
`guidance_for(finding, element, language='en')`, returning summary, facts,
actions, verification, citations and limitations. English and Chinese are local,
deterministic and usable without an API key. Citations preserve the supplied
finding citation rather than inventing project authority. PASS, FAIL, N/A,
execution errors and unknown rules have distinct handling; workflow states do
not overwrite the check result. This module does not mutate its input or the IFC.

Validation performed with the existing repository virtual environment and the
isolated phase-1 checkout:

- `python -m pytest tests/test_doctor_guidance.py -q -p no:cacheprovider`:
  **60 passed**. Covers all four rules in English/Chinese, check statuses,
  source/type/instance boundaries, unsupported results and input purity.
- `python -m ruff check --no-cache internal/doctor_adapter/guidance.py tests/test_doctor_guidance.py`:
  **passed**.
- Real public demo through ReviewStore: **39 elements, 32 renderable meshes,
  156 findings: 2 errors, 19 information prompts, 98 PASS, 37 N/A**. Generated
  and inspected guidance for all 156 findings in both languages (312 documents).
  Both PV failures expose USERDEFINED free text (chimney cover / fireplace cap).
  The 19 unresolved-storey prompts include legitimate building/site containers;
  their current container is included in the runtime evidence.
- Read four actual `POST /api/review/advice` responses from the local server:
  PV-001 and INFO-002 in English and Chinese. All returned local guidance,
  preserved the observed values and citation, and retained the specific warnings
  against guessing a terminal enum or treating site-level containment as a defect.

The optional AI prompt was reviewed for engineering meaning. It preserves the
local guidance baseline, separates hypotheses from observations, limits PASS
claims, requires fresh-export verification and prohibits invented model fixes,
codes and citations. Suggested integration improvements were sent to the PM:
include INFO severity explicitly in the provider evidence/prompt; make requested
action counts conditional on check status; keep INFO badges consistent in list,
details and rule selection. No live provider response was evaluated here.

The initial targeted test run failed because the new guidance module did not yet
exist, then passed after implementation. No pipeline artifacts were regenerated.
An unprivileged `git diff --check` was unavailable in this worker's worktree
context, so repository-wide diff verification remains with the integrating PM.
