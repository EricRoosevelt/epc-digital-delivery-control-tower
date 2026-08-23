"""Ingest: project manifests plus IFC files on disk become domain records.

Two things happen here that are easy to conflate. A manifest *declares* what a
project contains; ingest *verifies* it. Where a manifest pins a content hash,
the file on disk has to match it or the run stops — a swapped or edited input
must not be able to change the findings quietly.

The previous implementation kept this table inside the module, keyed by exact
filename, and raised on anything it did not recognise. That is the single
biggest obstacle to reusing the pipeline: pointing it at your own models meant
editing its source. The table is now the manifest.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import ifcopenshell

from ..config import ProjectManifest
from ..determinism import sha256_file
from ..domain import Model, Project

__all__ = ["IngestResult", "ingest"]


@dataclass(frozen=True, slots=True)
class IngestResult:
    projects: tuple[Project, ...]
    models: tuple[Model, ...]

    def model_inputs(self) -> tuple[tuple[str, str], ...]:
        """The ``(model_key, content_sha256)`` pairs the run identity covers."""

        return tuple(
            sorted(
                (model.model_key, model.provenance.content_sha256)
                for model in self.models
            )
        )


def _read_ifc_header(path: Path) -> tuple[str, str]:
    """Return ``(ifc_schema, ifc_project_guid)`` for one file."""

    opened = ifcopenshell.open(str(path))

    projects = opened.by_type("IfcProject")
    if len(projects) != 1:
        raise ValueError(
            f"{path.name} contains {len(projects)} IfcProject records; expected exactly 1"
        )

    project_guid = getattr(projects[0], "GlobalId", None)
    if not project_guid:
        raise ValueError(f"IfcProject in {path.name} has no GlobalId")

    return opened.schema, project_guid


def ingest(manifests: tuple[ProjectManifest, ...] | list[ProjectManifest]) -> IngestResult:
    """Turn manifests into verified :class:`~..domain.Project` and
    :class:`~..domain.Model` records.

    Ordering is by ``model_key`` rather than by however the manifests happened
    to list things, so the result does not depend on file order on disk.
    """

    projects: list[Project] = []
    models: list[Model] = []

    for manifest in manifests:
        projects.append(manifest.project)

        for declared in manifest.models:
            path = manifest.raw_data_dir / declared.filename
            if not path.exists():
                raise FileNotFoundError(
                    f"{manifest.project.project_id}: declared model not found: {path}"
                )

            observed = sha256_file(path)
            if declared.content_sha256 and observed != declared.content_sha256:
                raise ValueError(
                    f"{manifest.project.project_id}/{declared.model_id}: content hash "
                    f"mismatch for {declared.filename}\n"
                    f"  declared: {declared.content_sha256}\n"
                    f"  on disk:  {observed}"
                )

            ifc_schema, ifc_project_guid = _read_ifc_header(path)

            models.append(
                Model(
                    model_key=declared.model_key,
                    model_id=declared.model_id,
                    project_id=manifest.project.project_id,
                    discipline=declared.discipline,
                    filename=declared.filename,
                    provenance=declared.provenance(observed),
                    ifc_schema=ifc_schema,
                    ifc_project_guid=ifc_project_guid,
                )
            )

    projects.sort(key=lambda project: project.project_id)
    models.sort(key=lambda model: model.model_key)

    return IngestResult(projects=tuple(projects), models=tuple(models))


def resolve_model_path(manifest: ProjectManifest, model: Model) -> Path:
    """Locate a model's file on disk."""

    return manifest.raw_data_dir / model.filename
