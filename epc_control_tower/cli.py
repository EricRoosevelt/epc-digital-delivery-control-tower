"""Command-line entry point.

Replaces the previous arrangement of five scripts run by hand in a documented
order, two of which did their work at import time. Stages are named here and
sequenced by code rather than by a list of commands in a README.

Subcommands appear as the stages behind them land. Everything listed by
``--help`` works; nothing is advertised before it does.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import CONTRACT_VERSION, __version__
from .config import load_project_manifests, load_run_config
from .registry import default_registry

__all__ = ["main"]


def _repository_root(argument: str | None) -> Path:
    if argument:
        return Path(argument).resolve()
    # Installed or not, the package sits one level below the repository root.
    return Path(__file__).resolve().parents[1]


def _command_version(_arguments: argparse.Namespace) -> int:
    print(f"epc-control-tower {__version__}")
    print(f"data contract {CONTRACT_VERSION}")
    return 0


def _command_projects(arguments: argparse.Namespace) -> int:
    root = _repository_root(arguments.repository_root)
    config = load_run_config(root, arguments.config)
    if not config.project_manifests:
        print("No project manifests found under projects/.", file=sys.stderr)
        return 1

    manifests = load_project_manifests(
        config.project_manifests, repository_root=root
    )
    for manifest in manifests:
        project = manifest.project
        print(f"{project.project_id}  {project.name}")
        if project.stage:
            print(f"  stage: {project.stage}")
        print(f"  raw data: {manifest.raw_data_dir}")
        for model in manifest.models:
            hashed = model.content_sha256[:12] if model.content_sha256 else "unpinned"
            print(
                f"  - {model.model_key:<28} {model.discipline:<14} "
                f"{model.filename:<28} {hashed}  {model.license}"
            )
    return 0


def _command_components(arguments: argparse.Namespace) -> int:
    root = _repository_root(arguments.repository_root)
    registry = default_registry(load_run_config(root, arguments.config))
    for label, items in (
        ("checkers", registry.checkers),
        ("grouping policies", registry.grouping_policies),
        ("exporters", registry.exporters),
    ):
        print(f"{label}:")
        if not items:
            print("  (none registered)")
            continue
        for component_id in sorted(items):
            component = items[component_id]
            version = getattr(component, "version", "")
            print(f"  {component_id}{f'  {version}' if version else ''}")
    return 0


def _selected_exporters(arguments: argparse.Namespace, config) -> tuple[str, ...]:
    if getattr(arguments, "format", None):
        return tuple(arguments.format)
    return config.exporters


def _report_run(result) -> None:
    bundle = result.pipeline.bundle
    print(f"validation run   {bundle.run.validation_run_id}")
    print(f"artifact bundle  {result.export.artifact_bundle_id}")
    print(f"as of            {bundle.run.as_of}")
    print(
        f"{len(bundle.models)} model(s), {len(bundle.elements)} element(s), "
        f"{len(bundle.findings)} finding(s), {len(bundle.issues)} issue(s)"
    )
    for artifact in result.export.artifacts:
        print(f"  {artifact.sha256[:12]}  {artifact.byte_count:>8}  {artifact.path}")
    if result.legacy_manifest_path is not None:
        print(f"  legacy manifest: {result.legacy_manifest_path}")


def _command_check(arguments: argparse.Namespace) -> int:
    """Validate without writing any artifact."""

    from .pipeline import build_bundle

    root = _repository_root(arguments.repository_root)
    config = load_run_config(root, arguments.config)
    result = build_bundle(config, reports_dir=arguments.reports_dir)
    bundle = result.bundle

    print(f"validation run   {bundle.run.validation_run_id}")
    counts: dict[str, int] = {}
    for finding in bundle.findings:
        counts[str(finding.status)] = counts.get(str(finding.status), 0) + 1
    for status in sorted(counts):
        print(f"  {status:<4} {counts[status]}")
    applicable = sum(1 for finding in bundle.findings if finding.is_applicable)
    print(f"  {applicable} of {len(bundle.findings)} applicable")
    print(f"  {len(bundle.issues)} issue(s)")
    return 0


def _command_run(arguments: argparse.Namespace) -> int:
    """Run every stage and write the enabled exporters' artifacts."""

    from .pipeline import execute

    root = _repository_root(arguments.repository_root)
    config = load_run_config(root, arguments.config)
    result = execute(config, exporter_ids=_selected_exporters(arguments, config))
    _report_run(result)
    return 0


def _command_export(arguments: argparse.Namespace) -> int:
    """Write one named exporter's artifacts, and only that one.

    The validation is redone rather than reloaded from disk, deliberately. An
    export whose inputs are files somebody may have edited is not an export of
    anything in particular, and reading stage outputs back out of the
    repository is exactly how the stages came to be coupled through committed
    CSVs in the first place.
    """

    if not arguments.format:
        print(
            "error: export needs at least one --format; use `run` for the "
            "configured set",
            file=sys.stderr,
        )
        return 2
    return _command_run(arguments)


def _current_snapshot(config):
    from .exporters.legacy_projection import project_bundle
    from .pipeline import execute
    from .snapshots import build_snapshot

    result = execute(config)
    artifacts = {}
    for artifact in result.export.artifacts:
        relative = artifact.path.resolve().relative_to(config.repository_root.resolve())
        artifacts[relative.as_posix()] = artifact.sha256

    return result, build_snapshot(
        result.pipeline.bundle,
        legacy_run_id=project_bundle(
            result.pipeline.bundle, project_id=config.legacy_project_id or None
        ).run_id,
        artifact_bundle_id=result.export.artifact_bundle_id,
        artifacts=artifacts,
    )


def _command_snapshot(arguments: argparse.Namespace) -> int:
    """Verify — or, with ceremony, refresh — the characterization snapshot."""

    from .snapshots import (
        changelog_mentions,
        compare_snapshots,
        load_snapshot,
        snapshot_path,
        write_snapshot,
    )

    root = _repository_root(arguments.repository_root)
    config = load_run_config(root, arguments.config)
    _result, current = _current_snapshot(config)
    path = snapshot_path(root, str(current["contract_version"]))

    if arguments.refresh:
        if not arguments.contract_changed:
            print(
                "error: refreshing a snapshot means the published contract moved.\n"
                "       Pass --contract-changed to say so.",
                file=sys.stderr,
            )
            return 2
        if not changelog_mentions(root, str(current["contract_version"])):
            print(
                f"error: {CHANGELOG_HINT} must describe contract "
                f"{current['contract_version']} before its snapshot is refreshed.",
                file=sys.stderr,
            )
            return 2
        write_snapshot(path, current)
        print(f"refreshed {path}")
        return 0

    try:
        recorded = load_snapshot(path)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    differences = compare_snapshots(recorded, current)
    if differences:
        print(
            f"The published contract no longer matches {path.name}:", file=sys.stderr
        )
        for difference in differences:
            print(f"  - {difference}", file=sys.stderr)
        print(
            "\nIf this change is intended, record it in the CHANGELOG and run\n"
            "  epc-ct snapshot --refresh --contract-changed",
            file=sys.stderr,
        )
        return 1

    print(f"{path.name} matches: {len(current['artifacts'])} artifact(s) unchanged")
    return 0


CHANGELOG_HINT = "CHANGELOG.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="epc-ct",
        description=(
            "Turn IFC model data and project-authored information requirements "
            "into traceable digital-delivery findings."
        ),
    )
    parser.add_argument(
        "--repository-root",
        default=None,
        help="Repository root; defaults to the directory containing this package.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to control-tower.toml; defaults to the repository root.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    version = subparsers.add_parser("version", help="Print package and contract versions.")
    version.set_defaults(handler=_command_version)

    projects = subparsers.add_parser(
        "projects", help="List configured projects and their source models."
    )
    projects.set_defaults(handler=_command_projects)

    components = subparsers.add_parser(
        "components", help="List registered checkers, grouping policies, and exporters."
    )
    components.set_defaults(handler=_command_components)

    check = subparsers.add_parser(
        "check", help="Validate the configured projects without writing anything."
    )
    check.add_argument(
        "--reports-dir",
        type=Path,
        default=None,
        help="Where checker reports go; defaults to the configured reports directory.",
    )
    check.set_defaults(handler=_command_check)

    run = subparsers.add_parser(
        "run", help="Run every stage and write the enabled exporters' artifacts."
    )
    run.add_argument(
        "--format",
        action="append",
        default=None,
        metavar="EXPORTER",
        help="Exporter id to run; repeat for several. Defaults to the configured set.",
    )
    run.set_defaults(handler=_command_run)

    export = subparsers.add_parser(
        "export", help="Write one or more exporters' artifacts."
    )
    export.add_argument(
        "--format",
        action="append",
        default=None,
        metavar="EXPORTER",
        help="Exporter id to run; repeat for several. Defaults to the configured set.",
    )
    export.set_defaults(handler=_command_export)

    snapshot = subparsers.add_parser(
        "snapshot",
        help="Check the published contract against its recorded snapshot.",
        description=(
            "Verifies that a run still publishes what the recorded snapshot "
            "says. Refreshing one is a deliberate act: it means the contract "
            "moved, and the CHANGELOG has to say so first."
        ),
    )
    snapshot.add_argument(
        "--refresh",
        action="store_true",
        help="Rewrite the snapshot from the current run.",
    )
    snapshot.add_argument(
        "--contract-changed",
        action="store_true",
        help="Acknowledge that the published contract genuinely moved.",
    )
    snapshot.set_defaults(handler=_command_snapshot)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        return int(arguments.handler(arguments))
    except (ValueError, KeyError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
