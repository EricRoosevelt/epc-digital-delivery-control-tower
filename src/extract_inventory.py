"""Rebuild the published model and element registers.

Compatibility shim over :mod:`epc_control_tower`. Two things changed.

It no longer runs on import. The previous version had no ``main`` and no
``__name__`` guard, so merely importing it opened three IFC files and rewrote
two tracked CSVs. That is not a style preference: a module that acts when it is
read cannot be tested, cannot be introspected, and will eventually do its work
at a moment nobody chose.

It no longer carries a table of the three filenames it is willing to accept.
That table was the single biggest obstacle to reusing this pipeline — pointing
it at your own models meant editing its source, and an unrecognised filename
stopped the run. The table is a project manifest now, at
``projects/<id>/project.toml``, and it is data rather than code.

`epc-ct run` produces these two files along with everything else. This entry
point remains for anyone who wants only the registers.

It publishes one project: the one ``legacy_project_id`` names in
``control-tower.toml``, as the legacy writers do. The two files describe that
project alone — the Power BI project asserts three models and thirty-nine
elements — and before this was scoped, a checkout with a second project had
this script exit 0 having rewritten both of them with every project's models,
while the snapshot, the dashboard check and the contract tests stayed green.
With several projects and none named it refuses before reading a model or
writing a file, for the reason the pipeline gives
(:func:`epc_control_tower.pipeline._manifest_for_project`).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from epc_control_tower.config import load_project_manifests, load_run_config  # noqa: E402
from epc_control_tower.determinism import atomic_write_bytes, write_csv_bytes  # noqa: E402
from epc_control_tower.domain import field_names  # noqa: E402
from epc_control_tower.exporters.legacy_contract import (  # noqa: E402
    LegacyInventoryRow,
    LegacyModelRow,
)
from epc_control_tower.exporters.legacy_projection import project_register  # noqa: E402
from epc_control_tower.pipeline import _manifest_for_project  # noqa: E402
from epc_control_tower.stages.ingest import ingest  # noqa: E402
from epc_control_tower.stages.inventory import inventory  # noqa: E402

MODELS_OUTPUT = PROJECT_ROOT / "data" / "processed" / "models.csv"
INVENTORY_OUTPUT = PROJECT_ROOT / "data" / "processed" / "model_inventory.csv"


def build_registers(repository_root: Path = PROJECT_ROOT):
    """Return the published model and inventory rows for the legacy project.

    Raises :class:`ValueError` when the checkout has several projects and
    ``legacy_project_id`` names none, and :class:`KeyError` when it names one
    the checkout does not have — both before any model is opened.
    """

    config = load_run_config(repository_root)
    manifests = [
        _manifest_for_project(
            load_project_manifests(
                config.project_manifests, repository_root=repository_root
            ),
            config.legacy_project_id or None,
        )
    ]
    ingested = ingest(manifests)
    paths = {
        declared.model_key: manifest.raw_data_dir / declared.filename
        for manifest in manifests
        for declared in manifest.models
    }
    elements = inventory(ingested.models, paths)
    return project_register(ingested.models, elements)


def write_registers(
    models_output: Path = MODELS_OUTPUT,
    inventory_output: Path = INVENTORY_OUTPUT,
    repository_root: Path = PROJECT_ROOT,
) -> tuple[int, int]:
    model_rows, inventory_rows = build_registers(repository_root)

    for path, rows, row_type in (
        (models_output, model_rows, LegacyModelRow),
        (inventory_output, inventory_rows, LegacyInventoryRow),
    ):
        columns = field_names(row_type)
        atomic_write_bytes(
            path,
            write_csv_bytes(
                [{column: getattr(row, column) for column in columns} for row in rows],
                columns,
            ),
        )

    return len(model_rows), len(inventory_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models-output", type=Path, default=MODELS_OUTPUT)
    parser.add_argument("--inventory-output", type=Path, default=INVENTORY_OUTPUT)
    arguments = parser.parse_args()
    try:
        models, elements = write_registers(
            models_output=arguments.models_output,
            inventory_output=arguments.inventory_output,
        )
    except (KeyError, ValueError) as refused:
        # Nothing was written: the registers are built in full before either
        # file is touched.
        print(f"error: {refused}", file=sys.stderr)
        raise SystemExit(1) from None
    print(f"Wrote {models} models to {arguments.models_output}")
    print(f"Wrote {elements} elements to {arguments.inventory_output}")


if __name__ == "__main__":
    main()
