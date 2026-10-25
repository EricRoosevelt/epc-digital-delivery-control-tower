// Real local IFC UI measurement. Config and every raw output stay outside checkout.
// npm ci
// npx playwright install chromium
// node tools/model_case/browser.cjs private-config.json
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const { performance } = require("node:perf_hooks");
const { chromium } = require("playwright");

const percentile = (values, p) => [...values].sort((a, b) => a - b)[Math.min(values.length - 1, Math.ceil(values.length * p) - 1)];
const stats = values => ({ samples_ms: values, median_ms: percentile(values, .5), p95_ms: percentile(values, .95), max_ms: Math.max(...values) });

async function main() {
  const configPath = path.resolve(process.argv[2]);
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  assert.ok(["127.0.0.1", "localhost", "[::1]"].includes(new URL(config.base).hostname), "Only loopback case services are allowed");
  const root = path.resolve(__dirname, "../..");
  fs.mkdirSync(config.output_dir, { recursive: true });
  const output = fs.realpathSync(config.output_dir);
  assert.ok(output.toLowerCase() !== root.toLowerCase() && !output.toLowerCase().startsWith(root.toLowerCase() + path.sep), "Raw evidence must be outside checkout");
  assert.match(config.label, /^[a-zA-Z0-9_-]+$/);
  assert.ok(config.context, "Record the code revision / dirty-context and exploratory versus final run");
  const label = config.label;
  const source = path.resolve(config.source);
  const pageErrors = [];
  const externalRequests = [];
  const consoleMessages = [];
  let report = null;
  let geometry = null;
  let postDuration = null;
  let geometryDuration = null;
  let saved = null;
  const phases = {};
  const channel = config.channel || process.env.BROWSER_CHANNEL || "chromium";
  const browser = await chromium.launch({ headless: true, ...(channel === "chromium" ? {} : { channel }) });
  const page = await browser.newPage({ viewport: config.viewport || { width: 1440, height: 1000 } });
  await page.route("**/*", route => {
    const url = new URL(route.request().url());
    if (["data:", "blob:"].includes(url.protocol) || url.origin === new URL(config.base).origin) return route.continue();
    externalRequests.push(url.origin); return route.abort();
  });
  page.on("pageerror", error => pageErrors.push(error.message));
  page.on("console", message => { if (["error", "warning"].includes(message.type())) consoleMessages.push({ type: message.type(), text: message.text() }); });
  if (config.diagnostics) {
    await page.route("**/review.js", async route => {
      const response = await route.fetch();
      const body = (await response.text()).replace('if (error.name === "AbortError") throw error;', 'console.error("MODEL_CASE_GEOMETRY_ERROR", error.name, error.message, error.stack); if (error.name === "AbortError") throw error;');
      await route.fulfill({ response, body });
    });
  }
  page.on("request", request => {
    if (new URL(request.url()).pathname === "/api/review/advice") {
      assert.notEqual(request.postDataJSON()?.use_ai, true, "Private case must not request external AI advice");
    }
  });
  await page.addInitScript(() => {
    const probe = window.__modelCaseProbe = {
      firstTriangleSubmission: null, firstTriangleFrame: null, uploadStart: null,
      triangleDrawCalls: 0, longTasks: [], action: null, gpu: null, jsonFailures: [], contextFailures: [],
    };
    try { new PerformanceObserver(list => { for (const item of list.getEntries()) probe.longTasks.push({ at: item.startTime, duration: item.duration }); }).observe({ type: "longtask", buffered: true }); } catch {}
    const original = HTMLCanvasElement.prototype.getContext;
    // Observe the product's own single JSON parse. Reading huge bodies through
    // the inspector cache can evict them; cloning/re-parsing would distort heap.
    const originalJSON = Response.prototype.json;
    Response.prototype.json = function () {
      const pathname = this.url ? new URL(this.url).pathname : "";
      return originalJSON.call(this).then(body => {
        if (["/api/review/models", "/api/review/report"].includes(pathname) && body.elements) probe.report = body;
        if (pathname === "/api/review/geometry" && body.meshes) {
          probe.geometry = {
            meshes: body.meshes.map(mesh => ({ element_key: mesh.element_key })),
            triangles: body.meshes.reduce((n, mesh) => n + mesh.indices.length / 3, 0),
            vertices: body.meshes.reduce((n, mesh) => n + mesh.positions.length / 3, 0),
          };
        }
        return body;
      }).catch(error => { probe.jsonFailures.push({ path: pathname, name: error.name, message: error.message }); throw error; });
    };
    document.addEventListener("webglcontextcreationerror", event => probe.contextFailures.push({ event: "creation", message: event.statusMessage }), true);
    HTMLCanvasElement.prototype.getContext = function (...args) {
      const context = original.apply(this, args);
      if (!context && ["webgl", "webgl2"].includes(args[0])) probe.contextFailures.push({ event: "null-context", requested: args[0] });
      if (context && ["webgl", "webgl2"].includes(args[0]) && !context.__caseWrapped) {
        context.__caseWrapped = true;
        const extension = context.getExtension("WEBGL_debug_renderer_info");
        probe.gpu = extension ? context.getParameter(extension.UNMASKED_RENDERER_WEBGL) : context.getParameter(context.RENDERER);
        for (const method of ["drawElements", "drawArrays"]) {
          const draw = context[method];
          context[method] = function (...values) {
            if (values[0] === context.TRIANGLES && values[method === "drawElements" ? 1 : 2] > 0) {
              probe.triangleDrawCalls++;
              if (probe.firstTriangleSubmission === null) {
                probe.firstTriangleSubmission = performance.now();
                requestAnimationFrame(() => { probe.firstTriangleFrame = performance.now(); });
              }
            }
            return draw.apply(this, values);
          };
        }
      }
      return context;
    };
    document.addEventListener("click", () => {
      if (!probe.action || probe.action.started !== null) return;
      const action = probe.action;
      action.started = performance.now();
      action.drawsBefore = probe.triangleDrawCalls;
      requestAnimationFrame(() => { action.frame = performance.now(); action.drawsAfter = probe.triangleDrawCalls; });
    }, true);
  });
  const screenshot = async name => {
    const filename = path.join(output, `${label}-${name}.png`);
    await page.screenshot({ path: filename });
    return filename;
  };
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Performance.enable");
  const heap = async () => {
    const response = await cdp.send("Performance.getMetrics");
    const metrics = Object.fromEntries(response.metrics.map(m => [m.name, m.value]));
    return { used_bytes: metrics.JSHeapUsedSize, total_bytes: metrics.JSHeapTotalSize, documents: metrics.Documents, nodes: metrics.Nodes };
  };
  async function action(name, locator, times = 5) {
    const values = [];
    for (let i = 0; i < times; i++) {
      await page.evaluate(name => { window.__modelCaseProbe.action = { name, started: null, frame: null }; }, name);
      await locator.click();
      await page.waitForFunction(() => window.__modelCaseProbe.action?.frame !== null);
      const observation = await page.evaluate(() => window.__modelCaseProbe.action);
      assert.ok(observation.started !== null && observation.drawsAfter > observation.drawsBefore, `${name} must actually draw the model`);
      values.push(observation.frame - observation.started);
    }
    return stats(values);
  }
  try {
    await page.goto(`${config.base}/review.html?lang=en`);
    await page.locator("#review-file").waitFor({ state: "attached" });
    const heapBaseline = await heap();
    const wallStart = performance.now();
    phases.upload_start_epoch_ms = Date.now();
    await page.evaluate(() => { window.__modelCaseProbe.uploadStart = performance.now(); });
    await page.locator("#review-file").setInputFiles(source);
    await Promise.race([
      page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor({ timeout: 600000 }),
      page.locator(".review-status.has-error").waitFor({ timeout: 600000 }).then(async () => { throw new Error(await page.locator(".review-status").innerText()); }),
    ]);
    await page.waitForFunction(() => window.__modelCaseProbe.firstTriangleFrame !== null, null, { timeout: 60000 });
    const uiReadyWall = performance.now() - wallStart;
    phases.geometry_ready_epoch_ms = Date.now();
    const initialScreenshot = await screenshot("overview");
    const firstScreenshotWall = performance.now() - wallStart;
    const browserProbe = await page.evaluate(() => window.__modelCaseProbe);
    report = browserProbe.report; geometry = browserProbe.geometry;
    assert.ok(report && geometry?.meshes.length > 0, "Same case must contain real triangle geometry");
    const resources = await page.evaluate(() => performance.getEntriesByType("resource").filter(entry => ["/api/review/models", "/api/review/imports", "/api/review/report", "/api/review/geometry"].includes(new URL(entry.name).pathname)).map(entry => ({ path: new URL(entry.name).pathname, operation: new URL(entry.name).searchParams.has("filename") ? "submission" : "read", duration: entry.duration, bytes: entry.encodedBodySize })));
    postDuration = resources.find(entry => entry.operation === "submission")?.duration;
    geometryDuration = resources.find(entry => entry.path.endsWith("/geometry"))?.duration;
    const heapReady = await heap();
    const actions = {};
    actions.rotate_button_to_next_frame = await action("rotate", page.getByRole("button", { name: "Rotate right", exact: true }));
    actions.zoom_button_to_next_frame = await action("zoom", page.getByRole("button", { name: "Zoom in", exact: true }));
    await page.getByRole("button", { name: "Reset view", exact: true }).click();
    const targets = [];
    for (const guid of config.target_global_ids || []) {
      const element = report.elements.find(e => e.global_id === guid);
      assert.ok(element, "The intended engineering-change element must exist");
      assert.ok(geometry.meshes.some(m => m.element_key === element.element_key), "The changed element must have actual geometry");
      const finding = report.findings.find(f => f.element_key === element.element_key && f.rule_id === "PV-001");
      assert.ok(finding);
      await page.locator("#review-status-filter").selectOption("");
      await page.locator("#review-search").fill(guid);
      const row = page.locator(`[data-finding="${finding.finding_id}"]`);
      const selection = await action("select-finding", row, 1);
      assert.equal(new URL(page.url()).searchParams.get("finding"), finding.finding_id);
      assert.equal(await page.locator(".review-evidence .review-verdict").innerText(), finding.status);
      const focus = await action("focus", page.getByRole("button", { name: "Focus element", exact: true }), 1);
      const targetShot = await screenshot(`target-${targets.length + 1}-focused`);
      const isolate = await action("isolate", page.getByRole("button", { name: "Isolate element", exact: true }), 1);
      assert.match(await page.locator(".review-view-footer").innerText(), /Visible elements: 1/);
      const isolatedShot = await screenshot(`target-${targets.length + 1}-isolated`);
      await page.getByRole("button", { name: "Reset view", exact: true }).click();
      targets.push({ global_id: guid, element_key: element.element_key, finding_id: finding.finding_id, status: finding.status, actual: finding.actual, selection_to_frame: selection, focus_to_frame: focus, isolation_to_frame: isolate, target_screenshot: targetShot, isolated_screenshot: isolatedShot });
    }
    assert.ok(targets.length, "Choose at least one source-verified change element");
    if (config.save) {
      phases.save_start_epoch_ms = Date.now();
      const destination = { ...config.save };
      if (destination.from_result) {
        const prior = JSON.parse(fs.readFileSync(destination.from_result, "utf8"));
        destination.project_id = prior.saved.project_id; destination.model_id = prior.saved.model_id;
      }
      await page.locator(".project-review-context").getByRole("button", { name: "Save to project", exact: true }).click();
      if (destination.project_id) await page.locator("#save-project").selectOption(destination.project_id);
      else { await page.locator("#save-project").selectOption("__new__"); await page.locator("#save-project-name").fill(destination.project_name || "Local engineering model case"); }
      if (destination.model_id) {
        await page.waitForFunction(id => [...document.querySelector("#save-model").options].some(o => o.value === id), destination.model_id);
        await page.locator("#save-model").selectOption(destination.model_id);
      } else await page.locator("#save-model-name").fill(destination.model_name || "Representative source model");
      await page.locator("#save-revision-label").fill(destination.label || label);
      await page.getByRole("button", { name: "Save model revision", exact: true }).click();
      await page.locator(".project-context-status").filter({ hasText: "Saved model revision" }).waitFor({ timeout: 600000 });
      const params = new URL(page.url()).searchParams;
      saved = { project_id: params.get("project"), model_id: params.get("model"), revision_id: params.get("revision") };
      phases.save_end_epoch_ms = Date.now();
      await screenshot("saved-revision");
    }
    const finalHeap = await heap();
    const finalProbe = await page.evaluate(() => ({ longTasks: window.__modelCaseProbe.longTasks }));
    assert.deepEqual(pageErrors, []); assert.deepEqual(externalRequests, []);
    const result = {
      schema_version: 1, measured_at_utc: new Date().toISOString(), context: config.context, label,
      browser: { version: browser.version(), channel, headless: true, viewport: config.viewport || { width: 1440, height: 1000 }, renderer: browserProbe.gpu },
      source_path: source, source_sha256: crypto.createHash("sha256").update(fs.readFileSync(source)).digest("hex"), review_id: report.review_id,
      counts: { ifc_bytes: fs.statSync(source).size, elements: report.elements.length, findings: report.findings.length, meshes: geometry.meshes.length, triangles: geometry.triangles, vertices: geometry.vertices, geometry_json_bytes: resources.find(entry => entry.path.endsWith("/geometry"))?.bytes },
      timing: { browser_post_request_ms: postDuration, browser_geometry_request_ms: geometryDuration, upload_to_ui_ready_wall_ms: uiReadyWall, upload_to_first_triangle_submission_ms: browserProbe.firstTriangleSubmission - browserProbe.uploadStart, upload_to_next_frame_after_triangle_ms: browserProbe.firstTriangleFrame - browserProbe.uploadStart, upload_to_first_screenshot_complete_ms: firstScreenshotWall },
      phases, actions, targets, saved, js_heap: { baseline: heapBaseline, geometry_ready: heapReady, final: finalHeap }, long_tasks: finalProbe.longTasks, console_messages: consoleMessages,
      screenshots: { overview: initialScreenshot }, page_errors: pageErrors, blocked_external_requests: externalRequests,
      scope: "Headless real Chromium; test-only draw wrappers and requestAnimationFrame timing. Frame timing is an animation-frame opportunity after synchronous UI handling, not GPU presentation or a sustained FPS claim. JS heap excludes browser native/GPU memory. Upload includes real server tessellation; do not call a cached repeat cold."
    };
    fs.writeFileSync(path.join(output, `${label}-browser.json`), JSON.stringify(result, null, 2));
    fs.writeFileSync(path.join(output, `${label}-report.json`), JSON.stringify(report));
    console.log(JSON.stringify({ passed: true, label, counts: result.counts, timing: result.timing, actions, js_heap: result.js_heap, page_errors: pageErrors }, null, 2));
  } catch (error) {
    await screenshot("failure").catch(() => {});
    const probe = await page.evaluate(() => {
      const value = window.__modelCaseProbe;
      const resources = performance.getEntriesByType("resource").map(entry => ({ name: entry.name, start: entry.startTime, duration: entry.duration, bytes: entry.encodedBodySize }));
      return { firstTriangleSubmission: value.firstTriangleSubmission, firstTriangleFrame: value.firstTriangleFrame, triangleDrawCalls: value.triangleDrawCalls, gpu: value.gpu, jsonFailures: value.jsonFailures, contextFailures: value.contextFailures, longTasks: value.longTasks, report: value.report, geometry: value.geometry, resources };
    }).catch(() => null);
    const failure = { context: config.context, label, message: error.message, phases, page_errors: pageErrors, console_messages: consoleMessages, ui_status: await page.locator(".review-status").innerText().catch(() => null), probe };
    fs.writeFileSync(path.join(output, `${label}-failure.json`), JSON.stringify(failure, null, 2));
    throw error;
  } finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
