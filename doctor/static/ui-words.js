// Navigation/layout wording only. Domain wording stays in its existing tables.
import { bilingual } from "./i18n.js";

export const UI = bilingual("WORKSPACE_UI", {
  examples: "模拟示例", local: "本地 IFC 检查", navigation: "主要路径",
  preview: "内部预览", results: "定位到结果列表", back: "返回结果列表",
  clear: "清空搜索", input: "输入模型", models: "模型版本与记录",
  notDefects: "同一个构件可以出现在几个事项里，所以事项数不是缺陷数。",
  outside: "当前选中项不在筛选结果中；详情保持可读。",
  name: "名称", basis: "依据",
}, {
  examples: "Simulated examples", local: "Local IFC check", navigation: "Main paths",
  preview: "Internal preview", results: "Go to the results list", back: "Back to results",
  clear: "Clear search", input: "Input model", models: "Model versions and record",
  notDefects: "The same element can appear in several items, so the number of items is not a number of defects.",
  outside: "The selected item is outside this filter. Its detail remains visible.",
  name: "Name", basis: "Basis",
});
