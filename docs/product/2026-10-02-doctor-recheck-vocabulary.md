# Doctor 复检词表

日期：2026-10-02。负责：Product/UI Engineer。
范围：复检页（[D1 画面流程 S4](2026-09-16-doctor-d1-screen-flow.md)）把记录里的代码写成什么话。

这份词表是 `doctor/static/vocabulary.js` 的可读副本，供评审措辞用；以代码为准，
`tests/test_doctor_recheck_screens.py` 检查两者一致，也检查代码覆盖了记录类型
（`epc_control_tower/purpose/assessment/record.py`）允许的每一个值。

三条规则：

- 代码由记录给出，界面只负责换成人话。界面不决定状态，也不给状态排好坏。
- 人话在前，原码在可展开的“追溯信息”里；任何一句都不要求读者认识字段名。
- 词表里没有的值原样显示，并标注“未识别的值，按原值显示”；缺失的键显示“记录未携带”。

## 1. 旧证据的四种比较结果（`evidence_carry_over[].state`）

| 记录里的代码 | 页面上的说法 | 意思 | 必须同时说的话 |
| --- | --- | --- | --- |
| `equivalent` | **比较依据一致** | 这条旧证据在本次记录里有唯一对应的一条，逐项比较都相同。 | 这只说明不必因为引用换了键而重新收集这条证据，不代表整个交接不用复核。 |
| `changed` | **比较依据有变化** | 这条旧证据在本次记录里有唯一对应的一条，但至少有一个方面不同。 | 结果读起来相同，也仍然算有变化；变了的是哪些方面，见这一条的说明。 |
| `no-counterpart` | **未找到对应证据** | 可以比较，但本次记录没有引用与它对应的证据。 | 没有对应证据不代表问题已修复。 |
| `not-provable` | **现有依据不足以比较** | 比较本身无法建立，所以既不能说一致，也不能说变了。 | 这是“无法比较”，不是“证据缺失”，也不是“没有对应证据”。 |

没有第五种，也没有“是／否”。

## 2. 每种结果下的原因（`reason`）

| 记录里的代码 | 页面上的说法 |
| --- | --- |
| `finding-equivalent` | 对应的检查结果只有一条，模型版本、检查结果内容、检查要求、检查程序逐项相同。 |
| `finding-changed` | 对应的检查结果只有一条，逐项比较后至少有一个方面不同。 |
| `no-counterpart-in-the-cited-run` | 本次记录依据的验证运行里，这个构件在这条要求下没有检查结果。 |
| `counterpart-not-cited-under-the-current-binding` | 验证运行里有对应的检查结果，但本次记录没有引用它。 |
| `sealed-citation-has-no-comparison-basis` | 原记录封存时没有保存这条引用的比较依据（旧版本的记录）。本页不会用当前规则去补造，所以只能如实显示无法比较。 |
| `comparison-basis-version-unknown` | 原记录保存的比较依据，是本系统不认识的版本。 |
| `subject-not-present` | 这条证据所针对的构件，在本次记录里已经不在（去向见“记录给出的原因”）。构件不在不等于已修复。 |
| `counterpart-not-unique` | 本次有不止一条候选的对应检查结果，系统不从中挑选（全部候选见“记录给出的原因”）。 |
| `requirement-semantics-basis-unavailable` | 封存一方或当前一方没有“检查要求”的比较依据。 |
| `comparison-basis-incomplete` | 封存一方或当前一方缺少部分比较依据（模型版本、检查结果内容摘要或检查程序指纹）。 |
| `determination-same-reference-same-content` | 同一份判定：引用相同，内容摘要也相同。 |
| `determination-content-changed-under-the-same-reference` | 引用相同，但判定的内容已经不是原记录读到的那一份（被重新作出、重新归属或重新签署）。新判定照常作为证据读取，只是不能说它和原判定是同一份。 |
| `determination-not-cited-by-this-record` | 模型版本没有变，本次记录没有再引用这份判定：它被别的判定取代了。 |
| `determination-not-attributable-to-this-context` | 模型版本已经变化，原判定是针对旧版本作出的，不能归到当前版本。不是证据不存在，也不是原判定错误；需要针对当前版本的判定。 |

## 3. “有变化”时，变的是什么（`changed_aspects`）

| 记录里的代码 | 页面上的名词 |
| --- | --- |
| `model-version` | 模型版本 |
| `finding-content` | 检查结果内容 |
| `requirement-semantics` | 检查要求 |
| `checker` | 检查程序 |

页面把它们写成一句具体的事实，变了的在前、未变的在后，例如：

- 只有 `model-version`：“模型版本变了，检查结果内容、检查要求、检查程序未变。”
- 只有 `requirement-semantics`：“检查要求变了，模型版本、检查结果内容、检查程序未变。”
- `finding-content` 与 `requirement-semantics`：“检查结果内容、检查要求变了，模型版本、检查程序未变。”

“未变”的方面是这四项里记录没有列出的其余项。行内出现这四项之外的值时，页面
不再列“未变”，并写：“含有未识别的变化方面，本页因此不列“未变”的方面。”

随后按情况加一句：

| 情况 | 加的话 |
| --- | --- |
| 只有模型版本变了 | 只有模型版本变了，不等于检查结果的内容变了。记录也不就“这条证据能否沿用到新版本”下结论。 |
| 检查要求变了，检查结果内容没变 | 检查要求被修改过，检查结果读起来和原来一样——但它是按修改后的要求得出的，不能当作同一条证据。 |
| 检查要求和检查结果内容都变了 | 检查要求被修改过，检查结果内容也变了：结果的变化可能来自要求的修改（例如要求放宽），不能据此说模型修好了。记录不说明要求是放宽还是收紧。 |
| 检查结果内容变了，检查要求没变 | 检查要求没有变，检查结果内容变了。这一行不记录结果是变好还是变差，请看当前判断。 |
| 检查程序变了 | 检查程序（检查器或它的配置）版本不同：同样的模型和要求也可能得出不同结果。 |

## 4. 引用的键换没换（`key_changed`）

| 记录里的值 | 页面上的说法 |
| --- | --- |
| `yes`，且结果为“比较依据一致” | **只是引用换了键**：证据内容和比较依据都没有变。 |
| `yes`，且结果为“比较依据有变化” | 引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 |
| `no` | 引用的键没有换。 |

## 5. 哪一侧的模型重新发布了

取自 `model_version_context_comparison.changed_models`，与同一对象里的
`producing.model_key`、`consuming.model_key` 对照。`{from}`、`{to}` 是本次请求
交接里的角色名，`{producing}`、`{consuming}` 是模型的 key；页面不写任何专业名称。

| 情况 | 标题 | 说明 | 必须同时说的话 |
| --- | --- | --- | --- |
| `none` | **两侧模型都没有重新发布（版本未变）** | 本次复检和原记录用的是同一对模型版本，所以下面的差异不来自模型改动。 | （无） |
| `producing` | **交出方的模型重新发布了，接收方的模型没有变** | 交出方（{from}）的模型 {producing} 是新版本；接收方（{to}）的模型 {consuming} 还是原版本。 | 交出方重新发布可能改变了穿越关系或涉及的构件范围，不能据此说接收方的工作（例如开洞）已经做好。 针对旧版本作出的判定不能归到新版本。 |
| `consuming` | **接收方的模型重新发布了，交出方的模型没有变** | 接收方（{to}）的模型 {consuming} 是新版本；交出方（{from}）的模型 {producing} 还是原版本。 | 接收方重新发布可能是修复的途径，但不代表修复已经发生（例如洞口已完成）。 针对旧版本作出的判定同样不能归到新版本。 |
| `both` | **交出方和接收方的模型都重新发布了** | 交出方（{from}）的模型 {producing} 和接收方（{to}）的模型 {consuming} 都是新版本。 | 两侧同时变化：本页不把任何一条证据的变化归到某一侧。 重新发布不代表修复已经发生；针对旧版本作出的判定不能归到新版本。 |
| `unrecognised` | **记录的模型版本比较无法识别，按原值显示** | 记录给出的变化模型与本记录的交出方、接收方对不上，或两个字段互相矛盾。本页不猜是哪一侧。 | （无） |

四种情况下都加一句：“本页只说明哪一侧变了、记录证明了什么，不根据重新发布的方向预判好坏。”

## 6. 复检前各事项现在的情况（`dispositions[].disposition`）

| 记录里的代码 | 页面上的说法 | 下一步 |
| --- | --- | --- |
| `present` | 仍在本次检查范围内；判断与条件另看 | 看下面记录给出的当前情况：现在的判断、下一步和处理角色都以它为准。 |
| `element-deleted-in-reissued-model` | 在重发模型中删除，不等于修复 | 记录没有为已删除的构件给出下一步。请在源模型里核对这次删除是不是有意的设计变更；本预览不能记录这种确认。 |
| `element-out-of-subject-class` | 已不属于此活动对象类别，不等于修复 | 记录没有为它给出下一步。请核对构件的类别（导出映射）是不是有意改变；类别变了只说明本活动不再检查它。 |
| `pairing-no-longer-derived` | 这两个构件现在不再被配成一对来检查，不等于开洞已补 | 记录没有为这一对构件给出下一步。请核对让它不再被配对的那份依据（见“记录给出的原因”）是不是你认可的结论；原来的问题没有被证明已修复。 |
| `outside-declared-scope` | 本次未声明该范围，不等于问题解除 | 这个构件本次没有被重新检查。需要结论时，要重新发起一次包含它的复检；本预览不能发起。 |

## 7. 原复检条件被证明到哪一步（`condition_status`）

| 记录里的代码 | 短说法 | 页面上的结论句 |
| --- | --- | --- |
| `named-outcome-observed` | 仅命名结果已观察到；条件其余部分未检查 | 原复检条件里点名的那个结果，现在观察到了。条件句的其余部分没有被机器检查，需要人对照原条件确认；这不是“整句条件已满足”。 |
| `named-outcome-not-observed` | 未观察到命名结果 | 原复检条件里点名的那个结果，现在没有观察到：原条件未达成。 |
| `no-machine-checkable-part` | 条件没有可机检部分，需要人阅读 | 原复检条件没有机器能检查的部分，需要人阅读原条件并判断；记录对它不下结论。 |
| `not-comparable` | 不可比较：对应的构件不完整 | 无法对原复检条件下结论：原来的构件有的已经不在本次记录里，条件没有完整的对象可以检查。这不代表条件已满足。 |
| `no-recheck-condition` | 原记录没有复检条件 | 原记录没有复检条件：原来的判断没有留下待办。 |

没有“整句条件已满足”。

## 8. 始终展开的五句话

- “比较依据一致”不代表整个交接不用复核。
- 构件不在了、或找不到对应证据，不代表问题已修复。
- 模型重新发布（不论哪一侧）不代表修复已经发生。
- “只有模型版本变了”不等于检查结果的内容变了。
- “无法比较”不是“证据缺失”：旧记录没保存比较依据时，本页如实显示无法比较。

## 9. 本预览做不了的事

- 发起新的复检或上传新模型
- 把事项标记为已解决、关闭或接受风险
- 指派或通知责任人
- 在 Revit 中打开或定位构件
- 导出复检记录

这些动作没有实现，所以页面上没有对应的按钮。

## 10. 引用的种类与来源标签

| 记录里的代码 | 页面上的说法 |
| --- | --- |
| `finding` | 检查结果引用 |
| `determination` | 判定引用 |

来源标签按每条引用自身是否带模拟标记判定，不按整页或整份记录推断：

- **真实检查输出**：未带模拟标记的检查结果引用：来自真实的检查运行，是真实 IFC 模型按真实规则检查的产物。
- **模拟的检查结果**：带模拟标记（以 fixture 开头）的检查结果引用：由示例生成，不是任何真实检查运行的输出。
- **模拟的人工判定**：带模拟标记的判定引用：由示例提供，没有任何协调评审真的发生过。
- **来源未标注的判定**：未带模拟标记的判定引用：判定不是检查运行的输出，本界面也没有可核依据说明它来自哪里，因此不作真实或模拟的断言。

## 11. 2026-10-01 可用性修订新增的说法

主界面不再出现“夹具、信封、Framework、Purpose、裁决、子范围、成员”。对应关系：
夹具 → 模拟示例；裁决 → 判断；成员 → 构件（一个事项是一个构件或一对构件）；子范围 → 不在主界面出现，
只在“追溯信息”里以“内部分组编号”出现。路径与取舍见
[可用性修订](2026-10-01-doctor-usability-revision.md)。

**事项分组（按记录是否给出下一步，不看判断词）**

| 分组 | 页面上的说法 | 必须同时说的话 |
| --- | --- | --- |
| `open` | 待处理事项：记录给出了下一步，需要处理 | 每一项的页面写明涉及的构件、依据和记录给出的下一步。 |
| `unplaced` | 记录没有给出当前情况的事项 | 这些项现在是什么判断，记录没有说。构件不在了不代表问题已修复。 |
| `none` | 记录没有给出下一步的事项 | 记录没有为这些项给出下一步。这不代表整个交接不用复核。 |

出处缩写：**B§1** = `interdisciplinary-coordination-readiness-mep-to-architecture.md` 第 1 节（Checkpoint B）；
**Pack** = `purpose-packs/interdisciplinary-coordination-readiness/pack.toml`。下列中文都是本界面写的说明，
代码留在旁边；它们重述原文，不增加原文没有的结论。

**判断词（词在前，说明在旁）** —— 出处 B§1 “The four verdicts, defined once”。判断说的是接收方的一项工作
能否开始，不是某项检查是否通过。

| 记录里的词 | 旁边的说明 | 原文 |
| --- | --- | --- |
| `READY` | 必要的证据齐全且满足验收条件，没有未解决的阻碍，也没有证据缺口：在本次评估范围内，这项工作可以开始 | "Every piece of necessary evidence is present and satisfies the applicable acceptance conditions, and there is no unresolved blocker and no evidence gap. The activity can start, within the assessed scope." |
| `BLOCKED` | 有一项已知未满足的要求，阻止这项工作 | "A known unmet requirement prevents the activity." |
| `UNKNOWN` | 回答这个问题所需的证据没有产生，这项工作能否开始无法决定：既不能放行，也不能拒绝 | "An evidence gap makes the activity undecidable — the evidence needed to answer the question was never produced, so neither release nor refusal can be justified." |

每页另有一句：“每个判断只针对接收方的一项工作、本次评估范围内的这一项，以及所列的模型版本；它不是‘模型好不好’的总评，
也不是‘某项检查通过了’。”（B§1：“Each is a statement about one activity, in an assessed scope, against a named
model version”；“A single ‘is the MEP model good?’ verdict would be useless here”。）

**判断旁并置的事实**：记录的旧证据行里同一组有 `requirement-semantics` 变化时，判断词下方写
“记录同时显示：和这一项放在一起评估的旧证据里，有 N 条的检查要求变了；记录不说明是放宽还是收紧。读这个判断时要一并看”。
N 是记录里的行数；界面不由此下结论。

**接收方的哪项工作（原标签“检查内容”已撤）** —— 名称依 Pack `activities[].label`，说明依 B§1
“What Architecture does next with it”。

| 记录里的代码 | 名称 | 说明 | 原文 |
| --- | --- | --- | --- |
| `builders-work-openings` | 土建预留开洞 | 要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。 | "Builder's-work openings"；"needs to know where MEP penetrates architectural fabric, so openings can be cut in walls, floors and roof" |
| `ceiling-and-bulkhead-geometry` | 吊顶反向图与包封布置 | 要知道交出方的设备在哪一层、在什么位置，才能围着它画吊顶分区和包封。 | "Reflected ceiling and bulkhead layout"；"needs to know where MEP equipment physically is, in which storey, so ceiling zones and bulkheads can be drawn around it" |
| `schedules-and-room-data-sheets` | 房间数据表与设备明细表 | 要每件设备都带有项目的资产标识，明细表才能按它编排。 | "Room data sheets and equipment schedules"；"needs each piece of equipment to carry the project's asset identity, so a schedule can be keyed to it" |

Pack 在界面上叫“交接判断规则”（原“检查清单”已撤）：Pack 自述 "states a reusable question: which production
activities a handover is deciding about, what evidence each needs, and how those evidence outcomes reach a verdict"。

**得出这个判断的读数** —— 记录的 `current_leaf_outcomes`，按它所在路径终点的证据要求查表；
出处 Pack `evidence_requirements[]` 的 `answers` / `acceptance_condition` / `outcomes`。

| 证据要求 / 读数 | 本界面的中文 | 原文依据 |
| --- | --- | --- |
| `asset-identity/satisfied` | 适用于它的项目资产标识要求评为通过，并且它确实被评估到 | "every element … that a bound requirement_key applies to evaluates PASS, and every such element is covered by an evaluation at all" |
| `asset-identity/unmet` | 项目资产标识的要求没有满足 | 同上（未满足） |
| `asset-identity/not-yet-evaluated` | 项目资产标识还没有评估到它 | "an element with no finding under the binding is not covered, and not-covered is never read as satisfied" |
| `in-model-position/satisfied` | 已归属到接收方模型里也有的楼层 | "each MEP element in the assessed scope is assigned to a storey Architecture also models" |
| `in-model-position/unmet` | 没有归属到楼层 | 同上（未满足） |
| `in-model-position/not-yet-evaluated` | 楼层归属还没有评估到它 | 同上（未覆盖） |
| `cross-model-alignment/confirmed` | 已有记录确认两侧模型对齐到共同的基准（按项目接受的方法，针对所列模型版本） | "a recorded alignment confirmation exists for the named model versions, produced by a method the project's Overlay accepts, and it reports the models aligned"；"sit on a common, agreed datum" |
| `cross-model-alignment/misaligned` | 对齐确认的结果是两侧模型没有对齐 | 同上 |
| `cross-model-alignment/not-yet-confirmed` | 还没有对齐确认 | 同上 |
| `penetration-determination/no-penetration` | 已有协调评审判定：它不穿过接收方模型里的任何构件。不穿过就不需要开洞，所以这条路径上开洞情况没有被评估——这不是“开洞没问题” | "a recorded coordination-review determination … naming no penetration"；决策树注释 "an element that penetrates nothing needs no opening, so opening-status is structurally ruled out along this path" |
| `penetration-determination/penetration-confirmed` | 已有协调评审判定：它穿过接收方模型里的构件 | "naming every architectural element the penetrating element passes through, each as an element_key of the consuming model version" |
| `penetration-determination/not-yet-determined` | 还没有协调评审判定它是否穿过接收方模型里的构件 | 同上 |
| `opening-status/cross-referenced` | 这一对：开洞已建在被穿过的构件上，并且有一条可核查的关联指回这个穿过它的构件 | "for the pair, the opening is modelled in the penetrated architectural element and a recorded cross-reference to this penetrating element exists" |
| `opening-status/modelled-not-cross-referenced` | 这一对：开洞已建在被穿过的构件上，但没有可核查的关联指回这个穿过它的构件 | 同上 |
| `opening-status/not-modelled` | 这一对：被穿过的构件上没有建出开洞 | 同上 |
| `opening-status/not-yet-determined` | 这一对：开洞情况的评审还没有完成 | 同上 |

**问题类型（Pack 的十个 `resolution_kind`，全部有说明）** —— 出处 Pack `resolution_routes[]`。
UNKNOWN 的五个都以“不是模型缺陷”开头，与 Pack 的 `next_action` 开头 "Not a model defect" 一致。

| 记录里的代码 | 本界面的中文 | 原文依据 |
| --- | --- | --- |
| `missing-project-asset-identity` | 缺少项目要求的资产标识 | "populate or correct the project-required asset-identity values" |
| `asset-identity-not-evaluated` | 不是模型缺陷：资产标识的评估没有覆盖到它 | "The gap is missing coverage of the evaluation itself, not a known failure in the model." |
| `mep-element-not-spatially-assigned` | 它没有楼层归属 | "host the element to its correct level and space … avoiding unhosted or unlevelled MEP components"；证据要求 "assigned to a storey" |
| `in-model-position-not-evaluated` | 不是模型缺陷：楼层归属的评估没有覆盖到它 | "run the in-model-position evaluation over the full assessed scope; where a specific element still produces no finding at all …" |
| `cross-model-misalignment` | 两侧模型没有对齐到共同的基准 | "re-acquire the project's shared coordination datum" |
| `cross-model-alignment-not-confirmed` | 不是模型缺陷：还没有人确认两侧模型对齐到共同的基准 | "The gap is that no confirmation has been produced yet, not a known misalignment." |
| `penetration-not-determined` | 不是模型缺陷：还没有协调评审判定它是否穿过接收方模型里的构件 | "The gap is that the determination has not been made yet, not a known defect." |
| `opening-not-verifiably-linked` | 开洞已建，但没有可核查的关联指回穿过它的这个构件 | "add or correct the cross-reference from the modelled architectural opening back to the penetrating MEP element" |
| `missing-corresponding-opening` | 它穿过的构件上没有建出对应的开洞 | "model the opening in the architectural model … in the architectural element this penetration passes through" |
| `opening-status-not-determined` | 不是模型缺陷：开洞情况的评审还没有完成 | "The gap is that this review has not been completed yet, not a known missing opening." |

**对这项工作的后果** —— 出处 Pack `resolution_routes[].consequence_kinds`。

| 记录里的代码 | 本界面的中文 |
| --- | --- |
| `work-cannot-start` | 这项工作不能开始 |
| `work-suspended` | 这项工作暂停 |
| `rework-risk` | 有返工风险 |
| `re-identification-and-reissue-risk` | 有重新标识的风险：引用这些标识的文件届时也须重新出具（第 14 节） |

**复检条件的标签**：`recheck_condition` 写作“复检要显示什么，这一项才算结束”。它说的是结束这一项的条件
（Pack 各行如 "The opening-status evaluation is re-run and reports … cross-referenced"），不是发起复检的前提。

**构件**：只用界面拿到的五个字段。名称为空写“模型中没有填写名称”；楼层为空写“模型中没有楼层归属”；
专业一律写“记录未提供专业信息；本界面不从模型标识推断专业”；所属模型旁写“这是模型标识，不是专业声明”，
并写它是“本次交接中交出方的模型”或“接收方的模型”（取自记录的模型版本比较，是交接角色，不是专业）。
IFC 类别：`IfcAirTerminal` 风口、`IfcChimney` 烟囱、`IfcDuctSegment` 风管段、`IfcRoof` 屋顶、`IfcSlab` 楼板、`IfcWall` 墙。

**检查尝试没有开始**：拒绝码 `team-mapping-decision-basis-illustrative` 写作
“项目条件未满足：处理团队的登记只是示意值”。程序故障是另一屏，写“这是程序自身的问题，
不是对任何项目或模型的判断”。

## 12. 2026-10-02 首次检查路径改掉和新增的说法

第 11 节里下面这些已被取代；路径与取舍见[首次检查路径](2026-10-02-doctor-first-check-path.md)，
领域依据是 BIM 约束原文第 2、3、4、8、9 节。

**判断词的主标签是中文**：`READY` 可以开始、`BLOCKED` 受阻、`UNKNOWN` 无法判断。标签不单独出现，
总是写成“<那项工作>：<标签>”。第 11 节的三句长说明只在“如何阅读”里出现一次。英文词在追溯信息里。

**改名**：吊顶那项工作叫“吊顶平面与包封布置”（不叫天花综合图）。“读数”改叫“这个结论依据的结果”。
“交接判断规则”“检查清单”都不再出现；默认处理角色旁写“规则给出的默认，不是指派”。

**楼层或空间归属**：`in-model-position` 的三个结果和两个问题类型都说“楼层或空间归属”，
不再说“接收方模型里也有的楼层”——绑定的规则只查构件是否包含在某个楼层或空间里。

**“不是已知的模型缺陷”**：无法判断的五个问题类型以“不是已知的……”开头（Pack 原话 "not a known defect"），
不再写“不是模型缺陷”。

**动作句和复检说法**（BIM 约束第 3 节的表，原样使用；只在记录的 `pack_id` 和 `pack_version`
是 `interdisciplinary-coordination-readiness` 0.1.0 时使用，否则显示 Pack 的英文原文）：

| 问题类型 | 要做什么 | 完成后拿什么复检 |
| --- | --- | --- |
| `missing-project-asset-identity` | 在源模型里给这个构件补上本项目约定的资产标识属性（见所列属性集和属性名），重新导出 | 重新发布的模型上，这个构件在所列每条要求下都通过，范围内没有构件漏评 |
| `asset-identity-not-evaluated` | 现有资产标识规则没有覆盖到这个构件，所以它有没有资产标识还没有被评估，不能判断是否缺少；这项工作能否开始也因此无法判断。先确认项目约定是否要求它具备资产标识，以及规则该不该覆盖到它。在确认之前，这不表示它必须具备资产标识。（产品裁定的句子取代表中原句；2026-10-02 再按收口文件第 6 节改成现在这句） | 范围内每个构件在所绑定的要求下都有评估结果 |
| `in-model-position-not-evaluated` | 这不是已知的模型缺陷，也不需要改模型。空间归属的检查规则没有覆盖到这个构件，需要扩展规则的适用范围 | 范围内每个构件在所绑定的要求下都有检查结果 |
| `penetration-not-determined` | 这不是已知的模型缺陷。还没有协调评审判定它是否穿过接收方的构件；需要开一次评审，记录“不穿过”或写明穿过哪些构件 | 针对所列模型版本，有一份评审判定记录 |
| `missing-corresponding-opening` | 在接收方模型里、被穿过的构件上建出洞口或竖井，不要做成交出方模型里的空洞。穿过几个构件就要几个洞口 | 这一对的开洞核查结果为“洞口已建且已关联”。只建洞不够 |
| `cross-model-alignment-not-confirmed` | 这不是已知的错位。还没有人按项目接受的方法确认两侧模型对齐；需要针对所列模型版本做一次并记录 | 对齐确认已做，结果为已对齐，写明模型版本 |
| `mep-element-not-spatially-assigned` | 在源模型里把构件放到正确的标高和空间上，重新导出 | 重新发布的模型上，这个构件的空间归属要求通过 |
| `cross-model-misalignment` | 重新获取项目共用的坐标基准，按共用原点重新导出（不靠移动几何），再按项目接受的方法重做对齐确认 | 针对新版本重做对齐确认，结果为已对齐 |
| `opening-not-verifiably-linked` | 在接收方模型里，给洞口补上指回穿过它的那个构件的关联。一个洞口供几个构件穿过，每个各要一条 | 这一对的关联核查结果为已关联 |
| `opening-status-not-determined` | 这不是已知的缺洞。开洞情况的评审没完成：洞口是否已建、是否已关联 | 核查给出明确结果（已关联／已建未关联／未建） |

**汇总**：按处理团队分组，团队取自记录里该分组的人员安排；返回数据的 `mode` 是 `fixture` 时标“示例处理团队”；
记录没有团队时写“记录未提供”。默认处理角色列在团队下面。计数单位是事项；受阻和无法判断分开计。

**检查没有开始**：`team-mapping-decision-basis-illustrative` 写作“项目条件未满足：由谁处理的安排不是项目作出的决定”，
并写：需要项目负责人实际决定系统原文点名的每个角色由谁担任，然后如实记录；随附的公开样例没有项目负责人，
对它而言这次拒绝就是正确的结果。不引导任何人改样例的设定，不列这次拒绝没有验证过的后续门槛。

## 13. 2026-10-02 首次检查路径的措辞修正

依据：收口文件第 6 节和 `005c43d` 领域审计“带着走的遗留项”第 1、2、4 条。只改措辞，不改结构、分组和取数。

- **烟囱资产标识的动作句**不再说“这不是缺资产标识”。没有任何检查看过它有没有这个属性集，所以说的是：
  还没有被评估，不能判断是否缺少；先确认项目约定与规则覆盖；在确认之前不表示它必须具备。
- **“重新发布”只指模型。** `re-identification-and-reissue-risk` 改说“引用这些标识的文件届时也要更新”
  （Checkpoint B：“rows keyed to something other than the asset tag have to be re-identified when tags arrive,
  and any document quoting them re-issued”）。
- **目录和页首的来源提示**跟上页面：一个结论的证据可能是真实检查的结果、模拟的检查结果或模拟的人工判定；
  具体是哪一种，看每个结论旁的“依据”一行，按逐条引用标明。两句都只说“可能是哪几种”：
  没有一份记录同时有这三种，整页级的句子不能断言这一页有什么。
- **楼层或空间归属的动作句**里“这类构件”改成“这个构件”。记录只到构件这一层。

## 14. 2026-10-03 真实检查路径（工作区入口）新增的说法

依据：产品任务书第 2、4、5、10 节，产品收口与设计指导第 3、4 节，BIM 选例表与取值决定原文（私有区，
本节不转录其私有标识），规则集说明 `rules/product-validation/README.md`，以及 `doctor/README.md` 里工作区返回数据的字段表。
路径与取舍见[真实检查路径](2026-10-03-doctor-real-check-path.md)。

三条规则：

- **这里没有交接判断。** 结果只用检查自己的三个词：`FAIL` 不通过、`PASS` 通过、`N/A` 不适用。
  “受阻／可以开始／无法判断”不出现在这些页面上；页首和每页开头写明没有交接判断。
- **界面不比较。** 配对、未再评估、新出现、哪些模型变了，都取返回数据的 `comparison`；界面只计数和排列。
  任何一句都不说“修复”“解决”“改善”。哪一次是“前一次”，是启动命令的指定，页面写明。
- **通过不带观察值。** 通过的检查结果 `actual` 为空，页面不写它读到了什么。

**入口名**：`workspace` 写作“工作区里的真实检查”。

**原因原文的中文**（按原文逐字匹配，原文始终在旁边）：

| 原文 | 本界面的中文 |
| --- | --- |
| The required property set does not exist | 所要求的属性集不存在（要补的是整个属性集，不是给已有属性填值） |
| Requirement satisfied. | 要求已满足 |
| The predefined type "NOTDEFINED" does not meet the required type | 预定义类型“NOTDEFINED”不属于要求的取值 |
| No applicable elements exist in this model. | 这个模型里没有这条要求适用的构件 |

**首页卡片（`WORKSPACE_HOME`）** —— 只在服务器带工作区启动时出现

| 键 | 本界面的中文 |
| --- | --- |
| `title` | 查看一次真实检查 |
| `body` | 启动服务器时指定了一个工作区，里面是一次已经跑完的检查：每个构件在每条要求下的结果。若同时指定了前一次运行，还可以看两次的前后对比。这里只有检查结果，没有交接判断。页面只查看这次已经跑完的检查，不能在页面上选择或更换模型。 |
| `action` | 查看这次检查 |
| `unknown` | 未能确认服务器是否指定了工作区（不等于没有工作区）。错误原文： |

**结果页与单条结果（`WORKSPACE`）**

| 键 | 本界面的中文 |
| --- | --- |
| `directoryNote` | 工作区只能在启动服务器时指定；这里不能选择、上传或更换模型。 |
| `directoryNone` | 服务器启动时没有指定工作区，所以这里没有可以查看的检查。要查看，用下面的命令重新启动服务器： |
| `startCommand` | python doctor/serve.py --workspace <工作区目录> [--prior <前一次运行的目录>] |
| `openRun` | 打开这次检查的结果 |
| `back` | ← 返回首页 |
| `backToList` | ← 返回结果列表 |
| `contextNoJudgement` | 只有检查结果，没有交接判断 |
| `contextRun` | 检查运行 |
| `resultTitle` | 一次真实检查的结果 |
| `noJudgement` | 这是一次检查的结果，不是交接判断：页面只说每个构件在每条要求下通过、不通过还是不适用，不对任何工作能否开始下结论。 |
| `summary` | 本次结果：共 {count} 条检查结果 |
| `unit` | 单位是条：一条是一个构件在一条要求下的结果；模型里没有这条要求适用的构件时，是整个模型的一条。 |
| `compareLink` | 看与前一次运行的对比 |
| `compareTeaser` | 服务器启动时还指定了前一次运行。两次结果的前后对比： |
| `checkedHeading` | 检查了什么 |
| `ruleTitle` | 要求 |
| `rulePredicate` | 这条规则要求 |
| `ruleExpected` | 规则的原话（英文） |
| `ruleOrigin` | 出处（返回数据的引文，英文原文） |
| `ruleLabels` | 返回数据的标签 |
| `productValidation` | 返回数据的标签（ProductValidation）标明：这是一条产品验证规则。 |
| `noRuleNotes` | 本界面没有为这条规则写中文说明；规则以返回数据里的英文原话为准。 |
| `noRequirement` | 返回数据没有这条结果所属要求的说明。 |
| `listHeading` | 逐条结果 |
| `filterLabel` | 按 IFC Tag、名称或 GlobalId 查找 |
| `filterAll` | 全部 |
| `filterNone` | 没有符合筛选条件的结果。 |
| `filterShown` | 显示 {shown} 条，共 {count} 条 |
| `columns.status` | 结果 |
| `columns.tag` | IFC Tag |
| `columns.name` | 名称 |
| `columns.class` | 类别 |
| `columns.storey` | 楼层（IFC） |
| `columns.model` | 模型 |
| `pickOne` | 从结果列表里选一条，在这里看它的详情。 |
| `detailKicker` | 一条真实检查结果 |
| `wholeModel` | 整个模型 |
| `resultHeading` | 结果 |
| `findHeading` | 回到 Revit 找哪个对象 |
| `actionHeading` | 要改什么 |
| `actionWhat` | 改成什么 |
| `actionReads` | 检查器读哪里 |
| `actionRevise` | 在 Revit 里改哪里 |
| `actionUndecided` | 还没有决定的 |
| `requirementHeading` | 具体要求与这次检查的观察 |
| `reason` | 原因（检查结果的原文） |
| `actual` | 观察值一栏 |
| `actualEmpty` | 检查结果中为空。 |
| `actualHidden` | 检查结果带有观察值；本页不显示取值。 |
| `recheckHeading` | 复检时看什么 |
| `passHeading` | 这条通过证明了什么 |
| `passProves` | 它证明： |
| `passDoesNotProve` | 它不证明： |
| `passNoValue` | 通过的检查结果不带它读到的值：只记录了“要求已满足”。 |
| `passUnwritten` | 通过只说明这条要求被判为满足；它能证明到哪里，本界面没有为这条规则写说明，请看规则原话。 |
| `notApplicable` | 不适用：这个模型里没有这条要求适用的构件。不适用不是通过。 |
| `failNotDefect` | 不满足这条产品验证规则，不等于原项目的交付缺陷。这条规则的来源以返回数据的标签（ProductValidation）和出处原文为准。 |
| `noFinding` | 这次检查里没有这一条结果。 |
| `identityHeading` | 追溯信息：这次检查的运行号、规则集版本与模型文件 |
| `findingTrace` | 追溯信息：这条结果的内部键 |
| `identity.run` | 检查运行号 |
| `identity.ruleset` | 规则集 |
| `identity.asOf` | 逻辑日期（运行配置给定，不是运行的时间） |
| `identity.checkers` | 检查程序 |
| `identity.models` | 模型 |
| `identity.modelId` | 模型 |
| `identity.declaredDiscipline` | 项目清单声明的专业 |
| `identity.filename` | 文件 |
| `identity.digest` | 文件内容摘要（SHA-256） |
| `identity.tagSource` | IFC Tag 的来源 |
| `identity.elementKey` | 追溯用内部键 |
| `identity.findingKey` | 检查结果键 |
| `identity.requirementKey` | 要求键 |
| `element.name` | 名称 |
| `element.class` | 类别 |
| `element.storey` | 楼层（IFC） |
| `element.model` | 所属模型 |
| `element.file` | 模型文件 |
| `element.globalId` | GlobalId |

**IFC Tag（`TAG_WORDS`）** —— `tag_source` 的三个值各有一句；表格里用短语，详情里用整句

| 键 | 本界面的中文 |
| --- | --- |
| `note` | IFC Tag 是导出时写进 IFC 的标记；Revit 导出的通常是构件的 ElementId。核对：在 Revit 里用“按 ID 选择”选中这个 ID，看选中对象的名称和类别是否与本页相同；相同再按它处理，不同就不要按这个 Tag 去改，改用 GlobalId 在 IFC 里定位。 |
| `byIdNotStorey` | 在 Revit 里按 ID 找对象，不要按楼层找：本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上。 |
| `storeyFromIfc` | 本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上，不要只按楼层去找。 |
| `sources.model-file` | 模型文件里这个构件没有写 Tag。 |
| `sources.model-file-not-located` | 没有找到这次检查读的那个模型文件，所以读不到 Tag。 |
| `sources.model-file-differs` | 工作区里的模型文件已经不是这次检查读的那个版本，所以不读取 Tag。 |
| `sourceNotCarried` | 返回数据没有说明这个模型的 Tag 从哪里读，所以没有 Tag。 |
| `modelLevel` | 这条结果针对整个模型，没有具体构件可找。 |
| `useGlobalId` | 在 IFC 里定位用 GlobalId。 |
| `short.model-file` | 文件里没有 Tag |
| `short.model-file-not-located` | 未找到模型文件 |
| `short.model-file-differs` | 模型文件版本不同 |
| `short.notCarried` | 来源未说明 |
| `short.modelLevel` | 整个模型 |

**引文的中文（`CITATION_GLOSSES`）** —— 只在返回数据的引文逐字等于原文时显示

| 原文 | 本界面的中文 |
| --- | --- |
| Product validation rule of this repository; not a project, owner, statutory or buildingSMART requirement. Values from IFC4 ADD2 TC1 IfcAirTerminalTypeEnum. | 本仓库的产品验证规则；不是项目、业主、法规或 buildingSMART 的要求。取值来自 IFC4 ADD2 TC1 的 IfcAirTerminalTypeEnum。 |

**规则说明（`RULE_NOTES`）** —— 只在返回数据的规则集是 `product-validation` 1.0、规则是 `PV-001` 时使用；出处为规则集说明与 BIM 原文，其他规则集或版本只显示英文原话

| 键 | 本界面的中文 |
| --- | --- |
| `PV-001.title` | 风口要声明四种预定义类型之一 |
| `PV-001.predicate` | 每个适用的风口（IfcAirTerminal）都要声明预定义类型，取值是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一。IFC4 还允许 USERDEFINED 和 NOTDEFINED；不接受它们是这条规则自己的决定，用它们的模型仍是有效的 IFC4。 |
| `PV-001.passProves` | 检查器按它的读取顺序取到的那一个值（类型上的值优先；类型声明 USERDEFINED 时是它的自由文本；类型什么也没说时才读构件实例），逐字等于 DIFFUSER、GRILLE、LOUVRE、REGISTER 四个值之一。 |
| `PV-001.passDoesNotProve[0]` | 取值正确：四个值中任何一个都会通过，写成 GRILLE 也会通过。 |
| `PV-001.passDoesNotProve[1]` | 类型和构件实例的取值一致：类型上是四个值之一时，实例上写的值不参与比较；类型是 LOUVRE、实例是 DIFFUSER，也会通过。 |
| `PV-001.passDoesNotProve[2]` | 规则不接受的 USERDEFINED 没有出现：类型声明 USERDEFINED 时，检查器比较的是它的自由文本，逐字、区分大小写；文本恰好是 LOUVRE 会通过，写成 louvre、Louvre 或前后带空格则不通过。 |
| `PV-001.passDoesNotProve[3]` | 墙上有对应的洞口。 |
| `PV-001.passDoesNotProve[4]` | 风口所在的模型与风口所在的墙所属的模型已经对齐。 |
| `PV-001.passDoesNotProve[5]` | 任何工作可以开始，包括吊顶和开洞工作。 |
| `PV-001.action.what` | 回到 Revit 源模型，让这个风口导出后的预定义类型是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一；重新导出 IFC，再检查。NOTDEFINED 等于什么都没说。 |
| `PV-001.action.reads` | 检查器先看导出的 IFC 里它的类型对象：类型上是四个值之一，比较类型上的值；类型声明 USERDEFINED，比较它的自由文本；类型什么也没说时，才读构件实例本身的值。这说的是检查器读 IFC 的顺序，不是 Revit 里该改的位置。 |
| `PV-001.action.revise` | 这个值在 Revit 里从哪里写出（类型还是实例、哪个参数、哪项导出设置），返回数据没有记录，本页不指定。改之前先在 Revit 里确认；如果决定在类型上改，会作用于这个类型的全部实例。 |
| `PV-001.action.undecided` | 取哪一个值、由谁决定和操作，返回数据都没有提供。规则只要求四个值之一，不判断哪一个对。 |
| `PV-001.recheck` | 用同一规则集版本、同一组模型和同一导出设置重新检查，看这个构件在这条要求下的结果。 |
| `PV-001.gaps[0]` | 风口所在的墙上的洞口：需要对照风口所在的模型和这面墙所属的模型做协调评审判定；这项检查不比较两个模型的构件。 |
| `PV-001.gaps[1]` | 风口所在的模型与风口所在的墙所属的模型是否对齐：需要一份对齐确认记录。 |
| `PV-001.gaps[2]` | 取值是否选对：分类判断要另行记录；检查通过不能反过来证明分类判断正确。 |
| `PV-001.reasonFreeText` | 引号里不是预定义类型的枚举值，而是自由文本：类型声明 USERDEFINED 时，检查器拿它的自由文本来比较。 |

**前后对比（`WORKSPACE_COMPARE`）**

| 键 | 本界面的中文 |
| --- | --- |
| `title` | 复检对比：同一项检查，前后两次运行 |
| `lede` | 下面的配对、未再评估和新出现都由返回数据给出，页面只计数和排列。 |
| `runsHeading` | 两次运行 |
| `prior` | 被指定为前一次的运行（启动时用 --prior 指定） |
| `current` | 本次运行（启动时用 --workspace 指定） |
| `order` | 哪一次在前，是启动服务器时的指定；返回数据本身不能证明先后。 |
| `same` | 两次运行的规则集、各条要求的谓词、检查程序、逻辑日期和模型组都相同；其中任何一项不同，系统都会拒绝对比，不给出任何一侧的结果。 |
| `changedHeading` | 一、什么变了 |
| `differs` | 两次结果不同的：{count} 条 |
| `differsNone` | 没有两次结果不同的。 |
| `unchanged` | 两次结果相同的：{count} 条 |
| `unchangedNone` | 没有两次结果相同的。 |
| `transition` | {prior} → {current}：{count} 条 |
| `rows` | {count} 条 |
| `notReEvaluated.label` | 只在前一次有结果的（本次没有再评估）：{count} 条 |
| `notReEvaluated.note` | 这些只有前一次的结果，本次没有再评估。它们不是通过。 |
| `newlyAppearing.label` | 只在本次有结果的（新出现）：{count} 条 |
| `newlyAppearing.note` | 这些结果前一次没有。 |
| `inCurrent.true` | 构件还在本次的构件清单里 |
| `inCurrent.false` | 构件不在本次的构件清单里 |
| `inCurrent.null` | 整个模型的一条结果，不针对构件 |
| `inPrior.true` | 构件在前一次的构件清单里 |
| `inPrior.false` | 构件不在前一次的构件清单里 |
| `inPrior.null` | 整个模型的一条结果，不针对构件 |
| `whyHeading` | 二、为什么会变：返回数据能说明的部分 |
| `changedModels` | 两次之间内容变了的模型（返回数据列出）： |
| `noChangedModels` | 返回数据没有列出内容变了的模型：两次读的是同样的模型文件。 |
| `unchangedModels` | 内容未变的模型： |
| `why` | 两次的规则集、要求谓词、检查程序和逻辑日期都相同。在返回数据比较过的这些输入里，两次之间不同的只有上面列出的模型文件内容；模型文件里改了哪些地方，返回数据没有逐项列出。 |
| `notInData` | 在 Revit 里改了什么、取值由谁决定、由谁操作，返回数据没有记录。 |
| `gapsHeading` | 三、还缺什么证据 |
| `passLink` | 一条通过证明了什么、没证明什么，见通过那几条的详情。 |
| `open` | 查看 |
| `detailHeading` | 和前一次运行比 |
| `detailPrior` | 前一次的结果 |
| `detailCurrent` | 本次的结果 |
| `detailNewly` | 前一次运行没有这一条结果：它是新出现的。 |
| `detailNone` | 返回数据的对比里没有这一条。 |
| `priorReason` | 前一次的原因（原文） |
| `currentReason` | 本次的原因（原文） |
| `noComparison` | 服务器启动时没有指定前一次运行，所以没有对比。要对比，启动时加上 --prior。 |
| `elementMissing` | 返回数据没有这个构件的可读信息 |

**对比被拒绝（`WORKSPACE_REFUSAL`）** —— 拒绝码与系统原文始终在折叠区

| 键 | 本界面的中文 |
| --- | --- |
| `title` | 这两次运行不能对比 |
| `lede` | 系统拒绝了这次对比，并列出了全部原因。这是对请求条件的答复，不是程序故障，也不是检查结果：任何一侧的检查结果都没有返回。 |
| `reasonsHeading` | 为什么不能对比 |
| `actionHeading` | 要能对比，需要什么 |
| `action[0]` | 两次运行要用同一规则集（同一版本、同一内容）、同一组要求、同一检查程序、同一逻辑日期和同一组模型；两次之间只能是模型文件的内容不同。 |
| `action[1]` | 确认启动时用 --prior 指定的确实是同一项检查的前一次运行；或者去掉 --prior 重新启动服务器，只看本次检查的结果。 |
| `scope` | 处理这些原因之后能否对比，以下一次返回为准。 |
| `original` | 系统返回的原文（英文）与拒绝码 |
| `code` | 拒绝码 |
| `unglossed` | 本界面没有这个原因的中文说明，见下面的原文。 |
| `noResult` | 没有任何结果、零问题统计或完成比例：被拒绝不是一次没有问题的检查。 |

**拒绝原因（`WORKSPACE_REFUSAL_REASONS`）** —— 九个拒绝码，各一句

| 键 | 本界面的中文 |
| --- | --- |
| `ruleset-id-differs` | 两次用的不是同一个规则集。 |
| `ruleset-version-differs` | 两次用的规则集版本不同。 |
| `ruleset-digest-differs` | 两次用的规则集内容不同（内容摘要不同）。 |
| `requirement-set-differs` | 两次评估的不是同一组要求。 |
| `requirement-semantics-not-recorded` | 有一次运行没有记录某条要求的谓词摘要，无法证明两次是同一个检查。 |
| `requirement-semantics-differs` | 同一条要求，两次的谓词不同：检查的内容改过。 |
| `checker-differs` | 两次的检查程序、版本或配置不同。 |
| `as-of-differs` | 两次运行的逻辑日期不同。 |
| `model-set-differs` | 两次检查的不是同一组模型。 |

**返回数据形状不符（`ENVELOPE_WORDS`）** —— 显示为程序故障，不是结果也不是拒绝

| 键 | 本界面的中文 |
| --- | --- |
| `missing` | outcome={outcome} 但缺少 {key} |
| `unexpected` | outcome={outcome} 却同时带有 {key} |

**顺带完成的两处措辞**（收口文件第 9 节）：

- 页首与目录的来源提示加上：“示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定。”
  仍只说证据“可能是”哪几种，不断言某份记录同时具有三类证据。
- `re-identification-and-reissue-risk` 改为“有重新标识的风险：引用这些标识的文件届时也须重新出具”。
  “重新发布”仍只指模型。

## 15. 2026-10-03 经理走查前的 C2 措辞修正

依据：BIM 对 #26 的三条约束（经技术总监转述）和产品经理关于首页的决定。路径与未关闭项见
[真实检查路径](2026-10-03-doctor-real-check-path.md)第 8 节。

| 位置 | 原句 | 现在 |
| --- | --- | --- |
| `RULE_NOTES.PV-001.passDoesNotProve[2]` | 两侧模型已经对齐。 | 风口所在的模型与风口所在的墙所属的模型已经对齐。 |
| `RULE_NOTES.PV-001.gaps[0]` | 风口对应的外墙洞口：需要两侧一起做协调评审判定；这项检查不比较两个模型的构件。 | 风口所在的墙上的洞口：需要对照风口所在的模型和这面墙所属的模型做协调评审判定；这项检查不比较两个模型的构件。 |
| `RULE_NOTES.PV-001.gaps[1]` | 两侧模型是否对齐：需要一份对齐确认记录。 | 风口所在的模型与风口所在的墙所属的模型是否对齐：需要一份对齐确认记录。 |
| `TAG_WORDS.note` 的后半句 | 这一对应只在个别对象上从 Revit 界面核对过，本页没有逐个核对：选中后请对一下名称和类别。 | 本页不能确认这一对应：选中后请核对名称和类别。 |
| `RULE_NOTES.PV-001.action.what` 的前半句 | 把它在 IFC 里的预定义类型写成 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一，重新导出，再检查。 | 回到 Revit 源模型，让这个风口导出后的预定义类型是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一；重新导出 IFC，再检查。 |
| `HOME.statusWithWorkspace`（新增，只在服务器带工作区启动时代替 `HOME.status`） | （带工作区时仍显示）当前为示例预览：尚不能导入自己的 Revit 模型，也不提供整体合规或可施工结论。 | 当前同时提供两样：启动服务器时指定的工作区里一次已经跑完的真实检查，以及模拟示例。页面上不能导入、选择或更换模型，也不提供整体合规或可施工结论。 |

三条规则：

- **两个模型按各自持有什么来称呼**（风口所在的模型、风口所在的墙所属的模型），不写专业名，也不从模型标识推断专业。
  不预设那面墙是外墙：BIM 第一批复核 W1 发现两个目标风口之一贴的是内墙，而且这些说明会挂在任何工作区的任何风口上，包括室内排风口。
  也不断言两个模型由两方持有：可能是同一方。
  页面上能看到的专业只有返回数据里项目清单声明的 `discipline`，原样显示在模型名旁。
- **Tag 的说明不讲核对历史。** 某个项目里核对过多少对象，返回数据里没有；页面每次都请人自己核对名称和类别。
- **“改成什么”从 Revit 源头说起**，不规定用哪个参数或导出机制；那仍是“还没有决定的”一行。

没有带工作区启动时，首页仍是原来的 `HOME.status`。

## 16. 2026-10-03 经理走查前的第二批小修（W2、W3、W5–W7 与首页）

依据：产品经理决定 [2026-10-03-pm-response-to-td-week-one.md](2026-10-03-pm-response-to-td-week-one.md) 第 1 节、技术总监的任务包，以及 BIM 第一批复核的 W2、W3、W5、W6、W7。**BIM 原文本工程师没有拿到**，以产品经理文件与技术总监报告的转述为准。

| 位置 | 原句 | 现在 |
| --- | --- | --- |
| W5：`WORKSPACE.columns.storey`、`WORKSPACE.element.storey` | 楼层 | 楼层（IFC） |
| W5：`TAG_WORDS.byIdNotStorey`（新增，构件带 Tag 时在“回到 Revit 找哪个对象”里出现） | （无） | 在 Revit 里按 ID 找对象，不要按楼层找：本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上。 |
| W2：`WORKSPACE.failNotDefect`（新增，只在不通过、且要求的标签含 ProductValidation 时，紧跟结论出现） | （无） | 不满足这条产品验证规则，不等于原项目的交付缺陷。这条规则的来源以返回数据的标签（ProductValidation）和出处原文为准。 |
| W5：`TAG_WORDS.storeyFromIfc`（新增，构件没有 Tag 时代替上一句：页面上没有可按的 ID） | （无） | 本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上，不要只按楼层去找。 |
| W3：`RULE_NOTES.PV-001.passProves` | 检查器读到的预定义类型属于 DIFFUSER、GRILLE、LOUVRE、REGISTER 四个值之一。 | 检查器按它的读取顺序取到的那一个值（类型上的值优先；类型声明 USERDEFINED 时是它的自由文本；类型什么也没说时才读构件实例），逐字等于 DIFFUSER、GRILLE、LOUVRE、REGISTER 四个值之一。 |
| W3：`RULE_NOTES.PV-001.passDoesNotProve` 新增第 2 条 | （无） | 类型和构件实例的取值一致：类型上是四个值之一时，实例上写的值不参与比较；类型是 LOUVRE、实例是 DIFFUSER，也会通过。 |
| W3：`RULE_NOTES.PV-001.userDefined` 移入 `passDoesNotProve` 第 3 条 | 检查器会先把 USERDEFINED 换成它的自由文本再比较：类型写的是 USERDEFINED、文本恰好拼成 LOUVRE，也会通过。规则不接受 USERDEFINED，但这项检查分不出这种情况。 | 规则不接受的 USERDEFINED 没有出现：类型声明 USERDEFINED 时，检查器比较的是它的自由文本，逐字、区分大小写；文本恰好是 LOUVRE 会通过，写成 louvre、Louvre 或前后带空格则不通过。 |
| W6：`RULE_NOTES.PV-001.action.where` 拆成 `reads`、`revise`；标签 `WORKSPACE.actionWhere`（改在哪里）拆成 `actionReads`（检查器读哪里）、`actionRevise`（在 Revit 里改哪里） | 检查器先读它的类型对象：类型上是四个值之一时，比较的是类型上的值；类型什么也没说时，才读构件本身的值。在 Revit 的类型上改值，会作用于这个类型的全部实例。 | 检查器读哪里：检查器先看导出的 IFC 里它的类型对象：类型上是四个值之一，比较类型上的值；类型声明 USERDEFINED，比较它的自由文本；类型什么也没说时，才读构件实例本身的值。这说的是检查器读 IFC 的顺序，不是 Revit 里该改的位置。<br>在 Revit 里改哪里：这个值在 Revit 里从哪里写出（类型还是实例、哪个参数、哪项导出设置），返回数据没有记录，本页不指定。改之前先在 Revit 里确认；如果决定在类型上改，会作用于这个类型的全部实例。 |
| W6：`RULE_NOTES.PV-001.action.undecided` | 取哪一个值、由谁决定和操作、用哪个 Revit 参数或导出设置写出这个值，返回数据都没有提供。规则只要求四个值之一，不判断哪一个对。 | 取哪一个值、由谁决定和操作，返回数据都没有提供。规则只要求四个值之一，不判断哪一个对。（参数和导出设置已在上一行说过，不再重复。） |
| W7：`REASON_GLOSSES` 中 NOTDEFINED 的原因 | 预定义类型“NOTDEFINED”不满足要求的类型 | 预定义类型“NOTDEFINED”不属于要求的取值 |
| W7：`RULE_NOTES.PV-001.reasonFreeText`（新增，原因引号里不是枚举值时紧跟原因出现） | （无） | 引号里不是预定义类型的枚举值，而是自由文本：类型声明 USERDEFINED 时，检查器拿它的自由文本来比较。 |
| Tag：`TAG_WORDS.note` | IFC Tag 是导出时写进 IFC 的标记；Revit 导出的通常是构件的 ElementId，可以在 Revit 里按 ID 选中它。本页不能确认这一对应：选中后请核对名称和类别。 | IFC Tag 是导出时写进 IFC 的标记；Revit 导出的通常是构件的 ElementId。核对：在 Revit 里用“按 ID 选择”选中这个 ID，看选中对象的名称和类别是否与本页相同；相同再按它处理，不同就不要按这个 Tag 去改，改用 GlobalId 在 IFC 里定位。 |
| 首页：`HOME.cannot[0]` | 导入自己的 Revit 或 IFC 模型 | 在页面上导入、选择或更换模型，包括自己的 Revit 或 IFC 模型 |
| 首页：`HOME.statusWorkspaceUnknown`（新增，问询工作区失败时代替 `HOME.status`） | （问询失败时仍显示）当前为示例预览：尚不能导入自己的 Revit 模型，也不提供整体合规或可施工结论。 | 未能确认服务器是否指定了工作区，所以这里没有真实检查的入口；这不等于没有工作区，错误原文在下面。模拟示例照常可看。页面上不能导入、选择或更换模型，也不提供整体合规或可施工结论。 |
| 首页：`WORKSPACE_HOME.body` 句末 | （无） | 页面只查看这次已经跑完的检查，不能在页面上选择或更换模型。 |
| 首页：`WORKSPACE_HOME.unknown` | 未能确认服务器是否指定了工作区： | 未能确认服务器是否指定了工作区（不等于没有工作区）。错误原文： |

几条依据和边界：

- **W3 的两条边界是实测，不是推断。** 用检查器所用的 IfcTester，对公开样例 `data/raw/Building-Hvac.ifc` 的一个风口改值后按
  `ids/product-validation_v1.0.ids` 检查：类型 `USERDEFINED` 文本 `LOUVRE` 通过；`louvre`、`Louvre`、` LOUVRE`、`LOUVRE ` 都不通过；
  类型 `LOUVRE`、实例 `DIFFUSER` 通过；类型 `NOTDEFINED`、实例 `LOUVRE` 通过。改过的文件只在临时目录里，没有进仓库。
- **W5 不把这个案例的事实写成通则。** 页面只说 IFC 的楼层“不一定”对得上 Revit 明细表的标高，不说标高为空（测试检查）。
- **W6 不指定改法。** “检查器读哪里”只描述读 IFC 的顺序；“在 Revit 里改哪里”说返回数据没有记录，类型上改的后果只作为条件句。
- **W7 的注释怎样触发。** 原因形如 `The predefined type "…" does not meet the required type`，引号里不是 IFC4 ADD2 TC1
  `IfcAirTerminalTypeEnum` 的六个值之一时，才在原因旁加这句；只在规则说明适用（product-validation 1.0 / PV-001）时判断。
- **W2 只跟着标签出现。** 不通过、且这条要求的 `labels` 含 `ProductValidation` 时出现一次，不是每屏的通用警告；其他页面没有这句（测试检查）。
