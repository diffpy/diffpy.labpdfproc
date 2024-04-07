import numpy as np
import pytest

from diffpy.labpdfproc.functions import Gridded_circle

params1 = [
    [[1, 3, 1, {(0.0, -1.0), (0.0, 0.0), (-1.0, 0.0), (1.0, 0.0), (0.0, 1.0)}, 5]],
    [[0.2, 8, 1, {(-0.08571428571428572, -0.14285714285714285), (-0.02857142857142858, -0.14285714285714285), (0.02857142857142858, -0.14285714285714285), (0.08571428571428574, -0.14285714285714285), (-0.14285714285714285, -0.08571428571428572), (-0.08571428571428572, -0.08571428571428572), (-0.02857142857142858, -0.08571428571428572), (0.02857142857142858, -0.08571428571428572), (0.08571428571428574, -0.08571428571428572), (0.14285714285714285, -0.08571428571428572), (-0.14285714285714285, -0.02857142857142858), (-0.08571428571428572, -0.02857142857142858), (-0.02857142857142858, -0.02857142857142858), (0.02857142857142858, -0.02857142857142858), (0.08571428571428574, -0.02857142857142858), (0.14285714285714285, -0.02857142857142858), (-0.14285714285714285, 0.02857142857142858), (-0.08571428571428572, 0.02857142857142858), (-0.02857142857142858, 0.02857142857142858), (0.02857142857142858, 0.02857142857142858), (0.08571428571428574, 0.02857142857142858), (0.14285714285714285, 0.02857142857142858), (-0.14285714285714285, 0.08571428571428574), (-0.08571428571428572, 0.08571428571428574), (-0.02857142857142858, 0.08571428571428574), (0.02857142857142858, 0.08571428571428574), (0.08571428571428574, 0.08571428571428574), (0.14285714285714285, 0.08571428571428574), (-0.08571428571428572, 0.14285714285714285), (-0.02857142857142858, 0.14285714285714285), (0.02857142857142858, 0.14285714285714285), (0.08571428571428574, 0.14285714285714285)}, 32]]
]

@pytest.mark.parametrize('params1', params1)
def test_get_grid_points(params1):
    for param_set in params1:
        radius, n_points_on_diameter, mu, expected_grid, expected_total_points = param_set
        actual_gs = Gridded_circle(radius=radius, n_points_on_diameter=n_points_on_diameter, mu=mu)
        assert actual_gs.grid == expected_grid
        assert actual_gs.total_points_in_grid == expected_total_points



# values of distances are correct but im a bit confused about the order of distances
params2 = [
    [[1, 3, 1, [25, 90, 140],
     [[0, 2, 1.81261557406, 2, 0.845236523481399],
      [0, 2, 0, 2, 2],
      [0, 2, 0, 3.5320888862379562, 1.2855752193730785]]]],
    [[0.3, 6, 1, [14, 90, 120],
      [[0.5480340818997349, 0.5354482281467614, 0.601285995493114, 0.6027483291753729, 0.6034715865980909, 0.578005471973011, 0.4947788959442535, 0.5960138080070901, 0.5562896419944887, 0.5686908551742735, 0.45192085857776143, 0.427513512087355, 0.5844112402440541, 0.47163573802449577, 0.5181699073501158, 0.3969934749877318],
       [0.48, 0.6539387691339813, 0.7078775382679627, 0.41393876913398137, 0.5878775382679627, 0.5878775382679627, 0.84, 0.7739387691339814, 0.29393876913398137, 0.46787753826796274, 0.41393876913398137, 0.29393876913398137, 0.6539387691339813, 0.48, 0.7739387691339814, 0.12],
       [0.2977588782576409, 0.5701702621142971, 0.7350953659368239, 0.31137200214817157, 0.5444870368999288, 0.6205639884457963, 0.9585605421126093, 0.8882109144555469, 0.24428786600141425, 0.45117231748269127, 0.4384011167518993, 0.2916941133177683, 0.747448953694039, 0.5259897328952432, 0.7834632586801662, 0.10679139675021132]]]
    ]
]

@pytest.mark.parametrize('params2', params2)
def test_set_distances_at_angle(params2):
    for param_set in params2:
        radius, n_points_on_diameter, mu, angles, expected_distances = param_set
        actual_gs = Gridded_circle(radius=radius, n_points_on_diameter=n_points_on_diameter, mu=mu)
        for angle, expected_distance in zip(angles, expected_distances):
            actual_gs.set_distances_at_angle(angle)
            assert actual_gs.distances == pytest.approx(expected_distance, rel=1e-4, abs=1e-6)



params3 = [
    [1, 3, 2, [25, 90, 140],
     [[1, 0.01831563888, 0.02664293815, 0.01831563888, 0.18443225823],
      [1, 0.01831563888, 1, 0.01831563888, 0.01831563888],
      [1, 0.01831563888, 1, 0.00085519779, 0.07644754659]]]
]
@pytest.mark.parametrize('params3', params3)
def test_set_muls_at_angle(params3):
    radius, n_points_on_diameter, mu, angles, expected_muls = params3
    actual_gs = Gridded_circle(radius=radius, n_points_on_diameter=n_points_on_diameter, mu=mu)
    for angle, expected_mul in zip(angles, expected_muls):
        # here it seems like I need to set distances first (can't assign distances only using set muls)
        # but there is a function setting distances if distance is empty ... will check this
        actual_gs.set_distances_at_angle(angle)
        actual_gs.set_muls_at_angle(angle)
        assert actual_gs.muls == pytest.approx(expected_mul, rel=1e-4, abs=1e-6)



# the other functions are get_path_length, get_entry_exit_coordinates, compute_cve, and apply_corr
# it seems that get_path_length and get_entry_exit_coordinates functions are already included in set_distances
