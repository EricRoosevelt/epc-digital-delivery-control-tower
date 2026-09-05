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
from helpers import PROJECT_ROOT, shipped_run_config, writable_test_directory
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
        """ADR 0003 §8's fifth commitment, as far as this checkpoint reaches."""

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

    The shipped Pack's three activities declare the same three classes, which is
    a fact about this Pack and would make a test that used it prove nothing. So
    this uses a fixture whose activities differ, and asserts that one declared
    scope admits different subjects — and leaves different keys out of class —
    per activity.

    The admitted/out-of-class split is computed *here* rather than called,
    because the evaluator that would compute it does not exist yet. When it
    does, this expectation moves to it; what is being pinned now is that the
    Pack data supports the distinction at all.
    """

    #: A declared scope, as elements with the ifc_class elements.csv publishes.
    SCOPE = {
        "hvac::duct": "IfcDuctSegment",
        "hvac::terminal": "IfcAirTerminal",
        "hvac::chimney": "IfcChimney",
        "hvac::origin": "IfcBuildingElementProxy",
    }

    @classmethod
    def setUpClass(cls):
        document = mutated(base_pack_document())
        document["activities"][0]["subject_classes"] = ["IfcDuctSegment"]
        document["activities"][1]["subject_classes"] = ["IfcAirTerminal", "IfcChimney"]
        document["activities"][2]["subject_classes"] = ["IfcChimney"]
        cls._scratch = PROJECT_ROOT / "tests" / ".purpose-classes"
        shutil.rmtree(cls._scratch, ignore_errors=True)
        cls._scratch.mkdir()
        cls.pack = load_purpose_pack(write_pack(cls._scratch, document))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._scratch, ignore_errors=True)

    def _split(self, activity):
        declared = set(activity.subject_classes)
        admitted = {key for key, cls in self.SCOPE.items() if cls in declared}
        return admitted, set(self.SCOPE) - admitted

    def test_one_scope_admits_different_subjects_per_activity(self):
        splits = {
            activity.activity_id: self._split(activity) for activity in self.pack.activities
        }
        admitted = [frozenset(value[0]) for value in splits.values()]
        self.assertEqual(len(set(admitted)), 3, "each activity must admit a different set")
        out_of_class = [frozenset(value[1]) for value in splits.values()]
        self.assertEqual(len(set(out_of_class)), 3)

    def test_the_accounting_is_total_for_every_activity(self):
        for activity in self.pack.activities:
            admitted, out_of_class = self._split(activity)
            with self.subTest(activity=activity.activity_id):
                self.assertEqual(admitted | out_of_class, set(self.SCOPE))
                self.assertEqual(admitted & out_of_class, set())

    def test_a_zero_finding_element_is_admitted_by_class_not_by_coverage(self):
        """The chimney is in, and the setout proxy is out, for what they are."""

        for activity in self.pack.activities:
            admitted, out_of_class = self._split(activity)
            with self.subTest(activity=activity.activity_id):
                self.assertIn("hvac::origin", out_of_class)
        by_id = {activity.activity_id: activity for activity in self.pack.activities}
        admitted, _ = self._split(by_id["builders-work-openings"])
        self.assertEqual(admitted, {"hvac::chimney"})

    def test_the_shipped_pack_keeps_one_shared_class_list(self):
        """The fixture differentiates; the shipped Pack must not be bent to match."""

        shipped = load_purpose_pack(PACK_PATH)
        lists = {tuple(activity.subject_classes) for activity in shipped.activities}
        self.assertEqual(len(lists), 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
