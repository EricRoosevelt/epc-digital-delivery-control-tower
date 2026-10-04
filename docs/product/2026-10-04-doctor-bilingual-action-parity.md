# Doctor 中英文行动义务对照（P0）

日期：2026-10-04。负责：Product/UI Engineer。基线 `98601fc`。
依据：[98601fc 首次访客复走](2026-10-04-pm-revisit-and-product-potential.md)“最重要的双语证据”、
[公开展示与审计说明](2026-10-04-pm-public-display-audit-release-update.md)第 1 节、[D1–D6](2026-10-04-pm-six-decisions.md) 的 D6，
以及技术总监的 P0 任务包。状态：本文件列出的英文句子**全部未经 BIM 复核**，进 10/8 批次。

## 问题与根因

`#/fixture/member-evidence/item/2/1/0`（house - chimney）：中文要求先确认项目是否要求它具备资产标识；英文显示 Pack 的
`next_action` 原文，要求对全范围重跑评估，并以 “Not a model defect” 开头。两者的义务不同。

根因：中文的“要做什么”和“完成后拿什么复检”来自按问题类型裁定的 `ACTIONS` 表（BIM 约束第 3 节的表；烟囱资产标识一句是
产品裁定，见[中文词表](2026-10-02-doctor-recheck-vocabulary.md)第 12、13 节）。英文（#33 起）在同一位置读记录路由里的
`next_action`、`recheck_condition`，复检单项的“复检前留下的结束条件”读 `prior_recheck_condition`。

## 一、中文显示裁定句、英文显示原文的地方（全部位置）

先确认来源：随附样例的 12 份记录都属于 `interdisciplinary-coordination-readiness` 0.1.0，记录路由里的英文与 Pack
`resolution_routes[]` 逐字相同（脚本逐条比较，0 处不同）。所以下表每一行的“原英文”就是 Pack 的原句。

用到这些句子的位置有四类页面，七处：

| 页面 | 位置 | 中文读 | 英文（改前）读 |
| --- | --- | --- | --- |
| 首次结果列表 | 每张事项卡片的“要做什么” | `ACTIONS[kind].action` | 路由 `next_action` |
| 单项页 | “要做什么” | `ACTIONS[kind].action` | 路由 `next_action` |
| 单项页 | “完成后拿什么复检” | `ACTIONS[kind].recheck` | 路由 `recheck_condition` |
| 复检页（事项列表） | 每张卡片的“要做什么” | `ACTIONS[kind].action` | 路由 `next_action` |
| 复检单项页 | “要做什么” | `ACTIONS[kind].action` | 路由 `next_action` |
| 复检单项页 | “完成后拿什么复检” | `ACTIONS[kind].recheck` | 路由 `recheck_condition` |
| 复检单项页 | “复检前留下的结束条件” | `ACTIONS[prior_kind].recheck` | `prior_recheck_condition` |

实测（`98601fc`，英文，162 个公开页面）：记录原文作为行动或复检句出现在折叠之外的页面有 118 个（单项 16、复检单项 91、
列表 11），其中 106 个同时出现 Overlay、requirement_key 或 “Not a model defect”。改后：0 个。

工作区各页（真实检查）不读记录路由：PV-001 的规则说明两种语言都是本界面写的句子，逐条对照见第三节。

### 逐条对照：问题类型 × 行动

“出现在样例里”指随附样例里有没有这种问题类型的事项（当前事项／复检前的事项）。

| 问题类型 | 样例 | 原中文（不变） | 原英文（Pack，改前显示） | 新英文 | 义务差异 |
| --- | --- | --- | --- | --- | --- |
| `asset-identity-not-evaluated` | 12 份／9 份 | 现有资产标识规则没有覆盖到这个构件，所以它有没有资产标识还没有被评估，不能判断是否缺少；这项工作能否开始也因此无法判断。先确认项目约定是否要求它具备资产标识，以及规则该不该覆盖到它。在确认之前，这不表示它必须具备资产标识。 | Not a model defect: run (or re-run) the asset-identity evaluation over the full assessed scope so every element it covers actually produces a PASS or FAIL result. The gap is missing coverage of the evaluation itself, not a known failure in the model. | The existing asset-identity rules do not reach this element, so whether it has an asset identity has not been evaluated, and it cannot be judged to be missing one; for the same reason, whether this work can start cannot be decided. First confirm whether the project's convention requires this element to have an asset identity, and whether the rules should reach it. Until that is confirmed, this does not mean it must have one. | **有。** 中文：先确认是否要求、规则该不该覆盖；英文原文：直接对全范围重跑评估，且断言“不是模型缺陷”。 |
| `in-model-position-not-evaluated` | 12／9 | 这不是已知的模型缺陷，也不需要改模型。空间归属的检查规则没有覆盖到这个构件，需要扩展规则的适用范围 | Not a model defect: run the in-model-position evaluation over the full assessed scope; where a specific element still produces no finding at all, extend the rule set's applicability to reach it -- a rule-authoring action, not a model edit -- so the position question can be asked of it. | This is not a known model defect, and the model does not need changing. The spatial-assignment check rules do not reach this element; the rules' scope of application needs to be extended | **有。** 英文原文先要求全范围重跑、仍无结果才扩展规则；中文直接说规则没覆盖到、需要扩展。英文原文还把“不是已知的”说成“不是”。 |
| `missing-project-asset-identity` | 11／9 | 在源模型里给这个构件补上本项目约定的资产标识属性（见所列属性集和属性名），重新导出 | Source-model fix: populate or correct the project-required asset-identity values on the affected source elements according to the project's active Overlay binding and convention, then re-export the model so the bound requirement_keys can be evaluated. Which properties, authoring-tool fields, and export mapping this requires is project- and convention-specific; the Pack does not name them, because that binding belongs to the Overlay. | In the source model, add to this element the asset-identity properties the project's convention requires (see the property sets and property names listed), then re-export the model | 轻微：英文原文多了“或改正”，并用 Overlay、requirement_keys；改源模型并重新导出这一义务相同。 |
| `penetration-not-determined` | 12／9 | 这不是已知的模型缺陷。还没有协调评审判定它是否穿过接收方的构件；需要开一次评审，记录“不穿过”或写明穿过哪些构件 | Not a model defect: hold the coordination-review determination this project's Overlay accepts, naming either no penetration or the specific architectural elements penetrated. The gap is that the determination has not been made yet, not a known defect. | This is not a known model defect. No coordination review has yet determined whether it passes through the receiving side's elements; hold a review and record either “no penetration” or which elements it passes through | 义务相同；开头的断言不同（“不是模型缺陷”对“不是已知的模型缺陷”），英文原文用 Overlay。 |
| `missing-corresponding-opening` | 6／10 | 在接收方模型里、被穿过的构件上建出洞口或竖井，不要做成交出方模型里的空洞。穿过几个构件就要几个洞口 | Source-model fix: model the opening in the architectural model, as a hosted opening or shaft in the architectural element this penetration passes through, rather than as a void carried in the MEP model. An element that passes through several architectural elements needs one such opening in each of them -- one per pair. | In the receiving side's model, model an opening or shaft in the element it passes through, not a void in the handing-over side's model. One opening for each element it passes through | 无。 |
| `cross-model-alignment-not-confirmed` | 5／0 | 这不是已知的错位。还没有人按项目接受的方法确认两侧模型对齐；需要针对所列模型版本做一次并记录 | Not a model defect: perform the alignment-confirmation method this project's Overlay accepts (e.g. overlaying both models' exported placements in a common viewer) against the named model versions. The gap is that no confirmation has been produced yet, not a known misalignment. | This is not a known misalignment. No one has yet confirmed, by the method the project accepts, that the two models are aligned; do this once against the model versions listed, and record it | 轻微：中文要求“并记录”，英文原文没有明说；开头断言不同；英文原文用 Overlay。 |
| `mep-element-not-spatially-assigned` | 0／0 | 在源模型里把构件放到正确的标高和空间上，重新导出 | Source-model fix: host the element to its correct level and space before export, avoiding unhosted or unlevelled MEP components, so the export reports an IFCRELCONTAINEDINSPATIALSTRUCTURE relationship for it. | In the source model, place the element on its correct level and in its correct space, then re-export | 无（英文原文带 IFC 关系名）。 |
| `cross-model-misalignment` | 0／0 | 重新获取项目共用的坐标基准，按共用原点重新导出（不靠移动几何），再按项目接受的方法重做对齐确认 | Source-model fix: re-acquire the project's shared coordination datum in the authoring tool, re-export placement referencing that shared origin rather than moving geometry directly, and re-perform the accepted alignment-confirmation method. Which authoring-tool command produces the re-acquired datum is project- and tool-specific; the Pack does not name it, the same way the asset-identity route does not name the properties its own fix touches. | Re-acquire the project's shared coordinate datum, re-export against the shared origin (not by moving geometry), then redo the alignment confirmation by the method the project accepts | 无。 |
| `opening-not-verifiably-linked` | 0／0 | 在接收方模型里，给洞口补上指回穿过它的那个构件的关联。一个洞口供几个构件穿过，每个各要一条 | Source-model fix: add or correct the cross-reference from the modelled architectural opening back to the penetrating MEP element it was cut for, so the link the accepted method checks for actually exists and can be inspected. One such link per (penetrating element, penetrated architectural element) pair: a shared opening serving several penetrating elements needs a cross-reference to each of them. | In the receiving side's model, add to the opening a cross-reference back to the element that passes through it. Where several elements pass through one opening, each needs its own | 无。 |
| `opening-status-not-determined` | 0／0 | 这不是已知的缺洞。开洞情况的评审没完成：洞口是否已建、是否已关联 | Not a model defect: complete the opening-status review this project's Overlay accepts -- whether a corresponding opening is modelled and, if so, whether it is inspectably cross-referenced. The gap is that this review has not been completed yet, not a known missing opening. | This is not a known missing opening. The review of the opening is not complete: whether it is modelled, and whether it is cross-referenced | 义务相同（中文只说评审没完成，英文原文明说去完成）；开头断言不同。 |

### 逐条对照：问题类型 × 复检（单项页、复检单项页，及“复检前留下的结束条件”）

| 问题类型 | 原中文（不变） | 原英文（Pack） | 新英文 | 义务差异 |
| --- | --- | --- | --- | --- |
| `missing-project-asset-identity` | 重新发布的模型上，这个构件在所列每条要求下都通过，范围内没有构件漏评 | Every requirement_key bound to asset-identity evaluates PASS for every element in the assessed scope, with no element left uncovered, on the reissued model. | On the reissued model, this element passes every requirement listed, and no element in the scope is left unevaluated | **有。** 英文原文要求范围内**每个**构件都通过；中文要求**这个**构件通过、范围内没有漏评。 |
| `asset-identity-not-evaluated` | 范围内每个构件在所绑定的要求下都有评估结果 | Every element in the assessed scope is covered by an evaluation under the bound requirement_key(s) -- no element is left with no finding at all. | Every element in the scope has an evaluation result under the requirements bound to it | 无。 |
| `in-model-position-not-evaluated` | 范围内每个构件在所绑定的要求下都有检查结果 | Every element in the assessed scope is covered by a finding under the bound requirement_key(s). | Every element in the scope has a check result under the requirements bound to it | 无。 |
| `penetration-not-determined` | 针对所列模型版本，有一份评审判定记录 | A recorded coordination-review determination exists for the named model versions, naming either no penetration or the architectural elements penetrated. | A recorded review determination exists for the model versions listed | 无（英文原文把判定的两种写法再说一遍，行动句已说）。 |
| `missing-corresponding-opening` | 这一对的开洞核查结果为“洞口已建且已关联”。只建洞不够 | The opening-status evaluation is re-run and reports the opening modelled and cross-referenced (outcome = cross-referenced) for this pair, for the named model versions. | The opening check for this pair reports “opening modelled and cross-referenced”. Modelling the opening alone is not enough | 无。 |
| `cross-model-alignment-not-confirmed` | 对齐确认已做，结果为已对齐，写明模型版本 | The alignment-confirmation method is performed and reports the models aligned, against the specific model versions named. | The alignment confirmation has been done and reports the models aligned, naming the model versions | 无。 |
| `mep-element-not-spatially-assigned` | 重新发布的模型上，这个构件的空间归属要求通过 | The R-004-bound requirement_key(s) evaluate PASS for the element on the reissued model. | On the reissued model, this element passes its spatial-assignment requirement | 无（英文原文用规则号和 requirement_key）。 |
| `cross-model-misalignment` | 针对新版本重做对齐确认，结果为已对齐 | The alignment-confirmation method is re-run against the reissued model versions and reports the models aligned (outcome = confirmed). | The alignment confirmation is redone against the new versions and reports the models aligned | 无。 |
| `opening-not-verifiably-linked` | 这一对的关联核查结果为已关联 | The opening-cross-reference-check method is re-run and reports the opening cross-referenced to the penetrating element, for the pair. | The cross-reference check for this pair reports the opening cross-referenced | 无。 |
| `opening-status-not-determined` | 核查给出明确结果（已关联／已建未关联／未建） | The opening-cross-reference-check method is performed and reports a definite result (cross-referenced, modelled-not-cross-referenced, or not-modelled) for the named model versions. | The check gives a definite result (cross-referenced / modelled but not cross-referenced / not modelled) | 无。 |

“复检前留下的结束条件”在样例里出现的类型：`missing-project-asset-identity`、`asset-identity-not-evaluated`、
`in-model-position-not-evaluated`、`penetration-not-determined`、`missing-corresponding-opening`。另有 27 处该字段为空，
两种语言都不显示这一行。

**小结**：有义务差异 3 处（`asset-identity-not-evaluated` 行动、`in-model-position-not-evaluated` 行动、
`missing-project-asset-identity` 复检）；轻微 2 处；只有开头断言不同 3 处；其余无差异。修正后英文一律跟随中文，差异全部消除。

## 二、反过来的情况：中文用原文、英文用裁定句

没有。逐表核对过：

- 行动和复检句：两种语言共用一个判断——只有记录属于上面那个 Pack 版本、且问题类型在表里时才有句子。
  不属于时（样例里没有这种记录），改前两种语言都把 Pack 原文放进“要做什么”，现在两种语言都说“本界面没有为这个版本写行动句”，
  原文在折叠里。
- `REASON_GLOSSES`（4 条）：中文在检查结果原因的原文旁加一句释义，英文只显示原文。原因是检查结果的陈述，不是指令。
  其中 “The required property set does not exist” 的中文释义多了半句说明：要补的是整个属性集，不是给已有属性填值。
  这是对同一事实的解释，不改变义务，所以未改，列在这里供 BIM 判断英文是否也需要。
- `CITATION_GLOSSES`（1 条）：中文是出处原文的直译，英文只显示原文。无差异。
- `IFC_CLASS_NAMES`：只是类别名。无差异。

## 三、工作区：PV-001 规则说明（两种语言都是本界面写的）

`RULE_NOTES.PV-001` 的英文不读原文，是逐条写的。逐条对照如下（W6 一行见第四节）：

| 键 | 内容 | 义务差异 |
| --- | --- | --- |
| `title` | 风口要声明四种预定义类型之一 | 无（英文取自规则文件 `title`） |
| `predicate` | 四个取值；IFC4 也允许 USERDEFINED、NOTDEFINED，不接受它们是规则自己的决定 | 无 |
| `passProves` | 按读取顺序取到的那一个值逐字等于四个值之一 | 无 |
| `passDoesNotProve`（6 条） | 取值正确、类型与实例一致、USERDEFINED 未出现、墙上有洞口、两模型已对齐、任何工作可以开始 | 无，6 条一一对应 |
| `action.what` | 回到 Revit 源模型，使导出的预定义类型为四个值之一，重新导出再检查；NOTDEFINED 等于什么都没说 | 无（英文末句取自规则 `instructions`） |
| `action.reads` | 检查器读 IFC 的顺序，不是 Revit 里该改的位置 | 无 |
| `action.revise` | 返回数据没有记录在 Revit 里从哪里写出；先确认；在类型上改会作用于全部实例 | 无（本次两种语言同时补 W6 半句） |
| `action.undecided` | 取哪个值、谁决定和操作，返回数据没有提供 | 无 |
| `recheck` | 同一规则集版本、同一组模型、同一导出设置重新检查 | 无 |
| `gaps`（3 条） | 墙上洞口要协调评审判定；对齐要确认记录；取值是否选对要另行记录 | 无 |
| `reasonFreeText` | 引号里是自由文本，不是枚举值 | 无 |
| `TAG_WORDS.note` | Tag 核对步骤 | 无（本次两种语言同时改 Tag 不一致时的行动） |

工作区的“规则的原话”（`expected`）、原因、出处在两种语言里都显示返回数据的原文，标明是原文；它们不是行动句。

## 四、10/8 批次点名的两处（中英同时改）

| 位置 | 中文现在 | 英文现在 |
| --- | --- | --- |
| W6：`RULE_NOTES.PV-001.action.revise` 句末 | 一个 Revit 类型可能对应不止一个 IFC 类型对象，实例数按 Revit 类型算。 | One Revit type may correspond to more than one IFC type object; count instances by the Revit type. |
| Tag：`TAG_WORDS.note` 不一致时的行动 | 不同就不要按这个 Tag 去改：用 GlobalId 确认是哪个对象，再回到 Revit 源模型修改。 | if they do not, do not change anything by this Tag: use the GlobalId to confirm which object it is, then make the change in the Revit source model. |

## 五、交 10/8 BIM 的新增与改动条目

| 表．键 | 语言 | 类别 |
| --- | --- | --- |
| `ACTIONS.<10 个问题类型>.action` | 英文（新增 10 条） | 行动，有领域含义 |
| `ACTIONS.<10 个问题类型>.recheck` | 英文（新增 10 条） | 复检条件，有领域含义 |
| `ACTION.noSentence` | 中英（新增） | 来源边界 |
| `ACTION.original` | 中英（改） | 来源边界：折叠里是来源原文，不是操作指令 |
| `RECHECK_ITEM.originalSummary` | 中英（改） | 同上 |
| `ACTION.whatOriginal`、`ACTION.recheckOriginal` | 中英（删） | 原文不再出现在“要做什么”“完成后拿什么复检”两行 |
| `RULE_NOTES.PV-001.action.revise` | 中英（改，W6） | 源修改 |
| `TAG_WORDS.note` | 中英（改，Tag） | 源修改与定位 |

英文词表：690 条 → 709 条（有领域含义 517 → 537，界面用语 161 → 160）。
