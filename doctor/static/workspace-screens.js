// The workspace screens: one real check, its comparison with an earlier run,
// and a refused comparison. Kept apart from screens.js because none of them
// reads a record: there is no handover assessment behind a workspace run.
//
// Everything these screens say is in vocabulary.js; the counting and the
// lookups are in workspace-model.js.

import { clearResults, go, href } from "./app.js";
import { plural } from "./i18n.js";
import { code, copyable, definitions, h, link, missing, note, section, table } from "./dom.js";
import {
  carried,
  carries,
  className,
  field,
  named,
  short,
  storeyOf,
  tableWrap,
  unrecognised,
} from "./screens.js";
import {
  CITATION_GLOSSES,
  COMMON,
  CONTEXT,
  ELEMENT_WORDS,
  FINDING_STATUS,
  NOT_CARRIED,
  REASON_GLOSSES,
  TAG_WORDS,
  UNRECOGNISED,
  WORKSPACE,
  WORKSPACE_COMPARE,
  WORKSPACE_REFUSAL,
  WORKSPACE_REFUSAL_REASONS,
} from "./words.js";
import {
  comparisonElement,
  comparisonOf,
  elementOf,
  findingByKey,
  isProductValidation,
  matches,
  modelChanges,
  modelOf,
  quotesFreeText,
  requirementOf,
  ruleNotes,
  statusGroups,
  tagReading,
  transitions,
} from "./workspace-model.js";

// ---------------------------------------------------------------------------
// SW — a workspace's real check, its comparison, and a refused comparison
// ---------------------------------------------------------------------------
//
// One finished validation run, named when the server was started. There is no
// record behind it: no handover assessment was made, so nothing here is a
// verdict, a team, a work consequence or "can start", and the result words are
// the check's own (FINDING_STATUS). Every sentence is in vocabulary.js.
//
// The comparison is the adapter's. These screens count and arrange its pairs,
// its rows only one run has and its changed models (workspace-model.js); they
// never pair two findings themselves, and no word on them says a thing was
// mended. A passing result carries no observed value, and nothing here says
// what value a pass read.

// The list's filter, kept while the manager moves between the list and one
// result, and dropped when a different run is shown.
const workspaceView = { run: null, status: null, query: "" };

function fill(template, values) {
  return Object.entries(values).reduce(
    (text, [key, value]) => text.replaceAll(`{${key}}`, String(value)),
    template,
  );
}

function statusClass(status) {
  return status === "N/A" ? "na" : String(status).toLowerCase();
}

/** A check's result word, shaped by border as well as worded. */
function statusWord(status) {
  if (status === undefined) return missing(NOT_CARRIED);
  return Object.hasOwn(FINDING_STATUS, status)
    ? h("span", { class: `result result-${statusClass(status)}` }, FINDING_STATUS[status])
    : unrecognised(status);
}

function glossedText(text, glosses) {
  return [
    Object.hasOwn(glosses, text) ? h("div", {}, glosses[text]) : null,
    h("div", { class: "sub prose" }, text),
  ];
}

/** A check's reason, glossed by exact match, with a note when it quotes free text. */
function reasonText(text, notes) {
  return [
    glossedText(text, REASON_GLOSSES),
    notes && quotesFreeText(text) ? h("p", { class: "beside" }, notes.reasonFreeText) : null,
  ];
}

function modelName(model) {
  return model === null
    ? missing(NOT_CARRIED)
    : [code(model.model_id), carries(model, "discipline") ? fill(COMMON.aside, { text: model.discipline }) : null];
}

function ruleHeading(run, requirement) {
  if (requirement === null) return missing(WORKSPACE.noRequirement);
  const notes = ruleNotes(run, requirement);
  return [
    field(requirement, "rule_id", code),
    " ",
    notes ? notes.title : field(requirement, "specification_label", (text) => text),
  ];
}

/** What the rule asks, and where it comes from — the latter only as the data says it. */
function requirementBlock(run, requirement) {
  const notes = ruleNotes(run, requirement);
  return h(
    "div",
    { class: "requirement" },
    h("h3", {}, ruleHeading(run, requirement)),
    isProductValidation(requirement)
      ? h("p", { class: "callout" }, WORKSPACE.productValidation)
      : null,
    definitions([
      notes ? [WORKSPACE.rulePredicate, notes.predicate] : null,
      [
        WORKSPACE.ruleOrigin,
        field(requirement, "citation", (text) => glossedText(text, CITATION_GLOSSES)),
      ],
      [
        WORKSPACE.ruleLabels,
        field(requirement, "labels", (labels) => labels.map((label) => [code(label), " "])),
      ],
    ]),
    notes ? null : note(WORKSPACE.noRuleNotes),
  );
}

/** One element in the words its returned fields allow, for a table row. */
/** The columns of a result row, in reading order: what identifies the object
 * first, the long IFC Tag last (it is still searched, shown in full and copied
 * from the detail). `cells[1]` is the name. */
export const RESULT_COLUMNS = ["status", "name", "class", "model", "storey", "tag"];

function workspaceCells(state, finding, element, run) {
  const model = modelOf(run, finding.model_key);
  const tag = tagReading(element, model);
  // Each cell carries its column's name, so a narrow screen can show the row
  // as a card with the names beside the values (doctor.css).
  const cell = (column, ...content) =>
    h("td", { class: `c-${column}`, "data-label": WORKSPACE.columns[column] }, ...content);
  return [
    cell("status", statusWord(carried(finding, "status"))),
    cell(
      "name",
      element === null
        ? WORKSPACE.wholeModel
        : named(element)
          ? element.name
          : missing(ELEMENT_WORDS.unnamed),
    ),
    cell("class", element === null ? missing(NOT_CARRIED) : field(element, "ifc_class", className)),
    cell("model", modelName(model)),
    cell("storey", element === null ? missing(NOT_CARRIED) : storeyOf(element)),
    cell("tag", tag.kind === "tag" ? code(tag.value) : missing(tagAbsence(tag, true))),
  ];
}

/** Why there is no IFC Tag to show, from the returned data's own words for it. */
function tagAbsence(reading, brief = false) {
  if (reading.kind === "model-level") return brief ? TAG_WORDS.short.modelLevel : TAG_WORDS.modelLevel;
  if (reading.kind === "not-carried") return brief ? TAG_WORDS.short.notCarried : TAG_WORDS.sourceNotCarried;
  const words = brief ? TAG_WORDS.short : TAG_WORDS.sources;
  return Object.hasOwn(TAG_WORDS.sources, reading.value)
    ? words[reading.value]
    : `${UNRECOGNISED}${COMMON.colon}${reading.value}`;
}

/** Where to go back to in the authoring tool: the IFC Tag first, then the rest. */
function locateBlock(element, model) {
  const file = model === null ? missing(NOT_CARRIED) : field(model, "filename", code);
  if (element === null) {
    return h(
      "div",
      { class: "location" },
      h("p", {}, TAG_WORDS.modelLevel),
      definitions([
        [WORKSPACE.element.model, modelName(model)],
        [WORKSPACE.element.file, file],
      ]),
    );
  }
  const tag = tagReading(element, model);
  return h(
    "div",
    { class: "location" },
    definitions([
      [
        h("strong", {}, WORKSPACE.columns.tag),
        tag.kind === "tag"
          ? h("span", { class: "tag" }, copyable(tag.value))
          : missing(tagAbsence(tag)),
      ],
      [WORKSPACE.element.name, named(element) ? element.name : missing(ELEMENT_WORDS.unnamed)],
      [WORKSPACE.element.class, field(element, "ifc_class", className)],
      [WORKSPACE.element.storey, storeyOf(element)],
      [WORKSPACE.element.model, modelName(model)],
      [WORKSPACE.element.file, file],
      [WORKSPACE.element.globalId, field(element, "global_id", copyable)],
    ]),
    tag.kind === "tag" ? h("p", { class: "beside" }, TAG_WORDS.note) : null,
    h("p", { class: "beside" }, tag.kind === "tag" ? TAG_WORDS.byIdNotStorey : TAG_WORDS.storeyFromIfc),
    h("p", { class: "sub" }, TAG_WORDS.useGlobalId),
  );
}

/** What a pass proves and does not, beside the pass. Never what value it read. */
function passBlock(finding, notes) {
  return h(
    "div",
    { class: "pass-limits" },
    h("h4", {}, WORKSPACE.passHeading),
    notes
      ? [
          h("p", {}, h("strong", {}, WORKSPACE.passProves), notes.passProves),
          h("p", {}, h("strong", {}, WORKSPACE.passDoesNotProve)),
          h("ul", { class: "caveats" }, notes.passDoesNotProve.map((text) => h("li", {}, text))),
        ]
      : h("p", {}, WORKSPACE.passUnwritten),
    h(
      "p",
      { class: "beside" },
      carries(finding, "actual") && finding.actual !== ""
        ? WORKSPACE.actualHidden
        : WORKSPACE.passNoValue,
    ),
  );
}

/** The adapter's comparison as it places this one result, if it does. */
function findingComparison(state, finding, notes) {
  const comparison = state.envelope.comparison;
  const place = comparisonOf(comparison, finding.finding_key);
  const body =
    place.kind === "pair"
      ? definitions([
          [WORKSPACE_COMPARE.detailPrior, statusWord(place.row.prior.status)],
          [WORKSPACE_COMPARE.detailCurrent, statusWord(place.row.current.status)],
          [
            WORKSPACE_COMPARE.priorReason,
            field(place.row.prior, "reason", (text) => reasonText(text, notes)),
          ],
          [
            WORKSPACE_COMPARE.currentReason,
            field(place.row.current, "reason", (text) => reasonText(text, notes)),
          ],
        ])
      : place.kind === "newly"
        ? [
            h("p", {}, WORKSPACE_COMPARE.detailNewly),
            h("p", { class: "sub" }, WORKSPACE_COMPARE.inPrior[String(place.row.element_in_prior_run)]),
          ]
        : h("p", {}, WORKSPACE_COMPARE.detailNone);
  return h(
    "section",
    { class: "detail-part" },
    h("h3", {}, WORKSPACE_COMPARE.detailHeading),
    body,
    h("p", {}, link(WORKSPACE.compareLink, href(state.mode, state.runId, "compare"))),
  );
}

/** One result, read in the order a manager acts on it. */
function findingPanel(state, finding) {
  const envelope = state.envelope;
  const run = envelope.run;
  const requirement = requirementOf(envelope, finding);
  const notes = ruleNotes(run, requirement);
  const element = elementOf(envelope.elements, finding.element_key);
  const model = modelOf(run, finding.model_key);
  const status = carried(finding, "status");
  const panel = h(
    "div",
    {},
    h("p", { class: "kicker" }, WORKSPACE.detailKicker),
    h(
      "h2",
      { tabindex: "-1", "data-return-focus": true },
      element === null
        ? [WORKSPACE.wholeModel, COMMON.colon, modelName(model)]
        : named(element)
          ? element.name
          : missing(ELEMENT_WORDS.unnamed),
    ),
    h(
      "section",
      { class: "detail-part" },
      h("h3", {}, WORKSPACE.resultHeading),
      h("p", { class: "headline" }, ruleHeading(run, requirement), COMMON.colon, statusWord(status)),
      status === "N/A" ? h("p", { class: "beside" }, WORKSPACE.notApplicable) : null,
      status === "FAIL" && isProductValidation(requirement)
        ? h("p", { class: "beside" }, WORKSPACE.failNotDefect)
        : null,
      status === "PASS" ? passBlock(finding, notes) : null,
    ),
    h(
      "section",
      { class: "detail-part" },
      h("h3", {}, WORKSPACE.findHeading),
      locateBlock(element, model),
    ),
  );
  if (status === "FAIL") {
    panel.append(
      h(
        "section",
        { class: "detail-part next-step" },
        h("h3", {}, WORKSPACE.actionHeading),
        notes
          ? [
              definitions([
                [WORKSPACE.actionWhat, h("span", { class: "action" }, notes.action.what)],
                [WORKSPACE.actionReads, notes.action.reads],
                [WORKSPACE.actionRevise, notes.action.revise],
                [WORKSPACE.actionUndecided, notes.action.undecided],
                [WORKSPACE.recheckHeading, notes.recheck],
              ]),
            ]
          : note(WORKSPACE.noRuleNotes),
      ),
    );
  }
  panel.append(
    h(
      "section",
      { class: "detail-part" },
      h("h3", {}, WORKSPACE.requirementHeading),
      definitions([
        [WORKSPACE.ruleExpected, field(finding, "expected", (text) => h("span", { class: "prose" }, text))],
        [WORKSPACE.reason, field(finding, "reason", (text) => reasonText(text, notes))],
        [
          WORKSPACE.actual,
          carries(finding, "actual")
            ? finding.actual === ""
              ? WORKSPACE.actualEmpty
              : WORKSPACE.actualHidden
            : missing(NOT_CARRIED),
        ],
      ]),
    ),
  );
  if (carries(envelope, "comparison")) panel.append(findingComparison(state, finding, notes));
  panel.append(
    h(
      "details",
      { class: "evidence-details" },
      h("summary", {}, WORKSPACE.findingTrace),
      definitions([
        [WORKSPACE.identity.findingKey, field(finding, "finding_key", copyable)],
        [WORKSPACE.identity.requirementKey, field(finding, "requirement_key", code)],
        [
          WORKSPACE.identity.elementKey,
          finding.element_key ? code(finding.element_key) : WORKSPACE.wholeModel,
        ],
      ]),
    ),
  );
  return panel;
}

/** Which run this is, the rule set it was checked against and the files it read. */
function runIdentity(run) {
  return [
    definitions([
      [WORKSPACE.identity.run, field(run, "validation_run_id", copyable)],
      [
        WORKSPACE.identity.ruleset,
        field(run, "ruleset", (ruleset) => [
          field(ruleset, "id", code),
          " ",
          field(ruleset, "version", code),
        ]),
      ],
      [WORKSPACE.identity.asOf, field(run, "as_of", code)],
      [
        WORKSPACE.identity.checkers,
        field(run, "checkers", (checkers) =>
          checkers.map((checker) => [code(`${checker.id} ${checker.version}`), " "]),
        ),
      ],
    ]),
    tableWrap(
      table(
        WORKSPACE.identity.models,
        [
          WORKSPACE.identity.modelId,
          WORKSPACE.identity.declaredDiscipline,
          WORKSPACE.identity.filename,
          WORKSPACE.identity.digest,
          WORKSPACE.identity.tagSource,
        ],
        (carries(run, "models") ? run.models : []).map((model) =>
          h(
            "tr",
            {},
            h("td", {}, field(model, "model_id", code)),
            h("td", {}, field(model, "discipline", (text) => text)),
            h("td", {}, field(model, "filename", code)),
            h("td", {}, field(model, "content_sha256", code)),
            h(
              "td",
              {},
              field(model, "tag_source", (value) => [
                code(value),
                " ",
                value === "model-file"
                  ? null
                  : h("span", { class: "sub" }, tagAbsence({ kind: "source", value })),
              ]),
            ),
          ),
        ),
      ),
    ),
  ];
}

/** The filterable list of every result, in the adapter's order within each status. */
function workspaceList(state, selected) {
  const envelope = state.envelope;
  const groups = statusGroups(envelope.findings);
  const rows = [];
  const body = [];
  for (const group of groups) {
    for (const finding of group.findings) {
      const element = elementOf(envelope.elements, finding.element_key);
      const isSelected = selected !== null && finding.finding_key === selected.finding_key;
      const cells = workspaceCells(state, finding, element, envelope.run);
      // The name cell is the link: one keyboard stop per row.
      const nameCell = cells[1];
      nameCell.replaceChildren(
        h(
          "a",
          {
            href: href(state.mode, state.runId, "finding", finding.finding_key),
            "aria-current": isSelected ? "true" : null,
          },
          ...nameCell.childNodes,
        ),
      );
      // A click anywhere on the row opens it, as the name does: measured, a click
      // on the Tag or the class did nothing, and the Tag filled most of a row.
      // The keyboard keeps one stop per row, the name; a drag that selects text
      // (to copy a Tag) does not open anything.
      const target = href(state.mode, state.runId, "finding", finding.finding_key);
      const row = h(
        "tr",
        {
          class: isSelected ? "selected" : null,
          onclick: (event) => {
            if (event.target.closest("a, button, input")) return;
            if (String(globalThis.getSelection?.() ?? "") !== "") return;
            location.hash = target;
          },
        },
        cells,
      );
      rows.push({ node: row, finding, element });
      body.push(row);
    }
  }
  const shown = h("p", { class: "sub", role: "status" });
  const empty = h("p", { class: "note" }, WORKSPACE.filterNone);
  const apply = () => {
    let count = 0;
    for (const { node, finding, element } of rows) {
      const visible =
        (workspaceView.status === null || finding.status === workspaceView.status) &&
        matches(element, finding, workspaceView.query);
      node.hidden = !visible;
      if (visible) count += 1;
    }
    shown.textContent = fill(WORKSPACE.filterShown, { shown: count, count: rows.length });
    empty.hidden = count !== 0;
    for (const button of buttons) {
      button.setAttribute("aria-pressed", String(button.dataset.status === String(workspaceView.status)));
    }
  };
  const choice = (status, label, count) => {
    const button = h(
      "button",
      {
        type: "button",
        class: "quiet filter",
        "data-status": String(status),
        onclick: () => {
          workspaceView.status = status;
          apply();
        },
      },
      label,
      ` ${count}`,
    );
    return button;
  };
  const buttons = [
    choice(null, WORKSPACE.filterAll, envelope.findings.length),
    ...groups.map((group) =>
      choice(group.status, group.known ? FINDING_STATUS[group.status] : String(group.status), group.count),
    ),
  ];
  const search = h("input", {
    type: "search",
    id: "workspace-filter",
    value: workspaceView.query,
    oninput: (event) => {
      workspaceView.query = event.target.value;
      apply();
    },
  });
  const columns = WORKSPACE.columns;
  const list = h(
    "section",
    { class: "block ws-list" },
    h("h2", {}, WORKSPACE.listHeading),
    h("div", { class: "filters", role: "group", "aria-label": WORKSPACE.columns.status }, buttons),
    h("label", { for: "workspace-filter" }, WORKSPACE.filterLabel),
    search,
    shown,
    empty,
    tableWrap(
      table(
        null,
        RESULT_COLUMNS.map((column) => columns[column]),
        body,
      ),
    ),
  );
  apply();
  return list;
}

export function workspaceCheck(state, selectedKey) {
  const envelope = state.envelope;
  const run = envelope.run;
  if (workspaceView.run !== run.validation_run_id) {
    workspaceView.run = run.validation_run_id;
    workspaceView.status = null;
    workspaceView.query = "";
  }
  const selected = selectedKey === null ? null : findingByKey(envelope, selectedKey);
  const groups = statusGroups(envelope.findings);
  const requirementKeys = Object.keys(envelope.requirements);
  const content = h(
    "div",
    { class: "workspace" },
    h("p", {}, link(WORKSPACE.back, href())),
    h("h1", {}, WORKSPACE.resultTitle),
    h("p", { class: "callout" }, WORKSPACE.noJudgement),
    h(
      "section",
      { class: "block result" },
      h("h2", {}, plural(WORKSPACE.summary, envelope.findings.length)),
      h(
        "ul",
        { class: "result-lines" },
        groups.map((group) =>
          h("li", {}, h("strong", {}, plural(WORKSPACE_COMPARE.rows, group.count)), COMMON.colon, statusWord(group.status)),
        ),
      ),
      h("p", { class: "sub" }, WORKSPACE.unit),
    ),
  );
  if (carries(envelope, "comparison")) {
    const moved = transitions(envelope.comparison);
    content.append(
      h(
        "section",
        { class: "block" },
        h("p", {}, WORKSPACE.compareTeaser),
        h(
          "ul",
          { class: "result-lines" },
          moved.differing.map((group) =>
            h(
              "li",
              {},
              transitionLabel(group),
            ),
          ),
          h("li", {}, plural(WORKSPACE_COMPARE.unchanged, moved.sameCount)),
        ),
        h("p", {}, h("a", { class: "run", href: href(state.mode, state.runId, "compare") }, WORKSPACE.compareLink)),
      ),
    );
  }
  content.append(
    h(
      "section",
      { class: "block" },
      h("h2", {}, WORKSPACE.checkedHeading),
      requirementKeys.map((key) => requirementBlock(run, envelope.requirements[key])),
    ),
    // With nothing chosen, the list has the width to itself; the detail takes
    // its half only once there is something in it.
    h(
      "div",
      { class: selectedKey === null ? "ws-workbench no-pick" : "ws-workbench" },
      workspaceList(state, selected),
      h(
        "section",
        { class: selected ? "block ws-detail" : "block ws-detail empty" },
        selectedKey === null
          ? note(WORKSPACE.pickOne)
          : selected === null
            ? h("p", { class: "problem", tabindex: "-1", "data-return-focus": true }, WORKSPACE.noFinding)
            : findingPanel(state, selected),
      ),
    ),
    h(
      "details",
      { class: "block evidence-details" },
      h("summary", {}, WORKSPACE.identityHeading),
      runIdentity(run),
    ),
  );
  return content;
}

function transitionLabel(group) {
  return [
    statusWord(group.prior),
    " → ",
    statusWord(group.current),
    COMMON.colon,
    plural(WORKSPACE_COMPARE.rows, group.pairs.length),
  ];
}

/** Rows of one comparison group: the element, and a way into its current result. */
function comparisonRows(state, rows, side) {
  const envelope = state.envelope;
  const columns = WORKSPACE.columns;
  return tableWrap(
    table(
      null,
      [...RESULT_COLUMNS.map((column) => columns[column]), ""],
      rows.map((row) => {
        const { element, run, missing: gone } = comparisonElement(envelope, row);
        const finding = row[side];
        const cells = workspaceCells(state, { ...finding, model_key: row.model_key }, element, run);
        if (gone) cells[1].replaceChildren(missing(WORKSPACE_COMPARE.elementMissing));
        const current = side === "current" ? row.current.finding_key : null;
        return h(
          "tr",
          {},
          cells,
          h(
            "td",
            {},
            current
              ? link(WORKSPACE_COMPARE.open, href(state.mode, state.runId, "finding", current))
              : h(
                  "span",
                  { class: "sub" },
                  WORKSPACE_COMPARE.inCurrent[String(row.element_in_current_run)],
                ),
          ),
        );
      }),
    ),
  );
}

export function workspaceCompare(state) {
  const envelope = state.envelope;
  const back = h("p", {}, link(WORKSPACE.backToList, href(state.mode, state.runId)));
  if (!carries(envelope, "comparison")) {
    return h("div", {}, back, h("h1", {}, WORKSPACE_COMPARE.title), note(WORKSPACE_COMPARE.noComparison, "problem"));
  }
  const comparison = envelope.comparison;
  const moved = transitions(comparison);
  const models = modelChanges(comparison, envelope.run);
  const passing = envelope.findings.filter((finding) => finding.status === "PASS");
  const notes = Object.values(envelope.requirements)
    .map((requirement) => ruleNotes(envelope.run, requirement))
    .filter((entry) => entry !== null);
  const content = h(
    "div",
    { class: "workspace" },
    back,
    h("h1", {}, WORKSPACE_COMPARE.title),
    h("p", { class: "lede" }, WORKSPACE_COMPARE.lede),
    h("p", { class: "callout" }, WORKSPACE.noJudgement),
    section(
      WORKSPACE_COMPARE.runsHeading,
      definitions([
        [WORKSPACE_COMPARE.prior, field(comparison.prior_run, "validation_run_id", copyable)],
        [WORKSPACE_COMPARE.current, field(envelope.run, "validation_run_id", copyable)],
      ]),
      h("p", { class: "beside" }, WORKSPACE_COMPARE.order),
      h("p", { class: "sub" }, WORKSPACE_COMPARE.same),
    ),
    section(
      WORKSPACE_COMPARE.changedHeading,
      h("h3", {}, plural(WORKSPACE_COMPARE.differs, moved.differingCount)),
      moved.differing.length
        ? moved.differing.map((group) => [
            h("h4", {}, transitionLabel(group)),
            comparisonRows(state, group.pairs, "current"),
          ])
        : note(WORKSPACE_COMPARE.differsNone),
      h("h3", {}, plural(WORKSPACE_COMPARE.unchanged, moved.sameCount)),
      moved.same.length
        ? moved.same.map((group) =>
            h(
              "details",
              {},
              h("summary", {}, transitionLabel(group)),
              comparisonRows(state, group.pairs, "current"),
            ),
          )
        : note(WORKSPACE_COMPARE.unchangedNone),
      h("h3", {}, plural(WORKSPACE_COMPARE.notReEvaluated.label, moved.notReEvaluatedCount)),
      moved.notReEvaluatedCount
        ? [note(WORKSPACE_COMPARE.notReEvaluated.note), comparisonRows(state, comparison.not_re_evaluated, "prior")]
        : null,
      h("h3", {}, plural(WORKSPACE_COMPARE.newlyAppearing.label, moved.newlyAppearingCount)),
      moved.newlyAppearingCount
        ? [note(WORKSPACE_COMPARE.newlyAppearing.note), comparisonRows(state, comparison.newly_appearing, "current")]
        : null,
    ),
    section(
      WORKSPACE_COMPARE.whyHeading,
      models.changed.length
        ? [
            h("p", {}, WORKSPACE_COMPARE.changedModels),
            h(
              "ul",
              {},
              models.changed.map(({ row, model }) =>
                h(
                  "li",
                  {},
                  modelName(model),
                  " ",
                  model === null ? null : field(model, "filename", code),
                  h(
                    "div",
                    { class: "sub" },
                    WORKSPACE.identity.digest,
                    COMMON.colon,
                    code(short(row.prior_content_sha256)),
                    " → ",
                    code(short(row.current_content_sha256)),
                  ),
                ),
              ),
            ),
          ]
        : h("p", {}, WORKSPACE_COMPARE.noChangedModels),
      models.unchanged.length
        ? h("p", {}, WORKSPACE_COMPARE.unchangedModels, models.unchanged.map((model) => [" ", modelName(model)]))
        : null,
      h("p", {}, WORKSPACE_COMPARE.why),
    ),
    section(
      WORKSPACE_COMPARE.gapsHeading,
      h(
        "ul",
        { class: "caveats" },
        h("li", {}, WORKSPACE_COMPARE.notInData),
        notes.flatMap((entry) => entry.gaps.map((text) => h("li", {}, text))),
      ),
      passing.length
        ? h(
            "p",
            {},
            WORKSPACE_COMPARE.passLink,
            passing.map((finding) => [
              " ",
              link(
                elementTitleOf(envelope, finding),
                href(state.mode, state.runId, "finding", finding.finding_key),
              ),
            ]),
          )
        : null,
    ),
    h(
      "details",
      { class: "block evidence-details" },
      h("summary", {}, WORKSPACE.identityHeading),
      h("h3", {}, WORKSPACE_COMPARE.prior),
      runIdentity(comparison.prior_run),
      h("h3", {}, WORKSPACE_COMPARE.current),
      runIdentity(envelope.run),
    ),
  );
  return content;
}

function elementTitleOf(envelope, finding) {
  const element = elementOf(envelope.elements, finding.element_key);
  const model = modelOf(envelope.run, finding.model_key);
  const tag = tagReading(element, model);
  const name = element !== null && named(element) ? element.name : ELEMENT_WORDS.unnamed;
  return tag.kind === "tag" ? `${tag.value} ${name}` : name;
}

export function workspaceRefusal(state) {
  const refusal = state.envelope.refusal;
  return h(
    "div",
    { class: "refusal" },
    h("h1", {}, WORKSPACE_REFUSAL.title),
    h("p", { class: "lede" }, WORKSPACE_REFUSAL.lede),
    section(
      WORKSPACE_REFUSAL.reasonsHeading,
      h(
        "ul",
        {},
        refusal.reasons.map((reason) =>
          h(
            "li",
            {},
            h(
              "strong",
              {},
              Object.hasOwn(WORKSPACE_REFUSAL_REASONS, reason.code)
                ? WORKSPACE_REFUSAL_REASONS[reason.code]
                : WORKSPACE_REFUSAL.unglossed,
            ),
            " ",
            field(reason, "code", code),
          ),
        ),
      ),
    ),
    section(
      WORKSPACE_REFUSAL.actionHeading,
      WORKSPACE_REFUSAL.action.map((text) => h("p", {}, text)),
      h("p", { class: "callout" }, WORKSPACE_REFUSAL.scope),
    ),
    note(WORKSPACE_REFUSAL.noResult),
    h(
      "details",
      { class: "block evidence-details" },
      h("summary", {}, WORKSPACE_REFUSAL.original),
      definitions([[WORKSPACE_REFUSAL.code, copyable(refusal.code)]]),
      h("pre", { class: "refusal-text" }, refusal.text),
    ),
    h(
      "p",
      { class: "actions" },
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
        CONTEXT.home,
      ),
    ),
  );
}
