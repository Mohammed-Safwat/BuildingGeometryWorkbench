"""Functions for constructing building floor geometry."""

from shapely.geometry import Polygon

from buildingpipeline.domain.models import FloorModel
from buildingpipeline.geometry.models import FloorGeometry, OpeningGeometry


def create_floor_geometry(
    floor: FloorModel,
    openings: tuple[OpeningGeometry, ...] = (),
) -> FloorGeometry:
    """Create the 2D slab geometry for a building floor.

    Args:
        floor: Building floor model containing dimensions and elevation.
        openings: Rectangular openings to subtract from the slab.

    Returns:
        FloorGeometry containing the slab polygon and its openings.

    Raises:
        ValueError: If an opening lies outside the slab or is invalid.
    """
    exterior = [
        (0.0, 0.0),
        (floor.length, 0.0),
        (floor.length, floor.width),
        (0.0, floor.width),
    ]

    interior_rings = []

    for opening in openings:
        if (
            opening.min_x < 0
            or opening.min_y < 0
            or opening.max_x > floor.length
            or opening.max_y > floor.width
        ):
            raise ValueError(
                f"Opening '{opening.opening_id}' lies outside floor "
                f"'{floor.floor_id}'."
            )

        interior_rings.append(
            [
                (opening.min_x, opening.min_y),
                (opening.max_x, opening.min_y),
                (opening.max_x, opening.max_y),
                (opening.min_x, opening.max_y),
            ]
        )

    polygon = Polygon(exterior, holes=interior_rings)

    if not polygon.is_valid:
        raise ValueError(
            f"Openings produce invalid geometry for floor '{floor.floor_id}'."
        )

    return FloorGeometry(
        floor_id=floor.floor_id,
        elevation=floor.elevation,
        slab_thickness=floor.slab_thickness,
        polygon=polygon,
    )