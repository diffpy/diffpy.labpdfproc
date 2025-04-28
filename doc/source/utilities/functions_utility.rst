.. _Functions Utility:

Functions Utility
=================

The ``diffpy.labpdfproc.functions`` module provides tools
for computing and applying absorption correction (cve) to 1D diffraction patterns.

- ``Gridded_circle``: This class supports absorption correction by
  creating a uniform grid of points within a circle for a given radius and linear absorption coefficient mu,
  and computing the path length and effective volume for each grid point at a given angle.

- ``compute_cve``: This function computes the absorption correction curve for a given muD value
  (the product of mu and capillary diameter D).
  For brute-force computation, it averages the effective volume across all grid points
  and computes the cve values as the reciprocal of this average.
  Alternatively, for fast calculation,
  it uses polynomial interpolation with pre-computed coefficients to estimate cve values for a given muD.
  Polynomial interpolation is available for muD values between 0.5-7.

- ``apply_corr``: This function applies the computed absorption correction to the input diffraction pattern
  by multiplying it with the corresponding cve, resulting in a corrected diffraction pattern.

For a more in-depth tutorial for how to use these tools, click :ref:`here <Functions Example>`.
