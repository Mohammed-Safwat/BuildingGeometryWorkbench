"""Tests for parametric building generation."""

import pytest

from buildingpipeline.domain import BuildingParameters
from buildingpipeline.geometry import generate_building


def test_generates_expected_floor_count() -> None:
    building = generate_building(BuildingParameters(floor_count=3))

    assert len(building.floors) == 3
    assert [floor.floor_id for floor in building.floors] == [
        "F1",
        "F2",
        "F3",
    ]


def test_generates_expected_column_count_per_floor() -> None:
    parameters = BuildingParameters(
        grid_x_count=5,
        grid_y_count=4,
    )

    building = generate_building(parameters)

    assert all(len(floor.columns) == 20 for floor in building.floors)


def test_floor_elevations_are_level_spacings() -> None:
    building = generate_building(
        BuildingParameters(floor_count=3, floor_height=3.2)
    )

    assert [floor.elevation for floor in building.floors] == pytest.approx(
        [0.0, 3.2, 6.4]
    )


def test_roof_elevation_is_one_storey_above_last_floor_level() -> None:
    building = generate_building(
        BuildingParameters(floor_count=3, floor_height=3.2)
    )

    assert building.floors[-1].elevation == pytest.approx(6.4)
    assert building.roof_elevation == pytest.approx(9.6)


def test_slab_thickness_does_not_change_level_spacing() -> None:
    building = generate_building(
        BuildingParameters(
            floor_count=3,
            floor_height=3.2,
            slab_thickness=0.25,
        )
    )

    # Slab bottom-face elevations are 0.0, 3.2, and 6.4 m.
    # Each slab top is 0.25 m above its bottom face.
    assert [floor.elevation for floor in building.floors] == pytest.approx(
        [0.0, 3.2, 6.4]
    )
    assert building.floors[0].elevation + building.floors[0].slab_thickness == (
        pytest.approx(0.25)
    )


def test_column_grid_covers_building_gridline_extents() -> None:
    parameters = BuildingParameters(
        length=20.0,
        width=15.0,
        grid_x_count=5,
        grid_y_count=4,
    )

    building = generate_building(parameters)
    columns = building.floors[0].columns

    # Coordinates represent column centres on the grid lines, not corners.
    assert min(column.x for column in columns) == pytest.approx(0.0)
    assert max(column.x for column in columns) == pytest.approx(20.0)
    assert min(column.y for column in columns) == pytest.approx(0.0)
    assert max(column.y for column in columns) == pytest.approx(15.0)


def test_perimeter_column_can_extend_beyond_slab_boundary() -> None:
    building = generate_building(BuildingParameters())
    corner_column = building.floors[0].columns[0]

    assert corner_column.x == pytest.approx(0.0)
    assert corner_column.y == pytest.approx(0.0)
    assert corner_column.x - corner_column.width / 2 == pytest.approx(-0.2)
    assert corner_column.y - corner_column.depth / 2 == pytest.approx(-0.2)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("length", 0.0),
        ("width", -1.0),
        ("floor_height", 0.0),
        ("floor_count", 0),
        ("grid_x_count", 1),
        ("grid_y_count", 1),
        ("column_width", 0.0),
        ("column_depth", 0.0),
        ("slab_thickness", 0.0),
    ],
)
def test_rejects_invalid_parameters(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        BuildingParameters(**{field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("length", float("nan")),
        ("width", float("inf")),
        ("floor_height", float("-inf")),
    ],
)
def test_rejects_non_finite_dimensions(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        BuildingParameters(**{field: value})


def test_rejects_non_integer_floor_count() -> None:
    with pytest.raises(TypeError):
        BuildingParameters(floor_count=2.5)  # type: ignore[arg-type]


def test_generation_is_deterministic() -> None:
    parameters = BuildingParameters()

    first = generate_building(parameters)
    second = generate_building(parameters)

    assert first == second


def test_roof_elevation_uses_storey_count_and_height() -> None:
    building = generate_building(
        BuildingParameters(floor_count=3, floor_height=3.2)
    )

    assert building.roof_elevation == pytest.approx(9.6)
