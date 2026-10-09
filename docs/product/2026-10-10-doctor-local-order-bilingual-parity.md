# Doctor 本地检查的信息顺序与“不等于缺陷”一句：中英义务对照

日期：2026-10-10。负责：Product/UI Engineer。分支 `feat/doctor-local-order`：从 `baf7809` 开工，已用合并提交并入 `1c05dd2`（#58）和 `e067255`（#59）。
依据：
- [PM 进度复看](2026-10-09-pm-progress-review-66e7a57.md)第 2、4 条；
- 技术总监第 4 包；
- BIM 对第 4 包的四条约束。

状态：两句新句**未经 BIM 复核**，交 BIM。其余改动只是位置变化。

“同一义务”的判断标准：两种语言要求读者做的事、承诺或否认的事、限定的范围相同；措辞、语序、标点不同不算。

## 一、新句

| 键 | 中文 | 英文 | 何时显示 | 义务 |
| --- | --- | --- | --- | --- |
| `WORKSPACE.failNotDefectLocal` | 不满足这条产品验证规则，不等于你的模型有交付缺陷。这条规则的来源以返回数据的标签（ProductValidation）和出处原文为准。 | Not meeting this product validation rule does not mean your model has a delivery defect. Where this rule comes from is what the returned data's label (ProductValidation) and the citation as written say. | 本地检查，结果为不通过，且要求的标签含 ProductValidation，紧跟结果 | 同一义务。前半句与已通过的 L017、L018 用词一致；后半句（来源）与 `failNotDefect` 逐字相同 |
| `WORKSPACE.checkFirst` | 动手改之前，先按下面“{heading}”一节核对：在 Revit 里选中的就是这个构件。 | Before changing anything, check against "{heading}" below that the object you have selected in Revit is this element. | 本地检查详情，“要改什么”一节的第一句；`{heading}` 填“回到 Revit 找哪个对象”／"Which object to find in Revit" | 同一义务。只指向已有的核对步骤，不新增核对内容 |

`WORKSPACE.failNotDefect`（“……不等于原项目的交付缺陷。……”）不变，C2 工作区仍用它：那里检查的就是原项目的模型。按模式取句，没有一个键在两处改。

## 二、只换位置（字面不变）

| 页面 | 改前 | 改后 |
| --- | --- | --- |
| 本地结果页 | 练习说明 → 没有适用对象 → 这次检查的范围（规则集、声明的专业、进度计划、几何） → “只有检查结果” → 本次结果 → 检查了什么（规则原话、出处、标签） → 逐条结果 → 追溯 → 记录位置 | 练习说明 → 没有适用对象 → “只有检查结果” → 本次结果 → **逐条结果** → 检查了什么 → 这次检查的范围 → 追溯 → 记录位置 |
| 本地结果详情 | 结果（含读法限制） → 回到 Revit 找哪个对象 → 要改什么 → 具体要求与观察 → 对比 → 追溯 | 结果（含读法限制） → **要改什么**（开头是 `checkFirst`） → 回到 Revit 找哪个对象 → 具体要求与观察 → 对比 → 追溯 |
| 本地起始页 | 上下文栏的“返回首页”加页面里的“← 返回首页” | 只留上下文栏的“返回首页” |
| C2 工作区 | — | 顺序不变（私有工作区 202 页逐字相同） |

## 三、BIM 的四条约束怎样满足

1. **读法限制紧跟各自的结论**：仍都在详情的“结果”一节，紧跟结果，没有挪到“要改什么”或解释区后面。
   - PASS：“它证明／它不证明”，以及“通过的检查结果不带它读到的值”；
   - FAIL：“不等于你的模型有交付缺陷”；
   - N/A：“不适用不是通过”；
   - IFC Tag 核对说明（按 ID 选中、核对名称和类别、对不上时改用 GlobalId）：仍在“回到 Revit 找哪个对象”一节里，`locateBlock` 没有改。“要改什么”移到它前面，但开头的 `checkFirst` 明确指向这一节。类型修改的影响范围（“在 Revit 里改哪里”）本来就在“要改什么”里，没有移到行动之后。
   - 测试 `LocalOrderTests` 守住了以上几点。
2. **本地模式的用词**：`failNotDefectLocal` 与 L017、L018 一致，中文“不等于你的模型有交付缺陷”，英文 "does not mean your model has a delivery defect"。
3. **C2 保留“原项目”**：C2 仍用 `failNotDefect`，按 `state.mode === "local"` 分开取句，测试守住。
4. **来源说明留在 FAIL 句旁**：来源半句仍在同一句里（ProductValidation 标签和出处原文），没有拆开，也没有移走。“检查了什么”一节（标签和出处原文的全文）移到列表之后。

## 四、显示来源（PM 第 4 条）

- 既有记录 `e7838dad4ac0d3b3`（公开 `Building-Hvac.ifc`，暖通）的全部文件里没有 “original project”“原项目” 或 “delivery defect”。PM 看到的那句是 `workspace-screens.js` 按同一个键给两种模式显示的，是显示代码的问题，不是记录保存了旧文案。记录没有改。
- 改后在三份记录上中英都核对过：
  - `e7838dad4ac0d3b3`（PM 打开的 `finding/49f98c89-…`）；
  - 新生成的 `c653c7e0bb676a4a`（暖通加建筑两个文件）；
  - `7b9994459ab5eb1c`（没有适用对象）。
- 不通过的详情页都显示新句，见 PR 的差异清单。
- `doctor/README.md` 的 “a FAIL is not a defect of the original project” 已改为 “a FAIL does not mean your model has a delivery defect”，结果页顺序的说明也已更新。
