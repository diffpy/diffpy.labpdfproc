from argparse import ArgumentParser

import pytest

from diffpy.labpdfproc.tools import load_additional_info

params5 = [
    ([], []),
    ([["weather=rainy"]], [["weather", "rainy"]]),
    ([["weather=rainy", "day=tuesday"]], [["weather", "rainy"], ["day", "tuesday"]]),
]


@pytest.mark.parametrize("inputs, expected", params5)
def test_load_additional_info(inputs, expected):
    actual_parser = ArgumentParser()
    actual_parser.add_argument("-add", "--additional-info", action="append", metavar=("KEY=VALUE"))
    actual_args = actual_parser.parse_args([])
    expected_parser = ArgumentParser()
    expected_args = expected_parser.parse_args([])

    if not inputs:
        actual_args = load_additional_info(actual_args)
        assert actual_args == expected_args
    else:
        setattr(actual_args, "additional_info", inputs[0])
        actual_args = load_additional_info(actual_args)
        for expected_pair in expected:
            setattr(expected_args, expected_pair[0], expected_pair[1])
        assert actual_args == expected_args
