// Controlled job transport around a real public report/mesh. No fake IFC verdicts.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");
const { captureFailure, browserOptions } = require("./browser-qa-helpers.cjs");

async function main() {
  const [base, evidence] = process.argv.slice(2);
  assert.ok(base && evidence);
  fs.mkdirSync(evidence, { recursive: true });
  const browser = await chromium.launch(browserOptions());
  const errors = [];
  const observations = [];
  try {
    for (const lang of ["en", "zh"]) {
      const page = await browser.newPage({ viewport: lang === "en" ? { width: 1440, height: 1000 } : { width: 390, height: 844 } });
      page.on("pageerror", error => errors.push(error.message));
      const leaveAttempts = [];
      page.on("console", message => { if (message.text().startsWith("PUBLIC_QA_KEEPALIVE ")) leaveAttempts.push(JSON.parse(message.text().slice(20))); });
      await page.addInitScript(() => {
        const original = window.fetch;
        window.fetch = function (input, options) {
          if (options?.keepalive && String(input).endsWith("/api/review/imports/cancel")) console.debug("PUBLIC_QA_KEEPALIVE " + JSON.stringify({ job_id: JSON.parse(options.body).job_id, keepalive: options.keepalive }));
          return original.apply(this, arguments);
        };
      });
      const text = (en, zh) => lang === "en" ? en : zh;
      await page.goto(`${base}/review.html?lang=${lang}`);
      await page.getByRole("button", { name: text("Load public example", "载入公共示例"), exact: true }).click();
      await page.locator(".review-status").filter({ hasText: text("Model loaded", "模型已载入") }).waitFor();
      const previousReview = new URL(page.url()).searchParams.get("review");
      const previousSource = await page.locator(".review-source").innerText();
      let mode = "running";
      let posts = 0;
      let cancels = 0;
      let failPoll = false;
      let holdSubmission = false;
      let releaseSubmission = null;
      let submittedId = null;
      let dropSubmission = false;
      let resultReview = previousReview;
      let switching = false;
      const knownIds = new Set();
      const descriptor = id => ({ job_id: id, state: mode, stage: "tessellating", completed: 7, total: 100, review_id: mode === "succeeded" ? resultReview : null, error: mode === "failed" ? "Controlled worker failure" : null });
      await page.route(url => url.pathname === "/api/review/imports", async route => {
        const request = route.request();
        const id = new URL(request.url()).searchParams.get("job");
        if (request.method() === "POST") {
          posts++; submittedId = id;
          knownIds.add(id);
          assert.match(id, /^[0-9a-f-]{36}$/);
          if (dropSubmission) { dropSubmission = false; return route.abort("connectionreset"); }
          if (holdSubmission) await new Promise(resolve => { releaseSubmission = resolve; });
          return route.fulfill({ status: 202, json: { ...descriptor(id), state: "queued", stage: "queued" } });
        }
        if (failPoll) { failPoll = false; return route.fulfill({ status: 503, json: { error: "Controlled polling outage" } }); }
        return route.fulfill({ json: descriptor(id) });
      });
      await page.context().route("**/api/review/imports/cancel", route => { cancels++; if (!switching) mode = "cancelling"; const id = route.request().postDataJSON().job_id; assert.ok(knownIds.has(id)); return route.fulfill({ json: { ...descriptor(id), state: "cancelling" } }); });
      const upload = name => page.locator("#review-file").setInputFiles({ name: `${name}.ifc`, mimeType: "application/octet-stream", buffer: Buffer.from("controlled job transport; real report retained") });
      const kept = async () => {
        assert.equal(new URL(page.url()).searchParams.get("review"), previousReview);
        assert.equal(await page.locator(".review-source").innerText(), previousSource);
        assert.equal(await page.locator(".review-finding").count(), 2);
        assert.match(await page.locator(".review-view-footer").innerText(), /32/);
        assert.equal(await page.getByRole("button", { name: text("Focus element", "聚焦构件"), exact: true }).isEnabled(), true);
      };
      await upload("controlled-cancel");
      await page.locator(".review-status").filter({ hasText: "7 / 100" }).waitFor();
      await kept();
      await page.screenshot({ path: path.join(evidence, `job-${lang}-running.png`) });
      await page.getByRole("button", { name: text("Cancel loading", "取消载入"), exact: true }).click();
      await page.locator(".review-status").filter({ hasText: text("waiting for service confirmation", "等待服务确认") }).waitFor();
      assert.equal(await page.locator(".review-status").getAttribute("aria-busy"), "true", "cancel request is not a terminal confirmation");
      assert.doesNotMatch(await page.locator(".review-status").innerText(), /Loading cancelled|已取消载入/);
      await kept();
      mode = "cancelled";
      await page.locator(".review-status").filter({ hasText: text("Loading cancelled", "已取消载入") }).waitFor();
      assert.equal(cancels, 1);
      assert.equal(await page.locator(".review-status").getAttribute("aria-busy"), "false");
      await kept();
      mode = "running"; holdSubmission = true;
      const pendingUpload = page.waitForRequest(request => request.method() === "POST" && new URL(request.url()).pathname === "/api/review/imports");
      await upload("controlled-cancel-before-ack");
      await pendingUpload;
      const cancellation = page.waitForResponse(response => new URL(response.url()).pathname === "/api/review/imports/cancel");
      await page.getByRole("button", { name: text("Cancel loading", "取消载入"), exact: true }).click();
      await cancellation;
      assert.equal(cancels, 2, "client-generated id permits cancellation before submission acknowledgement");
      mode = "cancelled"; holdSubmission = false; releaseSubmission();
      await page.locator(".review-status").filter({ hasText: text("Loading cancelled", "已取消载入") }).waitFor();
      await kept();
      for (const terminal of ["failed", "timed_out"]) {
        mode = terminal;
        await upload(`controlled-${terminal}`);
        await page.locator(".review-status.has-error").waitFor();
        if (terminal === "timed_out") assert.match(await page.locator(".review-status").innerText(), /timed out and stopped|超时并停止/);
        await kept();
        const beforeRetry = posts;
        mode = "succeeded";
        await page.locator(".review-status").getByRole("button", { name: text("Retry", "重试"), exact: true }).click();
        await page.locator(".review-status").filter({ hasText: text("Model loaded", "模型已载入") }).waitFor();
        assert.equal(posts, beforeRetry + 1, "terminal job retry creates a new import");
      }
      mode = "running"; failPoll = true;
      await upload("controlled-network-retry");
      await page.locator(".review-status.has-error").waitFor();
      await kept();
      const beforeResume = posts;
      mode = "succeeded";
      await page.locator(".review-status").getByRole("button", { name: text("Retry", "重试"), exact: true }).click();
      await page.locator(".review-status").filter({ hasText: text("Model loaded", "模型已载入") }).waitFor();
      assert.equal(posts, beforeResume, "transport retry resumes known job without duplicate work");
      mode = "running"; dropSubmission = true;
      await upload("controlled-lost-submission-response");
      await page.locator(".review-status.has-error").waitFor();
      const beforeLostResponseRetry = posts;
      mode = "succeeded";
      await page.locator(".review-status").getByRole("button", { name: text("Retry", "重试"), exact: true }).click();
      await page.locator(".review-status").filter({ hasText: text("Model loaded", "模型已载入") }).waitFor();
      assert.equal(posts, beforeLostResponseRetry, "lost submission response recovers by client id without re-upload");
      const previousReport = await (await page.request.get(`${base}/api/review/report?review=${previousReview}`)).json();
      const architecture = await (await page.request.post(`${base}/api/review/models?filename=Building-Architecture.ifc`, { headers: { "Content-Type": "application/octet-stream" }, data: fs.readFileSync(path.resolve(__dirname, "../data/raw/Building-Architecture.ifc")) })).json();
      let releaseLateReport;
      let reportEntered;
      const entered = new Promise(resolve => { reportEntered = resolve; });
      await page.route("**/api/review/report?**", route => {
        if (new URL(route.request().url()).searchParams.get("review") !== previousReview) return route.continue();
        reportEntered();
        return new Promise(resolve => { releaseLateReport = async () => { await route.fulfill({ json: previousReport }).catch(() => {}); resolve(); }; });
      });
      switching = true;
      await upload("controlled-late-old-result");
      await entered;
      assert.equal(await page.locator(".review-status").getAttribute("aria-busy"), "true");
      assert.doesNotMatch(await page.locator(".review-status").innerText(), /Model loaded|模型已载入/, "worker completion alone is not a loaded UI");
      resultReview = architecture.review_id;
      await upload("controlled-newer-result");
      await page.locator(".review-source").filter({ hasText: "Building-Architecture.ifc" }).waitFor();
      await page.locator(".review-status").filter({ hasText: text("Model loaded", "模型已载入") }).waitFor();
      await releaseLateReport();
      assert.equal(new URL(page.url()).searchParams.get("review"), architecture.review_id, "late old result cannot overwrite the newer import");
      assert.equal(await page.locator("#review-status-filter").inputValue(), "INFO");
      mode = "running"; switching = false;
      await upload("controlled-leave-page");
      await page.locator(".review-status").filter({ hasText: "7 / 100" }).waitFor();
      const leavingId = submittedId;
      const beforeLeavePosts = posts;
      // Verify event handling while the frame is live; actual unload may drop delivery.
      const leaveCancel = page.context().waitForEvent("request", { predicate: request => new URL(request.url()).pathname === "/api/review/imports/cancel" && request.postDataJSON()?.job_id === leavingId });
      await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent("pagehide", { persisted: false })));
      await leaveCancel;
      const attemptsBeforeNavigation = leaveAttempts.filter(attempt => attempt.job_id === leavingId).length;
      await page.getByRole("button", { name: text("中文", "English"), exact: true }).click();
      await page.locator(".review-status").filter({ hasText: text("模型已载入", "Model loaded") }).waitFor();
      assert.ok(leaveAttempts.some(attempt => attempt.job_id === leavingId && attempt.keepalive), "pagehide attempts a keepalive cancellation for only its own job");
      assert.ok(leaveAttempts.filter(attempt => attempt.job_id === leavingId).length > attemptsBeforeNavigation, "language navigation attempts its own keepalive cancellation, without claiming delivery");
      assert.equal(new URL(page.url()).searchParams.get("review"), architecture.review_id);
      assert.equal(posts, beforeLeavePosts, "language reopening keeps the prior report without re-upload");
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      observations.push(`${lang}: real mesh retained during progress, confirmed cancellation, worker failure, timeout and retry; known-job polling retry avoids re-upload.`);
      await page.screenshot({ path: path.join(evidence, `job-${lang}-language-reopened.png`) });
      await page.close();
    }
    assert.deepEqual(errors, []);
    fs.writeFileSync(path.join(evidence, "import-jobs.json"), JSON.stringify({ observations, errors }, null, 2));
    console.log(JSON.stringify({ passed: true, observations, errors }));
  } catch (error) { await captureFailure(browser, evidence, error); throw error; }
  finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
