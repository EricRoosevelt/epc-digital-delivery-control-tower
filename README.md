# EPC Digital Delivery Control Tower

**From BIM Model Data to Delivery Decisions**

[![CI](https://github.com/EricRoosevelt/epc-digital-delivery-control-tower/actions/workflows/ci.yml/badge.svg)](https://github.com/EricRoosevelt/epc-digital-delivery-control-tower/actions/workflows/ci.yml)

This portfolio prototype converts multidisciplinary IFC model data and
project-authored information requirements into traceable digital-delivery
findings and future management KPIs.

It uses public buildingSMART sample models and clearly identifies
project-specific assumptions. It is not presented as a production deployment.

## Who it is for

* **BIM managers** who hand models from one discipline to the next and want to
  see what a pre-handover check found without reading JSON or using a command
  line. **BIM Doctor**, the local preview in [`doctor/`](doctor/), is for them.
* **BIM and digital-delivery engineers** who want a deterministic, extensible
  way to check IFC models against project-authored requirements and export the
  findings as issues and BCF. This repository is meant to be forked and adapted;
  start at [`AGENTS.md`](AGENTS.md).

## What it addresses

Before a model is handed from one discipline to another, a manager has to answer
a few plain questions: what is still open, which elements it concerns, what has
to change, who does it, and what a recheck must show. After a recheck: what
changed, and what is still open.

BIM Doctor lays those answers out for a check of IFC models against
project-authored requirements. It is careful about what it does not say. It gives
no overall compliance or constructability conclusion, a result that "cannot be
decided" is not a clean bill, and a change between two runs is never called a fix.
Underneath is the deterministic validation framework, `epc-ct`, described
[below](#two-layers-and-which-numbers-belong-to-which).

## BIM Doctor today

An internal, local preview: it runs on your machine, listens on `127.0.0.1` only,
and is not a release or a public interface. By default it shows a simulated
example and the bundled sample project; it cannot import your own models through
the interface.

**Language.** The interface opens in Chinese, and the Chinese interface is what the
screenshots below show and what this README recommends you try. An English wording
exists as a development trial and **has not been accepted**: it has not been
reviewed by a BIM domain specialist, and one next-step sentence on the example's
first-check path is known to differ in meaning from the Chinese and is being
corrected. Until it has been reviewed and corrected, do not rely on it, and do not
take it as a demonstration of the product. If you want to see it anyway, open any
address with `?lang=en`, or use the switch at the top of every screen. In English
the result of the check attempt on the bundled project, and the record, activity
and member pages, say "This page has not been translated yet".

![BIM Doctor home, Chinese interface: two entries, and a strip saying you cannot import your own Revit model and it gives no overall compliance conclusion](docs/evidence/doctor-first-minute-2026-10-03/zh-01-home.png)

*Home.* Two entries: **选择模拟示例** (choose a simulated example) and **查看这次检查尝试**
(view the check attempt on the bundled sample project, which did not start an
assessment and says why). The strip and the list at the foot say what it cannot do
yet: import, choose or change a model on the page, including your own Revit or IFC
model; give an overall compliance, constructability or "can be delivered"
conclusion; write back to a model, upload to the cloud, or open an element in
Revit.

![First-check result of the simulated example, Chinese interface: 13 items, 8 to handle, grouped by handling team](docs/evidence/doctor-first-minute-2026-10-03/zh-02-first-check-result.png)

*First-check result of the simulated example.* 13 items, 8 of which need handling:
4 **受阻** (blocked) and 4 **无法判断** (cannot be decided), involving 6 different
elements. An item is the conclusion for one element, or a pair assessed together,
on one piece of the receiving side's work, so the number of items is not a number
of defects. "Cannot be decided" means whether the work can start cannot be decided;
the page says it does not mean the element has no problem. Items are grouped by
handling team.

![One item, Chinese interface: an air terminal named "chimney cover", blocked because the project's required asset identity is missing](docs/evidence/doctor-first-minute-2026-10-03/zh-03-one-item.png)

*One item.* An air terminal named "chimney cover" in the `hvac` sample model is
**受阻** (blocked) for the work 房间数据表与设备明细表 (room data sheets and equipment
schedules): the project's required asset identity is missing (rule R-005B). Under
the conclusion the page gives what to do, the handling team, what it means for the
work (the work cannot start) and what a recheck must show. The element's class,
storey, model and GlobalId, and exactly which requirement is not met, follow
further down. The failing check is a real run of the shipped rule; the handling
team is the example's own setting and is marked as such. R-005 is a
project-specific assumption, not a defect of the public sample.

The screenshots use the bundled public sample only and were captured at commit
`872f76f`; see [their provenance](docs/evidence/doctor-first-minute-2026-10-03/README.md).

## Try it

Python 3.11 or newer (`pyproject.toml`; CI runs 3.14). There is no other install
step: `doctor/serve.py` imports the checkout directly.

```powershell
git clone https://github.com/EricRoosevelt/epc-digital-delivery-control-tower.git
cd epc-digital-delivery-control-tower
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python doctor/serve.py
```

On macOS or Linux, create and activate the environment with
`python3 -m venv .venv` and `source .venv/bin/activate`; the other lines are the
same.

1. Open <http://127.0.0.1:8765/>. The interface opens in Chinese.
2. Click **选择模拟示例** (choose a simulated example), then **打开这个示例的结果**
   (open this example's result) under step one, the first check.
3. Under any item, click **查看这一项：具体对象、要做什么、由谁处理、拿什么复检**
   (view this item: the element, what to do, who handles it, what a recheck must
   show).
4. Back in the catalogue, open step two, **模型未改，但交接判断发生变化** (models
   unchanged, but the handover judgement changed), to see the same record after a
   recheck.

The English interface (`?lang=en`) is an unaccepted development trial and is not
part of this walk; see *Language* above.

Stop the server with Ctrl+C; `--port` changes the port. The first result you open
in a session runs the shipped rules on the sample models once, in a scratch copy
under the system temporary directory that is removed afterwards; nothing is
written into the checkout.

## What works today

Four groups, so that a simulation is never read as a result and a built part is
never read as an accepted one.

**1. Implemented, and runs today on the public samples**

* `epc-ct run` validates the sample projects' IFC models (IDS validation and a
  cross-model completeness check) and writes findings, issues and a BCF 3.0
  archive: data contract 1.7, rule set 2.2, with the counts under
  [Canonical pipeline at a glance](#canonical-pipeline-at-a-glance-contract-17).
  CI regenerates every published artifact on Linux and Windows and fails if one
  byte moves.
* The Purpose Pack and Project Overlay loader, an assessment evaluator and a
  `recheck` that succeeds a sealed record
  ([below](#purpose-packs-and-project-overlays)). A library: there is no
  `epc-ct` command for it.
* The BIM Doctor preview software shown above: a local server and screens for the
  first check, one item and a recheck, in Chinese. An English wording exists as an
  unaccepted development trial.
* The frozen Power BI / Speckle showcase (below, under *Other entry points*).

**2. Shown only in simulation**

* The handover assessment in Doctor. The team arrangement, the accepted evidence
  methods and the human determinations (for example "does the opening pass
  through the receiving model's element") are the example's own settings, marked
  where they appear. The example cannot be used for a project decision and offers
  no export. In the first-check example the check results beside them come from a
  real run of the shipped rules; elsewhere a conclusion can also rest on a
  simulated check result, and each conclusion says which kind it cites.
* The recheck screens, shown on simulated scenarios built for the preview.
* The bundled sample project's own attempt, which Doctor's second entry shows
  being refused. That is the correct result, not a fault: the sample has never
  staffed a team or accepted an evidence method, so every assessment it could make
  would rest on a demonstration row (see the Purpose section below).

**3. A controlled real case, awaiting acceptance**

* Doctor's workspace entry, `python doctor/serve.py --workspace <dir> [--prior <dir>]`,
  shows the result of a real `epc-ct run` held in a workspace outside the
  checkout, and compares it with an earlier run. It shows check results and
  where to find each element in the authoring tool. It makes no handover
  assessment, names no team and never says anything was fixed. It is built on the
  isolated `product-validation` rule set 1.0 ([`rules/product-validation/`](rules/product-validation/README.md)),
  and the interface is described in [`doctor/README.md`](doctor/README.md). Its
  screens are in Chinese; an English wording exists as an unaccepted development
  trial.
  It has been exercised privately on one real IFC model under controlled
  conditions; that model is not in this repository. It has had one round of
  BIM-domain review. It is not yet accepted as a product feature: a
  walk-through of the real path by a person acting as manager, and product
  acceptance itself, are still to come.

**4. Not built**

* Importing your own Revit or IFC model through the interface.
* An overall compliance, constructability or "can be delivered" conclusion.
* Writing back to the model, uploading, and opening an element in Revit.
* Starting a recheck, marking an item resolved, assigning or notifying anyone,
  and exporting a recheck record.
* Accepting a risk, and continuing or ending a release.
* Attributing a change to a fix made in Revit or Tekla.
* A Singapore research view.

The first three of these are the limits Doctor's own home screen states; the
others are listed in [`doctor/README.md`](doctor/README.md) and in
[Not implemented](#not-implemented).

## Other entry points

* **Build on the framework.** Start at
  [`AGENTS.md`](AGENTS.md#where-to-extend): three extension points (`Checker`,
  `GroupingPolicy`, `Exporter`), a rule is one TOML file under `rules/<ruleset>/`,
  and a project is a directory under `projects/`. Run it with
  `python -m epc_control_tower.cli run`. The published contract is described in
  [`docs/data_contract.md`](docs/data_contract.md) and [`CHANGELOG.md`](CHANGELOG.md).
* **The frozen Power BI / Speckle showcase.** One project at one moment, V1.0.0,
  pinned byte for byte by test. Open the tracked Power BI Project under
  [`dashboard/`](dashboard/README.md); its acceptance evidence is in
  [`docs/evidence/stage_3b/`](docs/evidence/stage_3b/README.md). A fully connected
  copy needs Power BI Desktop and the official Speckle connector; see
  [Power BI and Speckle Control Tower](#power-bi-and-speckle-control-tower).

![EPC Delivery Control Tower overview, the frozen Power BI showcase](docs/evidence/stage_3b/overview-final.png)

## Two layers, and which numbers belong to which

This repository holds two things at once, and almost every number below belongs
to exactly one of them. Reading a figure from one layer as if it described the
other is the single easiest mistake to make here.

| | **Canonical pipeline** | **Frozen V1.0.0 showcase** |
| --- | --- | --- |
| What it is | The live framework: `epc-ct run`, every stage and exporter | A pinned demonstration of one project at one moment |
| Version | **Framework / data contract 1.7**, rule set 2.2 | V1.0.0, IDS v0.1, 47 findings |
| Scope | Both projects in `projects/` | One project, one frozen rule set version |
| Where it lands | `data/processed/canonical/`, `reports/bcf/issues.bcf` | The eight legacy CSVs, `reports/bcf/ids_failures.bcf`, the PBIP dashboard |
| Moves when | The pipeline or the rules change | **Never** — it is byte-pinned by test |

The Power BI / Speckle dashboard and its evidence screenshots read the **frozen
showcase**, not the canonical layer. That is why the dashboard still shows three
models and 47 findings while the canonical pipeline covers six and 121: the two
`Legacy…` exporters reproduce a frozen identity derivation on purpose, and they
retire together in Phase 5. See `AGENTS.md` for why that scope exists.

## Canonical pipeline at a glance (contract 1.7)

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

### BIM Doctor preview

```powershell
python doctor\serve.py
```

Then open <http://127.0.0.1:8765/>. The walk-through is under
[Try it](#try-it). To look at the result of a real `epc-ct run` held in a
workspace outside this checkout, add `--workspace <dir>` and, to compare it with an
earlier run, `--prior <dir>`; both are described in
[`doctor/README.md`](doctor/README.md).

### Canonical pipeline

```powershell
python -m epc_control_tower.cli check
python -m epc_control_tower.cli run
python -m epc_control_tower.cli snapshot
```

`check` validates without writing anything, `run` writes every enabled
exporter's artifacts, and `snapshot` compares the published contract with its
record. `epc-ct` is the same command once the package is installed; without
installing it, `python -m epc_control_tower.cli` does the same, as `AGENTS.md`
describes.

### Frozen showcase

The frozen V1.0.0 artifacts (the eight legacy CSVs and
`reports/bcf/ids_failures.bcf`) are written by the same `run`, through the two
`Legacy…` exporters; CI fails if a run changes any of their bytes. To validate
the frozen BCF archive strictly on its own:

```powershell
python src\validate_bcf.py
```

### Tests and gates

Install development dependencies and run the regression suite:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -p no:cacheprovider tests -q
```

One test, the IDS syntax audit, needs a tool the suite does not install and
skips with instructions without it; `AGENTS.md` lists the full gate order CI
runs.

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

What the composition produces is validated *configuration*. It contains no
verdict, no evidence outcome, no reading, no assigned team, and no risk
acceptance — not as a field, not as a cached value. A `default_role` in it is
still not an assignment: composition checks that the Overlay's `team_mapping`
*has* a row for it, and stops there, because an assignment is a decision made
against particular model versions and a configuration object has none.

### Running one

`epc_control_tower/purpose/assessment/` is the demand-driven operation that
turns those inputs into an answer. Given a project, a Pack, some activities, an
explicitly declared assessed scope and a model-version context, it either
refuses or returns one sealed **assessment record**, in which every subscope
carries the whole chain: the evidence read, the verdict, the `resolution_kind`,
the route that kind resolves through — consequence kinds, default role, next
action, recheck condition — and the team this project staffs that role with.

A few properties are worth stating because they are what the design is for:

* **A scope whose evidence disagrees is partitioned, not reduced.** There is no
  activity-level verdict. Under a scope of the whole `hvac` model, the schedules
  activity splits into three elements that fail R-005 and reach `BLOCKED`, and a
  zero-finding `IfcChimney` that reaches `UNKNOWN` — two subscopes, two
  verdicts, held apart.
* **Scope is declared, never discovered.** It never comes from which elements
  happen to carry a finding. An activity admits subjects from that scope by its
  declared `subject_classes` and by nothing else, so the `IfcChimney` is in for
  what it *is*, and the two `IfcBuildingElementProxy` setout markers are out for
  the same kind of reason — all three have zero findings.
* **Absence is never success.** A rule that applied to nothing reads as
  not-covered, not as a pass. Severity does not soften a verdict: R-005A and
  R-005B fail at `WARNING` and reach `BLOCKED`.
* **It moves no published byte.** The record lives outside `data/processed/`,
  `reports/`, `ids/` and the contract snapshot, is read back by nothing, and
  the one identifier it mints is never an input to any published value.

A sealed record can be **succeeded, never amended**. A `recheck` re-derives the
whole assessment from current evidence and returns a *new* sealed record saying,
for each subscope it answers for, three things that are not the same thing: where
that subscope's members are now, which of its evidence citations still carry, and
what could be established about its recheck condition — usually nothing, because
most of those conditions are sentences written for people and nothing here
adjudicates prose. A member that has vanished is classified — deleted from the
re-issued model, out of the activity's subject classes, a pair the current
determination no longer names, or a key this request's scope no longer declares —
and none of the four is read as resolved.

**Two things a production owner meets first, and neither is a fault.**

* **After a model re-issue, activities go back to `UNKNOWN`.** A determination is
  admissible only for the model versions it names, so a coordination review held
  against last week's export says nothing about this week's. The openings
  activity retreats from a `READY` pair and a `BLOCKED` pair to a single
  `UNKNOWN`, and the ceiling activity's alignment retreats to `not-yet-confirmed`.
  Nothing broke: the evidence behind the old verdicts was about models that no
  longer exist. What a recheck adds is the *reason* — that the citations stopped
  being attributable — rather than a bare `UNKNOWN`.
* **The sample in this repository produces no record, and that is permanent.**
  See below; it is a standing property, not an outstanding task.

**And one thing a production owner never meets, which is exactly why it is
written here.** Both notices above are things you run into. This one you cannot
run into, because what it is about is not in the record at all: **nobody in this
design is designated to declare the assessed scope, and an element nobody
declared is absent from every part of the answer.** Scope being declared rather
than discovered is the right decision and the reason the `IfcChimney` surfaces —
but it is declared by a person, and the accounting that says nothing disappears
is an accounting *of the declared keys*. A key that was never declared is not an
admitted subject, is not listed as out of class, and leaves no trace of the
place where it would have been. There is no check for this and there should not
be: nothing here has a concept of a scope being "too narrow", and no evidence
inside an assessment could tell the handover apart from what somebody
remembered.

The uncomfortable part is that a narrow scope reads *better*. Declare the whole
`hvac` model and the schedules activity answers `BLOCKED` over three elements
and `UNKNOWN` over a chimney no rule reached; declare just those three elements
and the same activity answers `BLOCKED` over three, with nothing `UNKNOWN` and
nothing reported out of class — every word of it true, and it looks like the
complete answer. A project adopting this design has to name who declares the
scope, and that person answers for declaring it narrowly. See
[`0003`](docs/decisions/0003-runtime-purpose-assessment-shape.md) §10.2 item 8.

**`pcert-sample` cannot produce one, that is the correct result, and it is a
standing property rather than a gap.** Every live verdict across its three
activities is non-`READY`, every non-`READY` subscope needs a resolving
assignment, and all four of its `team_mapping` rows are `illustrative` — so every
assignment it could make would rest on a demonstration row. The assessment
refuses, and names the four rows and the routes each one would have had to found.
Its three `accepted_evidence_methods` rows are `illustrative` too, so a
determination produced by one of those methods is refused on the same principle
from the other direction. This project has never appointed a team and has never
accepted an evidence method; nothing in this repository has been staffed, and no
record here claims otherwise. Making the sample produce a record would mean
writing `project-decision` onto nine rows describing decisions nobody took, which
is exactly what that field exists to prevent. Every positive path in the design is
covered instead on an isolated test fixture, through the same entry point and with
no test flag, no skip switch, and no relaxed check.

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
The runtime shape an assessment takes is fixed in
[`docs/decisions/0003-runtime-purpose-assessment-shape.md`](docs/decisions/0003-runtime-purpose-assessment-shape.md),
of which the evaluator and the `recheck` above are the implementation so far —
request scope, subscopes, the record, the identity boundary, and succeeding a
sealed record. What those two documents design and this implementation does not
build is listed below.

## Not implemented

Named here because they are discussed around this project and are easy to assume
exist. Treat each as named-but-unbuilt, and do not infer a design from the name.

The Purpose inputs, an evaluator over them, and a `recheck` that succeeds a
sealed record are built. What a *release* needs after that — accepting a risk,
carrying it forward, ending it — is not, and neither is anything that stores,
publishes, or acts on a record. That is the boundary this section is about.

* **Continuing or ending a release** — there is no `CONDITIONAL` promotion, and
  no `authorisation` successor record. A sealed record can be succeeded by a
  `recheck`, and that half is built and described above; what is missing is
  everything about accepting a risk. A release granted over a known deficiency
  has nowhere in this repository to be recorded at all, so there is nothing to
  carry forward and nothing to lapse. `authorisation` is named in the successor
  vocabulary so that the missing second kind is a designed gap on the record
  rather than one nobody thought of, and nothing sits behind the name. That
  naming is a statement of design and not a check: the field is an unvalidated
  string, and nothing in the code enforces the vocabulary. A second Pack, a Pack
  registry, and any Overlay override mechanism are likewise absent, as is any
  published machine contract or `epc-ct` command for an assessment. The only
  experience of one is the internal [BIM Doctor preview](doctor/README.md): it is
  not a release, it shows an example whose policy and determinations are
  simulated, and its attempt at the sample project's own assessment is refused
  (see above). Where a record is stored is also still an open decision: both
  entry points return one and write no file, and nothing stores a determination
  either — those are read by reference, from somebody else's store, and this
  repository has none.
* **Readiness from validation metadata** — a readiness verdict exists now, but
  only as a function of *(evidence outcome, decision tree)* and only inside an
  assessment record. It is never derived from validation metadata, and the
  distinction is load bearing rather than pedantic: `Finding.is_issue` and the
  `Issue` record are *validation* concepts — `is_issue` says a check failed in a
  way that warrants a topic, and an `Issue` groups such findings. Neither is a
  readiness verdict, the assessment cannot see either, and reading them as one
  will produce a number the pipeline never claimed.
* **Blockers outside an assessment** — `BLOCKED` is a verdict a subscope
  reaches, carrying a `resolution_kind` and the consequence *kinds* its Pack
  route names. Nothing else in this repository has a blocker concept, and the
  `Requirement` fields that look adjacent are not one: `owner_role`, `severity`,
  `stage`, `priority` and `labels` are *rule metadata* published in
  `requirements.csv`, carried for validation and for reproducing the frozen
  legacy archive. `priority` says when
  somebody will get to a failure, not what that failure stops; `owner_role` is
  the role the rule author expects to answer for the rule, not a final
  responsible-role decision; and severity does not soften a verdict. Nor does
  `discipline_scope` help: it says which disciplines a requirement is evaluated
  against, and carries no direction, so it cannot express an MEP-to-Architecture
  handoff — direction is Pack data. A consequence's *magnitude* is likewise
  absent: routes name kinds, the project's milestone dates are cited, and no
  duration, cost or delay is computed from either.
* **Source fix and recheck** — a `recheck` links a sealed assessment to a later
  validation run over the same members, and says of each one where it now stands.
  What nothing here can do is attribute any of that to a *fix*: no part of this
  repository observes a change made in Revit or Tekla, and the recheck is
  explicit that a member which has vanished is classified rather than read as
  resolved. So the loop from a fix made at source to the validation that confirms
  it is still missing its first half. What should close it is an open question,
  not a settled one: recomputing only the changed objects is one possible answer,
  but it is not the assumed design and nothing here presumes it. For the
  avoidance of doubt about present behaviour, `epc-ct run` recomputes the full
  scope every time.

Separately from any of that, eight things this design **cannot** do — and which
a project adopting it therefore has to give to a person — are recorded together
in [`docs/decisions/0003-runtime-purpose-assessment-shape.md`](docs/decisions/0003-runtime-purpose-assessment-shape.md)
§10.2, with the two that follow from the Pack/Overlay data shape in
[`docs/decisions/0002-minimal-purpose-pack-project-overlay.md`](docs/decisions/0002-minimal-purpose-pack-project-overlay.md)
§9. Two of them are the notices above, on that list because a production owner
runs into them without going looking, and one is the notice beside them that
nobody runs into — who declares the assessed scope, and what becomes of an
element nobody declared. The other five are about who is competent to determine
anything, what a `determiner` name does and does not prove, who owns the signal
that a cited determination was rewritten in place, why sealing a record does not
seal the documents it cites, and the fact that writing a record notifies nobody
and assigns nobody.

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
* The frozen BCF archive (`ids_failures.bcf`) covers the six IDS failures only.
  The canonical `issues.bcf` also carries failures from the cross-model
  completeness checker. Neither is an issue-server sync.
* The Power BI evidence is a validated portfolio fixture, not a hosted
  production monitoring service.
* Revit may be used for optional downstream visual or BCF review, but it is not
  an ingestion, validation, or control-tower source of truth.
* A fully connected local Power BI/Speckle copy requires the private,
  explicitly confirmed model-version URLs described under `dashboard/`; those
  URLs and credentials are intentionally not distributed.
