import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from diffpy.utils.scattering_objects.diffraction_objects import Diffraction_object

RADIUS_MM = 1
N_POINTS_ON_DIAMETER = 300
TTH_GRID = np.arange(1, 180.1, 0.1)
CVE_METHODS = ["brute_force", "polynomial_interpolation"]

# pre-computed datasets for polynomial interpolation (fast calculation)
MUD_LIST = [0.5, 1, 2, 3, 4, 5, 6]
CWD = Path(__file__).parent.resolve()
MULS = np.loadtxt(CWD / "data" / "inverse_cve.xy")
COEFFICIENT_LIST = np.array(pd.read_csv(CWD / "data" / "coefficient_list.csv", header=None))
INTERPOLATION_FUNCTIONS = [interp1d(MUD_LIST, coefficients, kind="quadratic") for coefficients in COEFFICIENT_LIST]


class Gridded_circle:
    def __init__(self, radius=1, n_points_on_diameter=N_POINTS_ON_DIAMETER, mu=None):
        self.radius = radius
        self.npoints = n_points_on_diameter
        self.mu = mu
        self.distances = []
        self.muls = []
        self._get_grid_points()

    def _get_grid_points(self):
        """
        given a radius and a grid size, return a grid of points to uniformly sample that circle
        """
        xs = np.linspace(-self.radius, self.radius, self.npoints)
        ys = np.linspace(-self.radius, self.radius, self.npoints)
        self.grid = {(x, y) for x in xs for y in ys if x**2 + y**2 <= self.radius**2}
        self.total_points_in_grid = len(self.grid)

    def set_distances_at_angle(self, angle):
        """
        given an angle, set the distances from the grid points to the entry and exit coordinates

        Parameters
        ----------
        angle float
          the angle in degrees

        Returns
        -------
        the list of distances containing total distance, primary distance and secondary distance

        """
        self.primary_distances, self.secondary_distances, self.distances = [], [], []
        for coord in self.grid:
            distance, primary, secondary = self.get_path_length(coord, angle)
            self.distances.append(distance)
            self.primary_distances.append(primary)
            self.secondary_distances.append(secondary)

    def set_muls_at_angle(self, angle):
        """
        compute muls = exp(-mu*distance) for a given angle

        Parameters
        ----------
        angle float
          the angle in degrees

        Returns
        -------
        an array of floats containing the muls corresponding to each angle

        """
        mu = self.mu
        self.muls = []
        if len(self.distances) == 0:
            self.set_distances_at_angle(angle)
        for distance in self.distances:
            self.muls.append(np.exp(-mu * distance))

    def _get_entry_exit_coordinates(self, coordinate, angle):
        """
        get the coordinates where the beam enters and leaves the circle for a given angle and grid point

        Parameters
        ----------
        grid_point tuple of floats
          the coordinates of the grid point

        angle float
          the angle in degrees

        radius float
          the radius of the circle in units of inverse mu

        it is calculated in the following way:
        For the entry coordinate, the y-component will be the y of the grid point and the x-component will be minus
        the value of x on the circle at the height of this y.

        For the exit coordinate:
        Find the line y = ax + b that passes through grid_point at angle angle
        The circle is x^2 + y^2 = r^2
        The exit point is where these are simultaneous equations
        x^2 + y^2 = r^2 & y = ax + b
        x^2 + (ax+b)^2 = r^2
        => x^2 + a^2x^2 + 2abx + b^2 - r^2 = 0
        => (1+a^2) x^2 + 2abx + (b^2 - r^2) = 0
        to find x_exit we find the roots of these equations and pick the root that is above y-grid
        then we get y_exit from y_exit = a*x_exit + b

        Returns
        -------
        (1) the coordinate of the entry point and (2) of the exit point of a beam entering horizontally
        impinging on a coordinate point that lies in the circle and then exiting at some angle, angle.

        """
        epsilon = 1e-7  # precision close to 90
        angle = math.radians(angle)
        xgrid = coordinate[0]
        ygrid = coordinate[1]

        entry_point = (-math.sqrt(self.radius**2 - ygrid**2), ygrid)

        if not math.isclose(angle, math.pi / 2, abs_tol=epsilon):
            b = ygrid - xgrid * math.tan(angle)
            a = math.tan(angle)
            xexit_root1, xexit_root2 = np.roots((1 + a**2, 2 * a * b, b**2 - self.radius**2))
            yexit_root1 = a * xexit_root1 + b
            yexit_root2 = a * xexit_root2 + b
            if yexit_root2 >= yexit_root1:  # We pick the point above
                exit_point = (xexit_root2, yexit_root2)
            else:
                exit_point = (xexit_root1, yexit_root1)
        else:
            exit_point = (xgrid, math.sqrt(self.radius**2 - xgrid**2))

        return entry_point, exit_point

    def get_path_length(self, grid_point, angle):
        """
        return the path length

        This is the pathlength of a horizontal line entering the circle at the
        same height to the grid point then exiting at angle angle

        Parameters
        ----------
        grid_point double of floats
          the coordinate inside the circle

        angle float
          the angle of the output beam

        radius
          the radius of the circle

        Returns
        -------
        floats total distance, primary distance and secondary distance

        """

        # move angle a tad above zero if it is zero to avoid it having the wrong sign due to some rounding error
        angle_delta = 0.000001
        if angle == float(0):
            angle = angle + angle_delta
        entry, exit = self._get_entry_exit_coordinates(grid_point, angle)
        primary_distance = math.dist(grid_point, entry)
        secondary_distance = math.dist(grid_point, exit)
        total_distance = primary_distance + secondary_distance
        return total_distance, primary_distance, secondary_distance


def _cve_brute_force(diffraction_data, mud):
    """
    compute cve for the given mud on a global grid using the brute-force method
    assume mu=mud/2, given that the same mu*D yields the same cve and D/2=1
    """

    mu_sample_invmm = mud / 2
    abs_correction = Gridded_circle(mu=mu_sample_invmm)
    distances, muls = [], []
    for angle in TTH_GRID:
        abs_correction.set_distances_at_angle(angle)
        abs_correction.set_muls_at_angle(angle)
        distances.append(sum(abs_correction.distances))
        muls.append(sum(abs_correction.muls))
    distances = np.array(distances) / abs_correction.total_points_in_grid
    muls = np.array(muls) / abs_correction.total_points_in_grid
    cve = 1 / muls

    cve_do = Diffraction_object(wavelength=diffraction_data.wavelength)
    cve_do.insert_scattering_quantity(
        TTH_GRID,
        cve,
        "tth",
        metadata=diffraction_data.metadata,
        name=f"absorption correction, cve, for {diffraction_data.name}",
        wavelength=diffraction_data.wavelength,
        scat_quantity="cve",
    )
    return cve_do


def _cve_polynomial_interpolation(diffraction_data, mud):
    """
    compute cve using polynomial interpolation method, raise an error if mu*D is out of the range (0.5 to 6)
    """

    if mud > 6 or mud < 0.5:
        raise ValueError(
            f"mu*D is out of the acceptable range (0.5 to 6) for polynomial interpolation. "
            f"Please rerun with a value within this range or specifying another method from {* CVE_METHODS, }."
        )
    coeff_a, coeff_b, coeff_c, coeff_d, coeff_e = [
        interpolation_function(mud) for interpolation_function in INTERPOLATION_FUNCTIONS
    ]
    muls = np.array(coeff_a * MULS**4 + coeff_b * MULS**3 + coeff_c * MULS**2 + coeff_d * MULS + coeff_e)
    cve = 1 / muls

    cve_do = Diffraction_object(wavelength=diffraction_data.wavelength)
    cve_do.insert_scattering_quantity(
        TTH_GRID,
        cve,
        "tth",
        metadata=diffraction_data.metadata,
        name=f"absorption correction, cve, for {diffraction_data.name}",
        wavelength=diffraction_data.wavelength,
        scat_quantity="cve",
    )
    return cve_do


def _cve_method(method):
    """
    retrieve the cve computation function for the given method
    """
    methods = {
        "brute_force": _cve_brute_force,
        "polynomial_interpolation": _cve_polynomial_interpolation,
    }
    if method not in CVE_METHODS:
        raise ValueError(f"Unknown method: {method}. Allowed methods are {*CVE_METHODS, }.")
    return methods[method]


def compute_cve(diffraction_data, mud, method="polynomial_interpolation"):
    f"""
    compute and interpolate the cve for the given diffraction data and mud using the selected method
    Parameters
    ----------
    diffraction_data Diffraction_object
      the diffraction pattern
    mud float
      the mu*D of the diffraction object, where D is the diameter of the circle
    method str
      the method used to calculate cve, must be one of {* CVE_METHODS, }

    Returns
    -------
    the diffraction object with cve curves
    """

    cve_function = _cve_method(method)
    abdo_on_global_tth = cve_function(diffraction_data, mud)
    global_tth = abdo_on_global_tth.on_tth[0]
    cve_on_global_tth = abdo_on_global_tth.on_tth[1]
    orig_grid = diffraction_data.on_tth[0]
    newcve = np.interp(orig_grid, global_tth, cve_on_global_tth)
    cve_do = Diffraction_object(wavelength=diffraction_data.wavelength)
    cve_do.insert_scattering_quantity(
        orig_grid,
        newcve,
        "tth",
        metadata=diffraction_data.metadata,
        name=f"absorption correction, cve, for {diffraction_data.name}",
        wavelength=diffraction_data.wavelength,
        scat_quantity="cve",
    )

    return cve_do


def apply_corr(diffraction_pattern, absorption_correction):
    """
    Apply absorption correction to the given diffraction object modo with the correction diffraction object abdo

    Parameters
    ----------
    diffraction_pattern Diffraction_object
      the input diffraction object to which the cve will be applied
    absorption_correction Diffraction_object
      the diffraction object that contains the cve to be applied

    Returns
    -------
    a corrected diffraction object with the correction applied through multiplication

    """

    corrected_pattern = diffraction_pattern * absorption_correction
    return corrected_pattern
