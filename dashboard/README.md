# Power BI Control Tower Handoff

This directory contains the Desktop-created, de-identified Power BI Project:

- `EPCDeliveryControlTower.pbip`
- `EPCDeliveryControlTower.Report/`
- `EPCDeliveryControlTower.SemanticModel/`

The project references the official Speckle 3D Visual and contains the fixed
nine-table TMDL model, eight explicit relationships, formula-driven DAX
measures, and the single-page English Control Tower. The compiled visual is an
external Desktop prerequisite: `CustomVisuals/**` is deliberately ignored and
is not redistributed. The committed repository parameter is a placeholder.
Exact Speckle URLs, credentials, connector state, cached data, and any
connected PBIX remain local and ignored.

Power BI Desktop created the PBIP/PBIR/TMDL skeleton before supported
`definition/**` files were edited. Import official visual version 2026.6.0 in
the temporary Desktop acceptance copy. Never create or externally edit
`.pbi/cache.abf`, `.pbi/localSettings.json`, legacy report metadata, or
diagram-layout files.

## Repository-Safe Assets

- `spec/model_contract.json`: machine-readable nine-table, relationship,
  mapping, and KPI contract.
- `spec/power_query_templates.md`: Power Query formulas for the repository CSV
  tables and the ignored local Speckle mapping export.
- `spec/speckle_connections.md`: exact ignored Federation/source connection
  manifest schema; all example URLs are deliberately invalid placeholders.
- `spec/tmdl_implementation.md`: relationship and metadata instructions to
  apply only after Desktop creates the project.
- `spec/measures.dax`: formula-driven DAX measure snippets.
- `spec/control_tower_theme.json`: English Power BI theme.
- `src/validate_dashboard.py`: offline, fail-closed acceptance validator.
- `src/validate_pbip.py`: fail-closed PBIP/PBIR/TMDL structure, binding,
  relationship, layout, and de-identification validator.
- `EPCDeliveryControlTower.*`: the Desktop-created de-identified PBIP delivery.
- `../docs/evidence/stage_3b/`: final Desktop acceptance screenshots, the
  fail-closed evidence manifest, and the evidence boundary.

No tracked asset is a PBIX, a connector cache, a real Speckle connection
manifest, or a substitute for the ignored local connection state.

## Locked Semantic Model

Only the following nine queries may have load enabled:

| Table | Rows | Role |
|---|---:|---|
| `DimModel` | 3 | Source-model identity and discipline |
| `DimElement` | 39 | Federated element identity plus Speckle mapping fields |
| `DimRequirement` | 9 | Stable IDS requirement identity |
| `DimRun` | 1 | Validation run identity |
| `FactIDSCheck` | 31 | Applicable PASS/FAIL checks only |
| `FactRequirementCoverage` | 27 | One run/model/requirement coverage row |
| `DimTopic` | 3 | BCF topics |
| `BridgeTopicFinding` | 6 | Hidden, disconnected BCF lineage bridge |
| `BridgeViewpointComponent` | 3 | Hidden, disconnected viewpoint bridge |

Disable automatic relationship detection. The exact eight active
relationships are recorded in `spec/model_contract.json` and
`spec/tmdl_implementation.md`. Only these two are bidirectional:

- `DimElement[element_key]` to `FactIDSCheck[element_key]`
- `DimElement[element_key]` to `DimTopic[element_key]`

Both bridge tables remain hidden and have no active relationship. DAX uses
`TREATAS`/`INTERSECT` for lineage so the model has no filter loop.

## Speckle Identity Contract

Use only IFC files uploaded directly to Speckle. Do not substitute a Revit
publish, because it produces a different object schema.

The business key is exactly:

```text
(model_id, speckle_ifc_guid)
```

`speckle_ifc_guid` is normalized from the installed connector's Direct IFC
schema. The current connector must support both observed shapes:

- modern: raw `data.properties["IFC GUID"]` cross-checked against raw
  `data.properties["IFC Attributes"]["GlobalId"]`;
- legacy Direct IFC: raw `data.properties["Attributes"]["GlobalId"]`
  cross-checked against the connector-flattened `properties["GlobalId"]`.

At least two non-blank identity fields must be present and every available
identity value must agree after whitespace trim. The canonical GUID is then
cross-checked against the inventory. `data.applicationId` is explicitly
forbidden as IFC identity evidence because Speckle does not guarantee that it
equals the IFC GUID.

Every row must cross-check that value against:

```text
inventory_global_id
```

`applicationId`, a Speckle object ID, and a bare IFC GUID are never federated
business keys. A Speckle object ID remains a visual-selection value only.

The complete local acceptance export is
`dashboard/local/speckle_mapping.csv`, which is ignored by Git. It must contain
these exact headers:

```text
model_id
speckle_ifc_guid
inventory_global_id
speckle_object_id
speckle_model_version_url
has_representation
highlight_verified
```

The file must contain all 39 elements: 15 Architecture, 18 Structural, and 6
HVAC rows. `speckle_ifc_guid` and `inventory_global_id` must be equal on every
row, and all 39 `speckle_object_id` values must be globally unique. The seven
elements whose IFC `Representation` is null remain in the file. The verified
render split is therefore Architecture 11/4, Structural 16/2, and HVAC 5/1
(renderable/non-renderable), for 32 true and 7 false rows overall. Set
`highlight_verified=true` only after an actual visual interaction proves the
element can be highlighted. Exactly the three BCF issue elements must be
mapped, renderable, and marked true; all other rows remain false.

The CSV is an audit/export interface. It cannot manufacture the connector's
native `Model Info` or `Object IDs` values and must not be used as a substitute
for the official Speckle query feeding the 3D visual.

Record the separately confirmed connection boundary in the second ignored
manual input, `dashboard/local/speckle_connections.json`:

```json
{
  "federation_url": "https://REPLACE_WITH_CONFIRMED_FEDERATION_URL",
  "models": [
    {
      "model_id": "architecture",
      "model_version_url": "https://REPLACE_WITH_ARCHITECTURE_VERSION_URL",
      "source_filename": "Building-Architecture.ifc",
      "ifc_sha256": "3ff9b10bd00c7b96dded51e7ca5a6b69efbea38b049adcdd05fcd247de7e70d5",
      "upload_route": "direct_ifc"
    },
    {
      "model_id": "structural",
      "model_version_url": "https://REPLACE_WITH_STRUCTURAL_VERSION_URL",
      "source_filename": "Building-Structural.ifc",
      "ifc_sha256": "68be722391e7aaa53bb9278645a02aa4b6382f13cc07548a1612e9b1dc3def67",
      "upload_route": "direct_ifc"
    },
    {
      "model_id": "hvac",
      "model_version_url": "https://REPLACE_WITH_HVAC_VERSION_URL",
      "source_filename": "Building-Hvac.ifc",
      "ifc_sha256": "11a8552bc555fa44dfdc49374d1ab2da0a16104c10f086af509f500ce03fa2b3",
      "upload_route": "direct_ifc"
    }
  ]
}
```

Do not copy these deliberately invalid placeholders. The completed manifest
must contain one exact, non-placeholder HTTPS Federation URL and exactly three
one-to-one `model_id` entries with the displayed filename, IFC hash, and
`upload_route=direct_ifc`. Each pinned `model_version_url` must exactly equal
that model's URL in `speckle_mapping.csv`. The Federation URL is retained only
as ignored audit information; it is not a semantic-model query source. The
report queries the three fixed versions and calls
`Speckle.Models.Federate({Architecture, Structural, Hvac}, false)` exactly
once. See `spec/speckle_connections.md`. Never store OAuth tokens, cookies, or
credentials in either local file.

## Desktop Reconnection and Verification Procedure

Use these steps to create a private connected acceptance copy without adding
connection state to Git:

1. Copy the three tracked `EPCDeliveryControlTower.*` project artifacts to a
   unique directory under `%TEMP%`. Do not modify `dashboard/local/**`.
2. Open that private PBIP in Power BI Desktop and set `RepositoryRoot` to the
   local repository path. Never copy that value back into the tracked TMDL.
3. Import the official installed Speckle visual version 2026.6.0 into the
   private copy. Do not copy its `.pbiviz` or expanded bundle into Git.
4. Under **Current File > Data Load**, confirm **Autodetect new relationships**
   is off. Do not add to or alter the eight explicit relationships.
5. With the existing connector session, run Refresh, Save, Close, Reopen, then
   Refresh again. The fixed query route receives the three pinned Direct IFC
   model versions and federates them in Power Query; it never loads a Revit
   conversion or the audit-only Federation URL.
6. Verify all seven KPI cards, the 32/7 render audit, Rule/Priority/Assignee
   propagation, and each of the three Topic selections. Capture the five final
   screenshots named in `../docs/evidence/stage_3b/README.md`.

OAuth, MFA, connector security prompts, confirmation of the three immutable
model/version URLs and the audit-only Federation URL, and visual-import
warnings always remain user-controlled checkpoints. A successful Python gate
requires the final five screenshot hashes and lifecycle attestations in
`../docs/evidence/stage_3b/acceptance_manifest.json`; it never infers those
manual facts from an absent or stale manifest.

## Single-Page English Report

Use a 16:9 page with these formula-driven cards:

- Total Elements: 39
- Evaluated Elements: 17
- Applicable Check Pass Rate: 25/31 = 80.65%
- Failed Checks: 6
- Noncompliant Elements: 3
- BCF Lineage Coverage: 6/6 = 100%
- Open Topics: 3

The page contains seven cards, two charts, two tables, four slicers
(Discipline, Rule, Priority, and Assignee), and one Speckle visual. Topic
selection is provided by the Topic table. The second table shows the two
findings linked to the selected Topic. Every KPI is calculated from normalized
CSV data; never use the IfcTester HTML headline percentage.

Filter acceptance is fixed:

- Architecture: 8/8 PASS
- Structural: 14/14 PASS
- HVAC: 3/9 PASS, 6 FAIL, 3 noncompliant elements
- R-005A: 1 element and 2 FAIL checks
- R-005B: 2 elements and 4 FAIL checks
- Priority Medium and the sole Assignee: all 3 issue elements
- Each topic: one highlighted element and exactly two linked findings

## Offline Validation

Validate the committed PBIP/PBIR/TMDL structure and de-identification boundary:

```powershell
python src\validate_pbip.py
```

The repository/core-data check is useful before BCF sidecars and the local
mapping exist, but it is deliberately not a Stage 3B acceptance result:

```powershell
python src\validate_dashboard.py --mode core
```

After deterministic BCF sidecars exist and both real ignored manual inputs
have been produced, run the fail-closed gate:

```powershell
python src\validate_dashboard.py --mode full `
  --mapping dashboard\local\speckle_mapping.csv `
  --connections dashboard\local\speckle_connections.json
```

The full data gate reports `OFFLINE_DATA_CONTRACT_PASSED`. The PBIP gate reports
`PBIP_STATIC_CONTRACT_AND_EVIDENCE_INTEGRITY_PASSED` only when its static
contract, post-reopen relationship hash, five screenshot hashes, lifecycle
attestations, interaction results, and privacy review all agree. Python checks
the evidence chain; the underlying Desktop interaction remains a manual
acceptance act.
