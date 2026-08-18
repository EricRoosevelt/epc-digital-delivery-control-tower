"""The published CSV contract, written from the canonical model.

This adapter is the anti-fork guarantee. The Power BI project, its nine TMDL
tables, and the committed acceptance evidence were all built against eight
specific CSV files, and none of that is being touched in this phase. The risk
in a refactor this size is not that the dashboard breaks loudly — it is that
the canonical model and the published contract quietly become two different
descriptions of the same thing, and nobody notices for months.

So the adapter is a *pure projection*: every value it writes is computed from
the bundle, and there is a characterization test asserting its output is byte-
identical to the committed files. That test is the only licence this module
has to exist. If it goes green while the canonical model changes underneath,
the dashboard is still reading the same thing the model says. If it goes red,
either the projection is wrong or the contract genuinely moved, and both are
worth a human looking at.

Columns the canonical model has and the published shape does not — ``project_id``
most of all — are dropped in the projection. That is exactly what lets the next
phase add a project dimension without the dashboard noticing.

The adapter retires in Phase 5, together with the frozen identity derivations
it depends on.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from ..determinism import atomic_write_bytes, sha256_bytes, write_csv_bytes
from ..domain import RunBundle, field_names
from ..protocols import Artifact
from .legacy_contract import (
    LegacyComponentRow,
    LegacyEventRow,
    LegacyFindingRow,
    LegacyInventoryRow,
    LegacyModelRow,
    LegacyTopicFindingRow,
    LegacyTopicRow,
    LegacyViewpointRow,
)
from .legacy_projection import LegacyProjection, project_bundle

__all__ = ["LEGACY_TABLES", "LegacyPbipAdapter"]

#: Each published file, the projection attribute that fills it, and its row
#: type. The column list is the row type's own field order, so there is no
#: second place a column name lives — which is the failure this refactor
#: started from. The row type is named rather than inferred from the first row
#: so that a table with nothing in it still writes its header.
LEGACY_TABLES = (
    ("models.csv", "models", LegacyModelRow),
    ("model_inventory.csv", "inventory", LegacyInventoryRow),
    ("ids_findings.csv", "findings", LegacyFindingRow),
    ("bcf_topics.csv", "topic_rows", LegacyTopicRow),
    ("bcf_topic_findings.csv", "topic_finding_rows", LegacyTopicFindingRow),
    ("bcf_viewpoints.csv", "viewpoint_rows", LegacyViewpointRow),
    ("bcf_viewpoint_components.csv", "component_rows", LegacyComponentRow),
    ("bcf_topic_events.csv", "event_rows", LegacyEventRow),
)

#: The five BCF sidecars are sorted by every column, as text, exactly as the
#: previous implementation did. The other three carry their own published
#: orderings, applied in the projection.
SIDECAR_TABLES = frozenset(
    {
        "bcf_topics.csv",
        "bcf_topic_findings.csv",
        "bcf_viewpoints.csv",
        "bcf_viewpoint_components.csv",
        "bcf_topic_events.csv",
    }
)


def _table_bytes(
    rows: Sequence[object],
    row_type: type,
    *,
    sort_by_every_column: bool,
) -> bytes:
    """Serialise one published table."""

    columns = field_names(row_type)
    records = [{column: getattr(row, column) for column in columns} for row in rows]
    if sort_by_every_column:
        records.sort(key=lambda record: tuple(str(record[c]) for c in columns))
    return write_csv_bytes(records, columns)


class LegacyPbipAdapter:
    """Projects the canonical bundle onto the eight published CSV files."""

    id = "legacy-pbip"
    version = "1.0.0"
    output_root_key = "processed"

    def __init__(self, *, project_id: str | None = None) -> None:
        #: The single project these files describe. See
        #: :func:`~.legacy_projection.narrow_to_project` for why the published
        #: contract has exactly one and why widening it is not an option.
        self._project_id = project_id

    def config_sha256(self) -> str:
        return ""

    def build_tables(
        self, bundle: RunBundle, projection: LegacyProjection | None = None
    ) -> dict[str, bytes]:
        """Return the published files as bytes, without writing anything."""

        projection = projection or project_bundle(bundle, project_id=self._project_id)
        return {
            filename: _table_bytes(
                getattr(projection, attribute),
                row_type,
                sort_by_every_column=filename in SIDECAR_TABLES,
            )
            for filename, attribute, row_type in LEGACY_TABLES
        }

    def export(self, bundle: RunBundle, output_root: Path) -> tuple[Artifact, ...]:
        tables = self.build_tables(bundle)
        artifacts: list[Artifact] = []
        for filename, data in tables.items():
            path = output_root / filename
            atomic_write_bytes(path, data)
            artifacts.append(
                Artifact(
                    path=path,
                    sha256=sha256_bytes(data),
                    byte_count=len(data),
                    exporter_id=self.id,
                )
            )
        return tuple(artifacts)
