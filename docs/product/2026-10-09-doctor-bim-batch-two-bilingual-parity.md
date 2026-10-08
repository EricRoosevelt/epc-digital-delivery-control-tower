# Doctor BIM 第二批修正：中英义务对照（M1、W2–W8、W10）

日期：2026-10-09。负责：Product/UI Engineer。基线 `0f4300b`，分支 `fix/doctor-bim-batch-two`。
依据：[PM 对汇报（五）的裁定](2026-10-08-pm-response-to-td-5.md)、技术总监第 1 包（BIM 原文由用户转达）；格式参照
[行动义务对照](2026-10-04-doctor-bilingual-action-parity.md)。
状态：下列改后的句子**都未经 BIM 复核**。M1 的复核通过之前，受影响的模拟示例页不用于对外展示（PM 裁定）。

“同一义务”的判断标准：两种语言要求读者做的事、承诺或否认的事、限定的范围相同；措辞、语序、标点不同不算。

## 结论

- 本轮改 11 个键，新增 1 个键（`CONDITION_ENTRIES.no-recheck-condition.plainNotReady`）。改后中英文 12 处全部是同一义务。
- 改前中英文也是同一义务：它们错在同一处，就是 BIM 指出的含义。本轮两种语言一起改。
- 没有改 Pack、规则、评估逻辑或复检判定逻辑。W4 只决定页面显示哪一句，判断依据是记录里已有的 `prior_verdict`。
- 不在本轮：W1（Pack 路由，属于 C 通道）、W9（目前没有可达入口）。

## 逐条对照

| BIM | 键 | 改前（中） | 改前（英） | 改后（中） | 改后（英） | 改后义务 |
| --- | --- | --- | --- | --- | --- | --- |
| M1（P0） | `ACTIONS.in-model-position-not-evaluated.action` | 这不是已知的模型缺陷，也不需要改模型。空间归属的检查规则没有覆盖到这个构件，需要扩展规则的适用范围 | This is not a known model defect, and the model does not need changing. The spatial-assignment check rules do not reach this element; the rules' scope of application needs to be extended | 这不是已知的模型缺陷。它的空间归属目前还没有评估：空间归属的检查规则没有覆盖到这个构件。这一步是扩展规则的适用范围，让检查覆盖到它，而不是改模型；覆盖并运行之后，才知道要不要改模型 | This is not a known model defect. Its spatial assignment has not been evaluated yet: the spatial-assignment check rules do not reach this element. This step is to extend the rules' scope of application so that the check reaches it, not to change the model; only once it is covered and the check has run will it be known whether the model needs changing | 同一义务。三层意思两种语言都有：尚未评估；这一步是扩规则、让检查覆盖到它，不是改模型；覆盖并运行后才知道要不要改模型。不再断言模型不用改，也没有把“还没有结论”写成通过 |
| W2（E014） | `ACTIONS.missing-project-asset-identity.recheck` | 重新发布的模型上，这个构件在所列每条要求下都通过，范围内没有构件漏评 | On the reissued model, this element passes every requirement listed, and no element in the scope is left unevaluated | 重新发布的模型上，这个构件在所列每条要求下都通过 | On the reissued model, this element passes every requirement listed | 同一义务。复检义务收窄到这个构件，保留“通过”这个条件；不再要求全范围没有漏评。复检判定逻辑没有改 |
| W3（E025） | `ACTIONS.mep-element-not-spatially-assigned.action` | 在源模型里把构件放到正确的标高和空间上，重新导出 | In the source model, place the element on its correct level and in its correct space, then re-export | 在源模型里把构件放到正确的标高上（项目要求空间归属时，再放进对应的空间），重新导出 | In the source model, place the element on its correct level (and, where the project requires spatial assignment, in its corresponding space), then re-export | 同一义务。与规则的“楼层或空间”一致：标高必须放对，空间只在项目要求时才放 |
| W4（E120） | `CONDITION_ENTRIES.no-recheck-condition.plain` | 原记录没有复检条件：原来的判断没有留下待办。 | The original record had no recheck condition: the original conclusion left nothing outstanding. | 不变，只在原判断（`prior_verdict`）为 `READY` 时显示 | 不变，同左 | 同一义务。“没有留下待办”只在原判断为“可以开始”时成立 |
| W4（E120） | `CONDITION_ENTRIES.no-recheck-condition.plainNotReady`（新增） | （无） | （无） | 原记录没有给出复检条件。 | The original record gave no recheck condition. | 同一义务。只陈述记录没有给出复检条件，不推断原判断有没有待办。原判断不是 `READY`、或记录没有携带原判断时显示 |
| W5（E357／E360／E372） | `RULE_NOTES.PV-001.passProves` | …类型声明 USERDEFINED 时是它的自由文本；类型什么也没说时才读构件实例），逐字等于… | …a USERDEFINED type's free text; the element instance only when the type says nothing) is, character for character, … | …类型什么也没说时才读构件实例；没有类型时，实例声明 USERDEFINED 也是它的自由文本），逐字等于… | …the element instance only when the type says nothing, and with no type, a USERDEFINED instance's free text too) is, character for character, … | 同一义务。补上测得的读取行为，见下文 |
| W5 | `RULE_NOTES.PV-001.passDoesNotProve[2]` | 规则不接受的 USERDEFINED 没有出现：类型声明 USERDEFINED 时，检查器比较的是它的自由文本，逐字、区分大小写；文本恰好是 LOUVRE 会通过，… | That no USERDEFINED, which the rule does not accept, is present: when the type declares USERDEFINED, the checker compares its free text, character for character and case-sensitively; text that happens to be LOUVRE passes, … | 规则不接受的 USERDEFINED 没有出现：类型声明 USERDEFINED 时，检查器比较的是它的自由文本；没有类型时，构件实例声明 USERDEFINED 也按它的自由文本比较。比较逐字、区分大小写；文本恰好是 LOUVRE 会通过，… | That no USERDEFINED, which the rule does not accept, is present: when the type declares USERDEFINED, the checker compares its free text; with no type, an element instance that declares USERDEFINED is compared by its free text as well. The comparison is character for character and case-sensitive; text that happens to be LOUVRE passes, … | 同一义务 |
| W5 | `RULE_NOTES.PV-001.reasonFreeText` | 引号里不是预定义类型的枚举值，而是自由文本：类型声明 USERDEFINED 时，检查器拿它的自由文本来比较。 | What is in the quotation marks is not an enumeration value but free text: when the type declares USERDEFINED, the checker compares its free text. | 引号里不是预定义类型的枚举值，而是自由文本：类型声明 USERDEFINED 时，检查器拿它的自由文本来比较；没有类型时，构件实例声明 USERDEFINED 也是这样。 | What is in the quotation marks is not an enumeration value but free text: when the type declares USERDEFINED, the checker compares its free text; with no type, the same holds for an element instance that declares USERDEFINED. | 同一义务 |
| W6（E386） | `TAG_WORDS.note`（后半句） | …不同就不要按这个 Tag 去改：用 GlobalId 确认是哪个对象，再回到 Revit 源模型修改。 | …if they do not, do not change anything by this Tag: use the GlobalId to confirm which object it is, then make the change in the Revit source model. | …不同就不要按这个 Tag 去改：在 IFC 查看器里按 GlobalId 定位，读出名称、类型和位置，再在 Revit 里按这些找到对象并核对，然后在源模型里修改。 | …if they do not, do not change anything by this Tag: locate the object by its GlobalId in an IFC viewer, read its name, type and location, find the object in Revit by these and check it, then make the change in the source model. | 同一义务。改前的说法隐含 Revit 能直接按 GlobalId 找对象，Revit 没有这样的原生命令；改后给出一条能走通的路线 |
| W7（E145） | `DETAILS_WORDS.projectAssumption` | 这是本项目约定的要求，不是通用要求。 | This is a requirement agreed for this project, not a general one. | 这是本项目假定的要求（ProjectAssumption），不是通用要求。 | This is a requirement assumed for this project (ProjectAssumption), not a general one. | 同一义务。“约定”暗示各方已经同意，标签本身只说这是假定 |
| W8（E127） | `CONSEQUENCE_KINDS.work-suspended` | 这项工作暂停 | This work is suspended | 这项工作暂缓，等有结论再定 | This work is held until decided | 同一义务。“暂停”像是已经开工又停下；这里说的是先不开始，等有结论再定 |
| W10 | `REASON_GLOSSES`（The required property set does not exist） | 所要求的属性集不存在（要补的是整个属性集，不是给已有属性填值） | （英文不加释义，显示原因原文） | 所要求的属性集不存在（要让导出写出这个属性集以及其中所要求的属性，不是给已有属性填值） | （不变：原因原文） | 中文释义改为可执行的说法：让导出写出属性集和其中要求的属性。英文仍只显示原文，没有新增义务 |

### W5 的依据

“没有类型时，实例声明 USERDEFINED 也按自由文本比较”是测得的行为。依据是 `tests/test_product_validation_ruleset.py` 的读取表（IfcTester 0.8.5）：

- `occurrence-free-text`：实例 USERDEFINED、自由文本 LOUVRE、没有类型对象 → PASS；
- `occurrence-userdefined`：同样没有类型，自由文本 "Weather louvre" → FAIL。

类型为 NOTDEFINED、实例为 USERDEFINED 的组合没有测过，所以句子只说“没有类型时”。

### W4 的依据

- 判断由页面做，见 `recheck-model.js` 的 `conditionModel`：只看这一组记录的 `prior_verdict`，短说法“原记录没有复检条件”不变。
- 随附的 12 份示例记录里，`no-recheck-condition` 共出现 27 组，原判断全部是 `READY`。所以现有页面一句也不会变，这与技术总监对生产路径的核验一致。
- 测试 `NoRecheckConditionTests` 把这一点固定下来，并对 `BLOCKED`、`UNKNOWN`、未携带三种情况核对改后的句子。

## 出现在哪些页面

| 键 | 页面 |
| --- | --- |
| M1、W2、W3 | 模拟示例的首次结果列表（卡片折叠里）、首次单项页、复检列表、复检单项页（含“复检前留下的结束条件”） |
| W8 | 模拟示例的首次单项页、复检单项页（“对这项工作的后果”） |
| W7、W10 | 模拟示例单项页的“检查结果明细”（`finding_details`，R-005 系列） |
| W5、W6 | 中文工作区页面（检查结果页、检查结果详情页、对比页），以及本地 IFC 检查的结果页（它复用工作区的结果画面，`local-check.js`）；C2 走查固定用 `577620e`，不受影响 |
| W4 | 复检单项页的“原复检条件”一节；现有记录全部是 `READY`，所以没有页面变化 |

页面差异清单（除这些键外逐字不变的证明）见 PR 描述。
