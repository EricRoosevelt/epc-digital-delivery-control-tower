const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");
function browserOptions() {
  const channel = process.env.BROWSER_CHANNEL || "msedge";
  return { headless: true, ...(channel === "chromium" ? {} : { channel }) };
}

// QA-only observation. Never record headers, request/response bodies or environment.
async function launchBrowser(evidence) {
  const browser = await chromium.launch(browserOptions());
  if (!evidence) return browser;
  fs.mkdirSync(evidence, { recursive: true });
  const log = path.join(evidence, "browser-diagnostics.jsonl");
  const started = Date.now();
  let sequence = 0, consoleCount = 0;
  const pages = new WeakMap();
  const emit = (phase, data = {}) => fs.appendFileSync(log, JSON.stringify({ ms: Date.now() - started, phase, ...data }) + "\n");
  emit("browser", { version: browser.version() });
  async function snapshot(page, phase) {
    if (page.isClosed()) return;
    try {
      const state = await page.evaluate(() => ({
        url: location.href, readyState: document.readyState, startup_state: document.documentElement.dataset.startupState,
        root_children: document.querySelector("#projects-root, #review-root, main")?.childElementCount,
        stylesheets: [...document.styleSheets].map(sheet => sheet.href),
        startup: window.__doctorStartup,
        navigation: performance.getEntriesByType("navigation").map(entry => ({ url: entry.name, status: entry.responseStatus, domContentLoaded: entry.domContentLoadedEventEnd, load: entry.loadEventEnd })),
      }));
      emit(phase, { page: pages.get(page), ...state });
    } catch (error) { emit("snapshot_error", { page: pages.get(page), message: error.message.slice(0, 500) }); }
  }
  async function observe(page) {
    if (pages.has(page)) return;
    const id = ++sequence; pages.set(page, id);
    const request = r => ({ url: r.url(), method: r.method(), resource: r.resourceType() });
    page.on("request", r => emit("request", { page: id, ...request(r) }));
    page.on("requestfinished", r => emit("requestfinished", { page: id, ...request(r), timing: r.timing() }));
    page.on("requestfailed", r => emit("requestfailed", { page: id, ...request(r), error: r.failure()?.errorText }));
    page.on("response", r => emit("response", { page: id, ...request(r.request()), status: r.status() }));
    page.on("pageerror", error => emit("pageerror", { page: id, message: error.message.slice(0, 1500) }));
    page.on("console", message => {
      if (["error", "warning"].includes(message.type()) && consoleCount++ < 200) emit("console", { page: id, level: message.type(), text: message.text().slice(0, 1500) });
    });
    page.on("domcontentloaded", () => { emit("DOMContentLoaded", { page: id, url: page.url() }); snapshot(page, "dom_state"); });
    page.on("load", () => { emit("load", { page: id, url: page.url() }); snapshot(page, "load_state"); });
    page.on("close", () => emit("page_closed", { page: id }));
    const session = await page.context().newCDPSession(page);
    await session.send("Network.enable");
    const urls = new Map();
    session.on("Network.requestWillBeSent", event => urls.set(event.requestId, event.request.url));
    session.on("Network.loadingFailed", event => emit("cdp_loading_failed", { page: id, url: urls.get(event.requestId), error: event.errorText, blocked: event.blockedReason, cancelled: event.canceled, type: event.type }));
    session.on("Network.loadingFinished", event => urls.delete(event.requestId));
    await page.addInitScript(() => {
      const probe = window.__doctorStartup = { geometryDecode: null, context: [], triangles: 0, firstTriangleSubmission: null, nextFrameAfterTriangle: null };
      const json = Response.prototype.json;
      Response.prototype.json = function (...args) {
        if (!this.url || new URL(this.url).pathname !== "/api/review/geometry") return json.apply(this, args);
        const timing = probe.geometryDecode = { start: performance.now() };
        return json.apply(this, args).then(body => { timing.end = performance.now(); timing.meshes = body?.meshes?.length; return body; }, error => { timing.error = error.name + ": " + error.message.slice(0, 500); throw error; });
      };
      for (const type of ["webglcontextcreationerror", "webglcontextlost"]) document.addEventListener(type, event => probe.context.push({ phase: type, at: performance.now(), message: (event.statusMessage || "").slice(0, 300) }), true);
      const getContext = HTMLCanvasElement.prototype.getContext;
      const wrapped = new WeakSet();
      HTMLCanvasElement.prototype.getContext = function (...args) {
        const start = performance.now();
        const context = getContext.apply(this, args);
        if (!["webgl", "webgl2"].includes(args[0])) return context;
        probe.context.push({ phase: "initialize", start, end: performance.now(), available: !!context });
        if (context && !wrapped.has(context)) {
          wrapped.add(context);
          for (const method of ["drawElements", "drawArrays"]) {
            const draw = context[method];
            context[method] = function (...values) {
              const result = draw.apply(this, values);
              const count = method === "drawElements" ? values[1] : values[2];
              if (values[0] === this.TRIANGLES && count > 0) {
                probe.triangles++;
                if (probe.firstTriangleSubmission === null) { probe.firstTriangleSubmission = performance.now(); requestAnimationFrame(() => { probe.nextFrameAfterTriangle = performance.now(); }); }
              }
              return result;
            };
          }
        }
        return context;
      };
    });
  }
  const newContext = browser.newContext.bind(browser);
  browser.newContext = async (...args) => {
    const context = await newContext(...args);
    const newPage = context.newPage.bind(context);
    context.newPage = async (...values) => { const page = await newPage(...values); await observe(page); return page; };
    return context;
  };
  const newPage = browser.newPage.bind(browser);
  browser.newPage = async (...args) => { const page = await newPage(...args); await observe(page); return page; };
  const close = browser.close.bind(browser);
  browser.close = async (...args) => {
    await Promise.all(browser.contexts().flatMap(context => context.pages()).map(page => snapshot(page, "final_state")));
    return close(...args);
  };
  browser.on("disconnected", () => emit("browser_closed"));
  return browser;
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
module.exports = { captureFailure, browserOptions, launchBrowser };
