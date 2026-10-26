import { h } from "./dom.js";
import { LANG } from "./i18n.js";
import { languageSwitch } from "./language.js";
import { W } from "./review-words.js";
import { P } from "./projects-words.js";
import { createProjectReview } from "./projects-review.js";
import { requestJSON } from "./projects-api.js";
import { createPurposeReview } from "./review-purpose.js";
import { E } from "./enterprise-words.js";

document.documentElement.lang = LANG === "en" ? "en" : "zh-CN";
document.title = `BIM Doctor · ${W.title}`;
const state = { report: null, selected: null, element: null, status: "ERROR", model: "", query: "", limit: 100, busy: false, ai: false, geometryReady: false };
let viewer = null;
let controller = null;
let adviceController = null;
let requestNumber = 0;
let retryLoad = null;
let activeImport = null;
function cancelOnDeparture() {
  const job = activeImport;
  if (!job || job.terminal) return;
  job.cancelRequested = true;
  // Leaving cannot await confirmation. The server's hard deadline remains the fallback.
  fetch("/api/review/imports/cancel", { method: "POST", keepalive: true, headers: { "Content-Type": "application/json" }, body: JSON.stringify({ job_id: job.id }) }).catch(() => {});
}
window.addEventListener("pagehide", cancelOnDeparture);
document.addEventListener("click", event => {
  if (event.defaultPrevented || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  const target = event.target.closest(".language-switch button, a[href]");
  if (!target || target.hasAttribute("download") || target.target === "_blank") return;
  if (target.matches(".language-switch button")) { if (target.getAttribute("aria-pressed") !== "true") cancelOnDeparture(); return; }
  const destination = new URL(target.href, location.href);
  if (destination.origin !== location.origin || destination.pathname !== location.pathname || destination.search !== location.search) cancelOnDeparture();
});
const number = n => Number(n || 0).toLocaleString(LANG === "en" ? "en" : "zh-CN");
const value = v => v === null || v === undefined || v === "" ? W.unknown : typeof v === "object" ? JSON.stringify(v) : String(v);
const button = (label, handler, cls = "") => h("button", { type: "button", class: cls, onclick: handler }, label);
const label = (name, control) => h("label", {}, h("span", {}, name), control);
const badge = status => h("span", { class: `review-verdict status-${String(status).toLowerCase()}` }, String(status));
const displayedStatus = finding => finding.status === "FAIL" && finding.severity === "INFO" ? "INFO" : finding.status;
const fileInput = h("input", { id: "review-file", type: "file", accept: ".ifc", "aria-label": W.input });
fileInput.addEventListener("change", () => { const file = fileInput.files[0]; fileInput.value = ""; if (file) importFile(file); });
const demoButton = button(W.demo, () => loadDemo(), "review-primary");
const importButton = button(W.import, () => fileInput.click());
const cancelButton = button(W.cancel, () => cancelLoad(), "quiet");
cancelButton.hidden = true;
const message = h("span", {}, W.idle);
const recovery = button(W.retry, () => retryLoad?.(), "quiet");
recovery.hidden = true;
const statusbar = h("div", { class: "review-status", role: "status", "aria-live": "polite" }, h("span", { class: "status-dot", "aria-hidden": "true" }), message, cancelButton, recovery);
const stats = h("div", { class: "review-stats", "aria-label": W.checks });
const sourceName = h("span", { class: "review-source" }, W.sample);
const sourceDisclosure = h("details", { class: "review-provenance" }, h("summary", {}, W.sourceDetails), h("div", { id: "review-source-records" }, W.local));
const modelSelect = h("select", { id: "review-model" }, h("option", { value: "" }, W.allModels));
const statusSelect = h("select", { id: "review-status-filter" }, [ ["ERROR", W.errors], ["INFO", W.information], ["FAIL", W.fail], ["", W.all], ["PASS", W.pass], ["NOT_APPLICABLE", W.na] ].map(([v, t]) => h("option", { value: v }, t)));
const search = h("input", { type: "search", id: "review-search", placeholder: W.search, autocomplete: "off" });
const clearSearch = button("×", () => { search.value = ""; state.query = ""; renderList(); search.focus(); }, "review-clear");
clearSearch.setAttribute("aria-label", W.clear); clearSearch.hidden = true;
const listCount = h("p", { class: "review-list-count", "aria-live": "polite" });
const list = h("div", { class: "review-findings", id: "review-findings" });
const outside = h("p", { class: "review-outside" }, W.selectedOutside); outside.hidden = true;
const detail = h("div", { class: "review-detail-content", id: "review-detail-content" }, h("div", { class: "review-detail-empty" }, h("span", { class: "review-crosshair", "aria-hidden": "true" }, "+"), h("p", {}, W.select)));
const viewport = h("div", { class: "review-canvas", id: "review-viewport", "aria-label": W.view });
const webglEvents = [];
for (const type of ["webglcontextcreationerror", "webglcontextlost"]) viewport.addEventListener(type, event => {
  const diagnostic = { type, message: event.statusMessage || "", at: new Date().toISOString() };
  webglEvents.push(diagnostic); if (webglEvents.length > 10) webglEvents.shift();
  console.error("BIM Doctor WebGL", diagnostic);
  if (type === "webglcontextlost" && state.report) {
    geometryFailure(new Error(event.statusMessage || type), "webgl_context");
    message.textContent = W.geometryError; statusbar.classList.add("has-error");
  }
}, true);
const viewOverlay = h("div", { class: "review-view-overlay" }, h("div", { class: "review-orbit-mark", "aria-hidden": "true" }, "IFC"), h("h2", {}, W.intro), h("p", {}, W.idleHint));
const viewNote = h("span", {}, W.units);
const visibleCount = h("span", {}, "");
const selectionLabel = h("span", { class: "review-selection-label" }, W.select);
const focusButton = button(W.focus, () => viewer?.focus());
const isolateButton = button(W.isolate, () => { if (viewer) { const isolated = viewer.isolate(); isolateButton.textContent = isolated ? W.isolated : W.isolate; isolateButton.setAttribute("aria-pressed", String(isolated)); refreshVisible(); } });
isolateButton.setAttribute("aria-pressed", "false");
const fitButton = button(W.fit, () => viewer?.fit());
const resetButton = button(W.reset, () => { viewer?.reset(); isolateButton.textContent = W.isolate; isolateButton.setAttribute("aria-pressed", "false"); refreshVisible(); });
const viewTools = [focusButton, isolateButton, fitButton, resetButton];
const viewControls = [
  button("+", () => viewer?.zoom(0.8)), button("−", () => viewer?.zoom(1.25)),
  button("↶", () => viewer?.rotate(Math.PI / 8)), button("↷", () => viewer?.rotate(-Math.PI / 8)),
  button(W.top, () => viewer?.fit(true)), button(W.iso, () => viewer?.fit()),
];
[W.zoomIn, W.zoomOut, W.rotateLeft, W.rotateRight, W.top, W.iso].forEach((name, i) => { viewControls[i].setAttribute("aria-label", name); viewControls[i].title = name; });
const aiStatus = h("span", { class: "review-ai-status" }, W.aiOff);
const projectReview = createProjectReview({ getReport: () => state.report, onSaved: () => renderDetail() });
const purposeReview = createPurposeReview(key => {
  state.selected = null; state.element = state.report?.elements.find(item => item.element_key === key) || null;
  selectionChanged();
});
document.querySelector("#review-root").append(
  h("header", { class: "review-header" }, h("a", { class: "brand", href: `/?lang=${LANG}` }, h("span", { class: "brand-mark", "aria-hidden": "true" }, "BD"), "BIM Doctor"),
    h("nav", { class: "review-nav", "aria-label": W.navigation }, h("a", { href: `/projects.html?lang=${LANG}` }, P.nav), h("a", { href: `/review.html?lang=${LANG}`, "aria-current": "page" }, W.workspace), h("a", { href: `/?lang=${LANG}` }, W.home)), languageSwitch()),
  h("main", { id: "main", class: "review-main", tabindex: "-1" },
    h("section", { class: "review-heading" }, h("div", {}, h("p", { class: "review-eyebrow" }, "IFC / MODEL REVIEW"), h("h1", {}, W.title), h("p", { class: "review-subtitle" }, W.introBody)),
      h("div", { class: "review-load-actions" }, demoButton, importButton, fileInput, h("span", { class: "review-file-hint" }, W.size))),
    h("section", { class: "review-overview" }, h("div", { class: "review-source-block" }, h("span", { class: "review-overline" }, W.source), sourceName), stats, aiStatus),
    projectReview.context, projectReview.panel, purposeReview.context,
    statusbar,
    h("div", { class: "review-workspace" },
      h("aside", { class: "review-left", "aria-label": W.models }, h("div", { class: "review-panel-heading" }, h("h2", {}, W.models), h("span", { class: "review-panel-index" }, "IFC")),
        h("div", { class: "review-filters" }, label(W.model, modelSelect), label(W.status, statusSelect), label(W.search, h("span", { class: "review-search-wrap" }, search, clearSearch))),
        listCount, outside, list),
      h("section", { class: "review-view", "aria-label": W.view }, h("div", { class: "review-view-toolbar" }, h("h2", {}, W.view), h("div", { class: "review-view-actions" }, viewTools)),
        h("div", { class: "review-stage" }, viewport, viewOverlay, h("div", { class: "review-view-controls", "aria-label": W.keyboard }, viewControls), h("div", { class: "review-view-legend" }, W.legend)),
        h("div", { class: "review-selection-bar" }, h("span", { class: "selection-dot", "aria-hidden": "true" }), selectionLabel),
        h("footer", { class: "review-view-footer" }, viewNote, visibleCount), h("p", { class: "review-orbit-hint" }, W.orbit)),
      h("aside", { class: "review-right", "aria-label": W.details }, h("div", { class: "review-panel-heading" }, h("h2", {}, W.details), h("span", { class: "review-panel-index", "aria-hidden": "true" }, "↗")), detail)), sourceDisclosure));

let composing = false;
search.addEventListener("compositionstart", () => { composing = true; });
search.addEventListener("compositionend", () => { composing = false; state.query = search.value; state.limit = 100; renderList(); });
search.addEventListener("input", () => { if (!composing) { state.query = search.value; state.limit = 100; renderList(); } });
modelSelect.addEventListener("change", () => { state.model = modelSelect.value; state.limit = 100; viewer?.filter(state.model); renderList(); refreshVisible(); });
statusSelect.addEventListener("change", () => { state.status = statusSelect.value; state.limit = 100; renderList(); });
function refreshVisible() { visibleCount.textContent = viewer && state.geometryReady ? `${W.visible}: ${number(viewer.visibleCount())}` : ""; }
function setBusy(busy, text) {
  const unresolved = activeImport && !activeImport.terminal;
  state.busy = busy; demoButton.disabled = importButton.disabled = busy || !!unresolved; cancelButton.hidden = !busy && !unresolved;
  cancelButton.disabled = false;
  statusbar.setAttribute("aria-busy", String(busy)); message.textContent = text; recovery.hidden = true;
}
async function json(url, options = {}) {
  return requestJSON(url, options);
}
function showError(text) { message.textContent = `${W.failed}: ${text} ${W.errorHint}`; statusbar.classList.add("has-error"); recovery.hidden = !retryLoad; }
function loadDemo() { return loadReport(() => json("/api/review/demo", { signal: controller.signal }), { fresh: true }); }
function importFile(file) {
  if (!/\.ifc$/i.test(file.name) || !file.size) { showError(W.invalid); return; }
  if (file.size > 50 * 1024 * 1024) { showError(W.tooLarge); return; }
  const job = { file, id: crypto.randomUUID(), submitted: false, cancelRequested: false, cancelSent: false };
  return loadReport(() => importReport(job), { fresh: true, importJob: job });
}
async function sendCancel(job) {
  if (!job.id || job.cancelSent) return;
  job.cancelSent = true;
  try {
    const status = await json("/api/review/imports/cancel", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ job_id: job.id }) });
    if (status.state === "cancelled") { job.confirmedCancelled = true; job.finished = true; job.terminal = true; job.controller?.abort(); }
    return status;
  }
  catch (error) { job.cancelSent = false; throw error; }
}
function cancelLoad() {
  if (!activeImport) { controller?.abort(); return; }
  const job = activeImport;
  job.cancelRequested = true;
  if (!state.busy) loadReport(() => importReport(job), { fresh: true, importJob: job });
  cancelButton.disabled = true; message.textContent = W.cancelling;
  sendCancel(job).catch(error => {
    if (activeImport !== job) return;
    cancelButton.disabled = false; message.textContent = `${W.cancelUnconfirmed} ${error.message}`;
  });
}
function importProgress(job, status) {
  if (activeImport !== job) return;
  if (job.cancelRequested || status.state === "cancelling") { message.textContent = W.cancelling; return; }
  const stages = { queued: W.queued, uploading: W.uploading, starting: W.starting, parsing: W.reading, checking: W.checking, tessellating: W.geometryLoading, serializing: W.serializing, publishing: W.importSaving, complete: W.resultsLoading };
  const stage = stages[status.stage] || (status.state === "queued" ? W.queued : W.importing);
  const measured = status.stage === "tessellating" && Number.isFinite(status.completed) && Number.isFinite(status.total) && status.total > 0;
  message.textContent = `${stage}${measured ? ` · ${W.processed}: ${number(status.completed)} / ${number(status.total)}` : ""}`;
}
function pollDelay(signal) {
  return new Promise((resolve, reject) => {
    const abort = () => { clearTimeout(timer); reject(new DOMException("Aborted", "AbortError")); };
    const timer = setTimeout(() => { signal.removeEventListener("abort", abort); resolve(); }, 500);
    if (signal.aborted) abort(); else signal.addEventListener("abort", abort, { once: true });
  });
}
async function importReport(job) {
  const signal = controller.signal;
  if (job.finished) Object.assign(job, { id: crypto.randomUUID(), submitted: false, cancelRequested: false, cancelSent: false, finished: false, terminal: false, confirmedCancelled: false });
  job.controller = controller;
  activeImport = job;
  try {
    const submit = async () => {
      job.submitted = true; job.terminal = false;
      try { return await json(`/api/review/imports?filename=${encodeURIComponent(job.file.name)}&job=${encodeURIComponent(job.id)}`, { method: "POST", headers: { "Content-Type": "application/octet-stream" }, body: job.file, signal }); }
      catch (error) { if (error.status >= 400 && error.status < 500) job.terminal = true; throw error; }
    };
    message.textContent = W.uploading;
    let status;
    if (!job.submitted) status = await submit();
    else {
      try { status = await json(`/api/review/imports?job=${encodeURIComponent(job.id)}`, { signal }); }
      catch (error) { if (error.status === 404) status = await submit(); else throw error; }
    }
    if (status.job_id !== job.id) throw new Error(W.invalidJob);
    while (true) {
      if (signal.aborted) throw new DOMException("Aborted", "AbortError");
      if (job.cancelRequested && !job.cancelSent) await sendCancel(job);
      importProgress(job, status);
      if (status.state === "succeeded") {
        job.terminal = true;
        if (job.cancelRequested) throw Object.assign(new Error(W.cancelTooLate), { name: "ImportDiscarded" });
        message.textContent = W.resultsLoading;
        return await json(`/api/review/report?review=${encodeURIComponent(status.review_id)}`, { signal });
      }
      if (["cancelled", "timed_out", "failed"].includes(status.state)) job.finished = job.terminal = true;
      if (status.state === "cancelled") throw Object.assign(new Error(W.cancelled), { name: "ImportCancelled" });
      if (status.state === "timed_out") throw new Error(W.importTimedOut);
      if (status.state === "failed") throw new Error(typeof status.error === "string" ? status.error : status.error?.message || W.failed);
      if (!["queued", "running", "cancelling"].includes(status.state)) throw new Error(W.invalidJob);
      await pollDelay(signal);
      status = await json(`/api/review/imports?job=${encodeURIComponent(job.id)}`, { signal });
    }
  } catch (error) {
    if (job.confirmedCancelled) throw Object.assign(new Error(W.cancelled), { name: "ImportCancelled" });
    if (signal.aborted) sendCancel(job).catch(() => {});
    throw error;
  } finally {
    // A lost HTTP response does not mean the worker stopped. Keep this page's
    // ownership so retry and pagehide can still address that exact job.
    if (activeImport === job && job.terminal) activeImport = null;
  }
}
async function settleOwnedImport(job, signal) {
  job.cancelRequested = true; cancelButton.disabled = true; message.textContent = W.cancelling;
  let status = await sendCancel(job);
  while (!["succeeded", "failed", "cancelled", "timed_out"].includes(status?.state)) {
    if (!job.cancelSent) {
      status = await sendCancel(job);
      if (["succeeded", "failed", "cancelled", "timed_out"].includes(status?.state)) break;
    }
    await pollDelay(signal);
    status = await json(`/api/review/imports?job=${encodeURIComponent(job.id)}`, { signal });
  }
  job.terminal = true;
  if (activeImport === job) activeImport = null;
}
async function loadReport(getReport, { fresh = false, importJob = null } = {}) {
  const previousImport = activeImport;
  controller?.abort(); controller = new AbortController();
  const current = ++requestNumber;
  retryLoad = () => loadReport(getReport, { fresh, importJob });
  setBusy(true, W.loading); statusbar.classList.remove("has-error");
  try {
    if (previousImport && previousImport !== importJob && !previousImport.terminal) await settleOwnedImport(previousImport, controller.signal);
    if (current !== requestNumber) return;
    cancelButton.disabled = false;
    const loaded = await getReport();
    const report = loaded.report || loaded;
    if (current !== requestNumber) return;
    adviceController?.abort();
    state.report = report; state.selected = null; state.element = null; state.geometryReady = false;
    state.model = ""; state.limit = 100;
    state.status = report.summary.errors > 0 ? "ERROR" : report.summary.information > 0 ? "INFO" : report.summary.passed > 0 ? "PASS" : "";
    const requestedFinding = fresh ? null : report.findings.find(f => f.finding_id === new URL(location.href).searchParams.get("finding"));
    if (requestedFinding) state.status = requestedFinding.status === "FAIL" ? requestedFinding.severity || "FAIL" : requestedFinding.status;
    state.query = ""; search.value = ""; statusSelect.value = state.status;
    projectReview.useReport(report, loaded.revision ? loaded : null);
    const url = new URL(location.href); url.searchParams.set("review", report.review_id);
    if (fresh) { url.searchParams.delete("finding"); url.searchParams.delete("assessment"); url.searchParams.delete("purpose_finding"); }
    if (loaded.revision) { url.searchParams.set("revision", loaded.revision.revision_id); url.searchParams.set("project", loaded.revision.project_id); url.searchParams.set("model", loaded.revision.model_id); }
    else url.searchParams.delete("revision");
    history.replaceState(null, "", url);
    await purposeReview.load(report, { fresh, signal: controller.signal });
    if (current !== requestNumber) return;
    statusSelect.closest("label").hidden = purposeReview.active();
    renderReport();
    const geometryReady = await loadGeometry(current);
    if (current === requestNumber) {
      setBusy(false, geometryReady ? W.loaded : W.geometryError);
      statusbar.classList.toggle("has-error", !geometryReady);
    }
  } catch (error) {
    if (current !== requestNumber) return;
    const cancelled = ["AbortError", "ImportCancelled", "ImportDiscarded"].includes(error.name);
    setBusy(false, error.name === "ImportDiscarded" ? error.message : cancelled ? W.cancelled : W.failed);
    if (state.report && !state.geometryReady && error.name === "AbortError") viewOverlay.replaceChildren(h("p", {}, W.cancelled), button(W.retry, () => { controller = new AbortController(); loadGeometry(); }));
    if (!cancelled) showError(error.message);
  }
}
async function loadGeometry(current = requestNumber) {
  message.textContent = W.geometryLoading; viewOverlay.hidden = false;
  viewOverlay.replaceChildren(h("p", {}, W.geometryLoading));
  let phase = "geometry_request";
  let requestId = null;
  try {
    const data = await json(`/api/review/geometry?review=${encodeURIComponent(state.report.review_id)}`, { signal: controller.signal, onResponse: response => { requestId = response.requestId; } });
    if (current !== requestNumber) return;
    phase = "viewer_initialize";
    if (!viewer) { const { createViewer } = await import("./review-viewer.js"); viewer = createViewer(viewport, key => selectElement(key)); }
    if (current !== requestNumber) return;
    phase = "viewer_load";
    const count = viewer.load(data, state.report); state.geometryReady = true;
    viewOverlay.hidden = count > 0;
    if (!count) viewOverlay.replaceChildren(h("p", {}, W.emptyGeometry));
    if (state.element) viewer.select(state.element.element_key);
    const geometryNote = detail.querySelector(".review-geometry-note");
    if (state.element && viewer.has(state.element.element_key)) geometryNote?.remove();
    updateViewButtons(); refreshVisible();
    return true;
  } catch (error) {
    if (current !== requestNumber) return false;
    if (error.name === "AbortError") throw error;
    geometryFailure(error, error.responsePhase === "decode" ? "geometry_decode" : phase, error.requestId || requestId);
    return false;
  }
}
function geometryFailure(error, phase, requestId = null) {
    const diagnostic = { phase, request_id: requestId, name: error.name, message: error.message, webgl_events: [...webglEvents] };
    console.error("BIM Doctor geometry", diagnostic, error);
    viewOverlay.hidden = false;
    viewOverlay.replaceChildren(h("h2", {}, W.geometryError), h("p", {}, W.fullReport), button(W.retry, () => {
      controller = new AbortController(); loadGeometry().then(ready => { message.textContent = ready ? W.loaded : W.geometryError; statusbar.classList.toggle("has-error", !ready); });
    }), h("details", { class: "review-geometry-error-details" }, h("summary", {}, W.technical), h("pre", {}, JSON.stringify(diagnostic, null, 2))));
    state.geometryReady = false; updateViewButtons();
}
function renderReport() {
  const report = state.report;
  sourceName.textContent = report.source.filename || W.sample;
  const purposeSummary = purposeReview.summary();
  const summaryStats = purposeReview.active() ? [[report.summary.elements, W.elements], [report.summary.renderable, W.renderable], [purposeSummary?.scope_count, E.scopeCount], [purposeSummary?.counts ? Object.values(purposeSummary.counts).reduce((sum, count) => sum + count, 0) : null, E.observations]] : [[report.summary.elements, W.elements], [report.summary.renderable, W.renderable], [report.summary.errors, W.errors], [report.summary.information, W.information]];
  stats.replaceChildren(...summaryStats.map(([n, title]) => h("div", { class: "review-stat" }, h("strong", {}, n == null ? "—" : number(n)), h("span", {}, title))));
  modelSelect.replaceChildren(h("option", { value: "" }, W.allModels), ...report.models.map(m => h("option", { value: m.model_key }, m.name || m.model_key)));
  modelSelect.value = "";
  const records = document.querySelector("#review-source-records");
  records.replaceChildren(h("p", {}, value(report.source.attribution)), h("p", {}, W.local), ...report.models.map(m => h("div", {}, h("strong", {}, m.name || m.model_key), h("p", {}, `${W.discipline}: ${value(m.discipline)}`), h("code", {}, `SHA-256 ${value(m.sha256)}`))));
  renderList();
  if (purposeReview.active()) { renderDetail(); updateViewButtons(); return; }
  const requested = report.findings.find(f => f.finding_id === new URL(location.href).searchParams.get("finding"));
  const first = requested || matching()[0] || report.findings[0];
  if (first) selectFinding(first.finding_id); else if (report.elements[0]) selectElement(report.elements[0].element_key);
}
function matching() {
  if (!state.report) return [];
  const elements = new Map(state.report.elements.map(e => [e.element_key, e]));
  const query = state.query.trim().toLocaleLowerCase();
  return state.report.findings.filter(f => {
    const e = elements.get(f.element_key) || {};
    const statusMatches = !state.status || String(f.status).toUpperCase() === state.status || ["ERROR", "INFO"].includes(state.status) && f.severity === state.status && f.status === "FAIL";
    return statusMatches && (!state.model || e.model_key === state.model) && (!query || [e.name, e.ifc_class, e.global_id, e.tag, f.rule_id, f.title].some(v => String(v || "").toLocaleLowerCase().includes(query)));
  });
}
function renderList() {
  clearSearch.hidden = !search.value;
  if (purposeReview.active()) {
    const result = purposeReview.renderList({ query: state.query, model: state.model, limit: state.limit, more: () => { state.limit += 100; renderList(); } });
    list.replaceChildren(...result.nodes); listCount.textContent = `${number(result.count)} ${W.results}`; outside.hidden = !result.outside; return;
  }
  const found = matching();
  listCount.textContent = `${number(found.length)} ${W.results}`;
  outside.hidden = !state.element || found.some(f => f.element_key === state.element.element_key);
  list.replaceChildren();
  if (!state.report) { list.append(h("p", { class: "review-empty" }, W.idleHint)); return; }
  if (!found.length) { list.append(h("div", { class: "review-empty" }, h("p", {}, W.noResults), button(W.clearFilters, () => { state.query = ""; state.model = ""; state.status = ""; search.value = ""; modelSelect.value = ""; statusSelect.value = ""; viewer?.filter(""); renderList(); refreshVisible(); }, "quiet"))); return; }
  const elements = new Map(state.report.elements.map(e => [e.element_key, e]));
  const visible = found.slice(0, state.limit);
  const selectedIndex = found.findIndex(f => f.finding_id === state.selected?.finding_id);
  if (selectedIndex >= state.limit) {
    visible.pop();
    visible.unshift(found[selectedIndex]);
  }
  for (const f of visible) {
    const e = elements.get(f.element_key) || {};
    const selected = state.selected?.finding_id === f.finding_id;
    const row = button("", () => selectFinding(f.finding_id), `review-finding${selected ? " is-selected" : ""}`);
    row.dataset.finding = f.finding_id; row.setAttribute("aria-pressed", String(selected));
    row.append(h("span", { class: "review-finding-top" }, badge(displayedStatus(f)), h("code", {}, f.rule_id)), h("strong", {}, e.name || e.ifc_class || f.title), h("span", { class: "review-finding-title" }, value(f.title)), h("span", { class: "review-finding-meta" }, `${value(e.ifc_class)} · ${value(e.storey)}`));
    list.append(row);
  }
  if (found.length > state.limit) list.append(button(W.more, () => { state.limit += 100; renderList(); }, "quiet review-load-more"));
}
function selectFinding(id) {
  const finding = state.report.findings.find(f => f.finding_id === id); if (!finding) return;
  state.selected = finding; state.element = state.report.elements.find(e => e.element_key === finding.element_key);
  selectionChanged();
}
function selectElement(key) {
  if (purposeReview.active()) { purposeReview.pick(key); return; }
  const e = state.report.elements.find(e => e.element_key === key); if (!e) return;
  state.element = e; state.selected = state.report.findings.find(f => f.element_key === key && String(f.status).toUpperCase() === "FAIL") || state.report.findings.find(f => f.element_key === key) || null;
  selectionChanged();
  const row = [...list.querySelectorAll("[data-finding]")].find(r => r.dataset.finding === state.selected?.finding_id);
  row?.scrollIntoView({ block: "nearest", behavior: "instant" });
}
function selectionChanged() {
  adviceController?.abort();
  viewer?.select(state.element?.element_key);
  selectionLabel.textContent = `${W.selected}: ${state.element?.name || state.element?.ifc_class || W.unknown}`;
  const url = new URL(location.href);
  if (!purposeReview.active() && state.selected) url.searchParams.set("finding", state.selected.finding_id); else url.searchParams.delete("finding");
  history.replaceState(null, "", url);
  renderList(); renderDetail(); updateViewButtons();
}
function updateViewButtons() {
  for (const b of [...viewTools, ...viewControls]) b.disabled = !state.geometryReady;
  focusButton.disabled = isolateButton.disabled = !state.geometryReady || !viewer?.has(state.element?.element_key);
}
function renderDetail() {
  if (purposeReview.active()) {
    detail.replaceChildren(purposeReview.renderDetail());
    if (state.element && state.element.geometry_status !== "renderable" && !viewer?.has(state.element.element_key)) detail.append(h("p", { class: "review-geometry-note" }, W.noGeometry));
    return;
  }
  const e = state.element; const f = state.selected; if (!e) return;
  const model = state.report.models.find(m => m.model_key === e.model_key);
  const facts = [[W.class, e.ifc_class], [W.storey, e.storey]];
  detail.replaceChildren(h("div", { class: "review-object-heading" }, h("span", { class: "review-overline" }, e.ifc_class), h("h3", {}, e.name || e.ifc_class), h("p", {}, model?.name || e.model_key)),
    h("dl", { class: "review-object-facts" }, facts.map(([k, v]) => [h("dt", {}, k), h("dd", {}, value(v))])),
    h("details", { class: "review-identifiers" }, h("summary", {}, "GlobalId / Tag"), h("dl", { class: "review-object-facts" }, [["GlobalId", e.global_id], ["Tag", e.tag]].map(([k, v]) => [h("dt", {}, k), h("dd", {}, value(v))]))));
  if (e.geometry_status !== "renderable" && !viewer?.has(e.element_key)) detail.append(h("p", { class: "review-geometry-note" }, W.noGeometry));
  const elementFindings = state.report.findings.filter(item => item.element_key === e.element_key);
  if (elementFindings.length > 1) {
    const choose = h("select", { "aria-label": W.selectedRule }, elementFindings.map(item => h("option", { value: item.finding_id }, `${displayedStatus(item)} · ${item.rule_id} · ${item.title}`)));
    choose.value = f?.finding_id || ""; choose.addEventListener("change", () => selectFinding(choose.value)); detail.append(label(W.selectedRule, choose));
  }
  if (!f) { detail.append(h("p", {}, W.noFindings)); return; }
  detail.append(projectReview.renderFollowup(f));
  detail.append(h("section", { class: `review-evidence${displayedStatus(f) === "INFO" ? " is-information" : ""}` }, h("div", { class: "review-section-title" }, h("h3", {}, W.evidence), badge(displayedStatus(f))), h("h4", {}, f.title), h("code", { class: "review-rule-id" }, f.rule_id), h("dl", {}, [[W.expected, f.expected], [W.actual, f.actual], [W.reason, f.reason]].map(([k, v]) => [h("dt", {}, k), h("dd", {}, value(v))])), h("p", { class: "review-citation" }, value(f.citation))));
  const adviceBody = h("div", { class: "review-advice-body", "aria-live": "polite" });
  const aiButton = button(W.generate, () => requestAdvice(f, true, adviceBody, aiButton), "review-primary");
  aiButton.hidden = !state.ai;
  detail.append(h("section", { class: "review-advice" }, h("div", { class: "review-section-title" }, h("h3", {}, W.suggestion), h("span", { class: "review-advice-mode" }, W.guidance)), adviceBody, aiButton, h("p", { class: "review-advice-notice" }, state.ai ? W.aiNotice : W.guidanceNotice)));
  detail.insertBefore(detail.querySelector(".review-advice"), detail.querySelector(".review-evidence"));
  requestAdvice(f, false, adviceBody, aiButton);
}
async function requestAdvice(finding, useAi, body, control) {
  adviceController?.abort(); adviceController = new AbortController();
  const signal = adviceController.signal;
  control.disabled = true; if (useAi) control.textContent = W.generating;
  body.setAttribute("aria-busy", "true");
  try {
    const data = await json("/api/review/advice", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ review_id: state.report.review_id, finding_id: finding.finding_id, language: LANG, use_ai: useAi }), signal });
    if (signal.aborted || state.selected?.finding_id !== finding.finding_id) return;
    body.parentElement.querySelector(".review-advice-mode").textContent = data.mode === "ai" ? W.ai : W.guidance;
    const sections = [[W.actions, data.actions], [W.verify, data.verification]]
      .filter(([, items]) => items?.length)
      .map(([title, items]) => h("div", {}, h("h4", {}, title), h(title === W.actions ? "ol" : "ul", {}, items.map(item => h("li", {}, item)))));
    body.replaceChildren(h("p", { class: "review-advice-summary" }, data.summary), ...sections);
    if (data.facts?.length) body.append(h("details", {}, h("summary", {}, W.facts), h("ul", {}, data.facts.map(item => h("li", {}, item)))));
    if (data.citations?.length) body.append(h("p", { class: "review-citation" }, `${W.citations}: `, data.citations.map(c => c.label || c.id).join(" · ")));
    if (data.limitations?.length) body.append(h("details", {}, h("summary", {}, W.limits), h("ul", {}, data.limitations.map(item => h("li", {}, item)))));
  } catch (error) {
    if (error.name !== "AbortError") body.replaceChildren(h("p", { class: "review-inline-error" }, W.adviceError), button(W.retry, () => requestAdvice(finding, useAi, body, control), "quiet"));
  } finally { if (!signal.aborted) { control.disabled = false; control.textContent = W.generate; body.setAttribute("aria-busy", "false"); } }
}
updateViewButtons(); renderList();
json("/api/review/ai").then(data => {
  state.ai = !!data.configured; aiStatus.textContent = state.ai ? `${W.aiReady} · ${data.model || data.provider || "AI"}` : W.aiOff;
  const aiButton = detail.querySelector(".review-advice > .review-primary"); if (aiButton) aiButton.hidden = !state.ai;
  const notice = detail.querySelector(".review-advice-notice"); if (notice) notice.textContent = state.ai ? W.aiNotice : W.guidanceNotice;
}).catch(() => {});
const saved = new URL(location.href).searchParams.get("review");
const revision = new URL(location.href).searchParams.get("revision");
if (revision) loadReport(() => json(`/api/projects/revision?revision=${encodeURIComponent(revision)}`, { signal: controller.signal }));
else if (saved) loadReport(() => json(`/api/review/report?review=${encodeURIComponent(saved)}`, { signal: controller.signal }));
