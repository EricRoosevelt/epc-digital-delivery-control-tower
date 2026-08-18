# Third-Party Notices

The EPC Digital Delivery Control Tower source code is licensed under the MIT
License in `LICENSE`. That license does not replace the licenses that apply to
third-party software, standards, schemas, or sample data described below.

## Runtime and Development Dependencies

Python packages are installed from their upstream distributions and are not
vendored in this repository.

| Component | Version | License | Use |
|---|---:|---|---|
| [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) | 0.8.5 | LGPL-3.0-or-later | IFC parsing and model inspection |
| [IfcTester](https://github.com/IfcOpenShell/IfcOpenShell) | 0.8.5 | LGPL-3.0-or-later | IDS authoring, validation, and reporting |
| [BCF library (`bcf-client`)](https://github.com/IfcOpenShell/IfcOpenShell) | 0.8.5 | Conflicting metadata; see note below | Transitive dependency of IfcTester; not imported by the normative BCF generator or validator |
| [pandas](https://github.com/pandas-dev/pandas) | 3.0.5 | BSD-3-Clause | Normalized tabular data products |
| [xmlschema](https://github.com/sissaschool/xmlschema) | 4.3.2 | MIT | Strict XML Schema validation |
| [pytest](https://github.com/pytest-dev/pytest) | 9.1.1 | MIT | Development-time automated tests only |

Each distribution may include additional transitive dependencies. Their own
metadata and license files remain authoritative.

The installed `bcf-client` 0.8.5 wheel declares the PyPI classifier
`GNU General Public License v3 (GPLv3)`, while its source project is distributed
within the IfcOpenShell repository, whose root licensing and BCF source headers
identify LGPL terms. This project does not resolve that upstream metadata
conflict or redistribute the package. The normative Stage 3 BCF implementation
uses Python XML/ZIP facilities and the vendored official schemas instead.

## buildingSMART Sample IFC Files

The following files are unmodified public samples from the buildingSMART
International
[Sample-Test-Files repository](https://github.com/buildingSMART/Sample-Test-Files),
IFC 4 PCERT Sample Scene:

- `data/raw/Building-Architecture.ifc`
- `data/raw/Building-Structural.ifc`
- `data/raw/Building-Hvac.ifc`

Copyright buildingSMART International Ltd. Licensed under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
The project records each file's source URL and SHA-256 in
`data/processed/models.csv`.

The following files are unmodified public samples from the same repository,
IFC 4 ISO Spec Reference View 1.2, pinned at commit
[`cecf656112a54a0d8cdd8b06b9398bfea5163886`](https://github.com/buildingSMART/Sample-Test-Files/tree/cecf656112a54a0d8cdd8b06b9398bfea5163886/IFC%204.0.2.1%20%28IFC%204%29/ISO%20Spec%20-%20ReferenceView_V1.2):

- `projects/iso-reference-view/wall-with-opening-and-window.ifc`
  — SHA-256 `73b0e45d931d5dc13bfee5fdc7bd80f796526445458b2de74c4168d209097832`
- `projects/iso-reference-view/column-straight-rectangle-tessellation.ifc`
  — SHA-256 `58bb9b2cae96edf2c368de95f526650f3f282e4e7fc37c0065c501bdbeed00a1`
- `projects/iso-reference-view/basin-tessellation.ifc`
  — SHA-256 `7278769ec5ef35d388819d2f197519061c7f0f68dd43a733f333ddeb74578121`

Copyright buildingSMART International Ltd. Licensed under the
[Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
Each file's source URL and SHA-256 is also recorded in
`projects/iso-reference-view/project.toml`, where ingest verifies the hash on
every run and stops if a file has changed.

## buildingSMART BCF 3.0 Schemas

Unmodified BCF-XML 3.0 schema files under
`third_party/buildingsmart/bcf-xml/3.0/` originate from the
[buildingSMART BCF-XML `release_3_0` branch](https://github.com/buildingSMART/BCF-XML/tree/release_3_0).

Copyright buildingSMART International Ltd. Licensed under the
[Creative Commons Attribution-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nd/4.0/).
These files are retained byte-for-byte as the validation source of truth. They
must not be reformatted, normalized, or modified. Source revision and file
hashes are recorded alongside the vendored snapshot.

## buildingSMART IDS 1.0 Implementer Test Cases

Unmodified IDS implementer test cases under
`third_party/buildingsmart/ids/1.0/testcases/` originate from the
[buildingSMART IDS repository](https://github.com/buildingSMART/IDS), pinned at
commit
[`dba4549e57a3a98e725e086991e19800a76850b8`](https://github.com/buildingSMART/IDS/tree/dba4549e57a3a98e725e086991e19800a76850b8/Documentation/ImplementersDocumentation/TestCases).

Copyright buildingSMART International Ltd. Licensed under the
[Creative Commons Attribution-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nd/4.0/),
whose text is retained verbatim in
`third_party/buildingsmart/ids/1.0/LICENSE`.

Four of the ten test case directories are vendored — `attribute`,
`classification`, `partof` and `property` — as 199 `.ids`/`.ifc` pairs. They are
retained byte-for-byte as an independent conformance judge and must not be
reformatted, normalized, or modified. The pinned revision, what was taken, and
per-file SHA-256 values are recorded in
`third_party/buildingsmart/ids/1.0/SOURCE.md` and `SHA256SUMS`, which the test
suite verifies on every run.

## buildingSMART IDS Audit Tool

The test suite and continuous integration invoke
[`ids-tool`](https://github.com/buildingSMART/IDS-Audit-tool)
(`ids-tool.CommandLine` 1.0.124, package SHA-256
`f0405a163c3e23c1fcd67a6f1b5397c4f618e2338adecb1de76a95d89e5d71ec`) as an
external process to audit this project's IDS documents against the schema and
the standard's content rules.

Copyright buildingSMART International Ltd and contributors. Licensed under the
MIT License. The tool is installed from NuGet as a .NET global tool and is not
redistributed here; no part of its implementation is copied into this
repository.

## Speckle Power BI Connector and 3D Visual

The Control Tower report definition references the official
[`specklePowerBiVisual`](https://github.com/specklesystems/speckle-powerbi)
version 2026.6.0. The connector and compiled visual bundle remain external
Desktop prerequisites: no `.pqx`, `.pbiviz`, or expanded `CustomVisuals/**`
payload is redistributed by this repository.

The audited upstream release is `v2026.6.0` at commit
`3d6a9391b3b5576b0e49ef9e844763681695a299`. The signed installer and installed
visual hashes, build-run provenance, and the exact redistribution boundary are
recorded in
`third_party/speckle/powerbi-visual/2026.6.0/provenance.json`. The upstream
visual directory contains an Apache-2.0 `LICENSE`, retained verbatim beside the
provenance record, but no `NOTICE` file. No NOTICE is invented here.

Upstream licensing metadata is not fully consistent: the visual directory's
license file is Apache-2.0 while its `package.json` declares MIT. This project
does not resolve that difference and therefore requires users to import the
official installed visual through Power BI Desktop instead of redistributing
the bundle.

For the complete adoption boundary, including projects used only as design or
architecture references, see `docs/open_source_adoption.md`.
