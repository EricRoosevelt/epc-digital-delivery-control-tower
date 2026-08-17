"""Inventory: source models become a federated element register.

The one decision worth spelling out is the join key. A bare IFC ``GlobalId`` is
not unique across the discipline files that describe a single building — the
shipped fixture has 39 element occurrences but only 32 distinct GlobalIds,
because four GUID groups recur across files. Joining on ``GlobalId`` would
therefore silently merge unrelated elements, so every cross-model join goes
through ``element_key``, which carries the model that owns it.

Only property sets are counted, not quantity sets: ``pset_count`` is a measure
of how much descriptive data an element carries, and mixing in derived
quantities would blur that.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path

import ifcopenshell
import ifcopenshell.util.element

from ..domain import Element, Model, make_element_key

__all__ = ["inventory", "inventory_one_model"]


def _text(value: object) -> str:
    """Normalise an optional IFC attribute to text.

    IFC leaves many attributes optional, and the difference between absent and
    empty is not one this register carries.
    """

    return "" if value is None else str(value)


def inventory_one_model(model: Model, ifc_path: Path) -> tuple[Element, ...]:
    """Extract every ``IfcElement`` occurrence from one source model."""

    opened = ifcopenshell.open(str(ifc_path))
    elements: list[Element] = []

    for entity in opened.by_type("IfcElement"):
        global_id = getattr(entity, "GlobalId", None)
        if not global_id:
            # element_key depends on GlobalId, so a missing one cannot be
            # papered over with a placeholder without corrupting every join.
            raise ValueError(
                f"Element #{entity.id()} in {ifc_path.name} has no GlobalId"
            )

        storey = ifcopenshell.util.element.get_container(
            entity, ifc_class="IfcBuildingStorey"
        )
        psets = ifcopenshell.util.element.get_psets(entity, psets_only=True)

        elements.append(
            Element(
                element_key=make_element_key(model.model_key, global_id),
                model_key=model.model_key,
                global_id=global_id,
                ifc_class=entity.is_a(),
                name=_text(getattr(entity, "Name", None)),
                storey=_text(getattr(storey, "Name", None) if storey else None),
                pset_count=len(psets),
            )
        )

    return tuple(elements)


def inventory(
    models: Sequence[Model],
    paths: dict[str, Path],
) -> tuple[Element, ...]:
    """Build the federated element register for a set of models.

    ``paths`` maps ``model_key`` to the file on disk. Passing paths in rather
    than deriving them keeps this stage independent of how projects lay out
    their storage.
    """

    elements: list[Element] = []
    for model in models:
        try:
            path = paths[model.model_key]
        except KeyError:
            raise KeyError(f"No file path supplied for model {model.model_key!r}") from None
        elements.extend(inventory_one_model(model, path))

    _require_unique_element_keys(elements)
    elements.sort(key=lambda element: (element.model_key, element.element_key))
    return tuple(elements)


def _require_unique_element_keys(elements: Iterable[Element]) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for element in elements:
        if element.element_key in seen:
            duplicates.add(element.element_key)
        seen.add(element.element_key)
    if duplicates:
        raise ValueError(f"Duplicate element_key values: {sorted(duplicates)}")
