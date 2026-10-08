# Doctor BIM T1 结论修正：中英义务对照

日期：2026-10-09。负责：Product/UI Engineer。基线 `26a0f4f`，分支 `fix/doctor-bim-t1-wording`。
依据：BIM 10/9 逐条结论 [`2026-10-09-bim-review-t1-verdicts.csv`](2026-10-09-bim-review-t1-verdicts.csv)（随本分支提交），技术总监第 1 包。
状态：改后的句子都按 BIM 的建议改写，仍待 BIM 确认改后措辞。

“同一义务”的判断标准：两种语言要求读者做的事、承诺或否认的事、限定的范围相同；措辞、语序、标点不同不算。

## 结论

- 改了 9 个键，新增 1 个键（`RECHECK_ITEM.changedCondition`，文字是已有句子末尾的原样摘出）。改后中英文全部是同一义务。
- 没有改 Pack、规则、评估或复检判定逻辑。
- 不在本包：W2（E289，等 PM 裁定）；E021（C 通道）。

## 逐条

| BIM | 键 | 改前（中） | 改前（英） | 改后（中） | 改后（英） | 改后义务 |
| --- | --- | --- | --- | --- | --- | --- |
| E127（含义错误） | `CONSEQUENCE_KINDS.work-suspended` | 这项工作暂缓，等有结论再定 | This work is held until decided | 这项工作暂缓 | This work is on hold | 同一义务。只说这项工作暂缓，不再暗示还没有结论：这一后果也挂在 4 种“受阻”问题类型上，“受阻”本身就是结论 |
| E079（含义错误） | `CARRY_OVER_REASONS.determination-not-cited-by-this-record` | 模型版本没有变，本次记录没有再引用这份判定：它被别的判定取代了。 | The model version did not change, and this record no longer cites this determination: another determination replaced it. | 模型版本没有变，本次记录没有再引用这份判定；记录没有说明原因。 | The model version did not change, and this record no longer cites this determination; the record does not say why. | 同一义务。只陈述引擎核对过的两件事，不再断言“被别的判定取代” |
| E357 | `RULE_NOTES.PV-001.passProves`（括号内后半） | 类型什么也没说时才读构件实例；没有类型时，实例声明 USERDEFINED 也是它的自由文本 | the element instance only when the type says nothing, and with no type, a USERDEFINED instance's free text too | 类型什么也没说（没有类型、NOTDEFINED，或 USERDEFINED 没写文本）时才读构件实例，实例声明 USERDEFINED 时也是它的自由文本 | the element instance only when the type says nothing (no type, NOTDEFINED, or USERDEFINED with no text), and then a USERDEFINED instance's free text too | 同一义务。“什么也没说”的三种情形写全；把原来分开说的两层并成一句，避免同一条件重复出现 |
| E360 | `RULE_NOTES.PV-001.passDoesNotProve[2]`（中段） | 没有类型时，构件实例声明 USERDEFINED 也按它的自由文本比较。 | with no type, an element instance that declares USERDEFINED is compared by its free text as well. | 类型什么也没说（没有类型、NOTDEFINED，或 USERDEFINED 没写文本）时，构件实例声明 USERDEFINED 也按它的自由文本比较。 | when the type says nothing (no type, NOTDEFINED, or USERDEFINED with no text), an element instance that declares USERDEFINED is compared by its free text as well. | 同一义务 |
| E372 | `RULE_NOTES.PV-001.reasonFreeText`（后半） | 没有类型时，构件实例声明 USERDEFINED 也是这样。 | with no type, the same holds for an element instance that declares USERDEFINED. | 类型什么也没说（没有类型、NOTDEFINED，或 USERDEFINED 没写文本）时，构件实例声明 USERDEFINED 也是这样。 | when the type says nothing (no type, NOTDEFINED, or USERDEFINED with no text), the same holds for an element instance that declares USERDEFINED. | 同一义务 |
| E291 | `RECHECK_ITEM.changedCondition`（新增） | （无；同一句话只在第四节 `conditionNote` 末尾） | （无） | 结论变了，不等于原条件已满足。 | A changed conclusion does not mean the original condition is met. | 同一义务。文字是 `conditionNote` 末句的原样摘出；只在结论变化时紧跟结论出现，第四节原句保留 |
| E587 | `FIRST.problem`（标签） | 问题 | Problem | 情况 | Situation | 同一义务。标签后面常接“不是已知的模型缺陷：……”，“问题”与之语气相抵 |
| Q01 | `SOURCE_SUMMARY.lead` | 随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。 | …project settings such as teams are for demonstration, not for formal project decisions. | 随附的模拟示例，不是你的模型；团队和证据方法的接受等项目设定为演示用，不能用于正式项目决定。 | …project settings such as teams and the acceptance of evidence methods are for demonstration, not for formal project decisions. | 同一义务。点名证据方法的接受，它决定一条人工判定能否当证据 |
| L008（与 E195 统一） | `LOCAL_CHECK.home.cannot[1]`（英文） | 给出整体合规、可施工或“可以交付”的结论（不变） | Give an overall compliance, ready-to-build or "can be handed over" conclusion | 不变 | Give an overall compliance, ready-to-build or "ready to hand over" conclusion | 同一义务。英文与首页 `HOME.cannot[1]`（E195）用同一说法 |

E357／E360／E372 的依据：BIM 用 IfcTester 实测（合成 IFC4），类型存在但什么也没说时，实例的 USERDEFINED 自由文本同样参与比较。另外，Revit 导出的类型默认就是 NOTDEFINED，比“没有类型”更常见。

## 出现在哪些页面

| 键 | 页面 |
| --- | --- |
| E127 | 模拟示例的首次单项页、复检单项页（“对这项工作的后果”），在“受阻”和“无法判断”两种结论下都会出现 |
| E079 | 复检单项页的证据比较说明 |
| E357／E360／E372 | 中文和英文的工作区页面、本地检查结果页（PV-001 说明） |
| E291 | 复检单项页：结论较复检前有变化时，紧跟结论 |
| E587 | 首次结果卡片、首次单项页、复检单项页的“情况”一行 |
| Q01 | 每个模拟示例页的页首摘要 |
| L008 | 首页“现在还不能做什么”的第二条（开启本地检查时用本地检查的这一组） |

页面差异清单见 PR 描述。
