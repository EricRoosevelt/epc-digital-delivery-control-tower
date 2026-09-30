# The replacement strings below must match the source byte for byte, so they
# are not wrapped to the line limit.
# ruff: noqa: E501
"""Round 2 edits and prototypes for ADR 0005 (2026-10-01).

Measurement only, on a disposable checkout, exactly like round 1. Round 1's
``patches.py`` is left byte-for-byte as audited; this module adds to it:

* ``EDITS2`` — four more rule edits for the P-3 question (what a title, a
  description, R-010's ``instructions`` and R-010's applicability do).
* ``O1b`` — O1 as P-3 ruled it: ``instructions`` is left out of the semantics
  digest only for the IDS checker, which hands it to IfcTester as prose; the
  completeness checker publishes it as ``expected``, so there it stays in.
* ``C`` — a prototype of the evidence carry-over comparison ADR 0005 §5.2
  designs: every cited finding is sealed with a comparison basis, and a recheck
  classifies each sealed citation into exactly one of four states. Requires O1b.

Usage, with the disposable checkout as the working directory::

    python patches_r2.py <name> [<name> ...]
"""

from __future__ import annotations

import sys
from pathlib import Path

import patches

RULES = "rules/epc-delivery"

EDITS2: dict[str, list[tuple]] = {
    "r005a-title": [
        (
            f"{RULES}/R-005A.toml",
            'title = "Duct segments need assumed EPC metadata"',
            'title = "Duct segments need the assumed EPC metadata"',
            1,
        )
    ],
    "r005a-description": [
        (
            f"{RULES}/R-005A.toml",
            'description = "Project-specific assumed EPC delivery requirement for IfcDuctSegment elements."',
            'description = "Project-specific assumed EPC delivery requirement for duct segments."',
            1,
        )
    ],
    "r010-instructions": [
        (
            f"{RULES}/R-010.toml",
            'instructions = "Carry the project\'s agreed setout references in every discipline model."',
            'instructions = "Carry the agreed setout references in every discipline model."',
            1,
        )
    ],
    "r010-applicability": [
        (
            f"{RULES}/R-010.toml",
            'name = "IFCBUILDINGELEMENTPROXY"',
            'name = "IFCWALL"',
            1,
        )
    ],
}

_O1B = [
    (
        "epc_control_tower/rule_definitions.py",
        "        values = {k: v for k, v in item.values.items() if k not in _NOT_EVALUATED}\n",
        "        dropped = _NOT_EVALUATED if rule.checker == 'ids' else set()\n"
        "        values = {k: v for k, v in item.values.items() if k not in dropped}\n",
        1,
    )
]

# A slice replacement: (path, (start marker, end marker), new text, 1) replaces
# everything from the start marker up to, not including, the end marker.
_C = [
    # --- facts: each finding carries what a comparison needs --------------
    (
        "epc_control_tower/purpose/assessment/facts.py",
        "    finding_key: str\n    element_key: str\n    requirement_key: str\n    status: str\n",
        "    finding_key: str\n    element_key: str\n    requirement_key: str\n    status: str\n"
        '    model_key: str = ""\n'
        '    semantics_digest: str = ""\n'
        '    content_digest: str = ""\n',
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/facts.py",
        "                    status=str(finding.status),\n                )\n",
        "                    status=str(finding.status),\n"
        "                    model_key=finding.model_key,\n"
        "                    semantics_digest=_semantics.get(finding.requirement_key, ''),\n"
        "                    content_digest=_finding_content_digest(finding),\n"
        "                )\n",
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/facts.py",
        "    findings = tuple(\n        sorted(\n            (\n                FindingFact(\n",
        "    _semantics = {\n"
        "        r.requirement_key: getattr(r, 'semantics_digest', '')\n"
        "        for r in bundle.ruleset.requirements\n"
        "    }\n"
        "    findings = tuple(\n        sorted(\n            (\n                FindingFact(\n",
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/facts.py",
        "def facts_from_bundle(bundle, project_id: str) -> AssessmentFacts:\n",
        "def _finding_content_digest(finding) -> str:\n"
        "    import hashlib\n\n"
        "    from ...determinism import canonical_json_document\n\n"
        "    document = {\n"
        "        'basis': 1,\n"
        "        'status': str(finding.status),\n"
        "        'expected': finding.expected,\n"
        "        'actual': finding.actual,\n"
        "        'reason': finding.reason,\n"
        "    }\n"
        "    return hashlib.sha256(canonical_json_document(document).encode('utf-8')).hexdigest()\n\n\n"
        "def facts_from_bundle(bundle, project_id: str) -> AssessmentFacts:\n",
        1,
    ),
    # --- record: the sealed basis, and a four-state carry-over row ----------
    (
        "epc_control_tower/purpose/assessment/record.py",
        "@dataclass(frozen=True, slots=True)\nclass Reading:\n",
        "@dataclass(frozen=True, slots=True)\n"
        "class CitedFinding:\n"
        "    finding_key: str\n"
        "    element_key: str\n"
        "    requirement_key: str\n"
        "    model_key: str\n"
        "    model_content_id: str\n"
        "    semantics_digest: str\n"
        "    content_digest: str\n\n"
        "    def as_document(self) -> dict[str, object]:\n"
        "        return {\n"
        "            'basis_version': 1,\n"
        "            'finding_key': self.finding_key,\n"
        "            'element_key': self.element_key,\n"
        "            'requirement_key': self.requirement_key,\n"
        "            'model_key': self.model_key,\n"
        "            'model_content_id': self.model_content_id,\n"
        "            'semantics_digest': self.semantics_digest,\n"
        "            'content_digest': self.content_digest,\n"
        "        }\n\n\n"
        "@dataclass(frozen=True, slots=True)\nclass Reading:\n",
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/record.py",
        "    finding_keys: tuple[str, ...] = ()\n",
        "    finding_keys: tuple[str, ...] = ()\n    cited_findings: tuple = ()\n",
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/record.py",
        '            document["finding_keys"] = list(self.finding_keys)\n',
        '            document["finding_keys"] = list(self.finding_keys)\n'
        "        if self.cited_findings:\n"
        '            document["cited_findings"] = [item.as_document() for item in self.cited_findings]\n',
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/record.py",
        '    sealed_content_digest: str = ""\n    current_content_digest: str = ""\n\n'
        "    @property\n    def carried(self) -> bool:\n",
        '    sealed_content_digest: str = ""\n    current_content_digest: str = ""\n'
        '    state: str = ""\n'
        '    current_citation: str = ""\n'
        '    key_changed: str = ""\n'
        "    changed_aspects: tuple = ()\n"
        '    cause: str = ""\n\n'
        "    @property\n    def carried(self) -> bool:\n",
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/record.py",
        '            "reason": self.reason,\n            "carried": self.carried,\n        }\n',
        '            "reason": self.reason,\n'
        '            "state": self.state,\n'
        "        }\n"
        "        if self.current_citation:\n"
        '            document["current_citation"] = self.current_citation\n'
        "        if self.key_changed:\n"
        '            document["key_changed"] = self.key_changed\n'
        "        if self.changed_aspects:\n"
        '            document["changed_aspects"] = list(self.changed_aspects)\n'
        "        if self.cause:\n"
        '            document["cause"] = self.cause\n',
        1,
    ),
    # --- evaluator: seal the basis beside every cited finding --------------
    (
        "epc_control_tower/purpose/assessment/evaluator.py",
        "                finding_keys=finding_keys,\n                absence=absence,\n",
        "                finding_keys=finding_keys,\n"
        "                cited_findings=_cited_findings(finding_keys, facts),\n"
        "                absence=absence,\n",
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/evaluator.py",
        "def _check_validation_backed_vocabulary(",
        "def _cited_findings(finding_keys, facts):\n"
        "    from .record import CitedFinding\n\n"
        "    cited = []\n"
        "    for key in finding_keys:\n"
        "        fact = next(f for f in facts.findings if f.finding_key == key)\n"
        "        model = facts.model(fact.model_key)\n"
        "        cited.append(\n"
        "            CitedFinding(\n"
        "                finding_key=key,\n"
        "                element_key=fact.element_key,\n"
        "                requirement_key=fact.requirement_key,\n"
        "                model_key=fact.model_key,\n"
        "                model_content_id=model.content_id if model else '',\n"
        "                semantics_digest=fact.semantics_digest,\n"
        "                content_digest=fact.content_digest,\n"
        "            )\n"
        "        )\n"
        "    return tuple(cited)\n\n\n"
        "def _check_validation_backed_vocabulary(",
        1,
    ),
    # --- recheck: the comparison ------------------------------------------
    (
        "epc_control_tower/purpose/assessment/recheck.py",
        "    carry_over = _carry_over(subscope, activity, context, facts)\n",
        "    carry_over = _carry_over(subscope, activity, context, facts, dispositions)\n",
        1,
    ),
    (
        "epc_control_tower/purpose/assessment/recheck.py",
        ("def _carry_over(\n", "def _condition_status(\n"),
        '''def _carry_over(subscope, activity, context, facts, dispositions):
    """Prototype of ADR 0005 §5.2: four states, compared on a sealed basis."""

    def origin(member):
        return member.refined_from or member.keys[0]

    present = {origin(d.member) for d in dispositions if d.disposition == "present"}
    gone = {
        origin(d.member): d.disposition
        for d in dispositions
        if d.disposition != "present"
    }

    cited_now: dict[str, set[str]] = {}
    current: dict[tuple[str, str], dict[str, object]] = {}
    for item in activity.subscopes:
        for step in item.path:
            for reading in step.readings:
                for citation in reading.cited_determinations:
                    cited_now.setdefault(citation.reference, set()).add(
                        citation.content_digest
                    )
                for cited in reading.cited_findings:
                    current.setdefault(
                        (reading.subject.keys[0], step.evidence_requirement_id), {}
                    )[cited.finding_key] = cited

    rows: list[EvidenceCarryOver] = []
    seen: set[tuple[str, str]] = set()
    for step in subscope.path:
        for reading in step.readings:
            element = reading.subject.keys[0]
            basis = {cited.finding_key: cited for cited in reading.cited_findings}
            for finding_key in reading.finding_keys:
                if ("finding", finding_key) in seen:
                    continue
                seen.add(("finding", finding_key))
                rows.append(
                    _compare_finding(
                        finding_key=finding_key,
                        sealed=basis.get(finding_key),
                        element=element,
                        evidence_requirement_id=step.evidence_requirement_id,
                        present=present,
                        gone=gone,
                        current=current,
                        facts=facts,
                    )
                )
            for citation in reading.cited_determinations:
                if ("determination", citation.reference) in seen:
                    continue
                seen.add(("determination", citation.reference))
                now = sorted(cited_now.get(citation.reference, ()))
                if not now:
                    state = "no-counterpart"
                    reason = (
                        "determination-not-cited-by-this-record"
                        if context.is_current
                        else "determination-not-attributable-to-this-context"
                    )
                elif now == [citation.content_digest]:
                    state, reason = "equivalent", "determination-same-reference-same-content"
                else:
                    state = "changed"
                    reason = "determination-content-changed-under-the-same-reference"
                rows.append(
                    EvidenceCarryOver(
                        citation=citation.reference,
                        citation_kind="determination",
                        reason=reason,
                        state=state,
                        sealed_content_digest=citation.content_digest,
                        current_content_digest=now[0] if now else "",
                    )
                )
    return tuple(sorted(rows, key=lambda item: (item.citation_kind, item.citation)))


def _compare_finding(
    *, finding_key, sealed, element, evidence_requirement_id, present, gone, current, facts
):
    def row(state, reason, **extra):
        return EvidenceCarryOver(
            citation=finding_key,
            citation_kind="finding",
            reason=reason,
            state=state,
            **extra,
        )

    if sealed is None:
        return row("not-provable", "sealed-citation-has-no-comparison-basis")
    if element not in present:
        return row(
            "not-provable",
            "subject-not-present",
            cause=gone.get(element, "not-a-member-of-the-sealed-subscope"),
        )
    candidates = [
        cited
        for cited in current.get((element, evidence_requirement_id), {}).values()
        if cited.requirement_key == sealed.requirement_key
        and cited.element_key == sealed.element_key
    ]
    if not candidates:
        in_facts = any(
            fact.element_key == sealed.element_key
            and fact.requirement_key == sealed.requirement_key
            for fact in facts.findings
        )
        return row(
            "no-counterpart",
            "counterpart-not-cited-under-the-current-binding"
            if in_facts
            else "no-counterpart-in-the-cited-run",
        )
    if len(candidates) > 1:
        return row(
            "not-provable",
            "counterpart-not-unique",
            cause=",".join(sorted(cited.finding_key for cited in candidates)),
        )
    now = candidates[0]
    if not sealed.semantics_digest or not now.semantics_digest:
        return row(
            "not-provable",
            "requirement-semantics-basis-unavailable",
            current_citation=now.finding_key,
        )
    aspects = []
    if sealed.semantics_digest != now.semantics_digest:
        aspects.append("requirement-semantics")
    if sealed.model_content_id != now.model_content_id:
        aspects.append("model-version")
    if sealed.content_digest != now.content_digest:
        aspects.append("finding-content")
    return row(
        "changed" if aspects else "equivalent",
        "finding-changed" if aspects else "finding-equivalent",
        current_citation=now.finding_key,
        key_changed="yes" if now.finding_key != finding_key else "no",
        changed_aspects=tuple(aspects),
    )


''',
        1,
    ),
]

EDITS: dict[str, list[tuple]] = {**patches.EDITS, **EDITS2}
OPTIONS: dict[str, list[tuple]] = {**patches.OPTIONS, "O1b": _O1B, "C": _C}


def apply(name: str, root: Path = Path(".")) -> list[tuple[Path, bytes]]:
    """Apply one named edit or option (``a+b`` for several); return the undo."""

    if "+" in name:
        undo: list[tuple[Path, bytes]] = []
        for part in name.split("+"):
            undo.extend(apply(part, root))
        return undo
    entries = EDITS.get(name) or OPTIONS.get(name)
    if entries is None:
        raise SystemExit(f"no such patch: {name}")
    undo = []
    for relative, old, new, count in entries:
        path = root / relative
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        if isinstance(old, tuple):
            start, end = old
            if text.count(start) != 1 or text.count(end) != 1:
                raise SystemExit(f"{name}: slice markers not unique in {relative}")
            head, rest = text.split(start, 1)
            _, tail = rest.split(end, 1)
            replaced = head + new + end + tail
        else:
            found = text.count(old)
            if found != count:
                raise SystemExit(
                    f"{name}: expected {count} occurrence(s) in {relative}, found {found}"
                )
            replaced = text.replace(old, new)
        undo.append((path, raw))
        path.write_bytes(replaced.encode("utf-8"))
    return undo


def restore(undo: list[tuple[Path, bytes]]) -> None:
    patches.restore(undo)


if __name__ == "__main__":
    for patch in sys.argv[1:]:
        apply(patch)
        print(f"applied {patch}")
