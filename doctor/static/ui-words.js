// Navigation/layout wording only. Domain wording stays in its existing tables.
import { bilingual } from "./i18n.js";

export const UI = bilingual("WORKSPACE_UI", {
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
