# Phase 2 candidate demonstration

The current demonstration is generated from the **same source commit** as the
clean-install checks. Download the `candidate-<40-character-SHA>-<Runner-OS>`
artifact from that commit's GitHub Actions run. Its `capture/manifest.json`
records `source_sha`, browser and Playwright versions, input hashes, assertions,
and a SHA-256 hash for every media file. Check that `source_sha` equals the
commit you intend to evaluate. A successful recording has
`status: "candidate-captured"` and `source_tree_verified: true`.

Find the run in the [candidate branch's CI history](https://github.com/EricRoosevelt/epc-digital-delivery-control-tower/actions/workflows/ci.yml?query=branch%3Afeat%2Fdoctor-product-phase1),
then verify its head SHA before downloading. Artifacts are retained for **90
days**, and GitHub may require sign-in to download them. After expiry, regenerate
from the same public source SHA using the commands below; no existing project
database or private model is needed.

Videos and screenshots are artifact outputs, **not committed back into source**.
This avoids changing the source SHA merely to add its own recording. Earlier
October 13 videos are historical material and do not demonstrate this candidate's
project persistence or revision comparison.

## What the recording shows

The first two scenes use the unmodified buildingSMART PCERT sample, with its real
architecture, structure and HVAC geometry. Attribution remains visible in the
product and is recorded in the manifest. The remaining scenes use an original,
explicitly labelled **PUBLIC SYNTHETIC** editable model from
[`public-source.json`](../../../tools/phase2_demo/public-source.json).
The exporter independently generates two IFC4 revisions from that JSON source;
every demo object has real extruded geometry. This is a software demonstration,
not a Revit export or an engineering acceptance case.

| Scene | Demonstrated action |
|---|---|
| 01–02 | Load public sample, select/focus/isolate a real element, read local rule guidance |
| 03–04 | Import synthetic R1, save to a new project/model, record Ready for recheck while machine FAIL remains |
| 05–06 | Reopen saved R1, import R2, save into the existing model |
| 07–08 | Compare revisions; distinguish rule recheck passed, remaining, new, missing and not comparable |
| 09–10 | Reopen the exact R2 PASS object in 3D, download the real Markdown work brief |
| 11–13 | Reopen the same saved finding in Chinese and at a 390 px mobile viewport |

The class change affects more than one rule, so comparison record counts are not
object counts. The assertions verify all five outcomes specifically for PV-001.
Removed objects are not counted as repaired. The manual follow-up status does not
change machine check results. No AI provider key is used: the product demonstrates
**local rule guidance**, without a live provider response or an external upload.

## Reproduce from an exact commit

Install the Python dependencies using the repository's clean-install instructions,
and use Node.js 20 or later. From the checked-out candidate commit:

```sh
npm ci
npx playwright install --with-deps chromium
npm run capture:phase2 -- --source-sha <full-40-character-SHA> --data-dir <new-external-data-directory> --output-dir <new-external-artifact-directory>/capture --python <python-executable> --browser chromium --port 0
```

On Windows, omit `--with-deps`; `--browser msedge` can use installed Edge after
Playwright's video encoder has been installed. Linux requires CJK fonts for the
Chinese scenes; CI installs `fonts-noto-cjk`. The default browser is Playwright's
pinned Chromium. `--language zh` records the main workflow in Chinese instead of
English. Both modes include Chinese saved-revision and mobile screenshots.

Both supplied directories must be fresh, separate, and outside the checkout.
The tool refuses reused directories, starts its own loopback server on an
automatically selected port (`--port 0`), verifies an empty project library, and
stops only that server when finished. It never uses an existing preview service
or database. Raw server logs stay in the data directory, outside the public
artifact. It removes the provider API key from the server environment and blocks
external browser requests. The final run rejects changes across the entire Git
worktree (including staged changes and all non-ignored untracked files), hashes
every tracked file using a NUL-delimited Git file list, and repeats the clean-source
check before writing its manifest. CI tests this guard against real changes in
temporary Git repositories.

The output contains `demo.webm`, `captions.vtt`, 13 PNG screenshots, `brief.md`,
the public JSON/IFC fixtures and `manifest.json`. Captions are approximate chapter
positions; state assertions use real UI readiness. The video has deliberate
reading pauses, not a benchmark timing claim. There is no audio narration.
The manifest format is documented in [`manifest.schema.json`](manifest.schema.json).

For script development only, `--rehearsal --hold-ms 0` allows uncommitted changes,
omits the video, and writes `status: "rehearsal-not-candidate"`. A rehearsal is
never evidence for a frozen candidate. Preserve failed runs separately rather
than reusing their directories. The tool writes a failure screenshot and compact
failure record if a step fails; it does not produce a successful manifest.

To verify downloaded files, compute SHA-256 for each relative `media[].path`
and compare it with `media[].sha256`. The manifest itself has no self-hash. Source
file hashes use repository-relative paths; local account names, raw server paths
and private case identifiers are not part of this artifact.
