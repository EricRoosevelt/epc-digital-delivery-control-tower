"""The frozen legacy compatibility document, and the projection built from it.

The published archive's metadata comes from a pinned document keyed by
requirement — not from ``bundle.issues`` or the current grouping policy. These
tests pin that: the document's schema/version/hash are checked, its requirement
set must equal the frozen rule set exactly, and the projection's topics are
independent of whatever the current run grouped.
"""

from __future__ import annotations

import dataclasses
import json
import unittest

from epc_control_tower.exporters.legacy_compat import (
    load_legacy_compatibility,
    legacy_config_sha256,
)
from epc_control_tower.exporters.legacy_projection import project_bundle
from helpers import (
    LEGACY_PROJECT_ID,
    PROJECT_ROOT,
    frozen_ruleset,
    legacy_compat,
    shipped_pipeline_result,
    shipped_run_config,
    writable_test_directory,
)

COMPAT_PATH = PROJECT_ROOT / "docs" / "contracts" / "legacy" / "legacy_bcf_compat.v0.1.json"


def _write_compat(directory, document) -> object:
    path = directory / "compat.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _valid_document() -> dict:
    return json.loads(COMPAT_PATH.read_text("utf-8"))


class PinnedDocumentTests(unittest.TestCase):
    def test_the_shipped_config_pins_the_document_by_hash(self):
        config = shipped_run_config()
        self.assertTrue(config.legacy_compat_path.exists())
        # Loading with the pinned hash must succeed; a wrong hash must not.
        load_legacy_compatibility(
            config.legacy_compat_path, expected_sha256=config.legacy_compat_sha256
        )
        with self.assertRaisesRegex(ValueError, "sha256"):
            load_legacy_compatibility(
                config.legacy_compat_path, expected_sha256="0" * 64
            )

    def test_an_unknown_schema_version_is_rejected(self):
        with writable_test_directory("compat") as scratch:
            document = _valid_document()
            document["schema_version"] = "2"
            path = _write_compat(scratch, document)
            with self.assertRaisesRegex(ValueError, "schema_version"):
                load_legacy_compatibility(path)


class RequirementSetValidationTests(unittest.TestCase):
    """Exact set equality against the frozen rule set."""

    def setUp(self):
        self.frozen = frozen_ruleset()

    def test_the_shipped_document_matches_the_frozen_rule_set(self):
        legacy_compat().validate_against_ruleset(self.frozen)

    def test_a_missing_requirement_is_rejected(self):
        with writable_test_directory("compat") as scratch:
            document = _valid_document()
            dropped = sorted(document["requirements"])[0]
            del document["requirements"][dropped]
            compat = load_legacy_compatibility(_write_compat(scratch, document))
        with self.assertRaisesRegex(ValueError, "missing"):
            compat.validate_against_ruleset(self.frozen)

    def test_an_extra_requirement_is_rejected(self):
        with writable_test_directory("compat") as scratch:
            document = _valid_document()
            sample = next(iter(document["requirements"].values()))
            document["requirements"]["ffffffff-0000-0000-0000-000000000000"] = sample
            compat = load_legacy_compatibility(_write_compat(scratch, document))
        with self.assertRaisesRegex(ValueError, "extra"):
            compat.validate_against_ruleset(self.frozen)

    def test_a_duplicate_requirement_key_is_rejected_at_load(self):
        with writable_test_directory("compat") as scratch:
            document = _valid_document()
            key = sorted(document["requirements"])[0]
            # Emit the raw JSON with the key repeated — json.dumps of a dict
            # cannot, so build the text by hand.
            body = json.dumps(document)
            dup = json.dumps({key: document["requirements"][key]})[1:-1]
            body = body.replace('"requirements": {', '"requirements": {' + dup + ", ", 1)
            path = scratch / "compat.json"
            path.write_text(body, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate key"):
                load_legacy_compatibility(path)

    def test_a_mismatched_ruleset_version_is_rejected(self):
        with writable_test_directory("compat") as scratch:
            document = _valid_document()
            document["ruleset"]["version"] = "9.9"
            compat = load_legacy_compatibility(_write_compat(scratch, document))
        with self.assertRaisesRegex(ValueError, "rule set"):
            compat.validate_against_ruleset(self.frozen)


class ProjectionIndependenceTests(unittest.TestCase):
    """The legacy topics do not read the current issues or grouping policy."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle

    def _topics(self, bundle):
        return project_bundle(
            bundle,
            project_id=LEGACY_PROJECT_ID,
            frozen_ruleset=frozen_ruleset(),
            compat=legacy_compat(),
        ).topics

    def test_topics_are_unchanged_when_the_current_issue_metadata_is_scrambled(self):
        # Rewrite every current issue's priority/stage/labels/assignee to junk.
        # The legacy projection reads none of it, so its topics are identical.
        scrambled = dataclasses.replace(
            self.bundle,
            issues=tuple(
                dataclasses.replace(
                    issue,
                    priority="SCRAMBLED",
                    stage="SCRAMBLED",
                    assignee_role="nobody",
                    labels=("SCRAMBLED",),
                )
                for issue in self.bundle.issues
            ),
        )
        base = self._topics(self.bundle)
        after = self._topics(scrambled)
        self.assertEqual(len(base), 3)
        self.assertEqual(
            [(t.element_key, t.priority, t.stage, t.assignee_role, t.labels) for t in base],
            [(t.element_key, t.priority, t.stage, t.assignee_role, t.labels) for t in after],
        )

    def test_the_topic_metadata_is_the_frozen_metadata(self):
        topics = self._topics(self.bundle)
        for topic in topics:
            with self.subTest(topic=topic.element_key):
                self.assertEqual(topic.priority, "Medium")
                self.assertEqual(topic.stage, "Coordination")
                self.assertEqual(topic.assignee_role, "model-coordination")
                self.assertEqual(topic.labels, ("HVAC", "IDS", "ProjectAssumption"))

    def test_projecting_without_compat_under_a_frozen_scope_is_refused(self):
        with self.assertRaisesRegex(ValueError, "compatibility metadata"):
            project_bundle(
                self.bundle,
                project_id=LEGACY_PROJECT_ID,
                frozen_ruleset=frozen_ruleset(),
            )


class ConfigIdentityTests(unittest.TestCase):
    def _config(self, compat):
        return legacy_config_sha256(
            subdirectory="bcf",
            project_id=LEGACY_PROJECT_ID,
            frozen_ruleset=frozen_ruleset(),
            compat=compat,
        )

    def test_the_config_folds_the_verified_raw_sha256(self):
        # The pinned file hash is exactly what the shipped config verifies, and
        # what the exporter identity folds in.
        config = shipped_run_config()
        self.assertEqual(legacy_compat().source_sha256, config.legacy_compat_sha256)

    def test_a_different_raw_sha_moves_the_config_identity(self):
        moved = dataclasses.replace(legacy_compat(), source_sha256="0" * 64)
        self.assertNotEqual(self._config(legacy_compat()), self._config(moved))

    def test_reformatting_the_file_moves_the_identity_even_at_equal_content(self):
        # The point of using the raw SHA rather than a rebuilt semantic digest:
        # two files with identical parsed content but different bytes have
        # different identities. A semantic digest would call them the same.
        with writable_test_directory("compat") as scratch:
            document = _valid_document()
            pretty = scratch / "pretty.json"
            pretty.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
            compact = scratch / "compact.json"
            compact.write_text(json.dumps(document, separators=(",", ":")), encoding="utf-8")
            a = load_legacy_compatibility(pretty)
            b = load_legacy_compatibility(compact)
        # Same parsed requirements...
        self.assertEqual(a.requirements.keys(), b.requirements.keys())
        # ...different bytes, therefore different config identity.
        self.assertNotEqual(a.source_sha256, b.source_sha256)
        self.assertNotEqual(self._config(a), self._config(b))


if __name__ == "__main__":
    unittest.main()
