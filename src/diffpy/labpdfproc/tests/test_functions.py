import pytest

from diffpy.labpdfproc.functions import Gridded_circle

params2 = [
    ([1, 3, 1, 45], [0, 1.4142135, 1.4142135, 2, 2]),
    ([1, 3, 1, 90], [0, 0, 2, 2, 2]),
    ([1, 3, 1, 140], [0, 2, 0, 3.5320888862379562, 1.2855752193730785]),
]


@pytest.mark.parametrize("inputs, expected", params2)
def test_set_distances_at_angle(inputs, expected):
    expected_distances = expected
    actual_gs = Gridded_circle(radius=inputs[0], n_points_on_diameter=inputs[1], mu=inputs[2])
    actual_gs.set_distances_at_angle(inputs[3])
    assert actual_gs.distances == pytest.approx(expected_distances, rel=1e-4, abs=1e-6)
