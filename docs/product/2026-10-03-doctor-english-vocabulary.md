# Doctor 英文词表（主路径：首页、示例目录、首次结果、单项、复检）

日期：2026-10-03，第二部分（单项、复检）同日补入。负责：Product/UI Engineer。
状态：**全部未经 BIM 复核**；有领域含义的条目进 10/15 BIM 批次。
本文件由界面实际注册的词表生成，测试逐条核对英文与这里一致。中文一列是同一键在 `vocabulary.js` 里的原文。

## 规则

- 英文是第二张词表，不是第二套页面：判断、计数、来源标签、限制在两种语言里完全相同（测试逐键核对结构与占位符）。
- 记录、Pack 或本仓库产品文档已有英文原文的地方，英文界面显示原文，不把中文释义译回英文。
  “要做什么”“完成后拿什么复检”在英文里直接读记录里路由的 `next_action`、`recheck_condition`，词表里没有副本（`ACTION_TEXT`）。
  IFC 类别在英文里只显示类别本身（`IFC_CLASS_NAMES` 英文为空）；检查结果的原因在英文里只显示原文（`REASON_GLOSSES` 英文为空）。
  复检单项里“复检前留下的结束条件”在英文里读记录的 `prior_recheck_condition` 原文。
- 带计数的说法分单数和复数两种形式（`one`／`other`），中文两种形式相同。
- 英文模式下，还没有翻译的页面不画出来，显示“This page has not been translated yet”，并给出用中文看同一页的按钮。

## 计数

| 类别 | 表 | 条目 |
| --- | --- | --- |
| 原文（取自 Pack、记录或产品文档，未翻译） | 3 | 12 |
| 有领域含义（判断、活动、问题类型、限制、来源），待 BIM | 44 | 337 |
| 界面用语 | 22 | 160 |
| 合计 | 69 | 509 |

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
| `determination-not-cited-by-this-record` | 模型版本没有变，本次记录没有再引用这份判定：它被别的判定取代了。 | The model version did not change, and this record no longer cites this determination: another determination replaced it. |
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
| `work-suspended` | 这项工作暂停 | This work is suspended |
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
| `projectAssumption` | 这是本项目约定的要求，不是通用要求。 | This is a requirement agreed for this project, not a general one. |
| `gap` | 要填什么值、对应哪个 Revit 参数，记录未提供。 | What value to fill in, and which Revit parameter it maps to, the record does not say. |
| `prior` | 复检前那次评估时，这条证据的要求和结果如下。有这段说明不等于这一行可以比较；这一行的状态以上面写的为准。 | At the assessment before the recheck, this evidence's requirement and result were as follows. Having this description does not make the row comparable; the row's state is what is written above. |
| `currentAbsent` | 本次记录引用的对应证据：要求明细记录未提供。 | The corresponding evidence this record cites: its requirement details are not given in the record. |

**`DIRECTORY_NOTE`**

| 键 | 中文 | English |
| --- | --- | --- |
| `DIRECTORY_NOTE` | 每个示例是一份检查记录。一个结论的证据可能是真实检查的结果，可能是模拟的检查结果，也可能是模拟的人工判定；具体是哪一种，看结果页和事项页每个结论旁的“依据”一行，按逐条引用标明。示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定。 | Each example is one check record. The evidence for a conclusion may be a real check result, a simulated check result or a simulated human determination; which one it is, the "Basis" line beside each conclusion on the result and item pages says, citation by citation. The project settings in the examples, including the handling teams and the acceptance of evidence methods, are demonstration settings, not real project decisions. |

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
| `pairing-no-longer-derived.next` | 记录没有为这一对构件给出下一步。请核对让它不再被配对的那份依据（见“记录给出的原因”）是不是你认可的结论；原来的问题没有被证明已修复。 | The record gives no next step for this pair. Check whether the basis that stopped them being paired (see "the reason the record gives") is a conclusion you accept; the original problem has not been shown to be fixed. |
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
| `pairNote` | 这两个构件已不再被配成一对检查：穿透判定现为“不穿透”（见下方记录给出的原因）。这不等于开洞已建成，也不等于开洞缺陷已修复。 | These two elements are no longer paired for checking: the penetration determination is now "no penetration" (see the reason the record gives below). This does not mean the opening has been built, nor that the opening defect has been fixed. |
| `model` | 模型 | Models |
| `whichOne` | 二、是哪个构件 | 2. Which element |
| `whichTwo` | 二、是哪两个构件 | 2. Which two elements |
| `actionHeading` | 三、要做什么、由谁处理、完成后拿什么复检 | 3. What to do, who deals with it, what a recheck must show |
| `noCurrent` | 记录没有给出这一项的当前情况，所以本页没有处理动作、处理团队或默认处理角色可以显示。复检前记录里的这些信息也没有随复检记录返回。 | The record does not give this item's current place, so this page has no action, handling team or default handling role to show. Those details from the record before the recheck did not come back with the recheck record either. |
| `conditionHeading` | 四、复检前留下的结束条件，这次达到了吗 | 4. Was the exit condition left before the recheck reached this time? |
| `priorCondition` | 复检前留下的结束条件：{text}。 | The exit condition left before the recheck: {text} |
| `end` | 。 | . |
| `conditionNote` | 这里只说复检前留下的结束条件被证明到了什么程度，与现在的结论分开读：结论变了，不等于原条件已满足。 | This says only how far the exit condition left before the recheck has been shown to be reached; read it apart from the conclusion now. A changed conclusion does not mean the original condition is met. |
| `originalSummary` | 规则原文（英文）与记录原码 | The rule's own words and record codes |
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

**`WORKSPACE_HOME`**

| 键 | 中文 | English |
| --- | --- | --- |
| `title` | 查看一次真实检查 | See a real check |
| `body` | 启动服务器时指定了一个工作区，里面是一次已经跑完的检查：每个构件在每条要求下的结果。若同时指定了前一次运行，还可以看两次的前后对比。这里只有检查结果，没有交接判断。页面只查看这次已经跑完的检查，不能在页面上选择或更换模型。 | The server was started with a workspace holding a check that has already run: each element's result under each requirement. If an earlier run was named as well, the two can be compared. There are check results only here, no handover judgement. This page only shows the check that has already run; you cannot choose or change a model on it. |
| `action` | 查看这次检查 | See this check |
| `unknown` | 未能确认服务器是否指定了工作区（不等于没有工作区）。错误原文： | Could not confirm whether the server was started with a workspace (that does not mean there is none). The error: |

## 界面用语

**`ACTION`**

| 键 | 中文 | English |
| --- | --- | --- |
| `what` | 要做什么 | What to do |
| `whatOriginal` | 要做什么（规则原文，英文） | What to do (the rule's own words) |
| `team` | 处理团队 | Handling team |
| `consequence` | 对这项工作的后果 | What it means for this work |
| `recheck` | 完成后拿什么复检 | What a recheck must show |
| `recheckOriginal` | 完成后拿什么复检（规则原文，英文） | What a recheck must show (the rule's own words) |
| `original` | 规则原文（英文） | The rule's own words |

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
| `realNote` | 仓库随附一个样例项目，下面是对它的一次检查尝试。目前不能选择别的模型，也不能导入自己的模型。 | The repository comes with a sample project; below is a check attempt on it. You cannot choose another model yet, nor import your own. |
| `exampleTitle` | 选择一个模拟示例 | Choose a simulated example |
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
| `problem` | 问题 | Problem |
| `openItem` | 查看这一项：具体对象、要做什么、由谁处理、拿什么复检 | See this item: the element, what to do, who deals with it, what a recheck must show |
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
