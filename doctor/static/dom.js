// DOM helpers. Every value from an envelope reaches the page as a text node,
// never as markup: a refusal message or a Pack sentence is shown, not executed.

export function h(tag, attributes = {}, ...children) {
  const node = document.createElement(tag);
  for (const [name, value] of Object.entries(attributes)) {
    if (value === undefined || value === null || value === false) continue;
    if (name === "class") node.className = value;
    else if (name.startsWith("on")) node.addEventListener(name.slice(2), value);
    else node.setAttribute(name, value === true ? "" : String(value));
  }
  append(node, children);
  return node;
}

function append(node, children) {
  for (const child of children) {
    if (child === undefined || child === null || child === false) continue;
    if (Array.isArray(child)) append(node, child);
    else if (child instanceof Node) node.appendChild(child);
    else node.appendChild(document.createTextNode(String(child)));
  }
}

// An identifier the manager may need to copy: shown whole, selectable, with a
// copy button that does not depend on hover.
export function code(value) {
  return h("code", { class: "ident" }, value);
}

export function copyable(value) {
  const button = h(
    "button",
    {
      type: "button",
      class: "copy",
      "aria-label": `复制 ${value}`,
      onclick: async () => {
        try {
          await navigator.clipboard.writeText(value);
          button.textContent = "已复制";
        } catch {
          button.textContent = "请手动选择复制";
        }
      },
    },
    "复制",
  );
  return h("span", { class: "copyable" }, code(value), button);
}

// A key the envelope does not carry. Rendered as words, never as an empty cell,
// a dash, a zero or a blank that could be mistaken for a recorded value.
export function missing(text) {
  return h("span", { class: "not-carried" }, text);
}

// One evidence citation's provenance, shown beside the citation itself. The
// short form is the label; the long sentence is spelled out in a legend on the
// same page, because a qualification that only appears on hover is not shown.
export function provenanceTag(entry) {
  return h("span", { class: `provenance provenance-${entry.key}` }, entry.short);
}

export function definitions(rows) {
  return h(
    "dl",
    { class: "facts" },
    rows
      .filter((row) => row)
      .map(([term, value]) => [h("dt", {}, term), h("dd", {}, value)]),
  );
}

export function table(caption, headers, rows, attributes = {}) {
  return h(
    "table",
    attributes,
    caption ? h("caption", {}, caption) : null,
    h("thead", {}, h("tr", {}, headers.map((label) => h("th", { scope: "col" }, label)))),
    h("tbody", {}, rows),
  );
}

export function section(title, ...children) {
  return h("section", { class: "block" }, h("h2", {}, title), children);
}

export function note(text, kind = "note") {
  return h("p", { class: kind }, text);
}

// Verdicts are words first. The shape class only adds a border style, so the
// meaning never depends on colour.
export function verdict(value) {
  return h("span", { class: `verdict verdict-${String(value).toLowerCase()}` }, value);
}

export function link(label, href) {
  return h("a", { href }, label);
}
