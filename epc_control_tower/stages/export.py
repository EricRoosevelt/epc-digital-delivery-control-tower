"""Export: a bundle becomes files, and the set of files gets an identity.

Exporters receive a :class:`~..domain.RunBundle` and nothing else. They do not
reopen IFC files, consult checkers, or branch on rule ids — if one needs to,
that is a sign the information belongs in the domain model rather than in the
exporter.

The identity of a *set of outputs* is computed here rather than by any
exporter, because no exporter can know it: it depends on the validation, on the
output contract version, and on every exporter that took part. Two bundles can
share a validation and still differ because an exporter changed, and this is
where that becomes visible.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from ..determinism import atomic_write_bytes, json_bytes, sha256_bytes
from ..domain import RunBundle
from ..identity import build_artifact_bundle_id
from ..protocols import Artifact
from ..registry import Registry

__all__ = ["ExportResult", "export"]

MANIFEST_NAME = "artifact_manifest.json"


@dataclass(frozen=True, slots=True)
class ExportResult:
    artifact_bundle_id: str
    artifacts: tuple[Artifact, ...]
    manifest: Artifact | None = None


def _relative(path: Path, root: Path) -> str:
    """A repository-relative POSIX path, or fail closed.

    Absolute paths would put the machine that ran the export into a
    deterministic artifact, and a path escaping the repository would mean an
    export wrote somewhere nobody reviewed.
    """

    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"Export must stay inside the repository: {path}") from error


def export(
    bundle: RunBundle,
    *,
    registry: Registry,
    exporter_ids: Sequence[str],
    output_root: Path,
    repository_root: Path,
    manifest_dir: Path | None = None,
) -> ExportResult:
    """Run each named exporter and record what the whole set produced."""

    ordered = sorted(set(exporter_ids))
    if not ordered:
        raise ValueError("No exporters enabled; nothing would be written")

    fingerprints = registry.exporter_fingerprints(ordered)
    artifact_bundle_id = build_artifact_bundle_id(
        validation_run_id=bundle.run.validation_run_id,
        contract_version=bundle.contract_version,
        exporters=fingerprints,
    )

    artifacts: list[Artifact] = []
    for exporter_id in ordered:
        exporter = registry.exporter(exporter_id)
        artifacts.extend(exporter.export(bundle, output_root))

    artifacts.sort(key=lambda artifact: _relative(artifact.path, repository_root))

    manifest: Artifact | None = None
    if manifest_dir is not None:
        document = {
            "artifact_bundle_id": artifact_bundle_id,
            "contract_version": bundle.contract_version,
            "validation_run_id": bundle.run.validation_run_id,
            "as_of": bundle.run.as_of,
            "exporters": [fingerprint.as_document() for fingerprint in fingerprints],
            "artifacts": [
                {
                    "path": _relative(artifact.path, repository_root),
                    "sha256": artifact.sha256,
                    "bytes": artifact.byte_count,
                    "exporter": artifact.exporter_id,
                }
                for artifact in artifacts
            ],
        }
        data = json_bytes(document)
        path = manifest_dir / MANIFEST_NAME
        atomic_write_bytes(path, data)
        manifest = Artifact(
            path=path,
            sha256=sha256_bytes(data),
            byte_count=len(data),
            exporter_id="",
        )

    return ExportResult(
        artifact_bundle_id=artifact_bundle_id,
        artifacts=tuple(artifacts),
        manifest=manifest,
    )
