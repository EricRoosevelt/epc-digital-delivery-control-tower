"""The pure BCF exporter, and what the published archive turned out to need.

Phase 4's plan was to replace ``LegacyBcfExporter`` with a pure one. Half of
that happened and half of it turned out to be the wrong target, and the tests
below pin both halves so neither claim drifts.

The half that happened: the legacy exporter's *rule-awareness* is gone. It knew
the R-005 family and the HVAC model, and refused everything else — correctly, at
the time, because the priority, stage, labels and assignee it wrote were four
constants chosen for that one family. All four come from rule metadata now, and
the published archive is reproduced from that metadata byte for byte.

The half that did not: a pure exporter cannot produce the published archive, and
not for want of metadata. Everything metadata-shaped matches. What does not is
identity — the published ``ReferenceLink``s carry legacy finding keys derived
from the frozen run id, and the canonical keys for the same elements share none
of them. That is why this exporter ships alongside rather than instead.
"""

from __future__ import annotations

import io
import unittest
import zipfile
from xml.etree import ElementTree as ET

from epc_control_tower.bcf.schema import default_schema_dir
from epc_control_tower.exporters.bcf import BcfExporter
from epc_control_tower.exporters.legacy_bcf import LegacyBcfExporter
from epc_control_tower.exporters.legacy_projection import project_bundle
from helpers import (
    LEGACY_PROJECT_ID,
    PROJECT_ROOT,
    frozen_ruleset,
    shipped_pipeline_result,
    shipped_run_config,
)

PUBLISHED_BCF = "b3c6f51abc9647ef4baeee9f9bccd884094b362362e516778c4bf083326abc99"


def _exporter() -> BcfExporter:
    config = shipped_run_config()
    return BcfExporter(
        schema_dir=default_schema_dir(PROJECT_ROOT),
        project_name=config.bcf_project_name,
        creation_author=config.bcf_creation_author,
        topic_type=config.bcf_topic_type,
        role_domain=config.bcf_role_domain,
        project_id=config.legacy_project_id or None,
        frozen_ruleset=frozen_ruleset(),
    )


def _members(blob: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


class MetadataDrivenTests(unittest.TestCase):
    """The published archive, rebuilt from what the rules say."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle
        config = shipped_run_config()
        cls.legacy = LegacyBcfExporter(
            schema_dir=default_schema_dir(PROJECT_ROOT),
            project_id=config.legacy_project_id or None,
            frozen_ruleset=frozen_ruleset(),
        )

    def test_the_published_archive_is_reproduced_from_rule_metadata(self):
        from epc_control_tower.determinism import sha256_bytes

        self.assertEqual(sha256_bytes(self.legacy.build_archive(self.bundle)), PUBLISHED_BCF)

    def test_the_values_it_writes_are_the_ones_the_rules_declare(self):
        # Traced to source, not just to value: R-005A and R-005B state these,
        # and a test that only checked the archive could not tell a derivation
        # from a constant that happens to agree with one.
        declared = {
            requirement.rule_id: requirement
            for requirement in self.bundle.ruleset.requirements
            if requirement.rule_id in {"R-005A", "R-005B"}
        }
        for rule_id, requirement in sorted(declared.items()):
            with self.subTest(rule=rule_id):
                self.assertEqual(requirement.priority, "Medium")
                self.assertEqual(requirement.stage, "Coordination")
                self.assertEqual(requirement.owner_role, "model-coordination")
                self.assertEqual(requirement.labels, ("IDS", "ProjectAssumption"))

    def test_a_rule_declaring_nothing_yields_a_topic_without_those_elements(self):
        # Every one of them is minOccurs="0" and NonEmptyOrBlankString, so an
        # absent value is omitted rather than written empty. A rule set read
        # from a bare `.ids` document has none of them — IDS 1.0 has nowhere to
        # put them — and blank elements make an archive the schema rejects.
        import dataclasses

        projection = project_bundle(
            self.bundle, project_id=LEGACY_PROJECT_ID, frozen_ruleset=frozen_ruleset()
        )
        bare = dataclasses.replace(
            projection.topics[0], priority="", stage="", assignee_role="", labels=()
        )
        markup = self.legacy.markup(bare, self.bundle.run.as_of).decode("utf-8")
        for tag in ("Priority", "Labels", "AssignedTo", "Stage"):
            with self.subTest(element=tag):
                self.assertNotIn(f"<{tag}", markup)


class PurityTests(unittest.TestCase):
    """What the exporter is not allowed to know."""

    def test_it_names_no_rule_and_no_file(self):
        # Code, not prose. The module docstring says what the old exporter knew,
        # which is the opposite of knowing it; what matters is that nothing the
        # module *executes* mentions a rule id or a source filename.
        import ast
        import pathlib

        import epc_control_tower.exporters.bcf as module

        tree = ast.parse(pathlib.Path(module.__file__).read_text("utf-8"))
        literals = [
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        ]
        module_docstring = ast.get_docstring(tree, clean=False)
        self.assertTrue(module_docstring)
        code = "\n".join(text for text in literals if text != module_docstring)
        for forbidden in ("R-00", "Building-", "ids_failures"):
            with self.subTest(knowledge=forbidden):
                self.assertNotIn(forbidden, code)

    def test_scope_is_a_projection_not_a_rule_filter(self):
        # It publishes one project and one frozen rule set version. That is a
        # statement about which slice of the run is published, not about what
        # any rule means — and the distinction is the reason the scope survives
        # while the rule-awareness went.
        bundle = shipped_pipeline_result().bundle
        published = _exporter()._published_issues(bundle)
        self.assertTrue(published)
        for issue in published:
            with self.subTest(issue=issue.issue_key):
                self.assertEqual(issue.project_id, LEGACY_PROJECT_ID)


class ArchiveShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle
        cls.members = _members(_exporter().build_archive(cls.bundle))

    def test_it_produces_a_topic_for_every_published_issue(self):
        markups = [n for n in self.members if n.endswith("/markup.bcf")]
        self.assertEqual(len(markups), len(_exporter()._published_issues(self.bundle)))

    def test_the_topic_guid_does_not_move_when_the_run_does(self):
        # Derived from the subject, not from issue_key, which folds in the
        # validation run. The same element with the same problem should be the
        # same topic to whoever opens the archive.
        from helpers import declared_rules_plus_one

        before = {n.split("/")[0] for n in self.members if n.endswith("/markup.bcf")}
        after_blob = _exporter().build_archive(declared_rules_plus_one())
        after = {n.split("/")[0] for n in _members(after_blob) if n.endswith("/markup.bcf")}
        self.assertEqual(before, after)

    def test_a_due_date_reaches_the_markup(self):
        for name, data in sorted(self.members.items()):
            if not name.endswith("/markup.bcf"):
                continue
            with self.subTest(topic=name):
                root = ET.fromstring(data.decode("utf-8"))
                due = root.findtext("Topic/DueDate")
                self.assertTrue(due)


class ModelLevelTopicTests(unittest.TestCase):
    """A topic about something that is not there gets no viewpoint."""

    @classmethod
    def setUpClass(cls):
        bundle = shipped_pipeline_result().bundle
        # The published projection covers one project, so build the whole run
        # to reach the model-level issues.
        exporter = BcfExporter(schema_dir=default_schema_dir(PROJECT_ROOT))
        cls.bundle = bundle
        cls.members = _members(exporter.build_archive(bundle))

    def test_an_issue_with_no_element_gets_a_topic_but_no_viewpoint(self):
        element_less = [i for i in self.bundle.issues if not i.element_key]
        self.assertEqual(len(element_less), 3)
        for issue in element_less:
            guid = BcfExporter._topic_guid(issue)
            with self.subTest(issue=issue.issue_key):
                # The topic exists — a real failure is not dropped.
                self.assertIn(f"{guid}/markup.bcf", self.members)
                # And carries no view, because there is nowhere to point one.
                self.assertNotIn(f"{guid}/viewpoint.bcfv", self.members)
                markup = self.members[f"{guid}/markup.bcf"].decode("utf-8")
                self.assertNotIn("<Viewpoints>", markup)

    def test_an_issue_with_an_element_does_get_one(self):
        with_element = [i for i in self.bundle.issues if i.element_key]
        self.assertTrue(with_element)
        guid = BcfExporter._topic_guid(with_element[0])
        self.assertIn(f"{guid}/viewpoint.bcfv", self.members)


class OverdueTests(unittest.TestCase):
    """A deadline with no clock in it."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle

    def test_the_programme_states_dates_not_offsets(self):
        # The distinction is why `overdue` is answerable at all. An offset from
        # the opening event would put every due date in the future of the only
        # moment this system has.
        milestones = dict(self.bundle.ruleset.milestones)
        self.assertEqual(
            sorted(milestones), ["Coordination", "Design", "Handover"]
        )
        for stage, due in sorted(milestones.items()):
            with self.subTest(stage=stage):
                self.assertRegex(due, r"^\d{4}-\d{2}-\d{2}T")

    def test_issues_past_their_milestone_are_overdue(self):
        overdue = [issue for issue in self.bundle.issues if issue.is_overdue]
        self.assertEqual(len(overdue), 12)
        for issue in overdue:
            with self.subTest(issue=issue.issue_key):
                self.assertTrue(issue.due)
                self.assertGreater(self.bundle.run.as_of, issue.due)

    def test_an_issue_with_no_due_date_is_never_overdue(self):
        for issue in self.bundle.issues:
            with self.subTest(issue=issue.issue_key):
                if not issue.due:
                    self.assertFalse(issue.is_overdue)

    def test_overdue_is_checked_against_its_inputs_not_trusted(self):
        import dataclasses

        from epc_control_tower.validation import BundleInvariantError, validate_bundle

        lying = dataclasses.replace(
            self.bundle,
            issues=tuple(
                dataclasses.replace(issue, is_overdue=not issue.is_overdue)
                for issue in self.bundle.issues
            ),
        )
        with self.assertRaises(BundleInvariantError):
            validate_bundle(lying)


if __name__ == "__main__":
    unittest.main()
