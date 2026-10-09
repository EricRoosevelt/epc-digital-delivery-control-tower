# BIM Doctor screenshots taken at 577620e (no longer shown by the root README)

Three captures of the BIM Doctor local preview, in the Chinese interface, taken at
`577620e` for the root [`README.md`](../../../README.md). **The root README no longer
shows them.** None of the three matches the current interface: the layout of the
home page and the item page was changed in PR #52, and the item-page capture shows
the sentence "no element in the scope is left unevaluated" under "what a recheck must
show", which BIM asked to change (W2) and which PR #50 changed. They are kept here as
a record of what the interface looked like at `577620e`, and nothing displays them.
The root README now shows a different capture, taken later and covered sentence by sentence:
[`../doctor-readme-item-page/`](../doctor-readme-item-page/README.md).

A screenshot goes back into the root README only after every visible sentence in it
has been reviewed (the subset of wording to review is in
[`docs/product/2026-10-09-bim-review-subset-public-route.md`](../../product/2026-10-09-bim-review-subset-public-route.md)).
They are illustrations of what the interface looked like. They are not acceptance
evidence for the preview, and nothing validates them: unlike
[`../stage_3b/`](../stage_3b/README.md), no manifest or test pins this directory.

| File | Route | Shows |
|---|---|---|
| `zh-01-home.png` | `#/` | The home screen: the two entries offered when the server starts without a workspace, and what it cannot do |
| `zh-02-first-check-result.png` | `#/fixture/member-evidence` | The first-check result of the simulated example: counts, then the items that need handling grouped by team |
| `zh-03-one-item.png` | `#/fixture/member-evidence/item/2/2/0` | One item: the conclusion, then what to do, who handles it and what a recheck must show |

## Withdrawn: the English screenshots

Three English captures were added in commit `505e2da` (PR #35) and **withdrawn
on 2026-10-04**. They are no longer in the tree, and no page in this repository
shows them.

| Withdrawn file | SHA-256 |
|---|---|
| `en-01-home.png` | `8177e79d02a6b77b135089736c9e4ca8dcb147744bf8d248f3ee2b9781c4662f` |
| `en-02-first-check-result.png` | `c0f295ba39ad0f26e4c2ea34777358a77a330dfbd6adb3fde004f5548531088c` |
| `en-03-one-item.png` | `64b1fdfacd9be0631107d3952dd1b28d3240e1b297f5e523cc851bb1da6a5e65` |

Why, as of the withdrawal: the root README is public display. The English
wording had not been reviewed by a BIM domain specialist (status line of
[`docs/product/2026-10-03-doctor-english-vocabulary.md`](../../product/2026-10-03-doctor-english-vocabulary.md)),
and one next-step sentence on the example's first-check path was known to differ
in meaning from the Chinese. A note beside a picture that the wording is
unreviewed does not make the picture safe to display.

Since then the English "what to do" and "what a recheck must show" sentences were
aligned with the Chinese ones (PR #40, merge commit `a5b89d0`). The wording as a
whole is still unreviewed by a BIM domain specialist, so the screenshots stay
withdrawn.

They are not restored by default. To show English screenshots again: have the
wording that would appear in them reviewed and any meaning error cleared, then
take new captures from the commit that carries the reviewed wording, and record
that commit, the routes, the heights and the hashes here. The old files are not
the ones to reuse: they show wording as it was at `872f76f`. They remain in Git
history for trace (`git show 505e2da:docs/evidence/doctor-first-minute-2026-10-03/en-01-home.png`),
and history is not rewritten.

## What is in the pixels

- **Public sample data only.** The example reads the two bundled buildingSMART
  PCERT sample models of the `pcert-sample` project (see *Data Source and
  Attribution* in the root README). No other model, workspace or run was open
  when the server was started, and the server offered no workspace entry.
- **Simulated content is marked on the screen.** Every page carries the
  "simulated example" strip. The team arrangement, accepted evidence methods
  and human determinations are the example's own settings. In the first-check
  example the check results beside them come from a real run of the shipped
  rules on the sample models. The page says which is which beside each
  conclusion.
- **No private material.** Nothing from the controlled real case, its models,
  its workspace or its results appears here, and no local path, account or
  address is visible. The PNG files carry no text or time metadata chunks.

## How they were made

Repository state: `577620e5532d837bc0d336b78418cdce05cf1e4f` (`origin/main` at
the time), clean worktree. The captures replace the earlier ones taken at
`872f76f8cad42269dcbfe5fe32375ecc7507ef4a`.

```bash
python doctor/serve.py --port 8792
```

Each route was loaded once in headless Microsoft Edge 154.0.4258.62 on Windows
11, with a throw-away profile, an 880 px wide window, device scale factor 2 and
a virtual-time budget long enough for the page to render:

```text
msedge.exe --headless=new --disable-gpu --hide-scrollbars --no-first-run
  --window-size=880,<height> --force-device-scale-factor=2
  --virtual-time-budget=60000 --user-data-dir=<scratch>
  --screenshot=<file>.png "http://127.0.0.1:8792/?lang=zh<route>"
```

Heights in CSS pixels, chosen so each image ends at the edge of a block rather
than in the middle of one; nothing is scrolled: home 880, first-check result
985, one item 910.

What changed against the `872f76f` captures:

| File | Against `872f76f` |
|---|---|
| `zh-01-home.png` | Re-captured; byte-identical. Not replaced. |
| `zh-02-first-check-result.png` | Re-captured; byte-identical. Not replaced. The cards below the part shown were folded in the meantime (`d2f81d6`); that is below the crop. |
| `zh-03-one-item.png` | Replaced. The fold under "what to do" is now labelled as the record's own English words, for tracing and not as an instruction (`295da77`), and the value column of the definition tables has more room (`1cc76b8`). The height went from 925 to 910: at 925 the image ran 9 CSS px into the next block. |

The one-item capture was taken twice and the two files were identical.

At `577620e` the server was also run from a clean Python 3.14.7 environment
holding only `requirements.txt`, to confirm the visitor path in the README: the
home page, the language script, the list of runs and the first-check data all
answered, and nothing was written into the checkout (`git status` showed only
the replaced screenshot).

These are captured images, so they are not reproducible byte for byte: the
rendering depends on the browser and the system fonts. Their SHA-256 values
identify the files as committed:

```text
48fec5ec8aa96ba5aabd3969fe2605f4ea5e347080bfc7fb114dd328942dbd8e  zh-01-home.png
c3789641b237acc64b3369e627314858d41bdb9c640129765a48daba6ce48f67  zh-02-first-check-result.png
5c5f316374db094ec0f9e77b9606c68cd99a017e4aa21c2327560974d62dfc1b  zh-03-one-item.png
```

## When they go stale

The captures show the interface as it was at the commit above. When the
preview's screens or wording change, replace the images and update the commit,
heights and hashes here; the README text that describes them does not quote any
number that is not also on the screen or pinned by a test.
