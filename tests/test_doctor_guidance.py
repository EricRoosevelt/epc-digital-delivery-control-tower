"""Local engineering guidance explains evidence without inventing a repair."""

import copy

import pytest

from internal.doctor_adapter.guidance import guidance_for


def finding(rule="PV-001", status="FAIL", **extra):
    return {
        "finding_id": "f-1", "element_key": "model:123", "rule_id": rule,
        "status": status, "expected": "DIFFUSER, GRILLE, LOUVRE or REGISTER",
        "actual": "chimney cover", "reason": "Effective type is outside the set",
        "citation": "Repository product rule, not a statutory requirement", **extra,
    }


ELEMENT = {
    "element_key": "model:123", "global_id": "123", "model_key": "model",
    "ifc_class": "IfcAirTerminal", "name": "Roof cap", "storey": "Roof",
    "tag": "C1", "geometry_status": "ready",
}


@pytest.mark.parametrize("language", ["en", "zh", "zh-CN"])
@pytest.mark.parametrize("rule", ["PV-001", "INFO-001", "INFO-002", "ID-001"])
@pytest.mark.parametrize("status", ["PASS", "FAIL", "NOT_APPLICABLE", "ERROR"])
def test_each_rule_and_check_status_has_structured_local_guidance(language, rule, status):
    result = guidance_for(finding(rule, status), ELEMENT, language)
    assert set(result) == {"summary", "facts", "actions", "verification", "citations",
                           "limitations"}
    assert isinstance(result["summary"], str) and result["summary"]
    for key in ("facts", "actions", "verification", "limitations"):
        assert result[key] and all(isinstance(item, str) for item in result[key])
    assert result["citations"] == [{"id": "PV-001" if rule == "PV-001" else rule,
                                   "label": finding()["citation"]}]


def test_pv_failure_supports_wrong_classification_without_choosing_a_target_value():
    result = guidance_for(finding(), ELEMENT)
    text = " ".join(result["actions"] + result["limitations"])
    assert "mapping" in text and "type" in text and "instance" in text
    assert "Do not choose" in text
    assert "chimney cover" in " ".join(result["facts"])
    assert "re-export" in " ".join(result["verification"])
    assert "USERDEFINED" in text


def test_name_is_an_instance_attribute_and_missing_name_is_not_a_schema_defect():
    result = guidance_for(finding("INFO-001", actual=""), ELEMENT)
    text = " ".join(result["actions"] + result["limitations"])
    assert "optional" in text and "instance" in text
    assert "type name" in text
    assert "schema defect" in text
    assert "not recorded" in " ".join(result["facts"])


def test_storey_guidance_does_not_infer_containment_from_coordinates():
    result = guidance_for(finding("INFO-002", actual=""), None)
    text = " ".join(result["actions"] + result["limitations"])
    assert "decomposition" in text and "coordinates" in text
    assert "room" in text and "multi-storey" in text


def test_identity_guidance_limits_scope_and_avoids_regenerating_all_ids():
    result = guidance_for(finding("ID-001", actual="duplicate"), ELEMENT)
    text = " ".join(result["actions"] + result["limitations"])
    assert "same file" in text and "unaffected" in text and "references" in text
    assert "different models" in text


def test_pass_is_not_an_acceptance_verdict_or_instruction_to_repair():
    result = guidance_for(finding(status="PASS", actual="LOUVRE"), ELEMENT)
    assert "No correction" in " ".join(result["actions"])
    assert "semantic" in " ".join(result["limitations"])
    assert "LOUVRE" in " ".join(result["facts"])


@pytest.mark.parametrize("status", ["ERROR", "UNKNOWN", "NOT_APPLICABLE", "N/A"])
def test_unchecked_findings_never_recommend_changing_model_values(status):
    result = guidance_for(finding(status=status), ELEMENT)
    assert "Do not change" in " ".join(result["actions"])
    assert "not" in result["summary"].lower()


def test_review_workflow_state_does_not_replace_check_result():
    result = guidance_for(finding(status="FAIL", review_status="resolved"), ELEMENT)
    assert "outside" in result["summary"]
    assert "re-export" in " ".join(result["verification"])


def test_unknown_rule_keeps_evidence_and_does_not_invent_a_rule_citation():
    result = guidance_for(finding("NEW-999", citation="", actual=0), None)
    assert "0" in " ".join(result["facts"])
    assert result["citations"] == []
    assert "no rule-specific" in " ".join(result["limitations"])


def test_guidance_is_pure_and_chinese_output_is_localized():
    original = finding()
    before = copy.deepcopy(original)
    result = guidance_for(original, ELEMENT, "zh")
    assert original == before
    assert "四个" in result["summary"]
    assert "重新导出" in " ".join(result["verification"])
    assert "类型" in " ".join(result["actions"])
