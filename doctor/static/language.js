// The language switch on every screen, and what an untranslated page says in
// English instead of being drawn half in each language.
//
// This module keeps its own words, in both languages, and registers them with
// i18n.js — the way a page added later (a local IFC check, say) can carry its
// own wording without adding to the central tables.

import { h } from "./dom.js";
import { LANG, LANGUAGES, bilingual, chooseLanguage } from "./i18n.js";

const WORDS = bilingual(
  "LANGUAGE",
  {
    label: "界面语言",
    current: "当前：中文",
    untranslatedTitle: "这一页还没有翻译",
    untranslatedBody:
      "这一页的英文还没有写好。下面的按钮会用中文打开同一页：同一个运行、同一份记录、同一个对象，内容不变。",
    showIn: "用中文查看这一页",
    back: "← 返回上一页",
    home: "返回首页",
  },
  {
    label: "Interface language",
    current: "Current: English",
    untranslatedTitle: "This page has not been translated yet",
    untranslatedBody:
      "The English for this page has not been written yet. The button below opens this same page in Chinese: the same run, the same record and the same element, with nothing changed.",
    showIn: "See this page in Chinese",
    back: "← Back to the previous page",
    home: "Back to the home page",
  },
);

// Each language is named in itself, so either can be found from the other.
const NAMES = { zh: "中文", en: "English" };

/** The switch: which language is on, and a way to the other on the same page. */
export function languageSwitch() {
  return h(
    "nav",
    { class: "language-switch", "aria-label": WORDS.label },
    h("span", { class: "sub" }, WORDS.current),
    Object.keys(LANGUAGES).map((language) =>
      h(
        "button",
        {
          type: "button",
          class: "quiet",
          lang: LANGUAGES[language],
          "aria-pressed": String(language === LANG),
          onclick: () => chooseLanguage(language),
        },
        NAMES[language],
      ),
    ),
  );
}

/** In English, a page whose words are not translated yet: said, never mixed.
 *
 * The links that lead here say beforehand that the page is Chinese only; this
 * page offers the way back to where the viewer came from, as well as home.
 */
export function untranslated(homeHref) {
  return h(
    "div",
    { class: "untranslated" },
    h("h1", {}, WORDS.untranslatedTitle),
    h("p", {}, WORDS.untranslatedBody),
    h(
      "p",
      { class: "actions" },
      h("button", { type: "button", onclick: () => chooseLanguage("zh") }, WORDS.showIn),
      " ",
      h("button", { type: "button", class: "quiet", onclick: () => history.back() }, WORDS.back),
      " ",
      h("a", { href: homeHref }, WORDS.home),
    ),
  );
}
