"""Scaffolding for the Purpose Pack / Overlay tests.

Not a test module — it defines no tests and pytest does not collect it.

Fixtures are built by **mutating the real shipped Pack**, not by hand-writing a
parallel one. A hand-written fixture drifts from the artifact it is supposed to
stand for, and then the invariant tests prove things about a Pack nobody ships.
So: parse ``purpose-packs/…/pack.toml``, change exactly the thing under test,
render it back, and assert the loader refuses it.

The renderer handles precisely the shapes a Pack uses — scalars, arrays of
strings, arrays of tables, and one level of table/array-of-table nesting inside
an array-of-tables entry. It is not a general TOML writer and is not trying to
be one.
"""

from __future__ import annotations

import copy
import tomllib
from pathlib import Path

from helpers import PROJECT_ROOT

__all__ = [
    "PACK_PATH",
    "base_pack_document",
    "base_overlay_document",
    "render_pack",
    "render_project_with_overlay",
    "synthetic_leaf_gate_pack",
    "synthetic_pair_pack",
    "write_pack",
]

PACK_PATH = (
    PROJECT_ROOT / "purpose-packs" / "interdisciplinary-coordination-readiness" / "pack.toml"
)
PCERT_MANIFEST = PROJECT_ROOT / "projects" / "pcert-sample" / "project.toml"

#: The order Pack tables are emitted in. Fixed, so a rendered fixture is
#: byte-stable and a failing test diff is readable.
_TABLE_ORDER = (
    "directions",
    "evidence_requirements",
    "activities",
    "resolution_routes",
    "decision_nodes",
)
_SCALAR_ORDER = ("pack_id", "pack_schema_version", "pack_version", "maturity")


def base_pack_document() -> dict:
    """The shipped Pack, parsed, as a mutable document."""

    with PACK_PATH.open("rb") as stream:
        return tomllib.load(stream)


def base_overlay_document() -> dict:
    """The shipped ``pcert-sample`` manifest, parsed, as a mutable document."""

    with PCERT_MANIFEST.open("rb") as stream:
        return tomllib.load(stream)


def _scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        escaped = (
            value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        )
        return f'"{escaped}"'
    raise TypeError(f"unsupported scalar {value!r}")


def _array(values) -> str:
    return "[" + ", ".join(_scalar(item) for item in values) + "]"


def _emit_entry(lines: list[str], prefix: str, entry: dict) -> None:
    """Emit one table's scalar and array keys, then its nested tables."""

    nested_tables = []
    nested_arrays = []
    for key, value in entry.items():
        if isinstance(value, dict):
            nested_tables.append((key, value))
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            nested_arrays.append((key, value))
        elif isinstance(value, list):
            lines.append(f"{key} = {_array(value)}")
        else:
            lines.append(f"{key} = {_scalar(value)}")
    for key, table in nested_tables:
        lines.append("")
        lines.append(f"[{prefix}.{key}]")
        _emit_entry(lines, f"{prefix}.{key}", table)
    for key, rows in nested_arrays:
        for row in rows:
            lines.append("")
            lines.append(f"[[{prefix}.{key}]]")
            _emit_entry(lines, f"{prefix}.{key}", row)


def render_pack(document: dict) -> str:
    """Render a Pack document back to TOML."""

    lines: list[str] = []
    for key in _SCALAR_ORDER:
        if key in document:
            lines.append(f"{key} = {_scalar(document[key])}")
    if "citations" in document:
        lines.append(f"citations = {_array(document['citations'])}")
    for name in _TABLE_ORDER:
        for entry in document.get(name, []):
            lines.append("")
            lines.append(f"[[{name}]]")
            _emit_entry(lines, name, entry)
    return "\n".join(lines) + "\n"


def write_pack(directory: Path, document: dict, *, pack_id: str | None = None) -> Path:
    """Write a Pack document into ``directory/<pack_id>/pack.toml``."""

    name = pack_id or document["pack_id"]
    target = directory / name
    target.mkdir(parents=True, exist_ok=True)
    path = target / "pack.toml"
    path.write_text(render_pack(document), encoding="utf-8")
    return path


def render_project_with_overlay(document: dict) -> str:
    """Render a project manifest that carries an ``[overlay]`` table.

    Only the shapes ``project.toml`` actually uses: the ``[project]`` table,
    ``[[models]]``, ``[[milestones]]``, and ``[overlay]`` with its arrays.
    """

    lines: list[str] = ["[project]"]
    _emit_entry(lines, "project", document["project"])
    for name in ("models", "milestones"):
        for entry in document.get(name, []):
            lines.append("")
            lines.append(f"[[{name}]]")
            _emit_entry(lines, name, entry)
    overlay = document.get("overlay")
    if overlay is not None:
        lines.append("")
        lines.append("[overlay]")
        scalars = {k: v for k, v in overlay.items() if not isinstance(v, list)}
        _emit_entry(lines, "overlay", scalars)
        for key, rows in overlay.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                lines.append("")
                lines.append(f"[[overlay.{key}]]")
                _emit_entry(lines, f"overlay.{key}", row)
    return "\n".join(lines) + "\n"


def synthetic_pair_pack() -> dict:
    """A minimal Pack whose pair-grained node is reachable the wrong way.

    The shipped Pack cannot express invariant 17's defect in isolation: its
    pair-grained node has exactly one incoming edge, so redirecting it always
    trips invariant 10 or 18 first. This Pack is built for that one job — three
    nodes, two evidence requirements, and a pair-grained node reached from the
    branch that does *not* name any counterpart.
    """

    return {
        "pack_id": "synthetic-pair",
        "pack_schema_version": "1",
        "pack_version": "0.0.1",
        "maturity": "draft",
        "citations": [],
        "directions": [{"direction_id": "d", "from": "A", "to": "B"}],
        "evidence_requirements": [
            {
                "evidence_requirement_id": "origin",
                "answers": "a",
                "binding_source": "assessment",
                "subject_grain": "per-subject",
                "acceptance_condition": "a",
                "outcomes": ["opened", "named", "unknown"],
            },
            {
                "evidence_requirement_id": "paired",
                "answers": "b",
                "binding_source": "assessment",
                "subject_grain": "per-subject-pair",
                "acceptance_condition": "b",
                "outcomes": ["linked", "unlinked", "undetermined"],
                "pair_source": {
                    "from_evidence_requirement_id": "origin",
                    "on_outcome": "named",
                    "counterpart_description": "the counterpart the determination named",
                },
            },
            {
                "evidence_requirement_id": "extra",
                "answers": "c",
                "binding_source": "assessment",
                "subject_grain": "per-subject",
                "acceptance_condition": "c",
                "outcomes": ["fine", "poor", "silent"],
            },
        ],
        "activities": [
            {
                "activity_id": "act",
                "label": "Act",
                "direction_id": "d",
                "subject_classes": ["IfcWall"],
                "evidence_requirement_ids": ["origin", "paired", "extra"],
                "decision_root_node": "n-origin",
            }
        ],
        "resolution_routes": [
            {
                "resolution_kind": "k-blocked",
                "default_role": "role-a",
                "consequence_kinds": ["work-suspended"],
                "next_action": "fix",
                "recheck_condition": "fixed",
            },
            {
                "resolution_kind": "k-unknown",
                "default_role": "role-a",
                "consequence_kinds": ["work-suspended"],
                "next_action": "look",
                "recheck_condition": "looked",
            },
        ],
        "decision_nodes": [
            {
                "node_id": "n-origin",
                "evidence_requirement_id": "origin",
                "branches": [
                    # The wrong gate: the pair-grained node hangs off "opened",
                    # while pair_source names "named". Nothing has named a
                    # counterpart by the time n-paired is read.
                    {
                        "outcome": "opened",
                        "next_node": "n-paired",
                        "renders_inapplicable": ["extra"],
                    },
                    {"outcome": "named", "next_node": "n-extra"},
                    {"outcome": "unknown", "verdict": "UNKNOWN", "gap_kind": "k-unknown"},
                ],
            },
            {
                "node_id": "n-paired",
                "evidence_requirement_id": "paired",
                "branches": [
                    {"outcome": "linked", "verdict": "READY"},
                    {"outcome": "unlinked", "verdict": "BLOCKED", "failure_kind": "k-blocked"},
                    {
                        "outcome": "undetermined",
                        "verdict": "UNKNOWN",
                        "gap_kind": "k-unknown",
                    },
                ],
            },
            {
                "node_id": "n-extra",
                "evidence_requirement_id": "extra",
                "branches": [
                    {
                        "outcome": "fine",
                        "verdict": "READY",
                        "renders_inapplicable": ["paired"],
                    },
                    {"outcome": "poor", "verdict": "BLOCKED", "failure_kind": "k-blocked"},
                    {"outcome": "silent", "verdict": "UNKNOWN", "gap_kind": "k-unknown"},
                ],
            },
        ],
    }


def synthetic_leaf_gate_pack() -> dict:
    """A Pack where an outcome names counterparts and then ends the path.

    Invariant 18 cannot be isolated on the shipped Pack either: making its
    ``penetration-confirmed`` branch a leaf leaves ``opening-status-node``
    unreachable, so invariant 7 fires first. Here the pair-grained node *is*
    correctly gated, and a **second** node testing the same origin requirement
    takes the counterpart-naming outcome straight to a leaf — counterparts
    named, and then dropped.
    """

    return {
        "pack_id": "synthetic-leaf-gate",
        "pack_schema_version": "1",
        "pack_version": "0.0.1",
        "maturity": "draft",
        "citations": [],
        "directions": [{"direction_id": "d", "from": "A", "to": "B"}],
        "evidence_requirements": [
            {
                "evidence_requirement_id": "origin",
                "answers": "a",
                "binding_source": "assessment",
                "subject_grain": "per-subject",
                "acceptance_condition": "a",
                "outcomes": ["opened", "named", "unknown"],
            },
            {
                "evidence_requirement_id": "paired",
                "answers": "b",
                "binding_source": "assessment",
                "subject_grain": "per-subject-pair",
                "acceptance_condition": "b",
                "outcomes": ["linked", "unlinked", "undetermined"],
                "pair_source": {
                    "from_evidence_requirement_id": "origin",
                    "on_outcome": "named",
                    "counterpart_description": "the counterpart the determination named",
                },
            },
        ],
        "activities": [
            {
                "activity_id": "act",
                "label": "Act",
                "direction_id": "d",
                "subject_classes": ["IfcWall"],
                "evidence_requirement_ids": ["origin", "paired"],
                "decision_root_node": "n-origin",
            }
        ],
        "resolution_routes": [
            {
                "resolution_kind": "k-blocked",
                "default_role": "role-a",
                "consequence_kinds": ["work-suspended"],
                "next_action": "fix",
                "recheck_condition": "fixed",
            },
            {
                "resolution_kind": "k-unknown",
                "default_role": "role-a",
                "consequence_kinds": ["work-suspended"],
                "next_action": "look",
                "recheck_condition": "looked",
            },
        ],
        "decision_nodes": [
            {
                "node_id": "n-origin",
                "evidence_requirement_id": "origin",
                "branches": [
                    {"outcome": "opened", "next_node": "n-second"},
                    {"outcome": "named", "next_node": "n-paired"},
                    {"outcome": "unknown", "verdict": "UNKNOWN", "gap_kind": "k-unknown"},
                ],
            },
            {
                "node_id": "n-paired",
                "evidence_requirement_id": "paired",
                "branches": [
                    {"outcome": "linked", "verdict": "READY"},
                    {
                        "outcome": "unlinked",
                        "verdict": "BLOCKED",
                        "failure_kind": "k-blocked",
                    },
                    {
                        "outcome": "undetermined",
                        "verdict": "UNKNOWN",
                        "gap_kind": "k-unknown",
                    },
                ],
            },
            {
                "node_id": "n-second",
                "evidence_requirement_id": "origin",
                "branches": [
                    {
                        "outcome": "opened",
                        "verdict": "READY",
                        "renders_inapplicable": ["paired"],
                    },
                    # Counterparts named, path over. Nothing ever reads them.
                    {
                        "outcome": "named",
                        "verdict": "BLOCKED",
                        "failure_kind": "k-blocked",
                    },
                    {"outcome": "unknown", "verdict": "UNKNOWN", "gap_kind": "k-unknown"},
                ],
            },
        ],
    }


def mutated(document: dict) -> dict:
    """A deep copy, so a fixture cannot leak into the next test."""

    return copy.deepcopy(document)
