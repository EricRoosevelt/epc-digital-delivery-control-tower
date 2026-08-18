"""Project manifests and run configuration.

The manifest is what a fork edits first, so it has to fail loudly and
specifically on the mistakes people actually make: a missing key, the wrong
type, a duplicated model, and — the one that would otherwise be silent — two
projects laying claim to the same global model key.
"""

from __future__ import annotations

import shutil
import unittest
import uuid
from contextlib import contextmanager
from pathlib import Path

from epc_control_tower.config import (
    load_project_manifest,
    load_project_manifests,
    load_run_config,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MINIMAL = """
[project]
project_id = "demo"
name = "Demo"

[[models]]
model_id = "architecture"
discipline = "Architecture"
filename = "A.ifc"
"""


@contextmanager
def writable_test_directory(prefix: str):
    """Avoid Python 3.14 TemporaryDirectory's restrictive Windows ACL mode."""

    path = PROJECT_ROOT / "tests" / f".{prefix}-{uuid.uuid4().hex}"
    path.mkdir(mode=0o777)
    try:
        yield path
    finally:
        shutil.rmtree(path)


def write_manifest(directory: Path, name: str, text: str) -> Path:
    path = directory / f"{name}.toml"
    path.write_text(text, encoding="utf-8")
    return path


class ShippedManifestTests(unittest.TestCase):
    """The manifest that ships with the repository."""

    def setUp(self):
        self.manifest = load_project_manifest(
            PROJECT_ROOT / "projects" / "pcert-sample" / "project.toml",
            repository_root=PROJECT_ROOT,
        )

    def test_it_declares_the_three_source_models(self):
        self.assertEqual(
            [model.model_id for model in self.manifest.models],
            ["architecture", "hvac", "structural"],
        )

    def test_model_keys_are_pinned_to_the_published_values(self):
        # Pinned rather than derived, so every already-published element_key,
        # topic GUID and viewpoint GUID keeps its value.
        self.assertEqual(
            sorted(model.model_key for model in self.manifest.models),
            ["architecture", "hvac", "structural"],
        )

    def test_attribution_survives_the_move_into_the_manifest(self):
        for model in self.manifest.models:
            with self.subTest(model=model.model_id):
                self.assertEqual(model.license, "CC BY 4.0")
                self.assertIn("buildingSMART/Sample-Test-Files", model.source_url)

    def test_declared_hashes_match_the_recorded_ones(self):
        from epc_control_tower.determinism import read_csv_rows

        recorded = {
            row["model_id"]: row["content_sha256"]
            for row in read_csv_rows(PROJECT_ROOT / "data" / "processed" / "models.csv")
        }
        for model in self.manifest.models:
            with self.subTest(model=model.model_id):
                self.assertEqual(model.content_sha256, recorded[model.model_id])


class ModelKeyDefaultingTests(unittest.TestCase):
    def test_an_undeclared_model_key_is_namespaced_by_project(self):
        with writable_test_directory("cfg") as directory:
            path = write_manifest(directory, "project", MINIMAL)
            manifest = load_project_manifest(path, repository_root=PROJECT_ROOT)
        self.assertEqual(manifest.models[0].model_key, "demo.architecture")

    def test_two_projects_sharing_a_business_code_do_not_collide(self):
        second = MINIMAL.replace('project_id = "demo"', 'project_id = "other"')
        with writable_test_directory("cfg") as directory:
            first_path = write_manifest(directory, "a", MINIMAL)
            second_path = write_manifest(directory, "b", second)
            manifests = load_project_manifests(
                [first_path, second_path], repository_root=PROJECT_ROOT
            )
        keys = [manifest.models[0].model_key for manifest in manifests]
        self.assertEqual(keys, ["demo.architecture", "other.architecture"])


class CrossManifestUniquenessTests(unittest.TestCase):
    def test_two_projects_pinning_the_same_model_key_are_rejected(self):
        # Each manifest is internally consistent; only the whole set shows the
        # clash. Left unchecked this would silently merge two projects' elements
        # rather than raise, because element_key is built from model_key.
        pinned = MINIMAL + '\nmodel_key = "shared"\n'
        other = pinned.replace('project_id = "demo"', 'project_id = "other"')
        with writable_test_directory("cfg") as directory:
            first_path = write_manifest(directory, "a", pinned)
            second_path = write_manifest(directory, "b", other)
            with self.assertRaisesRegex(ValueError, "globally unique"):
                load_project_manifests(
                    [first_path, second_path], repository_root=PROJECT_ROOT
                )

    def test_two_manifests_declaring_the_same_project_id_are_rejected(self):
        with writable_test_directory("cfg") as directory:
            first_path = write_manifest(directory, "a", MINIMAL)
            second_path = write_manifest(directory, "b", MINIMAL)
            with self.assertRaisesRegex(ValueError, "already declared"):
                load_project_manifests(
                    [first_path, second_path], repository_root=PROJECT_ROOT
                )


class MalformedManifestTests(unittest.TestCase):
    def _expect(self, text: str, pattern: str):
        with writable_test_directory("cfg") as directory:
            path = write_manifest(directory, "project", text)
            with self.assertRaisesRegex(ValueError, pattern):
                load_project_manifest(path, repository_root=PROJECT_ROOT)

    def test_missing_project_table(self):
        self._expect('[[models]]\nmodel_id = "a"\n', "missing required key 'project'")

    def test_project_must_be_a_table(self):
        self._expect('project = "demo"\n', r"\[project\] must be a table")

    def test_missing_project_id(self):
        self._expect('[project]\nname = "n"\n', "missing required key 'project_id'")

    def test_at_least_one_model_is_required(self):
        self._expect(
            '[project]\nproject_id = "demo"\nname = "n"\n',
            r"at least one \[\[models\]\] entry",
        )

    def test_model_entries_must_be_tables(self):
        # `models` has to precede the [project] header to stay at document
        # level; written after it, TOML would nest it inside [project].
        self._expect(
            'models = ["a"]\n\n[project]\nproject_id = "demo"\nname = "n"\n',
            r"each \[\[models\]\] entry must be a table",
        )

    def test_missing_model_field(self):
        self._expect(
            '[project]\nproject_id = "demo"\nname = "n"\n\n'
            '[[models]]\nmodel_id = "a"\ndiscipline = "A"\n',
            "missing required key 'filename'",
        )

    def test_duplicate_model_id(self):
        text = MINIMAL + """
[[models]]
model_id = "architecture"
discipline = "Architecture"
filename = "B.ifc"
"""
        self._expect(text, "duplicate model_id")

    def test_duplicate_filename(self):
        text = MINIMAL + """
[[models]]
model_id = "structural"
discipline = "Structural"
filename = "A.ifc"
"""
        self._expect(text, "duplicate filename")

    def test_project_id_must_be_a_slug(self):
        self._expect(MINIMAL.replace('"demo"', '"not a slug"'), "must be a slug")

    def test_a_declared_hash_must_look_like_a_digest(self):
        # Checked while reading the manifest rather than when the hash is first
        # used, so a typo is reported against the line that contains it.
        self._expect(MINIMAL + 'content_sha256 = "nope"\n', "64 lowercase hex")

    def test_an_omitted_hash_is_allowed(self):
        with writable_test_directory("cfg") as directory:
            path = write_manifest(directory, "project", MINIMAL)
            manifest = load_project_manifest(path, repository_root=PROJECT_ROOT)
        self.assertEqual(manifest.models[0].content_sha256, "")


class RunConfigTests(unittest.TestCase):
    def test_defaults_discover_every_shipped_project(self):
        # Discovery is a glob over projects/*/project.toml, so adding the
        # second project needed no change here at all — which is the property
        # this test exists to hold on to.
        config = load_run_config(PROJECT_ROOT)
        self.assertEqual(
            [path.parent.name for path in config.project_manifests],
            ["iso-reference-view", "pcert-sample"],
        )
        self.assertEqual(
            {path.name for path in config.project_manifests}, {"project.toml"}
        )
        self.assertEqual(config.as_of, "2026-08-13T00:00:00Z")

    def test_the_legacy_writers_are_told_which_project_they_publish(self):
        config = load_run_config(PROJECT_ROOT)
        self.assertEqual(config.legacy_project_id, "pcert-sample")

    def test_paths_resolve_below_the_repository_root(self):
        config = load_run_config(PROJECT_ROOT)
        self.assertEqual(
            config.resolved_processed_data_dir(), PROJECT_ROOT / "data" / "processed"
        )
        self.assertTrue(config.resolved_ruleset_path().exists())

    def test_a_malformed_run_table_is_rejected(self):
        with writable_test_directory("cfg") as directory:
            path = directory / "control-tower.toml"
            path.write_text('run = "nope"\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"\[run\] must be a table"):
                load_run_config(PROJECT_ROOT, path)

    def test_exporters_must_be_an_array(self):
        with writable_test_directory("cfg") as directory:
            path = directory / "control-tower.toml"
            path.write_text('[run]\nexporters = "csv"\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exporters must be an array"):
                load_run_config(PROJECT_ROOT, path)

    def test_project_manifests_must_be_an_array(self):
        with writable_test_directory("cfg") as directory:
            path = directory / "control-tower.toml"
            path.write_text('[run]\nproject_manifests = "a.toml"\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "project_manifests must be an array"):
                load_run_config(PROJECT_ROOT, path)


if __name__ == "__main__":
    unittest.main()
