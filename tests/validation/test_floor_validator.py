"""Tests for floor outline validation."""

import pytest
from shapely.geometry import Polygon

from buildingpipeline.validation.floor_validator import (
    validate_floor_outline,
)
from buildingpipeline.validation.models import ValidationSeverity


def test_valid_floor_outline_returns_no_issues() -> None:
    """Verify that a valid floor outline produces no issues."""
    polygon = Polygon(
        [(0, 0), (20, 0), (20, 15), (0, 15)]
    )

    issues = validate_floor_outline("F1", polygon)

    assert issues == ()


def test_empty_floor_outline_returns_error() -> None:
    """Verify that an empty floor outline produces an error."""
    polygon = Polygon()

    issues = validate_floor_outline("F1", polygon)

    assert len(issues) == 1
    assert issues[0].issue_code == "FLOOR_EMPTY"
    assert issues[0].severity == ValidationSeverity.ERROR
    assert issues[0].floor_id == "F1"


def test_self_intersecting_floor_outline_returns_error() -> None:
    """Verify that a self-intersecting outline is detected."""
    polygon = Polygon(
        [(0, 0), (10, 10), (0, 10), (10, 0)]
    )

    issues = validate_floor_outline("F1", polygon)

    assert len(issues) == 1
    assert issues[0].issue_code == "FLOOR_INVALID"
    assert issues[0].severity == ValidationSeverity.ERROR
    assert "Self-intersection" in issues[0].message


def test_non_polygon_input_is_rejected() -> None:
    """Verify that non-polygon geometry is rejected."""
    with pytest.raises(TypeError, match="Shapely Polygon"):
        validate_floor_outline("F1", None)


def test_empty_floor_id_is_rejected() -> None:
    """Verify that an empty floor ID is rejected."""
    polygon = Polygon(
        [(0, 0), (10, 0), (10, 10), (0, 10)]
    )

    with pytest.raises(ValueError, match="Floor ID"):
        validate_floor_outline(" ", polygon)