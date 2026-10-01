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
import unittest
from pathlib import Path

from doctor_recheck_cases import HANDOVER, REISSUE_SIDES, recheck_cases
from helpers import PROJECT_ROOT

from epc_control_tower.purpose.assessment import record

STATIC = PROJECT_ROOT / "doctor" / "static"

_DRIVER = """
import { readFileSync } from "node:fs";
import { recheckModel } from "./recheck-model.js";
import * as vocabulary from "./vocabulary.js";

const cases = JSON.parse(readFileSync(0, "utf8"));
const models = {};
for (const [name, document] of Object.entries(cases)) models[name] = recheckModel(document);
const keys = (name) => Object.keys(vocabulary[name]);
process.stdout.write(
  JSON.stringify({
    models,
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
        for name in ("recheck-model.js", "vocabulary.js"):
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
            "成员不在不等于已修复", self.vocabulary["reasonEntries"]["subject-not-present"]
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

    def test_the_limits_and_the_provenance_tags_are_never_inside_a_collapsed_block(self):
        limits = self._function("limits")
        self.assertIn("RECHECK_LIMITS", limits)
        self.assertNotIn("details", limits)
        for name in ("recheck", "recheckItem"):
            with self.subTest(screen=name):
                self.assertIn("limits()", self._function(name))
        card = self._function("evidenceCard")
        collapsed = card[card.index('"details"') :]
        shown = card[: card.index('"details"')]
        self.assertEqual(shown.count("provenance("), 2)
        self.assertNotIn("provenance(", collapsed)
        for key in ('"citation"', '"current_citation"', '"cause"'):
            with self.subTest(open=key):
                self.assertIn(key, shown)

    def test_the_way_back_returns_to_the_item_that_was_opened(self):
        app = (STATIC / "app.js").read_text(encoding="utf-8")
        self.assertIn('main.querySelector("[data-return-focus]")', app)
        self.assertIn(
            "lastRecheckItem = { runId: state.runId, subscopeIndex, memberIndex }", self.recheck
        )
        self.assertIn('"data-return-focus": here ? true : null', self.recheck)
        self.assertIn("返回复检事项列表", self._function("recheckItem"))


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
    "这条证据所针对的成员，在本次记录里已经不在（去向见“记录给出的原因”）。"
    + "成员不在不等于已修复。"
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
        self.assertIn("检查结果和判定是两种证据，分开计数，不相加。", screens)

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

    def test_a_run_name_states_no_cause(self):
        """A name is a number. What happened is for the page to show from the record.

        The record does not carry why a rule changed or which way (data gap R5),
        so a name saying "a rule was relaxed" would be the preview's own
        conclusion — and it would hand a walkthrough participant the answer.
        """

        vocabulary = (STATIC / "vocabulary.js").read_text(encoding="utf-8")
        labels = vocabulary[vocabulary.index("export const RUN_LABELS") :]
        labels = labels[: labels.index("};")]
        named = dict(re.findall(r'"(recheck-[a-z-]+)":\s*"([^"]+)"', labels))
        self.assertEqual(sorted(named), sorted({*ADAPTER_SCENARIOS, "recheck-comparison"}))
        self.assertEqual(len(set(named.values())), len(named))
        for name, label in named.items():
            with self.subTest(scenario=name):
                self.assertRegex(label, r"^复检记录 \d+（夹具）$")
        # The adapter's scenario name is not printed beside a run this preview names.
        screens = (STATIC / "screens.js").read_text(encoding="utf-8")
        self.assertIn(
            'Object.hasOwn(RUN_LABELS, run.run_id) ? null : [" ", code(run.run_id)]', screens
        )

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
        self.assertIn("两侧模型都没有重新发布，这些项的裁决却变了", changed["note"])
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
        self.assertEqual(quiet[0]["note"], "没有裁决变了的项。")
        self.assertEqual(quiet[1]["note"], "每一项记录都给出了当前对应的子范围。")

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


if __name__ == "__main__":
    unittest.main()
