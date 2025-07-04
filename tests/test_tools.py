import json
import os
import re
from pathlib import Path

import pytest

from diffpy.labpdfproc.labpdfprocapp import get_args
from diffpy.labpdfproc.tools import (
    known_sources,
    load_metadata,
    load_package_info,
    load_user_info,
    load_user_metadata,
    load_wavelength_from_config_file,
    preprocessing_args,
    set_input_lists,
    set_mud,
    set_output_directory,
    set_wavelength,
    set_xtype,
)
from diffpy.utils.diffraction_objects import XQUANTITIES


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # Use cases can be found here:
        # https://github.com/diffpy/diffpy.labpdfproc/issues/48.
        # This test covers existing single input file, directory,
        # a file list, and multiple files.
        # We store absolute path into input_directory
        # and file names into input_file.
        (  # C1: single good file in the current directory,
            # expect to return the absolute Path of the file
            ["good_data.chi"],
            ["good_data.chi"],
        ),
        (  # C2: single good file in an input directory,
            # expect to return the absolute Path of the file
            ["input_dir/good_data.chi"],
            ["input_dir/good_data.chi"],
        ),
        (  # C3: glob current directory,
            # expect to return all files in the current directory
            ["."],
            [
                "good_data.chi",
                "good_data.xy",
                "good_data.txt",
                "unreadable_file.txt",
                "binary.pkl",
            ],
        ),
        (  # C4: glob input directory,
            # expect to return all files in that directory
            ["./input_dir"],
            [
                "input_dir/good_data.chi",
                "input_dir/good_data.xy",
                "input_dir/good_data.txt",
                "input_dir/unreadable_file.txt",
                "input_dir/binary.pkl",
            ],
        ),
        (  # C5: glob list of input directories,
            # expect to return all files in the directories
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
        (  # C6: file_list_example2.txt
            # list of files provided in different directories with wildcard,
            # expect to return all files listed on the file_list file
            ["input_dir/file_list_example2.txt"],
            [
                "input_dir/good_data.chi",
                "good_data.xy",
                "input_dir/good_data.txt",
                "input_dir/unreadable_file.txt",
            ],
        ),
        (  # C7: wildcard pattern,
            # expect to match files with .chi extension in the same directory
            ["./*.chi"],
            ["good_data.chi"],
        ),
        (  # C8: wildcard pattern,
            # expect to match files with .chi extension in the input directory
            ["input_dir/*.chi"],
            ["input_dir/good_data.chi"],
        ),
        (  # C9: wildcard pattern,
            # expect to match files starting with good_data
            ["good_data*"],
            ["good_data.chi", "good_data.xy", "good_data.txt"],
        ),
    ],
)
def test_set_input_lists(inputs, expected, user_filesystem):
    base_dir = Path(user_filesystem)
    os.chdir(base_dir)
    expected_paths = [
        base_dir.resolve() / expected_path for expected_path in expected
    ]

    cli_inputs = ["applymud"] + inputs + ["--mud", "2.5"]
    actual_args = get_args(cli_inputs)
    actual_args = set_input_lists(actual_args)
    assert sorted(actual_args.input_paths) == sorted(expected_paths)


@pytest.mark.parametrize(
    "inputs, expected_error_msg",
    [
        # This test covers non-existing single input file or directory,
        # in this case we raise an error with message
        (  # C1: non-existing single file
            ["non_existing_file.xy"],
            "Cannot find non_existing_file.xy. "
            "Please specify valid input file(s) or directories.",
        ),
        (  # C2: non-existing single file with directory
            ["./input_dir/non_existing_file.xy"],
            "Cannot find ./input_dir/non_existing_file.xy. "
            "Please specify valid input file(s) or directories.",
        ),
        (  # C3: non-existing single directory
            ["./non_existing_dir"],
            "Cannot find ./non_existing_dir. "
            "Please specify valid input file(s) or directories.",
        ),
        (  # C4: list of files provided (with missing files)
            [
                "good_data.chi",
                "good_data.xy",
                "unreadable_file.txt",
                "missing_file.txt",
            ],
            "Cannot find missing_file.txt. "
            "Please specify valid input file(s) or directories.",
        ),
        (  # C5: file_list.txt list of files provided (with missing files)
            ["input_dir/file_list.txt"],
            "Cannot find missing_file.txt. "
            "Please specify valid input file(s) or directories.",
        ),
    ],
)
def test_set_input_files_bad(inputs, expected_error_msg, user_filesystem):
    base_dir = Path(user_filesystem)
    os.chdir(base_dir)
    cli_inputs = ["applymud"] + inputs + ["--mud", "2.5"]
    actual_args = get_args(cli_inputs)
    with pytest.raises(FileNotFoundError, match=re.escape(expected_error_msg)):
        actual_args = set_input_lists(actual_args)


@pytest.mark.parametrize(
    "inputs, expected",
    [
        ([], ["."]),
        (["--output-directory", "."], ["."]),
        (["--output-directory", "new_dir"], ["new_dir"]),
        (["--output-directory", "input_dir"], ["input_dir"]),
    ],
)
def test_set_output_directory(inputs, expected, user_filesystem):
    os.chdir(user_filesystem)
    expected_output_directory = Path(user_filesystem) / expected[0]
    cli_inputs = ["applymud", "data.xy", "--mud", "2.5"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args = set_output_directory(actual_args)
    assert actual_args.output_directory == expected_output_directory
    assert Path(actual_args.output_directory).exists()
    assert Path(actual_args.output_directory).is_dir()


def test_set_output_directory_bad(user_filesystem):
    os.chdir(user_filesystem)
    cli_inputs = [
        "applymud",
        "data.xy",
        "--mud",
        "2.5",
        "--output-directory",
        "good_data.chi",
    ]
    actual_args = get_args(cli_inputs)
    with pytest.raises(FileExistsError):
        actual_args = set_output_directory(actual_args)
        assert Path(actual_args.output_directory).exists()
        assert not Path(actual_args.output_directory).is_dir()


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # Test with only a home config file (no local config),
        # expect to return values directly from args
        # if either wavelength or anode type is specified,
        # otherwise update args with values from the home config file
        # (wavelength=0.3, no anode type).
        # This test only checks loading behavior,
        # not value validation (which is handled by `set_wavelength`).
        # C1: no args, expect to update arg values from home config
        ([], {"wavelength": 0.3, "anode_type": None}),
        # C2: wavelength provided, expect to return args unchanged
        (["--wavelength", "0.25"], {"wavelength": 0.25, "anode_type": None}),
        # C3: anode type provided, expect to return args unchanged
        (["--anode-type", "Mo"], {"wavelength": None, "anode_type": "Mo"}),
        # C4: both wavelength and anode type provided,
        # expect to return args unchanged
        (
            ["--wavelength", "0.7", "--anode-type", "Mo"],
            {"wavelength": 0.7, "anode_type": "Mo"},
        ),
    ],
)
def test_load_wavelength_from_config_file_with_home_conf_file(
    mocker, user_filesystem, inputs, expected
):
    cwd = Path(user_filesystem)
    home_dir = cwd / "home_dir"
    mocker.patch("pathlib.Path.home", lambda _: home_dir)
    os.chdir(cwd)

    cli_inputs = ["applymud", "data.xy", "--mud", "2.5"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args = load_wavelength_from_config_file(actual_args)
    assert actual_args.wavelength == expected["wavelength"]
    assert actual_args.anode_type == expected["anode_type"]


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # Test when a local config file exists,
        # expect to return values directly from args
        # if either wavelength or anode type is specified,
        # otherwise update args with values from the local config file
        # (wavelength=0.6, no anode type).
        # Results should be the same whether if the home config exists.
        # This test only checks loading behavior,
        # not value validation (which is handled by `set_wavelength`).
        # C1: no args, expect to update arg values from local config
        ([], {"wavelength": 0.6, "anode_type": None}),
        # C2: wavelength provided, expect to return args unchanged
        (["--wavelength", "0.25"], {"wavelength": 0.25, "anode_type": None}),
        # C3: anode type provided, expect to return args unchanged
        (["--anode-type", "Mo"], {"wavelength": None, "anode_type": "Mo"}),
        # C4: both wavelength and anode type provided,
        # expect to return args unchanged
        (
            ["--wavelength", "0.7", "--anode-type", "Mo"],
            {"wavelength": 0.7, "anode_type": "Mo"},
        ),
    ],
)
def test_load_wavelength_from_config_file_with_local_conf_file(
    mocker, user_filesystem, inputs, expected
):
    cwd = Path(user_filesystem)
    home_dir = cwd / "home_dir"
    mocker.patch("pathlib.Path.home", lambda _: home_dir)
    os.chdir(cwd)
    local_config_data = {"wavelength": 0.6}
    with open(cwd / "diffpyconfig.json", "w") as f:
        json.dump(local_config_data, f)

    cli_inputs = ["applymud", "data.xy", "--mud", "2.5"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args = load_wavelength_from_config_file(actual_args)
    assert actual_args.wavelength == expected["wavelength"]
    assert actual_args.anode_type == expected["anode_type"]

    # remove home config file, expect the same results
    confile = home_dir / "diffpyconfig.json"
    os.remove(confile)
    assert actual_args.wavelength == expected["wavelength"]
    assert actual_args.anode_type == expected["anode_type"]


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # Test when no config files exist,
        # expect to return args without modification.
        # This test only checks loading behavior,
        # not value validation (which is handled by `set_wavelength`).
        # C1: no args
        ([], {"wavelength": None, "anode_type": None}),
        # C1: wavelength provided
        (["--wavelength", "0.25"], {"wavelength": 0.25, "anode_type": None}),
        # C2: anode type provided
        (["--anode-type", "Mo"], {"wavelength": None, "anode_type": "Mo"}),
        # C4: both wavelength and anode type provided
        (
            ["--wavelength", "0.7", "--anode-type", "Mo"],
            {"wavelength": 0.7, "anode_type": "Mo"},
        ),
    ],
)
def test_load_wavelength_from_config_file_without_conf_files(
    mocker, user_filesystem, inputs, expected
):
    cwd = Path(user_filesystem)
    home_dir = cwd / "home_dir"
    mocker.patch("pathlib.Path.home", lambda _: home_dir)
    os.chdir(cwd)
    confile = home_dir / "diffpyconfig.json"
    os.remove(confile)

    cli_inputs = ["applymud", "data.xy", "--mud", "2.5"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args = load_wavelength_from_config_file(actual_args)
    assert actual_args.wavelength == expected["wavelength"]
    assert actual_args.anode_type == expected["anode_type"]


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # C1: only a valid anode type was entered (case independent),
        # expect to match the corresponding wavelength
        # and preserve the correct case anode type
        (["--anode-type", "Mo"], {"wavelength": 0.71073, "anode_type": "Mo"}),
        (
            ["--anode-type", "MoKa1"],
            {"wavelength": 0.70930, "anode_type": "MoKa1"},
        ),
        (
            ["--anode-type", "MoKa1Ka2"],
            {"wavelength": 0.71073, "anode_type": "MoKa1Ka2"},
        ),
        (["--anode-type", "Ag"], {"wavelength": 0.56087, "anode_type": "Ag"}),
        (
            ["--anode-type", "AgKa1"],
            {"wavelength": 0.55941, "anode_type": "AgKa1"},
        ),
        (
            ["--anode-type", "AgKa1Ka2"],
            {"wavelength": 0.56087, "anode_type": "AgKa1Ka2"},
        ),
        (["--anode-type", "Cu"], {"wavelength": 1.54184, "anode_type": "Cu"}),
        (
            ["--anode-type", "CuKa1"],
            {"wavelength": 1.54056, "anode_type": "CuKa1"},
        ),
        (
            ["--anode-type", "CuKa1Ka2"],
            {"wavelength": 1.54184, "anode_type": "CuKa1Ka2"},
        ),
        (
            ["--anode-type", "moKa1Ka2"],
            {"wavelength": 0.71073, "anode_type": "MoKa1Ka2"},
        ),
        (["--anode-type", "ag"], {"wavelength": 0.56087, "anode_type": "Ag"}),
        (
            ["--anode-type", "cuka1"],
            {"wavelength": 1.54056, "anode_type": "CuKa1"},
        ),
        # C2: a valid wavelength was entered,
        # expect to include the wavelength only and anode type is None
        (["--wavelength", "0.25"], {"wavelength": 0.25, "anode_type": None}),
        # C3: nothing passed in, but mu*D was provided and xtype is on tth
        # expect wavelength and anode type to be None
        # and program proceeds without error
        ([], {"wavelength": None, "anode_type": None}),
    ],
)
def test_set_wavelength(inputs, expected):
    cli_inputs = ["applymud", "data.xy", "--mud", "2.5"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args = set_wavelength(actual_args)
    assert actual_args.wavelength == expected["wavelength"]
    assert actual_args.anode_type == expected["anode_type"]


@pytest.mark.parametrize(
    "inputs, expected_error_msg",
    [
        (  # C1: nothing passed in, xtype is not on tth
            # expect error asking for either wavelength or anode type
            ["--xtype", "q"],
            f"Please provide a wavelength or anode type "
            f"because the independent variable axis is not on two-theta. "
            f"Allowed anode types are {*known_sources, }.",
        ),
        (  # C2: both wavelength and anode type were specified
            # expect error asking not to specify both
            ["--wavelength", "0.7", "--anode-type", "Mo"],
            f"Please provide either a wavelength or an anode type, not both. "
            f"Allowed anode types are {*known_sources, }.",
        ),
        (  # C3: invalid anode type
            # expect error asking to specify a valid anode type
            ["--anode-type", "invalid"],
            f"Anode type 'invalid' not recognized. "
            f"Please rerun specifying an anode_type from {*known_sources, }.",
        ),
        (  # C4: invalid wavelength
            # expect error asking to specify a valid wavelength or anode type
            ["--wavelength", "-0.2"],
            "Wavelength = -0.2 is not valid. "
            "Please rerun specifying a known anode_type "
            "or a positive wavelength.",
        ),
    ],
)
def test_set_wavelength_bad(inputs, expected_error_msg):
    cli_inputs = ["applymud", "data.xy", "--mud", "2.5"] + inputs
    actual_args = get_args(cli_inputs)
    with pytest.raises(ValueError, match=re.escape(expected_error_msg)):
        actual_args = set_wavelength(actual_args)


@pytest.mark.parametrize(
    "inputs, expected_xtype",
    [
        ([], "tth"),
        (["--xtype", "2theta"], "tth"),
        (["--xtype", "d"], "d"),
        (["--xtype", "q"], "q"),
    ],
)
def test_set_xtype(inputs, expected_xtype):
    cli_inputs = ["applymud", "data.xy", "--mud", "2.5"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args = set_xtype(actual_args)
    assert actual_args.xtype == expected_xtype


def test_set_xtype_bad():
    cli_inputs = ["applymud", "data.xy", "--mud", "2.5", "--xtype", "invalid"]
    actual_args = get_args(cli_inputs)
    with pytest.raises(
        ValueError,
        match=re.escape(
            f"Unknown xtype: invalid. Allowed xtypes are {*XQUANTITIES, }."
        ),
    ):
        actual_args = set_xtype(actual_args)


@pytest.mark.parametrize(
    "inputs, expected_mud",
    [
        # C1: user enters muD manually, expect to return the same value
        (["--mud", "2.5"], 2.5),
        # C2: user provides a z-scan file, expect to estimate through the file
        (["--z-scan-file", "test_dir/testfile.xy"], 3),
        # C3: user specifies sample composition, energy,
        # and sample mass density,
        # both with and without whitespaces, expect to estimate theoretically
        (["--theoretical-from-density", "ZrO2,17.45,1.2"], 1.49),
        (["--theoretical-from-density", "ZrO2, 17.45, 1.2"], 1.49),
        # C4: user specifies sample composition, energy, and packing fraction
        # both with and without whitespaces, expect to estimate theoretically
        # (["--theoretical-from-packing", "ZrO2,17.45,0.3"], 1.49),
        # (["--theoretical-from-packing", "ZrO2, 17.45, 0.3"], 1.49),
    ],
)
def test_set_mud(user_filesystem, inputs, expected_mud):
    cwd = Path(user_filesystem)
    os.chdir(cwd)
    cli_inputs = ["applymud", "data.xy"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args = set_mud(actual_args)
    assert actual_args.mud == pytest.approx(expected_mud, rel=1e-4, abs=0.1)


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # C1: user provides an invalid z-scan file,
        # expect FileNotFoundError and message to specify a valid file path
        (
            ["--z-scan-file", "invalid file"],
            [
                FileNotFoundError,
                "Cannot find invalid file. Please specify a valid file path.",
            ],
        ),
        # C2.1: (sample mass density option)
        # user provides fewer than three input values
        # expect ValueError with a message indicating the correct format
        (
            ["--theoretical-from-density", "ZrO2,0.5"],
            [
                ValueError,
                "Invalid mu*D input 'ZrO2,0.5'. "
                "Expected format is 'sample composition, energy, "
                "sample mass density or packing fraction' "
                "(e.g., 'ZrO2,17.45,0.5').",
            ],
        ),
        # C2.2: (packing fraction option)
        # user provides fewer than three input values
        # expect ValueError with a message indicating the correct format
        (
            ["--theoretical-from-packing", "ZrO2,0.5"],
            [
                ValueError,
                "Invalid mu*D input 'ZrO2,0.5'. "
                "Expected format is 'sample composition, energy, "
                "sample mass density or packing fraction' "
                "(e.g., 'ZrO2,17.45,0.5').",
            ],
        ),
        # C3.1: (sample mass density option)
        # user provides more than 3 input values
        # expect ValueError with a message indicating the correct format
        (
            ["--theoretical-from-density", "ZrO2,17.45,1.5,0.5"],
            [
                ValueError,
                "Invalid mu*D input 'ZrO2,17.45,1.5,0.5'. "
                "Expected format is 'sample composition, energy, "
                "sample mass density or packing fraction' "
                "(e.g., 'ZrO2,17.45,0.5').",
            ],
        ),
        # C3.2: (packing fraction option)
        # user provides more than 3 input values
        # expect ValueError with a message indicating the correct format
        (
            ["--theoretical-from-packing", "ZrO2,17.45,1.5,0.5"],
            [
                ValueError,
                "Invalid mu*D input 'ZrO2,17.45,1.5,0.5'. "
                "Expected format is 'sample composition, energy, "
                "sample mass density or packing fraction' "
                "(e.g., 'ZrO2,17.45,0.5').",
            ],
        ),
    ],
)
def test_set_mud_bad(user_filesystem, inputs, expected):
    expected_error, expected_error_msg = expected
    cwd = Path(user_filesystem)
    os.chdir(cwd)
    cli_inputs = ["applymud", "data.xy"] + inputs
    actual_args = get_args(cli_inputs)
    with pytest.raises(expected_error, match=re.escape(expected_error_msg)):
        actual_args = set_mud(actual_args)


@pytest.mark.parametrize(
    "inputs, expected",
    [
        ([], []),
        (
            [
                "--user-metadata",
                "facility=NSLS II",
                "beamline=28ID-2",
                "favorite color=blue",
            ],
            [
                ["facility", "NSLS II"],
                ["beamline", "28ID-2"],
                ["favorite color", "blue"],
            ],
        ),
        (["--user-metadata", "x=y=z"], [["x", "y=z"]]),
    ],
)
def test_load_user_metadata(inputs, expected):
    expected_args = get_args(["applymud", "data.xy", "--mud", "2.5"])
    for expected_pair in expected:
        setattr(expected_args, expected_pair[0], expected_pair[1])
    delattr(expected_args, "user_metadata")

    cli_inputs = ["applymud", "data.xy", "--mud", "2.5"] + inputs
    actual_args = get_args(cli_inputs)
    actual_args = load_user_metadata(actual_args)
    assert actual_args == expected_args


@pytest.mark.parametrize(
    "inputs, expected_error_msg",
    [
        (
            ["--user-metadata", "facility=", "NSLS II"],
            "Please provide key-value pairs in the format key=value. "
            "For more information, use `labpdfproc --help.`",
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
            "Please do not specify repeated keys: facility.",
        ),
        (
            ["--user-metadata", "wavelength=2"],
            "wavelength is a reserved name. "
            "Please rerun using a different key name.",
        ),
    ],
)
def test_load_user_metadata_bad(inputs, expected_error_msg):
    cli_inputs = ["applymud", "data.xy", "--mud", "2.5"] + inputs
    actual_args = get_args(cli_inputs)
    with pytest.raises(ValueError, match=re.escape(expected_error_msg)):
        actual_args = load_user_metadata(actual_args)


@pytest.mark.parametrize(
    "inputs, expected",
    [  # Test that when cli inputs are present, they override home config,
        # otherwise we take home config
        (
            {"username": None, "email": None, "orcid": None},
            {
                "username": "home_username",
                "email": "home@email.com",
                "orcid": "home_orcid",
            },
        ),
        (
            {"username": "cli_username", "email": None, "orcid": None},
            {
                "username": "cli_username",
                "email": "home@email.com",
                "orcid": "home_orcid",
            },
        ),
        (
            {"username": None, "email": "cli@email.com", "orcid": None},
            {
                "username": "home_username",
                "email": "cli@email.com",
                "orcid": "home_orcid",
            },
        ),
        (
            {"username": None, "email": None, "orcid": "cli_orcid"},
            {
                "username": "home_username",
                "email": "home@email.com",
                "orcid": "cli_orcid",
            },
        ),
        (
            {
                "username": "cli_username",
                "email": "cli@email.com",
                "orcid": "cli_orcid",
            },
            {
                "username": "cli_username",
                "email": "cli@email.com",
                "orcid": "cli_orcid",
            },
        ),
    ],
)
def test_load_user_info(monkeypatch, inputs, expected, user_filesystem):
    cwd = Path(user_filesystem)
    home_dir = cwd / "home_dir"
    monkeypatch.setattr("pathlib.Path.home", lambda _: home_dir)
    os.chdir(cwd)

    cli_inputs = [
        "applymud",
        "data.xy",
        "--mud",
        "2.5",
        "--username",
        inputs["username"],
        "--email",
        inputs["email"],
        "--orcid",
        inputs["orcid"],
    ]
    actual_args = get_args(cli_inputs)
    actual_args = load_user_info(actual_args)
    assert actual_args.username == expected["username"]
    assert actual_args.email == expected["email"]
    assert actual_args.orcid == expected["orcid"]


def test_load_package_info(mocker):
    mocker.patch(
        "importlib.metadata.version",
        side_effect=lambda package_name: (
            "3.3.0" if package_name == "diffpy.utils" else "1.2.3"
        ),
    )
    cli_inputs = ["applymud", "data.xy", "--mud", "2.5"]
    actual_args = get_args(cli_inputs)
    actual_args = load_package_info(actual_args)
    assert actual_args.package_info == {
        "diffpy.labpdfproc": "1.2.3",
        "diffpy.utils": "3.3.0",
    }


def test_load_metadata(mocker, user_filesystem):
    # Test if the function loads args
    # (which will be loaded into the header file).
    # Expect to include mu*D, anode type, xtype, cve method,
    # user-specified metadata, user info, package info, z-scan file,
    # and full paths for current input and output directories.
    cwd = Path(user_filesystem)
    home_dir = cwd / "home_dir"
    mocker.patch("pathlib.Path.home", lambda _: home_dir)
    os.chdir(cwd)
    mocker.patch(
        "importlib.metadata.version",
        side_effect=lambda package_name: (
            "3.3.0" if package_name == "diffpy.utils" else "1.2.3"
        ),
    )
    cli_inputs = [
        "applymud",
        ".",
        "--mud",
        "2.5",
        "--anode-type",
        "Mo",
        "--user-metadata",
        "key=value",
        "--username",
        "cli_username",
        "--email",
        "cli@email.com",
        "--orcid",
        "cli_orcid",
    ]
    actual_args = get_args(cli_inputs)
    actual_args = preprocessing_args(actual_args)
    for filepath in actual_args.input_paths:
        actual_metadata = load_metadata(actual_args, filepath)
        expected_metadata = {
            "mud": 2.5,
            "input_directory": str(filepath),
            "anode_type": "Mo",
            "output_directory": str(Path.cwd().resolve()),
            "xtype": "tth",
            "method": "polynomial_interpolation",
            "key": "value",
            "username": "cli_username",
            "email": "cli@email.com",
            "orcid": "cli_orcid",
            "package_info": {
                "diffpy.labpdfproc": "1.2.3",
                "diffpy.utils": "3.3.0",
            },
            "z_scan_file": None,
        }
        assert actual_metadata == expected_metadata
