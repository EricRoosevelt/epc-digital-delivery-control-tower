"""A manager's brief keeps check evidence separate from recorded follow-up."""

from copy import deepcopy

import pytest

from doctor.project_brief import project_brief


class Library:
    def __init__(self):
        self.requested = []
        self.models = [{
            "model_id": "m1", "name": "HVAC | North",
            "revisions": [
                {"revision_id": "r1", "number": 1, "label": "Before", "created_at": "date1"},
                {"revision_id": "r2", "number": 2, "label": "After", "created_at": "date2"},
            ],
        }]

    def detail(self, project_id):
        assert project_id == "p1"
        return {"project": {"project_id": "p1", "name": "Coordination review"},
                "models": deepcopy(self.models)}

    def revision(self, revision_id):
        self.requested.append(revision_id)
        assert revision_id == "r2", "The brief must use the latest saved revision"
        return {
            "revision": {"revision_id": "r2", "label": "After", "number": 2},
            "report": {
                "summary": {"elements": 3, "errors": 1, "information": 1},
                "elements": [{"element_key": "m::g", "name": "Roof cap", "global_id": "g"}],
                "findings": [
                    {"finding_id": "f1", "element_key": "m::g", "rule_id": "PV-001",
                     "status": "FAIL", "severity": "ERROR", "actual": "chimney cover"},
                    {"finding_id": "f2", "element_key": "m::g", "rule_id": "INFO-002",
                     "status": "FAIL", "severity": "INFO", "actual": "No storey"},
                ],
            },
            "followups": [{"finding_id": "f1", "status": "ready_for_recheck",
                           "owner": "Engineer A", "note": "Export checked | awaiting recheck"}],
        }

    def compare(self, before, after):
        assert (before, after) == ("r1", "r2")
        counts = {key: 0 for key in (
            "resolved", "remaining", "new", "missing", "not_applicable", "not_comparable",
        )}
        return {
            "summary": {**counts, "missing": 1,
                        "errors": {**counts, "missing": 1}, "information": counts},
            "rows": [{"change": "missing", "rule_id": "PV-001", "severity": "ERROR",
                      "before_name": "Old roof cap", "after_name": None,
                      "before_actual": "NOTDEFINED", "after_actual": None,
                      "reason": "The earlier element was not found in this model.",
                      "reason_zh": "当前模型中未找到原构件。"}],
        }


def test_brief_uses_latest_saved_evidence_and_separate_followup_states():
    library = Library()
    text = project_brief(library, "p1", "en")
    assert library.requested == ["r2"]
    assert "Coordination review" in text
    assert "Roof cap" in text and "chimney cover" in text
    assert "Engineer A" in text and "Ready for recheck" in text
    assert "Needs review: 1" in text
    assert "Information prompts: 1" in text
    assert "HVAC \\| North" in text
    assert "Export checked \\| awaiting recheck" in text


def test_missing_elements_are_never_reported_as_recheck_passes():
    text = project_brief(Library(), "p1", "en")
    assert "Not found now: 1" in text
    assert "Passed on recheck: 0" in text
    assert "Old roof cap" in text
    assert "The earlier element was not found" in text
    assert "Marked progress does not change a check result" in text


def test_chinese_brief_contains_real_observations_and_recorded_owner():
    text = project_brief(Library(), "p1", "zh")
    assert "项目工作简报" in text
    assert "需核对：1" in text and "信息提示：1" in text
    assert "待复查" in text and "Engineer A" in text
    assert "当前模型中未找到原构件。" in text


def test_empty_project_has_a_useful_next_step_and_no_invented_results():
    library = Library()
    library.models = []
    text = project_brief(library, "p1", "en")
    assert "No saved model revisions" in text
    assert "Save a review" in text
    assert not library.requested


def test_unsupported_language_is_rejected_before_exporting():
    with pytest.raises(ValueError, match="language"):
        project_brief(Library(), "p1", "fr")


def test_information_changes_use_prompt_wording_and_show_comparison_scope():
    library = Library()
    original = library.compare

    def comparison(before, after):
        result = original(before, after)
        result["summary"]["information"]["resolved"] = 1
        result["rows"].append({
            "change": "resolved", "rule_id": "INFO-002", "severity": "INFO",
            "before_name": "Site asset", "after_name": "Site asset",
            "before_actual": "No storey", "after_actual": "Storey 1",
            "reason": "Information prompt satisfied.", "reason_zh": "提示条件已满足。",
        })
        result["scope_note"] = "Single-file comparison scope."
        result["scope_note_zh"] = "单文件比较范围。"
        return result

    library.compare = comparison
    english = project_brief(library, "p1", "en")
    chinese = project_brief(library, "p1", "zh")
    assert "Prompts satisfied: 1" in english
    assert "提示已满足：1" in chinese
    assert "Single-file comparison scope." in english
    assert "单文件比较范围。" in chinese
