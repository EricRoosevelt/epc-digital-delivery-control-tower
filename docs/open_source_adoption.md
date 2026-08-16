# Open-Source Adoption Policy

Version: 0.1

This document records how external software and standards inform the EPC
Digital Delivery Control Tower. It distinguishes a direct dependency or
vendored standard artifact from a design reference. A repository being listed
here does not mean its source code has been copied into this project.

## Adoption Rules

- Pin every executable dependency used by the reproducible pipeline.
- Record the upstream repository, exact release or commit, license, and use.
- Keep official schemas and test fixtures unmodified and verify their SHA-256.
- Do not store access tokens, credentials, private Speckle URLs, or local Power
  BI caches in Git.
- Do not copy GPL- or AGPL-licensed implementation code into this MIT-licensed
  repository. Such systems may be evaluated or deployed as separate services.
- Treat external dashboards as UX references only unless a later review
  explicitly approves code reuse under their license.

## Adopted Dependencies and Standards

| Project | Version or reference | License | Adoption and boundary |
|---|---|---|---|
| [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) | 0.8.5 | LGPL-3.0-or-later | Direct Python dependency for IFC parsing; no upstream source is copied. |
| [IfcTester](https://github.com/IfcOpenShell/IfcOpenShell) | 0.8.5 | LGPL-3.0-or-later | Direct Python dependency for IDS processing; reports are generated project artifacts. |
| [IfcOpenShell BCF library (`bcf-client`)](https://github.com/IfcOpenShell/IfcOpenShell) | 0.8.5 | Wheel classifier: GPLv3; upstream source metadata: LGPL; unresolved conflict | Installed only as an IfcTester transitive dependency. The normative BCF generator and validator do not import it; an optional non-gating interoperability smoke test may use it when already installed. |
| [pandas](https://github.com/pandas-dev/pandas) | 3.0.5 | BSD-3-Clause | Direct Python dependency for deterministic CSV products. |
| [xmlschema](https://github.com/sissaschool/xmlschema) | 4.3.2 | MIT | Direct Python dependency for strict validation against local XSD snapshots. |
| [pytest](https://github.com/pytest-dev/pytest) | 9.1.1 | MIT | Development-only test runner. |
| [buildingSMART BCF-XML](https://github.com/buildingSMART/BCF-XML/tree/release_3_0) | `release_3_0`; exact commit and hashes recorded with snapshot | CC BY-ND 4.0 | Normative source for BCF-XML 3.0. Only unmodified schemas are vendored under `third_party/buildingsmart/bcf-xml/3.0/`; Git text normalization is disabled there. |
| [buildingSMART BCF-API](https://github.com/buildingSMART/BCF-API/tree/release_3_0) | `release_3_0` | CC BY-ND 4.0 | Standards reference for issue lifecycle and event semantics. No API schema or implementation is copied in Stage 3. |
| [buildingSMART Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files) | Source URLs and SHA-256 values in `models.csv` | CC BY 4.0 | Three unmodified IFC sample files are portfolio inputs, with attribution retained. |

If BCF 3.0 test cases are added later, they must be copied unmodified from the
same pinned BCF-XML revision, placed below the third-party namespace, and
accompanied by their source paths and SHA-256 values.

## External Tools and Reference Implementations

| Project | Version policy | License | Permitted use |
|---|---|---|---|
| [buildingSMART IDS Audit Tool](https://github.com/buildingSMART/IDS-Audit-tool) | Pin an exact release or commit when introduced | MIT | Future independent IDS audit gate; call the tool without copying its implementation. |
| [ifcqa-tool](https://github.com/tommylee0923/ifcqa-tool) | Reference only; no pinned dependency | Verify before any adoption | Learn from run manifests, quality gates, and finding/issue separation; do not copy code. |
| [Speckle Power BI](https://github.com/specklesystems/speckle-powerbi) | Official installed connector and visual release | Apache-2.0 at the reviewed upstream repository | Use the separately installed connector and visual; do not vendor its binaries or source. Store no Speckle credentials or private URLs in Git. |
| [ifc4PowerBI](https://github.com/shift-construction/ifc4PowerBI) | Reference only | GPL; verify the exact upstream license before any use | Learn from Power Query and PBIX organization only; do not copy M code or package it with this project. |
| [APS BIM 360 Issue Dashboard](https://github.com/autodesk-platform-services/aps-bim360-issue-dashboard) | Reference only | Verify before any adoption | UX reference for overdue, ageing, and assignee KPIs; do not copy source. |
| [That Open Components](https://github.com/ThatOpen/engine_components) | Pin a release in Stage 4 if adopted | MIT | Candidate direct dependency for the future browser-based IFC/BCF viewer. |
| [OpenProject](https://github.com/opf/openproject) | Separate deployment only | GPL-3.0 | Workflow reference or separately deployed service; do not merge its backend code. |

buildingSMART Validate, Kontroll, and `ifc-bcf-viewer` remain evaluation
references for validation, OpenCDE architecture, and lightweight UX. Their
repositories, versions, and licenses must be identified before any artifact is
copied or dependency added. The retired `web-ifc-viewer` route is not adopted.

## Power BI and Speckle Boundary

- Track source-control-friendly PBIP metadata when Power BI Desktop creates it.
- Keep PBIX binaries, PBIP local caches, and `dashboard/local/` out of Git.
- Load Control Tower KPIs from the normalized project CSV contracts, not from
  IfcTester's native HTML headline percentage.
- Use the official Speckle connector and visual as external installed products;
  do not redistribute `.pqx` or `.pbiviz` files.
- Authentication, federation URLs, Power BI workspace selection, publishing,
  and scheduled-refresh gateway configuration remain user-managed operations.

## Review Gate

Before adding any new external code, schema, fixture, binary, or service,
update this document and `THIRD_PARTY_NOTICES.md`, pin the version or commit,
record required attribution, and confirm that the proposed distribution model
is compatible with the repository's MIT license.
