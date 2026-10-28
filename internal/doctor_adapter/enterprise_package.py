"""Bounded enterprise ZIP intake, with native TOML compilation and visible gaps."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
from importlib.metadata import version
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import tempfile
import tomllib
from zipfile import BadZipFile, ZipFile

from epc_control_tower.checkers.ids_checker import IdsChecker, requirement_label
from epc_control_tower.identity import build_requirement_key
from epc_control_tower.rule_definitions import (
    FacetDefinition,
    RuleSetDefinition,
    compile_document,
    load_rule_definitions,
)

MAX_PACKAGE_BYTES = 8 * 1024 * 1024
MAX_EXPANDED_BYTES = 4 * 1024 * 1024
MAX_FILES = 100
_RULE_FIELDS = {
    "rule_id",
    "title",
    "description",
    "checker",
    "severity",
    "owner_role",
    "stage",
    "discipline_scope",
    "citation",
    "priority",
    "labels",
    "ifc_version",
    "applicability",
    "requirements",
    "hypotheses",
}
_FACET_FIELDS = {
    "entity": {"name", "predefinedType"},
    "attribute": {"name", "value"},
    "property": {"propertySet", "baseName", "value", "dataType", "uri"},
    "classification": {"system", "value", "uri"},
    "material": {"value", "uri"},
    "partof": {"name", "predefinedType", "relation"},
}
_RESTRICTIONS = {
    "base",
    "enumeration",
    "pattern",
    "minInclusive",
    "maxInclusive",
    "minExclusive",
    "maxExclusive",
}


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def checker_basis():
    return {
        "component_id": "ids",
        "version": IdsChecker.version,
        "config_sha256": digest({}),
        "engine": "ifctester",
        "engine_version": version("ifctester"),
    }


def _text(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 4000:
        raise ValueError(f"{label} must be non-blank text of at most 4000 characters.")
    return value


def _texts(value, label, *, empty=False):
    if not isinstance(value, list) or (not value and not empty):
        raise ValueError(f"{label} must be a list of text values.")
    for item in value:
        _text(item, label)
    if len(set(value)) != len(value):
        raise ValueError(f"{label} contains duplicates.")


def _identifier(value, label):
    _text(value, label)
    if value != value.strip():
        raise ValueError(f"{label} identifier must not contain surrounding whitespace.")
    if "::" in value or len(value) > 80:
        raise ValueError(
            f"{label} identifier must be at most 80 characters without reserved '::'."
        )


def _fields(value, allowed, label):
    if not isinstance(value, dict) or set(value) - allowed:
        unknown = sorted(set(value) - allowed) if isinstance(value, dict) else "expected object"
        raise ValueError(f"{label} has unsupported structure or fields: {unknown}")


def _manifest(value):
    _fields(
        value,
        {"schema_version", "package_id", "title", "version", "source", "purposes"},
        "Manifest",
    )
    if type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise ValueError("Only manifest schema_version 1 is supported.")
    for key in ("package_id", "title", "version"):
        _text(value.get(key), key)
    _identifier(value["package_id"], "package_id")
    source = value.get("source")
    _fields(source, {"organization", "reference", "issued_on"}, "source")
    for key in ("organization", "reference", "issued_on"):
        _text(source.get(key), "source." + key)
    purposes = value.get("purposes")
    if not isinstance(purposes, list) or not purposes:
        raise ValueError("Declare at least one purpose.")
    seen = set()
    for purpose in purposes:
        _fields(
            purpose,
            {
                "purpose_id",
                "title",
                "title_zh",
                "from_role",
                "to_role",
                "subject_classes",
                "required_rule_ids",
                "requires_counterpart",
                "evidence_requirements",
            },
            "purpose",
        )
        for key in ("purpose_id", "title", "from_role", "to_role"):
            _text(purpose.get(key), "purpose." + key)
        _identifier(purpose["purpose_id"], "purpose_id")
        if purpose["purpose_id"] in seen:
            raise ValueError("Duplicate purpose_id.")
        seen.add(purpose["purpose_id"])
        if "title_zh" in purpose:
            _text(purpose["title_zh"], "purpose.title_zh")
        _texts(purpose.get("subject_classes"), "subject_classes")
        _texts(purpose.get("required_rule_ids"), "required_rule_ids", empty=True)
        if type(purpose.get("requires_counterpart")) is not bool:
            raise ValueError("requires_counterpart must be a boolean.")
        evidence = purpose.get("evidence_requirements")
        if not isinstance(evidence, list):
            raise ValueError("evidence_requirements must be a list.")
        evidence_ids = set()
        for item in evidence:
            _fields(
                item,
                {
                    "evidence_id",
                    "title",
                    "acceptance",
                    "execution",
                    "method_id",
                    "method_description",
                    "reason",
                },
                "evidence requirement",
            )
            for key in ("evidence_id", "title", "acceptance"):
                _text(item.get(key), key)
            _identifier(item["evidence_id"], "evidence_id")
            if item["evidence_id"] in evidence_ids:
                raise ValueError("Duplicate evidence_id within purpose.")
            evidence_ids.add(item["evidence_id"])
            if item.get("execution") == "manual":
                _text(item.get("method_id"), "method_id")
                _text(item.get("method_description"), "method_description")
            elif item.get("execution") == "unsupported":
                _text(item.get("reason"), "reason")
            else:
                raise ValueError("Evidence execution must be manual or unsupported.")
    return value


def _archive(body):
    if not isinstance(body, bytes) or not body or len(body) > MAX_PACKAGE_BYTES:
        raise ValueError("Choose a nonempty ZIP package of at most 8 MiB.")
    files, total = {}, 0
    try:
        with ZipFile(BytesIO(body)) as archive:
            if len(archive.infolist()) > MAX_FILES:
                raise ValueError("The package contains too many files.")
            for info in archive.infolist():
                name = info.filename
                path = PurePosixPath(name)
                if "\\" in name or ":" in name or path.is_absolute() or ".." in path.parts:
                    raise ValueError("Package paths must remain relative to the ZIP root.")
                if info.is_dir():
                    continue
                if str(path) != name:
                    raise ValueError("Package file paths must use their canonical spelling.")
                if name in files:
                    raise ValueError("The package contains duplicate paths.")
                if name != "manifest.json" and not (
                    len(path.parts) == 2 and path.parts[0] == "rules" and path.suffix == ".toml"
                ):
                    raise ValueError(f"Unsupported package file: {name}")
                total += info.file_size
                if total > MAX_EXPANDED_BYTES or info.file_size > 512 * 1024:
                    raise ValueError("The package exceeds the expanded text budget.")
                files[name] = archive.read(info)
    except (BadZipFile, RuntimeError, NotImplementedError) as error:
        raise ValueError("The package could not be read as an unencrypted ZIP.") from error
    if "manifest.json" not in files or "rules/ruleset.toml" not in files or len(files) < 3:
        raise ValueError(
            "A package needs manifest.json, rules/ruleset.toml and rule TOML files."
        )
    return files


def _unsupported(rule):
    reasons = [f"Unknown rule field: {key}" for key in sorted(set(rule) - _RULE_FIELDS)]
    if rule.get("discipline_scope"):
        reasons.append(
            "discipline_scope is not executable for an uploaded model with no verified "
            "discipline binding. Use explicit IDS applicability and a declared purpose scope."
        )
    if rule.get("checker", "ids") != "ids":
        reasons.append(f"Unsupported checker: {rule.get('checker')}")
    declared_schemas = rule.get("ifc_version", ["IFC4"])
    if not set(declared_schemas).intersection(IdsChecker.capabilities.ifc_schemas):
        reasons.append(f"Declared IFC schemas have no supported engine: {declared_schemas}")
    for section in ("applicability", "requirements"):
        entries = rule.get(section)
        if not isinstance(entries, list) or not entries:
            raise ValueError(f"Declare at least one {section} facet.")
        for facet in entries:
            if not isinstance(facet, dict):
                raise ValueError("Each facet must be a TOML table.")
            kind = str(facet.get("facet", "")).lower()
            if kind not in _FACET_FIELDS:
                reasons.append(f"Unsupported {section} facet: {kind}")
                continue
            allowed = _FACET_FIELDS[kind] | {"facet", "cardinality", "instructions"}
            reasons.extend(
                f"Unknown {section}.{kind} field: {key}" for key in sorted(set(facet) - allowed)
            )
            if "cardinality" in facet and facet["cardinality"] not in (
                "required",
                "optional",
                "prohibited",
            ):
                reasons.append(
                    f"Unsupported {section}.{kind} cardinality: {facet['cardinality']}"
                )
            for key, value in facet.items():
                if isinstance(value, dict):
                    reasons.extend(
                        f"Unknown restriction {key}.{extra}"
                        for extra in sorted(set(value) - _RESTRICTIONS)
                    )
    return reasons


@dataclass(frozen=True)
class EnterprisePackage:
    manifest: dict
    definition: RuleSetDefinition
    checks: tuple[dict, ...]
    source_sha256: str
    _preview: dict

    def preview(self):
        return deepcopy(self._preview)


def parse_package(body: bytes, filename: str) -> EnterprisePackage:
    files = _archive(body)
    try:
        manifest = _manifest(json.loads(files["manifest.json"]))
        meta = tomllib.loads(files["rules/ruleset.toml"].decode("utf-8-sig"))
        _fields(meta, {"ruleset"}, "ruleset.toml")
        section = meta.get("ruleset")
        _fields(
            section,
            {"ruleset_id", "version", "title", "description", "purpose", "milestone"},
            "ruleset",
        )
        for key in ("ruleset_id", "version", "title"):
            _text(section.get(key), "ruleset." + key)
        for key in ("description", "purpose", "milestone"):
            if key in section and not isinstance(section[key], str):
                raise ValueError(f"ruleset.{key} must be text.")
        raw_rules = []
        for name, data in sorted(files.items()):
            if name in {"manifest.json", "rules/ruleset.toml"}:
                continue
            rule = tomllib.loads(data.decode("utf-8-sig"))
            for key in ("rule_id", "title"):
                _text(rule.get(key), key)
            for key in ("ifc_version", "discipline_scope", "labels"):
                if key in rule:
                    _texts(rule[key], key, empty=key != "ifc_version")
            raw_rules.append((name, rule, _unsupported(rule)))
    except (UnicodeDecodeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        raise ValueError("The package contains invalid UTF-8 JSON or TOML.") from error
    ids = [rule["rule_id"] for _, rule, _ in raw_rules]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate rule_id in package.")
    for purpose in manifest["purposes"]:
        missing = set(purpose["required_rule_ids"]) - set(ids)
        if missing:
            raise ValueError(f"Purpose references missing rule ids: {sorted(missing)}")
    # Only fully supported rules enter the existing loader/compiler. A rule
    # containing an unknown field is preserved as unsupported, never weakened.
    with tempfile.TemporaryDirectory(prefix="bim-doctor-rules-") as scratch:
        directory = Path(scratch)
        (directory / "ruleset.toml").write_bytes(files["rules/ruleset.toml"])
        for name, _, reasons in raw_rules:
            if not reasons:
                (directory / PurePosixPath(name).name).write_bytes(files[name])
        try:
            if any(not reasons for _, _, reasons in raw_rules):
                definition = load_rule_definitions(directory)
            else:
                definition = RuleSetDefinition(**section)
            _, ruleset, expectations = compile_document(definition)
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid native rule or facet: {error}") from error
    basis, checks, rules, diagnostics = checker_basis(), [], [], []
    for name, raw, reasons in raw_rules:
        own_checks = []
        native = [r for r in ruleset.requirements if r.rule_id == raw["rule_id"]]
        if not reasons:
            for requirement in native:
                own_checks.append(
                    {
                        "requirement_key": requirement.requirement_key,
                        "rule_id": requirement.rule_id,
                        "title": raw["title"],
                        "semantics_digest": requirement.semantics_digest,
                        "expected": expectations[requirement.requirement_key],
                        "support": "supported",
                        "unsupported_reasons": [],
                        "checker": basis,
                    }
                )
        else:
            for index, facet in enumerate(raw["requirements"]):
                try:
                    built = FacetDefinition(
                        str(facet.get("facet", "")).lower(),
                        {k: v for k, v in facet.items() if k != "facet"},
                    ).build()
                    label = requirement_label(built)
                except (KeyError, ValueError, TypeError):
                    label = f"unsupported-{index + 1}"
                own_checks.append(
                    {
                        "requirement_key": build_requirement_key(raw["rule_id"], label),
                        "rule_id": raw["rule_id"],
                        "title": raw["title"],
                        "semantics_digest": digest({"rule": raw, "requirement": facet}),
                        "expected": json.dumps(facet, ensure_ascii=False, sort_keys=True),
                        "support": "unsupported",
                        "unsupported_reasons": list(reasons),
                        "checker": basis,
                    }
                )
            diagnostics.extend({"path": name, "message": reason} for reason in reasons)
        hypotheses = raw.get("hypotheses", [])
        _texts(hypotheses, "hypotheses", empty=True)
        rules.append(
            {
                "rule_id": raw["rule_id"],
                "title": raw["title"],
                "declaration": deepcopy(raw),
                "applicability": raw["applicability"],
                "requirements": own_checks,
                "hypotheses": [{"text": text, "verified": False} for text in hypotheses],
                "support": "unsupported" if reasons else "supported",
                "unsupported_reasons": reasons,
            }
        )
        checks.extend(own_checks)
    keys = [c["requirement_key"] for c in checks]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate requirement labels would share a key.")
    for purpose in manifest["purposes"]:
        automatic = {
            "check-" + digest(c["requirement_key"])[:16]
            for c in checks
            if c["rule_id"] in purpose["required_rule_ids"]
        }
        conflicts = automatic & {
            item["evidence_id"] for item in purpose["evidence_requirements"]
        }
        if conflicts:
            raise ValueError(
                "Evidence identifier conflicts with a compiled check in purpose "
                f"{purpose['purpose_id']!r}: {sorted(conflicts)}"
            )
    source_sha = hashlib.sha256(body).hexdigest()
    preview = {
        "filename": str(filename).replace("\\", "/").rsplit("/", 1)[-1],
        "manifest": manifest,
        "source_sha256": source_sha,
        "source": manifest["source"],
        "package_id": manifest["package_id"],
        "title": manifest["title"],
        "version": manifest["version"],
        "ruleset": {
            "ruleset_id": ruleset.ruleset_id,
            "version": ruleset.version,
            "normalized_digest": ruleset.normalized_digest,
            "source_sha256": source_sha,
            "checker": basis,
        },
        "rules": rules,
        "checks": checks,
        "purposes": manifest["purposes"],
        "diagnostics": diagnostics,
        "executable": any(c["support"] == "supported" for c in checks),
    }
    return EnterprisePackage(manifest, definition, tuple(checks), source_sha, preview)
