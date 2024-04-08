import pytest

from diffpy.labpdfproc.functions import Gridded_circle

# Define test parameters
params1 = [
    ([0.5, 3, 1, {(0.0, -0.5), (0.0, 0.0), (-0.5, 0.0), (0.5, 0.0), (0.0, 0.5)}, 5]),
    ([1, 4, 1, {(-0.333333, -0.333333), (0.333333, -0.333333), (-0.333333, 0.333333), (0.333333, 0.333333)}, 4]),
]


# Define the test function
@pytest.mark.parametrize("params1", params1)
def test_get_grid_points(params1):
    radius, n_points_on_diameter, mu, expected_grid, expected_total_points = params1

    # Perform the test
    actual_gs = Gridded_circle(radius=radius, n_points_on_diameter=n_points_on_diameter, mu=mu)

    # Sort both sets of points to compare
    actual_grid_sorted = sorted(actual_gs.grid)
    expected_grid_sorted = sorted(expected_grid)

    # Assertions
    assert actual_gs.total_points_in_grid == expected_total_points
    for actual_point, expected_point in zip(actual_grid_sorted, expected_grid_sorted):
        assert actual_point == pytest.approx(expected_point, rel=1e-4, abs=1e-6)
