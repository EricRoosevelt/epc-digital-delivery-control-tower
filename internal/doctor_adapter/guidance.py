"""Deterministic engineering guidance grounded in a review finding.

This is the local explanation of the check, also usable as evidence context for
an optional language model. It neither chooses design values nor changes a model
or review state. The check result, not a workflow label, controls the advice.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

__all__ = ["guidance_for"]


# Each entry is: failure summary, actions, verification, limitation, pass summary.
_EN = {
    "PV-001": (
        "The effective air-terminal type is outside the four values in PV-001.",
        [
            "Locate this instance in the source model and confirm its function. For a roof cap "
            "or chimney component, check the IFC class mapping before changing its type.",
            "Inspect the assigned type and instance: the checker reads the type first, with "
            "fallback to the instance when the type provides no effective value. USERDEFINED "
            "may supply free text through ElementType or ObjectType.",
            "Choose a supported value only after confirming the object's function and the "
            "delivery requirement. A shared type change can affect every linked instance. "
            "Do not choose DIFFUSER, GRILLE, LOUVRE or REGISTER just to make the check pass; "
            "retain a justified classification and record an exception when appropriate.",
        ],
        [
            "Save and re-export the IFC, then upload it as a new revision and rerun PV-001. "
            "Compare the effective value and class for this object and other instances of "
            "the changed type; a recorded action alone does not verify the export.",
        ],
        "PV-001 is this repository's product rule. IFC also permits USERDEFINED and "
        "NOTDEFINED. A pass checks the effective text against four values; it does not "
        "establish semantic correctness, airflow performance or statutory compliance.",
        "The effective type matches one of the four PV-001 values.",
    ),
    "INFO-001": (
        "The exported element has no non-blank instance Name for readable identification.",
        [
            "Use GlobalId, tag and the view to identify the source instance. Confirm the "
            "project's naming convention before supplying a meaningful name; do not invent "
            "a label from the IFC class alone.",
            "Inspect the export mapping for the instance Name. A type name is a separate "
            "attribute and does not automatically fill the instance Name. If a shared "
            "mapping changes, check other affected instances too.",
        ],
        [
            "Save and re-export, upload the new revision, and rerun INFO-001. Confirm the "
            "instance Name is non-blank and useful to a reader, not just a placeholder.",
        ],
        "Name is optional in IFC for these elements. This is a readability prompt, not a "
        "schema defect or an assessment of the project's naming convention.",
        "The exported instance Name is non-blank.",
    ),
    "INFO-002": (
        "No building storey was resolved through the element's spatial hierarchy.",
        [
            "Inspect containment and decomposition parents in the source model, including "
            "a host or assembly. Confirm whether a building storey is appropriate for this "
            "object; site assets and multi-storey objects may need a different convention.",
            "If storey grouping is required, correct the source assignment or export "
            "relationship. Do not infer or assign a storey from coordinates alone. For an "
            "assembly change, inspect its child instances and hosting relationships.",
        ],
        [
            "Save and re-export, upload the new revision, and rerun INFO-002. Inspect the "
            "resolved storey and the containment/decomposition chain; compare with the "
            "source assignment, especially for hosted and multi-storey objects.",
        ],
        "This prompt supports storey-based navigation. It does not prove a room assignment, "
        "physical location, required IFC containment level or an error in a site-level asset.",
        "A building storey was resolved through the spatial hierarchy.",
    ),
    "ID-001": (
        "The element's GlobalId is malformed or repeated in the same file.",
        [
            "Use the model and local element key to locate the source object; a repeated "
            "GlobalId cannot identify it uniquely. Compare all objects using that ID in "
            "the same file to distinguish a duplicate export from distinct source objects.",
            "Correct the source identity or export process, preserving unaffected GlobalIds "
            "and checking existing issue references. Do not regenerate every ID or edit "
            "only a displayed label; a duplicate object may instead need export deduplication.",
        ],
        [
            "Save and re-export, upload the new revision, and rerun ID-001. Confirm valid "
            "compressed GlobalIds and uniqueness against all IfcRoot objects in that file. "
            "Check continuity of references for every intentionally changed ID.",
        ],
        "The check establishes format and uniqueness only within the uploaded file. Matching "
        "IDs in different models need federation context; a pass does not prove identity "
        "stability between revisions or worldwide uniqueness.",
        "The GlobalId has valid compressed format and is unique in this file.",
    ),
}

_ZH = {
    "PV-001": (
        "读取到的风口有效类型不在 PV-001 接受的四个值内。",
        [
            "在源模型中定位该实例并确认实际用途。若对象是屋面帽或烟囱部件，"
            "先核对 IFC 类别映射，再决定是否需要修改类型。",
            "同时查看实例及其关联类型：检查器优先读取类型，类型没有有效值时再回退到实例。"
            "USERDEFINED 可通过类型的 ElementType 或实例的 ObjectType 提供自由文本。",
            "根据对象用途和交付要求确认应填的值；修改共享类型会影响所有关联实例。不要为通过检查"
            "而猜填 DIFFUSER、GRILLE、LOUVRE 或 REGISTER。现有分类合理时，"
            "可保留分类并记录例外依据。",
        ],
        [
            "保存源模型并重新导出 IFC，以新修订上传后重跑 PV-001。比较该对象及同类型其他实例的"
            "有效类型和 IFC 类别；处理记录本身不能证明导出结果已修正。",
        ],
        "PV-001 是本仓库的产品规则。IFC 还允许 USERDEFINED 和 NOTDEFINED。通过只说明有效文本"
        "命中四个值之一，不能证明分类语义、气流性能或法规合规。",
        "读取到的有效类型属于 PV-001 接受的四个值之一。",
    ),
    "INFO-001": (
        "导出构件的实例 Name 为空，缺少便于阅读的名称。",
        [
            "结合 GlobalId、标记和视图定位源模型实例，先确认项目命名约定，再填写有意义的名称；"
            "不要只根据 IFC 类别猜名称。",
            "核对实例 Name 的导出映射。类型名称是另一个属性，不会自动成为实例 Name。修改共享"
            "映射时，一并查看其他受影响实例。",
        ],
        [
            "保存并重新导出 IFC，以新修订上传后重跑 INFO-001。确认实例 Name 非空且便于识别，"
            "不是仅用于通过检查的占位文本。",
        ],
        "对这些构件，Name 是 IFC 可选属性。本项是可读性提示，不表示 IFC 结构缺陷，也不验证"
        "项目命名约定是否满足。",
        "导出构件的实例 Name 非空。",
    ),
    "INFO-002": (
        "沿构件的空间层级未解析到建筑楼层。",
        [
            "查看源模型中的空间容纳和分解父级，包括宿主或装配体。先确认该对象是否适合归入"
            "建筑楼层；场地设施和跨楼层构件可能采用其他约定。",
            "若交付需要按楼层分组，修正源模型归属或导出关系。不要仅按坐标推断或指定楼层。"
            "修改装配体归属时，同时检查子实例及宿主关系。",
        ],
        [
            "保存并重新导出 IFC，以新修订上传后重跑 INFO-002。核对解析出的楼层及空间容纳、"
            "分解关系链是否与源模型一致，特别检查宿主构件和跨楼层构件。",
        ],
        "本项用于按楼层定位，不能证明房间归属或实际位置，也不表示 IFC 必须按此层级容纳构件；"
        "场地级对象未解析到楼层不一定需要修改。",
        "已沿空间层级解析到建筑楼层。",
    ),
    "ID-001": (
        "该构件的 GlobalId 格式不正确，或在同一文件中重复。",
        [
            "结合模型和本地构件键定位源对象，重复的 GlobalId 无法单独唯一定位。比较同一文件中"
            "使用该标识的全部对象，分清重复导出与不同源对象错误共用标识。",
            "修正源对象标识或导出流程，保留未受影响的 GlobalId，并检查已有问题引用。不要批量"
            "重建所有标识或只修改显示标签；重复导出的对象也可能需要从导出范围中去重。",
        ],
        [
            "保存并重新导出 IFC，以新修订上传后重跑 ID-001。对文件中全部 IfcRoot 对象检查压缩"
            "GlobalId 格式和唯一性，并核对主动变更的标识能否继续关联原有问题引用。",
        ],
        "本项仅检查当前上传文件内的格式和唯一性。不同模型使用相同标识需要结合模型联邦关系判断；"
        "通过不证明跨修订身份稳定或全球唯一。",
        "GlobalId 压缩格式正确，且在当前文件内唯一。",
    ),
}


def _text(value: Any) -> str:
    """Preserve zero/false and deterministic structured evidence without guessing."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return str(value)


def guidance_for(
    finding: Mapping, element: Mapping | None, language: str = "en"
) -> dict:
    """Explain the supplied evidence; never infer a repair from workflow state."""
    zh = str(language).lower().startswith("zh")
    rule = _text(finding.get("rule_id"))
    status = _text(finding.get("status")).upper()
    entry = (_ZH if zh else _EN).get(rule)
    absent = "未记录" if zh else "not recorded"
    facts = []
    for key, en, cn in (
        ("finding_id", "Finding", "检查记录"),
        ("rule_id", "Rule", "规则"),
        ("status", "Check result", "检查结果"),
        ("expected", "Expected", "期望"),
        ("actual", "Observed", "实际读取"),
        ("reason", "Checker explanation", "检查器说明"),
    ):
        facts.append(f"{cn if zh else en}: {_text(finding.get(key)) or absent}")
    if element is not None:
        for key, en, cn in (
            ("element_key", "Element", "构件键"),
            ("model_key", "Model", "模型"),
            ("global_id", "GlobalId", "GlobalId"),
            ("ifc_class", "IFC class", "IFC 类别"),
            ("name", "Name", "名称"),
            ("storey", "Resolved storey", "解析楼层"),
        ):
            facts.append(f"{cn if zh else en}: {_text(element.get(key)) or absent}")

    if entry is None:
        summary = "此规则尚无专用指导。" if zh else "This rule has no specific guidance yet."
        actions = [
            "按检查记录核对规则依据和源对象，再决定是否修改；不要猜填目标值。" if zh else
            "Review the cited requirement and source object before deciding on a change; "
            "do not invent a target value."
        ]
        verification = [
            "变更后重新导出、上传并运行同一规则，比较新旧证据。" if zh else
            "After a change, re-export, upload and rerun the same rule; compare the evidence."
        ]
        limitations = [
            "本地尚无该规则的专用工程指导。" if zh else
            "There is no rule-specific local engineering guidance for this rule."
        ]
    else:
        summary, actions, verification, limitation, pass_summary = entry
        actions, verification = list(actions), list(verification)
        limitations = [limitation]
        if status == "PASS":
            summary = pass_summary
            actions = [
                "本次检查不要求修正。结合项目用途核对信息含义后，可保留当前导出值。" if zh else
                "No correction is requested by this check. Keep the exported value after "
                "confirming its meaning for the project's use."
            ]
            verification = [
                "后续模型修订时，上传新导出并重跑同一检查，比较本项证据。" if zh else
                "On a later model revision, upload the new export and rerun this check; "
                "compare this evidence."
            ]

    if status in {"NOT_APPLICABLE", "N/A", "NA"}:
        summary = "该对象不在本项适用范围内，本项未作通过判定。" if zh else (
            "This check does not apply to the object; it is not a pass."
        )
        actions = [
            "不要为使本项适用而修改模型值。仅在范围与预期不符时，"
            "核对类别和规则适用条件。" if zh else
            "Do not change model values to make this rule apply. If the scope is unexpected, "
            "inspect the IFC class and the rule's applicability."
        ]
        verification = [
            "核对本项适用条件与模型对象；范围变更后重新运行检查。" if zh else
            "Compare applicability with the model objects; rerun after any scope change."
        ]
    elif status not in {"PASS", "FAIL"}:
        summary = "本项未获得可解释的检查结果，尚不能判定对象是否满足规则。" if zh else (
            "This check has not produced an interpretable result; "
            "satisfaction is not established."
        )
        actions = [
            "不要据此修改模型值。先核对检查器说明、上传文件及规则支持情况。" if zh else
            "Do not change model values from this result. Inspect the checker explanation, "
            "uploaded file and rule support first."
        ]
        verification = [
            "解决读取或执行问题后，重新运行检查并取得明确结果。" if zh else
            "Resolve the reading or execution problem, then rerun for a definite result."
        ]

    citation = _text(finding.get("citation"))
    return {
        "summary": summary,
        "facts": facts,
        "actions": actions,
        "verification": verification,
        "citations": [{"id": rule, "label": citation}] if citation else [],
        "limitations": limitations,
    }
