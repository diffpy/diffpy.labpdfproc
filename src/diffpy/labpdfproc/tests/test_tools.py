import argparse
import re

import pytest

from diffpy.labpdfproc.tools import known_sources, set_wavelength

params2 = [
    ([None, None], [0.71]),
    ([None, "Ag"], [0.59]),
    ([0.25, "Ag"], [0.25]),
    ([0.25, None], [0.25]),
]


@pytest.mark.parametrize("inputs, expected", params2)
def test_set_wavelength(inputs, expected):
    expected_wavelength = expected[0]
    actual_args = argparse.Namespace(wavelength=inputs[0], anode_type=inputs[1])
    actual_wavelength = set_wavelength(actual_args)
    assert actual_wavelength == expected_wavelength


params3 = [
    (
        [None, "invalid"],
        [f"Anode type not recognized. please rerun specifying an anode_type from {*known_sources, }"],
    ),
    ([0, None], ["No valid wavelength. Please rerun specifying a known anode_type or a positive wavelength"]),
    ([-1, "Mo"], ["No valid wavelength. Please rerun specifying a known anode_type or a positive wavelength"]),
]


@pytest.mark.parametrize("inputs, msg", params3)
def test_set_wavelength_bad(inputs, msg):
    actual_args = argparse.Namespace(wavelength=inputs[0], anode_type=inputs[1])
    with pytest.raises(ValueError, match=re.escape(msg[0])):
        actual_args.wavelength = set_wavelength(actual_args)
