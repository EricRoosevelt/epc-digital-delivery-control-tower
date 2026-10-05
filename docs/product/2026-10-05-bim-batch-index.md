# BIM 分批条目索引（D6）：总览

日期：2026-10-05。负责：README 会话。基线：`main` @ `a5b89d0`（含 #40）。状态：**索引，不是复核**；本文件不判断任何条目的含义对错，不改任何词条。

依据：PM 的 D6（按误读风险分两批，10/22 留作修正复核）与技术总监的任务包。条目取自 `doctor/static/vocabulary.js` 与 `vocabulary-en.js`，分类沿用英文词表记录 [`2026-10-03-doctor-english-vocabulary.md`](2026-10-03-doctor-english-vocabulary.md) 的原文／领域含义／界面用语三类，没有重新分类。

## 1. 条数

D6 要求分开记录**原有的 517 条领域文字**和**之后新增的文字**，不重复计算。“原有 517”按 `98601fc` 的词表记录定（12 + 517 + 161 = 690）；`a5b89d0` 的词表记录是 12 + 537 + 160 = 709，多出的 20 条领域条目就是 #40 新增的英文 `ACTIONS`。

| 范围 | 条数 | 说明 |
|---|---:|---|
| 原有英文领域条目 | **517** | `98601fc` 词表记录的 50 张表；每条有英文和对应中文。与 TD 报告的 517 一致 |
| 新增英文领域条目 | **20** | #40 新增的英文 `ACTIONS` 表（10 种问题类型 × 行动、复检）。中文早已在 `ACTIONS` 里，这 20 条是英文新增，所以按“新增”计 |
| 原文（Pack／记录／产品文档，未翻译） | 12 | 词表记录 3 张表：活动名、判断码、判断词定义。D6 的 10/8 清单点名了活动名和判断词，所以一并索引 |
| **小计：索引内英文条目** | **549** | 517 + 20 + 12；等于 `a5b89d0` 词表记录的 12 + 537 |
| 新增：#27／#31 的最终中文，不在上面 549 条里 | 1 | 中文终稿，没有英文对应 |
| 候选：界面用语表里带含义的句子 | 33 | 词表记录把它们归为界面用语（160 条），不在 549 里；建议 BIM 看，由 TD／PM 定 |

核对：代码里 `a5b89d0` 的英文表（原文 + 领域）共 549 条，与词表记录逐键一致（脚本已断言）；原有 517 条与 `98601fc` 的记录逐键一致。

#40 还改了原有 517 条里的 3 条的措辞（第 4 节），它们仍按原有 517 条计，在“来源 · 引入”里标“已由 #40 修改，待 BIM 复核”。

### 两批各多少

| 批次 | 原文 12 | 原有领域 517 | 新增领域 20 | 新增中文终稿 | 候选（界面用语） | 合计 |
|---|---:|---:|---:|---:|---:|---:|
| 10/8 A 层（D6 逐条点名） | 12 | 267 | 20 | 1 | 33 | 333 |
| 10/8 B 层（优先主路径与 C2） | 0 | 95 | 0 | 0 | 0 | 95 |
| **10/8 合计** | 12 | 362 | 20 | 1 | 33 | 428 |
| 10/15 | 0 | 155 | 0 | 0 | 0 | 155 |

新增中文终稿与候选条目全部放进 10/8 A 层：#27／#31 的最终中文是 D6 点名的；候选是处理角色／指派与行动的句子；新增的英文 `ACTIONS` 是源修改与复检行动。

条数不能代表复核时间：长句、含限制和否定的句子比标签慢得多。BIM 可用时间我没有，请 TD／PM 提供。

## 2. 怎么读

每条一行，字段如下；CSV 里有全部字段，Markdown 里是合并后的。

- **页面和路由**：条目的文字实际出现在哪些页面。页面是真的渲染出来的：把公开样例的 Doctor 在中文和英文下逐路由打开，读出页面文字，再按条目文字匹配（共 869 个页面，含默认服务器的全部模拟示例与随附项目页，以及用公开 HVAC 样例和 `product-validation` 规则集建的 5 个工作区组合）。占位符（`{count}` 之类）按其余文字匹配。固定文字少于 12 个字符的条目只算整块文字相等的页面；带占位符、固定文字又少于 12 个字符的模板（例如 `{label}: {meaning}.`）没有按页面匹配，“页面”列写“模板”。短标签（如 `Model`）在几张表里都有同一个词，页面数可能包含别的键写出同一个词的页面。
- **所在表与键**：`vocabulary.js`／`vocabulary-en.js` 里的表名和键，数组用 `[i]`，单复数用 `.one`／`.other`。
- **来源**：界面文字（为本界面所写）／Pack 或产品文档原文／规则文件。只有词表记录点明的三张原文表和 `RULE_NOTES.PV-001.title`（规则文件的 title）、`RULE_NOTES.PV-001.action.what` 里一句（规则文件的 instructions）属于前两类之外的来源，其余都是界面文字。
- **引入的提交和 PR**：按**值**追溯。取词表文件被改过的 21 个提交，逐个读出每个提交下的表，找当前文字从哪个提交起一直保持不变。所以这里写的是“写下当前措辞的提交”，不一定是这个键第一次出现的提交；措辞被改过的，更早的措辞不在这里。中文和英文各查一次，因为两边是分别写的。
- **中文原句早已存在，随提交移入词表**：#33／#34／#36 把许多中文句子从页面代码移进词表。我查了该提交的前一版代码里是否已有这句中文；有就标“移入”，没有标“新写”。这是机器查的，不是语义判断。
- **复用**：同一句英文（或中文）出现在几个键下，列出另外的键；同一页里重复出现的，写“同页最多 ×N”。同一个键在几个页面出现，看“页面”列。
- **页面上下文**：每张表后面摘两条，写出渲染页面上被匹配到的那一块文字及其前后各一块。CSV 的 `en_context`／`zh_context` 每条都有。
- **已由 #40 修改，待 BIM 复核**：#40（P0，中英行动一致）改过措辞或新增的条目（第 4 节）。

私有内容：这份索引没有用 C2 的私有工作区，也没有写任何私有标识、计数或截图。工作区页面是用公开 HVAC 样例和 `product-validation` 规则集在会话临时目录里新建的运行渲染的。

## 3. 分批规则

按表分，少数键单列。规则取自 D6 的 10/8 清单；清单没有点名、但属于“主路径与 C2 相关误读风险”的，放 B 层。

| 批次与层 | D6 类别 | 表 |
|---|---|---|
| 10/8 A | PASS／FAIL／N/A／拒绝区别 | `FINDING_STATUS` |
| 10/8 A | PASS／FAIL／N/A／拒绝区别（C2 工作区结果页） | `WORKSPACE` |
| 10/8 A | PASS／FAIL／N/A／拒绝区别（拒绝原因） | `WORKSPACE_REFUSAL_REASONS` |
| 10/8 A | PASS／FAIL／N/A／拒绝区别（拒绝页） | `WORKSPACE_REFUSAL` |
| 10/8 A | Tag 不一致后的行动 | `TAG_WORDS` |
| 10/8 A | W6 类型对应说明／PASS 证明什么 | `RULE_NOTES` |
| 10/8 A | 处理角色／指派 | `HANDOVER_SIDES` |
| 10/8 A | 活动名 | `ACTIVITY_NAMES` |
| 10/8 A | 源修改与复检行动 | `ACTION_GROUPS`、`CONDITION_ENTRIES`、`CONDITION_STATES`、`CONSEQUENCE_KINDS`、`RESOLUTION_KINDS` |
| 10/8 A | 源修改与复检行动（#40 新增的英文） | `ACTIONS` |
| 10/8 A | 英文判断词 | `VERDICT_LABELS`、`VERDICT_WORDS`、`READING_GUIDE`、`VERDICT_GROUPS` |
| 10/8 A | 范围限制 | `BESIDE`、`DEMO_NOTICE`、`DIRECTORY_NOTE`、`EXAMPLE_NOTE`、`ITEM_UNIT`、`PROVENANCE_NOTICE`、`READY_NOTES`、`RECHECK_CANNOT`、`RECHECK_LIMITS`、`VERDICT_SCOPE` |
| 10/8 A | 范围限制（首页写明不能做什么） | `HOME` |
| 10/8 A | 规则来源 | `BASIS_WORDS`、`CITATION_KINDS`、`CITATION_PROVENANCE`、`DETAILS_WORDS` |
| 10/8 B | C2 复检对比（误读风险） | `WORKSPACE_COMPARE` |
| 10/8 B | 主路径：结论所依据的结果 | `LEAF_READINGS`、`LEAF_READING_WORDS` |
| 10/8 B | 复检单项页（含复检前的结束条件） | `RECHECK_ITEM` |
| 10/15 | 入口名称 | `MODE_LABELS` |
| 10/15 | 复检结果页 | `RECHECK` |
| 10/15 | 复检：哪一侧模型重新发布 | `REISSUE_CASES`、`REISSUE_NEUTRAL` |
| 10/15 | 复检：引用换键 | `KEY_CHANGED`、`ONLY_REKEYED` |
| 10/15 | 复检：旧证据的去向 | `CARRY_OVER_REASONS`、`CARRY_OVER_STATES` |
| 10/15 | 复检：构件去向 | `DISPOSITIONS`、`DISPOSITION_ENTRIES` |
| 10/15 | 复检：比较了哪些方面 | `ASPECT_NOTES`、`CHANGED_ASPECTS` |
| 10/15 | 复检：要求变化提示 | `REQUIREMENT_CHANGED_NOTE` |
| 10/15 | 构件卡片用语 | `ELEMENT_WORDS` |
| 10/15 | 示例名称（含第二入口） | `RUN_LABELS` |
| 10/15 | 示例目录说明 | `EXAMPLES` |
| 10/15 | 首页标题与入口说明 | `HOME` |
| 10/15 | 首页第三入口（真实检查） | `WORKSPACE_HOME` |

`HOME` 表里写“不能做什么”的 7 个键（`status`、`statusWithWorkspace`、`statusWorkspaceUnknown`、`cannot[0..2]`、`cannotNote`）归 10/8 A（范围限制），其余 10 个键归 10/15。

这是我按 D6 原文的一次归类，不是 BIM 的判断。CSV 的 `batch`／`tier` 两列可以直接改，改了之后 Markdown 的条数以 CSV 为准。

## 4. #40（P0，中英行动一致）改了什么

#40 已合并（`a5b89d0`，提交 `295da77`）。对照文件 [`2026-10-04-doctor-bilingual-action-parity.md`](2026-10-04-doctor-bilingual-action-parity.md) 已在 main 上，第五节是交 10/8 BIM 的条目清单。下表是我用 `295da77` 前后的词表逐键比对得到的，与该文件第五节一致。

| 表 | 键 | 变化 | 索引 ID |
|---|---|---|---|
| `ACTION` | `noSentence` | 中英新增 | E583 |
| `ACTION` | `original` | 措辞修改 | E555 |
| `ACTIONS` | `asset-identity-not-evaluated.action` | en 新增 | E015 |
| `ACTIONS` | `asset-identity-not-evaluated.recheck` | en 新增 | E016 |
| `ACTIONS` | `cross-model-alignment-not-confirmed.action` | en 新增 | E023 |
| `ACTIONS` | `cross-model-alignment-not-confirmed.recheck` | en 新增 | E024 |
| `ACTIONS` | `cross-model-misalignment.action` | en 新增 | E027 |
| `ACTIONS` | `cross-model-misalignment.recheck` | en 新增 | E028 |
| `ACTIONS` | `in-model-position-not-evaluated.action` | en 新增 | E017 |
| `ACTIONS` | `in-model-position-not-evaluated.recheck` | en 新增 | E018 |
| `ACTIONS` | `mep-element-not-spatially-assigned.action` | en 新增 | E025 |
| `ACTIONS` | `mep-element-not-spatially-assigned.recheck` | en 新增 | E026 |
| `ACTIONS` | `missing-corresponding-opening.action` | en 新增 | E021 |
| `ACTIONS` | `missing-corresponding-opening.recheck` | en 新增 | E022 |
| `ACTIONS` | `missing-project-asset-identity.action` | en 新增 | E013 |
| `ACTIONS` | `missing-project-asset-identity.recheck` | en 新增 | E014 |
| `ACTIONS` | `opening-not-verifiably-linked.action` | en 新增 | E029 |
| `ACTIONS` | `opening-not-verifiably-linked.recheck` | en 新增 | E030 |
| `ACTIONS` | `opening-status-not-determined.action` | en 新增 | E031 |
| `ACTIONS` | `opening-status-not-determined.recheck` | en 新增 | E032 |
| `ACTIONS` | `penetration-not-determined.action` | en 新增 | E019 |
| `ACTIONS` | `penetration-not-determined.recheck` | en 新增 | E020 |
| `RECHECK_ITEM` | `originalSummary` | 措辞修改 | E293 |
| `RULE_NOTES` | `PV-001.action.revise` | 措辞修改 | E352 |
| `TAG_WORDS` | `note` | 措辞修改 | E372 |
| `ACTION` | `whatOriginal` | zh 删除 | （已删，不需要复核） |
| `ACTION` | `recheckOriginal` | zh 删除 | （已删，不需要复核） |
| `ACTION_TEXT` | `source` | zh 删除 | （已删，不需要复核） |
| `ACTION` | `whatOriginal` | en 删除 | （已删，不需要复核） |
| `ACTION` | `recheckOriginal` | en 删除 | （已删，不需要复核） |
| `ACTION_TEXT` | `source` | en 删除 | （已删，不需要复核） |

具体：英文新增 `ACTIONS` 表（10 种问题类型 × 行动、复检，共 20 条）；`ACTION` 表删 `whatOriginal`、`recheckOriginal`、新增 `noSentence`、改 `original`；`RECHECK_ITEM.originalSummary`、`RULE_NOTES.PV-001.action.revise`（W6）、`TAG_WORDS.note`（Tag 不一致时的行动）中英都改措辞；删 `ACTION_TEXT`。按 UI 会话的数：英文词表 690 → 709，领域 517 → 537，界面用语 161 → 160。

这些条目的新措辞**未经 BIM 复核**，全部在 10/8 批（A 层）。#40 之前，首次结果列表、单项页和复检页上的英文“要做什么”“复检要看到什么”不是词表条目，而是页面直接显示记录里路由的 `next_action` 和 `recheck_condition`；#40 起英文也读 `ACTIONS`，与中文同表同键。

对照文件还指出两件事，BIM 会用到，这里只转述位置，不转述结论：①英文行动改前与中文有义务差异的共 3 处（`asset-identity-not-evaluated` 的行动、`in-model-position-not-evaluated` 的行动、`missing-project-asset-identity` 的复检），轻微 2 处，只有开头断言不同 3 处；②`REASON_GLOSSES`（中文 4 条释义，英文显示原文）里有 1 条中文多了半句说明，该文件列出供 BIM 判断英文是否也需要。

## 5. 新增条目（不在 549 条英文条目内）

- **#27／#31 的最终中文**：#27（`44cf2d7`）与 #31（`2d40955`）的四个提交写下或改过 27 个键的中文，其中 26 个在上面的 549 条里（它们在“来源 · 引入”里标了“#27／#31 终稿”；若当前措辞后来又被 #40 改过，“引入”一栏会写 #40），1 个不在，列为新增。
- **这四个提交删去的中文键**：3 个（`RULE_NOTES.PV-001.userDefined`、`RULE_NOTES.PV-001.action.where`、`WORKSPACE.actionWhere`）。删去的不再显示，不需要复核。
- **候选**：33 条界面用语表里带含义的句子（处理团队、角色、“不是指派”、“后续动作”、判断、依据、重新发布等）。

全部在 [10/8 批文件](2026-10-05-bim-batch-index-1008.md) 的末节。

## 6. 复用

同一句话出现在几个键下的情况（长度不少于 12 个字符）：

英文：

- “Handling team” — `ACTION.team`、`FIRST.team`
- “The record does not say what these items' conclusions are now. An element that is gone does not mean the problem was fixed.” — `ACTION_GROUPS.unplaced.note`、`VERDICT_GROUPS.unplaced.note`
- “Only the named outcome observed; the rest of the condition not checked” — `CONDITION_ENTRIES.named-outcome-observed.text`、`CONDITION_STATES.named-outcome-observed`
- “Named outcome not observed” — `CONDITION_ENTRIES.named-outcome-not-observed.text`、`CONDITION_STATES.named-outcome-not-observed`
- “The condition has no machine-checkable part; a person must read it” — `CONDITION_ENTRIES.no-machine-checkable-part.text`、`CONDITION_STATES.no-machine-checkable-part`
- “Cannot be compared: the corresponding elements are incomplete” — `CONDITION_ENTRIES.not-comparable.text`、`CONDITION_STATES.not-comparable`
- “The original record had no recheck condition” — `CONDITION_ENTRIES.no-recheck-condition.text`、`CONDITION_STATES.no-recheck-condition`
- “Check results only, no handover judgement” — `CONTEXT.noJudgement`、`WORKSPACE.contextNoJudgement`
- “The rule's own words” — `DETAILS_WORDS.expected`、`WORKSPACE.ruleExpected`
- “Choose a simulated example” — `DIRECTORY.exampleTitle`、`HOME.example.action`
- “Still in this check's scope; conclusion and condition are read separately” — `DISPOSITIONS.present`、`DISPOSITION_ENTRIES.present.text`
- “Deleted in the re-issued model; that is not a fix” — `DISPOSITIONS.element-deleted-in-reissued-model`、`DISPOSITION_ENTRIES.element-deleted-in-reissued-model.text`
- “No longer of this activity's subject classes; that is not a fix” — `DISPOSITIONS.element-out-of-subject-class`、`DISPOSITION_ENTRIES.element-out-of-subject-class.text`
- “These two elements are no longer paired for checking; that does not mean the opening was added” — `DISPOSITIONS.pairing-no-longer-derived`、`DISPOSITION_ENTRIES.pairing-no-longer-derived.text`
- “This scope was not declared this time; that does not mean the problem is gone” — `DISPOSITIONS.outside-declared-scope`、`DISPOSITION_ENTRIES.outside-declared-scope.text`
- “Internal key for tracing” — `ELEMENT_CARD.traceKey`、`WORKSPACE.identity.elementKey`
- “{count} item” — `FIRST.items.one`、`RECHECK.groupLine.one`
- “{count} items” — `FIRST.items.other`、`RECHECK.groupLine.other`
- “{label} ({count} item)” — `FIRST.quietHeading.one`、`RECHECK.groupHeading.one`
- “{label} ({count} items)” — `FIRST.quietHeading.other`、`RECHECK.groupHeading.other`
- “Internal group number” — `FIRST.traceOrdinal`、`ITEM.ordinal`
- “It has no storey or space assignment” — `LEAF_READINGS.in-model-position/unmet`、`RESOLUTION_KINDS.mep-element-not-spatially-assigned`
- “Storey (IFC)” — `WORKSPACE.columns.storey`、`WORKSPACE.element.storey`
- “A result for the whole model, not for an element” — `WORKSPACE_COMPARE.inCurrent.null`、`WORKSPACE_COMPARE.inPrior.null`

中文：

- “仅命名结果已观察到；条件其余部分未检查” — `CONDITION_ENTRIES.named-outcome-observed.text`、`CONDITION_STATES.named-outcome-observed`
- “条件没有可机检部分，需要人阅读” — `CONDITION_ENTRIES.no-machine-checkable-part.text`、`CONDITION_STATES.no-machine-checkable-part`
- “不可比较：对应的构件不完整” — `CONDITION_ENTRIES.not-comparable.text`、`CONDITION_STATES.not-comparable`
- “只有检查结果，没有交接判断” — `CONTEXT.noJudgement`、`WORKSPACE.contextNoJudgement`
- “仍在本次检查范围内；判断与条件另看” — `DISPOSITIONS.present`、`DISPOSITION_ENTRIES.present.text`
- “在重发模型中删除，不等于修复” — `DISPOSITIONS.element-deleted-in-reissued-model`、`DISPOSITION_ENTRIES.element-deleted-in-reissued-model.text`
- “已不属于此活动对象类别，不等于修复” — `DISPOSITIONS.element-out-of-subject-class`、`DISPOSITION_ENTRIES.element-out-of-subject-class.text`
- “这两个构件现在不再被配成一对来检查，不等于开洞已补” — `DISPOSITIONS.pairing-no-longer-derived`、`DISPOSITION_ENTRIES.pairing-no-longer-derived.text`
- “本次未声明该范围，不等于问题解除” — `DISPOSITIONS.outside-declared-scope`、`DISPOSITION_ENTRIES.outside-declared-scope.text`
- “{label}（{count} 个事项）” — `FIRST.quietHeading.one`、`FIRST.quietHeading.other`、`RECHECK.groupHeading.one`、`RECHECK.groupHeading.other`
- “整个模型的一条结果，不针对构件” — `WORKSPACE_COMPARE.inCurrent.null`、`WORKSPACE_COMPARE.inPrior.null`

同一个键在多个页面出现的，是每条的“页面”列。页面最多的条目（英文）：

| ID | 表.键 | 页面数 | 页面类型 |
|---|---|---:|---|
| E170 | `ELEMENT_WORDS.noClassName` | 199 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3 |
| E432 | `WORKSPACE.columns.model` | 195 | fixture/recheck ×141; fixture/item ×26; fixture/result ×10; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3 |
| E464 | `WORKSPACE.identity.modelId` | 195 | fixture/recheck ×141; fixture/item ×26; fixture/result ×10; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3 |
| E475 | `WORKSPACE.element.model` | 195 | fixture/recheck ×141; fixture/item ×26; fixture/result ×10; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3 |
| E093 | `CHANGED_ASPECTS.model-version` | 182 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2; fixture/list ×1 |
| E007 | `VERDICT_LABELS.READY` | 181 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2 |
| E008 | `VERDICT_LABELS.BLOCKED` | 181 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2 |
| E009 | `VERDICT_LABELS.UNKNOWN` | 181 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2 |
| E010 | `VERDICT_WORDS.READY` | 181 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2 |
| E011 | `VERDICT_WORDS.BLOCKED` | 181 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2 |
| E012 | `VERDICT_WORDS.UNKNOWN` | 181 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2 |
| E100 | `CITATION_PROVENANCE.finding-real.short` | 181 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2 |
| E101 | `CITATION_PROVENANCE.finding-real.long` | 181 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2 |
| E103 | `CITATION_PROVENANCE.finding-fixture.short` | 181 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2 |
| E104 | `CITATION_PROVENANCE.finding-fixture.long` | 181 | fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2 |

## 7. 没有覆盖到的部分

- **没有在任何公开样例页面里渲染到的条目**：英文 89 条、中文 107 条（CSV 里 `en_pages`／`zh_pages` 为 0，Markdown 里标“未在公开样例页面里渲染到”）。它们对应的状态在公开样例里走不到（例如某些复检的构件去向、对比被拒绝的个别原因、故障与异常说明），也可能是文字被拆成几块显示、我的匹配没有对上。这不说明条目没用，只说明我没能给出页面上下文；它们的位置按键和所在表给出。
- **英文显示原文、中文有释义的表**：3 张——`CITATION_GLOSSES`（中文 1 键）、`IFC_CLASS_NAMES`（中文 6 键）、`REASON_GLOSSES`（中文 4 键）。英文下页面直接显示记录或规则的原文，没有英文条目；中文是对原文的释义。它们不在 549 条里，我没有逐条索引。
- **没有英文的中文表**：11 张，共 20 个中文键——`ACTION_PACK`（2）、`ASPECT_ORDER`（4）、`FIXTURE_MARKER`（1）、`FOLLOW_UP`（1）、`POLICY_SOURCE_NOTE`（1）、`PRODUCT_VALIDATION`（1）、`PROJECT_ASSUMPTION`（1）、`REFUSAL_REASONS`（4）、`REFUSAL_SCOPE_NOTE`（1）、`REFUSAL_UNGLOSSED`（2）、`RULE_NOTES_FOR`（2）。它们是记录、活动、成员、拒绝等没有翻译的页面或辅助表，英文下显示“尚未翻译”。我没有把它们列入索引（D6 说记录／活动／成员页后排）；其中被 #27／#31 改过的，已在第 5 节。
- **界面用语 160 条**：除候选之外没有索引。分类沿用词表记录；我按关键词挑了候选，没有读过每一条界面用语是否带含义。
- **不在表里的文字**：记录本身带的 `next_action`／`recheck_condition`／`prior_recheck_condition`（#40 起只在折叠里）、规则的 `expected`／`reason`／`citation` 原文、IFC 类别名，页面直接显示，不在任何词表。它们的英文是 Pack 或规则文件的原文，因此引用关系放在“来源”里，没有逐条索引。
- **D6 列入 10/15、但 a5b89d0 里还不存在的**：D2 第二入口（随附项目检查尝试的结果页与拒绝页）的英文——该页在英文下显示“尚未翻译”；本地 IFC 的规则选择与范围；留存／清理说明；3D 无几何与定位措辞；D1 的收起卡片新句。它们要等写出来才能索引。
- **私有工作区**：没有使用。C2 私有运行里的条目只按路由和键列出，不写标识、计数或截图；本索引因为用公开样例的工作区渲染了同样的页面，所以没有需要只写路由和键的条目。

## 8. 我没有做的

- 不判断任何条目含义对错；不改任何词条、测试或词表记录。
- 不替 BIM 排序：一批之内的先后由 BIM 定。
- 不估 BIM 用时。
- 不替 TD／PM 决定候选条目要不要进 10/8，也不重新分类词表记录里的界面用语。
- 生成脚本没有入库：它们要启动本地服务器和浏览器，我没有为它们过仓库的 lint。要复现，按第 2 节的方法在 `a5b89d0` 上重做；需要入库的话我另开 PR。

## 9. 附：提交与 PR 对照

| 提交 | PR | 日期 | 标题 |
|---|---|---|---|
| `55e90ba` | #13 | 2026-09-22 | feat: a clickable Doctor preview over the internal adapter's envelopes |
| `69678df` | #13 | 2026-09-22 | fix: decide a citation's provenance from that citation, not from the envelope |
| `9759242` | #13 | 2026-09-22 | fix: show no baseline-limitations table without a basis for it in the envelope |
| `eb05f61` | #21 | 2026-10-01 | feat: show a recheck as what changed, what is still open and what to do next |
| `64400d8` | #21 | 2026-10-01 | feat: word the nine adapter recheck scenarios, and count evidence by kind |
| `ab0cdff` | #21 | 2026-10-01 | fix: name recheck runs by number, and lead with what became of each verdict |
| `f4a984f` | #21 | 2026-10-02 | feat: carry one path a BIM manager can walk without being talked through it |
| `542636a` | #21 | 2026-10-02 | fix: say what a verdict means for the receiving side's work, not that a check passed |
| `968422d` | #21 | 2026-10-02 | feat: start from an ordinary first check, and say what to do before what to remember |
| `42720ab` | #21 | 2026-10-02 | feat: say what a cited check result required and found, from the returned data |
| `fd1fe79` | #23 | 2026-10-02 | fix: say no more than the record holds on the first-check path |
| `c356e33` | #23 | 2026-10-02 | fix: the source notices say which kinds evidence may be, not which a page has |
| `d6f89c1` | #26 | 2026-10-03 | feat: read a workspace's real check, and its comparison, in the Doctor |
| `70198bb` | #27 | 2026-10-03 | fix: correct four C2 workspace sentences before the manager walk |
| `92d788d` | #27 | 2026-10-03 | fix: name the wall an air terminal sits in, not an external wall |
| `82aa943` | #31 | 2026-10-03 | fix: close the manager-walk misreadings on the workspace pages |
| `7227110` | #31 | 2026-10-03 | fix: two readings the private walk found in the first commit |
| `39ae8ba` | #33 | 2026-10-03 | feat: an English home, example directory and first-check result |
| `50d129b` | #34 | 2026-10-03 | feat: English item and recheck pages, and counts that agree in number |
| `2934b01` | #36 | 2026-10-03 | feat: English workspace pages, with the Chinese ones unchanged to the character |
| `295da77` | #40 | 2026-10-04 | fix: say the same thing to do in both languages |

`PR` 一列是该提交所在的、最早合并进 main 的合并提交（`git log --merges --ancestry-path`）。
