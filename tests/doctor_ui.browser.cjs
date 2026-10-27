// Real app regression. Start Doctor with an external scratch --checks-dir.
// node tests/doctor_ui.browser.cjs http://127.0.0.1:18875 [evidence-directory]
// Uses externally available Playwright/browser; installs no product dependency.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");
const { captureFailure, browserOptions } = require("./browser-qa-helpers.cjs");

async function main() {
  const base = process.argv[2];
  const evidence = process.argv[3];
  assert.ok(base, "Supply an isolated Doctor URL");
  if (evidence) fs.mkdirSync(evidence, { recursive: true });
  const browser = await chromium.launch(browserOptions());
  const failures = [];
  const observations = [];
  function check(label, test) {
    try { test(); } catch (error) { failures.push(`${label}: ${error.message}`); }
  }
  async function capture(page, name) {
    if (evidence) await page.screenshot({ path: path.join(evidence, `${name}.png`) });
  }
  try {
    for (const lang of ["zh", "en"]) {
      const page = await browser.newPage({ viewport: { width: 375, height: 812 } });
      await page.goto(`${base}/?lang=${lang}`);
      await page.locator(".home .primary-action").waitFor();
      assert.equal(await page.locator(".home .primary-action").getAttribute("href"), `/projects.html?lang=${lang}`, "the primary entry starts the project workflow");
      assert.equal(await page.locator(".home .primary-action").count(), 1, "historical paths must not compete as primary actions");
      const home = await page.locator(".home .primary-action").evaluate((button) => {
        const r = button.getBoundingClientRect();
        return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, scroll: window.scrollY,
          bodyFont: getComputedStyle(document.body).fontSize,
          explanationTop: button.parentElement.querySelector("p:not(.kicker)").getBoundingClientRect().top,
          shell: !!document.querySelector(".app-header .brand") };
      });
      observations.push({ lang, home });
      check(`${lang} home main action`, () => {
        assert.ok(home.top >= 0 && home.bottom <= 812 && home.left >= 0 && home.right <= 375);
        assert.equal(home.scroll, 0);
        assert.ok(home.explanationTop >= home.bottom);
        assert.ok(parseFloat(home.bodyFont) >= 16);
        assert.equal(home.shell, true);
      });
      await capture(page, `${lang}-375-home`);
      await page.goto(`${base}/?lang=${lang}#/fixture/member-evidence/first`);
      await page.locator(".open-items").waitFor();
      const links = page.locator('.open-items a[href*="/item/"]');
      assert.equal(await links.count(), 8);
      const jumpExists = await page.locator(".results-jump").count();
      check(`${lang} example jump exists`, () => assert.equal(jumpExists, 1));
      await links.first().click();
      const itemHash = new URL(page.url()).hash;
      await page.locator(".next-step").waitFor();
      const itemTitle = await page.locator("main h1").innerText();
      await page.getByRole("button", { name: lang === "zh" ? "English" : "中文", exact: true }).click();
      await page.waitForURL((url) => url.searchParams.get("lang") === (lang === "zh" ? "en" : "zh"));
      await page.locator(".next-step").waitFor();
      assert.equal(new URL(page.url()).hash, itemHash);
      assert.equal(await page.locator("main h1").innerText(), itemTitle);
      await capture(page, `${lang}-375-example-item-locale`);
      await page.close();
    }
    const setup = await browser.newPage();
    await setup.goto(`${base}/?lang=en#/local`);
    await setup.locator("#local-files").setInputFiles(path.resolve(__dirname, "../data/raw/Building-Hvac.ifc"));
    await setup.locator("#local-discipline-0").selectOption("HVAC");
    await setup.getByRole("button", { name: "See the scope of the check", exact: true }).click();
    await setup.getByRole("button", { name: "Run the check", exact: true }).click();
    await setup.locator("#workspace-filter").waitFor();
    const resultRoute = new URL(setup.url()).hash;
    await setup.close();
    for (const width of [375, 1280]) {
      for (const lang of ["zh", "en"]) {
        const page = await browser.newPage({ viewport: { width, height: width === 375 ? 812 : 900 } });
        await page.goto(`${base}/?lang=${lang}${resultRoute}`);
        await page.locator("#workspace-filter").fill("house");
        await page.locator(".c-name a").filter({ hasText: "house fireplace cap" }).click();
        await page.locator(".ws-detail h2").waitFor();
        const detailRoute = new URL(page.url()).hash;
        await page.getByRole("button", { name: lang === "zh" ? "English" : "中文", exact: true }).click();
        await page.waitForURL((url) => url.searchParams.get("lang") === (lang === "zh" ? "en" : "zh"));
        await page.locator(".ws-detail h2").waitFor();
        assert.equal(new URL(page.url()).hash, detailRoute);
        assert.equal(await page.locator(".ws-detail h2").innerText(), "house fireplace cap");
        await page.getByRole("button", { name: lang === "zh" ? "English" : "中文", exact: true }).click();
        const unusedHandoff = await page.evaluate(() => sessionStorage.getItem("doctor.ui.language-handoff"));
        check(`${lang}/${width} current language stores no query`, () => assert.equal(unusedHandoff, null));
        const selected = await page.locator(".ws-detail").evaluate((detail) => ({
          top: detail.querySelector("h2").getBoundingClientRect().top,
          query: document.querySelector("#workspace-filter").value,
          overflow: getComputedStyle(detail).overflowY,
          maxHeight: getComputedStyle(detail).maxHeight,
          listVisible: document.querySelector(".ws-list").getClientRects().length > 0,
          url: location.href,
          sourceVisible: !!detail.querySelector(".input-identity"),
        }));
        observations.push({ lang, width, selected });
        check(`${lang}/${width} locale query`, () => assert.equal(selected.query, "house"));
        check(`${lang}/${width} document scroll`, () => assert.equal(selected.maxHeight, "none"));
        check(`${lang}/${width} mobile detail`, () => assert.equal(selected.listVisible, width > 700));
        check(`${lang}/${width} input identity`, () => assert.equal(selected.sourceVisible, true));
        assert.ok(!selected.url.includes("house"));
        await capture(page, `${lang}-${width}-detail-locale`);
        const backExists = await page.locator(".ws-back").count();
        check(`${lang}/${width} return control`, () => assert.equal(backExists, 1));
        if (backExists) {
          await page.locator(".ws-back").click();
          await page.locator("#workspace-filter").waitFor();
          // Desktop detail already contains a visible filter. Wait for the
          // hash route's actual focus handoff, not for that pre-existing field.
          await page.waitForFunction(() =>
            document.activeElement?.matches('.c-name a[aria-current="true"]'));
          const returned = await page.evaluate(() => ({ query: document.querySelector("#workspace-filter").value,
            focus: document.activeElement.textContent, current: document.activeElement.getAttribute("aria-current") }));
          assert.equal(returned.query, "house");
          assert.equal(returned.focus, "house fireplace cap");
          assert.equal(returned.current, "true");
          await capture(page, `${lang}-${width}-return`);
        }
        await page.close();
      }
    }
  } catch (error) { await captureFailure(browser, evidence, error); throw error; }
  finally {
    await browser.close();
    if (evidence) fs.writeFileSync(path.join(evidence, "observations.json"), JSON.stringify(observations, null, 2) + "\n");
  }
  console.log(JSON.stringify(observations, null, 2));
  assert.deepEqual(failures, [], failures.join("\n"));
  console.log("PASS: approved UI real-route shell, item locale, local query/detail/return matrix");
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
