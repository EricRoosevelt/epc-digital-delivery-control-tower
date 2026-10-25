"""The external legacy verifier compares cached reports without tessellating again."""

import hashlib
import json

import ifcopenshell
import ifcopenshell.geom
import pytest

from helpers import PROJECT_ROOT
from internal.doctor_adapter.review import ReviewStore
from tools.model_case.verify_legacy import main, verify


def inputs(tmp_path, *, terminal=True):
    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new())
    if terminal:
        model.create_entity(
            "IfcAirTerminal",
            GlobalId=ifcopenshell.guid.new(),
            Name="PRIVATE-LABEL-DO-NOT-PRINT",
            PredefinedType="LOUVRE",
        )
    model.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), Name="PRIVATE-WALL")
    source = tmp_path / "private-source.ifc"
    source.write_bytes(model.to_string().encode())
    report = ReviewStore().create(source.name, source.read_bytes())
    saved = tmp_path / "private-report.json"
    saved.write_text(json.dumps(report), encoding="utf-8")
    return source, saved, report


def test_real_legacy_registry_path_matches_cached_report_without_geometry(
    tmp_path, monkeypatch
):
    source, saved, report = inputs(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("Tessellation must not run in legacy parity verification")

    monkeypatch.setattr(ifcopenshell.geom, "create_shape", forbidden)
    monkeypatch.setattr(ReviewStore, "create", forbidden)
    output = tmp_path / "evidence"
    counts = verify(source, saved, output, expected_applicable=1)
    assert counts["matched"]
    assert counts["common_applicable"] == 1
    assert counts["workbench_not_applicable"] == 1
    assert counts["status_mismatches"] == 0
    assert counts["na_projection_matches"]
    assert list((output / "legacy-workspace/reports/ids").glob("*.html"))
    assert list((output / "legacy-workspace/ids").glob("*.ids"))
    copied = output / "legacy-workspace/projects/case/model.ifc"
    assert hashlib.sha256(copied.read_bytes()).hexdigest() == report["source"]["sha256"]


def test_zero_applicable_compares_intentional_model_and_element_na_projections(tmp_path):
    source, saved, _ = inputs(tmp_path, terminal=False)
    counts = verify(source, saved, tmp_path / "zero", expected_applicable=0)
    assert counts["matched"]
    assert counts["legacy_model_not_applicable"] == counts["workbench_not_applicable"] == 1
    assert counts["common_applicable"] == 0


def test_cli_output_contains_only_aggregate_counts_and_keeps_details_external(tmp_path, capsys):
    source, saved, report = inputs(tmp_path)
    output = tmp_path / "private-evidence"
    code = main(
        [
            "--ifc",
            str(source),
            "--report",
            str(saved),
            "--output-dir",
            str(output),
            "--expected-applicable",
            "1",
        ]
    )
    public = capsys.readouterr()
    assert code == 0
    assert json.loads(public.out)["matched"]
    for private in (
        str(source),
        report["elements"][0]["global_id"],
        report["source"]["sha256"],
        "PRIVATE-LABEL",
        report["review_id"],
    ):
        assert private not in public.out + public.err
    details = json.loads((output / "legacy-parity.json").read_text())
    assert details["source_path"] == str(source.resolve())
    assert details["details"]["status_mismatches"] == []


def test_wrong_input_report_fingerprint_is_rejected_before_legacy_run(tmp_path):
    source, saved, report = inputs(tmp_path)
    report["source"]["sha256"] = "not-the-source-hash"
    saved.write_text(json.dumps(report), encoding="utf-8")
    with pytest.raises(ValueError, match="single IFC payload"):
        verify(source, saved, tmp_path / "wrong")
    assert not (tmp_path / "wrong/legacy-workspace").exists()


def test_mismatch_is_a_nonzero_cli_result_without_publishing_globalids(tmp_path, capsys):
    source, saved, report = inputs(tmp_path)
    finding = next(
        f for f in report["findings"] if f["rule_id"] == "PV-001" and f["status"] == "PASS"
    )
    finding["status"] = "FAIL"
    saved.write_text(json.dumps(report), encoding="utf-8")
    output = tmp_path / "mismatch"
    code = main(["--ifc", str(source), "--report", str(saved), "--output-dir", str(output)])
    public = json.loads(capsys.readouterr().out)
    assert code == 1 and public["status_mismatches"] == 1
    assert public["matched"] is False
    evidence = json.loads((output / "legacy-parity.json").read_text())
    assert len(evidence["details"]["status_mismatches"]) == 1


def test_any_checkout_output_is_rejected(tmp_path):
    source, saved, _ = inputs(tmp_path)
    with pytest.raises(ValueError, match="outside checkout"):
        verify(source, saved, PROJECT_ROOT / "private-case-must-not-exist")
    other = tmp_path / "other-checkout"
    other.mkdir()
    (other / ".git").mkdir()
    with pytest.raises(ValueError, match="outside checkout"):
        verify(source, saved, other / "evidence")
    assert not (other / "evidence").exists()
