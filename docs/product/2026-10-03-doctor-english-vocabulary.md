# Doctor 英文词表（主路径与真实工作区）

日期：2026-10-03；第二部分（单项、复检）与第三部分（工作区的结果、详情、对比、拒绝、故障）同日补入；2026-10-04 补入行动与复检句（`ACTIONS`）；2026-10-05 补入首次结果卡片的三个标签（`FIRST.cardDetails`、`FIRST.cardElements`、`FIRST.openCard`），以及随附项目检查尝试的拒绝页（`REFUSAL_REASONS`、`REFUSAL_SCOPE_NOTE`、`REFUSAL_PAGE`、`REFUSAL_UNGLOSSED`）；同日删去与页首来源提示重复的 `DIRECTORY_NOTE`，复检单项页的标题序号随区块顺序调整。同日补入本地 IFC 检查的 `LOCAL_CHECK`（146 条，#29）。2026-10-08 补入页首来源提示的短摘要 `SOURCE_SUMMARY`（11 条；原 `DEMO_NOTICE` 不变，成为展开后的全文）和示例目录的一句简介 `DIRECTORY.exampleIntro`。2026-10-09 按 BIM 第二批修正 M1、W2–W8、W10 的中英文，并新增 `CONDITION_ENTRIES.no-recheck-condition.plainNotReady`（W4）。2026-10-09 首页补一句 `HOME.recommended`（简历版本 UI 主线整理）。同日按 BIM T1 结论修正 E127、E079、E357／E360／E372、E587、Q01、L008，并新增 `RECHECK_ITEM.changedCondition`（E291）。同日并入 BIM T2/T3 的 E282、E161、L017、L018。负责：Product/UI Engineer。
状态：**全部未经 BIM 复核**；有领域含义的条目进 10/15 BIM 批次。
本文件由界面实际注册的词表生成，测试逐条核对英文与这里一致。中文一列是同一键在 `vocabulary.js` 里的原文。

## 规则

- 英文是第二张词表，不是第二套页面：判断、计数、来源标签、限制在两种语言里完全相同（测试逐键核对结构与占位符）。
- 记录、Pack 或本仓库产品文档已有英文原文的地方，英文界面显示原文，不把中文释义译回英文。
  例外：“要做什么”“完成后拿什么复检”不显示原文。两种语言用同一张表（`ACTIONS`：BIM 约束第 3 节的表，烟囱资产标识一句是产品裁定），
  义务相同；记录路由里的 `next_action`、`recheck_condition` 只在折叠里，标明是来源原文，不是操作指令（2026-10-04 起，见 P0 修正）。
  IFC 类别在英文里只显示类别本身（`IFC_CLASS_NAMES` 英文为空）；检查结果的原因在英文里只显示原文（`REASON_GLOSSES` 英文为空）。
  复检单项里“复检前留下的结束条件”同样用 `ACTIONS` 的复检句；记录的 `prior_recheck_condition` 原文在折叠里。
  工作区页面里，规则的出处在英文里只显示返回数据的原文（`CITATION_GLOSSES` 英文为空）；检查结果的原因、规则原话（`expected`）同样只显示原文。
  PV-001 规则说明的英文标题取自 `rules/product-validation/PV-001.toml` 的 `title`，“NOTDEFINED states nothing.”取自同一文件的 `instructions`（测试核对）；其余规则说明是为本界面写的领域文字，待 BIM。
  拒绝原因旁的短句在两种语言里都是本界面写的说明；适配器给出的完整原文（英文）始终在“系统返回的原文”折叠里。
  随附项目检查尝试的拒绝页同样如此：拒绝原因、说明和“要让检查能够开始，需要什么”是本界面写的句子（中文词表第 12 节），英文与中文义务相同；系统返回的原文（英文）始终在折叠里，不当作说明或指令。
- 记录、活动、成员页还没有英文。英文界面里指向它们的链接旁写明“Chinese only”（`FIRST.notRevised` 的英文），中文没有这一句，因为中文页面本来就是中文；未翻译页加了“返回上一页”。
- 带计数的说法分单数和复数两种形式（`one`／`other`），中文两种形式相同。
- 英文模式下，还没有翻译的页面不画出来，显示“This page has not been translated yet”，并给出用中文看同一页的按钮。

## 计数

| 类别 | 表 | 条目 |
| --- | --- | --- |
| 原文（取自 Pack、记录或产品文档，未翻译） | 3 | 12 |
| 有领域含义（判断、活动、问题类型、限制、来源），待 BIM | 55 | 711 |
| 界面用语 | 24 | 167 |
| 合计 | 82 | 890 |

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

**`ACTIONS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `missing-project-asset-identity.action` | 在源模型里给这个构件补上本项目约定的资产标识属性（见所列属性集和属性名），重新导出 | In the source model, add to this element the asset-identity properties the project's convention requires (see the property sets and property names listed), then re-export the model |
| `missing-project-asset-identity.recheck` | 重新发布的模型上，这个构件在所列每条要求下都通过 | On the reissued model, this element passes every requirement listed |
| `asset-identity-not-evaluated.action` | 现有资产标识规则没有覆盖到这个构件，所以它有没有资产标识还没有被评估，不能判断是否缺少；这项工作能否开始也因此无法判断。先确认项目约定是否要求它具备资产标识，以及规则该不该覆盖到它。在确认之前，这不表示它必须具备资产标识。 | The existing asset-identity rules do not reach this element, so whether it has an asset identity has not been evaluated, and it cannot be judged to be missing one; for the same reason, whether this work can start cannot be decided. First confirm whether the project's convention requires this element to have an asset identity, and whether the rules should reach it. Until that is confirmed, this does not mean it must have one. |
| `asset-identity-not-evaluated.recheck` | 范围内每个构件在所绑定的要求下都有评估结果 | Every element in the scope has an evaluation result under the requirements bound to it |
| `in-model-position-not-evaluated.action` | 这不是已知的模型缺陷。它的空间归属目前还没有评估：空间归属的检查规则没有覆盖到这个构件。这一步是扩展规则的适用范围，让检查覆盖到它，而不是改模型；覆盖并运行之后，才知道要不要改模型 | This is not a known model defect. Its spatial assignment has not been evaluated yet: the spatial-assignment check rules do not reach this element. This step is to extend the rules' scope of application so that the check reaches it, not to change the model; only once it is covered and the check has run will it be known whether the model needs changing |
| `in-model-position-not-evaluated.recheck` | 范围内每个构件在所绑定的要求下都有检查结果 | Every element in the scope has a check result under the requirements bound to it |
| `penetration-not-determined.action` | 这不是已知的模型缺陷。还没有协调评审判定它是否穿过接收方的构件；需要开一次评审，记录“不穿过”或写明穿过哪些构件 | This is not a known model defect. No coordination review has yet determined whether it passes through the receiving side's elements; hold a review and record either “no penetration” or which elements it passes through |
| `penetration-not-determined.recheck` | 针对所列模型版本，有一份评审判定记录 | A recorded review determination exists for the model versions listed |
| `missing-corresponding-opening.action` | 在接收方模型里、被穿过的构件上建出洞口或竖井，不要做成交出方模型里的空洞。穿过几个构件就要几个洞口 | In the receiving side's model, model an opening or shaft in the element it passes through, not a void in the handing-over side's model. One opening for each element it passes through |
| `missing-corresponding-opening.recheck` | 这一对的开洞核查结果为“洞口已建且已关联”。只建洞不够 | The opening check for this pair reports “opening modelled and cross-referenced”. Modelling the opening alone is not enough |
| `cross-model-alignment-not-confirmed.action` | 这不是已知的错位。还没有人按项目接受的方法确认两侧模型对齐；需要针对所列模型版本做一次并记录 | This is not a known misalignment. No one has yet confirmed, by the method the project accepts, that the two models are aligned; do this once against the model versions listed, and record it |
| `cross-model-alignment-not-confirmed.recheck` | 对齐确认已做，结果为已对齐，写明模型版本 | The alignment confirmation has been done and reports the models aligned, naming the model versions |
| `mep-element-not-spatially-assigned.action` | 在源模型里把构件放到正确的标高上（项目要求空间归属时，再放进对应的空间），重新导出 | In the source model, place the element on its correct level (and, where the project requires spatial assignment, in its corresponding space), then re-export |
| `mep-element-not-spatially-assigned.recheck` | 重新发布的模型上，这个构件的空间归属要求通过 | On the reissued model, this element passes its spatial-assignment requirement |
| `cross-model-misalignment.action` | 重新获取项目共用的坐标基准，按共用原点重新导出（不靠移动几何），再按项目接受的方法重做对齐确认 | Re-acquire the project's shared coordinate datum, re-export against the shared origin (not by moving geometry), then redo the alignment confirmation by the method the project accepts |
| `cross-model-misalignment.recheck` | 针对新版本重做对齐确认，结果为已对齐 | The alignment confirmation is redone against the new versions and reports the models aligned |
| `opening-not-verifiably-linked.action` | 在接收方模型里，给洞口补上指回穿过它的那个构件的关联。一个洞口供几个构件穿过，每个各要一条 | In the receiving side's model, add to the opening a cross-reference back to the element that passes through it. Where several elements pass through one opening, each needs its own |
| `opening-not-verifiably-linked.recheck` | 这一对的关联核查结果为已关联 | The cross-reference check for this pair reports the opening cross-referenced |
| `opening-status-not-determined.action` | 这不是已知的缺洞。开洞情况的评审没完成：洞口是否已建、是否已关联 | This is not a known missing opening. The review of the opening is not complete: whether it is modelled, and whether it is cross-referenced |
| `opening-status-not-determined.recheck` | 核查给出明确结果（已关联／已建未关联／未建） | The check gives a definite result (cross-referenced / modelled but not cross-referenced / not modelled) |

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

**`ASPECT_NOTES`**

| 键 | 中文 | English |
| --- | --- | --- |
| `onlyModelVersion` | 只有模型版本变了，不等于检查结果的内容变了。记录也不就“这条证据能否沿用到新版本”下结论。 | Only the model version changed; that does not mean the check result's content changed. Nor does the record conclude whether this evidence can carry over to the new version. |
| `semanticsSameOutcome` | 检查要求被修改过，检查结果读起来和原来一样——但它是按修改后的要求得出的，不能当作同一条证据。 | The check requirement was edited, and the check result reads the same as before — but it was reached under the edited requirement and cannot be treated as the same evidence. |
| `semanticsAndContent` | 检查要求被修改过，检查结果内容也变了：结果的变化可能来自要求的修改（例如要求放宽），不能据此说模型修好了。记录不说明要求是放宽还是收紧。 | The check requirement was edited and the check result content changed too: the change in result may come from the edit to the requirement (for example a relaxed requirement), so it cannot be taken to mean the model was fixed. The record does not say whether the requirement was relaxed or tightened. |
| `contentUnderSameRequirement` | 检查要求没有变，检查结果内容变了。这一行不记录结果是变好还是变差，请看当前判断。 | The check requirement did not change, and the check result content did. This row does not record whether the result got better or worse; see the current conclusion. |
| `checker` | 检查程序（检查器或它的配置）版本不同：同样的模型和要求也可能得出不同结果。 | The checker (the check program or its configuration) version differs: the same model and requirement may give a different result. |
| `unrecognised` | 含有未识别的变化方面，本页因此不列“未变”的方面。 | There is an unrecognised aspect of change, so this page does not list the unchanged aspects. |

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

**`CARRY_OVER_REASONS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `finding-equivalent` | 对应的检查结果只有一条，模型版本、检查结果内容、检查要求、检查程序逐项相同。 | There is exactly one corresponding check result; model version, check result content, check requirement and checker are the same, aspect by aspect. |
| `finding-changed` | 对应的检查结果只有一条，逐项比较后至少有一个方面不同。 | There is exactly one corresponding check result; compared aspect by aspect, at least one differs. |
| `no-counterpart-in-the-cited-run` | 本次记录依据的验证运行里，这个构件在这条要求下没有检查结果。 | In the validation run this record rests on, this element has no check result under this requirement. |
| `counterpart-not-cited-under-the-current-binding` | 验证运行里有对应的检查结果，但本次记录没有引用它。 | The validation run has a corresponding check result, but this record does not cite it. |
| `sealed-citation-has-no-comparison-basis` | 原记录封存时没有保存这条引用的比较依据（旧版本的记录）。本页不会用当前规则去补造，所以只能如实显示无法比较。 | When the original record was sealed it kept no comparison basis for this citation (a record from an older version). This page will not make one up from the current rules, so it can only say honestly that it cannot compare. |
| `comparison-basis-version-unknown` | 原记录保存的比较依据，是本系统不认识的版本。 | The comparison basis the original record kept is of a version this system does not recognise. |
| `subject-not-present` | 这条证据所针对的构件，在本次记录里已经不在（去向见“记录给出的原因”）。构件不在不等于已修复。 | The element this evidence is about is no longer in this record (where it went: see "the reason the record gives"). An element that is gone is not fixed. |
| `counterpart-not-unique` | 本次有不止一条候选的对应检查结果，系统不从中挑选（全部候选见“记录给出的原因”）。 | This time there is more than one candidate corresponding check result, and the system does not choose between them (all candidates: see "the reason the record gives"). |
| `requirement-semantics-basis-unavailable` | 封存一方或当前一方没有“检查要求”的比较依据。 | The sealed side or the current side has no comparison basis for the check requirement. |
| `comparison-basis-incomplete` | 封存一方或当前一方缺少部分比较依据（模型版本、检查结果内容摘要或检查程序指纹）。 | The sealed side or the current side lacks part of the comparison basis (model version, check result content digest or checker fingerprint). |
| `determination-same-reference-same-content` | 同一份判定：引用相同，内容摘要也相同。 | The same determination: the same reference and the same content digest. |
| `determination-content-changed-under-the-same-reference` | 引用相同，但判定的内容已经不是原记录读到的那一份（被重新作出、重新归属或重新签署）。新判定照常作为证据读取，只是不能说它和原判定是同一份。 | The same reference, but the determination's content is no longer what the original record read (made again, re-attributed or re-signed). The new determination is read as evidence as usual; it just cannot be called the same determination as the original. |
| `determination-not-cited-by-this-record` | 模型版本没有变，本次记录没有再引用这份判定；记录没有说明原因。 | The model version did not change, and this record no longer cites this determination; the record does not say why. |
| `determination-not-attributable-to-this-context` | 模型版本已经变化，原判定是针对旧版本作出的，不能归到当前版本。不是证据不存在，也不是原判定错误；需要针对当前版本的判定。 | The model version has changed, and the original determination was made against the old version, so it cannot be attributed to the current one. The evidence is not missing and the original determination is not wrong; a determination against the current version is needed. |

**`CARRY_OVER_STATES`**

| 键 | 中文 | English |
| --- | --- | --- |
| `equivalent.label` | 比较依据一致 | Comparison basis unchanged |
| `equivalent.meaning` | 这条旧证据在本次记录里有唯一对应的一条，逐项比较都相同。 | This old evidence has exactly one counterpart in this record, and every aspect compared is the same.  |
| `equivalent.caveat` | 这只说明不必因为引用换了键而重新收集这条证据，不代表整个交接不用复核。 | It only means the evidence need not be gathered again because its citation changed key; it does not mean the whole handover needs no review. |
| `changed.label` | 比较依据有变化 | Comparison basis changed |
| `changed.meaning` | 这条旧证据在本次记录里有唯一对应的一条，但至少有一个方面不同。 | This old evidence has exactly one counterpart in this record, but at least one aspect differs.  |
| `changed.caveat` | 结果读起来相同，也仍然算有变化；变了的是哪些方面，见这一条的说明。 | Even if the result reads the same, it still counts as changed; which aspects changed is said on the row. |
| `no-counterpart.label` | 未找到对应证据 | No counterpart found |
| `no-counterpart.meaning` | 可以比较，但本次记录没有引用与它对应的证据。 | It can be compared, but this record cites no evidence corresponding to it.  |
| `no-counterpart.caveat` | 没有对应证据不代表问题已修复。 | No counterpart does not mean the problem was fixed. |
| `not-provable.label` | 现有依据不足以比较 | Not enough basis to compare |
| `not-provable.meaning` | 比较本身无法建立，所以既不能说一致，也不能说变了。 | The comparison itself cannot be made, so it can be called neither unchanged nor changed.  |
| `not-provable.caveat` | 这是“无法比较”，不是“证据缺失”，也不是“没有对应证据”。 | This is "cannot be compared", not "evidence missing", and not "no counterpart". |

**`CHANGED_ASPECTS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `model-version` | 模型版本 | model version |
| `finding-content` | 检查结果内容 | check result content |
| `requirement-semantics` | 检查要求 | check requirement |
| `checker` | 检查程序 | checker |

**`CITATION_KINDS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `finding` | 检查结果引用 | Check-result citation |
| `determination` | 判定引用 | Determination citation |

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

**`CONDITION_ENTRIES`**

| 键 | 中文 | English |
| --- | --- | --- |
| `named-outcome-observed.text` | 仅命名结果已观察到；条件其余部分未检查 | Only the named outcome observed; the rest of the condition not checked |
| `named-outcome-observed.plain` | 原复检条件里点名的那个结果，现在观察到了。条件句的其余部分没有被机器检查，需要人对照原条件确认；这不是“整句条件已满足”。 | The outcome named in the original recheck condition is now observed. The rest of the condition was not checked by machine and needs a person to confirm it against the original condition; this is not "the whole condition is met". |
| `named-outcome-not-observed.text` | 未观察到命名结果 | Named outcome not observed |
| `named-outcome-not-observed.plain` | 原复检条件里点名的那个结果，现在没有观察到：原条件未达成。 | The outcome named in the original recheck condition is not observed now: the original condition is not reached. |
| `no-machine-checkable-part.text` | 条件没有可机检部分，需要人阅读 | The condition has no machine-checkable part; a person must read it |
| `no-machine-checkable-part.plain` | 原复检条件没有机器能检查的部分，需要人阅读原条件并判断；记录对它不下结论。 | The original recheck condition has no part a machine can check; a person needs to read the original condition and judge it. The record draws no conclusion on it. |
| `not-comparable.text` | 不可比较：对应的构件不完整 | Cannot be compared: the corresponding elements are incomplete |
| `not-comparable.plain` | 无法对原复检条件下结论：原来的构件有的已经不在本次记录里，条件没有完整的对象可以检查。这不代表条件已满足。 | No conclusion can be drawn on the original recheck condition: some of the original elements are no longer in this record, so the condition has no complete subject to check. This does not mean the condition is met. |
| `no-recheck-condition.text` | 原记录没有复检条件 | The original record had no recheck condition |
| `no-recheck-condition.plain` | 原记录没有复检条件：原来的判断没有留下待办。 | The original record had no recheck condition: the original conclusion left nothing outstanding. |
| `no-recheck-condition.plainNotReady` | 原记录没有给出复检条件。 | The original record gave no recheck condition. |

**`CONDITION_STATES`**

| 键 | 中文 | English |
| --- | --- | --- |
| `named-outcome-observed` | 仅命名结果已观察到；条件其余部分未检查 | Only the named outcome observed; the rest of the condition not checked |
| `named-outcome-not-observed` | 未观察到命名结果 | Named outcome not observed |
| `no-machine-checkable-part` | 条件没有可机检部分，需要人阅读 | The condition has no machine-checkable part; a person must read it |
| `not-comparable` | 不可比较：对应的构件不完整 | Cannot be compared: the corresponding elements are incomplete |
| `no-recheck-condition` | 原记录没有复检条件 | The original record had no recheck condition |

**`CONSEQUENCE_KINDS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `work-cannot-start` | 这项工作不能开始 | This work cannot start |
| `work-suspended` | 这项工作暂缓 | This work is on hold |
| `rework-risk` | 有返工风险 | Risk of rework |
| `re-identification-and-reissue-risk` | 有重新标识的风险：引用这些标识的文件届时也须重新出具 | Risk of re-identification: documents that cite these identifiers would then have to be reissued too |

**`DEMO_NOTICE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `DEMO_NOTICE` | 模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；一个结论的证据可能是真实检查的结果、模拟的检查结果或模拟的人工判定，具体是哪一种，看每个结论旁的“依据”一行（按逐条引用标明）。不能用于正式项目决定，也不能导出正式检查记录。 | Simulated example: the project settings in the example, including the handling teams and the acceptance of evidence methods, are demonstration settings, not real project decisions; the evidence for a conclusion may be a real check result, a simulated check result or a simulated human determination — which one, the "Basis" line beside each conclusion says (citation by citation). Not for formal project decisions, and no formal check record can be exported. |

**`DETAILS_WORDS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `heading` | 具体缺什么 | What exactly is missing |
| `absent` | 记录未提供：返回数据里没有这条引用的要求明细。 | Not given in the record: the returned data has no requirement details for this citation. |
| `determinations` | 这个结论引用的是人工判定，不是检查结果；判定没有要求明细。缺的是什么，见上面的结论和“要做什么”。 | This conclusion cites human determinations, not check results; a determination has no requirement details. What is missing is said in the conclusion and in "What to do" above. |
| `nothingCited` | 这个结论没有引用任何检查结果，所以没有要求明细可以显示。 | This conclusion cites no check result, so there are no requirement details to show. |
| `requirement` | 不满足的要求 | Requirement not met |
| `requirementMet` | 要求 | Requirement |
| `rule` | 规则编号 | Rule |
| `status` | 那次检查的结果 | Result of that check |
| `reason` | 原因 | Reason |
| `actual` | 那次检查观察到的值 | Value that check observed |
| `noActual` | 那次检查没有观察到值 | That check observed no value |
| `hasActual` | 那次检查观察到了值；本页不显示取值 | That check observed a value; this page does not show it |
| `expected` | 规则的原话（英文） | The rule's own words |
| `source` | 规则给出的出处（英文原文）： | Source the rule gives:  |
| `projectAssumption` | 这是本项目假定的要求（ProjectAssumption），不是通用要求。 | This is a requirement assumed for this project (ProjectAssumption), not a general one. |
| `gap` | 要填什么值、对应哪个 Revit 参数，记录未提供。 | What value to fill in, and which Revit parameter it maps to, the record does not say. |
| `prior` | 复检前那次评估时，这条证据的要求和结果如下。有这段说明不等于这一行可以比较；这一行的状态以上面写的为准。 | At the assessment before the recheck, this evidence's requirement and result were as follows. Having this description does not make the row comparable; the row's state is what is written above. |
| `currentAbsent` | 本次记录引用的对应证据：要求明细记录未提供。 | The corresponding evidence this record cites: its requirement details are not given in the record. |

**`DISPOSITIONS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `present` | 仍在本次检查范围内；判断与条件另看 | Still in this check's scope; conclusion and condition are read separately |
| `element-deleted-in-reissued-model` | 在重发模型中删除，不等于修复 | Deleted in the re-issued model; that is not a fix |
| `element-out-of-subject-class` | 已不属于此活动对象类别，不等于修复 | No longer of this activity's subject classes; that is not a fix |
| `pairing-no-longer-derived` | 这两个构件现在不再被配成一对来检查，不等于开洞已补 | These two elements are no longer paired for checking; that does not mean the opening was added |
| `outside-declared-scope` | 本次未声明该范围，不等于问题解除 | This scope was not declared this time; that does not mean the problem is gone |

**`DISPOSITION_ENTRIES`**

| 键 | 中文 | English |
| --- | --- | --- |
| `present.text` | 仍在本次检查范围内；判断与条件另看 | Still in this check's scope; conclusion and condition are read separately |
| `present.next` | 看下面记录给出的当前情况：现在的判断、下一步和处理角色都以它为准。 | See the current place the record gives below: the conclusion now, the next step and the handling role all follow it. |
| `element-deleted-in-reissued-model.text` | 在重发模型中删除，不等于修复 | Deleted in the re-issued model; that is not a fix |
| `element-deleted-in-reissued-model.next` | 记录没有为已删除的构件给出下一步。请在源模型里核对这次删除是不是有意的设计变更；本预览不能记录这种确认。 | The record gives no next step for a deleted element. Check in the source model whether this deletion was an intended design change; this preview cannot record that confirmation. |
| `element-out-of-subject-class.text` | 已不属于此活动对象类别，不等于修复 | No longer of this activity's subject classes; that is not a fix |
| `element-out-of-subject-class.next` | 记录没有为它给出下一步。请核对构件的类别（导出映射）是不是有意改变；类别变了只说明本活动不再检查它。 | The record gives no next step for it. Check whether the element's class (the export mapping) was changed on purpose; a changed class only means this activity no longer checks it. |
| `pairing-no-longer-derived.text` | 这两个构件现在不再被配成一对来检查，不等于开洞已补 | These two elements are no longer paired for checking; that does not mean the opening was added |
| `pairing-no-longer-derived.next` | 记录没有为这一对构件给出下一步。请核对让它不再被配对的原因（见“记录给出的原因”）；没有判定时，需要先作出针对当前版本的判定。原来的问题没有被证明已修复。 | The record gives no next step for this pair. Check the reason they are no longer paired (see "the reason the record gives"); where there is no determination, one against the current version has to be made first. The original problem has not been shown to be fixed. |
| `outside-declared-scope.text` | 本次未声明该范围，不等于问题解除 | This scope was not declared this time; that does not mean the problem is gone |
| `outside-declared-scope.next` | 这个构件本次没有被重新检查。需要结论时，要重新发起一次包含它的复检；本预览不能发起。 | This element was not checked again this time. For a conclusion, a new recheck that includes it is needed; this preview cannot start one. |

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

**`FINDING_STATUS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `FAIL` | 不通过 | Fail |
| `PASS` | 通过 | Pass |
| `N/A` | 不适用 | Not applicable |

**`HANDOVER_SIDES`**

| 键 | 中文 | English |
| --- | --- | --- |
| `producing` | 本次交接中交出方的模型 | the handing-over side's model in this handover |
| `consuming` | 本次交接中接收方的模型 | the receiving side's model in this handover |

**`HOME`**

| 键 | 中文 | English |
| --- | --- | --- |
| `title` | 查看模型交接中仍需处理的事项 | Items still to be dealt with in a model handover |
| `lede` | 帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。 | For a BIM manager: what a pre-handover check found; after a recheck, which conclusions changed, which items still need dealing with, which elements each one involves, what it rests on, and what to do next. |
| `status` | 当前为示例预览：Revit 文件本身（.rvt）不能导入，也不提供整体合规或可施工结论。 | This is an example preview: a Revit file itself (.rvt) cannot be imported, and it gives no overall compliance or ready-to-build conclusion. |
| `statusWithWorkspace` | 当前同时提供两样：启动服务器时指定的工作区里一次已经跑完的真实检查，以及模拟示例。工作区里的检查不能在页面上选择或更换模型；Revit 文件本身不能导入，也不提供整体合规或可施工结论。 | Two things are offered here: a real check already run in the workspace named when the server was started, and simulated examples. The workspace check cannot have its model chosen or changed on this page; a Revit file itself cannot be imported, and it gives no overall compliance or ready-to-build conclusion. |
| `statusWorkspaceUnknown` | 未能确认服务器是否指定了工作区，所以这里没有真实检查的入口；这不等于没有工作区，错误原文在下面。模拟示例照常可看。Revit 文件本身不能导入，也不提供整体合规或可施工结论。 | Could not confirm whether the server was started with a workspace, so there is no entry to a real check here; that does not mean there is no workspace — the error is below. The simulated examples are available as usual. A Revit file itself cannot be imported, and it gives no overall compliance or ready-to-build conclusion. |
| `example.title` | 看一个模拟示例 | Look at a simulated example |
| `example.body` | 从一次首次检查出发：找到需要处理的事项，看清涉及的构件、要做什么、由谁处理、完成后拿什么复检；然后再看同一事项复检后的变化。示例里模拟的内容，页面上逐处标明。 | Start from a first check: find the items that need dealing with, and see which elements they involve, what to do, who deals with it and what a recheck must show; then see how the same item changed after a recheck. What is simulated in the example is marked where it appears. |
| `example.action` | 选择模拟示例 | Choose a simulated example |
| `attempt.title` | 查看随附项目的检查尝试 | See the check attempt on the bundled project |
| `attempt.body` | 仓库随附一个样例项目。对它的检查尝试没有开始评估；这里说明原因。这个入口不是导入入口：只看这个样例项目，不能换成别的模型。 | The repository comes with a sample project. The check attempt on it did not start an assessment; this explains why. This entry is not an import: it shows only this sample project, and you cannot swap in another model. |
| `attempt.action` | 查看这次检查尝试 | See this check attempt |
| `cannot[0]` | 导入 Revit 文件本身（.rvt），或在示例和工作区入口里选择、更换模型 | Import a Revit file itself (.rvt), or choose or change the model in the example and workspace entries |
| `cannot[1]` | 给出整体合规、可施工或“可以交付”的结论 | Give an overall compliance, ready-to-build or "ready to hand over" conclusion |
| `cannot[2]` | 写回模型、上传到云端，或在 Revit 里打开构件 | Write back to a model, upload to the cloud, or open an element in Revit |
| `canHeading` | 现在可以做什么 | What you can do now |
| `recommended` | 推荐从这里开始 | Start here |
| `cannotHeading` | 现在还不能做什么 | What you cannot do yet |
| `cannotNote` | 这些功能没有实现，所以页面上没有对应的入口。 | These are not implemented, so the page has no entry for them. |

**`ITEM_UNIT`**

| 键 | 中文 | English |
| --- | --- | --- |
| `ITEM_UNIT` | 一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。同一个构件可以出现在几个事项里，所以事项数不是缺陷数。 | An item is the conclusion for one element (or a pair of elements assessed together) on one piece of the receiving side's work. The same element can appear in several items, so the number of items is not a number of defects. |

**`KEY_CHANGED`**

| 键 | 中文 | English |
| --- | --- | --- |
| `yes` | 引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 | The citation changed key (the new key is the "corresponding evidence this record cites" above). A change of key is not itself a change. |
| `no` | 引用的键没有换。 | The citation's key did not change. |

**`LEAF_READINGS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `asset-identity/satisfied` | 适用于它的项目资产标识要求评为通过，并且它确实被评估到 | The project asset-identity requirements that apply to it passed, and it was actually evaluated |
| `asset-identity/unmet` | 项目资产标识的要求没有满足 | The project asset-identity requirement is not met |
| `asset-identity/not-yet-evaluated` | 资产标识的规则没有覆盖到它 | The asset-identity rules did not cover it |
| `in-model-position/satisfied` | 它有楼层或空间归属 | It has a storey or space assignment |
| `in-model-position/unmet` | 它没有楼层或空间归属 | It has no storey or space assignment |
| `in-model-position/not-yet-evaluated` | 楼层或空间归属的检查没有覆盖到它 | The storey or space check did not cover it |
| `cross-model-alignment/confirmed` | 已有记录确认两侧模型对齐到共同的基准（按项目接受的方法，针对所列模型版本） | A record confirms the two models are aligned to a common datum (by the method the project accepts, for the listed model versions) |
| `cross-model-alignment/misaligned` | 对齐确认的结果是两侧模型没有对齐 | The alignment confirmation found the two models not aligned |
| `cross-model-alignment/not-yet-confirmed` | 还没有对齐确认 | No alignment confirmation yet |
| `penetration-determination/no-penetration` | 已有协调评审判定：它不穿过接收方模型里的任何构件。不穿过就不需要开洞，所以开洞情况没有被评估——这不是“开洞没问题” | A coordination-review determination says it passes through no element of the receiving model. With no penetration no opening is needed, so the opening was not assessed — this is not "the opening is fine" |
| `penetration-determination/penetration-confirmed` | 已有协调评审判定：它穿过接收方模型里的构件 | A coordination-review determination says it passes through elements of the receiving model |
| `penetration-determination/not-yet-determined` | 还没有协调评审判定它是否穿过接收方模型里的构件 | No coordination review has determined yet whether it passes through elements of the receiving model |
| `opening-status/cross-referenced` | 这一对：洞口已建在被穿过的构件上，并且已关联到穿过它的这个构件 | This pair: the opening is modelled in the element passed through, and linked to the element passing through it |
| `opening-status/modelled-not-cross-referenced` | 这一对：洞口已建在被穿过的构件上，但没有关联到穿过它的这个构件 | This pair: the opening is modelled in the element passed through, but not linked to the element passing through it |
| `opening-status/not-modelled` | 这一对：被穿过的构件上没有建出洞口 | This pair: no opening is modelled in the element passed through |
| `opening-status/not-yet-determined` | 这一对：开洞情况的评审还没有完成 | This pair: the review of the opening has not been completed yet |

**`LEAF_READING_WORDS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `label` | 这个结论依据的结果 | The result this conclusion rests on |
| `notCarried` | 记录没有给出这一项现在依据的结果 | The record does not give the result this item now rests on |
| `unglossed` | 本界面没有这个结果的中文说明，见追溯信息 | This interface has no English for this result; see the tracing details |

**`MODE_LABELS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `fixture` | 模拟示例 | Simulated example |
| `real` | 随附项目的检查尝试 | Check attempt on the bundled project |
| `workspace` | 工作区里的真实检查 | Real check in a workspace |

**`ONLY_REKEYED`**

| 键 | 中文 | English |
| --- | --- | --- |
| `ONLY_REKEYED` | 只是引用换了键 | Only the citation's key changed |

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

**`RECHECK`**

| 键 | 中文 | English |
| --- | --- | --- |
| `title` | 复检结果 | Recheck result |
| `notRecheck` | 这份记录不是复检记录，没有复检前后的对比可以显示。 | This record is not a recheck record, so there is no before-and-after to show. |
| `unknownSuccessor` | 这份记录承接了一条已封存的记录，但承接类型不是本页认识的复检：successor.kind =  | This record follows a sealed record, but not as a recheck this page recognises: successor.kind =  |
| `unknownSuccessorAfter` | 。本页不把它当作复检来呈现。 | . This page does not present it as a recheck. |
| `resultTitle` | 复检结果：需要处理的事项 | Recheck result: items to deal with |
| `summary.one` | 本次结果：共 {count} 个事项 | This result: {count} item |
| `summary.other` | 本次结果：共 {count} 个事项 | This result: {count} items |
| `groupLine.one` | {count} 个事项 | {count} item |
| `groupLine.other` | {count} 个事项 | {count} items |
| `groupSummary` | ：{summary} | : {summary} |
| `models` | 模型：{headline}。 | Models: {headline}. |
| `moved.one` | {count} 个事项的结论和复检前不同： | {count} item's conclusion differs from before the recheck: |
| `moved.other` | {count} 个事项的结论和复检前不同： | {count} items' conclusions differ from before the recheck: |
| `requirementChanged` | 复检前引用的 {count} 条旧证据里，有 {edited} 条的检查要求变了。 | Of the old evidence cited before the recheck ({count} in all), the check requirement changed for {edited}. |
| `groupHeading.one` | {label}（{count} 个事项） | {label} ({count} item) |
| `groupHeading.other` | {label}（{count} 个事项） | {label} ({count} items) |
| `cannotHeading` | 本预览做不了的事 | What this preview cannot do |
| `cannotNote` | 这些动作没有实现，所以页面上没有对应的按钮。 | These actions are not implemented, so the page has no buttons for them. |
| `limitsHeading` | 读复检结果时 | When reading a recheck result |
| `sideModel` | {side}模型 | {side} model |
| `detailsSummary` | 复检前后的比较明细：模型、事项、旧证据 | Before-and-after details: models, items, old evidence |
| `modelsHeading` | 模型 | Models |
| `itemsHeading.one` | 复检前记录里的事项（{count} 个），现在的情况 | The item in the record before the recheck ({count}), and where it stands now |
| `itemsHeading.other` | 复检前记录里的事项（{count} 个），现在的情况 | The items in the record before the recheck ({count}), and where they stand now |
| `evidenceHeading.one` | 复检前引用的旧证据（{count} 条），和本次记录比较的结果 | The old evidence cited before the recheck ({count} row), compared with this record |
| `evidenceHeading.other` | 复检前引用的旧证据（{count} 条），和本次记录比较的结果 | The old evidence cited before the recheck ({count} rows), compared with this record |
| `kindsNote` | 检查结果和人工判定是两种证据，分开计数，不相加。 | Check results and human determinations are two kinds of evidence, counted apart and never added together. |
| `traceSummary` | 追溯信息：记录标识、模型版本指纹、记录原码对照 | Tracing: record identity, model version fingerprints, record codes |
| `priorDigest` | 复检前记录的指纹（assessment digest） | Fingerprint of the record before the recheck (assessment digest) |
| `currentDigest` | 本记录的指纹（assessment digest） | Fingerprint of this record (assessment digest) |
| `noChange` | （记录中为空列表：没有模型变化） | (an empty list in the record: no model changed) |
| `versionColumns.side` |  | Side |
| `versionColumns.prior` | 复检前记录 | Record before the recheck |
| `versionColumns.current` | 本记录 | This record |
| `versionNote` | 版本以内容指纹表示，不以文件名当版本。哪一侧变了取自记录的 changed_models，本页不比较指纹。 | A version is a content fingerprint, not a file name. Which side changed is taken from the record's changed_models; this page does not compare fingerprints. |
| `glossaryDispositions` | 事项现在的情况：记录原码 | Where items stand now: record codes |
| `glossaryConditions` | 复检前留下的条件：状态原码（没有“整句条件已满足”） | Conditions left before the recheck: state codes (there is no "the whole condition is met") |
| `glossaryStates` | 旧证据比较：状态原码 | Old-evidence comparison: state codes |
| `glossaryReasons` | 旧证据比较：原因原码 | Old-evidence comparison: reason codes |
| `glossaryAspects` | 变化方面：原码 | Aspects that changed: codes |

**`RECHECK_CANNOT`**

| 键 | 中文 | English |
| --- | --- | --- |
| `[0]` | 发起新的复检或上传新模型 | Start a new recheck or upload a new model |
| `[1]` | 把事项标记为已解决、关闭或接受风险 | Mark an item resolved, closed or risk-accepted |
| `[2]` | 指派或通知责任人 | Assign or notify anyone |
| `[3]` | 在 Revit 中打开或定位构件 | Open or locate an element in Revit |
| `[4]` | 导出复检记录 | Export a recheck record |

**`RECHECK_ITEM`**

| 键 | 中文 | English |
| --- | --- | --- |
| `missing` | 复检记录中没有这一项 | The recheck record has no such item |
| `back` | ← 返回复检事项列表（回到这一项的位置） | ← Back to the recheck items (to this item's place) |
| `kicker` | 复检事项 · {count} | Recheck item · {count} |
| `pairNote` | 这两个构件已不再被配成一对检查：穿透判定现在不再把它们配对（现在的判定情况见下方记录给出的原因）。这不等于开洞已建成，也不等于开洞缺陷已修复。 | These two elements are no longer paired for checking: the penetration determination no longer pairs them (its current reading is in the reason the record gives below). This does not mean the opening has been built, nor that the opening defect has been fixed. |
| `model` | 模型 | Models |
| `actionHeading` | 二、要做什么、由谁处理、完成后拿什么复检 | 2. What to do, who deals with it, what a recheck must show |
| `whichOne` | 三、是哪个构件 | 3. Which element |
| `whichTwo` | 三、是哪两个构件 | 3. Which two elements |
| `noCurrent` | 记录没有给出这一项的当前情况，所以本页没有处理动作、处理团队或默认处理角色可以显示。复检前记录里的这些信息也没有随复检记录返回。 | The record does not give this item's current place, so this page has no action, handling team or default handling role to show. Those details from the record before the recheck did not come back with the recheck record either. |
| `conditionHeading` | 四、复检前留下的结束条件，这次达到了吗 | 4. Was the exit condition left before the recheck reached this time? |
| `priorCondition` | 复检前留下的结束条件：{text}。 | The exit condition left before the recheck: {text} |
| `end` | 。 | . |
| `conditionNote` | 这里只说复检前留下的结束条件被证明到了什么程度，与现在的结论分开读：结论变了，不等于原条件已满足。 | This says only how far the exit condition left before the recheck has been shown to be reached; read it apart from the conclusion now. A changed conclusion does not mean the original condition is met. |
| `changedCondition` | 结论变了，不等于原条件已满足。 | A changed conclusion does not mean the original condition is met. |
| `originalSummary` | 来源原文（英文）与记录原码：供追溯，不是操作指令 | Source wording and record codes: for tracing, not an instruction |
| `conditionBasis` | condition_basis（原文） | condition_basis (as written) |
| `evidenceHeading` | 五、复检前的证据 | 5. The evidence before the recheck |
| `evidenceCount.one` | 和这一项放在一起评估的旧证据共 {count} 条 | {count} piece of old evidence was assessed together with this item |
| `evidenceCount.other` | 和这一项放在一起评估的旧证据共 {count} 条 | {count} pieces of old evidence were assessed together with this item |
| `requirementChanged.one` | ，其中 {count} 条的检查要求变了 | , and for {count} of them the check requirement changed |
| `requirementChanged.other` | ，其中 {count} 条的检查要求变了 | , and for {count} of them the check requirement changed |
| `priorSources` | 复检前引用的证据，来源： | Evidence cited before the recheck, by source:  |
| `currentSources` | 本次记录引用的对应证据，来源： | Corresponding evidence this record cites, by source:  |
| `rowsSummary` | 逐条查看旧证据和比较结果 | See each piece of old evidence and how it compared |
| `shared.one` | 记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 {count} 个事项共用下面这些行。 | The record keeps the old evidence of a group of elements assessed together in one place, not split by element: the group's {count} item shares the rows below. |
| `shared.other` | 记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 {count} 个事项共用下面这些行。 | The record keeps the old evidence of a group of elements assessed together in one place, not split by element: the group's {count} items share the rows below. |
| `noEvidence` | 复检前这一组的证据路径没有引用任何证据。 | The group's evidence path before the recheck cites no evidence. |
| `priorOrdinal` | 复检前的内部分组编号 | Internal group number before the recheck |
| `currentLine` | 现在的内部分组编号、verdict 与终点 outcome | Current internal group number, verdict and final outcome |

**`RECHECK_LIMITS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `[0]` | “比较依据一致”不代表整个交接不用复核。 | "Comparison basis unchanged" does not mean the whole handover needs no review. |
| `[1]` | 构件不在了、或找不到对应证据，不代表问题已修复。 | An element that is gone, or evidence with no counterpart, does not mean the problem was fixed. |
| `[2]` | 模型重新发布（不论哪一侧）不代表修复已经发生。 | A model re-issued (on either side) does not mean a fix has happened. |
| `[3]` | “只有模型版本变了”不等于检查结果的内容变了。 | "Only the model version changed" does not mean the check result's content changed. |
| `[4]` | “无法比较”不是“证据缺失”：旧记录没保存比较依据时，本页如实显示无法比较。 | "Cannot be compared" is not "evidence missing": where the old record kept no comparison basis, this page says honestly that it cannot compare. |

**`REFUSAL_PAGE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `title` | 这次检查尝试没有开始评估 | This check attempt did not start an assessment |
| `lede` | 系统在评估开始前拒绝了这次请求，并给出了原因。这是对请求条件的答复：不是程序故障，也不是检查结果。 | The system refused this request before the assessment started, and gave its reason. This is an answer about the request's conditions: not a program fault, and not a check result. |
| `whyHeading` | 为什么没有开始 | Why it did not start |
| `needHeading` | 要让检查能够开始，需要什么 | What is needed for the check to start |
| `onlyOne` | 本次只返回这一个原因，没有其他环节的诊断。 | Only this one reason was returned; there is no diagnosis of any other stage. |
| `noConclusion` | 没有任何事项的结论、零问题统计或完成百分比；被拒绝不是“无法判断”，也不是一次没有问题的检查。 | No conclusion on any item, no zero-problem count and no completion ratio: a refusal is not "Unknown", and not a check without problems. |
| `original` | 系统返回的原文（英文）与拒绝码 | What the system returned (as written) and the refusal code |
| `attempt` | 检查尝试 | Check attempt |
| `code` | 拒绝码 | Refusal code |
| `contextMissing` | 所提交的请求上下文尚未随拒绝返回。 | The context of the request that was submitted has not been returned with the refusal yet. |

**`REFUSAL_REASONS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `team-mapping-decision-basis-illustrative.title` | 项目条件未满足：由谁处理的安排不是项目作出的决定 | Project condition not met: who deals with what is not a decision the project has made |
| `team-mapping-decision-basis-illustrative.text` | 这次请求所用的项目设定里，“哪个角色由哪个团队担任”的安排只是演示用的占位内容，不是项目作出的决定。系统因此不生成评估结果：否则结果里的处理团队会被当成项目的真实安排。 | In the project settings this request used, the arrangement of which team fills which role is demonstration placeholder content, not a decision the project has made. The system therefore produces no assessment: otherwise the handling teams in the result would be taken for the project's real arrangement. |
| `team-mapping-decision-basis-illustrative.action[0]` | 在一个真实项目上，要让检查能够开始：需要项目负责人实际决定系统原文（折叠在下面）点名的每个角色由谁担任，然后如实记录。这是一个人员决定，不是改一个标签。 | On a real project, for the check to be able to start: the project lead has to actually decide who fills each role that the system's own text (folded below) names, and record it as decided. This is a staffing decision, not a change of label. |
| `team-mapping-decision-basis-illustrative.action[1]` | 如果这次请求用的是随附的公开样例：它没有项目负责人。对它而言，这次拒绝就是正确的结果，不需要、也不应该去改它的设定。 | If this request used the bundled public sample: it has no project lead. For it, this refusal is the correct result; its settings do not need to be changed, and should not be. |

**`REFUSAL_SCOPE_NOTE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `REFUSAL_SCOPE_NOTE` | 处理当前拒绝原因不保证随后可评估；其余限制尚未由本次运行验证。 | Dealing with the current reason for refusal does not guarantee that an assessment can follow; the other limitations have not been verified by this run. |

**`REISSUE_CASES`**

| 键 | 中文 | English |
| --- | --- | --- |
| `none.headline` | 两侧模型都没有重新发布（版本未变） | Neither model was re-issued (versions unchanged) |
| `none.detail` | 本次复检和原记录用的是同一对模型版本，所以下面的差异不来自模型改动。 | This recheck uses the same pair of model versions as the original record, so the differences below do not come from model edits. |
| `producing.headline` | 交出方的模型重新发布了，接收方的模型没有变 | The handing-over side's model was re-issued; the receiving side's model did not change |
| `producing.detail` | 交出方（{from}）的模型 {producing} 是新版本；接收方（{to}）的模型 {consuming} 还是原版本。 | The handing-over side's ({from}) model {producing} is a new version; the receiving side's ({to}) model {consuming} is the original version. |
| `producing.caveats[0]` | 交出方重新发布可能改变了穿越关系或涉及的构件范围，不能据此说接收方的工作（例如开洞）已经做好。 | Re-issuing on the handing-over side may have changed what passes through what, or which elements are involved; it cannot be taken to mean the receiving side's work (for example the openings) is done. |
| `producing.caveats[1]` | 针对旧版本作出的判定不能归到新版本。 | A determination made against an old version cannot be attributed to the new one. |
| `consuming.headline` | 接收方的模型重新发布了，交出方的模型没有变 | The receiving side's model was re-issued; the handing-over side's model did not change |
| `consuming.detail` | 接收方（{to}）的模型 {consuming} 是新版本；交出方（{from}）的模型 {producing} 还是原版本。 | The receiving side's ({to}) model {consuming} is a new version; the handing-over side's ({from}) model {producing} is the original version. |
| `consuming.caveats[0]` | 接收方重新发布可能是修复的途径，但不代表修复已经发生（例如洞口已完成）。 | Re-issuing on the receiving side may be the way to a fix, but it does not mean the fix has happened (for example that the opening is complete). |
| `consuming.caveats[1]` | 针对旧版本作出的判定同样不能归到新版本。 | Likewise, a determination made against an old version cannot be attributed to the new one. |
| `both.headline` | 交出方和接收方的模型都重新发布了 | Both the handing-over and the receiving side's models were re-issued |
| `both.detail` | 交出方（{from}）的模型 {producing} 和接收方（{to}）的模型 {consuming} 都是新版本。 | The handing-over side's ({from}) model {producing} and the receiving side's ({to}) model {consuming} are both new versions. |
| `both.caveats[0]` | 两侧同时变化：本页不把任何一条证据的变化归到某一侧。 | Both sides changed at once: this page attributes no change in any evidence to either side. |
| `both.caveats[1]` | 重新发布不代表修复已经发生；针对旧版本作出的判定不能归到新版本。 | A re-issue does not mean a fix has happened; a determination made against an old version cannot be attributed to the new one. |
| `unrecognised.headline` | 记录的模型版本比较无法识别，按原值显示 | The record's model version comparison cannot be recognised; shown as it came |
| `unrecognised.detail` | 记录给出的变化模型与本记录的交出方、接收方对不上，或两个字段互相矛盾。本页不猜是哪一侧。 | The changed models the record gives do not match this record's handing-over and receiving sides, or the two fields contradict each other. This page does not guess which side. |

**`REISSUE_NEUTRAL`**

| 键 | 中文 | English |
| --- | --- | --- |
| `REISSUE_NEUTRAL` | 本页只说明哪一侧变了、记录证明了什么，不根据重新发布的方向预判好坏。 | This page only says which side changed and what the record shows; it does not judge good or bad from the direction of a re-issue. |

**`REQUIREMENT_CHANGED_NOTE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `REQUIREMENT_CHANGED_NOTE` | 记录同时显示：和这一项放在一起评估的旧证据里，有 {count} 条的检查要求变了；记录不说明是放宽还是收紧。读这个结论时要一并看，逐条见“复检前的证据”。 | The record also shows that, among the old evidence assessed together with this item, the check requirement changed for {count}; the record does not say whether it was relaxed or tightened. Read this conclusion with that in mind; row by row, see "The evidence before the recheck". |

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

**`RULE_NOTES`**

| 键 | 中文 | English |
| --- | --- | --- |
| `PV-001.title` | 风口要声明四种预定义类型之一 | Air terminals declare one of four predefined types |
| `PV-001.predicate` | 每个适用的风口（IfcAirTerminal）都要声明预定义类型，取值是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一。IFC4 还允许 USERDEFINED 和 NOTDEFINED；不接受它们是这条规则自己的决定，用它们的模型仍是有效的 IFC4。 | Every applicable air terminal (IfcAirTerminal) declares a predefined type of DIFFUSER, GRILLE, LOUVRE or REGISTER. IFC4 also admits USERDEFINED and NOTDEFINED; not accepting them is this rule's own decision, and a model using them is still valid IFC4. |
| `PV-001.passProves` | 检查器按它的读取顺序取到的那一个值（类型上的值优先；类型声明 USERDEFINED 时是它的自由文本；类型什么也没说（没有类型、NOTDEFINED，或 USERDEFINED 没写文本）时才读构件实例，实例声明 USERDEFINED 时也是它的自由文本），逐字等于 DIFFUSER、GRILLE、LOUVRE、REGISTER 四个值之一。 | The one value the checker took in its reading order (the type's value first; a USERDEFINED type's free text; the element instance only when the type says nothing (no type, NOTDEFINED, or USERDEFINED with no text), and then a USERDEFINED instance's free text too) is, character for character, one of DIFFUSER, GRILLE, LOUVRE and REGISTER. |
| `PV-001.passDoesNotProve[0]` | 取值正确：四个值中任何一个都会通过，写成 GRILLE 也会通过。 | That the value is right: any of the four passes; GRILLE passes too. |
| `PV-001.passDoesNotProve[1]` | 类型和构件实例的取值一致：类型上是四个值之一时，实例上写的值不参与比较；类型是 LOUVRE、实例是 DIFFUSER，也会通过。 | That the type and the element instance agree: when the type carries one of the four, the instance's value is not compared; type LOUVRE with instance DIFFUSER also passes. |
| `PV-001.passDoesNotProve[2]` | 规则不接受的 USERDEFINED 没有出现：类型声明 USERDEFINED 时，检查器比较的是它的自由文本；类型什么也没说（没有类型、NOTDEFINED，或 USERDEFINED 没写文本）时，构件实例声明 USERDEFINED 也按它的自由文本比较。比较逐字、区分大小写；文本恰好是 LOUVRE 会通过，写成 louvre、Louvre 或前后带空格则不通过。 | That no USERDEFINED, which the rule does not accept, is present: when the type declares USERDEFINED, the checker compares its free text; when the type says nothing (no type, NOTDEFINED, or USERDEFINED with no text), an element instance that declares USERDEFINED is compared by its free text as well. The comparison is character for character and case-sensitive; text that happens to be LOUVRE passes, while louvre, Louvre or text with leading or trailing spaces does not. |
| `PV-001.passDoesNotProve[3]` | 墙上有对应的洞口。 | That the wall has a corresponding opening. |
| `PV-001.passDoesNotProve[4]` | 风口所在的模型与风口所在的墙所属的模型已经对齐。 | That the air terminal's model and the model of the wall it sits in are aligned. |
| `PV-001.passDoesNotProve[5]` | 任何工作可以开始，包括吊顶和开洞工作。 | That any work can start, including ceiling and opening work. |
| `PV-001.action.what` | 回到 Revit 源模型，让这个风口导出后的预定义类型是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一；重新导出 IFC，再检查。NOTDEFINED 等于什么都没说。 | Go back to the Revit source model and make this air terminal's exported predefined type one of DIFFUSER, GRILLE, LOUVRE and REGISTER; re-export the IFC and check again. NOTDEFINED states nothing. |
| `PV-001.action.reads` | 检查器先看导出的 IFC 里它的类型对象：类型上是四个值之一，比较类型上的值；类型声明 USERDEFINED，比较它的自由文本；类型什么也没说时，才读构件实例本身的值。这说的是检查器读 IFC 的顺序，不是 Revit 里该改的位置。 | The checker looks first at its type object in the exported IFC: if the type carries one of the four, the type's value is compared; if the type declares USERDEFINED, its free text is compared; only when the type says nothing is the element instance's own value read. This is the order in which the checker reads the IFC, not where to make the change in Revit. |
| `PV-001.action.revise` | 这个值在 Revit 里从哪里写出（类型还是实例、哪个参数、哪项导出设置），返回数据没有记录，本页不指定。改之前先在 Revit 里确认；如果决定在类型上改，会作用于这个类型的全部实例。一个 Revit 类型可能对应不止一个 IFC 类型对象，实例数按 Revit 类型算。 | Where this value is written from in Revit (type or instance, which parameter, which export setting), the returned data does not record, and this page does not say. Confirm it in Revit before changing anything; if you decide to change it on the type, the change applies to every instance of that type. One Revit type may correspond to more than one IFC type object; count instances by the Revit type. |
| `PV-001.action.undecided` | 取哪一个值、由谁决定和操作，返回数据都没有提供。规则只要求四个值之一，不判断哪一个对。 | Which value to use, and who decides and makes the change, the returned data does not say. The rule asks only for one of the four values and does not judge which is right. |
| `PV-001.recheck` | 用同一规则集版本、同一组模型和同一导出设置重新检查，看这个构件在这条要求下的结果。 | Check again with the same rule set version, the same set of models and the same export settings, and look at this element's result under this requirement. |
| `PV-001.gaps[0]` | 风口所在的墙上的洞口：需要对照风口所在的模型和这面墙所属的模型做协调评审判定；这项检查不比较两个模型的构件。 | The opening in the wall the air terminal sits in: a coordination-review determination is needed, made against the air terminal's model and the model of that wall; this check does not compare elements across the two models. |
| `PV-001.gaps[1]` | 风口所在的模型与风口所在的墙所属的模型是否对齐：需要一份对齐确认记录。 | Whether the air terminal's model and the model of the wall it sits in are aligned: an alignment confirmation record is needed. |
| `PV-001.gaps[2]` | 取值是否选对：分类判断要另行记录；检查通过不能反过来证明分类判断正确。 | Whether the value chosen is right: the classification decision has to be recorded separately; a pass cannot prove in reverse that the classification is right. |
| `PV-001.reasonFreeText` | 引号里不是预定义类型的枚举值，而是自由文本：类型声明 USERDEFINED 时，检查器拿它的自由文本来比较；类型什么也没说（没有类型、NOTDEFINED，或 USERDEFINED 没写文本）时，构件实例声明 USERDEFINED 也是这样。 | What is in the quotation marks is not an enumeration value but free text: when the type declares USERDEFINED, the checker compares its free text; when the type says nothing (no type, NOTDEFINED, or USERDEFINED with no text), the same holds for an element instance that declares USERDEFINED. |

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

**`SOURCE_SUMMARY`** —— 示例页页首的短摘要，`DEMO_NOTICE` 是展开后的全文。`cites` 只列这份记录的引用里实际出现的来源种类（逐条引用自己判定），所以混合来源不会被说成“全部真实”或“全部模拟”

| 键 | 中文 | English |
| --- | --- | --- |
| `lead` | 随附的模拟示例，不是你的模型；团队和证据方法的接受等项目设定为演示用，不能用于正式项目决定。 | A simulated example shipped with the tool, not your model; project settings such as teams and the acceptance of evidence methods are for demonstration, not for formal project decisions. |
| `cites` | 这份记录的结论引用了：{kinds}，逐条标在结论旁的“依据”一行。 | This record's conclusions cite {kinds}, labelled citation by citation on the "Basis" line beside each conclusion. |
| `citesNone` | 这份记录的结论没有引用证据。 | This record's conclusions cite no evidence. |
| `noRecord` | 结论引用的证据是真实的还是模拟的，逐条标在结论旁的“依据”一行。 | Whether the evidence a conclusion cites is real or simulated is labelled citation by citation on the "Basis" line beside it. |
| `kinds.finding-real` | 真实检查输出 | real check output |
| `kinds.finding-fixture` | 模拟的检查结果 | simulated check results |
| `kinds.determination-fixture` | 模拟的人工判定 | simulated human determinations |
| `kinds.determination-unmarked` | 来源未标注的判定 | determinations of unstated source |
| `join` | `、` | `, `（逗号加空格） |
| `lastJoin` | `、` | ` and `（前后各一个空格） |
| `more` | 来源说明 | About the sources |

**`TAG_WORDS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `note` | IFC Tag 是导出时写进 IFC 的标记；Revit 导出的通常是构件的 ElementId。核对：在 Revit 里用“按 ID 选择”选中这个 ID，看选中对象的名称和类别是否与本页相同；相同再按它处理，不同就不要按这个 Tag 去改：在 IFC 查看器里按 GlobalId 定位，读出名称、类型和位置，再在 Revit 里按这些找到对象并核对，然后在源模型里修改。 | The IFC Tag is a marker written into the IFC at export; what Revit writes is usually the element's ElementId. To check: in Revit, use "Select by ID" with this ID and see whether the selected object's name and class match this page; if they do, work from it; if they do not, do not change anything by this Tag: locate the object by its GlobalId in an IFC viewer, read its name, type and location, find the object in Revit by these and check it, then make the change in the source model. |
| `byIdNotStorey` | 在 Revit 里按 ID 找对象，不要按楼层找：本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上。 | Find the object in Revit by its ID, not by storey: the storey on this page is the IFC file's spatial assignment, which may not match the levels in a Revit schedule. |
| `storeyFromIfc` | 本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上，不要只按楼层去找。 | The storey on this page is the IFC file's spatial assignment, which may not match the levels in a Revit schedule; do not look for the object by storey alone. |
| `sources.model-file` | 模型文件里这个构件没有写 Tag。 | The model file has no Tag for this element. |
| `sources.model-file-not-located` | 没有找到这次检查读的那个模型文件，所以读不到 Tag。 | The model file this check read was not found, so the Tag cannot be read. |
| `sources.model-file-differs` | 工作区里的模型文件已经不是这次检查读的那个版本，所以不读取 Tag。 | The model file in the workspace is no longer the version this check read, so the Tag is not read. |
| `sourceNotCarried` | 返回数据没有说明这个模型的 Tag 从哪里读，所以没有 Tag。 | The returned data does not say where this model's Tags are read from, so there is no Tag. |
| `modelLevel` | 这条结果针对整个模型，没有具体构件可找。 | This result is about the whole model; there is no single element to find. |
| `useGlobalId` | 在 IFC 里定位用 GlobalId。 | To find it in the IFC, use the GlobalId. |
| `short.model-file` | 文件里没有 Tag | No Tag in the file |
| `short.model-file-not-located` | 未找到模型文件 | Model file not found |
| `short.model-file-differs` | 模型文件版本不同 | Model file version differs |
| `short.notCarried` | 来源未说明 | Source not stated |
| `short.modelLevel` | 整个模型 | Whole model |

**`VERDICT_GROUPS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `changed.label` | 判断变了的 | Conclusions that changed |
| `changed.none` | 没有判断变了的项。 | No conclusion changed. |
| `changed.notes.none` | 两侧模型都没有重新发布，这些项的判断却变了：变化不来自模型改动。每一项的旧证据写明变了的是什么。 | Neither model was re-issued, yet these conclusions changed: the change does not come from a model edit. Each item's old evidence says what changed. |
| `changed.notes.reissued` | 模型重新发布过。判断变了，不说明原来的问题怎样了；每一项的旧证据写明变了的是什么。 | A model was re-issued. A changed conclusion does not say what became of the original problem; each item's old evidence says what changed. |
| `changed.notes.unrecognised` | 判断变了，不说明原来的问题怎样了；每一项的旧证据写明变了的是什么。 | A changed conclusion does not say what became of the original problem; each item's old evidence says what changed. |
| `unplaced.label` | 记录没有给出当前情况的 | Items whose current place the record does not give |
| `unplaced.none` | 每一项记录都给出了当前情况。 | The record gives a current place for every item. |
| `unplaced.note` | 这些项现在是什么判断，记录没有说。构件不在了不代表问题已修复。 | The record does not say what these items' conclusions are now. An element that is gone does not mean the problem was fixed. |
| `unchanged.label` | 判断没有变的 | Conclusions that did not change |
| `unchanged.none` | 没有判断保持不变的项。 | No conclusion stayed the same. |
| `unchanged.note` | 判断没有变，不代表证据没有变；旧证据的情况见每一项。 | An unchanged conclusion does not mean the evidence is unchanged; see each item for the old evidence. |

**`VERDICT_SCOPE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `VERDICT_SCOPE` | 每个判断只针对接收方的一项工作、本次评估范围内的这一项，以及所列的模型版本；它不是“模型好不好”的总评，也不是“某项检查通过了”。 | Each conclusion is about one piece of the receiving side's work, this item within this assessment's scope, and the listed model versions; it is not an overall verdict on whether the model is good, nor a statement that some check passed. |

**`WORKSPACE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `directoryNote` | 工作区只能在启动服务器时指定；这里不能选择、上传或更换模型。 | A workspace can only be named when the server is started; you cannot choose, upload or change a model here. |
| `directoryNone` | 服务器启动时没有指定工作区，所以这里没有可以查看的检查。要查看，用下面的命令重新启动服务器： | The server was started without a workspace, so there is no check to look at here. To look at one, restart the server with this command: |
| `startCommand` | python doctor/serve.py --workspace <工作区目录> [--prior <前一次运行的目录>] | python doctor/serve.py --workspace <workspace directory> [--prior <earlier run directory>] |
| `openRun` | 打开这次检查的结果 | Open this check's results |
| `back` | ← 返回首页 | ← Back to the home page |
| `backToList` | ← 返回结果列表 | ← Back to the list of results |
| `contextNoJudgement` | 只有检查结果，没有交接判断 | Check results only, no handover judgement |
| `contextRun` | 检查运行 | Check run |
| `resultTitle` | 一次真实检查的结果 | Results of a real check |
| `noJudgement` | 这是一次检查的结果，不是交接判断：页面只说每个构件在每条要求下通过、不通过还是不适用，不对任何工作能否开始下结论。 | These are the results of a check, not a handover judgement: the page says only whether each element passed, failed or was not applicable under each requirement, and concludes nothing about whether any work can start. |
| `summary.one` | 本次结果：共 {count} 条检查结果 | This result: {count} check result |
| `summary.other` | 本次结果：共 {count} 条检查结果 | This result: {count} check results |
| `unit` | 单位是条：一条是一个构件在一条要求下的结果；模型里没有这条要求适用的构件时，是整个模型的一条。 | The unit is one result: one element under one requirement; where a model has no element the requirement applies to, it is one result for the whole model. |
| `compareLink` | 看与前一次运行的对比 | See the comparison with the earlier run |
| `compareTeaser` | 服务器启动时还指定了前一次运行。两次结果的前后对比： | The server was also started with an earlier run. Before and after: |
| `checkedHeading` | 检查了什么 | What was checked |
| `ruleTitle` | 要求 | Requirement |
| `rulePredicate` | 这条规则要求 | What this rule asks |
| `ruleExpected` | 规则的原话（英文） | The rule's own words |
| `ruleOrigin` | 出处（返回数据的引文，英文原文） | Source (the returned data's citation, as written) |
| `ruleLabels` | 返回数据的标签 | Labels in the returned data |
| `productValidation` | 返回数据的标签（ProductValidation）标明：这是一条产品验证规则。 | The label in the returned data (ProductValidation) says: this is a product validation rule. |
| `noRuleNotes` | 本界面没有为这条规则写中文说明；规则以返回数据里的英文原话为准。 | This interface has written no notes for this rule; the rule's own words in the returned data are what counts. |
| `noRequirement` | 返回数据没有这条结果所属要求的说明。 | The returned data has no description of the requirement this result belongs to. |
| `listHeading` | 逐条结果 | Results, one by one |
| `filterLabel` | 按 IFC Tag、名称或 GlobalId 查找 | Find by IFC Tag, name or GlobalId |
| `filterAll` | 全部 | All |
| `filterNone` | 没有符合筛选条件的结果。 | No result matches the filter. |
| `filterShown` | 显示 {shown} 条，共 {count} 条 | Showing {shown} of {count} |
| `columns.status` | 结果 | Result |
| `columns.tag` | IFC Tag | IFC Tag |
| `columns.name` | 名称 | Name |
| `columns.class` | 类别 | Class |
| `columns.storey` | 楼层（IFC） | Storey (IFC) |
| `columns.model` | 模型 | Model |
| `pickOne` | 从结果列表里选一条，在这里看它的详情。 | Choose a result from the list to see its details here. |
| `detailKicker` | 一条真实检查结果 | One result of a real check |
| `wholeModel` | 整个模型 | Whole model |
| `resultHeading` | 结果 | Result |
| `findHeading` | 回到 Revit 找哪个对象 | Which object to find in Revit |
| `actionHeading` | 要改什么 | What to change |
| `actionWhat` | 改成什么 | Change it to |
| `actionReads` | 检查器读哪里 | Where the checker reads |
| `actionRevise` | 在 Revit 里改哪里 | Where to change it in Revit |
| `actionUndecided` | 还没有决定的 | Not decided yet |
| `requirementHeading` | 具体要求与这次检查的观察 | The requirement, and what this check observed |
| `reason` | 原因（检查结果的原文） | Reason (as the check result gives it) |
| `actual` | 观察值一栏 | Observed value |
| `actualEmpty` | 检查结果中为空。 | Empty in the check result. |
| `actualHidden` | 检查结果带有观察值；本页不显示取值。 | The check result carries an observed value; this page does not show it. |
| `recheckHeading` | 复检时看什么 | What to look at in a recheck |
| `passHeading` | 这条通过证明了什么 | What this pass proves |
| `passProves` | 它证明： | It proves:  |
| `passDoesNotProve` | 它不证明： | It does not prove: |
| `passNoValue` | 通过的检查结果不带它读到的值：只记录了“要求已满足”。 | A passing check result does not carry the value it read: it records only "Requirement satisfied." |
| `passUnwritten` | 通过只说明这条要求被判为满足；它能证明到哪里，本界面没有为这条规则写说明，请看规则原话。 | A pass says only that this requirement was judged met; how far that goes, this interface has written no notes for this rule — see the rule's own words. |
| `notApplicable` | 不适用：这个模型里没有这条要求适用的构件。不适用不是通过。 | Not applicable: this model has no element the requirement applies to. Not applicable is not a pass. |
| `failNotDefect` | 不满足这条产品验证规则，不等于原项目的交付缺陷。这条规则的来源以返回数据的标签（ProductValidation）和出处原文为准。 | Not meeting this product validation rule is not a delivery defect of the original project. Where this rule comes from is what the returned data's label (ProductValidation) and the citation as written say. |
| `noFinding` | 这次检查里没有这一条结果。 | This check has no such result. |
| `identityHeading` | 追溯信息：这次检查的运行号、规则集版本与模型文件 | Tracing: this check's run identifier, rule set version and model files |
| `findingTrace` | 追溯信息：这条结果的内部键 | Tracing: this result's internal keys |
| `identity.run` | 检查运行号 | Check run identifier |
| `identity.ruleset` | 规则集 | Rule set |
| `identity.asOf` | 逻辑日期（运行配置给定，不是运行的时间） | Logical date (given by the run configuration, not when it ran) |
| `identity.checkers` | 检查程序 | Checkers |
| `identity.models` | 模型 | Models |
| `identity.modelId` | 模型 | Model |
| `identity.declaredDiscipline` | 项目清单声明的专业 | Discipline declared in the project manifest |
| `identity.filename` | 文件 | File |
| `identity.digest` | 文件内容摘要（SHA-256） | File content digest (SHA-256) |
| `identity.tagSource` | IFC Tag 的来源 | Where the IFC Tag comes from |
| `identity.elementKey` | 追溯用内部键 | Internal key for tracing |
| `identity.findingKey` | 检查结果键 | Check result key |
| `identity.requirementKey` | 要求键 | Requirement key |
| `element.name` | 名称 | Name |
| `element.class` | 类别 | Class |
| `element.storey` | 楼层（IFC） | Storey (IFC) |
| `element.model` | 所属模型 | Model |
| `element.file` | 模型文件 | Model file |
| `element.globalId` | GlobalId | GlobalId |

**`WORKSPACE_COMPARE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `title` | 复检对比：同一项检查，前后两次运行 | Recheck comparison: the same check, two runs |
| `lede` | 下面的配对、未再评估和新出现都由返回数据给出，页面只计数和排列。 | The pairs, the rows not re-evaluated and the newly appearing rows below are the returned data's; the page only counts and arranges them. |
| `runsHeading` | 两次运行 | The two runs |
| `prior` | 被指定为前一次的运行（启动时用 --prior 指定） | The run named as the earlier one (given with --prior at start-up) |
| `current` | 本次运行（启动时用 --workspace 指定） | This run (given with --workspace at start-up) |
| `order` | 哪一次在前，是启动服务器时的指定；返回数据本身不能证明先后。 | Which run came first is what the server was told at start-up; the returned data itself cannot prove the order. |
| `same` | 两次运行的规则集、各条要求的谓词、检查程序、逻辑日期和模型组都相同；其中任何一项不同，系统都会拒绝对比，不给出任何一侧的结果。 | The two runs have the same rule set, the same predicate for each requirement, the same checkers, the same logical date and the same set of models; were any of them different, the system would refuse the comparison and give neither side's results. |
| `changedHeading` | 一、什么变了 | 1. What changed |
| `differs.one` | 两次结果不同的：{count} 条 | Results that differ between the runs: {count} |
| `differs.other` | 两次结果不同的：{count} 条 | Results that differ between the runs: {count} |
| `differsNone` | 没有两次结果不同的。 | No result differs between the runs. |
| `unchanged.one` | 两次结果相同的：{count} 条 | Results that are the same in both runs: {count} |
| `unchanged.other` | 两次结果相同的：{count} 条 | Results that are the same in both runs: {count} |
| `unchangedNone` | 没有两次结果相同的。 | No result is the same in both runs. |
| `transition.one` | {prior} → {current}：{count} 条 | {prior} → {current}: {count} row |
| `transition.other` | {prior} → {current}：{count} 条 | {prior} → {current}: {count} rows |
| `rows.one` | {count} 条 | {count} row |
| `rows.other` | {count} 条 | {count} rows |
| `notReEvaluated.label.one` | 只在前一次有结果的（本次没有再评估）：{count} 条 | With a result in the earlier run only (not re-evaluated this time): {count} |
| `notReEvaluated.label.other` | 只在前一次有结果的（本次没有再评估）：{count} 条 | With a result in the earlier run only (not re-evaluated this time): {count} |
| `notReEvaluated.note` | 这些只有前一次的结果，本次没有再评估。它们不是通过。 | These have a result from the earlier run only and were not re-evaluated this time. They are not passes. |
| `newlyAppearing.label.one` | 只在本次有结果的（新出现）：{count} 条 | With a result in this run only (newly appearing): {count} |
| `newlyAppearing.label.other` | 只在本次有结果的（新出现）：{count} 条 | With a result in this run only (newly appearing): {count} |
| `newlyAppearing.note` | 这些结果前一次没有。 | The earlier run did not have these results. |
| `inCurrent.true` | 构件还在本次的构件清单里 | The element is still in this run's list of elements |
| `inCurrent.false` | 构件不在本次的构件清单里 | The element is not in this run's list of elements |
| `inCurrent.null` | 整个模型的一条结果，不针对构件 | A result for the whole model, not for an element |
| `inPrior.true` | 构件在前一次的构件清单里 | The element is in the earlier run's list of elements |
| `inPrior.false` | 构件不在前一次的构件清单里 | The element is not in the earlier run's list of elements |
| `inPrior.null` | 整个模型的一条结果，不针对构件 | A result for the whole model, not for an element |
| `whyHeading` | 二、为什么会变：返回数据能说明的部分 | 2. Why it changed: what the returned data can say |
| `changedModels` | 两次之间内容变了的模型（返回数据列出）： | Models whose content changed between the runs (listed by the returned data): |
| `noChangedModels` | 返回数据没有列出内容变了的模型：两次读的是同样的模型文件。 | The returned data lists no model whose content changed: both runs read the same model files. |
| `unchangedModels` | 内容未变的模型： | Models whose content did not change: |
| `why` | 两次的规则集、要求谓词、检查程序和逻辑日期都相同。在返回数据比较过的这些输入里，两次之间不同的只有上面列出的模型文件内容；模型文件里改了哪些地方，返回数据没有逐项列出。 | The two runs have the same rule set, requirement predicates, checkers and logical date. Of the inputs the returned data compared, the only difference between the runs is the content of the model files listed above; what changed inside those files, the returned data does not list item by item. |
| `notInData` | 在 Revit 里改了什么、取值由谁决定、由谁操作，返回数据没有记录。 | What was changed in Revit, who decided the value and who made the change, the returned data does not record. |
| `gapsHeading` | 三、还缺什么证据 | 3. What evidence is still missing |
| `passLink` | 一条通过证明了什么、没证明什么，见通过那几条的详情。 | What a pass proves and does not prove: see the details of the passing results. |
| `open` | 查看 | Open |
| `detailHeading` | 和前一次运行比 | Compared with the earlier run |
| `detailPrior` | 前一次的结果 | Earlier result |
| `detailCurrent` | 本次的结果 | This result |
| `detailNewly` | 前一次运行没有这一条结果：它是新出现的。 | The earlier run has no such result: it is newly appearing. |
| `detailNone` | 返回数据的对比里没有这一条。 | The returned data's comparison does not include this result. |
| `priorReason` | 前一次的原因（原文） | Earlier reason (as written) |
| `currentReason` | 本次的原因（原文） | This reason (as written) |
| `noComparison` | 服务器启动时没有指定前一次运行，所以没有对比。要对比，启动时加上 --prior。 | The server was started without an earlier run, so there is no comparison. To compare, add --prior at start-up. |
| `elementMissing` | 返回数据没有这个构件的可读信息 | The returned data has nothing readable about this element |

**`WORKSPACE_HOME`**

| 键 | 中文 | English |
| --- | --- | --- |
| `title` | 查看一次真实检查 | See a real check |
| `body` | 启动服务器时指定了一个工作区，里面是一次已经跑完的检查：每个构件在每条要求下的结果。若同时指定了前一次运行，还可以看两次的前后对比。这里只有检查结果，没有交接判断。页面只查看这次已经跑完的检查，不能在页面上选择或更换模型。 | The server was started with a workspace holding a check that has already run: each element's result under each requirement. If an earlier run was named as well, the two can be compared. There are check results only here, no handover judgement. This page only shows the check that has already run; you cannot choose or change a model on it. |
| `action` | 查看这次检查 | See this check |
| `unknown` | 未能确认服务器是否指定了工作区（不等于没有工作区）。错误原文： | Could not confirm whether the server was started with a workspace (that does not mean there is none). The error: |

**`WORKSPACE_REFUSAL`**

| 键 | 中文 | English |
| --- | --- | --- |
| `title` | 这两次运行不能对比 | These two runs cannot be compared |
| `lede` | 系统拒绝了这次对比，并列出了全部原因。这是对请求条件的答复，不是程序故障，也不是检查结果：任何一侧的检查结果都没有返回。 | The system refused this comparison and listed every reason. This is an answer about the request's conditions — not a program fault and not a check result: neither side's results were returned. |
| `reasonsHeading` | 为什么不能对比 | Why they cannot be compared |
| `actionHeading` | 要能对比，需要什么 | What a comparison needs |
| `action[0]` | 两次运行要用同一规则集（同一版本、同一内容）、同一组要求、同一检查程序、同一逻辑日期和同一组模型；两次之间只能是模型文件的内容不同。 | Both runs must use the same rule set (the same version and content), the same set of requirements, the same checkers, the same logical date and the same set of models; between the runs only the content of the model files may differ. |
| `action[1]` | 确认启动时用 --prior 指定的确实是同一项检查的前一次运行；或者去掉 --prior 重新启动服务器，只看本次检查的结果。 | Make sure the run given with --prior at start-up really is the earlier run of the same check; or restart the server without --prior and look at this check's results alone. |
| `scope` | 处理这些原因之后能否对比，以下一次返回为准。 | Whether they can be compared once these reasons are dealt with is for the next answer to say. |
| `original` | 系统返回的原文（英文）与拒绝码 | What the system returned (as written) and the refusal code |
| `code` | 拒绝码 | Refusal code |
| `unglossed` | 本界面没有这个原因的中文说明，见下面的原文。 | This interface has no English for this reason; see what the system returned below. |
| `noResult` | 没有任何结果、零问题统计或完成比例：被拒绝不是一次没有问题的检查。 | No result, no zero-problem count and no completion ratio: a refused comparison is not a check without problems. |

**`WORKSPACE_REFUSAL_REASONS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `ruleset-id-differs` | 两次用的不是同一个规则集。 | The two runs did not use the same rule set. |
| `ruleset-version-differs` | 两次用的规则集版本不同。 | The two runs used different rule set versions. |
| `ruleset-digest-differs` | 两次用的规则集内容不同（内容摘要不同）。 | The two runs used different rule set content (the content digests differ). |
| `requirement-set-differs` | 两次评估的不是同一组要求。 | The two runs did not evaluate the same set of requirements. |
| `requirement-semantics-not-recorded` | 有一次运行没有记录某条要求的谓词摘要，无法证明两次是同一个检查。 | One run did not record the predicate digest of a requirement, so it cannot be shown that both are the same check. |
| `requirement-semantics-differs` | 同一条要求，两次的谓词不同：检查的内容改过。 | The same requirement has a different predicate in the two runs: what is checked was changed. |
| `checker-differs` | 两次的检查程序、版本或配置不同。 | The two runs used different checkers, versions or configuration. |
| `as-of-differs` | 两次运行的逻辑日期不同。 | The two runs have different logical dates. |
| `model-set-differs` | 两次检查的不是同一组模型。 | The two runs did not check the same set of models. |

**`LOCAL_CHECK`** —— 本地 IFC 检查（#29，Framework Engineer，2026-10-05）。模块自己的两张表，在 `doctor/static/local-words.js` 里用 `bilingual()` 登记；含产品验证练习的范围、FAIL／PASS／没有适用对象的读法、本机记录与清理、拒绝原因与恢复指引、故障说明。界面用语（按钮、列名、大小单位）与领域文字同表，整表进 10/15 批次。“它目前不缩小检查范围”一句是实测（声明的专业不改变 PV-001 检查哪些风口），不是设计。

| 键 | 中文 | English |
| --- | --- | --- |
| `mode` | 本地检查 · 产品验证练习 | Local check · product validation exercise |
| `home.title` | 检查自己的 IFC 模型（产品验证练习） | Check your own IFC model (product validation exercise) |
| `home.body` | 选择自己导出的 IFC4 文件，只用一条产品验证规则检查风口的预定义类型。运行前会说明检查什么、要求从哪里来、结果不能说明什么，以及本机会留下哪些记录。 | Choose an IFC4 file you exported and check the predefined type of its air terminals against one product validation rule. Before it runs, the page says what is checked, where the requirement comes from, what the result cannot tell you, and what this computer keeps. |
| `home.action` | 开始本地检查 | Start a local check |
| `home.unknown` | 未能确认本地检查是否可用，错误原文： | Could not tell whether the local check is available. The error as given: |
| `home.status` | 当前提供模拟示例，以及对自己 IFC4 文件的一项有限产品验证练习；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。 | Available now: simulated examples, and one limited product validation exercise on your own IFC4 files. A Revit file itself cannot be imported, and there is no overall compliance or ready-to-build conclusion. |
| `home.statusWithWorkspace` | 当前提供：启动服务器时指定的工作区里一次已经跑完的真实检查、模拟示例，以及对自己 IFC4 文件的一项有限产品验证练习；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。 | Available now: a real check already run in the workspace named when the server was started, simulated examples, and one limited product validation exercise on your own IFC4 files. A Revit file itself cannot be imported, and there is no overall compliance or ready-to-build conclusion. |
| `home.statusWorkspaceUnknown` | 未能确认服务器是否指定了工作区，所以这里没有工作区检查的入口；这不等于没有工作区，错误原文在下面。模拟示例和本地 IFC 产品验证练习照常可用；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。 | Could not tell whether the server was started with a workspace, so there is no entry for a workspace check here; that does not mean there is none, and the error is below. The simulated examples and the local IFC product validation exercise work as usual. A Revit file itself cannot be imported, and there is no overall compliance or ready-to-build conclusion. |
| `home.cannot[0]` | 导入 Revit 文件本身（.rvt），或用产品验证练习以外的规则检查自己的模型 | Import a Revit file itself (.rvt), or check your own model against rules other than the product validation exercise |
| `home.cannot[1]` | 给出整体合规、可施工或“可以交付”的结论 | Give an overall compliance, ready-to-build or "ready to hand over" conclusion |
| `home.cannot[2]` | 写回模型、上传到云端，或在 Revit 里打开构件 | Write back to a model, upload to the cloud, or open an element in Revit |
| `start.back` | ← 返回首页 | ← Back to the home page |
| `start.title` | 检查自己的 IFC 模型 | Check your own IFC model |
| `start.lede` | 四步：先看清这次只检查什么和本机会留下的记录；选择文件；声明专业并确认规则；看清范围后运行。 | Four steps: first see what this checks and what this computer keeps; choose files; declare disciplines and confirm the rule set; look at the scope, then run. |
| `start.unavailable` | 本地检查现在不能用： | The local check cannot be used now: |
| `start.noRuleset` | 这个检出没有提供 product-validation 1.0 规则集，所以本地检查不能运行。其他规则集不在本地检查里提供。 | This checkout does not carry the product-validation 1.0 rule set, so the local check cannot run. No other rule set is offered here. |
| `exercise.heading` | 这次只检查什么 | What this checks, and only this |
| `exercise.what` | 这是一项产品验证练习：只用本仓库的产品验证规则集检查一件事——IFC4 模型里适用的风口（IfcAirTerminal）是否声明了 DIFFUSER、GRILLE、LOUVRE、REGISTER 四种预定义类型之一。它不是通用 BIM 质量检查、IFC 合规检查，也不是任何项目的交付要求。 | This is a product validation exercise. It checks one thing with this repository's product validation rule set: whether each applicable air terminal (IfcAirTerminal) in an IFC4 model declares one of the four predefined types DIFFUSER, GRILLE, LOUVRE or REGISTER. It is not a general BIM quality check, not an IFC compliance check, and not a delivery requirement of any project. |
| `exercise.sourceHeading` | 要求从哪里来 | Where the requirement comes from |
| `exercise.source` | 本仓库自己写的产品验证规则，不是项目、业主、法规或 buildingSMART 的要求；四个取值来自 IFC4 ADD2 TC1 的 IfcAirTerminalTypeEnum，只接受这四个是这条规则自己的决定。规则集的说明原文（英文）： | A product validation rule written for this repository; not a project, owner, statutory or buildingSMART requirement. The four values are from IFC4 ADD2 TC1 IfcAirTerminalTypeEnum; accepting only these four is this rule's own decision. The rule set's description, as written: |
| `exercise.readHeading` | 结果怎么读 | How to read the result |
| `exercise.read[0]` | 不通过（FAIL）：不满足这条练习规则，不等于你的模型有交付缺陷。 | FAIL: the model does not meet this exercise rule. It does not mean your model has a delivery defect. |
| `exercise.read[1]` | 通过（PASS）：只说明检查器读到的值是四个之一；不证明分类正确、洞口存在、模型已对齐，也不说明任何工作可以开始。 | PASS: only that the value the checker read is one of the four. It does not prove the classification is right, that openings exist or that models are aligned, and it does not say any work can start. |
| `exercise.read[2]` | 所选模型里没有风口：显示“没有适用对象”。这不是通过，此次也没有得到任何适用检查的通过结果。 | No air terminal in the chosen model: shown as "nothing applicable". That is not a pass, and this check produced no passing result for anything applicable. |
| `exercise.notes` | 检查器从类型还是实例读取取值、自由文本怎样比较，写在结果页这条规则的说明里。 | Whether the checker reads the value from the type or the occurrence, and how free text is compared, is in this rule's notes on the result page. |
| `records.heading` | 本机会留下哪些记录 | What this computer keeps |
| `records.lede` | 检查在这台电脑上运行，不上传到任何地方。下面这个目录保存所有记录，运行前就定好： | The check runs on this computer and uploads nothing anywhere. Everything is kept in this directory, fixed before anything runs: |
| `records.named` | 目录 | Directory |
| `records.onDisk` | 资源管理器里的实际位置 | Where File Explorer finds it |
| `records.redirected` | 服务器运行在打包应用（MSIX）里，Windows 把写到 %LOCALAPPDATA% 下的文件转到了应用自己的文件夹。在资源管理器里要找上面这个“实际位置”；按目录名去找会找不到。想避免这种转移，用下面的命令在 AppData 以外的文件夹启动服务器。 | The server is running inside a packaged (MSIX) app, and Windows has moved what is written under %LOCALAPPDATA% into the app's own folder. In File Explorer, look in the location above; the directory name alone will not find it. To avoid this, start the server with a folder outside AppData, as in the command below. |
| `records.notYet` | 目前还没有任何记录：选择第一个文件时才会创建这个目录。 | Nothing is kept yet: the directory is created when the first file is chosen. |
| `records.kept` | 目前保留：{uploads} 个模型副本，{checks} 次检查。 | Kept now: {uploads} model copies, {checks} checks. |
| `records.whatHeading` | 会留下什么 | What is kept |
| `records.what[0]` | 你选择的每个文件的副本：uploads\<内容摘要>.ifc。选择文件时就会保留，即使最后没有运行检查。 | A copy of every file you choose: uploads\<content digest>.ifc. It is kept as soon as the file is chosen, even if no check is run. |
| `records.what[1]` | 每次检查一个目录：checks\<检查号>\，里面有模型副本、规则集副本、检查结果（data\processed\canonical\run.json）、产物清单、本次检查的范围（check.json）和覆盖记录（coverage\）。 | One directory per check: checks\<check id>\, holding the model copies, a copy of the rule set, the result (data\processed\canonical\run.json), the artifact manifest, the scope of the check (check.json) and the coverage record (coverage\). |
| `records.what[2]` | 3D 几何缓存：现在不生成。以后加入 3D 查看时，它的缓存也放在这个目录里，按下面同样的步骤清理。 | 3D geometry cache: none is made now. When a 3D view is added, its cache will be kept in this directory too and cleaned up the same way. |
| `records.what[3]` | 这个目录以外不写任何文件：仓库检出不变，命令行 epc-ct run 使用的共享覆盖记录目录也不增加。 | Nothing is written outside this directory: the repository checkout does not change, and the shared coverage record directory used by the epc-ct run command gains nothing. |
| `records.what[4]` | 关闭页面或停止服务器都不会删除记录。 | Closing the page or stopping the server deletes nothing. |
| `records.cleanHeading` | 怎样清理 | How to clean up |
| `records.clean[0]` | 停止服务器：在运行它的终端里按 Ctrl+C。 | Stop the server: press Ctrl+C in the terminal running it. |
| `records.clean[1]` | 在资源管理器里打开上面的位置（实际位置与目录名不同时，用实际位置）。 | Open the location above in File Explorer (where the location differs from the directory name, use the location). |
| `records.clean[2]` | 删除整个目录，就清除了全部记录；只想删一次检查，删除 checks\<检查号>\。它用过的模型副本在 uploads\ 里，按内容摘要命名；摘要写在检查结果页的追溯信息里。 | Delete the whole directory to remove every record; to remove one check, delete checks\<check id>\. The model copies it used are in uploads\, named by content digest; the digest is in the trace details on the check's result page. |
| `records.afterHeading` | 清理之后不能再依赖什么 | What you can no longer rely on after cleaning up |
| `records.after[0]` | 已删除检查的结果页链接打不开，页面会说没有这次检查。 | A deleted check's result link stops opening; the page says there is no such check. |
| `records.after[1]` | 不能再拿它和以后的检查对比。 | It can no longer be compared with a later check. |
| `records.after[2]` | 它的覆盖记录一起删除，之后无法再说明那次检查覆盖了哪些构件和要求。 | Its coverage record goes with it, so nothing can say afterwards which elements and requirements that check covered. |
| `records.after[3]` | 删除模型副本后，要再检查就得重新选择文件。 | Once a model copy is deleted, the file has to be chosen again to check it. |
| `records.again` | 用同一个文件、同样声明的专业、同一规则集版本和同一逻辑日期重新检查，会得到同一个检查号和逐字节相同的结果。 | Checking the same file again, declared as the same discipline, with the same rule set version and the same logical date, gives the same check id and byte-identical results. |
| `records.startHeading` | 怎样把记录放在别的文件夹 | How to keep the records in another folder |
| `records.start` | 在仓库目录里，用自己的终端启动服务器，并指定 AppData 以外的文件夹，例如： | From the repository directory, start the server in your own terminal with a folder outside AppData, for example: |
| `records.command` | python doctor/serve.py --checks-dir "%USERPROFILE%\Documents\BIM Doctor checks" | python doctor/serve.py --checks-dir "%USERPROFILE%\Documents\BIM Doctor checks" |
| `records.startNote` | 服务器启动时会打印目录。第一次选择文件后目录才存在；如果 Windows 把它放到了别处，这一页会显示实际位置。 | The server prints the directory when it starts. It exists once the first file is chosen; if Windows keeps it somewhere else, this page shows where. |
| `choose.heading` | 1. 选择 IFC 文件 | 1. Choose IFC files |
| `choose.label` | 选择一个或多个 .ifc 文件 | Choose one or more .ifc files |
| `choose.note` | 只接受 IFC-SPF 文本（.ifc），不接受 .ifczip、.ifcxml 或 Revit 文件；单个文件最大 {max}。规则集只读取 IFC4，IFC2x3 文件会被拒绝，并告诉你怎样重新导出。 | Only IFC-SPF text (.ifc) is accepted, not .ifczip, .ifcxml or Revit files; at most {max} per file. The rule set reads IFC4 only; an IFC2x3 file is refused, with how to export it again. |
| `choose.copying` | 正在复制 {file}…… | Copying {file}… |
| `choose.chosenHeading` | 已选择的文件 | Chosen files |
| `choose.none` | 还没有选择文件。 | No file chosen yet. |
| `choose.remove` | 不检查这个文件 | Do not check this file |
| `choose.removed` | 已从本次选择中去掉；它的副本仍在 uploads\ 里，按上面的清理步骤删除。 | Taken out of this selection; its copy is still in uploads\. Delete it with the clean-up steps above. |
| `choose.columns.file` | 文件 | File |
| `choose.columns.size` | 大小 | Size |
| `choose.columns.schema` | IFC 版本（文件头） | IFC version (file header) |
| `choose.columns.discipline` | 你声明的专业 | Discipline you declare |
| `choose.columns.remove` | 不检查 | Leave out |
| `choose.size` | {mb} MB | {mb} MB |
| `choose.sizeGb` | {gb} GB | {gb} GB |
| `choose.sizeKb` | {kb} KB | {kb} KB |
| `choose.refusedHeading` | 这个文件没有被接受：{file} | This file was not accepted: {file} |
| `declare.heading` | 2. 声明专业并确认规则集 | 2. Declare disciplines and confirm the rule set |
| `declare.rulesetLegend` | 规则集（本地检查只提供这一个） | Rule set (the only one the local check offers) |
| `declare.ruleset` | {id} {version}：{title} | {id} {version}: {title} |
| `declare.disciplineLabel` | {file} 的专业 | Discipline of {file} |
| `declare.choose` | 请选择 | Choose |
| `declare.disciplineNote` | 专业由你声明，不从文件名猜测，写进本次检查的记录。它目前不缩小检查范围：规则会检查所选文件里的全部风口，不论声明的是哪个专业（规则自己声明适用于 {scope} 模型）。 | You declare the discipline; it is not guessed from the file name, and it is written into the check's record. It does not narrow the check now: the rule checks every air terminal in the chosen files, whichever discipline is declared (the rule itself declares it applies to {scope} models). |
| `declare.plan` | 查看检查范围 | See the scope of the check |
| `declare.planning` | 正在确定范围…… | Working out the scope… |
| `scope.heading` | 3. 运行前确认范围 | 3. Confirm the scope before running |
| `scope.ready` | 服务器按下面的范围运行这次检查；确认后再运行。 | The server will run this check with the scope below; confirm it, then run. |
| `scope.checkId` | 检查号（由规则集、逻辑日期和每个文件的名称、专业、内容决定） | Check id (decided by the rule set, the logical date, and each file's name, discipline and content) |
| `scope.ruleset` | 规则集 | Rule set |
| `scope.digest` | 规则集摘要（规范化） | Rule set digest (normalized) |
| `scope.requirement` | 要求 | Requirement |
| `scope.citation` | 出处（规则原文，英文） | Citation (the rule's own words) |
| `scope.models` | 模型 | Models |
| `scope.modelColumns.file` | 文件 | File |
| `scope.modelColumns.code` | 模型代码 | Model code |
| `scope.modelColumns.discipline` | 你声明的专业 | Discipline you declare |
| `scope.modelColumns.schema` | IFC 版本 | IFC version |
| `scope.modelColumns.size` | 大小 | Size |
| `scope.modelColumns.digest` | 内容摘要 | Content digest |
| `scope.asOf` | 逻辑日期 | Logical date |
| `scope.asOfNote` | （运行配置给定，不是今天的日期） | (set by the run configuration, not today's date) |
| `scope.programme` | 进度计划 | Programme |
| `scope.programmeText` | 你的模型不带进度计划。规则集的规则写了阶段 {stages}，所以本次检查代填了这些阶段，没有到期日；结果页不显示到期、逾期或优先级。 | Your model brings no programme. The rule set's rules name the stages {stages}, so this check fills those stages in, with no due date; the result page shows no due date, overdue state or priority. |
| `scope.geometry` | 几何 | Geometry |
| `scope.geometryText` | 不计算几何。没有形体的构件不会让整次检查中断，它的检查结果、标识和下一步照常显示；本次结果也没有 3D 视图。 | No geometry is computed. An element without a shape does not stop the check from finishing; its check result, identity and next step are shown as usual. There is no 3D view of this result. |
| `scope.location` | 结果保存在 | Results kept in |
| `scope.run` | 运行检查 | Run the check |
| `scope.running` | 正在检查，可能需要几十秒到几分钟。完成后会打开结果。 | Checking. This may take from tens of seconds to a few minutes; the result opens when it is done. |
| `scope.changed` | 选择或声明有变化，请重新查看检查范围。 | The selection or a declaration changed. See the scope of the check again. |
| `refusal.heading` | 这次检查不能开始 | This check cannot start |
| `refusal.lede` | 没有运行任何检查，也没有产生结果。每个原因和要做的事： | No check was run and there is no result. Each reason, and what to do: |
| `refusal.original` | 系统返回的原文（英文） | What the system returned (English original) |
| `refusal.unglossed` | 本界面没有为这个原因写说明，请看下面的原文。 | This interface has no note for this reason; see the original below. |
| `refusal.reasons.busy` | 另一次检查正在运行，一次只运行一个。等它完成后再运行这一次。 | Another check is running; one runs at a time. Wait for it to finish, then run this one. |
| `refusal.reasons.no-model` | 还没有选择文件。至少选择一个 .ifc 文件。 | No file has been chosen. Choose at least one .ifc file. |
| `refusal.reasons.model-too-large` | 文件超过这台服务器接受的上限，没有读取。可以导出范围更小的模型，或用更大的 --max-model-bytes 重新启动服务器。 | The file is over this server's limit and was not read. Export a smaller model, or restart the server with a larger --max-model-bytes. |
| `refusal.reasons.model-incomplete` | 文件没有完整传到服务器，没有保留。请重新选择这个文件。 | The file did not reach the server in full and was not kept. Choose the file again. |
| `refusal.reasons.not-an-ifc` | 这不是 IFC-SPF 文本文件：开头没有 ISO-10303-21 文件头。请选择 Revit 导出的 .ifc 文件，不是 .ifczip、.ifcxml 或 .rvt。 | This is not an IFC-SPF text file: it does not begin with an ISO-10303-21 header. Choose the .ifc file Revit exported, not an .ifczip, .ifcxml or .rvt. |
| `refusal.reasons.model-name-invalid` | 文件名不能用作模型名：要以 .ifc 结尾，不以“.”开头，不含路径或 < > : " / \ \| ? *。请改名后重新选择。 | The file name cannot name a model: it must end in .ifc, not start with ".", and have no path or any of < > : " / \ \| ? *. Rename it and choose it again. |
| `refusal.reasons.unknown-model` | 服务器上没有这个文件的副本（可能已被清理）。请重新选择这个文件。 | The server holds no copy of this file (it may have been cleaned up). Choose the file again. |
| `refusal.reasons.duplicate-model` | 同一个文件、同名文件或内容相同的文件选了两次。每个模型只选一次。 | The same file, a file of the same name, or one with the same content was chosen twice. Choose each model once. |
| `refusal.reasons.unknown-ruleset` | 本地检查只提供 product-validation 1.0。请选择它。 | The local check offers product-validation 1.0 only. Choose it. |
| `refusal.reasons.discipline-not-declared` | 还没有声明专业。为这个文件选择一个专业。 | No discipline is declared. Choose one for this file. |
| `refusal.reasons.unknown-discipline` | 声明的专业不在这里的专业列表里。请从列表里选择。 | The declared discipline is not in the list here. Choose one from the list. |
| `refusal.reasons.unsupported-schema` | 规则集的检查程序只读取 IFC4，这个文件不是 IFC4（例如 IFC2x3）。恢复办法：在 Revit 的 IFC 导出对话框里，把 IFC 版本选为 IFC4 Reference View，重新导出后选择新文件。原文件不用修改，也不用删除。 | The rule set's checker reads IFC4 only, and this file is not IFC4 (IFC2x3, for example). To recover: in Revit's IFC export dialog, set the IFC version to IFC4 Reference View, export again and choose the new file. The original file needs no change and need not be deleted. |
| `fault.heading` | 检查没有完成 | The check did not finish |
| `fault.lede` | 这是程序故障，不是对模型的结论。这次检查的目录已经删除，没有留下半份结果；之前选择的模型副本仍在 uploads\ 里。 | This is a fault of the program, not a conclusion about the model. The check's directory has been removed and no partial result is left; the model copies chosen before are still in uploads\. |
| `fault.todoHeading` | 可以怎么做 | What you can do |
| `fault.todo[0]` | 确认文件是从 Revit 导出的 IFC4 文件，再运行一次。 | Make sure the file is an IFC4 file exported from Revit, and run again. |
| `fault.todo[1]` | 如果同一个文件每次都在这里失败，重新导出后再选择新文件。 | If the same file fails here every time, export it again and choose the new file. |
| `fault.todo[2]` | 把下面的原文发给维护者；原文只描述程序在哪里停下，不说明模型的质量。 | Send the original text below to the maintainer; it only says where the program stopped, not anything about the model's quality. |
| `fault.original` | 故障原文 | The fault as given |
| `fault.network` | 没有收到服务器的回答：服务器可能已经停止。启动服务器后，刷新这一页。 | No answer came from the server: it may have stopped. Start the server, then reload this page. |
| `earlier.heading` | 以前的检查 | Earlier checks |
| `earlier.note` | 保存在上面的目录里，直到你删除它们。 | Kept in the directory above until you delete them. |
| `earlier.none` | 还没有完成的检查。 | No finished check yet. |
| `earlier.item` | {files} · {ruleset} · 检查号 {id} | {files} · {ruleset} · check {id} |
| `result.exercise` | 这是产品验证练习的结果：只检查风口是否声明了四种预定义类型之一。不通过不等于你的模型有交付缺陷；通过不证明分类正确、洞口存在、模型已对齐或任何工作可以开始。 | This is the result of a product validation exercise: it only checks whether air terminals declare one of four predefined types. A FAIL does not mean your model has a delivery defect; a PASS does not prove the classification is right, that openings exist, that models are aligned or that any work can start. |
| `result.nothingHeading` | 没有适用对象 | Nothing applicable |
| `result.nothing` | {file}：这条规则在这个模型里没有适用对象。这不是通过——此次没有得到任何适用检查的通过结果，也不说明模型质量。 | {file}: this rule has nothing to apply to in this model. That is not a pass — this check produced no passing result for anything applicable, and it says nothing about the model's quality. |
| `result.scopeHeading` | 这次检查的范围 | The scope of this check |
| `result.declared` | {file}（你声明的专业：{discipline}） | {file} (discipline you declared: {discipline}) |
| `result.programme` | 进度计划：规则集的阶段 {stages} 由本次检查代填，没有到期日；本页不显示到期、逾期或优先级。 | Programme: the rule set's stages {stages} were filled in by this check, with no due date; this page shows no due date, overdue state or priority. |
| `result.recordsHeading` | 这次检查的记录在哪里，怎样清理 | Where this check's records are, and how to clean up |
| `result.location` | 这次检查的目录 | This check's directory |
| `result.another` | 检查另一个模型 | Check another model |
| `result.missing` | 没有这次检查：它可能已被清理（目录被删除），或者链接不对。清理之后，结果页链接就打不开了。 | There is no such check: it may have been cleaned up (its directory deleted), or the link is wrong. After cleaning up, result links stop opening. |
| `disciplines.Architecture` | 建筑（Architecture） | Architecture |
| `disciplines.HVAC` | 暖通（HVAC） | HVAC |
| `disciplines.MEP` | 机电（MEP） | MEP |
| `disciplines.Plumbing` | 给排水（Plumbing） | Plumbing |
| `disciplines.Structural` | 结构（Structural） | Structural |
| `listSeparator` | 、 | ,  |
| `colon` | ： | :  |

## 界面用语

**`ACTION`**

| 键 | 中文 | English |
| --- | --- | --- |
| `what` | 要做什么 | What to do |
| `team` | 处理团队 | Handling team |
| `consequence` | 对这项工作的后果 | What it means for this work |
| `recheck` | 完成后拿什么复检 | What a recheck must show |
| `noSentence` | 本界面没有为这条记录所用的版本写要做什么。记录所带的来源原文在下面的折叠里，它不是操作指令。 | This interface has written no action for the version this record uses. The source wording the record carries is in the fold below; it is not an instruction. |
| `original` | 来源原文（英文，记录所带）：供追溯，不是操作指令 | Source wording (as the record carries it): for tracing, not an instruction |

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

**`CITATION_GLOSSES`**

| 键 | 中文 | English |
| --- | --- | --- |

**`COMMON`**

| 键 | 中文 | English |
| --- | --- | --- |
| `colon` | ： | :  |
| `aside` | （{text}） |  ({text}) |
| `emptyList` | （记录中为空列表） | (an empty list in the record) |
| `unknownMode` | 未识别的入口（{mode}） | Unrecognised entry ({mode}) |
| `unnamedElement` | 未命名构件 | Unnamed element |
| `and` |  与  |  and  |
| `oneElement` | 一个构件 | One element |
| `twoElements` | 一对构件 | A pair of elements |
| `nElements.one` | {count} 个构件 | {count} element |
| `nElements.other` | {count} 个构件 | {count} elements |
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
| `realNote` | 仓库随附一个样例项目，下面是对它的一次检查尝试。这个入口只看这个样例，不能换成别的模型；检查自己的 IFC4 文件，用首页的“检查自己的 IFC 模型”。Revit 文件本身不能导入。 | The repository comes with a sample project; below is a check attempt on it. This entry shows only that sample and cannot be switched to another model; to check your own IFC4 files, use "Check your own IFC model" on the home page. A Revit file itself cannot be imported. |
| `exampleTitle` | 选择一个模拟示例 | Choose a simulated example |
| `exampleIntro` | 每个示例是一份检查记录。 | Each example is one check record. |
| `empty` | 这个入口下目前没有可以查看的内容。 | There is nothing to look at under this entry yet. |
| `exampleTag` | 示例说明 | About this example |
| `open` | 打开这个示例的结果 | Open this example's result |
| `othersHeading` | 其他模拟示例 | Other simulated examples |
| `othersNote` | 这些示例还没有写说明，复检记录暂时只有编号；本轮没有改到它们。 | These examples have no description yet, and the recheck records have only a number for now; this round did not touch them. |

**`ELEMENT_CARD`**

| 键 | 中文 | English |
| --- | --- | --- |
| `traceKey` | 追溯用内部键 | Internal key for tracing |
| `class` | 类别 | Class |
| `storey` | 楼层 | Storey |
| `model` | 所属模型 | Model |
| `disciplineRow` | 专业 | Discipline |

**`EMPTY_STRING`**

| 键 | 中文 | English |
| --- | --- | --- |
| `EMPTY_STRING` | （记录中为空字符串） | (an empty string in the record) |

**`ENVELOPE_WORDS`**

| 键 | 中文 | English |
| --- | --- | --- |
| `missing` | outcome={outcome} 但缺少 {key} | outcome={outcome} but {key} is missing |
| `unexpected` | outcome={outcome} 却同时带有 {key} | outcome={outcome} but it also carries {key} |

**`EVIDENCE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `currentCitation` | 本次记录引用的对应证据： | Corresponding evidence this record cites:  |
| `reason` | 原因： | Reason:  |
| `recordCause` | 记录给出的原因（原文）： | Reason the record gives (as written):  |
| `trace` | 追溯信息（记录原码与内容指纹） | Tracing (record codes and content fingerprints) |
| `priorDigest` | 复检前的内容指纹 | Content fingerprint before the recheck |
| `currentDigest` | 本记录的内容指纹 | Content fingerprint in this record |
| `none` | 复检前的证据路径没有引用任何证据。 | The evidence path before the recheck cites no evidence. |
| `rows.one` | （{count} 条） |  ({count} row) |
| `rows.other` | （{count} 条） |  ({count} rows) |
| `empty` | （空） | (empty) |
| `glossaryCode` | 记录里的代码 | Code in the record |
| `glossarySaid` | 本页的说法 | What this page says |
| `meaning` | “{label}”是什么意思 | What "{label}" means |
| `dispositionNow` | 这个事项现在 | This item now |
| `currentMissing` | 记录给出了这一项的当前位置（内部编号 #{ordinal}），但在本记录里找不到它；本页不另行对应。 | The record gives this item's current place (internal number #{ordinal}), but it cannot be found in this record; this page does not match it up another way. |
| `memberLink` | 在明细页查看和它一起评估的全部构件与证据 | See every element and piece of evidence assessed with it on the detail page |
| `reissueColumns.side` | 交接的哪一侧 | Side of the handover |
| `reissueColumns.role` | 角色（取自本次请求的交接） | Role (from this request's handover) |
| `reissueColumns.model` | 模型 | Model |
| `reissueColumns.reissued` | 是否重新发布 | Re-issued? |
| `unrecognisedSide` | 无法识别，见上 | Cannot be recognised; see above |
| `reissued` | 重新发布了（新版本） | Re-issued (new version) |
| `notReissued` | 没有变（原版本） | Unchanged (original version) |

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
| `summary` | 本次结果：共 {items} 个事项，其中 {todo} 个需要处理 | This result: {items} in all; to deal with: {todo} |
| `items.one` | {count} 个事项 | {count} item |
| `items.other` | {count} 个事项 | {count} items |
| `verdictLine` | ：对应的那项工作  | : the work concerned is  |
| `quietLine` | ：{summary}（列在本页下方） | : {summary} (listed further down this page) |
| `elementsLine.one` | {unit}这份记录共涉及 {count} 个不同的构件。 | {unit} This record involves {count} element. |
| `elementsLine.other` | {unit}这份记录共涉及 {count} 个不同的构件。 | {unit} This record involves {count} different elements. |
| `action` | 要做什么 | What to do |
| `problem` | 情况 | Situation |
| `openItem` | 查看这一项：具体对象、要做什么、由谁处理、拿什么复检 | See this item: the element, what to do, who deals with it, what a recheck must show |
| `cardDetails` | 构件信息和要做什么 | Element details and what to do |
| `cardElements` | 构件信息 | Element details |
| `openCard` | 查看这一项 | See this item |
| `openHeading.one` | {label}，按处理团队（{count} 个事项） | {label}, by handling team ({count} item) |
| `openHeading.other` | {label}，按处理团队（{count} 个事项） | {label}, by handling team ({count} items) |
| `team` | 处理团队  | Handling team  |
| `teamCount.one` | ：{count} 个事项 | : {count} item |
| `teamCount.other` | ：{count} 个事项 | : {count} items |
| `columns.problem` | 问题 | Problem |
| `columns.work` | 哪项工作：结论 | Which work: conclusion |
| `columns.count` | 事项数 | Items |
| `quietHeading.one` | {label}（{count} 个事项） | {label} ({count} item) |
| `quietHeading.other` | {label}（{count} 个事项） | {label} ({count} items) |
| `separator` |  ｜  |  \|  |
| `nextHeading` | 然后：看这份记录复检之后的变化 | Then: see how this record changed after a recheck |
| `nextLink` | 打开示例“{run}” | Open the example "{run}" |
| `nextAfter` | 。每个事项的页面里也有直达它复检变化的链接。 | . Each item's page also links straight to how that item changed in the recheck. |
| `traceSummary` | 追溯信息：记录标识、规则版本、记录原码 | Tracing: record identity, rule version, record codes |
| `recordLink` | 这份记录的请求范围、版本与来源 | This record's requested scope, versions and sources |
| `notRevised` | （该页尚未改版，仍是内部用语） |  (Chinese only: that page has not been translated or revised yet, and still uses internal terms) |
| `traceItem` | 事项 | Item |
| `traceOrdinal` | 内部分组编号 | Internal group number |

**`HOW_TO_READ`**

| 键 | 中文 | English |
| --- | --- | --- |
| `HOW_TO_READ` | 如何阅读这一页 | How to read this page |

**`IFC_CLASS_NAMES`**

| 键 | 中文 | English |
| --- | --- | --- |

**`ITEM`**

| 键 | 中文 | English |
| --- | --- | --- |
| `missing` | 记录中没有这一项 | The record has no such item |
| `back` | ← 返回事项列表（回到这一项的位置） | ← Back to the list of items (to this item's place) |
| `kicker` | 首次检查事项 · {count} | First-check item · {count} |
| `conclusion` | 一、结论 | 1. Conclusion |
| `needs` | 这项工作需要什么 | What this work needs |
| `actionHeading` | 二、要做什么、由谁处理、完成后拿什么复检 | 2. What to do, who deals with it, what a recheck must show |
| `followUpHeading` | 二、后续 | 2. Follow-up |
| `noFollowUp` | 记录没有为这一项给出后续处理动作、处理团队或默认处理角色。 | The record gives no follow-up action, handling team or default handling role for this item. |
| `whichOne` | 三、是哪个构件 | 3. Which element |
| `whichTwo` | 三、是哪两个构件 | 3. Which two elements |
| `details` | 四、{heading} | 4. {heading} |
| `nextHeading` | 然后：这一项复检后的变化 | Then: how this item changed after a recheck |
| `nextLink` | 在示例“{run}”里看这一项 | See this item in the example "{run}" |
| `nextAfter` | 。那是对这同一份记录的一次复检，同样是模拟示例。 | . That is a recheck of this same record, and also a simulated example. |
| `basisSummary` | 依据逐条：这个结论引用的证据 | Basis, citation by citation: the evidence this conclusion cites |
| `context` | 背景引用：不是这个结论的依据，逐字显示。 | Background citations: not the basis of this conclusion, shown word for word. |
| `traceSummary` | 追溯信息：内部键与记录原码 | Tracing: internal keys and record codes |
| `keys` | 内部键 | Internal keys |
| `ordinal` | 内部分组编号 | Internal group number |
| `leaf` | 终点 outcome | Final outcome |
| `memberLink` | 在明细页查看完整的证据路径 | See the full evidence path on the detail page |

**`LANGUAGE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `label` | 界面语言 | Interface language |
| `current` | 当前：中文 | Current: English |
| `untranslatedTitle` | 这一页还没有翻译 | This page has not been translated yet |
| `untranslatedBody` | 这一页的英文还没有写好。下面的按钮会用中文打开同一页：同一个运行、同一份记录、同一个对象，内容不变。 | The English for this page has not been written yet. The button below opens this same page in Chinese: the same run, the same record and the same element, with nothing changed. |
| `showIn` | 用中文查看这一页 | See this page in Chinese |
| `back` | ← 返回上一页 | ← Back to the previous page |
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

**`REASON_GLOSSES`**

| 键 | 中文 | English |
| --- | --- | --- |

**`RECHECK_MODEL`**

| 键 | 中文 | English |
| --- | --- | --- |
| `producing` | 交出方 | Handing-over side |
| `consuming` | 接收方 | Receiving side |
| `listSeparator` | 、 | ,  |
| `aspectsChanged` | {list}变了 | {list} changed |
| `aspectsSame` | ，{list}未变 | ; {list} unchanged |
| `end` | 。 | . |
| `unrecognisedAspect` | “{code}”（{unrecognised}） | "{code}" ({unrecognised}) |
| `unrecognisedKey` | key_changed = “{value}”（{unrecognised}） | key_changed = "{value}" ({unrecognised}) |
| `onlyRekeyed` | {rekeyed}：证据内容和比较依据都没有变。 | {rekeyed}: neither the evidence content nor the comparison basis changed. |

**`REFUSAL_UNGLOSSED`**

| 键 | 中文 | English |
| --- | --- | --- |
| `title` | 系统拒绝了这次请求 | The system refused this request |
| `text` | 本界面没有这个原因的中文说明，请展开下面系统返回的原文。 | This interface has no English explanation for this reason; open what the system returned below. |

**`UNRECOGNISED`**

| 键 | 中文 | English |
| --- | --- | --- |
| `UNRECOGNISED` | 未识别的值，按原值显示 | unrecognised value, shown as it came |

**`WORK`**

| 键 | 中文 | English |
| --- | --- | --- |
| `unchanged` | {work}：{before} （{note}） | {work}: {before} ({note}) |
| `changed` | {work}：复检前 {before} → 现在 {now} | {work}: before the recheck {before} → now {now} |
| `missing` | {work}：复检前 {before}；现在：记录没有给出 | {work}: before the recheck {before}; now: not given in the record |
