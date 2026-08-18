"""Characterization tests for the ported ingest and inventory stages.

These pin the refactor to the data the previous implementation published. They
are not invariant tests — nothing here is a law of the domain — they are a
statement that rebuilding the register from the same IFC files still produces
the same register, field for field and row for row.

They will need refreshing whenever the shipped fixture legitimately changes,
which is exactly the point: that refresh is a deliberate act.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from epc_control_tower.config import load_project_manifests, load_run_config
from epc_control_tower.determinism import read_csv_rows
from epc_control_tower.stages.ingest import ingest
from epc_control_tower.stages.inventory import inventory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"
PUBLISHED_PROJECT_ID = "pcert-sample"


class StageFidelityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = load_run_config(PROJECT_ROOT)
        cls.manifests = load_project_manifests(
            config.project_manifests, repository_root=PROJECT_ROOT
        )
        # The published register describes one project. A second one now
        # exists, so the assertions below say which they are about instead of
        # relying on there being only one — which is what they always meant.
        cls.manifests = tuple(
            manifest
            for manifest in cls.manifests
            if manifest.project.project_id == PUBLISHED_PROJECT_ID
        )
        cls.result = ingest(cls.manifests)
        paths = {
            declared.model_key: manifest.raw_data_dir / declared.filename
            for manifest in cls.manifests
            for declared in manifest.models
        }
        cls.elements = inventory(cls.result.models, paths)
        cls.committed_models = read_csv_rows(PROCESSED / "models.csv")
        cls.committed_elements = read_csv_rows(PROCESSED / "model_inventory.csv")

    def test_every_model_field_matches_the_published_register(self):
        self.assertEqual(len(self.result.models), len(self.committed_models))
        published = {row["model_id"]: row for row in self.committed_models}
        for model in self.result.models:
            row = published[model.model_id]
            with self.subTest(model=model.model_id):
                self.assertEqual(model.discipline, row["discipline"])
                self.assertEqual(model.filename, row["filename"])
                self.assertEqual(model.ifc_schema, row["ifc_schema"])
                self.assertEqual(model.ifc_project_guid, row["ifc_project_guid"])
                self.assertEqual(model.provenance.content_sha256, row["content_sha256"])
                self.assertEqual(model.provenance.source_url, row["source_url"])
                self.assertEqual(model.provenance.license, row["license"])

    def test_every_element_field_matches_the_published_inventory(self):
        self.assertEqual(len(self.elements), len(self.committed_elements))
        published = {row["element_key"]: row for row in self.committed_elements}
        for element in self.elements:
            row = published[element.element_key]
            with self.subTest(element=element.element_key):
                self.assertEqual(element.global_id, row["global_id"])
                self.assertEqual(element.ifc_class, row["ifc_class"])
                self.assertEqual(element.name, row["name"])
                self.assertEqual(element.storey, row["storey"])
                self.assertEqual(str(element.pset_count), row["pset_count"])

    def test_row_order_is_reproduced(self):
        # Order is part of the contract: the published CSVs are byte-compared.
        self.assertEqual(
            [element.element_key for element in self.elements],
            [row["element_key"] for row in self.committed_elements],
        )

    def test_a_bare_global_id_would_not_have_been_a_safe_join_key(self):
        # 39 occurrences, 32 distinct GlobalIds: four GUID groups recur across
        # discipline files. This is why element_key carries its model.
        self.assertEqual(len(self.elements), 39)
        self.assertEqual(len({element.global_id for element in self.elements}), 32)
        self.assertEqual(len({element.element_key for element in self.elements}), 39)

    def test_run_identity_covers_every_ingested_model(self):
        self.assertEqual(
            [key for key, _ in self.result.model_inputs()],
            sorted(model.model_key for model in self.result.models),
        )

    def test_declared_hashes_are_verified_not_merely_recorded(self):
        for model in self.result.models:
            declared = next(
                candidate
                for manifest in self.manifests
                for candidate in manifest.models
                if candidate.model_key == model.model_key
            )
            with self.subTest(model=model.model_key):
                self.assertTrue(declared.content_sha256)
                self.assertEqual(model.provenance.content_sha256, declared.content_sha256)


class IngestFailureTests(unittest.TestCase):
    def test_a_declared_model_that_is_absent_stops_the_run(self):
        from epc_control_tower.config import ManifestModel, ProjectManifest
        from epc_control_tower.domain import Project

        manifest = ProjectManifest(
            project=Project(project_id="demo", name="Demo"),
            models=(
                ManifestModel(
                    model_id="a",
                    discipline="A",
                    filename="does-not-exist.ifc",
                    model_key="demo.a",
                ),
            ),
            raw_data_dir=PROJECT_ROOT / "data" / "raw",
        )
        with self.assertRaisesRegex(FileNotFoundError, "declared model not found"):
            ingest([manifest])

    def test_a_content_hash_mismatch_stops_the_run(self):
        from epc_control_tower.config import ManifestModel, ProjectManifest
        from epc_control_tower.domain import Project

        manifest = ProjectManifest(
            project=Project(project_id="demo", name="Demo"),
            models=(
                ManifestModel(
                    model_id="architecture",
                    discipline="Architecture",
                    filename="Building-Architecture.ifc",
                    model_key="demo.architecture",
                    content_sha256="0" * 64,
                ),
            ),
            raw_data_dir=PROJECT_ROOT / "data" / "raw",
        )
        with self.assertRaisesRegex(ValueError, "content hash mismatch"):
            ingest([manifest])


if __name__ == "__main__":
    unittest.main()
