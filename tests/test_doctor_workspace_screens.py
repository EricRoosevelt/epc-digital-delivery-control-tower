"""What the Doctor's workspace pages say about one real check and its comparison.

The pages read ``doctor/static/workspace-model.js``, which has no DOM in it, so
these tests run it under Node over envelopes the adapter really returns: every
workspace here is a real ``epc-ct run`` over the public sample models, made by
``test_doctor_workspace``'s own helpers. Nothing private is involved.

Four promises are pinned:

* **the pages count and arrange; they do not compare** — the groups of pairs are
  the adapter's pairs, every one of them and nothing else; the rows only one run
  has are counted apart; which run is "earlier" is whatever the server was told;
* **no handover judgement and no mending words** — the result words are the
  check's own three, and no sentence written for these pages says a thing was
  fixed, resolved or improved, or uses a handover verdict word;
* **a pass says what it proves and what it does not, and never what it read** —
  the rule's notes are shown only under the rule set version they were written
  for, and say the four things a pass does not prove;
* **every new sentence is in the vocabulary**, and the readable vocabulary under
  ``docs/product`` holds it.

They do not prove a manager can read the pages; that is a walkthrough, done by a
person.
"""

from __future__ import annotations

import copy
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from helpers import PROJECT_ROOT
from internal.doctor_adapter import workspace_envelope
from internal.doctor_adapter.workspace import REFUSAL_CODES
from test_doctor_workspace import _runs

STATIC = PROJECT_ROOT / "doctor" / "static"
VOCABULARY_DOC = PROJECT_ROOT / "docs" / "product" / "2026-10-02-doctor-recheck-vocabulary.md"

#: The vocabulary tables written for the workspace pages.
WORKSPACE_TABLES = (
    "WORKSPACE_HOME",
    "WORKSPACE",
    "TAG_WORDS",
    "CITATION_GLOSSES",
    "RULE_NOTES",
    "WORKSPACE_COMPARE",
    "WORKSPACE_REFUSAL",
    "WORKSPACE_REFUSAL_REASONS",
    "ENVELOPE_WORDS",
)

_DRIVER = """
import { readFileSync } from "node:fs";
import * as model from "./workspace-model.js";
import * as vocabulary from "./vocabulary.js";

const input = JSON.parse(readFileSync(0, "utf8"));
const out = {};
for (const [name, envelope] of Object.entries(input.envelopes)) {
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
    transitions: envelope.comparison ? model.transitions(envelope.comparison) : null,
    placed: envelope.comparison
      ? envelope.findings.map(
          (finding) => model.comparisonOf(envelope.comparison, finding.finding_key).kind,
        )
      : null,
    changes: envelope.comparison
      ? (({ changed, unchanged }) => ({
          changed: changed.map((entry) => entry.row.model_key),
          unchanged: unchanged.map((entry) => entry.model_key),
        }))(model.modelChanges(envelope.comparison, envelope.run))
      : null,
  };
}
const tags = input.tags.map(([element, model_]) => model.tagReading(element, model_));
const freeText = input.reasons.map((reason) => model.quotesFreeText(reason));
const tables = {};
for (const name of input.tables) tables[name] = vocabulary[name];
process.stdout.write(
  JSON.stringify({
    out,
    tags,
    freeText,
    tables,
    findingStatus: vocabulary.FINDING_STATUS,
    reasonGlosses: vocabulary.REASON_GLOSSES,
    ruleNotesFor: vocabulary.RULE_NOTES_FOR,
    demoNotice: vocabulary.DEMO_NOTICE,
    consequenceKinds: vocabulary.CONSEQUENCE_KINDS,
    modeLabels: vocabulary.MODE_LABELS,
  }),
);
"""


#: Reasons and whether each quotes a USERDEFINED type's free text. The public
#: sample's two air terminals give the second; the first is the private case's.
FREE_TEXT_CASES = (
    ('The predefined type "NOTDEFINED" does not meet the required type', False),
    ('The predefined type "chimney cover" does not meet the required type', True),
    ('The predefined type "louvre" does not meet the required type', True),
    ('The predefined type "USERDEFINED" does not meet the required type', False),
    ("Requirement satisfied.", False),
    ("No applicable elements exist in this model.", False),
)


def _node(payload: dict[str, object]) -> dict[str, object]:
    node = shutil.which("node")
    if node is None:
        message = "node is not on PATH; the workspace pages cannot be exercised"
        if os.environ.get("CI"):
            raise AssertionError(message)
        raise unittest.SkipTest(message)
    with tempfile.TemporaryDirectory() as directory:
        workdir = Path(directory)
        # The model reads its words through words.js, in Chinese here.
        for name in (
            "workspace-model.js",
            "vocabulary.js",
            "vocabulary-en.js",
            "words.js",
            "i18n.js",
        ):
            shutil.copyfile(STATIC / name, workdir / name)
        (workdir / "package.json").write_text('{"type": "module"}\n', encoding="utf-8")
        (workdir / "driver.js").write_text(_DRIVER, encoding="utf-8")
        completed = subprocess.run(
            [node, "driver.js"],
            cwd=workdir,
            input=json.dumps(payload).encode("utf-8"),
            capture_output=True,
            check=False,
        )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return json.loads(completed.stdout.decode("utf-8"))


def _strings(value) -> list[str]:
    """Every string in a vocabulary table, keys excluded."""

    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    return []


def _other_version(envelope):
    changed = copy.deepcopy(envelope)
    changed["run"]["ruleset"]["version"] = "1.1"
    return changed


def _without_label(envelope):
    changed = copy.deepcopy(envelope)
    for requirement in changed["requirements"].values():
        requirement["labels"] = [
            label for label in requirement["labels"] if label != "ProductValidation"
        ]
    return changed


class _Modelled(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runs = _runs()
        cls.envelopes = {
            "compared": workspace_envelope(runs.after, runs.before),
            "swapped": workspace_envelope(runs.before, runs.after),
            "removed": workspace_envelope(runs.removed, runs.before),
            "added": workspace_envelope(runs.before, runs.removed),
            "single": workspace_envelope(runs.after),
            "refused": workspace_envelope(runs.before, runs.shipped_rules),
        }
        cls.envelopes["other-version"] = _other_version(cls.envelopes["single"])
        cls.envelopes["no-label"] = _without_label(cls.envelopes["single"])
        cls.tag_cases = [
            [{"name": "a", "tag": "101"}, {"tag_source": "model-file"}],
            [{"name": "a"}, {"tag_source": "model-file"}],
            [{"name": "a"}, {"tag_source": "model-file-not-located"}],
            [{"name": "a"}, {"tag_source": "model-file-differs"}],
            [{"name": "a"}, {}],
            [None, {"tag_source": "model-file"}],
        ]
        cls.output = _node(
            {
                "envelopes": cls.envelopes,
                "tags": cls.tag_cases,
                "tables": [*WORKSPACE_TABLES, "HOME", "REASON_GLOSSES"],
                "reasons": [reason for reason, _ in FREE_TEXT_CASES],
            }
        )
        cls.out = cls.output["out"]
        cls.tables = cls.output["tables"]


class CountsAreTheRunsOwnTests(_Modelled):
    def test_every_finding_is_in_exactly_one_status_group(self):
        for name, envelope in self.envelopes.items():
            if envelope["outcome"] != "validation":
                continue
            with self.subTest(envelope=name):
                groups = self.out[name]["groups"]
                self.assertEqual(
                    {group["status"]: group["count"] for group in groups},
                    dict(Counter(finding["status"] for finding in envelope["findings"])),
                )
                listed = [key for group in groups for key in group["keys"]]
                self.assertEqual(
                    sorted(listed), sorted(f["finding_key"] for f in envelope["findings"])
                )
                order = list(self.output["findingStatus"])
                ranks = [order.index(group["status"]) for group in groups]
                self.assertEqual(ranks, sorted(ranks))

    def test_the_result_words_are_the_checks_own_three(self):
        self.assertEqual(
            self.output["findingStatus"], {"FAIL": "不通过", "PASS": "通过", "N/A": "不适用"}
        )
        for name, envelope in self.envelopes.items():
            for finding in envelope.get("findings", []):
                with self.subTest(envelope=name, status=finding["status"]):
                    self.assertIn(finding["status"], self.output["findingStatus"])


class ThePagesDoNotCompareTests(_Modelled):
    def test_the_groups_are_the_adapters_pairs_and_nothing_else(self):
        for name, envelope in self.envelopes.items():
            if "comparison" not in envelope:
                continue
            comparison = envelope["comparison"]
            moved = self.out[name]["transitions"]
            with self.subTest(envelope=name):
                counted = Counter()
                for group in moved["differing"] + moved["same"]:
                    self.assertEqual(group["differs"], group["prior"] != group["current"])
                    counted[(group["prior"], group["current"])] += len(group["pairs"])
                    self.assertTrue(group["pairs"])
                    for pair in group["pairs"]:
                        self.assertIn(pair, comparison["pairs"])
                self.assertEqual(
                    counted,
                    Counter(
                        (p["prior"]["status"], p["current"]["status"])
                        for p in comparison["pairs"]
                    ),
                )
                self.assertEqual(moved["pairCount"], len(comparison["pairs"]))
                self.assertEqual(
                    moved["differingCount"] + moved["sameCount"], len(comparison["pairs"])
                )
                # Rows one run has are counted apart and never inside a group.
                self.assertEqual(
                    moved["notReEvaluatedCount"], len(comparison["not_re_evaluated"])
                )
                self.assertEqual(
                    moved["newlyAppearingCount"], len(comparison["newly_appearing"])
                )

    def test_a_row_only_one_run_has_is_never_a_pair(self):
        removed = self.out["removed"]["transitions"]
        self.assertGreater(removed["notReEvaluatedCount"], 0)
        added = self.out["added"]
        self.assertGreater(added["transitions"]["newlyAppearingCount"], 0)
        # Each current finding is placed where the adapter placed it.
        envelope = self.envelopes["added"]
        newly = {
            row["current"]["finding_key"] for row in envelope["comparison"]["newly_appearing"]
        }
        for finding, kind in zip(envelope["findings"], added["placed"], strict=True):
            with self.subTest(finding=finding["finding_key"]):
                self.assertEqual(kind, "newly" if finding["finding_key"] in newly else "pair")

    def test_which_run_is_earlier_is_the_callers_word(self):
        def moved(name):
            return {
                (group["prior"], group["current"])
                for group in self.out[name]["transitions"]["differing"]
            }

        self.assertEqual(moved("compared"), {("FAIL", "PASS")})
        self.assertEqual(moved("swapped"), {("PASS", "FAIL")})

    def test_the_changed_models_are_the_adapters_list(self):
        for name in ("compared", "swapped"):
            envelope = self.envelopes[name]
            with self.subTest(envelope=name):
                changes = self.out[name]["changes"]
                self.assertEqual(
                    changes["changed"],
                    [row["model_key"] for row in envelope["comparison"]["changed_models"]],
                )
                self.assertEqual(
                    sorted(changes["changed"] + changes["unchanged"]),
                    sorted(model["model_key"] for model in envelope["run"]["models"]),
                )

    def test_no_screen_pairs_two_findings_itself(self):
        """The pairs are read in exactly one place, and the screens use what it returns."""

        section = (STATIC / "workspace-screens.js").read_text(encoding="utf-8")
        model = (STATIC / "workspace-model.js").read_text(encoding="utf-8")
        self.assertNotIn("comparison.pairs", section)
        self.assertIn("comparison.pairs", model)
        for verdict in ("verdictLabel", "workVerdict", "VERDICT_LABELS", "VERDICT_WORDS"):
            with self.subTest(verdict=verdict):
                self.assertNotIn(verdict, section)
        # The model compares two statuses only to put a pair in a group.
        self.assertEqual(model.count("pair.prior.status !== pair.current.status"), 1)


class RuleNotesTests(_Modelled):
    def test_the_notes_hold_for_their_rule_set_version_only(self):
        self.assertEqual(
            self.output["ruleNotesFor"], {"ruleset": "product-validation", "version": "1.0"}
        )
        self.assertEqual(self.out["single"]["notes"], [True])
        self.assertEqual(self.out["other-version"]["notes"], [False])

    def test_product_validation_is_read_off_the_labels(self):
        self.assertEqual(self.out["single"]["productValidation"], [True])
        self.assertEqual(self.out["no-label"]["productValidation"], [False])

    def test_a_pass_says_what_it_does_not_prove(self):
        notes = self.tables["RULE_NOTES"]["PV-001"]
        said = "".join(notes["passDoesNotProve"])
        for limit in ("取值正确", "写成 GRILLE 也会通过", "洞口", "对齐", "任何工作可以开始"):
            with self.subTest(limit=limit):
                self.assertIn(limit, said)
        # W3: what a pass proves is the predicate, read where the checker reads.
        self.assertIn("四个值之一", notes["passProves"])
        self.assertIn("逐字等于", notes["passProves"])
        # A pass shows no "检查器读哪里" row (only a failure does), so the pass
        # says the reading order itself rather than pointing at that row.
        self.assertNotIn("检查器读哪里", notes["passProves"])
        self.assertIn("类型什么也没说时才读构件实例", notes["passProves"])
        # A type and an instance that disagree still pass, as measured with
        # IfcTester: type LOUVRE, instance DIFFUSER -> PASS.
        self.assertIn("类型是 LOUVRE、实例是 DIFFUSER，也会通过", said)
        # USERDEFINED's text is compared exactly, case and spaces included, as
        # measured: "LOUVRE" passes; "louvre", "Louvre", " LOUVRE", "LOUVRE " fail.
        for boundary in (
            "USERDEFINED",
            "自由文本",
            "逐字、区分大小写",
            "louvre、Louvre 或前后带空格则不通过",
        ):
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, said)
        self.assertNotIn("userDefined", notes)

    def test_no_sentence_says_what_a_pass_read(self):
        """A passing finding carries no observed value, so no page says one."""

        for envelope in self.envelopes.values():
            for finding in envelope.get("findings", []):
                if finding["status"] == "PASS":
                    self.assertEqual(finding["actual"], "")
        for name in WORKSPACE_TABLES:
            for text in _strings(self.tables[name]):
                with self.subTest(table=name, text=text):
                    self.assertNotRegex(text, r"读到的是|读到了 ?[A-Z]|通过时读到")
        self.assertIn("不带它读到的值", self.tables["WORKSPACE"]["passNoValue"])

    def test_a_pass_and_a_not_applicable_are_glossed_and_a_failure_shown_as_it_came(self):
        """Glosses are exact matches; a reason without one is shown alone, as written.

        The public sample's two air terminals are ``USERDEFINED`` with free text,
        and the checker compares that text: their reasons quote it ("chimney
        cover"), which is the checker behaviour the rule notes warn about.
        """

        glosses = self.output["reasonGlosses"]
        seen = Counter()
        for envelope in self.envelopes.values():
            for finding in envelope.get("findings", []):
                seen[finding["status"]] += 1
                if finding["status"] in ("PASS", "N/A"):
                    with self.subTest(reason=finding["reason"]):
                        self.assertIn(finding["reason"], glosses)
        self.assertTrue(seen["PASS"] and seen["N/A"] and seen["FAIL"])
        self.assertIn(
            'The predefined type "NOTDEFINED" does not meet the required type', glosses
        )


class TagTests(_Modelled):
    def test_the_tag_is_shown_or_its_absence_is_said_from_tag_source(self):
        self.assertEqual(
            self.output["tags"],
            [
                {"kind": "tag", "value": "101"},
                {"kind": "source", "value": "model-file"},
                {"kind": "source", "value": "model-file-not-located"},
                {"kind": "source", "value": "model-file-differs"},
                {"kind": "not-carried"},
                {"kind": "model-level"},
            ],
        )
        words = self.tables["TAG_WORDS"]
        source = (PROJECT_ROOT / "internal" / "doctor_adapter" / "workspace.py").read_text(
            encoding="utf-8"
        )
        emitted = set(re.findall(r'tag_source"\] = "([\w-]+)"', source))
        self.assertEqual(
            emitted, {"model-file", "model-file-not-located", "model-file-differs"}
        )
        self.assertEqual(set(words["sources"]), emitted)
        self.assertTrue(emitted <= set(words["short"]))
        self.assertIn("ElementId", words["note"])
        # The page cannot know how far the Tag-to-ElementId match was checked in
        # any one project, so it never says, nor calls it reliable or not; it
        # gives the check a person can do every time.
        for step in ("按 ID 选择", "名称和类别", "不要按这个 Tag 去改"):
            with self.subTest(step=step):
                self.assertIn(step, words["note"])
        self.assertNotRegex(words["note"], r"核对过|个别对象|可靠")

    def test_the_storey_is_said_to_be_the_ifcs_and_an_object_is_found_by_id(self):
        """W5: the storey shown is the IFC's; Revit is searched by ID, never by level.

        That one case's schedule levels were empty is not said of every model.
        """

        workspace = self.tables["WORKSPACE"]
        self.assertEqual(workspace["columns"]["storey"], "楼层（IFC）")
        self.assertEqual(workspace["element"]["storey"], "楼层（IFC）")
        said = self.tables["TAG_WORDS"]["byIdNotStorey"]
        for words in ("按 ID 找对象", "不要按楼层找", "IFC 文件", "不一定"):
            with self.subTest(words=words):
                self.assertIn(words, said)
        for name in WORKSPACE_TABLES:
            for text in _strings(self.tables[name]):
                with self.subTest(table=name, text=text):
                    self.assertNotRegex(text, r"标高为空|没有标高")
        screens = (STATIC / "workspace-screens.js").read_text(encoding="utf-8")
        locate = screens[
            screens.index("function locateBlock(") : screens.index("function passBlock(")
        ]
        # "Find it by ID" only beside an ID: without a Tag the page has none.
        self.assertIn(
            'tag.kind === "tag" ? TAG_WORDS.byIdNotStorey : TAG_WORDS.storeyFromIfc', locate
        )
        without = self.tables["TAG_WORDS"]["storeyFromIfc"]
        self.assertIn("IFC 文件", without)
        self.assertNotIn("按 ID", without)
        self.assertIn("IFC Tag", self.tables["WORKSPACE"]["columns"]["tag"])


class WordingTests(_Modelled):
    def test_no_mending_and_no_handover_verdict_on_these_pages(self):
        for name in WORKSPACE_TABLES:
            for text in _strings(self.tables[name]):
                with self.subTest(table=name, text=text):
                    self.assertNotRegex(text, r"修复|修好|解决|改善|受阻|无法判断")

    def test_the_pages_say_there_is_no_handover_judgement(self):
        workspace = self.tables["WORKSPACE"]
        self.assertIn("不是交接判断", workspace["noJudgement"])
        self.assertIn("没有交接判断", workspace["contextNoJudgement"])
        self.assertIn("没有交接判断", self.tables["WORKSPACE_HOME"]["body"])

    def test_both_run_ids_are_named_and_which_was_called_earlier(self):
        compare = self.tables["WORKSPACE_COMPARE"]
        self.assertIn("--prior", compare["prior"])
        self.assertIn("--workspace", compare["current"])
        self.assertIn("不能证明先后", compare["order"])

    def test_the_two_models_are_named_by_what_they_hold(self):
        """No "两侧": a side is the model holding the air terminal or the wall.

        A discipline name could only come from the returned data's declared
        `discipline`, never from a model identifier, and no sentence here needs
        one.
        """

        for name in WORKSPACE_TABLES:
            for text in _strings(self.tables[name]):
                with self.subTest(table=name, text=text):
                    self.assertNotIn("两侧", text)
        notes = self.tables["RULE_NOTES"]["PV-001"]
        said = "".join([*notes["passDoesNotProve"], *notes["gaps"]])
        self.assertIn("风口所在的模型", said)
        self.assertIn("风口所在的墙", said)
        # The wall an air terminal sits in may be an internal one (BIM W1), and
        # the two models may have one holder or two: neither is presumed.
        for text in _strings(notes):
            with self.subTest(text=text):
                self.assertNotIn("外墙", text)
                self.assertNotIn("持有方", text)

    def test_where_the_checker_reads_is_not_where_revit_is_changed(self):
        """W6: two rows; no type is required and no parameter mapping is invented."""

        action = self.tables["RULE_NOTES"]["PV-001"]["action"]
        self.assertEqual(set(action), {"what", "reads", "revise", "undecided"})
        self.assertIn("不是 Revit 里该改的位置", action["reads"])
        self.assertIn("返回数据没有记录，本页不指定", action["revise"])
        self.assertIn("如果决定在类型上改", action["revise"])
        self.assertNotRegex(action["revise"], r"IfcExportAs|必须|应当在类型")
        workspace = self.tables["WORKSPACE"]
        self.assertEqual(workspace["actionReads"], "检查器读哪里")
        self.assertEqual(workspace["actionRevise"], "在 Revit 里改哪里")
        self.assertNotIn("actionWhere", workspace)

    def test_a_failed_product_validation_rule_is_not_a_project_defect(self):
        """W2: said beside a failure, only when the labels say product validation."""

        self.assertIn("不等于原项目的交付缺陷", self.tables["WORKSPACE"]["failNotDefect"])
        screens = (STATIC / "workspace-screens.js").read_text(encoding="utf-8")
        self.assertEqual(screens.count("WORKSPACE.failNotDefect"), 1)
        self.assertIn(
            'status === "FAIL" && isProductValidation(requirement)\n'
            '        ? h("p", { class: "beside" }, WORKSPACE.failNotDefect)',
            screens,
        )
        for other in ("screens.js", "app.js"):
            with self.subTest(file=other):
                self.assertNotIn("failNotDefect", (STATIC / other).read_text(encoding="utf-8"))

    def test_the_reason_gloss_and_a_free_text_reason(self):
        """W7: the gloss says "not one of the required values"; free text gets a note."""

        glosses = self.tables["REASON_GLOSSES"]
        self.assertEqual(
            glosses['The predefined type "NOTDEFINED" does not meet the required type'],
            "预定义类型“NOTDEFINED”不属于要求的取值",
        )
        self.assertEqual(self.output["freeText"], [expected for _, expected in FREE_TEXT_CASES])
        self.assertIn("自由文本", self.tables["RULE_NOTES"]["PV-001"]["reasonFreeText"])
        screens = (STATIC / "workspace-screens.js").read_text(encoding="utf-8")
        self.assertEqual(screens.count("(text) => reasonText(text, notes)"), 3)

    def test_what_to_change_starts_from_the_revit_source(self):
        """The change is made in Revit and exported; no parameter mechanism is named."""

        what = self.tables["RULE_NOTES"]["PV-001"]["action"]["what"]
        self.assertTrue(what.startswith("回到 Revit 源模型"), what)
        self.assertIn("重新导出", what)
        self.assertNotIn("在 IFC 里", what)
        self.assertNotIn("参数", what)

    def test_the_home_says_what_it_offers_when_a_workspace_is_named(self):
        home = self.tables["HOME"]
        self.assertIn("尚不能导入自己的 Revit 模型", home["status"])
        with_workspace = home["statusWithWorkspace"]
        for said in ("同时提供", "真实检查", "模拟示例", "整体合规或可施工结论"):
            with self.subTest(said=said):
                self.assertIn(said, with_workspace)
        self.assertNotIn("示例预览", with_workspace)
        # A question that failed is said as such: not "examples only".
        unknown = home["statusWorkspaceUnknown"]
        for said in ("未能确认", "不等于没有工作区"):
            with self.subTest(said=said):
                self.assertIn(said, unknown)
        self.assertNotIn("示例预览", unknown)
        self.assertIn("不等于没有工作区", self.tables["WORKSPACE_HOME"]["unknown"])
        # Viewing a finished workspace is not choosing a model on the page.
        self.assertIn("在页面上导入、选择或更换模型", home["cannot"][0])
        self.assertIn("不能在页面上选择或更换模型", self.tables["WORKSPACE_HOME"]["body"])
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        entry = screens[screens.index("function entry(") : screens.index("function runLink(")]
        self.assertIn(
            "workspaceRun\n        ? HOME.statusWithWorkspace\n"
            '        : carries(workspace, "error")\n          ? HOME.statusWorkspaceUnknown\n'
            "          : HOME.status",
            entry,
        )

    def test_every_refusal_code_has_words(self):
        self.assertEqual(set(self.tables["WORKSPACE_REFUSAL_REASONS"]), set(REFUSAL_CODES))
        reasons = self.envelopes["refused"]["refusal"]["reasons"]
        self.assertTrue(reasons)

    def test_the_two_wordings_product_left_for_the_next_change(self):
        for notice in (self.output["demoNotice"],):
            with self.subTest(notice=notice):
                self.assertIn(
                    "包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定",
                    notice,
                )
        consequence = self.output["consequenceKinds"]["re-identification-and-reissue-risk"]
        self.assertEqual(consequence, "有重新标识的风险：引用这些标识的文件届时也须重新出具")
        self.assertNotIn("更新", consequence)

    def test_the_workspace_screens_write_no_sentence_of_their_own(self):
        """Every Chinese word on these pages comes from vocabulary.js."""

        section = (STATIC / "workspace-screens.js").read_text(encoding="utf-8")
        code_lines = [
            line.split("//")[0]
            for line in section.splitlines()
            if not line.lstrip().startswith(("//", "*", "/*"))
        ]
        # Not even the back button: it reads CONTEXT.home now, and no
        # full-width punctuation is written here either.
        written = set(re.findall(r"[一-鿿\u3000-\u303f\uff00-\uffef]+", "\n".join(code_lines)))
        self.assertEqual(written, set())
        app = (STATIC / "app.js").read_text(encoding="utf-8")
        problem = app[
            app.index("function workspaceProblem") : app.index(
                "// What is wrong with an envelope"
            )
        ]
        self.assertEqual(set(re.findall(r"[一-鿿]+", problem)) - {"未识别的"}, set())

    def test_every_workspace_sentence_is_in_the_readable_vocabulary(self):
        text = VOCABULARY_DOC.read_text(encoding="utf-8")
        for name in WORKSPACE_TABLES:
            for sentence in _strings(self.tables[name]):
                with self.subTest(table=name, sentence=sentence):
                    self.assertIn(sentence, text)
        self.assertIn(self.output["modeLabels"]["workspace"], text)


class NothingElseMovedTests(unittest.TestCase):
    def test_the_refused_envelope_carries_only_the_refusal(self):
        envelope = workspace_envelope(_runs().before, _runs().shipped_rules)
        self.assertEqual(list(envelope), ["mode", "outcome", "refusal"])
        self.assertIsInstance(envelope["refusal"]["reasons"], list)


if __name__ == "__main__":
    unittest.main()
