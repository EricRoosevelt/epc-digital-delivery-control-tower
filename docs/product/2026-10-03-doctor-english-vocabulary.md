# Doctor 英文词表（主路径第一部分：首页、示例目录、首次结果）

日期：2026-10-03。负责：Product/UI Engineer。状态：**全部未经 BIM 复核**；有领域含义的条目进 10/15 BIM 批次。
本文件由界面实际注册的词表生成，测试逐条核对英文与这里一致。中文一列是同一键在 `vocabulary.js` 里的原文。

## 规则

- 英文是第二张词表，不是第二套页面：判断、计数、来源标签、限制在两种语言里完全相同（测试逐键核对结构与占位符）。
- 记录、Pack 或本仓库产品文档已有英文原文的地方，英文界面显示原文，不把中文释义译回英文。
  “要做什么”“完成后拿什么复检”在英文里直接读记录里路由的 `next_action`、`recheck_condition`，词表里没有副本（`ACTION_TEXT`）。
  IFC 类别在英文里只显示类别本身（`IFC_CLASS_NAMES` 英文为空）。
- 英文模式下，还没有翻译的页面不画出来，显示“This page has not been translated yet”，并给出用中文看同一页的按钮。

## 计数

| 类别 | 表 | 条目 |
| --- | --- | --- |
| 原文（取自 Pack、记录或产品文档，未翻译） | 3 | 12 |
| 有领域含义（判断、活动、问题类型、限制、来源），待 BIM | 19 | 113 |
| 界面用语 | 15 | 86 |
| 合计 | 37 | 211 |

## 原文

**`ACTIVITY_NAMES`** —— 名称取自 Pack 的 `label`；`needs` 取自产品文档 interdisciplinary-coordination-readiness-mep-to-architecture.md 的 “What Architecture does next with it”，原句只把首字母大写

| 键 | 中文 | English |
| --- | --- | --- |
| `builders-work-openings.name` | 土建预留开洞 | Builder's-work openings |
| `builders-work-openings.needs` | 要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。 | Needs to know where MEP penetrates architectural fabric, so openings can be cut in walls, floors and roof. |
| `ceiling-and-bulkhead-geometry.name` | 吊顶平面与包封布置 | Reflected ceiling and bulkhead layout |
| `ceiling-and-bulkhead-geometry.needs` | 要知道交出方的设备在哪一层、在什么位置，才能围着它画吊顶分区和包封。 | Needs to know where MEP equipment physically is, in which storey, so ceiling zones and bulkheads can be drawn around it. |
| `schedules-and-room-data-sheets.name` | 房间数据表与设备明细表 | Room data sheets and equipment schedules |
| `schedules-and-room-data-sheets.needs` | 要每件设备都带有项目的资产标识，明细表才能按它编排。 | Needs each piece of equipment to carry the project's asset identity, so a schedule can be keyed to it. |

**`VERDICT_LABELS`** —— 记录本身的判断码 READY／BLOCKED／UNKNOWN，只改成首字母大写

| 键 | 中文 | English |
| --- | --- | --- |
| `READY` | 可以开始 | Ready |
| `BLOCKED` | 受阻 | Blocked |
| `UNKNOWN` | 无法判断 | Unknown |

**`VERDICT_WORDS`** —— 取自同一产品文档的判断词定义表（Definition 一列），去掉加粗和句末句号

| 键 | 中文 | English |
| --- | --- | --- |
| `READY` | 必要的证据齐全且满足验收条件，没有未解决的阻碍，也没有证据缺口：在本次评估范围内，这项工作可以开始 | Every piece of necessary evidence is present and satisfies the applicable acceptance conditions, and there is no unresolved blocker and no evidence gap. The activity can start, within the assessed scope |
| `BLOCKED` | 有一项已知未满足的要求，阻止这项工作 | A known unmet requirement prevents the activity |
| `UNKNOWN` | 回答这个问题所需的证据没有产生，这项工作能否开始无法决定：既不能放行，也不能拒绝 | An evidence gap makes the activity undecidable — the evidence needed to answer the question was never produced, so neither release nor refusal can be justified |

## 有领域含义，待 BIM 复核（10/15 批次）

**`ACTION_GROUPS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `open.label` | 需要处理的事项 | Items to deal with |
| `open.summary` | 记录给出了处理动作 | the record gives an action |
| `open.none` | 记录没有为任何一个事项给出处理动作。 | The record gives no action for any item. |
| `open.note` | 每个事项的页面写明涉及的构件、要做什么、由谁处理、完成后拿什么复检。 | Each item's page says which elements it involves, what to do, who deals with it and what a recheck must show. |
| `unplaced.label` | 需要人工核对的事项 | Items to check by hand |
| `unplaced.summary` | 记录没有给出当前情况，需要人工核对 | the record gives no current state; check by hand |
| `unplaced.none` | 每个事项记录都给出了当前情况。 | The record gives a current state for every item. |
| `unplaced.note` | 这些事项现在是什么判断，记录没有说。构件不在了不代表问题已修复。 | The record does not say what these items' conclusions are now. An element that is gone does not mean the problem was fixed. |
| `none.label` | 记录没有给出后续处理动作的事项 | Items for which the record gives no follow-up action |
| `none.summary` | 记录没有给出后续处理动作 | the record gives no follow-up action |
| `none.none` | 没有这样的事项。 | There are no such items. |
| `none.note` | 记录没有为下面这些事项给出后续处理动作。每一行的结论各自成立，范围写在它旁边。 | The record gives no follow-up action for the items below. Each line's conclusion stands on its own, with its scope beside it. |

**`BASIS_WORDS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `simulated` | 这个结论建立在模拟证据上： | This conclusion rests on simulated evidence: |
| `real` | 这个结论的依据： | Basis of this conclusion: |
| `sharedSimulated` | 同组事项共用的依据，其中有模拟证据： | Basis shared by the items in this group, some of it simulated: |
| `sharedReal` | 同组事项共用的依据： | Basis shared by the items in this group: |
| `none` | 这个结论没有引用任何证据。 | This conclusion cites no evidence. |
| `gaps.no-finding` | 没有任何检查结果（真实的缺席） | no check result at all (a real absence) |
| `gaps.no-determination` | 还没有判定（真实的缺席） | no determination yet (a real absence) |
| `gaps.not-applicable-finding` | 有检查结果，但检查不适用，没有覆盖到它 | there are check results, but the check did not apply and did not cover it |

**`BESIDE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `readyScope` | 只对这一个事项、这项工作、所列的模型版本成立；不代表整次交接完成。 | Holds for this one item, this work and the listed model versions only; it does not mean the whole handover is complete. |
| `unknown` | “无法判断”说的是这项工作能否开始无法判断：不等于这个构件没有问题，也不是系统出错。 | "Unknown" means whether this work can start cannot be decided: it does not mean the element has no problem, and it is not a system error. |
| `assetIdentity` | 资产标识的取值从哪里来、对应哪个 Revit 参数，记录未提供。 | Where the asset-identity value comes from, and which Revit parameter it maps to, the record does not say. |
| `team` | 处理团队是记录里的安排，不代表已经派发。 | The handling team is an entry in the record; it does not mean the work has been assigned. |
| `simulatedTeam` | 示例处理团队 | Example handling team |
| `noTeam` | 记录未提供 | Not given in the record |
| `defaultRole` | 默认处理角色（规则给出的默认，不是指派） | Default handling role (the rule's default, not an assignment) |
| `unchanged` | 复检前后未变 | Unchanged by the recheck |

**`CITATION_PROVENANCE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `finding-real.key` | real | real |
| `finding-real.short` | 真实检查输出 | Real check output |
| `finding-real.long` | 未带模拟标记的检查结果引用：来自真实的检查运行，是真实 IFC 模型按真实规则检查的产物。 | A check-result citation without the simulation marker: from a real check run, the product of checking a real IFC model against real rules. |
| `finding-fixture.key` | fixture | fixture |
| `finding-fixture.short` | 模拟的检查结果 | Simulated check result |
| `finding-fixture.long` | 带模拟标记（以 fixture 开头）的检查结果引用：由示例生成，不是任何真实检查运行的输出。 | A check-result citation with the simulation marker (starting with fixture): generated by the example, not the output of any real check run. |
| `determination-fixture.key` | fixture | fixture |
| `determination-fixture.short` | 模拟的人工判定 | Simulated human determination |
| `determination-fixture.long` | 带模拟标记的判定引用：由示例提供，没有任何协调评审真的发生过。 | A determination citation with the simulation marker: supplied by the example; no coordination review ever took place. |
| `determination-unmarked.key` | unmarked | unmarked |
| `determination-unmarked.short` | 来源未标注的判定 | Determination of unstated source |
| `determination-unmarked.long` | 未带模拟标记的判定引用：判定不是检查运行的输出，本界面也没有可核依据说明它来自哪里，因此不作真实或模拟的断言。 | A determination citation without the simulation marker: a determination is not the output of a check run, and this interface has nothing it can verify about where it came from, so it says neither real nor simulated. |

**`DEMO_NOTICE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `DEMO_NOTICE` | 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的检查结果或模拟的人工判定，具体是哪一种，看每个结论旁的“依据”一行（按逐条引用标明）。不能用于正式项目决定，也不能导出正式检查记录。 | Simulated example: the project settings in the example, including the handling teams and the acceptance of evidence methods, are demonstration settings, not real project decisions; the evidence for a conclusion may be a real check result, a simulated check result or a simulated human determination — which one, the "Basis" line beside each conclusion says (citation by citation). Not for formal project decisions, and no formal check record can be exported. |

**`DIRECTORY_NOTE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `DIRECTORY_NOTE` | 每个示例是一份检查记录。一个结论的证据可能是真实检查的结果，可能是模拟的检查结果，也可能是模拟的人工判定；具体是哪一种，看结果页和事项页每个结论旁的“依据”一行，按逐条引用标明。示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定。 | Each example is one check record. The evidence for a conclusion may be a real check result, a simulated check result or a simulated human determination; which one it is, the "Basis" line beside each conclusion on the result and item pages says, citation by citation. The project settings in the examples, including the handling teams and the acceptance of evidence methods, are demonstration settings, not real project decisions. |

**`ELEMENT_WORDS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `unnamed` | 模型中没有填写名称 | No name filled in in the model |
| `noFacts` | 记录没有返回这个构件的可读信息 | The record returned nothing readable about this element |
| `noStorey` | 模型中没有楼层归属 | No storey assignment in the model |
| `noDiscipline` | 记录未提供专业信息；本界面不从模型标识推断专业 | The record gives no discipline; this interface does not infer one from a model identifier |
| `modelIsNotDiscipline` | 这是模型标识，不是专业声明 | This is a model identifier, not a statement of discipline |
| `noClassName` | 本界面没有这个类别的中文名 | (IFC class) |
| `naming` | 名称取自模型文件本身，可能为空，也可能与别的构件重名；要在模型里定位，请用 GlobalId。 | The name is taken from the model file itself; it may be empty or shared with other elements. To find it in the model, use the GlobalId. |

**`EXAMPLES`**

| 键 | 中文 | English |
| --- | --- | --- |
| `member-evidence.step` | 第一步 | Step 1 |
| `member-evidence.question` | 交出方交了模型：有哪些事项要处理，各由谁处理，每一项要做什么？ | The handing-over side has handed over its model: which items need dealing with, who deals with each, and what does each one need? |
| `member-evidence.given` | 这个示例被给了：随附样例项目的两份模型；处理团队的安排，以及人工判定（是否穿过、洞口情况、两侧模型是否对齐），由示例设定。 | This example was given: the bundled sample project's two models; the handling teams, and the human determinations (whether something passes through, the state of openings, whether the two models are aligned), set by the example. |
| `recheck-requirement-relaxed.step` | 第二步 | Step 2 |
| `recheck-requirement-relaxed.question` | 同一份记录复检之后：两侧模型都没有重新发布，却有判断变了。变的是哪一项，为什么？ | The same record after a recheck: neither model was re-issued, yet a conclusion changed. Which one changed, and why? |
| `recheck-requirement-relaxed.given` | 这个示例被给了：一条被引用的检查要求放宽了；交出方和接收方的模型版本都没有变。 | This example was given: one cited check requirement was relaxed; neither the handing-over nor the receiving side's model version changed. |

**`EXAMPLE_NOTE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `EXAMPLE_NOTE` | 示例说明由搭建示例的人提供，只说这个示例被给了什么；它不是检查得出的结论。检查得出了什么，只看结果页。 | An example's description is written by whoever built the example and says only what the example was given; it is not a conclusion of any check. What the check concluded is on the result page only. |

**`HOME`**

| 键 | 中文 | English |
| --- | --- | --- |
| `title` | 查看模型交接中仍需处理的事项 | Items still to be dealt with in a model handover |
| `lede` | 帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。 | For a BIM manager: what a pre-handover check found; after a recheck, which conclusions changed, which items still need dealing with, which elements each one involves, what it rests on, and what to do next. |
| `status` | 当前为示例预览：尚不能导入自己的 Revit 模型，也不提供整体合规或可施工结论。 | This is an example preview: you cannot import your own Revit model yet, and it gives no overall compliance or ready-to-build conclusion. |
| `statusWithWorkspace` | 当前同时提供两样：启动服务器时指定的工作区里一次已经跑完的真实检查，以及模拟示例。页面上不能导入、选择或更换模型，也不提供整体合规或可施工结论。 | Two things are offered here: a real check already run in the workspace named when the server was started, and simulated examples. You cannot import, choose or change a model on this page, and it gives no overall compliance or ready-to-build conclusion. |
| `statusWorkspaceUnknown` | 未能确认服务器是否指定了工作区，所以这里没有真实检查的入口；这不等于没有工作区，错误原文在下面。模拟示例照常可看。页面上不能导入、选择或更换模型，也不提供整体合规或可施工结论。 | Could not confirm whether the server was started with a workspace, so there is no entry to a real check here; that does not mean there is no workspace — the error is below. The simulated examples are available as usual. You cannot import, choose or change a model on this page, and it gives no overall compliance or ready-to-build conclusion. |
| `example.title` | 看一个模拟示例 | Look at a simulated example |
| `example.body` | 从一次首次检查出发：找到需要处理的事项，看清涉及的构件、要做什么、由谁处理、完成后拿什么复检；然后再看同一事项复检后的变化。示例里模拟的内容，页面上逐处标明。 | Start from a first check: find the items that need dealing with, and see which elements they involve, what to do, who deals with it and what a recheck must show; then see how the same item changed after a recheck. What is simulated in the example is marked where it appears. |
| `example.action` | 选择模拟示例 | Choose a simulated example |
| `attempt.title` | 查看随附项目的检查尝试 | See the check attempt on the bundled project |
| `attempt.body` | 仓库随附一个样例项目。对它的检查尝试没有开始评估；这里说明原因。这不是导入入口，不能换成自己的模型。 | The repository comes with a sample project. The check attempt on it did not start an assessment; this explains why. It is not an import, and you cannot swap in your own model. |
| `attempt.action` | 查看这次检查尝试 | See this check attempt |
| `cannot[0]` | 在页面上导入、选择或更换模型，包括自己的 Revit 或 IFC 模型 | Import, choose or change a model on the page, including your own Revit or IFC model |
| `cannot[1]` | 给出整体合规、可施工或“可以交付”的结论 | Give an overall compliance, ready-to-build or "ready to hand over" conclusion |
| `cannot[2]` | 写回模型、上传到云端，或在 Revit 里打开构件 | Write back to a model, upload to the cloud, or open an element in Revit |
| `canHeading` | 现在可以做什么 | What you can do now |
| `cannotHeading` | 现在还不能做什么 | What you cannot do yet |
| `cannotNote` | 这些功能没有实现，所以页面上没有对应的入口。 | These are not implemented, so the page has no entry for them. |

**`ITEM_UNIT`**

| 键 | 中文 | English |
| --- | --- | --- |
| `ITEM_UNIT` | 一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。同一个构件可以出现在几个事项里，所以事项数不是缺陷数。 | An item is the conclusion for one element (or a pair of elements assessed together) on one piece of the receiving side's work. The same element can appear in several items, so the number of items is not a number of defects. |

**`MODE_LABELS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `fixture` | 模拟示例 | Simulated example |
| `real` | 随附项目的检查尝试 | Check attempt on the bundled project |
| `workspace` | 工作区里的真实检查 | Real check in a workspace |

**`PROVENANCE_NOTICE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `PROVENANCE_NOTICE` | 本页每条引用旁的来源标注按该条引用自身判定（是否带模拟标记），不按整页或整份记录推断： | Each citation's source label on this page is decided from that citation alone (whether it carries the simulation marker), never inferred for the whole page or record: |

**`READING_GUIDE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `verdictWords` | 三个判断词 | The three conclusion words |
| `verdictLine` | {label}：{meaning}。 | {label}: {meaning}. |
| `provenance` | 证据来源的标注 | How the source of evidence is labelled |
| `teams` | 处理团队与默认处理角色 | Handling team and default handling role |
| `teamsBody` | 处理团队取自记录里的人员安排；默认处理角色是规则给出的默认，是安排的输入，不是指派。两者分开显示。 | The handling team is taken from the staffing in the record; the default handling role is the rule's default, an input to the staffing, not an assignment. The two are shown apart. |

**`READY_NOTES`**

| 键 | 中文 | English |
| --- | --- | --- |
| `ceiling-and-bulkhead-geometry[0]` | 规则只证明构件有楼层或空间归属，没有验证接收方模型有对应楼层。 | The rule proves only that the element has a storey or space assignment; it does not check that the receiving model has a matching storey. |
| `ceiling-and-bulkhead-geometry[1]` | 这个结论靠的是两侧模型的对齐确认，不是共享定位标记通过。 | This conclusion rests on a confirmation that the two models are aligned, not on a shared positioning marker passing. |

**`RESOLUTION_KINDS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `missing-project-asset-identity` | 缺少本项目约定的资产标识 | The project's required asset identity is missing |
| `asset-identity-not-evaluated` | 不是已知的模型缺陷：现有资产标识规则没有覆盖到这个构件 | Not a known model defect: the existing asset-identity rules did not cover this element |
| `mep-element-not-spatially-assigned` | 它没有楼层或空间归属 | It has no storey or space assignment |
| `in-model-position-not-evaluated` | 不是已知的模型缺陷：楼层或空间归属的检查没有覆盖到它 | Not a known model defect: the storey or space check did not cover it |
| `cross-model-misalignment` | 两侧模型没有对齐到共同的基准 | The two models are not aligned to a common datum |
| `cross-model-alignment-not-confirmed` | 不是已知的错位：还没有人确认两侧模型对齐 | Not a known misalignment: nobody has confirmed yet that the two models are aligned |
| `penetration-not-determined` | 不是已知的模型缺陷：还没有协调评审判定它是否穿过接收方的构件 | Not a known model defect: no coordination review has determined yet whether it passes through the receiving side's elements |
| `opening-not-verifiably-linked` | 洞口已建，但没有关联到穿过它的这个构件 | The opening is modelled, but not linked to this element that passes through it |
| `missing-corresponding-opening` | 它穿过的构件上没有建出对应的洞口 | No corresponding opening is modelled in the element it passes through |
| `opening-status-not-determined` | 不是已知的缺洞：开洞情况的评审还没有完成 | Not a known missing opening: the review of the opening has not been completed yet |

**`RUN_LABELS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `member-evidence` | 一次首次检查：交了模型，发现这些事项 | A first check: the model was handed over, and these items were found |
| `pair-verdicts` | 同一份检查记录：成对构件的判断（模拟示例） | The same check record: conclusions on pairs of elements (simulated example) |
| `recheck-both-reissued` | 复检记录 1（模拟示例） | Recheck record 1 (simulated example) |
| `recheck-comparison` | 复检记录 2（模拟示例） | Recheck record 2 (simulated example) |
| `recheck-consuming-reissued` | 复检记录 3（模拟示例） | Recheck record 3 (simulated example) |
| `recheck-key-change-only` | 复检记录 4（模拟示例） | Recheck record 4 (simulated example) |
| `recheck-member-gone` | 复检记录 5（模拟示例） | Recheck record 5 (simulated example) |
| `recheck-prior-without-basis` | 复检记录 6（模拟示例） | Recheck record 6 (simulated example) |
| `recheck-producing-reissued` | 复检记录 7（模拟示例） | Recheck record 7 (simulated example) |
| `recheck-producing-reissued-content-changed` | 复检记录 8（模拟示例） | Recheck record 8 (simulated example) |
| `recheck-requirement-relaxed` | 模型未改，但交接判断发生变化 | The models did not change, but a handover conclusion did |
| `recheck-semantics-changed` | 复检记录 10（模拟示例） | Recheck record 10 (simulated example) |
| `real-refusal` | 对随附样例项目的一次检查尝试 | A check attempt on the bundled sample project |

**`VERDICT_SCOPE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `VERDICT_SCOPE` | 每个判断只针对接收方的一项工作、本次评估范围内的这一项，以及所列的模型版本；它不是“模型好不好”的总评，也不是“某项检查通过了”。 | Each conclusion is about one piece of the receiving side's work, this item within this assessment's scope, and the listed model versions; it is not an overall verdict on whether the model is good, nor a statement that some check passed. |

**`WORKSPACE_HOME`**

| 键 | 中文 | English |
| --- | --- | --- |
| `title` | 查看一次真实检查 | See a real check |
| `body` | 启动服务器时指定了一个工作区，里面是一次已经跑完的检查：每个构件在每条要求下的结果。若同时指定了前一次运行，还可以看两次的前后对比。这里只有检查结果，没有交接判断。页面只查看这次已经跑完的检查，不能在页面上选择或更换模型。 | The server was started with a workspace holding a check that has already run: each element's result under each requirement. If an earlier run was named as well, the two can be compared. There are check results only here, no handover judgement. This page only shows the check that has already run; you cannot choose or change a model on it. |
| `action` | 查看这次检查 | See this check |
| `unknown` | 未能确认服务器是否指定了工作区（不等于没有工作区）。错误原文： | Could not confirm whether the server was started with a workspace (that does not mean there is none). The error: |

## 界面用语

**`APP`**

| 键 | 中文 | English |
| --- | --- | --- |
| `loading` | 正在读取检查记录… | Reading the check record… |
| `noPage` | 没有这个页面：{screen} | There is no such page: {screen} |
| `technical` | 技术信息（原文）： | Technical detail (as given): |
| `up` | 返回上一级 | Back up one level |
| `notInMode` | 这个入口下没有 {run} | There is no {run} under this entry |
| `invalid` | 返回的数据不符合约定：{problem}。未显示任何结果。 | The returned data does not match the agreed shape: {problem}. No result is shown. |
| `unknownOutcome` | 未识别的 outcome {outcome} | Unrecognised outcome {outcome} |
| `notObject` | 返回的数据不是对象 | The returned data is not an object |
| `modeMismatch` | 返回数据的 mode 为 {got}，与所选入口 {want} 不一致 | The returned data's mode is {got}, not the entry chosen, {want} |
| `missingElements` | 返回的数据缺少 elements | The returned data has no elements |
| `recordMissing` | outcome=record 但缺少 record | outcome=record but record is missing |
| `digestMissing` | outcome=record 但缺少 assessment_digest | outcome=record but assessment_digest is missing |
| `recordWithRefusal` | outcome=record 却同时带有 refusal | outcome=record but it also carries refusal |
| `refusalIncomplete` | outcome=refusal 但 refusal 缺少 code 或 text | outcome=refusal but refusal has no code or text |
| `refusalWithRecord` | outcome=refusal 却同时带有 record 或 assessment_digest | outcome=refusal but it also carries record or assessment_digest |

**`COMMON`**

| 键 | 中文 | English |
| --- | --- | --- |
| `colon` | ： | :  |
| `emptyList` | （记录中为空列表） | (an empty list in the record) |
| `unknownMode` | 未识别的入口（{mode}） | Unrecognised entry ({mode}) |
| `unnamedElement` | 未命名构件 | Unnamed element |
| `and` |  与  |  and  |
| `oneElement` | 一个构件 | One element |
| `twoElements` | 一对构件 | A pair of elements |
| `nElements` | {count} 个构件 | {count} elements |
| `inModel` |  · 模型  |  · model  |

**`CONTEXT`**

| 键 | 中文 | English |
| --- | --- | --- |
| `project` | 项目 {project} | Project {project} |
| `handover` | 交接：{from} → {to} · {milestone} | Handover: {from} → {to} · {milestone} |
| `workspaceRun` | 检查运行 | Check run |
| `noJudgement` | 只有检查结果，没有交接判断 | Check results only, no handover judgement |
| `noResult` | 本次没有检查结果 | No check results this time |
| `home` | 返回首页 | Back to the home page |

**`COPY`**

| 键 | 中文 | English |
| --- | --- | --- |
| `button` | 复制 | Copy |
| `label` | 复制 {value} | Copy {value} |
| `done` | 已复制 | Copied |
| `manual` | 请手动选择复制 | Select it to copy by hand |

**`DIRECTORY`**

| 键 | 中文 | English |
| --- | --- | --- |
| `realNote` | 仓库随附一个样例项目，下面是对它的一次检查尝试。目前不能选择别的模型，也不能导入自己的模型。 | The repository comes with a sample project; below is a check attempt on it. You cannot choose another model yet, nor import your own. |
| `exampleTitle` | 选择一个模拟示例 | Choose a simulated example |
| `empty` | 这个入口下目前没有可以查看的内容。 | There is nothing to look at under this entry yet. |
| `exampleTag` | 示例说明 | About this example |
| `open` | 打开这个示例的结果 | Open this example's result |
| `othersHeading` | 其他模拟示例 | Other simulated examples |
| `othersNote` | 这些示例还没有写说明，复检记录暂时只有编号；本轮没有改到它们。 | These examples have no description yet, and the recheck records have only a number for now; this round did not touch them. |

**`EMPTY_STRING`**

| 键 | 中文 | English |
| --- | --- | --- |
| `EMPTY_STRING` | （记录中为空字符串） | (an empty string in the record) |

**`ENVELOPE_WORDS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `missing` | outcome={outcome} 但缺少 {key} | outcome={outcome} but {key} is missing |
| `unexpected` | outcome={outcome} 却同时带有 {key} | outcome={outcome} but it also carries {key} |

**`FAULT_WORDS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `fault` | 程序故障：没有拿到检查数据 | Program fault: no check data was received |
| `unavailable` | 检查程序不可用 | The check program is unavailable |
| `note` | 这是程序自身的问题，不是对任何项目或模型的判断；没有任何检查结果可以显示。 | This is a problem of the program itself, not a judgement about any project or model; there are no check results to show. |

**`FIRST`**

| 键 | 中文 | English |
| --- | --- | --- |
| `back` | ← 返回示例目录 | ← Back to the examples |
| `title` | 首次检查结果：需要处理的事项 | First check result: items to deal with |
| `runLine` | {mode}：{run} | {mode}: {run} |
| `summary` | 本次结果：共 {items} 个事项，其中 {todo} 个需要处理 | This result: {items} items, {todo} of which need dealing with |
| `items` | {count} 个事项 | {count} items |
| `verdictLine` | ：对应的那项工作  | : the work concerned is  |
| `quietLine` | ：{summary}（列在本页下方） | : {summary} (listed further down this page) |
| `elementsLine` | {unit}这份记录共涉及 {count} 个不同的构件。 | {unit} This record involves {count} different elements. |
| `action` | 要做什么 | What to do |
| `problem` | 问题 | Problem |
| `openItem` | 查看这一项：具体对象、要做什么、由谁处理、拿什么复检 | See this item: the element, what to do, who deals with it, what a recheck must show |
| `openHeading` | {label}，按处理团队（{count} 个事项） | {label}, by handling team ({count} items) |
| `team` | 处理团队  | Handling team  |
| `teamCount` | ：{count} 个事项 | : {count} items |
| `columns.problem` | 问题 | Problem |
| `columns.work` | 哪项工作：结论 | Which work: conclusion |
| `columns.count` | 事项数 | Items |
| `quietHeading` | {label}（{count} 个事项） | {label} ({count} items) |
| `separator` |  ｜  |  \|  |
| `nextHeading` | 然后：看这份记录复检之后的变化 | Then: see how this record changed after a recheck |
| `nextLink` | 打开示例“{run}” | Open the example "{run}" |
| `nextAfter` | 。每个事项的页面里也有直达它复检变化的链接。 | . Each item's page also links straight to how that item changed in the recheck. |
| `traceSummary` | 追溯信息：记录标识、规则版本、记录原码 | Tracing: record identity, rule version, record codes |
| `recordLink` | 这份记录的请求范围、版本与来源 | This record's requested scope, versions and sources |
| `notRevised` | （该页尚未改版，仍是内部用语） |  (that page has not been revised yet and still uses internal terms) |
| `traceItem` | 事项 | Item |
| `traceOrdinal` | 内部分组编号 | Internal group number |

**`HOW_TO_READ`**

| 键 | 中文 | English |
| --- | --- | --- |
| `HOW_TO_READ` | 如何阅读这一页 | How to read this page |

**`IFC_CLASS_NAMES`**

| 键 | 中文 | English |
| --- | --- | --- |

**`LANGUAGE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `label` | 界面语言 | Interface language |
| `current` | 当前：中文 | Current: English |
| `untranslatedTitle` | 这一页还没有翻译 | This page has not been translated yet |
| `untranslatedBody` | 这一页的英文还没有写好。下面可以用中文查看同一页：同一个运行、同一份记录、同一个对象，内容不变。 | The English for this page has not been written yet. You can see the same page in Chinese below: the same run, the same record and the same element, with nothing changed. |
| `showIn` | 用中文查看这一页 | See this page in Chinese |
| `home` | 返回首页 | Back to the home page |

**`NOT_CARRIED`**

| 键 | 中文 | English |
| --- | --- | --- |
| `NOT_CARRIED` | 记录未携带 | Not carried in the record |

**`PAGE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `title` | BIM Doctor 预览 | BIM Doctor preview |
| `skip` | 跳到正文 | Skip to the content |
| `contextLabel` | 当前模式与上下文 | Current mode and context |

**`UNRECOGNISED`**

| 键 | 中文 | English |
| --- | --- | --- |
| `UNRECOGNISED` | 未识别的值，按原值显示 | unrecognised value, shown as it came |
