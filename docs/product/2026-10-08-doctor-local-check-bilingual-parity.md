# Doctor 本地 IFC 检查：中英义务对照（#29）

日期：2026-10-08。负责：Framework Engineer。分支 `feat/doctor-local-ifc-check`，审计对象为本文件随附的提交。
依据：技术总监对 #29 第二轮（`8378c63`）的审计，第 1 项；格式参照 [行动义务对照](2026-10-04-doctor-bilingual-action-parity.md)。
状态：下列中英文句子**全部未经 BIM 复核**，进 10/15 批次；本文件由界面实际注册的词表生成（`doctor/static/local-words.js`，
`bilingual("LOCAL_CHECK", …)`），中文、英文两列就是页面上的字。

## 结论

`LOCAL_CHECK` 共 146 条：有领域含义的 76 条逐条列在第一至九节；其余 70 条是界面用语（标题、按钮、列名、
大小单位、分隔符），列在第十一节。

- 有领域含义的 76 条中，**改前有 2 条义务不同或不完整，本轮已改**：`scope.geometryText`（英文可读成“构件不会 FAIL”）、
  `records.again`（两种语言都漏了“声明的专业”也决定检查号）。改后全部为同一义务。
- 2 条（`scope.programmeText`、`result.programme`）义务相同，英文语法别扭，按技术总监的安排记为后续。
- 第十节另列本轮修改的 6 条中央词表句子（随附项目目录页与首页），两种语言同改。

“同一义务”的判断标准：两种语言要求读者做的事、承诺或否认的事、限定的范围相同；措辞、语序、标点不同不算。

## 一、范围说明（这次只检查什么、要求从哪里来、规则集只提供哪一个）

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `mode` | 本地检查 · 产品验证练习 | Local check · product validation exercise | 同一义务 |
| `home.title` | 检查自己的 IFC 模型（产品验证练习） | Check your own IFC model (product validation exercise) | 同一义务 |
| `home.body` | 选择自己导出的 IFC4 文件，只用一条产品验证规则检查风口的预定义类型。运行前会说明检查什么、要求从哪里来、结果不能说明什么，以及本机会留下哪些记录。 | Choose an IFC4 file you exported and check the predefined type of its air terminals against one product validation rule. Before it runs, the page says what is checked, where the requirement comes from, what the result cannot tell you, and what this computer keeps. | 同一义务 |
| `home.status` | 当前提供模拟示例，以及对自己 IFC4 文件的一项有限产品验证练习；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。 | Available now: simulated examples, and one limited product validation exercise on your own IFC4 files. A Revit file itself cannot be imported, and there is no overall compliance or ready-to-build conclusion. | 同一义务；首页在服务器提供本地检查时用这句代替中央 `HOME.status` |
| `home.statusWithWorkspace` | 当前提供：启动服务器时指定的工作区里一次已经跑完的真实检查、模拟示例，以及对自己 IFC4 文件的一项有限产品验证练习；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。 | Available now: a real check already run in the workspace named when the server was started, simulated examples, and one limited product validation exercise on your own IFC4 files. A Revit file itself cannot be imported, and there is no overall compliance or ready-to-build conclusion. | 同一义务 |
| `home.statusWorkspaceUnknown` | 未能确认服务器是否指定了工作区，所以这里没有工作区检查的入口；这不等于没有工作区，错误原文在下面。模拟示例和本地 IFC 产品验证练习照常可用；不能导入 Revit 文件本身，也不提供整体合规或可施工结论。 | Could not tell whether the server was started with a workspace, so there is no entry for a workspace check here; that does not mean there is none, and the error is below. The simulated examples and the local IFC product validation exercise work as usual. A Revit file itself cannot be imported, and there is no overall compliance or ready-to-build conclusion. | 同一义务；“这不等于没有工作区”保留 |
| `home.cannot[0]` | 导入 Revit 文件本身（.rvt），或用产品验证练习以外的规则检查自己的模型 | Import a Revit file itself (.rvt), or check your own model against rules other than the product validation exercise | 同一义务；Revit 文件本身仍不能导入 |
| `home.cannot[1]` | 给出整体合规、可施工或“可以交付”的结论 | Give an overall compliance, ready-to-build or "can be handed over" conclusion | 同一义务 |
| `home.cannot[2]` | 写回模型、上传到云端，或在 Revit 里打开构件 | Write back to a model, upload to the cloud, or open an element in Revit | 同一义务 |
| `start.lede` | 四步：先看清这次只检查什么和本机会留下的记录；选择文件；声明专业并确认规则；看清范围后运行。 | Four steps: first see what this checks and what this computer keeps; choose files; declare disciplines and confirm the rule set; look at the scope, then run. | 同一义务 |
| `start.noRuleset` | 这个检出没有提供 product-validation 1.0 规则集，所以本地检查不能运行。其他规则集不在本地检查里提供。 | This checkout does not carry the product-validation 1.0 rule set, so the local check cannot run. No other rule set is offered here. | 同一义务 |
| `exercise.what` | 这是一项产品验证练习：只用本仓库的产品验证规则集检查一件事——IFC4 模型里适用的风口（IfcAirTerminal）是否声明了 DIFFUSER、GRILLE、LOUVRE、REGISTER 四种预定义类型之一。它不是通用 BIM 质量检查、IFC 合规检查，也不是任何项目的交付要求。 | This is a product validation exercise. It checks one thing with this repository's product validation rule set: whether each applicable air terminal (IfcAirTerminal) in an IFC4 model declares one of the four predefined types DIFFUSER, GRILLE, LOUVRE or REGISTER. It is not a general BIM quality check, not an IFC compliance check, and not a delivery requirement of any project. | 同一义务；范围是 PV-001 一条，PM 10/3 第 1 节 |
| `exercise.source` | 本仓库自己写的产品验证规则，不是项目、业主、法规或 buildingSMART 的要求；四个取值来自 IFC4 ADD2 TC1 的 IfcAirTerminalTypeEnum，只接受这四个是这条规则自己的决定。规则集的说明原文（英文）： | A product validation rule written for this repository; not a project, owner, statutory or buildingSMART requirement. The four values are from IFC4 ADD2 TC1 IfcAirTerminalTypeEnum; accepting only these four is this rule's own decision. The rule set's description, as written: | 同一义务；与 PV-001 的 `citation` 原文一致（原文在“出处”里另行显示） |
| `exercise.notes` | 检查器从类型还是实例读取取值、自由文本怎样比较，写在结果页这条规则的说明里。 | Whether the checker reads the value from the type or the occurrence, and how free text is compared, is in this rule's notes on the result page. | 同一义务；类型／实例读取顺序与自由文本比较只在规则说明（`RULE_NOTES`，C2 已复核）里 |
| `declare.rulesetLegend` | 规则集（本地检查只提供这一个） | Rule set (the only one the local check offers) | 同一义务 |
| `refusal.reasons.unknown-ruleset` | 本地检查只提供 product-validation 1.0。请选择它。 | The local check offers product-validation 1.0 only. Choose it. | 同一义务 |
| `result.exercise` | 这是产品验证练习的结果：只检查风口是否声明了四种预定义类型之一。不通过不等于原项目有缺陷；通过不证明分类正确、洞口存在、模型已对齐或任何工作可以开始。 | This is the result of a product validation exercise: it only checks whether air terminals declare one of four predefined types. A FAIL does not mean the original project has a defect; a PASS does not prove the classification is right, that openings exist, that models are aligned or that any work can start. | 同一义务 |

## 二、结果怎么读（FAIL、PASS 的边界）

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `exercise.read[0]` | 不通过（FAIL）：不满足这条练习规则，不等于原项目有缺陷。 | FAIL: the model does not meet this exercise rule. It does not mean the original project has a defect. | 同一义务；FAIL 不等于原项目缺陷 |
| `exercise.read[1]` | 通过（PASS）：只说明检查器读到的值是四个之一；不证明分类正确、洞口存在、模型已对齐，也不说明任何工作可以开始。 | PASS: only that the value the checker read is one of the four. It does not prove the classification is right, that openings exist or that models are aligned, and it does not say any work can start. | 同一义务；PASS 不证明分类正确、洞口存在、模型对齐、可以开始工作 |
| `fault.lede` | 这是程序故障，不是对模型的结论。这次检查的目录已经删除，没有留下半份结果；之前选择的模型副本仍在 uploads\ 里。 | This is a fault of the program, not a conclusion about the model. The check's directory has been removed and no partial result is left; the model copies chosen before are still in uploads\. | 同一义务；故障不是对模型的结论 |
| `fault.todo[2]` | 把下面的原文发给维护者；原文只描述程序在哪里停下，不说明模型的质量。 | Send the original text below to the maintainer; it only says where the program stopped, not anything about the model's quality. | 同一义务 |

## 三、没有适用对象

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `exercise.read[2]` | 所选模型里没有风口：显示“没有适用对象”。这不是通过，此次也没有得到任何适用检查的通过结果。 | No air terminal in the chosen model: shown as "nothing applicable". That is not a pass, and this check produced no passing result for anything applicable. | 同一义务；不是通过，也没有任何适用检查的通过结果 |
| `result.nothingHeading` | 没有适用对象 | Nothing applicable | 同一义务 |
| `result.nothing` | {file}：这条规则在这个模型里没有适用对象。这不是通过——此次没有得到任何适用检查的通过结果，也不说明模型质量。 | {file}: this rule has nothing to apply to in this model. That is not a pass — this check produced no passing result for anything applicable, and it says nothing about the model's quality. | 同一义务；另说明不代表模型质量 |

## 四、本机记录与清理

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `records.lede` | 检查在这台电脑上运行，不上传到任何地方。下面这个目录保存所有记录，运行前就定好： | The check runs on this computer and uploads nothing anywhere. Everything is kept in this directory, fixed before anything runs: | 同一义务；不上传 |
| `records.redirected` | 服务器运行在打包应用（MSIX）里，Windows 把写到 %LOCALAPPDATA% 下的文件转到了应用自己的文件夹。在资源管理器里要找上面这个“实际位置”；按目录名去找会找不到。想避免这种转移，用下面的命令在 AppData 以外的文件夹启动服务器。 | The server is running inside a packaged (MSIX) app, and Windows has moved what is written under %LOCALAPPDATA% into the app's own folder. In File Explorer, look in the location above; the directory name alone will not find it. To avoid this, start the server with a folder outside AppData, as in the command below. | 同一义务；MSIX 转移为实测（`…\Packages\Claude_…\LocalCache\Local\…`） |
| `records.notYet` | 目前还没有任何记录：选择第一个文件时才会创建这个目录。 | Nothing is kept yet: the directory is created when the first file is chosen. | 同一义务 |
| `records.kept` | 目前保留：{uploads} 个模型副本，{checks} 次检查。 | Kept now: {uploads} model copies, {checks} checks. | 同一义务 |
| `records.what[0]` | 你选择的每个文件的副本：uploads\<内容摘要>.ifc。选择文件时就会保留，即使最后没有运行检查。 | A copy of every file you choose: uploads\<content digest>.ifc. It is kept as soon as the file is chosen, even if no check is run. | 同一义务；选文件即保留，即使不运行 |
| `records.what[1]` | 每次检查一个目录：checks\<检查号>\，里面有模型副本、规则集副本、检查结果（data\processed\canonical\run.json）、产物清单、本次检查的范围（check.json）和覆盖记录（coverage\）。 | One directory per check: checks\<check id>\, holding the model copies, a copy of the rule set, the result (data\processed\canonical\run.json), the artifact manifest, the scope of the check (check.json) and the coverage record (coverage\). | 同一义务 |
| `records.what[3]` | 这个目录以外不写任何文件：仓库检出不变，命令行 epc-ct run 使用的共享覆盖记录目录也不增加。 | Nothing is written outside this directory: the repository checkout does not change, and the shared coverage record directory used by the epc-ct run command gains nothing. | 同一义务；共享 coverage 目录走查前后都是 8 条 |
| `records.what[4]` | 关闭页面或停止服务器都不会删除记录。 | Closing the page or stopping the server deletes nothing. | 同一义务；不承诺关闭页面即删除（PM 10/3 第 2 节） |
| `records.clean[0]` | 停止服务器：在运行它的终端里按 Ctrl+C。 | Stop the server: press Ctrl+C in the terminal running it. | 同一义务 |
| `records.clean[1]` | 在资源管理器里打开上面的位置（实际位置与目录名不同时，用实际位置）。 | Open the location above in File Explorer (where the location differs from the directory name, use the location). | 同一义务 |
| `records.clean[2]` | 删除整个目录，就清除了全部记录；只想删一次检查，删除 checks\<检查号>\。它用过的模型副本在 uploads\ 里，按内容摘要命名；摘要写在检查结果页的追溯信息里。 | Delete the whole directory to remove every record; to remove one check, delete checks\<check id>\. The model copies it used are in uploads\, named by content digest; the digest is in the trace details on the check's result page. | 同一义务 |
| `records.start` | 在仓库目录里，用自己的终端启动服务器，并指定 AppData 以外的文件夹，例如： | From the repository directory, start the server in your own terminal with a folder outside AppData, for example: | 同一义务 |
| `records.startNote` | 服务器启动时会打印目录。第一次选择文件后目录才存在；如果 Windows 把它放到了别处，这一页会显示实际位置。 | The server prints the directory when it starts. It exists once the first file is chosen; if Windows keeps it somewhere else, this page shows where. | 同一义务 |
| `choose.removed` | 已从本次选择中去掉；它的副本仍在 uploads\ 里，按上面的清理步骤删除。 | Taken out of this selection; its copy is still in uploads\. Delete it with the clean-up steps above. | 同一义务；去掉选择不删除副本 |
| `earlier.note` | 保存在上面的目录里，直到你删除它们。 | Kept in the directory above until you delete them. | 同一义务 |
| `result.missing` | 没有这次检查：它可能已被清理（目录被删除），或者链接不对。清理之后，结果页链接就打不开了。 | There is no such check: it may have been cleaned up (its directory deleted), or the link is wrong. After cleaning up, result links stop opening. | 同一义务 |

## 五、清理之后不能再依赖什么

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `records.after[0]` | 已删除检查的结果页链接打不开，页面会说没有这次检查。 | A deleted check's result link stops opening; the page says there is no such check. | 同一义务 |
| `records.after[1]` | 不能再拿它和以后的检查对比。 | It can no longer be compared with a later check. | 同一义务 |
| `records.after[2]` | 它的覆盖记录一起删除，之后无法再说明那次检查覆盖了哪些构件和要求。 | Its coverage record goes with it, so nothing can say afterwards which elements and requirements that check covered. | 同一义务；覆盖记录随检查目录删除 |
| `records.after[3]` | 删除模型副本后，要再检查就得重新选择文件。 | Once a model copy is deleted, the file has to be chosen again to check it. | 同一义务 |
| `records.again` | 用同一个文件、同样声明的专业、同一规则集版本和同一逻辑日期重新检查，会得到同一个检查号和逐字节相同的结果。 | Checking the same file again, declared as the same discipline, with the same rule set version and the same logical date, gives the same check id and byte-identical results. | **改前两种语言一样不完整，本轮已改。** 检查号还取决于声明的专业（`local_check._scope` 的摘要包含每个文件声明的专业），两种语言都补上“同样声明的专业” |

## 六、专业声明不缩小检查范围

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `declare.disciplineNote` | 专业由你声明，不从文件名猜测，写进本次检查的记录。它目前不缩小检查范围：规则会检查所选文件里的全部风口，不论声明的是哪个专业（规则自己声明适用于 {scope} 模型）。 | You declare the discipline; it is not guessed from the file name, and it is written into the check's record. It does not narrow the check now: the rule checks every air terminal in the chosen files, whichever discipline is declared (the rule itself declares it applies to {scope} models). | 同一义务；“不缩小”是实测（声明为建筑的 HVAC 样例仍得到 2 条 FAIL），不是设计；请 BIM 核 |
| `result.declared` | {file}（你声明的专业：{discipline}） | {file} (discipline you declared: {discipline}) | 同一义务 |
| `refusal.reasons.discipline-not-declared` | 还没有声明专业。为这个文件选择一个专业。 | No discipline is declared. Choose one for this file. | 同一义务 |
| `refusal.reasons.unknown-discipline` | 声明的专业不在这里的专业列表里。请从列表里选择。 | The declared discipline is not in the list here. Choose one from the list. | 同一义务 |
| `disciplines.Architecture` | 建筑（Architecture） | Architecture | 同一义务；中文附专业名，英文只用代码 |
| `disciplines.HVAC` | 暖通（HVAC） | HVAC | 同一义务；同上 |
| `disciplines.MEP` | 机电（MEP） | MEP | 同一义务；同上 |
| `disciplines.Plumbing` | 给排水（Plumbing） | Plumbing | 同一义务；同上 |
| `disciplines.Structural` | 结构（Structural） | Structural | 同一义务；同上 |

## 七、IFC2x3 与其他拒绝原因的恢复办法

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `choose.note` | 只接受 IFC-SPF 文本（.ifc），不接受 .ifczip、.ifcxml 或 Revit 文件；单个文件最大 {max}。规则集只读取 IFC4，IFC2x3 文件会被拒绝，并告诉你怎样重新导出。 | Only IFC-SPF text (.ifc) is accepted, not .ifczip, .ifcxml or Revit files; at most {max} per file. The rule set reads IFC4 only; an IFC2x3 file is refused, with how to export it again. | 同一义务 |
| `refusal.lede` | 没有运行任何检查，也没有产生结果。每个原因和要做的事： | No check was run and there is no result. Each reason, and what to do: | 同一义务；拒绝时没有运行、没有结果 |
| `refusal.reasons.unsupported-schema` | 规则集的检查程序只读取 IFC4，这个文件不是 IFC4（例如 IFC2x3）。恢复办法：在 Revit 的 IFC 导出对话框里，把 IFC 版本选为 IFC4 Reference View，重新导出后选择新文件。原文件不用修改，也不用删除。 | The rule set's checker reads IFC4 only, and this file is not IFC4 (IFC2x3, for example). To recover: in Revit's IFC export dialog, set the IFC version to IFC4 Reference View, export again and choose the new file. The original file needs no change and need not be deleted. | 同一义务；恢复办法：Revit IFC 导出对话框选 IFC4 Reference View，重新导出，原文件不动 |
| `refusal.reasons.not-an-ifc` | 这不是 IFC-SPF 文本文件：开头没有 ISO-10303-21 文件头。请选择 Revit 导出的 .ifc 文件，不是 .ifczip、.ifcxml 或 .rvt。 | This is not an IFC-SPF text file: it does not begin with an ISO-10303-21 header. Choose the .ifc file Revit exported, not an .ifczip, .ifcxml or .rvt. | 同一义务 |
| `refusal.reasons.model-too-large` | 文件超过这台服务器接受的上限，没有读取。可以导出范围更小的模型，或用更大的 --max-model-bytes 重新启动服务器。 | The file is over this server's limit and was not read. Export a smaller model, or restart the server with a larger --max-model-bytes. | 同一义务 |
| `refusal.reasons.model-incomplete` | 文件没有完整传到服务器，没有保留。请重新选择这个文件。 | The file did not reach the server in full and was not kept. Choose the file again. | 同一义务 |
| `refusal.reasons.model-name-invalid` | 文件名不能用作模型名：要以 .ifc 结尾，不以“.”开头，不含路径或 < > : " / \ \| ? *。请改名后重新选择。 | The file name cannot name a model: it must end in .ifc, not start with ".", and have no path or any of < > : " / \ \| ? *. Rename it and choose it again. | 同一义务 |
| `refusal.reasons.unknown-model` | 服务器上没有这个文件的副本（可能已被清理）。请重新选择这个文件。 | The server holds no copy of this file (it may have been cleaned up). Choose the file again. | 同一义务 |
| `refusal.reasons.duplicate-model` | 同一个文件、同名文件或内容相同的文件选了两次。每个模型只选一次。 | The same file, a file of the same name, or one with the same content was chosen twice. Choose each model once. | 同一义务 |
| `refusal.reasons.no-model` | 还没有选择文件。至少选择一个 .ifc 文件。 | No file has been chosen. Choose at least one .ifc file. | 同一义务 |
| `refusal.reasons.busy` | 另一次检查正在运行，一次只运行一个。等它完成后再运行这一次。 | Another check is running; one runs at a time. Wait for it to finish, then run this one. | 同一义务 |
| `fault.todo[0]` | 确认文件是从 Revit 导出的 IFC4 文件，再运行一次。 | Make sure the file is an IFC4 file exported from Revit, and run again. | 同一义务 |
| `fault.todo[1]` | 如果同一个文件每次都在这里失败，重新导出后再选择新文件。 | If the same file fails here every time, export it again and choose the new file. | 同一义务 |
| `fault.network` | 没有收到服务器的回答：服务器可能已经停止。启动服务器后，刷新这一页。 | No answer came from the server: it may have stopped. Start the server, then reload this page. | 同一义务 |

## 八、几何与 3D

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `scope.geometryText` | 不计算几何。没有形体的构件不会让整次检查中断，它的检查结果、标识和下一步照常显示；本次结果也没有 3D 视图。 | No geometry is computed. An element without a shape does not stop the check from finishing; its check result, identity and next step are shown as usual. There is no 3D view of this result. | **改前不同，本轮已改。** 改前英文 “does not fail the check” 可读成“这个构件不会得到 FAIL”，中文“不会让检查失败”说的是整次检查不中断；没有形体的构件照样可能 FAIL。两种语言都改成“不会让整次检查中断／does not stop the check from finishing”，并写明照常显示的是“检查结果” |
| `records.what[2]` | 3D 几何缓存：现在不生成。以后加入 3D 查看时，它的缓存也放在这个目录里，按下面同样的步骤清理。 | 3D geometry cache: none is made now. When a 3D view is added, its cache will be kept in this directory too and cleaned up the same way. | 同一义务；“将来的 3D 几何缓存放在同一目录、同样清理”是对 3D 会话的约束，待技术总监确认后转告 |

## 九、范围确认与代填进度（技术总监 10/3 条件：不显示到期、逾期、优先级，并说明进度是代填的）

| 键 | 中文 | English | 义务 |
| --- | --- | --- | --- |
| `scope.ready` | 服务器按下面的范围运行这次检查；确认后再运行。 | The server will run this check with the scope below; confirm it, then run. | 同一义务 |
| `scope.checkId` | 检查号（由规则集、逻辑日期和每个文件的名称、专业、内容决定） | Check id (decided by the rule set, the logical date, and each file's name, discipline and content) | 同一义务 |
| `scope.asOfNote` | （运行配置给定，不是今天的日期） | (set by the run configuration, not today's date) | 同一义务 |
| `scope.programmeText` | 你的模型不带进度计划。规则集的规则写了阶段 {stages}，所以本次检查代填了这些阶段，没有到期日；结果页不显示到期、逾期或优先级。 | Your model brings no programme. The rule set's rules name the stages {stages}, so this check fills those stages in, with no due date; the result page shows no due date, overdue state or priority. | 同一义务。英文 “name the stages Coordination” 语法别扭，技术总监已记为后续，进 BIM 措辞复核，本轮不改 |
| `result.programme` | 进度计划：规则集的阶段 {stages} 由本次检查代填，没有到期日；本页不显示到期、逾期或优先级。 | Programme: the rule set's stages {stages} were filled in by this check, with no due date; this page shows no due date, overdue state or priority. | 同一义务。英文 “name the stages Coordination” 语法别扭，技术总监已记为后续，进 BIM 措辞复核，本轮不改 |
| `scope.running` | 正在检查，可能需要几十秒到几分钟。完成后会打开结果。 | Checking. This may take from tens of seconds to a few minutes; the result opens when it is done. | 同一义务 |

## 十、本轮改的中央词表句子（技术总监第 2 项）

扫描范围：`doctor/static/vocabulary.js` 与 `vocabulary-en.js` 中所有提到导入、上传、选择或更换模型的句子。
改的是在“有本地检查”和“没有本地检查”两种情况下会有一种不成立的绝对说法；改后两种情况都成立。Revit 文件本身仍不能导入，句子保留这一点。
首页在服务器提供本地检查时仍用 `LOCAL_CHECK.home` 的三句状态和“还不能做什么”（第一节），这里改的是没有本地检查时显示的中央句子。
随附项目目录页那句指向首页的“检查自己的 IFC 模型”；`doctor/serve.py` 启动的服务器总是提供本地检查，只有测试里不带本地检查的服务器没有这个入口。

| 表.键 | 位置 | 改前（中／英） | 改后中文 | 改后 English | 义务 |
| --- | --- | --- | --- | --- | --- |
| `HOME.status` | 首页状态句（服务器不提供本地检查时显示） | 当前为示例预览：尚不能导入自己的 Revit 模型，也不提供整体合规或可施工结论。 ／ This is an example preview: you cannot import your own Revit model yet, and it gives no overall compliance or ready-to-build conclusion. | 当前为示例预览：Revit 文件本身（.rvt）不能导入，也不提供整体合规或可施工结论。 | This is an example preview: a Revit file itself (.rvt) cannot be imported, and it gives no overall compliance or ready-to-build conclusion. | 同一义务 |
| `HOME.statusWithWorkspace` | 同上，指定了工作区时 | ……页面上不能导入、选择或更换模型，也不提供整体合规或可施工结论。 ／ … You cannot import, choose or change a model on this page, and it gives no overall compliance or ready-to-build conclusion. | 当前同时提供两样：启动服务器时指定的工作区里一次已经跑完的真实检查，以及模拟示例。工作区里的检查不能在页面上选择或更换模型；Revit 文件本身不能导入，也不提供整体合规或可施工结论。 | Two things are offered here: a real check already run in the workspace named when the server was started, and simulated examples. The workspace check cannot have its model chosen or changed on this page; a Revit file itself cannot be imported, and it gives no overall compliance or ready-to-build conclusion. | 同一义务 |
| `HOME.statusWorkspaceUnknown` | 同上，无法确认工作区时 | ……模拟示例照常可看。页面上不能导入、选择或更换模型，也不提供整体合规或可施工结论。 ／ … The simulated examples are available as usual. You cannot import, choose or change a model on this page, and it gives no overall compliance or ready-to-build conclusion. | 未能确认服务器是否指定了工作区，所以这里没有真实检查的入口；这不等于没有工作区，错误原文在下面。模拟示例照常可看。Revit 文件本身不能导入，也不提供整体合规或可施工结论。 | Could not confirm whether the server was started with a workspace, so there is no entry to a real check here; that does not mean there is no workspace — the error is below. The simulated examples are available as usual. A Revit file itself cannot be imported, and it gives no overall compliance or ready-to-build conclusion. | 同一义务 |
| `HOME.attempt.body` | 随附项目入口卡片 | ……这不是导入入口，不能换成自己的模型。 ／ … It is not an import, and you cannot swap in your own model. | 仓库随附一个样例项目。对它的检查尝试没有开始评估；这里说明原因。这个入口不是导入入口：只看这个样例项目，不能换成别的模型。 | The repository comes with a sample project. The check attempt on it did not start an assessment; this explains why. This entry is not an import: it shows only this sample project, and you cannot swap in another model. | 同一义务 |
| `HOME.cannot[0]` | 首页“现在还不能做什么”第一条 | 在页面上导入、选择或更换模型，包括自己的 Revit 或 IFC 模型 ／ Import, choose or change a model on the page, including your own Revit or IFC model | 导入 Revit 文件本身（.rvt），或在示例和工作区入口里选择、更换模型 | Import a Revit file itself (.rvt), or choose or change the model in the example and workspace entries | 同一义务 |
| `DIRECTORY.realNote` | 随附项目目录页 | 仓库随附一个样例项目，下面是对它的一次检查尝试。目前不能选择别的模型，也不能导入自己的模型。 ／ The repository comes with a sample project; below is a check attempt on it. You cannot choose another model yet, nor import your own. | 仓库随附一个样例项目，下面是对它的一次检查尝试。这个入口只看这个样例，不能换成别的模型；检查自己的 IFC4 文件，用首页的“检查自己的 IFC 模型”。Revit 文件本身不能导入。 | The repository comes with a sample project; below is a check attempt on it. This entry shows only that sample and cannot be switched to another model; to check your own IFC4 files, use "Check your own IFC model" on the home page. A Revit file itself cannot be imported. | 同一义务 |

扫过但不改的（在各自页面的语境里两种情况都成立）：

| 表.键 | 中文 | 为什么不改 |
| --- | --- | --- |
| `WORKSPACE_HOME.body` | 页面只查看这次已经跑完的检查，不能在页面上选择或更换模型。 | 说的是工作区入口；工作区确实不能在页面上换模型 |
| `WORKSPACE.directoryNote` | 工作区只能在启动服务器时指定；这里不能选择、上传或更换模型。 | “这里”是工作区目录页 |
| `RECHECK_CANNOT[0]` | 发起新的复检或上传新模型 | 复检页的“不能做什么”；本地检查不发起复检，也不给复检上传模型 |
| 文件头注释（`vocabulary.js` 第 5–7 行） | “nothing can be imported here” | 注释，说的是随附项目入口；不显示 |

测试：`tests/test_doctor_english.py::LocalCheckWordsTests::test_no_table_says_your_own_model_cannot_be_checked`
逐条检查所有已注册词表的两种语言，不再出现“导入自己的／import your own／导入、选择或更换模型”一类说法。

## 十一、界面用语（70 条，没有领域含义，不逐条判断义务）

`home.action`, `home.unknown`, `start.back`, `start.title`, `start.unavailable`, `exercise.heading`, `exercise.sourceHeading`, `exercise.readHeading`, `records.heading`, `records.named`, `records.onDisk`, `records.whatHeading`, `records.cleanHeading`, `records.afterHeading`, `records.startHeading`, `records.command`, `choose.heading`, `choose.label`, `choose.copying`, `choose.chosenHeading`, `choose.none`, `choose.remove`, `choose.columns.file`, `choose.columns.size`, `choose.columns.schema`, `choose.columns.discipline`, `choose.columns.remove`, `choose.size`, `choose.sizeGb`, `choose.sizeKb`, `choose.refusedHeading`, `declare.heading`, `declare.ruleset`, `declare.disciplineLabel`, `declare.choose`, `declare.plan`, `declare.planning`, `scope.heading`, `scope.ruleset`, `scope.digest`, `scope.requirement`, `scope.citation`, `scope.models`, `scope.modelColumns.file`, `scope.modelColumns.code`, `scope.modelColumns.discipline`, `scope.modelColumns.schema`, `scope.modelColumns.size`, `scope.modelColumns.digest`, `scope.asOf`, `scope.programme`, `scope.geometry`, `scope.location`, `scope.run`, `scope.changed`, `refusal.heading`, `refusal.original`, `refusal.unglossed`, `fault.heading`, `fault.todoHeading`, `fault.original`, `earlier.heading`, `earlier.none`, `earlier.item`, `result.scopeHeading`, `result.recordsHeading`, `result.location`, `result.another`, `listSeparator`, `colon`
