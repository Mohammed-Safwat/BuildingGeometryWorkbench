
"""Data models representing derived building geometry."""

from dataclasses import dataclass
from math import isfinite

from shapely.geometry import Polygon


@dataclass(frozen=True, slots=True)
class OpeningGeometry:
    """Represent a rectangular opening in a floor slab.

    Coordinates are expressed in the global XY plane in metres.
    The opening is defined by its minimum X and Y coordinates,
    width along X, and depth along Y.
    """

    opening_id: str
    min_x: float
    min_y: float
    width: float
    depth: float

    def __post_init__(self) -> None:
        """Validate the opening identifier and dimensions."""
        if not isinstance(self.opening_id, str) or not self.opening_id.strip():
            raise ValueError("Opening ID must be a non-empty string.")

        values = (self.min_x, self.min_y, self.width, self.depth)

        if any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            for value in values
        ):
            raise TypeError("Opening coordinates and dimensions must be numeric.")

        if not all(isfinite(value) for value in values):
            raise ValueError("Opening coordinates and dimensions must be finite.")

        if self.width <= 0 or self.depth <= 0:
            raise ValueError("Opening width and depth must be positive.")

    @property
    def max_x(self) -> float:
        """Return the maximum X coordinate of the opening."""
        return self.min_x + self.width

    @property
    def max_y(self) -> float:
        """Return the maximum Y coordinate of the opening."""
        return self.min_y + self.depth


@dataclass(frozen=True, slots=True)
class FloorGeometry:
    """Represent the geometric definition of a floor slab.

    The Shapely polygon contains the exterior slab boundary
    and interior rings representing slab openings.

    Elevation represents the bottom-face elevation of the slab.
    """

    floor_id: str
    elevation: float
    slab_thickness: float
    polygon: Polygon

    def __post_init__(self) -> None:
        """Validate the floor geometry properties."""
        if not isinstance(self.floor_id, str) or not self.floor_id.strip():
            raise ValueError("Floor ID must be a non-empty string.")

        if isinstance(self.elevation, bool) or not isinstance(
            self.elevation, (int, float)
        ):
            raise TypeError("Floor elevation must be numeric.")

        if isinstance(self.slab_thickness, bool) or not isinstance(
            self.slab_thickness, (int, float)
        ):
            raise TypeError("Slab thickness must be numeric.")

        if not isfinite(self.elevation):
            raise ValueError("Floor elevation must be finite.")

        if not isfinite(self.slab_thickness) or self.slab_thickness <= 0:
            raise ValueError("Slab thickness must be finite and positive.")

        if not isinstance(self.polygon, Polygon):
            raise TypeError("Floor geometry must contain a Shapely Polygon.")

        if self.polygon.is_empty or not self.polygon.is_valid:
            raise ValueError("Floor polygon must be non-empty and valid.")

@dataclass(frozen=True, slots=True)
class BuildingGeometry:
    """Represent the derived geometry of an entire building."""

    floors: tuple[FloorGeometry, ...]

    def __post_init__(self) -> None:
        """Validate the building geometry."""
        if not isinstance(self.floors, tuple):
            raise TypeError("Building floors must be provided as a tuple.")

        if not all(isinstance(floor, FloorGeometry) for floor in self.floors):
            raise TypeError("All building floors must be FloorGeometry objects.")

        floor_ids = [floor.floor_id for floor in self.floors]

        if len(floor_ids) != len(set(floor_ids)):
            raise ValueError("Building geometry cannot contain duplicate floor IDs.")