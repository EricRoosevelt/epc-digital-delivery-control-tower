// Regression for verified review findings: tablet grid order and unbroken names.
const assert = require("node:assert/strict");
const { chromium } = require("playwright");
async function main() {
  const base = process.argv[2]; assert.ok(base);
  const browser = await chromium.launch({ channel: process.env.BROWSER_CHANNEL || "msedge", headless: true });
  const failures = [];
  try {
    for (const width of [701, 768, 900]) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      await page.goto(`${base}/?lang=en#/local/e7838dad4ac0d3b3`);
      await page.locator("#workspace-filter").waitFor();
      const initial = await page.evaluate(() => ({
        list: document.querySelector(".ws-list").getBoundingClientRect().width,
        frame: document.querySelector(".ws-workbench").getBoundingClientRect().width,
      }));
      if (Math.abs(initial.list - initial.frame) > 1) failures.push(`${width}: unselected list ${initial.list} vs frame ${initial.frame}`);
      await page.locator(".c-name a").filter({ hasText: "house fireplace cap" }).click();
      await page.locator(".ws-detail h2").waitFor();
      const chosen = await page.evaluate(() => ({
        list: document.querySelector(".ws-list").getBoundingClientRect().left,
        detail: document.querySelector(".ws-detail").getBoundingClientRect().left,
      }));
      if (!(chosen.list < chosen.detail)) failures.push(`${width}: detail ${chosen.detail} must follow list ${chosen.list}`);
      await page.close();
    }
    for (const width of [375, 1280]) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      const url = `${base}/api/local/envelope?run=e7838dad4ac0d3b3`;
      const envelope = await (await page.request.get(url)).json();
      const finding = envelope.findings[0];
      envelope.elements[finding.element_key].name = "CONTROLLED_LONG_NAME_" + "A".repeat(160);
      await page.route(url, (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify(envelope) }));
      await page.goto(`${base}/?lang=en#/local/e7838dad4ac0d3b3/finding/${finding.finding_key}`);
      await page.locator(".ws-detail h2").waitFor();
      const geometry = await page.evaluate(() => ({
        client: document.documentElement.clientWidth, content: document.documentElement.scrollWidth,
        detail: document.querySelector(".ws-detail").getBoundingClientRect().width,
        frame: document.querySelector(".ws-workbench").getBoundingClientRect().width,
      }));
      if (geometry.client !== geometry.content) failures.push(`${width}: unbroken name page overflow ${geometry.content} vs ${geometry.client}`);
      if (width === 375 && Math.abs(geometry.detail - geometry.frame) > 1) failures.push(`375: single detail ${geometry.detail} must fill ${geometry.frame}`);
      assert.equal((await page.locator(".ws-detail h2").innerText()).length, 181);
      await page.close();
    }
  } finally { await browser.close(); }
  assert.deepEqual(failures, [], failures.join("\n"));
  console.log("PASS: 701/768/900 local grid and full-width initial list; 375/1280 unbroken name");
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
