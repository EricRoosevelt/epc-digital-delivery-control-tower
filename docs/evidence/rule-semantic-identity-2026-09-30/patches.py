# The replacement strings below must match the source byte for byte, so they
# are not wrapped to the line limit.
# ruff: noqa: E501
"""Exact-string edits for the rule-semantic-identity measurements (ADR 0005).

Measurement only. Every entry is applied to a *disposable* checkout by exact
string replacement, with the number of occurrences asserted, and the checkout is
restored with ``git checkout -- . && git clean -fdq`` between scenarios.

Two kinds of entry:

* ``EDITS`` change one rule file (or the rule set header). They are the inputs
  whose effect is being measured; nobody proposes making any of them.
* ``OPTIONS`` are throwaway prototypes of the fixes ADR 0005 compares. They
  exist so an option can be run instead of argued, and none of them is the
  implementation.

Usage, with the disposable checkout as the working directory::

    python patches.py <name> [<name> ...]
"""

from __future__ import annotations

import sys
from pathlib import Path

RULES = "rules/epc-delivery"

#: name -> [(path, old, new, expected occurrences)]
EDITS: dict[str, list[tuple[str, str, str, int]]] = {
    # The technical director's four measured facet edits.
    "r002-datatype": [
        (f"{RULES}/R-002.toml", 'dataType = "IFCBOOLEAN"', 'dataType = "IFCLABEL"', 1)
    ],
    "r001-cardinality": [
        (f"{RULES}/R-001.toml", 'cardinality = "required"', 'cardinality = "optional"', 1)
    ],
    "r006-entity": [
        (
            f"{RULES}/R-006.toml",
            '[[applicability]]\nfacet = "entity"\nname = "IFCWALL"',
            '[[applicability]]\nfacet = "entity"\nname = "IFCSLAB"',
            1,
        )
    ],
    "r010-pattern": [
        (
            f"{RULES}/R-010.toml",
            'name_pattern = "^(origin|geo-reference)$"',
            'name_pattern = "^(origin)$"',
            1,
        )
    ],
    # The two edits the Purpose reproduction drives. R-005A is the rule
    # pcert-sample's Overlay binds to asset-identity.
    "r005a-optional": [
        (f"{RULES}/R-005A.toml", 'cardinality = "required"', 'cardinality = "optional"', 2)
    ],
    "r005a-datatype": [
        (f"{RULES}/R-005A.toml", 'dataType = "IFCLABEL"', 'dataType = "IFCTEXT"', 2)
    ],
    # Controls.
    "r005a-instructions": [
        (
            f"{RULES}/R-005A.toml",
            'instructions = "Provide the project-assumed EPC asset tag."',
            'instructions = "Provide the project-assumed EPC asset tag, as agreed."',
            1,
        )
    ],
    "r005a-reformat": [
        (
            f"{RULES}/R-005A.toml",
            '[[applicability]]\nfacet = "entity"\nname = "IFCDUCTSEGMENT"',
            '[[applicability]]\n# reordered, no meaning changed\nname = "IFCDUCTSEGMENT"\n'
            'facet    =    "entity"',
            1,
        )
    ],
    "version-2.3": [(f"{RULES}/ruleset.toml", 'version = "2.2"', 'version = "2.3"', 1)],
}


#: Option 1 — every requirement carries a digest of what it evaluates, and the
#: normalized digest covers it. Measured first as a rule-set-level field, which
#: ``validate_bundle`` refused: it recomputes the digest from the bundle's own
#: ``Requirement`` objects, so the semantics have to live on the requirement.
#: The field is empty for a requirement loaded from an ``.ids`` document and is
#: then left out of the digest, so the frozen legacy rule set's digest is not
#: touched.
_O1_IDENTITY = [
    (
        "epc_control_tower/domain.py",
        "    labels: tuple[str, ...] = ()\n\n    def __post_init__(self) -> None:",
        "    labels: tuple[str, ...] = ()\n"
        '    semantics_digest: str = ""\n\n    def __post_init__(self) -> None:',
        1,
    ),
    (
        "epc_control_tower/identity.py",
        '                "labels": list(requirement.labels),\n            }\n',
        '                "labels": list(requirement.labels),\n'
        "                **(\n"
        '                    {"semantics_digest": requirement.semantics_digest}\n'
        "                    if requirement.semantics_digest\n"
        "                    else {}\n"
        "                ),\n"
        "            }\n",
        1,
    ),
    (
        "epc_control_tower/rule_definitions.py",
        "                    labels=rule.labels,\n                )\n            )\n"
        "            expectations[key] = (",
        "                    labels=rule.labels,\n"
        "                    semantics_digest=_semantics_digest(rule, facet),\n"
        "                )\n            )\n"
        "            expectations[key] = (",
        1,
    ),
    (
        "epc_control_tower/rule_definitions.py",
        "                labels=rule.labels,\n            )\n        )\n    return built\n",
        "                labels=rule.labels,\n"
        "                semantics_digest=_semantics_digest(rule, facet),\n"
        "            )\n        )\n    return built\n\n\n"
        "_NOT_EVALUATED = {'instructions'}\n\n\n"
        "def _semantics_digest(rule, own):\n"
        "    import hashlib\n"
        "    import json\n\n"
        "    def facet(item):\n"
        "        values = {k: v for k, v in item.values.items() if k not in _NOT_EVALUATED}\n"
        "        return {'facet': item.kind, **values}\n\n"
        "    document = {\n"
        "        'derivation': 2,\n"
        "        'rule_id': rule.rule_id,\n"
        "        'checker': rule.checker,\n"
        "        'ifc_version': sorted(rule.ifc_version),\n"
        "        'applicability': sorted(\n"
        "            json.dumps(facet(i), sort_keys=True) for i in rule.applicability\n"
        "        ),\n"
        "        'requirement': facet(own),\n"
        "    }\n"
        "    return hashlib.sha256(\n"
        "        json.dumps(document, sort_keys=True, separators=(',', ':')).encode('utf-8')\n"
        "    ).hexdigest()\n",
        1,
    ),
]

#: Option 1 variant — the same, with ``instructions`` counted as semantics.
_O1_WITH_INSTRUCTIONS = [
    (
        "epc_control_tower/rule_definitions.py",
        "_NOT_EVALUATED = {'instructions'}",
        "_NOT_EVALUATED = set()",
        1,
    )
]

#: Option 3 — a content digest beside every cited finding_key, compared on
#: recheck, the way PR #7 did for determinations. The digest is over what the
#: finding *says* (O3a): model, element, requirement, status, expected, actual,
#: reason. No published identity moves.
_O3 = [
    (
        "epc_control_tower/purpose/assessment/facts.py",
        "    finding_key: str\n    element_key: str\n    requirement_key: str\n    status: str\n",
        "    finding_key: str\n    element_key: str\n    requirement_key: str\n    status: str\n"
        '    content_digest: str = ""\n',
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/facts.py",
        "                    status=str(finding.status),\n                )\n",
        "                    status=str(finding.status),\n"
        "                    content_digest=_finding_digest(finding),\n                )\n",
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/facts.py",
        "def facts_from_bundle(bundle, project_id: str) -> AssessmentFacts:\n",
        "def _finding_digest(finding) -> str:\n"
        "    import hashlib\n\n"
        "    from ...determinism import canonical_json_document\n\n"
        "    document = {\n"
        "        'model_key': finding.model_key,\n"
        "        'element_key': finding.element_key,\n"
        "        'requirement_key': finding.requirement_key,\n"
        "        'status': str(finding.status),\n"
        "        'expected': finding.expected,\n"
        "        'actual': finding.actual,\n"
        "        'reason': finding.reason,\n"
        "    }\n"
        "    return hashlib.sha256(canonical_json_document(document).encode('utf-8')).hexdigest()\n\n\n"
        "def facts_from_bundle(bundle, project_id: str) -> AssessmentFacts:\n",
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/record.py",
        "    finding_keys: tuple[str, ...] = ()\n",
        "    finding_keys: tuple[str, ...] = ()\n    finding_digests: tuple[str, ...] = ()\n",
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/record.py",
        '            document["finding_keys"] = list(self.finding_keys)\n',
        '            document["finding_keys"] = list(self.finding_keys)\n'
        "        if self.finding_digests:\n"
        '            document["finding_digests"] = list(self.finding_digests)\n',
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/evaluator.py",
        "                finding_keys=finding_keys,\n                absence=absence,\n",
        "                finding_keys=finding_keys,\n"
        "                finding_digests=tuple(\n"
        "                    next(f.content_digest for f in facts.findings if f.finding_key == k)\n"
        "                    for k in finding_keys\n"
        "                ),\n"
        "                absence=absence,\n",
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/recheck.py",
        "            for finding_key in reading.finding_keys:\n"
        '                if ("finding", finding_key) in seen:\n'
        "                    continue\n"
        '                seen.add(("finding", finding_key))\n'
        "                present = any(\n"
        "                    fact.finding_key == finding_key for fact in facts.findings\n"
        "                )\n"
        "                rows.append(\n"
        "                    EvidenceCarryOver(\n"
        "                        citation=finding_key,\n"
        '                        citation_kind="finding",\n'
        "                        reason=(\n"
        '                            "carried" if present else "finding-absent-from-the-cited-run"\n'
        "                        ),\n"
        "                    )\n"
        "                )\n",
        "            for finding_key, sealed in zip(\n"
        "                reading.finding_keys, reading.finding_digests, strict=True\n"
        "            ):\n"
        '                if ("finding", finding_key) in seen:\n'
        "                    continue\n"
        '                seen.add(("finding", finding_key))\n'
        "                now = [\n"
        "                    fact.content_digest for fact in facts.findings\n"
        "                    if fact.finding_key == finding_key\n"
        "                ]\n"
        "                if not now:\n"
        '                    reason = "finding-absent-from-the-cited-run"\n'
        "                elif now == [sealed]:\n"
        '                    reason = "carried"\n'
        "                else:\n"
        '                    reason = "finding-content-changed-under-the-same-key"\n'
        "                rows.append(\n"
        "                    EvidenceCarryOver(\n"
        "                        citation=finding_key,\n"
        '                        citation_kind="finding",\n'
        "                        reason=reason,\n"
        "                        sealed_content_digest=sealed,\n"
        '                        current_content_digest=now[0] if now else "",\n'
        "                    )\n"
        "                )\n",
        1,
    ),
]

OPTIONS: dict[str, list[tuple[str, str, str, int]]] = {
    "O1": _O1_IDENTITY,
    "O1-instructions": _O1_WITH_INSTRUCTIONS,
    "O3": _O3,
}


def apply(name: str, root: Path = Path(".")) -> list[tuple[Path, bytes]]:
    """Apply one named edit or option; return what to write back to undo it.

    ``a+b`` applies ``a`` and then ``b``.
    """

    if "+" in name:
        undo: list[tuple[Path, bytes]] = []
        for part in name.split("+"):
            undo.extend(apply(part, root))
        return undo
    entries = EDITS.get(name) or OPTIONS.get(name)
    if entries is None:
        raise SystemExit(f"no such patch: {name}")
    undo: list[tuple[Path, bytes]] = []
    for relative, old, new, count in entries:
        path = root / relative
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        found = text.count(old)
        if found != count:
            raise SystemExit(
                f"{name}: expected {count} occurrence(s) in {relative}, found {found}"
            )
        undo.append((path, raw))
        path.write_bytes(text.replace(old, new).encode("utf-8"))
    return undo


def restore(undo: list[tuple[Path, bytes]]) -> None:
    for path, raw in reversed(undo):
        path.write_bytes(raw)


if __name__ == "__main__":
    for patch in sys.argv[1:]:
        apply(patch)
        print(f"applied {patch}")
