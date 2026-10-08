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
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from helpers import PROJECT_ROOT, outside_repository_directory

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


#: What a copy of the checkout needs for ``src/extract_inventory.py`` to run in it
#: exactly as it runs here: the script, the package it shims, the configuration,
#: both projects with their models, and the two published registers it writes.
_EXTRACT_TREE = (
    "src/extract_inventory.py",
    "epc_control_tower",
    "control-tower.toml",
    "rules",
    "projects",
    "data/raw",
    "data/processed/models.csv",
    "data/processed/model_inventory.csv",
)
_REGISTERS = ("data/processed/models.csv", "data/processed/model_inventory.csv")


#: The configuration line that names the legacy project, whatever the line
#: ending: ``*.toml`` has no ``eol`` rule in .gitattributes, so a Windows
#: checkout has it with CRLF.
_LEGACY_PROJECT_LINE = re.compile(rb'^legacy_project_id = "pcert-sample"\r?\n', re.M)


def _copy_checkout(
    destination: Path, *, legacy_project_id: bool, newline: bytes | None = None
) -> Path:
    """Copy what the script needs; ``newline`` rewrites the configuration's line
    endings first, so a test can hold for both kinds of checkout."""

    for name in _EXTRACT_TREE:
        source = PROJECT_ROOT / name
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copyfile(source, target)
    config = destination / "control-tower.toml"
    if newline is not None:
        lines = config.read_bytes().replace(b"\r\n", b"\n")
        config.write_bytes(lines.replace(b"\n", newline))
    if not legacy_project_id:
        text, removed = _LEGACY_PROJECT_LINE.subn(b"", config.read_bytes())
        assert removed == 1, removed
        config.write_bytes(text)
    return destination


def _tree(root: Path) -> dict[str, tuple[int, int, bytes]]:
    """Every file under ``root``: size, modification time and content digest."""

    import hashlib

    return {
        path.relative_to(root).as_posix(): (
            path.stat().st_size,
            path.stat().st_mtime_ns,
            hashlib.sha256(path.read_bytes()).digest(),
        )
        for path in sorted(root.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def _run_extract(checkout: Path) -> subprocess.CompletedProcess:
    # The legacy entry point exactly as a user runs it, with no arguments, from
    # the copied checkout: the script puts its own checkout first on the path.
    return subprocess.run(
        [sys.executable, "src/extract_inventory.py"],
        cwd=checkout,
        capture_output=True,
        text=True,
        check=False,
    )


class ExtractInventoryScopeTests(unittest.TestCase):
    """``src/extract_inventory.py`` publishes the frozen project, or nothing.

    Measured on ``d59dee0`` before this was written (AGENTS.md rule 6): with a
    second project in the checkout, the script exited 0 and rewrote both
    published registers with every project's models — ``models.csv`` went from
    three rows to six, with a second ``architecture`` and a second
    ``structural``. ``epc-ct snapshot``, ``validate_dashboard.py --mode core``
    and the contract tests all still passed on the rewritten files; a later
    ``epc-ct run`` silently wrote the published bytes back. These two tests are
    that measurement, kept.
    """

    def test_with_the_legacy_project_named_it_writes_the_published_bytes(self):
        with outside_repository_directory("extract-scoped") as scratch:
            checkout = _copy_checkout(scratch / "checkout", legacy_project_id=True)
            # The copy is the real configuration: two projects, one named.
            self.assertEqual(
                sorted(path.name for path in (checkout / "projects").iterdir()),
                ["iso-reference-view", "pcert-sample"],
            )
            for name in _REGISTERS:
                (checkout / name).unlink()
            completed = _run_extract(checkout)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            for name in _REGISTERS:
                with self.subTest(register=name):
                    self.assertEqual(
                        (checkout / name).read_bytes(), (PROJECT_ROOT / name).read_bytes()
                    )

    def test_with_several_projects_and_none_named_it_refuses_and_writes_nothing(self):
        # Both line endings on every platform: a Windows checkout has the
        # configuration with CRLF, and the refusal must not depend on that.
        for name, newline in (("lf", b"\n"), ("crlf", b"\r\n")):
            with (
                self.subTest(config=name),
                outside_repository_directory(f"extract-unscoped-{name}") as scratch,
            ):
                checkout = _copy_checkout(
                    scratch / "checkout", legacy_project_id=False, newline=newline
                )
                config = (checkout / "control-tower.toml").read_bytes()
                self.assertEqual(config.count(b"\r\n") > 0, newline == b"\r\n")
                self.assertNotIn(b"legacy_project_id", config)
                before = _tree(checkout)
                completed = _run_extract(checkout)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("legacy_project_id", completed.stderr)
                self.assertIn("['iso-reference-view', 'pcert-sample']", completed.stderr)
                self.assertNotIn("Wrote", completed.stdout)
                self.assertEqual(_tree(checkout), before)


if __name__ == "__main__":
    unittest.main()
