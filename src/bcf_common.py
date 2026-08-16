"""Shared deterministic and security helpers for the BCF 3.0 workflow."""

from __future__ import annotations

import csv
import hashlib
import io
import itertools
import math
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Mapping
from xml.etree import ElementTree as ET

import ifcopenshell
import ifcopenshell.geom

from identity import build_finding_key, build_requirement_key, uuid5_from_values


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = (
    PROJECT_ROOT
    / "third_party"
    / "buildingsmart"
    / "bcf-xml"
    / "3.0"
    / "Schemas"
)

FIXED_TIMESTAMP = "2026-08-13T00:00:00Z"
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
BCF_VERSION = "3.0"
PROJECT_NAME = "EPC Digital Delivery Control Tower"
PROJECT_GUID = uuid5_from_values("bcf-project", [PROJECT_NAME])
CREATION_AUTHOR = "control-tower@example.invalid"
ASSIGNEE = "model-coordination@example.invalid"
FINDING_URN_PREFIX = "urn:epc-digital-delivery:finding:"

MAX_ARCHIVE_ENTRIES = 100
MAX_ENTRY_SIZE = 5 * 1024 * 1024
MAX_ARCHIVE_SIZE = 20 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100

UUID_PATTERN = re.compile(
    r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-"
    r"[a-f0-9]{4}-[a-f0-9]{12}$"
)
IFC_GUID_PATTERN = re.compile(r"^[0-9A-Za-z_$]{22}$")

OFFICIAL_SCHEMA_COMMIT = "bc48611d0d7a1587f028a2b69677a1aafd5cd0a8"
OFFICIAL_SCHEMA_SHA256 = {
    "documents.xsd": (
        "9f74995582ed5b1e3375a785c818466d3a24171cc5935976970e8acc2f0f0da7"
    ),
    "extensions.xsd": (
        "5551f83d99e1c82de61201071756f118c8a429afba969e3ebdd95abeb5fe6141"
    ),
    "markup.xsd": (
        "e274d9020ec30b6ea05eb5ebde875d3859319cc5324df030f7e5579a4287d631"
    ),
    "project.xsd": (
        "3ee87efa318882c76177477147b959a706757743bf089ddbf8365ca7d8f0bfdb"
    ),
    "shared-types.xsd": (
        "c5cb0526cae1b38820f1b1311115a189c5df600431cf9d87c9a96b53efe1b725"
    ),
    "version.xsd": (
        "6663e7acaef740ca49e81df01f14d075bc136952282e7df40219584bc62a82c3"
    ),
    "visinfo.xsd": (
        "683c20f6d06daaa16f8c93ef1dc6bdabcecf66ff1548a6c4d24b6f3b8b476222"
    ),
}


@dataclass(frozen=True)
class Aabb:
    """A world-coordinate axis-aligned bounding box in metres."""

    minimum: tuple[float, float, float]
    maximum: tuple[float, float, float]

    @property
    def center(self) -> tuple[float, float, float]:
        return tuple(
            (lower + upper) / 2.0
            for lower, upper in zip(self.minimum, self.maximum, strict=True)
        )

    @property
    def diagonal(self) -> float:
        return math.sqrt(
            sum(
                (upper - lower) ** 2
                for lower, upper in zip(
                    self.minimum,
                    self.maximum,
                    strict=True,
                )
            )
        )


@dataclass(frozen=True)
class Camera:
    """A deterministic perspective camera aimed at an AABB centre."""

    position: tuple[float, float, float]
    direction: tuple[float, float, float]
    up: tuple[float, float, float]
    target: tuple[float, float, float]
    field_of_view: float = 60.0
    aspect_ratio: float = 16.0 / 9.0


def calculate_sha256(path: Path) -> str:
    """Return a lowercase SHA-256 digest for one file."""

    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def bytes_sha256(data: bytes) -> str:
    """Return a lowercase SHA-256 digest for an in-memory artifact."""

    return hashlib.sha256(data).hexdigest()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV while preserving the literal value ``N/A``."""

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv_bytes(
    rows: Iterable[Mapping[str, object]],
    columns: list[str],
) -> bytes:
    """Serialize rows using the repository's deterministic CSV convention."""

    text_stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        text_stream,
        fieldnames=columns,
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return b"\xef\xbb\xbf" + text_stream.getvalue().encode("utf-8")


def split_specification(value: str) -> tuple[str, str]:
    """Split ``R-001: title`` into its stable identifier and title."""

    identifier, separator, title = value.partition(":")
    if not separator or not identifier.strip() or not title.strip():
        raise ValueError(f"Invalid specification label: {value!r}")
    return identifier.strip(), title.strip()


def enrich_finding_identity(row: Mapping[str, str]) -> dict[str, str]:
    """Return a finding with stable keys, supporting the phase-two CSV shape."""

    enriched = dict(row)
    label_specification_id, _ = split_specification(enriched["specification"])
    specification_id = (
        enriched.get("specification_id") or label_specification_id
    )
    if specification_id != label_specification_id:
        raise ValueError(
            "specification_id does not match the specification label: "
            f"{specification_id!r}"
        )
    requirement_id = enriched.get("requirement_id") or enriched["requirement"]
    expected_requirement_key = build_requirement_key(
        specification_id,
        requirement_id,
    )
    requirement_key = enriched.get("requirement_key") or expected_requirement_key
    if requirement_key != expected_requirement_key:
        raise ValueError(
            "requirement_key does not match its specification/requirement payload: "
            f"{requirement_key!r}"
        )
    expected_finding_key = build_finding_key(
        enriched["run_id"],
        enriched["model_id"],
        requirement_key,
        enriched.get("element_key", ""),
    )
    finding_key = enriched.get("finding_key") or expected_finding_key
    if finding_key != expected_finding_key:
        raise ValueError(
            "finding_key does not match its finding payload: "
            f"{finding_key!r}"
        )

    if not UUID_PATTERN.fullmatch(requirement_key):
        raise ValueError(f"Invalid requirement_key: {requirement_key!r}")
    if not UUID_PATTERN.fullmatch(finding_key):
        raise ValueError(f"Invalid finding_key: {finding_key!r}")

    enriched["specification_id"] = specification_id
    enriched["requirement_id"] = requirement_id
    enriched["requirement_key"] = requirement_key
    enriched["finding_key"] = finding_key
    return enriched


def world_coordinate_aabb(
    model: ifcopenshell.file,
    global_id: str,
) -> Aabb:
    """Tessellate an IFC element and return its world-coordinate AABB."""

    if not IFC_GUID_PATTERN.fullmatch(global_id):
        raise ValueError(f"Invalid IFC GlobalId: {global_id!r}")
    element = model.by_guid(global_id)
    if element is None:
        raise ValueError(f"IFC element not found: {global_id}")

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    settings.set(settings.WELD_VERTICES, True)
    settings.set(settings.CONVERT_BACK_UNITS, False)
    shape = ifcopenshell.geom.create_shape(settings, element)
    coordinates = tuple(float(value) for value in shape.geometry.verts)

    if len(coordinates) < 3 or len(coordinates) % 3:
        raise ValueError(f"Element has no usable tessellated vertices: {global_id}")
    if not all(math.isfinite(value) for value in coordinates):
        raise ValueError(f"Element has non-finite geometry: {global_id}")

    axes = (
        coordinates[0::3],
        coordinates[1::3],
        coordinates[2::3],
    )
    minimum = tuple(min(axis) for axis in axes)
    maximum = tuple(max(axis) for axis in axes)
    return Aabb(minimum=minimum, maximum=maximum)


def camera_for_aabb(aabb: Aabb) -> Camera:
    """Build an isometric camera by solving every AABB corner constraint."""

    target = aabb.center
    if aabb.diagonal <= 1e-9:
        raise ValueError("Cannot construct a camera for a degenerate AABB")
    inverse_sqrt_three = 1.0 / math.sqrt(3.0)
    direction = (
        -inverse_sqrt_three,
        -inverse_sqrt_three,
        -inverse_sqrt_three,
    )
    inverse_sqrt_six = 1.0 / math.sqrt(6.0)
    up = (
        -inverse_sqrt_six,
        -inverse_sqrt_six,
        2.0 * inverse_sqrt_six,
    )
    right = _normalize(_cross(direction, up))
    vertical_tangent = math.tan(math.radians(60.0 / 2.0))
    aspect_ratio = 16.0 / 9.0
    margin = 1.10
    minimum_distance = 0.0
    for corner in _aabb_corners(aabb):
        offset = tuple(
            value - center
            for value, center in zip(corner, target, strict=True)
        )
        depth_offset = _dot(offset, direction)
        horizontal = abs(_dot(offset, right))
        vertical = abs(_dot(offset, up))
        required_depth = max(
            margin * vertical / vertical_tangent,
            margin * horizontal / (vertical_tangent * aspect_ratio),
        )
        minimum_distance = max(
            minimum_distance,
            required_depth - depth_offset,
        )
    distance = minimum_distance + max(aabb.diagonal * 0.01, 1e-6)
    position = tuple(
        coordinate - axis * distance
        for coordinate, axis in zip(target, direction, strict=True)
    )
    camera = Camera(
        position=position,
        direction=direction,
        up=up,
        target=target,
        aspect_ratio=aspect_ratio,
    )
    verify_camera_frames_aabb(aabb, camera, tolerance=1e-12)
    return camera


def _dot(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def _cross(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _normalize(
    vector: tuple[float, float, float],
) -> tuple[float, float, float]:
    length = math.sqrt(_dot(vector, vector))
    if length <= 1e-12:
        raise ValueError("A camera vector cannot be zero")
    return tuple(value / length for value in vector)


def _aabb_corners(aabb: Aabb) -> tuple[tuple[float, float, float], ...]:
    return tuple(itertools.product(*zip(aabb.minimum, aabb.maximum, strict=True)))


def verify_camera_frames_aabb(
    aabb: Aabb,
    camera: Camera,
    tolerance: float = 2e-6,
) -> None:
    """Project all eight corners and fail if any lies outside the view frustum."""

    direction = _normalize(camera.direction)
    up = _normalize(camera.up)
    if tolerance < 0 or not math.isfinite(tolerance):
        raise ValueError("Camera verification tolerance must be finite and non-negative")
    if abs(_dot(direction, up)) > tolerance:
        raise ValueError("Camera direction and up vectors are not orthogonal")
    right = _normalize(_cross(direction, up))
    tangent = math.tan(math.radians(camera.field_of_view / 2.0))
    for corner in _aabb_corners(aabb):
        relative = tuple(
            value - origin
            for value, origin in zip(corner, camera.position, strict=True)
        )
        depth = _dot(relative, direction)
        horizontal = abs(_dot(relative, right))
        vertical = abs(_dot(relative, up))
        if depth <= tolerance:
            raise ValueError("AABB corner is behind the BCF camera")
        if vertical > depth * tangent + tolerance:
            raise ValueError("AABB corner is outside the vertical camera frustum")
        if horizontal > depth * tangent * camera.aspect_ratio + tolerance:
            raise ValueError("AABB corner is outside the horizontal camera frustum")


def format_float(value: float) -> str:
    """Return a platform-stable decimal suitable for BCF XML and CSV."""

    rounded = round(float(value), 9)
    if rounded == 0:
        rounded = 0.0
    return f"{rounded:.9f}"


def xml_bytes(root: ET.Element) -> bytes:
    """Serialize an ElementTree with deterministic indentation and encoding."""

    ET.indent(root, space="  ")
    body = ET.tostring(
        root,
        encoding="utf-8",
        short_empty_elements=True,
    )
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + body + b"\n"


def validate_archive_name(name: str) -> None:
    """Reject traversal, ambiguous separators, and Windows-dangerous names."""

    if not name or "\x00" in name or "\\" in name or "//" in name:
        raise ValueError(f"Unsafe ZIP member name: {name!r}")
    is_directory = name.endswith("/")
    stripped_name = name[:-1] if is_directory else name
    if not stripped_name:
        raise ValueError(f"Unsafe ZIP member name: {name!r}")
    path = PurePosixPath(stripped_name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Unsafe ZIP member name: {name!r}")
    if ":" in path.parts[0]:
        raise ValueError(f"Unsafe ZIP member name: {name!r}")


def build_deterministic_zip(entries: Mapping[str, bytes]) -> bytes:
    """Create a safe byte-for-byte reproducible ZIP archive."""

    if not entries:
        raise ValueError("A BCF archive cannot be empty")
    normalized_names: set[str] = set()
    total_size = 0
    for name, data in entries.items():
        validate_archive_name(name)
        collision_key = name.casefold()
        if collision_key in normalized_names:
            raise ValueError(f"Case-insensitive duplicate ZIP member: {name}")
        normalized_names.add(collision_key)
        if not isinstance(data, bytes):
            raise TypeError(f"ZIP entry is not bytes: {name}")
        if len(data) > MAX_ENTRY_SIZE:
            raise ValueError(f"ZIP entry is too large: {name}")
        total_size += len(data)
    if len(entries) > MAX_ARCHIVE_ENTRIES or total_size > MAX_ARCHIVE_SIZE:
        raise ValueError("BCF archive exceeds safe generation limits")

    output = io.BytesIO()
    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_STORED,
        allowZip64=False,
    ) as archive:
        archive.comment = b""
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, FIXED_ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 0
            info.external_attr = 0x10 if name.endswith("/") else 0o600 << 16
            info.internal_attr = 0
            info.extra = b""
            info.comment = b""
            archive.writestr(info, entries[name])
    return output.getvalue()


def read_safe_zip(path: Path) -> dict[str, bytes]:
    """Read a small canonical BCF ZIP while rejecting common archive attacks."""

    if not path.is_file():
        raise FileNotFoundError(f"BCF archive not found: {path}")

    entries: dict[str, bytes] = {}
    seen_names: set[str] = set()
    total_size = 0
    with zipfile.ZipFile(path, mode="r") as archive:
        if archive.comment:
            raise ValueError("BCF archive comment is not allowed")
        infos = archive.infolist()
        if len(infos) > MAX_ARCHIVE_ENTRIES:
            raise ValueError("BCF archive contains too many entries")
        if [info.filename for info in infos] != sorted(
            info.filename for info in infos
        ):
            raise ValueError("BCF archive members are not canonically ordered")

        for info in infos:
            validate_archive_name(info.filename)
            collision_key = info.filename.casefold()
            if collision_key in seen_names:
                raise ValueError(
                    f"Duplicate or ambiguous ZIP member: {info.filename}"
                )
            seen_names.add(collision_key)
            if info.flag_bits & 0x1:
                raise ValueError(f"Encrypted ZIP member: {info.filename}")
            if info.compress_type != zipfile.ZIP_STORED:
                raise ValueError(
                    f"Non-canonical compression for ZIP member: {info.filename}"
                )
            if info.date_time != FIXED_ZIP_TIMESTAMP:
                raise ValueError(
                    f"Non-canonical timestamp for ZIP member: {info.filename}"
                )
            if info.extra or info.comment:
                raise ValueError(
                    f"Unexpected ZIP metadata for member: {info.filename}"
                )
            if info.create_system != 0:
                raise ValueError(f"Non-canonical ZIP host: {info.filename}")
            expected_attributes = 0x10 if info.is_dir() else 0o600 << 16
            if info.external_attr != expected_attributes:
                raise ValueError(f"Non-canonical ZIP attributes: {info.filename}")
            if info.file_size > MAX_ENTRY_SIZE:
                raise ValueError(f"ZIP member is too large: {info.filename}")
            if info.is_dir() and info.file_size != 0:
                raise ValueError(f"Non-empty ZIP directory: {info.filename}")
            if info.compress_size == 0:
                ratio = 1 if info.file_size == 0 else math.inf
            else:
                ratio = info.file_size / info.compress_size
            if ratio > MAX_COMPRESSION_RATIO:
                raise ValueError(f"Suspicious ZIP ratio: {info.filename}")
            total_size += info.file_size
            if total_size > MAX_ARCHIVE_SIZE:
                raise ValueError("BCF archive expands beyond the safe limit")
            data = archive.read(info)
            if len(data) != info.file_size:
                raise ValueError(f"Truncated ZIP member: {info.filename}")
            entries[info.filename] = data
    return entries


def parse_xml(data: bytes, source: str) -> ET.Element:
    """Parse bounded XML without permitting DTD/entity declarations."""

    upper = data.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise ValueError(f"DTD/entity declarations are forbidden in {source}")
    try:
        return ET.fromstring(data)
    except ET.ParseError as error:
        raise ValueError(f"Invalid XML in {source}: {error}") from error


def verify_schema_bundle(schema_dir: Path = SCHEMA_DIR) -> dict[str, str]:
    """Fail closed unless every official BCF XSD matches the pinned commit."""

    actual: dict[str, str] = {}
    for filename, expected_hash in OFFICIAL_SCHEMA_SHA256.items():
        path = schema_dir / filename
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Pinned BCF schema is missing or unsafe: {path}")
        digest = calculate_sha256(path)
        if digest != expected_hash:
            raise ValueError(
                f"Pinned BCF schema hash mismatch for {filename}: {digest}"
            )
        actual[filename] = digest
    return actual


def validate_xml_schemas(
    entries: Mapping[str, bytes],
    schema_dir: Path = SCHEMA_DIR,
) -> None:
    """Validate every recognized BCF XML payload against the pinned XSDs."""

    verify_schema_bundle(schema_dir)
    try:
        import xmlschema
    except ImportError as error:  # pragma: no cover - dependency gate
        raise RuntimeError("xmlschema is required for BCF validation") from error

    schemas = {
        name: xmlschema.XMLSchema(schema_dir / name)
        for name in (
            "documents.xsd",
            "extensions.xsd",
            "markup.xsd",
            "project.xsd",
            "version.xsd",
            "visinfo.xsd",
        )
    }

    for name, data in entries.items():
        if name == "bcf.version":
            schema_name = "version.xsd"
        elif name == "project.bcfp":
            schema_name = "project.xsd"
        elif name == "extensions.xml":
            schema_name = "extensions.xsd"
        elif name == "documents.xml":
            schema_name = "documents.xsd"
        elif name.endswith("/markup.bcf"):
            schema_name = "markup.xsd"
        elif name.endswith(".bcfv"):
            schema_name = "visinfo.xsd"
        else:
            continue
        try:
            schemas[schema_name].validate(data)
        except xmlschema.XMLSchemaValidationError as error:
            raise ValueError(
                f"BCF XSD validation failed for {name}: {error.reason}"
            ) from error


def repo_relative(path: Path, project_root: Path = PROJECT_ROOT) -> str:
    """Return a forward-slash repository-relative path or fail closed."""

    resolved = path.resolve()
    try:
        return resolved.relative_to(project_root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"Output must stay inside the repository: {path}") from error
