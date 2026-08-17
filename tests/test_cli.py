"""The orchestrator's command line.

Replaces an arrangement in which the pipeline existed only as a list of
commands in a README, two of the scripts did their work at import time, and the
stages passed data to each other through CSV files committed to the repository.
The tests worth having here are about that: that the sequence is real, that
nothing is advertised which does not work, and that a run writes where the
published contract says it does.
"""

from __future__ import annotations

import contextlib
import io
import json
import unittest

from epc_control_tower.cli import build_parser, main
from helpers import shipped_reports_dir, writable_test_directory


def run_cli(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class AdvertisedCommandsTests(unittest.TestCase):
    def test_every_advertised_subcommand_has_a_handler(self):
        # Nothing is listed by --help before it does something. Registering an
        # entry point for work that does not exist yet is a claim, and this
        # project does not make claims it cannot keep.
        parser = build_parser()
        subparsers = next(
            action
            for action in parser._actions
            if isinstance(action, __import__("argparse")._SubParsersAction)
        )
        self.assertEqual(
            sorted(subparsers.choices),
            ["check", "components", "export", "projects", "run", "version"],
        )
        for name, subparser in subparsers.choices.items():
            with self.subTest(command=name):
                self.assertTrue(subparser.get_default("handler"))

    def test_version_reports_the_package_and_the_contract(self):
        code, out, _ = run_cli("version")
        self.assertEqual(code, 0)
        self.assertIn("epc-control-tower", out)
        self.assertIn("data contract 0.1", out)

    def test_components_lists_what_is_registered(self):
        code, out, _ = run_cli("components")
        self.assertEqual(code, 0)
        for expected in ("ids", "element", "csv", "json", "legacy-bcf", "legacy-pbip"):
            with self.subTest(component=expected):
                self.assertIn(expected, out)

    def test_projects_lists_the_shipped_manifest(self):
        code, out, _ = run_cli("projects")
        self.assertEqual(code, 0)
        self.assertIn("pcert-sample", out)
        for model in ("architecture", "structural", "hvac"):
            with self.subTest(model=model):
                self.assertIn(model, out)


class CheckCommandTests(unittest.TestCase):
    def test_check_validates_without_writing_artifacts(self):
        with writable_test_directory("cli-check") as scratch:
            code, out, _ = run_cli("check", "--reports-dir", str(scratch))
            written = sorted(path.name for path in scratch.rglob("*") if path.is_file())

        self.assertEqual(code, 0)
        self.assertIn("47 applicable", out.replace("31 of ", ""))
        self.assertIn("3 issue(s)", out)
        # Checker reports are written; published artifacts are not.
        self.assertTrue(written)
        for name in written:
            with self.subTest(file=name):
                self.assertNotIn(".csv", name)
                self.assertNotIn(".bcf", name)


class RunCommandTests(unittest.TestCase):
    def test_a_run_writes_each_exporter_where_that_kind_of_output_goes(self):
        with writable_test_directory("cli-run") as scratch:
            code, out, err = run_cli(
                "--config",
                str(_config_pointing_at(scratch)),
                "run",
            )
            processed = sorted(
                path.name for path in (scratch / "processed").glob("*.csv")
            )
            canonical = sorted(
                path.name for path in (scratch / "processed" / "canonical").glob("*")
            )
            reports = sorted(path.name for path in (scratch / "reports").glob("*"))

        self.assertEqual(code, 0, err)
        self.assertEqual(len(processed), 8)
        self.assertIn("run.json", canonical)
        self.assertIn("artifact_manifest.json", reports)
        self.assertIn("bcf", reports)
        self.assertIn("artifact bundle  bundle-", out)

    def test_export_without_a_format_says_so_rather_than_guessing(self):
        code, _, err = run_cli("export")
        self.assertEqual(code, 2)
        self.assertIn("needs at least one --format", err)

    def test_a_single_format_writes_only_that_format(self):
        with writable_test_directory("cli-export") as scratch:
            code, _, err = run_cli(
                "--config",
                str(_config_pointing_at(scratch)),
                "export",
                "--format",
                "json",
            )
            written = sorted(
                path.relative_to(scratch).as_posix()
                for path in scratch.rglob("*")
                if path.is_file() and path.suffix in {".csv", ".bcf", ".json"}
            )

        self.assertEqual(code, 0, err)
        self.assertIn("processed/canonical/run.json", written)
        self.assertNotIn("processed/ids_findings.csv", written)

    def test_an_unknown_exporter_is_reported_rather_than_ignored(self):
        code, _, err = run_cli("run", "--format", "nope")
        self.assertEqual(code, 1)
        self.assertIn("Unknown exporter", err)


def _config_pointing_at(scratch):
    """Write a control-tower.toml that sends every output into a scratch tree."""

    from helpers import PROJECT_ROOT

    relative = scratch.relative_to(PROJECT_ROOT).as_posix()
    path = scratch / "control-tower.toml"
    path.write_text(
        "[run]\n"
        f'processed_data_dir = "{relative}/processed"\n'
        f'reports_dir = "{relative}/reports"\n',
        encoding="utf-8",
    )
    return path


class RunManifestTests(unittest.TestCase):
    def test_the_artifact_manifest_describes_the_run_that_produced_it(self):
        with writable_test_directory("cli-manifest") as scratch:
            code, _, err = run_cli(
                "--config", str(_config_pointing_at(scratch)), "run"
            )
            manifest = json.loads(
                (scratch / "reports" / "artifact_manifest.json").read_text("utf-8")
            )

        self.assertEqual(code, 0, err)
        self.assertEqual(manifest["contract_version"], "0.1")
        self.assertEqual(
            sorted(entry["id"] for entry in manifest["exporters"]),
            ["csv", "json", "legacy-bcf", "legacy-pbip"],
        )
        self.assertEqual(len(manifest["artifacts"]), 18)
        for entry in manifest["artifacts"]:
            with self.subTest(artifact=entry["path"]):
                self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
