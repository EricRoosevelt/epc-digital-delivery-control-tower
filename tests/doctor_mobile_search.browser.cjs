// Real-browser regression for UX-01: CSS must not reveal filtered result rows.
// Start doctor/serve.py with a scratch --checks-dir outside the checkout first.
// Run: node tests/doctor_mobile_search.browser.cjs http://127.0.0.1:8765 [evidence-dir]
// Requires an externally installed Playwright and browser; no product dependency.
// BROWSER_CHANNEL can select an installed browser (defaults to Edge on Windows).
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

async function main() {
  const base = process.argv[2];
  assert.ok(base, "Supply the isolated Doctor server URL");
  const evidence = process.argv[3];
  if (evidence) fs.mkdirSync(evidence, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    channel: process.env.BROWSER_CHANNEL || (process.platform === "win32" ? "msedge" : undefined),
  });
  const failures = [];
  const observations = [];
  try {
    const setup = await browser.newPage();
    await setup.goto(`${base}/?lang=en#/local`);
    await setup.locator("#local-files").setInputFiles(
      path.resolve(__dirname, "../data/raw/Building-Hvac.ifc"),
    );
    await setup.locator("#local-discipline-0").selectOption("HVAC");
    await setup.getByRole("button", { name: "See the scope of the check", exact: true }).click();
    await setup.getByRole("button", { name: "Run the check", exact: true }).click();
    await setup.locator("#workspace-filter").waitFor();
    const resultRoute = new URL(setup.url()).hash;
    await setup.close();
    for (const lang of ["zh", "en"]) {
      for (const width of [375, 1280]) {
        const page = await browser.newPage({ viewport: { width, height: width === 375 ? 812 : 900 } });
        await page.goto(`${base}/?lang=${lang}${resultRoute}`);
        await page.locator("#workspace-filter").waitFor();
        for (const [state, query, names] of [
          ["zero", "ux-no-match", []],
          ["single", "house", ["house fireplace cap"]],
          ["clear", "", ["chimney cover", "house fireplace cap"]],
        ]) {
          const input = page.locator("#workspace-filter");
          if (state === "clear") {
            await input.focus();
            await page.keyboard.press(process.platform === "darwin" ? "Meta+A" : "Control+A");
            await page.keyboard.press("Backspace");
            assert.equal(await input.inputValue(), "");
          } else {
            await input.fill(query);
          }
          const snapshot = await page.locator(".ws-list").evaluate((list) => ({
            status: list.querySelector('[role="status"]').textContent,
            emptyVisible: list.querySelector(".note").getClientRects().length > 0,
            rows: [...list.querySelectorAll("tbody tr")].map((row) => ({
              name: row.querySelector(".c-name a").textContent,
              hidden: row.hidden,
              display: getComputedStyle(row).display,
              height: row.getBoundingClientRect().height,
              visible: row.getClientRects().length > 0,
            })),
          }));
          observations.push({ lang, width, state, query, ...snapshot });
          try {
            assert.deepEqual(snapshot.rows.filter((row) => row.visible).map((row) => row.name), names);
            assert.equal(snapshot.status, lang === "en"
              ? `Showing ${names.length} of 2`
              : `显示 ${names.length} 条，共 2 条`);
            assert.equal(snapshot.emptyVisible, names.length === 0);
            for (const row of snapshot.rows.filter((row) => row.hidden)) {
              assert.equal(row.display, "none");
              assert.equal(row.height, 0);
            }
          } catch (error) {
            failures.push(`${lang}/${width}/${state}: ${error.message}`);
          }
          await page.locator(".ws-list").scrollIntoViewIfNeeded();
          if (evidence) {
            await page.screenshot({ path: path.join(evidence, `${lang}-${width}-${state}.png`) });
          }
          if (state === "single") {
            // Keyboard selection opens the matching detail and preserves the filter.
            const selected = page.locator(".c-name a").filter({ hasText: "house fireplace cap" });
            await selected.focus();
            await page.keyboard.press("Enter");
            await page.locator(".ws-detail:not(.empty)").waitFor();
            assert.match(await page.locator(".ws-detail").innerText(), /house fireplace cap/);
            assert.equal(await page.locator("#workspace-filter").inputValue(), "house");
            assert.equal(await page.locator(".ws-list tr.selected a").getAttribute("aria-current"), "true");
            if (width > 700) {
              assert.deepEqual(await page.locator(".ws-list tbody tr:visible .c-name a").allTextContents(), names);
            } else {
              assert.equal(await page.locator(".ws-list").isVisible(), false);
            }
            if (evidence) {
              await page.locator(".ws-detail").scrollIntoViewIfNeeded();
              await page.screenshot({ path: path.join(evidence, `${lang}-${width}-detail.png`) });
            }
            if (width <= 700) {
              await page.locator(".ws-back").click();
              await page.locator("#workspace-filter").waitFor();
              assert.equal(await page.locator("#workspace-filter").inputValue(), "house");
            }
          }
        }
        // Restored rows remain selectable by clicking the row outside its link.
        await page.locator(".ws-list tr").filter({ hasText: "chimney cover" }).locator(".c-status").click();
        await page.waitForFunction(() => document.querySelector(".ws-detail")?.textContent.includes("chimney cover"));
        assert.equal(await page.locator("#workspace-filter").inputValue(), "");
        await page.close();
      }
    }
  } finally {
    await browser.close();
    if (evidence) fs.writeFileSync(path.join(evidence, "observations.json"), JSON.stringify(observations, null, 2) + "\n");
  }
  console.log(JSON.stringify(observations, null, 2));
  assert.deepEqual(failures, [], failures.join("\n"));
  console.log("PASS: zh/en, 375/1280, zero/single/clear, keyboard and row detail selection");
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
