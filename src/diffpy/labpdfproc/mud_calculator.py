import numpy as np
from scipy.optimize import dual_annealing
from scipy.signal import convolve

from diffpy.utils.parsers.loaddata import loadData


def _top_hat(z, half_slit_width):
    """
    Create a top-hat function, return 1.0 for values within the specified slit width and 0 otherwise
    """
    return np.where((z >= -half_slit_width) & (z <= half_slit_width), 1.0, 0.0)


def _model_function(z, diameter, z0, I0, mud, slope):
    """
    Compute the model function with the following steps:
    1. Recenter z to x by subtracting z0 (so that the circle is centered at 0 and it is easier to compute length l)
    2. Compute length l that is the effective length for computing intensity I = I0 * e^{-mu * l}:
    - For x within the diameter range, l is the chord length of the circle at position x
    - For x outside this range, l = 0
    3. Apply a linear adjustment to I0 by taking I0 as I0 - slope * z
    """
    min_radius = -diameter / 2
    max_radius = diameter / 2
    x = z - z0
    length = np.piecewise(
        x,
        [x < min_radius, (min_radius <= x) & (x <= max_radius), x > max_radius],
        [0, lambda x: 2 * np.sqrt((diameter / 2) ** 2 - x**2), 0],
    )
    return (I0 - slope * z) * np.exp(-mud / diameter * length)


def _extend_z_and_convolve(z, diameter, half_slit_width, z0, I0, mud, slope):
    """
    extend z values and I values for padding (so that we don't have tails in convolution), then perform convolution
    (note that the convolved I values are the same as modeled I values if slit width is close to 0)
    """
    n_points = len(z)
    z_left_pad = np.linspace(z.min() - n_points * (z[1] - z[0]), z.min(), n_points)
    z_right_pad = np.linspace(z.max(), z.max() + n_points * (z[1] - z[0]), n_points)
    z_extended = np.concatenate([z_left_pad, z, z_right_pad])
    I_extended = _model_function(z_extended, diameter, z0, I0, mud, slope)
    kernel = _top_hat(z_extended - z_extended.mean(), half_slit_width)
    I_convolved = I_extended  # this takes care of the case where slit width is close to 0
    if kernel.sum() != 0:
        kernel /= kernel.sum()
        I_convolved = convolve(I_extended, kernel, mode="same")
    padding_length = len(z_left_pad)
    return I_convolved[padding_length:-padding_length]


def _objective_function(params, z, observed_data):
    """
    Compute the objective function for fitting a model to the observed/experimental data
    by minimizing the sum of squared residuals between the observed data and the convolved model data
    """
    diameter, half_slit_width, z0, I0, mud, slope = params
    convolved_model_data = _extend_z_and_convolve(z, diameter, half_slit_width, z0, I0, mud, slope)
    residuals = observed_data - convolved_model_data
    return np.sum(residuals**2)


def _compute_single_mud(z_data, I_data):
    """
    Perform dual annealing optimization and extract the parameters
    """
    bounds = [
        (1e-5, z_data.max() - z_data.min()),  # diameter: [small positive value, upper bound]
        (0, (z_data.max() - z_data.min()) / 2),  # half slit width: [0, upper bound]
        (z_data.min(), z_data.max()),  # z0: [min z, max z]
        (1e-5, I_data.max()),  # I0: [small positive value, max observed intensity]
        (1e-5, 20),  # muD: [small positive value, upper bound]
        (-100000, 100000),  # slope: [lower bound, upper bound]
    ]
    result = dual_annealing(_objective_function, bounds, args=(z_data, I_data))
    diameter, half_slit_width, z0, I0, mud, slope = result.x
    convolved_fitted_signal = _extend_z_and_convolve(z_data, diameter, half_slit_width, z0, I0, mud, slope)
    residuals = I_data - convolved_fitted_signal
    rmse = np.sqrt(np.mean(residuals**2))
    return mud, rmse


def compute_mud(filepath):
    """Compute the best-fit mu*D value from a z-scan file, removing the sample holder effect.

    This function loads z-scan data and fits it to a model
    that convolves a top-hat function with I = I0 * e^{-mu * l}.
    The fitting procedure is run multiple times, and we return the best-fit parameters based on the lowest rmse.

    Parameters
    ----------
    filepath : str
        The path to the z-scan file.

    Returns
    -------
    mu*D : float
        The best-fit mu*D value.
    """
    z_data, I_data = loadData(filepath, unpack=True)
    best_mud, _ = min((_compute_single_mud(z_data, I_data) for _ in range(20)), key=lambda pair: pair[1])
    return best_mud
