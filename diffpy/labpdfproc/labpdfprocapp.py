import sys
from argparse import ArgumentParser

import numpy as np
from diffpy.labpdfproc.functions import compute_cve, apply_corr, wavelengths
from diffpy.utils.parsers.loaddata import loadData
from diffpy.utils.scattering_objects.diffraction_objects import Diffraction_object


known_sources = ["Ag", "Mo"]



def get_args():
    p = ArgumentParser()
    p.add_argument("data_file", help="the filename of the datafile to load")
    p.add_argument("mud", help="mu*D for your sample", type=float)
    p.add_argument("--anode_type", help=f"x-ray source, allowed values:{*[known_sources],}", default="Mo")
    args = p.parse_args()
    return args

def main():
    # we want the user to type the following:
    # labpdfproc <input_file> <mu> <diameter> <Ag, ag, Mo, mo, Cu, cu>

    # if they give less or more than 4 positional arguments, we return an error message.
    if len(sys.argv) < 4:
        print('usage: labpdfproc <input_file> <mu> <diameter> <lambda>')
    
    args = get_args()
    wavelength = wavelengths[args.anode_type]
    input_pattern = Diffraction_object(wavelength=wavelength)
    xarray, yarray = loadData(args.data_file, unpack=True)
    input_pattern.insert_scattering_quantity(xarray, yarray, "tth")

    abdo = compute_cve(input_pattern, args.mud, wavelength)
    abscormodo = apply_corr(input_pattern, abdo)

    base_name = args.data_file.split('.')[0]
    data_to_save = np.column_stack((abscormodo.on_tth[0], abscormodo.on_tth[1]))
    np.savetxt(f'{base_name}_proc.chi', data_to_save)

if __name__ == '__main__':
    main()
