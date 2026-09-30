# 0005 — 规则语义身份与证据沿用（设计裁定包）

- **状态：Proposed，PM 已裁定。** 技术总监对 `14697eb` 的审计为 APPROVED（从干净检出重跑
  全部测量，运行记录逐行一致）。PM 于 2026-10-01 采纳 O1、接受契约 1.7，并要求复检对
  "证据沿用"的判断同时修正；**第 8 节逐条记录 P-1–P-6，每条都标明是 PM 的决定。** 第 5 节是
  裁定之后的修复设计。本文仍然**不增改任何生产代码、身份派生、规则、契约、快照、Pack、
  Overlay、测试或生成产物**；`data/processed/`、`reports/`、`ids/` 与 legacy 字节均未移动。
  修复检查点（第 5.9 节）尚未开始。
- **日期：** 2026-09-30，修订 2026-10-01。**基线：** 初版 `main` = `4e05c03`；本次修订的
  测量在 `main` = `c9cf3b2`（PR #17 合并后）上做。
- **修订记录：**
  - `14697eb`（2026-09-30）：初版设计裁定包，停在 PM 裁定。
  - 2026-10-01：写入 PM 对 P-1–P-6 的裁定（第 8 节）。第 5 节由"推荐方案"改为裁定后的修复
    设计：四种沿用状态与封存依据（5.2）、二元 `carried` 的去留与下游（5.3）、模型重新发布
    （5.4，待 BIM 审）、P-2(b) 守卫的设计与原型计划（5.5）、P-3 的代码证据（5.6）、P-4–P-6
    （5.7）、验收清单与契约 1.7 的移动（5.8）。第二轮实测见证据目录的 *Round 2*。更正
    第 2.2 节的一个计数（判定沿用行是 6 行，不是 8 条）。第 1–4 节其余部分是第一轮的记录，
    原样保留。
- **输入（在仓库之外，分开对待）：** 初版：PM 的原始要求与技术总监实测的五条事实。本次修订：
  PM 对 ADR 0005 的裁定原文（本轮的原始需求）与技术总监的修订指示。两轮都**没有** BIM 域
  输入；本文不作域主张，第 5.4 节把一个域问题明确留给 BIM。
- **证据：** [`docs/evidence/rule-semantic-identity-2026-09-30/`](../evidence/rule-semantic-identity-2026-09-30/README.md)。
  第一轮一条命令从 `4e05c03` 复现；第二轮一条命令从 `c9cf3b2` 复现（该文件末尾的 *Round 2*）。
  本文每个数字都能在两份运行记录里找到对应段落（第 11 节）。
- **与既有决定的关系：** 修复检查点会改 ADR 0001 派生之下的规范化摘要内容（第 5.1 节），不改
  `finding_key` 的派生公式；**不改 ADR 0003 的"按成员对应"**（第 7 节实测它不动）；改 ADR 0003
  §4.7.2 / §4.7.6 关于沿用的说法（第 5.3 节，随代码一起改）；满足 ADR 0004 检查点 4 前提的方式
  见第 6 节；不碰 ADR 0004 检查点 2–4。

---

## 0. 一页结论

**缺陷，一句话：** 规则集的规范化摘要不含任何 facet 参数，所以只改规则"检查什么"时，
`validation_run_id` 与全部 `finding_key` 原样保留；复检只要 `finding_key` 还在就记 `carried`，
于是**同一个键下的事实变了，记录却说"证据沿用"**（第 1–2 节，第一轮实测）。

**PM 的裁定（第 8 节）：** 采纳 O1，接受契约 1.6 → 1.7；**但不能只换键**——复检必须区分四种
情况，不能只比 outcome；规则集保留 2.2，摘要派生版本化，守卫不得"派生不同即放行"；展示
文字不进新的语义摘要，但被检查器消费的字段不能因为名字叫 `instructions` 就排除；发布
`semantics_digest`；Pack / Overlay schema 不改，但不再声称只钉版本就能约束工作区副本；legacy
当前规则投影单独登记为阻塞项。

**修复设计（第 5 节），一段话：** 每条要求带一个 `semantics_digest`（它实际检查的谓词），
规范化摘要覆盖它。评估记录封存时，在每个被引用的 finding 旁边写下一份**比较依据**：
对应坐标 `(element_key, requirement_key)`、模型版本、要求的语义摘要、finding 内容摘要、
检查器指纹。复检先按成员对应（ADR 0003，不变），再按坐标找唯一对应，逐项比较，每一行
恰好落在四种状态之一：

| 状态 | 意思 | 第二轮原型实测的例子 |
|---|---|---|
| `equivalent` | 引用可以换了键，但语义与证据内容比较下来相同 | 改无关的 R-002：9/9 行，全部换了键 |
| `changed` | 语义、内容、模型版本或检查器至少一项不同——**即使 outcome 相同** | 改 R-005A 数据类型：2 行，只有 `requirement-semantics` 不同 |
| `no-counterpart` | 可以比较，但本记录没有引用任何对应证据 | 重新发布后未被重新提交的判定：6 行 |
| `not-provable` | 比较本身无法建立：旧记录没有依据、成员不在、对应不唯一 | 1.7 之前的记录：9/9 行；删掉风管：3 行；造一个重复结果：1 行 |

记录里不再有布尔 `carried`；"无法证明"与"没有对应"在记录层就是两个值，不靠 UI 区分。
Doctor 复检页的呈现是一个 UI 后续任务，本轮与修复检查点都不改 `doctor/`（第 5.3 节）。

**还开着的（第 9 节）：** 模型重新发布之后"读数相同"算不算等价——本设计记为
`changed`（`model-version`），**待 BIM 审**；P-2(b) 守卫本轮只有设计与原型计划，它不能安全成立
就回 PM，不自动改选 2.3；IfcTester / ifcopenshell 升级的影响仍未验证。

## 1. 缺陷是什么，以及哪些现有说法因此不成立

### 1.1 机制

- `identity.build_ruleset_normalized_digest` 摘要每条要求的 `rule_id`、`requirement_id`、
  `requirement_key`、两个标签、`checker`、`facet_kinds`、`severity`、`owner_role`、`stage`、
  `discipline_scope`、`citation`、`priority`、`labels`。**任何 facet 参数都不在其中**：
  适用实体、属性集、`dataType`、`cardinality`、取值约束、`ifc_version`、完整性检查器的
  `name_pattern`，一概没有。只有恰好进入 `requirement_label` 的参数（如 `baseName`）会移动它。
- `validation_run_id` 摘要这个规范化摘要；`finding_key` 摘要 `validation_run_id`。所以
  只改 facet 的编辑不移动任何一层身份。
- `ruleset_source_blob_sha256` 对规则**目录**是空字符串（实测 `''`，`### D`），只有 `.ids`
  文档来源才有值，不能拿来补。PR #17 的 `rule_definitions_digest` 是覆盖记录内部的执行前后
  夹板，不是身份。
- `recheck._carry_over` 对 finding 引用只问"这个键在不在当前事实里"。

### 1.2 实测：8 种编辑，摘要一次都没动（`### D`）

| 编辑 | 规范化摘要 |
|---|---|
| R-002 `dataType` `IFCBOOLEAN`→`IFCLABEL` | 不变 `c3be0db4…` |
| R-001 `cardinality` `required`→`optional` | 不变 |
| R-006 适用实体 `IFCWALL`→`IFCSLAB` | 不变 |
| R-010 `name_pattern` 去掉 `geo-reference` | 不变 |
| R-005A 两条要求 `required`→`optional` | 不变 |
| R-005A 两条要求 `dataType` `IFCLABEL`→`IFCTEXT` | 不变 |
| R-005A 说明文字（`instructions`）改一句 | 不变 |
| R-005A 适用表换键序、加注释、加空白（对照） | 不变 |
| `ruleset.toml` 版本 2.2→2.3（对照） | **移动** |

### 1.3 因此不成立的现有说法

这些都是本文的发现，**本文不改其中任何一处**；它们在修复检查点里随代码一起改（第 5.7、5.8 节）：

| 位置 | 说法 | 实测 |
|---|---|---|
| `epc_control_tower/identity.py:119-120` | "Only a change to the rules themselves moves it." | 6 种改变规则检查内容的编辑都不移动它 |
| `epc_control_tower/checkers/ids_checker.py:460-462` | 规则"说什么"已经经由规范化摘要进入验证身份 | 同上 |
| `epc_control_tower/purpose/assessment/recheck.py:601-604`、`record.py:121` | `finding_key` "already is" 内容摘要 | 第 2 节：同键两种事实 |
| ADR 0003 修订记录（D-13）第 451 行、§4.7.6 末段 | finding 分支"already honest"，因为 `finding_key` 由 finding 自身内容派生 | 同上 |
| ADR 0002 §3.3（第 1210–1224 行） | 规范化摘要哈希"every field that gives the requirement its actual meaning"；钉住版本号就能挡住"applicability changed underneath it" | 摘要不含适用性；版本号只在有人升的时候才挡得住（第 4 节） |
| `epc_control_tower/purpose/composition.py:229-231` | `(ruleset_id, ruleset_version)` 证明这一行"still means what the author assumed" | 同上 |
| `CHANGELOG.md` 契约 1.4 条目第 338–339 行 | "Identity was never at risk. The digest was doing its job the whole time." | 对"加规则"成立（当时测的就是这个）；对 facet 编辑不成立。历史记录不改写，只在 1.7 条目里说明 |

## 2. 复现：真实的复检路径，逐键逐状态

### 2.1 怎么跑的

`probe.py recheck <编辑>` 在一次性检出里：`build_bundle` 跑一次完整验证 →
`facts_from_bundle` → 用 `tests/assessment_fixtures.py` 的 Overlay（与每个复检测试相同：
三张政策表决定了两张，判定由测试提供）组合真实 Pack → `assess_purpose` 封存第一份记录 →
在磁盘上改一个规则文件 → 用全新的配置与注册表重新验证 → `recheck_purpose`，**继承第一份
记录的全部 8 个子范围**。没有替身，没有跳过的检查。夹具的判定与政策不是任何人的决定。

### 2.2 R-005A 放宽：`required` → `optional`（`### RP` 第一段）

身份：`validation_run_id` `epc-delivery-v2.2-71d28a7c8bddb4e7` → **同一个**；规范化摘要
`c3be0db4…` → **同一个**；两个模型的内容标识不变，`context.is_current = True`。
第一份记录 `aef0bd06…`（与 `test_purpose_authorisation` 钉住的 `BASE_ASSESSMENT_DIGEST`
一致），后继记录 `42aa00aa…`。

全部 9 行 finding 沿用：

| 子范围 | `finding_key` | 构件 | 要求 | 之前 → 之后 | 后继记录写的 |
|---|---|---|---|---|---|
| schedules #2 | `31f9255b-fa9d-522b-8af2-e45bd33bb216` | `hvac::23uPJWDfXEcwHH3kdFgV9c` | R-005B AssetTag | FAIL → FAIL | `carried` |
| schedules #2 | `366d684e-8e45-53c7-8993-5299a27c6d39` | `hvac::34Y6EIt3nDCAS1k$kPGOKm` | R-005B SystemCode | FAIL → FAIL | `carried` |
| schedules #2 | **`5454a69b-d62a-57a2-a9e7-a96a4c4a364a`** | `hvac::38WbwIGD90nB_3T2BTU5Ed` | R-005A SystemCode | **FAIL → PASS** | **`carried`** |
| schedules #2 | `90ea1aba-c7f0-5142-a123-f12e3c7c54f5` | `hvac::34Y6EIt3nDCAS1k$kPGOKm` | R-005B AssetTag | FAIL → FAIL | `carried` |
| schedules #2 | `9b6e100b-f05d-51cd-93cd-36f6b2597c70` | `hvac::23uPJWDfXEcwHH3kdFgV9c` | R-005B SystemCode | FAIL → FAIL | `carried` |
| schedules #2 | **`d0bdd588-2a41-5ddd-ab44-d7e59f99ed35`** | `hvac::38WbwIGD90nB_3T2BTU5Ed` | R-005A AssetTag | **FAIL → PASS** | **`carried`** |
| ceiling #2 | `12dc1e52-b4a8-5fd8-b650-222c2cf3060b` | `hvac::23uPJWDfXEcwHH3kdFgV9c` | R-004B | PASS → PASS | `carried` |
| ceiling #2 | `4cd5d234-8820-5068-b957-c7c04f4f296b` | `hvac::38WbwIGD90nB_3T2BTU5Ed` | R-004A | PASS → PASS | `carried` |
| ceiling #2 | `9b1eafbf-e3df-5c5d-9096-83ffbd2e4805` | `hvac::34Y6EIt3nDCAS1k$kPGOKm` | R-004B | PASS → PASS | `carried` |

成员与判定（全部 8 个子范围的对应都是 `complete`，没有成员消失）：

| 子范围（之前） | 成员 → 现在 |
|---|---|
| schedules #2 `BLOCKED` `missing-project-asset-identity` | 两个风口 → `BLOCKED`；**风管 → `READY`** |
| schedules #1 `UNKNOWN` `asset-identity-not-evaluated` | 烟囱 → `UNKNOWN` |
| ceiling #1 `UNKNOWN` / ceiling #2 `READY` | 不变 |
| openings #1–#4 | 不变；连同 ceiling #2 的 1 行，判定引用共 6 行，全部 `carried`，判定内容确实没变（初版此处写"8 条"，是计数错误，本次修订更正；见运行记录 `### RP`） |

读这份后继记录的人看到的是：**模型没动、上下文没动、支撑证据"沿用"，风管的资产标识阻塞却
解除了**。三句话放在一起自相矛盾，而记录里没有任何字段能说明真正发生的事——是规则被放宽了，
没有人补过资产标识。R-005A 的 `recheck_condition` 本来就不可机读
（`no-machine-checkable-part`），所以这条阻塞"解除"的唯一依据就是这两行 `carried`。

同一编辑在 finding 层（`### RB`）：121/121 键保留，2 条状态翻转（上表两行），另有 10 条
`N/A` 行只有 `expected` 文本从 "shall be provided" 变成 "may be provided"
（5 个模型 × 2 条要求）。

### 2.3 R-005A 改数据类型：`IFCLABEL` → `IFCTEXT`（`### RP` 第二段）

身份同样一个字都不变。更关键的是 finding 本身：**121 条里 0 条状态变化、0 条文本变化**
（`### RB`）——已发布的 `expected` 文本来自 IfcTester 的 `to_string`，它不写数据类型。
风管的两行（`d0bdd588-…`、`5454a69b-…`）仍是 `FAIL → FAIL`、字节全同、记 `carried`，
而产生它们的谓词已经从"是 IfcLabel"变成"是 IfcText"。探针对照规则文件本身的解析结果把这
两行标了出来（"finding bytes identical, the rule that produced it changed"：2 行）。

这一例决定了第 3 节 O3 的边界：**任何只看 finding 内容的摘要都看不见它。**

### 2.4 同一缺陷在已发布运行上的样子（`### SQ`）

把 R-002 `dataType` 改掉后照常 `run`：

- 25 个生成文件改变，`epc-ct snapshot` exit 1；`validation_run_id`、`artifact_bundle_id`、
  legacy `run_id` **三者都不变**；121/121 键保留，其中 9 条内容变了（技术总监测到的 9 条
  PASS→FAIL，逐键见 `### RB`）；21/21 `issue_key` 保留；通用 BCF 21 个 topic 中 9 份 markup
  改字节。
- **其中 8 个是 legacy 冻结产物**（`ids_findings.csv`、五份 `bcf_*.csv`、`ids_failures.bcf`、
  `run_manifest.json`）：`pcert-sample` 的 8 行 R-002 legacy finding 在
  `ids-v0.1-8706ef58303bfd11` 之下保留原 legacy 键、状态 PASS→FAIL，冻结 BCF 从 3 个 topic
  变成 11 个。原因是 legacy 投影按 `requirement_key` 取**当前**规则的结果，而冻结身份摘要的是
  v0.1 文档的字节。今天挡住它的只有快照与 CI 的逐字节比较。这是同一类碰撞在 legacy 层的
  样子；本文**不**提议修它（冻结派生不动，第 3 节边界 3），只记录（第 9 节 U5）。

改一句说明文字（R-005A `instructions`）：13 个文件改变——`reports/ids/` 下 12 个检查报告和
`ids/epc-delivery_v2.2.ids`——没有一条 finding、没有一个已发布契约文件、没有一个身份变化，
`snapshot` exit 0。这是第 8 节 P-3 的依据。

## 3. 方案与实测对照

> 本节是裁定之前的第一轮比较，原样保留。PM 的裁定见第 8 节，裁定之后的设计见第 5 节。

### 3.1 三个方案

- **O1 — facet 进入规范化摘要。** 每条 `Requirement` 带一个 `semantics_digest`：它所属规则的
  `rule_id`、`checker`、`ifc_version`、全部适用 facet（排序后）、以及它自己这条要求 facet 的
  全部参数（**不含** `instructions`），外加派生号 `derivation: 2`。规范化摘要只在该字段非空时
  把它纳入。从 `.ids` 文档加载的要求（即冻结的 legacy v0.1）该字段为空，其摘要逐字节不变。

  第一版原型把语义挂在规则集层，**被 `validate_bundle` 拒绝**：它从 bundle 自带的
  `Requirement` 对象重算规范化摘要，以保证 bundle 不能声称它不含的规则
  （`### O1` 之前一次失败的运行，记录在证据说明里）。这等于把"摘要只是 `Requirement` 的
  函数"钉成了不变量——所以语义必须落在要求上，这是实测得出的设计约束，不是偏好。
- **O1i — 同上，`instructions` 也算语义。** 只测摘要。
- **O2 — 只靠版本纪律。** 语义编辑必须同时把 `ruleset.toml` 的版本升一格。原型就是
  2.2→2.3 本身。
- **O3 — 引用旁附内容摘要（仿 PR #7 对判定的做法）。** `FindingFact` 带一个对
  `(model_key, element_key, requirement_key, status, expected, actual, reason)` 的摘要，
  评估记录在每个 `finding_key` 旁封存它，复检比较：同键同摘要 → `carried`；同键异摘要 →
  `finding-content-changed-under-the-same-key`。不动任何已发布身份。

### 3.2 对照表（全部实测）

| 量 | 现状 | **O1** | O2（升 2.3） | O1 + 2.3 | O3 |
|---|---|---|---|---|---|
| 6 种 facet 编辑移动摘要 | 0/6 | **6/6** | 0/6 | 6/6 | 0/6 |
| 说明文字 / 重排版移动摘要 | 0 / 0 | **0 / 0**（O1i：1 / 0） | — | — | — |
| `run` exit | 0 | 0 | 0 | 0 | 0 |
| 改变的已发布文件 | — | **8**：canonical 6（含 `requirements.csv` 新增一列）+ `artifact_manifest.json` + `issues.bcf` | 7 改 + `ids/epc-delivery_v2.3.ids` 新增（v2.2 那份留在原地） | 8 改 + 1 增 | **0** |
| legacy 冻结产物改变 | — | **0** | 0 | 0 | 0 |
| legacy `run_id` / 冻结规则集摘要 | `ids-v0.1-8706ef58303bfd11` / `ecd14778…` | **两者不变** | 不变 | 不变 | 不变 |
| `validation_run_id` | `…-v2.2-71d28a7c8bddb4e7` | `…-v2.2-d4cc6703d427f69d` | `…-v2.3-94ae5d15d466e549` | `…-v2.3-4b307de9eab475e8` | 不变 |
| `finding_key` / `issue_key` 保留 | — | **0/121 / 0/21** | 0/121 / 0/21 | 0/121 / 0/21 | 121/121 / 21/21 |
| finding 内容相同 | — | 121/121 | 121/121 | 121/121 | 121/121 |
| BCF topic 保留 / markup 改字节 | — | 21/21 / 21 | 21/21 / 21 | 21/21 / 21 | 21/21 / 0 |
| `artifact_bundle_id` | `bundle-a1fd9360e12c71fa` | `bundle-8b27f2ea58ac413e` | `bundle-ec0de02a7096f2ee` | `bundle-d54b1c49896eb1d1` | 不变 |
| `epc-ct snapshot` | exit 0 | exit 1（须走仪式） | exit 1 | — | exit 0 |
| 版本守卫对已记录快照 | 0 冲突 | **1 冲突**（1.6 已记录 v2.2 为另一摘要） | 0 | 0 | 0 |
| fixture Overlay 组合 | 成功 | **成功**，`composition_digest` 不变 `2b3d9af1…` | **拒绝** `binding-ruleset-mismatch` | 拒绝 | 成功 |
| `validate_dashboard --mode core` / `validate_pbip` | — | 0 / 0 | — | — | — |
| 全套测试 | 881 过 | 10 失败：快照 2 + 子测试 7；`BASE_ASSESSMENT_DIGEST` 1 | 25 失败 + **218 错误**（第 3.4 节） | — | 1 失败：`BASE_ASSESSMENT_DIGEST` |
| 复现 2.2（放宽）后继记录 | 2 行错误 `carried` | **0**；9 行全部 `finding-absent-from-the-cited-run` | 组合被拒，**没有后继记录** | — | **0**；那 2 行记 `finding-content-changed-under-the-same-key` |
| 复现 2.3（改类型）后继记录 | 2 行 `carried`，规则已变 | **0** | 组合被拒 | — | **2 行 `carried`，规则已变** |
| 第一份记录的摘要 | `aef0bd06…` | `4c5eae80…` | — | — | `d5af435e…` |
| "按成员对应"（第 7 节） | — | 不变 | — | — | 不变 |

### 3.3 逐项说明契约代价

**O1。**

- *canonical / BCF / manifest / 快照：* 一次性 0/121、0/21、21 份 markup、`run.json`、
  `artifact_manifest.json`、`requirements.csv`；`snapshot` 失败。这是一次**契约移动**，
  必须走 `CHANGELOG` + `epc-ct snapshot --refresh --contract-changed`，即 1.6 → 1.7。
  `requirements.csv` 多出的 `semantics_digest` 列来自 `REQUIREMENT_COLUMNS = field_names(Requirement)`；
  它是否作为公开列发布是 P-4。
- *legacy：* 8 个冻结文件 0 字节变化；legacy `run_id` 不变；冻结规则集的规范化摘要
  `ecd14778…` 在现状与 O1 下逐字节相同（`### D`、`### O1` 各一行）。**冻结身份派生不受影响**，
  这是设计出来的，不是碰巧：`.ids` 来源的要求不带该字段。
- *Pack 与 Overlay 的 `ruleset_version` 钉住：* 不受影响（仍是 2.2），组合成功，组合摘要不变
  ——**前提是版本号不升**，见 P-2。
- *Purpose 夹具记录：* 第一份记录摘要 `aef0bd06…` → `4c5eae80…`，因为它引用
  `validation_run_id` 与 `finding_key`。仓库里钉住它的只有 `test_purpose_authorisation`
  的 `BASE_ASSESSMENT_DIGEST`（1 个测试）；它的文档说明这是"`669307e` 时的值"，须重钉并
  写明为什么动。
- *Doctor：* 夹具信封是按需现算的，不入库；`test_doctor_adapter.py`、`test_doctor_preview.py`
  在 O1 下**全部通过**。
- *两份数据契约文档与 dashboard：* `docs/data_contract.md` 要写明 `requirements.csv` 的新列
  （若 P-4 决定发布它）和规范化摘要覆盖什么；`docs/bcf_data_contract.md` 描述的是 legacy
  BCF，**不变**。两个 dashboard 校验器 exit 0。
- *代价的性质：* O1 之后任何一条规则的语义编辑都会换掉**全部**键——包括与编辑无关的 R-004、
  R-005B（复现 2.2 在 O1 下 9 行全部 `finding-absent`）。这与模型重新发布时的行为一致，是
  "`finding_key` 是运行级摘要"的直接后果。更细的（按要求派生 `finding_key`）会改 `finding_key`
  的派生本身，本文不提议，列为 U3。

**O2。** 升版本本身的发布代价与 O1 同级（0/121、0/21、21 份 markup），外加：

- `ids/epc-delivery_v2.3.ids` 新增，v2.2 那份留在原地（`run` 不删旧文件，ADR 0004 已记录的
  残留）；
- **Pack 与 Overlay 双双钉在 2.2**：Pack 的 `pack_binding`、`insufficient_evidence` 与
  Overlay 的 `evidence_bindings`、`conventions` 都写着 `ruleset_version = "2.2"`，组合以
  `binding-ruleset-mismatch` 拒绝。要让 Purpose 重新可用，Pack 内容要改（Pack 的
  `pack_version` 随之要不要升、Overlay 按精确相等钉住 `pack_version` 要不要跟着改，是连锁的
  产品问题），Overlay 要改，夹具要改；
- 全套测试 25 失败 + 218 错误，Purpose 与 Doctor 测试全线在 `setUpClass` 里因组合被拒而
  出错（第 3.4 节）；
- 复现路径上：**组合被拒，根本产不出后继记录**。这是 fail-closed，但它同时挡住了所有其他
  复检；
- 最要紧的：**O2 抓不住忘了升版本的那一次**——那就是第 2 节的现状。今天的守卫（第 4 节）
  也抓不住，因为它看的正是那个看不见 facet 的摘要。

**O3。** 发布层 0 变化，这是它唯一的优势，但：

- 抓不住 2.3 的改类型（finding 字节全同）；要看见它，摘要必须包含规则语义，而 Purpose 层今天
  读不到规则定义——要么先有 O1（引用它的 `semantics_digest`），要么给 Purpose 开一条读规则
  文件的新输入路径（违背 ADR 0003 §1.2 的输入边界，本文不考虑）；
- 已发布层的碰撞原封不动：`findings.csv`、BCF `ReferenceLink` 里同一个 finding URN 继续指向
  含义已变的结果；
- 不满足 ADR 0004 检查点 4 的前提（第 6 节）；
- Purpose 记录形状变（每个引用多一个摘要），第一份记录摘要 `aef0bd06…` → `d5af435e…`。

### 3.4 O2 的测试代价，逐文件（`### O2`）

| 文件 | 失败 | 错误 |
|---|---:|---:|
| `test_purpose_assessment.py` | | 81 |
| `test_purpose_recheck.py` | | 66 |
| `test_purpose_authorisation.py` | | 29 |
| `test_doctor_adapter.py` | | 23 |
| `test_purpose_composition.py` | 9 | 12 |
| `test_doctor_preview.py` | 2 | 4 |
| `test_purpose_isolation.py` | 4 | 3 |
| `test_contract_snapshot.py` | 3 + 子测试 6 | |
| `test_ids_syntax_audit.py` | 1 | |

## 4. "规则语义变了但版本号没变"：靠身份、靠纪律，还是两者

**两者都要，而且分工不同。**

1. **身份负责自动抓住。** 语义变了，由它派生的一切必须变，不能指望有人记得。O1 之后实测
   6/6 种 facet 编辑移动摘要、2/2 种非语义编辑不移动；复现 2.2 与 2.3 在 O1 下都不再有一行
   错误的 `carried`。这一层不依赖任何人的纪律，对 ADR 0004 §5.0 的隔离工作区同样生效——
   工作区带着 `rules/` 的副本，副本会漂移，而工作区没有快照守卫。
2. **版本纪律负责给人一个名字。** 身份是摘要，没人会在交付计划里写摘要；`(ruleset_id,
   version)` 是人引用规则集的方式，也是 Pack 与 Overlay 钉住规则集的方式。仓库**已经有**把
   这条纪律机器化的守卫：`snapshots.ruleset_version_conflicts`，在 `--refresh` 时拒绝"一个版本
   号对应两套规则"（契约 1.4）。**但它比较的正是那个看不见 facet 的摘要**，所以对第 1.2 节的
   任何一种编辑都一次也不会触发。O1 让它看得见：在记录 O1 摘要之后（`### O1` 用一份只存在于
   一次性检出里的合成记录代替真正的刷新），R-002 `dataType` 与 R-005A `dataType` 各多出
   **1 条**冲突，说明文字与重排版**0 条**。
3. **钉住只钉版本号的地方，靠的是第 2 条。** Pack 与 Overlay 的绑定只钉 `(ruleset_id,
   ruleset_version)`。对已发布规则集，O1 + 守卫保证"语义变了就必须换版本号"，于是这些钉住
   会 fail-closed（O2 实测）。对不经过快照刷新的规则副本，守卫不在场，版本钉住就挡不住；
   在那里挡住它的是检查点 4 的摘要钉住（第 6 节）。Pack / Overlay 是否也该钉摘要，是 P-5。

## 5. PM 裁定之后的修复设计

本节是第 8 节裁定的落地设计，**只是设计**：修复检查点尚未开始。具体形状、字段、状态名和
算法由工程决定（PM 裁定），每一项都写了理由。凡需要实测才能回答的，已用一次性原型在
`c9cf3b2` 上测过（证据 *Round 2*）；原型 `C` 实现了本节 5.2 的比较，只缺两样：检查器指纹
这个方面，以及第 2 步对 `basis_version` 的检查（原型写入版本号但不检查它）。

| 技术总监本轮七项 | 节 |
|---|---|
| 1　四种沿用状态、封存依据、对应规则、旧记录 | 5.2 |
| 2　二元 `carried` 与它的下游 | 5.3 |
| 3　模型重新发布之后的沿用（待 BIM 审） | 5.4 |
| 4　P-2(b) 守卫：具名基线、内容未变的证据、未知派生、历史快照、原型计划 | 5.5 |
| 5　P-3：检查器实际消费哪些字段 | 5.6 |
| 6　P-4、P-5、P-6 | 5.7 |
| 7　验收清单与契约 1.7 的移动 | 5.8 |

### 5.1 O1，按裁定

- 每条 `Requirement` 带 `semantics_digest`：对 `{derivation: 2, rule_id, checker,
  ifc_version, 所属规则的全部适用 facet（排序）, 这条要求自己的 facet 的全部参数}` 取
  sha256，**减去该检查器在代码里声明的非执行字段**（第 5.6 节：IDS 检查器是
  `{instructions}`，完整性检查器是空集；新检查器默认空集，即全部计入）。
- 规范化摘要只在该字段非空时纳入它。从 `.ids` 文档加载的要求（今天只有冻结的 legacy v0.1）
  该字段为空，冻结规则集的摘要 `ecd14778…` 逐字节不变（两轮都实测）。
- 规范化摘要里既有的元数据字段一个不动（P-3 裁定不做"全部去文字"的迁移），所以标题、
  `citation`、`owner_role` 等的编辑**仍会换键**（第 5.6 节实测）。
- `finding_key` 的派生公式不变，按成员对应不变（P-1 裁定）。
- 实测（*Round 2* `### P3c`，O1 + O1b）：R-005A 放宽或改类型只移动 R-005A 两条要求的语义摘要；
  R-002 改类型只移动 R-002 那一条；IDS 的说明文字、描述、重排版一条都不移动；R-010 的说明文字
  和适用实体各移动 R-010 那一条。

### 5.2 证据沿用：四种状态（第 1 项）

#### 5.2.1 一行怎么编码

复检记录里每一行 `evidence_carry_over`（finding 与判定都是）必带 `state`，取且只取下表
之一；`reason` 是 `state` 之下的封闭词表。finding 行另带：

- `current_citation`：有唯一对应时，本记录引用的那个 `finding_key`；
- `key_changed`：`yes` / `no`，只在 `equivalent` 与 `changed` 上出现；
- `changed_aspects`：只在 `changed` 上出现，非空、排序，取自封闭词表
  `{checker, finding-content, model-version, requirement-semantics}`；
- `cause`：`not-provable` 时写出原因的事实（成员处置名，或全部候选键）。

判定行保留 PR #7 的 `sealed_content_digest` / `current_content_digest`。

| `state` | 定义 | 判据 | `reason` |
|---|---|---|---|
| `equivalent` | 本记录引用了与封存引用唯一对应的证据，比较依据逐项相等；引用身份可以变 | finding：依据存在且版本已知、主体在场、候选恰好一个、双方语义摘要非空、四个方面全部相等。判定：同 reference、同内容摘要 | `finding-equivalent`；`determination-same-reference-same-content`（即原 reason `carried`，改名，见 5.3） |
| `changed` | 对应唯一且可比较，但至少一个方面不同——**即使 outcome 相同** | 同上，但 `changed_aspects` 非空。判定：同 reference、内容摘要不同 | `finding-changed`；`determination-content-changed-under-the-same-reference` |
| `no-counterpart` | 可以比较（有封存依据、主体在场），但本记录没有引用任何对应证据 | 候选为零 | `no-counterpart-in-the-cited-run`（被引用的运行里没有该坐标的 finding）；`counterpart-not-cited-under-the-current-binding`（运行里有，当前读数不引用）；`determination-not-cited-by-this-record`；`determination-not-attributable-to-this-context` |
| `not-provable` | 比较本身无法建立 | 下面判定顺序中第 1、2、3、4（多于一个候选）、5 步任一不满足 | `sealed-citation-has-no-comparison-basis`；`comparison-basis-version-unknown`；`subject-not-present`；`counterpart-not-unique`；`requirement-semantics-basis-unavailable` |

**判定顺序是全序，每一步以前一步为前提：**

1. 封存引用带比较依据吗？没有 → `not-provable`（旧记录，5.2.4）。
2. 依据的 `basis_version` 在已知集合里吗？不在 → `not-provable`。
3. 封存读数的主体仍是在场成员吗（5.2.3）？不是 → `not-provable`，`cause` 写成员处置。
4. 候选有几个？零 → `no-counterpart`；多于一个 → `not-provable`。
5. 封存与当前两边的语义摘要都非空吗？有空的 → `not-provable`。
6. 逐方面比较 → `equivalent` 或 `changed`。

理由：**先确定能不能比，再下结论**，与 ADR 0003 §4.7.4"先确认对应、再看条件"同构。
"无法比较"只可能在第 1、2、3、4（多个）、5 步终止，所以它在结构上到不了
`no-counterpart`——"无法比较"不会被编码成"证据消失"（PM 裁定）。主体不在场之所以是
`not-provable` 而不是 `no-counterpart`：PM 的第四类反例明示成员消失即"无法证明"；而且成员
处置已经在同一记录里说明主体去了哪里，再把它的证据记成"没有对应"，会把主体的离开记成
证据的消失。

#### 5.2.2 封存时必须保存的历史依据

每个被引用的 finding，封存时从**被引用的那次运行**写进记录：读数上新增 `cited_findings`，
与既有的 `finding_keys` 一一对应、同序（`finding_keys` 保留，因为 Doctor 读它，5.3）。

| 字段 | 来自 | 为什么 |
|---|---|---|
| `finding_key` | 运行 | 句柄 |
| `element_key`、`requirement_key` | finding | 对应坐标（5.2.3） |
| `model_key`、`model_content_id` | finding 与运行的模型版本 | 模型版本方面（5.4） |
| `semantics_digest` | 运行里这条要求的 `Requirement`（5.1） | 谓词方面。第 2.3 节的改类型只有它看得见 |
| `content_digest` | 对 `{basis: 1, status, expected, actual, reason}` 取 sha256 | 内容方面：谓词与模型都没变而输出变了的情况仍看得见，例如检查器库升级（U2） |
| `checker` | 这条要求路由到的检查器指纹 `(id, version, config_sha256)` | 检查器方面：`IdsChecker.version` 升级表示行为变了，谓词摘要看不见它。**原型未含此项** |
| `basis_version` | 常量 `1` | 依据自己的形状以后可以演进；不认识的版本 → `not-provable` |

这些都是记录内容，进入 `assessment_digest`，所以封存后不可改写。它们只在记录里：不进
任何冻结身份、不进已发布契约，ADR 0003 §5 的约束原样适用。事实投影（`AssessmentFacts`）
为此多带 `model_key`、`semantics_digest`、`content_digest` 与检查器指纹——都不是 ADR 0003
§3.4 禁止读取的字段；`severity`、`owner_role` 等仍然不投影。

#### 5.2.3 靠什么对应

1. **先按成员。** 沿用 ADR 0003 §4.7.1 的成员处置，一行不改。封存读数的主体是一个构件
   `E`（finding 读数从来是按构件读的，成对子范围里上层节点的读数也是）；`E` 在场，当且仅当
   某个处置为 `present` 的成员的来源（构件本身，或它细化出来的成对的 `refined_from`）是
   `E`。否则第 3 步终止，`cause` 写这个成员的处置（例如 `element-deleted-in-reissued-model`）。
2. **再按 `(element_key, requirement_key)`。** 候选 = 本记录里、主体为同一构件 `E`、位于同一个
   证据要求节点的读数所引用的 finding 中，`element_key` 与 `requirement_key` 都与封存依据相同
   者，按 `finding_key` 去重。`model_key` 由 `element_key` 的前缀蕴含。
3. **多个候选：`not-provable`，`cause` 列出全部候选键。不挑、不合并、不取第一个。** 今天一次
   运行里 `(model, requirement, element)` 唯一（`finding_key` 唯一性由 `validate_bundle`
   校验），所以这个分支今天只能由构造出的事实触发（*Round 2* `ambiguous`）。但它必须存在：
   将来任何按实例产出多条结果的检查器，都会让一个没有这个分支的比较默默挑中一条。
4. **零个候选时，区分两种情形：** 运行里根本没有这个坐标的 finding（例如一条规则的适用实体
   被改掉之后，原来那类构件上不再产生它的结果；本轮没有单独测这一例），与运行里有但当前绑定不引用它。两者都是 `no-counterpart`，
   `reason` 不同。

#### 5.2.4 1.7 之前的记录

- **识别：** 读数有 `finding_keys` 而没有 `cited_findings`。只看记录自己带不带依据，不看
  版本号、不看日期。
- **结论：** 这个读数的每个 finding 引用都是 `not-provable` /
  `sealed-citation-has-no-comparison-basis`，**从不**是 `no-counterpart`（实测 9/9）。
- **不补造：** 复检不读规则文件，也不读当前的 `Requirement` 去推算封存一方的值；封存一方的
  依据只来自记录本身。原型 `C` 的比较只读记录与当前事实。**同一个 `finding_key` 在当前事实里
  出现也不算证明**：1.7 之前的键产生于看不见 facet 的派生之下，同键不蕴含同谓词——那正是
  第 2 节。反过来，1.7 的派生 2 改变了 `validation_run_id`，旧键不会在新运行里再出现（第一轮
  实测 0/121），所以这条规则不会让任何一行因"键相同"而被放过。
- **影响面：** 仓库里没有持久化的 1.7 之前记录（Doctor 信封按需现算）。仓库之外保存的 U1
  走查记录属于这一类；复检它们，finding 引用只能得到 `not-provable`。判定引用自 PR #7 起就
  带内容摘要，照常比较。

#### 5.2.5 原型实测（*Round 2* `### C`，O1 + O1b + C，`c9cf3b2`）

第一份记录封存后，对全部 8 个子范围做复检：

| 场景 | finding 行（共 9） | 判定行（共 6） |
|---|---|---|
| `relax` R-005A `required`→`optional` | **`changed` 2**（风管两条，`requirement-semantics` + `finding-content`）；`equivalent` 7（全部换了键） | `equivalent` 6 |
| `retype` R-005A `dataType` | **`changed` 2**（只有 `requirement-semantics`）；`equivalent` 7 | `equivalent` 6 |
| `unrelated` R-002 `dataType` | **`equivalent` 9**，全部 `key_changed=yes` | `equivalent` 6 |
| `pre-1.7-record`（去掉依据后重新封存，再做 R-002 编辑） | **`not-provable` 9**（`sealed-citation-has-no-comparison-basis`） | `equivalent` 6 |
| `reissue`（HVAC 新内容标识，键全换，读数全同） | **`changed` 9**（只有 `model-version`） | `no-counterpart` 6（`determination-not-attributable-to-this-context`） |
| `reissue-deleted`（同上，并删掉风管） | `changed` 6；**`not-provable` 3**（风管的三条，`subject-not-present`，`cause=element-deleted-in-reissued-model`） | `no-counterpart` 6 |
| `ambiguous`（风管 R-005A AssetTag 多一个同坐标 finding） | `equivalent` 8；**`not-provable` 1**（`counterpart-not-unique`，两个候选键都列出） | `equivalent` 6 |

七个场景里没有一行带布尔 `carried`。与第一轮对照：现状下 `relax` 与 `retype` 各有 2 行错误的
`carried`；只做 O1 时，同样两个场景 9/9 行都报"不在被引用的运行里"，连与编辑无关的 R-004、
R-005B 也是——这正是 PM 说"不能以所有旧引用都报缺席作为完成状态"的原因。

### 5.3 二元 `carried` 怎么办（第 2 项）

**设计：从记录文档里删掉 `carried` 键，删掉 Python 属性 `EvidenceCarryOver.carried`；每一行
改为必带 `state`。**

理由：布尔只能装两种情况。四种状态压成两种时，"无法证明"与"没有对应"必然落在同一个
`false` 上；保留一个"只有 `equivalent` 为 true"的布尔，等于继续把后三种合成一个，而 Doctor
今天正是照这个字段显示"是 / 否"。删掉它，是让区分在记录层成立、而不依赖任何 UI 的唯一办法。

同时改变的词表：原 reason `carried`（只用于判定）改名为
`determination-same-reference-same-content`——`carried` 这个名字在四种状态之下已经说不清
是哪一种；finding 的 `finding-absent-from-the-cited-run` 退役，由 5.2.1 的 finding reason 取代。
其余三个判定 reason 不变。

**过渡期的呈现：** Doctor 对不认识的 reason 显示"未识别的值，按原值显示"
（`vocabulary.js` 的 `glossed`），对缺失的键显示"记录未携带"（`screens.js` 的 `field`）。所以在
UI 任务落地之前，复检页的 `carried` 列会对每一行显示"记录未携带"——不是错误陈述，但也不
呈现新的区分。原型下 `test_doctor_preview.py` 与 `test_doctor_adapter.py` 全部通过（*Round 2*
套件结果里没有 Doctor 测试）。

**读取这个字段或沿用词表的全部下游**（按全仓库 grep `carried`、`carry_over`、
`evidence_carry_over`、`EvidenceCarryOver`、`CARRY_OVER_REASONS`、`finding-absent-from-the-cited-run`）：

| 位置 | 读什么 | 归谁改 |
|---|---|---|
| `epc_control_tower/purpose/assessment/record.py:394-420` | `CARRY_OVER_REASONS` 词表 | 修复检查点 |
| `record.py:538-574` | `EvidenceCarryOver`：`carried` 属性与 `as_document` 里的 `"carried"` | 修复检查点 |
| `epc_control_tower/purpose/assessment/recheck.py:361`、`:563-672` | `_carry_over` 与它的调用 | 修复检查点 |
| `epc_control_tower/purpose/assessment/__init__.py` | 导出记录类型（新增 `CitedFinding` 与状态词表） | 修复检查点 |
| `tests/test_purpose_recheck.py`（13 处） | `.carried`、reason 集合；原型下 2 个测试失败，见 5.8 | 修复检查点 |
| `tests/test_doctor_preview.py:331-345` | 遍历 `evidence_carry_over` 行（结构检查）；原型下通过 | 修复检查点核对 |
| `internal/doctor_adapter/` | 原样透传 `as_document()`，不读这些字段（grep 0 处） | 不改；信封内容随记录变 |
| `doctor/static/screens.js:998-1049` | 复检页的"引用 / 原因 / carried / 封存时摘要 / 本记录摘要"表；第 1019 行把 `carried` 显示为"是 / 否"，第 1049 行是表头 | **UI 任务** |
| `doctor/static/vocabulary.js:115-122` | `CARRY_OVER` 词表（含 `carried`、`finding-absent-from-the-cited-run`） | **UI 任务** |
| `doctor/static/screens.js:240-246`、`:538-541` | 读数的 `finding_keys` | 不受影响（设计保留 `finding_keys`） |
| `docs/product/2026-09-16-doctor-d1-screen-flow.md:193`、`:215` | 描述 `reason`、`carried` 的呈现 | **UI 任务**（产品 / UI 文档） |
| ADR 0003 修订记录第 451 行、§4.7.2 第 2080–2093 行、§4.7.6 末段 | 沿用的说法与"finding 分支本来就诚实" | 修复检查点，加修订记录条目 |

**UI 后续任务（需要，由 UI 工程师做）：** 复检页按 `state` 呈现四种状态，不得映射成"是 / 否"；
呈现 `reason`、`changed_aspects`、`key_changed`、`current_citation`、`cause`；更新 `CARRY_OVER`
词表和 D1 画面流程文档。本轮 Framework 不改 `doctor/`，修复检查点也不改。建议排在修复检查点
合并之后、任何对外的复检演示之前。

### 5.4 模型重新发布之后的沿用（第 3 项）——待 BIM 审

**设计：模型版本是比较依据的一个方面。** 对应的 finding 语义相同、内容相同、但
`model_content_id` 不同 → `changed`，`changed_aspects = [model-version]`，**永远不是
`equivalent`**。

理由：

1. **与判定的规则一致。** ADR 0003 把证据归属到具体模型版本：判定必须针对请求所命名的版本
   （§7.1 的版本归属行），一个判定被重新归属到新版本时，它的内容摘要随之改变，被记为内容
   已变（§4.7.6 所说的第二种后果）。如果 finding 跨版本仍记为等价，同一份记录里两种证据就
   用了两种标准，没有理由这样做。
2. **"等价"在这里省不下任何劳动。** PM 说明，证明等价只意味着"不必因为换键重新收集这份
   证据"。finding 在重新发布后本来就由重新验证自动重新收集；记成等价不会省下谁的工作，只会
   多出一个更强的主张：新模型上的这条证据就是旧模型上那一条。
3. **需要的信息都已在记录里。** `changed` + `model-version` 已经说出"读数相同、模型换了"；
   记录不替人下"可以沿用"的结论。

实测：`reissue` 9/9 行 `changed`（只有 `model-version`），判定 6/6 `no-counterpart`（不可归属于
当前上下文）；`reissue-deleted` 被删构件的三条是 `not-provable`，不是 `changed`。

**PM 的限定照原样成立：** 即使是 `equivalent`，也只意味着不必因为换键重新收集这份证据，
**不等于整个交接不用复核**。记录里没有任何字段表达"交接无需复核"，本设计也不增加。

**明确留给 BIM 审的域问题：**

- **D-1** 跨模型版本、读数相同的 finding 是否应当永远不算等价（本设计：是）。
- **D-2** 如果域上需要区分"只改了别的构件的重新发布"与"改了这个构件的重新发布"：今天的
  依据里没有构件级的内容标识，看不见这一点，本设计不提供。
- **D-3** 生产方与消费方的模型分别重新发布时，呈现是否需要不同。依据里有 `model_key`，
  可以区分；呈现归 UI 任务。

### 5.5 P-2(b) 守卫：设计与原型计划（第 4 项）

按指示，本轮只写设计与原型计划；守卫原型是修复检查点的第一步。不需要原型就能测的事实
已经测了（*Round 2* 开头几行）。

**5.5.1 记录派生号。** 快照的 `ruleset` 块新增 `normalized_digest_derivation`（整数），
`contract-1.7.json` 写 `2`。代码里有一张封闭表 `KNOWN_DERIVATIONS = {1, 2}`：1 是现在这种
看不见 facet 的派生，2 是 O1。

**5.5.2 历史快照没有这个字段。** `contract-0.1.json` 到 `contract-1.6.json` 八个文件都没有
（实测）。守卫把"缺字段"解释为派生 1，**只限一份封闭的具名清单**：这八个文件名，以及它们
今天的 sha256，写进代码常量。清单之外、缺字段的记录 → 拒绝（`snapshot-derivation-missing`）；
清单之内、但 sha256 不符（历史快照被改写）→ 拒绝。

**5.5.3 未知派生号必须拒绝。** 记录或当前值的派生号不在封闭表里 → 拒绝
（`unknown-derivation`），不比较、不放行。

**5.5.4 比较规则。** 对同一个 `(ruleset_id, version)`：

- 派生相同：摘要必须相同（今天的规则，不变）；
- 派生不同：**只有**当一条迁移条目精确匹配 `(id, version, from_derivation, from_digest =
  记录值, to_derivation, to_digest = 当前值)` 时才通过，否则就是冲突。**没有"派生不同即放行"
  这条路。**

**5.5.5 具名基线，与"规则内容未变"的证据。** 迁移条目随契约 1.7 提交（放在
`docs/contracts/` 下的一份小文件里，还是作为 `contract-1.7.json` 的一个块，实现时定），写明：

- **基线：** `contract-1.6.json` 及其 sha256，它在 `11e4163` 写入；`epc-delivery` v2.2，派生 1
  摘要 `c3be0db4…`；
- **目标：** 派生 2 摘要，由迁移提交上的规则计算；
- **证据一，字节级，与任何派生都无关：** `rules/epc-delivery` 的 git tree 在 `11e4163`、
  `4e05c03`、`c9cf3b2` 上都是 `de7a6b0e7c29aca72b896a4e1bd2746afb94ee88`（实测），迁移提交上
  必须仍是它。tree id 覆盖目录里每个文件的每个字节，所以它不依赖那个看不见 facet 的摘要；
- **证据二，解析级，运行时可复核，不需要 git 历史：** PR #17 的 `rule_definitions_digest`
  （全部声明字段，含 facet、说明文字、标题）今天是 `a0953845…`（实测）。刷新时守卫从工作树
  重新计算，必须等于条目里的值；
- **明确不用作证据：** 派生 1 的摘要。它看不见 facet，在条目里只作匹配键。

为什么要两份证据：tree id 最强，但 CI 的检出只有一层历史，运行时算不出 `11e4163` 的 tree；
解析级摘要在任何检出上都能算，但它依赖当时的解析器。两者合起来：tree id 在迁移提交时由人
和测试核对并写进条目，解析级摘要在每次刷新时复核。

**5.5.6 对历史快照的预期行为**（当前值 = `epc-delivery` v2.2，派生 2）：

| 快照 | 记录的规则集 | 预期 |
|---|---|---|
| 0.1、1.0 | `ids` 0.1 | id 不同，不比较（同今天） |
| 1.1、1.2、1.3 | `epc-delivery` 1.0 | 版本不同，不比较 |
| 1.4 | 2.0 | 版本不同，不比较 |
| 1.5 | 2.1 | 版本不同，不比较 |
| 1.6 | 2.2，派生 1，`c3be0db4…` | 跨派生：有匹配的迁移条目才通过；没有条目就是 1 条冲突（第一轮实测） |

契约 1.4 写下的既有反例必须保持：1.2 与 1.3 同为 v1.0、同为派生 1、摘要不同，守卫对它们仍然
拒绝（同派生比较不变）。1.7 记录之后，v2.2 上的任何 facet 编辑都会与 1.7 的派生 2 记录冲突
（第一轮用合成记录实测：R-002 与 R-005A 的 `dataType` 各 1 条冲突，说明文字与重排版 0 条）。

**5.5.7 原型要证明的（修复检查点第一步）：**

| # | 条件 | 预期 |
|---|---|---|
| G1 | 没有迁移条目，当前 v2.2 派生 2 对 1.6 | 1 条冲突 |
| G2 | 迁移条目正确 | 0 条冲突 |
| G3 | 有条目，但 R-002 `dataType` 被改 | 冲突（当前派生 2 摘要 ≠ 条目的目标） |
| G4 | 条目的来源摘要 ≠ 1.6 的记录值 | 冲突 |
| G5 | 证据二不符（`rule_definitions_digest` 不等） | 迁移刷新被拒绝 |
| G6 | 合成一条派生号为 3 的记录 | `unknown-derivation` 拒绝 |
| G7 | 缺派生字段、且不在具名清单里的合成记录 | `snapshot-derivation-missing` 拒绝 |
| G8 | 具名清单里某个历史快照的字节被改 | 拒绝 |
| G9 | 1.2 / 1.3 的既有反例；0.1–1.5 | 前者仍拒绝，后者不产生新冲突 |
| G10 | 迁移刷新写出 `contract-1.7.json` 后，再做一次 facet 编辑 | 与 1.7 冲突 |

**停止条件：** 任何一条不能以安全方式成立——尤其是 G3–G8 里出现一条"派生不同即放行"的
路径——修复检查点停在原型，回 PM；**不自动改选 2.3**（PM 裁定）。

### 5.6 P-3：检查器实际消费哪些字段（第 5 项）

证据分两类：代码去向，以及实测（*Round 2* `### P3a`–`### P3c`，另见第一轮）。

**IDS 检查器**（`rule_definitions.py` 的 `FacetDefinition.build` 与 `compile_document`；
`checkers/ids_checker.py` 的 `requirement_label`）：

| 字段 | 代码去向 | 实测 | 进 `semantics_digest` |
|---|---|---|---|
| facet 参数：`entity` 的 `name`/`predefinedType`，`attribute` 的 `name`/`value`，`classification` 的 `system`/`value`/`uri`，`property` 的 `propertySet`/`baseName`/`value`/`dataType`/`uri`，`material` 的 `value`/`uri`，`partof` 的 `name`/`predefinedType`/`relation` | `build()` 构造 IfcTester facet，就是执行的谓词 | 第一轮：`dataType`、适用实体等编辑都改变结果或谓词 | 是 |
| `cardinality` | 作为 facet 的 `cardinality` 交给 IfcTester | R-005A 放宽：2 条 FAIL→PASS，10 条 `expected` 文本变化 | 是 |
| 适用 facet | `specification.applicability` | 第一轮 R-006 | 是 |
| `ifc_version` | `Specification(ifcVersion=…)` | 未单独测 | 是 |
| `instructions` | `build()` 把它作为 `instructions` 交给 IfcTester，只写进编译出的 IDS 文档和 `reports/ids/` 检查报告 | R-005A：finding 0 变化、身份不变；已发布运行改 13 个文件（`reports/ids/` 12 个 + IDS 文档），都不在 `artifact_manifest.json` 里 | **否**（IDS 检查器声明的非执行字段） |
| `title` | `Specification(name=…)`；`specification_label` = "R-xxx: 标题"，是规范化摘要的既有字段 | R-005A：finding 0 变化，但规范化摘要移动，`finding_key` 0/121 存活 | 否。**但仍会换键**（经既有元数据字段），按裁定保留 |
| `description` | `Specification(description=…)` | R-005A：什么都不变 | 否 |
| `severity`、`owner_role`、`stage`、`discipline_scope`、`citation`、`priority`、`labels` | 规范化摘要的既有字段；执行不读 | 已知：编辑会换键 | 否。仍会换键 |

**完整性检查器**（`checkers/completeness.py`）：

| 字段 | 代码去向 | 实测 | 进 `semantics_digest` |
|---|---|---|---|
| `name_pattern` | `parameters()` 从规则文件读回；`_shared_across_models` 用它匹配构件名 | 第一轮：现状下摘要不动；O1 下移动 | 是 |
| `instructions` | `_foreign_requirements` 把它作为 `requirement_label`；`_finding` 写成 `Finding.expected`，即已发布内容 | R-010：6 条 finding 的 `expected` 变化；规范化摘要**今天就**移动（经标签），0/121 | **是**：完整性检查器的非执行字段集为空。不能因为它叫 `instructions` 就排除 |
| 适用 facet（`IFCBUILDINGELEMENTPROXY`） | **检查器不读**：`_shared_across_models` 遍历全部构件，只按名字匹配 | R-010：今天摘要与 finding 都不变；O1b 下 R-010 的语义摘要移动 | 是，理由见下 |

R-010 的适用实体为什么计入：语义摘要覆盖的是**声明的**谓词，不是某个实现碰巧读了什么。如果
排除它，摘要就依赖检查器的内部实现；将来检查器一旦开始尊重它，含义就会无声改变。"声明了
却没被执行"这个差异本身登记为开放点（第 9 节 U8），不在本修复里处理。

**原则：** 排除集由每个检查器在代码里声明，新检查器默认空集。**版本出处：** 被排除的展示
文字仍然随 `(ruleset_id, version)` 一起发布；每次运行的覆盖记录里有 `rule_definitions_digest`
（PR #17，覆盖全部声明字段），把它们绑定到那次运行。这就是它们的版本出处。

### 5.7 P-4、P-5、P-6（第 6 项）

**P-4：`docs/data_contract.md` 要写明的 `semantics_digest` 列**（`requirements.csv`）：

- **值：** 64 位小写十六进制 sha256。
- **覆盖：** 所属规则的 `rule_id`、`checker`、`ifc_version`、全部适用 facet（排序），以及这条
  要求自己 facet 的全部参数，减去该检查器声明的非执行字段（5.6）。**不覆盖：** 标题、描述、
  元数据字段、IDS 规则的 `instructions`。
- **派生版本：** 被哈希的文档里写着 `derivation: 2`；只有同一派生号下的值才可比较。派生号
  同时记在快照的 `normalized_digest_derivation` 里。
- **空值：** 这条要求来自 `.ids` 文档（今天只有冻结的 legacy v0.1，它不出现在
  `requirements.csv` 里）。空值的意思是"没有记录语义指纹"，不是"语义为空"，也不是
  "没有变化"；消费者必须把它当作不可比较。
- **它是什么、不是什么：** 可比较的指纹，**不是完整规则，也不证明检查正确**（PM 原话）。
- 规范化摘要的说明同时补一句：它现在覆盖每条要求的 `semantics_digest`。

**P-5：声称"只钉版本就能约束规则副本"的现有说法**，在修复检查点里一并改正：

| 位置 | 说法 |
|---|---|
| ADR 0002 §3.3，第 1204–1225 行 | 钉在 2.2 的绑定不会对着一个"适用性已在底下改变"的 2.3 默默继续解析 |
| ADR 0002 §4，第 2031–2035 行 | 只有 `ruleset_id` + `ruleset_version` 与键一起在组合时检查，才能补上这个缺口 |
| ADR 0003 §4.1，第 1351–1354 行 | `ruleset_id` + `ruleset_version` 证明这一行仍是绑定所假定的含义 |
| `epc_control_tower/purpose/composition.py:228-231` | `_check_requirement_keys` 的文档字符串，同一说法 |
| `epc_control_tower/purpose/model.py:112-116` | `PackBinding` 的文档字符串：规则集身份随键同行（暗示足够） |
| `purpose-packs/interdisciplinary-coordination-readiness/pack.toml:80-81` | 注释，同上。只改注释不改解析内容；改之前要实测 `composition_digest` 不变 |

另有第 1.3 节列出的七处"摘要已覆盖语义"的说法。改正后的措辞：**只有在"语义变了就必须换
版本"被守卫强制的地方（已发布规则集，经 5.5 的守卫），版本钉住才约束语义；对工作区里的规则
副本，它不约束语义。** 按 P-5 裁定：在建立可信的语义绑定之前，这类副本不得用于正式的 Purpose
放行；采用声明（ADR 0004 检查点 4）与 Purpose 消费边界（ADR 0004 §7.2）仍是接入前置。本设计
不改 Pack / Overlay schema。

**P-6：登记阻塞项 B-1——规则库演进：legacy 当前规则投影。**

- **事实：** legacy 投影按 `requirement_key` 取**当前**规则的结果，而冻结身份摘要的是 v0.1
  文档的字节。v0.1 包含 R-001、R-002、R-003、R-004A、R-004B、R-005A、R-005B。改其中任何一条
  规则的语义，冻结产物都会移动而 legacy `run_id` 不变（R-002 实测：8 个文件，第 2.4 节）。
- **约束（PM 裁定）：** 冻结规则集 v0.1 的既有语义暂不修改。新增规则或版本不一概禁止，但每一次
  都要实测 legacy 字节不动（CI 的 diff 闸门与 snapshot 已经覆盖，读 CI 时要逐步看）。确需修改
  旧规则时，先解决冻结投影或退役路径。
- **与本修复的关系：** 不并入本修复检查点。**特别注意：** 本文和修复检查点的反例都编辑
  R-002 与 R-005A，它们正在 v0.1 里。这些编辑只能发生在一次性检出或测试的临时副本里，**永远
  不提交**。

### 5.8 验收清单与契约 1.7 的移动（第 7 项）

**与 PM 四类反例一一对应的验收测试**（规则编辑都只做在临时副本里）：

| PM 反例 | 测试 | 断言 |
|---|---|---|
| **K1** 放宽要求，模型没变 | R-005A `required`→`optional` 之后复检 | 风管两条引用 `changed`，`changed_aspects ⊇ {requirement-semantics}`；它们不是 `equivalent`；上下文 `is_current`；记录里没有任何一行是 `carried`；记录词表里没有"修好"一类的值（状态与 reason 都是封闭词表） |
| **K2** 谓词变了、outcome 没变 | R-005A `dataType`→`IFCTEXT` | 风管两条 `changed`，`changed_aspects == [requirement-semantics]`（内容摘要相同）；outcome 与判决都不变 |
| **K3** 无关规则改变 | R-002 `dataType` | 9/9 finding 行 `equivalent`，`key_changed=yes`；0 行 `no-counterpart`；判定 6/6 `equivalent` |
| **K4a** 旧记录缺依据 | 去掉依据后重新封存的记录 + R-002 编辑 | 9/9 `not-provable` / `sealed-citation-has-no-comparison-basis`，0 行 `no-counterpart`；复检期间规则目录不可读时结果相同（证明没有读规则去补造） |
| **K4b** 成员消失 | 重新发布并删掉风管 | 风管三条 `not-provable` / `subject-not-present`，`cause` 为成员处置；其余 `changed`（`model-version`） |
| **K4c** 对应不唯一 | 一个坐标上两个 finding | `not-provable` / `counterpart-not-unique`，两个候选键都在 `cause` 里；不选其中任何一个 |
| **K4d** 依据不可用 | 任一边 `semantics_digest` 为空；`basis_version` 未知 | `not-provable`，对应 reason |

另外还有：

- **5.4 的重新发布：** 9/9 `changed`，`changed_aspects == [model-version]`，不是 `equivalent`。
- **检查器方面：** 检查器版本改变、其余相同 → `changed` / `checker`（原型未含，修复检查点补）。
- **守卫：** 5.5.7 的 G1–G10。
- **P-3：** IDS 的说明文字、描述、重排版不移动语义摘要；完整性检查器的 `instructions` 与
  `name_pattern` 移动；标题移动规范化摘要。按今天的实测把这些钉住。
- **legacy：** 冻结规则集摘要等于 `ecd14778…`；8 个 legacy 文件 0 字节变化；legacy `run_id` 不变。
- **确定性：** 两次运行记录逐字节相同，`test_determinism.py` 一字不改。

**契约 1.7 会移动的东西：**

| 类别 | 内容 | 依据 |
|---|---|---|
| canonical 发布物 | `findings.csv`、`issues.csv`、`issue_findings.csv`、`issue_events.csv`、`run.json`、`requirements.csv`（多一列 `semantics_digest`）、`artifact_manifest.json`、`issues.bcf`（21 份 markup） | 第一轮实测 8 个文件；`finding_key` 0/121、`issue_key` 0/21 |
| 快照 | 新增 `contract-1.7.json`，带 `normalized_digest_derivation`；迁移条目；守卫代码 | 5.5 |
| legacy | **不动**：8 个文件 0 字节，legacy `run_id`、冻结摘要不变 | 两轮实测 |
| Purpose 记录的形状 | 读数新增 `cited_findings`；沿用行删掉 `carried`，新增 `state`、`current_citation`、`key_changed`、`changed_aspects`、`cause`；reason 词表改变（5.3） | 5.2、5.3 |
| Purpose 记录的摘要 | 全部移动。夹具第一份记录：现状 `aef0bd06…`，只做 O1 为 `4c5eae80…`，加上 C 之后又变（新值在实现时确定） | 第一轮 `### O1`；*Round 2* 套件结果 |
| 测试 | O1 + O1b + C 原型下 11 个失败：快照 2 个 + 子测试 7 个；`test_purpose_authorisation` 的 `BASE_ASSESSMENT_DIGEST` 1 个；`test_purpose_recheck` 2 个（`test_a_determination_that_did_not_change_at_all_is_carried`、`test_the_repaired_findings_are_new_keys_and_the_old_ones_do_not_carry`） | *Round 2* |
| Doctor | 适配器信封内容随记录改变；`test_doctor_adapter.py`、`test_doctor_preview.py` 原型下全部通过；复检页的 `carried` 列显示"记录未携带"，直到 UI 任务完成 | 5.3 |
| 文档 | `docs/data_contract.md`（新列、语义摘要、规范化摘要的覆盖、派生号）；`docs/bcf_data_contract.md` **不变**（它描述 legacy BCF）；`CHANGELOG.md` 1.7 条目（在刷新之前写）；ADR 0002 §3.3 / §4 与 ADR 0003 §4.1 / §4.7.2 / §4.7.6 的修订条目；第 1.3 节与 5.7 列出的文档字符串；D1 画面流程文档归 UI 任务 | 5.3、5.7 |
| dashboard | 两个校验器 exit 0，不需要改 | 第一轮 `### O1` |

### 5.9 实施与验收顺序（PM 裁定）

1. 原型验证 P-2(b) 的迁移与守卫（5.5.7）。不能安全成立就停，回 PM。
2. 明确并保存沿用比较所需的历史依据（5.2.2）。
3. 落地 O1、复检比较与契约迁移。先写 `CHANGELOG` 的 1.7 条目，再
   `epc-ct snapshot --refresh --contract-changed`。
4. 技术审计 → BIM 定向审计（含 5.4 的 D-1–D-3）→ 产品收口。

UI 任务排在修复检查点之后、任何复检演示之前。这次修复优先于 ADR 0004 的后续检查点；E2–E4 与
第二个 Pack 继续关闭。

## 6. 如何满足 ADR 0004 检查点 4 的前提

ADR 0004 §4.4 第 1 条与 §5.1 检查点 4 要求采用声明钉住规则集的 **id、版本与规范化摘要**，
并把"摘要钉住"列为检查点 4 的验收项（U6）。它的用意是：规则集新增或改变规则时，声明先
不再成立，从而先被拒绝，而不是被默认采用。

- **现状下这个前提不成立。** 摘要对第 1.2 节 8 种编辑中的 6 种语义编辑全部不变，所以一份
  钉住摘要的采用声明会原样接受一个 `dataType`、适用实体或 `name_pattern` 已被改过的规则副本。
  钉了等于没钉。
- **O1 之后成立。** 6/6 种语义编辑移动摘要，钉住它的声明会在打开任何模型之前被拒绝；2/2 种
  非语义编辑不移动，声明不会因为改一句说明或重排版而无谓失效。
- **O2、O3 都不满足：** O2 下摘要在版本不变时仍看不见 facet；O3 不碰摘要。

所以推荐方案必须先于检查点 4 落地——这与 PM"须在项目采用声明及真实闭环演示前闭合"的要求
是同一个顺序。

## 7. ADR 0003 的"按成员对应"不变

本文修的是**证据沿用**这个说法，不是复检的对应关系。实测：

- 现状、O1、O3 三种情况下，复现 2.2 的 8 个子范围的成员处置完全相同：全部 `present`、
  对应全部 `complete`，风管 `READY`、两个风口 `BLOCKED`、烟囱 `UNKNOWN`，openings 四个
  子范围不变（`### RP`、`### O1`、`### O3` 三段）。
- O1 不改 `recheck.py` 一行；它改变的只是被比较的键本身，于是 `_carry_over` 的既有逻辑自己
  给出正确的 `finding-absent-from-the-cited-run`。
- O3 只改 `_carry_over` 的 finding 分支，不碰 `_dispose` / `_landings`。

第二轮：原型 `C` 改了 `_carry_over` 的 finding 分支，并把已经算好的成员处置传给它；它**没有**改
`_dispose` 与 `_landings`。5.2.3 的第一步只**读**成员处置。七个场景里的成员处置都由既有代码给出。

## 8. PM 的裁定（2026-10-01）

以下都是 **PM 的决定**，本文只记录，并注明落在哪一节。初版列出的选项与实测代价见 `14697eb`
的本节，这里不重复。

**总裁定（PM）：** 采纳 O1，但不能只换键，必须同时修正复检对"证据沿用"的判断。PM 接受"键
变了但证据等价，需要单独说明"，**不接受只比较 outcome**：第 2.3 节的改类型就是反例——按
成员、同绑定、同 outcome 比较，会再次错误地宣称沿用。复检必须区分四种情况：引用身份改变但
语义与证据内容比较下来等价；语义或证据内容改变，即使 outcome 相同；找不到对应证据；旧记录
缺少比较依据、无法证明等价。字段、状态名与算法由工程决定。旧记录不能靠读今天的规则补造
历史依据；"无法比较"不能伪装成"证据消失"。**即使证明了证据等价，也只意味着不必因为换键
重新收集这份证据，不等于整个交接不用复核。** → 第 5.2–5.4 节。

**P-1（PM）——O1 与契约迁移。** 采纳 O1，接受契约 1.6 → 1.7 的一次性代价。交付验收必须包含
上面的沿用区分，不能以"所有旧引用都报缺席"作为最终完成状态。保留按成员对应，不重做
`finding_key` 的整套派生。→ 5.1、5.2、5.8。

**P-2（PM）——版本守卫选 (b)。** 规则集保留 2.2，摘要派生版本化。先做守卫原型与历史快照测试。
不得简单地"派生号不同就放行"：这次迁移必须有具名基线和规则内容未变的证据；未知派生不能
绕过检查。原型若不能安全成立，回产品，**不自动改选 2.3**。→ 5.5。

**P-3（PM）——说明文字。** 给人看的标题、指导语不属于执行谓词，但必须有版本出处。本轮新增的
语义摘要排除纯展示文字；现有身份里已纳入的元数据保留，不顺手做一次"全部去文字"的额外迁移，
因此标题等仍可能导致换键，要如实说明。凡被检查器实际消费、影响执行的字段，不能因为名字叫
`instructions` 就排除。→ 5.1、5.6。

**P-4（PM）——发布 `semantics_digest`。** 契约要说明它的覆盖范围、派生版本、空值含义。它是可比较
的指纹，不是完整规则，也不证明检查正确。→ 5.7。

**P-5（PM）——Pack / Overlay 钉摘要。** 本轮不改它们的 schema；但不能继续声称只钉版本就能约束
任意工作区副本。在建立可信的语义绑定之前，这类副本不得用于正式的 Purpose 放行；采用声明与
Purpose 消费边界保持为后续接入的前置。→ 5.7。

**P-6（PM）——legacy 当前规则投影。** 单独登记为规则库演进的阻塞项，不并入本轮重构。冻结规则集
v0.1 的既有语义暂不修改；新增规则或版本不一概禁止，但仍须实测 legacy 字节不动；确需修改旧
规则时，先解决冻结投影或退役路径。→ 5.7（B-1）。

**另外两条（PM）：** IfcTester / ifcopenshell 升级的影响继续列为未验证，不因 O1 落地就宣称所有
"同键异事实"的来源都已解决（→ U2）。这次修复优先于 ADR 0004 的后续核心检查点；E2–E4、第二个
Pack 继续关闭（→ 5.9）。

## 9. 仍然开放

| # | 开放点 | 为什么仍然开放 |
|---|---|---|
| U1 | P-2(b) 守卫能否按 5.5 安全成立 | 本轮按指示只写设计与原型计划；G1–G10 是修复检查点的第一步。不成立就回 PM |
| U2 | IfcTester / ifcopenshell 升级是否让同一对应下的 finding 改变 | 库版本不在身份里（`IdsChecker.version` 的注释说明这是有意的）。设计里的 `finding-content` 方面能看见输出变化，但看不见"输出碰巧相同而实现变了"。PM 裁定继续列为未验证 |
| U3 | 按要求而不是按运行派生 `finding_key` | 超出最小修复，P-1 裁定不重做；四种状态让无关规则的证据不再误报丢失（K3），不需要它 |
| U4 | A→B→A 编辑 | 按构造，摘要与键回到原值；未单独测 |
| U5 | B-1 在 Phase 5 之前会不会被别的变更触发 | 今天由快照与 CI 的 diff 挡住；只测了 R-002 一例 |
| U6 | 私有真实模型上的规模 | 本轮只用仓库样例；私有模型不进仓库 |
| U7 | 采用声明钉住摘要之后的实际拒绝行为 | ADR 0004 检查点 4 的验收项 |
| U8 | R-010 声明了适用实体，但完整性检查器不读它 | 代码事实（5.6）。它是规则定义与检查器之间的差异，归谁判断（规则作者、BIM）、要不要修，本文不定 |
| U9 | 第 5.4 节的 D-1–D-3 | **待 BIM 审的域问题** |
| U10 | 检查器指纹方面；`basis_version` 检查 | 设计里有，原型 `C` 没实现；修复检查点补上并加测试（5.8 的"检查器方面"与 K4d） |
| U11 | 迁移条目放在哪个文件、叫什么 | 实现细节，修复检查点定；5.5.5 已定它必须包含的内容 |
| U12 | 仓库之外的 1.7 之前记录（U1 走查记录）今后怎么处理 | 按本设计复检它们只能得到 `not-provable`；是否需要重新评估它们，是产品问题 |

## 10. 非目标

不改代码、规则、身份派生、契约、快照、Pack、Overlay、测试或任何生成产物；不改 ADR 0003 的成员
对应；不改 legacy 派生；不改 `doctor/`；不碰 E2–E4、第二个 Pack、ADR 0004 的检查点 2–4；私有
模型不进仓库。第 1.3 节与 5.7 列出的错误说法本文只列出，不改——它们和代码在同一个修复检查点里
改，免得文档先于代码声称已修。

## 11. 测量索引

**第一轮**（`4e05c03`，证据 README 的 *Transcript*）：

| 本文内容 | 证据段 |
|---|---|
| 基线运行 0 变化、881 个测试通过 | `### S0` |
| 8 种编辑下摘要不变、源文件摘要为空 | `### D` |
| 逐键的状态变化（R-002 9 条；R-005A 2 条 + 10 条文本；R-005A 改类型 0 条） | `### RB` |
| 第 2.2、2.3 节的复现 | `### RP` |
| 已发布运行上的 R-002 编辑（含 legacy 8 个文件）与说明文字编辑 | `### SQ` |
| O1：摘要、发布代价、守卫、组合、复检、测试 | `### O1` |
| O1i | `### O1i` |
| O2：发布代价、守卫、组合、测试、带版本号的复检 | `### O2` |
| O1 + 2.3 | `### O1+2.3` |
| O3 | `### O3` |
| O1 第一版原型被 `validate_bundle` 拒绝 | README 的"O1 的第一版" |
| 放宽之下文本变了的那 10 条 | README 的"补充测量" |

**第二轮**（`c9cf3b2`，证据 README 的 *Round 2*）：

| 本文内容 | 证据段 |
|---|---|
| 规则目录 tree 在 `11e4163`、`4e05c03`、`c9cf3b2` 相同；`rule_definitions_digest` | 开头几行 |
| 标题、描述、说明文字、R-010 编辑对今天摘要的影响 | `### P3a` |
| 它们对 finding 的影响 | `### P3b` |
| O1 + O1b 下哪些语义摘要移动 | `### P3c` |
| 四种状态的七个场景，以及原型下的测试结果 | `### C` |
| 快照 0.1–1.6 记录的规则集、没有派生字段 | 5.5.2（逐个读取八个快照文件） |
| 下游清单 | 5.3（全仓库 grep） |
