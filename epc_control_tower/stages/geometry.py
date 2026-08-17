"""Geometry: bounding boxes for the elements something needs to point at.

This stage exists so that no exporter has to open an IFC file. An exporter that
reopened the source model would be reaching around the bundle boundary, and
that boundary is the whole reason two runs over unchanged inputs can be
expected to produce identical bytes.

It is deliberately selective. Tessellating an element is expensive and most
elements are never the subject of a viewpoint, so the caller says which keys it
needs rather than the stage computing everything on the chance somebody wants
it.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import ifcopenshell

from ..bcf.geometry import world_coordinate_aabb
from ..domain import Element, ElementGeometry

__all__ = ["compute_geometry"]


def compute_geometry(
    element_keys: Sequence[str],
    *,
    elements: Sequence[Element],
    model_paths: dict[str, Path],
) -> tuple[ElementGeometry, ...]:
    """Return the world-coordinate AABB of each requested element.

    ``model_paths`` maps ``model_key`` to the IFC file on disk. Each file is
    opened at most once however many of its elements are asked for.
    """

    wanted = sorted(set(element_keys))
    if not wanted:
        return ()

    by_key = {element.element_key: element for element in elements}
    opened: dict[str, ifcopenshell.file] = {}
    computed: list[ElementGeometry] = []

    for element_key in wanted:
        element = by_key.get(element_key)
        if element is None:
            raise KeyError(f"Cannot compute geometry for unknown element: {element_key}")

        if element.model_key not in opened:
            path = model_paths.get(element.model_key)
            if path is None:
                raise KeyError(
                    f"No file path supplied for model {element.model_key!r}"
                )
            opened[element.model_key] = ifcopenshell.open(str(path))

        aabb = world_coordinate_aabb(opened[element.model_key], element.global_id)
        computed.append(
            ElementGeometry(
                element_key=element_key,
                aabb_min=tuple(aabb.minimum),
                aabb_max=tuple(aabb.maximum),
            )
        )

    return tuple(computed)
