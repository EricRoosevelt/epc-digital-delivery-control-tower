import { h } from "./dom.js";
import { E } from "./enterprise-words.js";
import { LANG } from "./i18n.js";

export const text = value => value === null || value === undefined || value === "" ? "—" : typeof value === "object" ? JSON.stringify(value) : String(value);
export const title = item => LANG === "zh" ? item?.title_zh || item?.title || item?.purpose_id || "—" : item?.title || item?.purpose_id || "—";
export const field = (name, input) => h("label", {}, h("span", {}, name), input);
export const action = (name, handler, cls = "") => h("button", { type: "button", class: cls, onclick: handler }, name);
export const details = (name, value) => h("details", { class: "enterprise-technical" }, h("summary", {}, name), h("pre", {}, JSON.stringify(value, null, 2)));
export const facts = rows => h("dl", { class: "enterprise-facts" }, rows.flatMap(([key, value]) => [h("dt", {}, key), h("dd", {}, text(value))]));
export const status = value => h("span", { class: `enterprise-status state-${value}` }, E[value] || text(value));
export const ruleURL = run => `/projects.html?lang=${LANG}&project=${encodeURIComponent(run.project_id)}&tab=rules&rule_revision=${encodeURIComponent(run.rule_revision_id)}`;
export const purposeURL = run => `/projects.html?lang=${LANG}&project=${encodeURIComponent(run.project_id)}&tab=purpose&assessment=${encodeURIComponent(run.run_id)}`;
export const findingURL = (run, blocker) => `/review.html?lang=${LANG}&revision=${encodeURIComponent(run.revision_id)}&assessment=${encodeURIComponent(run.run_id)}&purpose_finding=${encodeURIComponent(blocker.blocker_id)}`;

export function finiteRows(items, row) {
  const node = h("div", { class: "enterprise-finite" });
  let offset = 0;
  const append = () => {
    node.append(...items.slice(offset, offset + 100).map(row)); offset += 100;
    if (items.length > offset) {
      const more = action(E.more, () => { more.remove(); append(); }); node.append(more);
    }
  };
  append(); return node;
}

export function blockerCard(run, blocker) {
  const node = h("article", { class: "enterprise-blocker", id: `purpose-blocker-${blocker.blocker_id}` }, h("div", { class: "enterprise-row-heading" }, h("h3", {}, blocker.element_name || blocker.title || blocker.rule_id || E.evidence), status(blocker.verdict || "UNKNOWN")),
    h("p", {}, blocker.reason || blocker.title), facts([[E.evidence, blocker.rule_id || blocker.evidence_id], [E.expected, blocker.expected], [E.observed, blocker.actual], [E.next, LANG === "zh" ? blocker.next_action_zh || blocker.next_action : blocker.next_action], [E.recheck, blocker.recheck_condition]]),
    h("div", { class: "enterprise-actions" }, blocker.review_element_key ? h("a", { class: "project-secondary-link", href: findingURL(run, blocker) }, E.locate) : h("span", { class: "project-muted" }, E.missingTarget), h("a", { href: `${ruleURL(run)}${blocker.rule_id ? `&rule=${encodeURIComponent(blocker.rule_id)}` : ""}` }, E.ruleLink)));
  if (blocker.hypotheses?.length) node.append(h("details", {}, h("summary", {}, `${E.hypotheses} · ${E.unverified}`), h("ul", {}, blocker.hypotheses.map(item => h("li", {}, item.text || text(item))))));
  node.append(details(E.technical, blocker));
  return node;
}

export function changeSummary(run) {
  const change = run.change_summary;
  const section = h("section", { class: "enterprise-changes" }, h("h3", {}, E.changes));
  if (!change) { section.append(h("p", { class: "project-muted" }, E.noChanges)); return section; }
  if (change.basis_changes?.length) section.append(h("p", {}, E.basisNote));
  for (const item of change.basis_changes || []) section.append(h("article", { class: "enterprise-rule enterprise-basis-change", "data-kind": item.kind }, h("h3", {}, E[`basis_${item.kind}`] || item.kind), facts([[E.before, item.before], [E.after, item.after]])));
  const names = new Map((run.evaluation?.elements || []).map(item => [item.element_key, item.name || item.ifc_class]));
  const rows = h("div", { class: "enterprise-change-outcomes" });
  let limit = 100;
  const render = () => {
    rows.replaceChildren(...(change.outcomes || []).slice(0, limit).map(item => h("article", { class: "enterprise-rule enterprise-change-row", "data-change": item.change }, h("h3", {}, E[`change_${item.change}`] || item.change), h("p", {}, (item.subject_keys || []).map(key => names.get(key) || key).join(" · ")), facts([[E.evidence, item.evidence_id], [E.before, E[`reading_${item.before}`] || item.before], [E.after, E[`reading_${item.after}`] || item.after]]), details(E.technical, { subject_keys: item.subject_keys, review_element_key: item.review_element_key, change: item.change }))));
    if (change.outcomes?.length > limit) rows.append(action(E.more, () => { limit += 100; render(); }, "enterprise-more-changes"));
  };
  render(); section.append(rows, details(E.technical, change));
  if (!change.basis_changes?.length && !change.outcomes?.length) section.append(h("p", { class: "project-muted" }, E.noChanges));
  return section;
}

export function draftGuard(getPanel) {
  let pending = null;
  const keep = action(E.keep, () => { pending = null; dialog.close(); });
  const leave = action(E.discard, () => { const next = pending; pending = null; getPanel()?.discard?.(); dialog.close(); next?.(); });
  const dialog = h("dialog", { class: "project-draft-dialog", "aria-labelledby": "enterprise-draft-title", "aria-describedby": "enterprise-draft-body" }, h("h2", { id: "enterprise-draft-title" }, E.unsavedTitle), h("p", { id: "enterprise-draft-body" }, E.unsavedBody), h("div", { class: "project-dialog-actions" }, keep, leave));
  document.body.append(dialog);
  const request = next => { if (!getPanel()?.hasDirty?.()) { next(); return; } pending = next; dialog.showModal(); keep.focus(); };
  document.addEventListener("click", event => {
    const target = event.target.closest("a[href], .language-switch button");
    if (!target || target.hasAttribute("download") || target.closest("dialog") || !getPanel()?.hasDirty?.()) return;
    event.preventDefault(); event.stopImmediatePropagation(); request(() => target.click());
  }, true);
  window.addEventListener("beforeunload", event => { if (getPanel()?.hasDirty?.()) { event.preventDefault(); event.returnValue = ""; } });
  dialog.addEventListener("cancel", () => { pending = null; });
  return request;
}
