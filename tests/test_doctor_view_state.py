"""Same-check UI continuity without a durable or shareable model search query."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "doctor" / "static"

DRIVER = '''
import { readFileSync } from "node:fs";
const input = JSON.parse(readFileSync(0, "utf8"));
const memory = new Map();
globalThis.location = { hash: "#/local/check-a/finding/one" };
globalThis.sessionStorage = {
  getItem: (key) => memory.get(key) ?? null,
  setItem: (key, value) => memory.set(key, value),
  removeItem: (key) => memory.delete(key),
};
if (input.bad !== undefined) {
  memory.set("doctor.ui.language-handoff", input.bad);
  const m = await import("./view-state.js");
  process.stdout.write(JSON.stringify({ view: m.workspaceView, kept: [...memory.keys()] }));
} else {
  const first = await import("./view-state.js");
  Object.assign(first.selectRun("local/check-a"), {
    query: "private object name", status: "FAIL", selected: "one",
  });
  const before = {...first.workspaceView};
  const writesBeforeLanguage = [...memory.keys()];
  first.carryForLanguage();
  const locale = await import("./view-state.js?language");
  const after = {...locale.workspaceView};
  const kept = [...memory.keys()];
  const refresh = await import("./view-state.js?ordinary-refresh");
  const ordinary = {...refresh.workspaceView};
  const other = {...locale.selectRun("local/check-b")};
  process.stdout.write(JSON.stringify({
    before, writesBeforeLanguage, after, kept, ordinary, other,
  }));
}
'''


def run_state(payload):
    node = shutil.which("node")
    if node is None:
        if os.environ.get("CI"):
            raise AssertionError("Node is required for the UI state gate")
        raise unittest.SkipTest("Node is required for the UI state gate")
    with tempfile.TemporaryDirectory() as directory:
        work = Path(directory)
        shutil.copyfile(STATIC / "view-state.js", work / "view-state.js")
        (work / "package.json").write_text('{"type":"module"}\n', encoding="utf-8")
        (work / "driver.mjs").write_text(DRIVER, encoding="utf-8")
        result = subprocess.run(
            [node, "driver.mjs"], cwd=work, input=json.dumps(payload).encode("utf-8"),
            capture_output=True, check=False,
        )
    if result.returncode:
        raise AssertionError(result.stderr.decode("utf-8", "replace"))
    return json.loads(result.stdout)


class ViewStateTests(unittest.TestCase):
    def test_language_handoff_is_consumed_once_and_another_check_resets_state(self):
        result = run_state({})
        expected = {
            "run": "local/check-a", "query": "private object name",
            "status": "FAIL", "selected": "one",
        }
        self.assertEqual(result["before"], expected)
        self.assertEqual(result["writesBeforeLanguage"], [])
        self.assertEqual(result["after"], expected)
        self.assertEqual(result["kept"], [])
        self.assertEqual(result["ordinary"], {
            "run": None, "query": "", "status": None, "selected": None,
        })
        self.assertEqual(result["other"], {
            "run": "local/check-b", "query": "", "status": None, "selected": None,
        })

    def test_corrupt_or_other_route_handoff_is_discarded(self):
        for raw in (
            "not JSON", json.dumps({"route": "#/local/check-b", "view": {
                "run": "local/check-a", "query": "private", "status": None, "selected": "one",
            }}),
            json.dumps({"route": "#/local/check-a/finding/one", "view": {
                "run": "local/check-a", "query": 3, "status": None, "selected": "one",
            }}),
        ):
            with self.subTest(raw=raw):
                result = run_state({"bad": raw})
                self.assertEqual(result["view"], {
                    "run": None, "query": "", "status": None, "selected": None,
                })
                self.assertEqual(result["kept"], [])
