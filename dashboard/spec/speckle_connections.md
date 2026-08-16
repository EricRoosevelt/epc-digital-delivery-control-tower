# Speckle Connection Manifest Contract

This is a schema and handoff specification only. It is not a connector
configuration, does not contain credentials, and is not part of a PBIP/PBIR or
TMDL definition.

After manually confirming the three immutable source model/version URLs and
the exact Federation URL in Speckle, create the ignored local file
`dashboard/local/speckle_connections.json` with exactly this shape:

```json
{
  "federation_url": "https://REPLACE_WITH_CONFIRMED_FEDERATION_URL",
  "models": [
    {
      "model_id": "architecture",
      "model_version_url": "https://REPLACE_WITH_ARCHITECTURE_MODEL_VERSION_URL",
      "source_filename": "Building-Architecture.ifc",
      "ifc_sha256": "3ff9b10bd00c7b96dded51e7ca5a6b69efbea38b049adcdd05fcd247de7e70d5",
      "upload_route": "direct_ifc"
    },
    {
      "model_id": "structural",
      "model_version_url": "https://REPLACE_WITH_STRUCTURAL_MODEL_VERSION_URL",
      "source_filename": "Building-Structural.ifc",
      "ifc_sha256": "68be722391e7aaa53bb9278645a02aa4b6382f13cc07548a1612e9b1dc3def67",
      "upload_route": "direct_ifc"
    },
    {
      "model_id": "hvac",
      "model_version_url": "https://REPLACE_WITH_HVAC_MODEL_VERSION_URL",
      "source_filename": "Building-Hvac.ifc",
      "ifc_sha256": "11a8552bc555fa44dfdc49374d1ab2da0a16104c10f086af509f500ce03fa2b3",
      "upload_route": "direct_ifc"
    }
  ]
}
```

The `REPLACE_...` values above are deliberately invalid and cannot pass full
validation. The completed local manifest must satisfy all of these invariants:

- `federation_url` is one exact, absolute, non-placeholder HTTPS URL retained
  only as read-only audit metadata. It is not a Power Query source and does not
  provide the final visual data.
- `models` contains exactly three entries, mapped one-to-one to
  `architecture`, `structural`, and `hvac`.
- Every model entry contains exactly `model_id`, `model_version_url`,
  `source_filename`, `ifc_sha256`, and `upload_route`; no field may be omitted
  or added.
- Every `model_version_url` is immutable/version-pinned and exactly equals the
  URL for that `model_id` in `dashboard/local/speckle_mapping.csv`.
- Every `source_filename` and lowercase 64-character `ifc_sha256` exactly
  equals `filename` and `content_sha256`, respectively, for the same
  `model_id` in `data/processed/models.csv`.
- Every `upload_route` is exactly `direct_ifc`. A Revit, federation-upload, or
  other route does not satisfy this stage's source-provenance contract.
- The mapping CSV uses the normalized columns `speckle_ifc_guid` and
  `inventory_global_id`; they must match for every row. Its model distribution
  is 15 Architecture, 18 Structural, and 6 HVAC rows, with 39 globally unique
  `speckle_object_id` values.
- The Federation URL is distinct from each of the three source URLs.
- No token, cookie, OAuth response, email address, or other credential is
  recorded in either local acceptance file.

The machine-readable schema boundary is also locked in `model_contract.json`.
The local file is manual acceptance evidence; it is not loaded as one of the
nine semantic-model tables. Full offline validation reports
`OFFLINE_DATA_CONTRACT_PASSED` only after the three direct-IFC source records,
mapping URLs, filenames, and IFC digests all reconcile.
