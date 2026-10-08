"""What the Doctor recheck screens say, for every state the record can hold.

The screens' wording lives in ``doctor/static/recheck-model.js``, which has no
DOM in it, so it runs under Node exactly as the browser runs it. These tests
hand it recheck envelopes and read back the sentences. They pin three things:

* **the page consumes and does not recompute** — the four states, their
  reasons, the changed aspects and "which side was re-issued" are looked up from
  the record, and a value the page does not know is shown as it came;
* **the sentences that must not be misread** — equivalent is not "no review
  needed", a missing member or a missing counterpart is not "fixed", a re-issue
  is not a repair, "only the model version changed" is not "the result changed",
  and "cannot compare" is not "evidence missing";
* **the vocabulary matches the Framework's** — every state, reason, aspect,
  disposition and condition status the record types admit has words here.

They do not prove a manager can read the page. That is the walkthrough in
``docs/product/2026-10-02-doctor-recheck-walkthrough.md``, done by a person.

Node is the one tool these need that the suite does not install. Without it the
module skips with a reason; under continuous integration (``CI`` set, where the
hosted runners ship Node) a missing Node is a failure, because a gate that
disappears with its tool is not a gate.
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

from doctor_recheck_cases import HANDOVER, REISSUE_SIDES, recheck_cases
from helpers import PROJECT_ROOT

from epc_control_tower.purpose.assessment import record

STATIC = PROJECT_ROOT / "doctor" / "static"

_DRIVER = """
import { readFileSync } from "node:fs";
import { firstCheckModel, recordCitations } from "./first-check-model.js";
import { recheckModel } from "./recheck-model.js";
import * as vocabulary from "./vocabulary.js";

const cases = JSON.parse(readFileSync(0, "utf8"));
const models = {};
const first = {};
const citations = {};
for (const [name, document] of Object.entries(cases)) {
  models[name] = recheckModel(document);
  if (!document.successor) first[name] = firstCheckModel(document);
  citations[name] = recordCitations(document);
}
const keys = (name) => Object.keys(vocabulary[name]);
process.stdout.write(
  JSON.stringify({
    models,
    first,
    citations,
    vocabulary: {
      states: keys("CARRY_OVER_STATES"),
      reasons: keys("CARRY_OVER_REASONS"),
      aspects: keys("CHANGED_ASPECTS"),
      aspectOrder: vocabulary.ASPECT_ORDER,
      dispositions: keys("DISPOSITION_ENTRIES"),
      conditions: keys("CONDITION_ENTRIES"),
      reissue: keys("REISSUE_CASES"),
      limits: vocabulary.RECHECK_LIMITS,
      unrecognised: vocabulary.UNRECOGNISED,
      notCarried: vocabulary.NOT_CARRIED,
      stateEntries: vocabulary.CARRY_OVER_STATES,
      reasonEntries: vocabulary.CARRY_OVER_REASONS,
      notes: vocabulary.ASPECT_NOTES,
      reissueEntries: vocabulary.REISSUE_CASES,
      verdictWords: vocabulary.VERDICT_WORDS,
      verdictScope: vocabulary.VERDICT_SCOPE,
      activityNames: vocabulary.ACTIVITY_NAMES,
      resolutionKinds: vocabulary.RESOLUTION_KINDS,
      leafReadings: vocabulary.LEAF_READINGS,
      consequenceKinds: vocabulary.CONSEQUENCE_KINDS,
      verdictLabels: vocabulary.VERDICT_LABELS,
      actions: vocabulary.ACTIONS,
      actionPack: vocabulary.ACTION_PACK,
      followUp: vocabulary.FOLLOW_UP,
      beside: vocabulary.BESIDE,
      readyNotes: vocabulary.READY_NOTES,
      refusalReasons: vocabulary.REFUSAL_REASONS,
      sourceSummary: vocabulary.SOURCE_SUMMARY,
      citationProvenance: vocabulary.CITATION_PROVENANCE,
      directory: vocabulary.DIRECTORY,
    },
  }),
);
"""


def _run_model(documents: dict[str, object]) -> dict[str, object]:
    """Run the screens' own modules under Node over ``name -> record document``.

    The static tree has no ``package.json`` and stays that way, so the modules
    are copied beside one in a temporary directory outside the repository; that
    is what lets any supported Node load them as ES modules.
    """

    node = shutil.which("node")
    if node is None:
        message = "node is not on PATH; the recheck wording cannot be exercised"
        if os.environ.get("CI"):
            raise AssertionError(message)
        raise unittest.SkipTest(message)
    with tempfile.TemporaryDirectory() as directory:
        workdir = Path(directory)
        # The model reads its words through words.js, in Chinese here.
        for name in (
            "recheck-model.js",
            "first-check-model.js",
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
            input=json.dumps(documents).encode("utf-8"),
            capture_output=True,
            check=False,
        )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return json.loads(completed.stdout.decode("utf-8"))


class _Modelled(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from internal.doctor_adapter import scenario_envelope

        cls.envelopes = dict(recheck_cases())
        cls.envelopes["adapter:recheck-comparison"] = scenario_envelope("recheck-comparison")
        cls.envelopes["adapter:member-evidence"] = scenario_envelope("member-evidence")
        output = _run_model(
            {name: envelope["record"] for name, envelope in cls.envelopes.items()}
        )
        cls.models = output["models"]
        cls.first = output["first"]
        cls.vocabulary = output["vocabulary"]

    def rows(self, name):
        return [
            row for subscope in self.models[name]["subscopes"] for row in subscope["evidence"]
        ]

    def row(self, name, citation_suffix):
        matches = [
            row for row in self.rows(name) if row["row"]["citation"].endswith(citation_suffix)
        ]
        self.assertEqual(len(matches), 1, citation_suffix)
        return matches[0]


class VocabularyMatchesTheRecordTests(_Modelled):
    """Every value the record types admit has words, and no stale one lingers."""

    def test_states_reasons_aspects_dispositions_and_conditions(self):
        for name, expected in (
            ("states", record.CARRY_OVER_STATES),
            ("reasons", record.CARRY_OVER_REASONS),
            ("aspects", record.CHANGED_ASPECTS),
            ("aspectOrder", record.CHANGED_ASPECTS),
            ("dispositions", record.MEMBER_DISPOSITIONS),
            ("conditions", record.RECHECK_CONDITION_STATES),
        ):
            with self.subTest(vocabulary=name):
                self.assertEqual(sorted(self.vocabulary[name]), sorted(expected))

    def test_the_retired_binary_is_gone(self):
        """``carried`` and the reason it replaced are not read or worded anywhere."""

        for path in sorted(STATIC.glob("*.js")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(file=path.name):
                self.assertNotRegex(text, r'"carried"|\.carried\b|\bcarried:')
                self.assertNotIn("finding-absent-from-the-cited-run", text)
                self.assertNotRegex(text, r'\?\s*"是"\s*:\s*"否"')

    def test_the_four_state_labels_are_four_different_things(self):
        entries = self.vocabulary["stateEntries"]
        labels = [entries[state]["label"] for state in record.CARRY_OVER_STATES]
        self.assertEqual(len(set(labels)), 4)
        self.assertEqual(
            labels, ["比较依据一致", "比较依据有变化", "未找到对应证据", "现有依据不足以比较"]
        )


class VocabularyDocumentTests(_Modelled):
    """The readable vocabulary under ``docs/product`` says what the screens say."""

    def test_every_code_and_sentence_is_in_the_document(self):
        text = (
            PROJECT_ROOT / "docs" / "product" / "2026-10-02-doctor-recheck-vocabulary.md"
        ).read_text(encoding="utf-8")
        for name in ("states", "reasons", "aspects", "dispositions", "conditions"):
            for code in self.vocabulary[name]:
                with self.subTest(vocabulary=name, code=code):
                    self.assertIn(f"`{code}`", text)
        sentences = [
            *self.vocabulary["reasonEntries"].values(),
            *self.vocabulary["limits"],
            *self.vocabulary["notes"].values(),
        ]
        for entry in self.vocabulary["stateEntries"].values():
            sentences += [entry["label"], entry["meaning"], entry["caveat"]]
        for entry in self.vocabulary["reissueEntries"].values():
            sentences += [entry["headline"], entry["detail"], *entry["caveats"]]
        for sentence in sentences:
            with self.subTest(sentence=sentence):
                self.assertIn(sentence, text)


class FourStatesTests(_Modelled):
    def test_each_state_is_worded_from_the_rows_own_state(self):
        entries = self.vocabulary["stateEntries"]
        seen = set()
        for name in self.envelopes:
            if not self.models[name] or not self.models[name]["recognised"]:
                continue
            for row in self.rows(name):
                state = row["row"].get("state")
                if state not in entries:
                    continue
                seen.add(state)
                with self.subTest(case=name, citation=row["row"]["citation"]):
                    self.assertEqual(row["state"]["code"], state)
                    self.assertEqual(row["state"]["label"], entries[state]["label"])
        self.assertEqual(seen, set(record.CARRY_OVER_STATES))

    def test_one_page_holds_all_four_and_tallies_them_as_recorded(self):
        tally = {
            entry["code"]: entry["count"]
            for entry in self.models["four-states"]["evidenceTally"]
        }
        self.assertEqual(tally, dict.fromkeys(record.CARRY_OVER_STATES, 1))

    def test_every_reason_has_its_own_sentence(self):
        reasons = self.vocabulary["reasonEntries"]
        self.assertEqual(len(set(reasons.values())), len(reasons))
        worded = set()
        for name in self.envelopes:
            if not self.models[name] or not self.models[name]["recognised"]:
                continue
            for row in self.rows(name):
                if row["reason"]["known"]:
                    worded.add(row["reason"]["code"])
                    self.assertEqual(row["reason"]["text"], reasons[row["reason"]["code"]])
        # Every reason the record admits is exercised by some case.
        self.assertEqual(worded, set(record.CARRY_OVER_REASONS))

    def test_equivalent_is_never_worded_as_no_review_needed(self):
        entry = self.vocabulary["stateEntries"]["equivalent"]
        self.assertIn("不代表整个交接不用复核", entry["caveat"])
        self.assertIn("“比较依据一致”不代表整个交接不用复核。", self.vocabulary["limits"])

    def test_no_counterpart_and_a_missing_member_are_never_worded_as_fixed(self):
        self.assertIn(
            "不代表问题已修复", self.vocabulary["stateEntries"]["no-counterpart"]["caveat"]
        )
        self.assertIn(
            "构件不在不等于已修复", self.vocabulary["reasonEntries"]["subject-not-present"]
        )
        gone = self.models["member-deleted"]["items"][1]
        self.assertEqual(gone["disposition"]["code"], "element-deleted-in-reissued-model")
        self.assertIn("不等于修复", gone["disposition"]["text"])
        self.assertIsNone(gone["current"])
        # No state, reason or disposition is worded as resolved.
        said = json.dumps(
            [self.vocabulary["stateEntries"], self.vocabulary["reasonEntries"]],
            ensure_ascii=False,
        )
        for claim in ("已解决", "已修复。", "问题已修复，", "可以沿用"):
            with self.subTest(claim=claim):
                for sentence in re.findall(rf"[^。”“]*{claim}[^。”“]*", said):
                    self.assertRegex(sentence, "不|没有")

    def test_cannot_compare_is_never_worded_as_evidence_missing(self):
        """A record sealed before 1.7 has no comparison basis. That is its own fact."""

        row = self.row("four-states", "sealed-pre-1.7")
        self.assertEqual(row["state"]["label"], "现有依据不足以比较")
        self.assertIn("无法比较", row["reason"]["text"])
        self.assertIn("不会用当前规则去补造", row["reason"]["text"])
        self.assertIn("不是“证据缺失”", row["state"]["caveat"])
        for row in self.rows("not-provable-reasons"):
            if row["state"]["code"] != "not-provable":
                continue
            with self.subTest(reason=row["reason"]["code"]):
                self.assertNotEqual(
                    row["state"]["label"],
                    self.vocabulary["stateEntries"]["no-counterpart"]["label"],
                )
                self.assertNotRegex(row["reason"]["text"], "证据缺失|证据不存在|没有对应")


class OnlyReKeyedTests(_Modelled):
    def test_a_new_key_alone_is_said_to_be_only_a_new_key(self):
        rekeyed = self.row("only-rekeyed", "sealed-rekeyed")
        self.assertEqual(rekeyed["state"]["code"], "equivalent")
        self.assertEqual(rekeyed["brief"], "只是引用换了键")
        self.assertEqual(rekeyed["facts"], ["只是引用换了键：证据内容和比较依据都没有变。"])
        self.assertEqual(rekeyed["notes"], [])

    def test_an_unchanged_key_and_a_determination_say_what_they_are(self):
        same = self.row("only-rekeyed", "sealed-same-key")
        self.assertEqual(same["brief"], "")
        self.assertEqual(same["facts"], ["引用的键没有换。"])
        determination = self.row("only-rekeyed", "same-document")
        self.assertEqual(determination["facts"], [])
        self.assertIn("同一份判定", determination["reason"]["text"])

    def test_a_new_key_on_a_changed_row_is_not_the_change(self):
        row = self.row("semantics-same-outcome", "sealed-retyped")
        self.assertEqual(len(row["facts"]), 1)
        self.assertIn("换键本身不算变化", row["facts"][0])


class ChangedAspectsTests(_Modelled):
    """``changed`` is never left as a tag: the page states which aspects moved."""

    def test_semantics_changed_and_the_outcome_did_not(self):
        row = self.row("semantics-same-outcome", "sealed-retyped")
        self.assertEqual(row["state"]["code"], "changed")
        self.assertEqual(row["brief"], "检查要求变了，模型版本、检查结果内容、检查程序未变。")
        self.assertEqual(row["notes"], [self.vocabulary["notes"]["semanticsSameOutcome"]])
        self.assertIn("不能当作同一条证据", row["notes"][0])

    def test_a_relaxed_requirement_is_not_reported_as_a_repaired_model(self):
        row = self.row("four-states", "sealed-relaxed")
        self.assertEqual(row["brief"], "检查结果内容、检查要求变了，模型版本、检查程序未变。")
        self.assertEqual(row["notes"], [self.vocabulary["notes"]["semanticsAndContent"]])
        self.assertIn("不能据此说模型修好了", row["notes"][0])
        self.assertIn("记录不说明要求是放宽还是收紧", row["notes"][0])

    def test_only_the_model_version_changed_is_not_the_result_changed(self):
        row = self.row("reissue-producing", "sealed-reissued")
        self.assertEqual(row["brief"], "模型版本变了，检查结果内容、检查要求、检查程序未变。")
        self.assertEqual(row["notes"], [self.vocabulary["notes"]["onlyModelVersion"]])
        self.assertIn("不等于检查结果的内容变了", row["notes"][0])

    def test_a_checker_change_is_named(self):
        row = self.row("checker-changed", "sealed-upgraded")
        self.assertEqual(row["brief"], "检查程序变了，模型版本、检查结果内容、检查要求未变。")
        self.assertEqual(row["notes"], [self.vocabulary["notes"]["checker"]])
        self.assertEqual(row["facts"], ["引用的键没有换。"])

    def test_the_aspects_are_the_rows_own_and_never_computed(self):
        """The sentence is a function of ``changed_aspects`` and of nothing else."""

        source = (STATIC / "recheck-model.js").read_text(encoding="utf-8")
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        for text in (source, screens):
            code = "\n".join(
                line for line in text.splitlines() if not line.lstrip().startswith(("//", "*"))
            )
            # No digest, content id or key is compared on the page.
            self.assertNotRegex(code, r"(digest|content_id|citation)\s*[!=]==?\s*\w")
            self.assertNotRegex(code, r"[!=]==?\s*[\w.\[\]]*(digest|content_id|citation)\b")


class FirstCheckTests(_Modelled):
    """The first-check result: items, whose they are, and what each rests on.

    Counts are counts of items the record holds — an element or a pair under one
    activity — and are never called defects. A known unmet requirement and a
    missing piece of evidence are counted under their own words.
    """

    name = "adapter:member-evidence"

    def setUp(self):
        self.model = self.first[self.name]
        self.record = self.envelopes[self.name]["record"]

    def test_only_a_record_that_succeeds_nothing_is_a_first_check(self):
        self.assertEqual(
            sorted(self.first),
            sorted(n for n, e in self.envelopes.items() if "successor" not in e["record"]),
        )

    def test_one_item_per_member_and_the_counts_are_of_items(self):
        expected = [
            (index, subscope["ordinal"], member_index, member["keys"])
            for index, activity in enumerate(self.record["activities"])
            for subscope in activity["subscopes"]
            for member_index, member in enumerate(subscope["members"])
        ]
        self.assertEqual(
            [
                (item["activityIndex"], item["ordinal"], item["memberIndex"], item["keys"])
                for item in self.model["items"]
            ],
            expected,
        )
        self.assertEqual(
            self.model["counts"], {"items": 13, "todo": 8, "quiet": 5, "elements": 6}
        )
        # To do is "the record gives a next action", read off the subscope.
        for item in self.model["items"]:
            self.assertEqual(item["todo"], "next_action" in item["subscope"].get("route", {}))
        # Blocked and undecidable are counted apart and never added into one.
        self.assertEqual(
            {entry["verdict"]: entry["count"] for entry in self.model["verdicts"]},
            {"UNKNOWN": 4, "BLOCKED": 4},
        )
        self.assertTrue(all(item["verdict"] == "READY" for item in self.model["quiet"]))
        source = (STATIC / "first-check-model.js").read_text(encoding="utf-8")
        code = "\n".join(
            line
            for line in source.splitlines()
            if not line.lstrip().startswith(("//", "*", "/*"))
        )
        self.assertNotRegex(code, r"READY|BLOCKED|UNKNOWN|score|Math\.|%")

    def test_items_are_grouped_by_the_team_the_assignment_names(self):
        teams = {team["team"]: team for team in self.model["teams"]}
        self.assertEqual(
            {name: team["count"] for name, team in teams.items()},
            {
                "coordination-team": 6,
                "architecture-design-team": 1,
                "information-management-team": 1,
            },
        )
        self.assertEqual(
            {name: team["roles"] for name, team in teams.items()},
            {
                "coordination-team": ["model-coordination"],
                "architecture-design-team": ["architecture-lead"],
                "information-management-team": ["information-manager"],
            },
        )
        for item in self.model["todo"]:
            self.assertEqual(
                item["team"], item["subscope"]["assignment"]["assigned_team_or_person"]
            )
            self.assertEqual(item["role"], item["subscope"]["route"]["default_role"])
        rows = [
            (row["kind"], row["activity"], row["verdict"], len(row["items"]))
            for row in teams["coordination-team"]["rows"]
        ]
        self.assertEqual(
            rows,
            [
                ("penetration-not-determined", "builders-work-openings", "UNKNOWN", 2),
                (
                    "asset-identity-not-evaluated",
                    "schedules-and-room-data-sheets",
                    "UNKNOWN",
                    1,
                ),
                (
                    "missing-project-asset-identity",
                    "schedules-and-room-data-sheets",
                    "BLOCKED",
                    3,
                ),
            ],
        )
        # No team in the record is no team on the page: nothing stands in for it.
        source = (STATIC / "first-check-model.js").read_text(encoding="utf-8")
        self.assertIn('team: carried(assignment, "assigned_team_or_person"),', source)
        self.assertEqual(source.count("assigned_team_or_person"), 1)
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        line = screens[screens.index("function teamLine(") :]
        line = line[: line.index("\n}\n")]
        self.assertIn("if (team === undefined) return missing(BESIDE.noTeam);", line)
        self.assertIn('mode === "fixture"', line)
        self.assertEqual(self.vocabulary["beside"]["simulatedTeam"], "示例处理团队")
        self.assertEqual(self.vocabulary["beside"]["noTeam"], "记录未提供")

    def test_each_items_basis_is_its_own_citations_and_named_absences(self):
        said = {}
        for item in self.model["items"]:
            basis = item["basis"]
            marked = [
                c
                for c in basis["findings"] + basis["determinations"]
                if c.startswith("fixture")
            ]
            said[(item["activity"], item["ordinal"], item["memberIndex"])] = (
                item["verdict"],
                len(basis["findings"]),
                len(basis["determinations"]),
                basis["gaps"],
                bool(marked),
            )
        self.assertEqual(
            said,
            {
                ("builders-work-openings", 1, 0): ("READY", 0, 1, [], True),
                ("builders-work-openings", 2, 0): (
                    "UNKNOWN",
                    0,
                    0,
                    ["no-determination"],
                    False,
                ),
                ("builders-work-openings", 2, 1): (
                    "UNKNOWN",
                    0,
                    0,
                    ["no-determination"],
                    False,
                ),
                ("builders-work-openings", 3, 0): ("READY", 0, 2, [], True),
                ("builders-work-openings", 4, 0): ("BLOCKED", 0, 2, [], True),
                ("ceiling-and-bulkhead-geometry", 1, 0): (
                    "UNKNOWN",
                    0,
                    0,
                    ["no-finding"],
                    False,
                ),
                ("ceiling-and-bulkhead-geometry", 2, 0): ("READY", 1, 1, [], True),
                ("ceiling-and-bulkhead-geometry", 2, 1): ("READY", 1, 1, [], True),
                ("ceiling-and-bulkhead-geometry", 2, 2): ("READY", 1, 1, [], True),
                ("schedules-and-room-data-sheets", 1, 0): (
                    "UNKNOWN",
                    0,
                    0,
                    ["no-finding"],
                    False,
                ),
                ("schedules-and-room-data-sheets", 2, 0): ("BLOCKED", 2, 0, [], False),
                ("schedules-and-room-data-sheets", 2, 1): ("BLOCKED", 2, 0, [], False),
                ("schedules-and-room-data-sheets", 2, 2): ("BLOCKED", 2, 0, [], False),
            },
        )
        # In this example every "can start" rests on a simulated determination,
        # so the tag has to be beside each one and not only at the page's head.
        self.assertTrue(all(entry[4] for entry in said.values() if entry[0] == "READY"))

    def test_on_an_item_page_what_to_do_comes_before_which_element(self):
        """The action, or the record's word that there is none, before the element's facts."""

        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        item = screens[screens.index("function firstItem(") : screens.index("// S4 — recheck")]
        # The headings are in the wording tables; the screen places them.
        order = ["ITEM.conclusion", "ITEM.actionHeading", "ITEM.whichOne", "ITEM.details"]
        positions = [item.index(heading) for heading in order]
        self.assertEqual(positions, sorted(positions), order)
        self.assertLess(item.index("ITEM.followUpHeading"), item.index("ITEM.whichOne"))
        self.assertLess(
            item.index("actionBlock(item.subscope"), item.index("elementCard(state, key")
        )
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        for said in (
            'actionHeading: "二、要做什么、由谁处理、完成后拿什么复检"',
            'followUpHeading: "二、后续"',
            'whichOne: "三、是哪个构件"',
            'details: "四、{heading}"',
        ):
            with self.subTest(said=said):
                self.assertIn(said, vocabulary)

    def test_a_first_check_card_folds_only_the_particulars_and_the_full_action(self):
        """D1: closed by default, and what changes how a conclusion reads stays out."""

        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        first = screens[screens.index("function first(") : screens.index("function leafName(")]
        card = first[first.index("const card = (item, said) => {") : first.index("\n  };\n")]
        fold = card.index('"details"')
        link = card.index('{ class: "run", href: itemHref(item)')
        # Outside the fold: the element, the work and its verdict, the basis
        # (simulated or not), the notes, the problem in a few words, the link.
        for shown in (
            "itemTitle(state, item.keys)",
            "workVerdict(item.activity, item.verdict)",
            "basisLine(item.basis)",
            "besideVerdict(item.activity, item.verdict, said)",
            "FIRST.problem),",
        ):
            with self.subTest(shown=shown):
                self.assertLess(card.index(shown), fold)
        self.assertGreater(link, card.index("FIRST.cardElements"))
        # Inside the fold: the element's particulars and the full action.
        inside = card[fold:link]
        self.assertIn("elementBrief(state, element", inside)
        self.assertIn("definitions([[FIRST.action, sentences.action]])", inside)
        self.assertNotIn("elementBrief(", card[:fold])
        self.assertNotIn("sentences.action", card[:fold])
        # Closed unless the viewer opened it; which ones are open survives a
        # visit to an item and back, for the same run only.
        self.assertIn("open: opened.has(key)", inside)
        self.assertIn("openFirstCards.runId === state.runId", first)
        # The way back to the item is the link, never inside the fold.
        self.assertIn('"data-return-focus": here(item) ? true : null', card[link:])
        self.assertIn("FIRST.openCard", card[link:])
        # The item page is untouched: what to do still comes first there.
        item = screens[screens.index("function firstItem(") : screens.index("// S4 — recheck")]
        self.assertNotIn("card-details", item)

    def test_on_a_recheck_item_page_what_to_do_comes_before_which_element(self):
        """The same order as the first check's item page, numbered to match."""

        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        item = screens[screens.index("function recheckItem(") :]
        item = item[: item.index("\n}\n")]
        order = [
            "ITEM.conclusion",
            "RECHECK_ITEM.actionHeading",
            "RECHECK_ITEM.whichTwo : RECHECK_ITEM.whichOne",
            "RECHECK_ITEM.conditionHeading",
        ]
        positions = [item.index(heading) for heading in order]
        self.assertEqual(positions, sorted(positions), order)
        self.assertLess(
            item.index("currentSubscopeBlock(state, item, current)"),
            item.index("elementCard(state, key"),
        )
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        recheck = vocabulary[vocabulary.index("export const RECHECK_ITEM = {") :]
        recheck = recheck[: recheck.index("\n};\n")]
        for said in (
            'actionHeading: "二、要做什么、由谁处理、完成后拿什么复检"',
            'whichOne: "三、是哪个构件"',
            'whichTwo: "三、是哪两个构件"',
            'conditionHeading: "四、复检前留下的结束条件，这次达到了吗"',
        ):
            with self.subTest(said=said):
                self.assertIn(said, recheck)

    def test_a_conclusion_is_never_shown_without_its_work_its_basis_and_its_limits(self):
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        first = screens[
            screens.index("// S3b — first check") : screens.index("// S4 — recheck")
        ]

        def function(name):
            body = first[first.index(f"function {name}(") :]
            return body[: body.index("\n}\n")]

        # A verdict label is produced in one place and reaches the page only
        # through a helper that puts the work beside it, or in the legend.
        callers = [
            line.strip()
            for line in screens.splitlines()
            if "verdictLabel(" in line and not line.lstrip().startswith(("//", "*", "function"))
        ]
        self.assertEqual(len(callers), 4, callers)
        self.assertIn("activityTitle(activity)", function("workVerdict"))
        for name in ("first", "firstItem"):
            body = function(name)
            with self.subTest(screen=name):
                self.assertIn("workVerdict(item.activity, item.verdict)", body)
                self.assertIn("basisLine(item.basis)", body)
                self.assertIn("besideVerdict(item.activity, item.verdict", body)
                self.assertIn("howToRead()", body)
        # On the result page every conclusion still gets its basis and its
        # limits; a block (one team, or the items with no action) says each
        # general note once, beside the first conclusion it applies to.
        result = function("first")
        self.assertEqual(result.count("besideVerdict(item.activity, item.verdict, said)"), 2)
        self.assertEqual(result.count("})(new Set())") + result.count("))(new Set())"), 2)
        self.assertEqual(result.count("basisLine(item.basis)"), 2)
        # The item page has one conclusion: everything beside it, always.
        self.assertIn("besideVerdict(item.activity, item.verdict),", function("firstItem"))
        # The summary's count line is only ever built from items to do: a "can
        # start" is never counted there, only shown beside its own item.
        result = function("first")
        self.assertIn("model.verdicts", result)
        self.assertNotIn("model.quiet.length} 个事项可以开始", result)
        beside = function("besideVerdict")
        self.assertIn('if (value === "UNKNOWN") once(BESIDE.unknown);', beside)
        self.assertIn("once(BESIDE.readyScope);", beside)
        # The notes written for one activity are specific limits: never once-only.
        self.assertIn("notes.push(...READY_NOTES[activity])", beside)
        self.assertIn("if (said === null || !said.has(text)) notes.push(text);", beside)
        words = self.vocabulary["beside"]
        self.assertIn("不代表整次交接完成", words["readyScope"])
        self.assertIn("不等于这个构件没有问题", words["unknown"])
        self.assertIn("不代表已经派发", words["team"])
        # That a requirement is the project's own is read off the data's labels;
        # what stays beside an asset-identity item is only the gap.
        self.assertIn("记录未提供", words["assetIdentity"])
        self.assertNotIn("本项目约定", words["assetIdentity"])
        self.assertEqual(
            self.vocabulary["readyNotes"],
            {
                "ceiling-and-bulkhead-geometry": [
                    "规则只证明构件有楼层或空间归属，没有验证接收方模型有对应楼层。",
                    "这个结论靠的是两侧模型的对齐确认，不是共享定位标记通过。",
                ]
            },
        )

    def test_the_sentences_hold_for_one_pack_version_and_say_so_otherwise(self):
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        guard = screens[screens.index("function actionSentences(") :]
        guard = guard[: guard.index("\n}\n")]
        for said in (
            "request.pack_id === ACTION_PACK.id",
            "request.pack_version === ACTION_PACK.version",
            "Object.hasOwn(ACTIONS, kind)",
            "if (!written) return null;",
            "return ACTIONS[kind];",
        ):
            with self.subTest(guard=said):
                self.assertIn(said, guard)
        # Under any other version there is no sentence, and the page says so;
        # the record's route words are never put in its place.
        block = screens[screens.index("function actionBlock(") :]
        block = block[: block.index("\n}\n")]
        self.assertIn(
            'sentences ? h("span", { class: "action" }, sentences.action)'
            " : missing(ACTION.noSentence)",
            block,
        )
        self.assertIn("sentences ? [ACTION.recheck, sentences.recheck] : null", block)
        self.assertEqual(
            self.record["request"]["pack_version"], self.vocabulary["actionPack"]["version"]
        )

    def test_what_is_missing_comes_from_the_returned_data_or_is_said_to_be_absent(self):
        """Eight fields per cited check result, shown as they came — or said to be absent.

        No rule file is read, no rule or property is named in the page's own
        source, and no required value, Revit parameter or export mapping is
        written: the run holds none of them. That a requirement is the project's
        own is read off the entry's labels.
        """

        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")

        def function(name):
            body = screens[screens.index(f"function {name}(") :]
            return body[: body.index("\n}\n")]

        block = function("detailsBlock")
        self.assertIn('carried(state.envelope, "finding_details")', block)
        self.assertIn("basis.findings.map((key) => findingDetail(details, key))", block)
        detail = function("findingDetail")
        self.assertIn("const entry = carries(details, key) ? details[key] : null;", detail)
        self.assertIn("missing(DETAILS_WORDS.absent)", detail)
        envelope = self.envelopes[self.name]
        entries = envelope["finding_details"]
        fields = sorted(next(iter(entries.values())))
        self.assertEqual(
            fields,
            [
                "actual",
                "citation",
                "expected",
                "labels",
                "reason",
                "requirement_id",
                "rule_id",
                "status",
            ],
        )
        for name in fields:
            with self.subTest(read=name):
                self.assertRegex(detail, rf'"{name}"')
        # "Project's own" comes from the label; an empty `actual` is a value.
        self.assertIn("labels.includes(PROJECT_ASSUMPTION)", detail)
        self.assertIn('PROJECT_ASSUMPTION = "ProjectAssumption"', vocabulary)
        self.assertIn('entry.actual === ""', detail)
        self.assertIn("DETAILS_WORDS.noActual", detail)
        # A value the run did observe is not printed.
        self.assertEqual(len(re.findall(r"entry\.actual\b", detail)), 1)
        # Every check result this record's items cite has an entry; nothing
        # else is looked up, and a determination has none to look up.
        cited = {key for item in self.model["items"] for key in item["basis"]["findings"]}
        self.assertEqual(cited, set(entries))
        self.assertEqual(len(cited), 9)
        todo = [item for item in self.model["todo"] if item["basis"]["findings"]]
        self.assertEqual(len(todo), 3)
        for item in todo:
            for key in item["basis"]["findings"]:
                self.assertEqual(entries[key]["status"], "FAIL")
                self.assertIn("ProjectAssumption", entries[key]["labels"])
                self.assertEqual(entries[key]["actual"], "")
        # The reasons the run gives for these have words here, by exact match.
        reasons = {entry["reason"] for entry in entries.values()}
        for reason in reasons:
            with self.subTest(reason=reason):
                self.assertIn(f'"{reason}"', vocabulary)
        for path in sorted(STATIC.iterdir()):
            text = path.read_text(encoding="utf-8")
            with self.subTest(file=path.name):
                self.assertNotRegex(
                    text, r"AssetTag|SystemCode|EPC_Delivery|R-00\d|rules/|\.toml"
                )

    def test_an_old_citations_requirement_is_the_earlier_runs_and_compares_nothing(self):
        """On a recheck row the old citation has its entry and the new one has none.

        Having the earlier assessment's words beside a row does not make the row
        comparable: its state is the record's, and the page says so on the row.
        """

        from internal.doctor_adapter import scenario_envelope

        again = scenario_envelope(self.vocabulary["followUp"]["member-evidence"])
        entries = again["finding_details"]
        rows = [
            row
            for outcome in again["record"]["successor"]["subscopes"]
            for row in outcome["evidence_carry_over"]
            if row["citation_kind"] == "finding"
        ]
        self.assertEqual(len(rows), 9)
        for row in rows:
            self.assertIn(row["citation"], entries)
            self.assertNotIn(row["current_citation"], entries)
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        card = screens[screens.index("function evidenceCard(") :]
        card = card[: card.index("\n}\n")]
        self.assertIn('kind === "finding" && carries(row, "citation")', card)
        self.assertIn("DETAILS_WORDS.prior", card)
        self.assertIn("findingDetail(details, row.citation)", card)
        self.assertIn("DETAILS_WORDS.currentAbsent", card)
        # The state is rendered from the row and before the old requirement.
        self.assertLess(card.index("stateBadge(item.state)"), card.index("DETAILS_WORDS.prior"))
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        self.assertIn(
            "有这段说明不等于这一行可以比较；这一行的状态以上面写的为准。", vocabulary
        )
        model = (STATIC / "recheck-model.js").read_text(encoding="utf-8")
        self.assertNotIn("finding_details", model)

    def test_the_follow_up_really_is_a_recheck_of_this_record(self):
        from internal.doctor_adapter import scenario_envelope

        follow = self.vocabulary["followUp"]
        self.assertEqual(follow, {"member-evidence": "recheck-requirement-relaxed"})
        first = scenario_envelope("member-evidence")
        again = scenario_envelope(follow["member-evidence"])
        successor = again["record"]["successor"]
        self.assertEqual(successor["prior_assessment_digest"], first["assessment_digest"])
        # The same item is found by the activity and group number the recheck
        # record carries, and its members are the sealed group's, in order.
        sealed = {
            (activity["activity_ref"], subscope["ordinal"]): [
                m["keys"] for m in subscope["members"]
            ]
            for activity in first["record"]["activities"]
            for subscope in activity["subscopes"]
        }
        self.assertEqual(
            {
                (outcome["activity_ref"], outcome["subscope_ordinal"]): [
                    item["member"]["keys"] for item in outcome["dispositions"]
                ]
                for outcome in successor["subscopes"]
            },
            sealed,
        )
        model = (STATIC / "recheck-model.js").read_text(encoding="utf-8")
        lookup = model[model.index("export function sealedGroupIndex(") :]
        lookup = lookup[: lookup.index("\n}\n")]
        self.assertIn("subscope.outcome.subscope_ordinal === ordinal", lookup)
        self.assertNotRegex(lookup, r"keys|refined_from|activities")

    def test_a_check_that_did_not_start_says_what_would_be_needed_and_no_more(self):
        reason = self.vocabulary["refusalReasons"]["team-mapping-decision-basis-illustrative"]
        action = "".join(reason["action"])
        self.assertIn("项目负责人实际决定", action)
        self.assertIn("不是改一个标签", action)
        # Nobody is sent to edit the shipped sample.
        self.assertIn("不需要、也不应该去改它的设定", action)
        # Later gates this refusal did not test are not part of this diagnosis.
        for untested in ("证据方法", "风险授权", "CONDITIONAL"):
            self.assertNotIn(untested, reason["text"] + action)
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        refusal = screens[screens.index("function refusal(") :]
        english = refusal.index("envelope.refusal.text")
        self.assertLess(refusal.index('"details"'), english)
        self.assertLess(refusal.index("reason.action"), refusal.index('"details"'))
        self.assertLess(refusal.index("REFUSAL_SCOPE_NOTE"), refusal.index('"details"'))


class ReissuedSideTests(_Modelled):
    """Which side moved is looked up from ``changed_models``; no discipline is named."""

    def test_the_four_situations_are_four_different_statements(self):
        headlines = {}
        for name, (producing, consuming) in REISSUE_SIDES.items():
            reissue = self.models[name]["reissue"]
            with self.subTest(case=name):
                self.assertEqual(reissue["name"], name.removeprefix("reissue-"))
                self.assertEqual(
                    [side["reissued"] for side in reissue["sides"]], [producing, consuming]
                )
            headlines[name] = reissue["headline"]
        self.assertEqual(len(set(headlines.values())), 4)
        self.assertEqual(headlines["reissue-none"], "两侧模型都没有重新发布（版本未变）")
        self.assertEqual(headlines["reissue-both"], "交出方和接收方的模型都重新发布了")

    def test_the_case_follows_changed_models_and_not_the_content_ids(self):
        """Swap the record's list and leave the ids alone: the page follows the list."""

        document = json.loads(json.dumps(self.envelopes["reissue-producing"]["record"]))
        comparison = document["successor"]["model_version_context_comparison"]
        comparison["changed_models"] = [comparison["consuming"]["model_key"]]
        model = _run_model({"swapped": document})["models"]["swapped"]
        self.assertEqual(model["reissue"]["name"], "consuming")

    def test_role_names_come_from_the_requests_handover(self):
        for name in REISSUE_SIDES:
            reissue = self.models[name]["reissue"]
            with self.subTest(case=name):
                self.assertEqual(
                    [side["role"] for side in reissue["sides"]],
                    [HANDOVER["from_role"], HANDOVER["to_role"]],
                )
        detail = self.models["reissue-both"]["reissue"]["detail"]
        self.assertIn(HANDOVER["from_role"], detail)
        self.assertIn(HANDOVER["to_role"], detail)

    def test_no_discipline_or_model_name_is_written_into_the_recheck_wording(self):
        context = self.envelopes["adapter:recheck-comparison"]["record"]["request"][
            "model_version_context"
        ]
        named = {
            context["handover"]["from_role"],
            context["handover"]["to_role"],
            context["producing"]["model_key"],
            context["consuming"]["model_key"],
            "机电",
            "暖通",
            "建筑专业",
            "结构专业",
        }
        model = (STATIC / "recheck-model.js").read_text(encoding="utf-8")
        said = json.dumps(
            [
                self.vocabulary["reissueEntries"],
                self.vocabulary["stateEntries"],
                self.vocabulary["reasonEntries"],
                self.vocabulary["notes"],
                self.vocabulary["limits"],
            ],
            ensure_ascii=False,
        )
        for word in sorted(named):
            with self.subTest(word=word):
                self.assertNotRegex(model, rf"(?i)\b{re.escape(word)}\b")
                self.assertNotIn(word.lower(), said.lower())

    def test_no_direction_is_prejudged(self):
        entries = self.vocabulary["reissueEntries"]
        consuming = " ".join(entries["consuming"]["caveats"])
        producing = " ".join(entries["producing"]["caveats"])
        self.assertIn("不代表修复已经发生", consuming)
        self.assertIn("洞口已完成", consuming)
        self.assertIn("不能据此说接收方的工作", producing)
        # A re-issue on either side leaves the old determinations unattributable.
        for side in (consuming, producing, " ".join(entries["both"]["caveats"])):
            self.assertIn("针对旧版本作出的判定", side)
        self.assertIn("不把任何一条证据的变化归到某一侧", " ".join(entries["both"]["caveats"]))
        self.assertEqual(entries["none"]["caveats"], [])
        for name in REISSUE_SIDES:
            self.assertIn(
                "不根据重新发布的方向预判好坏", self.models[name]["reissue"]["neutral"]
            )

    def test_a_comparison_the_page_cannot_place_is_not_guessed(self):
        for name in ("unrecognised-values", "reissue-contradiction"):
            reissue = self.models[name]["reissue"]
            with self.subTest(case=name):
                self.assertEqual(reissue["name"], "unrecognised")
                self.assertEqual([side["reissued"] for side in reissue["sides"]], [None, None])

    def test_the_real_scenario_is_the_unchanged_case(self):
        model = self.models["adapter:recheck-comparison"]
        self.assertEqual(model["reissue"]["name"], "none")
        self.assertEqual(
            [(entry["code"], entry["count"]) for entry in model["evidenceTally"]],
            [("no-counterpart", 2)],
        )
        self.assertEqual(len(model["items"]), 1)
        self.assertIsNone(model["items"][0]["current"])
        self.assertEqual(model["items"][0]["condition"]["code"], "not-comparable")


class UnrecognisedValuesTests(_Modelled):
    """A value from a later contract is shown as it came, never as its neighbour."""

    def test_an_unknown_state_reason_aspect_disposition_and_condition(self):
        unrecognised = self.vocabulary["unrecognised"]
        row = self.row("unrecognised-values", "sealed-unknown-state")
        self.assertEqual(
            row["state"],
            {
                "code": "superseded-by-policy",
                "known": False,
                "label": unrecognised,
                "meaning": "",
                "caveat": "",
            },
        )
        self.assertEqual(row["reason"]["code"], "a-reason-from-a-later-contract")
        self.assertFalse(row["reason"]["known"])
        self.assertEqual(row["brief"], "")
        self.assertEqual(row["facts"], [])

        aspect = self.row("unrecognised-values", "sealed-unknown-aspect")
        self.assertEqual(aspect["brief"], f"模型版本、“geometry”（{unrecognised}）变了。")
        # With a value outside the closed list, nothing is called unchanged.
        self.assertNotIn("未变", aspect["brief"])
        self.assertEqual(aspect["notes"], [self.vocabulary["notes"]["unrecognised"]])
        self.assertEqual(aspect["facts"], [f"key_changed = “maybe”（{unrecognised}）"])

        item = self.models["unrecognised-values"]["items"][0]
        self.assertEqual(item["disposition"]["code"], "merged-into-another-member")
        self.assertFalse(item["disposition"]["known"])
        self.assertEqual(item["disposition"]["next"], "")
        self.assertEqual(item["condition"]["code"], "partly-observed")
        self.assertFalse(item["condition"]["known"])
        tally = {
            entry["code"]: entry["known"]
            for entry in self.models["unrecognised-values"]["evidenceTally"]
        }
        self.assertEqual(tally["superseded-by-policy"], False)

    def test_a_key_the_record_does_not_carry_is_words_and_not_a_state(self):
        missing = self.vocabulary["notCarried"]
        row = self.row("keys-not-carried", "sealed-bare")
        self.assertEqual((row["state"]["code"], row["state"]["label"]), (None, missing))
        self.assertEqual((row["reason"]["code"], row["reason"]["text"]), (None, missing))
        item = self.models["keys-not-carried"]["items"][0]
        self.assertEqual(
            (item["disposition"]["code"], item["disposition"]["text"]), (None, missing)
        )
        self.assertEqual(
            (item["condition"]["code"], item["condition"]["plain"]), (None, missing)
        )

    def test_a_successor_that_is_not_a_recheck_is_not_shown_as_one(self):
        model = self.models["successor-not-a-recheck"]
        self.assertEqual(model, {"kind": "authorisation", "recognised": False})
        self.assertIsNone(self.models["adapter:member-evidence"])


class ItemsStayPerMemberTests(_Modelled):
    def test_one_item_per_sealed_member_in_the_records_order(self):
        for name, envelope in self.envelopes.items():
            model = self.models[name]
            if not model or not model["recognised"]:
                continue
            expected = [
                item["member"]["keys"]
                for outcome in envelope["record"]["successor"]["subscopes"]
                for item in outcome["dispositions"]
            ]
            with self.subTest(case=name):
                self.assertEqual(
                    [item["entry"]["member"]["keys"] for item in model["items"]], expected
                )
                # No overall status and no score: the model's keys are these.
                self.assertEqual(
                    sorted(model),
                    [
                        "actionGroups",
                        "conditionTally",
                        "dispositionTally",
                        "evidenceGroups",
                        "evidenceTally",
                        "items",
                        "kind",
                        "recognised",
                        "reissue",
                        "subscopes",
                        "verdictGroups",
                    ],
                )

    def test_a_present_member_reads_the_subscope_the_framework_named(self):
        envelope = self.envelopes["member-deleted"]
        outcome = envelope["record"]["successor"]["subscopes"][0]
        present, gone = self.models["member-deleted"]["items"]
        ordinal = outcome["dispositions"][0]["current_ordinals"][0]
        located = present["current"][0]["located"]
        activity = envelope["record"]["activities"][located["activityIndex"]]
        self.assertEqual(activity["activity_ref"], outcome["activity_ref"])
        self.assertEqual(located["subscope"]["ordinal"], ordinal)
        self.assertIn("next_action", located["subscope"]["route"])
        self.assertIsNone(gone["current"])

    def test_the_current_partition_is_read_only_for_an_ordinal_the_record_gave(self):
        """Where the Framework records no correspondence, the page constructs none.

        A member that left has no ``current_ordinals``. Looking its
        ``refined_from`` element up in the current partition, or matching its
        keys against current members, would be the page inventing the
        correspondence the record declines to state.
        """

        model = (STATIC / "recheck-model.js").read_text(encoding="utf-8")
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        recheck = screens[
            screens.index("// S4 — recheck") : screens.index("// SX — real refusal")
        ]
        self.assertEqual(model.count("document.activities"), 2)
        lookup = model[model.index("function currentSubscope(") :]
        lookup = lookup[: lookup.index("\n}\n")]
        self.assertEqual(lookup.count("document.activities"), 2)
        self.assertEqual(model.count("currentSubscope("), 2)
        self.assertRegex(
            model,
            r'carries\(item, "current_ordinals"\)\s*\?\s*item\.current_ordinals\.map\(',
        )
        for text in (model, recheck):
            code = "\n".join(
                line for line in text.splitlines() if not line.lstrip().startswith(("//", "*"))
            )
            self.assertNotIn("refined_from", code)
            self.assertNotRegex(code, r"\.keys\s*[!=]==?|sameKeys\(|readingsFor\(")
        self.assertNotIn(".activities", recheck)


class ScreenStructureTests(unittest.TestCase):
    """What can be pinned about the screens without a browser."""

    @classmethod
    def setUpClass(cls):
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        cls.recheck = screens[
            screens.index("// S4 — recheck") : screens.index("// SX — real refusal")
        ]

    def _function(self, name):
        body = self.recheck[self.recheck.index(f"function {name}(") :]
        return body[: body.index("\n}\n")]

    def test_no_button_on_the_recheck_screens(self):
        """Nothing here can be done, so nothing here looks like it can."""

        self.assertNotIn('"button"', self.recheck)
        self.assertNotIn("onclick", self.recheck)
        self.assertIn("RECHECK_CANNOT", self._function("recheck"))
        self.assertIn("RECHECK_CANNOT", self._function("recheckItem"))

    def test_what_qualifies_a_conclusion_sits_beside_it_and_the_rest_is_one_fold_away(self):
        """Simulated evidence, a requirement edit and a missing member stay in view.

        The second walkthrough failed on reading load: five sentences on every
        page, most of them about something the page did not show. What a manager
        must read with a conclusion now sits beside that conclusion and only
        where it applies; what he may want once is in "how to read this page".
        A citation's own tag is still on the same line as the citation.
        """

        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        for name in ("recheck", "recheckItem"):
            body = self._function(name)
            with self.subTest(screen=name):
                # Beside the conclusion: its basis and the requirement edit.
                self.assertIn("besideChange(item)", body)
                self.assertIn("requirementNote(item)", body)
                # One fold away: the general reading rules.
                self.assertIn("howToRead(", body)
                self.assertIn("RECHECK_LIMITS", body)
        beside = self._function("besideChange")
        self.assertIn("basisLine(basisOf(current.located.subscope), true)", beside)
        self.assertNotIn("details", beside)
        self.assertNotIn("details", self._function("workChange"))
        # A re-issue's caveats and a member that left are said in the result
        # block and on the item, outside every fold.
        result = self._function("recheck")
        self.assertLess(result.index("model.reissue.caveats"), result.index('"details"'))
        self.assertIn("dispositionRow(item)", self._function("recheckItem"))
        basis = screens[screens.index("function basisLine(") :]
        basis = basis[: basis.index("\n}\n")]
        self.assertIn('provenanceCounts("finding", basis.findings)', basis)
        self.assertIn('provenanceCounts("determination", basis.determinations)', basis)
        self.assertNotRegex(basis, r"mode|envelope")
        # Row by row, the tag is on the citation's own line.
        card = self._function("evidenceCard")
        collapsed = card[card.index('"details"') :]
        shown = card[: card.index('"details"')]
        self.assertEqual(shown.count("provenance("), 2)
        self.assertNotIn("provenance(", collapsed)
        # Before and after are sourced apart, never as two tags on one line.
        item = self._function("recheckItem")
        self.assertIn('sources("citation")', item)
        self.assertIn('sources("current_citation")', item)

    def test_the_way_back_returns_to_the_item_that_was_opened(self):
        app = (STATIC / "app.js").read_text(encoding="utf-8")
        self.assertIn('main.querySelector("[data-return-focus]")', app)
        self.assertIn(
            "lastRecheckItem = { runId: state.runId, subscopeIndex, memberIndex }", self.recheck
        )
        self.assertIn('"data-return-focus": here ? true : null', self.recheck)
        self.assertIn("RECHECK_ITEM.back", self._function("recheckItem"))
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        self.assertIn('back: "← 返回复检事项列表（回到这一项的位置）"', vocabulary)

    def test_the_path_screens_use_no_internal_term(self):
        """Home, directory, recheck result, recheck item and the check attempt.

        The words a manager could not read are gone from the path this revision
        carries. They are still on the record, activity and member screens, which
        this revision did not reach; those are named here so the list shrinks on
        purpose rather than by accident.
        """

        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        cut = lambda start, end: screens[screens.index(start) : screens.index(end)]  # noqa: E731
        path = {
            "context bar": cut("export function renderContext(", "function elementFacts("),
            "home and directory": cut("function entry(", "function record(state) {"),
            "first check": cut("// S3b — first check", "// S4 — recheck"),
            "recheck": self.recheck,
            "check attempt": screens[screens.index("function refusal(") :],
        }
        strings = {
            name: "\n".join(
                line
                for line in text.splitlines()
                if not line.lstrip().startswith(("//", "*", "/*"))
            )
            for name, text in path.items()
        }
        strings["vocabulary"] = "\n".join(
            line
            for line in (STATIC / "vocabulary.js").read_text(encoding="utf-8").splitlines()
            if not line.lstrip().startswith("//")
        )
        # ABSENCES is read by the member screens only.
        absences = strings["vocabulary"]
        absences = absences[absences.index("const ABSENCES") :]
        strings["vocabulary"] = strings["vocabulary"].replace(
            absences[: absences.index("};")], ""
        )
        for name, text in strings.items():
            for term in (
                "夹具",
                "信封",
                "Framework",
                "Purpose",
                "Overlay",
                "真实输入",
                "裁决",
                "子范围",
                "成员",
                "读数",
                "交接判断规则",
                "示意值",
            ):
                with self.subTest(screen=name, term=term):
                    self.assertNotIn(term, text)
        # Internal English is kept out of what a manager reads: no string that
        # carries Chinese also carries these words. Code that reads the record's
        # own keys (`"finding"`, `basis.findings`) is not a sentence. The words
        # the context bar, the home, the directory and the first-check result
        # used to write inline are in vocabulary.js's moved tables now, and are
        # read from there.
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        strings["moved"] = vocabulary[vocabulary.index("export const COMMON") :]
        checked = 0
        for name in (
            "context bar",
            "home and directory",
            "first check",
            "recheck",
            "check attempt",
            "moved",
        ):
            sentences = re.findall(r'["`]([^"`\n]*[\u4e00-\u9fff][^"`\n]*)["`]', strings[name])
            checked += len(sentences)
            for sentence in sentences:
                with self.subTest(screen=name, sentence=sentence):
                    self.assertNotRegex(sentence, r"\bPack\b|finding")
        self.assertGreater(checked, 100)

    def test_the_first_screen_says_what_it_is_for_and_what_it_cannot_do(self):
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        home = vocabulary[vocabulary.index("export const HOME") :]
        home = home[: home.index("\n};")]
        for said in (
            "BIM 经理",
            "仍需处理",
            "Revit 文件本身（.rvt）不能导入",
            "整体合规或可施工结论",
        ):
            with self.subTest(said=said):
                self.assertIn(said, home)
        # The shipped project's entry promises an attempt, not an input.
        self.assertIn('real: "随附项目的检查尝试"', vocabulary)
        self.assertIn("这个入口不是导入入口", home)
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        entry = screens[
            screens.index("function entry(") : screens.index("function runLink(")
        ]
        self.assertLess(entry.index("HOME.lede"), entry.index("said.status"))
        self.assertLess(entry.index("said.status"), entry.index("entry-grid"))
        self.assertNotIn("details", entry)

    def test_an_element_is_described_from_what_was_handed_over_and_nothing_else(self):
        """Name, class, storey, GlobalId and model. Discipline is said to be missing.

        The envelope's elements carry no discipline, and a model key is a model
        identifier, not a discipline statement. The card says both, and no
        screen maps a model key to a discipline name.
        """

        card = self._function("elementCard")
        for key in ('"ifc_class"', '"model_key"', '"global_id"', "storeyOf(facts)"):
            with self.subTest(read=key):
                self.assertIn(key, card)
        self.assertIn("[ELEMENT_CARD.disciplineRow, missing(ELEMENT_WORDS.noDiscipline)]", card)
        self.assertIn("ELEMENT_WORDS.modelIsNotDiscipline", card)
        self.assertNotIn("details", card)
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        self.assertIn("不从模型标识推断专业", vocabulary)
        for file in ("screens.js", "recheck-model.js", "vocabulary.js"):
            text = (STATIC / file).read_text(encoding="utf-8")
            with self.subTest(file=file):
                self.assertNotRegex(text, r"discipline\s*[:=]|DISCIPLINE")
                for word in ("机电", "暖通", "建筑专业", "结构专业"):
                    self.assertNotIn(word, text)
        # A pair shows both elements, each with its own card.
        item = self._function("recheckItem")
        self.assertIn(
            "keys.map((key) => elementCard(state, key, model.reissue.comparison))", item
        )
        side = (STATIC / "recheck-model.js").read_text(encoding="utf-8")
        side = side[side.index("export function handoverSide(") :]
        side = side[: side.index("\n}\n")]
        self.assertIn("comparison[side].model_key", side)

    def test_a_refusal_and_a_fault_are_two_different_screens(self):
        """A project condition not met is an answer; a failure of the program is not.

        The refusal arrives as a result and is worded from its code. Anything
        else — an exception, an adapter that cannot be imported — never reaches
        that screen: it is shown as a fault of the program, with no statement
        about a project.
        """

        app = (STATIC / "app.js").read_text(encoding="utf-8")
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        fault = app[app.index("} catch (failure) {") :]
        fault = fault[: fault.index("if (token !== rendering")]
        fault = "\n".join(
            line for line in fault.splitlines() if not line.lstrip().startswith("//")
        )
        self.assertIn("FAULT_WORDS.unavailable : FAULT_WORDS.fault", fault)
        self.assertIn("FAULT_WORDS.note", fault)
        self.assertIn("failure.message", fault)
        self.assertNotIn("refusal", fault.replace("refusal-text", ""))
        refusal = screens[screens.index("function refusal(") :]
        self.assertNotIn("FAULT_WORDS", refusal)
        self.assertIn("REFUSAL_PAGE.lede", refusal)
        self.assertIn("不是程序故障，也不是检查结果", vocabulary)
        self.assertIn('"team-mapping-decision-basis-illustrative": {', vocabulary)
        self.assertIn("项目条件未满足", vocabulary)
        self.assertIn("不是对任何项目或模型的判断", vocabulary)


# What the page says for each of the adapter's recheck scenarios. The rows of a
# scenario are the Framework's and are pinned in ``test_doctor_recheck_scenarios.py``;
# what is pinned here is the wording those rows reach the manager in.
_REKEYED = "只是引用换了键"
_SAME_DETERMINATION = "同一份判定：引用相同，内容摘要也相同。"
_NOT_ATTRIBUTABLE = (
    "模型版本已经变化，原判定是针对旧版本作出的，不能归到当前版本。"
    "不是证据不存在，也不是原判定错误；需要针对当前版本的判定。"
)
_NO_BASIS = (
    "原记录封存时没有保存这条引用的比较依据（旧版本的记录）。本页不会用当前规则去补造，"
    "所以只能如实显示无法比较。"
)
_SUBJECT_GONE = (
    "这条证据所针对的构件，在本次记录里已经不在（去向见“记录给出的原因”）。"
    + "构件不在不等于已修复。"
)
_ONLY_VERSION = "模型版本变了，检查结果内容、检查要求、检查程序未变。"
_VERSION_AND_CONTENT = "模型版本、检查结果内容变了，检查要求、检查程序未变。"
_ONLY_SEMANTICS = "检查要求变了，模型版本、检查结果内容、检查程序未变。"
_SEMANTICS_AND_CONTENT = "检查结果内容、检查要求变了，模型版本、检查程序未变。"

_DETERMINATIONS_KEPT = {"比较依据一致": {_SAME_DETERMINATION: 6}}
_DETERMINATIONS_LEFT_BEHIND = {"未找到对应证据": {_NOT_ATTRIBUTABLE: 6}}

#: ``scenario -> (re-issue case, check-result rows, determination rows)``, each
#: rows table being ``state label -> {the fact said beside it: count}``.
ADAPTER_SCENARIOS = {
    "recheck-key-change-only": (
        "none",
        {"比较依据一致": {_REKEYED: 9}},
        _DETERMINATIONS_KEPT,
    ),
    "recheck-semantics-changed": (
        "none",
        {"比较依据一致": {_REKEYED: 7}, "比较依据有变化": {_ONLY_SEMANTICS: 2}},
        _DETERMINATIONS_KEPT,
    ),
    "recheck-requirement-relaxed": (
        "none",
        {"比较依据一致": {_REKEYED: 7}, "比较依据有变化": {_SEMANTICS_AND_CONTENT: 2}},
        _DETERMINATIONS_KEPT,
    ),
    "recheck-prior-without-basis": (
        "none",
        {"现有依据不足以比较": {_NO_BASIS: 9}},
        _DETERMINATIONS_KEPT,
    ),
    "recheck-producing-reissued": (
        "producing",
        {"比较依据有变化": {_ONLY_VERSION: 9}},
        _DETERMINATIONS_LEFT_BEHIND,
    ),
    "recheck-producing-reissued-content-changed": (
        "producing",
        {"比较依据有变化": {_VERSION_AND_CONTENT: 6, _ONLY_VERSION: 3}},
        _DETERMINATIONS_LEFT_BEHIND,
    ),
    "recheck-consuming-reissued": (
        "consuming",
        {"比较依据一致": {_REKEYED: 9}},
        _DETERMINATIONS_LEFT_BEHIND,
    ),
    "recheck-both-reissued": (
        "both",
        {"比较依据有变化": {_ONLY_VERSION: 9}},
        _DETERMINATIONS_LEFT_BEHIND,
    ),
    "recheck-member-gone": (
        "producing",
        {"比较依据有变化": {_ONLY_VERSION: 6}, "现有依据不足以比较": {_SUBJECT_GONE: 3}},
        _DETERMINATIONS_LEFT_BEHIND,
    ),
}


class AdapterScenarioTests(unittest.TestCase):
    """The nine recheck scenarios the adapter evaluates, as the page words them."""

    @classmethod
    def setUpClass(cls):
        from internal.doctor_adapter import scenario_envelope, scenario_index

        offered = {
            item["name"] for item in scenario_index() if item["name"].startswith("recheck-")
        }
        # Every recheck the adapter offers is worded here, and no other.
        assert offered == {*ADAPTER_SCENARIOS, "recheck-comparison"}, sorted(offered)
        cls.envelopes = {name: scenario_envelope(name) for name in ADAPTER_SCENARIOS}
        output = _run_model({name: item["record"] for name, item in cls.envelopes.items()})
        cls.models = output["models"]
        cls.vocabulary = output["vocabulary"]

    @staticmethod
    def _said(group):
        return {
            state["label"]: {fact["text"]: fact["count"] for fact in state["facts"]}
            for state in group["states"]
        }

    def test_each_scenario_says_which_side_and_what_became_of_each_kind_of_evidence(self):
        for name, (reissue, findings, determinations) in ADAPTER_SCENARIOS.items():
            model = self.models[name]
            with self.subTest(scenario=name):
                self.assertTrue(model["recognised"])
                self.assertEqual(model["reissue"]["name"], reissue)
                groups = {group["kind"]: group for group in model["evidenceGroups"]}
                self.assertEqual(sorted(groups), ["determination", "finding"])
                self.assertEqual(self._said(groups["finding"]), findings)
                self.assertEqual(self._said(groups["determination"]), determinations)
                self.assertEqual(groups["finding"]["count"], 9)
                self.assertEqual(groups["determination"]["count"], 6)
                self.assertEqual(len(model["subscopes"]), 8)

    def test_nothing_the_adapter_records_is_unrecognised(self):
        for name, model in self.models.items():
            with self.subTest(scenario=name):
                for subscope in model["subscopes"]:
                    self.assertTrue(subscope["condition"]["known"])
                    for row in subscope["evidence"]:
                        self.assertTrue(row["state"]["known"])
                        self.assertTrue(row["reason"]["known"])
                for item in model["items"]:
                    self.assertTrue(item["disposition"]["known"])

    def test_a_consuming_reissue_keeps_two_statements_apart(self):
        """The check results only changed key; the determinations cannot be attributed.

        Those are two facts about two kinds of evidence. Neither is said for the
        other, and they are never added into one count that could read "unchanged".
        """

        model = self.models["recheck-consuming-reissued"]
        groups = {group["kind"]: group for group in model["evidenceGroups"]}
        self.assertEqual(self._said(groups["finding"]), {"比较依据一致": {_REKEYED: 9}})
        self.assertEqual(
            self._said(groups["determination"]), {"未找到对应证据": {_NOT_ATTRIBUTABLE: 6}}
        )
        both_kinds = 0
        for subscope in model["subscopes"]:
            said = {
                group["kind"]: [state["code"] for state in group["states"]]
                for group in subscope["evidenceGroups"]
            }
            # Wherever a subscope cites both kinds, each has its own line.
            if len(said) == 2:
                both_kinds += 1
                self.assertEqual(
                    said, {"finding": ["equivalent"], "determination": ["no-counterpart"]}
                )
        self.assertGreater(both_kinds, 0)
        self.assertEqual(
            model["reissue"]["headline"], "接收方的模型重新发布了，交出方的模型没有变"
        )
        self.assertIn("针对旧版本作出的判定同样不能归到新版本。", model["reissue"]["caveats"])
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        self.assertIn("note(RECHECK.kindsNote)", screens)
        kinds = "检查结果和人工判定是两种证据，分开计数，不相加。"
        self.assertIn(f'kindsNote: "{kinds}"', vocabulary)

    def test_a_relaxed_requirement_and_a_repaired_model_read_differently(self):
        relaxed = self.models["recheck-requirement-relaxed"]
        repaired = self.models["recheck-producing-reissued-content-changed"]

        def notes(model, sentence):
            found = {
                note
                for subscope in model["subscopes"]
                for row in subscope["evidence"]
                if row["brief"] == sentence
                for note in row["notes"]
            }
            self.assertEqual(len(found), 1, sentence)
            return found.pop()

        self.assertEqual(relaxed["reissue"]["name"], "none")
        self.assertIn("不能据此说模型修好了", notes(relaxed, _SEMANTICS_AND_CONTENT))
        self.assertEqual(repaired["reissue"]["name"], "producing")
        after_reissue = notes(repaired, _VERSION_AND_CONTENT)
        self.assertIn("检查要求没有变，检查结果内容变了", after_reissue)
        # R4: the row does not say which way the result moved, and neither does the page.
        self.assertIn("不记录结果是变好还是变差", after_reissue)

    def test_every_present_member_reaches_the_subscope_the_record_named(self):
        """…and a member the record gives no ordinal for reaches none (R1)."""

        seen = {"present": 0, "left": 0}
        for name, model in self.models.items():
            record = self.envelopes[name]["record"]
            for item in model["items"]:
                with self.subTest(scenario=name, member=item["entry"]["member"]["keys"]):
                    if item["disposition"]["code"] != "present":
                        seen["left"] += 1
                        self.assertIsNone(item["current"])
                        continue
                    seen["present"] += 1
                    for current in item["current"]:
                        located = current["located"]
                        activity = record["activities"][located["activityIndex"]]
                        self.assertEqual(
                            activity["activity_ref"], item["outcome"]["activity_ref"]
                        )
                        self.assertEqual(located["subscope"]["ordinal"], current["ordinal"])
                        self.assertEqual(located["subscope"]["verdict"], current["verdict"])
        self.assertGreater(seen["present"], 0)
        self.assertGreater(seen["left"], 0)

    def test_an_example_is_described_in_the_directory_and_nowhere_else(self):
        """The directory may say what an example was given. A result page may not.

        This replaces a rule that every run be named by a number. That rule kept
        a cause the record does not carry (data gap R5) off the screen, and paid
        for it by making the directory unusable for everyone, to protect one
        walkthrough from a leaked answer. The line is now drawn where the claim
        is made: what an example was *given* is its builder's statement, shown
        in the directory and labelled as the example's description; what a run
        *found* is the record's, and only that reaches a result page.
        """

        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        labels = vocabulary[vocabulary.index("export const RUN_LABELS") :]
        labels = labels[: labels.index("};")]
        named = dict(re.findall(r'"(recheck-[a-z-]+)":\s*"([^"]+)"', labels))
        self.assertEqual(sorted(named), sorted({*ADAPTER_SCENARIOS, "recheck-comparison"}))
        self.assertEqual(len(set(named.values())), len(named))

        examples = vocabulary[vocabulary.index("export const EXAMPLES") :]
        examples = examples[: examples.index("\n};")]
        described = set(re.findall(r'"([a-z-]+)": \{', examples))
        self.assertEqual(described, {"member-evidence", "recheck-requirement-relaxed"})
        given = re.findall(r'given:\s*"([^"]+)"', examples)
        self.assertEqual(len(given), len(described))
        for sentence in given:
            # Said as what the example was handed, never as a finding.
            self.assertTrue(sentence.startswith("这个示例被给了："), sentence)

        # A described example has a name, and the name states only what its own
        # record holds: no model was re-issued, and a verdict differs.
        self.assertEqual(named["recheck-requirement-relaxed"], "模型未改，但交接判断发生变化")
        relaxed = self.models["recheck-requirement-relaxed"]
        self.assertEqual(relaxed["reissue"]["name"], "none")
        self.assertGreater(relaxed["verdictGroups"][0]["count"], 0)
        # The rest keep a number and say they are simulated; none states a cause.
        for name, label in named.items():
            if name in described:
                continue
            with self.subTest(scenario=name):
                self.assertRegex(label, r"^复检记录 \d+（模拟示例）$")

        # The description is rendered by the directory and by nothing else, and
        # the directory says whose words it is.
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        directory = screens[screens.index("function runs(") : screens.index("function record(")]
        elsewhere = screens.replace(directory, "")
        self.assertIn("EXAMPLES[run.run_id].given", directory)
        self.assertIn("EXAMPLE_NOTE", directory)
        # The tag that says this is the example's description, not a result.
        self.assertIn("DIRECTORY.exampleTag", directory)
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        self.assertIn('exampleTag: "示例说明"', vocabulary)
        code = "\n".join(
            line for line in elsewhere.splitlines() if not line.lstrip().startswith("//")
        )
        self.assertEqual(
            re.findall(r"\bEXAMPLES\b|\bEXAMPLE_NOTE\b", code), ["EXAMPLES", "EXAMPLE_NOTE"]
        )
        for file in ("recheck-model.js", "app.js"):
            with self.subTest(file=file):
                self.assertNotIn("EXAMPLES", (STATIC / file).read_text(encoding="utf-8"))
        # The adapter's scenario name is not printed beside a run this preview names.
        self.assertIn(
            'Object.hasOwn(RUN_LABELS, run.run_id) ? null : [" ", code(run.run_id)]', screens
        )

    def test_the_words_cover_the_pack_and_say_what_a_verdict_means_for_the_work(self):
        """Every gloss is keyed on the Pack's vocabulary; none reads as "a check passed".

        A verdict is a statement about one activity of the receiving side, in an
        assessed scope (Checkpoint B section 1). The glosses carry that
        consequence, the activities are named as work, and every resolution kind,
        consequence kind and (evidence requirement, outcome) the Pack declares
        has words here — an unglossed one would reach the manager as
        "unrecognised", which is what happened to three of the ten.
        """

        pack = tomllib.loads(
            (
                PROJECT_ROOT
                / "purpose-packs"
                / "interdisciplinary-coordination-readiness"
                / "pack.toml"
            ).read_text(encoding="utf-8")
        )
        words = self.vocabulary
        self.assertEqual(
            sorted(words["activityNames"]),
            sorted(item["activity_id"] for item in pack["activities"]),
        )
        routes = pack["resolution_routes"]
        self.assertEqual(
            sorted(words["resolutionKinds"]), sorted(item["resolution_kind"] for item in routes)
        )
        self.assertEqual(len(words["resolutionKinds"]), 10)
        self.assertEqual(
            sorted(words["consequenceKinds"]),
            sorted({kind for item in routes for kind in item["consequence_kinds"]}),
        )
        self.assertEqual(
            sorted(words["leafReadings"]),
            sorted(
                f"{item['evidence_requirement_id']}/{outcome}"
                for item in pack["evidence_requirements"]
                for outcome in item["outcomes"]
            ),
        )
        # An UNKNOWN route opens, as the Pack's own next_action does, by saying
        # it is not a model defect; a BLOCKED route never does.
        unknown = {
            branch["gap_kind"]
            for node in pack["decision_nodes"]
            for branch in node["branches"]
            if "gap_kind" in branch
        }
        for item in routes:
            kind = item["resolution_kind"]
            with self.subTest(kind=kind):
                self.assertEqual(
                    kind in unknown, item["next_action"].startswith("Not a model defect")
                )
                # "Not a *known* defect": the Pack's words, and less than "not a defect".
                self.assertEqual(
                    kind in unknown, words["resolutionKinds"][kind].startswith("不是已知的")
                )
                self.assertNotIn("不是模型缺陷", words["resolutionKinds"][kind])
        # The storey rules check containment in a storey or a space, and the
        # words say that and no more: not that the receiving model has the storey.
        for key in ("in-model-position-not-evaluated", "mep-element-not-spatially-assigned"):
            self.assertIn("楼层或空间归属", words["resolutionKinds"][key])
        for key, text in words["leafReadings"].items():
            if key.startswith("in-model-position/"):
                self.assertIn("楼层或空间归属", text)
        static = "".join(path.read_text(encoding="utf-8") for path in sorted(STATIC.iterdir()))
        for said in (
            "接收方模型里也有的楼层",
            "天花综合",
            "综合天花",
            "吊顶反向图",
            "无需处理",
        ):
            with self.subTest(never=said):
                self.assertNotIn(said, static)
        self.assertEqual(
            words["activityNames"]["ceiling-and-bulkhead-geometry"]["name"],
            "吊顶平面与包封布置",
        )

        # The action and recheck sentences: one pair per resolution kind, for
        # the one Pack version they were written against.
        self.assertEqual(sorted(words["actions"]), sorted(words["resolutionKinds"]))
        self.assertEqual(
            words["actionPack"], {"id": pack["pack_id"], "version": pack["pack_version"]}
        )
        for kind, entry in words["actions"].items():
            with self.subTest(action=kind):
                self.assertEqual(sorted(entry), ["action", "recheck"])
                for text in entry.values():
                    self.assertNotRegex(
                        text, r"Revit|参数|导出映射|requirement_key|Overlay|Pack"
                    )
        self.assertEqual(
            words["actions"]["asset-identity-not-evaluated"]["action"],
            "现有资产标识规则没有覆盖到这个构件，所以它有没有资产标识还没有被评估，不能判断是否缺少；"
            "这项工作能否开始也因此无法判断。先确认项目约定是否要求它具备资产标识，"
            "以及规则该不该覆盖到它。在确认之前，这不表示它必须具备资产标识。",
        )
        # Nothing checked whether the element carries the property set, so no
        # sentence says it is not missing one — and none makes it an obligation.
        static = "".join(path.read_text(encoding="utf-8") for path in sorted(STATIC.iterdir()))
        self.assertNotIn("这不是缺资产标识", static)
        # The record reaches one element, never its class.
        self.assertNotIn("这类构件", static)
        # "重新发布" is said of a model only; the consequence is about documents.
        self.assertNotIn(
            "重新发布", words["consequenceKinds"]["re-identification-and-reissue-risk"]
        )
        self.assertIn("文件", words["consequenceKinds"]["re-identification-and-reissue-risk"])
        # The head-of-page notice says which kinds a conclusion's evidence *may*
        # be and where each citation's source is shown. It does not say a page
        # holds all of them: no record does, and a sentence about a whole page
        # cannot assert what that page contains. The directory no longer says it
        # a second time under its heading.
        vocabulary_source = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        for name in ("DEMO_NOTICE",):
            notice = vocabulary_source[vocabulary_source.index(f"export const {name} =") :]
            notice = notice[: notice.index(";\n")]
            with self.subTest(notice=name):
                for said in (
                    "一个结论的证据可能是",
                    "真实检查的结果",
                    "模拟的检查结果",
                    "模拟的人工判定",
                    "具体是哪一种，看",
                    "“依据”一行",
                    "逐条引用",
                ):
                    self.assertIn(said, notice)
                for asserted in ("既有", "也有", "都有", "记录里的证据"):
                    self.assertNotIn(asserted, notice)
        self.assertNotIn("DIRECTORY_NOTE", (STATIC / "screens.js").read_text(encoding="utf-8"))
        self.assertNotIn("DIRECTORY_NOTE", vocabulary_source)
        self.assertEqual(
            words["verdictLabels"],
            {"READY": "可以开始", "BLOCKED": "受阻", "UNKNOWN": "无法判断"},
        )

        # Verdicts: the consequence for the work, and the scope it holds in.
        verdicts = words["verdictWords"]
        self.assertEqual(sorted(verdicts), ["BLOCKED", "READY", "UNKNOWN"])
        self.assertIn("这项工作可以开始", verdicts["READY"])
        self.assertIn("在本次评估范围内", verdicts["READY"])
        self.assertIn("没有证据缺口", verdicts["READY"])
        self.assertIn("阻止这项工作", verdicts["BLOCKED"])
        self.assertIn("这项工作能否开始无法决定", verdicts["UNKNOWN"])
        self.assertIn("既不能放行，也不能拒绝", verdicts["UNKNOWN"])
        for text in verdicts.values():
            for claim in ("检查通过", "合格", "没有问题"):
                with self.subTest(claim=claim):
                    self.assertNotIn(claim, text)
        self.assertIn("评估范围", words["verdictScope"])
        self.assertIn("模型版本", words["verdictScope"])

        # A READY reached because the element penetrates nothing says so.
        through_nothing = words["leafReadings"]["penetration-determination/no-penetration"]
        self.assertIn("开洞情况没有被评估", through_nothing)
        self.assertIn("这不是“开洞没问题”", through_nothing)

        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        for text in (screens, vocabulary):
            self.assertNotIn("检查内容", text)
            self.assertNotIn("检查清单", text)
        self.assertIn('recheck: "完成后拿什么复检"', vocabulary)
        self.assertIn("ACTION.recheck", screens)
        for text in (screens, vocabulary):
            self.assertNotIn("可以再次复检", text)

    def test_a_requirement_edit_is_said_beside_the_verdict_it_bears_on(self):
        """Two recorded facts side by side; the page concludes nothing from them.

        The one verdict that moved in the relaxed example is READY under an
        edited requirement. A gloss that said "can start" and left the edit among
        the evidence rows would be a status without its predicate.
        """

        relaxed = self.models["recheck-requirement-relaxed"]
        record = self.envelopes["recheck-requirement-relaxed"]["record"]
        for subscope, outcome in zip(
            relaxed["subscopes"], record["successor"]["subscopes"], strict=True
        ):
            expected = sum(
                "requirement-semantics" in row.get("changed_aspects", [])
                for row in outcome["evidence_carry_over"]
            )
            self.assertEqual(subscope["requirementChanged"], expected)
            for item in subscope["items"]:
                self.assertEqual(item["requirementChanged"], expected)
        moved = [
            item for item in relaxed["items"] if item["verdictChange"]["kind"] == "changed"
        ]
        self.assertEqual([item["requirementChanged"] for item in moved], [2])
        self.assertEqual(sum(1 for item in relaxed["items"] if item["requirementChanged"]), 3)
        for name in ("recheck-key-change-only", "recheck-producing-reissued"):
            with self.subTest(scenario=name):
                self.assertFalse(
                    any(item["requirementChanged"] for item in self.models[name]["items"])
                )

        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        recheck = screens[
            screens.index("// S4 — recheck") : screens.index("// SX — real refusal")
        ]
        # Beside the verdict on the card, on the one-line items, on the item
        # page and in the result block; never inside a collapsed block.
        self.assertEqual(recheck.count("requirementNote("), 5)
        note = recheck[recheck.index("function requirementNote(") :]
        note = note[: note.index("\n}\n")]
        self.assertNotIn("details", note)
        self.assertNotRegex(note, r"READY|BLOCKED|UNKNOWN|verdict")
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        sentence = vocabulary[vocabulary.index("export const REQUIREMENT_CHANGED_NOTE") :]
        sentence = sentence[: sentence.index(";\n")]
        self.assertIn("记录不说明是放宽还是收紧", sentence)
        for claim in ("所以", "因此", "修好", "放宽了"):
            self.assertNotIn(claim, sentence)

    def test_the_reading_behind_a_verdict_is_shown_when_the_record_carries_one(self):
        """`current_leaf_outcomes`, worded from the requirement the path ended on."""

        relaxed = self.models["recheck-requirement-relaxed"]
        readings = {}
        for item in relaxed["items"]:
            for current in item["current"]:
                step = current["located"]["subscope"]["path"][-1]
                key = f"{step['evidence_requirement_id']}/{current['leafOutcome']}"
                readings.setdefault(current["verdict"], set()).add(key)
                self.assertIn(key, self.vocabulary["leafReadings"])
                # The record's own reading at the end of the path it named.
                self.assertEqual(step["outcome"], current["leafOutcome"])
        self.assertEqual(
            readings["READY"],
            {
                "penetration-determination/no-penetration",
                "opening-status/cross-referenced",
                "cross-model-alignment/confirmed",
                "asset-identity/satisfied",
            },
        )
        gone = self.models["recheck-member-gone"]
        self.assertTrue(any(item["current"] is None for item in gone["items"]))
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        self.assertIn(": missing(LEAF_READING_WORDS.notCarried)", screens)
        self.assertEqual(screens.count("readingRow(item),"), 1)

    def test_what_is_left_to_do_is_what_the_record_gives_a_next_step_for(self):
        """Three groups by what the record asks, read off the place it named.

        An item is "to do" when the subscope the record gave for it carries a
        next action; it has no group of its own for a verdict word, and no group
        is an overall status.
        """

        for name, model in self.models.items():
            record = self.envelopes[name]["record"]
            activities = {item["activity_ref"]: item for item in record["activities"]}
            with self.subTest(scenario=name):
                self.assertEqual(
                    [group["kind"] for group in model["actionGroups"]],
                    ["open", "unplaced", "none"],
                )
                placed = [
                    tuple(index) for group in model["actionGroups"] for index in group["items"]
                ]
                self.assertEqual(
                    sorted(placed),
                    sorted(
                        (item["subscopeIndex"], item["memberIndex"]) for item in model["items"]
                    ),
                )
                for group in model["actionGroups"]:
                    self.assertEqual(group["count"], len(group["items"]))
                    for subscope_index, member_index in group["items"]:
                        outcome = record["successor"]["subscopes"][subscope_index]
                        entry = outcome["dispositions"][member_index]
                        if "current_ordinals" not in entry:
                            self.assertEqual(group["kind"], "unplaced")
                            continue
                        asked = any(
                            "next_action" in subscope.get("route", {})
                            for subscope in activities[outcome["activity_ref"]]["subscopes"]
                            if subscope["ordinal"] in entry["current_ordinals"]
                        )
                        self.assertEqual(group["kind"], "open" if asked else "none")
        relaxed = {
            group["kind"]: group["count"]
            for group in self.models["recheck-requirement-relaxed"]["actionGroups"]
        }
        self.assertEqual(relaxed, {"open": 7, "unplaced": 0, "none": 6})
        model = (STATIC / "recheck-model.js").read_text(encoding="utf-8")
        action = model[
            model.index("function actionKind(") : model.index("export function handoverSide(")
        ]
        self.assertNotRegex(action, r"READY|BLOCKED|UNKNOWN|verdict|score|Math\.|%")
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        groups = vocabulary[vocabulary.index("export const ACTION_GROUPS") :]
        groups = groups[: groups.index("\n};")]
        for claim in ("已解决", "修好", "已修复", "通过", "就绪", "评分", "%", "不用复核"):
            with self.subTest(claim=claim):
                for sentence in re.findall(rf"[^。\"]*{claim}[^。\"]*", groups):
                    self.assertRegex(sentence, "不")

    def test_the_two_recorded_verdicts_are_grouped_and_counted_first(self):
        """Changed, not placed, unchanged — counts of what the record holds."""

        def said(name):
            return {
                group["kind"]: {
                    (transition["from"], tuple(transition["to"])): transition["count"]
                    for transition in group["transitions"]
                }
                for group in self.models[name]["verdictGroups"]
            }

        after_a_reissue = {
            "changed": {("READY", ("UNKNOWN",)): 4},
            "unplaced": {("READY", ()): 1, ("BLOCKED", ()): 1},
            "unchanged": {("UNKNOWN", ("UNKNOWN",)): 4, ("BLOCKED", ("BLOCKED",)): 3},
        }
        nothing_moved = {
            "changed": {},
            "unplaced": {},
            "unchanged": {
                ("READY", ("READY",)): 5,
                ("UNKNOWN", ("UNKNOWN",)): 4,
                ("BLOCKED", ("BLOCKED",)): 4,
            },
        }
        expected = {
            "recheck-key-change-only": nothing_moved,
            "recheck-semantics-changed": nothing_moved,
            "recheck-prior-without-basis": nothing_moved,
            "recheck-requirement-relaxed": {
                "changed": {("BLOCKED", ("READY",)): 1},
                "unplaced": {},
                "unchanged": {
                    ("READY", ("READY",)): 5,
                    ("UNKNOWN", ("UNKNOWN",)): 4,
                    ("BLOCKED", ("BLOCKED",)): 3,
                },
            },
            "recheck-producing-reissued": after_a_reissue,
            "recheck-consuming-reissued": after_a_reissue,
            "recheck-both-reissued": after_a_reissue,
            "recheck-producing-reissued-content-changed": {
                "changed": {("READY", ("UNKNOWN",)): 4, ("BLOCKED", ("READY",)): 3},
                "unplaced": {("READY", ()): 1, ("BLOCKED", ()): 1},
                "unchanged": {("UNKNOWN", ("UNKNOWN",)): 4},
            },
            "recheck-member-gone": {
                "changed": {("READY", ("UNKNOWN",)): 2},
                "unplaced": {("READY", ()): 3, ("BLOCKED", ()): 2},
                "unchanged": {("UNKNOWN", ("UNKNOWN",)): 4, ("BLOCKED", ("BLOCKED",)): 2},
            },
        }
        self.assertEqual(sorted(expected), sorted(ADAPTER_SCENARIOS))
        for name, groups in expected.items():
            with self.subTest(scenario=name):
                self.assertEqual(said(name), groups)

    def test_every_item_is_in_exactly_one_group_and_the_groups_follow_the_record(self):
        for name, model in self.models.items():
            record = self.envelopes[name]["record"]
            placed = [
                tuple(index)
                for group in model["verdictGroups"]
                for transition in group["transitions"]
                for index in transition["items"]
            ]
            with self.subTest(scenario=name):
                self.assertEqual(
                    sorted(placed),
                    sorted(
                        (item["subscopeIndex"], item["memberIndex"]) for item in model["items"]
                    ),
                )
                self.assertEqual(
                    [group["kind"] for group in model["verdictGroups"]],
                    ["changed", "unplaced", "unchanged"],
                )
                for group in model["verdictGroups"]:
                    self.assertEqual(
                        group["count"], sum(item["count"] for item in group["transitions"])
                    )
                    for transition in group["transitions"]:
                        for subscope_index, member_index in transition["items"]:
                            outcome = record["successor"]["subscopes"][subscope_index]
                            entry = outcome["dispositions"][member_index]
                            # Both ends are read off the record, value for value.
                            self.assertEqual(transition["from"], outcome["prior_verdict"])
                            self.assertEqual(
                                transition["to"], entry.get("current_verdicts", [])
                            )
                            self.assertEqual(
                                group["kind"] == "unplaced", "current_ordinals" not in entry
                            )

    def test_a_verdict_that_moved_under_unchanged_models_is_said_to_have(self):
        """The relaxed rule: one item BLOCKED to READY, and no model was re-issued."""

        relaxed = self.models["recheck-requirement-relaxed"]
        changed = relaxed["verdictGroups"][0]
        self.assertEqual(relaxed["reissue"]["name"], "none")
        self.assertEqual(changed["count"], 1)
        self.assertIn("两侧模型都没有重新发布，这些项的判断却变了", changed["note"])
        self.assertIn("变化不来自模型改动", changed["note"])
        for name in (
            "recheck-producing-reissued",
            "recheck-consuming-reissued",
            "recheck-both-reissued",
        ):
            note = self.models[name]["verdictGroups"][0]["note"]
            with self.subTest(scenario=name):
                self.assertIn("模型重新发布过", note)
                self.assertIn("不说明原来的问题怎样了", note)
        quiet = self.models["recheck-key-change-only"]["verdictGroups"]
        self.assertEqual(quiet[0]["note"], "没有判断变了的项。")
        self.assertEqual(quiet[1]["note"], "每一项记录都给出了当前情况。")

    def test_no_group_is_a_status_a_score_or_a_claim_of_repair(self):
        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        groups = vocabulary[vocabulary.index("export const VERDICT_GROUPS") :]
        groups = groups[: groups.index("\n};")]
        for claim in ("已解决", "修好", "已修复", "通过", "就绪", "评分", "%"):
            with self.subTest(claim=claim):
                for sentence in re.findall(rf"[^。\"]*{claim}[^。\"]*", groups):
                    self.assertRegex(sentence, "不")
        model = (STATIC / "recheck-model.js").read_text(encoding="utf-8")
        change = model[
            model.index("function verdictChange(") : model.index(
                "export function recheckModel("
            )
        ]
        # Grouping and counting only: nothing is ranked, summed into one figure or divided.
        self.assertNotRegex(
            change, r"[/%]\s*\w+\.length|Math\.|score|ready|READY|BLOCKED|UNKNOWN"
        )

    def test_the_walkthrough_script_names_runs_the_adapter_offers(self):
        text = (
            PROJECT_ROOT / "docs" / "product" / "2026-10-02-doctor-recheck-walkthrough.md"
        ).read_text(encoding="utf-8")
        named = set(re.findall(r"`(recheck-[a-z-]+)`", text))
        self.assertEqual(named, {*ADAPTER_SCENARIOS, "recheck-comparison"} & named)
        for name in (
            "recheck-comparison",
            "recheck-key-change-only",
            "recheck-semantics-changed",
            "recheck-requirement-relaxed",
            "recheck-producing-reissued",
            "recheck-consuming-reissued",
            "recheck-both-reissued",
            "recheck-prior-without-basis",
        ):
            with self.subTest(run=name):
                self.assertIn(name, named)


#: Where a record keeps a citation. Every other marked string in a record is an
#: identifier of a run, model or content, not evidence a conclusion cites.
_CITATION_KEYS = {"finding_keys", "finding_key", "reference", "citation", "current_citation"}


def _marked_citations(value, key=None, under_context=False):
    """Every fixture-marked citation in a record, found without the screens' walk."""

    if isinstance(value, dict):
        for inner_key, inner in value.items():
            yield from _marked_citations(
                inner, inner_key, under_context or inner_key == "context_citations"
            )
    elif isinstance(value, list):
        for inner in value:
            yield from _marked_citations(inner, key, under_context)
    elif (
        isinstance(value, str)
        and value.startswith("fixture")
        and key in _CITATION_KEYS
        and not under_context
    ):
        yield value


class SourceSummaryTests(unittest.TestCase):
    """The short line at the head of an example page (PM Q2, 2026-10-08).

    It names the kinds of evidence one record's conclusions cite. If the walk
    behind it missed a simulated citation, the line would call a record real
    that is not, so it is checked against every record the adapter offers.
    """

    @classmethod
    def setUpClass(cls):
        from internal.doctor_adapter import scenario_envelope, scenario_index

        cls.records = {}
        for item in scenario_index():
            if item["mode"] != "fixture":
                continue
            envelope = scenario_envelope(item["name"])
            if "record" in envelope:
                cls.records[item["name"]] = envelope["record"]
        output = _run_model(cls.records)
        cls.citations = output["citations"]
        cls.vocabulary = output["vocabulary"]

    def kinds(self, name):
        found = self.citations[name]
        marked = lambda citation: citation.startswith("fixture")  # noqa: E731
        kinds = set()
        for citation in found["findings"]:
            kinds.add("finding-fixture" if marked(citation) else "finding-real")
        for citation in found["determinations"]:
            kinds.add("determination-fixture" if marked(citation) else "determination-unmarked")
        return kinds

    def test_every_example_record_is_walked(self):
        self.assertGreaterEqual(len(self.records), 12)

    def test_no_simulated_citation_is_missed(self):
        for name, document in self.records.items():
            found = self.citations[name]
            walked = set(found["findings"]) | set(found["determinations"])
            with self.subTest(record=name):
                missed = set(_marked_citations(document)) - walked
                self.assertEqual(missed, set())

    def test_every_cited_key_and_reference_is_walked(self):
        for name, document in self.records.items():
            found = self.citations[name]
            with self.subTest(record=name):
                text = json.dumps(found)
                for activity in document.get("activities", []):
                    for subscope in activity["subscopes"]:
                        for step in subscope["path"]:
                            for reading in step["readings"]:
                                for key in reading.get("finding_keys", []):
                                    self.assertIn(key, found["findings"])
                                for cited in reading.get("cited_determinations", []):
                                    self.assertIn(cited["reference"], found["determinations"])
                self.assertNotIn('""', text)

    def test_context_citations_are_not_a_conclusions_basis(self):
        for name, document in self.records.items():
            context = set()
            for activity in document.get("activities", []):
                for subscope in activity["subscopes"]:
                    for step in subscope["path"]:
                        context |= set(step.get("context_citations", []))
            cited = set()
            for activity in document.get("activities", []):
                for subscope in activity["subscopes"]:
                    for step in subscope["path"]:
                        for reading in step["readings"]:
                            cited |= set(reading.get("finding_keys", []))
            only_context = context - cited
            with self.subTest(record=name):
                self.assertEqual(only_context & set(self.citations[name]["findings"]), set())

    def test_the_examples_mix_sources_so_no_record_wide_word_would_be_true(self):
        """The counterfactual: one word for a whole record would be wrong here."""

        kinds = {name: self.kinds(name) for name in self.records}
        mixed = [
            name
            for name, found in kinds.items()
            if "finding-real" in found
            and {"finding-fixture", "determination-fixture"} & found
        ]
        self.assertIn("member-evidence", mixed)
        self.assertEqual(kinds["member-evidence"], {"finding-real", "determination-fixture"})
        self.assertTrue(any(len(found) >= 3 for found in kinds.values()))

    def test_the_summary_names_each_kind_as_the_tag_beside_a_conclusion_does(self):
        summary = self.vocabulary["sourceSummary"]
        provenance = self.vocabulary["citationProvenance"]
        self.assertEqual(sorted(summary["kinds"]), sorted(provenance))
        for name, entry in provenance.items():
            with self.subTest(kind=name):
                self.assertEqual(summary["kinds"][name], entry["short"])
        self.assertIn("{kinds}", summary["cites"])
        self.assertIn("随附的模拟示例，不是你的模型", summary["lead"])
        self.assertIn("项目设定为演示用", summary["lead"])
        self.assertIn("不能用于正式项目决定", summary["lead"])
        for text in (summary["lead"], summary["cites"], summary["noRecord"]):
            with self.subTest(text=text):
                self.assertIn("依据" if text is not summary["lead"] else "模拟", text)
                for blanket in ("全部", "都是", "均为", "既有", "也有"):
                    self.assertNotIn(blanket, text)

    def test_the_directory_says_each_example_is_one_check_record(self):
        self.assertEqual(
            self.vocabulary["directory"]["exampleIntro"], "每个示例是一份检查记录。"
        )
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        self.assertIn("note(DIRECTORY.exampleIntro)", screens)

    def test_the_full_notice_is_one_fold_away_and_the_summary_outside_it(self):
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        body = screens[screens.index("function sourceNotice(") :]
        body = body[: body.index("\n}\n")]
        self.assertIn('"details"', body)
        self.assertIn('"summary"', body)
        self.assertIn("SOURCE_SUMMARY.lead", body)
        self.assertIn("recordCitations(envelope.record)", body)
        self.assertLess(body.index('"summary"'), body.index("DEMO_NOTICE"))
        self.assertNotIn("open", re.sub(r"//.*", "", body).replace("SOURCE_SUMMARY", ""))


if __name__ == "__main__":
    unittest.main()
