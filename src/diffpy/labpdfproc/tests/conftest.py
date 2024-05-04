import os
from pathlib import Path

import pytest


@pytest.fixture
def user_filesystem(tmp_path):
    directory = Path(tmp_path)
    os.chdir(directory)

    existing_dir = Path(tmp_path).resolve() / "existing_dir"
    existing_dir.mkdir(parents=True, exist_ok=True)

    existing_file = Path(tmp_path).resolve() / "existing_file.py"
    existing_file.touch()

    input_directory = Path(tmp_path).resolve() / "input_directory"
    input_directory.mkdir(parents=True, exist_ok=True)

    with open(os.path.join(input_directory, "good_data.chi"), "w") as f:
        f.write("1 2 \n 3 4 \n 5 6 \n 7 8")
    with open(os.path.join(input_directory, "good_data.xy"), "w") as f:
        f.write("1 2 \n 3 4 \n 5 6 \n 7 8")
    with open(os.path.join(input_directory, "unreadable_file.txt"), "w") as f:
        f.write("This is an unreadable file.")
    with open(os.path.join(input_directory, "binary.pkl"), "wb") as f:
        f.write(b"\x00\x01\x02\x03\x04")

    yield tmp_path
