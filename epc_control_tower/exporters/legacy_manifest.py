"""The published BCF run manifest.

A manifest *over* exporters rather than one of them: it records the hash of
every file the legacy path read and every file it wrote, and several of those
files are written by the adapter next door. So it is produced after both legacy
writers have run, which is also why it is a function rather than an
:class:`~..protocols.Exporter`.

Its shape is frozen along with everything else in the published contract, down
to the order of the input list. It retires with the legacy adapters, at which
point the export stage's own artifact manifest — which records the same kind of
thing without knowing anything about IDS or BCF — is the only one left.
"""

from __future__ import annotations

from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from ..bcf.schema import OFFICIAL_SCHEMA_COMMIT, verify_schema_bundle
from ..determinism import atomic_write_bytes, json_bytes, read_csv_rows, sha256_file
from .legacy_bcf import BCF_FILENAME
from .legacy_contract import BCF_VERSION, PROJECT_GUID
from .legacy_projection import LegacyProjection

__all__ = [
    "MANIFEST_FILENAME",
    "build_legacy_manifest",
    "legacy_input_paths",
    "write_legacy_manifest",
]

MANIFEST_FILENAME = "run_manifest.json"

#: The published input list, in its published order.
_INPUT_TABLES = ("ids_findings.csv", "models.csv", "model_inventory.csv")

#: The sidecars the manifest reports on. The other three published tables are
#: inputs to this step rather than outputs of it, which is how the previous
#: implementation drew the line.
_OUTPUT_TABLES = (
    "bcf_topics.csv",
    "bcf_topic_findings.csv",
    "bcf_viewpoints.csv",
    "bcf_viewpoint_components.csv",
    "bcf_topic_events.csv",
)

_ROW_COUNT_ATTRIBUTE = {
    "bcf_topics.csv": "topic_rows",
    "bcf_topic_findings.csv": "topic_finding_rows",
    "bcf_viewpoints.csv": "viewpoint_rows",
    "bcf_viewpoint_components.csv": "component_rows",
    "bcf_topic_events.csv": "event_rows",
}


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unknown"


def _relative(path: Path, repository_root: Path) -> str:
    try:
        return path.resolve().relative_to(repository_root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"Output must stay inside the repository: {path}") from error


def legacy_input_paths(
    projection: LegacyProjection,
    *,
    processed_dir: Path,
    raw_data_dir: Path,
    ruleset_path: Path,
) -> list[Path]:
    """The published input list, in its published order."""

    subject_model = next(
        (row for row in projection.models if row.model_id == "hvac"),
        projection.models[0],
    )
    return [
        *(processed_dir / name for name in _INPUT_TABLES),
        ruleset_path,
        raw_data_dir / subject_model.filename,
    ]


def build_legacy_manifest(
    projection: LegacyProjection,
    *,
    repository_root: Path,
    input_paths: Sequence[Path],
    sidecar_dir: Path,
    bcf_path: Path,
    schema_dir: Path,
) -> dict[str, object]:
    """Describe one legacy run: what it read, what it wrote, and under what.

    Inputs and outputs are given separately rather than derived from one
    directory, because they genuinely can live apart: a caller may rebuild the
    archive from the published files while writing the result somewhere else,
    and a manifest that claimed otherwise would name files it had not touched.
    """

    output_paths = [bcf_path, *(sidecar_dir / name for name in _OUTPUT_TABLES)]

    return {
        "manifest_version": "0.1",
        "pipeline": "ids-failures-to-bcf-3.0",
        "run_id": projection.run_id,
        "generated_at": projection.as_of,
        "bcf_version": BCF_VERSION,
        "project_guid": PROJECT_GUID,
        "generator": "stdlib-xml-zipfile",
        "dependencies": {
            "ifcopenshell": _package_version("ifcopenshell"),
            "xmlschema": _package_version("xmlschema"),
        },
        "schema_bundle": {
            "repository": "buildingSMART/BCF-XML",
            "commit": OFFICIAL_SCHEMA_COMMIT,
            "path": _relative(schema_dir, repository_root),
            "files": verify_schema_bundle(schema_dir),
        },
        "counts": {
            "topics": len(projection.topic_rows),
            "topic_findings": len(projection.topic_finding_rows),
            "viewpoints": len(projection.viewpoint_rows),
            "viewpoint_components": len(projection.component_rows),
            "topic_events": len(projection.event_rows),
        },
        "inputs": [
            {
                "path": _relative(path, repository_root),
                "sha256": sha256_file(path),
                **({"rows": len(read_csv_rows(path))} if path.suffix.lower() == ".csv" else {}),
            }
            for path in input_paths
        ],
        "outputs": [
            {
                "path": _relative(path, repository_root),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
                **(
                    {"rows": len(getattr(projection, _ROW_COUNT_ATTRIBUTE[path.name]))}
                    if path.suffix.lower() == ".csv"
                    else {}
                ),
            }
            for path in output_paths
        ],
    }


def write_legacy_manifest(manifest: dict[str, object], reports_dir: Path) -> Path:
    path = reports_dir / "bcf" / MANIFEST_FILENAME
    atomic_write_bytes(path, json_bytes(manifest))
    return path
