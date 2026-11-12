import { h } from "./dom.js";
import { LANG } from "./i18n.js";
import { P } from "./projects-words.js";
import { requestJSON } from "./projects-api.js";

const CHANGES = ["resolved", "remaining", "new", "missing", "not_applicable", "not_comparable"];
const text = value => value === null || value === undefined || value === "" ? P.none : typeof value === "object" ? JSON.stringify(value) : String(value);
const label = (name, control) => h("label", {}, h("span", {}, name), control);
const categoryTitle = (change, severity) => severity === "INFO" && change === "resolved" ? P.infoResolved : severity === "INFO" && change === "remaining" ? P.infoRemaining : severity === "INFO" && change === "new" ? P.infoNew : P[change];
const linkTo = (revision, finding) => `/review.html?lang=${LANG}&revision=${encodeURIComponent(revision)}${finding ? `&finding=${encodeURIComponent(finding)}` : ""}`;

export function comparisonPanel(models) {
  let data = null;
  let controller = null;
  let current = 0;
  let severity = "ERROR";
  let category = "remaining";
  let limit = 100;
  const modelSelect = h("select", { id: "compare-model" }, models.map(m => h("option", { value: m.model_id }, m.name)));
  const before = h("select", { id: "compare-before" });
  const after = h("select", { id: "compare-after" });
  const submit = h("button", { class: "review-primary", type: "submit" }, P.compareAction);
  const message = h("p", { class: "project-form-message", role: "status", "aria-live": "polite" });
  const severityControl = h("div", { class: "project-severity-switch" });
  const categories = h("div", { class: "project-comparison-categories" });
  const results = h("div", { class: "project-comparison-results" });
  const scopeNote = h("p", { class: "project-comparison-scope" });
  const outcome = h("div", { class: "project-comparison-outcome" }, scopeNote, severityControl, categories, results);
  const form = h("form", { class: "project-compare-form", novalidate: true }, label(P.model, modelSelect), label(P.before, before), label(P.after, after), submit);
  const section = h("section", { class: "project-compare project-surface", id: "project-comparison", "aria-label": P.compare }, h("div", { class: "project-section-header" }, h("div", {}, h("p", { class: "review-eyebrow" }, "IFC / RECHECK"), h("h2", {}, P.compare), h("p", { class: "project-muted" }, P.compareSubtitle))), form, message, outcome);

  function setModel(id) {
    controller?.abort(); ++current; data = null; outcome.hidden = true;
    modelSelect.value = id;
    const model = models.find(m => m.model_id === id);
    const revisions = [...(model?.revisions || [])].sort((a, b) => a.number - b.number);
    for (const select of [before, after]) select.replaceChildren(...revisions.map(r => h("option", { value: r.revision_id }, `R${r.number} · ${r.label}`)));
    before.value = revisions.at(-2)?.revision_id || revisions[0]?.revision_id || "";
    after.value = revisions.at(-1)?.revision_id || "";
    submit.disabled = revisions.length < 2; before.disabled = after.disabled = revisions.length < 2;
    message.textContent = revisions.length < 2 ? P.compareEmpty : P.compareChoose;
    message.classList.remove("is-error");
  }
  function renderResults() {
    if (!data) return;
    const rows = data.rows.filter(row => (row.severity || "ERROR") === severity && row.change === category);
    categories.replaceChildren(...CHANGES.map(change => {
      const count = data.rows.filter(row => (row.severity || "ERROR") === severity && row.change === change).length;
      const control = h("button", { type: "button", class: `project-change-count change-${change}`, "aria-pressed": String(category === change), onclick: () => { category = change; limit = 100; renderResults(); } }, h("strong", {}, count), h("span", {}, categoryTitle(change, severity)));
      return control;
    }));
    severityControl.replaceChildren(...[["ERROR", P.errorChecks], ["INFO", P.infoChecks]].map(([key, name]) => h("button", { type: "button", "aria-pressed": String(severity === key), onclick: () => { severity = key; limit = 100; renderResults(); } }, name, h("span", {}, data.rows.filter(row => (row.severity || "ERROR") === key).length))));
    results.replaceChildren(h("div", { class: "project-comparison-heading" }, h("h3", {}, categoryTitle(category, severity)), h("span", { class: "project-muted" }, `${rows.length} ${P.total}`)), h("p", { class: "project-comparison-hint" }, P[`${category}Hint`]));
    if (!rows.length) results.append(h("p", { class: "project-empty-inline" }, P.noChanges));
    const ids = { before: data.before_revision.revision_id, after: data.after_revision.revision_id };
    for (const row of rows.slice(0, limit)) {
      const afterFinding = row.after_finding_id;
      const beforeFinding = row.before_finding_id;
      const target = afterFinding ? h("a", { href: linkTo(ids.after, afterFinding), class: "project-text-link" }, P.openAfter, " ↗") : beforeFinding ? h("a", { href: linkTo(ids.before, beforeFinding), class: "project-text-link" }, P.openBefore, " ↗") : null;
      results.append(h("article", { class: `project-change-row change-${category}` },
        h("div", { class: "project-change-row-heading" }, h("div", {}, h("code", {}, row.rule_id), h("strong", {}, row.after_name || row.before_name || row.global_id || P.element)), target),
        h("dl", { class: "project-observations" }, h("dt", {}, P.beforeValue), h("dd", {}, h("span", { class: "project-raw-status" }, text(row.before_status)), text(row.before_actual)), h("dt", {}, P.afterValue), h("dd", {}, h("span", { class: "project-raw-status" }, text(row.after_status)), text(row.after_actual))),
        h("p", { class: "project-change-reason" }, LANG === "zh" ? row.reason_zh || row.reason : row.reason),
        h("details", { class: "project-row-identity" }, h("summary", {}, "GlobalId / IFC"), h("p", {}, text(row.global_id)), h("p", {}, `${text(row.before_class)} → ${text(row.after_class)}`))));
    }
    if (rows.length > limit) results.append(h("button", { type: "button", onclick: () => { limit += 100; renderResults(); } }, P.more));
  }
  modelSelect.addEventListener("change", () => setModel(modelSelect.value));
  for (const select of [before, after]) select.addEventListener("change", () => { outcome.hidden = true; message.textContent = before.value === after.value ? P.sameRevision : P.compareChoose; submit.disabled = before.value === after.value; });
  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (submit.disabled || !before.value || before.value === after.value) return;
    controller?.abort(); controller = new AbortController(); const token = ++current;
    submit.disabled = true; modelSelect.disabled = before.disabled = after.disabled = true;
    submit.textContent = P.comparing; message.textContent = P.comparing; message.classList.remove("is-error");
    form.setAttribute("aria-busy", "true");
    const pair = { before: before.value, after: after.value };
    try {
      const response = await requestJSON(`/api/projects/compare?before=${encodeURIComponent(pair.before)}&after=${encodeURIComponent(pair.after)}`, { signal: controller.signal });
      if (token !== current) return;
      data = response; severity = data.rows.some(r => r.severity === "ERROR") ? "ERROR" : "INFO";
      scopeNote.textContent = LANG === "zh" ? data.scope_note_zh || data.scope_note || "" : data.scope_note || "";
      scopeNote.hidden = !scopeNote.textContent;
      category = CHANGES.find(change => data.rows.some(row => (row.severity || "ERROR") === severity && row.change === change)) || "remaining";
      limit = 100; outcome.hidden = false; message.textContent = `${before.selectedOptions[0].textContent} → ${after.selectedOptions[0].textContent}`;
      renderResults();
      outcome.scrollIntoView({ block: "start" });
      const url = new URL(location.href); url.searchParams.set("before", pair.before); url.searchParams.set("after", pair.after); history.replaceState(null, "", url);
    } catch (error) { if (error.name !== "AbortError") { message.textContent = `${P.compareError} ${error.message}`; message.classList.add("is-error"); } }
    finally { if (token === current) { submit.disabled = false; modelSelect.disabled = before.disabled = after.disabled = false; submit.textContent = P.compareAction; form.setAttribute("aria-busy", "false"); } }
  });
  setModel(models[0]?.model_id || "");
  function restore() {
    const url = new URL(location.href);
    if (url.searchParams.has("before") && url.searchParams.has("after")) {
      const first = url.searchParams.get("before"); const second = url.searchParams.get("after");
      const model = models.find(m => m.revisions.some(r => r.revision_id === first) && m.revisions.some(r => r.revision_id === second));
      if (model && first !== second) { setModel(model.model_id); before.value = first; after.value = second; form.requestSubmit(); }
    }
  }
  return { element: section, restore, chooseModel: id => { setModel(id); section.scrollIntoView({ block: "start" }); modelSelect.focus(); }, dispose: () => { ++current; controller?.abort(); } };
}
