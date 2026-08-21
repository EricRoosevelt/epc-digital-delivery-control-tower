"""Run configuration and project manifests.

These are two different things and are kept apart on purpose.

A **project manifest** is *data about a project*: which models it contains,
where each came from, under what licence, and what its content hash should be.
It is versioned alongside the project and it is what a fork replaces first.

**Run configuration** is a handful of genuine runtime knobs: where output goes,
which exporters are enabled, which rule set is active, and the logical
``as_of``. It stays small deliberately. The temptation with a refactor like
this one is to sweep every frozen constant into a single settings file, which
just relocates the problem into a bag nobody can reason about. Constants that
describe a project belong in its manifest, constants that describe a rule
belong on the rule, and constants that merely record what the fixture happened
to contain belong in tests.

TOML throughout, read with :mod:`tomllib` from the standard library, so
configuration costs no dependency.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .domain import Project, ProjectMilestone, Provenance, derive_model_key

__all__ = [
    "DEFAULT_CONFIG_FILENAME",
    "DEFAULT_EXPORTERS",
    "ManifestModel",
    "ProjectManifest",
    "RunConfig",
    "discover_project_manifests",
    "load_project_manifest",
    "load_project_manifests",
    "load_run_config",
]

DEFAULT_CONFIG_FILENAME = "control-tower.toml"

#: Everything that writes a tracked artifact, so that a default run regenerates
#: the repository in full and continuous integration can simply check that
#: nothing changed.
DEFAULT_EXPORTERS = ("bcf", "csv", "json", "legacy-bcf", "legacy-pbip")

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class ManifestModel:
    """One source model as declared by a project.

    ``model_key`` is the globally stable join identity; ``model_id`` is the
    project-scoped business code. After loading, ``model_key`` is always
    populated: a manifest that declares one keeps it, and one that does not gets
    ``project_id.model_id``.

    Defaulting to the bare ``model_id`` would have been friendlier and wrong —
    two projects each with an ``architecture`` model would share a key, and
    since ``element_key`` is built from ``model_key`` their elements would merge
    silently rather than collide loudly. The shipped project pins its keys to
    the original values explicitly, which is why its published identities are
    unaffected by this rule.

    ``content_sha256`` is optional but strongly recommended. When present it is
    an assertion checked at ingest, so a silently edited or swapped input file
    fails the run instead of quietly changing the results. When absent the hash
    is recorded from whatever is on disk, which is weaker.
    """

    model_id: str
    discipline: str
    filename: str
    model_key: str
    source_url: str = ""
    license: str = ""
    content_sha256: str = ""

    def provenance(self, observed_sha256: str) -> Provenance:
        return Provenance(
            source_url=self.source_url,
            license=self.license,
            content_sha256=observed_sha256,
        )


@dataclass(frozen=True, slots=True)
class ProjectManifest:
    project: Project
    models: tuple[ManifestModel, ...]
    raw_data_dir: Path
    #: This project's delivery programme, one row per stage. Programme is
    #: project data, not rule data, so it is declared here beside the models.
    milestones: tuple[ProjectMilestone, ...] = ()

    def model_by_filename(self, filename: str) -> ManifestModel:
        for model in self.models:
            if model.filename == filename:
                return model
        raise KeyError(f"No model declared for {filename!r} in {self.project.project_id}")


@dataclass(frozen=True, slots=True)
class RunConfig:
    """The genuine runtime knobs. Keep this small.

    ``as_of`` is a logical date, not a clock reading. It participates in the
    validation identity because a rule may legitimately depend on a date, and
    it is what BCF creation timestamps are stamped with. Reading the wall clock
    here instead would make every run produce different bytes.
    """

    repository_root: Path
    as_of: str = "2026-08-13T00:00:00Z"
    ruleset_path: Path | None = None
    project_manifests: tuple[Path, ...] = ()
    processed_data_dir: Path | None = None
    reports_dir: Path | None = None
    grouping_policy: str = "element"
    exporters: tuple[str, ...] = DEFAULT_EXPORTERS
    #: Which project the legacy writers publish.
    #:
    #: The eight published CSV files and the BCF archive describe exactly one
    #: project, and that is a property of the frozen contract rather than of the
    #: pipeline. With one project configured this can be left unset; with
    #: several it is required, because guessing would silently republish a
    #: different contract under the same filenames. It retires with the legacy
    #: adapters.
    legacy_project_id: str = ""
    #: The frozen rule document the legacy writers publish.
    #:
    #: The published files mean "what rule set 0.1 said about one project".
    #: Adding a rule to the *current* document must therefore not touch them —
    #: and it would, catastrophically, since the published run_id is a digest
    #: of the document's bytes and re-keys all forty-seven findings. Left unset
    #: the legacy writers use whatever rule set the run used, which is correct
    #: only while the two are the same document. Retires with the adapters.
    legacy_ruleset_path: Path | None = None
    #: The frozen metadata the legacy topics are rendered from, keyed by
    #: requirement, and the SHA-256 that pins its exact bytes. The published
    #: archive's priority, stage, labels and assignee come from here rather than
    #: from the current rules, so a live rule edit cannot move a frozen byte.
    #: Retires with the adapters.
    legacy_compat_path: Path | None = None
    legacy_compat_sha256: str = ""
    #: How issues are rendered as BCF topics.
    #:
    #: These are here rather than on a rule because they are the same for
    #: every rule in every rule set: who is writing the archive, what the
    #: archive calls itself, and how a role becomes the address BCF insists
    #: on. A fork changes them once, not per requirement.
    #:
    #: ``bcf_project_name`` is the name of the *BCF project*, which is not
    #: the name of any ``Project`` in a manifest. The published archive calls
    #: itself after the tool, and the BCF project GUID is derived from this
    #: string, so it is configuration rather than something to look up.
    bcf_project_name: str = "EPC Digital Delivery Control Tower"
    bcf_creation_author: str = "control-tower@example.invalid"
    bcf_topic_type: str = "Issue"
    #: A role is what a rule can state; BCF wants an address. This is the
    #: domain appended to a role to make one, and no part of it is a claim
    #: that the address exists — `.invalid` is reserved precisely so that it
    #: cannot.
    bcf_role_domain: str = "example.invalid"

    def resolved_processed_data_dir(self) -> Path:
        return self.processed_data_dir or self.repository_root / "data" / "processed"

    def resolved_reports_dir(self) -> Path:
        return self.reports_dir or self.repository_root / "reports"

    def resolved_ruleset_path(self) -> Path:
        return self.ruleset_path or (
            self.repository_root / "ids" / "epc_delivery_requirements_v0.1.ids"
        )


def _read_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as stream:
        return tomllib.load(stream)


def _require(document: dict[str, object], key: str, source: Path) -> object:
    if key not in document:
        raise ValueError(f"{source} is missing required key {key!r}")
    return document[key]


def load_project_manifest(path: Path, *, repository_root: Path) -> ProjectManifest:
    """Read one ``project.toml``.

    ``raw_data_dir`` defaults to the manifest's own directory, so a project is
    self-contained and can be moved or copied wholesale.
    """

    document = _read_toml(path)
    project_section = _require(document, "project", path)
    if not isinstance(project_section, dict):
        raise ValueError(f"{path}: [project] must be a table")

    project = Project(
        project_id=str(_require(project_section, "project_id", path)),
        name=str(_require(project_section, "name", path)),
        stage=str(project_section.get("stage", "")),
        description=str(project_section.get("description", "")),
    )

    raw_entries = document.get("models", [])
    if not isinstance(raw_entries, list) or not raw_entries:
        raise ValueError(f"{path}: at least one [[models]] entry is required")

    models: list[ManifestModel] = []
    for entry in raw_entries:
        if not isinstance(entry, dict):
            raise ValueError(f"{path}: each [[models]] entry must be a table")
        model_id = str(_require(entry, "model_id", path))
        declared_key = str(entry.get("model_key", ""))
        declared_hash = str(entry.get("content_sha256", ""))
        if declared_hash and not _SHA256.match(declared_hash):
            raise ValueError(
                f"{path}: {model_id} content_sha256 must be 64 lowercase hex "
                f"characters, got {declared_hash!r}"
            )
        models.append(
            ManifestModel(
                model_id=model_id,
                discipline=str(_require(entry, "discipline", path)),
                filename=str(_require(entry, "filename", path)),
                model_key=declared_key or derive_model_key(project.project_id, model_id),
                source_url=str(entry.get("source_url", "")),
                license=str(entry.get("license", "")),
                content_sha256=declared_hash,
            )
        )

    declared_raw_dir = project_section.get("raw_data_dir")
    if declared_raw_dir:
        raw_data_dir = (repository_root / str(declared_raw_dir)).resolve()
    else:
        raw_data_dir = path.parent

    _check_manifest_uniqueness(models, path)
    milestones = _load_milestones(document, project.project_id, path)

    return ProjectManifest(
        project=project,
        models=tuple(models),
        raw_data_dir=raw_data_dir,
        milestones=milestones,
    )


def _load_milestones(
    document: dict[str, object], project_id: str, source: Path
) -> tuple[ProjectMilestone, ...]:
    """Read a project's ``[[milestones]]`` programme, failing closed on a dup.

    A ``(project_id, stage)`` pair names exactly one deadline. A stage listed
    twice is a contradiction, not a merge, so it is rejected here rather than
    silently letting the last one win. ``due`` may be absent or empty — that is
    a stated stage with no deadline — but a present ``due`` is validated as a
    timezone-aware datetime by :class:`~.domain.ProjectMilestone` itself.
    """

    raw = document.get("milestones", [])
    if not isinstance(raw, list):
        raise ValueError(f"{source}: [[milestones]] must be an array of tables")

    milestones: list[ProjectMilestone] = []
    seen: set[str] = set()
    for entry in raw:
        if not isinstance(entry, dict):
            raise ValueError(f"{source}: each [[milestones]] entry must be a table")
        stage = str(_require(entry, "stage", source))
        if stage in seen:
            raise ValueError(
                f"{source}: milestone stage {stage!r} is declared more than once"
            )
        seen.add(stage)
        milestones.append(
            ProjectMilestone(
                project_id=project_id,
                stage=stage,
                due=str(entry.get("due", "")),
            )
        )
    return tuple(milestones)


def _check_manifest_uniqueness(models: Sequence[ManifestModel], source: Path) -> None:
    for label, values in (
        ("model_id", [model.model_id for model in models]),
        ("model_key", [model.model_key for model in models]),
        ("filename", [model.filename for model in models]),
    ):
        duplicates = sorted({value for value in values if values.count(value) > 1})
        if duplicates:
            raise ValueError(f"{source}: duplicate {label} values {duplicates}")


def load_project_manifests(
    paths: Sequence[Path],
    *,
    repository_root: Path,
) -> tuple[ProjectManifest, ...]:
    """Load several manifests and check what only the whole set can show.

    Uniqueness within one manifest is not enough. ``model_key`` is a *global*
    identity, and two projects can each be internally consistent while pinning
    the same key — most easily by both pinning explicit legacy keys. Catch that
    here, where every manifest is in view.
    """

    manifests = tuple(
        load_project_manifest(path, repository_root=repository_root) for path in paths
    )

    seen_projects: dict[str, Path] = {}
    seen_model_keys: dict[str, str] = {}
    for manifest, path in zip(manifests, paths, strict=True):
        project_id = manifest.project.project_id
        if project_id in seen_projects:
            raise ValueError(
                f"{path}: project_id {project_id!r} is already declared by "
                f"{seen_projects[project_id]}"
            )
        seen_projects[project_id] = path

        for model in manifest.models:
            owner = seen_model_keys.get(model.model_key)
            if owner is not None:
                raise ValueError(
                    f"{path}: model_key {model.model_key!r} is already used by "
                    f"project {owner!r}; model_key must be globally unique"
                )
            seen_model_keys[model.model_key] = project_id

    return manifests


def discover_project_manifests(root: Path) -> tuple[Path, ...]:
    """Find every ``project.toml`` under ``root``, in a stable order."""

    if not root.exists():
        return ()
    return tuple(sorted(root.glob("*/project.toml")))


def load_run_config(
    repository_root: Path,
    path: Path | None = None,
) -> RunConfig:
    """Read run configuration, falling back to defaults that match the shipped setup."""

    config_path = path or repository_root / DEFAULT_CONFIG_FILENAME
    if not config_path.exists():
        return RunConfig(
            repository_root=repository_root,
            project_manifests=discover_project_manifests(repository_root / "projects"),
        )

    document = _read_toml(config_path)
    run_section = document.get("run", {})
    bcf_section = document.get("bcf", {})
    if not isinstance(run_section, dict):
        raise ValueError(f"{config_path}: [run] must be a table")

    def _optional_path(key: str) -> Path | None:
        value = run_section.get(key)
        return (repository_root / str(value)) if value else None

    declared_manifests = run_section.get("project_manifests")
    if declared_manifests:
        if not isinstance(declared_manifests, list):
            raise ValueError(f"{config_path}: project_manifests must be an array")
        manifests = tuple(repository_root / str(item) for item in declared_manifests)
    else:
        manifests = discover_project_manifests(repository_root / "projects")

    exporters = run_section.get("exporters", list(DEFAULT_EXPORTERS))
    if not isinstance(exporters, list):
        raise ValueError(f"{config_path}: exporters must be an array")

    return RunConfig(
        repository_root=repository_root,
        as_of=str(run_section.get("as_of", "2026-08-13T00:00:00Z")),
        bcf_project_name=str(
            bcf_section.get("project_name", "EPC Digital Delivery Control Tower")
        ),
        bcf_creation_author=str(
            bcf_section.get("creation_author", "control-tower@example.invalid")
        ),
        bcf_topic_type=str(bcf_section.get("topic_type", "Issue")),
        bcf_role_domain=str(bcf_section.get("role_domain", "example.invalid")),
        ruleset_path=_optional_path("ruleset_path"),
        project_manifests=manifests,
        processed_data_dir=_optional_path("processed_data_dir"),
        reports_dir=_optional_path("reports_dir"),
        grouping_policy=str(run_section.get("grouping_policy", "element")),
        exporters=tuple(str(item) for item in exporters),
        legacy_project_id=str(run_section.get("legacy_project_id", "")),
        legacy_ruleset_path=_optional_path("legacy_ruleset_path"),
        legacy_compat_path=_optional_path("legacy_compat_path"),
        legacy_compat_sha256=str(run_section.get("legacy_compat_sha256", "")),
    )
