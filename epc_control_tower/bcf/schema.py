"""BCF XML: deterministic serialisation, and validation against pinned schemas.

The XSDs are buildingSMART's own, vendored verbatim at a recorded commit. They
are verified by hash before any validation runs, so "this file validates
against BCF 3.0" means the published schema and not whatever happens to be in
the directory. That check fails closed: a missing, edited, or symlinked schema
stops the run rather than downgrading it to no validation at all, which is the
failure mode that would otherwise go unnoticed for months.

:func:`parse_xml` refuses DTD and entity declarations outright. Nothing this
project reads has any use for them, and accepting them is how an XML reader
becomes a file-disclosure primitive.

:func:`xml_bytes` pins indentation, empty-element form and the declaration, so
that the same document always serialises to the same bytes.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from xml.etree import ElementTree as ET

from ..determinism import sha256_file

__all__ = [
    "OFFICIAL_SCHEMA_COMMIT",
    "OFFICIAL_SCHEMA_SHA256",
    "default_schema_dir",
    "parse_xml",
    "validate_xml_schemas",
    "verify_schema_bundle",
    "xml_bytes",
]

#: The buildingSMART/BCF-XML commit the vendored schemas were taken from.
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

#: Which schema validates which archive member.
_SCHEMA_FOR_MEMBER = {
    "bcf.version": "version.xsd",
    "project.bcfp": "project.xsd",
    "extensions.xml": "extensions.xsd",
    "documents.xml": "documents.xsd",
}

_VALIDATING_SCHEMAS = (
    "documents.xsd",
    "extensions.xsd",
    "markup.xsd",
    "project.xsd",
    "version.xsd",
    "visinfo.xsd",
)


def default_schema_dir(repository_root: Path) -> Path:
    """Where the vendored buildingSMART BCF 3.0 schemas live."""

    return (
        repository_root
        / "third_party"
        / "buildingsmart"
        / "bcf-xml"
        / "3.0"
        / "Schemas"
    )


def xml_bytes(root: ET.Element) -> bytes:
    """Serialize an ElementTree with deterministic indentation and encoding."""

    ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="utf-8", short_empty_elements=True)
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + body + b"\n"


def parse_xml(data: bytes, source: str) -> ET.Element:
    """Parse bounded XML without permitting DTD/entity declarations."""

    upper = data.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise ValueError(f"DTD/entity declarations are forbidden in {source}")
    try:
        return ET.fromstring(data)
    except ET.ParseError as error:
        raise ValueError(f"Invalid XML in {source}: {error}") from error


def verify_schema_bundle(schema_dir: Path) -> dict[str, str]:
    """Fail closed unless every official BCF XSD matches the pinned commit."""

    actual: dict[str, str] = {}
    for filename, expected_hash in OFFICIAL_SCHEMA_SHA256.items():
        path = schema_dir / filename
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Pinned BCF schema is missing or unsafe: {path}")
        digest = sha256_file(path)
        if digest != expected_hash:
            raise ValueError(
                f"Pinned BCF schema hash mismatch for {filename}: {digest}"
            )
        actual[filename] = digest
    return actual


def validate_xml_schemas(entries: Mapping[str, bytes], schema_dir: Path) -> None:
    """Validate every recognized BCF XML payload against the pinned XSDs."""

    verify_schema_bundle(schema_dir)
    try:
        import xmlschema
    except ImportError as error:  # pragma: no cover - dependency gate
        raise RuntimeError("xmlschema is required for BCF validation") from error

    schemas = {
        name: xmlschema.XMLSchema(schema_dir / name) for name in _VALIDATING_SCHEMAS
    }

    for name, data in entries.items():
        schema_name = _SCHEMA_FOR_MEMBER.get(name)
        if schema_name is None:
            if name.endswith("/markup.bcf"):
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
