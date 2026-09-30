# 0005 — 规则语义身份与证据沿用（设计裁定包）

- **状态：Proposed，停在 PM 裁定。** 本文只含设计与测量：**不增改任何生产代码、身份派生、
  规则、契约、快照、Pack、Overlay、测试或生成产物**；`data/processed/`、`reports/`、`ids/`
  与 legacy 字节均未移动。第 3 节的三个方案都真的跑过，但原型只存在于一次性检出里，只为测量。
- **日期：** 2026-09-30。**基线：** `main` = `4e05c03`。
- **输入（在仓库之外）：** PM 本轮原始要求（新增优先项：复现"finding key 不变但事实改变"的
  真实复检行为，提出规则语义身份及证据沿用的最小修复与契约代价，须在项目采用声明及真实闭环
  演示前闭合；E2–E4、第二 Pack 不开工）；技术总监在 `4e05c03` 上实测的五条事实。本轮**没有**
  BIM 域输入；本文不作任何域主张。
- **证据：** [`docs/evidence/rule-semantic-identity-2026-09-30/`](../evidence/rule-semantic-identity-2026-09-30/README.md)，
  一条命令从 `4e05c03` 的一次性检出复现，只用仓库内已跟踪的文件。本文每个数字都能在那里的
  运行记录里找到对应段落（第 11 节）。
- **与既有决定的关系：** 不改 ADR 0001 的身份派生（本文只提议，第 5 节）；**不改 ADR 0003
  的"按成员对应"**（第 7 节实测它在每个方案下都不动）；满足 ADR 0004 检查点 4 前提的方式见
  第 6 节；不碰 ADR 0004 检查点 2–4。

---

## 0. 一页结论

**缺陷，一句话：** 规则集的规范化摘要不含任何 facet 参数，所以只改规则"检查什么"时，
`validation_run_id` 与全部 `finding_key` 原样保留；复检只要 `finding_key` 还在就记 `carried`，
于是**同一个键下的事实变了，记录却说"证据沿用"**。

**真实复检路径上的复现（第 2 节）：** 只把 R-005A 的两条要求从 `required` 改为 `optional`，
模型一个字节没动、上下文未变。风管 `hvac::38WbwIGD90nB_3T2BTU5Ed` 在
`schedules-and-room-data-sheets` 上从 `BLOCKED` 变成 `READY`；支撑它的两个键
`d0bdd588-…`、`5454a69b-…` 由 `FAIL` 变 `PASS`，**后继记录把两者都记为 `carried`**。
另一个编辑（R-005A 的 `dataType` 改 `IFCTEXT`）更隐蔽：两个键下 finding 的**每一个发布字节
都不变**，规则的谓词却已经变了，同样记为 `carried`。

**三个方案，全部实测（第 3 节）：**

| | O1 facet 进规范化摘要 | O2 只靠版本纪律 | O3 引用旁附 finding 内容摘要 |
|---|---|---|---|
| 抓住"放宽"复现（FAIL→PASS） | **是**（键全部换新，记 `finding-absent-from-the-cited-run`） | 只有作者记得升版本时；忘了就是现状 | 是（`finding-content-changed-under-the-same-key`） |
| 抓住"改类型"复现（字节全同） | **是** | 同上 | **否**，仍记 `carried` |
| 已发布 canonical / BCF | 0/121 键、0/21 issue、21 份 markup | 同左 | **0 变化** |
| legacy 冻结产物与身份 | **0 变化**，冻结规则集摘要不变 | 0 变化 | 0 变化 |
| Pack / Overlay 钉住 `2.2` | 照常组合 | **组合被拒**（`binding-ruleset-mismatch`） | 照常组合 |
| 全套测试（881 基线） | 10 失败（快照 9，记录摘要钉 1） | **25 失败 + 218 错误**（Purpose / Doctor 全线） | 1 失败（记录摘要钉） |
| ADR 0004 检查点 4 前提 | **满足** | 不满足 | 不满足 |

**推荐（第 5 节）：O1**——每条要求带一个"它评估什么"的语义摘要并纳入规范化摘要，冻结的
`.ids` 路径不带、因而 legacy 摘要不变；走契约 **1.6 → 1.7** 的仪式。附带一个必须由 PM 裁定的
代价岔路：既有的"一个版本号只指一套规则"守卫会拒绝 v2.2 换摘要（实测 1 条冲突），要么
升到 2.3（实测会连带 Pack、Overlay 与 243 个测试），要么让快照记录摘要的派生版本（未原型，
第 8 节 P-2）。

**"语义变了、版本号没变"（第 4 节）：** 两者都要。身份负责**自动**抓住它（O1 之后，6 种
facet 编辑 6 次都移动摘要，2 种非语义编辑 0 次）；版本纪律负责**给人一个名字**，而仓库里
早就有把这条纪律机器化的守卫——只是它今天摘要的东西和身份一样看不见 facet，所以一次也
不会触发。O1 让同一个守卫看得见（实测：记录 O1 摘要后，R-002 与 R-005A 的 facet 编辑各
触发 1 条冲突，说明文字与重排版 0 条）。

---

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

这些都是本文的发现，**本文不改其中任何一处**；它们在实现检查点里随代码一起改（第 5.3 节）：

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
| openings #1–#4 | 不变；8 条判定引用全部 `carried`（判定内容确实没变） |

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

## 5. 推荐方案：O1，走契约 1.7

### 5.1 内容

1. `Requirement` 增加一个语义摘要字段，由规则定义编译时计算，覆盖：所属规则的 `rule_id`、
   `checker`、`ifc_version`、全部适用 facet、这条要求自己的 facet 的全部参数；**不含**
   `instructions`（P-3）；带派生号。
2. `build_ruleset_normalized_digest` 在该字段非空时纳入它；从 `.ids` 加载的要求为空，
   冻结规则集的摘要逐字节不变。
3. `validate_bundle` 不需要改：它照旧从 `Requirement` 重算，语义在要求上，所以重算成立
   （原型实测）。
4. 同一实现检查点里改正第 1.3 节列出的全部说法；ADR 0003 §4.7.6 与 ADR 0002 §3.3 按各自
   的修订记录格式加一条修订，不改写历史段落的意思之外的文字。
5. 钉住反例测试（硬规则 6）：六种 facet 编辑各自移动摘要；说明文字与重排版不移动；冻结规则集
   摘要等于 `ecd14778…`；复现 2.2 与 2.3 的后继记录里 0 行 `carried`。

### 5.2 契约流程

**必须走 1.6 → 1.7。** 实测已发布 canonical 键全部移动、`requirements.csv` 多一列、
`snapshot` 失败。按 `AGENTS.md` 硬规则 2：先写 `CHANGELOG` 的 1.7 条目（写明本文第 3.2 节的
逐文件变化与 legacy 0 变化），再 `epc-ct snapshot --refresh --contract-changed`。刷新会被
版本守卫拒绝（实测 1 条冲突），**怎么过这一关是 P-2**，本文不替 PM 决定。

### 5.3 不在推荐方案里

不改 `finding_key` 的派生、不改 legacy 任何派生、不改复检的成员对应、不给 Purpose 开读规则
文件的路径、不引入 O3。O3 在 O1 之后是否还值得做（例如 IfcTester 升级那一类仍在身份之外的
变化，U2）留作以后的独立问题。

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

## 8. 需要 PM 裁定的

**P-1　是否采纳 O1 作为最小修复，并接受契约 1.7 的一次性代价。** 代价（实测）：已发布 canonical
0/121 键、0/21 issue、21 份 BCF markup、`requirements.csv` 多一列、`artifact_bundle_id` 变；
legacy 0 字节、legacy 身份不变；Pack / Overlay 不变；1 个 Purpose 记录摘要钉需重钉；Doctor
测试不受影响。

**P-2　版本守卫这一关怎么过。** 守卫对"v2.2 换了摘要"报 1 条冲突，两条路：

- **(a) 升到 2.3。** 与 `ruleset.toml` 自己写下的规则字面一致（"anything else that moves the
  normalized digest" 升次版本号）。实测连带：Pack 与 Overlay 组合被拒，须改 Pack 内容（及其
  `pack_version` 是否升的连锁问题）、Overlay、夹具；测试 25 失败 + 218 错误须逐一迁移。
- **(b) 保留 2.2，让快照记录摘要的派生号，守卫只比较同一派生下的摘要。** 理由：规则集本身
  一条没变，变的是指纹的算法；"2.2"仍然只指一套规则。代价：快照记录多一个字段、守卫改几行，
  **本轮未原型**；已实测的只有"不改守卫就拒绝"。

我倾向 (b)：它让"版本号只指一套规则"保持为真，又不把一次指纹算法的修正变成 Pack/Overlay
的产品变更。但这改变了 `ruleset.toml` 版本规则的一句字面解释，属于 PM 裁定。

**P-3　`instructions` 算不算语义。** 实测：它不改变任何 finding，只改变 `reports/ids/` 下 12 个
检查报告与编译出的 IDS 文档（13 个文件，都不在 `artifact_manifest.json` 里）。O1 排除它、
O1i 包含它。我倾向排除——改一句说明不应重编全部键。已知的不对称：完整性检查器（R-010）的
`instructions` 本来就是它的 `requirement_label`，已经在摘要里。

**P-4　`semantics_digest` 是否作为 `requirements.csv` 的公开列。** 发布它，消费者能看出键为什么
动了；不发布，契约只多一个摘要定义、不多一列。两者契约代价同级（都要 1.7）。

**P-5　Pack / Overlay 的绑定是否也钉规范化摘要。** 本轮**不做**：Pack schema "1" 已声明发布并冻结
（ADR 0002 addendum），加字段是另一次 schema 决定。这里只把缺口写明：O1 + 守卫之后，已发布
规则集的语义编辑必然换版本号，版本钉住因此可信；隔离工作区里的规则副本不经过守卫，版本钉住
对它无效，只有检查点 4 的摘要钉住挡得住。

**P-6　legacy 投影读当前规则结果（第 2.4 节）是否另立一项。** 本文不修，冻结派生不动；
今天由快照逐字节比较挡住。是否需要在 Phase 5 之前单独处理，由 PM 排优先级。

## 9. 仍然未知

| # | 未知 | 为什么仍未知 |
|---|---|---|
| U1 | P-2(b) 守卫改动的实际形状与它对历史快照（1.1–1.6）的行为 | 本轮未原型 |
| U2 | IfcTester / ifcopenshell 升级是否让同一键下的 finding 改变 | `IdsChecker.version` 有意不含库版本（`ids_checker.py` 注释），库版本只作出处记录；本轮没有换库测量 |
| U3 | 按要求而非按运行派生 `finding_key`（让无关规则的键在编辑后存活）的代价 | 会改 `finding_key` 派生本身，超出"最小修复"，未测 |
| U4 | 一次编辑前后又改回（A→B→A）时 O1 的行为 | 按构造摘要回到原值、键回到原值；未单独测 |
| U5 | legacy 投影读当前规则结果在 Phase 5 之前是否会被别的变更触发 | 今天由快照挡住；第 2.4 节只测了 R-002 一例 |
| U6 | 真实（私有）模型上复现的规模 | 本轮只用仓库样例；私有模型不进仓库，本轮也没有在工作区里跑 |
| U7 | 采用声明钉住摘要之后的实际拒绝行为 | 检查点 4 的验收项；本文只证明 O1 之后摘要值得钉 |

## 10. 非目标

不改代码、规则、身份派生、契约、快照、Pack、Overlay、测试或任何生成产物；不改 ADR 0003 的
成员对应；不改 legacy 派生；不碰 E2–E4、第二个 Pack、ADR 0004 的检查点 2–4；私有模型不进
仓库。第 1.3 节列出的错误说法本文只列出，不改——它们与代码同在一个实现检查点里改，避免文档
先于代码声称已修。

## 11. 测量索引

| 本文内容 | 证据段 |
|---|---|
| 基线运行 0 变化、881 测试通过 | `### S0` |
| 8 种编辑摘要不变、源文件摘要为空 | `### D` |
| 逐键状态变化（R-002 9 条、R-005A 2 条 + 10 条文本、R-005A 改类型 0 条） | `### RB` |
| 第 2.2、2.3 节复现 | `### RP` |
| 已发布运行上的 R-002 编辑（含 legacy 8 个文件）与说明文字编辑 | `### SQ` |
| O1：摘要、发布代价、守卫、组合、复检、测试 | `### O1` |
| O1i | `### O1i` |
| O2：发布代价、守卫、组合、测试、带版本号的复检 | `### O2` |
| O1 + 2.3 | `### O1+2.3` |
| O3 | `### O3` |
| O1 第一版原型被 `validate_bundle` 拒绝 | 证据说明"O1 的第一版" |
| 放宽下那 10 条文本变化是哪些 | 证据说明"补充测量" |
