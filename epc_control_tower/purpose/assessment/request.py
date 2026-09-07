"""What a caller must say before a verdict is a statement about anything.

ADR 0003 §2 fixes two coordinates and this module is both of them. Neither has a
default, and the absence of a default is the point of the module.

**The assessed scope is declared, never discovered.** It does not come from
which elements happen to carry a finding. Letting coverage define scope is
Checkpoint B case 4's trap: an ``IfcChimney`` no rule reaches would quietly
leave the scope instead of surfacing as an unevaluated element. So a scope is
element keys and model keys a caller wrote down, a ``model_key`` expands to
*every* element of that model version, and there is no constructor here that
takes a finding set.

**The model-version context names the artefacts the verdict is true of.** A
verdict is only ever true of the exact versions named; the same element keys
against a different context are a different assessment, never an update of an
existing one. The handover event is runtime data this repository does not hold,
so it is recorded exactly as supplied and nothing is derived from it — the date
in particular is a string that is carried, never parsed and never compared.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import PurposeAssessmentError

__all__ = [
    "AssessedScope",
    "AssessmentRequest",
    "HandoverEvent",
    "ModelVersion",
    "ModelVersionContext",
]


@dataclass(frozen=True, slots=True)
class ModelVersion:
    """One model at one content version.

    ``content_id`` is the content hash ``models.csv`` already carries. There is
    no issue status, revision, or suitability code in contract 1.6, and none is
    invented here.
    """

    model_key: str
    content_id: str


@dataclass(frozen=True, slots=True)
class HandoverEvent:
    """Who issued what to whom, at which milestone, on which date.

    Every field is recorded as supplied. ``date`` is never parsed into a point
    in time and never compared with a milestone: ADR 0003 §4.6 admits
    consequence *kinds* and forbids magnitudes, and a date this module knew how
    to subtract is the shortest path to a fabricated delay.
    """

    from_role: str
    to_role: str
    milestone: str
    date: str


@dataclass(frozen=True, slots=True)
class ModelVersionContext:
    producing: ModelVersion
    consuming: ModelVersion
    handover: HandoverEvent


@dataclass(frozen=True, slots=True)
class AssessedScope:
    """The caller's explicit declaration of which labour a verdict is about.

    A ``model_key`` here means every element in that model version, expanded
    from the element inventory — which is what makes an unevaluated element
    appear as a ``not-yet-evaluated`` subscope rather than disappear.
    """

    element_keys: tuple[str, ...] = ()
    model_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.element_keys and not self.model_keys:
            raise PurposeAssessmentError(
                "scope-declared-empty",
                "an assessed scope is a required input and is never defaulted to "
                "'whatever has findings'; declare at least one element_key or model_key",
            )

    def as_document(self) -> dict[str, list[str]]:
        """The scope exactly as declared, in a deterministic order.

        Sorted for the record and for the digest, never de-duplicated against
        the inventory: the request records the scope as declared, and the
        assessment resolves coverage *within* it.
        """

        return {
            "element_keys": sorted(self.element_keys),
            "model_keys": sorted(self.model_keys),
        }


@dataclass(frozen=True, slots=True)
class AssessmentRequest:
    """One ``{project, pack, direction, activities, scope, context}`` tuple.

    ``activity_ids`` are local ids within the named Pack; the compound
    ``pack_id::activity_id`` is what the record carries, because two Packs bound
    by one project may legally reuse a local id.
    """

    project_id: str
    pack_id: str
    pack_version: str
    direction_id: str
    activity_ids: tuple[str, ...]
    assessed_scope: AssessedScope
    model_version_context: ModelVersionContext
