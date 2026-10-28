"""Owned project UI messages keep parity without importing the application DOM."""

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import PROJECT_ROOT


class ProjectWordsTests(unittest.TestCase):
    def test_project_messages_have_matching_locales_and_no_english_fallback(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node is required to load the actual UI wording module")
        static = PROJECT_ROOT / "doctor" / "static"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("i18n.js", "projects-words.js"):
                shutil.copyfile(static / name, root / name)
            (root / "package.json").write_text('{"type":"module"}', encoding="utf-8")
            driver = (
                'await import("./projects-words.js");'
                'const {REGISTRY}=await import("./i18n.js");'
                'console.log(JSON.stringify(REGISTRY.get("PROJECTS")));'
            )
            completed = subprocess.run(
                [node, "--input-type=module", "-e", driver], cwd=root,
                capture_output=True, check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8", "replace"))
        words = json.loads(completed.stdout.decode("utf-8"))
        self.assertEqual(set(words["zh"]), set(words["en"]))
        self.assertGreater(len(words["en"]), 90)
        for key, value in words["en"].items():
            with self.subTest(key=key):
                self.assertTrue(value)
                self.assertNotRegex(value, r"[\u3400-\u9fff]")
                self.assertEqual(
                    set(re.findall(r"\{\w+\}", value)),
                    set(re.findall(r"\{\w+\}", words["zh"][key])),
                )
        self.assertIn("snapshot", words["en"]["saveDescription"])
        self.assertIn("not a repair", words["en"]["missingHint"])
        self.assertIn("new IFC", words["en"]["manualNote"])
        self.assertEqual(words["en"]["errorChecks"], "Rule check records")
        self.assertEqual(words["en"]["infoChecks"], "Information prompt records")
