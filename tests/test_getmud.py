import pytest

from diffpy.labpdfproc.getmud import estimate_diameter, estimate_mass_density


@pytest.mark.parametrize(
    "inputs, expected_mass_density",
    [
        (
            {
                "mud": 2.0,
                "diameter": 1.5,
                "sample_composition": "ZrO2",
                "energy": 20,
            },
            0.25,
        ),
    ],
)
def test_estimate_mass_density(inputs, expected_mass_density):
    actual_mass_density = estimate_mass_density(
        inputs["mud"],
        inputs["diameter"],
        inputs["sample_composition"],
        inputs["energy"],
    )
    assert actual_mass_density == pytest.approx(
        expected_mass_density, rel=0.01, abs=0.1
    )


@pytest.mark.parametrize(
    "inputs, expected_diameter",
    [
        (  # C1: user specifies a sample mass density
            {
                "mud": 2.0,
                "sample_composition": "ZrO2",
                "energy": 20,
                "sample_mass_density": 0.25,
            },
            1.5,
        ),
        # (   # C2: user specifies a packing fraction
        #     {
        #         "mud": 2.0,
        #         "sample_composition": "ZrO2",
        #         "energy": 20,
        #         "packing_fraction": 0.3
        #     },
        #     1.5
        # ),
    ],
)
def test_estimate_diameter(inputs, expected_diameter):
    actual_diameter = estimate_diameter(**inputs)
    assert actual_diameter == pytest.approx(
        expected_diameter, rel=0.01, abs=0.1
    )
