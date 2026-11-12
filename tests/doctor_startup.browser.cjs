// Fresh browser processes observe the real module graph and public Three.js scene.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { launchBrowser, captureFailure } = require("./browser-qa-helpers.cjs");

async function verifyRecovery(base, evidence) {
  const browser = await launchBrowser(evidence);
  try {
    const api = await browser.newContext();
    const post = async (route, data, binary = false) => {
      const response = await api.request.post(base + route, binary ? { data, headers: { "Content-Type": "application/octet-stream" } } : { data });
      assert.ok(response.ok(), `${route}: ${response.status()}`); return response.json();
    };
    const project = await post("/api/projects", { name: "PUBLIC startup recovery" });
    const report = await post("/api/review/models?filename=public-startup.ifc", fs.readFileSync(path.resolve(__dirname, "../data/raw/Building-Hvac.ifc")), true);
    const saved = await post("/api/projects/revisions", { project_id: project.project_id, review_id: report.review_id, model_name: "PUBLIC startup model", label: "Public source baseline", retain_source: true });
    const template = await api.request.get(base + "/api/projects/rules/example");
    const preview = await post(`/api/projects/rules/preview?project=${project.project_id}&filename=public.zip`, await template.body(), true);
    const rule = await post("/api/projects/rules/confirm", { project_id: project.project_id, preview_id: preview.preview_id, confirmed_by: "Public startup fixture", responsible_team: "Public test team" });
    let job = await post("/api/projects/purpose/runs", { project_id: project.project_id, revision_id: saved.revision.revision_id, rule_revision_id: rule.rule_revision_id, purpose_id: "terminal-schedule", scope: { kind: "all" }, job_id: require("node:crypto").randomUUID() });
    const deadline = Date.now() + 30000;
    while (["queued", "running"].includes(job.state)) {
      assert.ok(Date.now() < deadline, "public startup fixture purpose run must finish");
      await new Promise(resolve => setTimeout(resolve, 100));
      job = await (await api.request.get(base + `/api/projects/purpose/jobs?job=${job.job_id}`)).json();
    }
    assert.equal(job.state, "succeeded");
    const runId = job.result.run_id;
    const targets = [
      { url: `${base}/?lang=zh#/fixture/member-evidence/first`, ready: ".first-register", identity: { hash: "#/fixture/member-evidence/first" } },
      { url: `${base}/projects.html?lang=en&project=${project.project_id}&tab=purpose&revision=${saved.revision.revision_id}&assessment=${runId}`, ready: "[data-run]", identity: { project: project.project_id, revision: saved.revision.revision_id, assessment: runId } },
      { url: `${base}/review.html?lang=zh&revision=${saved.revision.revision_id}&assessment=${runId}`, ready: ".enterprise-purpose-context", identity: { revision: saved.revision.revision_id, assessment: runId } },
    ];
    for (const [index, target] of targets.entries()) for (const fault of ["dependency", "stylesheet"]) {
      const page = await browser.newPage();
      // Interrupt an actual common dependency, not a synthetic DOM error event.
      const resource = fault === "dependency" ? "**/dom.js" : "**/doctor.css";
      await page.route(resource, route => route.abort("internetdisconnected"));
      await page.goto(target.url);
      await page.locator('html[data-startup-state="failed"] #startup-error').waitFor();
      assert.equal(await page.locator("#startup-error .startup-failure").isVisible(), true);
      assert.equal(await page.locator("#startup-error").getByRole("button").isEnabled(), true);
      await page.screenshot({ path: path.join(evidence, `startup-${index}-${fault}-failure.png`) });
      await page.unroute(resource);
      await page.locator("#startup-error").getByRole("button").click();
      await page.locator(target.ready).first().waitFor();
      if (index === 2) await page.locator(".review-status").filter({ hasText: "模型已载入" }).waitFor();
      const url = new URL(page.url());
      for (const [key, value] of Object.entries(target.identity)) assert.equal(key === "hash" ? url.hash : url.searchParams.get(key), value, "manual startup recovery preserves the exact record URL");
      assert.equal(await page.locator("#startup-error").isHidden(), true);
      await page.screenshot({ path: path.join(evidence, `startup-${index}-${fault}-recovered.png`) });
      await page.close();
    }
    console.log("PASS: actual dependency interruption exposes recovery on all three entries; explicit reload retains project/revision/assessment/hash");
  } catch (error) { await captureFailure(browser, evidence, error); throw error; }
  finally { await browser.close(); }
}

async function verifyViewerRecovery(base, evidence) {
  const browser = await launchBrowser(evidence);
  try {
    const page = await browser.newPage();
    await page.route("**/vendor/three/build/three.core.js", route => route.abort("internetdisconnected"));
    await page.goto(`${base}/review.html?lang=en`);
    await page.getByRole("button", { name: "Load public example", exact: true }).click();
    await page.locator(".review-status.has-error").waitFor();
    assert.equal(JSON.parse(await page.locator(".review-geometry-error-details pre").textContent()).phase, "viewer_module");
    assert.equal(await page.locator(".review-finding").count(), 2, "a viewer-module failure must preserve readable report evidence");
    await page.screenshot({ path: path.join(evidence, "viewer-module-failed.png") });
    const identity = new URL(page.url()).searchParams;
    await page.unroute("**/vendor/three/build/three.core.js");
    await page.locator(".review-view-overlay").getByRole("button", { name: "Reload page", exact: true }).click();
    await page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor();
    await page.waitForFunction(() => window.__doctorStartup.nextFrameAfterTriangle !== null);
    assert.equal(new URL(page.url()).searchParams.get("review"), identity.get("review"));
    assert.equal(new URL(page.url()).searchParams.get("finding"), identity.get("finding"));
    await page.locator("#review-viewport canvas").scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(evidence, "viewer-module-recovered.png") });
    console.log("PASS: real Three dependency interruption retains report and recovers actual triangle rendering");
  } catch (error) { await captureFailure(browser, evidence, error); throw error; }
  finally { await browser.close(); }
}

async function main() {
  const [base, evidence] = process.argv.slice(2);
  assert.ok(base && evidence);
  fs.mkdirSync(evidence, { recursive: true });
  const observations = [];
  // Every attempt owns a new Chromium process. The server cache is not reset.
  for (let attempt = 0; attempt < 12; attempt++) {
    const directory = path.join(evidence, `attempt-${attempt + 1}`);
    const browser = await launchBrowser(directory);
    const language = attempt % 2 ? "zh" : "en";
    const scenario = attempt % 3;
    const page = await browser.newPage({ viewport: language === "en" ? { width: 1440, height: 1000 } : { width: 390, height: 844 } });
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    try {
      if (scenario === 0) {
        const response = await page.goto(`${base}/?lang=${language}`);
        assert.equal(response.status(), 200);
        await page.locator(".home .primary-action").click();
      } else {
        const response = await page.goto(`${base}/${scenario === 1 ? "projects" : "review"}.html?lang=${language}`);
        assert.equal(response.status(), 200);
      }
      if (scenario < 2) {
        await page.locator("#project-name").waitFor();
        assert.equal(await page.locator(".project-create-form").isVisible(), true);
      } else {
        await page.getByRole("button", { name: language === "en" ? "Load public example" : "载入公共示例", exact: true }).click();
        await page.locator(".review-status").filter({ hasText: language === "en" ? "Model loaded" : "模型已载入" }).waitFor();
        await page.waitForFunction(() => window.__doctorStartup.nextFrameAfterTriangle !== null);
        const before = await page.evaluate(() => window.__doctorStartup.triangles);
        await page.getByRole("button", { name: language === "en" ? "Rotate left" : "向左旋转", exact: true }).click();
        await page.getByRole("button", { name: language === "en" ? "Zoom in" : "放大", exact: true }).click();
        assert.ok(await page.evaluate(previous => window.__doctorStartup.triangles > previous, before), "camera controls must render the actual mesh again");
        await page.locator("#review-viewport canvas").scrollIntoViewIfNeeded();
        await page.screenshot({ path: path.join(directory, `public-geometry-${language}.png`) });
      }
      const result = await page.evaluate(() => ({
        readyState: document.readyState, startup_state: document.documentElement.dataset.startupState,
        stylesheet_count: document.styleSheets.length,
        startup: window.__doctorStartup,
        geometry: performance.getEntriesByType("resource").filter(item => new URL(item.name).pathname === "/api/review/geometry").map(item => ({ start: item.startTime, responseEnd: item.responseEnd, duration: item.duration, status: item.responseStatus })),
        modules: performance.getEntriesByType("resource").filter(item => item.initiatorType === "script").map(item => ({ url: item.name, duration: item.duration, status: item.responseStatus })),
        canvas: document.querySelector("#review-viewport canvas") ? { width: document.querySelector("#review-viewport canvas").width, height: document.querySelector("#review-viewport canvas").height } : null,
      }));
      assert.equal(result.readyState, "complete");
      assert.equal(result.startup_state, "ready", "HTML completion alone cannot hide a failed entry module or stylesheet");
      assert.ok(result.stylesheet_count >= 1, "startup must load the actual stylesheets");
      assert.deepEqual(errors, []);
      if (scenario === 2) {
        assert.ok(result.startup.geometryDecode.end >= result.startup.geometryDecode.start);
        assert.equal(result.startup.geometryDecode.meshes, 32);
        assert.ok(result.startup.firstTriangleSubmission >= result.startup.geometryDecode.end);
        assert.ok(result.canvas.width > 0 && result.canvas.height > 0);
      }
      observations.push({ attempt: attempt + 1, language, scenario: ["home-to-project", "direct-project", "public-geometry"][scenario], fresh_browser_process: true, ...result });
    } catch (error) { await captureFailure(browser, directory, error); throw error; }
    finally {
      await browser.close();
      fs.writeFileSync(path.join(evidence, "startup.json"), JSON.stringify({ note: "A nonempty TRIANGLES submission followed by requestAnimationFrame is observed, not physical GPU presentation or sustained frame rate. Server cache is shared; these are fresh browser processes, not repeated cold native IFC imports.", observations }, null, 2));
    }
  }
  console.log("PASS: 12 fresh Chromium processes, home/project/module initialization, public geometry decode, WebGL initialization, triangle submission and camera redraw");
  await verifyRecovery(base, path.join(evidence, "recovery"));
  await verifyViewerRecovery(base, path.join(evidence, "viewer-recovery"));
}
module.exports = { verifyRecovery, verifyViewerRecovery };
if (require.main === module) main().catch(error => { console.error(error); process.exitCode = 1; });
