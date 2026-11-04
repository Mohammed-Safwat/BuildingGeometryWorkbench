"""Validation functions for floor outlines."""

from shapely.geometry import Polygon
from shapely.validation import explain_validity

from buildingpipeline.validation.models import (
    ValidationIssue,
    ValidationSeverity,
)


def validate_floor_outline(
    floor_id: str,
    polygon: Polygon,
) -> tuple[ValidationIssue, ...]:
    """Validate a candidate floor outline.

    Args:
        floor_id: Identifier of the floor being validated.
        polygon: Candidate Shapely polygon representing the floor outline.

    Returns:
        A tuple containing detected validation issues.
    """
    if not isinstance(floor_id, str) or not floor_id.strip():
        raise ValueError("Floor ID must be a non-empty string.")

    if not isinstance(polygon, Polygon):
        raise TypeError("Floor outline must be a Shapely Polygon.")

    if polygon.is_empty:
        return (
            ValidationIssue(
                issue_code="FLOOR_EMPTY",
                severity=ValidationSeverity.ERROR,
                message="Floor outline is empty.",
                element_id=floor_id,
                floor_id=floor_id,
            ),
        )

    if not polygon.is_valid:
        return (
            ValidationIssue(
                issue_code="FLOOR_INVALID",
                severity=ValidationSeverity.ERROR,
                message=explain_validity(polygon),
                element_id=floor_id,
                floor_id=floor_id,
            ),
        )

    return ()