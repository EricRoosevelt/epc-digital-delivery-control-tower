"""Session-local IFC review and real tessellation for BIM Doctor.

This read-only adapter never invokes pipeline writers or modifies published artifacts.
Review data and geometry live in memory until the local server exits.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re
import threading
import tempfile
import tomllib

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element

from .review_rules import ProductValidation

ROOT = Path(__file__).resolve().parents[2]
MAX_MODEL_BYTES = 64 * 1024 * 1024
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
    """Own reviews for one local server; methods return isolated JSON-shaped copies."""

    def __init__(
        self,
        repository_root: Path = ROOT,
        max_model_bytes: int = MAX_MODEL_BYTES,
        *,
        rule_library_path: Path | None = None,
    ):
        self.root = Path(repository_root)
        library = rule_library_path or ROOT / "rules/product-validation"
        self._product_validation = ProductValidation(library)
        self._rules = [deepcopy(self._product_validation.snapshot), *deepcopy(LOCAL_RULES)]
        self.max_model_bytes = max_model_bytes
        self._reviews: dict[str, tuple[dict, dict]] = {}
        self._lock = threading.RLock()
        self._demo_id: str | None = None

    def demo(self) -> dict:
        with self._lock:
            if self._demo_id is not None:
                return self.get(self._demo_id)
            manifest = tomllib.loads(
                (self.root / "projects/pcert-sample/project.toml").read_text(encoding="utf-8")
            )
            inputs = []
            for item in manifest["models"]:
                body = (self.root / "data/raw" / item["filename"]).read_bytes()
                digest = hashlib.sha256(body).hexdigest()
                if digest != item["content_sha256"]:
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
            report = self._build(source, inputs)
            self._demo_id = report["review_id"]
            return deepcopy(report)

    def create(self, filename: str, body: bytes) -> dict:
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
        with self._lock:
            return deepcopy(self._build(source, [(model, body)]))

    def get(self, review_id: str) -> dict:
        with self._lock:
            return deepcopy(self._reviews[review_id][0])

    def geometry(self, review_id: str) -> dict:
        with self._lock:
            return deepcopy(self._reviews[review_id][1])

    def admit(self, report: dict, geometry: dict) -> dict:
        """Restore an immutable saved review without changing its evidence or identity."""
        if not isinstance(report, dict) or not isinstance(geometry, dict):
            raise ValueError("Saved report and geometry must be objects.")
        review_id = report.get("review_id")
        if (
            not isinstance(review_id, str)
            or not review_id
            or geometry.get("review_id") != review_id
        ):
            raise ValueError("Saved report and geometry identities must match.")
        if any(
            not isinstance(report.get(key), list)
            for key in ("models", "elements", "findings", "rules")
        ):
            raise ValueError("Saved report is missing review evidence.")
        if any(not isinstance(geometry.get(key), list) for key in ("meshes", "unavailable")):
            raise ValueError("Saved geometry is missing mesh evidence.")
        keys = {item["element_key"] for item in report["elements"]}
        if len(keys) != len(report["elements"]) or any(
            item["element_key"] not in keys
            for item in report["findings"] + geometry["meshes"] + geometry["unavailable"]
        ):
            raise ValueError("Saved review element bindings are inconsistent.")
        # Verify JSON validity before admitting persisted evidence to existing endpoints.
        json.dumps((report, geometry), allow_nan=False)
        with self._lock:
            prior = self._reviews.get(review_id)
            if prior is not None and prior != (report, geometry):
                raise ValueError("A different review already uses this session identity.")
            self._reviews[review_id] = (deepcopy(report), deepcopy(geometry))
            return deepcopy(report)

    def _build(self, source: dict, inputs: list[tuple[dict, bytes]]) -> dict:
        identity = source["kind"] + source["filename"] + source["sha256"]
        identity += json.dumps(self._rules, sort_keys=True, ensure_ascii=False)
        review_id = "review-" + hashlib.sha256(identity.encode()).hexdigest()[:24]
        if review_id in self._reviews:
            return self._reviews[review_id][0]
        elements, findings, models, meshes, unavailable = [], [], [], [], []
        for metadata, body in inputs:
            try:
                model = _open_step(body)
                model.by_type("IfcRoot")
            except Exception as error:
                raise ReviewInputError(
                    f"{metadata['filename']} could not be read as an IFC STEP model."
                ) from error
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
            product_results = self._product_validation.evaluate(model)
            counts = Counter(str(root.GlobalId or "") for root in model.by_type("IfcRoot"))
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            for entity in sorted(model.by_type("IfcElement"), key=lambda item: item.id()):
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
                mesh, reason = _mesh(entity, key, settings, metadata["discipline"])
                if mesh is not None:
                    row["geometry_status"] = "renderable"
                    meshes.append(mesh)
                else:
                    unavailable.append({"element_key": key, "reason": reason})
                elements.append(row)
                findings.extend(
                    _findings(entity, row, counts[guid], self._rules, product_results)
                )
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
        self._reviews[review_id] = (report, geometry)
        return report


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
