.. _Functions Example:

:tocdepth: -1

Functions Example
#################

This example will demonstrate how to use ``diffpy.labpdfproc.functions`` module independently
to apply absorption correction to your 1D diffraction data.

1. First, you will need to prepare and load your input diffraction data.
For example, if you want to load data from ``zro2_mo.xy`` in the ``example_data`` directory, you can write:

.. code-block:: python

    from diffpy.utils.parsers.loaddata import loadData
    from diffpy.utils.diffraction_objects import DiffractionObject

    filepath = "../example_data/zro2_mo.xy"
    xarray, yarray = loadData(filepath, unpack=True)
    input_pattern = DiffractionObject(
        xarray=xarray,
        yarray=yarray,
        xtype="tth",
        wavelength=0.7,
        scat_quantity="x-ray",
        name="input diffraction data",
        metadata={"beamline": "28ID-2"},
    )

For the full tutorial, please refer to https://www.diffpy.org/diffpy.utils/examples/diffraction_objects_example.html.

2. Assume you have created your ``input_pattern`` and specified mu*D value as ``muD`` (e.g., ``muD=2``).
You can now compute the absorption correction (cve) for the given mu*D using the ``compute_cve`` function,
apply it to your input pattern, and save the corrected file.

.. code-block:: python

    from diffpy.labpdfproc.functions import apply_corr, compute_cve
    absorption_correction = compute_cve(input_pattern, muD) # compute cve, default method is "polynomial_interpolation"
    corrected_pattern = apply_corr(input_pattern, absorption_correction) # apply cve correction
    corrected_data.dump("corrected pattern.chi", xtype="tth") # save the corrected pattern

If you want to use brute-force computation instead, you can replace the first line with:

.. code-block:: python

    absorption_correction = compute_cve(input_pattern, muD, method="brute_force")

3. Now, you can visualize the effect of the absorption correction
by plotting the original and corrected diffraction patterns.

.. code-block:: python

    import matplotlib.pyplot as plt
    plt.plot(input_pattern.xarray, input_pattern.yarray, label="Original Intensity")
    plt.plot(corrected_pattern.xarray, corrected_pattern.yarray, label="Corrected Intensity")
    plt.xlabel("tth (degrees)")
    plt.ylabel("Intensity")
    plt.legend()
    plt.title("Original vs. Corrected Intensity")
    plt.show()

4. You can modify the global parameters
``N_POINTS_ON_DIAMETER`` (the number of points on each diameter to sample the circle)
and ``TTH_GRID`` (the range of angles) when using the brute-force method.

To speed up computation, you can reduce the range of ``TTH_GRID``. You can also increase ``N_POINTS_ON_DIAMETER``
for better accuracy, but keep in mind that this will increase computation time.
For optimal results, we recommend setting it to an even number.

Currently, the interpolation coefficients were computed using ``N_POINTS_ON_DIAMETER=2000``,
which ensures good accuracy within the mu*D range of 0.5 to 6.
This value also provides flexibility if we decide to extend the interpolation range in the future.
