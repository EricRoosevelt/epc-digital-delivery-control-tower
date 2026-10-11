# README screenshot: one item page, Chinese interface

One capture of the BIM Doctor local preview, in the Chinese interface, shown by the root
[`README.md`](../../../README.md) under *What you will see*, step 3. It is an illustration of what
the interface looked like. It is not acceptance evidence for the preview, and nothing validates
it: no manifest or test pins this directory.

| File | Route | Shows |
|---|---|---|
| `item-blocked-zh.png` | `#/fixture/member-evidence/item/2/2/0` | One item of the simulated first-check example, from the banner at the top of the page to the end of part 四: the banner (a bundled example with simulated project settings, not your model), the back link and the item's name, 一、结论 (the conclusion, its basis and the situation), 二、下一步 (what to do, the handling team, the default handling role, what it means for the work, what a recheck must show), 三、是哪个构件 (the element) and 四、具体缺什么 (the requirements that were not met, with the rule's own words) |

```text
55e4d1ba842301917c22740508f681350a8848bd7ff096cd362e8e87371b7302  item-blocked-zh.png
```

1760 x 3916 pixels.

## What is in the pixels

- **Public sample data only.** The example reads the two bundled buildingSMART PCERT sample
  models of the `pcert-sample` project (see *Data Source and Attribution* in the root README).
  The server was started without a workspace, so the page offered no workspace entry.
- **Simulated content is marked in the image.** The banner at the top says it is a bundled example
  with simulated project settings, not your model, and that each conclusion's "Basis" line says where
  its evidence comes from. The handling team carries the label 示例处理团队 (example handling team)
  and the page says the team is an entry in the record and does not mean anything has been assigned.
  The conclusion's basis reads "real check output": the check results behind this item come from a
  real run of the shipped rules on the sample models.
- **No private material.** Nothing from the controlled real case, its models or its workspace
  appears, and no local path, account or address is visible. The PNG carries no text or time
  metadata chunks (IHDR, IDAT, IEND only).

## Why this crop, and what is outside it

The rule for putting a screenshot in the public README is that every visible text block is either
a sentence or label BIM passed **as it reads now**, or data from the model or the record. The crop
is the longest stretch of this page for which that holds. It starts at the banner and ends at the
bottom edge of part 四.

Outside it, because no BIM verdict covers them:

- **Above:** the context bar (the 模拟示例 tag, `项目 pcert-sample`, `交接：MEP → Architecture · Coordination`,
  `返回首页`), the language switch (`当前：中文`) and the skip link. BIM's verdicts cover the tag's
  sentence but not the project, handover and home entries (`CONTEXT.project`, `CONTEXT.handover`,
  `CONTEXT.home`) or `LANGUAGE.current`, and the bar is one row, so it is cut off whole. The banner
  below it, which carries the "simulated" statement, is inside the image.
- **Below:** the heading and link "然后：这一项复检后的变化", the folded "依据逐条", "如何阅读这一页" and
  "追溯信息" summaries and the second back link (`ITEM.nextHeading`, `ITEM.nextLink`,
  `ITEM.basisSummary`, `HOW_TO_READ`, `ITEM.traceSummary`).

## Sentence by sentence

The table lists every text block in the image, top to bottom (74). *Id* is the index id in
[`2026-10-09-bim-review-subset-public-route.csv`](../../product/2026-10-09-bim-review-subset-public-route.csv)
or in BIM's verdict files, which are
[`2026-10-09-bim-review-t1-verdicts.csv`](../../product/2026-10-09-bim-review-t1-verdicts.csv),
[`2026-10-09-bim-review-t2-verdicts.csv`](../../product/2026-10-09-bim-review-t2-verdicts.csv),
[`2026-10-10-bim-review-56-57-verdicts.csv`](../../product/2026-10-10-bim-review-56-57-verdicts.csv)
(BIM's review of PR #56 and #57) and
[`2026-10-10-bim-review-item-frame-verdicts.csv`](../../product/2026-10-10-bim-review-item-frame-verdicts.csv)
(BIM's review of the item page's frame wording). Rows from the last file have no index id, so they
show the wording table and key instead (for example `ITEM.back`). "10/8, same sentence" means BIM's
10/8 review of the first-check path, and the sentence is byte-identical today. A sentence that
changed after the T1 review rests on the #56/#57 file instead: 情况 (E587), 二、下一步 (E582),
跳到下一步 and the banner sentence (U2).

| # | On the image | Id | Kind | Basis |
|---:|---|---|---|---|
| 1 | 随附示例，含模拟的项目设定，不是你的模型；证据来源逐条标在各结论的“依据”一行。 来源说明 | U2, Q11 | 界面用语 | BIM #56/#57复核：通过；BIM T1 复核：通过 |
| 2 | ← 返回事项列表（回到这一项的位置） | ITEM.back | 界面用语 | BIM 页面框架用语复核：通过 |
| 3 | 首次检查事项 · 一个构件 | ITEM.kicker | 界面用语 | BIM 页面框架用语复核：通过 |
| 4 | chimney cover | — | model data | 构件名称，取自样例模型（不是界面用语） |
| 5 | 跳到下一步 | U2 | 界面用语 | BIM #56/#57复核：通过 |
| 6 | 一、结论 | ITEM.conclusion | 界面用语 | BIM 页面框架用语复核：通过 |
| 7 | 房间数据表与设备明细表：受阻 | E008, E005 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 8 | 这个结论的依据：真实检查输出 ×2 | E100, E052 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 9 | 情况 | E587 | 界面用语 | BIM #56/#57复核：通过 |
| 10 | 缺少本项目约定的资产标识 | E345 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 11 | 这个结论依据的结果 | E219 | 界面用语 | BIM T1 复核：通过 |
| 12 | 项目资产标识的要求没有满足 | E204 | 界面用语 | BIM T1 复核：通过 |
| 13 | 二、下一步 | E582 | 界面用语 | BIM #56/#57复核：通过 |
| 14 | 要做什么 | E573 | 界面用语 | BIM T1 复核：通过 |
| 15 | 在源模型里给这个构件补上本项目约定的资产标识属性（见所列属性集和属性名），重新导出 | E013 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 16 | 处理团队 | E584 | 界面用语 | BIM T1 复核：通过 |
| 17 | coordination-team 示例处理团队 | E063 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 18 | 处理团队是记录里的安排，不代表已经派发。 | E062 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 19 | 默认处理角色（规则给出的默认，不是指派） | E065 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 20 | model-coordination | — | record data | 默认处理角色的代码，来自记录（不是界面用语） |
| 21 | 对这项工作的后果 | E575 | 界面用语 | BIM T1 复核：通过 |
| 22 | 这项工作不能开始 | E126 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 23 | 有重新标识的风险：引用这些标识的文件届时也须重新出具 | E129 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 24 | 完成后拿什么复检 | E576 | 界面用语 | BIM T1 复核：通过 |
| 25 | 重新发布的模型上，这个构件在所列每条要求下都通过 | E014 | 界面用语 | BIM T1 复核：通过 |
| 26 | 来源原文（英文，记录所带）：供追溯，不是操作指令 | E577 | 界面用语 | BIM T1 复核：通过 |
| 27 | 这项工作需要什么 | E579 | 界面用语 | BIM T1 复核：通过 |
| 28 | 要每件设备都带有项目的资产标识，明细表才能按它编排。 | E006 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 29 | 三、是哪个构件 | E285 | 界面用语 | BIM T1 复核：通过 |
| 30 | chimney cover | — | model data | 构件名称，取自样例模型（不是界面用语） |
| 31 | 类别 | E444 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 32 | 风口 IfcAirTerminal | — | gloss + model data | “风口”是界面给 IFC 类别的中文名（IFC_CLASS_NAMES.IfcAirTerminal，BIM T1 复核：通过）；“IfcAirTerminal”是模型里的类别名 |
| 33 | 楼层 | ELEMENT_CARD.storey | 界面用语 | BIM 页面框架用语复核：通过 |
| 34 | 00 groundfloor | — | model data | 楼层，取自 IFC 的空间归属（不是界面用语） |
| 35 | 所属模型 | E489 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 36 | hvac：本次交接中交出方的模型 | — | model data + 界面用语 | “hvac”是模型标识（数据）；“本次交接中交出方的模型”是 HANDOVER_SIDES.producing，E181，BIM 10/8 复核，同句 |
| 37 | 这是模型标识，不是专业声明 | E168 | 界面用语 | BIM T1 复核：通过 |
| 38 | 专业 | ELEMENT_CARD.disciplineRow | 界面用语 | BIM 页面框架用语复核：通过 |
| 39 | 记录未提供专业信息；本界面不从模型标识推断专业 | E167 | 界面用语 | BIM T1 复核：通过 |
| 40 | GlobalId | E491 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 41 | 23uPJWDfXEcwHH3kdFgV9c复制 | — | model data + 界面用语 | GlobalId 的值取自模型（数据）；“复制”是 COPY.button，BIM 页面框架复核：通过 |
| 42 | 追溯用内部键 | E483 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 43 | hvac::23uPJWDfXEcwHH3kdFgV9c | — | record data | 内部键 = 模型标识 :: GlobalId，取自记录 |
| 44 | 名称取自模型文件本身，可能为空，也可能与别的构件重名；要在模型里定位，请用 GlobalId。 | E170 | 界面用语 | BIM T1 复核：通过 |
| 45 | 四、具体缺什么 | — | 界面用语 | ITEM.details（“四、{heading}”）BIM 页面框架复核：通过；“具体缺什么”是 DETAILS_WORDS.heading，BIM 10/8 复核，同句 |
| 46 | 不满足的要求 | E135 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 47 | EPC_Delivery.SystemCode | — | record data | 属性集.属性名，取自记录里的检查结果 |
| 48 | 规则编号 | E137 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 49 | R-005B | — | record data | 规则编号，取自记录里的检查结果 |
| 50 | 那次检查的结果 | E138 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 51 | 不通过 | E178 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 52 | 原因 | E139 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 53 | 所要求的属性集不存在（要让导出写出这个属性集以及其中所要求的属性，不是给已有属性填值） | Z01 | 界面用语 | BIM T1 复核：通过 |
| 54 | The required property set does not exist | — | record data | 检查结果的原因，记录自带的英文原文 |
| 55 | 那次检查观察到的值 | E140 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 56 | 那次检查没有观察到值 | E141 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 57 | 规则的原话（英文） | E143 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 58 | SystemCode data shall be provided in the dataset EPC_Delivery | — | record data | 规则的原话，记录自带的英文原文 |
| 59 | 这是本项目假定的要求（ProjectAssumption），不是通用要求。 规则给出的出处（英文原文）：Project-assumed EPC delivery requirement; not a buildingSMART obligation. | E144, E145 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed）；BIM T1 复核：通过 |
| 60 | 不满足的要求 | E135 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 61 | EPC_Delivery.AssetTag | — | record data | 属性集.属性名，取自记录里的检查结果 |
| 62 | 规则编号 | E137 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 63 | R-005B | — | record data | 规则编号，取自记录里的检查结果 |
| 64 | 那次检查的结果 | E138 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 65 | 不通过 | E178 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 66 | 原因 | E139 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 67 | 所要求的属性集不存在（要让导出写出这个属性集以及其中所要求的属性，不是给已有属性填值） | Z01 | 界面用语 | BIM T1 复核：通过 |
| 68 | The required property set does not exist | — | record data | 检查结果的原因，记录自带的英文原文 |
| 69 | 那次检查观察到的值 | E140 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 70 | 那次检查没有观察到值 | E141 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 71 | 规则的原话（英文） | E143 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 72 | AssetTag data shall be provided in the dataset EPC_Delivery | — | record data | 规则的原话，记录自带的英文原文 |
| 73 | 这是本项目假定的要求（ProjectAssumption），不是通用要求。 规则给出的出处（英文原文）：Project-assumed EPC delivery requirement; not a buildingSMART obligation. | E144, E145 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed）；BIM T1 复核：通过 |
| 74 | 资产标识的取值从哪里来、对应哪个 Revit 参数，记录未提供。 | E061 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |

## How it was made

Repository state: the `doctor/` directory is byte-identical to `origin/main` at `aa67b73`
(`git diff aa67b73 HEAD -- doctor` is empty); `main` then contained PR #56 to #60.

```bash
python doctor/serve.py --checks-dir <an empty folder>
```

The route was loaded in headless Microsoft Edge 155.0.4283.45 on Windows 11 through the DevTools
protocol, with a throw-away profile, an 880 px wide window, device scale factor 2 and the page
settled (its text unchanged for 600 ms). The image is the clip y = 92 to 2050 in CSS pixels, taken
from the full page without scrolling, 1760 x 3916 pixels. It was captured twice and the two
files were byte-identical. The block table was made with a script kept outside this repository, which
hard-codes this machine's paths: it reads every text block of the page with its position, matches
each to the wording registry, and looks the matched sentence up in the files above. The page has no
text drawn by CSS (the only `content:` strings in `doctor.css` belong to a narrow-screen table that is
not on this page), so the text blocks are the whole of the text in the image.

A captured image is not reproducible byte for byte on another machine, because rendering depends on
the browser and the system fonts; the SHA-256 above identifies the file as committed.

## When it goes stale

The capture shows the interface as it was at the commit above. When the item page or any sentence
in the table changes, replace the image, redo the table and update the commit and the hash here;
the README caption does not quote anything that is not on the screen.
