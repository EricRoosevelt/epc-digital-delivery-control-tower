from pathlib import Path

import ifcopenshell
import ifcopenshell.util.element
import pandas as pd


# rows 用于暂存从所有 IFC 构件中提取出来的记录
# 列表中的每个字典，最终都会成为 CSV 中的一行
rows = []

# 查找 data/raw 目录下的所有 IFC 文件
# sorted 用于保证每次处理文件的顺序一致
raw_paths = sorted(Path("data/raw").glob("*.ifc"))

# 如果没有找到 IFC 文件，就立即停止并显示明确的错误
if not raw_paths:
    raise FileNotFoundError("No IFC files found in data/raw")


# 依次处理每个 IFC 模型
for path in raw_paths:
    # 使用 IfcOpenShell 打开当前 IFC 文件
    model = ifcopenshell.open(str(path))

    # IfcElement 是大多数实体构件的父级类型
    # 墙、梁、楼板、家具和风管等通常都属于 IfcElement
    for element in model.by_type("IfcElement"):
        global_id = getattr(element, "GlobalId", None)

        # 明确查找构件所属的 IfcBuildingStorey
        # 如果找不到真正的楼层，storey 就会是 None
        storey = ifcopenshell.util.element.get_container(
            element,
            ifc_class="IfcBuildingStorey",
        )

        # 只读取 Property Set，不把 Quantity Set 计算在内
        psets = ifcopenshell.util.element.get_psets(
            element,
            psets_only=True,
        )

        # 把当前构件的选定字段追加到 rows 列表
        rows.append(
            {
                # GlobalId 可能在不同专业模型中重复，因此使用来源模型组成联邦唯一键
                "element_key": f"{path.name}::{global_id or element.id()}",
                "source_model": path.name,
                "discipline": path.stem.removeprefix("Building-"),
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


# 设置处理结果的输出位置
output = Path("data/processed/model_inventory.csv")
output.parent.mkdir(parents=True, exist_ok=True)

# 把字典列表转换成 DataFrame，再写入 CSV
df = pd.DataFrame(rows)
df.to_csv(output, index=False, encoding="utf-8-sig")

# 在控制台显示处理总数和按专业、IFC 类型统计的结果
print(f"Wrote {len(df)} elements to {output}")
print(df.groupby(["discipline", "ifc_class"]).size().head(20))
