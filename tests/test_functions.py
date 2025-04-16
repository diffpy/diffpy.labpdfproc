import re

import numpy as np
import pytest

from diffpy.labpdfproc.functions import (
    CVE_METHODS,
    Gridded_circle,
    apply_corr,
    compute_cve,
)
from diffpy.utils.diffraction_objects import DiffractionObject


@pytest.mark.parametrize(
    "inputs, expected_grid",
    [
        (
            {"radius": 0.5, "n_points_on_diameter": 3, "mu": 1},
            {(0.0, -0.5), (0.0, 0.0), (0.5, 0.0), (-0.5, 0.0), (0.0, 0.5)},
        ),
        (
            {"radius": 1, "n_points_on_diameter": 4, "mu": 1},
            {
                (-0.333333, -0.333333),
                (0.333333, -0.333333),
                (-0.333333, 0.333333),
                (0.333333, 0.333333),
            },
        ),
    ],
)
def test_get_grid_points(inputs, expected_grid):
    actual_gs = Gridded_circle(
        radius=inputs["radius"],
        n_points_on_diameter=inputs["n_points_on_diameter"],
        mu=inputs["mu"],
    )
    actual_grid_sorted = sorted(actual_gs.grid)
    expected_grid_sorted = sorted(expected_grid)
    for actual_pt, expected_pt in zip(
        actual_grid_sorted, expected_grid_sorted
    ):
        assert actual_pt == pytest.approx(expected_pt, rel=1e-4, abs=1e-6)


@pytest.mark.parametrize(
    "inputs, expected_distances",
    [
        (
            {"radius": 1, "n_points_on_diameter": 3, "mu": 1, "angle": 45},
            [0, 1.4142135, 1.4142135, 2, 2],
        ),
        (
            {"radius": 1, "n_points_on_diameter": 3, "mu": 1, "angle": 90},
            [0, 0, 2, 2, 2],
        ),
        (
            {"radius": 1, "n_points_on_diameter": 3, "mu": 1, "angle": 120},
            [0, 0, 2, 3, 1.73205],
        ),
        (
            {"radius": 1, "n_points_on_diameter": 4, "mu": 1, "angle": 30},
            [2.057347, 2.044451, 1.621801, 1.813330],
        ),
        (
            {"radius": 1, "n_points_on_diameter": 4, "mu": 1, "angle": 90},
            [1.885618, 1.885618, 2.552285, 1.218951],
        ),
        (
            {"radius": 1, "n_points_on_diameter": 4, "mu": 1, "angle": 140},
            [1.139021, 2.200102, 2.744909, 1.451264],
        ),
    ],
)
def test_set_distances_at_angle(inputs, expected_distances):
    actual_gs = Gridded_circle(
        radius=inputs["radius"],
        n_points_on_diameter=inputs["n_points_on_diameter"],
        mu=inputs["mu"],
    )
    actual_gs.set_distances_at_angle(inputs["angle"])
    actual_distances_sorted = sorted(actual_gs.distances)
    expected_distances_sorted = sorted(expected_distances)
    assert actual_distances_sorted == pytest.approx(
        expected_distances_sorted, rel=1e-4, abs=1e-6
    )


@pytest.mark.parametrize(
    "input_mu, expected_muls",
    [
        (1, [1, 1, 0.135335, 0.049787, 0.176921]),
        (2, [1, 1, 0.018316, 0.002479, 0.031301]),
    ],
)
def test_set_muls_at_angle(input_mu, expected_muls):
    actual_gs = Gridded_circle(radius=1, n_points_on_diameter=3, mu=input_mu)
    actual_gs.set_muls_at_angle(120)
    actual_muls_sorted = sorted(actual_gs.muls)
    expected_muls_sorted = sorted(expected_muls)
    assert actual_muls_sorted == pytest.approx(
        expected_muls_sorted, rel=1e-4, abs=1e-6
    )


@pytest.mark.parametrize(
    "input_diffraction_data, input_cve_params",
    [  # Test that cve diffraction object contains the expected info
        # Note that all cve values are interpolated to 0.5
        # cve do should contain the same input xarray, xtype,
        # wavelength, and metadata
        (  # C1: User did not specify method, default to fast calculation
            {
                "xarray": np.array([90, 90.1, 90.2]),
                "yarray": np.array([2, 2, 2]),
            },
            {"mud": 1, "xtype": "tth"},
        ),
        (  # C2: User specified brute-force computation method
            {
                "xarray": np.array([5.1, 5.2, 5.3]),
                "yarray": np.array([2, 2, 2]),
            },
            {"mud": 1, "method": "brute_force", "xtype": "q"},
        ),
        (  # C3: User specified mu*D outside the fast calculation range,
            # default to brute-force computation
            {
                "xarray": np.array([5.1, 5.2, 5.3]),
                "yarray": np.array([2, 2, 2]),
            },
            {"mud": 20, "xtype": "q"},
        ),
    ],
)
def test_compute_cve(mocker, input_diffraction_data, input_cve_params):
    expected_xarray = input_diffraction_data["xarray"]
    expected_cve = np.array([0.5, 0.5, 0.5])
    expected_xtype = input_cve_params["xtype"]
    mocker.patch("diffpy.labpdfproc.functions.N_POINTS_ON_DIAMETER", 4)
    mocker.patch("numpy.interp", return_value=expected_cve)
    input_pattern = DiffractionObject(
        xarray=input_diffraction_data["xarray"],
        yarray=input_diffraction_data["yarray"],
        xtype=input_cve_params["xtype"],
        wavelength=1.54,
        scat_quantity="x-ray",
        name="test",
        metadata={"thing1": 1, "thing2": "thing2"},
    )
    actual_cve_do = compute_cve(input_pattern, **input_cve_params)
    expected_cve_do = DiffractionObject(
        xarray=expected_xarray,
        yarray=expected_cve,
        xtype=expected_xtype,
        wavelength=1.54,
        scat_quantity="cve",
        name="absorption correction, cve, for test",
        metadata={"thing1": 1, "thing2": "thing2"},
    )
    assert actual_cve_do == expected_cve_do


def test_compute_cve_bad(mocker):
    xarray, yarray = np.array([90, 90.1, 90.2]), np.array([2, 2, 2])
    expected_cve = np.array([0.5, 0.5, 0.5])
    mocker.patch("numpy.interp", return_value=expected_cve)
    input_pattern = DiffractionObject(
        xarray=xarray,
        yarray=yarray,
        xtype="tth",
        wavelength=1.54,
        scat_quantity="x-ray",
        name="test",
        metadata={"thing1": 1, "thing2": "thing2"},
    )
    # Test that the function raises a ValueError
    # when an invalid method is provided
    with pytest.raises(
        ValueError,
        match=re.escape(
            f"Unknown method: invalid_method. "
            f"Allowed methods are {*CVE_METHODS, }."
        ),
    ):
        compute_cve(input_pattern, mud=1, method="invalid_method")


def test_apply_corr(mocker):
    xarray, yarray = np.array([90, 90.1, 90.2]), np.array([2, 2, 2])
    expected_cve = np.array([0.5, 0.5, 0.5])
    mocker.patch("numpy.interp", return_value=expected_cve)
    input_pattern = DiffractionObject(
        xarray=xarray,
        yarray=yarray,
        xtype="tth",
        wavelength=1.54,
        scat_quantity="x-ray",
        name="test",
        metadata={"thing1": 1, "thing2": "thing2"},
    )
    absorption_correction = DiffractionObject(
        xarray=xarray,
        yarray=expected_cve,
        xtype="tth",
        wavelength=1.54,
        scat_quantity="cve",
        name="absorption correction, cve, for test",
        metadata={"thing1": 1, "thing2": "thing2"},
    )
    actual_corr = apply_corr(input_pattern, absorption_correction)
    expected_corr = DiffractionObject(
        xarray=xarray,
        yarray=np.array([1, 1, 1]),
        xtype="tth",
        wavelength=1.54,
        scat_quantity="x-ray",
        name="test",
        metadata={"thing1": 1, "thing2": "thing2"},
    )
    assert actual_corr == expected_corr
