import pytest

from diffpy.labpdfproc.getmud import get_diameter


@pytest.mark.parametrize(
    "inputs, expected_diameter",
    [
        (  # C1: User specifies target mud,
            # sample composition, energy, and mass density
            # expect to return diameter
            {
                "mud": 2.0,
                "sample_composition": "ZrO2",
                "xray_energy": 17.45,
                "sample_mass_density": 1.20,
            },
            1.3439,
        ),
    ],
)
def test_compute_diameter(inputs, expected_diameter):
    actual_diameter = get_diameter(**inputs)
    assert actual_diameter == pytest.approx(
        expected_diameter, rel=0.01, abs=0.1
    )
