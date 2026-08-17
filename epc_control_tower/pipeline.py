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
from .config import ProjectManifest, RunConfig, load_project_manifests
from .domain import RunBundle, RuleSet, ValidationRun
from .identity import build_validation_run_id
from .registry import Registry, default_registry
from .rules import load_ruleset
from .stages.check import check
from .stages.ingest import IngestResult, ingest
from .stages.inventory import inventory
from .validation import validate_bundle

__all__ = ["PipelineResult", "build_bundle", "load_manifests"]


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
