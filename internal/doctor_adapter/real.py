"""The real entry: the shipped project, the shipped Pack library, the validated run.

Its envelope is always ``mode = "real"``, whatever the outcome. There is no
parameter through which composed inputs, an Overlay or determinations could be
supplied, so a refused real run cannot be turned into a fixture one here — the
only way to see fixture policy is to call the fixture entry, and then the
envelope says so.
"""

from __future__ import annotations

from epc_control_tower.purpose import (
    AssessmentRequest,
    assess_purpose,
    compose_purpose_inputs,
    discover_purpose_packs,
    load_project_overlay,
    load_purpose_packs,
)

from .envelope import PROJECT_ROOT, REAL, build_envelope
from .validated import requirement_keys_by_ruleset, validated_facts

__all__ = ["real_envelope"]


def real_envelope(request: AssessmentRequest) -> dict[str, object]:
    """Assess ``request`` against the project's own manifest, or return its refusal."""

    manifest = PROJECT_ROOT / "projects" / request.project_id / "project.toml"
    composed = compose_purpose_inputs(
        project_id=request.project_id,
        overlay=load_project_overlay(manifest),
        packs=load_purpose_packs(discover_purpose_packs(PROJECT_ROOT / "purpose-packs")),
        requirement_keys_by_ruleset=requirement_keys_by_ruleset(),
        source=manifest,
    )
    facts = validated_facts(request.project_id)
    return build_envelope(
        REAL,
        lambda: assess_purpose(request=request, composed=composed, facts=facts),
    )
