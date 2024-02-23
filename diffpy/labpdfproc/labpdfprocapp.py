import sys
import numpy as np

def load_data(input_file):
    # we want to load .xy, xye, file types. These are the most common. For anyting else (.snc, .txt, .csv, .dat) we return an error message. Why: some of them have different delimineters.
    # we want to load the tth column in a numpy array 
    # we want to load the intensitie Im into a numpy array
    # the input files should not contain any header. Typically, .xy or .xye files don't contain headers.
    tth = np.loadtxt(input_file, usecols=0)
    i_m = np.loadtxt(input_file, usecols=1)
    # this should return an error if the first row contains anything except a float, and if the columns are not separated by a space. 
    # I think the latter is also dealt with if we check if the first elemnt in one tth is a flaot.
    if np.issubdtype(tth[0], np.floating) and np.issubdtype(i_m[0], np.floating):
        return tth, i_m
    else:
        raise ValueError('Error: your .xy contains headers. Delete the header rows in your .xy or .xye file')
    
def tth_to_q(tth, wl):
    tth_rad = np.deg2rad(tth)
    q = (4 * np.pi / wl) * np.sin(tth_rad / 2)
    return q

def compute_cve(tth, mu, wl, diameter):
    # for a given mu and d and lambda, we will compute cve on a tth grid
    
    # something arbitrary for the moment
    cve = np.ones(len(tth))
    cve = cve * mu * wl * diameter

    return cve

def apply_corr(i_m, cve):
    # we apply the absorption correction by doing: I(tth) * c_ve
    i_c = i_m * cve
    return i_c

# def write_files(base_name):
    # we save the corrected intensities in a two-column file on a q-grid and a tth-grid.
    # we need to know the x-ray wavelenth so that we can convert tth to q
    # we make a new two-column file .chi where column 1 contains the q grid and columnt 2 contains the corrected intensities.
    

def main():
    # we want the user to type the following:
    # labpdfproc <input_file> <mu> <diameter> <Ag, ag, Mo, mo, Cu, cu>

    # if they give less or more than 4 positional arguments, we return an error message.
    if len(sys.argv) < 4:
        print('usage: labpdfcor <input_file> <mu> <diameter> <lambda>')
    

    input_file = sys.argv[1]
    tth, i_m = load_data(input_file)

    mu = float(sys.argv[2])
    diameter = float(sys.argv[3])
    wl = float(sys.argv[4])
    cve = compute_cve(tth, mu, diameter, wl)
    i_c = apply_corr(i_m, cve)
    q = tth_to_q(tth, wl)

    # get the basename from the input_file and save the corrected patter as a .tth and a .chi file.
    base_name = input_file.split('.')[0]
    output_chi = f"{base_name}.chi"
    output_tth = f"{base_name}.tth"
    np.savetxt(output_tth, np.column_stack((tth, i_c)), header='tth I(tth)')
    np.savetxt(output_chi, np.column_stack((q, i_c)), header='tth I(tth)')

if __name__ == '__main__':
    main()