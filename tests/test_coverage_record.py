"""The coverage record — ADR 0004, checkpoint 1.

What a run checked, and what it did not, at the two granularities the
validation layer owns: requirement × model, and element overall. The third,
requirement × member, belongs to a Purpose assessment and is recorded as
absent rather than approximated.

Most of these tests pin a counterexample rather than a count. Each one is a
way the record could have told a plausible untruth: calling an out-of-scope
pair "not checked" when it was executed, letting a pair whose results went
missing disappear, labelling a project's adoption with a decision nobody
made, or shipping itself inside the published tree.
"""

from __future__ import annotations

import dataclasses
import json
import shutil
import unittest
from pathlib import Path

from epc_control_tower.coverage import (
    ADOPTION_VALUES,
    COVERAGE_DIR_VARIABLE,
    EXECUTION_STATES,
    LEGACY_COMPAT_PROJECT_IDS,
    SCOPE_RELATIONS,
    build_coverage_record,
    resolve_coverage_root,
)
from epc_control_tower.determinism import sha256_file
from epc_control_tower.pipeline import build_bundle, execute
from epc_control_tower.protocols import CheckOutcome
from epc_control_tower.registry import default_registry
from helpers import (
    PROJECT_ROOT,
    outside_repository_directory,
    shipped_pipeline_result,
    shipped_run_config,
    writable_test_directory,
)


def _shipped_record() -> dict:
    config = shipped_run_config()
    return build_coverage_record(
        shipped_pipeline_result().bundle, ruleset_path=config.resolved_ruleset_path()
    )


def _row(record: dict, model_key: str, rule_id: str) -> dict:
    rows = [
        row
        for row in record["requirement_x_model"]
        if row["model_key"] == model_key and row["rule_id"] == rule_id
    ]
    if len(rows) != 1:
        raise AssertionError(f"{len(rows)} rows for {model_key} × {rule_id}")
    return rows[0]


class RequirementByModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = _shipped_record()
        cls.rows = cls.record["requirement_x_model"]

    def test_every_pair_of_the_run_has_exactly_one_row(self):
        bundle = shipped_pipeline_result().bundle
        expected = sorted(
            (model.model_key, requirement.requirement_key)
            for model in bundle.models
            for requirement in bundle.ruleset.requirements
        )
        recorded = sorted((row["model_key"], row["requirement_key"]) for row in self.rows)
        self.assertEqual(recorded, expected)
        # Six models, fourteen requirements (twelve rules; R-005A and R-005B
        # carry two requirements each).
        self.assertEqual(len(recorded), 84)

    def test_each_axis_carries_exactly_one_value(self):
        for row in self.rows:
            with self.subTest(model=row["model_key"], rule=row["requirement_key"]):
                declaration, execution = row["declaration"], row["execution"]
                self.assertIn(declaration["adoption"], ADOPTION_VALUES)
                self.assertIn(declaration["scope_relation"], SCOPE_RELATIONS)
                self.assertIn(execution["state"], EXECUTION_STATES)
                # A reason belongs to not-executed and to nothing else.
                if execution["state"] == "not-executed":
                    self.assertTrue(execution["not_executed_reason"])
                else:
                    self.assertIsNone(execution["not_executed_reason"])

    def test_r001_on_pcert_structural_walls_is_outside_scope_and_executed(self):
        # The case ADR 0004 §2.2 names. R-001 is scoped to Architecture, the
        # model is Structural, and the rule ran anyway: four walls, four
        # passes. Recording it as "not checked" would hide an over-check.
        row = _row(self.record, "structural", "R-001")
        self.assertEqual(row["declaration"]["discipline_scope"], ["Architecture"])
        self.assertEqual(row["declaration"]["scope_relation"], "outside")
        self.assertEqual(row["execution"]["state"], "executed-with-results")
        self.assertEqual(row["result"]["predicate"]["state"], "derived")
        self.assertEqual(row["result"]["statuses"], {"FAIL": 0, "N/A": 0, "PASS": 4})

    def test_the_published_run_crosses_the_axes_as_adr_0004_measured(self):
        # §1: 5 inside and 52 outside return only N/A; 25 inside and 2
        # outside return PASS/FAIL; none returns nothing.
        crossed = self.record["summary"]["execution_by_scope_relation"]
        self.assertEqual(crossed["executed-no-applicable-entity"]["inside"], 5)
        self.assertEqual(crossed["executed-no-applicable-entity"]["outside"], 52)
        self.assertEqual(crossed["executed-with-results"]["inside"], 25)
        self.assertEqual(crossed["executed-with-results"]["outside"], 2)
        self.assertEqual(sum(crossed["executed-no-result"].values()), 0)
        self.assertEqual(sum(crossed["not-executed"].values()), 0)

    def test_both_published_samples_are_legacy_compat_and_nothing_is_adopted(self):
        self.assertEqual(
            sorted(LEGACY_COMPAT_PROJECT_IDS), ["iso-reference-view", "pcert-sample"]
        )
        for row in self.rows:
            with self.subTest(model=row["model_key"], rule=row["requirement_key"]):
                self.assertEqual(row["declaration"]["adoption"], "legacy-compat")


class PredicateTests(unittest.TestCase):
    """P8: a status travels with the predicate it answers, or not at all."""

    @classmethod
    def setUpClass(cls):
        cls.record = _shipped_record()

    def test_a_predicate_names_every_constraint_the_rule_declares(self):
        # IfcTester's own sentence for R-002 drops the data type; the record
        # must not, because "IsExternal is an IfcBoolean" is half of what a
        # PASS here actually asserts.
        predicate = _row(self.record, "architecture", "R-002")["result"]["predicate"]
        self.assertEqual(predicate["applicability"], ["entity[name=IFCWALL]"])
        self.assertIn("dataType=IFCBOOLEAN", predicate["requirement"])
        self.assertIn("propertySet=Pset_WallCommon", predicate["requirement"])

    def test_a_predicate_says_what_the_rule_leaves_unconstrained(self):
        # R-002 checks presence and type, never the value (ADR 0004 P3).
        predicate = _row(self.record, "architecture", "R-002")["result"]["predicate"]
        self.assertEqual(predicate["not_constrained"], ["value"])
        name = _row(self.record, "architecture", "R-001")["result"]["predicate"]
        self.assertEqual(name["not_constrained"], ["value"])

    def test_without_a_reliable_predicate_no_status_is_shown(self):
        # R-010 is evaluated by the completeness checker. What its facet means
        # lives in that checker's code, not in a standard, so no predicate can
        # be read off the rule — and then neither PASS nor FAIL is shown.
        for model_key in ("architecture", "hvac", "structural"):
            with self.subTest(model=model_key):
                row = _row(self.record, model_key, "R-010")
                self.assertEqual(row["execution"]["state"], "executed-with-results")
                self.assertEqual(row["result"]["predicate"]["state"], "unavailable")
                self.assertTrue(row["result"]["predicate"]["reason"])
                self.assertIsNone(row["result"]["statuses"])
                self.assertGreater(row["result"]["finding_count"], 0)
                self.assertNotIn("PASS", json.dumps(row))

    def test_every_status_shown_has_a_derived_predicate_beside_it(self):
        for row in self.record["requirement_x_model"]:
            with self.subTest(model=row["model_key"], rule=row["requirement_key"]):
                if row["result"]["statuses"] is not None:
                    self.assertEqual(row["result"]["predicate"]["state"], "derived")


class OtherGranularitiesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = _shipped_record()

    def test_the_member_layer_is_stated_absent(self):
        member = self.record["requirement_x_member"]
        self.assertEqual(member["layer"], "no-member-layer")
        self.assertIn("Purpose assessment", member["reason"])

    def test_elements_are_recorded_as_reached_or_not_by_this_rule_set(self):
        elements = self.record["element_overall"]
        self.assertEqual(len(elements), 44)
        reach = sorted({row["reach"] for row in elements})
        self.assertEqual(
            reach, ["has-results-from-this-ruleset", "no-result-from-this-ruleset"]
        )
        unreached = [row for row in elements if row["reach"] == "no-result-from-this-ruleset"]
        self.assertEqual(len(unreached), 22)
        for row in unreached:
            self.assertEqual(row["finding_count"], 0)

    def test_nothing_in_the_record_calls_an_element_unchecked(self):
        # §2.1: "no result touched it" is not "never checked". The record's
        # wording must not be able to say the second.
        text = json.dumps(self.record).lower()
        for phrase in ("unchecked", "not checked", "not-checked", "never checked"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)


class DroppedResultTests(unittest.TestCase):
    """ADR 0004 §2.4: a pair that executed and lost its results stays visible."""

    def test_an_injected_silent_drop_lands_in_executed_no_result(self):
        config = shipped_run_config()
        registry = default_registry(config)
        registry.checkers["ids"] = _DroppingChecker(
            registry.checkers["ids"], model_key="structural", rule_id="R-001"
        )
        with writable_test_directory("coverage-drop") as scratch:
            # Exit status of the counterexample: the run itself completes and
            # says nothing. Without the record the loss is invisible.
            result = build_bundle(config, registry=registry, reports_dir=scratch)
        record = build_coverage_record(
            result.bundle, ruleset_path=config.resolved_ruleset_path()
        )

        self.assertEqual(len(record["requirement_x_model"]), 84)
        row = _row(record, "structural", "R-001")
        self.assertEqual(row["execution"]["state"], "executed-no-result")
        self.assertEqual(row["result"]["finding_count"], 0)
        self.assertEqual(
            record["summary"]["execution_by_scope_relation"]["executed-no-result"],
            {"inside": 0, "outside": 1, "unknown": 0},
        )


class _DroppingChecker:
    """Delegates to a real checker and silently discards one pair's findings."""

    def __init__(self, inner, *, model_key: str, rule_id: str) -> None:
        self._inner = inner
        self._model_key = model_key
        self._rule_id = rule_id
        self.id = inner.id
        self.version = inner.version
        self.capabilities = inner.capabilities

    def config_sha256(self) -> str:
        return self._inner.config_sha256()

    def check(self, context):
        outcome = self._inner.check(context)
        dropped = {
            requirement.requirement_key
            for requirement in context.requirements
            if requirement.rule_id == self._rule_id
        }
        kept = tuple(
            finding
            for finding in outcome.findings
            if not (
                finding.model_key == self._model_key
                and finding.requirement_key in dropped
            )
        )
        return CheckOutcome(findings=kept, failures=outcome.failures)


class IsolatedProjectAdoptionTests(unittest.TestCase):
    """Boundary: before checkpoint 4, a new project's adoption is neither
    ``legacy-compat`` nor ``adopted`` — nobody decided anything for it."""

    def test_a_non_sample_project_is_recorded_as_undeclared(self):
        with writable_test_directory("coverage-isolated") as scratch:
            manifest = _isolated_project(scratch, project_id="probe-coverage")
            config = dataclasses.replace(
                shipped_run_config(),
                project_manifests=(manifest,),
                processed_data_dir=scratch / "processed",
                reports_dir=scratch / "reports",
            )
            result = build_bundle(config, reports_dir=scratch / "reports")
        record = build_coverage_record(
            result.bundle, ruleset_path=config.resolved_ruleset_path()
        )

        self.assertEqual(record["adoption_mechanism"], "not-implemented")
        rows = record["requirement_x_model"]
        self.assertEqual(len(rows), 14)
        for row in rows:
            with self.subTest(rule=row["requirement_key"]):
                self.assertEqual(row["declaration"]["adoption"], "undeclared")
                # "Facade" is in no rule's discipline_scope vocabulary.
                self.assertEqual(row["declaration"]["scope_relation"], "unknown")
        self.assertEqual(record["summary"]["adoption"], {"undeclared": 14})

    def test_resembling_a_sample_is_not_being_one(self):
        with writable_test_directory("coverage-lookalike") as scratch:
            manifest = _isolated_project(scratch, project_id="pcert-sample-copy")
            config = dataclasses.replace(
                shipped_run_config(), project_manifests=(manifest,)
            )
            result = build_bundle(config, reports_dir=scratch / "reports")
        record = build_coverage_record(
            result.bundle, ruleset_path=config.resolved_ruleset_path()
        )
        self.assertEqual(record["summary"]["adoption"], {"undeclared": 14})


def _isolated_project(scratch: Path, *, project_id: str) -> Path:
    """A one-model project assembled from a tracked sample, outside projects/."""

    source = PROJECT_ROOT / "projects" / "iso-reference-view"
    directory = scratch / "projects" / project_id
    directory.mkdir(parents=True)
    shutil.copyfile(
        source / "wall-with-opening-and-window.ifc", directory / "facade.ifc"
    )
    manifest = directory / "project.toml"
    manifest.write_bytes(
        (
            "[project]\n"
            f'project_id = "{project_id}"\n'
            'name = "Coverage counterexample"\n'
            "\n"
            "[[models]]\n"
            'model_id = "facade"\n'
            'discipline = "Facade"\n'
            'filename = "facade.ifc"\n'
            'source_url = "tracked sample, copied"\n'
            'license = "CC BY 4.0"\n'
            'content_sha256 = "'
            + sha256_file(directory / "facade.ifc")
            + '"\n'
            "\n"
            "[[milestones]]\n"
            'stage = "Design"\n'
            'due = "2026-07-01T00:00:00Z"\n'
            "\n"
            "[[milestones]]\n"
            'stage = "Coordination"\n'
            'due = "2026-08-01T00:00:00Z"\n'
            "\n"
            "[[milestones]]\n"
            'stage = "Handover"\n'
            'due = "2026-12-01T00:00:00Z"\n'
        ).encode("utf-8")
    )
    return manifest


class PersistenceTests(unittest.TestCase):
    """P7: kept, bound to its run, outside the published tree — and the
    published tree does not notice."""

    def _run(self, scratch: Path, coverage_root: Path | None):
        config = dataclasses.replace(
            shipped_run_config(),
            processed_data_dir=scratch / "processed",
            reports_dir=scratch / "reports",
        )
        result = execute(config, coverage_root=coverage_root)
        published = {
            path.relative_to(scratch).as_posix(): sha256_file(path)
            for path in sorted(scratch.rglob("*"))
            if path.is_file()
        }
        return result, published

    def test_the_record_is_kept_outside_the_published_tree_and_moves_no_byte(self):
        with (
            writable_test_directory("coverage-published") as scratch,
            outside_repository_directory("coverage-root") as root,
        ):
            # Into the same destination each time: the manifests record where
            # their artifacts went, so two destinations would differ anyway.
            without, before = self._run(scratch, None)
            with_record, after = self._run(scratch, root)
            again, _ = self._run(scratch, root)

            path = with_record.coverage_record_path
            first = path.read_bytes()
            second = again.coverage_record_path.read_bytes()
            kept = sorted(
                p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()
            )

        # Published bytes, identity and manifest: nothing moved.
        self.assertEqual(before, after)
        self.assertEqual(
            without.export.artifact_bundle_id, with_record.export.artifact_bundle_id
        )
        self.assertIsNone(without.coverage_record_path)
        for name in after:
            self.assertNotIn("coverage", name)

        # Bound to the run that produced it, and kept.
        run_id = with_record.pipeline.bundle.run.validation_run_id
        self.assertEqual(path.parent.name, run_id)
        self.assertEqual(json.loads(first)["run"]["validation_run_id"], run_id)
        self.assertEqual(len(kept), 1)

        # Deterministic: same run, same bytes, same place, LF only.
        self.assertEqual(again.coverage_record_path, path)
        self.assertEqual(first, second)
        self.assertNotIn(b"\r\n", first)
        self.assertTrue(first.endswith(b"\n"))

    def test_no_component_is_registered_for_the_record(self):
        # It is neither a checker, a grouping policy nor an exporter. The
        # artifact manifest digests the exporter list, so registering it as one
        # would have moved artifact_bundle_id.
        registry = default_registry(shipped_run_config())
        for kind in (registry.checkers, registry.grouping_policies, registry.exporters):
            for component_id in kind:
                self.assertNotIn("coverage", component_id)

    def test_a_location_inside_the_repository_is_refused(self):
        for inside in (
            PROJECT_ROOT / "coverage",
            PROJECT_ROOT / "reports" / "coverage",
            PROJECT_ROOT,
        ):
            with self.subTest(location=inside):
                with self.assertRaises(ValueError):
                    resolve_coverage_root(
                        PROJECT_ROOT, environ={COVERAGE_DIR_VARIABLE: str(inside)}
                    )

    def test_the_default_location_is_the_users_state_directory(self):
        root = resolve_coverage_root(
            PROJECT_ROOT,
            environ={"LOCALAPPDATA": "/state/win", "XDG_STATE_HOME": "/state/xdg"},
        )
        self.assertEqual(root.parts[-2:], ("epc-control-tower", "coverage"))
        self.assertFalse(root.resolve().is_relative_to(PROJECT_ROOT.resolve()))


class CommandLineTests(unittest.TestCase):
    def test_check_writes_no_coverage_record(self):
        import contextlib
        import io
        import os

        from epc_control_tower.cli import main

        with (
            writable_test_directory("coverage-check") as scratch,
            outside_repository_directory("coverage-check-root") as root,
        ):
            previous = os.environ[COVERAGE_DIR_VARIABLE]
            os.environ[COVERAGE_DIR_VARIABLE] = str(root)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = main(["check", "--reports-dir", str(scratch)])
            finally:
                os.environ[COVERAGE_DIR_VARIABLE] = previous
            written = sorted(root.rglob("*"))

        self.assertEqual(code, 0)
        self.assertEqual(written, [])


if __name__ == "__main__":
    unittest.main()
