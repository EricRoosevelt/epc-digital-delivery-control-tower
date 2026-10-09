// What the local check says, in both languages, registered with i18n.js.
//
// The local check's own module keeps its own two tables, as language.js does,
// rather than adding to the central ones: the screens are new, and the result
// page reuses the workspace screens, whose words are already in both tables.
//
// The scope of the exercise follows the product decision of 2026-10-03
// (docs/product/2026-10-03-pm-local-ifc-scope-decision.md): only the product
// validation rule set is offered; a FAIL is not a defect of the original
// project; nothing applicable is said as such and never as a pass. Every
// sentence that carries domain meaning is listed for BIM review in
// docs/product/2026-10-03-doctor-english-vocabulary.md.

import { bilingual } from "./i18n.js";

export const LOCAL = bilingual(
  "LOCAL_CHECK",
  {
    mode: "本地检查 · 产品验证练习",
    home: {
      title: "检查自己的 IFC 模型（产品验证练习）",
      body:
        "选择自己导出的 IFC4 文件，只用一条产品验证规则检查风口的预定义类型。" +
        "运行前会说明检查什么、要求从哪里来、结果不能说明什么，以及本机会留下哪些记录。",
      action: "开始本地检查",
      unknown: "未能确认本地检查是否可用，错误原文：",
      status:
        "当前提供模拟示例，以及对自己 IFC4 文件的一项有限产品验证练习；" +
        "不能导入 Revit 文件本身，也不提供整体合规或可施工结论。",
      statusWithWorkspace:
        "当前提供：启动服务器时指定的工作区里一次已经跑完的真实检查、模拟示例，" +
        "以及对自己 IFC4 文件的一项有限产品验证练习；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。",
      statusWorkspaceUnknown:
        "未能确认服务器是否指定了工作区，所以这里没有工作区检查的入口；这不等于没有工作区，错误原文在下面。" +
        "模拟示例和本地 IFC 产品验证练习照常可用；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。",
      cannot: [
        "导入 Revit 文件本身（.rvt），或用产品验证练习以外的规则检查自己的模型",
        "给出整体合规、可施工或“可以交付”的结论",
        "写回模型、上传到云端，或在 Revit 里打开构件",
      ],
    },
    start: {
      back: "← 返回首页",
      title: "检查自己的 IFC 模型",
      lede: "四步：先看清这次只检查什么和本机会留下的记录；选择文件；声明专业并确认规则；看清范围后运行。",
      unavailable: "本地检查现在不能用：",
      noRuleset:
        "这个检出没有提供 product-validation 1.0 规则集，所以本地检查不能运行。其他规则集不在本地检查里提供。",
    },
    exercise: {
      heading: "这次只检查什么",
      what:
        "这是一项产品验证练习：只用本仓库的产品验证规则集检查一件事——IFC4 模型里适用的风口（IfcAirTerminal）" +
        "是否声明了 DIFFUSER、GRILLE、LOUVRE、REGISTER 四种预定义类型之一。" +
        "它不是通用 BIM 质量检查、IFC 合规检查，也不是任何项目的交付要求。",
      sourceHeading: "要求从哪里来",
      source:
        "本仓库自己写的产品验证规则，不是项目、业主、法规或 buildingSMART 的要求；四个取值来自 IFC4 ADD2 TC1 的 " +
        "IfcAirTerminalTypeEnum，只接受这四个是这条规则自己的决定。规则集的说明原文（英文）：",
      readHeading: "结果怎么读",
      read: [
        "不通过（FAIL）：不满足这条练习规则，不等于你的模型有交付缺陷。",
        "通过（PASS）：只说明检查器读到的值是四个之一；不证明分类正确、洞口存在、模型已对齐，也不说明任何工作可以开始。",
        "所选模型里没有风口：显示“没有适用对象”。这不是通过，此次也没有得到任何适用检查的通过结果。",
      ],
      notes: "检查器从类型还是实例读取取值、自由文本怎样比较，写在结果页这条规则的说明里。",
    },
    records: {
      heading: "本机会留下哪些记录",
      lede: "检查在这台电脑上运行，不上传到任何地方。下面这个目录保存所有记录，运行前就定好：",
      named: "目录",
      onDisk: "资源管理器里的实际位置",
      redirected:
        "服务器运行在打包应用（MSIX）里，Windows 把写到 %LOCALAPPDATA% 下的文件转到了应用自己的文件夹。" +
        "在资源管理器里要找上面这个“实际位置”；按目录名去找会找不到。" +
        "想避免这种转移，用下面的命令在 AppData 以外的文件夹启动服务器。",
      notYet: "目前还没有任何记录：选择第一个文件时才会创建这个目录。",
      kept: "目前保留：{uploads} 个模型副本，{checks} 次检查。",
      whatHeading: "会留下什么",
      what: [
        "你选择的每个文件的副本：uploads\\<内容摘要>.ifc。选择文件时就会保留，即使最后没有运行检查。",
        "每次检查一个目录：checks\\<检查号>\\，里面有模型副本、规则集副本、检查结果（data\\processed\\canonical\\run.json）、" +
          "产物清单、本次检查的范围（check.json）和覆盖记录（coverage\\）。",
        "3D 几何缓存：现在不生成。以后加入 3D 查看时，它的缓存也放在这个目录里，按下面同样的步骤清理。",
        "这个目录以外不写任何文件：仓库检出不变，命令行 epc-ct run 使用的共享覆盖记录目录也不增加。",
        "关闭页面或停止服务器都不会删除记录。",
      ],
      cleanHeading: "怎样清理",
      clean: [
        "停止服务器：在运行它的终端里按 Ctrl+C。",
        "在资源管理器里打开上面的位置（实际位置与目录名不同时，用实际位置）。",
        "删除整个目录，就清除了全部记录；只想删一次检查，删除 checks\\<检查号>\\。" +
          "它用过的模型副本在 uploads\\ 里，按内容摘要命名；摘要写在检查结果页的追溯信息里。",
      ],
      afterHeading: "清理之后不能再依赖什么",
      after: [
        "已删除检查的结果页链接打不开，页面会说没有这次检查。",
        "不能再拿它和以后的检查对比。",
        "它的覆盖记录一起删除，之后无法再说明那次检查覆盖了哪些构件和要求。",
        "删除模型副本后，要再检查就得重新选择文件。",
      ],
      again:
        "用同一个文件、同样声明的专业、同一规则集版本和同一逻辑日期重新检查，会得到同一个检查号和逐字节相同的结果。",
      startHeading: "怎样把记录放在别的文件夹",
      start: "在仓库目录里，用自己的终端启动服务器，并指定 AppData 以外的文件夹，例如：",
      command: 'python doctor/serve.py --checks-dir "%USERPROFILE%\\Documents\\BIM Doctor checks"',
      startNote:
        "服务器启动时会打印目录。第一次选择文件后目录才存在；如果 Windows 把它放到了别处，这一页会显示实际位置。",
    },
    choose: {
      heading: "1. 选择 IFC 文件",
      label: "选择一个或多个 .ifc 文件",
      note:
        "只接受 IFC-SPF 文本（.ifc），不接受 .ifczip、.ifcxml 或 Revit 文件；单个文件最大 {max}。" +
        "规则集只读取 IFC4，IFC2x3 文件会被拒绝，并告诉你怎样重新导出。",
      copying: "正在复制 {file}……",
      chosenHeading: "已选择的文件",
      none: "还没有选择文件。",
      remove: "不检查这个文件",
      removed:
        "已从本次选择中去掉；它的副本仍在 uploads\\ 里，按上面的清理步骤删除。",
      columns: {
        file: "文件",
        size: "大小",
        schema: "IFC 版本（文件头）",
        discipline: "你声明的专业",
        remove: "不检查",
      },
      size: "{mb} MB",
      sizeGb: "{gb} GB",
      sizeKb: "{kb} KB",
      refusedHeading: "这个文件没有被接受：{file}",
    },
    declare: {
      heading: "2. 声明专业并确认规则集",
      rulesetLegend: "规则集（本地检查只提供这一个）",
      ruleset: "{id} {version}：{title}",
      disciplineLabel: "{file} 的专业",
      choose: "请选择",
      disciplineNote:
        "专业由你声明，不从文件名猜测，写进本次检查的记录。它目前不缩小检查范围：" +
        "规则会检查所选文件里的全部风口，不论声明的是哪个专业（规则自己声明适用于 {scope} 模型）。",
      plan: "查看检查范围",
      planning: "正在确定范围……",
    },
    scope: {
      heading: "3. 运行前确认范围",
      ready: "服务器按下面的范围运行这次检查；确认后再运行。",
      checkId: "检查号（由规则集、逻辑日期和每个文件的名称、专业、内容决定）",
      ruleset: "规则集",
      digest: "规则集摘要（规范化）",
      requirement: "要求",
      citation: "出处（规则原文，英文）",
      models: "模型",
      modelColumns: {
        file: "文件",
        code: "模型代码",
        discipline: "你声明的专业",
        schema: "IFC 版本",
        size: "大小",
        digest: "内容摘要",
      },
      asOf: "逻辑日期",
      asOfNote: "（运行配置给定，不是今天的日期）",
      // The fold for what only tracing needs (PM U4): ids, digests, run fields.
      trace: "追溯信息：检查号、摘要与运行字段",
      programme: "进度计划",
      programmeText:
        "你的模型不带进度计划。规则集的规则写了阶段 {stages}，所以本次检查代填了这些阶段，没有到期日；" +
        "结果页不显示到期、逾期或优先级。",
      geometry: "几何",
      geometryText:
        "不计算几何。没有形体的构件不会让整次检查中断，它的检查结果、标识和下一步照常显示；本次结果也没有 3D 视图。",
      location: "结果保存在",
      run: "运行检查",
      running: "正在检查，可能需要几十秒到几分钟。完成后会打开结果。",
      changed: "选择或声明有变化，请重新查看检查范围。",
    },
    refusal: {
      heading: "这次检查不能开始",
      lede: "没有运行任何检查，也没有产生结果。每个原因和要做的事：",
      original: "系统返回的原文（英文）",
      unglossed: "本界面没有为这个原因写说明，请看下面的原文。",
      reasons: {
        busy: "另一次检查正在运行，一次只运行一个。等它完成后再运行这一次。",
        "no-model": "还没有选择文件。至少选择一个 .ifc 文件。",
        "model-too-large":
          "文件超过这台服务器接受的上限，没有读取。可以导出范围更小的模型，或用更大的 --max-model-bytes 重新启动服务器。",
        "model-incomplete": "文件没有完整传到服务器，没有保留。请重新选择这个文件。",
        "not-an-ifc":
          "这不是 IFC-SPF 文本文件：开头没有 ISO-10303-21 文件头。请选择 Revit 导出的 .ifc 文件，不是 .ifczip、.ifcxml 或 .rvt。",
        "model-name-invalid":
          "文件名不能用作模型名：要以 .ifc 结尾，不以“.”开头，不含路径或 < > : \" / \\ | ? *。请改名后重新选择。",
        "unknown-model": "服务器上没有这个文件的副本（可能已被清理）。请重新选择这个文件。",
        "duplicate-model": "同一个文件、同名文件或内容相同的文件选了两次。每个模型只选一次。",
        "unknown-ruleset": "本地检查只提供 product-validation 1.0。请选择它。",
        "discipline-not-declared": "还没有声明专业。为这个文件选择一个专业。",
        "unknown-discipline": "声明的专业不在这里的专业列表里。请从列表里选择。",
        "unsupported-schema":
          "规则集的检查程序只读取 IFC4，这个文件不是 IFC4（例如 IFC2x3）。恢复办法：在 Revit 的 IFC 导出对话框里，" +
          "把 IFC 版本选为 IFC4 Reference View，重新导出后选择新文件。原文件不用修改，也不用删除。",
      },
    },
    fault: {
      heading: "检查没有完成",
      lede:
        "这是程序故障，不是对模型的结论。这次检查的目录已经删除，没有留下半份结果；之前选择的模型副本仍在 uploads\\ 里。",
      todoHeading: "可以怎么做",
      todo: [
        "确认文件是从 Revit 导出的 IFC4 文件，再运行一次。",
        "如果同一个文件每次都在这里失败，重新导出后再选择新文件。",
        "把下面的原文发给维护者；原文只描述程序在哪里停下，不说明模型的质量。",
      ],
      original: "故障原文",
      network: "没有收到服务器的回答：服务器可能已经停止。启动服务器后，刷新这一页。",
    },
    earlier: {
      heading: "以前的检查",
      note: "保存在上面的目录里，直到你删除它们。",
      none: "还没有完成的检查。",
      item: "{files} · {ruleset} · 检查号 {id}",
    },
    result: {
      exercise:
        "这是产品验证练习的结果：只检查风口是否声明了四种预定义类型之一。不通过不等于你的模型有交付缺陷；" +
        "通过不证明分类正确、洞口存在、模型已对齐或任何工作可以开始。",
      nothingHeading: "没有适用对象",
      nothing:
        "{file}：这条规则在这个模型里没有适用对象。这不是通过——此次没有得到任何适用检查的通过结果，也不说明模型质量。",
      scopeHeading: "这次检查的范围",
      declared: "{file}（你声明的专业：{discipline}）",
      programme: "进度计划：规则集的阶段 {stages} 由本次检查代填，没有到期日；本页不显示到期、逾期或优先级。",
      recordsHeading: "这次检查的记录在哪里，怎样清理",
      location: "这次检查的目录",
      another: "检查另一个模型",
      missing:
        "没有这次检查：它可能已被清理（目录被删除），或者链接不对。清理之后，结果页链接就打不开了。",
    },
    disciplines: {
      Architecture: "建筑（Architecture）",
      HVAC: "暖通（HVAC）",
      MEP: "机电（MEP）",
      Plumbing: "给排水（Plumbing）",
      Structural: "结构（Structural）",
    },
    listSeparator: "、",
    colon: "：",
  },
  {
    mode: "Local check · product validation exercise",
    home: {
      title: "Check your own IFC model (product validation exercise)",
      body:
        "Choose an IFC4 file you exported and check the predefined type of its air terminals against one product validation rule. " +
        "Before it runs, the page says what is checked, where the requirement comes from, what the result cannot tell you, and what this computer keeps.",
      action: "Start a local check",
      unknown: "Could not tell whether the local check is available. The error as given:",
      status:
        "Available now: simulated examples, and one limited product validation exercise on your own IFC4 files. " +
        "A Revit file itself cannot be imported, and there is no overall compliance or ready-to-build conclusion.",
      statusWithWorkspace:
        "Available now: a real check already run in the workspace named when the server was started, simulated examples, " +
        "and one limited product validation exercise on your own IFC4 files. A Revit file itself cannot be imported, and there is no overall compliance or ready-to-build conclusion.",
      statusWorkspaceUnknown:
        "Could not tell whether the server was started with a workspace, so there is no entry for a workspace check here; that does not mean there is none, and the error is below. " +
        "The simulated examples and the local IFC product validation exercise work as usual. A Revit file itself cannot be imported, and there is no overall compliance or ready-to-build conclusion.",
      cannot: [
        "Import a Revit file itself (.rvt), or check your own model against rules other than the product validation exercise",
        "Give an overall compliance, ready-to-build or \"ready to hand over\" conclusion",
        "Write back to a model, upload to the cloud, or open an element in Revit",
      ],
    },
    start: {
      back: "← Back to the home page",
      title: "Check your own IFC model",
      lede: "Four steps: first see what this checks and what this computer keeps; choose files; declare disciplines and confirm the rule set; look at the scope, then run.",
      unavailable: "The local check cannot be used now:",
      noRuleset:
        "This checkout does not carry the product-validation 1.0 rule set, so the local check cannot run. No other rule set is offered here.",
    },
    exercise: {
      heading: "What this checks, and only this",
      what:
        "This is a product validation exercise. It checks one thing with this repository's product validation rule set: whether each applicable air terminal (IfcAirTerminal) in an IFC4 model " +
        "declares one of the four predefined types DIFFUSER, GRILLE, LOUVRE or REGISTER. " +
        "It is not a general BIM quality check, not an IFC compliance check, and not a delivery requirement of any project.",
      sourceHeading: "Where the requirement comes from",
      source:
        "A product validation rule written for this repository; not a project, owner, statutory or buildingSMART requirement. The four values are from IFC4 ADD2 TC1 " +
        "IfcAirTerminalTypeEnum; accepting only these four is this rule's own decision. The rule set's description, as written:",
      readHeading: "How to read the result",
      read: [
        "FAIL: the model does not meet this exercise rule. It does not mean your model has a delivery defect.",
        "PASS: only that the value the checker read is one of the four. It does not prove the classification is right, that openings exist or that models are aligned, and it does not say any work can start.",
        "No air terminal in the chosen model: shown as \"nothing applicable\". That is not a pass, and this check produced no passing result for anything applicable.",
      ],
      notes: "Whether the checker reads the value from the type or the occurrence, and how free text is compared, is in this rule's notes on the result page.",
    },
    records: {
      heading: "What this computer keeps",
      lede: "The check runs on this computer and uploads nothing anywhere. Everything is kept in this directory, fixed before anything runs:",
      named: "Directory",
      onDisk: "Where File Explorer finds it",
      redirected:
        "The server is running inside a packaged (MSIX) app, and Windows has moved what is written under %LOCALAPPDATA% into the app's own folder. " +
        "In File Explorer, look in the location above; the directory name alone will not find it. " +
        "To avoid this, start the server with a folder outside AppData, as in the command below.",
      notYet: "Nothing is kept yet: the directory is created when the first file is chosen.",
      kept: "Kept now: {uploads} model copies, {checks} checks.",
      whatHeading: "What is kept",
      what: [
        "A copy of every file you choose: uploads\\<content digest>.ifc. It is kept as soon as the file is chosen, even if no check is run.",
        "One directory per check: checks\\<check id>\\, holding the model copies, a copy of the rule set, the result (data\\processed\\canonical\\run.json), " +
          "the artifact manifest, the scope of the check (check.json) and the coverage record (coverage\\).",
        "3D geometry cache: none is made now. When a 3D view is added, its cache will be kept in this directory too and cleaned up the same way.",
        "Nothing is written outside this directory: the repository checkout does not change, and the shared coverage record directory used by the epc-ct run command gains nothing.",
        "Closing the page or stopping the server deletes nothing.",
      ],
      cleanHeading: "How to clean up",
      clean: [
        "Stop the server: press Ctrl+C in the terminal running it.",
        "Open the location above in File Explorer (where the location differs from the directory name, use the location).",
        "Delete the whole directory to remove every record; to remove one check, delete checks\\<check id>\\. " +
          "The model copies it used are in uploads\\, named by content digest; the digest is in the trace details on the check's result page.",
      ],
      afterHeading: "What you can no longer rely on after cleaning up",
      after: [
        "A deleted check's result link stops opening; the page says there is no such check.",
        "It can no longer be compared with a later check.",
        "Its coverage record goes with it, so nothing can say afterwards which elements and requirements that check covered.",
        "Once a model copy is deleted, the file has to be chosen again to check it.",
      ],
      again:
        "Checking the same file again, declared as the same discipline, with the same rule set version and the same logical date, gives the same check id and byte-identical results.",
      startHeading: "How to keep the records in another folder",
      start: "From the repository directory, start the server in your own terminal with a folder outside AppData, for example:",
      command: 'python doctor/serve.py --checks-dir "%USERPROFILE%\\Documents\\BIM Doctor checks"',
      startNote:
        "The server prints the directory when it starts. It exists once the first file is chosen; if Windows keeps it somewhere else, this page shows where.",
    },
    choose: {
      heading: "1. Choose IFC files",
      label: "Choose one or more .ifc files",
      note:
        "Only IFC-SPF text (.ifc) is accepted, not .ifczip, .ifcxml or Revit files; at most {max} per file. " +
        "The rule set reads IFC4 only; an IFC2x3 file is refused, with how to export it again.",
      copying: "Copying {file}…",
      chosenHeading: "Chosen files",
      none: "No file chosen yet.",
      remove: "Do not check this file",
      removed:
        "Taken out of this selection; its copy is still in uploads\\. Delete it with the clean-up steps above.",
      columns: {
        file: "File",
        size: "Size",
        schema: "IFC version (file header)",
        discipline: "Discipline you declare",
        remove: "Leave out",
      },
      size: "{mb} MB",
      sizeGb: "{gb} GB",
      sizeKb: "{kb} KB",
      refusedHeading: "This file was not accepted: {file}",
    },
    declare: {
      heading: "2. Declare disciplines and confirm the rule set",
      rulesetLegend: "Rule set (the only one the local check offers)",
      ruleset: "{id} {version}: {title}",
      disciplineLabel: "Discipline of {file}",
      choose: "Choose",
      disciplineNote:
        "You declare the discipline; it is not guessed from the file name, and it is written into the check's record. It does not narrow the check now: " +
        "the rule checks every air terminal in the chosen files, whichever discipline is declared (the rule itself declares it applies to {scope} models).",
      plan: "See the scope of the check",
      planning: "Working out the scope…",
    },
    scope: {
      heading: "3. Confirm the scope before running",
      ready: "The server will run this check with the scope below; confirm it, then run.",
      checkId: "Check id (decided by the rule set, the logical date, and each file's name, discipline and content)",
      ruleset: "Rule set",
      digest: "Rule set digest (normalized)",
      requirement: "Requirement",
      citation: "Citation (the rule's own words)",
      models: "Models",
      modelColumns: {
        file: "File",
        code: "Model code",
        discipline: "Discipline you declare",
        schema: "IFC version",
        size: "Size",
        digest: "Content digest",
      },
      asOf: "Logical date",
      asOfNote: "(set by the run configuration, not today's date)",
      trace: "Tracing: check number, digests and run fields",
      programme: "Programme",
      programmeText:
        "Your model brings no programme. The rule set's rules name the stages {stages}, so this check fills those stages in, with no due date; " +
        "the result page shows no due date, overdue state or priority.",
      geometry: "Geometry",
      geometryText:
        "No geometry is computed. An element without a shape does not stop the check from finishing; its check result, identity and next step are shown as usual. There is no 3D view of this result.",
      location: "Results kept in",
      run: "Run the check",
      running: "Checking. This may take from tens of seconds to a few minutes; the result opens when it is done.",
      changed: "The selection or a declaration changed. See the scope of the check again.",
    },
    refusal: {
      heading: "This check cannot start",
      lede: "No check was run and there is no result. Each reason, and what to do:",
      original: "What the system returned (English original)",
      unglossed: "This interface has no note for this reason; see the original below.",
      reasons: {
        busy: "Another check is running; one runs at a time. Wait for it to finish, then run this one.",
        "no-model": "No file has been chosen. Choose at least one .ifc file.",
        "model-too-large":
          "The file is over this server's limit and was not read. Export a smaller model, or restart the server with a larger --max-model-bytes.",
        "model-incomplete": "The file did not reach the server in full and was not kept. Choose the file again.",
        "not-an-ifc":
          "This is not an IFC-SPF text file: it does not begin with an ISO-10303-21 header. Choose the .ifc file Revit exported, not an .ifczip, .ifcxml or .rvt.",
        "model-name-invalid":
          "The file name cannot name a model: it must end in .ifc, not start with \".\", and have no path or any of < > : \" / \\ | ? *. Rename it and choose it again.",
        "unknown-model": "The server holds no copy of this file (it may have been cleaned up). Choose the file again.",
        "duplicate-model": "The same file, a file of the same name, or one with the same content was chosen twice. Choose each model once.",
        "unknown-ruleset": "The local check offers product-validation 1.0 only. Choose it.",
        "discipline-not-declared": "No discipline is declared. Choose one for this file.",
        "unknown-discipline": "The declared discipline is not in the list here. Choose one from the list.",
        "unsupported-schema":
          "The rule set's checker reads IFC4 only, and this file is not IFC4 (IFC2x3, for example). To recover: in Revit's IFC export dialog, " +
          "set the IFC version to IFC4 Reference View, export again and choose the new file. The original file needs no change and need not be deleted.",
      },
    },
    fault: {
      heading: "The check did not finish",
      lede:
        "This is a fault of the program, not a conclusion about the model. The check's directory has been removed and no partial result is left; the model copies chosen before are still in uploads\\.",
      todoHeading: "What you can do",
      todo: [
        "Make sure the file is an IFC4 file exported from Revit, and run again.",
        "If the same file fails here every time, export it again and choose the new file.",
        "Send the original text below to the maintainer; it only says where the program stopped, not anything about the model's quality.",
      ],
      original: "The fault as given",
      network: "No answer came from the server: it may have stopped. Start the server, then reload this page.",
    },
    earlier: {
      heading: "Earlier checks",
      note: "Kept in the directory above until you delete them.",
      none: "No finished check yet.",
      item: "{files} · {ruleset} · check {id}",
    },
    result: {
      exercise:
        "This is the result of a product validation exercise: it only checks whether air terminals declare one of four predefined types. A FAIL does not mean your model has a delivery defect; " +
        "a PASS does not prove the classification is right, that openings exist, that models are aligned or that any work can start.",
      nothingHeading: "Nothing applicable",
      nothing:
        "{file}: this rule has nothing to apply to in this model. That is not a pass — this check produced no passing result for anything applicable, and it says nothing about the model's quality.",
      scopeHeading: "The scope of this check",
      declared: "{file} (discipline you declared: {discipline})",
      programme: "Programme: the rule set's stages {stages} were filled in by this check, with no due date; this page shows no due date, overdue state or priority.",
      recordsHeading: "Where this check's records are, and how to clean up",
      location: "This check's directory",
      another: "Check another model",
      missing:
        "There is no such check: it may have been cleaned up (its directory deleted), or the link is wrong. After cleaning up, result links stop opening.",
    },
    disciplines: {
      Architecture: "Architecture",
      HVAC: "HVAC",
      MEP: "MEP",
      Plumbing: "Plumbing",
      Structural: "Structural",
    },
    listSeparator: ", ",
    colon: ": ",
  },
);
