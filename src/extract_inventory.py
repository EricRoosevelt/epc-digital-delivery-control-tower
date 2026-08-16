import hashlib
from pathlib import Path

import ifcopenshell
import ifcopenshell.util.element
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


# buildingSMART 官方样例所在的基础网址
SOURCE_BASE_URL = (
    "https://github.com/buildingSMART/Sample-Test-Files/blob/main/"
    "IFC%204.0.2.1%20%28IFC%204%29/PCERT-Sample-Scene"
)


# 为三个已知模型定义稳定的项目标识和专业名称
# 不直接从文件名随意推断，是为了保持输出字段长期稳定
MODEL_METADATA = {
    "Building-Architecture.ifc": {
        "model_id": "architecture",
        "discipline": "Architecture",
    },
    "Building-Structural.ifc": {
        "model_id": "structural",
        "discipline": "Structural",
    },
    "Building-Hvac.ifc": {
        "model_id": "hvac",
        "discipline": "HVAC",
    },
}


def calculate_sha256(path):
    """计算文件内容的 SHA-256 摘要。"""

    hasher = hashlib.sha256()

    # 使用二进制模式读取文件，避免文本编码或换行转换影响哈希
    with path.open("rb") as file:
        # 每次读取 1 MB，避免将大型 IFC 一次性全部放入内存
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


# model_rows 保存模型级记录，最终写入 models.csv
# element_rows 保存构件级记录，最终写入 model_inventory.csv
model_rows = []
element_rows = []


# 查找并排序全部原始 IFC 文件
raw_paths = sorted(
    (PROJECT_ROOT / "data" / "raw").glob("*.ifc")
)

if not raw_paths:
    raise FileNotFoundError("No IFC files found in data/raw")


# 依次处理每个 IFC 模型
for path in raw_paths:
    metadata = MODEL_METADATA.get(path.name)

    # 如果出现合同之外的文件，立即停止，避免生成含义不明确的数据
    if metadata is None:
        raise ValueError(f"No model metadata configured for {path.name}")

    model = ifcopenshell.open(str(path))

    # 每个样例模型应当只有一个 IfcProject
    projects = model.by_type("IfcProject")

    if len(projects) != 1:
        raise ValueError(
            f"{path.name} contains {len(projects)} IfcProject records; "
            "expected exactly 1"
        )

    project = projects[0]
    project_guid = getattr(project, "GlobalId", None)

    if not project_guid:
        raise ValueError(f"IfcProject in {path.name} has no GlobalId")

    # 每个 IFC 文件向 model_rows 添加一条模型级记录
    model_rows.append(
        {
            "model_id": metadata["model_id"],
            "filename": path.name,
            "discipline": metadata["discipline"],
            "ifc_project_guid": project_guid,
            "ifc_schema": model.schema,
            "content_sha256": calculate_sha256(path),
            "source_url": f"{SOURCE_BASE_URL}/{path.name}",
            "license": "CC BY 4.0",
        }
    )

    # 提取当前模型中的全部 IfcElement
    for element in model.by_type("IfcElement"):
        global_id = getattr(element, "GlobalId", None)

        # element_key 依赖 GlobalId，因此缺失时不能静默生成不完整数据
        if not global_id:
            raise ValueError(
                f"Element #{element.id()} in {path.name} has no GlobalId"
            )

        # 明确查找构件所属的 IfcBuildingStorey
        storey = ifcopenshell.util.element.get_container(
            element,
            ifc_class="IfcBuildingStorey",
        )

        # 只读取 Property Set，不把 Quantity Set 计算在内
        psets = ifcopenshell.util.element.get_psets(
            element,
            psets_only=True,
        )

        # 每个构件向 element_rows 添加一条构件级记录
        element_rows.append(
            {
                "model_id": metadata["model_id"],
                "source_model": path.name,
                "discipline": metadata["discipline"],
                "element_key": (
                    f"{metadata['model_id']}::{global_id}"
                ),
                "global_id": global_id,
                "ifc_class": element.is_a(),
                "name": getattr(element, "Name", None),
                "storey": (
                    getattr(storey, "Name", None)
                    if storey
                    else None
                ),
                "pset_count": len(psets),
            }
        )


# 将两组记录分别转换成 DataFrame
models_df = pd.DataFrame(model_rows)
inventory_df = pd.DataFrame(element_rows)


# 显式排序，保证相同输入重复运行时行顺序一致
models_df = models_df.sort_values(
    ["model_id"]
).reset_index(drop=True)

inventory_df = inventory_df.sort_values(
    ["model_id", "element_key"]
).reset_index(drop=True)


# 在写出文件前检查数据合同中的唯一性约束
if not models_df["model_id"].is_unique:
    raise ValueError("model_id is not unique")

if not models_df["filename"].is_unique:
    raise ValueError("filename is not unique")

if not inventory_df["element_key"].is_unique:
    raise ValueError("element_key is not unique")


# 检查库存中的全部 model_id 都能够回到 models.csv
unknown_model_ids = (
    set(inventory_df["model_id"])
    - set(models_df["model_id"])
)

if unknown_model_ids:
    raise ValueError(
        f"Unknown model_id values in inventory: {unknown_model_ids}"
    )


# 创建输出目录，并分别写出模型表和构件库存表
output_dir = PROJECT_ROOT / "data" / "processed"
output_dir.mkdir(parents=True, exist_ok=True)

models_output = output_dir / "models.csv"
inventory_output = output_dir / "model_inventory.csv"

models_df.to_csv(
    models_output,
    index=False,
    encoding="utf-8-sig",
)

inventory_df.to_csv(
    inventory_output,
    index=False,
    encoding="utf-8-sig",
)


# 输出执行摘要
print(f"Wrote {len(models_df)} models to {models_output}")
print(f"Wrote {len(inventory_df)} elements to {inventory_output}")
print(
    inventory_df.groupby(
        ["discipline", "ifc_class"]
    ).size().head(20)
)
