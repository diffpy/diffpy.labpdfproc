import argparse
import os
import re
from pathlib import Path

import pytest

from diffpy.labpdfproc.tools import known_sources, set_input_directory, set_output_directory, set_wavelength

params1 = [
    ([None], ["."]),
    (["."], ["."]),
    (["new_dir"], ["new_dir"]),
    (["existing_dir"], ["existing_dir"]),
]


@pytest.mark.parametrize("inputs, expected", params1)
def test_set_output_directory(inputs, expected, tmp_path):
    directory = Path(tmp_path)
    os.chdir(directory)

    existing_dir = Path(tmp_path).resolve() / "existing_dir"
    existing_dir.mkdir(parents=True, exist_ok=True)

    expected_output_directory = Path(tmp_path).resolve() / expected[0]
    actual_args = argparse.Namespace(output_directory=inputs[0])
    actual_args.output_directory = set_output_directory(actual_args)
    assert actual_args.output_directory == expected_output_directory
    assert Path(actual_args.output_directory).exists()
    assert Path(actual_args.output_directory).is_dir()


def test_set_output_directory_bad(tmp_path):
    directory = Path(tmp_path)
    os.chdir(directory)

    existing_file = Path(tmp_path).resolve() / "existing_file.py"
    existing_file.touch()

    actual_args = argparse.Namespace(output_directory="existing_file.py")
    with pytest.raises(FileExistsError):
        actual_args.output_directory = set_output_directory(actual_args)
        assert Path(actual_args.output_directory).exists()
        assert not Path(actual_args.output_directory).is_dir()


params2 = [
    ([None], ["."]),
    (["data.xy"], ["."]),
    (["existing_dir/data.xy"], ["existing_dir"]),
]


@pytest.mark.parametrize("inputs, expected", params2)
def test_set_input_directory(inputs, expected, tmp_path):
    directory = Path(tmp_path)
    os.chdir(directory)

    existing_dir = Path(tmp_path).resolve() / "existing_dir"
    existing_dir.mkdir(parents=True, exist_ok=True)

    expected_input_directory = Path(tmp_path).resolve() / expected[0]
    actual_args = argparse.Namespace(input_file=inputs[0])
    actual_args = set_input_directory(actual_args)
    assert actual_args.input_directory == expected_input_directory


params3 = [
    (
        ["new_dir/data.xy"],
        [
            "Path to input file doesn't exist. "
            "Please rerun specifying a valid input file with a valid directory. "
            "Please avoid forward slashes in your path or file name."
        ],
    ),
    (["data.xy/"], ["Please remove the forward slash at the end and rerun specifying a valid file name."]),
]


@pytest.mark.parametrize("inputs, msg", params3)
def test_set_input_directory_bad(inputs, msg, tmp_path):
    directory = Path(tmp_path)
    os.chdir(directory)
    actual_args = argparse.Namespace(input_file=inputs[0])
    with pytest.raises(ValueError, match=re.escape(msg[0])):
        actual_args = set_input_directory(actual_args)


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
        [f"Anode type not recognized. Please rerun specifying an anode_type from {*known_sources, }."],
    ),
    ([0, None], ["No valid wavelength. Please rerun specifying a known anode_type or a positive wavelength."]),
    ([-1, "Mo"], ["No valid wavelength. Please rerun specifying a known anode_type or a positive wavelength."]),
]


@pytest.mark.parametrize("inputs, msg", params3)
def test_set_wavelength_bad(inputs, msg):
    actual_args = argparse.Namespace(wavelength=inputs[0], anode_type=inputs[1])
    with pytest.raises(ValueError, match=re.escape(msg[0])):
        actual_args.wavelength = set_wavelength(actual_args)
