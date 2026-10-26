import { h } from "./dom.js";
import { LANG } from "./i18n.js";
import { requestJSON, postJSON } from "./projects-api.js";
import { E } from "./enterprise-words.js";
import { action, field, text, title, facts, details, status } from "./enterprise-ui.js";

export function rulesPanel(projectId, { navigate = next => next() } = {}) {
  let current = null;
  let token = 0;
  let disposed = false;
  let dirty = false;
  const controller = new AbortController();
  const message = h("p", { class: "project-form-message", role: "status", "aria-live": "polite" });
  const history = h("div", { class: "enterprise-history" });
  const content = h("div", { class: "enterprise-rule-content" });
  const input = h("input", { id: "project-rules-file", type: "file", accept: ".zip", hidden: true, "aria-label": E.upload });
  const upload = action(E.upload, () => input.click(), "review-primary");
  upload.disabled = true;
  const element = h("section", { class: "enterprise-panel", "aria-label": E.rules }, h("div", { class: "project-surface enterprise-section" }, h("div", { class: "enterprise-row-heading" }, h("h2", {}, E.rules), h("div", { class: "enterprise-actions" }, upload, h("a", { class: "project-secondary-link", href: "/api/projects/rules/example", download: true }, E.example))), h("p", { class: "project-muted" }, E.zipOnly), input, message), history, content);
  function error(error) { message.textContent = `${E.failed}: ${error.message}`; message.classList.add("is-error"); }
  async function refresh(selected) {
    try {
      const data = await requestJSON(`/api/projects/rules?project=${encodeURIComponent(projectId)}`, { signal: controller.signal });
      if (disposed) return;
      history.replaceChildren(h("h2", {}, E.adopted));
      const revisions = data.rule_revisions || [];
      if (!revisions.length) history.append(h("p", { class: "project-muted" }, E.noRules));
      for (const item of revisions) history.append(action(`${item.title || item.package_id} · ${item.version} · ${item.rule_revision_id.slice(-8)}`, () => navigate(() => open(item.rule_revision_id)), "enterprise-history-item"));
      if (data.previews?.length) history.append(h("details", {}, h("summary", {}, `${E.previews} · ${data.previews.length}`), data.previews.map(item => action(`${item.title || item.filename} · ${item.version || ""}`, () => navigate(() => render(item)), "enterprise-history-item"))));
      const asked = selected || new URL(location.href).searchParams.get("rule_revision");
      if (asked) await open(asked); else if (!current && revisions[0]) await open(revisions[0].rule_revision_id);
    } catch (failure) { if (failure.name !== "AbortError") { error(failure); message.append(" ", action(E.retry, () => refresh(selected))); } }
    finally { if (!disposed) upload.disabled = false; }
  }
  async function open(id) {
    const request = ++token;
    try {
      const data = await requestJSON(`/api/projects/rules/detail?rule_revision=${encodeURIComponent(id)}`, { signal: controller.signal });
      if (request !== token || disposed) return;
      render(data);
      const url = new URL(location.href); url.searchParams.set("rule_revision", id); historyReplace(url);
    } catch (failure) { if (failure.name !== "AbortError") error(failure); }
  }
  function historyReplace(url) { window.history.replaceState(null, "", url); }
  function ruleContent(rule) {
    const card = h("article", { class: "enterprise-rule", id: `enterprise-rule-${rule.rule_id}` }, h("div", { class: "enterprise-row-heading" }, h("h3", {}, `${rule.rule_id} · ${rule.title || ""}`), status(rule.support || "unsupported")), facts([[E.applicability, rule.applicability]]));
    const checks = rule.requirements || [];
    for (const check of checks) card.append(h("div", { class: "enterprise-requirement" }, h("strong", {}, text(check.expected)), status(check.support || rule.support || "unsupported"), check.unsupported_reasons?.length ? h("p", {}, check.unsupported_reasons.map(text).join(" · ")) : null));
    if (rule.unsupported_reasons?.length) card.append(h("p", {}, rule.unsupported_reasons.map(text).join(" · ")));
    if (rule.hypotheses?.length) card.append(h("p", { class: "project-muted" }, `${E.unverified}: ${rule.hypotheses.map(item => item.text || text(item)).join(" · ")}`));
    card.append(details(E.technical, rule)); return card;
  }
  function render(data) {
    current = data; dirty = false;
    const frozen = !!data.rule_revision_id;
    const checks = data.checks || (data.rules || []).flatMap(rule => rule.requirements || []);
    const unsupported = checks.filter(item => item.support === "unsupported");
    const supported = checks.filter(item => item.support === "supported");
    const source = data.source || {};
    content.replaceChildren(h("section", { class: "project-surface enterprise-section" }, h("div", { class: "enterprise-row-heading" }, h("h2", {}, `${frozen ? E.adopted : E.preview} · ${data.title || data.package_id}`), h("code", {}, data.version)),
      facts([[E.source, data.filename], [E.version, `${data.package_id} / ${data.version}`], [E.organization, source.organization], [E.reference, source.reference], [E.issued, source.issued_on]]),
      h("p", { class: "enterprise-execution" }, `${E.supported}: ${supported.length} · ${E.unsupported}: ${unsupported.length}`),
      h("p", { class: "project-muted" }, E.unsupportedNote),
      data.version_reused ? h("p", {}, E.reused) : null,
      frozen ? facts([[E.confirmer, data.confirmed_by], [E.team, data.responsible_team], [E.adoptedBy, data.created_at]]) : null,
      details(E.technical, { source_sha256: data.source_sha256, rule_revision_id: data.rule_revision_id, ruleset: data.ruleset, diagnostics: data.diagnostics, unsupported: data.unsupported })),
      h("section", { class: "project-surface enterprise-section" }, h("h2", {}, E.content), ...(data.rules || []).map(ruleContent)),
      h("section", { class: "project-surface enterprise-section" }, h("h2", {}, E.purpose), ...(data.purposes || []).map(purpose => h("article", { class: "enterprise-rule" }, h("h3", {}, title(purpose)), facts([[E.scope, purpose.subject_classes], [E.content, purpose.required_rule_ids], [E.source, `${purpose.from_role} → ${purpose.to_role}`]]), ...(purpose.evidence_requirements || []).map(item => h("div", {}, h("p", {}, `${item.title} · ${item.execution === "unsupported" ? E.unsupported : E.manual}: ${item.acceptance || ""}`), item.execution === "manual" ? facts([[E.method, item.method_id], [E.basis, item.method_description]]) : h("p", {}, item.reason)))))));
    if (!frozen) {
      const name = h("input", { id: "rules-confirmed-by", type: "text", autocomplete: "off", maxlength: "160" });
      const team = h("input", { id: "rules-responsible-team", type: "text", autocomplete: "off", maxlength: "160" });
      for (const control of [name, team]) control.addEventListener("input", () => { dirty = !!name.value || !!team.value; });
      const save = h("button", { class: "review-primary", type: "submit", disabled: data.can_confirm === false }, E.adopt);
      const note = h("p", { class: "project-form-message", role: "status", id: "rules-confirm-message" });
      for (const control of [name, team]) control.setAttribute("aria-describedby", "rules-confirm-message");
      const form = h("form", { class: "enterprise-form", novalidate: true }, h("p", {}, E.confirmation), h("p", {}, E.methodPolicy), field(E.confirmer, name), field(E.team, team), save, note);
      form.addEventListener("submit", async event => {
        event.preventDefault(); if (save.disabled) return;
        for (const control of [name, team]) control.removeAttribute("aria-invalid");
        const invalid = [name, team].find(control => !control.value.trim());
        if (invalid) { invalid.setAttribute("aria-invalid", "true"); note.textContent = E.required; invalid.focus(); return; }
        save.disabled = name.disabled = team.disabled = true; note.textContent = E.loading;
        try {
          const result = await postJSON("/api/projects/rules/confirm", { project_id: projectId, preview_id: data.preview_id, confirmed_by: name.value.trim(), responsible_team: team.value.trim() });
          if (disposed) return;
          dirty = false; message.textContent = E.saved; message.classList.remove("is-error"); await refresh(result.rule_revision_id);
        } catch (failure) { note.textContent = `${E.failed}: ${failure.message}`; note.classList.add("is-error"); }
        finally { save.disabled = name.disabled = team.disabled = false; }
      });
      content.append(h("section", { class: "project-surface enterprise-section" }, form));
    }
    const selectedRule = new URL(location.href).searchParams.get("rule");
    if (selectedRule) requestAnimationFrame(() => document.getElementById(`enterprise-rule-${selectedRule}`)?.scrollIntoView({ block: "start" }));
  }
  async function uploadFile(file) {
    const request = ++token;
    if (!/\.zip$/i.test(file.name) || !file.size) { error(new Error(E.invalidZip)); return; }
    upload.disabled = true; message.textContent = E.loading; message.classList.remove("is-error");
    try {
      const data = await requestJSON(`/api/projects/rules/preview?project=${encodeURIComponent(projectId)}&filename=${encodeURIComponent(file.name)}`, { method: "POST", headers: { "Content-Type": "application/octet-stream" }, body: file, signal: controller.signal });
      if (!disposed && request === token) { render(data); message.textContent = E.preview; }
    } catch (failure) { if (failure.name !== "AbortError") error(failure); }
    finally { upload.disabled = false; }
  }
  input.addEventListener("change", () => { const file = input.files[0]; input.value = ""; if (file) navigate(() => uploadFile(file)); });
  refresh();
  return { element, hasDirty: () => dirty, discard: () => { dirty = false; }, dispose: () => { disposed = true; ++token; controller.abort(); } };
}
