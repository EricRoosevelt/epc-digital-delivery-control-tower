"""Read a Purpose Pack, and refuse it unless every structural invariant holds.

A Pack is checked entirely on its own terms, before any project is considered.
That is not tidiness: an unsound decision tree is unsound for everyone, so
catching it once at Pack load beats catching it once per project that binds the
Pack — and it means a Pack cannot be "valid for a lenient project".

The eighteen invariants of ADR 0002 §3.8 are implemented one function each,
named ``_invariant_01`` … ``_invariant_18``, and each raises with the code
``pack-invariant-NN``. The numbering is the ADR's, so a reviewer can read the
two side by side, and :mod:`tests.test_purpose_pack_invariants` asserts that
every number is reachable.

Nothing here evaluates anything. The tree is checked as a graph; no evidence is
read, no outcome is produced, and no verdict is computed. ``epc-ct run`` does
not call this module, and this module writes nothing anywhere.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from .errors import PurposePackError
from .model import (
    BINDING_SOURCES,
    SUBJECT_GRAINS,
    VERDICTS,
    Activity,
    Branch,
    DecisionNode,
    Direction,
    EvidenceRequirement,
    InsufficientEvidence,
    PackBinding,
    PairSource,
    PurposePack,
    ResolutionRoute,
)

__all__ = [
    "SUPPORTED_PACK_SCHEMA_VERSIONS",
    "discover_purpose_packs",
    "load_purpose_pack",
    "load_purpose_packs",
]

#: The Pack file formats this loader implements.
#:
#: Format ``"1"`` is published: a loader reads it, so other things may now be
#: written against it, and its shape is frozen. A Pack declaring any other
#: version is refused — there is no "load with reduced capability", because a
#: loader that half-understands a format is a loader that silently ignores the
#: half it does not.
SUPPORTED_PACK_SCHEMA_VERSIONS = frozenset({"1"})

PACK_FILENAME = "pack.toml"

# The same slug shape ``identity.py`` already applies to a ruleset version.
_SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

# An IFC entity name as ``elements.csv`` publishes it. Matched by exact string
# equality at assessment time; validated here only for shape, so a wildcard or
# a pattern cannot be smuggled in as a class name.
_IFC_CLASS = re.compile(r"^Ifc[A-Za-z0-9]+$")

_UNBOUNDED = frozenset({"*", "all", "any", "ALL", "ANY"})


def _fail(code: str, message: str, source: Path) -> None:
    raise PurposePackError(code, message, source=source)


def _table(value: object, code: str, label: str, source: Path) -> Mapping[str, object]:
    if not isinstance(value, dict):
        _fail(code, f"{label} must be a table", source)
    return value  # type: ignore[return-value]


def _rows(document: Mapping[str, object], key: str, source: Path) -> list[dict]:
    raw = document.get(key, [])
    if not isinstance(raw, list):
        _fail("pack-field-invalid", f"{key} must be an array of tables", source)
    for entry in raw:
        if not isinstance(entry, dict):
            _fail("pack-field-invalid", f"each {key} entry must be a table", source)
    return list(raw)  # type: ignore[arg-type]


def _text(entry: Mapping[str, object], key: str, label: str, source: Path) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value:
        _fail("pack-field-missing", f"{label} requires a non-empty {key}", source)
    return str(value)


def _optional_text(entry: Mapping[str, object], key: str) -> str:
    value = entry.get(key)
    return str(value) if isinstance(value, str) else ""


def _string_tuple(
    entry: Mapping[str, object], key: str, label: str, source: Path
) -> tuple[str, ...]:
    raw = entry.get(key, [])
    if not isinstance(raw, list):
        _fail("pack-field-invalid", f"{label}: {key} must be an array", source)
    values: list[str] = []
    for item in raw:  # type: ignore[union-attr]
        if not isinstance(item, str) or not item:
            _fail(
                "pack-field-invalid",
                f"{label}: {key} entries must be non-empty strings",
                source,
            )
        values.append(str(item))
    return tuple(values)


def _duplicates(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


# --------------------------------------------------------------------------
# Reading
# --------------------------------------------------------------------------


def load_purpose_pack(path: Path) -> PurposePack:
    """Read one ``pack.toml`` and refuse it unless every invariant holds."""

    path = Path(path)
    if not path.is_file():
        raise PurposePackError(
            "pack-file-missing", f"no {PACK_FILENAME} at {path}", source=path
        )

    with path.open("rb") as stream:
        document = tomllib.load(stream)

    pack_id = _text(document, "pack_id", "pack", path)
    directory_name = path.parent.name
    if pack_id != directory_name:
        _fail(
            "pack-id-directory-mismatch",
            f"pack_id {pack_id!r} must match its directory name {directory_name!r}",
            path,
        )

    schema_version = _text(document, "pack_schema_version", "pack", path)
    if schema_version not in SUPPORTED_PACK_SCHEMA_VERSIONS:
        _fail(
            "pack-schema-version-unsupported",
            f"pack_schema_version {schema_version!r} is not one this loader implements "
            f"({sorted(SUPPORTED_PACK_SCHEMA_VERSIONS)})",
            path,
        )

    pack_version = _text(document, "pack_version", "pack", path)
    if not _SLUG.match(pack_version):
        _fail(
            "pack-version-invalid",
            f"pack_version {pack_version!r} must be a slug; it is pinned by exact equality "
            "and never parsed as a range",
            path,
        )

    directions = _read_directions(document, path)
    requirements = _read_evidence_requirements(document, path)
    activities = _read_activities(document, path)
    routes = _read_resolution_routes(document, path)
    nodes = _read_decision_nodes(document, requirements, routes, path)

    pack = PurposePack(
        pack_id=pack_id,
        pack_schema_version=schema_version,
        pack_version=pack_version,
        maturity=_optional_text(document, "maturity"),
        citations=_string_tuple(document, "citations", "pack", path),
        directions=directions,
        evidence_requirements=requirements,
        activities=activities,
        resolution_routes=routes,
        decision_nodes=nodes,
    )
    _check_structural_invariants(pack, path)
    return pack


def _read_directions(document: Mapping[str, object], source: Path) -> tuple[Direction, ...]:
    entries = _rows(document, "directions", source)
    if not entries:
        _fail("pack-field-missing", "a Pack declares at least one [[directions]] entry", source)
    directions = tuple(
        Direction(
            direction_id=_text(entry, "direction_id", "directions", source),
            from_discipline=_text(entry, "from", "directions", source),
            to_discipline=_text(entry, "to", "directions", source),
        )
        for entry in entries
    )
    repeated = _duplicates(item.direction_id for item in directions)
    if repeated:
        _fail("direction-id-duplicate", f"duplicate direction_id values {repeated}", source)
    return directions


def _read_evidence_requirements(
    document: Mapping[str, object], source: Path
) -> tuple[EvidenceRequirement, ...]:
    entries = _rows(document, "evidence_requirements", source)
    if not entries:
        _fail(
            "pack-field-missing",
            "a Pack declares at least one [[evidence_requirements]] entry",
            source,
        )

    requirements: list[EvidenceRequirement] = []
    for entry in entries:
        requirement_id = _text(
            entry, "evidence_requirement_id", "evidence_requirements", source
        )
        label = f"evidence requirement {requirement_id!r}"

        binding_source = _text(entry, "binding_source", label, source)
        if binding_source not in BINDING_SOURCES:
            _fail(
                "binding-source-invalid",
                f"{label}: binding_source {binding_source!r} is not one of "
                f"{list(BINDING_SOURCES)}",
                source,
            )

        subject_grain = _text(entry, "subject_grain", label, source)
        if subject_grain not in SUBJECT_GRAINS:
            _fail(
                "subject-grain-invalid",
                f"{label}: subject_grain {subject_grain!r} is not one of "
                f"{list(SUBJECT_GRAINS)}",
                source,
            )

        outcomes = _string_tuple(entry, "outcomes", label, source)
        if len(outcomes) < 3:
            _fail(
                "outcomes-incomplete",
                f"{label}: outcomes[] must name all three states the Framework "
                "distinguishes -- satisfied, failed, and no admissible evidence yet",
                source,
            )
        repeated = _duplicates(outcomes)
        if repeated:
            _fail("outcomes-duplicate", f"{label}: duplicate outcomes {repeated}", source)

        binding = _read_pack_binding(entry, binding_source, label, source)
        insufficient = _read_insufficient_evidence(entry, label, source)
        pair_source = _read_pair_source(entry, label, source)

        requirements.append(
            EvidenceRequirement(
                evidence_requirement_id=requirement_id,
                answers=_text(entry, "answers", label, source),
                binding_source=binding_source,
                subject_grain=subject_grain,
                acceptance_condition=_text(entry, "acceptance_condition", label, source),
                outcomes=outcomes,
                pack_binding=binding,
                insufficient_evidence=insufficient,
                pair_source=pair_source,
            )
        )

    repeated = _duplicates(item.evidence_requirement_id for item in requirements)
    if repeated:
        _fail(
            "evidence-requirement-id-duplicate",
            f"duplicate evidence_requirement_id values {repeated}",
            source,
        )
    return tuple(requirements)


def _read_pack_binding(
    entry: Mapping[str, object], binding_source: str, label: str, source: Path
) -> PackBinding | None:
    raw = entry.get("pack_binding")
    if raw is None:
        if binding_source == "pack":
            _fail(
                "pack-binding-missing",
                f"{label}: binding_source is 'pack' but no [pack_binding] is declared",
                source,
            )
        return None
    if binding_source != "pack":
        _fail(
            "pack-binding-unexpected",
            f"{label}: [pack_binding] is only legal when binding_source is 'pack'; "
            "an Overlay-bound or assessment-bound question is not answered by the Pack",
            source,
        )
    table = _table(raw, "pack-field-invalid", f"{label}: pack_binding", source)
    keys = _string_tuple(table, "requirement_keys", f"{label}: pack_binding", source)
    if not keys:
        _fail(
            "pack-binding-empty",
            f"{label}: pack_binding declares no requirement_keys",
            source,
        )
    return PackBinding(
        ruleset_id=_text(table, "ruleset_id", f"{label}: pack_binding", source),
        ruleset_version=_text(table, "ruleset_version", f"{label}: pack_binding", source),
        requirement_keys=keys,
    )


def _read_insufficient_evidence(
    entry: Mapping[str, object], label: str, source: Path
) -> tuple[InsufficientEvidence, ...]:
    entries = _rows(entry, "insufficient_evidence", source)
    records = []
    for row in entries:
        sub = f"{label}: insufficient_evidence"
        records.append(
            InsufficientEvidence(
                ruleset_id=_text(row, "ruleset_id", sub, source),
                ruleset_version=_text(row, "ruleset_version", sub, source),
                requirement_key=_text(row, "requirement_key", sub, source),
                # The sentence is the point of the entry. An insufficient-evidence
                # reference with no statement of what it cannot answer is
                # indistinguishable from a binding that answers the question.
                cannot_answer=_text(row, "cannot_answer", sub, source),
            )
        )
    return tuple(records)


def _read_pair_source(
    entry: Mapping[str, object], label: str, source: Path
) -> PairSource | None:
    raw = entry.get("pair_source")
    if raw is None:
        return None
    table = _table(raw, "pack-field-invalid", f"{label}: pair_source", source)
    sub = f"{label}: pair_source"
    return PairSource(
        from_evidence_requirement_id=_text(table, "from_evidence_requirement_id", sub, source),
        on_outcome=_text(table, "on_outcome", sub, source),
        counterpart_description=_text(table, "counterpart_description", sub, source),
    )


def _read_activities(document: Mapping[str, object], source: Path) -> tuple[Activity, ...]:
    entries = _rows(document, "activities", source)
    if not entries:
        _fail("pack-field-missing", "a Pack declares at least one [[activities]] entry", source)

    activities: list[Activity] = []
    for entry in entries:
        activity_id = _text(entry, "activity_id", "activities", source)
        label = f"activity {activity_id!r}"
        classes = _string_tuple(entry, "subject_classes", label, source)
        for value in classes:
            if value in _UNBOUNDED or not _IFC_CLASS.match(value):
                _fail(
                    "subject-classes-invalid",
                    f"{label}: subject_classes entry {value!r} is not a plain IFC entity "
                    "name; the list is closed and enumerable, with no wildcard and no pattern",
                    source,
                )
        repeated = _duplicates(classes)
        if repeated:
            _fail(
                "subject-classes-invalid",
                f"{label}: duplicate subject_classes entries {repeated}",
                source,
            )
        requirement_ids = _string_tuple(entry, "evidence_requirement_ids", label, source)
        if not requirement_ids:
            _fail(
                "pack-field-missing",
                f"{label}: declares no evidence_requirement_ids",
                source,
            )
        activities.append(
            Activity(
                activity_id=activity_id,
                label=_text(entry, "label", label, source),
                direction_id=_text(entry, "direction_id", label, source),
                subject_classes=classes,
                evidence_requirement_ids=requirement_ids,
                decision_root_node=_text(entry, "decision_root_node", label, source),
            )
        )

    repeated = _duplicates(item.activity_id for item in activities)
    if repeated:
        _fail("activity-id-duplicate", f"duplicate activity_id values {repeated}", source)
    return tuple(activities)


def _read_resolution_routes(
    document: Mapping[str, object], source: Path
) -> tuple[ResolutionRoute, ...]:
    entries = _rows(document, "resolution_routes", source)
    if not entries:
        _fail(
            "pack-field-missing",
            "a Pack declares at least one [[resolution_routes]] entry",
            source,
        )
    routes: list[ResolutionRoute] = []
    for entry in entries:
        kind = _text(entry, "resolution_kind", "resolution_routes", source)
        label = f"resolution route {kind!r}"
        consequences = _string_tuple(entry, "consequence_kinds", label, source)
        if not consequences:
            _fail("route-field-missing", f"{label}: declares no consequence_kinds", source)
        routes.append(
            ResolutionRoute(
                resolution_kind=kind,
                default_role=_text(entry, "default_role", label, source),
                consequence_kinds=consequences,
                next_action=_text(entry, "next_action", label, source),
                recheck_condition=_text(entry, "recheck_condition", label, source),
            )
        )
    repeated = _duplicates(item.resolution_kind for item in routes)
    if repeated:
        _fail(
            "route-resolution-kind-duplicate",
            f"duplicate resolution_kind values {repeated}; the join key must be unique",
            source,
        )
    return tuple(routes)


def _read_decision_nodes(
    document: Mapping[str, object],
    requirements: Sequence[EvidenceRequirement],
    routes: Sequence[ResolutionRoute],
    source: Path,
) -> tuple[DecisionNode, ...]:
    entries = _rows(document, "decision_nodes", source)
    if not entries:
        _fail(
            "pack-field-missing",
            "a Pack declares at least one [[decision_nodes]] entry",
            source,
        )
    outcomes_by_requirement = {
        item.evidence_requirement_id: item.outcomes for item in requirements
    }
    route_kinds = {item.resolution_kind for item in routes}

    nodes: list[DecisionNode] = []
    for entry in entries:
        node_id = _text(entry, "node_id", "decision_nodes", source)
        requirement_id = _text(entry, "evidence_requirement_id", f"node {node_id!r}", source)
        branches = _read_branches(entry, node_id, requirement_id, route_kinds, source)

        declared = outcomes_by_requirement.get(requirement_id)
        if declared is None:
            # Invariant 4, checked here because branch coverage cannot be
            # checked at all without the outcome vocabulary.
            _fail(
                "pack-invariant-04",
                f"node {node_id!r} tests evidence_requirement_id {requirement_id!r}, "
                "which no [[evidence_requirements]] entry declares",
                source,
            )
        covered = [branch.outcome for branch in branches]
        repeated = _duplicates(covered)
        if repeated:
            _fail(
                "branch-outcome-duplicate",
                f"node {node_id!r} covers outcomes {repeated} more than once",
                source,
            )
        missing = [outcome for outcome in declared or () if outcome not in set(covered)]
        extra = [outcome for outcome in covered if outcome not in set(declared or ())]
        if missing or extra:
            _fail(
                "branch-outcome-coverage",
                f"node {node_id!r} must cover every declared outcome exactly once; "
                f"missing {missing}, unknown {extra}",
                source,
            )
        nodes.append(
            DecisionNode(
                node_id=node_id,
                evidence_requirement_id=requirement_id,
                branches=branches,
            )
        )

    repeated = _duplicates(item.node_id for item in nodes)
    if repeated:
        _fail("pack-invariant-03", f"duplicate node_id values {repeated}", source)
    return tuple(nodes)


def _read_branches(
    entry: Mapping[str, object],
    node_id: str,
    requirement_id: str,
    route_kinds: set[str],
    source: Path,
) -> tuple[Branch, ...]:
    entries = _rows(entry, "branches", source)
    if not entries:
        _fail("pack-field-missing", f"node {node_id!r} declares no branches", source)

    branches: list[Branch] = []
    for row in entries:
        outcome = _text(row, "outcome", f"node {node_id!r} branch", source)
        label = f"node {node_id!r} branch {outcome!r}"
        verdict = _optional_text(row, "verdict")
        next_node = _optional_text(row, "next_node")
        failure_kind = _optional_text(row, "failure_kind")
        gap_kind = _optional_text(row, "gap_kind")
        inapplicable = _string_tuple(row, "renders_inapplicable", label, source)

        if verdict == "CONDITIONAL":
            _fail(
                "pack-invariant-09",
                f"{label}: CONDITIONAL is not a legal leaf value anywhere in a decision "
                "tree -- it must originate in a named authorisation event, which no "
                "evidence outcome can encode",
                source,
            )
        if bool(verdict) == bool(next_node):
            _fail(
                "branch-shape-invalid",
                f"{label}: exactly one of verdict and next_node is required",
                source,
            )
        if verdict and verdict not in VERDICTS:
            _fail(
                "branch-verdict-invalid",
                f"{label}: verdict {verdict!r} is not one of {list(VERDICTS)}",
                source,
            )
        if verdict == "BLOCKED" and (not failure_kind or gap_kind):
            _fail(
                "branch-kind-mismatch",
                f"{label}: a BLOCKED leaf requires failure_kind and forbids gap_kind",
                source,
            )
        if verdict == "UNKNOWN" and (not gap_kind or failure_kind):
            _fail(
                "branch-kind-mismatch",
                f"{label}: an UNKNOWN leaf requires gap_kind and forbids failure_kind",
                source,
            )
        if verdict == "READY" and (failure_kind or gap_kind):
            _fail(
                "branch-kind-mismatch",
                f"{label}: a READY leaf carries neither failure_kind nor gap_kind",
                source,
            )
        if next_node and (failure_kind or gap_kind):
            _fail(
                "branch-kind-mismatch",
                f"{label}: an interior branch carries no failure_kind or gap_kind",
                source,
            )

        resolution_kind = failure_kind or gap_kind
        if resolution_kind and resolution_kind not in route_kinds:
            _fail(
                "leaf-resolution-kind-unmatched",
                f"{label}: resolution_kind {resolution_kind!r} matches no "
                "[[resolution_routes]] row",
                source,
            )
        if inapplicable:
            repeated = _duplicates(inapplicable)
            if repeated:
                _fail(
                    "pack-invariant-13",
                    f"{label}: renders_inapplicable contains {repeated} more than once",
                    source,
                )
            if requirement_id in inapplicable:
                _fail(
                    "pack-invariant-14",
                    f"{label}: renders_inapplicable names {requirement_id!r}, the very "
                    "evidence requirement this branch's own node just tested",
                    source,
                )

        branches.append(
            Branch(
                outcome=outcome,
                verdict=verdict,
                failure_kind=failure_kind,
                gap_kind=gap_kind,
                next_node=next_node,
                renders_inapplicable=inapplicable,
            )
        )
    return tuple(branches)


# --------------------------------------------------------------------------
# The eighteen structural invariants of ADR 0002 §3.8
# --------------------------------------------------------------------------


def _check_structural_invariants(pack: PurposePack, source: Path) -> None:
    node_ids = {node.node_id for node in pack.decision_nodes}
    requirement_ids = {item.evidence_requirement_id for item in pack.evidence_requirements}
    direction_ids = {item.direction_id for item in pack.directions}

    grain_by_requirement = {
        item.evidence_requirement_id: item.subject_grain
        for item in pack.evidence_requirements
    }

    for activity in pack.activities:
        if activity.direction_id not in direction_ids:
            _fail(
                "activity-direction-unresolved",
                f"activity {activity.activity_id!r} names direction_id "
                f"{activity.direction_id!r}, which no [[directions]] entry declares",
                source,
            )
        for requirement_id in activity.evidence_requirement_ids:
            if requirement_id not in requirement_ids:
                _fail(
                    "activity-evidence-requirement-unresolved",
                    f"activity {activity.activity_id!r} declares evidence_requirement_id "
                    f"{requirement_id!r}, which no [[evidence_requirements]] entry declares",
                    source,
                )
        element_grained = any(
            grain_by_requirement.get(requirement_id) in ("per-subject", "per-subject-pair")
            for requirement_id in activity.evidence_requirement_ids
        )
        if element_grained and not activity.subject_classes:
            _fail(
                "subject-classes-required",
                f"activity {activity.activity_id!r} reads element-grained evidence and "
                "must declare which class of object its labour is about; there is no "
                "default, and inferring the classes from which elements carry findings "
                "is exactly what this field exists to prevent",
                source,
            )
        if not element_grained and activity.subject_classes:
            _fail(
                "subject-classes-required",
                f"activity {activity.activity_id!r} reads only whole-scope evidence, so "
                "it has no element subjects for subject_classes to be about",
                source,
            )
        if activity.decision_root_node not in node_ids:
            _fail(
                "pack-invariant-01",
                f"activity {activity.activity_id!r} names decision_root_node "
                f"{activity.decision_root_node!r}, which is not an existing node_id",
                source,
            )

    for node in pack.decision_nodes:
        for branch in node.branches:
            if branch.next_node and branch.next_node not in node_ids:
                _fail(
                    "pack-invariant-02",
                    f"node {node.node_id!r} branch {branch.outcome!r} points at "
                    f"next_node {branch.next_node!r}, which is not an existing node_id",
                    source,
                )
            for requirement_id in branch.renders_inapplicable:
                if requirement_id not in requirement_ids:
                    _fail(
                        "renders-inapplicable-unresolved",
                        f"node {node.node_id!r} branch {branch.outcome!r} renders "
                        f"{requirement_id!r} inapplicable, which no evidence "
                        "requirement declares",
                        source,
                    )

    # Invariants 03, 04, 09, 13 and 14 are enforced while reading, because the
    # read cannot complete without them; the rest need the whole Pack in view.
    _invariants_05_07_10_11(pack, source)
    _invariants_06_08(pack, source)
    _invariants_12_15(pack, source)
    _invariants_16_18(pack, source)
    _check_no_orphaned_route(pack, source)


def _check_acyclic(pack: PurposePack, root: str, source: Path) -> None:
    """Invariant 05: no node reachable from ``root`` is its own ancestor."""

    stack: list[tuple[str, tuple[str, ...]]] = [(root, ())]
    while stack:
        node_id, prefix = stack.pop()
        if node_id in prefix:
            _fail(
                "pack-invariant-05",
                f"following next_node from {root!r} revisits {node_id!r}: the graph "
                "reachable from an activity's root must be acyclic",
                source,
            )
        path = prefix + (node_id,)
        for branch in pack.node(node_id).branches:
            if branch.next_node:
                stack.append((branch.next_node, path))


def _reachable(pack: PurposePack, root: str) -> set[str]:
    seen: set[str] = set()
    frontier = [root]
    while frontier:
        node_id = frontier.pop()
        if node_id in seen:
            continue
        seen.add(node_id)
        for branch in pack.node(node_id).branches:
            if branch.next_node:
                frontier.append(branch.next_node)
    return seen


def _invariants_05_07_10_11(pack: PurposePack, source: Path) -> None:
    """Acyclicity, no dangling node, one incoming edge, disjoint per-activity trees."""

    owner: dict[str, str] = {}
    for activity in pack.activities:
        _check_acyclic(pack, activity.decision_root_node, source)
        for node_id in _reachable(pack, activity.decision_root_node):
            previous = owner.get(node_id)
            if previous is not None and previous != activity.activity_id:
                _fail(
                    "pack-invariant-11",
                    f"node {node_id!r} belongs to both activity {previous!r} and "
                    f"activity {activity.activity_id!r}; an activity's tree is disjoint "
                    "from every other activity's",
                    source,
                )
            owner[node_id] = activity.activity_id

    dangling = sorted({node.node_id for node in pack.decision_nodes} - set(owner))
    if dangling:
        _fail(
            "pack-invariant-07",
            f"decision nodes {dangling} are not reachable from any activity's root",
            source,
        )

    roots = {activity.decision_root_node for activity in pack.activities}
    incoming: dict[str, int] = {node.node_id: 0 for node in pack.decision_nodes}
    for node in pack.decision_nodes:
        for branch in node.branches:
            if branch.next_node:
                incoming[branch.next_node] += 1
    for node_id, count in sorted(incoming.items()):
        if node_id in roots:
            if count:
                _fail(
                    "pack-invariant-10",
                    f"node {node_id!r} is an activity root and also receives "
                    f"{count} next_node edge(s)",
                    source,
                )
            continue
        if count != 1:
            _fail(
                "pack-invariant-10",
                f"non-root node {node_id!r} has {count} incoming next_node edges; "
                "every activity's decision_nodes must form a genuine tree",
                source,
            )


def _invariants_06_08(pack: PurposePack, source: Path) -> None:
    """A tree tests only, and tests all of, its own activity's declared evidence."""

    for activity in pack.activities:
        declared = set(activity.evidence_requirement_ids)
        tested = {
            pack.node(node_id).evidence_requirement_id
            for node_id in _reachable(pack, activity.decision_root_node)
        }
        outside = sorted(tested - declared)
        if outside:
            _fail(
                "pack-invariant-06",
                f"activity {activity.activity_id!r} reaches nodes testing {outside}, "
                "which it never declared needing",
                source,
            )
        untested = sorted(declared - tested)
        if untested:
            _fail(
                "pack-invariant-08",
                f"activity {activity.activity_id!r} declares {untested}, which no node "
                "reachable from its root tests",
                source,
            )


def _leaf_paths(pack: PurposePack, root: str) -> list[list[tuple[str, Branch]]]:
    """Every root-to-leaf path as ``[(node_id, branch), ...]``."""

    results: list[list[tuple[str, Branch]]] = []
    stack: list[tuple[str, list[tuple[str, Branch]]]] = [(root, [])]
    while stack:
        node_id, prefix = stack.pop()
        node = pack.node(node_id)
        for branch in node.branches:
            step = prefix + [(node_id, branch)]
            if branch.next_node:
                stack.append((branch.next_node, step))
            else:
                results.append(step)
    return results


def _invariants_12_15(pack: PurposePack, source: Path) -> None:
    """READY-path closure, and no retest of evidence an ancestor ruled out."""

    for activity in pack.activities:
        declared = set(activity.evidence_requirement_ids)
        for path in _leaf_paths(pack, activity.decision_root_node):
            tested: list[str] = []
            inapplicable: set[str] = set()
            for node_id, branch in path:
                requirement_id = pack.node(node_id).evidence_requirement_id
                # Invariant 15 is a prefix rule: it holds whatever verdict the
                # path eventually reaches, so it is checked as the path is
                # walked rather than only at READY leaves.
                if requirement_id in inapplicable:
                    _fail(
                        "pack-invariant-15",
                        f"activity {activity.activity_id!r}: node {node_id!r} tests "
                        f"{requirement_id!r} on a path where an ancestor branch already "
                        "rendered it inapplicable",
                        source,
                    )
                tested.append(requirement_id)
                inapplicable.update(branch.renders_inapplicable)

            final = path[-1][1]
            if final.verdict != "READY":
                continue
            tested_set = set(tested)
            overlap = sorted(tested_set & inapplicable)
            if overlap:
                _fail(
                    "pack-invariant-12",
                    f"activity {activity.activity_id!r}: on a READY path, {overlap} is "
                    "both tested and rendered inapplicable",
                    source,
                )
            union = tested_set | inapplicable
            if union != declared:
                _fail(
                    "pack-invariant-12",
                    f"activity {activity.activity_id!r}: a READY path accounts for "
                    f"{sorted(union)}, but the activity declares {sorted(declared)}",
                    source,
                )


def _invariants_16_18(pack: PurposePack, source: Path) -> None:
    """The pair grain: declared together, reachable only below its source, never a leaf."""

    by_id = {item.evidence_requirement_id: item for item in pack.evidence_requirements}

    for requirement in pack.evidence_requirements:
        paired = requirement.subject_grain == "per-subject-pair"
        if paired != (requirement.pair_source is not None):
            _fail(
                "pack-invariant-16",
                f"evidence requirement {requirement.evidence_requirement_id!r}: "
                "pair_source is declared if and only if subject_grain is 'per-subject-pair'",
                source,
            )
        if requirement.pair_source is None:
            continue

        pair_source = requirement.pair_source
        origin = by_id.get(pair_source.from_evidence_requirement_id)
        if origin is None:
            _fail(
                "pack-invariant-16",
                f"evidence requirement {requirement.evidence_requirement_id!r}: "
                f"pair_source names {pair_source.from_evidence_requirement_id!r}, which "
                "no evidence requirement declares",
                source,
            )
            return
        if pair_source.on_outcome not in origin.outcomes:
            _fail(
                "pack-invariant-16",
                f"evidence requirement {requirement.evidence_requirement_id!r}: "
                f"pair_source on_outcome {pair_source.on_outcome!r} is not one of "
                f"{list(origin.outcomes)}",
                source,
            )

        for activity in pack.activities:
            if requirement.evidence_requirement_id not in activity.evidence_requirement_ids:
                continue
            declared_ids = activity.evidence_requirement_ids
            if pair_source.from_evidence_requirement_id not in declared_ids:
                _fail(
                    "pack-invariant-16",
                    f"activity {activity.activity_id!r} declares "
                    f"{requirement.evidence_requirement_id!r} but not its pair source "
                    f"{pair_source.from_evidence_requirement_id!r}",
                    source,
                )
            _check_pair_reachability(
                pack,
                activity,
                requirement.evidence_requirement_id,
                pair_source.from_evidence_requirement_id,
                pair_source.on_outcome,
                source,
            )


def _check_pair_reachability(
    pack: PurposePack,
    activity: Activity,
    paired_requirement_id: str,
    origin_requirement_id: str,
    on_outcome: str,
    source: Path,
) -> None:
    """Invariants 17 and 18, over every path prefix of one activity's tree."""

    for path in _leaf_paths(pack, activity.decision_root_node):
        seen_source = False
        for node_id, branch in path:
            requirement_id = pack.node(node_id).evidence_requirement_id
            if requirement_id == origin_requirement_id and branch.outcome == on_outcome:
                if branch.is_leaf:
                    _fail(
                        "pack-invariant-18",
                        f"node {node_id!r} branch {on_outcome!r} names the counterparts "
                        f"{paired_requirement_id!r} keys on, and then terminates the path; "
                        "an outcome whose purpose is to name counterparts must continue "
                        "to the node that reads them",
                        source,
                    )
                seen_source = True
            if requirement_id == paired_requirement_id and not seen_source:
                _fail(
                    "pack-invariant-17",
                    f"activity {activity.activity_id!r}: node {node_id!r} reads the "
                    f"pair-grained {paired_requirement_id!r} on a path whose prefix does "
                    f"not take {origin_requirement_id!r} = {on_outcome!r}, so no "
                    "counterpart has been named",
                    source,
                )


def _check_no_orphaned_route(pack: PurposePack, source: Path) -> None:
    """Every route is used by at least one leaf.

    ADR 0002 requires the join to be total in both directions: every leaf's
    kind matches exactly one route, and every route is reached by at least one
    leaf. It does **not** require at most one leaf per route — a kind may sit
    on several leaves, sharing the identical route behind it — which is why
    this is a reachability check and not a bijection check.
    """

    used = {
        branch.resolution_kind
        for node in pack.decision_nodes
        for branch in node.branches
        if branch.resolution_kind
    }
    orphaned = sorted(
        route.resolution_kind
        for route in pack.resolution_routes
        if route.resolution_kind not in used
    )
    if orphaned:
        _fail(
            "route-orphaned",
            f"resolution_routes {orphaned} are the failure_kind or gap_kind of no branch "
            "in any of this Pack's decision trees",
            source,
        )


# --------------------------------------------------------------------------
# Discovery
# --------------------------------------------------------------------------


def discover_purpose_packs(root: Path) -> tuple[Path, ...]:
    """Find every ``pack.toml`` under ``root``, in a stable order.

    Sorted, so a Pack library is the same library however the filesystem chose
    to order its entries.
    """

    root = Path(root)
    if not root.exists():
        return ()
    return tuple(sorted(root.glob(f"*/{PACK_FILENAME}")))


def load_purpose_packs(paths: Sequence[Path]) -> tuple[PurposePack, ...]:
    """Load several Packs and check what only the whole set can show."""

    packs = tuple(load_purpose_pack(path) for path in paths)
    seen: dict[str, Path] = {}
    for pack, path in zip(packs, paths, strict=True):
        if pack.pack_id in seen:
            raise PurposePackError(
                "pack-id-duplicate",
                f"pack_id {pack.pack_id!r} is already declared by {seen[pack.pack_id]}",
                source=path,
            )
        seen[pack.pack_id] = path
    return packs
