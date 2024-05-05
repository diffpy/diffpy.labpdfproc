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
    txt_data = "dataformat = twotheta\n mode = xray\n # chi_Q chi_I\n 1 2\n 3 4\n 5 6\n 7 8\n"
    unreadable_data = "This is an unreadable file."
    binary_data = b"\x00\x01\x02\x03\x04"

    with open("good_data.chi", "w") as f:
        f.write(chi_data)
    with open("good_data.xy", "w") as f:
        f.write(xy_data)
    with open("good_data.txt", "w") as f:
        f.write(txt_data)
    with open("unreadable_file.txt", "w") as f:
        f.write(unreadable_data)
    with open("binary.pkl", "wb") as f:
        f.write(binary_data)

    with open(os.path.join(input_dir, "good_data.chi"), "w") as f:
        f.write(chi_data)
    with open(os.path.join(input_dir, "good_data.xy"), "w") as f:
        f.write(xy_data)
    with open(os.path.join(input_dir, "good_data.txt"), "w") as f:
        f.write(txt_data)
    with open(os.path.join(input_dir, "unreadable_file.txt"), "w") as f:
        f.write(unreadable_data)
    with open(os.path.join(input_dir, "binary.pkl"), "wb") as f:
        f.write(binary_data)

    yield tmp_path
