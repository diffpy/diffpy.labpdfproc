import pytest

from diffpy.labpdfproc.labpdfprocapp import (
    apply_absorption_correction,
    get_args_cli,
)


# Case: user tries to run absorption correction, but the output
# filename already exists.
# expected: the function should raise a FileExistsError, telling the
# user that the output
# file already exists and asking if they want to overwrite it.
def test_file_exists_error(user_filesystem):
    input_data_file = str(user_filesystem / "data.chi")
    existing_corrected_file = str(user_filesystem / "data_corrected.chi")

    cli_inputs = ["mud"] + [input_data_file] + ["2.5"]
    args = get_args_cli(cli_inputs)
    # assert args == []
    msg = (
        "The following output files already exist:"
        f"\n{existing_corrected_file}\n"
        "Use --force to overwrite them."
    )
    with pytest.raises(FileExistsError, match=msg):
        apply_absorption_correction(args)
