# BIM Doctor：已批准 UI 的正式实现候选

2026-10-13，新加坡。文件名沿用 10/12 实施任务。**实际产品代码与可审 PR 已交付；独立 TD、UX、BIM、PM 验收尚未完成，不是最终冻结。**

## 候选、隔离与审查入口

- [PR #64](https://github.com/EricRoosevelt/epc-digital-delivery-control-tower/pull/64)，已 attach 到实现会话，状态 OPEN；没有自批、自合并或发布。
- 实际基线：`c62df8cc0c1d930e95827186709df3ef4a509e03`。直接核对 #63 MERGED、远端 main 指向该 merge、手机隐藏行修复仍在；开工与提交时 main 均未前移。
- 产品代码及测试提交：`d79b57842e518b84f9b99180ed00fc9f9789a435`。本报告后续提交只补交接记录；完整候选 head 以 PR 和实现会话交接为准。
- 新托管 worktree `doctor-approved-ui`、分支 `feat/doctor-approved-ui`。没有在共享旧 checkout 切分支、重置、清理、暂存用户文件或覆盖其他会话的报告/预览。原 #63 worktree 与证据保留。
- 当前代码量在单包范围内：实现提交 23 文件、1221 insertions / 95 deletions；包括设计/行为记录、计划、词表与回归，生产数据/规则/Pack/包代码无差异。

实施沿用已批准的 PM 决定、v2 间距及 UX/BIM/技术报告，按 [计划和 owner 映射](2026-10-12-ui-implementation-plan.md) 执行，没有重新发起风格或开工审批。原 10/12 准备阶段的 #63 自动审批阻塞已由用户确认后合并解除，本轮没有沿用旧阻塞。

## 实际实现

共享壳包含 BIM Doctor 身份、内部预览标识、两条真实主路径和语言选择。首页、示例目录、首检、单项、同项复检、本地选择/声明/范围/结果/详情、拒绝/加载/错误继承同一 CSS/控件。入口仍进入实际目录或本地输入，没有把预览快照、固定两条 FAIL 或直接跳过上传的按钮装进产品。

首检沿用真实 `first-check-model` 投影：13 个事项、8 个有动作、6 个不同构件；按处理团队显示紧凑事项表，工作和结论、逐项依据/缺席及默认角色/未派发限制保留。每项仍有独立 route 和深链接；同项复检闭环及 #58/#60 原条件反例保留。没有新增示例搜索或全量 inline detail。

本地桌面名称优先、状态横向、完整 class/model/storey/Tag 可读；列表与自然增长详情并排。375 使用既有 finding route 的独立单列详情及可见返回；文档是垂直滚动 owner，详情没有旧的 sticky/max-height 内滚动。通用 workspace/compare 保留完整列，局部布局变体不借首模型或 PV-001 假设推导其他结果。

同一检查内 query/status/选中对象留在内存；切语言时用一次性 tab handoff，下一次加载在渲染前消费并删除，普通输入不写 storage，query 不进入 URL/localStorage。重复点当前语言不会留下 handoff；其他检查重置 view。返回聚焦可见选中行，筛选外选中项返回时聚焦搜索。未知 finding 的手机错误也聚焦可见错误，不去隐藏列表。

定位、结果跳转及 skip 只移动可见焦点/文档滚动，不改 router hash。换对象时新标题进入视口；普通新页从顶部呈现壳与来源，返回/对象目标单独处理。等待新模式/记录时清空旧来源栏，避免本地加载仍被旧“模拟示例”标识；页面标题使用实际当前对象/页名。

详情模式及输入文件从当前 finding 对应 model 读取，提供实际 run/models 的内容指纹与记录入口。当前上传 API 没有“这是随附公开样例”的可信字段，因此 UI 显示实际本地模式/输入文件名，不凭文件名猜公开样例，也不把所有用户文件固定标为公开样例。模型追溯不使用软件 SHA。

FAIL/PASS/模型级 N/A、多文件、缺字段/未知要求、空观察值、加载/拒绝/程序错误原分支保留。PASS 只说该规则证明的内容且不补造观察值；N/A 不是通过；未知要求没有借用 PV-001 修改建议。

## 文字、移动与折叠增量：供 BIM 定向复核

原 `vocabulary.js`、`vocabulary-en.js`、`local-words.js` 和领域模型/规则没有修改。布局词单独注册为 `WORKSPACE_UI`，逐词追加到已有 [中英词表](2026-10-03-doctor-english-vocabulary.md)，没有覆盖原记录或把预览 PASS 写成生产候选 PASS。

| 增量 | 实际落位与边界 |
|---|---|
| 模拟示例 / Simulated examples；本地 IFC 检查 / Local IFC check；主要路径 / Main paths；内部预览 / Internal preview | 全局真实导航、产品身份与 ARIA；不表示未运行检查的纯设计预览 |
| 定位到结果列表 / Go to the results list | 首检摘要旁焦点跳转按钮；不隐藏必要说明或更改结果 |
| 返回结果列表 / Back to results；清空搜索 / Clear search | 本地实际 route 返回及查询清空；不关闭、修复、派发或修改模型 |
| 输入模型 / Input model；模型版本与记录 / Model versions and record | 当前 finding 的实际文件字段、实际 run/models 追溯；没有软件 SHA 代替模型版本 |
| 事项数不是缺陷数的中英开放句 | 来自已审预览原句，保持在 13/8 摘要旁；完整原粒度与 6 构件说明进入现有“如何阅读”折叠，没有删原定义 |
| 当前选中项在筛选外、详情仍可读的中英句 | 来自已审预览状态句，桌面真实状态按当前选择/过滤计算；不是模型 N/A、PASS 或结果改变 |
| 名称 / Name；依据 / Basis | 表格列名；领域实体、工作、结论、来源仍取实际投影 |
| 原团队问题/工作聚合小表进入额外 overview 折叠 | 个体事项表仍开放显示对象、问题、工作/结论、依据及必要限制；聚合原数据未删除，未代替个体结果 |
| 五项无后续动作进入 disclosure | 原五项的工作、READY、来源及 scoped/对齐限制仍在；返回该类事项会展开，确保焦点可见。不是整个交接 READY |
| 首检版本上下文进入现有追溯 | 从原 request.model_version_context 原样显示 producing/consuming/handover 等记录字段，保留原 record 链接；未制造模型版本 |
| 已审本地 PV-001 FAIL 的 checker-read 后移/折叠 | 只在已有 ruleNotes 且 ProductValidation 的 local FAIL action 中；修改前核对、改成什么、源映射未知、类型全部实例影响、未定值/操作者及复检指令仍开放 |
| 已审本地 PV-001 FAIL 的原要求/观察折叠 | expected/reason/actual-empty 原分支未改；PASS、N/A、未知要求仍保持原开放解释分支 |
| 手机详情隐藏重复列表标题/练习介绍/总览 | 详情自身保留实际本地模式、输入文件、对象、状态和对应来源/PASS/N/A限制；原列表/范围/清理信息仍在同页下方或返回路径可达 |

## 与预览的明确差异

本实现用真实 adapter/envelope 与现有路由，不用预览 `data.js`。推荐按钮到真实示例目录；本地入口选择/声明/确认并实际运行。示例没有预览新增搜索和同页全量详情；本地不默认假定首模型、两条 FAIL 或当前 PV-001 可解释任何规则。

采用 v2 间距和推荐家族/层级，同时保留现产品正文 16px（预览是 15/14px），不靠缩字满足首屏。状态、名称、来源/限制完整；连续无空格的名称也换行，不裁掉字段。采用浅色已批准身份，系统 dark preference 不另造未审主题。

查询不复制预览 q/item/view URL 或跨刷新持久化；基本返回/跨语言连续性已实现，不承诺原像素滚动位置。实际本地上传没有可靠样例归属字段，故显示真实输入身份而不是固定“公开样例”。

## 实际浏览器证据与截图

Edge 155.0.4283.45 headless、外部既有 Playwright 1.62.1、Node 24.19.0。按中英 1280×900、375×812 实际建立视口，没有编辑/拼接截图。源码来源是上述实现提交；不是沿用 4904192 的预览图片。代表截图与全部本机证据入口由实现会话文件链接提供，公共报告不写绝对本机路径。

| 场景 | 实测与证据组 |
|---|---|
| 首页主按钮 | scrollY=0、正文16px；375 中文 top494.9/bottom539.3，英文 top617.8/bottom662.2，完整在812内且说明在按钮后；`home/` 四张与 home-bounds.json |
| 目录/首检/单项/复检 | 中英两视口实际路由；13/8/6、八项链接、五项展开、跳结果、同项复检及对象切语言；`states/*-directory/first/item/same-item-recheck`、`after/*-example-item-locale` |
| 本地手机/桌面搜索 | 零/单/清空 0/1/2 行、隐藏行高度0、键盘开项及返回；`search/`、`after/` |
| 当前对象与查询 | 同一 finding 切中英不丢 query；显式 Back / browser Back、筛选外返回聚焦搜索、清空聚焦输入；`after/`、`states/*-return/outside-filter` |
| 定位后换对象 | 中英桌面及375真实选择 chimney→定位→house（手机先返回列表）；新标题进入视口，route改到新 finding、没有旧 locate hash；`states/*-locate/new-object` |
| PASS/N/A/多文件 | 公开 HVAC+Architecture 真实多文件3行；Architecture 真实模型级N/A；明确 SYNTHETIC 名称/Tag 的外部派生测试输入实际跑出2条PASS，原公开文件未改；`states/*-multi-file/synthetic-pass-long/model-na` |
| 错误与读取边界 | 真无文件 refusal；延迟真实 API 的加载；有明确 CONTROLLED 标记的500/恢复、缺名/缺文件名/未知规则 envelope 注入；不是实际私有模型结果；`resilience/` |
| #58/#60 | 实际 adapter 的 requirement-relaxed 与 semantics-changed 场景及单项，原条件/whole-scope/结论改变不等于原条件满足句仍在；`resilience/recheck-*.png` |
| 断点/长字段 | 639/640/641/700/701 隐藏搜索；701/768/900 未选列表满宽、已选左列表右详情；375/1280 连续181字符名不横向溢出；layout日志、真实合成长名图 |

保存 baseline/red/green 日志、几何 JSON、最终 PNG 和 SHA-256 manifest。输入/范围/清理截图可能包含本机 checks 目录，**只作本机验收资料，不作为公开 README/视频素材**。CONTROLLED 注入、SYNTHETIC 派生输入均单独标示，不能当未修改公开模型或真实项目的检查结果。

浏览器命令是显式独立 gate，不由 pytest 自动收集；需要现有外部 Playwright/浏览器与 checkout 外检查目录。可复跑 `doctor_ui.browser.cjs`、`doctor_mobile_search.browser.cjs`、`doctor_ui_states.browser.cjs`、`doctor_ui_resilience.browser.cjs`、`doctor_ui_layout.browser.cjs`。`doctor_ui_stress_fixture.py <外部输出.ifc>` 提供可复现派生输入并拒绝写到 checkout；没有新增产品或测试安装依赖。

## 工程门禁与反事实

使用项目已有 `.venv`，每步实际运行到末尾；不声称新 clone/new venv 安装。固定 ids-tool 1.0.124 在 PATH，EPC_REQUIRE_IDS_AUDIT=1，无 skips。

| 门禁 | 结果 |
|---|---|
| Ruff | exit0；初次新增测试 driver 两行超长已修正，最终全绿 |
| 完整 pytest | exit0；1276 passed、11698 subtests passed、0 skipped；最终完整运行137.30秒 |
| Pipeline run | exit0；6 models、44 elements、121 findings、21 issues |
| Generated diff / 完整 porcelain | exit0、diff空，run前后完整状态一致，没有新增生成输出 |
| Generated SHA-256 集合 | 36文件，0 changed / 0 added / 0 removed |
| Snapshot | exit0；contract-1.7，20件 artifact unchanged；未refresh、未改determinism或snapshot测试 |
| Dashboard core | exit0；CORE_ONLY_NOT_STAGE_3B_COMPLETE |
| PBIP | exit0；PBIP_STATIC_CONTRACT_AND_EVIDENCE_INTEGRITY_PASSED |
| pip check | exit0；No broken requirements found |
| UI/设计辅助 | 五个 browser gate passed；diff --check passed；显式 doctor/static premium strict 0 findings；文档token/结构/字体映射及六组前景对比 passed（最低5.413:1） |

新增两项 Node-backed pytest 保证同 check handoff 一次消费、普通刷新不恢复、另一检查清空、非法/错 route 数据丢弃。已有英文 registry owner 检查纳入新 UI 表；静态树门禁允许新 JS 模块，继续禁止打包结果/JSON等 fallback，未改变其源数据真实性要求。

先在未改产品的 merged main 实测：示例单项切语言原本就保留独立 route；本地 query 丢失、桌面详情内滚动、缺返回/输入身份等才是实际差异。内部新故障包括初始首页滚动、重复当前语言留下 handoff、加载旧来源、未知 finding 隐藏焦点，都先有实际 RED 再修复。内部只读 review 的两项 P2（701–900列顺序/满宽、连续名称横向溢出）同样 RED→GREEN；手机满宽 selector specificity也随后被回归约束。没有未处理的内部 review finding；这不替代指定 TD/UX/BIM 审查。

## 未完成项与边界

PR 创建时 exact-head Ubuntu/Windows CI 正在运行；以 PR 最终 head 的逐步骤结果为准，后续完成状态在 PR 描述及实现会话证据更新。独立 TD/UX/BIM/PM 实页审查尚未完成，文字/移动/折叠不能因本轮工程全绿而自动等义批准。

官方 designmd CLI 未安装，本轮不为 lint 添加库；用了现有 strict auditor 和本机明确 token/结构/对比检查，不能冒充官方 lint。未做真人首访/C2、实体手机/软键盘/真实系统IME、Safari/Firefox、屏幕阅读器、完整200%缩放、超大IFC性能或 Revit 修改；只做脚本 composition 事件和现有浏览器实际键盘。浏览器禁止 sessionStorage 时同对象 route仍保留，query跨语言恢复会降级，未声称该环境的连续性通过。

未冻结、未打tag/release、未定稿 README 实图/实际视频；3D不在范围。10/14仍是可审候选目标，最终展示/冻结按同SHA独立验收决定；本轮不预填未来通过。
