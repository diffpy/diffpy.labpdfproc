from pathlib import Path

import numpy as np
import pytest

from diffpy.labpdfproc.mud_calculator import _extend_z_and_convolve, compute_mud


def test_compute_mud(tmp_path):
    diameter, slit_width, z0, I0, mud, slope = 1, 0.1, 0, 1e5, 3, 0
    z_data = np.linspace(-1, 1, 50)
    convolved_I_data = _extend_z_and_convolve(z_data, diameter, slit_width, z0, I0, mud, slope)

    directory = Path(tmp_path)
    file = directory / "testfile"
    with open(file, "w") as f:
        for x, I in zip(z_data, convolved_I_data):
            f.write(f"{x}\t{I}\n")

    expected_mud = 3
    actual_mud = compute_mud(file)
    assert actual_mud == pytest.approx(expected_mud, rel=0.01, abs=0.1)
