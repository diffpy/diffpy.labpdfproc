import pytest

from diffpy.labpdfproc.getmud import compute_diameter


@pytest.mark.parametrize(
    "inputs, expected_diameter",
    [
        (
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
    actual_diameter = compute_diameter(**inputs)
    assert actual_diameter == pytest.approx(
        expected_diameter, rel=0.01, abs=0.1
    )
