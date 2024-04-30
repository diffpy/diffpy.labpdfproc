import sys
from argparse import ArgumentParser
from pathlib import Path

from diffpy.labpdfproc.functions import apply_corr, compute_cve
from diffpy.labpdfproc.tools import load_additional_info
from diffpy.utils.parsers.loaddata import loadData
from diffpy.utils.scattering_objects.diffraction_objects import XQUANTITIES, Diffraction_object

WAVELENGTHS = {"Mo": 0.71, "Ag": 0.59, "Cu": 1.54}
known_sources = [key for key in WAVELENGTHS.keys()]


def get_args():
    p = ArgumentParser()
    p.add_argument("mud", help="Value of mu*D for your " "sample. Required.", type=float)
    p.add_argument("-i", "--input-file", help="The filename of the " "datafile to load")
    p.add_argument(
        "-a", "--anode-type", help=f"X-ray source, allowed " f"values: {*[known_sources], }", default="Mo"
    )
    p.add_argument(
        "-w",
        "--wavelength",
        help="X-ray source wavelength. Not needed if the anode-type "
        "is specified. This will override the wavelength if anode "
        "type is specified",
        default=None,
        type=float,
    )
    p.add_argument(
        "-o",
        "--output-directory",
        help="the name of the output directory. If it doesn't exist it "
        "will be created.  Not currently implemented",
        default=None,
    )
    p.add_argument(
        "-x",
        "--xtype",
        help=f"the quantity on the independnt variable axis. allowed "
        f"values: {*XQUANTITIES, }. If not specified then two-theta "
        f"is assumed for the independent variable. Only implemented for "
        f"tth currently",
        default="tth",
    )
    p.add_argument(
        "-c",
        "--output-correction",
        action="store_true",
        help="the absorption correction will be output to a file if this "
        "flag is set. Default is that it is not output",
        default="tth",
    )
    p.add_argument(
        "-f",
        "--force-overwrite",
        action="store_true",
        help="outputs will not overwrite existing file unless --force is spacified",
    )
    p.add_argument(
        "-add",
        "--additional-info",
        metavar=("KEY=VALUE"),
        action="append",
        help="specify key-value pairs to be loaded into metadata by using key=value. "
        "You can specify multiple paris by calling -add multiple times.",
    )
    args = p.parse_args()
    return args


def main():
    args = get_args()
    args = load_additional_info(args)
    wavelength = WAVELENGTHS[args.anode_type]
    filepath = Path(args.input_file)
    outfilestem = filepath.stem + "_corrected"
    corrfilestem = filepath.stem + "_cve"
    outfile = Path(outfilestem + ".chi")
    corrfile = Path(corrfilestem + ".chi")

    if outfile.exists() and not args.force_overwrite:
        sys.exit(
            f"output file {str(outfile)} already exists. Please rerun "
            f"specifying -f if you want to overwrite it"
        )
    if corrfile.exists() and args.output_correction and not args.force_overwrite:
        sys.exit(
            f"corrections file {str(corrfile)} was requested and already "
            f"exists. Please rerun specifying -f if you want to overwrite it"
        )

    input_pattern = Diffraction_object(wavelength=wavelength)
    xarray, yarray = loadData(args.input_file, unpack=True)
    input_pattern.insert_scattering_quantity(
        xarray,
        yarray,
        "tth",
        scat_quantity="x-ray",
        name=str(args.input_file),
        metadata={"muD": args.mud, "anode_type": args.anode_type},
    )

    absorption_correction = compute_cve(input_pattern, args.mud, wavelength)
    corrected_data = apply_corr(input_pattern, absorption_correction)
    corrected_data.name = f"Absorption corrected input_data: {input_pattern.name}"
    corrected_data.dump(f"{outfile}", xtype="tth")

    if args.output_correction:
        absorption_correction.dump(f"{corrfile}", xtype="tth")


if __name__ == "__main__":
    main()
