import numpy as np
from scipy.optimize import newton

from diffpy.utils.tools import compute_mu_using_xraydb


def estimate_mass_density(mud, diameter, sample_composition, energy):
    """Estimate sample mass density (g/cm^3) from mu*D
    using capillary diameter, sample composition, and energy.

    Parameters
    ----------
    mud : float
        The given product of attenuation coefficient mu
        in mm^{-1} and capillary diameter in mm.
    diameter : float
        The given diameter of the sample capillary in mm.
    sample_composition : str
        The chemical formula of the material.
    energy : float
        The energy of the incident x-rays in keV.

    Returns
    -------
    estimated_density : float
        The estimated mass density of the packed powder/sample in g/cm^3.
    """
    mu = mud / diameter

    def residual_density(density):
        return np.abs(
            compute_mu_using_xraydb(
                sample_composition, energy, sample_mass_density=density
            )
            - mu
        )

    estimated_density = newton(residual_density, x0=1.0, x1=10.0)
    return estimated_density


def estimate_diameter(
    mud,
    sample_composition,
    energy,
    sample_mass_density=None,
    packing_fraction=None,
):
    """Estimate capillary diameter (mm) from mu*D and mu.

    Parameters
    ----------
    mud : float
        The given product of attenuation coefficient mu
        in mm^{-1} and capillary diameter in mm.
    sample_composition : str
        The chemical formula of the material.
    energy : float
        The energy of the incident x-rays in keV.
    sample_mass_density : float
        The mass density of the packed powder/sample in g/cm^3.
    packing_fraction : float, optional, Default is None
        The fraction of sample in the capillary (between 0 and 1).
        Specify either sample_mass_density or packing_fraction but not both.

    Returns
    -------
    diameter : float
        The given diameter of the sample capillary in mm.
    """
    mu = compute_mu_using_xraydb(
        sample_composition, energy, sample_mass_density, packing_fraction
    )
    return mud / mu
