"""Result presentation keeps observations, objects and recheck claims distinct."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "doctor" / "static"


def present(payload):
    node = shutil.which("node")
    if not node:
        if os.environ.get("CI"):
            raise AssertionError("Node is required for result presentation tests")
        raise unittest.SkipTest("Node unavailable")
    with tempfile.TemporaryDirectory() as folder:
        work = Path(folder)
        shutil.copyfile(STATIC / "enterprise-results.js", work / "results.mjs")
        driver = '''
import { readFileSync } from "node:fs";
import { resultSummary, problemReading, recheckSummary } from "./results.mjs";
const input = JSON.parse(readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify({
  summary: resultSummary(input.run), changes: recheckSummary(input.run),
  readings: (input.run.blockers || []).map(b =>
    problemReading(input.run, b, input.lang || "en")),
}));
'''
        (work / "driver.mjs").write_text(driver, encoding="utf-8")
        result = subprocess.run([node, "driver.mjs"], cwd=work,
                                input=json.dumps(payload).encode(), capture_output=True)
    if result.returncode:
        raise AssertionError(result.stderr.decode("utf-8", "replace"))
    return json.loads(result.stdout)


class EnterpriseResultsTests(unittest.TestCase):
    def test_objects_are_not_observations_and_zero_is_an_actual_value(self):
        result = present({"run": {"record": {}, "conclusion": {"status": "BLOCKED"},
            "blockers": [
                {"kind": "machine", "verdict": "BLOCKED", "subject_keys": ["slot::a"],
                 "actual": 0, "finding_key": "observed"},
                {"kind": "manual", "verdict": "UNKNOWN", "subject_keys": ["slot::a"]},
                {"kind": "unsupported", "verdict": "UNKNOWN", "subject_keys": ["slot::b"]},
            ]}})
        self.assertEqual(result["summary"], {"objects": 2, "failed": 1,
                         "manualUnmet": 0, "pending": 2, "observations": 3})
        self.assertEqual(result["readings"][0]["actual"], "0")
        self.assertEqual(result["readings"][1]["label"], "Human evidence needed")
        self.assertEqual(result["readings"][2]["label"], "Not executed this run")

    def test_empty_observation_differs_from_unexecuted_and_manual_values(self):
        result = present({"lang": "zh", "run": {"evaluation": {"elements": [
            {"element_key": "bad", "identity_comparable": False}]}, "blockers": [
            {"kind": "machine", "verdict": "BLOCKED", "finding_key": "x", "actual": ""},
            {"kind": "machine", "verdict": "UNKNOWN", "actual": ""},
            {"blocker_id": "m", "kind": "manual", "verdict": "BLOCKED"},
            {"kind": "machine", "verdict": "UNKNOWN", "subject_keys": ["bad"]}],
            "evidence_requests": [{"blocker_id": "m", "current_outcome": "unmet"}]}})
        readings = result["readings"]
        self.assertEqual([r["actual"] for r in readings[:3]],
                         ["空值", "未取得检查结果", "人工记录：未满足"])
        self.assertEqual(readings[3]["label"], "构件身份待核对")

    def test_recheck_summary_does_not_call_deletion_reclassification_or_evidence_a_repair(self):
        changes = ["rule_recheck_passed", "missing", "class_changed", "scope_excluded",
                   "not_comparable", "evidence_updated", "remaining", "remaining"]
        result = present({"run": {"change_summary": {"outcomes": [
            {"change": kind, "after": "UNKNOWN" if index == 7 else "BLOCKED"}
            for index, kind in enumerate(changes)]}}})
        self.assertEqual(result["changes"], {"rule_recheck_passed": 1, "missing": 1,
            "class_changed": 1, "scope_excluded": 1, "not_comparable": 1,
            "evidence_updated": 1, "remaining_BLOCKED": 1, "remaining_UNKNOWN": 1})

    def test_unexecuted_coverage_is_not_called_a_machine_violation(self):
        result = present({"run": {"evaluation": {"coverage": [
            {"requirement_key": "x", "support": "unsupported"}]}, "blockers": [
            {"kind": "machine", "verdict": "UNKNOWN", "requirement_key": "x"}]}})
        self.assertEqual(result["readings"][0]["label"], "Not executed this run")
