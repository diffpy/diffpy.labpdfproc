import argparse
from argparse import ArgumentParser

import pytest

from diffpy.labpdfproc.tools import load_user_metadata, set_wavelength

params5 = [
    ([[]], []),
    ([["toast=for breakfast"]], [["toast", "for breakfast"]]),
    ([["mylist=[1,2,3.0]"]], [["mylist", "[1,2,3.0]"]]),
    ([["weather=rainy", "day=tuesday"]], [["weather", "rainy"], ["day", "tuesday"]]),
]


@pytest.mark.parametrize("inputs, expected", params5)
def test_load_user_metadata(inputs, expected):
    actual_parser = ArgumentParser()
    actual_parser.add_argument("-u", "--user-metadata", action="append", metavar="KEY=VALUE", nargs="+")
    actual_args = actual_parser.parse_args([])
    expected_parser = ArgumentParser()
    expected_args = expected_parser.parse_args([])

    setattr(actual_args, "user_metadata", inputs[0])
    actual_args = load_user_metadata(actual_args)
    for expected_pair in expected:
        setattr(expected_args, expected_pair[0], expected_pair[1])
    assert actual_args == expected_args


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
    ([None, "invalid"]),
    ([0, None]),
    ([-1, "Mo"]),
]


@pytest.mark.parametrize("inputs", params3)
def test_set_wavelength_bad(inputs):
    with pytest.raises(ValueError):
        actual_args = argparse.Namespace(wavelength=inputs[0], anode_type=inputs[1])
        actual_args.wavelength = set_wavelength(actual_args)
