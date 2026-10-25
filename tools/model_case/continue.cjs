// Same real saved model: manual record -> exact comparison -> brief -> restart.
// node tools/model_case/continue.cjs BASE before-browser.json after-browser.json PRIVATE_DIR [--restarted]
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const { chromium } = require("playwright");

async function main() {
  const [base, beforePath, afterPath, outputPath, flag] = process.argv.slice(2);
  assert.ok(["127.0.0.1", "localhost", "[::1]"].includes(new URL(base).hostname));
  const before = JSON.parse(fs.readFileSync(beforePath, "utf8"));
  const after = JSON.parse(fs.readFileSync(afterPath, "utf8"));
  const afterReport = JSON.parse(fs.readFileSync(path.join(path.dirname(afterPath), `${after.label}-report.json`), "utf8"));
  const remainingFinding = afterReport.findings.find(finding => finding.rule_id === "PV-001" && finding.status === "FAIL");
  assert.ok(remainingFinding);
  assert.equal(before.saved.project_id, after.saved.project_id);
  assert.equal(before.saved.model_id, after.saved.model_id);
  assert.notEqual(before.saved.revision_id, after.saved.revision_id);
  fs.mkdirSync(outputPath, { recursive: true });
  const output = fs.realpathSync(outputPath);
  const checkout = path.resolve(__dirname, "../..").toLowerCase();
  assert.ok(output.toLowerCase() !== checkout && !output.toLowerCase().startsWith(checkout + path.sep));
  const restarted = flag === "--restarted";
  const label = restarted ? "restart" : "flow";
  const errors = [];
  const browser = await chromium.launch({ headless: true, channel: "msedge" });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on("pageerror", error => errors.push(error.message));
  await page.route("**/*", route => {
    const url = new URL(route.request().url());
    if (url.origin === new URL(base).origin || ["data:", "blob:"].includes(url.protocol)) return route.continue();
    return route.abort();
  });
  const note = "Historical source-model editing and IFC export evidence is retained. The classification choice was a BIM role exercise, without a named engineer's approval. Requesting recheck does not change this revision's machine verdict.";
  const currentNote = "Two exported type conditions passed; 94 remain unmet. This item still needs source classification review. The historical type choice was a role exercise, not a named engineer's approval. Work status does not change the machine result.";
  const owner = "BIM role exercise";
  const shot = name => page.screenshot({ path: path.join(output, `${label}-${name}.png`) });
  const loaded = async () => {
    await page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor({ timeout: 60000 });
    assert.equal(await page.locator("#review-viewport canvas").count(), 1);
    assert.ok(await page.getByRole("button", { name: "Focus element", exact: true }).isEnabled());
  };
  async function followup(status, text) {
    await page.locator(".project-followup > summary").click();
    if (!restarted) {
      await page.locator("#followup-status").selectOption(status);
      await page.locator("#followup-owner").fill(owner);
      await page.locator("#followup-note").fill(text);
      await page.getByRole("button", { name: "Save follow-up", exact: true }).click();
      await page.locator(".project-followup-form .project-form-message").filter({ hasText: "Follow-up saved" }).waitFor();
    }
    assert.equal(await page.locator("#followup-status").inputValue(), status);
    assert.equal(await page.locator("#followup-owner").inputValue(), owner);
    assert.equal(await page.locator("#followup-note").inputValue(), text);
    assert.equal(await page.locator(".review-evidence .review-verdict").innerText(), "FAIL");
  }
  try {
    await page.goto(`${base}/review.html?lang=en&revision=${before.saved.revision_id}&finding=${before.targets[0].finding_id}`);
    await loaded();
    assert.equal(await page.locator(".review-evidence .review-verdict").innerText(), "FAIL");
    await followup("ready_for_recheck", note);
    await shot("manual-ready-machine-fail");
    await page.getByRole("link", { name: "Back to project", exact: false }).click();
    await page.locator(".project-model-card").waitFor();
    assert.equal(await page.locator(".project-model-card").count(), 1);
    assert.equal(await page.locator(".project-revision-row").count(), 2);
    await page.getByRole("button", { name: "Compare revisions", exact: true }).click();
    await page.getByRole("button", { name: "View recheck changes", exact: true }).click();
    await page.locator(".project-change-count").first().waitFor();
    assert.equal(await page.locator(".project-change-count.change-resolved strong").innerText(), "2");
    assert.equal(await page.locator(".project-change-count.change-remaining strong").innerText(), "94");
    for (const category of ["new", "missing", "not_applicable", "not_comparable"]) assert.equal(await page.locator(`.project-change-count.change-${category} strong`).innerText(), "0");
    await shot("comparison-two-pass-94-remain");
    const response = await page.request.get(`${base}/api/projects/compare?before=${before.saved.revision_id}&after=${after.saved.revision_id}`);
    assert.ok(response.ok());
    const comparison = await response.json();
    const resolved = comparison.rows.filter(row => row.change === "resolved" && row.rule_id === "PV-001");
    assert.equal(resolved.length, 2);
    assert.deepEqual(new Set(resolved.map(row => row.global_id)), new Set(before.targets.map(target => target.global_id)));
    for (const row of resolved) { assert.equal(row.before_actual, "NOTDEFINED"); assert.equal(row.after_actual, "LOUVRE"); }
    await page.goto(`${base}/review.html?lang=en&revision=${after.saved.revision_id}&finding=${remainingFinding.finding_id}`);
    await loaded();
    await followup("in_progress", currentNote);
    await shot("current-work-still-fail");
    await page.getByRole("link", { name: "Back to project", exact: false }).click();
    await page.locator(".project-model-card").waitFor();
    const downloadPromise = page.waitForEvent("download");
    await page.getByRole("link", { name: "Download work brief", exact: true }).click();
    const download = await downloadPromise;
    const briefPath = path.join(output, `${label}-work-brief.md`);
    await download.saveAs(briefPath);
    const brief = fs.readFileSync(briefPath, "utf8");
    assert.ok(brief.includes("PV-001") && brief.includes(owner));
    await page.getByRole("button", { name: "Compare revisions", exact: true }).click();
    await page.getByRole("button", { name: "View recheck changes", exact: true }).click();
    await page.locator(".project-change-count").first().waitFor();
    await page.locator(".project-change-count.change-resolved").click();
    await page.locator(".project-change-row a").first().click();
    await loaded();
    assert.equal(new URL(page.url()).searchParams.get("revision"), after.saved.revision_id);
    assert.equal(await page.locator(".review-evidence .review-verdict").innerText(), "PASS");
    assert.equal(await page.locator(".review-geometry-note").count(), 0);
    await page.getByRole("button", { name: "Focus element", exact: true }).click();
    await page.getByRole("button", { name: "Isolate element", exact: true }).click();
    assert.match(await page.locator(".review-view-footer").innerText(), /Visible elements: 1/);
    await shot("current-passed-real-mesh");
    await page.getByRole("button", { name: "中文", exact: true }).click();
    await page.locator(".review-status").filter({ hasText: "模型已载入" }).waitFor();
    assert.equal(new URL(page.url()).searchParams.get("revision"), after.saved.revision_id);
    assert.equal(await page.locator(".review-evidence .review-verdict").innerText(), "PASS");
    await shot("chinese-current-evidence");
    assert.deepEqual(errors, []);
    const result = { passed: true, restarted, project_id: before.saved.project_id, model_id: before.saved.model_id, before_revision: before.saved.revision_id, after_revision: after.saved.revision_id, summary: comparison.summary, exact_resolved_targets_verified: true, manual_ready_did_not_change_fail: true, current_in_progress_still_fail: true, original_mesh_visible: true, note_exact: true, brief_downloaded: true, errors };
    fs.writeFileSync(path.join(output, `${label}-verification.json`), JSON.stringify(result, null, 2));
    console.log(JSON.stringify({ passed: true, restarted, summary: comparison.summary, errors }, null, 2));
  } catch (error) { await shot("failure").catch(() => {}); throw error; }
  finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
