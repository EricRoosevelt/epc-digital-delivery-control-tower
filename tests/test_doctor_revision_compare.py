"""Fresh IFC evidence, rather than manual closure, drives revision comparison."""

from copy import deepcopy

import ifcopenshell
import pytest

from internal.doctor_adapter.review import ReviewStore
from internal.doctor_adapter.revision_compare import compare_revisions


GUID = ifcopenshell.guid.compress("0123456789abcdef0123456789abcdef")


def report(kind="NOTDEFINED", name="Terminal", ifc_class="IfcAirTerminal", *,
           duplicate=False, root_collision=False, typed=False, guid=GUID, empty=False):
    model = ifcopenshell.file(schema="IFC4")
    if not empty:
        kwargs = {"GlobalId": guid, "Name": name, "Tag": "A"}
        if ifc_class == "IfcAirTerminal":
            kwargs["PredefinedType"] = "GRILLE" if typed else kind
        element = model.create_entity(ifc_class, **kwargs)
        if duplicate:
            model.create_entity("IfcWall", GlobalId=guid, Name="Duplicate")
        if root_collision or typed:
            source_type = model.create_entity(
                "IfcAirTerminalType", GlobalId=guid if root_collision else
                ifcopenshell.guid.compress("1123456789abcdef0123456789abcdef"),
                PredefinedType="USERDEFINED", ElementType=kind,
            )
            if typed:
                model.create_entity(
                    "IfcRelDefinesByType",
                    GlobalId=ifcopenshell.guid.compress("2123456789abcdef0123456789abcdef"),
                    RelatedObjects=[element], RelatingType=source_type,
                )
    return ReviewStore().create(name + ".ifc", model.to_string().encode())


def envelope(rep, revision="r1", **metadata):
    return {"revision": {"revision_id": revision, "project_id": "p", "model_id": "slot",
                         **metadata}, "report": rep, "followups": []}


def compare(before, after):
    return compare_revisions(envelope(before), envelope(after, "r2"))


def pv(result):
    return [row for row in result["rows"] if row["rule_id"] == "PV-001"]


def test_real_reexport_pass_joins_stable_guid_despite_filename_name_and_sha_changes():
    before, after = report(), report("DIFFUSER", name="Renamed object")
    assert before["elements"][0]["element_key"] != after["elements"][0]["element_key"]
    row = pv(compare(before, after))[0]
    assert row["change"] == "resolved"
    assert (row["before_status"], row["after_status"]) == ("FAIL", "PASS")
    assert row["before_actual"] == "NOTDEFINED" and row["after_actual"] == "DIFFUSER"
    assert row["before_element_key"] == before["elements"][0]["element_key"]
    assert row["after_element_key"] == after["elements"][0]["element_key"]


def test_deleted_failed_element_is_missing_never_resolved():
    result = compare(report(), report(empty=True))
    assert pv(result)[0]["change"] == "missing"
    assert pv(result)[0]["after_element_key"] is None
    assert result["summary"]["resolved"] == 0


def test_class_change_exposes_changed_basis_without_claiming_a_repair():
    row = pv(compare(report(), report(ifc_class="IfcWall")))[0]
    assert row["change"] == "not_comparable"
    assert row["reason_code"] == "class_changed"
    assert row["after_class"] == "IfcWall"
    assert row["after_status"] == "NOT_APPLICABLE"


@pytest.mark.parametrize("option", [{"duplicate": True}, {"root_collision": True},
                                    {"guid": "invalid"}])
def test_ambiguous_or_invalid_identity_cannot_be_joined_to_a_unique_guid(option):
    result = compare(report(**option), report("DIFFUSER"))
    rows = pv(result)
    assert all(row["change"] == "not_comparable" for row in rows)
    assert all(not (row["before_finding_id"] and row["after_finding_id"]) for row in rows)
    assert result["summary"]["resolved"] == 0


def test_duplicate_current_guid_does_not_make_old_failure_missing_or_resolved():
    result = compare(report(), report("DIFFUSER", duplicate=True))
    assert {row["change"] for row in pv(result)} == {"not_comparable"}


@pytest.mark.parametrize("field,value", [("expected", "NEW VALUE"),
                                         ("scope", "A different scope"),
                                         ("predicate_version", "different-predicate-version")])
def test_changed_rule_predicate_cannot_claim_pass_as_resolution(field, value):
    before, after = report(), report("DIFFUSER")
    after["rules"][0][field] = value
    row = pv(compare(before, after))[0]
    assert row["change"] == "not_comparable" and row["reason_code"] == "rule_changed"
    assert row["before_predicate"] != row["after_predicate"]


def test_changed_finding_expected_alone_is_still_a_basis_change():
    after = report("DIFFUSER")
    after["findings"][0]["expected"] = "Changed requirement"
    assert pv(compare(report(), after))[0]["reason_code"] == "rule_changed"


def test_unversioned_historical_predicates_cannot_establish_same_checking_basis():
    before, after = report(), report("DIFFUSER")
    for rep in (before, after):
        for key in ("predicate_version", "semantics_digest", "version"):
            rep["rules"][0].pop(key, None)
    assert pv(compare(before, after))[0]["reason_code"] == "rule_changed"


def test_missing_rule_or_missing_finding_is_not_a_pass():
    before, after = report(), report("DIFFUSER")
    after["findings"] = [f for f in after["findings"] if f["rule_id"] != "PV-001"]
    assert pv(compare(before, after))[0]["reason_code"] == "missing_finding"
    after["rules"] = [r for r in after["rules"] if r["rule_id"] != "PV-001"]
    assert pv(compare(before, after))[0]["reason_code"] == "rule_changed"


def test_no_finding_on_either_side_never_infers_pass():
    before, after = report(), report()
    before["findings"] = after["findings"] = []
    assert compare(before, after)["rows"] == []


def test_effective_type_text_from_assigned_type_drives_the_real_recheck():
    before = report("SPECIAL", typed=True)
    after = report("LOUVRE", typed=True)
    row = pv(compare(before, after))[0]
    assert row["change"] == "resolved"
    assert row["before_actual"] == "SPECIAL" and row["after_actual"] == "LOUVRE"


def test_remaining_and_new_failures_have_distinct_meanings():
    assert pv(compare(report(), report("USERDEFINED")))[0]["change"] == "remaining"
    assert pv(compare(report("DIFFUSER"), report()))[0]["change"] == "new"


def test_fail_to_na_with_stable_class_is_no_longer_applicable_not_resolved():
    before, after = report(), report()
    after["findings"][0]["status"] = "NOT_APPLICABLE"
    assert pv(compare(before, after))[0]["change"] == "not_applicable"


def test_manual_ready_for_recheck_never_changes_machine_comparison():
    before, after = envelope(report()), envelope(report(), "r2")
    plain = compare_revisions(before, after)
    before["followups"] = [{"finding_id": before["report"]["findings"][0]["finding_id"],
                            "status": "ready_for_recheck"}]
    after["followups"] = deepcopy(before["followups"])
    assert compare_revisions(before, after) == plain


def test_info_counts_do_not_inflate_error_counts_and_unchanged_pass_is_omitted():
    result = compare(report(), report())
    assert result["summary"]["errors"]["remaining"] == 1
    assert result["summary"]["information"]["remaining"] == 1
    assert result["summary"]["remaining"] == 2
    assert not any(row["before_status"] == row["after_status"] == "PASS"
                   for row in result["rows"])


@pytest.mark.parametrize("metadata", [{"model_id": "other"}, {"project_id": "other"}])
def test_cross_slot_or_project_scope_is_rejected_even_with_same_guid(metadata):
    with pytest.raises(ValueError):
        compare_revisions(envelope(report()), envelope(report(), "r2", **metadata))


def test_federated_reports_never_join_same_globalid_from_different_files():
    before, after = report(), report("DIFFUSER")
    for rep in (before, after):
        rep["models"].append({"model_key": "second-file", "schema": "IFC4"})
    after["models"] = deepcopy(before["models"])
    result = compare(before, after)
    assert {r["change"] for r in result["rows"]} == {"not_comparable"}
    assert {r["reason_code"] for r in result["rows"]} == {"federated_report"}


def test_real_public_federation_is_retained_as_unpaired_observations():
    demo = ReviewStore().demo()
    result = compare(demo, demo)
    failed = sum(f["status"] == "FAIL" for f in demo["findings"])
    assert len(result["rows"]) == 2 * failed == 42
    assert result["summary"]["resolved"] == result["summary"]["missing"] == 0
    assert {r["reason_code"] for r in result["rows"]} == {"federated_report"}
    assert all(not (r["before_element_key"] and r["after_element_key"])
               for r in result["rows"])
    assert result["basis_change"] == "federated_report"
    assert "multiple IFC files" in result["scope_note"]
    assert all(r["before_status"] == "FAIL" or r["after_status"] == "FAIL"
               for r in result["rows"])


def test_changed_federation_roster_with_same_file_count_is_scope_changed():
    before = ReviewStore().demo()
    after = deepcopy(before)
    after["models"][0]["model_key"] = "replacement-model"
    assert {r["reason_code"] for r in compare(before, after)["rows"]} == {"scope_changed"}


def test_same_name_tag_and_step_id_do_not_replace_globalid_identity():
    after = report(guid=ifcopenshell.guid.compress("3123456789abcdef0123456789abcdef"))
    result = compare(report(), after)
    assert {r["change"] for r in pv(result)} == {"missing", "new"}


def test_unknown_check_status_cannot_be_closed_as_a_success():
    after = report("DIFFUSER")
    after["findings"][0]["status"] = "ERROR"
    assert pv(compare(report(), after))[0]["reason_code"] == "unknown_status"


def test_single_to_federation_scope_change_is_explicit():
    after = report("DIFFUSER")
    after["models"].append({"model_key": "second", "schema": "IFC4"})
    assert {r["reason_code"] for r in compare(report(), after)["rows"]} == {"scope_changed"}


def test_schema_change_is_exposed_even_with_equal_rule_text():
    after = report("DIFFUSER")
    after["models"][0]["schema"] = "IFC2X3"
    assert pv(compare(report(), after))[0]["reason_code"] == "schema_changed"


def test_duplicate_findings_do_not_silently_overwrite_evidence():
    after = report("DIFFUSER")
    after["findings"].append(deepcopy(after["findings"][0]))
    assert pv(compare(report(), after))[0]["reason_code"] == "ambiguous_finding"


def test_pure_deterministic_result_preserves_both_revision_evidence():
    before, after = envelope(report()), envelope(report("DIFFUSER"), "r2")
    originals = deepcopy((before, after))
    result = compare_revisions(before, after)
    assert (before, after) == originals
    assert result == compare_revisions(before, after)
    row = pv(result)[0]
    assert row["reason_zh"] and row["before_citation"] and row["after_citation"]
    result["before_revision"]["model_id"] = "mutated"
    assert before["revision"]["model_id"] == "slot"
