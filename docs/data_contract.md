# Data Contract

Version: 0.1
Status: Draft

This document defines the **frozen legacy** tabular data contract for the EPC
Digital Delivery Control Tower prototype — the eight CSVs under
`data/processed/` that the Power BI project reads, keyed on the legacy `run_id`.
It is deliberately at version 0.1 and does not move: through **contract 1.7**
every file it describes is byte-identical, including
`run_id ids-v0.1-8706ef58303bfd11`.

The evolving *canonical* surface — `data/processed/canonical/`, including the
`project_milestones.csv` table (`project_id, stage, due`) added in contract 1.6,
the `group_ref` column on `issues.csv`, and the `semantics_digest` column on
`requirements.csv` added in contract 1.7 — is versioned by `CHANGELOG.md` and
the recorded snapshots under `docs/contracts/`, not here. Keeping the two apart
is what lets the canonical model grow a column without disturbing the published
legacy contract this file governs. The one canonical rule this file states is
[what the rule set's digests cover](#canonical-rule-set-digests-contract-17),
because it decides when a legacy-looking identity can and cannot move.

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

## Canonical rule set digests (contract 1.7)

Not part of the legacy contract above; recorded here because it says what the
canonical identities do and do not respond to.

### `requirements.csv` column `semantics_digest`

- **Value:** 64 lowercase hexadecimal characters, a SHA-256.
- **Covers:** the predicate the requirement evaluates, as its rule declares it —
  the rule's `rule_id`, `checker` and `ifc_version`, every applicability facet
  (sorted), and every parameter of this requirement's own facet, less the fields
  its checker declares it does not evaluate. For the IDS checker that is
  `instructions`, which it hands to IfcTester as prose; the completeness checker
  publishes its `instructions` as each finding's `expected`, so there they are
  covered.
- **Does not cover:** the rule's title or description, the requirement metadata
  (`severity`, `owner_role`, `stage`, `discipline_scope`, `citation`,
  `priority`, `labels`), or an IDS requirement's `instructions`. Those still have
  a version provenance: they are published with the rule set's `(ruleset_id,
  version)`, and each run's internal coverage record carries a digest of every
  declared field.
- **Derivation:** the hashed document carries `derivation: 2`. Only values of
  the same derivation are comparable.
- **Empty value:** "no fingerprint was recorded" — a requirement read back from
  an `.ids` document, which today is only the frozen legacy rule set and never
  appears in this table. It does not mean "no semantics" and does not mean
  "unchanged"; treat it as not comparable.
- **What it is not:** a comparable fingerprint of what the rule checks. It is
  not the rule, and it does not show the check is correct.

### The rule set's normalized digest

`run.json` and each snapshot's `ruleset.normalized_digest` cover, per
requirement, the metadata and labels listed above **and** its
`semantics_digest` where non-empty. This is **derivation 2**, recorded in each
snapshot from contract 1.7 on as `ruleset.normalized_digest_derivation`.
Derivation 1 (contracts 0.1–1.6) covered the metadata only, so a facet edit —
applicability, `dataType`, `cardinality`, `name_pattern` — moved no
`validation_run_id` and no `finding_key`. A title or metadata edit moves the
digest under both derivations. Because an `.ids`-loaded requirement has an empty
`semantics_digest`, the frozen legacy rule set's digest is the same under both,
`ecd1477878548dea29b4187761ecc42ef87df1a28fb1df1c4bb5ce1ec8df256b`.

A recorded digest is compared with another only under the same derivation. The
snapshots recorded before derivations were written down are listed by name and
SHA-256 in `docs/contracts/ruleset-digest-derivations.json`, and the one
cross-derivation pair accepted — `epc-delivery` v2.2, contract 1.6 to 1.7 — is a
migration entry there, with its baseline and the evidence that the rules did
not change.

## Determinism

The same IFC files, IDS file, script version, and dependency versions must
produce the same ordered CSV content.

`run_id` will be derived from the IDS content and source model hashes so that
unchanged validation inputs produce the same identifier.
