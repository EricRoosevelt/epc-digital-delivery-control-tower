# IDS Validation Rules

Version: 0.1
Status: Draft

This directory contains the project-authored Information Delivery
Specification used by the EPC Digital Delivery Control Tower prototype.

## Purpose

The IDS defines machine-readable information requirements for the public
buildingSMART sample IFC models.

The validation results show whether the sample data satisfies these selected
project rules. A failed project-authored rule must not automatically be
described as a defect in the buildingSMART sample model.

## Rule Groups

| Rule ID | Applicability | Requirement | Severity | Origin |
|---|---|---|---|---|
| `R-001` | `IfcWall` | The IFC `Name` attribute must be provided | Error | General project information requirement |
| `R-002` | `IfcWall` | `Pset_WallCommon.IsExternal` must be provided as an IFC boolean | Error | General project information requirement |
| `R-003` | `IfcBeam` | `Pset_BeamCommon.LoadBearing` must be provided as an IFC boolean | Error | General project information requirement |
| `R-004` | `IfcDuctSegment` and `IfcAirTerminal` | The element must have an applicable spatial assignment | Error | General coordination requirement |
| `R-005` | Selected HVAC elements | `EPC_Delivery.AssetTag` and `EPC_Delivery.SystemCode` must be provided | Warning | Project-specific assumed EPC delivery requirement |

## Rule Interpretation

### R-001: Wall name

Every applicable `IfcWall` must provide its IFC `Name` attribute.

The rule checks information presence. It does not enforce a naming convention
in version 0.1.

### R-002: Wall external classification

Every applicable `IfcWall` must provide the property:

`Pset_WallCommon.IsExternal`

The property indicates whether the wall is external. Version 0.1 checks that
the property exists and uses the IFC boolean data type; it does not require a
particular true or false value.

### R-003: Beam load-bearing classification

Every applicable `IfcBeam` must provide the property:

`Pset_BeamCommon.LoadBearing`

Version 0.1 checks that the property exists and uses the IFC boolean data
type; it does not require a particular true or false value.

### R-004: HVAC spatial assignment

Every applicable `IfcDuctSegment` and `IfcAirTerminal` must be assigned to an
appropriate IFC spatial container, such as an `IfcSpace` or
`IfcBuildingStorey`.

This supports coordination because an element without a usable spatial
assignment cannot reliably be grouped by room, floor, or delivery zone.

This rule group may be represented by more than one IDS specification because
different IFC classes can require separate applicability definitions.

### R-005: Assumed EPC delivery metadata

Applicable MEP distribution elements must provide:

- `EPC_Delivery.AssetTag`
- `EPC_Delivery.SystemCode`

The custom property set deliberately does not use the `Pset_` prefix. That
prefix is reserved for property sets defined by the official IFC dictionary,
as stated in the
[buildingSMART data-dictionary guidelines](https://technical.buildingsmart.org/services/bsdd/guidelines/).

This is a project-specific assumed EPC delivery requirement created for this
portfolio prototype. It is not presented as a mandatory requirement of the
buildingSMART sample files.

Version 0.1 reports failures of this rule as warnings. A production EPC project
could promote the severity to error if these fields were contractually
required.

## Result Status

Validation results use the following normalized statuses:

| Status | Meaning |
|---|---|
| `PASS` | An applicable element satisfies the requirement |
| `FAIL` | An applicable element does not satisfy the requirement |
| `N/A` | The model contains no elements to which the specification applies |

Zero applicable elements must be reported as `N/A`, not as 100 percent
compliance.

## Provenance

The IFC files are public buildingSMART sample data.

The validation rules in this directory are authored specifically for this
portfolio prototype. They are informed by the buildingSMART IDS standard but
are not official buildingSMART delivery requirements.
