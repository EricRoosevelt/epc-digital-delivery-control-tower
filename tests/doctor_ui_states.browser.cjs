// Extended real-check and labelled controlled robustness cases for candidate review.
// node tests/doctor_ui_states.browser.cjs URL EVIDENCE_DIR SYNTHETIC_IFC
const assert = require("node:assert/strict");
const path = require("node:path");
const fs = require("node:fs");
const { launchBrowser, captureFailure } = require("./browser-qa-helpers.cjs");

async function main() {
  const [base, evidence, synthetic] = process.argv.slice(2);
  assert.ok(base && evidence && synthetic);
  fs.mkdirSync(evidence, { recursive: true });
  const browser = await launchBrowser(evidence);
  const facts = [];
  async function shot(page, name) {
    const geometry = await page.evaluate(() => ({ width: innerWidth, height: innerHeight, scroll: scrollY,
      client: document.documentElement.clientWidth, content: document.documentElement.scrollWidth,
      verticalOwners: [...document.querySelectorAll("main *")].filter((el) =>
        ["auto", "scroll"].includes(getComputedStyle(el).overflowY) && el.scrollHeight > el.clientHeight + 2
      ).map((el) => el.className),
    }));
    assert.equal(geometry.client, geometry.content, name + " horizontal overflow");
    assert.deepEqual(geometry.verticalOwners, [], name + " internal vertical scroll");
    facts.push({ name, route: new URL(page.url()).hash, ...geometry });
    await page.screenshot({ path: path.join(evidence, name + ".png") });
  }
  async function run(page, files, disciplines) {
    await page.goto(`${base}/?lang=en#/local`);
    await page.locator("#local-files").setInputFiles(files);
    for (let i = 0; i < disciplines.length; i++) await page.locator(`#local-discipline-${i}`).selectOption(disciplines[i]);
    await shot(page, "en-input-" + disciplines.join("-"));
    await page.getByRole("button", { name: "See the scope of the check", exact: true }).click();
    await page.getByRole("button", { name: "Run the check", exact: true }).waitFor();
    await shot(page, "en-scope-" + disciplines.join("-"));
    await page.getByRole("button", { name: "Run the check", exact: true }).click();
    await page.locator("#workspace-filter").waitFor();
    return new URL(page.url()).hash;
  }
  try {
    const setup = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const hvac = path.resolve(__dirname, "../data/raw/Building-Hvac.ifc");
    const architecture = path.resolve(__dirname, "../data/raw/Building-Architecture.ifc");
    const failRoute = await run(setup, [hvac], ["HVAC"]);
    const multiRoute = await run(setup, [hvac, architecture], ["HVAC", "Architecture"]);
    assert.equal(await setup.locator(".ws-list tbody tr").count(), 3);
    const passRoute = await run(setup, [synthetic], ["HVAC"]);
    assert.equal(await setup.locator(".ws-list tbody tr").count(), 2);
    const naRoute = await run(setup, [architecture], ["Architecture"]);
    assert.equal(await setup.locator(".ws-list tbody tr").count(), 1);
    await setup.close();

    for (const lang of ["zh", "en"]) for (const width of [375, 1280]) {
      const page = await browser.newPage({ viewport: { width, height: width === 375 ? 812 : 900 } });
      const prefix = `${lang}-${width}`;
      await page.goto(`${base}/?lang=${lang}#/fixture`);
      await page.locator(".example-list").waitFor(); await shot(page, prefix + "-directory");
      await page.goto(`${base}/?lang=${lang}#/fixture/member-evidence/first`);
      await page.locator(".first-register").first().waitFor();
      await shot(page, prefix + "-first");
      assert.equal(await page.locator(".first-register tbody tr").count(), 8);
      assert.equal(await page.locator(".quiet-items > li").count(), 5);
      assert.ok(await page.locator(".unit-note").isVisible());
      await page.locator(".results-jump").click();
      assert.match(await page.evaluate(() => document.activeElement.textContent), lang === "en" ? /8 items/ : /8 个事项/);
      await shot(page, prefix + "-results-jump");
      await page.locator(".quiet-records > summary").click();
      assert.ok(await page.locator(".quiet-items").isVisible());
      await page.locator(".quiet-records").scrollIntoViewIfNeeded(); await shot(page, prefix + "-quiet-records");
      await page.locator(".quiet-records > summary").click();
      await page.locator(".first-register a.run").filter({ hasText: /查看|See/ }).first().click();
      await page.locator(".next-step").waitFor(); await shot(page, prefix + "-item");
      const follow = page.locator('main a[href*="/recheck/of/"]').first();
      await follow.click(); await page.locator(".next-step").waitFor();
      await shot(page, prefix + "-same-item-recheck");
      if (lang === "en") assert.match(await page.locator("main").innerText(), /changed conclusion does not mean the original condition is met/i);

      await page.goto(`${base}/?lang=${lang}${failRoute}`);
      await page.locator("#workspace-filter").waitFor();
      await page.locator(".c-name a").filter({ hasText: "chimney cover" }).click();
      await page.locator(".locate-jump").click();
      const beforeLocateRoute = new URL(page.url()).hash;
      const locateTop = await page.locator(".locate-part h3").evaluate((el) => el.getBoundingClientRect().top);
      assert.ok(locateTop >= 0 && locateTop < (width === 375 ? 812 : 900));
      await shot(page, prefix + "-locate");
      if (width <= 700) await page.locator(".ws-back").click();
      await page.locator(".c-name a").filter({ hasText: "house fireplace cap" }).click();
      await page.waitForFunction(() => document.querySelector(".ws-detail h2")?.textContent === "house fireplace cap");
      const changedTop = await page.locator(".ws-detail h2").evaluate((el) => el.getBoundingClientRect().top);
      assert.ok(changedTop >= 0 && changedTop < (width === 375 ? 812 : 900));
      assert.notEqual(new URL(page.url()).hash, beforeLocateRoute);
      await shot(page, prefix + "-new-object");
      await page.locator(".ws-back").click();
      await page.locator("#workspace-filter").fill("house");
      await page.locator(".c-name a").filter({ hasText: "house fireplace cap" }).click();
      await page.goBack(); await page.locator("#workspace-filter").waitFor();
      await page.waitForFunction(() => document.activeElement?.matches('.c-name a[aria-current="true"]'));
      assert.equal(await page.locator("#workspace-filter").inputValue(), "house");
      assert.equal(await page.evaluate(() => document.activeElement.textContent), "house fireplace cap");
      await page.locator(".clear-search").click();
      assert.equal(await page.locator("#workspace-filter").inputValue(), "");
      assert.equal(await page.evaluate(() => document.activeElement.id), "workspace-filter");
      await page.locator("#workspace-filter").evaluate((input) => {
        input.dispatchEvent(new CompositionEvent("compositionstart")); input.value = "house";
        input.dispatchEvent(new InputEvent("input", { bubbles: true, isComposing: true }));
      });
      assert.equal(await page.locator(".ws-list tbody tr:visible").count(), 2);
      await page.locator("#workspace-filter").dispatchEvent("compositionend");
      assert.equal(await page.locator(".ws-list tbody tr:visible").count(), 1);
      await page.locator(".clear-search").click();
      await page.locator(".c-name a").filter({ hasText: "chimney cover" }).click();
      await page.waitForFunction(() => document.querySelector(".ws-detail h2")?.textContent === "chimney cover");
      if (width > 700) {
        await page.locator("#workspace-filter").fill("house");
        assert.ok(await page.locator(".out-of-filter").isVisible());
        await page.locator("#workspace-filter").fill("ux-no-match");
        assert.equal(await page.locator(".ws-list tbody tr:visible").count(), 0);
        await shot(page, prefix + "-outside-filter");
        await page.locator(".ws-back").click();
        await page.waitForFunction(() => document.activeElement?.id === "workspace-filter");
        assert.equal(await page.evaluate(() => document.activeElement.id), "workspace-filter");
      }

      for (const [name, route] of [["multi-file", multiRoute], ["synthetic-pass-long", passRoute], ["model-na", naRoute]]) {
        await page.goto(`${base}/?lang=${lang}${route}`); await page.locator("#workspace-filter").waitFor();
        assert.equal(await page.locator("#workspace-filter").inputValue(), "");
        await shot(page, prefix + "-" + name + "-list");
        await page.locator(".c-name a").last().click(); await page.locator(".ws-detail h2").waitFor();
        assert.ok(await page.locator(".input-identity").isVisible());
        assert.equal(await page.locator(".input-identity").innerText().then((t) => /public sample|公开样例/i.test(t)), false);
        if (name === "synthetic-pass-long") {
          assert.ok(await page.locator(".pass-limits").isVisible());
          assert.equal(await page.locator(".ws-detail .next-step").count(), 0);
          assert.match(await page.locator(".ws-detail h2").innerText(), /SYNTHETIC/);
        }
        if (name === "model-na") {
          assert.equal(await page.locator(".ws-detail .next-step").count(), 0);
          assert.equal(await page.locator(".ws-detail .pass-limits").count(), 0);
          assert.match(await page.locator(".ws-detail").innerText(), /not a pass|不是通过|不等于通过/i);
        }
        await shot(page, prefix + "-" + name + "-detail");
      }
      await page.goto(`${base}/?lang=${lang}#/local`); await page.locator("#local-files").waitFor();
      await page.getByRole("button", { name: lang === "en" ? "See the scope of the check" : "查看检查范围", exact: true }).click();
      await page.locator(".local-steps .refusal").waitFor();
      assert.equal(await page.locator(".ws-list").count(), 0);
      await shot(page, prefix + "-refusal");
      await page.close();
    }
    for (const width of [639, 640, 641, 700, 701]) {
      const page = await browser.newPage({ viewport: { width, height: 812 } });
      await page.goto(`${base}/?lang=en${failRoute}`); await page.locator("#workspace-filter").fill("ux-no-match");
      assert.equal(await page.locator(".ws-list tbody tr:visible").count(), 0);
      await page.locator(".clear-search").click();
      assert.equal(await page.locator(".ws-list tbody tr:visible").count(), 2);
      await page.close();
    }
  } catch (error) { await captureFailure(browser, evidence, error); throw error; } finally {
    await browser.close();
    fs.writeFileSync(path.join(evidence, "states.json"), JSON.stringify(facts, null, 2) + "\n");
  }
  console.log("PASS: real multi-file/PASS/N/A, source identity, example/recheck, object and filter navigation, refusal, scroll, composition, breakpoints");
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
