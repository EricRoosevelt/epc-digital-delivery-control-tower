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
- Boolean CSV values are serialized as the lowercase strings `true` and
  `false`.
- The federated element key is:

```text
element_key = model_id::global_id
```

## Stable UUID Keys

Normalized requirement and finding keys use UUIDv5 with the fixed namespace:

```text
7611c2a0-c29a-50fa-b00d-5058d25a41d3
```

The UUID name is a versioned type prefix followed by a canonical JSON array.
Canonical JSON is produced with `ensure_ascii=False` and
`separators=(",", ":")`, so it contains no incidental whitespace. UUIDs are
stored as lowercase, hyphenated strings.

```text
requirement_key = uuid5(
  namespace,
  "requirement:v1:" + canonical_json([
    specification_id,
    requirement_id
  ])
)

finding_key = uuid5(
  namespace,
  "finding:v1:" + canonical_json([
    run_id,
    model_id,
    requirement_key,
    element_key or ""
  ])
)
```

Array order, empty-string handling, type prefix, and version are part of the
identity contract and must not be changed without an explicit schema version.

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

| Column             | Type    |    Required | Description                                             |
| ------------------ | ------- | ----------: | ------------------------------------------------------- |
| `finding_key`      | UUIDv5  |         Yes | Stable primary key for the normalized finding           |
| `run_id`           | string  |         Yes | Stable identifier for the validation inputs             |
| `model_id`         | string  |         Yes | Foreign key to `models.csv`                             |
| `element_key`      | string  | Conditional | Federated element key; blank only for `N/A`             |
| `global_id`        | string  | Conditional | IFC `GlobalId`; blank only for `N/A`                    |
| `ids_version`      | string  |         Yes | Project IDS version, such as `0.1`                      |
| `specification_id` | string  |         Yes | IDS `identifier`, such as `R-005A`                      |
| `specification`    | string  |         Yes | Human-readable IDS specification label                  |
| `requirement_id`   | string  |         Yes | Canonical IfcTester requirement label within the spec    |
| `requirement_key`  | UUIDv5  |         Yes | Stable key for `specification_id` plus `requirement_id` |
| `requirement`      | string  |         Yes | Human-readable requirement label                        |
| `status`           | string  |         Yes | `PASS`, `FAIL`, or `N/A`                                |
| `is_applicable`    | boolean |         Yes | `true` for `PASS`/`FAIL`; `false` for `N/A`             |
| `is_issue`         | boolean |         Yes | `true` only for `FAIL`                                  |
| `severity`         | string  |         Yes | `ERROR`, `WARNING`, or `INFO`                           |
| `ifc_class`        | string  | Conditional | IFC class; blank only for `N/A`                         |
| `element_name`     | string  |          No | IFC element name                                        |
| `expected`         | string  |         Yes | Expected information or relationship                    |
| `actual`           | string  |          No | Actual model value                                      |
| `reason`           | string  |         Yes | Human-readable validation explanation                   |

Constraints:

* `status` must be `PASS`, `FAIL`, or `N/A`.
* Zero applicable objects must produce `N/A`, not `PASS`.
* `specification_id` is read directly from the IDS specification identifier.
* `requirement_id` is the canonical requirement label emitted by IfcTester and
  must be unique within its specification.
* `requirement_key` must match its documented UUIDv5 payload.
* `finding_key` must be unique and match its documented UUIDv5 payload.
* The composite key `(run_id, model_id, requirement_key, element_key)` must be
  unique.
* `PASS` and `FAIL` rows have `is_applicable=true`; `N/A` rows have
  `is_applicable=false`.
* Only `FAIL` rows have `is_issue=true`.
* Every non-`N/A` row must contain `model_id` and `element_key`.
* Every `model_id` must exist in `models.csv`.
* A project-specific EPC requirement must be labelled as a project assumption.
* Official sample data failures must not automatically be described as defects.

## Determinism

The same IFC files, IDS file, script version, and dependency versions must
produce the same ordered CSV content.

`run_id` will be derived from the IDS content and source model hashes so that
unchanged validation inputs produce the same identifier.
