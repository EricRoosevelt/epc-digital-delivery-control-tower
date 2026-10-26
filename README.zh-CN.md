# BIM Doctor — 企业规则与用途审查

**带入项目规则，审查明确的交付用途，再沿证据复检变化。**

[English](README.md) · [当前候选演示与同提交证据](docs/evidence/phase2-candidate/README.md) · [快速开始](#快速开始) · [Windows／Ubuntu CI](https://github.com/EricRoosevelt/epc-digital-delivery-control-tower/actions/workflows/ci.yml?query=branch%3Afeat%2Fdoctor-product-phase1)

BIM Doctor 是面向工程师和 BIM 协调人员的个人开源应用，在本机浏览器中查看 IFC
模型和检查证据。项目记录留在本机；规则结果与真人工程判断、项目接纳分别处理。

## 这个候选版本能做什么

- **带入并管理规则。** 导入含原生 TOML 规则和用途清单的 ZIP，先看来源、版本、
  适用对象、检查要求和不支持部分，再明确采用为项目内不可变版本。
- **回答交付问题。** 选择内部审核、投标提交或规则包声明的交接用途，绑定模型修订
  和对象范围，由现有 Purpose 引擎判断。未检查、不支持、缺证据都保留为 UNKNOWN；
  没有 FAIL 不等于可以提交。
- **沿证据处理和复检。** 从受阻项进入规则、实际构件与证据；人工判断记录复核人、
  引用和依据，与处理备注分开。新审查说明模型、规则、范围、引擎或人工证据的变化；
  建议中的可能原因始终标为待验证假设。
- **真实 3D 检查。** 载入随附的 buildingSMART 公共模型，或导入单个 IFC；选择结果，
  聚焦和隔离实际三角化的构件几何。
- **项目保存与修订复查。** 保存报告及 3D 快照，记录处理人、状态和备注；把新 IFC
  存为同一模型的新修订，比较证据、下载 Markdown 简报。服务重启后可直接重开保存记录。
- **解释变化。** 分别展示复检通过、仍未满足、新增、构件未找到、不适用和不可比较；
  删除、改分类或检查依据变化不会直接计为修正。
- **本地指导与可选 OpenAI 建议。** 无密钥也能阅读规则指导；配置自己的 API 账户后，
  可按需发送所选问题的文字证据生成建议，IFC 和几何不发送。[配置方法](doctor/README.md#openai-setup)。

三维工作台的四项基础检查覆盖风口类型 PV-001、名称、楼层归属及文件内 GlobalId 完整性。
PV-001 与旧框架共享规则定义和 IfcTester 判断；名称、楼层属于信息提示，不是工程缺陷计数。
企业规则的检查与用途记录单独保存，复用原网格，不改写基础报告。

在 **项目与复查** 内打开 **项目规则**，下载可编辑的公开示例包，预览并采用后进入
**用途审查**。旧修订首次执行新规则时，需明确附加 SHA 一致的原 IFC；源文件仅留在
本机项目库，供后续复检，企业规则和源模型不会发送给 AI 服务。
示例分别演示纯机器内部审核、需要人工证据的投标提交，以及需真实对方模型的交接。
首版不解析 Excel、Word 或 PDF。[规则包格式与流程](docs/product/enterprise-purpose.md)。

## 快速开始

使用 **Python 3.14、Git，以及支持 WebGL2、ES modules 和 import maps 的浏览器**。
候选 CI 平台为 Windows 和 Ubuntu。运行应用无需 Node.js、Revit 或 OpenAI 账户。
必须保留完整源码检出；现有框架 wheel 不包含整个网页应用和配套资源。

候选代码位于 `feat/doctor-product-phase1`；候选 PR 合并前，默认主线克隆可能仍是旧阶段。

**Windows PowerShell**

```powershell
git clone -c core.longpaths=true --branch feat/doctor-product-phase1 https://github.com/EricRoosevelt/epc-digital-delivery-control-tower.git
cd epc-digital-delivery-control-tower
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
$doctorState = Join-Path $env:LOCALAPPDATA 'BIMDoctor\phase2-rc1'
.\.venv\Scripts\python.exe doctor/serve.py --checks-dir "$doctorState"
```

**Ubuntu／Bash**

```bash
git clone --branch feat/doctor-product-phase1 https://github.com/EricRoosevelt/epc-digital-delivery-control-tower.git
cd epc-digital-delivery-control-tower
python3.14 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python doctor/serve.py --checks-dir "$HOME/.local/state/bim-doctor/phase2-rc1"
```

打开 **[3D 检查工作台](http://127.0.0.1:8765/review.html?lang=zh)**，选择 **载入公共示例**，
保存到项目后进入 **[项目与复查](http://127.0.0.1:8765/projects.html?lang=zh)**。
按 Ctrl+C 停止，再用**同一个存储目录**启动即可重开。
端口被占用时加 `--port 8770`，浏览器地址也改成 8770。

[逐步操作、备份与排错](docs/quick-start.md#中文操作指南) ·
[本机存储细节](doctor/README.md#projects-and-revision-rechecks)

## 复现同一版本与演示

运行 `git rev-parse HEAD`，应与候选 CI 附件清单中的 `source_sha` 完全相同。
固定复现时，先 `git checkout <source_sha>`，再安装。Windows 和 Ubuntu 都运行完整检查，
并从新环境验证安装、保存、停止服务及重开。同提交命名的附件包含机器结果、新演示、截图和校验值。

[当前候选证据与录制命令](docs/evidence/phase2-candidate/README.md)说明如何下载或重新生成。
只有 HEAD 相同的 CI 才能证明这个候选；此前旧提交上的绿色结果不作为新版证据。

## 当前边界

这是本机候选版本，尚无经过身份认证的团队派单、通知、自动修改源模型或项目接纳决定。
跨修订配对目前要求一个模型槽对应单个 IFC；公共联邦示例可保存重开，但不跨版本配对。

导入在独立进程中执行，显示真实阶段和处理数量；取消等待服务端确认进程退出。
浏览器单次请求限时 30 秒，状态查询中断后可继续，不会重复启动导入；服务端任务
默认限时 600 秒。计算期间仍可读取已有结果。内存载荷缓存上限为 16 项／64 MiB，
已保存修订从 SQLite 恢复；未保存结果的临时存储有上限，会过期，请及时保存。

上传大小限制不是已验证的容量上限。既有 2,055 网格、107 万三角形案例在旧同步
接口下约需 179.5 秒。一次早期冷加载三维异常仍未定位；现已增加请求编号、几何及
视口阶段诊断，并在浏览器 CI 中验证异常恢复。
[实测范围及限定](docs/handoffs/model-case.md)。OpenAI 建议需要用户自行配置账户，
候选的离线检查和演示不以真实 API 调用为前提。

## 历史素材与开发参考

[10 月 13 日中文录像](docs/evidence/doctor-resume-ui-2026-10-13/doctor-live.webm)
和[早期案例](https://app.notion.com/p/3f81cb00200581f2aad8dd078f9d5fa9)展示之前的模拟交接体验，
保留作历史材料，不作为 Phase 2 候选或源模型修正的证明。

- [开发参考](docs/engineering-reference.md)与[候选版本约定](docs/product/phase2-candidate.md)。
- [规则定义](rules/product-validation/README.md)、[一致性保障](docs/handoffs/rule-parity.md)和[数据格式](docs/data_contract.md)。
- [早期 Power BI／Speckle 工作](dashboard/README.md)。

## 数据来源与署名

公开 IFC 模型来自 buildingSMART International 的
[Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files)，包括 PCERT Sample Scene
和 ISO Spec Reference View 1.2。Copyright buildingSMART International Ltd.
模型采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，输入文件保持原样。
项目自行编写的检查规则与交接设定详见[第三方声明](THIRD_PARTY_NOTICES.md)。
