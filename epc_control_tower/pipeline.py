"""The orchestrator: stages, in order, with identity computed where it belongs.

Previously this sequence existed only as a list of commands in a README, and
the stages passed data to each other through CSV files committed to the
repository. That made the pipeline unrunnable as a whole, impossible to test
end to end, and quietly dependent on whichever artifacts happened to be checked
in at the time.

The order here is not arbitrary. The validation identity has to be known before
any finding is produced, because every finding key derives from it; and it can
only be known once the models are hashed, the rules are parsed, and the
participating checkers have been fingerprinted. So: ingest, inventory, load
rules, route, *then* identify, then check, then group. Export is a separate
call, because a bundle is worth having whether or not anything is written.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from . import CONTRACT_VERSION
from .bcf.schema import default_schema_dir
from .config import ProjectManifest, RunConfig, load_project_manifests
from .domain import RunBundle, RuleSet, ValidationRun
from .exporters.legacy_bcf import BCF_FILENAME
from .exporters.legacy_manifest import (
    build_legacy_manifest,
    legacy_input_paths,
    write_legacy_manifest,
)
from .exporters.legacy_projection import project_bundle
from .identity import build_validation_run_id
from .registry import Registry, default_registry
from .rules import load_ruleset
from .stages.check import check
from .stages.export import ExportResult, export
from .stages.geometry import compute_geometry
from .stages.group import group
from .stages.ingest import IngestResult, ingest
from .stages.inventory import inventory
from .validation import validate_bundle

__all__ = [
    "PipelineResult",
    "RunResult",
    "build_bundle",
    "execute",
    "load_manifests",
    "output_roots",
]


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """A completed validation, plus the working state that produced it.

    :attr:`bundle` is what exporters consume and is deliberately the only thing
    they get. The rest is here for the orchestrator and for diagnostics.
    """

    bundle: RunBundle
    manifests: tuple[ProjectManifest, ...]
    registry: Registry
    ingested: IngestResult
    ruleset: RuleSet


def load_manifests(config: RunConfig) -> tuple[ProjectManifest, ...]:
    if not config.project_manifests:
        raise FileNotFoundError(
            "No project manifests configured; expected at least one "
            "projects/<id>/project.toml"
        )
    return load_project_manifests(
        config.project_manifests, repository_root=config.repository_root
    )


def build_bundle(
    config: RunConfig,
    *,
    registry: Registry | None = None,
    manifests: Sequence[ProjectManifest] | None = None,
    reports_dir: Path | None = None,
    verify: bool = True,
) -> PipelineResult:
    """Run every stage up to and including grouping, and return the bundle."""

    registry = registry if registry is not None else default_registry(config)
    manifests = tuple(manifests) if manifests is not None else load_manifests(config)
    reports_dir = reports_dir or config.resolved_reports_dir()

    ingested = ingest(manifests)
    paths = {
        declared.model_key: manifest.raw_data_dir / declared.filename
        for manifest in manifests
        for declared in manifest.models
    }
    elements = inventory(ingested.models, paths)

    ruleset = load_ruleset(config.resolved_ruleset_path())
    routed = registry.route(ruleset.requirements)
    registry.validate_plan(routed, ingested.models)
    checker_fingerprints = registry.fingerprints(routed)

    model_inputs = ingested.model_inputs()
    validation_run_id = build_validation_run_id(
        ruleset_id=ruleset.ruleset_id,
        ruleset_version=ruleset.version,
        ruleset_normalized_digest=ruleset.normalized_digest,
        models=model_inputs,
        checkers=checker_fingerprints,
        as_of=config.as_of,
    )

    checked = check(
        registry=registry,
        ruleset=ruleset,
        manifests=manifests,
        projects=ingested.projects,
        models=ingested.models,
        elements=elements,
        validation_run_id=validation_run_id,
        as_of=config.as_of,
        reports_dir=reports_dir,
    )
    checked.raise_for_failures()

    grouped = group(
        checked.findings,
        registry=registry,
        policy_id=config.grouping_policy,
        validation_run_id=validation_run_id,
        as_of=config.as_of,
    )

    # Only for elements an issue points at. Tessellating every element to
    # produce a bounding box nobody asks for would be the expensive half of
    # the run, spent on nothing.
    geometry = compute_geometry(
        [issue.element_key for issue in grouped.issues],
        elements=elements,
        model_paths=paths,
    )

    run = ValidationRun(
        validation_run_id=validation_run_id,
        ruleset_id=ruleset.ruleset_id,
        ruleset_version=ruleset.version,
        ruleset_normalized_digest=ruleset.normalized_digest,
        as_of=config.as_of,
        ruleset_source_blob_sha256=ruleset.source_blob_sha256,
        model_inputs=model_inputs,
        checker_fingerprints=checker_fingerprints,
    )

    bundle = RunBundle(
        contract_version=CONTRACT_VERSION,
        run=run,
        ruleset=ruleset,
        projects=ingested.projects,
        models=ingested.models,
        elements=elements,
        findings=checked.findings,
        issues=grouped.issues,
        issue_events=grouped.events,
        geometry=geometry,
    )

    if verify:
        validate_bundle(bundle)

    return PipelineResult(
        bundle=bundle,
        manifests=manifests,
        registry=registry,
        ingested=ingested,
        ruleset=ruleset,
    )


@dataclass(frozen=True, slots=True)
class RunResult:
    """A validation and everything writing it produced."""

    pipeline: PipelineResult
    export: ExportResult
    legacy_manifest_path: Path | None = None


def _manifest_for_project(
    manifests: Sequence[ProjectManifest],
    project_id: str | None,
) -> ProjectManifest:
    if project_id is None:
        if len(manifests) != 1:
            raise ValueError(
                "The legacy writers publish one project, but this run covers "
                f"{sorted(m.project.project_id for m in manifests)}. Set "
                "`legacy_project_id` in control-tower.toml."
            )
        return manifests[0]
    for manifest in manifests:
        if manifest.project.project_id == project_id:
            return manifest
    raise KeyError(f"No manifest for legacy project {project_id!r}")


def output_roots(config: RunConfig) -> dict[str, Path]:
    """Where each kind of output goes, from configuration.

    Exporters declare which kind they write and carry no path of their own, so
    this mapping is the single place the answer lives.
    """

    return {
        "processed": config.resolved_processed_data_dir(),
        "reports": config.resolved_reports_dir(),
    }


def execute(
    config: RunConfig,
    *,
    exporter_ids: Sequence[str] | None = None,
    registry: Registry | None = None,
) -> RunResult:
    """Validate, group, and write — the whole thing, in order.

    Where everything lands comes from the configuration and nowhere else. A
    parameter that could redirect one output but not another would make it
    possible to produce a half-redirected run, and a manifest describing it as
    if it were whole.
    """

    result = build_bundle(config, registry=registry)
    roots = output_roots(config)

    enabled = tuple(exporter_ids) if exporter_ids is not None else config.exporters
    exported = export(
        result.bundle,
        registry=result.registry,
        exporter_ids=enabled,
        output_roots=roots,
        repository_root=config.repository_root,
        # Beside the reports rather than inside any exporter's directory: it
        # describes whichever exporters ran, so it does not belong to one of
        # them.
        manifest_dir=roots["reports"],
    )

    # The published BCF manifest describes files both legacy writers produce,
    # so it can only be built once both have run — and only makes sense when
    # both did.
    legacy_manifest_path: Path | None = None
    if {"legacy-bcf", "legacy-pbip"} <= set(enabled):
        legacy_project_id = config.legacy_project_id or None
        projection = project_bundle(result.bundle, project_id=legacy_project_id)
        # The manifest names the IFC file the archive was built from, so it has
        # to read the raw data directory of the project the legacy writers
        # actually published — not whichever project happened to sort first.
        legacy_manifest_source = _manifest_for_project(
            result.manifests, legacy_project_id
        )
        manifest = build_legacy_manifest(
            projection,
            repository_root=config.repository_root,
            input_paths=legacy_input_paths(
                projection,
                processed_dir=roots["processed"],
                raw_data_dir=legacy_manifest_source.raw_data_dir,
                ruleset_path=config.resolved_ruleset_path(),
            ),
            sidecar_dir=roots["processed"],
            bcf_path=roots["reports"] / "bcf" / BCF_FILENAME,
            schema_dir=default_schema_dir(config.repository_root),
        )
        legacy_manifest_path = write_legacy_manifest(manifest, roots["reports"])

    return RunResult(
        pipeline=result,
        export=exported,
        legacy_manifest_path=legacy_manifest_path,
    )
