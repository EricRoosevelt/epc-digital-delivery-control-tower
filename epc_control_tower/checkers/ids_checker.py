"""The built-in IDS checker.

Compiling and running an IDS document is an *implementation detail of this
checker*, not a stage of the pipeline. That distinction is the whole reason the
`Checker` protocol exists: the previous layout made "compile IDS" a step every
run passed through, which baked one rule language into the shape of the
pipeline and put a ceiling on the project at whatever IDS 1.0 can express. Here,
IDS goes in one box, and a cross-model completeness checker can go in another
without either knowing about the other.

Five behaviours of IfcTester 0.8.5 are accommodated deliberately and must not be
"tidied up":

1. Re-reading an IDS document does not restore each specification's
   ``identifier``, so rule ids are read from the raw XML instead of from the
   parsed objects.
2. The JSON report never carries a stable observed value, so ``actual`` is
   emitted empty. Empty is a true statement; a fabricated one would not be.
3. The HTML template emits trailing whitespace, which is stripped so the
   generated report survives a whitespace check.
4. A specification with zero applicable elements is reported as *passing*.
   Counting that as compliance would inflate every pass rate, so it is
   normalised to ``N/A`` and excluded from the applicable denominator.
5. Validation accumulates passing elements in ``set`` objects and stamps each
   report with ``datetime.now()``. Both are pinned before a report is written —
   see :func:`_order_deterministically` — because an artifact this repository
   publishes may not depend on set iteration order or on the wall clock.
"""

from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import MappingProxyType

import ifcopenshell
from ifctester import ids, reporter

from ..determinism import (
    atomic_write_bytes,
    canonical_json_document,
    sha256_file,
)
from ..domain import (
    Element,
    Finding,
    FindingStatus,
    Model,
    Requirement,
    RuleSet,
    Severity,
)
from ..identity import build_finding_key, build_requirement_key, build_ruleset_normalized_digest
from ..protocols import CheckContext, CheckerCapabilities, CheckerFailure, CheckOutcome

__all__ = [
    "IDS_NAMESPACE",
    "IdsChecker",
    "IdsRuleSource",
    "load_ids_rule_source",
    "load_ids_ruleset",
]

#: The IDS 1.0 XML namespace.
IDS_NAMESPACE = {"ids": "http://standards.buildingsmart.org/IDS"}

#: Facet kinds this checker evaluates, in the vocabulary
#: :class:`~..domain.Requirement` uses.
SUPPORTED_FACETS = ("attribute", "partof", "property")

_PASS_REASON = "Requirement satisfied."
_FAIL_REASON = "Requirement not satisfied."
_NOT_APPLICABLE_REASON = "No applicable elements exist in this model."


# ---------------------------------------------------------------------------
# Reading a rule set out of an IDS document
# ---------------------------------------------------------------------------


def _read_document_metadata(path: Path) -> tuple[str, dict[str, str]]:
    """Return ``(version, {specification_name: rule_id})`` from the raw XML.

    Read from the XML rather than from IfcTester's parsed objects because
    IfcTester 0.8.5 does not restore ``identifier`` when it re-reads a
    document, and ``identifier`` is what every published key is built on.
    """

    root = ET.parse(path).getroot()

    version_node = root.find("ids:info/ids:version", IDS_NAMESPACE)
    if version_node is None or not version_node.text:
        raise ValueError(f"{path.name}: IDS version is missing")

    rule_ids: dict[str, str] = {}
    seen_rule_ids: set[str] = set()
    for node in root.findall(".//ids:specification", IDS_NAMESPACE):
        name = node.get("name")
        rule_id = node.get("identifier")
        if not name or not rule_id:
            raise ValueError(
                f"{path.name}: a specification has no name or no identifier"
            )
        if name in rule_ids:
            raise ValueError(f"{path.name}: duplicate specification name {name!r}")
        if rule_id in seen_rule_ids:
            raise ValueError(f"{path.name}: duplicate specification identifier {rule_id!r}")
        rule_ids[name] = rule_id
        seen_rule_ids.add(rule_id)

    return version_node.text, rule_ids


def _facet_kind(facet: object) -> str:
    """Map an IfcTester facet class onto the requirement's facet vocabulary."""

    return type(facet).__name__.lower()


def _requirement_label(facet: object) -> str:
    """Reproduce the canonical label IfcTester puts on a reported requirement.

    Derived here rather than read back out of a validation report so that a
    rule set can be loaded — and its identity computed — without opening a
    single model. The mapping mirrors ``ifctester.reporter``; a facet kind it
    does not cover raises rather than producing a silently different key.
    """

    kind = _facet_kind(facet)
    if kind == "attribute":
        return str(facet.name)
    if kind == "property":
        return f"{facet.propertySet}.{facet.baseName}"
    if kind == "partof":
        return str(facet.relation)
    if kind == "entity":
        return "IFC Class / Predefined Type" if facet.predefinedType else "IFC Class"
    if kind == "material":
        return "Name / Category"
    if kind == "classification":
        if facet.system and facet.value:
            return "System / Reference"
        if facet.system:
            return "System"
        if facet.value:
            return "Reference"
    raise ValueError(f"Cannot label an IDS requirement of kind {kind!r}")


def _global_id_of(entity: object) -> str:
    return str(getattr(entity, "GlobalId", "") or "")


def _order_deterministically(document: object) -> None:
    """Impose a stable order on IfcTester's validation results.

    IfcTester accumulates the elements that satisfied a requirement in a
    ``set``, and the applicable elements come out of a filter that does not
    promise an order either. Iterating those directly means the generated
    report lists the same elements in a different order on every run, which is
    enough to make a published artifact irreproducible even though nothing
    about the validation changed.

    Findings do not depend on this — they are keyed and sorted downstream — but
    the JSON and HTML reports are written from these collections directly, so
    the order is pinned at the source rather than patched afterwards. Doing it
    here also means the fix holds for report shapes that only appear on larger
    models, such as the grouping the HTML reporter applies past a hundred
    elements.
    """

    for specification in document.specifications:
        specification.applicable_entities.sort(key=_global_id_of)
        for facet in specification.requirements:
            facet.passed_entities = sorted(facet.passed_entities, key=_global_id_of)
            facet.failures.sort(key=lambda failure: _global_id_of(failure["element"]))


def _as_of_stamp(as_of: str) -> str:
    """Render the logical ``as_of`` the way IfcTester renders a report date.

    The reporter stamps ``datetime.now()``. Overwriting it with the run's
    logical date is what makes the report an output of its inputs rather than
    of when somebody happened to run it.
    """

    moment = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    return moment.strftime("%Y-%m-%d %H:%M:%S")


def _severity_for_rule(rule_id: str) -> Severity:
    """Severity of a *failure* of this rule.

    IDS 1.0 has nowhere to record how badly a rule matters, so the one
    distinction this project draws — that the R-005 family states an assumed
    project requirement rather than a defect in a supplied model, and so fails
    as a warning — is derived from the rule id.

    That is a prefix match on an identifier, which is exactly the kind of thing
    that stops scaling once there are more than a handful of rules. It survives
    here only because declarative rule definitions, which carry severity as a
    field, are the next phase's work; when they land this function goes.
    """

    return Severity.WARNING if rule_id.startswith("R-005") else Severity.ERROR


@dataclass(frozen=True, slots=True)
class IdsRuleSource:
    """An IDS document, parsed once, in both of the forms this system needs.

    ``ruleset`` is checker-independent: it is what the registry routes on and
    what the validation identity derives from. ``expectations`` is the human
    statement of each requirement, which the checker copies onto every finding
    it emits.
    """

    path: Path
    version: str
    ruleset: RuleSet
    expectations: Mapping[str, str]
    rule_ids: Mapping[str, str]

    def requirement_for(self, rule_id: str, requirement_id: str) -> Requirement:
        key = build_requirement_key(rule_id, requirement_id)
        return self.ruleset.by_key(key)


def load_ids_rule_source(path: Path, *, ruleset_id: str = "ids") -> IdsRuleSource:
    """Parse an IDS document into a rule set plus the text of each requirement."""

    if not path.is_file():
        raise FileNotFoundError(f"IDS document not found: {path}")

    version, rule_ids = _read_document_metadata(path)
    document = ids.open(str(path))

    requirements: list[Requirement] = []
    expectations: dict[str, str] = {}

    for specification in document.specifications:
        rule_id = rule_ids.get(specification.name)
        if not rule_id:
            raise ValueError(
                f"{path.name}: specification {specification.name!r} has no identifier "
                "in the source XML"
            )

        seen_labels: set[str] = set()
        for facet in specification.requirements:
            requirement_id = _requirement_label(facet)
            if requirement_id in seen_labels:
                raise ValueError(
                    f"{path.name}: duplicate requirement label {requirement_id!r} in "
                    f"specification {rule_id}"
                )
            seen_labels.add(requirement_id)

            requirement_key = build_requirement_key(rule_id, requirement_id)
            requirements.append(
                Requirement(
                    requirement_key=requirement_key,
                    rule_id=rule_id,
                    requirement_id=requirement_id,
                    specification_label=f"{rule_id}: {specification.name}",
                    requirement_label=requirement_id,
                    checker=IdsChecker.id,
                    facet_kinds=(_facet_kind(facet),),
                    severity=_severity_for_rule(rule_id),
                )
            )
            expectations[requirement_key] = (
                facet.to_string("requirement", specification, facet) or requirement_id
            )

    if not requirements:
        raise ValueError(f"{path.name}: the IDS document declares no requirements")

    ruleset = RuleSet(
        ruleset_id=ruleset_id,
        version=version,
        normalized_digest=build_ruleset_normalized_digest(
            ruleset_id=ruleset_id,
            version=version,
            requirements=requirements,
        ),
        # Which file was read. Provenance only: reformatting a rule document
        # must not re-key the validation it drives, so this deliberately takes
        # no part in the identity computed just above.
        source_blob_sha256=sha256_file(path),
        requirements=tuple(requirements),
    )

    return IdsRuleSource(
        path=path,
        version=version,
        ruleset=ruleset,
        expectations=MappingProxyType(expectations),
        rule_ids=MappingProxyType(rule_ids),
    )


def load_ids_ruleset(path: Path, *, ruleset_id: str = "ids") -> RuleSet:
    """Load only the rule set from an IDS document."""

    return load_ids_rule_source(path, ruleset_id=ruleset_id).ruleset


# ---------------------------------------------------------------------------
# The checker
# ---------------------------------------------------------------------------


class IdsChecker:
    """Evaluates IDS requirements against a project's models."""

    id = "ids"

    #: Version of *this implementation*, bumped when its behaviour changes.
    #:
    #: The IfcTester release in use is deliberately not folded in. It would be
    #: defensible — a different IfcTester can produce different findings — but
    #: it would also mean the same inputs validated on two machines carried two
    #: different identities, which defeats the purpose of having one. The
    #: library version is recorded in the run manifest as provenance instead.
    version = "1.0.0"

    capabilities = CheckerCapabilities(
        facets=SUPPORTED_FACETS,
        ifc_schemas=("IFC4",),
        requires_federated_context=False,
    )

    def __init__(self, ruleset_path: Path, *, ruleset_id: str = "ids") -> None:
        self._ruleset_path = Path(ruleset_path)
        self._ruleset_id = ruleset_id
        self._source: IdsRuleSource | None = None

    # -- rule access -------------------------------------------------------

    @property
    def ruleset_path(self) -> Path:
        return self._ruleset_path

    def rule_source(self) -> IdsRuleSource:
        """Parse the IDS document once and reuse it."""

        if self._source is None:
            self._source = load_ids_rule_source(
                self._ruleset_path, ruleset_id=self._ruleset_id
            )
        return self._source

    def load_ruleset(self) -> RuleSet:
        return self.rule_source().ruleset

    # -- identity ----------------------------------------------------------

    def config_sha256(self) -> str:
        """Digest of this checker's own configuration.

        Not the hash of the IDS document: what the rules *say* already reaches
        the validation identity through the rule set's normalized digest, and
        counting it twice would only make the identity harder to reason about.

        The configuration is empty today, so this is a constant. The method
        earns its place anyway — the moment a knob is added that can change
        what the checker finds, the digest moves and so does every key derived
        from it, with nobody having to remember to wire it up.
        """

        return hashlib.sha256(
            canonical_json_document({}).encode("utf-8")
        ).hexdigest()

    # -- checking ----------------------------------------------------------

    def check(self, context: CheckContext) -> CheckOutcome:
        source = self.rule_source()
        wanted = {requirement.requirement_key for requirement in context.requirements}

        findings: list[Finding] = []
        failures: list[CheckerFailure] = []

        for model in sorted(context.models, key=lambda item: item.model_key):
            try:
                report = self._validate_model(model, context)
                findings.extend(
                    self._normalise(
                        report=report,
                        model=model,
                        context=context,
                        source=source,
                        wanted=wanted,
                    )
                )
            except Exception as exc:  # noqa: BLE001 - reported, not swallowed
                # A checker that raises must not take the run down with an
                # opaque traceback from the middle of a validation. The stage
                # still fails closed; it just fails legibly.
                failures.append(
                    CheckerFailure(
                        checker_id=self.id,
                        project_id=context.project.project_id,
                        model_key=model.model_key,
                        message=str(exc) or exc.__class__.__name__,
                        detail=exc.__class__.__name__,
                    )
                )

        return CheckOutcome(findings=tuple(findings), failures=tuple(failures))

    # -- internals ---------------------------------------------------------

    def _validate_model(self, model: Model, context: CheckContext) -> dict:
        """Run one model through IfcTester and return its report.

        The IDS document is re-opened per model on purpose: IfcTester holds
        validation state on the parsed specifications, so reusing one document
        would let the previous model's results bleed into the next one's.
        """

        ifc_path = context.raw_data_dir / model.filename
        if not ifc_path.is_file():
            raise FileNotFoundError(f"IFC file not found: {ifc_path}")

        observed = sha256_file(ifc_path)
        if observed != model.provenance.content_sha256:
            raise ValueError(
                f"IFC content hash changed for {model.filename}: expected "
                f"{model.provenance.content_sha256}, found {observed}"
            )

        document = ids.open(str(self._ruleset_path))
        opened = ifcopenshell.open(str(ifc_path))
        document.validate(opened)
        _order_deterministically(document)

        report_dir = context.reports_dir / "ids"
        stamp = _as_of_stamp(context.as_of)

        json_reporter = reporter.Json(document)
        json_reporter.report()
        json_reporter.results["date"] = stamp
        report_bytes = json.dumps(
            json_reporter.results, ensure_ascii=False, default=str
        ).encode("utf-8")
        atomic_write_bytes(report_dir / f"{model.model_key}.json", report_bytes)

        html_reporter = reporter.Html(document)
        html_reporter.report()
        html_reporter.results["date"] = stamp
        # The IfcTester template leaves trailing whitespace on many lines.
        # Strip it so the generated report passes a whitespace check, and write
        # LF explicitly so the bytes do not depend on which platform ran.
        cleaned = "\n".join(line.rstrip() for line in html_reporter.to_string().splitlines())
        atomic_write_bytes(
            report_dir / f"{model.model_key}.html", f"{cleaned}\n".encode("utf-8")
        )

        # Round-trip through JSON rather than reading the reporter's own
        # objects: the report holds live ifcopenshell entities, which only
        # become the strings a finding can carry once they are serialised.
        return json.loads(report_bytes.decode("utf-8"))

    @staticmethod
    def _specification_status(specification: Mapping[str, object]) -> FindingStatus:
        """Normalise one specification's outcome.

        IfcTester reports zero applicable elements as a pass. Reporting that as
        compliance would inflate every pass rate this project publishes, so it
        becomes its own status and leaves the applicable denominator.
        """

        total_applicable = int(specification.get("total_applicable", 0) or 0)
        if specification.get("is_skipped") or total_applicable == 0:
            return FindingStatus.NOT_APPLICABLE
        return FindingStatus.PASS if specification.get("status") else FindingStatus.FAIL

    def _normalise(
        self,
        *,
        report: Mapping[str, object],
        model: Model,
        context: CheckContext,
        source: IdsRuleSource,
        wanted: set[str],
    ) -> list[Finding]:
        elements = {
            element.global_id: element for element in context.elements_for(model.model_key)
        }
        findings: list[Finding] = []

        for specification in report["specifications"]:
            name = specification["name"]
            rule_id = source.rule_ids.get(name)
            if not rule_id:
                raise ValueError(f"Specification name not found in the IDS XML: {name}")

            requirements = specification.get("requirements") or []
            status = self._specification_status(specification)

            if status is FindingStatus.NOT_APPLICABLE:
                for reported in requirements:
                    requirement = source.requirement_for(rule_id, reported["label"])
                    if requirement.requirement_key not in wanted:
                        continue
                    findings.append(
                        self._finding(
                            context=context,
                            model=model,
                            requirement=requirement,
                            source=source,
                            element=None,
                            status=FindingStatus.NOT_APPLICABLE,
                            reason=_NOT_APPLICABLE_REASON,
                        )
                    )
                continue

            for reported in requirements:
                requirement = source.requirement_for(rule_id, reported["label"])
                passed = reported.get("passed_entities") or []
                failed = reported.get("failed_entities") or []
                total_applicable = int(reported.get("total_applicable", 0) or 0)
                if len(passed) + len(failed) != total_applicable:
                    raise ValueError(
                        "Requirement entity counts do not reconcile: "
                        f"{rule_id} {requirement.requirement_id}"
                    )
                if requirement.requirement_key not in wanted:
                    continue

                for entity in passed:
                    findings.append(
                        self._finding(
                            context=context,
                            model=model,
                            requirement=requirement,
                            source=source,
                            element=self._element_for(entity, elements, model),
                            status=FindingStatus.PASS,
                            reason=_PASS_REASON,
                        )
                    )
                for entity in failed:
                    findings.append(
                        self._finding(
                            context=context,
                            model=model,
                            requirement=requirement,
                            source=source,
                            element=self._element_for(entity, elements, model),
                            status=FindingStatus.FAIL,
                            reason=str(entity.get("reason") or _FAIL_REASON),
                        )
                    )

        return findings

    @staticmethod
    def _element_for(
        entity: Mapping[str, object],
        elements: Mapping[str, Element],
        model: Model,
    ) -> Element:
        global_id = entity.get("global_id")
        if not global_id:
            raise ValueError("A non-N/A finding has no GlobalId")
        element = elements.get(str(global_id))
        if element is None:
            raise ValueError(
                f"Validation element not found in the inventory: "
                f"({model.model_key}, {global_id})"
            )
        return element

    def _finding(
        self,
        *,
        context: CheckContext,
        model: Model,
        requirement: Requirement,
        source: IdsRuleSource,
        element: Element | None,
        status: FindingStatus,
        reason: str,
    ) -> Finding:
        element_key = element.element_key if element is not None else ""
        severity = (
            requirement.severity if status is FindingStatus.FAIL else Severity.INFO
        )
        return Finding(
            finding_key=build_finding_key(
                validation_run_id=context.validation_run_id,
                model_key=model.model_key,
                requirement_key=requirement.requirement_key,
                element_key=element_key,
            ),
            validation_run_id=context.validation_run_id,
            project_id=context.project.project_id,
            model_key=model.model_key,
            element_key=element_key,
            requirement_key=requirement.requirement_key,
            status=status,
            severity=severity,
            is_applicable=status is not FindingStatus.NOT_APPLICABLE,
            is_issue=status is FindingStatus.FAIL,
            expected=source.expectations[requirement.requirement_key],
            # IfcTester does not stably report the value it observed, and an
            # invented one would be worse than none. Empty is a statement.
            actual="",
            reason=reason,
        )
