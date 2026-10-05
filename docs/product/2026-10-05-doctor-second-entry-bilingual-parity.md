# Doctor 首页第二入口：中英义务对照（D2）

日期：2026-10-05。负责：Product/UI Engineer。基线 `fd9bc9c`。
依据：[D1–D6 决定](2026-10-04-pm-six-decisions.md)的 D2 与技术总监的任务包；对照方法同
[P0 行动义务对照](2026-10-04-doctor-bilingual-action-parity.md)。状态：本文件列出的英文**全部未经 BIM 复核**，进 10/15 批次。

## 路径与来源

首页第二入口“随附项目检查尝试”的整条路径：

- 首页卡片 → `#/real` 列表 → `#/real/real-refusal` 拒绝页 → 返回上一级或返回首页；
- 途中的故障：程序故障屏、返回数据不符合约定的说明。

拒绝页上有三种文字，来源不同：

| 文字 | 来源 | 英文显示的是 |
| --- | --- | --- |
| 拒绝原因的标题、说明、“要让检查能够开始，需要什么” | 本界面写的句子，[中文词表](2026-10-02-doctor-recheck-vocabulary.md)第 12 节（“检查没有开始”） | **裁定句的英文**，与中文同一义务 |
| 页面框架（标题、引言、小标题、注记、折叠标题、标签） | 本界面写的句子，D2 前直接写在页面代码里，现在原样移进 `REFUSAL_PAGE` | 同一句的英文 |
| 拒绝码与系统返回的原文 | 适配器返回的 `refusal.code`、`refusal.text`，原本就是英文 | **原文**，两种语言都只在“系统返回的原文”折叠里显示，不当作说明或指令 |

系统原文（`team-mapping-decision-basis-illustrative`）说的是三件事：

- 为什么不能产出评估记录：所请求的活动能到达的每个非 READY 叶子，都落到一个默认角色上，而这个角色只由 `decision_basis` 不是 `project-decision` 的人员映射担任；
- 若照这样指派，就等于声称项目做过一个它从未做过的人员决定；
- 列出 4 条阻塞的映射行。

**原文没有给出行动。**“要让检查能够开始，需要什么”两句是产品写的，中英相同。

## 一、拒绝原因与说明（有领域含义）

| 键 | 中文（不变） | 英文（新增） | 同一义务？ | 与系统原文的关系 |
| --- | --- | --- | --- | --- |
| `REFUSAL_REASONS.team-mapping-decision-basis-illustrative.title` | 项目条件未满足：由谁处理的安排不是项目作出的决定 | Project condition not met: who deals with what is not a decision the project has made | 是 | 原文的结论（这些映射的 decision_basis 不是项目决定），用界面用语说 |
| `….text` | 这次请求所用的项目设定里，“哪个角色由哪个团队担任”的安排只是演示用的占位内容，不是项目作出的决定。系统因此不生成评估结果：否则结果里的处理团队会被当成项目的真实安排。 | In the project settings this request used, the arrangement of which team fills which role is demonstration placeholder content, not a decision the project has made. The system therefore produces no assessment: otherwise the handling teams in the result would be taken for the project's real arrangement. | 是 | 与原文第 1、2 句同义（illustrative 映射；会声称一个从未做过的人员决定）；不复述 4 条映射行，它们在折叠里 |
| `….action[0]` | 在一个真实项目上，要让检查能够开始：需要项目负责人实际决定系统原文（折叠在下面）点名的每个角色由谁担任，然后如实记录。这是一个人员决定，不是改一个标签。 | On a real project, for the check to be able to start: the project lead has to actually decide who fills each role that the system's own text (folded below) names, and record it as decided. This is a staffing decision, not a change of label. | 是 | 原文没有行动句；这是产品写的。“改一个标签”对应把 `decision_basis` 改成 `project-decision`，两种语言都明确说不是这样做 |
| `….action[1]` | 如果这次请求用的是随附的公开样例：它没有项目负责人。对它而言，这次拒绝就是正确的结果，不需要、也不应该去改它的设定。 | If this request used the bundled public sample: it has no project lead. For it, this refusal is the correct result; its settings do not need to be changed, and should not be. | 是 | 产品写的；不把拒绝改写成成功示例 |
| `REFUSAL_UNGLOSSED.title` | 系统拒绝了这次请求 | The system refused this request | 是 | 本界面没有说明的拒绝码用它（随附样例没有这种情况） |
| `REFUSAL_UNGLOSSED.text` | 本界面没有这个原因的中文说明，请展开下面系统返回的原文。 | This interface has no English explanation for this reason; open what the system returned below. | 是（“中文说明”在英文里相应写作“English explanation”） | 指向原文，不代替原文 |
| `REFUSAL_SCOPE_NOTE` | 处理当前拒绝原因不保证随后可评估；其余限制尚未由本次运行验证。 | Dealing with the current reason for refusal does not guarantee that an assessment can follow; the other limitations have not been verified by this run. | 是 | 产品写的，每次拒绝都显示 |

## 二、拒绝页框架（`REFUSAL_PAGE`，中文从页面代码原样移入）

| 键 | 中文（不变） | 英文（新增） | 同一义务？ |
| --- | --- | --- | --- |
| `title` | 这次检查尝试没有开始评估 | This check attempt did not start an assessment | 是 |
| `lede` | 系统在评估开始前拒绝了这次请求，并给出了原因。这是对请求条件的答复：不是程序故障，也不是检查结果。 | The system refused this request before the assessment started, and gave its reason. This is an answer about the request's conditions: not a program fault, and not a check result. | 是 |
| `whyHeading` | 为什么没有开始 | Why it did not start | 是 |
| `needHeading` | 要让检查能够开始，需要什么 | What is needed for the check to start | 是 |
| `onlyOne` | 本次只返回这一个原因，没有其他环节的诊断。 | Only this one reason was returned; there is no diagnosis of any other stage. | 是 |
| `noConclusion` | 没有任何事项的结论、零问题统计或完成百分比；被拒绝不是“无法判断”，也不是一次没有问题的检查。 | No conclusion on any item, no zero-problem count and no completion ratio: a refusal is not "Unknown", and not a check without problems. | 是（“无法判断”在英文界面里就是 “Unknown”，`VERDICT_LABELS`） |
| `original` | 系统返回的原文（英文）与拒绝码 | What the system returned (as written) and the refusal code | 是（与工作区拒绝页的英文折叠标题一致） |
| `attempt` | 检查尝试 | Check attempt | 是 |
| `code` | 拒绝码 | Refusal code | 是 |
| `contextMissing` | 所提交的请求上下文尚未随拒绝返回。 | The context of the request that was submitted has not been returned with the refusal yet. | 是 |

页面上的两个按钮改取已有词条：`APP.up`（返回上一级／Back up one level）、`CONTEXT.home`（返回首页／Back to the home page）。

## 三、路径上已有的英文（#33 起，本次未改，列出备查）

| 键 | 中文 | 英文 | 同一义务？ |
| --- | --- | --- | --- |
| `HOME.attempt.title` | 查看随附项目的检查尝试 | See the check attempt on the bundled project | 是 |
| `HOME.attempt.body` | 仓库随附一个样例项目。对它的检查尝试没有开始评估；这里说明原因。这不是导入入口，不能换成自己的模型。 | The repository comes with a sample project. The check attempt on it did not start an assessment; this explains why. It is not an import, and you cannot swap in your own model. | 是 |
| `HOME.attempt.action` | 查看这次检查尝试 | See this check attempt | 是 |
| `MODE_LABELS.real` | 随附项目的检查尝试 | Check attempt on the bundled project | 是 |
| `DIRECTORY.realNote` | 仓库随附一个样例项目，下面是对它的一次检查尝试。目前不能选择别的模型，也不能导入自己的模型。 | The repository comes with a sample project; below is a check attempt on it. You cannot choose another model yet, nor import your own. | 是 |
| `RUN_LABELS.real-refusal` | 对随附样例项目的一次检查尝试 | A check attempt on the bundled sample project | 是 |
| `CONTEXT.noResult` | 本次没有检查结果 | No check results this time | 是 |

途中可能遇到的故障说明（`FAULT_WORDS`、`APP` 里返回数据不符合约定的各句）在 #33 已有英文，本次未改。

## 四、未翻译页面的链接（界面用语）

记录、活动、成员页这次不翻译。英文界面里指向它们的四处链接如下：

- 首次结果页“追溯信息”里的“这份记录的请求范围、版本与来源”（`FIRST.recordLink`）；
- 复检页“追溯信息”里的同一链接；
- 单项页“在明细页查看完整的证据路径”（`ITEM.memberLink`）；
- 复检单项页“在明细页查看和它一起评估的全部构件与证据”（`EVIDENCE.memberLink`）。

这四处链接后面紧跟的说明改为写明 “Chinese only”：

| 键 | 中文（不变） | 英文（改） | 说明 |
| --- | --- | --- | --- |
| `FIRST.notRevised` | （该页尚未改版，仍是内部用语） | (Chinese only: that page has not been translated or revised yet, and still uses internal terms) | 英文多出 “Chinese only” 是有意的：中文界面里那一页本来就是中文。原有的“尚未改版、仍是内部用语”两种语言都保留 |
| `LANGUAGE.back`（新增） | ← 返回上一页 | ← Back to the previous page | 只出现在英文的“这一页还没有翻译”页上，作为返回路径；原有的“用中文查看这一页”和“返回首页”不变 |

## 五、交 10/15 BIM 的条目

- 有领域含义（第一、二节）：`REFUSAL_REASONS` 4 条、`REFUSAL_SCOPE_NOTE` 1 条、`REFUSAL_PAGE` 10 条；
- 界面用语：`REFUSAL_UNGLOSSED` 2 条、`LANGUAGE.back` 1 条、`FIRST.notRevised` 英文 1 条（改）。

英文词表 712 → 730 条（有领域含义 537 → 552，界面用语 163 → 166）。
