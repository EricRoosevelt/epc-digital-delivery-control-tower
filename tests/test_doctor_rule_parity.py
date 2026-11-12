"""Independent same-input checks pin legacy PV-001 before and after adapter sharing."""

from copy import deepcopy
import json
import shutil

import ifcopenshell
import pytest
from ifctester import ids

from epc_control_tower.rule_definitions import compile_document, load_rule_definitions
from helpers import PROJECT_ROOT
from internal.doctor_adapter.review import ReviewStore
from internal.doctor_adapter.revision_compare import compare_revisions
from rule_parity_cases import CASES, measure, model_bytes

BASELINE = json.loads(
    (PROJECT_ROOT / "docs/handoffs/rule-parity-baseline.json").read_text(encoding="utf-8")
)
ORIGINAL = {item["case"]: item for item in BASELINE["cases"]}


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_same_input_status_agrees_with_real_legacy_checker(case):
    measured = measure(case)
    baseline = ORIGINAL[case.name]
    assert measured["pipeline"] == baseline["pipeline"]
    assert measured["legacy"] == baseline["legacy"]
    assert all(f["actual"] == "" for f in measured["legacy"])
    expected = measured["legacy"][0]["status"]
    if case.empty:
        assert expected == "N/A" and measured["runtime"] == []
    elif expected == "N/A":
        assert measured["runtime"][0]["status"] == "NOT_APPLICABLE"
        assert not measured["legacy"][0]["element_scope"]
    else:
        assert measured["runtime"][0]["status"] == expected
        assert measured["legacy"][0]["element_scope"]
    if case.name != "ifc2x3-other-class-type-mapping":
        assert measured["runtime"] == baseline["runtime"]
    else:
        assert baseline["runtime"][0]["status"] == "NOT_APPLICABLE"
        assert measured["runtime"][0] == {"status": "PASS", "actual": "DIFFUSER"}


def test_workbench_rule_snapshot_is_derived_from_the_loaded_source():
    report = ReviewStore().create("case.ifc", model_bytes(CASES[0])[0])
    definition = load_rule_definitions(PROJECT_ROOT / "rules/product-validation")
    _, ruleset, expectations = compile_document(definition)
    source_rule, requirement = definition.rules[0], ruleset.requirements[0]
    pv = report["rules"][0]
    assert pv["predicate_version"] == "2"
    assert pv["title"] == source_rule.title
    assert pv["citation"] == source_rule.citation
    assert pv["severity"] == source_rule.severity.value
    assert pv["expected"] == expectations[requirement.requirement_key]
    assert pv["semantics_digest"] == requirement.semantics_digest
    assert pv["ruleset_version"] == ruleset.version == "1.0"
    assert pv["ruleset_digest"] == ruleset.normalized_digest
    assert pv["declared_ifc_versions"] == ["IFC4"]
    assert [rule["predicate_version"] for rule in report["rules"][1:]] == ["1", "1", "1"]


def test_workbench_uses_loaded_restriction_not_a_copied_enum(tmp_path):
    rules = tmp_path / "rules/product-validation"
    shutil.copytree(PROJECT_ROOT / "rules/product-validation", rules)
    path = rules / "PV-001.toml"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"LOUVRE", "REGISTER"]', '"LOUVRE"]'), encoding="utf-8")
    model = model_bytes(next(c for c in CASES if c.name == "enum-register"))[0]
    before = ReviewStore().create("register.ifc", model)
    after = ReviewStore(rule_library_path=rules).create("register.ifc", model)
    assert before["findings"][0]["status"] == "PASS"
    assert after["findings"][0]["status"] == "FAIL"
    assert before["rules"][0]["semantics_digest"] != after["rules"][0]["semantics_digest"]
    assert before["review_id"] != after["review_id"]


def test_ifctester_validation_runs_once_per_model_not_per_element(monkeypatch):
    calls = []
    original = ids.Ids.validate

    def counted(self, model, *args, **kwargs):
        calls.append(model)
        return original(self, model, *args, **kwargs)

    monkeypatch.setattr(ids.Ids, "validate", counted)
    model = ifcopenshell.file(schema="IFC4")
    for _ in range(4):
        model.create_entity(
            "IfcAirTerminal", GlobalId=ifcopenshell.guid.new(), PredefinedType="DIFFUSER"
        )
    store = ReviewStore()
    report = store.create("four.ifc", model.to_string().encode())
    assert len(calls) == 1
    assert (
        sum(f["status"] == "PASS" for f in report["findings"] if f["rule_id"] == "PV-001") == 4
    )
    store.demo()
    assert len(calls) == 4


def test_fresh_validation_state_does_not_leak_between_models():
    store = ReviewStore()
    passing = store.create("pass.ifc", model_bytes(CASES[0])[0])
    failing = store.create("fail.ifc", model_bytes(CASES[4])[0])
    assert passing["findings"][0]["status"] == "PASS"
    assert failing["findings"][0]["status"] == "FAIL"
    assert store.get(passing["review_id"]) == passing


def test_old_runtime_snapshot_stays_distinct_and_does_not_claim_v2_resolution():
    report = ReviewStore().create("case.ifc", model_bytes(CASES[0])[0])
    old = deepcopy(report)
    old["rules"] = deepcopy(BASELINE["original_runtime_rules"])

    def envelope(value, revision):
        return {
            "revision": {"project_id": "public", "model_id": "slot", "revision_id": revision},
            "report": value,
            "followups": [],
        }

    comparison = compare_revisions(envelope(old, "v1"), envelope(report, "v2"))
    pv = [row for row in comparison["rows"] if row["rule_id"] == "PV-001"]
    assert pv and all(row["reason_code"] == "rule_changed" for row in pv)
    assert comparison["summary"]["resolved"] == 0
    assert old["rules"][0]["predicate_version"] == "1"
    assert report["rules"][0]["predicate_version"] == "2"


@pytest.mark.parametrize("field", ["engine", "engine_version", "checker_version"])
def test_changed_execution_basis_cannot_turn_a_failure_into_a_claimed_repair(field):
    failed = ReviewStore().create("before.ifc", model_bytes(CASES[4])[0])
    passed = ReviewStore().create("after.ifc", model_bytes(CASES[0])[0])
    passed["rules"][0][field] = "different-execution-basis"

    def envelope(report, revision):
        return {
            "revision": {"project_id": "public", "model_id": "slot", "revision_id": revision},
            "report": report,
            "followups": [],
        }

    compared = compare_revisions(envelope(failed, "before"), envelope(passed, "after"))
    pv = next(row for row in compared["rows"] if row["rule_id"] == "PV-001")
    assert pv["reason_code"] == "rule_changed"
    assert pv["change"] == "not_comparable"
    assert compared["summary"]["errors"]["resolved"] == 0
