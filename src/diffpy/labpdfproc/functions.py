import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from diffpy.utils.diffraction_objects import XQUANTITIES, DiffractionObject

RADIUS_MM = 1
N_POINTS_ON_DIAMETER = 300
TTH_GRID = np.arange(1, 180.1, 0.1)
# Round down the last element if it's slightly above 180.00
# due to floating point precision
TTH_GRID[-1] = 180.00
CVE_METHODS = ["brute_force", "polynomial_interpolation"]

# Pre-computed datasets for polynomial interpolation (fast calculation)
MUD_LIST = np.array([0.5, 1, 2, 3, 4, 5, 6, 7])
CWD = Path(__file__).parent.resolve()
MULS = np.loadtxt(CWD / "data" / "inverse_cve.xy")
COEFFICIENT_LIST = np.array(
    pd.read_csv(CWD / "data" / "coefficient_list.csv", header=None)
)
INTERPOLATION_FUNCTIONS = [
    interp1d(MUD_LIST, coeffs, kind="quadratic") for coeffs in COEFFICIENT_LIST
]


class Gridded_circle:
    def __init__(
        self, radius=1, n_points_on_diameter=N_POINTS_ON_DIAMETER, mu=None
    ):
        self.radius = radius
        self.npoints = n_points_on_diameter
        self.mu = mu
        self.distances = []
        self.muls = []
        self._get_grid_points()

    def _get_grid_points(self):
        """Given a radius and a grid size, return a grid of points to uniformly
        sample that circle."""
        xs = np.linspace(-self.radius, self.radius, self.npoints)
        ys = np.linspace(-self.radius, self.radius, self.npoints)
        self.grid = {
            (x, y) for x in xs for y in ys if x**2 + y**2 <= self.radius**2
        }
        self.total_points_in_grid = len(self.grid)

    def _get_entry_exit_coordinates(self, coordinate, angle):
        """Get the coordinates where the beam enters and leaves the circle for
        a given angle and grid point.

        It is calculated in the following way:
        For the entry coordinate,
        the y-component will be the y of the grid point
        and the x-component will be minus
        the value of x on the circle at the height of this y.

        For the exit coordinate:
        Find the line y = ax + b that passes through grid_point at angle.
        The circle is x^2 + y^2 = r^2.
        The exit point is where these are simultaneous equations
        x^2 + y^2 = r^2 & y = ax + b
        x^2 + (ax+b)^2 = r^2
        => x^2 + a^2x^2 + 2abx + b^2 - r^2 = 0
        => (1+a^2) x^2 + 2abx + (b^2 - r^2) = 0
        to find x_exit we find the roots of these equations
        and pick the root that is above y-grid
        then we get y_exit from y_exit = a*x_exit + b.

        Parameters
        ----------
        coordinate : tuple of floats
            The coordinates of the grid point.
        angle : float
            The angle in degrees.

        Returns
        -------
        (entry_point, exit_point): tuple of floats
            (1) The coordinate of the entry point and
            (2) of the exit point of a beam entering horizontally
            impinging on a coordinate point that lies in the circle
            and then exiting at some angle, angle.
        """
        epsilon = 1e-7  # precision close to 90
        angle = math.radians(angle)
        xgrid = coordinate[0]
        ygrid = coordinate[1]
        entry_point = (-math.sqrt(self.radius**2 - ygrid**2), ygrid)
        if not math.isclose(angle, math.pi / 2, abs_tol=epsilon):
            b = ygrid - xgrid * math.tan(angle)
            a = math.tan(angle)
            xexit_root1, xexit_root2 = np.roots(
                (1 + a**2, 2 * a * b, b**2 - self.radius**2)
            )
            yexit_root1 = a * xexit_root1 + b
            yexit_root2 = a * xexit_root2 + b
            if yexit_root2 >= yexit_root1:  # We pick the point above
                exit_point = (xexit_root2, yexit_root2)
            else:
                exit_point = (xexit_root1, yexit_root1)
        else:
            exit_point = (xgrid, math.sqrt(self.radius**2 - xgrid**2))
        return entry_point, exit_point

    def _get_path_length(self, grid_point, angle):
        """Return the path length of a horizontal line entering the circle at
        the same height to the grid point then exiting at angle.

        Parameters
        ----------
        grid_point : double of floats
            The coordinate inside the circle.
        angle : float
            The angle of the output beam in degrees.

        Returns
        -------
        (total distance, primary distance, secondary distance): tuple of floats
            The tuple containing three floats,
            which are the total distance, entry distance and exit distance.
        """
        # move angle a tad above zero if it is zero
        # to avoid it having the wrong sign due to some rounding error
        angle_delta = 0.000001
        if angle == float(0):
            angle = angle + angle_delta
        entry, exit = self._get_entry_exit_coordinates(grid_point, angle)
        primary_distance = math.dist(grid_point, entry)
        secondary_distance = math.dist(grid_point, exit)
        total_distance = primary_distance + secondary_distance
        return total_distance, primary_distance, secondary_distance

    def set_distances_at_angle(self, angle):
        """Given an angle, set the distances from the grid points to the entry
        and exit coordinates.

        Parameters
        ----------
        angle : float
            The angle of the output beam in degrees.
        """
        self.primary_distances = []
        self.secondary_distances = []
        self.distances = []
        for coord in self.grid:
            distance, primary, secondary = self._get_path_length(coord, angle)
            self.distances.append(distance)
            self.primary_distances.append(primary)
            self.secondary_distances.append(secondary)

    def set_muls_at_angle(self, angle):
        """Compute muls = exp(-mu*distance) for a given angle.

        Parameters
        ----------
        angle : float
            The angle of the output beam in degrees.
        """
        mu = self.mu
        self.muls = []
        if len(self.distances) == 0:
            self.set_distances_at_angle(angle)
        for distance in self.distances:
            self.muls.append(np.exp(-mu * distance))


def _cve_brute_force(input_pattern, mud):
    """Compute cve for the given mud on a global grid using the brute-force
    method.

    Assume mu=mud/2, given that the same mu*D yields the same cve and
    D/2=1.
    """
    mu_sample_invmm = mud / 2
    abs_correction = Gridded_circle(
        n_points_on_diameter=N_POINTS_ON_DIAMETER, mu=mu_sample_invmm
    )
    distances, muls = [], []
    for angle in TTH_GRID:
        abs_correction.set_distances_at_angle(angle)
        abs_correction.set_muls_at_angle(angle)
        distances.append(sum(abs_correction.distances))
        muls.append(sum(abs_correction.muls))
    distances = np.array(distances) / abs_correction.total_points_in_grid
    muls = np.array(muls) / abs_correction.total_points_in_grid
    cve = 1 / muls
    cve_do = DiffractionObject(
        xarray=TTH_GRID,
        yarray=cve,
        xtype="tth",
        wavelength=input_pattern.wavelength,
        scat_quantity="cve",
        name=f"absorption correction, cve, for {input_pattern.name}",
        metadata=input_pattern.metadata,
    )
    return cve_do


def _cve_polynomial_interpolation(input_pattern, mud):
    """Compute cve using polynomial interpolation method, default to brute-
    force computation if mu*D is out of the range (0.5 to 7)."""
    if mud > 7 or mud < 0.5:
        warnings.warn(
            f"Input mu*D = {mud} is out of the acceptable range "
            f"({np.min(MUD_LIST)} to {np.max(MUD_LIST)}) "
            f"for polynomial interpolation. "
            f"Proceeding with brute-force computation. "
        )
        return _cve_brute_force(input_pattern, mud)

    coeffs = np.array([f(mud) for f in INTERPOLATION_FUNCTIONS])
    muls = np.polyval(coeffs, MULS)
    cve = 1 / muls
    cve_do = DiffractionObject(
        xarray=TTH_GRID,
        yarray=cve,
        xtype="tth",
        wavelength=input_pattern.wavelength,
        scat_quantity="cve",
        name=f"absorption correction, cve, for {input_pattern.name}",
        metadata=input_pattern.metadata,
    )
    return cve_do


def _cve_method(method):
    """Retrieve the cve computation function for the given method."""
    methods = {
        "brute_force": _cve_brute_force,
        "polynomial_interpolation": _cve_polynomial_interpolation,
    }
    if method not in CVE_METHODS:
        raise ValueError(
            f"Unknown method: {method}. "
            f"Allowed methods are {*CVE_METHODS, }."
        )
    return methods[method]


def compute_cve(
    input_pattern, mud, method="polynomial_interpolation", xtype="tth"
):
    f"""Compute and interpolate the cve
    for the given input diffraction data and mu*D
    using the selected method.

    Parameters
    ----------
    input_pattern : DiffractionObject
        The input diffraction object to which the cve will be applied.
    mud : float
        The mu*D value of the diffraction object,
        where D is the diameter of the circle.
    xtype : str
        The quantity on the independent variable axis,
        allowed values are {*XQUANTITIES, }.
    method : str
        The method used to calculate cve, must be one of {*CVE_METHODS, }.

    Returns
    -------
    cve_do: DiffractionObject
        The diffraction object that contains the cve to be applied.
    """
    cve_function = _cve_method(method)
    cve_do_on_global_grid = cve_function(input_pattern, mud)
    orig_grid = input_pattern.on_xtype(xtype)[0]
    global_xtype = cve_do_on_global_grid.on_xtype(xtype)[0]
    cve_on_global_xtype = cve_do_on_global_grid.on_xtype(xtype)[1]
    newcve = np.interp(orig_grid, global_xtype, cve_on_global_xtype)
    cve_do = DiffractionObject(
        xarray=orig_grid,
        yarray=newcve,
        xtype=xtype,
        wavelength=input_pattern.wavelength,
        scat_quantity="cve",
        name=f"absorption correction, cve, for {input_pattern.name}",
        metadata=input_pattern.metadata,
    )
    return cve_do


def apply_corr(input_pattern, absorption_correction):
    """Apply absorption correction to the given diffraction object with the
    correction diffraction object.

    Parameters
    ----------
    input_pattern : DiffractionObject
        The input diffraction object to which the cve will be applied.
    absorption_correction : DiffractionObject
        The diffraction object that contains the cve to be applied.

    Returns
    -------
    corrected_pattern: DiffractionObject
        The corrected diffraction object
        with the correction applied through multiplication.
    """
    corrected_pattern = input_pattern * absorption_correction
    return corrected_pattern
