
# Building Geometry Workbench

A desktop application for generating, inspecting, visualizing, and validating
building geometry.

## Planned capabilities

- Parametric multi-storey building generation
- Floor extraction and polygon geometry analysis
- 2D floor plans and 3D visualization
- Geometry validation and problem highlighting
- CSV and JSON validation reports
- Automated tests and continuous integration

## Technology stack

- Python
- PySide6
- PyVista / VTK
- NumPy
- Shapely
- scikit-spatial
- Matplotlib
- pytest and Ruff

## Development setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project and development tools:

```powershell
python -m pip install -e ".[dev]"
```

Run tests:

```powershell
python -m pytest
```

Check code quality:

```powershell
python -m ruff check .
```

## Status

Under active development. Features will be documented as they are implemented.