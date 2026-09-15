"""The risk-authorisation policy is read when a promotion would consume it.

One claim, and the counterexamples below are what make it a claim rather than a
description: **a project's ``overlay.risk_authorisations[]`` policy is resolved
at the moment a ``CONDITIONAL`` promotion would rest on it, and "that row is a
demonstration value", "there is no such row at all", and "the role this citation
names is not listed" are three different answers to three different questions.**

The three matter separately because each sends a maintainer somewhere else:

* **no row** — this project has no authorisation path for that
  ``resolution_kind`` at all, and giving it one is a new policy decision nobody
  has taken;
* **an illustrative row** — the shape of the policy is there and the decision is
  not, and the line to edit is the one already in the manifest;
* **a role not listed** — the policy is real, was decided, and does not cover
  the role this citation named.

Collapsing any two of them would report one of those situations as another, and
the repository has twice already gone to the trouble of keeping exactly this
distinction: ``determinations.py``'s "the row exists, so this is not the
missing-row case", and ADR 0003 §4.3's "a project told its policy is
illustrative is not left looking for a row that is already there".

**What is deliberately absent.** No promotion record, no nine fields, no
successor, no store, no CLI. The subject here is the authorisation decision
alone — given a project, an exact ``pack_id::resolution_kind``, and the role a
citation names, which of the three answers holds — together with the citations
it refuses outright. A promotion is Checkpoint E2's, unstarted, and nothing in
this module builds one.

**And the ordinary assessment is untouched.** :class:`OrdinaryAssessmentIsUnmovedTests`
pins that as bytes rather than asserting it as an intention.
"""

from __future__ import annotations

import ast
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import assessment_fixtures as fx  # noqa: E402
from epc_control_tower.purpose import (  # noqa: E402
    PurposeAssessmentError,
    assess_purpose,
    compose_purpose_inputs,
    load_project_overlay,
    load_purpose_pack,
)
from epc_control_tower.purpose.assessment.authorisation import (  # noqa: E402
    AUTHORISED,
    NO_AUTHORISATION_PATH,
    RISK_AUTHORISATION_ANSWERS,
    ROLE_NOT_AUTHORISED,
    AuthorisationCitation,
    RiskAuthorisationDecision,
    resolve_risk_authorisation,
)
from helpers import PROJECT_ROOT  # noqa: E402

PACK_ID = fx.PACK_ID
PCERT_MANIFEST = PROJECT_ROOT / "projects" / "pcert-sample" / "project.toml"
ASSESSMENT_PACKAGE = (
    PROJECT_ROOT / "epc_control_tower" / "purpose" / "assessment"
)
DECISIONS = PROJECT_ROOT / "docs" / "decisions"

ALL_ACTIVITIES = (
    "schedules-and-room-data-sheets",
    "ceiling-and-bulkhead-geometry",
    "builders-work-openings",
)

#: The two `resolution_kind` values `pcert-sample` writes a risk-authorisation
#: row for, and the one role both rows list. Read back from the manifest in
#: :meth:`OverlayFactsTheseTestsRestOnTests.test_the_shipped_rows_are_what_these_tests_assume`
#: rather than trusted here.
AUTHORISED_KIND = "cross-model-alignment-not-confirmed"
OTHER_AUTHORISED_KIND = "missing-project-asset-identity"
AUTHORISING_ROLE = "information-manager"

#: Two kinds `pcert-sample` writes no authorisation row for. The first is a
#: `BLOCKED` kind the shipped fixture record actually reaches; the second's Pack
#: `default_role` is `information-manager` — the same string the two rows above
#: list, which is the coincidence counterexample 3 exists to refuse.
UNAUTHORISED_BLOCKED_KIND = "missing-corresponding-opening"
SAME_ROLE_NAME_KIND = "in-model-position-not-evaluated"


def authorising_overlay_document() -> dict:
    """The fixture Overlay with its **risk-authorisation** rows recorded as decided.

    A third edit on top of :func:`assessment_fixtures.fixture_overlay_document`'s
    two, and kept here rather than folded into that function on purpose: every
    other test in this repository composes against an Overlay whose
    ``risk_authorisations`` rows read ``illustrative``, and moving them there
    would change the ``composition_digest`` those tests see for a reason that has
    nothing to do with them.

    Like every other fixture policy value, it is written in memory and never
    back to ``projects/pcert-sample/project.toml``: this repository has recorded
    no risk-authorisation policy, and this round does not give it one.
    """

    document = copy.deepcopy(fx.fixture_overlay_document())
    for row in document["overlay"]["risk_authorisations"]:
        row["decision_basis"] = "project-decision"
    return document


def citation(resolution_kind: str, role: str, *, pack_id: str = PACK_ID):
    return AuthorisationCitation(
        pack_id=pack_id, resolution_kind=resolution_kind, role=role
    )


class OverlayFactsTheseTestsRestOnTests(unittest.TestCase):
    """The live facts every counterexample below is built on, asserted once.

    Read back from the shipped manifest and the shipped Pack. A counterexample
    whose premise has quietly moved does not fail — it passes for a new reason,
    which is the failure mode this class exists to prevent.
    """

    @classmethod
    def setUpClass(cls):
        cls.pack = load_purpose_pack(fx.PACK_PATH)
        cls.overlay = load_project_overlay(PCERT_MANIFEST)

    def test_the_shipped_rows_are_what_these_tests_assume(self):
        rows = {
            (row.pack_id, row.resolution_kind): row
            for row in self.overlay.risk_authorisations
        }
        self.assertEqual(
            sorted(kind for _, kind in rows),
            sorted((AUTHORISED_KIND, OTHER_AUTHORISED_KIND)),
            "pcert-sample no longer authorises exactly these two kinds",
        )
        for kind in (AUTHORISED_KIND, OTHER_AUTHORISED_KIND):
            with self.subTest(resolution_kind=kind):
                row = rows[(PACK_ID, kind)]
                self.assertEqual(row.may_authorise_roles, (AUTHORISING_ROLE,))
                self.assertEqual(row.decision_basis, "illustrative")

    def test_the_two_unauthorised_kinds_really_have_no_row(self):
        covered = {row.resolution_kind for row in self.overlay.risk_authorisations}
        for kind in (UNAUTHORISED_BLOCKED_KIND, SAME_ROLE_NAME_KIND):
            with self.subTest(resolution_kind=kind):
                self.assertIn(kind, {r.resolution_kind for r in self.pack.resolution_routes})
                self.assertNotIn(kind, covered)

    def test_the_role_name_coincidence_counterexample_3_needs_is_real(self):
        """Its `default_role` is the very string the two authorised rows list."""

        self.assertEqual(
            self.pack.route(SAME_ROLE_NAME_KIND).default_role, AUTHORISING_ROLE
        )

    def test_the_unauthorised_blocked_kind_routes_to_a_different_default_role(self):
        """So counterexample 2 can prove the fallback is not taken by role name."""

        self.assertEqual(
            self.pack.route(UNAUTHORISED_BLOCKED_KIND).default_role, "architecture-lead"
        )

    def test_the_fixture_declares_the_authorisation_policy_it_relies_on(self):
        """The positive path rests on a declared decision, not on a silent gate."""

        document = authorising_overlay_document()
        self.assertEqual(
            [row["decision_basis"] for row in document["overlay"]["risk_authorisations"]],
            ["project-decision", "project-decision"],
        )

    def test_the_shipped_manifest_still_records_all_nine_rows_as_illustrative(self):
        text = PCERT_MANIFEST.read_text(encoding="utf-8")
        self.assertEqual(text.count('decision_basis = "project-decision"'), 0)
        self.assertEqual(text.count('decision_basis = "illustrative"'), 9)


class ThreeDistinctAnswersTests(unittest.TestCase):
    """Counterexamples 1 to 5: the three answers, and the citations refused."""

    @classmethod
    def setUpClass(cls):
        cls.pack = load_purpose_pack(fx.PACK_PATH)
        cls.decided = fx.fixture_composed(
            overlay_document=authorising_overlay_document()
        )
        #: The fixture Overlay as every other test composes it: staffed and
        #: accepting methods for real, and authorising risk only illustratively.
        cls.illustrative = fx.fixture_composed()

    def _resolve(self, resolution_kind, role, *, composed=None, cited_kind=None):
        return resolve_risk_authorisation(
            composed=composed if composed is not None else self.decided,
            pack_id=PACK_ID,
            resolution_kind=resolution_kind,
            citation=citation(
                cited_kind if cited_kind is not None else resolution_kind, role
            ),
        )

    # -- the positive path, on the fixture only -----------------------------

    def test_a_listed_role_under_a_decided_row_is_authorised(self):
        decision = self._resolve(AUTHORISED_KIND, AUTHORISING_ROLE)
        self.assertEqual(decision.answer, AUTHORISED)
        self.assertTrue(decision.supports_promotion)
        self.assertEqual(decision.may_authorise_roles, (AUTHORISING_ROLE,))
        self.assertEqual(decision.resolution_kind, AUTHORISED_KIND)
        self.assertEqual(decision.cited_role, AUTHORISING_ROLE)

    def test_the_positive_path_is_reachable_only_on_declared_policy(self):
        """No project this repository ships can reach it; the fixture declares it.

        The same call against the Overlay as shipped raises instead, which is
        what keeps the positive path a fixture's property rather than a claim
        about `pcert-sample`.
        """

        self.assertIsInstance(
            self._resolve(AUTHORISED_KIND, AUTHORISING_ROLE), RiskAuthorisationDecision
        )
        with self.assertRaises(PurposeAssessmentError):
            self._resolve(AUTHORISED_KIND, AUTHORISING_ROLE, composed=self.illustrative)

    # -- counterexample 1: the row is a demonstration value ------------------

    def test_an_illustrative_authorisation_row_refuses(self):
        with self.assertRaises(PurposeAssessmentError) as caught:
            self._resolve(AUTHORISED_KIND, AUTHORISING_ROLE, composed=self.illustrative)
        self.assertEqual(
            caught.exception.code, "risk-authorisation-decision-basis-illustrative"
        )
        message = str(caught.exception)
        self.assertIn("overlay.risk_authorisations", message)
        self.assertIn(AUTHORISED_KIND, message)
        self.assertIn("'illustrative'", message)
        self.assertIn("not the missing-row case", message)

    def test_that_refusal_does_not_support_a_promotion(self):
        """Counterexample 1's first half: an illustrative row authorises nothing."""

        with self.assertRaises(PurposeAssessmentError):
            self._resolve(AUTHORISED_KIND, AUTHORISING_ROLE, composed=self.illustrative)

    def test_an_illustrative_row_and_an_absent_row_are_different_answers(self):
        """Counterexample 1's second half: a different reason, not a shared one.

        One raises with a code naming the table and the row; the other returns
        an answer naming no row to look at. A maintainer reading the first edits
        a line already in the manifest; a maintainer reading the second has a
        policy decision to take first.
        """

        with self.assertRaises(PurposeAssessmentError) as caught:
            self._resolve(AUTHORISED_KIND, AUTHORISING_ROLE, composed=self.illustrative)
        absent = self._resolve(UNAUTHORISED_BLOCKED_KIND, "architecture-lead")
        self.assertEqual(absent.answer, NO_AUTHORISATION_PATH)
        self.assertNotIn(caught.exception.code, absent.answer)
        self.assertNotIn("illustrative", absent.reason)

    def test_the_illustrative_gate_is_reached_before_the_role_check(self):
        """A demonstration row is refused whoever the citation names.

        Otherwise an unlisted role under an illustrative row would report the
        weaker of the two problems and hide the fabrication underneath it.
        """

        with self.assertRaises(PurposeAssessmentError) as caught:
            self._resolve(AUTHORISED_KIND, "mep-lead", composed=self.illustrative)
        self.assertEqual(
            caught.exception.code, "risk-authorisation-decision-basis-illustrative"
        )

    # -- counterexample 2: there is no row at all ---------------------------

    def test_a_kind_with_no_row_has_no_authorisation_path(self):
        decision = self._resolve(UNAUTHORISED_BLOCKED_KIND, "architecture-lead")
        self.assertEqual(decision.answer, NO_AUTHORISATION_PATH)
        self.assertFalse(decision.supports_promotion)
        self.assertEqual(decision.may_authorise_roles, ())

    def test_it_does_not_fall_back_to_the_routes_default_role(self):
        """The cited role *is* the route's `default_role`, and it authorises nothing.

        `resolution_routes[].default_role` names the role that does the work the
        route's `next_action` describes. It is an input to an assignment. It has
        never been, and must not become, a standing authorisation to release the
        work the route describes as blocked.
        """

        role = self.pack.route(UNAUTHORISED_BLOCKED_KIND).default_role
        decision = self._resolve(UNAUTHORISED_BLOCKED_KIND, role)
        self.assertEqual(decision.answer, NO_AUTHORISATION_PATH)
        self.assertNotEqual(decision.answer, AUTHORISED)

    # -- counterexample 3: the same role name is not an authorisation path ---

    def test_a_shared_role_name_is_not_an_authorisation_path(self):
        """`in-model-position-not-evaluated` routes to `information-manager` too.

        Both rows `pcert-sample` does write list exactly that role. An
        implementation that asked "is this role an authoriser in this project?"
        rather than "for this exact `pack_id::resolution_kind`?" would answer
        `authorised` here, and would have released a gap nobody was authorised to
        release.
        """

        decision = self._resolve(SAME_ROLE_NAME_KIND, AUTHORISING_ROLE)
        self.assertEqual(decision.answer, NO_AUTHORISATION_PATH)
        self.assertEqual(decision.may_authorise_roles, ())

    def test_the_same_role_is_authorised_for_the_kinds_that_do_carry_a_row(self):
        """Which is what makes the answer above a boundary rather than a refusal of the role."""

        for kind in (AUTHORISED_KIND, OTHER_AUTHORISED_KIND):
            with self.subTest(resolution_kind=kind):
                self.assertEqual(
                    self._resolve(kind, AUTHORISING_ROLE).answer, AUTHORISED
                )

    # -- counterexample 4: the cited role is not listed ---------------------

    def test_a_role_absent_from_may_authorise_roles_is_not_authorised(self):
        decision = self._resolve(AUTHORISED_KIND, "mep-lead")
        self.assertEqual(decision.answer, ROLE_NOT_AUTHORISED)
        self.assertFalse(decision.supports_promotion)
        self.assertEqual(decision.may_authorise_roles, (AUTHORISING_ROLE,))
        self.assertIn("mep-lead", decision.reason)

    def test_an_unlisted_role_is_a_different_answer_from_an_absent_row(self):
        """The policy exists and does not cover this citation; it is not missing."""

        unlisted = self._resolve(AUTHORISED_KIND, "mep-lead")
        absent = self._resolve(UNAUTHORISED_BLOCKED_KIND, "architecture-lead")
        self.assertNotEqual(unlisted.answer, absent.answer)
        self.assertTrue(unlisted.may_authorise_roles)
        self.assertFalse(absent.may_authorise_roles)

    def test_a_role_this_project_staffs_is_still_not_an_authoriser(self):
        """`team_mapping` staffs a resolver; it never staffs an authoriser."""

        staffed = {row.role for row in self.decided.overlay.team_mapping}
        self.assertIn("mep-lead", staffed)
        self.assertEqual(self._resolve(AUTHORISED_KIND, "mep-lead").answer, ROLE_NOT_AUTHORISED)

    # -- counterexample 5: cross-kind borrowing -----------------------------

    def test_an_authorisation_granted_under_another_kind_refuses(self):
        with self.assertRaises(PurposeAssessmentError) as caught:
            self._resolve(
                AUTHORISED_KIND, AUTHORISING_ROLE, cited_kind=OTHER_AUTHORISED_KIND
            )
        self.assertEqual(caught.exception.code, "risk-authorisation-kind-borrowed")
        message = str(caught.exception)
        self.assertIn(OTHER_AUTHORISED_KIND, message)
        self.assertIn(AUTHORISED_KIND, message)

    def test_the_borrowed_citation_would_otherwise_have_been_authorised(self):
        """Which is what makes the refusal load-bearing rather than incidental.

        The role is listed for both kinds, so every value the citation carries is
        acceptable somewhere. The only thing wrong with it is that it was granted
        against a different deficiency, and an implementation that compared
        nothing but the role would call this a promotion.
        """

        self.assertEqual(
            self._resolve(AUTHORISED_KIND, AUTHORISING_ROLE).answer, AUTHORISED
        )
        with self.assertRaises(PurposeAssessmentError):
            self._resolve(
                AUTHORISED_KIND, AUTHORISING_ROLE, cited_kind=OTHER_AUTHORISED_KIND
            )

    def test_a_citation_naming_another_pack_refuses_the_same_way(self):
        with self.assertRaises(PurposeAssessmentError) as caught:
            resolve_risk_authorisation(
                composed=self.decided,
                pack_id=PACK_ID,
                resolution_kind=AUTHORISED_KIND,
                citation=citation(
                    AUTHORISED_KIND, AUTHORISING_ROLE, pack_id="some-other-pack"
                ),
            )
        self.assertEqual(caught.exception.code, "risk-authorisation-kind-borrowed")

    # -- the kind itself has to be one this configuration can produce -------

    def test_a_resolution_kind_no_bound_pack_declares_refuses(self):
        """`no-authorisation-path` would be a lie: there is no such deficiency."""

        with self.assertRaises(PurposeAssessmentError) as caught:
            self._resolve("not-a-resolution-kind", AUTHORISING_ROLE)
        self.assertEqual(
            caught.exception.code, "risk-authorisation-resolution-kind-unresolved"
        )
        self.assertIn("not-a-resolution-kind", str(caught.exception))

    def test_a_pack_this_project_does_not_bind_refuses(self):
        with self.assertRaises(PurposeAssessmentError) as caught:
            resolve_risk_authorisation(
                composed=self.decided,
                pack_id="some-other-pack",
                resolution_kind=AUTHORISED_KIND,
                citation=citation(
                    AUTHORISED_KIND, AUTHORISING_ROLE, pack_id="some-other-pack"
                ),
            )
        self.assertEqual(
            caught.exception.code, "risk-authorisation-resolution-kind-unresolved"
        )
        self.assertIn("some-other-pack", str(caught.exception))

    # -- shape --------------------------------------------------------------

    def test_the_answer_vocabulary_is_closed_and_every_member_is_reachable(self):
        reached = {
            self._resolve(AUTHORISED_KIND, AUTHORISING_ROLE).answer,
            self._resolve(AUTHORISED_KIND, "mep-lead").answer,
            self._resolve(UNAUTHORISED_BLOCKED_KIND, "architecture-lead").answer,
        }
        self.assertEqual(reached, set(RISK_AUTHORISATION_ANSWERS))
        self.assertEqual(len(RISK_AUTHORISATION_ANSWERS), 3)

    def test_only_one_of_the_three_answers_supports_a_promotion(self):
        supporting = [
            decision.answer
            for decision in (
                self._resolve(AUTHORISED_KIND, AUTHORISING_ROLE),
                self._resolve(AUTHORISED_KIND, "mep-lead"),
                self._resolve(UNAUTHORISED_BLOCKED_KIND, "architecture-lead"),
            )
            if decision.supports_promotion
        ]
        self.assertEqual(supporting, [AUTHORISED])

    def test_the_decision_is_deterministic_and_carries_no_default_role(self):
        first = self._resolve(AUTHORISED_KIND, AUTHORISING_ROLE)
        second = self._resolve(AUTHORISED_KIND, AUTHORISING_ROLE)
        self.assertEqual(first, second)
        self.assertNotIn("model-coordination", repr(first))

    def test_the_refusals_are_ascii_so_a_windows_console_shows_them_whole(self):
        for resolve in (
            lambda: self._resolve(
                AUTHORISED_KIND, AUTHORISING_ROLE, composed=self.illustrative
            ),
            lambda: self._resolve(
                AUTHORISED_KIND, AUTHORISING_ROLE, cited_kind=OTHER_AUTHORISED_KIND
            ),
            lambda: self._resolve("not-a-resolution-kind", AUTHORISING_ROLE),
        ):
            with self.assertRaises(PurposeAssessmentError) as caught:
                resolve()
            str(caught.exception).encode("ascii")


class TheAsymmetryWithTeamMappingIsDeliberateTests(unittest.TestCase):
    """Why this gate fires on consumption where §4.3's fires on the request.

    Staffing is a question every non-`READY` record must answer: the assignment
    sentence is written whichever leaf is reached, so founding it on a
    demonstration row asserts a staffing decision nobody made. Authorisation is
    not like that. A `CONDITIONAL` must originate in a named authorisation event
    (Framework invariant 6), and *the event not having happened* is the normal
    case — Checkpoint B §3's live conclusion is that no activity in that handover
    is `CONDITIONAL`.

    Reverse the two and the consequence is measurable, which is what this class
    measures: a `team_mapping`-shaped static gate over `risk_authorisations`
    would stop `pcert-sample` producing even one `BLOCKED` row, because nobody is
    authorised to release a missing asset identity. The gate would suppress the
    refusals instead of the releases, and the safety direction would be exactly
    inverted.
    """

    @classmethod
    def setUpClass(cls):
        cls.pack = load_purpose_pack(fx.PACK_PATH)
        cls.overlay = load_project_overlay(PCERT_MANIFEST)
        cls.facts = fx.assessment_facts()
        cls.record = assess_purpose(
            request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=cls.facts),
            composed=fx.fixture_composed(),
            facts=cls.facts,
            determinations=fx.fixture_determinations(facts=cls.facts),
        )

    def _reachable_kinds(self) -> set[str]:
        kinds: set[str] = set()
        for activity in self.pack.activities:
            seen: set[str] = set()
            frontier = [activity.decision_root_node]
            while frontier:
                node_id = frontier.pop()
                if node_id in seen:
                    continue
                seen.add(node_id)
                for branch in self.pack.node(node_id).branches:
                    if branch.is_leaf:
                        if branch.resolution_kind:
                            kinds.add(branch.resolution_kind)
                    elif branch.next_node:
                        frontier.append(branch.next_node)
        return kinds

    def test_a_static_gate_would_cover_ten_kinds_and_the_project_authorises_two(self):
        reachable = self._reachable_kinds()
        authorised = {
            row.resolution_kind
            for row in self.overlay.risk_authorisations
            if row.pack_id == PACK_ID
        }
        self.assertEqual(len(reachable), 10)
        self.assertEqual(len(authorised & reachable), 2)
        self.assertEqual(len(reachable - authorised), 8)

    def test_a_static_gate_would_suppress_blocked_rows_this_project_can_produce(self):
        """The reversal, measured rather than argued.

        A `team_mapping`-shaped gate refuses the **request** when any reachable
        non-`READY` leaf lands on a row that is missing or illustrative. Eight of
        the ten reachable kinds have no row at all and the other two read
        `illustrative`, so such a gate refuses every request `pcert-sample` could
        make — and every `BLOCKED` row below, which exists today, would never be
        assessed. The rule meant to stop an unauthorised release would instead
        stop the project saying that the work is blocked.

        The sharper half is the last assertion: one of those `BLOCKED` rows
        resolves through a kind nobody is authorised to release at all, so even a
        per-leaf static gate — a weaker one than §4.3's — would suppress it.
        """

        decided = {
            row.resolution_kind
            for row in self.overlay.risk_authorisations
            if row.pack_id == PACK_ID and row.decision_basis == "project-decision"
        }
        self.assertEqual(decided, set(), "pcert-sample has decided no authorisation")
        blocked = [
            subscope.resolution_kind
            for activity in self.record.activities
            for subscope in activity.subscopes
            if subscope.verdict == "BLOCKED"
        ]
        self.assertTrue(blocked)
        self.assertEqual([kind for kind in blocked if kind in decided], [])

        covered = {
            row.resolution_kind
            for row in self.overlay.risk_authorisations
            if row.pack_id == PACK_ID
        }
        self.assertIn(UNAUTHORISED_BLOCKED_KIND, blocked)
        self.assertNotIn(UNAUTHORISED_BLOCKED_KIND, covered)

    def test_the_project_still_produces_those_blocked_rows_today(self):
        """Because the gate this round adds is not static, and is reached by nothing."""

        verdicts = {
            subscope.verdict
            for activity in self.record.activities
            for subscope in activity.subscopes
        }
        self.assertEqual(verdicts, {"READY", "BLOCKED", "UNKNOWN"})


class OrdinaryAssessmentIsUnmovedTests(unittest.TestCase):
    """Counterexample 6: not one byte of ordinary assessment behaviour moved.

    The digests below were computed on `669307e`, this branch's base, before any
    file in this round was written. They are here rather than in a comment
    because "unchanged" asserted is not "unchanged" proved.
    """

    #: `assess_purpose` over the fixture, all three activities, as of `669307e`.
    BASE_ASSESSMENT_DIGEST = (
        "aef0bd066b87a71521c7908cbebe7bc19283781420e6f7435af7fff0d1cb53de"
    )
    #: `fixture_composed()`'s composition digest, as of `669307e`.
    BASE_COMPOSITION_DIGEST = (
        "2b3d9af14f7b4bb87fdb9ffdf41b2d8674650c0895a7b585d48871348ddb237e"
    )
    #: Every subscope the fixture reaches, as of `669307e`.
    BASE_SUBSCOPES = (
        ("builders-work-openings", 1, "READY", ""),
        ("builders-work-openings", 2, "UNKNOWN", "penetration-not-determined"),
        ("builders-work-openings", 3, "READY", ""),
        ("builders-work-openings", 4, "BLOCKED", "missing-corresponding-opening"),
        ("ceiling-and-bulkhead-geometry", 1, "UNKNOWN", "in-model-position-not-evaluated"),
        ("ceiling-and-bulkhead-geometry", 2, "READY", ""),
        ("schedules-and-room-data-sheets", 1, "UNKNOWN", "asset-identity-not-evaluated"),
        ("schedules-and-room-data-sheets", 2, "BLOCKED", "missing-project-asset-identity"),
    )

    @classmethod
    def setUpClass(cls):
        cls.facts = fx.assessment_facts()
        cls.composed = fx.fixture_composed()
        cls.record = assess_purpose(
            request=fx.fixture_request(activity_ids=ALL_ACTIVITIES, facts=cls.facts),
            composed=cls.composed,
            facts=cls.facts,
            determinations=fx.fixture_determinations(facts=cls.facts),
        )

    def test_the_sealed_record_still_hashes_to_the_same_digest(self):
        self.assertEqual(self.record.assessment_digest, self.BASE_ASSESSMENT_DIGEST)

    def test_the_composed_configuration_still_hashes_to_the_same_digest(self):
        self.assertEqual(self.composed.composition_digest, self.BASE_COMPOSITION_DIGEST)

    def test_every_verdict_and_resolution_kind_is_where_it_was(self):
        observed = tuple(
            (
                activity.activity_ref.split("::", 1)[1],
                subscope.ordinal,
                subscope.verdict,
                subscope.resolution_kind,
            )
            for activity in self.record.activities
            for subscope in activity.subscopes
        )
        self.assertEqual(sorted(observed), sorted(self.BASE_SUBSCOPES))

    def test_the_shipped_project_is_still_refused_by_the_team_mapping_gate_alone(self):
        """No new reason, and not a new reason wearing the old code.

        `pcert-sample`'s risk-authorisation rows are illustrative too, so an
        implementation that gated them on the request would refuse here with a
        different code — and, worse, would refuse a request that has no promotion
        in it at all.
        """

        composed = compose_purpose_inputs(
            project_id="pcert-sample",
            overlay=load_project_overlay(PCERT_MANIFEST),
            packs=(load_purpose_pack(fx.PACK_PATH),),
            requirement_keys_by_ruleset=fx.requirement_keys_by_ruleset(),
        )
        with self.assertRaises(PurposeAssessmentError) as caught:
            assess_purpose(
                request=fx.fixture_request(
                    activity_ids=ALL_ACTIVITIES, facts=self.facts
                ),
                composed=composed,
                facts=self.facts,
            )
        self.assertEqual(
            caught.exception.code, "team-mapping-decision-basis-illustrative"
        )
        self.assertNotIn("risk_authorisations", str(caught.exception))


class NothingOnTheAssessmentPathReachesItTests(unittest.TestCase):
    """Consumption-triggered means no consumer, because no promotion exists yet."""

    #: Every module of the assessment package except the one under test and the
    #: package's own re-export surface.
    OTHER_MODULES = (
        "determinations.py",
        "evaluator.py",
        "facts.py",
        "reading.py",
        "recheck.py",
        "record.py",
        "request.py",
    )

    def test_the_module_exists_and_the_others_are_what_this_test_assumes(self):
        present = sorted(
            path.name
            for path in ASSESSMENT_PACKAGE.glob("*.py")
            if path.name != "__init__.py"
        )
        self.assertEqual(present, sorted(("authorisation.py", *self.OTHER_MODULES)))

    def test_no_other_assessment_module_imports_it(self):
        offenders = []
        for name in self.OTHER_MODULES:
            tree = ast.parse(
                (ASSESSMENT_PACKAGE / name).read_text(encoding="utf-8"), filename=name
            )
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and "authorisation" in (
                    node.module or ""
                ):
                    offenders.append(f"{name}: from {node.module}")
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if "authorisation" in alias.name:
                            offenders.append(f"{name}: import {alias.name}")
        self.assertEqual(offenders, [])

    def test_no_other_assessment_module_calls_it(self):
        offenders = []
        for name in self.OTHER_MODULES:
            tree = ast.parse(
                (ASSESSMENT_PACKAGE / name).read_text(encoding="utf-8"), filename=name
            )
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                function = node.func
                called = (
                    function.attr
                    if isinstance(function, ast.Attribute)
                    else getattr(function, "id", "")
                )
                if called == "resolve_risk_authorisation":
                    offenders.append(f"{name}: {called}()")
        self.assertEqual(offenders, [])

    def test_it_never_reads_a_routes_default_role(self):
        """The forbidden fallback is absent structurally, not merely untaken."""

        tree = ast.parse(
            (ASSESSMENT_PACKAGE / "authorisation.py").read_text(encoding="utf-8")
        )
        attributes = {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        for forbidden in ("default_role", "team_mapping", "resolution_routes"):
            with self.subTest(attribute=forbidden):
                self.assertNotIn(forbidden, attributes)

    def test_it_builds_no_promotion_and_no_successor(self):
        """The nine fields, the successor and the store are all still absent."""

        source = (ASSESSMENT_PACKAGE / "authorisation.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        defined = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.ClassDef, ast.FunctionDef))
        }
        for absent in (
            "Promotion",
            "PromotionRecord",
            "promote",
            "SuccessorSection",
            "accepted_risk",
            "release_scope",
            "voiding_condition",
        ):
            with self.subTest(name=absent):
                self.assertNotIn(absent, defined)
        self.assertNotIn("open(", source)
        self.assertNotIn("Path(", source)


class TheThreeIllustrativeGatesAreThreeCodesTests(unittest.TestCase):
    """One family, three tables, three rows a maintainer might have to edit."""

    CODES = (
        ("evaluator.py", "team-mapping-decision-basis-illustrative"),
        ("determinations.py", "accepted-method-decision-basis-illustrative"),
        ("authorisation.py", "risk-authorisation-decision-basis-illustrative"),
    )

    def test_each_gate_lives_in_its_own_module_with_its_own_code(self):
        sources = {
            name: (ASSESSMENT_PACKAGE / name).read_text(encoding="utf-8")
            for name, _ in self.CODES
        }
        for name, code in self.CODES:
            with self.subTest(code=code):
                self.assertIn(code, sources[name])
                for other, other_source in sources.items():
                    if other != name:
                        self.assertNotIn(code, other_source)

    def test_the_three_codes_are_distinct(self):
        codes = [code for _, code in self.CODES]
        self.assertEqual(len(set(codes)), 3)


class TheRulesHaveAHomeInTheADRsTests(unittest.TestCase):
    """Every rule above is written down where the next round will look for it.

    Four rounds have now caught a rule drifting away from the document that was
    supposed to govern it. A test is cheaper than a fifth.
    """

    @classmethod
    def setUpClass(cls):
        cls.adr0002 = (
            DECISIONS / "0002-minimal-purpose-pack-project-overlay.md"
        ).read_text(encoding="utf-8")
        cls.adr0003 = (
            DECISIONS / "0003-runtime-purpose-assessment-shape.md"
        ).read_text(encoding="utf-8")

    def test_adr_0003_records_all_three_answers_and_both_refusals(self):
        for fragment in (
            "risk-authorisation-decision-basis-illustrative",
            "risk-authorisation-kind-borrowed",
            "risk-authorisation-resolution-kind-unresolved",
            "no-authorisation-path",
            "role-not-authorised",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.adr0003)

    def test_adr_0002_records_the_illustrative_authorisation_row(self):
        self.assertIn(
            "overlay.risk_authorisations[]`, whose `decision_basis` is not",
            self.adr0002,
        )

    def test_both_adrs_say_the_asymmetry_with_team_mapping_is_deliberate(self):
        for name, text in (("0002", self.adr0002), ("0003", self.adr0003)):
            with self.subTest(adr=name):
                self.assertIn("asymmetry is deliberate", text)

    def test_adr_0003_records_that_open_point_2_is_not_closed(self):
        self.assertIn(
            "does not close the open point about §4.3's gate reading statically",
            self.adr0003,
        )

    def test_the_adrs_still_say_nothing_has_ever_been_produced(self):
        """The new rows do not turn a designed capability into a used one."""

        for text in (self.adr0002, self.adr0003):
            self.assertIn("Never used, and not usable on anything shipped here", text)
            self.assertIn("nothing ever produced from", text)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
