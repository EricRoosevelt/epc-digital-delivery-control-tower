# Doctor W2（E289）复检前留下的结束条件：中英义务对照

日期：2026-10-10。负责：Product/UI Engineer。基线 `66e7a57`；分支 `fix/doctor-w2-prior-condition`。
依据：[PM 对汇报（七）与 W2 的裁定](2026-10-09-pm-response-to-td-7-w2.md)，选 (a)；技术总监同意的方案与三点补充（释义只对 Pack 0.1.0 成立；全范围由释义条目自己声明；逐条列四项位置）。
状态：BIM 已复核（`docs/product/2026-10-10-bim-review-58-verdicts.csv`）。`scopeMet` 为含义错误，已删去；释义 6–9 按建议补“项目接受的”；见 [#58 复核后的修正](2026-10-10-doctor-w2-scope-met-bilingual-parity.md)。下文的表已按修正后的句子更新，删去的句子在修正对照里。

“同一义务”的判断标准：两种语言要求读者做的事、承诺或否认的事、限定的范围相同；措辞、语序、标点不同不算。

## 结论

- 复检单项页第四节不再用 `ACTIONS` 的复检句代替历史条件，改为读记录自己的 `prior_recheck_condition`：
  - 与 Pack 0.1.0 路由原文逐字相同，并且记录的 Pack id、版本就是 `interdisciplinary-coordination-readiness` 0.1.0：显示释义；
  - 其他措辞、Pack 或版本：显示标注的原文，不加范围说明；
  - 记录没有携带时如实说缺失。
- 同一区域依次是：原记录的条件、机读状态（照记录）、状态边界句、范围说明（只在释义声明全范围时）、原有说明句、追溯折叠（原文和记录原码，不变）。
- E014 的当前建议不变，仍在“二、下一步”。
- 没有改 Pack、评估器、机读状态、规则或发布产物。
- 共 9 条释义、5 句新句、1 处改句，中英都是同一义务。
- 空间归属一条（`mep-element-not-spatially-assigned`）没有写释义，显示标注的原文。见第三节第 1 条。

## 一、替换了历史条件的显示位置（全部列举）

逐个查了 `doctor/static` 里读 `ACTIONS`、`recheck`、`recheck_condition`、`prior_recheck_condition`、`prior_resolution_kind` 的地方：

| 位置 | 显示什么 | 取值来源 | 是否替换了历史条件 | 本包处理 |
| --- | --- | --- | --- | --- |
| `screens.js` `recheckItem` 第四节“复检前留下的结束条件” | 原记录在复检前留下的结束条件 | 改前：`ACTIONS[prior_resolution_kind].recheck`（界面建议） | **是，唯一一处** | 改为记录自己的 `prior_recheck_condition`，见上 |
| `screens.js` `actionBlock`（首次单项、复检单项的“二、下一步”） | 完成后拿什么复检（E014） | `ACTIONS[当前 resolution_kind].recheck` | 否：说的是本项现在的建议 | 不变 |
| `screens.js` 首次结果卡片、`actionRow` | 要做什么 | `ACTIONS[当前 resolution_kind].action` | 否：只用 `action`，不用复检句 | 不变 |
| `screens.js` 成员页（只有中文） | 记录路由的 `recheck_condition` | 记录原文 | 否：显示的就是原文 | 不变 |
| `screens.js` `actionBlock` 来源折叠、第四节追溯折叠 | `recheck_condition`／`prior_recheck_condition` 原文 | 记录原文 | 否 | 不变 |
| `workspace-screens.js` PV-001 规则说明 | 工作区检查的复检说明 | `RULE_NOTES` | 否：不是复检记录的条件 | 不变 |

## 二、释义：Pack 原文 → 中文释义 → 英文释义

键是 Pack 0.1.0 `resolution_routes[].recheck_condition` 的原文，逐字匹配。“全范围”一栏是条目自己声明的 `scope: "whole-scope"`，不是从原文里猜的关键词；测试核对这一声明与原文是否写了 “every element in the assessed scope” 一致。

### 1. `missing-project-asset-identity`（全范围）

- 原文：Every requirement_key bound to asset-identity evaluates PASS for every element in the assessed scope, with no element left uncovered, on the reissued model.
- 中文：在重新发布的模型上，评估范围内的每一个构件，在资产标识所绑定的每一条要求下都评估为通过，没有一个构件漏评
- 英文：On the reissued model, every element in the assessed scope passes every requirement bound to asset identity, with no element left unevaluated

| 四项 | 原文 | 中文 | 英文 |
| --- | --- | --- | --- |
| 全称范围 | for every element in the assessed scope; with no element left uncovered | 评估范围内的每一个构件；没有一个构件漏评 | every element in the assessed scope; with no element left unevaluated |
| 模型版本 | on the reissued model | 在重新发布的模型上 | On the reissued model |
| 要求集合 | every requirement_key bound to asset-identity | 资产标识所绑定的每一条要求 | every requirement bound to asset identity |
| 通过条件 | evaluates PASS | 都评估为通过 | passes |

### 2. `asset-identity-not-evaluated`（全范围）

- 原文：Every element in the assessed scope is covered by an evaluation under the bound requirement_key(s) -- no element is left with no finding at all.
- 中文：评估范围内的每一个构件，在所绑定的要求下都被评估到：没有一个构件完全没有检查结果
- 英文：Every element in the assessed scope is evaluated under the bound requirements: no element is left with no check result at all

| 四项 | 原文 | 中文 | 英文 |
| --- | --- | --- | --- |
| 全称范围 | Every element in the assessed scope; no element is left … | 评估范围内的每一个构件；没有一个构件…… | Every element in the assessed scope; no element is left … |
| 模型版本 | 原文没有写 | 不补写 | 不补写 |
| 要求集合 | the bound requirement_key(s) | 所绑定的要求 | the bound requirements |
| 通过条件 | covered by an evaluation（覆盖，不是 PASS） | 都被评估到；没有一个构件完全没有检查结果 | is evaluated; no element is left with no check result at all |

### 3. `in-model-position-not-evaluated`（全范围）

- 原文：Every element in the assessed scope is covered by a finding under the bound requirement_key(s).
- 中文：评估范围内的每一个构件，在所绑定的要求下都有检查结果
- 英文：Every element in the assessed scope has a check result under the bound requirements

| 四项 | 原文 | 中文 | 英文 |
| --- | --- | --- | --- |
| 全称范围 | Every element in the assessed scope | 评估范围内的每一个构件 | Every element in the assessed scope |
| 模型版本 | 原文没有写 | 不补写 | 不补写 |
| 要求集合 | the bound requirement_key(s) | 所绑定的要求 | the bound requirements |
| 通过条件 | covered by a finding（覆盖，不是 PASS） | 都有检查结果 | has a check result |

### 4. `penetration-not-determined`

- 原文：A recorded coordination-review determination exists for the named model versions, naming either no penetration or the architectural elements penetrated.
- 中文：针对所列模型版本，有一份已记录的协调评审判定，写明不穿过，或写明穿过了哪些建筑构件
- 英文：For the model versions named, a recorded coordination-review determination exists, stating either that there is no penetration or which architectural elements are penetrated

| 四项 | 原文 | 中文 | 英文 |
| --- | --- | --- | --- |
| 全称范围 | 原文没有写构件范围（对象是这次判定） | 不补写 | 不补写 |
| 模型版本 | for the named model versions | 针对所列模型版本 | For the model versions named |
| 要求集合 | a recorded coordination-review determination（不是要求键） | 一份已记录的协调评审判定 | a recorded coordination-review determination |
| 通过条件 | exists, naming either no penetration or the architectural elements penetrated | 有……，写明不穿过，或写明穿过了哪些建筑构件 | exists, stating either that there is no penetration or which architectural elements are penetrated |

“不穿过”出自原文本身，不是界面补的（对照 E282：那里是界面在原文之外补了“不穿过”）。

### 5. `missing-corresponding-opening`

- 原文：The opening-status evaluation is re-run and reports the opening modelled and cross-referenced (outcome = cross-referenced) for this pair, for the named model versions.
- 中文：针对所列模型版本，重新运行开洞情况评估，这一对的结果为洞口已建且已关联
- 英文：For the model versions named, the opening-status evaluation is re-run and reports, for this pair, the opening modelled and cross-referenced

| 四项 | 原文 | 中文 | 英文 |
| --- | --- | --- | --- |
| 全称范围 | for this pair（与本项同一范围，所以不加范围说明） | 这一对 | for this pair |
| 模型版本 | for the named model versions | 针对所列模型版本 | For the model versions named |
| 要求集合 | the opening-status evaluation, re-run | 重新运行开洞情况评估 | the opening-status evaluation is re-run |
| 通过条件 | reports the opening modelled and cross-referenced (outcome = cross-referenced) | 结果为洞口已建且已关联 | reports … the opening modelled and cross-referenced |

结果码 `cross-referenced` 留在折叠里的原文中，顶层不铺开。

### 6. `cross-model-alignment-not-confirmed`

- 原文：The alignment-confirmation method is performed and reports the models aligned, against the specific model versions named.
- 中文：针对所列的具体模型版本，按项目接受的对齐确认方法做一次确认，结果为模型已对齐
- 英文：For the specific model versions named, the alignment confirmation is performed by the method the project accepts and reports the models aligned

| 四项 | 原文 | 中文 | 英文 |
| --- | --- | --- | --- |
| 全称范围 | the models（两侧模型，与本项的对齐建议同一范围） | 模型 | the models |
| 模型版本 | against the specific model versions named | 针对所列的具体模型版本 | For the specific model versions named |
| 要求集合 | the alignment-confirmation method（Pack 的 next_action：项目接受的方法） | 项目接受的对齐确认方法 | the method the project accepts |
| 通过条件 | is performed and reports the models aligned | 做一次确认，结果为模型已对齐 | is performed … and reports the models aligned |

### 7. `cross-model-misalignment`

- 原文：The alignment-confirmation method is re-run against the reissued model versions and reports the models aligned (outcome = confirmed).
- 中文：针对重新发布的模型版本，按项目接受的对齐确认方法重新确认，结果为模型已对齐（已确认）
- 英文：For the reissued model versions, the alignment confirmation is re-run by the method the project accepts and reports the models aligned (confirmed)

| 四项 | 原文 | 中文 | 英文 |
| --- | --- | --- | --- |
| 全称范围 | the models | 模型 | the models |
| 模型版本 | against the reissued model versions | 针对重新发布的模型版本 | For the reissued model versions |
| 要求集合 | the alignment-confirmation method, re-run（项目接受的方法） | 按项目接受的对齐确认方法重新确认 | is re-run by the method the project accepts |
| 通过条件 | reports the models aligned (outcome = confirmed) | 结果为模型已对齐（已确认） | reports the models aligned (confirmed) |

### 8. `opening-not-verifiably-linked`

- 原文：The opening-cross-reference-check method is re-run and reports the opening cross-referenced to the penetrating element, for the pair.
- 中文：针对这一对，重新运行项目接受的开洞关联核查，结果为洞口已关联到穿过它的构件
- 英文：For this pair, the opening cross-reference check the project accepts is re-run and reports the opening cross-referenced to the element passing through it

| 四项 | 原文 | 中文 | 英文 |
| --- | --- | --- | --- |
| 全称范围 | for the pair（与本项同一范围） | 针对这一对 | For this pair |
| 模型版本 | 原文没有写 | 不补写 | 不补写 |
| 要求集合 | the opening-cross-reference-check method, re-run（项目接受的方法） | 重新运行项目接受的开洞关联核查 | the opening cross-reference check the project accepts is re-run |
| 通过条件 | reports the opening cross-referenced to the penetrating element | 结果为洞口已关联到穿过它的构件 | reports the opening cross-referenced to the element passing through it |

### 9. `opening-status-not-determined`

- 原文：The opening-cross-reference-check method is performed and reports a definite result (cross-referenced, modelled-not-cross-referenced, or not-modelled) for the named model versions.
- 中文：针对所列模型版本，运行项目接受的开洞关联核查，并给出明确结果（已关联、已建未关联或未建）
- 英文：For the model versions named, the opening cross-reference check the project accepts is run and gives a definite result (cross-referenced, modelled but not cross-referenced, or not modelled)

| 四项 | 原文 | 中文 | 英文 |
| --- | --- | --- | --- |
| 全称范围 | 原文没有写（对象是这次核查） | 不补写 | 不补写 |
| 模型版本 | for the named model versions | 针对所列模型版本 | For the model versions named |
| 要求集合 | the opening-cross-reference-check method（项目接受的方法） | 项目接受的开洞关联核查 | the opening cross-reference check the project accepts |
| 通过条件 | reports a definite result (three named outcomes) | 给出明确结果（已关联、已建未关联或未建） | gives a definite result (three outcomes) |

### 10. `mep-element-not-spatially-assigned`：没有释义，显示标注的原文

- 原文：The R-004-bound requirement_key(s) evaluate PASS for the element on the reissued model.
- 原文用规则编号（R-004）指明要求集合。界面静态文件不得出现规则编号，这是已有测试守住的约束，本包不改它。所以这一条没有释义，显示“原文照录，本界面没有可靠的释义”加原文。
- 测试固定了这一点（`spatial` 用例）。如果 BIM 认为需要释义，要先决定能否在界面里写规则编号，或者用“空间归属规则”代替编号是否忠实。

## 三、新句与改句

| 键 | 改前（中） | 改前（英） | 改后（中） | 改后（英） | 何时显示 | 义务 |
| --- | --- | --- | --- | --- | --- | --- |
| `RECHECK_ITEM.priorCondition`（改） | 复检前留下的结束条件：{text}。（{text} 为 `ACTIONS` 复检句） | The exit condition left before the recheck: {text} | 原记录在复检前留下的结束条件（释义）：{text}。 | The exit condition the original record left before the recheck (paraphrased): {text}. | 原文与 Pack 0.1.0 逐字相同 | 同一义务。标明是原记录的条件，且是释义 |
| `RECHECK_ITEM.priorConditionOriginal`（新增） | （无） | （无） | 原记录在复检前留下的结束条件（原文照录，本界面没有可靠的释义）： | The exit condition the original record left before the recheck (as written; this interface has no reliable paraphrase of it): | 其他措辞、Pack 或版本；后接原文引用块 | 同一义务。英文界面里原文本身就是英文，标签仍说明这是照录原文 |
| `RECHECK_ITEM.priorConditionMissing`（新增） | （无） | （无） | 原记录没有携带复检前留下的结束条件；本页不拿本项的建议补写它。 | The original record does not carry the exit condition left before the recheck; this page does not fill it in from this item's suggestion. | 没有携带条件，且状态不是“原记录没有复检条件” | 同一义务 |
| `RECHECK_ITEM.conditionBoundary`（新增） | （无） | （无） | 上面的状态说的是原记录的这个结束条件：不是本项构件自己的通过状态，也不是本项的结论。 | The status above is about the original record's exit condition: it is not the pass status of this item's own element(s), and not this item's conclusion. | 每个复检单项，紧跟机读状态 | 同一义务。英文的 element(s) 覆盖一对构件的事项；中文“本项构件”同样不限一个 |
| `RECHECK_ITEM.scopeWhole`（新增） | （无） | （无） | 原记录的这个结束条件覆盖评估范围内的全部构件，不只这一项：即使本项的要求满足了，也不能据此宣布原全范围结束条件满足。 | The original record's exit condition covers every element in the assessed scope, not only this item: even once this item's requirements are met, that cannot be taken to mean the original whole-scope exit condition is met. | 释义声明全范围时一律显示，不看本项现在的判定 | 同一义务。不声称本项已满足 |

原来还有一句 `scopeMet`（“本项的要求已满足；但……”），在本项现在全部 READY 时代替 `scopeWhole`。BIM 复核为含义错误：从 READY 推不出本项满足了原条件里属于它的部分，因为模型可能没有重新发布，或者引用的检查要求已经改过。已删去，见修正对照。

## 四、反例验收（测试，构造数据）

`tests/test_doctor_recheck_screens.py` 的 `PriorConditionTests`。用适配器的 `recheck-comparison` 记录复制后改一个结果，不碰规则、Pack 和发布产物：

| 用例 | 构造 | 页面模型给出 |
| --- | --- | --- |
| `passes`（反例） | 上次问题类型 `missing-project-asset-identity`，原文为 Pack 原文；本项现在 READY；状态 `no-machine-checkable-part` | 释义（含“评估范围内的每一个构件”“没有一个构件漏评”，不含 E014 的建议句）；`scopeWhole`，含“不能据此宣布原全范围结束条件满足”，不出现“本项的要求已满足”；状态照记录，说“记录对它不下结论” |
| `partial` | 同上，状态 `named-outcome-observed` | 状态句保留“这不是‘整句条件已满足’”；范围说明照常 |
| `unknown` | 同上，状态为界面不认识的码 | 标为不认识，范围说明照常 |
| `still-blocked` | 同上，本项现在 BLOCKED | `scopeWhole`，不说本项已满足 |
| `pair` | `missing-corresponding-opening`，Pack 原文 | 释义，没有范围说明（同一范围） |
| `other-version` | Pack 版本 0.2.0 | 标注的原文，没有范围说明 |
| `other-wording` | 原文改了一个词 | 标注的原文，没有范围说明 |
| `spatial` | 空间归属的 Pack 原文 | 标注的原文 |
| `missing` | 没有携带条件，状态 `not-comparable` | 说缺失 |
| `none` | 空条件，状态 `no-recheck-condition`，上次 READY | 不加句子，由状态句说 |

**撤掉修正，测试必须是红的。** 已实测：把 `screens.js`、`recheck-model.js` 换回基线（`ACTIONS` 句填进第四节），8 个测试方法中 7 个失败（5 个直接失败；“其他版本或措辞”“状态边界”两个的每个子测试都失败），其中包括检查第四节不再调用 `actionSentences(carried(outcome, "prior_resolution_kind")…)` 的源码测试。唯一仍通过的是只核对词表的“释义保留四项”。（pytest 的汇总行写作“10 failed, 3 passed”，那是把子测试也算进去了。）

## 五、请 BIM 复核的点

1. 9 条释义各自是否忠实，第二节逐条列了四项各在哪里。
2. 第 4、6、7、8、9 条没有加范围说明，理由是原条件与本项建议同一范围（一对构件，或两侧模型整体）。请确认。
3. 第 10 条（空间归属）没有释义，是否接受只显示标注的原文。
