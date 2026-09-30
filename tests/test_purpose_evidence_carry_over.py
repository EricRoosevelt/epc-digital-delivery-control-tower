"""Evidence carry-over across a recheck (ADR 0005 §5.2-§5.4, §5.8).

A successor record has to say, for every finding the sealed record cited,
whether the finding it cites now is **the same evidence** — perhaps under a new
key — or **different evidence**, or **none**, or whether that **cannot be
shown**. Before contract 1.7 it could only ask whether the old key was still in
the facts; after 1.7 re-keyed every finding, that question would have reported
every old citation absent, and before 1.7 it would have reported a relaxed rule
as carried evidence.

This module starts where the answer has to start: with what the sealed record
wrote down at the time.
"""

from __future__ import annotations

import dataclasses
import unittest

import assessment_fixtures as fx
from epc_control_tower.purpose import assess_purpose
from epc_control_tower.purpose.assessment.facts import finding_content_digest
from epc_control_tower.purpose.assessment.record import (
    CITED_FINDING_BASIS_VERSION,
    build_assessment_digest,
)
from helpers import shipped_pipeline_result

ALL_ACTIVITIES = (
    "schedules-and-room-data-sheets",
    "ceiling-and-bulkhead-geometry",
    "builders-work-openings",
)


def first_record(facts, *, composed=None):
    """The fixture's originating record over ``facts``, all three activities."""

    return assess_purpose(
        request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=facts),
        composed=composed if composed is not None else fx.fixture_composed(),
        facts=facts,
        determinations=fx.fixture_determinations(facts=facts),
    )


def finding_readings(record):
    for activity in record.activities:
        for subscope in activity.subscopes:
            for step in subscope.path:
                for reading in step.readings:
                    if reading.finding_keys:
                        yield reading


class SealedBasisTests(unittest.TestCase):
    """§5.2.2: each cited finding is sealed with the basis a later record needs."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle
        cls.facts = fx.assessment_facts()
        cls.record = first_record(cls.facts)
        cls.readings = tuple(finding_readings(cls.record))

    def test_every_cited_finding_has_a_basis_one_for_one(self):
        self.assertTrue(self.readings)
        cited = 0
        for reading in self.readings:
            with self.subTest(subject=reading.subject.keys):
                self.assertEqual(
                    tuple(item.finding_key for item in reading.cited_findings),
                    reading.finding_keys,
                )
                cited += len(reading.finding_keys)
        # Nine distinct findings, cited from more than one reading.
        self.assertEqual(
            len({key for reading in self.readings for key in reading.finding_keys}), 9
        )
        self.assertGreaterEqual(cited, 9)

    def test_the_basis_is_what_the_cited_run_says(self):
        findings = {finding.finding_key: finding for finding in self.bundle.findings}
        requirements = {r.requirement_key: r for r in self.bundle.ruleset.requirements}
        checkers = {f.component_id: f for f in self.bundle.run.checker_fingerprints}
        models = {m.model_key: m.provenance.content_sha256 for m in self.bundle.models}
        for reading in self.readings:
            for basis in reading.cited_findings:
                with self.subTest(finding=basis.finding_key):
                    finding = findings[basis.finding_key]
                    requirement = requirements[finding.requirement_key]
                    checker = checkers[requirement.checker]
                    self.assertEqual(basis.basis_version, CITED_FINDING_BASIS_VERSION)
                    self.assertEqual(basis.element_key, finding.element_key)
                    self.assertEqual(basis.requirement_key, finding.requirement_key)
                    self.assertEqual(basis.model_key, finding.model_key)
                    self.assertEqual(basis.model_content_id, models[finding.model_key])
                    self.assertEqual(basis.semantics_digest, requirement.semantics_digest)
                    self.assertRegex(basis.semantics_digest, r"^[0-9a-f]{64}$")
                    self.assertEqual(basis.content_digest, finding_content_digest(finding))
                    self.assertEqual(
                        (
                            basis.checker_id,
                            basis.checker_version,
                            basis.checker_config_sha256,
                        ),
                        (checker.component_id, checker.version, checker.config_sha256),
                    )

    def test_the_basis_is_sealed_with_the_record(self):
        document = self.record.as_document()
        self.assertEqual(build_assessment_digest(document), self.record.assessment_digest)
        reading = next(
            reading
            for activity in document["activities"]
            for subscope in activity["subscopes"]
            for step in subscope["path"]
            for reading in step["readings"]
            if "cited_findings" in reading
        )
        self.assertEqual(
            [item["finding_key"] for item in reading["cited_findings"]],
            reading["finding_keys"],
        )
        reading["cited_findings"][0]["semantics_digest"] = "0" * 64
        self.assertNotEqual(
            build_assessment_digest(document), self.record.assessment_digest
        )

    def test_the_content_digest_sees_status_and_text_and_nothing_else(self):
        finding = self.bundle.findings[0]
        digest = finding_content_digest(finding)
        self.assertEqual(
            finding_content_digest(dataclasses.replace(finding, finding_key="other")),
            digest,
        )
        for field in ("expected", "actual", "reason"):
            with self.subTest(field=field):
                self.assertNotEqual(
                    finding_content_digest(
                        dataclasses.replace(finding, **{field: "something else"})
                    ),
                    digest,
                )

    def test_a_basis_that_does_not_match_its_keys_is_refused(self):
        reading = self.readings[0]
        with self.assertRaises(ValueError):
            dataclasses.replace(reading, cited_findings=tuple(reversed(
                reading.cited_findings
            )) + reading.cited_findings[:1])


if __name__ == "__main__":
    unittest.main()
