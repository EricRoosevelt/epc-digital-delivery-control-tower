"""The coverage record: what one run checked, and what it did not.

ADR 0004, checkpoint 1. An **internal** record, bound to the run that produced
it. It is not a published artifact: it is not written under
``data/processed/`` or ``reports/``, it is not listed in
``artifact_manifest.json``, it takes no part in any identity, and it is not a
data contract. It is also not a pipeline component — not a checker, not a
grouping policy, not an exporter — because it is none of those three shapes,
and registering it as an exporter would have folded it into
``artifact_bundle_id``.

Three granularities, which do not stand in for one another (ADR 0004 §2.1):

* **requirement × model** — one row per pair in the run, on two independent
  axes (§2.2). The *declaration* axis says what was declared about the pair
  beforehand: its adoption, and how the model's declared discipline relates to
  the rule's ``discipline_scope``. The *execution* axis says what actually
  happened. Each axis carries exactly one value, and the two are not required
  to agree: R-001 on the PCERT structural walls is ``outside`` × ``executed-with-results``,
  which is an over-check, and is recorded as one rather than as "not checked".
* **requirement × member** — exists only in a Purpose assessment record. The
  validation layer does not read Purpose, so a run records that there is **no
  member layer** instead of approximating one.
* **element overall** — whether any finding of *this run, under this rule set*
  names the element. "No result from this rule set" is not "never checked":
  another rule set, another run or a person may have checked it, and this
  record asserts nothing about them.

Status and predicate travel together (P8). A status answers a question, and the
question is the rule's own facets, rendered here as declared: every constraint
the rule sets, and every parameter of that facet kind it leaves open — R-002
checks that ``IsExternal`` exists as an ``IFCBOOLEAN`` and never what its value
is. Nothing is added to the rule to make this possible. Where a predicate cannot
be read reliably off the rule — its requirement kind is defined by a checker's
implementation rather than by IDS 1.0, or the rule source is not a rule
directory, or it no longer matches what the run read — the row says so and
shows **no status at all**, neither PASS nor FAIL, only how many results came
back. A bare count of passes next to an unknown question is exactly the
statement P8 forbids, and withholding FAIL too keeps the row's meaning from
depending on which answer happened to come back; the failures themselves are
still in the findings and issues the run publishes.

Adoption does not exist yet (checkpoint 4). The two published samples are
``legacy-compat`` by PM ruling P1. Any other project is ``undeclared``: it has
made no decision because it cannot make one yet, and it was evaluated against
the whole rule set by default. ``undeclared`` is outside ADR 0004 §2.2's three
values on purpose — ``legacy-compat`` is a status granted to two named samples,
and ``adopted`` would claim a decision nobody took.

Where it is kept: ``<root>/<validation_run_id>/coverage-<digest>.json``, the
digest being the first sixteen hex digits of the file's own SHA-256. The run
id binds the record to its run; the content address keeps two different
records of one run id — a model's declared discipline, say, is not part of the
run id — side by side rather than one silently replacing the other. ``<root>``
is ``$EPC_CT_COVERAGE_DIR`` when set, otherwise the user's state directory. It
is refused anywhere inside the repository: a record left in the working tree
would be untracked pipeline output. The location is per machine, not per
repository, which is why it is an environment variable and not a key in the
tracked ``control-tower.toml``.

Only ``run`` and ``export`` write it. ``check`` does not.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path

from .determinism import atomic_write_bytes, json_bytes, sha256_bytes
from .domain import FindingStatus, RunBundle

__all__ = [
    "ADOPTION_VALUES",
    "COVERAGE_DIR_VARIABLE",
    "EXECUTION_STATES",
    "LEGACY_COMPAT_PROJECT_IDS",
    "SCOPE_RELATIONS",
    "build_coverage_record",
    "resolve_coverage_root",
    "write_coverage_record",
]

RECORD_VERSION = "1"

COVERAGE_DIR_VARIABLE = "EPC_CT_COVERAGE_DIR"

#: The two samples PM ruling P1 (ADR 0004 §9) places in the compatibility
#: state: no adoption decision was made for them, and they are evaluated
#: against the whole rule set by compatibility behaviour. A closed list, and
#: deliberately not configuration: anything that could add a project to it
#: would be a way to label a new project with a status it was never granted.
LEGACY_COMPAT_PROJECT_IDS = ("iso-reference-view", "pcert-sample")

ADOPTION_VALUES = ("adopted", "not-adopted", "legacy-compat", "undeclared")
SCOPE_RELATIONS = ("inside", "outside", "unknown")
EXECUTION_STATES = (
    "not-executed",
    "executed-no-applicable-entity",
    "executed-with-results",
    "executed-no-result",
)

#: Every parameter each IDS 1.0 facet kind has, in the order the standard lists
#: them. Used to say which constraints a rule leaves open; ``cardinality``,
#: ``uri`` and ``instructions`` are qualifiers or prose, not constraints on a
#: value, and are not listed.
_IDS_FACET_PARAMETERS = {
    "entity": ("name", "predefinedType"),
    "attribute": ("name", "value"),
    "classification": ("system", "value"),
    "property": ("propertySet", "baseName", "dataType", "value"),
    "material": ("value",),
    "partof": ("relation", "name", "predefinedType"),
}

_LEGEND = {
    "adoption": {
        "adopted": (
            "the project decided to adopt this requirement "
            "(not implemented before ADR 0004 checkpoint 4)"
        ),
        "not-adopted": (
            "the project decided, with a reason, not to adopt it "
            "(not implemented before ADR 0004 checkpoint 4)"
        ),
        "legacy-compat": (
            "a published sample (ADR 0004 P1): no adoption decision was made; "
            "the whole rule set is evaluated by compatibility behaviour"
        ),
        "undeclared": (
            "no adoption mechanism exists yet, so no decision was made; the whole "
            "rule set was evaluated by default, which is not a decision"
        ),
    },
    "scope_relation": {
        "inside": "the model's declared discipline is in the rule's discipline_scope",
        "outside": (
            "the model's declared discipline is in the rule set's discipline "
            "vocabulary but not in this rule's scope"
        ),
        "unknown": (
            "the model's declared discipline is in no rule's discipline_scope, "
            "or the rule declares no scope"
        ),
    },
    "execution": {
        "not-executed": "not handed to its checker; always carries a reason",
        "executed-no-applicable-entity": (
            "executed; the applicability selected nothing (model-level N/A)"
        ),
        "executed-with-results": "executed; returned PASS and/or FAIL",
        "executed-no-result": "executed, and no finding came back at all",
    },
    "statuses": (
        "counts of PASS, FAIL and N/A, shown only beside a derived predicate; "
        "null when the predicate is unavailable"
    ),
    "element_reach": {
        "has-results-from-this-ruleset": "at least one finding of this run names the element",
        "no-result-from-this-ruleset": (
            "no finding of this run, under this rule set, names the element; this "
            "says nothing about other rule sets, other runs or manual review"
        ),
    },
}

_NOTICE = (
    "Internal coverage record (ADR 0004 checkpoint 1). Not a published "
    "artifact, not listed in artifact_manifest.json, not part of any identity "
    "or data contract."
)

_DISPATCH = (
    "Every requirement of the rule set was handed to its checker for every "
    "model of every project in the run. No adoption mechanism and no "
    "discipline filtering exist, so no pair can be not-executed in this run."
)

_NO_MEMBER_LAYER = (
    "No member layer. Requirement x member readings exist only in a Purpose "
    "assessment record, the validation layer does not read Purpose, and this "
    "run produced no Purpose assessment."
)


# ---------------------------------------------------------------------------
# Predicates
# ---------------------------------------------------------------------------


def _render_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _render_facet(kind: str, values: Mapping[str, object]) -> str:
    declared = {key: value for key, value in values.items() if key != "instructions"}
    order = [key for key in _IDS_FACET_PARAMETERS[kind] if key in declared]
    order += sorted(key for key in declared if key not in order)
    rendered = ", ".join(f"{key}={_render_value(declared[key])}" for key in order)
    return f"{kind}[{rendered}]"


def _unavailable(reason: str) -> dict[str, object]:
    return {"state": "unavailable", "reason": reason}


def _derive_predicates(bundle: RunBundle, ruleset_path: Path) -> dict[str, dict]:
    """Map each requirement key of the run to its predicate, derived or not.

    Read back from the rule directory the run read. The rule set rebuilt from
    it must have the run's own normalized digest, or nothing is derived: a
    predicate from rules other than the ones evaluated would be a guess.
    """

    keys = [requirement.requirement_key for requirement in bundle.ruleset.requirements]
    if not ruleset_path.is_dir():
        reason = (
            "the rule source is a rule document, not a rule directory; "
            "its facets are not read here"
        )
        return {key: _unavailable(reason) for key in keys}

    from .checkers.ids_checker import requirement_label
    from .identity import build_requirement_key
    from .rule_definitions import compile_document, load_rule_definitions

    definition = load_rule_definitions(ruleset_path)
    _document, reread, _expectations = compile_document(definition)
    if reread.normalized_digest != bundle.ruleset.normalized_digest:
        reason = "the rule directory no longer matches the rule set this run evaluated"
        return {key: _unavailable(reason) for key in keys}

    predicates: dict[str, dict] = {}
    for rule in definition.rules:
        for facet in rule.requirements:
            if rule.checker == "ids" and facet.kind in _IDS_FACET_PARAMETERS:
                key = build_requirement_key(rule.rule_id, requirement_label(facet.build()))
                predicates[key] = {
                    "state": "derived",
                    "source": f"rule {rule.rule_id} facets (IDS 1.0)",
                    "applicability": [
                        _render_facet(item.kind, item.values)
                        for item in rule.applicability
                    ],
                    "requirement": _render_facet(facet.kind, facet.values),
                    "not_constrained": [
                        parameter
                        for parameter in _IDS_FACET_PARAMETERS[facet.kind]
                        if parameter not in facet.values
                    ],
                }
            else:
                key = build_requirement_key(rule.rule_id, facet.kind)
                predicates[key] = _unavailable(
                    f"requirement kind {facet.kind!r} is defined by the "
                    f"implementation of checker {rule.checker!r}, not by IDS 1.0; "
                    "what a result asserts cannot be read from the rule's declaration"
                )

    for key in keys:
        predicates.setdefault(
            key, _unavailable("no facet of the rule directory produces this requirement")
        )
    return predicates


# ---------------------------------------------------------------------------
# The record
# ---------------------------------------------------------------------------


def _adoption(project_id: str) -> str:
    return "legacy-compat" if project_id in LEGACY_COMPAT_PROJECT_IDS else "undeclared"


def _scope_relation(discipline: str, scope: tuple[str, ...], vocabulary: set[str]) -> str:
    if not scope or discipline not in vocabulary:
        return "unknown"
    return "inside" if discipline in scope else "outside"


def _execution_state(statuses: Mapping[str, int]) -> str:
    if statuses[FindingStatus.PASS] + statuses[FindingStatus.FAIL]:
        return "executed-with-results"
    if statuses[FindingStatus.NOT_APPLICABLE]:
        return "executed-no-applicable-entity"
    return "executed-no-result"


def build_coverage_record(bundle: RunBundle, *, ruleset_path: Path) -> dict:
    """Build the coverage record of one completed validation run.

    Pure: reads the bundle and the rule directory the run read, writes nothing.
    """

    predicates = _derive_predicates(bundle, Path(ruleset_path))
    vocabulary = {
        discipline
        for requirement in bundle.ruleset.requirements
        for discipline in requirement.discipline_scope
    }

    counts: dict[tuple[str, str], dict[str, int]] = {}
    reached: dict[str, int] = {}
    for finding in bundle.findings:
        pair = counts.setdefault(
            (finding.model_key, finding.requirement_key),
            {status: 0 for status in FindingStatus},
        )
        pair[finding.status] += 1
        if finding.element_key:
            reached[finding.element_key] = reached.get(finding.element_key, 0) + 1

    requirements = sorted(
        bundle.ruleset.requirements,
        key=lambda requirement: (requirement.rule_id, requirement.requirement_id),
    )
    rows = []
    for model in sorted(bundle.models, key=lambda item: item.model_key):
        for requirement in requirements:
            statuses = counts.get(
                (model.model_key, requirement.requirement_key),
                {status: 0 for status in FindingStatus},
            )
            predicate = predicates[requirement.requirement_key]
            rows.append(
                {
                    "project_id": model.project_id,
                    "model_key": model.model_key,
                    "model_discipline": model.discipline,
                    "rule_id": requirement.rule_id,
                    "requirement_id": requirement.requirement_id,
                    "requirement_key": requirement.requirement_key,
                    "checker": requirement.checker,
                    "declaration": {
                        "adoption": _adoption(model.project_id),
                        "discipline_scope": list(requirement.discipline_scope),
                        "scope_relation": _scope_relation(
                            model.discipline, requirement.discipline_scope, vocabulary
                        ),
                    },
                    "execution": {
                        "state": _execution_state(statuses),
                        "not_executed_reason": None,
                    },
                    "result": {
                        "finding_count": sum(statuses.values()),
                        "predicate": predicate,
                        "statuses": (
                            {str(status): count for status, count in statuses.items()}
                            if predicate["state"] == "derived"
                            else None
                        ),
                    },
                }
            )

    project_of = {model.model_key: model.project_id for model in bundle.models}
    elements = [
        {
            "project_id": project_of[element.model_key],
            "model_key": element.model_key,
            "element_key": element.element_key,
            "global_id": element.global_id,
            "ifc_class": element.ifc_class,
            "reach": (
                "has-results-from-this-ruleset"
                if reached.get(element.element_key)
                else "no-result-from-this-ruleset"
            ),
            "finding_count": reached.get(element.element_key, 0),
        }
        for element in sorted(bundle.elements, key=lambda item: item.element_key)
    ]

    return {
        "record": "epc-control-tower coverage record",
        "record_version": RECORD_VERSION,
        "notice": _NOTICE,
        "run": {
            "validation_run_id": bundle.run.validation_run_id,
            "as_of": bundle.run.as_of,
            "contract_version": bundle.contract_version,
            "ruleset": {
                "ruleset_id": bundle.run.ruleset_id,
                "version": bundle.run.ruleset_version,
                "normalized_digest": bundle.run.ruleset_normalized_digest,
            },
            "model_inputs": [
                {"model_key": model_key, "content_sha256": digest}
                for model_key, digest in sorted(bundle.run.model_inputs)
            ],
            "checkers": [
                fingerprint.as_document()
                for fingerprint in sorted(
                    bundle.run.checker_fingerprints,
                    key=lambda item: item.component_id,
                )
            ],
        },
        "adoption_mechanism": "not-implemented",
        "dispatch": _DISPATCH,
        "requirement_x_model": rows,
        "requirement_x_member": {"layer": "no-member-layer", "reason": _NO_MEMBER_LAYER},
        "element_overall": elements,
        "summary": _summary(rows, elements),
        "legend": _LEGEND,
    }


def _summary(rows: list[dict], elements: list[dict]) -> dict:
    crossed = {state: dict.fromkeys(SCOPE_RELATIONS, 0) for state in EXECUTION_STATES}
    adoption: dict[str, int] = {}
    predicate: dict[str, int] = {}
    for row in rows:
        crossed[row["execution"]["state"]][row["declaration"]["scope_relation"]] += 1
        value = row["declaration"]["adoption"]
        adoption[value] = adoption.get(value, 0) + 1
        state = row["result"]["predicate"]["state"]
        predicate[state] = predicate.get(state, 0) + 1
    reach: dict[str, int] = {}
    for element in elements:
        reach[element["reach"]] = reach.get(element["reach"], 0) + 1
    return {
        "pairs": len(rows),
        "execution_by_scope_relation": crossed,
        "adoption": adoption,
        "predicate": predicate,
        "elements": {"total": len(elements), **reach},
    }


# ---------------------------------------------------------------------------
# Where it is kept
# ---------------------------------------------------------------------------


def _package_checkout() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_coverage_root(
    repository_root: Path, *, environ: Mapping[str, str] | None = None
) -> Path:
    """Where coverage records are kept, refusing any place inside a checkout.

    Called before a run opens any model, so a bad location costs nothing.
    """

    environ = os.environ if environ is None else environ
    explicit = environ.get(COVERAGE_DIR_VARIABLE, "")
    if explicit:
        root = Path(explicit)
    else:
        if os.name == "nt":
            base = environ.get("LOCALAPPDATA", "")
        else:
            base = environ.get("XDG_STATE_HOME", "") or str(
                Path.home() / ".local" / "state"
            )
        if not base:
            raise ValueError(
                "Cannot tell where to keep the coverage record: no user state "
                f"directory is set. Set {COVERAGE_DIR_VARIABLE} to a directory "
                "outside the repository."
            )
        root = Path(base) / "epc-control-tower" / "coverage"

    # Compared resolved, so a link cannot carry the record into a checkout;
    # returned as given, so the path reported is the one the user named rather
    # than wherever the platform redirects it.
    root = Path(os.path.abspath(root))
    resolved = root.resolve()
    for checkout in (Path(repository_root).resolve(), _package_checkout()):
        if resolved.is_relative_to(checkout) or root.is_relative_to(checkout):
            raise ValueError(
                f"The coverage record is kept outside the repository, and {root} "
                f"is inside {checkout}. A record left in the working tree would be "
                f"untracked pipeline output. Set {COVERAGE_DIR_VARIABLE} to a "
                "directory elsewhere."
            )
    return root


def write_coverage_record(record: dict, root: Path) -> Path:
    """Keep ``record`` under ``root``, bound to its run; return where it went."""

    data = json_bytes(record)
    run_id = str(record["run"]["validation_run_id"])
    path = Path(root) / run_id / f"coverage-{sha256_bytes(data)[:16]}.json"
    atomic_write_bytes(path, data)
    return path
