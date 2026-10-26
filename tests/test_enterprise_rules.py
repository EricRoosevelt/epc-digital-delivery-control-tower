"""Public synthetic packages exercise the native compiler and real IFC evaluator."""

from copy import deepcopy
import hashlib
from io import BytesIO
import json
from zipfile import ZipFile

import ifcopenshell
import pytest

from internal.doctor_adapter.enterprise_rules import evaluate_rules, parse_package
from internal.doctor_adapter.review import ReviewStore
from tools.enterprise_rules_example import example_package


META = '[ruleset]\nruleset_id="company-checks"\nversion="1"\ntitle="Public checks"\n'
RULE = """rule_id="COMPANY-01"
title="Terminals have an allowed type and readable name"
checker="ids"
ifc_version=["IFC4"]
[[applicability]]
facet="entity"
name="IFCAIRTERMINAL"
[[requirements]]
facet="entity"
name="IFCAIRTERMINAL"
[requirements.predefinedType]
enumeration=["DIFFUSER","LOUVRE"]
[[requirements]]
facet="attribute"
name="Name"
"""


def manifest():
    return {
        "schema_version": 1,
        "package_id": "public-company",
        "version": "1",
        "title": "Public synthetic requirements",
        "source": {
            "organization": "Example author",
            "reference": "Synthetic test",
            "issued_on": "2026-10-26",
        },
        "purposes": [
            {
                "purpose_id": "schedule",
                "title": "Equipment schedule",
                "from_role": "MEP",
                "to_role": "Coordinator",
                "subject_classes": ["IfcAirTerminal"],
                "required_rule_ids": ["COMPANY-01"],
                "requires_counterpart": False,
                "evidence_requirements": [],
            }
        ],
    }


def package_bytes(rule=RULE, *, extra=None, declaration=None):
    stream = BytesIO()
    with ZipFile(stream, "w") as archive:
        archive.writestr("manifest.json", json.dumps(declaration or manifest()))
        archive.writestr("rules/ruleset.toml", META)
        archive.writestr("rules/company.toml", rule)
        for name, data in (extra or {}).items():
            archive.writestr(name, data)
    return stream.getvalue()


@pytest.mark.parametrize("field", ["package_id", "purpose_id", "evidence_id"])
def test_manifest_identifiers_cannot_break_purpose_reference_coordinates(field):
    document = manifest()
    if field == "package_id":
        document[field] = "company::other"
    elif field == "purpose_id":
        document["purposes"][0][field] = "handover::other"
    else:
        document["purposes"][0]["evidence_requirements"] = [{
            "evidence_id": "evidence::other", "title": "Unsupported example",
            "acceptance": "Need evidence", "execution": "unsupported", "reason": "No engine",
        }]
    with pytest.raises(ValueError, match="identifier|reserved|separator"):
        parse_package(package_bytes(declaration=document), "public.zip")


def test_declared_discipline_filter_cannot_be_claimed_executed_from_an_unknown_upload():
    body = package_bytes(rule='discipline_scope=["Mechanical"]\n' + RULE)
    package = parse_package(body, "public.zip")
    assert all(check["support"] == "unsupported" for check in package.checks)
    assert any("discipline_scope" in reason for check in package.checks
               for reason in check["unsupported_reasons"])


def model_case(*, schema="IFC4", predefined="DIFFUSER", name="Public terminal", typed=False):
    model = ifcopenshell.file(schema=schema)
    terminal = model.create_entity(
        "IfcAirTerminal", GlobalId=ifcopenshell.guid.new(), Name=name, PredefinedType=predefined
    )
    if typed:
        kind = model.create_entity(
            "IfcAirTerminalType",
            GlobalId=ifcopenshell.guid.new(),
            PredefinedType="USERDEFINED",
            ElementType="LOUVRE",
        )
        model.create_entity(
            "IfcRelDefinesByType",
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[terminal],
            RelatingType=kind,
        )
    return model, terminal


def evaluate(model, rule=RULE):
    body = model.to_string().encode()
    report = ReviewStore().create("public.ifc", body)
    return evaluate_rules(
        parse_package(package_bytes(rule), "checks.zip"), body, report, "stable-slot"
    ), report


def test_example_is_reproducible_native_package_with_provenance():
    body = example_package()
    assert body == example_package()
    package = parse_package(body, "example.zip")
    preview = package.preview()
    assert package.source_sha256 == hashlib.sha256(body).hexdigest()
    assert package.definition.rules
    assert preview["rules"] and preview["purposes"]
    assert all(check["semantics_digest"] for check in package.checks)
    assert preview["executable"] is True


@pytest.mark.parametrize(
    "predefined,typed,expected",
    [("DIFFUSER", False, "PASS"), ("NOTDEFINED", True, "PASS"), ("GRILLE", False, "FAIL")],
)
def test_native_inheritance_userdefined_and_independent_requirements(
    predefined, typed, expected
):
    model, terminal = model_case(predefined=predefined, typed=typed)
    result, report = evaluate(model)
    assert len(result["checks"]) == 2
    assert [f["status"] for f in result["findings"]] == [expected, "PASS"]
    element = next(e for e in result["elements"] if e["step_id"] == terminal.id())
    assert element["model_key"] == "stable-slot"
    assert element["element_key"] == "stable-slot::" + terminal.GlobalId
    assert element["review_element_key"] == report["elements"][0]["element_key"]
    assert "IfcElement" in element["class_ancestors"]
    assert result["models"][0]["content_id"] == report["source"]["sha256"]
    assert all(f["checker"]["engine"] == "ifctester" for f in result["findings"])


def test_execution_does_not_call_geometry_and_binds_step_not_globalid(monkeypatch):
    from internal.doctor_adapter import review

    model, _ = model_case()
    body = model.to_string().encode()
    report = ReviewStore().create("public.ifc", body)

    def forbidden(*args, **kwargs):
        raise AssertionError("Enterprise execution tessellated geometry")

    monkeypatch.setattr(review, "_mesh", forbidden)
    monkeypatch.setattr(ReviewStore, "geometry_payload", forbidden)
    result = evaluate_rules(parse_package(package_bytes(), "rules.zip"), body, report, "slot")
    assert all(f["status"] == "PASS" for f in result["findings"])
    altered = deepcopy(report)
    altered["elements"][0]["step_id"] += 100
    other = evaluate_rules(parse_package(package_bytes(), "rules.zip"), body, altered, "slot")
    assert not other["elements"][0]["review_element_key"]


def test_real_property_set_requirement_is_executed():
    model, terminal = model_case()
    model.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="Public project")
    value = model.create_entity(
        "IfcPropertySingleValue",
        Name="AssetId",
        NominalValue=model.create_entity("IfcLabel", "A-01"),
    )
    pset = model.create_entity(
        "IfcPropertySet",
        GlobalId=ifcopenshell.guid.new(),
        Name="Pset_Company",
        HasProperties=[value],
    )
    model.create_entity(
        "IfcRelDefinesByProperties",
        GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=[terminal],
        RelatingPropertyDefinition=pset,
    )
    rule = (
        RULE.split("[[requirements]]")[0]
        + """[[requirements]]
facet="property"
propertySet="Pset_Company"
baseName="AssetId"
value="A-01"
dataType="IFCLABEL"
"""
    )
    result, _ = evaluate(model, rule)
    assert result["findings"][0]["status"] == "PASS"
    result, _ = evaluate(model, rule.replace('value="A-01"', 'value="A-02"'))
    assert result["findings"][0]["status"] == "FAIL"


def test_unknown_field_cannot_silently_produce_pass():
    package = parse_package(
        package_bytes(RULE.replace('name="Name"', 'name="Name"\nvale="not-evaluated"')),
        "unknown.zip",
    )
    assert package.preview()["executable"] is False
    assert any("vale" in str(c["unsupported_reasons"]) for c in package.checks)
    model, _ = model_case()
    body = model.to_string().encode()
    result = evaluate_rules(package, body, ReviewStore().create("a.ifc", body), "slot")
    assert result["findings"] == []
    assert all(
        c["support"] == "unsupported" and c["evaluated"] == 0 for c in result["coverage"]
    )


def test_unknown_checker_is_visible_but_not_executed():
    package = parse_package(
        package_bytes(RULE.replace('checker="ids"', 'checker="fire-code"')), "unknown.zip"
    )
    assert package.checks and all(c["support"] == "unsupported" for c in package.checks)
    assert "fire-code" in str(package.preview())


def test_schema_mismatch_is_unknown_not_na_or_pass():
    model, _ = model_case(schema="IFC4X3")
    result, _ = evaluate(model)
    assert result["findings"] == []
    assert all(
        c["support"] == "unsupported" and c["evaluated"] == 0 for c in result["coverage"]
    )


def test_no_applicable_entities_retains_model_level_na():
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new())
    result, _ = evaluate(model)
    assert len(result["findings"]) == 2
    assert all(f["status"] == "N/A" and f["element_key"] == "" for f in result["findings"])
    assert all(c["applicable"] == 0 for c in result["coverage"])


def test_non_geometry_objects_and_duplicate_ids_are_not_lost_or_misbound():
    model, terminal = model_case()
    other = model.create_entity(
        "IfcAirTerminal", GlobalId=terminal.GlobalId, PredefinedType="GRILLE"
    )
    space = model.create_entity(
        "IfcSpace", GlobalId=ifcopenshell.guid.new(), Name="Public room"
    )
    rule = RULE.replace('name="IFCAIRTERMINAL"', 'name="IFCSPACE"')
    result, _ = evaluate(model, rule)
    assert len({e["element_key"] for e in result["elements"]}) == len(result["elements"])
    ambiguous = [e for e in result["elements"] if e["step_id"] in [terminal.id(), other.id()]]
    assert len(ambiguous) == 2 and not any(e["identity_comparable"] for e in ambiguous)
    room = next(e for e in result["elements"] if e["step_id"] == space.id())
    assert room["review_element_key"] == ""
    assert any(f["element_key"] == room["element_key"] for f in result["findings"])


def test_rule_content_and_source_change_are_frozen_separately():
    before = parse_package(package_bytes(), "a.zip")
    after = parse_package(package_bytes(RULE.replace('"LOUVRE"', '"GRILLE"')), "a.zip")
    assert before.manifest["version"] == after.manifest["version"]
    assert before.source_sha256 != after.source_sha256
    assert before.checks[0]["semantics_digest"] != after.checks[0]["semantics_digest"]
    assert before.checks[1]["semantics_digest"] == after.checks[1]["semantics_digest"]


@pytest.mark.parametrize(
    "name", ["../escape.toml", "rules/../../escape.toml", "C:/evil.toml", "rules\\evil.toml"]
)
def test_archive_paths_cannot_escape(name):
    with pytest.raises(ValueError):
        parse_package(package_bytes(extra={name: "bad"}), "bad.zip")


def test_malformed_and_unbound_manifest_are_rejected():
    with pytest.raises(ValueError):
        parse_package(b"not zip", "a.zip")
    declaration = manifest()
    declaration["purposes"][0]["required_rule_ids"] = ["does-not-exist"]
    with pytest.raises(ValueError, match="does-not-exist"):
        parse_package(package_bytes(declaration=declaration), "bad.zip")


def test_wrong_source_hash_is_refused_without_evaluation():
    model, _ = model_case()
    body = model.to_string().encode()
    report = ReviewStore().create("a.ifc", body)
    with pytest.raises(ValueError, match="hash"):
        evaluate_rules(parse_package(package_bytes(), "a.zip"), body + b"\n", report, "slot")


@pytest.mark.parametrize("value", [None, "NOTDEFINED"])
def test_native_notdefined_assigned_type_falls_back_to_instance(value):
    model, terminal = model_case(predefined="DIFFUSER", typed=True)
    assigned = terminal.IsTypedBy[0].RelatingType
    if value is None:
        assigned = model.create_entity("IfcAirTerminalType", GlobalId=ifcopenshell.guid.new())
        terminal.IsTypedBy[0].RelatingType = assigned
    else:
        assigned.PredefinedType = value
    result, _ = evaluate(model)
    assert result["findings"][0]["status"] == "PASS"


def test_unknown_restriction_and_rule_fields_are_visible():
    rule = RULE.replace('title="Terminals', 'vendor_option="unimplemented"\ntitle="Terminals')
    rule = rule.replace(
        'enumeration=["DIFFUSER","LOUVRE"]', 'enumeration=["DIFFUSER","LOUVRE"]\nminLength=1'
    )
    package = parse_package(package_bytes(rule), "unknown.zip")
    assert not package.preview()["executable"]
    reasons = str(package.preview()["diagnostics"])
    assert "vendor_option" in reasons and "minLength" in reasons
    assert package.preview()["rules"][0]["declaration"]["vendor_option"] == "unimplemented"


def test_unsupported_rule_does_not_hide_separate_executable_rule():
    other = RULE.replace('rule_id="COMPANY-01"', 'rule_id="COMPANY-02"')
    package = parse_package(
        package_bytes(
            RULE.replace('checker="ids"', 'checker="unknown"'),
            extra={"rules/other.toml": other},
        ),
        "mixed.zip",
    )
    assert package.preview()["executable"]
    assert {c["support"] for c in package.checks} == {"supported", "unsupported"}
    model, _ = model_case()
    body = model.to_string().encode()
    result = evaluate_rules(package, body, ReviewStore().create("a.ifc", body), "slot")
    assert {f["rule_id"] for f in result["findings"]} == {"COMPANY-02"}
    assert {c["rule_id"] for c in result["coverage"]} == {"COMPANY-01", "COMPANY-02"}


def test_native_outcomes_are_stable_and_do_not_leak_between_executions():
    model, terminal = model_case(predefined="GRILLE")
    package = parse_package(package_bytes(), "public.zip")
    body = model.to_string().encode()
    report = ReviewStore().create("a.ifc", body)
    first = evaluate_rules(package, body, report, "slot")
    assert first == evaluate_rules(package, body, report, "slot")
    terminal.PredefinedType = "DIFFUSER"
    passing = model.to_string().encode()
    second = evaluate_rules(package, passing, ReviewStore().create("b.ifc", passing), "slot")
    assert first["elements"][0]["element_key"] == second["elements"][0]["element_key"]
    assert first["findings"][0]["status"] == "FAIL"
    assert second["findings"][0]["status"] == "PASS"


def test_nonroot_native_subject_remains_visible_without_mesh_link():
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcCartesianPoint", Coordinates=(1.0, 2.0, 3.0))
    rule = RULE.split("[[requirements]]")[0].replace(
        'name="IFCAIRTERMINAL"', 'name="IFCCARTESIANPOINT"'
    )
    rule += '[[requirements]]\nfacet="attribute"\nname="Coordinates"\n'
    result, _ = evaluate(model, rule)
    assert len(result["elements"]) == 1
    assert result["findings"][0]["status"] == "PASS"
    assert not result["elements"][0]["identity_comparable"]
    assert not result["elements"][0]["review_element_key"]


@pytest.mark.parametrize("name", ["rules//other.toml", "./rules/other.toml"])
def test_noncanonical_archive_aliases_cannot_overwrite_rules(name):
    with pytest.raises(ValueError):
        parse_package(package_bytes(extra={name: RULE}), "alias.zip")


def test_package_expansion_and_duplicate_paths_are_rejected():
    with pytest.raises(ValueError, match="budget"):
        parse_package(
            package_bytes(extra={"rules/large.toml": "x" * (513 * 1024)}), "large.zip"
        )
    stream = BytesIO(package_bytes())
    with pytest.warns(UserWarning), ZipFile(stream, "a") as archive:
        archive.writestr("rules/company.toml", RULE)
    with pytest.raises(ValueError, match="duplicate"):
        parse_package(stream.getvalue(), "duplicate.zip")


def test_preview_copy_and_hypotheses_do_not_change_executable_evidence():
    package = parse_package(example_package(), "example.zip")
    before = package.preview()
    assert before["rules"][0]["hypotheses"][0]["verified"] is False
    before["checks"][0]["expected"] = "changed response"
    assert package.preview()["checks"][0]["expected"] != "changed response"


def test_example_has_distinct_internal_tender_and_handover_questions():
    purposes = {
        p["purpose_id"]: p
        for p in parse_package(example_package(), "public.zip").manifest["purposes"]
    }
    internal = purposes["terminal-schedule"]
    tender = purposes["tender-submission"]
    handover = purposes["mep-to-architecture"]
    assert internal["evidence_requirements"] == []
    assert tender["evidence_requirements"][0]["execution"] == "manual"
    assert handover["requires_counterpart"] is True
    assert handover["evidence_requirements"][0]["execution"] == "unsupported"
    assert (
        internal["required_rule_ids"]
        == tender["required_rule_ids"]
        == handover["required_rule_ids"]
    )


def test_missing_native_facet_field_is_a_readable_package_error():
    rule = RULE.replace('name="Name"', 'value="missing-field"')
    with pytest.raises(ValueError, match="facet|name"):
        parse_package(package_bytes(rule), "invalid.zip")


def test_declared_schema_without_any_supported_engine_is_visible_in_preview():
    rule = RULE.replace('ifc_version=["IFC4"]', 'ifc_version=["IFC4X3"]')
    package = parse_package(package_bytes(rule), "future-schema.zip")
    assert package.preview()["executable"] is False
    assert all(check["support"] == "unsupported" for check in package.checks)
    assert "IFC4X3" in str(package.preview()["diagnostics"])


def test_zero_attribute_source_evidence_is_not_reported_as_missing():
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcBuildingStorey", GlobalId=ifcopenshell.guid.new(), Elevation=0.0)
    rule = RULE.split("[[requirements]]")[0].replace(
        'name="IFCAIRTERMINAL"', 'name="IFCBUILDINGSTOREY"'
    )
    rule += '[[requirements]]\nfacet="attribute"\nname="Elevation"\nvalue="0"\n'
    result, _ = evaluate(model, rule)
    assert result["findings"][0]["status"] == "PASS"
    assert result["findings"][0]["actual"] == "0.0"
