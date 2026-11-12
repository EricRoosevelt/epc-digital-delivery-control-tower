"""Create explicitly synthetic IFC revisions through a real local Doctor API.

Run with the project environment (IfcOpenShell installed):
  python tests/doctor_projects_fixture.py http://127.0.0.1:8774 --output <scratch.json>
No public model or published result is modified. The IFC entities intentionally
have no representations; geometry-less inspection is part of the product path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import urllib.request

import ifcopenshell


def synthetic_ifc(after: bool = False) -> bytes:
    model = ifcopenshell.file(schema="IFC4")
    entries = [
        (1, "SYNTHETIC recheck passes", "DIFFUSER" if after else "NOTDEFINED"),
        (2, "SYNTHETIC still needs review", "NOTDEFINED"),
        (3, "SYNTHETIC new failure", "NOTDEFINED" if after else "DIFFUSER"),
        (5, "SYNTHETIC class changes", "NOTDEFINED"),
        (7, "SYNTHETIC unchanged pass", "DIFFUSER"),
    ]
    if after:
        entries.append((6, "SYNTHETIC added element", "NOTDEFINED"))
    else:
        entries.append((4, "SYNTHETIC disappears, not repaired", "NOTDEFINED"))
    for number, name, predefined in entries:
        kwargs = {
            "GlobalId": ifcopenshell.guid.compress(f"{number:032x}"),
            "Name": name,
            "Tag": f"SYN-{number:02d}",
        }
        if after and number == 5:
            model.create_entity("IfcWall", **kwargs)
        else:
            model.create_entity("IfcAirTerminal", **kwargs, PredefinedType=predefined)
    return model.to_string().encode("utf-8")


def request(base: str, endpoint: str, body=None):
    headers = {}
    payload = None
    if isinstance(body, bytes):
        payload = body
        headers["Content-Type"] = "application/octet-stream"
    elif body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base.rstrip("/") + endpoint, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.load(response)


def create_fixture(base: str):
    project = request(base, "/api/projects", {"name": "SYNTHETIC · revision comparison test"})
    report_before = request(
        base, "/api/review/models?filename=synthetic-before.ifc", synthetic_ifc(),
    )
    before = request(base, "/api/projects/revisions", {
        "project_id": project["project_id"], "model_name": "SYNTHETIC · stable identity cases",
        "label": "SYNTHETIC · R1", "review_id": report_before["review_id"],
    })["revision"]
    report_after = request(
        base, "/api/review/models?filename=synthetic-after.ifc", synthetic_ifc(True),
    )
    after = request(base, "/api/projects/revisions", {
        "project_id": project["project_id"], "model_id": before["model_id"],
        "label": "SYNTHETIC · R2", "review_id": report_after["review_id"],
    })["revision"]
    pair_query = f"before={before['revision_id']}&after={after['revision_id']}"
    compared = request(base, f"/api/projects/compare?{pair_query}")
    errors = compared["summary"]["errors"]
    for change in ("resolved", "remaining", "new", "missing", "not_comparable"):
        assert errors[change] > 0, (change, errors)
    missing = [
        row for row in compared["rows"]
        if row["rule_id"] == "PV-001" and row["change"] == "missing"
    ]
    assert missing and all(row["after_finding_id"] is None for row in missing)
    return {
        "synthetic": True, "project_id": project["project_id"], "model_id": before["model_id"],
        "before_revision": before["revision_id"], "after_revision": after["revision_id"],
        "summary": compared["summary"],
        "url": (f"{base.rstrip('/')}/projects.html?lang=en&project={project['project_id']}"
                f"&{pair_query}"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = create_fixture(args.base)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
