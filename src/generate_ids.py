"""Author the IDS document this project validates against.

Rule authoring is the one thing not moved into :mod:`epc_control_tower` by this
phase. Declarative rule definitions — a rule as data, with severity, owner role
and stage as fields — are the next phase's work, and porting these calls into
the package first would only mean porting them twice. The checker *reads* this
document; nothing in the package writes one.

Two things did change.

It no longer runs on import. The previous version had no ``main`` and no
``__name__`` guard, so importing it rewrote the rule document as a side effect.

It no longer asserts a count and a literal list of identifiers taken from the
fixture. The checks are now derived from what was actually declared: the
document read back has to contain the same identifiers, in the same order, as
the specifications that went in. That keeps meaning when an eighth rule is
added, which ``!= 7`` did not.

.. warning::

   Rewriting this file changes the published ``run_id``. Under data contract
   0.1 the run identity is a SHA-256 over this document's *raw bytes*, so even
   a change in line endings re-keys all forty-seven findings — which is why
   ``.gitattributes`` pins ``ids/*.ids -text``. Overwriting therefore requires
   ``--force``. The canonical model already derives rule identity from parsed
   requirements instead, and this hazard retires with the legacy adapters.
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

from ifctester import ids

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "ids" / "epc_delivery_requirements_v0.1.ids"

IDS_NAMESPACE = {"ids": "http://standards.buildingsmart.org/IDS"}


def add_specification(document, identifier, name, entity_name, requirements, description):
    """Add one specification: what it applies to, and what that must satisfy."""

    specification = ids.Specification(
        name=name,
        identifier=identifier,
        description=description,
        ifcVersion=["IFC4"],
        # minOccurs=0 so that a model with no applicable elements reports N/A
        # rather than failing. Whether that counts as compliance is decided
        # downstream, where it is normalised away from PASS.
        minOccurs=0,
        maxOccurs="unbounded",
    )
    specification.applicability.append(ids.Entity(name=entity_name))
    specification.requirements.extend(requirements)
    document.specifications.append(specification)


def make_spatial_requirement():
    """Require an HVAC element to sit directly in a space or a storey."""

    allowed_containers = ids.Restriction(
        options={"enumeration": ["IFCSPACE", "IFCBUILDINGSTOREY"]},
        base="string",
    )
    return ids.PartOf(
        name=allowed_containers,
        relation="IFCRELCONTAINEDINSPATIALSTRUCTURE",
        cardinality="required",
        instructions="Assign the HVAC element directly to an IfcSpace or IfcBuildingStorey.",
    )


def make_epc_metadata_requirements():
    """The project's assumed EPC delivery metadata.

    Two requirements in one specification are conjunctive: both the asset tag
    and the system code must be present.
    """

    return [
        ids.Property(
            propertySet="EPC_Delivery",
            baseName="AssetTag",
            dataType="IFCLABEL",
            cardinality="required",
            instructions="Provide the project-assumed EPC asset tag.",
        ),
        ids.Property(
            propertySet="EPC_Delivery",
            baseName="SystemCode",
            dataType="IFCLABEL",
            cardinality="required",
            instructions="Provide the project-assumed EPC system code.",
        ),
    ]


def build_document():
    """Declare every rule and return the document, without writing it."""

    document = ids.Ids(
        title="EPC Digital Delivery Requirements",
        version="0.1",
        description=(
            "Project-authored information requirements for the EPC Digital "
            "Delivery Control Tower prototype."
        ),
        purpose=(
            "Validate selected information requirements in public "
            "multidisciplinary IFC sample models."
        ),
        milestone="Portfolio prototype",
    )

    add_specification(
        document=document,
        identifier="R-001",
        name="Walls must have a name",
        entity_name="IFCWALL",
        requirements=[
            ids.Attribute(
                name="Name",
                cardinality="required",
                instructions="Provide a non-empty IFC Name.",
            )
        ],
        description="Checks whether every applicable IfcWall provides its IFC Name attribute.",
    )

    add_specification(
        document=document,
        identifier="R-002",
        name="Walls must declare IsExternal",
        entity_name="IFCWALL",
        requirements=[
            ids.Property(
                propertySet="Pset_WallCommon",
                baseName="IsExternal",
                dataType="IFCBOOLEAN",
                cardinality="required",
                instructions="Declare whether the wall is external.",
            )
        ],
        description="Checks the presence and IFC data type of Pset_WallCommon.IsExternal.",
    )

    add_specification(
        document=document,
        identifier="R-003",
        name="Beams must declare LoadBearing",
        entity_name="IFCBEAM",
        requirements=[
            ids.Property(
                propertySet="Pset_BeamCommon",
                baseName="LoadBearing",
                dataType="IFCBOOLEAN",
                cardinality="required",
                instructions="Declare whether the beam is load-bearing.",
            )
        ],
        description="Checks the presence and IFC data type of Pset_BeamCommon.LoadBearing.",
    )

    # R-004 is split in two so that duct segments and air terminals can be
    # reported on separately.
    add_specification(
        document=document,
        identifier="R-004A",
        name="Duct segments need spatial assignment",
        entity_name="IFCDUCTSEGMENT",
        requirements=[make_spatial_requirement()],
        description=(
            "Checks whether each IfcDuctSegment is directly contained in an "
            "IfcSpace or IfcBuildingStorey."
        ),
    )

    add_specification(
        document=document,
        identifier="R-004B",
        name="Air terminals need spatial assignment",
        entity_name="IFCAIRTERMINAL",
        requirements=[make_spatial_requirement()],
        description=(
            "Checks whether each IfcAirTerminal is directly contained in an "
            "IfcSpace or IfcBuildingStorey."
        ),
    )

    # R-005 is a requirement this project assumes. It is not an obligation the
    # buildingSMART sample files were ever meant to satisfy, which is why its
    # failures are warnings rather than errors.
    add_specification(
        document=document,
        identifier="R-005A",
        name="Duct segments need assumed EPC metadata",
        entity_name="IFCDUCTSEGMENT",
        requirements=make_epc_metadata_requirements(),
        description=(
            "Project-specific assumed EPC delivery requirement for "
            "IfcDuctSegment elements."
        ),
    )

    add_specification(
        document=document,
        identifier="R-005B",
        name="Air terminals need assumed EPC metadata",
        entity_name="IFCAIRTERMINAL",
        requirements=make_epc_metadata_requirements(),
        description=(
            "Project-specific assumed EPC delivery requirement for "
            "IfcAirTerminal elements."
        ),
    )

    return document


def declared_identifiers(document) -> list[str]:
    return [specification.identifier for specification in document.specifications]


def write_document(output_path: Path = OUTPUT_PATH, *, force: bool = False) -> list[str]:
    """Write the rule document and check that it reads back as declared."""

    if output_path.exists() and not force:
        raise FileExistsError(
            f"{output_path} already exists. Under data contract 0.1 the "
            "published run_id is a SHA-256 over this file's raw bytes, so "
            "rewriting it re-keys every published finding. Pass force=True "
            "only if that is what you mean to do."
        )

    document = build_document()
    expected = declared_identifiers(document)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.to_xml(str(output_path))

    # Read it back: a document that cannot be parsed, or that lost its
    # identifiers on the way through, is not a rule set anybody can validate
    # against.
    reloaded = ids.open(str(output_path), validate=True)
    if len(reloaded.specifications) != len(expected):
        raise ValueError(
            f"Generated IDS declares {len(expected)} specifications but reads "
            f"back {len(reloaded.specifications)}"
        )

    # IfcTester 0.8.5 does not restore `identifier` when it re-reads a
    # document, so the check goes to the XML rather than the parsed objects.
    root = ET.parse(output_path).getroot()
    actual = [
        node.get("identifier")
        for node in root.findall(".//ids:specification", IDS_NAMESPACE)
    ]
    if actual != expected:
        raise ValueError(f"Generated IDS identifiers are {actual}, expected {expected}")

    return actual


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing rule document, re-keying every published finding.",
    )
    arguments = parser.parse_args()
    try:
        identifiers = write_document(arguments.output, force=arguments.force)
    except FileExistsError as refusal:
        raise SystemExit(f"error: {refusal}") from None
    print(f"Wrote {len(identifiers)} specifications to {arguments.output}")
    for identifier in identifiers:
        print(f"- {identifier}")


if __name__ == "__main__":
    main()
