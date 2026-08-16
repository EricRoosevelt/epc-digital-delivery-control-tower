# TMDL Implementation Template

This document is not a TMDL definition and must not be renamed or presented as
a PBIP semantic model. Apply it only after Power BI Desktop has created the
PBIP skeleton and all nine Power Query tables exist. Prefer Desktop's TMDL view
and preview the diff before applying changes.

Never create a complete `createOrReplace model` script from this document.
First script the Desktop-created objects to a new TMDL tab, then add the
relationship and metadata fragments below to those real objects. If supported
`definition/**` files are edited externally, close Desktop first and restart it
afterward. Do not edit cache, local settings, legacy report, or diagram files.

## Exact Active Relationships

| Name | One side | Many side | Filter direction |
|---|---|---|---|
| `DimModel_DimElement` | `DimModel.model_id` | `DimElement.model_id` | Single |
| `DimModel_FactRequirementCoverage` | `DimModel.model_id` | `FactRequirementCoverage.model_id` | Single |
| `DimRun_FactIDSCheck` | `DimRun.run_id` | `FactIDSCheck.run_id` | Single |
| `DimRun_FactRequirementCoverage` | `DimRun.run_id` | `FactRequirementCoverage.run_id` | Single |
| `DimRequirement_FactIDSCheck` | `DimRequirement.requirement_key` | `FactIDSCheck.requirement_key` | Single |
| `DimRequirement_FactRequirementCoverage` | `DimRequirement.requirement_key` | `FactRequirementCoverage.requirement_key` | Single |
| `DimElement_FactIDSCheck` | `DimElement.element_key` | `FactIDSCheck.element_key` | Both |
| `DimElement_DimTopic` | `DimElement.element_key` | `DimTopic.element_key` | Both |

For a Tabular relationship, the `fromColumn` is the many side and the
`toColumn` is the one side. The two bidirectional fragments therefore follow
this form after the actual Desktop-created lineage tags have been preserved:

```tmdl
relationship DimElement_FactIDSCheck
    fromColumn: FactIDSCheck.element_key
    toColumn: DimElement.element_key
    crossFilteringBehavior: bothDirections

relationship DimElement_DimTopic
    fromColumn: DimTopic.element_key
    toColumn: DimElement.element_key
    crossFilteringBehavior: bothDirections
```

For the other six relationships, omit `crossFilteringBehavior` or retain the
Desktop-generated one-direction setting. Do not add active relationships from
either bridge table. Do not add direct `DimRun`-to-`DimTopic` or
`DimModel`-to-`DimTopic` relationships: with the two controlled bidirectional
paths, those shortcuts create ambiguous filter routes.

## Table and Column Metadata

- Hide `BridgeTopicFinding` and `BridgeViewpointComponent` from report view.
- Hide technical IDs on all other tables unless needed for drill-through.
- Keep `model_id`, `element_key`, `finding_key`, `requirement_key`,
  `topic_guid`, and `viewpoint_guid` as Text; never summarize them.
- Keep `component_index`, `finding_count`, and coverage counts as Whole Number.
- Keep `is_applicable`, `is_issue`, `has_representation`, and
  `highlight_verified` as Boolean.
- Format pass-rate and lineage-coverage measures as `0.00%`.
- Disable Auto date/time and automatic relationship discovery.
- Put KPI measures in a display folder named `Control Tower KPIs`; put mapping
  audit measures in `Speckle Mapping Audit`.

## Post-Apply Validation

After applying model changes, run **Refresh**, save, close, reopen, and rerun
the offline validator. A model metadata preview or successful TMDL apply does
not refresh data and does not prove that the Speckle visual can render or
highlight an object.
