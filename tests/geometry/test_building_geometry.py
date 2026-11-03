"""Tests for building-level geometry generation."""

import pytest

from buildingpipeline.domain.models import BuildingParameters
from buildingpipeline.geometry.building_geometry import (
    create_building_geometry,
)
from buildingpipeline.geometry.generator import generate_building
from buildingpipeline.geometry.models import BuildingGeometry


@pytest.fixture
def building():
    """Return a sample building."""
    return generate_building(
        BuildingParameters(
            length=20.0,
            width=15.0,
            floor_count=3,
            floor_height=3.2,
        )
    )


def test_create_building_geometry_returns_building_geometry(building):
    """Verify the returned building geometry type."""
    geometry = create_building_geometry(building)

    assert isinstance(geometry, BuildingGeometry)


def test_create_building_geometry_contains_all_floors(building):
    """Verify that geometry is generated for every floor."""
    geometry = create_building_geometry(building)

    assert len(geometry.floors) == len(building.floors)


def test_create_building_geometry_preserves_floor_ids(building):
    """Verify that floor identifiers are preserved."""
    geometry = create_building_geometry(building)

    assert [floor.floor_id for floor in geometry.floors] == [
        floor.floor_id for floor in building.floors
    ]


def test_create_building_geometry_preserves_elevations(building):
    """Verify that floor elevations are preserved."""
    geometry = create_building_geometry(building)

    assert [floor.elevation for floor in geometry.floors] == [
        floor.elevation for floor in building.floors
    ]


def test_create_building_geometry_creates_valid_polygons(building):
    """Verify that every generated floor polygon is valid."""
    geometry = create_building_geometry(building)

    assert all(floor.polygon.is_valid for floor in geometry.floors)
    assert all(not floor.polygon.is_empty for floor in geometry.floors)