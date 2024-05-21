import json
import os
import re
from pathlib import Path

import pytest

from diffpy.labpdfproc.labpdfprocapp import get_args
from diffpy.labpdfproc.tools import (
    known_sources,
    load_user_info,
    load_user_metadata,
    set_input_lists,
    set_output_directory,
    set_wavelength,
)

# Use cases can be found here: https://github.com/diffpy/diffpy.labpdfproc/issues/48

# This test covers existing single input file, directory, a file list, and multiple files
# We store absolute path into input_directory and file names into input_file
params_input = [
    (["good_data.chi"], ["good_data.chi"]),  # single good file, same directory
    (["input_dir/good_data.chi"], ["input_dir/good_data.chi"]),  # single good file, input directory
    (  # glob current directory
        ["."],
        ["good_data.chi", "good_data.xy", "good_data.txt", "unreadable_file.txt", "binary.pkl"],
    ),
    (  # glob input directory
        ["./input_dir"],
        [
            "input_dir/good_data.chi",
            "input_dir/good_data.xy",
            "input_dir/good_data.txt",
            "input_dir/unreadable_file.txt",
            "input_dir/binary.pkl",
        ],
    ),
    (  # glob list of input directories
        [".", "./input_dir"],
        [
            "./good_data.chi",
            "./good_data.xy",
            "./good_data.txt",
            "./unreadable_file.txt",
            "./binary.pkl",
            "input_dir/good_data.chi",
            "input_dir/good_data.xy",
            "input_dir/good_data.txt",
            "input_dir/unreadable_file.txt",
            "input_dir/binary.pkl",
        ],
    ),
    (  # file_list_example2.txt list of files provided in different directories with wildcard
        ["input_dir/file_list_example2.txt"],
        ["input_dir/good_data.chi", "good_data.xy", "input_dir/good_data.txt", "input_dir/unreadable_file.txt"],
    ),
    (  # wildcard pattern, matching files with .chi extension in the same directory
        ["./*.chi"],
        ["good_data.chi"],
    ),
    (  # wildcard pattern, matching files with .chi extension in the input directory
        ["input_dir/*.chi"],
        ["input_dir/good_data.chi"],
    ),
    (  # wildcard pattern, matching files starting with good_data
        ["good_data*"],
        ["good_data.chi", "good_data.xy", "good_data.txt"],
    ),
]


@pytest.mark.parametrize("inputs, expected", params_input)
def test_set_input_lists(inputs, expected, user_filesystem):
    base_dir = Path(user_filesystem)
    os.chdir(base_dir)
    expected_paths = [base_dir.resolve() / expected_path for expected_path in expected]

    cli_inputs = ["2.5"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args = set_input_lists(actual_args)
    assert sorted(actual_args.input_paths) == sorted(expected_paths)


# This test covers non-existing single input file or directory, in this case we raise an error with message
params_input_bad = [
    (
        ["non_existing_file.xy"],
        "Cannot find non_existing_file.xy. Please specify valid input file(s) or directories.",
    ),
    (
        ["./input_dir/non_existing_file.xy"],
        "Cannot find ./input_dir/non_existing_file.xy. Please specify valid input file(s) or directories.",
    ),
    (["./non_existing_dir"], "Cannot find ./non_existing_dir. Please specify valid input file(s) or directories."),
    (  # list of files provided (with missing files)
        ["good_data.chi", "good_data.xy", "unreadable_file.txt", "missing_file.txt"],
        "Cannot find missing_file.txt. Please specify valid input file(s) or directories.",
    ),
    (  # file_list.txt list of files provided (with missing files)
        ["input_dir/file_list.txt"],
        "Cannot find missing_file.txt. Please specify valid input file(s) or directories.",
    ),
]


@pytest.mark.parametrize("inputs, msg", params_input_bad)
def test_set_input_files_bad(inputs, msg, user_filesystem):
    base_dir = Path(user_filesystem)
    os.chdir(base_dir)
    cli_inputs = ["2.5"] + inputs
    actual_args = get_args(cli_inputs)
    with pytest.raises(FileNotFoundError, match=msg[0]):
        actual_args = set_input_lists(actual_args)


params1 = [
    ([], ["."]),
    (["--output-directory", "."], ["."]),
    (["--output-directory", "new_dir"], ["new_dir"]),
    (["--output-directory", "input_dir"], ["input_dir"]),
]


@pytest.mark.parametrize("inputs, expected", params1)
def test_set_output_directory(inputs, expected, user_filesystem):
    os.chdir(user_filesystem)
    expected_output_directory = Path(user_filesystem) / expected[0]
    cli_inputs = ["2.5", "data.xy"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args.output_directory = set_output_directory(actual_args)
    assert actual_args.output_directory == expected_output_directory
    assert Path(actual_args.output_directory).exists()
    assert Path(actual_args.output_directory).is_dir()


def test_set_output_directory_bad(user_filesystem):
    os.chdir(user_filesystem)
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


params_user_info = [
    # No config file, check username and email are properly loaded and config file in ~ is created and written
    (
        ["new_username", "new@email.com"],
        ["input_dir", "input_dir/diffpyconfig.json", "diffpyconfig.json", "diffpyconfig.json"],
        ["new_username", "new@email.com", "new_username", "new@email.com"],
    ),
    # Config file in cwd, check username and email are properly loaded and config file is unchanged
    (
        ["", ""],
        ["conf_dir", "conf_dir/diffpyconfig.json", "diffpyconfig.json", "conf_dir/diffpyconfig.json"],
        ["good_username", "good@email.com", "good_username", "good@email.com"],
    ),
    (
        ["new_username", ""],
        ["conf_dir", "conf_dir/diffpyconfig.json", "diffpyconfig.json", "conf_dir/diffpyconfig.json"],
        ["new_username", "good@email.com", "good_username", "good@email.com"],
    ),
    (
        ["", "new@email.com"],
        ["conf_dir", "conf_dir/diffpyconfig.json", "diffpyconfig.json", "conf_dir/diffpyconfig.json"],
        ["good_username", "new@email.com", "good_username", "good@email.com"],
    ),
    (
        ["new_username", "new@email.com"],
        ["conf_dir", "conf_dir/diffpyconfig.json", "diffpyconfig.json", "conf_dir/diffpyconfig.json"],
        ["new_username", "new@email.com", "good_username", "good@email.com"],
    ),
    # Config file in home dir not in cwd, check username and email are properly loaded and config file is unchanged
    (
        ["", ""],
        ["input_dir", "input_dir/diffpyconfig.json", "conf_dir/diffpyconfig.json", "conf_dir/diffpyconfig.json"],
        ["good_username", "good@email.com", "good_username", "good@email.com"],
    ),
    (
        ["new_username", ""],
        ["input_dir", "input_dir/diffpyconfig.json", "conf_dir/diffpyconfig.json", "conf_dir/diffpyconfig.json"],
        ["new_username", "good@email.com", "good_username", "good@email.com"],
    ),
    (
        ["", "new@email.com"],
        ["input_dir", "input_dir/diffpyconfig.json", "conf_dir/diffpyconfig.json", "conf_dir/diffpyconfig.json"],
        ["good_username", "new@email.com", "good_username", "good@email.com"],
    ),
    (
        ["new_username", "new@email.com"],
        ["input_dir", "input_dir/diffpyconfig.json", "conf_dir/diffpyconfig.json", "conf_dir/diffpyconfig.json"],
        ["new_username", "new@email.com", "good_username", "good@email.com"],
    ),
]


@pytest.mark.parametrize("inputs, paths, expected", params_user_info)
def test_load_user_info(monkeypatch, inputs, paths, expected, user_filesystem):
    os.chdir(user_filesystem / paths[0])
    expected_args_username, expected_args_email, expected_conf_username, expected_conf_email = expected
    mock_prompt_user_info = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(mock_prompt_user_info))
    monkeypatch.setattr("diffpy.labpdfproc.user_config.CWD_CONFIG_PATH", user_filesystem / paths[1])
    monkeypatch.setattr("diffpy.labpdfproc.user_config.HOME_CONFIG_PATH", user_filesystem / paths[2])

    cli_inputs = ["2.5", "data.xy"]
    actual_args = get_args(cli_inputs)
    actual_args = load_user_info(actual_args)

    assert actual_args.username == expected_args_username
    assert actual_args.email == expected_args_email
    with open(user_filesystem / paths[3], "r") as f:
        config_data = json.load(f)
        assert config_data == {"username": expected_conf_username, "email": expected_conf_email}


params_user_info_bad = [
    # No valid username/email in config file (or no config file),
    # and user didn't enter username/email the first time they were asked
    (["", ""], "Please rerun the program and provide a username and email."),
    (["", "good@email.com"], "Please rerun the program and provide a username."),
    (["good_username", ""], "Please rerun the program and provide an email."),
    # User entered an invalid email
    (["good_username", "bad_email"], "Please rerun the program and provide a valid email."),
]


@pytest.mark.parametrize("inputs, msg", params_user_info_bad)
def test_load_user_info_bad(monkeypatch, inputs, msg, user_filesystem):
    os.chdir(user_filesystem)
    input_username, input_email = inputs
    mock_prompt_user_info = iter([input_username, input_email])
    monkeypatch.setattr("builtins.input", lambda _: next(mock_prompt_user_info))
    monkeypatch.setattr("diffpy.labpdfproc.user_config.CWD_CONFIG_PATH", Path.cwd() / "diffpyconfig.json")
    monkeypatch.setattr("diffpy.labpdfproc.user_config.HOME_CONFIG_PATH", user_filesystem / "diffpyconfig.json")

    cli_inputs = ["2.5", "data.xy"]
    actual_args = get_args(cli_inputs)
    with pytest.raises(ValueError, match=msg[0]):
        actual_args = load_user_info(actual_args)
