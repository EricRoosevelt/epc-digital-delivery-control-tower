"""Compatibility shim. The implementation lives in :mod:`epc_control_tower`.

This module held about six hundred lines: deterministic ZIP construction, safe
archive reading, world-coordinate bounding boxes, camera solving, XML
serialisation, schema pinning, and four copies of a SHA-256 helper. All of it
now lives in ``epc_control_tower.bcf`` and ``epc_control_tower.determinism``,
split by concern so the rules that make an archive reproducible can be reviewed
without reading geometry code.

What remains here is the module's *interface*: the names the legacy scripts and
the pre-existing tests import, and the default arguments they rely on. Nothing
is reimplemented. A shim that reimplemented anything would be a second copy,
and a second copy of a determinism rule is a rule that will eventually be
enforced in one place and not the other.

Retires with the legacy adapters.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from epc_control_tower.bcf.archive import (  # noqa: E402
    FIXED_ZIP_TIMESTAMP,
    MAX_ARCHIVE_ENTRIES,
    MAX_ARCHIVE_SIZE,
    MAX_COMPRESSION_RATIO,
    MAX_ENTRY_SIZE,
    build_deterministic_zip,
    read_safe_zip,
    validate_archive_name,
)
from epc_control_tower.bcf.geometry import (  # noqa: E402
    IFC_GUID_PATTERN,
    Aabb,
    Camera,
    camera_for_aabb,
    verify_camera_frames_aabb,
    world_coordinate_aabb,
)
from epc_control_tower.bcf.schema import (  # noqa: E402
    OFFICIAL_SCHEMA_COMMIT,
    OFFICIAL_SCHEMA_SHA256,
    default_schema_dir,
    parse_xml,
    xml_bytes,
)
from epc_control_tower.bcf.schema import (  # noqa: E402
    validate_xml_schemas as _validate_xml_schemas,
)
from epc_control_tower.bcf.schema import (  # noqa: E402
    verify_schema_bundle as _verify_schema_bundle,
)
from epc_control_tower.determinism import (  # noqa: E402
    format_float,
    read_csv_rows,
    sha256_bytes as bytes_sha256,
    sha256_file as calculate_sha256,
    write_csv_bytes as _write_csv_bytes,
)
from epc_control_tower.exporters.legacy_contract import (  # noqa: E402
    ASSIGNEE,
    BCF_VERSION,
    CREATION_AUTHOR,
    FINDING_URN_PREFIX,
    FIXED_TIMESTAMP,
    PROJECT_GUID,
    PROJECT_NAME,
    UUID_PATTERN,
    enrich_finding_identity,
    split_specification,
)

SCHEMA_DIR = default_schema_dir(PROJECT_ROOT)

__all__ = [
    "ASSIGNEE",
    "BCF_VERSION",
    "CREATION_AUTHOR",
    "FINDING_URN_PREFIX",
    "FIXED_TIMESTAMP",
    "FIXED_ZIP_TIMESTAMP",
    "IFC_GUID_PATTERN",
    "MAX_ARCHIVE_ENTRIES",
    "MAX_ARCHIVE_SIZE",
    "MAX_COMPRESSION_RATIO",
    "MAX_ENTRY_SIZE",
    "OFFICIAL_SCHEMA_COMMIT",
    "OFFICIAL_SCHEMA_SHA256",
    "PROJECT_GUID",
    "PROJECT_NAME",
    "PROJECT_ROOT",
    "SCHEMA_DIR",
    "UUID_PATTERN",
    "Aabb",
    "Camera",
    "build_deterministic_zip",
    "bytes_sha256",
    "calculate_sha256",
    "camera_for_aabb",
    "enrich_finding_identity",
    "format_float",
    "parse_xml",
    "read_csv_rows",
    "read_safe_zip",
    "repo_relative",
    "split_specification",
    "validate_archive_name",
    "validate_xml_schemas",
    "verify_camera_frames_aabb",
    "verify_schema_bundle",
    "world_coordinate_aabb",
    "write_csv_bytes",
    "xml_bytes",
]


def write_csv_bytes(rows: Iterable[Mapping[str, object]], columns: list[str]) -> bytes:
    """Serialize rows using the repository's deterministic CSV convention."""

    return _write_csv_bytes(rows, columns)


def verify_schema_bundle(schema_dir: Path = SCHEMA_DIR) -> dict[str, str]:
    """Fail closed unless every official BCF XSD matches the pinned commit."""

    return _verify_schema_bundle(schema_dir)


def validate_xml_schemas(
    entries: Mapping[str, bytes],
    schema_dir: Path = SCHEMA_DIR,
) -> None:
    """Validate every recognized BCF XML payload against the pinned XSDs."""

    _validate_xml_schemas(entries, schema_dir)


def repo_relative(path: Path, project_root: Path = PROJECT_ROOT) -> str:
    """Return a forward-slash repository-relative path or fail closed."""

    resolved = path.resolve()
    try:
        return resolved.relative_to(project_root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError(f"Output must stay inside the repository: {path}") from error
