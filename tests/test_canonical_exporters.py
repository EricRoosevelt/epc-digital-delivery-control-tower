"""The canonical exporters, and the column drift they are designed to prevent.

The point worth testing hardest is not that the files come out right, but that
their columns are *computed* from the domain types. The previous layout stated
the finding columns twice, in two modules, in two different container types,
and the two drifted apart with nothing to notice. A test that merely asserted
the expected header would have been a third copy of the same list.
"""

from __future__ import annotations

import csv
import io
import json
import unittest

from epc_control_tower.determinism import CSV_BOM
from epc_control_tower.domain import (
    Element,
    Finding,
    Issue,
    IssueEvent,
    Model,
    Project,
    Provenance,
    Requirement,
    field_names,
)
from epc_control_tower.exporters.canonical import (
    CANONICAL_SUBDIRECTORY,
    CsvExporter,
    JsonExporter,
)
from epc_control_tower.stages.export import export
from helpers import PROJECT_ROOT, shipped_pipeline_result, writable_test_directory


def read_csv_bytes(data: bytes) -> tuple[list[str], list[dict[str, str]]]:
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    rows = list(reader)
    return list(reader.fieldnames or []), rows


class ExportedShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle
        cls.scratch_context = writable_test_directory("canonical-export")
        cls.scratch = cls.scratch_context.__enter__()
        cls.artifacts = CsvExporter().export(cls.bundle, cls.scratch)
        cls.tables = {
            artifact.path.name: read_csv_bytes(artifact.path.read_bytes())
            for artifact in cls.artifacts
        }

    @classmethod
    def tearDownClass(cls):
        cls.scratch_context.__exit__(None, None, None)

    def test_columns_are_the_domain_type_s_own_fields(self):
        for filename, row_type in (
            ("projects.csv", Project),
            ("elements.csv", Element),
            ("requirements.csv", Requirement),
            ("findings.csv", Finding),
        ):
            with self.subTest(table=filename):
                self.assertEqual(self.tables[filename][0], list(field_names(row_type)))

    def test_a_nested_record_is_spliced_in_where_it_sits(self):
        columns = self.tables["models.csv"][0]
        self.assertNotIn("provenance", columns)
        for column in field_names(Provenance):
            self.assertIn(column, columns)
        # Position, not just presence: the provenance fields replace the field
        # they came from rather than being appended.
        self.assertEqual(
            columns.index("source_url"), list(field_names(Model)).index("provenance")
        )

    def test_an_issue_s_findings_are_a_table_not_a_delimited_cell(self):
        self.assertNotIn("finding_keys", self.tables["issues.csv"][0])
        self.assertEqual(
            self.tables["issue_findings.csv"][0], ["issue_key", "finding_key"]
        )
        self.assertEqual(
            len(self.tables["issue_findings.csv"][1]),
            sum(len(issue.finding_keys) for issue in self.bundle.issues),
        )

    def test_event_columns_come_from_the_event_type(self):
        self.assertEqual(
            self.tables["issue_events.csv"][0], list(field_names(IssueEvent))
        )

    def test_every_domain_entity_reaches_a_table(self):
        self.assertEqual(
            sorted(self.tables),
            [
                "elements.csv",
                "findings.csv",
                "issue_events.csv",
                "issue_findings.csv",
                "issues.csv",
                "models.csv",
                "projects.csv",
                "requirements.csv",
            ],
        )
        self.assertEqual(len(self.tables["findings.csv"][1]), len(self.bundle.findings))
        self.assertEqual(len(self.tables["elements.csv"][1]), len(self.bundle.elements))
        self.assertEqual(len(self.tables["issues.csv"][1]), len(self.bundle.issues))

    def test_the_repository_csv_convention_is_used(self):
        for artifact in self.artifacts:
            data = artifact.path.read_bytes()
            with self.subTest(table=artifact.path.name):
                self.assertTrue(data.startswith(CSV_BOM))
                self.assertNotIn(b"\r\n", data)

    def test_booleans_use_the_published_lowercase_spelling(self):
        values = {row["is_applicable"] for row in self.tables["findings.csv"][1]}
        self.assertEqual(values, {"true", "false"})

    def test_enumerations_are_written_as_their_values(self):
        self.assertEqual(
            {row["status"] for row in self.tables["findings.csv"][1]},
            {"PASS", "FAIL", "N/A"},
        )

    def test_a_tuple_field_becomes_one_cell(self):
        kinds = {row["facet_kinds"] for row in self.tables["requirements.csv"][1]}
        self.assertEqual(kinds, {"attribute", "partof", "property"})

    def test_the_canonical_contract_is_kept_apart_from_the_published_one(self):
        for artifact in self.artifacts:
            with self.subTest(table=artifact.path.name):
                self.assertEqual(artifact.path.parent.name, CANONICAL_SUBDIRECTORY)


class JsonExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle

    def test_the_document_carries_the_inputs_its_identity_derives_from(self):
        with writable_test_directory("canonical-json") as scratch:
            artifact = JsonExporter().export(self.bundle, scratch)[0]
            document = json.loads(artifact.path.read_text("utf-8"))

        from epc_control_tower.identity import build_validation_run_id

        run = document["run"]
        recomputed = build_validation_run_id(
            ruleset_id=run["ruleset"]["id"],
            ruleset_version=run["ruleset"]["version"],
            ruleset_normalized_digest=run["ruleset"]["normalized_digest"],
            models=[
                (item["model_key"], item["content_sha256"])
                for item in run["model_inputs"]
            ],
            checkers=[
                __import__(
                    "epc_control_tower.domain", fromlist=["ComponentFingerprint"]
                ).ComponentFingerprint(
                    component_id=item["id"],
                    version=item["version"],
                    config_sha256=item["config_sha256"],
                )
                for item in run["checkers"]
            ],
            as_of=run["as_of"],
        )
        self.assertEqual(recomputed, run["validation_run_id"])

    def test_no_execution_record_reaches_a_deterministic_artifact(self):
        with writable_test_directory("canonical-json-exec") as scratch:
            artifact = JsonExporter().export(self.bundle, scratch)[0]
            text = artifact.path.read_text("utf-8")
        for forbidden in ("execution_id", "started_at", "nonce", "platform"):
            with self.subTest(field=forbidden):
                self.assertNotIn(forbidden, text)


class ExportStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = shipped_pipeline_result()

    def test_the_artifact_bundle_identifies_the_set_not_the_validation(self):
        with writable_test_directory("export-stage") as scratch:
            first = export(
                self.result.bundle,
                registry=self.result.registry,
                exporter_ids=["csv", "json"],
                output_root=scratch,
                repository_root=PROJECT_ROOT,
                manifest_dir=scratch,
            )
            fewer = export(
                self.result.bundle,
                registry=self.result.registry,
                exporter_ids=["csv"],
                output_root=scratch,
                repository_root=PROJECT_ROOT,
            )

        self.assertNotEqual(first.artifact_bundle_id, fewer.artifact_bundle_id)
        self.assertTrue(first.artifact_bundle_id.startswith("bundle-"))
        self.assertEqual(len(first.artifacts), 9)
        self.assertEqual(len(fewer.artifacts), 8)

    def test_running_the_same_export_twice_writes_the_same_bytes(self):
        # Into the same location both times: the manifest records where each
        # artifact went, so a different destination is a different manifest and
        # comparing across two scratch directories would prove nothing.
        digests = []
        with writable_test_directory("export-repeat") as scratch:
            for _ in range(2):
                result = export(
                    self.result.bundle,
                    registry=self.result.registry,
                    exporter_ids=["csv", "json"],
                    output_root=scratch,
                    repository_root=PROJECT_ROOT,
                    manifest_dir=scratch,
                )
                digests.append(
                    (
                        result.artifact_bundle_id,
                        {a.path.name: a.sha256 for a in result.artifacts},
                        result.manifest.sha256,
                    )
                )
        self.assertEqual(digests[0], digests[1])

    def test_the_manifest_records_repository_relative_paths_only(self):
        with writable_test_directory("export-manifest") as scratch:
            result = export(
                self.result.bundle,
                registry=self.result.registry,
                exporter_ids=["csv", "json"],
                output_root=scratch,
                repository_root=PROJECT_ROOT,
                manifest_dir=scratch,
            )
            document = json.loads(result.manifest.path.read_text("utf-8"))

        self.assertEqual(document["artifact_bundle_id"], result.artifact_bundle_id)
        for entry in document["artifacts"]:
            with self.subTest(path=entry["path"]):
                self.assertFalse(entry["path"].startswith("/"))
                self.assertNotIn(":", entry["path"])
                self.assertNotIn("\\", entry["path"])

    def test_enabling_no_exporters_is_rejected_rather_than_silently_writing_nothing(self):
        with self.assertRaisesRegex(ValueError, "No exporters enabled"):
            export(
                self.result.bundle,
                registry=self.result.registry,
                exporter_ids=[],
                output_root=PROJECT_ROOT,
                repository_root=PROJECT_ROOT,
            )

    def test_an_export_outside_the_repository_fails_closed(self):
        outside = PROJECT_ROOT.parent / f".outside-{id(self)}"
        outside.mkdir(mode=0o777, exist_ok=True)
        try:
            with self.assertRaisesRegex(ValueError, "must stay inside the repository"):
                export(
                    self.result.bundle,
                    registry=self.result.registry,
                    exporter_ids=["json"],
                    output_root=outside,
                    repository_root=PROJECT_ROOT,
                )
        finally:
            import shutil

            shutil.rmtree(outside, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
