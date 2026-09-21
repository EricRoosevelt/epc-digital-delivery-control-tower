// State, routing and the envelope boundary. Screens live in screens.js.
//
// The envelope is taken as the adapter returned it. This file checks that it
// has the agreed keys for its outcome and that its mode is the mode the manager
// chose; it never fills a missing key, never re-derives a verdict, and never
// turns one mode's result into the other's.
//
// Routes are #/<mode>/<run_id>/<screen>/…, so a reload or a shared link asks the
// adapter for the same run again rather than keeping a copy of any result.

import { h, note } from "./dom.js";
import { renderContext, screens } from "./screens.js";

const state = {
  mode: null, // the experience the manager chose
  runs: null,
  runId: null,
  envelope: null,
};

const MODES = ["fixture", "real"];

export function clearResults(mode) {
  state.mode = mode;
  state.runs = null;
  state.runId = null;
  state.envelope = null;
}

// What is wrong with an envelope, or null. Only presence and type: the values
// themselves are the Framework's and are shown as they are.
function envelopeProblem(envelope, mode) {
  if (!envelope || typeof envelope !== "object") return "信封不是对象";
  if (envelope.mode !== mode) {
    return `信封的 mode 为 ${JSON.stringify(envelope.mode)}，与所选模式 ${JSON.stringify(mode)} 不一致`;
  }
  if (!envelope.elements || typeof envelope.elements !== "object") return "信封缺少 elements";
  if (envelope.outcome === "record") {
    if (!envelope.record || typeof envelope.record !== "object") return "outcome=record 但缺少 record";
    if (typeof envelope.assessment_digest !== "string" || !envelope.assessment_digest) {
      return "outcome=record 但缺少 assessment_digest";
    }
    if ("refusal" in envelope) return "outcome=record 却同时带有 refusal";
    return null;
  }
  if (envelope.outcome === "refusal") {
    const refusal = envelope.refusal;
    if (!refusal || typeof refusal.code !== "string" || typeof refusal.text !== "string") {
      return "outcome=refusal 但 refusal 缺少 code 或 text";
    }
    if ("record" in envelope || "assessment_digest" in envelope) {
      return "outcome=refusal 却同时带有 record 或 assessment_digest";
    }
    return null;
  }
  return `未识别的 outcome ${JSON.stringify(envelope.outcome)}`;
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
    throw error;
  }
  return body;
}

export function unavailableText(failure) {
  return failure.unavailable
    ? `输入不可用（不是拒绝，也不是成功）：${failure.message}`
    : failure.message;
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
  if (!run) throw new Error(`适配器没有为此模式提供运行 ${JSON.stringify(runId)}`);
  const envelope = await fetchJson(
    `/api/envelope?mode=${encodeURIComponent(mode)}&run=${encodeURIComponent(runId)}`,
  );
  if (state.mode !== mode || state.runId !== runId) return;
  const problem = envelopeProblem(envelope, mode);
  if (problem) throw new Error(`适配器返回的信封不符合约定：${problem}。未显示任何结果。`);
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
  const token = ++rendering;
  const main = document.getElementById("main");
  const header = document.getElementById("context");
  const [mode, runId, screen, ...rest] = parseRoute();

  if (!mode || !MODES.includes(mode)) {
    clearResults(null);
    header.replaceChildren();
    main.replaceChildren(screens.entry());
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
      content = screens.runs(state);
    } else {
      main.replaceChildren(h("p", { role: "status" }, "正在请求适配器…"));
      await ensureEnvelope(mode, runId);
      if (token !== rendering) return;
      const outcome = state.envelope.outcome;
      const wanted = screen || (outcome === "record" ? "record" : "refusal");
      if (wanted === "refusal" ? outcome !== "refusal" : outcome !== "record") {
        go(mode, runId);
        return;
      }
      switch (wanted) {
        case "record":
          content = screens.record(state);
          break;
        case "activity":
          content = screens.activity(state, Number(rest[0]));
          break;
        case "member":
          content = screens.member(state, Number(rest[0]), Number(rest[1]), Number(rest[2]));
          break;
        case "recheck":
          content = screens.recheck(state);
          break;
        case "refusal":
          content = screens.refusal(state);
          break;
        default:
          content = h("div", {}, note(`没有这个页面：${wanted}`, "problem"));
      }
    }
  } catch (failure) {
    if (runId) {
      state.runId = null;
      state.envelope = null;
    }
    content = h(
      "div",
      {},
      h("h1", {}, "无法显示结果"),
      note(unavailableText(failure), "problem"),
      h("p", {}, h("a", { href: href(mode) }, "返回运行列表")),
    );
  }
  if (token !== rendering || state.mode !== mode) return;
  header.replaceChildren(...renderContext(state));
  main.replaceChildren(content);
  focusMain(main);
}

function focusMain(main) {
  const heading = main.querySelector("h1");
  if (heading) {
    heading.setAttribute("tabindex", "-1");
    heading.focus();
  }
}

window.addEventListener("hashchange", render);
window.addEventListener("DOMContentLoaded", render);
