"""Compare frozen review evidence within a stable project/model slot.

GlobalId is the only cross-revision object join. Names, STEP identifiers,
file names, hashes, finding IDs and manual follow-ups never establish identity
or machine closure. Ambiguous identities remain separate observations.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping
from copy import deepcopy
import hashlib
import json
import re

__all__ = ["compare_revisions"]

_GUID = re.compile(r"[0-3][0-9A-Za-z_$]{21}\Z")
_CHANGES = ("resolved", "remaining", "new", "missing", "not_applicable", "not_comparable")
_PREDICATE_KEYS = (
    "rule_id", "expected", "scope", "checker", "predicate_version", "version",
    "semantics_digest", "applicability", "severity",
)
_REASONS = {
    "resolved": (
        "The same rule changed from FAIL to PASS for this unique GlobalId. "
        "This rule's recheck passed; it is not overall model acceptance.",
        "同一唯一 GlobalId 的同一规则由 FAIL 变为 PASS；仅表示本规则复查通过，不是整体验收。",
    ),
    "remaining": (
        "The same rule still reports FAIL. Compare the exported evidence before deciding "
        "what action, if any, the project requires.",
        "同一规则仍为 FAIL。先比较导出证据，再判断项目是否需要进一步处理。",
    ),
    "new": (
        "The current revision reports FAIL without an earlier FAIL for this object and rule.",
        "当前版本出现本对象、本规则的新增 FAIL，旧版没有对应 FAIL。",
    ),
    "missing": (
        "The previously failing GlobalId was not found in the current model. "
        "Removal or an identity change is not evidence that the check passed.",
        "旧版未通过构件的 GlobalId 未在当前模型中找到；删除或标识变更不证明检查已通过。",
    ),
    "not_applicable": (
        "The prior FAIL is now NOT_APPLICABLE under an unchanged rule and IFC class. "
        "No positive pass is established.",
        "规则和 IFC 类别未变，旧版 FAIL 在当前为不适用；这不是通过判定。",
    ),
    "rule_changed": (
        "The rule snapshot, effective expected value, version or applicability changed "
        "or is absent. Its results cannot establish a repair under the earlier predicate.",
        "规则快照、期望值、版本或适用范围已变化或缺失，不能据此认定旧规则下的问题已修正。",
    ),
    "class_changed": (
        "The same GlobalId has a different IFC class. Review the classification change "
        "before interpreting the rule result as an improvement.",
        "同一 GlobalId 的 IFC 类别发生变化；需先核对分类变更，不能直接认定检查结果改善。",
    ),
    "schema_changed": (
        "The IFC schema changed between revisions; the checking basis needs review.",
        "两版 IFC 模式不同，需要先核对检查依据。",
    ),
    "scope_changed": (
        "The report's single-file/federated model scope changed. "
        "Cross-file identities cannot be paired by GlobalId alone.",
        "报告的单文件或联邦模型范围发生变化，不能仅按 GlobalId 跨文件配对。",
    ),
    "federated_report": (
        "This report contains multiple IFC files. Reopening is supported; revision "
        "comparison currently requires a single-file model slot to avoid cross-file joins.",
        "报告含多个 IFC 文件，可保存并重开；本轮修订比较要求单文件模型槽，避免跨文件误配。",
    ),
    "invalid_or_duplicate_global_id": (
        "GlobalId is invalid, duplicated or lacks evidence of uniqueness among all "
        "IfcRoot objects in its file. These observations are not paired across revisions.",
        "GlobalId 无效、重复，或缺少文件内全部 IfcRoot 唯一性证据；两版观察结果不作配对。",
    ),
    "missing_finding": (
        "One revision has no corresponding finding for the existing element. "
        "Absence of a finding is not a PASS.",
        "现存构件在某一版缺少对应检查记录；没有记录不等于 PASS。",
    ),
    "ambiguous_finding": (
        "More than one finding represents this element and rule in a revision; "
        "no unique result can be compared.",
        "某版同一构件、规则存在多条检查记录，无法确定唯一比较结果。",
    ),
    "unknown_status": (
        "A check result is neither PASS, FAIL nor NOT_APPLICABLE; no repair can be inferred.",
        "检查结果不是 PASS、FAIL 或不适用，不能推断已修正。",
    ),
}


def _predicate(rule, finding=None):
    if rule is None:
        return None
    result = {key: deepcopy(rule[key]) for key in _PREDICATE_KEYS if key in rule}
    if finding is not None:
        result["finding_expected"] = deepcopy(finding.get("expected"))
    return result


def _versioned(rule):
    return rule is not None and any(rule.get(key) for key in
                                    ("predicate_version", "semantics_digest", "version"))


def _index(report):
    elements = defaultdict(list)
    findings = defaultdict(lambda: defaultdict(list))
    rules = defaultdict(list)
    for element in report.get("elements", []):
        elements[str(element.get("global_id") or "")].append(element)
    for finding in report.get("findings", []):
        findings[finding.get("element_key")][finding.get("rule_id")].append(finding)
    for rule in report.get("rules", []):
        rules[rule.get("rule_id")].append(rule)
    return elements, findings, rules


def _unique(element, group, findings):
    guid = str(element.get("global_id") or "")
    if not _GUID.fullmatch(guid) or len(group) != 1:
        return False
    count = element.get("global_id_count")
    if count is not None:
        return type(count) is int and count == 1
    # Historical reports can establish this through the frozen identity check.
    identity = findings[element.get("element_key")].get("ID-001", [])
    return len(identity) == 1 and identity[0].get("status") == "PASS"


def _one(items):
    return items[0] if len(items) == 1 else None


def _schema(report):
    return sorted(str(m.get("schema") or "") for m in report.get("models", []))


def _basis_change(before, after):
    bm, am = before.get("models", []), after.get("models", [])
    if len(bm) != len(am):
        return "scope_changed"
    if len(bm) > 1:
        # This is a scope check only, never a cross-file element correspondence.
        def roster(models):
            return sorted((str(m.get("model_key") or ""), str(m.get("name") or ""))
                          for m in models)
        return "federated_report" if roster(bm) == roster(am) else "scope_changed"
    if not bm:
        return "scope_changed"
    if _schema(before) != _schema(after):
        return "schema_changed"
    return None


def compare_revisions(before: Mapping, after: Mapping) -> dict:
    """Return six evidence-change categories, separately counted by severity.

    Inputs are ``{revision: {...}, report: {...}, followups: [...]}`` envelopes.
    The library also checks scope; this function rejects a cross-slot call on
    its own. Immutable reports carry the rule predicates that were evaluated.
    Unchanged non-failing checks are omitted from the attention list.
    """
    br, ar = before.get("revision", {}), after.get("revision", {})
    for key in ("project_id", "model_id"):
        if not br.get(key) or br.get(key) != ar.get(key):
            raise ValueError("Compare revisions in the same project and stable model slot.")
    bp, ap = before["report"], after["report"]
    be, bf, b_rules = _index(bp)
    ae, af, a_rules = _index(ap)
    rows = []

    def append(b_element, a_element, rule_id, b_items, a_items, change, reason_code):
        b = b_items[0] if b_items else None
        a = a_items[0] if a_items else None
        b_rule, a_rule = _one(b_rules[rule_id]), _one(a_rules[rule_id])
        severity = (a or b or {}).get("severity") or (a_rule or b_rule or {}).get(
            "severity", "INFO"
        )
        guid = (a_element or b_element or {}).get("global_id") or ""
        reason, reason_zh = _REASONS[reason_code]
        if severity == "INFO" and reason_code in {"resolved", "remaining", "new"}:
            reason = {
                "resolved": "The same information prompt now reports PASS. This satisfies "
                "the prompt only; it does not establish project acceptance.",
                "remaining": "The same information prompt remains. Confirm whether the "
                "project needs a change or whether the existing data is appropriate.",
                "new": "The current revision has a new information prompt. Its FAIL "
                "status does not itself establish a model defect.",
            }[reason_code]
            reason_zh = {
                "resolved": "同一信息提示本次为 PASS，仅表示提示条件已满足，不代表项目验收。",
                "remaining": "同一信息提示仍存在；需判断项目是否需要修改，或现有信息是否合理。",
                "new": "当前版本新增信息提示；其 FAIL 状态本身不表示模型缺陷。",
            }[reason_code]
        row = {
            "global_id": guid, "rule_id": rule_id, "change": change,
            "severity": severity, "title": (a or b or {}).get("title", rule_id),
            "reason": reason, "reason_zh": reason_zh, "reason_code": reason_code,
            "before_predicate": _predicate(b_rule, b),
            "after_predicate": _predicate(a_rule, a),
            "before_finding_count": len(b_items), "after_finding_count": len(a_items),
        }
        for prefix, element, finding in (("before", b_element, b), ("after", a_element, a)):
            for name in ("finding_id", "status", "actual", "expected", "citation"):
                row[f"{prefix}_{name}"] = finding.get(name) if finding else None
            for name, source in (("element_key", "element_key"), ("class", "ifc_class"),
                                 ("name", "name")):
                row[f"{prefix}_{name}"] = element.get(source) if element else None
        identity = [br.get("revision_id"), ar.get("revision_id"), br["model_id"], guid,
                    rule_id, row["before_element_key"], row["after_element_key"]]
        row["key"] = hashlib.sha256(json.dumps(identity).encode()).hexdigest()[:24]
        rows.append(row)

    def unpaired(element, side, code):
        index = bf if side == "before" else af
        for rule_id, items in sorted(index[element.get("element_key")].items()):
            if not any(item.get("status") == "FAIL" for item in items):
                continue
            append(element if side == "before" else None,
                   element if side == "after" else None, rule_id,
                   items if side == "before" else [], items if side == "after" else [],
                   "not_comparable", code)

    basis_change = _basis_change(bp, ap)
    for guid in sorted(set(be) | set(ae)):
        b_group, a_group = be[guid], ae[guid]
        if basis_change:
            for side, group in (("before", b_group), ("after", a_group)):
                for element in group:
                    unpaired(element, side, basis_change)
            continue
        unique = all(_unique(e, group, index) for group, index in
                     ((b_group, bf), (a_group, af)) for e in group)
        if not unique:
            for side, group in (("before", b_group), ("after", a_group)):
                for element in group:
                    unpaired(element, side, "invalid_or_duplicate_global_id")
            continue
        b_element, a_element = _one(b_group), _one(a_group)
        b_findings = bf[b_element.get("element_key")] if b_element else {}
        a_findings = af[a_element.get("element_key")] if a_element else {}
        for rule_id in sorted(set(b_findings) | set(a_findings)):
            b_items, a_items = b_findings.get(rule_id, []), a_findings.get(rule_id, [])
            b, a = _one(b_items), _one(a_items)
            b_rule, a_rule = _one(b_rules[rule_id]), _one(a_rules[rule_id])
            bs, ass = (b or {}).get("status"), (a or {}).get("status")
            code = None
            if len(b_items) > 1 or len(a_items) > 1:
                code = "ambiguous_finding"
            elif (not _versioned(b_rule) or not _versioned(a_rule) or
                  _predicate(b_rule) != _predicate(a_rule) or
                  b and a and b.get("expected") != a.get("expected")):
                code = "rule_changed"
            elif (b_element and a_element and
                  b_element.get("ifc_class") != a_element.get("ifc_class")):
                code = "class_changed"
            elif b_element and a_element and (b is None or a is None):
                code = "missing_finding"
            elif any(s is not None and s not in {"PASS", "FAIL", "NOT_APPLICABLE"}
                     for s in (bs, ass)):
                code = "unknown_status"
            if code:
                append(b_element, a_element, rule_id, b_items, a_items,
                       "not_comparable", code)
                continue
            change = None
            if bs == "FAIL":
                if a_element is None:
                    change = "missing"
                else:
                    change = {"PASS": "resolved", "FAIL": "remaining",
                              "NOT_APPLICABLE": "not_applicable"}.get(ass)
            elif ass == "FAIL":
                change = "new"
            if change:
                append(b_element, a_element, rule_id, b_items, a_items, change, change)

    rows.sort(key=lambda r: (r["global_id"], r["rule_id"], r["before_element_key"] or "",
                            r["after_element_key"] or ""))
    counts = Counter(row["change"] for row in rows)
    summary = {change: counts[change] for change in _CHANGES}
    for label, severity in (("errors", "ERROR"), ("information", "INFO")):
        counts = Counter(row["change"] for row in rows if row["severity"] == severity)
        summary[label] = {change: counts[change] for change in _CHANGES}
    scope_note, scope_note_zh = _REASONS[basis_change] if basis_change else (
        "Single-file comparison uses only valid GlobalIds proven unique within each file. "
        "Unpaired observations list failed checks only; "
        "full evidence remains in each revision.",
        "单文件比较只配对已证实在文件内唯一的合法 GlobalId；无法配对时仅列未通过检查，"
        "完整证据仍保留在各版本中。",
    )
    return {"before_revision": deepcopy(dict(br)), "after_revision": deepcopy(dict(ar)),
            "summary": summary, "rows": rows, "basis_change": basis_change,
            "scope_note": scope_note, "scope_note_zh": scope_note_zh}
