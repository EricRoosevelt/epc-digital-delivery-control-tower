# BIM 分批条目索引：10/15 批

10/15 批是英文领域条目里除 10/8 批之外的其余，共 155 条，全部在原有 517 条之内。D6 列入 10/15 的另外几项（D2 第二入口的英文、本地 IFC 的规则选择与范围、留存／清理说明、3D 无几何与定位措辞）在 a5b89d0 里还不存在，没有条目可索引，见总览第 7 节。

本批：155 条英文条目（原文 0、原有 517 条内 155、#40 新增 0）。

列的含义见[总览](2026-10-05-bim-batch-index.md)。提交与 PR 对照见总览末尾。

### ASPECT_NOTES（6 条）— 复检：比较了哪些方面

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E045 | `onlyModelVersion` | Only the model version changed; that does not mean the check result's content changed. Nor does the record conclude whether this evidence can carry over to the new version. | 只有模型版本变了，不等于检查结果的内容变了。记录也不就“这条证据能否沿用到新版本”下结论。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 21 页（fixture/recheck ×21）；例 `#/fixture/recheck-both-reissued/recheck/5/0`；同页最多 ×6；zh 21 页 |
| E046 | `semanticsSameOutcome` | The check requirement was edited, and the check result reads the same as before — but it was reached under the edited requirement and cannot be treated as the same evidence. | 检查要求被修改过，检查结果读起来和原来一样——但它是按修改后的要求得出的，不能当作同一条证据。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 3 页（fixture/recheck ×3）；例 `#/fixture/recheck-semantics-changed/recheck/7/0`；同页最多 ×2；zh 3 页 |
| E047 | `semanticsAndContent` | The check requirement was edited and the check result content changed too: the change in result may come from the edit to the requirement (for example a relaxed requirement), so it cannot be taken to mean the model was fixed. The record does not say whether the requirement was relaxed or tightened. | 检查要求被修改过，检查结果内容也变了：结果的变化可能来自要求的修改（例如要求放宽），不能据此说模型修好了。记录不说明要求是放宽还是收紧。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 6 页（fixture/recheck ×6）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；同页最多 ×2；zh 6 页 |
| E048 | `contentUnderSameRequirement` | The check requirement did not change, and the check result content did. This row does not record whether the result got better or worse; see the current conclusion. | 检查要求没有变，检查结果内容变了。这一行不记录结果是变好还是变差，请看当前判断。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 3 页（fixture/recheck ×3）；例 `#/fixture/recheck-producing-reissued-content-changed/recheck/7/0`；同页最多 ×6；zh 3 页 |
| E049 | `checker` | The checker (the check program or its configuration) version differs: the same model and requirement may give a different result. | 检查程序（检查器或它的配置）版本不同：同样的模型和要求也可能得出不同结果。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E050 | `unrecognised` | There is an unrecognised aspect of change, so this page does not list the unchanged aspects. | 含有未识别的变化方面，本页因此不列“未变”的方面。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E045` `onlyModelVersion`）：
- en `#/fixture/recheck-both-reissued/recheck/5/0`：The citation changed key (the new key is the "corresponding evidence this record cites" above). A ch ‹ Only the model version changed; that does not mean the check result's content changed. Nor does the record conclude whether this evidence can carry over to the new version. › changed
- zh `#/fixture/recheck-both-reissued/recheck/5/0`：引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 ‹ 只有模型版本变了，不等于检查结果的内容变了。记录也不就“这条证据能否沿用到新版本”下结论。 › changed

页面上下文（`E046` `semanticsSameOutcome`）：
- en `#/fixture/recheck-semantics-changed/recheck/7/0`：The citation changed key (the new key is the "corresponding evidence this record cites" above). A ch ‹ The check requirement was edited, and the check result reads the same as before — but it was reached under the edited requirement and cannot be treated as the same evidence. › changed
- zh `#/fixture/recheck-semantics-changed/recheck/7/0`：引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 ‹ 检查要求被修改过，检查结果读起来和原来一样——但它是按修改后的要求得出的，不能当作同一条证据。 › changed

### CARRY_OVER_REASONS（14 条）— 复检：旧证据的去向

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E067 | `finding-equivalent` | There is exactly one corresponding check result; model version, check result content, check requirement and checker are the same, aspect by aspect. | 对应的检查结果只有一条，模型版本、检查结果内容、检查要求、检查程序逐项相同。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 50 页（fixture/recheck ×40; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×6；zh 50 页 |
| E068 | `finding-changed` | There is exactly one corresponding check result; compared aspect by aspect, at least one differs. | 对应的检查结果只有一条，逐项比较后至少有一个方面不同。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 53 页（fixture/recheck ×43; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×6；zh 53 页 |
| E069 | `no-counterpart-in-the-cited-run` | In the validation run this record rests on, this element has no check result under this requirement. | 本次记录依据的验证运行里，这个构件在这条要求下没有检查结果。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E070 | `counterpart-not-cited-under-the-current-binding` | The validation run has a corresponding check result, but this record does not cite it. | 验证运行里有对应的检查结果，但本次记录没有引用它。 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E071 | `sealed-citation-has-no-comparison-basis` | When the original record was sealed it kept no comparison basis for this citation (a record from an older version). This page will not make one up from the current rules, so it can only say honestly that it cannot compare. | 原记录封存时没有保存这条引用的比较依据（旧版本的记录）。本页不会用当前规则去补造，所以只能如实显示无法比较。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 26 页（fixture/recheck ×16; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×6；zh 26 页 |
| E072 | `comparison-basis-version-unknown` | The comparison basis the original record kept is of a version this system does not recognise. | 原记录保存的比较依据，是本系统不认识的版本。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E073 | `subject-not-present` | The element this evidence is about is no longer in this record (where it went: see "the reason the record gives"). An element that is gone is not fixed. | 这条证据所针对的构件，在本次记录里已经不在（去向见“记录给出的原因”）。构件不在不等于已修复。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 26 页（fixture/recheck ×16; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 26 页 |
| E074 | `counterpart-not-unique` | This time there is more than one candidate corresponding check result, and the system does not choose between them (all candidates: see "the reason the record gives"). | 本次有不止一条候选的对应检查结果，系统不从中挑选（全部候选见“记录给出的原因”）。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E075 | `requirement-semantics-basis-unavailable` | The sealed side or the current side has no comparison basis for the check requirement. | 封存一方或当前一方没有“检查要求”的比较依据。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E076 | `comparison-basis-incomplete` | The sealed side or the current side lacks part of the comparison basis (model version, check result content digest or checker fingerprint). | 封存一方或当前一方缺少部分比较依据（模型版本、检查结果内容摘要或检查程序指纹）。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E077 | `determination-same-reference-same-content` | The same determination: the same reference and the same content digest. | 同一份判定：引用相同，内容摘要也相同。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 50 页（fixture/recheck ×40; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 50 页 |
| E078 | `determination-content-changed-under-the-same-reference` | The same reference, but the determination's content is no longer what the original record read (made again, re-attributed or re-signed). The new determination is read as evidence as usual; it just cannot be called the same determination as the original. | 引用相同，但判定的内容已经不是原记录读到的那一份（被重新作出、重新归属或重新签署）。新判定照常作为证据读取，只是不能说它和原判定是同一份。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E079 | `determination-not-cited-by-this-record` | The model version did not change, and this record no longer cites this determination: another determination replaced it. | 模型版本没有变，本次记录没有再引用这份判定：它被别的判定取代了。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 21 页（fixture/recheck ×11; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 21 页 |
| E080 | `determination-not-attributable-to-this-context` | The model version has changed, and the original determination was made against the old version, so it cannot be attributed to the current one. The evidence is not missing and the original determination is not wrong; a determination against the current version is needed. | 模型版本已经变化，原判定是针对旧版本作出的，不能归到当前版本。不是证据不存在，也不是原判定错误；需要针对当前版本的判定。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 50 页（fixture/recheck ×40; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 50 页 |

页面上下文（`E067` `finding-equivalent`）：
- en `#/fixture/recheck-requirement-relaxed`：finding-equivalent ‹ There is exactly one corresponding check result; model version, check result content, check requirement and checker are the same, aspect by aspect. › finding-changed
- zh `#/fixture/recheck-requirement-relaxed`：finding-equivalent ‹ 对应的检查结果只有一条，模型版本、检查结果内容、检查要求、检查程序逐项相同。 › finding-changed

页面上下文（`E068` `finding-changed`）：
- en `#/fixture/recheck-requirement-relaxed`：finding-changed ‹ There is exactly one corresponding check result; compared aspect by aspect, at least one differs. › no-counterpart-in-the-cited-run
- zh `#/fixture/recheck-requirement-relaxed`：finding-changed ‹ 对应的检查结果只有一条，逐项比较后至少有一个方面不同。 › no-counterpart-in-the-cited-run

### CARRY_OVER_STATES（12 条）— 复检：旧证据的去向

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E081 | `equivalent.label` | Comparison basis unchanged | 比较依据一致 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×8；zh 68 页 |
| E082 | `equivalent.meaning` | This old evidence has exactly one counterpart in this record, and every aspect compared is the same.  | 这条旧证据在本次记录里有唯一对应的一条，逐项比较都相同。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 58 页（fixture/recheck ×53; fixture/result ×5）；例 `#/fixture/recheck-requirement-relaxed`；zh 58 页 |
| E083 | `equivalent.caveat` | It only means the evidence need not be gathered again because its citation changed key; it does not mean the whole handover needs no review. | 这只说明不必因为引用换了键而重新收集这条证据，不代表整个交接不用复核。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 58 页（fixture/recheck ×53; fixture/result ×5）；例 `#/fixture/recheck-requirement-relaxed`；zh 58 页 |
| E084 | `changed.label` | Comparison basis changed | 比较依据有变化 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 53 页（fixture/recheck ×43; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×7；zh 53 页 |
| E085 | `changed.meaning` | This old evidence has exactly one counterpart in this record, but at least one aspect differs.  | 这条旧证据在本次记录里有唯一对应的一条，但至少有一个方面不同。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 45 页（fixture/recheck ×39; fixture/result ×6）；例 `#/fixture/recheck-requirement-relaxed`；zh 45 页 |
| E086 | `changed.caveat` | Even if the result reads the same, it still counts as changed; which aspects changed is said on the row. | 结果读起来相同，也仍然算有变化；变了的是哪些方面，见这一条的说明。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 45 页（fixture/recheck ×39; fixture/result ×6）；例 `#/fixture/recheck-requirement-relaxed`；zh 45 页 |
| E087 | `no-counterpart.label` | No counterpart found | 未找到对应证据 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 51 页（fixture/recheck ×41; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×3；zh 51 页 |
| E088 | `no-counterpart.meaning` | It can be compared, but this record cites no evidence corresponding to it.  | 可以比较，但本次记录没有引用与它对应的证据。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 43 页（fixture/recheck ×37; fixture/result ×6）；例 `#/fixture/recheck-both-reissued`；zh 43 页 |
| E089 | `no-counterpart.caveat` | No counterpart does not mean the problem was fixed. | 没有对应证据不代表问题已修复。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 43 页（fixture/recheck ×37; fixture/result ×6）；例 `#/fixture/recheck-both-reissued`；zh 43 页 |
| E090 | `not-provable.label` | Not enough basis to compare | 现有依据不足以比较 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 32 页（fixture/recheck ×22; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×7；zh 32 页 |
| E091 | `not-provable.meaning` | The comparison itself cannot be made, so it can be called neither unchanged nor changed.  | 比较本身无法建立，所以既不能说一致，也不能说变了。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 16 页（fixture/recheck ×14; fixture/result ×2）；例 `#/fixture/recheck-member-gone`；zh 16 页 |
| E092 | `not-provable.caveat` | This is "cannot be compared", not "evidence missing", and not "no counterpart". | 这是“无法比较”，不是“证据缺失”，也不是“没有对应证据”。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 16 页（fixture/recheck ×14; fixture/result ×2）；例 `#/fixture/recheck-member-gone`；zh 16 页 |

页面上下文（`E081` `equivalent.label`）：
- en `#/fixture/recheck-requirement-relaxed`：When reading a recheck result ‹ "Comparison basis unchanged" does not mean the whole handover needs no review. › An element that is gone, or evidence with no counterpart, does not mean the problem was fixed.
- zh `#/fixture/recheck-requirement-relaxed`：equivalent ‹ 比较依据一致 › changed

页面上下文（`E082` `equivalent.meaning`）：
- en `#/fixture/recheck-requirement-relaxed`：What "Comparison basis unchanged" means ‹ This old evidence has exactly one counterpart in this record, and every aspect compared is the same. It only means the evidence need not be gathered again because its citation changed key; it does not mean the whole handover needs no review. › What "Comparison basis changed" means
- zh `#/fixture/recheck-requirement-relaxed`：“比较依据一致”是什么意思 ‹ 这条旧证据在本次记录里有唯一对应的一条，逐项比较都相同。这只说明不必因为引用换了键而重新收集这条证据，不代表整个交接不用复核。 › “比较依据有变化”是什么意思

### CHANGED_ASPECTS（4 条）— 复检：比较了哪些方面

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E093 | `model-version` | model version | 模型版本 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 182 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; fixture/first ×2; fixture/list ×1）；例 `#/fixture`；同页最多 ×20；zh 179 页 |
| E094 | `finding-content` | check result content | 检查结果内容 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 74 页（fixture/recheck ×64; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×12；zh 20 页 |
| E095 | `requirement-semantics` | check requirement | 检查要求 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 75 页（fixture/recheck ×64; fixture/result ×10; fixture/list ×1）；例 `#/fixture`；同页最多 ×12；zh 20 页 |
| E096 | `checker` | checker | 检查程序 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 38 页 |

页面上下文（`E093` `model-version`）：
- en `#/fixture`：The same record after a recheck: neither model was re-issued, yet a conclusion changed. Which one ch ‹ About this example This example was given: one cited check requirement was relaxed; neither the handing-over nor the receiving side's model version changed. › Step 2The models did not change, but a handover conclusion didThe same record after a recheck: neith
- zh `#/fixture/recheck-requirement-relaxed`：model-version ‹ 模型版本 › finding-content

页面上下文（`E094` `finding-content`）：
- en `#/fixture/recheck-requirement-relaxed`：Comparison basis unchanged × 7Only the citation's key changed × 7 ‹ Comparison basis changed × 2check result content, check requirement changed; model version, checker unchanged. × 2 › Check-result citation (9 rows)Comparison basis unchanged × 7Only the citation's key changed × 7Compa
- zh `#/fixture/recheck-requirement-relaxed`：finding-content ‹ 检查结果内容 › requirement-semantics

### DISPOSITIONS（5 条）— 复检：构件去向

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E150 | `present` | Still in this check's scope; conclusion and condition are read separately | 仍在本次检查范围内；判断与条件另看 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 20 页；同句（en）：DISPOSITION_ENTRIES.present.text |
| E151 | `element-deleted-in-reissued-model` | Deleted in the re-issued model; that is not a fix | 在重发模型中删除，不等于修复 | 界面文字；en #34 `50d129b`；zh #13 `55e90ba` | en 23 页（fixture/recheck ×13; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×5；zh 23 页；同句（en）：DISPOSITION_ENTRIES.element-deleted-in-reissued-model.text |
| E152 | `element-out-of-subject-class` | No longer of this activity's subject classes; that is not a fix | 已不属于此活动对象类别，不等于修复 | 界面文字；en #34 `50d129b`；zh #13 `55e90ba` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页；同句（en）：DISPOSITION_ENTRIES.element-out-of-subject-class.text |
| E153 | `pairing-no-longer-derived` | These two elements are no longer paired for checking; that does not mean the opening was added | 这两个构件现在不再被配成一对来检查，不等于开洞已补 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 31 页（fixture/recheck ×21; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×4；zh 31 页；同句（en）：DISPOSITION_ENTRIES.pairing-no-longer-derived.text |
| E154 | `outside-declared-scope` | This scope was not declared this time; that does not mean the problem is gone | 本次未声明该范围，不等于问题解除 | 界面文字；en #34 `50d129b`；zh #13 `55e90ba` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页；同句（en）：DISPOSITION_ENTRIES.outside-declared-scope.text |

页面上下文（`E150` `present`）：
- en `#/fixture/recheck-requirement-relaxed`：The items in the record before the recheck (13), and where they stand now ‹ Still in this check's scope; conclusion and condition are read separately × 13 › The old evidence cited before the recheck (15 rows), compared with this record
- zh `#/fixture/recheck-requirement-relaxed`：复检前记录里的事项（13 个），现在的情况 ‹ 仍在本次检查范围内；判断与条件另看 × 13 › 复检前引用的旧证据（15 条），和本次记录比较的结果

页面上下文（`E151` `element-deleted-in-reissued-model`）：
- en `#/fixture/recheck-requirement-relaxed`：element-deleted-in-reissued-model ‹ Deleted in the re-issued model; that is not a fix › element-out-of-subject-class
- zh `#/fixture/recheck-requirement-relaxed`：element-deleted-in-reissued-model ‹ 在重发模型中删除，不等于修复 › element-out-of-subject-class

### DISPOSITION_ENTRIES（10 条）— 复检：构件去向

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E155 | `present.text` | Still in this check's scope; conclusion and condition are read separately | 仍在本次检查范围内；判断与条件另看 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 20 页；同句（en）：DISPOSITIONS.present |
| E156 | `present.next` | See the current place the record gives below: the conclusion now, the next step and the handling role all follow it. | 看下面记录给出的当前情况：现在的判断、下一步和处理角色都以它为准。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E157 | `element-deleted-in-reissued-model.text` | Deleted in the re-issued model; that is not a fix | 在重发模型中删除，不等于修复 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 23 页（fixture/recheck ×13; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×5；zh 23 页；同句（en）：DISPOSITIONS.element-deleted-in-reissued-model |
| E158 | `element-deleted-in-reissued-model.next` | The record gives no next step for a deleted element. Check in the source model whether this deletion was an intended design change; this preview cannot record that confirmation. | 记录没有为已删除的构件给出下一步。请在源模型里核对这次删除是不是有意的设计变更；本预览不能记录这种确认。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 3 页（fixture/recheck ×3）；例 `#/fixture/recheck-member-gone/recheck/0/0`；zh 3 页 |
| E159 | `element-out-of-subject-class.text` | No longer of this activity's subject classes; that is not a fix | 已不属于此活动对象类别，不等于修复 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页；同句（en）：DISPOSITIONS.element-out-of-subject-class |
| E160 | `element-out-of-subject-class.next` | The record gives no next step for it. Check whether the element's class (the export mapping) was changed on purpose; a changed class only means this activity no longer checks it. | 记录没有为它给出下一步。请核对构件的类别（导出映射）是不是有意改变；类别变了只说明本活动不再检查它。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E161 | `pairing-no-longer-derived.text` | These two elements are no longer paired for checking; that does not mean the opening was added | 这两个构件现在不再被配成一对来检查，不等于开洞已补 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 31 页（fixture/recheck ×21; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×4；zh 31 页；同句（en）：DISPOSITIONS.pairing-no-longer-derived |
| E162 | `pairing-no-longer-derived.next` | The record gives no next step for this pair. Check whether the basis that stopped them being paired (see "the reason the record gives") is a conclusion you accept; the original problem has not been shown to be fixed. | 记录没有为这一对构件给出下一步。请核对让它不再被配对的那份依据（见“记录给出的原因”）是不是你认可的结论；原来的问题没有被证明已修复。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 11 页（fixture/recheck ×11）；例 `#/fixture/recheck-both-reissued/recheck/2/0`；zh 11 页 |
| E163 | `outside-declared-scope.text` | This scope was not declared this time; that does not mean the problem is gone | 本次未声明该范围，不等于问题解除 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页；同句（en）：DISPOSITIONS.outside-declared-scope |
| E164 | `outside-declared-scope.next` | This element was not checked again this time. For a conclusion, a new recheck that includes it is needed; this preview cannot start one. | 这个构件本次没有被重新检查。需要结论时，要重新发起一次包含它的复检；本预览不能发起。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E155` `present.text`）：
- en `#/fixture/recheck-requirement-relaxed`：The items in the record before the recheck (13), and where they stand now ‹ Still in this check's scope; conclusion and condition are read separately × 13 › The old evidence cited before the recheck (15 rows), compared with this record
- zh `#/fixture/recheck-requirement-relaxed`：复检前记录里的事项（13 个），现在的情况 ‹ 仍在本次检查范围内；判断与条件另看 × 13 › 复检前引用的旧证据（15 条），和本次记录比较的结果

页面上下文（`E157` `element-deleted-in-reissued-model.text`）：
- en `#/fixture/recheck-requirement-relaxed`：element-deleted-in-reissued-model ‹ Deleted in the re-issued model; that is not a fix › element-out-of-subject-class
- zh `#/fixture/recheck-requirement-relaxed`：element-deleted-in-reissued-model ‹ 在重发模型中删除，不等于修复 › element-out-of-subject-class

### ELEMENT_WORDS（7 条）— 构件卡片用语

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E165 | `unnamed` | No name filled in in the model | 模型中没有填写名称 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E166 | `noFacts` | The record returned nothing readable about this element | 记录没有返回这个构件的可读信息 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E167 | `noStorey` | No storey assignment in the model | 模型中没有楼层归属 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 37 页（fixture/recheck ×21; fixture/result ×12; fixture/item ×2; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 13 页 |
| E168 | `noDiscipline` | The record gives no discipline; this interface does not infer one from a model identifier | 记录未提供专业信息；本界面不从模型标识推断专业 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 157 页（fixture/recheck ×131; fixture/item ×26）；例 `#/fixture/member-evidence/item/0/2/0`；同页最多 ×2；zh 157 页 |
| E169 | `modelIsNotDiscipline` | This is a model identifier, not a statement of discipline | 这是模型标识，不是专业声明 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 157 页（fixture/recheck ×131; fixture/item ×26）；例 `#/fixture/member-evidence/item/0/2/0`；同页最多 ×2；zh 157 页 |
| E170 | `noClassName` | (IFC class) | 本界面没有这个类别的中文名 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 199 页（fixture/recheck ×141; fixture/item ×26; fixture/result ×12; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3）；例 `#/fixture/member-evidence`；zh 0 页（未渲染到） |
| E171 | `naming` | The name is taken from the model file itself; it may be empty or shared with other elements. To find it in the model, use the GlobalId. | 名称取自模型文件本身，可能为空，也可能与别的构件重名；要在模型里定位，请用 GlobalId。 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 157 页（fixture/recheck ×131; fixture/item ×26）；例 `#/fixture/member-evidence/item/0/2/0`；zh 157 页 |

页面上下文（`E167` `noStorey`）：
- en `#/fixture/member-evidence`：house - chimney: IfcChimney (IFC class) · 00 groundfloor · model hvac ‹ house - roof: IfcRoof (IFC class) · No storey assignment in the model · model architecture › Simulated human determination
- zh `#/fixture/member-evidence/item/0/4/0`：屋顶 IfcRoof ‹ 模型中没有楼层归属 › architecture：本次交接中接收方的模型这是模型标识，不是专业声明

页面上下文（`E168` `noDiscipline`）：
- en `#/fixture/member-evidence/item/0/2/0`：Discipline ‹ The record gives no discipline; this interface does not infer one from a model identifier › GlobalId
- zh `#/fixture/member-evidence/item/0/2/0`：专业 ‹ 记录未提供专业信息；本界面不从模型标识推断专业 › GlobalId

### EXAMPLES（6 条）— 示例目录说明

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E172 | `member-evidence.step` | Step 1 | 第一步 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 1 页（fixture/list ×1）；例 `#/fixture`；zh 1 页 |
| E173 | `member-evidence.question` | The handing-over side has handed over its model: which items need dealing with, who deals with each, and what does each one need? | 交出方交了模型：有哪些事项要处理，各由谁处理，每一项要做什么？ | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 1 页（fixture/list ×1）；例 `#/fixture`；zh 1 页 |
| E174 | `member-evidence.given` | This example was given: the bundled sample project's two models; the handling teams, and the human determinations (whether something passes through, the state of openings, whether the two models are aligned), set by the example. | 这个示例被给了：随附样例项目的两份模型；处理团队的安排，以及人工判定（是否穿过、洞口情况、两侧模型是否对齐），由示例设定。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 1 页（fixture/list ×1）；例 `#/fixture`；zh 1 页 |
| E175 | `recheck-requirement-relaxed.step` | Step 2 | 第二步 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 1 页（fixture/list ×1）；例 `#/fixture`；zh 1 页 |
| E176 | `recheck-requirement-relaxed.question` | The same record after a recheck: neither model was re-issued, yet a conclusion changed. Which one changed, and why? | 同一份记录复检之后：两侧模型都没有重新发布，却有判断变了。变的是哪一项，为什么？ | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 1 页（fixture/list ×1）；例 `#/fixture`；zh 1 页 |
| E177 | `recheck-requirement-relaxed.given` | This example was given: one cited check requirement was relaxed; neither the handing-over nor the receiving side's model version changed. | 这个示例被给了：一条被引用的检查要求放宽了；交出方和接收方的模型版本都没有变。 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 1 页（fixture/list ×1）；例 `#/fixture`；zh 1 页 |

页面上下文（`E172` `member-evidence.step`）：
- en `#/fixture`：Each example is one check record. The evidence for a conclusion may be a real check result, a simula ‹ Step 1 › A first check: the model was handed over, and these items were found
- zh `#/fixture`：每个示例是一份检查记录。一个结论的证据可能是真实检查的结果，可能是模拟的检查结果，也可能是模拟的人工判定；具体是哪一种，看结果页和事项页每个结论旁的“依据”一行，按逐条引用标明。示例中的项目设定，包括 ‹ 第一步 › 一次首次检查：交了模型，发现这些事项

页面上下文（`E173` `member-evidence.question`）：
- en `#/fixture`：A first check: the model was handed over, and these items were found ‹ The handing-over side has handed over its model: which items need dealing with, who deals with each, and what does each one need? › About this example
- zh `#/fixture`：一次首次检查：交了模型，发现这些事项 ‹ 交出方交了模型：有哪些事项要处理，各由谁处理，每一项要做什么？ › 示例说明

### HOME（10 条）— 首页标题与入口说明

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E184 | `title` | Items still to be dealt with in a model handover | 查看模型交接中仍需处理的事项 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 6 页（home ×6）；例 `#/`；zh 6 页 |
| E185 | `lede` | For a BIM manager: what a pre-handover check found; after a recheck, which conclusions changed, which items still need dealing with, which elements each one involves, what it rests on, and what to do next. | 帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 6 页（home ×6）；例 `#/`；zh 6 页 |
| E189 | `example.title` | Look at a simulated example | 看一个模拟示例 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 6 页（home ×6）；例 `#/`；zh 6 页 |
| E190 | `example.body` | Start from a first check: find the items that need dealing with, and see which elements they involve, what to do, who deals with it and what a recheck must show; then see how the same item changed after a recheck. What is simulated in the example is marked where it appears. | 从一次首次检查出发：找到需要处理的事项，看清涉及的构件、要做什么、由谁处理、完成后拿什么复检；然后再看同一事项复检后的变化。示例里模拟的内容，页面上逐处标明。 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 6 页（home ×6）；例 `#/`；zh 6 页 |
| E191 | `example.action` | Choose a simulated example | 选择模拟示例 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 7 页（home ×6; fixture/list ×1）；例 `#/`；zh 6 页；同句（en）：DIRECTORY.exampleTitle |
| E192 | `attempt.title` | See the check attempt on the bundled project | 查看随附项目的检查尝试 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 6 页（home ×6）；例 `#/`；zh 6 页 |
| E193 | `attempt.body` | The repository comes with a sample project. The check attempt on it did not start an assessment; this explains why. It is not an import, and you cannot swap in your own model. | 仓库随附一个样例项目。对它的检查尝试没有开始评估；这里说明原因。这不是导入入口，不能换成自己的模型。 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 6 页（home ×6）；例 `#/`；zh 6 页 |
| E194 | `attempt.action` | See this check attempt | 查看这次检查尝试 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 6 页（home ×6）；例 `#/`；zh 6 页 |
| E198 | `canHeading` | What you can do now | 现在可以做什么 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba`；中文原句在此前的代码里已有，随该提交移入词表 | en 6 页（home ×6）；例 `#/`；zh 6 页 |
| E199 | `cannotHeading` | What you cannot do yet | 现在还不能做什么 | 界面文字；en #33 `39ae8ba`；zh #33 `39ae8ba`；中文原句在此前的代码里已有，随该提交移入词表 | en 6 页（home ×6）；例 `#/`；zh 6 页 |

页面上下文（`E184` `title`）：
- en `#/`：‹ Items still to be dealt with in a model handover › For a BIM manager: what a pre-handover check found; after a recheck, which conclusions changed, whic
- zh `#/`：‹ 查看模型交接中仍需处理的事项 › 帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。

页面上下文（`E185` `lede`）：
- en `#/`：Items still to be dealt with in a model handover ‹ For a BIM manager: what a pre-handover check found; after a recheck, which conclusions changed, which items still need dealing with, which elements each one involves, what it rests on, and what to do next. › This is an example preview: you cannot import your own Revit model yet, and it gives no overall comp
- zh `#/`：查看模型交接中仍需处理的事项 ‹ 帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。 › 当前为示例预览：尚不能导入自己的 Revit 模型，也不提供整体合规或可施工结论。

### KEY_CHANGED（2 条）— 复检：引用换键

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E202 | `yes` | The citation changed key (the new key is the "corresponding evidence this record cites" above). A change of key is not itself a change. | 引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 33 页（fixture/recheck ×33）；例 `#/fixture/recheck-requirement-relaxed/recheck/7/2`；同页最多 ×6；zh 33 页 |
| E203 | `no` | The citation's key did not change. | 引用的键没有换。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E202` `yes`）：
- en `#/fixture/recheck-requirement-relaxed/recheck/7/2`：There is exactly one corresponding check result; compared aspect by aspect, at least one differs. ‹ The citation changed key (the new key is the "corresponding evidence this record cites" above). A change of key is not itself a change. › The check requirement was edited and the check result content changed too: the change in result may
- zh `#/fixture/recheck-requirement-relaxed/recheck/7/2`：对应的检查结果只有一条，逐项比较后至少有一个方面不同。 ‹ 引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。 › 检查要求被修改过，检查结果内容也变了：结果的变化可能来自要求的修改（例如要求放宽），不能据此说模型修好了。记录不说明要求是放宽还是收紧。

### MODE_LABELS（3 条）— 入口名称

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E223 | `fixture` | Simulated example | 模拟示例 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 24 页（fixture/result ×12; fixture/recheck ×10; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 0 页（未渲染到） |
| E224 | `real` | Check attempt on the bundled project | 随附项目的检查尝试 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 1 页（real/list ×1）；例 `#/real`；zh 1 页 |
| E225 | `workspace` | Real check in a workspace | 工作区里的真实检查 | 界面文字；en #33 `39ae8ba`；zh #26 `d6f89c1` | en 5 页（ws-compare:workspace/result ×1; ws-newly:workspace/result ×1; ws-notreeval:workspace/result ×1; ws-refusal:workspace/result ×1; ws-single:workspace/result ×1）；例 `ws-compare:#/workspace`；zh 5 页 |

页面上下文（`E223` `fixture`）：
- en `#/fixture/member-evidence`：First check result: items to deal with ‹ Simulated example: A first check: the model was handed over, and these items were found › This result: 13 in all; to deal with: 8

页面上下文（`E224` `real`）：
- en `#/real`：‹ Check attempt on the bundled project › The repository comes with a sample project; below is a check attempt on it. You cannot choose anothe
- zh `#/real`：‹ 随附项目的检查尝试 › 仓库随附一个样例项目，下面是对它的一次检查尝试。目前不能选择别的模型，也不能导入自己的模型。

### ONLY_REKEYED（1 条）— 复检：引用换键

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E226 | `(整表)` | Only the citation's key changed | 只是引用换了键 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 38 页（fixture/recheck ×34; fixture/result ×4）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×12；zh 30 页 |

页面上下文（`E226` ``）：
- en `#/fixture/recheck-requirement-relaxed`：Check-result citation (9 rows) ‹ Comparison basis unchanged × 7Only the citation's key changed × 7 › Comparison basis changed × 2check result content, check requirement changed; model version, checker
- zh `#/fixture/recheck-requirement-relaxed/recheck/7/2`：比较依据一致 ‹ 只是引用换了键 › 比较依据一致 只是引用换了键

### RECHECK（40 条）— 复检结果页

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E235 | `title` | Recheck result | 复检结果 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 134 页 |
| E236 | `notRecheck` | This record is not a recheck record, so there is no before-and-after to show. | 这份记录不是复检记录，没有复检前后的对比可以显示。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E237 | `unknownSuccessor` | This record follows a sealed record, but not as a recheck this page recognises: successor.kind =  | 这份记录承接了一条已封存的记录，但承接类型不是本页认识的复检：successor.kind =  | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E238 | `unknownSuccessorAfter` | . This page does not present it as a recheck. | 。本页不把它当作复检来呈现。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E239 | `resultTitle` | Recheck result: items to deal with | 复检结果：需要处理的事项 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E240 | `summary.one` | This result: {count} item | 本次结果：共 {count} 个事项 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 24 页（fixture/result ×12; fixture/recheck ×10; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E241 | `summary.other` | This result: {count} items | 本次结果：共 {count} 个事项 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 24 页（fixture/result ×12; fixture/recheck ×10; fixture/first ×2）；例 `#/fixture/member-evidence`；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E242 | `groupLine.one` | {count} item | {count} 个事项 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配）；同句（en）：FIRST.items.one |
| E243 | `groupLine.other` | {count} items | {count} 个事项 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配）；同句（en）：FIRST.items.other |
| E244 | `groupSummary` | : {summary} | ：{summary} | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E245 | `models` | Models: {headline}. | 模型：{headline}。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E246 | `moved.one` | {count} item's conclusion differs from before the recheck: | {count} 个事项的结论和复检前不同： | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 2 页（fixture/result ×1; fixture/recheck ×1）；例 `#/fixture/recheck-requirement-relaxed`；zh 12 页 |
| E247 | `moved.other` | {count} items' conclusions differ from before the recheck: | {count} 个事项的结论和复检前不同： | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 10 页（fixture/result ×5; fixture/recheck ×5）；例 `#/fixture/recheck-both-reissued`；zh 12 页 |
| E248 | `requirementChanged` | Of the old evidence cited before the recheck ({count} in all), the check requirement changed for {edited}. | 复检前引用的 {count} 条旧证据里，有 {edited} 条的检查要求变了。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 4 页（fixture/result ×2; fixture/recheck ×2）；例 `#/fixture/recheck-requirement-relaxed`；zh 4 页 |
| E249 | `groupHeading.one` | {label} ({count} item) | {label}（{count} 个事项） | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配）；同句（en）：FIRST.quietHeading.one |
| E250 | `groupHeading.other` | {label} ({count} items) | {label}（{count} 个事项） | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配）；同句（en）：FIRST.quietHeading.other |
| E251 | `cannotHeading` | What this preview cannot do | 本预览做不了的事 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |
| E252 | `cannotNote` | These actions are not implemented, so the page has no buttons for them. | 这些动作没有实现，所以页面上没有对应的按钮。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E253 | `limitsHeading` | When reading a recheck result | 读复检结果时 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 151 页（fixture/recheck ×141; fixture/result ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 151 页 |
| E254 | `sideModel` | {side} model | {side}模型 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 0 页（模板，固定文字太少，没有按页面匹配）；zh 0 页（模板，固定文字太少，没有按页面匹配） |
| E255 | `detailsSummary` | Before-and-after details: models, items, old evidence | 复检前后的比较明细：模型、事项、旧证据 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E256 | `modelsHeading` | Models | 模型 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 169 页（fixture/recheck ×141; fixture/result ×10; ws-compare:workspace/finding ×3; ws-newly:workspace/finding ×3; ws-single:workspace/finding ×3; ws-notreeval:workspace/finding ×2）；例 `#/fixture/recheck-requirement-relaxed`；zh 328 页 |
| E257 | `itemsHeading.one` | The item in the record before the recheck ({count}), and where it stands now | 复检前记录里的事项（{count} 个），现在的情况 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 2 页（fixture/result ×1; fixture/recheck ×1）；例 `#/fixture/recheck-comparison`；zh 20 页 |
| E258 | `itemsHeading.other` | The items in the record before the recheck ({count}), and where they stand now | 复检前记录里的事项（{count} 个），现在的情况 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 18 页（fixture/result ×9; fixture/recheck ×9）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E259 | `evidenceHeading.one` | The old evidence cited before the recheck ({count} row), compared with this record | 复检前引用的旧证据（{count} 条），和本次记录比较的结果 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 0 页（未在公开样例页面里渲染到）；zh 20 页 |
| E260 | `evidenceHeading.other` | The old evidence cited before the recheck ({count} rows), compared with this record | 复检前引用的旧证据（{count} 条），和本次记录比较的结果 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E261 | `kindsNote` | Check results and human determinations are two kinds of evidence, counted apart and never added together. | 检查结果和人工判定是两种证据，分开计数，不相加。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E262 | `traceSummary` | Tracing: record identity, model version fingerprints, record codes | 追溯信息：记录标识、模型版本指纹、记录原码对照 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E263 | `priorDigest` | Fingerprint of the record before the recheck (assessment digest) | 复检前记录的指纹（assessment digest） | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E264 | `currentDigest` | Fingerprint of this record (assessment digest) | 本记录的指纹（assessment digest） | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E265 | `noChange` | (an empty list in the record: no model changed) | （记录中为空列表：没有模型变化） | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 10 页（fixture/result ×5; fixture/recheck ×5）；例 `#/fixture/recheck-requirement-relaxed`；zh 10 页 |
| E266 | `versionColumns.side` | Side |  | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed` |
| E267 | `versionColumns.prior` | Record before the recheck | 复检前记录 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E268 | `versionColumns.current` | This record | 本记录 | 界面文字；en #34 `50d129b`；zh #34 `50d129b` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E269 | `versionNote` | A version is a content fingerprint, not a file name. Which side changed is taken from the record's changed_models; this page does not compare fingerprints. | 版本以内容指纹表示，不以文件名当版本。哪一侧变了取自记录的 changed_models，本页不比较指纹。 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E270 | `glossaryDispositions` | Where items stand now: record codes | 事项现在的情况：记录原码 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E271 | `glossaryConditions` | Conditions left before the recheck: state codes (there is no "the whole condition is met") | 复检前留下的条件：状态原码（没有“整句条件已满足”） | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E272 | `glossaryStates` | Old-evidence comparison: state codes | 旧证据比较：状态原码 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E273 | `glossaryReasons` | Old-evidence comparison: reason codes | 旧证据比较：原因原码 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |
| E274 | `glossaryAspects` | Aspects that changed: codes | 变化方面：原码 | 界面文字；en #34 `50d129b`；zh #34 `50d129b`；中文原句在此前的代码里已有，随该提交移入词表 | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |

页面上下文（`E235` `title`）：
- en `#/fixture/recheck-requirement-relaxed`：← Back to the examples ‹ Recheck result: items to deal with › Simulated example: The models did not change, but a handover conclusion did
- zh `#/fixture/recheck-requirement-relaxed/activity/2/sub/2/7/2`：← 记录上下文 ‹ 复检结果 › 活动：schedules-and-room-data-sheets

页面上下文（`E239` `resultTitle`）：
- en `#/fixture/recheck-requirement-relaxed`：← Back to the examples ‹ Recheck result: items to deal with › Simulated example: The models did not change, but a handover conclusion did
- zh `#/fixture/recheck-requirement-relaxed`：← 返回示例目录 ‹ 复检结果：需要处理的事项 › 模拟示例：模型未改，但交接判断发生变化

### REISSUE_CASES（16 条）— 复检：哪一侧模型重新发布

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E313 | `none.headline` | Neither model was re-issued (versions unchanged) | 两侧模型都没有重新发布（版本未变） | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 76 页（fixture/recheck ×71; fixture/result ×5）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×2；zh 76 页 |
| E314 | `none.detail` | This recheck uses the same pair of model versions as the original record, so the differences below do not come from model edits. | 本次复检和原记录用的是同一对模型版本，所以下面的差异不来自模型改动。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 10 页（fixture/result ×5; fixture/recheck ×5）；例 `#/fixture/recheck-requirement-relaxed`；zh 10 页 |
| E315 | `producing.headline` | The handing-over side's model was re-issued; the receiving side's model did not change | 交出方的模型重新发布了，接收方的模型没有变 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 45 页（fixture/recheck ×42; fixture/result ×3）；例 `#/fixture/recheck-member-gone`；同页最多 ×2；zh 45 页 |
| E316 | `producing.detail` | The handing-over side's ({from}) model {producing} is a new version; the receiving side's ({to}) model {consuming} is the original version. | 交出方（{from}）的模型 {producing} 是新版本；接收方（{to}）的模型 {consuming} 还是原版本。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 6 页（fixture/result ×3; fixture/recheck ×3）；例 `#/fixture/recheck-member-gone`；zh 6 页 |
| E317 | `producing.caveats[0]` | Re-issuing on the handing-over side may have changed what passes through what, or which elements are involved; it cannot be taken to mean the receiving side's work (for example the openings) is done. | 交出方重新发布可能改变了穿越关系或涉及的构件范围，不能据此说接收方的工作（例如开洞）已经做好。 | 界面文字；en #34 `50d129b`；zh #21 `f4a984f` | en 6 页（fixture/result ×3; fixture/recheck ×3）；例 `#/fixture/recheck-member-gone`；同页最多 ×2；zh 6 页 |
| E318 | `producing.caveats[1]` | A determination made against an old version cannot be attributed to the new one. | 针对旧版本作出的判定不能归到新版本。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 6 页（fixture/result ×3; fixture/recheck ×3）；例 `#/fixture/recheck-member-gone`；同页最多 ×2；zh 8 页 |
| E319 | `consuming.headline` | The receiving side's model was re-issued; the handing-over side's model did not change | 接收方的模型重新发布了，交出方的模型没有变 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 15 页（fixture/recheck ×14; fixture/result ×1）；例 `#/fixture/recheck-consuming-reissued`；同页最多 ×2；zh 15 页 |
| E320 | `consuming.detail` | The receiving side's ({to}) model {consuming} is a new version; the handing-over side's ({from}) model {producing} is the original version. | 接收方（{to}）的模型 {consuming} 是新版本；交出方（{from}）的模型 {producing} 还是原版本。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 2 页（fixture/result ×1; fixture/recheck ×1）；例 `#/fixture/recheck-consuming-reissued`；zh 2 页 |
| E321 | `consuming.caveats[0]` | Re-issuing on the receiving side may be the way to a fix, but it does not mean the fix has happened (for example that the opening is complete). | 接收方重新发布可能是修复的途径，但不代表修复已经发生（例如洞口已完成）。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 2 页（fixture/result ×1; fixture/recheck ×1）；例 `#/fixture/recheck-consuming-reissued`；同页最多 ×2；zh 2 页 |
| E322 | `consuming.caveats[1]` | Likewise, a determination made against an old version cannot be attributed to the new one. | 针对旧版本作出的判定同样不能归到新版本。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 2 页（fixture/result ×1; fixture/recheck ×1）；例 `#/fixture/recheck-consuming-reissued`；同页最多 ×2；zh 2 页 |
| E323 | `both.headline` | Both the handing-over and the receiving side's models were re-issued | 交出方和接收方的模型都重新发布了 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 15 页（fixture/recheck ×14; fixture/result ×1）；例 `#/fixture/recheck-both-reissued`；同页最多 ×2；zh 15 页 |
| E324 | `both.detail` | The handing-over side's ({from}) model {producing} and the receiving side's ({to}) model {consuming} are both new versions. | 交出方（{from}）的模型 {producing} 和接收方（{to}）的模型 {consuming} 都是新版本。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 2 页（fixture/result ×1; fixture/recheck ×1）；例 `#/fixture/recheck-both-reissued`；zh 2 页 |
| E325 | `both.caveats[0]` | Both sides changed at once: this page attributes no change in any evidence to either side. | 两侧同时变化：本页不把任何一条证据的变化归到某一侧。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 2 页（fixture/result ×1; fixture/recheck ×1）；例 `#/fixture/recheck-both-reissued`；同页最多 ×2；zh 2 页 |
| E326 | `both.caveats[1]` | A re-issue does not mean a fix has happened; a determination made against an old version cannot be attributed to the new one. | 重新发布不代表修复已经发生；针对旧版本作出的判定不能归到新版本。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 2 页（fixture/result ×1; fixture/recheck ×1）；例 `#/fixture/recheck-both-reissued`；同页最多 ×2；zh 2 页 |
| E327 | `unrecognised.headline` | The record's model version comparison cannot be recognised; shown as it came | 记录的模型版本比较无法识别，按原值显示 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |
| E328 | `unrecognised.detail` | The changed models the record gives do not match this record's handing-over and receiving sides, or the two fields contradict each other. This page does not guess which side. | 记录给出的变化模型与本记录的交出方、接收方对不上，或两个字段互相矛盾。本页不猜是哪一侧。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E313` `none.headline`）：
- en `#/fixture/recheck-requirement-relaxed`：6 items: the record gives no follow-up action ‹ Models: Neither model was re-issued (versions unchanged). › 1 item's conclusion differs from before the recheck:
- zh `#/fixture/recheck-requirement-relaxed`：6 个事项：记录没有给出后续处理动作 ‹ 模型：两侧模型都没有重新发布（版本未变）。 › 1 个事项的结论和复检前不同：

页面上下文（`E314` `none.detail`）：
- en `#/fixture/recheck-requirement-relaxed`：Neither model was re-issued (versions unchanged) ‹ This recheck uses the same pair of model versions as the original record, so the differences below do not come from model edits. › Side of the handover
- zh `#/fixture/recheck-requirement-relaxed`：两侧模型都没有重新发布（版本未变） ‹ 本次复检和原记录用的是同一对模型版本，所以下面的差异不来自模型改动。 › 交接的哪一侧

### REISSUE_NEUTRAL（1 条）— 复检：哪一侧模型重新发布

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E329 | `(整表)` | This page only says which side changed and what the record shows; it does not judge good or bad from the direction of a re-issue. | 本页只说明哪一侧变了、记录证明了什么，不根据重新发布的方向预判好坏。 | 界面文字；en #34 `50d129b`；zh #21 `eb05f61` | en 20 页（fixture/result ×10; fixture/recheck ×10）；例 `#/fixture/recheck-requirement-relaxed`；zh 20 页 |

页面上下文（`E329` ``）：
- en `#/fixture/recheck-requirement-relaxed`：architecture ‹ This page only says which side changed and what the record shows; it does not judge good or bad from the direction of a re-issue. › The items in the record before the recheck (13), and where they stand now
- zh `#/fixture/recheck-requirement-relaxed`：architecture ‹ 本页只说明哪一侧变了、记录证明了什么，不根据重新发布的方向预判好坏。 › 复检前记录里的事项（13 个），现在的情况

### REQUIREMENT_CHANGED_NOTE（1 条）— 复检：要求变化提示

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E330 | `(整表)` | The record also shows that, among the old evidence assessed together with this item, the check requirement changed for {count}; the record does not say whether it was relaxed or tightened. Read this conclusion with that in mind; row by row, see "The evidence before the recheck". | 记录同时显示：和这一项放在一起评估的旧证据里，有 {count} 条的检查要求变了；记录不说明是放宽还是收紧。读这个结论时要一并看，逐条见“复检前的证据”。 | 界面文字；en #34 `50d129b`；zh #21 `968422d` | en 13 页（fixture/recheck ×11; fixture/result ×2）；例 `#/fixture/recheck-requirement-relaxed`；同页最多 ×4；zh 13 页 |

页面上下文（`E330` ``）：
- en `#/fixture/recheck-requirement-relaxed`：Holds for this one item, this work and the listed model versions only; it does not mean the whole ha ‹ The record also shows that, among the old evidence assessed together with this item, the check requirement changed for 2; the record does not say whether it was relaxed or tightened. Read this conclusion with that in mind; row by row, see "The evidence before the recheck". › building element | Room data sheets and equipment schedules: before the recheck Blocked → now Ready
- zh `#/fixture/recheck-requirement-relaxed`：只对这一个事项、这项工作、所列的模型版本成立；不代表整次交接完成。 ‹ 记录同时显示：和这一项放在一起评估的旧证据里，有 2 条的检查要求变了；记录不说明是放宽还是收紧。读这个结论时要一并看，逐条见“复检前的证据”。 › building element ｜ 房间数据表与设备明细表：复检前 受阻 → 现在 可以开始 同组事项共用的依据，其中有模拟证据：模拟的检查结果 ×2 只对这一个事项、这项工作、所列的模型版本成立；

### RUN_LABELS（13 条）— 示例名称（含第二入口）

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E359 | `member-evidence` | A first check: the model was handed over, and these items were found | 一次首次检查：交了模型，发现这些事项 | 界面文字；en #33 `39ae8ba`；zh #21 `968422d` | en 3 页（fixture/list ×1; fixture/result ×1; fixture/first ×1）；例 `#/fixture`；zh 4 页 |
| E360 | `pair-verdicts` | The same check record: conclusions on pairs of elements (simulated example) | 同一份检查记录：成对构件的判断（模拟示例） | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 3 页（fixture/list ×1; fixture/result ×1; fixture/first ×1）；例 `#/fixture`；zh 4 页 |
| E361 | `recheck-both-reissued` | Recheck record 1 (simulated example) | 复检记录 1（模拟示例） | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 3 页（fixture/list ×1; fixture/result ×1; fixture/recheck ×1）；例 `#/fixture`；zh 4 页 |
| E362 | `recheck-comparison` | Recheck record 2 (simulated example) | 复检记录 2（模拟示例） | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 3 页（fixture/list ×1; fixture/result ×1; fixture/recheck ×1）；例 `#/fixture`；zh 4 页 |
| E363 | `recheck-consuming-reissued` | Recheck record 3 (simulated example) | 复检记录 3（模拟示例） | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 3 页（fixture/list ×1; fixture/result ×1; fixture/recheck ×1）；例 `#/fixture`；zh 4 页 |
| E364 | `recheck-key-change-only` | Recheck record 4 (simulated example) | 复检记录 4（模拟示例） | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 3 页（fixture/list ×1; fixture/result ×1; fixture/recheck ×1）；例 `#/fixture`；zh 4 页 |
| E365 | `recheck-member-gone` | Recheck record 5 (simulated example) | 复检记录 5（模拟示例） | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 3 页（fixture/list ×1; fixture/result ×1; fixture/recheck ×1）；例 `#/fixture`；zh 4 页 |
| E366 | `recheck-prior-without-basis` | Recheck record 6 (simulated example) | 复检记录 6（模拟示例） | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 3 页（fixture/list ×1; fixture/result ×1; fixture/recheck ×1）；例 `#/fixture`；zh 4 页 |
| E367 | `recheck-producing-reissued` | Recheck record 7 (simulated example) | 复检记录 7（模拟示例） | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 3 页（fixture/list ×1; fixture/result ×1; fixture/recheck ×1）；例 `#/fixture`；zh 4 页 |
| E368 | `recheck-producing-reissued-content-changed` | Recheck record 8 (simulated example) | 复检记录 8（模拟示例） | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 3 页（fixture/list ×1; fixture/result ×1; fixture/recheck ×1）；例 `#/fixture`；zh 4 页 |
| E369 | `recheck-requirement-relaxed` | The models did not change, but a handover conclusion did | 模型未改，但交接判断发生变化 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 18 页（fixture/item ×13; fixture/result ×2; fixture/list ×1; fixture/first ×1; fixture/recheck ×1）；例 `#/fixture`；zh 19 页 |
| E370 | `recheck-semantics-changed` | Recheck record 10 (simulated example) | 复检记录 10（模拟示例） | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 3 页（fixture/list ×1; fixture/result ×1; fixture/recheck ×1）；例 `#/fixture`；zh 4 页 |
| E371 | `real-refusal` | A check attempt on the bundled sample project | 对随附样例项目的一次检查尝试 | 界面文字；en #33 `39ae8ba`；zh #21 `f4a984f` | en 1 页（real/list ×1）；例 `#/real`；zh 2 页 |

页面上下文（`E359` `member-evidence`）：
- en `#/fixture`：Step 1 ‹ A first check: the model was handed over, and these items were found › The handing-over side has handed over its model: which items need dealing with, who deals with each,
- zh `#/fixture`：第一步 ‹ 一次首次检查：交了模型，发现这些事项 › 交出方交了模型：有哪些事项要处理，各由谁处理，每一项要做什么？

页面上下文（`E360` `pair-verdicts`）：
- en `#/fixture`：These examples have no description yet, and the recheck records have only a number for now; this rou ‹ The same check record: conclusions on pairs of elements (simulated example) › Recheck record 1 (simulated example)
- zh `#/fixture`：这些示例还没有写说明，复检记录暂时只有编号；本轮没有改到它们。 ‹ 同一份检查记录：成对构件的判断（模拟示例） › 复检记录 1（模拟示例）

### WORKSPACE_HOME（4 条）— 首页第三入口（真实检查）

| ID | 键 | English | 中文 | 来源 · 引入 | 页面 · 复用 |
|---|---|---|---|---|---|
| E526 | `title` | See a real check | 查看一次真实检查 | 界面文字；en #33 `39ae8ba`；zh #26 `d6f89c1` | en 5 页（home ×5）；例 `ws-compare:#/`；zh 5 页 |
| E527 | `body` | The server was started with a workspace holding a check that has already run: each element's result under each requirement. If an earlier run was named as well, the two can be compared. There are check results only here, no handover judgement. This page only shows the check that has already run; you cannot choose or change a model on it. | 启动服务器时指定了一个工作区，里面是一次已经跑完的检查：每个构件在每条要求下的结果。若同时指定了前一次运行，还可以看两次的前后对比。这里只有检查结果，没有交接判断。页面只查看这次已经跑完的检查，不能在页面上选择或更换模型。 | 界面文字；en #33 `39ae8ba`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 5 页（home ×5）；例 `ws-compare:#/`；zh 5 页 |
| E528 | `action` | See this check | 查看这次检查 | 界面文字；en #33 `39ae8ba`；zh #26 `d6f89c1` | en 6 页（home ×6）；例 `#/`；同页最多 ×2；zh 5 页 |
| E529 | `unknown` | Could not confirm whether the server was started with a workspace (that does not mean there is none). The error: | 未能确认服务器是否指定了工作区（不等于没有工作区）。错误原文： | 界面文字；en #33 `39ae8ba`；zh #31 `82aa943`；#27／#31 终稿：#31 82aa943 | en 0 页（未在公开样例页面里渲染到）；zh 0 页（未渲染到） |

页面上下文（`E526` `title`）：
- en `ws-compare:#/`：What you can do now ‹ See a real check › The server was started with a workspace holding a check that has already run: each element's result
- zh `ws-compare:#/`：现在可以做什么 ‹ 查看一次真实检查 › 启动服务器时指定了一个工作区，里面是一次已经跑完的检查：每个构件在每条要求下的结果。若同时指定了前一次运行，还可以看两次的前后对比。这里只有检查结果，没有交接判断。页面只查看这次已经跑完的检查，不能在

页面上下文（`E527` `body`）：
- en `ws-compare:#/`：See a real check ‹ The server was started with a workspace holding a check that has already run: each element's result under each requirement. If an earlier run was named as well, the two can be compared. There are check results only here, no handover judgement. This page only shows the check that has already run; you cannot choose or change a model on it. › See this check
- zh `ws-compare:#/`：查看一次真实检查 ‹ 启动服务器时指定了一个工作区，里面是一次已经跑完的检查：每个构件在每条要求下的结果。若同时指定了前一次运行，还可以看两次的前后对比。这里只有检查结果，没有交接判断。页面只查看这次已经跑完的检查，不能在页面上选择或更换模型。 › 查看这次检查

