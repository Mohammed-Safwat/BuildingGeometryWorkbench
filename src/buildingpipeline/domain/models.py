"""Core domain models for a simplified building geometry model.

Conventions
-----------
- Coordinates are Cartesian XYZ and lengths are in metres.
- X follows building length; Y follows building width; Z is vertical.
- A column's (x, y) is the centre of its cross-section, aligned to grid lines.
- The rectangular slab footprint starts at (0, 0); edge columns may overhang it.
- Each FloorModel.elevation is the structural level datum at the bottom face
  of that floor's slab.
- floor_height is floor-to-floor level spacing, not clear height. With a slab
  thickness t, the clear vertical gap between consecutive slabs is
  floor_height - t.
- floor_count is the number of storeys. F1 is the ground storey at z = 0.
- roof_elevation is the reference level one storey interval above the last
  floor level. The roof slab itself is not generated in this milestone.
"""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class BuildingParameters:
    """Inputs for a rectangular multi-storey building, with dimensions in metres.

    Grid coordinates are column centre-lines. They may coincide with the
    slab boundary, so edge columns can extend beyond the slab footprint.
    """

    length: float = 20.0
    width: float = 15.0
    floor_count: int = 3
    floor_height: float = 3.2
    grid_x_count: int = 5
    grid_y_count: int = 4
    column_width: float = 0.4
    column_depth: float = 0.4
    slab_thickness: float = 0.25

    def __post_init__(self) -> None:
        """Reject non-positive or non-finite dimensions and invalid counts."""
        positive_values = {
            "length": self.length,
            "width": self.width,
            "floor_height": self.floor_height,
            "column_width": self.column_width,
            "column_depth": self.column_depth,
            "slab_thickness": self.slab_thickness,
        }

        for name, value in positive_values.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero.")
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be a number.")
            if not isfinite(value):
                raise ValueError(f"{name} must be finite.")

        integer_values = {
            "floor_count": (self.floor_count, 1),
            "grid_x_count": (self.grid_x_count, 2),
            "grid_y_count": (self.grid_y_count, 2),
        }
        for name, (value, minimum) in integer_values.items():
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an integer.")
            if value < minimum:
                raise ValueError(f"{name} must be at least {minimum}.")

        if self.column_width >= self.length:
            raise ValueError("column_width must be smaller than length.")

        if self.column_depth >= self.width:
            raise ValueError("column_depth must be smaller than width.")


@dataclass(frozen=True, slots=True)
class ColumnModel:
    """A column cross-section centred at (x, y) on the building's XY grid."""

    column_id: str
    x: float
    y: float
    width: float
    depth: float


@dataclass(frozen=True, slots=True)
class FloorModel:
    """A storey's slab footprint and structural level datum.

    ``elevation`` is the slab's bottom-face elevation in metres. The slab
    occupies Z from ``elevation`` to ``elevation + slab_thickness``.
    """

    floor_id: str
    level: int
    elevation: float
    length: float
    width: float
    slab_thickness: float
    columns: tuple[ColumnModel, ...]


@dataclass(frozen=True, slots=True)
class BuildingModel:
    """Generated building data consumed by geometry, services, and UI."""

    parameters: BuildingParameters
    floors: tuple[FloorModel, ...]

    @property
    def roof_elevation(self) -> float:
        """Return the roof reference level, one storey above the last floor.

        The roof slab geometry is not represented yet. For N storeys, the
        reference level is N * floor_height above the base level.
        """
        return self.parameters.floor_count * self.parameters.floor_height
