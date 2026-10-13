# Quick start / 快速开始

[Project overview](../README.md) · [中文介绍](../README.zh-CN.md)

## Installation

Follow the five commands in the [root README](../README.md#quick-start).
They were tested with Python 3.14 on Windows 11. The virtual environment uses
about 280 MB. Keep `-c core.longpaths=true` in the clone command to avoid Windows
path-length errors. A short checkout path, such as `C:\src`, also helps.

For macOS/Linux, use `python3 -m venv .venv` and `.venv/bin/python` in place of
the Windows Python paths. These setup variants have not been manually verified;
automated tests run on Ubuntu and Windows.

The server prints its address and the location of local check records. If port
8765 is busy, add `--port 8770` to the server command and open that port instead.
Use Ctrl+C to stop it. The application listens on your own machine only.

## Follow the example

Open <http://127.0.0.1:8765/?lang=en>.

1. Choose **Choose a simulated example**, then **Open this example's result**
   under **Step 1**.
2. Find **building element** under **Room data sheets and equipment schedules**
   and choose **See this item**. The list has 13 workflow items, eight needing
   attention; these are not a count of model defects.
3. Read the conclusion, then use **Jump to the next step** for the action and
   what a recheck should establish. The handling team is an example setting.
4. Follow the link to **The models did not change, but a handover conclusion did**
   for the same item's supplied recheck. Its requirement changed while the model
   stayed the same. The page explains why the new conclusion does not establish
   that the original condition was met.

[Watch this flow](evidence/doctor-resume-ui-en-2026-10-13/doctor-live-en.webm)

## Check a local file

1. Choose **Start a local check**, then **Choose one or more .ifc files**.
2. Select IFC4 text files and declare each file's discipline. For a first run,
   use `data/raw/Building-Hvac.ifc` from the repository and declare HVAC.
3. Choose **See the scope of the check**, inspect it, then **Run the check**.
4. Open a result to see the requirement and the object's GlobalId, an identifier
   you can use to find it in a modeling tool.

This checks PV-001: each air terminal declares one of four predefined types.
The public HVAC sample produces two failures. The architecture sample has no
applicable air terminals and produces a not-applicable result. Revit `.rvt`,
IFC2x3, `.ifczip`, and `.ifcxml` files need to be exported as IFC4 text first.

Files are copied into the local checks folder; no model upload service is used.
The page explains how to remove records. To choose a folder, start with
`python doctor/serve.py --checks-dir "<your folder>"`.

## 中文操作指南

先按[中文 README](../README.zh-CN.md#快速开始)安装并启动，打开
<http://127.0.0.1:8765/?lang=zh>。

### 体验示例

1. 点 **选择模拟示例**，在 **第一步** 下点 **打开这个示例的结果**。
2. 找到 **building element** 的 **房间数据表与设备明细表** 事项，点 **查看这一项**。
   列表有 13 个工作事项，其中 8 个需要处理；事项数不是模型缺陷数。
3. 先看结论，再用 **跳到下一步** 查看行动和复检条件。处理团队来自示例设定。
4. 在页面下方打开 **模型未改，但交接判断发生变化** 的同项复检。
   页面会解释：模型未改、要求改变时，结论也可能变化，原来的结束条件仍需另行判断。

[观看中文操作录像](evidence/doctor-resume-ui-2026-10-13/doctor-live.webm)

### 检查文件

1. 点 **开始本地检查**，再点 **选择一个或多个 .ifc 文件**。
2. 选择 IFC4 文本文件并声明专业。可以先用仓库里的
   `data/raw/Building-Hvac.ifc`，专业选暖通。
3. 点 **查看检查范围**，核对后点 **运行检查**。
4. 打开结果查看具体要求与 GlobalId，后者可用于在建模工具中查找构件。

目前检查风口有没有声明四种预定义类型之一。暖通样例得到两条不通过；建筑样例没有
适用风口，显示不适用。Revit 原文件、IFC2x3 和压缩 IFC 等格式需先导出为 IFC4 文本。
文件和记录都留在本机，存储目录会在启动时打印，页面提供清理说明。

### 启动问题

- 克隆时保留 `-c core.longpaths=true`，也可使用 `C:\src` 这样的短目录，避免 Windows 长路径错误。
- 端口被占用时，在启动命令后加 `--port 8770`，浏览器地址也改用 8770。
- 在终端按 Ctrl+C 停止服务。macOS/Linux 的命令差异见本页 Installation。
