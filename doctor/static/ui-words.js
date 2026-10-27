// Navigation/layout wording only. Domain wording stays in its existing tables.
import { bilingual } from "./i18n.js";

export const UI = bilingual("WORKSPACE_UI", {
  startTitle: "按项目开展用途审查", startBody: "建立项目，采用企业规则，保存模型修订，再按实际用途定位阻碍与复检变化。", startAction: "打开项目", workflow: "项目 → 企业规则 → 模型 → 用途审查", legacy: "历史记录与独立检查", legacyBody: "原有示例和检查记录保留在这里；项目规则与用途审查从上方项目入口开始。", currentScope: "当前支持 IFC 几何、企业规则 ZIP、模型修订与用途证据复检。源模型修改后重新导出 IFC；本工具不写回 Revit，也不提供整体合规或施工许可。",
  projects: "项目与复查",
  review: "3D 检查工作台",
  reviewAction: "打开 3D 检查工作台", reviewBody: "载入真实公共示例或自己的 IFC，在模型中定位问题，并查看有证据的处理建议。",
  examples: "模拟示例", local: "本地 IFC 检查", navigation: "主要路径",
  preview: "内部预览", results: "定位到结果列表", back: "返回结果列表",
  clear: "清空搜索", input: "输入模型", models: "模型版本与记录",
  notDefects: "同一个构件可以出现在几个事项里，所以事项数不是缺陷数。",
  outside: "当前选中项不在筛选结果中；详情保持可读。",
  name: "名称", basis: "依据",
}, {
  startTitle: "Review model purposes in a project", startBody: "Create a project, adopt your rules, save a model revision, then locate blockers and recheck changes for its intended purpose.", startAction: "Open projects", workflow: "Project → Enterprise rules → Model → Purpose review", legacy: "Historical records & standalone checks", legacyBody: "Earlier examples and check records remain available here. Start project rules and purpose reviews from the project entry above.", currentScope: "Supports IFC geometry, enterprise rule ZIPs, model revisions and purpose-evidence rechecks. Edit the source model and re-export IFC; this tool does not write back to Revit or grant overall compliance or construction approval.",
  projects: "Projects & rechecks",
  review: "3D review workspace",
  reviewAction: "Open 3D review workspace", reviewBody: "Load the real public example or your own IFC, locate issues in the model, and read evidence-based next steps.",
  examples: "Simulated examples", local: "Local IFC check", navigation: "Main paths",
  preview: "Internal preview", results: "Go to the results list", back: "Back to results",
  clear: "Clear search", input: "Input model", models: "Model versions and record",
  notDefects: "The same element can appear in several items, so the number of items is not a number of defects.",
  outside: "The selected item is outside this filter. Its detail remains visible.",
  name: "Name", basis: "Basis",
});
