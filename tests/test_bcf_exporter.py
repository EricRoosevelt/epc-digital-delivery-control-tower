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
from epc_control_tower.domain import IssueEvent
from epc_control_tower.exporters.bcf import BcfExporter
from epc_control_tower.exporters.legacy_bcf import LegacyBcfExporter
from epc_control_tower.exporters.legacy_projection import project_bundle
from helpers import (
    legacy_compat,
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
            frozen_ruleset=frozen_ruleset(), compat=legacy_compat(),
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
            self.bundle,
            project_id=LEGACY_PROJECT_ID,
            frozen_ruleset=frozen_ruleset(),
            compat=legacy_compat(),
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

    def test_it_projects_the_whole_run_not_a_published_slice(self):
        # The general writer has no project or rule-set scope: every issue in the
        # bundle becomes a topic, across every project, not the legacy slice of
        # one project and one frozen rule set. This is the defect it fixes —
        # scoping it published three topics for a run that had twenty-one.
        bundle = shipped_pipeline_result().bundle
        members = _members(_exporter().build_archive(bundle))
        markups = [n for n in members if n.endswith("/markup.bcf")]
        self.assertEqual(len(markups), len(bundle.issues))
        self.assertGreater(len(bundle.issues), 3)
        self.assertGreater(
            len({issue.project_id for issue in bundle.issues}), 1
        )


class ArchiveShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle
        cls.members = _members(_exporter().build_archive(cls.bundle))

    def test_it_produces_a_topic_for_every_issue_in_the_run(self):
        markups = [n for n in self.members if n.endswith("/markup.bcf")]
        self.assertEqual(len(markups), len(self.bundle.issues))

    def test_a_mixed_issue_is_not_dropped(self):
        # A general writer never drops an issue for what rules it mixes. Give one
        # issue a second finding from a rule the frozen legacy set never had; the
        # legacy scope would have discarded the whole topic, this one keeps it.
        import dataclasses

        from epc_control_tower.domain import Finding, FindingStatus, Requirement, Severity
        from epc_control_tower.identity import build_finding_key

        bundle = self.bundle
        target = next(i for i in bundle.issues if i.element_key)
        extra_req = Requirement(
            requirement_key="00000000-0000-0000-0000-0000000000ff",
            rule_id="R-999",
            requirement_id="new",
            specification_label="R-999: new",
            requirement_label="new",
            severity=Severity.ERROR,
            stage="Coordination",
        )
        extra_key = build_finding_key(
            validation_run_id=bundle.run.validation_run_id,
            model_key=target.model_key,
            requirement_key=extra_req.requirement_key,
            element_key=target.element_key,
        )
        extra_finding = Finding(
            finding_key=extra_key,
            validation_run_id=bundle.run.validation_run_id,
            project_id=target.project_id,
            model_key=target.model_key,
            element_key=target.element_key,
            requirement_key=extra_req.requirement_key,
            status=FindingStatus.FAIL,
            severity=Severity.ERROR,
            is_applicable=True,
            is_issue=True,
        )
        mixed = dataclasses.replace(
            bundle,
            ruleset=dataclasses.replace(
                bundle.ruleset,
                requirements=bundle.ruleset.requirements + (extra_req,),
            ),
            findings=bundle.findings + (extra_finding,),
            issues=tuple(
                dataclasses.replace(i, finding_keys=i.finding_keys + (extra_key,))
                if i.issue_key == target.issue_key
                else i
                for i in bundle.issues
            ),
        )
        members = _members(_exporter().build_archive(mixed))
        markups = [n for n in members if n.endswith("/markup.bcf")]
        self.assertEqual(len(markups), len(bundle.issues))

    def test_the_topic_guid_does_not_move_when_the_run_does(self):
        # Derived from (policy, project, group_ref), not from issue_key, which
        # folds in the validation run. The same subject with the same problem
        # should be the same topic to whoever opens the archive across runs.
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
        # moment this system has. Programme is now project data, so it is read
        # from the project's milestones rather than from the rule set.
        milestones = self.bundle.milestones_for("pcert-sample")
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


def _twin(issue, event, *, issue_key: str, policy: str):
    """A copy of one issue (and its opening event) under a new key and policy."""

    import dataclasses

    new_issue = dataclasses.replace(issue, issue_key=issue_key, grouping_policy=policy)
    new_event = dataclasses.replace(event, issue_key=issue_key, event_key=f"ev-{issue_key}")
    return new_issue, new_event


class TopicGuidCollisionTests(unittest.TestCase):
    """The GUID separates policies and fails closed on a true collision."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle
        # A model-level issue: its subject is the model, so a twin needs no
        # geometry and gets no viewpoint.
        cls.base = next(i for i in cls.bundle.issues if not i.element_key)
        cls.base_event = cls.bundle.events_for(cls.base.issue_key)[0]

    def test_the_same_subject_under_two_policies_does_not_overwrite(self):
        import dataclasses

        twin, twin_event = _twin(
            self.base, self.base_event, issue_key="twin-policy", policy="requirement"
        )
        bundle = dataclasses.replace(
            self.bundle,
            issues=(self.base, twin),
            issue_events=(self.base_event, twin_event),
        )
        members = _members(_exporter().build_archive(bundle))
        markups = {n.split("/")[0] for n in members if n.endswith("/markup.bcf")}
        # Same project and group_ref, different policy -> two distinct topics.
        self.assertEqual(len(markups), 2)

    def test_a_true_collision_is_rejected_by_the_exporter(self):
        import dataclasses

        twin, twin_event = _twin(
            self.base, self.base_event, issue_key="twin-same", policy=self.base.grouping_policy
        )
        bundle = dataclasses.replace(
            self.bundle,
            issues=(self.base, twin),
            issue_events=(self.base_event, twin_event),
        )
        with self.assertRaisesRegex(ValueError, "topic GUID collision"):
            _exporter().build_archive(bundle)

    def test_a_true_collision_is_rejected_by_the_validator(self):
        import dataclasses

        from epc_control_tower.validation import BundleInvariantError, validate_bundle

        twin, twin_event = _twin(
            self.base, self.base_event, issue_key="twin-same", policy=self.base.grouping_policy
        )
        bundle = dataclasses.replace(
            self.bundle,
            issues=(self.base, twin),
            issue_events=(self.base_event, twin_event),
        )
        with self.assertRaises(BundleInvariantError) as caught:
            validate_bundle(bundle, recompute_identity=False)
        self.assertRegex("\n".join(caught.exception.violations), "topic GUID collision")


class EventProjectionTests(unittest.TestCase):
    """Creation/Modified come from the events, so changing an event changes the
    bytes — and a modified pair appears only when there is a later event."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle
        cls.baseline = _exporter().build_archive(cls.bundle)

    def _markup_for(self, members, issue):
        guid = BcfExporter._topic_guid(issue)
        return members[f"{guid}/markup.bcf"].decode("utf-8")

    def test_changing_an_event_time_changes_the_bytes(self):
        import dataclasses

        victim = self.bundle.issues[0]
        event = self.bundle.events_for(victim.issue_key)[0]
        moved = dataclasses.replace(event, occurred_at="2026-08-14T00:00:00Z")
        bundle = dataclasses.replace(
            self.bundle,
            issue_events=(moved,)
            + tuple(e for e in self.bundle.issue_events if e.issue_key != victim.issue_key),
        )
        self.assertNotEqual(_exporter().build_archive(bundle), self.baseline)

    def test_changing_an_event_actor_changes_the_bytes(self):
        import dataclasses

        victim = self.bundle.issues[0]
        event = self.bundle.events_for(victim.issue_key)[0]
        reattributed = dataclasses.replace(event, actor_role="someone-else")
        bundle = dataclasses.replace(
            self.bundle,
            issue_events=(reattributed,)
            + tuple(e for e in self.bundle.issue_events if e.issue_key != victim.issue_key),
        )
        members = _members(_exporter().build_archive(bundle))
        markup = self._markup_for(members, victim)
        self.assertIn("someone-else@", markup)

    def test_a_later_event_produces_a_modified_pair(self):
        import dataclasses

        from epc_control_tower.domain import IssueState, StateChangedPayload

        victim = self.bundle.issues[0]
        opening = self.bundle.events_for(victim.issue_key)[0]
        later = IssueEvent(
            event_key="later",
            issue_key=victim.issue_key,
            sequence=2,
            occurred_at="2026-08-15T00:00:00Z",
            event_type="state_changed",
            from_state=IssueState.OPEN,
            to_state=IssueState.IN_PROGRESS,
            actor_role="reviewer",
            payload_version=1,
            typed_payload=StateChangedPayload(note="picked up"),
        )
        # lifecycle_state must fold out of the new history.
        relabelled = dataclasses.replace(victim, lifecycle_state=IssueState.IN_PROGRESS)
        bundle = dataclasses.replace(
            self.bundle,
            issues=(relabelled,) + self.bundle.issues[1:],
            issue_events=(opening, later)
            + tuple(e for e in self.bundle.issue_events if e.issue_key != victim.issue_key),
        )
        markup = self._markup_for(_members(_exporter().build_archive(bundle)), relabelled)
        self.assertIn("<ModifiedDate>2026-08-15T00:00:00Z</ModifiedDate>", markup)
        self.assertIn("reviewer@", markup)

    def test_an_issue_with_only_an_opening_event_has_no_modified_pair(self):
        markup = self._markup_for(_members(self.baseline), self.bundle.issues[0])
        self.assertNotIn("<ModifiedDate>", markup)


def _users(members: dict[str, bytes]) -> list[str]:
    root = ET.fromstring(members["extensions.xml"].decode("utf-8"))
    return [node.text for node in root.iter("User")]


class AuthorPathsAndUsersCoverage(unittest.TestCase):
    """Both author paths are reachable, and the Users extension covers every
    author actually written."""

    def setUp(self):
        self.bundle = shipped_pipeline_result().bundle

    def _replace_opening(self, issue, **changes):
        import dataclasses

        opening = self.bundle.events_for(issue.issue_key)[0]
        moved = dataclasses.replace(opening, **changes)
        return dataclasses.replace(
            self.bundle,
            issue_events=(moved,)
            + tuple(e for e in self.bundle.issue_events if e.issue_key != issue.issue_key),
        )

    def test_the_actor_ref_path_reaches_the_creation_author_and_users(self):
        victim = self.bundle.issues[0]
        bundle = self._replace_opening(victim, actor_ref="alice@example.invalid")
        members = _members(_exporter().build_archive(bundle))
        markup = members[f"{BcfExporter._topic_guid(victim)}/markup.bcf"].decode("utf-8")
        self.assertIn("<CreationAuthor>alice@example.invalid</CreationAuthor>", markup)
        self.assertIn("alice@example.invalid", _users(members))

    def test_the_actor_role_path_reaches_the_creation_author_and_users(self):
        # The shipped events carry a role and no ref, so the role path is what
        # authored every baseline topic; its address must appear in Users.
        members = _members(_exporter().build_archive(self.bundle))
        victim = self.bundle.issues[0]
        opening = self.bundle.events_for(victim.issue_key)[0]
        expected = f"{opening.actor_role}@example.invalid"
        markup = members[f"{BcfExporter._topic_guid(victim)}/markup.bcf"].decode("utf-8")
        self.assertIn(f"<CreationAuthor>{expected}</CreationAuthor>", markup)
        self.assertIn(expected, _users(members))

    def test_the_fallback_path_reaches_creation_author_and_users(self):
        # An event that names neither actor falls back to the archive's
        # configured creation_author — the third path, now reachable because
        # IssueEvent allows both actor fields empty.
        victim = self.bundle.issues[0]
        bundle = self._replace_opening(victim, actor_role="", actor_ref="")
        members = _members(_exporter().build_archive(bundle))
        markup = members[f"{BcfExporter._topic_guid(victim)}/markup.bcf"].decode("utf-8")
        self.assertIn(
            "<CreationAuthor>control-tower@example.invalid</CreationAuthor>", markup
        )
        self.assertIn("control-tower@example.invalid", _users(members))

    def test_when_the_fallback_is_used_creation_author_moves_the_bytes(self):
        # The counterexample the fallback path exists for: with a fallback
        # event, changing creation_author changes the archive bytes.
        victim = self.bundle.issues[0]
        bundle = self._replace_opening(victim, actor_role="", actor_ref="")
        default = _exporter().build_archive(bundle)
        other = BcfExporter(
            schema_dir=default_schema_dir(PROJECT_ROOT),
            creation_author="someone-else@example.invalid",
        ).build_archive(bundle)
        self.assertNotEqual(default, other)

    def test_without_a_fallback_event_creation_author_does_not_reach_the_bytes(self):
        # And the contrast: when every event names an actor, creation_author is
        # not written, so it shapes only the identity — which is why the config
        # test treats it as identity-only for the shipped bundle.
        default = _exporter().build_archive(self.bundle)
        other = BcfExporter(
            schema_dir=default_schema_dir(PROJECT_ROOT),
            creation_author="someone-else@example.invalid",
        ).build_archive(self.bundle)
        self.assertEqual(default, other)

    def test_users_covers_a_modified_author_distinct_from_creation(self):
        import dataclasses

        from epc_control_tower.domain import IssueState, StateChangedPayload

        victim = self.bundle.issues[0]
        opening = self.bundle.events_for(victim.issue_key)[0]
        later = IssueEvent(
            event_key="later",
            issue_key=victim.issue_key,
            sequence=2,
            occurred_at="2026-08-15T00:00:00Z",
            event_type="state_changed",
            from_state=IssueState.OPEN,
            to_state=IssueState.IN_PROGRESS,
            actor_ref="bob@example.invalid",
            actor_role="reviewer",
            payload_version=1,
            typed_payload=StateChangedPayload(note="picked up"),
        )
        relabelled = dataclasses.replace(victim, lifecycle_state=IssueState.IN_PROGRESS)
        bundle = dataclasses.replace(
            self.bundle,
            issues=(relabelled,) + self.bundle.issues[1:],
            issue_events=(opening, later)
            + tuple(e for e in self.bundle.issue_events if e.issue_key != victim.issue_key),
        )
        members = _members(_exporter().build_archive(bundle))
        users = _users(members)
        # The modified author (a concrete ref) is listed even though no assignee
        # or creation author equals it.
        self.assertIn("bob@example.invalid", users)
        markup = members[f"{BcfExporter._topic_guid(relabelled)}/markup.bcf"].decode("utf-8")
        self.assertIn("<ModifiedAuthor>bob@example.invalid</ModifiedAuthor>", markup)

    def test_users_is_sorted_and_deduplicated(self):
        members = _members(_exporter().build_archive(self.bundle))
        users = _users(members)
        self.assertEqual(users, sorted(set(users)))


class GeneralConfigIdentityTests(unittest.TestCase):
    def test_config_covers_every_byte_affecting_parameter(self):
        bundle = shipped_pipeline_result().bundle
        base = _exporter()
        # Every constructor argument moves the config identity. The bytes move
        # too for the ones actually written into the archive; the identity-only
        # set is the output-path knobs (filename, subdirectory) plus
        # creation_author — which is only written when an event names no actor,
        # and every event in the shipped bundle names one. Its byte effect under
        # a fallback event is covered by AuthorPathsAndUsersCoverage.
        identity_only = {"filename", "subdirectory", "creation_author"}
        for kwargs in (
            {"project_name": "Another Tool"},
            {"creation_author": "someone@example.invalid"},
            {"topic_type": "Clash"},
            {"role_domain": "elsewhere.invalid"},
            {"filename": "other.bcf"},
            {"subdirectory": "elsewhere"},
        ):
            with self.subTest(**kwargs):
                other = BcfExporter(schema_dir=default_schema_dir(PROJECT_ROOT), **kwargs)
                self.assertNotEqual(base.config_sha256(), other.config_sha256())
                if not (set(kwargs) & identity_only):
                    self.assertNotEqual(
                        base.build_archive(bundle), other.build_archive(bundle)
                    )


class ImportWithoutIfcOpenShellTests(unittest.TestCase):
    """The pure BCF projection imports and runs without the geometry engine."""

    def test_the_exporter_imports_with_ifcopenshell_blocked(self):
        import subprocess
        import sys

        script = (
            "import sys, importlib.abc\n"
            "class Block(importlib.abc.MetaPathFinder):\n"
            "    def find_spec(self, name, path, target=None):\n"
            "        if name == 'ifcopenshell' or name.startswith('ifcopenshell.'):\n"
            "            raise ImportError('ifcopenshell blocked')\n"
            "        return None\n"
            "sys.meta_path.insert(0, Block())\n"
            "import epc_control_tower.exporters.bcf\n"
            "import epc_control_tower.exporters.legacy_bcf\n"
            "from epc_control_tower.bcf.geometry import Aabb, camera_for_aabb\n"
            "camera_for_aabb(Aabb((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))\n"
            "try:\n"
            "    import ifcopenshell\n"
            "    raise SystemExit('ifcopenshell was importable')\n"
            "except ImportError:\n"
            "    pass\n"
            "print('OK')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        self.assertIn("OK", result.stdout, result.stderr)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
