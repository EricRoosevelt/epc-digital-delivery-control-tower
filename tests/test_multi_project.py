"""Two projects: what that proves, and what it is not allowed to break.

Every test written before this one demonstrated that nothing changed. These
demonstrate that something *can* change — which is the only way to find out
whether the architecture's portability claim was real or merely stated.

The properties worth pinning are:

*Adding a project is data.* Discovery is a glob, the manifest is TOML, and the
models live beside it. Nothing in the pipeline needed to learn about this
project's existence.

*Business codes may repeat across projects.* The second project deliberately
calls two of its models ``architecture`` and ``structural`` — the same codes
the PCERT project uses. Had ``model_id`` and ``model_key`` been one field this
project could not have been added without renaming its models, and worse, the
collision would have merged two projects' elements silently, because
``element_key`` is built from ``model_key``.

*The published contract does not widen by accident.* It describes one project,
and with two present the legacy writers publish the one they are told to.
"""

from __future__ import annotations

import dataclasses
import unittest

from epc_control_tower.config import load_project_manifests, load_run_config
from epc_control_tower.domain import ELEMENT_KEY_SEPARATOR, derive_model_key
from epc_control_tower.exporters.legacy_pbip import LegacyPbipAdapter
from epc_control_tower.exporters.legacy_projection import (
    narrow_to_project,
    project_bundle,
)
from epc_control_tower.validation import BundleInvariantError, validate_bundle
from helpers import (
    LEGACY_PROJECT_ID,
    frozen_ruleset,
    PROJECT_ROOT,
    published_bundle,
    shipped_pipeline_result,
)

SECOND_PROJECT_ID = "iso-reference-view"


class AddingAProjectIsDataTests(unittest.TestCase):
    def test_both_projects_are_discovered_without_naming_either(self):
        # projects/*/project.toml. No registry of known projects anywhere.
        config = load_run_config(PROJECT_ROOT)
        manifests = load_project_manifests(
            config.project_manifests, repository_root=PROJECT_ROOT
        )
        self.assertEqual(
            [m.project.project_id for m in manifests],
            [SECOND_PROJECT_ID, LEGACY_PROJECT_ID],
        )

    def test_a_project_may_keep_its_models_beside_its_manifest(self):
        # The shipped example points at data/raw/ for historical reasons; the
        # intended layout is self-contained, and the second project uses it.
        config = load_run_config(PROJECT_ROOT)
        manifests = {
            m.project.project_id: m
            for m in load_project_manifests(
                config.project_manifests, repository_root=PROJECT_ROOT
            )
        }
        second = manifests[SECOND_PROJECT_ID]
        self.assertEqual(second.raw_data_dir.name, SECOND_PROJECT_ID)
        for model in second.models:
            with self.subTest(model=model.model_id):
                self.assertTrue((second.raw_data_dir / model.filename).is_file())

    def test_the_new_models_are_pinned_by_content_hash(self):
        config = load_run_config(PROJECT_ROOT)
        manifests = {
            m.project.project_id: m
            for m in load_project_manifests(
                config.project_manifests, repository_root=PROJECT_ROOT
            )
        }
        for model in manifests[SECOND_PROJECT_ID].models:
            with self.subTest(model=model.model_id):
                self.assertRegex(model.content_sha256, r"^[0-9a-f]{64}$")
                self.assertTrue(model.source_url.startswith("https://github.com/"))
                self.assertEqual(model.license, "CC BY 4.0")


class KeySplitTests(unittest.TestCase):
    """The reason ``model_key`` and ``model_id`` are separate fields."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle

    def test_two_projects_use_the_same_business_codes(self):
        by_project: dict[str, set[str]] = {}
        for model in self.bundle.models:
            by_project.setdefault(model.project_id, set()).add(model.model_id)
        shared = by_project[LEGACY_PROJECT_ID] & by_project[SECOND_PROJECT_ID]
        self.assertEqual(shared, {"architecture", "structural"})

    def test_their_global_keys_do_not_collide(self):
        keys = [model.model_key for model in self.bundle.models]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertIn("architecture", keys)
        self.assertIn(derive_model_key(SECOND_PROJECT_ID, "architecture"), keys)

    def test_elements_of_same_named_models_stay_apart(self):
        # element_key is built from model_key, so a collision there would have
        # merged two projects' registers rather than raising.
        prefixes = {
            element.element_key.split(ELEMENT_KEY_SEPARATOR)[0]
            for element in self.bundle.elements
        }
        self.assertIn("architecture", prefixes)
        self.assertIn(f"{SECOND_PROJECT_ID}.architecture", prefixes)
        self.assertEqual(
            len({e.element_key for e in self.bundle.elements}),
            len(self.bundle.elements),
        )

    def test_the_shipped_project_kept_its_original_keys(self):
        # Pinned in its manifest, which is why its published identities are
        # untouched by the rule that would otherwise namespace them.
        pcert = {
            m.model_key for m in self.bundle.models if m.project_id == LEGACY_PROJECT_ID
        }
        self.assertEqual(pcert, {"architecture", "structural", "hvac"})


class BundleInvariantTests(unittest.TestCase):
    """The uniqueness rules, provoked rather than described.

    Both checks were written in Phase 1 but had never had multi-project data to
    run against. An invariant nobody has seen fail is one nobody knows is
    checked.
    """

    def setUp(self):
        self.bundle = shipped_pipeline_result().bundle

    def test_the_shipped_two_project_run_satisfies_every_invariant(self):
        validate_bundle(self.bundle)

    def test_a_model_key_reused_across_projects_is_caught(self):
        # Added rather than substituted, so the violation under test is the
        # duplicate key itself and not the wreckage of removing a model every
        # element and finding still points at.
        pcert = next(
            m for m in self.bundle.models if m.project_id == LEGACY_PROJECT_ID
        )
        other = next(
            m for m in self.bundle.models if m.project_id == SECOND_PROJECT_ID
        )
        self.assertNotEqual(pcert.model_key, other.model_key)

        collision = dataclasses.replace(other, model_key=pcert.model_key)
        broken = dataclasses.replace(
            self.bundle, models=(*self.bundle.models, collision)
        )
        with self.assertRaises(BundleInvariantError) as raised:
            validate_bundle(broken)
        self.assertIn("duplicate model_key", str(raised.exception))
        self.assertIn(pcert.model_key, str(raised.exception))

    def test_a_model_id_reused_inside_one_project_is_caught(self):
        pcert = [m for m in self.bundle.models if m.project_id == LEGACY_PROJECT_ID]
        clash = dataclasses.replace(
            pcert[1], model_id=pcert[0].model_id, model_key="pcert-sample.clash"
        )
        broken = dataclasses.replace(self.bundle, models=(*self.bundle.models, clash))
        with self.assertRaises(BundleInvariantError) as raised:
            validate_bundle(broken)
        self.assertIn("duplicate model_id", str(raised.exception))

    def test_the_same_model_id_across_projects_is_not_an_error(self):
        # The asymmetry is the whole point: project-scoped for the business
        # code, global for the join key.
        validate_bundle(self.bundle)
        ids = [m.model_id for m in self.bundle.models]
        self.assertGreater(len(ids), len(set(ids)))


class CanonicalGrainTests(unittest.TestCase):
    """Which table carries the project, and which reaches it by join."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle

    def test_projects_are_a_dimension_of_their_own(self):
        self.assertEqual(
            sorted(p.project_id for p in self.bundle.projects),
            [SECOND_PROJECT_ID, LEGACY_PROJECT_ID],
        )

    def test_a_model_names_its_project_directly(self):
        known = {p.project_id for p in self.bundle.projects}
        for model in self.bundle.models:
            with self.subTest(model=model.model_key):
                self.assertIn(model.project_id, known)

    def test_an_element_reaches_its_project_through_its_model(self):
        # Not denormalised onto the element: an element belongs to a model, and
        # the model belongs to a project. Repeating project_id here would be a
        # second place for it to be wrong.
        from epc_control_tower.domain import Element, field_names

        self.assertNotIn("project_id", field_names(Element))
        owners = {m.model_key: m.project_id for m in self.bundle.models}
        for element in self.bundle.elements:
            with self.subTest(element=element.element_key):
                self.assertIn(element.model_key, owners)

    def test_findings_and_issues_carry_the_project_they_belong_to(self):
        # These are the grain a dashboard slices on, so the project is on the
        # row rather than two joins away.
        for finding in self.bundle.findings:
            self.assertTrue(finding.project_id)
        for issue in self.bundle.issues:
            self.assertTrue(issue.project_id)
        self.assertEqual(
            {f.project_id for f in self.bundle.findings},
            {LEGACY_PROJECT_ID, SECOND_PROJECT_ID},
        )

    def test_every_project_actually_produced_findings(self):
        # A second project that evaluated to nothing would prove nothing.
        counts: dict[str, int] = {}
        for finding in self.bundle.findings:
            counts[finding.project_id] = counts.get(finding.project_id, 0) + 1
        self.assertEqual(counts[LEGACY_PROJECT_ID], 47)
        self.assertEqual(counts[SECOND_PROJECT_ID], 27)

    def test_the_second_project_has_applicable_findings_not_only_na(self):
        applicable = [
            f
            for f in self.bundle.findings
            if f.project_id == SECOND_PROJECT_ID and f.is_applicable
        ]
        self.assertEqual(len(applicable), 2)
        self.assertEqual(
            sorted(self.bundle.ruleset.by_key(f.requirement_key).rule_id for f in applicable),
            ["R-001", "R-002"],
        )



class LegacyScopeTests(unittest.TestCase):
    """The published contract describes one project, and says which."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle

    def test_narrowing_reproduces_the_published_shape(self):
        narrowed = published_bundle()
        self.assertEqual(len(narrowed.projects), 1)
        self.assertEqual(len(narrowed.models), 3)
        self.assertEqual(len(narrowed.elements), 39)
        self.assertEqual(len(narrowed.findings), 47)
        self.assertEqual(len(narrowed.issues), 3)

    def test_a_project_narrowed_bundle_still_satisfies_every_invariant(self):
        # Narrowing by project leaves a bundle that is still a coherent run.
        # Narrowing by *rule set* deliberately does not: it replaces the rule
        # set with the frozen one, which no longer matches the identity the run
        # recorded, because that is exactly what publishing an older contract
        # means. Only the first is a run bundle.
        from epc_control_tower.exporters.legacy_projection import narrow_to_project

        validate_bundle(
            narrow_to_project(shipped_pipeline_result().bundle, LEGACY_PROJECT_ID)
        )

    def test_narrowing_keeps_the_run_identity_it_actually_had(self):
        # The validation genuinely covered six models. Rewriting the run to
        # match the projection would publish an identity that never happened.
        narrowed = published_bundle()
        self.assertEqual(
            narrowed.run.validation_run_id, self.bundle.run.validation_run_id
        )
        self.assertEqual(len(narrowed.run.model_inputs), 6)

    def test_publishing_without_saying_which_project_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            project_bundle(self.bundle)
        message = str(raised.exception)
        self.assertIn("describes one project", message)
        self.assertIn(SECOND_PROJECT_ID, message)
        self.assertIn("legacy_project_id", message)

    def test_publishing_a_project_the_run_does_not_have_is_refused(self):
        with self.assertRaisesRegex(KeyError, "which this run does not contain"):
            narrow_to_project(self.bundle, "no-such-project")

    def test_the_second_project_is_absent_from_every_published_file(self):
        tables = LegacyPbipAdapter(
            project_id=LEGACY_PROJECT_ID, frozen_ruleset=frozen_ruleset()
        ).build_tables(self.bundle)
        for filename, data in tables.items():
            with self.subTest(table=filename):
                self.assertNotIn(SECOND_PROJECT_ID, data.decode("utf-8-sig"))

    def test_emitting_every_project_would_have_changed_the_published_files(self):
        # Measured, not assumed. This is the outcome the scope decision exists
        # to prevent, and it would have been silent.
        published = LegacyPbipAdapter(
            project_id=LEGACY_PROJECT_ID, frozen_ruleset=frozen_ruleset()
        ).build_tables(self.bundle)
        widened = LegacyPbipAdapter(frozen_ruleset=frozen_ruleset()).build_tables(
            dataclasses.replace(
                self.bundle,
                projects=tuple(
                    p for p in self.bundle.projects if p.project_id == LEGACY_PROJECT_ID
                ),
            )
        )
        # The bundle above still holds both projects' models and findings, so
        # the "one project" guard passes while the data is wider.
        self.assertNotEqual(published["models.csv"], widened["models.csv"])
        self.assertNotEqual(published["ids_findings.csv"], widened["ids_findings.csv"])


if __name__ == "__main__":
    unittest.main()
