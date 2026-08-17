"""Primitives every deterministic product depends on.

These were previously copied into four modules, which is how the same helper
came to exist in three verbatim copies plus a fourth variant that read whole
files into memory. One definition each, here.

The rules enforced by this module:

* Hash file bytes, never decoded text, so encoding and newline translation
  cannot affect a digest.
* CSV is UTF-8 with a BOM and ``\\n`` line endings, so the same bytes appear on
  every platform and Excel and Power BI still read it.
* JSON is sorted, unescaped, and newline-terminated.
* Floats are rounded to nine decimals with negative zero normalised, because
  ``-0.0`` and ``0.0`` format differently but mean the same thing.
* Writes are atomic, so an interrupted run cannot leave a half-written
  artifact that a later run would treat as input.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

__all__ = [
    "CSV_BOM",
    "atomic_write_bytes",
    "canonical_json_document",
    "canonical_json_sequence",
    "format_float",
    "json_bytes",
    "read_csv_rows",
    "sha256_bytes",
    "sha256_file",
    "sort_rows",
    "write_csv_bytes",
]

CSV_BOM = b"\xef\xbb\xbf"

_CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 digest for one file.

    Read in binary and in chunks: binary so that text encoding and newline
    translation cannot change the digest, chunked so a large IFC never has to
    be resident all at once.
    """

    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(_CHUNK_SIZE), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Return a lowercase SHA-256 digest for an in-memory artifact."""

    return hashlib.sha256(data).hexdigest()


def canonical_json_sequence(values: Iterable[object]) -> str:
    """Serialise an ordered payload without incidental whitespace.

    Order is significant here — this is used to build identity keys, where
    reordering the inputs must produce a different key.
    """

    return json.dumps(list(values), ensure_ascii=False, separators=(",", ":"))


def canonical_json_document(document: Mapping[str, object]) -> str:
    """Serialise a mapping with sorted keys and no incidental whitespace.

    Order is *not* significant here, so keys are sorted: the same logical
    payload must hash identically however the mapping was assembled.
    """

    return json.dumps(
        document,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def json_bytes(document: object) -> bytes:
    """Serialise a JSON artifact deterministically, with a trailing newline."""

    text = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True)
    return (text + "\n").encode("utf-8")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """Read a CSV while preserving the literal string ``N/A``.

    ``csv`` is used rather than pandas precisely because pandas would coerce
    ``N/A`` to a missing value, and ``N/A`` is a meaningful status here.
    """

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv_bytes(
    rows: Iterable[Mapping[str, object]],
    columns: Sequence[str],
) -> bytes:
    """Serialise rows to the repository's deterministic CSV convention."""

    text_stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        text_stream,
        fieldnames=list(columns),
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return CSV_BOM + text_stream.getvalue().encode("utf-8")


def sort_rows(
    rows: Iterable[Mapping[str, object]],
    columns: Sequence[str],
) -> list[dict[str, object]]:
    """Sort rows by the given columns, comparing as text.

    Comparing as text keeps the ordering stable regardless of whether a value
    arrived as an int, a float, or a string.
    """

    return sorted(
        (dict(row) for row in rows),
        key=lambda row: tuple(str(row[column]) for column in columns),
    )


def format_float(value: float) -> str:
    """Return a platform-stable decimal suitable for BCF XML and CSV."""

    rounded = round(float(value), 9)
    if rounded == 0:
        rounded = 0.0
    return f"{rounded:.9f}"


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write bytes so that readers never observe a partial artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.tmp"
    temporary.write_bytes(data)
    os.replace(temporary, path)
