"""Byte-reproducible ZIP archives, and safe reading of them.

A BCF file is a ZIP, and a ZIP records a great deal that has nothing to do with
its contents: modification times, the host operating system, permission bits,
extra fields, the order members happen to be added in. Left alone, every one of
those makes the same logical archive come out as different bytes, which is the
end of any claim that an artifact is reproducible. Each is therefore pinned,
and the constants below are load-bearing rather than stylistic — changing any
one of them changes the published archive's SHA-256.

Reading is the same discipline pointed the other way. :func:`read_safe_zip`
re-asserts every one of those properties on the way in, so an archive that was
tampered with, rebuilt by a different tool, or crafted to be hostile does not
get read as if it were ours. Path traversal, case-colliding members, encryption,
non-stored compression and decompression-bomb ratios are all refused.

Ported unchanged from the pre-package layout.
"""

from __future__ import annotations

import io
import math
import zipfile
from collections.abc import Mapping
from pathlib import Path, PurePosixPath

__all__ = [
    "FIXED_ZIP_TIMESTAMP",
    "MAX_ARCHIVE_ENTRIES",
    "MAX_ARCHIVE_SIZE",
    "MAX_COMPRESSION_RATIO",
    "MAX_ENTRY_SIZE",
    "build_deterministic_zip",
    "read_safe_zip",
    "validate_archive_name",
]

#: The earliest timestamp the ZIP format can represent. Any real time would be
#: a wall-clock reading baked into a deterministic artifact.
FIXED_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

MAX_ARCHIVE_ENTRIES = 100
MAX_ENTRY_SIZE = 5 * 1024 * 1024
MAX_ARCHIVE_SIZE = 20 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100


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
        # Stored, not deflated: compression output depends on the zlib build,
        # so a compressed archive is not reproducible across machines.
        compression=zipfile.ZIP_STORED,
        allowZip64=False,
    ) as archive:
        archive.comment = b""
        # Sorted, so the archive does not record the order the caller happened
        # to build its entries in.
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
                raise ValueError(f"Duplicate or ambiguous ZIP member: {info.filename}")
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
                raise ValueError(f"Unexpected ZIP metadata for member: {info.filename}")
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
