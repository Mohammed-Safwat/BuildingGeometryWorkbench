from buildingpipeline import __doc__


def test_package_is_importable() -> None:
    assert __doc__ is not None
    assert "Building Geometry Workbench" in __doc__