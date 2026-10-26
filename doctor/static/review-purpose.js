import { h } from "./dom.js";
import { LANG } from "./i18n.js";
import { requestJSON } from "./projects-api.js";
import { E } from "./enterprise-words.js";
import { action, text, title, facts, details, status, blockerCard, ruleURL, purposeURL } from "./enterprise-ui.js";

// Purpose evidence has its own identities; it never becomes a base finding.
export function createPurposeReview(onSelect) {
  let run = null;
  let selected = null;
  let requested = false;
  let report = null;
  let current = 0;
  let failure = null;
  const context = h("section", { class: "enterprise-purpose-context", hidden: true, "aria-label": E.assessment });
  function select(item, pickedKey = null) {
    selected = item;
    const url = new URL(location.href); url.searchParams.delete("finding");
    if (item) url.searchParams.set("purpose_finding", item.blocker_id); else url.searchParams.delete("purpose_finding");
    history.replaceState(null, "", url);
    onSelect(item?.review_element_key || pickedKey);
  }
  async function load(baseReport, { fresh, signal }) {
    const token = ++current;
    report = baseReport;
    const params = new URL(location.href).searchParams;
    requested = !fresh && !!params.get("assessment"); run = null; selected = null; failure = null; context.hidden = !requested;
    if (!requested) return;
    context.replaceChildren(h("p", {}, E.loading));
    try {
      const loaded = await requestJSON(`/api/projects/purpose/run?run=${encodeURIComponent(params.get("assessment"))}`, { signal });
      if (token !== current || signal.aborted) return;
      if (loaded.revision_id !== params.get("revision")) throw new Error(E.missingTarget);
      const asked = params.get("purpose_finding");
      const item = asked ? (loaded.blockers || []).find(entry => entry.blocker_id === asked) : loaded.blockers?.[0];
      if (asked && !item) throw new Error(E.missingTarget);
      run = loaded;
      context.replaceChildren(h("strong", {}, `${E.assessment} · ${run.purpose_snapshot ? title(run.purpose_snapshot) : run.purpose_id}`), " ", status(run.conclusion?.status || "UNKNOWN"), h("p", { class: "project-muted" }, `${E.ruleVersion}: ${run.rule_snapshot ? `${run.rule_snapshot.title} · ${run.rule_snapshot.version}` : run.rule_revision_id}`), h("div", { class: "enterprise-actions" }, h("a", { href: purposeURL(run) }, E.back), h("a", { href: ruleURL(run) }, E.ruleLink), h("a", { href: `/review.html?lang=${LANG}&revision=${encodeURIComponent(run.revision_id)}` }, E.base)), details(E.technical, { run_id: run.run_id, revision_id: run.revision_id, rule_revision_id: run.rule_revision_id, source: run.rule_snapshot?.source, confirmed_by: run.rule_snapshot?.confirmed_by, responsible_team: run.rule_snapshot?.responsible_team }));
      select(item || null);
    } catch (error) {
      if (error.name === "AbortError") throw error;
      if (token !== current) return;
      failure = `${E.failed}: ${error.message}`;
      context.replaceChildren(h("p", {}, `${E.failed}: ${error.message}`), action(E.retry, () => load(baseReport, { fresh: false, signal })));
    }
  }
  function renderList({ query, model, limit, more }) {
    const lookup = new Map((report?.elements || []).map(item => [item.element_key, item]));
    const needle = query.trim().toLocaleLowerCase();
    const found = (run?.blockers || []).filter(item => {
      const element = lookup.get(item.review_element_key);
      return (!model || element?.model_key === model) && (!needle || [item.title, item.element_name, item.rule_id, item.evidence_id, element?.global_id, element?.ifc_class].some(value => String(value || "").toLocaleLowerCase().includes(needle)));
    });
    const visible = found.slice(0, limit);
    if (selected && found.indexOf(selected) >= limit) { visible.pop(); visible.unshift(selected); }
    const nodes = visible.map(item => {
      const isSelected = selected?.blocker_id === item.blocker_id;
      const row = action("", () => select(item), `review-finding${isSelected ? " is-selected" : ""}`);
      row.dataset.purposeFinding = item.blocker_id; row.setAttribute("aria-pressed", String(isSelected));
      row.append(h("span", { class: "review-finding-top" }, status(item.verdict || "UNKNOWN"), h("code", {}, item.rule_id || item.evidence_id)), h("strong", {}, item.element_name || item.title), h("span", { class: "review-finding-title" }, item.reason || item.title));
      return row;
    });
    if (!found.length) nodes.push(h("p", { class: "review-empty" }, run ? run.blockers?.length ? E.noMatches : E.noBlockers : failure || E.loading));
    if (found.length > limit) nodes.push(action(E.more, more, "quiet review-load-more"));
    return { nodes, count: found.length, outside: !!selected && !found.includes(selected) };
  }
  function renderDetail() {
    if (!run || !selected) return h("p", { class: "review-detail-empty" }, failure || E.noBlockers);
    const readings = (run.evaluation?.findings || []).filter(item => item.requirement_key === selected.requirement_key && (selected.subject_keys || []).includes(item.element_key || item.subject_key));
    return h("div", { class: "enterprise-purpose-detail" }, blockerCard(run, selected), ...readings.map(item => h("section", { class: "enterprise-section" }, h("h3", {}, E.evidence), facts([[E.expected, item.expected], [E.outcome, item.status], [E.observed, item.actual], [E.basis, item.reason || item.citation]]))), details(E.technical, { run_id: run.run_id, rule_revision_id: run.rule_revision_id, blocker: selected, readings }));
  }
  return { context, load, active: () => requested, renderList, renderDetail,
    summary: () => run?.conclusion,
    pick: key => { select(run?.blockers?.find(item => item.review_element_key === key) || null, key); },
    selected: () => selected,
  };
}
