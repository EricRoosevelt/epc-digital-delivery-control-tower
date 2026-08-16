# Stage 3B Desktop Acceptance Evidence

This directory is the tracked, de-identified evidence boundary for the final
Power BI Desktop acceptance of `EPCDeliveryControlTower`. The authoritative
machine-readable index is `acceptance_manifest.json`. The evidence set is valid
only when `python src/validate_pbip.py` reports
`PBIP_STATIC_CONTRACT_AND_EVIDENCE_INTEGRITY_PASSED`.

## Required evidence set

The final directory contains exactly these five PNG files plus this README and
the acceptance manifest:

| File | Acceptance state represented |
|---|---|
| `relationship-autodetect-disabled.png` | **Current File > Data Load** with **Autodetect new relationships** visibly disabled |
| `overview-final.png` | Post-reopen overview with the seven fixed KPIs and the final 39/17/31/6/3/6/3 data state |
| `topic-7fe29ad3-674a-57fe-aa74-325e34053ffc.png` | Topic for `hvac::34Y6EIt3nDCAS1k$kPGOKm`, one highlighted component and two linked findings |
| `topic-be0ef29b-2855-5f97-b60e-466abc66252d.png` | Topic for `hvac::38WbwIGD90nB_3T2BTU5Ed`, one highlighted component and two linked findings |
| `topic-dbfa5125-2ea0-5587-ab5b-947a02c3ba49.png` | Topic for `hvac::23uPJWDfXEcwHH3kdFgV9c`, one highlighted component and two linked findings |

The manifest records each PNG's lowercase SHA-256. It also binds the captures
to the Desktop version and capture time, the tracked PBIR/TMDL definition-tree
hash, the post-reopen `relationships.tmdl` hash and exact count of eight, and
the current IDS/BCF data hashes. Any missing, renamed, extra, or modified PNG
causes validation to fail.

## Acceptance represented

The final Desktop run follows this lifecycle in a unique `%TEMP%` private PBIP
copy: import the separately installed official Speckle visual 2026.6.0, set the
local repository parameter, Refresh, Save, Close, Reopen, and Refresh again.
Credentials, connector state, expanded custom-visual files, caches, and the
private copy are not committed.

Manual acceptance checks the following fixed results:

- KPI values: Total Elements 39; Evaluated Elements 17; Applicable Check Pass
  Rate 80.65%; Failed Checks 6; Noncompliant Elements 3; BCF Lineage Coverage
  100%; Open Topics 3.
- Discipline results: Architecture 8/8 PASS; Structural 14/14 PASS; HVAC 3/9
  PASS with 6 FAIL checks and 3 noncompliant elements.
- Mapping audit: semantic identity 39/39, renderable 32, non-renderable 7.
- Rule results: R-005A filters to 1 element and 2 FAIL checks; R-005B filters
  to 2 elements and 4 FAIL checks.
- Priority `Medium` and assignee `model-coordination@example.invalid` each
  propagate to the 3 issue elements.
- Each Topic selection drives the Speckle visual to exactly one highlighted
  component and displays exactly two linked findings.

The static validator separately verifies the four slicer bindings, Topic table
binding, active relationship paths, Speckle `Model Info` / `Object IDs` /
`element_key` roles, and the deterministic BCF lineage. The screenshots are
manual visual evidence; they do not independently prove the underlying query
logic or connector API behavior.

## Privacy boundary

Every capture is reviewed before tracking. No real Speckle URL, account
identity, token, credential, private Speckle object ID, or local absolute path
may be visible in pixels or PNG metadata. Sample `element_key` and BCF Topic
GUID values are intentionally retained because they are public fixture
identities required for lineage verification.

The tracked PBIP remains de-identified. Real model/version and Federation URLs
stay only in ignored `dashboard/local/speckle_connections.json`; the
Federation URL is audit-only and is not a report query source.

## Accepted state

The five screenshots and `acceptance_manifest.json` were completed after the
ignored connection manifest passed the full offline data gate and the final
Refresh/Save/Close/Reopen/Refresh lifecycle succeeded in Power BI Desktop
2.156.951.0. The user manually verified the Rule, Topic, Priority, and Assignee
interaction paths and accepted the captured card rendering at the evidence
viewport. The evidence is delivery-ready only while the PBIP validator, full
dashboard gate, test suite, and screenshot hashes all continue to pass.
