import numpy as np

from diffpy.labpdfproc.fast_cve import FAST_TTH_GRID, INVERSE_CVE_DATA, fast_compute_cve


def test_fast_compute_cve():
    expected_tth_grid = FAST_TTH_GRID
    expected_cve = 1 / np.array(INVERSE_CVE_DATA)
    actual_tth_grid, actual_cve = fast_compute_cve(mud=1)
    assert np.allclose(actual_tth_grid, expected_tth_grid)
    assert np.allclose(actual_cve, expected_cve, rtol=1e-5)
