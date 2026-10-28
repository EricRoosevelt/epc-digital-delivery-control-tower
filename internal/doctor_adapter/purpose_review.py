"""Enterprise evidence projected into the existing, sealed purpose evaluator.

No geometry, canonical data, status override or risk authorisation is used here.
One compiled requirement becomes one activity so partial execution cannot satisfy
a group. Human evidence is attributable user input, never a signature.
"""

from __future__ import annotations

import copy
from collections import Counter
from collections.abc import Mapping
from dataclasses import fields
import hashlib
import json

from epc_control_tower.domain import ComponentFingerprint
from epc_control_tower.purpose import (
    AcceptedEvidenceMethod,
    Activity,
    AssessedScope,
    AssessmentFacts,
    AssessmentRequest,
    Branch,
    DecisionNode,
    Determination,
    DeterminedAgainst,
    Direction,
    EvidenceRequirement,
    HandoverEvent,
    ModelVersion,
    ModelVersionContext,
    OverlayPackRef,
    PackBinding,
    ProjectOverlay,
    PurposeAssessmentError,
    PurposePack,
    ResolutionRoute,
    TeamMapping,
    assess_purpose,
    compose_purpose_inputs,
    recheck_purpose,
)
from epc_control_tower.purpose.assessment import record as records
from epc_control_tower.purpose.assessment.facts import (
    ElementFact,
    FindingFact,
    ModelVersionFact,
)
from .review import GUID_PATTERN


def _digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        ).encode("utf8")
    ).hexdigest()


def _subject(value):
    return records.Subject(tuple(value["keys"]), value.get("refined_from", ""))


def _decode(cls, value):
    """Whitelist-only JSON decoding; derived document fields must roundtrip exactly."""
    data = dict(value)
    if cls is records.CitedFinding:
        checker = data.pop("checker")
        data.update(
            checker_id=checker["id"],
            checker_version=checker["version"],
            checker_config_sha256=checker["config_sha256"],
        )
    if cls is records.Reading:
        data["subject"] = _subject(data["subject"])
        for name, kind in (
            ("cited_findings", records.CitedFinding),
            ("cited_determinations", records.CitedDetermination),
        ):
            data[name] = tuple(_decode(kind, x) for x in data.get(name, ()))
    if cls is records.PathStep:
        data["readings"] = tuple(_decode(records.Reading, x) for x in data["readings"])
    if cls is records.SubscopeResult:
        data["members"] = tuple(_subject(x) for x in data["members"])
        data["path"] = tuple(_decode(records.PathStep, x) for x in data["path"])
        for name, kind in (
            ("route", records.ResolvedRoute),
            ("assignment", records.ResolvingAssignment),
        ):
            if name in data:
                data[name] = _decode(kind, data[name])
    if cls is records.ActivityResult:
        data.pop("partition_is_empty")
        data["subscopes"] = tuple(_decode(records.SubscopeResult, x) for x in data["subscopes"])
        data["out_of_subject_class"] = tuple(
            _decode(records.OutOfClassKey, x) for x in data["out_of_subject_class"]
        )
    if cls is records.MemberDisposition:
        data["member"] = _subject(data["member"])
    if cls is records.RecheckOutcome:
        data["prior_members"] = tuple(_subject(x) for x in data["prior_members"])
        data["dispositions"] = tuple(
            _decode(records.MemberDisposition, x) for x in data["dispositions"]
        )
        data["carry_over"] = tuple(
            _decode(records.EvidenceCarryOver, x) for x in data.pop("evidence_carry_over")
        )
    if cls is records.SuccessorSection:
        context = data.pop("model_version_context_comparison")
        data["context"] = records.ContextComparison(
            **{
                k: (context[k]["model_key"], context[k]["content_id"])
                for k in ("prior_producing", "producing", "prior_consuming", "consuming")
            }
        )
        data["outcomes"] = tuple(
            _decode(records.RecheckOutcome, x) for x in data.pop("subscopes")
        )
    allowed = {f.name for f in fields(cls)}
    if set(data) - allowed:
        raise ValueError("Unknown sealed record fields")
    for name, item in data.items():
        if isinstance(item, list):
            data[name] = tuple(item)
    return cls(**data)


def restore_record(document: Mapping, assessment_digest: str) -> records.AssessmentRecord:
    """Reconstruct only known types and verify the original document and its seal."""
    try:
        if records.build_assessment_digest(document) != assessment_digest:
            raise ValueError("Assessment seal mismatch")
        request = dict(document["request"])
        schema = request.pop("pack_schema_version")
        scope = AssessedScope(**{k: tuple(v) for k, v in request.pop("assessed_scope").items()})
        raw_context = request.pop("model_version_context")
        context = ModelVersionContext(
            ModelVersion(**raw_context["producing"]),
            ModelVersion(**raw_context["consuming"]),
            HandoverEvent(**raw_context["handover"]),
        )
        req = AssessmentRequest(**request, assessed_scope=scope, model_version_context=context)
        provenance = dict(document["provenance"])
        record = records.AssessmentRecord(
            request=req,
            pack_schema_version=schema,
            **provenance,
            activities=tuple(
                _decode(records.ActivityResult, x) for x in document["activities"]
            ),
            assessment_digest=assessment_digest,
            successor=_decode(records.SuccessorSection, document["successor"])
            if "successor" in document
            else None,
        )
        if record.as_document() != document:
            raise ValueError("Assessment seal document does not roundtrip")
        return record
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("Invalid sealed assessment record") from error


def _matches(element, classes):
    return bool(set(classes) & {element["ifc_class"], *element.get("class_ancestors", ())})


def _scope_keys(scope, elements):
    kind = scope.get("kind")
    if kind == "all":
        return sorted(e["element_key"] for e in elements)
    if kind == "classes":
        return sorted(
            e["element_key"] for e in elements if _matches(e, scope.get("classes", ()))
        )
    if kind == "elements":
        keys = sorted(set(scope.get("element_keys", ())))
        if set(keys) - {e["element_key"] for e in elements}:
            raise ValueError("Declared scope contains an absent element")
        return keys
    raise ValueError("Scope kind must be all, classes or elements")


def _consumer_context(consumer, project_id):
    revision, report = consumer["revision"], consumer["report"]
    if revision.get("project_id", project_id) != project_id:
        raise ValueError("Counterpart belongs to another project")
    key = revision["model_id"]
    models = report.get("models", ())
    content = report.get("source", {}).get("sha256")
    if not content and len(models) == 1:
        content = models[0].get("sha256") or models[0].get("content_id")
    if not content:
        raise ValueError("Counterpart requires one exact model content hash")
    counts = Counter(e.get("global_id", "") for e in report["elements"])
    for element in report["elements"]:
        guid = element.get("global_id", "")
        if (
            not GUID_PATTERN.fullmatch(guid)
            or counts[guid] != 1
            or element.get("global_id_count", 1) != 1
        ):
            raise ValueError("Counterpart contains invalid or ambiguous object identities")
    elements = tuple(
        ElementFact(f"{key}::{e.get('global_id') or 'step-' + str(i)}", key, e["ifc_class"])
        for i, e in enumerate(report["elements"])
    )
    return ModelVersion(key, content), elements


def _definitions(package, evaluation, purpose):
    wanted = set(purpose["required_rule_ids"])
    checks = {c["requirement_key"]: dict(c) for c in package.checks if c["rule_id"] in wanted}
    checks.update(
        {c["requirement_key"]: dict(c) for c in evaluation["checks"] if c["rule_id"] in wanted}
    )
    rows = []
    preview = package.preview() if hasattr(package, "preview") else {}
    suggestions = {r["rule_id"]: r.get("hypotheses", ()) for r in preview.get("rules", ())}
    for key, check in sorted(checks.items()):
        rows.append(
            {
                **check,
                "evidence_id": "check-" + _digest(key)[:16],
                "execution": "machine",
                "acceptance": check.get("expected", ""),
                "hypotheses": suggestions.get(check["rule_id"], ()),
            }
        )
    covered = {c["rule_id"] for c in checks.values()}
    for rule_id in sorted(wanted - covered):
        rows.append(
            {
                "requirement_key": "missing-" + rule_id,
                "rule_id": rule_id,
                "evidence_id": "missing-" + _digest(rule_id)[:16],
                "title": rule_id,
                "execution": "unsupported",
                "support": "unsupported",
                "reason": "No compiled requirement is available for this required rule",
            }
        )
    for evidence in purpose.get("evidence_requirements", ()):
        rows.append({**evidence, "requirement_key": "evidence-" + evidence["evidence_id"]})
    if not rows:
        rows.append(
            {
                "evidence_id": "unconfigured",
                "requirement_key": "unconfigured",
                "execution": "unsupported",
                "title": "No executable evidence declared",
                "reason": "No requirement can establish this purpose",
            }
        )
    return rows


def _next_actions(row, failed, coverage=None):
    if row["execution"] == "manual":
        method = row["method_id"]
        return (
            f"Use the accepted method {method} to collect evidence. Record the recorder, "
            "evidence reference, basis and outcome, then run a new assessment.",
            f"按已接受的方法 {method} 收集证据，"
            "记录录入人、证据引用、判断依据及结论，再发起新评估。",
        )
    if (
        row["execution"] == "unsupported"
        or row.get("support") == "unsupported"
        or (coverage or {}).get("support") == "unsupported"
    ):
        return (
            "Provide a supported rule or executor for this requirement and rerun the "
            "assessment. Record the changed checking basis; a rule or engine change "
            "is not proof of a model repair.",
            "为本要求补充受支持的规则或执行器后重检；记录检查依据变化，"
            "不能将规则或执行器变更称为模型修复。",
        )
    if failed:
        return (
            "Compare expected and actual with the source object and its assigned type. "
            "Correct the source against the verified requirement, re-export IFC to a new "
            "revision in the same model slot, and rerun this check.",
            "对照本检查的真实要求和实际值核对源构件及其关联类型，按已核实的要求修正源模型；"
            "重新导出 IFC，在同一模型槽保存新修订后重检。",
        )
    return (
        "Check rule applicability and the declared object scope. Supply or repair "
        "executable checks for uncovered objects, then reassess the complete scope.",
        "核对规则适用条件与声明范围，为未覆盖对象补充可执行检查后重新评估完整范围。",
    )


def _configuration(package, purpose, rows, elements, evaluation, team):
    evidence_ids = [row["evidence_id"] for row in rows]
    if len(evidence_ids) != len(set(evidence_ids)):
        raise ValueError(
            "Duplicate evidence identifiers would shadow required purpose evidence"
        )
    pack_id = package.manifest["package_id"] + "--" + purpose["purpose_id"]
    version = package.manifest["version"]
    ruleset = evaluation["ruleset"]
    classes = tuple(
        sorted(
            set(purpose["subject_classes"])
            | {e["ifc_class"] for e in elements if _matches(e, purpose["subject_classes"])}
        )
    )
    requirements, activities, nodes, routes, methods = [], [], [], [], []
    coverage = {r["requirement_key"]: r for r in evaluation.get("coverage", ())}
    for row in rows:
        key = row["evidence_id"]
        manual = row["execution"] == "manual"
        outcomes = (
            ("unmet", "not-yet-confirmed", "confirmed")
            if manual
            else ("unmet", "not-yet-evaluated", "satisfied")
        )
        requirements.append(
            EvidenceRequirement(
                key,
                row.get("title", key),
                "assessment" if manual else "pack",
                "per-subject",
                row.get("acceptance", row.get("expected", "")),
                outcomes,
                None
                if manual
                else PackBinding(
                    ruleset["ruleset_id"], ruleset["version"], (row["requirement_key"],)
                ),
            )
        )
        if manual:
            methods.append(
                AcceptedEvidenceMethod(
                    pack_id,
                    key,
                    row["method_id"],
                    row["method_description"],
                    "project-decision",
                )
            )
        activities.append(
            Activity(key, row.get("title", key), "delivery", classes, (key,), key)
        )
        nodes.append(
            DecisionNode(
                key,
                key,
                (
                    Branch(outcomes[0], "BLOCKED", failure_kind=key + "-unmet"),
                    Branch(outcomes[1], "UNKNOWN", gap_kind=key + "-unknown"),
                    Branch(outcomes[2], "READY"),
                ),
            )
        )
        for suffix in ("unmet", "unknown"):
            routes.append(
                ResolutionRoute(
                    key + "-" + suffix,
                    "responsible-reviewer",
                    (),
                    _next_actions(row, suffix == "unmet", coverage.get(row["requirement_key"]))[
                        0
                    ],
                    outcomes[2],
                )
            )
    pack = PurposePack(
        pack_id,
        "1",
        version,
        "project-confirmed",
        (),
        (Direction("delivery", purpose["from_role"], purpose["to_role"]),),
        tuple(requirements),
        tuple(activities),
        tuple(routes),
        tuple(nodes),
    )
    overlay = ProjectOverlay(
        packs=(OverlayPackRef(pack_id, version),),
        accepted_evidence_methods=tuple(methods),
        team_mapping=(TeamMapping("responsible-reviewer", team, "project-decision"),),
    )
    keys = frozenset(r["requirement_key"] for r in rows if r["execution"] != "manual")
    return pack, overlay, {(ruleset["ruleset_id"], ruleset["version"]): keys}


def _facts(evaluation, project_id, rows, context, consumer_elements):
    by_key = {r["requirement_key"]: r for r in rows}
    coverage = {c["requirement_key"]: c for c in evaluation.get("coverage", ())}
    identities = {
        e["element_key"]: e.get("identity_comparable", False) for e in evaluation["elements"]
    }
    findings = []
    for finding in evaluation["findings"]:
        check = by_key.get(finding["requirement_key"])
        cov = coverage.get(finding["requirement_key"], {})
        if (
            not check
            or check["execution"] != "machine"
            or check.get("support") != "supported"
            or cov.get("support") != "supported"
            or not cov.get("evaluated")
            or not identities.get(finding["element_key"])
        ):
            continue
        basis = (
            finding.get("checker") or check.get("checker") or evaluation["ruleset"]["checker"]
        )
        findings.append(
            FindingFact(
                finding["finding_key"],
                finding["element_key"],
                finding["requirement_key"],
                finding["status"],
                finding["model_key"],
                check.get("semantics_digest", ""),
                _digest(
                    {k: finding.get(k) for k in ("status", "expected", "actual", "reason")}
                ),
                ComponentFingerprint(
                    basis.get("component_id", basis.get("id", "ids")),
                    basis["version"],
                    basis.get("config_sha256", ""),
                ),
            )
        )
    models = [ModelVersionFact(m["model_key"], m["content_id"]) for m in evaluation["models"]]
    if context.consuming.model_key not in {m.model_key for m in models}:
        models.append(
            ModelVersionFact(context.consuming.model_key, context.consuming.content_id)
        )
    return AssessmentFacts(
        project_id,
        _digest(evaluation),
        evaluation["ruleset"]["ruleset_id"],
        evaluation["ruleset"]["version"],
        tuple(
            ElementFact(e["element_key"], e["model_key"], e["ifc_class"])
            for e in evaluation["elements"]
        )
        + consumer_elements,
        tuple(findings),
        {},
        tuple(models),
    )


def _determinations(offered, rows, context_digest, context, selected):
    manual = {r["evidence_id"]: r for r in rows if r["execution"] == "manual"}
    accepted, declined = [], []
    against = DeterminedAgainst(
        context.producing.model_key,
        context.producing.content_id,
        context.consuming.model_key,
        context.consuming.content_id,
    )
    for raw in offered:
        row = manual.get(raw.get("evidence_id"))
        subject = tuple(raw.get("subject_keys", ()))
        if (
            not row
            or raw.get("context_digest") != context_digest
            or not subject
            or not set(subject) <= set(selected)
        ):
            declined.append(
                {
                    "reference": raw.get("reference", ""),
                    "reason": "Evidence does not name this method, "
                    "model revision and declared scope",
                }
            )
            continue
        accepted.append(
            Determination(
                raw.get("reference", ""),
                row["evidence_id"],
                raw.get("method_id", ""),
                raw.get("determiner", raw.get("recorder", "")),
                raw.get("basis", ""),
                raw.get("outcome", ""),
                subject,
                determined_against=against,
            )
        )
    return tuple(accepted), declined


def _states(document):
    return {
        (a["activity_ref"].split("::", 1)[1], key): s["verdict"]
        for a in document.get("activities", ())
        for s in a["subscopes"]
        for member in s["members"]
        for key in member["keys"]
    }


def _changes(prior, basis, elements, selected, purpose, document):
    result = {"basis_changes": [], "outcomes": [], "comparable": bool(prior)}
    if not prior:
        return result
    result["prior_run_id"] = prior.get("run_id")
    old_basis = prior.get("comparison_basis", {})
    for kind in ("model", "rules", "scope", "human", "engine", "configuration"):
        if old_basis.get(kind) != basis[kind]:
            result["basis_changes"].append(
                {
                    "kind": kind,
                    "before": old_basis.get(kind),
                    "after": basis[kind],
                    "explanation": "This assessment basis changed; "
                    "it is not evidence of a model repair.",
                }
            )
    incompatible = any(
        x["kind"] in ("rules", "configuration", "engine") for x in result["basis_changes"]
    )
    slots_changed = [m["model_key"] for m in old_basis.get("model", ())] != [
        m["model_key"] for m in basis["model"]
    ]
    if slots_changed:
        result["basis_changes"].append(
            {
                "kind": "model_slot_changed",
                "before": [m["model_key"] for m in old_basis.get("model", ())],
                "after": [m["model_key"] for m in basis["model"]],
                "explanation": "A different model slot asks a new question; "
                "old objects are not proven deleted.",
            }
        )
    current_classes = {e["element_key"]: e["ifc_class"] for e in elements}
    changed_classes = {
        key
        for key, before in old_basis.get("classes", {}).items()
        if key in current_classes and current_classes[key] != before
    }
    result["comparable"] = not incompatible and not slots_changed and not changed_classes
    if any(
        not e.get("identity_comparable", False)
        for e in elements
        if e["element_key"] in selected and _matches(e, purpose["subject_classes"])
    ):
        result["comparable"] = False
    if not all(old_basis.get("identities", {}).values()):
        result["comparable"] = False
    inventory = {e["element_key"]: e for e in elements}
    current = _states(document or {})
    manual_ids = {
        r["evidence_id"]
        for r in purpose.get("evidence_requirements", ())
        if r["execution"] == "manual"
    }
    for (evidence, key), before in _states(prior.get("record") or {}).items():
        element = inventory.get(key)
        after = current.get((evidence, key))
        if slots_changed or old_basis.get("identities", {}).get(key) is False:
            change = "not_comparable"
        elif not element:
            change = "missing"
        elif not element.get("identity_comparable", False):
            change = "not_comparable"
        elif key in changed_classes or not _matches(element, purpose["subject_classes"]):
            change = "class_changed"
        elif key not in selected:
            change = "scope_excluded"
        elif incompatible or after is None:
            change = "not_comparable"
        elif before == after:
            change = "remaining" if after != "READY" else "unchanged"
        else:
            change = (
                "rule_recheck_passed"
                if before == "BLOCKED" and after == "READY" and evidence not in manual_ids
                else "evidence_updated"
            )
        result["outcomes"].append(
            {
                "evidence_id": evidence,
                "subject_keys": [key],
                "before": before,
                "after": after,
                "change": change,
                "review_element_key": element.get("review_element_key", "") if element else "",
            }
        )
    return result


def assess_evaluation(
    package,
    evaluation,
    *,
    project_id,
    revision_id,
    purpose_id,
    scope,
    responsible_team,
    determinations=(),
    prior=None,
    consumer=None,
):
    """Assess one confirmed package against one explicit immutable revision/scope."""
    if not responsible_team or not responsible_team.strip():
        raise ValueError("A declared responsible reviewer/team is required")
    purpose = next(
        (p for p in package.manifest["purposes"] if p["purpose_id"] == purpose_id), None
    )
    if purpose is None:
        raise ValueError("Unknown purpose")
    previous_record = (
        restore_record(prior["record"], prior["assessment_digest"])
        if prior and prior.get("record")
        else None
    )
    elements = evaluation["elements"]
    for label, values in (
        ("element", [e["element_key"] for e in elements]),
        ("finding", [f["finding_key"] for f in evaluation["findings"]]),
        (
            "observation",
            [(f["element_key"], f["requirement_key"]) for f in evaluation["findings"]],
        ),
    ):
        if len(values) != len(set(values)):
            raise ValueError("Duplicate " + label + " in evaluation")
    selected = _scope_keys(scope, elements)
    admitted = [
        e
        for e in elements
        if e["element_key"] in selected and _matches(e, purpose["subject_classes"])
    ]
    rows = _definitions(package, evaluation, purpose)
    if len(evaluation["models"]) != 1:
        raise ValueError("A purpose review requires one producing model slot")
    model = evaluation["models"][0]
    producing = ModelVersion(model["model_key"], model["content_id"])
    consuming, consumer_elements = (
        (producing, ()) if not consumer else _consumer_context(consumer, project_id)
    )
    context = ModelVersionContext(
        producing,
        consuming,
        HandoverEvent(
            purpose["from_role"], purpose["to_role"], purpose["title"], "not-recorded"
        ),
    )
    context_document = {
        "kind": "counterpart-model" if consumer else "same-delivered-artifact",
        "project_id": project_id,
        "revision_id": revision_id,
        "purpose_id": purpose_id,
        "producing": {"model_key": producing.model_key, "content_id": producing.content_id},
        "consuming": {"model_key": consuming.model_key, "content_id": consuming.content_id},
        "scope": copy.deepcopy(scope),
        "subject_keys": selected,
        "package_sha256": package.source_sha256,
    }
    context_digest = _digest(context_document)
    basis = {
        "model": [context_document["producing"], context_document["consuming"]],
        "rules": {
            "source_sha256": package.source_sha256,
            "version": package.manifest["version"],
            "checks": {r["requirement_key"]: r.get("semantics_digest", "") for r in rows},
        },
        "scope": {"declaration": copy.deepcopy(scope), "subjects": selected},
        "human": _digest(determinations),
        "identities": {e["element_key"]: e.get("identity_comparable", False) for e in admitted},
        "classes": {e["element_key"]: e["ifc_class"] for e in admitted},
        "engine": copy.deepcopy(evaluation["ruleset"].get("checker", {})),
        "configuration": {
            "project_id": project_id,
            "purpose": copy.deepcopy(purpose),
            "responsible_team": responsible_team,
        },
    }
    result = {
        "record": None,
        "assessment_digest": None,
        "context": context_document,
        "context_digest": context_digest,
        "comparison_basis": basis,
        "blockers": [],
        "evidence_requests": [],
        "declined_determinations": [],
        "conclusion": {
            "status": "UNKNOWN",
            "counts": {"ready": 0, "blocked": 0, "unknown": 0},
            "scope_count": len(admitted),
            "caveats": [
                "Readiness concerns only this purpose, scope and exact evidence versions.",
                "User-recorded judgments are not signatures or risk authorisations.",
            ],
        },
    }
    if not admitted or purpose["requires_counterpart"] and not consumer:
        reason = (
            "No purpose subjects in the declared scope"
            if not admitted
            else "An actual counterpart revision is required"
        )
        result["refusal"] = {
            "code": "scope-empty" if not admitted else "counterpart-required",
            "text": reason,
        }
        result["conclusion"]["caveats"].append(reason)
        result["change_summary"] = _changes(prior, basis, elements, selected, purpose, None)
        return result
    pack, overlay, keys = _configuration(
        package, purpose, rows, elements, evaluation, responsible_team
    )
    composed = compose_purpose_inputs(
        project_id=project_id, overlay=overlay, packs=(pack,), requirement_keys_by_ruleset=keys
    )
    facts = _facts(evaluation, project_id, rows, context, consumer_elements)
    request = AssessmentRequest(
        project_id,
        pack.pack_id,
        pack.pack_version,
        "delivery",
        tuple(a.activity_id for a in pack.activities),
        AssessedScope(element_keys=tuple(selected)),
        context,
    )
    attributable = [e["element_key"] for e in admitted if e.get("identity_comparable", False)]
    claims, declined = _determinations(
        determinations, rows, context_digest, context, attributable
    )
    result["declined_determinations"] = declined
    changes = _changes(prior, basis, elements, selected, purpose, None)
    try:
        if previous_record and changes["comparable"]:
            record = recheck_purpose(
                prior=previous_record,
                request=request,
                composed=composed,
                facts=facts,
                determinations=claims,
                succeeds=tuple(
                    (a.activity_ref, s.ordinal)
                    for a in previous_record.activities
                    for s in a.subscopes
                ),
            )
        else:
            record = assess_purpose(
                request=request, composed=composed, facts=facts, determinations=claims
            )
    except PurposeAssessmentError as error:
        result["refusal"] = {"code": error.code, "text": str(error)}
        result["conclusion"]["caveats"].append(str(error))
        result["change_summary"] = changes
        return result
    result.update(record=record.as_document(), assessment_digest=record.assessment_digest)
    verdicts = Counter()
    by_key = {e["element_key"]: e for e in elements}
    by_evidence = {r["evidence_id"]: r for r in rows}
    coverage = {r["requirement_key"]: r for r in evaluation.get("coverage", ())}
    for activity in record.activities:
        row = by_evidence[activity.activity_ref.split("::", 1)[1]]
        for subscope in activity.subscopes:
            for member in subscope.members:
                verdicts[subscope.verdict.lower()] += 1
                element = by_key[member.keys[0]]
                if subscope.verdict == "READY" and row["execution"] != "manual":
                    continue
                reading = next(
                    r for r in subscope.path[-1].readings if r.subject.keys == member.keys
                )
                reason = reading.absence or (
                    "Requirement failed"
                    if subscope.verdict == "BLOCKED"
                    else "; ".join(row.get("unsupported_reasons", ()))
                    or row.get("reason")
                    or "No admissible evidence"
                )
                if not element.get("identity_comparable", False):
                    reason = "Element identity is invalid or ambiguous; "
                    reason += "evidence is not attributable."
                elif row.get("support") == "unsupported" or row["execution"] == "unsupported":
                    reason = "; ".join(row.get("unsupported_reasons", ())) or row.get(
                        "reason", "Unsupported check"
                    )
                elif coverage.get(row["requirement_key"], {}).get("reason"):
                    reason = coverage[row["requirement_key"]]["reason"]
                finding = next(
                    (
                        f
                        for f in evaluation["findings"]
                        if f.get("finding_key") in reading.finding_keys
                    ),
                    None,
                )
                if finding:
                    reason = finding["reason"]
                action_en, action_zh = _next_actions(
                    row, subscope.verdict == "BLOCKED", coverage.get(row["requirement_key"])
                )
                block = {
                    "blocker_id": _digest([row["evidence_id"], member.keys])[:24],
                    "kind": row["execution"],
                    "verdict": subscope.verdict,
                    "evidence_id": row["evidence_id"],
                    "rule_id": row.get("rule_id", ""),
                    "requirement_key": row["requirement_key"],
                    "title": row.get("title", row["evidence_id"]),
                    "reason": reason,
                    "expected": row.get("expected", row.get("acceptance", "")),
                    "actual": finding.get("actual", "") if finding else "",
                    "finding_key": finding.get("finding_key", "") if finding else "",
                    "subject_keys": list(member.keys),
                    "review_element_key": element.get("review_element_key", ""),
                    "element_name": element.get("name", ""),
                    "next_action": action_en,
                    "next_action_zh": action_zh,
                    "recheck_condition": subscope.route.recheck_condition
                    if subscope.route
                    else "confirmed",
                    "hypotheses": [
                        {"text": h if isinstance(h, str) else h["text"], "status": "unverified"}
                        for h in row.get("hypotheses", ())
                    ],
                }
                if subscope.verdict != "READY":
                    result["blockers"].append(block)
                if row["execution"] in ("manual", "unsupported"):
                    result["evidence_requests"].append(
                        {
                            **block,
                            "acceptance": row.get("acceptance", ""),
                            "execution": row["execution"],
                            "method_id": row.get("method_id", ""),
                            "method_description": row.get("method_description", ""),
                            "outcomes": ["confirmed", "unmet", "not-yet-confirmed"],
                            "context_digest": context_digest,
                            "current_outcome": reading.outcome,
                        }
                    )
    status = (
        "BLOCKED"
        if verdicts["blocked"]
        else "UNKNOWN"
        if verdicts["unknown"] or not verdicts
        else "READY"
    )
    result["conclusion"].update(
        status=status, counts={k: verdicts[k] for k in ("ready", "blocked", "unknown")}
    )
    result["change_summary"] = _changes(
        prior, basis, elements, selected, purpose, result["record"]
    )
    return result
