# 拟公开路线的 BIM 待审子集

日期：2026-10-09（新加坡）。负责：README 会话。基线：`origin/main` = `62a63697f7701a4340be3354885dc800582b4e70`（含 #49、#50、#52）。状态：**清单，不是复核**；本文件不判断任何条目的含义对错，不改任何词条。

依据：技术总监 10/9 的任务，出自 PM 的[简历版本与 UI 优化任务书](2026-10-08-pm-resume-release-ui-brief.md)第 5 节；档次沿用技术总监的顺序“C2 和公开主路径必需 → 本地 IFC → 其余”。在 D6 索引（[总览](2026-10-05-bim-batch-index.md)，基线 `d59dee0`）的基础上，补入 #29（本地 IFC）、#48（Q2）、#50（M1 等）之后的增量。CSV 是全表，含每条的页面与上下文：[`2026-10-09-bim-review-subset-public-route.csv`](2026-10-09-bim-review-subset-public-route.csv)。

## 1. 每档多少条

先是每档的完整状态分布；各状态相加等于档内总条数（最后一列是校验）。状态的含义见第 9 节第 5 条：**待核**＝改句需重核、新增未核、B 层未核、10/15 批未核、其他；其余几种不需要现在再审。

| 档 | 10/8 已核 | 10/8 后改句，需重核 | 10/8 已核；C 通道待裁 | 新增，未核 | B 层，10/8 未核 | 10/15 批，未核 | 同句已核 | 分隔符，无需判断 | D6 未列，待 BIM 确认 | 其他 | 合计 | 校验 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| T1 示例主线与 C2 必需 | 214 | 11 | 1 | 17 | 74 | 118 | 3 | 0 | 8 | 0 | **446** | 446 |
| T2 本地 IFC 与第二入口 | 2 | 1 | 0 | 68 | 1 | 16 | 2 | 0 | 0 | 0 | **90** | 90 |
| T3 其余 | 13 | 5 | 1 | 2 | 7 | 21 | 0 | 2 | 1 | 0 | **52** | 52 |
| **合计（子集）** | 229 | 17 | 2 | 87 | 82 | 155 | 5 | 2 | 9 | 0 | **588** | 588 |

再看待核与去重：

| 档 | 条目 | **待核** | 待核·去重句数 | 档内全部·去重句数 | 其中公开路线上不出现（条件出现） | D6 未列、待确认（单列，不在待核里） |
|---|---:|---:|---:|---:|---:|---:|
| T1 示例主线与 C2 必需 | 446 | **220** | 211 | 421 | 37 | 8 |
| T2 本地 IFC 与第二入口 | 90 | **86** | 86 | 88 | 10 | 0 |
| T3 其余 | 52 | **35** | 35 | 52 | 11 | 1 |
| **合计（子集）** | **588** | **341** | 332 | 561 | 58 | 9 |

**去重怎么算**：按（中文原句，英文原句）这一对去重，同一句出现在几个键下只算一次；只有中文的条目按中文句。去重只用来估工作量，不改变条目数。CSV 的 `reuse_en`／`reuse_zh` 列标了重复的组。

按“从末尾往前砍”累计的待核量：

| 做到哪一档 | 待核条目 | 待核·去重 |
|---|---:|---:|
| 只做 T1 | 220 | 211 |
| 做到 T2 | 306 | 297 |
| 全做（T3） | 341 | 332 |

**那 11 条中文单语释义**（`REASON_GLOSSES` 4 条、`IFC_CLASS_NAMES` 6 条、`CITATION_GLOSSES` 1 条；英文页显示原文）已按页面归档，计入总数：T1 10、T2 0、T3 1。它们的状态：1 条是 W10 改过的（计入待核）；1 条 D6 索引已列且 10/8 已核（`REASON_GLOSSES` 里的 E565，不在待核里）；9 条是“是否已核待 BIM 确认”（D6 索引当时没有逐条列），**不计入待核数**，单列在上表最后一列。10/8 BIM 读过 `REASON_GLOSSES`（W10 出自它），但哪几条已核我没有记录。
**英文页上的事实**：渲染的 369 个英文页里，这 11 条中文释义有 0 条出现；英文页显示的是记录或规则的英文原文，没有中文释义。英文页上没有任何别的中文字符（语言切换按钮上的“中文”除外）。（这是事实记录，本 PR 不修。）

不进子集（X）：117 条，原因见第 8 节；它们在公开路线上渲染不到、也不被本地结果页的代码引用，不计入上表。

条数不能代表复核时间：长句、含限制和否定的句子比标签慢得多。BIM 的可用时间还没有确认，这里不估工时。#50 改过的句子（第 4 节）和 Q2 的 12 条最短、也最该先看。

## 2. 某一档审不完，公开版本会缺什么

下面是事实，不是建议；取舍由 TD／PM 定。

- **T3 审不完**：目录里其余示例的页面（中文 138 页）和每份记录的“记录／活动／成员”明细页（中文 299 页，英文都是“尚未翻译”）上的文字没有复核。这些页面都是从公开页上的链接点得到的。要么复核，要么公开版本不链接、或在链接处标明未复核（任务书 §5 的“英文未译的次要链接仍提前注明”）。T3 里还有只在特定条件下出现的句子（指定工作区时的首页状态、没有证据可引用时的摘要等），公开路线默认不出现。
- **T2 审不完**：本地 IFC 检查（#/local 各页和结果页里 #29 的句子）与首页第二入口的拒绝页上的文字没有复核。这两条路径的文字就是它们的主体；按任务书 §5，没有复核的文字不进公开展示，所以这两个入口要么复核完，要么不公开。
- **T1 审不完**：示例主线（首页、目录、首次结果、单项、复检）与工作区结果页没有复核，没有可展示的路线。T1 不可砍。

## 3. 渲染了哪些页面

页面是真的渲染出来的：用 `2e6eafc` 这棵树起默认的 `python doctor/serve.py`（#52 之后只多了首页的一句 `HOME.recommended`，所以首页按 `62a6369` 重读，其余页面按 `2e6eafc`）（带一个临时的 `--checks-dir`），在无头 Edge 里按中文和英文各从首页起，沿页面上的链接广度遍历，并逐状态走完本地检查（见下）。读出每页的文字块，再按条目文字匹配。

| 页面种类 | 含什么 | 中文页数 | 英文页数 |
|---|---|---:|---:|
| 首页 | `#/` | 1 | 1 |
| 示例目录 | `#/fixture` | 1 | 1 |
| 示例主线 | `member-evidence`（首次结果、单项）、`recheck-requirement-relaxed`（复检、复检单项） | 43 | 43 |
| 本地结果页 | `#/local/<检查号>` 及其检查结果详情 | 16 | 16 |
| 本地检查（选文件至运行） | `#/local` 与本地检查各状态（见下） | 26 | 26 |
| 第二入口 | `#/real`、`#/real/real-refusal` | 2 | 2 |
| 其他示例 | 目录里其余示例的各页 | 138 | 138 |
| 次要明细页 | 记录、活动、成员明细页 | 299 | 142 |

本地检查按真实界面逐状态走了一遍（中英各一遍）：`check-architecture:planned`、`check-architecture:result`、`check-architecture:running`、`check-both:planned`、`check-both:result`、`check-both:running`、`check-garbled:after-run`、`check-garbled:planned`、`check-garbled:running`、`check-hvac:planned`、`check-hvac:result`、`check-hvac:running`、`check-mixed:planned`、`check-mixed:result`、`check-mixed:running`、`fresh:chosen-file-removed`、`fresh:file-refused-name-invalid`、`fresh:file-refused-too-large`、`fresh:plan-refused-no-model`、`fresh:plan-same-name-twice`、`fresh:same-name-twice-chosen`、`fresh:start-nothing-kept`、`local:chosen`、`local:file-refused-not-an-ifc`、`local:plan-refused-discipline-not-declared`、`local:plan-refused-unsupported-schema`、`local:result-missing`、`local:start`、`local:start-with-earlier-checks`。其中 `fresh:` 开头的几个状态是在记录目录为空、`--max-model-bytes 100000` 的第二个服务器上走的：首次访问（还没有任何记录）、选文件时被拒（文件太大、文件名不合规）、不选文件就确认范围、两个同名文件。输入是仓库里的公开样例 `Building-Hvac.ifc`、`Building-Architecture.ifc`，加三个小文件：一个 IFC2x3 头的、一个根本不是 IFC 的、一个文件头对但内容坏的（触发“程序故障”），以及把 HVAC 样例里一个类型改成 DIFFUSER 的变体（得到 PASS 与 FAIL 并存）。

## 4. M1 包（#50）改过的句子

按技术总监的指示，#50 已合并，这些句子按 `2e6eafc` 的新句子收进子集，状态是“10/8 后改句，需重核”，不再标“修正中”。10/8 已核的是改前原句。逐条中英对照见 [`2026-10-09-doctor-bim-batch-two-bilingual-parity.md`](2026-10-09-doctor-bim-batch-two-bilingual-parity.md)。

| ID | 键 | BIM 项 | 档 | 随附示例里出现 | 说明 |
|---|---|---|---|---|---|
| E014 | `ACTIONS.missing-project-asset-identity.recheck` | W2 | T1 | zh 36｜en 36 | W2：复检义务收窄到这个构件“在所列要求下都通过”，删去“范围内没有构件漏评”；#50 已改句（10/8 已核的是改前原句），需重核 |
| E017 | `ACTIONS.in-model-position-not-evaluated.action` | M1 | T1 | zh 34｜en 34 | M1：含义错误（P0）：断言“模型不需要改”，而空间归属尚未评估；中英同改；#50 已改句（10/8 已核的是改前原句），需重核 |
| E120 | `CONDITION_ENTRIES.no-recheck-condition.plain` | W4 | T1 | zh 50｜en 50 | W4：句子未变；#50 起只在原判断为“可以开始”时显示，需 BIM 确认 |
| E127 | `CONSEQUENCE_KINDS.work-suspended` | W8 | T1 | zh 73｜en 73 | W8：“暂停”暗示工作已经开始；#50 已改句（10/8 已核的是改前原句），需重核 |
| E145 | `DETAILS_WORDS.projectAssumption` | W7 | T1 | zh 36｜en 36 | W7：“约定”说重了；#50 已改句（10/8 已核的是改前原句），需重核 |
| Z01 | `REASON_GLOSSES.The required property set does not exist` | W10 | T1 | zh 36｜en 0 | W10：属性集的释义：改为可执行的说法（让导出写出属性集和其中要求的属性）；#50 已改句（10/8 已核的是改前原句），需重核 |
| E357 | `RULE_NOTES.PV-001.passProves` | W5 | T1 | zh 1｜en 1 | W5：实例层的 USERDEFINED 没写到；#50 已改句（10/8 已核的是改前原句），需重核 |
| E360 | `RULE_NOTES.PV-001.passDoesNotProve[2]` | W5 | T1 | zh 1｜en 1 | W5：实例层的 USERDEFINED 没写到；#50 已改句（10/8 已核的是改前原句），需重核 |
| E372 | `RULE_NOTES.PV-001.reasonFreeText` | W5 | T1 | zh 5｜en 5 | W5：实例层的 USERDEFINED 没写到；#50 已改句（10/8 已核的是改前原句），需重核 |
| E386 | `TAG_WORDS.note` | W6 | T1 | zh 6｜en 6 | W6：Tag 对不上时给的办法在 Revit 里做不到；#50 已改句（10/8 已核的是改前原句），需重核 |
| E025 | `ACTIONS.mep-element-not-spatially-assigned.action` | W3 | T3 | 不出现（随附 12 份示例记录没有触发） | W3：行动要求比规则严（“楼层和空间”对规则的“楼层或空间”）；#50 已改句（10/8 已核的是改前原句），需重核 |
| N01 | `CONDITION_ENTRIES.no-recheck-condition.plainNotReady` | W4 | T3 | 不出现（随附 12 份示例记录没有触发） | #50 新增（W4）：原判断不是“可以开始”或没有携带时显示，未核 |

没改的：

- **W1**（E021 `ACTIONS.missing-corresponding-opening.action`）：“在接收方模型里”：忠实表达 Pack 0.1.0 的路线；BIM 建议的改法会扩路线，按 C 通道，本轮不改。
- **W1**（E029 `ACTIONS.opening-not-verifiably-linked.action`）：同上。
- **W9**：Framework 有 CONDITIONAL，界面上没有它的标签和定义；公开样例、工作区与本地检查都不产出它，本轮没有可达入口，所以没有条目。`READING_GUIDE` 里“三个判断词”的说法因此仍成立。

## 5. 重复使用的句子

子集内有 46 组句子在几个键下重复出现（CSV 的 `reuse_en`／`reuse_zh` 列标了组号 G###）。同组只需看一次；组里既有“10/8 已核”又有待核时，待核的那条通常是同一句的新位置。下面列出含待核条目的组：

| 组 | 条目 | 句子（中文） | 状态 |
|---|---|---|---|
| G002 | E096、E476 | 检查程序 | 10/15 批，未核、10/8 已核 |
| G003 | E100、Q05 | 真实检查输出 | 10/8 已核、新增，未核 |
| G005 | E103、Q06 | 模拟的检查结果 | 10/8 已核、新增，未核 |
| G006 | E106、Q07 | 模拟的人工判定 | 10/8 已核、新增，未核 |
| G007 | E109、Q08 | 来源未标注的判定 | 10/8 已核、新增，未核 |
| G015 | E149、E154 | 仍在本次检查范围内；判断与条件另看 | 10/15 批，未核 |
| G016 | E150、E156 | 在重发模型中删除，不等于修复 | 10/15 批，未核 |
| G017 | E151、E158 | 已不属于此活动对象类别，不等于修复 | 10/15 批，未核 |
| G018 | E152、E160 | 这两个构件现在不再被配成一对来检查，不等于开洞已补 | 10/15 批，未核 |
| G019 | E153、E162 | 本次未声明该范围，不等于问题解除 | 10/15 批，未核 |
| G020 | E195、L008 | 给出整体合规、可施工或“可以交付”的结论 | 10/8 已核、新增，未核 |
| G023 | E239、E240 | 本次结果：共 {count} 个事项 | 10/15 批，未核 |
| G024 | E241、E242 | {count} 个事项 | 10/15 批，未核 |
| G025 | E245、E246 | {count} 个事项的结论和复检前不同： | 10/15 批，未核 |
| G026 | E248、E249 | {label}（{count} 个事项） | 10/15 批，未核 |
| G029 | E256、E257 | 复检前记录里的事项（{count} 个），现在的情况 | 10/15 批，未核 |
| G030 | E258、E259 | 复检前引用的旧证据（{count} 条），和本次记录比较的结果 | 10/15 批，未核 |
| G031 | E582、E284 | 二、要做什么、由谁处理、完成后拿什么复检 | B 层，10/8 未核 |
| G032 | E295、E296 | 和这一项放在一起评估的旧证据共 {count} 条 | B 层，10/8 未核 |
| G033 | E297、E298 | ，其中 {count} 条的检查要求变了 | B 层，10/8 未核 |
| G034 | E302、E303 | 记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 {count} 个事项共用下面这些行。 | B 层，10/8 未核 |
| G046 | E503、E504 | 两次结果相同的：{count} 条 | B 层，10/8 未核 |
| G048 | E508、E509 | {count} 条 | B 层，10/8 未核 |
| G052 | E574、E584 | 处理团队 | B 层，10/8 未核 |
| G053 | E589、E590 | {label}，按处理团队（{count} 个事项） | B 层，10/8 未核 |

中文逐字相同、英文不同的（没有按“同句已核”处理；英文差别是否算同义由 BIM 定）：

| 待核条目 | 英文 | 已核条目 | 英文 | 中文 |
|---|---|---|---|---|
| E096 | checker | E476 | Checkers | 检查程序 |
| L008 | Give an overall compliance, ready-to-build or "can be handed over" co… | E195 | Give an overall compliance, ready-to-build or "ready to hand over" co… | 给出整体合规、可施工或“可以交付”的结论 |
| Q05 | real check output | E100 | Real check output | 真实检查输出 |
| Q06 | simulated check results | E103 | Simulated check result | 模拟的检查结果 |
| Q07 | simulated human determinations | E106 | Simulated human determination | 模拟的人工判定 |
| Q08 | determinations of unstated source | E109 | Determination of unstated source | 来源未标注的判定 |

“同句已核”：句子与某条 10/8 已核且未改的条目逐字相同（中英都相同），不再列入待核。Q2 的 `kinds.*` 与 `CITATION_PROVENANCE.*.short` 中文逐字相同、英文只差大小写和单复数（见上表），所以没有按同句已核处理。

## 6. 没覆盖到的、没核验的

- **条件出现、本次没触发**：58 条在子集里，但本次渲染没看到它们（取决于用户自己的模型、拒绝或故障状态等）。CSV 的 `conditional` 列写了原因；它们的页面列为空。是否触发过，以“本地检查各状态”那一行为准。
- **英文未译的页面**：142 个路由在英文里显示“This page has not been translated yet”（记录、活动、成员明细页；每份记录各有若干个）。这些页面在英文里是死胡同，主线不经过它们；单项页上的“在明细页查看完整的证据路径”链接指向其中一个，英文里旁注“Chinese only”。
- **C2 工作区专用页**（对比页、拒绝页）不在公开路线上，没有渲染；这部分句子不进子集。C2 走查按 `577620e` 做过，之后这些页面的文字没有变。
- **UI 包 2（任务书 §3，10/10–12）**：首页和示例目录的措辞可能还会改。CSV 的 `ui_pkg2_watch` 标了只出现在首页／目录上的条目，它们的复核最好排在包 2 的措辞冻结之后。
- **本地检查的异常状态**：任务书 §3 要求走通的五个状态里，成功、没有适用对象、不支持 schema、运行失败（程序故障）都在界面里走通了；“无几何对象”在界面里没有单独的状态（没有形体的构件照常显示检查结果，页面只有一句静态说明 `scope.geometryText`）。Framework 待命补异常状态；如果补了，会有新句子，需要追加。
- **选了超过上限的文件时，页面没有显示“文件太大”的拒绝（L059），而是“没有收到服务器的回答：服务器可能已经停止”（L068）**：在 `--max-model-bytes 100000` 的服务器上选一个 179 KB 的文件，无头 Edge 里就是这样。服务器按文件大小拒绝时不读剩下的请求体并关闭连接（`doctor/serve.py` 的 `_local_post`），浏览器可能还在上传，就报网络错误。默认上限是 4 GB，只有超过它的文件会碰到。这是观察，不是结论，没有在其他浏览器里试；本 PR 不修。
- **匹配方法的限制**：条目靠文字匹配到页面。长句按固定文字的子串匹配；短标签只算整块或整个元素相等；极短的模板（如 `{label}：{meaning}。`）无法按文字找到，按所在表其余条目出现的页面继承（CSV 的 `inherited_pages` 列）。短标签按文字匹配，会把页面别处的同一个词也算进页数（例如 Q2 的 `kinds.*` 与图例里的同一个词），页数只是“出现过”的粗指标。一个词条只写在代码里、不在词表里的页面文字（词表测试保证这种情况不应有）不在本清单内。
- **与第一阶段（5b64b42，用 `0f4300b` 上渲染的页面）相比**：在 `2e6eafc` 上重新渲染后，爬到的页面数变化：en 示例主线 42→43；en 次要明细页 141→142。第一阶段之后 #52 新增了 H01（首页的“推荐从这里开始”），它不算在这次比较里。条目变化 6 条（原因是匹配方法，不是页面变了：中文单语释义现在按“和它注释的原文在同一页”匹配，第一阶段没有这条规则）：
- **没有私有内容**：渲染只用仓库里的公开样例和随附示例；没有用 C2 的私有工作区、模型或路径。

## 7. 清单

列：ID 沿用 D6 索引的 `E###`；`L###` 是 #29 的 76 条，`Q##` 是 #48 的 12 条，`N01` 是 #50 新增的一条，`H01` 是 #52 新增的一条（首页的“推荐从这里开始”），`C01` 是 #29 改了但 D6 索引没列的一条。页面列是“中文页数｜英文页数｜在哪些页面”。

### T1 示例主线与 C2 必需（446 条，待核 220）

#### ACTIVITY_NAMES（6 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E001 | `builders-work-openings.name` | Builder's-work openings | 土建预留开洞 | 10/8 已核 | zh 85｜en 85｜示例主线、其他示例 |
| E002 | `builders-work-openings.needs` | Needs to know where MEP penetrates architectural fabric, so openings can be cut in walls, floors and roof. | 要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。 | 10/8 已核 | zh 10｜en 10｜示例主线、其他示例 |
| E003 | `ceiling-and-bulkhead-geometry.name` | Reflected ceiling and bulkhead layout | 吊顶平面与包封布置 | 10/8 已核 | zh 70｜en 70｜示例主线、其他示例 |
| E004 | `ceiling-and-bulkhead-geometry.needs` | Needs to know where MEP equipment physically is, in which storey, so ceiling zones and bulkheads can be drawn around it. | 要知道交出方的设备在哪一层、在什么位置，才能围着它画吊顶分区和包封。 | 10/8 已核 | zh 8｜en 8｜示例主线、其他示例 |
| E005 | `schedules-and-room-data-sheets.name` | Room data sheets and equipment schedules | 房间数据表与设备明细表 | 10/8 已核 | zh 70｜en 70｜示例主线、其他示例 |
| E006 | `schedules-and-room-data-sheets.needs` | Needs each piece of equipment to carry the project's asset identity, so a schedule can be keyed to it. | 要每件设备都带有项目的资产标识，明细表才能按它编排。 | 10/8 已核 | zh 8｜en 8｜示例主线、其他示例 |

#### VERDICT_LABELS（3 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E007 | `READY` | Ready | 可以开始 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |
| E008 | `BLOCKED` | Blocked | 受阻 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |
| E009 | `UNKNOWN` | Unknown | 无法判断 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |

#### VERDICT_WORDS（3 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E010 | `READY` | Every piece of necessary evidence is present and satisfies the applicable acceptance conditions, and there is no unresolved blocker and no evidence gap. The activity can… | 必要的证据齐全且满足验收条件，没有未解决的阻碍，也没有证据缺口：在本次评估范围内，这项工作可以开始 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |
| E011 | `BLOCKED` | A known unmet requirement prevents the activity | 有一项已知未满足的要求，阻止这项工作 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |
| E012 | `UNKNOWN` | An evidence gap makes the activity undecidable — the evidence needed to answer the question was never produced, so neither release nor refusal can be justified | 回答这个问题所需的证据没有产生，这项工作能否开始无法决定：既不能放行，也不能拒绝 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |

#### ACTIONS（10 条，待核 2）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E013 | `missing-project-asset-identity.action` | In the source model, add to this element the asset-identity properties the project's convention requires (see the property sets and property names listed), then re-expor… | 在源模型里给这个构件补上本项目约定的资产标识属性（见所列属性集和属性名），重新导出 | 10/8 已核 | zh 50｜en 50｜示例主线、其他示例 |
| E014 | `missing-project-asset-identity.recheck` | On the reissued model, this element passes every requirement listed | 重新发布的模型上，这个构件在所列每条要求下都通过 | 10/8 后改句，需重核 | zh 36｜en 36｜示例主线、其他示例 |
| E015 | `asset-identity-not-evaluated.action` | The existing asset-identity rules do not reach this element, so whether it has an asset identity has not been evaluated, and it cannot be judged to be missing one; for t… | 现有资产标识规则没有覆盖到这个构件，所以它有没有资产标识还没有被评估，不能判断是否缺少；这项工作能否开始也因此无法判断。先确认项目约定是否要求它具备资产标识，以及规则该不该覆盖到它。在确认之前，这不表示它必须具备资产标… | 10/8 已核 | zh 34｜en 34｜示例主线、其他示例 |
| E016 | `asset-identity-not-evaluated.recheck` | Every element in the scope has an evaluation result under the requirements bound to it | 范围内每个构件在所绑定的要求下都有评估结果 | 10/8 已核 | zh 12｜en 12｜示例主线、其他示例 |
| E017 | `in-model-position-not-evaluated.action` | This is not a known model defect. Its spatial assignment has not been evaluated yet: the spatial-assignment check rules do not reach this element. This step is to extend… | 这不是已知的模型缺陷。它的空间归属目前还没有评估：空间归属的检查规则没有覆盖到这个构件。这一步是扩展规则的适用范围，让检查覆盖到它，而不是改模型；覆盖并运行之后，才知道要不要改模型 | 10/8 后改句，需重核 | zh 34｜en 34｜示例主线、其他示例 |
| E018 | `in-model-position-not-evaluated.recheck` | Every element in the scope has a check result under the requirements bound to it | 范围内每个构件在所绑定的要求下都有检查结果 | 10/8 已核 | zh 12｜en 12｜示例主线、其他示例 |
| E019 | `penetration-not-determined.action` | This is not a known model defect. No coordination review has yet determined whether it passes through the receiving side's elements; hold a review and record either “no… | 这不是已知的模型缺陷。还没有协调评审判定它是否穿过接收方的构件；需要开一次评审，记录“不穿过”或写明穿过哪些构件 | 10/8 已核 | zh 50｜en 50｜示例主线、其他示例 |
| E020 | `penetration-not-determined.recheck` | A recorded review determination exists for the model versions listed | 针对所列模型版本，有一份评审判定记录 | 10/8 已核 | zh 28｜en 28｜示例主线、其他示例 |
| E021 | `missing-corresponding-opening.action` | In the receiving side's model, model an opening or shaft in the element it passes through, not a void in the handing-over side's model. One opening for each element it p… | 在接收方模型里、被穿过的构件上建出洞口或竖井，不要做成交出方模型里的空洞。穿过几个构件就要几个洞口 | 10/8 已核；C 通道待裁（W1） | zh 19｜en 19｜示例主线、其他示例 |
| E022 | `missing-corresponding-opening.recheck` | The opening check for this pair reports “opening modelled and cross-referenced”. Modelling the opening alone is not enough | 这一对的开洞核查结果为“洞口已建且已关联”。只建洞不够 | 10/8 已核 | zh 13｜en 13｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E014` zh `#/fixture/member-evidence/item/2/2/0`：完成后拿什么复检 ‹ 重新发布的模型上，这个构件在所列每条要求下都通过 › 来源原文（英文，记录所带）：供追溯，不是操作指令；en `#/fixture/member-evidence/item/2/2/0`：What a recheck must show ‹ On the reissued model, this element passes every requirement listed › Source wording (as the record carries it): for tracing, not an instruc
- `E017` zh `#/fixture/member-evidence`：要做什么 ‹ 这不是已知的模型缺陷。它的空间归属目前还没有评估：空间归属的检查规则没有覆盖到这个构件。这一步是扩展规则的适用范围，让检查覆盖到它，而不是改模型；覆盖并运行之后，才知道要不要改模型 › 查看这一项；en `#/fixture/member-evidence`：What to do ‹ This is not a known model defect. Its spatial assignment has not been evaluated yet: the spatial-assignment ch › See this item

#### ACTION_GROUPS（6 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E033 | `open.label` | Items to deal with | 需要处理的事项 | 10/8 已核 | zh 0｜en 24｜示例主线、其他示例 |
| E034 | `open.summary` | the record gives an action | 记录给出了处理动作 | 10/8 已核 | zh 0｜en 20｜示例主线、其他示例 |
| E036 | `open.note` | Each item's page says which elements it involves, what to do, who deals with it and what a recheck must show. | 每个事项的页面写明涉及的构件、要做什么、由谁处理、完成后拿什么复检。 | 10/8 已核 | zh 18｜en 18｜示例主线、其他示例 |
| E041 | `none.label` | Items for which the record gives no follow-up action | 记录没有给出后续处理动作的事项 | 10/8 已核 | zh 14｜en 14｜示例主线、其他示例 |
| E042 | `none.summary` | the record gives no follow-up action | 记录没有给出后续处理动作 | 10/8 已核 | zh 14｜en 14｜示例主线、其他示例 |
| E044 | `none.note` | The record gives no follow-up action for the items below. Each line's conclusion stands on its own, with its scope beside it. | 记录没有为下面这些事项给出后续处理动作。每一行的结论各自成立，范围写在它旁边。 | 10/8 已核 | zh 14｜en 14｜示例主线、其他示例 |

#### ASPECT_NOTES（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E047 | `semanticsAndContent` | The check requirement was edited and the check result content changed too: the change in result may come from the edit to the requirement (for example a relaxed requirem… | 检查要求被修改过，检查结果内容也变了：结果的变化可能来自要求的修改（例如要求放宽），不能据此说模型修好了。记录不说明要求是放宽还是收紧。 | 10/15 批，未核 | zh 6｜en 6｜示例主线 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E047` zh `#/fixture/recheck-requirement-relaxed/recheck/7/0`：引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 ‹ 检查要求被修改过，检查结果内容也变了：结果的变化可能来自要求的修改（例如要求放宽），不能据此说模型修好了。记录不说明要求是放宽还是收紧。 › 追溯信息（记录原码与内容指纹）；en `#/fixture/recheck-requirement-relaxed/recheck/7/0`：The citation changed key (the new key is the "corresponding evidence t ‹ The check requirement was edited and the check result content changed too: the change in result may come from  › Tracing (record codes and content fingerprints)

#### BASIS_WORDS（6 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E051 | `simulated` | This conclusion rests on simulated evidence: | 这个结论建立在模拟证据上： | 10/8 已核 | zh 16｜en 16｜示例主线、其他示例 |
| E052 | `real` | Basis of this conclusion: | 这个结论的依据： | 10/8 已核 | zh 18｜en 18｜示例主线、其他示例 |
| E053 | `sharedSimulated` | Basis shared by the items in this group, some of it simulated: | 同组事项共用的依据，其中有模拟证据： | 10/8 已核 | zh 88｜en 88｜示例主线、其他示例 |
| E054 | `sharedReal` | Basis shared by the items in this group: | 同组事项共用的依据： | 10/8 已核 | zh 65｜en 65｜示例主线、其他示例 |
| E056 | `gaps.no-finding` | no check result at all (a real absence) | 没有任何检查结果（真实的缺席） | 10/8 已核 | zh 46｜en 46｜示例主线、其他示例 |
| E057 | `gaps.no-determination` | no determination yet (a real absence) | 还没有判定（真实的缺席） | 10/8 已核 | zh 64｜en 64｜示例主线、其他示例 |

#### BESIDE（7 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E059 | `readyScope` | Holds for this one item, this work and the listed model versions only; it does not mean the whole handover is complete. | 只对这一个事项、这项工作、所列的模型版本成立；不代表整次交接完成。 | 10/8 已核 | zh 54｜en 54｜示例主线、其他示例 |
| E060 | `unknown` | "Unknown" means whether this work can start cannot be decided: it does not mean the element has no problem, and it is not a system error. | “无法判断”说的是这项工作能否开始无法判断：不等于这个构件没有问题，也不是系统出错。 | 10/8 已核 | zh 88｜en 88｜示例主线、其他示例 |
| E061 | `assetIdentity` | Where the asset-identity value comes from, and which Revit parameter it maps to, the record does not say. | 资产标识的取值从哪里来、对应哪个 Revit 参数，记录未提供。 | 10/8 已核 | zh 6｜en 6｜示例主线、其他示例 |
| E062 | `team` | The handling team is an entry in the record; it does not mean the work has been assigned. | 处理团队是记录里的安排，不代表已经派发。 | 10/8 已核 | zh 107｜en 107｜示例主线、其他示例 |
| E063 | `simulatedTeam` | Example handling team | 示例处理团队 | 10/8 已核 | zh 107｜en 107｜示例主线、其他示例 |
| E065 | `defaultRole` | Default handling role (the rule's default, not an assignment) | 默认处理角色（规则给出的默认，不是指派） | 10/8 已核 | zh 107｜en 107｜示例主线、其他示例 |
| E066 | `unchanged` | Unchanged by the recheck | 复检前后未变 | 10/8 已核 | zh 0｜en 112｜示例主线、其他示例 |

#### CARRY_OVER_REASONS（14 条，待核 14）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E067 | `finding-equivalent` | There is exactly one corresponding check result; model version, check result content, check requirement and checker are the same, aspect by aspect. | 对应的检查结果只有一条，模型版本、检查结果内容、检查要求、检查程序逐项相同。 | 10/15 批，未核 | zh 50｜en 50｜示例主线、其他示例 |
| E068 | `finding-changed` | There is exactly one corresponding check result; compared aspect by aspect, at least one differs. | 对应的检查结果只有一条，逐项比较后至少有一个方面不同。 | 10/15 批，未核 | zh 53｜en 53｜示例主线、其他示例 |
| E069 | `no-counterpart-in-the-cited-run` | In the validation run this record rests on, this element has no check result under this requirement. | 本次记录依据的验证运行里，这个构件在这条要求下没有检查结果。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E070 | `counterpart-not-cited-under-the-current-binding` | The validation run has a corresponding check result, but this record does not cite it. | 验证运行里有对应的检查结果，但本次记录没有引用它。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E071 | `sealed-citation-has-no-comparison-basis` | When the original record was sealed it kept no comparison basis for this citation (a record from an older version). This page will not make one up from the current rules… | 原记录封存时没有保存这条引用的比较依据（旧版本的记录）。本页不会用当前规则去补造，所以只能如实显示无法比较。 | 10/15 批，未核 | zh 26｜en 26｜示例主线、其他示例 |
| E072 | `comparison-basis-version-unknown` | The comparison basis the original record kept is of a version this system does not recognise. | 原记录保存的比较依据，是本系统不认识的版本。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E073 | `subject-not-present` | The element this evidence is about is no longer in this record (where it went: see "the reason the record gives"). An element that is gone is not fixed. | 这条证据所针对的构件，在本次记录里已经不在（去向见“记录给出的原因”）。构件不在不等于已修复。 | 10/15 批，未核 | zh 26｜en 26｜示例主线、其他示例 |
| E074 | `counterpart-not-unique` | This time there is more than one candidate corresponding check result, and the system does not choose between them (all candidates: see "the reason the record gives"). | 本次有不止一条候选的对应检查结果，系统不从中挑选（全部候选见“记录给出的原因”）。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E075 | `requirement-semantics-basis-unavailable` | The sealed side or the current side has no comparison basis for the check requirement. | 封存一方或当前一方没有“检查要求”的比较依据。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E076 | `comparison-basis-incomplete` | The sealed side or the current side lacks part of the comparison basis (model version, check result content digest or checker fingerprint). | 封存一方或当前一方缺少部分比较依据（模型版本、检查结果内容摘要或检查程序指纹）。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E077 | `determination-same-reference-same-content` | The same determination: the same reference and the same content digest. | 同一份判定：引用相同，内容摘要也相同。 | 10/15 批，未核 | zh 50｜en 50｜示例主线、其他示例 |
| E078 | `determination-content-changed-under-the-same-reference` | The same reference, but the determination's content is no longer what the original record read (made again, re-attributed or re-signed). The new determination is read as… | 引用相同，但判定的内容已经不是原记录读到的那一份（被重新作出、重新归属或重新签署）。新判定照常作为证据读取，只是不能说它和原判定是同一份。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E079 | `determination-not-cited-by-this-record` | The model version did not change, and this record no longer cites this determination: another determination replaced it. | 模型版本没有变，本次记录没有再引用这份判定：它被别的判定取代了。 | 10/15 批，未核 | zh 21｜en 21｜示例主线、其他示例 |
| E080 | `determination-not-attributable-to-this-context` | The model version has changed, and the original determination was made against the old version, so it cannot be attributed to the current one. The evidence is not missin… | 模型版本已经变化，原判定是针对旧版本作出的，不能归到当前版本。不是证据不存在，也不是原判定错误；需要针对当前版本的判定。 | 10/15 批，未核 | zh 50｜en 50｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E067` zh `#/fixture/recheck-requirement-relaxed`：finding-equivalent ‹ 对应的检查结果只有一条，模型版本、检查结果内容、检查要求、检查程序逐项相同。 › finding-changed；en `#/fixture/recheck-requirement-relaxed`：finding-equivalent ‹ There is exactly one corresponding check result; model version, check result content, check requirement and ch › finding-changed
- `E068` zh `#/fixture/recheck-requirement-relaxed`：finding-changed ‹ 对应的检查结果只有一条，逐项比较后至少有一个方面不同。 › no-counterpart-in-the-cited-run；en `#/fixture/recheck-requirement-relaxed`：finding-changed ‹ There is exactly one corresponding check result; compared aspect by aspect, at least one differs. › no-counterpart-in-the-cited-run
- `E069` zh `#/fixture/recheck-requirement-relaxed`：no-counterpart-in-the-cited-run ‹ 本次记录依据的验证运行里，这个构件在这条要求下没有检查结果。 › counterpart-not-cited-under-the-current-binding；en `#/fixture/recheck-requirement-relaxed`：no-counterpart-in-the-cited-run ‹ In the validation run this record rests on, this element has no check result under this requirement. › counterpart-not-cited-under-the-current-binding
- `E070` zh `#/fixture/recheck-requirement-relaxed`：counterpart-not-cited-under-the-current-binding ‹ 验证运行里有对应的检查结果，但本次记录没有引用它。 › sealed-citation-has-no-comparison-basis；en `#/fixture/recheck-requirement-relaxed`：counterpart-not-cited-under-the-current-binding ‹ The validation run has a corresponding check result, but this record does not cite it. › sealed-citation-has-no-comparison-basis
- `E071` zh `#/fixture/recheck-requirement-relaxed`：sealed-citation-has-no-comparison-basis ‹ 原记录封存时没有保存这条引用的比较依据（旧版本的记录）。本页不会用当前规则去补造，所以只能如实显示无法比较。 › comparison-basis-version-unknown；en `#/fixture/recheck-requirement-relaxed`：sealed-citation-has-no-comparison-basis ‹ When the original record was sealed it kept no comparison basis for this citation (a record from an older vers › comparison-basis-version-unknown
- `E072` zh `#/fixture/recheck-requirement-relaxed`：comparison-basis-version-unknown ‹ 原记录保存的比较依据，是本系统不认识的版本。 › subject-not-present；en `#/fixture/recheck-requirement-relaxed`：comparison-basis-version-unknown ‹ The comparison basis the original record kept is of a version this system does not recognise. › subject-not-present
- `E073` zh `#/fixture/recheck-requirement-relaxed`：subject-not-present ‹ 这条证据所针对的构件，在本次记录里已经不在（去向见“记录给出的原因”）。构件不在不等于已修复。 › counterpart-not-unique；en `#/fixture/recheck-requirement-relaxed`：subject-not-present ‹ The element this evidence is about is no longer in this record (where it went: see "the reason the record give › counterpart-not-unique
- `E074` zh `#/fixture/recheck-requirement-relaxed`：counterpart-not-unique ‹ 本次有不止一条候选的对应检查结果，系统不从中挑选（全部候选见“记录给出的原因”）。 › requirement-semantics-basis-unavailable；en `#/fixture/recheck-requirement-relaxed`：counterpart-not-unique ‹ This time there is more than one candidate corresponding check result, and the system does not choose between  › requirement-semantics-basis-unavailable
- `E075` zh `#/fixture/recheck-requirement-relaxed`：requirement-semantics-basis-unavailable ‹ 封存一方或当前一方没有“检查要求”的比较依据。 › comparison-basis-incomplete；en `#/fixture/recheck-requirement-relaxed`：requirement-semantics-basis-unavailable ‹ The sealed side or the current side has no comparison basis for the check requirement. › comparison-basis-incomplete
- `E076` zh `#/fixture/recheck-requirement-relaxed`：comparison-basis-incomplete ‹ 封存一方或当前一方缺少部分比较依据（模型版本、检查结果内容摘要或检查程序指纹）。 › determination-same-reference-same-content；en `#/fixture/recheck-requirement-relaxed`：comparison-basis-incomplete ‹ The sealed side or the current side lacks part of the comparison basis (model version, check result content di › determination-same-reference-same-content
- `E077` zh `#/fixture/recheck-requirement-relaxed`：比较依据一致 × 6 ‹ 同一份判定：引用相同，内容摘要也相同。 × 6 › “比较依据一致”是什么意思；en `#/fixture/recheck-requirement-relaxed`：Comparison basis unchanged × 6 ‹ The same determination: the same reference and the same content digest. × 6 › What "Comparison basis unchanged" means
- `E078` zh `#/fixture/recheck-requirement-relaxed`：determination-content-changed-under-the-same-reference ‹ 引用相同，但判定的内容已经不是原记录读到的那一份（被重新作出、重新归属或重新签署）。新判定照常作为证据读取，只是不能说它和原判定是同一份。 › determination-not-cited-by-this-record；en `#/fixture/recheck-requirement-relaxed`：determination-content-changed-under-the-same-reference ‹ The same reference, but the determination's content is no longer what the original record read (made again, re › determination-not-cited-by-this-record
- `E079` zh `#/fixture/recheck-requirement-relaxed`：determination-not-cited-by-this-record ‹ 模型版本没有变，本次记录没有再引用这份判定：它被别的判定取代了。 › determination-not-attributable-to-this-context；en `#/fixture/recheck-requirement-relaxed`：determination-not-cited-by-this-record ‹ The model version did not change, and this record no longer cites this determination: another determination re › determination-not-attributable-to-this-context
- `E080` zh `#/fixture/recheck-requirement-relaxed`：determination-not-attributable-to-this-context ‹ 模型版本已经变化，原判定是针对旧版本作出的，不能归到当前版本。不是证据不存在，也不是原判定错误；需要针对当前版本的判定。 › 变化方面：原码；en `#/fixture/recheck-requirement-relaxed`：determination-not-attributable-to-this-context ‹ The model version has changed, and the original determination was made against the old version, so it cannot b › Aspects that changed: codes

#### CARRY_OVER_STATES（8 条，待核 8）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E081 | `equivalent.label` | Comparison basis unchanged | 比较依据一致 | 10/15 批，未核 | zh 68｜en 151｜示例主线、其他示例 |
| E082 | `equivalent.meaning` | This old evidence has exactly one counterpart in this record, and every aspect compared is the same. | 这条旧证据在本次记录里有唯一对应的一条，逐项比较都相同。 | 10/15 批，未核 | zh 58｜en 58｜示例主线、其他示例 |
| E083 | `equivalent.caveat` | It only means the evidence need not be gathered again because its citation changed key; it does not mean the whole handover needs no review. | 这只说明不必因为引用换了键而重新收集这条证据，不代表整个交接不用复核。 | 10/15 批，未核 | zh 58｜en 58｜示例主线、其他示例 |
| E084 | `changed.label` | Comparison basis changed | 比较依据有变化 | 10/15 批，未核 | zh 53｜en 53｜示例主线、其他示例 |
| E085 | `changed.meaning` | This old evidence has exactly one counterpart in this record, but at least one aspect differs. | 这条旧证据在本次记录里有唯一对应的一条，但至少有一个方面不同。 | 10/15 批，未核 | zh 45｜en 45｜示例主线、其他示例 |
| E086 | `changed.caveat` | Even if the result reads the same, it still counts as changed; which aspects changed is said on the row. | 结果读起来相同，也仍然算有变化；变了的是哪些方面，见这一条的说明。 | 10/15 批，未核 | zh 45｜en 45｜示例主线、其他示例 |
| E087 | `no-counterpart.label` | No counterpart found | 未找到对应证据 | 10/15 批，未核 | zh 51｜en 51｜示例主线、其他示例 |
| E090 | `not-provable.label` | Not enough basis to compare | 现有依据不足以比较 | 10/15 批，未核 | zh 32｜en 32｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E081` zh `#/fixture/recheck-requirement-relaxed`：读复检结果时 ‹ “比较依据一致”不代表整个交接不用复核。 › 构件不在了、或找不到对应证据，不代表问题已修复。；en `#/fixture/recheck-requirement-relaxed`：When reading a recheck result ‹ "Comparison basis unchanged" does not mean the whole handover needs no review. › An element that is gone, or evidence with no counterpart, does not mea
- `E082` zh `#/fixture/recheck-requirement-relaxed`：“比较依据一致”是什么意思 ‹ 这条旧证据在本次记录里有唯一对应的一条，逐项比较都相同。这只说明不必因为引用换了键而重新收集这条证据，不代表整个交接不用复核。 › “比较依据有变化”是什么意思；en `#/fixture/recheck-requirement-relaxed`：What "Comparison basis unchanged" means ‹ This old evidence has exactly one counterpart in this record, and every aspect compared is the same. It only m › What "Comparison basis changed" means
- `E083` zh `#/fixture/recheck-requirement-relaxed`：“比较依据一致”是什么意思 ‹ 这条旧证据在本次记录里有唯一对应的一条，逐项比较都相同。这只说明不必因为引用换了键而重新收集这条证据，不代表整个交接不用复核。 › “比较依据有变化”是什么意思；en `#/fixture/recheck-requirement-relaxed`：What "Comparison basis unchanged" means ‹ This old evidence has exactly one counterpart in this record, and every aspect compared is the same. It only m › What "Comparison basis changed" means
- `E084` zh `#/fixture/recheck-requirement-relaxed`：只是引用换了键 × 7 ‹ 比较依据有变化 × 2 › 检查结果内容、检查要求变了，模型版本、检查程序未变。 × 2；en `#/fixture/recheck-requirement-relaxed`：Only the citation's key changed × 7 ‹ Comparison basis changed × 2 › check result content, check requirement changed; model version, checke
- `E085` zh `#/fixture/recheck-requirement-relaxed`：“比较依据有变化”是什么意思 ‹ 这条旧证据在本次记录里有唯一对应的一条，但至少有一个方面不同。结果读起来相同，也仍然算有变化；变了的是哪些方面，见这一条的说明。 › 追溯信息：记录标识、模型版本指纹、记录原码对照；en `#/fixture/recheck-requirement-relaxed`：What "Comparison basis changed" means ‹ This old evidence has exactly one counterpart in this record, but at least one aspect differs. Even if the res › Tracing: record identity, model version fingerprints, record codes
- `E086` zh `#/fixture/recheck-requirement-relaxed`：“比较依据有变化”是什么意思 ‹ 这条旧证据在本次记录里有唯一对应的一条，但至少有一个方面不同。结果读起来相同，也仍然算有变化；变了的是哪些方面，见这一条的说明。 › 追溯信息：记录标识、模型版本指纹、记录原码对照；en `#/fixture/recheck-requirement-relaxed`：What "Comparison basis changed" means ‹ This old evidence has exactly one counterpart in this record, but at least one aspect differs. Even if the res › Tracing: record identity, model version fingerprints, record codes
- `E087` zh `#/fixture/recheck-requirement-relaxed`：no-counterpart ‹ 未找到对应证据 › not-provable；en `#/fixture/recheck-requirement-relaxed`：no-counterpart ‹ No counterpart found › not-provable
- `E090` zh `#/fixture/recheck-requirement-relaxed`：not-provable ‹ 现有依据不足以比较 › 旧证据比较：原因原码；en `#/fixture/recheck-requirement-relaxed`：not-provable ‹ Not enough basis to compare › Old-evidence comparison: reason codes

#### CHANGED_ASPECTS（4 条，待核 4）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E093 | `model-version` | model version | 模型版本 | 10/15 批，未核 | zh 179｜en 182｜示例目录、示例主线、其他示例、次要明细页 |
| E094 | `finding-content` | check result content | 检查结果内容 | 10/15 批，未核 | zh 20｜en 74｜示例主线、其他示例 |
| E095 | `requirement-semantics` | check requirement | 检查要求 | 10/15 批，未核 | zh 20｜en 75｜示例目录、示例主线、其他示例 |
| E096 | `checker` | checker | 检查程序 | 10/15 批，未核 | zh 36｜en 20｜示例主线、本地结果页、其他示例；复用 G002 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E093` zh `#/fixture/recheck-requirement-relaxed`：同组事项共用的依据，其中有模拟证据：模拟的检查结果 ×2 ‹ 只对这一个事项、这项工作、所列的模型版本成立；不代表整次交接完成。 › 记录同时显示：和这一项放在一起评估的旧证据里，有 2 条的检查要求变了；记录不说明是放宽还是收紧。读这个结论时要一并看，逐条见“复检前的证据；en `#/fixture`：The same record after a recheck: neither model was re-issued, yet a co ‹ About this example This example was given: one cited check requirement was relaxed; neither the handing-over n › Open this example's result
- `E094` zh `#/fixture/recheck-requirement-relaxed`：比较依据有变化 × 2 ‹ 检查结果内容、检查要求变了，模型版本、检查程序未变。 × 2 › 判定引用（6 条）；en `#/fixture/recheck-requirement-relaxed`：Comparison basis changed × 2 ‹ check result content, check requirement changed; model version, checker unchanged. × 2 › Determination citation (6 rows)
- `E095` zh `#/fixture/recheck-requirement-relaxed`：只对这一个事项、这项工作、所列的模型版本成立；不代表整次交接完成。 ‹ 记录同时显示：和这一项放在一起评估的旧证据里，有 2 条的检查要求变了；记录不说明是放宽还是收紧。读这个结论时要一并看，逐条见“复检前的证据”。 › 两侧模型都没有重新发布，这些项的判断却变了：变化不来自模型改动。每一项的旧证据写明变了的是什么。；en `#/fixture`：The same record after a recheck: neither model was re-issued, yet a co ‹ About this example This example was given: one cited check requirement was relaxed; neither the handing-over n › Open this example's result
- `E096` zh `#/fixture/recheck-requirement-relaxed`：比较依据有变化 × 2 ‹ 检查结果内容、检查要求变了，模型版本、检查程序未变。 × 2 › 判定引用（6 条）；en `#/fixture/recheck-requirement-relaxed`：Comparison basis changed × 2 ‹ check result content, check requirement changed; model version, checker unchanged. × 2 › Determination citation (6 rows)

#### CITATION_KINDS（2 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E097 | `finding` | Check-result citation | 检查结果引用 | 10/8 已核 | zh 0｜en 78｜示例主线、其他示例 |
| E098 | `determination` | Determination citation | 判定引用 | 10/8 已核 | zh 0｜en 81｜示例主线、其他示例 |

#### CITATION_PROVENANCE（8 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E100 | `finding-real.short` | Real check output | 真实检查输出 | 10/8 已核 | zh 468｜en 181｜示例主线、其他示例、次要明细页；复用 G003 |
| E101 | `finding-real.long` | A check-result citation without the simulation marker: from a real check run, the product of checking a real IFC model against real rules. | 未带模拟标记的检查结果引用：来自真实的检查运行，是真实 IFC 模型按真实规则检查的产物。 | 10/8 已核 | zh 468｜en 181｜示例主线、其他示例、次要明细页 |
| E103 | `finding-fixture.short` | Simulated check result | 模拟的检查结果 | 10/8 已核 | zh 468｜en 181｜示例主线、其他示例、次要明细页；复用 G005 |
| E104 | `finding-fixture.long` | A check-result citation with the simulation marker (starting with fixture): generated by the example, not the output of any real check run. | 带模拟标记（以 fixture 开头）的检查结果引用：由示例生成，不是任何真实检查运行的输出。 | 10/8 已核 | zh 468｜en 181｜示例主线、其他示例、次要明细页 |
| E106 | `determination-fixture.short` | Simulated human determination | 模拟的人工判定 | 10/8 已核 | zh 468｜en 181｜示例主线、其他示例、次要明细页；复用 G006 |
| E107 | `determination-fixture.long` | A determination citation with the simulation marker: supplied by the example; no coordination review ever took place. | 带模拟标记的判定引用：由示例提供，没有任何协调评审真的发生过。 | 10/8 已核 | zh 468｜en 181｜示例主线、其他示例、次要明细页 |
| E109 | `determination-unmarked.short` | Determination of unstated source | 来源未标注的判定 | 10/8 已核 | zh 468｜en 181｜示例主线、其他示例、次要明细页；复用 G007 |
| E110 | `determination-unmarked.long` | A determination citation without the simulation marker: a determination is not the output of a check run, and this interface has nothing it can verify about where it cam… | 未带模拟标记的判定引用：判定不是检查运行的输出，本界面也没有可核依据说明它来自哪里，因此不作真实或模拟的断言。 | 10/8 已核 | zh 468｜en 181｜示例主线、其他示例、次要明细页 |

#### CONDITION_ENTRIES（8 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E111 | `named-outcome-observed.text` | Only the named outcome observed; the rest of the condition not checked | 仅命名结果已观察到；条件其余部分未检查 | 10/8 已核 | zh 20｜en 20｜示例主线、其他示例；复用 G008 |
| E113 | `named-outcome-not-observed.text` | Named outcome not observed | 未观察到命名结果 | 10/8 已核 | zh 25｜en 25｜示例主线、其他示例；复用 G009 |
| E114 | `named-outcome-not-observed.plain` | The outcome named in the original recheck condition is not observed now: the original condition is not reached. | 原复检条件里点名的那个结果，现在没有观察到：原条件未达成。 | 10/8 已核 | zh 5｜en 5｜示例主线、其他示例 |
| E115 | `no-machine-checkable-part.text` | The condition has no machine-checkable part; a person must read it | 条件没有可机检部分，需要人阅读 | 10/8 已核 | zh 87｜en 87｜示例主线、其他示例；复用 G010 |
| E116 | `no-machine-checkable-part.plain` | The original recheck condition has no part a machine can check; a person needs to read the original condition and judge it. The record draws no conclusion on it. | 原复检条件没有机器能检查的部分，需要人阅读原条件并判断；记录对它不下结论。 | 10/8 已核 | zh 67｜en 67｜示例主线、其他示例 |
| E117 | `not-comparable.text` | Cannot be compared: the corresponding elements are incomplete | 不可比较：对应的构件不完整 | 10/8 已核 | zh 29｜en 29｜示例主线、其他示例；复用 G011 |
| E119 | `no-recheck-condition.text` | The original record had no recheck condition | 原记录没有复检条件 | 10/8 已核 | zh 70｜en 70｜示例主线、其他示例；复用 G012 |
| E120 | `no-recheck-condition.plain` | The original record had no recheck condition: the original conclusion left nothing outstanding. | 原记录没有复检条件：原来的判断没有留下待办。 | 10/8 后改句，需重核 | zh 50｜en 50｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E120` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：四、复检前留下的结束条件，这次达到了吗 ‹ 原记录没有复检条件：原来的判断没有留下待办。 › 这里只说复检前留下的结束条件被证明到了什么程度，与现在的结论分开读：结论变了，不等于原条件已满足。；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：4. Was the exit condition left before the recheck reached this time? ‹ The original record had no recheck condition: the original conclusion left nothing outstanding. › This says only how far the exit condition left before the recheck has

#### CONDITION_STATES（5 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E121 | `named-outcome-observed` | Only the named outcome observed; the rest of the condition not checked | 仅命名结果已观察到；条件其余部分未检查 | 10/8 已核 | zh 20｜en 20｜示例主线、其他示例；复用 G008 |
| E122 | `named-outcome-not-observed` | Named outcome not observed | 未观察到命名结果 | 10/8 已核 | zh 25｜en 25｜示例主线、其他示例；复用 G009 |
| E123 | `no-machine-checkable-part` | The condition has no machine-checkable part; a person must read it | 条件没有可机检部分，需要人阅读 | 10/8 已核 | zh 87｜en 87｜示例主线、其他示例；复用 G010 |
| E124 | `not-comparable` | Cannot be compared: the corresponding elements are incomplete | 不可比较：对应的构件不完整 | 10/8 已核 | zh 29｜en 29｜示例主线、其他示例；复用 G011 |
| E125 | `no-recheck-condition` | The original record had no recheck condition | 原记录没有复检条件 | 10/8 已核 | zh 70｜en 70｜示例主线、其他示例；复用 G012 |

#### CONSEQUENCE_KINDS（3 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E126 | `work-cannot-start` | This work cannot start | 这项工作不能开始 | 10/8 已核 | zh 30｜en 30｜示例主线、其他示例 |
| E127 | `work-suspended` | This work is held until decided | 这项工作暂缓，等有结论再定 | 10/8 后改句，需重核 | zh 73｜en 73｜示例主线、其他示例 |
| E129 | `re-identification-and-reissue-risk` | Risk of re-identification: documents that cite these identifiers would then have to be reissued too | 有重新标识的风险：引用这些标识的文件届时也须重新出具 | 10/8 已核 | zh 30｜en 30｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E127` zh `#/fixture/member-evidence/item/0/2/0`：对这项工作的后果 ‹ 这项工作暂缓，等有结论再定 › 完成后拿什么复检；en `#/fixture/member-evidence/item/0/2/0`：What it means for this work ‹ This work is held until decided › What a recheck must show

#### DEMO_NOTICE（1 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E130 | `(整表)` | Simulated example: the project settings in the example, including the handling teams and the acceptance of evidence methods, are demonstration settings, not real project… | 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的检查结果或模拟的人工判定，具体是哪一种，看每个结论旁的“依据”一行（按逐条引用… | 10/8 已核 | zh 481｜en 324｜示例目录、示例主线、其他示例、次要明细页 |

#### DETAILS_WORDS（15 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E131 | `heading` | What exactly is missing | 具体缺什么 | 10/8 已核 | zh 0｜en 16｜示例主线、其他示例 |
| E133 | `determinations` | This conclusion cites human determinations, not check results; a determination has no requirement details. What is missing is said in the conclusion and in "What to do"… | 这个结论引用的是人工判定，不是检查结果；判定没有要求明细。缺的是什么，见上面的结论和“要做什么”。 | 10/8 已核 | zh 2｜en 2｜示例主线、其他示例 |
| E134 | `nothingCited` | This conclusion cites no check result, so there are no requirement details to show. | 这个结论没有引用任何检查结果，所以没有要求明细可以显示。 | 10/8 已核 | zh 8｜en 8｜示例主线、其他示例 |
| E135 | `requirement` | Requirement not met | 不满足的要求 | 10/8 已核 | zh 36｜en 36｜示例主线、其他示例 |
| E136 | `requirementMet` | Requirement | 要求 | 10/8 已核 | zh 40｜en 40｜示例主线、本地检查（选文件至运行）、其他示例；复用 G013 |
| E137 | `rule` | Rule | 规则编号 | 10/8 已核 | zh 66｜en 66｜示例主线、其他示例 |
| E138 | `status` | Result of that check | 那次检查的结果 | 10/8 已核 | zh 66｜en 66｜示例主线、其他示例 |
| E139 | `reason` | Reason | 原因 | 10/8 已核 | zh 206｜en 66｜示例主线、其他示例、次要明细页 |
| E140 | `actual` | Value that check observed | 那次检查观察到的值 | 10/8 已核 | zh 66｜en 66｜示例主线、其他示例 |
| E141 | `noActual` | That check observed no value | 那次检查没有观察到值 | 10/8 已核 | zh 66｜en 66｜示例主线、其他示例 |
| E143 | `expected` | The rule's own words | 规则的原话（英文） | 10/8 已核 | zh 74｜en 74｜示例主线、本地结果页、其他示例；复用 G014 |
| E144 | `source` | Source the rule gives: | 规则给出的出处（英文原文）： | 10/8 已核 | zh 66｜en 66｜示例主线、其他示例 |
| E145 | `projectAssumption` | This is a requirement assumed for this project (ProjectAssumption), not a general one. | 这是本项目假定的要求（ProjectAssumption），不是通用要求。 | 10/8 后改句，需重核 | zh 36｜en 36｜示例主线、其他示例 |
| E147 | `prior` | At the assessment before the recheck, this evidence's requirement and result were as follows. Having this description does not make the row comparable; the row's state i… | 复检前那次评估时，这条证据的要求和结果如下。有这段说明不等于这一行可以比较；这一行的状态以上面写的为准。 | 10/8 已核 | zh 60｜en 60｜示例主线、其他示例 |
| E148 | `currentAbsent` | The corresponding evidence this record cites: its requirement details are not given in the record. | 本次记录引用的对应证据：要求明细记录未提供。 | 10/8 已核 | zh 54｜en 54｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E145` zh `#/fixture/member-evidence/item/2/2/0`：SystemCode data shall be provided in the dataset EPC_Delivery ‹ 这是本项目假定的要求（ProjectAssumption），不是通用要求。 规则给出的出处（英文原文）：Project-assumed EPC delivery requirement; not a buildingSM › 不满足的要求；en `#/fixture/member-evidence/item/2/2/0`：SystemCode data shall be provided in the dataset EPC_Delivery ‹ This is a requirement assumed for this project (ProjectAssumption), not a general one. Source the rule gives:  › Requirement not met

#### DISPOSITIONS（5 条，待核 5）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E149 | `present` | Still in this check's scope; conclusion and condition are read separately | 仍在本次检查范围内；判断与条件另看 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例；复用 G015 |
| E150 | `element-deleted-in-reissued-model` | Deleted in the re-issued model; that is not a fix | 在重发模型中删除，不等于修复 | 10/15 批，未核 | zh 23｜en 23｜示例主线、其他示例；复用 G016 |
| E151 | `element-out-of-subject-class` | No longer of this activity's subject classes; that is not a fix | 已不属于此活动对象类别，不等于修复 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例；复用 G017 |
| E152 | `pairing-no-longer-derived` | These two elements are no longer paired for checking; that does not mean the opening was added | 这两个构件现在不再被配成一对来检查，不等于开洞已补 | 10/15 批，未核 | zh 31｜en 31｜示例主线、其他示例；复用 G018 |
| E153 | `outside-declared-scope` | This scope was not declared this time; that does not mean the problem is gone | 本次未声明该范围，不等于问题解除 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例；复用 G019 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E149` zh `#/fixture/recheck-requirement-relaxed`：复检前记录里的事项（13 个），现在的情况 ‹ 仍在本次检查范围内；判断与条件另看 × 13 › 复检前引用的旧证据（15 条），和本次记录比较的结果；en `#/fixture/recheck-requirement-relaxed`：The items in the record before the recheck (13), and where they stand  ‹ Still in this check's scope; conclusion and condition are read separately × 13 › The old evidence cited before the recheck (15 rows), compared with thi
- `E150` zh `#/fixture/recheck-requirement-relaxed`：element-deleted-in-reissued-model ‹ 在重发模型中删除，不等于修复 › element-out-of-subject-class；en `#/fixture/recheck-requirement-relaxed`：element-deleted-in-reissued-model ‹ Deleted in the re-issued model; that is not a fix › element-out-of-subject-class
- `E151` zh `#/fixture/recheck-requirement-relaxed`：element-out-of-subject-class ‹ 已不属于此活动对象类别，不等于修复 › pairing-no-longer-derived；en `#/fixture/recheck-requirement-relaxed`：element-out-of-subject-class ‹ No longer of this activity's subject classes; that is not a fix › pairing-no-longer-derived
- `E152` zh `#/fixture/recheck-requirement-relaxed`：pairing-no-longer-derived ‹ 这两个构件现在不再被配成一对来检查，不等于开洞已补 › outside-declared-scope；en `#/fixture/recheck-requirement-relaxed`：pairing-no-longer-derived ‹ These two elements are no longer paired for checking; that does not mean the opening was added › outside-declared-scope
- `E153` zh `#/fixture/recheck-requirement-relaxed`：outside-declared-scope ‹ 本次未声明该范围，不等于问题解除 › 复检前留下的条件：状态原码（没有“整句条件已满足”）；en `#/fixture/recheck-requirement-relaxed`：outside-declared-scope ‹ This scope was not declared this time; that does not mean the problem is gone › Conditions left before the recheck: state codes (there is no "the whol

#### DISPOSITION_ENTRIES（5 条，待核 5）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E154 | `present.text` | Still in this check's scope; conclusion and condition are read separately | 仍在本次检查范围内；判断与条件另看 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例；复用 G015 |
| E156 | `element-deleted-in-reissued-model.text` | Deleted in the re-issued model; that is not a fix | 在重发模型中删除，不等于修复 | 10/15 批，未核 | zh 23｜en 23｜示例主线、其他示例；复用 G016 |
| E158 | `element-out-of-subject-class.text` | No longer of this activity's subject classes; that is not a fix | 已不属于此活动对象类别，不等于修复 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例；复用 G017 |
| E160 | `pairing-no-longer-derived.text` | These two elements are no longer paired for checking; that does not mean the opening was added | 这两个构件现在不再被配成一对来检查，不等于开洞已补 | 10/15 批，未核 | zh 31｜en 31｜示例主线、其他示例；复用 G018 |
| E162 | `outside-declared-scope.text` | This scope was not declared this time; that does not mean the problem is gone | 本次未声明该范围，不等于问题解除 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例；复用 G019 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E154` zh `#/fixture/recheck-requirement-relaxed`：复检前记录里的事项（13 个），现在的情况 ‹ 仍在本次检查范围内；判断与条件另看 × 13 › 复检前引用的旧证据（15 条），和本次记录比较的结果；en `#/fixture/recheck-requirement-relaxed`：The items in the record before the recheck (13), and where they stand  ‹ Still in this check's scope; conclusion and condition are read separately × 13 › The old evidence cited before the recheck (15 rows), compared with thi
- `E156` zh `#/fixture/recheck-requirement-relaxed`：element-deleted-in-reissued-model ‹ 在重发模型中删除，不等于修复 › element-out-of-subject-class；en `#/fixture/recheck-requirement-relaxed`：element-deleted-in-reissued-model ‹ Deleted in the re-issued model; that is not a fix › element-out-of-subject-class
- `E158` zh `#/fixture/recheck-requirement-relaxed`：element-out-of-subject-class ‹ 已不属于此活动对象类别，不等于修复 › pairing-no-longer-derived；en `#/fixture/recheck-requirement-relaxed`：element-out-of-subject-class ‹ No longer of this activity's subject classes; that is not a fix › pairing-no-longer-derived
- `E160` zh `#/fixture/recheck-requirement-relaxed`：pairing-no-longer-derived ‹ 这两个构件现在不再被配成一对来检查，不等于开洞已补 › outside-declared-scope；en `#/fixture/recheck-requirement-relaxed`：pairing-no-longer-derived ‹ These two elements are no longer paired for checking; that does not mean the opening was added › outside-declared-scope
- `E162` zh `#/fixture/recheck-requirement-relaxed`：outside-declared-scope ‹ 本次未声明该范围，不等于问题解除 › 复检前留下的条件：状态原码（没有“整句条件已满足”）；en `#/fixture/recheck-requirement-relaxed`：outside-declared-scope ‹ This scope was not declared this time; that does not mean the problem is gone › Conditions left before the recheck: state codes (there is no "the whol

#### ELEMENT_WORDS（6 条，待核 6）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E164 | `unnamed` | No name filled in in the model | 模型中没有填写名称 | 10/15 批，未核 | zh 0｜en 0｜（本次渲染未触发） |
| E166 | `noStorey` | No storey assignment in the model | 模型中没有楼层归属 | 10/15 批，未核 | zh 13｜en 37｜示例主线、其他示例 |
| E167 | `noDiscipline` | The record gives no discipline; this interface does not infer one from a model identifier | 记录未提供专业信息；本界面不从模型标识推断专业 | 10/15 批，未核 | zh 157｜en 157｜示例主线、其他示例 |
| E168 | `modelIsNotDiscipline` | This is a model identifier, not a statement of discipline | 这是模型标识，不是专业声明 | 10/15 批，未核 | zh 157｜en 157｜示例主线、其他示例 |
| E169 | `noClassName` | (IFC class) | 本界面没有这个类别的中文名 | 10/15 批，未核 | zh 0｜en 194｜示例主线、本地结果页、其他示例 |
| E170 | `naming` | The name is taken from the model file itself; it may be empty or shared with other elements. To find it in the model, use the GlobalId. | 名称取自模型文件本身，可能为空，也可能与别的构件重名；要在模型里定位，请用 GlobalId。 | 10/15 批，未核 | zh 157｜en 157｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E166` zh `#/fixture/member-evidence/item/0/4/0`：楼层 ‹ 模型中没有楼层归属 › 所属模型；en `#/fixture/member-evidence`：house - chimney: IfcChimney (IFC class) · 00 groundfloor · model hvac ‹ house - roof: IfcRoof (IFC class) · No storey assignment in the model · model architecture › What to do
- `E167` zh `#/fixture/member-evidence/item/0/1/0`：专业 ‹ 记录未提供专业信息；本界面不从模型标识推断专业 › GlobalId；en `#/fixture/member-evidence/item/0/1/0`：Discipline ‹ The record gives no discipline; this interface does not infer one from a model identifier › GlobalId
- `E168` zh `#/fixture/member-evidence/item/0/1/0`：hvac：本次交接中交出方的模型 ‹ 这是模型标识，不是专业声明 › 专业；en `#/fixture/member-evidence/item/0/1/0`：hvac: the handing-over side's model in this handover ‹ This is a model identifier, not a statement of discipline › Discipline
- `E169` en `#/fixture/member-evidence`：Element details and what to do ‹ IfcAirTerminal (IFC class) · 00 groundfloor · model hvac › What to do
- `E170` zh `#/fixture/member-evidence/item/0/1/0`：hvac::38WbwIGD90nB_3T2BTU5Ed ‹ 名称取自模型文件本身，可能为空，也可能与别的构件重名；要在模型里定位，请用 GlobalId。 › 然后：这一项复检后的变化；en `#/fixture/member-evidence/item/0/1/0`：hvac::38WbwIGD90nB_3T2BTU5Ed ‹ The name is taken from the model file itself; it may be empty or shared with other elements. To find it in the › Then: how this item changed after a recheck

#### EXAMPLES（6 条，待核 6）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E171 | `member-evidence.step` | Step 1 | 第一步 | 10/15 批，未核 | zh 1｜en 1｜示例目录 |
| E172 | `member-evidence.question` | The handing-over side has handed over its model: which items need dealing with, who deals with each, and what does each one need? | 交出方交了模型：有哪些事项要处理，各由谁处理，每一项要做什么？ | 10/15 批，未核 | zh 1｜en 1｜示例目录 |
| E173 | `member-evidence.given` | This example was given: the bundled sample project's two models; the handling teams, and the human determinations (whether something passes through, the state of opening… | 这个示例被给了：随附样例项目的两份模型；处理团队的安排，以及人工判定（是否穿过、洞口情况、两侧模型是否对齐），由示例设定。 | 10/15 批，未核 | zh 1｜en 1｜示例目录 |
| E174 | `recheck-requirement-relaxed.step` | Step 2 | 第二步 | 10/15 批，未核 | zh 1｜en 1｜示例目录 |
| E175 | `recheck-requirement-relaxed.question` | The same record after a recheck: neither model was re-issued, yet a conclusion changed. Which one changed, and why? | 同一份记录复检之后：两侧模型都没有重新发布，却有判断变了。变的是哪一项，为什么？ | 10/15 批，未核 | zh 1｜en 1｜示例目录 |
| E176 | `recheck-requirement-relaxed.given` | This example was given: one cited check requirement was relaxed; neither the handing-over nor the receiving side's model version changed. | 这个示例被给了：一条被引用的检查要求放宽了；交出方和接收方的模型版本都没有变。 | 10/15 批，未核 | zh 1｜en 1｜示例目录 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E171` zh `#/fixture`：每个示例是一份检查记录。 ‹ 第一步 › 一次首次检查：交了模型，发现这些事项；en `#/fixture`：Each example is one check record. ‹ Step 1 › A first check: the model was handed over, and these items were found
- `E172` zh `#/fixture`：一次首次检查：交了模型，发现这些事项 ‹ 交出方交了模型：有哪些事项要处理，各由谁处理，每一项要做什么？ › 示例说明 这个示例被给了：随附样例项目的两份模型；处理团队的安排，以及人工判定（是否穿过、洞口情况、两侧模型是否对齐），由示例设定。；en `#/fixture`：A first check: the model was handed over, and these items were found ‹ The handing-over side has handed over its model: which items need dealing with, who deals with each, and what  › About this example This example was given: the bundled sample project'
- `E173` zh `#/fixture`：交出方交了模型：有哪些事项要处理，各由谁处理，每一项要做什么？ ‹ 示例说明 这个示例被给了：随附样例项目的两份模型；处理团队的安排，以及人工判定（是否穿过、洞口情况、两侧模型是否对齐），由示例设定。 › 打开这个示例的结果；en `#/fixture`：The handing-over side has handed over its model: which items need deal ‹ About this example This example was given: the bundled sample project's two models; the handling teams, and th › Open this example's result
- `E174` zh `#/fixture`：打开这个示例的结果 ‹ 第二步 › 模型未改，但交接判断发生变化；en `#/fixture`：Open this example's result ‹ Step 2 › The models did not change, but a handover conclusion did
- `E175` zh `#/fixture`：模型未改，但交接判断发生变化 ‹ 同一份记录复检之后：两侧模型都没有重新发布，却有判断变了。变的是哪一项，为什么？ › 示例说明 这个示例被给了：一条被引用的检查要求放宽了；交出方和接收方的模型版本都没有变。；en `#/fixture`：The models did not change, but a handover conclusion did ‹ The same record after a recheck: neither model was re-issued, yet a conclusion changed. Which one changed, and › About this example This example was given: one cited check requirement
- `E176` zh `#/fixture`：同一份记录复检之后：两侧模型都没有重新发布，却有判断变了。变的是哪一项，为什么？ ‹ 示例说明 这个示例被给了：一条被引用的检查要求放宽了；交出方和接收方的模型版本都没有变。 › 打开这个示例的结果；en `#/fixture`：The same record after a recheck: neither model was re-issued, yet a co ‹ About this example This example was given: one cited check requirement was relaxed; neither the handing-over n › Open this example's result

#### EXAMPLE_NOTE（1 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E177 | `(整表)` | An example's description is written by whoever built the example and says only what the example was given; it is not a conclusion of any check. What the check concluded… | 示例说明由搭建示例的人提供，只说这个示例被给了什么；它不是检查得出的结论。检查得出了什么，只看结果页。 | 10/8 已核 | zh 1｜en 1｜示例目录 |

#### FINDING_STATUS（3 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E178 | `FAIL` | Fail | 不通过 | 10/8 已核 | zh 49｜en 49｜示例主线、本地结果页、其他示例 |
| E179 | `PASS` | Pass | 通过 | 10/8 已核 | zh 34｜en 34｜示例主线、本地结果页、其他示例 |
| E180 | `N/A` | Not applicable | 不适用 | 10/8 已核 | zh 8｜en 8｜本地结果页 |

#### HANDOVER_SIDES（2 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E181 | `producing` | the handing-over side's model in this handover | 本次交接中交出方的模型 | 10/8 已核 | zh 0｜en 157｜示例主线、其他示例 |
| E182 | `consuming` | the receiving side's model in this handover | 本次交接中接收方的模型 | 10/8 已核 | zh 0｜en 25｜示例主线、其他示例 |

#### HOME（14 条，待核 11）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E183 | `title` | Items still to be dealt with in a model handover | 查看模型交接中仍需处理的事项 | 10/15 批，未核 | zh 1｜en 1｜首页 |
| E184 | `lede` | For a BIM manager: what a pre-handover check found; after a recheck, which conclusions changed, which items still need dealing with, which elements each one involves, wh… | 帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。 | 10/15 批，未核 | zh 1｜en 1｜首页 |
| E188 | `example.title` | Look at a simulated example | 看一个模拟示例 | 10/15 批，未核 | zh 1｜en 1｜首页 |
| E189 | `example.body` | Start from a first check: find the items that need dealing with, and see which elements they involve, what to do, who deals with it and what a recheck must show; then se… | 从一次首次检查出发：找到需要处理的事项，看清涉及的构件、要做什么、由谁处理、完成后拿什么复检；然后再看同一事项复检后的变化。示例里模拟的内容，页面上逐处标明。 | 10/15 批，未核 | zh 1｜en 1｜首页 |
| E190 | `example.action` | Choose a simulated example | 选择模拟示例 | 10/15 批，未核 | zh 1｜en 2｜首页、示例目录 |
| E191 | `attempt.title` | See the check attempt on the bundled project | 查看随附项目的检查尝试 | 10/15 批，未核 | zh 1｜en 1｜首页 |
| E192 | `attempt.body` | The repository comes with a sample project. The check attempt on it did not start an assessment; this explains why. This entry is not an import: it shows only this sampl… | 仓库随附一个样例项目。对它的检查尝试没有开始评估；这里说明原因。这个入口不是导入入口：只看这个样例项目，不能换成别的模型。 | 10/8 后改句，需重核 | zh 1｜en 1｜首页 |
| E193 | `attempt.action` | See this check attempt | 查看这次检查尝试 | 10/15 批，未核 | zh 1｜en 1｜首页 |
| E195 | `cannot[1]` | Give an overall compliance, ready-to-build or "ready to hand over" conclusion | 给出整体合规、可施工或“可以交付”的结论 | 10/8 已核 | zh 1｜en 0｜首页；复用 G020 |
| E196 | `cannot[2]` | Write back to a model, upload to the cloud, or open an element in Revit | 写回模型、上传到云端，或在 Revit 里打开构件 | 10/8 已核 | zh 1｜en 1｜首页；复用 G021 |
| E197 | `canHeading` | What you can do now | 现在可以做什么 | 10/15 批，未核 | zh 1｜en 1｜首页 |
| E198 | `cannotHeading` | What you cannot do yet | 现在还不能做什么 | 10/15 批，未核 | zh 1｜en 1｜首页 |
| E199 | `cannotNote` | These are not implemented, so the page has no entry for them. | 这些功能没有实现，所以页面上没有对应的入口。 | 10/8 已核 | zh 1｜en 1｜首页 |
| H01 | `recommended` | Start here | 推荐从这里开始 | 新增，未核 | zh 1｜en 1｜首页 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E183` zh `#/`：English ‹ 查看模型交接中仍需处理的事项 › 帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。；en `#/`：English ‹ Items still to be dealt with in a model handover › For a BIM manager: what a pre-handover check found; after a recheck, w
- `E184` zh `#/`：查看模型交接中仍需处理的事项 ‹ 帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。 › 当前提供模拟示例，以及对自己 IFC4 文件的一项有限产品验证练习；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。；en `#/`：Items still to be dealt with in a model handover ‹ For a BIM manager: what a pre-handover check found; after a recheck, which conclusions changed, which items st › Available now: simulated examples, and one limited product validation
- `E188` zh `#/`：推荐从这里开始 ‹ 看一个模拟示例 › 从一次首次检查出发：找到需要处理的事项，看清涉及的构件、要做什么、由谁处理、完成后拿什么复检；然后再看同一事项复检后的变化。示例里模拟的内容；en `#/`：Start here ‹ Look at a simulated example › Start from a first check: find the items that need dealing with, and s
- `E189` zh `#/`：看一个模拟示例 ‹ 从一次首次检查出发：找到需要处理的事项，看清涉及的构件、要做什么、由谁处理、完成后拿什么复检；然后再看同一事项复检后的变化。示例里模拟的内容，页面上逐处标明。 › 选择模拟示例；en `#/`：Look at a simulated example ‹ Start from a first check: find the items that need dealing with, and see which elements they involve, what to  › Choose a simulated example
- `E190` zh `#/`：从一次首次检查出发：找到需要处理的事项，看清涉及的构件、要做什么、由谁处理、完成后拿什么复检；然后再看同一事项复检后的变化。示例里模拟的内容 ‹ 选择模拟示例 › 检查自己的 IFC 模型（产品验证练习）；en `#/`：Start from a first check: find the items that need dealing with, and s ‹ Choose a simulated example › Check your own IFC model (product validation exercise)
- `E191` zh `#/`：开始本地检查 ‹ 查看随附项目的检查尝试 › 仓库随附一个样例项目。对它的检查尝试没有开始评估；这里说明原因。这个入口不是导入入口：只看这个样例项目，不能换成别的模型。；en `#/`：Start a local check ‹ See the check attempt on the bundled project › The repository comes with a sample project. The check attempt on it di
- `E192` zh `#/`：查看随附项目的检查尝试 ‹ 仓库随附一个样例项目。对它的检查尝试没有开始评估；这里说明原因。这个入口不是导入入口：只看这个样例项目，不能换成别的模型。 › 查看这次检查尝试；en `#/`：See the check attempt on the bundled project ‹ The repository comes with a sample project. The check attempt on it did not start an assessment; this explains › See this check attempt
- `E193` zh `#/`：仓库随附一个样例项目。对它的检查尝试没有开始评估；这里说明原因。这个入口不是导入入口：只看这个样例项目，不能换成别的模型。 ‹ 查看这次检查尝试 › 现在还不能做什么；en `#/`：The repository comes with a sample project. The check attempt on it di ‹ See this check attempt › What you cannot do yet
- `E197` zh `#/`：当前提供模拟示例，以及对自己 IFC4 文件的一项有限产品验证练习；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。 ‹ 现在可以做什么 › 推荐从这里开始；en `#/`：Available now: simulated examples, and one limited product validation  ‹ What you can do now › Start here
- `E198` zh `#/`：查看这次检查尝试 ‹ 现在还不能做什么 › 导入 Revit 文件本身（.rvt），或用产品验证练习以外的规则检查自己的模型；en `#/`：See this check attempt ‹ What you cannot do yet › Import a Revit file itself (.rvt), or check your own model against rul
- `H01` zh `#/`：现在可以做什么 ‹ 推荐从这里开始 › 看一个模拟示例；en `#/`：What you can do now ‹ Start here › Look at a simulated example

#### ITEM_UNIT（1 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E200 | `(整表)` | An item is the conclusion for one element (or a pair of elements assessed together) on one piece of the receiving side's work. The same element can appear in several ite… | 一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。同一个构件可以出现在几个事项里，所以事项数不是缺陷数。 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |

#### KEY_CHANGED（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E201 | `yes` | The citation changed key (the new key is the "corresponding evidence this record cites" above). A change of key is not itself a change. | 引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 | 10/15 批，未核 | zh 33｜en 33｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E201` zh `#/fixture/recheck-requirement-relaxed/recheck/7/0`：对应的检查结果只有一条，逐项比较后至少有一个方面不同。 ‹ 引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 › 检查要求被修改过，检查结果内容也变了：结果的变化可能来自要求的修改（例如要求放宽），不能据此说模型修好了。记录不说明要求是放宽还是收紧。；en `#/fixture/recheck-requirement-relaxed/recheck/7/0`：There is exactly one corresponding check result; compared aspect by as ‹ The citation changed key (the new key is the "corresponding evidence this record cites" above). A change of ke › The check requirement was edited and the check result content changed

#### LEAF_READINGS（9 条，待核 9）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E203 | `asset-identity/satisfied` | The project asset-identity requirements that apply to it passed, and it was actually evaluated | 适用于它的项目资产标识要求评为通过，并且它确实被评估到 | B 层，10/8 未核 | zh 5｜en 5｜示例主线、其他示例 |
| E204 | `asset-identity/unmet` | The project asset-identity requirement is not met | 项目资产标识的要求没有满足 | B 层，10/8 未核 | zh 30｜en 30｜示例主线、其他示例 |
| E205 | `asset-identity/not-yet-evaluated` | The asset-identity rules did not cover it | 资产标识的规则没有覆盖到它 | B 层，10/8 未核 | zh 12｜en 12｜示例主线、其他示例 |
| E208 | `in-model-position/not-yet-evaluated` | The storey or space check did not cover it | 楼层或空间归属的检查没有覆盖到它 | B 层，10/8 未核 | zh 16｜en 12｜示例主线、其他示例 |
| E209 | `cross-model-alignment/confirmed` | A record confirms the two models are aligned to a common datum (by the method the project accepts, for the listed model versions) | 已有记录确认两侧模型对齐到共同的基准（按项目接受的方法，针对所列模型版本） | B 层，10/8 未核 | zh 21｜en 21｜示例主线、其他示例 |
| E212 | `penetration-determination/no-penetration` | A coordination-review determination says it passes through no element of the receiving model. With no penetration no opening is needed, so the opening was not assessed —… | 已有协调评审判定：它不穿过接收方模型里的任何构件。不穿过就不需要开洞，所以开洞情况没有被评估——这不是“开洞没问题” | B 层，10/8 未核 | zh 7｜en 7｜示例主线、其他示例 |
| E214 | `penetration-determination/not-yet-determined` | No coordination review has determined yet whether it passes through elements of the receiving model | 还没有协调评审判定它是否穿过接收方模型里的构件 | B 层，10/8 未核 | zh 28｜en 28｜示例主线、其他示例 |
| E215 | `opening-status/cross-referenced` | This pair: the opening is modelled in the element passed through, and linked to the element passing through it | 这一对：洞口已建在被穿过的构件上，并且已关联到穿过它的这个构件 | B 层，10/8 未核 | zh 7｜en 7｜示例主线、其他示例 |
| E217 | `opening-status/not-modelled` | This pair: no opening is modelled in the element passed through | 这一对：被穿过的构件上没有建出洞口 | B 层，10/8 未核 | zh 7｜en 7｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E203` zh `#/fixture/recheck-requirement-relaxed/recheck/7/2`：这个结论依据的结果 ‹ 适用于它的项目资产标识要求评为通过，并且它确实被评估到 › 模型；en `#/fixture/recheck-requirement-relaxed/recheck/7/2`：The result this conclusion rests on ‹ The project asset-identity requirements that apply to it passed, and it was actually evaluated › Models
- `E204` zh `#/fixture/member-evidence/item/2/2/0`：这个结论依据的结果 ‹ 项目资产标识的要求没有满足 › 这项工作需要什么；en `#/fixture/member-evidence/item/2/2/0`：The result this conclusion rests on ‹ The project asset-identity requirement is not met › What this work needs
- `E205` zh `#/fixture/member-evidence/item/2/1/0`：这个结论依据的结果 ‹ 资产标识的规则没有覆盖到它 › 这项工作需要什么；en `#/fixture/member-evidence/item/2/1/0`：The result this conclusion rests on ‹ The asset-identity rules did not cover it › What this work needs
- `E208` zh `#/fixture/member-evidence`：事项数 ‹ 不是已知的模型缺陷：楼层或空间归属的检查没有覆盖到它 › 吊顶平面与包封布置：无法判断；en `#/fixture/member-evidence/item/1/1/0`：The result this conclusion rests on ‹ The storey or space check did not cover it › What this work needs
- `E209` zh `#/fixture/member-evidence/item/1/2/0`：这个结论依据的结果 ‹ 已有记录确认两侧模型对齐到共同的基准（按项目接受的方法，针对所列模型版本） › 这项工作需要什么；en `#/fixture/member-evidence/item/1/2/0`：The result this conclusion rests on ‹ A record confirms the two models are aligned to a common datum (by the method the project accepts, for the lis › What this work needs
- `E212` zh `#/fixture/member-evidence/item/0/1/0`：这个结论依据的结果 ‹ 已有协调评审判定：它不穿过接收方模型里的任何构件。不穿过就不需要开洞，所以开洞情况没有被评估——这不是“开洞没问题” › 这项工作需要什么；en `#/fixture/member-evidence/item/0/1/0`：The result this conclusion rests on ‹ A coordination-review determination says it passes through no element of the receiving model. With no penetrat › What this work needs
- `E214` zh `#/fixture/member-evidence/item/0/2/0`：这个结论依据的结果 ‹ 还没有协调评审判定它是否穿过接收方模型里的构件 › 这项工作需要什么；en `#/fixture/member-evidence/item/0/2/0`：The result this conclusion rests on ‹ No coordination review has determined yet whether it passes through elements of the receiving model › What this work needs
- `E215` zh `#/fixture/member-evidence/item/0/3/0`：这个结论依据的结果 ‹ 这一对：洞口已建在被穿过的构件上，并且已关联到穿过它的这个构件 › 这项工作需要什么；en `#/fixture/member-evidence/item/0/3/0`：The result this conclusion rests on ‹ This pair: the opening is modelled in the element passed through, and linked to the element passing through it › What this work needs
- `E217` zh `#/fixture/member-evidence/item/0/4/0`：这个结论依据的结果 ‹ 这一对：被穿过的构件上没有建出洞口 › 这项工作需要什么；en `#/fixture/member-evidence/item/0/4/0`：The result this conclusion rests on ‹ This pair: no opening is modelled in the element passed through › What this work needs

#### LEAF_READING_WORDS（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E219 | `label` | The result this conclusion rests on | 这个结论依据的结果 | B 层，10/8 未核 | zh 157｜en 157｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E219` zh `#/fixture/member-evidence/item/0/1/0`：只对这一个事项、这项工作、所列的模型版本成立；不代表整次交接完成。 ‹ 这个结论依据的结果 › 已有协调评审判定：它不穿过接收方模型里的任何构件。不穿过就不需要开洞，所以开洞情况没有被评估——这不是“开洞没问题”；en `#/fixture/member-evidence/item/0/1/0`：Holds for this one item, this work and the listed model versions only; ‹ The result this conclusion rests on › A coordination-review determination says it passes through no element

#### MODE_LABELS（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E222 | `fixture` | Simulated example | 模拟示例 | 10/15 批，未核 | zh 481｜en 324｜示例目录、示例主线、其他示例、次要明细页 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E222` zh `#/fixture`：English ‹ 模拟示例 › 返回首页；en `#/fixture`：English ‹ Simulated example › Back to the home page

#### ONLY_REKEYED（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E225 | `(整表)` | Only the citation's key changed | 只是引用换了键 | 10/15 批，未核 | zh 30｜en 38｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E225` zh `#/fixture/recheck-requirement-relaxed/recheck/5/0`：58491270f2af3ded52165b6024e1097e9128a80cbbc6f6d6ed844aeb8fecb10d ‹ 比较依据一致 只是引用换了键 › 检查结果引用：2c232698-eeff-592e-a20a-a48be0847c64复制 真实检查输出；en `#/fixture/recheck-requirement-relaxed`：Comparison basis unchanged × 7 ‹ Only the citation's key changed × 7 › Comparison basis changed × 2

#### PROVENANCE_NOTICE（1 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E226 | `(整表)` | Each citation's source label on this page is decided from that citation alone (whether it carries the simulation marker), never inferred for the whole page or record: | 本页每条引用旁的来源标注按该条引用自身判定（是否带模拟标记），不按整页或整份记录推断： | 10/8 已核 | zh 468｜en 181｜示例主线、其他示例、次要明细页 |

#### READING_GUIDE（5 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E227 | `verdictWords` | The three conclusion words | 三个判断词 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |
| E228 | `verdictLine` | {label}: {meaning}. | {label}：{meaning}。 | 10/8 已核 | zh 181｜en 368｜首页、示例目录、示例主线、本地结果页、本地检查（选文件至运行）、第二入口、其他示例、次要明细页 |
| E229 | `provenance` | How the source of evidence is labelled | 证据来源的标注 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |
| E230 | `teams` | Handling team and default handling role | 处理团队与默认处理角色 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |
| E231 | `teamsBody` | The handling team is taken from the staffing in the record; the default handling role is the rule's default, an input to the staffing, not an assignment. The two are sho… | 处理团队取自记录里的人员安排；默认处理角色是规则给出的默认，是安排的输入，不是指派。两者分开显示。 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |

#### READY_NOTES（2 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E232 | `ceiling-and-bulkhead-geometry[0]` | The rule proves only that the element has a storey or space assignment; it does not check that the receiving model has a matching storey. | 规则只证明构件有楼层或空间归属，没有验证接收方模型有对应楼层。 | 10/8 已核 | zh 33｜en 33｜示例主线、其他示例 |
| E233 | `ceiling-and-bulkhead-geometry[1]` | This conclusion rests on a confirmation that the two models are aligned, not on a shared positioning marker passing. | 这个结论靠的是两侧模型的对齐确认，不是共享定位标记通过。 | 10/8 已核 | zh 33｜en 33｜示例主线、其他示例 |

#### RECHECK（37 条，待核 36）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E234 | `title` | Recheck result | 复检结果 | 10/15 批，未核 | zh 134｜en 20｜示例主线、其他示例、次要明细页 |
| E238 | `resultTitle` | Recheck result: items to deal with | 复检结果：需要处理的事项 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E239 | `summary.one` | This result: {count} item | 本次结果：共 {count} 个事项 | 10/15 批，未核 | zh 24｜en 20｜示例主线、其他示例；复用 G023 |
| E240 | `summary.other` | This result: {count} items | 本次结果：共 {count} 个事项 | 10/15 批，未核 | zh 24｜en 18｜示例主线、其他示例；复用 G023 |
| E241 | `groupLine.one` | {count} item | {count} 个事项 | 10/15 批，未核 | zh 24｜en 6｜示例主线、其他示例；复用 G024 |
| E242 | `groupLine.other` | {count} items | {count} 个事项 | 10/15 批，未核 | zh 24｜en 183｜首页、示例目录、示例主线、其他示例；复用 G024 |
| E243 | `groupSummary` | : {summary} | ：{summary} | 10/15 批，未核 | zh 474｜en 368｜首页、示例目录、示例主线、本地结果页、本地检查（选文件至运行）、第二入口、其他示例、次要明细页 |
| E244 | `models` | Models: {headline}. | 模型：{headline}。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E245 | `moved.one` | {count} item's conclusion differs from before the recheck: | {count} 个事项的结论和复检前不同： | 10/15 批，未核 | zh 12｜en 2｜示例主线、其他示例；复用 G025 |
| E246 | `moved.other` | {count} items' conclusions differ from before the recheck: | {count} 个事项的结论和复检前不同： | 10/15 批，未核 | zh 12｜en 10｜示例主线、其他示例；复用 G025 |
| E247 | `requirementChanged` | Of the old evidence cited before the recheck ({count} in all), the check requirement changed for {edited}. | 复检前引用的 {count} 条旧证据里，有 {edited} 条的检查要求变了。 | 10/15 批，未核 | zh 4｜en 4｜示例主线、其他示例 |
| E248 | `groupHeading.one` | {label} ({count} item) | {label}（{count} 个事项） | 10/15 批，未核 | zh 24｜en 2｜示例主线、其他示例；复用 G026 |
| E249 | `groupHeading.other` | {label} ({count} items) | {label}（{count} 个事项） | 10/15 批，未核 | zh 24｜en 24｜示例主线、其他示例；复用 G026 |
| E250 | `cannotHeading` | What this preview cannot do | 本预览做不了的事 | 10/15 批，未核 | zh 151｜en 151｜示例主线、其他示例 |
| E251 | `cannotNote` | These actions are not implemented, so the page has no buttons for them. | 这些动作没有实现，所以页面上没有对应的按钮。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E252 | `limitsHeading` | When reading a recheck result | 读复检结果时 | 10/15 批，未核 | zh 151｜en 151｜示例主线、其他示例 |
| E253 | `sideModel` | {side} model | {side}模型 | 10/15 批，未核 | zh 474｜en 368｜首页、示例目录、示例主线、本地结果页、本地检查（选文件至运行）、第二入口、其他示例、次要明细页 |
| E254 | `detailsSummary` | Before-and-after details: models, items, old evidence | 复检前后的比较明细：模型、事项、旧证据 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E255 | `modelsHeading` | Models | 模型 | 同句已核 | zh 336｜en 177｜示例主线、本地结果页、本地检查（选文件至运行）、其他示例、次要明细页；复用 G027、G028 |
| E256 | `itemsHeading.one` | The item in the record before the recheck ({count}), and where it stands now | 复检前记录里的事项（{count} 个），现在的情况 | 10/15 批，未核 | zh 20｜en 2｜示例主线、其他示例；复用 G029 |
| E257 | `itemsHeading.other` | The items in the record before the recheck ({count}), and where they stand now | 复检前记录里的事项（{count} 个），现在的情况 | 10/15 批，未核 | zh 20｜en 18｜示例主线、其他示例；复用 G029 |
| E258 | `evidenceHeading.one` | The old evidence cited before the recheck ({count} row), compared with this record | 复检前引用的旧证据（{count} 条），和本次记录比较的结果 | 10/15 批，未核 | zh 20｜en 0｜示例主线、其他示例；复用 G030 |
| E259 | `evidenceHeading.other` | The old evidence cited before the recheck ({count} rows), compared with this record | 复检前引用的旧证据（{count} 条），和本次记录比较的结果 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例；复用 G030 |
| E260 | `kindsNote` | Check results and human determinations are two kinds of evidence, counted apart and never added together. | 检查结果和人工判定是两种证据，分开计数，不相加。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E261 | `traceSummary` | Tracing: record identity, model version fingerprints, record codes | 追溯信息：记录标识、模型版本指纹、记录原码对照 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E262 | `priorDigest` | Fingerprint of the record before the recheck (assessment digest) | 复检前记录的指纹（assessment digest） | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E263 | `currentDigest` | Fingerprint of this record (assessment digest) | 本记录的指纹（assessment digest） | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E264 | `noChange` | (an empty list in the record: no model changed) | （记录中为空列表：没有模型变化） | 10/15 批，未核 | zh 10｜en 10｜示例主线、其他示例 |
| E265 | `versionColumns.side` | Side |  | 10/15 批，未核 | zh 0｜en 20｜示例主线、其他示例 |
| E266 | `versionColumns.prior` | Record before the recheck | 复检前记录 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E267 | `versionColumns.current` | This record | 本记录 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E268 | `versionNote` | A version is a content fingerprint, not a file name. Which side changed is taken from the record's changed_models; this page does not compare fingerprints. | 版本以内容指纹表示，不以文件名当版本。哪一侧变了取自记录的 changed_models，本页不比较指纹。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E269 | `glossaryDispositions` | Where items stand now: record codes | 事项现在的情况：记录原码 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E270 | `glossaryConditions` | Conditions left before the recheck: state codes (there is no "the whole condition is met") | 复检前留下的条件：状态原码（没有“整句条件已满足”） | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E271 | `glossaryStates` | Old-evidence comparison: state codes | 旧证据比较：状态原码 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E272 | `glossaryReasons` | Old-evidence comparison: reason codes | 旧证据比较：原因原码 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |
| E273 | `glossaryAspects` | Aspects that changed: codes | 变化方面：原码 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E234` zh `#/fixture/recheck-comparison/activity/0`：← 记录上下文 ‹ 复检结果 › 活动：builders-work-openings；en `#/fixture/recheck-requirement-relaxed`：← Back to the examples ‹ Recheck result: items to deal with › Simulated example: The models did not change, but a handover conclusio
- `E238` zh `#/fixture/recheck-requirement-relaxed`：← 返回示例目录 ‹ 复检结果：需要处理的事项 › 模拟示例：模型未改，但交接判断发生变化；en `#/fixture/recheck-requirement-relaxed`：← Back to the examples ‹ Recheck result: items to deal with › Simulated example: The models did not change, but a handover conclusio
- `E239` zh `#/fixture/member-evidence`：模拟示例：一次首次检查：交了模型，发现这些事项 ‹ 本次结果：共 13 个事项，其中 8 个需要处理 › 4 个事项：对应的那项工作 受阻；en `#/fixture/recheck-requirement-relaxed`：Simulated example: The models did not change, but a handover conclusio ‹ This result: 13 items › 7 items: the record gives an action
- `E240` zh `#/fixture/member-evidence`：模拟示例：一次首次检查：交了模型，发现这些事项 ‹ 本次结果：共 13 个事项，其中 8 个需要处理 › 4 个事项：对应的那项工作 受阻；en `#/fixture/recheck-requirement-relaxed`：Simulated example: The models did not change, but a handover conclusio ‹ This result: 13 items › 7 items: the record gives an action
- `E241` zh `#/fixture/member-evidence`：需要处理的事项，按处理团队（8 个事项） ‹ 处理团队 coordination-team 示例处理团队：6 个事项 › 默认处理角色（规则给出的默认，不是指派）：model-coordination 处理团队是记录里的安排，不代表已经派发。；en `#/fixture/member-evidence`：Room data sheets and equipment schedules: Unknown ‹ 1 item › The project's required asset identity is missing
- `E242` zh `#/fixture/member-evidence`：需要处理的事项，按处理团队（8 个事项） ‹ 处理团队 coordination-team 示例处理团队：6 个事项 › 默认处理角色（规则给出的默认，不是指派）：model-coordination 处理团队是记录里的安排，不代表已经派发。；en `#/`：Items still to be dealt with in a model handover ‹ For a BIM manager: what a pre-handover check found; after a recheck, which conclusions changed, which items st › Available now: simulated examples, and one limited product validation
- `E243` zh `#/fixture/member-evidence`：跳到正文 › 当前：中文；en `#/`：Skip to the content › Current: English
- `E244` zh `#/fixture/recheck-requirement-relaxed`：6 个事项：记录没有给出后续处理动作 ‹ 模型：两侧模型都没有重新发布（版本未变）。 › 1 个事项的结论和复检前不同：；en `#/fixture/recheck-requirement-relaxed`：6 items: the record gives no follow-up action ‹ Models: Neither model was re-issued (versions unchanged). › 1 item's conclusion differs from before the recheck:
- `E245` zh `#/fixture/recheck-requirement-relaxed`：模型：两侧模型都没有重新发布（版本未变）。 ‹ 1 个事项的结论和复检前不同： › building element ｜ 房间数据表与设备明细表：复检前 受阻 → 现在 可以开始；en `#/fixture/recheck-requirement-relaxed`：Models: Neither model was re-issued (versions unchanged). ‹ 1 item's conclusion differs from before the recheck: › building element \| Room data sheets and equipment schedules: before th
- `E246` zh `#/fixture/recheck-requirement-relaxed`：模型：两侧模型都没有重新发布（版本未变）。 ‹ 1 个事项的结论和复检前不同： › building element ｜ 房间数据表与设备明细表：复检前 受阻 → 现在 可以开始；en `#/fixture/recheck-member-gone`：A determination made against an old version cannot be attributed to th ‹ 2 items' conclusions differ from before the recheck: › chimney cover \| Reflected ceiling and bulkhead layout: before the rech
- `E247` zh `#/fixture/recheck-requirement-relaxed`：两侧模型都没有重新发布，这些项的判断却变了：变化不来自模型改动。每一项的旧证据写明变了的是什么。 ‹ 复检前引用的 15 条旧证据里，有 2 条的检查要求变了。 › 需要处理的事项（7 个事项）；en `#/fixture/recheck-requirement-relaxed`：Neither model was re-issued, yet these conclusions changed: the change ‹ Of the old evidence cited before the recheck (15 in all), the check requirement changed for 2. › Items to deal with (7 items)
- `E248` zh `#/fixture/member-evidence`：一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。同一个构件可以出现在几个事项里，所以事项数不是缺陷数。这份记录共 ‹ 需要处理的事项，按处理团队（8 个事项） › 处理团队 coordination-team 示例处理团队：6 个事项；en `#/fixture/recheck-comparison`：The record gives no action for any item. ‹ Items to check by hand (1 item) › The record does not say what these items' conclusions are now. An elem
- `E249` zh `#/fixture/member-evidence`：一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。同一个构件可以出现在几个事项里，所以事项数不是缺陷数。这份记录共 ‹ 需要处理的事项，按处理团队（8 个事项） › 处理团队 coordination-team 示例处理团队：6 个事项；en `#/fixture/member-evidence`：An item is the conclusion for one element (or a pair of elements asses ‹ Items to deal with, by handling team (8 items) › Handling team coordination-team Example handling team: 6 items
- `E250` zh `#/fixture/recheck-requirement-relaxed`：记录同时显示：和这一项放在一起评估的旧证据里，有 2 条的检查要求变了；记录不说明是放宽还是收紧。读这个结论时要一并看，逐条见“复检前的证据 ‹ 本预览做不了的事 › 发起新的复检或上传新模型；en `#/fixture/recheck-requirement-relaxed`：The record also shows that, among the old evidence assessed together w ‹ What this preview cannot do › Start a new recheck or upload a new model
- `E251` zh `#/fixture/recheck-requirement-relaxed`：导出复检记录 ‹ 这些动作没有实现，所以页面上没有对应的按钮。 › 如何阅读这一页；en `#/fixture/recheck-requirement-relaxed`：Export a recheck record ‹ These actions are not implemented, so the page has no buttons for them. › How to read this page
- `E252` zh `#/fixture/recheck-requirement-relaxed`：处理团队取自记录里的人员安排；默认处理角色是规则给出的默认，是安排的输入，不是指派。两者分开显示。 ‹ 读复检结果时 › “比较依据一致”不代表整个交接不用复核。；en `#/fixture/recheck-requirement-relaxed`：The handling team is taken from the staffing in the record; the defaul ‹ When reading a recheck result › "Comparison basis unchanged" does not mean the whole handover needs no
- `E253` zh `#/fixture/member-evidence`：跳到正文 › 当前：中文；en `#/`：English ‹ Items still to be dealt with in a model handover › For a BIM manager: what a pre-handover check found; after a recheck, w
- `E254` zh `#/fixture/recheck-requirement-relaxed`：“无法比较”不是“证据缺失”：旧记录没保存比较依据时，本页如实显示无法比较。 ‹ 复检前后的比较明细：模型、事项、旧证据 › 模型；en `#/fixture/recheck-requirement-relaxed`："Cannot be compared" is not "evidence missing": where the old record k ‹ Before-and-after details: models, items, old evidence › Models
- `E256` zh `#/fixture/recheck-requirement-relaxed`：本页只说明哪一侧变了、记录证明了什么，不根据重新发布的方向预判好坏。 ‹ 复检前记录里的事项（13 个），现在的情况 › 仍在本次检查范围内；判断与条件另看 × 13；en `#/fixture/recheck-comparison`：This page only says which side changed and what the record shows; it d ‹ The item in the record before the recheck (1), and where it stands now › These two elements are no longer paired for checking; that does not me
- `E257` zh `#/fixture/recheck-requirement-relaxed`：本页只说明哪一侧变了、记录证明了什么，不根据重新发布的方向预判好坏。 ‹ 复检前记录里的事项（13 个），现在的情况 › 仍在本次检查范围内；判断与条件另看 × 13；en `#/fixture/recheck-requirement-relaxed`：This page only says which side changed and what the record shows; it d ‹ The items in the record before the recheck (13), and where they stand now › Still in this check's scope; conclusion and condition are read separat
- `E258` zh `#/fixture/recheck-requirement-relaxed`：仍在本次检查范围内；判断与条件另看 × 13 ‹ 复检前引用的旧证据（15 条），和本次记录比较的结果 › 检查结果和人工判定是两种证据，分开计数，不相加。
- `E259` zh `#/fixture/recheck-requirement-relaxed`：仍在本次检查范围内；判断与条件另看 × 13 ‹ 复检前引用的旧证据（15 条），和本次记录比较的结果 › 检查结果和人工判定是两种证据，分开计数，不相加。；en `#/fixture/recheck-requirement-relaxed`：Still in this check's scope; conclusion and condition are read separat ‹ The old evidence cited before the recheck (15 rows), compared with this record › Check results and human determinations are two kinds of evidence, coun
- `E260` zh `#/fixture/recheck-requirement-relaxed`：复检前引用的旧证据（15 条），和本次记录比较的结果 ‹ 检查结果和人工判定是两种证据，分开计数，不相加。 › 检查结果引用（9 条）；en `#/fixture/recheck-requirement-relaxed`：The old evidence cited before the recheck (15 rows), compared with thi ‹ Check results and human determinations are two kinds of evidence, counted apart and never added together. › Check-result citation (9 rows)
- `E261` zh `#/fixture/recheck-requirement-relaxed`：这条旧证据在本次记录里有唯一对应的一条，但至少有一个方面不同。结果读起来相同，也仍然算有变化；变了的是哪些方面，见这一条的说明。 ‹ 追溯信息：记录标识、模型版本指纹、记录原码对照 › 这份记录的请求范围、版本与来源（该页尚未改版，仍是内部用语）；en `#/fixture/recheck-requirement-relaxed`：This old evidence has exactly one counterpart in this record, but at l ‹ Tracing: record identity, model version fingerprints, record codes › This record's requested scope, versions and sources (Chinese only: tha
- `E262` zh `#/fixture/recheck-requirement-relaxed`：recheck ‹ 复检前记录的指纹（assessment digest） › 6c524a06485f4f309a54ce76ce9ba39a628ba8f49d777d33c5e841fe348282e0复制；en `#/fixture/recheck-requirement-relaxed`：recheck ‹ Fingerprint of the record before the recheck (assessment digest) › 6c524a06485f4f309a54ce76ce9ba39a628ba8f49d777d33c5e841fe348282e0Copy
- `E263` zh `#/fixture/recheck-requirement-relaxed`：6c524a06485f4f309a54ce76ce9ba39a628ba8f49d777d33c5e841fe348282e0复制 ‹ 本记录的指纹（assessment digest） › 506bf207cd74279a0e895ffe8f72db743bf63159f8aa8262c06818a7b1658bb5复制；en `#/fixture/recheck-requirement-relaxed`：6c524a06485f4f309a54ce76ce9ba39a628ba8f49d777d33c5e841fe348282e0Copy ‹ Fingerprint of this record (assessment digest) › 506bf207cd74279a0e895ffe8f72db743bf63159f8aa8262c06818a7b1658bb5Copy
- `E264` zh `#/fixture/recheck-requirement-relaxed`：changed_models ‹ （记录中为空列表：没有模型变化） › 复检前记录；en `#/fixture/recheck-requirement-relaxed`：changed_models ‹ (an empty list in the record: no model changed) › Side
- `E265` en `#/fixture/recheck-requirement-relaxed`：This recheck uses the same pair of model versions as the original reco ‹ Side of the handover › Role (from this request's handover)
- `E266` zh `#/fixture/recheck-requirement-relaxed`：本页只说明哪一侧变了、记录证明了什么，不根据重新发布的方向预判好坏。 ‹ 复检前记录里的事项（13 个），现在的情况 › 仍在本次检查范围内；判断与条件另看 × 13；en `#/fixture/recheck-requirement-relaxed`：Side ‹ Record before the recheck › This record
- `E267` zh `#/fixture/recheck-requirement-relaxed`：6c524a06485f4f309a54ce76ce9ba39a628ba8f49d777d33c5e841fe348282e0复制 ‹ 本记录的指纹（assessment digest） › 506bf207cd74279a0e895ffe8f72db743bf63159f8aa8262c06818a7b1658bb5复制；en `#/fixture/recheck-requirement-relaxed`：Back to the home page ‹ A simulated example shipped with the tool, not your model; project settings such as teams are for demonstratio › Simulated example: the project settings in the example, including the
- `E268` zh `#/fixture/recheck-requirement-relaxed`：architecture 3ff9b10bd00c7b96dded51e7ca5a6b69efbea38b049adcdd05fcd247d ‹ 版本以内容指纹表示，不以文件名当版本。哪一侧变了取自记录的 changed_models，本页不比较指纹。 › 事项现在的情况：记录原码；en `#/fixture/recheck-requirement-relaxed`：architecture 3ff9b10bd00c7b96dded51e7ca5a6b69efbea38b049adcdd05fcd247d ‹ A version is a content fingerprint, not a file name. Which side changed is taken from the record's changed_mod › Where items stand now: record codes
- `E269` zh `#/fixture/recheck-requirement-relaxed`：版本以内容指纹表示，不以文件名当版本。哪一侧变了取自记录的 changed_models，本页不比较指纹。 ‹ 事项现在的情况：记录原码 › 记录里的代码；en `#/fixture/recheck-requirement-relaxed`：A version is a content fingerprint, not a file name. Which side change ‹ Where items stand now: record codes › Code in the record
- `E270` zh `#/fixture/recheck-requirement-relaxed`：本次未声明该范围，不等于问题解除 ‹ 复检前留下的条件：状态原码（没有“整句条件已满足”） › 记录里的代码；en `#/fixture/recheck-requirement-relaxed`：This scope was not declared this time; that does not mean the problem  ‹ Conditions left before the recheck: state codes (there is no "the whole condition is met") › Code in the record
- `E271` zh `#/fixture/recheck-requirement-relaxed`：原记录没有复检条件 ‹ 旧证据比较：状态原码 › 记录里的代码；en `#/fixture/recheck-requirement-relaxed`：The original record had no recheck condition ‹ Old-evidence comparison: state codes › Code in the record
- `E272` zh `#/fixture/recheck-requirement-relaxed`：现有依据不足以比较 ‹ 旧证据比较：原因原码 › 记录里的代码；en `#/fixture/recheck-requirement-relaxed`：Not enough basis to compare ‹ Old-evidence comparison: reason codes › Code in the record
- `E273` zh `#/fixture/recheck-requirement-relaxed`：模型版本已经变化，原判定是针对旧版本作出的，不能归到当前版本。不是证据不存在，也不是原判定错误；需要针对当前版本的判定。 ‹ 变化方面：原码 › 记录里的代码；en `#/fixture/recheck-requirement-relaxed`：The model version has changed, and the original determination was made ‹ Aspects that changed: codes › Code in the record

#### RECHECK_CANNOT（5 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E274 | `[0]` | Start a new recheck or upload a new model | 发起新的复检或上传新模型 | 10/8 已核 | zh 151｜en 151｜示例主线、其他示例 |
| E275 | `[1]` | Mark an item resolved, closed or risk-accepted | 把事项标记为已解决、关闭或接受风险 | 10/8 已核 | zh 151｜en 151｜示例主线、其他示例 |
| E276 | `[2]` | Assign or notify anyone | 指派或通知责任人 | 10/8 已核 | zh 151｜en 151｜示例主线、其他示例 |
| E277 | `[3]` | Open or locate an element in Revit | 在 Revit 中打开或定位构件 | 10/8 已核 | zh 151｜en 151｜示例主线、其他示例 |
| E278 | `[4]` | Export a recheck record | 导出复检记录 | 10/8 已核 | zh 151｜en 151｜示例主线、其他示例 |

#### RECHECK_ITEM（24 条，待核 23）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E280 | `back` | ← Back to the recheck items (to this item's place) | ← 返回复检事项列表（回到这一项的位置） | B 层，10/8 未核 | zh 131｜en 131｜示例主线、其他示例 |
| E281 | `kicker` | Recheck item · {count} | 复检事项 · {count} | B 层，10/8 未核 | zh 131｜en 131｜示例主线、其他示例 |
| E283 | `model` | Models | 模型 | 同句已核 | zh 336｜en 177｜示例主线、本地结果页、本地检查（选文件至运行）、其他示例、次要明细页；复用 G027、G028 |
| E284 | `actionHeading` | 2. What to do, who deals with it, what a recheck must show | 二、要做什么、由谁处理、完成后拿什么复检 | B 层，10/8 未核 | zh 147｜en 147｜示例主线、其他示例；复用 G031 |
| E285 | `whichOne` | 3. Which element | 三、是哪个构件 | B 层，10/8 未核 | zh 132｜en 132｜示例主线、其他示例 |
| E286 | `whichTwo` | 3. Which two elements | 三、是哪两个构件 | B 层，10/8 未核 | zh 25｜en 25｜示例主线、其他示例 |
| E288 | `conditionHeading` | 4. Was the exit condition left before the recheck reached this time? | 四、复检前留下的结束条件，这次达到了吗 | B 层，10/8 未核 | zh 131｜en 131｜示例主线、其他示例 |
| E289 | `priorCondition` | The exit condition left before the recheck: {text} | 复检前留下的结束条件：{text}。 | B 层，10/8 未核 | zh 81｜en 81｜示例主线、其他示例 |
| E291 | `conditionNote` | This says only how far the exit condition left before the recheck has been shown to be reached; read it apart from the conclusion now. A changed conclusion does not mean… | 这里只说复检前留下的结束条件被证明到了什么程度，与现在的结论分开读：结论变了，不等于原条件已满足。 | B 层，10/8 未核 | zh 131｜en 131｜示例主线、其他示例 |
| E292 | `originalSummary` | Source wording and record codes: for tracing, not an instruction | 来源原文（英文）与记录原码：供追溯，不是操作指令 | B 层，10/8 未核 | zh 131｜en 131｜示例主线、其他示例 |
| E293 | `conditionBasis` | condition_basis (as written) | condition_basis（原文） | B 层，10/8 未核 | zh 131｜en 131｜示例主线、其他示例 |
| E294 | `evidenceHeading` | 5. The evidence before the recheck | 五、复检前的证据 | B 层，10/8 未核 | zh 131｜en 131｜示例主线、其他示例 |
| E295 | `evidenceCount.one` | {count} piece of old evidence was assessed together with this item | 和这一项放在一起评估的旧证据共 {count} 条 | B 层，10/8 未核 | zh 91｜en 10｜示例主线、其他示例；复用 G032 |
| E296 | `evidenceCount.other` | {count} pieces of old evidence were assessed together with this item | 和这一项放在一起评估的旧证据共 {count} 条 | B 层，10/8 未核 | zh 91｜en 81｜示例主线、其他示例；复用 G032 |
| E297 | `requirementChanged.one` | , and for {count} of them the check requirement changed | ，其中 {count} 条的检查要求变了 | B 层，10/8 未核 | zh 9｜en 9｜示例主线、其他示例；复用 G033 |
| E298 | `requirementChanged.other` | , and for {count} of them the check requirement changed | ，其中 {count} 条的检查要求变了 | B 层，10/8 未核 | zh 9｜en 9｜示例主线、其他示例；复用 G033 |
| E299 | `priorSources` | Evidence cited before the recheck, by source: | 复检前引用的证据，来源： | B 层，10/8 未核 | zh 91｜en 91｜示例主线、其他示例 |
| E300 | `currentSources` | Corresponding evidence this record cites, by source: | 本次记录引用的对应证据，来源： | B 层，10/8 未核 | zh 91｜en 91｜示例主线、其他示例 |
| E301 | `rowsSummary` | See each piece of old evidence and how it compared | 逐条查看旧证据和比较结果 | B 层，10/8 未核 | zh 91｜en 91｜示例主线、其他示例 |
| E302 | `shared.one` | The record keeps the old evidence of a group of elements assessed together in one place, not split by element: the group's {count} item shares the rows below. | 记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 {count} 个事项共用下面这些行。 | B 层，10/8 未核 | zh 91｜en 31｜示例主线、其他示例；复用 G034 |
| E303 | `shared.other` | The record keeps the old evidence of a group of elements assessed together in one place, not split by element: the group's {count} items share the rows below. | 记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 {count} 个事项共用下面这些行。 | B 层，10/8 未核 | zh 91｜en 60｜示例主线、其他示例；复用 G034 |
| E304 | `noEvidence` | The group's evidence path before the recheck cites no evidence. | 复检前这一组的证据路径没有引用任何证据。 | B 层，10/8 未核 | zh 40｜en 40｜示例主线、其他示例 |
| E305 | `priorOrdinal` | Internal group number before the recheck | 复检前的内部分组编号 | B 层，10/8 未核 | zh 131｜en 131｜示例主线、其他示例 |
| E306 | `currentLine` | Current internal group number, verdict and final outcome | 现在的内部分组编号、verdict 与终点 outcome | B 层，10/8 未核 | zh 131｜en 131｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E280` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的 ‹ ← 返回复检事项列表（回到这一项的位置） › 复检事项 · 一个构件；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：Simulated example: the project settings in the example, including the  ‹ ← Back to the recheck items (to this item's place) › Recheck item · One element
- `E281` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：← 返回复检事项列表（回到这一项的位置） ‹ 复检事项 · 一个构件 › building element；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：← Back to the recheck items (to this item's place) ‹ Recheck item · One element › building element
- `E284` zh `#/fixture/member-evidence/item/0/2/0`：要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。 ‹ 二、要做什么、由谁处理、完成后拿什么复检 › 要做什么；en `#/fixture/member-evidence/item/0/2/0`：Needs to know where MEP penetrates architectural fabric, so openings c ‹ 2. What to do, who deals with it, what a recheck must show › What to do
- `E285` zh `#/fixture/member-evidence/item/0/1/0`：记录没有为这一项给出后续处理动作、处理团队或默认处理角色。 ‹ 三、是哪个构件 › building element；en `#/fixture/member-evidence/item/0/1/0`：The record gives no follow-up action, handling team or default handlin ‹ 3. Which element › building element
- `E286` zh `#/fixture/member-evidence/item/0/3/0`：记录没有为这一项给出后续处理动作、处理团队或默认处理角色。 ‹ 三、是哪两个构件 › house - chimney；en `#/fixture/member-evidence/item/0/3/0`：The record gives no follow-up action, handling team or default handlin ‹ 3. Which two elements › house - chimney
- `E288` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：名称取自模型文件本身，可能为空，也可能与别的构件重名；要在模型里定位，请用 GlobalId。 ‹ 四、复检前留下的结束条件，这次达到了吗 › 原记录没有复检条件：原来的判断没有留下待办。；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：The name is taken from the model file itself; it may be empty or share ‹ 4. Was the exit condition left before the recheck reached this time? › The original record had no recheck condition: the original conclusion
- `E289` zh `#/fixture/recheck-requirement-relaxed/recheck/1/0`：原复检条件没有机器能检查的部分，需要人阅读原条件并判断；记录对它不下结论。 ‹ 复检前留下的结束条件：针对所列模型版本，有一份评审判定记录。 › 这里只说复检前留下的结束条件被证明到了什么程度，与现在的结论分开读：结论变了，不等于原条件已满足。；en `#/fixture/recheck-requirement-relaxed/recheck/1/0`：The original recheck condition has no part a machine can check; a pers ‹ The exit condition left before the recheck: A recorded review determination exists for the model versions list › This says only how far the exit condition left before the recheck has
- `E291` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：原记录没有复检条件：原来的判断没有留下待办。 ‹ 这里只说复检前留下的结束条件被证明到了什么程度，与现在的结论分开读：结论变了，不等于原条件已满足。 › 来源原文（英文）与记录原码：供追溯，不是操作指令；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：The original record had no recheck condition: the original conclusion  ‹ This says only how far the exit condition left before the recheck has been shown to be reached; read it apart  › Source wording and record codes: for tracing, not an instruction
- `E292` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：这里只说复检前留下的结束条件被证明到了什么程度，与现在的结论分开读：结论变了，不等于原条件已满足。 ‹ 来源原文（英文）与记录原码：供追溯，不是操作指令 › prior_recheck_condition；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：This says only how far the exit condition left before the recheck has  ‹ Source wording and record codes: for tracing, not an instruction › prior_recheck_condition
- `E293` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：no-recheck-condition 原记录没有复检条件 ‹ condition_basis（原文） › the cited subscope is READY and carries no resolution route, so there；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：no-recheck-condition The original record had no recheck condition ‹ condition_basis (as written) › the cited subscope is READY and carries no resolution route, so there
- `E294` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：penetration-determination ‹ 五、复检前的证据 › 和这一项放在一起评估的旧证据共 1 条。；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：penetration-determination ‹ 5. The evidence before the recheck › 1 piece of old evidence was assessed together with this item.
- `E295` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：五、复检前的证据 ‹ 和这一项放在一起评估的旧证据共 1 条。 › 复检前引用的证据，来源：模拟的人工判定 ×1；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：5. The evidence before the recheck ‹ 1 piece of old evidence was assessed together with this item. › Evidence cited before the recheck, by source: Simulated human determin
- `E296` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：五、复检前的证据 ‹ 和这一项放在一起评估的旧证据共 1 条。 › 复检前引用的证据，来源：模拟的人工判定 ×1；en `#/fixture/recheck-requirement-relaxed/recheck/2/0`：5. The evidence before the recheck ‹ 2 pieces of old evidence were assessed together with this item. › Evidence cited before the recheck, by source: Simulated human determin
- `E297` zh `#/fixture/recheck-requirement-relaxed/recheck/7/0`：五、复检前的证据 ‹ 和这一项放在一起评估的旧证据共 6 条，其中 2 条的检查要求变了。 › 复检前引用的证据，来源：真实检查输出 ×6；en `#/fixture/recheck-requirement-relaxed/recheck/7/0`：5. The evidence before the recheck ‹ 6 pieces of old evidence were assessed together with this item, and for 2 of them the check requirement change › Evidence cited before the recheck, by source: Real check output ×6
- `E298` zh `#/fixture/recheck-requirement-relaxed/recheck/7/0`：五、复检前的证据 ‹ 和这一项放在一起评估的旧证据共 6 条，其中 2 条的检查要求变了。 › 复检前引用的证据，来源：真实检查输出 ×6；en `#/fixture/recheck-requirement-relaxed/recheck/7/0`：5. The evidence before the recheck ‹ 6 pieces of old evidence were assessed together with this item, and for 2 of them the check requirement change › Evidence cited before the recheck, by source: Real check output ×6
- `E299` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：和这一项放在一起评估的旧证据共 1 条。 ‹ 复检前引用的证据，来源：模拟的人工判定 ×1 › 本次记录引用的对应证据，来源：；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：1 piece of old evidence was assessed together with this item. ‹ Evidence cited before the recheck, by source: Simulated human determination ×1 › Corresponding evidence this record cites, by source:
- `E300` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：复检前引用的证据，来源：模拟的人工判定 ×1 ‹ 本次记录引用的对应证据，来源： › 逐条查看旧证据和比较结果；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：Evidence cited before the recheck, by source: Simulated human determin ‹ Corresponding evidence this record cites, by source: › See each piece of old evidence and how it compared
- `E301` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：本次记录引用的对应证据，来源： ‹ 逐条查看旧证据和比较结果 › 记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 1 个事项共用下面这些行。；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：Corresponding evidence this record cites, by source: ‹ See each piece of old evidence and how it compared › The record keeps the old evidence of a group of elements assessed toge
- `E302` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：逐条查看旧证据和比较结果 ‹ 记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 1 个事项共用下面这些行。 › “比较依据一致”是什么意思；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：See each piece of old evidence and how it compared ‹ The record keeps the old evidence of a group of elements assessed together in one place, not split by element: › What "Comparison basis unchanged" means
- `E303` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：逐条查看旧证据和比较结果 ‹ 记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 1 个事项共用下面这些行。 › “比较依据一致”是什么意思；en `#/fixture/recheck-requirement-relaxed/recheck/5/0`：See each piece of old evidence and how it compared ‹ The record keeps the old evidence of a group of elements assessed together in one place, not split by element: › What "Comparison basis unchanged" means
- `E304` zh `#/fixture/recheck-requirement-relaxed/recheck/1/0`：五、复检前的证据 ‹ 复检前这一组的证据路径没有引用任何证据。 › 本预览做不了的事；en `#/fixture/recheck-requirement-relaxed/recheck/1/0`：5. The evidence before the recheck ‹ The group's evidence path before the recheck cites no evidence. › What this preview cannot do
- `E305` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：interdisciplinary-coordination-readiness::builders-work-openings ‹ 复检前的内部分组编号 › #1；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：interdisciplinary-coordination-readiness::builders-work-openings ‹ Internal group number before the recheck › #1
- `E306` zh `#/fixture/recheck-requirement-relaxed/recheck/0/0`：present ‹ 现在的内部分组编号、verdict 与终点 outcome › #1 READY no-penetration；en `#/fixture/recheck-requirement-relaxed/recheck/0/0`：present ‹ Current internal group number, verdict and final outcome › #1 READY no-penetration

#### RECHECK_LIMITS（5 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E307 | `[0]` | "Comparison basis unchanged" does not mean the whole handover needs no review. | “比较依据一致”不代表整个交接不用复核。 | 10/8 已核 | zh 151｜en 151｜示例主线、其他示例 |
| E308 | `[1]` | An element that is gone, or evidence with no counterpart, does not mean the problem was fixed. | 构件不在了、或找不到对应证据，不代表问题已修复。 | 10/8 已核 | zh 151｜en 151｜示例主线、其他示例 |
| E309 | `[2]` | A model re-issued (on either side) does not mean a fix has happened. | 模型重新发布（不论哪一侧）不代表修复已经发生。 | 10/8 已核 | zh 151｜en 151｜示例主线、其他示例 |
| E310 | `[3]` | "Only the model version changed" does not mean the check result's content changed. | “只有模型版本变了”不等于检查结果的内容变了。 | 10/8 已核 | zh 151｜en 151｜示例主线、其他示例 |
| E311 | `[4]` | "Cannot be compared" is not "evidence missing": where the old record kept no comparison basis, this page says honestly that it cannot compare. | “无法比较”不是“证据缺失”：旧记录没保存比较依据时，本页如实显示无法比较。 | 10/8 已核 | zh 151｜en 151｜示例主线、其他示例 |

#### REISSUE_CASES（2 条，待核 2）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E327 | `none.headline` | Neither model was re-issued (versions unchanged) | 两侧模型都没有重新发布（版本未变） | 10/15 批，未核 | zh 76｜en 76｜示例主线、其他示例 |
| E328 | `none.detail` | This recheck uses the same pair of model versions as the original record, so the differences below do not come from model edits. | 本次复检和原记录用的是同一对模型版本，所以下面的差异不来自模型改动。 | 10/15 批，未核 | zh 10｜en 10｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E327` zh `#/fixture/recheck-requirement-relaxed`：6 个事项：记录没有给出后续处理动作 ‹ 模型：两侧模型都没有重新发布（版本未变）。 › 1 个事项的结论和复检前不同：；en `#/fixture/recheck-requirement-relaxed`：6 items: the record gives no follow-up action ‹ Models: Neither model was re-issued (versions unchanged). › 1 item's conclusion differs from before the recheck:
- `E328` zh `#/fixture/recheck-requirement-relaxed`：两侧模型都没有重新发布（版本未变） ‹ 本次复检和原记录用的是同一对模型版本，所以下面的差异不来自模型改动。 › 交接的哪一侧；en `#/fixture/recheck-requirement-relaxed`：Neither model was re-issued (versions unchanged) ‹ This recheck uses the same pair of model versions as the original record, so the differences below do not come › Side of the handover

#### REISSUE_NEUTRAL（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E343 | `(整表)` | This page only says which side changed and what the record shows; it does not judge good or bad from the direction of a re-issue. | 本页只说明哪一侧变了、记录证明了什么，不根据重新发布的方向预判好坏。 | 10/15 批，未核 | zh 20｜en 20｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E343` zh `#/fixture/recheck-requirement-relaxed`：没有变（原版本） ‹ 本页只说明哪一侧变了、记录证明了什么，不根据重新发布的方向预判好坏。 › 复检前记录里的事项（13 个），现在的情况；en `#/fixture/recheck-requirement-relaxed`：Unchanged (original version) ‹ This page only says which side changed and what the record shows; it does not judge good or bad from the direc › The items in the record before the recheck (13), and where they stand

#### REQUIREMENT_CHANGED_NOTE（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E344 | `(整表)` | The record also shows that, among the old evidence assessed together with this item, the check requirement changed for {count}; the record does not say whether it was re… | 记录同时显示：和这一项放在一起评估的旧证据里，有 {count} 条的检查要求变了；记录不说明是放宽还是收紧。读这个结论时要一并看，逐条见“复检前的证据”。 | 10/15 批，未核 | zh 13｜en 13｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E344` zh `#/fixture/recheck-requirement-relaxed`：只对这一个事项、这项工作、所列的模型版本成立；不代表整次交接完成。 ‹ 记录同时显示：和这一项放在一起评估的旧证据里，有 2 条的检查要求变了；记录不说明是放宽还是收紧。读这个结论时要一并看，逐条见“复检前的证据”。 › 两侧模型都没有重新发布，这些项的判断却变了：变化不来自模型改动。每一项的旧证据写明变了的是什么。；en `#/fixture/recheck-requirement-relaxed`：Holds for this one item, this work and the listed model versions only; ‹ The record also shows that, among the old evidence assessed together with this item, the check requirement cha › Neither model was re-issued, yet these conclusions changed: the change

#### RESOLUTION_KINDS（5 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E345 | `missing-project-asset-identity` | The project's required asset identity is missing | 缺少本项目约定的资产标识 | 10/8 已核 | zh 34｜en 34｜示例主线、其他示例 |
| E346 | `asset-identity-not-evaluated` | Not a known model defect: the existing asset-identity rules did not cover this element | 不是已知的模型缺陷：现有资产标识规则没有覆盖到这个构件 | 10/8 已核 | zh 16｜en 16｜示例主线、其他示例 |
| E348 | `in-model-position-not-evaluated` | Not a known model defect: the storey or space check did not cover it | 不是已知的模型缺陷：楼层或空间归属的检查没有覆盖到它 | 10/8 已核 | zh 16｜en 16｜示例主线、其他示例 |
| E351 | `penetration-not-determined` | Not a known model defect: no coordination review has determined yet whether it passes through the receiving side's elements | 不是已知的模型缺陷：还没有协调评审判定它是否穿过接收方的构件 | 10/8 已核 | zh 32｜en 32｜示例主线、其他示例 |
| E353 | `missing-corresponding-opening` | No corresponding opening is modelled in the element it passes through | 它穿过的构件上没有建出对应的洞口 | 10/8 已核 | zh 11｜en 11｜示例主线、其他示例 |

#### RULE_NOTES（18 条，待核 3）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E355 | `PV-001.title` | Air terminals declare one of four predefined types | 风口要声明四种预定义类型之一 | 10/8 已核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| E356 | `PV-001.predicate` | Every applicable air terminal (IfcAirTerminal) declares a predefined type of DIFFUSER, GRILLE, LOUVRE or REGISTER. IFC4 also admits USERDEFINED and NOTDEFINED; not accep… | 每个适用的风口（IfcAirTerminal）都要声明预定义类型，取值是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一。IFC4 还允许 USERDEFINED 和 NOTDEFINED；不接受… | 10/8 已核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| E357 | `PV-001.passProves` | The one value the checker took in its reading order (the type's value first; a USERDEFINED type's free text; the element instance only when the type says nothing, and wi… | 检查器按它的读取顺序取到的那一个值（类型上的值优先；类型声明 USERDEFINED 时是它的自由文本；类型什么也没说时才读构件实例；没有类型时，实例声明 USERDEFINED 也是它的自由文本），逐字等于 DIFF… | 10/8 后改句，需重核 | zh 1｜en 1｜本地结果页 |
| E358 | `PV-001.passDoesNotProve[0]` | That the value is right: any of the four passes; GRILLE passes too. | 取值正确：四个值中任何一个都会通过，写成 GRILLE 也会通过。 | 10/8 已核 | zh 1｜en 1｜本地结果页 |
| E359 | `PV-001.passDoesNotProve[1]` | That the type and the element instance agree: when the type carries one of the four, the instance's value is not compared; type LOUVRE with instance DIFFUSER also passes. | 类型和构件实例的取值一致：类型上是四个值之一时，实例上写的值不参与比较；类型是 LOUVRE、实例是 DIFFUSER，也会通过。 | 10/8 已核 | zh 1｜en 1｜本地结果页 |
| E360 | `PV-001.passDoesNotProve[2]` | That no USERDEFINED, which the rule does not accept, is present: when the type declares USERDEFINED, the checker compares its free text; with no type, an element instanc… | 规则不接受的 USERDEFINED 没有出现：类型声明 USERDEFINED 时，检查器比较的是它的自由文本；没有类型时，构件实例声明 USERDEFINED 也按它的自由文本比较。比较逐字、区分大小写；文本恰好是… | 10/8 后改句，需重核 | zh 1｜en 1｜本地结果页 |
| E361 | `PV-001.passDoesNotProve[3]` | That the wall has a corresponding opening. | 墙上有对应的洞口。 | 10/8 已核 | zh 1｜en 1｜本地结果页 |
| E362 | `PV-001.passDoesNotProve[4]` | That the air terminal's model and the model of the wall it sits in are aligned. | 风口所在的模型与风口所在的墙所属的模型已经对齐。 | 10/8 已核 | zh 1｜en 1｜本地结果页 |
| E363 | `PV-001.passDoesNotProve[5]` | That any work can start, including ceiling and opening work. | 任何工作可以开始，包括吊顶和开洞工作。 | 10/8 已核 | zh 1｜en 1｜本地结果页 |
| E364 | `PV-001.action.what` | Go back to the Revit source model and make this air terminal's exported predefined type one of DIFFUSER, GRILLE, LOUVRE and REGISTER; re-export the IFC and check again.… | 回到 Revit 源模型，让这个风口导出后的预定义类型是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一；重新导出 IFC，再检查。NOTDEFINED 等于什么都没说。 | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E365 | `PV-001.action.reads` | The checker looks first at its type object in the exported IFC: if the type carries one of the four, the type's value is compared; if the type declares USERDEFINED, its… | 检查器先看导出的 IFC 里它的类型对象：类型上是四个值之一，比较类型上的值；类型声明 USERDEFINED，比较它的自由文本；类型什么也没说时，才读构件实例本身的值。这说的是检查器读 IFC 的顺序，不是 Revi… | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E366 | `PV-001.action.revise` | Where this value is written from in Revit (type or instance, which parameter, which export setting), the returned data does not record, and this page does not say. Confi… | 这个值在 Revit 里从哪里写出（类型还是实例、哪个参数、哪项导出设置），返回数据没有记录，本页不指定。改之前先在 Revit 里确认；如果决定在类型上改，会作用于这个类型的全部实例。一个 Revit 类型可能对应不… | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E367 | `PV-001.action.undecided` | Which value to use, and who decides and makes the change, the returned data does not say. The rule asks only for one of the four values and does not judge which is right. | 取哪一个值、由谁决定和操作，返回数据都没有提供。规则只要求四个值之一，不判断哪一个对。 | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E368 | `PV-001.recheck` | Check again with the same rule set version, the same set of models and the same export settings, and look at this element's result under this requirement. | 用同一规则集版本、同一组模型和同一导出设置重新检查，看这个构件在这条要求下的结果。 | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E369 | `PV-001.gaps[0]` | The opening in the wall the air terminal sits in: a coordination-review determination is needed, made against the air terminal's model and the model of that wall; this c… | 风口所在的墙上的洞口：需要对照风口所在的模型和这面墙所属的模型做协调评审判定；这项检查不比较两个模型的构件。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E370 | `PV-001.gaps[1]` | Whether the air terminal's model and the model of the wall it sits in are aligned: an alignment confirmation record is needed. | 风口所在的模型与风口所在的墙所属的模型是否对齐：需要一份对齐确认记录。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E371 | `PV-001.gaps[2]` | Whether the value chosen is right: the classification decision has to be recorded separately; a pass cannot prove in reverse that the classification is right. | 取值是否选对：分类判断要另行记录；检查通过不能反过来证明分类判断正确。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E372 | `PV-001.reasonFreeText` | What is in the quotation marks is not an enumeration value but free text: when the type declares USERDEFINED, the checker compares its free text; with no type, the same… | 引号里不是预定义类型的枚举值，而是自由文本：类型声明 USERDEFINED 时，检查器拿它的自由文本来比较；没有类型时，构件实例声明 USERDEFINED 也是这样。 | 10/8 后改句，需重核 | zh 5｜en 5｜本地结果页 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E357` zh `#/local/ce485f9c0c179def/finding/b642cc33-f6ce-586c-a8dd-fe64325b560e`：这条通过证明了什么 ‹ 它证明：检查器按它的读取顺序取到的那一个值（类型上的值优先；类型声明 USERDEFINED 时是它的自由文本；类型什么也没说时才读构件实例；没有类型时，实例声明 USERDEFINED 也是它的自由文本），逐字等于 D › 它不证明：；en `#/local/ce485f9c0c179def/finding/b642cc33-f6ce-586c-a8dd-fe64325b560e`：What this pass proves ‹ It proves: The one value the checker took in its reading order (the type's value first; a USERDEFINED type's f › It does not prove:
- `E360` zh `#/local/ce485f9c0c179def/finding/b642cc33-f6ce-586c-a8dd-fe64325b560e`：类型和构件实例的取值一致：类型上是四个值之一时，实例上写的值不参与比较；类型是 LOUVRE、实例是 DIFFUSER，也会通过。 ‹ 规则不接受的 USERDEFINED 没有出现：类型声明 USERDEFINED 时，检查器比较的是它的自由文本；没有类型时，构件实例声明 USERDEFINED 也按它的自由文本比较。比较逐字、区分大小写；文本恰好是  › 墙上有对应的洞口。；en `#/local/ce485f9c0c179def/finding/b642cc33-f6ce-586c-a8dd-fe64325b560e`：That the type and the element instance agree: when the type carries on ‹ That no USERDEFINED, which the rule does not accept, is present: when the type declares USERDEFINED, the check › That the wall has a corresponding opening.
- `E372` zh `#/local/c653c7e0bb676a4a/finding/eed53402-33a9-5b7a-9d4c-a912e10c4566`：The predefined type "chimney cover" does not meet the required type ‹ 引号里不是预定义类型的枚举值，而是自由文本：类型声明 USERDEFINED 时，检查器拿它的自由文本来比较；没有类型时，构件实例声明 USERDEFINED 也是这样。 › 观察值一栏；en `#/local/c653c7e0bb676a4a/finding/eed53402-33a9-5b7a-9d4c-a912e10c4566`：The predefined type "chimney cover" does not meet the required type ‹ What is in the quotation marks is not an enumeration value but free text: when the type declares USERDEFINED,  › Observed value

#### RUN_LABELS（12 条，待核 12）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E373 | `member-evidence` | A first check: the model was handed over, and these items were found | 一次首次检查：交了模型，发现这些事项 | 10/15 批，未核 | zh 4｜en 3｜示例目录、示例主线、次要明细页 |
| E374 | `pair-verdicts` | The same check record: conclusions on pairs of elements (simulated example) | 同一份检查记录：成对构件的判断（模拟示例） | 10/15 批，未核 | zh 4｜en 3｜示例目录、其他示例、次要明细页 |
| E375 | `recheck-both-reissued` | Recheck record 1 (simulated example) | 复检记录 1（模拟示例） | 10/15 批，未核 | zh 4｜en 3｜示例目录、其他示例、次要明细页 |
| E376 | `recheck-comparison` | Recheck record 2 (simulated example) | 复检记录 2（模拟示例） | 10/15 批，未核 | zh 4｜en 3｜示例目录、其他示例、次要明细页 |
| E377 | `recheck-consuming-reissued` | Recheck record 3 (simulated example) | 复检记录 3（模拟示例） | 10/15 批，未核 | zh 4｜en 3｜示例目录、其他示例、次要明细页 |
| E378 | `recheck-key-change-only` | Recheck record 4 (simulated example) | 复检记录 4（模拟示例） | 10/15 批，未核 | zh 4｜en 3｜示例目录、其他示例、次要明细页 |
| E379 | `recheck-member-gone` | Recheck record 5 (simulated example) | 复检记录 5（模拟示例） | 10/15 批，未核 | zh 4｜en 3｜示例目录、其他示例、次要明细页 |
| E380 | `recheck-prior-without-basis` | Recheck record 6 (simulated example) | 复检记录 6（模拟示例） | 10/15 批，未核 | zh 4｜en 3｜示例目录、其他示例、次要明细页 |
| E381 | `recheck-producing-reissued` | Recheck record 7 (simulated example) | 复检记录 7（模拟示例） | 10/15 批，未核 | zh 4｜en 3｜示例目录、其他示例、次要明细页 |
| E382 | `recheck-producing-reissued-content-changed` | Recheck record 8 (simulated example) | 复检记录 8（模拟示例） | 10/15 批，未核 | zh 4｜en 3｜示例目录、其他示例、次要明细页 |
| E383 | `recheck-requirement-relaxed` | The models did not change, but a handover conclusion did | 模型未改，但交接判断发生变化 | 10/15 批，未核 | zh 19｜en 18｜示例目录、示例主线、次要明细页 |
| E384 | `recheck-semantics-changed` | Recheck record 10 (simulated example) | 复检记录 10（模拟示例） | 10/15 批，未核 | zh 4｜en 3｜示例目录、其他示例、次要明细页 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E373` zh `#/fixture`：第一步 ‹ 一次首次检查：交了模型，发现这些事项 › 交出方交了模型：有哪些事项要处理，各由谁处理，每一项要做什么？；en `#/fixture`：Step 1 ‹ A first check: the model was handed over, and these items were found › The handing-over side has handed over its model: which items need deal
- `E374` zh `#/fixture`：这些示例还没有写说明，复检记录暂时只有编号；本轮没有改到它们。 ‹ 同一份检查记录：成对构件的判断（模拟示例） › 复检记录 1（模拟示例）；en `#/fixture`：These examples have no description yet, and the recheck records have o ‹ The same check record: conclusions on pairs of elements (simulated example) › Recheck record 1 (simulated example)
- `E375` zh `#/fixture`：同一份检查记录：成对构件的判断（模拟示例） ‹ 复检记录 1（模拟示例） › 复检记录 2（模拟示例）；en `#/fixture`：The same check record: conclusions on pairs of elements (simulated exa ‹ Recheck record 1 (simulated example) › Recheck record 2 (simulated example)
- `E376` zh `#/fixture`：复检记录 1（模拟示例） ‹ 复检记录 2（模拟示例） › 复检记录 3（模拟示例）；en `#/fixture`：Recheck record 1 (simulated example) ‹ Recheck record 2 (simulated example) › Recheck record 3 (simulated example)
- `E377` zh `#/fixture`：复检记录 2（模拟示例） ‹ 复检记录 3（模拟示例） › 复检记录 4（模拟示例）；en `#/fixture`：Recheck record 2 (simulated example) ‹ Recheck record 3 (simulated example) › Recheck record 4 (simulated example)
- `E378` zh `#/fixture`：复检记录 3（模拟示例） ‹ 复检记录 4（模拟示例） › 复检记录 5（模拟示例）；en `#/fixture`：Recheck record 3 (simulated example) ‹ Recheck record 4 (simulated example) › Recheck record 5 (simulated example)
- `E379` zh `#/fixture`：复检记录 4（模拟示例） ‹ 复检记录 5（模拟示例） › 复检记录 6（模拟示例）；en `#/fixture`：Recheck record 4 (simulated example) ‹ Recheck record 5 (simulated example) › Recheck record 6 (simulated example)
- `E380` zh `#/fixture`：复检记录 5（模拟示例） ‹ 复检记录 6（模拟示例） › 复检记录 7（模拟示例）；en `#/fixture`：Recheck record 5 (simulated example) ‹ Recheck record 6 (simulated example) › Recheck record 7 (simulated example)
- `E381` zh `#/fixture`：复检记录 6（模拟示例） ‹ 复检记录 7（模拟示例） › 复检记录 8（模拟示例）；en `#/fixture`：Recheck record 6 (simulated example) ‹ Recheck record 7 (simulated example) › Recheck record 8 (simulated example)
- `E382` zh `#/fixture`：复检记录 7（模拟示例） ‹ 复检记录 8（模拟示例） › 复检记录 10（模拟示例）；en `#/fixture`：Recheck record 7 (simulated example) ‹ Recheck record 8 (simulated example) › Recheck record 10 (simulated example)
- `E383` zh `#/fixture`：第二步 ‹ 模型未改，但交接判断发生变化 › 同一份记录复检之后：两侧模型都没有重新发布，却有判断变了。变的是哪一项，为什么？；en `#/fixture`：Step 2 ‹ The models did not change, but a handover conclusion did › The same record after a recheck: neither model was re-issued, yet a co
- `E384` zh `#/fixture`：复检记录 8（模拟示例） ‹ 复检记录 10（模拟示例）；en `#/fixture`：Recheck record 8 (simulated example) ‹ Recheck record 10 (simulated example)

#### TAG_WORDS（14 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E386 | `note` | The IFC Tag is a marker written into the IFC at export; what Revit writes is usually the element's ElementId. To check: in Revit, use "Select by ID" with this ID and see… | IFC Tag 是导出时写进 IFC 的标记；Revit 导出的通常是构件的 ElementId。核对：在 Revit 里用“按 ID 选择”选中这个 ID，看选中对象的名称和类别是否与本页相同；相同再按它处理，不同就… | 10/8 后改句，需重核 | zh 6｜en 6｜本地结果页 |
| E387 | `byIdNotStorey` | Find the object in Revit by its ID, not by storey: the storey on this page is the IFC file's spatial assignment, which may not match the levels in a Revit schedule. | 在 Revit 里按 ID 找对象，不要按楼层找：本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上。 | 10/8 已核 | zh 6｜en 6｜本地结果页 |
| E388 | `storeyFromIfc` | The storey on this page is the IFC file's spatial assignment, which may not match the levels in a Revit schedule; do not look for the object by storey alone. | 本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上，不要只按楼层去找。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E389 | `sources.model-file` | The model file has no Tag for this element. | 模型文件里这个构件没有写 Tag。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E390 | `sources.model-file-not-located` | The model file this check read was not found, so the Tag cannot be read. | 没有找到这次检查读的那个模型文件，所以读不到 Tag。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E391 | `sources.model-file-differs` | The model file in the workspace is no longer the version this check read, so the Tag is not read. | 工作区里的模型文件已经不是这次检查读的那个版本，所以不读取 Tag。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E392 | `sourceNotCarried` | The returned data does not say where this model's Tags are read from, so there is no Tag. | 返回数据没有说明这个模型的 Tag 从哪里读，所以没有 Tag。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E393 | `modelLevel` | This result is about the whole model; there is no single element to find. | 这条结果针对整个模型，没有具体构件可找。 | 10/8 已核 | zh 2｜en 2｜本地结果页 |
| E394 | `useGlobalId` | To find it in the IFC, use the GlobalId. | 在 IFC 里定位用 GlobalId。 | 10/8 已核 | zh 6｜en 6｜本地结果页 |
| E395 | `short.model-file` | No Tag in the file | 文件里没有 Tag | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E396 | `short.model-file-not-located` | Model file not found | 未找到模型文件 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E397 | `short.model-file-differs` | Model file version differs | 模型文件版本不同 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E398 | `short.notCarried` | Source not stated | 来源未说明 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E399 | `short.modelLevel` | Whole model | 整个模型 | 10/8 已核 | zh 8｜en 8｜本地结果页；复用 G037 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E386` zh `#/local/c653c7e0bb676a4a/finding/eed53402-33a9-5b7a-9d4c-a912e10c4566`：23uPJWDfXEcwHH3kdFgV9c复制 ‹ IFC Tag 是导出时写进 IFC 的标记；Revit 导出的通常是构件的 ElementId。核对：在 Revit 里用“按 ID 选择”选中这个 ID，看选中对象的名称和类别是否与本页相同；相同再按它处理，不同就不 › 在 Revit 里按 ID 找对象，不要按楼层找：本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上。；en `#/local/c653c7e0bb676a4a/finding/eed53402-33a9-5b7a-9d4c-a912e10c4566`：23uPJWDfXEcwHH3kdFgV9cCopy ‹ The IFC Tag is a marker written into the IFC at export; what Revit writes is usually the element's ElementId.  › Find the object in Revit by its ID, not by storey: the storey on this

#### VERDICT_GROUPS（1 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E402 | `changed.notes.none` | Neither model was re-issued, yet these conclusions changed: the change does not come from a model edit. Each item's old evidence says what changed. | 两侧模型都没有重新发布，这些项的判断却变了：变化不来自模型改动。每一项的旧证据写明变了的是什么。 | 10/8 已核 | zh 4｜en 4｜示例主线 |

#### VERDICT_SCOPE（1 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E411 | `(整表)` | Each conclusion is about one piece of the receiving side's work, this item within this assessment's scope, and the listed model versions; it is not an overall verdict on… | 每个判断只针对接收方的一项工作、本次评估范围内的这一项，以及所列的模型版本；它不是“模型好不好”的总评，也不是“某项检查通过了”。 | 10/8 已核 | zh 181｜en 181｜示例主线、其他示例 |

#### WORKSPACE（73 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E416 | `back` | ← Back to the home page | ← 返回首页 | 10/8 已核 | zh 42｜en 42｜本地结果页、本地检查（选文件至运行） |
| E420 | `resultTitle` | Results of a real check | 一次真实检查的结果 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E421 | `noJudgement` | These are the results of a check, not a handover judgement: the page says only whether each element passed, failed or was not applicable under each requirement, and conc… | 这是一次检查的结果，不是交接判断：页面只说每个构件在每条要求下通过、不通过还是不适用，不对任何工作能否开始下结论。 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E422 | `summary.one` | This result: {count} check result | 本次结果：共 {count} 条检查结果 | 10/8 已核 | zh 16｜en 16｜本地结果页；复用 G039 |
| E423 | `summary.other` | This result: {count} check results | 本次结果：共 {count} 条检查结果 | 10/8 已核 | zh 16｜en 13｜本地结果页；复用 G039 |
| E424 | `unit` | The unit is one result: one element under one requirement; where a model has no element the requirement applies to, it is one result for the whole model. | 单位是条：一条是一个构件在一条要求下的结果；模型里没有这条要求适用的构件时，是整个模型的一条。 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E425 | `compareLink` | See the comparison with the earlier run | 看与前一次运行的对比 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E426 | `compareTeaser` | The server was also started with an earlier run. Before and after: | 服务器启动时还指定了前一次运行。两次结果的前后对比： | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E427 | `checkedHeading` | What was checked | 检查了什么 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E428 | `ruleTitle` | Requirement | 要求 | 10/8 已核 | zh 40｜en 40｜示例主线、本地检查（选文件至运行）、其他示例；复用 G013 |
| E429 | `rulePredicate` | What this rule asks | 这条规则要求 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E430 | `ruleExpected` | The rule's own words | 规则的原话（英文） | 10/8 已核 | zh 74｜en 74｜示例主线、本地结果页、其他示例；复用 G014 |
| E431 | `ruleOrigin` | Source (the returned data's citation, as written) | 出处（返回数据的引文，英文原文） | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E432 | `ruleLabels` | Labels in the returned data | 返回数据的标签 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E433 | `productValidation` | The label in the returned data (ProductValidation) says: this is a product validation rule. | 返回数据的标签（ProductValidation）标明：这是一条产品验证规则。 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E434 | `noRuleNotes` | This interface has written no notes for this rule; the rule's own words in the returned data are what counts. | 本界面没有为这条规则写中文说明；规则以返回数据里的英文原话为准。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E435 | `noRequirement` | The returned data has no description of the requirement this result belongs to. | 返回数据没有这条结果所属要求的说明。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E436 | `listHeading` | Results, one by one | 逐条结果 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E437 | `filterLabel` | Find by IFC Tag, name or GlobalId | 按 IFC Tag、名称或 GlobalId 查找 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E438 | `filterAll` | All | 全部 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E439 | `filterNone` | No result matches the filter. | 没有符合筛选条件的结果。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E440 | `filterShown` | Showing {shown} of {count} | 显示 {shown} 条，共 {count} 条 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E441 | `columns.status` | Result | 结果 | 10/8 已核 | zh 16｜en 16｜本地结果页；复用 G040 |
| E442 | `columns.tag` | IFC Tag | IFC Tag | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E443 | `columns.name` | Name | 名称 | 10/8 已核 | zh 156｜en 16｜本地结果页、次要明细页；复用 G041 |
| E444 | `columns.class` | Class | 类别 | 10/8 已核 | zh 173｜en 173｜示例主线、本地结果页、其他示例；复用 G042 |
| E445 | `columns.storey` | Storey (IFC) | 楼层（IFC） | 10/8 已核 | zh 16｜en 16｜本地结果页；复用 G043 |
| E446 | `columns.model` | Model | 模型 | 10/8 已核 | zh 336｜en 193｜示例主线、本地结果页、本地检查（选文件至运行）、其他示例、次要明细页；复用 G044、G028 |
| E447 | `pickOne` | Choose a result from the list to see its details here. | 从结果列表里选一条，在这里看它的详情。 | 10/8 已核 | zh 8｜en 8｜本地结果页 |
| E448 | `detailKicker` | One result of a real check | 一条真实检查结果 | 10/8 已核 | zh 8｜en 8｜本地结果页 |
| E449 | `wholeModel` | Whole model | 整个模型 | 10/8 已核 | zh 8｜en 8｜本地结果页；复用 G037 |
| E450 | `resultHeading` | Result | 结果 | 10/8 已核 | zh 16｜en 16｜本地结果页；复用 G040 |
| E451 | `findHeading` | Which object to find in Revit | 回到 Revit 找哪个对象 | 10/8 已核 | zh 8｜en 8｜本地结果页 |
| E452 | `actionHeading` | What to change | 要改什么 | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E453 | `actionWhat` | Change it to | 改成什么 | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E454 | `actionReads` | Where the checker reads | 检查器读哪里 | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E455 | `actionRevise` | Where to change it in Revit | 在 Revit 里改哪里 | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E456 | `actionUndecided` | Not decided yet | 还没有决定的 | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E457 | `requirementHeading` | The requirement, and what this check observed | 具体要求与这次检查的观察 | 10/8 已核 | zh 8｜en 8｜本地结果页 |
| E458 | `reason` | Reason (as the check result gives it) | 原因（检查结果的原文） | 10/8 已核 | zh 8｜en 8｜本地结果页 |
| E459 | `actual` | Observed value | 观察值一栏 | 10/8 已核 | zh 8｜en 8｜本地结果页 |
| E460 | `actualEmpty` | Empty in the check result. | 检查结果中为空。 | 10/8 已核 | zh 8｜en 8｜本地结果页 |
| E461 | `actualHidden` | The check result carries an observed value; this page does not show it. | 检查结果带有观察值；本页不显示取值。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E462 | `recheckHeading` | What to look at in a recheck | 复检时看什么 | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E463 | `passHeading` | What this pass proves | 这条通过证明了什么 | 10/8 已核 | zh 1｜en 1｜本地结果页 |
| E464 | `passProves` | It proves: | 它证明： | 10/8 已核 | zh 1｜en 1｜本地结果页 |
| E465 | `passDoesNotProve` | It does not prove: | 它不证明： | 10/8 已核 | zh 1｜en 1｜本地结果页 |
| E466 | `passNoValue` | A passing check result does not carry the value it read: it records only "Requirement satisfied." | 通过的检查结果不带它读到的值：只记录了“要求已满足”。 | 10/8 已核 | zh 1｜en 1｜本地结果页 |
| E467 | `passUnwritten` | A pass says only that this requirement was judged met; how far that goes, this interface has written no notes for this rule — see the rule's own words. | 通过只说明这条要求被判为满足；它能证明到哪里，本界面没有为这条规则写说明，请看规则原话。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E468 | `notApplicable` | Not applicable: this model has no element the requirement applies to. Not applicable is not a pass. | 不适用：这个模型里没有这条要求适用的构件。不适用不是通过。 | 10/8 已核 | zh 2｜en 2｜本地结果页 |
| E469 | `failNotDefect` | Not meeting this product validation rule is not a delivery defect of the original project. Where this rule comes from is what the returned data's label (ProductValidatio… | 不满足这条产品验证规则，不等于原项目的交付缺陷。这条规则的来源以返回数据的标签（ProductValidation）和出处原文为准。 | 10/8 已核 | zh 5｜en 5｜本地结果页 |
| E470 | `noFinding` | This check has no such result. | 这次检查里没有这一条结果。 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| E471 | `identityHeading` | Tracing: this check's run identifier, rule set version and model files | 追溯信息：这次检查的运行号、规则集版本与模型文件 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E472 | `findingTrace` | Tracing: this result's internal keys | 追溯信息：这条结果的内部键 | 10/8 已核 | zh 8｜en 8｜本地结果页 |
| E473 | `identity.run` | Check run identifier | 检查运行号 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E474 | `identity.ruleset` | Rule set | 规则集 | 10/8 已核 | zh 38｜en 26｜本地结果页、本地检查（选文件至运行）、次要明细页 |
| E475 | `identity.asOf` | Logical date (given by the run configuration, not when it ran) | 逻辑日期（运行配置给定，不是运行的时间） | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E476 | `identity.checkers` | Checkers | 检查程序 | 10/8 已核 | zh 36｜en 16｜示例主线、本地结果页、其他示例；复用 G002 |
| E477 | `identity.models` | Models | 模型 | 10/8 已核 | zh 336｜en 177｜示例主线、本地结果页、本地检查（选文件至运行）、其他示例、次要明细页；复用 G027、G028 |
| E478 | `identity.modelId` | Model | 模型 | 10/8 已核 | zh 336｜en 193｜示例主线、本地结果页、本地检查（选文件至运行）、其他示例、次要明细页；复用 G044、G028 |
| E479 | `identity.declaredDiscipline` | Discipline declared in the project manifest | 项目清单声明的专业 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E480 | `identity.filename` | File | 文件 | 10/8 已核 | zh 32｜en 32｜本地结果页、本地检查（选文件至运行） |
| E481 | `identity.digest` | File content digest (SHA-256) | 文件内容摘要（SHA-256） | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E482 | `identity.tagSource` | Where the IFC Tag comes from | IFC Tag 的来源 | 10/8 已核 | zh 16｜en 16｜本地结果页 |
| E483 | `identity.elementKey` | Internal key for tracing | 追溯用内部键 | 10/8 已核 | zh 165｜en 165｜示例主线、本地结果页、其他示例 |
| E484 | `identity.findingKey` | Check result key | 检查结果键 | 10/8 已核 | zh 8｜en 8｜本地结果页 |
| E485 | `identity.requirementKey` | Requirement key | 要求键 | 10/8 已核 | zh 8｜en 8｜本地结果页 |
| E486 | `element.name` | Name | 名称 | 10/8 已核 | zh 156｜en 16｜本地结果页、次要明细页；复用 G041 |
| E487 | `element.class` | Class | 类别 | 10/8 已核 | zh 173｜en 173｜示例主线、本地结果页、其他示例；复用 G042 |
| E488 | `element.storey` | Storey (IFC) | 楼层（IFC） | 10/8 已核 | zh 16｜en 16｜本地结果页；复用 G043 |
| E489 | `element.model` | Model | 所属模型 | 10/8 已核 | zh 165｜en 193｜示例主线、本地结果页、其他示例；复用 G044 |
| E490 | `element.file` | Model file | 模型文件 | 10/8 已核 | zh 8｜en 8｜本地结果页 |
| E491 | `element.globalId` | GlobalId | GlobalId | 10/8 已核 | zh 310｜en 163｜示例主线、本地结果页、其他示例、次要明细页 |

#### WORKSPACE_COMPARE（14 条，待核 14）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E503 | `unchanged.one` | Results that are the same in both runs: {count} | 两次结果相同的：{count} 条 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发）；复用 G046 |
| E504 | `unchanged.other` | Results that are the same in both runs: {count} | 两次结果相同的：{count} 条 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发）；复用 G046 |
| E508 | `rows.one` | {count} row | {count} 条 | B 层，10/8 未核 | zh 0｜en 12｜本地结果页；复用 G048 |
| E509 | `rows.other` | {count} rows | {count} 条 | B 层，10/8 未核 | zh 0｜en 9｜本地结果页；复用 G048 |
| E519 | `inPrior.true` | The element is in the earlier run's list of elements | 构件在前一次的构件清单里 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发） |
| E520 | `inPrior.false` | The element is not in the earlier run's list of elements | 构件不在前一次的构件清单里 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发） |
| E521 | `inPrior.null` | A result for the whole model, not for an element | 整个模型的一条结果，不针对构件 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发）；复用 G051 |
| E531 | `detailHeading` | Compared with the earlier run | 和前一次运行比 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发） |
| E532 | `detailPrior` | Earlier result | 前一次的结果 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发） |
| E533 | `detailCurrent` | This result | 本次的结果 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发） |
| E534 | `detailNewly` | The earlier run has no such result: it is newly appearing. | 前一次运行没有这一条结果：它是新出现的。 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发） |
| E535 | `detailNone` | The returned data's comparison does not include this result. | 返回数据的对比里没有这一条。 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发） |
| E536 | `priorReason` | Earlier reason (as written) | 前一次的原因（原文） | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发） |
| E537 | `currentReason` | This reason (as written) | 本次的原因（原文） | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发） |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E508` en `flow:check-both:result`：
- `E509` en `flow:check-both:result`：

#### WORKSPACE_HOME（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E542 | `action` | See this check | 查看这次检查 | 10/15 批，未核 | zh 0｜en 1｜首页 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E542` en `#/`：The repository comes with a sample project. The check attempt on it di ‹ See this check attempt › What you cannot do yet

#### REASON_GLOSSES（4 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E565 | `The predefined type "NOTDEFINED" does not meet the required type` |  | 预定义类型“NOTDEFINED”不属于要求的取值 | 10/8 已核 | zh 0｜en 0｜（本次渲染未触发） |
| Z01 | `The required property set does not exist` |  | 所要求的属性集不存在（要让导出写出这个属性集以及其中所要求的属性，不是给已有属性填值） | 10/8 后改句，需重核 | zh 36｜en 0｜示例主线、其他示例 |
| Z02 | `Requirement satisfied.` |  | 要求已满足 | D6 未列，是否已核待确认 | zh 31｜en 0｜示例主线、本地结果页、其他示例 |
| Z03 | `No applicable elements exist in this model.` |  | 这个模型里没有这条要求适用的构件 | D6 未列，是否已核待确认 | zh 2｜en 0｜本地结果页 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `Z01` zh `#/fixture/member-evidence/item/2/2/0`：原因 ‹ 所要求的属性集不存在（要让导出写出这个属性集以及其中所要求的属性，不是给已有属性填值） › The required property set does not exist

#### FIRST（11 条，待核 11）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E566 | `cardDetails` | Element details and what to do | 构件信息和要做什么 | 10/15 批，未核 | zh 4｜en 4｜示例主线、其他示例 |
| E567 | `cardElements` | Element details | 构件信息 | 10/15 批，未核 | zh 0｜en 4｜示例主线、其他示例 |
| E568 | `openCard` | See this item | 查看这一项 | 10/15 批，未核 | zh 4｜en 37｜示例主线、其他示例 |
| E572 | `notRevised` | (Chinese only: that page has not been translated or revised yet, and still uses internal terms) | （该页尚未改版，仍是内部用语） | 10/15 批，未核 | zh 167｜en 167｜示例主线、其他示例 |
| E584 | `team` | Handling team | 处理团队 | B 层，10/8 未核 | zh 103｜en 181｜示例主线、其他示例；复用 G052 |
| E585 | `verdictLine` | : the work concerned is | ：对应的那项工作 | B 层，10/8 未核 | zh 0｜en 4｜示例主线、其他示例 |
| E586 | `quietLine` | : {summary} (listed further down this page) | ：{summary}（列在本页下方） | B 层，10/8 未核 | zh 4｜en 4｜示例主线、其他示例 |
| E587 | `problem` | Problem | 问题 | B 层，10/8 未核 | zh 107｜en 107｜示例主线、其他示例 |
| E588 | `columns.work` | Which work: conclusion | 哪项工作：结论 | B 层，10/8 未核 | zh 4｜en 4｜示例主线、其他示例 |
| E589 | `openHeading.one` | {label}, by handling team ({count} item) | {label}，按处理团队（{count} 个事项） | B 层，10/8 未核 | zh 4｜en 0｜示例主线、其他示例；复用 G053 |
| E590 | `openHeading.other` | {label}, by handling team ({count} items) | {label}，按处理团队（{count} 个事项） | B 层，10/8 未核 | zh 4｜en 4｜示例主线、其他示例；复用 G053 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E566` zh `#/fixture/member-evidence`：问题：不是已知的模型缺陷：还没有协调评审判定它是否穿过接收方的构件 ‹ 构件信息和要做什么 › 风口 IfcAirTerminal · 00 groundfloor · 模型 hvac；en `#/fixture/member-evidence`：Problem: Not a known model defect: no coordination review has determin ‹ Element details and what to do › IfcAirTerminal (IFC class) · 00 groundfloor · model hvac
- `E567` en `#/fixture/member-evidence`：Problem: Not a known model defect: no coordination review has determin ‹ Element details and what to do › IfcAirTerminal (IFC class) · 00 groundfloor · model hvac
- `E568` zh `#/fixture/member-evidence`：这不是已知的模型缺陷。还没有协调评审判定它是否穿过接收方的构件；需要开一次评审，记录“不穿过”或写明穿过哪些构件 ‹ 查看这一项 › 一个构件；en `#/fixture/member-evidence`：This is not a known model defect. No coordination review has yet deter ‹ See this item › One element
- `E572` zh `#/fixture/member-evidence`：追溯信息：记录标识、规则版本、记录原码 ‹ 这份记录的请求范围、版本与来源（该页尚未改版，仍是内部用语） › assessment digest；en `#/fixture/member-evidence`：Tracing: record identity, rule version, record codes ‹ This record's requested scope, versions and sources (Chinese only: that page has not been translated or revise › assessment digest
- `E584` zh `#/fixture/member-evidence/item/0/2/0`：随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 这份记录的结论引用了：真实检查输出、模拟的人工判定，逐条标在结 ‹ 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的检查结果或模拟的人工判定，具体是哪一种，看每个结论旁的“依据”一行（按逐条引用标 › ← 返回事项列表（回到这一项的位置）；en `#/fixture/member-evidence`：Items to deal with, by handling team (8 items) ‹ Handling team coordination-team Example handling team: 6 items › Default handling role (the rule's default, not an assignment): model-c
- `E585` en `#/fixture/member-evidence`：This result: 13 in all; to deal with: 8 ‹ 4 items: the work concerned is Blocked › 4 items: the work concerned is Unknown
- `E586` zh `#/fixture/member-evidence`：4 个事项：对应的那项工作 无法判断 ‹ 5 个事项：记录没有给出后续处理动作（列在本页下方） › 一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。同一个构件可以出现在几个事项里，所以事项数不是缺陷数。这份记录共；en `#/fixture/member-evidence`：4 items: the work concerned is Unknown ‹ 5 items: the record gives no follow-up action (listed further down this page) › An item is the conclusion for one element (or a pair of elements asses
- `E587` zh `#/fixture/member-evidence`：默认处理角色（规则给出的默认，不是指派）：model-coordination 处理团队是记录里的安排，不代表已经派发。 ‹ 问题 › 哪项工作：结论；en `#/fixture/member-evidence`：Default handling role (the rule's default, not an assignment): model-c ‹ Problem › Which work: conclusion
- `E588` zh `#/fixture/member-evidence`：问题 ‹ 哪项工作：结论 › 事项数；en `#/fixture/member-evidence`：Problem ‹ Which work: conclusion › Items
- `E589` zh `#/fixture/member-evidence`：一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。同一个构件可以出现在几个事项里，所以事项数不是缺陷数。这份记录共 ‹ 需要处理的事项，按处理团队（8 个事项） › 处理团队 coordination-team 示例处理团队：6 个事项
- `E590` zh `#/fixture/member-evidence`：一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。同一个构件可以出现在几个事项里，所以事项数不是缺陷数。这份记录共 ‹ 需要处理的事项，按处理团队（8 个事项） › 处理团队 coordination-team 示例处理团队：6 个事项；en `#/fixture/member-evidence`：An item is the conclusion for one element (or a pair of elements asses ‹ Items to deal with, by handling team (8 items) › Handling team coordination-team Example handling team: 6 items

#### ACTION（5 条，待核 5）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E573 | `what` | What to do | 要做什么 | B 层，10/8 未核 | zh 125｜en 125｜示例主线、其他示例 |
| E574 | `team` | Handling team | 处理团队 | B 层，10/8 未核 | zh 103｜en 181｜示例主线、其他示例；复用 G052 |
| E575 | `consequence` | What it means for this work | 对这项工作的后果 | B 层，10/8 未核 | zh 103｜en 103｜示例主线、其他示例 |
| E576 | `recheck` | What a recheck must show | 完成后拿什么复检 | B 层，10/8 未核 | zh 103｜en 103｜示例主线、其他示例 |
| E577 | `original` | Source wording (as the record carries it): for tracing, not an instruction | 来源原文（英文，记录所带）：供追溯，不是操作指令 | B 层，10/8 未核 | zh 103｜en 103｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E573` zh `#/fixture/member-evidence`：问题：不是已知的模型缺陷：还没有协调评审判定它是否穿过接收方的构件 ‹ 构件信息和要做什么 › 风口 IfcAirTerminal · 00 groundfloor · 模型 hvac；en `#/fixture/member-evidence`：IfcAirTerminal (IFC class) · 00 groundfloor · model hvac ‹ What to do › This is not a known model defect. No coordination review has yet deter
- `E574` zh `#/fixture/member-evidence/item/0/2/0`：随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 这份记录的结论引用了：真实检查输出、模拟的人工判定，逐条标在结 ‹ 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的检查结果或模拟的人工判定，具体是哪一种，看每个结论旁的“依据”一行（按逐条引用标 › ← 返回事项列表（回到这一项的位置）；en `#/fixture/member-evidence`：Items to deal with, by handling team (8 items) ‹ Handling team coordination-team Example handling team: 6 items › Default handling role (the rule's default, not an assignment): model-c
- `E575` zh `#/fixture/member-evidence/item/0/2/0`：model-coordination ‹ 对这项工作的后果 › 这项工作暂缓，等有结论再定；en `#/fixture/member-evidence/item/0/2/0`：model-coordination ‹ What it means for this work › This work is held until decided
- `E576` zh `#/fixture/member-evidence/item/0/2/0`：要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。 ‹ 二、要做什么、由谁处理、完成后拿什么复检 › 要做什么；en `#/fixture/member-evidence/item/0/2/0`：This work is held until decided ‹ What a recheck must show › A recorded review determination exists for the model versions listed
- `E577` zh `#/fixture/member-evidence/item/0/2/0`：针对所列模型版本，有一份评审判定记录 ‹ 来源原文（英文，记录所带）：供追溯，不是操作指令 › next_action；en `#/fixture/member-evidence/item/0/2/0`：A recorded review determination exists for the model versions listed ‹ Source wording (as the record carries it): for tracing, not an instruction › next_action

#### ITEM（6 条，待核 6）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E578 | `noFollowUp` | The record gives no follow-up action, handling team or default handling role for this item. | 记录没有为这一项给出后续处理动作、处理团队或默认处理角色。 | B 层，10/8 未核 | zh 40｜en 40｜示例主线、其他示例 |
| E579 | `needs` | What this work needs | 这项工作需要什么 | B 层，10/8 未核 | zh 26｜en 26｜示例主线、其他示例 |
| E580 | `leaf` | Final outcome | 终点 outcome | B 层，10/8 未核 | zh 26｜en 26｜示例主线、其他示例 |
| E581 | `context` | Background citations: not the basis of this conclusion, shown word for word. | 背景引用：不是这个结论的依据，逐字显示。 | B 层，10/8 未核 | zh 6｜en 6｜示例主线、其他示例 |
| E582 | `actionHeading` | 2. What to do, who deals with it, what a recheck must show | 二、要做什么、由谁处理、完成后拿什么复检 | B 层，10/8 未核 | zh 147｜en 147｜示例主线、其他示例；复用 G031 |
| E583 | `followUpHeading` | 2. Follow-up | 二、后续 | B 层，10/8 未核 | zh 10｜en 10｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E578` zh `#/fixture/member-evidence/item/0/1/0`：二、后续 ‹ 记录没有为这一项给出后续处理动作、处理团队或默认处理角色。 › 三、是哪个构件；en `#/fixture/member-evidence/item/0/1/0`：2. Follow-up ‹ The record gives no follow-up action, handling team or default handling role for this item. › 3. Which element
- `E579` zh `#/fixture/member-evidence/item/0/1/0`：已有协调评审判定：它不穿过接收方模型里的任何构件。不穿过就不需要开洞，所以开洞情况没有被评估——这不是“开洞没问题” ‹ 这项工作需要什么 › 要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。；en `#/fixture/member-evidence/item/0/1/0`：A coordination-review determination says it passes through no element  ‹ What this work needs › Needs to know where MEP penetrates architectural fabric, so openings c
- `E580` zh `#/fixture/member-evidence/item/0/1/0`：记录未携带 ‹ 终点 outcome › penetration-determination/no-penetration；en `#/fixture/member-evidence/item/0/1/0`：Not carried in the record ‹ Final outcome › penetration-determination/no-penetration
- `E581` zh `#/fixture/member-evidence/item/1/2/0`：fixture-determination/alignment/confirmed复制 模拟的人工判定 ‹ 背景引用：不是这个结论的依据，逐字显示。 › insufficient_evidence epc-delivery 2.2 acb11f11-bf18-5516-a6f2-21e451a；en `#/fixture/member-evidence/item/1/2/0`：fixture-determination/alignment/confirmedCopy Simulated human determin ‹ Background citations: not the basis of this conclusion, shown word for word. › insufficient_evidence epc-delivery 2.2 acb11f11-bf18-5516-a6f2-21e451a
- `E582` zh `#/fixture/member-evidence/item/0/2/0`：要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。 ‹ 二、要做什么、由谁处理、完成后拿什么复检 › 要做什么；en `#/fixture/member-evidence/item/0/2/0`：Needs to know where MEP penetrates architectural fabric, so openings c ‹ 2. What to do, who deals with it, what a recheck must show › What to do
- `E583` zh `#/fixture/member-evidence/item/0/1/0`：要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。 ‹ 二、后续 › 记录没有为这一项给出后续处理动作、处理团队或默认处理角色。；en `#/fixture/member-evidence/item/0/1/0`：Needs to know where MEP penetrates architectural fabric, so openings c ‹ 2. Follow-up › The record gives no follow-up action, handling team or default handlin

#### EVIDENCE（2 条，待核 2）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E593 | `reissueColumns.role` | Role (from this request's handover) | 角色（取自本次请求的交接） | B 层，10/8 未核 | zh 20｜en 20｜示例主线、其他示例 |
| E596 | `notReissued` | Unchanged (original version) | 没有变（原版本） | B 层，10/8 未核 | zh 18｜en 18｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E593` zh `#/fixture/recheck-requirement-relaxed`：交接的哪一侧 ‹ 角色（取自本次请求的交接） › 模型；en `#/fixture/recheck-requirement-relaxed`：Side of the handover ‹ Role (from this request's handover) › Model
- `E596` zh `#/fixture/recheck-requirement-relaxed`：hvac ‹ 没有变（原版本） › 接收方；en `#/fixture/recheck-requirement-relaxed`：hvac ‹ Unchanged (original version) › Receiving side

#### RECHECK_MODEL（3 条，待核 3）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E597 | `onlyRekeyed` | {rekeyed}: neither the evidence content nor the comparison basis changed. | {rekeyed}：证据内容和比较依据都没有变。 | B 层，10/8 未核 | zh 30｜en 30｜示例主线、其他示例 |
| E598 | `producing` | Handing-over side | 交出方 | B 层，10/8 未核 | zh 20｜en 20｜示例主线、其他示例 |
| E599 | `consuming` | Receiving side | 接收方 | B 层，10/8 未核 | zh 20｜en 20｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E597` zh `#/fixture/recheck-requirement-relaxed/recheck/5/0`：对应的检查结果只有一条，模型版本、检查结果内容、检查要求、检查程序逐项相同。 ‹ 只是引用换了键：证据内容和比较依据都没有变。 › 追溯信息（记录原码与内容指纹）；en `#/fixture/recheck-requirement-relaxed/recheck/5/0`：There is exactly one corresponding check result; model version, check  ‹ Only the citation's key changed: neither the evidence content nor the comparison basis changed. › Tracing (record codes and content fingerprints)
- `E598` zh `#/fixture/recheck-requirement-relaxed`：要做什么 ‹ 在接收方模型里、被穿过的构件上建出洞口或竖井，不要做成交出方模型里的空洞。穿过几个构件就要几个洞口 › 查看这一项：具体对象、要做什么、由谁处理、拿什么复检；en `#/fixture/recheck-requirement-relaxed`：Re-issued? ‹ Handing-over side › MEP
- `E599` zh `#/fixture/recheck-requirement-relaxed`：要做什么 ‹ 这不是已知的模型缺陷。还没有协调评审判定它是否穿过接收方的构件；需要开一次评审，记录“不穿过”或写明穿过哪些构件 › 查看这一项：具体对象、要做什么、由谁处理、拿什么复检；en `#/fixture/recheck-requirement-relaxed`：Unchanged (original version) ‹ Receiving side › Architecture

#### WORK（2 条，待核 2）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E600 | `unchanged` | {work}: {before} ({note}) | {work}：{before} （{note}） | B 层，10/8 未核 | zh 112｜en 121｜示例目录、示例主线、本地结果页、其他示例 |
| E601 | `changed` | {work}: before the recheck {before} → now {now} | {work}：复检前 {before} → 现在 {now} | B 层，10/8 未核 | zh 35｜en 35｜示例主线、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E600` zh `#/fixture/recheck-requirement-relaxed`：风口 IfcAirTerminal · 00 groundfloor · 模型 hvac ‹ 土建预留开洞：无法判断 （复检前后未变） › 同组事项共用的依据：还没有判定（真实的缺席） ×2；en `#/fixture`：These examples have no description yet, and the recheck records have o ‹ The same check record: conclusions on pairs of elements (simulated example) › Recheck record 1 (simulated example)
- `E601` zh `#/fixture/recheck-requirement-relaxed`：1 个事项的结论和复检前不同： ‹ building element ｜ 房间数据表与设备明细表：复检前 受阻 → 现在 可以开始 › 同组事项共用的依据，其中有模拟证据：模拟的检查结果 ×2；en `#/fixture/recheck-requirement-relaxed`：1 item's conclusion differs from before the recheck: ‹ building element \| Room data sheets and equipment schedules: before the recheck Blocked → now Ready › Basis shared by the items in this group, some of it simulated:Simulate

#### FAULT_WORDS（2 条，待核 2）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E603 | `note` | This is a problem of the program itself, not a judgement about any project or model; there are no check results to show. | 这是程序自身的问题，不是对任何项目或模型的判断；没有任何检查结果可以显示。 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发） |
| E604 | `fault` | Program fault: no check data was received | 程序故障：没有拿到检查数据 | B 层，10/8 未核 | zh 0｜en 0｜（本次渲染未触发） |

#### LOCAL_CHECK（8 条，待核 7）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| L002 | `home.title` | Check your own IFC model (product validation exercise) | 检查自己的 IFC 模型（产品验证练习） | 新增，未核 | zh 1｜en 1｜首页 |
| L003 | `home.body` | Choose an IFC4 file you exported and check the predefined type of its air terminals against one product validation rule. Before it runs, the page says what is checked, w… | 选择自己导出的 IFC4 文件，只用一条产品验证规则检查风口的预定义类型。运行前会说明检查什么、要求从哪里来、结果不能说明什么，以及本机会留下哪些记录。 | 新增，未核 | zh 1｜en 1｜首页 |
| L004 | `home.status` | Available now: simulated examples, and one limited product validation exercise on your own IFC4 files. A Revit file itself cannot be imported, and there is no overall co… | 当前提供模拟示例，以及对自己 IFC4 文件的一项有限产品验证练习；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。 | 新增，未核 | zh 1｜en 1｜首页 |
| L007 | `home.cannot[0]` | Import a Revit file itself (.rvt), or check your own model against rules other than the product validation exercise | 导入 Revit 文件本身（.rvt），或用产品验证练习以外的规则检查自己的模型 | 新增，未核 | zh 1｜en 1｜首页 |
| L008 | `home.cannot[1]` | Give an overall compliance, ready-to-build or "can be handed over" conclusion | 给出整体合规、可施工或“可以交付”的结论 | 新增，未核 | zh 1｜en 1｜首页；复用 G020 |
| L009 | `home.cannot[2]` | Write back to a model, upload to the cloud, or open an element in Revit | 写回模型、上传到云端，或在 Revit 里打开构件 | 同句已核 | zh 1｜en 1｜首页；复用 G021 |
| L050 | `disciplines.Architecture` | Architecture | 建筑（Architecture） | 新增，未核 | zh 24｜en 351｜示例主线、本地结果页、本地检查（选文件至运行）、其他示例、次要明细页 |
| L052 | `disciplines.MEP` | MEP | 机电（MEP） | 新增，未核 | zh 16｜en 36｜示例主线、本地检查（选文件至运行）、其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `L002` zh `#/`：选择模拟示例 ‹ 检查自己的 IFC 模型（产品验证练习） › 选择自己导出的 IFC4 文件，只用一条产品验证规则检查风口的预定义类型。运行前会说明检查什么、要求从哪里来、结果不能说明什么，以及本机会留；en `#/`：Choose a simulated example ‹ Check your own IFC model (product validation exercise) › Choose an IFC4 file you exported and check the predefined type of its
- `L003` zh `#/`：检查自己的 IFC 模型（产品验证练习） ‹ 选择自己导出的 IFC4 文件，只用一条产品验证规则检查风口的预定义类型。运行前会说明检查什么、要求从哪里来、结果不能说明什么，以及本机会留下哪些记录。 › 开始本地检查；en `#/`：Check your own IFC model (product validation exercise) ‹ Choose an IFC4 file you exported and check the predefined type of its air terminals against one product valida › Start a local check
- `L004` zh `#/`：帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。 ‹ 当前提供模拟示例，以及对自己 IFC4 文件的一项有限产品验证练习；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。 › 现在可以做什么；en `#/`：For a BIM manager: what a pre-handover check found; after a recheck, w ‹ Available now: simulated examples, and one limited product validation exercise on your own IFC4 files. A Revit › What you can do now
- `L007` zh `#/`：现在还不能做什么 ‹ 导入 Revit 文件本身（.rvt），或用产品验证练习以外的规则检查自己的模型 › 给出整体合规、可施工或“可以交付”的结论；en `#/`：What you cannot do yet ‹ Import a Revit file itself (.rvt), or check your own model against rules other than the product validation exe › Give an overall compliance, ready-to-build or "can be handed over" con
- `L008` zh `#/`：导入 Revit 文件本身（.rvt），或用产品验证练习以外的规则检查自己的模型 ‹ 给出整体合规、可施工或“可以交付”的结论 › 写回模型、上传到云端，或在 Revit 里打开构件；en `#/`：Import a Revit file itself (.rvt), or check your own model against rul ‹ Give an overall compliance, ready-to-build or "can be handed over" conclusion › Write back to a model, upload to the cloud, or open an element in Revi
- `L050` zh `flow:check-both:result`：product-validation 1.0 Product Validation Rules ‹ Building-Architecture.ifc（你声明的专业：建筑（Architecture）） › Building-Hvac.ifc（你声明的专业：暖通（HVAC））；en `#/fixture/member-evidence`：Project pcert-sample ‹ Handover: MEP → Architecture · Coordination › Back to the home page
- `L052` zh `flow:local:chosen`：暖通（HVAC） ‹ 机电（MEP） › 给排水（Plumbing）；en `#/fixture/recheck-requirement-relaxed`：Project pcert-sample ‹ Handover: MEP → Architecture · Coordination › Back to the home page

#### SOURCE_SUMMARY（8 条，待核 8）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| Q01 | `lead` | A simulated example shipped with the tool, not your model; project settings such as teams are for demonstration, not for formal project decisions. | 随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 | 新增，未核 | zh 481｜en 324｜示例目录、示例主线、其他示例、次要明细页 |
| Q02 | `cites` | This record's conclusions cite {kinds}, labelled citation by citation on the "Basis" line beside each conclusion. | 这份记录的结论引用了：{kinds}，逐条标在结论旁的“依据”一行。 | 新增，未核 | zh 480｜en 323｜示例主线、其他示例、次要明细页 |
| Q04 | `noRecord` | Whether the evidence a conclusion cites is real or simulated is labelled citation by citation on the "Basis" line beside it. | 结论引用的证据是真实的还是模拟的，逐条标在结论旁的“依据”一行。 | 新增，未核 | zh 1｜en 1｜示例目录 |
| Q05 | `kinds.finding-real` | real check output | 真实检查输出 | 新增，未核 | zh 468｜en 323｜示例主线、其他示例、次要明细页；复用 G003 |
| Q06 | `kinds.finding-fixture` | simulated check results | 模拟的检查结果 | 新增，未核 | zh 468｜en 232｜示例主线、其他示例、次要明细页；复用 G005 |
| Q07 | `kinds.determination-fixture` | simulated human determinations | 模拟的人工判定 | 新增，未核 | zh 468｜en 323｜示例主线、其他示例、次要明细页；复用 G006 |
| Q08 | `kinds.determination-unmarked` | determinations of unstated source | 来源未标注的判定 | 新增，未核 | zh 468｜en 0｜示例主线、其他示例、次要明细页；复用 G007 |
| Q11 | `more` | About the sources | 来源说明 | 新增，未核 | zh 481｜en 324｜示例目录、示例主线、其他示例、次要明细页 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `Q01` zh `#/fixture`：返回首页 ‹ 随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 结论引用的证据是真实的还是模拟的，逐条标在结论旁的“依据”一行。 来源说明 › 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的；en `#/fixture`：Back to the home page ‹ A simulated example shipped with the tool, not your model; project settings such as teams are for demonstratio › Simulated example: the project settings in the example, including the
- `Q02` zh `#/fixture/member-evidence`：返回首页 ‹ 随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 这份记录的结论引用了：真实检查输出、模拟的人工判定，逐条标在结论旁的“依据”一行。 来源说明 › 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的；en `#/fixture/member-evidence`：Back to the home page ‹ A simulated example shipped with the tool, not your model; project settings such as teams are for demonstratio › Simulated example: the project settings in the example, including the
- `Q04` zh `#/fixture`：返回首页 ‹ 随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 结论引用的证据是真实的还是模拟的，逐条标在结论旁的“依据”一行。 来源说明 › 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的；en `#/fixture`：Back to the home page ‹ A simulated example shipped with the tool, not your model; project settings such as teams are for demonstratio › Simulated example: the project settings in the example, including the
- `Q05` zh `#/fixture/member-evidence`：返回首页 ‹ 随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 这份记录的结论引用了：真实检查输出、模拟的人工判定，逐条标在结论旁的“依据”一行。 来源说明 › 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的；en `#/fixture/member-evidence`：Back to the home page ‹ A simulated example shipped with the tool, not your model; project settings such as teams are for demonstratio › Simulated example: the project settings in the example, including the
- `Q06` zh `#/fixture/member-evidence`：随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 这份记录的结论引用了：真实检查输出、模拟的人工判定，逐条标在结 ‹ 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的检查结果或模拟的人工判定，具体是哪一种，看每个结论旁的“依据”一行（按逐条引用标 › ← 返回示例目录；en `#/fixture/recheck-requirement-relaxed`：Back to the home page ‹ A simulated example shipped with the tool, not your model; project settings such as teams are for demonstratio › Simulated example: the project settings in the example, including the
- `Q07` zh `#/fixture/member-evidence`：返回首页 ‹ 随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 这份记录的结论引用了：真实检查输出、模拟的人工判定，逐条标在结论旁的“依据”一行。 来源说明 › 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的；en `#/fixture/member-evidence`：Back to the home page ‹ A simulated example shipped with the tool, not your model; project settings such as teams are for demonstratio › Simulated example: the project settings in the example, including the
- `Q08` zh `#/fixture/member-evidence`：模拟的人工判定 带模拟标记的判定引用：由示例提供，没有任何协调评审真的发生过。 ‹ 来源未标注的判定 未带模拟标记的判定引用：判定不是检查运行的输出，本界面也没有可核依据说明它来自哪里，因此不作真实或模拟的断言。 › 处理团队与默认处理角色
- `Q11` zh `#/fixture`：返回首页 ‹ 随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 结论引用的证据是真实的还是模拟的，逐条标在结论旁的“依据”一行。 来源说明 › 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的；en `#/fixture`：Back to the home page ‹ A simulated example shipped with the tool, not your model; project settings such as teams are for demonstratio › Simulated example: the project settings in the example, including the

#### DIRECTORY（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| Q12 | `exampleIntro` | Each example is one check record. | 每个示例是一份检查记录。 | 新增，未核 | zh 1｜en 1｜示例目录 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `Q12` zh `#/fixture`：选择一个模拟示例 ‹ 每个示例是一份检查记录。 › 第一步；en `#/fixture`：Choose a simulated example ‹ Each example is one check record. › Step 1

#### IFC_CLASS_NAMES（5 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| Z04 | `IfcAirTerminal` |  | 风口 | D6 未列，是否已核待确认 | zh 135｜en 0｜示例主线、本地结果页、本地检查（选文件至运行）、其他示例 |
| Z05 | `IfcChimney` |  | 烟囱 | D6 未列，是否已核待确认 | zh 73｜en 0｜示例主线、其他示例 |
| Z06 | `IfcDuctSegment` |  | 风管段 | D6 未列，是否已核待确认 | zh 56｜en 0｜示例主线、其他示例 |
| Z07 | `IfcRoof` |  | 屋顶 | D6 未列，是否已核待确认 | zh 37｜en 0｜示例主线、其他示例 |
| Z08 | `IfcSlab` |  | 楼板 | D6 未列，是否已核待确认 | zh 22｜en 0｜示例主线、其他示例 |

#### CITATION_GLOSSES（1 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| Z10 | `Product validation rule of this repository; not a project, owner, statutory or buildingSMART requirement. Values from IFC4 ADD2 TC1 IfcAirTerminalTypeEnum.` |  | 本仓库的产品验证规则；不是项目、业主、法规或 buildingSMART 的要求。取值来自 IFC4 ADD2 TC1 的 IfcAirTerminalTypeEnum。 | D6 未列，是否已核待确认 | zh 41｜en 0｜本地结果页、本地检查（选文件至运行） |

### T2 本地 IFC 与第二入口（90 条，待核 86）

#### MODE_LABELS（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E223 | `real` | Check attempt on the bundled project | 随附项目的检查尝试 | 10/15 批，未核 | zh 2｜en 2｜第二入口 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E223` zh `#/real`：English ‹ 随附项目的检查尝试 › 返回首页；en `#/real`：English ‹ Check attempt on the bundled project › Back to the home page

#### REFUSAL_PAGE（10 条，待核 8）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E312 | `title` | This check attempt did not start an assessment | 这次检查尝试没有开始评估 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |
| E313 | `lede` | The system refused this request before the assessment started, and gave its reason. This is an answer about the request's conditions: not a program fault, and not a chec… | 系统在评估开始前拒绝了这次请求，并给出了原因。这是对请求条件的答复：不是程序故障，也不是检查结果。 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |
| E314 | `whyHeading` | Why it did not start | 为什么没有开始 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |
| E315 | `needHeading` | What is needed for the check to start | 要让检查能够开始，需要什么 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |
| E316 | `onlyOne` | Only this one reason was returned; there is no diagnosis of any other stage. | 本次只返回这一个原因，没有其他环节的诊断。 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |
| E317 | `noConclusion` | No conclusion on any item, no zero-problem count and no completion ratio: a refusal is not "Unknown", and not a check without problems. | 没有任何事项的结论、零问题统计或完成百分比；被拒绝不是“无法判断”，也不是一次没有问题的检查。 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |
| E318 | `original` | What the system returned (as written) and the refusal code | 系统返回的原文（英文）与拒绝码 | 同句已核 | zh 1｜en 1｜第二入口；复用 G035 |
| E319 | `attempt` | Check attempt | 检查尝试 | 10/15 批，未核 | zh 1｜en 2｜第二入口 |
| E320 | `code` | Refusal code | 拒绝码 | 同句已核 | zh 1｜en 1｜第二入口；复用 G036 |
| E321 | `contextMissing` | The context of the request that was submitted has not been returned with the refusal yet. | 所提交的请求上下文尚未随拒绝返回。 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E312` zh `#/real/real-refusal`：返回首页 ‹ 这次检查尝试没有开始评估 › 系统在评估开始前拒绝了这次请求，并给出了原因。这是对请求条件的答复：不是程序故障，也不是检查结果。；en `#/real/real-refusal`：Back to the home page ‹ This check attempt did not start an assessment › The system refused this request before the assessment started, and gav
- `E313` zh `#/real/real-refusal`：这次检查尝试没有开始评估 ‹ 系统在评估开始前拒绝了这次请求，并给出了原因。这是对请求条件的答复：不是程序故障，也不是检查结果。 › 为什么没有开始；en `#/real/real-refusal`：This check attempt did not start an assessment ‹ The system refused this request before the assessment started, and gave its reason. This is an answer about th › Why it did not start
- `E314` zh `#/real/real-refusal`：系统在评估开始前拒绝了这次请求，并给出了原因。这是对请求条件的答复：不是程序故障，也不是检查结果。 ‹ 为什么没有开始 › 项目条件未满足：由谁处理的安排不是项目作出的决定；en `#/real/real-refusal`：The system refused this request before the assessment started, and gav ‹ Why it did not start › Project condition not met: who deals with what is not a decision the p
- `E315` zh `#/real/real-refusal`：这次请求所用的项目设定里，“哪个角色由哪个团队担任”的安排只是演示用的占位内容，不是项目作出的决定。系统因此不生成评估结果：否则结果里的处理 ‹ 要让检查能够开始，需要什么 › 在一个真实项目上，要让检查能够开始：需要项目负责人实际决定系统原文（折叠在下面）点名的每个角色由谁担任，然后如实记录。这是一个人员决定，不是；en `#/real/real-refusal`：In the project settings this request used, the arrangement of which te ‹ What is needed for the check to start › On a real project, for the check to be able to start: the project lead
- `E316` zh `#/real/real-refusal`：处理当前拒绝原因不保证随后可评估；其余限制尚未由本次运行验证。 ‹ 本次只返回这一个原因，没有其他环节的诊断。 › 没有任何事项的结论、零问题统计或完成百分比；被拒绝不是“无法判断”，也不是一次没有问题的检查。；en `#/real/real-refusal`：Dealing with the current reason for refusal does not guarantee that an ‹ Only this one reason was returned; there is no diagnosis of any other stage. › No conclusion on any item, no zero-problem count and no completion rat
- `E317` zh `#/real/real-refusal`：本次只返回这一个原因，没有其他环节的诊断。 ‹ 没有任何事项的结论、零问题统计或完成百分比；被拒绝不是“无法判断”，也不是一次没有问题的检查。 › 系统返回的原文（英文）与拒绝码；en `#/real/real-refusal`：Only this one reason was returned; there is no diagnosis of any other  ‹ No conclusion on any item, no zero-problem count and no completion ratio: a refusal is not "Unknown", and not  › What the system returned (as written) and the refusal code
- `E319` zh `#/real/real-refusal`：English ‹ 随附项目的检查尝试 › 本次没有检查结果；en `#/real`：English ‹ Check attempt on the bundled project › Back to the home page
- `E321` zh `#/real/real-refusal`：team-mapping-decision-basis-illustrative复制 ‹ 所提交的请求上下文尚未随拒绝返回。 › [team-mapping-decision-basis-illustrative] project 'pcert-sample' cann；en `#/real/real-refusal`：team-mapping-decision-basis-illustrativeCopy ‹ The context of the request that was submitted has not been returned with the refusal yet. › [team-mapping-decision-basis-illustrative] project 'pcert-sample' cann

#### REFUSAL_REASONS（4 条，待核 4）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E322 | `team-mapping-decision-basis-illustrative.title` | Project condition not met: who deals with what is not a decision the project has made | 项目条件未满足：由谁处理的安排不是项目作出的决定 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |
| E323 | `team-mapping-decision-basis-illustrative.text` | In the project settings this request used, the arrangement of which team fills which role is demonstration placeholder content, not a decision the project has made. The… | 这次请求所用的项目设定里，“哪个角色由哪个团队担任”的安排只是演示用的占位内容，不是项目作出的决定。系统因此不生成评估结果：否则结果里的处理团队会被当成项目的真实安排。 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |
| E324 | `team-mapping-decision-basis-illustrative.action[0]` | On a real project, for the check to be able to start: the project lead has to actually decide who fills each role that the system's own text (folded below) names, and re… | 在一个真实项目上，要让检查能够开始：需要项目负责人实际决定系统原文（折叠在下面）点名的每个角色由谁担任，然后如实记录。这是一个人员决定，不是改一个标签。 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |
| E325 | `team-mapping-decision-basis-illustrative.action[1]` | If this request used the bundled public sample: it has no project lead. For it, this refusal is the correct result; its settings do not need to be changed, and should no… | 如果这次请求用的是随附的公开样例：它没有项目负责人。对它而言，这次拒绝就是正确的结果，不需要、也不应该去改它的设定。 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E322` zh `#/real/real-refusal`：为什么没有开始 ‹ 项目条件未满足：由谁处理的安排不是项目作出的决定 › 这次请求所用的项目设定里，“哪个角色由哪个团队担任”的安排只是演示用的占位内容，不是项目作出的决定。系统因此不生成评估结果：否则结果里的处理；en `#/real/real-refusal`：Why it did not start ‹ Project condition not met: who deals with what is not a decision the project has made › In the project settings this request used, the arrangement of which te
- `E323` zh `#/real/real-refusal`：项目条件未满足：由谁处理的安排不是项目作出的决定 ‹ 这次请求所用的项目设定里，“哪个角色由哪个团队担任”的安排只是演示用的占位内容，不是项目作出的决定。系统因此不生成评估结果：否则结果里的处理团队会被当成项目的真实安排。 › 要让检查能够开始，需要什么；en `#/real/real-refusal`：Project condition not met: who deals with what is not a decision the p ‹ In the project settings this request used, the arrangement of which team fills which role is demonstration pla › What is needed for the check to start
- `E324` zh `#/real/real-refusal`：要让检查能够开始，需要什么 ‹ 在一个真实项目上，要让检查能够开始：需要项目负责人实际决定系统原文（折叠在下面）点名的每个角色由谁担任，然后如实记录。这是一个人员决定，不是改一个标签。 › 如果这次请求用的是随附的公开样例：它没有项目负责人。对它而言，这次拒绝就是正确的结果，不需要、也不应该去改它的设定。；en `#/real/real-refusal`：What is needed for the check to start ‹ On a real project, for the check to be able to start: the project lead has to actually decide who fills each r › If this request used the bundled public sample: it has no project lead
- `E325` zh `#/real/real-refusal`：在一个真实项目上，要让检查能够开始：需要项目负责人实际决定系统原文（折叠在下面）点名的每个角色由谁担任，然后如实记录。这是一个人员决定，不是 ‹ 如果这次请求用的是随附的公开样例：它没有项目负责人。对它而言，这次拒绝就是正确的结果，不需要、也不应该去改它的设定。 › 处理当前拒绝原因不保证随后可评估；其余限制尚未由本次运行验证。；en `#/real/real-refusal`：On a real project, for the check to be able to start: the project lead ‹ If this request used the bundled public sample: it has no project lead. For it, this refusal is the correct re › Dealing with the current reason for refusal does not guarantee that an

#### REFUSAL_SCOPE_NOTE（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E326 | `(整表)` | Dealing with the current reason for refusal does not guarantee that an assessment can follow; the other limitations have not been verified by this run. | 处理当前拒绝原因不保证随后可评估；其余限制尚未由本次运行验证。 | 10/15 批，未核 | zh 1｜en 1｜第二入口 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E326` zh `#/real/real-refusal`：如果这次请求用的是随附的公开样例：它没有项目负责人。对它而言，这次拒绝就是正确的结果，不需要、也不应该去改它的设定。 ‹ 处理当前拒绝原因不保证随后可评估；其余限制尚未由本次运行验证。 › 本次只返回这一个原因，没有其他环节的诊断。；en `#/real/real-refusal`：If this request used the bundled public sample: it has no project lead ‹ Dealing with the current reason for refusal does not guarantee that an assessment can follow; the other limita › Only this one reason was returned; there is no diagnosis of any other

#### RUN_LABELS（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E385 | `real-refusal` | A check attempt on the bundled sample project | 对随附样例项目的一次检查尝试 | 10/15 批，未核 | zh 2｜en 2｜第二入口 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E385` zh `#/real`：仓库随附一个样例项目，下面是对它的一次检查尝试。这个入口只看这个样例，不能换成别的模型；检查自己的 IFC4 文件，用首页的“检查自己的 I ‹ 对随附样例项目的一次检查尝试；en `#/real`：The repository comes with a sample project; below is a check attempt o ‹ A check attempt on the bundled sample project

#### WORKSPACE_REFUSAL（2 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E551 | `original` | What the system returned (as written) and the refusal code | 系统返回的原文（英文）与拒绝码 | 10/8 已核 | zh 1｜en 1｜第二入口；复用 G035 |
| E552 | `code` | Refusal code | 拒绝码 | 10/8 已核 | zh 1｜en 1｜第二入口；复用 G036 |

#### REFUSAL_UNGLOSSED（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E570 | `title` | The system refused this request | 系统拒绝了这次请求 | 10/15 批，未核 | zh 0｜en 1｜第二入口 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E570` en `#/real/real-refusal`：This check attempt did not start an assessment ‹ The system refused this request before the assessment started, and gave its reason. This is an answer about th › Why it did not start

#### CONTEXT（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E592 | `noResult` | No check results this time | 本次没有检查结果 | B 层，10/8 未核 | zh 1｜en 1｜第二入口 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E592` zh `#/real/real-refusal`：随附项目的检查尝试 ‹ 本次没有检查结果 › 返回首页；en `#/real/real-refusal`：Check attempt on the bundled project ‹ No check results this time › Back to the home page

#### DIRECTORY（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| C01 | `realNote` | The repository comes with a sample project; below is a check attempt on it. This entry shows only that sample and cannot be switched to another model; to check your own… | 仓库随附一个样例项目，下面是对它的一次检查尝试。这个入口只看这个样例，不能换成别的模型；检查自己的 IFC4 文件，用首页的“检查自己的 IFC 模型”。Revit 文件本身不能导入。 | 10/8 后改句，需重核 | zh 1｜en 1｜第二入口 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `C01` zh `#/real`：随附项目的检查尝试 ‹ 仓库随附一个样例项目，下面是对它的一次检查尝试。这个入口只看这个样例，不能换成别的模型；检查自己的 IFC4 文件，用首页的“检查自己的 IFC 模型”。Revit 文件本身不能导入。 › 对随附样例项目的一次检查尝试；en `#/real`：Check attempt on the bundled project ‹ The repository comes with a sample project; below is a check attempt on it. This entry shows only that sample  › A check attempt on the bundled sample project

#### LOCAL_CHECK（68 条，待核 68）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| L001 | `mode` | Local check · product validation exercise | 本地检查 · 产品验证练习 | 新增，未核 | zh 42｜en 42｜本地结果页、本地检查（选文件至运行） |
| L005 | `home.statusWithWorkspace` | Available now: a real check already run in the workspace named when the server was started, simulated examples, and one limited product validation exercise on your own I… | 当前提供：启动服务器时指定的工作区里一次已经跑完的真实检查、模拟示例，以及对自己 IFC4 文件的一项有限产品验证练习；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。 | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |
| L006 | `home.statusWorkspaceUnknown` | Could not tell whether the server was started with a workspace, so there is no entry for a workspace check here; that does not mean there is none, and the error is below… | 未能确认服务器是否指定了工作区，所以这里没有工作区检查的入口；这不等于没有工作区，错误原文在下面。模拟示例和本地 IFC 产品验证练习照常可用；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。 | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |
| L010 | `start.lede` | Four steps: first see what this checks and what this computer keeps; choose files; declare disciplines and confirm the rule set; look at the scope, then run. | 四步：先看清这次只检查什么和本机会留下的记录；选择文件；声明专业并确认规则；看清范围后运行。 | 新增，未核 | zh 25｜en 25｜本地检查（选文件至运行） |
| L011 | `start.noRuleset` | This checkout does not carry the product-validation 1.0 rule set, so the local check cannot run. No other rule set is offered here. | 这个检出没有提供 product-validation 1.0 规则集，所以本地检查不能运行。其他规则集不在本地检查里提供。 | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |
| L012 | `exercise.what` | This is a product validation exercise. It checks one thing with this repository's product validation rule set: whether each applicable air terminal (IfcAirTerminal) in a… | 这是一项产品验证练习：只用本仓库的产品验证规则集检查一件事——IFC4 模型里适用的风口（IfcAirTerminal）是否声明了 DIFFUSER、GRILLE、LOUVRE、REGISTER 四种预定义类型之一。它… | 新增，未核 | zh 25｜en 25｜本地检查（选文件至运行） |
| L013 | `exercise.source` | A product validation rule written for this repository; not a project, owner, statutory or buildingSMART requirement. The four values are from IFC4 ADD2 TC1 IfcAirTermina… | 本仓库自己写的产品验证规则，不是项目、业主、法规或 buildingSMART 的要求；四个取值来自 IFC4 ADD2 TC1 的 IfcAirTerminalTypeEnum，只接受这四个是这条规则自己的决定。规则… | 新增，未核 | zh 25｜en 25｜本地检查（选文件至运行） |
| L014 | `exercise.notes` | Whether the checker reads the value from the type or the occurrence, and how free text is compared, is in this rule's notes on the result page. | 检查器从类型还是实例读取取值、自由文本怎样比较，写在结果页这条规则的说明里。 | 新增，未核 | zh 25｜en 25｜本地检查（选文件至运行） |
| L015 | `declare.rulesetLegend` | Rule set (the only one the local check offers) | 规则集（本地检查只提供这一个） | 新增，未核 | zh 25｜en 25｜本地检查（选文件至运行） |
| L016 | `refusal.reasons.unknown-ruleset` | The local check offers product-validation 1.0 only. Choose it. | 本地检查只提供 product-validation 1.0。请选择它。 | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |
| L017 | `result.exercise` | This is the result of a product validation exercise: it only checks whether air terminals declare one of four predefined types. A FAIL does not mean the original project… | 这是产品验证练习的结果：只检查风口是否声明了四种预定义类型之一。不通过不等于原项目有缺陷；通过不证明分类正确、洞口存在、模型已对齐或任何工作可以开始。 | 新增，未核 | zh 16｜en 16｜本地结果页 |
| L018 | `exercise.read[0]` | FAIL: the model does not meet this exercise rule. It does not mean the original project has a defect. | 不通过（FAIL）：不满足这条练习规则，不等于原项目有缺陷。 | 新增，未核 | zh 25｜en 25｜本地检查（选文件至运行） |
| L019 | `exercise.read[1]` | PASS: only that the value the checker read is one of the four. It does not prove the classification is right, that openings exist or that models are aligned, and it does… | 通过（PASS）：只说明检查器读到的值是四个之一；不证明分类正确、洞口存在、模型已对齐，也不说明任何工作可以开始。 | 新增，未核 | zh 25｜en 25｜本地检查（选文件至运行） |
| L020 | `fault.lede` | This is a fault of the program, not a conclusion about the model. The check's directory has been removed and no partial result is left; the model copies chosen before ar… | 这是程序故障，不是对模型的结论。这次检查的目录已经删除，没有留下半份结果；之前选择的模型副本仍在 uploads\ 里。 | 新增，未核 | zh 1｜en 1｜本地检查（选文件至运行） |
| L021 | `fault.todo[2]` | Send the original text below to the maintainer; it only says where the program stopped, not anything about the model's quality. | 把下面的原文发给维护者；原文只描述程序在哪里停下，不说明模型的质量。 | 新增，未核 | zh 1｜en 1｜本地检查（选文件至运行） |
| L022 | `exercise.read[2]` | No air terminal in the chosen model: shown as "nothing applicable". That is not a pass, and this check produced no passing result for anything applicable. | 所选模型里没有风口：显示“没有适用对象”。这不是通过，此次也没有得到任何适用检查的通过结果。 | 新增，未核 | zh 25｜en 25｜本地检查（选文件至运行） |
| L023 | `result.nothingHeading` | Nothing applicable | 没有适用对象 | 新增，未核 | zh 8｜en 8｜本地结果页 |
| L024 | `result.nothing` | {file}: this rule has nothing to apply to in this model. That is not a pass — this check produced no passing result for anything applicable, and it says nothing about th… | {file}：这条规则在这个模型里没有适用对象。这不是通过——此次没有得到任何适用检查的通过结果，也不说明模型质量。 | 新增，未核 | zh 8｜en 8｜本地结果页 |
| L025 | `records.lede` | The check runs on this computer and uploads nothing anywhere. Everything is kept in this directory, fixed before anything runs: | 检查在这台电脑上运行，不上传到任何地方。下面这个目录保存所有记录，运行前就定好： | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L026 | `records.redirected` | The server is running inside a packaged (MSIX) app, and Windows has moved what is written under %LOCALAPPDATA% into the app's own folder. In File Explorer, look in the l… | 服务器运行在打包应用（MSIX）里，Windows 把写到 %LOCALAPPDATA% 下的文件转到了应用自己的文件夹。在资源管理器里要找上面这个“实际位置”；按目录名去找会找不到。想避免这种转移，用下面的命令在 A… | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |
| L027 | `records.notYet` | Nothing is kept yet: the directory is created when the first file is chosen. | 目前还没有任何记录：选择第一个文件时才会创建这个目录。 | 新增，未核 | zh 4｜en 4｜本地检查（选文件至运行） |
| L028 | `records.kept` | Kept now: {uploads} model copies, {checks} checks. | 目前保留：{uploads} 个模型副本，{checks} 次检查。 | 新增，未核 | zh 37｜en 37｜本地结果页、本地检查（选文件至运行） |
| L029 | `records.what[0]` | A copy of every file you choose: uploads\<content digest>.ifc. It is kept as soon as the file is chosen, even if no check is run. | 你选择的每个文件的副本：uploads\<内容摘要>.ifc。选择文件时就会保留，即使最后没有运行检查。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L030 | `records.what[1]` | One directory per check: checks\<check id>\, holding the model copies, a copy of the rule set, the result (data\processed\canonical\run.json), the artifact manifest, the… | 每次检查一个目录：checks\<检查号>\，里面有模型副本、规则集副本、检查结果（data\processed\canonical\run.json）、产物清单、本次检查的范围（check.json）和覆盖记录（co… | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L031 | `records.what[3]` | Nothing is written outside this directory: the repository checkout does not change, and the shared coverage record directory used by the epc-ct run command gains nothing. | 这个目录以外不写任何文件：仓库检出不变，命令行 epc-ct run 使用的共享覆盖记录目录也不增加。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L032 | `records.what[4]` | Closing the page or stopping the server deletes nothing. | 关闭页面或停止服务器都不会删除记录。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L033 | `records.clean[0]` | Stop the server: press Ctrl+C in the terminal running it. | 停止服务器：在运行它的终端里按 Ctrl+C。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L034 | `records.clean[1]` | Open the location above in File Explorer (where the location differs from the directory name, use the location). | 在资源管理器里打开上面的位置（实际位置与目录名不同时，用实际位置）。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L035 | `records.clean[2]` | Delete the whole directory to remove every record; to remove one check, delete checks\<check id>\. The model copies it used are in uploads\, named by content digest; the… | 删除整个目录，就清除了全部记录；只想删一次检查，删除 checks\<检查号>\。它用过的模型副本在 uploads\ 里，按内容摘要命名；摘要写在检查结果页的追溯信息里。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L036 | `records.start` | From the repository directory, start the server in your own terminal with a folder outside AppData, for example: | 在仓库目录里，用自己的终端启动服务器，并指定 AppData 以外的文件夹，例如： | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L037 | `records.startNote` | The server prints the directory when it starts. It exists once the first file is chosen; if Windows keeps it somewhere else, this page shows where. | 服务器启动时会打印目录。第一次选择文件后目录才存在；如果 Windows 把它放到了别处，这一页会显示实际位置。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L038 | `choose.removed` | Taken out of this selection; its copy is still in uploads\. Delete it with the clean-up steps above. | 已从本次选择中去掉；它的副本仍在 uploads\ 里，按上面的清理步骤删除。 | 新增，未核 | zh 1｜en 1｜本地检查（选文件至运行） |
| L039 | `earlier.note` | Kept in the directory above until you delete them. | 保存在上面的目录里，直到你删除它们。 | 新增，未核 | zh 25｜en 25｜本地检查（选文件至运行） |
| L040 | `result.missing` | There is no such check: it may have been cleaned up (its directory deleted), or the link is wrong. After cleaning up, result links stop opening. | 没有这次检查：它可能已被清理（目录被删除），或者链接不对。清理之后，结果页链接就打不开了。 | 新增，未核 | zh 1｜en 1｜本地检查（选文件至运行） |
| L041 | `records.after[0]` | A deleted check's result link stops opening; the page says there is no such check. | 已删除检查的结果页链接打不开，页面会说没有这次检查。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L042 | `records.after[1]` | It can no longer be compared with a later check. | 不能再拿它和以后的检查对比。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L043 | `records.after[2]` | Its coverage record goes with it, so nothing can say afterwards which elements and requirements that check covered. | 它的覆盖记录一起删除，之后无法再说明那次检查覆盖了哪些构件和要求。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L044 | `records.after[3]` | Once a model copy is deleted, the file has to be chosen again to check it. | 删除模型副本后，要再检查就得重新选择文件。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L045 | `records.again` | Checking the same file again, declared as the same discipline, with the same rule set version and the same logical date, gives the same check id and byte-identical resul… | 用同一个文件、同样声明的专业、同一规则集版本和同一逻辑日期重新检查，会得到同一个检查号和逐字节相同的结果。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L046 | `declare.disciplineNote` | You declare the discipline; it is not guessed from the file name, and it is written into the check's record. It does not narrow the check now: the rule checks every air… | 专业由你声明，不从文件名猜测，写进本次检查的记录。它目前不缩小检查范围：规则会检查所选文件里的全部风口，不论声明的是哪个专业（规则自己声明适用于 {scope} 模型）。 | 新增，未核 | zh 25｜en 25｜本地检查（选文件至运行） |
| L047 | `result.declared` | {file} (discipline you declared: {discipline}) | {file}（你声明的专业：{discipline}） | 新增，未核 | zh 16｜en 16｜本地结果页 |
| L048 | `refusal.reasons.discipline-not-declared` | No discipline is declared. Choose one for this file. | 还没有声明专业。为这个文件选择一个专业。 | 新增，未核 | zh 1｜en 1｜本地检查（选文件至运行） |
| L049 | `refusal.reasons.unknown-discipline` | The declared discipline is not in the list here. Choose one from the list. | 声明的专业不在这里的专业列表里。请从列表里选择。 | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |
| L051 | `disciplines.HVAC` | HVAC | 暖通（HVAC） | 新增，未核 | zh 16｜en 29｜本地结果页、本地检查（选文件至运行） |
| L053 | `disciplines.Plumbing` | Plumbing | 给排水（Plumbing） | 新增，未核 | zh 16｜en 16｜本地检查（选文件至运行） |
| L054 | `disciplines.Structural` | Structural | 结构（Structural） | 新增，未核 | zh 16｜en 16｜本地检查（选文件至运行） |
| L055 | `choose.note` | Only IFC-SPF text (.ifc) is accepted, not .ifczip, .ifcxml or Revit files; at most {max} per file. The rule set reads IFC4 only; an IFC2x3 file is refused, with how to e… | 只接受 IFC-SPF 文本（.ifc），不接受 .ifczip、.ifcxml 或 Revit 文件；单个文件最大 {max}。规则集只读取 IFC4，IFC2x3 文件会被拒绝，并告诉你怎样重新导出。 | 新增，未核 | zh 25｜en 25｜本地检查（选文件至运行） |
| L056 | `refusal.lede` | No check was run and there is no result. Each reason, and what to do: | 没有运行任何检查，也没有产生结果。每个原因和要做的事： | 新增，未核 | zh 4｜en 4｜本地检查（选文件至运行） |
| L057 | `refusal.reasons.unsupported-schema` | The rule set's checker reads IFC4 only, and this file is not IFC4 (IFC2x3, for example). To recover: in Revit's IFC export dialog, set the IFC version to IFC4 Reference… | 规则集的检查程序只读取 IFC4，这个文件不是 IFC4（例如 IFC2x3）。恢复办法：在 Revit 的 IFC 导出对话框里，把 IFC 版本选为 IFC4 Reference View，重新导出后选择新文件。原… | 新增，未核 | zh 1｜en 1｜本地检查（选文件至运行） |
| L058 | `refusal.reasons.not-an-ifc` | This is not an IFC-SPF text file: it does not begin with an ISO-10303-21 header. Choose the .ifc file Revit exported, not an .ifczip, .ifcxml or .rvt. | 这不是 IFC-SPF 文本文件：开头没有 ISO-10303-21 文件头。请选择 Revit 导出的 .ifc 文件，不是 .ifczip、.ifcxml 或 .rvt。 | 新增，未核 | zh 1｜en 1｜本地检查（选文件至运行） |
| L059 | `refusal.reasons.model-too-large` | The file is over this server's limit and was not read. Export a smaller model, or restart the server with a larger --max-model-bytes. | 文件超过这台服务器接受的上限，没有读取。可以导出范围更小的模型，或用更大的 --max-model-bytes 重新启动服务器。 | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |
| L060 | `refusal.reasons.model-incomplete` | The file did not reach the server in full and was not kept. Choose the file again. | 文件没有完整传到服务器，没有保留。请重新选择这个文件。 | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |
| L061 | `refusal.reasons.model-name-invalid` | The file name cannot name a model: it must end in .ifc, not start with ".", and have no path or any of < > : " / \ \| ? *. Rename it and choose it again. | 文件名不能用作模型名：要以 .ifc 结尾，不以“.”开头，不含路径或 < > : " / \ \| ? *。请改名后重新选择。 | 新增，未核 | zh 1｜en 0｜本地检查（选文件至运行） |
| L062 | `refusal.reasons.unknown-model` | The server holds no copy of this file (it may have been cleaned up). Choose the file again. | 服务器上没有这个文件的副本（可能已被清理）。请重新选择这个文件。 | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |
| L063 | `refusal.reasons.duplicate-model` | The same file, a file of the same name, or one with the same content was chosen twice. Choose each model once. | 同一个文件、同名文件或内容相同的文件选了两次。每个模型只选一次。 | 新增，未核 | zh 1｜en 1｜本地检查（选文件至运行） |
| L064 | `refusal.reasons.no-model` | No file has been chosen. Choose at least one .ifc file. | 还没有选择文件。至少选择一个 .ifc 文件。 | 新增，未核 | zh 1｜en 1｜本地检查（选文件至运行） |
| L065 | `refusal.reasons.busy` | Another check is running; one runs at a time. Wait for it to finish, then run this one. | 另一次检查正在运行，一次只运行一个。等它完成后再运行这一次。 | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |
| L066 | `fault.todo[0]` | Make sure the file is an IFC4 file exported from Revit, and run again. | 确认文件是从 Revit 导出的 IFC4 文件，再运行一次。 | 新增，未核 | zh 1｜en 1｜本地检查（选文件至运行） |
| L067 | `fault.todo[1]` | If the same file fails here every time, export it again and choose the new file. | 如果同一个文件每次都在这里失败，重新导出后再选择新文件。 | 新增，未核 | zh 1｜en 1｜本地检查（选文件至运行） |
| L068 | `fault.network` | No answer came from the server: it may have stopped. Start the server, then reload this page. | 没有收到服务器的回答：服务器可能已经停止。启动服务器后，刷新这一页。 | 新增，未核 | zh 1｜en 2｜本地检查（选文件至运行） |
| L069 | `scope.geometryText` | No geometry is computed. An element without a shape does not stop the check from finishing; its check result, identity and next step are shown as usual. There is no 3D v… | 不计算几何。没有形体的构件不会让整次检查中断，它的检查结果、标识和下一步照常显示；本次结果也没有 3D 视图。 | 新增，未核 | zh 26｜en 26｜本地结果页、本地检查（选文件至运行） |
| L070 | `records.what[2]` | 3D geometry cache: none is made now. When a 3D view is added, its cache will be kept in this directory too and cleaned up the same way. | 3D 几何缓存：现在不生成。以后加入 3D 查看时，它的缓存也放在这个目录里，按下面同样的步骤清理。 | 新增，未核 | zh 41｜en 41｜本地结果页、本地检查（选文件至运行） |
| L071 | `scope.ready` | The server will run this check with the scope below; confirm it, then run. | 服务器按下面的范围运行这次检查；确认后再运行。 | 新增，未核 | zh 10｜en 10｜本地检查（选文件至运行） |
| L072 | `scope.checkId` | Check id (decided by the rule set, the logical date, and each file's name, discipline and content) | 检查号（由规则集、逻辑日期和每个文件的名称、专业、内容决定） | 新增，未核 | zh 10｜en 10｜本地检查（选文件至运行） |
| L073 | `scope.asOfNote` | (set by the run configuration, not today's date) | （运行配置给定，不是今天的日期） | 新增，未核 | zh 10｜en 10｜本地检查（选文件至运行） |
| L074 | `scope.programmeText` | Your model brings no programme. The rule set's rules name the stages {stages}, so this check fills those stages in, with no due date; the result page shows no due date,… | 你的模型不带进度计划。规则集的规则写了阶段 {stages}，所以本次检查代填了这些阶段，没有到期日；结果页不显示到期、逾期或优先级。 | 新增，未核 | zh 10｜en 10｜本地检查（选文件至运行） |
| L075 | `result.programme` | Programme: the rule set's stages {stages} were filled in by this check, with no due date; this page shows no due date, overdue state or priority. | 进度计划：规则集的阶段 {stages} 由本次检查代填，没有到期日；本页不显示到期、逾期或优先级。 | 新增，未核 | zh 16｜en 16｜本地结果页 |
| L076 | `scope.running` | Checking. This may take from tens of seconds to a few minutes; the result opens when it is done. | 正在检查，可能需要几十秒到几分钟。完成后会打开结果。 | 新增，未核 | zh 5｜en 5｜本地检查（选文件至运行） |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `L001` zh `flow:check-both:result`：English ‹ 本地检查 · 产品验证练习 › c653c7e0bb676a4a；en `flow:check-both:result`：English ‹ Local check · product validation exercise › c653c7e0bb676a4a
- `L010` zh `#/local`：检查自己的 IFC 模型 ‹ 四步：先看清这次只检查什么和本机会留下的记录；选择文件；声明专业并确认规则；看清范围后运行。 › 这次只检查什么；en `#/local`：Check your own IFC model ‹ Four steps: first see what this checks and what this computer keeps; choose files; declare disciplines and con › What this checks, and only this
- `L012` zh `#/local`：这次只检查什么 ‹ 这是一项产品验证练习：只用本仓库的产品验证规则集检查一件事——IFC4 模型里适用的风口（IfcAirTerminal）是否声明了 DIFFUSER、GRILLE、LOUVRE、REGISTER 四种预定义类型之一。它不 › product-validation 1.0 Product Validation Rules；en `#/local`：What this checks, and only this ‹ This is a product validation exercise. It checks one thing with this repository's product validation rule set: › product-validation 1.0 Product Validation Rules
- `L013` zh `#/local`：要求从哪里来 ‹ 本仓库自己写的产品验证规则，不是项目、业主、法规或 buildingSMART 的要求；四个取值来自 IFC4 ADD2 TC1 的 IfcAirTerminalTypeEnum，只接受这四个是这条规则自己的决定。规则集 › Rules written to exercise this product's check, source-fix and recheck；en `#/local`：Where the requirement comes from ‹ A product validation rule written for this repository; not a project, owner, statutory or buildingSMART requir › Rules written to exercise this product's check, source-fix and recheck
- `L014` zh `#/local`：所选模型里没有风口：显示“没有适用对象”。这不是通过，此次也没有得到任何适用检查的通过结果。 ‹ 检查器从类型还是实例读取取值、自由文本怎样比较，写在结果页这条规则的说明里。 › 本机会留下哪些记录；en `#/local`：No air terminal in the chosen model: shown as "nothing applicable". Th ‹ Whether the checker reads the value from the type or the occurrence, and how free text is compared, is in this › What this computer keeps
- `L015` zh `#/local`：2. 声明专业并确认规则集 ‹ 规则集（本地检查只提供这一个） › product-validation 1.0：Product Validation Rules；en `#/local`：2. Declare disciplines and confirm the rule set ‹ Rule set (the only one the local check offers) › product-validation 1.0: Product Validation Rules
- `L017` zh `flow:check-both:result`：一次真实检查的结果 ‹ 这是产品验证练习的结果：只检查风口是否声明了四种预定义类型之一。不通过不等于原项目有缺陷；通过不证明分类正确、洞口存在、模型已对齐或任何工作可以开始。 › 没有适用对象；en `flow:check-both:result`：Results of a real check ‹ This is the result of a product validation exercise: it only checks whether air terminals declare one of four  › Nothing applicable
- `L018` zh `#/local`：结果怎么读 ‹ 不通过（FAIL）：不满足这条练习规则，不等于原项目有缺陷。 › 通过（PASS）：只说明检查器读到的值是四个之一；不证明分类正确、洞口存在、模型已对齐，也不说明任何工作可以开始。；en `#/local`：How to read the result ‹ FAIL: the model does not meet this exercise rule. It does not mean the original project has a defect. › PASS: only that the value the checker read is one of the four. It does
- `L019` zh `#/local`：不通过（FAIL）：不满足这条练习规则，不等于原项目有缺陷。 ‹ 通过（PASS）：只说明检查器读到的值是四个之一；不证明分类正确、洞口存在、模型已对齐，也不说明任何工作可以开始。 › 所选模型里没有风口：显示“没有适用对象”。这不是通过，此次也没有得到任何适用检查的通过结果。；en `#/local`：FAIL: the model does not meet this exercise rule. It does not mean the ‹ PASS: only that the value the checker read is one of the four. It does not prove the classification is right,  › No air terminal in the chosen model: shown as "nothing applicable". Th
- `L020` zh `flow:check-garbled:after-run`：检查没有完成 ‹ 这是程序故障，不是对模型的结论。这次检查的目录已经删除，没有留下半份结果；之前选择的模型副本仍在 uploads\ 里。 › 可以怎么做；en `flow:check-garbled:after-run`：The check did not finish ‹ This is a fault of the program, not a conclusion about the model. The check's directory has been removed and n › What you can do
- `L021` zh `flow:check-garbled:after-run`：如果同一个文件每次都在这里失败，重新导出后再选择新文件。 ‹ 把下面的原文发给维护者；原文只描述程序在哪里停下，不说明模型的质量。 › 故障原文；en `flow:check-garbled:after-run`：If the same file fails here every time, export it again and choose the ‹ Send the original text below to the maintainer; it only says where the program stopped, not anything about the › The fault as given
- `L022` zh `#/local`：通过（PASS）：只说明检查器读到的值是四个之一；不证明分类正确、洞口存在、模型已对齐，也不说明任何工作可以开始。 ‹ 所选模型里没有风口：显示“没有适用对象”。这不是通过，此次也没有得到任何适用检查的通过结果。 › 检查器从类型还是实例读取取值、自由文本怎样比较，写在结果页这条规则的说明里。；en `#/local`：PASS: only that the value the checker read is one of the four. It does ‹ No air terminal in the chosen model: shown as "nothing applicable". That is not a pass, and this check produce › Whether the checker reads the value from the type or the occurrence, a
- `L023` zh `flow:check-both:result`：这是产品验证练习的结果：只检查风口是否声明了四种预定义类型之一。不通过不等于原项目有缺陷；通过不证明分类正确、洞口存在、模型已对齐或任何工作 ‹ 没有适用对象 › Building-Architecture.ifc：这条规则在这个模型里没有适用对象。这不是通过——此次没有得到任何适用检查的通过结果，也不；en `flow:check-both:result`：This is the result of a product validation exercise: it only checks wh ‹ Nothing applicable › Building-Architecture.ifc: this rule has nothing to apply to in this m
- `L024` zh `flow:check-both:result`：没有适用对象 ‹ Building-Architecture.ifc：这条规则在这个模型里没有适用对象。这不是通过——此次没有得到任何适用检查的通过结果，也不说明模型质量。 › 这次检查的范围；en `flow:check-both:result`：Nothing applicable ‹ Building-Architecture.ifc: this rule has nothing to apply to in this model. That is not a pass — this check pr › The scope of this check
- `L025` zh `flow:check-both:result`：这次检查的记录在哪里，怎样清理 ‹ 检查在这台电脑上运行，不上传到任何地方。下面这个目录保存所有记录，运行前就定好： › 目录；en `flow:check-both:result`：Where this check's records are, and how to clean up ‹ The check runs on this computer and uploads nothing anywhere. Everything is kept in this directory, fixed befo › Directory
- `L027` zh `flow:fresh:start-nothing-kept`：C:\Users\ericr\AppData\Local\Temp\ep-subset-checks-b复制 ‹ 目前还没有任何记录：选择第一个文件时才会创建这个目录。 › 会留下什么；en `flow:fresh:start-nothing-kept`：C:\Users\ericr\AppData\Local\Temp\ep-subset-checks-cCopy ‹ Nothing is kept yet: the directory is created when the first file is chosen. › What is kept
- `L028` zh `flow:check-both:result`：C:\Users\ericr\AppData\Local\Temp\ep-subset-checks\checks\c653c7e0bb67 ‹ 目前保留：5 个模型副本，4 次检查。 › 怎样清理；en `flow:check-both:result`：C:\Users\ericr\AppData\Local\Temp\ep-subset-checks\checks\c653c7e0bb67 ‹ Kept now: 5 model copies, 4 checks. › How to clean up
- `L029` zh `flow:check-both:result`：会留下什么 ‹ 你选择的每个文件的副本：uploads\<内容摘要>.ifc。选择文件时就会保留，即使最后没有运行检查。 › 每次检查一个目录：checks\<检查号>\，里面有模型副本、规则集副本、检查结果（data\processed\canonical\run；en `flow:check-both:result`：What is kept ‹ A copy of every file you choose: uploads\<content digest>.ifc. It is kept as soon as the file is chosen, even  › One directory per check: checks\<check id>\, holding the model copies,
- `L030` zh `flow:check-both:result`：你选择的每个文件的副本：uploads\<内容摘要>.ifc。选择文件时就会保留，即使最后没有运行检查。 ‹ 每次检查一个目录：checks\<检查号>\，里面有模型副本、规则集副本、检查结果（data\processed\canonical\run.json）、产物清单、本次检查的范围（check.json）和覆盖记录（cov › 3D 几何缓存：现在不生成。以后加入 3D 查看时，它的缓存也放在这个目录里，按下面同样的步骤清理。；en `flow:check-both:result`：A copy of every file you choose: uploads\<content digest>.ifc. It is k ‹ One directory per check: checks\<check id>\, holding the model copies, a copy of the rule set, the result (dat › 3D geometry cache: none is made now. When a 3D view is added, its cach
- `L031` zh `flow:check-both:result`：3D 几何缓存：现在不生成。以后加入 3D 查看时，它的缓存也放在这个目录里，按下面同样的步骤清理。 ‹ 这个目录以外不写任何文件：仓库检出不变，命令行 epc-ct run 使用的共享覆盖记录目录也不增加。 › 关闭页面或停止服务器都不会删除记录。；en `flow:check-both:result`：3D geometry cache: none is made now. When a 3D view is added, its cach ‹ Nothing is written outside this directory: the repository checkout does not change, and the shared coverage re › Closing the page or stopping the server deletes nothing.
- `L032` zh `flow:check-both:result`：这个目录以外不写任何文件：仓库检出不变，命令行 epc-ct run 使用的共享覆盖记录目录也不增加。 ‹ 关闭页面或停止服务器都不会删除记录。 › 怎样清理；en `flow:check-both:result`：Nothing is written outside this directory: the repository checkout doe ‹ Closing the page or stopping the server deletes nothing. › How to clean up
- `L033` zh `flow:check-both:result`：怎样清理 ‹ 停止服务器：在运行它的终端里按 Ctrl+C。 › 在资源管理器里打开上面的位置（实际位置与目录名不同时，用实际位置）。；en `flow:check-both:result`：How to clean up ‹ Stop the server: press Ctrl+C in the terminal running it. › Open the location above in File Explorer (where the location differs f
- `L034` zh `flow:check-both:result`：停止服务器：在运行它的终端里按 Ctrl+C。 ‹ 在资源管理器里打开上面的位置（实际位置与目录名不同时，用实际位置）。 › 删除整个目录，就清除了全部记录；只想删一次检查，删除 checks\<检查号>\。它用过的模型副本在 uploads\ 里，按内容摘要命名；；en `flow:check-both:result`：Stop the server: press Ctrl+C in the terminal running it. ‹ Open the location above in File Explorer (where the location differs from the directory name, use the location › Delete the whole directory to remove every record; to remove one check
- `L035` zh `flow:check-both:result`：在资源管理器里打开上面的位置（实际位置与目录名不同时，用实际位置）。 ‹ 删除整个目录，就清除了全部记录；只想删一次检查，删除 checks\<检查号>\。它用过的模型副本在 uploads\ 里，按内容摘要命名；摘要写在检查结果页的追溯信息里。 › 清理之后不能再依赖什么；en `flow:check-both:result`：Open the location above in File Explorer (where the location differs f ‹ Delete the whole directory to remove every record; to remove one check, delete checks\<check id>\. The model c › What you can no longer rely on after cleaning up
- `L036` zh `flow:check-both:result`：怎样把记录放在别的文件夹 ‹ 在仓库目录里，用自己的终端启动服务器，并指定 AppData 以外的文件夹，例如： › python doctor/serve.py --checks-dir "%USERPROFILE%\Documents\BIM Docto；en `flow:check-both:result`：How to keep the records in another folder ‹ From the repository directory, start the server in your own terminal with a folder outside AppData, for exampl › python doctor/serve.py --checks-dir "%USERPROFILE%\Documents\BIM Docto
- `L037` zh `flow:check-both:result`：python doctor/serve.py --checks-dir "%USERPROFILE%\Documents\BIM Docto ‹ 服务器启动时会打印目录。第一次选择文件后目录才存在；如果 Windows 把它放到了别处，这一页会显示实际位置。 › 检查另一个模型；en `flow:check-both:result`：python doctor/serve.py --checks-dir "%USERPROFILE%\Documents\BIM Docto ‹ The server prints the directory when it starts. It exists once the first file is chosen; if Windows keeps it s › Check another model
- `L038` zh `flow:fresh:chosen-file-removed`：选择一个或多个 .ifc 文件 ‹ 已从本次选择中去掉；它的副本仍在 uploads\ 里，按上面的清理步骤删除。 › 已选择的文件；en `flow:fresh:chosen-file-removed`：Choose one or more .ifc files ‹ Taken out of this selection; its copy is still in uploads\. Delete it with the clean-up steps above. › Chosen files
- `L039` zh `#/local`：以前的检查 ‹ 保存在上面的目录里，直到你删除它们。 › Building-Architecture.ifc、Building-Hvac.ifc · product-validation 1.0 ·；en `#/local`：Earlier checks ‹ Kept in the directory above until you delete them. › Building-Architecture.ifc, Building-Hvac.ifc · product-validation 1.0
- `L040` zh `flow:local:result-missing`：检查自己的 IFC 模型 ‹ 没有这次检查：它可能已被清理（目录被删除），或者链接不对。清理之后，结果页链接就打不开了。 › 检查另一个模型；en `flow:local:result-missing`：Check your own IFC model ‹ There is no such check: it may have been cleaned up (its directory deleted), or the link is wrong. After clean › Check another model
- `L041` zh `flow:check-both:result`：清理之后不能再依赖什么 ‹ 已删除检查的结果页链接打不开，页面会说没有这次检查。 › 不能再拿它和以后的检查对比。；en `flow:check-both:result`：What you can no longer rely on after cleaning up ‹ A deleted check's result link stops opening; the page says there is no such check. › It can no longer be compared with a later check.
- `L042` zh `flow:check-both:result`：已删除检查的结果页链接打不开，页面会说没有这次检查。 ‹ 不能再拿它和以后的检查对比。 › 它的覆盖记录一起删除，之后无法再说明那次检查覆盖了哪些构件和要求。；en `flow:check-both:result`：A deleted check's result link stops opening; the page says there is no ‹ It can no longer be compared with a later check. › Its coverage record goes with it, so nothing can say afterwards which
- `L043` zh `flow:check-both:result`：不能再拿它和以后的检查对比。 ‹ 它的覆盖记录一起删除，之后无法再说明那次检查覆盖了哪些构件和要求。 › 删除模型副本后，要再检查就得重新选择文件。；en `flow:check-both:result`：It can no longer be compared with a later check. ‹ Its coverage record goes with it, so nothing can say afterwards which elements and requirements that check cov › Once a model copy is deleted, the file has to be chosen again to check
- `L044` zh `flow:check-both:result`：它的覆盖记录一起删除，之后无法再说明那次检查覆盖了哪些构件和要求。 ‹ 删除模型副本后，要再检查就得重新选择文件。 › 用同一个文件、同样声明的专业、同一规则集版本和同一逻辑日期重新检查，会得到同一个检查号和逐字节相同的结果。；en `flow:check-both:result`：Its coverage record goes with it, so nothing can say afterwards which  ‹ Once a model copy is deleted, the file has to be chosen again to check it. › Checking the same file again, declared as the same discipline, with th
- `L045` zh `flow:check-both:result`：删除模型副本后，要再检查就得重新选择文件。 ‹ 用同一个文件、同样声明的专业、同一规则集版本和同一逻辑日期重新检查，会得到同一个检查号和逐字节相同的结果。 › 怎样把记录放在别的文件夹；en `flow:check-both:result`：Once a model copy is deleted, the file has to be chosen again to check ‹ Checking the same file again, declared as the same discipline, with the same rule set version and the same log › How to keep the records in another folder
- `L046` zh `#/local`：product-validation 1.0：Product Validation Rules ‹ 专业由你声明，不从文件名猜测，写进本次检查的记录。它目前不缩小检查范围：规则会检查所选文件里的全部风口，不论声明的是哪个专业（规则自己声明适用于 暖通（HVAC）、机电（MEP） 模型）。 › 查看检查范围；en `#/local`：product-validation 1.0: Product Validation Rules ‹ You declare the discipline; it is not guessed from the file name, and it is written into the check's record. I › See the scope of the check
- `L047` zh `flow:check-both:result`：product-validation 1.0 Product Validation Rules ‹ Building-Architecture.ifc（你声明的专业：建筑（Architecture）） › Building-Hvac.ifc（你声明的专业：暖通（HVAC））；en `flow:check-both:result`：product-validation 1.0 Product Validation Rules ‹ Building-Architecture.ifc (discipline you declared: Architecture) › Building-Hvac.ifc (discipline you declared: HVAC)
- `L048` zh `flow:local:plan-refused-discipline-not-declared`：没有运行任何检查，也没有产生结果。每个原因和要做的事： ‹ Building-Hvac.ifc：还没有声明专业。为这个文件选择一个专业。 discipline-not-declared › 系统返回的原文（英文）；en `flow:local:plan-refused-discipline-not-declared`：No check was run and there is no result. Each reason, and what to do: ‹ Building-Hvac.ifc: No discipline is declared. Choose one for this file. discipline-not-declared › What the system returned (English original)
- `L051` zh `flow:local:chosen`：建筑（Architecture） ‹ 暖通（HVAC） › 机电（MEP）；en `flow:check-both:result`：Building-Architecture.ifc (discipline you declared: Architecture) ‹ Building-Hvac.ifc (discipline you declared: HVAC) › Programme: the rule set's stages Coordination were filled in by this c
- `L053` zh `flow:local:chosen`：机电（MEP） ‹ 给排水（Plumbing） › 结构（Structural）；en `flow:local:chosen`：MEP ‹ Plumbing › Structural
- `L054` zh `flow:local:chosen`：给排水（Plumbing） ‹ 结构（Structural） › 专业由你声明，不从文件名猜测，写进本次检查的记录。它目前不缩小检查范围：规则会检查所选文件里的全部风口，不论声明的是哪个专业（规则自己声明适；en `flow:local:chosen`：Plumbing ‹ Structural › You declare the discipline; it is not guessed from the file name, and
- `L055` zh `#/local`：1. 选择 IFC 文件 ‹ 只接受 IFC-SPF 文本（.ifc），不接受 .ifczip、.ifcxml 或 Revit 文件；单个文件最大 4.3 GB。规则集只读取 IFC4，IFC2x3 文件会被拒绝，并告诉你怎样重新导出。 › 选择一个或多个 .ifc 文件；en `#/local`：1. Choose IFC files ‹ Only IFC-SPF text (.ifc) is accepted, not .ifczip, .ifcxml or Revit files; at most 4.3 GB per file. The rule s › Choose one or more .ifc files
- `L056` zh `flow:fresh:plan-same-name-twice`：这次检查不能开始 ‹ 没有运行任何检查，也没有产生结果。每个原因和要做的事： › same.ifc：同一个文件、同名文件或内容相同的文件选了两次。每个模型只选一次。 duplicate-model；en `flow:fresh:plan-same-name-twice`：This check cannot start ‹ No check was run and there is no result. Each reason, and what to do: › same.ifc: The same file, a file of the same name, or one with the same
- `L057` zh `flow:local:plan-refused-unsupported-schema`：没有运行任何检查，也没有产生结果。每个原因和要做的事： ‹ old-schema.ifc：规则集的检查程序只读取 IFC4，这个文件不是 IFC4（例如 IFC2x3）。恢复办法：在 Revit 的 IFC 导出对话框里，把 IFC 版本选为 IFC4 Reference Vie › 系统返回的原文（英文）；en `flow:local:plan-refused-unsupported-schema`：No check was run and there is no result. Each reason, and what to do: ‹ old-schema.ifc: The rule set's checker reads IFC4 only, and this file is not IFC4 (IFC2x3, for example). To re › What the system returned (English original)
- `L058` zh `flow:local:file-refused-not-an-ifc`：这个文件没有被接受：not-an-ifc.ifc ‹ not-an-ifc.ifc：这不是 IFC-SPF 文本文件：开头没有 ISO-10303-21 文件头。请选择 Revit 导出的 .ifc 文件，不是 .ifczip、.ifcxml 或 .rvt。 not-an- › 系统返回的原文（英文）；en `flow:local:file-refused-not-an-ifc`：This file was not accepted: not-an-ifc.ifc ‹ not-an-ifc.ifc: This is not an IFC-SPF text file: it does not begin with an ISO-10303-21 header. Choose the .i › What the system returned (English original)
- `L061` zh `flow:fresh:file-refused-name-invalid`：这个文件没有被接受：.hidden.ifc ‹ .hidden.ifc：文件名不能用作模型名：要以 .ifc 结尾，不以“.”开头，不含路径或 < > : " / \ \| ? *。请改名后重新选择。 model-name-invalid › 系统返回的原文（英文）
- `L063` zh `flow:fresh:plan-same-name-twice`：没有运行任何检查，也没有产生结果。每个原因和要做的事： ‹ same.ifc：同一个文件、同名文件或内容相同的文件选了两次。每个模型只选一次。 duplicate-model › 系统返回的原文（英文）；en `flow:fresh:plan-same-name-twice`：No check was run and there is no result. Each reason, and what to do: ‹ same.ifc: The same file, a file of the same name, or one with the same content was chosen twice. Choose each m › What the system returned (English original)
- `L064` zh `flow:fresh:plan-refused-no-model`：没有运行任何检查，也没有产生结果。每个原因和要做的事： ‹ 还没有选择文件。至少选择一个 .ifc 文件。 no-model › 系统返回的原文（英文）；en `flow:fresh:plan-refused-no-model`：No check was run and there is no result. Each reason, and what to do: ‹ No file has been chosen. Choose at least one .ifc file. no-model › What the system returned (English original)
- `L066` zh `flow:check-garbled:after-run`：可以怎么做 ‹ 确认文件是从 Revit 导出的 IFC4 文件，再运行一次。 › 如果同一个文件每次都在这里失败，重新导出后再选择新文件。；en `flow:check-garbled:after-run`：What you can do ‹ Make sure the file is an IFC4 file exported from Revit, and run again. › If the same file fails here every time, export it again and choose the
- `L067` zh `flow:check-garbled:after-run`：确认文件是从 Revit 导出的 IFC4 文件，再运行一次。 ‹ 如果同一个文件每次都在这里失败，重新导出后再选择新文件。 › 把下面的原文发给维护者；原文只描述程序在哪里停下，不说明模型的质量。；en `flow:check-garbled:after-run`：Make sure the file is an IFC4 file exported from Revit, and run again. ‹ If the same file fails here every time, export it again and choose the new file. › Send the original text below to the maintainer; it only says where the
- `L068` zh `flow:fresh:file-refused-too-large`：检查没有完成 ‹ 没有收到服务器的回答：服务器可能已经停止。启动服务器后，刷新这一页。 › 以前的检查；en `flow:fresh:file-refused-too-large`：The check did not finish ‹ No answer came from the server: it may have stopped. Start the server, then reload this page. › Earlier checks
- `L069` zh `flow:check-both:result`：进度计划：规则集的阶段 Coordination 由本次检查代填，没有到期日；本页不显示到期、逾期或优先级。 ‹ 不计算几何。没有形体的构件不会让整次检查中断，它的检查结果、标识和下一步照常显示；本次结果也没有 3D 视图。 › 这是一次检查的结果，不是交接判断：页面只说每个构件在每条要求下通过、不通过还是不适用，不对任何工作能否开始下结论。；en `flow:check-both:result`：Programme: the rule set's stages Coordination were filled in by this c ‹ No geometry is computed. An element without a shape does not stop the check from finishing; its check result,  › These are the results of a check, not a handover judgement: the page s
- `L070` zh `flow:check-both:result`：每次检查一个目录：checks\<检查号>\，里面有模型副本、规则集副本、检查结果（data\processed\canonical\run ‹ 3D 几何缓存：现在不生成。以后加入 3D 查看时，它的缓存也放在这个目录里，按下面同样的步骤清理。 › 这个目录以外不写任何文件：仓库检出不变，命令行 epc-ct run 使用的共享覆盖记录目录也不增加。；en `flow:check-both:result`：One directory per check: checks\<check id>\, holding the model copies, ‹ 3D geometry cache: none is made now. When a 3D view is added, its cache will be kept in this directory too and › Nothing is written outside this directory: the repository checkout doe
- `L071` zh `flow:check-both:planned`：3. 运行前确认范围 ‹ 服务器按下面的范围运行这次检查；确认后再运行。 › 检查号（由规则集、逻辑日期和每个文件的名称、专业、内容决定）；en `flow:check-both:planned`：3. Confirm the scope before running ‹ The server will run this check with the scope below; confirm it, then run. › Check id (decided by the rule set, the logical date, and each file's n
- `L072` zh `flow:check-both:planned`：服务器按下面的范围运行这次检查；确认后再运行。 ‹ 检查号（由规则集、逻辑日期和每个文件的名称、专业、内容决定） › c653c7e0bb676a4a；en `flow:check-both:planned`：The server will run this check with the scope below; confirm it, then  ‹ Check id (decided by the rule set, the logical date, and each file's name, discipline and content) › c653c7e0bb676a4a
- `L073` zh `flow:check-both:planned`：逻辑日期 ‹ 2026-08-13T00:00:00Z （运行配置给定，不是今天的日期） › 进度计划；en `flow:check-both:planned`：Logical date ‹ 2026-08-13T00:00:00Z (set by the run configuration, not today's date) › Programme
- `L074` zh `flow:check-both:planned`：进度计划 ‹ 你的模型不带进度计划。规则集的规则写了阶段 Coordination，所以本次检查代填了这些阶段，没有到期日；结果页不显示到期、逾期或优先级。 › 几何；en `flow:check-both:planned`：Programme ‹ Your model brings no programme. The rule set's rules name the stages Coordination, so this check fills those s › Geometry
- `L075` zh `flow:check-both:result`：Building-Hvac.ifc（你声明的专业：暖通（HVAC）） ‹ 进度计划：规则集的阶段 Coordination 由本次检查代填，没有到期日；本页不显示到期、逾期或优先级。 › 不计算几何。没有形体的构件不会让整次检查中断，它的检查结果、标识和下一步照常显示；本次结果也没有 3D 视图。；en `flow:check-both:result`：Building-Hvac.ifc (discipline you declared: HVAC) ‹ Programme: the rule set's stages Coordination were filled in by this check, with no due date; this page shows  › No geometry is computed. An element without a shape does not stop the
- `L076` zh `flow:check-both:running`：运行检查 ‹ 正在检查，可能需要几十秒到几分钟。完成后会打开结果。 › 以前的检查；en `flow:check-both:running`：Run the check ‹ Checking. This may take from tens of seconds to a few minutes; the result opens when it is done. › Earlier checks

### T3 其余（52 条，待核 35）

#### ACTIONS（4 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E023 | `cross-model-alignment-not-confirmed.action` | This is not a known misalignment. No one has yet confirmed, by the method the project accepts, that the two models are aligned; do this once against the model versions l… | 这不是已知的错位。还没有人按项目接受的方法确认两侧模型对齐；需要针对所列模型版本做一次并记录 | 10/8 已核 | zh 24｜en 24｜其他示例 |
| E024 | `cross-model-alignment-not-confirmed.recheck` | The alignment confirmation has been done and reports the models aligned, naming the model versions | 对齐确认已做，结果为已对齐，写明模型版本 | 10/8 已核 | zh 14｜en 14｜其他示例 |
| E025 | `mep-element-not-spatially-assigned.action` | In the source model, place the element on its correct level (and, where the project requires spatial assignment, in its corresponding space), then re-export | 在源模型里把构件放到正确的标高上（项目要求空间归属时，再放进对应的空间），重新导出 | 10/8 后改句，需重核 | zh 0｜en 0｜（本次渲染未触发） |
| E029 | `opening-not-verifiably-linked.action` | In the receiving side's model, add to the opening a cross-reference back to the element that passes through it. Where several elements pass through one opening, each nee… | 在接收方模型里，给洞口补上指回穿过它的那个构件的关联。一个洞口供几个构件穿过，每个各要一条 | 10/8 已核；C 通道待裁（W1） | zh 0｜en 0｜（本次渲染未触发） |

#### ACTION_GROUPS（4 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E035 | `open.none` | The record gives no action for any item. | 记录没有为任何一个事项给出处理动作。 | 10/8 已核 | zh 2｜en 2｜其他示例 |
| E037 | `unplaced.label` | Items to check by hand | 需要人工核对的事项 | 10/8 已核 | zh 0｜en 12｜其他示例 |
| E038 | `unplaced.summary` | the record gives no current state; check by hand | 记录没有给出当前情况，需要人工核对 | 10/8 已核 | zh 12｜en 12｜其他示例 |
| E040 | `unplaced.note` | The record does not say what these items' conclusions are now. An element that is gone does not mean the problem was fixed. | 这些事项现在是什么判断，记录没有说。构件不在了不代表问题已修复。 | 10/8 已核 | zh 12｜en 12｜其他示例；复用 G001 |

#### ASPECT_NOTES（3 条，待核 3）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E045 | `onlyModelVersion` | Only the model version changed; that does not mean the check result's content changed. Nor does the record conclude whether this evidence can carry over to the new versi… | 只有模型版本变了，不等于检查结果的内容变了。记录也不就“这条证据能否沿用到新版本”下结论。 | 10/15 批，未核 | zh 21｜en 21｜其他示例 |
| E046 | `semanticsSameOutcome` | The check requirement was edited, and the check result reads the same as before — but it was reached under the edited requirement and cannot be treated as the same evide… | 检查要求被修改过，检查结果读起来和原来一样——但它是按修改后的要求得出的，不能当作同一条证据。 | 10/15 批，未核 | zh 3｜en 3｜其他示例 |
| E048 | `contentUnderSameRequirement` | The check requirement did not change, and the check result content did. This row does not record whether the result got better or worse; see the current conclusion. | 检查要求没有变，检查结果内容变了。这一行不记录结果是变好还是变差，请看当前判断。 | 10/15 批，未核 | zh 3｜en 3｜其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E045` zh `#/fixture/recheck-member-gone/recheck/5/0`：引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 ‹ 只有模型版本变了，不等于检查结果的内容变了。记录也不就“这条证据能否沿用到新版本”下结论。 › 追溯信息（记录原码与内容指纹）；en `#/fixture/recheck-member-gone/recheck/5/0`：The citation changed key (the new key is the "corresponding evidence t ‹ Only the model version changed; that does not mean the check result's content changed. Nor does the record con › Tracing (record codes and content fingerprints)
- `E046` zh `#/fixture/recheck-semantics-changed/recheck/7/0`：引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 ‹ 检查要求被修改过，检查结果读起来和原来一样——但它是按修改后的要求得出的，不能当作同一条证据。 › 追溯信息（记录原码与内容指纹）；en `#/fixture/recheck-semantics-changed/recheck/7/0`：The citation changed key (the new key is the "corresponding evidence t ‹ The check requirement was edited, and the check result reads the same as before — but it was reached under the › Tracing (record codes and content fingerprints)
- `E048` zh `#/fixture/recheck-producing-reissued-content-changed/recheck/7/0`：引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 ‹ 检查要求没有变，检查结果内容变了。这一行不记录结果是变好还是变差，请看当前判断。 › 追溯信息（记录原码与内容指纹）；en `#/fixture/recheck-producing-reissued-content-changed/recheck/7/0`：The citation changed key (the new key is the "corresponding evidence t ‹ The check requirement did not change, and the check result content did. This row does not record whether the r › Tracing (record codes and content fingerprints)

#### CARRY_OVER_STATES（4 条，待核 4）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E088 | `no-counterpart.meaning` | It can be compared, but this record cites no evidence corresponding to it. | 可以比较，但本次记录没有引用与它对应的证据。 | 10/15 批，未核 | zh 43｜en 43｜其他示例 |
| E089 | `no-counterpart.caveat` | No counterpart does not mean the problem was fixed. | 没有对应证据不代表问题已修复。 | 10/15 批，未核 | zh 43｜en 43｜其他示例 |
| E091 | `not-provable.meaning` | The comparison itself cannot be made, so it can be called neither unchanged nor changed. | 比较本身无法建立，所以既不能说一致，也不能说变了。 | 10/15 批，未核 | zh 16｜en 16｜其他示例 |
| E092 | `not-provable.caveat` | This is "cannot be compared", not "evidence missing", and not "no counterpart". | 这是“无法比较”，不是“证据缺失”，也不是“没有对应证据”。 | 10/15 批，未核 | zh 16｜en 16｜其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E088` zh `#/fixture/recheck-comparison`：“未找到对应证据”是什么意思 ‹ 可以比较，但本次记录没有引用与它对应的证据。没有对应证据不代表问题已修复。 › 追溯信息：记录标识、模型版本指纹、记录原码对照；en `#/fixture/recheck-comparison`：What "No counterpart found" means ‹ It can be compared, but this record cites no evidence corresponding to it. No counterpart does not mean the pr › Tracing: record identity, model version fingerprints, record codes
- `E089` zh `#/fixture/recheck-comparison`：“未找到对应证据”是什么意思 ‹ 可以比较，但本次记录没有引用与它对应的证据。没有对应证据不代表问题已修复。 › 追溯信息：记录标识、模型版本指纹、记录原码对照；en `#/fixture/recheck-comparison`：What "No counterpart found" means ‹ It can be compared, but this record cites no evidence corresponding to it. No counterpart does not mean the pr › Tracing: record identity, model version fingerprints, record codes
- `E091` zh `#/fixture/recheck-member-gone`：“现有依据不足以比较”是什么意思 ‹ 比较本身无法建立，所以既不能说一致，也不能说变了。这是“无法比较”，不是“证据缺失”，也不是“没有对应证据”。 › 追溯信息：记录标识、模型版本指纹、记录原码对照；en `#/fixture/recheck-member-gone`：What "Not enough basis to compare" means ‹ The comparison itself cannot be made, so it can be called neither unchanged nor changed. This is "cannot be co › Tracing: record identity, model version fingerprints, record codes
- `E092` zh `#/fixture/recheck-member-gone`：“现有依据不足以比较”是什么意思 ‹ 比较本身无法建立，所以既不能说一致，也不能说变了。这是“无法比较”，不是“证据缺失”，也不是“没有对应证据”。 › 追溯信息：记录标识、模型版本指纹、记录原码对照；en `#/fixture/recheck-member-gone`：What "Not enough basis to compare" means ‹ The comparison itself cannot be made, so it can be called neither unchanged nor changed. This is "cannot be co › Tracing: record identity, model version fingerprints, record codes

#### CONDITION_ENTRIES（2 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E118 | `not-comparable.plain` | No conclusion can be drawn on the original recheck condition: some of the original elements are no longer in this record, so the condition has no complete subject to che… | 无法对原复检条件下结论：原来的构件有的已经不在本次记录里，条件没有完整的对象可以检查。这不代表条件已满足。 | 10/8 已核 | zh 9｜en 9｜其他示例 |
| N01 | `no-recheck-condition.plainNotReady` | The original record gave no recheck condition. | 原记录没有给出复检条件。 | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |

#### CONSEQUENCE_KINDS（1 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E128 | `rework-risk` | Risk of rework | 有返工风险 | 10/8 已核 | zh 14｜en 14｜其他示例 |

#### DISPOSITION_ENTRIES（2 条，待核 2）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E157 | `element-deleted-in-reissued-model.next` | The record gives no next step for a deleted element. Check in the source model whether this deletion was an intended design change; this preview cannot record that confi… | 记录没有为已删除的构件给出下一步。请在源模型里核对这次删除是不是有意的设计变更；本预览不能记录这种确认。 | 10/15 批，未核 | zh 3｜en 3｜其他示例 |
| E161 | `pairing-no-longer-derived.next` | The record gives no next step for this pair. Check whether the basis that stopped them being paired (see "the reason the record gives") is a conclusion you accept; the o… | 记录没有为这一对构件给出下一步。请核对让它不再被配对的那份依据（见“记录给出的原因”）是不是你认可的结论；原来的问题没有被证明已修复。 | 10/15 批，未核 | zh 11｜en 11｜其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E157` zh `#/fixture/recheck-member-gone/recheck/0/0`：二、要做什么、由谁处理、完成后拿什么复检 ‹ 记录没有为已删除的构件给出下一步。请在源模型里核对这次删除是不是有意的设计变更；本预览不能记录这种确认。 › 记录没有给出这一项的当前情况，所以本页没有处理动作、处理团队或默认处理角色可以显示。复检前记录里的这些信息也没有随复检记录返回。；en `#/fixture/recheck-member-gone/recheck/0/0`：2. What to do, who deals with it, what a recheck must show ‹ The record gives no next step for a deleted element. Check in the source model whether this deletion was an in › The record does not give this item's current place, so this page has n
- `E161` zh `#/fixture/recheck-comparison/recheck/0/0`：二、要做什么、由谁处理、完成后拿什么复检 ‹ 记录没有为这一对构件给出下一步。请核对让它不再被配对的那份依据（见“记录给出的原因”）是不是你认可的结论；原来的问题没有被证明已修复。 › 记录没有给出这一项的当前情况，所以本页没有处理动作、处理团队或默认处理角色可以显示。复检前记录里的这些信息也没有随复检记录返回。；en `#/fixture/recheck-comparison/recheck/0/0`：2. What to do, who deals with it, what a recheck must show ‹ The record gives no next step for this pair. Check whether the basis that stopped them being paired (see "the  › The record does not give this item's current place, so this page has n

#### HOME（4 条，待核 4）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E185 | `status` | This is an example preview: a Revit file itself (.rvt) cannot be imported, and it gives no overall compliance or ready-to-build conclusion. | 当前为示例预览：Revit 文件本身（.rvt）不能导入，也不提供整体合规或可施工结论。 | 10/8 后改句，需重核 | zh 0｜en 0｜（本次渲染未触发） |
| E186 | `statusWithWorkspace` | Two things are offered here: a real check already run in the workspace named when the server was started, and simulated examples. The workspace check cannot have its mod… | 当前同时提供两样：启动服务器时指定的工作区里一次已经跑完的真实检查，以及模拟示例。工作区里的检查不能在页面上选择或更换模型；Revit 文件本身不能导入，也不提供整体合规或可施工结论。 | 10/8 后改句，需重核 | zh 0｜en 0｜（本次渲染未触发） |
| E187 | `statusWorkspaceUnknown` | Could not confirm whether the server was started with a workspace, so there is no entry to a real check here; that does not mean there is no workspace — the error is bel… | 未能确认服务器是否指定了工作区，所以这里没有真实检查的入口；这不等于没有工作区，错误原文在下面。模拟示例照常可看。Revit 文件本身不能导入，也不提供整体合规或可施工结论。 | 10/8 后改句，需重核 | zh 0｜en 0｜（本次渲染未触发） |
| E194 | `cannot[0]` | Import a Revit file itself (.rvt), or choose or change the model in the example and workspace entries | 导入 Revit 文件本身（.rvt），或在示例和工作区入口里选择、更换模型 | 10/8 后改句，需重核 | zh 0｜en 0｜（本次渲染未触发） |

#### LEAF_READINGS（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E211 | `cross-model-alignment/not-yet-confirmed` | No alignment confirmation yet | 还没有对齐确认 | B 层，10/8 未核 | zh 14｜en 14｜其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E211` zh `#/fixture/recheck-member-gone/recheck/5/0`：这个结论依据的结果 ‹ 还没有对齐确认 › 模型；en `#/fixture/recheck-member-gone/recheck/5/0`：The result this conclusion rests on ‹ No alignment confirmation yet › Models

#### LEAF_READING_WORDS（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E220 | `notCarried` | The record does not give the result this item now rests on | 记录没有给出这一项现在依据的结果 | B 层，10/8 未核 | zh 14｜en 14｜其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E220` zh `#/fixture/recheck-comparison/recheck/0/0`：这个结论依据的结果 ‹ 记录没有给出这一项现在依据的结果 › 这个事项现在；en `#/fixture/recheck-comparison/recheck/0/0`：The result this conclusion rests on ‹ The record does not give the result this item now rests on › This item now

#### RECHECK_ITEM（2 条，待核 2）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E282 | `pairNote` | These two elements are no longer paired for checking: the penetration determination is now "no penetration" (see the reason the record gives below). This does not mean t… | 这两个构件已不再被配成一对检查：穿透判定现为“不穿透”（见下方记录给出的原因）。这不等于开洞已建成，也不等于开洞缺陷已修复。 | B 层，10/8 未核 | zh 11｜en 11｜其他示例 |
| E287 | `noCurrent` | The record does not give this item's current place, so this page has no action, handling team or default handling role to show. Those details from the record before the… | 记录没有给出这一项的当前情况，所以本页没有处理动作、处理团队或默认处理角色可以显示。复检前记录里的这些信息也没有随复检记录返回。 | B 层，10/8 未核 | zh 14｜en 14｜其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E282` zh `#/fixture/recheck-comparison/recheck/0/0`：土建预留开洞：复检前 受阻；现在：记录没有给出 ‹ 这两个构件已不再被配成一对检查：穿透判定现为“不穿透”（见下方记录给出的原因）。这不等于开洞已建成，也不等于开洞缺陷已修复。 › 这个结论依据的结果；en `#/fixture/recheck-comparison/recheck/0/0`：Builder's-work openings: before the recheck Blocked; now: not given in ‹ These two elements are no longer paired for checking: the penetration determination is now "no penetration" (s › The result this conclusion rests on
- `E287` zh `#/fixture/recheck-comparison/recheck/0/0`：记录没有为这一对构件给出下一步。请核对让它不再被配对的那份依据（见“记录给出的原因”）是不是你认可的结论；原来的问题没有被证明已修复。 ‹ 记录没有给出这一项的当前情况，所以本页没有处理动作、处理团队或默认处理角色可以显示。复检前记录里的这些信息也没有随复检记录返回。 › 三、是哪两个构件；en `#/fixture/recheck-comparison/recheck/0/0`：The record gives no next step for this pair. Check whether the basis t ‹ The record does not give this item's current place, so this page has no action, handling team or default handl › 3. Which two elements

#### REISSUE_CASES（12 条，待核 12）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E329 | `producing.headline` | The handing-over side's model was re-issued; the receiving side's model did not change | 交出方的模型重新发布了，接收方的模型没有变 | 10/15 批，未核 | zh 45｜en 45｜其他示例 |
| E330 | `producing.detail` | The handing-over side's ({from}) model {producing} is a new version; the receiving side's ({to}) model {consuming} is the original version. | 交出方（{from}）的模型 {producing} 是新版本；接收方（{to}）的模型 {consuming} 还是原版本。 | 10/15 批，未核 | zh 6｜en 6｜其他示例 |
| E331 | `producing.caveats[0]` | Re-issuing on the handing-over side may have changed what passes through what, or which elements are involved; it cannot be taken to mean the receiving side's work (for… | 交出方重新发布可能改变了穿越关系或涉及的构件范围，不能据此说接收方的工作（例如开洞）已经做好。 | 10/15 批，未核 | zh 6｜en 6｜其他示例 |
| E332 | `producing.caveats[1]` | A determination made against an old version cannot be attributed to the new one. | 针对旧版本作出的判定不能归到新版本。 | 10/15 批，未核 | zh 8｜en 6｜其他示例 |
| E333 | `consuming.headline` | The receiving side's model was re-issued; the handing-over side's model did not change | 接收方的模型重新发布了，交出方的模型没有变 | 10/15 批，未核 | zh 15｜en 15｜其他示例 |
| E334 | `consuming.detail` | The receiving side's ({to}) model {consuming} is a new version; the handing-over side's ({from}) model {producing} is the original version. | 接收方（{to}）的模型 {consuming} 是新版本；交出方（{from}）的模型 {producing} 还是原版本。 | 10/15 批，未核 | zh 2｜en 2｜其他示例 |
| E335 | `consuming.caveats[0]` | Re-issuing on the receiving side may be the way to a fix, but it does not mean the fix has happened (for example that the opening is complete). | 接收方重新发布可能是修复的途径，但不代表修复已经发生（例如洞口已完成）。 | 10/15 批，未核 | zh 2｜en 2｜其他示例 |
| E336 | `consuming.caveats[1]` | Likewise, a determination made against an old version cannot be attributed to the new one. | 针对旧版本作出的判定同样不能归到新版本。 | 10/15 批，未核 | zh 2｜en 2｜其他示例 |
| E337 | `both.headline` | Both the handing-over and the receiving side's models were re-issued | 交出方和接收方的模型都重新发布了 | 10/15 批，未核 | zh 15｜en 15｜其他示例 |
| E338 | `both.detail` | The handing-over side's ({from}) model {producing} and the receiving side's ({to}) model {consuming} are both new versions. | 交出方（{from}）的模型 {producing} 和接收方（{to}）的模型 {consuming} 都是新版本。 | 10/15 批，未核 | zh 2｜en 2｜其他示例 |
| E339 | `both.caveats[0]` | Both sides changed at once: this page attributes no change in any evidence to either side. | 两侧同时变化：本页不把任何一条证据的变化归到某一侧。 | 10/15 批，未核 | zh 2｜en 2｜其他示例 |
| E340 | `both.caveats[1]` | A re-issue does not mean a fix has happened; a determination made against an old version cannot be attributed to the new one. | 重新发布不代表修复已经发生；针对旧版本作出的判定不能归到新版本。 | 10/15 批，未核 | zh 2｜en 2｜其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E329` zh `#/fixture/recheck-member-gone`：5 个事项：记录没有给出当前情况，需要人工核对 ‹ 模型：交出方的模型重新发布了，接收方的模型没有变。 › 交出方重新发布可能改变了穿越关系或涉及的构件范围，不能据此说接收方的工作（例如开洞）已经做好。；en `#/fixture/recheck-member-gone`：5 items: the record gives no current state; check by hand ‹ Models: The handing-over side's model was re-issued; the receiving side's model did not change. › Re-issuing on the handing-over side may have changed what passes throu
- `E330` zh `#/fixture/recheck-member-gone`：交出方的模型重新发布了，接收方的模型没有变 ‹ 交出方（MEP）的模型 hvac 是新版本；接收方（Architecture）的模型 architecture 还是原版本。 › 交接的哪一侧；en `#/fixture/recheck-member-gone`：The handing-over side's model was re-issued; the receiving side's mode ‹ The handing-over side's (MEP) model hvac is a new version; the receiving side's (Architecture) model architect › Side of the handover
- `E331` zh `#/fixture/recheck-member-gone`：模型：交出方的模型重新发布了，接收方的模型没有变。 ‹ 交出方重新发布可能改变了穿越关系或涉及的构件范围，不能据此说接收方的工作（例如开洞）已经做好。 › 针对旧版本作出的判定不能归到新版本。；en `#/fixture/recheck-member-gone`：Models: The handing-over side's model was re-issued; the receiving sid ‹ Re-issuing on the handing-over side may have changed what passes through what, or which elements are involved; › A determination made against an old version cannot be attributed to th
- `E332` zh `#/fixture/recheck-member-gone`：交出方重新发布可能改变了穿越关系或涉及的构件范围，不能据此说接收方的工作（例如开洞）已经做好。 ‹ 针对旧版本作出的判定不能归到新版本。 › 2 个事项的结论和复检前不同：；en `#/fixture/recheck-member-gone`：Re-issuing on the handing-over side may have changed what passes throu ‹ A determination made against an old version cannot be attributed to the new one. › 2 items' conclusions differ from before the recheck:
- `E333` zh `#/fixture/recheck-consuming-reissued`：2 个事项：记录没有给出当前情况，需要人工核对 ‹ 模型：接收方的模型重新发布了，交出方的模型没有变。 › 接收方重新发布可能是修复的途径，但不代表修复已经发生（例如洞口已完成）。；en `#/fixture/recheck-consuming-reissued`：2 items: the record gives no current state; check by hand ‹ Models: The receiving side's model was re-issued; the handing-over side's model did not change. › Re-issuing on the receiving side may be the way to a fix, but it does
- `E334` zh `#/fixture/recheck-consuming-reissued`：接收方的模型重新发布了，交出方的模型没有变 ‹ 接收方（Architecture）的模型 architecture 是新版本；交出方（MEP）的模型 hvac 还是原版本。 › 交接的哪一侧；en `#/fixture/recheck-consuming-reissued`：The receiving side's model was re-issued; the handing-over side's mode ‹ The receiving side's (Architecture) model architecture is a new version; the handing-over side's (MEP) model h › Side of the handover
- `E335` zh `#/fixture/recheck-consuming-reissued`：模型：接收方的模型重新发布了，交出方的模型没有变。 ‹ 接收方重新发布可能是修复的途径，但不代表修复已经发生（例如洞口已完成）。 › 针对旧版本作出的判定同样不能归到新版本。；en `#/fixture/recheck-consuming-reissued`：Models: The receiving side's model was re-issued; the handing-over sid ‹ Re-issuing on the receiving side may be the way to a fix, but it does not mean the fix has happened (for examp › Likewise, a determination made against an old version cannot be attrib
- `E336` zh `#/fixture/recheck-consuming-reissued`：接收方重新发布可能是修复的途径，但不代表修复已经发生（例如洞口已完成）。 ‹ 针对旧版本作出的判定同样不能归到新版本。 › 4 个事项的结论和复检前不同：；en `#/fixture/recheck-consuming-reissued`：Re-issuing on the receiving side may be the way to a fix, but it does  ‹ Likewise, a determination made against an old version cannot be attributed to the new one. › 4 items' conclusions differ from before the recheck:
- `E337` zh `#/fixture/recheck-both-reissued`：2 个事项：记录没有给出当前情况，需要人工核对 ‹ 模型：交出方和接收方的模型都重新发布了。 › 两侧同时变化：本页不把任何一条证据的变化归到某一侧。；en `#/fixture/recheck-both-reissued`：2 items: the record gives no current state; check by hand ‹ Models: Both the handing-over and the receiving side's models were re-issued. › Both sides changed at once: this page attributes no change in any evid
- `E338` zh `#/fixture/recheck-both-reissued`：交出方和接收方的模型都重新发布了 ‹ 交出方（MEP）的模型 hvac 和接收方（Architecture）的模型 architecture 都是新版本。 › 交接的哪一侧；en `#/fixture/recheck-both-reissued`：Both the handing-over and the receiving side's models were re-issued ‹ The handing-over side's (MEP) model hvac and the receiving side's (Architecture) model architecture are both n › Side of the handover
- `E339` zh `#/fixture/recheck-both-reissued`：模型：交出方和接收方的模型都重新发布了。 ‹ 两侧同时变化：本页不把任何一条证据的变化归到某一侧。 › 重新发布不代表修复已经发生；针对旧版本作出的判定不能归到新版本。；en `#/fixture/recheck-both-reissued`：Models: Both the handing-over and the receiving side's models were re- ‹ Both sides changed at once: this page attributes no change in any evidence to either side. › A re-issue does not mean a fix has happened; a determination made agai
- `E340` zh `#/fixture/recheck-both-reissued`：两侧同时变化：本页不把任何一条证据的变化归到某一侧。 ‹ 重新发布不代表修复已经发生；针对旧版本作出的判定不能归到新版本。 › 4 个事项的结论和复检前不同：；en `#/fixture/recheck-both-reissued`：Both sides changed at once: this page attributes no change in any evid ‹ A re-issue does not mean a fix has happened; a determination made against an old version cannot be attributed  › 4 items' conclusions differ from before the recheck:

#### RESOLUTION_KINDS（1 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E350 | `cross-model-alignment-not-confirmed` | Not a known misalignment: nobody has confirmed yet that the two models are aligned | 不是已知的错位：还没有人确认两侧模型对齐 | 10/8 已核 | zh 14｜en 14｜其他示例 |

#### VERDICT_GROUPS（4 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E401 | `changed.none` | No conclusion changed. | 没有判断变了的项。 | 10/8 已核 | zh 8｜en 8｜其他示例 |
| E403 | `changed.notes.reissued` | A model was re-issued. A changed conclusion does not say what became of the original problem; each item's old evidence says what changed. | 模型重新发布过。判断变了，不说明原来的问题怎样了；每一项的旧证据写明变了的是什么。 | 10/8 已核 | zh 31｜en 31｜其他示例 |
| E404 | `changed.notes.unrecognised` | A changed conclusion does not say what became of the original problem; each item's old evidence says what changed. | 判断变了，不说明原来的问题怎样了；每一项的旧证据写明变了的是什么。 | 10/8 已核 | zh 31｜en 31｜其他示例 |
| E407 | `unplaced.note` | The record does not say what these items' conclusions are now. An element that is gone does not mean the problem was fixed. | 这些项现在是什么判断，记录没有说。构件不在了不代表问题已修复。 | 10/8 已核 | zh 0｜en 12｜其他示例；复用 G001 |

#### EVIDENCE（2 条，待核 2）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E594 | `dispositionNow` | This item now | 这个事项现在 | B 层，10/8 未核 | zh 26｜en 26｜其他示例 |
| E595 | `reissued` | Re-issued (new version) | 重新发布了（新版本） | B 层，10/8 未核 | zh 10｜en 10｜其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E594` zh `#/fixture/recheck-comparison`：土建预留开洞：复检前 受阻；现在：记录没有给出 ‹ 这个事项现在 › 这两个构件现在不再被配成一对来检查，不等于开洞已补；en `#/fixture/recheck-comparison`：Builder's-work openings: before the recheck Blocked; now: not given in ‹ This item now › These two elements are no longer paired for checking; that does not me
- `E595` zh `#/fixture/recheck-member-gone`：hvac ‹ 重新发布了（新版本） › 接收方；en `#/fixture/recheck-member-gone`：hvac ‹ Re-issued (new version) › Receiving side

#### WORK（1 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| E602 | `missing` | {work}: before the recheck {before}; now: not given in the record | {work}：复检前 {before}；现在：记录没有给出 | B 层，10/8 未核 | zh 26｜en 26｜其他示例 |

页面上下文（只列待核的条目；前后各一块，‹ › 里是匹配到的那一块）：

- `E602` zh `#/fixture/recheck-comparison`：house - roof：屋顶 IfcRoof · 模型中没有楼层归属 · 模型 architecture ‹ 土建预留开洞：复检前 受阻；现在：记录没有给出 › 这个事项现在；en `#/fixture/recheck-comparison`：house - roof: IfcRoof (IFC class) · No storey assignment in the model  ‹ Builder's-work openings: before the recheck Blocked; now: not given in the record › This item now

#### SOURCE_SUMMARY（3 条，待核 1）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| Q03 | `citesNone` | This record's conclusions cite no evidence. | 这份记录的结论没有引用证据。 | 新增，未核 | zh 0｜en 0｜（本次渲染未触发） |
| Q09 | `join` | , | 、 | 分隔符，无需判断 | zh 0｜en 0｜（本次渲染未触发）；复用 G054 |
| Q10 | `lastJoin` | and | 、 | 分隔符，无需判断 | zh 0｜en 0｜（本次渲染未触发）；复用 G054 |

#### IFC_CLASS_NAMES（1 条，待核 0）

| ID | 键 | English | 中文 | 状态 | 页面 |
|---|---|---|---|---|---|
| Z09 | `IfcWall` |  | 墙 | D6 未列，是否已核待确认 | zh 0｜en 0｜（本次渲染未触发） |

## 8. 不进子集的条目（X）

D6 索引里的条目，在公开路线上渲染不到，也没有被本地结果页的代码引用。CSV 里 `tier` = X，`x_reason` 写了原因。

| 表 | 条目 | 待核口径 | 原因 |
|---|---:|---:|---|
| ACTION | 1 | 1 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| ACTIONS | 6 | 0 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| ACTION_GROUPS | 2 | 0 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| ASPECT_NOTES | 2 | 2 | 公开路线上的代码不引用它 |
| BASIS_WORDS | 2 | 0 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| BESIDE | 1 | 0 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| CITATION_PROVENANCE | 4 | 0 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| CONDITION_ENTRIES | 1 | 0 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| CONTEXT | 1 | 0 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| DETAILS_WORDS | 1 | 0 | 公开路线上的代码不引用它 |
| DETAILS_WORDS | 2 | 0 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| DISPOSITION_ENTRIES | 3 | 3 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| ELEMENT_WORDS | 1 | 1 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| KEY_CHANGED | 1 | 1 | 公开路线上的代码不引用它 |
| LANGUAGE | 1 | 1 | 公开路线上的代码不引用它 |
| LEAF_READINGS | 6 | 5 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| LEAF_READING_WORDS | 1 | 1 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| MODE_LABELS | 1 | 1 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| RECHECK | 3 | 3 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| RECHECK_ITEM | 2 | 2 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| REFUSAL_UNGLOSSED | 1 | 1 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| REISSUE_CASES | 2 | 2 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| RESOLUTION_KINDS | 4 | 0 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| VERDICT_GROUPS | 6 | 0 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| WORKSPACE | 2 | 0 | 公开路线上的代码不引用它 |
| WORKSPACE | 1 | 0 | 只在工作区的对比页或拒绝页（C2 专用）出现，不在公开路线上 |
| WORKSPACE | 4 | 0 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| WORKSPACE_COMPARE | 2 | 2 | 公开路线上的代码不引用它 |
| WORKSPACE_COMPARE | 32 | 32 | 只在工作区的对比页或拒绝页（C2 专用）出现，不在公开路线上 |
| WORKSPACE_HOME | 2 | 2 | 公开路线上的代码不引用它 |
| WORKSPACE_HOME | 1 | 1 | 示例页的代码能到达，但随附的 12 份示例记录都没有触发 |
| WORKSPACE_REFUSAL | 9 | 0 | 只在工作区的对比页或拒绝页（C2 专用）出现，不在公开路线上 |
| WORKSPACE_REFUSAL_REASONS | 9 | 0 | 只在工作区的对比页或拒绝页（C2 专用）出现，不在公开路线上 |

## 9. 方法与复现

1. 词表：用 `tests/test_doctor_english.py` 里同一套 Node 驱动，把 `doctor/static` 里所有登记的词表（中英）导出，按 `表.键`（数组 `[i]`、单复数 `.one`/`.other`）展平。在 `d59dee0` 上这样展平的结果与 D6 索引的 605 行逐键、逐字一致，所以条目 ID 沿用 D6 的 `E###`。`2e6eafc` 相对 `d59dee0` 的差别：新增 `LOCAL_CHECK` 146 条（其中领域含义 76 条，按[对照表](2026-10-08-doctor-local-check-bilingual-parity.md)第一至九节取，另 70 条界面用语不列入）、`SOURCE_SUMMARY` 11 条、`DIRECTORY.exampleIntro` 1 条、`CONDITION_ENTRIES.no-recheck-condition.plainNotReady` 1 条、`HOME.recommended` 1 条；改句 16 条（#29 的 6 条中央句子，#50 的 10 条）；没有删去的。
2. 页面：见第 3 节。每页读出文字块和短元素文本，匹配方法见第 6 节。
3. 档次：T1＝出现在首页、目录、示例主线页，或出现在本地结果页但不属于 `LOCAL_CHECK` 表（结果页复用工作区的结果画面，C2 走查看的也是这些画面）；T2＝其余出现在本地检查页或第二入口页上的，以及 `LOCAL_CHECK` 表里在首页以外的；T3＝其余只出现在其他示例、次要明细页上的，加条件出现的句子。
4. 条件出现：本次没渲染到的条目，若本地结果页的代码（经调用图）能引用到它所在的表和键，就按条件出现收进子集；只被示例页引用、而随附 12 份记录都没有触发的，不进子集。
5. 状态（每条恰好一个）：
   - **10/8 已核**：D6 的 A 层（299 条，BIM 10/8 已核完）且句子自 `d59dee0` 起没变。不再审。
   - **10/8 后改句，需重核**：10/8 已核或已列入 D6 的条目，句子在 10/8 之后改过（#29 的 6 条中央句子、#50 的 10 条）或显示条件改了（W4）。**待核**。
   - **10/8 已核；C 通道待裁**：W1 的两条，本轮不改。不再审。
   - **新增，未核**：#29（`L###`）、#48（`Q##`）、#50（`N01`）、#52（`H01`）新增的句子。**待核**。
   - **B 层，10/8 未核**、**10/15 批，未核**：D6 里原本排在 10/8 之后的条目，在公开页上出现，所以收进来。**待核**。
   - **同句已核**：句子与某条 10/8 已核且未改的条目中英都逐字相同。不再审。
   - **分隔符，无需判断**：Q2 的列举分隔符 `join`／`lastJoin`。
   - **D6 未列，待 BIM 确认**：三张中文单语释义表里 D6 没逐条列的条目。**不计入待核**，单列。
   - **其他**：不属于以上任何一种的（本次为 0）。
   **待核** ＝ 改句需重核 ＋ 新增未核 ＋ B 层未核 ＋ 10/15 批未核 ＋ 其他。
6. 生成的是这份清单，不是复核；渲染用的服务器、临时检查目录和浏览器配置都在会话临时目录，没有写进检出目录。
7. 生成清单用的脚本（词表导出、页面遍历、本地检查逐状态走查、匹配与分档）没有提交进仓库：它们是为这次清单写的会话工具。main 变动后要重新生成时，请 TD 说一声，我整理脚本后另开 PR，不在这个 PR 里加代码。
