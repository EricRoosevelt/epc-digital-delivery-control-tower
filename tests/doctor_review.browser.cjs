// Real IFC integration, with one injected transport failure for recovery.
// NODE_PATH=<external Playwright node_modules> node tests/doctor_review.browser.cjs URL [evidence-dir]
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { captureFailure, launchBrowser } = require("./browser-qa-helpers.cjs");

async function main() {
  const base = process.argv[2];
  assert.ok(base, "Supply a running isolated Doctor URL");
  const evidence = process.argv[3];
  if (evidence) fs.mkdirSync(evidence, { recursive: true });
  const browser = await launchBrowser(evidence);
  const observations = [];
  const errors = [];
  const capture = async (page, name, fullPage = false) => {
    if (evidence) await page.screenshot({ path: path.join(evidence, `${name}.png`), fullPage });
  };
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    page.on("pageerror", e => errors.push(e.message));
    await page.goto(`${base}/review.html?lang=en`);
    await page.getByRole("button", { name: "Load public example", exact: true }).click();
    await page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor();
    await page.locator(".review-advice-summary").waitFor();
    assert.equal(await page.locator("#review-viewport canvas").count(), 1);
    assert.equal(await page.getByRole("button", { name: "Focus element", exact: true }).isEnabled(), true);
    assert.equal(await page.locator(".review-finding").count(), 2);
    assert.equal(await page.locator(".review-geometry-note").count(), 0, "renderable element must not be called geometry-less");
    for (const failure of [
      { status: 503, body: JSON.stringify({ error: "Temporary geometry test failure" }), phase: "geometry_request" },
      { status: 200, body: "{invalid geometry JSON", phase: "geometry_decode" },
      { status: 200, body: '{"meshes":{}}', phase: "viewer_load" },
    ]) {
      await page.route("**/api/review/geometry**", route => route.fulfill({ status: failure.status, body: failure.body, contentType: "application/json", headers: { "X-Request-ID": "public-geometry-regression" } }));
      await page.getByRole("button", { name: "Load public example", exact: true }).click();
      await page.locator('.review-status[aria-busy="false"]').waitFor();
      assert.equal(await page.locator(".review-status.has-error").count(), 1, "geometry failure must stay recoverable rather than report Model loaded");
      assert.doesNotMatch(await page.locator(".review-status").innerText(), /Model loaded/);
      assert.equal(await page.locator(".review-finding").count(), 2, "geometry failure keeps check evidence available");
      assert.equal(await page.locator(".review-geometry-note").count(), 0, "renderer/transport failure is not missing IFC geometry");
      assert.ok(await page.locator(".review-geometry-error-details pre").textContent(), "original error remains inspectable");
      const diagnostic = JSON.parse(await page.locator(".review-geometry-error-details pre").textContent());
      assert.equal(diagnostic.phase, failure.phase);
      assert.equal(diagnostic.request_id, "public-geometry-regression");
      assert.equal(await page.getByRole("button", { name: "Focus element", exact: true }).isEnabled(), false);
      await page.unroute("**/api/review/geometry**");
      await page.locator(".review-view-overlay").getByRole("button", { name: "Retry", exact: true }).click();
      await page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor();
      assert.equal(await page.getByRole("button", { name: "Focus element", exact: true }).isEnabled(), true);
    }
    // An injected browser event verifies reporting, not a claim of actual GPU loss.
    await page.locator("#review-viewport canvas").evaluate(canvas => canvas.dispatchEvent(new Event("webglcontextlost")));
    await page.locator(".review-status.has-error").waitFor();
    const webglDiagnostic = JSON.parse(await page.locator(".review-geometry-error-details pre").textContent());
    assert.equal(webglDiagnostic.phase, "webgl_context");
    assert.ok(webglDiagnostic.webgl_events.some(event => event.type === "webglcontextlost"));
    await page.locator("#review-viewport canvas").evaluate(canvas => canvas.dispatchEvent(new Event("webglcontextrestored")));
    await page.locator(".review-view-overlay").getByRole("button", { name: "Retry", exact: true }).click();
    await page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor();
    assert.match(await page.locator(".review-ai-status").innerText(), /Local rule guidance|AI configured/);
    await capture(page, "review-en-1440");
    const review = new URL(page.url()).searchParams.get("review");
    const report = await (await page.request.get(`${base}/api/review/report?review=${review}`)).json();
    assert.equal(report.summary.elements, 39);
    assert.equal(report.summary.renderable, 32);
    assert.equal(report.summary.errors, 2);
    assert.equal(report.summary.information, 19);
    const first = await page.locator(".review-object-heading h3").innerText();
    await page.locator(".review-finding").nth(1).click();
    assert.notEqual(await page.locator(".review-object-heading h3").innerText(), first);
    await page.getByRole("button", { name: "Focus element", exact: true }).click();
    await page.getByRole("button", { name: "Isolate element", exact: true }).click();
    assert.match(await page.locator(".review-view-footer").innerText(), /Visible elements: 1/);
    await capture(page, "review-en-isolated");
    await page.getByRole("button", { name: "Reset view", exact: true }).click();
    assert.match(await page.locator(".review-view-footer").innerText(), /Visible elements: 32/);
    await page.getByRole("button", { name: "Show all", exact: true }).click();
    await page.getByRole("button", { name: "Reset view", exact: true }).click();
    const beforePick = await page.locator(".review-object-heading h3").innerText();
    const box = await page.locator("#review-viewport canvas").boundingBox();
    for (const [x, y] of [[.52, .55], [.45, .67], [.62, .7]]) {
      await page.mouse.click(box.x + box.width * x, box.y + box.height * y);
      if (await page.locator(".review-object-heading h3").innerText() !== beforePick) break;
    }
    assert.notEqual(await page.locator(".review-object-heading h3").innerText(), beforePick, "canvas picking changes detail");
    await page.locator("#review-status-filter").selectOption("INFO");
    assert.equal(await page.locator(".review-finding").count(), 19);
    await page.locator(".review-finding").first().click();
    assert.equal(await page.locator(".review-evidence .review-verdict").innerText(), "INFO");
    assert.equal(await page.locator(".review-evidence.is-information").count(), 1);
    await page.locator("#review-search").fill("no-match-ui-regression");
    assert.match(await page.locator("#review-findings").innerText(), /No matching results/);
    await page.getByRole("button", { name: "Clear search", exact: true }).click();
    assert.equal(await page.locator(".review-finding").count(), 19);
    assert.equal(await page.locator("#review-search").evaluate(el => el === document.activeElement), true);
    const unavailable = report.elements.find(e => e.geometry_status !== "renderable");
    assert.ok(unavailable);
    await page.locator("#review-status-filter").selectOption("");
    await page.locator("#review-search").fill(unavailable.global_id);
    await page.locator(".review-finding").first().click();
    assert.equal(await page.locator(".review-geometry-note").count(), 1);
    assert.equal(await page.getByRole("button", { name: "Focus element", exact: true }).isEnabled(), false);
    await capture(page, "review-en-no-geometry");
    await page.locator("#review-model").selectOption({ index: 1 });
    const visible = await page.locator(".review-view-footer").innerText();
    assert.doesNotMatch(visible, /Visible elements: 32/);
    await page.getByRole("button", { name: "Load public example", exact: true }).click();
    await page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor();
    await page.route("**/api/review/demo", route => route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ error: "Temporary test outage" }) }));
    await page.getByRole("button", { name: "Load public example", exact: true }).click();
    await page.locator(".review-status.has-error").waitFor();
    assert.equal(await page.locator(".review-finding").count(), 2, "failure preserves prior results");
    await page.unroute("**/api/review/demo");
    await page.locator(".review-status").getByRole("button", { name: "Retry", exact: true }).click();
    await page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor();
    await page.locator("#review-file").setInputFiles(path.resolve(__dirname, "../data/raw/Building-Hvac.ifc"));
    await page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor();
    await page.locator(".review-source").filter({ hasText: "Building-Hvac.ifc" }).waitFor();
    assert.equal(await page.locator("#review-model option").count(), 2);
    await page.locator("#review-file").setInputFiles(path.resolve(__dirname, "../data/raw/Building-Architecture.ifc"));
    await page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor();
    await page.locator(".review-source").filter({ hasText: "Building-Architecture.ifc" }).waitFor();
    assert.equal(await page.locator("#review-status-filter").inputValue(), "INFO", "information-only import starts with its relevant results");
    assert.ok(await page.locator(".review-finding").count() > 0);
    assert.equal(await page.locator(".review-outside").isVisible(), false);
    assert.equal(await page.locator(".review-evidence .review-verdict").innerText(), "INFO");
    await capture(page, "review-en-information-only-import");
    observations.push("English desktop: real demo, list selection, picking, focus, isolate/reset, all extents, INFO semantics, local search/clear, no geometry, model filtering, failed-load preservation/retry, raw HVAC and information-only Architecture IFC import.");
    await page.goto(`${base}/review.html?lang=zh`);
    await page.setViewportSize({ width: 390, height: 844 });
    await page.getByRole("button", { name: "载入公共示例", exact: true }).click();
    await page.locator(".review-status").filter({ hasText: "模型已载入" }).waitFor();
    assert.equal(await page.locator("#review-viewport canvas").count(), 1);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), "no phone horizontal overflow");
    await capture(page, "review-zh-390-top");
    await page.locator(".review-view").scrollIntoViewIfNeeded();
    await capture(page, "review-zh-390-viewport");
    await page.locator(".review-finding").nth(1).click();
    await page.locator(".review-advice-summary").waitFor();
    await page.locator(".review-advice").scrollIntoViewIfNeeded();
    await capture(page, "review-zh-390-advice");
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.getByRole("button", { name: "English", exact: true }).click();
    await page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor();
    assert.equal(new URL(page.url()).searchParams.get("lang"), "en");
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    observations.push("Chinese 390px: real WebGL, full viewport controls, selection/advice, no horizontal overflow; locale reload and reduced motion.");
    // Controlled HTTP UI contract only: no key and no live provider call.
    for (const language of ["en", "zh"]) {
      const wording = (en, zh) => language === "en" ? en : zh;
      await page.route("**/api/review/ai", route => route.fulfill({ json: { configured: true, provider: "CONTROLLED", model: "UI fixture; no live provider" } }));
      let mode = "error", release, heldStarted, heldFinished;
      const started = new Promise(resolve => { heldStarted = resolve; });
      const finished = new Promise(resolve => { heldFinished = resolve; });
      await page.route("**/api/review/advice", async route => {
        const payload = route.request().postDataJSON();
        assert.deepEqual(Object.keys(payload).sort(), ["finding_id", "language", "review_id", "use_ai"], "AI request sends identifiers and language only, never IFC or geometry");
        if (!payload.use_ai) return route.continue();
        if (mode === "error") return route.fulfill({ status: 503, json: { error: "CONTROLLED provider outage" } });
        if (mode === "held") {
          heldStarted();
          await new Promise(resolve => { release = resolve; });
          try { await route.fulfill({ json: { mode: "ai", summary: "CONTROLLED late answer for old selection", actions: [], verification: [], facts: [], citations: [], limitations: [] } }); }
          finally { heldFinished(); }
          return;
        }
        return route.fulfill({ json: { mode: "ai", summary: "CONTROLLED AI response; not a live provider", actions: ["CONTROLLED source verification action"], verification: ["CONTROLLED export verification"], facts: [], citations: [{ id: "CONTROLLED", label: "Controlled public UI fixture" }], limitations: ["Controlled response for browser-state verification only"] } });
      });
      await page.goto(`${base}/review.html?lang=${language}`);
      await page.getByRole("button", { name: wording("Load public example", "载入公共示例"), exact: true }).click();
      await page.locator(".review-status").filter({ hasText: wording("Model loaded", "模型已载入") }).waitFor();
      await page.locator(".review-advice-summary").waitFor();
      const generate = page.getByRole("button", { name: wording("Generate AI advice", "生成 AI 建议"), exact: true });
      await generate.click();
      await page.locator(".review-inline-error").waitFor();
      assert.equal(await generate.isEnabled(), true);
      assert.equal(await page.locator(".review-advice-mode").innerText(), wording("Rule guidance", "规则指导"), "a failed AI request must not claim an AI answer");
      mode = "success";
      await page.locator(".review-advice").getByRole("button", { name: wording("Retry", "重试"), exact: true }).click();
      await page.locator(".review-advice-summary").filter({ hasText: "CONTROLLED AI response" }).waitFor();
      assert.equal(await page.locator(".review-advice-mode").innerText(), wording("AI advice", "AI 建议"));
      await page.locator(".review-advice").scrollIntoViewIfNeeded();
      await capture(page, `review-${language}-controlled-ai`);
      mode = "held";
      await generate.click(); await started;
      assert.equal(await page.getByRole("button", { name: wording("Generating…", "正在生成…"), exact: true }).isEnabled(), false);
      assert.equal(await page.locator(".review-advice-body").getAttribute("aria-busy"), "true");
      await page.locator(".review-finding").nth(1).click();
      await page.locator(".review-advice-summary").waitFor();
      const currentAdvice = await page.locator(".review-advice-summary").innerText();
      release(); await finished;
      assert.equal(await page.locator(".review-advice-summary").innerText(), currentAdvice, "late AI response cannot overwrite a newly selected object's guidance");
      assert.equal(await page.locator(".review-advice-mode").innerText(), wording("Rule guidance", "规则指导"));
      await page.unroute("**/api/review/ai"); await page.unroute("**/api/review/advice");
    }
    observations.push("CONTROLLED HTTP only, no live AI: zh/en configured label, generating/disabled state, provider error and Retry, explicit AI response label, minimal request fields, and late old-selection response ignored.");
    assert.deepEqual(errors, []);
    if (evidence) fs.writeFileSync(path.join(evidence, "review-browser.json"), JSON.stringify({ observations, errors }, null, 2));
    console.log(JSON.stringify({ passed: true, observations, errors }, null, 2));
  } catch (error) { await captureFailure(browser, evidence, error); throw error; }
  finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
