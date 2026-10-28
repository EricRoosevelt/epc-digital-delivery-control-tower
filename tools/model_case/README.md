# Local model-case measurement

These are development measurement tools, not product dependencies or a benchmark
claim. Use one authorized, source-editable IFC model throughout the source export,
3D inspection, revision and comparison workflow. Never substitute a geometry demo
and a separate geometry-less fixture for that complete case.

## Privacy and isolation

- Use a separate loopback Doctor service, checks directory and project database.
  Coordinate its lifecycle and PID before sampling. Do not mix public demo traffic
  or another source tool's CPU work into a measurement window.
- Config, source identities, full reports, screenshots and raw logs belong outside
  the checkout. Both tools reject a raw evidence directory under this checkout.
- Browser requests to other origins are blocked, and the tool rejects an AI advice
  request. The product is exercised with local rule guidance only.
- Only deliberately de-identified counts, timings and memory summaries should be
  copied into public documentation. No actual filename, model identifier, GlobalId,
  hash, screenshot or private route is embedded in this tool's source.

## Browser upload and interaction, with server memory

Prepare a private JSON config. Replace every example value locally:

```json
{
  "base": "http://127.0.0.1:18876",
  "source": "<authorized-before-export.ifc>",
  "output_dir": "<outside-checkout-private-evidence>/before",
  "label": "before",
  "context": "<commit and dirty-code context>; cold service, no review cache; OS caches retained",
  "target_global_ids": ["<source-verified-change-instance>", "<second-instance>"],
  "save": {
    "project_name": "Local engineering case",
    "model_name": "Representative source model",
    "label": "Verified source export before"
  }
}
```

Install the repository's pinned QA dependencies and Chromium once. These are
development tools; normal application startup does not require Node.js:

```powershell
npm ci
npx playwright install chromium
python tools/model_case/measure_browser.py '<private-config.json>' --pid <server-pid>
```

This drives the actual file input, not an injected report. The GUI submits an
import job and polls its progress; `browser_post_request_ms` measures submission
only. Parsing, checking and tessellation happen in the worker before the final
report GET. Browser upload-to-ready includes that work, polling, geometry transfer,
JSON parsing and the real Three.js scene. The response probe reads the final
report GET as well as the legacy synchronous endpoint.

The test-only WebGL draw wrapper confirms actual triangle draws, not an empty
canvas. It records first triangle command submission and the next animation-frame
opportunity. It separately records completion of a real screenshot. Neither
animation-frame timing nor screenshot overhead is mislabelled as exact GPU
presentation time. Named rotate/zoom controls are sampled five times; intended
change instances must have real meshes and are selected, focused and isolated.
Screenshots must still be visually inspected by the reviewer.

The wrapper samples the specified server PID every 50 ms using the Windows
process API (or Linux `/proc`). It reports baseline RSS, sampled operation-local
peak/delta, ending RSS, private bytes and the OS lifetime peak separately. Upload
through browser geometry-ready and revision snapshot save have separate stage
peaks. A sampled peak can miss short spikes; the lifetime OS peak may predate the
measured operation. Neither is browser/GPU memory.

Browser JS heap comes from Chromium's `Performance.getMetrics`, with baseline,
geometry-ready and final values. It excludes native and GPU allocations. The
actual browser version, headless mode, viewport and renderer are recorded; do not
generalize a software-rendered measurement to a physical GPU or sustained FPS.

For the after export, use a new source payload on the same process and label it as
a warm-process / uncached-content run. To save in the same logical model, replace
the `save` config with:

```json
{
  "save": {
    "from_result": "<private-before-browser.json>",
    "label": "Verified source export after"
  }
}
```

The returned private `saved` metadata identifies the project/model/revisions for
the later exact comparison, manual record, brief and actual restart check. Keep
source-tool editing/export evidence and its real date alongside these current UI
observations. Reusing verified historical evidence is not a claim that the source
tool was operated during this measurement.

Continue the same saved model through manual records, exact comparison and a real
Markdown attachment, without another IFC import:

```powershell
node tools/model_case/continue.cjs http://127.0.0.1:18876 '<private-before-browser.json>' '<private-after-browser.json>' '<private-output>'
```

After the service is actually stopped and restarted against the same database,
repeat that command with `--restarted`. It checks existing manual records rather
than writing them again, restores real geometry and exact selected findings, and
verifies current/previous comparison and the latest-revision brief. Manual status
is explicitly a role exercise, not a named engineer's classification approval.
The helper's expected 2 passed / 94 remaining is the executed representative case,
not a generic rule; adapt those assertions before using a different case.
The default QA browser is Chromium. Set `channel` in the browser config or
`BROWSER_CHANNEL` for another installed Playwright browser channel; recorded
measurements identify the actual channel/version. The earlier case used Edge.

Conclusions must name the measured element, mesh, triangle and input-byte counts.
A larger file's metadata or a successful synthetic regression is not evidence of
interactive capacity at that larger scale.
