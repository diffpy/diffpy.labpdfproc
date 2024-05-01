import argparse
from pathlib import Path

import pytest

from diffpy.labpdfproc.tools import set_output_directory

params1 = [
    ([None], [Path.cwd().resolve()]),
    (["."], [Path.cwd().resolve()]),
    (["new_dir"], [Path.cwd().resolve() / "new_dir"]),
    (["new_dir.py"], [Path.cwd().resolve() / "new_dir.py"]),
    (["existing_dir"], [Path.cwd().resolve() / "existing_dir"]),
]


@pytest.mark.parametrize("inputs, expected", params1)
def test_set_output_directory(inputs, expected):
    existing_dir = Path().cwd().resolve() / "existing_dir"
    existing_dir.mkdir(parents=True, exist_ok=True)

    expected_output_directory = expected[0]
    actual_args = argparse.Namespace(output_directory=inputs[0])
    actual_args.output_directory = set_output_directory(actual_args)
    assert actual_args.output_directory == expected_output_directory
    assert Path(actual_args.output_directory).exists()
    assert Path(actual_args.output_directory).is_dir()


def test_set_output_directory_bad():
    existing_dir = Path().cwd().resolve() / "existing_dir.py"
    with open(existing_dir, "w"):
        pass

    actual_args = argparse.Namespace(output_directory="existing_dir.py")
    with pytest.raises(FileExistsError):
        actual_args.output_directory = set_output_directory(actual_args)
        assert Path(actual_args.output_directory).exists()
        assert not Path(actual_args.output_directory).is_dir()
