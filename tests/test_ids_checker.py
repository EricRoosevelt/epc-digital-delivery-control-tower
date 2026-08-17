"""The IDS checker: rule loading, identity hygiene, and finding fidelity.

Three separate claims are made here.

*Fidelity* — re-deriving the findings from the same IFC files and the same IDS
document reproduces, field for field, every finding the previous implementation
published. This is a characterization test: it pins the port, and refreshing it
is a deliberate act.

*Identity hygiene* — the rule set's semantic digest survives reformatting the
document it came from, while the provenance hash does not. Getting this
backwards is not hypothetical; the published v1.0.0 baseline hashes raw file
bytes, which is why the same commit produced different finding keys on Linux
than on Windows.

*Determinism* — two runs over unchanged inputs write byte-identical reports.
IfcTester collects passing elements in a ``set`` and stamps each report with
the wall clock, so this only holds because both are pinned.
"""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from epc_control_tower.checkers.ids_checker import (
    IdsChecker,
    load_ids_rule_source,
)
from epc_control_tower.determinism import read_csv_rows, sha256_file
from epc_control_tower.domain import FindingStatus, Severity
from epc_control_tower.identity import (
    build_requirement_key,
    build_validation_run_id,
)
from helpers import PROJECT_ROOT, shipped_pipeline_result, writable_test_directory

IDS_PATH = PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"
COMMITTED_FINDINGS = PROJECT_ROOT / "data" / "processed" / "ids_findings.csv"


class RuleSetLoadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load_ids_rule_source(IDS_PATH)
        cls.ruleset = cls.source.ruleset

    def test_every_specification_requirement_becomes_one_requirement(self):
        # Seven specifications, two of which carry two requirements each.
        self.assertEqual(len(self.ruleset.requirements), 9)
        self.assertEqual(
            len({r.requirement_key for r in self.ruleset.requirements}), 9
        )

    def test_rule_ids_come_from_the_xml_not_from_the_parsed_objects(self):
        # IfcTester 0.8.5 drops `identifier` when it re-reads a document, and
        # every published key is built on it.
        from ifctester import ids

        reparsed = ids.open(str(IDS_PATH))
        self.assertTrue(
            all(getattr(s, "identifier", None) is None for s in reparsed.specifications)
        )
        self.assertEqual(
            sorted({r.rule_id for r in self.ruleset.requirements}),
            ["R-001", "R-002", "R-003", "R-004A", "R-004B", "R-005A", "R-005B"],
        )

    def test_requirement_keys_match_the_published_ones(self):
        published = {
            (row["specification_id"], row["requirement_id"]): row["requirement_key"]
            for row in read_csv_rows(COMMITTED_FINDINGS)
        }
        self.assertEqual(len(published), 9)
        for (rule_id, requirement_id), key in published.items():
            with self.subTest(rule=rule_id, requirement=requirement_id):
                self.assertEqual(build_requirement_key(rule_id, requirement_id), key)
                self.assertEqual(
                    self.source.requirement_for(rule_id, requirement_id).requirement_key,
                    key,
                )

    def test_only_the_three_facet_kinds_this_document_uses_appear(self):
        kinds = sorted({k for r in self.ruleset.requirements for k in r.facet_kinds})
        self.assertEqual(kinds, ["attribute", "partof", "property"])
        for kind in kinds:
            self.assertIn(kind, IdsChecker.capabilities.facets)

    def test_severity_is_rule_metadata_not_a_property_of_the_outcome(self):
        for requirement in self.ruleset.requirements:
            expected = (
                Severity.WARNING
                if requirement.rule_id.startswith("R-005")
                else Severity.ERROR
            )
            with self.subTest(rule=requirement.rule_id):
                self.assertIs(requirement.severity, expected)

    def test_specification_labels_reproduce_the_published_wording(self):
        published = {
            row["specification_id"]: row["specification"]
            for row in read_csv_rows(COMMITTED_FINDINGS)
        }
        for requirement in self.ruleset.requirements:
            with self.subTest(rule=requirement.rule_id):
                self.assertEqual(
                    requirement.specification_label, published[requirement.rule_id]
                )


class RuleIdentityHygieneTests(unittest.TestCase):
    """The two digests answer two different questions, and must not be swapped."""

    @staticmethod
    def _reformatted(target_dir: Path) -> Path:
        """The same rules, written differently: CRLF and a blank line added."""

        original = IDS_PATH.read_bytes()
        rewritten = original.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        rewritten = rewritten.replace(
            b"<specifications>", b"\r\n<specifications>", 1
        )
        path = target_dir / "reformatted.ids"
        path.write_bytes(rewritten)
        return path

    def test_reformatting_the_document_leaves_the_rules_saying_the_same_thing(self):
        with writable_test_directory("ids-reformat") as scratch:
            other = self._reformatted(scratch)
            original = load_ids_rule_source(IDS_PATH).ruleset
            reformatted = load_ids_rule_source(other).ruleset

            self.assertNotEqual(
                original.source_blob_sha256, reformatted.source_blob_sha256
            )
            self.assertEqual(
                original.normalized_digest, reformatted.normalized_digest
            )

    def test_a_validation_identity_survives_reformatting_its_rule_document(self):
        with writable_test_directory("ids-reformat-run") as scratch:
            other = self._reformatted(scratch)
            models = (("architecture", "a" * 64),)
            checkers = ()

            def run_id_for(ruleset):
                return build_validation_run_id(
                    ruleset_id=ruleset.ruleset_id,
                    ruleset_version=ruleset.version,
                    ruleset_normalized_digest=ruleset.normalized_digest,
                    models=models,
                    checkers=checkers,
                    as_of="2026-08-13T00:00:00Z",
                )

            self.assertEqual(
                run_id_for(load_ids_rule_source(IDS_PATH).ruleset),
                run_id_for(load_ids_rule_source(other).ruleset),
            )

    def test_the_provenance_hash_is_the_file_and_says_so(self):
        ruleset = load_ids_rule_source(IDS_PATH).ruleset
        self.assertEqual(ruleset.source_blob_sha256, sha256_file(IDS_PATH))

    def test_the_checker_config_digest_is_not_the_rule_document(self):
        # The rules already reach the identity through the normalized digest.
        # Counting the document twice, under a second name, would only make the
        # identity harder to reason about.
        checker = IdsChecker(IDS_PATH)
        self.assertNotEqual(checker.config_sha256(), sha256_file(IDS_PATH))
        self.assertNotEqual(
            checker.config_sha256(), checker.load_ruleset().normalized_digest
        )
        self.assertRegex(checker.config_sha256(), r"^[0-9a-f]{64}$")

    def test_the_checker_declares_what_it_can_evaluate(self):
        self.assertEqual(IdsChecker.capabilities.ifc_schemas, ("IFC4",))
        self.assertFalse(IdsChecker.capabilities.requires_federated_context)


class FindingFidelityTests(unittest.TestCase):
    """Re-deriving the findings reproduces every published one."""

    @classmethod
    def setUpClass(cls):
        cls.result = shipped_pipeline_result()
        cls.findings = cls.result.bundle.findings
        cls.published = read_csv_rows(COMMITTED_FINDINGS)

    def test_the_published_counts_are_reproduced(self):
        self.assertEqual(len(self.findings), 47)
        counts = {
            status: sum(1 for f in self.findings if f.status is status)
            for status in FindingStatus
        }
        self.assertEqual(counts[FindingStatus.PASS], 25)
        self.assertEqual(counts[FindingStatus.FAIL], 6)
        self.assertEqual(counts[FindingStatus.NOT_APPLICABLE], 16)
        self.assertEqual(sum(1 for f in self.findings if f.is_applicable), 31)

    def test_every_finding_matches_the_published_row_field_for_field(self):
        published = {
            (row["model_id"], row["requirement_key"], row["element_key"]): row
            for row in self.published
        }
        derived = {
            (f.model_key, f.requirement_key, f.element_key): f for f in self.findings
        }
        self.assertEqual(set(published), set(derived))

        for key, row in published.items():
            finding = derived[key]
            with self.subTest(finding=key):
                self.assertEqual(str(finding.status), row["status"])
                self.assertEqual(str(finding.severity), row["severity"])
                self.assertEqual(finding.expected, row["expected"])
                self.assertEqual(finding.actual, row["actual"])
                self.assertEqual(finding.reason, row["reason"])
                self.assertEqual(
                    "true" if finding.is_applicable else "false", row["is_applicable"]
                )
                self.assertEqual(
                    "true" if finding.is_issue else "false", row["is_issue"]
                )

    def test_the_actual_column_stays_empty_because_nothing_reports_it(self):
        # IfcTester does not stably report the value it observed. An invented
        # one would be worse than none.
        self.assertEqual({f.actual for f in self.findings}, {""})

    def test_zero_applicable_specifications_are_not_counted_as_compliance(self):
        # Sixteen of the forty-seven. Reported as passing by IfcTester; treating
        # them that way is what would inflate the published pass rate.
        not_applicable = [
            f for f in self.findings if f.status is FindingStatus.NOT_APPLICABLE
        ]
        self.assertEqual(len(not_applicable), 16)
        for finding in not_applicable:
            with self.subTest(finding=finding.finding_key):
                self.assertEqual(finding.element_key, "")
                self.assertFalse(finding.is_applicable)
                self.assertIs(finding.severity, Severity.INFO)

    def test_only_the_project_assumed_rules_fail_and_they_fail_as_warnings(self):
        failures = [f for f in self.findings if f.status is FindingStatus.FAIL]
        self.assertEqual(len(failures), 6)
        for finding in failures:
            requirement = self.result.ruleset.by_key(finding.requirement_key)
            with self.subTest(finding=finding.finding_key):
                self.assertTrue(requirement.rule_id.startswith("R-005"))
                self.assertIs(finding.severity, Severity.WARNING)

    def test_the_run_identity_is_not_the_published_one_and_the_reason_is_recorded(self):
        # Splitting run identity three ways changed what a validation is: the
        # new id folds in each checker's version and configuration. The old
        # value survives only inside the legacy adapter.
        run = self.result.bundle.run
        self.assertNotEqual(run.validation_run_id, "ids-v0.1-8706ef58303bfd11")
        self.assertEqual(
            [f.component_id for f in run.checker_fingerprints], ["ids"]
        )
        self.assertEqual(run.ruleset_source_blob_sha256, sha256_file(IDS_PATH))


class ReportDeterminismTests(unittest.TestCase):
    """Reports are an output of the inputs, not of when somebody ran them."""

    def test_two_runs_write_byte_identical_reports(self):
        from epc_control_tower.pipeline import build_bundle
        from helpers import shipped_run_config

        digests = []
        for attempt in range(2):
            with writable_test_directory(f"ids-reports-{attempt}") as scratch:
                build_bundle(shipped_run_config(), reports_dir=scratch)
                digests.append(
                    {
                        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in sorted((scratch / "ids").iterdir())
                    }
                )

        self.assertEqual(sorted(digests[0]), sorted(digests[1]))
        self.assertEqual(len(digests[0]), 6)
        self.assertEqual(digests[0], digests[1])

    def test_the_report_carries_the_logical_date_not_the_wall_clock(self):
        import json

        from helpers import shipped_reports_dir, shipped_run_config

        shipped_pipeline_result()
        report = json.loads(
            (shipped_reports_dir() / "ids" / "architecture.json").read_text("utf-8")
        )
        self.assertTrue(shipped_run_config().as_of.startswith("2026-08-13"))
        self.assertEqual(report["date"], "2026-08-13 00:00:00")


if __name__ == "__main__":
    unittest.main()
