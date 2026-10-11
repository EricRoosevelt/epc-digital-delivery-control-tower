# UX-01：手机本地搜索窄修交接

2026-10-11（新加坡）。实现者报告；独立技术审核与合并尚未进行。

## 结果与版本

已完成最小修复并建立 [PR #63](https://github.com/EricRoosevelt/epc-digital-delivery-control-tower/pull/63)。应用改动只有 `doctor/static/doctor.css:448` 的一个选择器：手机卡片布局只对没有 `hidden` 属性的行设置 `display: block`。搜索逻辑、详情选择、领域文字、规则和契约均未修改。没有新增产品依赖或引入第三方源码。

- 起点：实际核对 GitHub `main` 为 `4904192ab3510b501a6ce906819a42a395de36d8`；提交时再次核对仍相同。本地名为 main 的分支较旧，没有拿它作起点。
- 修复及浏览器回归测试提交：`e9b4d640056b3747ee3f203a4b75a36dc31d89f2`。
- 分支：`fix/doctor-mobile-search`，从上述 main 建立原生托管隔离 worktree；共享旧 checkout 的分支和用户文件未切换、重置、暂存或覆盖。
- 原生首次创建遇到已有 buildingSMART fixture 的 Windows 长文件名限制；启用 Git 本仓库 `core.longpaths=true` 后重新创建成功。没有更改 fixture 字节。
- PR 已 attach 到实现会话。没有自批、自合并、打 tag、发布或向其他会话发送消息。

任务依据是共享目录中已有的 `2026-10-11-closeout-ux.md` 的 UX-01 和 `2026-10-11-pm-ui-redesign-brief.md`。本改动不实施该 brief 的 UI 重设计。

## 原因与实测反事实

搜索原本正确设置了不匹配行的 `hidden=true`，计数也正确。`tr[hidden]` 和手机 `.ws-list tr` 的选择器优先级相同，后出现的手机 `display: block` 覆盖隐藏规则。桌面没有这一覆盖。

先写 `tests/doctor_mobile_search.browser.cjs`，在没有修复的 main 上运行。第一次脚本因按钮名称写错而超时；修正测试选择器后，正式红灯来自真实故障：中英 375 的零匹配和单匹配共四项失败，桌面对应状态及清空正常。零匹配时，两条行的 `hidden=true`、computed display 为 `block`，高度各约 199.67 px，仍然可见。没有把测试选择器超时算作缺陷证据。

应用一个选择器修复后，同一浏览器测试通过；手机隐藏行 computed display 为 `none`、高度 0、没有布局矩形。此次没有需要改变发布契约的理由，未进行 snapshot refresh 或编辑生成文件。

## 浏览器证据

实际使用 Windows Edge 155.0.4283.45（headless）、既有外部 Playwright 1.62.1、Node 24.19.0。不是手机实体机测试。程序实际选择仓库公开 `data/raw/Building-Hvac.ifc`、声明 HVAC、确认范围、运行检查，然后访问真实结果页；没有伪造 API 结果或用静态 HTML 替代应用。

| 状态 | 中文 375×812 | 英文 375×812 | 中文 1280×900 | 英文 1280×900 |
|---|---|---|---|---|
| `ux-no-match` | 0/2，零行，空结果说明可见 | 同左 | 同左 | 同左 |
| `house` | 1/2，仅 house fireplace cap | 同左 | 同左 | 同左 |
| 键盘全选并清空 | 2/2，两行恢复 | 同左 | 同左 | 同左 |
| 单匹配链接键盘 Enter | 打开 house 详情；搜索与选中项保留；仅匹配行可见 | 同左 | 同左 | 同左 |
| 清空后点击 chimney 行状态单元格 | 打开 chimney 详情；搜索为空 | 同左 | 同左 | 同左 |

截图不是重绘或用桌面图冒充手机：浏览器逐个建立相应视口，截图前把列表或详情滚动到可见位置。人工查看了修复前英文手机零匹配、修复后英文手机零匹配、中文手机单匹配、英文桌面单匹配和中文手机详情截图。

本机交接证据保留 `before.log`、`before/observations.json`、`after.log`、`after/observations.json`、前后各 16 张实际视口截图、`after-manifest.json` 和工程门禁日志。本机位置通过实现会话的文件链接提供，未将绝对本机路径写入公开报告。修复后 observations SHA-256：`543c9785f0c494b104f774f6683a025595f206291ea731be8d14e70b514bec50`。

回归测试复跑方式（先使用 checkout 的 Python，启动独立检查目录）：

```text
python doctor/serve.py --port 18874 --checks-dir <checkout 外的临时检查目录>
node tests/doctor_mobile_search.browser.cjs http://127.0.0.1:18874 <可选截图目录>
```

需要外部已安装的 Playwright 和浏览器；如不在模块查找路径上，用 `NODE_PATH` 指向现有运行时包目录。Windows 默认用已安装 Edge；`BROWSER_CHANNEL` 可指定已有浏览器。本测试是独立显式命令，不由 pytest 自动收集，也没有加入 CI 的新浏览器安装步骤。审核者复验时须实际运行此命令，不能只以 pytest 绿灯替代 CSS 浏览器验证。

## 完整工程门禁

按 AGENTS 顺序使用项目已有 `.venv`，在隔离目录执行；没有声称新建环境安装验证。`ids-tool.CommandLine` 1.0.124 已安装，设置 `EPC_REQUIRE_IDS_AUDIT=1`，套件没有跳过 IDS 审计。

| 命令/检查 | 实际结果 | 本机日志 |
|---|---|---|
| `python -m ruff check .` | exit 0 | `01-ruff.log` |
| `python -m pytest -p no:cacheprovider tests -q`（IDS 必跑） | exit 0；1274 passed，11633 subtests passed；无 skips | `02-pytest.log` |
| `python -m epc_control_tower.cli run` | exit 0 | `03-run.log` |
| `git diff --exit-code -- data/processed reports` | exit 0，无 diff | `04-generated-diff.log` |
| `git status --porcelain --untracked-files=all` | run 前后完全相同：仅 CSS 修改与新增浏览器测试；没有新增或修改生成产物 | `pre-run-status.txt`、`05-post-run-status.txt` |
| `python -m epc_control_tower.cli snapshot` | exit 0；contract-1.7 的 20 个 artifact 不变 | `06-snapshot.log` |
| `python src/validate_dashboard.py --mode core` | exit 0 | `07-dashboard.log` |
| `python src/validate_pbip.py` | exit 0 | `08-pbip.log` |
| `python -m pip check` | exit 0；No broken requirements found | `09-pip-check.log` |

相关基线测试另有 71 passed、427 subtests passed。`git diff --check` 通过。前端技能 strict 静态审计 exit 0、0 findings，证据为 `premium-audit.json`；它不替代上述真实浏览器检查，也不证明全应用 UX 或 WCAG 合规。当前没有 DESIGN.md；本次窄修不创建或改写设计系统，沿用现有 CSS 与共享 workspace 列表及详情组件。

## 未完成项与审核边界

PR 创建时 Ubuntu/Windows CI 都在运行，未预填通过。以 PR 最新提交的 checks 为准。独立技术审核及合并由技术收口会话负责；本报告的通过是实现者本轮验证，不是独立审批。

未执行实体手机、Safari/Firefox、屏幕阅读器、全应用可访问性、C2 真人走查、Revit 修改或新环境安装。UI 重设计、领域扩审、视频及 README 素材定稿不在本次授权范围；这些事项没有被本修复关闭。
