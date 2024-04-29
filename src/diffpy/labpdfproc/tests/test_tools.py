import pytest

from diffpy.labpdfproc.labpdfprocapp import WAVELENGTHS
from diffpy.labpdfproc.tools import load_wavelength

params1 = [
    ([None, None], [0.71]),
    ([None, "Ag"], [0.59]),
    ([0.25, "Ag"], [0.25]),
    ([0.25, None], [0.25]),
]


@pytest.mark.parametrize("inputs, expected", params1)
def test_load_wavelengths(inputs, expected):
    expected_wavelength = expected[0]
    actual_wavelength = load_wavelength(inputs[0], inputs[1], WAVELENGTHS)
    assert actual_wavelength == expected_wavelength
