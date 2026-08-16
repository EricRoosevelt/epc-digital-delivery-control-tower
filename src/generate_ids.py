from pathlib import Path
import xml.etree.ElementTree as ET
from ifctester import ids


PROJECT_ROOT = Path(__file__).resolve().parents[1]


# IDS 文件的输出位置
OUTPUT_PATH = (
    PROJECT_ROOT
    / "ids"
    / "epc_delivery_requirements_v0.1.ids"
)


def add_specification(
    document,
    identifier,
    name,
    entity_name,
    requirements,
    description,
):
    """
    向 IDS 文档添加一条 specification。

    entity_name 定义适用对象；
    requirements 定义这些对象必须满足的要求。
    """

    specification = ids.Specification(
        name=name,
        identifier=identifier,
        description=description,
        ifcVersion=["IFC4"],
        # minOccurs=0 表示模型中没有适用对象时允许显示 N/A
        minOccurs=0,
        maxOccurs="unbounded",
    )

    # Applicability：确定哪些 IFC 对象接受检查
    specification.applicability.append(
        ids.Entity(name=entity_name)
    )

    # Requirements：添加一项或多项信息要求
    specification.requirements.extend(requirements)

    document.specifications.append(specification)


def make_spatial_requirement():
    """
    创建 HVAC 构件空间归属要求。

    合格的直接空间容器可以是房间 IfcSpace，
    也可以是楼层 IfcBuildingStorey。
    """

    allowed_containers = ids.Restriction(
        options={
            "enumeration": [
                "IFCSPACE",
                "IFCBUILDINGSTOREY",
            ]
        },
        base="string",
    )

    return ids.PartOf(
        name=allowed_containers,
        relation="IFCRELCONTAINEDINSPATIALSTRUCTURE",
        cardinality="required",
        instructions=(
            "Assign the HVAC element directly to an "
            "IfcSpace or IfcBuildingStorey."
        ),
    )


def make_epc_metadata_requirements():
    """
    创建本项目假设的 EPC 交付元数据要求。

    同一 specification 中的两项要求使用 AND 逻辑，
    即 AssetTag 和 SystemCode 都必须存在。
    """

    return [
        ids.Property(
            propertySet="EPC_Delivery",
            baseName="AssetTag",
            dataType="IFCLABEL",
            cardinality="required",
            instructions=(
                "Provide the project-assumed EPC asset tag."
            ),
        ),
        ids.Property(
            propertySet="EPC_Delivery",
            baseName="SystemCode",
            dataType="IFCLABEL",
            cardinality="required",
            instructions=(
                "Provide the project-assumed EPC system code."
            ),
        ),
    ]


# 创建 IDS 文档及其基本说明
document = ids.Ids(
    title="EPC Digital Delivery Requirements",
    version="0.1",
    description=(
        "Project-authored information requirements for "
        "the EPC Digital Delivery Control Tower prototype."
    ),
    purpose=(
        "Validate selected information requirements in "
        "public multidisciplinary IFC sample models."
    ),
    milestone="Portfolio prototype",
)


# R-001：墙必须具有 Name
add_specification(
    document=document,
    identifier="R-001",
    name="Walls must have a name",
    entity_name="IFCWALL",
    requirements=[
        ids.Attribute(
            name="Name",
            cardinality="required",
            instructions="Provide a non-empty IFC Name.",
        )
    ],
    description=(
        "Checks whether every applicable IfcWall "
        "provides its IFC Name attribute."
    ),
)


# R-002：墙必须具有 IsExternal 属性
add_specification(
    document=document,
    identifier="R-002",
    name="Walls must declare IsExternal",
    entity_name="IFCWALL",
    requirements=[
        ids.Property(
            propertySet="Pset_WallCommon",
            baseName="IsExternal",
            dataType="IFCBOOLEAN",
            cardinality="required",
            instructions=(
                "Declare whether the wall is external."
            ),
        )
    ],
    description=(
        "Checks the presence and IFC data type of "
        "Pset_WallCommon.IsExternal."
    ),
)


# R-003：梁必须具有 LoadBearing 属性
add_specification(
    document=document,
    identifier="R-003",
    name="Beams must declare LoadBearing",
    entity_name="IFCBEAM",
    requirements=[
        ids.Property(
            propertySet="Pset_BeamCommon",
            baseName="LoadBearing",
            dataType="IFCBOOLEAN",
            cardinality="required",
            instructions=(
                "Declare whether the beam is load-bearing."
            ),
        )
    ],
    description=(
        "Checks the presence and IFC data type of "
        "Pset_BeamCommon.LoadBearing."
    ),
)


# R-004 分成两条 specification，分别检查风管和风口
add_specification(
    document=document,
    identifier="R-004A",
    name="Duct segments need spatial assignment",
    entity_name="IFCDUCTSEGMENT",
    requirements=[make_spatial_requirement()],
    description=(
        "Checks whether each IfcDuctSegment is directly "
        "contained in an IfcSpace or IfcBuildingStorey."
    ),
)

add_specification(
    document=document,
    identifier="R-004B",
    name="Air terminals need spatial assignment",
    entity_name="IFCAIRTERMINAL",
    requirements=[make_spatial_requirement()],
    description=(
        "Checks whether each IfcAirTerminal is directly "
        "contained in an IfcSpace or IfcBuildingStorey."
    ),
)


# R-005 是本项目假设的 EPC 信息要求
# 它不是 buildingSMART 样例文件必须遵守的官方要求
add_specification(
    document=document,
    identifier="R-005A",
    name="Duct segments need assumed EPC metadata",
    entity_name="IFCDUCTSEGMENT",
    requirements=make_epc_metadata_requirements(),
    description=(
        "Project-specific assumed EPC delivery requirement "
        "for IfcDuctSegment elements."
    ),
)

add_specification(
    document=document,
    identifier="R-005B",
    name="Air terminals need assumed EPC metadata",
    entity_name="IFCAIRTERMINAL",
    requirements=make_epc_metadata_requirements(),
    description=(
        "Project-specific assumed EPC delivery requirement "
        "for IfcAirTerminal elements."
    ),
)


# 创建 ids 目录并写出 XML 格式的 IDS 文件
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
document.to_xml(str(OUTPUT_PATH))


# 重新读取刚生成的文件，验证它能被 IfcTester 正常解析
loaded_document = ids.open(
    str(OUTPUT_PATH),
    validate=True,
)

if len(loaded_document.specifications) != 7:
    raise ValueError(
        "Generated IDS does not contain 7 specifications"
    )


# IfcTester 0.8.5 重新读取 IDS 后，没有将 specification 的
# identifier 恢复到 Python 对象中，因此直接从 XML 检查编号
IDS_NAMESPACE = {
    "ids": "http://standards.buildingsmart.org/IDS"
}

xml_root = ET.parse(OUTPUT_PATH).getroot()

specification_nodes = xml_root.findall(
    ".//ids:specification",
    IDS_NAMESPACE,
)

expected_identifiers = [
    "R-001",
    "R-002",
    "R-003",
    "R-004A",
    "R-004B",
    "R-005A",
    "R-005B",
]

actual_identifiers = [
    node.get("identifier")
    for node in specification_nodes
]

if actual_identifiers != expected_identifiers:
    raise ValueError(
        "Unexpected IDS identifiers: "
        f"{actual_identifiers}"
    )


print(
    f"Wrote {len(specification_nodes)} "
    f"specifications to {OUTPUT_PATH}"
)

for node in specification_nodes:
    print(
        f"- {node.get('identifier')}: "
        f"{node.get('name')}"
    )
