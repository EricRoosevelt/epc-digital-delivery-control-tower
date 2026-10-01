// The screens. Each one selects, names and lays out what the envelope already
// says. None of them decides a verdict, a disposition, a condition state or a
// coverage reading, and none of them joins a successor's dispositions to the
// current partition: where the Framework records no correspondence, there is
// none on screen either.
//
// Two rules run through every screen below:
//
// * a key the envelope does not carry is shown as "记录未携带" — never as an
//   empty cell, a dash, a zero or a blank, and never confused with a key that
//   is carried and empty, which is a value and says something of its own;
// * every citation carries its provenance beside it, decided from that one
//   citation's own fixture marker. One record can mix real validation output
//   with fixture-minted values, so a per-page or per-envelope rule would label
//   some of them wrongly — and labelling a simulation "real" is the one thing
//   this product must never do.

import { clearResults, go, href } from "./app.js";
import {
  code,
  copyable,
  definitions,
  h,
  link,
  missing,
  note,
  provenanceTag,
  section,
  table,
  verdict,
} from "./dom.js";
import { recheckModel } from "./recheck-model.js";
import {
  CARRY_OVER_REASONS,
  CARRY_OVER_STATES,
  CHANGED_ASPECTS,
  CITATION_KINDS,
  CITATION_PROVENANCE,
  CONDITION_STATES,
  DEMO_NOTICE,
  DISPOSITIONS,
  EMPTY_STRING,
  MODE_LABELS,
  NOT_CARRIED,
  POLICY_SOURCE_NOTE,
  PROVENANCE_NOTICE,
  RECHECK_CANNOT,
  RECHECK_LIMITS,
  REFUSAL_SCOPE_NOTE,
  RUN_LABELS,
  UNRECOGNISED,
  absence,
  citationProvenance,
  conditionState,
} from "./vocabulary.js";

const R010_HEADING = "背景引用，不能回答对齐问题";

// The recheck item the manager last opened, so the list can put them back on it.
let lastRecheckItem = null;
const UNIMPLEMENTED_AUTHORISER = "当前未实现（E2），没有授权记录";

// ---------------------------------------------------------------------------
// Omitted keys, and the provenance of one citation
// ---------------------------------------------------------------------------

function carries(object, key) {
  return object !== null && typeof object === "object" && Object.hasOwn(object, key);
}

/** ``render(value)`` when the key is carried, the two absences named otherwise. */
function field(object, key, render) {
  if (!carries(object, key)) return missing(NOT_CARRIED);
  const value = object[key];
  if (value === "") return missing(EMPTY_STRING);
  if (Array.isArray(value) && value.length === 0) return missing("（记录中为空列表）");
  return render(value);
}

/** The provenance of **one** citation, read off that citation's own marker.
 *
 * Whether the label is true is a property of the single citation it sits beside,
 * so the criterion is too: a fixture-minted value is machine-visibly untrue and
 * carries the fixture marker, and everything else does not. The envelope's mode
 * is deliberately not consulted. One record can mix the two — the model-reissue
 * scenario cites six fixture-minted finding keys beside three real ones — and a
 * per-envelope rule would label those six as real validation output.
 *
 * **When the test that pins this goes red**, the answer is to make the label
 * follow the individual citation, never to drop the mixed scenario from the
 * demonstration. A red light there says "one simulated citation on this page is
 * labelled real", not "this scenario should not exist".
 */
function provenance(kind, citation) {
  const entry = citationProvenance(kind, citation);
  return entry === null ? null : provenanceTag(entry);
}

/** One tag per provenance actually found among these citations, with its count.
 *
 * A summary line still decides citation by citation: a reading whose keys are
 * mixed shows both tags with the number each one covers, rather than one label
 * standing for the group.
 */
function provenanceCounts(kind, citations) {
  const counts = new Map();
  for (const citation of citations) {
    const entry = citationProvenance(kind, citation);
    if (entry === null) continue;
    counts.set(entry, (counts.get(entry) ?? 0) + 1);
  }
  return [...counts].map(([entry, count]) => [provenanceTag(entry), ` ×${count} `]);
}

function provenanceLegend() {
  return h(
    "div",
    { class: "legend" },
    h("p", {}, PROVENANCE_NOTICE),
    h(
      "ul",
      { class: "plain" },
      Object.values(CITATION_PROVENANCE).map((entry) =>
        h("li", {}, provenanceTag(entry), " ", entry.long),
      ),
    ),
  );
}

// ---------------------------------------------------------------------------
// Shared pieces
// ---------------------------------------------------------------------------

function modeLabel(mode) {
  return `${MODE_LABELS[mode] || "未识别模式"}（mode = ${mode}）`;
}

// The adapter names its scenarios; an unlisted name is shown as it came.
export function runLabel(runId) {
  return Object.hasOwn(RUN_LABELS, runId) ? RUN_LABELS[runId] : runId;
}

function short(value) {
  return value && value.length > 12 ? `${value.slice(0, 12)}…` : value;
}

export function renderContext(state) {
  const parts = [];
  const mode = state.envelope ? state.envelope.mode : state.mode;
  const bar = h(
    "div",
    { class: "context-bar" },
    h("span", { class: `mode mode-${mode}` }, modeLabel(mode)),
  );
  const record = state.envelope && state.envelope.record;
  if (record) {
    const request = record.request;
    const context = request.model_version_context;
    bar.append(
      h("span", {}, `项目 ${request.project_id}`),
      h(
        "span",
        { title: `${context.producing.content_id} → ${context.consuming.content_id}` },
        `提交 ${context.producing.model_key}@${short(context.producing.content_id)} → 接收 ${context.consuming.model_key}@${short(context.consuming.content_id)}`,
      ),
      h(
        "span",
        {},
        `交接 ${context.handover.from_role} → ${context.handover.to_role} · ${context.handover.milestone}`,
      ),
    );
  } else if (state.envelope && state.envelope.outcome === "refusal") {
    bar.append(h("span", {}, "本次没有评估记录"));
  }
  bar.append(
    h(
      "button",
      {
        type: "button",
        class: "quiet",
        onclick: () => {
          clearResults(null);
          go();
        },
      },
      "返回入口（清空当前结果）",
    ),
  );
  parts.push(bar);
  if (mode === "fixture") {
    parts.push(h("p", { class: "demo-notice", role: "note" }, DEMO_NOTICE));
  }
  return parts;
}

function elementFacts(state, key) {
  const facts = state.envelope.elements[key];
  return facts && typeof facts === "object" ? facts : null;
}

function elementName(state, key) {
  const facts = elementFacts(state, key);
  return facts && facts.name ? facts.name : "名称不可用";
}

function memberTitle(state, member) {
  return member.keys.map((key) => elementName(state, key)).join(" + ");
}

function memberKeys(member) {
  return h(
    "span",
    { class: "keys" },
    member.keys.map((key, index) => [index ? " + " : "", code(key)]),
  );
}

function sameKeys(left, right) {
  return left.length === right.length && left.every((key, index) => key === right[index]);
}

function readingsFor(step, member) {
  return step.readings.filter((reading) => sameKeys(reading.subject.keys, member.keys));
}

function activityShortName(activityRef) {
  const index = activityRef.indexOf("::");
  return index >= 0 ? activityRef.slice(index + 2) : activityRef;
}

function tableWrap(node) {
  return h("div", { class: "table-wrap" }, node);
}

function codeWithGloss(value, lookup) {
  const gloss = lookup(value);
  return h(
    "span",
    {},
    code(value || "（空）"),
    " ",
    h("span", { class: gloss.known ? "gloss" : "gloss unknown" }, gloss.text),
  );
}

function readingEvidence(reading) {
  const items = [h("div", {}, "读数 outcome：", field(reading, "outcome", code))];
  items.push(h("div", {}, "绑定：", field(reading, "binding", code)));
  if (carries(reading, "finding_keys")) {
    items.push(
      h(
        "div",
        {},
        `finding 引用（${reading.finding_keys.length}）：`,
        field(reading, "finding_keys", (keys) =>
          h(
            "ul",
            { class: "plain" },
            keys.map((key) => h("li", {}, copyable(key), " ", provenance("finding", key))),
          ),
        ),
      ),
    );
  }
  if (carries(reading, "cited_determinations")) {
    items.push(
      h(
        "div",
        {},
        `判定引用（${reading.cited_determinations.length}）：`,
        field(reading, "cited_determinations", (cited) =>
          h(
            "ul",
            { class: "plain" },
            cited.map((item) =>
              h(
                "li",
                {},
                field(item, "reference", copyable),
                " ",
                provenance("determination", carries(item, "reference") ? item.reference : null),
                h("div", { class: "sub" }, "内容摘要 ", field(item, "content_digest", code)),
              ),
            ),
          ),
        ),
      ),
    );
  }
  if (carries(reading, "absence")) {
    items.push(
      h("div", {}, "缺失：", field(reading, "absence", (value) => codeWithGloss(value, absence))),
    );
  }
  if (!["finding_keys", "cited_determinations", "absence"].some((key) => carries(reading, key))) {
    items.push(h("div", {}, "引用与缺失说明：", missing(NOT_CARRIED)));
  }
  return items;
}

function locate(state, subscopeMembers, activity, memberIndex) {
  return href(state.mode, state.runId, "member", activity, subscopeMembers.ordinal, memberIndex);
}

// ---------------------------------------------------------------------------
// S0 — entry
// ---------------------------------------------------------------------------

function entry() {
  const card = (mode, title, body) =>
    h(
      "article",
      { class: "entry-card" },
      h("h2", {}, title),
      h("p", {}, body),
      h(
        "button",
        {
          type: "button",
          onclick: () => {
            clearResults(mode);
            go(mode);
          },
        },
        `进入${MODE_LABELS[mode]}`,
      ),
    );
  return h(
    "div",
    {},
    h("h1", {}, "BIM Doctor 预览：交接前检查"),
    note(
      "两种体验严格分开。进入任一体验或切换体验，都会清空当前结果；真实输入被拒绝时不会转成夹具演示。",
    ),
    h(
      "div",
      { class: "entry-grid" },
      card("fixture", "夹具演示 — 模拟政策与判定", DEMO_NOTICE),
      card(
        "real",
        "真实输入 — 保留真实拒绝",
        "按随附项目自身的政策运行。Framework 拒绝时显示实际拒绝，不生成评估记录。",
      ),
    ),
    note("这是内部预览，不是公共接口或发布版本。没有模型写回、云上传或 Revit 插件。"),
  );
}

// ---------------------------------------------------------------------------
// S1 — runs the adapter offers, and the chosen record's context
// ---------------------------------------------------------------------------

function runs(state) {
  const mode = state.mode;
  const container = h("div", {}, h("h1", {}, `${MODE_LABELS[mode]}：选择运行`));
  container.append(
    mode === "real"
      ? note("本切片的真实输入由内部适配器固定为随附项目；尚无模型版本、Pack 与活动的选择目录（F2 未交付）。被拒绝时显示实际拒绝。")
      : note("以下运行由内部适配器提供。政策与判定为模拟，结果只演示已实现的 Framework 行为。"),
  );
  if (!state.runs.length) {
    container.append(note("适配器没有为此模式提供任何运行。", "problem"));
    return container;
  }
  container.append(
    h(
      "ul",
      { class: "run-list" },
      state.runs.map((run) =>
        h(
          "li",
          {},
          h(
            "a",
            { class: "run", href: href(mode, run.run_id) },
            mode === "real" ? `运行：${runLabel(run.run_id)}` : runLabel(run.run_id),
          ),
          " ",
          code(run.run_id),
        ),
      ),
    ),
  );
  return container;
}

function record(state) {
  lastRecheckItem = null;
  const envelope = state.envelope;
  const document = envelope.record;
  const request = document.request;
  const context = request.model_version_context;
  const source = document.provenance;
  const scope = request.assessed_scope;
  const content = h(
    "div",
    {},
    h("h1", {}, `评估记录：${runLabel(state.runId)}`),
    note("确认本记录的“模型版本 × 交接 × Purpose/活动 × 声明范围”，再进入活动与成员。"),
  );
  if (document.successor) {
    content.append(
      h(
        "p",
        { class: "callout" },
        "这是一条复检记录，承接一条已封存的记录。",
        " ",
        link("查看复检结果：什么变了、什么仍未解决、下一步", href(state.mode, state.runId, "recheck")),
      ),
    );
  }
  content.append(
    section(
      "模型版本",
      definitions([
        ["提交模型", h("span", {}, code(context.producing.model_key), " ", copyable(context.producing.content_id))],
        ["接收模型", h("span", {}, code(context.consuming.model_key), " ", copyable(context.consuming.content_id))],
      ]),
      note("版本以内容标识表示，不以文件名当版本。"),
    ),
    section(
      "交接",
      definitions([
        ["交出角色", context.handover.from_role],
        ["接收角色", context.handover.to_role],
        ["里程碑", context.handover.milestone],
        ["声明日期", context.handover.date],
      ]),
    ),
    section(
      "Purpose 与活动",
      definitions([
        ["Purpose Pack", h("span", {}, code(request.pack_id), ` 版本 ${request.pack_version}，schema ${request.pack_schema_version}`)],
        ["方向", code(request.direction_id)],
        ["请求的活动", h("ul", { class: "plain" }, request.activity_ids.map((id) => h("li", {}, code(id))))],
      ]),
    ),
    section(
      "声明范围",
      definitions([
        ["模型", scope.model_keys.length ? scope.model_keys.map((key) => [code(key), " "]) : "（无）"],
        ["构件", scope.element_keys.length ? scope.element_keys.map((key) => [code(key), " "]) : "（无）"],
      ]),
      note("范围由请求显式声明，由 Framework 展开与准入。"),
    ),
    section(
      "来源",
      definitions([
        ["validation run", copyable(source.validation_run_id)],
        ["规则集", `${source.ruleset_id} ${source.ruleset_version}`],
        ["composition digest", copyable(source.composition_digest)],
        ["assessment digest", copyable(envelope.assessment_digest)],
        [
          "引用的里程碑（仅引用，不计算工期）",
          h(
            "ul",
            { class: "plain" },
            Object.entries(source.cited_milestones).map(([name, date]) => h("li", {}, `${name}：${date}`)),
          ),
        ],
        [
          "引用的成本参数名（仅名称，不估算金额）",
          source.cited_cost_parameter_names.length ? source.cited_cost_parameter_names.join("，") : "（无）",
        ],
      ]),
    ),
    section(
      "活动",
      h(
        "ul",
        { class: "plain" },
        document.activities.map((activity, index) =>
          h("li", {}, link(activityShortName(activity.activity_ref), href(state.mode, state.runId, "activity", index)), " ", code(activity.activity_ref)),
        ),
      ),
    ),
  );
  return content;
}

// ---------------------------------------------------------------------------
// S2 — activity workbench
// ---------------------------------------------------------------------------

const filters = new Map();

// `from` is set when the manager arrives from a recheck item: the subscope the
// Framework named for that item, and the item to go back to. It marks rows and
// offers the way back; it changes nothing the workbench says about them.
function activity(state, activityIndex, from = null) {
  lastRecheckItem = null;
  const envelope = state.envelope;
  const document = envelope.record;
  const current = document.activities[activityIndex];
  if (!current) throw new Error("记录中没有这个活动");
  const nav = h(
    "nav",
    { class: "activity-nav", "aria-label": "活动" },
    h(
      "ul",
      {},
      document.activities.map((item, index) =>
        h(
          "li",
          {},
          h(
            "a",
            { href: href(state.mode, state.runId, "activity", index), "aria-current": index === activityIndex ? "page" : null },
            activityShortName(item.activity_ref),
          ),
        ),
      ),
    ),
    h("p", { class: "sub" }, link("← 记录上下文", href(state.mode, state.runId, "record"))),
    document.successor ? h("p", { class: "sub" }, link("复检结果", href(state.mode, state.runId, "recheck"))) : null,
  );

  const body = h("div", { class: "workbench-body" });
  body.append(
    h("h1", {}, `活动：${activityShortName(current.activity_ref)}`),
    definitions([
      ["activity_ref", code(current.activity_ref)],
      ["对象类别", current.subject_classes.map((name) => [code(name), " "])],
    ]),
    note("按记录的活动与子范围顺序逐成员列出。没有总体裁决、准备度评分或“可交付”标记；成员对各有自己的裁决。"),
  );
  if (from) {
    body.append(
      h(
        "p",
        { class: "callout" },
        `从复检事项进入：Framework 把那一项对应到本活动的子范围 #${from.ordinal}，下表中已标出。`,
        " ",
        link(
          "← 返回那一项复检事项",
          href(state.mode, state.runId, "recheck", from.subscopeIndex, from.memberIndex),
        ),
      ),
    );
  }

  if (current.partition_is_empty) {
    body.append(note("本活动无准入成员，因此无裁决。", "callout"));
  } else {
    const key = `${envelope.assessment_digest}/${activityIndex}`;
    const search = h("input", {
      type: "search",
      id: "member-filter",
      value: filters.has(key) ? filters.get(key) : "",
      placeholder: "按名称或 key 筛选成员",
    });
    const rows = [];
    current.subscopes.forEach((subscope) => {
      const terminal = subscope.path[subscope.path.length - 1];
      const marked = from !== null && subscope.ordinal === from.ordinal;
      subscope.members.forEach((member, memberIndex) => {
        const readings = terminal ? readingsFor(terminal, member) : [];
        const evidence = readings.length
          ? readings.map((reading) =>
              h(
                "div",
                {},
                field(reading, "outcome", code),
                carries(reading, "absence")
                  ? [" · ", field(reading, "absence", (value) => codeWithGloss(value, absence))]
                  : null,
                carries(reading, "finding_keys")
                  ? [
                      ` · finding 引用 ${reading.finding_keys.length} `,
                      provenanceCounts("finding", reading.finding_keys),
                    ]
                  : null,
                carries(reading, "cited_determinations")
                  ? [
                      ` · 判定引用 ${reading.cited_determinations.length} `,
                      provenanceCounts(
                        "determination",
                        reading.cited_determinations.map((item) =>
                          carries(item, "reference") ? item.reference : null,
                        ),
                      ),
                    ]
                  : null,
              ),
            )
          : terminal
            ? h("div", {}, "终点节点读数主体不是本成员（grain：", field(terminal, "grain", code), "）")
            : h("div", {}, "路径：", missing(NOT_CARRIED));
        const refinedFrom = carries(member, "refined_from") ? member.refined_from : "";
        const haystack = [memberTitle(state, member), ...member.keys, refinedFrom]
          .join(" ")
          .toLowerCase();
        rows.push(
          h(
            "tr",
            { "data-haystack": haystack },
            h(
              "th",
              { scope: "row" },
              h("div", { class: "member-name" }, memberTitle(state, member)),
              memberKeys(member),
              carries(member, "refined_from")
                ? h(
                    "div",
                    { class: "sub" },
                    "由 ",
                    field(member, "refined_from", (key) =>
                      h("span", {}, code(key), `（${elementName(state, key)}）`),
                    ),
                    " 细化",
                  )
                : null,
            ),
            h(
              "td",
              {},
              field(subscope, "verdict", verdict),
              h(
                "div",
                { class: "sub" },
                "resolution_kind：",
                field(subscope, "resolution_kind", code),
              ),
            ),
            h(
              "td",
              {},
              field(subscope, "ordinal", (ordinal) => `#${ordinal}`),
              marked ? h("div", { class: "sub from-recheck" }, "复检事项对应的子范围") : null,
            ),
            h(
              "td",
              {},
              terminal
                ? h("div", { class: "sub" }, field(terminal, "evidence_requirement_id", code))
                : null,
              evidence,
            ),
            h(
              "td",
              {},
              h(
                "a",
                {
                  href: locate(state, subscope, activityIndex, memberIndex),
                  "data-return-focus": marked && memberIndex === 0 ? true : null,
                },
                "查看证据与回源",
              ),
            ),
          ),
        );
      });
    });
    const count = h("p", { class: "status", role: "status" });
    const applyFilter = () => {
      const needle = search.value.trim().toLowerCase();
      filters.set(key, search.value);
      let shown = 0;
      for (const row of rows) {
        const visible = !needle || row.dataset.haystack.includes(needle);
        row.hidden = !visible;
        if (visible) shown += 1;
      }
      count.textContent = `显示 ${shown} / ${rows.length} 个成员`;
    };
    search.addEventListener("input", applyFilter);
    body.append(
      section(
        "受评成员",
        h("label", { for: "member-filter" }, "筛选成员"),
        search,
        count,
        provenanceLegend(),
        tableWrap(
          table(null, ["成员", "Framework 裁决", "子范围", "证据 / 缺口（终点节点）", "详情"], rows, { class: "members" }),
        ),
      ),
    );
    applyFilter();
  }

  const excluded = current.out_of_subject_class;
  body.append(
    section(
      "本活动排除范围（无裁决）",
      note("这些声明范围内的构件不属于本活动的对象类别，没有裁决、修复角色或通过标记。"),
      excluded.length
        ? tableWrap(
            table(
              null,
              ["名称", "element_key", "IFC 类别", "原因"],
              excluded.map((item) =>
                h(
                  "tr",
                  {},
                  h("td", {}, elementName(state, item.element_key)),
                  h("td", {}, copyable(item.element_key)),
                  h("td", {}, code(item.ifc_class)),
                  h("td", {}, code("out_of_subject_class")),
                ),
              ),
            ),
          )
        : note("本活动没有排除项。"),
    ),
  );

  return h("div", { class: "workbench" }, nav, body);
}

// ---------------------------------------------------------------------------
// S3 — member evidence, impact, roles, source fix, recheck
// ---------------------------------------------------------------------------

function sourceLocation(state, key) {
  const facts = elementFacts(state, key);
  if (!facts) {
    return h("div", { class: "location" }, h("div", { class: "member-name" }, "名称不可用"), copyable(key), note("elements 中没有这个 key 的名称信息。"));
  }
  return h(
    "div",
    { class: "location" },
    h("div", { class: "member-name" }, carries(facts, "name") && facts.name ? facts.name : "名称不可用"),
    definitions([
      ["IFC 类别", field(facts, "ifc_class", code)],
      ["模型", field(facts, "model_key", code)],
      ["GlobalId", field(facts, "global_id", copyable)],
      // A carried empty storey is a value: the element has no storey assignment.
      // A missing key would be a different fact and says so.
      [
        "楼层",
        carries(facts, "storey")
          ? facts.storey === ""
            ? "无楼层归属"
            : facts.storey
          : missing(NOT_CARRIED),
      ],
      ["element_key", copyable(key)],
    ]),
  );
}

function member(state, activityIndex, ordinal, memberIndex) {
  const document = state.envelope.record;
  const current = document.activities[activityIndex];
  const subscope = current && current.subscopes.find((item) => item.ordinal === ordinal);
  const subject = subscope && subscope.members[memberIndex];
  if (!subject) throw new Error("记录中没有这个成员");
  const context = document.request.model_version_context;

  const content = h(
    "div",
    {},
    h("p", {}, link("← 返回活动工作台", href(state.mode, state.runId, "activity", activityIndex))),
    h("h1", {}, memberTitle(state, subject)),
    definitions([
      ["活动", field(current, "activity_ref", code)],
      ["成员", memberKeys(subject)],
      [
        "细化来源",
        field(subject, "refined_from", (key) =>
          h("span", {}, code(key), `（${elementName(state, key)}）`),
        ),
      ],
      ["子范围", `#${subscope.ordinal}（共 ${subscope.members.length} 个成员）`],
      ["Framework 裁决", field(subscope, "verdict", verdict)],
      ["resolution_kind", field(subscope, "resolution_kind", code)],
      ["模型版本", `${context.producing.model_key}@${short(context.producing.content_id)} → ${context.consuming.model_key}@${short(context.consuming.content_id)}`],
    ]),
    provenanceLegend(),
  );

  // Why: the full path, with this member's readings at each node.
  const contextCitations = [];
  const steps = subscope.path.map((step, index) => {
    if (carries(step, "context_citations")) contextCitations.push(...step.context_citations);
    const mine = readingsFor(step, subject);
    const readings = mine.length ? mine : step.readings;
    return h(
      "li",
      { class: "path-step" },
      h(
        "div",
        { class: "step-head" },
        `${index + 1}. `,
        field(step, "node_id", code),
        " · 证据要求 ",
        field(step, "evidence_requirement_id", code),
        " · 观察粒度 ",
        field(step, "grain", code),
      ),
      h("div", {}, "节点 outcome：", field(step, "outcome", code)),
      mine.length
        ? null
        : h(
            "div",
            { class: "sub" },
            "此节点的读数主体不是本成员单独读数（grain：",
            field(step, "grain", code),
            "），以下为该节点记录的读数：",
          ),
      readings.map((reading) =>
        h(
          "div",
          { class: "reading" },
          mine.length ? null : h("div", {}, "读数主体：", memberKeys(reading.subject)),
          readingEvidence(reading),
        ),
      ),
    );
  });
  content.append(
    section(
      "为什么：证据路径",
      h("ol", { class: "path" }, steps),
      note("界面只显示引用与摘要标识；判定原件与 finding 明细未随信封提供（仅有引用，原件未提供）。"),
    ),
  );

  if (contextCitations.length) {
    content.append(
      h(
        "section",
        { class: "block context-citations" },
        h("h2", {}, R010_HEADING),
        note("以下引用是背景，不是本路径任何 outcome 的依据。全文逐字显示。"),
        h("ul", { class: "plain" }, contextCitations.map((text) => h("li", {}, h("blockquote", {}, text)))),
      ),
    );
  }

  content.append(
    section(
      "影响",
      definitions([
        ["resolution_kind", field(subscope, "resolution_kind", code)],
        [
          "后果类型",
          field(subscope, "route", (value) =>
            field(value, "consequence_kinds", (kinds) => kinds.map((kind) => [code(kind), " "])),
          ),
        ],
        [
          "交接里程碑（引用）",
          h(
            "span",
            {},
            `${context.handover.milestone}：`,
            field(document.provenance.cited_milestones, context.handover.milestone, (date) => date),
          ),
        ],
      ]),
      note("只列后果类型与引用的里程碑，不计算工期或金额。"),
    ),
    h(
      "section",
      { class: "block roles" },
      h("h2", {}, "谁应处理：三种角色分行"),
      tableWrap(
        table(
          null,
          ["角色", "记录中的值"],
          [
            h(
              "tr",
              {},
              h("th", { scope: "row" }, "Pack 默认修复角色"),
              h(
                "td",
                {},
                field(subscope, "route", (value) => field(value, "default_role", code)),
              ),
            ),
            h(
              "tr",
              {},
              h("th", { scope: "row" }, "Overlay 记录的映射对象"),
              h(
                "td",
                {},
                field(subscope, "assignment", (value) => [
                  field(value, "assigned_team_or_person", code),
                  h(
                    "div",
                    { class: "sub" },
                    "decision_basis：",
                    field(value, "decision_basis", code),
                  ),
                  // A policy row is not a citation and carries no marker, so the
                  // envelope says nothing about whose decision it was. Stating
                  // that is true of every row; calling it the fixture's would be
                  // the per-envelope inference this page does not make.
                  h("div", { class: "sub" }, POLICY_SOURCE_NOTE),
                ]),
              ),
            ),
            h("tr", {}, h("th", { scope: "row" }, "风险授权人"), h("td", {}, UNIMPLEMENTED_AUTHORISER)),
          ],
        ),
      ),
      note("映射对象是记录中的 Overlay 映射值，不代表已派发；风险授权人不借用前两行或判定签署者。"),
    ),
    section(
      "回源做什么",
      h(
        "p",
        { class: "prose" },
        "next_action：",
        field(subscope, "route", (value) => field(value, "next_action", (text) => text)),
      ),
      h("h3", {}, "源定位"),
      h("div", { class: "locations" }, subject.keys.map((key) => sourceLocation(state, key))),
      note("回 Revit 或持久建模工作流修正，不做临时 IFC 补丁。项目特定 Revit 字段与可靠的源元素映射未提供（F5），因此没有“在 Revit 打开”。"),
    ),
    section(
      "复检需要什么",
      h(
        "p",
        { class: "prose" },
        "recheck_condition：",
        field(subscope, "route", (value) => field(value, "recheck_condition", (text) => text)),
      ),
    ),
  );
  return content;
}

// ---------------------------------------------------------------------------
// S4 — recheck: what changed, what is still open, what to do next
// ---------------------------------------------------------------------------
//
// Two screens over one successor record. The list answers the three questions
// in words and lays the sealed members out as work items, one per member and in
// the record's order; an item opens to its before/after, the sealed condition,
// the old evidence row by row, and whatever the record gives as a next step.
//
// The wording and the tallies come from recheck-model.js. Nothing here decides
// a state, and there is no overall status: a member pair keeps its own line.
//
// Three things stay open on these screens and are never placed inside a
// collapsed block: the fixture notice (in the context bar), the provenance tag
// beside every citation, and the sentences in RECHECK_LIMITS.

function glossary(title, entries) {
  return h(
    "details",
    { class: "glossary" },
    h("summary", {}, title),
    tableWrap(table(null, ["记录里的代码", "本页的说法"], entries.map(([key, text]) => h("tr", {}, h("td", {}, code(key)), h("td", {}, text))))),
  );
}

function limits() {
  return h(
    "section",
    { class: "block limits", "aria-label": "读这一页时请记住" },
    h("h2", {}, "读这一页时请记住"),
    h("ul", {}, RECHECK_LIMITS.map((text) => h("li", {}, text))),
  );
}

/** A code the record carried and this preview has no words for. */
function unrecognised(value) {
  return h("span", { class: "gloss unknown" }, code(String(value)), ` ${UNRECOGNISED}`);
}

function stateBadge(state) {
  if (state.code === null) return missing(NOT_CARRIED);
  if (!state.known) return unrecognised(state.code);
  return h("span", { class: `state state-${state.code}` }, state.label);
}

function tallyLine(entries) {
  return h(
    "ul",
    { class: "tally" },
    entries.map((entry) =>
      h(
        "li",
        {},
        entry.code === null
          ? missing(NOT_CARRIED)
          : entry.known
            ? entry.label
            : unrecognised(entry.code),
        ` × ${entry.count}`,
      ),
    ),
  );
}

// What each state on this page means, said once above the rows that carry it.
// Only the states this record holds; all four are in the code table under the
// evidence details of the list.
function stateLegend(entries) {
  return h(
    "dl",
    { class: "state-legend" },
    entries
      .filter((entry) => entry.known)
      .map((entry) => [
        h("dt", {}, `“${entry.label}”是什么意思`),
        h("dd", {}, `${CARRY_OVER_STATES[entry.code].meaning}${CARRY_OVER_STATES[entry.code].caveat}`),
      ]),
  );
}

function reissueBlock(reissue) {
  return [
    h("p", { class: "headline" }, reissue.headline),
    h("p", {}, reissue.detail),
    tableWrap(
      table(
        null,
        ["交接的哪一侧", "角色（取自本次请求的交接）", "模型", "是否重新发布"],
        reissue.sides.map((side) =>
          h(
            "tr",
            {},
            h("th", { scope: "row" }, side.label),
            h("td", {}, side.role === NOT_CARRIED ? missing(NOT_CARRIED) : side.role),
            h("td", {}, side.now ? field(side.now, "model_key", code) : missing(NOT_CARRIED)),
            h(
              "td",
              {},
              side.reissued === null
                ? "无法识别，见上"
                : side.reissued
                  ? "重新发布了（新版本）"
                  : "没有变（原版本）",
            ),
          ),
        ),
      ),
    ),
    reissue.caveats.length
      ? h("ul", { class: "caveats" }, reissue.caveats.map((text) => h("li", {}, text)))
      : null,
    note(reissue.neutral),
  ];
}

function recheckIntro(state, model) {
  const successor = state.envelope.record.successor;
  const content = h(
    "div",
    {},
    h("p", {}, link("← 记录上下文", href(state.mode, state.runId, "record"))),
  );
  if (model === null) {
    content.append(h("h1", {}, "复检结果"), note("尚无可用复检对比：本记录不是复检记录。"));
    return { content, usable: false };
  }
  if (!model.recognised) {
    content.append(
      h("h1", {}, "复检结果"),
      h(
        "p",
        { class: "problem" },
        "本记录承接了一条已封存记录，但承接类型不是本页认识的复检：successor.kind = ",
        field(successor, "kind", unrecognised),
        "。本页不把它当作复检来呈现。",
      ),
    );
    return { content, usable: false };
  }
  return { content, usable: true };
}

function recheck(state) {
  const envelope = state.envelope;
  const document = envelope.record;
  const model = recheckModel(document);
  const { content, usable } = recheckIntro(state, model);
  if (!usable) return content;
  const successor = document.successor;
  const comparison = successor.model_version_context_comparison;

  content.append(
    h("h1", {}, "复检结果"),
    h("p", { class: "sub" }, runLabel(state.runId)),
    h(
      "p",
      { class: "lede" },
      "这一页回答三件事：这次复检什么变了、什么仍未解决、下一步做什么。先看结论，证据细节可以展开。",
    ),
    h(
      "section",
      { class: "block" },
      h("h2", {}, "一、什么变了"),
      h("h3", {}, "模型"),
      reissueBlock(model.reissue),
      h("h3", {}, `原记录里的成员（${model.items.length} 个），现在的去向`),
      tallyLine(model.dispositionTally),
      h(
        "h3",
        {},
        `原记录引用的旧证据（${model.subscopes.reduce((sum, item) => sum + item.evidence.length, 0)} 条），和本次记录比较的结果`,
      ),
      tallyLine(model.evidenceTally),
      stateLegend(model.evidenceTally),
    ),
    limits(),
  );

  const returning = lastRecheckItem && lastRecheckItem.runId === state.runId ? lastRecheckItem : null;
  lastRecheckItem = null;
  content.append(
    h(
      "section",
      { class: "block" },
      h("h2", {}, "二、什么仍未解决：逐项查看"),
      note(
        "记录里没有“已解决”这个状态。下面每一项写明记录证明到了哪一步；" +
          "每个成员（或成员对）各占一项，不合并成一个总状态，也没有就绪评分。",
      ),
      h(
        "ol",
        { class: "recheck-items" },
        model.items.map((item) => {
          const subscope = model.subscopes[item.subscopeIndex];
          const here =
            returning &&
            returning.subscopeIndex === item.subscopeIndex &&
            returning.memberIndex === item.memberIndex;
          return h(
            "li",
            { class: "recheck-item", id: `item-${item.subscopeIndex}-${item.memberIndex}` },
            h("div", { class: "member-name" }, memberTitle(state, item.entry.member)),
            memberKeys(item.entry.member),
            h(
              "div",
              { class: "sub" },
              "活动 ",
              field(item.outcome, "activity_ref", (ref) => activityShortName(ref)),
              " · 原子范围 ",
              field(item.outcome, "subscope_ordinal", (ordinal) => `#${ordinal}`),
            ),
            definitions([
              ["原裁决", field(item.outcome, "prior_verdict", verdict)],
              [
                "现在",
                item.disposition.code === null
                  ? missing(NOT_CARRIED)
                  : item.disposition.known
                    ? item.disposition.text
                    : unrecognised(item.disposition.code),
              ],
              [
                "当前裁决",
                item.current
                  ? item.current.map((current) =>
                      h("span", {}, `子范围 #${current.ordinal} `, verdict(current.verdict), " "),
                    )
                  : "记录没有给出这一项当前对应的子范围",
              ],
              [
                "原复检条件",
                item.condition.code !== null && !item.condition.known
                  ? unrecognised(item.condition.code)
                  : item.condition.plain,
              ],
              [`旧证据（${subscope.evidence.length} 条）`, tallyLine(subscope.evidenceTally)],
            ]),
            h(
              "a",
              {
                class: "run",
                href: href(state.mode, state.runId, "recheck", item.subscopeIndex, item.memberIndex),
                "data-return-focus": here ? true : null,
              },
              "查看这一项：前后差异、责任信息、下一步",
            ),
          );
        }),
      ),
    ),
    h(
      "section",
      { class: "block" },
      h("h2", {}, "三、下一步做什么"),
      h(
        "p",
        {},
        "逐项进入上面的事项。每一项的页面写明记录给出的下一步；记录没有给出时，页面会直接说没有。",
      ),
      h("h3", {}, "本预览做不了的事"),
      h("ul", {}, RECHECK_CANNOT.map((text) => h("li", {}, text))),
      note("这些动作没有实现，所以页面上没有对应的按钮。"),
    ),
  );

  const versionRow = (side) =>
    h(
      "tr",
      {},
      h("th", { scope: "row" }, `${side.label}模型`),
      h("td", {}, side.prior ? [field(side.prior, "model_key", code), " ", field(side.prior, "content_id", copyable)] : missing(NOT_CARRIED)),
      h("td", {}, side.now ? [field(side.now, "model_key", code), " ", field(side.now, "content_id", copyable)] : missing(NOT_CARRIED)),
    );
  content.append(
    h(
      "details",
      { class: "block evidence-details" },
      h("summary", {}, "证据细节：记录标识、模型版本的内容标识、代码对照"),
      definitions([
        ["successor.kind", field(successor, "kind", code)],
        ["原记录 assessment digest", field(successor, "prior_assessment_digest", copyable)],
        ["本记录 assessment digest", copyable(envelope.assessment_digest)],
        ["is_current", field(comparison, "is_current", (value) => code(String(value)))],
        [
          "changed_models",
          carries(comparison, "changed_models") && comparison.changed_models.length === 0
            ? "（记录中为空列表：没有模型变化）"
            : field(comparison, "changed_models", (keys) => keys.map((key) => [code(key), " "])),
        ],
      ]),
      tableWrap(table(null, ["", "原记录", "本记录"], model.reissue.sides.map(versionRow))),
      note("版本以内容标识表示，不以文件名当版本。哪一侧变了取自记录的 changed_models，本页不比较内容标识。"),
      glossary("成员去向代码", Object.entries(DISPOSITIONS)),
      glossary("原复检条件状态代码（没有“整句条件已满足”）", Object.entries(CONDITION_STATES)),
      glossary(
        "旧证据比较状态代码",
        Object.entries(CARRY_OVER_STATES).map(([key, entry]) => [key, entry.label]),
      ),
      glossary("旧证据比较原因代码", Object.entries(CARRY_OVER_REASONS)),
      glossary("变化方面代码", Object.entries(CHANGED_ASPECTS)),
    ),
  );
  return content;
}

function citationKind(row) {
  return field(row, "citation_kind", (kind) =>
    Object.hasOwn(CITATION_KINDS, kind) ? CITATION_KINDS[kind] : unrecognised(kind),
  );
}

function evidenceCard(item) {
  const row = item.row;
  const kind = carries(row, "citation_kind") ? row.citation_kind : null;
  return h(
    "li",
    { class: "evidence-row" },
    h(
      "p",
      { class: "evidence-head" },
      stateBadge(item.state),
      item.brief ? h("span", { class: "brief" }, ` ${item.brief}`) : null,
    ),
    // The citation and its provenance tag are on the line, never folded away:
    // which of these is simulated is not a detail.
    h(
      "p",
      { class: "citation-line" },
      citationKind(row),
      "：",
      field(row, "citation", copyable),
      " ",
      carries(row, "citation") ? provenance(kind, row.citation) : null,
    ),
    carries(row, "current_citation")
      ? h(
          "p",
          { class: "citation-line" },
          "本次记录引用的对应证据：",
          field(row, "current_citation", copyable),
          " ",
          provenance(kind, row.current_citation),
        )
      : null,
    h(
      "p",
      {},
      item.reason.code === null
        ? ["原因：", missing(NOT_CARRIED)]
        : item.reason.known
          ? item.reason.text
          : ["原因：", unrecognised(item.reason.code)],
    ),
    item.facts.map((text) => h("p", { class: "fact" }, text)),
    item.notes.map((text) => h("p", { class: "caveat" }, text)),
    carries(row, "cause")
      ? h("div", {}, "记录给出的原因（原文）：", field(row, "cause", (text) => h("blockquote", {}, text)))
      : null,
    h(
      "details",
      {},
      h("summary", {}, "证据细节（记录原码与摘要）"),
      definitions([
        ["state", field(row, "state", code)],
        ["reason", field(row, "reason", code)],
        ["key_changed", field(row, "key_changed", code)],
        [
          "changed_aspects",
          field(row, "changed_aspects", (aspects) => aspects.map((aspect) => [code(aspect), " "])),
        ],
        ["封存时内容摘要", field(row, "sealed_content_digest", code)],
        ["本记录内容摘要", field(row, "current_content_digest", code)],
      ]),
    ),
  );
}

function currentSubscopeBlock(state, item, current) {
  const back = [item.subscopeIndex, item.memberIndex];
  if (!current.located) {
    return h(
      "div",
      { class: "current-subscope" },
      h("h3", {}, `当前子范围 #${current.ordinal}`),
      note("记录给出了这个子范围编号，但本记录的活动里找不到它；本页不另行对应。", "problem"),
    );
  }
  const subscope = current.located.subscope;
  return h(
    "div",
    { class: "current-subscope" },
    h("h3", {}, `当前子范围 #${current.ordinal}（Framework 给出的对应）`),
    definitions([
      ["当前裁决", current.verdict === undefined ? missing(NOT_CARRIED) : verdict(current.verdict)],
      [
        "下一步（记录原文）",
        field(subscope, "route", (value) => field(value, "next_action", (text) => h("span", { class: "prose" }, text))),
      ],
      [
        "复检条件（记录原文）",
        field(subscope, "route", (value) =>
          field(value, "recheck_condition", (text) => h("span", { class: "prose" }, text)),
        ),
      ],
      ["Pack 默认修复角色", field(subscope, "route", (value) => field(value, "default_role", code))],
      [
        "Overlay 记录的映射对象",
        field(subscope, "assignment", (value) => [
          field(value, "assigned_team_or_person", code),
          h("div", { class: "sub" }, POLICY_SOURCE_NOTE),
        ]),
      ],
    ]),
    note("映射对象是记录中的 Overlay 映射值，不代表已派发。当前裁决为 READY 时记录不携带下一步和角色。"),
    h(
      "p",
      {},
      link(
        `在活动工作台查看子范围 #${current.ordinal} 的成员与证据`,
        href(state.mode, state.runId, "activity", current.located.activityIndex, "sub", current.ordinal, ...back),
      ),
    ),
  );
}

function recheckItem(state, subscopeIndex, memberIndex) {
  const envelope = state.envelope;
  const model = recheckModel(envelope.record);
  const { content, usable } = recheckIntro(state, model);
  if (!usable) return content;
  const subscope = model.subscopes[subscopeIndex];
  const item = subscope && subscope.items[memberIndex];
  if (!item) throw new Error("复检记录中没有这一项");
  const outcome = item.outcome;
  lastRecheckItem = { runId: state.runId, subscopeIndex, memberIndex };
  const backToList = () => h("p", {}, link("← 返回复检事项列表（回到这一项的位置）", href(state.mode, state.runId, "recheck")));

  content.replaceChildren(
    backToList(),
    h("h1", {}, memberTitle(state, item.entry.member)),
    definitions([
      ["成员", memberKeys(item.entry.member)],
      ["活动", field(outcome, "activity_ref", (ref) => [activityShortName(ref), " ", code(ref)])],
      ["原子范围", field(outcome, "subscope_ordinal", (ordinal) => `#${ordinal}`)],
    ]),
    h(
      "section",
      { class: "block" },
      h("h2", {}, "一、这一项什么变了"),
      definitions([
        [
          "原记录",
          h(
            "span",
            {},
            field(outcome, "prior_verdict", verdict),
            " 原问题类型（记录原码）：",
            field(outcome, "prior_resolution_kind", code),
          ),
        ],
        [
          "现在",
          item.disposition.code === null
            ? missing(NOT_CARRIED)
            : item.disposition.known
              ? h("span", {}, item.disposition.text, " ", h("span", { class: "sub" }, "记录原码 ", code(item.disposition.code)))
              : unrecognised(item.disposition.code),
        ],
        ["模型", model.reissue.headline],
      ]),
      // Keyed on the disposition code alone, beside the Framework's own cause.
      // This wording is written for **this Pack's** `pair_source`: the pair
      // comes from a penetration determination, and the openings activity is
      // what an unbuilt opening blocks. A Pack deriving pairs from something
      // else would need its own sentence. Generalising it was considered and
      // declined by BIM and the technical director: one Pack, one sentence.
      item.disposition.code === "pairing-no-longer-derived"
        ? h(
            "strong",
            { class: "caveat" },
            "这两个构件已不再被配成一对检查：穿透判定现为“不穿透”（见下方记录给出的原因）。" +
              "这不等于开洞已建成，也不等于开洞缺陷已修复。",
          )
        : null,
      h(
        "div",
        {},
        "记录给出的原因（原文）：",
        field(item.entry, "cause", (text) => h("blockquote", {}, text)),
      ),
      item.current
        ? h(
            "div",
            {},
            "Framework 给出的当前子范围：",
            h(
              "ul",
              { class: "plain" },
              item.current.map((current) =>
                h(
                  "li",
                  {},
                  `#${current.ordinal} `,
                  current.verdict === undefined ? missing(NOT_CARRIED) : verdict(current.verdict),
                  " 终点 outcome ",
                  current.leafOutcome === undefined ? missing(NOT_CARRIED) : code(current.leafOutcome),
                ),
              ),
            ),
          )
        : h(
            "div",
            { class: "sub" },
            "当前子范围（current_ordinals）：",
            missing(NOT_CARRIED),
            "；界面不另行对应。",
          ),
    ),
    h(
      "section",
      { class: "block condition" },
      h("h2", {}, "二、什么仍未解决：原复检条件"),
      h(
        "p",
        { class: "headline" },
        item.condition.code !== null && !item.condition.known
          ? unrecognised(item.condition.code)
          : item.condition.plain,
      ),
      note("这里只说明原复检条件被证明到了什么程度，与当前裁决分开读：当前裁决变好，不等于原条件已满足。"),
      h(
        "div",
        {},
        "原复检条件（逐字）：",
        field(outcome, "prior_recheck_condition", (text) => h("blockquote", {}, text)),
      ),
      h(
        "details",
        {},
        h("summary", {}, "证据细节（记录原码与依据原文）"),
        definitions([
          ["condition_status", field(outcome, "condition_status", (value) => codeWithGloss(value, conditionState))],
          ["condition_basis（原文）", field(outcome, "condition_basis", (text) => h("blockquote", {}, text))],
          ["correspondence", field(outcome, "correspondence", code)],
          ["named_outcome", field(outcome, "named_outcome", code)],
          ["原叶节点证据要求", field(outcome, "prior_leaf_evidence_requirement_id", code)],
        ]),
      ),
    ),
    limits(),
    h(
      "section",
      { class: "block" },
      h("h2", {}, `三、旧证据逐条（${subscope.evidence.length} 条）`),
      note(
        `记录按子范围保存旧证据，不按成员拆分：原子范围的 ${outcome.prior_members.length} 个成员共用下面这些行。`,
      ),
      stateLegend(subscope.evidenceTally),
      provenanceLegend(),
      subscope.evidence.length
        ? h("ol", { class: "evidence-rows" }, subscope.evidence.map(evidenceCard))
        : note("原子范围的证据路径没有引用任何证据。"),
    ),
    h(
      "section",
      { class: "block" },
      h("h2", {}, "四、责任信息与下一步"),
      item.disposition.known ? h("p", { class: "headline" }, item.disposition.next) : null,
      item.current
        ? item.current.map((current) => currentSubscopeBlock(state, item, current))
        : note(
            "记录没有给出这一项当前对应的子范围，所以本页没有下一步原文、修复角色或映射对象可以显示。" +
              "原记录里的责任信息也没有随复检记录返回。",
          ),
      definitions([["风险授权人", UNIMPLEMENTED_AUTHORISER]]),
      h("h3", {}, "本预览做不了的事"),
      h("ul", {}, RECHECK_CANNOT.map((text) => h("li", {}, text))),
    ),
    backToList(),
  );
  return content;
}

// ---------------------------------------------------------------------------
// SX — real refusal
// ---------------------------------------------------------------------------

function refusal(state) {
  const envelope = state.envelope;
  const content = h(
    "div",
    { class: "refusal" },
    h("h1", {}, "评估被拒绝 — 本次没有生成评估记录"),
    definitions([
      ["运行", runLabel(state.runId)],
      ["拒绝码", copyable(envelope.refusal.code)],
    ]),
    note("所提交的请求上下文尚未随拒绝返回。"),
    section(
      "Framework 返回的拒绝文本（完整显示一次）",
      h("pre", { class: "refusal-text" }, envelope.refusal.text),
    ),
    note("没有成员裁决、零问题统计或完成百分比；拒绝不是 UNKNOWN，也不是空的成功运行。"),
    // Shown for every refusal, whatever its code. It is the sentence that stops
    // "one gate is cleared" being read as "the next run will succeed", so it
    // cannot live inside a condition that may not hold.
    h("p", { class: "callout" }, REFUSAL_SCOPE_NOTE),
    note("本次只返回此拒绝原因，未提供其他环节的诊断。"),
  );
  // The known-limitations table is **not** rendered here, and its absence is the
  // correct result rather than a gap in this screen.
  //
  // The approved condition is two things: trusted evidence that the request used
  // the shipped baseline policy, *and* a matching refusal code. A refusal
  // envelope carries `mode`, `outcome`, `refusal` and `elements` — no provenance
  // for the policy the request was composed against — so the first half cannot
  // be established. `mode === "real"` says which entry ran, not which project or
  // which policy, and an earlier revision of this screen wrongly treated it as
  // enough. Nothing here sniffs the project name out of `refusal.text` or
  // compares `elements` against the canonical inventory to reconstruct a basis:
  // no evidence is no evidence, and a table of policy limitations shown beside
  // an unrelated project's refusal would be a false statement about it.
  //
  // Recorded as F9 in the D1 design's data-gap table. When an envelope carries
  // that basis, this is where it is read.
  content.append(
    h(
      "p",
      { class: "actions" },
      h("a", { class: "run", href: href(state.mode) }, "修改输入重试：返回运行列表"),
      " ",
      h(
        "button",
        {
          type: "button",
          class: "quiet",
          onclick: () => {
            clearResults(null);
            go();
          },
        },
        "返回入口（清空当前结果）",
      ),
    ),
  );
  return content;
}

export const screens = { entry, runs, record, activity, member, recheck, recheckItem, refusal };
