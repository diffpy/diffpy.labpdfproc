import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

TTH_GRID = np.arange(1, 180.1, 0.1)
MUD_LIST = [0.5, 1, 2, 3, 4, 5, 6]
INVERSE_CVE_DATA = np.loadtxt("data/inverse_cve.xy")
COEFFICIENT_LIST = pd.read_csv("data/coefficient_list.csv", header=None)
INTERPOLATION_FUNCTIONS = [interp1d(MUD_LIST, coefficients, kind="quadratic") for coefficients in COEFFICIENT_LIST]
