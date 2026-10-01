"""The adapter says what a cited finding required, from the run that record cites.

One claim: the envelope's ``finding_details`` lets a screen say, for a finding a
record cites, what was required, what was found and why it failed — and what it
says is the requirement *that assessment was made against*, copied from the
validation run the citing record names, never read back from a rule file.

Three kinds of assertion, kept apart:

* **Verbatim.** Every entry is compared with the published canonical tables and
  with the test suite's own run of the shipped rules, field by field. The adapter
  reads neither; it reads the run its own records were assessed against.
* **Pinned.** Which citations of which scenario carry an entry, and which do not,
  is a table below — measured, then written down (``AGENTS.md`` rule 6).
* **Refused.** The guards are exercised directly, on citations built for the
  purpose, because no shipped scenario reaches them by key: since ADR 0005 a rule
  edit moves the run identity and with it every finding key, so a citation under
  an edited requirement is already absent from the shipped run. A guard that only
  ever passes vacuously is not pinned, so each one is given a citation it must
  refuse.
"""

from __future__ import annotations

import copy
import unittest

import assessment_fixtures as fx
from epc_control_tower.determinism import read_csv_rows
from epc_control_tower.purpose.assessment.record import build_assessment_digest
from helpers import PROJECT_ROOT, shipped_pipeline_result
from test_doctor_adapter import _observed

from internal.doctor_adapter import SCENARIOS
from internal.doctor_adapter.details import finding_details, source_from_bundle

CANONICAL = PROJECT_ROOT / "data" / "processed" / "canonical"

FIELDS = [
    "rule_id",
    "requirement_id",
    "labels",
    "citation",
    "expected",
    "actual",
    "reason",
    "status",
]

#: What a rule author wrote about the rule. None of it is the project's
#: assignment, and none of it crosses.
RULE_AUTHOR_METADATA = ("owner_role", "severity", "priority", "stage")

RECORD_SCENARIOS = tuple(sorted(name for name in SCENARIOS if name != "real-refusal"))
EDITED_R005A = ("recheck-requirement-relaxed", "recheck-semantics-changed")

PROJECT_ASSUMPTION = (
    "Project-assumed EPC delivery requirement; not a buildingSMART obligation."
)
PSET_MISSING = "The required property set does not exist"
#: Copied as the checker wrote it, Python ``repr`` and all. It checks containment
#: in a space or a storey of the element's own model, and nothing about whether
#: another model has that storey.
CONTAINED_IN = (
    "An element must have an IFCRELCONTAINEDINSPATIALSTRUCTURE relationship with an "
    "{'enumeration': ['IFCSPACE', 'IFCBUILDINGSTOREY']}"
)
SATISFIED = "Requirement satisfied."

#: The first record's nine citations: ``(element, rule, requirement) -> (status,
#: expected, actual, reason)``.
FIRST_RECORD = {
    **{
        (element, rule, "IFCRELCONTAINEDINSPATIALSTRUCTURE"): (
            "PASS",
            CONTAINED_IN,
            "",
            SATISFIED,
        )
        for element, rule in (
            (fx.HVAC_DUCT, "R-004A"),
            (fx.HVAC_AIR_TERMINAL_COVER, "R-004B"),
            (fx.HVAC_AIR_TERMINAL_CAP, "R-004B"),
        )
    },
    **{
        (element, rule, f"EPC_Delivery.{name}"): (
            "FAIL",
            f"{name} data shall be provided in the dataset EPC_Delivery",
            "",
            PSET_MISSING,
        )
        for element, rule in (
            (fx.HVAC_DUCT, "R-005A"),
            (fx.HVAC_AIR_TERMINAL_COVER, "R-005B"),
            (fx.HVAC_AIR_TERMINAL_CAP, "R-005B"),
        )
        for name in ("AssetTag", "SystemCode")
    },
}

#: ``scenario -> (current citations with an entry, current citations, sealed
#: citations with an entry, sealed citations)``. A *current* citation is one the
#: record's own readings cite; a *sealed* one is a finding the prior record cited,
#: named by a carry-over row.
CARRIED = {
    "member-evidence": (9, 9, 0, 0),
    "pair-verdicts": (9, 9, 0, 0),
    "recheck-comparison": (9, 9, 0, 0),
    "recheck-prior-without-basis": (9, 9, 9, 9),
    "recheck-key-change-only": (0, 9, 9, 9),
    "recheck-semantics-changed": (0, 9, 9, 9),
    "recheck-requirement-relaxed": (0, 9, 9, 9),
    "recheck-producing-reissued": (0, 9, 9, 9),
    "recheck-producing-reissued-content-changed": (0, 9, 9, 9),
    "recheck-consuming-reissued": (0, 9, 9, 9),
    "recheck-both-reissued": (0, 9, 9, 9),
    "recheck-member-gone": (0, 6, 9, 9),
}


def _current(record):
    """Every finding the record's own readings cite, with its sealed basis."""

    return [
        cited
        for activity in record["activities"]
        for subscope in activity["subscopes"]
        for node in subscope["path"]
        for reading in node["readings"]
        for cited in reading.get("cited_findings", ())
    ]


def _finding_rows(record):
    return [
        row
        for subscope in record.get("successor", {}).get("subscopes", ())
        for row in subscope["evidence_carry_over"]
        if row["citation_kind"] == "finding"
    ]


def _walk(value):
    yield value
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


class _DetailsCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.envelopes = _observed().envelopes
        cls.bundle = shipped_pipeline_result().bundle
        cls.source = source_from_bundle(cls.bundle)
        cls.first = cls.envelopes["member-evidence"]["record"]

    def details(self, name):
        return self.envelopes[name]["finding_details"]


class TheKeyIsThereExactlyForARecordTests(_DetailsCase):
    def test_a_record_envelope_gains_one_key_and_keeps_the_rest_in_order(self):
        for name in RECORD_SCENARIOS:
            with self.subTest(scenario=name):
                self.assertEqual(
                    list(self.envelopes[name]),
                    [
                        "mode",
                        "outcome",
                        "record",
                        "assessment_digest",
                        "elements",
                        "finding_details",
                    ],
                )
                self.assertIsInstance(self.details(name), dict)

    def test_a_refusal_envelope_does_not_carry_it(self):
        self.assertEqual(
            list(self.envelopes["real-refusal"]), ["mode", "outcome", "refusal", "elements"]
        )

    def test_the_record_and_its_digest_did_not_move(self):
        """The details sit beside the record; nothing of them is sealed into it."""

        for name in RECORD_SCENARIOS:
            with self.subTest(scenario=name):
                envelope = self.envelopes[name]
                self.assertEqual(
                    build_assessment_digest(envelope["record"]),
                    envelope["assessment_digest"],
                )
                self.assertNotIn("finding_details", envelope["record"])


class EveryEntryIsCopiedTests(_DetailsCase):
    def test_every_entry_has_exactly_the_eight_fields_and_no_null(self):
        for name in RECORD_SCENARIOS:
            for key, entry in self.details(name).items():
                with self.subTest(scenario=name, finding=key):
                    self.assertEqual(list(entry), FIELDS)
                    self.assertIsInstance(entry["labels"], list)
                    for field in FIELDS:
                        if field != "labels":
                            self.assertIsInstance(entry[field], str)
                    self.assertNotIn(None, list(_walk(entry)))

    def test_no_rule_author_metadata_crosses(self):
        for name in RECORD_SCENARIOS:
            with self.subTest(scenario=name):
                seen = {item for item in _walk(self.details(name)) if isinstance(item, str)}
                self.assertEqual(seen & set(RULE_AUTHOR_METADATA), set())

    def test_every_entry_is_the_published_row_field_for_field(self):
        """Not what the adapter read — which is why agreeing with it means something."""

        findings = {
            row["finding_key"]: row for row in read_csv_rows(CANONICAL / "findings.csv")
        }
        requirements = {
            row["requirement_key"]: row
            for row in read_csv_rows(CANONICAL / "requirements.csv")
        }
        for name in RECORD_SCENARIOS:
            for key, entry in self.details(name).items():
                with self.subTest(scenario=name, finding=key):
                    finding = findings[key]
                    requirement = requirements[finding["requirement_key"]]
                    self.assertEqual(
                        entry,
                        {
                            "rule_id": requirement["rule_id"],
                            "requirement_id": requirement["requirement_id"],
                            "labels": [
                                label for label in requirement["labels"].split(";") if label
                            ],
                            "citation": requirement["citation"],
                            "expected": finding["expected"],
                            "actual": finding["actual"],
                            "reason": finding["reason"],
                            "status": finding["status"],
                        },
                    )

    def test_every_entry_is_what_the_test_suites_own_run_holds(self):
        findings = {item.finding_key: item for item in self.bundle.findings}
        requirements = {
            item.requirement_key: item for item in self.bundle.ruleset.requirements
        }
        for name in RECORD_SCENARIOS:
            for key, entry in self.details(name).items():
                with self.subTest(scenario=name, finding=key):
                    finding = findings[key]
                    requirement = requirements[finding.requirement_key]
                    self.assertEqual(
                        entry,
                        {
                            "rule_id": requirement.rule_id,
                            "requirement_id": requirement.requirement_id,
                            "labels": list(requirement.labels),
                            "citation": requirement.citation,
                            "expected": finding.expected,
                            "actual": finding.actual,
                            "reason": finding.reason,
                            "status": str(finding.status),
                        },
                    )

    def test_entries_are_in_finding_key_order(self):
        for name in RECORD_SCENARIOS:
            with self.subTest(scenario=name):
                self.assertEqual(list(self.details(name)), sorted(self.details(name)))


class TheFirstRecordTests(_DetailsCase):
    """The ordinary first check: nine citations, nine entries."""

    def test_each_of_the_nine_citations_says_what_it_required_and_found(self):
        details = self.details("member-evidence")
        cited = _current(self.first)
        self.assertEqual(sorted(details), sorted(item["finding_key"] for item in cited))
        observed = {}
        for item in cited:
            entry = details[item["finding_key"]]
            observed[(item["element_key"], entry["rule_id"], entry["requirement_id"])] = (
                entry["status"],
                entry["expected"],
                entry["actual"],
                entry["reason"],
            )
        self.assertEqual(len(FIRST_RECORD), 9)
        self.assertEqual(observed, FIRST_RECORD)

    def test_the_project_assumption_is_carried_from_the_data(self):
        """"本项目约定的" is the rule's own label and citation, not a screen's claim."""

        for entry in self.details("member-evidence").values():
            with self.subTest(rule=entry["rule_id"], requirement=entry["requirement_id"]):
                if entry["rule_id"].startswith("R-005"):
                    self.assertEqual(entry["labels"], ["IDS", "ProjectAssumption"])
                    self.assertEqual(entry["citation"], PROJECT_ASSUMPTION)
                else:
                    self.assertNotIn("ProjectAssumption", entry["labels"])

    def test_an_empty_actual_stays_an_empty_string(self):
        """The run observed no value and published none; that is not a missing key."""

        for entry in self.details("member-evidence").values():
            self.assertEqual(entry["actual"], "")


class WhichCitationsCarryAnEntryTests(_DetailsCase):
    def test_every_scenario_is_pinned(self):
        self.assertEqual(sorted(CARRIED), list(RECORD_SCENARIOS))

    def test_the_counts_are_the_pinned_ones(self):
        for name in RECORD_SCENARIOS:
            with self.subTest(scenario=name):
                record = self.envelopes[name]["record"]
                details = self.details(name)
                current = [item["finding_key"] for item in _current(record)]
                sealed = [row["citation"] for row in _finding_rows(record)]
                self.assertEqual(
                    (
                        sum(key in details for key in current),
                        len(current),
                        sum(key in details for key in sealed),
                        len(sealed),
                    ),
                    CARRIED[name],
                )
                # And nothing is described that the record does not cite.
                self.assertEqual(set(details) - set(current) - set(sealed), set())

    def test_no_fixture_marked_finding_is_described(self):
        """A simulated finding is not the output of the run the details come from."""

        marked = 0
        for name in RECORD_SCENARIOS:
            record = self.envelopes[name]["record"]
            details = self.details(name)
            for key in details:
                self.assertFalse(key.startswith(fx.FIXTURE_MARKER), (name, key))
            for item in _current(record):
                if item["finding_key"].startswith(f"{fx.FIXTURE_MARKER}/finding/"):
                    marked += 1
                    self.assertNotIn(item["finding_key"], details)
            for row in _finding_rows(record):
                current = row.get("current_citation", "")
                if current:
                    self.assertNotIn(current, details)
        self.assertEqual(marked, 69)

    def test_an_entry_exists_only_under_the_run_its_citing_record_names(self):
        published = self.first["provenance"]["validation_run_id"]
        self.assertEqual(self.source.validation_run_id, published)
        for name in RECORD_SCENARIOS:
            record = self.envelopes[name]["record"]
            if record["provenance"]["validation_run_id"] == published:
                continue
            with self.subTest(scenario=name):
                # Every entry here is a sealed citation of the first record,
                # which names the published run; the successor names another.
                self.assertEqual(
                    record["successor"]["prior_assessment_digest"],
                    self.envelopes["member-evidence"]["assessment_digest"],
                )
                self.assertEqual(
                    set(self.details(name)),
                    {row["citation"] for row in _finding_rows(record)},
                )


class AnEditedRequirementIsNeverExplainedByTheShippedOneTests(_DetailsCase):
    """The counterexample: two R-005A citations under an edited predicate."""

    def edited(self, name):
        """The duct's two current R-005A citations, and the rows that name them."""

        requirements = {
            item.requirement_key: item for item in self.bundle.ruleset.requirements
        }
        record = self.envelopes[name]["record"]
        current = [
            item
            for item in _current(record)
            if requirements[item["requirement_key"]].rule_id == "R-005A"
        ]
        self.assertEqual(len(current), 2)
        self.assertEqual({item["element_key"] for item in current}, {fx.HVAC_DUCT})
        return requirements, record, current

    def test_the_two_citations_carry_no_entry(self):
        for name in EDITED_R005A:
            requirements, _record, current = self.edited(name)
            for item in current:
                with self.subTest(scenario=name, finding=item["finding_key"]):
                    # Same requirement key, another predicate: the shipped
                    # requirement is not the one this citation was made under.
                    self.assertNotEqual(
                        item["semantics_digest"],
                        requirements[item["requirement_key"]].semantics_digest,
                    )
                    self.assertNotIn(item["finding_key"], self.details(name))

    def test_what_the_first_assessment_cited_is_still_explained_as_it_was(self):
        """The sealed side is the first record's, under the requirement it sealed."""

        for name in EDITED_R005A:
            _requirements, record, current = self.edited(name)
            replaced = {item["finding_key"] for item in current}
            sealed = [
                row["citation"]
                for row in _finding_rows(record)
                if row.get("current_citation") in replaced
            ]
            self.assertEqual(len(sealed), 2)
            for key in sealed:
                with self.subTest(scenario=name, finding=key):
                    self.assertEqual(
                        self.details(name)[key],
                        self.details("member-evidence")[key],
                    )
                    self.assertEqual(self.details(name)[key]["rule_id"], "R-005A")

    def test_a_published_key_cited_under_another_predicate_is_refused(self):
        """The guard itself: were the key to survive the edit, the digest would not."""

        for name in EDITED_R005A:
            _requirements, _record, current = self.edited(name)
            edited = {
                (item["element_key"], item["requirement_key"]): item["semantics_digest"]
                for item in current
            }
            record = copy.deepcopy(self.first)
            moved = []
            for item in _current(record):
                coordinates = (item["element_key"], item["requirement_key"])
                if coordinates in edited:
                    item["semantics_digest"] = edited[coordinates]
                    moved.append(item["finding_key"])
            self.assertEqual(len(moved), 2)
            with self.subTest(scenario=name):
                details = finding_details(self.source, record)
                self.assertEqual(len(details), 7)
                for key in moved:
                    self.assertNotIn(key, details)


class TheGuardsRefuseTests(_DetailsCase):
    def test_the_first_record_alone_gives_the_nine(self):
        self.assertEqual(
            finding_details(self.source, self.first), self.details("member-evidence")
        )

    def test_a_record_citing_another_run_gets_nothing(self):
        record = copy.deepcopy(self.first)
        record["provenance"]["validation_run_id"] = "epc-delivery-v2.2-0000000000000000"
        self.assertEqual(finding_details(self.source, record), {})

    def test_a_citation_without_a_recorded_predicate_is_not_comparable(self):
        record = copy.deepcopy(self.first)
        stripped = _current(record)[0]
        stripped["semantics_digest"] = ""
        details = finding_details(self.source, record)
        self.assertEqual(len(details), 8)
        self.assertNotIn(stripped["finding_key"], details)

    def test_a_citation_that_says_something_else_is_refused(self):
        """Same key and predicate, other content: the text would not be what was sealed."""

        record = copy.deepcopy(self.first)
        other = _current(record)[0]
        other["content_digest"] = "0" * 64
        details = finding_details(self.source, record)
        self.assertEqual(len(details), 8)
        self.assertNotIn(other["finding_key"], details)

    def test_a_citation_under_another_requirement_is_refused(self):
        record = copy.deepcopy(self.first)
        cited = _current(record)
        cited[0]["requirement_key"] = cited[-1]["requirement_key"]
        self.assertNotIn(cited[0]["finding_key"], finding_details(self.source, record))

    def test_a_key_the_run_does_not_hold_is_omitted_and_never_null(self):
        record = copy.deepcopy(self.first)
        unknown = _current(record)[0]
        unknown["finding_key"] = "00000000-0000-5000-8000-000000000000"
        details = finding_details(self.source, record)
        self.assertEqual(len(details), 8)
        self.assertNotIn(unknown["finding_key"], details)

    def test_a_reading_with_keys_and_no_basis_gets_nothing(self):
        """A record sealed before contract 1.7: what it cited cannot be compared."""

        record = copy.deepcopy(self.first)
        for activity in record["activities"]:
            for subscope in activity["subscopes"]:
                for node in subscope["path"]:
                    for reading in node["readings"]:
                        reading.pop("cited_findings", None)
        self.assertEqual(finding_details(self.source, record), {})

    def test_a_prior_the_record_does_not_name_is_a_defect(self):
        successor = self.envelopes["recheck-requirement-relaxed"]["record"]
        other = copy.deepcopy(self.first)
        other["provenance"]["cited_cost_parameter_names"] = ["not-the-prior"]
        with self.assertRaises(ValueError):
            finding_details(self.source, successor, other)
        with self.assertRaises(ValueError):
            finding_details(self.source, self.first, self.first)

    def test_a_prior_describes_only_what_the_successor_names(self):
        """One rechecked subscope names no finding row, so the prior adds nothing."""

        successor = copy.deepcopy(self.envelopes["recheck-requirement-relaxed"]["record"])
        self.assertEqual(len(finding_details(self.source, successor, self.first)), 9)
        for subscope in successor["successor"]["subscopes"]:
            subscope["evidence_carry_over"] = [
                row
                for row in subscope["evidence_carry_over"]
                if row["citation_kind"] != "finding"
            ]
        self.assertEqual(finding_details(self.source, successor, self.first), {})


if __name__ == "__main__":
    unittest.main()
