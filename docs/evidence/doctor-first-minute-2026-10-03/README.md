# BIM Doctor screenshots used by the root README

Three captures of the BIM Doctor local preview, taken for the "first minute"
section of the root [`README.md`](../../../README.md). They are illustrations of
what the interface looks like. They are not acceptance evidence for the
preview, and nothing validates them: unlike
[`../stage_3b/`](../stage_3b/README.md), no manifest or test pins this
directory.

| File | Route | Shows |
|---|---|---|
| `01-doctor-home.png` | `#/` | The home screen: the two entries offered when the server starts without a workspace, and what it cannot do |
| `02-first-check-result.png` | `#/fixture/member-evidence` | The first-check result of the simulated example: counts, then the items that need handling grouped by team |
| `03-one-item.png` | `#/fixture/member-evidence/item/2/2/0` | One item: the conclusion, which element it is, what to do, who handles it and what a recheck must show |

## What is in the pixels

- **Public sample data only.** The example reads the two bundled buildingSMART
  PCERT sample models of the `pcert-sample` project (see *Data Source and
  Attribution* in the root README). No other model, workspace or run was open
  when the server was started, and the server offered no workspace entry.
- **The interface is Chinese.** The preview has no English interface. The root
  README captions give the English meaning of the words a visitor needs.
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

Repository state: `cd73f2c9994a65e782d6bdfb510db6043125f323` (`origin/main` at
the time), clean worktree.

```bash
python doctor/serve.py --port 8791
```

Each route was loaded once in headless Microsoft Edge 154.0.4258.53 on Windows
11, with a throw-away profile, a 880 px wide window, device scale factor 2 and
a virtual-time budget long enough for the page to render:

```text
msedge.exe --headless=new --disable-gpu --hide-scrollbars --no-first-run
  --window-size=880,<height> --force-device-scale-factor=2
  --virtual-time-budget=60000 --user-data-dir=<scratch>
  --screenshot=<file>.png "http://127.0.0.1:8791/<route>"
```

Heights were 760, 950 and 1270 CSS pixels; each image is cut at the window
edge, not scrolled. The server was run from a clean `requirements.txt`
environment as well, to confirm the visitor path in the README, and wrote
nothing into the checkout (`git status` stayed empty).

These are captured images, so they are not reproducible byte for byte: the
rendering depends on the browser and the system fonts. Their SHA-256 values
identify the files as committed:

```text
0daf963150ed18b283d0ecee89bd68295361e1e37609271bf12c089004c6ba02  01-doctor-home.png
6981428fa007edffb645589ddc4381390df98ff5e656b891cf8bcf656d24642d  02-first-check-result.png
4750f70035dabe36eae205a85c75efd9c7dcee85c48b4847ced1cdf53c140416  03-one-item.png
```

## When they go stale

The captures show the interface as it was at the commit above. When the
preview's screens or wording change, replace the images and update the commit
and hashes here; the README text that describes them does not quote any number
that is not also on the screen or pinned by a test.
