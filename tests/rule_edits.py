"""Edits to a *copy* of the rule library, for tests that ask what an edit moves.

Not a test module. Every edit here is applied by exact string replacement to a
scratch copy under ``tests/``, with the number of occurrences asserted, and the
copy is thrown away. **None of them is ever made to ``rules/``**: R-001 to R-005B
are the frozen v0.1 rule set's rules, and editing one of them for real moves
eight frozen legacy files under an unchanged legacy ``run_id`` (ADR 0005 §5.7,
blocker B-1). The edits are the ones ADR 0005 measured, by the same names.
"""

from __future__ import annotations

import atexit
import dataclasses
import functools
import shutil
import uuid
from contextlib import contextmanager
from pathlib import Path

from helpers import PROJECT_ROOT, shipped_run_config

__all__ = ["EDITS", "edited_rules", "edited_run"]

RULES = PROJECT_ROOT / "rules" / "epc-delivery"

#: ``name -> [(rule file, old text, new text, occurrences)]``.
EDITS: dict[str, list[tuple[str, str, str, int]]] = {
    # Facet edits: each changes what a rule checks.
    "r002-datatype": [("R-002.toml", 'dataType = "IFCBOOLEAN"', 'dataType = "IFCLABEL"', 1)],
    "r001-cardinality": [
        ("R-001.toml", 'cardinality = "required"', 'cardinality = "optional"', 1)
    ],
    "r006-entity": [
        (
            "R-006.toml",
            '[[applicability]]\nfacet = "entity"\nname = "IFCWALL"',
            '[[applicability]]\nfacet = "entity"\nname = "IFCSLAB"',
            1,
        )
    ],
    "r010-pattern": [
        (
            "R-010.toml",
            'name_pattern = "^(origin|geo-reference)$"',
            'name_pattern = "^(origin)$"',
            1,
        )
    ],
    "r005a-optional": [
        ("R-005A.toml", 'cardinality = "required"', 'cardinality = "optional"', 2)
    ],
    "r005a-datatype": [("R-005A.toml", 'dataType = "IFCLABEL"', 'dataType = "IFCTEXT"', 2)],
    "r010-applicability": [
        ("R-010.toml", 'name = "IFCBUILDINGELEMENTPROXY"', 'name = "IFCWALL"', 1)
    ],
    # The completeness checker publishes this text as ``expected``.
    "r010-instructions": [
        (
            "R-010.toml",
            "instructions = \"Carry the project's agreed setout references in every "
            'discipline model."',
            'instructions = "Carry the agreed setout references in every discipline '
            'model."',
            1,
        )
    ],
    # Presentation, and one control that changes nothing at all.
    "r005a-instructions": [
        (
            "R-005A.toml",
            'instructions = "Provide the project-assumed EPC asset tag."',
            'instructions = "Provide the project-assumed EPC asset tag, as agreed."',
            1,
        )
    ],
    "r005a-title": [
        (
            "R-005A.toml",
            'title = "Duct segments need assumed EPC metadata"',
            'title = "Duct segments need the assumed EPC metadata"',
            1,
        )
    ],
    "r005a-description": [
        (
            "R-005A.toml",
            'description = "Project-specific assumed EPC delivery requirement for '
            'IfcDuctSegment elements."',
            'description = "Project-specific assumed EPC delivery requirement for duct '
            'segments."',
            1,
        )
    ],
    "r005a-reformat": [
        (
            "R-005A.toml",
            '[[applicability]]\nfacet = "entity"\nname = "IFCDUCTSEGMENT"',
            '[[applicability]]\n# reordered, no meaning changed\nname = "IFCDUCTSEGMENT"\n'
            'facet    =    "entity"',
            1,
        )
    ],
}


def _apply(rules: Path, name: str) -> None:
    for filename, old, new, count in EDITS[name]:
        path = rules / filename
        text = path.read_bytes().decode("utf-8")
        found = text.count(old)
        if found != count:
            raise AssertionError(
                f"{name}: expected {count} occurrence(s) in {filename}, found {found}"
            )
        path.write_bytes(text.replace(old, new).encode("utf-8"))


def _scratch_rules(prefix: str) -> Path:
    # Nested to mirror the repository: a rule directory compiles its IDS
    # document to ``<dir>/../../ids``, which must land in the scratch copy.
    root = PROJECT_ROOT / "tests" / f".{prefix}-{uuid.uuid4().hex}"
    rules = root / "rules" / "epc-delivery"
    shutil.copytree(RULES, rules)
    return rules


@contextmanager
def edited_rules(*names: str):
    """A scratch copy of the rule library with ``names`` applied, in order."""

    rules = _scratch_rules("edited-rules")
    try:
        for name in names:
            _apply(rules, name)
        yield rules
    finally:
        shutil.rmtree(rules.parents[1])


@functools.cache
def edited_run(*names: str):
    """The shipped run, over a copy of the rules with ``names`` applied.

    Cached for the session like :func:`helpers.shipped_pipeline_result`: a run
    opens every IFC model. The copy is removed at exit.
    """

    from epc_control_tower.pipeline import build_bundle

    rules = _scratch_rules("edited-run")
    atexit.register(shutil.rmtree, rules.parents[1], True)
    for name in names:
        _apply(rules, name)
    scratch = rules.parents[1]
    config = dataclasses.replace(
        shipped_run_config(),
        ruleset_path=rules,
        processed_data_dir=scratch / "processed",
        reports_dir=scratch / "reports",
    )
    return build_bundle(config, reports_dir=scratch / "reports")
