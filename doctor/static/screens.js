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
import {
  BASELINE_LIMITATIONS,
  BASELINE_REFUSAL_CODE,
  CITATION_PROVENANCE,
  CONDITION_STATES,
  DEMO_NOTICE,
  DISPOSITIONS,
  EMPTY_STRING,
  MODE_LABELS,
  NOT_CARRIED,
  POLICY_SOURCE_NOTE,
  PROVENANCE_NOTICE,
  RUN_LABELS,
  absence,
  carryOver,
  citationProvenance,
  conditionState,
  disposition,
} from "./vocabulary.js";

const R010_HEADING = "背景引用，不能回答对齐问题";
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
        `这是复检记录（successor.kind = ${document.successor.kind}），承接一条已封存记录。`,
        " ",
        link("查看复检对比", href(state.mode, state.runId, "recheck")),
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

function activity(state, activityIndex) {
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
    document.successor ? h("p", { class: "sub" }, link("复检对比", href(state.mode, state.runId, "recheck"))) : null,
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
            h("td", {}, field(subscope, "ordinal", (ordinal) => `#${ordinal}`)),
            h(
              "td",
              {},
              terminal
                ? h("div", { class: "sub" }, field(terminal, "evidence_requirement_id", code))
                : null,
              evidence,
            ),
            h("td", {}, h("a", { href: locate(state, subscope, activityIndex, memberIndex) }, "查看证据与回源")),
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
// S4 — recheck comparison
// ---------------------------------------------------------------------------

function glossary(title, entries) {
  return h(
    "details",
    { class: "glossary" },
    h("summary", {}, title),
    tableWrap(table(null, ["代码（保留原码）", "给经理的含义"], entries.map(([key, text]) => h("tr", {}, h("td", {}, code(key)), h("td", {}, text))))),
  );
}

function recheck(state) {
  const envelope = state.envelope;
  const document = envelope.record;
  const successor = document.successor;
  const content = h(
    "div",
    {},
    h("p", {}, link("← 记录上下文", href(state.mode, state.runId, "record"))),
    h("h1", {}, "复检对比"),
  );
  if (!successor) {
    content.append(note("尚无可用复检对比：本记录不是复检记录。"));
    return content;
  }
  const comparison = successor.model_version_context_comparison;
  const versionRow = (label, prior, now) =>
    h("tr", {}, h("th", { scope: "row" }, label), h("td", {}, code(prior.model_key), " ", copyable(prior.content_id)), h("td", {}, code(now.model_key), " ", copyable(now.content_id)));
  content.append(
    definitions([
      ["successor.kind", code(successor.kind)],
      ["原记录 assessment digest", copyable(successor.prior_assessment_digest)],
      ["本记录 assessment digest", copyable(envelope.assessment_digest)],
    ]),
    section(
      "模型版本前后",
      tableWrap(
        table(null, ["", "原记录", "本记录"], [
          versionRow("提交模型", comparison.prior_producing, comparison.producing),
          versionRow("接收模型", comparison.prior_consuming, comparison.consuming),
        ]),
      ),
      comparison.is_current
        ? note("is_current = true：两个模型的内容标识都未变化，本次不是模型重发。")
        : note(`is_current = false：发生变化的模型 ${comparison.changed_models.join("，")}。`, "callout"),
    ),
    glossary("成员去向代码说明", Object.entries(DISPOSITIONS)),
    glossary("条件状态代码说明（现有状态没有“整句条件已满足”）", Object.entries(CONDITION_STATES)),
  );

  successor.subscopes.forEach((outcome) => {
    const dispositions = outcome.dispositions.map((item) => {
      const current = [];
      if (carries(item, "current_ordinals")) {
        item.current_ordinals.forEach((ordinal, index) =>
          current.push(
            h(
              "li",
              {},
              `#${ordinal} `,
              field(item, "current_verdicts", (verdicts) => verdict(verdicts[index])),
              " 终点 outcome ",
              field(item, "current_leaf_outcomes", (outcomes) => code(outcomes[index])),
            ),
          ),
        );
      }
      return h(
        "div",
        { class: "disposition" },
        h("div", { class: "member-name" }, memberTitle(state, item.member)),
        memberKeys(item.member),
        h("div", {}, "去向：", field(item, "disposition", (value) => codeWithGloss(value, disposition))),
        h(
          "div",
          {},
          "cause（原文）：",
          field(item, "cause", (text) => h("blockquote", {}, text)),
        ),
        // Beside the Framework's own cause, and keyed on the disposition code
        // alone. It states what this record says on this disposition and names no
        // verdict: "the fix landed" and "the pair stopped being derived" are
        // indistinguishable from a verdict, which is why the disposition
        // vocabulary separates them in the first place.
        //
        // This wording is written for **this Pack's** `pair_source`: the pair
        // comes from a penetration determination, and the openings activity is
        // what an unbuilt opening blocks. A Pack deriving pairs from something
        // else would need its own sentence. Generalising it now was considered
        // and declined by BIM and the technical director — this repository has
        // one Pack, and a sentence abstracted away from the only case it has
        // ever been read against is not more general, only vaguer.
        item.disposition === "pairing-no-longer-derived"
          ? h(
              "strong",
              { class: "caveat" },
              "该对已不再被推导：穿透判定现为“不穿透”（见上方 cause）。" +
                "这不等于开洞已建成，也不等于开洞缺陷已修复。",
            )
          : null,
        current.length
          ? h("div", {}, "Framework 给出的当前子范围：", h("ul", { class: "plain" }, current))
          : h(
              "div",
              { class: "sub" },
              "当前子范围（current_ordinals）：",
              missing(NOT_CARRIED),
              "；界面不另行对应。",
            ),
      );
    });

    const carry = outcome.evidence_carry_over.map((item) =>
      h(
        "tr",
        {},
        h(
          "td",
          {},
          field(item, "citation", copyable),
          h(
            "div",
            { class: "sub" },
            field(item, "citation_kind", code),
            " ",
            // The kind is the record's own; the tag beside it is read off this
            // one citation's own marker, like every other tag on these screens.
            carries(item, "citation_kind") && carries(item, "citation")
              ? provenance(item.citation_kind, item.citation)
              : null,
          ),
        ),
        h("td", {}, field(item, "reason", (value) => codeWithGloss(value, carryOver))),
        h("td", {}, field(item, "carried", (value) => (value ? "是" : "否"))),
        h("td", {}, field(item, "sealed_content_digest", code)),
        h("td", {}, field(item, "current_content_digest", code)),
      ),
    );

    content.append(
      h(
        "article",
        { class: "recheck-outcome" },
        h("h2", {}, `${activityShortName(outcome.activity_ref)} · 原子范围 #${outcome.subscope_ordinal}`),
        definitions([
          ["activity_ref", field(outcome, "activity_ref", code)],
          ["原裁决", field(outcome, "prior_verdict", verdict)],
          ["原 resolution_kind", field(outcome, "prior_resolution_kind", code)],
          [
            "原成员",
            field(outcome, "prior_members", (members) =>
              members.map((item) => h("div", {}, memberTitle(state, item), " ", memberKeys(item))),
            ),
          ],
        ]),
        h(
          "div",
          { class: "recheck-grid" },
          h("section", { class: "block" }, h("h3", {}, "1. 成员去了哪里"), dispositions),
          h(
            "section",
            { class: "block" },
            h("h3", {}, "2. 旧证据是否仍被引用"),
            tableWrap(table(null, ["引用", "原因", "carried", "封存时内容摘要", "本记录内容摘要"], carry)),
          ),
          h(
            "section",
            { class: "block condition" },
            h("h3", {}, "3. 旧复检条件能证明什么"),
            note("这里只说明原复检条件能被证明到什么程度，与当前裁决分开阅读。"),
            definitions([
              [
                "原复检条件（逐字）",
                field(outcome, "prior_recheck_condition", (text) => h("blockquote", {}, text)),
              ],
              [
                "condition_status",
                field(outcome, "condition_status", (value) => codeWithGloss(value, conditionState)),
              ],
              [
                "condition_basis（原文）",
                field(outcome, "condition_basis", (text) => h("blockquote", {}, text)),
              ],
              ["correspondence", field(outcome, "correspondence", code)],
              ["named_outcome", field(outcome, "named_outcome", code)],
              [
                "原叶节点证据要求",
                field(outcome, "prior_leaf_evidence_requirement_id", code),
              ],
            ]),
          ),
        ),
      ),
    );
  });
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
  );
  // Shown only for a real run refused with the baseline code. The condition is
  // the envelope's own mode and code; the project name is never consulted.
  if (envelope.mode === "real" && envelope.refusal.code === BASELINE_REFUSAL_CODE) {
    content.append(
      h(
        "section",
        { class: "block limitations" },
        h("h2", {}, "当前版本的已知限制（说明，不是本次执行日志）"),
        tableWrap(
          table(
            null,
            ["政策环节", "此次真实运行与当前能力"],
            BASELINE_LIMITATIONS.map(([stage, text]) => h("tr", {}, h("th", { scope: "row" }, stage), h("td", {}, text))),
          ),
        ),
        h("p", { class: "callout" }, "处理当前拒绝原因不保证随后可评估；其余限制尚未由本次运行验证。"),
      ),
    );
  } else {
    content.append(note("本次只返回此拒绝原因，未提供其他环节的诊断。"));
  }
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

export const screens = { entry, runs, record, activity, member, recheck, refusal };
