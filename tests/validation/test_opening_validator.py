"""Tests for opening validation."""

import pytest

from buildingpipeline.domain.models import BuildingParameters
from buildingpipeline.geometry.floor_geometry import create_floor_geometry
from buildingpipeline.geometry.generator import generate_building
from buildingpipeline.geometry.models import OpeningGeometry
from buildingpipeline.validation.models import ValidationSeverity
from buildingpipeline.validation.opening_validator import validate_openings

# ---------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------


def _create_floor_geometry():
    """Create a default floor geometry for testing."""
    building = generate_building(BuildingParameters(floor_count=1))
    return create_floor_geometry(building.floors[0])


def _create_opening(
    opening_id: str = "O1",
    min_x: float = 2.0,
    min_y: float = 2.0,
    width: float = 1.0,
    depth: float = 1.0,
) -> OpeningGeometry:
    """Create an opening with configurable dimensions."""
    return OpeningGeometry(
        opening_id=opening_id,
        min_x=min_x,
        min_y=min_y,
        width=width,
        depth=depth,
    )


# ---------------------------------------------------------------------
# Opening boundary tests
# ---------------------------------------------------------------------


def test_opening_inside_slab_returns_no_issues() -> None:
    """Verify that an opening completely inside the slab is accepted."""
    floor = _create_floor_geometry()
    openings = (_create_opening(),)

    issues = validate_openings(floor, openings)

    assert issues == ()


def test_opening_outside_slab_returns_error() -> None:
    """Verify that an opening outside the slab is detected."""
    floor = _create_floor_geometry()
    openings = (
        _create_opening(
            min_x=25.0,
            min_y=2.0,
        ),
    )

    issues = validate_openings(floor, openings)

    assert len(issues) == 1
    assert issues[0].issue_code == "OPENING_OUTSIDE_SLAB"
    assert issues[0].severity == ValidationSeverity.ERROR
    assert issues[0].element_id == "O1"
    assert issues[0].floor_id == floor.floor_id


def test_opening_crossing_slab_boundary_returns_error() -> None:
    """Verify that a partially outside opening is detected."""
    floor = _create_floor_geometry()
    openings = (
        _create_opening(
            min_x=19.5,
            min_y=2.0,
            width=1.0,
        ),
    )

    issues = validate_openings(floor, openings)

    assert len(issues) == 1
    assert issues[0].issue_code == "OPENING_OUTSIDE_SLAB"


def test_opening_touching_slab_boundary_is_accepted() -> None:
    """Verify that an opening touching the slab boundary is accepted."""
    floor = _create_floor_geometry()
    openings = (
        _create_opening(
            min_x=0.0,
            min_y=2.0,
        ),
    )

    issues = validate_openings(floor, openings)

    assert issues == ()


def test_multiple_valid_openings_return_no_issues() -> None:
    """Verify that multiple non-overlapping openings are accepted."""
    floor = _create_floor_geometry()
    openings = (
        _create_opening("O1", min_x=2.0, min_y=2.0),
        _create_opening("O2", min_x=5.0, min_y=5.0),
        _create_opening("O3", min_x=10.0, min_y=8.0),
    )

    issues = validate_openings(floor, openings)

    assert issues == ()


# ---------------------------------------------------------------------
# Opening overlap tests
# ---------------------------------------------------------------------


def test_overlapping_openings_return_error() -> None:
    """Verify that openings with positive-area overlap are detected."""
    floor = _create_floor_geometry()
    openings = (
        _create_opening("O1", min_x=2.0, min_y=2.0),
        _create_opening("O2", min_x=2.5, min_y=2.5),
    )

    issues = validate_openings(floor, openings)

    assert len(issues) == 1
    assert issues[0].issue_code == "OPENINGS_OVERLAP"
    assert issues[0].severity == ValidationSeverity.ERROR
    assert issues[0].element_id == "O2"
    assert issues[0].floor_id == floor.floor_id


def test_openings_touching_edges_do_not_overlap() -> None:
    """Verify that openings sharing only an edge are accepted."""
    floor = _create_floor_geometry()
    openings = (
        _create_opening("O1", min_x=2.0, min_y=2.0),
        _create_opening("O2", min_x=3.0, min_y=2.0),
    )

    issues = validate_openings(floor, openings)

    assert issues == ()


def test_empty_openings_return_no_issues() -> None:
    """Verify that a floor without openings passes validation."""
    floor = _create_floor_geometry()

    issues = validate_openings(floor, ())

    assert issues == ()


# ---------------------------------------------------------------------
# Input validation tests
# ---------------------------------------------------------------------


def test_non_floor_geometry_input_is_rejected() -> None:
    """Verify that invalid floor input is rejected."""
    with pytest.raises(TypeError, match="FloorGeometry"):
        validate_openings(None, ())


def test_non_tuple_openings_input_is_rejected() -> None:
    """Verify that openings must be supplied as a tuple."""
    floor = _create_floor_geometry()

    with pytest.raises(TypeError, match="tuple"):
        validate_openings(floor, [_create_opening()])


def test_invalid_opening_type_is_rejected() -> None:
    """Verify that every opening must be an OpeningGeometry."""
    floor = _create_floor_geometry()

    with pytest.raises(TypeError, match="OpeningGeometry"):
        validate_openings(floor, ("invalid",))
