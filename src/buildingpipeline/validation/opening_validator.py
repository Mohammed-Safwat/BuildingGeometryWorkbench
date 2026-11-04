"""Validation functions for floor openings."""

from itertools import combinations

from shapely.geometry import box

from buildingpipeline.geometry.models import FloorGeometry, OpeningGeometry
from buildingpipeline.validation.models import (
    ValidationIssue,
    ValidationSeverity,
)


def validate_openings(
    floor: FloorGeometry,
    openings: tuple[OpeningGeometry, ...],
) -> tuple[ValidationIssue, ...]:
    """Validate opening geometry against a floor slab.

    Checks that every opening is valid and completely covered by the
    floor polygon. Also detects overlapping openings.

    Args:
        floor: Floor geometry containing the slab polygon.
        openings: Opening geometries to validate.

    Returns:
        A tuple of validation issues. An empty tuple means all openings
        passed validation.

    Raises:
        TypeError: If the floor or openings have invalid types.
    """
    if not isinstance(floor, FloorGeometry):
        raise TypeError("floor must be a FloorGeometry.")

    if not isinstance(openings, tuple):
        raise TypeError("openings must be a tuple.")

    if not all(isinstance(opening, OpeningGeometry) for opening in openings):
        raise TypeError("Every opening must be an OpeningGeometry.")

    issues: list[ValidationIssue] = []
    opening_polygons = {
        opening.opening_id: box(
            opening.min_x,
            opening.min_y,
            opening.max_x,
            opening.max_y,
        )
        for opening in openings
    }

    for opening in openings:
        opening_polygon = opening_polygons[opening.opening_id]

        if opening_polygon.is_empty or not opening_polygon.is_valid:
            issues.append(
                ValidationIssue(
                    issue_code="OPENING_INVALID",
                    severity=ValidationSeverity.ERROR,
                    message=(
                        f"Opening {opening.opening_id} on {floor.floor_id} "
                        "has invalid geometry."
                    ),
                    element_id=opening.opening_id,
                    floor_id=floor.floor_id,
                )
            )
            continue

        if not floor.polygon.covers(opening_polygon):
            issues.append(
                ValidationIssue(
                    issue_code="OPENING_OUTSIDE_SLAB",
                    severity=ValidationSeverity.ERROR,
                    message=(
                        f"Opening {opening.opening_id} is not completely "
                        f"inside the slab boundary of {floor.floor_id}."
                    ),
                    element_id=opening.opening_id,
                    floor_id=floor.floor_id,
                )
            )

    for first, second in combinations(openings, 2):
        first_polygon = opening_polygons[first.opening_id]
        second_polygon = opening_polygons[second.opening_id]

        if first_polygon.intersection(second_polygon).area > 0:
            issues.append(
                ValidationIssue(
                    issue_code="OPENINGS_OVERLAP",
                    severity=ValidationSeverity.ERROR,
                    message=(
                        f"Opening {first.opening_id} overlaps opening "
                        f"{second.opening_id} on {floor.floor_id}."
                    ),
                    element_id=second.opening_id,
                    floor_id=floor.floor_id,
                )
            )

    return tuple(issues)
