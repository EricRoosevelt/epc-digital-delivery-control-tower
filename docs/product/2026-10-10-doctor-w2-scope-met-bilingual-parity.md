# Doctor W2：#58 复核后的修正，中英义务对照

日期：2026-10-10。负责：Product/UI Engineer。基线 `1c05dd2`（#58 已合并）；分支 `fix/doctor-w2-scope-met`。
依据：[BIM 对 #58 的复核](2026-10-10-bim-review-58-verdicts.csv)，技术总监的修正包。只列这次改动的句子；#58 的其余句子见 [W2 对照](2026-10-10-doctor-w2-prior-condition-bilingual-parity.md)，BIM 已通过。
状态：删句按 BIM 的结论执行；4 条改句采用 BIM 给的措辞，交 BIM 确认。

“同一义务”的判断标准：两种语言要求读者做的事、承诺或否认的事、限定的范围相同；措辞、语序、标点不同不算。

## 一、删去：`RECHECK_ITEM.scopeMet`（含义错误）

| 改前（中） | 改前（英） | 现在 |
| --- | --- | --- |
| 本项的要求已满足；但原记录的这个结束条件覆盖评估范围内的全部构件，不只这一项，所以不能据此宣布原全范围结束条件满足。 | This item's requirements are met; but the original record's exit condition covers every element in the assessed scope, not only this item, so this cannot be taken to mean the original whole-scope exit condition is met. | 删去。释义声明全范围时，一律显示 `scopeWhole`（BIM 已通过）：“原记录的这个结束条件覆盖评估范围内的全部构件，不只这一项：即使本项的要求满足了，也不能据此宣布原全范围结束条件满足。” |

- BIM 的理由：从 READY 推不出“本项的要求已满足”。例如 `#/fixture/recheck-requirement-relaxed/recheck/7/2`：两侧模型都没有重新发布，同组 6 条旧证据里有 2 条的检查要求改过，所以本项现在 READY，并没有证明它满足了原条件里属于它的那部分。
- `scopeNote` 不再看本项现在的判定。`scopeWhole` 只作假设（“即使……满足了”），在任何情况下都成立。

## 二、改句：释义 6–9 补“项目接受的”

理由（BIM）：Pack 0.1.0 的 `next_action` 指明，这个方法是本项目接受的方法，原条件里的定冠词 The 指的就是它；`ACTIONS` 的中文也写“按项目接受的方法”。写成泛称的“方法”，读者可能理解为任何方法都行。

| 释义 | 改前（中） | 改后（中） | 改前（英） | 改后（英） | 义务 |
| --- | --- | --- | --- | --- | --- |
| 6 `cross-model-alignment-not-confirmed` | 针对所列的具体模型版本，按对齐确认方法做一次确认，结果为模型已对齐 | 针对所列的具体模型版本，按**项目接受的**对齐确认方法做一次确认，结果为模型已对齐 | For the specific model versions named, the alignment confirmation is performed by its method and reports the models aligned | For the specific model versions named, the alignment confirmation is performed by **the method the project accepts** and reports the models aligned | 同一义务 |
| 7 `cross-model-misalignment` | 针对重新发布的模型版本，按对齐确认方法重新确认，结果为模型已对齐（已确认） | 针对重新发布的模型版本，按**项目接受的**对齐确认方法重新确认，结果为模型已对齐（已确认） | For the reissued model versions, the alignment confirmation is re-run by its method and reports the models aligned (confirmed) | For the reissued model versions, the alignment confirmation is re-run by **the method the project accepts** and reports the models aligned (confirmed) | 同一义务 |
| 8 `opening-not-verifiably-linked` | 针对这一对，重新运行开洞关联核查，结果为洞口已关联到穿过它的构件 | 针对这一对，重新运行**项目接受的**开洞关联核查，结果为洞口已关联到穿过它的构件 | For this pair, the opening cross-reference check is re-run and reports the opening cross-referenced to the element passing through it | For this pair, the opening cross-reference check **the project accepts** is re-run and reports the opening cross-referenced to the element passing through it | 同一义务 |
| 9 `opening-status-not-determined` | 针对所列模型版本，运行开洞关联核查，并给出明确结果（已关联、已建未关联或未建） | 针对所列模型版本，运行**项目接受的**开洞关联核查，并给出明确结果（已关联、已建未关联或未建） | For the model versions named, the opening cross-reference check is run and gives a definite result (cross-referenced, modelled but not cross-referenced, or not modelled) | For the model versions named, the opening cross-reference check **the project accepts** is run and gives a definite result (cross-referenced, modelled but not cross-referenced, or not modelled) | 同一义务 |

加粗只为标出改动，页面上没有加粗。其余三项（全称范围、模型版本、通过条件）不变。

## 三、不改

- 空间归属（`mep-element-not-spatially-assigned`）维持原样，照录原文。BIM 给的释义是可选改进，冻结后再做。
- 释义 1–5、`priorCondition`、`priorConditionOriginal`、`priorConditionMissing`、`conditionBoundary`、`scopeWhole` 都已通过，字面不变。
