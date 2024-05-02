import argparse
import os
from pathlib import Path

import pytest

from diffpy.labpdfproc.tools import known_sources, set_output_directory, set_wavelength

params1 = [
    ([None], ["."]),
    (["."], ["."]),
    (["new_dir"], ["new_dir"]),
    (["existing_dir"], ["existing_dir"]),
]


@pytest.mark.parametrize("inputs, expected", params1)
def test_set_output_directory(inputs, expected, tmpdir):
    existing_dir = Path(tmpdir) / "existing_dir"
    existing_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(tmpdir)

    expected_output_directory = Path(tmpdir).resolve() / expected[0]
    actual_args = argparse.Namespace(output_directory=inputs[0])
    actual_args.output_directory = set_output_directory(actual_args)
    assert actual_args.output_directory == expected_output_directory
    assert Path(actual_args.output_directory).exists()
    assert Path(actual_args.output_directory).is_dir()


def test_set_output_directory_bad(tmpdir):
    existing_file = Path(tmpdir) / "existing_file.py"
    existing_file.touch()
    os.chdir(tmpdir)

    actual_args = argparse.Namespace(output_directory="existing_file.py")
    with pytest.raises(FileExistsError):
        actual_args.output_directory = set_output_directory(actual_args)
        assert Path(actual_args.output_directory).exists()
        assert not Path(actual_args.output_directory).is_dir()


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
    with pytest.raises(ValueError, match=msg[0]):
        actual_args.wavelength = set_wavelength(actual_args)
