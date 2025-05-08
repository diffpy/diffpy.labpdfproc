from diffpy.utils.tools import compute_mu_using_xraydb


def get_diameter(
    mud,
    sample_composition,
    xray_energy,
    sample_mass_density=None,
    packing_fraction=None,
):
    """
    Compute capillary diameter (mm) from muD, sample composition, energy,
    and either sample mass density or packing fraction.

    Parameters
    ----------
    mud : float
        The given muD of the sample.
    sample_composition : str
        The chemical formula of the material (e.g. "ZrO2").
    xray_energy : float
        The energy of the incident x-rays in keV.
    sample_mass_density : float, optional
        The mass density of the packed sample in g/cm^3.
    packing_fraction : float, optional
        The packing fraction of the sample (0–1).

    Returns
    -------
    diameter : float
        Computed capillary diameter in mm.
    """
    return mud / compute_mu_using_xraydb(
        sample_composition,
        xray_energy,
        sample_mass_density,
        packing_fraction,
    )
