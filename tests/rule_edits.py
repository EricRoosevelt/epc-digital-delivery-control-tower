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

__all__ = ["EDITS", "apply_edit", "edited_rules", "edited_run"]

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


def apply_edit(rules: Path, name: str) -> None:
    """Apply one edit, whatever line endings the checkout gave the rule files.

    ``*.toml`` has no explicit ``eol`` in ``.gitattributes``, so a Windows
    checkout with ``core.autocrlf`` holds the rules with CRLF, and an edit whose
    text spans a line break would then match nothing. So the edit is matched and
    applied to the file read with LF endings, and the file is written back with
    the endings it had. A file with both endings is refused rather than guessed
    at.
    """

    for filename, old, new, count in EDITS[name]:
        path = rules / filename
        raw = path.read_bytes()
        crlf = raw.count(b"\r\n")
        if crlf and crlf != raw.count(b"\n"):
            raise AssertionError(f"{name}: {filename} mixes CRLF and LF line endings")
        text = raw.decode("utf-8").replace("\r\n", "\n")
        found = text.count(old)
        if found != count:
            raise AssertionError(
                f"{name}: expected {count} occurrence(s) in {filename}, found {found}"
            )
        text = text.replace(old, new)
        if crlf:
            text = text.replace("\n", "\r\n")
        path.write_bytes(text.encode("utf-8"))


def _scratch_rules(prefix: str, line_ending: str | None = None) -> Path:
    # Nested to mirror the repository: a rule directory compiles its IDS
    # document to ``<dir>/../../ids``, which must land in the scratch copy.
    root = PROJECT_ROOT / "tests" / f".{prefix}-{uuid.uuid4().hex}"
    rules = root / "rules" / "epc-delivery"
    shutil.copytree(RULES, rules)
    if line_ending is not None:
        # Rewrite every rule file with one line ending, as a checkout of the
        # other kind would hold it.
        for path in sorted(rules.glob("*.toml")):
            text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
            path.write_bytes(text.replace("\n", line_ending).encode("utf-8"))
    return rules


@contextmanager
def edited_rules(*names: str, line_ending: str | None = None):
    """A scratch copy of the rule library with ``names`` applied, in order.

    ``line_ending`` rewrites the copy to ``"\\n"`` or ``"\\r\\n"`` first; by
    default the copy keeps whatever this checkout has.
    """

    rules = _scratch_rules("edited-rules", line_ending)
    try:
        for name in names:
            apply_edit(rules, name)
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
        apply_edit(rules, name)
    scratch = rules.parents[1]
    config = dataclasses.replace(
        shipped_run_config(),
        ruleset_path=rules,
        processed_data_dir=scratch / "processed",
        reports_dir=scratch / "reports",
    )
    return build_bundle(config, reports_dir=scratch / "reports")
