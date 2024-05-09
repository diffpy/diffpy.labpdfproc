import glob
import os
from pathlib import Path

WAVELENGTHS = {"Mo": 0.71, "Ag": 0.59, "Cu": 1.54}
known_sources = [key for key in WAVELENGTHS.keys()]


def set_input_files(args):
    """
    Set input directory and files

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    It is implemented as this:
    If input is a file, we first try to read it as a file list and store all listed file names.
    If any filename is invalid, then proceed to treat it as a data file.
    Otherwise if we have a directory, glob all files within it.

    Returns
    -------
    args argparse.Namespace

    """

    if not Path(args.input).exists():
        raise ValueError("Please specify valid input file or directory.")

    if not Path(args.input).is_dir():
        input_dir = Path.cwd() / Path(args.input).parent
        file_names = []
        with open(args.input, "r") as f:
            for line in f:
                if not os.path.isfile(line.strip()):
                    file_names = []
                    break
                else:
                    file_name = line.strip()
                    file_names.append(file_name)

        if len(file_names) > 0:
            input_file_name = file_names
        else:
            input_file_name = Path(args.input).name

    else:
        input_dir = Path(args.input).resolve()
        input_files = [file for file in glob.glob(str(input_dir) + "/*", recursive=True) if os.path.isfile(file)]
        input_file_name = [os.path.basename(input_file_path) for input_file_path in input_files]

    setattr(args, "input_directory", input_dir)
    setattr(args, "input_file", input_file_name)
    return args


def set_output_directory(args):
    """
    set the output directory based on the given input arguments

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    Returns
    -------
    pathlib.PosixPath that contains the full path of the output directory

    it is determined as follows:
    If user provides an output directory, use it.
    Otherwise, we set it to the current directory if nothing is provided.
    We then create the directory if it does not exist.

    """
    output_dir = Path(args.output_directory).resolve() if args.output_directory else Path.cwd().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def set_wavelength(args):
    """
    Set the wavelength based on the given input arguments

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    Returns
    -------
        float: the wavelength value

    we raise an ValueError if the input wavelength is non-positive
    or if the input anode_type is not one of the known sources

    """
    if args.wavelength is not None and args.wavelength <= 0:
        raise ValueError(
            "No valid wavelength. Please rerun specifying a known anode_type or a positive wavelength."
        )
    if not args.wavelength and args.anode_type and args.anode_type not in WAVELENGTHS:
        raise ValueError(
            f"Anode type not recognized. Please rerun specifying an anode_type from {*known_sources, }."
        )

    if args.wavelength:
        return args.wavelength
    elif args.anode_type:
        return WAVELENGTHS[args.anode_type]
    else:
        return WAVELENGTHS["Mo"]


def _load_key_value_pair(s):
    items = s.split("=")
    key = items[0].strip()
    if len(items) > 1:
        value = "=".join(items[1:])
    return (key, value)


def load_user_metadata(args):
    """
    Load user metadata into the provided argparse Namespace, raise ValueError if in incorrect format

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    Returns
    -------
    the updated argparse Namespace with user metadata inserted as key-value pairs

    """

    reserved_keys = vars(args).keys()

    if args.user_metadata:
        for item in args.user_metadata:
            if "=" not in item:
                raise ValueError(
                    "Please provide key-value pairs in the format key=value. "
                    "For more information, use `labpdfproc --help.`"
                )
            key, value = _load_key_value_pair(item)
            if key in reserved_keys:
                raise ValueError(f"{key} is a reserved name.  Please rerun using a different key name. ")
            if hasattr(args, key):
                raise ValueError(f"Please do not specify repeated keys: {key}. ")
            setattr(args, key, value)
    delattr(args, "user_metadata")
    return args
