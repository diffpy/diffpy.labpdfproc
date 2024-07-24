import numpy as np

from diffpy.labpdfproc.fast_cve import apply_fast_corr, fast_compute_cve
from diffpy.utils.scattering_objects.diffraction_objects import Diffraction_object


def _instantiate_test_do(xarray, yarray, name="test", scat_quantity="x-ray"):
    test_do = Diffraction_object(wavelength=1.54)
    test_do.insert_scattering_quantity(
        xarray,
        yarray,
        "tth",
        scat_quantity=scat_quantity,
        name=name,
        metadata={"thing1": 1, "thing2": "thing2"},
    )
    return test_do


def test_fast_compute_cve(mocker):
    xarray, yarray = np.array([90, 90.1, 90.2]), np.array([2, 2, 2])
    expected_cve = np.array([0.5, 0.5, 0.5])
    mocker.patch("numpy.interp", return_value=expected_cve)
    input_pattern = _instantiate_test_do(xarray, yarray)
    actual_abdo = fast_compute_cve(input_pattern, mud=1, wavelength=1.54)
    expected_abdo = _instantiate_test_do(
        xarray,
        expected_cve,
        name="absorption correction, cve, for test",
        scat_quantity="cve",
    )
    assert actual_abdo == expected_abdo


def test_apply_fast_corr(mocker):
    xarray, yarray = np.array([90, 90.1, 90.2]), np.array([2, 2, 2])
    expected_cve = np.array([0.5, 0.5, 0.5])
    mocker.patch("numpy.interp", return_value=expected_cve)
    input_pattern = _instantiate_test_do(xarray, yarray)
    absorption_correction = _instantiate_test_do(
        xarray,
        expected_cve,
        name="absorption correction, cve, for test",
        scat_quantity="cve",
    )
    actual_corr = apply_fast_corr(input_pattern, absorption_correction)
    expected_corr = _instantiate_test_do(xarray, np.array([1, 1, 1]))
    assert actual_corr == expected_corr
