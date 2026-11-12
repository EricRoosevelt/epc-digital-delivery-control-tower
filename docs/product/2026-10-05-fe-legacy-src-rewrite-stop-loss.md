# 旧 `src/` 脚本静默改写冻结产物：复现条件、最小止损方案与成本

日期：2026-10-05。Framework Engineer 交技术总监，10/9 周报用。**只给方案，没有改任何代码**；不删除任何入口（PM 10/3 决定）。与 #29 无关，不进该 PR。

## 1. 复现条件（已复现）

- 基线：`origin/main` = `d59dee0`，在一次性克隆 `C:\t\srcrepro` 里运行，每个脚本前 `git checkout -- . && git clean -fdx`；`PYTHONPATH` 指向克隆，coverage 记录指到克隆外的临时目录。真实检出没有被碰。
- 条件只有一个：**检出里登记了不止一个项目**（现状就是：`pcert-sample` 与 `iso-reference-view`）。不需要任何参数，按旧 README 的写法直接运行即可。

| 脚本（默认参数） | 退出码 | 已跟踪文件变化 | 说明 |
|---|---|---|---|
| `src/extract_inventory.py` | **0** | **`data/processed/models.csv`、`data/processed/model_inventory.csv`**（+8 行） | 打印 "Wrote 6 models … Wrote 44 elements"；`models.csv` 从 3 行变 6 行，出现第二个 `architecture`、第二个 `structural`，以及 `plumbing` |
| `src/generate_ids.py` | 1 | 无 | 拒绝覆盖冻结的 IDS 文件，并说明原因（已经失败即关闭） |
| `src/validate_ids.py` | 1 | 无 | `ValueError`：契约只描述一个项目，要求设置 `legacy_project_id`（已经失败即关闭） |
| `src/generate_bcf.py` | 0 | 无 | 3 个 topic；重新生成的字节与已发布的相同 |
| `src/validate_bcf.py` | 0 | 无 | 只读 |

**有问题的只有 `extract_inventory.py` 一个。** 根因：它的 `build_registers()` 读入配置里的**全部**项目，而旧版写出器在 Phase 4 已经收窄到 `legacy_project_id`。这正是 AGENTS.md 第 6 条记下的第一次实测（"all eight published CSVs changed and `models.csv` grew a second `architecture` row, while all four exporters reported success"），只是这个兼容脚本当时没有跟着收窄。

## 2. 现有门禁能不能发现（实测）

在被改写的状态下逐个运行：

| 门禁 | 结果 |
|---|---|
| `epc-ct snapshot` | 通过："contract-1.7.json matches: 20 artifact(s) unchanged"（它不读磁盘上的这两个文件） |
| `src/validate_dashboard.py --mode core` | 通过（重复的 `model_id = architecture` 没有被拒绝） |
| `tests/test_legacy_pbip_contract.py`、`tests/test_contract_snapshot.py` | 31 passed |
| `epc-ct run` 之后 `git status` | **干净**：`run` 把两个文件按已发布字节写回 |

含义：

- 本地是静默的。只要不提交，下一次 `epc-ct run` 就悄悄修好了，没有任何提示说它曾经被改坏；在这之间打开 Power BI 项目，读到的是六个模型的注册表。
- 如果有人把改坏的文件提交了，CI 会抓到：CI 先 `epc-ct run` 再 `git diff --exit-code`，`run` 写回已发布字节，于是与提交的内容不同而失败。所以风险是"本地静默误导、可能被提交"，不是"进入 main 而不被发现"。
- 快照与看板校验都看不到它：这是第二个缺口，与脚本本身无关。

## 3. 最小止损方案与成本

| 方案 | 做什么 | 工作量（含测试与全套门禁） | 风险 / 代价 |
|---|---|---|---|
| **A. 收窄（推荐）** | `build_registers()` 只读 `config.legacy_project_id` 指定的项目；未设置且有多个项目时，像 `validate_ids.py` 一样报错退出、什么都不写 | 约 0.5 个工程日：实现约 1 小时；测试钉住反例（多项目克隆里运行 → 两个文件逐字节等于已发布版本；去掉 `legacy_project_id` → 非零退出且无写入）；跑全套门禁 | 已实测：按 `pcert-sample` 收窄后，两个文件与已发布版本**逐字节相同**（3 行 / 39 行）。不动身份、契约或已发布字节，通道 A/B |
| B. 拒绝运行 | 检出里有多个项目就直接拒绝，不尝试写 | 约 2–3 小时 | 更小，但留下一个永远拒绝的入口，等于提前退役却不明说 |
| C. 现在退役 | 删除 `src/extract_inventory.py` 及其在 `test_legacy_shims.py` 的登记 | 约 2 小时 | 需要 PM/TD 决定；PM 10/3 明确本次不授权删除入口；原计划随 Phase 5 与旧适配器一起退役 |
| 附加：补看板校验的缺口 | `validate_dashboard.py --mode core` 拒绝重复的 `model_id`（及同类主键） | 约 2–3 小时 | 与 A 独立；能让以后同类改写在 CI 之外的本地也被发现 |

建议：现在做 A（加附加项则约 0.75–1 个工程日），C 仍留给 Phase 5。只做 A 已经消除复现的静默改写；附加项补的是"改坏了也没人说"的检测缺口。

## 4. 没有做的

- 没有改任何代码，没有删除任何入口；README 早已不再引用这些脚本，那不算修复。
- 一次性克隆会在下次清理时删除；复现命令在 Framework 会话的临时目录 `C:\t\lc\src_repro.sh`。
