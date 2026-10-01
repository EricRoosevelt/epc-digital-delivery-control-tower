"""What a cited finding required and found, copied from the run its record cites.

A record cites a finding by key and seals a comparison basis beside it; it does
not say which rule that was, which property it asked for, or why the check
failed. Those are in the validation run, and this module copies them out of it
so a screen can say them — eight fields per finding, each exactly as the run
holds it:

``rule_id``, ``requirement_id``, ``labels``, ``citation``
    the requirement the finding was evaluated under, as that run loaded it;
``expected``, ``actual``, ``reason``, ``status``
    what the finding says.

Nothing is rewritten, translated or summarised, and nothing is judged. An empty
``actual`` stays an empty string: the run observed no value and published none.

**The source is one validation run, and it is the run the adapter's own records
were assessed against** — the shipped models under the shipped rule library
(:func:`.validated.detail_source`). It is never a rule file: explaining a record
from today's ``rules/`` would be writing history from today's rules, which is
the thing a record's sealed basis exists to prevent.

**A citation gets an entry only when all of these hold**, and otherwise gets none
— no ``null``, no placeholder:

* the record that cites it names the source run as its ``validation_run_id``;
* the source run holds a finding under that key, for the same requirement;
* the predicate the record sealed (``semantics_digest``) is the predicate of the
  requirement the source run loaded, and is not empty — an empty digest means
  "not recorded" and is never equal to anything (ADR 0005 §5.7, P-4);
* what the record sealed the finding as saying (``content_digest``) is what the
  source finding says.

So a finding that carries the fixture marker never gets an entry: it is by
construction not the output of the source run, and its record names a run nobody
published. That is one rule and not a special case — nothing here looks at a
key's prefix.

**A successor record also names findings its prior cited**, on its carry-over
rows. Those are the earlier assessment's citations, sealed against the earlier
run, so they are admitted from the *prior* record's own document under the same
four conditions — and only for the keys the successor names. The prior must be
the record the successor says it succeeds, by digest; handing over any other is a
defect and raises. A prior sealed without a comparison basis has no predicate to
compare and contributes nothing.

**Rule author metadata does not cross.** ``owner_role``, ``severity``,
``priority`` and ``stage`` say what a rule author expected of the rule; none of
them is the project's assignment, and a screen that had them would show them as
one.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass

from epc_control_tower.domain import Finding, Requirement
from epc_control_tower.purpose.assessment.facts import finding_content_digest
from epc_control_tower.purpose.assessment.record import build_assessment_digest

__all__ = ["DetailSource", "finding_details", "source_from_bundle"]


@dataclass(frozen=True, slots=True)
class DetailSource:
    """One validation run's findings and the requirements it evaluated them under."""

    validation_run_id: str
    findings: Mapping[str, Finding]
    requirements: Mapping[str, Requirement]


def source_from_bundle(bundle) -> DetailSource:
    return DetailSource(
        validation_run_id=bundle.run.validation_run_id,
        findings={finding.finding_key: finding for finding in bundle.findings},
        requirements={
            requirement.requirement_key: requirement
            for requirement in bundle.ruleset.requirements
        },
    )


def _cited(document: Mapping[str, object]) -> Iterator[Mapping[str, object]]:
    """Every finding a record's readings cite, with the basis sealed beside it."""

    for activity in document["activities"]:
        for subscope in activity["subscopes"]:
            for node in subscope["path"]:
                for reading in node["readings"]:
                    yield from reading.get("cited_findings", ())


def _admitted(
    source: DetailSource, document: Mapping[str, object]
) -> Iterator[tuple[str, dict[str, object]]]:
    if document["provenance"]["validation_run_id"] != source.validation_run_id:
        return
    for cited in _cited(document):
        finding = source.findings.get(cited["finding_key"])
        if finding is None or finding.requirement_key != cited["requirement_key"]:
            continue
        requirement = source.requirements[finding.requirement_key]
        if (
            not cited["semantics_digest"]
            or cited["semantics_digest"] != requirement.semantics_digest
        ):
            continue
        if cited["content_digest"] != finding_content_digest(finding):
            continue
        yield (
            finding.finding_key,
            {
                "rule_id": requirement.rule_id,
                "requirement_id": requirement.requirement_id,
                "labels": list(requirement.labels),
                "citation": requirement.citation,
                "expected": finding.expected,
                "actual": finding.actual,
                "reason": finding.reason,
                "status": str(finding.status),
            },
        )


def finding_details(
    source: DetailSource,
    record: Mapping[str, object],
    prior: Mapping[str, object] | None = None,
) -> dict[str, dict[str, object]]:
    """``finding_key`` → the eight fields, for every citation that may have them.

    ``record`` and ``prior`` are ``as_document()`` documents. In ``finding_key``
    order, so the same record always gives the same bytes.
    """

    details = dict(_admitted(source, record))
    if prior is not None:
        successor = record.get("successor")
        if (
            successor is None
            or build_assessment_digest(prior) != successor["prior_assessment_digest"]
        ):
            raise ValueError(
                "the prior handed over is not the record this one says it succeeds"
            )
        named = {
            row["citation"]
            for subscope in successor["subscopes"]
            for row in subscope["evidence_carry_over"]
            if row["citation_kind"] == "finding"
        }
        details.update(
            (key, entry) for key, entry in _admitted(source, prior) if key in named
        )
    return {key: details[key] for key in sorted(details)}
