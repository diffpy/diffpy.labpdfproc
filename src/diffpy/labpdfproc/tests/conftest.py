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

    yield tmp_path
