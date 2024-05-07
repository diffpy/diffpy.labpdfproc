import argparse
import os
import re
from pathlib import Path

import pytest

from diffpy.labpdfproc.labpdfprocapp import get_args
from diffpy.labpdfproc.tools import known_sources, load_user_metadata, set_output_directory, set_wavelength

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


params5 = [
    ([], []),
    (
        ["--user-metadata", "facility=NSLS II", "beamline=28ID-2", "favorite color=blue"],
        [["facility", "NSLS II"], ["beamline", "28ID-2"], ["favorite color", "blue"]],
    ),
    (["--user-metadata", "x=y=z"], [["x", "y=z"]]),
]


@pytest.mark.parametrize("inputs, expected", params5)
def test_load_user_metadata(inputs, expected):
    expected_args = get_args(["2.5"])
    for expected_pair in expected:
        setattr(expected_args, expected_pair[0], expected_pair[1])
    delattr(expected_args, "user_metadata")

    cli_inputs = ["2.5"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args = load_user_metadata(actual_args)
    assert actual_args == expected_args


params6 = [
    (
        ["--user-metadata", "facility=", "NSLS II"],
        [
            "Please provide key-value pairs in the format key=value. "
            "For more information, use `labpdfproc --help.`"
        ],
    ),
    (
        ["--user-metadata", "favorite", "color=blue"],
        "Please provide key-value pairs in the format key=value. "
        "For more information, use `labpdfproc --help.`",
    ),
    (
        ["--user-metadata", "beamline", "=", "28ID-2"],
        "Please provide key-value pairs in the format key=value. "
        "For more information, use `labpdfproc --help.`",
    ),
    (
        ["--user-metadata", "facility=NSLS II", "facility=NSLS III"],
        "Please do not specify repeated keys: facility. ",
    ),
    (
        ["--user-metadata", "wavelength=2"],
        "wavelength is a reserved name.  Please rerun using a different key name. ",
    ),
]


@pytest.mark.parametrize("inputs, msg", params6)
def test_load_user_metadata_bad(inputs, msg):
    cli_inputs = ["2.5"] + inputs
    actual_args = get_args(cli_inputs)
    with pytest.raises(ValueError, match=msg[0]):
        actual_args = load_user_metadata(actual_args)
