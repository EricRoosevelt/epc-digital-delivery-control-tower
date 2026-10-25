// Public synthetic regression for a saved/deep-linked PASS outside the first 100.
// No geometry/capacity claim: this fixture isolates result-window selection.
// node tests/doctor_review_large_selection.browser.cjs URL [scratch-evidence-dir]
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

function publicIFC() {
  const rows = Array.from({ length: 150 }, (_, index) => {
    const guid = "0" + "A".repeat(17) + index.toString(36).padStart(4, "0");
    return `#${index + 1}=IFCAIRTERMINAL('${guid}',$,'Public PASS terminal ${String(index).padStart(3, "0")}',$,$,$,$,'TEST-${index}',.DIFFUSER.);`;
  });
  return Buffer.from("ISO-10303-21;\nHEADER;\nFILE_DESCRIPTION(('Public synthetic selection regression'),'2;1');\nFILE_NAME('selection.ifc','2026-10-25T00:00:00',('test'),('test'),'test','test','');\nFILE_SCHEMA(('IFC4'));\nENDSEC;\nDATA;\n" + rows.join("\n") + "\nENDSEC;\nEND-ISO-10303-21;\n");
}

async function main() {
  const base = process.argv[2];
  const evidence = process.argv[3];
  assert.ok(base);
  if (evidence) fs.mkdirSync(evidence, { recursive: true });
  const browser = await chromium.launch({ headless: true, channel: process.env.BROWSER_CHANNEL || "msedge" });
  const errors = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    page.on("pageerror", error => errors.push(error.message));
    await page.goto(`${base}/review.html?lang=en`);
    const responsePromise = page.waitForResponse(response => new URL(response.url()).pathname === "/api/review/models");
    await page.locator("#review-file").setInputFiles({ name: "public-selection-regression.ifc", mimeType: "application/octet-stream", buffer: publicIFC() });
    const report = await (await responsePromise).json();
    await page.locator(".review-status").filter({ hasText: "Model loaded" }).waitFor();
    assert.equal(report.summary.elements, 150);
    const target = report.elements.at(-1);
    const finding = report.findings.find(f => f.element_key === target.element_key && f.rule_id === "PV-001");
    const passes = report.findings.filter(f => f.status === "PASS");
    assert.ok(passes.length > 100);
    assert.ok(passes.findIndex(f => f.finding_id === finding.finding_id) > 100);
    await page.locator(".project-review-context").getByRole("button", { name: "Save to project", exact: true }).click();
    await page.locator("#save-project").selectOption("__new__");
    await page.locator("#save-project-name").fill("Public synthetic selection regression");
    await page.locator("#save-model-name").fill("Public synthetic terminal register");
    await page.locator("#save-revision-label").fill("R1 · selection window");
    await page.getByRole("button", { name: "Save model revision", exact: true }).click();
    await page.locator(".project-context-status").filter({ hasText: "Saved model revision" }).waitFor();
    const revision = new URL(page.url()).searchParams.get("revision");
    for (const lang of ["en", "zh"]) {
      await page.goto(`${base}/review.html?lang=${lang}&revision=${revision}&finding=${finding.finding_id}`);
      await page.locator(".review-status").filter({ hasText: lang === "en" ? "Model loaded" : "模型已载入" }).waitFor();
      assert.equal(await page.locator("#review-status-filter").inputValue(), "PASS");
      assert.equal(await page.locator(".review-finding").count(), 100);
      assert.equal(await page.locator(".review-finding").first().getAttribute("data-finding"), finding.finding_id);
      assert.equal(await page.locator(".review-finding.is-selected").count(), 1);
      assert.equal(await page.locator(".review-finding.is-selected").getAttribute("aria-pressed"), "true");
      assert.equal(await page.locator(".review-object-heading h3").innerText(), target.name);
      await page.locator("#review-status-filter").selectOption("FAIL");
      assert.equal(await page.locator(`[data-finding="${finding.finding_id}"]`).count(), 0);
      assert.equal(await page.locator(".review-finding.is-selected").count(), 0);
      assert.equal(await page.locator(".review-finding").count(), 100);
      await page.locator("#review-status-filter").selectOption("PASS");
      assert.equal(await page.locator(".review-finding").first().getAttribute("data-finding"), finding.finding_id);
      await page.locator("#review-search").fill("Public PASS terminal 001");
      assert.equal(await page.locator(".review-finding").count(), 3);
      assert.equal(await page.locator(".review-finding.is-selected").count(), 0);
      assert.equal(await page.locator(".review-outside").isVisible(), true);
      assert.equal(await page.locator(".review-object-heading h3").innerText(), target.name);
      await page.locator(".review-clear").click();
      assert.equal(await page.locator(".review-finding").count(), 100);
      assert.equal(await page.locator(".review-finding").first().getAttribute("data-finding"), finding.finding_id);
      if (evidence) await page.screenshot({ path: path.join(evidence, `public-selection-${lang}.png`) });
    }
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ passed: true, synthetic: true, elements: 150, pass_findings: passes.length, rendered_limit: 100, locales: ["en", "zh"], errors }));
  } finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
