import numpy as np
import pytest

from diffpy.labpdfproc.functions import Gridded_circle


def test_get_grid_points():
    actual_gs = Gridded_circle(radius=1, n_points_on_diameter=3, mu=1)
    expected_gs = Gridded_circle()
    expected_gs.grid = {(0.0, -1.0), (0.0, 0.0), (-1.0, 0.0), (1.0, 0.0), (0.0, 1.0)}
    expected_gs.total_points_in_grid = 5
    assert actual_gs.grid == expected_gs.grid
    assert actual_gs.total_points_in_grid == expected_gs.total_points_in_grid


@pytest.mark.parametrize("angle, expected_distances", [
    (25, [0, 2, 1.81261557406, 2, 0.845236523481399]),
    (90, [0, 2, 0, 2, 2]),
    (140, [0, 2, 0, 3.5320888862379562, 1.2855752193730785]),
])
def test_set_distances_at_angle(angle, expected_distances):
    actual_gs = Gridded_circle(radius=1, n_points_on_diameter=3, mu=1)
    actual_gs.set_distances_at_angle(angle)
    assert actual_gs.distances == pytest.approx(expected_distances, rel=1e-4, abs=1e-6)