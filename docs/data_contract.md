# Data Contract

Version: 0.1
Status: Draft

This document defines the tabular data contract for the EPC Digital
Delivery Control Tower prototype.

## General Rules

- Raw IFC files in `data/raw` are read-only inputs and must never be modified.
- Generated CSV files use `utf-8-sig` encoding.
- Column names use lowercase `snake_case`.
- Empty CSV values represent unavailable or non-applicable data.
- Generated rows must use deterministic ordering.
- A bare IFC `GlobalId` is not treated as unique across federated models.
- When pandas reads `ids_findings.csv`, use `keep_default_na=False` so the
  literal status `N/A` is not converted to a missing value.
- The federated element key is:

```text
element_key = model_id::global_id
```

## Table: `data/processed/models.csv`

One row represents one source IFC model.

| Column             | Type   | Required | Description                                                        |
| ------------------ | ------ | -------: | ------------------------------------------------------------------ |
| `model_id`         | string |      Yes | Stable project identifier: `architecture`, `structural`, or `hvac` |
| `filename`         | string |      Yes | Source IFC filename                                                |
| `discipline`       | string |      Yes | `Architecture`, `Structural`, or `HVAC`                            |
| `ifc_project_guid` | string |      Yes | `GlobalId` of the model's `IfcProject`                             |
| `ifc_schema`       | string |      Yes | IFC schema reported by IfcOpenShell                                |
| `content_sha256`   | string |      Yes | SHA-256 hash of the unmodified IFC file                            |
| `source_url`       | string |      Yes | Public source URL of the sample model                              |
| `license`          | string |      Yes | License of the source model                                        |

Constraints:

* `model_id` must be unique.
* `filename` must be unique.
* `content_sha256` must contain 64 hexadecimal characters.
* The current source model license is `CC BY 4.0`.

## Table: `data/processed/model_inventory.csv`

One row represents one `IfcElement` occurrence in one source model.

| Column         | Type    | Required | Description                                         |
| -------------- | ------- | -------: | --------------------------------------------------- |
| `model_id`     | string  |      Yes | Foreign key to `models.csv`                         |
| `source_model` | string  |      Yes | Source IFC filename                                 |
| `discipline`   | string  |      Yes | Model discipline                                    |
| `element_key`  | string  |      Yes | Federated unique key: `model_id::global_id`         |
| `global_id`    | string  |      Yes | IFC `GlobalId` within the source model              |
| `ifc_class`    | string  |      Yes | IFC entity class                                    |
| `name`         | string  |       No | IFC element name                                    |
| `storey`       | string  |       No | Related `IfcBuildingStorey`, when available         |
| `pset_count`   | integer |      Yes | Number of property sets associated with the element |

Constraints:

* `element_key` must be unique across the complete inventory.
* Every `model_id` must exist in `models.csv`.
* `pset_count` must be zero or greater.
* Missing `name` or `storey` values remain blank and are not replaced with invented data.

## Table: `data/processed/ids_findings.csv`

One row represents one normalized IDS validation result.

| Column          | Type   |    Required | Description                                 |
| --------------- | ------ | ----------: | ------------------------------------------- |
| `run_id`        | string |         Yes | Stable identifier for the validation inputs |
| `model_id`      | string |         Yes | Foreign key to `models.csv`                 |
| `element_key`   | string | Conditional | Federated element key; blank only for `N/A` |
| `global_id`     | string | Conditional | IFC `GlobalId`; blank only for `N/A`        |
| `ids_version`   | string |         Yes | Project IDS version, such as `0.1`          |
| `specification` | string |         Yes | IDS specification name                      |
| `requirement`   | string |         Yes | Requirement being evaluated                 |
| `status`        | string |         Yes | `PASS`, `FAIL`, or `N/A`                    |
| `severity`      | string |         Yes | `ERROR`, `WARNING`, or `INFO`               |
| `ifc_class`     | string | Conditional | IFC class; blank only for `N/A`             |
| `element_name`  | string |          No | IFC element name                            |
| `expected`      | string |         Yes | Expected information or relationship        |
| `actual`        | string |          No | Actual model value                          |
| `reason`        | string |         Yes | Human-readable validation explanation       |

Constraints:

* `status` must be `PASS`, `FAIL`, or `N/A`.
* Zero applicable objects must produce `N/A`, not `PASS`.
* The composite key `(run_id, model_id, specification, requirement, element_key)`
  must be unique.
* Every non-`N/A` row must contain `model_id` and `element_key`.
* Every `model_id` must exist in `models.csv`.
* A project-specific EPC requirement must be labelled as a project assumption.
* Official sample data failures must not automatically be described as defects.

## Determinism

The same IFC files, IDS file, script version, and dependency versions must
produce the same ordered CSV content.

`run_id` will be derived from the IDS content and source model hashes so that
unchanged validation inputs produce the same identifier.
