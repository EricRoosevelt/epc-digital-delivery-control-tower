"""Purpose configuration exists, and the published tree does not notice.

`AGENTS.md` rule 6 is the reason this file runs the pipeline instead of reading
the code: twice in this project's history a change that "obviously" could not
move a published byte moved every one of them, and in both cases the code
reported success while doing the wrong thing. Reading ``load_project_manifest``
and observing that it only picks named tables is an argument. Running the
pipeline with and without a Pack library and an ``[overlay]`` and diffing the
bytes is a measurement.

So each of ADR 0002 §4's four changed-input counterfactuals is executed here,
plus the two ADR 0003 §8 adds that this checkpoint can reach. A full run takes
about a second and a half, which is cheap enough that these stay true rather
than merely having been true once.

The fourth counterfactual — giving ``iso-reference-view`` an ``[overlay]`` — is
run against a **copy** of the manifest and never against the repository's own.
That project is three unrelated sample files; binding it to a coordination
Purpose would assert it is a project with an MEP-to-Architecture handover, and
it is not.
"""

from __future__ import annotations

import ast
import dataclasses
import shutil
import tomllib
import unittest
from pathlib import Path

from epc_control_tower.determinism import sha256_file
from epc_control_tower.pipeline import execute
from epc_control_tower.purpose import (
    compose_purpose_inputs,
    load_project_overlay,
    load_purpose_pack,
)
from helpers import (
    PROJECT_ROOT,
    shipped_pipeline_result,
    shipped_run_config,
    writable_test_directory,
)
from purpose_fixtures import (
    PACK_PATH,
    base_pack_document,
    mutated,
    synthetic_pair_pack,
    write_pack,
)

PACKAGE = PROJECT_ROOT / "epc_control_tower"
PACKS_ROOT = PROJECT_ROOT / "purpose-packs"
PCERT_MANIFEST = PROJECT_ROOT / "projects" / "pcert-sample" / "project.toml"
ISO_MANIFEST = PROJECT_ROOT / "projects" / "iso-reference-view" / "project.toml"


def _run_into(out: Path, *, projects_dir: Path | None = None) -> dict[str, str]:
    """Run the whole pipeline into ``out`` and digest every file it produced.

    Always the *same* destination across a comparison. The artifact manifests
    record where each output went, so two runs into two different directories
    differ legitimately and would prove nothing — the same trap
    ``test_determinism`` documents.
    """

    config = dataclasses.replace(
        shipped_run_config(),
        processed_data_dir=out / "processed",
        reports_dir=out / "reports",
    )
    if projects_dir is not None:
        config = dataclasses.replace(
            config,
            project_manifests=tuple(sorted(projects_dir.glob("*/project.toml"))),
        )
    execute(config)
    return {
        path.relative_to(out).as_posix(): sha256_file(path)
        for path in sorted(out.rglob("*"))
        if path.is_file()
    }


def _copy_projects(destination: Path) -> Path:
    """A private copy of ``projects/``, so a counterfactual edits nothing real."""

    target = destination / "projects"
    shutil.copytree(PROJECT_ROOT / "projects", target)
    return target


class PublishedTreeIsUnmovedTests(unittest.TestCase):
    """ADR 0002 §4's counterfactuals, executed rather than argued."""

    def _compare(self, mutate) -> None:
        """Run, apply the counterfactual, run again into the same place, diff.

        ``mutate`` receives a scratch directory for its fixtures and returns a
        replacement ``projects/`` directory or ``None``.
        """

        with writable_test_directory("purpose-cf") as scratch:
            out = scratch / "out"
            out.mkdir()
            fixtures = scratch / "fixtures"
            fixtures.mkdir()

            before = _run_into(out)
            self.assertGreater(len(before), 20, "the baseline run produced almost nothing")

            projects_dir = mutate(fixtures)
            # Same destination *path*, emptied first. The artifact manifests
            # record where each output went, so the path has to be identical
            # for the comparison to mean anything; clearing it avoids racing a
            # Windows file lock on the atomic replace.
            shutil.rmtree(out)
            out.mkdir()
            after = _run_into(out, projects_dir=projects_dir)

        self.assertEqual(sorted(after), sorted(before))
        for name in sorted(before):
            with self.subTest(artifact=name):
                self.assertEqual(after[name], before[name])

    def test_the_shipped_pack_and_overlay_move_no_published_byte(self):
        """The state this checkpoint lands: both files present, nothing moved."""

        self.assertTrue(PACK_PATH.is_file())
        self.assertIn("[overlay]", PCERT_MANIFEST.read_text(encoding="utf-8"))
        self._compare(lambda fixtures: None)

    def test_counterfactual_1_changing_only_a_purpose(self):
        """Edit the Pack library in place; touch no project.

        The edit goes into the repository's own ``purpose-packs/``, because
        that is the only place a Pack library exists — there is no
        configuration knob pointing the pipeline at one, which is itself the
        result being measured. It is removed again in every outcome.
        """

        def mutate(fixtures: Path):
            document = mutated(base_pack_document())
            document["pack_id"] = "counterfactual-edited-pack"
            document["pack_version"] = "9.9.9"
            document["evidence_requirements"][0]["answers"] = "something else entirely"
            document["resolution_routes"][0]["next_action"] = "a different action"
            write_pack(PACKS_ROOT, document)
            return None

        added = PACKS_ROOT / "counterfactual-edited-pack"
        try:
            self._compare(mutate)
            self.assertTrue(added.is_dir(), "the counterfactual must really have added a Pack")
        finally:
            shutil.rmtree(added, ignore_errors=True)
        self.assertFalse(added.exists())

    def test_counterfactual_2_changing_only_an_overlay(self):
        """Edit pcert-sample's [overlay]; touch no model, ruleset or programme."""

        def mutate(fixtures: Path):
            projects = _copy_projects(fixtures)
            manifest = projects / "pcert-sample" / "project.toml"
            text = manifest.read_text(encoding="utf-8")
            edited = text.replace(
                'team_or_person = "coordination-team"', 'team_or_person = "someone-else"'
            ).replace('decision_basis = "illustrative"', 'decision_basis = "project-decision"')
            self.assertNotEqual(edited, text)
            manifest.write_text(edited, encoding="utf-8")
            return projects

        self._compare(mutate)

    def test_counterfactual_3_adding_a_pack_no_project_references(self):
        def mutate(fixtures: Path):
            document = synthetic_pair_pack()
            document["pack_id"] = "counterfactual-unreferenced-pack"
            write_pack(PACKS_ROOT, document)
            return None

        added = PACKS_ROOT / "counterfactual-unreferenced-pack"
        try:
            self._compare(mutate)
            self.assertTrue(added.is_dir())
        finally:
            shutil.rmtree(added, ignore_errors=True)
        self.assertFalse(added.exists())

    def test_counterfactual_4_adding_an_overlay_to_iso_reference_view(self):
        """Run against a copy, and never leave the file in the repository.

        ``iso-reference-view`` is three unrelated buildingSMART samples. Binding
        it to a coordination Purpose would claim it is a project with an
        MEP-to-Architecture handover, which is a claim about a project this
        repository does not have — so the counterfactual is run and reverted,
        and the assertion at the end is that the real manifest never moved.
        """

        original = ISO_MANIFEST.read_bytes()

        def mutate(fixtures: Path):
            projects = _copy_projects(fixtures)
            manifest = projects / "iso-reference-view" / "project.toml"
            overlay_text = PCERT_MANIFEST.read_text(encoding="utf-8")
            overlay_text = overlay_text[overlay_text.index("[overlay]") :]
            manifest.write_text(
                manifest.read_text(encoding="utf-8") + "\n" + overlay_text,
                encoding="utf-8",
            )
            with manifest.open("rb") as stream:
                self.assertIn("overlay", tomllib.load(stream))
            return projects

        self._compare(mutate)

        self.assertEqual(ISO_MANIFEST.read_bytes(), original)
        self.assertNotIn("[overlay]", ISO_MANIFEST.read_text(encoding="utf-8"))
        self.assertIsNone(load_project_overlay(ISO_MANIFEST))

    def test_counterfactual_5_composing_the_inputs_writes_nothing(self):
        """ADR 0003 §8's fifth commitment, for the composition half."""

        from test_purpose_composition import _requirement_keys

        with writable_test_directory("purpose-cf5") as scratch:
            out = scratch / "out"
            out.mkdir()
            before = _run_into(out)
            composed = compose_purpose_inputs(
                project_id="pcert-sample",
                overlay=load_project_overlay(PCERT_MANIFEST),
                packs=(load_purpose_pack(PACK_PATH),),
                requirement_keys_by_ruleset=_requirement_keys(),
            )
            self.assertTrue(composed.composition_digest)
            after = {
                path.relative_to(out).as_posix(): sha256_file(path)
                for path in sorted(out.rglob("*"))
                if path.is_file()
            }
        self.assertEqual(before, after)

    def test_counterfactual_5_running_an_assessment_and_storing_a_record(self):
        """The rest of commitment 5: run one, materialise it, move nothing.

        The record is written to a scratch directory rather than kept in memory,
        because the commitment is about *storing* one. Storage is a later
        decision, so what is exercised here is the shape the assessment offers a
        future store — the canonical document — put somewhere on disk that is not
        ``data/processed/``, ``reports/``, ``ids/``, or the contract snapshot.
        """

        import assessment_fixtures as fixtures
        from epc_control_tower.determinism import json_bytes
        from epc_control_tower.purpose import assess_purpose

        with writable_test_directory("purpose-cf5b") as scratch:
            out = scratch / "out"
            out.mkdir()
            before = _run_into(out)

            facts = fixtures.assessment_facts()
            record = assess_purpose(
                request=fixtures.fixture_request(
                    activity_ids=(
                        "schedules-and-room-data-sheets",
                        "ceiling-and-bulkhead-geometry",
                        "builders-work-openings",
                    ),
                    facts=facts,
                ),
                composed=fixtures.fixture_composed(),
                facts=facts,
                determinations=fixtures.fixture_determinations(facts=facts),
            )
            self.assertTrue(record.assessment_digest)
            store = scratch / "assessments"
            store.mkdir()
            (store / f"{record.assessment_digest}.json").write_bytes(
                json_bytes(record.as_document())
            )

            after = {
                path.relative_to(out).as_posix(): sha256_file(path)
                for path in sorted(out.rglob("*"))
                if path.is_file()
            }
            self.assertEqual(sorted(store.iterdir()).__len__(), 1)

        self.assertEqual(before, after)

    def test_counterfactual_6_minting_a_digest_moves_no_frozen_identity(self):
        """ADR 0003 §8's sixth commitment: the dependency really is one-way.

        Two assessments whose digests differ — the second reads one determination
        fewer, so a verdict moves — over the *same* validated facts. Every
        ``validation_run_id``, ``requirement_key`` and ``finding_key`` the run
        produced is compared before and after, because "no identity takes an
        assessment value as input" is a claim about values and not about
        signatures.
        """

        import assessment_fixtures as fixtures
        from epc_control_tower.purpose import assess_purpose

        def identities(bundle):
            return (
                bundle.run.validation_run_id,
                tuple(sorted(item.requirement_key for item in bundle.ruleset.requirements)),
                tuple(sorted(item.finding_key for item in bundle.findings)),
                tuple(sorted(item.issue_key for item in bundle.issues)),
                bundle.ruleset.normalized_digest,
            )

        with writable_test_directory("purpose-cf6") as scratch:
            out = scratch / "out"
            out.mkdir()
            before = _run_into(out)
            bundle_before = identities(shipped_pipeline_result().bundle)

            facts = fixtures.assessment_facts()
            composed = fixtures.fixture_composed()
            activities = (
                "schedules-and-room-data-sheets",
                "ceiling-and-bulkhead-geometry",
                "builders-work-openings",
            )
            first = assess_purpose(
                request=fixtures.fixture_request(activity_ids=activities, facts=facts),
                composed=composed,
                facts=facts,
                determinations=fixtures.fixture_determinations(facts=facts),
            )
            second = assess_purpose(
                request=fixtures.fixture_request(activity_ids=activities, facts=facts),
                composed=composed,
                facts=facts,
                determinations=fixtures.fixture_determinations(facts=facts, alignment=False),
            )
            self.assertNotEqual(first.assessment_digest, second.assessment_digest)

            after = {
                path.relative_to(out).as_posix(): sha256_file(path)
                for path in sorted(out.rglob("*"))
                if path.is_file()
            }
            bundle_after = identities(shipped_pipeline_result().bundle)

        self.assertEqual(before, after)
        self.assertEqual(bundle_before, bundle_after)
        for digest in (first.assessment_digest, second.assessment_digest):
            with self.subTest(digest=digest[:12]):
                self.assertNotIn(digest, bundle_after[0])
                self.assertNotIn(digest, str(bundle_after))


class PipelineDoesNotKnowAboutPurposeTests(unittest.TestCase):
    """Not a Checker, not a GroupingPolicy, not an Exporter, not registered."""

    def test_the_registry_holds_no_purpose_component(self):
        from epc_control_tower.registry import default_registry

        registry = default_registry(shipped_run_config())
        rendered = repr(
            {
                name: sorted(getattr(registry, name, {}))
                for name in ("checkers", "grouping_policies", "exporters")
                if hasattr(registry, name)
            }
        )
        for word in ("purpose", "pack", "overlay", "assessment"):
            with self.subTest(word=word):
                self.assertNotIn(word, rendered.lower())

    def test_nothing_outside_the_purpose_package_imports_it(self):
        """`epc-ct run` cannot reach code no module on its path imports."""

        offenders = []
        for path in sorted(PACKAGE.rglob("*.py")):
            if path.parent.name == "purpose":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and "purpose" in (node.module or ""):
                    offenders.append(f"{path.name}: from {node.module}")
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if "purpose" in alias.name:
                            offenders.append(f"{path.name}: import {alias.name}")
        self.assertEqual(offenders, [])

    def test_the_manifest_loader_ignores_the_overlay_table(self):
        """Measured, not assumed: the overlay is present and not read."""

        from epc_control_tower.config import load_project_manifest

        manifest = load_project_manifest(PCERT_MANIFEST, repository_root=PROJECT_ROOT)
        rendered = repr(manifest)
        for word in ("overlay", "decision_basis", "coordination-team", "pack_version"):
            with self.subTest(word=word):
                self.assertNotIn(word, rendered)

    #: Every way this repository writes a file.
    WRITERS = frozenset(
        {
            "atomic_write_bytes",
            "write_csv_bytes",
            "json_bytes",
            "write_text",
            "write_bytes",
            "mkdir",
            "rename",
            "replace",
            "unlink",
        }
    )

    def test_the_purpose_package_calls_nothing_that_writes(self):
        """Checked over the parsed code, so a docstring cannot pass or fail it."""

        offenders = []
        for path in sorted((PACKAGE / "purpose").rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                function = node.func
                name = (
                    function.attr
                    if isinstance(function, ast.Attribute)
                    else getattr(function, "id", "")
                )
                if name in self.WRITERS:
                    offenders.append(f"{path.name}: {name}()")
                if name == "open":
                    for argument in list(node.args[1:]) + [
                        keyword.value for keyword in node.keywords
                    ]:
                        if isinstance(argument, ast.Constant) and "w" in str(argument.value):
                            offenders.append(f"{path.name}: open(..., {argument.value!r})")
        self.assertEqual(offenders, [])


class IdentityBoundaryTests(unittest.TestCase):
    """The composition digest cites frozen identities and is cited by none."""

    @classmethod
    def setUpClass(cls):
        from test_purpose_composition import _requirement_keys

        cls.composed = compose_purpose_inputs(
            project_id="pcert-sample",
            overlay=load_project_overlay(PCERT_MANIFEST),
            packs=(load_purpose_pack(PACK_PATH),),
            requirement_keys_by_ruleset=_requirement_keys(),
        )

    def test_no_identity_derivation_accepts_a_composition_value(self):
        import inspect

        from epc_control_tower import identity

        for name in (
            "build_validation_run_id",
            "build_requirement_key",
            "build_ruleset_normalized_digest",
            "build_finding_key",
            "build_issue_key",
        ):
            signature = inspect.signature(getattr(identity, name))
            with self.subTest(derivation=name):
                for parameter in signature.parameters:
                    self.assertNotIn("pack", parameter)
                    self.assertNotIn("overlay", parameter)
                    self.assertNotIn("composition", parameter)

    def test_the_digest_appears_in_no_published_artifact(self):
        digest = self.composed.composition_digest
        published = list((PROJECT_ROOT / "data" / "processed").rglob("*")) + list(
            (PROJECT_ROOT / "reports").rglob("*")
        )
        checked = 0
        for path in published:
            if not path.is_file():
                continue
            checked += 1
            with self.subTest(artifact=path.name):
                self.assertNotIn(digest.encode(), path.read_bytes())
        self.assertGreater(checked, 10)

    #: Calls that would make a digest depend on when or where it ran, or on
    #: how a file happened to be written rather than what it says.
    FORBIDDEN_CALLS = frozenset(
        {"now", "utcnow", "today", "time", "monotonic", "sha256_file", "read_bytes", "stat"}
    )

    def test_the_digest_reads_no_clock_and_no_file_bytes(self):
        """Over the parsed code: prose about mtimes is not a call to one."""

        source = (PACKAGE / "purpose" / "composition.py").read_text(encoding="utf-8")
        offenders = []
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            name = (
                function.attr
                if isinstance(function, ast.Attribute)
                else getattr(function, "id", "")
            )
            if name in self.FORBIDDEN_CALLS:
                offenders.append(name)
        self.assertEqual(offenders, [])


class SubjectClassIndependenceTests(unittest.TestCase):
    """ADR 0003 §8 commitment 7: object scope is genuinely per-activity.

    The commitment's substance — that one declared scope admits different
    subjects and leaves different keys out of class per activity — now runs
    through the evaluator, in
    ``test_purpose_assessment.DeclaredScopeTests.test_one_scope_admits_different_subjects_per_activity``.
    It used to be computed here instead, because the evaluator did not exist;
    that expectation has moved, as the note here said it would.

    What stays is the fact that made the move necessary. The shipped Pack's three
    activities declare the same three classes, so a test drawing its evidence
    from them would pass whether the field were per-activity or Pack-wide — and
    the shipped Pack must not be bent into differing just to make a test look
    like it proves something.
    """

    def test_the_shipped_pack_keeps_one_shared_class_list(self):
        shipped = load_purpose_pack(PACK_PATH)
        lists = {tuple(activity.subject_classes) for activity in shipped.activities}
        self.assertEqual(len(lists), 1)
        self.assertEqual(
            lists, {("IfcDuctSegment", "IfcAirTerminal", "IfcChimney")}
        )

    def test_the_commitment_is_discharged_against_differing_activities(self):
        """The moved test exists, and exercises classes that actually differ."""

        source = (PROJECT_ROOT / "tests" / "test_purpose_assessment.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("test_one_scope_admits_different_subjects_per_activity", source)
        self.assertIn('["IfcDuctSegment"]', source)
        self.assertIn('["IfcChimney"]', source)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
