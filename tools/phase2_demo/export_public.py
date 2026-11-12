"""Export real IFC geometry from the original public editable JSON source.

This is a synthetic authoring/export fixture, not a Revit or engineering project.
Both exports are generated independently from the same editable source; no IFC
text is patched and no private model is read. Stable GUIDs preserve source identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
from pathlib import Path

import ifcopenshell
import ifcopenshell.geom


def guid(name):
    return ifcopenshell.guid.compress(
        uuid.uuid5(uuid.NAMESPACE_URL, "https://example.invalid/bim-doctor-demo/" + name).hex
    )


def export(source, revision):
    model = ifcopenshell.file(schema="IFC4")
    def point(xyz):
        return model.create_entity("IfcCartesianPoint", Coordinates=tuple(xyz))

    def axis(xyz):
        return model.create_entity("IfcAxis2Placement3D", Location=point(xyz))
    origin = axis((0.0, 0.0, 0.0))
    context = model.create_entity(
        "IfcGeometricRepresentationContext", ContextIdentifier="Model", ContextType="Model",
        CoordinateSpaceDimension=3, Precision=0.00001, WorldCoordinateSystem=origin,
    )
    unit = model.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")
    units = model.create_entity("IfcUnitAssignment", Units=[unit])
    project = model.create_entity(
        "IfcProject", GlobalId=guid("project"), Name=source["title"],
        RepresentationContexts=[context], UnitsInContext=units,
    )
    site = model.create_entity("IfcSite", GlobalId=guid("site"), Name="PUBLIC SYNTHETIC site")
    building = model.create_entity(
        "IfcBuilding", GlobalId=guid("building"), Name="PUBLIC SYNTHETIC building",
    )
    storey = model.create_entity(
        "IfcBuildingStorey", GlobalId=guid("storey"), Name="PUBLIC SYNTHETIC level",
        Elevation=0.0,
    )
    for index, (parent, child) in enumerate(((project, site), (site, building),
                                            (building, storey))):
        model.create_entity("IfcRelAggregates", GlobalId=guid(f"aggregate-{index}"),
                            RelatingObject=parent, RelatedObjects=[child])
    objects = []
    for item in source["elements"]:
        if revision == "after" and item.get("removed_after"):
            continue
        kind = item.get("after_class", item["class"]) if revision == "after" else item["class"]
        predefined = item.get(f"{revision}_type", item.get("type", "NOTDEFINED"))
        width, depth, height = map(float, item["size"])
        profile = model.create_entity(
            "IfcRectangleProfileDef", ProfileType="AREA", XDim=width, YDim=depth,
        )
        solid = model.create_entity(
            "IfcExtrudedAreaSolid", SweptArea=profile, Position=origin,
            ExtrudedDirection=model.create_entity("IfcDirection", DirectionRatios=(0., 0., 1.)),
            Depth=height,
        )
        shape = model.create_entity(
            "IfcShapeRepresentation", ContextOfItems=context, RepresentationIdentifier="Body",
            RepresentationType="SweptSolid", Items=[solid],
        )
        representation = model.create_entity(
            "IfcProductDefinitionShape", Representations=[shape],
        )
        placement = model.create_entity(
            "IfcLocalPlacement", RelativePlacement=axis(tuple(map(float, item["position"]))),
        )
        objects.append(model.create_entity(
            kind, GlobalId=guid(item["id"]), Name=item["name"], ObjectPlacement=placement,
            Representation=representation, Tag="PUBLIC-DEMO-" + item["id"],
            PredefinedType=predefined,
        ))
    model.create_entity("IfcRelContainedInSpatialStructure", GlobalId=guid("containment"),
                        RelatedElements=objects, RelatingStructure=storey)
    model.header.file_name.name = f"PUBLIC-SYNTHETIC-{revision}.ifc"
    model.header.file_name.time_stamp = "2026-01-01T00:00:00"
    model.header.file_name.author = ("BIM Doctor public demo generator",)
    model.header.file_name.organization = ("Original public synthetic fixture",)
    model.header.file_name.preprocessor_version = "IfcOpenShell " + ifcopenshell.version
    model.header.file_name.originating_system = "Editable JSON public demonstration source"
    model.header.file_name.authorization = "MIT"
    model.header.file_description.description = ("PUBLIC SYNTHETIC geometry fixture",)
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    triangles = 0
    for element in objects:
        shape = ifcopenshell.geom.create_shape(settings, element)
        assert shape.geometry.faces, "Every public demonstration object must have real geometry"
        triangles += len(shape.geometry.faces) // 3
    return model.to_string().encode("utf-8"), len(objects), triangles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    source_path = Path(__file__).with_name("public-source.json")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    shutil.copyfile(source_path, args.output_dir / source_path.name)
    result = {"synthetic": True, "editable_source": source_path.name,
              "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
              "license": source["license"], "exports": {}}
    for revision in ("before", "after"):
        body, elements, triangles = export(source, revision)
        name = f"PUBLIC-SYNTHETIC-{revision}.ifc"
        (args.output_dir / name).write_bytes(body)
        result["exports"][revision] = {
            "file": name, "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body),
            "elements": elements, "triangles": triangles,
        }
    (args.output_dir / "fixture.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
