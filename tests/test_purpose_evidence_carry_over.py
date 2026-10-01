"""Evidence carry-over across a recheck (ADR 0005 §5.2-§5.4, §5.8).

A successor record has to say, for every finding the sealed record cited,
whether the finding it cites now is **the same evidence** — perhaps under a new
key — or **different evidence**, or **none**, or whether that **cannot be
shown**. Before contract 1.7 it could only ask whether the old key was still in
the facts; after 1.7 re-keyed every finding, that question would have reported
every old citation absent, and before 1.7 it would have reported a relaxed rule
as carried evidence.

This module starts where the answer has to start — with what the sealed record
wrote down at the time — and then pins the PM's four counterexamples (K1-K4d),
the re-issue case, the checker case, and determinism. Every rule edit is made to
a scratch copy of the rules (``rule_edits``), never to ``rules/``.
"""

from __future__ import annotations

import builtins
import dataclasses
import functools
import io
import pathlib
import unittest
from contextlib import ExitStack, contextmanager
from unittest import mock

import assessment_fixtures as fx
from epc_control_tower.checkers.ids_checker import IdsChecker
from epc_control_tower.purpose import assess_purpose, facts_from_bundle, recheck_purpose
from epc_control_tower.purpose.assessment.facts import finding_content_digest
from epc_control_tower.purpose.assessment.record import (
    CARRY_OVER_REASON_STATES,
    CARRY_OVER_REASONS,
    CARRY_OVER_STATES,
    CHANGED_ASPECTS,
    CITED_FINDING_BASIS_VERSION,
    build_assessment_digest,
)
from helpers import PROJECT_ROOT, shipped_pipeline_result, shipped_run_config
from rule_edits import edited_run

ALL_ACTIVITIES = (
    "schedules-and-room-data-sheets",
    "ceiling-and-bulkhead-geometry",
    "builders-work-openings",
)
PROJECT = "pcert-sample"


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


# ---------------------------------------------------------------------------
# Scenario building blocks
# ---------------------------------------------------------------------------


def facts_after(*edits: str):
    """The facts of a fresh run over a scratch copy of the rules, edited."""

    return facts_from_bundle(edited_run(*edits).bundle, PROJECT)


@functools.cache
def checker_version_moved_facts():
    """The facts of a fresh run in which the IDS checker reports another version.

    Nothing else differs — the same rules, the same models — so any row that
    moves, moves because the checker fingerprint did. The run writes to a
    scratch directory, never to the published tree.
    """

    import atexit
    import shutil
    import uuid

    from epc_control_tower.pipeline import build_bundle

    scratch = PROJECT_ROOT / "tests" / f".checker-version-{uuid.uuid4().hex}"
    atexit.register(shutil.rmtree, scratch, True)
    config = dataclasses.replace(
        shipped_run_config(),
        processed_data_dir=scratch / "processed",
        reports_dir=scratch / "reports",
    )
    with mock.patch.object(IdsChecker, "version", "1.0.0+checker-version-test"):
        bundle = build_bundle(config, reports_dir=scratch / "reports").bundle
    return facts_from_bundle(bundle, PROJECT)


def recheck_all(prior, facts, *, determinations=None):
    """Recheck every sealed subscope of ``prior`` against ``facts``."""

    return recheck_purpose(
        prior=prior,
        request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=facts),
        composed=fx.fixture_composed(),
        facts=facts,
        determinations=(
            fx.fixture_determinations(facts=facts)
            if determinations is None
            else determinations
        ),
        succeeds=tuple(
            (activity.activity_ref, subscope.ordinal)
            for activity in prior.activities
            for subscope in activity.subscopes
        ),
    )


def rows(record, kind: str):
    return [
        row
        for outcome in record.successor.outcomes
        for row in outcome.carry_over
        if row.citation_kind == kind
    ]


def states(record, kind: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows(record, kind):
        counts[row.state] = counts.get(row.state, 0) + 1
    return counts


resealed = fx.resealed_record


def reissued(facts, *, delete: str = ""):
    """``facts`` with the HVAC model reissued: a new content id and new keys.

    Every finding reads exactly what it read before — the same element,
    requirement, status and text — which is the case ADR 0005 §5.4 decides:
    identical evidence about a *different* model version. ``delete`` removes one
    element and its findings as well. Every minted value carries the fixture
    marker.
    """

    models = tuple(
        dataclasses.replace(model, content_id=fx.reissued_content_id("hvac"))
        if model.model_key == "hvac"
        else model
        for model in facts.models
    )
    findings = tuple(
        dataclasses.replace(
            finding, finding_key=f"{fx.FIXTURE_MARKER}/reissued/{finding.finding_key}"
        )
        if finding.model_key == "hvac"
        else finding
        for finding in facts.findings
        if finding.element_key != delete
    )
    return dataclasses.replace(
        facts,
        validation_run_id=fx.REISSUED_VALIDATION_RUN_ID,
        models=models,
        findings=findings,
        elements=tuple(item for item in facts.elements if item.element_key != delete),
    )


def with_findings(facts, predicate, **changes):
    """``facts`` with ``changes`` applied to every finding ``predicate`` picks."""

    return dataclasses.replace(
        facts,
        findings=tuple(
            dataclasses.replace(finding, **changes) if predicate(finding) else finding
            for finding in facts.findings
        ),
    )


@contextmanager
def rules_unreadable():
    """Make every rule file, and every way of loading one, fail.

    A recheck compares a sealed record with current facts and nothing else. If
    it read a rule file to fill in what an old record lacks, it would be
    rebuilding history from today's rules; under this context it cannot.
    """

    rules_dirs = (PROJECT_ROOT / "rules", PROJECT_ROOT / "tests")

    def blocked(path) -> bool:
        try:
            resolved = pathlib.Path(path).resolve()
        except (TypeError, OSError):
            return False
        return resolved.suffix == ".toml" and any(
            resolved.is_relative_to(root) for root in rules_dirs
        )

    def guard(original):
        def wrapper(target, *args, **kwargs):
            if blocked(target):
                raise PermissionError(f"rule file read during a recheck: {target}")
            return original(target, *args, **kwargs)

        return wrapper

    def refuse(*_args, **_kwargs):
        raise PermissionError("rule loading during a recheck")

    with ExitStack() as stack:
        stack.enter_context(mock.patch.object(builtins, "open", guard(builtins.open)))
        stack.enter_context(mock.patch.object(io, "open", guard(io.open)))
        for name in ("open", "read_text", "read_bytes"):
            stack.enter_context(
                mock.patch.object(
                    pathlib.Path, name, guard(getattr(pathlib.Path, name))
                )
            )
        for target in (
            "epc_control_tower.rule_definitions.load_rule_definitions",
            "epc_control_tower.rules.load_ruleset",
            "epc_control_tower.coverage.rule_definitions_digest",
        ):
            stack.enter_context(mock.patch(target, refuse))
        yield


class CarryOverTestCase(unittest.TestCase):
    """The shipped run's first record, and a way to name its cited findings."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = shipped_pipeline_result().bundle
        cls.facts = fx.assessment_facts()
        cls.prior = first_record(cls.facts)
        labels = {
            r.requirement_key: f"{r.rule_id}/{r.requirement_id}"
            for r in cls.bundle.ruleset.requirements
        }
        cls.sealed = {
            finding.finding_key: (finding.element_key, labels[finding.requirement_key])
            for finding in cls.facts.findings
        }

    def split(self, record, element: str, label_prefix: str):
        """Finding rows about ``element`` whose requirement label starts with
        ``label_prefix`` (``"R-005A/"``, say), and all the others."""

        mine, others = [], []
        for row in rows(record, "finding"):
            where, label = self.sealed[row.citation]
            target = mine if where == element and label.startswith(label_prefix) else others
            target.append(row)
        return mine, others

    def assert_closed_vocabulary(self, record):
        for outcome in record.successor.outcomes:
            for row in outcome.carry_over:
                document = row.as_document()
                with self.subTest(citation=row.citation):
                    self.assertNotIn("carried", document)
                    self.assertIn(row.state, CARRY_OVER_STATES)
                    self.assertEqual(CARRY_OVER_REASON_STATES[row.reason], row.state)
                    self.assertTrue(set(row.changed_aspects) <= set(CHANGED_ASPECTS))


class VocabularyTests(unittest.TestCase):
    def test_four_states_and_no_word_for_fixed(self):
        # PM, K1: a relaxed rule must not read as a repaired model. The record
        # has no value that says either — only what differed.
        self.assertEqual(
            CARRY_OVER_STATES, ("equivalent", "changed", "no-counterpart", "not-provable")
        )
        for value in CARRY_OVER_STATES + CARRY_OVER_REASONS + CHANGED_ASPECTS:
            with self.subTest(value=value):
                for word in ("fix", "repair", "resolv", "carried", "clear"):
                    self.assertNotIn(word, value)

    def test_every_reason_belongs_to_exactly_one_state(self):
        self.assertEqual(set(CARRY_OVER_REASON_STATES.values()), set(CARRY_OVER_STATES))
        self.assertNotIn("finding-absent-from-the-cited-run", CARRY_OVER_REASONS)
        self.assertNotIn("carried", CARRY_OVER_REASONS)


class K1RelaxedRequirementTests(CarryOverTestCase):
    """K1: R-005A ``required`` → ``optional``; no model changed."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.after = facts_after("r005a-optional")
        cls.record = recheck_all(cls.prior, cls.after)

    def test_the_context_did_not_move(self):
        self.assertTrue(self.record.successor.context.is_current)

    def test_the_duct_blocker_lifted_and_the_evidence_is_not_called_the_same(self):
        schedules = next(
            outcome
            for outcome in self.record.successor.outcomes
            if outcome.activity_ref.endswith("schedules-and-room-data-sheets")
            and outcome.prior_verdict == "BLOCKED"
        )
        duct = next(
            item
            for item in schedules.dispositions
            if item.member.keys == (fx.HVAC_DUCT,)
        )
        # The situation K1 is about: the verdict advanced with no model change.
        self.assertEqual(duct.current_verdicts, ("READY",))
        mine, _ = self.split(self.record, fx.HVAC_DUCT, "R-005A/")
        self.assertEqual(len(mine), 2)
        for row in mine:
            with self.subTest(citation=row.citation):
                self.assertEqual(row.state, "changed")
                self.assertNotEqual(row.state, "equivalent")
                self.assertIn("requirement-semantics", row.changed_aspects)
                self.assertEqual(
                    row.changed_aspects, ("finding-content", "requirement-semantics")
                )
                self.assertEqual(row.key_changed, "yes")

    def test_everything_the_edit_did_not_touch_is_equivalent_under_new_keys(self):
        _, others = self.split(self.record, fx.HVAC_DUCT, "R-005A/")
        self.assertEqual(len(others), 7)
        for row in others:
            with self.subTest(citation=row.citation):
                self.assertEqual((row.state, row.key_changed), ("equivalent", "yes"))
        self.assertEqual(states(self.record, "determination"), {"equivalent": 6})

    def test_every_row_speaks_the_closed_vocabulary(self):
        self.assert_closed_vocabulary(self.record)


class K2PredicateChangedOutcomeNotTests(CarryOverTestCase):
    """K2: R-005A ``dataType`` → ``IFCTEXT``; every finding byte is the same."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.after = facts_after("r005a-datatype")
        cls.record = recheck_all(cls.prior, cls.after)

    def test_only_the_semantics_differ_and_that_is_enough(self):
        mine, others = self.split(self.record, fx.HVAC_DUCT, "R-005A/")
        self.assertEqual(len(mine), 2)
        for row in mine:
            with self.subTest(citation=row.citation):
                self.assertEqual(row.state, "changed")
                self.assertEqual(row.changed_aspects, ("requirement-semantics",))
        self.assertEqual({row.state for row in others}, {"equivalent"})

    def test_the_outcomes_and_verdicts_did_not_move(self):
        def verdicts(record):
            return sorted(
                (activity.activity_ref, s.ordinal, s.verdict, s.resolution_kind)
                for activity in record.activities
                for s in activity.subscopes
            )

        self.assertEqual(verdicts(self.record), verdicts(self.prior))
        before = {(f.element_key, f.requirement_key): f.status for f in self.facts.findings}
        after = {(f.element_key, f.requirement_key): f.status for f in self.after.findings}
        self.assertEqual(before, after)


class K3UnrelatedRuleTests(CarryOverTestCase):
    """K3: R-002 ``dataType`` changes; nothing the record cites is about R-002."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.after = facts_after("r002-datatype")
        cls.record = recheck_all(cls.prior, cls.after)

    def test_every_cited_finding_is_equivalent_under_a_new_key(self):
        findings = rows(self.record, "finding")
        self.assertEqual(len(findings), 9)
        for row in findings:
            with self.subTest(citation=row.citation):
                self.assertEqual((row.state, row.reason), ("equivalent", "finding-equivalent"))
                self.assertEqual(row.key_changed, "yes")
                self.assertNotEqual(row.current_citation, row.citation)
                self.assertEqual(row.changed_aspects, ())

    def test_nothing_is_reported_missing(self):
        self.assertNotIn("no-counterpart", states(self.record, "finding"))
        self.assertEqual(states(self.record, "determination"), {"equivalent": 6})
        self.assert_closed_vocabulary(self.record)


class K4aRecordWithoutABasisTests(CarryOverTestCase):
    """K4a: a record sealed before 1.7 — ``finding_keys`` and no basis."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.old = resealed(
            cls.prior, lambda reading: dataclasses.replace(reading, cited_findings=())
        )
        cls.after = facts_after("r002-datatype")
        cls.record = recheck_all(cls.old, cls.after)

    def test_the_old_record_really_has_no_basis_and_is_still_sealed(self):
        self.assertNotIn('"cited_findings"', repr(self.old.as_document()))
        self.assertEqual(
            build_assessment_digest(self.old.as_document()), self.old.assessment_digest
        )

    def test_every_finding_citation_is_not_provable_and_none_is_missing(self):
        findings = rows(self.record, "finding")
        self.assertEqual(len(findings), 9)
        for row in findings:
            with self.subTest(citation=row.citation):
                self.assertEqual(
                    (row.state, row.reason),
                    ("not-provable", "sealed-citation-has-no-comparison-basis"),
                )
        self.assertNotIn("no-counterpart", states(self.record, "finding"))

    def test_a_key_that_is_still_present_proves_nothing_without_a_basis(self):
        # Against the shipped facts every old key is still there. Before 1.7 that
        # was read as "carried"; a key derived without the rule's semantics does
        # not show the rule is the same, so it stays not provable.
        record = recheck_all(self.old, self.facts)
        present = {fact.finding_key for fact in self.facts.findings}
        for row in rows(record, "finding"):
            with self.subTest(citation=row.citation):
                self.assertIn(row.citation, present)
                self.assertEqual(row.state, "not-provable")

    def test_the_rules_are_not_read_to_rebuild_what_the_record_lacks(self):
        with rules_unreadable():
            blind = recheck_all(self.old, self.after)
        self.assertEqual(blind.as_document(), self.record.as_document())
        self.assertEqual(blind.assessment_digest, self.record.assessment_digest)

    def test_a_recheck_with_a_basis_does_not_read_them_either(self):
        with rules_unreadable():
            blind = recheck_all(self.prior, self.after)
        self.assertEqual(
            blind.as_document(), recheck_all(self.prior, self.after).as_document()
        )


class ReissueTests(CarryOverTestCase):
    """ADR 0005 §5.4: identical readings of a re-issued model are ``changed``."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.after = reissued(cls.facts)
        cls.record = recheck_all(cls.prior, cls.after, determinations=())

    def test_every_finding_is_changed_by_model_version_alone(self):
        findings = rows(self.record, "finding")
        self.assertEqual(len(findings), 9)
        for row in findings:
            with self.subTest(citation=row.citation):
                self.assertEqual(row.state, "changed")
                self.assertEqual(row.changed_aspects, ("model-version",))
                self.assertEqual(row.key_changed, "yes")

    def test_no_determination_is_attributable_to_the_new_context(self):
        self.assertFalse(self.record.successor.context.is_current)
        self.assertEqual(
            {row.reason for row in rows(self.record, "determination")},
            {"determination-not-attributable-to-this-context"},
        )
        self.assertEqual(states(self.record, "determination"), {"no-counterpart": 6})


class K4bMemberGoneTests(CarryOverTestCase):
    """K4b: re-issued, and the duct deleted."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.after = reissued(cls.facts, delete=fx.HVAC_DUCT)
        cls.record = recheck_all(cls.prior, cls.after, determinations=())

    def test_the_ducts_citations_are_not_provable_with_the_disposition_as_cause(self):
        mine, _ = self.split(self.record, fx.HVAC_DUCT, "R-00")
        self.assertEqual(len(mine), 3)
        for row in mine:
            with self.subTest(citation=row.citation):
                self.assertEqual(
                    (row.state, row.reason), ("not-provable", "subject-not-present")
                )
                self.assertEqual(row.cause, "element-deleted-in-reissued-model")
                self.assertEqual(row.current_citation, "")

    def test_the_rest_changed_by_model_version(self):
        _, others = self.split(self.record, fx.HVAC_DUCT, "R-00")
        self.assertEqual(len(others), 6)
        for row in others:
            with self.subTest(citation=row.citation):
                self.assertEqual(
                    (row.state, row.changed_aspects), ("changed", ("model-version",))
                )


class K4cAmbiguousCounterpartTests(CarryOverTestCase):
    """K4c: two current findings at one sealed coordinate."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        key = next(
            r.requirement_key
            for r in cls.bundle.ruleset.requirements
            if r.rule_id == "R-005A" and r.requirement_id.endswith("AssetTag")
        )
        cls.original = next(
            f
            for f in cls.facts.findings
            if f.element_key == fx.HVAC_DUCT and f.requirement_key == key
        )
        cls.twin = dataclasses.replace(
            cls.original,
            finding_key=f"{fx.FIXTURE_MARKER}/twin/{cls.original.finding_key}",
        )
        cls.after = dataclasses.replace(
            cls.facts,
            findings=tuple(
                sorted(
                    cls.facts.findings + (cls.twin,),
                    key=lambda f: (f.element_key, f.requirement_key, f.finding_key),
                )
            ),
        )
        cls.record = recheck_all(cls.prior, cls.after)

    def test_neither_candidate_is_chosen(self):
        key = self.original.finding_key
        (row,) = [r for r in rows(self.record, "finding") if r.citation == key]
        self.assertEqual((row.state, row.reason), ("not-provable", "counterpart-not-unique"))
        self.assertEqual(
            row.cause,
            ",".join(sorted([self.original.finding_key, self.twin.finding_key])),
        )
        self.assertEqual(row.current_citation, "")

    def test_the_other_eight_are_equivalent_under_the_same_keys(self):
        key = self.original.finding_key
        others = [r for r in rows(self.record, "finding") if r.citation != key]
        self.assertEqual(len(others), 8)
        for row in others:
            with self.subTest(citation=row.citation):
                self.assertEqual((row.state, row.key_changed), ("equivalent", "no"))


class K4dBasisUnavailableTests(CarryOverTestCase):
    """K4d: a basis that exists but cannot be compared."""

    def duct_r005a(self, finding) -> bool:
        where, label = self.sealed[finding.finding_key]
        return where == fx.HVAC_DUCT and label.startswith("R-005A/")

    def duct_rows(self, record):
        mine, others = self.split(record, fx.HVAC_DUCT, "R-005A/")
        self.assertEqual(len(mine), 2)
        return mine, others

    def test_an_empty_semantics_digest_now_is_not_provable(self):
        after = with_findings(self.facts, self.duct_r005a, semantics_digest="")
        mine, others = self.duct_rows(recheck_all(self.prior, after))
        for row in mine:
            with self.subTest(citation=row.citation):
                self.assertEqual(
                    (row.state, row.reason),
                    ("not-provable", "requirement-semantics-basis-unavailable"),
                )
                self.assertEqual(row.current_citation, row.citation)
        self.assertEqual({row.state for row in others}, {"equivalent"})

    def test_an_empty_semantics_digest_when_sealed_is_not_provable(self):
        blank = with_findings(self.facts, self.duct_r005a, semantics_digest="")
        prior = first_record(blank)
        mine, _ = self.duct_rows(recheck_all(prior, self.facts))
        self.assertEqual(
            {(row.state, row.reason) for row in mine},
            {("not-provable", "requirement-semantics-basis-unavailable")},
        )

    def test_an_unknown_basis_version_is_not_provable(self):
        def version(reading):
            return dataclasses.replace(
                reading,
                cited_findings=tuple(
                    dataclasses.replace(item, basis_version=2)
                    for item in reading.cited_findings
                ),
            )

        record = recheck_all(resealed(self.prior, version), self.facts)
        findings = rows(record, "finding")
        self.assertEqual(len(findings), 9)
        for row in findings:
            with self.subTest(citation=row.citation):
                self.assertEqual(
                    (row.state, row.reason),
                    ("not-provable", "comparison-basis-version-unknown"),
                )

    def test_a_missing_checker_fingerprint_is_never_read_as_the_same_checker(self):
        after = with_findings(self.facts, self.duct_r005a, checker=None)
        mine, _ = self.duct_rows(recheck_all(self.prior, after))
        self.assertEqual(
            {(row.state, row.reason) for row in mine},
            {("not-provable", "comparison-basis-incomplete")},
        )


class CheckerAspectTests(CarryOverTestCase):
    """A checker that reports another version, with nothing else changed."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.after = checker_version_moved_facts()
        cls.record = recheck_all(cls.prior, cls.after)

    def test_every_ids_finding_is_changed_by_the_checker_alone(self):
        findings = rows(self.record, "finding")
        self.assertEqual(len(findings), 9)
        for row in findings:
            with self.subTest(citation=row.citation):
                self.assertEqual(
                    (row.state, row.changed_aspects), ("changed", ("checker",))
                )
                # The version is in the validation identity, so keys moved too.
                self.assertEqual(row.key_changed, "yes")


class DeterminismTests(CarryOverTestCase):
    def test_the_same_recheck_twice_is_the_same_record(self):
        after = facts_after("r005a-optional")
        first = recheck_all(self.prior, after)
        second = recheck_all(first_record(fx.assessment_facts()), after)
        self.assertEqual(first.as_document(), second.as_document())
        self.assertEqual(first.assessment_digest, second.assessment_digest)


if __name__ == "__main__":
    unittest.main()
