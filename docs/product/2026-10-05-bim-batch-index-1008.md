# BIM 分批条目索引：10/8 批

10/8 批按 D6 的清单分两层：A 层（D6 逐条点名）299 条，B 层（D6 说的“优先主路径及 C2 相关误读风险”，但 D6 清单没有逐条点名）95 条。BIM 容量不足时，B 层是最先可以让给 10/15 的部分。标“已由 #40 修改，待 BIM 复核”的条目是 P0（中英行动一致）改过措辞的，索引里是 a5b89d0（含 #40）的措辞。

本批：394 条英文条目（原文 12、原有 517 条内 362、#40 新增 20）；另有 34 条新增中文终稿或候选条目。

列的含义见[总览](2026-10-05-bim-batch-index.md)。提交与 PR 对照见总览末尾。

### ACTIVITY_NAMES（6 条）— 活动名

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E001 | `builders-work-openings.name` | Builder's-work openings | 土建预留开洞 | Pack／产品文档原文；en #33 `39ae8ba`；zh #21 `542636a` | en 85 页（fixture/recheck ×61; fixture/result ×12; fixture/item ×10; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×7；zh 0 页（未渲染到） |
| E002 | `builders-work-openings.needs` | Needs to know where MEP penetrates architectural fabric, so openings can be cut in walls, floors and roof. | 要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。 | Pack／产品文档原文；en #33 `39ae8ba`；zh #21 `542636a` | en 10 页（fixture/item ×10）；例 `#/fixture/member-evidence/item/0/2/0`；zh 10 页 |
| E003 | `ceiling-and-bulkhead-geometry.name` | Reflected ceiling and bulkhead layout | 吊顶平面与包封布置 | Pack／产品文档原文；en #33 `39ae8ba`；zh #21 `968422d` | en 70 页（fixture/recheck ×49; fixture/result ×11; fixture/item ×8; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×7；zh 0 页（未渲染到） |
| E004 | `ceiling-and-bulkhead-geometry.needs` | Needs to know where MEP equipment physically is, in which storey, so ceiling zones and bulkheads can be drawn around it. | 要知道交出方的设备在哪一层、在什么位置，才能围着它画吊顶分区和包封。 | Pack／产品文档原文；en #33 `39ae8ba`；zh #21 `542636a` | en 8 页（fixture/item ×8）；例 `#/fixture/member-evidence/item/1/1/0`；zh 8 页 |
| E005 | `schedules-and-room-data-sheets.name` | Room data sheets and equipment schedules | 房间数据表与设备明细表 | Pack／产品文档原文；en #33 `39ae8ba`；zh #21 `542636a` | en 70 页（fixture/recheck ×49; fixture/result ×11; fixture/item ×8; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×7；zh 0 页（未渲染到） |
| E006 | `schedules-and-room-data-sheets.needs` | Needs each piece of equipment to carry the project's asset identity, so a schedule can be keyed to it. | 要每件设备都带有项目的资产标识，明细表才能按它编排。 | Pack／产品文档原文；en #33 `39ae8ba`；zh #21 `542636a` | en 8 页（fixture/item ×8）；例 `#/fixture/member-evidence/item/2/1/0`；zh 8 页 |

页面上下文（`E001` `builders-work-openings.name`）：
- en `#/fixture/member-evidence`：Not a known model defect: no coordination review has determined yet whether it passes through the re ‹ Builder's-work openings: Unknown › 2 items

页面上下文（`E002` `builders-work-openings.needs`）：
- en `#/fixture/member-evidence/item/0/2/0`：What this work needs ‹ Needs to know where MEP penetrates architectural fabric, so openings can be cut in walls, floors and roof. › 2. What to do, who deals with it, what a recheck must show
- zh `#/fixture/member-evidence/item/0/2/0`：这项工作需要什么 ‹ 要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。 › 二、要做什么、由谁处理、完成后拿什么复检

### VERDICT_LABELS（3 条）— 英文判断词

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E007 | `READY` | Ready | 可以开始 | 记录判断码；en #33 `39ae8ba`；zh #21 `968422d` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 181 页 |
| E008 | `BLOCKED` | Blocked | 受阻 | 记录判断码；en #33 `39ae8ba`；zh #21 `968422d` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 181 页 |
| E009 | `UNKNOWN` | Unknown | 无法判断 | 记录判断码；en #33 `39ae8ba`；zh #21 `968422d` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 181 页 |

页面上下文（`E007` `READY`）：
- en `#/fixture/member-evidence`：building element ‹ Ready › This conclusion rests on simulated evidence:Simulated human determination ×1
- zh `#/fixture/member-evidence`：building element ‹ 可以开始 › 这个结论建立在模拟证据上：模拟的人工判定 ×1

页面上下文（`E008` `BLOCKED`）：
- en `#/fixture/member-evidence`：This result: 13 in all; to deal with: 8 ‹ Blocked › 4 items: the work concerned is Blocked
- zh `#/fixture/member-evidence`：本次结果：共 13 个事项，其中 8 个需要处理 ‹ 受阻 › 4 个事项：对应的那项工作 受阻

### VERDICT_WORDS（3 条）— 英文判断词

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E010 | `READY` | Every piece of necessary evidence is present and satisfies the applicable acceptance conditions, and there is no unresolved blocker and no evidence gap. The activity can start, within the assessed scope | 必要的证据齐全且满足验收条件，没有未解决的阻碍，也没有证据缺口：在本次评估范围内，这项工作可以开始 | 产品文档原文；en #33 `39ae8ba`；zh #21 `542636a` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 181 页 |
| E011 | `BLOCKED` | A known unmet requirement prevents the activity | 有一项已知未满足的要求，阻止这项工作 | 产品文档原文；en #33 `39ae8ba`；zh #21 `542636a` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 181 页 |
| E012 | `UNKNOWN` | An evidence gap makes the activity undecidable — the evidence needed to answer the question was never produced, so neither release nor refusal can be justified | 回答这个问题所需的证据没有产生，这项工作能否开始无法决定：既不能放行，也不能拒绝 | 产品文档原文；en #33 `39ae8ba`；zh #21 `542636a` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 181 页 |

页面上下文（`E010` `READY`）：
- en `#/fixture/member-evidence`：The three conclusion words ‹ Ready: Every piece of necessary evidence is present and satisfies the applicable acceptance conditions, and there is no unresolved blocker and no evidence gap. The activity can start, within the assessed scope. › Blocked: A known unmet requirement prevents the activity.
- zh `#/fixture/member-evidence`：三个判断词 ‹ 可以开始：必要的证据齐全且满足验收条件，没有未解决的阻碍，也没有证据缺口：在本次评估范围内，这项工作可以开始。 › 受阻：有一项已知未满足的要求，阻止这项工作。

页面上下文（`E011` `BLOCKED`）：
- en `#/fixture/member-evidence`：Ready: Every piece of necessary evidence is present and satisfies the applicable acceptance conditio ‹ Blocked: A known unmet requirement prevents the activity. › Unknown: An evidence gap makes the activity undecidable — the evidence needed to answer the question
- zh `#/fixture/member-evidence`：可以开始：必要的证据齐全且满足验收条件，没有未解决的阻碍，也没有证据缺口：在本次评估范围内，这项工作可以开始。 ‹ 受阻：有一项已知未满足的要求，阻止这项工作。 › 无法判断：回答这个问题所需的证据没有产生，这项工作能否开始无法决定：既不能放行，也不能拒绝。

### ACTIONS（20 条）— 源修改与复检行动（#40 新增的英文）

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E013 | `missing-project-asset-identity.action` | In the source model, add to this element the asset-identity properties the project's convention requires (see the property sets and property names listed), then re-export the model | 在源模型里给这个构件补上本项目约定的资产标识属性（见所列属性集和属性名），重新导出 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 50 页（fixture/recheck ×32; fixture/result ×10; fixture/item ×6; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×3；zh 50 页 |
| E014 | `missing-project-asset-identity.recheck` | On the reissued model, this element passes every requirement listed, and no element in the scope is left unevaluated | 重新发布的模型上，这个构件在所列每条要求下都通过，范围内没有构件漏评 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 36 页（fixture/recheck ×30; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；同页最多 ×2；zh 36 页 |
| E015 | `asset-identity-not-evaluated.action` | The existing asset-identity rules do not reach this element, so whether it has an asset identity has not been evaluated, and it cannot be judged to be missing one; for the same reason, whether this work can start cannot be decided. First confirm whether the project's convention requires this element to have an asset identity, and whether the rules should reach it. Until that is confirmed, this does not mean it must have one. | 现有资产标识规则没有覆盖到这个构件，所以它有没有资产标识还没有被评估，不能判断是否缺少；这项工作能否开始也因此无法判断。先确认项目约定是否要求它具备资产标识，以及规则该不该覆盖到它。在确认之前，这不表示它必须具备资产标识。 | 界面文字；en #40 `295da77`；zh #23 `fd1fe79`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 34 页（fixture/recheck ×19; fixture/result ×11; fixture/item ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 34 页 |
| E016 | `asset-identity-not-evaluated.recheck` | Every element in the scope has an evaluation result under the requirements bound to it | 范围内每个构件在所绑定的要求下都有评估结果 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 12 页（fixture/recheck ×10; fixture/item ×2）；例 `#/fixture/member-evidence/item/2/1/0`；同页最多 ×2；zh 12 页 |
| E017 | `in-model-position-not-evaluated.action` | This is not a known model defect, and the model does not need changing. The spatial-assignment check rules do not reach this element; the rules' scope of application needs to be extended | 这不是已知的模型缺陷，也不需要改模型。空间归属的检查规则没有覆盖到这个构件，需要扩展规则的适用范围 | 界面文字；en #40 `295da77`；zh #23 `fd1fe79`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 34 页（fixture/recheck ×19; fixture/result ×11; fixture/item ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 34 页 |
| E018 | `in-model-position-not-evaluated.recheck` | Every element in the scope has a check result under the requirements bound to it | 范围内每个构件在所绑定的要求下都有检查结果 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 12 页（fixture/recheck ×10; fixture/item ×2）；例 `#/fixture/member-evidence/item/1/1/0`；同页最多 ×2；zh 12 页 |
| E019 | `penetration-not-determined.action` | This is not a known model defect. No coordination review has yet determined whether it passes through the receiving side's elements; hold a review and record either “no penetration” or which elements it passes through | 这不是已知的模型缺陷。还没有协调评审判定它是否穿过接收方的构件；需要开一次评审，记录“不穿过”或写明穿过哪些构件 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 50 页（fixture/recheck ×33; fixture/result ×11; fixture/item ×4; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×3；zh 50 页 |
| E020 | `penetration-not-determined.recheck` | A recorded review determination exists for the model versions listed | 针对所列模型版本，有一份评审判定记录 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 28 页（fixture/recheck ×24; fixture/item ×4）；例 `#/fixture/member-evidence/item/0/2/0`；同页最多 ×2；zh 28 页 |
| E021 | `missing-corresponding-opening.action` | In the receiving side's model, model an opening or shaft in the element it passes through, not a void in the handing-over side's model. One opening for each element it passes through | 在接收方模型里、被穿过的构件上建出洞口或竖井，不要做成交出方模型里的空洞。穿过几个构件就要几个洞口 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 19 页（fixture/recheck ×9; fixture/result ×6; fixture/item ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 19 页 |
| E022 | `missing-corresponding-opening.recheck` | The opening check for this pair reports “opening modelled and cross-referenced”. Modelling the opening alone is not enough | 这一对的开洞核查结果为“洞口已建且已关联”。只建洞不够 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 13 页（fixture/recheck ×11; fixture/item ×2）；例 `#/fixture/member-evidence/item/0/4/0`；同页最多 ×2；zh 13 页 |
| E023 | `cross-model-alignment-not-confirmed.action` | This is not a known misalignment. No one has yet confirmed, by the method the project accepts, that the two models are aligned; do this once against the model versions listed, and record it | 这不是已知的错位。还没有人按项目接受的方法确认两侧模型对齐；需要针对所列模型版本做一次并记录 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 24 页（fixture/recheck ×19; fixture/result ×5）；例 `#/fixture/recheck-both-reissued`；同页最多 ×3；zh 24 页 |
| E024 | `cross-model-alignment-not-confirmed.recheck` | The alignment confirmation has been done and reports the models aligned, naming the model versions | 对齐确认已做，结果为已对齐，写明模型版本 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 14 页（fixture/recheck ×14）；例 `#/fixture/recheck-both-reissued/recheck/5/0`；zh 14 页 |
| E025 | `mep-element-not-spatially-assigned.action` | In the source model, place the element on its correct level and in its correct space, then re-export | 在源模型里把构件放到正确的标高和空间上，重新导出 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E026 | `mep-element-not-spatially-assigned.recheck` | On the reissued model, this element passes its spatial-assignment requirement | 重新发布的模型上，这个构件的空间归属要求通过 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E027 | `cross-model-misalignment.action` | Re-acquire the project's shared coordinate datum, re-export against the shared origin (not by moving geometry), then redo the alignment confirmation by the method the project accepts | 重新获取项目共用的坐标基准，按共用原点重新导出（不靠移动几何），再按项目接受的方法重做对齐确认 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E028 | `cross-model-misalignment.recheck` | The alignment confirmation is redone against the new versions and reports the models aligned | 针对新版本重做对齐确认，结果为已对齐 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E029 | `opening-not-verifiably-linked.action` | In the receiving side's model, add to the opening a cross-reference back to the element that passes through it. Where several elements pass through one opening, each needs its own | 在接收方模型里，给洞口补上指回穿过它的那个构件的关联。一个洞口供几个构件穿过，每个各要一条 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E030 | `opening-not-verifiably-linked.recheck` | The cross-reference check for this pair reports the opening cross-referenced | 这一对的关联核查结果为已关联 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E031 | `opening-status-not-determined.action` | This is not a known missing opening. The review of the opening is not complete: whether it is modelled, and whether it is cross-referenced | 这不是已知的缺洞。开洞情况的评审没完成：洞口是否已建、是否已关联 | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E032 | `opening-status-not-determined.recheck` | The check gives a definite result (cross-referenced / modelled but not cross-referenced / not modelled) | 核查给出明确结果（已关联／已建未关联／未建） | 界面文字；en #40 `295da77`；zh #21 `968422d`；**已由 #40 修改，待 BIM 复核（en 新增）** | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E013` `missing-project-asset-identity.action`）：
- en `#/fixture/member-evidence`：Basis of this conclusion:Real check output ×2 ‹ In the source model, add to this element the asset-identity properties the project's convention requires (see the property sets and property names listed), then re-export the model › One elementchimney coverIfcAirTerminal (IFC class) · 00 groundfloor · model hvacRoom data sheets and
- zh `#/fixture/member-evidence`：这个结论的依据：真实检查输出 ×2 ‹ 在源模型里给这个构件补上本项目约定的资产标识属性（见所列属性集和属性名），重新导出 › 一个构件chimney cover风口 IfcAirTerminal · 00 groundfloor · 模型 hvac房间数据表与设备明细表：受阻这个结论的依据：真实检查输出 ×2 要做什么在源模

页面上下文（`E014` `missing-project-asset-identity.recheck`）：
- en `#/fixture/member-evidence/item/2/2/0`：What a recheck must show ‹ On the reissued model, this element passes every requirement listed, and no element in the scope is left unevaluated › Source wording (as the record carries it): for tracing, not an instruction
- zh `#/fixture/member-evidence/item/2/2/0`：完成后拿什么复检 ‹ 重新发布的模型上，这个构件在所列每条要求下都通过，范围内没有构件漏评 › 来源原文（英文，记录所带）：供追溯，不是操作指令

### ACTION_GROUPS（12 条）— 源修改与复检行动

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E033 | `open.label` | Items to deal with | 需要处理的事项 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 24 页（fixture/result ×12; fixture/recheck ×10; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 0 页（未渲染到） |
| E034 | `open.summary` | the record gives an action | 记录给出了处理动作 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 0 页（未渲染到） |
| E035 | `open.none` | The record gives no action for any item. | 记录没有为任何一个事项给出处理动作。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 2 页（fixture/result ×1; fixture/recheck ×1）；例 `#/fixture/recheck-comparison`；zh 2 页 |
| E036 | `open.note` | Each item's page says which elements it involves, what to do, who deals with it and what a recheck must show. | 每个事项的页面写明涉及的构件、要做什么、由谁处理、完成后拿什么复检。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 18 页（fixture/result ×9; fixture/recheck ×9）；例 `#/fixture/recheck-requirement-relaxed`；zh 18 页 |
| E037 | `unplaced.label` | Items to check by hand | 需要人工核对的事项 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 12 页（fixture/result ×6; fixture/recheck ×6）；例 `#/fixture/recheck-both-reissued`；zh 0 页（未渲染到） |
| E038 | `unplaced.summary` | the record gives no current state; check by hand | 记录没有给出当前情况，需要人工核对 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 12 页（fixture/result ×6; fixture/recheck ×6）；例 `#/fixture/recheck-both-reissued`；zh 12 页 |
| E039 | `unplaced.none` | The record gives a current state for every item. | 每个事项记录都给出了当前情况。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E040 | `unplaced.note` | The record does not say what these items' conclusions are now. An element that is gone does not mean the problem was fixed. | 这些事项现在是什么判断，记录没有说。构件不在了不代表问题已修复。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 12 页（fixture/result ×6; fixture/recheck ×6）；例 `#/fixture/recheck-both-reissued`；zh 12 页；同句（en）：VERDICT_GROUPS.unplaced.note |
| E041 | `none.label` | Items for which the record gives no follow-up action | 记录没有给出后续处理动作的事项 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 14 页（fixture/result ×7; fixture/recheck ×5; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 14 页 |
| E042 | `none.summary` | the record gives no follow-up action | 记录没有给出后续处理动作 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 14 页（fixture/result ×7; fixture/recheck ×5; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×2；zh 14 页 |
| E043 | `none.none` | There are no such items. | 没有这样的事项。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E044 | `none.note` | The record gives no follow-up action for the items below. Each line's conclusion stands on its own, with its scope beside it. | 记录没有为下面这些事项给出后续处理动作。每一行的结论各自成立，范围写在它旁边。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 14 页（fixture/result ×7; fixture/recheck ×5; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 14 页 |

页面上下文（`E033` `open.label`）：
- en `#/fixture/member-evidence`：An item is the conclusion for one element (or a pair of elements assessed together) on one piece of ‹ Items to deal with, by handling team (8 items) › Example handling team

页面上下文（`E034` `open.summary`）：
- en `#/fixture/recheck-requirement-relaxed`：This result: 13 items ‹ 7 items: the record gives an action › 6 items: the record gives no follow-up action

### BASIS_WORDS（8 条）— 规则来源

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E051 | `simulated` | This conclusion rests on simulated evidence: | 这个结论建立在模拟证据上： | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 16 页（fixture/item ×12; fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×6；zh 16 页 |
| E052 | `real` | Basis of this conclusion: | 这个结论的依据： | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 18 页（fixture/item ×14; fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×7；zh 0 页（未渲染到） |
| E053 | `sharedSimulated` | Basis shared by the items in this group, some of it simulated: | 同组事项共用的依据，其中有模拟证据： | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 88 页（fixture/recheck ×79; fixture/result ×9）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×12；zh 88 页 |
| E054 | `sharedReal` | Basis shared by the items in this group: | 同组事项共用的依据： | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 65 页（fixture/recheck ×56; fixture/result ×9）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×7；zh 0 页（未渲染到） |
| E055 | `none` | This conclusion cites no evidence. | 这个结论没有引用任何证据。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E056 | `gaps.no-finding` | no check result at all (a real absence) | 没有任何检查结果（真实的缺席） | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 46 页（fixture/recheck ×29; fixture/result ×11; fixture/item ×4; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×2；zh 46 页 |
| E057 | `gaps.no-determination` | no determination yet (a real absence) | 还没有判定（真实的缺席） | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 64 页（fixture/recheck ×47; fixture/result ×11; fixture/item ×4; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×10；zh 64 页 |
| E058 | `gaps.not-applicable-finding` | there are check results, but the check did not apply and did not cover it | 有检查结果，但检查不适用，没有覆盖到它 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E051` `simulated`）：
- en `#/fixture/member-evidence`：Simulated human determination ‹ This conclusion rests on simulated evidence:Simulated human determination ×2 › In the receiving side's model, model an opening or shaft in the element it passes through, not a voi
- zh `#/fixture/member-evidence`：模拟的人工判定 ‹ 这个结论建立在模拟证据上：模拟的人工判定 ×2 › 在接收方模型里、被穿过的构件上建出洞口或竖井，不要做成交出方模型里的空洞。穿过几个构件就要几个洞口

页面上下文（`E052` `real`）：
- en `#/fixture/member-evidence`：no determination yet (a real absence) ×1 ‹ Basis of this conclusion:no determination yet (a real absence) ×1 › "Unknown" means whether this work can start cannot be decided: it does not mean the element has no p

### BESIDE（8 条）— 范围限制

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E059 | `readyScope` | Holds for this one item, this work and the listed model versions only; it does not mean the whole handover is complete. | 只对这一个事项、这项工作、所列的模型版本成立；不代表整次交接完成。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 54 页（fixture/recheck ×35; fixture/item ×10; fixture/result ×7; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×7；zh 54 页 |
| E060 | `unknown` | "Unknown" means whether this work can start cannot be decided: it does not mean the element has no problem, and it is not a system error. | “无法判断”说的是这项工作能否开始无法判断：不等于这个构件没有问题，也不是系统出错。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 88 页（fixture/recheck ×67; fixture/result ×11; fixture/item ×8; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×12；zh 88 页 |
| E061 | `assetIdentity` | Where the asset-identity value comes from, and which Revit parameter it maps to, the record does not say. | 资产标识的取值从哪里来、对应哪个 Revit 参数，记录未提供。 | 界面文字；en #33 `39ae8ba`；zh #21 `42720ab` | en 6 页（fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；zh 6 页 |
| E062 | `team` | The handling team is an entry in the record; it does not mean the work has been assigned. | 处理团队是记录里的安排，不代表已经派发。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 107 页（fixture/recheck ×87; fixture/item ×16; fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×3；zh 107 页 |
| E063 | `simulatedTeam` | Example handling team | 示例处理团队 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 107 页（fixture/recheck ×87; fixture/item ×16; fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×3；zh 107 页 |
| E064 | `noTeam` | Not given in the record | 记录未提供 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E065 | `defaultRole` | Default handling role (the rule's default, not an assignment) | 默认处理角色（规则给出的默认，不是指派） | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 107 页（fixture/recheck ×87; fixture/item ×16; fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×3；zh 107 页 |
| E066 | `unchanged` | Unchanged by the recheck | 复检前后未变 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 112 页（fixture/recheck ×103; fixture/result ×9）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×13；zh 0 页（未渲染到） |

页面上下文（`E059` `readyScope`）：
- en `#/fixture/member-evidence`：This conclusion rests on simulated evidence:Simulated human determination ×1 ‹ Holds for this one item, this work and the listed model versions only; it does not mean the whole handover is complete. › building element | Builder's-work openings: ReadyThis conclusion rests on simulated evidence:Simulat
- zh `#/fixture/member-evidence`：这个结论建立在模拟证据上：模拟的人工判定 ×1 ‹ 只对这一个事项、这项工作、所列的模型版本成立；不代表整次交接完成。 › building element ｜ 土建预留开洞：可以开始这个结论建立在模拟证据上：模拟的人工判定 ×1 只对这一个事项、这项工作、所列的模型版本成立；不代表整次交接完成。

页面上下文（`E060` `unknown`）：
- en `#/fixture/member-evidence`：Basis of this conclusion:no determination yet (a real absence) ×1 ‹ "Unknown" means whether this work can start cannot be decided: it does not mean the element has no problem, and it is not a system error. › What to do
- zh `#/fixture/member-evidence`：这个结论的依据：还没有判定（真实的缺席） ×1 ‹ “无法判断”说的是这项工作能否开始无法判断：不等于这个构件没有问题，也不是系统出错。 › 要做什么

### CITATION_KINDS（2 条）— 规则来源

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E097 | `finding` | Check-result citation | 检查结果引用 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 78 页（fixture/recheck ×69; fixture/result ×9）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×6；zh 0 页（未渲染到） |
| E098 | `determination` | Determination citation | 判定引用 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 81 页（fixture/recheck ×71; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 0 页（未渲染到） |

页面上下文（`E097` `finding`）：
- en `#/fixture/recheck-requirement-relaxed`：Check results and human determinations are two kinds of evidence, counted apart and never added toge ‹ Check-result citation (9 rows) › Comparison basis unchanged × 7Only the citation's key changed × 7

页面上下文（`E098` `determination`）：
- en `#/fixture/recheck-requirement-relaxed`：Check-result citation (9 rows)Comparison basis unchanged × 7Only the citation's key changed × 7Compa ‹ Determination citation (6 rows) › Comparison basis unchanged × 6The same determination: the same reference and the same content digest

### CITATION_PROVENANCE（12 条）— 规则来源

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E099 | `finding-real.key` | real | real | 界面文字；en #33 `39ae8ba`；zh #13 `69678df` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E100 | `finding-real.short` | Real check output | 真实检查输出 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×9；zh 468 页 |
| E101 | `finding-real.long` | A check-result citation without the simulation marker: from a real check run, the product of checking a real IFC model against real rules. | 未带模拟标记的检查结果引用：来自真实的检查运行，是真实 IFC 模型按真实规则检查的产物。 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 468 页 |
| E102 | `finding-fixture.key` | fixture | fixture | 界面文字；en #33 `39ae8ba`；zh #13 `69678df` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E103 | `finding-fixture.short` | Simulated check result | 模拟的检查结果 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×13；zh 468 页 |
| E104 | `finding-fixture.long` | A check-result citation with the simulation marker (starting with fixture): generated by the example, not the output of any real check run. | 带模拟标记（以 fixture 开头）的检查结果引用：由示例生成，不是任何真实检查运行的输出。 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 468 页 |
| E105 | `determination-fixture.key` | fixture | fixture | 界面文字；en #33 `39ae8ba`；zh #13 `69678df` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E106 | `determination-fixture.short` | Simulated human determination | 模拟的人工判定 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×7；zh 468 页 |
| E107 | `determination-fixture.long` | A determination citation with the simulation marker: supplied by the example; no coordination review ever took place. | 带模拟标记的判定引用：由示例提供，没有任何协调评审真的发生过。 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 468 页 |
| E108 | `determination-unmarked.key` | unmarked | unmarked | 界面文字；en #33 `39ae8ba`；zh #13 `69678df` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E109 | `determination-unmarked.short` | Determination of unstated source | 来源未标注的判定 | 界面文字；en #33 `39ae8ba`；zh #13 `69678df` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 468 页 |
| E110 | `determination-unmarked.long` | A determination citation without the simulation marker: a determination is not the output of a check run, and this interface has nothing it can verify about where it came from, so it says neither real nor simulated. | 未带模拟标记的判定引用：判定不是检查运行的输出，本界面也没有可核依据说明它来自哪里，因此不作真实或模拟的断言。 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 468 页 |

页面上下文（`E100` `finding-real.short`）：
- en `#/fixture/member-evidence`：One elementhouse - chimneyIfcChimney (IFC class) · 00 groundfloor · model hvacRoom data sheets and e ‹ Real check output › Basis of this conclusion:Real check output ×2
- zh `#/fixture/member-evidence`：一个构件house - chimney烟囱 IfcChimney · 00 groundfloor · 模型 hvac房间数据表与设备明细表：无法判断这个结论的依据：没有任何检查结果（真实的缺席） × ‹ 真实检查输出 › 这个结论的依据：真实检查输出 ×2

页面上下文（`E101` `finding-real.long`）：
- en `#/fixture/member-evidence`：Each citation's source label on this page is decided from that citation alone (whether it carries th ‹ Real check output A check-result citation without the simulation marker: from a real check run, the product of checking a real IFC model against real rules. › Simulated check result
- zh `#/fixture/member-evidence`：本页每条引用旁的来源标注按该条引用自身判定（是否带模拟标记），不按整页或整份记录推断： ‹ 真实检查输出 未带模拟标记的检查结果引用：来自真实的检查运行，是真实 IFC 模型按真实规则检查的产物。 › 模拟的检查结果

### CONDITION_ENTRIES（10 条）— 源修改与复检行动

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E111 | `named-outcome-observed.text` | Only the named outcome observed; the rest of the condition not checked | 仅命名结果已观察到；条件其余部分未检查 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页；同句（en）：CONDITION_STATES.named-outcome-observed |
| E112 | `named-outcome-observed.plain` | The outcome named in the original recheck condition is now observed. The rest of the condition was not checked by machine and needs a person to confirm it against the original condition; this is not "the whole condition is met". | 原复检条件里点名的那个结果，现在观察到了。条件句的其余部分没有被机器检查，需要人对照原条件确认；这不是“整句条件已满足”。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E113 | `named-outcome-not-observed.text` | Named outcome not observed | 未观察到命名结果 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 25 页（fixture/recheck ×15; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 25 页；同句（en）：CONDITION_STATES.named-outcome-not-observed |
| E114 | `named-outcome-not-observed.plain` | The outcome named in the original recheck condition is not observed now: the original condition is not reached. | 原复检条件里点名的那个结果，现在没有观察到：原条件未达成。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 5 页（fixture/recheck ×5）；例 `#/fixture/recheck-requirement-relaxed/recheck/3/0`；zh 5 页 |
| E115 | `no-machine-checkable-part.text` | The condition has no machine-checkable part; a person must read it | 条件没有可机检部分，需要人阅读 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 87 页（fixture/recheck ×77; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 87 页；同句（en）：CONDITION_STATES.no-machine-checkable-part |
| E116 | `no-machine-checkable-part.plain` | The original recheck condition has no part a machine can check; a person needs to read the original condition and judge it. The record draws no conclusion on it. | 原复检条件没有机器能检查的部分，需要人阅读原条件并判断；记录对它不下结论。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 67 页（fixture/recheck ×67）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 67 页 |
| E117 | `not-comparable.text` | Cannot be compared: the corresponding elements are incomplete | 不可比较：对应的构件不完整 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 29 页（fixture/recheck ×19; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 29 页；同句（en）：CONDITION_STATES.not-comparable |
| E118 | `not-comparable.plain` | No conclusion can be drawn on the original recheck condition: some of the original elements are no longer in this record, so the condition has no complete subject to check. This does not mean the condition is met. | 无法对原复检条件下结论：原来的构件有的已经不在本次记录里，条件没有完整的对象可以检查。这不代表条件已满足。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 9 页（fixture/recheck ×9）；例 `#/fixture/recheck-both-reissued/recheck/3/0`；zh 9 页 |
| E119 | `no-recheck-condition.text` | The original record had no recheck condition | 原记录没有复检条件 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 70 页（fixture/recheck ×60; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 70 页；同句（en）：CONDITION_STATES.no-recheck-condition |
| E120 | `no-recheck-condition.plain` | The original record had no recheck condition: the original conclusion left nothing outstanding. | 原记录没有复检条件：原来的判断没有留下待办。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 50 页（fixture/recheck ×50）；例 `#/fixture/recheck-requirement-relaxed/recheck/0/0`；zh 50 页 |

页面上下文（`E111` `named-outcome-observed.text`）：
- en `#/fixture/recheck-requirement-relaxed`：named-outcome-observed ‹ Only the named outcome observed; the rest of the condition not checked › named-outcome-not-observed
- zh `#/fixture/recheck-requirement-relaxed`：named-outcome-observed ‹ 仅命名结果已观察到；条件其余部分未检查 › named-outcome-not-observed

页面上下文（`E113` `named-outcome-not-observed.text`）：
- en `#/fixture/recheck-requirement-relaxed`：named-outcome-not-observed ‹ Named outcome not observed › no-machine-checkable-part
- zh `#/fixture/recheck-requirement-relaxed`：named-outcome-not-observed ‹ 未观察到命名结果 › no-machine-checkable-part

### CONDITION_STATES（5 条）— 源修改与复检行动

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E121 | `named-outcome-observed` | Only the named outcome observed; the rest of the condition not checked | 仅命名结果已观察到；条件其余部分未检查 | 界面文字；en #34 `50d129b`；zh #13 `55e90ba` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页；同句（en）：CONDITION_ENTRIES.named-outcome-observed.text |
| E122 | `named-outcome-not-observed` | Named outcome not observed | 未观察到命名结果 | 界面文字；en #34 `50d129b`；zh #13 `55e90ba` | en 25 页（fixture/recheck ×15; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 25 页；同句（en）：CONDITION_ENTRIES.named-outcome-not-observed.text |
| E123 | `no-machine-checkable-part` | The condition has no machine-checkable part; a person must read it | 条件没有可机检部分，需要人阅读 | 界面文字；en #34 `50d129b`；zh #13 `55e90ba` | en 87 页（fixture/recheck ×77; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 87 页；同句（en）：CONDITION_ENTRIES.no-machine-checkable-part.text |
| E124 | `not-comparable` | Cannot be compared: the corresponding elements are incomplete | 不可比较：对应的构件不完整 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 29 页（fixture/recheck ×19; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 29 页；同句（en）：CONDITION_ENTRIES.not-comparable.text |
| E125 | `no-recheck-condition` | The original record had no recheck condition | 原记录没有复检条件 | 界面文字；en #34 `50d129b`；zh #13 `55e90ba` | en 70 页（fixture/recheck ×60; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 70 页；同句（en）：CONDITION_ENTRIES.no-recheck-condition.text |

页面上下文（`E121` `named-outcome-observed`）：
- en `#/fixture/recheck-requirement-relaxed`：named-outcome-observed ‹ Only the named outcome observed; the rest of the condition not checked › named-outcome-not-observed
- zh `#/fixture/recheck-requirement-relaxed`：named-outcome-observed ‹ 仅命名结果已观察到；条件其余部分未检查 › named-outcome-not-observed

页面上下文（`E122` `named-outcome-not-observed`）：
- en `#/fixture/recheck-requirement-relaxed`：named-outcome-not-observed ‹ Named outcome not observed › no-machine-checkable-part
- zh `#/fixture/recheck-requirement-relaxed`：named-outcome-not-observed ‹ 未观察到命名结果 › no-machine-checkable-part

### CONSEQUENCE_KINDS（4 条）— 源修改与复检行动

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E126 | `work-cannot-start` | This work cannot start | 这项工作不能开始 | 界面文字；en #34 `50d129b`；zh #21 `542636a` | en 30 页（fixture/recheck ×24; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；zh 0 页（未渲染到） |
| E127 | `work-suspended` | This work is suspended | 这项工作暂停 | 界面文字；en #34 `50d129b`；zh #21 `542636a` | en 73 页（fixture/recheck ×63; fixture/item ×10）；例 `#/fixture/member-evidence/item/0/2/0`；zh 59 页 |
| E128 | `rework-risk` | Risk of rework | 有返工风险 | 界面文字；en #34 `50d129b`；zh #21 `542636a` | en 14 页（fixture/recheck ×14）；例 `#/fixture/recheck-both-reissued/recheck/5/0`；zh 0 页（未渲染到） |
| E129 | `re-identification-and-reissue-risk` | Risk of re-identification: documents that cite these identifiers would then have to be reissued too | 有重新标识的风险：引用这些标识的文件届时也须重新出具 | 界面文字；en #34 `50d129b`；zh #26 `d6f89c1` | en 30 页（fixture/recheck ×24; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；zh 30 页 |

页面上下文（`E126` `work-cannot-start`）：
- en `#/fixture/member-evidence/item/2/2/0`：What it means for this work ‹ This work cannot startRisk of re-identification: documents that cite these identifiers would then have to be reissued too › What a recheck must show

页面上下文（`E127` `work-suspended`）：
- en `#/fixture/member-evidence/item/0/2/0`：What it means for this work ‹ This work is suspended › What a recheck must show
- zh `#/fixture/member-evidence/item/0/2/0`：对这项工作的后果 ‹ 这项工作暂停 › 完成后拿什么复检

### DEMO_NOTICE（1 条）— 范围限制

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E130 | `(整表)` | Simulated example: the project settings in the example, including the handling teams and the acceptance of evidence methods, are demonstration settings, not real project decisions; the evidence for a conclusion may be a real check result, a simulated check result or a simulated human determination — which one, the "Basis" line beside each conclusion says (citation by citation). Not for formal project decisions, and no formal check record can be exported. | 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的检查结果或模拟的人工判定，具体是哪一种，看每个结论旁的“依据”一行（按逐条引用标明）。不能用于正式项目决定，也不能导出正式检查记录。 | 界面文字；en #33 `39ae8ba`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

### DETAILS_WORDS（18 条）— 规则来源

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E131 | `heading` | What exactly is missing | 具体缺什么 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 16 页（fixture/item ×16）；例 `#/fixture/member-evidence/item/0/2/0`；zh 0 页（未渲染到） |
| E132 | `absent` | Not given in the record: the returned data has no requirement details for this citation. | 记录未提供：返回数据里没有这条引用的要求明细。 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E133 | `determinations` | This conclusion cites human determinations, not check results; a determination has no requirement details. What is missing is said in the conclusion and in "What to do" above. | 这个结论引用的是人工判定，不是检查结果；判定没有要求明细。缺的是什么，见上面的结论和“要做什么”。 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 2 页（fixture/item ×2）；例 `#/fixture/member-evidence/item/0/4/0`；zh 2 页 |
| E134 | `nothingCited` | This conclusion cites no check result, so there are no requirement details to show. | 这个结论没有引用任何检查结果，所以没有要求明细可以显示。 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 8 页（fixture/item ×8）；例 `#/fixture/member-evidence/item/0/2/0`；zh 8 页 |
| E135 | `requirement` | Requirement not met | 不满足的要求 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 36 页（fixture/recheck ×30; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；同页最多 ×6；zh 36 页 |
| E136 | `requirementMet` | Requirement | 要求 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 30 页（fixture/recheck ×30）；例 `#/fixture/recheck-requirement-relaxed/recheck/5/0`；zh 30 页 |
| E137 | `rule` | Rule | 规则编号 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 66 页（fixture/recheck ×60; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；zh 66 页 |
| E138 | `status` | Result of that check | 那次检查的结果 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 66 页（fixture/recheck ×60; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；同页最多 ×6；zh 66 页 |
| E139 | `reason` | Reason | 原因 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 66 页（fixture/recheck ×60; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；zh 206 页 |
| E140 | `actual` | Value that check observed | 那次检查观察到的值 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 66 页（fixture/recheck ×60; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；同页最多 ×6；zh 66 页 |
| E141 | `noActual` | That check observed no value | 那次检查没有观察到值 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 66 页（fixture/recheck ×60; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；同页最多 ×6；zh 66 页 |
| E142 | `hasActual` | That check observed a value; this page does not show it | 那次检查观察到了值；本页不显示取值 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E143 | `expected` | The rule's own words | 规则的原话（英文） | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 77 页（fixture/recheck ×60; fixture/item ×6; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `#/fixture/member-evidence/item/2/2/0`；同页最多 ×6；zh 77 页；同句（en）：WORKSPACE.ruleExpected |
| E144 | `source` | Source the rule gives:  | 规则给出的出处（英文原文）： | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 66 页（fixture/recheck ×60; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；同页最多 ×6；zh 66 页 |
| E145 | `projectAssumption` | This is a requirement agreed for this project, not a general one. | 这是本项目约定的要求，不是通用要求。 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 36 页（fixture/recheck ×30; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；同页最多 ×6；zh 36 页 |
| E146 | `gap` | What value to fill in, and which Revit parameter it maps to, the record does not say. | 要填什么值、对应哪个 Revit 参数，记录未提供。 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E147 | `prior` | At the assessment before the recheck, this evidence's requirement and result were as follows. Having this description does not make the row comparable; the row's state is what is written above. | 复检前那次评估时，这条证据的要求和结果如下。有这段说明不等于这一行可以比较；这一行的状态以上面写的为准。 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 60 页（fixture/recheck ×60）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；同页最多 ×6；zh 60 页 |
| E148 | `currentAbsent` | The corresponding evidence this record cites: its requirement details are not given in the record. | 本次记录引用的对应证据：要求明细记录未提供。 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 54 页（fixture/recheck ×54）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；同页最多 ×6；zh 54 页 |

页面上下文（`E131` `heading`）：
- en `#/fixture/member-evidence/item/0/2/0`：The name is taken from the model file itself; it may be empty or shared with other elements. To find ‹ 4. What exactly is missing › This conclusion cites no check result, so there are no requirement details to show.

页面上下文（`E133` `determinations`）：
- en `#/fixture/member-evidence/item/0/4/0`：4. What exactly is missing ‹ This conclusion cites human determinations, not check results; a determination has no requirement details. What is missing is said in the conclusion and in "What to do" above. › Then: how this item changed after a recheck
- zh `#/fixture/member-evidence/item/0/4/0`：四、具体缺什么 ‹ 这个结论引用的是人工判定，不是检查结果；判定没有要求明细。缺的是什么，见上面的结论和“要做什么”。 › 然后：这一项复检后的变化

### DIRECTORY_NOTE（1 条）— 范围限制

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E149 | `(整表)` | Each example is one check record. The evidence for a conclusion may be a real check result, a simulated check result or a simulated human determination; which one it is, the "Basis" line beside each conclusion on the result and item pages says, citation by citation. The project settings in the examples, including the handling teams and the acceptance of evidence methods, are demonstration settings, not real project decisions. | 每个示例是一份检查记录。一个结论的证据可能是真实检查的结果，可能是模拟的检查结果，也可能是模拟的人工判定；具体是哪一种，看结果页和事项页每个结论旁的“依据”一行，按逐条引用标明。示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定。 | 界面文字；en #33 `39ae8ba`；zh #26 `d6f89c1` | en 1 页（fixture/list ×1）；例 `#/fixture`；zh 1 页 |

页面上下文（`E149` ``）：
- en `#/fixture`：Choose a simulated example ‹ Each example is one check record. The evidence for a conclusion may be a real check result, a simulated check result or a simulated human determination; which one it is, the "Basis" line beside each conclusion on the result and item pages says, citation by citation. The project settings in the examples, including the handling teams and the acceptance of evid › Step 1
- zh `#/fixture`：选择一个模拟示例 ‹ 每个示例是一份检查记录。一个结论的证据可能是真实检查的结果，可能是模拟的检查结果，也可能是模拟的人工判定；具体是哪一种，看结果页和事项页每个结论旁的“依据”一行，按逐条引用标明。示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定。 › 第一步

### EXAMPLE_NOTE（1 条）— 范围限制

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E178 | `(整表)` | An example's description is written by whoever built the example and says only what the example was given; it is not a conclusion of any check. What the check concluded is on the result page only. | 示例说明由搭建示例的人提供，只说这个示例被给了什么；它不是检查得出的结论。检查得出了什么，只看结果页。 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 1 页（fixture/list ×1）；例 `#/fixture`；zh 1 页 |

页面上下文（`E178` ``）：
- en `#/fixture`：Step 2The models did not change, but a handover conclusion didThe same record after a recheck: neith ‹ An example's description is written by whoever built the example and says only what the example was given; it is not a conclusion of any check. What the check concluded is on the result page only. › Other simulated examples
- zh `#/fixture`：第二步模型未改，但交接判断发生变化同一份记录复检之后：两侧模型都没有重新发布，却有判断变了。变的是哪一项，为什么？示例说明 这个示例被给了：一条被引用的检查要求放宽了；交出方和接收方的模型版本都没有变 ‹ 示例说明由搭建示例的人提供，只说这个示例被给了什么；它不是检查得出的结论。检查得出了什么，只看结果页。 › 其他模拟示例

### FINDING_STATUS（3 条）— PASS／FAIL／N/A／拒绝区别

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E179 | `FAIL` | Fail | 不通过 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 54 页（fixture/recheck ×30; fixture/item ×6; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `#/fixture/member-evidence/item/2/2/0`；zh 54 页 |
| E180 | `PASS` | Pass | 通过 | 界面文字；en #34 `50d129b`；zh #21 `42720ab` | en 35 页（fixture/recheck ×30; ws-compare:workspace/finding ×3; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `#/fixture/recheck-requirement-relaxed/recheck/5/0`；zh 35 页 |
| E181 | `N/A` | Not applicable | 不适用 | 界面文字；en #34 `50d129b`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；同页最多 ×8；zh 18 页 |

页面上下文（`E179` `FAIL`）：
- en `#/fixture/member-evidence/item/2/2/0`：Result of that check ‹ Fail › Reason
- zh `#/fixture/member-evidence/item/2/2/0`：那次检查的结果 ‹ 不通过 › 原因

页面上下文（`E180` `PASS`）：
- en `#/fixture/recheck-requirement-relaxed/recheck/5/0`：Result of that check ‹ Pass › Reason
- zh `#/fixture/recheck-requirement-relaxed/recheck/5/0`：那次检查的结果 ‹ 通过 › 原因

### HANDOVER_SIDES（2 条）— 处理角色／指派

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E182 | `producing` | the handing-over side's model in this handover | 本次交接中交出方的模型 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 157 页（fixture/recheck ×131; fixture/item ×26）；例 `#/fixture/member-evidence/item/0/2/0`；zh 0 页（未渲染到） |
| E183 | `consuming` | the receiving side's model in this handover | 本次交接中接收方的模型 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 25 页（fixture/recheck ×21; fixture/item ×4）；例 `#/fixture/member-evidence/item/0/4/0`；zh 0 页（未渲染到） |

页面上下文（`E182` `producing`）：
- en `#/fixture/member-evidence/item/0/2/0`：Model ‹ hvac: the handing-over side's model in this handoverThis is a model identifier, not a statement of discipline › Discipline

页面上下文（`E183` `consuming`）：
- en `#/fixture/member-evidence/item/0/4/0`：No storey assignment in the model ‹ architecture: the receiving side's model in this handoverThis is a model identifier, not a statement of discipline › 2iPwJwpPDCSgMheXwk9cBTCopy

### HOME（7 条）— 范围限制（首页写明不能做什么）

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E186 | `status` | This is an example preview: you cannot import your own Revit model yet, and it gives no overall compliance or ready-to-build conclusion. | 当前为示例预览：尚不能导入自己的 Revit 模型，也不提供整体合规或可施工结论。 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 1 页（home ×1）；例 `#/`；zh 1 页 |
| E187 | `statusWithWorkspace` | Two things are offered here: a real check already run in the workspace named when the server was started, and simulated examples. You cannot import, choose or change a model on this page, and it gives no overall compliance or ready-to-build conclusion. | 当前同时提供两样：启动服务器时指定的工作区里一次已经跑完的真实检查，以及模拟示例。页面上不能导入、选择或更换模型，也不提供整体合规或可施工结论。 | 界面文字；en #33 `39ae8ba`；zh #27 `70198bb`；#27／#31 终稿：#27 70198bb | en 5 页（home ×5）；例 `ws-compare:#/`；zh 5 页 |
| E188 | `statusWorkspaceUnknown` | Could not confirm whether the server was started with a workspace, so there is no entry to a real check here; that does not mean there is no workspace — the error is below. The simulated examples are available as usual. You cannot import, choose or change a model on this page, and it gives no overall compliance or ready-to-build conclusion. | 未能确认服务器是否指定了工作区，所以这里没有真实检查的入口；这不等于没有工作区，错误原文在下面。模拟示例照常可看。页面上不能导入、选择或更换模型，也不提供整体合规或可施工结论。 | 界面文字；en #33 `39ae8ba`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E195 | `cannot[0]` | Import, choose or change a model on the page, including your own Revit or IFC model | 在页面上导入、选择或更换模型，包括自己的 Revit 或 IFC 模型 | 界面文字；en #33 `39ae8ba`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 6 页（home ×6）；例 `#/`；zh 6 页 |
| E196 | `cannot[1]` | Give an overall compliance, ready-to-build or "ready to hand over" conclusion | 给出整体合规、可施工或“可以交付”的结论 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 6 页（home ×6）；例 `#/`；zh 6 页 |
| E197 | `cannot[2]` | Write back to a model, upload to the cloud, or open an element in Revit | 写回模型、上传到云端，或在 Revit 里打开构件 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 6 页（home ×6）；例 `#/`；zh 6 页 |
| E200 | `cannotNote` | These are not implemented, so the page has no entry for them. | 这些功能没有实现，所以页面上没有对应的入口。 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba`；中文原句在此前的代码里已有，随该提交移入词表 | en 6 页（home ×6）；例 `#/`；zh 6 页 |

页面上下文（`E186` `status`）：
- en `#/`：For a BIM manager: what a pre-handover check found; after a recheck, which conclusions changed, whic ‹ This is an example preview: you cannot import your own Revit model yet, and it gives no overall compliance or ready-to-build conclusion. › What you can do now
- zh `#/`：帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。 ‹ 当前为示例预览：尚不能导入自己的 Revit 模型，也不提供整体合规或可施工结论。 › 现在可以做什么

页面上下文（`E187` `statusWithWorkspace`）：
- en `ws-compare:#/`：For a BIM manager: what a pre-handover check found; after a recheck, which conclusions changed, whic ‹ Two things are offered here: a real check already run in the workspace named when the server was started, and simulated examples. You cannot import, choose or change a model on this page, and it gives no overall compliance or ready-to-build conclusion. › What you can do now
- zh `ws-compare:#/`：帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。 ‹ 当前同时提供两样：启动服务器时指定的工作区里一次已经跑完的真实检查，以及模拟示例。页面上不能导入、选择或更换模型，也不提供整体合规或可施工结论。 › 现在可以做什么

### ITEM_UNIT（1 条）— 范围限制

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E201 | `(整表)` | An item is the conclusion for one element (or a pair of elements assessed together) on one piece of the receiving side's work. The same element can appear in several items, so the number of items is not a number of defects. | 一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。同一个构件可以出现在几个事项里，所以事项数不是缺陷数。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×2；zh 181 页 |

页面上下文（`E201` ``）：
- en `#/fixture/member-evidence`：5 items: the record gives no follow-up action (listed further down this page) ‹ An item is the conclusion for one element (or a pair of elements assessed together) on one piece of the receiving side's work. The same element can appear in several items, so the number of items is not a number of defects. This record involves 6 different elements. › Items to deal with, by handling team (8 items)
- zh `#/fixture/member-evidence`：5 个事项：记录没有给出后续处理动作（列在本页下方） ‹ 一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。同一个构件可以出现在几个事项里，所以事项数不是缺陷数。这份记录共涉及 6 个不同的构件。 › 需要处理的事项，按处理团队（8 个事项）

### PROVENANCE_NOTICE（1 条）— 范围限制

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E227 | `(整表)` | Each citation's source label on this page is decided from that citation alone (whether it carries the simulation marker), never inferred for the whole page or record: | 本页每条引用旁的来源标注按该条引用自身判定（是否带模拟标记），不按整页或整份记录推断： | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 468 页 |

页面上下文（`E227` ``）：
- en `#/fixture/member-evidence`：How the source of evidence is labelled ‹ Each citation's source label on this page is decided from that citation alone (whether it carries the simulation marker), never inferred for the whole page or record: › Real check output A check-result citation without the simulation marker: from a real check run, the
- zh `#/fixture/member-evidence`：证据来源的标注 ‹ 本页每条引用旁的来源标注按该条引用自身判定（是否带模拟标记），不按整页或整份记录推断： › 真实检查输出 未带模拟标记的检查结果引用：来自真实的检查运行，是真实 IFC 模型按真实规则检查的产物。

### READING_GUIDE（5 条）— 英文判断词

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E228 | `verdictWords` | The three conclusion words | 三个判断词 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 181 页 |
| E229 | `verdictLine` | {label}: {meaning}. | {label}：{meaning}。 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E230 | `provenance` | How the source of evidence is labelled | 证据来源的标注 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba`；中文原句在此前的代码里已有，随该提交移入词表 | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 181 页 |
| E231 | `teams` | Handling team and default handling role | 处理团队与默认处理角色 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba`；中文原句在此前的代码里已有，随该提交移入词表 | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 181 页 |
| E232 | `teamsBody` | The handling team is taken from the staffing in the record; the default handling role is the rule's default, an input to the staffing, not an assignment. The two are shown apart. | 处理团队取自记录里的人员安排；默认处理角色是规则给出的默认，是安排的输入，不是指派。两者分开显示。 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba`；中文原句在此前的代码里已有，随该提交移入词表 | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 181 页 |

页面上下文（`E228` `verdictWords`）：
- en `#/fixture/member-evidence`：An item is the conclusion for one element (or a pair of elements assessed together) on one piece of ‹ The three conclusion words › Ready: Every piece of necessary evidence is present and satisfies the applicable acceptance conditio
- zh `#/fixture/member-evidence`：一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。同一个构件可以出现在几个事项里，所以事项数不是缺陷数。 ‹ 三个判断词 › 可以开始：必要的证据齐全且满足验收条件，没有未解决的阻碍，也没有证据缺口：在本次评估范围内，这项工作可以开始。

页面上下文（`E230` `provenance`）：
- en `#/fixture/member-evidence`：Each conclusion is about one piece of the receiving side's work, this item within this assessment's ‹ How the source of evidence is labelled › Each citation's source label on this page is decided from that citation alone (whether it carries th
- zh `#/fixture/member-evidence`：每个判断只针对接收方的一项工作、本次评估范围内的这一项，以及所列的模型版本；它不是“模型好不好”的总评，也不是“某项检查通过了”。 ‹ 证据来源的标注 › 本页每条引用旁的来源标注按该条引用自身判定（是否带模拟标记），不按整页或整份记录推断：

### READY_NOTES（2 条）— 范围限制

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E233 | `ceiling-and-bulkhead-geometry[0]` | The rule proves only that the element has a storey or space assignment; it does not check that the receiving model has a matching storey. | 规则只证明构件有楼层或空间归属，没有验证接收方模型有对应楼层。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 33 页（fixture/recheck ×19; fixture/result ×6; fixture/item ×6; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×3；zh 33 页 |
| E234 | `ceiling-and-bulkhead-geometry[1]` | This conclusion rests on a confirmation that the two models are aligned, not on a shared positioning marker passing. | 这个结论靠的是两侧模型的对齐确认，不是共享定位标记通过。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 33 页（fixture/recheck ×19; fixture/result ×6; fixture/item ×6; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×3；zh 33 页 |

页面上下文（`E233` `ceiling-and-bulkhead-geometry[0]`）：
- en `#/fixture/member-evidence`：This conclusion rests on simulated evidence:Real check output ×1 Simulated human determination ×1 ‹ The rule proves only that the element has a storey or space assignment; it does not check that the receiving model has a matching storey. › This conclusion rests on a confirmation that the two models are aligned, not on a shared positioning
- zh `#/fixture/member-evidence`：这个结论建立在模拟证据上：真实检查输出 ×1 模拟的人工判定 ×1 ‹ 规则只证明构件有楼层或空间归属，没有验证接收方模型有对应楼层。 › 这个结论靠的是两侧模型的对齐确认，不是共享定位标记通过。

页面上下文（`E234` `ceiling-and-bulkhead-geometry[1]`）：
- en `#/fixture/member-evidence`：The rule proves only that the element has a storey or space assignment; it does not check that the r ‹ This conclusion rests on a confirmation that the two models are aligned, not on a shared positioning marker passing. › chimney cover | Reflected ceiling and bulkhead layout: ReadyThis conclusion rests on simulated evide
- zh `#/fixture/member-evidence`：规则只证明构件有楼层或空间归属，没有验证接收方模型有对应楼层。 ‹ 这个结论靠的是两侧模型的对齐确认，不是共享定位标记通过。 › chimney cover ｜ 吊顶平面与包封布置：可以开始这个结论建立在模拟证据上：真实检查输出 ×1 模拟的人工判定 ×1 规则只证明构件有楼层或空间归属，没有验证接收方模型有对应楼层。这个结论靠

### RECHECK_CANNOT（5 条）— 范围限制

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E275 | `[0]` | Start a new recheck or upload a new model | 发起新的复检或上传新模型 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |
| E276 | `[1]` | Mark an item resolved, closed or risk-accepted | 把事项标记为已解决、关闭或接受风险 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |
| E277 | `[2]` | Assign or notify anyone | 指派或通知责任人 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |
| E278 | `[3]` | Open or locate an element in Revit | 在 Revit 中打开或定位构件 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |
| E279 | `[4]` | Export a recheck record | 导出复检记录 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |

页面上下文（`E275` `[0]`）：
- en `#/fixture/recheck-requirement-relaxed`：What this preview cannot do ‹ Start a new recheck or upload a new model › Mark an item resolved, closed or risk-accepted
- zh `#/fixture/recheck-requirement-relaxed`：本预览做不了的事 ‹ 发起新的复检或上传新模型 › 把事项标记为已解决、关闭或接受风险

页面上下文（`E276` `[1]`）：
- en `#/fixture/recheck-requirement-relaxed`：Start a new recheck or upload a new model ‹ Mark an item resolved, closed or risk-accepted › Assign or notify anyone
- zh `#/fixture/recheck-requirement-relaxed`：发起新的复检或上传新模型 ‹ 把事项标记为已解决、关闭或接受风险 › 指派或通知责任人

### RECHECK_LIMITS（5 条）— 范围限制

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E308 | `[0]` | "Comparison basis unchanged" does not mean the whole handover needs no review. | “比较依据一致”不代表整个交接不用复核。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |
| E309 | `[1]` | An element that is gone, or evidence with no counterpart, does not mean the problem was fixed. | 构件不在了、或找不到对应证据，不代表问题已修复。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |
| E310 | `[2]` | A model re-issued (on either side) does not mean a fix has happened. | 模型重新发布（不论哪一侧）不代表修复已经发生。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |
| E311 | `[3]` | "Only the model version changed" does not mean the check result's content changed. | “只有模型版本变了”不等于检查结果的内容变了。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |
| E312 | `[4]` | "Cannot be compared" is not "evidence missing": where the old record kept no comparison basis, this page says honestly that it cannot compare. | “无法比较”不是“证据缺失”：旧记录没保存比较依据时，本页如实显示无法比较。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |

页面上下文（`E308` `[0]`）：
- en `#/fixture/recheck-requirement-relaxed`：When reading a recheck result ‹ "Comparison basis unchanged" does not mean the whole handover needs no review. › An element that is gone, or evidence with no counterpart, does not mean the problem was fixed.
- zh `#/fixture/recheck-requirement-relaxed`：读复检结果时 ‹ “比较依据一致”不代表整个交接不用复核。 › 构件不在了、或找不到对应证据，不代表问题已修复。

页面上下文（`E309` `[1]`）：
- en `#/fixture/recheck-requirement-relaxed`："Comparison basis unchanged" does not mean the whole handover needs no review. ‹ An element that is gone, or evidence with no counterpart, does not mean the problem was fixed. › A model re-issued (on either side) does not mean a fix has happened.
- zh `#/fixture/recheck-requirement-relaxed`：“比较依据一致”不代表整个交接不用复核。 ‹ 构件不在了、或找不到对应证据，不代表问题已修复。 › 模型重新发布（不论哪一侧）不代表修复已经发生。

### RESOLUTION_KINDS（10 条）— 源修改与复检行动

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E331 | `missing-project-asset-identity` | The project's required asset identity is missing | 缺少本项目约定的资产标识 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 34 页（fixture/recheck ×24; fixture/item ×6; fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 34 页 |
| E332 | `asset-identity-not-evaluated` | Not a known model defect: the existing asset-identity rules did not cover this element | 不是已知的模型缺陷：现有资产标识规则没有覆盖到这个构件 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 16 页（fixture/recheck ×10; fixture/result ×2; fixture/item ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 16 页 |
| E333 | `mep-element-not-spatially-assigned` | It has no storey or space assignment | 它没有楼层或空间归属 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到）；同句（en）：LEAF_READINGS.in-model-position/unmet |
| E334 | `in-model-position-not-evaluated` | Not a known model defect: the storey or space check did not cover it | 不是已知的模型缺陷：楼层或空间归属的检查没有覆盖到它 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 16 页（fixture/recheck ×10; fixture/result ×2; fixture/item ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 16 页 |
| E335 | `cross-model-misalignment` | The two models are not aligned to a common datum | 两侧模型没有对齐到共同的基准 | 界面文字；en #33 `39ae8ba`；zh #21 `542636a` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E336 | `cross-model-alignment-not-confirmed` | Not a known misalignment: nobody has confirmed yet that the two models are aligned | 不是已知的错位：还没有人确认两侧模型对齐 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 14 页（fixture/recheck ×14）；例 `#/fixture/recheck-both-reissued/recheck/5/0`；zh 14 页 |
| E337 | `penetration-not-determined` | Not a known model defect: no coordination review has determined yet whether it passes through the receiving side's elements | 不是已知的模型缺陷：还没有协调评审判定它是否穿过接收方的构件 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 32 页（fixture/recheck ×24; fixture/item ×4; fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 32 页 |
| E338 | `opening-not-verifiably-linked` | The opening is modelled, but not linked to this element that passes through it | 洞口已建，但没有关联到穿过它的这个构件 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E339 | `missing-corresponding-opening` | No corresponding opening is modelled in the element it passes through | 它穿过的构件上没有建出对应的洞口 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 11 页（fixture/recheck ×5; fixture/result ×2; fixture/item ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 11 页 |
| E340 | `opening-status-not-determined` | Not a known missing opening: the review of the opening has not been completed yet | 不是已知的缺洞：开洞情况的评审还没有完成 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E331` `missing-project-asset-identity`）：
- en `#/fixture/member-evidence`：1 item ‹ The project's required asset identity is missing › Room data sheets and equipment schedules: Blocked
- zh `#/fixture/member-evidence`：1 个事项 ‹ 缺少本项目约定的资产标识 › 房间数据表与设备明细表：受阻

页面上下文（`E332` `asset-identity-not-evaluated`）：
- en `#/fixture/member-evidence`：2 items ‹ Not a known model defect: the existing asset-identity rules did not cover this element › Room data sheets and equipment schedules: Unknown
- zh `#/fixture/member-evidence`：2 个事项 ‹ 不是已知的模型缺陷：现有资产标识规则没有覆盖到这个构件 › 房间数据表与设备明细表：无法判断

### RULE_NOTES（18 条）— W6 类型对应说明／PASS 证明什么

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E341 | `PV-001.title` | Air terminals declare one of four predefined types | 风口要声明四种预定义类型之一 | 规则文件 rules/product-validation/PV-001.toml 的 title；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；同页最多 ×2；zh 15 页 |
| E342 | `PV-001.predicate` | Every applicable air terminal (IfcAirTerminal) declares a predefined type of DIFFUSER, GRILLE, LOUVRE or REGISTER. IFC4 also admits USERDEFINED and NOTDEFINED; not accepting them is this rule's own decision, and a model using them is still valid IFC4. | 每个适用的风口（IfcAirTerminal）都要声明预定义类型，取值是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一。IFC4 还允许 USERDEFINED 和 NOTDEFINED；不接受它们是这条规则自己的决定，用它们的模型仍是有效的 IFC4。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 15 页 |
| E343 | `PV-001.passProves` | The one value the checker took in its reading order (the type's value first; a USERDEFINED type's free text; the element instance only when the type says nothing) is, character for character, one of DIFFUSER, GRILLE, LOUVRE and REGISTER. | 检查器按它的读取顺序取到的那一个值（类型上的值优先；类型声明 USERDEFINED 时是它的自由文本；类型什么也没说时才读构件实例），逐字等于 DIFFUSER、GRILLE、LOUVRE、REGISTER 四个值之一。 | 界面文字；en #36 `2934b01`；zh #31 `7227110`；#27／#31 终稿：#31 82aa943; #31 7227110 | en 1 页（ws-compare:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/a52c30cc-6d9f-54e3-9ed1-05cc4da48249`；zh 1 页 |
| E344 | `PV-001.passDoesNotProve[0]` | That the value is right: any of the four passes; GRILLE passes too. | 取值正确：四个值中任何一个都会通过，写成 GRILLE 也会通过。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-compare:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/a52c30cc-6d9f-54e3-9ed1-05cc4da48249`；zh 1 页 |
| E345 | `PV-001.passDoesNotProve[1]` | That the type and the element instance agree: when the type carries one of the four, the instance's value is not compared; type LOUVRE with instance DIFFUSER also passes. | 类型和构件实例的取值一致：类型上是四个值之一时，实例上写的值不参与比较；类型是 LOUVRE、实例是 DIFFUSER，也会通过。 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 1 页（ws-compare:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/a52c30cc-6d9f-54e3-9ed1-05cc4da48249`；zh 1 页 |
| E346 | `PV-001.passDoesNotProve[2]` | That no USERDEFINED, which the rule does not accept, is present: when the type declares USERDEFINED, the checker compares its free text, character for character and case-sensitively; text that happens to be LOUVRE passes, while louvre, Louvre or text with leading or trailing spaces does not. | 规则不接受的 USERDEFINED 没有出现：类型声明 USERDEFINED 时，检查器比较的是它的自由文本，逐字、区分大小写；文本恰好是 LOUVRE 会通过，写成 louvre、Louvre 或前后带空格则不通过。 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#27 70198bb; #27 92d788d; #31 82aa943 | en 1 页（ws-compare:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/a52c30cc-6d9f-54e3-9ed1-05cc4da48249`；zh 1 页 |
| E347 | `PV-001.passDoesNotProve[3]` | That the wall has a corresponding opening. | 墙上有对应的洞口。 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 1 页（ws-compare:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/a52c30cc-6d9f-54e3-9ed1-05cc4da48249`；zh 1 页 |
| E348 | `PV-001.passDoesNotProve[4]` | That the air terminal's model and the model of the wall it sits in are aligned. | 风口所在的模型与风口所在的墙所属的模型已经对齐。 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 1 页（ws-compare:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/a52c30cc-6d9f-54e3-9ed1-05cc4da48249`；zh 1 页 |
| E349 | `PV-001.passDoesNotProve[5]` | That any work can start, including ceiling and opening work. | 任何工作可以开始，包括吊顶和开洞工作。 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 1 页（ws-compare:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/a52c30cc-6d9f-54e3-9ed1-05cc4da48249`；zh 1 页 |
| E350 | `PV-001.action.what` | Go back to the Revit source model and make this air terminal's exported predefined type one of DIFFUSER, GRILLE, LOUVRE and REGISTER; re-export the IFC and check again. NOTDEFINED states nothing. | 回到 Revit 源模型，让这个风口导出后的预定义类型是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一；重新导出 IFC，再检查。NOTDEFINED 等于什么都没说。 | 界面文字（含取自 PV-001.toml instructions 的一句 “NOTDEFINED states nothing.”）；en #36 `2934b01`；zh #27 `70198bb`；#27／#31 终稿：#27 70198bb | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E351 | `PV-001.action.reads` | The checker looks first at its type object in the exported IFC: if the type carries one of the four, the type's value is compared; if the type declares USERDEFINED, its free text is compared; only when the type says nothing is the element instance's own value read. This is the order in which the checker reads the IFC, not where to make the change in Revit. | 检查器先看导出的 IFC 里它的类型对象：类型上是四个值之一，比较类型上的值；类型声明 USERDEFINED，比较它的自由文本；类型什么也没说时，才读构件实例本身的值。这说的是检查器读 IFC 的顺序，不是 Revit 里该改的位置。 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E352 | `PV-001.action.revise` | Where this value is written from in Revit (type or instance, which parameter, which export setting), the returned data does not record, and this page does not say. Confirm it in Revit before changing anything; if you decide to change it on the type, the change applies to every instance of that type. One Revit type may correspond to more than one IFC type object; count instances by the Revit type. | 这个值在 Revit 里从哪里写出（类型还是实例、哪个参数、哪项导出设置），返回数据没有记录，本页不指定。改之前先在 Revit 里确认；如果决定在类型上改，会作用于这个类型的全部实例。一个 Revit 类型可能对应不止一个 IFC 类型对象，实例数按 Revit 类型算。 | 界面文字；en #40 `295da77`；zh #40 `295da77`；#27／#31 终稿：#31 82aa943；**已由 #40 修改，待 BIM 复核（措辞修改）** | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E353 | `PV-001.action.undecided` | Which value to use, and who decides and makes the change, the returned data does not say. The rule asks only for one of the four values and does not judge which is right. | 取哪一个值、由谁决定和操作，返回数据都没有提供。规则只要求四个值之一，不判断哪一个对。 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E354 | `PV-001.recheck` | Check again with the same rule set version, the same set of models and the same export settings, and look at this element's result under this requirement. | 用同一规则集版本、同一组模型和同一导出设置重新检查，看这个构件在这条要求下的结果。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E355 | `PV-001.gaps[0]` | The opening in the wall the air terminal sits in: a coordination-review determination is needed, made against the air terminal's model and the model of that wall; this check does not compare elements across the two models. | 风口所在的墙上的洞口：需要对照风口所在的模型和这面墙所属的模型做协调评审判定；这项检查不比较两个模型的构件。 | 界面文字；en #36 `2934b01`；zh #27 `92d788d`；#27／#31 终稿：#27 70198bb; #27 92d788d | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E356 | `PV-001.gaps[1]` | Whether the air terminal's model and the model of the wall it sits in are aligned: an alignment confirmation record is needed. | 风口所在的模型与风口所在的墙所属的模型是否对齐：需要一份对齐确认记录。 | 界面文字；en #36 `2934b01`；zh #27 `92d788d`；#27／#31 终稿：#27 70198bb; #27 92d788d | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E357 | `PV-001.gaps[2]` | Whether the value chosen is right: the classification decision has to be recorded separately; a pass cannot prove in reverse that the classification is right. | 取值是否选对：分类判断要另行记录；检查通过不能反过来证明分类判断正确。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E358 | `PV-001.reasonFreeText` | What is in the quotation marks is not an enumeration value but free text: when the type declares USERDEFINED, the checker compares its free text. | 引号里不是预定义类型的枚举值，而是自由文本：类型声明 USERDEFINED 时，检查器拿它的自由文本来比较。 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 7 页（ws-compare:workspace/finding ×2; ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；同页最多 ×3；zh 7 页 |

页面上下文（`E341` `PV-001.title`）：
- en `ws-compare:#/workspace/workspace`：What was checked ‹ PV-001 Air terminals declare one of four predefined types › The label in the returned data (ProductValidation) says: this is a product validation rule.
- zh `ws-compare:#/workspace/workspace`：检查了什么 ‹ PV-001 风口要声明四种预定义类型之一 › 返回数据的标签（ProductValidation）标明：这是一条产品验证规则。

页面上下文（`E342` `PV-001.predicate`）：
- en `ws-compare:#/workspace/workspace`：What this rule asks ‹ Every applicable air terminal (IfcAirTerminal) declares a predefined type of DIFFUSER, GRILLE, LOUVRE or REGISTER. IFC4 also admits USERDEFINED and NOTDEFINED; not accepting them is this rule's own decision, and a model using them is still valid IFC4. › Source (the returned data's citation, as written)
- zh `ws-compare:#/workspace/workspace`：这条规则要求 ‹ 每个适用的风口（IfcAirTerminal）都要声明预定义类型，取值是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一。IFC4 还允许 USERDEFINED 和 NOTDEFINED；不接受它们是这条规则自己的决定，用它们的模型仍是有效的 IFC4。 › 出处（返回数据的引文，英文原文）

### TAG_WORDS（14 条）— Tag 不一致后的行动

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E372 | `note` | The IFC Tag is a marker written into the IFC at export; what Revit writes is usually the element's ElementId. To check: in Revit, use "Select by ID" with this ID and see whether the selected object's name and class match this page; if they do, work from it; if they do not, do not change anything by this Tag: use the GlobalId to confirm which object it is, then make the change in the Revit source model. | IFC Tag 是导出时写进 IFC 的标记；Revit 导出的通常是构件的 ElementId。核对：在 Revit 里用“按 ID 选择”选中这个 ID，看选中对象的名称和类别是否与本页相同；相同再按它处理，不同就不要按这个 Tag 去改：用 GlobalId 确认是哪个对象，再回到 Revit 源模型修改。 | 界面文字；en #40 `295da77`；zh #40 `295da77`；#27／#31 终稿：#27 70198bb; #31 82aa943；**已由 #40 修改，待 BIM 复核（措辞修改）** | en 7 页（ws-compare:workspace/finding ×2; ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 7 页 |
| E373 | `byIdNotStorey` | Find the object in Revit by its ID, not by storey: the storey on this page is the IFC file's spatial assignment, which may not match the levels in a Revit schedule. | 在 Revit 里按 ID 找对象，不要按楼层找：本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上。 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 7 页（ws-compare:workspace/finding ×2; ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 7 页 |
| E374 | `storeyFromIfc` | The storey on this page is the IFC file's spatial assignment, which may not match the levels in a Revit schedule; do not look for the object by storey alone. | 本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上，不要只按楼层去找。 | 界面文字；en #36 `2934b01`；zh #31 `7227110`；#27／#31 终稿：#31 7227110 | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E375 | `sources.model-file` | The model file has no Tag for this element. | 模型文件里这个构件没有写 Tag。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E376 | `sources.model-file-not-located` | The model file this check read was not found, so the Tag cannot be read. | 没有找到这次检查读的那个模型文件，所以读不到 Tag。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E377 | `sources.model-file-differs` | The model file in the workspace is no longer the version this check read, so the Tag is not read. | 工作区里的模型文件已经不是这次检查读的那个版本，所以不读取 Tag。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E378 | `sourceNotCarried` | The returned data does not say where this model's Tags are read from, so there is no Tag. | 返回数据没有说明这个模型的 Tag 从哪里读，所以没有 Tag。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E379 | `modelLevel` | This result is about the whole model; there is no single element to find. | 这条结果针对整个模型，没有具体构件可找。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 4 页（ws-compare:workspace/finding ×1; ws-newly:workspace/finding ×1; ws-notreeval:workspace/finding ×1; ws-single:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/3ea38c47-b628-5ce1-82eb-7e524cab69f5`；zh 4 页 |
| E380 | `useGlobalId` | To find it in the IFC, use the GlobalId. | 在 IFC 里定位用 GlobalId。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 7 页（ws-compare:workspace/finding ×2; ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 7 页 |
| E381 | `short.model-file` | No Tag in the file | 文件里没有 Tag | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E382 | `short.model-file-not-located` | Model file not found | 未找到模型文件 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E383 | `short.model-file-differs` | Model file version differs | 模型文件版本不同 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-notreeval:workspace/compare ×1）；例 `ws-notreeval:#/workspace/workspace/compare`；zh 1 页 |
| E384 | `short.notCarried` | Source not stated | 来源未说明 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E385 | `short.modelLevel` | Whole model | 整个模型 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 18 页 |

页面上下文（`E372` `note`）：
- en `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`：34Y6EIt3nDCAS1k$kPGOKmCopy ‹ The IFC Tag is a marker written into the IFC at export; what Revit writes is usually the element's ElementId. To check: in Revit, use "Select by ID" with this ID and see whether the selected object's name and class match this page; if they do, work from it; if they do not, do not change anything by this Tag: use the GlobalId to confirm which object it is, th › Find the object in Revit by its ID, not by storey: the storey on this page is the IFC file's spatial
- zh `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`：34Y6EIt3nDCAS1k$kPGOKm复制 ‹ IFC Tag 是导出时写进 IFC 的标记；Revit 导出的通常是构件的 ElementId。核对：在 Revit 里用“按 ID 选择”选中这个 ID，看选中对象的名称和类别是否与本页相同；相同再按它处理，不同就不要按这个 Tag 去改：用 GlobalId 确认是哪个对象，再回到 Revit 源模型修改。 › 在 Revit 里按 ID 找对象，不要按楼层找：本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上。

页面上下文（`E373` `byIdNotStorey`）：
- en `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`：The IFC Tag is a marker written into the IFC at export; what Revit writes is usually the element's E ‹ Find the object in Revit by its ID, not by storey: the storey on this page is the IFC file's spatial assignment, which may not match the levels in a Revit schedule. › To find it in the IFC, use the GlobalId.
- zh `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`：IFC Tag 是导出时写进 IFC 的标记；Revit 导出的通常是构件的 ElementId。核对：在 Revit 里用“按 ID 选择”选中这个 ID，看选中对象的名称和类别是否与本页相同；相同 ‹ 在 Revit 里按 ID 找对象，不要按楼层找：本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上。 › 在 IFC 里定位用 GlobalId。

### VERDICT_GROUPS（11 条）— 英文判断词

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E386 | `changed.label` | Conclusions that changed | 判断变了的 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E387 | `changed.none` | No conclusion changed. | 没有判断变了的项。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 8 页（fixture/result ×4; fixture/recheck ×4）；例 `#/fixture/recheck-comparison`；zh 8 页 |
| E388 | `changed.notes.none` | Neither model was re-issued, yet these conclusions changed: the change does not come from a model edit. Each item's old evidence says what changed. | 两侧模型都没有重新发布，这些项的判断却变了：变化不来自模型改动。每一项的旧证据写明变了的是什么。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 4 页（fixture/recheck ×3; fixture/result ×1）；例 `#/fixture/recheck-requirement-relaxed`；zh 4 页 |
| E389 | `changed.notes.reissued` | A model was re-issued. A changed conclusion does not say what became of the original problem; each item's old evidence says what changed. | 模型重新发布过。判断变了，不说明原来的问题怎样了；每一项的旧证据写明变了的是什么。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 31 页（fixture/recheck ×26; fixture/result ×5）；例 `#/fixture/recheck-both-reissued`；zh 31 页 |
| E390 | `changed.notes.unrecognised` | A changed conclusion does not say what became of the original problem; each item's old evidence says what changed. | 判断变了，不说明原来的问题怎样了；每一项的旧证据写明变了的是什么。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 31 页（fixture/recheck ×26; fixture/result ×5）；例 `#/fixture/recheck-both-reissued`；zh 31 页 |
| E391 | `unplaced.label` | Items whose current place the record does not give | 记录没有给出当前情况的 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E392 | `unplaced.none` | The record gives a current place for every item. | 每一项记录都给出了当前情况。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E393 | `unplaced.note` | The record does not say what these items' conclusions are now. An element that is gone does not mean the problem was fixed. | 这些项现在是什么判断，记录没有说。构件不在了不代表问题已修复。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 12 页（fixture/result ×6; fixture/recheck ×6）；例 `#/fixture/recheck-both-reissued`；zh 0 页（未渲染到）；同句（en）：ACTION_GROUPS.unplaced.note |
| E394 | `unchanged.label` | Conclusions that did not change | 判断没有变的 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E395 | `unchanged.none` | No conclusion stayed the same. | 没有判断保持不变的项。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E396 | `unchanged.note` | An unchanged conclusion does not mean the evidence is unchanged; see each item for the old evidence. | 判断没有变，不代表证据没有变；旧证据的情况见每一项。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E387` `changed.none`）：
- en `#/fixture/recheck-comparison`：Models: Neither model was re-issued (versions unchanged). ‹ No conclusion changed. › Items to deal with (0 items)
- zh `#/fixture/recheck-comparison`：模型：两侧模型都没有重新发布（版本未变）。 ‹ 没有判断变了的项。 › 需要处理的事项（0 个事项）

页面上下文（`E388` `changed.notes.none`）：
- en `#/fixture/recheck-requirement-relaxed`：building element | Room data sheets and equipment schedules: before the recheck Blocked → now Ready ‹ Neither model was re-issued, yet these conclusions changed: the change does not come from a model edit. Each item's old evidence says what changed. › Of the old evidence cited before the recheck (15 in all), the check requirement changed for 2.
- zh `#/fixture/recheck-requirement-relaxed`：building element ｜ 房间数据表与设备明细表：复检前 受阻 → 现在 可以开始 同组事项共用的依据，其中有模拟证据：模拟的检查结果 ×2 只对这一个事项、这项工作、所列的模型版本成立； ‹ 两侧模型都没有重新发布，这些项的判断却变了：变化不来自模型改动。每一项的旧证据写明变了的是什么。 › 复检前引用的 15 条旧证据里，有 2 条的检查要求变了。

### VERDICT_SCOPE（1 条）— 范围限制

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E397 | `(整表)` | Each conclusion is about one piece of the receiving side's work, this item within this assessment's scope, and the listed model versions; it is not an overall verdict on whether the model is good, nor a statement that some check passed. | 每个判断只针对接收方的一项工作、本次评估范围内的这一项，以及所列的模型版本；它不是“模型好不好”的总评，也不是“某项检查通过了”。 | 界面文字；en #33 `39ae8ba`；zh #21 `542636a` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 181 页 |

页面上下文（`E397` ``）：
- en `#/fixture/member-evidence`：Unknown: An evidence gap makes the activity undecidable — the evidence needed to answer the question ‹ Each conclusion is about one piece of the receiving side's work, this item within this assessment's scope, and the listed model versions; it is not an overall verdict on whether the model is good, nor a statement that some check passed. › How the source of evidence is labelled
- zh `#/fixture/member-evidence`：无法判断：回答这个问题所需的证据没有产生，这项工作能否开始无法决定：既不能放行，也不能拒绝。 ‹ 每个判断只针对接收方的一项工作、本次评估范围内的这一项，以及所列的模型版本；它不是“模型好不好”的总评，也不是“某项检查通过了”。 › 证据来源的标注

### WORKSPACE（80 条）— PASS／FAIL／N/A／拒绝区别（C2 工作区结果页）

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E398 | `directoryNote` | A workspace can only be named when the server is started; you cannot choose, upload or change a model here. | 工作区只能在启动服务器时指定；这里不能选择、上传或更换模型。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 5 页（ws-compare:workspace/result ×1; ws-newly:workspace/result ×1; ws-notreeval:workspace/result ×1; ws-refusal:workspace/result ×1; ws-single:workspace/result ×1）；例 `ws-compare:#/workspace`；zh 5 页 |
| E399 | `directoryNone` | The server was started without a workspace, so there is no check to look at here. To look at one, restart the server with this command: | 服务器启动时没有指定工作区，所以这里没有可以查看的检查。要查看，用下面的命令重新启动服务器： | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E400 | `startCommand` | python doctor/serve.py --workspace <workspace directory> [--prior <earlier run directory>] | python doctor/serve.py --workspace <工作区目录> [--prior <前一次运行的目录>] | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E401 | `openRun` | Open this check's results | 打开这次检查的结果 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 5 页（ws-compare:workspace/result ×1; ws-newly:workspace/result ×1; ws-notreeval:workspace/result ×1; ws-refusal:workspace/result ×1; ws-single:workspace/result ×1）；例 `ws-compare:#/workspace`；zh 5 页 |
| E402 | `back` | ← Back to the home page | ← 返回首页 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 20 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-compare:workspace/result ×2; ws-newly:workspace/result ×2; ws-notreeval:workspace/result ×2）；例 `ws-compare:#/workspace`；zh 20 页 |
| E403 | `backToList` | ← Back to the list of results | ← 返回结果列表 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E404 | `contextNoJudgement` | Check results only, no handover judgement | 只有检查结果，没有交接判断 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 5 页；同句（en）：CONTEXT.noJudgement |
| E405 | `contextRun` | Check run | 检查运行 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E406 | `resultTitle` | Results of a real check | 一次真实检查的结果 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 15 页 |
| E407 | `noJudgement` | These are the results of a check, not a handover judgement: the page says only whether each element passed, failed or was not applicable under each requirement, and concludes nothing about whether any work can start. | 这是一次检查的结果，不是交接判断：页面只说每个构件在每条要求下通过、不通过还是不适用，不对任何工作能否开始下结论。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 18 页 |
| E408 | `summary.one` | This result: {count} check result | 本次结果：共 {count} 条检查结果 | 界面文字；en #36 `2934b01`；zh #36 `2934b01`；中文是该提交新写的 | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E409 | `summary.other` | This result: {count} check results | 本次结果：共 {count} 条检查结果 | 界面文字；en #36 `2934b01`；zh #36 `2934b01`；中文是该提交新写的 | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E410 | `unit` | The unit is one result: one element under one requirement; where a model has no element the requirement applies to, it is one result for the whole model. | 单位是条：一条是一个构件在一条要求下的结果；模型里没有这条要求适用的构件时，是整个模型的一条。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 15 页 |
| E411 | `compareLink` | See the comparison with the earlier run | 看与前一次运行的对比 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1; ws-notreeval:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；同页最多 ×2；zh 11 页 |
| E412 | `compareTeaser` | The server was also started with an earlier run. Before and after: | 服务器启动时还指定了前一次运行。两次结果的前后对比： | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1; ws-notreeval:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 11 页 |
| E413 | `checkedHeading` | What was checked | 检查了什么 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 15 页 |
| E414 | `ruleTitle` | Requirement | 要求 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 30 页（fixture/recheck ×30）；例 `#/fixture/recheck-requirement-relaxed/recheck/5/0`；zh 30 页 |
| E415 | `rulePredicate` | What this rule asks | 这条规则要求 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 15 页 |
| E416 | `ruleExpected` | The rule's own words | 规则的原话（英文） | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 77 页（fixture/recheck ×60; fixture/item ×6; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `#/fixture/member-evidence/item/2/2/0`；同页最多 ×6；zh 77 页；同句（en）：DETAILS_WORDS.expected |
| E417 | `ruleOrigin` | Source (the returned data's citation, as written) | 出处（返回数据的引文，英文原文） | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 15 页 |
| E418 | `ruleLabels` | Labels in the returned data | 返回数据的标签 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 15 页 |
| E419 | `productValidation` | The label in the returned data (ProductValidation) says: this is a product validation rule. | 返回数据的标签（ProductValidation）标明：这是一条产品验证规则。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 15 页 |
| E420 | `noRuleNotes` | This interface has written no notes for this rule; the rule's own words in the returned data are what counts. | 本界面没有为这条规则写中文说明；规则以返回数据里的英文原话为准。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E421 | `noRequirement` | The returned data has no description of the requirement this result belongs to. | 返回数据没有这条结果所属要求的说明。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E422 | `listHeading` | Results, one by one | 逐条结果 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 15 页 |
| E423 | `filterLabel` | Find by IFC Tag, name or GlobalId | 按 IFC Tag、名称或 GlobalId 查找 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 15 页 |
| E424 | `filterAll` | All | 全部 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E425 | `filterNone` | No result matches the filter. | 没有符合筛选条件的结果。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 15 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 15 页 |
| E426 | `filterShown` | Showing {shown} of {count} | 显示 {shown} 条，共 {count} 条 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E427 | `columns.status` | Result | 结果 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 18 页 |
| E428 | `columns.tag` | IFC Tag | IFC Tag | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 18 页 |
| E429 | `columns.name` | Name | 名称 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 158 页 |
| E430 | `columns.class` | Class | 类别 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 175 页（fixture/recheck ×131; fixture/item ×26; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `#/fixture/member-evidence/item/0/2/0`；zh 175 页 |
| E431 | `columns.storey` | Storey (IFC) | 楼层（IFC） | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；同页最多 ×3；zh 18 页；同句（en）：WORKSPACE.element.storey |
| E432 | `columns.model` | Model | 模型 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 195 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×10; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3）；例 `#/fixture/recheck-requirement-relaxed`；zh 328 页 |
| E433 | `pickOne` | Choose a result from the list to see its details here. | 从结果列表里选一条，在这里看它的详情。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 4 页（ws-compare:workspace/result ×1; ws-newly:workspace/result ×1; ws-notreeval:workspace/result ×1; ws-single:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 4 页 |
| E434 | `detailKicker` | One result of a real check | 一条真实检查结果 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 11 页 |
| E435 | `wholeModel` | Whole model | 整个模型 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 18 页 |
| E436 | `resultHeading` | Result | 结果 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 18 页 |
| E437 | `findHeading` | Which object to find in Revit | 回到 Revit 找哪个对象 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 11 页 |
| E438 | `actionHeading` | What to change | 要改什么 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E439 | `actionWhat` | Change it to | 改成什么 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E440 | `actionReads` | Where the checker reads | 检查器读哪里 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E441 | `actionRevise` | Where to change it in Revit | 在 Revit 里改哪里 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E442 | `actionUndecided` | Not decided yet | 还没有决定的 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E443 | `requirementHeading` | The requirement, and what this check observed | 具体要求与这次检查的观察 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 11 页 |
| E444 | `reason` | Reason (as the check result gives it) | 原因（检查结果的原文） | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 11 页 |
| E445 | `actual` | Observed value | 观察值一栏 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 11 页 |
| E446 | `actualEmpty` | Empty in the check result. | 检查结果中为空。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 11 页 |
| E447 | `actualHidden` | The check result carries an observed value; this page does not show it. | 检查结果带有观察值；本页不显示取值。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E448 | `recheckHeading` | What to look at in a recheck | 复检时看什么 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E449 | `passHeading` | What this pass proves | 这条通过证明了什么 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-compare:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/a52c30cc-6d9f-54e3-9ed1-05cc4da48249`；zh 1 页 |
| E450 | `passProves` | It proves:  | 它证明： | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E451 | `passDoesNotProve` | It does not prove: | 它不证明： | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-compare:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/a52c30cc-6d9f-54e3-9ed1-05cc4da48249`；zh 1 页 |
| E452 | `passNoValue` | A passing check result does not carry the value it read: it records only "Requirement satisfied." | 通过的检查结果不带它读到的值：只记录了“要求已满足”。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-compare:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/a52c30cc-6d9f-54e3-9ed1-05cc4da48249`；zh 1 页 |
| E453 | `passUnwritten` | A pass says only that this requirement was judged met; how far that goes, this interface has written no notes for this rule — see the rule's own words. | 通过只说明这条要求被判为满足；它能证明到哪里，本界面没有为这条规则写说明，请看规则原话。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E454 | `notApplicable` | Not applicable: this model has no element the requirement applies to. Not applicable is not a pass. | 不适用：这个模型里没有这条要求适用的构件。不适用不是通过。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 4 页（ws-compare:workspace/finding ×1; ws-newly:workspace/finding ×1; ws-notreeval:workspace/finding ×1; ws-single:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/3ea38c47-b628-5ce1-82eb-7e524cab69f5`；zh 4 页 |
| E455 | `failNotDefect` | Not meeting this product validation rule is not a delivery defect of the original project. Where this rule comes from is what the returned data's label (ProductValidation) and the citation as written say. | 不满足这条产品验证规则，不等于原项目的交付缺陷。这条规则的来源以返回数据的标签（ProductValidation）和出处原文为准。 | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 6 页（ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-compare:workspace/finding ×1; ws-notreeval:workspace/finding ×1）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 6 页 |
| E456 | `noFinding` | This check has no such result. | 这次检查里没有这一条结果。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E457 | `identityHeading` | Tracing: this check's run identifier, rule set version and model files | 追溯信息：这次检查的运行号、规则集版本与模型文件 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 18 页 |
| E458 | `findingTrace` | Tracing: this result's internal keys | 追溯信息：这条结果的内部键 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 11 页 |
| E459 | `identity.run` | Check run identifier | 检查运行号 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；同页最多 ×2；zh 18 页 |
| E460 | `identity.ruleset` | Rule set | 规则集 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 30 页 |
| E461 | `identity.asOf` | Logical date (given by the run configuration, not when it ran) | 逻辑日期（运行配置给定，不是运行的时间） | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；同页最多 ×2；zh 18 页 |
| E462 | `identity.checkers` | Checkers | 检查程序 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 38 页 |
| E463 | `identity.models` | Models | 模型 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 169 页（fixture/recheck ×141; fixture/result ×10; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `#/fixture/recheck-requirement-relaxed`；zh 328 页 |
| E464 | `identity.modelId` | Model | 模型 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 195 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×10; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3）；例 `#/fixture/recheck-requirement-relaxed`；zh 328 页 |
| E465 | `identity.declaredDiscipline` | Discipline declared in the project manifest | 项目清单声明的专业 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；同页最多 ×2；zh 18 页 |
| E466 | `identity.filename` | File | 文件 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 18 页 |
| E467 | `identity.digest` | File content digest (SHA-256) | 文件内容摘要（SHA-256） | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；同页最多 ×3；zh 18 页 |
| E468 | `identity.tagSource` | Where the IFC Tag comes from | IFC Tag 的来源 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；同页最多 ×2；zh 18 页 |
| E469 | `identity.elementKey` | Internal key for tracing | 追溯用内部键 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 168 页（fixture/recheck ×131; fixture/item ×26; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `#/fixture/member-evidence/item/0/2/0`；同页最多 ×2；zh 168 页；同句（en）：ELEMENT_CARD.traceKey |
| E470 | `identity.findingKey` | Check result key | 检查结果键 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 11 页 |
| E471 | `identity.requirementKey` | Requirement key | 要求键 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 11 页 |
| E472 | `element.name` | Name | 名称 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；zh 158 页 |
| E473 | `element.class` | Class | 类别 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 175 页（fixture/recheck ×131; fixture/item ×26; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `#/fixture/member-evidence/item/0/2/0`；zh 175 页 |
| E474 | `element.storey` | Storey (IFC) | 楼层（IFC） | 界面文字；en #36 `2934b01`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 18 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace`；同页最多 ×3；zh 18 页；同句（en）：WORKSPACE.columns.storey |
| E475 | `element.model` | Model | 所属模型 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 195 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×10; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3）；例 `#/fixture/recheck-requirement-relaxed`；zh 168 页 |
| E476 | `element.file` | Model file | 模型文件 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 11 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 11 页 |
| E477 | `element.globalId` | GlobalId | GlobalId | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 164 页（fixture/recheck ×131; fixture/item ×26; ws-compare:workspace/finding ×2; ws-newly:workspace/finding ×2; ws-single:workspace/finding ×2; ws-notreeval:workspace/finding ×1）；例 `#/fixture/member-evidence/item/0/2/0`；zh 311 页 |

页面上下文（`E398` `directoryNote`）：
- en `ws-compare:#/workspace`：Real check in a workspace ‹ A workspace can only be named when the server is started; you cannot choose, upload or change a model here. › Open this check's results
- zh `ws-compare:#/workspace`：工作区里的真实检查 ‹ 工作区只能在启动服务器时指定；这里不能选择、上传或更换模型。 › 打开这次检查的结果

页面上下文（`E401` `openRun`）：
- en `ws-compare:#/workspace`：A workspace can only be named when the server is started; you cannot choose, upload or change a mode ‹ Open this check's results ›
- zh `ws-compare:#/workspace`：工作区只能在启动服务器时指定；这里不能选择、上传或更换模型。 ‹ 打开这次检查的结果 ›

### WORKSPACE_REFUSAL（11 条）— PASS／FAIL／N/A／拒绝区别（拒绝页）

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E530 | `title` | These two runs cannot be compared | 这两次运行不能对比 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E531 | `lede` | The system refused this comparison and listed every reason. This is an answer about the request's conditions — not a program fault and not a check result: neither side's results were returned. | 系统拒绝了这次对比，并列出了全部原因。这是对请求条件的答复，不是程序故障，也不是检查结果：任何一侧的检查结果都没有返回。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E532 | `reasonsHeading` | Why they cannot be compared | 为什么不能对比 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E533 | `actionHeading` | What a comparison needs | 要能对比，需要什么 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E534 | `action[0]` | Both runs must use the same rule set (the same version and content), the same set of requirements, the same checkers, the same logical date and the same set of models; between the runs only the content of the model files may differ. | 两次运行要用同一规则集（同一版本、同一内容）、同一组要求、同一检查程序、同一逻辑日期和同一组模型；两次之间只能是模型文件的内容不同。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E535 | `action[1]` | Make sure the run given with --prior at start-up really is the earlier run of the same check; or restart the server without --prior and look at this check's results alone. | 确认启动时用 --prior 指定的确实是同一项检查的前一次运行；或者去掉 --prior 重新启动服务器，只看本次检查的结果。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E536 | `scope` | Whether they can be compared once these reasons are dealt with is for the next answer to say. | 处理这些原因之后能否对比，以下一次返回为准。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E537 | `original` | What the system returned (as written) and the refusal code | 系统返回的原文（英文）与拒绝码 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 2 页 |
| E538 | `code` | Refusal code | 拒绝码 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 2 页 |
| E539 | `unglossed` | This interface has no English for this reason; see what the system returned below. | 本界面没有这个原因的中文说明，见下面的原文。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E540 | `noResult` | No result, no zero-problem count and no completion ratio: a refused comparison is not a check without problems. | 没有任何结果、零问题统计或完成比例：被拒绝不是一次没有问题的检查。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |

页面上下文（`E530` `title`）：
- en `ws-refusal:#/workspace/workspace`：‹ These two runs cannot be compared › The system refused this comparison and listed every reason. This is an answer about the request's co
- zh `ws-refusal:#/workspace/workspace`：‹ 这两次运行不能对比 › 系统拒绝了这次对比，并列出了全部原因。这是对请求条件的答复，不是程序故障，也不是检查结果：任何一侧的检查结果都没有返回。

页面上下文（`E531` `lede`）：
- en `ws-refusal:#/workspace/workspace`：These two runs cannot be compared ‹ The system refused this comparison and listed every reason. This is an answer about the request's conditions — not a program fault and not a check result: neither side's results were returned. › Why they cannot be compared
- zh `ws-refusal:#/workspace/workspace`：这两次运行不能对比 ‹ 系统拒绝了这次对比，并列出了全部原因。这是对请求条件的答复，不是程序故障，也不是检查结果：任何一侧的检查结果都没有返回。 › 为什么不能对比

### WORKSPACE_REFUSAL_REASONS（9 条）— PASS／FAIL／N/A／拒绝区别（拒绝原因）

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E541 | `ruleset-id-differs` | The two runs did not use the same rule set. | 两次用的不是同一个规则集。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E542 | `ruleset-version-differs` | The two runs used different rule set versions. | 两次用的规则集版本不同。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E543 | `ruleset-digest-differs` | The two runs used different rule set content (the content digests differ). | 两次用的规则集内容不同（内容摘要不同）。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E544 | `requirement-set-differs` | The two runs did not evaluate the same set of requirements. | 两次评估的不是同一组要求。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E545 | `requirement-semantics-not-recorded` | One run did not record the predicate digest of a requirement, so it cannot be shown that both are the same check. | 有一次运行没有记录某条要求的谓词摘要，无法证明两次是同一个检查。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E546 | `requirement-semantics-differs` | The same requirement has a different predicate in the two runs: what is checked was changed. | 同一条要求，两次的谓词不同：检查的内容改过。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E547 | `checker-differs` | The two runs used different checkers, versions or configuration. | 两次的检查程序、版本或配置不同。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-refusal:workspace/result ×1）；例 `ws-refusal:#/workspace/workspace`；zh 1 页 |
| E548 | `as-of-differs` | The two runs have different logical dates. | 两次运行的逻辑日期不同。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E549 | `model-set-differs` | The two runs did not check the same set of models. | 两次检查的不是同一组模型。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E541` `ruleset-id-differs`）：
- en `ws-refusal:#/workspace/workspace`：Why they cannot be compared ‹ The two runs did not use the same rule set. ruleset-id-differs › The two runs used different rule set versions. ruleset-version-differs
- zh `ws-refusal:#/workspace/workspace`：为什么不能对比 ‹ 两次用的不是同一个规则集。 ruleset-id-differs › 两次用的规则集版本不同。 ruleset-version-differs

页面上下文（`E542` `ruleset-version-differs`）：
- en `ws-refusal:#/workspace/workspace`：The two runs did not use the same rule set. ruleset-id-differs ‹ The two runs used different rule set versions. ruleset-version-differs › The two runs used different rule set content (the content digests differ). ruleset-digest-differs
- zh `ws-refusal:#/workspace/workspace`：两次用的不是同一个规则集。 ruleset-id-differs ‹ 两次用的规则集版本不同。 ruleset-version-differs › 两次用的规则集内容不同（内容摘要不同）。 ruleset-digest-differs

### LEAF_READINGS（16 条）— 主路径：结论所依据的结果

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E204 | `asset-identity/satisfied` | The project asset-identity requirements that apply to it passed, and it was actually evaluated | 适用于它的项目资产标识要求评为通过，并且它确实被评估到 | 界面文字；en #34 `50d129b`；zh #21 `542636a` | en 5 页（fixture/recheck ×5）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 5 页 |
| E205 | `asset-identity/unmet` | The project asset-identity requirement is not met | 项目资产标识的要求没有满足 | 界面文字；en #34 `50d129b`；zh #21 `542636a` | en 30 页（fixture/recheck ×24; fixture/item ×6）；例 `#/fixture/member-evidence/item/2/2/0`；zh 30 页 |
| E206 | `asset-identity/not-yet-evaluated` | The asset-identity rules did not cover it | 资产标识的规则没有覆盖到它 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 12 页（fixture/recheck ×10; fixture/item ×2）；例 `#/fixture/member-evidence/item/2/1/0`；zh 12 页 |
| E207 | `in-model-position/satisfied` | It has a storey or space assignment | 它有楼层或空间归属 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E208 | `in-model-position/unmet` | It has no storey or space assignment | 它没有楼层或空间归属 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到）；同句（en）：RESOLUTION_KINDS.mep-element-not-spatially-assigned |
| E209 | `in-model-position/not-yet-evaluated` | The storey or space check did not cover it | 楼层或空间归属的检查没有覆盖到它 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 12 页（fixture/recheck ×10; fixture/item ×2）；例 `#/fixture/member-evidence/item/1/1/0`；zh 16 页 |
| E210 | `cross-model-alignment/confirmed` | A record confirms the two models are aligned to a common datum (by the method the project accepts, for the listed model versions) | 已有记录确认两侧模型对齐到共同的基准（按项目接受的方法，针对所列模型版本） | 界面文字；en #34 `50d129b`；zh #21 `542636a` | en 21 页（fixture/recheck ×15; fixture/item ×6）；例 `#/fixture/member-evidence/item/1/2/0`；zh 21 页 |
| E211 | `cross-model-alignment/misaligned` | The alignment confirmation found the two models not aligned | 对齐确认的结果是两侧模型没有对齐 | 界面文字；en #34 `50d129b`；zh #21 `542636a` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E212 | `cross-model-alignment/not-yet-confirmed` | No alignment confirmation yet | 还没有对齐确认 | 界面文字；en #34 `50d129b`；zh #21 `542636a` | en 14 页（fixture/recheck ×14）；例 `#/fixture/recheck-both-reissued/recheck/5/0`；zh 14 页 |
| E213 | `penetration-determination/no-penetration` | A coordination-review determination says it passes through no element of the receiving model. With no penetration no opening is needed, so the opening was not assessed — this is not "the opening is fine" | 已有协调评审判定：它不穿过接收方模型里的任何构件。不穿过就不需要开洞，所以开洞情况没有被评估——这不是“开洞没问题” | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 7 页（fixture/recheck ×5; fixture/item ×2）；例 `#/fixture/member-evidence/item/0/1/0`；zh 7 页 |
| E214 | `penetration-determination/penetration-confirmed` | A coordination-review determination says it passes through elements of the receiving model | 已有协调评审判定：它穿过接收方模型里的构件 | 界面文字；en #34 `50d129b`；zh #21 `542636a` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E215 | `penetration-determination/not-yet-determined` | No coordination review has determined yet whether it passes through elements of the receiving model | 还没有协调评审判定它是否穿过接收方模型里的构件 | 界面文字；en #34 `50d129b`；zh #21 `542636a` | en 28 页（fixture/recheck ×24; fixture/item ×4）；例 `#/fixture/member-evidence/item/0/2/0`；zh 28 页 |
| E216 | `opening-status/cross-referenced` | This pair: the opening is modelled in the element passed through, and linked to the element passing through it | 这一对：洞口已建在被穿过的构件上，并且已关联到穿过它的这个构件 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 7 页（fixture/recheck ×5; fixture/item ×2）；例 `#/fixture/member-evidence/item/0/3/0`；zh 7 页 |
| E217 | `opening-status/modelled-not-cross-referenced` | This pair: the opening is modelled in the element passed through, but not linked to the element passing through it | 这一对：洞口已建在被穿过的构件上，但没有关联到穿过它的这个构件 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E218 | `opening-status/not-modelled` | This pair: no opening is modelled in the element passed through | 这一对：被穿过的构件上没有建出洞口 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 7 页（fixture/recheck ×5; fixture/item ×2）；例 `#/fixture/member-evidence/item/0/4/0`；zh 7 页 |
| E219 | `opening-status/not-yet-determined` | This pair: the review of the opening has not been completed yet | 这一对：开洞情况的评审还没有完成 | 界面文字；en #34 `50d129b`；zh #21 `542636a` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E204` `asset-identity/satisfied`）：
- en `#/fixture/recheck-requirement-relaxed/recheck/7/2`：The result this conclusion rests on ‹ The project asset-identity requirements that apply to it passed, and it was actually evaluated › Models
- zh `#/fixture/recheck-requirement-relaxed/recheck/7/2`：这个结论依据的结果 ‹ 适用于它的项目资产标识要求评为通过，并且它确实被评估到 › 模型

页面上下文（`E205` `asset-identity/unmet`）：
- en `#/fixture/member-evidence/item/2/2/0`：The result this conclusion rests on ‹ The project asset-identity requirement is not met › What this work needs
- zh `#/fixture/member-evidence/item/2/2/0`：这个结论依据的结果 ‹ 项目资产标识的要求没有满足 › 这项工作需要什么

### LEAF_READING_WORDS（3 条）— 主路径：结论所依据的结果

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E220 | `label` | The result this conclusion rests on | 这个结论依据的结果 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 157 页（fixture/recheck ×131; fixture/item ×26）；例 `#/fixture/member-evidence/item/0/2/0`；zh 157 页 |
| E221 | `notCarried` | The record does not give the result this item now rests on | 记录没有给出这一项现在依据的结果 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 14 页（fixture/recheck ×14）；例 `#/fixture/recheck-both-reissued/recheck/2/0`；zh 14 页 |
| E222 | `unglossed` | This interface has no English for this result; see the tracing details | 本界面没有这个结果的中文说明，见追溯信息 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E220` `label`）：
- en `#/fixture/member-evidence/item/0/2/0`：Not a known model defect: no coordination review has determined yet whether it passes through the re ‹ The result this conclusion rests on › No coordination review has determined yet whether it passes through elements of the receiving model
- zh `#/fixture/member-evidence/item/0/2/0`：不是已知的模型缺陷：还没有协调评审判定它是否穿过接收方的构件 ‹ 这个结论依据的结果 › 还没有协调评审判定它是否穿过接收方模型里的构件

页面上下文（`E221` `notCarried`）：
- en `#/fixture/recheck-both-reissued/recheck/2/0`：The result this conclusion rests on ‹ The record does not give the result this item now rests on › This item now
- zh `#/fixture/recheck-both-reissued/recheck/2/0`：这个结论依据的结果 ‹ 记录没有给出这一项现在依据的结果 › 这个事项现在

### RECHECK_ITEM（28 条）— 复检单项页（含复检前的结束条件）

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E280 | `missing` | The recheck record has no such item | 复检记录中没有这一项 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E281 | `back` | ← Back to the recheck items (to this item's place) | ← 返回复检事项列表（回到这一项的位置） | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 131 页（fixture/recheck ×131）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；同页最多 ×2；zh 131 页 |
| E282 | `kicker` | Recheck item · {count} | 复检事项 · {count} | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 131 页（fixture/recheck ×131）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E283 | `pairNote` | These two elements are no longer paired for checking: the penetration determination is now "no penetration" (see the reason the record gives below). This does not mean the opening has been built, nor that the opening defect has been fixed. | 这两个构件已不再被配成一对检查：穿透判定现为“不穿透”（见下方记录给出的原因）。这不等于开洞已建成，也不等于开洞缺陷已修复。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 11 页（fixture/recheck ×11）；例 `#/fixture/recheck-both-reissued/recheck/2/0`；zh 11 页 |
| E284 | `model` | Models | 模型 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 169 页（fixture/recheck ×141; fixture/result ×10; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `#/fixture/recheck-requirement-relaxed`；zh 328 页 |
| E285 | `whichOne` | 2. Which element | 二、是哪个构件 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 110 页（fixture/recheck ×110）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 110 页 |
| E286 | `whichTwo` | 2. Which two elements | 二、是哪两个构件 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 21 页（fixture/recheck ×21）；例 `#/fixture/recheck-requirement-relaxed/recheck/3/0`；zh 21 页 |
| E287 | `actionHeading` | 3. What to do, who deals with it, what a recheck must show | 三、要做什么、由谁处理、完成后拿什么复检 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 131 页（fixture/recheck ×131）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 131 页 |
| E288 | `noCurrent` | The record does not give this item's current place, so this page has no action, handling team or default handling role to show. Those details from the record before the recheck did not come back with the recheck record either. | 记录没有给出这一项的当前情况，所以本页没有处理动作、处理团队或默认处理角色可以显示。复检前记录里的这些信息也没有随复检记录返回。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 14 页（fixture/recheck ×14）；例 `#/fixture/recheck-both-reissued/recheck/2/0`；zh 14 页 |
| E289 | `conditionHeading` | 4. Was the exit condition left before the recheck reached this time? | 四、复检前留下的结束条件，这次达到了吗 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 131 页（fixture/recheck ×131）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 131 页 |
| E290 | `priorCondition` | The exit condition left before the recheck: {text} | 复检前留下的结束条件：{text}。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 81 页（fixture/recheck ×81）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 81 页 |
| E291 | `end` | . | 。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E292 | `conditionNote` | This says only how far the exit condition left before the recheck has been shown to be reached; read it apart from the conclusion now. A changed conclusion does not mean the original condition is met. | 这里只说复检前留下的结束条件被证明到了什么程度，与现在的结论分开读：结论变了，不等于原条件已满足。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 131 页（fixture/recheck ×131）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 131 页 |
| E293 | `originalSummary` | Source wording and record codes: for tracing, not an instruction | 来源原文（英文）与记录原码：供追溯，不是操作指令 | 界面文字；en #40 `295da77`；zh #40 `295da77`；**已由 #40 修改，待 BIM 复核（措辞修改）** | en 131 页（fixture/recheck ×131）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 131 页 |
| E294 | `conditionBasis` | condition_basis (as written) | condition_basis（原文） | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 131 页（fixture/recheck ×131）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 131 页 |
| E295 | `evidenceHeading` | 5. The evidence before the recheck | 五、复检前的证据 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 131 页（fixture/recheck ×131）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 131 页 |
| E296 | `evidenceCount.one` | {count} piece of old evidence was assessed together with this item | 和这一项放在一起评估的旧证据共 {count} 条 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 10 页（fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed/recheck/0/0`；zh 91 页 |
| E297 | `evidenceCount.other` | {count} pieces of old evidence were assessed together with this item | 和这一项放在一起评估的旧证据共 {count} 条 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 81 页（fixture/recheck ×81）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 91 页 |
| E298 | `requirementChanged.one` | , and for {count} of them the check requirement changed | ，其中 {count} 条的检查要求变了 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 9 页（fixture/recheck ×9）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E299 | `requirementChanged.other` | , and for {count} of them the check requirement changed | ，其中 {count} 条的检查要求变了 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 9 页（fixture/recheck ×9）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E300 | `priorSources` | Evidence cited before the recheck, by source:  | 复检前引用的证据，来源： | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 91 页（fixture/recheck ×91）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 91 页 |
| E301 | `currentSources` | Corresponding evidence this record cites, by source:  | 本次记录引用的对应证据，来源： | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 91 页（fixture/recheck ×91）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 91 页 |
| E302 | `rowsSummary` | See each piece of old evidence and how it compared | 逐条查看旧证据和比较结果 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 91 页（fixture/recheck ×91）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 91 页 |
| E303 | `shared.one` | The record keeps the old evidence of a group of elements assessed together in one place, not split by element: the group's {count} item shares the rows below. | 记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 {count} 个事项共用下面这些行。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 31 页（fixture/recheck ×31）；例 `#/fixture/recheck-requirement-relaxed/recheck/3/0`；zh 91 页 |
| E304 | `shared.other` | The record keeps the old evidence of a group of elements assessed together in one place, not split by element: the group's {count} items share the rows below. | 记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 {count} 个事项共用下面这些行。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 60 页（fixture/recheck ×60）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 91 页 |
| E305 | `noEvidence` | The group's evidence path before the recheck cites no evidence. | 复检前这一组的证据路径没有引用任何证据。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 40 页（fixture/recheck ×40）；例 `#/fixture/recheck-requirement-relaxed/recheck/1/0`；zh 40 页 |
| E306 | `priorOrdinal` | Internal group number before the recheck | 复检前的内部分组编号 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 131 页（fixture/recheck ×131）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 131 页 |
| E307 | `currentLine` | Current internal group number, verdict and final outcome | 现在的内部分组编号、verdict 与终点 outcome | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 131 页（fixture/recheck ×131）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；zh 131 页 |

页面上下文（`E281` `back`）：
- en `#/fixture/recheck-requirement-relaxed/recheck/7/2`：‹ ← Back to the recheck items (to this item's place) › Recheck item · One element
- zh `#/fixture/recheck-requirement-relaxed/recheck/7/2`：‹ ← 返回复检事项列表（回到这一项的位置） › 复检事项 · 一个构件

页面上下文（`E282` `kicker`）：
- en `#/fixture/recheck-requirement-relaxed/recheck/7/2`：← Back to the recheck items (to this item's place) ‹ Recheck item · One element › building element

### WORKSPACE_COMPARE（48 条）— C2 复检对比（误读风险）

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E478 | `title` | Recheck comparison: the same check, two runs | 复检对比：同一项检查，前后两次运行 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E479 | `lede` | The pairs, the rows not re-evaluated and the newly appearing rows below are the returned data's; the page only counts and arranges them. | 下面的配对、未再评估和新出现都由返回数据给出，页面只计数和排列。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E480 | `runsHeading` | The two runs | 两次运行 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 4 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1; ws-refusal:workspace/result ×1）；例 `ws-compare:#/workspace/workspace/compare`；同页最多 ×5；zh 3 页 |
| E481 | `prior` | The run named as the earlier one (given with --prior at start-up) | 被指定为前一次的运行（启动时用 --prior 指定） | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；同页最多 ×2；zh 3 页 |
| E482 | `current` | This run (given with --workspace at start-up) | 本次运行（启动时用 --workspace 指定） | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；同页最多 ×2；zh 3 页 |
| E483 | `order` | Which run came first is what the server was told at start-up; the returned data itself cannot prove the order. | 哪一次在前，是启动服务器时的指定；返回数据本身不能证明先后。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E484 | `same` | The two runs have the same rule set, the same predicate for each requirement, the same checkers, the same logical date and the same set of models; were any of them different, the system would refuse the comparison and give neither side's results. | 两次运行的规则集、各条要求的谓词、检查程序、逻辑日期和模型组都相同；其中任何一项不同，系统都会拒绝对比，不给出任何一侧的结果。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E485 | `changedHeading` | 1. What changed | 一、什么变了 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E486 | `differs.one` | Results that differ between the runs: {count} | 两次结果不同的：{count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01`；中文是该提交新写的 | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E487 | `differs.other` | Results that differ between the runs: {count} | 两次结果不同的：{count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01`；中文是该提交新写的 | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E488 | `differsNone` | No result differs between the runs. | 没有两次结果不同的。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 2 页（ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-newly:#/workspace/workspace/compare`；zh 2 页 |
| E489 | `unchanged.one` | Results that are the same in both runs: {count} | 两次结果相同的：{count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01`；中文是该提交新写的 | en 14 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E490 | `unchanged.other` | Results that are the same in both runs: {count} | 两次结果相同的：{count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01`；中文是该提交新写的 | en 14 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-notreeval:workspace/finding ×2; ws-compare:workspace/result ×1; ws-compare:workspace/compare ×1; ws-newly:workspace/result ×1）；例 `ws-compare:#/workspace/workspace`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E491 | `unchangedNone` | No result is the same in both runs. | 没有两次结果相同的。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E492 | `transition.one` | {prior} → {current}: {count} row | {prior} → {current}：{count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E493 | `transition.other` | {prior} → {current}: {count} rows | {prior} → {current}：{count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E494 | `rows.one` | {count} row | {count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E495 | `rows.other` | {count} rows | {count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E496 | `notReEvaluated.label.one` | With a result in the earlier run only (not re-evaluated this time): {count} | 只在前一次有结果的（本次没有再评估）：{count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01`；中文是该提交新写的 | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E497 | `notReEvaluated.label.other` | With a result in the earlier run only (not re-evaluated this time): {count} | 只在前一次有结果的（本次没有再评估）：{count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01`；中文是该提交新写的 | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E498 | `notReEvaluated.note` | These have a result from the earlier run only and were not re-evaluated this time. They are not passes. | 这些只有前一次的结果，本次没有再评估。它们不是通过。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-notreeval:workspace/compare ×1）；例 `ws-notreeval:#/workspace/workspace/compare`；zh 1 页 |
| E499 | `newlyAppearing.label.one` | With a result in this run only (newly appearing): {count} | 只在本次有结果的（新出现）：{count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01`；中文是该提交新写的 | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E500 | `newlyAppearing.label.other` | With a result in this run only (newly appearing): {count} | 只在本次有结果的（新出现）：{count} 条 | 界面文字；en #36 `2934b01`；zh #36 `2934b01`；中文是该提交新写的 | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E501 | `newlyAppearing.note` | The earlier run did not have these results. | 这些结果前一次没有。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-newly:workspace/compare ×1）；例 `ws-newly:#/workspace/workspace/compare`；zh 1 页 |
| E502 | `inCurrent.true` | The element is still in this run's list of elements | 构件还在本次的构件清单里 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E503 | `inCurrent.false` | The element is not in this run's list of elements | 构件不在本次的构件清单里 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-notreeval:workspace/compare ×1）；例 `ws-notreeval:#/workspace/workspace/compare`；zh 1 页 |
| E504 | `inCurrent.null` | A result for the whole model, not for an element | 整个模型的一条结果，不针对构件 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到）；同句（en）：WORKSPACE_COMPARE.inPrior.null |
| E505 | `inPrior.true` | The element is in the earlier run's list of elements | 构件在前一次的构件清单里 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E506 | `inPrior.false` | The element is not in the earlier run's list of elements | 构件不在前一次的构件清单里 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-newly:workspace/finding ×1）；例 `ws-newly:#/workspace/workspace/finding/43907325-dccd-5b20-bc26-b401fad0f039`；zh 1 页 |
| E507 | `inPrior.null` | A result for the whole model, not for an element | 整个模型的一条结果，不针对构件 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到）；同句（en）：WORKSPACE_COMPARE.inCurrent.null |
| E508 | `whyHeading` | 2. Why it changed: what the returned data can say | 二、为什么会变：返回数据能说明的部分 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E509 | `changedModels` | Models whose content changed between the runs (listed by the returned data): | 两次之间内容变了的模型（返回数据列出）： | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E510 | `noChangedModels` | The returned data lists no model whose content changed: both runs read the same model files. | 返回数据没有列出内容变了的模型：两次读的是同样的模型文件。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E511 | `unchangedModels` | Models whose content did not change: | 内容未变的模型： | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 0 页（未渲染到） |
| E512 | `why` | The two runs have the same rule set, requirement predicates, checkers and logical date. Of the inputs the returned data compared, the only difference between the runs is the content of the model files listed above; what changed inside those files, the returned data does not list item by item. | 两次的规则集、要求谓词、检查程序和逻辑日期都相同。在返回数据比较过的这些输入里，两次之间不同的只有上面列出的模型文件内容；模型文件里改了哪些地方，返回数据没有逐项列出。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E513 | `notInData` | What was changed in Revit, who decided the value and who made the change, the returned data does not record. | 在 Revit 里改了什么、取值由谁决定、由谁操作，返回数据没有记录。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E514 | `gapsHeading` | 3. What evidence is still missing | 三、还缺什么证据 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E515 | `passLink` | What a pass proves and does not prove: see the details of the passing results. | 一条通过证明了什么、没证明什么，见通过那几条的详情。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-compare:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 1 页 |
| E516 | `open` | Open | 查看 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 3 页（ws-compare:workspace/compare ×1; ws-newly:workspace/compare ×1; ws-notreeval:workspace/compare ×1）；例 `ws-compare:#/workspace/workspace/compare`；zh 3 页 |
| E517 | `detailHeading` | Compared with the earlier run | 和前一次运行比 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 8 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 8 页 |
| E518 | `detailPrior` | Earlier result | 前一次的结果 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 7 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×2; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 7 页 |
| E519 | `detailCurrent` | This result | 本次的结果 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 7 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×2; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 7 页 |
| E520 | `detailNewly` | The earlier run has no such result: it is newly appearing. | 前一次运行没有这一条结果：它是新出现的。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 1 页（ws-newly:workspace/finding ×1）；例 `ws-newly:#/workspace/workspace/finding/43907325-dccd-5b20-bc26-b401fad0f039`；zh 1 页 |
| E521 | `detailNone` | The returned data's comparison does not include this result. | 返回数据的对比里没有这一条。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E522 | `priorReason` | Earlier reason (as written) | 前一次的原因（原文） | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 7 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×2; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 7 页 |
| E523 | `currentReason` | This reason (as written) | 本次的原因（原文） | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 7 页（ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×2; ws-notreeval:workspace/finding ×2）；例 `ws-compare:#/workspace/workspace/finding/76d69ece-295b-5b41-a7b3-9381efe80cd4`；zh 7 页 |
| E524 | `noComparison` | The server was started without an earlier run, so there is no comparison. To compare, add --prior at start-up. | 服务器启动时没有指定前一次运行，所以没有对比。要对比，启动时加上 --prior。 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E525 | `elementMissing` | The returned data has nothing readable about this element | 返回数据没有这个构件的可读信息 | 界面文字；en #36 `2934b01`；zh #26 `d6f89c1` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E478` `title`）：
- en `ws-compare:#/workspace/workspace/compare`：← Back to the list of results ‹ Recheck comparison: the same check, two runs › The pairs, the rows not re-evaluated and the newly appearing rows below are the returned data's; the
- zh `ws-compare:#/workspace/workspace/compare`：← 返回结果列表 ‹ 复检对比：同一项检查，前后两次运行 › 下面的配对、未再评估和新出现都由返回数据给出，页面只计数和排列。

页面上下文（`E479` `lede`）：
- en `ws-compare:#/workspace/workspace/compare`：Recheck comparison: the same check, two runs ‹ The pairs, the rows not re-evaluated and the newly appearing rows below are the returned data's; the page only counts and arranges them. › These are the results of a check, not a handover judgement: the page says only whether each element
- zh `ws-compare:#/workspace/workspace/compare`：复检对比：同一项检查，前后两次运行 ‹ 下面的配对、未再评估和新出现都由返回数据给出，页面只计数和排列。 › 这是一次检查的结果，不是交接判断：页面只说每个构件在每条要求下通过、不通过还是不适用，不对任何工作能否开始下结论。

## 新增中文终稿与候选条目（不在 549 条英文条目内）

### REASON_GLOSSES（1 条）— #27／#31 中文终稿

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E550 | `The predefined type "NOTDEFINED" does not meet the required type` | （无英文） | 预定义类型“NOTDEFINED”不属于要求的取值 | 界面文字（中文）；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | zh 0 页（未渲染到） |

### ACTION（6 条）— 处理角色／指派、行动：界面用语表里带含义的句子

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E551 | `what` | What to do | 要做什么 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 125 页（fixture/recheck ×96; fixture/item ×16; fixture/result ×11; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 125 页 |
| E552 | `team` | Handling team | 处理团队 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×4；zh 103 页；同句（en）：FIRST.team |
| E553 | `consequence` | What it means for this work | 对这项工作的后果 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 103 页（fixture/recheck ×87; fixture/item ×16）；例 `#/fixture/member-evidence/item/0/2/0`；zh 103 页 |
| E554 | `recheck` | What a recheck must show | 完成后拿什么复检 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 103 页（fixture/recheck ×87; fixture/item ×16）；例 `#/fixture/member-evidence/item/0/2/0`；zh 103 页 |
| E555 | `original` | Source wording (as the record carries it): for tracing, not an instruction | 来源原文（英文，记录所带）：供追溯，不是操作指令 | 界面文字；en #40 `295da77`；zh #40 `295da77`；**已由 #40 修改，待 BIM 复核（措辞修改）** | en 103 页（fixture/recheck ×87; fixture/item ×16）；例 `#/fixture/member-evidence/item/0/2/0`；zh 103 页 |
| E583 | `noSentence` | This interface has written no action for the version this record uses. The source wording the record carries is in the fold below; it is not an instruction. | 本界面没有为这条记录所用的版本写要做什么。记录所带的来源原文在下面的折叠里，它不是操作指令。 | 界面文字；en #40 `295da77`；zh #40 `295da77`；**已由 #40 修改，待 BIM 复核（中英新增）** | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E551` `what`）：
- en `#/fixture/member-evidence`："Unknown" means whether this work can start cannot be decided: it does not mean the element has no p ‹ What to do › This is not a known model defect. No coordination review has yet determined whether it passes throug
- zh `#/fixture/member-evidence`：“无法判断”说的是这项工作能否开始无法判断：不等于这个构件没有问题，也不是系统出错。 ‹ 要做什么 › 这不是已知的模型缺陷。还没有协调评审判定它是否穿过接收方的构件；需要开一次评审，记录“不穿过”或写明穿过哪些构件

页面上下文（`E552` `team`）：
- en `#/fixture/member-evidence`：Example handling team ‹ Handling team coordination-team Example handling team: 6 items › Default handling role (the rule's default, not an assignment): model-coordination The handling team
- zh `#/fixture/member-evidence/item/0/2/0`：这不是已知的模型缺陷。还没有协调评审判定它是否穿过接收方的构件；需要开一次评审，记录“不穿过”或写明穿过哪些构件 ‹ 处理团队 › 示例处理团队

### ITEM（6 条）— 处理角色／指派、行动：界面用语表里带含义的句子

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E556 | `noFollowUp` | The record gives no follow-up action, handling team or default handling role for this item. | 记录没有为这一项给出后续处理动作、处理团队或默认处理角色。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 40 页（fixture/recheck ×30; fixture/item ×10）；例 `#/fixture/member-evidence/item/0/1/0`；zh 40 页 |
| E557 | `needs` | What this work needs | 这项工作需要什么 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 26 页（fixture/item ×26）；例 `#/fixture/member-evidence/item/0/2/0`；zh 26 页 |
| E558 | `leaf` | Final outcome | 终点 outcome | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 26 页（fixture/item ×26）；例 `#/fixture/member-evidence/item/0/2/0`；zh 26 页 |
| E559 | `context` | Background citations: not the basis of this conclusion, shown word for word. | 背景引用：不是这个结论的依据，逐字显示。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 6 页（fixture/item ×6）；例 `#/fixture/member-evidence/item/1/2/0`；zh 6 页 |
| E560 | `actionHeading` | 2. What to do, who deals with it, what a recheck must show | 二、要做什么、由谁处理、完成后拿什么复检 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 16 页（fixture/item ×16）；例 `#/fixture/member-evidence/item/0/2/0`；zh 16 页 |
| E561 | `followUpHeading` | 2. Follow-up | 二、后续 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 10 页（fixture/item ×10）；例 `#/fixture/member-evidence/item/0/1/0`；zh 10 页 |

页面上下文（`E556` `noFollowUp`）：
- en `#/fixture/member-evidence/item/0/1/0`：2. Follow-up ‹ The record gives no follow-up action, handling team or default handling role for this item. › 3. Which element
- zh `#/fixture/member-evidence/item/0/1/0`：二、后续 ‹ 记录没有为这一项给出后续处理动作、处理团队或默认处理角色。 › 三、是哪个构件

页面上下文（`E557` `needs`）：
- en `#/fixture/member-evidence/item/0/2/0`：No coordination review has determined yet whether it passes through elements of the receiving model ‹ What this work needs › Needs to know where MEP penetrates architectural fabric, so openings can be cut in walls, floors and
- zh `#/fixture/member-evidence/item/0/2/0`：还没有协调评审判定它是否穿过接收方模型里的构件 ‹ 这项工作需要什么 › 要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。

### FIRST（7 条）— 处理角色／指派、行动：界面用语表里带含义的句子

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E562 | `team` | Handling team  | 处理团队  | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba` | en 181 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×4；zh 103 页；同句（en）：ACTION.team |
| E563 | `verdictLine` | : the work concerned is  | ：对应的那项工作  | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba`；中文原句在此前的代码里已有，随该提交移入词表 | en 4 页（fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×2；zh 0 页（未渲染到） |
| E564 | `quietLine` | : {summary} (listed further down this page) | ：{summary}（列在本页下方） | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba`；中文原句在此前的代码里已有，随该提交移入词表 | en 4 页（fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E565 | `problem` | Problem | 问题 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba` | en 107 页（fixture/recheck ×87; fixture/item ×16; fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 107 页 |
| E566 | `columns.work` | Which work: conclusion | 哪项工作：结论 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba`；中文原句在此前的代码里已有，随该提交移入词表 | en 4 页（fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；同页最多 ×3；zh 4 页 |
| E567 | `openHeading.one` | {label}, by handling team ({count} item) | {label}，按处理团队（{count} 个事项） | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文是该提交新写的 | en 0 页（未在公开样例页面里渲染到）；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E568 | `openHeading.other` | {label}, by handling team ({count} items) | {label}，按处理团队（{count} 个事项） | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文是该提交新写的 | en 4 页（fixture/result ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 0 页（模板，固定文字太少，没有按页面匹配） |

页面上下文（`E562` `team`）：
- en `#/fixture/member-evidence`：Example handling team ‹ Handling team coordination-team Example handling team: 6 items › Default handling role (the rule's default, not an assignment): model-coordination The handling team
- zh `#/fixture/member-evidence/item/0/2/0`：这不是已知的模型缺陷。还没有协调评审判定它是否穿过接收方的构件；需要开一次评审，记录“不穿过”或写明穿过哪些构件 ‹ 处理团队 › 示例处理团队

页面上下文（`E563` `verdictLine`）：
- en `#/fixture/member-evidence`：Blocked ‹ 4 items: the work concerned is Blocked › Unknown

### CONTEXT（2 条）— 处理角色／指派、行动：界面用语表里带含义的句子

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E569 | `noJudgement` | Check results only, no handover judgement | 只有检查结果，没有交接判断 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba`；中文是该提交新写的 | en 0 页（未在公开样例页面里渲染到）；zh 5 页；同句（en）：WORKSPACE.contextNoJudgement |
| E570 | `noResult` | No check results this time | 本次没有检查结果 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba`；中文原句在此前的代码里已有，随该提交移入词表 | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E569` `noJudgement`）：
- zh `ws-compare:#/`：查看一次真实检查 ‹ 启动服务器时指定了一个工作区，里面是一次已经跑完的检查：每个构件在每条要求下的结果。若同时指定了前一次运行，还可以看两次的前后对比。这里只有检查结果，没有交接判断。页面只查看这次已经跑完的检查，不能在页面上选择或更换模型。 › 查看这次检查

### EVIDENCE（4 条）— 处理角色／指派、行动：界面用语表里带含义的句子

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E571 | `reissueColumns.role` | Role (from this request's handover) | 角色（取自本次请求的交接） | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E572 | `dispositionNow` | This item now | 这个事项现在 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 26 页（fixture/recheck ×20; fixture/result ×6）；例 `#/fixture/recheck-both-reissued`；同页最多 ×5；zh 26 页 |
| E573 | `reissued` | Re-issued (new version) | 重新发布了（新版本） | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 10 页（fixture/result ×5; fixture/recheck ×5）；例 `#/fixture/recheck-both-reissued`；同页最多 ×2；zh 10 页 |
| E574 | `notReissued` | Unchanged (original version) | 没有变（原版本） | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 18 页（fixture/result ×9; fixture/recheck ×9）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 18 页 |

页面上下文（`E571` `reissueColumns.role`）：
- en `#/fixture/recheck-requirement-relaxed`：Side of the handover ‹ Role (from this request's handover) › Model
- zh `#/fixture/recheck-requirement-relaxed`：交接的哪一侧 ‹ 角色（取自本次请求的交接） › 是否重新发布

页面上下文（`E572` `dispositionNow`）：
- en `#/fixture/recheck-both-reissued`：Builder's-work openings: before the recheck Ready; now: not given in the record ‹ This item now › These two elements are no longer paired for checking; that does not mean the opening was added
- zh `#/fixture/recheck-both-reissued`：土建预留开洞：复检前 可以开始；现在：记录没有给出 ‹ 这个事项现在 › 这两个构件现在不再被配成一对来检查，不等于开洞已补

### RECHECK_MODEL（3 条）— 处理角色／指派、行动：界面用语表里带含义的句子

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E575 | `onlyRekeyed` | {rekeyed}: neither the evidence content nor the comparison basis changed. | {rekeyed}：证据内容和比较依据都没有变。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 30 页（fixture/recheck ×30）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；同页最多 ×6；zh 30 页 |
| E576 | `producing` | Handing-over side | 交出方 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 20 页 |
| E577 | `consuming` | Receiving side | 接收方 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 20 页 |

页面上下文（`E575` `onlyRekeyed`）：
- en `#/fixture/recheck-requirement-relaxed/recheck/7/2`：There is exactly one corresponding check result; model version, check result content, check requirem ‹ Only the citation's key changed: neither the evidence content nor the comparison basis changed. › Tracing (record codes and content fingerprints)
- zh `#/fixture/recheck-requirement-relaxed/recheck/7/2`：对应的检查结果只有一条，模型版本、检查结果内容、检查要求、检查程序逐项相同。 ‹ 只是引用换了键：证据内容和比较依据都没有变。 › 追溯信息（记录原码与内容指纹）

页面上下文（`E576` `producing`）：
- en `#/fixture/recheck-requirement-relaxed`：Re-issued? ‹ Handing-over side › MEP
- zh `#/fixture/recheck-requirement-relaxed`：是否重新发布 ‹ 交出方 › MEP

### WORK（3 条）— 处理角色／指派、行动：界面用语表里带含义的句子

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E578 | `unchanged` | {work}: {before} ({note}) | {work}：{before} （{note}） | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E579 | `changed` | {work}: before the recheck {before} → now {now} | {work}：复检前 {before} → 现在 {now} | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 35 页（fixture/recheck ×29; fixture/result ×6）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×14；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E580 | `missing` | {work}: before the recheck {before}; now: not given in the record | {work}：复检前 {before}；现在：记录没有给出 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 26 页（fixture/recheck ×20; fixture/result ×6）；例 `#/fixture/recheck-both-reissued`；同页最多 ×5；zh 26 页 |

页面上下文（`E579` `changed`）：
- en `#/fixture/recheck-requirement-relaxed`：The record also shows that, among the old evidence assessed together with this item, the check requi ‹ building element | Room data sheets and equipment schedules: before the recheck Blocked → now Ready Basis shared by the items in this group, some of it simulated:Simulated check result ×2 Holds for this one item, this work and the listed model versions only; it does not mean the whole handover is complete.The record also shows that, among the old evidence as › Neither model was re-issued, yet these conclusions changed: the change does not come from a model ed

页面上下文（`E580` `missing`）：
- en `#/fixture/recheck-both-reissued`：floor: IfcSlab (IFC class) · 00 groundfloor · model architecture ‹ Builder's-work openings: before the recheck Ready; now: not given in the record › This item now
- zh `#/fixture/recheck-both-reissued`：floor：楼板 IfcSlab · 00 groundfloor · 模型 architecture ‹ 土建预留开洞：复检前 可以开始；现在：记录没有给出 › 这个事项现在

### FAULT_WORDS（2 条）— 处理角色／指派、行动：界面用语表里带含义的句子

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E581 | `note` | This is a problem of the program itself, not a judgement about any project or model; there are no check results to show. | 这是程序自身的问题，不是对任何项目或模型的判断；没有任何检查结果可以显示。 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E582 | `fault` | Program fault: no check data was received | 程序故障：没有拿到检查数据 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

