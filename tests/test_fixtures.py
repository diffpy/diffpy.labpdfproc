import os

import pytest

from diffpy.utils.parsers import loadData


# Test that our readable and unreadable files are indeed readable and
# unreadable by loadData (which is our definition of readable and unreadable)
def test_loadData_with_input_files(user_filesystem):
    os.chdir(user_filesystem)
    xarray_chi, yarray_chi = loadData("good_data.chi", unpack=True)
    xarray_xy, yarray_xy = loadData("good_data.xy", unpack=True)
    xarray_txt, yarray_txt = loadData("good_data.txt", unpack=True)
    with pytest.raises(ValueError):
        xarray_txt, yarray_txt = loadData("unreadable_file.txt", unpack=True)
    with pytest.raises(ValueError):
        xarray_pkl, yarray_pkl = loadData("binary.pkl", unpack=True)
