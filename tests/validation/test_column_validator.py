"""Tests for column validation."""

from dataclasses import replace

import pytest

from buildingpipeline.domain.models import (
    BuildingModel,
    BuildingParameters,
    ColumnModel,
    FloorModel,
)
from buildingpipeline.geometry.generator import generate_building
from buildingpipeline.validation.column_validator import (
    validate_column_boundaries,
    validate_column_support,
)
from buildingpipeline.validation.models import ValidationSeverity

# ---------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------


def _get_interior_columns(floor: FloorModel) -> tuple[ColumnModel, ...]:
    """Return columns whose complete footprints are inside the floor."""
    return tuple(
        column
        for column in floor.columns
        if (
            column.x - column.width / 2 >= 0
            and column.y - column.depth / 2 >= 0
            and column.x + column.width / 2 <= floor.length
            and column.y + column.depth / 2 <= floor.width
        )
    )


def _create_two_floor_building() -> BuildingModel:
    """Create a two-floor building containing only interior columns."""
    building = generate_building(BuildingParameters(floor_count=2))

    floors = tuple(
        replace(floor, columns=_get_interior_columns(floor))
        for floor in building.floors
    )

    return replace(building, floors=floors)


def _replace_floor_columns(
    building: BuildingModel,
    floor_index: int,
    columns: tuple[ColumnModel, ...],
) -> BuildingModel:
    """Return a building with replacement columns on one floor.

    Args:
        building: Original building.
        floor_index: Index of the floor to update.
        columns: Replacement column tuple.

    Returns:
        A new building containing the updated floor.
    """
    floors = list(building.floors)

    floors[floor_index] = replace(
        floors[floor_index],
        columns=columns,
    )

    return replace(building, floors=tuple(floors))


# ---------------------------------------------------------------------
# Column boundary tests
# ---------------------------------------------------------------------


def test_columns_inside_floor_boundaries_return_no_issues() -> None:
    """Verify that columns inside floor boundaries are accepted."""
    building = _create_two_floor_building()

    issues = validate_column_boundaries(building)

    assert issues == ()


def test_column_outside_floor_boundary_returns_error() -> None:
    """Verify that a column completely outside the floor is detected."""
    building = _create_two_floor_building()

    floor = building.floors[1]
    column = replace(floor.columns[0], x=100.0)

    updated_building = _replace_floor_columns(
        building,
        floor_index=1,
        columns=(column,),
    )

    issues = validate_column_boundaries(updated_building)

    assert len(issues) == 1
    assert issues[0].issue_code == "COLUMN_OUTSIDE_FLOOR"
    assert issues[0].severity == ValidationSeverity.ERROR
    assert issues[0].element_id == column.column_id
    assert issues[0].floor_id == floor.floor_id


def test_column_crossing_floor_boundary_returns_error() -> None:
    """Verify that a partially outside column is detected."""
    building = _create_two_floor_building()

    floor = building.floors[0]
    column = replace(floor.columns[0], x=0.1)

    updated_building = _replace_floor_columns(
        building,
        floor_index=0,
        columns=(column,),
    )

    issues = validate_column_boundaries(updated_building)

    assert len(issues) == 1
    assert issues[0].issue_code == "COLUMN_OUTSIDE_FLOOR"
    assert issues[0].severity == ValidationSeverity.ERROR
    assert issues[0].element_id == column.column_id
    assert issues[0].floor_id == floor.floor_id


def test_column_touching_floor_boundary_is_accepted() -> None:
    """Verify that a column touching the boundary is accepted."""
    building = generate_building(BuildingParameters(floor_count=1))
    floor = building.floors[0]

    column = replace(
        floor.columns[0],
        x=0.2,
        y=5.0,
    )

    updated_building = _replace_floor_columns(
        building,
        floor_index=0,
        columns=(column,),
    )

    assert validate_column_boundaries(updated_building) == ()


def test_non_building_input_is_rejected_by_boundary_validator() -> None:
    """Verify that the boundary validator rejects invalid input types."""
    with pytest.raises(TypeError, match="BuildingModel"):
        validate_column_boundaries(None)


# ---------------------------------------------------------------------
# Column support tests
# ---------------------------------------------------------------------


def test_aligned_columns_return_no_support_issues() -> None:
    """Verify that aligned columns are supported by the floor below."""
    building = _create_two_floor_building()

    issues = validate_column_support(building)

    assert issues == ()


def test_one_upper_column_is_supported_by_one_lower_column() -> None:
    """Verify that one overlapping lower column is sufficient support."""
    building = _create_two_floor_building()

    lower_column = building.floors[0].columns[0]
    upper_column = replace(
        building.floors[1].columns[0],
        x=lower_column.x + 0.1,
        y=lower_column.y,
    )

    updated_building = _replace_floor_columns(
        building,
        floor_index=1,
        columns=(upper_column,),
    )

    issues = validate_column_support(updated_building)

    assert issues == ()


def test_unsupported_column_inside_floor_returns_error() -> None:
    """Verify that an in-boundary column without lower support is detected."""
    building = _create_two_floor_building()

    upper_floor = building.floors[1]
    unsupported_column = replace(
        upper_floor.columns[0],
        x=2.5,
        y=2.5,
    )

    updated_building = _replace_floor_columns(
        building,
        floor_index=1,
        columns=(unsupported_column,),
    )

    # Ensure this test isolates support validation.
    assert validate_column_boundaries(updated_building) == ()

    issues = validate_column_support(updated_building)

    assert len(issues) == 1
    assert issues[0].issue_code == "UNSUPPORTED_COLUMN"
    assert issues[0].severity == ValidationSeverity.ERROR
    assert issues[0].element_id == unsupported_column.column_id
    assert issues[0].floor_id == upper_floor.floor_id


def test_column_touching_support_boundary_is_not_supported() -> None:
    """Verify that edge contact without positive-area overlap is insufficient."""
    building = _create_two_floor_building()

    lower_column = building.floors[0].columns[0]
    upper_column = replace(
        building.floors[1].columns[0],
        x=(
            lower_column.x
            + lower_column.width / 2
            + building.floors[1].columns[0].width / 2
        ),
        y=lower_column.y,
    )

    updated_building = _replace_floor_columns(
        building,
        floor_index=1,
        columns=(upper_column,),
    )

    issues = validate_column_support(updated_building)

    assert len(issues) == 1
    assert issues[0].issue_code == "UNSUPPORTED_COLUMN"
    assert issues[0].severity == ValidationSeverity.ERROR


def test_empty_lower_floor_columns_make_upper_columns_unsupported() -> None:
    """Verify that upper columns are unsupported when the lower floor has none."""
    building = _create_two_floor_building()

    updated_building = _replace_floor_columns(
        building,
        floor_index=0,
        columns=(),
    )

    issues = validate_column_support(updated_building)

    assert len(issues) == len(building.floors[1].columns)
    assert all(
        issue.issue_code == "UNSUPPORTED_COLUMN"
        for issue in issues
    )


def test_ground_floor_columns_are_assumed_supported() -> None:
    """Verify that ground-floor columns need no lower-floor support check."""
    building = generate_building(BuildingParameters(floor_count=1))

    issues = validate_column_support(building)

    assert issues == ()


def test_non_building_input_is_rejected_by_support_validator() -> None:
    """Verify that the support validator rejects invalid input types."""
    with pytest.raises(TypeError, match="BuildingModel"):
        validate_column_support(None)
