# Evidence — what the IfcOpenShell 0.8.5 wheel contains, and what its metadata says (2026-10-09)

This records what was inspected about the IfcOpenShell 0.8.5 binary wheel this
project installs through `requirements.txt`, so that the dependency entries in
[`open_source_adoption.md`](../../open_source_adoption.md) and
[`THIRD_PARTY_NOTICES.md`](../../../THIRD_PARTY_NOTICES.md) say what is known
rather than what the metadata alone implies.

## What this is, and what it is not

- **A factual record, not a legal opinion.** Nothing here concludes what
  obligations do or do not apply to this project or to anyone who redistributes
  it. Those questions are listed under [Open questions](#open-questions) and
  are left open.
- **One wheel was inspected byte for byte**: the Windows x86-64 wheel for Python
  3.14. Other platform wheels of the same release are listed by name and
  published digest only; their contents were not inspected.
- **No dependency, requirement or code changes.** The project keeps
  `ifcopenshell==0.8.5` and keeps using the library's default geometry library
  (OpenCASCADE). Switching to the CGAL-based geometry library was measured
  during 3D research and **not adopted** (product decision, 2026-10-09).

## Verified: the inspected wheel

| Fact | Value |
|---|---|
| File | `ifcopenshell-0.8.5-py314-none-win_amd64.whl` |
| Platform | Windows x86-64, CPython 3.14 |
| SHA-256 | `13a5992dc07e69c0c78df5479e1ff9635e6ce9fa70c841d9ce2931e8481eabb9` |
| Size | 24,542,242 bytes |
| Matches PyPI | Yes: the digest published by PyPI's JSON API for this file name (uploaded 2026-04-13) equals the digest of the file pip cached when installing |
| Entries in the archive | 584 |
| `LICENSE`, `COPYING`, `NOTICE` or similar files | **None** — no archive entry matches `licen`, `copying` or `notice` (case-insensitive) |
| `METADATA` licence fields | No `License:` field, no `License-Expression:` field; one classifier: `License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)` |
| PyPI JSON `info.license` / `info.license_expression` | `null` / `null` |
| `WHEEL` tag | `Tag: py3-none-any`, `Root-Is-Purelib: true` — the file name carries a platform tag, the metadata inside does not |
| Native extension | `ifcopenshell/_ifcopenshell_wrapper.cp314-win_amd64.pyd`, 56,004,608 bytes, SHA-256 `95a380099c4f8dc04df891c510ba1cf4b64db90d81b673192b97399430f613c0` |
| Installed copy | The `.pyd` in this project's `.venv` has the same SHA-256, and the installed `RECORD` lists that digest |
| Other native files | None: no separate `.dll` ships beside the extension |

Byte strings found inside that extension. A string shows that the name is
present in the binary; it does not by itself show which code paths execute.

| String | Occurrences | Upstream component it names |
|---|---:|---|
| `Polyhedron_3` | 14 | CGAL Polyhedron package |
| `Polygon_mesh_processing` | 12 | CGAL Polygon Mesh Processing package |
| `Nef_polyhedron_3` | 20 | CGAL Nef_3 package |
| `Epick` | 639 | CGAL kernel (exact predicates, inexact constructions) |
| `Epeck` | 1,212 | CGAL kernel (exact predicates, exact constructions) |
| `Open CASCADE` | 4 | Open CASCADE Technology |
| `7.8.1` | present | consistent with the OCCT version the build scripts pin (below) |

No CGAL, GMP/MPIR or MPFR version string was found in the binary.

## Verified: upstream source and build records

All references are to the public
[IfcOpenShell repository](https://github.com/IfcOpenShell/IfcOpenShell).

- The release tag `ifcopenshell-python-0.8.5` points at commit `16723d11cab9`,
  published 2026-04-13; its `VERSION` file reads `0.8.5`.
- At that tag, `src/ifcopenshell-python/Makefile` builds the PyPI wheel by:
  1. downloading a prebuilt native module
     `ifcopenshell-python-<py>-v0.8.5-1c5b825-<platform>.zip` from the
     `ifcopenshell-builds` S3 bucket (`BUILD_COMMIT := 1c5b825`);
  2. copying that module, `README.md` and `pyproject.toml` into a pure-Python
     package;
  3. building a wheel and renaming it with the platform tag.

  No step copies `COPYING`, `COPYING.LESSER` or third-party licence texts. This
  explains both the absent licence files and the `py3-none-any` tag above.
- At build commit `1c5b825d8ef05ab9d14a15dac12e9eae2f5a37c2` (2026-02-27), the
  dependency scripts pin:

  | Script | CGAL | OCCT | Arbitrary-precision libraries |
  |---|---|---|---|
  | `win/build-deps.cmd` (Windows) | v5.5.5 | 7.8.1 | MPIR (GMP fork), MPFR |
  | `nix/build-all.py` (Linux, macOS) | v5.6.3 | 7.8.1 | GMP 6.3.0, MPFR 3.1.6 |

- IfcOpenShell's own source is licensed LGPL-3.0-or-later. The repository
  root carries `COPYING` (GPL-3.0 text) and `COPYING.LESSER` (LGPL-3.0 text).
  The [IfcOpenShell documentation](https://docs.ifcopenshell.org/ifcopenshell.html)
  describes the library as LGPL-3.0-or-later. It does not discuss the licences
  of the geometry libraries compiled into binary builds.
- The CGAL headers IfcOpenShell's CGAL geometry kernel includes
  (`src/ifcgeom/kernels/cgal/`, tag `bonsai-0.8.5`) carry these
  `SPDX-License-Identifier` lines in CGAL v5.5.5 and v5.6.3; spot checks gave
  the same results for both versions:

  | CGAL package | Example header | SPDX identifier |
  |---|---|---|
  | Kernel_23 | `Exact_predicates_inexact_constructions_kernel.h` | `LGPL-3.0-or-later OR LicenseRef-Commercial` |
  | Polygon | `Polygon_2.h` | `LGPL-3.0-or-later OR LicenseRef-Commercial` |
  | HalfedgeDS | `HalfedgeDS_default.h` | `LGPL-3.0-or-later OR LicenseRef-Commercial` |
  | Number_types | `Gmpq.h` | `LGPL-3.0-or-later OR LicenseRef-Commercial` |
  | Polyhedron | `Polyhedron_3.h` | `GPL-3.0-or-later OR LicenseRef-Commercial` |
  | Polygon_mesh_processing | `triangulate_faces.h`, `self_intersections.h` | `GPL-3.0-or-later OR LicenseRef-Commercial` |
  | Nef_3 | `Nef_polyhedron_3.h` | `GPL-3.0-or-later OR LicenseRef-Commercial` |
  | Boolean_set_operations_2, Arrangement_on_surface_2, Minkowski_sum_2/3, Convex_decomposition_3, Spatial_searching, Box_intersection_d, Straight_skeleton_2, Triangulation_2 | one header each | `GPL-3.0-or-later OR LicenseRef-Commercial` |

- The [CGAL licensing page](https://www.cgal.org/license.html) states that the
  kernel and support libraries are broadly LGPL, most geometric algorithms and
  data structures are GPL, exceptions exist in both directions, and commercial
  licences are sold by GeometryFactory. That page describes CGAL as a whole. It
  cannot by itself establish which packages a particular binary contains.
  Neither it nor the IfcOpenShell page above determines the complete licensing
  boundary of this specific 0.8.5 wheel.

## Not verified

- **Exact versions in the binary.** That the S3 module for `1c5b825` was built
  with exactly the pinned CGAL, MPIR/GMP and MPFR versions is inferred from the
  build scripts. Only the OCCT `7.8.1` string was observed in the binary.
- **Which CGAL object code is linked.** Type names in a binary indicate that
  templates from those packages were instantiated. This record is not a full
  audit of linked object code.
- **Other platform wheels.** The Linux wheel continuous integration installs
  (`ifcopenshell-0.8.5-py314-none-manylinux_2_31_x86_64.whl`, PyPI SHA-256
  `15b488347efce0d7…`) and the macOS wheels were not opened. Given the
  packaging recipe they are expected to be built the same way, but that is
  unverified.
- **IfcTester and `bcf-client`.** Their wheels were not re-inspected for this
  record.

## Open questions

These are deliberately left open. They are for the user, and for legal advice
if it is sought; this record does not answer them.

1. Which licence terms govern the 0.8.5 binary wheel as distributed on PyPI,
   given that its metadata names only LGPL-3.0-or-later while the binary
   contains code from packages whose source files are GPL-3.0-or-later (or
   commercially licensed)?
2. What, if anything, follows for a project that distributes only its own
   source and lets each user obtain the wheel from PyPI with pip?
3. What would follow if anyone later distributed a bundle that includes the
   wheel or its binary (an installer, a container image, an offline package):
   which notices, licence texts and source offers would that bundle need?
4. Does using a geometry library selection that executes those packages differ,
   for any of the above, from installing a binary that merely contains them?

## Distribution scope decision (product decision, 2026-10-09)

For the résumé release, the project distributes **source code only**.
Dependencies, including this wheel, are obtained by each user's own `pip
install` from PyPI. The project does **not** produce installers, container
images or offline packages that contain third-party binaries.

This is a scoping decision about what the project ships. It is not a
conclusion that source-only distribution carries no obligations, and not a
conclusion about what any bundle would require. Producing any bundle with
third-party binaries would need a new review against this record first.

## Reproduce

1. `pip cache dir` locates pip's cache. The wheel body is the cached HTTP
   response of 24,542,242 bytes under `http-v2/`. Alternatively, download
   `ifcopenshell-0.8.5-py314-none-win_amd64.whl` from PyPI into a scratch
   directory outside the repository.
2. Compare its SHA-256 with `https://pypi.org/pypi/ifcopenshell/0.8.5/json`.
3. Open it with Python's `zipfile`, then:
   - list the entries;
   - read `*.dist-info/METADATA` and `*.dist-info/WHEEL`;
   - hash the `.pyd`;
   - count the byte strings in the table above.
4. Read the upstream files named above at the stated tags and commits, through
   the GitHub contents API or a clone.
