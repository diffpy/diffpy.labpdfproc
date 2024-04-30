import argparse
from pathlib import Path

import pytest

from diffpy.labpdfproc.tools import set_output_directory

params1 = [
    ([None], [Path.cwd()]),
    (["corrected"], [Path("corrected").resolve()]),
]


@pytest.mark.parametrize("inputs, expected", params1)
def test_set_output_directory(inputs, expected):
    expected_output_directory = expected[0]
    actual_args = argparse.Namespace(output_directory=inputs[0])
    actual_output_directory = set_output_directory(actual_args)
    assert actual_output_directory == expected_output_directory
