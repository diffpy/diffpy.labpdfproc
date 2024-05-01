from argparse import ArgumentParser

import pytest

from diffpy.labpdfproc.tools import load_user_metadata

params5 = [
    ([[]], []),
    ([["toast=for breakfast"]], [["toast", "for breakfast"]]),
    ([["mylist=[1,2,3.0]"]], [["mylist", "[1,2,3.0]"]]),
    ([["weather=rainy", "day=tuesday"]], [["weather", "rainy"], ["day", "tuesday"]]),
]


@pytest.mark.parametrize("inputs, expected", params5)
def test_load_additional_info(inputs, expected):
    actual_parser = ArgumentParser()
    actual_parser.add_argument("-u", "--user-metadata", action="append", metavar=("KEY=VALUE"))
    actual_args = actual_parser.parse_args([])
    expected_parser = ArgumentParser()
    expected_args = expected_parser.parse_args([])

    setattr(actual_args, "user_metadata", inputs[0])
    actual_args = load_user_metadata(actual_args)
    for expected_pair in expected:
        setattr(expected_args, expected_pair[0], expected_pair[1])
    assert actual_args == expected_args
