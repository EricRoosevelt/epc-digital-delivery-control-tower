"""Compatibility shim. The implementation lives in :mod:`epc_control_tower`.

This module was the identity kernel. It is now three lines of delegation,
because keeping a second copy of an identity derivation is how two copies come
to disagree — and an identity that disagrees with itself re-keys everything
downstream of it.

``build_finding_key`` deliberately resolves to the *frozen* derivation. Its
signature here is positional and keyed on ``model_id``, which is the shape the
published artifacts were built with; the current derivation keys on
``model_key`` and on a run identity that now folds in each checker's version.
Both compute the same function, so nothing about the algorithm is duplicated —
only which run identity is fed in differs, and this shim feeds in the old one.

Retires with the legacy adapters.
"""

from __future__ import annotations

import sys
from pathlib import Path

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    # Importable both as ``src.identity`` and, with ``src/`` on the path, as a
    # bare ``identity``. Both routes are in use and both must keep working.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from epc_control_tower.determinism import (  # noqa: E402
    canonical_json_sequence as canonical_json,
)
from epc_control_tower.identity import (  # noqa: E402
    IDENTITY_NAMESPACE,
    build_requirement_key,
    uuid5_from_values,
)
from epc_control_tower.legacy_identity import (  # noqa: E402
    legacy_finding_key as _legacy_finding_key,
)

__all__ = [
    "IDENTITY_NAMESPACE",
    "build_finding_key",
    "build_requirement_key",
    "canonical_json",
    "uuid5_from_values",
]


def build_finding_key(run_id, model_id, requirement_key, element_key):
    """Return the published key for one normalized IDS finding."""

    return _legacy_finding_key(
        run_id=run_id,
        model_id=model_id,
        requirement_key=requirement_key,
        element_key=element_key,
    )
