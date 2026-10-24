import { h } from "./dom.js";
import { UI } from "./ui-words.js";

// Both links use the real existing directory/entry routes. No snapshot shortcuts.
export function shell(mode) {
  return h("div", { class: "top-inner" },
    h("a", { class: "brand", href: "#/" },
      h("span", { class: "brand-mark", "aria-hidden": "true" }, "BD"),
      h("span", { class: "brand-name" }, "BIM Doctor"), h("span", { class: "version-label" }, UI.preview)),
    h("nav", { class: "main-nav", "aria-label": UI.navigation },
      h("a", { href: `./projects.html?lang=${document.documentElement.lang.startsWith("en") ? "en" : "zh"}` }, UI.projects),
      h("a", { href: `./review.html?lang=${document.documentElement.lang.startsWith("en") ? "en" : "zh"}` }, UI.review),
      h("a", { href: "#/fixture", "aria-current": mode === "fixture" ? "page" : null }, UI.examples),
      h("a", { href: "#/local", "aria-current": mode === "local" ? "page" : null }, UI.local)),
    h("div", { id: "language", class: "language" }));
}
