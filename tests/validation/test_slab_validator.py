"""Tests for slab validation."""

import pytest

from buildingpipeline.validation.models import ValidationSeverity
from buildingpipeline.validation.slab_validator import (
    validate_slab_planarity,
)

# ---------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------


PLANAR_POINTS = (
    (0.0, 0.0, 0.0),
    (10.0, 0.0, 0.0),
    (10.0, 10.0, 0.0),
    (0.0, 10.0, 0.0),
)

NON_PLANAR_POINTS = (
    (0.0, 0.0, 0.0),
    (10.0, 0.0, 0.0),
    (10.0, 10.0, 0.0),
    (0.0, 10.0, 0.1),
)


# ---------------------------------------------------------------------
# Slab planarity tests
# ---------------------------------------------------------------------


def test_planar_slab_returns_no_issues() -> None:
    """Verify that a perfectly planar slab passes validation."""
    issues = validate_slab_planarity(
        floor_id="F1",
        points=PLANAR_POINTS,
    )

    assert issues == ()


def test_non_planar_slab_returns_error() -> None:
    """Verify that a nonplanar slab exceeding tolerance is detected."""
    issues = validate_slab_planarity(
        floor_id="F1",
        points=NON_PLANAR_POINTS,
        tolerance=0.001,
    )

    assert len(issues) == 1
    assert issues[0].issue_code == "SLAB_NON_PLANAR"
    assert issues[0].severity == ValidationSeverity.ERROR
    assert issues[0].element_id == "F1"
    assert issues[0].floor_id == "F1"


def test_slab_within_tolerance_returns_no_issues() -> None:
    """Verify that deviations within tolerance are accepted."""
    points = (
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 0.0),
        (10.0, 10.0, 0.0),
        (0.0, 10.0, 0.001),
    )

    issues = validate_slab_planarity(
        floor_id="F1",
        points=points,
        tolerance=0.01,
    )

    assert issues == ()


def test_custom_tolerance_is_respected() -> None:
    """Verify that a stricter tolerance detects smaller deviations."""
    points = (
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 0.0),
        (10.0, 10.0, 0.0),
        (0.0, 10.0, 0.01),
    )

    issues = validate_slab_planarity(
        floor_id="F1",
        points=points,
        tolerance=0.0001,
    )

    assert len(issues) == 1
    assert issues[0].issue_code == "SLAB_NON_PLANAR"


def test_inclined_but_planar_slab_returns_no_issues() -> None:
    """Verify that an inclined planar slab is accepted."""
    points = (
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 1.0),
        (10.0, 10.0, 1.0),
        (0.0, 10.0, 0.0),
    )

    issues = validate_slab_planarity(
        floor_id="F1",
        points=points,
    )

    assert issues == ()


# ---------------------------------------------------------------------
# Input validation tests
# ---------------------------------------------------------------------


def test_empty_floor_id_is_rejected() -> None:
    """Verify that an empty floor ID is rejected."""
    with pytest.raises(ValueError, match="floor_id"):
        validate_slab_planarity(
            floor_id="",
            points=PLANAR_POINTS,
        )


def test_invalid_tolerance_is_rejected() -> None:
    """Verify that zero tolerance is rejected."""
    with pytest.raises(ValueError, match="tolerance"):
        validate_slab_planarity(
            floor_id="F1",
            points=PLANAR_POINTS,
            tolerance=0.0,
        )


def test_negative_tolerance_is_rejected() -> None:
    """Verify that negative tolerance is rejected."""
    with pytest.raises(ValueError, match="tolerance"):
        validate_slab_planarity(
            floor_id="F1",
            points=PLANAR_POINTS,
            tolerance=-0.001,
        )


def test_less_than_four_points_are_rejected() -> None:
    """Verify that fewer than four points are rejected."""
    with pytest.raises(ValueError, match="four"):
        validate_slab_planarity(
            floor_id="F1",
            points=PLANAR_POINTS[:3],
        )


def test_points_without_three_coordinates_are_rejected() -> None:
    """Verify that points must have exactly three coordinates."""
    points = (
        (0.0, 0.0),
        (10.0, 0.0),
        (10.0, 10.0),
        (0.0, 10.0),
    )

    with pytest.raises(ValueError, match=r"\(n, 3\)"):
        validate_slab_planarity(
            floor_id="F1",
            points=points,
        )


def test_non_finite_coordinates_are_rejected() -> None:
    """Verify that NaN and infinite coordinates are rejected."""
    points = (
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 0.0),
        (10.0, 10.0, 0.0),
        (0.0, 10.0, float("nan")),
    )

    with pytest.raises(ValueError, match="finite"):
        validate_slab_planarity(
            floor_id="F1",
            points=points,
        )


def test_non_numeric_coordinates_are_rejected() -> None:
    """Verify that non-numeric coordinates are rejected."""
    points = (
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 0.0),
        (10.0, 10.0, 0.0),
        (0.0, 10.0, "invalid"),
    )

    with pytest.raises(TypeError, match="numeric"):
        validate_slab_planarity(
            floor_id="F1",
            points=points,
        )
