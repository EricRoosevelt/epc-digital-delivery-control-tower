import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import ifcopenshell
import pandas as pd
from ifctester import ids, reporter


# 取得项目根目录，使脚本不依赖当前 PowerShell 所在位置
PROJECT_ROOT = Path(__file__).resolve().parents[1]

IDS_PATH = (
    PROJECT_ROOT
    / "ids"
    / "epc_delivery_requirements_v0.1.ids"
)

MODELS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "models.csv"
)

INVENTORY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "model_inventory.csv"
)

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "reports" / "ids"

FINDINGS_OUTPUT = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ids_findings.csv"
)


# ids_findings.csv 的固定列顺序
FINDING_COLUMNS = [
    "run_id",
    "model_id",
    "element_key",
    "global_id",
    "ids_version",
    "specification",
    "requirement",
    "status",
    "severity",
    "ifc_class",
    "element_name",
    "expected",
    "actual",
    "reason",
]


# XML 中的 IDS 命名空间
IDS_NAMESPACE = {
    "ids": "http://standards.buildingsmart.org/IDS"
}


def calculate_sha256(path):
    """计算文件的 SHA-256 内容摘要。"""

    hasher = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            hasher.update(chunk)

    return hasher.hexdigest()


def read_ids_metadata():
    """
    直接从 XML 读取 IDS 版本、规则编号和名称。

    IfcTester 0.8.5 重新读取 IDS 后，不会把 identifier
    恢复到 Python specification 对象，因此这里读取原始 XML。
    """

    root = ET.parse(IDS_PATH).getroot()

    version_node = root.find(
        "ids:info/ids:version",
        IDS_NAMESPACE,
    )

    if version_node is None or not version_node.text:
        raise ValueError("IDS version is missing")

    specification_nodes = root.findall(
        ".//ids:specification",
        IDS_NAMESPACE,
    )

    specification_ids = {}

    for node in specification_nodes:
        name = node.get("name")
        identifier = node.get("identifier")

        if not name or not identifier:
            raise ValueError(
                "An IDS specification has no name or identifier"
            )

        if name in specification_ids:
            raise ValueError(
                f"Duplicate IDS specification name: {name}"
            )

        specification_ids[name] = identifier

    return version_node.text, specification_ids


def build_run_id(
    ids_version,
    ids_hash,
    models_df,
):
    """
    根据 IDS 内容和三个 IFC 文件的内容生成稳定 run_id。

    输入不变时 run_id 不变；
    IDS 或任一 IFC 改变时 run_id 随之改变。
    """

    hasher = hashlib.sha256()
    hasher.update(f"ids:{ids_hash}\n".encode("utf-8"))

    for row in models_df.sort_values(
        "model_id"
    ).itertuples(index=False):
        hasher.update(
            (
                f"{row.model_id}:"
                f"{row.content_sha256}\n"
            ).encode("utf-8")
        )

    return (
        f"ids-v{ids_version}-"
        f"{hasher.hexdigest()[:16]}"
    )


def get_specification_status(specification_report):
    """
    将 IfcTester 的状态转换成 PASS、FAIL 或 N/A。

    IfcTester 会把 0/0 显示为 PASS；
    本项目必须把零适用对象规范化为 N/A。
    """

    total_applicable = int(
        specification_report.get(
            "total_applicable",
            0,
        )
        or 0
    )

    if (
        specification_report.get("is_skipped")
        or total_applicable == 0
    ):
        return "N/A"

    if specification_report.get("status"):
        return "PASS"

    return "FAIL"


def get_severity(identifier, status):
    """
    根据规则来源和结果确定 Finding 严重度。

    R-005 是本项目假设的 EPC 要求，失败只记为 WARNING。
    其他规则失败记为 ERROR。
    PASS 和 N/A 不是问题，因此记为 INFO。
    """

    if status != "FAIL":
        return "INFO"

    if identifier.startswith("R-005"):
        return "WARNING"

    return "ERROR"


def validate_model(model_row):
    """
    验证一个 IFC 模型，同时生成 JSON 和 HTML 原始报告。

    每个模型都重新读取 IDS，防止上一个模型的验证状态
    残留到下一个模型中。
    """

    model_id = model_row.model_id
    ifc_path = RAW_DATA_DIR / model_row.filename

    if not ifc_path.exists():
        raise FileNotFoundError(
            f"IFC file not found: {ifc_path}"
        )

    # 验证原始 IFC 内容与 models.csv 中记录的哈希一致
    actual_hash = calculate_sha256(ifc_path)

    if actual_hash != model_row.content_sha256:
        raise ValueError(
            f"IFC content hash changed: {model_row.filename}"
        )

    specifications = ids.open(str(IDS_PATH))
    model = ifcopenshell.open(str(ifc_path))

    specifications.validate(model)

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    json_path = REPORT_DIR / f"{model_id}.json"
    html_path = REPORT_DIR / f"{model_id}.html"

    # 生成供程序读取的 JSON 报告
    json_reporter = reporter.Json(specifications)
    json_reporter.report()
    json_reporter.to_file(str(json_path))

    # 生成供人阅读的 HTML 报告
    html_reporter = reporter.Html(specifications)
    html_reporter.report()
    html_reporter.to_file(str(html_path))

    # IfcTester 的 HTML 模板包含行尾空格。清理格式噪声，
    # 使生成报告可以通过 Git whitespace 检查。
    html_content = html_path.read_text(
        encoding="utf-8-sig",
    )
    cleaned_html = "\n".join(
        line.rstrip()
        for line in html_content.splitlines()
    )
    html_path.write_text(
        f"{cleaned_html}\n",
        encoding="utf-8",
    )

    # 从刚刚生成的 JSON 读取真实报告结构
    with json_path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        report_data = json.load(file)

    print(f"Validated {model_row.filename}")

    return report_data


def add_na_findings(
    findings,
    run_id,
    model_id,
    ids_version,
    identifier,
    specification_name,
    requirements,
):
    """
    为零适用对象的 specification 生成 N/A 记录。

    一项 requirement 对应一行 N/A；
    N/A 没有具体构件，因此构件字段留空。
    """

    for requirement in requirements:
        label = (
            requirement.get("label")
            or requirement.get("description")
            or "Unnamed requirement"
        )

        expected = (
            requirement.get("description")
            or label
        )

        findings.append(
            {
                "run_id": run_id,
                "model_id": model_id,
                "element_key": "",
                "global_id": "",
                "ids_version": ids_version,
                "specification": (
                    f"{identifier}: "
                    f"{specification_name}"
                ),
                "requirement": label,
                "status": "N/A",
                "severity": "INFO",
                "ifc_class": "",
                "element_name": "",
                "expected": expected,
                "actual": "",
                "reason": (
                    "No applicable elements "
                    "exist in this model."
                ),
            }
        )


def add_entity_findings(
    findings,
    entities,
    status,
    run_id,
    model_id,
    ids_version,
    identifier,
    specification_name,
    requirement,
    element_lookup,
):
    """
    将通过或失败的构件结果转换成扁平 Finding 行。
    """

    label = (
        requirement.get("label")
        or requirement.get("description")
        or "Unnamed requirement"
    )

    expected = (
        requirement.get("description")
        or label
    )

    for entity in entities:
        global_id = entity.get("global_id")

        if not global_id:
            raise ValueError(
                "A non-N/A finding has no GlobalId"
            )

        lookup_key = (model_id, global_id)
        element_key = element_lookup.get(lookup_key)

        if not element_key:
            raise ValueError(
                "Validation element not found in inventory: "
                f"{lookup_key}"
            )

        if status == "PASS":
            reason = "Requirement satisfied."
        else:
            reason = (
                entity.get("reason")
                or "Requirement not satisfied."
            )

        findings.append(
            {
                "run_id": run_id,
                "model_id": model_id,
                "element_key": element_key,
                "global_id": global_id,
                "ids_version": ids_version,
                "specification": (
                    f"{identifier}: "
                    f"{specification_name}"
                ),
                "requirement": label,
                "status": status,
                "severity": get_severity(
                    identifier,
                    status,
                ),
                "ifc_class": (
                    entity.get("class")
                    or ""
                ),
                "element_name": (
                    entity.get("name")
                    or ""
                ),
                "expected": expected,
                # IfcTester 的 JSON 没有稳定提供属性实际值；
                # 不编造数据，暂时保留为空
                "actual": "",
                "reason": reason,
            }
        )


def normalize_report(
    report_data,
    model_id,
    run_id,
    ids_version,
    specification_ids,
    element_lookup,
):
    """
    把一个模型的嵌套 JSON 报告转换成 Finding 行。
    """

    findings = []

    for specification in report_data[
        "specifications"
    ]:
        specification_name = specification["name"]

        identifier = specification_ids.get(
            specification_name
        )

        if not identifier:
            raise ValueError(
                "Specification name not found in IDS XML: "
                f"{specification_name}"
            )

        requirements = specification.get(
            "requirements",
            [],
        )

        specification_status = (
            get_specification_status(specification)
        )

        print(
            f"  {identifier}: "
            f"{specification_status}"
        )

        if specification_status == "N/A":
            add_na_findings(
                findings=findings,
                run_id=run_id,
                model_id=model_id,
                ids_version=ids_version,
                identifier=identifier,
                specification_name=specification_name,
                requirements=requirements,
            )
            continue

        for requirement in requirements:
            passed_entities = (
                requirement.get(
                    "passed_entities",
                    [],
                )
                or []
            )

            failed_entities = (
                requirement.get(
                    "failed_entities",
                    [],
                )
                or []
            )

            total_applicable = int(
                requirement.get(
                    "total_applicable",
                    0,
                )
                or 0
            )

            # 每个 requirement 的通过数和失败数
            # 应当等于其适用构件总数
            if (
                len(passed_entities)
                + len(failed_entities)
                != total_applicable
            ):
                raise ValueError(
                    "Requirement entity counts "
                    "do not reconcile: "
                    f"{identifier} "
                    f"{requirement.get('label')}"
                )

            add_entity_findings(
                findings=findings,
                entities=passed_entities,
                status="PASS",
                run_id=run_id,
                model_id=model_id,
                ids_version=ids_version,
                identifier=identifier,
                specification_name=specification_name,
                requirement=requirement,
                element_lookup=element_lookup,
            )

            add_entity_findings(
                findings=findings,
                entities=failed_entities,
                status="FAIL",
                run_id=run_id,
                model_id=model_id,
                ids_version=ids_version,
                identifier=identifier,
                specification_name=specification_name,
                requirement=requirement,
                element_lookup=element_lookup,
            )

    return findings


def main():
    """执行三个模型的批量 IDS 验证。"""

    required_inputs = [
        IDS_PATH,
        MODELS_PATH,
        INVENTORY_PATH,
    ]

    for path in required_inputs:
        if not path.exists():
            raise FileNotFoundError(
                f"Required input not found: {path}"
            )

    models_df = pd.read_csv(
        MODELS_PATH,
        dtype=str,
    ).fillna("")

    inventory_df = pd.read_csv(
        INVENTORY_PATH,
        dtype=str,
    ).fillna("")

    # 同一个模型中的 GlobalId 必须唯一，
    # 才能可靠回到 element_key
    duplicated_elements = inventory_df.duplicated(
        subset=["model_id", "global_id"],
        keep=False,
    )

    if duplicated_elements.any():
        raise ValueError(
            "Duplicate model_id + global_id "
            "found in model inventory"
        )

    element_lookup = {
        (row.model_id, row.global_id): row.element_key
        for row in inventory_df.itertuples(index=False)
    }

    ids_version, specification_ids = (
        read_ids_metadata()
    )

    ids_hash = calculate_sha256(IDS_PATH)

    run_id = build_run_id(
        ids_version=ids_version,
        ids_hash=ids_hash,
        models_df=models_df,
    )

    print(f"Validation run: {run_id}")

    all_findings = []

    for model_row in models_df.sort_values(
        "model_id"
    ).itertuples(index=False):
        report_data = validate_model(model_row)

        model_findings = normalize_report(
            report_data=report_data,
            model_id=model_row.model_id,
            run_id=run_id,
            ids_version=ids_version,
            specification_ids=specification_ids,
            element_lookup=element_lookup,
        )

        all_findings.extend(model_findings)

    findings_df = pd.DataFrame(
        all_findings,
        columns=FINDING_COLUMNS,
    )

    if findings_df.empty:
        raise ValueError(
            "Validation produced no findings"
        )

    # 固定排序，保证相同输入重复运行时 CSV 顺序一致
    findings_df = findings_df.sort_values(
        [
            "model_id",
            "specification",
            "requirement",
            "element_key",
            "status",
        ]
    ).reset_index(drop=True)

    # 同一次验证中，一项要求对同一模型构件只能产生一条结果。
    # N/A 记录的 element_key 为空，但 specification 和 requirement
    # 仍可共同保证每项不适用要求只有一行。
    finding_key_columns = [
        "run_id",
        "model_id",
        "specification",
        "requirement",
        "element_key",
    ]

    duplicated_findings = findings_df.duplicated(
        subset=finding_key_columns,
        keep=False,
    )

    if duplicated_findings.any():
        duplicate_keys = findings_df.loc[
            duplicated_findings,
            finding_key_columns,
        ].to_dict("records")

        raise ValueError(
            "Duplicate normalized findings: "
            f"{duplicate_keys}"
        )

    # 所有非 N/A 结果都必须关联到一个真实构件
    non_na = findings_df[
        findings_df["status"] != "N/A"
    ]

    if (
        non_na["element_key"].eq("").any()
        or non_na["global_id"].eq("").any()
    ):
        raise ValueError(
            "A non-N/A finding has no element key"
        )

    known_element_keys = set(
        inventory_df["element_key"]
    )

    unknown_element_keys = (
        set(non_na["element_key"])
        - known_element_keys
    )

    if unknown_element_keys:
        raise ValueError(
            "Unknown element keys in findings: "
            f"{unknown_element_keys}"
        )

    FINDINGS_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    findings_df.to_csv(
        FINDINGS_OUTPUT,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"Wrote {len(findings_df)} findings "
        f"to {FINDINGS_OUTPUT}"
    )

    print(
        findings_df.groupby(
            ["model_id", "status"]
        ).size()
    )

    print(
        "Findings SHA-256: "
        f"{calculate_sha256(FINDINGS_OUTPUT)}"
    )


if __name__ == "__main__":
    main()
