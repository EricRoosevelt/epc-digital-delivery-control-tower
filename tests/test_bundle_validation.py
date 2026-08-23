"""Cross-entity validation of a run bundle.

Domain types police themselves; this covers what only the whole picture shows —
references that resolve, keys that are what they claim to be, and an issue whose
stated lifecycle matches its own history.

Each test builds a valid bundle and then breaks exactly one thing, which is the
only way to be sure a check is actually load-bearing rather than incidentally
satisfied.
"""

from __future__ import annotations

import dataclasses
import unittest

from epc_control_tower.domain import (
    ComponentFingerprint,
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
    RunBundle,
    Severity,
    TopicCreatedPayload,
    ValidationRun,
    make_element_key,
)
from epc_control_tower.identity import (
    build_finding_key,
    build_issue_event_key,
    build_issue_key,
    build_requirement_key,
    build_ruleset_normalized_digest,
    build_validation_run_id,
)
from epc_control_tower.validation import BundleInvariantError, validate_bundle

MODEL_SHA = "a" * 64
AS_OF = "2026-08-13T00:00:00Z"


def build_bundle() -> RunBundle:
    """Assemble a bundle every invariant is satisfied by."""

    project = Project(project_id="demo", name="Demo")
    model = Model(
        model_key="demo.hvac",
        model_id="hvac",
        project_id="demo",
        discipline="HVAC",
        filename="H.ifc",
        provenance=Provenance("https://example.invalid/H.ifc", "CC BY 4.0", MODEL_SHA),
        ifc_schema="IFC4",
        ifc_project_guid="guid",
    )
    element = Element(
        element_key=make_element_key("demo.hvac", "GUID1"),
        model_key="demo.hvac",
        global_id="GUID1",
        ifc_class="IfcDuctSegment",
        name="duct",
        storey="L1",
        pset_count=1,
    )
    requirement = Requirement(
        requirement_key=build_requirement_key("R-005A", "EPC_Delivery.AssetTag"),
        rule_id="R-005A",
        requirement_id="EPC_Delivery.AssetTag",
        specification_label="R-005A: duct segments need assumed EPC metadata",
        requirement_label="EPC_Delivery.AssetTag",
        severity=Severity.WARNING,
        owner_role="model-coordination",
    )
    ruleset = RuleSet(
        ruleset_id="epc-delivery",
        version="0.1",
        normalized_digest=build_ruleset_normalized_digest(
            ruleset_id="epc-delivery", version="0.1", requirements=[requirement]
        ),
        requirements=(requirement,),
    )

    fingerprints = (ComponentFingerprint("ids", "0.8.5"),)
    model_inputs = ((model.model_key, MODEL_SHA),)
    validation_run_id = build_validation_run_id(
        ruleset_id="epc-delivery",
        ruleset_version="0.1",
        ruleset_normalized_digest=ruleset.normalized_digest,
        models=model_inputs,
        checkers=fingerprints,
        as_of=AS_OF,
    )
    run = ValidationRun(
        validation_run_id=validation_run_id,
        ruleset_id="epc-delivery",
        ruleset_version="0.1",
        ruleset_normalized_digest=ruleset.normalized_digest,
        as_of=AS_OF,
        model_inputs=model_inputs,
        checker_fingerprints=fingerprints,
    )

    finding = Finding(
        finding_key=build_finding_key(
            validation_run_id=validation_run_id,
            model_key=model.model_key,
            requirement_key=requirement.requirement_key,
            element_key=element.element_key,
        ),
        validation_run_id=validation_run_id,
        project_id="demo",
        model_key=model.model_key,
        element_key=element.element_key,
        requirement_key=requirement.requirement_key,
        status=FindingStatus.FAIL,
        severity=Severity.WARNING,
        is_applicable=True,
        is_issue=True,
        reason="The required property set does not exist",
    )

    issue_key = build_issue_key(
        validation_run_id=validation_run_id,
        grouping_policy="element",
        group_ref=element.element_key,
    )
    event = IssueEvent(
        event_key=build_issue_event_key(
            issue_key=issue_key, sequence=1, event_type="topic_created"
        ),
        issue_key=issue_key,
        sequence=1,
        occurred_at=AS_OF,
        event_type="topic_created",
        from_state=None,
        to_state=IssueState.OPEN,
        actor_role="control-tower",
        payload_version=1,
        typed_payload=TopicCreatedPayload(finding_count=1, title="duct"),
    )
    issue = Issue(
        issue_key=issue_key,
        validation_run_id=validation_run_id,
        project_id="demo",
        model_key=model.model_key,
        element_key=element.element_key,
        grouping_policy="element",
        group_ref=element.element_key,
        finding_keys=(finding.finding_key,),
        lifecycle_state=IssueState.OPEN,
        assignee_role="model-coordination",
    )

    return RunBundle(
        contract_version="0.1",
        run=run,
        ruleset=ruleset,
        projects=(project,),
        models=(model,),
        elements=(element,),
        findings=(finding,),
        issues=(issue,),
        issue_events=(event,),
    )


class ValidBundleTests(unittest.TestCase):
    def test_a_well_formed_bundle_passes(self):
        validate_bundle(build_bundle())

    def test_no_execution_record_is_reachable_from_a_bundle(self):
        # An exporter that could see a wall-clock timestamp would eventually
        # write one, and determinism would quietly stop holding.
        self.assertNotIn(
            "execution", {f.name for f in dataclasses.fields(RunBundle)}
        )


class ReferentialIntegrityTests(unittest.TestCase):
    def _expect(self, bundle: RunBundle, pattern: str):
        with self.assertRaises(BundleInvariantError) as caught:
            validate_bundle(bundle)
        joined = "\n".join(caught.exception.violations)
        self.assertRegex(joined, pattern)

    def test_a_finding_naming_an_unknown_element_is_caught(self):
        bundle = build_bundle()
        broken = dataclasses.replace(
            bundle.findings[0], element_key="demo.hvac::MISSING"
        )
        self._expect(
            dataclasses.replace(bundle, findings=(broken,)), "unknown element_key"
        )

    def test_a_finding_naming_an_unknown_requirement_is_caught(self):
        bundle = build_bundle()
        broken = dataclasses.replace(bundle.findings[0], requirement_key="nope")
        self._expect(
            dataclasses.replace(bundle, findings=(broken,)), "unknown requirement_key"
        )

    def test_a_finding_from_another_run_is_caught(self):
        bundle = build_bundle()
        broken = dataclasses.replace(bundle.findings[0], validation_run_id="other")
        self._expect(
            dataclasses.replace(bundle, findings=(broken,)), "belongs to run"
        )

    def test_an_orphaned_event_is_caught(self):
        bundle = build_bundle()
        broken = dataclasses.replace(bundle.issue_events[0], issue_key="nope")
        self._expect(
            dataclasses.replace(bundle, issue_events=(broken,)), "orphaned"
        )

    def test_an_issue_with_no_history_is_caught(self):
        bundle = build_bundle()
        self._expect(dataclasses.replace(bundle, issue_events=()), "has no events")

    def test_a_model_missing_from_the_run_inputs_is_caught(self):
        bundle = build_bundle()
        broken_run = dataclasses.replace(bundle.run, model_inputs=())
        self._expect(
            dataclasses.replace(bundle, run=broken_run),
            "not recorded in the run's model inputs",
        )

    def test_a_run_input_hash_disagreeing_with_provenance_is_caught(self):
        bundle = build_bundle()
        broken_run = dataclasses.replace(
            bundle.run, model_inputs=(("demo.hvac", "b" * 64),)
        )
        self._expect(
            dataclasses.replace(bundle, run=broken_run), "disagrees with its provenance"
        )


class LifecycleConsistencyTests(unittest.TestCase):
    def test_a_lifecycle_state_the_history_does_not_support_is_caught(self):
        bundle = build_bundle()
        broken = dataclasses.replace(
            bundle.issues[0], lifecycle_state=IssueState.CLOSED
        )
        with self.assertRaises(BundleInvariantError) as caught:
            validate_bundle(dataclasses.replace(bundle, issues=(broken,)))
        self.assertRegex(
            "\n".join(caught.exception.violations), "its history derives"
        )


class RecomputedIdentityTests(unittest.TestCase):
    def test_a_tampered_finding_key_is_caught(self):
        bundle = build_bundle()
        broken = dataclasses.replace(
            bundle.findings[0], finding_key="00000000-0000-5000-8000-000000000000"
        )
        bundle = dataclasses.replace(
            bundle,
            findings=(broken,),
            issues=(dataclasses.replace(
                bundle.issues[0], finding_keys=(broken.finding_key,)
            ),),
        )
        with self.assertRaises(BundleInvariantError) as caught:
            validate_bundle(bundle)
        self.assertRegex("\n".join(caught.exception.violations), "does not recompute")

    def test_a_tampered_ruleset_digest_is_caught(self):
        bundle = build_bundle()
        broken = dataclasses.replace(bundle.ruleset, normalized_digest="f" * 64)
        with self.assertRaises(BundleInvariantError) as caught:
            validate_bundle(dataclasses.replace(bundle, ruleset=broken))
        self.assertRegex(
            "\n".join(caught.exception.violations),
            "normalized_digest .* does not recompute",
        )

    def test_a_run_claiming_a_different_ruleset_is_caught(self):
        bundle = build_bundle()
        broken_run = dataclasses.replace(
            bundle.run, ruleset_normalized_digest="e" * 64
        )
        with self.assertRaises(BundleInvariantError) as caught:
            validate_bundle(dataclasses.replace(bundle, run=broken_run))
        self.assertRegex("\n".join(caught.exception.violations), "disagrees with")

    def test_legacy_bundles_skip_identity_recomputation_but_not_structure(self):
        # The legacy adapters emit keys from frozen pre-split derivations, so
        # their values will not match the current ones. Everything structural
        # is still checked.
        bundle = build_bundle()
        broken = dataclasses.replace(
            bundle.findings[0], finding_key="00000000-0000-5000-8000-000000000000"
        )
        bundle = dataclasses.replace(
            bundle,
            findings=(broken,),
            issues=(dataclasses.replace(
                bundle.issues[0], finding_keys=(broken.finding_key,)
            ),),
        )
        validate_bundle(bundle, recompute_identity=False)

    def test_every_violation_is_reported_not_only_the_first(self):
        bundle = build_bundle()
        broken = dataclasses.replace(
            bundle.findings[0],
            element_key="demo.hvac::MISSING",
            requirement_key="nope",
        )
        bundle = dataclasses.replace(
            bundle,
            findings=(broken,),
            issues=(dataclasses.replace(
                bundle.issues[0], finding_keys=(broken.finding_key,)
            ),),
        )
        with self.assertRaises(BundleInvariantError) as caught:
            validate_bundle(bundle)
        self.assertGreater(len(caught.exception.violations), 1)


if __name__ == "__main__":
    unittest.main()
