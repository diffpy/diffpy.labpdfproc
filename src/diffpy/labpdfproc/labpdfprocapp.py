import sys
from argparse import ArgumentParser

from gooey import Gooey, GooeyParser

from diffpy.labpdfproc.functions import CVE_METHODS, apply_corr, compute_cve
from diffpy.labpdfproc.tools import (
    known_sources,
    load_metadata,
    preprocessing_args,
)
from diffpy.utils.diffraction_objects import XQUANTITIES, DiffractionObject
from diffpy.utils.parsers.loaddata import loadData

theoretical_mud_hmsg_suffix = (
    "in that exact order, "
    "separated by commas (e.g., ZrO2,17.45,0.5). "
    "If you add whitespaces, "
    "enclose it in quotes (e.g., 'ZrO2, 17.45, 0.5'). "
)


def _define_arguments():
    args = [
        {
            "name": ["input"],
            "help": (
                "The filename(s) or folder(s) of the datafile(s) to load. "
                "Required.\n"
                "Supply a space-separated list of files or directories. "
                "Avoid spaces in filenames when possible; "
                "if present, enclose the name in quotes. "
                "Long lists can be supplied, one per line, "
                "in a file with name file_list.txt. "
                "If one or more directory is provided, all valid "
                "data-files in that directory will be processed. "
                "Examples of valid inputs are 'file.xy', 'data/file.xy', "
                "'file.xy data/file.xy', "
                "'.' (load everything in the current directory), "
                "'data' (load everything in the folder ./data), "
                "'data/file_list.txt' (load the list of files "
                "contained in the text-file called file_list.txt "
                "that can be found in the folder ./data), "
                "'./*.chi', 'data/*.chi' "
                "(load all files with extension .chi in the folder ./data)."
            ),
            "nargs": "+",
            "widget": "MultiFileChooser",
        },
        {
            "name": ["-a", "--anode-type"],
            "help": (
                f"The type of the x-ray source. "
                f"Allowed values are {*known_sources, }. "
                f"Either specify a known x-ray source or specify wavelength."
            ),
            "default": None,
        },
        {
            "name": ["-w", "--wavelength"],
            "help": (
                "X-ray source wavelength in angstroms. "
                "Not needed if the anode-type is specified."
            ),
            "type": float,
        },
        {
            "name": ["-o", "--output-directory"],
            "help": (
                "The name of the output directory. "
                "If not specified then corrected files will be "
                "written to the current directory. "
                "If the specified directory doesn't exist it will be created."
            ),
            "default": None,
            "widget": "DirChooser",
        },
        {
            "name": ["-x", "--xtype"],
            "help": (
                f"The quantity on the independent variable axis. "
                f"Allowed values: {*XQUANTITIES, }. "
                f"If not specified then two-theta "
                f"is assumed for the independent variable."
            ),
            "default": "tth",
        },
        {
            "name": ["-c", "--output-correction"],
            "help": (
                "The absorption correction will be output to a file "
                "if this flag is set. "
                "Default is that it is not output."
            ),
            "action": "store_true",
        },
        {
            "name": ["-f", "--force-overwrite"],
            "help": "Outputs will not overwrite existing file "
            "unless --force is specified.",
            "action": "store_true",
        },
        {
            "name": ["-m", "--method"],
            "help": (
                f"The method for computing absorption correction. "
                f"Allowed methods: {*CVE_METHODS, }. "
                f"Default method is polynomial interpolation "
                f"if not specified."
            ),
            "default": "polynomial_interpolation",
        },
        {
            "name": ["-u", "--user-metadata"],
            "help": (
                "Specify key-value pairs to be loaded into metadata "
                "using the format key=value. "
                "Separate pairs with whitespace, "
                "and ensure no whitespaces before or after the = sign. "
                "Avoid using = in keys. If multiple = signs are present, "
                "only the first separates the key and value. "
                "If a key or value contains whitespace, enclose it in quotes. "
                "For example, facility='NSLS II', "
                "'facility=NSLS II', beamline=28ID-2, "
                "'beamline'='28ID-2', 'favorite color'=blue, "
                "are all valid key=value items."
            ),
            "nargs": "+",
            "metavar": "KEY=VALUE",
        },
        {
            "name": ["-n", "--username"],
            "help": (
                "Username will be loaded from config files. "
                "Specify here only if you want to "
                "override that behavior at runtime."
            ),
            "default": None,
        },
        {
            "name": ["-e", "--email"],
            "help": (
                "Email will be loaded from config files. "
                "Specify here only if you want to "
                "override that behavior at runtime."
            ),
            "default": None,
        },
        {
            "name": ["--orcid"],
            "help": (
                "ORCID will be loaded from config files. "
                "Specify here only if you want to "
                "override that behavior at runtime."
            ),
            "default": None,
        },
    ]
    return args


def _add_mud_selection_group(p, use_gui=False):
    """Current Options:
    1. Manually enter muD (`--mud`).
    2. Estimate from a z-scan file (`-z` or `--z-scan-file`).
    3. Estimate theoretically based on sample mass density
    (`-d` or `--theoretical-from-density`).
    4. Estimate theoretically based on packing fraction
    (`-p` or `--theoretical-from-packing`).
    """
    g = p.add_argument_group("Options for setting mu*D value (Required)")
    g = g.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--mud",
        type=float,
        help="Enter the mu*D value manually.",
        **({"widget": "DecimalField"} if use_gui else {}),
    )
    g.add_argument(
        "-z",
        "--z-scan-file",
        help=(
            "Estimate mu*D experimentally from a z-scan file. "
            "Specify the path to the file "
            "used to compute the mu*D value."
        ),
        **({"widget": "FileChooser"} if use_gui else {}),
    )
    g.add_argument(
        "-d",
        "--theoretical-from-density",
        help=(
            "Estimate mu*D theoretically using sample mass density. "
            "Specify the chemical formula, incident x-ray energy (in keV), "
            "and sample mass density (in g/cm^3), "
            + theoretical_mud_hmsg_suffix
        ),
    )
    g.add_argument(
        "-p",
        "--theoretical-from-packing",
        help=(
            "Estimate mu*D theoretically using packing fraction. "
            "Specify the chemical formula, incident x-ray energy (in keV), "
            "and packing fraction (0 to 1), " + theoretical_mud_hmsg_suffix
        ),
    )
    return p


def _register_applymud_subparser(subp, use_gui=False):
    applymudp = subp.add_parser(
        "applymud", help="Apply absorption correction."
    )
    _add_mud_selection_group(applymudp, use_gui=use_gui)
    for arg in _define_arguments():
        names = arg["name"]
        options = {k: v for k, v in arg.items() if k != "name"}
        if not use_gui and "widget" in options:
            options.pop("widget")
        applymudp.add_argument(*names, **options)


def create_parser(use_gui=False):
    p = GooeyParser() if use_gui else ArgumentParser()
    subp = p.add_subparsers(title="subcommand", dest="subcommand")
    _register_applymud_subparser(subp, use_gui)
    return p


@Gooey(
    required_cols=1,
    optional_cols=1,
    show_sidebar=True,
    program_name="labpdfproc GUI",
)
def _get_args_gui():
    p = create_parser(use_gui=True)
    args = p.parse_args()
    return args


def _get_args_cli(override_cli_inputs=None):
    p = create_parser(use_gui=False)
    args = p.parse_args(override_cli_inputs)
    return args


def get_args(override_cli_inputs=None, use_gui=False):
    return _get_args_gui() if use_gui else _get_args_cli(override_cli_inputs)


def applymud(args):
    args = preprocessing_args(args)
    for filepath in args.input_paths:
        outfilestem = filepath.stem + "_corrected"
        corrfilestem = filepath.stem + "_cve"
        outfile = args.output_directory / (outfilestem + ".chi")
        corrfile = args.output_directory / (corrfilestem + ".chi")

        if outfile.exists() and not args.force_overwrite:
            sys.exit(
                f"Output file {str(outfile)} already exists. "
                f"Please rerun specifying -f if you want to overwrite it."
            )
        if (
            corrfile.exists()
            and args.output_correction
            and not args.force_overwrite
        ):
            sys.exit(
                f"Corrections file {str(corrfile)} "
                f"was requested and already exists. "
                f"Please rerun specifying -f if you want to overwrite it."
            )

        xarray, yarray = loadData(filepath, unpack=True)
        input_pattern = DiffractionObject(
            xarray=xarray,
            yarray=yarray,
            xtype=args.xtype,
            wavelength=args.wavelength,
            scat_quantity="x-ray",
            name=filepath.stem,
            metadata=load_metadata(args, filepath),
        )

        absorption_correction = compute_cve(
            input_pattern, args.mud, args.method, args.xtype
        )
        corrected_data = apply_corr(input_pattern, absorption_correction)
        corrected_data.name = (
            f"Absorption corrected input_data: " f"{input_pattern.name}"
        )
        corrected_data.dump(f"{outfile}", xtype=args.xtype)

        if args.output_correction:
            absorption_correction.dump(f"{corrfile}", xtype=args.xtype)


def run_subcommand(args):
    if args.subcommand == "applymud":
        return applymud(args)
    else:
        raise ValueError(f"Unknown subcommand: {args.subcommand}")


def main():
    use_gui = len(sys.argv) == 1 or "--gui" in sys.argv
    args = get_args(use_gui=use_gui)
    return run_subcommand(args)


if __name__ == "__main__":
    main()
