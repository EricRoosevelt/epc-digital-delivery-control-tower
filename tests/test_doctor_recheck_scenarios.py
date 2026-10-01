"""The adapter's recheck scenarios record what the Framework recorded, row by row.

One claim: the internal Doctor adapter offers enough fixture recheck scenarios for
a screen to show every state a carry-over row can be in and every side a re-issue
can come from — and each of them is the Framework's own successor record,
unchanged, inside the same fixed envelope.

Two kinds of assertion, kept apart:

* **Unchanged.** Every scenario's record is compared, byte for byte, with one this
  module builds *without* the adapter, from the test suite's own runs
  (``rule_edits.edited_run`` writes its scratch copy under ``tests/``; the adapter
  writes its copy outside the checkout — the facts must not depend on which).
* **Pinned.** Every carry-over row of every scenario is pinned by what it is
  about — the element and the rule a sealed finding citation belongs to, or a
  determination's reference — to its state, reason, ``key_changed``,
  ``changed_aspects`` and ``cause``; and each scenario's ``changed_models`` is
  pinned beside them. The identities are resolved here, from the shipped run,
  because the record itself does not carry them on the row (see the data gaps in
  the checkpoint report).

The envelopes are read as the bytes the command line prints, through the same
session-wide observation ``test_doctor_adapter`` makes — which is also what
measures, for these scenarios like every other, that nothing is written inside
the checkout and that refusing the network changes no byte.
"""

from __future__ import annotations

import csv
import json
import unittest

import assessment_fixtures as fx
from epc_control_tower.purpose import assess_purpose, facts_from_bundle, recheck_purpose
from epc_control_tower.purpose.assessment.record import (
    CARRY_OVER_REASON_STATES,
    CARRY_OVER_STATES,
    build_assessment_digest,
)
from helpers import PROJECT_ROOT, shipped_pipeline_result
from rule_edits import edited_run
from test_doctor_adapter import ALL_ACTIVITIES, _compact, _observed

from internal.doctor_adapter import SCENARIOS, scenario_index
from internal.doctor_adapter.fixture import RECHECK_SCENARIOS

PROJECT = "pcert-sample"
SCHEDULES = f"{fx.PACK_ID}::schedules-and-room-data-sheets"
CEILING = f"{fx.PACK_ID}::ceiling-and-bulkhead-geometry"
OPENINGS = f"{fx.PACK_ID}::builders-work-openings"

HVAC = "hvac"
ARCHITECTURE = "architecture"

# --- What a sealed citation is about. Names for the four admitted HVAC elements,
# --- and ``rule_id/requirement_id`` for the requirement.
ELEMENTS = {
    fx.HVAC_DUCT: "duct",
    fx.HVAC_AIR_TERMINAL_COVER: "cover",
    fx.HVAC_AIR_TERMINAL_CAP: "cap",
    fx.HVAC_CHIMNEY: "chimney",
}
CONTAINED = "IFCRELCONTAINEDINSPATIALSTRUCTURE"
DUCT_R004 = ("duct", f"R-004A/{CONTAINED}")
COVER_R004 = ("cover", f"R-004B/{CONTAINED}")
CAP_R004 = ("cap", f"R-004B/{CONTAINED}")
DUCT_SYSTEM = ("duct", "R-005A/EPC_Delivery.SystemCode")
DUCT_TAG = ("duct", "R-005A/EPC_Delivery.AssetTag")
COVER_SYSTEM = ("cover", "R-005B/EPC_Delivery.SystemCode")
COVER_TAG = ("cover", "R-005B/EPC_Delivery.AssetTag")
CAP_SYSTEM = ("cap", "R-005B/EPC_Delivery.SystemCode")
CAP_TAG = ("cap", "R-005B/EPC_Delivery.AssetTag")

R004 = (DUCT_R004, COVER_R004, CAP_R004)
R005 = (DUCT_SYSTEM, DUCT_TAG, COVER_SYSTEM, COVER_TAG, CAP_SYSTEM, CAP_TAG)
FINDINGS = R004 + R005

ALIGNMENT = fx.ALIGNMENT_CONFIRMED
DUCT_NONE = "fixture-determination/penetration/duct-none"
SLAB_AND_ROOF = "fixture-determination/penetration/chimney-slab-and-roof"
SLAB_OPENING = "fixture-determination/opening/chimney-slab-cross-referenced"
ROOF_OPENING = "fixture-determination/opening/chimney-roof-not-modelled"

#: Where each row sits when every sealed subscope is answered for: 9 finding rows
#: and 6 determination rows, the slab-and-roof penetration cited by both pairs.
LAYOUT = {
    (OPENINGS, 1): [DUCT_NONE],
    (OPENINGS, 2): [],
    (OPENINGS, 3): [SLAB_OPENING, SLAB_AND_ROOF],
    (OPENINGS, 4): [ROOF_OPENING, SLAB_AND_ROOF],
    (CEILING, 1): [],
    (CEILING, 2): [ALIGNMENT, *R004],
    (SCHEDULES, 1): [],
    (SCHEDULES, 2): [*R005],
}
DETERMINATIONS = (ALIGNMENT, DUCT_NONE, SLAB_AND_ROOF, SLAB_OPENING, ROOF_OPENING)

# --- One row, as ``(state, reason, key_changed, changed_aspects, cause)``. ``None``
# --- is "the row does not carry this key", which is a fact about the row.
EQUIVALENT_REKEYED = ("equivalent", "finding-equivalent", "yes", None, None)
NO_BASIS = ("not-provable", "sealed-citation-has-no-comparison-basis", None, None, None)
SUBJECT_GONE = (
    "not-provable",
    "subject-not-present",
    None,
    None,
    "element-deleted-in-reissued-model",
)
SAME_DETERMINATION = (
    "equivalent",
    "determination-same-reference-same-content",
    None,
    None,
    None,
)
NOT_ATTRIBUTABLE = (
    "no-counterpart",
    "determination-not-attributable-to-this-context",
    None,
    None,
    None,
)


def changed(*aspects: str):
    return ("changed", "finding-changed", "yes", list(aspects), None)


def every(identities, row, overrides=None):
    return {identity: row for identity in identities} | (overrides or {})


#: ``scenario -> (changed_models, rows)``. Every row of every scenario is here.
EXPECTED = {
    "recheck-key-change-only": (
        [],
        every(FINDINGS, EQUIVALENT_REKEYED) | every(DETERMINATIONS, SAME_DETERMINATION),
    ),
    "recheck-semantics-changed": (
        [],
        every(
            FINDINGS,
            EQUIVALENT_REKEYED,
            every((DUCT_SYSTEM, DUCT_TAG), changed("requirement-semantics")),
        )
        | every(DETERMINATIONS, SAME_DETERMINATION),
    ),
    "recheck-requirement-relaxed": (
        [],
        every(
            FINDINGS,
            EQUIVALENT_REKEYED,
            every(
                (DUCT_SYSTEM, DUCT_TAG),
                changed("finding-content", "requirement-semantics"),
            ),
        )
        | every(DETERMINATIONS, SAME_DETERMINATION),
    ),
    "recheck-prior-without-basis": (
        [],
        every(FINDINGS, NO_BASIS) | every(DETERMINATIONS, SAME_DETERMINATION),
    ),
    "recheck-producing-reissued": (
        [HVAC],
        every(FINDINGS, changed("model-version")) | every(DETERMINATIONS, NOT_ATTRIBUTABLE),
    ),
    "recheck-producing-reissued-content-changed": (
        [HVAC],
        every(R004, changed("model-version"))
        | every(R005, changed("finding-content", "model-version"))
        | every(DETERMINATIONS, NOT_ATTRIBUTABLE),
    ),
    "recheck-consuming-reissued": (
        [ARCHITECTURE],
        every(FINDINGS, EQUIVALENT_REKEYED) | every(DETERMINATIONS, NOT_ATTRIBUTABLE),
    ),
    "recheck-both-reissued": (
        [ARCHITECTURE, HVAC],
        every(FINDINGS, changed("model-version")) | every(DETERMINATIONS, NOT_ATTRIBUTABLE),
    ),
    "recheck-member-gone": (
        [HVAC],
        every(
            FINDINGS,
            changed("model-version"),
            every((DUCT_R004, DUCT_SYSTEM, DUCT_TAG), SUBJECT_GONE),
        )
        | every(DETERMINATIONS, NOT_ATTRIBUTABLE),
    ),
}

#: The keys a row carries, by what it turned out to be. Nothing else is on a row.
FINDING_ROW_KEYS = {
    "equivalent": [
        "citation",
        "citation_kind",
        "state",
        "reason",
        "current_citation",
        "key_changed",
    ],
    "changed": [
        "citation",
        "citation_kind",
        "state",
        "reason",
        "current_citation",
        "key_changed",
        "changed_aspects",
    ],
    "not-provable/sealed-citation-has-no-comparison-basis": [
        "citation",
        "citation_kind",
        "state",
        "reason",
    ],
    "not-provable/subject-not-present": [
        "citation",
        "citation_kind",
        "state",
        "reason",
        "cause",
    ],
}
DETERMINATION_ROW_KEYS = {
    "equivalent": [
        "citation",
        "citation_kind",
        "state",
        "reason",
        "sealed_content_digest",
        "current_content_digest",
    ],
    "no-counterpart": ["citation", "citation_kind", "state", "reason", "sealed_content_digest"],
}

SUCCESSOR_KEYS = [
    "kind",
    "prior_assessment_digest",
    "model_version_context_comparison",
    "subscopes",
]
COMPARISON_KEYS = [
    "prior_producing",
    "producing",
    "prior_consuming",
    "consuming",
    "is_current",
    "changed_models",
]
SUBSCOPE_KEYS = [
    "activity_ref",
    "subscope_ordinal",
    "prior_verdict",
    "prior_resolution_kind",
    "prior_recheck_condition",
    "prior_leaf_evidence_requirement_id",
    "prior_members",
    "dispositions",
    "evidence_carry_over",
    "correspondence",
    "named_outcome",
    "condition_status",
    "condition_basis",
]


class _Direct:
    """Every recheck scenario's record, produced without the adapter."""

    @classmethod
    def build(cls):
        facts = fx.assessment_facts()
        composed = fx.fixture_composed()
        first = assess_purpose(
            request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=facts),
            composed=composed,
            facts=facts,
            determinations=fx.fixture_determinations(facts=facts),
        )

        def recheck(prior, after, determinations):
            return recheck_purpose(
                prior=prior,
                request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=after),
                composed=composed,
                facts=after,
                determinations=determinations,
                succeeds=tuple(
                    (activity.activity_ref, subscope.ordinal)
                    for activity in prior.activities
                    for subscope in activity.subscopes
                ),
            )

        def edited(edit):
            after = fx.fixture_revalidated_facts(
                facts_from_bundle(edited_run(edit).bundle, PROJECT),
                label=f"rules-edited-{edit}",
            )
            return recheck(first, after, fx.fixture_determinations(facts=after))

        def reissued(label, *model_keys, **changes):
            after = fx.fixture_revalidated_facts(
                facts, label=label, reissued_model_keys=model_keys, **changes
            )
            return recheck(first, after, ())

        without_basis = fx.fixture_record_without_comparison_basis(first)
        return {
            "first": first,
            "without-basis": without_basis,
            "records": {
                "recheck-key-change-only": edited("r002-datatype"),
                "recheck-semantics-changed": edited("r005a-datatype"),
                "recheck-requirement-relaxed": edited("r005a-optional"),
                "recheck-prior-without-basis": recheck(
                    without_basis, facts, fx.fixture_determinations(facts=facts)
                ),
                "recheck-producing-reissued": reissued("producing-reissued", HVAC),
                "recheck-producing-reissued-content-changed": reissued(
                    "producing-reissued-content-changed", HVAC, asset_identity_fixed=True
                ),
                "recheck-consuming-reissued": reissued("consuming-reissued", ARCHITECTURE),
                "recheck-both-reissued": reissued("both-reissued", HVAC, ARCHITECTURE),
                "recheck-member-gone": reissued(
                    "producing-reissued-duct-deleted", HVAC, delete=fx.HVAC_DUCT
                ),
            },
        }


class _ScenarioCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        observed = _observed()
        cls.envelopes = {name: observed.envelopes[name] for name in EXPECTED}
        cls.first_digest = observed.envelopes["member-evidence"]["assessment_digest"]
        bundle = shipped_pipeline_result().bundle
        labels = {
            requirement.requirement_key: f"{requirement.rule_id}/{requirement.requirement_id}"
            for requirement in bundle.ruleset.requirements
        }
        #: sealed ``finding_key`` -> ``(element name, rule label)``, from the shipped run.
        cls.sealed = {
            finding.finding_key: (
                ELEMENTS.get(finding.element_key, finding.element_key),
                labels[finding.requirement_key],
            )
            for finding in fx.assessment_facts().findings
        }
        with (PROJECT_ROOT / "data" / "processed" / "canonical" / "findings.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.published = {row["finding_key"] for row in csv.DictReader(stream)}

    def successor(self, name):
        return self.envelopes[name]["record"]["successor"]

    def identity(self, row):
        if row["citation_kind"] == "finding":
            return self.sealed[row["citation"]]
        return row["citation"]

    def rows(self, name):
        for outcome in self.successor(name)["subscopes"]:
            for row in outcome["evidence_carry_over"]:
                yield outcome, row


class TheScenariosAreTheseTests(_ScenarioCase):
    def test_the_recheck_scenarios_are_exactly_the_pinned_ones(self):
        self.assertEqual(sorted(RECHECK_SCENARIOS), sorted(EXPECTED))
        self.assertEqual(
            sorted(name for name in SCENARIOS if name.startswith("recheck-")),
            sorted([*EXPECTED, "recheck-comparison"]),
        )

    def test_every_recheck_is_a_fixture_and_the_real_mode_offers_none(self):
        """``mode`` is the entry called, and no real recheck is conjured."""

        declared = {entry["name"]: entry["mode"] for entry in scenario_index()}
        for name in EXPECTED:
            with self.subTest(scenario=name):
                self.assertEqual(declared[name], "fixture")
                self.assertEqual(self.envelopes[name]["mode"], "fixture")
        self.assertEqual(
            [name for name, mode in declared.items() if mode == "real"], ["real-refusal"]
        )
        real = _observed().envelopes["real-refusal"]
        self.assertEqual(real["outcome"], "refusal")
        self.assertNotIn("record", real)


class TheEnvelopeShapeDoesNotMoveTests(_ScenarioCase):
    """Boundary 1: the same five keys, and ``record`` is ``as_document()``."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.direct = _Direct.build()

    def test_the_envelope_keys_are_the_fixed_five(self):
        for name, envelope in self.envelopes.items():
            with self.subTest(scenario=name):
                self.assertEqual(
                    list(envelope),
                    ["mode", "outcome", "record", "assessment_digest", "elements"],
                )
                self.assertEqual(envelope["outcome"], "record")
                self.assertEqual(
                    list(envelope["record"]),
                    ["request", "provenance", "activities", "successor"],
                )

    def test_the_record_is_byte_identical_to_the_frameworks_own(self):
        for name, envelope in self.envelopes.items():
            direct = self.direct["records"][name]
            with self.subTest(scenario=name):
                self.assertEqual(_compact(envelope["record"]), _compact(direct.as_document()))
                self.assertEqual(envelope["assessment_digest"], direct.assessment_digest)
                self.assertEqual(
                    build_assessment_digest(envelope["record"]), envelope["assessment_digest"]
                )

    def test_the_successor_carries_exactly_the_keys_the_record_defines(self):
        for name in EXPECTED:
            successor = self.successor(name)
            with self.subTest(scenario=name):
                self.assertEqual(list(successor), SUCCESSOR_KEYS)
                self.assertEqual(successor["kind"], "recheck")
                self.assertEqual(
                    list(successor["model_version_context_comparison"]), COMPARISON_KEYS
                )
                for outcome in successor["subscopes"]:
                    self.assertEqual(list(outcome), SUBSCOPE_KEYS)

    def test_every_row_carries_exactly_the_keys_its_state_allows(self):
        for name in EXPECTED:
            for _outcome, row in self.rows(name):
                with self.subTest(scenario=name, citation=row["citation"]):
                    self.assertNotIn("carried", row)
                    if row["citation_kind"] == "determination":
                        expected = DETERMINATION_ROW_KEYS[row["state"]]
                    elif row["state"] == "not-provable":
                        expected = FINDING_ROW_KEYS[f"not-provable/{row['reason']}"]
                    else:
                        expected = FINDING_ROW_KEYS[row["state"]]
                    self.assertEqual(list(row), expected)

    def test_each_prior_is_the_sealed_record_it_says_it_is(self):
        first = self.direct["first"]
        without_basis = self.direct["without-basis"]
        self.assertEqual(first.assessment_digest, self.first_digest)
        self.assertNotEqual(without_basis.assessment_digest, first.assessment_digest)
        self.assertNotIn('"cited_findings"', json.dumps(without_basis.as_document()))
        for name in EXPECTED:
            prior = without_basis if name == "recheck-prior-without-basis" else first
            with self.subTest(scenario=name):
                self.assertEqual(
                    self.successor(name)["prior_assessment_digest"], prior.assessment_digest
                )


class EveryRowIsPinnedTests(_ScenarioCase):
    """Acceptance: each row's state, reason and changed aspects, and ``changed_models``."""

    def test_every_sealed_subscope_is_answered_for_with_the_same_rows(self):
        for name in EXPECTED:
            layout = {
                (outcome["activity_ref"], outcome["subscope_ordinal"]): sorted(
                    (self.identity(row) for row in outcome["evidence_carry_over"]), key=repr
                )
                for outcome in self.successor(name)["subscopes"]
            }
            with self.subTest(scenario=name):
                self.assertEqual(
                    layout,
                    {key: sorted(value, key=repr) for key, value in LAYOUT.items()},
                )

    def test_every_row_is_in_the_state_and_for_the_reason_pinned(self):
        for name, (_changed_models, expected) in EXPECTED.items():
            seen = {}
            for _outcome, row in self.rows(name):
                identity = self.identity(row)
                observed = (
                    row["state"],
                    row["reason"],
                    row.get("key_changed"),
                    row.get("changed_aspects"),
                    row.get("cause"),
                )
                with self.subTest(scenario=name, row=identity):
                    self.assertEqual(observed, expected[identity])
                    self.assertIn(row["state"], CARRY_OVER_STATES)
                    self.assertEqual(CARRY_OVER_REASON_STATES[row["reason"]], row["state"])
                seen[identity] = observed
            with self.subTest(scenario=name):
                self.assertEqual(seen, expected)

    def test_changed_models_and_the_four_versions(self):
        real = {
            model.model_key: model.content_id for model in fx.assessment_facts().models
        }
        for name, (changed_models, _rows) in EXPECTED.items():
            comparison = self.successor(name)["model_version_context_comparison"]
            now = {
                key: fx.reissued_content_id(key) if key in changed_models else real[key]
                for key in (HVAC, ARCHITECTURE)
            }
            with self.subTest(scenario=name):
                self.assertEqual(comparison["changed_models"], changed_models)
                self.assertEqual(comparison["is_current"], not changed_models)
                self.assertEqual(
                    comparison["prior_producing"], {"model_key": HVAC, "content_id": real[HVAC]}
                )
                self.assertEqual(
                    comparison["prior_consuming"],
                    {"model_key": ARCHITECTURE, "content_id": real[ARCHITECTURE]},
                )
                self.assertEqual(
                    comparison["producing"], {"model_key": HVAC, "content_id": now[HVAC]}
                )
                self.assertEqual(
                    comparison["consuming"],
                    {"model_key": ARCHITECTURE, "content_id": now[ARCHITECTURE]},
                )

    def test_which_side_moved_is_a_lookup_and_the_roles_are_on_the_request(self):
        """The four re-issue cases, read the way a screen would read them."""

        sides = {}
        for name in EXPECTED:
            record = self.envelopes[name]["record"]
            comparison = record["successor"]["model_version_context_comparison"]
            sides[name] = tuple(
                side
                for side in ("producing", "consuming")
                if comparison[side]["model_key"] in comparison["changed_models"]
            )
            with self.subTest(scenario=name):
                handover = record["request"]["model_version_context"]["handover"]
                self.assertEqual(
                    (handover["from_role"], handover["to_role"]), ("MEP", "Architecture")
                )
        self.assertEqual(
            sides,
            {
                "recheck-key-change-only": (),
                "recheck-semantics-changed": (),
                "recheck-requirement-relaxed": (),
                "recheck-prior-without-basis": (),
                "recheck-producing-reissued": ("producing",),
                "recheck-producing-reissued-content-changed": ("producing",),
                "recheck-consuming-reissued": ("consuming",),
                "recheck-both-reissued": ("producing", "consuming"),
                "recheck-member-gone": ("producing",),
            },
        )


class WhatTheScenariosCoverTests(_ScenarioCase):
    """The cases the round asked for, each found in a named scenario."""

    def states(self, name, kind):
        return {
            row["state"]
            for _outcome, row in self.rows(name)
            if row["citation_kind"] == kind
        }

    def test_all_four_states_appear_and_each_in_a_named_scenario(self):
        seen = set()
        for name in EXPECTED:
            seen |= {row["state"] for _outcome, row in self.rows(name)}
        self.assertEqual(seen, set(CARRY_OVER_STATES))
        self.assertEqual(self.states("recheck-key-change-only", "finding"), {"equivalent"})
        self.assertEqual(self.states("recheck-producing-reissued", "finding"), {"changed"})
        self.assertEqual(
            self.states("recheck-producing-reissued", "determination"), {"no-counterpart"}
        )
        self.assertEqual(
            self.states("recheck-prior-without-basis", "finding"), {"not-provable"}
        )

    def test_the_relaxed_requirement_moved_a_verdict_with_no_model_change(self):
        successor = self.successor("recheck-requirement-relaxed")
        self.assertTrue(successor["model_version_context_comparison"]["is_current"])
        (blocked,) = [
            outcome
            for outcome in successor["subscopes"]
            if (outcome["activity_ref"], outcome["subscope_ordinal"]) == (SCHEDULES, 2)
        ]
        self.assertEqual(blocked["prior_verdict"], "BLOCKED")
        verdicts = {
            ELEMENTS[item["member"]["keys"][0]]: item["current_verdicts"]
            for item in blocked["dispositions"]
        }
        self.assertEqual(
            verdicts, {"duct": ["READY"], "cover": ["BLOCKED"], "cap": ["BLOCKED"]}
        )

    def test_the_changed_predicate_moved_no_verdict(self):
        """Semantics changed, outcome did not: only the row says so."""

        for name in ("recheck-semantics-changed", "recheck-key-change-only"):
            for outcome in self.successor(name)["subscopes"]:
                for item in outcome["dispositions"]:
                    with self.subTest(scenario=name, member=item["member"]["keys"]):
                        self.assertEqual(item["disposition"], "present")
                        self.assertEqual(item["current_verdicts"], [outcome["prior_verdict"]])

    def test_the_deleted_member_is_reported_gone_and_never_fixed(self):
        dispositions = {}
        for outcome in self.successor("recheck-member-gone")["subscopes"]:
            for item in outcome["dispositions"]:
                if item["member"]["keys"] == [fx.HVAC_DUCT]:
                    dispositions[
                        (outcome["activity_ref"], outcome["subscope_ordinal"])
                    ] = (item["disposition"], outcome["correspondence"])
        self.assertEqual(
            dispositions,
            {
                (OPENINGS, 1): ("element-deleted-in-reissued-model", "incomplete"),
                (CEILING, 2): ("element-deleted-in-reissued-model", "incomplete"),
                (SCHEDULES, 2): ("element-deleted-in-reissued-model", "incomplete"),
            },
        )
        (blocked,) = [
            outcome
            for outcome in self.successor("recheck-member-gone")["subscopes"]
            if (outcome["activity_ref"], outcome["subscope_ordinal"]) == (SCHEDULES, 2)
        ]
        self.assertEqual(blocked["condition_status"], "not-comparable")


class FixtureEvidenceIsMarkedTests(_ScenarioCase):
    """Boundary 2: nothing a fixture minted can be read as real validation output."""

    def test_a_sealed_citation_is_published_and_a_current_one_is_marked(self):
        for name in EXPECTED:
            for _outcome, row in self.rows(name):
                if row["citation_kind"] != "finding":
                    continue
                with self.subTest(scenario=name, citation=row["citation"]):
                    # The first record was assessed against the shipped run.
                    self.assertIn(row["citation"], self.published)
                    self.assertFalse(row["citation"].startswith(fx.FIXTURE_MARKER))
                    if "current_citation" in row:
                        self.assertTrue(
                            row["current_citation"].startswith(f"{fx.FIXTURE_MARKER}/finding/")
                        )
                        self.assertNotIn(row["current_citation"], self.published)

    def test_every_determination_reference_is_marked(self):
        for name in EXPECTED:
            for _outcome, row in self.rows(name):
                if row["citation_kind"] == "determination":
                    with self.subTest(scenario=name, citation=row["citation"]):
                        self.assertTrue(row["citation"].startswith(fx.FIXTURE_MARKER))

    def test_every_finding_the_successor_itself_cites_is_marked_or_published(self):
        """On the evidence path too, the marker alone decides the label."""

        for name, envelope in self.envelopes.items():
            revalidated = name != "recheck-prior-without-basis"
            cited = 0
            for activity in envelope["record"]["activities"]:
                for subscope in activity["subscopes"]:
                    for step in subscope["path"]:
                        for reading in step["readings"]:
                            for key in reading.get("finding_keys", ()):
                                cited += 1
                                with self.subTest(scenario=name, finding_key=key):
                                    marked = key.startswith(fx.FIXTURE_MARKER)
                                    self.assertEqual(marked, key not in self.published)
                                    self.assertEqual(marked, revalidated)
            with self.subTest(scenario=name):
                self.assertGreater(cited, 0)

    def test_a_second_run_is_never_given_a_published_runs_identity(self):
        shipped = fx.assessment_facts().validation_run_id
        for name, envelope in self.envelopes.items():
            run_id = envelope["record"]["provenance"]["validation_run_id"]
            with self.subTest(scenario=name):
                if name == "recheck-prior-without-basis":
                    # No second run: the same shipped facts, an older-shaped prior.
                    self.assertEqual(run_id, shipped)
                else:
                    self.assertTrue(run_id.startswith(f"{fx.FIXTURE_MARKER}-validation-run/"))
                    self.assertTrue(run_id.endswith("-not-a-published-run"))

    def test_a_reissued_model_is_never_given_a_content_hash(self):
        for name, (changed_models, _rows) in EXPECTED.items():
            comparison = self.successor(name)["model_version_context_comparison"]
            for side in ("producing", "consuming"):
                version = comparison[side]
                with self.subTest(scenario=name, side=side):
                    self.assertEqual(
                        version["content_id"].startswith(fx.FIXTURE_MARKER),
                        version["model_key"] in changed_models,
                    )


if __name__ == "__main__":
    unittest.main()
