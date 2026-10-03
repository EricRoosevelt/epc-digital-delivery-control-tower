"""The local check: a user's own IFC files, checked in a workspace of their own.

The Doctor's first entry that runs anything. A user hands over one or more IFC
files, chooses one of the rule sets this checkout carries and says which
discipline each file is; the check is planned, the plan is shown, and the run
is the real pipeline — :func:`~epc_control_tower.pipeline.execute` — over a
workspace made for that one check. The result is read back through the
workspace entry (:mod:`.workspace`) exactly as a run somebody made by hand
would be: nothing about it is computed here.

**Where everything goes was decided by measurement, not by reading the code**
(AGENTS.md rule 6; the table is in the pull request that added this module).
Done without isolation, a check of one public model re-keyed every published
canonical finding of this checkout, a workspace naming the checkout's
``rules/`` rewrote ``ids/`` in the checkout, and ``epc-ct run`` kept a coverage
record in the user's state directory without telling anybody. So:

- every check is a directory of its own under the *checks directory*, which is
  outside any checkout, named when the server starts (or the user's state
  directory), and reported in every answer — never a place the user is not
  told about;
- the rule set is *copied* into the check's directory, so the IDS document it
  compiles is written there; the copy has the identity of the original, since
  every digest is of parsed content and none of a path;
- the check writes only the JSON document the Doctor reads (``exporters =
  ["json"]``), so no BCF archive is attempted and its entry limit is never
  reached; and the coverage record is kept beside the run, in the check's own
  directory.

**A check is named by what it checked.** Its identifier is a digest of the
rule set (identifier, version, normalized digest and the digest of its parsed
definitions, which unlike the normalized one sees facets), the logical date,
and each model's name, discipline and content digest. The same request is the
same check: it is run again, into the same directory, and gives the same
bytes. Nothing reads a clock.

**The plan is the scope.** Before anything runs, :meth:`LocalChecks.plan` says
which rule set at which version, which requirements, which models under which
model key and discipline, which logical date, and where the result will be
kept. It is the request a run then makes; the run's own identity says the
same, and the tests hold the two equal. Requirements are described as the
workspace entry describes them — without ``owner_role``, ``severity``,
``priority`` or ``stage``.

The pipeline needs a delivery programme covering every stage its rules name.
A user's model comes with none, so the check declares exactly those stages
with no due date. That is in the plan, under ``programme``, rather than
assumed silently.

**A refusal is a result, and names every reason** — the shape of the
workspace entry's comparison refusal: ``outcome = "refusal"``, ``refusal =
{code, text, reasons}``, ``code`` the first of ``reasons`` in
:data:`REFUSAL_CODES` order. Each reason's text says what to do next. A model
whose schema the rule set's checkers do not read (IFC2x3, say) is refused when
the check is planned, before any model is opened, for the reason the pipeline
would give. A request that is not a request at all — the wrong JSON shape —
is :class:`MalformedRequest`, a caller's error and not a refusal. Anything that
goes wrong while a check runs is a fault: it propagates, and the check's
directory is removed first, so a failed check leaves nothing behind.

One check runs at a time; a second is refused as ``busy`` rather than queued.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import shutil
import threading
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import BinaryIO

from epc_control_tower import CONTRACT_VERSION
from epc_control_tower.config import RunConfig, load_run_config
from epc_control_tower.coverage import rule_definitions_digest
from epc_control_tower.determinism import json_bytes, sha256_bytes
from epc_control_tower.domain import derive_model_key
from epc_control_tower.pipeline import execute
from epc_control_tower.registry import default_registry
from epc_control_tower.rule_definitions import load_rule_definitions
from epc_control_tower.rules import load_ruleset

from .envelope import PROJECT_ROOT
from .workspace import RUN_DOCUMENT, RUN_MANIFEST, workspace_envelope

__all__ = [
    "CHECKS_DIR_VARIABLE",
    "CHECK_RECORD",
    "LocalChecks",
    "MalformedRequest",
    "REFUSAL_CODES",
    "resolve_checks_root",
]

#: Names the checks directory; otherwise it is the user's state directory.
CHECKS_DIR_VARIABLE = "EPC_DOCTOR_CHECKS_DIR"

#: The project every check's models belong to. Fixed, so that two checks of a
#: model file of the same name have the same model key and can be compared.
PROJECT_ID = "local"

#: What a check writes: the JSON document the workspace entry reads, and the
#: manifest that vouches for it. Nothing else.
EXPORTERS = ("json",)

#: The scope a check was run with, kept beside its run. Written last, so a
#: directory without it is not a finished check.
CHECK_RECORD = "check.json"

DEFAULT_MAX_MODEL_BYTES = 4 * 1024**3

#: Every reason a request is refused, in the order they are reported.
REFUSAL_CODES = (
    "busy",
    "no-model",
    "model-too-large",
    "model-incomplete",
    "not-an-ifc",
    "model-name-invalid",
    "unknown-model",
    "duplicate-model",
    "unknown-ruleset",
    "discipline-not-declared",
    "unknown-discipline",
    "unsupported-schema",
)

_CHECK_ID = re.compile(r"^[0-9a-f]{16}$")
_UPLOAD_ID = re.compile(r"^[0-9a-f]{64}$")
_SPF_START = re.compile(rb"^\s*ISO-10303-21\s*;")
_FILE_SCHEMA = re.compile(rb"FILE_SCHEMA\s*\(\s*\(\s*'([A-Za-z0-9_]+)'")
_HEADER_BYTES = 1 << 16
_UNSAFE_NAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_SLUG_CHARACTERS = re.compile(r"[^a-z0-9._-]+")
_REQUIREMENT_FIELDS = (
    "rule_id",
    "requirement_id",
    "specification_label",
    "requirement_label",
    "checker",
    "labels",
    "discipline_scope",
    "citation",
)


class MalformedRequest(ValueError):
    """The request is not shaped like one. The caller's error, not a refusal."""


def _package_checkout() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_checks_root(
    repository_root: Path = PROJECT_ROOT, *, environ: Mapping[str, str] | None = None
) -> Path:
    """Where local checks are kept, refusing any place inside a checkout.

    ``$EPC_DOCTOR_CHECKS_DIR`` when set, otherwise ``epc-control-tower/doctor-checks``
    in the user's state directory — the same parent the coverage record uses.
    Returned as given rather than resolved, so the path reported is the one the
    user can look for.
    """

    environ = os.environ if environ is None else environ
    explicit = environ.get(CHECKS_DIR_VARIABLE, "")
    if explicit:
        root = Path(explicit)
    else:
        if os.name == "nt":
            base = environ.get("LOCALAPPDATA", "")
        else:
            base = environ.get("XDG_STATE_HOME", "") or str(Path.home() / ".local" / "state")
        if not base:
            raise ValueError(
                "Cannot tell where to keep local checks: no user state directory "
                f"is set. Set {CHECKS_DIR_VARIABLE} to a directory outside the "
                "repository."
            )
        root = Path(base) / "epc-control-tower" / "doctor-checks"
    return _outside_checkouts(Path(os.path.abspath(root)), repository_root)


def _outside_checkouts(root: Path, repository_root: Path) -> Path:
    resolved = root.resolve()
    for checkout in (Path(repository_root).resolve(), _package_checkout()):
        if resolved.is_relative_to(checkout) or root.is_relative_to(checkout):
            raise ValueError(
                f"Local checks are kept outside the repository, and {root} is "
                f"inside {checkout}: a user's model and its results would become "
                f"untracked files of the checkout. Set {CHECKS_DIR_VARIABLE} to "
                "a directory elsewhere."
            )
    return root


def _refused(reasons: list[tuple[str, str]]) -> dict[str, object]:
    ordered = sorted(reasons, key=lambda reason: REFUSAL_CODES.index(reason[0]))
    listed = [{"code": code, "text": f"[{code}] {text}"} for code, text in ordered]
    return {
        "outcome": "refusal",
        "refusal": {
            "code": listed[0]["code"],
            "text": "\n".join(reason["text"] for reason in listed),
            "reasons": listed,
        },
    }


def _header_schema(head: bytes) -> str | None:
    """The schema an IFC-SPF file's header names, or ``None`` if it is not one."""

    if head.startswith(b"\xef\xbb\xbf"):
        head = head[3:]
    if not _SPF_START.match(head):
        return None
    found = _FILE_SCHEMA.search(head)
    return found.group(1).decode("ascii").upper() if found else None


def _name_problem(name: object) -> str | None:
    if not isinstance(name, str) or not name:
        return "a model needs the name of its file"
    if (
        _UNSAFE_NAME.search(name)
        or name.startswith(".")
        or name != name.strip()
        or not name.lower().endswith(".ifc")
        or len(name) > 200
    ):
        return (
            f"{name!r} cannot name a model: it must be a file name ending in "
            '.ifc, not starting with ".", and without a path or any of '
            '< > : " / \\ | ? *. Rename the file and choose it again.'
        )
    return None


def _model_id(filename: str) -> str:
    """A model's project-scoped code, from its file name.

    The same file name gives the same code, so two checks of one model can be
    compared. A name with nothing a code can be spelled from is coded by its
    digest instead.
    """

    slug = _SLUG_CHARACTERS.sub("-", Path(filename).stem.lower()).strip("-.")
    if slug and slug[0].isalnum():
        return slug[:64]
    return "m-" + sha256_bytes(filename.encode("utf-8"))[:12]


def _toml_string(value: str) -> str:
    # A JSON string with every non-ASCII character escaped is a valid TOML
    # basic string.
    return json.dumps(value, ensure_ascii=True)


@dataclasses.dataclass(frozen=True)
class _RuleSet:
    name: str
    path: Path
    title: str
    description: str
    ruleset: object
    definitions_digest: str

    def summary(self) -> dict[str, object]:
        return {
            "name": self.name,
            "id": self.ruleset.ruleset_id,
            "version": self.ruleset.version,
            "normalized_digest": self.ruleset.normalized_digest,
            "definitions_digest": self.definitions_digest,
            "title": self.title,
            "description": self.description,
        }


class LocalChecks:
    """Staging, planning, running and reading local checks under one directory."""

    #: What :meth:`plan` and :meth:`run` raise for a request of the wrong shape,
    #: here so that a caller holding only the instance can tell it apart.
    MalformedRequest = MalformedRequest

    def __init__(
        self,
        root: Path,
        *,
        repository_root: Path = PROJECT_ROOT,
        max_model_bytes: int = DEFAULT_MAX_MODEL_BYTES,
    ) -> None:
        self.root = _outside_checkouts(Path(os.path.abspath(root)), repository_root)
        self.repository_root = Path(repository_root)
        self.max_model_bytes = max_model_bytes
        self._running = threading.Lock()

    # -- what may be chosen ------------------------------------------------

    def _rulesets(self) -> dict[str, _RuleSet]:
        """Every rule set this checkout carries, read without writing anything.

        A rule directory compiles to its IDS document in memory here; only a
        checker writes that document, and only into the check's own copy.
        """

        found: dict[str, _RuleSet] = {}
        for marker in sorted((self.repository_root / "rules").glob("*/ruleset.toml")):
            path = marker.parent
            definition = load_rule_definitions(path)
            found[path.name] = _RuleSet(
                name=path.name,
                path=path,
                title=definition.title,
                description=definition.description,
                ruleset=load_ruleset(path),
                definitions_digest=rule_definitions_digest(path) or "",
            )
        return found

    @staticmethod
    def _disciplines(rulesets: Mapping[str, _RuleSet]) -> list[str]:
        return sorted(
            {
                discipline
                for item in rulesets.values()
                for requirement in item.ruleset.requirements
                for discipline in requirement.discipline_scope
            }
        )

    def describe(self) -> dict[str, object]:
        """What a user may choose, and where the checks will be kept."""

        rulesets = self._rulesets()
        return {
            "checks_dir": str(self.root),
            "as_of": self._as_of(),
            "max_model_bytes": self.max_model_bytes,
            "rulesets": [item.summary() for item in rulesets.values()],
            "disciplines": self._disciplines(rulesets),
        }

    def _as_of(self) -> str:
        # The checkout's configured logical date: configuration, never a clock.
        return load_run_config(self.repository_root).as_of

    # -- staging -----------------------------------------------------------

    def _uploads(self) -> Path:
        return self.root / "uploads"

    def stage_model(self, filename: str, stream: BinaryIO, length: int) -> dict[str, object]:
        """Keep one model file under the checks directory, named by its digest.

        Refused unread when its name or declared length is not acceptable;
        refused and not kept when it arrives short or is not IFC-SPF text.
        """

        problem = _name_problem(filename)
        if problem is not None:
            return _refused([("model-name-invalid", problem)])
        if length > self.max_model_bytes:
            return _refused(
                [
                    (
                        "model-too-large",
                        f"{filename} is {length} bytes and this server accepts at "
                        f"most {self.max_model_bytes}. Start the server with a "
                        "larger --max-model-bytes, or check a smaller export.",
                    )
                ]
            )

        uploads = self._uploads()
        uploads.mkdir(parents=True, exist_ok=True)
        partial = uploads / f".partial-{uuid.uuid4().hex}"
        digest = hashlib.sha256()
        head = bytearray()
        received = 0
        try:
            with partial.open("wb") as out:
                while received < length:
                    block = stream.read(min(1 << 20, length - received))
                    if not block:
                        break
                    received += len(block)
                    digest.update(block)
                    if len(head) < _HEADER_BYTES:
                        head.extend(block[: _HEADER_BYTES - len(head)])
                    out.write(block)
            if received < length:
                return _refused(
                    [
                        (
                            "model-incomplete",
                            f"only {received} of {length} bytes of {filename} "
                            "arrived. Choose the file again.",
                        )
                    ]
                )
            schema = _header_schema(bytes(head))
            if schema is None:
                return _refused(
                    [
                        (
                            "not-an-ifc",
                            f"{filename} is not an IFC file: it does not begin with "
                            "an ISO-10303-21 header naming a schema. Choose the .ifc "
                            "file the authoring tool exported (IFC-SPF text, not "
                            ".ifczip or .ifcxml).",
                        )
                    ]
                )
            upload = digest.hexdigest()
            os.replace(partial, uploads / f"{upload}.ifc")
        finally:
            partial.unlink(missing_ok=True)
        return {
            "outcome": "staged",
            "model": {
                "upload": upload,
                "filename": filename,
                "byte_count": received,
                "ifc_schema": schema,
            },
        }

    # -- planning ----------------------------------------------------------

    def plan(self, request: object) -> dict[str, object]:
        """The scope a check of ``request`` would have, or every reason it cannot run."""

        if not isinstance(request, Mapping):
            raise MalformedRequest("a check request is a JSON object")
        name = request.get("ruleset")
        models = request.get("models")
        if not isinstance(name, str) or not isinstance(models, list):
            raise MalformedRequest('a check request has "ruleset" (text) and "models" (a list)')
        if not all(isinstance(entry, Mapping) for entry in models):
            raise MalformedRequest('each of "models" is an object')

        reasons: list[tuple[str, str]] = []
        rulesets = self._rulesets()
        vocabulary = self._disciplines(rulesets)
        chosen = rulesets.get(name)
        if chosen is None:
            reasons.append(
                (
                    "unknown-ruleset",
                    f"{name!r} is not a rule set this checkout carries; choose one "
                    f"of {sorted(rulesets)}.",
                )
            )
        if not models:
            reasons.append(("no-model", "choose at least one IFC file to check."))

        planned: list[dict[str, object]] = []
        seen: dict[str, set[str]] = {"upload": set(), "filename": set(), "model_id": set()}
        for entry in models:
            upload, filename = entry.get("upload"), entry.get("filename")
            discipline = entry.get("discipline")
            path = (
                self._uploads() / f"{upload}.ifc"
                if isinstance(upload, str) and _UPLOAD_ID.match(upload)
                else None
            )
            if path is None or not path.is_file():
                reasons.append(
                    (
                        "unknown-model",
                        f"{filename!r} is not a file this server holds; choose the file again.",
                    )
                )
                continue
            problem = _name_problem(filename)
            if problem is not None:
                reasons.append(("model-name-invalid", problem))
                continue
            model_id = _model_id(filename)
            keys = {"upload": upload, "filename": filename.casefold(), "model_id": model_id}
            duplicate = any(keys[kind] in seen[kind] for kind in keys)
            if duplicate:
                reasons.append(
                    (
                        "duplicate-model",
                        f"{filename} is chosen twice, or shares its file name or "
                        "content with another chosen file; choose each model once.",
                    )
                )
            for kind, key in keys.items():
                seen[kind].add(key)
            if not isinstance(discipline, str) or not discipline:
                reasons.append(
                    (
                        "discipline-not-declared",
                        f"say which discipline {filename} is: one of {vocabulary}.",
                    )
                )
            elif discipline not in vocabulary:
                reasons.append(
                    (
                        "unknown-discipline",
                        f"{discipline!r} is not a discipline any rule set here "
                        f"names; choose one of {vocabulary}.",
                    )
                )
            if duplicate:
                continue
            with path.open("rb") as stream:
                schema = _header_schema(stream.read(_HEADER_BYTES))
            planned.append(
                {
                    "model_id": model_id,
                    "model_key": derive_model_key(PROJECT_ID, model_id),
                    "filename": filename,
                    "discipline": discipline,
                    "content_sha256": upload,
                    "byte_count": path.stat().st_size,
                    "ifc_schema": schema,
                }
            )

        if chosen is not None:
            reasons.extend(self._schema_reasons(chosen, planned))
        if reasons:
            return _refused(reasons)
        return {"outcome": "plan", "plan": self._scope(chosen, planned)}

    def _schema_reasons(
        self, chosen: _RuleSet, planned: list[dict[str, object]]
    ) -> list[tuple[str, str]]:
        """The models a checker of this rule set cannot read, as the pipeline decides it.

        The same registry the run will use, asked the same question its planning
        asks — which schemas each routed checker declares — before any model is
        opened rather than after ingest.
        """

        registry = default_registry(
            RunConfig(repository_root=self.repository_root, ruleset_path=chosen.path)
        )
        reasons: list[tuple[str, str]] = []
        for checker_id in registry.route(chosen.ruleset.requirements):
            supported = registry.checker(checker_id).capabilities.ifc_schemas
            if not supported:
                continue
            for model in planned:
                if model["ifc_schema"] not in supported:
                    reasons.append(
                        (
                            "unsupported-schema",
                            f"{model['filename']} is {model['ifc_schema']}, and this "
                            f"rule set's checker {checker_id!r} reads "
                            f"{list(supported)} only. Export the model again as "
                            "IFC4 (in Revit: IFC4 Reference View) and choose that "
                            "file.",
                        )
                    )
        return reasons

    def _scope(self, chosen: _RuleSet, planned: list[dict[str, object]]) -> dict[str, object]:
        models = sorted(planned, key=lambda model: model["model_key"])
        as_of = self._as_of()
        identity = {
            "contract_version": CONTRACT_VERSION,
            "ruleset": {
                key: chosen.summary()[key]
                for key in ("name", "id", "version", "normalized_digest", "definitions_digest")
            },
            "as_of": as_of,
            "models": [
                {
                    key: model[key]
                    for key in ("model_id", "filename", "discipline", "content_sha256")
                }
                for model in models
            ],
        }
        check_id = sha256_bytes(json_bytes(identity))[:16]
        requirements = {
            requirement.requirement_key: {
                field: (
                    list(getattr(requirement, field))
                    if isinstance(getattr(requirement, field), tuple)
                    else getattr(requirement, field)
                )
                for field in _REQUIREMENT_FIELDS
            }
            for requirement in sorted(
                chosen.ruleset.requirements, key=lambda item: item.requirement_key
            )
        }
        stages = sorted({r.stage for r in chosen.ruleset.requirements if r.stage})
        return {
            "check_id": check_id,
            "ruleset": chosen.summary(),
            "requirements": requirements,
            "models": models,
            "as_of": as_of,
            "programme": [{"stage": stage, "due": ""} for stage in stages],
            "exporters": list(EXPORTERS),
            "location": str(self.root / "checks" / check_id),
        }

    # -- running -----------------------------------------------------------

    def run(self, request: object) -> dict[str, object]:
        """Plan ``request`` and, if it may run, run it; return the finished check."""

        planned = self.plan(request)
        if planned["outcome"] != "plan":
            return planned
        if not self._running.acquire(blocking=False):
            return _refused(
                [
                    (
                        "busy",
                        "another check is running. Wait for it to finish, then run this one.",
                    )
                ]
            )
        try:
            return {"outcome": "finished", "check": self._run(planned["plan"])}
        finally:
            self._running.release()

    def _run(self, scope: dict[str, object]) -> dict[str, object]:
        directory = Path(scope["location"])
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)
        try:
            ruleset = scope["ruleset"]
            rules = directory / "rules" / ruleset["name"]
            shutil.copytree(self.repository_root / "rules" / ruleset["name"], rules)
            project = directory / "projects" / PROJECT_ID
            project.mkdir(parents=True)
            manifest = [
                "[project]",
                f"project_id = {_toml_string(PROJECT_ID)}",
                f"name = {_toml_string('Local check ' + scope['check_id'])}",
            ]
            for model in scope["models"]:
                shutil.copyfile(
                    self._uploads() / f"{model['content_sha256']}.ifc",
                    project / model["filename"],
                )
                manifest += [
                    "",
                    "[[models]]",
                    f"model_id = {_toml_string(model['model_id'])}",
                    f"discipline = {_toml_string(model['discipline'])}",
                    f"filename = {_toml_string(model['filename'])}",
                    f"content_sha256 = {_toml_string(model['content_sha256'])}",
                ]
            for stage in scope["programme"]:
                manifest += [
                    "",
                    "[[milestones]]",
                    f"stage = {_toml_string(stage['stage'])}",
                    f"due = {_toml_string(stage['due'])}",
                ]
            (project / "project.toml").write_bytes(("\n".join(manifest) + "\n").encode("utf-8"))
            config = [
                "[run]",
                f"ruleset_path = {_toml_string('rules/' + ruleset['name'])}",
                f"as_of = {_toml_string(scope['as_of'])}",
                "exporters = [" + ", ".join(_toml_string(e) for e in scope["exporters"]) + "]",
            ]
            (directory / "control-tower.toml").write_bytes(
                ("\n".join(config) + "\n").encode("utf-8")
            )

            result = execute(load_run_config(directory), coverage_root=directory / "coverage")
            run = result.pipeline.bundle.run
            if (run.ruleset_id, run.ruleset_version, run.ruleset_normalized_digest) != (
                ruleset["id"],
                ruleset["version"],
                ruleset["normalized_digest"],
            ):
                raise RuntimeError(
                    f"the check ran rule set {run.ruleset_id} {run.ruleset_version} "
                    f"({run.ruleset_normalized_digest}), not the planned one"
                )
            record = {key: value for key, value in scope.items() if key != "location"}
            (directory / CHECK_RECORD).write_bytes(json_bytes(record))
        except BaseException:
            shutil.rmtree(directory, ignore_errors=True)
            raise
        return self._summary(directory)

    # -- reading -----------------------------------------------------------

    def _summary(self, directory: Path) -> dict[str, object]:
        record = json.loads((directory / CHECK_RECORD).read_text(encoding="utf-8"))
        return {"check_id": directory.name, "location": str(directory), "scope": record}

    def _finished(self, check_id: object) -> Path | None:
        if not isinstance(check_id, str) or not _CHECK_ID.match(check_id):
            return None
        directory = self.root / "checks" / check_id
        finished = all(
            (directory / name).is_file() for name in (CHECK_RECORD, RUN_DOCUMENT, RUN_MANIFEST)
        )
        return directory if finished else None

    def checks(self) -> list[dict[str, object]]:
        """Every finished check under the checks directory, by identifier."""

        root = self.root / "checks"
        if not root.is_dir():
            return []
        return [
            self._summary(directory)
            for directory in sorted(root.iterdir(), key=lambda path: path.name)
            if self._finished(directory.name) is not None
        ]

    def envelope(self, check_id: str, prior: str | None = None) -> dict[str, object]:
        """The workspace entry's envelope for a finished check, unchanged.

        Raises :class:`KeyError` for an identifier that names no finished check.
        """

        directory = self._finished(check_id)
        earlier = self._finished(prior) if prior is not None else None
        if directory is None or (prior is not None and earlier is None):
            raise KeyError(
                f"no finished local check {check_id!r}" + (f" or {prior!r}" if prior else "")
            )
        return workspace_envelope(directory, earlier)
