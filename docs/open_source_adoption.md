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
| [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) | 0.8.5 | Upstream source and wheel metadata: LGPL-3.0-or-later. The binary wheel's native extension also contains type names and strings from third-party geometry libraries, including CGAL packages whose source files are GPL-3.0-or-later or LGPL-3.0-or-later (each also commercially licensable); see [IfcOpenShell binary wheel](#ifcopenshell-binary-wheel) | Direct Python dependency for IFC parsing, installed from PyPI by pip; no upstream source is copied and no wheel or binary is redistributed. The default geometry library (OpenCASCADE) is used; the CGAL-based geometry library is not selected. |
| [IfcTester](https://github.com/IfcOpenShell/IfcOpenShell) | 0.8.5 | LGPL-3.0-or-later | Direct Python dependency for IDS processing; reports are generated project artifacts. |
| [IfcOpenShell BCF library (`bcf-client`)](https://github.com/IfcOpenShell/IfcOpenShell) | 0.8.5 | Wheel classifier: GPLv3; upstream source metadata: LGPL; unresolved conflict | Installed only as an IfcTester transitive dependency. The normative BCF generator and validator do not import it; an optional non-gating interoperability smoke test may use it when already installed. |
| [pandas](https://github.com/pandas-dev/pandas) | 3.0.5 | BSD-3-Clause | Direct Python dependency for deterministic CSV products. |
| [xmlschema](https://github.com/sissaschool/xmlschema) | 4.3.2 | MIT | Direct Python dependency for strict validation against local XSD snapshots. Its installed copies of the W3C schemas are also what IfcTester's `ids.xsd` imports resolve to, so no W3C schema is vendored here; see `epc_control_tower.ids_schema`. |
| [pytest](https://github.com/pytest-dev/pytest) | 9.1.1 | MIT | Development-only test runner. |
| [three.js](https://github.com/mrdoob/three.js) (npm `three`) | 0.186.1; tarball SHA-256 `8cd068708ea44f2c73c944b1cead2ba2f0d5c15c8fc194e5700f4e4f4a033fe7`; per-file SHA-256 in `third_party/three/0.186.1/provenance.json` | MIT | Browser 3D runtime for the Doctor preview's planned locate view. Admitted, not yet vendored: when the view is built, exactly three files — `build/three.module.js`, `build/three.core.js` and `examples/jsm/controls/OrbitControls.js` — are copied unmodified from the pinned tarball into `third_party/three/0.186.1/`, Git text normalization is disabled for them, and they load as ES modules through an import map with no bundler. The test suite holds any vendored file to its recorded digest. Geometry is prepared by IfcOpenShell (above); no other browser 3D library is admitted. |
| [buildingSMART BCF-XML](https://github.com/buildingSMART/BCF-XML/tree/release_3_0) | `release_3_0`; exact commit and hashes recorded with snapshot | CC BY-ND 4.0 | Normative source for BCF-XML 3.0. Only unmodified schemas are vendored under `third_party/buildingsmart/bcf-xml/3.0/`; Git text normalization is disabled there. |
| [buildingSMART BCF-API](https://github.com/buildingSMART/BCF-API/tree/release_3_0) | `release_3_0` | CC BY-ND 4.0 | Standards reference for issue lifecycle and event semantics. No API schema or implementation is copied in Stage 3. |
| [buildingSMART Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files) — PCERT Sample Scene | Source URLs and SHA-256 values in `models.csv` | CC BY 4.0 | Three unmodified IFC sample files are portfolio inputs, with attribution retained. |
| [buildingSMART Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files) — ISO Spec Reference View 1.2 | Commit `cecf656112a54a0d8cdd8b06b9398bfea5163886`; per-file SHA-256 in `projects/iso-reference-view/project.toml` and `THIRD_PARTY_NOTICES.md` | CC BY 4.0 | Three further unmodified IFC 4 sample files form the second project fixture. Ingest verifies each hash on every run. |
| [buildingSMART IDS](https://github.com/buildingSMART/IDS) — implementer test cases | Commit `dba4549e57a3a98e725e086991e19800a76850b8`; per-file SHA-256 in `third_party/buildingsmart/ids/1.0/SHA256SUMS` | CC BY-ND 4.0 | Independent conformance judge for this project's IDS interpretation. Four of ten facet directories — 199 `.ids`/`.ifc` pairs — are vendored verbatim under `third_party/buildingsmart/ids/1.0/`; Git text normalization is disabled there and the digests are checked on every test run. The `development` branch is pinned rather than the `v1.0.0` tag because the tag predates this directory. |

If BCF 3.0 test cases are added later, they must be copied unmodified from the
same pinned BCF-XML revision, placed below the third-party namespace, and
accompanied by their source paths and SHA-256 values.

### IfcOpenShell binary wheel

The licence column above is not the whole record for IfcOpenShell. What the
installed 0.8.5 wheel contains was inspected on 2026-10-09; the evidence, and
what remains unverified, is in
[`docs/evidence/ifcopenshell-0.8.5-wheel-licensing-2026-10-09/`](evidence/ifcopenshell-0.8.5-wheel-licensing-2026-10-09/README.md).
In short:

- Verified for `ifcopenshell-0.8.5-py314-none-win_amd64.whl` (SHA-256
  `13a5992dc07e69c0c78df5479e1ff9635e6ce9fa70c841d9ce2931e8481eabb9`, equal to
  PyPI's published digest):
  - its metadata names only LGPL-3.0-or-later, through a classifier;
  - it ships no licence or notice files;
  - its single native extension contains CGAL type names, including
    `Polyhedron_3`, `Polygon_mesh_processing` and `Nef_polyhedron_3`, and Open
    CASCADE strings;
  - in CGAL, the headers for those packages are marked
    `GPL-3.0-or-later OR LicenseRef-Commercial`.
- Inferred from upstream build scripts, not verified in the binary:
  - CGAL v5.5.5 on Windows and v5.6.3 elsewhere;
  - OCCT 7.8.1;
  - MPIR or GMP, and MPFR.
- Not inspected: the other platform wheels, including the Linux wheel CI
  installs.
- Open, and not answered here: which terms govern that binary as distributed,
  and what would follow for source-only distribution or for any bundle. Those
  are questions for the user, and for legal advice if sought.

**Distribution scope (product decision, 2026-10-09).** For the résumé
release the project distributes source code only. Each user obtains
dependencies, including this wheel, with their own `pip install` from PyPI. No
installer, container image or offline package containing third-party binaries
is produced. This is a scoping decision, not a legal conclusion. Producing any
such bundle requires a new review against the evidence record first.

The CGAL-based geometry library (`hybrid-cgal-simple-opencascade`) was
measured during 3D research and is **not adopted**. Selecting it would be a
separate Review Gate decision.

## External Tools and Reference Implementations

| Project | Version policy | License | Permitted use |
|---|---|---|---|
| [buildingSMART IDS Audit Tool](https://github.com/buildingSMART/IDS-Audit-tool) | `ids-tool.CommandLine` 1.0.124 on NuGet; package SHA-256 `f0405a163c3e23c1fcd67a6f1b5397c4f618e2338adecb1de76a95d89e5d71ec` | MIT | Independent IDS syntax and content gate. Installed in CI as a pinned .NET global tool and invoked as an external process; no implementation is copied. Both rule documents under `ids/` are audited on every CI run, on both platforms. |
| [ifcqa-tool](https://github.com/tommylee0923/ifcqa-tool) | Reference only; no pinned dependency | Verify before any adoption | Learn from run manifests, quality gates, and finding/issue separation; do not copy code. |
| [Speckle Power BI](https://github.com/specklesystems/speckle-powerbi) | `v2026.6.0`, commit `3d6a9391b3b5576b0e49ef9e844763681695a299` | Visual directory LICENSE: Apache-2.0; package metadata says MIT | The report references the separately installed connector and visual. The signed-installer and installed-visual hashes are recorded, but the expired build artifact prevents a complete published inner-bundle hash chain, so no `.pqx`, `.pbiviz`, or expanded visual bundle is committed. |
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
- Use the official Speckle connector and visual as external installed products.
  Import visual version 2026.6.0 through Desktop; `CustomVisuals/**`, `.pqx`,
  and `.pbiviz` payloads are deliberately ignored and not redistributed.
- Retain the audited Apache-2.0 license and provenance record. The reviewed tag
  has no NOTICE file, and the Apache/MIT metadata difference remains disclosed.
- Authentication, federation URLs, Power BI workspace selection, publishing,
  and scheduled-refresh gateway configuration remain user-managed operations.

## Review Gate

Before adding any new external code, schema, fixture, binary, or service,
update this document and `THIRD_PARTY_NOTICES.md`, pin the version or commit,
record required attribution, and confirm that the proposed distribution model
is compatible with the repository's MIT license.
