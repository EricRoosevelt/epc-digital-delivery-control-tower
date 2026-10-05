"""The English interface: a second wording table, never a second page.

What these tests hold, in the order the user requirement states it:

* the language is the viewer's, read when the page loads, Chinese by default,
  and changing it keeps the route — the same run, record and element;
* every English table has the same keys, list lengths and `{placeholders}` as
  the Chinese one, and no Chinese in it;
* where the Pack, the record or this repository's product documents already
  say it in English, the English shown is that text — quoted, not a
  translation of the Chinese gloss — except what to do and what a recheck must
  show: those are reviewed sentences, one obligation per problem type in both
  languages, and the record's route words stay a labelled source, never the
  instruction;
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
#: Chinese characters and the full-width punctuation that would come with them.
CJK_TEXT = re.compile(r"[一-鿿\u3000-\u303f\uff00-\uffef]")

#: The screens drawn in English. Everything else says it is not translated yet.
TRANSLATED = {
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
}

#: Where each translated screen starts in screens.js.
ROOTS = [
    "renderContext",
    "entry",
    "runs",
    "first",
    "firstItem",
    "recheck",
    "recheckItem",
    "recheckItemOf",
    "refusal",
]

#: English tables that are empty by design: the English is the thing itself.
EMPTY_IN_ENGLISH = {
    # An IFC class is shown by its own English name.
    "IFC_CLASS_NAMES",
    # A check's reason is the record's own English.
    "REASON_GLOSSES",
    # A rule's citation is the returned data's own English.
    "CITATION_GLOSSES",
}

#: Tables a translated screen may touch without English, and why. None now:
#: the action sentences have English, so the two languages say the same thing.
WITHOUT_ENGLISH: set[str] = set()

#: Words of the record and the Pack that are not a user's words. None may be
#: in a sentence that tells someone what to do.
INTERNAL_WORDS = re.compile(
    r"Overlay|requirement_key|\bPack\b|\bR-0\d\d|IFCREL|binding|Not a model defect"
)

#: Functions of words.js that word their answer in the chosen language.
IN_LANGUAGE = {"citationProvenance", "disposition", "conditionState", "carryOverReason"}

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
                if name in EMPTY_IN_ENGLISH:
                    self.assertEqual(en, {})
                    continue
                self.assertEqual(_shape(en), _shape(zh))
            zh_strings = dict(_flat(zh))
            for key, text in _flat(en):
                with self.subTest(table=name, key=key):
                    self.assertTrue(text.strip())
                    self.assertFalse(CJK_TEXT.search(text), text)
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



class ActionTests(_Loaded):
    """What to do and what a recheck must show: one obligation, two languages.

    The Chinese sentences are the BIM reviewer's table and, for the uncovered
    asset identity, the product's ruling. The Pack's route words say something
    else for some problem types — for the uncovered chimney, re-run the
    evaluation where the ruling says first confirm whether an asset identity is
    required at all — so English shows the reviewed sentence too, and the route
    words stay in the source fold.
    """

    def _pack_routes(self) -> dict[str, dict]:
        pack = tomllib.loads(PACK.read_text(encoding="utf-8"))
        return {route["resolution_kind"]: route for route in pack["resolution_routes"]}

    def test_every_problem_type_has_a_sentence_pair_in_both_languages(self):
        zh = self.registry["ACTIONS"]["zh"]
        en = self.registry["ACTIONS"]["en"]
        self.assertIsNotNone(en)
        self.assertEqual(set(zh), set(self._pack_routes()))
        self.assertEqual(set(en), set(zh))
        for kind in zh:
            for part in ("action", "recheck"):
                with self.subTest(kind=kind, part=part):
                    self.assertTrue(zh[kind][part].strip())
                    self.assertTrue(en[kind][part].strip())
        self.assertNotIn("ACTION_TEXT", self.registry)

    def test_the_english_action_is_not_the_records_route_words(self):
        routes = self._pack_routes()
        for kind, pair in self.registry["ACTIONS"]["en"].items():
            for part, field in (("action", "next_action"), ("recheck", "recheck_condition")):
                with self.subTest(kind=kind, part=part):
                    self.assertNotEqual(pair[part], routes[kind][field])
                    self.assertNotIn(routes[kind][field][:40], pair[part])
                    self.assertIsNone(INTERNAL_WORDS.search(pair[part]), pair[part])

    def test_the_uncovered_asset_identity_asks_first_whether_it_is_required(self):
        """The case the product owner walked: confirm the obligation, do not re-run."""

        sentence = self.registry["ACTIONS"]["en"]["asset-identity-not-evaluated"]["action"]
        self.assertIn("First confirm whether the project's convention requires", sentence)
        self.assertIn("this does not mean it must have one", sentence)
        self.assertNotIn("re-run", sentence)

    def test_the_screens_read_the_route_words_only_into_the_source_fold(self):
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        found = _functions(screens)
        sentences = _code(found["actionSentences"])
        for word in ("route", "next_action", "recheck_condition", "LANG"):
            with self.subTest(word=word):
                self.assertNotIn(word, sentences)
        self.assertIn("return ACTIONS[kind];", sentences)
        # The item pages: the route words appear below the fold's summary only.
        block = _code(found["actionBlock"])
        fold = block.index("h(\"summary\", {}, ACTION.original)")
        self.assertNotIn('original("next_action")', block[:fold])
        self.assertNotIn('original("recheck_condition")', block[:fold])
        self.assertIn('["next_action", original("next_action")]', block[fold:])
        self.assertIn("missing(ACTION.noSentence)", block[:fold])
        item = _code(found["recheckItem"])
        summary = item.index("RECHECK_ITEM.originalSummary")
        for match in re.finditer("prior_recheck_condition", item):
            with self.subTest(at=match.start()):
                self.assertGreater(match.start(), summary)
        # Of the screens, only these read a route's words; `member` is drawn in
        # Chinese only.
        readers = {
            name
            for name, body in found.items()
            if re.search(r'"(?:prior_)?(?:next_action|recheck_condition)"', _code(body))
        }
        self.assertEqual(readers, {"actionBlock", "recheckItem", "member"})

    def test_the_source_fold_says_it_is_not_an_instruction(self):
        labels = (
            ("ACTION", "original"),
            ("ACTION", "noSentence"),
            ("RECHECK_ITEM", "originalSummary"),
        )
        for language, words in (("en", "not an instruction"), ("zh", "不是操作指令")):
            for table, key in labels:
                with self.subTest(language=language, table=table, key=key):
                    self.assertIn(words, self.registry[table][language][key])


class ScreenTests(unittest.TestCase):
    def test_the_router_draws_only_translated_screens_in_english(self):
        app = (STATIC / "app.js").read_text(encoding="utf-8")
        declared = re.search(r"export const TRANSLATED = new Set\(\[([^\]]*)\]\)", app).group(1)
        self.assertEqual(set(re.findall(r'"([^"]+)"', declared)), TRANSLATED)
        render = _functions(app)["render"]
        self.assertIn(
            'inLanguage("entry") ? screens.entry(workspace) : untranslated(href(), token > 1)',
            render,
        )
        self.assertIn(
            "inLanguage(`runs/${mode}`) ? screens.runs(state)"
            " : untranslated(href(), token > 1)",
            render,
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
        reached, todo = set(), list(ROOTS)
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
                self.assertFalse(CJK_TEXT.findall(code), name)
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

    def test_a_link_to_an_untranslated_page_says_so_before_the_click(self):
        """Record, activity and member pages are Chinese only; the way there says it."""

        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        found = _functions(screens)
        untranslated = re.compile(
            r'href\(state\.mode, state\.runId, "(?:record|member|activity)"'
        )
        sites = 0
        for name in found:
            # The untranslated pages themselves, and the helper only they call.
            if name in ("record", "activity", "member", "locate"):
                continue
            body = _code(found[name])
            for match in untranslated.finditer(body):
                sites += 1
                # The note follows the link inside the same paragraph.
                with self.subTest(screen=name, at=match.start()):
                    self.assertIn("FIRST.notRevised", body[match.start() : match.start() + 200])
        self.assertEqual(sites, 4)
        english = _load("?lang=en")["registry"]
        self.assertIn("Chinese only", english["FIRST"]["en"]["notRevised"])
        # And the page they reach offers the way back, not only the way home.
        language = (STATIC / "language.js").read_text(encoding="utf-8")
        page = language[language.index("export function untranslated(") :]
        self.assertIn("history.back()", page)
        self.assertIn("WORDS.back", page)
        # Only when there is a page inside the preview to go back to: one opened
        # directly has none, and going back would leave the preview.
        self.assertIn("canGoBack\n        ? [", page)
        app = (STATIC / "app.js").read_text(encoding="utf-8")
        self.assertEqual(app.count("untranslated(href(), token > 1)"), 3)
        self.assertNotIn("untranslated(href())", app)

    def test_no_sentence_is_written_outside_the_tables(self):
        for name in (
            "app.js",
            "dom.js",
            "i18n.js",
            "words.js",
            "vocabulary-en.js",
            "recheck-model.js",
        ):
            with self.subTest(file=name):
                code = _code((STATIC / name).read_text(encoding="utf-8"))
                self.assertFalse(CJK_TEXT.findall(code))
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
            for key, text in _flat(pair["en"]):
                with self.subTest(table=name, key=key):
                    self.assertIn(text.replace("|", "\\|"), record)


_MODEL_DRIVER = """
import { readFileSync } from "node:fs";
globalThis.location = { search: process.argv[2] };
const { firstCheckModel } = await import("./first-check-model.js");
const { recheckModel } = await import("./recheck-model.js");
const documents = JSON.parse(readFileSync(0, "utf8"));
const out = {};
for (const [name, document] of Object.entries(documents)) {
  out[name] = {
    recheck: recheckModel(document),
    first: document.successor ? null : firstCheckModel(document),
  };
}
process.stdout.write(JSON.stringify(out));
"""


def _models(documents: dict, search: str) -> dict:
    node = shutil.which("node")
    if node is None:
        raise unittest.SkipTest("node is not on PATH")
    with tempfile.TemporaryDirectory() as directory:
        workdir = Path(directory)
        for path in STATIC.glob("*.js"):
            shutil.copyfile(path, workdir / path.name)
        (workdir / "package.json").write_text('{"type": "module"}\n', encoding="utf-8")
        (workdir / "driver.mjs").write_text(_MODEL_DRIVER, encoding="utf-8")
        completed = subprocess.run(
            [node, "driver.mjs", search],
            cwd=workdir,
            input=json.dumps(documents).encode("utf-8"),
            capture_output=True,
            check=False,
        )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return json.loads(completed.stdout.decode("utf-8"))


class SameRecordTests(unittest.TestCase):
    """Every adapter scenario and recheck case, modelled in both languages."""

    @classmethod
    def setUpClass(cls):
        import sys

        sys.path.insert(0, str(PROJECT_ROOT / "tests"))
        from doctor_recheck_cases import recheck_cases
        from internal.doctor_adapter import scenario_envelope, scenario_index

        documents = {
            name: envelope["record"] for name, envelope in dict(recheck_cases()).items()
        }
        for item in scenario_index():
            envelope = scenario_envelope(item["name"])
            if envelope.get("outcome") == "record":
                documents[f"adapter:{item['name']}"] = envelope["record"]
        cls.documents = documents
        cls.zh = _models(documents, "")
        cls.en = _models(documents, "?lang=en")

    def _compare(self, zh, en, path, record=()):
        if isinstance(zh, dict):
            self.assertIsInstance(en, dict, path)
            self.assertEqual(list(zh), list(en), path)
            for key in zh:
                self._compare(zh[key], en[key], f"{path}.{key}", record)
        elif isinstance(zh, list):
            self.assertIsInstance(en, list, path)
            self.assertEqual(len(zh), len(en), path)
            for index, (left, right) in enumerate(zip(zh, en)):
                self._compare(left, right, f"{path}[{index}]", record)
        elif isinstance(zh, str):
            self.assertIsInstance(en, str, path)
            # The record's own values are shown as they came, whatever their
            # language (the test cases name roles in Chinese); the words
            # around them are not.
            for value in record:
                en = en.replace(value, "")
            self.assertFalse(CJK_TEXT.search(en), f"{path}: {en}")
        else:
            # A count, a flag, a missing value: the same in both languages.
            self.assertEqual(zh, en, path)

    def test_the_same_record_gives_the_same_model_in_both_languages(self):
        """Counts, codes, groupings and every flag agree; only the words differ."""

        self.assertGreater(len(self.documents), 10)
        for name, document in self.documents.items():
            record = sorted(
                {text for _, text in _flat(document) if CJK_TEXT.search(text)},
                key=len,
                reverse=True,
            )
            with self.subTest(document=name):
                self._compare(self.zh[name], self.en[name], name, record)

    def test_codes_are_the_same_codes(self):
        """A string that is a record code in Chinese is the same code in English."""

        def codes(value, path=""):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key in ("code", "kind", "name", "activity", "verdict", "state"):
                        if isinstance(item, str):
                            yield f"{path}.{key}", item
                    yield from codes(item, f"{path}.{key}")
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    yield from codes(item, f"{path}[{index}]")

        for name in self.documents:
            with self.subTest(document=name):
                self.assertEqual(dict(codes(self.zh[name])), dict(codes(self.en[name])))


_WORKSPACE_DRIVER = """
import { readFileSync } from "node:fs";
globalThis.location = { search: process.argv[2] };
const model = await import("./workspace-model.js");
const envelopes = JSON.parse(readFileSync(0, "utf8"));
const out = {};
for (const [name, envelope] of Object.entries(envelopes)) {
  if (envelope.outcome !== "validation") continue;
  const requirements = Object.values(envelope.requirements);
  out[name] = {
    groups: model.statusGroups(envelope.findings).map((group) => ({
      status: group.status,
      known: group.known,
      count: group.count,
      keys: group.findings.map((finding) => finding.finding_key),
    })),
    notes: requirements.map((one) => model.ruleNotes(envelope.run, one) !== null),
    productValidation: requirements.map((one) => model.isProductValidation(one)),
    freeText: envelope.findings.map((finding) => model.quotesFreeText(finding.reason)),
    transitions: envelope.comparison ? model.transitions(envelope.comparison) : null,
    placed: envelope.comparison
      ? envelope.findings.map(
          (finding) => model.comparisonOf(envelope.comparison, finding.finding_key).kind,
        )
      : null,
  };
}
process.stdout.write(JSON.stringify(out));
"""


class WorkspaceTests(unittest.TestCase):
    """The workspace pages: one real check, its comparison, a refused comparison."""

    def test_the_workspace_modules_read_words_through_words_js(self):
        english = {
            name
            for name, pair in _load("?lang=en")["registry"].items()
            if pair["en"] is not None
        }
        for name in ("workspace-screens.js", "workspace-model.js"):
            source = (STATIC / name).read_text(encoding="utf-8")
            with self.subTest(file=name):
                self.assertNotIn('from "./vocabulary.js"', source)
                imported = re.search(r'import \{([^}]*)\} from "\./words\.js"', source).group(1)
                tables = {item.strip() for item in imported.split(",") if item.strip()}
                self.assertEqual(tables - english, set())
                self.assertFalse(CJK_TEXT.findall(_code(source)))

    def test_the_rule_notes_quote_the_rule_where_it_speaks_english(self):
        rule = tomllib.loads(
            (PROJECT_ROOT / "rules" / "product-validation" / "PV-001.toml").read_text(
                encoding="utf-8"
            )
        )
        notes = _load("?lang=en")["registry"]["RULE_NOTES"]["en"]["PV-001"]
        self.assertEqual(notes["title"], rule["title"])
        instruction = rule["requirements"][0]["instructions"]
        # "Declare DIFFUSER, GRILLE, LOUVRE or REGISTER. NOTDEFINED states nothing."
        self.assertTrue(notes["action"]["what"].endswith(instruction.split(". ", 1)[1]))

    def test_the_same_run_gives_the_same_model_in_both_languages(self):
        """Groups, transitions, pairing and which notes apply do not depend on the language."""

        import sys

        sys.path.insert(0, str(PROJECT_ROOT / "tests"))
        from internal.doctor_adapter import workspace_envelope
        from test_doctor_workspace import _runs

        runs = _runs()
        envelopes = {
            "compared": workspace_envelope(runs.after, runs.before),
            "swapped": workspace_envelope(runs.before, runs.after),
            "single": workspace_envelope(runs.after),
            "refused": workspace_envelope(runs.before, runs.shipped_rules),
        }
        node = shutil.which("node")
        if node is None:
            raise unittest.SkipTest("node is not on PATH")
        outputs = {}
        for search in ("", "?lang=en"):
            with tempfile.TemporaryDirectory() as directory:
                workdir = Path(directory)
                for path in STATIC.glob("*.js"):
                    shutil.copyfile(path, workdir / path.name)
                (workdir / "package.json").write_text('{"type": "module"}\n', encoding="utf-8")
                (workdir / "driver.mjs").write_text(_WORKSPACE_DRIVER, encoding="utf-8")
                completed = subprocess.run(
                    [node, "driver.mjs", search],
                    cwd=workdir,
                    input=json.dumps(envelopes).encode("utf-8"),
                    capture_output=True,
                    check=False,
                )
            if completed.returncode != 0:
                raise AssertionError(completed.stderr.decode("utf-8", "replace"))
            outputs[search] = json.loads(completed.stdout.decode("utf-8"))
        self.assertEqual(set(outputs[""]), {"compared", "swapped", "single"})
        self.assertEqual(outputs[""], outputs["?lang=en"])


if __name__ == "__main__":
    unittest.main()
