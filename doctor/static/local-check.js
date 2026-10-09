// The local check: a user's own IFC file, checked in a workspace of its own.
//
// #/local is the start page: what this checks and only this, what this
// computer keeps and how to clean it up — both before anything is chosen —
// then choosing files, declaring each one's discipline, the scope the server
// plans, and the run. #/local/<check_id> is one finished check: the workspace
// screens' result list and details (workspace-screens.js, unchanged), framed
// by what the exercise is, whether anything was applicable, the scope it ran
// with, and where its records are.
//
// Nothing here decides anything. The server stages, plans, refuses and runs
// (internal/doctor_adapter/local_check.py); this page says what it answered.
// A refusal is an answer about the request and is shown with what to do; a
// fault is the program's and is shown as such, never as a result. The words
// are local-words.js, registered in both languages.

import { clearResults, envelopeProblem, go, href } from "./app.js";
import { code, copyable, definitions, h, link, note, section, table } from "./dom.js";
import { fill } from "./i18n.js";
import { LOCAL } from "./local-words.js";
import { carries, field, tableWrap } from "./screens.js";
import { CITATION_GLOSSES, CONTEXT } from "./words.js";
import { workspaceCheck } from "./workspace-screens.js";
import { ruleNotes } from "./workspace-model.js";

const STORE_KEY = "doctor.local.selection";

// What the viewer has chosen on the start page. Kept for this browser tab, so
// that changing the language — which reloads the page — keeps the selection.
// The files themselves are on the server; the plan says if one has gone.
const session = {
  described: null,
  selection: restore(),
  plan: null,
  planFor: null,
  refusal: null,
  fileRefusals: [],
  fault: null,
  records: null,
  // Which step's newest answer focus goes to after a redraw.
  focus: null,
};

// The finished check on screen, read once per check rather than per route.
const shown = { checkId: null, envelope: null, scope: null, described: null };

function restore() {
  try {
    const stored = JSON.parse(globalThis.sessionStorage?.getItem(STORE_KEY) ?? "null");
    if (stored && typeof stored.ruleset === "string" && Array.isArray(stored.models)) return stored;
  } catch {
    // Unreadable or unavailable storage is no selection.
  }
  return { ruleset: "", models: [] };
}

function persist() {
  try {
    globalThis.sessionStorage?.setItem(STORE_KEY, JSON.stringify(session.selection));
  } catch {
    // The selection still holds until the page is reloaded.
  }
}

/** A request to the server; a refusal is a 200 answer, a fault is thrown. */
async function ask(url, options = {}) {
  let response;
  try {
    response = await fetch(url, { cache: "no-store", ...options });
  } catch {
    const failure = new Error(LOCAL.fault.network);
    failure.network = true;
    throw failure;
  }
  let body = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  if (!response.ok) {
    const failure = new Error(body && body.error ? body.error : `HTTP ${response.status}`);
    failure.status = response.status;
    throw failure;
  }
  return body;
}

function postJson(url, body) {
  return ask(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

function size(bytes) {
  if (bytes >= 1e9) return fill(LOCAL.choose.sizeGb, { gb: (bytes / 1e9).toFixed(1) });
  if (bytes >= 1e5) return fill(LOCAL.choose.size, { mb: (bytes / 1e6).toFixed(1) });
  return fill(LOCAL.choose.sizeKb, { kb: Math.max(1, Math.round(bytes / 1e3)) });
}

function joined(values) {
  return values.join(LOCAL.listSeparator);
}

function disciplineName(value) {
  return Object.hasOwn(LOCAL.disciplines, value) ? LOCAL.disciplines[value] : value;
}

/** Where a path under the checks directory really is, when the system moved it. */
function onDisk(described, path) {
  const named = described.checks_dir;
  const real = described.checks_dir_on_disk;
  if (!real || real === named || !path.startsWith(named)) return null;
  return real + path.slice(named.length);
}

// ---------------------------------------------------------------------------
// The home page's card
// ---------------------------------------------------------------------------

/**
 * What the home page shows for the local check, given what `/api/local`
 * answered: nothing when this server was started without it, otherwise its
 * card and the home sentences that are true when it is offered.
 */
export function localEntry(answer) {
  if (answer === null || (answer.error && answer.status === 503)) return null;
  const card = h(
    "article",
    { class: "entry-card" },
    h("h3", {}, LOCAL.home.title),
    h("p", {}, LOCAL.home.body),
    answer.error
      ? h("p", { class: "problem" }, LOCAL.home.unknown, " ", answer.error)
      : h("button", { type: "button", onclick: () => go("local") }, LOCAL.home.action),
  );
  return { card, words: LOCAL.home };
}

// ---------------------------------------------------------------------------
// Shared blocks
// ---------------------------------------------------------------------------

function contextBar(checkId) {
  return [
    h(
      "div",
      { class: "context-bar" },
      h("span", { class: "mode mode-local" }, LOCAL.mode),
      checkId ? h("span", {}, code(checkId)) : null,
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
  ];
}

function requirementRows(ruleset) {
  const run = { ruleset: { id: ruleset.id, version: ruleset.version } };
  return Object.values(ruleset.requirements ?? {}).map((requirement) => {
    const notes = ruleNotes(run, requirement);
    return h(
      "div",
      { class: "requirement" },
      h("h4", {}, field(requirement, "rule_id", code), " ", notes ? notes.title : field(requirement, "specification_label", (text) => text)),
      notes ? h("p", {}, notes.predicate) : null,
      definitions([
        [
          LOCAL.scope.citation,
          field(requirement, "citation", (text) => [
            Object.hasOwn(CITATION_GLOSSES, text) ? h("div", {}, CITATION_GLOSSES[text]) : null,
            h("div", { class: "sub prose" }, text),
          ]),
        ],
      ]),
    );
  });
}

function exerciseBlock(described) {
  const ruleset = described.rulesets[0] ?? null;
  return h(
    "section",
    { class: "block" },
    h("h2", {}, LOCAL.exercise.heading),
    h("p", { class: "callout" }, LOCAL.exercise.what),
    // How to read a result stays in view; the rule's own words and where the
    // requirement comes from are one fold away, under their own heading.
    h("h3", {}, LOCAL.exercise.readHeading),
    h("ul", { class: "caveats" }, LOCAL.exercise.read.map((text) => h("li", {}, text))),
    note(LOCAL.exercise.notes),
    h(
      "details",
      { class: "evidence-details" },
      h("summary", {}, LOCAL.exercise.sourceHeading),
      ruleset
        ? [
            h("p", {}, code(`${ruleset.id} ${ruleset.version}`), " ", ruleset.title),
            requirementRows(ruleset),
          ]
        : null,
      h("p", {}, LOCAL.exercise.source),
      ruleset ? h("p", { class: "sub prose" }, ruleset.description) : null,
    ),
  );
}

/** What this computer keeps, where, and how to clean it up; `location` is one check's. */
function recordsBlock(described, location = null, open = true) {
  const real = described.checks_dir_on_disk;
  const words = LOCAL.records;
  const facts = [
    [words.named, copyable(described.checks_dir)],
    real && real !== described.checks_dir ? [words.onDisk, copyable(real)] : null,
    location ? [LOCAL.result.location, copyable(onDisk(described, location) ?? location)] : null,
  ];
  const where = [
    h("p", {}, words.lede),
    definitions(facts),
    real && real !== described.checks_dir ? h("p", { class: "problem" }, words.redirected) : null,
    real === null
      ? note(words.notYet)
      : note(fill(words.kept, { uploads: described.kept.uploads, checks: described.kept.checks })),
  ];
  const body = [
    h("h3", {}, words.whatHeading),
    h("ul", {}, words.what.map((text) => h("li", {}, text))),
    h("h3", {}, words.cleanHeading),
    h("ol", {}, words.clean.map((text) => h("li", {}, text))),
    h("h3", {}, words.afterHeading),
    h("ul", { class: "caveats" }, words.after.map((text) => h("li", {}, text))),
    h("p", {}, words.again),
    h("h3", {}, words.startHeading),
    h("p", {}, words.start),
    h("pre", { class: "refusal-text" }, words.command),
    note(words.startNote),
  ];
  return h(
    "section",
    { class: "block", id: "local-records" },
    h("h2", {}, open ? words.heading : LOCAL.result.recordsHeading),
    where,
    // Where the records are and how many are kept stay in view; what is kept,
    // how to clean up and what cannot be relied on afterwards are one fold away.
    h("details", { class: "evidence-details" }, h("summary", {}, words.cleanHeading), body),
  );
}

/** Ask again what is kept, and redraw the records section in place. */
async function refreshRecords(host) {
  try {
    session.described = await ask("/api/local");
    host.replaceChildren(recordsBlock(session.described));
  } catch {
    // The section keeps what it last said; the next action reports the fault.
  }
}

/** A refusal's reasons, each with what to do; a check's refusal also says nothing ran. */
function refusalBlock(refusal, ofCheck = true) {
  const words = LOCAL.refusal;
  return h(
    "div",
    { class: "refusal" },
    ofCheck ? [h("h3", { tabindex: "-1", "data-local-focus": session.focus === "scope" }, words.heading), h("p", {}, words.lede)] : null,
    h(
      "ul",
      {},
      refusal.reasons.map((reason) =>
        h(
          "li",
          {},
          typeof reason.filename === "string" ? [code(reason.filename), LOCAL.colon] : null,
          h(
            "strong",
            {},
            Object.hasOwn(words.reasons, reason.code) ? words.reasons[reason.code] : words.unglossed,
          ),
          " ",
          code(reason.code),
        ),
      ),
    ),
    // What the system returned, when it returned something: a refusal this
    // page made itself has no original, and is not shown as if it had one.
    typeof refusal.text === "string"
      ? h(
          "details",
          { class: "evidence-details" },
          h("summary", {}, words.original),
          h("pre", { class: "refusal-text" }, refusal.text),
        )
      : null,
  );
}

function faultBlock(failure) {
  const words = LOCAL.fault;
  return h(
    "div",
    { class: "fault" },
    h("h3", { tabindex: "-1", "data-local-focus": true }, words.heading),
    h("p", { class: "problem" }, failure.network ? words.network : words.lede),
    failure.network
      ? null
      : [
          h("h4", {}, words.todoHeading),
          h("ol", {}, words.todo.map((text) => h("li", {}, text))),
          h("p", {}, words.original),
          h("pre", { class: "refusal-text" }, failure.message),
        ],
  );
}

// ---------------------------------------------------------------------------
// #/local — the start page
// ---------------------------------------------------------------------------

function request() {
  return {
    ruleset: session.selection.ruleset,
    models: session.selection.models.map((model) => ({
      upload: model.upload,
      filename: model.filename,
      discipline: model.discipline,
    })),
  };
}

function forget() {
  session.plan = null;
  session.planFor = null;
  session.refusal = null;
  session.fault = null;
  persist();
}

function focusIn(container) {
  const target = container.querySelector("[data-local-focus]");
  if (target) {
    target.focus();
    target.scrollIntoView({ block: "nearest" });
  }
}

/** Whether this server would refuse a file of `size` bytes as too large, unread.
 *
 * The same comparison the server makes: a file of exactly the limit is taken.
 */
export function overLimit(size, max) {
  return typeof max === "number" && typeof size === "number" && size > max;
}

async function stage(files, steps) {
  const status = steps.querySelector("#local-copying");
  session.fileRefusals = [];
  session.fault = null;
  for (const file of files) {
    // A file over this server's limit is refused here and never sent. The
    // server refuses it unread too, but a connection closed in the middle of
    // an upload reaches a browser as a dropped connection, not as that answer.
    if (overLimit(file.size, session.described && session.described.max_model_bytes)) {
      session.fileRefusals.push({
        filename: file.name,
        refusal: { reasons: [{ code: "model-too-large", filename: file.name }] },
      });
      continue;
    }
    status.textContent = fill(LOCAL.choose.copying, { file: file.name });
    try {
      const answer = await ask(`/api/local/models?filename=${encodeURIComponent(file.name)}`, {
        method: "POST",
        headers: { "Content-Type": "application/octet-stream" },
        body: file,
      });
      if (answer.outcome === "staged") {
        const model = answer.model;
        if (!session.selection.models.some((item) => item.upload === model.upload)) {
          session.selection.models.push({ ...model, discipline: "" });
        }
      } else {
        session.fileRefusals.push({ filename: file.name, refusal: answer.refusal });
      }
    } catch (failure) {
      session.fault = failure;
      break;
    }
  }
  status.textContent = "";
  session.focus = "files";
  session.plan = null;
  session.planFor = null;
  session.refusal = null;
  persist();
  await refreshRecords(session.records);
  drawSteps(steps);
  focusIn(steps);
}

function chooseStep(steps, described) {
  const words = LOCAL.choose;
  const input = h("input", {
    type: "file",
    id: "local-files",
    accept: ".ifc",
    multiple: true,
    onchange: (event) => {
      const files = [...event.target.files];
      event.target.value = "";
      if (files.length) stage(files, steps);
    },
  });
  const models = session.selection.models;
  return h(
    "section",
    { class: "block" },
    h("h2", {}, words.heading),
    note(fill(words.note, { max: size(described.max_model_bytes) })),
    h("span", { class: "file-pick" }, input, h("label", { for: "local-files" }, words.label)),
    h("p", { class: "sub status", role: "status", id: "local-copying" }),
    session.fileRefusals.map(({ filename, refusal }) => [
      h(
        "h3",
        { class: "problem", tabindex: "-1", "data-local-focus": session.focus === "files" },
        fill(words.refusedHeading, { file: filename }),
      ),
      refusalBlock(refusal, false),
    ]),
    h("h3", {}, words.chosenHeading),
    models.length
      ? tableWrap(
          table(
            null,
            [words.columns.file, words.columns.size, words.columns.schema, words.columns.remove],
            models.map((model, index) =>
              h(
                "tr",
                {},
                h("td", {}, code(model.filename)),
                h("td", {}, size(model.byte_count)),
                h("td", {}, code(model.ifc_schema)),
                h(
                  "td",
                  {},
                  h(
                    "button",
                    {
                      type: "button",
                      class: "quiet",
                      onclick: () => {
                        models.splice(index, 1);
                        forget();
                        drawSteps(steps);
                        steps.querySelector("#local-copying").textContent = words.removed;
                      },
                    },
                    words.remove,
                  ),
                ),
              ),
            ),
          ),
        )
      : note(words.none),
  );
}

function declareStep(steps, described) {
  const words = LOCAL.declare;
  const offered = described.rulesets;
  if (!offered.some((ruleset) => ruleset.name === session.selection.ruleset)) {
    session.selection.ruleset = offered[0].name;
    persist();
  }
  const scope = [
    ...new Set(
      offered.flatMap((ruleset) =>
        Object.values(ruleset.requirements ?? {}).flatMap((requirement) => requirement.discipline_scope ?? []),
      ),
    ),
  ];
  const models = session.selection.models;
  return h(
    "section",
    { class: "block" },
    h("h2", {}, words.heading),
    h(
      "fieldset",
      {},
      h("legend", {}, words.rulesetLegend),
      offered.map((ruleset) =>
        h(
          "label",
          { class: "choice" },
          h("input", {
            type: "radio",
            name: "local-ruleset",
            value: ruleset.name,
            checked: ruleset.name === session.selection.ruleset,
            onchange: () => {
              session.selection.ruleset = ruleset.name;
              forget();
              drawSteps(steps);
            },
          }),
          " ",
          fill(words.ruleset, { id: ruleset.id, version: ruleset.version, title: ruleset.title }),
        ),
      ),
    ),
    models.map((model, index) =>
      h(
        "p",
        {},
        h("label", { for: `local-discipline-${index}` }, fill(words.disciplineLabel, { file: model.filename })),
        " ",
        h(
          "select",
          {
            id: `local-discipline-${index}`,
            onchange: (event) => {
              model.discipline = event.target.value;
              forget();
              drawSteps(steps);
            },
          },
          h("option", { value: "", selected: model.discipline === "" }, words.choose),
          described.disciplines.map((discipline) =>
            h("option", { value: discipline, selected: model.discipline === discipline }, disciplineName(discipline)),
          ),
        ),
      ),
    ),
    note(fill(words.disciplineNote, { scope: joined(scope.map(disciplineName)) })),
    h(
      "p",
      { class: "actions" },
      h(
        "button",
        {
          type: "button",
          onclick: async (event) => {
            event.target.disabled = true;
            event.target.textContent = words.planning;
            const asked = request();
            session.focus = "scope";
            session.refusal = null;
            session.fault = null;
            session.plan = null;
            try {
              const answer = await postJson("/api/local/plan", asked);
              if (answer.outcome === "plan") {
                session.plan = answer.plan;
                session.planFor = JSON.stringify(asked);
              } else {
                session.refusal = answer.refusal;
              }
            } catch (failure) {
              session.fault = failure;
            }
            drawSteps(steps);
            focusIn(steps);
          },
        },
        words.plan,
      ),
    ),
  );
}

function scopeStep(steps, described) {
  const words = LOCAL.scope;
  const container = h("section", { class: "block" }, h("h2", {}, words.heading));
  if (session.fault) {
    container.append(faultBlock(session.fault));
    return container;
  }
  if (session.refusal) {
    container.append(refusalBlock(session.refusal));
    return container;
  }
  if (session.plan === null) return container;
  if (session.planFor !== JSON.stringify(request())) {
    container.append(note(words.changed));
    return container;
  }
  const plan = session.plan;
  const stages = plan.programme.map((item) => item.stage);
  const running = h("p", { class: "sub status", role: "status" });
  container.append(
    h("p", { tabindex: "-1", "data-local-focus": session.focus === "scope", class: "headline" }, words.ready),
    h("h3", {}, words.models),
    tableWrap(
      table(
        null,
        [words.modelColumns.file, words.modelColumns.discipline, words.modelColumns.schema, words.modelColumns.size],
        plan.models.map((model) =>
          h(
            "tr",
            {},
            h("td", {}, code(model.filename)),
            h("td", {}, disciplineName(model.discipline)),
            h("td", {}, code(model.ifc_schema)),
            h("td", {}, size(model.byte_count)),
          ),
        ),
      ),
    ),
    definitions([
      [words.ruleset, [code(`${plan.ruleset.id} ${plan.ruleset.version}`), " ", plan.ruleset.title]],
      [words.requirement, requirementRows({ ...plan.ruleset, requirements: plan.requirements })],
      [words.location, copyable(onDisk(described, plan.location) ?? plan.location)],
      [words.geometry, words.geometryText],
    ]),
    h(
      "p",
      { class: "actions" },
      h(
        "button",
        {
          type: "button",
          onclick: async (event) => {
            event.target.disabled = true;
            session.focus = "scope";
            running.textContent = words.running;
            try {
              const answer = await postJson("/api/local/checks", JSON.parse(session.planFor));
              if (answer.outcome === "finished") {
                // A finished check starts the next one from an empty choice.
                session.selection.models = [];
                session.fileRefusals = [];
                forget();
                go("local", answer.check.check_id);
                return;
              }
              session.refusal = answer.refusal;
            } catch (failure) {
              session.fault = failure;
            }
            drawSteps(steps);
            focusIn(steps);
          },
        },
        words.run,
      ),
    ),
    running,
    h(
      "details",
      { class: "evidence-details" },
      h("summary", {}, words.trace),
      definitions([
        [words.checkId, code(plan.check_id)],
        [words.digest, copyable(plan.ruleset.normalized_digest)],
        [words.asOf, [code(plan.as_of), " ", h("span", { class: "sub" }, words.asOfNote)]],
        [words.programme, fill(words.programmeText, { stages: joined(stages) })],
      ]),
      tableWrap(
        table(
          null,
          [words.modelColumns.file, words.modelColumns.code, words.modelColumns.digest],
          plan.models.map((model) =>
            h(
              "tr",
              {},
              h("td", {}, code(model.filename)),
              h("td", {}, code(model.model_id)),
              h("td", {}, copyable(model.content_sha256)),
            ),
          ),
        ),
      ),
    ),
  );
  return container;
}

function drawSteps(steps) {
  const described = session.described;
  if (!described.rulesets.length) {
    steps.replaceChildren(note(LOCAL.start.noRuleset, "problem"));
    return;
  }
  steps.replaceChildren(
    chooseStep(steps, described),
    declareStep(steps, described),
    scopeStep(steps, described),
  );
}

function earlierBlock(checks) {
  const words = LOCAL.earlier;
  return section(
    words.heading,
    note(words.note),
    checks.length
      ? h(
          "ul",
          { class: "run-list" },
          checks.map((check) =>
            h(
              "li",
              {},
              link(
                fill(words.item, {
                  files: joined(check.scope.models.map((model) => model.filename)),
                  ruleset: `${check.scope.ruleset.id} ${check.scope.ruleset.version}`,
                  id: check.check_id,
                }),
                href("local", check.check_id),
              ),
            ),
          ),
        )
      : note(words.none),
  );
}

async function startPage() {
  const described = await ask("/api/local");
  const listed = await ask("/api/local/checks");
  session.described = described;
  // Redrawn in place when a file is kept, so it says what is there now.
  session.records = h("div", {}, recordsBlock(described));
  const steps = h("div", { class: "local-steps" });
  drawSteps(steps);
  return h(
    "div",
    { class: "local" },
    h("p", {}, link(LOCAL.start.back, href())),
    h("h1", {}, LOCAL.start.title),
    h("p", { class: "lede" }, LOCAL.start.lede),
    exerciseBlock(described),
    session.records,
    steps,
    earlierBlock(Array.isArray(listed.checks) ? listed.checks : []),
  );
}

// ---------------------------------------------------------------------------
// #/local/<check_id> — one finished check
// ---------------------------------------------------------------------------

function resultFrame(envelope, scope) {
  const models = carries(envelope.run, "models") ? envelope.run.models : [];
  const nothing = models.filter((model) => {
    const own = envelope.findings.filter((finding) => finding.model_key === model.model_key);
    return own.length > 0 && own.every((finding) => finding.status === "N/A");
  });
  const words = LOCAL.result;
  return [
    h("p", { class: "callout" }, words.exercise),
    nothing.length
      ? h(
          "section",
          { class: "block result" },
          h("h2", {}, words.nothingHeading),
          nothing.map((model) => h("p", { class: "headline" }, fill(words.nothing, { file: model.filename }))),
        )
      : null,
    scope
      ? h(
          "section",
          { class: "block" },
          h("h2", {}, words.scopeHeading),
          h("p", {}, code(`${scope.ruleset.id} ${scope.ruleset.version}`), " ", scope.ruleset.title),
          h(
            "ul",
            {},
            scope.models.map((model) =>
              h(
                "li",
                {},
                fill(words.declared, { file: model.filename, discipline: disciplineName(model.discipline) }),
              ),
            ),
          ),
          h(
            "p",
            {},
            fill(words.programme, { stages: joined(scope.programme.map((item) => item.stage)) }),
          ),
          h("p", { class: "sub" }, LOCAL.scope.geometryText),
        )
      : null,
  ];
}

async function resultPage(checkId, screen, rest) {
  if (shown.checkId !== checkId) {
    shown.checkId = null;
    let envelope;
    try {
      envelope = await ask(`/api/local/envelope?run=${encodeURIComponent(checkId)}`);
    } catch (failure) {
      if (failure.status === 404) {
        return h(
          "div",
          {},
          h("p", {}, link(LOCAL.start.back, href())),
          h("h1", {}, LOCAL.start.title),
          h("p", { class: "problem" }, LOCAL.result.missing),
          h("p", {}, link(LOCAL.result.another, href("local"))),
        );
      }
      throw failure;
    }
    const problem = envelopeProblem(envelope, "workspace");
    if (problem) throw new Error(problem);
    const listed = await ask("/api/local/checks");
    shown.described = await ask("/api/local");
    shown.scope = (listed.checks ?? []).find((check) => check.check_id === checkId) ?? null;
    shown.envelope = envelope;
    shown.checkId = checkId;
  }
  const state = { mode: "local", runId: checkId, envelope: shown.envelope };
  const content = workspaceCheck(state, screen === "finding" ? (rest[0] ?? "") : null);
  content.querySelector("h1").after(...resultFrame(shown.envelope, shown.scope?.scope ?? null).filter(Boolean));
  content.append(
    recordsBlock(shown.described, shown.scope?.location ?? null, false),
    h("p", { class: "actions" }, link(LOCAL.result.another, href("local"))),
  );
  return content;
}

/** The local check's page for a route under #/local: its context and content. */
export async function localScreen(checkId, screen, rest) {
  let content;
  try {
    content = checkId ? await resultPage(checkId, screen, rest) : await startPage();
  } catch (failure) {
    content = h(
      "div",
      {},
      h("p", {}, link(LOCAL.start.back, href())),
      h("h1", {}, LOCAL.start.title),
      failure.status === 503 ? h("p", { class: "problem" }, LOCAL.start.unavailable, " ", failure.message) : faultBlock(failure),
    );
  }
  return { context: contextBar(checkId), content };
}
