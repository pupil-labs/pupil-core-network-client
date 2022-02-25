import pupil_labs.pupil_core_network_client as this_project


def test_package_metadata() -> None:
    assert hasattr(this_project, "__version__")
    assert this_project.__version__ is not None
