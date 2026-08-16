# EPC Digital Delivery Control Tower

**From BIM Model Data to Delivery Decisions**

This portfolio prototype converts multidisciplinary IFC model data and
project-authored information requirements into traceable digital-delivery
findings and future management KPIs.

It uses public buildingSMART sample models and clearly identifies
project-specific assumptions. It is not presented as a production deployment.

## Current MVP

The current implementation:

- parses Architecture, Structural, and HVAC IFC models;
- registers source-model identity and content hashes;
- extracts a 39-element federated model inventory;
- generates a project-authored IDS;
- validates all three IFC models in one batch;
- produces JSON, HTML, and normalized CSV validation results;
- converts the six failed checks into three deterministic BCF 3.0 issues;
- validates BCF XML, archive safety, model lineage, and repeatability.

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

### `data/processed/ids_findings.csv`

One row represents one normalized IDS requirement result for one applicable
element, or one `N/A` result when no elements are applicable.

The current batch produces 47 findings with the normalized statuses:

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

`ids_findings.csv` is the canonical normalized source for Control Tower KPIs.
The raw IfcTester JSON and HTML reports retain IfcTester's native aggregates,
where an optional zero-applicable specification may appear as passed even
though its individual section is marked as skipped. Those native headline
percentages must not be used as the dashboard compliance measure.

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

## Reproducibility and Input Protection

* Files in `data/raw` are read-only source inputs.
* The validation script checks each IFC file against its recorded SHA-256.
* The validation `run_id` is derived from the IDS and source-model hashes.
* Repeated validation with unchanged inputs produces the same ordered
  `ids_findings.csv`.
* The verified normalized findings SHA-256 is:

```text
4e655d7f82ef68c5d72750c2eb74a5e2fc4e799bf6f57d4a29bbad0afa44e18d
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

Copyright buildingSMART International Ltd.

The sample files are licensed under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

The IDS rules and normalization logic are authored for this portfolio
prototype and are not official buildingSMART delivery requirements.

## Current Limitations

* The inventory is a selected `IfcElement` export, not a complete IFC database export.
* Geometry, materials, quantities, connections, and individual property values are not fully extracted.
* The first IDS version covers selected information requirements, not all BIM quality dimensions.
* Property actual values are left blank when IfcTester does not provide them consistently; the pipeline does not invent data.
* The validation results demonstrate a portfolio workflow, not a contractual model acceptance decision.
* The BCF workflow covers IDS failures only; it is not an issue-server sync.
* KPI calculations and the connected Power BI/Speckle dashboard require the
  explicitly confirmed model-version and federation URLs described under
  `dashboard/`.
