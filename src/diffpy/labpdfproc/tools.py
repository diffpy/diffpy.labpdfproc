from pathlib import Path

WAVELENGTHS = {"Mo": 0.71, "Ag": 0.59, "Cu": 1.54}
known_sources = [key for key in WAVELENGTHS.keys()]


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


def set_input_directory(args):
    """
    Set the input directory based on input file, default is current working directory if nothing is given

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    Returns
    -------
    args argparse.Namespace
        the arguments from the parser with a new argument input_directory

    """
    if args.input_file and args.input_file.endswith("/"):
        raise ValueError("Please remove the forward slash at the end and rerun specifying a valid file name.")
    input_dir = Path.cwd() / Path(args.input_file).parent if args.input_file else Path.cwd()
    if not input_dir.exists() or not input_dir.is_dir():
        raise ValueError(
            "Path to input file doesn't exist. "
            "Please rerun specifying a valid input file with a valid directory. "
            "Please avoid forward slashes in your path or file name."
        )
    setattr(args, "input_directory", input_dir)
    return args


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
