// State, routing and the envelope boundary. Screens live in screens.js.
//
// The envelope is taken as the adapter returned it. This file checks that it
// has the agreed keys for its outcome and that its mode is the mode the manager
// chose; it never fills a missing key, never re-derives a verdict, and never
// turns one mode's result into the other's.
//
// Routes are #/<mode>/<run_id>/<screen>/…, so a reload or a shared link asks the
// adapter for the same run again rather than keeping a copy of any result.
// One recheck item is #/<mode>/<run_id>/recheck/<subscope index>/<member index>.
// One first-check item is #/<mode>/<run_id>/item/<activity index>/<group>/<member index>.
// A workspace run is #/workspace/workspace, one of its results is
// …/finding/<finding_key>, and its comparison with the earlier run …/compare.
// The local check is #/local, and one finished check #/local/<check_id>[/finding/<key>]
// (local-check.js, which makes its own requests).

import { h, note } from "./dom.js";
import { LANG, LANGUAGES, fill } from "./i18n.js";
import { languageSwitch, untranslated } from "./language.js";
import { localEntry, localScreen } from "./local-check.js";
import { renderContext, screens } from "./screens.js";
import { APP, ENVELOPE_WORDS, FAULT_WORDS, PAGE } from "./words.js";

const state = {
  mode: null, // the experience the manager chose
  runs: null,
  runId: null,
  envelope: null,
};

// `workspace` offers a run only when the server was started with one; the home
// screen asks before showing its card.
const MODES = ["fixture", "real", "workspace"];

// The screens whose words have English. In English, any other screen says it
// is not translated yet instead of being drawn half in each language; in
// Chinese every screen is drawn. Which screen a route shows never depends on
// the language — only whether its words can be shown in it.
export const TRANSLATED = new Set([
  "entry",
  "runs/fixture",
  "runs/real",
  "runs/workspace",
  "first",
  "item",
  "recheck",
  "refusal",
  "workspace/check",
  "workspace/finding",
  "workspace/compare",
  "workspace/refusal",
]);

function inLanguage(name) {
  return LANG !== "en" || TRANSLATED.has(name);
}

function shapeWords(template, outcome, key) {
  return template.replace("{outcome}", outcome).replace("{key}", key);
}

// A workspace envelope is a validation run or a refused comparison. It carries
// no record, and a refusal carries nothing but the refusal: neither run's
// findings, no comparison and no elements.
function workspaceProblem(envelope) {
  const isObject = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
  const outcome = envelope.outcome;
  if (outcome === "validation") {
    for (const [key, valid] of [
      ["run", isObject],
      ["findings", Array.isArray],
      ["requirements", isObject],
      ["elements", isObject],
    ]) {
      if (!valid(envelope[key])) return shapeWords(ENVELOPE_WORDS.missing, outcome, key);
    }
    for (const key of ["record", "assessment_digest", "refusal"]) {
      if (key in envelope) return shapeWords(ENVELOPE_WORDS.unexpected, outcome, key);
    }
    if ("comparison" in envelope) {
      const comparison = envelope.comparison;
      for (const [key, valid] of [
        ["prior_run", isObject],
        ["changed_models", Array.isArray],
        ["pairs", Array.isArray],
        ["not_re_evaluated", Array.isArray],
        ["newly_appearing", Array.isArray],
        ["prior_elements", isObject],
      ]) {
        if (!isObject(comparison) || !valid(comparison[key])) {
          return shapeWords(ENVELOPE_WORDS.missing, outcome, `comparison.${key}`);
        }
      }
    }
    return null;
  }
  if (outcome === "refusal") {
    const refusal = envelope.refusal;
    if (!refusal || typeof refusal.code !== "string" || typeof refusal.text !== "string") {
      return shapeWords(ENVELOPE_WORDS.missing, outcome, "refusal.code / refusal.text");
    }
    if (!Array.isArray(refusal.reasons)) {
      return shapeWords(ENVELOPE_WORDS.missing, outcome, "refusal.reasons");
    }
    for (const key of ["run", "findings", "comparison", "record", "assessment_digest"]) {
      if (key in envelope) return shapeWords(ENVELOPE_WORDS.unexpected, outcome, key);
    }
    return null;
  }
  return fill(APP.unknownOutcome, { outcome: JSON.stringify(outcome) });
}

export function clearResults(mode) {
  state.mode = mode;
  state.runs = null;
  state.runId = null;
  state.envelope = null;
}

// What is wrong with an envelope, or null. Only presence and type: the values
// themselves are the Framework's and are shown as they are.
export function envelopeProblem(envelope, mode) {
  if (!envelope || typeof envelope !== "object") return APP.notObject;
  if (envelope.mode !== mode) {
    return fill(APP.modeMismatch, { got: JSON.stringify(envelope.mode), want: JSON.stringify(mode) });
  }
  if (mode === "workspace") return workspaceProblem(envelope);
  if (!envelope.elements || typeof envelope.elements !== "object") return APP.missingElements;
  if (envelope.outcome === "record") {
    if (!envelope.record || typeof envelope.record !== "object") return APP.recordMissing;
    if (typeof envelope.assessment_digest !== "string" || !envelope.assessment_digest) {
      return APP.digestMissing;
    }
    if ("refusal" in envelope) return APP.recordWithRefusal;
    return null;
  }
  if (envelope.outcome === "refusal") {
    const refusal = envelope.refusal;
    if (!refusal || typeof refusal.code !== "string" || typeof refusal.text !== "string") {
      return APP.refusalIncomplete;
    }
    if ("record" in envelope || "assessment_digest" in envelope) {
      return APP.refusalWithRecord;
    }
    return null;
  }
  return fill(APP.unknownOutcome, { outcome: JSON.stringify(envelope.outcome) });
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  let body = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  if (!response.ok) {
    const detail = body && body.error ? body.error : `HTTP ${response.status}`;
    const error = new Error(detail);
    error.unavailable = response.status === 503;
    error.status = response.status;
    throw error;
  }
  return body;
}

async function ensureRuns(mode) {
  if (state.runs !== null) return;
  const body = await fetchJson(`/api/runs?mode=${encodeURIComponent(mode)}`);
  if (state.mode === mode) state.runs = Array.isArray(body.runs) ? body.runs : [];
}

async function ensureEnvelope(mode, runId) {
  if (state.runId === runId && state.envelope) return;
  state.runId = runId;
  state.envelope = null;
  await ensureRuns(mode);
  const run = state.runs.find((item) => item.run_id === runId);
  if (!run) throw new Error(fill(APP.notInMode, { run: JSON.stringify(runId) }));
  const envelope = await fetchJson(
    `/api/envelope?mode=${encodeURIComponent(mode)}&run=${encodeURIComponent(runId)}`,
  );
  if (state.mode !== mode || state.runId !== runId) return;
  const problem = envelopeProblem(envelope, mode);
  if (problem) throw new Error(fill(APP.invalid, { problem }));
  state.envelope = envelope;
}

function parseRoute() {
  return location.hash
    .replace(/^#\/?/, "")
    .split("/")
    .filter(Boolean)
    .map((part) => decodeURIComponent(part));
}

export function href(...parts) {
  return "#/" + parts.map((part) => encodeURIComponent(String(part))).join("/");
}

export function go(...parts) {
  location.hash = href(...parts);
}

let rendering = 0;

async function render() {
  // Also the count of routes shown since this page loaded: past the first, there
  // is a page inside the preview to go back to.
  const token = ++rendering;
  const main = document.getElementById("main");
  const header = document.getElementById("context");
  const [mode, runId, screen, ...rest] = parseRoute();
  // The language is on every screen, whatever the screen.
  document.getElementById("language").replaceChildren(languageSwitch());

  if (mode === "local") {
    if (state.mode !== mode) clearResults(mode);
    main.replaceChildren(h("p", { role: "status" }, APP.loading));
    const local = await localScreen(runId ?? null, screen ?? null, rest);
    if (token !== rendering) return;
    header.replaceChildren(...local.context);
    main.replaceChildren(local.content);
    focusMain(main);
    return;
  }
  if (!mode || !MODES.includes(mode)) {
    clearResults(null);
    header.replaceChildren();
    // The workspace card is shown only when the server says it has a run to
    // offer. A failed question is said as such, never as "no workspace".
    let workspace;
    try {
      const body = await fetchJson("/api/runs?mode=workspace");
      workspace = { runs: Array.isArray(body.runs) ? body.runs : [] };
    } catch (problem) {
      workspace = { error: problem.message };
    }
    // The local check's card, when this server offers one.
    let local;
    try {
      local = localEntry(await fetchJson("/api/local"));
    } catch (problem) {
      local = localEntry({ error: problem.message, status: problem.status });
    }
    if (token !== rendering) return;
    main.replaceChildren(
      inLanguage("entry") ? screens.entry(workspace, local) : untranslated(href(), token > 1),
    );
    focusMain(main);
    return;
  }
  if (state.mode !== mode) clearResults(mode); // arriving in a mode clears the other's result
  if (!runId && state.runId) {
    state.runId = null;
    state.envelope = null;
  }

  let content;
  try {
    if (!runId) {
      await ensureRuns(mode);
      content = inLanguage(`runs/${mode}`) ? screens.runs(state) : untranslated(href(), token > 1);
    } else {
      main.replaceChildren(h("p", { role: "status" }, APP.loading));
      await ensureEnvelope(mode, runId);
      if (token !== rendering) return;
      const outcome = state.envelope.outcome;
      // A workspace run has screens of its own: there is no record behind it.
      const workspaceWanted =
        mode === "workspace" ? screen || (outcome === "refusal" ? "refusal" : "check") : null;
      // A recheck record opens on its result: what is left to do comes before
      // the record's own context, which stays one link away.
      const wanted =
        workspaceWanted ??
        (screen ||
          (outcome !== "record" ? "refusal" : state.envelope.record.successor ? "recheck" : "first"));
      const expected = wanted === "refusal" ? "refusal" : mode === "workspace" ? "validation" : "record";
      if (outcome !== expected) {
        go(mode, runId);
        return;
      }
      if (!inLanguage(mode === "workspace" ? `workspace/${wanted}` : wanted)) {
        content = untranslated(href(), token > 1);
      } else if (mode === "workspace") {
        switch (wanted) {
          case "check":
            content = screens.workspaceCheck(state, null);
            break;
          case "finding":
            content = screens.workspaceCheck(state, rest[0] ?? "");
            break;
          case "compare":
            content = screens.workspaceCompare(state);
            break;
          case "refusal":
            content = screens.workspaceRefusal(state);
            break;
          default:
            content = h("div", {}, note(fill(APP.noPage, { screen: wanted }), "problem"));
        }
      } else switch (wanted) {
        case "record":
          content = screens.record(state);
          break;
        case "activity":
          // …/activity/<index>/sub/<ordinal>/<item…> arrives from a recheck item.
          content = screens.activity(
            state,
            Number(rest[0]),
            rest[1] === "sub"
              ? {
                  ordinal: Number(rest[2]),
                  subscopeIndex: Number(rest[3]),
                  memberIndex: Number(rest[4]),
                }
              : null,
          );
          break;
        case "member":
          content = screens.member(state, Number(rest[0]), Number(rest[1]), Number(rest[2]));
          break;
        case "first":
          content = screens.first(state);
          break;
        case "item":
          content = screens.firstItem(state, Number(rest[0]), Number(rest[1]), Number(rest[2]));
          break;
        case "recheck":
          // …/recheck/of/<activity>/<group>/<member> arrives from a first-check item.
          content = !rest.length
            ? screens.recheck(state)
            : rest[0] === "of"
              ? screens.recheckItemOf(state, rest[1], Number(rest[2]), Number(rest[3]))
              : screens.recheckItem(state, Number(rest[0]), Number(rest[1]));
          break;
        case "refusal":
          content = screens.refusal(state);
          break;
        default:
          content = h("div", {}, note(fill(APP.noPage, { screen: wanted }), "problem"));
      }
    }
  } catch (failure) {
    if (runId) {
      state.runId = null;
      state.envelope = null;
    }
    // A fault of the program, kept apart from a refusal: a refusal is an answer
    // about the request and arrives as a result with its own screen. Nothing
    // here is a statement about a project or a model.
    content = h(
      "div",
      { class: "fault" },
      h("h1", {}, failure.unavailable ? FAULT_WORDS.unavailable : FAULT_WORDS.fault),
      note(FAULT_WORDS.note, "problem"),
      h("p", {}, APP.technical),
      h("pre", { class: "refusal-text" }, failure.message),
      h("p", {}, h("a", { href: href(mode) }, APP.up)),
    );
  }
  if (token !== rendering || state.mode !== mode) return;
  header.replaceChildren(...renderContext(state));
  main.replaceChildren(content);
  focusMain(main);
}

// A screen may mark the place the manager came from; they are put back on it
// instead of at the top of the page. Otherwise focus goes to the heading.
function focusMain(main) {
  const origin = main.querySelector("[data-return-focus]");
  if (origin) {
    origin.focus();
    origin.scrollIntoView({ block: "center" });
    return;
  }
  const heading = main.querySelector("h1");
  if (heading) {
    heading.setAttribute("tabindex", "-1");
    heading.focus();
  }
}

// The page's own words, once: they do not change with the route.
function framePage() {
  document.documentElement.lang = LANGUAGES[LANG];
  document.title = PAGE.title;
  document.querySelector("a.skip").textContent = PAGE.skip;
  document.getElementById("context").setAttribute("aria-label", PAGE.contextLabel);
}

window.addEventListener("hashchange", render);
window.addEventListener("DOMContentLoaded", () => {
  framePage();
  render();
});
