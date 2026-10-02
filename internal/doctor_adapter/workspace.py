"""The workspace entry: one finished validation run, read from where it was written.

A workspace is a directory outside this checkout with its own
``control-tower.toml`` and ``projects/``, in which somebody ran ``epc-ct run``.
This entry hands over what that run published — its identity, its findings, the
requirements it evaluated and its element inventory — read from the run's own
``run.json`` and copied unchanged. It validates nothing, runs nothing and writes
nothing. Its envelope is always ``mode = "workspace"``, ``outcome =
"validation"``, and carries no ``record`` and no ``assessment_digest``: no
handover assessment was made, so there is none to carry.

**Which workspace is an argument, every time.** Nothing here looks for one,
lists a directory to find a run, or remembers the last one used.

**A run is believed only as far as its own manifest vouches for it.** The run
document must be listed in ``reports/artifact_manifest.json`` under the hash its
bytes have. A run whose export stopped half way, or a document edited since, is
a fault and raises; it is never shown.

**The comparison is made here, and it is all or nothing.** Given an earlier run,
the envelope carries ``comparison``: for every element × requirement pair both
runs evaluated, the earlier and the current finding side by side. That is only
said when both runs asked the same question of the same models — same rule set
identifier, version and digest, the same requirements under the same recorded
predicates, the same checkers, the same ``as_of``, the same set of models. When
any of those differs the whole request is refused with every reason named, and
no part of either run is handed over as if it were comparable.

A pair only one run evaluated is listed apart, as not re-evaluated or as newly
appearing, with whether its element is in the other run's inventory at all. It
is never counted with the pairs that have two sides. Nothing here says
"fixed", "resolved" or "improved": the adapter gives two statuses and the
screens give them back.

**Rule author metadata does not cross**, as in :mod:`.details`: a requirement is
described by its identity, wording, citation and labels, never by
``owner_role``, ``severity``, ``priority`` or ``stage``.

**``tag`` is the IFC ``Tag`` attribute of the element, read from the model file
and shown for finding the element in its authoring tool.** It is display only:
it takes no part in any key, and a pair is never matched on it. It is read from
the file the workspace's own project manifest names for that model, and only
when that file's SHA-256 is the content digest the run recorded — a tag read
from some other version of the file would be a guess. Otherwise the element has
no ``tag`` key and the model says why under ``tag_source``. The canonical
element inventory is not widened for this.
"""

from __future__ import annotations

import functools
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from epc_control_tower import CONTRACT_VERSION
from epc_control_tower.config import load_project_manifests, load_run_config

__all__ = [
    "REFUSAL_CODES",
    "RUN_DOCUMENT",
    "RUN_MANIFEST",
    "WORKSPACE",
    "workspace_envelope",
]

WORKSPACE = "workspace"

#: Where a run leaves its document and the manifest that vouches for it,
#: relative to the workspace. The default layout, and the only one read: a
#: workspace that redirected its outputs is not guessed at.
RUN_DOCUMENT = "data/processed/canonical/run.json"
RUN_MANIFEST = "reports/artifact_manifest.json"

#: Every reason a comparison is refused, in the order they are reported.
REFUSAL_CODES = (
    "ruleset-id-differs",
    "ruleset-version-differs",
    "ruleset-digest-differs",
    "requirement-set-differs",
    "requirement-semantics-not-recorded",
    "requirement-semantics-differs",
    "checker-differs",
    "as-of-differs",
    "model-set-differs",
)

_FINDING_FIELDS = ("finding_key", "status", "expected", "actual", "reason")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _listed(value: str) -> list[str]:
    """A ``;``-joined column of the run document, as the list it was."""

    return [item for item in value.split(";") if item]


def _read_run(root: Path) -> dict[str, object]:
    """The run document under ``root``, once its manifest has vouched for it."""

    document_path, manifest_path = root / RUN_DOCUMENT, root / RUN_MANIFEST
    for path in (document_path, manifest_path):
        if not path.is_file():
            raise FileNotFoundError(f"{root} holds no finished run: {path} is missing")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    vouched = [a["sha256"] for a in manifest["artifacts"] if a["path"] == RUN_DOCUMENT]
    if vouched != [_sha256(document_path)]:
        raise ValueError(
            f"{document_path} is not the document {manifest_path} describes; "
            "the run did not finish, or a file was changed after it did"
        )

    document = json.loads(document_path.read_text(encoding="utf-8"))
    if document["contract_version"] != CONTRACT_VERSION:
        raise ValueError(
            f"{document_path} was written under contract "
            f"{document['contract_version']!r}; this adapter reads {CONTRACT_VERSION!r}"
        )

    run = document["run"]
    models = {model["model_key"]: model for model in document["models"]}
    recorded = {m["model_key"]: m["content_sha256"] for m in run["model_inputs"]}
    if recorded != {key: model["content_sha256"] for key, model in models.items()}:
        raise ValueError(f"{document_path}: models and run.model_inputs disagree")

    elements = {element["element_key"] for element in document["elements"]}
    requirements = {r["requirement_key"] for r in document["requirements"]}
    pairs: set[tuple[str, str, str]] = set()
    for finding in document["findings"]:
        pair = _pair(finding)
        if (
            finding["validation_run_id"] != run["validation_run_id"]
            or finding["model_key"] not in models
            or finding["requirement_key"] not in requirements
            or (finding["element_key"] and finding["element_key"] not in elements)
            or pair in pairs
        ):
            raise ValueError(
                f"{document_path}: finding {finding['finding_key']!r} does not "
                "belong to the run that document describes"
            )
        pairs.add(pair)
    return document


def _pair(finding: Mapping[str, object]) -> tuple[str, str, str]:
    """What a finding is about. An empty ``element_key`` is a model-level finding."""

    return (finding["model_key"], finding["element_key"], finding["requirement_key"])


def _identity(document: Mapping[str, object]) -> dict[str, object]:
    run = document["run"]
    return {
        "validation_run_id": run["validation_run_id"],
        "as_of": run["as_of"],
        "ruleset": {
            "id": run["ruleset"]["id"],
            "version": run["ruleset"]["version"],
            "normalized_digest": run["ruleset"]["normalized_digest"],
        },
        "checkers": [
            {key: checker[key] for key in ("id", "version", "config_sha256")}
            for checker in sorted(run["checkers"], key=lambda checker: checker["id"])
        ],
        "models": [
            {
                key: model[key]
                for key in (
                    "model_key",
                    "project_id",
                    "model_id",
                    "discipline",
                    "filename",
                    "content_sha256",
                )
            }
            for model in sorted(document["models"], key=lambda model: model["model_key"])
        ],
    }


def _requirements(document: Mapping[str, object]) -> dict[str, dict[str, object]]:
    return {
        row["requirement_key"]: {
            "rule_id": row["rule_id"],
            "requirement_id": row["requirement_id"],
            "specification_label": row["specification_label"],
            "requirement_label": row["requirement_label"],
            "checker": row["checker"],
            "labels": _listed(row["labels"]),
            "discipline_scope": _listed(row["discipline_scope"]),
            "citation": row["citation"],
            "semantics_digest": row["semantics_digest"],
        }
        for row in sorted(document["requirements"], key=lambda row: row["requirement_key"])
    }


def _finding(finding: Mapping[str, object]) -> dict[str, object]:
    return {key: finding[key] for key in _FINDING_FIELDS}


def _findings(document: Mapping[str, object]) -> list[dict[str, object]]:
    return [
        {
            "model_key": finding["model_key"],
            "element_key": finding["element_key"],
            "requirement_key": finding["requirement_key"],
            **_finding(finding),
        }
        for finding in sorted(document["findings"], key=_pair)
    ]


def _element(element: Mapping[str, object]) -> dict[str, object]:
    return {
        key: element[key]
        for key in ("name", "ifc_class", "storey", "global_id", "model_key")
    }


@functools.lru_cache(maxsize=8)
def _file_tags(path: str, content_sha256: str) -> Mapping[str, str]:
    """``GlobalId`` → ``Tag`` for every element of one model file that states one.

    Keyed by the digest as well as the path, so a file replaced between two
    calls is read again rather than answered from the earlier one.
    """

    import ifcopenshell

    tags: dict[str, str] = {}
    for entity in ifcopenshell.open(path).by_type("IfcElement"):
        tag = getattr(entity, "Tag", None)
        if tag is not None:
            tags[entity.GlobalId] = str(tag)
    return tags


def _model_files(workspace: Path) -> dict[str, Path]:
    """``model_key`` → the file the workspace's own manifests name for it."""

    config = load_run_config(workspace)
    if not config.project_manifests:
        return {}
    return {
        model.model_key: manifest.raw_data_dir / model.filename
        for manifest in load_project_manifests(
            config.project_manifests, repository_root=workspace
        )
        for model in manifest.models
    }


def _tags(
    workspace: Path, models: list[dict[str, object]]
) -> dict[str, Mapping[str, str]]:
    """Read each model's tags if its file is the one the run read; say so on the model."""

    files = _model_files(workspace)
    tags: dict[str, Mapping[str, str]] = {}
    for model in models:
        path = files.get(model["model_key"])
        if path is None or not path.is_file():
            model["tag_source"] = "model-file-not-located"
        elif _sha256(path) != model["content_sha256"]:
            model["tag_source"] = "model-file-differs"
        else:
            model["tag_source"] = "model-file"
            tags[model["model_key"]] = _file_tags(str(path), model["content_sha256"])
    return tags


def _display_elements(
    document: Mapping[str, object],
    tags: Mapping[str, Mapping[str, str]],
    only: frozenset[str] | None = None,
) -> dict[str, dict[str, object]]:
    elements: dict[str, dict[str, object]] = {}
    for row in sorted(document["elements"], key=lambda row: row["element_key"]):
        if only is not None and row["element_key"] not in only:
            continue
        element = _element(row)
        tag = tags.get(row["model_key"], {}).get(row["global_id"])
        if tag is not None:
            element["tag"] = tag
        elements[row["element_key"]] = element
    return elements


def _refusal_reasons(
    prior: Mapping[str, object], current: Mapping[str, object]
) -> list[dict[str, str]]:
    """Every way the two runs did not ask the same question of the same models."""

    reasons: list[dict[str, str]] = []

    def refuse(code: str, text: str) -> None:
        reasons.append({"code": code, "text": f"[{code}] {text}"})

    was, now = prior["run"], current["run"]
    for code, field in (
        ("ruleset-id-differs", "id"),
        ("ruleset-version-differs", "version"),
        ("ruleset-digest-differs", "normalized_digest"),
    ):
        if was["ruleset"][field] != now["ruleset"][field]:
            refuse(
                code,
                f"the earlier run's rule set {field} is {was['ruleset'][field]!r} "
                f"and the current run's is {now['ruleset'][field]!r}",
            )

    before = {r["requirement_key"]: r for r in prior["requirements"]}
    after = {r["requirement_key"]: r for r in current["requirements"]}
    if set(before) != set(after):
        refuse(
            "requirement-set-differs",
            f"{len(set(before) - set(after))} requirement(s) only the earlier run "
            f"evaluated, {len(set(after) - set(before))} only the current one",
        )
    for key in sorted(set(before) & set(after)):
        one, other = before[key]["semantics_digest"], after[key]["semantics_digest"]
        name = f"{after[key]['rule_id']} {after[key]['requirement_id']!r}"
        if not one or not other:
            refuse(
                "requirement-semantics-not-recorded",
                f"{name}: a run recorded no predicate digest, so the two cannot be "
                "shown to be the same check",
            )
        elif one != other:
            refuse(
                "requirement-semantics-differs",
                f"{name}: the predicate digest is {one} in the earlier run and "
                f"{other} in the current one",
            )

    def checkers(run: Mapping[str, object]) -> list[tuple[str, str, str]]:
        return sorted((c["id"], c["version"], c["config_sha256"]) for c in run["checkers"])

    if checkers(was) != checkers(now):
        refuse(
            "checker-differs",
            f"the earlier run was checked by {checkers(was)} and the current one "
            f"by {checkers(now)}",
        )
    if was["as_of"] != now["as_of"]:
        refuse(
            "as-of-differs",
            f"the earlier run is as of {was['as_of']!r} and the current one as of "
            f"{now['as_of']!r}",
        )

    earlier = {model["model_key"] for model in prior["models"]}
    later = {model["model_key"] for model in current["models"]}
    if earlier != later:
        refuse(
            "model-set-differs",
            f"model(s) only in the earlier run: {sorted(earlier - later)}; only in "
            f"the current run: {sorted(later - earlier)}",
        )
    return sorted(reasons, key=lambda reason: REFUSAL_CODES.index(reason["code"]))


def _comparison(
    workspace: Path,
    prior: Mapping[str, object],
    current: Mapping[str, object],
) -> dict[str, object]:
    was = {_pair(finding): finding for finding in prior["findings"]}
    now = {_pair(finding): finding for finding in current["findings"]}
    in_prior = {element["element_key"] for element in prior["elements"]}
    in_current = {element["element_key"] for element in current["elements"]}

    def row(pair: tuple[str, str, str]) -> dict[str, object]:
        return dict(zip(("model_key", "element_key", "requirement_key"), pair, strict=True))

    def present(element_key: str, inventory: set[str]) -> bool | None:
        # A model-level finding names no element, so there is none to be present.
        return (element_key in inventory) if element_key else None

    identity = _identity(prior)
    digests = {m["model_key"]: m["content_sha256"] for m in _identity(current)["models"]}
    not_re_evaluated = [
        {
            **row(pair),
            "prior": _finding(was[pair]),
            "element_in_current_run": present(pair[1], in_current),
        }
        for pair in sorted(set(was) - set(now))
    ]
    gone = frozenset(
        item["element_key"]
        for item in not_re_evaluated
        if item["element_in_current_run"] is False
    )
    return {
        "prior_run": identity,
        "changed_models": [
            {
                "model_key": model["model_key"],
                "prior_content_sha256": model["content_sha256"],
                "current_content_sha256": digests[model["model_key"]],
            }
            for model in identity["models"]
            if model["content_sha256"] != digests[model["model_key"]]
        ],
        "pairs": [
            {**row(pair), "prior": _finding(was[pair]), "current": _finding(now[pair])}
            for pair in sorted(set(was) & set(now))
        ],
        "not_re_evaluated": not_re_evaluated,
        "newly_appearing": [
            {
                **row(pair),
                "current": _finding(now[pair]),
                "element_in_prior_run": present(pair[1], in_prior),
            }
            for pair in sorted(set(now) - set(was))
        ],
        # Elements the current inventory no longer holds, so the rows above that
        # name them can still be shown as something. Tags come from the same
        # rule as everywhere: only from a file that is the one that run read.
        "prior_elements": _display_elements(
            prior, _tags(workspace, identity["models"]), only=gone
        ),
    }


def workspace_envelope(workspace: Path, prior: Path | None = None) -> dict[str, object]:
    """The run in ``workspace``, and its comparison with the run in ``prior`` if given.

    Both are directories holding a finished run in the default layout. A
    directory that does not is a fault and raises; a comparison whose
    preconditions fail is a refusal and is returned as one.
    """

    workspace = Path(workspace)
    current = _read_run(workspace)
    earlier = _read_run(Path(prior)) if prior is not None else None

    if earlier is not None:
        reasons = _refusal_reasons(earlier, current)
        if reasons:
            return {
                "mode": WORKSPACE,
                "outcome": "refusal",
                "refusal": {
                    "code": reasons[0]["code"],
                    "text": "\n".join(reason["text"] for reason in reasons),
                    "reasons": reasons,
                },
            }

    identity = _identity(current)
    tags = _tags(workspace, identity["models"])
    envelope: dict[str, object] = {
        "mode": WORKSPACE,
        "outcome": "validation",
        "run": identity,
        "findings": _findings(current),
        "requirements": _requirements(current),
        "elements": _display_elements(current, tags),
    }
    if earlier is not None:
        envelope["comparison"] = _comparison(workspace, earlier, current)
    return envelope
