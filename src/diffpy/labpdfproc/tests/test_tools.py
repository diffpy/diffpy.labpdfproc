import argparse
import os
import re
from pathlib import Path

import pytest

from diffpy.labpdfproc.tools import known_sources, load_metadata, set_output_directory, set_wavelength

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


params6 = [
    (
        ["2.5", "zro2_mo.xy", "Mo", "0.71", "output_directory", "tth", "tth", False],
        [
            {
                "mud": 2.5,
                "input_file": "zro2_mo.xy",
                "anode_type": "Mo",
                "wavelength": 0.71,
                "output_directory": "output_directory",
                "xtype": "tth",
                "output_correction": "tth",
                "force_overwrite": False,
            }
        ],
    ),
]


@pytest.mark.parametrize("inputs, expected", params6)
def test_load_metadata(inputs, expected):
    expected_metadata = expected[0]

    actual_parser = argparse.ArgumentParser()
    actual_parser.add_argument("--mud", type=float)
    actual_parser.add_argument("--input_file")
    actual_parser.add_argument("--anode_type")
    actual_parser.add_argument("--wavelength", type=float)
    actual_parser.add_argument("--output_directory")
    actual_parser.add_argument("--xtype")
    actual_parser.add_argument("--output_correction")
    actual_parser.add_argument("--force_overwrite")

    actual_args = actual_parser.parse_args(
        [
            "--mud",
            inputs[0],
            "--input_file",
            inputs[1],
            "--anode_type",
            inputs[2],
            "--wavelength",
            inputs[3],
            "--output_directory",
            inputs[4],
            "--xtype",
            inputs[5],
            "--output_correction",
            inputs[6],
            "--force_overwrite",
            inputs[7],
        ]
    )

    actual_metadata = load_metadata(actual_args)
    assert actual_metadata == expected_metadata
