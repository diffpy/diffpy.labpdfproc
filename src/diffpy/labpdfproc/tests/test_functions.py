import re

import numpy as np
import pytest

from diffpy.labpdfproc.functions import CVE_METHODS, Gridded_circle, apply_corr, compute_cve
from diffpy.utils.scattering_objects.diffraction_objects import Diffraction_object

params1 = [
    ([0.5, 3, 1], {(0.0, -0.5), (0.0, 0.0), (0.5, 0.0), (-0.5, 0.0), (0.0, 0.5)}),
    ([1, 4, 1], {(-0.333333, -0.333333), (0.333333, -0.333333), (-0.333333, 0.333333), (0.333333, 0.333333)}),
]


@pytest.mark.parametrize("inputs, expected", params1)
def test_get_grid_points(inputs, expected):
    expected_grid = expected
    actual_gs = Gridded_circle(radius=inputs[0], n_points_on_diameter=inputs[1], mu=inputs[2])
    actual_grid_sorted = sorted(actual_gs.grid)
    expected_grid_sorted = sorted(expected_grid)
    for actual_point, expected_point in zip(actual_grid_sorted, expected_grid_sorted):
        assert actual_point == pytest.approx(expected_point, rel=1e-4, abs=1e-6)


params2 = [
    ([1, 3, 1, 45], [0, 1.4142135, 1.4142135, 2, 2]),
    ([1, 3, 1, 90], [0, 0, 2, 2, 2]),
    ([1, 3, 1, 120], [0, 0, 2, 3, 1.73205]),
    ([1, 4, 1, 30], [2.057347, 2.044451, 1.621801, 1.813330]),
    ([1, 4, 1, 90], [1.885618, 1.885618, 2.552285, 1.218951]),
    ([1, 4, 1, 140], [1.139021, 2.200102, 2.744909, 1.451264]),
]


@pytest.mark.parametrize("inputs, expected", params2)
def test_set_distances_at_angle(inputs, expected):
    expected_distances = expected
    actual_gs = Gridded_circle(radius=inputs[0], n_points_on_diameter=inputs[1], mu=inputs[2])
    actual_gs.set_distances_at_angle(inputs[3])
    actual_distances_sorted = sorted(actual_gs.distances)
    expected_distances_sorted = sorted(expected_distances)
    assert actual_distances_sorted == pytest.approx(expected_distances_sorted, rel=1e-4, abs=1e-6)


params3 = [
    ([1], [1, 1, 0.135335, 0.049787, 0.176921]),
    ([2], [1, 1, 0.018316, 0.002479, 0.031301]),
]


@pytest.mark.parametrize("inputs, expected", params3)
def test_set_muls_at_angle(inputs, expected):
    expected_muls = expected
    actual_gs = Gridded_circle(radius=1, n_points_on_diameter=3, mu=inputs[0])
    actual_gs.set_muls_at_angle(120)
    actual_muls_sorted = sorted(actual_gs.muls)
    expected_muls_sorted = sorted(expected_muls)
    assert actual_muls_sorted == pytest.approx(expected_muls_sorted, rel=1e-4, abs=1e-6)


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


def test_compute_cve(mocker):
    xarray, yarray = np.array([90, 90.1, 90.2]), np.array([2, 2, 2])
    expected_cve = np.array([0.5, 0.5, 0.5])
    mocker.patch("diffpy.labpdfproc.functions.TTH_GRID", xarray)
    mocker.patch("numpy.interp", return_value=expected_cve)
    input_pattern = _instantiate_test_do(xarray, yarray)
    actual_cve_do = compute_cve(input_pattern, mud=1)
    expected_cve_do = _instantiate_test_do(
        xarray,
        expected_cve,
        name="absorption correction, cve, for test",
        scat_quantity="cve",
    )
    assert actual_cve_do == expected_cve_do


params_cve_bad = [
    (
        [7, "polynomial_interpolation"],
        [
            f"mu*D is out of the acceptable range (0.5 to 6) for polynomial interpolation. "
            f"Please rerun with a value within this range or specifying another method from {* CVE_METHODS, }."
        ],
    ),
    ([1, "invalid_method"], [f"Unknown method: invalid_method. Allowed methods are {*CVE_METHODS, }."]),
    ([7, "invalid_method"], [f"Unknown method: invalid_method. Allowed methods are {*CVE_METHODS, }."]),
]


@pytest.mark.parametrize("inputs, msg", params_cve_bad)
def test_compute_cve_bad(mocker, inputs, msg):
    xarray, yarray = np.array([90, 90.1, 90.2]), np.array([2, 2, 2])
    expected_cve = np.array([0.5, 0.5, 0.5])
    mocker.patch("diffpy.labpdfproc.functions.TTH_GRID", xarray)
    mocker.patch("numpy.interp", return_value=expected_cve)
    input_pattern = _instantiate_test_do(xarray, yarray)
    with pytest.raises(ValueError, match=re.escape(msg[0])):
        compute_cve(input_pattern, mud=inputs[0], method=inputs[1])


def test_apply_corr(mocker):
    xarray, yarray = np.array([90, 90.1, 90.2]), np.array([2, 2, 2])
    expected_cve = np.array([0.5, 0.5, 0.5])
    mocker.patch("diffpy.labpdfproc.functions.TTH_GRID", xarray)
    mocker.patch("numpy.interp", return_value=expected_cve)
    input_pattern = _instantiate_test_do(xarray, yarray)
    absorption_correction = _instantiate_test_do(
        xarray,
        expected_cve,
        name="absorption correction, cve, for test",
        scat_quantity="cve",
    )
    actual_corr = apply_corr(input_pattern, absorption_correction)
    expected_corr = _instantiate_test_do(xarray, np.array([1, 1, 1]))
    assert actual_corr == expected_corr
