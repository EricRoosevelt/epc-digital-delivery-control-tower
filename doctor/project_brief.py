"""A downloadable work brief drawn from saved review evidence and local notes."""

from __future__ import annotations

_WORDS = {
    "en": {
        "title": "Project work brief", "model": "Model", "revision": "Revision",
        "checks": "Current review items", "empty": "No saved model revisions.",
        "start": "Save a review to this project to start a model history.",
        "errors": "Needs review", "info": "Information prompts", "element": "Element",
        "rule": "Rule", "observed": "Observed", "owner": "Recorded owner",
        "status": "Follow-up", "note": "Note", "recheck": "Recheck against previous revision",
        "resolved": "Passed on recheck", "remaining": "Still needs review",
        "new": "New findings", "missing": "Not found now",
        "not_applicable": "No longer applicable", "not_comparable": "Not comparable",
        "info_resolved": "Prompts satisfied", "info_remaining": "Prompts remaining",
        "info_new": "New information prompts",
        "before": "Earlier observation", "after": "Current observation",
        "reason": "Explanation",
        "open": "Open", "in_progress": "In progress", "ready_for_recheck": "Ready for recheck",
        "none": "None recorded", "no_items": "No failed review checks in this revision.",
        "basis": "Source: the latest saved revision of each model, on this computer.",
        "boundary": "Marked progress does not change a check result. Missing elements, "
        "changed rules and checks that no longer apply are listed separately from passes. "
        "Information prompts are this tool's defaults; assess their relevance against "
        "your project conventions.",
    },
    "zh": {
        "title": "项目工作简报", "model": "模型", "revision": "版本",
        "checks": "当前需核对事项", "empty": "项目尚未保存模型版本。",
        "start": "将一次检查保存到此项目，开始建立模型历史。",
        "errors": "需核对", "info": "信息提示", "element": "构件",
        "rule": "规则", "observed": "实际读取", "owner": "记录的处理人",
        "status": "处理进展", "note": "备注", "recheck": "与前一版本的复查对比",
        "resolved": "本规则复查通过", "remaining": "仍需核对",
        "new": "新增问题", "missing": "当前未找到",
        "not_applicable": "当前不再适用", "not_comparable": "无法比较",
        "info_resolved": "提示已满足", "info_remaining": "仍有提示", "info_new": "新增提示",
        "before": "原版本读取", "after": "当前版本读取", "reason": "说明",
        "open": "待处理", "in_progress": "处理中", "ready_for_recheck": "待复查",
        "none": "尚未记录", "no_items": "本版本没有未满足的检查项。",
        "basis": "来源：本机保存的每个模型的最新版本。",
        "boundary": "记录处理进展不会改变检查结果。构件未找到、规则改变和检查不再适用，"
        "与复查通过分开列示；信息提示是本工具的默认检查，需要结合项目约定判断。",
    },
}
_CHANGES = ("resolved", "remaining", "new", "missing", "not_applicable", "not_comparable")


def _cell(value) -> str:
    if value is None or value == "":
        return "—"
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\r", "").replace(
        "\n", " / "
    )


def _table(headers, rows) -> list[str]:
    return [
        "| " + " | ".join(_cell(item) for item in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *("| " + " | ".join(_cell(item) for item in row) + " |" for row in rows),
        "",
    ]


def project_brief(library, project_id: str, language: str = "en") -> str:
    """Export every model's latest evidence without turning human notes into passes."""
    if language not in _WORDS:
        raise ValueError("language must be 'en' or 'zh'")
    w = _WORDS[language]
    detail = library.detail(project_id)
    lines = [f"# {w['title']}: {_cell(detail['project']['name'])}", "", w["basis"], "",
             w["boundary"], ""]
    saved = [model for model in detail["models"] if model["revisions"]]
    if not saved:
        return "\n".join([*lines, w["empty"], "", w["start"], ""])
    for model in saved:
        versions = sorted(model["revisions"], key=lambda revision: revision["number"])
        latest = versions[-1]
        record = library.revision(latest["revision_id"])
        report = record["report"]
        summary = report["summary"]
        separator = "：" if language == "zh" else ": "
        lines.extend([
            f"## {_cell(model['name'])}", "",
            f"{w['revision']}: {_cell(latest['label'])} (#{latest['number']})", "",
            f"{w['errors']}{separator}{summary['errors']} · "
            f"{w['info']}{separator}{summary['information']}", "",
            f"### {w['checks']}", "",
        ])
        elements = {item["element_key"]: item for item in report["elements"]}
        followups = {item["finding_id"]: item for item in record["followups"]}
        rows = []
        for finding in report["findings"]:
            if finding["status"] != "FAIL":
                continue
            element = elements.get(finding["element_key"], {})
            progress = followups.get(finding["finding_id"], {})
            status = progress.get("status", "open")
            rows.append([
                element.get("name") or element.get("global_id") or finding["element_key"],
                finding["rule_id"],
                w["info"] if finding["severity"] == "INFO" else w["errors"],
                finding["actual"], progress.get("owner") or w["none"],
                w.get(status, status), progress.get("note") or w["none"],
            ])
        if rows:
            lines.extend(_table(
                [w["element"], w["rule"], w["checks"], w["observed"],
                 w["owner"], w["status"], w["note"]], rows,
            ))
        else:
            lines.extend([w["no_items"], ""])
        if len(versions) > 1:
            comparison = library.compare(versions[-2]["revision_id"], latest["revision_id"])
            lines.extend([f"### {w['recheck']}", ""])
            scope_note = comparison.get("scope_note_zh" if language == "zh" else "scope_note")
            if scope_note:
                lines.extend([scope_note, ""])
            for kind in ("errors", "information"):
                group = "errors" if kind == "errors" else "info"
                lines.extend([
                    f"**{w[group]}**", "",
                    " · ".join(f"{w.get('info_' + key, w[key]) if group == 'info' else w[key]}"
                               f"{separator}{comparison['summary'][kind][key]}"
                               for key in _CHANGES), "",
                ])
            changes = []
            for row in comparison["rows"]:
                changes.append([
                    row.get("after_name") or row.get("before_name") or row.get("global_id"),
                    row["rule_id"],
                    w.get("info_" + row["change"], w[row["change"]])
                    if row["severity"] == "INFO" else w[row["change"]],
                    row.get("before_actual"), row.get("after_actual"),
                    row["reason_zh"] if language == "zh" else row["reason"],
                ])
            if changes:
                lines.extend(_table(
                    [w["element"], w["rule"], w["recheck"], w["before"],
                     w["after"], w["reason"]],
                    changes,
                ))
    return "\n".join(lines).rstrip() + "\n"
