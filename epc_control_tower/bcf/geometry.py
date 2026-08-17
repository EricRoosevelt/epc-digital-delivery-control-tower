"""Bounding boxes and the cameras that frame them.

A BCF viewpoint is only useful if opening it actually shows the element the
topic is about. "Only useful" is doing real work there: a viewpoint that frames
nothing is worse than no viewpoint, because it looks like evidence.

So the camera is *solved* rather than guessed. Every one of the eight corners
of the element's bounding box imposes a minimum viewing distance, the largest
of those wins, and :func:`verify_camera_frames_aabb` then re-projects all eight
corners and refuses a camera that leaves any of them outside the frustum. The
self-check runs at a tolerance of 1e-12 — far tighter than the 2e-6 a reader
might be offered — because at construction time the answer should be exact, and
a loose tolerance would hide an error in the solve rather than in the input.

Ported from the pre-package layout with its arithmetic unchanged. The constants
here (the isometric direction, the 1.10 margin, the 60-degree field of view)
determine published viewpoint bytes; they are not free parameters.
"""

from __future__ import annotations

import itertools
import math
import re
from dataclasses import dataclass

import ifcopenshell
import ifcopenshell.geom

__all__ = [
    "IFC_GUID_PATTERN",
    "Aabb",
    "Camera",
    "camera_for_aabb",
    "verify_camera_frames_aabb",
    "world_coordinate_aabb",
]

IFC_GUID_PATTERN = re.compile(r"^[0-9A-Za-z_$]{22}$")

Vector = tuple[float, float, float]


@dataclass(frozen=True)
class Aabb:
    """A world-coordinate axis-aligned bounding box in metres."""

    minimum: Vector
    maximum: Vector

    @property
    def center(self) -> Vector:
        return tuple(
            (lower + upper) / 2.0
            for lower, upper in zip(self.minimum, self.maximum, strict=True)
        )

    @property
    def diagonal(self) -> float:
        return math.sqrt(
            sum(
                (upper - lower) ** 2
                for lower, upper in zip(self.minimum, self.maximum, strict=True)
            )
        )


@dataclass(frozen=True)
class Camera:
    """A deterministic perspective camera aimed at an AABB centre."""

    position: Vector
    direction: Vector
    up: Vector
    target: Vector
    field_of_view: float = 60.0
    aspect_ratio: float = 16.0 / 9.0


def _dot(left: Vector, right: Vector) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def _cross(left: Vector, right: Vector) -> Vector:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _normalize(vector: Vector) -> Vector:
    length = math.sqrt(_dot(vector, vector))
    if length <= 1e-12:
        raise ValueError("A camera vector cannot be zero")
    return tuple(value / length for value in vector)


def _aabb_corners(aabb: Aabb) -> tuple[Vector, ...]:
    return tuple(itertools.product(*zip(aabb.minimum, aabb.maximum, strict=True)))


def world_coordinate_aabb(model: ifcopenshell.file, global_id: str) -> Aabb:
    """Tessellate one IFC element and return its world-coordinate AABB.

    World coordinates rather than local: a viewpoint has to place the camera in
    the same space the viewer's model is in, and an element's own placement is
    exactly the part that would be lost.
    """

    if not IFC_GUID_PATTERN.fullmatch(global_id):
        raise ValueError(f"Invalid IFC GlobalId: {global_id!r}")
    element = model.by_guid(global_id)
    if element is None:
        raise ValueError(f"IFC element not found: {global_id}")

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    settings.set(settings.WELD_VERTICES, True)
    settings.set(settings.CONVERT_BACK_UNITS, False)
    shape = ifcopenshell.geom.create_shape(settings, element)
    coordinates = tuple(float(value) for value in shape.geometry.verts)

    if len(coordinates) < 3 or len(coordinates) % 3:
        raise ValueError(f"Element has no usable tessellated vertices: {global_id}")
    if not all(math.isfinite(value) for value in coordinates):
        raise ValueError(f"Element has non-finite geometry: {global_id}")

    axes = (coordinates[0::3], coordinates[1::3], coordinates[2::3])
    return Aabb(
        minimum=tuple(min(axis) for axis in axes),
        maximum=tuple(max(axis) for axis in axes),
    )


def camera_for_aabb(aabb: Aabb) -> Camera:
    """Build an isometric camera by solving every AABB corner constraint."""

    target = aabb.center
    if aabb.diagonal <= 1e-9:
        raise ValueError("Cannot construct a camera for a degenerate AABB")

    inverse_sqrt_three = 1.0 / math.sqrt(3.0)
    direction = (-inverse_sqrt_three, -inverse_sqrt_three, -inverse_sqrt_three)
    inverse_sqrt_six = 1.0 / math.sqrt(6.0)
    up = (-inverse_sqrt_six, -inverse_sqrt_six, 2.0 * inverse_sqrt_six)
    right = _normalize(_cross(direction, up))

    vertical_tangent = math.tan(math.radians(60.0 / 2.0))
    aspect_ratio = 16.0 / 9.0
    margin = 1.10

    minimum_distance = 0.0
    for corner in _aabb_corners(aabb):
        offset = tuple(
            value - center for value, center in zip(corner, target, strict=True)
        )
        depth_offset = _dot(offset, direction)
        horizontal = abs(_dot(offset, right))
        vertical = abs(_dot(offset, up))
        required_depth = max(
            margin * vertical / vertical_tangent,
            margin * horizontal / (vertical_tangent * aspect_ratio),
        )
        minimum_distance = max(minimum_distance, required_depth - depth_offset)

    distance = minimum_distance + max(aabb.diagonal * 0.01, 1e-6)
    position = tuple(
        coordinate - axis * distance
        for coordinate, axis in zip(target, direction, strict=True)
    )
    camera = Camera(
        position=position,
        direction=direction,
        up=up,
        target=target,
        aspect_ratio=aspect_ratio,
    )
    # Tight on purpose: at construction the solve should be exact, and a loose
    # tolerance here would hide a mistake in the arithmetic rather than in the
    # geometry it was given.
    verify_camera_frames_aabb(aabb, camera, tolerance=1e-12)
    return camera


def verify_camera_frames_aabb(
    aabb: Aabb,
    camera: Camera,
    tolerance: float = 2e-6,
) -> None:
    """Project all eight corners and fail if any lies outside the view frustum."""

    direction = _normalize(camera.direction)
    up = _normalize(camera.up)
    if tolerance < 0 or not math.isfinite(tolerance):
        raise ValueError("Camera verification tolerance must be finite and non-negative")
    if abs(_dot(direction, up)) > tolerance:
        raise ValueError("Camera direction and up vectors are not orthogonal")

    right = _normalize(_cross(direction, up))
    tangent = math.tan(math.radians(camera.field_of_view / 2.0))
    for corner in _aabb_corners(aabb):
        relative = tuple(
            value - origin
            for value, origin in zip(corner, camera.position, strict=True)
        )
        depth = _dot(relative, direction)
        horizontal = abs(_dot(relative, right))
        vertical = abs(_dot(relative, up))
        if depth <= tolerance:
            raise ValueError("AABB corner is behind the BCF camera")
        if vertical > depth * tangent + tolerance:
            raise ValueError("AABB corner is outside the vertical camera frustum")
        if horizontal > depth * tangent * camera.aspect_ratio + tolerance:
            raise ValueError("AABB corner is outside the horizontal camera frustum")
