# IfcQA 前端复用与 API 映射评估

日期：2026-10-02。负责：产品经理。状态：源码可行性评估；未复制外部代码、未安装依赖、未执行集成或性能测试。

## 1. 结论

部分显示字段可以映射，部分组件值得复用；整套前端不能直接连接当前 Doctor 后端。接口地址、数据结构和用户决策均不兼容。增加投影可以帮助复用检查详情，但不能把 Purpose 事项变成一条普通 QA 问题而不丢信息。

建议近期参考交互、完善当前 Doctor；后续遇到明确定位需求，再评估局部组件复用。若要整体移植，属于另一个前端集成项目，需要 React 构建、数据边界、页面状态和新后端能力，不能当成一次换皮。

## 2. 固定证据与检查范围

| 项 | 版本及来源 |
| --- | --- |
| 上游 | `tommylee0923/ifcqa-tool`，提交 `517654cb79c8ba9acd213a3542e877f5929ce626` |
| 上游 API | [auditApi.ts](https://github.com/tommylee0923/ifcqa-tool/blob/517654cb79c8ba9acd213a3542e877f5929ce626/frontend/src/api/auditApi.ts) |
| 上游类型 | [audit.ts](https://github.com/tommylee0923/ifcqa-tool/blob/517654cb79c8ba9acd213a3542e877f5929ce626/frontend/src/types/audit.ts) |
| 上游应用与查看器 | [App.tsx](https://github.com/tommylee0923/ifcqa-tool/blob/517654cb79c8ba9acd213a3542e877f5929ce626/frontend/src/App.tsx)、[viewer.ts](https://github.com/tommylee0923/ifcqa-tool/blob/517654cb79c8ba9acd213a3542e877f5929ce626/frontend/src/viewer/viewer.ts) |
| 上游依赖与许可证 | [package.json](https://github.com/tommylee0923/ifcqa-tool/blob/517654cb79c8ba9acd213a3542e877f5929ce626/frontend/package.json)、[LICENSE](https://github.com/tommylee0923/ifcqa-tool/blob/517654cb79c8ba9acd213a3542e877f5929ce626/LICENSE) |
| 我方后端 | PR #22 已合并 `1548bc376f240b8ec69f90155567878d8406a1a0`；该版本的 `doctor/serve.py`、`internal/doctor_adapter/{envelope,details}.py`、评估 record 类型 |
| 我方 UI | PR #21 分支 `ce3f6517c814de033b65043530c467322992d6b7`；可点击首次检查路径，待经理短测 |

以下判断来自文件阅读。没有证明上游能在本机完整构建，没有运行两套后端互通，也没有核完其全部传递依赖和资产许可。

后续状态，2026-10-02：我方 PR #21 已到 `005c43d414e3a3bc3af469696cf37e98a6269814`，用户转交领域 ALIGNED 和经理复检初步通过。本评估保留上表实际读过的源码基线，不声称对新 HEAD 重新执行过 API 集成；下一轮继续采用现有 Doctor，按受控真实模型任务推进。

## 3. 端点不是直接对应关系

| IfcQA 前端请求 | 当前 Doctor 提供 | 可复用程度及实际缺口 |
| --- | --- | --- |
| `GET /runs` → `AuditRun[]` | `GET /api/runs?mode=fixture或real` → `{mode,runs:[{run_id}]}` | 可重做列表适配。Doctor 是固定场景目录，不是数据库历史；ID 是字符串，没有同形的时间、文件名和检查统计 |
| `GET /runs/{数字ID}/issues` → `AuditIssue[]` | `GET /api/envelope?mode=…&run=…` → record 或 refusal | 不能直接替换。要保留两种 outcome；record 包含活动、分组、成员／成员对、路径、行动、处理方和 successor |
| `POST /upload`，IFC、可选 JSON 规则集、GLB 转换 | 无对应 POST 接入 | 上传按钮不会创造接入能力；需另做文件许可与接入、版本身份、适用性、检查执行及结果获取。上游 JSON 规则不是我方 TOML 规则或 Pack |
| `GET /rulesets` 与 `GET /rulesets/{id}` | 无对应目录接口 | 规则集不等于 Purpose Pack 或 Overlay。需独立定义用户选择和兼容目录，不伪装成同一对象 |
| `GET /model/{filename}.glb` | 无 GLB 端点；静态服务只提供 HTML/CSS/JS | 需模型转换或其他查看格式、资产服务与版本绑定。不能仅补一个 `glb_filename` 字符串 |

查看器 `viewer.ts` 还有独立写死的 `/runs/{id}/issues` 请求和 `/model/{filename}` 路径，因此只改 `auditApi.ts` 不足以接通整个应用。

## 4. 字段级映射：哪些有数据，哪些不能猜

| 上游字段或概念 | 我方可用来源 | 限制／设计要求 |
| --- | --- | --- |
| `issue_code` | `finding_key` 或显示用 `rule_id`，只在检查详情视图 | Finding、Issue、Purpose 事项是三个不同对象；稳定选择标识须保留真正对象键，不能把问题类型当唯一键 |
| `message` | 已核 `finding_details.reason`；Purpose 动作另取 `subscope.route.next_action` | 检查原因与行动是不同字段；不拼成新的业务判断 |
| `expected`、`actual` | `finding_details` 同名字段 | 已合入 #22；只解释匹配引用和封存依据的那次检查，不是全量检查 API。没有条目的引用显示未提供；实际值披露沿用当前 UI 边界 |
| `path`（属性路径） | 当前明细无独立结构化字段 | `expected` 是原文，不通过解析英文凑属性路径；需后续检查侧提供可信结构 |
| `global_id`、类别、名称 | `elements[element_key]` | 元素库存有这些值，但 `finding_details` 不带每条 finding 的 element_key；共用证据不能臆配给某个成员。检查行定位需核关联来源 |
| `severity` | Doctor 明细不提供 | 如未来新增检查投影，可单独取同次规则的验证元数据并标明用途；绝不由 READY/BLOCKED/UNKNOWN 换算 |
| `total_elements`、`total_issues` | 当前没有同定义字段 | 库存条数不是本次已检查数；事项数不是 Finding 或 Issue 数；模拟场景目录也不是历史运行。不得为适配看板伪造统计 |
| `run_timestamp`、数字 `id` | 当前场景 ID，不是同形历史元数据 | 优先修改消费类型以保留源身份。不得读系统时钟补日期，不能靠场景顺序制造生产运行身份 |
| 处理方、活动、构件对、来源标记、复检比较 | 我方 record 内已有 | 上游 `AuditIssue` 没有对应字段；需要新显示模型与相应组件，单纯字段改名无法保留 |

建议保留检查详情与交接事项两种显示模型。UI 可展示已有数据、做计数与筛选，但判断、沿用状态、成员去向和条件证明仍由 Framework 给出。

## 5. 三维定位的额外要求

上游查看器维护 `GlobalId → meshes`，通过 GLB 节点名称找 GUID，选中事件携带一个 `gid`。这适合其当前运行视图，尚未证明适合我们的多模型、版本和构件对场景。

我方后续最小定位键应包含模型、版本和源元素标识；选择成员对必须能分别选择两侧。不得把不同模型的相同 GlobalId 合并，不因文件同名加载其他版本，不把几何居中／相机适配当成两侧模型对齐证据。

GLB 转换是新能力，不是已有 canonical 或 BCF 数据自然变成 GLB。转换工具、格式、许可、身份映射与坐标必须另行测量；不得为新查看器重写已发布产物。模型没有获准再分发时，不把 IFC 或派生 GLB 放进公开演示。

## 6. 复用方案比较

| 方案 | 成本与风险的性质 | 本轮建议 |
| --- | --- | --- |
| 参考交互，在现有原生 JS Doctor 落地 | 不引入 React；重点在行动组织和可读数据。仍需要用户验收 | 推荐近期路线 |
| 选择性复用布局、详情或查看组件 | 要维护上游来源、React 宿主或明确的移植边界，修正数据契约与状态；查看器另需模型资产 | 后续有具体需求时评估；先选择一个组件并测量收益 |
| 整套 React 前端替换＋兼容后端 | 要改主流程、检查与评估类型、身份、拒绝、复检、中文、上传、目录和模型端点；是迁移项目 | 技术上可构建，当前不推荐直接采用；不声称已跑通 |

整套复用可以用于另做“验证结果查看器”，但它不能自动成为完整 BIM Doctor。若只投影 FAIL 行来快速演示，会丢失零 finding 的证据缺口、人工判定与当前可以开始的工作，必须限制并标注用途。

## 7. 许可证与取用条件

所查提交的根许可证是 MIT，版权为 Tommy Lee（2026）；许可证文本允许修改和再分发，并要求在软件副本或实质部分保留版权与许可声明。因此根许可证层面存在代码复用路径，但本轮没有核完依赖、图片、示例模型或其他独立许可。

仓库现行[开源采纳规则](../open_source_adoption.md)把外部界面列为参考，复制前须过 Review Gate。后续如决定引入代码：

1. 确定具体文件和依赖，固定提交与依赖版本，核查实际分发物的许可；不自动引入上游全部后端、模型和资源。
2. 保存原始来源、原始文件 SHA-256、修改记录与所需版权／许可；本轮列的 GitHub 提交或 blob 标识不能替代文件 SHA-256。
3. 更新 `docs/open_source_adoption.md` 和 `THIRD_PARTY_NOTICES.md`，按仓库规则排除 GPL/AGPL 实现代码入树；若涉及具有独立限制的工具，按其分发方式单独评估。
4. 作品集明确哪些布局／组件来自 IfcQA，哪些判断、适配和验证由本项目实现。技术上能接线不等于可把别人作品作为原创展示。

本轮只写评估和来源链接，没有引入第三方代码或依赖；既有参考条目未被转换为已采用组件。

## 8. 后续集成验证的停点

若产品决定试用组件，技术总监先定义一个可丢弃的小范围探查：同一条真实检查详情能否显示并定位到正确对象，同时不丢失拒绝与模拟来源。先验证所选组件，不做平台迁移。

任何保留实现至少验证：

- 未匹配的旧引用不读今天规则；不存在的明细明确缺失。
- 两模型相同 GlobalId、成员对、模型级问题分别可表达，不误定位。
- 拒绝不变成空成功，fixture 与 real 不混用，未知状态不默认为通过。
- 运行切换和过期响应不展示错误版本；模型加载失败仍能读到文字行动。
- 主路径比当前版本更易完成用户任务，真人短测提供证据。
- 运行与展示不改变生成物、评估身份或已发布契约；仅当真实扩展移动这些边界时，另走实测与契约流程。

目前结论停在源码可行性，不能作为“已兼容”“可直接替换”或“已获生产验证”的依据。
