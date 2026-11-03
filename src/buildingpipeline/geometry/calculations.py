"""Functions for calculating floor geometry measurements."""

from shapely.geometry import Polygon

from buildingpipeline.geometry.models import FloorGeometry


def calculate_gross_area(geometry: FloorGeometry) -> float:
    """Calculate the floor area before subtracting openings.

    Args:
        geometry: Floor geometry to measure.

    Returns:
        Area enclosed by the exterior boundary, in square metres.
    """
    exterior_polygon = Polygon(geometry.polygon.exterior)
    return exterior_polygon.area


def calculate_opening_area(geometry: FloorGeometry) -> float:
    """Calculate the combined area of all floor openings.

    Args:
        geometry: Floor geometry to measure.

    Returns:
        Combined opening area, in square metres.
    """
    return sum(
        Polygon(interior).area
        for interior in geometry.polygon.interiors
    )


def calculate_net_area(geometry: FloorGeometry) -> float:
    """Calculate the usable slab area after subtracting openings.

    Args:
        geometry: Floor geometry to measure.

    Returns:
        Net slab area, in square metres.
    """
    return geometry.polygon.area


def calculate_exterior_perimeter(geometry: FloorGeometry) -> float:
    """Calculate the length of the exterior floor boundary.

    Args:
        geometry: Floor geometry to measure.

    Returns:
        Exterior boundary length, in metres.
    """
    return geometry.polygon.exterior.length


def calculate_opening_perimeter(geometry: FloorGeometry) -> float:
    """Calculate the combined boundary length of all openings.

    Args:
        geometry: Floor geometry to measure.

    Returns:
        Combined opening boundary length, in metres.
    """
    return sum(
        interior.length
        for interior in geometry.polygon.interiors
    )


def calculate_total_boundary_length(geometry: FloorGeometry) -> float:
    """Calculate the total length of all floor polygon boundaries.

    Includes both the exterior boundary and opening boundaries.

    Args:
        geometry: Floor geometry to measure.

    Returns:
        Total boundary length, in metres.
    """
    return geometry.polygon.length