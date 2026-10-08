# Doctor 页首来源提示“摘要＋展开”：中英义务对照（Q2）

日期：2026-10-08。负责：Product/UI Engineer。基线 `7b93ba5`，分支 `feat/doctor-source-summary`。
依据：[PM 对技术总监汇报（四）的回复](2026-10-08-pm-response-to-td-4.md) Q2；格式参照
[行动义务对照](2026-10-04-doctor-bilingual-action-parity.md)。
状态：下列新句子**全部未经 BIM 复核**，按 PM 安排进 10/15 增量复核，不进今日 C2 必审范围。

“同一义务”的判断标准：两种语言要求读者做的事、承诺或否认的事、限定的范围相同；措辞、语序、标点不同不算。

## 结论

新增 12 条（`SOURCE_SUMMARY` 11 条、`DIRECTORY.exampleIntro` 1 条），两种语言义务全部相同。原来的 `DEMO_NOTICE` 一字未改，
从页首常显的黄条变成摘要展开后的全文。没有删去任何一句已有的话。

## 一、页首摘要（每个模拟示例页，折叠外常显）

摘要 = `lead` ＋ `cites`（或 `citesNone`／`noRecord`）＋ 展开链接 `more`。

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `lead` | 随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 | A simulated example shipped with the tool, not your model; project settings such as teams are for demonstration, not for formal project decisions. | 同一义务：说明这是随附示例而不是自己的模型；项目设定是演示用；不能用于正式项目决定。 |
| `cites` | 这份记录的结论引用了：{kinds}，逐条标在结论旁的“依据”一行。 | This record's conclusions cite {kinds}, labelled citation by citation on the "Basis" line beside each conclusion. | 同一义务：只陈述**这一份记录**实际引用的来源种类，并指向结论旁的逐条标注。 |
| `citesNone` | 这份记录的结论没有引用证据。 | This record's conclusions cite no evidence. | 同一义务。随附的 12 份记录都有引用，这一句目前不会出现。 |
| `noRecord` | 结论引用的证据是真实的还是模拟的，逐条标在结论旁的“依据”一行。 | Whether the evidence a conclusion cites is real or simulated is labelled citation by citation on the "Basis" line beside it. | 同一义务：没有打开记录的页面（示例目录、拒绝页）不断言任何来源种类，只说在哪里看。 |
| `kinds.finding-real` | 真实检查输出 | real check output | 同一义务；与结论旁标签 `CITATION_PROVENANCE.finding-real.short` 同词（测试核对中文逐字相同） |
| `kinds.finding-fixture` | 模拟的检查结果 | simulated check results | 同上 |
| `kinds.determination-fixture` | 模拟的人工判定 | simulated human determinations | 同上 |
| `kinds.determination-unmarked` | 来源未标注的判定 | determinations of unstated source | 同上；既不说真实也不说模拟 |
| `join` | `、` | `, ` | 列举分隔符 |
| `lastJoin` | `、` | ` and ` | 列举的最后一个分隔符 |
| `more` | 来源说明 | About the sources | 同一义务：展开后是原 `DEMO_NOTICE` 全文 |

### `{kinds}` 怎么来，为什么不是“全部真实／全部模拟”

`{kinds}` 只列这份记录的引用里**实际出现**的种类，按固定顺序（真实检查输出、模拟的检查结果、模拟的人工判定、来源未标注的判定）。
每条引用的种类由它自己是否带模拟标记决定，和结论旁“依据”一行同一个函数（`citationProvenance`）；整页、整份记录、
模式都不参与判定。引用的收集（`recordCitations`）遍历整份记录：首次检查的读数、复检前后的读数、证据延续行的两侧；
`context_citations` 是节点上参考的上下文，不是结论的依据，不计入。

实测（随附 12 份记录）：

- 4 份（`member-evidence`、`pair-verdicts`、`recheck-comparison`、`recheck-prior-without-basis`）：真实检查输出、模拟的人工判定；
- 8 份（其余复检记录）：真实检查输出、模拟的检查结果、模拟的人工判定；
- 12 份全部是混合来源，任何一个整份记录的词（“全部真实”或“全部模拟”）都不对；没有一份引用“来源未标注的判定”。

测试 `SourceSummaryTests` 用另一种方法（不经界面的遍历，直接找记录里所有带模拟标记的引用）核对没有一条模拟引用被漏掉；
人为去掉证据延续行那一支，这个测试即在多份复检记录上失败（已还原）。

## 二、展开项（折叠内）

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `DEMO_NOTICE` | 未改 | 未改 | 与改前相同（2026-10-03 起的同一义务；英文见[英文词表](2026-10-03-doctor-english-vocabulary.md)） |

来源细节（项目设定具体包括什么、三种证据各是什么、不能导出正式检查记录）都在这一句里，现在放进展开项。

## 三、留在结论旁、没有进折叠的限制

这些句子本轮**没有改动**，列出来是为了说明：影响结论读法的限制仍在结论旁，不是只在折叠里。

| 页面 | 结论旁的内容 | 中文 | English |
| --- | --- | --- | --- |
| 首次结果单项、列表卡片 | 这个结论的依据（逐条来源标签） | `BASIS_WORDS.simulated`／`real`：这个结论建立在模拟证据上：／这个结论的依据： | This conclusion rests on simulated evidence: / Basis of this conclusion: |
| 首次结果单项 | “无法判断”的读法 | `BESIDE.unknown` | 同一义务（10/4 已对照） |
| 首次结果单项 | “可以开始”的范围 | `BESIDE.readyScope` | 同一义务 |
| 行动区 | 处理团队是示例的 | `BESIDE.simulatedTeam`：示例处理团队 | Example handling team |
| 复检单项 | 同组共用依据，其中有模拟证据 | `BASIS_WORDS.sharedSimulated` | Basis shared by the items in this group, some of it simulated |
| 复检单项 | 结论变化不说明原问题怎样了 | 复检变化组的说明（`changed.note`） | 同一义务 |

“FAIL 不等于原项目缺陷”一类的读法限制属于自己模型的检查结果（工作区、本地检查），那些页面本轮不改，句子仍在结果旁。

## 四、示例目录的简介

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `DIRECTORY.exampleIntro` | 每个示例是一份检查记录。 | Each example is one check record. | 同一义务。补回 #44 删去的 `DIRECTORY_NOTE` 中唯一没有在别处说过的一句；整段不恢复。 |

## 五、没有改的

- 工作区（自己模型的真实检查）各页：中文逐字不变（证明见 PR 描述）。
- 本地 IFC 检查各页、首页、随附项目的检查尝试页：不显示这条提示，未改。
- 字号、行高未改；摘要用正文字号，只有 `lead` 加粗。
