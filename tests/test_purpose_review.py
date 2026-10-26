"""Purpose adapter regressions: declared coverage, attributable evidence and recheck."""

import copy
import json
from types import SimpleNamespace

import pytest

from internal.doctor_adapter import purpose_review


def case(*, manual=False, counterpart=False):
    checks = [
        {
            "requirement_key": key,
            "rule_id": "ORG-1",
            "title": key,
            "semantics_digest": key * 64,
            "expected": "present",
            "support": "supported",
            "unsupported_reasons": [],
            "checker": {"component_id": "ids", "version": "1", "config_sha256": "c" * 64},
        }
        for key in ("a", "b")
    ]
    purpose = {
        "purpose_id": "delivery",
        "title": "Information delivery",
        "from_role": "Author",
        "to_role": "Recipient",
        "subject_classes": ["IfcElement"],
        "required_rule_ids": ["ORG-1"],
        "requires_counterpart": counterpart,
        "evidence_requirements": [],
    }
    if manual:
        purpose["evidence_requirements"] = [
            {
                "evidence_id": "review",
                "title": "Review",
                "acceptance": "Inspect the evidence",
                "execution": "manual",
                "method_id": "recorded-review",
                "method_description": "Recorded inspection",
            }
        ]
    package = SimpleNamespace(
        manifest={
            "schema_version": 1,
            "package_id": "company",
            "title": "Company requirements",
            "version": "1",
            "purposes": [purpose],
        },
        checks=checks,
        definition=None,
        source_sha256="f" * 64,
    )
    evaluation = {
        "ruleset": {
            "ruleset_id": "company",
            "version": "1",
            "normalized_digest": "d" * 64,
            "checker": checks[0]["checker"],
        },
        "checks": checks,
        "models": [{"model_key": "slot", "content_id": "1" * 64}],
        "elements": [
            {
                "element_key": "slot::guid",
                "review_element_key": "sha::guid",
                "model_key": "slot",
                "global_id": "guid",
                "identity_comparable": True,
                "ifc_class": "IfcWall",
                "class_ancestors": ["IfcElement", "IfcProduct"],
                "name": "Wall",
            }
        ],
        "findings": [],
        "coverage": [],
    }
    for check in checks:
        evaluation["findings"].append(
            {
                **check,
                "finding_key": "finding-" + check["requirement_key"],
                "element_key": "slot::guid",
                "model_key": "slot",
                "status": "PASS",
                "actual": "present",
                "reason": "Requirement satisfied",
            }
        )
        evaluation["coverage"].append(
            {
                "requirement_key": check["requirement_key"],
                "support": "supported",
                "applicable": 1,
                "evaluated": 1,
                "passed": 1,
                "failed": 0,
                "not_applicable": 0,
            }
        )
    return package, evaluation


def assess(package, evaluation, **kwargs):
    return purpose_review.assess_evaluation(
        package,
        evaluation,
        project_id="project",
        revision_id=kwargs.pop("revision_id", "revision-1"),
        purpose_id="delivery",
        scope=kwargs.pop("scope", {"kind": "all", "classes": [], "element_keys": []}),
        responsible_team="Project reviewer",
        **kwargs,
    )


def test_complete_checks_use_real_sealed_engine_and_single_delivered_artifact():
    package, evaluation = case()
    result = assess(package, evaluation)
    assert result["conclusion"]["status"] == "READY"
    assert result["conclusion"]["scope_count"] == 1
    restored = purpose_review.restore_record(result["record"], result["assessment_digest"])
    assert restored.as_document() == result["record"]
    assert result["context"]["kind"] == "same-delivered-artifact"


@pytest.mark.parametrize("change", ["missing", "unsupported", "na", "bad-identity"])
def test_partial_or_uncheckable_evidence_cannot_make_ready(change):
    package, evaluation = case()
    if change == "missing":
        evaluation["findings"].pop()
        evaluation["coverage"][1]["evaluated"] = 0
    elif change == "unsupported":
        evaluation["checks"][1]["support"] = "unsupported"
        evaluation["checks"][1]["unsupported_reasons"] = ["Unsupported schema"]
    elif change == "na":
        evaluation["findings"][1]["status"] = "N/A"
    else:
        evaluation["elements"][0]["identity_comparable"] = False
    result = assess(package, evaluation)
    assert result["conclusion"]["status"] == "UNKNOWN"
    assert result["blockers"]


def test_fail_is_blocked_with_exact_geometry_link():
    package, evaluation = case()
    evaluation["findings"][0]["status"] = "FAIL"
    result = assess(package, evaluation)
    assert result["conclusion"]["status"] == "BLOCKED"
    block = next(x for x in result["blockers"] if x["verdict"] == "BLOCKED")
    assert block["review_element_key"] == "sha::guid"
    assert block["requirement_key"] == "a"


def test_empty_partition_and_missing_counterpart_are_unknown():
    package, evaluation = case(counterpart=True)
    assert assess(package, evaluation)["conclusion"]["status"] == "UNKNOWN"
    package.manifest["purposes"][0]["requires_counterpart"] = False
    result = assess(package, evaluation, scope={"kind": "classes", "classes": ["IfcDoor"]})
    assert result["conclusion"]["status"] == "UNKNOWN"
    assert result["conclusion"]["scope_count"] == 0


def judgment(result, **changes):
    return {
        "evidence_id": "review",
        "subject_keys": ["slot::guid"],
        "outcome": "confirmed",
        "method_id": "recorded-review",
        "determiner": "Reviewer",
        "basis": "Inspection record",
        "reference": "record-123",
        "context_digest": result["context_digest"],
        **changes,
    }


def test_manual_evidence_is_attributed_and_does_not_override_failed_checks():
    package, evaluation = case(manual=True)
    initial = assess(package, evaluation)
    assert initial["conclusion"]["status"] == "UNKNOWN"
    approved = assess(package, evaluation, determinations=[judgment(initial)])
    assert approved["conclusion"]["status"] == "READY"
    for changes in ({"method_id": "unaccepted"}, {"basis": ""}, {"context_digest": "old"}):
        assert (
            assess(package, evaluation, determinations=[judgment(initial, **changes)])[
                "conclusion"
            ]["status"]
            == "UNKNOWN"
        )
    evaluation["findings"][0]["status"] = "FAIL"
    assert (
        assess(package, evaluation, determinations=[judgment(initial)])["conclusion"]["status"]
        == "BLOCKED"
    )
    evaluation["findings"][0]["status"] = "PASS"
    assert (
        assess(
            package, evaluation, revision_id="revision-2", determinations=[judgment(initial)]
        )["conclusion"]["status"]
        == "UNKNOWN"
    )


def test_recheck_survives_json_restart_and_rejects_a_broken_seal():
    package, evaluation = case()
    evaluation["findings"][0]["status"] = "FAIL"
    prior = json.loads(json.dumps(assess(package, evaluation)))
    evaluation["findings"][0]["status"] = "PASS"
    evaluation["models"][0]["content_id"] = "2" * 64
    current = assess(package, evaluation, revision_id="revision-2", prior=prior)
    assert current["record"]["successor"]["kind"] == "recheck"
    assert current["conclusion"]["status"] == "READY"
    assert "model" in [x["kind"] for x in current["change_summary"]["basis_changes"]]
    altered = copy.deepcopy(prior)
    altered["record"]["activities"][0]["subscopes"][0]["verdict"] = "READY"
    with pytest.raises(ValueError, match="seal"):
        assess(package, evaluation, prior=altered)


def test_rule_change_is_a_new_assessment_not_a_claimed_model_repair():
    package, evaluation = case()
    prior = assess(package, evaluation)
    package.source_sha256 = "e" * 64
    package.manifest["version"] = "2"
    evaluation["checks"][0]["semantics_digest"] = "e" * 64
    current = assess(package, evaluation, prior=prior)
    assert "successor" not in current["record"]
    assert not current["change_summary"]["comparable"]
    assert "rules" in [x["kind"] for x in current["change_summary"]["basis_changes"]]


@pytest.mark.parametrize("change", ["delete", "class", "scope"])
def test_disappearing_scope_is_never_reported_as_repair(change):
    package, evaluation = case()
    second = copy.deepcopy(evaluation["elements"][0])
    second.update(element_key="slot::second", review_element_key="sha::second")
    evaluation["elements"].append(second)
    evaluation["findings"].extend(
        [
            {
                **f,
                "element_key": "slot::second",
                "finding_key": f["finding_key"] + "second",
                "status": "FAIL",
            }
            for f in copy.deepcopy(evaluation["findings"])
        ]
    )
    prior = assess(package, evaluation)
    scope = {"kind": "all"}
    if change == "delete":
        evaluation["elements"].pop()
        evaluation["findings"] = [
            f for f in evaluation["findings"] if f["element_key"] != "slot::second"
        ]
    elif change == "class":
        evaluation["elements"][1].update(ifc_class="IfcSite", class_ancestors=["IfcRoot"])
    else:
        scope = {"kind": "elements", "element_keys": ["slot::guid"]}
    current = assess(package, evaluation, prior=prior, scope=scope)
    assert current["change_summary"]["outcomes"]
    assert any(
        x["change"] in ("missing", "class_changed", "scope_excluded")
        for x in current["change_summary"]["outcomes"]
    )


def test_successor_record_can_be_restored_for_another_recheck():
    package, evaluation = case()
    first = assess(package, evaluation)
    second = assess(package, evaluation, prior=json.loads(json.dumps(first)))
    third = assess(package, evaluation, prior=json.loads(json.dumps(second)))
    assert (
        third["record"]["successor"]["prior_assessment_digest"] == second["assessment_digest"]
    )


def test_actual_counterpart_is_in_the_sealed_context():
    package, evaluation = case(counterpart=True)
    consumer = {
        "revision": {"project_id": "project", "model_id": "architecture"},
        "report": {
            "source": {"sha256": "3" * 64},
            "elements": [{"global_id": "0AAAAAAAAAAAAAAAAAAAAA", "ifc_class": "IfcSlab"}],
        },
    }
    result = assess(package, evaluation, consumer=consumer)
    assert result["conclusion"]["status"] == "READY"
    actual = result["record"]["request"]["model_version_context"]["consuming"]
    assert actual == {"model_key": "architecture", "content_id": "3" * 64}
    assert result["context"]["kind"] == "counterpart-model"


def test_engine_change_does_not_claim_model_repair():
    package, evaluation = case()
    evaluation["findings"][0]["status"] = "FAIL"
    prior = assess(package, evaluation)
    evaluation["findings"][0]["status"] = "PASS"
    evaluation["ruleset"]["checker"]["version"] = "new-engine"
    result = assess(package, evaluation, prior=prior)
    assert not result["change_summary"]["comparable"]
    assert {x["change"] for x in result["change_summary"]["outcomes"]} == {"not_comparable"}


def test_bad_guid_change_marks_comparison_unprovable():
    package, evaluation = case()
    prior = assess(package, evaluation)
    evaluation["elements"][0]["identity_comparable"] = False
    result = assess(package, evaluation, prior=prior)
    assert not result["change_summary"]["comparable"]
    assert "identity" in result["blockers"][0]["reason"].lower()


def test_duplicate_observations_cannot_be_silently_selected():
    package, evaluation = case()
    evaluation["findings"].append(copy.deepcopy(evaluation["findings"][0]))
    with pytest.raises(ValueError, match="[Dd]uplicate"):
        assess(package, evaluation)


def test_manual_progress_note_without_exact_context_is_not_evidence():
    package, evaluation = case(manual=True)
    result = assess(
        package,
        evaluation,
        determinations=[
            {
                "evidence_id": "review",
                "subject_keys": ["slot::guid"],
                "outcome": "confirmed",
                "method_id": "recorded-review",
                "determiner": "User",
                "basis": "Done",
                "reference": "note",
                "status": "ready_for_recheck",
            }
        ],
    )
    assert result["conclusion"]["status"] == "UNKNOWN"
    assert result["declined_determinations"]


def test_ready_manual_evidence_remains_editable_in_a_new_assessment():
    package, evaluation = case(manual=True)
    initial = assess(package, evaluation)
    ready = assess(package, evaluation, determinations=[judgment(initial)])
    assert ready["conclusion"]["status"] == "READY"
    request = next(r for r in ready["evidence_requests"] if r["evidence_id"] == "review")
    assert request["current_outcome"] == "confirmed"
    assert request["verdict"] == "READY"
    blocked = assess(
        package,
        evaluation,
        prior=ready,
        determinations=[judgment(ready, outcome="unmet", basis="Evidence was incorrect")],
    )
    assert blocked["conclusion"]["status"] == "BLOCKED"
    assert ready["conclusion"]["status"] == "READY"
    assert "human" in [c["kind"] for c in blocked["change_summary"]["basis_changes"]]


def test_coverage_gap_keeps_the_specific_checker_reason():
    package, evaluation = case()
    evaluation["coverage"][1].update(
        support="unsupported",
        evaluated=0,
        reason="IFC schema IFC2X3 is not supported by this check",
    )
    result = assess(package, evaluation)
    assert result["conclusion"]["status"] == "UNKNOWN"
    assert any("IFC2X3" in b["reason"] for b in result["blockers"])


def test_manual_change_is_not_classified_as_a_rule_repair():
    package, evaluation = case(manual=True)
    initial = assess(package, evaluation)
    blocked = assess(package, evaluation, determinations=[judgment(initial, outcome="unmet")])
    ready = assess(package, evaluation, prior=blocked, determinations=[judgment(blocked)])
    row = next(r for r in ready["change_summary"]["outcomes"] if r["evidence_id"] == "review")
    assert row["change"] == "evidence_updated"


def test_native_package_and_checker_feed_the_purpose_engine_without_geometry():
    import hashlib
    from internal.doctor_adapter.enterprise_rules import evaluate_rules, parse_package
    from test_enterprise_rules import model_case, package_bytes

    model, terminal = model_case(predefined="GRILLE")
    body = model.to_string().encode()
    package = parse_package(package_bytes(), "public.zip")
    report = {
        "review_id": "test",
        "source": {"sha256": hashlib.sha256(body).hexdigest()},
        "elements": [
            {
                "step_id": terminal.id(),
                "global_id": terminal.GlobalId,
                "ifc_class": "IfcAirTerminal",
                "element_key": "live::target",
            }
        ],
    }
    evaluation = evaluate_rules(package, body, report, "stable-slot")
    run = purpose_review.assess_evaluation(
        package,
        evaluation,
        project_id="project",
        revision_id="native-1",
        purpose_id="schedule",
        scope={"kind": "all"},
        responsible_team="Declared reviewer",
    )
    assert run["conclusion"]["status"] == "BLOCKED"
    assert run["blockers"][0]["review_element_key"] == "live::target"
    terminal.PredefinedType = "DIFFUSER"
    fixed = model.to_string().encode()
    report["source"]["sha256"] = hashlib.sha256(fixed).hexdigest()
    reevaluated = evaluate_rules(package, fixed, report, "stable-slot")
    rechecked = purpose_review.assess_evaluation(
        package,
        reevaluated,
        project_id="project",
        revision_id="native-2",
        purpose_id="schedule",
        scope={"kind": "all"},
        responsible_team="Declared reviewer",
        prior=json.loads(json.dumps(run)),
    )
    assert rechecked["conclusion"]["status"] == "READY"
    assert rechecked["record"]["successor"]["kind"] == "recheck"


def test_manual_only_purpose_cannot_confirm_an_ambiguous_identity():
    package, evaluation = case(manual=True)
    package.manifest["purposes"][0]["required_rule_ids"] = []
    evaluation["elements"][0]["identity_comparable"] = False
    initial = assess(package, evaluation)
    result = assess(package, evaluation, determinations=[judgment(initial)])
    assert result["conclusion"]["status"] == "UNKNOWN"


def test_undeclared_execution_has_no_vacuous_readiness():
    package, evaluation = case()
    package.manifest["purposes"][0]["required_rule_ids"] = []
    result = assess(package, evaluation)
    assert result["conclusion"]["status"] == "UNKNOWN"
    assert result["blockers"]


def test_unknown_manual_outcome_does_not_become_ready():
    package, evaluation = case(manual=True)
    first = assess(package, evaluation)
    result = assess(package, evaluation, determinations=[judgment(first, outcome="approved")])
    assert result["conclusion"]["status"] == "UNKNOWN"


def test_ambiguous_prior_step_identity_is_not_reported_as_a_deletion():
    package, evaluation = case()
    evaluation["elements"][0]["identity_comparable"] = False
    prior = assess(package, evaluation)
    evaluation["elements"][0]["element_key"] = "slot::guid::step-200"
    for finding in evaluation["findings"]:
        finding["element_key"] = "slot::guid::step-200"
    current = assess(package, evaluation, prior=prior)
    assert not current["change_summary"]["comparable"]
    assert {r["change"] for r in current["change_summary"]["outcomes"]} == {"not_comparable"}


def test_declared_hypotheses_stay_unverified_beside_original_evidence():
    package, evaluation = case()
    package.preview = lambda: {
        "rules": [
            {
                "rule_id": "ORG-1",
                "hypotheses": [{"text": "Inspect the source mapping", "verified": False}],
            }
        ]
    }
    evaluation["findings"][0].update(status="FAIL", actual="Not declared")
    result = assess(package, evaluation)
    block = next(x for x in result["blockers"] if x["requirement_key"] == "a")
    assert block["expected"] == "present"
    assert block["actual"] == "Not declared"
    assert block["hypotheses"] == [
        {"text": "Inspect the source mapping", "status": "unverified"}
    ]


def test_another_model_slot_is_a_new_question_not_a_deleted_model():
    package, evaluation = case()
    prior = assess(package, evaluation)
    evaluation["models"][0]["model_key"] = "other-slot"
    evaluation["elements"][0].update(element_key="other-slot::guid", model_key="other-slot")
    for finding in evaluation["findings"]:
        finding.update(element_key="other-slot::guid", model_key="other-slot")
    current = assess(package, evaluation, prior=prior)
    assert "successor" not in current["record"]
    assert not current["change_summary"]["comparable"]
    assert {row["change"] for row in current["change_summary"]["outcomes"]} == {
        "not_comparable"
    }


@pytest.mark.parametrize("guid,count", [("0AAAAAAAAAAAAAAAAAAAAA", 2), ("bad-id", 1)])
def test_counterpart_ambiguous_identity_is_refused_without_guessing(guid, count):
    package, evaluation = case(counterpart=True)
    consumer = {
        "revision": {"project_id": "project", "model_id": "architecture"},
        "report": {
            "source": {"sha256": "3" * 64},
            "elements": [{"global_id": guid, "global_id_count": count, "ifc_class": "IfcSlab"}],
        },
    }
    with pytest.raises(ValueError, match="[Cc]ounterpart.*identit"):
        assess(package, evaluation, consumer=consumer)


def test_reclassification_within_a_purpose_parent_class_is_not_a_repair():
    package, evaluation = case()
    evaluation["findings"][0]["status"] = "FAIL"
    prior = assess(package, evaluation)
    evaluation["elements"][0]["ifc_class"] = "IfcDoor"
    evaluation["models"][0]["content_id"] = "2" * 64
    evaluation["findings"][0]["status"] = "PASS"
    current = assess(package, evaluation, prior=prior)
    assert current["conclusion"]["status"] == "READY"
    assert not current["change_summary"]["comparable"]
    assert {row["change"] for row in current["change_summary"]["outcomes"]} == {"class_changed"}


def test_next_steps_distinguish_machine_failure_coverage_manual_and_unsupported():
    package, evaluation = case(manual=True)
    evaluation["findings"][0]["status"] = "FAIL"
    evaluation["findings"].pop()
    evaluation["coverage"][1]["evaluated"] = 0
    package.manifest["purposes"][0]["evidence_requirements"].append(
        {
            "evidence_id": "coordination",
            "title": "Coordination evidence",
            "acceptance": "Supported coordination evidence",
            "execution": "unsupported",
            "reason": "No coordination executor",
        }
    )
    result = assess(package, evaluation)
    by_key = {row["requirement_key"]: row for row in result["blockers"]}
    machine = by_key["a"]
    assert "re-export IFC" in machine["next_action"]
    assert "same model slot" in machine["next_action"]
    assert "source" in machine["next_action"]
    assert "适用条件" in by_key["b"]["next_action_zh"]
    assert "declared" in by_key["b"]["next_action"]
    manual = by_key["evidence-review"]
    assert "recorded-review" in manual["next_action"]
    assert "reference" in manual["next_action"] and "basis" in manual["next_action"]
    unsupported = by_key["evidence-coordination"]
    assert "executor" in unsupported["next_action"]
    assert "检查依据变化" in unsupported["next_action_zh"]
    assert len({row["next_action"] for row in by_key.values()}) == 4
    routes = [
        s["route"]["next_action"]
        for activity in result["record"]["activities"]
        for s in activity["subscopes"]
    ]
    assert machine["next_action"] in routes
    assert unsupported["next_action"] in routes
