import os

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

FAST_TTH_GRID = np.arange(1, 180.1, 0.1)
MUD_LIST = [0.5, 1, 2, 3, 4, 5, 6]
CWD = os.path.dirname(os.path.abspath(__file__))
INVERSE_CVE_DATA = np.loadtxt(CWD + "/data/inverse_cve.xy")
COEFFICIENT_LIST = np.array(pd.read_csv(CWD + "/data/coefficient_list.csv", header=None))
INTERPOLATION_FUNCTIONS = [interp1d(MUD_LIST, coefficients, kind="quadratic") for coefficients in COEFFICIENT_LIST]


def fast_compute_cve(mud):
    """
    use precomputed datasets to compute the cve for given mud

    Parameters
    ----------
    mud float
      the mu*D of the diffraction object, where D is the diameter of the circle

    Returns
    -------
    the array of tth grid and the corresponding cve
    """

    coefficient_a, coefficient_b, coefficient_c, coefficient_d, coefficient_e = [
        interpolation_function(mud) for interpolation_function in INTERPOLATION_FUNCTIONS
    ]
    inverse_cve = (
        coefficient_a * INVERSE_CVE_DATA**4
        + coefficient_b * INVERSE_CVE_DATA**3
        + coefficient_c * INVERSE_CVE_DATA**2
        + coefficient_d * INVERSE_CVE_DATA**1
        + coefficient_e
    )
    cve = 1 / np.array(inverse_cve)
    return FAST_TTH_GRID, cve
