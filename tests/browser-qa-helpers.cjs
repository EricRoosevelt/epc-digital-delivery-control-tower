const fs = require("node:fs");
const path = require("node:path");
function browserOptions() {
  const channel = process.env.BROWSER_CHANNEL || "msedge";
  return { headless: true, ...(channel === "chromium" ? {} : { channel }) };
}

async function captureFailure(browser, evidence, error) {
  if (!evidence) return;
  fs.mkdirSync(evidence, { recursive: true });
  fs.writeFileSync(path.join(evidence, "failure.json"), JSON.stringify({ error: error.stack || String(error) }, null, 2));
  let index = 0;
  for (const context of browser.contexts()) for (const page of context.pages()) {
    if (!page.isClosed()) await page.screenshot({ path: path.join(evidence, `failure-${++index}.png`), timeout: 5000 }).catch(() => {});
  }
}
module.exports = { captureFailure, browserOptions };
