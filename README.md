# EPC Digital Delivery Control Tower

**From BIM Model Data to Delivery Decisions**

This portfolio prototype is being developed to convert multidisciplinary IFC models and BCF-style issue data into measurable digital-delivery KPIs. It uses public buildingSMART sample models and will use clearly labelled synthetic issue records. It is not presented as a production deployment.

## Current MVP

The current implementation parses three multidisciplinary IFC models:

- Architecture
- Structural
- HVAC

It extracts 39 `IfcElement` records into:

```text
data/processed/model_inventory.csv
```

## Data Pipeline

```text
IFC models -> Python and IfcOpenShell -> pandas DataFrame -> CSV inventory
```

## Extracted Fields

| Field          | Description                                         |
| -------------- | --------------------------------------------------- |
| `element_key`  | Federated unique key: source model plus IFC GlobalId |
| `source_model` | Source IFC filename                                 |
| `discipline`   | Model discipline                                    |
| `global_id`    | IFC GlobalId of the element                         |
| `ifc_class`    | IFC entity class, such as `IfcWall` or `IfcBeam`    |
| `name`         | Element name                                        |
| `storey`       | Related `IfcBuildingStorey`, when available         |
| `pset_count`   | Number of property sets associated with the element |

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

Run the inventory extraction:

```powershell
python src\extract_inventory.py
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

## Current Limitations

* The CSV is a selected `IfcElement` inventory, not a complete export of all IFC data.
* IFC GlobalIds may repeat across discipline files; `element_key` is used for cross-model joins.
* Geometry, materials, relationships, quantities, and individual property values are not yet extracted.
* BCF-style issue data, IDS validation, KPIs, and the Power BI dashboard are planned but not yet implemented.
* The project uses public sample models and is not evidence of a production deployment.
