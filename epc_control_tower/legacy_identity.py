"""Frozen reproductions of the pre-split identity derivations.

**Do not extend, refactor, or "improve" anything in this module.** Its entire
job is to reproduce identity values that were already published, byte for
byte, so that the legacy adapters can keep emitting the artifacts the tracked
Power BI project and the committed evidence manifest were built against.

Two derivations changed when run identity was split three ways, and only two:

``legacy_run_id``
    The old single ``run_id``. Hashed the IDS document and the model contents
    with an ad-hoc newline-delimited byte stream. Superseded by
    :func:`~.identity.build_validation_run_id`, which hashes a canonical
    document and also folds in checker versions and configuration.

``legacy_finding_key``
    Keyed on the old ``run_id`` and on ``model_id``. Superseded by
    :func:`~.identity.build_finding_key`, which keys on ``validation_run_id``
    and ``model_key``.

Everything else — requirement keys, BCF topic, viewpoint, event and project
GUIDs — derives from inputs the split did not touch, so those functions live
in :mod:`~.identity` and are shared rather than duplicated here.

This module retires together with the legacy adapters.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable

from .identity import uuid5_from_values

__all__ = [
    "LEGACY_RUN_ID",
    "legacy_bcf_project_guid",
    "legacy_finding_key",
    "legacy_run_id",
    "legacy_topic_event_id",
    "legacy_topic_guid",
    "legacy_viewpoint_guid",
]

#: The published run identity of the v1.0.0 fixture. Present so tests can state
#: the expected value without recomputing it from the thing under test.
LEGACY_RUN_ID = "ids-v0.1-8706ef58303bfd11"


def legacy_run_id(
    *,
    ids_version: str,
    ids_sha256: str,
    models: Iterable[tuple[str, str]],
) -> str:
    """Reproduce the pre-split ``run_id``.

    ``models`` is an iterable of ``(model_id, content_sha256)``, sorted here by
    ``model_id`` exactly as the original did.

    The byte stream is reproduced verbatim, trailing newlines and all. It is
    not a canonical-JSON document and must not be turned into one.
    """

    hasher = hashlib.sha256()
    hasher.update(f"ids:{ids_sha256}\n".encode("utf-8"))
    for model_id, content_sha256 in sorted(models):
        hasher.update(f"{model_id}:{content_sha256}\n".encode("utf-8"))
    return f"ids-v{ids_version}-{hasher.hexdigest()[:16]}"


def legacy_finding_key(
    *,
    run_id: str,
    model_id: str,
    requirement_key: str,
    element_key: str,
) -> str:
    """Reproduce the pre-split ``finding_key``."""

    return uuid5_from_values(
        "finding",
        [run_id, model_id, requirement_key, element_key or ""],
    )


def legacy_topic_guid(element_key: str) -> str:
    """One BCF topic per issue element."""

    return uuid5_from_values("bcf-topic", [element_key])


def legacy_viewpoint_guid(topic_guid: str) -> str:
    """One viewpoint per topic."""

    return uuid5_from_values("bcf-viewpoint", [topic_guid])


def legacy_topic_event_id(topic_guid: str) -> str:
    """The single ``topic_created`` event the legacy workflow emits."""

    return uuid5_from_values("bcf-topic-event", [topic_guid, "created"])


def legacy_bcf_project_guid(project_name: str) -> str:
    """The BCF project GUID, derived from the project name."""

    return uuid5_from_values("bcf-project", [project_name])
