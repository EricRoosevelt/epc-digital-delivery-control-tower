import { h } from "./dom.js";
import { LANG } from "./i18n.js";
import { requestJSON, postJSON } from "./projects-api.js";
import { E } from "./enterprise-words.js";
import { action, field, text, title, facts, details, status, blockerCard, ruleURL, changeSummary, finiteRows, problemSummary, noProblemsText } from "./enterprise-ui.js";
import { orderedProblems, noticeText } from "./enterprise-results.js";

const terminal = value => ["succeeded", "failed", "cancelled", "timed_out"].includes(value);
const lines = value => value.split(/\r?\n/).map(item => item.trim()).filter(Boolean);

export function purposePanel(project, models) {
  const revisions = models.flatMap(model => model.revisions.map(revision => ({ ...revision, model_name: model.name, model_id: model.model_id })));
  let library = null;
  let selectedRule = null;
  let currentRun = null;
  let disposed = false;
  let job = null;
  let pending = false;
  let generation = 0;
  let sourceToken = 0;
  let catalog = [];
  let catalogRevision = null;
  let limit = 100;
  let retryAction = () => refresh();
  const dirty = new Set();
  const drafts = new Map();
  const objectKeys = new Set();
  const controller = new AbortController();
  const revision = h("select", { id: "purpose-revision" }, revisions.map(item => h("option", { value: item.revision_id }, `${item.model_name} · R${item.number} · ${item.label}`)));
  const requestedRevision = new URL(location.href).searchParams.get("revision");
  if (revisions.some(item => item.revision_id === requestedRevision)) revision.value = requestedRevision;
  const rule = h("select", { id: "purpose-rule-revision" });
  const purpose = h("select", { id: "purpose-id" });
  const counterpart = h("select", { id: "purpose-counterpart" }, h("option", { value: "" }, E.noCounterpart), revisions.map(item => h("option", { value: item.revision_id }, `${item.model_name} · R${item.number} · ${item.label}`)));
  const counterpartHint = h("p", { class: "project-muted" });
  const scopeKind = h("select", { id: "purpose-scope-kind" }, ["all", "classes", "elements"].map(kind => h("option", { value: kind }, E[kind])));
  const classes = h("textarea", { id: "purpose-scope-classes", rows: "2", placeholder: "IfcAirTerminal" });
  const classesField = field(E.classes, classes);
  const search = h("input", { id: "purpose-object-search", type: "search", placeholder: E.search });
  const selectionCount = h("span", { class: "project-muted" });
  const objectList = h("div", { class: "enterprise-object-list" });
  const objectsField = h("div", { class: "enterprise-objects" }, field(E.search, h("div", { class: "enterprise-actions" }, search, action(E.clear, () => { search.value = ""; limit = 100; renderObjects(); search.focus(); }))), selectionCount, objectList);
  const sourceNote = h("p", { class: "project-muted" });
  const attachInput = h("input", { id: "purpose-source-file", type: "file", accept: ".ifc", hidden: true, "aria-label": E.attach });
  const attach = action(E.attach, () => attachInput.click()); attach.disabled = true;
  const sourceMessage = h("p", { class: "project-form-message", role: "status" });
  const prior = h("select", { id: "purpose-prior" }, h("option", { value: "" }, E.noPrior));
  const start = h("button", { type: "submit", class: "review-primary", disabled: true }, E.start);
  const cancel = action(E.cancel, () => cancelJob()); cancel.hidden = true;
  const retry = action(E.retry, () => job ? execute(job) : retryAction()); retry.hidden = true;
  const message = h("p", { class: "project-form-message enterprise-job-status", role: "status", "aria-live": "polite" });
  const history = h("div", { class: "enterprise-history" });
  const result = h("div", { class: "enterprise-result" });
  const retentionNote = h("p", { class: "project-muted" }, E.retainSource);
  const form = h("form", { class: "enterprise-form", novalidate: true }, field(E.revision, revision), h("div", { class: "enterprise-source" }, sourceNote, retentionNote, attach, attachInput, sourceMessage), field(E.ruleVersion, rule), field(E.choosePurpose, purpose), field(E.scope, scopeKind), h("p", { class: "project-muted" }, E.scopeHint), classesField, objectsField, field(E.counterpart, counterpart), counterpartHint, field(E.prior, prior), h("div", { class: "enterprise-actions" }, start, cancel, retry), message);
  const element = h("section", { class: "enterprise-panel", "aria-label": E.purpose }, h("section", { class: "project-surface enterprise-section" }, h("h2", {}, E.purpose), !revisions.length ? h("p", {}, E.noRevision) : null, form), result, history);
  function error(failure) { message.textContent = `${E.failed}: ${failure.message}`; message.classList.add("is-error"); retry.hidden = false; }
  function sourceState() {
    const available = library?.sources?.find(item => item.revision_id === revision.value)?.source_available;
    sourceNote.textContent = available ? E.sourceReady : E.sourceMissing;
    retentionNote.hidden = !!available;
    attach.hidden = !!available; attach.disabled = pending || !library || !revision.value; start.disabled = pending || !available || !rule.value || !purpose.value;
  }
  function scopeFields() { classesField.hidden = scopeKind.value !== "classes"; objectsField.hidden = scopeKind.value !== "elements"; }
  function renderObjects() {
    const query = search.value.toLocaleLowerCase();
    const found = catalog.filter(item => !query || [item.name, item.element_key, item.global_id, item.ifc_class].some(value => String(value || "").toLocaleLowerCase().includes(query)));
    selectionCount.textContent = `${E.selected}: ${objectKeys.size} / ${catalog.length}`;
    objectList.replaceChildren(...found.slice(0, limit).map(item => {
      const input = h("input", { type: "checkbox", value: item.element_key }); input.checked = objectKeys.has(item.element_key);
      input.addEventListener("change", () => { input.checked ? objectKeys.add(item.element_key) : objectKeys.delete(item.element_key); selectionCount.textContent = `${E.selected}: ${objectKeys.size} / ${catalog.length}`; });
      return h("label", {}, input, h("span", {}, item.name || item.ifc_class, h("code", {}, item.element_key)));
    }));
    if (found.length > limit) objectList.append(action(E.more, () => { limit += 100; renderObjects(); }));
  }
  async function loadRevision() {
    const token = ++sourceToken;
    if (catalogRevision !== revision.value) { catalog = []; objectKeys.clear(); }
    renderObjects(); sourceState();
    if (!revision.value) return;
    try {
      const data = await requestJSON(`/api/projects/revision?revision=${encodeURIComponent(revision.value)}`, { signal: controller.signal });
      if (token !== sourceToken || disposed) return;
      catalog = data.report.elements; catalogRevision = revision.value; renderObjects();
    } catch (failure) { if (failure.name !== "AbortError") sourceMessage.textContent = `${E.failed}: ${failure.message}`; }
  }
  function setPurpose() {
    const item = selectedRule?.purposes?.find(entry => entry.purpose_id === purpose.value);
    const priorCounterpart = counterpart.value;
    const producer = revisions.find(entry => entry.revision_id === revision.value);
    counterpart.replaceChildren(h("option", { value: "" }, E.noCounterpart), ...revisions.filter(entry => entry.model_id !== producer?.model_id).map(entry => h("option", { value: entry.revision_id }, `${entry.model_name} · R${entry.number} · ${entry.label}`)));
    if ([...counterpart.options].some(option => option.value === priorCounterpart)) counterpart.value = priorCounterpart;
    counterpart.disabled = !item?.requires_counterpart;
    counterpartHint.textContent = item?.requires_counterpart ? E.counterpartRequired : E.singleArtifact;
    const selectedPrior = prior.value;
    prior.replaceChildren(h("option", { value: "" }, E.noPrior), ...(library?.assessments || []).filter(run => run.purpose_id === purpose.value).map(run => h("option", { value: run.run_id }, `${run.created_at || ""} · ${run.purpose_id} · ${run.conclusion?.status || "UNKNOWN"}`)));
    if ([...prior.options].some(option => option.value === selectedPrior)) prior.value = selectedPrior;
    sourceState();
  }
  async function loadRule() {
    const asked = rule.value;
    purpose.replaceChildren(); start.disabled = true;
    if (!asked) { selectedRule = null; purpose.replaceChildren(); sourceState(); return; }
    try {
      const data = await requestJSON(`/api/projects/rules/detail?rule_revision=${encodeURIComponent(asked)}`, { signal: controller.signal });
      if (disposed || rule.value !== asked) return;
      selectedRule = data;
      purpose.replaceChildren(...(data.purposes || []).map(item => h("option", { value: item.purpose_id }, title(item))));
      setPurpose();
    } catch (failure) { if (failure.name !== "AbortError") { retryAction = loadRule; error(failure); } }
  }
  async function refresh(openId) {
    try {
      library = await requestJSON(`/api/projects/purpose?project=${encodeURIComponent(project.project_id)}`, { signal: controller.signal });
      if (disposed) return;
      const selected = rule.value;
      rule.replaceChildren(...(library.rule_revisions || []).map(item => h("option", { value: item.rule_revision_id }, `${item.title} · ${item.version} · ${item.rule_revision_id.slice(-8)}`)));
      if ([...rule.options].some(item => item.value === selected)) rule.value = selected;
      prior.replaceChildren(h("option", { value: "" }, E.noPrior), ...(library.assessments || []).map(run => h("option", { value: run.run_id }, `${run.created_at || ""} · ${run.purpose_id} · ${run.conclusion?.status || "UNKNOWN"}`)));
      history.replaceChildren(h("h2", {}, E.history), finiteRows(library.assessments || [], run => action(`${run.created_at || run.run_id} · ${run.purpose_id} · ${E[run.conclusion?.status] || run.conclusion?.status || "UNKNOWN"}`, () => openRun(run.run_id), "enterprise-history-item")));
      if (!library.assessments?.length) history.append(h("p", { class: "project-muted" }, E.empty));
      await loadRule(); await loadRevision();
      const asked = openId || new URL(location.href).searchParams.get("assessment");
      if (asked) await openRun(asked);
    } catch (failure) { if (failure.name !== "AbortError") { retryAction = () => refresh(openId); error(failure); } }
  }
  async function openRun(id) {
    const token = ++generation;
    try {
      const run = await requestJSON(`/api/projects/purpose/run?run=${encodeURIComponent(id)}`, { signal: controller.signal });
      if (disposed || token !== generation) return;
      const ruleInfo = run.rule_snapshot && run.purpose_snapshot ? { ...run.rule_snapshot, purposes: [run.purpose_snapshot] } : selectedRule?.rule_revision_id === run.rule_revision_id ? selectedRule : await requestJSON(`/api/projects/rules/detail?rule_revision=${encodeURIComponent(run.rule_revision_id)}`, { signal: controller.signal });
      if (disposed || token !== generation) return;
      currentRun = run; renderRun(run, ruleInfo);
      const url = new URL(location.href); url.searchParams.set("assessment", id); window.history.replaceState(null, "", url);
    } catch (failure) { if (failure.name !== "AbortError") { retryAction = () => openRun(id); error(failure); } }
  }
  async function prepareReassessment(run) {
    revision.value = run.revision_id; rule.value = run.rule_revision_id; await loadRule(); purpose.value = run.purpose_id; setPurpose();
    scopeKind.value = run.scope.kind; classes.value = (run.scope.classes || []).join("\n"); scopeFields(); await loadRevision();
    const exactKeys = new Set(catalog.map(item => item.element_key));
    const mapping = new Map((run.evaluation?.elements || []).map(item => [item.element_key, item.review_element_key]));
    objectKeys.clear();
    for (const key of run.scope.element_keys || []) {
      const reviewKey = mapping.get(key) || key;
      if (exactKeys.has(reviewKey)) objectKeys.add(reviewKey);
    }
    renderObjects(); counterpart.value = run.consuming_revision_id || ""; prior.value = run.run_id;
    start.textContent = E.rerun; form.scrollIntoView({ block: "start" }); start.focus();
  }
  function manualForm(run, request) {
    const key = `${run.run_id}/${request.evidence_id}/${(request.subject_keys || []).join("|")}`;
    const draft = drafts.get(key) || { outcome: request.current_outcome || "not-yet-confirmed", person: "", basis: "", reference: "" };
    drafts.set(key, draft);
    const outcome = h("select", { "aria-label": E.outcome }, (request.outcomes || ["confirmed", "unmet", "not-yet-confirmed"]).map(value => h("option", { value }, E[value] || value)));
    const person = h("input", { type: "text", maxlength: "160", autocomplete: "off" });
    const basis = h("textarea", { rows: "3" });
    const reference = h("input", { type: "text", autocomplete: "off" });
    outcome.value = draft.outcome; person.value = draft.person; basis.value = draft.basis; reference.value = draft.reference;
    const save = h("button", { type: "submit", class: "review-primary" }, E.saveEvidence);
    const note = h("p", { class: "project-form-message", role: "status", "aria-live": "polite", id: `purpose-evidence-message-${request.blocker_id}` });
    for (const control of [outcome, person, basis, reference]) control.setAttribute("aria-describedby", note.id);
    const entry = h("form", { class: "enterprise-manual-form", novalidate: true }, h("h3", {}, `${request.element_name || ""} · ${request.title || request.evidence_id}`), h("p", {}, request.acceptance || request.reason), facts([[E.method, request.method_description || request.method_id], [E.scope, request.element_name || request.subject_keys]]), field(E.outcome, outcome), field(E.determiner, person), field(E.basis, basis), field(E.evidenceReference, reference), save, note, h("p", { class: "project-muted" }, E.manualNote), details(E.technical, { subject_keys: request.subject_keys, context_digest: request.context_digest, evidence_id: request.evidence_id }));
    for (const control of [outcome, person, basis, reference]) control.addEventListener("input", () => { draft.outcome = outcome.value; draft.person = person.value; draft.basis = basis.value; draft.reference = reference.value; dirty.add(key); });
    for (const control of [basis]) control.addEventListener("input", () => { control.style.height = "auto"; control.style.height = `${Math.min(360, Math.max(100, control.scrollHeight))}px`; });
    entry.addEventListener("submit", async event => {
      event.preventDefault(); if (save.disabled) return;
      for (const control of [person, basis, reference]) control.removeAttribute("aria-invalid");
      const invalid = [person, basis, reference].find(control => !control.value.trim());
      if (invalid) { invalid.setAttribute("aria-invalid", "true"); note.textContent = E.required; invalid.focus(); return; }
      const controls = [outcome, person, basis, reference, save]; controls.forEach(control => { control.disabled = true; }); note.textContent = E.loading;
      try {
        await postJSON("/api/projects/purpose/determinations", { run_id: run.run_id, evidence_id: request.evidence_id, subject_keys: request.subject_keys, outcome: outcome.value, method_id: request.method_id, determiner: person.value.trim(), basis: basis.value.trim(), reference: reference.value.trim(), context_digest: request.context_digest });
        dirty.delete(key); note.textContent = E.evidenceSaved; note.classList.remove("is-error");
      } catch (failure) { note.textContent = `${E.failed}: ${failure.message}`; note.classList.add("is-error"); }
      finally { controls.forEach(control => { control.disabled = false; }); }
    });
    return entry;
  }
  function renderRun(run, ruleInfo) {
    const conclusion = run.conclusion || { status: "UNKNOWN" };
    const revisionInfo = revisions.find(item => item.revision_id === run.revision_id);
    const purposeInfo = ruleInfo.purposes?.find(item => item.purpose_id === run.purpose_id);
    const blockers = h("section", { class: "project-surface enterprise-section enterprise-blockers" });
    const ordered = orderedProblems(run);
    let blockLimit = 100;
    const renderBlockers = () => {
      blockers.replaceChildren(h("h2", {}, E.blockers), problemSummary(run), ...ordered.slice(0, blockLimit).map(item => blockerCard(run, item)));
      if (!run.blockers?.length) blockers.append(h("p", { class: "project-muted" }, noProblemsText(run)));
      if (run.blockers?.length > blockLimit) blockers.append(action(E.more, () => { blockLimit += 100; renderBlockers(); }, "enterprise-more-blockers"));
    };
    renderBlockers();
    result.replaceChildren(h("section", { class: "project-surface enterprise-section enterprise-run", "data-run": run.run_id }, h("div", { class: "enterprise-row-heading" }, h("h2", {}, E.conclusion), status(conclusion.status)), facts([[E.choosePurpose, purposeInfo ? title(purposeInfo) : run.purpose_id], [E.revision, revisionInfo ? `${revisionInfo.model_name} · R${revisionInfo.number} · ${revisionInfo.label}` : run.revision_id], [E.ruleVersion, `${ruleInfo.title} · ${ruleInfo.version}`], [E.source, ruleInfo.source?.organization], [E.confirmer, ruleInfo.confirmed_by], [E.scopeCount, conclusion.scope_count], [E.responsible, ruleInfo.responsible_team]]), ...(conclusion.caveats || []).map(item => h("p", {}, noticeText(text(item), LANG))),
      h("div", { class: "enterprise-actions" }, action(E.rerun, () => prepareReassessment(run)), h("a", { class: "project-secondary-link", href: `/api/projects/purpose/brief?run=${encodeURIComponent(run.run_id)}&language=${LANG}`, download: true }, E.brief), h("a", { href: ruleURL(run) }, E.ruleLink)), run.refusal ? h("p", { class: "project-form-message is-error", role: "status" }, `${E.refusal}: ${noticeText(run.refusal.text || text(run.refusal), LANG)}`) : null,
      changeSummary(run)),
      blockers,
      h("section", { class: "project-surface enterprise-section" }, h("h2", {}, E.evidenceRequests), finiteRows((run.evidence_requests || []).filter(item => item.execution !== "unsupported" && item.method_id), item => manualForm(run, item))),
      h("section", { class: "project-surface enterprise-section" }, h("h2", {}, E.records), ...(run.determinations || []).map(item => h("article", { class: "enterprise-rule" }, facts([[E.evidence, item.evidence_id], [E.outcome, E[item.outcome] || item.outcome], [E.determiner, item.determiner], [E.basis, item.basis], [E.evidenceReference, item.reference], [E.method, item.method_id]]))), details(E.technical, { run_id: run.run_id, assessment_digest: run.assessment_digest, scope: run.scope, record: run.record, evaluation: run.evaluation })));
  }
  async function cancelJob() {
    if (!job || job.terminal) return;
    job.cancelRequested = true; cancel.disabled = true; message.textContent = E.cancelling;
    try { await postJSON("/api/projects/purpose/jobs/cancel", { job_id: job.id }); if (!pending) execute(job); }
    catch (failure) { cancel.disabled = false; error(failure); }
  }
  function leaveJob() {
    if (job && !job.terminal) fetch("/api/projects/purpose/jobs/cancel", { method: "POST", keepalive: true, headers: { "Content-Type": "application/json" }, body: JSON.stringify({ job_id: job.id }) }).catch(() => {});
  }
  window.addEventListener("pagehide", leaveJob);
  async function execute(task) {
    if (pending) return;
    pending = true; form.setAttribute("aria-busy", "true"); retryAction = () => form.requestSubmit(); start.disabled = true; cancel.hidden = false; cancel.disabled = false; retry.hidden = true; message.classList.remove("is-error");
    for (const control of [revision, rule, purpose, scopeKind, classes, counterpart, prior, attach]) control.disabled = true;
    try {
      let state;
      if (task.submitted) {
        try { state = await requestJSON(`/api/projects/purpose/jobs?job=${encodeURIComponent(task.id)}`, { signal: controller.signal }); }
        catch (failure) { if (failure.status !== 404) throw failure; }
      }
      if (!state) {
        task.submitted = true;
        try { state = await postJSON("/api/projects/purpose/runs", { ...task.body, job_id: task.id }, { signal: controller.signal }); }
        catch (failure) { if (failure.status >= 400 && failure.status < 500) task.terminal = true; throw failure; }
      }
      while (!disposed) {
        message.textContent = task.cancelRequested || state.state === "cancelling" ? E.cancelling : `${E.running} ${state.stage || state.state}${state.total > 0 ? ` · ${state.completed} / ${state.total}` : ""}`;
        if (terminal(state.state)) {
          task.terminal = true;
          if (state.state === "succeeded") { if (task.cancelRequested) { await refresh(currentRun?.run_id); message.textContent = E.notAdopted; } else { message.textContent = E.complete; await refresh(state.result?.run_id || state.run_id); message.textContent = E.saved; } }
          else if (state.state === "cancelled") message.textContent = E.cancelled;
          else throw new Error(state.state === "timed_out" ? E.timeout : state.error?.message || state.error || E.failed);
          break;
        }
        await new Promise(resolve => setTimeout(resolve, 500));
        state = await requestJSON(`/api/projects/purpose/jobs?job=${encodeURIComponent(task.id)}`, { signal: controller.signal });
      }
    } catch (failure) { if (failure.name !== "AbortError") { error(new Error(`${failure.message} ${task.terminal ? "" : E.jobUnknown}`)); } }
    finally {
      pending = false; form.setAttribute("aria-busy", "false"); cancel.hidden = !!task.terminal; cancel.disabled = false;
      for (const control of [revision, rule, purpose, scopeKind, classes, counterpart, prior, attach]) control.disabled = !task.terminal;
      if (task.terminal) { job = null; sourceState(); setPurpose(); }
    }
  }
  form.addEventListener("submit", event => {
    event.preventDefault(); if (start.disabled || job) return;
    const scope = { kind: scopeKind.value, classes: scopeKind.value === "classes" ? lines(classes.value) : [], element_keys: scopeKind.value === "elements" ? [...objectKeys] : [] };
    job = { id: crypto.randomUUID(), body: { project_id: project.project_id, revision_id: revision.value, rule_revision_id: rule.value, purpose_id: purpose.value, scope, ...(counterpart.disabled || !counterpart.value ? {} : { consuming_revision_id: counterpart.value }), ...(prior.value ? { prior_run_id: prior.value } : {}) } };
    execute(job);
  });
  attachInput.addEventListener("change", async () => {
    const file = attachInput.files[0]; attachInput.value = ""; if (!file) return;
    const target = revision.value; attach.disabled = true; sourceMessage.textContent = E.loading;
    try {
      await requestJSON(`/api/projects/source?revision=${encodeURIComponent(target)}&filename=${encodeURIComponent(file.name)}`, { method: "POST", headers: { "Content-Type": "application/octet-stream" }, body: file, signal: controller.signal });
      if (disposed || revision.value !== target) return;
      const source = library.sources.find(item => item.revision_id === target);
      if (source) source.source_available = true; else library.sources.push({ revision_id: target, source_available: true });
      sourceMessage.textContent = E.saved; sourceState();
    } catch (failure) {
      sourceMessage.replaceChildren(`${E.failed}: ${failure.message} `, h("span", {}, E.mismatch), h("a", { href: `/review.html?lang=${LANG}&project=${encodeURIComponent(project.project_id)}&model=${encodeURIComponent(revisions.find(item => item.revision_id === target)?.model_id || "")}` }, E.newRevision));
    } finally { attach.disabled = false; }
  });
  revision.addEventListener("change", () => { loadRevision(); setPurpose(); }); rule.addEventListener("change", loadRule); purpose.addEventListener("change", setPurpose); scopeKind.addEventListener("change", scopeFields);
  search.addEventListener("input", () => { limit = 100; renderObjects(); }); scopeFields(); refresh();
  return { element, hasDirty: () => !!dirty.size, discard: () => dirty.clear(), dispose: () => { disposed = true; ++generation; ++sourceToken; leaveJob(); controller.abort(); window.removeEventListener("pagehide", leaveJob); } };
}
