from diffpy.utils.scattering_objects.diffraction_objects import Diffraction_object
from absorption.functions import Gridded_circle
import numpy as np

wavelengths = {"Mo": 0.7107, "Ag": 0.59}
def compute_cve(diffraction_data, mud, wavelength):
    # this function takes the original diffraction data, mu*D, and wavelength
    # and returns a new diffraction object (DO) with muls curves
    # where cve=1/muls (or muls=1/cve)

    # resample data and absorption correction to more reasonable grid
    # calculate corresponding cve for the given mud in resampled grid
    radius_mm = 1
    n_points_on_diameter = 249
    mu_sample_invmm = mud/2
    tth_grid = np.arange(1, 141, 1)
    abs_correction = Gridded_circle(radius_mm, n_points_on_diameter, mu=mu_sample_invmm)
    distances, muls = [], []

    for angle in tth_grid:
        abs_correction.set_distances_at_angle(angle)
        abs_correction.set_muls_at_angle(angle)
        distances.append(sum(abs_correction.distances))
        muls.append(sum(abs_correction.muls))
    distances = np.array(distances) / abs_correction.total_points_in_grid
    muls = np.array(muls) / abs_correction.total_points_in_grid

    # interpolate muls to the original grid in diffraction_data
    # this gives us the cve we need to multiply for the correction
    orig_grid = diffraction_data.on_tth[0]
    newmuls = np.interp(orig_grid, tth_grid, muls)

    abdo = Diffraction_object(wavelength=wavelength)
    abdo.insert_scattering_quantity(orig_grid, newmuls, "tth")

    return abdo


def apply_corr(modo, abdo):
    # we apply the absorption correction by doing: I(tth) * c_ve
    abscormodo = modo * (1/ abdo)
    #print(modo.on_tth[0])
    #print(modo.on_tth[1])
    #print(abdo.on_tth[0])
    #print(abdo.on_tth[1])
    #print(abscormodo.on_tth[0])
    #print(abscormodo.on_tth[1])
    return abscormodo


#def dump(base_name, do):
#    data_to_save = np.column_stack((do.on_tth[0], do.on_tth[1]))
#    np.savetxt(f'{base_name}_proc.chi', data_to_save)