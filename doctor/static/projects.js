import { h } from "./dom.js";
import { LANG } from "./i18n.js";
import { languageSwitch } from "./language.js";
import { P } from "./projects-words.js";
import { requestJSON, postJSON } from "./projects-api.js";
import { comparisonPanel } from "./projects-compare.js";
import { E } from "./enterprise-words.js";
import { draftGuard } from "./enterprise-ui.js";
import { rulesPanel } from "./projects-rules.js";
import { purposePanel } from "./projects-purpose.js";

document.documentElement.lang = LANG === "en" ? "en" : "zh-CN";
document.title = `BIM Doctor · ${P.title}`;
const state = { projects: [], project: null, controller: null, current: 0, limit: 100 };
let compare = null;
let enterprise = null;
const navigate = draftGuard(() => enterprise);
const date = value => value ? new Date(value).toLocaleString(LANG === "zh" ? "zh-CN" : "en", { dateStyle: "medium", timeStyle: "short" }) : P.unknown;
const linkToReview = (project, model) => `/review.html?lang=${LANG}&project=${encodeURIComponent(project)}${model ? `&model=${encodeURIComponent(model)}` : ""}`;
const projectList = h("div", { class: "project-list", id: "project-list" });
const createName = h("input", { id: "project-name", type: "text", maxlength: "160", placeholder: P.projectPlaceholder, autocomplete: "off" });
const createMessage = h("p", { class: "project-form-message", id: "create-project-message", role: "status", "aria-live": "polite" });
createName.setAttribute("aria-describedby", "create-project-message");
const createButton = h("button", { type: "submit", class: "review-primary" }, P.create);
const form = h("form", { class: "project-create-form", novalidate: true }, h("label", { for: "project-name" }, P.projectName), createName, createButton, createMessage);
const mainPanel = h("div", { class: "project-main-panel", id: "project-main-panel" }, h("div", { class: "project-start-state project-surface" }, h("h2", {}, P.emptyProjects), h("p", {}, P.emptyProjectsBody)));
const listStatus = h("p", { class: "project-list-status", role: "status", "aria-live": "polite" }, P.loading);
document.querySelector("#projects-root").append(
  h("header", { class: "review-header" }, h("a", { class: "brand", href: `/?lang=${LANG}` }, h("span", { class: "brand-mark", "aria-hidden": "true" }, "BD"), "BIM Doctor"),
    h("nav", { class: "review-nav", "aria-label": P.navigation }, h("a", { href: `/projects.html?lang=${LANG}`, "aria-current": "page" }, P.nav), h("a", { href: `/review.html?lang=${LANG}` }, P.review), h("a", { href: `/?lang=${LANG}` }, P.records)), languageSwitch()),
  h("main", { id: "main", class: "projects-main", tabindex: "-1" }, h("div", { class: "projects-page-heading" }, h("p", { class: "review-eyebrow" }, "IFC / PROJECTS"), h("h1", {}, P.title), h("p", {}, P.subtitle)),
    h("div", { class: "projects-layout" }, h("aside", { class: "project-sidebar project-surface", "aria-label": P.projects }, h("h2", {}, P.projects), listStatus, projectList, h("div", { class: "project-create-section" }, h("h3", {}, P.create), form)), mainPanel)));

function renderList() {
  projectList.replaceChildren(...state.projects.slice(0, state.limit).map(project => h("button", { type: "button", class: `project-list-item${state.project?.project_id === project.project_id ? " is-selected" : ""}`, "aria-pressed": String(state.project?.project_id === project.project_id), onclick: () => navigate(() => openProject(project.project_id)) }, h("strong", {}, project.name), h("span", {}, `${project.model_count || 0} ${P.models} · ${project.revision_count || 0} ${P.revisions}`))));
  if (state.projects.length > state.limit) projectList.append(h("button", { type: "button", onclick: () => { state.limit += 100; renderList(); } }, P.more));
  listStatus.textContent = state.projects.length ? `${state.projects.length} ${P.projects}` : P.chooseProject;
}
async function refreshProjects(preferred = null) {
  listStatus.textContent = P.loading;
  try {
    const response = await requestJSON("/api/projects"); state.projects = response.projects; renderList();
    const asked = preferred || new URL(location.href).searchParams.get("project");
    if (asked) await openProject(asked);
    else if (state.projects[0]) await openProject(state.projects[0].project_id);
  } catch (error) {
    listStatus.replaceChildren(`${P.projectLoadError} ${error.message} `, h("button", { type: "button", onclick: () => refreshProjects(preferred) }, P.retry));
  }
}
async function openProject(id) {
  state.controller?.abort(); state.controller = new AbortController(); const token = ++state.current;
  compare?.dispose(); compare = null; mainPanel.setAttribute("aria-busy", "true");
  enterprise?.dispose(); enterprise = null;
  mainPanel.replaceChildren(h("p", { class: "project-surface project-loading", role: "status" }, P.loading));
  try {
    const data = await requestJSON(`/api/projects/detail?project=${encodeURIComponent(id)}`, { signal: state.controller.signal });
    if (token !== state.current) return;
    state.project = data.project; renderList();
    const url = new URL(location.href); if (url.searchParams.get("project") !== id) { for (const key of ["before", "after", "assessment", "rule_revision", "rule"]) url.searchParams.delete(key); }
    url.searchParams.set("project", id); history.replaceState(null, "", url);
    renderProject(data);
    document.title = `${data.project.name} · BIM Doctor`;
  } catch (error) {
    if (error.name !== "AbortError") mainPanel.replaceChildren(h("div", { class: "project-surface project-error", role: "alert" }, h("p", {}, `${P.projectLoadError} ${error.message}`), h("button", { type: "button", onclick: () => openProject(id) }, P.retry)));
  } finally { if (token === state.current) mainPanel.setAttribute("aria-busy", "false"); }
}
function renderProject(data) {
  const { project, models } = data;
  const heading = h("section", { class: "project-detail-heading project-surface" }, h("div", {}, h("p", { class: "review-overline" }, P.projects), h("h2", {}, project.name), h("p", { class: "project-muted" }, `${models.length} ${P.models} · ${models.reduce((n, m) => n + m.revisions.length, 0)} ${P.revisions}`)),
    h("div", { class: "project-header-actions" }, h("a", { class: "project-primary-link", href: linkToReview(project.project_id) }, P.addModel), h("a", { class: "project-secondary-link", href: `/api/projects/brief?project=${encodeURIComponent(project.project_id)}&language=${LANG}`, download: true }, P.brief)));
  mainPanel.replaceChildren(heading);
  const tab = new URL(location.href).searchParams.get("tab") || "models";
  mainPanel.append(h("nav", { class: "enterprise-tabs", "aria-label": P.projects }, ["models", "rules", "purpose"].map(key => h("a", { href: `/projects.html?lang=${LANG}&project=${encodeURIComponent(project.project_id)}&tab=${key}`, "aria-current": key === tab ? "page" : null }, E[key]))));
  if (tab === "rules") { enterprise = rulesPanel(project.project_id, { navigate }); mainPanel.append(enterprise.element); return; }
  if (tab === "purpose") { enterprise = purposePanel(project, models); mainPanel.append(enterprise.element); return; }
  if (!models.length) {
    mainPanel.append(h("div", { class: "project-start-state project-surface" }, h("h3", {}, P.emptyModels), h("p", {}, P.emptyModelsBody), h("a", { class: "project-text-link", href: linkToReview(project.project_id) }, P.open3d, " ↗")));
    return;
  }
  const modelList = h("div", { class: "project-model-list" });
  for (const model of models) {
    const revisions = [...model.revisions].sort((a, b) => b.number - a.number);
    const rows = h("div", { class: "project-revision-list" });
    const revisionRow = (revision, index) => h("article", { class: "project-revision-row" }, h("span", { class: "project-revision-number" }, `R${revision.number}`),
      h("div", { class: "project-revision-name" }, h("strong", {}, revision.label), h("span", {}, `${revision.filename || P.unknown} · ${date(revision.created_at)}`)),
      h("div", { class: "project-revision-counts" }, h("span", {}, `${revision.summary?.errors || 0} ${P.needsReview}`), h("span", {}, `${revision.summary?.information || 0} ${P.information}`)),
      h("a", { class: "project-secondary-link", href: `/review.html?lang=${LANG}&revision=${encodeURIComponent(revision.revision_id)}` }, P.open3d, " ↗"));
    rows.append(...revisions.slice(0, 5).map(revisionRow));
    if (revisions.length > 5) rows.append(h("details", { class: "project-earlier-revisions" }, h("summary", {}, `${P.revisions} · ${revisions.length - 5}`), revisions.slice(5).map(revisionRow)));
    const compareButton = h("button", { type: "button", onclick: () => compare?.chooseModel(model.model_id), disabled: revisions.length < 2 }, P.compare);
    modelList.append(h("section", { class: "project-model-card project-surface" }, h("div", { class: "project-model-heading" }, h("div", {}, h("span", { class: "review-overline" }, P.model), h("h3", {}, model.name), h("p", { class: "project-muted" }, `${revisions.length} ${P.revisions}`)), h("div", { class: "project-model-actions" }, compareButton, h("a", { class: "project-secondary-link", href: linkToReview(project.project_id, model.model_id) }, P.addRevision))), rows));
  }
  mainPanel.append(modelList);
  compare = comparisonPanel(models); mainPanel.append(compare.element); compare.restore();
}
form.addEventListener("submit", async event => {
  event.preventDefault(); if (createButton.disabled) return;
  const name = createName.value.trim();
  if (!name) { createMessage.textContent = P.projectRequired; createName.setAttribute("aria-invalid", "true"); createName.focus(); return; }
  createName.removeAttribute("aria-invalid"); createButton.disabled = true; createButton.textContent = P.creating; createMessage.textContent = P.creating;
  try {
    const project = await postJSON("/api/projects", { name });
    createName.value = ""; createMessage.textContent = P.projectCreated; createMessage.classList.remove("is-error");
    await refreshProjects(project.project_id);
  } catch (error) { createMessage.textContent = `${P.error}: ${error.message}`; createMessage.classList.add("is-error"); }
  finally { createButton.disabled = false; createButton.textContent = P.create; }
});
refreshProjects();
