// Which language the Doctor speaks, and how a module says its words in both.
//
// The language is the viewer's choice and nothing else: it is read once, when
// the page loads, from `?lang=` and then from what this browser chose before,
// and it defaults to Chinese. Changing it reloads the page with the same
// `#/…` route, so the run, the record, the mode and the element shown stay
// exactly what they were; only the wording table changes.
//
// A module that writes words registers them here, in both languages, with
// `bilingual(name, zh, en)`, and uses what it returns. The central tables in
// vocabulary.js and vocabulary-en.js go through words.js; a new page can keep
// its own two tables in its own module and register them the same way. Every
// registered pair is what the parity tests read: the same keys, the same
// placeholders, and no Chinese in the English.
//
// A table registered without English is Chinese in both languages, and a page
// that uses one is not translated: in English the router shows that page's
// "not translated yet" notice instead of drawing it half in each language.

export const LANGUAGES = Object.freeze({ zh: "zh-CN", en: "en" });

const STORE_KEY = "doctor.language";

function chosen() {
  try {
    const asked = new URLSearchParams(globalThis.location?.search ?? "").get("lang");
    if (asked && Object.hasOwn(LANGUAGES, asked)) return asked;
  } catch {
    // An unreadable address is no choice.
  }
  try {
    const stored = globalThis.localStorage?.getItem(STORE_KEY);
    if (stored && Object.hasOwn(LANGUAGES, stored)) return stored;
  } catch {
    // Storage can be unavailable; the default stands.
  }
  return "zh";
}

export const LANG = chosen();

/** Every table registered, by name, with both languages as given. */
export const REGISTRY = new Map();

/** The table for the current language; `en` undefined means "not translated". */
export function bilingual(name, zh, en) {
  if (REGISTRY.has(name)) throw new Error(`wording table registered twice: ${name}`);
  REGISTRY.set(name, { zh, en });
  return LANG === "en" && en !== undefined ? en : zh;
}

/** Whether a registered table has English. */
export function hasEnglish(name) {
  return REGISTRY.has(name) && REGISTRY.get(name).en !== undefined;
}

/** Reload in another language, on the same route. */
export function chooseLanguage(language) {
  if (!Object.hasOwn(LANGUAGES, language) || language === LANG) return;
  try {
    globalThis.localStorage?.setItem(STORE_KEY, language);
  } catch {
    // The address below still carries the choice.
  }
  const url = new URL(globalThis.location.href);
  url.searchParams.set("lang", language);
  // The hash — the route — is part of the URL and is kept as it is.
  globalThis.location.replace(url.toString());
}

/** A wording template with its `{name}` placeholders filled. */
export function fill(template, values) {
  return Object.entries(values).reduce(
    (text, [key, value]) => text.replaceAll(`{${key}}`, String(value)),
    template,
  );
}
