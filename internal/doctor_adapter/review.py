"""Session-local IFC review and real tessellation for BIM Doctor.

This adapter never invokes pipeline writers or modifies published artifacts.
It retains bounded immutable JSON payloads and can stream worker geometry into
an explicitly supplied scratch file. Native computation never holds cache locks.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
import tomllib

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element

from .review_rules import ProductValidation
from .review_cache import SerializedReviewCache

ROOT = Path(__file__).resolve().parents[2]
MAX_MODEL_BYTES = 64 * 1024 * 1024
CACHE_MAX_ENTRIES = 16
CACHE_MAX_BYTES = 64 * 1024 * 1024
GUID_PATTERN = re.compile(r"[0-3][0-9A-Za-z_$]{21}\Z")
LOCAL_RULES = [
    {
        "rule_id": "INFO-001",
        "predicate_version": "1",
        "severity": "INFO",
        "title": "Element has a readable Name",
        "expected": "A non-blank Name",
        "citation": "BIM Doctor information-quality convention. IFC Name is optional; "
        "this check does not establish schema or regulatory compliance.",
        "scope": "IfcElement occurrences",
    },
    {
        "rule_id": "INFO-002",
        "predicate_version": "1",
        "severity": "INFO",
        "title": "Element resolves to a building storey",
        "expected": "An IfcBuildingStorey through spatial containment or parent relations",
        "citation": "BIM Doctor information-location convention, using IFC containment "
        "and decomposition. Not a room-assignment or statutory check.",
        "scope": "IfcElement occurrences including nested parts and openings",
    },
    {
        "rule_id": "ID-001",
        "predicate_version": "1",
        "severity": "ERROR",
        "title": "GlobalId is valid and unique within its IFC file",
        "expected": "A 22-character compressed IFC GlobalId unique among this file's IfcRoot",
        "citation": "IFC IfcGloballyUniqueId compressed identifier format; "
        "uniqueness checked within one file, not across federated models.",
        "scope": "Displayed IfcElement; duplicate counts include every IfcRoot in the file",
    },
]
COLORS = {
    "Architecture": [0.70, 0.76, 0.81],
    "HVAC": [0.26, 0.69, 0.78],
    "Structural": [0.86, 0.67, 0.43],
    "Unknown": [0.65, 0.74, 0.81],
}


class ReviewInputError(ValueError):
    """The supplied bytes cannot be reviewed as an IFC STEP file."""


class ReviewStore:
    """Bounded payload LRU. Limits cover retained bytes, not total process peak RSS."""

    def __init__(
        self,
        repository_root: Path = ROOT,
        max_model_bytes: int = MAX_MODEL_BYTES,
        *,
        rule_library_path: Path | None = None,
        cache_max_entries: int = CACHE_MAX_ENTRIES,
        cache_max_bytes: int = CACHE_MAX_BYTES,
    ):
        self.root = Path(repository_root)
        library = rule_library_path or ROOT / "rules/product-validation"
        self._product_validation = ProductValidation(library)
        self._rules = [deepcopy(self._product_validation.snapshot), *deepcopy(LOCAL_RULES)]
        self.max_model_bytes = max_model_bytes
        self._cache = SerializedReviewCache(cache_max_entries, cache_max_bytes)
        self._lock = self._cache.lock
        self._report_loader = self._geometry_loader = None
        self._demo_id: str | None = None

    def demo(self, *, progress=None, geometry_output: Path | None = None) -> dict:
        with self._lock:
            demo_id = self._demo_id
        if demo_id is not None:
            try:
                report = self.get(demo_id)
                if geometry_output is not None:
                    geometry_output.write_bytes(self.geometry_payload(demo_id))
                return report
            except KeyError:
                pass
        manifest = tomllib.loads(
            (self.root / "projects/pcert-sample/project.toml").read_text(encoding="utf-8")
        )
        inputs = []
        for item in manifest["models"]:
            body = (self.root / "data/raw" / item["filename"]).read_bytes()
            if hashlib.sha256(body).hexdigest() != item["content_sha256"]:
                raise ReviewInputError(f"Demo source hash mismatch: {item['filename']}")
            inputs.append((dict(item), body))
        source = {
            "kind": "demo",
            "filename": "PCERT Sample Scene (3 models)",
            "sha256": hashlib.sha256(b"".join(b for _, b in inputs)).hexdigest(),
            "attribution": "PCERT Sample Scene © buildingSMART International Ltd. "
            "CC BY 4.0. Unmodified public IFC sample files.",
            "source_url": "https://github.com/buildingSMART/Sample-Test-Files",
        }
        report = self._build(source, inputs, progress=progress, geometry_output=geometry_output)
        with self._lock:
            self._demo_id = report["review_id"]
        return report

    def create(
        self, filename: str, body: bytes, *, progress=None, geometry_output: Path | None = None
    ) -> dict:
        # Only the displayed filename is used; it is never opened as a local path.
        filename = str(filename).replace("\\", "/").rsplit("/", 1)[-1]
        if not filename.lower().endswith(".ifc"):
            raise ReviewInputError("Choose an .ifc STEP model file.")
        if not body:
            raise ReviewInputError("The IFC file is empty.")
        if len(body) > self.max_model_bytes:
            raise ReviewInputError(f"The model exceeds {self.max_model_bytes} bytes.")
        digest = hashlib.sha256(body).hexdigest()
        source = {
            "kind": "upload",
            "filename": filename,
            "sha256": digest,
            "attribution": "Local user-supplied model; processed in memory on this server.",
        }
        model = {
            "model_key": "upload." + digest[:16],
            "filename": filename,
            "discipline": "Unknown",
            "content_sha256": digest,
        }
        return self._build(
            source, [(model, body)], progress=progress, geometry_output=geometry_output
        )

    def set_loaders(self, *, report_loader=None, geometry_loader=None):
        """Miss loaders run outside locks and return serialized bytes, never call getters."""
        with self._lock:
            if report_loader is not None:
                self._report_loader = report_loader
            if geometry_loader is not None:
                self._geometry_loader = geometry_loader

    def stats(self):
        """Entry count means serialized report/geometry payloads, not whole reviews."""
        return self._cache.stats()

    def clear(self, review_id=None):
        return self._cache.clear(review_id)

    def report_payload(self, review_id: str) -> bytes:
        payload = self._cache.get("report", review_id)
        if payload is not None:
            return payload
        with self._lock:
            loader = self._report_loader
        if loader is None:
            raise KeyError(review_id)
        report, encoded = _report_payload(loader(review_id))
        if report["review_id"] != review_id:
            raise ValueError("Restored report identity does not match.")
        self._cache.admit({("report", review_id): _prepared(encoded)})
        return encoded

    def get(self, review_id: str) -> dict:
        return json.loads(self.report_payload(review_id))

    def geometry_payload(self, review_id: str) -> bytes:
        """Return immutable JSON bytes directly; no float tree or payload copies."""
        payload = self._cache.get("geometry", review_id)
        if payload is not None:
            return payload
        with self._lock:
            loader = self._geometry_loader
        if loader is None:
            raise KeyError(review_id)
        payload = loader(review_id)
        return self.admit_geometry_payload(review_id, payload)

    def geometry(self, review_id: str) -> dict:
        """Compatibility accessor; HTTP should use geometry_payload instead."""
        return json.loads(self.geometry_payload(review_id))

    def admit_report(self, report, *, expected_review_id=None) -> dict:
        decoded, payload = _report_payload(report)
        if expected_review_id is not None and decoded["review_id"] != expected_review_id:
            raise ValueError("Restored report identity does not match.")
        self._cache.admit({("report", decoded["review_id"]): _prepared(payload)})
        return decoded

    def admit_geometry_payload(self, review_id: str, payload: bytes) -> bytes:
        _geometry_identity(payload, review_id)
        self._cache.admit({("geometry", review_id): _prepared(payload)})
        return payload

    def admit_serialized(
        self, report_payload: bytes, geometry_payload: bytes | None = None
    ) -> dict:
        """Admit trusted complete worker output without decoding geometry arrays.

        Geometry JSON must start with review_id, as this adapter's writer does.
        The worker owns full JSON/mesh validation; admission checks binding and
        immutable payload hashes. These methods are not an untrusted JSON API.
        """
        report, encoded = _report_payload(report_payload)
        prepared = {("report", report["review_id"]): _prepared(encoded)}
        if geometry_payload is not None:
            _geometry_identity(geometry_payload, report["review_id"])
            prepared[("geometry", report["review_id"])] = _prepared(geometry_payload)
        self._cache.admit(prepared)
        return report

    def admit(self, report: dict, geometry: dict) -> dict:
        """Compatibility admission with full dictionary binding/finite JSON checks."""
        decoded, encoded = _report_payload(report)
        if not isinstance(geometry, dict) or geometry.get("review_id") != decoded["review_id"]:
            raise ValueError("Saved report and geometry identities must match.")
        if any(not isinstance(geometry.get(key), list) for key in ("meshes", "unavailable")):
            raise ValueError("Saved geometry is missing mesh evidence.")
        keys = {item["element_key"] for item in decoded["elements"]}
        if any(
            item["element_key"] not in keys
            for item in geometry["meshes"] + geometry["unavailable"]
        ):
            raise ValueError("Saved geometry element bindings are inconsistent.")
        ordered = {"review_id": geometry["review_id"], **geometry}
        return self.admit_serialized(encoded, _encode(ordered))

    def _build(
        self,
        source: dict,
        inputs: list[tuple[dict, bytes]],
        *,
        progress=None,
        geometry_output: Path | None = None,
    ) -> dict:
        identity = source["kind"] + source["filename"] + source["sha256"]
        identity += json.dumps(self._rules, sort_keys=True, ensure_ascii=False)
        review_id = "review-" + hashlib.sha256(identity.encode()).hexdigest()[:24]
        try:
            cached = self.get(review_id)
            if geometry_output is not None:
                geometry_output.write_bytes(self.geometry_payload(review_id))
            _progress(progress, "complete", 1, 1)
            return cached
        except KeyError:
            pass
        elements, findings, models, meshes, unavailable = [], [], [], [], []
        _progress(progress, "parsing", 0, len(inputs))
        for model_number, (metadata, body) in enumerate(inputs, 1):
            try:
                model = _open_step(body)
                model.by_type("IfcRoot")
            except Exception as error:
                raise ReviewInputError(
                    f"{metadata['filename']} could not be read as an IFC STEP model."
                ) from error
            _progress(progress, "parsing", model_number, len(inputs))
            model_key = metadata["model_key"]
            models.append(
                {
                    "model_key": model_key,
                    "name": metadata["filename"],
                    "discipline": metadata["discipline"],
                    "schema": model.schema,
                    "sha256": metadata["content_sha256"],
                    "source_url": metadata.get("source_url", ""),
                    "license": metadata.get("license", "User supplied"),
                }
            )
            model_elements = sorted(model.by_type("IfcElement"), key=lambda item: item.id())
            _progress(progress, "checking", 0, len(model_elements))
            product_results = self._product_validation.evaluate(model)
            counts = Counter(str(root.GlobalId or "") for root in model.by_type("IfcRoot"))
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            rows_for_model = []
            for element_number, entity in enumerate(model_elements, 1):
                guid = str(entity.GlobalId or "")
                ambiguous = not GUID_PATTERN.fullmatch(guid) or counts[guid] > 1
                suffix = f"::step-{entity.id()}" if ambiguous else ""
                key = f"{model_key}::{guid or 'missing-global-id'}{suffix}"
                storey = ifcopenshell.util.element.get_container(
                    entity, ifc_class="IfcBuildingStorey"
                )
                container = ifcopenshell.util.element.get_container(entity)
                container_name = (
                    f"{container.is_a()}: {container.Name or container.id()}"
                    if container
                    else "No spatial container resolved"
                )
                storey_name = str(storey.Name or f"Storey #{storey.id()}") if storey else ""
                row = {
                    "element_key": key,
                    "global_id": guid,
                    "global_id_count": counts[guid],
                    "model_key": model_key,
                    "step_id": entity.id(),
                    "ifc_class": entity.is_a(),
                    "name": str(entity.Name or ""),
                    "storey": storey_name,
                    "tag": str(getattr(entity, "Tag", None) or ""),
                    "spatial_container": container_name,
                    "geometry_status": "unavailable",
                }
                elements.append(row)
                rows_for_model.append(row)
                findings.extend(
                    _findings(entity, row, counts[guid], self._rules, product_results)
                )
                if element_number % 25 == 0 or element_number == len(model_elements):
                    _progress(progress, "checking", element_number, len(model_elements))
            _progress(progress, "tessellating", 0, len(model_elements))
            for element_number, (entity, row) in enumerate(
                zip(model_elements, rows_for_model), 1
            ):
                mesh, reason = _mesh(
                    entity, row["element_key"], settings, metadata["discipline"]
                )
                if mesh is not None:
                    row["geometry_status"] = "renderable"
                    meshes.append(mesh)
                else:
                    unavailable.append({"element_key": row["element_key"], "reason": reason})
                if element_number % 25 == 0 or element_number == len(model_elements):
                    _progress(progress, "tessellating", element_number, len(model_elements))
        statuses = Counter(item["status"] for item in findings)
        report = {
            "review_id": review_id,
            "source": source,
            "models": models,
            "elements": elements,
            "findings": findings,
            "rules": deepcopy(self._rules),
            "summary": {
                "elements": len(elements),
                "renderable": len(meshes),
                "findings": len(findings),
                "failed": statuses["FAIL"],
                "passed": statuses["PASS"],
                "not_applicable": statuses["NOT_APPLICABLE"],
                "errors": sum(
                    f["status"] == "FAIL" and f["severity"] == "ERROR" for f in findings
                ),
                "information": sum(
                    f["status"] == "FAIL" and f["severity"] == "INFO" for f in findings
                ),
            },
            "scope": "Information-quality checks and geometry inspection. "
            "No clash, clearance, fire-safety or regulatory assessment.",
        }
        geometry = {
            "review_id": review_id,
            "coordinate_system": "IFC world coordinates",
            "units": "metres",
            "up_axis": "Z",
            "meshes": meshes,
            "unavailable": unavailable,
        }
        _progress(progress, "serializing", 0, 1)
        if geometry_output is not None:
            geometry_output = Path(geometry_output)
            temporary = geometry_output.with_name(geometry_output.name + ".tmp")
            with temporary.open("w", encoding="utf-8", newline="\n") as stream:
                json.dump(
                    geometry, stream, ensure_ascii=False, allow_nan=False, separators=(",", ":")
                )
            os.replace(temporary, geometry_output)
            self.admit_report(report)
        else:
            self.admit_serialized(_encode(report), _encode(geometry))
        _progress(progress, "serializing", 1, 1)
        _progress(progress, "complete", 1, 1)
        return report


def _encode(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode(
        "utf-8"
    )


def _prepared(payload: bytes):
    return payload, hashlib.sha256(payload).digest()


def _report_payload(value):
    if isinstance(value, bytes):
        decoded = json.loads(value)
    elif isinstance(value, dict):
        decoded = json.loads(_encode(value))
    else:
        raise ValueError("Saved report must be an object or UTF-8 JSON bytes.")
    if (
        not isinstance(decoded, dict)
        or not isinstance(decoded.get("review_id"), str)
        or not decoded["review_id"]
    ):
        raise ValueError("Saved report has no review identity.")
    if any(
        not isinstance(decoded.get(key), list)
        for key in ("models", "elements", "findings", "rules")
    ):
        raise ValueError("Saved report is missing review evidence.")
    keys = {item["element_key"] for item in decoded["elements"]}
    if len(keys) != len(decoded["elements"]) or any(
        item["element_key"] not in keys for item in decoded["findings"]
    ):
        raise ValueError("Saved review element bindings are inconsistent.")
    payload = json.dumps(
        decoded, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    ).encode("utf-8")
    return decoded, payload


_GEOMETRY_HEADER = re.compile(rb'^\s*\{\s*"review_id"\s*:\s*("(?:\\.|[^"\\])*")\s*[,}]')


def _geometry_identity(payload, review_id):
    if not isinstance(payload, bytes):
        raise ValueError("Geometry payload must be immutable UTF-8 JSON bytes.")
    match = _GEOMETRY_HEADER.match(payload[:4096])
    if match is None or json.loads(match.group(1)) != review_id:
        raise ValueError("Serialized geometry must start with its matching review_id.")
    last = len(payload) - 1
    while last >= 0 and payload[last] in b" \t\r\n":
        last -= 1
    if last < 0 or payload[last] != ord("}"):
        raise ValueError("Serialized geometry is incomplete.")


def _progress(callback, stage, completed, total):
    if callback is not None:
        callback(stage, completed, total)


def _open_step(body: bytes):
    if not body.removeprefix(b"\xef\xbb\xbf").lstrip().startswith(b"ISO-10303-21;"):
        raise ValueError("missing STEP header")
    try:
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Legacy STEP text can contain non-UTF-8 bytes. Let the native reader
        # interpret the original encoding, rather than guessing or replacing it.
        # IfcOpenShell's in-memory SWIG reader accepts str only, so retain exact
        # input bytes in a short-lived temporary file and remove it after parse.
        with tempfile.TemporaryDirectory(prefix="epc-doctor-ifc-") as scratch:
            path = Path(scratch) / "model.ifc"
            path.write_bytes(body)
            return ifcopenshell.open(path)
    return ifcopenshell.file.from_string(text)


def _mesh(entity, key, settings, discipline):
    if not entity.Representation:
        return None, "The IFC element has no representation."
    try:
        shape = ifcopenshell.geom.create_shape(settings, entity)
        positions = list(shape.geometry.verts)
        indices = list(shape.geometry.faces)
        if not positions or not indices:
            return None, "No triangle geometry was produced for this representation."
        if not all(math.isfinite(value) for value in positions):
            return None, "The representation produced non-finite coordinates."
        return {
            "element_key": key,
            "positions": positions,
            "indices": indices,
            "color": COLORS.get(discipline, COLORS["Unknown"]),
        }, ""
    except Exception:
        return None, "IfcOpenShell could not tessellate this representation."


def _findings(entity, row, id_count, rules, product_results):
    # The effective value is evidence for the UI only. Applicability and status
    # come from the shared compiled rule + IfcTester model evaluation above.
    effective = ifcopenshell.util.element.get_predefined_type(entity)
    pv_status = product_results.get(entity.id(), "NOT_APPLICABLE")
    applicable = pv_status != "NOT_APPLICABLE"
    valid_id = bool(GUID_PATTERN.fullmatch(row["global_id"])) and id_count == 1
    outcomes = [
        (
            pv_status,
            str(effective or "Not declared") if applicable else entity.is_a(),
            "The source rule requirement is satisfied by the effective predefined type."
            if pv_status == "PASS"
            else "The source rule is not satisfied; verify effective type and IFC mapping."
            if applicable
            else "This element is outside the source rule applicability.",
        ),
        (
            "PASS" if row["name"].strip() else "FAIL",
            row["name"] or "Not declared",
            "The occurrence Name is non-blank."
            if row["name"].strip()
            else "No readable Name; model selection relies on IFC identity.",
        ),
        (
            "PASS" if row["storey"] else "FAIL",
            row["storey"] or "No storey resolved; " + row["spatial_container"],
            "A building storey resolves through the IFC spatial/parent chain."
            if row["storey"]
            else "No storey resolves through IFC parent relations; existing site/building "
            "containment may be appropriate for this object.",
        ),
        (
            "PASS" if valid_id else "FAIL",
            f"{row['global_id'] or 'Missing'}; {id_count} occurrence(s) among IfcRoot",
            "The compressed GlobalId is valid and unique within this file."
            if valid_id
            else "GlobalId is malformed, absent, or repeated; STEP id preserves selection.",
        ),
    ]
    result = []
    for rule, (status, actual, reason) in zip(rules, outcomes):
        identity = row["element_key"] + "::" + rule["rule_id"]
        result.append(
            {
                "finding_id": hashlib.sha256(identity.encode()).hexdigest()[:24],
                "element_key": row["element_key"],
                "rule_id": rule["rule_id"],
                "status": status,
                "severity": rule["severity"],
                "title": rule["title"],
                "expected": rule["expected"],
                "actual": actual,
                "reason": reason,
                "citation": rule["citation"],
            }
        )
    return result
