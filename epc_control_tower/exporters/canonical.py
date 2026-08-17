"""Canonical exporters: the domain model, written out as it actually is.

Every column here is derived from a domain type rather than restated as a
string list. That is not tidiness for its own sake. The previous layout
declared the finding columns twice — a twenty-item list in one module, an
eleven-item set in another — and nothing connected the two, so they drifted
apart without anything noticing. A column list that is computed cannot drift
from the type it describes.

The shapes are normalised, not report-shaped. An issue does not carry its
findings inline; a bridge table joins them, the way the semantic model already
expects. Denormalising is a choice each consumer makes, and different consumers
want different denormalisations, which is exactly why the exporter should not
make it for them.

These write the *canonical* contract, under their own subdirectory. The legacy
adapter, which reproduces the published shape byte for byte, writes elsewhere;
keeping them apart is what lets the canonical model grow a column without
touching anything the Power BI project reads.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from ..determinism import (
    atomic_write_bytes,
    canonical_json_document,
    json_bytes,
    sha256_bytes,
    write_csv_bytes,
)
from ..domain import (
    Element,
    Finding,
    Issue,
    IssueEvent,
    Model,
    Project,
    Provenance,
    Requirement,
    RunBundle,
    field_names,
)
from ..protocols import Artifact

__all__ = ["CANONICAL_SUBDIRECTORY", "CsvExporter", "JsonExporter"]

#: Canonical products live under their own directory so that adding a column
#: here can never disturb the published legacy contract next door.
CANONICAL_SUBDIRECTORY = "canonical"

#: A tuple field is written as one cell. Semicolon rather than comma so that no
#: value ever needs quoting for the separator's sake alone.
LIST_SEPARATOR = ";"


def _expand(columns: Sequence[str], expansions: Mapping[str, Sequence[str]]) -> tuple[str, ...]:
    """Splice a nested record's own fields in where the record sits.

    The names still come from the types; only the knowledge that a field is a
    record worth flattening is stated here, and that is structure, not a
    restatement of the column list.
    """

    result: list[str] = []
    for column in columns:
        result.extend(expansions.get(column, (column,)))
    return tuple(result)


def _drop(columns: Sequence[str], *dropped: str) -> tuple[str, ...]:
    return tuple(column for column in columns if column not in dropped)


PROJECT_COLUMNS = field_names(Project)
MODEL_COLUMNS = _expand(field_names(Model), {"provenance": field_names(Provenance)})
ELEMENT_COLUMNS = field_names(Element)
REQUIREMENT_COLUMNS = field_names(Requirement)
FINDING_COLUMNS = field_names(Finding)
# An issue's findings are a relationship, so they get a table of their own
# rather than a delimited list crammed into a cell.
ISSUE_COLUMNS = _drop(field_names(Issue), "finding_keys")
ISSUE_FINDING_COLUMNS = ("issue_key", "finding_key")
ISSUE_EVENT_COLUMNS = field_names(IssueEvent)


def _cell(value: object) -> object:
    """Render one field as a CSV cell.

    Booleans become ``true``/``false`` rather than Python's ``True``/``False``:
    the published contract uses the lowercase spelling, and every consumer of
    these files reads it that way.
    """

    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    if isinstance(value, tuple):
        return LIST_SEPARATOR.join(str(item) for item in value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return canonical_json_document(
            {field.name: str(getattr(value, field.name)) for field in dataclasses.fields(value)}
        )
    return str(value)


def _row(record: object, columns: Sequence[str]) -> dict[str, object]:
    """Project one record onto its columns, reaching into nested records."""

    values: dict[str, object] = {}
    for column in columns:
        if hasattr(record, column):
            values[column] = _cell(getattr(record, column))
            continue
        for field in dataclasses.fields(record):
            nested = getattr(record, field.name)
            if dataclasses.is_dataclass(nested) and hasattr(nested, column):
                values[column] = _cell(getattr(nested, column))
                break
        else:
            raise AttributeError(
                f"{type(record).__name__} has no field {column!r} to export"
            )
    return values


def _rows(records: Iterable[object], columns: Sequence[str]) -> list[dict[str, object]]:
    return [_row(record, columns) for record in records]


def _write(path: Path, data: bytes, exporter_id: str) -> Artifact:
    atomic_write_bytes(path, data)
    return Artifact(
        path=path,
        sha256=sha256_bytes(data),
        byte_count=len(data),
        exporter_id=exporter_id,
    )


class CsvExporter:
    """The canonical model as normalised CSV tables."""

    id = "csv"
    version = "1.0.0"

    def config_sha256(self) -> str:
        return ""

    def export(self, bundle: RunBundle, output_root: Path) -> tuple[Artifact, ...]:
        target = output_root / CANONICAL_SUBDIRECTORY

        issue_findings = [
            {"issue_key": issue.issue_key, "finding_key": finding_key}
            for issue in bundle.issues
            for finding_key in issue.finding_keys
        ]

        tables: tuple[tuple[str, list[dict[str, object]], tuple[str, ...]], ...] = (
            ("projects.csv", _rows(bundle.projects, PROJECT_COLUMNS), PROJECT_COLUMNS),
            ("models.csv", _rows(bundle.models, MODEL_COLUMNS), MODEL_COLUMNS),
            ("elements.csv", _rows(bundle.elements, ELEMENT_COLUMNS), ELEMENT_COLUMNS),
            (
                "requirements.csv",
                _rows(bundle.ruleset.requirements, REQUIREMENT_COLUMNS),
                REQUIREMENT_COLUMNS,
            ),
            ("findings.csv", _rows(bundle.findings, FINDING_COLUMNS), FINDING_COLUMNS),
            ("issues.csv", _rows(bundle.issues, ISSUE_COLUMNS), ISSUE_COLUMNS),
            ("issue_findings.csv", issue_findings, ISSUE_FINDING_COLUMNS),
            (
                "issue_events.csv",
                _rows(bundle.issue_events, ISSUE_EVENT_COLUMNS),
                ISSUE_EVENT_COLUMNS,
            ),
        )

        return tuple(
            _write(target / name, write_csv_bytes(rows, columns), self.id)
            for name, rows, columns in tables
        )


class JsonExporter:
    """The whole bundle as one document, identity and all.

    Written so that a published validation can be checked rather than believed:
    the run's recorded inputs travel with it, so ``validation_run_id`` can be
    recomputed from the file itself. There is no execution record here — see
    :class:`~..domain.Execution` — because an exporter that could see a wall
    clock would eventually write one.
    """

    id = "json"
    version = "1.0.0"

    def config_sha256(self) -> str:
        return ""

    def export(self, bundle: RunBundle, output_root: Path) -> tuple[Artifact, ...]:
        document = {
            "contract_version": bundle.contract_version,
            "run": {
                "validation_run_id": bundle.run.validation_run_id,
                "as_of": bundle.run.as_of,
                "ruleset": {
                    "id": bundle.run.ruleset_id,
                    "version": bundle.run.ruleset_version,
                    "normalized_digest": bundle.run.ruleset_normalized_digest,
                    "source_blob_sha256": bundle.run.ruleset_source_blob_sha256,
                },
                "model_inputs": [
                    {"model_key": key, "content_sha256": digest}
                    for key, digest in bundle.run.model_inputs
                ],
                "checkers": [
                    fingerprint.as_document()
                    for fingerprint in bundle.run.checker_fingerprints
                ],
            },
            "projects": _rows(bundle.projects, PROJECT_COLUMNS),
            "models": _rows(bundle.models, MODEL_COLUMNS),
            "elements": _rows(bundle.elements, ELEMENT_COLUMNS),
            "requirements": _rows(bundle.ruleset.requirements, REQUIREMENT_COLUMNS),
            "findings": _rows(bundle.findings, FINDING_COLUMNS),
            "issues": [
                {
                    **_row(issue, ISSUE_COLUMNS),
                    "finding_keys": list(issue.finding_keys),
                }
                for issue in bundle.issues
            ],
            "issue_events": _rows(bundle.issue_events, ISSUE_EVENT_COLUMNS),
        }
        target = output_root / CANONICAL_SUBDIRECTORY / "run.json"
        return (_write(target, json_bytes(document), self.id),)
