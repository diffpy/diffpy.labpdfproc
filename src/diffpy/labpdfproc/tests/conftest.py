from pathlib import Path

import pytest


@pytest.fixture
def user_filesystem(tmp_path):
    base_dir = Path(tmp_path)
    input_dir = base_dir / "input_dir"
    input_dir.mkdir(parents=True, exist_ok=True)

    chi_data = "dataformat = twotheta\n mode = xray\n # chi_Q chi_I\n 1 2\n 3 4\n 5 6\n 7 8\n"
    xy_data = "1 2\n 3 4\n 5 6\n 7 8"
    unreadable_data = "This is a file with no data that is non-readable by " "LoadData"
    binary_data = b"\x00\x01\x02\x03\x04"

    with open(base_dir / "good_data.chi", "w") as f:
        f.write(chi_data)
    with open(base_dir / "good_data.xy", "w") as f:
        f.write(xy_data)
    with open(base_dir / "good_data.txt", "w") as f:
        f.write(chi_data)
    with open(base_dir / "unreadable_file.txt", "w") as f:
        f.write(unreadable_data)
    with open(base_dir / "binary.pkl", "wb") as f:
        f.write(binary_data)

    with open(input_dir / "good_data.chi", "w") as f:
        f.write(chi_data)
    with open(input_dir / "good_data.xy", "w") as f:
        f.write(xy_data)
    with open(input_dir / "good_data.txt", "w") as f:
        f.write(chi_data)
    with open(input_dir / "unreadable_file.txt", "w") as f:
        f.write(unreadable_data)
    with open(input_dir / "binary.pkl", "wb") as f:
        f.write(binary_data)

    with open(input_dir / "file_list.txt", "w") as f:
        f.write("good_data.chi \n good_data.xy \n good_data.txt \n missing_file.txt")
    with open(input_dir / "file_list_example2.txt", "w") as f:
        f.write("input_dir/*.txt \n")
        f.write("input_dir/good_data.chi \n")
        f.write("good_data.xy \n")
        f.write(f"{str(input_dir.resolve() / 'good_data.txt')}\n")

    yield tmp_path
