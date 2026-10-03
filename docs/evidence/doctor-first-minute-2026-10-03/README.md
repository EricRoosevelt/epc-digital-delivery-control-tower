# BIM Doctor screenshots used by the root README

Six captures of the BIM Doctor local preview, three screens in each interface
language, taken for the "BIM Doctor today" section of the root
[`README.md`](../../../README.md). They are illustrations of what the interface
looks like. They are not acceptance evidence for the preview, and nothing
validates them: unlike [`../stage_3b/`](../stage_3b/README.md), no manifest or
test pins this directory.

| File | Route | Shows |
|---|---|---|
| `en-01-home.png`, `zh-01-home.png` | `#/` | The home screen: the two entries offered when the server starts without a workspace, and what it cannot do |
| `en-02-first-check-result.png`, `zh-02-first-check-result.png` | `#/fixture/member-evidence` | The first-check result of the simulated example: counts, then the items that need handling grouped by team |
| `en-03-one-item.png`, `zh-03-one-item.png` | `#/fixture/member-evidence/item/2/2/0` | One item: the conclusion, then what to do, who handles it and what a recheck must show |

The language is chosen with `?lang=en` or `?lang=zh` in front of the route.

## What is in the pixels

- **Public sample data only.** The example reads the two bundled buildingSMART
  PCERT sample models of the `pcert-sample` project (see *Data Source and
  Attribution* in the root README). No other model, workspace or run was open
  when the server was started, and the server offered no workspace entry.
- **The two languages are two wordings of the same screens.** The English
  screens are drawn from the English wording table and the Chinese from the
  Chinese one, so a sentence can differ in more than language. The item page's
  "what to do" is an example: in English it is the assessment record's own
  English text, not a translation of the Chinese sentence. The root README
  captions each set on its own screen.
- **The English wording has not been reviewed by a BIM domain specialist yet**
  (status line of
  [`docs/product/2026-10-03-doctor-english-vocabulary.md`](../../product/2026-10-03-doctor-english-vocabulary.md)).
  These captures show what the interface says, not that it has been checked.
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

Repository state: `872f76f8cad42269dcbfe5fe32375ecc7507ef4a` (`origin/main` at
the time), clean worktree.

```bash
python doctor/serve.py --port 8791
```

Each route was loaded once in headless Microsoft Edge 154.0.4258.53 on Windows
11, with a throw-away profile, an 880 px wide window, device scale factor 2 and
a virtual-time budget long enough for the page to render:

```text
msedge.exe --headless=new --disable-gpu --hide-scrollbars --no-first-run
  --window-size=880,<height> --force-device-scale-factor=2
  --virtual-time-budget=60000 --user-data-dir=<scratch>
  --screenshot=<file>.png "http://127.0.0.1:8791/?lang=<en|zh><route>"
```

Heights in CSS pixels, chosen so each image ends at the edge of a block rather
than in the middle of one; nothing is scrolled:

| Screen | `en` | `zh` |
|---|---|---|
| Home | 880 | 880 |
| First-check result | 1160 | 985 |
| One item | 1360 | 925 |

At this commit the server was also run from a clean environment holding only
`requirements.txt`, to confirm the visitor path in the README: the home page,
the language script and the first-check data all answered, and nothing was
written into the checkout (`git status` unchanged).

These are captured images, so they are not reproducible byte for byte: the
rendering depends on the browser and the system fonts. Their SHA-256 values
identify the files as committed:

```text
8177e79d02a6b77b135089736c9e4ca8dcb147744bf8d248f3ee2b9781c4662f  en-01-home.png
c0f295ba39ad0f26e4c2ea34777358a77a330dfbd6adb3fde004f5548531088c  en-02-first-check-result.png
64b1fdfacd9be0631107d3952dd1b28d3240e1b297f5e523cc851bb1da6a5e65  en-03-one-item.png
48fec5ec8aa96ba5aabd3969fe2605f4ea5e347080bfc7fb114dd328942dbd8e  zh-01-home.png
c3789641b237acc64b3369e627314858d41bdb9c640129765a48daba6ce48f67  zh-02-first-check-result.png
045305448be03e78b3b04a3b22baaae62ee28d43dc7e997d07309d18e9674f95  zh-03-one-item.png
```

## When they go stale

The captures show the interface as it was at the commit above. When the
preview's screens or wording change, replace the images and update the commit,
heights and hashes here; the README text that describes them does not quote any
number that is not also on the screen or pinned by a test.
