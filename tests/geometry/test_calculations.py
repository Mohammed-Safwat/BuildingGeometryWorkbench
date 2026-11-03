"""Tests for floor geometry calculations."""

import pytest
from shapely.geometry import Polygon

from buildingpipeline.geometry.calculations import (
    calculate_exterior_perimeter,
    calculate_gross_area,
    calculate_net_area,
    calculate_opening_area,
    calculate_opening_perimeter,
    calculate_total_boundary_length,
)
from buildingpipeline.geometry.models import FloorGeometry


@pytest.fixture
def floor_geometry() -> FloorGeometry:
    """Return a floor geometry containing one rectangular opening."""
    polygon = Polygon(
        [
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 15.0),
            (0.0, 15.0),
        ],
        holes=[
            [
                (2.0, 2.0),
                (6.0, 2.0),
                (6.0, 5.0),
                (2.0, 5.0),
            ]
        ],
    )

    return FloorGeometry(
        floor_id="F1",
        elevation=0.0,
        slab_thickness=0.25,
        polygon=polygon,
    )


def test_calculate_gross_area(floor_geometry: FloorGeometry) -> None:
    """Verify that gross area includes the opening."""
    assert calculate_gross_area(floor_geometry) == pytest.approx(300.0)


def test_calculate_opening_area(floor_geometry: FloorGeometry) -> None:
    """Verify the combined opening area."""
    assert calculate_opening_area(floor_geometry) == pytest.approx(12.0)


def test_calculate_net_area(floor_geometry: FloorGeometry) -> None:
    """Verify that net area excludes the opening."""
    assert calculate_net_area(floor_geometry) == pytest.approx(288.0)


def test_calculate_exterior_perimeter(
    floor_geometry: FloorGeometry,
) -> None:
    """Verify that exterior perimeter excludes opening boundaries."""
    assert calculate_exterior_perimeter(floor_geometry) == pytest.approx(70.0)


def test_calculate_opening_perimeter(
    floor_geometry: FloorGeometry,
) -> None:
    """Verify the opening boundary length."""
    assert calculate_opening_perimeter(floor_geometry) == pytest.approx(14.0)


def test_calculate_total_boundary_length(
    floor_geometry: FloorGeometry,
) -> None:
    """Verify that total boundary length includes opening boundaries."""
    assert calculate_total_boundary_length(floor_geometry) == pytest.approx(84.0)