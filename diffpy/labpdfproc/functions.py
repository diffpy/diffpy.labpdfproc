from diffpy.utils.scattering_objects.diffraction_objects import Diffraction_object

wavelengths = {"Mo": 0.7107, "Ag": 0.59}
def compute_cve(diffraction_data, mud, wavelength):
    # for a given mu and d and lambda, we will compute cve on a tth grid
    # something arbitrary for the moment

    # calculate corresponding cve for the given mud
    radius_mm = 1
    n_points_on_diameter = 249
    mu = mud/2
    tth_grid = np.arange(1, 141, 1)
    abs_correction = Gridded_circle(radius_mm, n_points_on_diameter, mu=mu)
    distances, muls = [], []

    for angle in tth_grid:
        abs_correction.set_distances_at_angle(angle)
        abs_correction.set_muls_at_angle(angle)
        distances.append(sum(abs_correction.distances))
        muls.append(sum(abs_correction.muls))
    distances = np.array(distances) / abs_correction.total_points_in_grid
    muls = np.array(muls) / abs_correction.total_points_in_grid

    # interpolate
    cve = Diffraction_object(wavelength=wavelength)
    cve_x = diffraction_data.on_tth[0]
    cve_y = np.interp(cve_x, tth_grid, muls)
    cve.insert_scattering_quantity(cve_x, cve_y, "tth", metadata={})
    return cve


def apply_corr(i_m, cve):
    # we apply the absorption correction by doing: I(tth) * c_ve
    i_c = i_m / cve.on_tth[1]
    return i_c
