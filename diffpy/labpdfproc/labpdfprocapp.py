import sys
from argparse import ArgumentParser

from diffpy.labpdfproc.functions import compute_cve, apply_corr, wavelengths
from diffpy.utils.parsers.loaddata import loadData
from diffpy.utils.scattering_objects import DiffractionObject


known_sources = ["Ag", "Mo"]
# def load_data(input_file):
#     # we want to load .xy, xye, file types. These are the most common. For anyting else (.snc, .txt, .csv, .dat) we return an error message. Why: some of them have different delimineters.
#     # we want to load the tth column in a numpy array 
#     # we want to load the intensitie Im into a numpy array
#     # the input files should not contain any header. Typically, .xy or .xye files don't contain headers.
#     tth = np.loadtxt(input_file, usecols=0)
#     i_m = np.loadtxt(input_file, usecols=1)
#     # this should return an error if the first row contains anything except a float, and if the columns are not separated by a space. 
#     # I think the latter is also dealt with if we check if the first elemnt in one tth is a flaot.
#     if np.issubdtype(tth[0], np.floating) and np.issubdtype(i_m[0], np.floating):
#         return tth, i_m
#     else:
#         raise ValueError('Error: your .xy contains headers. Delete the header rows in your .xy or .xye file')

# def tth_to_q(tth, wl):
#     tth_rad = np.deg2rad(tth)
#     q = (4 * np.pi / wl) * np.sin(tth_rad / 2)
#     return q



# def write_files(base_name):
    # we save the corrected intensities in a two-column file on a q-grid and a tth-grid.
    # we need to know the x-ray wavelenth so that we can convert tth to q
    # we make a new two-column file .chi where column 1 contains the q grid and columnt 2 contains the corrected intensities.

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
    input_pattern = DiffractionObject()
    xarray, yarray = loadData(args.data_file, unpack=True)
    input_pattern.insert_scattering_quantity(xarray, yarray, "tth", metadata={ })

    cve = compute_cve(input_pattern, args.mud, wavelength)
    i_c = input_pattern * cve

    # get the basename from the input_file and save the corrected patter as a .tth and a .chi file.
    # base_name = input_file.split('.')[0]
    # output_chi = f"{base_name}.chi"
    # output_tth = f"{base_name}.tth"
    # np.savetxt(output_tth, np.column_stack((tth, i_c)), header='tth I(tth)')
    # np.savetxt(output_chi, np.column_stack((q, i_c)), header='tth I(tth)')
    input_pattern.dump("filename", type="chi")

if __name__ == '__main__':
    main()
