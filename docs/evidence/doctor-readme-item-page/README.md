# README screenshot: one item page, Chinese interface

One capture of the BIM Doctor local preview, in the Chinese interface, shown by the root
[`README.md`](../../../README.md) under *What you will see*, step 3. It is an illustration of what
the interface looked like. It is not acceptance evidence for the preview, and nothing validates
it: no manifest or test pins this directory.

| File | Route | Shows |
|---|---|---|
| `item-blocked-zh.png` | `#/fixture/member-evidence/item/2/2/0` | One item of the simulated first-check example: the conclusion with its basis, then part 二、下一步 (what to do, the handling team, the default handling role, what it means for the work, what a recheck must show), then the element's name and class |

```text
5ea20a08eb3515aaa639e23c8eb5119ff69b8b4966aaf2cdb41eb44dbcc37d3f  item-blocked-zh.png
```

## What is in the pixels

- **Public sample data only.** The example reads the two bundled buildingSMART PCERT sample
  models of the `pcert-sample` project (see *Data Source and Attribution* in the root README).
  The server was started without a workspace, so the page offered no workspace entry.
- **Simulated content is marked.** The "simulated example" strip and the line saying the example
  is not your model sit above this crop, so they are not in the image; the README caption says it.
  Inside the image, the handling team carries the label 示例处理团队 (example handling team) and
  the page says the team is an entry in the record and does not mean anything has been assigned.
  The conclusion's basis reads "real check output": the check results behind this item come from a
  real run of the shipped rules on the sample models.
- **No private material.** Nothing from the controlled real case, its models or its workspace
  appears, and no local path, account or address is visible. The PNG carries no text or time
  metadata chunks (IHDR, IDAT, IEND only).

## Why this crop, and what is outside it

The rule for putting a screenshot in the public README is that every visible text block is either
a sentence BIM passed **as it reads now**, or data from the model or the record. The crop is the
longest stretch of this page for which that holds: it starts at the conclusion line and ends at the
class row of part 三.

Outside it, because no BIM verdict covers them (they are interface wording that none of the review
files lists): the page heading and back link above, the kicker "首次检查事项 · 一个构件", the heading
"一、结论", and from the 楼层 and 专业 labels downward in part 三. That is why the image starts and
ends mid-card. Part 四 (what exactly is missing) is not in the image for the same reason: its
heading is not covered.

## Sentence by sentence

The table lists every text block in the image, top to bottom (26). *Id* is the index id in
[`2026-10-09-bim-review-subset-public-route.csv`](../../product/2026-10-09-bim-review-subset-public-route.csv)
or in BIM's verdict files, which are
[`2026-10-09-bim-review-t1-verdicts.csv`](../../product/2026-10-09-bim-review-t1-verdicts.csv),
[`2026-10-09-bim-review-t2-verdicts.csv`](../../product/2026-10-09-bim-review-t2-verdicts.csv) and
`2026-10-10-bim-review-56-57-verdicts.csv` (BIM's review of PR #56 and #57; at the time of writing
this last file is held by the technical director and is not committed, so the two rows that rest on
it, 情况 and 二、下一步, cannot be checked from the repository alone).
"10/8, same sentence" means BIM's 10/8 review of the first-check path, and the sentence is
byte-identical today.

| # | On the image | Id | Kind | Basis |
|---:|---|---|---|---|
| 1 | 房间数据表与设备明细表：受阻 | E008, E005 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 2 | 这个结论的依据：真实检查输出 ×2 | E100, E052 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 3 | 情况 | E587 | 界面用语 | BIM #56/#57 复核：通过 |
| 4 | 缺少本项目约定的资产标识 | E345 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 5 | 这个结论依据的结果 | E219 | 界面用语 | BIM T1 复核：通过 |
| 6 | 项目资产标识的要求没有满足 | E204 | 界面用语 | BIM T1 复核：通过 |
| 7 | 二、下一步 | E582 | 界面用语 | BIM #56/#57 复核：通过 |
| 8 | 要做什么 | E573 | 界面用语 | BIM T1 复核：通过 |
| 9 | 在源模型里给这个构件补上本项目约定的资产标识属性（见所列属性集和属性名），重新导出 | E013 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 10 | 处理团队 | E584 | 界面用语 | BIM T1 复核：通过 |
| 11 | coordination-team 示例处理团队 | E063 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 12 | 处理团队是记录里的安排，不代表已经派发。 | E062 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 13 | 默认处理角色（规则给出的默认，不是指派） | E065 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 14 | model-coordination | — | record data | 默认处理角色的代码，来自记录（不是界面用语） |
| 15 | 对这项工作的后果 | E575 | 界面用语 | BIM T1 复核：通过 |
| 16 | 这项工作不能开始 | E126 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 17 | 有重新标识的风险：引用这些标识的文件届时也须重新出具 | E129 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 18 | 完成后拿什么复检 | E576 | 界面用语 | BIM T1 复核：通过 |
| 19 | 重新发布的模型上，这个构件在所列每条要求下都通过 | E014 | 界面用语 | BIM T1 复核：通过 |
| 20 | 来源原文（英文，记录所带）：供追溯，不是操作指令 | E577 | 界面用语 | BIM T1 复核：通过 |
| 21 | 这项工作需要什么 | E579 | 界面用语 | BIM T1 复核：通过 |
| 22 | 要每件设备都带有项目的资产标识，明细表才能按它编排。 | E006 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 23 | 三、是哪个构件 | E285 | 界面用语 | BIM T1 复核：通过 |
| 24 | chimney cover | — | model data | 构件名称，取自样例模型（不是界面用语） |
| 25 | 类别 | E444 | 界面用语 | BIM 10/8 复核，同句（子集状态 reviewed） |
| 26 | 风口 IfcAirTerminal | — | gloss + model data | “风口”是界面给 IFC 类别的中文名，IFC_CLASS_NAMES.IfcAirTerminal，BIM T1 复核：通过；“IfcAirTerminal”是模型里的类别名 |

## How it was made

Repository state: the `doctor/` directory is byte-identical to `origin/main` at
`e067255` (`git diff e067255 HEAD -- doctor` is empty); `main` then contained PR #56, #57 and #58.

```bash
python doctor/serve.py --checks-dir <an empty folder>
```

The route was loaded in headless Microsoft Edge 155.0.4283.45 on Windows 11 through the DevTools
protocol, with a throw-away profile, an 880 px wide window, device scale factor 2 and the page
settled (its text unchanged for 600 ms). The image is the clip y = 385 to 1092 in CSS pixels, taken
from the full page without scrolling, 1760 x 1414 pixels. It was captured twice and the two files
were byte-identical. The block table was made with a script kept outside this repository, which
hard-codes this machine's paths: it reads every text block of the page with its position, matches
each to the wording registry, and looks the matched sentence up in the files above.

A captured image is not reproducible byte for byte on another machine, because rendering depends on
the browser and the system fonts; the SHA-256 above identifies the file as committed.

## When it goes stale

The capture shows the interface as it was at the commit above. When the item page or any sentence
in the table changes, replace the image, redo the table and update the commit and the hash here;
the README caption does not quote anything that is not on the screen.
