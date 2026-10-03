"""The English interface: a second wording table, never a second page.

What these tests hold, in the order the user requirement states it:

* the language is the viewer's, read when the page loads, Chinese by default,
  and changing it keeps the route — the same run, record and element;
* every English table has the same keys, list lengths and `{placeholders}` as
  the Chinese one, and no Chinese in it;
* where the Pack, the record or this repository's product documents already
  say it in English, the English shown is that text — quoted, not a
  translation of the Chinese gloss; and what the record carries is read from
  the record, with no copy in the static files;
* a screen drawn in English uses only tables that have English, and writes no
  sentence of its own; any other screen is not drawn in English but says that
  it has not been translated yet;
* every English entry is in the record the BIM reviewer reads.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC = PROJECT_ROOT / "doctor" / "static"
RECORD = PROJECT_ROOT / "docs" / "product" / "2026-10-03-doctor-english-vocabulary.md"
PACK = PROJECT_ROOT / "purpose-packs" / "interdisciplinary-coordination-readiness" / "pack.toml"
PRODUCT = (
    PROJECT_ROOT
    / "docs"
    / "product"
    / "interdisciplinary-coordination-readiness-mep-to-architecture.md"
)
CJK = re.compile(r"[一-鿿]")

#: The screens drawn in English. Everything else says it is not translated yet.
TRANSLATED = {"entry", "runs/fixture", "runs/real", "first"}

#: Tables a translated screen may touch without English, and why.
WITHOUT_ENGLISH = {
    # Only the workspace branch of runs() reads it: route runs/workspace,
    # which is not translated and is not drawn in English.
    "WORKSPACE",
    # Read only to decide whether action sentences exist for this Pack
    # version; in English their words are the record's own route text.
    "ACTIONS",
}

#: Functions of words.js that word their answer in the chosen language.
IN_LANGUAGE = {"citationProvenance"}

#: Tables that are data, the same in both languages.
NEUTRAL = {
    "ACTION_PACK",
    "ASPECT_ORDER",
    "FIXTURE_MARKER",
    "FOLLOW_UP",
    "PRODUCT_VALIDATION",
    "PROJECT_ASSUMPTION",
    "RULE_NOTES_FOR",
}

_DRIVER = """
globalThis.location = { search: process.argv[2] };
const i18n = await import("./i18n.js");
const words = await import("./words.js");
await import("./language.js");
const registry = {};
for (const [name, pair] of i18n.REGISTRY) {
  registry[name] = {
    zh: typeof pair.zh === "function" ? null : pair.zh,
    en: pair.en === undefined || typeof pair.en === "function" ? null : pair.en,
    same: pair.en === pair.zh,
  };
}
process.stdout.write(
  JSON.stringify({
    lang: i18n.LANG,
    registry,
    home: words.HOME,
    exports: Object.keys(words).sort(),
  }),
);
"""


def _load(search: str) -> dict:
    node = shutil.which("node")
    if node is None:
        message = "node is not on PATH; the wording tables cannot be loaded"
        if os.environ.get("CI"):
            raise AssertionError(message)
        raise unittest.SkipTest(message)
    with tempfile.TemporaryDirectory() as directory:
        workdir = Path(directory)
        for path in STATIC.glob("*.js"):
            shutil.copyfile(path, workdir / path.name)
        (workdir / "package.json").write_text('{"type": "module"}\n', encoding="utf-8")
        (workdir / "driver.mjs").write_text(_DRIVER, encoding="utf-8")
        completed = subprocess.run(
            [node, "driver.mjs", search], cwd=workdir, capture_output=True, check=False
        )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return json.loads(completed.stdout.decode("utf-8"))


def _flat(value, prefix=""):
    if isinstance(value, str):
        yield prefix, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _flat(item, f"{prefix}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _flat(item, f"{prefix}.{key}" if prefix else key)


def _shape(value):
    if isinstance(value, dict):
        return {key: _shape(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_shape(item) for item in value]
    return type(value).__name__


def _exports(path: Path) -> set[str]:
    return set(
        re.findall(r"^export (?:const|function) (\w+)", path.read_text(encoding="utf-8"), re.M)
    )


def _functions(text: str) -> dict[str, str]:
    found = {}
    for match in re.finditer(r"^(?:export )?(?:async )?function (\w+)\(", text, re.M):
        end = text.index("\n}\n", match.start()) + 2
        found[match.group(1)] = text[match.start() : end]
    return found


def _locals(body: str) -> set[str]:
    """The parameters and variables a function body declares."""

    signature = body[body.index("(") : body.index(")")]
    names = set(re.findall(r"\b([a-zA-Z_]\w*)\b", signature))
    names |= set(re.findall(r"\b(?:const|let)\s+(\w+)", body))
    for params in re.findall(r"\(([\w\s,=]*)\)\s*=>", body):
        names |= set(re.findall(r"\b([a-zA-Z_]\w*)\b", params))
    names |= set(re.findall(r"\b(\w+)\s*=>", body))
    return names


def _code(body: str) -> str:
    return "\n".join(
        line.split(" // ")[0]
        for line in body.splitlines()
        if not line.lstrip().startswith(("//", "*", "/*"))
    )


class _Loaded(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zh = _load("")
        cls.en = _load("?lang=en")
        cls.registry = cls.en["registry"]
        cls.english = {
            name: pair
            for name, pair in cls.registry.items()
            if pair["en"] is not None and not pair["same"]
        }


class LanguageTests(_Loaded):
    def test_the_language_is_the_viewers_and_chinese_by_default(self):
        self.assertEqual(self.zh["lang"], "zh")
        self.assertEqual(self.en["lang"], "en")
        self.assertEqual(_load("?lang=fr")["lang"], "zh")
        self.assertTrue(CJK.search(self.zh["home"]["title"]))
        self.assertFalse(CJK.search(self.en["home"]["title"]))

    def test_changing_language_keeps_the_route(self):
        i18n = (STATIC / "i18n.js").read_text(encoding="utf-8")
        choose = _functions(i18n)["chooseLanguage"]
        self.assertIn('url.searchParams.set("lang", language)', choose)
        self.assertIn("location.replace(url.toString())", choose)
        self.assertNotIn(".hash", _code(choose))

    def test_the_switch_is_on_every_screen(self):
        app = (STATIC / "app.js").read_text(encoding="utf-8")
        render = _functions(app)["render"]
        switch = render.index("languageSwitch()")
        self.assertLess(switch, render.index("return"))
        self.assertLess(switch, render.index("screens.entry("))
        language = (STATIC / "language.js").read_text(encoding="utf-8")
        self.assertIn('"aria-pressed": String(language === LANG)', language)


class ParityTests(_Loaded):
    def test_words_mirrors_vocabulary_export_for_export(self):
        self.assertEqual(set(self.en["exports"]), _exports(STATIC / "vocabulary.js"))

    def test_the_english_tables_are_vocabulary_en_and_the_modules_own(self):
        self.assertEqual(
            set(self.english), _exports(STATIC / "vocabulary-en.js") | {"LANGUAGE"}
        )
        self.assertEqual(
            {name for name, pair in self.registry.items() if pair["same"]}, NEUTRAL
        )

    def test_english_has_the_same_keys_and_placeholders_and_no_chinese(self):
        for name, pair in self.english.items():
            zh, en = pair["zh"], pair["en"]
            with self.subTest(table=name):
                if name == "IFC_CLASS_NAMES":
                    # An IFC class is shown by its own English name.
                    self.assertEqual(en, {})
                    continue
                self.assertEqual(_shape(en), _shape(zh))
            zh_strings = dict(_flat(zh))
            for key, text in _flat(en):
                with self.subTest(table=name, key=key):
                    self.assertTrue(text.strip())
                    self.assertFalse(CJK.search(text), text)
                    self.assertEqual(
                        set(re.findall(r"\{(\w+)\}", text)),
                        set(re.findall(r"\{(\w+)\}", zh_strings[key])),
                    )

    def test_a_provenance_entry_keeps_its_key_in_both_languages(self):
        pair = self.registry["CITATION_PROVENANCE"]
        for name, entry in pair["zh"].items():
            with self.subTest(entry=name):
                self.assertEqual(pair["en"][name]["key"], entry["key"])


class OriginalTests(_Loaded):
    def test_the_activity_names_are_the_packs_labels(self):
        pack = tomllib.loads(PACK.read_text(encoding="utf-8"))
        labels = {activity["activity_id"]: activity["label"] for activity in pack["activities"]}
        names = self.registry["ACTIVITY_NAMES"]["en"]
        self.assertEqual({key: value["name"] for key, value in names.items()}, labels)

    def test_what_each_activity_needs_is_the_product_documents_sentence(self):
        text = PRODUCT.read_text(encoding="utf-8")
        section = text[text.index("### What Architecture does next with it") :]
        section = section[: section.index("These are three different questions")]
        listed = {
            re.sub(r"\W", "", title).lower(): " ".join(body.split())
            for title, body in re.findall(
                r"\d\. \*\*(.+?)\*\* — (.+?)(?=\n\d\.|\n\n)", section, re.S
            )
        }
        needs = self.registry["ACTIVITY_NAMES"]["en"]
        self.assertEqual(len(listed), len(needs))
        for activity in needs.values():
            sentence = listed[re.sub(r"\W", "", activity["name"]).lower()]
            with self.subTest(activity=activity["name"]):
                self.assertEqual(activity["needs"], sentence[0].upper() + sentence[1:])

    def test_the_verdict_meanings_are_the_product_documents_definitions(self):
        text = PRODUCT.read_text(encoding="utf-8")
        defined = {
            word: definition.replace("**", "").rstrip(".")
            for word, definition in re.findall(r"^\| \*\*(\w+)\*\* \| (.+?) \|$", text, re.M)
        }
        for word, meaning in self.registry["VERDICT_WORDS"]["en"].items():
            with self.subTest(verdict=word):
                self.assertEqual(meaning, defined[word])
        self.assertEqual(
            {
                word: label.upper()
                for word, label in self.registry["VERDICT_LABELS"]["en"].items()
            },
            {word: word for word in self.registry["VERDICT_LABELS"]["en"]},
        )

    def test_english_reads_the_records_own_action_words(self):
        """No copy of the Pack's next_action in a static file: the record carries it."""

        self.assertNotIn("ACTIONS", _exports(STATIC / "vocabulary-en.js"))
        self.assertEqual(self.registry["ACTION_TEXT"]["en"], {"source": "record"})
        self.assertEqual(self.registry["ACTION_TEXT"]["zh"], {"source": "gloss"})
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        sentences = _functions(screens)["actionSentences"]
        self.assertIn('original("next_action")', sentences)
        self.assertIn('original("recheck_condition")', sentences)
        self.assertIn(
            "actionSentences(item.kind, request, item.subscope)", _functions(screens)["first"]
        )


class ScreenTests(unittest.TestCase):
    def test_the_router_draws_only_translated_screens_in_english(self):
        app = (STATIC / "app.js").read_text(encoding="utf-8")
        declared = re.search(r"export const TRANSLATED = new Set\(\[([^\]]*)\]\)", app).group(1)
        self.assertEqual(set(re.findall(r'"([^"]+)"', declared)), TRANSLATED)
        render = _functions(app)["render"]
        self.assertIn(
            'inLanguage("entry") ? screens.entry(workspace) : untranslated(href())', render
        )
        self.assertIn(
            "inLanguage(`runs/${mode}`) ? screens.runs(state) : untranslated(href())", render
        )
        guard = render.index("if (!inLanguage(")
        for call in re.findall(r"screens\.(?!entry|runs)\w+\(", render):
            with self.subTest(screen=call):
                self.assertLess(guard, render.index(call))

    def test_a_translated_screen_uses_only_words_with_english(self):
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        found = _functions(screens)
        imported = re.search(r'import \{([^}]*)\} from "\./words\.js"', screens).group(1)
        tables = {name.strip() for name in imported.split(",") if name.strip()}
        roots = ["renderContext", "entry", "runs", "first"]
        reached, todo = set(), list(roots)
        while todo:
            name = todo.pop()
            if name in reached:
                continue
            reached.add(name)
            # A call, or a function handed over as the last argument or to
            # .map(); never a word or a variable that shares its name
            # (`state.runs`, `envelope.record`, an `activity` parameter).
            body = _code(found[name])
            local = _locals(body)
            for other in found:
                if other in reached:
                    continue
                handed = other not in local and re.search(
                    rf",\s*{other}\s*\)|\.map\(\s*{other}\s*\)", body
                )
                if re.search(rf"(?<![.\w]){other}\(", body) or handed:
                    todo.append(other)
        english = {
            name
            for name, pair in _load("?lang=en")["registry"].items()
            if pair["en"] is not None
        }
        used = set()
        for name in sorted(reached):
            code = _code(found[name])
            with self.subTest(function=name):
                self.assertFalse(CJK.findall(code), name)
            # Identifiers only: a CSS class such as "absence" is not a table.
            bare = re.sub(r'"(?:[^"\\\n]|\\.)*"', '""', code)
            used |= {table for table in tables if re.search(rf"\b{table}\b", bare)}
        self.assertEqual(used - english - IN_LANGUAGE, WITHOUT_ENGLISH)
        # And each exception is read where the reason says, nowhere else.
        runs = _code(found["runs"])
        workspace_branch = runs[
            runs.index('if (mode === "workspace")') : runs.index('if (mode === "real")')
        ]
        self.assertEqual(runs.count("WORKSPACE."), workspace_branch.count("WORKSPACE."))
        users = {name for name in reached if re.search(r"\bACTIONS\b", _code(found[name]))}
        self.assertEqual(users, {"actionSentences"})

    def test_no_sentence_is_written_outside_the_tables(self):
        for name in ("app.js", "dom.js", "i18n.js", "words.js", "vocabulary-en.js"):
            with self.subTest(file=name):
                self.assertFalse(
                    CJK.findall(_code((STATIC / name).read_text(encoding="utf-8")))
                )
        # The switch module keeps its own two tables and names each language in
        # itself; it writes nothing else.
        language = _code((STATIC / "language.js").read_text(encoding="utf-8"))
        registered = _load("")["registry"]["LANGUAGE"]["zh"]
        for text in re.findall(r'"([^"\n]*[一-鿿][^"\n]*)"', language):
            with self.subTest(text=text):
                self.assertTrue(text in registered.values() or text == "中文", text)


class RecordTests(_Loaded):
    def test_every_english_entry_is_in_the_record_the_reviewer_reads(self):
        record = RECORD.read_text(encoding="utf-8")
        self.assertIn("全部未经 BIM 复核", record)
        for name, pair in self.english.items():
            if name == "ACTION_TEXT":
                continue
            for key, text in _flat(pair["en"]):
                with self.subTest(table=name, key=key):
                    self.assertIn(text.replace("|", "\\|"), record)


if __name__ == "__main__":
    unittest.main()
