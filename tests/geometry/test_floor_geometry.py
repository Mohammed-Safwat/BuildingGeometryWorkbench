"""Tests for building floor geometry generation."""

import pytest
from shapely.geometry import Polygon

from buildingpipeline.domain.models import BuildingParameters
from buildingpipeline.geometry.floor_geometry import create_floor_geometry
from buildingpipeline.geometry.generator import generate_building
from buildingpipeline.geometry.models import OpeningGeometry


@pytest.fixture
def floor():
    """Return a sample building floor."""
    building = generate_building(
        BuildingParameters(
            length=20.0,
            width=15.0,
            floor_count=2,
            floor_height=3.2,
        )
    )
    return building.floors[0]


def test_create_floor_geometry_returns_floor_geometry(floor):
    """Verify that floor geometry is generated correctly."""
    geometry = create_floor_geometry(floor)

    assert geometry.floor_id == floor.floor_id
    assert geometry.elevation == floor.elevation
    assert geometry.slab_thickness == floor.slab_thickness


def test_create_floor_geometry_creates_polygon(floor):
    """Verify that the generated geometry is a Shapely polygon."""
    geometry = create_floor_geometry(floor)

    assert isinstance(geometry.polygon, Polygon)
    assert geometry.polygon.is_valid
    assert not geometry.polygon.is_empty


def test_create_floor_geometry_has_correct_bounds(floor):
    """Verify the rectangular floor boundary coordinates."""
    geometry = create_floor_geometry(floor)

    assert geometry.polygon.bounds == pytest.approx(
        (0.0, 0.0, 20.0, 15.0)
    )


def test_create_floor_geometry_has_correct_area(floor):
    """Verify the generated floor polygon area."""
    geometry = create_floor_geometry(floor)

    assert geometry.polygon.area == pytest.approx(300.0)


def test_create_floor_geometry_has_no_openings(floor):
    """Verify that the generated floor has no interior rings."""
    geometry = create_floor_geometry(floor)

    assert len(geometry.polygon.interiors) == 0

def test_create_floor_geometry_with_one_opening(floor):
    """Verify that a rectangular opening becomes an interior ring."""
    opening = OpeningGeometry(
        opening_id="O1",
        min_x=2.0,
        min_y=2.0,
        width=4.0,
        depth=3.0,
    )

    geometry = create_floor_geometry(floor, (opening,))

    assert len(geometry.polygon.interiors) == 1
    assert geometry.polygon.area == pytest.approx(288.0)


def test_create_floor_geometry_with_multiple_openings(floor):
    """Verify that multiple openings are represented as interior rings."""
    openings = (
        OpeningGeometry("O1", 2.0, 2.0, 4.0, 3.0),
        OpeningGeometry("O2", 10.0, 5.0, 2.0, 2.0),
    )

    geometry = create_floor_geometry(floor, openings)

    assert len(geometry.polygon.interiors) == 2
    assert geometry.polygon.area == pytest.approx(284.0)


def test_create_floor_geometry_rejects_opening_outside_floor(floor):
    """Verify that openings outside the slab are rejected."""
    opening = OpeningGeometry(
        "O1",
        min_x=18.0,
        min_y=2.0,
        width=4.0,
        depth=3.0,
    )

    with pytest.raises(ValueError, match="lies outside floor"):
        create_floor_geometry(floor, (opening,))


def test_create_floor_geometry_rejects_overlapping_openings(floor):
    """Verify that overlapping openings produce an error."""
    openings = (
        OpeningGeometry("O1", 2.0, 2.0, 4.0, 3.0),
        OpeningGeometry("O2", 4.0, 3.0, 4.0, 3.0),
    )

    with pytest.raises(ValueError, match="invalid geometry"):
        create_floor_geometry(floor, openings)