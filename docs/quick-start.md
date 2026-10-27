# Phase 2 candidate quick start / 快速开始

[English overview](../README.md) · [中文介绍](../README.zh-CN.md) · [Exact-commit CI and demonstration](evidence/phase2-candidate/README.md)

## Install the complete candidate checkout

Follow the Windows or Ubuntu commands in the [README](../README.md#quick-start).
Use Python **3.14** with venv/pip, Git and a modern **WebGL2** browser. The native
IfcOpenShell dependency does not support Python 3.15. Candidate CI verifies
Windows and Ubuntu; macOS is not a certified candidate platform.

Clone `feat/doctor-product-phase1` while the candidate PR is unmerged. For an
immutable reproduction, compare `git rev-parse HEAD` with `source_sha` in the CI
artifact manifest and check out that SHA. Keep the complete repository: the
framework wheel is not a standalone installer for the Doctor application.
Normal use needs no Revit, Node.js, .NET audit tool or OpenAI key.

Run from the repository root using that checkout's virtual-environment Python.
The server binds to 127.0.0.1 and prints its browser and data-directory addresses.
Choose an external writable `--checks-dir`; use the same directory after restart.
If port 8765 is busy, add `--port 8770` and change the browser URL accordingly.

## Bring your rules into a purpose review

1. Open <http://127.0.0.1:8765/projects.html?lang=en> and create a project.
2. In **Project rules**, download the editable template. Keep `manifest.json` at
   the ZIP root; edit purposes and evidence methods there, with executable checks
   in `rules/*.toml` listed by `rules/ruleset.toml`.
3. Upload the ZIP for preview. Check source/version, applicability, requirements,
   manual evidence and unsupported parts, then name the confirmer/team and adopt.
   Uploading is not execution. This version does not convert Office/PDF documents.
4. Add a model and import one IFC. Save its revision with **Permanently retain this
   original IFC…** selected. Source and revision are stored together, then the
   purpose form opens for that exact revision without another file upload.
5. Select purpose and scope, run the review and follow element/requirement/observed
   value/next action in each problem card. Supply required human evidence and
   explicitly reassess; saving a note alone does not change the conclusion.
6. Export an updated IFC into the same model slot and compare purpose runs.
   The summary separates same-rule passes, evidence changes, removal and changed
   classes/scope. Restart with the same checks directory to reopen the records.

Source retention defaults off. If skipped, saving still preserves the report and
geometry. Historical revisions missing source offer an exact SHA-matching
attachment. A different export belongs in a new revision. Retained sources stay
in the local project database; include them in your backup.

## Explore public geometry, save and reopen

1. Open <http://127.0.0.1:8765/review.html?lang=en> and choose **Load public example**.
   No uploaded file or existing project is needed.
2. Select a result, then **Focus element** / **Isolate element**. The three-file
   public example contains 39 elements and 32 real renderable shapes. Information
   prompts and missing geometry remain distinct from rule failures.
3. Choose **Save to project**, create a project/logical model and save R1. This
   retains the report, rule snapshot and triangle geometry.
4. Record an owner, work status and note. **Ready for recheck** is a work record;
   it does not change a machine FAIL to PASS.
5. Stop the server with Ctrl+C. Restart with the same `--checks-dir`, open
   **Projects & rechecks** and choose the revision. Its report and real geometry
   reopen without re-uploading the IFC.

Revision data is in `<checks-dir>/projects/library.sqlite3`. Back up the entire
external checks directory while the server is stopped. Report-only snapshots do
not archive the original IFC; keep source models separately unless you selected
source retention. The federated public example cannot retain a single IFC. Clearing browser
storage does not delete this library. An empty directory opens an empty library.

## Import a revision and explain the change

Import a single-file source-tool re-export, select **Save to project**, and choose
the existing project/model slot. Compare R1/R2 from the project, open the exact
saved result and download the Markdown work brief. Pairing uses unique GlobalIds
and an unchanged rule basis. A passed rule, a missing object, a changed IFC class
and a changed checking basis are distinct. Actual classification and engineering
acceptance belong to a person with project context. The public federation can be
saved/reopened; cross-revision pairing currently requires one IFC file per slot.

The [current demonstration](evidence/phase2-candidate/README.md) reproduces a
revision example from clearly labelled public synthetic source geometry. It does
not present that exercise as a Revit edit or engineer-approved repair. No private
authoring project or previously populated database is needed.

## Local guidance and optional AI

Rule guidance works without an account. Optional generated advice needs the
user's own `OPENAI_API_KEY` in the server environment; see [setup](../doctor/README.md#openai-setup).
Keep secrets out of the repository and browser. Selected finding text can be
sent; IFC and meshes are not sent by this action. A configured key does not prove
a live call or engineering correctness. Candidate CI uses no provider secret.

## Verify a new environment

From the candidate checkout, using Python 3.14:

```bash
python3.14 tools/verify_clean_install.py --source . --output ../phase2-clean-check
```

On Windows use `py -3.14 tools/verify_clean_install.py --source . --output ../phase2-clean-check`.
Choose
a **new output directory outside any checkout**. The supervisor clones the exact
commit, creates another venv, installs it and tests the real server, persistence,
comparison and process restart. It does not copy dirty application files or
reuse an existing database. Read `evidence/clean-install.json`,
`evidence/smoke.json` and the logs; compare their source SHA with the candidate.
Both OS results are available in the same-SHA CI artifact.

Browser recording additionally needs pinned Node.js/Playwright QA tooling, not
an application dependency. [Recording commands](evidence/phase2-candidate/README.md).

## Troubleshooting and limits

- Keep `-c core.longpaths=true` on Windows; a short checkout path also helps.
- For import errors, check the venv Python, repository root, complete source and
  pip installation. Do not add this developer's machine paths to `PYTHONPATH`.
- A viewport failure leaves check evidence readable. Inspect its technical
  details and retry; a failed viewer is not evidence of missing IFC geometry.
- Imports show worker stages and progress. Cancel waits for the native process to
  stop; a failed/cancelled job keeps the existing report and viewport. A lost
  response can resume polling. The server enforces a 600-second deadline; use
  `--import-timeout-seconds` to choose another positive deadline at startup.
- The 50 MB browser upload cap is not a capacity guarantee. A recorded 2,055-mesh
  case took about 179.5 seconds under the old synchronous API. One earlier cold
  3D failure remains unexplained; technical details now include the request ID
  and failure phase. [Measured scope](handoffs/model-case.md).
- Save important work. The report/geometry cache is limited to 16 payloads and
  64 MiB; saved revisions restore from SQLite after eviction or restart. Notes,
  comparison and briefs read reports without restoring full geometry. Unsaved
  completed imports retain at most four temporary results / 256 MiB.
- The [October 13 recording](evidence/doctor-resume-ui-en-2026-10-13/doctor-live-en.webm)
  and [earlier phase evidence](evidence/product-phase2/README.md) are historical.
  Use the current SHA-bound CI artifacts for candidate acceptance.

## 中文操作指南

按[中文 README](../README.zh-CN.md#快速开始)克隆候选分支，建立 Python 3.14 环境，
安装完整源码并指定仓库外的 `--checks-dir`。普通运行无需 Revit、Node 或 AI 账户。
固定复现时，把 `git rev-parse HEAD` 与 CI 附件里的 `source_sha` 对齐。

1. 打开 <http://127.0.0.1:8765/projects.html?lang=zh> 创建项目，在 **项目规则** 下载可编辑模板。
2. 编辑 ZIP 根目录的 `manifest.json` 用途与证据方法，以及 `rules/` 内的 TOML 要求。
   上传后核对来源、版本、适用对象、要求及不支持部分，记录确认人和团队，再采用。
   上传成功不等于执行；当前不转换 Excel、Word、PDF。
3. 添加模型并导入单个 IFC，保存修订时明确勾选留存原文件。源文件与修订一并保存，
   然后进入该修订的用途审查，无需重复上传。默认不勾选；缺源历史记录才需附加同 SHA 原文件。
4. 选择用途和范围，按问题卡片查看构件、要求、实际值和下一步，补充证据后明确复检。
   处理备注或 **待复检** 状态不会把机器 FAIL 改成 PASS。
5. 导入新导出的 IFC 到同一模型槽，查看用途复检摘要；删除、改分类和范围变化不算修复。
   Ctrl+C 停止后，用**同一个存储目录**重启，在项目内重开保存版本。

如需先体验几何，3D 工作台仍提供公共联邦示例：39 个构件、32 个真实网格，可聚焦、
隔离并保存重开。该多文件示例不能提供单份原 IFC 执行企业规则。

数据在 `<checks-dir>/projects/library.sqlite3`。停止服务后备份整个外部存储目录，
未选择留存的原 IFC 需另行保留。清理浏览器缓存不会删除 SQLite；换空目录则会打开空项目库。
端口忙时加 `--port 8770`，浏览器地址也改为 8770。

从源工具重新导出单个 IFC，保存到同一模型槽的新修订，比较证据并下载简报。
删除、改分类、不适用或规则变化不等于修正；工程取值和接纳仍由有上下文的人判断。
公共联邦示例可保存重开，跨版配对目前只支持单文件槽。

[新版演示](evidence/phase2-candidate/README.md)用带几何的公开合成源生成前后导出，
不依赖私有模型，也不冒称 Revit 修改或具名工程师签认。规则指导无需密钥；可选
OpenAI 建议的配置和发送范围见[说明](../doctor/README.md#openai-setup)。
Windows／Ubuntu 的安装、保存和重开结果以当前完整 SHA 的 CI 附件为准；旧录像保留为历史。
