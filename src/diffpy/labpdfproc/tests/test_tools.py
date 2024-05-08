import re
from pathlib import Path

import pytest

from diffpy.labpdfproc.labpdfprocapp import get_args
from diffpy.labpdfproc.tools import (
    known_sources,
    load_user_metadata,
    set_input_files,
    set_output_directory,
    set_wavelength,
)
from diffpy.utils.parsers.loaddata import loadData

# Use cases can be found here: https://github.com/diffpy/diffpy.labpdfproc/issues/48

# This test covers existing single input file or directory
# We store absolute path into input_directory and file names into input_file
params_input = [
    (["good_data.chi"], [".", "good_data.chi"]),
    (["input_dir/good_data.chi"], ["input_dir", "good_data.chi"]),
    (["./input_dir/good_data.chi"], ["input_dir", "good_data.chi"]),
    (
        ["."],
        [
            ".",
            ["good_data.chi", "good_data.xy", "good_data.txt", "unreadable_file.txt", "binary.pkl"],
        ],
    ),
    (
        ["./input_dir"],
        [
            "input_dir",
            ["good_data.chi", "good_data.xy", "good_data.txt", "unreadable_file.txt", "binary.pkl"],
        ],
    ),
    (
        ["input_dir"],
        [
            "input_dir",
            ["good_data.chi", "good_data.xy", "good_data.txt", "unreadable_file.txt", "binary.pkl"],
        ],
    ),
]


@pytest.mark.parametrize("inputs, expected", params_input)
def test_set_input_files(inputs, expected, user_filesystem):
    expected_input_directory = Path(user_filesystem) / expected[0]
    expected_input_files = expected[1]

    cli_inputs = ["2.5"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args = set_input_files(actual_args)
    assert actual_args.input_directory == expected_input_directory
    assert set(actual_args.input_file) == set(expected_input_files)


# This test covers non-existing single input file or directory, in this case we raise an error with message
params_input_bad = [
    (["non_existing_file.xy"], "Please specify valid input file or directory."),
    (["./input_dir/non_existing_file.xy"], "Please specify valid input file or directory."),
    (["./non_existing_dir"], "Please specify valid input file or directory."),
]


@pytest.mark.parametrize("inputs, msg", params_input_bad)
def test_set_input_files_bad(inputs, msg, user_filesystem):
    cli_inputs = ["2.5"] + inputs
    actual_args = get_args(cli_inputs)
    with pytest.raises(ValueError, match=msg[0]):
        actual_args = set_input_files(actual_args)


# Pass files to loadData and use it to check if file is valid or not
def test_loadData_with_input_files(user_filesystem):
    xarray_chi, yarray_chi = loadData("good_data.chi", unpack=True)
    xarray_xy, yarray_xy = loadData("good_data.xy", unpack=True)
    xarray_txt, yarray_txt = loadData("good_data.txt", unpack=True)
    with pytest.raises(ValueError):
        xarray_txt, yarray_txt = loadData("unreadable_file.txt", unpack=True)
    with pytest.raises(ValueError):
        xarray_pkl, yarray_pkl = loadData("binary.pkl", unpack=True)


params1 = [
    ([], ["."]),
    (["--output-directory", "."], ["."]),
    (["--output-directory", "new_dir"], ["new_dir"]),
    (["--output-directory", "input_dir"], ["input_dir"]),
]


@pytest.mark.parametrize("inputs, expected", params1)
def test_set_output_directory(inputs, expected, user_filesystem):
    expected_output_directory = Path(user_filesystem) / expected[0]
    cli_inputs = ["2.5", "data.xy"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args.output_directory = set_output_directory(actual_args)
    assert actual_args.output_directory == expected_output_directory
    assert Path(actual_args.output_directory).exists()
    assert Path(actual_args.output_directory).is_dir()


def test_set_output_directory_bad(user_filesystem):
    cli_inputs = ["2.5", "data.xy", "--output-directory", "good_data.chi"]
    actual_args = get_args(cli_inputs)
    with pytest.raises(FileExistsError):
        actual_args.output_directory = set_output_directory(actual_args)
        assert Path(actual_args.output_directory).exists()
        assert not Path(actual_args.output_directory).is_dir()


params2 = [
    ([], [0.71]),
    (["--anode-type", "Ag"], [0.59]),
    (["--wavelength", "0.25"], [0.25]),
    (["--wavelength", "0.25", "--anode-type", "Ag"], [0.25]),
]


@pytest.mark.parametrize("inputs, expected", params2)
def test_set_wavelength(inputs, expected):
    expected_wavelength = expected[0]
    cli_inputs = ["2.5", "data.xy"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args.wavelength = set_wavelength(actual_args)
    assert actual_args.wavelength == expected_wavelength


params3 = [
    (
        ["--anode-type", "invalid"],
        [f"Anode type not recognized. Please rerun specifying an anode_type from {*known_sources, }."],
    ),
    (
        ["--wavelength", "0"],
        ["No valid wavelength. Please rerun specifying a known anode_type or a positive wavelength."],
    ),
    (
        ["--wavelength", "-1", "--anode-type", "Mo"],
        ["No valid wavelength. Please rerun specifying a known anode_type or a positive wavelength."],
    ),
]


@pytest.mark.parametrize("inputs, msg", params3)
def test_set_wavelength_bad(inputs, msg):
    cli_inputs = ["2.5", "data.xy"] + inputs
    actual_args = get_args(cli_inputs)
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
    expected_args = get_args(["2.5", "data.xy"])
    for expected_pair in expected:
        setattr(expected_args, expected_pair[0], expected_pair[1])
    delattr(expected_args, "user_metadata")

    cli_inputs = ["2.5", "data.xy"] + inputs
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
    cli_inputs = ["2.5", "data.xy"] + inputs
    actual_args = get_args(cli_inputs)
    with pytest.raises(ValueError, match=msg[0]):
        actual_args = load_user_metadata(actual_args)
