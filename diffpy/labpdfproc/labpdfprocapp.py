import sys
from argparse import ArgumentParser

import numpy as np
from diffpy.labpdfproc.functions import compute_cve, apply_corr, WAVELENGTHS
from diffpy.utils.parsers.loaddata import loadData
from diffpy.utils.scattering_objects.diffraction_objects import Diffraction_object, XQUANTITIES

WAVELENGTHS = {"Mo": 0.71, "Ag": 0.59, "Cu": 1.54}
known_sources = [key for key in WAVELENGTHS.keys()]


def get_args():
    p = ArgumentParser()
    p.add_argument("mud", help="Value of mu*D for your sample. Required.", type=float)
    p.add_argument("-i", "--input-file", help="The filename of the datafile to load")
    p.add_argument("-a", "--anode-type", help=f"X-ray source, allowed values:{*[known_sources],}", default="Mo")
    p.add_argument("-w", "--wavelength", help=f"X-ray source wavelength. Not needed if the anode-type is specified. This will override the wavelength if anode type is specified", default=None, type=float)
    p.add_argument("-o", "--output-directory", help=f"the name of the output directory. If it doesn't exist it will be created.  Not currently implemented", default=None)
    p.add_argument("-x", "--xtype", help=f"the quantity on the independnt variable axis. allowed values:{*XQUANTITIES,}. If not specified then two-theta is assumed for the independent variable. Only implemented for tth currently", default="tth")
    args = p.parse_args()
    return args


def main():
    # we want the user to type the following:
    # labpdfproc <input_file> <mu> <diameter> <Ag, ag, Mo, mo, Cu, cu>

    # if they give less or more than 4 positional arguments, we return an error message.
    if len(sys.argv) < 4:
        print("usage: labpdfproc <input_file> <mu> <diameter> <lambda>")

    args = get_args()
    wavelength = WAVELENGTHS[args.anode_type]
    input_pattern = Diffraction_object(wavelength=wavelength)
    xarray, yarray = loadData(args.input_file, unpack=True)
    input_pattern.insert_scattering_quantity(xarray, yarray, "tth")

    abdo = compute_cve(input_pattern, args.mud, wavelength)
    abscormodo = apply_corr(input_pattern, abdo)

    base_name = args.input_file.split(".")[0]
    data_to_save = np.column_stack((abscormodo.on_tth[0], abscormodo.on_tth[1]))
    np.savetxt(f"{base_name}_proc.chi", data_to_save)


if __name__ == "__main__":
    main()
