import json
import os
import re
from pathlib import Path

import pytest

from diffpy.labpdfproc.labpdfprocapp import get_args_cli
from diffpy.labpdfproc.tools import (
    known_sources,
    load_metadata,
    load_package_info,
    load_user_info,
    load_user_metadata,
    load_wavelength_from_config_file,
    normalize_wavelength,
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

    cli_inputs = ["mud"] + inputs + ["2.5"]
    actual_args = get_args_cli(cli_inputs)
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
    cli_inputs = ["mud"] + inputs + ["2.5"]
    actual_args = get_args_cli(cli_inputs)
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
    cli_inputs = ["mud", "data.xy", "2.5"] + inputs
    actual_args = get_args_cli(cli_inputs)
    actual_args = set_output_directory(actual_args)
    assert actual_args.output_directory == expected_output_directory
    assert Path(actual_args.output_directory).exists()
    assert Path(actual_args.output_directory).is_dir()


def test_set_output_directory_bad(user_filesystem):
    os.chdir(user_filesystem)
    cli_inputs = [
        "mud",
        "data.xy",
        "2.5",
        "--output-directory",
        "good_data.chi",
    ]
    actual_args = get_args_cli(cli_inputs)
    with pytest.raises(FileExistsError):
        actual_args = set_output_directory(actual_args)
        assert Path(actual_args.output_directory).exists()
        assert not Path(actual_args.output_directory).is_dir()


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # UC1: input is numeric wavelength
        # expect to return the same value
        (["--wavelength", "0.25"], 0.25),
        # UC2: input is valid source name (case-sensitive canonical)
        # expect to return the corresponding wavelength from dict
        (["--wavelength", "Mo"], 0.71073),
        # UC3: input is valid source name, mismatched case
        # expect to return the corresponding wavelength from dict
        (["--wavelength", "agka1Ka2"], 0.56087),
    ],
)
def test_normalize_wavelength(inputs, expected):
    cli_inputs = ["mud", "data.xy", "2.5"] + inputs
    args = get_args_cli(cli_inputs)
    args = normalize_wavelength(args)
    assert args.wavelength == expected


def test_normalize_wavelength_bad():
    cli_inputs = ["mud", "data.xy", "2.5", "--wavelength", "invalid_source"]
    args = get_args_cli(cli_inputs)
    with pytest.raises(
        ValueError,
        match=(
            "Anode type 'invalid_source' not recognized\\. "
            "Please rerun specifying an anode type from "
        ),
    ):
        normalize_wavelength(args)


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # Test with only a home config file (no local config),
        # expect to return values directly from args
        # if wavelength is specified,
        # otherwise update args with values from the home config file
        # (wavelength=0.3).
        # This test only checks loading behavior,
        # not value validation (which is handled by `set_wavelength`).
        # C1: no args, expect to update arg values from home config
        ([], {"wavelength": 0.3}),
        # C2: wavelength provided, expect to return args unchanged
        (["--wavelength", "0.25"], {"wavelength": 0.25}),
        # C3: anode type provided, expect to return args unchanged
        (["--wavelength", "Mo"], {"wavelength": 0.71073}),
    ],
)
def test_load_wavelength_from_config_file_with_home_conf_file(
    mocker, user_filesystem, inputs, expected
):
    cwd = Path(user_filesystem)
    home_dir = cwd / "home_dir"
    mocker.patch("pathlib.Path.home", lambda _: home_dir)
    os.chdir(cwd)

    cli_inputs = ["mud", "data.xy", "2.5"] + inputs
    actual_args = get_args_cli(cli_inputs)
    actual_args = load_wavelength_from_config_file(actual_args)
    assert actual_args.wavelength == expected["wavelength"]


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
        ([], {"wavelength": 0.6}),
        # C2: wavelength provided, expect to return args unchanged
        (["--wavelength", "0.25"], {"wavelength": 0.25}),
        # C3: anode type provided, expect to return args unchanged
        (["--wavelength", "Mo"], {"wavelength": 0.71073}),
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

    cli_inputs = ["mud", "data.xy", "2.5"] + inputs
    actual_args = get_args_cli(cli_inputs)
    actual_args = load_wavelength_from_config_file(actual_args)
    assert actual_args.wavelength == expected["wavelength"]

    # remove home config file, expect the same results
    confile = home_dir / "diffpyconfig.json"
    os.remove(confile)
    assert actual_args.wavelength == expected["wavelength"]


@pytest.mark.parametrize(
    "local_config, home_config",
    [
        # C1: no config files exist
        # expected: raise ValueError
        (None, None),
        # C2: local config is empty, no home config
        # expected: raise ValueError
        ({}, None),
        # C3: no local config, home config is empty
        # expected: raise ValueError
        (None, {}),
        # C4: both config files are empty
        # expected: raise ValueError
        ({}, {}),
    ],
)
def test_load_wavelength_from_config_file_without_conf_files_bad(
    mocker,
    user_filesystem,
    local_config,
    home_config,
):
    # User tries to correct data without specifying wavelength and
    # no config files
    # with wavelength exist -- expected to raise ValueError
    cwd = Path(user_filesystem)
    home_dir = cwd / "home_dir"
    mocker.patch("pathlib.Path.home", return_value=home_dir)
    os.chdir(cwd)

    local_config_file = cwd / "diffpyconfig.json"
    if local_config_file.exists():
        local_config_file.unlink()
    home_config_file = home_dir / "diffpyconfig.json"
    if home_config_file.exists():
        home_config_file.unlink()

    if local_config is not None:
        with open(local_config_file, "w") as f:
            json.dump(local_config, f)
    if home_config is not None:
        with open(home_config_file, "w") as f:
            json.dump(home_config, f)

    cli_inputs = ["mud", "data.xy", "2.5"]
    actual_args = get_args_cli(cli_inputs)

    msg = re.escape(
        "\nThe wavelength was not specified and no "
        "configuration file 'diffpyconfig.json' containing "
        "the wavelength or X-ray source was found in either the "
        "local or home directories. Either specify the wavelength "
        "or source using the -w/--wavelength option or "
        "create a configuration file.\n\n"
        "You can add the wavelength or anode type to a "
        "configuration file on this computer. Once created, it "
        "will be automatically used for subsequent diffpy data "
        "by default, and you will only need to do this once.\n\n"
        "For detailed instructions on creating the configuration "
        "file, please refer to:\n"
        "https://www.diffpy.org/diffpy.labpdfproc/examples/"
        "toolsexample.html"
    )
    with pytest.raises(ValueError, match=msg):
        load_wavelength_from_config_file(actual_args)


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # Test when no config files exist,
        # expect to return args without modification.
        # This test only checks loading behavior,
        # not value validation (which is handled by `set_wavelength`).
        # C1: wavelength provided
        (["--wavelength", "0.25"], {"wavelength": 0.25}),
        # C2: anode type provided
        (["--wavelength", "Mo"], {"wavelength": 0.71073}),
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

    cli_inputs = ["mud", "data.xy", "2.5"] + inputs
    actual_args = get_args_cli(cli_inputs)
    actual_args = load_wavelength_from_config_file(actual_args)
    assert actual_args.wavelength == expected["wavelength"]


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # C1: only a valid anode type was entered (case independent),
        # expect to match the corresponding wavelength
        (["--wavelength", "Mo"], {"wavelength": 0.71073}),
        (
            ["--wavelength", "MoKa1"],
            {"wavelength": 0.70930},
        ),
        (
            ["--wavelength", "MoKa1Ka2"],
            {"wavelength": 0.71073},
        ),
        (["--wavelength", "Ag"], {"wavelength": 0.56087}),
        (
            ["--wavelength", "AgKa1"],
            {"wavelength": 0.55941},
        ),
        (
            ["--wavelength", "AgKa1Ka2"],
            {"wavelength": 0.56087},
        ),
        (["--wavelength", "Cu"], {"wavelength": 1.54184}),
        (
            ["--wavelength", "CuKa1"],
            {"wavelength": 1.54056},
        ),
        (
            ["--wavelength", "CuKa1Ka2"],
            {"wavelength": 1.54184},
        ),
        (
            ["--wavelength", "moKa1Ka2"],
            {"wavelength": 0.71073},
        ),
        (["--wavelength", "ag"], {"wavelength": 0.56087}),
        (
            ["--wavelength", "cuka1"],
            {"wavelength": 1.54056},
        ),
        # C2: a valid wavelength was entered,
        (["--wavelength", "0.25"], {"wavelength": 0.25}),
        # C3: nothing passed in, but mu*D was provided and xtype is on tth
        # expect wavelength to be None
        # and program proceeds without error
        ([], {"wavelength": None}),
    ],
)
def test_set_wavelength(inputs, expected):
    cli_inputs = ["mud", "data.xy", "2.5"] + inputs
    actual_args = get_args_cli(cli_inputs)
    actual_args = set_wavelength(actual_args)
    assert actual_args.wavelength == expected["wavelength"]


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
        (  # C2: invalid anode type
            # expect error asking to specify a valid anode type
            ["--wavelength", "invalid"],
            f"Anode type 'invalid' not recognized. "
            f"Please rerun specifying an anode type from {*known_sources, }.",
        ),
        (  # C3: invalid wavelength
            # expect error asking to specify a valid wavelength or anode type
            ["--wavelength", "-0.2"],
            "Wavelength = -0.2 is not valid. "
            "Please rerun specifying a known anode type "
            "or a positive wavelength.",
        ),
    ],
)
def test_set_wavelength_bad(inputs, expected_error_msg):
    cli_inputs = ["mud", "data.xy", "2.5"] + inputs
    actual_args = get_args_cli(cli_inputs)
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
    cli_inputs = ["mud", "data.xy", "2.5"] + inputs
    actual_args = get_args_cli(cli_inputs)
    actual_args = set_xtype(actual_args)
    assert actual_args.xtype == expected_xtype


def test_set_xtype_bad():
    cli_inputs = ["mud", "data.xy", "2.5", "--xtype", "invalid"]
    actual_args = get_args_cli(cli_inputs)
    with pytest.raises(
        ValueError,
        match=re.escape(
            f"Unknown xtype: invalid. Allowed xtypes are {*XQUANTITIES, }."
        ),
    ):
        actual_args = set_xtype(actual_args)


def test_set_mud_from_mud(user_filesystem):
    cwd = Path(user_filesystem)
    os.chdir(cwd)
    cli_inputs = ["mud", "data.xy", "2.5"]
    actual_args = get_args_cli(cli_inputs)
    actual_args = set_mud(actual_args)
    expected_mud = 2.5
    assert actual_args.mud == expected_mud


def test_set_mud_from_zscan(user_filesystem):
    cwd = Path(user_filesystem)
    os.chdir(cwd)
    cli_inputs = ["zscan", "data.xy", "test_dir/testfile.xy"]
    actual_args = get_args_cli(cli_inputs)
    actual_args = set_mud(actual_args)
    expected_mud = 3.0
    assert actual_args.mud == pytest.approx(expected_mud, rel=1e-4, abs=0.1)


@pytest.mark.parametrize(
    "inputs,expected_mud",
    # C1: user specifies a wavelength
    # and the wavelength is used to compute mu*D
    [
        (["--wavelength", ".71"], 4.32),
        # C2: user specifies an anode type
        # and the corresponding wavelength is used
        # to compute mu*D
        (["--wavelength", "Mo"], 4.32),
        # C3: user does not specify wavelength or anode type
        # and the wavelength is retrieved from a config file
        ([], 4.32),
    ],
)
def test_set_mud_from_sample(mocker, user_filesystem, inputs, expected_mud):
    cwd = Path(user_filesystem)
    home_dir = cwd / "home_dir"
    mocker.patch("pathlib.Path.home", lambda _: home_dir)
    os.chdir(cwd)
    local_config_data = {"wavelength": 0.71}
    with open(cwd / "diffpyconfig.json", "w") as f:
        json.dump(local_config_data, f)
    # [command,datafile,sample_composition,sample_mass_density,diameter]
    cli_inputs = ["sample", "data.xy", "ZrO2", "1.745", "2"] + inputs
    actual_args = get_args_cli(cli_inputs)
    actual_args = set_mud(actual_args)
    assert actual_args.mud == pytest.approx(expected_mud, rel=1e-4, abs=0.1)


@pytest.mark.parametrize(
    "inputs, expected",
    [
        # C1: user provides an invalid z-scan file,
        # expect FileNotFoundError and message to specify a valid file path
        (
            ["invalid file"],
            [
                FileNotFoundError,
                "Cannot find invalid file. Please specify a valid file path.",
            ],
        ),
    ],
)
def test_set_mud_bad(user_filesystem, inputs, expected):
    expected_error, expected_error_msg = expected
    cwd = Path(user_filesystem)
    os.chdir(cwd)
    cli_inputs = ["zscan", "data.xy"] + inputs
    actual_args = get_args_cli(cli_inputs)
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
    expected_args = get_args_cli(["mud", "data.xy", "2.5"])
    for expected_pair in expected:
        setattr(expected_args, expected_pair[0], expected_pair[1])
    delattr(expected_args, "user_metadata")

    cli_inputs = ["mud", "data.xy", "2.5"] + inputs
    actual_args = get_args_cli(cli_inputs)
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
    cli_inputs = ["mud", "data.xy", "2.5"] + inputs
    actual_args = get_args_cli(cli_inputs)
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
        "mud",
        "data.xy",
        "2.5",
        "--username",
        inputs["username"],
        "--email",
        inputs["email"],
        "--orcid",
        inputs["orcid"],
    ]
    actual_args = get_args_cli(cli_inputs)
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
    cli_inputs = ["mud", "data.xy", "2.5"]
    actual_args = get_args_cli(cli_inputs)
    actual_args = load_package_info(actual_args)
    assert actual_args.package_info == {
        "diffpy.labpdfproc": "1.2.3",
        "diffpy.utils": "3.3.0",
    }


@pytest.mark.parametrize(
    "inputs,expected",
    # C1: user corrects data using `mud` command
    # expect to include mud value and method
    [
        (
            ["mud", ".", "2.5"],
            {
                "mud": 2.5,
                "command": "mud",
            },
        ),
        # C2: user corrects data using `zscan` command
        # expect to include z-scan file and method
        (
            ["zscan", ".", "test_dir/testfile.xy"],
            {
                "z_scan_file": "test_dir/testfile.xy",
                "command": "zscan",
                "mud": 3.0,
            },
        ),
        # C3: user corrects data using `sample` command
        # expected to include sample composition,
        # mass density, diameter, and method
        (
            ["sample", ".", "ZrO2", "1.745", "2"],
            {
                "sample_composition": "ZrO2",
                "sample_mass_density": 1.745,
                "diameter": 2.0,
                "command": "sample",
                "mud": 4.3321,
            },
        ),
    ],
)
def test_load_metadata(mocker, user_filesystem, inputs, expected):
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
    cli_inputs = inputs + [
        "--wavelength",
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
    actual_args = get_args_cli(cli_inputs)
    actual_args = preprocessing_args(actual_args)
    for filepath in actual_args.input_paths:
        if "z_scan_file" in expected:
            # adjust path to be relative to cwd
            expected["z_scan_file"] = str(
                (cwd / expected["z_scan_file"]).resolve()
            )
        actual_metadata = load_metadata(actual_args, filepath)
        expected_metadata = {
            "input_directory": str(filepath),
            "wavelength": 0.71073,
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
            **expected,
        }
        assert actual_metadata == expected_metadata
