"""Original public example of the native enterprise rule package (no model data).

Use ``python tools/enterprise_rules_example.py output.zip`` to write a template.
"""

from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def example_package() -> bytes:
    manifest = {
        "schema_version": 1,
        "package_id": "public-terminal-schedule",
        "version": "1.0",
        "title": "Example terminal schedule handover",
        "source": {
            "organization": "BIM Doctor public example",
            "reference": "Original educational requirements; not a statutory standard",
            "issued_on": "2026-10-26",
        },
        "purposes": [
            {
                "purpose_id": "terminal-schedule",
                "title": "Prepare a terminal schedule",
                "title_zh": "编制风口明细表",
                "from_role": "MEP designer",
                "to_role": "Schedule coordinator",
                "subject_classes": ["IfcAirTerminal"],
                "required_rule_ids": ["EXAMPLE-TERMINAL"],
                "requires_counterpart": False,
                "evidence_requirements": [
                    {
                        "evidence_id": "source-mapping",
                        "title": "Check source object mapping",
                        "acceptance": (
                            "A reviewer checked the IFC terminal mapping against the "
                            "source object and referenced the evidence."
                        ),
                        "execution": "manual",
                        "method_id": "source-object-review",
                        "method_description": (
                            "Inspect source object and exported IFC identity; "
                            "cite the drawing or source view."
                        ),
                    }
                ],
            }
        ],
    }
    internal = manifest["purposes"][0]
    manual_evidence = internal["evidence_requirements"]
    internal.update(title="Internal review", title_zh="内部审查", evidence_requirements=[])
    manifest["purposes"].extend(
        [
            {
                **internal,
                "purpose_id": "tender-submission",
                "title": "Tender submission",
                "title_zh": "投标提交",
                "to_role": "Tender reviewer",
                "evidence_requirements": manual_evidence,
            },
            {
                **internal,
                "purpose_id": "mep-to-architecture",
                "title": "MEP to Architecture handover",
                "title_zh": "机电向建筑专业交接",
                "to_role": "Architecture coordinator",
                "requires_counterpart": True,
                "evidence_requirements": [
                    {
                        "evidence_id": "geometry-coordination",
                        "title": "Geometry coordination evidence",
                        "acceptance": (
                            "The delivered MEP and counterpart architecture "
                            "geometry are coordinated."
                        ),
                        "execution": "unsupported",
                        "reason": (
                            "This example's IDS checks do not evaluate clashes, clearances or "
                            "cross-model geometric coordination. "
                            "Supply a separately supported method."
                        ),
                    }
                ],
            },
        ]
    )
    files = {
        "manifest.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        "rules/ruleset.toml": (
            '[ruleset]\nruleset_id="public-terminal-schedule"\n'
            'version="1.0"\ntitle="Example terminal schedule checks"\n'
        ),
        "rules/terminal.toml": """rule_id = "EXAMPLE-TERMINAL"
title = "Terminals have an accepted effective type and a Name"
description = "Original example requirement, not a regulatory assessment."
checker = "ids"
severity = "ERROR"
ifc_version = ["IFC4"]
citation = "BIM Doctor educational example authored for this repository."
hypotheses = ["An unsuitable source IFC mapping is possible; this suggestion is unverified."]
[[applicability]]
facet = "entity"
name = "IFCAIRTERMINAL"
[[requirements]]
facet = "entity"
name = "IFCAIRTERMINAL"
[requirements.predefinedType]
enumeration = ["DIFFUSER", "GRILLE", "LOUVRE", "REGISTER"]
[[requirements]]
facet = "attribute"
name = "Name"
""",
    }
    stream = BytesIO()
    with ZipFile(stream, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            info = ZipInfo(name, date_time=(2026, 10, 26, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content.encode("utf-8"))
    return stream.getvalue()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_bytes(example_package())
