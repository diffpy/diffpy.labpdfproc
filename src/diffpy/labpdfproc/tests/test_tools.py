import argparse
import re
from pathlib import Path

import pytest

from diffpy.labpdfproc.tools import known_sources, set_input_files, set_output_directory, set_wavelength
from diffpy.utils.parsers.loaddata import loadData

params1 = [
    ([None], ["."]),
    (["."], ["."]),
    (["new_dir"], ["new_dir"]),
    (["input_dir"], ["input_dir"]),
]


@pytest.mark.parametrize("inputs, expected", params1)
def test_set_output_directory(inputs, expected, user_filesystem):
    tmp_dir = user_filesystem
    expected_output_directory = tmp_dir / expected[0]

    actual_parser = argparse.ArgumentParser()
    actual_parser.add_argument("--output_directory")
    actual_args = actual_parser.parse_args(["--output_directory", inputs[0]])
    actual_args.output_directory = set_output_directory(actual_args)
    assert actual_args.output_directory == expected_output_directory
    assert Path(actual_args.output_directory).exists()
    assert Path(actual_args.output_directory).is_dir()


def test_set_output_directory_bad(user_filesystem):
    actual_parser = argparse.ArgumentParser()
    actual_parser.add_argument("--output_directory")
    actual_args = actual_parser.parse_args(["--output_directory", "good_data.chi"])

    with pytest.raises(FileExistsError):
        actual_args.output_directory = set_output_directory(actual_args)
        assert Path(actual_args.output_directory).exists()
        assert not Path(actual_args.output_directory).is_dir()


params2 = [
    (
        [None],
        [
            ".",
            ["good_data.chi", "good_data.xy", "good_data.txt", "unreadable_file.txt", "binary.pkl", "input_dir"],
        ],
    ),
    (["good_data.chi"], [".", "good_data.chi"]),
    (["input_dir/unreadable_file.txt"], ["input_dir", "input_dir/unreadable_file.txt"]),
    # ([Path.cwd()], [Path.cwd()]),
]


@pytest.mark.parametrize("inputs, expected", params2)
def test_set_input_files(inputs, expected, user_filesystem):
    tmp_dir = user_filesystem
    expected_input_directory = tmp_dir / expected[0]
    expected_input_files = expected[1]

    actual_parser = argparse.ArgumentParser()
    actual_parser.add_argument("--input_file")
    actual_args = actual_parser.parse_args(["--input_file", inputs[0]])
    actual_args = set_input_files(actual_args)
    assert actual_args.input_directory == expected_input_directory
    assert set(actual_args.input_file) == set(expected_input_files)


def test_loadData_with_input_files(user_filesystem):
    xarray_chi, yarray_chi = loadData("good_data.chi", unpack=True)
    xarray_xy, yarray_xy = loadData("good_data.xy", unpack=True)
    xarray_txt, yarray_txt = loadData("good_data.txt", unpack=True)
    with pytest.raises(ValueError):
        xarray_txt, yarray_txt = loadData("unreadable_file.txt", unpack=True)
    with pytest.raises(ValueError):
        xarray_pkl, yarray_pkl = loadData("binary.pkl", unpack=True)


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
