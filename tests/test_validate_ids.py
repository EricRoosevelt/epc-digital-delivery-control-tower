import csv
import unittest
from collections import Counter
from pathlib import Path

from src.identity import (
    build_finding_key,
    build_requirement_key,
)
from src.validate_ids import (
    FINDING_COLUMNS,
    get_requirement_id,
    normalize_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class NormalizeReportTests(unittest.TestCase):
    def test_fail_finding_contains_stable_identity_and_flags(self):
        report = {
            "specifications": [
                {
                    "name": (
                        "Duct segments need assumed EPC metadata"
                    ),
                    "total_applicable": 1,
                    "is_skipped": False,
                    "status": False,
                    "requirements": [
                        {
                            "label": "EPC_Delivery.AssetTag",
                            "description": (
                                "AssetTag data shall be provided"
                            ),
                            "total_applicable": 1,
                            "passed_entities": [],
                            "failed_entities": [
                                {
                                    "global_id": "ifc-guid",
                                    "class": "IfcDuctSegment",
                                    "name": "Duct 1",
                                    "reason": "Missing property",
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        findings = normalize_report(
            report_data=report,
            model_id="hvac",
            run_id="ids-v0.1-test",
            ids_version="0.1",
            specification_ids={
                "Duct segments need assumed EPC metadata": (
                    "R-005A"
                )
            },
            element_lookup={
                ("hvac", "ifc-guid"): "hvac::ifc-guid"
            },
        )

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        expected_requirement_key = build_requirement_key(
            "R-005A",
            "EPC_Delivery.AssetTag",
        )
        self.assertEqual(finding["specification_id"], "R-005A")
        self.assertEqual(
            finding["requirement_id"],
            "EPC_Delivery.AssetTag",
        )
        self.assertEqual(
            finding["requirement_key"],
            expected_requirement_key,
        )
        self.assertEqual(
            finding["finding_key"],
            build_finding_key(
                "ids-v0.1-test",
                "hvac",
                expected_requirement_key,
                "hvac::ifc-guid",
            ),
        )
        self.assertEqual(finding["is_applicable"], "true")
        self.assertEqual(finding["is_issue"], "true")

    def test_na_finding_has_empty_element_identity_and_false_flags(self):
        report = {
            "specifications": [
                {
                    "name": "Beams must declare LoadBearing",
                    "total_applicable": 0,
                    "is_skipped": True,
                    "status": True,
                    "requirements": [
                        {
                            "label": (
                                "Pset_BeamCommon.LoadBearing"
                            ),
                            "description": (
                                "LoadBearing data shall be provided"
                            ),
                        }
                    ],
                }
            ]
        }

        finding = normalize_report(
            report_data=report,
            model_id="architecture",
            run_id="ids-v0.1-test",
            ids_version="0.1",
            specification_ids={
                "Beams must declare LoadBearing": "R-003"
            },
            element_lookup={},
        )[0]

        self.assertEqual(finding["status"], "N/A")
        self.assertEqual(finding["element_key"], "")
        self.assertEqual(finding["global_id"], "")
        self.assertEqual(finding["is_applicable"], "false")
        self.assertEqual(finding["is_issue"], "false")

    def test_missing_or_duplicate_requirement_label_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "no canonical label",
        ):
            get_requirement_id({"description": "Only a description"})

        report = {
            "specifications": [
                {
                    "name": "Duplicate labels",
                    "total_applicable": 0,
                    "is_skipped": True,
                    "status": True,
                    "requirements": [
                        {"label": "Name"},
                        {"label": "Name"},
                    ],
                }
            ]
        }

        with self.assertRaisesRegex(
            ValueError,
            "Duplicate requirement label",
        ):
            normalize_report(
                report_data=report,
                model_id="architecture",
                run_id="ids-v0.1-test",
                ids_version="0.1",
                specification_ids={"Duplicate labels": "R-TEST"},
                element_lookup={},
            )


class CurrentFindingsContractTests(unittest.TestCase):
    def test_checked_in_findings_match_current_baseline(self):
        path = PROJECT_ROOT / "data" / "processed" / "ids_findings.csv"

        with path.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            fieldnames = reader.fieldnames

        self.assertEqual(fieldnames, FINDING_COLUMNS)
        self.assertEqual(len(rows), 47)
        self.assertEqual(
            Counter(row["status"] for row in rows),
            {"PASS": 25, "FAIL": 6, "N/A": 16},
        )
        self.assertEqual(
            sum(row["is_applicable"] == "true" for row in rows),
            31,
        )
        self.assertEqual(
            sum(row["is_issue"] == "true" for row in rows),
            6,
        )
        self.assertEqual(
            len({row["requirement_key"] for row in rows}),
            9,
        )
        self.assertEqual(
            len({row["finding_key"] for row in rows}),
            47,
        )

        for row in rows:
            requirement_key = build_requirement_key(
                row["specification_id"],
                row["requirement_id"],
            )
            self.assertEqual(
                row["requirement_key"],
                requirement_key,
            )
            self.assertEqual(
                row["finding_key"],
                build_finding_key(
                    row["run_id"],
                    row["model_id"],
                    requirement_key,
                    row["element_key"],
                ),
            )


if __name__ == "__main__":
    unittest.main()
