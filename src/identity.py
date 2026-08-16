import json
import uuid


IDENTITY_NAMESPACE = uuid.UUID(
    "7611c2a0-c29a-50fa-b00d-5058d25a41d3"
)


def canonical_json(values):
    """Serialize an ordered identity payload without incidental whitespace."""

    return json.dumps(
        list(values),
        ensure_ascii=False,
        separators=(",", ":"),
    )


def uuid5_from_values(identity_type, values, version=1):
    """Build a stable lowercase UUIDv5 from a typed canonical JSON payload."""

    name = (
        f"{identity_type}:v{version}:"
        f"{canonical_json(values)}"
    )
    return str(uuid.uuid5(IDENTITY_NAMESPACE, name))


def build_requirement_key(specification_id, requirement_id):
    """Return the stable key for one requirement within an IDS specification."""

    return uuid5_from_values(
        "requirement",
        [specification_id, requirement_id],
    )


def build_finding_key(
    run_id,
    model_id,
    requirement_key,
    element_key,
):
    """Return the stable key for one normalized IDS finding."""

    return uuid5_from_values(
        "finding",
        [
            run_id,
            model_id,
            requirement_key,
            element_key or "",
        ],
    )
