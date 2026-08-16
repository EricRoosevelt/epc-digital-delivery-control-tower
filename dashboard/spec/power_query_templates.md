# Power Query Templates

These are query-editor templates, not PBIP or TMDL definition files. Create the
Power BI project in Desktop first. Paste each formula into a separately named
query and enable load for exactly the nine model tables listed here. Keep the
parameter, helper function, and Speckle staging queries connection-only.

The offline `DimElement` formula reads the ignored mapping audit CSV. In the
real connected report, replace that staging source with normalized output from
the official Speckle connector and preserve its native `Model Info` and
`Object IDs` typed fields. Do not construct those fields from CSV strings.

## Connection-Only Parameter: `RepositoryRoot`

Create a required Text parameter in Desktop. The committed project must use a
neutral placeholder, not a username-specific absolute path:

```powerquery-m
"C:\REPLACE_WITH_LOCAL_REPOSITORY"
```

## Connection-Only Function: `LoadProjectCsv`

```powerquery-m
(relativePath as text) as table =>
let
    NativeRelativePath = Text.Replace(relativePath, "/", "\"),
    Source = Csv.Document(
        File.Contents(RepositoryRoot & "\" & NativeRelativePath),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
in
    Headers
```

## Loaded Table: `DimModel`

```powerquery-m
let
    Source = LoadProjectCsv("data/processed/models.csv"),
    Selected = Table.SelectColumns(
        Source,
        {
            "model_id", "filename", "discipline", "ifc_project_guid",
            "ifc_schema", "content_sha256", "source_url", "license"
        }
    ),
    Typed = Table.TransformColumnTypes(
        Selected,
        List.Transform(Table.ColumnNames(Selected), each {_, type text})
    )
in
    Typed
```

## Loaded Table: `DimElement`

This offline authoring form proves the 39/39 tabular join. For the connected
report, the official connector staging query must expose the same seven audit
columns and additionally retain the native `Model Info` and `Object IDs`
fields before this merge.

```powerquery-m
let
    InventorySource = LoadProjectCsv("data/processed/model_inventory.csv"),
    Inventory = Table.TransformColumnTypes(
        InventorySource,
        {
            {"model_id", type text}, {"source_model", type text},
            {"discipline", type text}, {"element_key", type text},
            {"global_id", type text}, {"ifc_class", type text},
            {"name", type text}, {"storey", type text},
            {"pset_count", Int64.Type}
        }
    ),
    MappingSource = LoadProjectCsv("dashboard/local/speckle_mapping.csv"),
    Mapping = Table.TransformColumnTypes(
        MappingSource,
        {
            {"model_id", type text},
            {"speckle_ifc_guid", type text},
            {"inventory_global_id", type text},
            {"speckle_object_id", type text},
            {"speckle_model_version_url", type text},
            {"has_representation", type logical},
            {"highlight_verified", type logical}
        }
    ),
    CrossChecked = Table.AddColumn(
        Mapping,
        "ifc_guid_cross_check",
        each
            if [speckle_ifc_guid] = [inventory_global_id]
            then true
            else error "Speckle IFC GUID cross-check failed",
        type logical
    ),
    Joined = Table.NestedJoin(
        Inventory,
        {"model_id", "global_id"},
        CrossChecked,
        {"model_id", "speckle_ifc_guid"},
        "SpeckleMapping",
        JoinKind.LeftOuter
    ),
    Expanded = Table.ExpandTableColumn(
        Joined,
        "SpeckleMapping",
        {
            "speckle_ifc_guid", "inventory_global_id",
            "speckle_object_id", "speckle_model_version_url",
            "has_representation", "highlight_verified",
            "ifc_guid_cross_check"
        },
        {
            "speckle_ifc_guid", "inventory_global_id",
            "speckle_object_id", "speckle_model_version_url",
            "has_representation", "highlight_verified",
            "ifc_guid_cross_check"
        }
    ),
    Complete =
        if Table.RowCount(Expanded) <> 39
            or List.NonNullCount(Expanded[speckle_object_id]) <> 39
            or List.Count(List.Distinct(Expanded[speckle_object_id])) <> 39
        then error "Semantic identity mapping must be complete and one-to-one (39/39)"
        else Expanded
in
    Complete
```

## Loaded Table: `DimRequirement`

```powerquery-m
let
    Source = LoadProjectCsv("data/processed/ids_findings.csv"),
    Selected = Table.SelectColumns(
        Source,
        {
            "requirement_key", "specification_id", "specification",
            "requirement_id", "requirement"
        }
    ),
    DistinctRows = Table.Distinct(Selected, {"requirement_key"}),
    Validated =
        if Table.RowCount(DistinctRows) <> 9
        then error "DimRequirement must contain 9 rows"
        else DistinctRows
in
    Validated
```

## Loaded Table: `DimRun`

```powerquery-m
let
    Source = LoadProjectCsv("data/processed/ids_findings.csv"),
    Selected = Table.SelectColumns(Source, {"run_id", "ids_version"}),
    DistinctRows = Table.Distinct(Selected),
    Validated =
        if Table.RowCount(DistinctRows) <> 1
        then error "DimRun must contain 1 row"
        else DistinctRows
in
    Validated
```

## Loaded Table: `FactIDSCheck`

```powerquery-m
let
    Source = LoadProjectCsv("data/processed/ids_findings.csv"),
    Typed = Table.TransformColumnTypes(
        Source,
        {{"is_applicable", type logical}, {"is_issue", type logical}}
    ),
    Applicable = Table.SelectRows(
        Typed,
        each [is_applicable] = true and List.Contains({"PASS", "FAIL"}, [status])
    ),
    Validated =
        if Table.RowCount(Applicable) <> 31
        then error "FactIDSCheck must contain 31 applicable PASS/FAIL rows"
        else Applicable
in
    Validated
```

## Loaded Table: `FactRequirementCoverage`

The grouping grain is exactly `(run_id, model_id, requirement_key)`. This keeps
the nine requirements for all three models, including zero-applicable `N/A`
coverage, for 27 rows.

```powerquery-m
let
    Source = LoadProjectCsv("data/processed/ids_findings.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"is_applicable", type logical}}),
    Grouped = Table.Group(
        Typed,
        {
            "run_id", "model_id", "requirement_key", "specification_id",
            "specification", "requirement_id", "requirement"
        },
        {
            {
                "applicable_checks",
                each Table.RowCount(Table.SelectRows(_, each [is_applicable] = true)),
                Int64.Type
            },
            {
                "pass_checks",
                each Table.RowCount(Table.SelectRows(_, each [status] = "PASS")),
                Int64.Type
            },
            {
                "fail_checks",
                each Table.RowCount(Table.SelectRows(_, each [status] = "FAIL")),
                Int64.Type
            },
            {
                "na_rows",
                each Table.RowCount(Table.SelectRows(_, each [status] = "N/A")),
                Int64.Type
            }
        }
    ),
    WithRate = Table.AddColumn(
        Grouped,
        "pass_rate",
        each
            if [applicable_checks] = 0
            then null
            else [pass_checks] / [applicable_checks],
        Percentage.Type
    ),
    Validated =
        if Table.RowCount(WithRate) <> 27
        then error "FactRequirementCoverage must contain 27 rows"
        else WithRate
in
    Validated
```

## Loaded Table: `DimTopic`

```powerquery-m
let
    Source = LoadProjectCsv("data/processed/bcf_topics.csv"),
    Typed = Table.TransformColumnTypes(
        Source,
        {{"finding_count", Int64.Type}, {"creation_date", type datetimezone}}
    ),
    Validated =
        if Table.RowCount(Typed) <> 3
        then error "DimTopic must contain 3 rows"
        else Typed
in
    Validated
```

## Loaded Hidden Table: `BridgeTopicFinding`

```powerquery-m
let
    Source = LoadProjectCsv("data/processed/bcf_topic_findings.csv"),
    Selected = Table.SelectColumns(
        Source,
        {
            "run_id", "topic_guid", "finding_key", "requirement_key",
            "model_id", "element_key", "global_id"
        }
    ),
    Validated =
        if Table.RowCount(Selected) <> 6
        then error "BridgeTopicFinding must contain 6 rows"
        else Selected
in
    Validated
```

Do not create an active relationship from this table.

## Loaded Hidden Table: `BridgeViewpointComponent`

```powerquery-m
let
    Source = LoadProjectCsv("data/processed/bcf_viewpoint_components.csv"),
    Typed = Table.TransformColumnTypes(Source, {{"component_index", Int64.Type}}),
    Selected = Table.SelectColumns(
        Typed,
        {
            "run_id", "viewpoint_guid", "topic_guid", "component_index",
            "model_id", "element_key", "global_id"
        }
    ),
    Validated =
        if Table.RowCount(Selected) <> 3
        then error "BridgeViewpointComponent must contain 3 rows"
        else Selected
in
    Validated
```

Do not create an active relationship from this table.

## Speckle Staging Boundary

The connector query expressions are intentionally not fabricated here. Use
Desktop's **Get Data > Speckle** flow for each manually confirmed model/version
URL. Add a constant `model_id` in each query and normalize `speckle_ifc_guid`
from at least two agreeing Direct IFC identity fields. Support both the modern
raw `data.properties["IFC GUID"]` / raw
`data.properties["IFC Attributes"]["GlobalId"]` pair and the observed legacy
Direct IFC raw `data.properties["Attributes"]["GlobalId"]` / connector-
flattened `properties["GlobalId"]` pair. Then join the inventory GUID as
`inventory_global_id`. Never use `applicationId`, a Speckle object ID, a bare
GUID, or an IfcProject GUID as the federated business key. Inspect the
installed connector's actual preview before selecting fields. Keep all staging
queries load-disabled and merge their native `Model Info` and `Object IDs`
values into `DimElement` for the official visual.

The accepted data route is three independently pinned Direct IFC source
queries. For each entry in the ignored connection manifest, first require
`upload_route = "direct_ifc"`, then reconcile `source_filename` and
`ifc_sha256` with `filename` and `content_sha256` in
`data/processed/models.csv`. Load that entry's `model_version_url` with the
installed connector, and only after all three source tables succeed combine
them with the official `Speckle.Models.Federate({Architecture, Structural,
Hvac}, false)` helper. Do not substitute a Revit upload or a query against the
Federation URL.

`federation_url` is retained in `dashboard/local/speckle_connections.json`
only for read-only audit traceability. It must not be passed to
`Speckle.GetByUrl`, loaded into `DimElement`, or described as the final visual
data source.

The connected export must preserve the measured acceptance distribution: 15,
18, and 6 rows for Architecture, Structural, and HVAC; renderable counts 11,
16, and 5; non-renderable counts 4, 2, and 1. All 39 object IDs are globally
unique, all available GUID evidence fields agree on every row, and exactly the three issue rows
have `highlight_verified=true`.

`Speckle.GetByUrl` may also return hierarchy/container rows that are not
inventory `IfcElement` occurrences. A row with no IFC GUID evidence is excluded
as a non-identity container. Any candidate with fewer than two evidence fields,
or with disagreeing values after whitespace trim, fails closed. The flattened
`properties["GlobalId"]` field is accepted only as a cross-check for the
legacy Direct IFC shape; it cannot replace the raw identity field. The
downstream `(model_id, global_id)` join must still prove exactly one connector
match for every one of the 39 inventory rows.
