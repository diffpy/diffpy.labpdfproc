import numpy as np
from scipy.optimize import dual_annealing
from scipy.signal import convolve

from diffpy.utils.parsers.loaddata import loadData


def _top_hat(x, slit_width):
    """
    create a top-hat function, return 1.0 for values within the specified slit width and 0 otherwise
    """
    return np.where((x >= -slit_width) & (x <= slit_width), 1.0, 0)


def _model_function(x, diameter, x0, I0, mud, slope):
    """
    compute the model function with the following steps:
    1. Recenter x to h by subtracting x0 (so that the circle is centered at 0 and it is easier to compute length l)
    2. Compute length l that is the effective length for computing intensity I = I0 * e^{-mu * l}:
    - For h within the diameter range, l is the chord length of the circle at position h
    - For h outside this range, l = 0
    3. Apply a linear adjustment to I0 by taking I0 as I0 - slope * x
    """
    min_radius = -diameter / 2
    max_radius = diameter / 2
    h = x - x0
    length = np.piecewise(
        h,
        [h < min_radius, (min_radius <= h) & (h <= max_radius), h > max_radius],
        [0, lambda h: 2 * np.sqrt((diameter / 2) ** 2 - h**2), 0],
    )
    return (I0 - slope * x) * np.exp(-mud / diameter * length)


def _extend_x_and_convolve(x, diameter, slit_width, x0, I0, mud, slope):
    """
    extend x values and I values for padding (so that we don't have tails in convolution), then perform convolution
    (note that the convolved I values are the same as modeled I values if slit width is close to 0)
    """
    n_points = len(x)
    x_left_pad = np.linspace(x.min() - n_points * (x[1] - x[0]), x.min(), n_points)
    x_right_pad = np.linspace(x.max(), x.max() + n_points * (x[1] - x[0]), n_points)
    x_extended = np.concatenate([x_left_pad, x, x_right_pad])
    I_extended = _model_function(x_extended, diameter, x0, I0, mud, slope)
    kernel = _top_hat(x_extended - x_extended.mean(), slit_width)
    I_convolved = I_extended  # this takes care of the case where slit width is close to 0
    if kernel.sum() != 0:
        kernel /= kernel.sum()
        I_convolved = convolve(I_extended, kernel, mode="same")
    padding_length = len(x_left_pad)
    return I_convolved[padding_length:-padding_length]


def _objective_function(params, x, observed_data):
    """
    compute the objective function for fitting a model to the observed/experimental data
    by minimizing the sum of squared residuals between the observed data and the convolved model data
    """
    diameter, slit_width, x0, I0, mud, slope = params
    convolved_model_data = _extend_x_and_convolve(x, diameter, slit_width, x0, I0, mud, slope)
    residuals = observed_data - convolved_model_data
    return np.sum(residuals**2)


def _compute_single_mud(x_data, I_data):
    """
    perform dual annealing optimization and extract the parameters
    """
    bounds = [
        (1e-5, x_data.max() - x_data.min()),  # diameter: [small positive value, upper bound]
        (0, (x_data.max() - x_data.min()) / 2),  # slit width: [0, upper bound]
        (x_data.min(), x_data.max()),  # x0: [min x, max x]
        (1e-5, I_data.max()),  # I0: [small positive value, max observed intensity]
        (1e-5, 20),  # muD: [small positive value, upper bound]
        (-10000, 10000),  # slope: [lower bound, upper bound]
    ]
    result = dual_annealing(_objective_function, bounds, args=(x_data, I_data))
    diameter, slit_width, x0, I0, mud, slope = result.x
    convolved_fitted_signal = _extend_x_and_convolve(x_data, diameter, slit_width, x0, I0, mud, slope)
    residuals = I_data - convolved_fitted_signal
    rmse = np.sqrt(np.mean(residuals**2))
    return mud, rmse


def compute_mud(filepath):
    """
    compute the best-fit mu*D value from a z-scan file

    Parameters
    ----------
    filepath str
        the path to the z-scan file

    Returns
    -------
    a float contains the best-fit mu*D value
    """
    x_data, I_data = loadData(filepath, unpack=True)
    best_mud, _ = min((_compute_single_mud(x_data, I_data) for _ in range(10)), key=lambda pair: pair[1])
    return best_mud
