"""Validation functions for slab geometry."""

import numpy as np
from skspatial.objects import Plane

from buildingpipeline.validation.models import (
    ValidationIssue,
    ValidationSeverity,
)


def validate_slab_planarity(
    floor_id: str,
    points: tuple[tuple[float, float, float], ...],
    tolerance: float = 0.001,
) -> tuple[ValidationIssue, ...]:
    """Validate slab planarity using sampled 3D points.

    A best-fit plane is calculated from the supplied points. The maximum
    perpendicular distance from any point to that plane is compared
    against the allowed tolerance.

    Args:
        floor_id: Identifier of the floor being validated.
        points: At least four sampled 3D points on the slab surface.
        tolerance: Maximum allowed deviation from the best-fit plane,
            in metres. Defaults to 0.001 m (1 mm).

    Returns:
        A tuple containing a validation issue if the slab is nonplanar,
        or an empty tuple if it passes validation.

    Raises:
        ValueError: If the floor ID, tolerance, or point coordinates
            are invalid, or if the points cannot define a plane.
        TypeError: If the supplied points cannot be converted to
            numeric coordinates.
    """
    if not isinstance(floor_id, str) or not floor_id.strip():
        raise ValueError("floor_id must be a non-empty string.")

    if (
        isinstance(tolerance, bool)
        or not isinstance(tolerance, (int, float))
        or not np.isfinite(tolerance)
        or tolerance <= 0
    ):
        raise ValueError("tolerance must be a positive finite number.")

    try:
        coordinates = np.asarray(points, dtype=float)
    except (TypeError, ValueError) as exc:
        raise TypeError("points must contain numeric 3D coordinates.") from exc

    if coordinates.ndim != 2 or coordinates.shape[1] != 3:
        raise ValueError("points must have shape (n, 3).")

    if len(coordinates) < 4:
        raise ValueError("At least four 3D points are required.")

    if not np.isfinite(coordinates).all():
        raise ValueError("Point coordinates must be finite.")

    try:
        best_fit_plane = Plane.best_fit(coordinates)
    except ValueError as exc:
        raise ValueError(
            "The supplied points cannot define a best-fit plane."
        ) from exc

    deviations = tuple(
        abs(best_fit_plane.distance_point(point))
        for point in coordinates
    )

    maximum_deviation = max(deviations)

    if maximum_deviation <= tolerance:
        return ()

    return (
        ValidationIssue(
            issue_code="SLAB_NON_PLANAR",
            severity=ValidationSeverity.ERROR,
            message=(
                f"Slab on {floor_id} exceeds the planarity tolerance. "
                f"Maximum deviation: {maximum_deviation:.6f} m; "
                f"allowed tolerance: {tolerance:.6f} m."
            ),
            element_id=floor_id,
            floor_id=floor_id,
        ),
    )
