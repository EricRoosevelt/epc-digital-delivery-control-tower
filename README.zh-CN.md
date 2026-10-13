# BIM Doctor

**看懂模型检查结果，找到下一步，再看清复检改变了什么。**

[English](README.md) · [观看 80 秒演示](docs/evidence/doctor-resume-ui-2026-10-13/doctor-live.webm) · [产品案例](https://app.notion.com/p/3f81cb00200581f2aad8dd078f9d5fa9) · [快速开始](#快速开始)

准备把建筑模型交给下一个专业时，BIM 协调人员需要的不只是“不通过”清单：
它影响哪项工作？接下来要补什么？重新检查后，变化又来自哪里？

BIM Doctor 把这些问题放到同一条阅读路径里。它在本机浏览器中运行，面向负责模型交接
和专业协调的人。项目使用 IFC 文件——一种在不同建模工具之间交换建筑模型的开放格式。

## 从检查结果走到下一步

随附示例中，一段风管缺少项目要求的资产标识，设备明细表因此无法按这些标识建立对应。
Doctor 先说明受影响的工作与原因，再给出补充信息的行动，以及复检需要确认的内容。

![初检结论：示例项目要求的资产标识缺失，房间数据表与设备明细表事项受阻。](docs/evidence/doctor-case-study-2026-10-13/01-conclusion-zh.png)

页面按 **结论 → 下一步 → 细节** 排列。需要进一步核对时，读者可以继续查看构件标识
和每一条检查结果。

复检示例展示了另一种情况：模型没有改，检查要求变了，同一事项的结论从“受阻”变为
“可以开始”。页面把变化的原因放在结论旁，帮助读者区分“答案变了”和“模型修好了”。

**[观看完整示例](docs/evidence/doctor-resume-ui-2026-10-13/doctor-live.webm)**：80 秒中文界面实录，无旁白。

## 看一个示例，或检查自己的文件

- **体验模拟交接。** 从一个事项的初检结论，看到下一步与随附复检记录。公开模型和
  示例项目设定让你无需准备文件就能体验完整流程。
- **检查自己的 IFC4 文件。** 真实检查风口有没有声明规则要求的类型。目前接受
  `DIFFUSER`、`GRILLE`、`LOUVRE`、`REGISTER` 四种值；结果附有构件标识，方便回到
  建模工具中查找。文件和检查记录保存在本机。

这两个入口回答不同的问题：示例解释一次交接判断，自己的文件检查一项属性声明。
分开呈现，是为了让样例项目的约定留在样例里，而不被直接套到其他人的模型上。

## 快速开始

需要 **Python 3.11 或更新版本、Git 和浏览器**。以下命令在 Windows PowerShell 下验证过，
首次安装下载约 80 MB。

```powershell
git clone -c core.longpaths=true https://github.com/EricRoosevelt/epc-digital-delivery-control-tower.git
cd epc-digital-delivery-control-tower
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe doctor/serve.py
```

打开 **[BIM Doctor 中文界面](http://127.0.0.1:8765/?lang=zh)**，选择 **选择模拟示例**。
在终端按 **Ctrl+C** 停止服务。

[逐步操作、公开样例与常见启动问题](docs/quick-start.md#中文操作指南)

## 当前范围

这是一个个人开源项目，提供模拟交接流程和针对本地 IFC4 文件的一条真实规则检查。
交接判断依赖具体项目的要求；本地检查报告这条规则的结果，不提供模型整体质量评分。
模型编辑、任务派发、从页面发起复检和三维查看器留待后续开发。
主要使用流程支持中英双语，部分次级记录页仍只有中文。

## 了解实现

项目使用 Python 和 IfcOpenShell 读取模型，界面采用 HTML、CSS 和 JavaScript。
底层支持配置检查规则，并把结果导出为其他 BIM 工具可读取的问题文件（BCF）。

- [开发参考](docs/engineering-reference.md)：架构与开发命令。
- [规则定义](rules/product-validation/README.md)和[数据格式](docs/data_contract.md)。
- [自动检查记录](https://github.com/EricRoosevelt/epc-digital-delivery-control-tower/actions/workflows/ci.yml)。
- [早期 Power BI / Speckle 工作](dashboard/README.md)：同一项目的报表阶段。

## 数据来源与署名

公开 IFC 模型来自 buildingSMART International 的
[Sample-Test-Files](https://github.com/buildingSMART/Sample-Test-Files)，包括 PCERT Sample Scene
和 ISO Spec Reference View 1.2。Copyright buildingSMART International Ltd.
模型采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，输入文件保持原样。
项目自行编写的检查规则与交接设定详见[第三方声明](THIRD_PARTY_NOTICES.md)。
