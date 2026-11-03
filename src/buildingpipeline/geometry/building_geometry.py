"""Functions for constructing building-level geometry."""

from buildingpipeline.domain.models import BuildingModel
from buildingpipeline.geometry.floor_geometry import create_floor_geometry
from buildingpipeline.geometry.models import BuildingGeometry


def create_building_geometry(
    building: BuildingModel,
) -> BuildingGeometry:
    """Create geometric representations for all building floors.

    Args:
        building: Building domain model.

    Returns:
        BuildingGeometry containing the geometry of every floor.
    """
    floors = tuple(
        create_floor_geometry(floor)
        for floor in building.floors
    )

    return BuildingGeometry(floors=floors)