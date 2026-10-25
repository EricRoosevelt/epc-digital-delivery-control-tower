// Shared request boundary for project persistence and the review workspace.
export async function requestJSON(url, options = {}) {
  const { onResponse, ...fetchOptions } = options;
  const timeout = AbortSignal.timeout(30000);
  const response = await fetch(url, { ...fetchOptions, signal: options.signal ? AbortSignal.any([options.signal, timeout]) : timeout });
  onResponse?.({ requestId: response.headers.get("X-Request-ID"), status: response.status });
  let body;
  try { body = await response.json(); }
  catch (error) {
    if (response.ok) { error.requestId = response.headers.get("X-Request-ID"); error.responsePhase = "decode"; throw error; }
    body = {};
  }
  if (!response.ok) throw Object.assign(new Error(typeof body.error === "string" ? body.error : body.error?.message || `HTTP ${response.status}`), { status: response.status, requestId: response.headers.get("X-Request-ID") || body.request_id });
  return body;
}

export function postJSON(url, body, options = {}) {
  return requestJSON(url, { ...options, method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
}
