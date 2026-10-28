import { h } from "./dom.js";
import { LANG } from "./i18n.js";
import { P } from "./projects-words.js";
import { requestJSON, postJSON } from "./projects-api.js";

const field = (name, input) => h("label", {}, h("span", {}, name), input);
const statuses = ["open", "in_progress", "ready_for_recheck"];
const option = (id, text) => h("option", { value: id }, text);

// Project persistence stays separate from geometry and the IFC check renderer.
export function createProjectReview({ getReport, onSaved }) {
  let revision = null;
  let projects = [];
  let models = [];
  let projectLoading = false;
  let modelLoading = false;
  let modelController = null;
  let modelRequest = 0;
  let saving = false;
  let sourceStatus = null;
  let sourceRequest = 0;
  let nextRequest = 0;
  let autoPurposeRevision = null;
  const projectRules = new Map();
  const followups = new Map();
  const drafts = new Map();
  const expanded = new Map();
  const params = new URL(location.href).searchParams;
  let preferredProject = params.get("project") || "";
  let preferredModel = params.get("model") || "";
  const context = h("section", { class: "project-review-context", "aria-label": P.sourceRevision });
  const openSave = h("button", { type: "button", onclick: () => { panel.hidden = !panel.hidden; if (!panel.hidden) projectSelect.focus(); } }, P.saveToProject);
  const contextText = h("div", { class: "project-review-context-text" });
  context.append(contextText, openSave);
  const projectSelect = h("select", { id: "save-project" });
  const newProjectName = h("input", { type: "text", id: "save-project-name", maxlength: "160", placeholder: P.projectPlaceholder, autocomplete: "off" });
  const newProjectField = field(P.projectName, newProjectName);
  const modelSelect = h("select", { id: "save-model" }, option("", P.newModel));
  const newModelName = h("input", { type: "text", id: "save-model-name", maxlength: "160", placeholder: P.modelPlaceholder, autocomplete: "off" });
  const newModelField = field(P.modelName, newModelName);
  const revisionLabel = h("input", { type: "text", id: "save-revision-label", maxlength: "120", placeholder: P.revisionPlaceholder, autocomplete: "off" });
  const retainSource = h("input", { id: "save-retain-source", type: "checkbox", disabled: true });
  const sourceNote = h("p", { class: "project-muted", id: "save-source-status", role: "status" }, P.sourceChecking);
  retainSource.setAttribute("aria-describedby", "save-source-status");
  const retainField = h("div", { class: "project-source-retention" }, h("label", { class: "project-checkbox" }, retainSource, h("span", {}, P.retainSource)), sourceNote);
  const saveMessage = h("p", { class: "project-form-message", id: "save-revision-message", role: "status", "aria-live": "polite" });
  for (const control of [projectSelect, newProjectName, modelSelect, newModelName, revisionLabel]) control.setAttribute("aria-describedby", "save-revision-message");
  const submit = h("button", { class: "review-primary", type: "submit" }, P.saveRevision);
  const form = h("form", { class: "project-save-form", novalidate: true }, field(P.projects, projectSelect), newProjectField, field(P.model, modelSelect), newModelField, field(P.revisionLabel, revisionLabel), retainField, submit, saveMessage);
  const panel = h("section", { class: "project-review-save project-surface", hidden: true }, h("div", { class: "project-section-header" }, h("div", {}, h("h2", {}, P.saveRevision), h("p", { class: "project-muted" }, P.saveDescription)), h("button", { type: "button", onclick: () => { panel.hidden = true; openSave.focus(); } }, P.close)), form);

  function hasDirty() { return [...drafts.values()].some(draft => draft.dirty); }
  window.addEventListener("beforeunload", event => { if (hasDirty()) { event.preventDefault(); event.returnValue = ""; } });
  const dialogTitle = h("h2", { id: "project-draft-title" }, P.unsavedTitle);
  const dialogBody = h("p", { id: "project-draft-description" }, P.unsavedBody);
  let pending = null;
  let bypass = false;
  const keep = h("button", { type: "button", autofocus: true, onclick: () => { pending = null; dialog.close(); } }, P.keepEditing);
  const discard = h("button", { type: "button", onclick: () => { for (const draft of drafts.values()) draft.dirty = false; const action = pending; pending = null; dialog.close(); bypass = true; action?.(); bypass = false; } }, P.discard);
  const dialog = h("dialog", { class: "project-draft-dialog", "aria-labelledby": "project-draft-title", "aria-describedby": "project-draft-description" }, dialogTitle, dialogBody, h("div", { class: "project-dialog-actions" }, keep, discard));
  document.body.append(dialog);
  document.addEventListener("click", event => {
    if (bypass || !hasDirty()) return;
    const target = event.target.closest("a[href], .language-switch button");
    if (!target || target.closest("dialog")) return;
    // Downloading a brief leaves the page and its in-memory drafts in place.
    if (target.hasAttribute("download")) return;
    event.preventDefault(); event.stopImmediatePropagation();
    pending = () => target.click(); dialog.showModal(); keep.focus();
  }, true);
  dialog.addEventListener("cancel", () => { pending = null; });
  function renderContext() {
    const report = getReport();
    context.hidden = !report;
    openSave.disabled = !report || saving;
    if (revision) {
      const project = projects.find(item => item.project_id === revision.project_id);
      contextText.replaceChildren(h("span", { class: "project-context-status" }, P.savedRevision), h("strong", {}, `${project?.name || P.projects} / ${revision.label} · R${revision.number}`), h("a", { class: "project-text-link", href: `/projects.html?lang=${LANG}&project=${encodeURIComponent(revision.project_id)}&tab=models` }, P.back, " ↗"));
      renderNextStep(revision);
      openSave.hidden = true; panel.hidden = true;
    } else {
      contextText.replaceChildren(h("span", { class: "project-context-status" }, P.noProject), h("span", { class: "project-muted" }, P.unsavedImport));
      openSave.hidden = false;
    }
  }
  async function renderNextStep(savedRevision) {
    const token = ++nextRequest;
    try {
      if (!projectRules.has(savedRevision.project_id)) projectRules.set(savedRevision.project_id, requestJSON(`/api/projects/rules?project=${encodeURIComponent(savedRevision.project_id)}`));
      const rules = await projectRules.get(savedRevision.project_id);
      if (token !== nextRequest || revision?.revision_id !== savedRevision.revision_id) return;
      const adopted = !!rules.rule_revisions?.length;
      const target = `/projects.html?lang=${LANG}&project=${encodeURIComponent(savedRevision.project_id)}&revision=${encodeURIComponent(savedRevision.revision_id)}&tab=${adopted ? "purpose" : "rules"}`;
      const next = h("a", { class: "project-primary-link project-purpose-next", href: target }, adopted ? P.continuePurpose : P.continueRules);
      contextText.append(next);
      if (!adopted) contextText.append(h("span", { class: "project-muted project-purpose-hint" }, P.ruleFirst));
      if (autoPurposeRevision === savedRevision.revision_id) { autoPurposeRevision = null; next.click(); }
    } catch (error) {
      projectRules.delete(savedRevision.project_id);
      if (token === nextRequest && revision?.revision_id === savedRevision.revision_id) contextText.append(h("span", { class: "project-muted" }, `${P.projectLoadError} `, h("button", { type: "button", onclick: () => renderContext() }, P.retry)));
    }
  }
  async function loadSourceStatus(report) {
    const token = ++sourceRequest; sourceStatus = null; retainSource.checked = false; retainSource.disabled = true; sourceNote.textContent = P.sourceChecking;
    try {
      const result = await requestJSON(`/api/review/source-status?review=${encodeURIComponent(report.review_id)}`);
      if (token !== sourceRequest || getReport()?.review_id !== report.review_id) return;
      sourceStatus = result; retainSource.disabled = saving || !result.retainable;
      retainField.hidden = false;
      sourceNote.textContent = result.source_available ? P.retainedSource : result.reason === "federated_demo" ? P.federatedSource : result.retainable ? P.temporarySource : P.expiredSource;
    } catch (error) {
      if (token !== sourceRequest) return;
      sourceNote.replaceChildren(P.sourceStatusError, " ", h("button", { type: "button", onclick: () => loadSourceStatus(report) }, P.retry));
    }
  }
  function showFields() {
    newProjectField.hidden = projectSelect.value !== "__new__";
    newModelField.hidden = !!modelSelect.value;
    submit.disabled = saving || projectLoading || modelLoading || !getReport();
  }
  async function loadModels(projectId, requested = "") {
    modelController?.abort(); modelController = new AbortController(); const token = ++modelRequest;
    modelLoading = true; showFields();
    models = []; modelSelect.replaceChildren(option("", P.newModel)); modelSelect.disabled = true;
    if (!projectId || projectId === "__new__") { modelLoading = false; modelSelect.disabled = false; showFields(); return; }
    try {
      const result = await requestJSON(`/api/projects/detail?project=${encodeURIComponent(projectId)}`, { signal: modelController.signal });
      if (token !== modelRequest) return;
      models = result.models; modelSelect.replaceChildren(option("", P.newModel), ...models.map(model => option(model.model_id, model.name)));
      modelSelect.value = models.some(m => m.model_id === requested) ? requested : "";
      modelLoading = false; modelSelect.disabled = false; showFields();
    } catch (error) {
      if (error.name !== "AbortError") {
        saveMessage.replaceChildren(`${P.projectLoadError} ${error.message} `, h("button", { type: "button", onclick: () => loadModels(projectId, requested) }, P.retry));
        saveMessage.classList.add("is-error");
      }
    }
  }
  async function loadProjects() {
    projectLoading = true; showFields();
    try {
      const result = await requestJSON("/api/projects"); projects = result.projects;
      projectSelect.replaceChildren(...projects.map(project => option(project.project_id, project.name)), option("__new__", P.newProject));
      const targetProject = revision?.project_id || preferredProject;
      projectSelect.value = projects.some(project => project.project_id === targetProject) ? targetProject : projects[0]?.project_id || "__new__";
      await loadModels(projectSelect.value, revision?.model_id || preferredModel);
      renderContext();
    } catch (error) {
      saveMessage.replaceChildren(`${P.projectLoadError} ${error.message} `, h("button", { type: "button", onclick: loadProjects }, P.retry)); saveMessage.classList.add("is-error");
    } finally { projectLoading = false; showFields(); }
  }
  projectSelect.addEventListener("change", () => { preferredProject = projectSelect.value; preferredModel = ""; showFields(); loadModels(projectSelect.value); });
  modelSelect.addEventListener("change", () => { preferredModel = modelSelect.value; showFields(); });
  function invalid(control, message) { control.setAttribute("aria-invalid", "true"); saveMessage.textContent = message; saveMessage.classList.add("is-error"); control.focus(); }
  form.addEventListener("submit", async event => {
    event.preventDefault(); if (saving || submit.disabled) return;
    for (const control of [projectSelect, newProjectName, modelSelect, newModelName, revisionLabel]) control.removeAttribute("aria-invalid");
    if (projectSelect.value === "__new__" && !newProjectName.value.trim()) { invalid(newProjectName, P.projectRequired); return; }
    if (!modelSelect.value && !newModelName.value.trim()) { invalid(newModelName, P.modelRequired); return; }
    const report = getReport(); if (!report) return;
    saving = true; submit.disabled = true; submit.textContent = P.saving; form.setAttribute("aria-busy", "true"); saveMessage.textContent = P.saving; saveMessage.classList.remove("is-error");
    const fields = [projectSelect, newProjectName, modelSelect, newModelName, revisionLabel, retainSource]; fields.forEach(control => { control.disabled = true; });
    try {
      let projectId = projectSelect.value;
      if (projectId === "__new__") {
        const created = await postJSON("/api/projects", { name: newProjectName.value.trim() });
        projects.push(created); preferredProject = projectId = created.project_id;
        projectSelect.prepend(option(projectId, created.name)); projectSelect.value = projectId;
      }
      const body = { project_id: projectId, label: revisionLabel.value.trim(), review_id: report.review_id, retain_source: !!(retainSource.checked && sourceStatus?.retainable) };
      if (modelSelect.value) body.model_id = modelSelect.value; else body.model_name = newModelName.value.trim();
      const result = await postJSON("/api/projects/revisions", body);
      if (getReport()?.review_id !== report.review_id) return;
      if (body.retain_source && result.revision.source_available) autoPurposeRevision = result.revision.revision_id;
      useReport(report, result); saveMessage.textContent = P.saveSuccess;
      const url = new URL(location.href); url.searchParams.set("revision", result.revision.revision_id); url.searchParams.set("project", result.revision.project_id); url.searchParams.set("model", result.revision.model_id); history.replaceState(null, "", url);
      onSaved(result);
    } catch (error) { saveMessage.textContent = `${P.revisionSaveError} ${error.message}`; saveMessage.classList.add("is-error"); }
    finally { saving = false; fields.forEach(control => { control.disabled = false; }); retainSource.disabled = !sourceStatus?.retainable; submit.textContent = P.saveRevision; form.setAttribute("aria-busy", "false"); showFields(); renderContext(); }
  });
  function useReport(report, envelope = null) {
    ++nextRequest; loadSourceStatus(report);
    if (envelope?.revision) {
      revision = envelope.revision; preferredProject = revision.project_id; preferredModel = revision.model_id;
      followups.clear(); for (const item of envelope.followups || []) followups.set(item.finding_id, item);
    } else { revision = null; followups.clear(); }
    newModelName.value = report.source.filename?.replace(/\.ifc$/i, "") || P.model;
    revisionLabel.value = "";
    renderContext(); showFields();
    if (projects.length) {
      projectSelect.value = projects.some(p => p.project_id === preferredProject) ? preferredProject : projects[0].project_id;
      loadModels(projectSelect.value, preferredModel);
    }
  }
  function renderFollowup(finding) {
    if (!finding) return null;
    if (!revision) return h("div", { class: "project-followup-unsaved" }, h("span", {}, P.openSave), h("button", { type: "button", onclick: () => { panel.hidden = false; panel.scrollIntoView({ block: "start" }); projectSelect.focus(); } }, P.saveToProject));
    const savedRevision = revision;
    const key = `${savedRevision.revision_id}:${finding.finding_id}`;
    const saved = followups.get(finding.finding_id) || { status: "open", owner: "", note: "" };
    if (!drafts.has(key)) drafts.set(key, { status: saved.status, owner: saved.owner, note: saved.note, dirty: false });
    const draft = drafts.get(key);
    const summaryState = h("span", { class: `project-followup-state work-${draft.status}` }, P[draft.status]);
    const summaryOwner = h("span", { class: "project-followup-owner" }, draft.owner);
    const work = h("select", { id: "followup-status" }, statuses.map(status => option(status, P[status]))); work.value = draft.status;
    const owner = h("input", { type: "text", id: "followup-owner", maxlength: "160", placeholder: P.ownerPlaceholder, autocomplete: "off" }); owner.value = draft.owner;
    const note = h("textarea", { id: "followup-note", maxlength: "4000", rows: "4", placeholder: P.notePlaceholder }); note.value = draft.note;
    const message = h("p", { class: "project-form-message", role: "status", "aria-live": "polite" }, draft.dirty ? P.draft : "");
    const save = h("button", { class: "review-primary", type: "submit" }, P.saveFollowup);
    const fields = h("form", { novalidate: true, class: "project-followup-form" }, field(P.followupStatus, work), field(P.owner, owner), field(P.note, note), save, message);
    const container = h("details", { class: "project-followup", open: !!expanded.get(key) }, h("summary", {}, h("strong", {}, P.followup), summaryState, summaryOwner), fields, h("p", { class: "project-followup-note" }, P.manualNote));
    const fitNote = () => { note.style.height = "auto"; note.style.height = `${Math.max(112, Math.min(note.scrollHeight, 360))}px`; };
    container.addEventListener("toggle", () => { expanded.set(key, container.open); if (container.open) fitNote(); });
    const update = () => {
      draft.status = work.value; draft.owner = owner.value; draft.note = note.value;
      draft.dirty = draft.status !== saved.status || draft.owner !== saved.owner || draft.note !== saved.note;
      message.textContent = draft.dirty ? P.draft : ""; summaryState.textContent = P[draft.status]; summaryState.className = `project-followup-state work-${draft.status}`; summaryOwner.textContent = draft.owner;
    };
    work.addEventListener("change", update); owner.addEventListener("input", update); note.addEventListener("input", () => { update(); fitNote(); });
    fields.addEventListener("submit", async event => {
      event.preventDefault(); if (save.disabled) return;
      save.disabled = true; work.disabled = owner.disabled = note.disabled = true; message.textContent = P.saving; fields.setAttribute("aria-busy", "true");
      try {
        const result = await postJSON("/api/projects/followup", { revision_id: savedRevision.revision_id, finding_id: finding.finding_id, status: work.value, owner: owner.value, note: note.value });
        draft.status = result.status; draft.owner = result.owner; draft.note = result.note; draft.dirty = false;
        if (revision?.revision_id === savedRevision.revision_id) followups.set(finding.finding_id, result);
        Object.assign(saved, result); message.textContent = P.followupSaved; message.classList.remove("is-error");
      } catch (error) { message.textContent = `${P.error}: ${error.message} ${P.draftRetained}`; message.classList.add("is-error"); }
      finally { save.disabled = false; work.disabled = owner.disabled = note.disabled = false; fields.setAttribute("aria-busy", "false"); }
    });
    return container;
  }
  renderContext(); loadProjects();
  return { context, panel, useReport, renderFollowup, getRevision: () => revision, hasDirty };
}
