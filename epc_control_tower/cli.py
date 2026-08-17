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
