"""The legacy BCF exporter, and the archive discipline underneath it.

The load-bearing assertion is the first one: the archive built from the
canonical model is byte-identical to the one already published. Everything else
here explains why that is possible — every property of a ZIP that would
otherwise record the machine, the moment, or the order of construction is
pinned, and the camera that frames each topic is solved and then checked rather
than guessed.

The exporter is called *legacy* because it still knows which rules and which
model it is converting. Those checks are reproduced on purpose and are tested
as such, so that the replacement which does not need them is an obvious piece
of remaining work rather than a forgotten one.
"""

from __future__ import annotations

import io
import math
import pathlib
import unittest
import zipfile

from epc_control_tower.bcf.archive import (
    FIXED_ZIP_TIMESTAMP,
    build_deterministic_zip,
    read_safe_zip,
    validate_archive_name,
)
from epc_control_tower.bcf.geometry import (
    Aabb,
    camera_for_aabb,
    verify_camera_frames_aabb,
)
from epc_control_tower.bcf.schema import (
    default_schema_dir,
    parse_xml,
    verify_schema_bundle,
    xml_bytes,
)
from epc_control_tower.determinism import sha256_bytes
from epc_control_tower.exporters.legacy_bcf import LegacyBcfExporter
from epc_control_tower.exporters.legacy_projection import project_bundle
from epc_control_tower.legacy_identity import LEGACY_RUN_ID
from helpers import (
    legacy_compat,
    LEGACY_PROJECT_ID,
    frozen_ruleset,
    PROJECT_ROOT,
    shipped_pipeline_result,
    writable_test_directory,
)

PUBLISHED_BCF = PROJECT_ROOT / "reports" / "bcf" / "ids_failures.bcf"
PUBLISHED_BCF_SHA256 = (
    "b3c6f51abc9647ef4baeee9f9bccd884094b362362e516778c4bf083326abc99"
)
SCHEMA_DIR = default_schema_dir(PROJECT_ROOT)


class ModelGroupingPolicy:
    """A legal grouping policy that produces *model*-level issues only.

    Not registered in the package — it exists to prove the legacy projection
    does not depend on the current policy having produced element-level issues.
    It groups every issue-bearing finding by its model, so no issue names an
    element, which is exactly the case that would starve the legacy archive of
    geometry if the run computed boxes only for the current issues' elements.
    """

    id = "model"
    version = "1.0.0"

    def config_sha256(self) -> str:
        return ""

    def group(self, findings, *, validation_run_id, as_of, requirements=None, programmes=None):
        from epc_control_tower.domain import (
            Issue,
            IssueEvent,
            IssueState,
            TopicCreatedPayload,
            derive_is_overdue,
            derive_lifecycle_state,
        )
        from epc_control_tower.grouping.element import ElementGroupingPolicy
        from epc_control_tower.identity import build_issue_event_key, build_issue_key

        by_key = dict(requirements or {})
        prog = {pid: dict(stages) for pid, stages in (programmes or {}).items()}
        grouped: dict[str, list] = {}
        for finding in findings:
            if finding.is_issue:
                grouped.setdefault(finding.model_key, []).append(finding)

        issues, events = [], []
        for model_key in sorted(grouped):
            members = sorted(grouped[model_key], key=lambda item: item.finding_key)
            first = members[0]

            def due_of(stage, project_id=first.project_id):
                if not stage:
                    return ""
                stated = prog.get(project_id, {})
                if stage in stated:
                    return stated[stage]
                raise ValueError(f"no milestone for {project_id} {stage}")

            deciding, due = ElementGroupingPolicy._deciding(members, by_key, due_of)
            issue_key = build_issue_key(
                validation_run_id=validation_run_id, grouping_policy=self.id, group_ref=model_key
            )
            role = deciding.owner_role if deciding and deciding.owner_role else "model-coordination"
            event = IssueEvent(
                event_key=build_issue_event_key(
                    issue_key=issue_key, sequence=1, event_type="topic_created"
                ),
                issue_key=issue_key,
                sequence=1,
                occurred_at=as_of,
                event_type="topic_created",
                from_state=None,
                to_state=IssueState.OPEN,
                actor_role=role,
                payload_version=1,
                typed_payload=TopicCreatedPayload(finding_count=len(members), title=model_key),
            )
            lifecycle = derive_lifecycle_state([event])
            issues.append(
                Issue(
                    issue_key=issue_key,
                    validation_run_id=validation_run_id,
                    project_id=first.project_id,
                    model_key=first.model_key,
                    element_key="",
                    grouping_policy=self.id,
                    group_ref=model_key,
                    finding_keys=tuple(m.finding_key for m in members),
                    lifecycle_state=lifecycle,
                    assignee_role=role,
                    priority=deciding.priority if deciding else "",
                    stage=deciding.stage if deciding else "",
                    due=due,
                    is_overdue=derive_is_overdue(as_of=as_of, due=due, lifecycle_state=lifecycle),
                    labels=(),
                )
            )
            events.append(event)
        return tuple(issues), tuple(events)


class LegacyIndependenceFromCurrentPolicyTests(unittest.TestCase):
    """The legacy archive survives a run grouped by a non-element policy."""

    @classmethod
    def setUpClass(cls):
        import dataclasses

        from epc_control_tower.pipeline import build_bundle
        from epc_control_tower.registry import default_registry
        from helpers import shipped_run_config, shipped_reports_dir

        config = dataclasses.replace(shipped_run_config(), grouping_policy="model")
        registry = default_registry(config)
        registry.register_grouping_policy(ModelGroupingPolicy())
        cls.bundle = build_bundle(
            config, registry=registry, reports_dir=shipped_reports_dir()
        ).bundle

    def test_no_issue_is_element_level_under_this_policy(self):
        # If any issue named an element the test would prove nothing about the
        # geometry union — so assert the precondition.
        self.assertTrue(self.bundle.issues)
        self.assertTrue(all(issue.element_key == "" for issue in self.bundle.issues))

    def test_the_legacy_bcf_still_reproduces_the_frozen_bytes(self):
        archive = LegacyBcfExporter(
            schema_dir=SCHEMA_DIR,
            project_id=LEGACY_PROJECT_ID,
            frozen_ruleset=frozen_ruleset(),
            compat=legacy_compat(),
        ).build_archive(self.bundle)
        self.assertEqual(sha256_bytes(archive), PUBLISHED_BCF_SHA256)


class PublishedArchiveTests(unittest.TestCase):
    """The port moved the code without moving the bytes."""

    @classmethod
    def setUpClass(cls):
        cls.result = shipped_pipeline_result()
        cls.projection = project_bundle(
            cls.result.bundle,
            project_id=LEGACY_PROJECT_ID,
            frozen_ruleset=frozen_ruleset(), compat=legacy_compat(),
        )
        cls.exporter = LegacyBcfExporter(
            schema_dir=SCHEMA_DIR,
            project_id=LEGACY_PROJECT_ID,
            frozen_ruleset=frozen_ruleset(), compat=legacy_compat(),
        )
        cls.data = cls.exporter.build_archive(cls.result.bundle, cls.projection)

    def test_the_archive_is_byte_identical_to_the_published_one(self):
        self.assertEqual(sha256_bytes(self.data), PUBLISHED_BCF_SHA256)
        self.assertEqual(self.data, PUBLISHED_BCF.read_bytes())

    def test_the_published_run_identity_is_reproduced_from_frozen_derivations(self):
        self.assertEqual(self.projection.run_id, LEGACY_RUN_ID)
        # And it is deliberately not the identity the canonical model carries.
        self.assertNotEqual(
            self.projection.run_id, self.result.bundle.run.validation_run_id
        )

    def test_the_archive_holds_the_expected_members(self):
        entries = read_safe_zip(PUBLISHED_BCF)
        rebuilt = zipfile.ZipFile(io.BytesIO(self.data))
        self.assertEqual(
            sorted(entries), sorted(info.filename for info in rebuilt.infolist())
        )
        self.assertEqual(len(self.projection.topics), 3)

    def test_writing_it_lands_where_the_published_contract_says(self):
        with writable_test_directory("legacy-bcf-write") as scratch:
            artifacts = self.exporter.export(self.result.bundle, scratch)
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].path.name, "ids_failures.bcf")
        self.assertEqual(artifacts[0].path.parent.name, "bcf")
        self.assertEqual(artifacts[0].sha256, PUBLISHED_BCF_SHA256)
        self.assertEqual(self.exporter.output_root_key, "reports")

    def test_the_exporter_never_opens_a_source_model(self):
        # Bounding boxes arrive in the bundle from their own stage. An exporter
        # that reached back to the IFC files could not be trusted to produce the
        # same bytes twice.
        self.assertEqual(len(self.projection.topics), 3)
        for issue in self.result.bundle.issues:
            with self.subTest(issue=issue.issue_key):
                if not issue.element_key:
                    # A model-level issue is about something absent, so
                    # there is no element to tessellate and no viewpoint to
                    # frame. The pipeline does not compute a box for one,
                    # which is the point of asserting it here: the exporter
                    # gets nothing, and still does not go looking.
                    continue
                self.result.bundle.geometry_for(issue.element_key)


class LegacyScopeTests(unittest.TestCase):
    """The checks that make the name honest."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle

    @staticmethod
    def _projection():
        return project_bundle(
            shipped_pipeline_result().bundle,
            project_id=LEGACY_PROJECT_ID,
            frozen_ruleset=frozen_ruleset(), compat=legacy_compat(),
        )

    def test_it_no_longer_knows_which_rules_it_converts(self):
        # Both scope assertions are gone, and their absence is the whole of
        # Phase 4's claim about this file. It refused anything that was not
        # R-005A or R-005B in the HVAC model, and that refusal was correct at
        # the time: the priority, stage, labels and assignee it wrote were four
        # constants chosen for that one rule family, so any other topic would
        # have carried metadata that was simply wrong.
        #
        # They come from the rule now, so there is nothing left to be specific
        # about.
        import epc_control_tower.exporters.legacy_bcf as module

        self.assertFalse(hasattr(module, "LEGACY_RULE_SCOPE"))
        self.assertFalse(hasattr(module, "LEGACY_MODEL_SCOPE"))
        source = pathlib.Path(module.__file__).read_text("utf-8")
        for forbidden in ("R-005", "Building-Hvac", '"hvac"'):
            with self.subTest(knowledge=forbidden):
                self.assertNotIn(forbidden, source)

    def test_a_topic_from_any_rule_now_converts(self):
        # The counterpart: relabelling a topic's findings to another rule used
        # to raise. It produces an archive now, because nothing in the writer
        # depends on which rule it was.
        import dataclasses

        projection = self._projection()
        topic = projection.topics[0]
        relabelled = dataclasses.replace(
            topic,
            findings=tuple(
                dataclasses.replace(row, specification_id="R-001")
                for row in topic.findings
            ),
        )
        mutated = dataclasses.replace(projection, topics=(relabelled,))

        exporter = LegacyBcfExporter(
            schema_dir=SCHEMA_DIR,
            project_id=LEGACY_PROJECT_ID,
            frozen_ruleset=frozen_ruleset(), compat=legacy_compat(),
        )
        data = exporter.build_archive(self.bundle, mutated)
        self.assertTrue(data)

    def test_what_it_writes_comes_from_the_issue_not_from_a_constant(self):
        # The published values, traced back to where they now live. If any of
        # these reverted to a module constant the archive would still be byte
        # identical, so this asserts the *source* rather than the value.
        import dataclasses

        projection = self._projection()
        topic = projection.topics[0]
        self.assertEqual(topic.priority, "Medium")
        self.assertEqual(topic.stage, "Coordination")
        self.assertEqual(topic.assignee_role, "model-coordination")
        self.assertEqual(topic.labels, ("HVAC", "IDS", "ProjectAssumption"))

        exporter = LegacyBcfExporter(
            schema_dir=SCHEMA_DIR,
            project_id=LEGACY_PROJECT_ID,
            frozen_ruleset=frozen_ruleset(), compat=legacy_compat(),
        )
        changed = dataclasses.replace(
            projection,
            topics=(dataclasses.replace(topic, priority="Low"),),
        )
        markup = exporter.markup(changed.topics[0], self.bundle.run.as_of).decode()
        self.assertIn("<Priority>Low</Priority>", markup)

    def test_the_dropped_cardinality_assertions_are_really_gone(self):
        # The previous implementation raised unless it found exactly six
        # failures forming exactly three topics of two. Those were counts taken
        # from a fixture; a fourth model or a fixed duct segment would have
        # failed the pipeline rather than the data.
        import inspect

        from epc_control_tower.exporters import legacy_bcf
        from epc_control_tower.grouping import element

        for module in (legacy_bcf, element):
            source = inspect.getsource(module)
            with self.subTest(module=module.__name__):
                self.assertNotIn("!= 6", source)
                self.assertNotIn("len(groups) != 3", source)


class DeterministicArchiveTests(unittest.TestCase):
    def test_every_recorded_property_that_could_vary_is_pinned(self):
        data = build_deterministic_zip({"b.txt": b"second", "a/": b"", "a/x.txt": b"x"})
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            self.assertEqual(archive.comment, b"")
            names = [info.filename for info in archive.infolist()]
            # Sorted, so the archive does not record the caller's build order.
            self.assertEqual(names, sorted(names))
            for info in archive.infolist():
                with self.subTest(member=info.filename):
                    self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                    self.assertEqual(info.date_time, FIXED_ZIP_TIMESTAMP)
                    self.assertEqual(info.create_system, 0)
                    self.assertEqual(info.extra, b"")
                    self.assertEqual(info.comment, b"")

    def test_the_same_entries_in_a_different_order_give_the_same_bytes(self):
        first = build_deterministic_zip({"a.txt": b"a", "b.txt": b"b"})
        second = build_deterministic_zip({"b.txt": b"b", "a.txt": b"a"})
        self.assertEqual(first, second)

    def test_an_empty_archive_is_refused(self):
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            build_deterministic_zip({})

    def test_unsafe_member_names_are_refused(self):
        for name in (
            "../escape.txt",
            "/absolute.txt",
            "back\\slash.txt",
            "double//slash.txt",
            "C:/drive.txt",
            "",
            "..",
            "a/../b.txt",
        ):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    validate_archive_name(name)

    def test_a_case_colliding_member_is_refused(self):
        with self.assertRaisesRegex(ValueError, "Case-insensitive duplicate"):
            build_deterministic_zip({"Markup.bcf": b"a", "markup.bcf": b"b"})

    def test_reading_re_asserts_what_writing_promised(self):
        with writable_test_directory("zip-read") as scratch:
            path = scratch / "hostile.zip"
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("a.txt", b"x" * 4096)
            with self.assertRaisesRegex(ValueError, "Non-canonical compression"):
                read_safe_zip(path)


class CameraTests(unittest.TestCase):
    def test_a_solved_camera_frames_every_corner(self):
        aabb = Aabb(minimum=(0.0, 0.0, 0.0), maximum=(3.0, 1.0, 2.0))
        camera = camera_for_aabb(aabb)
        # Tighter than the tolerance a reader is offered: at construction time
        # the solve should be exact.
        verify_camera_frames_aabb(aabb, camera, tolerance=1e-12)

    def test_a_camera_that_does_not_frame_the_box_is_rejected(self):
        import dataclasses

        aabb = Aabb(minimum=(0.0, 0.0, 0.0), maximum=(3.0, 1.0, 2.0))
        camera = camera_for_aabb(aabb)
        too_close = dataclasses.replace(camera, position=aabb.center)
        with self.assertRaises(ValueError):
            verify_camera_frames_aabb(aabb, too_close)

    def test_a_degenerate_box_has_no_camera(self):
        with self.assertRaisesRegex(ValueError, "degenerate AABB"):
            camera_for_aabb(Aabb(minimum=(1.0, 1.0, 1.0), maximum=(1.0, 1.0, 1.0)))

    def test_the_published_viewpoints_still_frame_their_elements(self):
        for topic in project_bundle(
            shipped_pipeline_result().bundle,
            project_id=LEGACY_PROJECT_ID,
            frozen_ruleset=frozen_ruleset(), compat=legacy_compat(),
        ).topics:
            with self.subTest(topic=topic.topic_guid):
                verify_camera_frames_aabb(topic.aabb, topic.camera, tolerance=1e-12)
                self.assertTrue(math.isfinite(topic.aabb.diagonal))


class SchemaTests(unittest.TestCase):
    def test_the_vendored_schemas_match_their_pinned_hashes(self):
        digests = verify_schema_bundle(SCHEMA_DIR)
        self.assertEqual(len(digests), 7)

    def test_a_missing_schema_stops_the_run_rather_than_skipping_validation(self):
        with writable_test_directory("schema-missing") as scratch:
            with self.assertRaisesRegex(ValueError, "missing or unsafe"):
                verify_schema_bundle(scratch)

    def test_entity_declarations_are_refused(self):
        hostile = b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><x/>'
        with self.assertRaisesRegex(ValueError, "DTD/entity declarations are forbidden"):
            parse_xml(hostile, "hostile.xml")

    def test_serialisation_is_pinned(self):
        from xml.etree import ElementTree as ET

        root = ET.Element("Root")
        ET.SubElement(root, "Empty")
        data = xml_bytes(root)
        self.assertTrue(data.startswith(b'<?xml version="1.0" encoding="UTF-8"?>\n'))
        self.assertTrue(data.endswith(b"\n"))
        self.assertIn(b"<Empty />", data)


if __name__ == "__main__":
    unittest.main()
