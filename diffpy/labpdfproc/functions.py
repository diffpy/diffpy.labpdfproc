from diffpy.utils.scattering_objects.diffraction_objects import Diffraction_object

wavelengths = {"Mo": 0.7107, "Ag": 0.59}
def compute_cve(diffraction_data, mud, wavelength):
    # for a given mu and d and lambda, we will compute cve on a tth grid
    # something arbitrary for the moment
    cve = Diffraction_object()
    cve_x = diffraction_data.on_tth[0]
    cve_y = cve_x * mud * wavelength
    cve.insert_scattering_quantity(cve_x, cve_y, "tth", metadata={ })
    return cve

def apply_corr(i_m, cve):
    # we apply the absorption correction by doing: I(tth) * c_ve
    i_c = i_m * cve
    return i_c
