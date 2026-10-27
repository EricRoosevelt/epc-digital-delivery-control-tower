// Presentation only. The sealed server conclusion is never recomputed here.
const words = {
  en: {
    failed: "Check unmet", manualUnmet: "Human review unmet", manualPending: "Human evidence needed",
    unsupported: "Not executed this run", pending: "Check result needs verification", identity: "Verify element identity",
    unnamed: "Unnamed element", context: "Assessment context", empty: "Empty value", unobserved: "No check result obtained",
    confirmed: "Human record: confirmed satisfied", unmet: "Human record: unmet", unconfirmed: "No accepted human confirmation",
    objects: "Objects needing attention", failures: "Unmet machine checks", manualFailures: "Unmet human reviews",
    gaps: "Pending evidence observations", countNote: "One object can have several requirements. These counts are evidence observations, not defect totals.",
    incomplete: "This purpose has not been fully assessed. Review the missing context or evidence above.",
    passed: "Same machine rule passed on recheck", remaining_BLOCKED: "Still unmet", remaining_UNKNOWN: "Still unconfirmed",
    missing: "Not found in current revision", class_changed: "Object class changed", scope_excluded: "Excluded from assessment scope",
    not_comparable: "Not directly comparable", evidence_updated: "Determination or evidence changed", unchanged: "Conclusion unchanged",
    changeDetail: "View individual recheck observations", noRepair: "Removal, class or scope changes and changed human evidence are not counted as model repairs.",
  },
  zh: {
    failed: "检查未通过", manualUnmet: "人工复核未满足", manualPending: "待补人工证据",
    unsupported: "本轮无法执行", pending: "检查结果待核对", identity: "构件身份待核对",
    unnamed: "未命名构件", context: "审查上下文", empty: "空值", unobserved: "未取得检查结果",
    confirmed: "人工记录：已确认满足", unmet: "人工记录：未满足", unconfirmed: "尚无被采纳的人工确认",
    objects: "需关注构件", failures: "检查未通过", manualFailures: "人工复核未满足",
    gaps: "待核对证据", countNote: "同一构件可能对应多项要求。检查与证据按观察项计数，不是缺陷总数。",
    incomplete: "本次尚未完成用途判断，请核对上方缺少的上下文或证据。",
    passed: "同一机器规则复检已通过", remaining_BLOCKED: "仍未满足", remaining_UNKNOWN: "仍待核对",
    missing: "本版未找到", class_changed: "构件分类已变", scope_excluded: "已移出本次范围",
    not_comparable: "不可直接比较", evidence_updated: "人工判定或证据变化", unchanged: "结论未变",
    changeDetail: "查看逐项复检变化", noRepair: "删除、分类或范围变化，以及人工证据变化，均不计为模型修正。",
  },
};
export const resultWords = language => words[language === "zh" ? "zh" : "en"];
export function noticeText(value, language = "en") {
  if (language !== "zh") return value;
  return {
    "Readiness concerns only this purpose, scope and exact evidence versions.": "结论仅适用于本次用途、范围和所列证据版本。",
    "User-recorded judgments are not signatures or risk authorisations.": "人工记录不等于工程签认或风险接纳。",
    "No purpose subjects in the declared scope": "声明范围内没有适用于本用途的对象。",
    "An actual counterpart revision is required": "本用途需要选择真实的对方模型修订。",
  }[value] || value;
}
const display = value => typeof value === "object" ? JSON.stringify(value) : String(value);
export const problemPriority = blocker => blocker.kind === "machine" && blocker.verdict === "BLOCKED" ? 0 : blocker.kind === "manual" && blocker.verdict === "BLOCKED" ? 1 : 2;
export const orderedProblems = run => [...(run.blockers || [])].sort((a, b) => problemPriority(a) - problemPriority(b));

export function problemReading(run, blocker, language = "en") {
  const w = resultWords(language);
  const elements = (run.evaluation?.elements || []).filter(item => (blocker.subject_keys || []).includes(item.element_key));
  const manual = blocker.kind === "manual";
  const unsupported = blocker.kind === "unsupported" || [...(run.evaluation?.checks || []), ...(run.evaluation?.coverage || [])].some(item => item.requirement_key === blocker.requirement_key && (item.execution === "unsupported" || item.support === "unsupported"));
  const invalid = elements.some(item => item.identity_comparable === false);
  const label = invalid ? w.identity : unsupported ? w.unsupported : manual ? blocker.verdict === "BLOCKED" ? w.manualUnmet : w.manualPending : blocker.verdict === "BLOCKED" ? w.failed : w.pending;
  const request = manual ? (run.evidence_requests || []).find(item => item.blocker_id === blocker.blocker_id) : null;
  const actual = manual ? request?.current_outcome === "confirmed" ? w.confirmed : request?.current_outcome === "unmet" ? w.unmet : w.unconfirmed
    : blocker.actual !== "" && blocker.actual !== null && blocker.actual !== undefined ? display(blocker.actual) : blocker.finding_key ? w.empty : w.unobserved;
  return {
    name: blocker.element_name || elements.map(item => item.name || `${w.unnamed} · ${item.ifc_class}`).join(" · ") || w.context,
    label, actual,
    priority: problemPriority(blocker),
  };
}

export function resultSummary(run) {
  const rows = run.blockers || [];
  return {
    objects: new Set(rows.flatMap(item => item.subject_keys || [])).size,
    failed: rows.filter(item => item.kind === "machine" && item.verdict === "BLOCKED").length,
    manualUnmet: rows.filter(item => item.kind === "manual" && item.verdict === "BLOCKED").length,
    pending: rows.filter(item => item.verdict === "UNKNOWN").length,
    observations: rows.length,
  };
}

export function recheckSummary(run) {
  const counts = {};
  for (const item of run.change_summary?.outcomes || []) {
    const key = item.change === "remaining" ? `remaining_${item.after}` : item.change;
    counts[key] = (counts[key] || 0) + 1;
  }
  return counts;
}
