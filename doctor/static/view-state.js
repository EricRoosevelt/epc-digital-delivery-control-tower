// View state is tab-local memory, never a result and never part of a share URL.
// Only a language reload gets a one-use handoff; it is removed before rendering.
const HANDOFF = "doctor.ui.language-handoff";
const blank = () => ({ run: null, query: "", status: null, selected: null });

function receive() {
  try {
    const raw = globalThis.sessionStorage?.getItem(HANDOFF);
    globalThis.sessionStorage?.removeItem(HANDOFF);
    if (!raw) return blank();
    const saved = JSON.parse(raw);
    const view = saved.view;
    if (saved.route !== globalThis.location?.hash || !view || typeof view.run !== "string" ||
        typeof view.query !== "string" ||
        !(view.selected === null || typeof view.selected === "string") ||
        !(view.status === null || typeof view.status === "string")) return blank();
    return { run: view.run, query: view.query, status: view.status, selected: view.selected };
  } catch {
    return blank();
  }
}

export const workspaceView = receive();

export function selectRun(key) {
  if (workspaceView.run !== key) Object.assign(workspaceView, blank(), { run: key });
  return workspaceView;
}

export function carryForLanguage() {
  try {
    globalThis.sessionStorage?.removeItem(HANDOFF);
    const route = globalThis.location?.hash;
    const prefix = workspaceView.run === null ? null
      : "#/" + workspaceView.run.split("/").map(encodeURIComponent).join("/");
    if (prefix !== null && (route === prefix || route?.startsWith(prefix + "/"))) {
      globalThis.sessionStorage?.setItem(HANDOFF, JSON.stringify({
        route, view: workspaceView,
      }));
    }
  } catch {
    // Unavailable storage does not prevent the same object route being reloaded.
  }
}
