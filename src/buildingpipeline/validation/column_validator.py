"""Validation functions for building columns."""

from shapely.geometry import Polygon, box

from buildingpipeline.domain.models import BuildingModel, ColumnModel
from buildingpipeline.geometry.building_geometry import create_building_geometry
from buildingpipeline.validation.models import (
    ValidationIssue,
    ValidationSeverity,
)


def _create_column_polygon(column: ColumnModel) -> Polygon:
    """Create a rectangular polygon representing a column footprint.

    Args:
        column: Column model.

    Returns:
        A Shapely polygon representing the column footprint.
    """
    half_width = column.width / 2
    half_depth = column.depth / 2

    return box(
        column.x - half_width,
        column.y - half_depth,
        column.x + half_width,
        column.y + half_depth,
    )


def validate_column_boundaries(
    building: BuildingModel,
) -> tuple[ValidationIssue, ...]:
    """Validate that every column footprint is covered by its floor polygon.

    Args:
        building: Building model to validate.

    Returns:
        A tuple containing column boundary issues.
    """
    if not isinstance(building, BuildingModel):
        raise TypeError("Building must be a BuildingModel.")

    building_geometry = create_building_geometry(building)
    geometry_by_floor = {
        floor.floor_id: floor
        for floor in building_geometry.floors
    }

    issues: list[ValidationIssue] = []

    for floor in building.floors:
        floor_geometry = geometry_by_floor[floor.floor_id]

        for column in floor.columns:
            column_polygon = _create_column_polygon(column)

            if not floor_geometry.polygon.covers(column_polygon):
                issues.append(
                    ValidationIssue(
                        issue_code="COLUMN_OUTSIDE_FLOOR",
                        severity=ValidationSeverity.ERROR,
                        message=(
                            f"Column {column.column_id} on {floor.floor_id} "
                            "is not completely covered by the floor boundary."
                        ),
                        element_id=column.column_id,
                        floor_id=floor.floor_id,
                    )
                )

    return tuple(issues)


def _columns_overlap(
    first: ColumnModel,
    second: ColumnModel,
) -> bool:
    """Return whether two column footprints overlap with positive area.

    Args:
        first: First column.
        second: Second column.

    Returns:
        True when the column footprints have positive-area overlap.
    """
    first_polygon = _create_column_polygon(first)
    second_polygon = _create_column_polygon(second)

    return first_polygon.intersection(second_polygon).area > 0


def validate_column_support(
    building: BuildingModel,
) -> tuple[ValidationIssue, ...]:
    """Validate column support between consecutive building floors.

    Ground-floor columns are assumed to be supported by the foundation.
    Every column on an upper floor must overlap at least one column on the
    immediately lower floor.

    Args:
        building: Building model containing floors and columns.

    Returns:
        A tuple containing unsupported-column issues.
    """
    if not isinstance(building, BuildingModel):
        raise TypeError("Building must be a BuildingModel.")

    floors = sorted(building.floors, key=lambda floor: floor.level)

    issues: list[ValidationIssue] = []

    for lower_floor, upper_floor in zip(
        floors,
        floors[1:],
        strict=False,
    ):
        if upper_floor.level != lower_floor.level + 1:
            continue

        for upper_column in upper_floor.columns:
            is_supported = any(
                _columns_overlap(upper_column, lower_column)
                for lower_column in lower_floor.columns
            )

            if not is_supported:
                issues.append(
                    ValidationIssue(
                        issue_code="UNSUPPORTED_COLUMN",
                        severity=ValidationSeverity.ERROR,
                        message=(
                            f"Column {upper_column.column_id} on "
                            f"{upper_floor.floor_id} has no supporting "
                            f"column on {lower_floor.floor_id}."
                        ),
                        element_id=upper_column.column_id,
                        floor_id=upper_floor.floor_id,
                    )
                )

    return tuple(issues)
