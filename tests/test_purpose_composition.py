"""The Overlay composes with the Pack, and every missing input refuses.

The interesting tests here are the three that assert an absence: no fallback to
R-005, no fallback to a rule's ``owner_role``, and no range match on
``pack_version``. Each has an implementation that would "work" — and each would
turn a project's missing decision into a decision the software made on its
behalf, which is the failure mode ADR 0002 §3.7 exists to prevent.

The other thing asserted here is what the composed object *cannot* say. A
configuration object that could hold a verdict is a place for a per-run answer
to be filed as a project setting, so the test walks the type and proves there is
nowhere to put one.
"""

from __future__ import annotations

import dataclasses
import tomllib
import unittest

from epc_control_tower.purpose import (
    DECISION_BASES,
    PurposeCompositionError,
    compose_purpose_inputs,
    load_project_overlay,
    load_purpose_pack,
    read_overlay_table,
)
from helpers import PROJECT_ROOT, writable_test_directory
from purpose_fixtures import (
    PACK_PATH,
    base_overlay_document,
    base_pack_document,
    mutated,
    render_project_with_overlay,
    write_pack,
)

PCERT_MANIFEST = PROJECT_ROOT / "projects" / "pcert-sample" / "project.toml"
ISO_MANIFEST = PROJECT_ROOT / "projects" / "iso-reference-view" / "project.toml"

#: The rule set the shipped bindings pin, as the loader would be handed it.
RULESET_ADDRESS = ("epc-delivery", "2.2")


def _requirement_keys() -> dict[tuple[str, str], frozenset[str]]:
    """The requirement keys of the rule set that is actually loaded."""

    from epc_control_tower.rule_definitions import compile_document, load_rule_definitions

    definition = load_rule_definitions(PROJECT_ROOT / "rules" / "epc-delivery")
    _, ruleset, _ = compile_document(definition)
    return {
        (ruleset.ruleset_id, ruleset.version): frozenset(
            requirement.requirement_key for requirement in ruleset.requirements
        )
    }


def _compose(overlay, packs=None, keys=None, project_id="pcert-sample"):
    return compose_purpose_inputs(
        project_id=project_id,
        overlay=overlay,
        packs=packs if packs is not None else (load_purpose_pack(PACK_PATH),),
        requirement_keys_by_ruleset=keys if keys is not None else _requirement_keys(),
        source=PCERT_MANIFEST,
    )


def _overlay_from(document: dict):
    with writable_test_directory("overlay") as scratch:
        path = scratch / "project.toml"
        path.write_text(render_project_with_overlay(document), encoding="utf-8")
        with path.open("rb") as stream:
            return read_overlay_table(tomllib.load(stream), path)


def _overlay_row(document: dict, table: str, index: int = 0) -> dict:
    return document["overlay"][table][index]


class ShippedOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.overlay = load_project_overlay(PCERT_MANIFEST)
        cls.composed = _compose(cls.overlay)

    def test_the_shipped_project_composes(self):
        self.assertEqual(self.composed.project_id, "pcert-sample")
        self.assertEqual(len(self.composed.packs), 1)
        self.assertEqual(
            self.composed.pack("interdisciplinary-coordination-readiness").pack_version,
            "0.1.0",
        )

    def test_all_four_roles_the_routes_reach_are_staffed(self):
        """Two of the ten routes would otherwise have no resolvable assignee."""

        self.assertEqual(
            sorted(item.role for item in self.overlay.team_mapping),
            ["architecture-lead", "information-manager", "mep-lead", "model-coordination"],
        )

    def test_every_policy_row_declares_its_basis_and_this_project_has_no_decisions(self):
        rows = (
            list(self.overlay.team_mapping)
            + list(self.overlay.risk_authorisations)
            + list(self.overlay.accepted_evidence_methods)
        )
        self.assertEqual(len(rows), 9)
        for row in rows:
            with self.subTest(row=row):
                self.assertIn(row.decision_basis, DECISION_BASES)
                self.assertEqual(row.decision_basis, "illustrative")

    def test_the_basis_reaches_the_composed_object(self):
        bases = {item.decision_basis for item in self.composed.overlay.team_mapping}
        self.assertEqual(bases, {"illustrative"})

    def test_bindings_and_conventions_carry_no_basis(self):
        """They state facts about a rule set, not policy anyone decided."""

        for row in list(self.overlay.evidence_bindings) + list(self.overlay.conventions):
            with self.subTest(row=row):
                self.assertFalse(hasattr(row, "decision_basis"))

    def test_r005_enters_only_through_the_overlay(self):
        binding = self.overlay.evidence_bindings[0]
        self.assertEqual(binding.evidence_requirement_id, "asset-identity")
        self.assertEqual(len(binding.requirement_keys), 4)
        pack_text = PACK_PATH.read_text(encoding="utf-8")
        for key in binding.requirement_keys:
            with self.subTest(key=key):
                self.assertNotIn(key, pack_text)
        self.assertNotIn("R-005", pack_text)

    def test_only_two_of_ten_kinds_have_an_authorisation_path(self):
        """A kind with no row has no path to CONDITIONAL — not a default one."""

        authorised = {item.resolution_kind for item in self.overlay.risk_authorisations}
        self.assertEqual(
            authorised,
            {"cross-model-alignment-not-confirmed", "missing-project-asset-identity"},
        )
        self.assertNotIn("cross-model-misalignment", authorised)


class NoFallbackTests(unittest.TestCase):
    """Three refusals whose plausible fallback would be a fabricated decision."""

    def test_a_missing_evidence_binding_never_falls_back_to_r005(self):
        document = mutated(base_overlay_document())
        document["overlay"]["evidence_bindings"] = []
        overlay = _overlay_from(document)
        with self.assertRaises(PurposeCompositionError) as caught:
            _compose(overlay)
        self.assertEqual(caught.exception.code, "evidence-binding-missing")
        self.assertIn("no default", str(caught.exception))

    def test_a_missing_team_mapping_never_falls_back_to_owner_role(self):
        """``owner_role`` is what a rule author expected, not who this project tasks."""

        document = mutated(base_overlay_document())
        document["overlay"]["team_mapping"] = [
            row
            for row in document["overlay"]["team_mapping"]
            if row["role"] != "architecture-lead"
        ]
        overlay = _overlay_from(document)
        with self.assertRaises(PurposeCompositionError) as caught:
            _compose(overlay)
        self.assertEqual(caught.exception.code, "team-mapping-role-missing")
        self.assertIn("owner_role", str(caught.exception))

        # And the role really is one a rule declares, so a fallback would have
        # silently succeeded rather than obviously failed.
        rules = (PROJECT_ROOT / "rules" / "epc-delivery" / "R-001.toml").read_text(
            encoding="utf-8"
        )
        self.assertIn('owner_role = "architecture-lead"', rules)

    def test_pack_version_is_matched_exactly_and_never_as_a_range(self):
        document = mutated(base_overlay_document())
        document["overlay"]["packs"][0]["pack_version"] = "0.1"
        overlay = _overlay_from(document)
        with self.assertRaises(PurposeCompositionError) as caught:
            _compose(overlay)
        self.assertEqual(caught.exception.code, "pack-version-mismatch")


class CompositionRefusalTests(unittest.TestCase):
    """One refusal per remaining ADR 0002 §3.7 / ADR 0003 §7.1 row."""

    def _refuses(self, document: dict, expected_code: str, **kwargs) -> None:
        # Some rows are refused while reading the table and some while
        # composing it against a Pack. Both are refusals, and which phase
        # catches a given row is an implementation detail this test is not
        # about.
        with self.assertRaises(PurposeCompositionError) as caught:
            _compose(_overlay_from(document), **kwargs)
        self.assertEqual(caught.exception.code, expected_code)

    def test_a_project_with_no_overlay_is_refused_for_the_request_only(self):
        with self.assertRaises(PurposeCompositionError) as caught:
            _compose(None)
        self.assertEqual(caught.exception.code, "overlay-missing")
        self.assertIn("not a pipeline error", str(caught.exception))

    def test_reading_a_manifest_without_an_overlay_is_not_an_error(self):
        self.assertIsNone(load_project_overlay(ISO_MANIFEST))

    def test_a_pack_the_library_does_not_hold_is_refused(self):
        document = mutated(base_overlay_document())
        document["overlay"]["packs"][0]["pack_id"] = "not-a-pack"
        self._refuses(document, "overlay-pack-not-found")

    def test_a_missing_accepted_method_is_refused(self):
        document = mutated(base_overlay_document())
        document["overlay"]["accepted_evidence_methods"] = [
            row
            for row in document["overlay"]["accepted_evidence_methods"]
            if row["evidence_requirement_id"] != "opening-status"
        ]
        self._refuses(document, "accepted-method-missing")

    def test_a_binding_pinned_to_another_ruleset_version_is_refused(self):
        document = mutated(base_overlay_document())
        _overlay_row(document, "evidence_bindings")["ruleset_version"] = "2.1"
        self._refuses(document, "binding-ruleset-mismatch")

    def test_a_binding_naming_an_absent_requirement_key_is_refused(self):
        document = mutated(base_overlay_document())
        _overlay_row(document, "evidence_bindings")["requirement_keys"] = [
            "00000000-0000-5000-8000-000000000000"
        ]
        self._refuses(document, "binding-requirement-key-unknown")

    def test_a_pack_binding_naming_an_absent_key_is_refused_too(self):
        """The Pack's own binding gets the same check as the Overlay's."""

        keys = {RULESET_ADDRESS: frozenset({"842a37c7-3183-5fce-ab45-b93c37ec7a08"})}
        overlay = load_project_overlay(PCERT_MANIFEST)
        with self.assertRaises(PurposeCompositionError) as caught:
            _compose(overlay, keys=keys)
        self.assertEqual(caught.exception.code, "binding-requirement-key-unknown")

    def test_an_insufficient_evidence_reference_is_checked_as_hard_as_a_binding(self):
        """R-010's key must resolve, and it is still not a binding."""

        document = mutated(base_pack_document())
        for entry in document["evidence_requirements"]:
            for reference in entry.get("insufficient_evidence", []):
                reference["requirement_key"] = "00000000-0000-5000-8000-000000000000"
        with writable_test_directory("insufficient") as scratch:
            pack = load_purpose_pack(write_pack(scratch, document))
        overlay = load_project_overlay(PCERT_MANIFEST)
        with self.assertRaises(PurposeCompositionError) as caught:
            _compose(overlay, packs=(pack,))
        self.assertEqual(caught.exception.code, "binding-requirement-key-unknown")
        self.assertIn("insufficient_evidence", str(caught.exception))

    def test_a_duplicate_team_mapping_role_is_refused(self):
        document = mutated(base_overlay_document())
        document["overlay"]["team_mapping"].append(
            dict(document["overlay"]["team_mapping"][0])
        )
        self._refuses(document, "team-mapping-role-duplicate")

    def test_a_wildcard_authoriser_is_refused(self):
        document = mutated(base_overlay_document())
        _overlay_row(document, "risk_authorisations")["may_authorise_roles"] = ["all"]
        self._refuses(document, "risk-authorisation-roles-unbounded")

    def test_an_empty_authoriser_list_is_refused(self):
        document = mutated(base_overlay_document())
        _overlay_row(document, "risk_authorisations")["may_authorise_roles"] = []
        self._refuses(document, "risk-authorisation-roles-unbounded")

    def test_an_authorisation_for_an_unknown_kind_is_refused(self):
        document = mutated(base_overlay_document())
        _overlay_row(document, "risk_authorisations")["resolution_kind"] = "invented"
        self._refuses(document, "risk-authorisation-kind-unresolved")

    def test_a_duplicate_pack_reference_is_refused(self):
        document = mutated(base_overlay_document())
        document["overlay"]["packs"].append(dict(document["overlay"]["packs"][0]))
        self._refuses(document, "overlay-pack-duplicate")

    def test_a_binding_addressing_no_declared_requirement_is_refused(self):
        document = mutated(base_overlay_document())
        spurious = dict(_overlay_row(document, "evidence_bindings"))
        spurious["evidence_requirement_id"] = "invented"
        document["overlay"]["evidence_bindings"].append(spurious)
        self._refuses(document, "evidence-binding-unresolved")


class DecisionBasisTests(unittest.TestCase):
    """A policy row with no stated standing is refused, not defaulted."""

    def _refuses(self, document: dict, expected_code: str) -> None:
        with self.assertRaises(PurposeCompositionError) as caught:
            _overlay_from(document)
        self.assertEqual(caught.exception.code, expected_code)

    def test_a_team_mapping_row_without_a_basis_is_refused(self):
        document = mutated(base_overlay_document())
        del _overlay_row(document, "team_mapping")["decision_basis"]
        self._refuses(document, "decision-basis-missing")

    def test_a_risk_authorisation_row_without_a_basis_is_refused(self):
        document = mutated(base_overlay_document())
        del _overlay_row(document, "risk_authorisations")["decision_basis"]
        self._refuses(document, "decision-basis-missing")

    def test_an_accepted_method_row_without_a_basis_is_refused(self):
        document = mutated(base_overlay_document())
        del _overlay_row(document, "accepted_evidence_methods")["decision_basis"]
        self._refuses(document, "decision-basis-missing")

    def test_an_unrecognised_basis_is_refused(self):
        document = mutated(base_overlay_document())
        _overlay_row(document, "team_mapping")["decision_basis"] = "probably-real"
        self._refuses(document, "decision-basis-invalid")

    def test_a_project_decision_basis_is_accepted_when_a_project_states_one(self):
        """The other value is reachable; this project simply has no decisions."""

        document = mutated(base_overlay_document())
        _overlay_row(document, "team_mapping")["decision_basis"] = "project-decision"
        overlay = _overlay_from(document)
        self.assertIn(
            "project-decision", {item.decision_basis for item in overlay.team_mapping}
        )


class ComposedObjectBoundaryTests(unittest.TestCase):
    """The composed object has nowhere to put an answer.

    The distinction this class turns on: a ``Branch``'s ``verdict`` is *Pack
    data* — the tree's declared mapping from an outcome to a verdict, written
    by a Pack author and true of no project. A readiness answer is something
    else entirely: it is *reached*, for particular elements, against particular
    model versions. So the test is not "does the word verdict appear" but
    "could this object hold something a run produced".
    """

    #: Fields for things a runtime produces about one assessment of two named
    #: model versions. None of these may exist anywhere in the composed object.
    FORBIDDEN_FIELDS = (
        "reached",
        "reading",
        "subscope",
        "assigned",
        "assignee",
        "actual_actor",
        "promotion",
        "risk_accepted",
        "authoriser",
        "finding_key",
        "readiness",
        "determination",
    )

    #: A decision-tree branch carries exactly this, and nothing that could
    #: record which outcome a subject actually reached.
    BRANCH_FIELDS = {
        "outcome",
        "verdict",
        "failure_kind",
        "gap_kind",
        "next_node",
        "renders_inapplicable",
    }

    @classmethod
    def setUpClass(cls):
        cls.composed = _compose(load_project_overlay(PCERT_MANIFEST))

    def _field_names(self, value, seen=None):
        seen = seen if seen is not None else set()
        if not dataclasses.is_dataclass(value) or id(value) in seen:
            return set()
        seen.add(id(value))
        names = set()
        for field in dataclasses.fields(value):
            names.add(field.name)
            attribute = getattr(value, field.name)
            children = attribute if isinstance(attribute, tuple) else (attribute,)
            for child in children:
                names |= self._field_names(child, seen)
        return names

    def test_no_field_anywhere_can_hold_a_runtime_answer(self):
        names = self._field_names(self.composed)
        self.assertIn("composition_digest", names)
        for word in self.FORBIDDEN_FIELDS:
            with self.subTest(word=word):
                self.assertEqual(sorted(name for name in names if word in name), [])

    def test_a_branch_carries_a_declaration_and_not_a_result(self):
        branch = self.composed.packs[0].decision_nodes[0].branches[0]
        self.assertEqual({f.name for f in dataclasses.fields(branch)}, self.BRANCH_FIELDS)

    def test_the_composed_object_is_independent_of_any_model(self):
        """No element, no model version, no content hash reaches it."""

        from epc_control_tower.config import load_project_manifest

        manifest = load_project_manifest(PCERT_MANIFEST, repository_root=PROJECT_ROOT)
        rendered = repr(self.composed)
        for model in manifest.models:
            with self.subTest(model=model.model_id):
                self.assertNotIn(model.content_sha256, rendered)
                self.assertNotIn(model.filename, rendered)

    def test_the_composed_object_exposes_no_resolved_assignment(self):
        """8a resolves through 8b as a *check*; 8c is not produced here."""

        public = {name for name in dir(self.composed) if not name.startswith("_")}
        for name in sorted(public):
            with self.subTest(attribute=name):
                self.assertNotIn("assign", name)
                self.assertNotIn("resolve", name)

    def test_default_role_and_team_mapping_stay_two_separate_facts(self):
        """Nothing joins them into a third value."""

        pack = self.composed.pack("interdisciplinary-coordination-readiness")
        roles = {route.default_role for route in pack.resolution_routes}
        staffed = {item.team_or_person for item in self.composed.overlay.team_mapping}
        self.assertTrue(roles.isdisjoint(staffed))


class CompositionDigestTests(unittest.TestCase):
    def test_the_digest_is_stable_across_loads(self):
        first = _compose(load_project_overlay(PCERT_MANIFEST)).composition_digest
        second = _compose(load_project_overlay(PCERT_MANIFEST)).composition_digest
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[0-9a-f]{64}$")

    def test_the_digest_hashes_meaning_and_not_file_bytes(self):
        """Reformatting a Pack must not change what the composition is."""

        baseline = _compose(load_project_overlay(PCERT_MANIFEST)).composition_digest
        document = mutated(base_pack_document())
        with writable_test_directory("reformat") as scratch:
            # The fixture renderer emits different bytes from the shipped file:
            # different comments, different spacing, different key order.
            path = write_pack(scratch, document)
            self.assertNotEqual(
                path.read_bytes(), PACK_PATH.read_bytes(), "fixture must differ in bytes"
            )
            reformatted = load_purpose_pack(path)
        composed = _compose(load_project_overlay(PCERT_MANIFEST), packs=(reformatted,))
        self.assertEqual(composed.composition_digest, baseline)

    def test_the_digest_moves_when_the_meaning_moves(self):
        baseline = _compose(load_project_overlay(PCERT_MANIFEST)).composition_digest
        document = mutated(base_pack_document())
        document["pack_version"] = "0.1.1"
        overlay_document = mutated(base_overlay_document())
        overlay_document["overlay"]["packs"][0]["pack_version"] = "0.1.1"
        with writable_test_directory("moved") as scratch:
            moved = load_purpose_pack(write_pack(scratch, document))
        composed = _compose(_overlay_from(overlay_document), packs=(moved,))
        self.assertNotEqual(composed.composition_digest, baseline)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
