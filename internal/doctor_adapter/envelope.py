"""The one envelope every scenario is handed over in.

Two things happen here and nothing else: a record or a refusal is placed in the
envelope exactly as the Framework produced it, and the canonical element
inventory is attached for display.

**Only an assessment refusal is a refusal.** :class:`PurposeAssessmentError` means
the request was refused and no record exists, so turning it into ``outcome =
"refusal"`` at the level of the whole request says nothing untrue. Any other
exception — including the sibling :class:`PurposeCompositionError` and the base
:class:`PurposeError` — is a defect or a different failure, and propagates as
itself: a bug rendered as "the assessment was refused" would be a false statement
about the project. Nor does this ever keep part of a record: a request either
produced a sealed record or it did not.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from epc_control_tower.determinism import read_csv_rows
from epc_control_tower.purpose import AssessmentRecord, PurposeAssessmentError

__all__ = [
    "CANONICAL_ELEMENTS",
    "FIXTURE",
    "MODES",
    "PROJECT_ROOT",
    "REAL",
    "build_envelope",
    "display_elements",
    "envelope_bytes",
]

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FIXTURE = "fixture"
REAL = "real"
MODES = (FIXTURE, REAL)

#: The current canonical inventory. Never the frozen presentation inventory
#: beside it, which describes one project under the legacy contract and would
#: silently drop elements a current record can name.
CANONICAL_ELEMENTS = PROJECT_ROOT / "data" / "processed" / "canonical" / "elements.csv"


def display_elements() -> dict[str, dict[str, str]]:
    """``element_key`` → what a person needs to find the element, for display only.

    Values are copied as published. An empty ``storey`` stays an empty string: it
    means the element has no storey assignment, not that a value is missing.
    """

    elements: dict[str, dict[str, str]] = {}
    for row in sorted(read_csv_rows(CANONICAL_ELEMENTS), key=lambda row: row["element_key"]):
        key = row["element_key"]
        if key in elements:
            raise ValueError(f"{CANONICAL_ELEMENTS.name} repeats element_key {key!r}")
        elements[key] = {
            "name": row["name"],
            "ifc_class": row["ifc_class"],
            "storey": row["storey"],
            "global_id": row["global_id"],
            "model_key": row["model_key"],
        }
    return elements


def build_envelope(mode: str, produce: Callable[[], AssessmentRecord]) -> dict[str, object]:
    """Call ``produce`` once and place what it returned, or refused with, in the envelope.

    ``mode`` is supplied by the entry that was called and is checked only for
    being one of the two; nothing here can change it.
    """

    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, not {mode!r}")
    try:
        record = produce()
    except PurposeAssessmentError as error:
        return {
            "mode": mode,
            "outcome": "refusal",
            "refusal": {"code": error.code, "text": str(error)},
            "elements": display_elements(),
        }
    return {
        "mode": mode,
        "outcome": "record",
        "record": record.as_document(),
        "assessment_digest": record.assessment_digest,
        "elements": display_elements(),
    }


def envelope_bytes(envelope: object) -> bytes:
    """An envelope (or the scenario index) as UTF-8 JSON with LF line endings.

    Keys are **not** sorted: the record's key order is the order ``as_document()``
    gave it, and handing it over "as returned" includes that.
    """

    return (json.dumps(envelope, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
