# EPC Digital Delivery Control Tower

**From BIM Model Data to Delivery Decisions**

[![CI](https://github.com/EricRoosevelt/epc-digital-delivery-control-tower/actions/workflows/ci.yml/badge.svg)](https://github.com/EricRoosevelt/epc-digital-delivery-control-tower/actions/workflows/ci.yml)

This portfolio prototype converts multidisciplinary IFC model data and
project-authored information requirements into traceable digital-delivery
findings and future management KPIs.

It uses public buildingSMART sample models and clearly identifies
project-specific assumptions. It is not presented as a production deployment.

![EPC Delivery Control Tower overview](docs/evidence/stage_3b/overview-final.png)

## Two layers, and which numbers belong to which

This repository holds two things at once, and almost every number below belongs
to exactly one of them. Reading a figure from one layer as if it described the
other is the single easiest mistake to make here.

| | **Canonical pipeline** | **Frozen V1.0.0 showcase** |
| --- | --- | --- |
| What it is | The live framework: `epc-ct run`, every stage and exporter | A pinned demonstration of one project at one moment |
| Version | **Framework / data contract 1.6**, rule set 2.2 | V1.0.0, IDS v0.1, 47 findings |
| Scope | Both projects in `projects/` | One project, one frozen rule set version |
| Where it lands | `data/processed/canonical/`, `reports/bcf/issues.bcf` | The eight legacy CSVs, `reports/bcf/ids_failures.bcf`, the PBIP dashboard |
| Moves when | The pipeline or the rules change | **Never** — it is byte-pinned by test |

The Power BI / Speckle dashboard and its evidence screenshots read the **frozen
showcase**, not the canonical layer. That is why the dashboard still shows three
models and 47 findings while the canonical pipeline covers six and 121: the two
`Legacy…` exporters reproduce a frozen identity derivation on purpose, and they
retire together in Phase 5. See `AGENTS.md` for why that scope exists.

## Canonical pipeline at a glance (contract 1.6)

What one `epc-ct run` currently produces across every project in `projects/`:

| Canonical measure | Current result |
| --- | ---: |
| Projects | 2 |
| Source IFC models | **6** |
| Federated elements | **44** |
| Findings | **121** |
| Issues | **21** |
| Requirements | 14 |
| Project milestones | 6 |

These are the counts the framework stands behind today. They are produced by
the canonical stages and written to `data/processed/canonical/`; the general
`BcfExporter` projects the whole run into `reports/bcf/issues.bcf`.

## V1.0.0 showcase at a glance (frozen)

Everything in this section describes the **frozen** fixture and does not move.
The verified portfolio fixture contains three multidisciplinary IFC models and
39 federated element occurrences. The end-to-end workflow produces:

| Delivery measure | Verified result |
| --- | ---: |
| Source IFC models | 3 |
| Federated element occurrences | 39 |
| Evaluated elements | 17 |
| Applicable IDS checks | 31 |
| Passed / failed checks | 25 / 6 |
| Selected-rule applicable pass rate | 80.65% |
| Noncompliant elements | 3 |
| Deterministic BCF 3.0 topics | 3 |
| Failed-check-to-BCF lineage | 6/6 (100%) |

The 80.65 percent result is an **applicable-check pass rate for the selected
project-authored rules**, not an overall model-compliance score. The six
failed checks belong to three elements and generate three traceable BCF topics.

## What the frozen showcase demonstrates

The workflow behind the V1.0.0 figures above:

- parses Architecture, Structural, and HVAC IFC models;
- registers source-model identity and content hashes;
- extracts a 39-element federated model inventory;
- generates a project-authored IDS;
- validates all three IFC models in one batch;
- produces JSON, HTML, and normalized CSV validation results;
- converts the six failed checks into three deterministic BCF 3.0 issues;
- validates BCF XML, archive safety, model lineage, and repeatability;
- delivers a de-identified Power BI Project with seven KPI cards, four
  operational filters, BCF finding lineage, and Speckle 3D topic isolation.

## Data Pipeline

```text
Public IFC models
-> Python and IfcOpenShell
-> models.csv and model_inventory.csv
-> project-authored IDS requirements
-> IfcTester validation
-> per-model JSON and HTML reports
-> normalized ids_findings.csv
-> deterministic BCF 3.0 issues and analytical sidecars
-> Power BI semantic model and KPI measures
-> Speckle federated-model selection and topic isolation
```

## Data Products

### `data/processed/models.csv`

One row represents one source IFC model.

It records:

* stable `model_id`;
* source filename and discipline;
* IFC project GUID and schema;
* source-file SHA-256;
* source URL and license.

### `data/processed/model_inventory.csv`

One row represents one `IfcElement` occurrence in one source model.

| Field          | Description                                          |
| -------------- | ---------------------------------------------------- |
| `model_id`     | Stable source-model identifier                       |
| `source_model` | Source IFC filename                                  |
| `discipline`   | Model discipline                                     |
| `element_key`  | Federated unique key: stable model ID plus IFC GlobalId |
| `global_id`    | IFC GlobalId within the source model                 |
| `ifc_class`    | IFC entity class, such as `IfcWall` or `IfcBeam`     |
| `name`         | Element name                                         |
| `storey`       | Related `IfcBuildingStorey`, when available          |
| `pset_count`   | Number of property sets associated with the element  |

A bare IFC `GlobalId` is not treated as unique across federated discipline
files. Cross-model joins use:

```text
element_key = model_id::global_id
```

The fixture contains 39 unique `element_key` values but only 32 distinct bare
IFC GlobalIds because four GUID groups recur across discipline files. A bare
GlobalId is therefore never used as a federated join key.

### `data/processed/ids_findings.csv`

One row represents one normalized IDS requirement result for one applicable
element, or one `N/A` result when no elements are applicable.

This is a frozen legacy projection, not the canonical findings table; the
canonical one is `data/processed/canonical/findings.csv`, which currently holds
121 rows across both projects. The frozen batch produces 47 findings with the
normalized statuses:

* `PASS`;
* `FAIL`;
* `N/A`.

Every non-`N/A` finding can be traced back to a `model_id` and `element_key`.
Stable requirement and finding UUIDv5 keys are generated once in Python for
downstream lineage; dashboard queries do not reimplement identity logic.

The complete table definitions and constraints are documented in
[`docs/data_contract.md`](docs/data_contract.md).

## IDS Validation Rules

The project-authored IDS is:

```text
ids/epc_delivery_requirements_v0.1.ids
```

Version 0.1 contains five business rule groups implemented as seven IDS
specifications:

| Rule       | Requirement                                                                      |
| ---------- | -------------------------------------------------------------------------------- |
| `R-001`    | `IfcWall` must provide `Name`                                                    |
| `R-002`    | `IfcWall` must provide `Pset_WallCommon.IsExternal`                              |
| `R-003`    | `IfcBeam` must provide `Pset_BeamCommon.LoadBearing`                             |
| `R-004A/B` | `IfcDuctSegment` and `IfcAirTerminal` must have an applicable spatial assignment |
| `R-005A/B` | Selected HVAC elements must provide the assumed EPC `AssetTag` and `SystemCode` metadata |

R-005 is a project-specific assumed EPC delivery requirement. Its failure does
not mean the public buildingSMART sample model is defective.

Further rule definitions and interpretation are documented in
[`ids/README.md`](ids/README.md).

## Current Validation Results

| Rule group                        | Architecture | Structural |     HVAC |
| --------------------------------- | -----------: | ---------: | -------: |
| Wall Name                         |     PASS 4/4 |   PASS 4/4 |      N/A |
| Wall IsExternal                   |     PASS 4/4 |   PASS 4/4 |      N/A |
| Beam LoadBearing                  |          N/A |   PASS 6/6 |      N/A |
| Duct spatial assignment           |          N/A |        N/A | PASS 1/1 |
| Air-terminal spatial assignment   |          N/A |        N/A | PASS 2/2 |
| Assumed duct EPC metadata         |          N/A |        N/A | FAIL 0/1 |
| Assumed air-terminal EPC metadata |          N/A |        N/A | FAIL 0/2 |

In `ids_findings.csv`, the six failed requirement checks are reported as
`WARNING` because they belong to the project-specific R-005 assumption. This
severity is assigned by the project's normalization logic, not by the native
IfcTester report.

A zero-applicable result is normalized to `N/A`; it is not counted as 100
percent compliance.

`ids_findings.csv` is **not** the canonical source of truth. It is one of the
frozen legacy projections: a normalized view of one project under one pinned
rule set version, kept byte-stable so the published dashboard and its evidence
keep meaning what they meant. The canonical record for the whole run is
`data/processed/canonical/` — `findings.csv` and `issues.csv` in particular —
and any new consumer should read that instead. `ids_findings.csv` remains
authoritative for the V1.0.0 dashboard KPIs and for nothing else, and it
retires with the other `Legacy…` outputs in Phase 5.

The raw IfcTester JSON and HTML reports retain IfcTester's native aggregates,
where an optional zero-applicable specification may appear as passed even
though its individual section is marked as skipped. Those native headline
percentages must not be used as the dashboard compliance measure.

## Power BI and Speckle Control Tower

The tracked Power BI Project is under [`dashboard/`](dashboard/). Its semantic
model uses normalized repository data for KPIs and the official Speckle visual
for federated 3D selection. The accepted single-page report provides:

- seven formula-driven KPI cards;
- applicable-check and renderability views by discipline;
- Discipline, Rule, Priority, and Assignee filters;
- three BCF topics with two linked findings each;
- selection of exactly one issue element in the federated 3D view.

The Direct IFC connector mapping uniquely resolves all 39 inventory
`element_key` values. Of those, 32 elements have IFC representations and all
32 map to renderable objects. Seven `Representation=NULL` elements remain in
the semantic inventory and are reported separately; they are not claimed as
highlightable geometry. All three issue elements are mapped, renderable, and
verified in the topic workflow.

The committed PBIP/PBIR/TMDL source and de-identified evidence are public and
reproducible. Real Speckle model/version URLs, authentication state, cached
connector data, and the connected PBIX remain local and Git-ignored. Opening a
fully connected copy therefore requires Power BI Desktop, the official Speckle
connector/visual, and user-controlled access to the source models. See
[`dashboard/README.md`](dashboard/README.md) for the exact boundary and
reconnection procedure.

## Reports

The batch validation generates one JSON report and one HTML report for each
source model:

```text
reports/ids/architecture.json
reports/ids/architecture.html
reports/ids/structural.json
reports/ids/structural.html
reports/ids/hvac.json
reports/ids/hvac.html
```

JSON reports provide detailed machine-readable validation output. HTML reports
provide human-readable review output.

### BCF issue workflow

The current six `FAIL` findings form three element-level issues. Each issue has
exactly two linked findings, one perspective viewpoint, and one selected HVAC
IFC component. The issue wording records that a project-assumed information
requirement is unmet; it does not classify the public sample as defective.

Generated artifacts are:

```text
reports/bcf/ids_failures.bcf
reports/bcf/run_manifest.json
data/processed/bcf_topics.csv
data/processed/bcf_topic_findings.csv
data/processed/bcf_viewpoints.csv
data/processed/bcf_viewpoint_components.csv
data/processed/bcf_topic_events.csv
```

The normative generator and validator use the official pinned BCF 3.0 XSDs
and do not import `bcf-client`. See
[`docs/bcf_data_contract.md`](docs/bcf_data_contract.md) for identities,
sidecar grains, archive rules, and validation gates.

## Run Locally

Create and activate a Python virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Generate the model register and inventory:

```powershell
python src\extract_inventory.py
```

Generate the project IDS:

```powershell
python src\generate_ids.py
```

Validate all three IFC models and generate the reports and normalized findings:

```powershell
python src\validate_ids.py
```

Generate and strictly validate the deterministic BCF workflow:

```powershell
python src\generate_bcf.py
python src\validate_bcf.py
```

Install development dependencies and run the regression suite:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -p no:cacheprovider tests -q
```

Validate the repository-safe dashboard data and tracked Power BI Project:

```powershell
python src\validate_dashboard.py --mode core
python src\validate_pbip.py
python -m pip check
```

## Reproducibility and Input Protection

* Files in `data/raw` are read-only source inputs.
* The validation script checks each IFC file against its recorded SHA-256.
* The validation `run_id` is derived from the IDS and source-model hashes.
* Repeated validation with unchanged inputs produces the same ordered
  `ids_findings.csv`.
* The verified normalized findings SHA-256 is:

```text
ea7d2fa2cd1690eb8b791dcab2792f116238566f0c60b10b64f1b02ce504eb4d
```

* The deterministic BCF SHA-256 is:

```text
b3c6f51abc9647ef4baeee9f9bccd884094b362362e516778c4bf083326abc99
```

## Data Source and Attribution

The IFC sample models are taken from the buildingSMART International
[Sample-Test-Files repository](https://github.com/buildingSMART/Sample-Test-Files),
specifically the
[IFC 4 PCERT Sample Scene](https://github.com/buildingSMART/Sample-Test-Files/tree/main/IFC%204.0.2.1%20%28IFC%204%29/PCERT-Sample-Scene).

Files used:

* `Building-Architecture.ifc`
* `Building-Structural.ifc`
* `Building-Hvac.ifc`

A second project uses three further unmodified samples from the same
repository, the
[IFC 4 ISO Spec Reference View 1.2 set](https://github.com/buildingSMART/Sample-Test-Files/tree/cecf656112a54a0d8cdd8b06b9398bfea5163886/IFC%204.0.2.1%20%28IFC%204%29/ISO%20Spec%20-%20ReferenceView_V1.2),
pinned at commit `cecf656112a54a0d8cdd8b06b9398bfea5163886`:

* `wall-with-opening-and-window.ifc`
* `column-straight-rectangle-tessellation.ifc`
* `basin-tessellation.ifc`

Copyright buildingSMART International Ltd.

The sample files are licensed under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

The IDS rules and normalization logic are authored for this portfolio
prototype and are not official buildingSMART delivery requirements.

## Purpose Packs and Project Overlays

A **Purpose Pack** states a reusable question: which production activities a
handover is deciding about, what evidence each needs, and how those evidence
outcomes would reach a verdict. It names no project. A **Project Overlay** is
one project's policy against the Pack(s) it uses — which of that project's
validation rules answer a project-specific question, which methods it accepts,
how a role is staffed, and who may authorise a release. Neither holds an answer.

Both exist as files and both are read:

```text
purpose-packs/interdisciplinary-coordination-readiness/pack.toml
projects/pcert-sample/project.toml        # its [overlay] table
```

`epc_control_tower/purpose/` loads them and composes them for a project, or
refuses. Refusing is the whole behaviour on any defect: every version, binding,
reference and role must resolve, and the eighteen structural invariants a
decision tree must satisfy are checked at load time, before any project uses the
file. There is no partial load and no reduced-capability mode. Each refusal
carries a code naming the rule it enforces, so the mapping between the design
and the loader is a test rather than a claim.

**This is the input side, and only the input side.** What the composition
produces is validated *configuration*. It contains no verdict, no evidence
outcome, no reading, no assigned team, and no risk acceptance — not as a field,
not as a cached value. In particular:

* **Nothing evaluates a decision tree.** No evaluator exists. A Pack's tree is
  checked as a graph and never walked against a model.
* **Nothing records an assessment.** There is no assessment record, no
  `CONDITIONAL` promotion, and no place for either to be written.
* **A default role is not an assignment.** Composition checks that a Pack's
  `default_role` resolves through the Overlay's `team_mapping` — that the
  mapping *exists*. It does not produce the resolved assignment, because an
  assignment is a decision made against particular model versions, and this
  object has none.

So: readiness still cannot be computed here, and none of the boundaries in the
next section has moved.

**Nothing in the pipeline reads either file.** `epc-ct run`, `check`, `group`
and every exporter are unaffected by their presence, their contents, or their
absence; the loader is not a `Checker`, a `GroupingPolicy` or an `Exporter`, and
appears in no registry. That is measured rather than assumed: the test suite
runs the whole pipeline twice into the same destination — editing a Pack,
editing an Overlay, adding a Pack no project references, and giving a second
project an Overlay — and diffs every output byte.

**The worked Overlay's policy rows are illustrative, and say so.** Every row of
`pcert-sample`'s `team_mapping`, `risk_authorisations` and
`accepted_evidence_methods` carries `decision_basis = "illustrative"`: this
repository has never recorded a real staffing decision, risk-authorisation
policy, or accepted evidence method, and none of those nine rows should be read
as one. The field is required, has no default, and a row without it is refused —
so a demonstration value cannot quietly pass for a decision. The evidence
bindings and the convention note carry no such field and need none; they state
which of this repository's real rules answer a question, which is a fact rather
than a policy.

The shapes both files take, and why, are fixed in
[`docs/decisions/0002-minimal-purpose-pack-project-overlay.md`](docs/decisions/0002-minimal-purpose-pack-project-overlay.md).
What a runtime assessment *would* look like, if one were ever built, is designed
but not implemented in
[`docs/decisions/0003-runtime-purpose-assessment-shape.md`](docs/decisions/0003-runtime-purpose-assessment-shape.md).

## Not implemented

Named here because they are discussed around this project and are easy to assume
exist. Treat each as named-but-unbuilt, and do not infer a design from the name.

The Purpose *inputs* above are built. Everything that would turn them into an
answer is not, and that is the boundary this section is about.

* **Purpose assessment** — nothing walks a Pack's decision tree against a
  model, and no assessment record exists. Loading and composing a Pack and an
  Overlay establishes that the question is well-formed and that this project has
  supplied what the question needs; it produces no verdict, and there is no code
  that could. A second Pack, a Pack registry, and any Overlay override mechanism
  are likewise absent.
* **Readiness** — nothing computes whether a deliverable is ready. In
  particular, `Finding.is_issue` and the `Issue` record are *validation*
  concepts: `is_issue` says a check failed in a way that warrants a topic, and
  an `Issue` groups such findings. Neither is a readiness verdict, and reading
  them as one will produce a number the pipeline never claimed.
* **Blockers** — no blocker concept exists. The `Requirement` fields that look
  adjacent — `owner_role`, `severity`, `stage`, `priority`, `labels` — are
  contract 1.6 *rule metadata* carried for validation and for reproducing the
  frozen legacy archive. `priority` says when somebody will get to a failure,
  not what that failure stops; `owner_role` is the role the rule author expects
  to answer for the rule, not a final responsible-role decision. Nor does
  `discipline_scope` help: it says which disciplines a requirement is evaluated
  against, and carries no direction, so it cannot express an MEP-to-Architecture
  handoff. Direction would be Pack data.
* **Source fix and recheck** — there is no traceable loop from a fix made at
  source to the subsequent validation that confirms it. Today a fix and the run
  that follows it are two unrelated events, and nothing links them. What such a
  loop should do is an open question, not a settled one: recomputing only the
  changed objects is one possible answer, but it is not the assumed design and
  nothing here presumes it. For the avoidance of doubt about present behaviour,
  `epc-ct run` recomputes the full scope every time.

The three seams in `AGENTS.md` (`Checker`, `GroupingPolicy`, `Exporter`) are
extension points of the pipeline as it stands. They are not a roadmap, and none
of the above is a matter of implementing one of them — including the Purpose
loader above, which is deliberately none of the three and is registered
nowhere.

## Current Limitations

* The inventory is a selected `IfcElement` export, not a complete IFC database export.
* Geometry, materials, quantities, connections, and individual property values are not fully extracted.
* The first IDS version covers selected information requirements, not all BIM quality dimensions.
* Property actual values are left blank when IfcTester does not provide them consistently; the pipeline does not invent data.
* The validation results demonstrate a portfolio workflow, not a contractual model acceptance decision.
* The BCF workflow covers IDS failures only; it is not an issue-server sync.
* The Power BI evidence is a validated portfolio fixture, not a hosted
  production monitoring service.
* Revit may be used for optional downstream visual or BCF review, but it is not
  an ingestion, validation, or control-tower source of truth.
* A fully connected local Power BI/Speckle copy requires the private,
  explicitly confirmed model-version URLs described under `dashboard/`; those
  URLs and credentials are intentionally not distributed.
