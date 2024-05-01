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
    actual_args.output_directory = set_output_directory(actual_args)
    assert actual_args.output_directory == expected_output_directory
    assert Path(actual_args.output_directory).exists()
    assert Path(actual_args.output_directory).is_dir()

    with pytest.raises(FileExistsError):
        actual_args = argparse.Namespace(output_directory="test_tools.py")
        actual_args.output_directory = set_output_directory(actual_args)
