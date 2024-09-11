import copy
from pathlib import Path

from diffpy.labpdfproc.mud_calculator import compute_mud
from diffpy.utils.tools import get_package_info, get_user_info

WAVELENGTHS = {"Mo": 0.71, "Ag": 0.59, "Cu": 1.54}
known_sources = [key for key in WAVELENGTHS.keys()]
METADATA_KEYS_TO_EXCLUDE = ["output_correction", "force_overwrite", "input", "input_paths"]


def set_output_directory(args):
    """
    set the output directory based on the given input arguments

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    it is determined as follows:
    If user provides an output directory, use it.
    Otherwise, we set it to the current directory if nothing is provided.
    We then create the directory if it does not exist.

    Returns
    -------
    a Path object that contains the full path of the output directory
    """
    output_dir = Path(args.output_directory).resolve() if args.output_directory else Path.cwd().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _expand_user_input(args):
    """
    Expands the list of inputs by adding files from file lists and wildcards.

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    Returns
    -------
    the arguments with the modified input list

    """
    file_list_inputs = [input_name for input_name in args.input if "file_list" in input_name]
    for file_list_input in file_list_inputs:
        with open(file_list_input, "r") as f:
            file_inputs = [input_name.strip() for input_name in f.readlines()]
        args.input.extend(file_inputs)
        args.input.remove(file_list_input)
    wildcard_inputs = [input_name for input_name in args.input if "*" in input_name]
    for wildcard_input in wildcard_inputs:
        input_files = [str(file) for file in Path(".").glob(wildcard_input) if "file_list" not in file.name]
        args.input.extend(input_files)
        args.input.remove(wildcard_input)
    return args


def set_input_lists(args):
    """
    Set input directory and files.

    It takes cli inputs, checks if they are files or directories and creates
    a list of files to be processed which is stored in the args Namespace.

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    Returns
    -------
    args argparse.Namespace

    """

    input_paths = []
    args = _expand_user_input(args)
    for input_name in args.input:
        input_path = Path(input_name).resolve()
        if input_path.exists():
            if input_path.is_file():
                input_paths.append(input_path)
            elif input_path.is_dir():
                input_files = input_path.glob("*")
                input_files = [
                    file.resolve() for file in input_files if file.is_file() and "file_list" not in file.name
                ]
                input_paths.extend(input_files)
            else:
                raise FileNotFoundError(
                    f"Cannot find {input_name}. Please specify valid input file(s) or directories."
                )
        else:
            raise FileNotFoundError(f"Cannot find {input_name}.")
    setattr(args, "input_paths", list(set(input_paths)))
    return args


def set_wavelength(args):
    """
    Set the wavelength based on the given input arguments

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    we raise a ValueError if the input wavelength is non-positive
    or if the input anode_type is not one of the known sources

    Returns
    -------
    args argparse.Namespace
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
        delattr(args, "anode_type")
    elif args.anode_type:
        args.wavelength = WAVELENGTHS[args.anode_type]
    else:
        args.wavelength = WAVELENGTHS["Mo"]
    return args


def set_mud(args):
    """
    Set the mud based on the given input arguments

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    Returns
    -------
    args argparse.Namespace
    """
    if args.z_scan_file:
        filepath = Path(args.z_scan_file).resolve()
        if not filepath.is_file():
            raise FileNotFoundError(f"Cannot find {args.z_scan_file}. Please specify a valid file path.")
        args.z_scan_file = str(filepath)
        args.mud = compute_mud(filepath)
    return args


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


def load_user_info(args):
    """
    Update username and email using get_user_info function from diffpy.utils

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser, default is None

    Returns
    -------
    the updated argparse Namespace with username and email inserted

    """
    config = {"username": args.username, "email": args.email}
    config = get_user_info(config)
    args.username = config["username"]
    args.email = config["email"]
    return args


def load_package_info(args):
    """
    Load diffpy.labpdfproc package name and version into args using get_package_info function from diffpy.utils

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser, default is None

    Returns
    -------
    the updated argparse Namespace with diffpy.labpdfproc name and version inserted

    """
    metadata = get_package_info("diffpy.labpdfproc")
    setattr(args, "package_info", metadata["package_info"])
    return args


def preprocessing_args(args):
    """
    Perform preprocessing on the provided argparse Namespace

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser, default is None

    Returns
    -------
    the updated argparse Namespace with arguments preprocessed
    """
    args = load_package_info(args)
    args = load_user_info(args)
    args = set_input_lists(args)
    args.output_directory = set_output_directory(args)
    args = set_wavelength(args)
    args = set_mud(args)
    args = load_user_metadata(args)
    return args


def load_metadata(args, filepath):
    """
    Load relevant metadata from args

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    Returns
    -------
    A dictionary with relevant arguments from the parser
    """

    metadata = copy.deepcopy(vars(args))
    for key in METADATA_KEYS_TO_EXCLUDE:
        metadata.pop(key, None)
    metadata["input_directory"] = str(filepath)
    metadata["output_directory"] = str(metadata["output_directory"])
    return metadata
