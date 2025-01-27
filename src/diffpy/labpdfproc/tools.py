import copy
from pathlib import Path

from diffpy.utils.diffraction_objects import ANGLEQUANTITIES, QQUANTITIES, XQUANTITIES
from diffpy.utils.tools import check_and_build_global_config, compute_mud, get_package_info, get_user_info

# Reference values are taken from https://x-server.gmca.aps.anl.gov/cgi/www_dbli.exe?x0hdb=waves
# Ka1Ka2 values are calculated as: (Ka1 * 2 + Ka2) / 3
# For CuKa1Ka2: (1.54056 * 2 + 1.544398) / 3 = 1.54184
WAVELENGTHS = {
    "Mo": 0.71073,
    "MoKa1": 0.70930,
    "MoKa1Ka2": 0.71073,
    "Ag": 0.56087,
    "AgKa1": 0.55941,
    "AgKa1Ka2": 0.56087,
    "Cu": 1.54184,
    "CuKa1": 1.54056,
    "CuKa1Ka2": 1.54184,
}
known_sources = [key for key in WAVELENGTHS.keys()]

# Exclude wavelength from metadata to prevent duplication,
# as the dump function in diffpy.utils writes it explicitly.
METADATA_KEYS_TO_EXCLUDE = ["output_correction", "force_overwrite", "input", "input_paths", "wavelength"]


def set_output_directory(args):
    """Set the output directory based on the given input arguments.

    It is determined as follows:
    If user provides an output directory, use it.
    Otherwise, we set it to the current directory if nothing is provided.
    We then create the directory if it does not exist.

    Parameters
    ----------
    args : argparse.Namespace
        The arguments from the parser.

    Returns
    -------
    args : argparse.Namespace
        The updated arguments, with output_directory as the full path to the output file directory.
    """
    output_dir = Path(args.output_directory).resolve() if args.output_directory else Path.cwd().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    args.output_directory = output_dir
    return args


def _expand_user_input(args):
    """Expand the list of inputs by adding files from file lists and wildcards.

    Parameters
    ----------
    args : argparse.Namespace
        The arguments from the parser.

    Returns
    -------
    args : argparse.Namespace
        The updated arguments with the modified input list.
    """
    file_list_inputs = [input_name for input_name in args.input if "file_list" in input_name]
    for file_list_input in file_list_inputs:
        with open(file_list_input, "r") as f:
            file_inputs = [input_name.strip() for input_name in f.readlines()]
        args.input.extend(file_inputs)
        args.input.remove(file_list_input)
    wildcard_inputs = [input_name for input_name in args.input if "*" in input_name]
    for wildcard_input in wildcard_inputs:
        input_files = [
            str(file)
            for file in Path(".").glob(wildcard_input)
            if "file_list" not in file.name and "diffpyconfig.json" not in file.name
        ]
        args.input.extend(input_files)
        args.input.remove(wildcard_input)
    return args


def set_input_lists(args):
    """Set input directory and files. It takes cli inputs, checks if they are files or directories and creates
    a list of files to be processed which is stored in the args Namespace.

    Parameters
    ----------
    args : argparse.Namespace
        The arguments from the parser.

    Raises
    ------
    FileNotFoundError
        Raised when an input is invalid.

    Returns
    -------
    args : argparse.Namespace
        The updated arguments with the modified input list.
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
                    file.resolve()
                    for file in input_files
                    if file.is_file() and "file_list" not in file.name and "diffpyconfig.json" not in file.name
                ]
                input_paths.extend(input_files)
            else:
                raise FileNotFoundError(
                    f"Cannot find {input_name}. Please specify valid input file(s) or directories."
                )
        else:
            raise FileNotFoundError(
                f"Cannot find {input_name}. Please specify valid input file(s) or directories."
            )
    setattr(args, "input_paths", list(set(input_paths)))
    return args


def set_wavelength(args):
    """Set the wavelength based on the given anode_type. If a wavelength is provided,
    it will be used, and the anode_type argument will be removed.

    Parameters
    ----------
    args : argparse.Namespace
        The arguments from the parser.

    Raises
    ------
    ValueError
        Raised when input wavelength is non-positive or if input anode_type is not one of the known sources.

    Returns
    -------
    args : argparse.Namespace
        The updated arguments with the wavelength.
    """
    if args.wavelength is not None and args.wavelength <= 0:
        raise ValueError(
            "No valid wavelength. Please rerun specifying a known anode_type or a positive wavelength."
        )
    elif not args.wavelength and args.anode_type:
        matched_anode_type = next((key for key in WAVELENGTHS if key.lower() == args.anode_type.lower()), None)
        if matched_anode_type is None:
            raise ValueError(
                f"Anode type not recognized. Please rerun specifying an anode_type from {*known_sources, }."
            )
        args.anode_type = matched_anode_type
        args.wavelength = WAVELENGTHS[args.anode_type]
    elif not args.wavelength:
        args.wavelength = WAVELENGTHS["Mo"]
    else:
        delattr(args, "anode_type")
    return args


def set_xtype(args):
    f"""Set the xtype based on the given input arguments, raise an error if xtype is not one of {*XQUANTITIES, }.

    Parameters
    ----------
    args : argparse.Namespace
        The arguments from the parser.

    Returns
    -------
    args : argparse.Namespace
        The updated arguments with the xtype as one of q, tth, or d.
    """
    if args.xtype.lower() not in XQUANTITIES:
        raise ValueError(f"Unknown xtype: {args.xtype}. Allowed xtypes are {*XQUANTITIES, }.")
    args.xtype = (
        "q" if args.xtype.lower() in QQUANTITIES else "tth" if args.xtype.lower() in ANGLEQUANTITIES else "d"
    )
    return args


def set_mud(args):
    """Compute mu*D based on the given z-scan file, if provided.

    Parameters
    ----------
    args : argparse.Namespace
        The arguments from the parser.

    Returns
    -------
    args : argparse.Namespace
        The updated arguments with mu*D.
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
    return key, value


def load_user_metadata(args):
    """Load user metadata into args, raise ValueError if it is in incorrect format.

    Parameters
    ----------
    args : argparse.Namespace
        The arguments from the parser.

    Returns
    -------
    args : argparse.Namespace
        The updated argparse Namespace with user metadata inserted as key-value pairs.
    """

    reserved_keys = set(vars(args).keys())

    if args.user_metadata:
        for item in args.user_metadata:
            if "=" not in item:
                raise ValueError(
                    "Please provide key-value pairs in the format key=value. "
                    "For more information, use `labpdfproc --help.`"
                )
            key, value = _load_key_value_pair(item)
            if key in reserved_keys:
                raise ValueError(f"{key} is a reserved name. Please rerun using a different key name.")
            if hasattr(args, key):
                raise ValueError(f"Please do not specify repeated keys: {key}.")
            setattr(args, key, value)
    delattr(args, "user_metadata")
    return args


def load_user_info(args):
    """Load user info into args. If none is provided, call check_and_build_global_config function from
    diffpy.utils to prompt the user for inputs. Otherwise, call get_user_info with the provided arguments.

    Parameters
    ----------
    args : argparse.Namespace
        The arguments from the parser.

    Returns
    -------
    args : argparse.Namespace
        The updated argparse Namespace with username, email, and orcid inserted.
    """
    if args.username is None or args.email is None:
        check_and_build_global_config()
    config = get_user_info(owner_name=args.username, owner_email=args.email, owner_orcid=args.orcid)
    args.username = config.get("owner_name")
    args.email = config.get("owner_email")
    args.orcid = config.get("owner_orcid")
    return args


def load_package_info(args):
    """Load diffpy.labpdfproc package name and version into args using get_package_info function from diffpy.utils.

    Parameters
    ----------
    args : argparse.Namespace
        The arguments from the parser.

    Returns
    -------
    args : argparse.Namespace
        The updated argparse Namespace with diffpy.labpdfproc name and version inserted.
    """
    metadata = get_package_info("diffpy.labpdfproc")
    setattr(args, "package_info", metadata["package_info"])
    return args


def preprocessing_args(args):
    """Perform preprocessing on the provided args.
    The process includes loading package and user information,
    setting input, output, wavelength, xtype, mu*D, and loading user metadata.

    Parameters
    ----------
    args : argparse.Namespace
        The arguments from the parser.

    Returns
    -------
    args : argparse.Namespace
        The updated argparse Namespace with arguments preprocessed.
    """
    args = load_package_info(args)
    args = load_user_info(args)
    args = set_input_lists(args)
    args = set_output_directory(args)
    args = set_wavelength(args)
    args = set_xtype(args)
    args = set_mud(args)
    args = load_user_metadata(args)
    return args


def load_metadata(args, filepath):
    """Load the relevant metadata from args to write into the header of the output files.

    Parameters
    ----------
    args : argparse.Namespace
        The arguments from the parser.

    filepath : Path
        The filepath of the current input file.

    Returns
    -------
    metadata : dict
        The dictionary with relevant arguments from the parser.
    """
    metadata = copy.deepcopy(vars(args))
    for key in METADATA_KEYS_TO_EXCLUDE:
        metadata.pop(key, None)
    metadata["input_directory"] = str(filepath)
    metadata["output_directory"] = str(metadata["output_directory"])
    return metadata
