"""The published CSV contract, asserted byte for byte.

This is the gate the whole phase turns on, and it is worth being explicit about
what it is for. The risk in a refactor this size was never that the dashboard
would break loudly — it is that the canonical model and the published contract
would quietly become two different descriptions of the same thing, and that
nobody would find out for months.

So the assertion is byte equality, not equivalence. "The same rows in the same
order with the same values" is what a human would check and it is not enough:
the encoding, the byte-order mark, the line terminator, the float formatting
and the column order are all part of what the Power BI project and the
committed evidence were built against.

While this file is green, the adapter is a pure projection of the canonical
model and the two cannot have forked. That is the adapter's only licence to
exist, and when it is finally deleted, this file goes with it.

Refreshing these expectations is deliberate: it means the published contract
genuinely moved, which requires a contract version bump and a CHANGELOG entry.
It is not something to do to make a red test go green.
"""

from __future__ import annotations

import unittest

from epc_control_tower.determinism import read_csv_rows, sha256_bytes
from epc_control_tower.domain import field_names
from epc_control_tower.exporters.legacy_pbip import LEGACY_TABLES, LegacyPbipAdapter
from epc_control_tower.exporters.legacy_projection import project_bundle
from epc_control_tower.legacy_identity import LEGACY_RUN_ID
from helpers import PROJECT_ROOT, shipped_pipeline_result, writable_test_directory

PROCESSED = PROJECT_ROOT / "data" / "processed"

#: Published digests, quoted from the release they were published in.
PUBLISHED_SHA256 = {
    "ids_findings.csv": (
        "ea7d2fa2cd1690eb8b791dcab2792f116238566f0c60b10b64f1b02ce504eb4d"
    ),
}


class ByteEqualityTests(unittest.TestCase):
    """The gate."""

    @classmethod
    def setUpClass(cls):
        cls.result = shipped_pipeline_result()
        cls.tables = LegacyPbipAdapter().build_tables(cls.result.bundle)

    def test_all_eight_published_files_are_reproduced_byte_for_byte(self):
        self.assertEqual(len(self.tables), 8)
        for filename, data in sorted(self.tables.items()):
            committed = (PROCESSED / filename).read_bytes()
            with self.subTest(table=filename):
                self.assertEqual(
                    data,
                    committed,
                    f"{filename} no longer reproduces the published bytes",
                )

    def test_the_published_digests_are_reproduced(self):
        for filename, digest in PUBLISHED_SHA256.items():
            with self.subTest(table=filename):
                self.assertEqual(sha256_bytes(self.tables[filename]), digest)

    def test_writing_the_tables_lands_them_where_the_dashboard_reads_them(self):
        with writable_test_directory("legacy-pbip-write") as scratch:
            artifacts = LegacyPbipAdapter().export(self.result.bundle, scratch)
            self.assertEqual(len(artifacts), 8)
            for artifact in artifacts:
                with self.subTest(table=artifact.path.name):
                    self.assertEqual(artifact.path.parent, scratch)
                    self.assertEqual(
                        artifact.path.read_bytes(),
                        (PROCESSED / artifact.path.name).read_bytes(),
                    )


class ProjectionPurityTests(unittest.TestCase):
    """Everything published is computed from the bundle, and nothing else."""

    @classmethod
    def setUpClass(cls):
        cls.result = shipped_pipeline_result()
        cls.projection = project_bundle(cls.result.bundle)

    def test_the_published_run_identity_comes_from_the_frozen_derivation(self):
        self.assertEqual(self.projection.run_id, LEGACY_RUN_ID)

    def test_the_published_keys_are_not_the_canonical_ones(self):
        # The derivation did not change — build_finding_key and
        # legacy_finding_key compute the same function. What changed is the run
        # identity they consume, because it now folds in each checker's version
        # and configuration. The published keys survive by feeding the old run
        # identity back in, not by keeping a second algorithm around.
        canonical = {finding.finding_key for finding in self.result.bundle.findings}
        published = {row.finding_key for row in self.projection.findings}
        self.assertEqual(len(canonical), len(published))
        self.assertEqual(canonical & published, set())

    def test_keys_that_do_not_depend_on_run_identity_are_unchanged(self):
        published = {
            (row["specification_id"], row["requirement_id"]): row["requirement_key"]
            for row in read_csv_rows(PROCESSED / "ids_findings.csv")
        }
        derived = {
            (row.specification_id, row.requirement_id): row.requirement_key
            for row in self.projection.findings
        }
        self.assertEqual(derived, published)

    def test_the_canonical_project_dimension_is_dropped_on_the_way_out(self):
        # This is what lets the next phase add a project dimension without the
        # dashboard noticing.
        self.assertTrue(all(f.project_id for f in self.result.bundle.findings))
        for _filename, _attribute, row_type in LEGACY_TABLES:
            with self.subTest(row=row_type.__name__):
                self.assertNotIn("project_id", field_names(row_type))

    def test_column_order_is_the_row_type_s_field_order(self):
        # Not a second list stated somewhere: the published order is a property
        # of the type. Restating it was how the finding columns came to exist
        # twice, in two shapes, and drift apart.
        for filename, _attribute, row_type in LEGACY_TABLES:
            header = (
                (PROCESSED / filename)
                .read_bytes()
                .decode("utf-8-sig")
                .splitlines()[0]
                .split(",")
            )
            with self.subTest(table=filename):
                self.assertEqual(header, list(field_names(row_type)))

    def test_every_published_table_is_covered(self):
        self.assertEqual(
            sorted(filename for filename, _, _ in LEGACY_TABLES),
            sorted(path.name for path in PROCESSED.glob("*.csv")),
        )


class LegacyManifestTests(unittest.TestCase):
    def test_the_published_manifest_is_reproduced(self):
        import json

        from epc_control_tower.bcf.schema import default_schema_dir
        from epc_control_tower.exporters.legacy_bcf import LegacyBcfExporter
        from epc_control_tower.exporters.legacy_manifest import (
            build_legacy_manifest,
            legacy_input_paths,
        )

        result = shipped_pipeline_result()
        projection = project_bundle(result.bundle)

        with writable_test_directory("legacy-manifest") as scratch:
            processed = scratch / "processed"
            reports = scratch / "reports"
            LegacyPbipAdapter().export(result.bundle, processed)
            LegacyBcfExporter(
                schema_dir=default_schema_dir(PROJECT_ROOT)
            ).export(result.bundle, reports)

            manifest = build_legacy_manifest(
                projection,
                repository_root=PROJECT_ROOT,
                input_paths=legacy_input_paths(
                    projection,
                    processed_dir=processed,
                    raw_data_dir=PROJECT_ROOT / "data" / "raw",
                    ruleset_path=PROJECT_ROOT
                    / "ids"
                    / "epc_delivery_requirements_v0.1.ids",
                ),
                sidecar_dir=processed,
                bcf_path=reports / "bcf" / "ids_failures.bcf",
                schema_dir=default_schema_dir(PROJECT_ROOT),
            )

        committed = json.loads(
            (PROJECT_ROOT / "reports" / "bcf" / "run_manifest.json").read_text("utf-8")
        )
        # Paths differ because the test wrote to a scratch directory; the
        # digests, counts and identities are what the manifest is for.
        for section in ("counts", "schema_bundle", "dependencies"):
            with self.subTest(section=section):
                self.assertEqual(manifest[section], committed[section])
        for field in ("run_id", "generated_at", "project_guid", "bcf_version"):
            with self.subTest(field=field):
                self.assertEqual(manifest[field], committed[field])
        self.assertEqual(
            [entry["sha256"] for entry in manifest["outputs"]],
            [entry["sha256"] for entry in committed["outputs"]],
        )
        self.assertEqual(
            [entry["sha256"] for entry in manifest["inputs"]],
            [entry["sha256"] for entry in committed["inputs"]],
        )


if __name__ == "__main__":
    unittest.main()
