// Public-only candidate capture. Final output belongs to a CI/release artifact,
// not a source commit. See docs/evidence/phase2-candidate/README.md.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const net = require("node:net");
const assert = require("node:assert/strict");
const { spawn, execFileSync } = require("node:child_process");
const { performance } = require("node:perf_hooks");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "../..");
const SOURCE_PATHS = ["doctor", "internal", "epc_control_tower", "config", "ids", "tools/phase2_demo", "package.json", "package-lock.json", "requirements.txt", "pyproject.toml", ".github/workflows", "third_party/three", "data/raw/Building-Architecture.ifc", "data/raw/Building-Hvac.ifc", "data/raw/Building-Structural.ifc"];
const sha256 = body => crypto.createHash("sha256").update(body).digest("hex");
const git = args => execFileSync("git", args, { cwd: ROOT, encoding: "utf8" }).trim();

function options(argv) {
  const result = { browser: "chromium", port: 0, language: "en", hold: 1600, python: process.platform === "win32" ? "python" : "python3" };
  for (let i = 0; i < argv.length; i++) {
    const name = argv[i];
    if (name === "--rehearsal") result.rehearsal = true;
    else if (["--source-sha", "--data-dir", "--output-dir", "--python", "--browser", "--port", "--language", "--hold-ms"].includes(name)) result[name.slice(2)] = argv[++i];
    else throw new Error(`Unknown argument: ${name}`);
  }
  assert.match(result["source-sha"] || "", /^[0-9a-f]{40}$/i, "Supply the exact 40-character source commit SHA");
  assert.ok(result["data-dir"] && result["output-dir"], "Supply new external --data-dir and --output-dir directories");
  assert.ok(["chromium", "msedge"].includes(result.browser));
  assert.ok(["en", "zh"].includes(result.language));
  result.port = Number(result.port); result.hold = Number(result["hold-ms"] ?? result.hold);
  assert.ok(result.port >= 0 && result.port <= 65535 && Number.isInteger(result.port));
  assert.ok(result.hold >= 0 && result.hold <= 10000);
  return result;
}
function freshExternal(directory) {
  const result = path.resolve(directory);
  const relative = path.relative(ROOT, result);
  assert.ok(relative === ".." || relative.startsWith(".." + path.sep) || path.isAbsolute(relative), "Capture data and media must be outside the source checkout");
  assert.ok(!fs.existsSync(result) || fs.readdirSync(result).length === 0, "Refusing a reused data/media directory");
  fs.mkdirSync(result, { recursive: true });
  const real = fs.realpathSync(result);
  const actual = path.relative(ROOT, real);
  assert.ok(actual === ".." || actual.startsWith(".." + path.sep) || path.isAbsolute(actual), "Capture output may not link back into the checkout");
  return real;
}
async function freePort(requested) {
  const server = net.createServer();
  await new Promise((resolve, reject) => { server.once("error", reject); server.listen(requested, "127.0.0.1", resolve); });
  const port = server.address().port;
  await new Promise(resolve => server.close(resolve));
  return port;
}
async function ready(base, server) {
  for (let attempt = 0; attempt < 150; attempt++) {
    if (server.exitCode !== null) throw new Error("Fresh demo server exited during startup; see external server.log");
    try { const response = await fetch(`${base}/api/projects`); if (response.ok) { const body = await response.json(); assert.equal(body.projects.length, 0, "Fresh demo library must be empty"); return; } } catch (error) { if (error.code === "ERR_ASSERTION") throw error; }
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  throw new Error("Fresh public demo server did not become ready");
}
function files(directory, prefix = "") {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const relative = path.posix.join(prefix, entry.name);
    return entry.isDirectory() ? files(path.join(directory, entry.name), relative) : [relative];
  });
}
function vttTime(ms) {
  const seconds = Math.max(0, Math.floor(ms / 1000));
  return `${String(Math.floor(seconds / 3600)).padStart(2, "0")}:${String(Math.floor(seconds / 60) % 60).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}.${String(Math.floor(ms % 1000)).padStart(3, "0")}`;
}

async function main() {
  const opt = options(process.argv.slice(2));
  const sourceSHA = git(["rev-parse", "HEAD"]);
  assert.equal(sourceSHA, opt["source-sha"], "Run from the requested exact source commit");
  if (!opt.rehearsal) {
    execFileSync("git", ["diff", "--exit-code", sourceSHA, "--", ...SOURCE_PATHS], { cwd: ROOT, stdio: "pipe" });
    const untracked = git(["ls-files", "--others", "--exclude-standard", "--", ...SOURCE_PATHS]);
    assert.equal(untracked, "", "Candidate capture requires all runtime/capture inputs committed");
  }
  const dataDir = freshExternal(opt["data-dir"]);
  const output = freshExternal(opt["output-dir"]);
  for (const [parent, child] of [[dataDir, output], [output, dataDir]]) {
    const relative = path.relative(parent, child);
    assert.ok(relative === ".." || relative.startsWith(".." + path.sep) || path.isAbsolute(relative), "Keep raw server data and public artifact directories separate");
  }
  const sanitize = message => String(message).replaceAll(ROOT, "<checkout>").replaceAll(dataDir, "<external-demo-data>").replaceAll(output, "<artifact>");
  const sourceFiles = git(["ls-files", "--", ...SOURCE_PATHS]).split(/\r?\n/).filter(Boolean).sort();
  const sourceHashes = sourceFiles.map(name => ({ path: name.replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(path.join(ROOT, name))) }));
  const fixtureDir = path.join(dataDir, "public-fixtures");
  const generated = JSON.parse(execFileSync(opt.python, [path.join(__dirname, "export_public.py"), "--output-dir", fixtureDir], { cwd: ROOT, encoding: "utf8" }).trim());
  fs.cpSync(fixtureDir, path.join(output, "public-fixtures"), { recursive: true });
  fs.mkdirSync(path.join(output, "screenshots"));
  const port = await freePort(opt.port);
  const base = `http://127.0.0.1:${port}`;
  const env = { ...process.env, PYTHONUNBUFFERED: "1" };
  delete env.OPENAI_API_KEY;
  delete env.EPC_DOCTOR_CHECKS_DIR;
  const serverLog = fs.createWriteStream(path.join(dataDir, "server.log"));
  const server = spawn(opt.python, ["-m", "doctor.serve", "--port", String(port), "--checks-dir", path.join(dataDir, "checks")], { cwd: ROOT, env, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] });
  server.stdout.pipe(serverLog); server.stderr.pipe(serverLog);
  let browser = null;
  let context = null;
  let page = null;
  let video = null;
  const scenes = [];
  const errors = [];
  const blocked = [];
  let activeScene = "startup";
  const observations = {};
  const started = new Date().toISOString();
  let timelineStart = 0;
  try {
    await ready(base, server);
    const ai = await (await fetch(`${base}/api/review/ai`)).json();
    assert.equal(ai.configured, false, "Public capture uses local rule guidance without a provider key");
    browser = await chromium.launch({ headless: true, ...(opt.browser === "msedge" ? { channel: "msedge" } : {}) });
    context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, locale: "en-GB", timezoneId: "UTC", reducedMotion: "reduce", ...(opt.rehearsal ? {} : { recordVideo: { dir: path.join(dataDir, "video"), size: { width: 1440, height: 1000 } } }) });
    timelineStart = performance.now();
    page = await context.newPage(); video = page.video();
    page.on("pageerror", error => errors.push(sanitize(error.message)));
    await page.route("**/*", route => {
      const url = new URL(route.request().url());
      if (["data:", "blob:"].includes(url.protocol) || url.origin === new URL(base).origin) return route.continue();
      blocked.push(url.origin); return route.abort();
    });
    page.on("request", request => { if (new URL(request.url()).pathname === "/api/review/advice") assert.notEqual(request.postDataJSON()?.use_ai, true, "No live AI generation in this capture"); });
    const loaded = () => page.locator(".review-status").filter({ hasText: /Model loaded|模型已载入/ }).waitFor();
    const hasMesh = async () => { assert.equal(await page.locator("#review-viewport canvas").count(), 1); assert.ok(await page.getByRole("button", { name: opt.language === "zh" ? "聚焦构件" : "Focus element", exact: true }).isEnabled()); };
    async function scene(id, caption) {
      activeScene = id;
      const at = performance.now() - timelineStart;
      const image = `screenshots/${id}.png`;
      await page.screenshot({ path: path.join(output, image) });
      scenes.push({ id, caption, at_ms: Math.round(at), screenshot: image });
      // Deliberate reading time for the demonstration, never a readiness test.
      if (opt.hold) await page.waitForTimeout(opt.hold);
    }
    const lang = opt.language;
    const words = (en, zh) => lang === "zh" ? zh : en;
    await page.goto(`${base}/review.html?lang=${lang}`);
    await page.getByRole("button", { name: words("Load public example", "载入公共示例"), exact: true }).click();
    await loaded(); await hasMesh();
    const demoId = new URL(page.url()).searchParams.get("review");
    const demo = await (await page.request.get(`${base}/api/review/report?review=${demoId}`)).json();
    const demoGeometry = await (await page.request.get(`${base}/api/review/geometry?review=${demoId}`)).json();
    assert.ok(demoGeometry.meshes.length > 0);
    observations.public_example = { models: demo.models.length, elements: demo.summary.elements, meshes: demoGeometry.meshes.length, triangles: demoGeometry.meshes.reduce((count, mesh) => count + mesh.indices.length / 3, 0) };
    await scene("01-public-buildingsmart-overview", "Unmodified buildingSMART public sample: real architecture, structure and HVAC geometry.");
    await page.locator(".review-finding").first().click();
    await page.getByRole("button", { name: words("Focus element", "聚焦构件"), exact: true }).click();
    await page.getByRole("button", { name: words("Isolate element", "隔离构件"), exact: true }).click();
    await page.locator(".review-advice-summary").waitFor();
    assert.equal(await page.locator(".review-advice-mode").innerText(), words("Rule guidance", "规则指导"));
    await scene("02-public-element-local-guidance", "Select and isolate a real sample element. Advice here is local rule guidance, not a live AI response.");

    const beforeFile = path.join(fixtureDir, generated.exports.before.file);
    await page.locator("#review-file").setInputFiles(beforeFile);
    await loaded();
    const beforeReview = new URL(page.url()).searchParams.get("review");
    assert.notEqual(beforeReview, demoId);
    const beforeReport = await (await page.request.get(`${base}/api/review/report?review=${beforeReview}`)).json();
    assert.equal(beforeReport.summary.renderable, generated.exports.before.elements);
    const terminal = beforeReport.elements.find(element => element.tag === "PUBLIC-DEMO-terminal-a");
    const finding = beforeReport.findings.find(item => item.element_key === terminal.element_key && item.rule_id === "PV-001");
    await page.locator(`[data-finding="${finding.finding_id}"]`).click();
    await page.getByRole("button", { name: words("Focus element", "聚焦构件"), exact: true }).click();
    await scene("03-public-synthetic-editable-r1", "PUBLIC SYNTHETIC model exported from the included editable JSON source. Every demo object has real geometry.");
    await page.locator(".project-review-context").getByRole("button", { name: words("Save to project", "保存到项目"), exact: true }).click();
    await page.locator("#save-project").selectOption("__new__");
    await page.locator("#save-project-name").fill("PUBLIC SYNTHETIC · candidate demonstration");
    await page.locator("#save-model-name").fill("PUBLIC SYNTHETIC · editable source model");
    await page.locator("#save-revision-label").fill("R1 · public synthetic baseline");
    await page.getByRole("button", { name: words("Save model revision", "保存模型修订"), exact: true }).click();
    await page.locator(".project-context-status").filter({ hasText: words("Saved model revision", "已保存的模型修订") }).waitFor();
    const before = Object.fromEntries(["project", "model", "revision"].map(key => [key, new URL(page.url()).searchParams.get(key)]));
    await page.locator(".project-followup > summary").click();
    await page.locator("#followup-status").selectOption("ready_for_recheck");
    await page.locator("#followup-owner").fill("Public synthetic demo reviewer");
    await page.locator("#followup-note").fill("Demonstration source R2 changes terminal A. This manual work record does not change the IFC check result.");
    await page.getByRole("button", { name: words("Save follow-up", "保存处理记录"), exact: true }).click();
    await page.locator(".project-followup-form .project-form-message").filter({ hasText: words("Follow-up saved", "处理记录已保存") }).waitFor();
    assert.equal(await page.locator(".review-evidence .review-verdict").innerText(), "FAIL");
    await scene("04-saved-manual-record-still-fail", "Save R1 to a project. A human Ready for recheck record leaves its machine FAIL unchanged.");
    await page.getByRole("link", { name: words("Back to project", "返回项目"), exact: false }).click();
    await page.locator(".project-revision-row").waitFor();
    await scene("05-persisted-project-r1", "Saved project and model revision: reopen the recorded check instead of re-uploading.");
    await page.getByRole("link", { name: words("Open 3D review", "打开 3D 检查") + " ↗", exact: true }).click();
    await loaded(); assert.equal(new URL(page.url()).searchParams.get("revision"), before.revision);
    await page.getByRole("link", { name: words("Back to project", "返回项目"), exact: false }).click();
    await page.getByRole("link", { name: words("Import new revision", "导入新修订"), exact: true }).click();
    await page.locator("#review-file").setInputFiles(path.join(fixtureDir, generated.exports.after.file));
    await loaded();
    const afterReview = new URL(page.url()).searchParams.get("review");
    assert.notEqual(afterReview, beforeReview);
    const afterReport = await (await page.request.get(`${base}/api/review/report?review=${afterReview}`)).json();
    assert.equal(afterReport.summary.renderable, generated.exports.after.elements);
    await page.locator(".project-review-context").getByRole("button", { name: words("Save to project", "保存到项目"), exact: true }).click();
    await page.waitForFunction(id => document.querySelector("#save-model")?.value === id, before.model);
    await page.locator("#save-revision-label").fill("R2 · public synthetic source changes");
    await scene("06-save-r2-in-same-model", "R2 is regenerated from the editable public source and saved into the existing model, not a new model slot.");
    await page.getByRole("button", { name: words("Save model revision", "保存模型修订"), exact: true }).click();
    await page.locator(".project-context-status").filter({ hasText: words("Saved model revision", "已保存的模型修订") }).waitFor();
    const after = new URL(page.url()).searchParams.get("revision");
    assert.notEqual(after, before.revision); assert.equal(new URL(page.url()).searchParams.get("model"), before.model);
    await page.getByRole("link", { name: words("Back to project", "返回项目"), exact: false }).click();
    await page.locator(".project-model-card").waitFor();
    assert.equal(await page.locator(".project-model-card").count(), 1);
    await page.getByRole("button", { name: words("Compare revisions", "比较修订"), exact: true }).click();
    await page.getByRole("button", { name: words("View recheck changes", "查看复查变化"), exact: true }).click();
    await page.locator(".project-change-count").first().waitFor();
    const comparison = await (await page.request.get(`${base}/api/projects/compare?before=${before.revision}&after=${after}`)).json();
    for (const category of ["resolved", "remaining", "new", "missing", "not_comparable"]) {
      assert.equal(comparison.rows.filter(row => row.rule_id === "PV-001" && row.change === category).length, 1);
    }
    assert.equal(comparison.summary.errors.not_applicable, 0);
    observations.synthetic = { before_elements: beforeReport.summary.elements, after_elements: afterReport.summary.elements, before_meshes: beforeReport.summary.renderable, after_meshes: afterReport.summary.renderable, comparison: comparison.summary };
    await scene("07-same-model-recheck-outcomes", "One rule recheck passes, one remains, one is new, one is missing, and one is not comparable. These are synthetic demonstration changes.");
    await page.locator(".project-change-count.change-missing").click();
    await scene("08-disappearance-is-not-repair", "A removed object is Not found in current revision. Disappearance is not counted as a repair.");
    await page.locator(".project-change-count.change-resolved").click();
    await page.locator(".project-change-row a").first().click();
    await loaded(); await hasMesh();
    assert.equal(await page.locator(".review-evidence .review-verdict").innerText(), "PASS");
    await page.getByRole("button", { name: words("Focus element", "聚焦构件"), exact: true }).click();
    await page.getByRole("button", { name: words("Isolate element", "隔离构件"), exact: true }).click();
    await scene("09-reopened-r2-pass-real-mesh", "Open the exact R2 finding in 3D. The rule result is PASS for this synthetic source change; local rule guidance remains clearly labelled.");
    await page.getByRole("link", { name: words("Back to project", "返回项目"), exact: false }).click();
    const downloadPromise = page.waitForEvent("download");
    await page.getByRole("link", { name: words("Download work brief", "下载工作简报"), exact: true }).click();
    await (await downloadPromise).saveAs(path.join(output, "brief.md"));
    await scene("10-project-revisions-and-brief", "The project retains both revisions and offers a real Markdown work brief download.");
    await page.goto(`${base}/review.html?lang=zh&revision=${after}&finding=${comparison.rows.find(row => row.change === "resolved").after_finding_id}`);
    await page.locator(".review-status").filter({ hasText: "模型已载入" }).waitFor();
    assert.equal(await page.locator(".review-evidence .review-verdict").innerText(), "PASS");
    await scene("11-chinese-saved-revision", "The same saved revision and finding reopen in Chinese.");
    await page.close();
    if (video) await video.saveAs(path.join(output, "demo.webm"));
    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, locale: "zh-CN", timezoneId: "UTC", reducedMotion: "reduce" });
    mobile.on("pageerror", error => errors.push(sanitize(error.message)));
    await mobile.goto(`${base}/review.html?lang=zh&revision=${after}&finding=${comparison.rows.find(row => row.change === "resolved").after_finding_id}`);
    await mobile.locator(".review-status").filter({ hasText: "模型已载入" }).waitFor();
    assert.ok(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await mobile.locator(".review-view").scrollIntoViewIfNeeded();
    await mobile.screenshot({ path: path.join(output, "screenshots/12-mobile-real-mesh.png") });
    await mobile.locator(".review-right").scrollIntoViewIfNeeded();
    await mobile.screenshot({ path: path.join(output, "screenshots/13-mobile-saved-evidence.png") });
    await mobile.close();
    assert.deepEqual(errors, []); assert.deepEqual(blocked, []);
    assert.equal(git(["rev-parse", "HEAD"]), sourceSHA, "Source commit changed during capture");
    if (!opt.rehearsal) execFileSync("git", ["diff", "--exit-code", sourceSHA, "--", ...SOURCE_PATHS], { cwd: ROOT, stdio: "pipe" });
    const end = performance.now() - timelineStart;
    const captions = scenes.map((item, index) => `${index + 1}\n${vttTime(item.at_ms)} --> ${vttTime(scenes[index + 1]?.at_ms ?? end)}\n${item.caption}\n`).join("\n");
    fs.writeFileSync(path.join(output, "captions.vtt"), "WEBVTT\n\n" + captions);
    const media = files(output).sort().map(name => ({ path: name, bytes: fs.statSync(path.join(output, name)).size, sha256: sha256(fs.readFileSync(path.join(output, name))) }));
    const manifest = {
      schema_version: 1, status: opt.rehearsal ? "rehearsal-not-candidate" : "candidate-captured",
      source_sha: sourceSHA, source_tree_verified: !opt.rehearsal, capture_started_utc: started, capture_finished_utc: new Date().toISOString(),
      browser: { engine: "chromium", channel: opt.browser, version: browser.version(), playwright: require("playwright/package.json").version, headless: true, viewport: { width: 1440, height: 1000 } },
      platform: process.platform, language: opt.language, source_files: sourceHashes,
      media, scenes, observations, page_errors: errors, blocked_external_requests: blocked,
      ai: { configured: false, demonstrated_mode: "guidance", live_provider_call: false },
      public_inputs: { buildingsmart: { attribution: "PCERT Sample Scene © buildingSMART International Ltd. CC BY 4.0. Unmodified repository sample files.", url: "https://github.com/buildingSMART/Sample-Test-Files" }, synthetic: generated },
      limits: ["Public demonstration, not a private engineering case or capacity benchmark.", "The synthetic IFC revisions are generated from the included editable JSON source, not edited/exported in Revit.", "The video demonstrates local rule guidance without a configured AI key; no live AI output is claimed.", "Video chapter times are approximate playback positions; assertions use actual UI state, not fixed delays."],
    };
    fs.writeFileSync(path.join(output, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
    console.log(JSON.stringify({ status: manifest.status, source_sha: sourceSHA, browser: manifest.browser, scenes: scenes.length, files: media.length, page_errors: errors }));
  } catch (error) {
    if (page && !page.isClosed()) await page.screenshot({ path: path.join(output, "capture-failure.png") }).catch(() => {});
    fs.writeFileSync(path.join(output, "capture-failure.json"), JSON.stringify({ status: "failed", source_sha: sourceSHA, scene: activeScene, error: sanitize(error.message), page_errors: errors }, null, 2));
    throw new Error(sanitize(error.message));
  } finally {
    await context?.close().catch(() => {}); await browser?.close().catch(() => {});
    if (server.exitCode === null) server.kill();
    serverLog.end();
  }
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });
