"""Parametric generation of rectangular building geometry."""

from buildingpipeline.domain.models import (
    BuildingModel,
    BuildingParameters,
    ColumnModel,
    FloorModel,
)


def generate_building(parameters: BuildingParameters) -> BuildingModel:
    """Generate a rectangular multi-storey building.

    Floor F1 is the ground storey at z = 0. Each floor elevation is the
    bottom-face elevation of its slab, and floor_height is the spacing between
    these level datums. Column x/y coordinates are their centre-lines, so
    columns on the perimeter grid lines can extend beyond the slab footprint.
    """
    x_spacing = parameters.length / (parameters.grid_x_count - 1)
    y_spacing = parameters.width / (parameters.grid_y_count - 1)

    floors: list[FloorModel] = []

    for floor_index in range(parameters.floor_count):
        columns = tuple(
            ColumnModel(
                column_id=f"C{row_index + 1}-{column_index + 1}",
                x=column_index * x_spacing,
                y=row_index * y_spacing,
                width=parameters.column_width,
                depth=parameters.column_depth,
            )
            for row_index in range(parameters.grid_y_count)
            for column_index in range(parameters.grid_x_count)
        )

        floors.append(
            FloorModel(
                floor_id=f"F{floor_index + 1}",
                level=floor_index + 1,
                elevation=floor_index * parameters.floor_height,
                length=parameters.length,
                width=parameters.width,
                slab_thickness=parameters.slab_thickness,
                columns=columns,
            )
        )

    return BuildingModel(parameters=parameters, floors=tuple(floors))
