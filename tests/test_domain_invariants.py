"""Invariants the domain model must refuse to violate.

These tests exist because a dataclass that merely holds fields is not a source
of truth. Each case below constructs a state that is meaningless in the problem
domain and asserts that it cannot be built at all — a `PASS` finding flagged as
an issue, an element whose key disagrees with its own model and GlobalId, an
event whose declared type contradicts its payload.
"""

import unittest

from epc_control_tower.domain import (
    Element,
    Finding,
    FindingStatus,
    Issue,
    IssueEvent,
    IssueState,
    Model,
    Project,
    Provenance,
    Requirement,
    RuleSet,
    Severity,
    StateChangedPayload,
    TopicCreatedPayload,
    derive_lifecycle_state,
    derive_model_key,
    make_element_key,
)

SHA_A = "a" * 64
SHA_B = "b" * 64


def make_finding(**overrides):
    values = {
        "finding_key": "fk",
        "validation_run_id": "run",
        "project_id": "proj",
        "model_key": "hvac",
        "element_key": "hvac::GUID",
        "requirement_key": "rk",
        "status": FindingStatus.PASS,
        "severity": Severity.INFO,
        "is_applicable": True,
        "is_issue": False,
    }
    values.update(overrides)
    return Finding(**values)


def make_event(**overrides):
    values = {
        "event_key": "ek",
        "issue_key": "ik",
        "sequence": 1,
        "occurred_at": "2026-08-13T00:00:00Z",
        "event_type": "topic_created",
        "from_state": None,
        "to_state": IssueState.OPEN,
        "actor_role": "control-tower",
        "payload_version": 1,
        "typed_payload": TopicCreatedPayload(finding_count=2, title="t"),
    }
    values.update(overrides)
    return IssueEvent(**values)


class ElementInvariantTests(unittest.TestCase):
    def test_element_key_must_match_its_own_parts(self):
        with self.assertRaisesRegex(ValueError, "does not match its own"):
            Element(
                element_key="hvac::WRONG",
                model_key="hvac",
                global_id="GUID",
                ifc_class="IfcWall",
                name="n",
                storey="s",
                pset_count=1,
            )

    def test_well_formed_element_is_accepted(self):
        element = Element(
            element_key=make_element_key("hvac", "GUID"),
            model_key="hvac",
            global_id="GUID",
            ifc_class="IfcWall",
            name="n",
            storey="s",
            pset_count=0,
        )
        self.assertEqual(element.element_key, "hvac::GUID")

    def test_negative_pset_count_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "pset_count"):
            Element(
                element_key="hvac::GUID",
                model_key="hvac",
                global_id="GUID",
                ifc_class="IfcWall",
                name="n",
                storey="s",
                pset_count=-1,
            )

    def test_model_key_may_not_contain_the_separator(self):
        # Otherwise an element key could be split two different ways.
        with self.assertRaisesRegex(ValueError, "must not contain"):
            make_element_key("a::b", "GUID")


class FindingInvariantTests(unittest.TestCase):
    def test_the_three_meaningful_shapes_are_accepted(self):
        make_finding(status=FindingStatus.PASS, severity=Severity.INFO, is_issue=False)
        make_finding(
            status=FindingStatus.FAIL, severity=Severity.WARNING, is_issue=True
        )
        make_finding(
            status=FindingStatus.NOT_APPLICABLE,
            severity=Severity.INFO,
            is_applicable=False,
            is_issue=False,
            element_key="",
        )

    def test_pass_may_not_be_an_issue(self):
        with self.assertRaisesRegex(ValueError, "only a FAIL is an issue"):
            make_finding(status=FindingStatus.PASS, is_issue=True)

    def test_fail_must_be_an_issue(self):
        with self.assertRaisesRegex(ValueError, "only a FAIL is an issue"):
            make_finding(
                status=FindingStatus.FAIL, severity=Severity.WARNING, is_issue=False
            )

    def test_fail_may_not_be_info(self):
        with self.assertRaisesRegex(ValueError, "severity above INFO"):
            make_finding(
                status=FindingStatus.FAIL, severity=Severity.INFO, is_issue=True
            )

    def test_non_failure_must_be_info(self):
        with self.assertRaisesRegex(ValueError, "must be INFO"):
            make_finding(status=FindingStatus.PASS, severity=Severity.ERROR)

    def test_not_applicable_must_not_be_applicable(self):
        with self.assertRaisesRegex(ValueError, "is_applicable"):
            make_finding(
                status=FindingStatus.NOT_APPLICABLE,
                is_applicable=True,
                element_key="",
            )

    def test_not_applicable_must_not_name_an_element(self):
        # An N/A finding is specification-level: no element was applicable, so
        # there is nothing to point at.
        with self.assertRaisesRegex(ValueError, "must not name an element"):
            make_finding(
                status=FindingStatus.NOT_APPLICABLE,
                is_applicable=False,
                element_key="hvac::GUID",
            )

    def test_a_passing_finding_needs_the_element_it_checked(self):
        # A pass says a specific thing was checked and was correct, so there
        # is always something to name.
        with self.assertRaisesRegex(ValueError, "must name the element"):
            make_finding(element_key="")

    def test_a_failure_may_be_about_something_that_is_not_there(self):
        # The fourth shape. A finding names the smallest thing that exists
        # and that a person can go and look at; when a whole model is missing
        # a required thing, that is the model. The alternative was to mint an
        # element key for something never modelled, which this project treats
        # the same way it treats an invented `actual` value: not at all.
        finding = make_finding(
            status=FindingStatus.FAIL,
            is_applicable=True,
            is_issue=True,
            severity=Severity.ERROR,
            element_key="",
        )
        self.assertEqual(finding.element_key, "")
        self.assertTrue(finding.model_key)

    def test_element_must_belong_to_the_finding_s_model(self):
        with self.assertRaisesRegex(ValueError, "does not belong to model"):
            make_finding(model_key="hvac", element_key="architecture::GUID")


class RequirementInvariantTests(unittest.TestCase):
    def test_severity_info_is_meaningless_for_a_requirement(self):
        # `severity` is the severity of a failure, so INFO says nothing.
        with self.assertRaisesRegex(ValueError, "INFO"):
            Requirement(
                requirement_key="rk",
                rule_id="R-001",
                requirement_id="Name",
                specification_label="R-001: x",
                requirement_label="Name",
                severity=Severity.INFO,
            )

    def test_ruleset_rejects_duplicate_requirement_keys(self):
        requirement = Requirement(
            requirement_key="rk",
            rule_id="R-001",
            requirement_id="Name",
            specification_label="R-001: x",
            requirement_label="Name",
        )
        with self.assertRaisesRegex(ValueError, "Duplicate requirement_key"):
            RuleSet(
                ruleset_id="rs",
                version="0.1",
                normalized_digest=SHA_A,
                requirements=(requirement, requirement),
            )

    def test_normalized_digest_must_look_like_a_digest(self):
        with self.assertRaisesRegex(ValueError, "64 lowercase hex"):
            RuleSet(ruleset_id="rs", version="0.1", normalized_digest="nope")

    def test_source_blob_hash_is_optional_but_validated(self):
        # Provenance, not identity: a rule set assembled in memory has no
        # source file, but one that claims a hash must supply a real digest.
        RuleSet(ruleset_id="rs", version="0.1", normalized_digest=SHA_A)
        with self.assertRaisesRegex(ValueError, "source_blob_sha256"):
            RuleSet(
                ruleset_id="rs",
                version="0.1",
                normalized_digest=SHA_A,
                source_blob_sha256="nope",
            )


class IssueEventInvariantTests(unittest.TestCase):
    def test_event_type_must_agree_with_its_payload(self):
        with self.assertRaisesRegex(ValueError, "disagrees with"):
            make_event(event_type="state_changed")

    def test_sequence_starts_at_one(self):
        with self.assertRaisesRegex(ValueError, "sequence starts at 1"):
            make_event(sequence=0)

    def test_an_event_must_change_state(self):
        with self.assertRaisesRegex(ValueError, "must change state"):
            make_event(
                event_type="state_changed",
                typed_payload=StateChangedPayload(),
                from_state=IssueState.OPEN,
                to_state=IssueState.OPEN,
            )

    def test_a_created_topic_covers_at_least_one_finding(self):
        with self.assertRaisesRegex(ValueError, "at least one finding"):
            TopicCreatedPayload(finding_count=0, title="t")


class LifecycleDerivationTests(unittest.TestCase):
    def test_state_is_folded_from_the_stream_regardless_of_input_order(self):
        opened = make_event()
        resolved = make_event(
            event_key="ek2",
            sequence=2,
            event_type="state_changed",
            typed_payload=StateChangedPayload(note="done"),
            from_state=IssueState.OPEN,
            to_state=IssueState.RESOLVED,
        )
        self.assertIs(derive_lifecycle_state([resolved, opened]), IssueState.RESOLVED)

    def test_a_stream_may_not_mix_two_issues(self):
        with self.assertRaisesRegex(ValueError, "must belong to one issue"):
            derive_lifecycle_state([make_event(), make_event(issue_key="other")])

    def test_a_gap_in_the_sequence_is_rejected(self):
        opened = make_event()
        detached = make_event(
            event_key="ek3",
            sequence=3,
            event_type="state_changed",
            typed_payload=StateChangedPayload(),
            from_state=IssueState.OPEN,
            to_state=IssueState.CLOSED,
        )
        with self.assertRaisesRegex(ValueError, "gap or duplicate"):
            derive_lifecycle_state([opened, detached])

    def test_a_discontinuous_transition_is_rejected(self):
        opened = make_event()
        impossible = make_event(
            event_key="ek2",
            sequence=2,
            event_type="state_changed",
            typed_payload=StateChangedPayload(),
            from_state=IssueState.CLOSED,
            to_state=IssueState.RESOLVED,
        )
        with self.assertRaisesRegex(ValueError, "starts from"):
            derive_lifecycle_state([opened, impossible])

    def test_an_empty_stream_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one event"):
            derive_lifecycle_state([])


class IssueInvariantTests(unittest.TestCase):
    def test_an_issue_must_cover_a_finding(self):
        with self.assertRaisesRegex(ValueError, "at least one finding"):
            Issue(
                issue_key="ik",
                validation_run_id="run",
                project_id="proj",
                model_key="hvac",
                element_key="hvac::GUID",
                grouping_policy="element",
                group_ref="hvac::GUID",
                finding_keys=(),
                lifecycle_state=IssueState.OPEN,
            )

    def test_duplicate_finding_keys_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate finding_keys"):
            Issue(
                issue_key="ik",
                validation_run_id="run",
                project_id="proj",
                model_key="hvac",
                element_key="hvac::GUID",
                grouping_policy="element",
                group_ref="hvac::GUID",
                finding_keys=("a", "a"),
                lifecycle_state=IssueState.OPEN,
            )


class ProvenanceAndModelTests(unittest.TestCase):
    def test_provenance_hash_must_look_like_a_digest(self):
        with self.assertRaisesRegex(ValueError, "64 lowercase hex"):
            Provenance(source_url="u", license="CC BY 4.0", content_sha256="ABC")

    def test_uppercase_digest_is_rejected(self):
        # Digests are compared as text throughout, so case must be pinned.
        with self.assertRaisesRegex(ValueError, "64 lowercase hex"):
            Provenance(source_url="u", license="CC BY 4.0", content_sha256=SHA_A.upper())

    def test_project_id_must_be_a_slug(self):
        with self.assertRaisesRegex(ValueError, "must be a slug"):
            Project(project_id="not a slug", name="n")

    def test_model_key_may_not_contain_the_element_key_separator(self):
        with self.assertRaisesRegex(ValueError, "must not contain"):
            Model(
                model_key="a::b",
                model_id="a",
                project_id="proj",
                discipline="D",
                filename="f.ifc",
                provenance=Provenance("u", "CC BY 4.0", SHA_B),
                ifc_schema="IFC4",
                ifc_project_guid="g",
            )


class ModelKeyDerivationTests(unittest.TestCase):
    def test_derived_key_is_namespaced_by_project(self):
        self.assertEqual(
            derive_model_key("plant-a", "architecture"), "plant-a.architecture"
        )

    def test_two_projects_with_the_same_business_code_get_distinct_keys(self):
        self.assertNotEqual(
            derive_model_key("plant-a", "architecture"),
            derive_model_key("plant-b", "architecture"),
        )


if __name__ == "__main__":
    unittest.main()
