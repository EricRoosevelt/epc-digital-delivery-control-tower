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

Six of the nine test case directories — one per IDS facet kind. The three left
behind are `restriction` and `tolerance`, which test value semantics rather
than a facet, and `ids`, which tests document-level metadata; the two
documentation files are also not copied. Under a NoDerivatives license the rule
applied was to take what this project's checker actually claims to evaluate and
no more.

The six here are exactly the six facet kinds `IdsChecker.capabilities` declares.
That is the point of taking all of them: a capability claim with no external
evidence behind it is an assertion, and this repository already had one — the
capability tuple used to list the three facets the rule library happened to
use, not the ones the checker can evaluate.

| Directory | Cases | `pass-` | `fail-` | `invalid-` |
|---|---|---|---|---|
| `attribute/` | 56 | 30 | 15 | 11 |
| `classification/` | 27 | 17 | 10 | 0 |
| `entity/` | 33 | 18 | 9 | 6 |
| `material/` | 29 | 23 | 6 | 0 |
| `partof/` | 34 | 17 | 16 | 1 |
| `property/` | 82 | 44 | 32 | 6 |
| **Total** | **261** | **149** | **88** | **24** |

Each case is a pair: an `.ids` document and the minimal `.ifc` model it is to
be run against. The filename prefix states the outcome the standard expects,
which is what `tests/test_ids_conformance.py` asserts. `invalid-` marks a
document the standard considers invalid; the upstream case titles say what a
validator must do with one ("Invalid attribute names always fail", "Derived
attributes cannot be checked and always fail"), so this project reads the
prefix as *must not report a pass* rather than as a specific status.

## SHA-256

Per-file digests are recorded in `SHA256SUMS`, one line per file in
`sha256sum` format, sorted by path. There are 523 entries: 522 test case files
plus the upstream `LICENSE`. The manifest is checked on every test run by
`tests/test_ids_conformance.py`, which fails if any vendored byte has moved.

The manifest's own SHA-256 is
`00d450bb1de238a63227f19101b81b1eb1467fa7cd1f1223ecddb0947958d729`.

Every vendored file was additionally verified against its upstream Git blob
SHA-1 at the pinned revision before being committed, which is a stronger check
than a re-hash of what was downloaded: it confirms the bytes are the ones the
upstream repository stores, not merely the ones an archive endpoint served.

## Why the facet directories sit directly here

Upstream nests them one level deeper, under `TestCases/`. That level is
dropped, and the reason is not taste: two of the vendored filenames are 127
characters long, and with the extra segment the full path on a GitHub
`windows-latest` runner came to 261 characters. `git checkout` failed with
*Filename too long* and the build never got as far as running anything.

Renaming the files was not an option — a NoDerivatives license means the
bytes and the names are the upstream ones — and dropping the two long cases
would have made the corpus a selection rather than a facet directory. So the
path above them got shorter instead. `tests/test_ids_conformance.py` asserts
the remaining margin, so the next widening of this corpus finds out on a
developer's machine rather than in CI.

The test case files and upstream license must not be reformatted, normalized,
or otherwise modified. The repository's `.gitattributes` disables text
normalization for this directory; without it, `* text=auto` would rewrite every
line ending on a Windows checkout and the digests above would not survive.
