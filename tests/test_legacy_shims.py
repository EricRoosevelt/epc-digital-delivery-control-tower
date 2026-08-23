"""The ``src/`` scripts, now shims over the package.

Two things are worth pinning here, and neither is about behaviour that changed.

*Both import routes still work.* The pre-existing tests reach these modules two
different ways — ``from src.X import ...`` in four files, and a
``sys.path`` insertion followed by a bare ``from bcf_common import ...`` in a
fifth — and both are load-bearing. Adding ``src/__init__.py`` would change how
the first resolves, so ``src`` is deliberately not a package.

*Nothing happens on import.* Two of these scripts used to do their work when
they were read: importing them opened IFC files and rewrote tracked artifacts.
A module that acts when it is read cannot be tested, cannot be introspected,
and will eventually do its work at a moment nobody chose.
"""

from __future__ import annotations

import ast
import importlib
import subprocess
import sys
import unittest

from helpers import PROJECT_ROOT

SRC = PROJECT_ROOT / "src"


class ImportRouteTests(unittest.TestCase):
    def test_src_is_not_a_package(self):
        # An __init__.py here would change how `from src.X import ...`
        # resolves, and four pre-existing test files depend on it.
        self.assertFalse((SRC / "__init__.py").exists())

    def test_the_dotted_route_works(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                "from src.identity import build_finding_key, canonical_json;"
                "from src.validate_ids import FINDING_COLUMNS, normalize_report;"
                "print(len(FINDING_COLUMNS))",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "20")

    def test_the_bare_route_with_src_on_the_path_works(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; sys.path.insert(0, 'src');"
                "from bcf_common import SCHEMA_DIR, Aabb, read_safe_zip;"
                "from generate_bcf import build_workflow_artifacts;"
                "from validate_bcf import validate_bcf_workflow;"
                "print('ok')",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "ok")


class ImportTimeSideEffectTests(unittest.TestCase):
    def test_no_script_does_its_work_at_import_time(self):
        # Every module-level statement must be a definition, an import, or a
        # constant. A call at module level is work happening on import.
        for path in sorted(SRC.glob("*.py")):
            tree = ast.parse(path.read_text("utf-8"))
            offenders = [
                node.lineno
                for node in tree.body
                if isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Call)
                and not (
                    isinstance(node.value.func, ast.Attribute)
                    and getattr(node.value.func.value, "id", "") == "sys"
                )
            ]
            with self.subTest(module=path.name):
                self.assertEqual(offenders, [], f"{path.name} calls at module level")

    def test_every_script_has_a_main_behind_a_guard(self):
        for name in (
            "extract_inventory",
            "generate_bcf",
            "generate_ids",
            "validate_ids",
        ):
            module = importlib.import_module(f"src.{name}")
            with self.subTest(module=name):
                self.assertTrue(callable(getattr(module, "main", None)))


class ShimFidelityTests(unittest.TestCase):
    def test_the_identity_shim_resolves_to_the_frozen_derivation(self):
        from epc_control_tower.legacy_identity import legacy_finding_key
        from src.identity import build_finding_key

        self.assertEqual(
            build_finding_key("run", "hvac", "requirement", "hvac::E1"),
            legacy_finding_key(
                run_id="run",
                model_id="hvac",
                requirement_key="requirement",
                element_key="hvac::E1",
            ),
        )

    def test_the_finding_columns_come_from_the_row_type(self):
        from epc_control_tower.domain import field_names
        from epc_control_tower.exporters.legacy_contract import LegacyFindingRow
        from src.validate_ids import FINDING_COLUMNS

        self.assertEqual(FINDING_COLUMNS, list(field_names(LegacyFindingRow)))

    def test_the_rule_authoring_script_refuses_to_re_key_the_published_run(self):
        # The published run_id is a SHA-256 over this document's raw bytes, so
        # rewriting it re-keys all forty-seven findings.
        from src.generate_ids import OUTPUT_PATH, write_document

        with self.assertRaisesRegex(FileExistsError, "re-keys every published finding"):
            write_document(OUTPUT_PATH)

    def test_the_declared_rules_still_match_the_shipped_document(self):
        import xml.etree.ElementTree as ET

        from src.generate_ids import (
            IDS_NAMESPACE,
            OUTPUT_PATH,
            build_document,
            declared_identifiers,
        )

        shipped = [
            node.get("identifier")
            for node in ET.parse(OUTPUT_PATH)
            .getroot()
            .findall(".//ids:specification", IDS_NAMESPACE)
        ]
        self.assertEqual(declared_identifiers(build_document()), shipped)


if __name__ == "__main__":
    unittest.main()
