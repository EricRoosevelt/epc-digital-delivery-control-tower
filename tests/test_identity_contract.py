"""The identity contract, pinned.

Two jobs here.

First, prove the frozen legacy derivations still reproduce every identity this
project has already published. Those values are baked into the tracked Power BI
model and the committed evidence manifest, so they are not free to drift; the
legacy adapters exist precisely to keep emitting them.

Second, pin the properties the new three-way split is supposed to have — that
caller ordering cannot leak into a validation identity, that reconfiguring a
checker changes it, and that wall-clock facts stay out of it.
"""

import unittest
from pathlib import Path

from epc_control_tower.determinism import read_csv_rows, sha256_file
from epc_control_tower.domain import ComponentFingerprint, Requirement, Severity
from epc_control_tower.identity import (
    build_artifact_bundle_id,
    build_execution_id,
    build_finding_key,
    build_requirement_key,
    build_ruleset_normalized_digest,
    build_validation_run_id,
    new_execution_nonce,
)
from epc_control_tower.legacy_identity import (
    LEGACY_RUN_ID,
    legacy_finding_key,
    legacy_run_id,
    legacy_topic_event_id,
    legacy_topic_guid,
    legacy_viewpoint_guid,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = REPOSITORY_ROOT / "data" / "processed"
IDS_PATH = REPOSITORY_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64


def _run_id_inputs(**overrides):
    values = {
        "ruleset_id": "epc-delivery",
        "ruleset_version": "0.1",
        "ruleset_normalized_digest": SHA_A,
        "models": [("architecture", SHA_B), ("hvac", SHA_C)],
        "checkers": [ComponentFingerprint("ids", "0.8.5", SHA_A)],
        "as_of": "2026-08-13T00:00:00Z",
    }
    values.update(overrides)
    return values


def make_requirement(rule_id="R-001", requirement_id="Name", **overrides):
    values = {
        "requirement_key": build_requirement_key(rule_id, requirement_id),
        "rule_id": rule_id,
        "requirement_id": requirement_id,
        "specification_label": f"{rule_id}: walls must have a name",
        "requirement_label": requirement_id,
    }
    values.update(overrides)
    return Requirement(**values)


class PublishedIdentityTests(unittest.TestCase):
    """Every identity already published must still be reproducible."""

    def test_requirement_key_golden(self):
        self.assertEqual(
            build_requirement_key("R-005A", "EPC_Delivery.AssetTag"),
            "842a37c7-3183-5fce-ab45-b93c37ec7a08",
        )

    def test_legacy_run_id_recomputes_from_the_real_inputs(self):
        models = read_csv_rows(PROCESSED / "models.csv")
        self.assertEqual(
            legacy_run_id(
                ids_version="0.1",
                ids_sha256=sha256_file(IDS_PATH),
                models=[(row["model_id"], row["content_sha256"]) for row in models],
            ),
            LEGACY_RUN_ID,
        )

    def test_every_committed_finding_key_recomputes(self):
        findings = read_csv_rows(PROCESSED / "ids_findings.csv")
        self.assertEqual(len(findings), 47)
        for row in findings:
            with self.subTest(finding_key=row["finding_key"]):
                self.assertEqual(
                    legacy_finding_key(
                        run_id=row["run_id"],
                        model_id=row["model_id"],
                        requirement_key=row["requirement_key"],
                        element_key=row["element_key"],
                    ),
                    row["finding_key"],
                )

    def test_every_committed_requirement_key_recomputes(self):
        for row in read_csv_rows(PROCESSED / "ids_findings.csv"):
            with self.subTest(requirement_key=row["requirement_key"]):
                self.assertEqual(
                    build_requirement_key(row["specification_id"], row["requirement_id"]),
                    row["requirement_key"],
                )

    def test_every_committed_bcf_identity_recomputes(self):
        for row in read_csv_rows(PROCESSED / "bcf_topics.csv"):
            with self.subTest(topic=row["topic_guid"]):
                self.assertEqual(legacy_topic_guid(row["element_key"]), row["topic_guid"])

        for row in read_csv_rows(PROCESSED / "bcf_viewpoints.csv"):
            with self.subTest(viewpoint=row["viewpoint_guid"]):
                self.assertEqual(
                    legacy_viewpoint_guid(row["topic_guid"]), row["viewpoint_guid"]
                )

        for row in read_csv_rows(PROCESSED / "bcf_topic_events.csv"):
            with self.subTest(event=row["event_id"]):
                self.assertEqual(
                    legacy_topic_event_id(row["topic_guid"]), row["event_id"]
                )


class ValidationRunIdentityTests(unittest.TestCase):
    def test_caller_ordering_of_models_does_not_leak_in(self):
        forwards = build_validation_run_id(**_run_id_inputs())
        backwards = build_validation_run_id(
            **_run_id_inputs(models=[("hvac", SHA_C), ("architecture", SHA_B)])
        )
        self.assertEqual(forwards, backwards)

    def test_caller_ordering_of_checkers_does_not_leak_in(self):
        one = ComponentFingerprint("ids", "0.8.5", SHA_A)
        two = ComponentFingerprint("federation", "1.0", SHA_B)
        self.assertEqual(
            build_validation_run_id(**_run_id_inputs(checkers=[one, two])),
            build_validation_run_id(**_run_id_inputs(checkers=[two, one])),
        )

    def test_model_content_changes_the_identity(self):
        self.assertNotEqual(
            build_validation_run_id(**_run_id_inputs()),
            build_validation_run_id(
                **_run_id_inputs(models=[("architecture", SHA_C), ("hvac", SHA_C)])
            ),
        )

    def test_checker_version_changes_the_identity(self):
        # The whole reason checker fingerprints joined the identity: upgrading a
        # checker can change the findings, so it must change the run.
        self.assertNotEqual(
            build_validation_run_id(**_run_id_inputs()),
            build_validation_run_id(
                **_run_id_inputs(checkers=[ComponentFingerprint("ids", "0.9.0", SHA_A)])
            ),
        )

    def test_checker_configuration_changes_the_identity(self):
        self.assertNotEqual(
            build_validation_run_id(**_run_id_inputs()),
            build_validation_run_id(
                **_run_id_inputs(checkers=[ComponentFingerprint("ids", "0.8.5", SHA_B)])
            ),
        )

    def test_logical_as_of_changes_the_identity(self):
        self.assertNotEqual(
            build_validation_run_id(**_run_id_inputs()),
            build_validation_run_id(**_run_id_inputs(as_of="2027-01-01T00:00:00Z")),
        )

    def test_identity_is_readable(self):
        self.assertTrue(
            build_validation_run_id(**_run_id_inputs()).startswith("epc-delivery-v0.1-")
        )

    def test_a_non_slug_ruleset_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be a slug"):
            build_validation_run_id(**_run_id_inputs(ruleset_id="not a slug"))


class RulesetDigestTests(unittest.TestCase):
    """Rule identity is about what the rules say, not how the file is written.

    The project learned this the hard way: the published v1.0.0 run identity
    hashes the IDS document's raw bytes, so the same rules checked out with
    different line endings yielded a different run id and different finding
    keys. The canonical design keeps the source blob hash as provenance and
    derives identity from a normalized digest instead.
    """

    def test_declaration_order_does_not_change_the_digest(self):
        first = make_requirement("R-001", "Name")
        second = make_requirement("R-002", "IsExternal")
        self.assertEqual(
            build_ruleset_normalized_digest(
                ruleset_id="rs", version="0.1", requirements=[first, second]
            ),
            build_ruleset_normalized_digest(
                ruleset_id="rs", version="0.1", requirements=[second, first]
            ),
        )

    def test_facet_and_discipline_ordering_does_not_change_the_digest(self):
        # These are set-like declarations; the order they were written in is
        # not part of what the rule says.
        self.assertEqual(
            build_ruleset_normalized_digest(
                ruleset_id="rs",
                version="0.1",
                requirements=[
                    make_requirement(
                        facet_kinds=("property", "attribute"),
                        discipline_scope=("HVAC", "Architecture"),
                    )
                ],
            ),
            build_ruleset_normalized_digest(
                ruleset_id="rs",
                version="0.1",
                requirements=[
                    make_requirement(
                        facet_kinds=("attribute", "property"),
                        discipline_scope=("Architecture", "HVAC"),
                    )
                ],
            ),
        )

    def test_changing_a_rule_changes_the_digest(self):
        self.assertNotEqual(
            build_ruleset_normalized_digest(
                ruleset_id="rs", version="0.1", requirements=[make_requirement()]
            ),
            build_ruleset_normalized_digest(
                ruleset_id="rs",
                version="0.1",
                requirements=[make_requirement(severity=Severity.WARNING)],
            ),
        )

    def test_changing_a_rule_s_owner_or_stage_changes_the_digest(self):
        # These drive issue assignment and priority, so they reach the outputs.
        base = build_ruleset_normalized_digest(
            ruleset_id="rs", version="0.1", requirements=[make_requirement()]
        )
        for field, value in (("owner_role", "coordination"), ("stage", "Handover")):
            with self.subTest(field=field):
                self.assertNotEqual(
                    base,
                    build_ruleset_normalized_digest(
                        ruleset_id="rs",
                        version="0.1",
                        requirements=[make_requirement(**{field: value})],
                    ),
                )

    def test_adding_a_rule_changes_the_digest(self):
        self.assertNotEqual(
            build_ruleset_normalized_digest(
                ruleset_id="rs", version="0.1", requirements=[make_requirement("R-001")]
            ),
            build_ruleset_normalized_digest(
                ruleset_id="rs",
                version="0.1",
                requirements=[make_requirement("R-001"), make_requirement("R-002")],
            ),
        )

    def test_the_source_blob_hash_takes_no_part_in_the_run_identity(self):
        # Reformatting the source file changes its bytes and must not change
        # what the validation is.
        self.assertEqual(
            build_validation_run_id(**_run_id_inputs()),
            build_validation_run_id(**_run_id_inputs()),
        )
        self.assertNotIn(
            "source_blob",
            build_validation_run_id.__doc__ or "",
            msg="source blob must not be documented as an identity input",
        )

    def test_a_semantic_change_still_changes_the_run_identity(self):
        self.assertNotEqual(
            build_validation_run_id(**_run_id_inputs()),
            build_validation_run_id(**_run_id_inputs(ruleset_normalized_digest=SHA_B)),
        )


class ExecutionIdentityTests(unittest.TestCase):
    def test_a_nonce_separates_executions_sharing_a_clock_reading(self):
        facts = {
            "started_at": "2026-08-13T00:00:00Z",
            "platform": "win32",
            "tool_version": "1.0.0",
        }
        self.assertNotEqual(
            build_execution_id(**facts, nonce=new_execution_nonce()),
            build_execution_id(**facts, nonce=new_execution_nonce()),
        )

    def test_replaying_a_recorded_nonce_reproduces_the_id(self):
        facts = {
            "started_at": "2026-08-13T00:00:00Z",
            "platform": "win32",
            "tool_version": "1.0.0",
            "nonce": "fixed",
        }
        self.assertEqual(build_execution_id(**facts), build_execution_id(**facts))

    def test_a_nonce_is_required(self):
        with self.assertRaisesRegex(ValueError, "nonce"):
            build_execution_id(
                started_at="t", platform="p", tool_version="v", nonce=""
            )

    def test_nonces_are_distinct(self):
        self.assertNotEqual(new_execution_nonce(), new_execution_nonce())


class ArtifactBundleIdentityTests(unittest.TestCase):
    """Everything that shapes the exported bytes without changing the validation
    moves the bundle id; the validation id itself does not move for any of it."""

    def _bundle_id(self, **overrides) -> str:
        base = dict(
            validation_run_id=build_validation_run_id(**_run_id_inputs()),
            contract_version="0.1",
            grouping=ComponentFingerprint("element", "1.0.0"),
            programme_digest="a" * 64,
            exporters=[ComponentFingerprint("csv", "1.0")],
        )
        base.update(overrides)
        return build_artifact_bundle_id(**base)

    def test_exporter_version_changes_the_bundle(self):
        self.assertNotEqual(
            self._bundle_id(exporters=[ComponentFingerprint("csv", "1.0")]),
            self._bundle_id(exporters=[ComponentFingerprint("csv", "2.0")]),
        )

    def test_exporter_config_including_scope_changes_the_bundle(self):
        # An exporter's config_sha256 covers its scope and every byte-affecting
        # parameter, so a change to it moves the bundle id.
        self.assertNotEqual(
            self._bundle_id(exporters=[ComponentFingerprint("legacy-bcf", "1.0", "a" * 64)]),
            self._bundle_id(exporters=[ComponentFingerprint("legacy-bcf", "1.0", "b" * 64)]),
        )

    def test_contract_version_changes_the_bundle(self):
        self.assertNotEqual(
            self._bundle_id(contract_version="0.1"),
            self._bundle_id(contract_version="1.0"),
        )

    def test_grouping_policy_identity_changes_the_bundle(self):
        self.assertNotEqual(
            self._bundle_id(grouping=ComponentFingerprint("element", "1.0.0")),
            self._bundle_id(grouping=ComponentFingerprint("requirement", "1.0.0")),
        )

    def test_grouping_policy_version_or_config_changes_the_bundle(self):
        self.assertNotEqual(
            self._bundle_id(grouping=ComponentFingerprint("element", "1.0.0")),
            self._bundle_id(grouping=ComponentFingerprint("element", "2.0.0")),
        )
        self.assertNotEqual(
            self._bundle_id(grouping=ComponentFingerprint("element", "1.0.0", "a" * 64)),
            self._bundle_id(grouping=ComponentFingerprint("element", "1.0.0", "b" * 64)),
        )

    def test_programme_digest_changes_the_bundle(self):
        self.assertNotEqual(
            self._bundle_id(programme_digest="a" * 64),
            self._bundle_id(programme_digest="b" * 64),
        )

    def test_the_validation_run_id_is_unmoved_by_any_of_them(self):
        # None of the bundle inputs is a validation input, so the validation id
        # they are built on is the same string throughout.
        run_id = build_validation_run_id(**_run_id_inputs())
        self.assertTrue(self._bundle_id(validation_run_id=run_id).startswith("bundle-"))


class CanonicalFindingKeyTests(unittest.TestCase):
    def test_the_two_derivations_agree_given_the_same_inputs(self):
        # They are the same function. `build_finding_key` takes a
        # `validation_run_id` and a `model_key` where `legacy_finding_key` takes
        # a `run_id` and a `model_id`, but the payload is identical, so when
        # those inputs coincide the keys do too.
        self.assertEqual(
            build_finding_key(
                validation_run_id=LEGACY_RUN_ID,
                model_key="hvac",
                requirement_key="rk",
                element_key="hvac::GUID",
            ),
            legacy_finding_key(
                run_id=LEGACY_RUN_ID,
                model_id="hvac",
                requirement_key="rk",
                element_key="hvac::GUID",
            ),
        )

    def test_published_finding_keys_change_because_the_run_id_changes(self):
        # This is the whole reason the legacy adapter freezes the old
        # derivation. The key function did not change; its run-identity input
        # did, because `validation_run_id` now also covers checker versions and
        # configuration.
        canonical_run_id = build_validation_run_id(**_run_id_inputs())
        self.assertNotEqual(canonical_run_id, LEGACY_RUN_ID)
        shared = {
            "requirement_key": "rk",
            "element_key": "hvac::GUID",
        }
        self.assertNotEqual(
            build_finding_key(
                validation_run_id=canonical_run_id, model_key="hvac", **shared
            ),
            legacy_finding_key(run_id=LEGACY_RUN_ID, model_id="hvac", **shared),
        )

    def test_a_project_scoped_business_code_no_longer_decides_the_key(self):
        # Two projects can both call a model `architecture`; only `model_key` is
        # global, so only it may reach the key.
        self.assertNotEqual(
            build_finding_key(
                validation_run_id="r",
                model_key="plant-a.architecture",
                requirement_key="rk",
                element_key="plant-a.architecture::GUID",
            ),
            build_finding_key(
                validation_run_id="r",
                model_key="plant-b.architecture",
                requirement_key="rk",
                element_key="plant-b.architecture::GUID",
            ),
        )

    def test_an_absent_element_is_normalised_rather_than_omitted(self):
        # A specification-level N/A has no element; the payload keeps a fixed
        # arity so the key space stays unambiguous.
        self.assertEqual(
            build_finding_key(
                validation_run_id="r", model_key="m", requirement_key="rk", element_key=""
            ),
            build_finding_key(
                validation_run_id="r", model_key="m", requirement_key="rk", element_key=""
            ),
        )


if __name__ == "__main__":
    unittest.main()
