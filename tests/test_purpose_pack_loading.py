"""The shipped Pack loads, and every structural invariant actually refuses.

Two claims, and the second is the one worth the code. It is easy to write a
loader that accepts the one Pack in the repository, and easy to believe it
enforces eighteen invariants because eighteen functions exist. What proves it
is a broken Pack per invariant, each refused with its own code.

Every fixture is the *shipped* Pack with exactly one thing changed, so a test
that passes is a statement about the artifact this repository actually ships
rather than about a parallel one written to be convenient.
"""

from __future__ import annotations

import unittest

from epc_control_tower.purpose import (
    SUPPORTED_PACK_SCHEMA_VERSIONS,
    PurposePackError,
    discover_purpose_packs,
    load_purpose_pack,
    load_purpose_packs,
)
from helpers import PROJECT_ROOT, writable_test_directory
from purpose_fixtures import (
    PACK_PATH,
    base_pack_document,
    mutated,
    synthetic_leaf_gate_pack,
    synthetic_pair_pack,
    write_pack,
)

PACKS_DIR = PROJECT_ROOT / "purpose-packs"


def _node(document: dict, node_id: str) -> dict:
    for node in document["decision_nodes"]:
        if node["node_id"] == node_id:
            return node
    raise KeyError(node_id)


def _branch(document: dict, node_id: str, outcome: str) -> dict:
    for branch in _node(document, node_id)["branches"]:
        if branch["outcome"] == outcome:
            return branch
    raise KeyError(outcome)


def _requirement(document: dict, requirement_id: str) -> dict:
    for entry in document["evidence_requirements"]:
        if entry["evidence_requirement_id"] == requirement_id:
            return entry
    raise KeyError(requirement_id)


def _activity(document: dict, activity_id: str) -> dict:
    for entry in document["activities"]:
        if entry["activity_id"] == activity_id:
            return entry
    raise KeyError(activity_id)


class ShippedPackTests(unittest.TestCase):
    """What the repository actually ships, loaded and inspected."""

    @classmethod
    def setUpClass(cls):
        cls.pack = load_purpose_pack(PACK_PATH)

    def test_the_shipped_pack_loads(self):
        self.assertEqual(self.pack.pack_id, "interdisciplinary-coordination-readiness")
        self.assertEqual(self.pack.pack_schema_version, "1")
        self.assertEqual(self.pack.pack_version, "0.1.0")

    def test_discovery_finds_it_in_a_stable_order(self):
        found = discover_purpose_packs(PACKS_DIR)
        self.assertEqual(list(found), sorted(found))
        self.assertIn(PACK_PATH, found)
        self.assertEqual(len(load_purpose_packs(found)), len(found))

    def test_the_worked_pack_has_the_shape_the_adr_fixes(self):
        self.assertEqual(len(self.pack.directions), 1)
        self.assertEqual(len(self.pack.evidence_requirements), 5)
        self.assertEqual(len(self.pack.activities), 3)
        self.assertEqual(len(self.pack.resolution_routes), 10)
        self.assertEqual(len(self.pack.decision_nodes), 5)

    def test_ten_routes_stand_one_to_one_with_ten_non_ready_leaves(self):
        leaves = [
            branch
            for node in self.pack.decision_nodes
            for branch in node.branches
            if branch.is_leaf and branch.verdict != "READY"
        ]
        self.assertEqual(len(leaves), 10)
        kinds = sorted(branch.resolution_kind for branch in leaves)
        self.assertEqual(kinds, sorted(r.resolution_kind for r in self.pack.resolution_routes))
        self.assertEqual(len(set(kinds)), 10)

    def test_the_four_roles_the_routes_reach(self):
        """Six, one, two and one — not "coordination and MEP"."""

        counts: dict[str, int] = {}
        for route in self.pack.resolution_routes:
            counts[route.default_role] = counts.get(route.default_role, 0) + 1
        self.assertEqual(
            counts,
            {
                "model-coordination": 6,
                "architecture-lead": 2,
                "mep-lead": 1,
                "information-manager": 1,
            },
        )

    def test_insufficient_evidence_is_a_different_shape_from_a_binding(self):
        """R-010 is reachable only as a rule that *cannot* answer the question."""

        alignment = self.pack.evidence_requirement("cross-model-alignment")
        self.assertIsNone(alignment.pack_binding)
        self.assertEqual(len(alignment.insufficient_evidence), 1)
        reference = alignment.insufficient_evidence[0]
        self.assertEqual(reference.requirement_key, "acb11f11-bf18-5516-a6f2-21e451a6e410")
        self.assertIn("not alignment evidence", reference.cannot_answer)

        # And no evidence requirement carries R-010 as something that answers it.
        answering = {
            key
            for requirement in self.pack.evidence_requirements
            if requirement.pack_binding is not None
            for key in requirement.pack_binding.requirement_keys
        }
        self.assertNotIn("acb11f11-bf18-5516-a6f2-21e451a6e410", answering)

    def test_the_pair_grain_is_declared_with_its_source(self):
        opening = self.pack.evidence_requirement("opening-status")
        self.assertEqual(opening.subject_grain, "per-subject-pair")
        assert opening.pair_source is not None
        self.assertEqual(
            opening.pair_source.from_evidence_requirement_id, "penetration-determination"
        )
        self.assertEqual(opening.pair_source.on_outcome, "penetration-confirmed")

    def test_the_chimney_class_is_in_every_activity_subject_class_list(self):
        """The zero-finding element is what the list exists to keep in view."""

        for activity in self.pack.activities:
            with self.subTest(activity=activity.activity_id):
                self.assertIn("IfcChimney", activity.subject_classes)

    def test_no_branch_anywhere_reaches_conditional(self):
        verdicts = {
            branch.verdict
            for node in self.pack.decision_nodes
            for branch in node.branches
            if branch.verdict
        }
        self.assertEqual(verdicts, {"READY", "BLOCKED", "UNKNOWN"})


class SchemaVersionTests(unittest.TestCase):
    def test_an_unimplemented_schema_version_is_refused_not_downgraded(self):
        document = mutated(base_pack_document())
        document["pack_schema_version"] = "2"
        with writable_test_directory("pack-schema") as scratch:
            path = write_pack(scratch, document)
            with self.assertRaises(PurposePackError) as caught:
                load_purpose_pack(path)
        self.assertEqual(caught.exception.code, "pack-schema-version-unsupported")

    def test_format_one_is_the_published_format(self):
        self.assertEqual(SUPPORTED_PACK_SCHEMA_VERSIONS, frozenset({"1"}))


class PackFieldTests(unittest.TestCase):
    """Field-level refusals that are not numbered invariants."""

    def _refuses(self, document: dict, expected_code: str) -> None:
        with writable_test_directory("pack-field") as scratch:
            path = write_pack(scratch, document)
            with self.assertRaises(PurposePackError) as caught:
                load_purpose_pack(path)
        self.assertEqual(caught.exception.code, expected_code)

    def test_pack_id_must_match_its_directory(self):
        document = mutated(base_pack_document())
        with writable_test_directory("pack-dir") as scratch:
            path = write_pack(scratch, document, pack_id="somewhere-else")
            with self.assertRaises(PurposePackError) as caught:
                load_purpose_pack(path)
        self.assertEqual(caught.exception.code, "pack-id-directory-mismatch")

    def test_a_pack_version_that_is_not_a_slug_is_refused(self):
        document = mutated(base_pack_document())
        document["pack_version"] = ">=0.1,<0.2"
        self._refuses(document, "pack-version-invalid")

    def test_an_unknown_subject_grain_is_refused(self):
        document = mutated(base_pack_document())
        _requirement(document, "asset-identity")["subject_grain"] = "per-storey"
        self._refuses(document, "subject-grain-invalid")

    def test_a_wildcard_subject_class_is_refused(self):
        document = mutated(base_pack_document())
        _activity(document, "schedules-and-room-data-sheets")["subject_classes"] = ["all"]
        self._refuses(document, "subject-classes-invalid")

    def test_an_element_grained_activity_must_declare_subject_classes(self):
        document = mutated(base_pack_document())
        del _activity(document, "schedules-and-room-data-sheets")["subject_classes"]
        self._refuses(document, "subject-classes-required")

    def test_an_activity_naming_an_undeclared_direction_is_refused(self):
        document = mutated(base_pack_document())
        _activity(document, "schedules-and-room-data-sheets")["direction_id"] = "nowhere"
        self._refuses(document, "activity-direction-unresolved")

    def test_a_branch_carrying_both_verdict_and_next_node_is_refused(self):
        document = mutated(base_pack_document())
        branch = _branch(document, "asset-identity-node", "satisfied")
        branch["next_node"] = "asset-identity-node"
        self._refuses(document, "branch-shape-invalid")

    def test_a_blocked_leaf_without_a_failure_kind_is_refused(self):
        document = mutated(base_pack_document())
        del _branch(document, "asset-identity-node", "unmet")["failure_kind"]
        self._refuses(document, "branch-kind-mismatch")

    def test_a_leaf_whose_kind_matches_no_route_is_refused(self):
        document = mutated(base_pack_document())
        _branch(document, "asset-identity-node", "unmet")["failure_kind"] = "invented-kind"
        self._refuses(document, "leaf-resolution-kind-unmatched")

    def test_an_uncovered_outcome_is_refused(self):
        document = mutated(base_pack_document())
        node = _node(document, "asset-identity-node")
        node["branches"] = [b for b in node["branches"] if b["outcome"] != "not-yet-evaluated"]
        self._refuses(document, "branch-outcome-coverage")

    def test_a_duplicate_resolution_kind_is_refused(self):
        document = mutated(base_pack_document())
        document["resolution_routes"].append(dict(document["resolution_routes"][0]))
        self._refuses(document, "route-resolution-kind-duplicate")

    def test_an_orphaned_route_is_refused(self):
        document = mutated(base_pack_document())
        document["resolution_routes"].append(
            {
                "resolution_kind": "nobody-reaches-this",
                "default_role": "model-coordination",
                "consequence_kinds": ["work-suspended"],
                "next_action": "x",
                "recheck_condition": "y",
            }
        )
        self._refuses(document, "route-orphaned")

    def test_an_insufficient_evidence_entry_must_say_what_it_cannot_answer(self):
        """Without the sentence it is indistinguishable from a binding."""

        document = mutated(base_pack_document())
        del _requirement(document, "cross-model-alignment")["insufficient_evidence"][0][
            "cannot_answer"
        ]
        self._refuses(document, "pack-field-missing")

    def test_a_pack_binding_on_an_overlay_bound_requirement_is_refused(self):
        """A Pack may not answer a question it declared the project owns."""

        document = mutated(base_pack_document())
        _requirement(document, "asset-identity")["pack_binding"] = {
            "ruleset_id": "epc-delivery",
            "ruleset_version": "2.2",
            "requirement_keys": ["842a37c7-3183-5fce-ab45-b93c37ec7a08"],
        }
        self._refuses(document, "pack-binding-unexpected")


class StructuralInvariantTests(unittest.TestCase):
    """One broken Pack per numbered invariant of ADR 0002 §3.8."""

    def _refuses(self, document: dict, number: int) -> None:
        with writable_test_directory(f"pack-inv-{number:02d}") as scratch:
            path = write_pack(scratch, document)
            with self.assertRaises(PurposePackError) as caught:
                load_purpose_pack(path)
        self.assertEqual(caught.exception.code, f"pack-invariant-{number:02d}")

    def test_01_root_node_must_exist(self):
        document = mutated(base_pack_document())
        _activity(document, "schedules-and-room-data-sheets")["decision_root_node"] = "absent"
        self._refuses(document, 1)

    def test_02_next_node_must_exist(self):
        document = mutated(base_pack_document())
        _branch(document, "in-model-position-node", "satisfied")["next_node"] = "absent"
        self._refuses(document, 2)

    def test_03_node_id_is_unique(self):
        document = mutated(base_pack_document())
        document["decision_nodes"].append(mutated(_node(document, "asset-identity-node")))
        self._refuses(document, 3)

    def test_04_a_node_tests_a_declared_evidence_requirement(self):
        document = mutated(base_pack_document())
        _node(document, "asset-identity-node")["evidence_requirement_id"] = "absent"
        self._refuses(document, 4)

    def test_05_the_reachable_graph_is_acyclic(self):
        document = mutated(base_pack_document())
        branch = _branch(document, "opening-status-node", "not-yet-determined")
        branch.pop("verdict", None)
        branch.pop("gap_kind", None)
        branch["next_node"] = "penetration-determination-node"
        self._refuses(document, 5)

    def test_06_a_tree_tests_only_its_own_activitys_evidence(self):
        document = mutated(base_pack_document())
        branch = _branch(document, "asset-identity-node", "satisfied")
        branch.pop("verdict", None)
        branch["next_node"] = "smuggled-node"
        document["decision_nodes"].append(
            {
                "node_id": "smuggled-node",
                "evidence_requirement_id": "in-model-position",
                "branches": [
                    {"outcome": "satisfied", "verdict": "READY"},
                    {
                        "outcome": "unmet",
                        "verdict": "BLOCKED",
                        "failure_kind": "mep-element-not-spatially-assigned",
                    },
                    {
                        "outcome": "not-yet-evaluated",
                        "verdict": "UNKNOWN",
                        "gap_kind": "in-model-position-not-evaluated",
                    },
                ],
            }
        )
        self._refuses(document, 6)

    def test_07_no_node_is_dangling(self):
        document = mutated(base_pack_document())
        document["decision_nodes"].append(
            {
                "node_id": "unreachable-node",
                "evidence_requirement_id": "asset-identity",
                "branches": [
                    {"outcome": "satisfied", "verdict": "READY"},
                    {
                        "outcome": "unmet",
                        "verdict": "BLOCKED",
                        "failure_kind": "missing-project-asset-identity",
                    },
                    {
                        "outcome": "not-yet-evaluated",
                        "verdict": "UNKNOWN",
                        "gap_kind": "asset-identity-not-evaluated",
                    },
                ],
            }
        )
        self._refuses(document, 7)

    def test_08_every_declared_evidence_requirement_is_tested(self):
        document = mutated(base_pack_document())
        _activity(document, "schedules-and-room-data-sheets")["evidence_requirement_ids"] = [
            "asset-identity",
            "cross-model-alignment",
        ]
        self._refuses(document, 8)

    def test_09_conditional_is_not_a_legal_leaf(self):
        document = mutated(base_pack_document())
        branch = _branch(document, "asset-identity-node", "unmet")
        branch["verdict"] = "CONDITIONAL"
        self._refuses(document, 9)

    def test_10_a_non_root_node_has_exactly_one_incoming_edge(self):
        document = mutated(base_pack_document())
        branch = _branch(document, "in-model-position-node", "unmet")
        branch.pop("verdict", None)
        branch.pop("failure_kind", None)
        branch["next_node"] = "cross-model-alignment-node"
        self._refuses(document, 10)

    def test_11_no_node_is_shared_between_two_activities(self):
        document = mutated(base_pack_document())
        branch = _branch(document, "penetration-determination-node", "not-yet-determined")
        branch.pop("verdict", None)
        branch.pop("gap_kind", None)
        branch["next_node"] = "cross-model-alignment-node"
        self._refuses(document, 11)

    def test_12_a_ready_path_accounts_for_the_whole_declared_set(self):
        document = mutated(base_pack_document())
        del _branch(document, "penetration-determination-node", "no-penetration")[
            "renders_inapplicable"
        ]
        self._refuses(document, 12)

    def test_13_renders_inapplicable_has_no_duplicates(self):
        document = mutated(base_pack_document())
        _branch(document, "penetration-determination-node", "no-penetration")[
            "renders_inapplicable"
        ] = ["opening-status", "opening-status"]
        self._refuses(document, 13)

    def test_14_a_branch_never_renders_its_own_requirement_inapplicable(self):
        document = mutated(base_pack_document())
        _branch(document, "penetration-determination-node", "no-penetration")[
            "renders_inapplicable"
        ] = ["penetration-determination"]
        self._refuses(document, 14)

    def test_15_no_descendant_retests_evidence_an_ancestor_ruled_out(self):
        document = mutated(base_pack_document())
        _branch(document, "penetration-determination-node", "penetration-confirmed")[
            "renders_inapplicable"
        ] = ["opening-status"]
        self._refuses(document, 15)

    def test_16_pair_source_is_declared_with_the_pair_grain_and_not_otherwise(self):
        document = mutated(base_pack_document())
        _requirement(document, "opening-status")["subject_grain"] = "per-subject"
        self._refuses(document, 16)

    def test_17_a_pair_grained_node_is_reachable_only_below_its_source(self):
        with writable_test_directory("pack-inv-17") as scratch:
            path = write_pack(scratch, synthetic_pair_pack())
            with self.assertRaises(PurposePackError) as caught:
                load_purpose_pack(path)
        self.assertEqual(caught.exception.code, "pack-invariant-17")

    def test_18_the_pair_sources_outcome_branch_is_never_a_leaf(self):
        with writable_test_directory("pack-inv-18") as scratch:
            path = write_pack(scratch, synthetic_leaf_gate_pack())
            with self.assertRaises(PurposePackError) as caught:
                load_purpose_pack(path)
        self.assertEqual(caught.exception.code, "pack-invariant-18")

    def test_every_invariant_number_is_covered_by_a_test(self):
        """The eighteen are eighteen, and none is quietly unexercised."""

        covered = {
            int(name.split("_")[1])
            for name in dir(self)
            if name.startswith("test_") and name.split("_")[1].isdigit()
        }
        self.assertEqual(covered, set(range(1, 19)))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
