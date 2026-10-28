"""Runtime IFC review; published pipeline artifacts are never rewritten."""

import importlib.util
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import ifcopenshell
import pytest

from helpers import PROJECT_ROOT
from internal.doctor_adapter.review import ReviewStore, ReviewInputError


def model_bytes(duplicate=False):
    model = ifcopenshell.file(schema="IFC4")
    guid = ifcopenshell.guid.new()
    model.create_entity("IfcWall", GlobalId=guid, Name="Wall A", Tag="W-01")
    model.create_entity("IfcWall", GlobalId=guid if duplicate else ifcopenshell.guid.new())
    model.create_entity(
        "IfcAirTerminal",
        GlobalId=ifcopenshell.guid.new(),
        Name="Supply",
        PredefinedType="DIFFUSER",
    )
    model.create_entity(
        "IfcAirTerminal",
        GlobalId=ifcopenshell.guid.new(),
        Name="Undefined",
        PredefinedType="NOTDEFINED",
    )
    return model.to_string().encode("utf-8")


def test_review_upload_real_entities_and_rule_evidence():
    store = ReviewStore()
    report = store.create("small.ifc", model_bytes())
    assert report["source"]["kind"] == "upload"
    assert report["summary"]["elements"] == 4
    assert len({item["element_key"] for item in report["elements"]}) == 4
    pv = [item for item in report["findings"] if item["rule_id"] == "PV-001"]
    assert {item["status"] for item in pv} == {"PASS", "FAIL", "NOT_APPLICABLE"}
    assert sum(item["status"] == "PASS" for item in pv) == 1
    assert all(item["citation"] and item["reason"] for item in pv)
    assert store.get(report["review_id"]) == report
    geometry = store.geometry(report["review_id"])
    assert not geometry["meshes"]
    assert len(geometry["unavailable"]) == 4


def test_duplicate_global_ids_never_select_the_wrong_entity():
    store = ReviewStore()
    report = store.create("duplicate.ifc", model_bytes(duplicate=True))
    walls = [item for item in report["elements"] if item["ifc_class"] == "IfcWall"]
    assert walls[0]["global_id"] == walls[1]["global_id"]
    assert walls[0]["element_key"] != walls[1]["element_key"]
    assert all(item["element_key"].startswith(item["model_key"] + "::") for item in walls)
    failures = [
        item
        for item in report["findings"]
        if item["status"] == "FAIL" and item["rule_id"] == "ID-001"
    ]
    assert {item["element_key"] for item in failures} >= {w["element_key"] for w in walls}


@pytest.mark.parametrize(
    "filename,body", [("bad.txt", b"not IFC"), ("bad.ifc", b"not IFC"), ("empty.ifc", b"")]
)
def test_invalid_upload_is_a_useful_input_error(filename, body):
    with pytest.raises(ReviewInputError):
        ReviewStore().create(filename, body)


def test_demo_real_federation_meshes_are_bound_and_finite():
    store = ReviewStore()
    report = store.demo()
    geometry = store.geometry(report["review_id"])
    assert len(report["models"]) == 3
    assert report["source"]["attribution"]
    assert report["summary"]["renderable"] > 0
    assert report == store.demo()
    keys = {item["element_key"] for item in report["elements"]}
    assert {mesh["element_key"] for mesh in geometry["meshes"]} <= keys
    for mesh in geometry["meshes"]:
        assert len(mesh["positions"]) % 3 == 0
        assert len(mesh["indices"]) % 3 == 0
        assert max(mesh["indices"]) < len(mesh["positions"]) // 3
    json.dumps(geometry, allow_nan=False)
    json.dumps(report, allow_nan=False)


def test_review_http_upload_report_and_geometry_share_identity():
    spec = importlib.util.spec_from_file_location(
        "review_serve", PROJECT_ROOT / "doctor/serve.py"
    )
    serve = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(serve)
    store = ReviewStore()
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), serve.make_handler(lambda: None, review_factory=lambda: store)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        request = urllib.request.Request(
            base + "/api/review/models?filename=small.ifc",
            data=model_bytes(),
            headers={"Content-Type": "application/octet-stream"},
        )
        report = json.load(urllib.request.urlopen(request))
        review_id = report["review_id"]
        url = base + "/api/review/report?review=" + review_id
        assert json.load(urllib.request.urlopen(url)) == report
        url = base + "/api/review/geometry?review=" + review_id
        assert len(json.load(urllib.request.urlopen(url))["unavailable"]) == 4
        with pytest.raises(urllib.error.HTTPError) as missing:
            urllib.request.urlopen(base + "/api/review/report?review=unknown")
        assert missing.value.code == 404
    finally:
        server.shutdown()
        server.server_close()


def test_effective_terminal_type_matches_existing_pv_semantics():
    model = ifcopenshell.file(schema="IFC4")
    terminal = model.create_entity(
        "IfcAirTerminal", GlobalId=ifcopenshell.guid.new(), PredefinedType="GRILLE"
    )
    assigned = model.create_entity(
        "IfcAirTerminalType",
        GlobalId=ifcopenshell.guid.new(),
        PredefinedType="USERDEFINED",
        ElementType="LOUVRE",
    )
    model.create_entity(
        "IfcRelDefinesByType",
        GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=[terminal],
        RelatingType=assigned,
    )
    report = ReviewStore().create("typed.ifc", model.to_string().encode())
    pv = next(f for f in report["findings"] if f["rule_id"] == "PV-001")
    assert pv["actual"] == "LOUVRE"
    assert pv["status"] == "PASS"


def test_storey_resolves_through_aggregate_and_opening_parent():
    model = ifcopenshell.file(schema="IFC4")
    storey = model.create_entity(
        "IfcBuildingStorey", GlobalId=ifcopenshell.guid.new(), Name="Ground"
    )
    wall = model.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), Name="Assembly")
    part = model.create_entity("IfcBuildingElementPart", GlobalId=ifcopenshell.guid.new())
    opening = model.create_entity("IfcOpeningElement", GlobalId=ifcopenshell.guid.new())
    model.create_entity(
        "IfcRelContainedInSpatialStructure",
        GlobalId=ifcopenshell.guid.new(),
        RelatedElements=[wall],
        RelatingStructure=storey,
    )
    model.create_entity(
        "IfcRelAggregates",
        GlobalId=ifcopenshell.guid.new(),
        RelatingObject=wall,
        RelatedObjects=[part],
    )
    model.create_entity(
        "IfcRelVoidsElement",
        GlobalId=ifcopenshell.guid.new(),
        RelatingBuildingElement=wall,
        RelatedOpeningElement=opening,
    )
    report = ReviewStore().create("nested.ifc", model.to_string().encode())
    assert {item["storey"] for item in report["elements"]} == {"Ground"}
    assert all(f["status"] == "PASS" for f in report["findings"] if f["rule_id"] == "INFO-002")


def test_report_and_geometry_cannot_be_mutated_by_callers():
    store = ReviewStore()
    report = store.create("small.ifc", model_bytes())
    review_id = report["review_id"]
    report["findings"].clear()
    report["elements"].clear()
    geometry = store.geometry(review_id)
    geometry["unavailable"].clear()
    assert len(store.get(review_id)["findings"]) == 16
    assert len(store.get(review_id)["elements"]) == 4
    assert len(store.geometry(review_id)["unavailable"]) == 4


def test_duplicate_geometry_is_bound_by_step_entity_not_guid():
    import ifcopenshell.api

    model = ifcopenshell.api.run("project.create_file", version="IFC4")
    ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject")
    ifcopenshell.api.run("unit.assign_unit", model)
    context = ifcopenshell.api.run("context.add_context", model, context_type="Model")
    body = ifcopenshell.api.run(
        "context.add_context",
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=context,
    )
    walls = []
    for length in (2.0, 5.0):
        wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")
        representation = ifcopenshell.api.run(
            "geometry.add_wall_representation",
            model,
            context=body,
            length=length,
            height=3.0,
            thickness=0.2,
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", model, product=wall, representation=representation
        )
        walls.append(wall)
    walls[1].GlobalId = walls[0].GlobalId
    store = ReviewStore()
    report = store.create("two-walls.ifc", model.to_string().encode())
    meshes = store.geometry(report["review_id"])["meshes"]
    assert len(meshes) == 2
    assert len({m["element_key"] for m in meshes}) == 2
    lengths = [max(m["positions"][::3]) - min(m["positions"][::3]) for m in meshes]
    assert sorted(lengths) == pytest.approx([2.0, 5.0])
    assert report["summary"]["errors"] == 2


def test_ifc2x3_air_terminal_type_mapping_is_not_silently_skipped():
    model = ifcopenshell.file(schema="IFC2X3")
    terminal = model.create_entity("IfcFlowTerminal", GlobalId=ifcopenshell.guid.new())
    assigned = model.create_entity(
        "IfcAirTerminalType", GlobalId=ifcopenshell.guid.new(), PredefinedType="DIFFUSER"
    )
    model.create_entity(
        "IfcRelDefinesByType",
        GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=[terminal],
        RelatingType=assigned,
    )
    report = ReviewStore().create("legacy.ifc", model.to_string().encode())
    finding = next(f for f in report["findings"] if f["rule_id"] == "PV-001")
    assert finding["status"] == "PASS"
    assert finding["actual"] == "DIFFUSER"


def test_legacy_step_character_bytes_use_native_reader_without_changing_source(
    tmp_path, monkeypatch
):
    import hashlib
    import tempfile

    model = ifcopenshell.file(schema="IFC4")
    model.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new(), Name="public-name")
    body = model.to_string().encode().replace(b"public-name", b"public-\xb5")
    reference = tmp_path / "native-reference.ifc"
    reference.write_bytes(body)
    expected_name = ifcopenshell.open(reference).by_type("IfcWall")[0].Name
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    report = ReviewStore().create("legacy-text.ifc", body)
    assert report["elements"][0]["name"] == expected_name
    assert report["source"]["sha256"] == hashlib.sha256(body).hexdigest()
    assert report["models"][0]["sha256"] == hashlib.sha256(body).hexdigest()
    assert reference.read_bytes() == body
    assert sorted(path.name for path in tmp_path.iterdir()) == ["native-reference.ifc"]
