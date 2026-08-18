# buildingSMART IDS 1.0 implementer test cases

These files are vendored byte-for-byte from the official buildingSMART `IDS`
repository. They are isolated from the project's MIT-licensed source code and
remain covered by the upstream CC BY-ND 4.0 license in `LICENSE`.

- Repository: https://github.com/buildingSMART/IDS
- Branch used to resolve the revision: `development`
- Immutable revision: `dba4549e57a3a98e725e086991e19800a76850b8`
- Test case source directory: https://github.com/buildingSMART/IDS/tree/dba4549e57a3a98e725e086991e19800a76850b8/Documentation/ImplementersDocumentation/TestCases

The `development` branch is named rather than the `v1.0.0` tag because the tag
does not contain this directory: the test cases were added to the repository
after the standard was released. The revision above is therefore the pin, and
the branch name records only how it was resolved.

## What is vendored

Four of the ten test case directories, chosen because they are the facet kinds
this project's rule library either uses today or is about to: `attribute`,
`classification`, `partof`, and `property`. The remaining directories —
`entity`, `material`, `restriction`, `tolerance`, `ids`, and the two
documentation files — are deliberately not copied. Vendoring the whole suite
would quadruple what this repository carries under a NoDerivatives license for
coverage it cannot yet act on.

| Directory | Cases | `pass-` | `fail-` | `invalid-` |
|---|---|---|---|---|
| `testcases/attribute` | 56 | 30 | 15 | 11 |
| `testcases/classification` | 27 | 17 | 10 | 0 |
| `testcases/partof` | 34 | 17 | 16 | 1 |
| `testcases/property` | 82 | 44 | 32 | 6 |
| **Total** | **199** | **108** | **73** | **18** |

Each case is a pair: an `.ids` document and the minimal `.ifc` model it is to
be run against. The filename prefix states the outcome the standard expects,
which is what `tests/test_ids_conformance.py` asserts. `invalid-` marks a
document the standard considers invalid; the upstream case titles say what a
validator must do with one ("Invalid attribute names always fail", "Derived
attributes cannot be checked and always fail"), so this project reads the
prefix as *must not report a pass* rather than as a specific status.

## SHA-256

Per-file digests are recorded in `SHA256SUMS`, one line per file in
`sha256sum` format, sorted by path. There are 399 entries: 398 test case files
plus the upstream `LICENSE`. The manifest is checked on every test run by
`tests/test_ids_conformance.py`, which fails if any vendored byte has moved.

The manifest's own SHA-256 is
`948e80fef0432b0e70389e3a6e10d4b9a28ff761edf773ea02c59731aab2068a`.

Every vendored file was additionally verified against its upstream Git blob
SHA-1 at the pinned revision before being committed, which is a stronger check
than a re-hash of what was downloaded: it confirms the bytes are the ones the
upstream repository stores, not merely the ones an archive endpoint served.

The test case files and upstream license must not be reformatted, normalized,
or otherwise modified. The repository's `.gitattributes` disables text
normalization for this directory; without it, `* text=auto` would rewrite every
line ending on a Windows checkout and the digests above would not survive.
