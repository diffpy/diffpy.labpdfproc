import sys
from argparse import ArgumentParser
from pathlib import Path

from diffpy.labpdfproc.functions import apply_corr, compute_cve
from diffpy.labpdfproc.tools import known_sources, set_input_files, set_output_directory, set_wavelength
from diffpy.utils.parsers.loaddata import loadData
from diffpy.utils.scattering_objects.diffraction_objects import XQUANTITIES, Diffraction_object


def get_args():
    p = ArgumentParser()
    p.add_argument("mud", help="Value of mu*D for your " "sample. Required.", type=float)
    p.add_argument("-i", "--input-file", help="The filename of the " "datafile to load.")
    p.add_argument(
        "-a",
        "--anode-type",
        help=f"The type of the x-ray source. Allowed values are "
        f"{*[known_sources], }. Either specify a known x-ray source or specify wavelength.",
        default="Mo",
    )
    p.add_argument(
        "-w",
        "--wavelength",
        help="X-ray source wavelength in angstroms. Not needed if the anode-type "
        "is specified. This wavelength will override the anode wavelength if both are specified.",
        default=None,
        type=float,
    )
    p.add_argument(
        "-o",
        "--output-directory",
        help="The name of the output directory. If not specified "
        "then corrected files will be written to the current directory."
        "If the specified directory doesn't exist it will be created.",
        default=None,
    )
    p.add_argument(
        "-x",
        "--xtype",
        help=f"The quantity on the independent variable axis. Allowed "
        f"values: {*XQUANTITIES, }. If not specified then two-theta "
        f"is assumed for the independent variable. Only implemented for "
        f"tth currently.",
        default="tth",
    )
    p.add_argument(
        "-c",
        "--output-correction",
        action="store_true",
        help="The absorption correction will be output to a file if this "
        "flag is set. Default is that it is not output.",
        default="tth",
    )
    p.add_argument(
        "-f",
        "--force-overwrite",
        action="store_true",
        help="Outputs will not overwrite existing file unless --force is specified.",
    )
    args = p.parse_args()
    return args


def main():
    args = get_args()
    args = set_input_files(args)
    args.output_directory = set_output_directory(args)
    args.wavelength = set_wavelength(args)

    for input_file in args.input_file:
        filepath = Path(input_file)
        outfilestem = filepath.stem + "_corrected"
        corrfilestem = filepath.stem + "_cve"
        outfile = args.output_directory / (outfilestem + ".chi")
        corrfile = args.output_directory / (corrfilestem + ".chi")

        if outfile.exists() and not args.force_overwrite:
            sys.exit(
                f"Output file {str(outfile)} already exists. Please rerun "
                f"specifying -f if you want to overwrite it."
            )
        if corrfile.exists() and args.output_correction and not args.force_overwrite:
            sys.exit(
                f"Corrections file {str(corrfile)} was requested and already "
                f"exists. Please rerun specifying -f if you want to overwrite it."
            )

        input_pattern = Diffraction_object(wavelength=args.wavelength)

        try:
            xarray, yarray = loadData(args.input_file, unpack=True)
        except Exception as e:
            raise ValueError(f"Failed to load data from {filepath}: {e}.")

        input_pattern.insert_scattering_quantity(
            xarray,
            yarray,
            "tth",
            scat_quantity="x-ray",
            name=str(args.input_file),
            metadata={"muD": args.mud, "anode_type": args.anode_type},
        )

        absorption_correction = compute_cve(input_pattern, args.mud, args.wavelength)
        corrected_data = apply_corr(input_pattern, absorption_correction)
        corrected_data.name = f"Absorption corrected input_data: {input_pattern.name}"
        corrected_data.dump(f"{outfile}", xtype="tth")

        if args.output_correction:
            absorption_correction.dump(f"{corrfile}", xtype="tth")


if __name__ == "__main__":
    main()
