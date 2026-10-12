// Controlled transport/schema cases are labelled; they are not real model results.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

async function main() {
  const [base, out] = process.argv.slice(2); assert.ok(base && out);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ channel: process.env.BROWSER_CHANNEL || "msedge", headless: true });
  const page = await browser.newPage({ viewport: { width: 375, height: 812 } });
  const facts = [];
  try {
    await page.goto(`${base}/?lang=en#/fixture`); await page.locator(".example-list").waitFor();
    let release;
    const pending = new Promise((resolve) => { release = resolve; });
    await page.route(`${base}/api/local`, async (route) => { await pending; await route.continue(); });
    await page.locator('.main-nav a[href="#/local"]').click();
    await page.locator('main > [role="status"]').waitFor();
    const staleContext = await page.locator("#context").innerText();
    facts.push({ name: "controlled-delay-real-request", staleContext });
    await page.screenshot({ path: path.join(out, "controlled-loading.png") });
    release(); await page.locator("#local-files").waitFor(); await page.unroute(`${base}/api/local`);
    assert.equal(staleContext, "", "old example context must not label a pending local request");

    await page.route(`${base}/api/local`, (route) => route.fulfill({ status: 500,
      contentType: "application/json", body: JSON.stringify({error: "Controlled transport-fault test"}) }));
    await page.reload(); await page.locator(".fault").waitFor();
    assert.equal(await page.locator(".ws-list").count(), 0);
    await page.screenshot({ path: path.join(out, "controlled-fault.png") });
    await page.unroute(`${base}/api/local`); await page.reload(); await page.locator("#local-files").waitFor();
    facts.push({ name: "controlled-fault-real-recovery", passed: true });

    for (const name of ["recheck-requirement-relaxed", "recheck-semantics-changed"]) {
      await page.goto(`${base}/?lang=en#/fixture/${name}/recheck`);
      await page.locator(".recheck-items").first().waitFor();
      const objectLinks = page.locator('main a[href*="/recheck/"]').filter({ hasText: /building element/ });
      assert.ok(await objectLinks.count() > 0);
      await objectLinks.first().click(); await page.locator(".next-step").waitFor();
      const reading = await page.locator("main").innerText();
      assert.match(reading, /original.*condition/i);
      assert.match(reading, /whole.scope|every element|whole assessed scope/i);
      assert.match(reading, /changed conclusion does not mean the original condition is met/i);
      facts.push({ name, kind: "real-simulated-example", passed: true });
      await page.screenshot({ path: path.join(out, `${name}.png`) });
    }

    const check = "e7838dad4ac0d3b3";
    const response = await page.request.get(`${base}/api/local/envelope?run=${check}`);
    const envelope = await response.json();
    const finding = envelope.findings[0];
    const element = envelope.elements[finding.element_key];
    delete element.name;
    delete envelope.run.models[0].filename;
    envelope.requirements[finding.requirement_key].rule_id = "CONTROLLED-UNKNOWN-RULE";
    await page.route(`${base}/api/local/envelope?run=${check}`, (route) => route.fulfill({
      contentType: "application/json", body: JSON.stringify(envelope),
    }));
    await page.goto(`${base}/?lang=en#/local/${check}/finding/${finding.finding_key}`);
    await page.locator(".ws-detail h2").waitFor();
    assert.equal(await page.locator(".ws-detail h2 .not-carried").count(), 1);
    assert.ok(await page.locator(".input-identity .not-carried").isVisible());
    assert.equal(await page.locator(".ws-detail .checker-read").count(), 0);
    assert.equal(await page.locator(".ws-detail .next-step dl.facts").count(), 0);
    await page.screenshot({ path: path.join(out, "controlled-missing-unknown.png") });
    facts.push({ name: "missing-name-filename-unknown-rule", kind: "controlled-envelope-only", passed: true });
    await page.goto(`${base}/?lang=en#/local/${check}/finding/does-not-exist`);
    await page.locator(".ws-detail .problem").waitFor();
    const errorFocused = await page.locator(".ws-detail .problem").evaluate((el) => document.activeElement === el);
    assert.equal(errorFocused, true, "invalid finding must focus visible error, not the hidden result list");
    facts.push({ name: "invalid-finding-route", kind: "real-route-refusal", passed: true });
  } finally {
    await browser.close();
    fs.writeFileSync(path.join(out, "resilience.json"), JSON.stringify(facts, null, 2) + "\n");
  }
  console.log("PASS: loading, controlled fault/recovery, real #58/#60 examples, controlled missing fields/unknown rule");
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
