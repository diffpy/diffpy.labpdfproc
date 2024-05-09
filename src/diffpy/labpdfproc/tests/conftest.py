import os
from pathlib import Path

import pytest


@pytest.fixture
def user_filesystem(tmp_path):
    directory = Path(tmp_path)
    os.chdir(directory)

    input_dir = Path(tmp_path).resolve() / "input_dir"
    input_dir.mkdir(parents=True, exist_ok=True)

    chi_data = "dataformat = twotheta\n mode = xray\n # chi_Q chi_I\n 1 2\n 3 4\n 5 6\n 7 8\n"
    xy_data = "1 2\n 3 4\n 5 6\n 7 8"
    unreadable_data = "This is an unreadable file."
    binary_data = b"\x00\x01\x02\x03\x04"

    with open("good_data.chi", "w") as f:
        f.write(chi_data)
    with open("good_data.xy", "w") as f:
        f.write(xy_data)
    with open("good_data.txt", "w") as f:
        f.write(chi_data)
    with open("unreadable_file.txt", "w") as f:
        f.write(unreadable_data)
    with open("binary.pkl", "wb") as f:
        f.write(binary_data)

    with open(os.path.join(input_dir, "good_data.chi"), "w") as f:
        f.write(chi_data)
    with open(os.path.join(input_dir, "good_data.xy"), "w") as f:
        f.write(xy_data)
    with open(os.path.join(input_dir, "good_data.txt"), "w") as f:
        f.write(chi_data)
    with open(os.path.join(input_dir, "unreadable_file.txt"), "w") as f:
        f.write(unreadable_data)
    with open(os.path.join(input_dir, "binary.pkl"), "wb") as f:
        f.write(binary_data)

    file_list_dir = Path(tmp_path).resolve() / "file_list_dir"
    file_list_dir.mkdir(parents=True, exist_ok=True)
    with open(os.path.join(file_list_dir, "file_list.txt"), "w") as f:
        f.write("good_data.chi \n good_data.xy \n good_data.txt")
    with open(os.path.join(file_list_dir, "invalid_file_list.txt"), "w") as f:
        f.write("good_data.chi \n non_existing_file.xy \n non_existing_file.txt")
    with open(os.path.join(file_list_dir, "invalid_format_file_list.txt"), "w") as f:
        f.write("good_data.chi good_data.xy \n non_existing_file.txt")

    yield tmp_path
