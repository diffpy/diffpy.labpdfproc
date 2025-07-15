"""Unit tests for __version__.py."""

import diffpy.my_labpdfproc  # noqa


def test_package_version():
    """Ensure the package version is defined and not set to the initial
    placeholder."""
    assert hasattr(diffpy.my_labpdfproc, "__version__")
    assert diffpy.my_labpdfproc.__version__ != "0.0.0"
