// Shared request boundary for project persistence and the review workspace.
export async function requestJSON(url, options = {}) {
  const timeout = AbortSignal.timeout(180000);
  const response = await fetch(url, { ...options, signal: options.signal ? AbortSignal.any([options.signal, timeout]) : timeout });
  let body;
  try { body = await response.json(); }
  catch (error) {
    if (response.ok) throw error;
    body = {};
  }
  if (!response.ok) throw new Error(typeof body.error === "string" ? body.error : body.error?.message || `HTTP ${response.status}`);
  return body;
}

export function postJSON(url, body, options = {}) {
  return requestJSON(url, { ...options, method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
}
