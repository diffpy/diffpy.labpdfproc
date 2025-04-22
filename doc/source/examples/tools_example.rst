.. _Tools Example:

:tocdepth: -1

Tools Example
#############

This example will demonstrate how to use ``diffpy.labpdfproc.tools`` module
to preprocess diffraction data using an ``argparse.Namespace`` called ``args``.
These functions help set up inputs, metadata, and parameters before applying absorption correction.

1. We begin by estimating the mu*D value used for absorption correction using ``set_mud(args)``.
You can do this in one of the following four ways:

.. code-block:: python

    from argparse import Namespace
    # Option 1: Manual value
    args = Namespace(mud=2)
    # Option 2: From a z-scan file
    args = Namespace(z_scan_file="zscan.xy")
    # Option 3: Using mass density
    args = Namespace(sample_composition="ZrO2", energy=1.745, density=1.2)
    # Option 4: Using packing fraction
    args = Namespace(sample_composition="ZrO2", energy=1.745, packing_fraction=0.3)
    # Set and view the computed mu*D value
    args = set_mud(args)
    print(args.mud)

Note that only one method should be used at a time. The following are invalid examples:

.. code-block:: python

    # Invalid example 1: manual mu*D and z-scan file both provided
    args = Namespace(mud=2, z_scan_file="zscan.xy")
    # Invalid example 2: missing required energy
    args = Namespace(sample_composition="ZrO2", density=1.2)
    # Invalid example 3: both mass density and packing fraction specified
    args = Namespace(sample_composition="ZrO2", energy=1.745, density=1.2, packing_fraction=0.3)

If the packing fraction option is not supported at the moment, you can approximate
``mass density = packing fraction * material density``, where the material density can be looked up manually.


2. Next, we load the input files for correction using ``set_input_lists(args)``:

.. code-block:: python

    args = Namespace(input="file1.xy file2.xy")
    args = set_input_lists(args)
    print(args.input_paths)

This function resolves the input filenames into full file paths.
For details on supported input formats, check ``labpdfproc --help``.


3. We now set the output directory where the cve and corrected files will be saved:

.. code-block:: python

    args = Namespace(output_directory="output") # creates "output/" directory if it doesn't exist
    args = set_output_directory(args)
    print(args.output_directory)

If a filename is provided instead of a directory, an error will be raised.
If no output directory is specified, it defaults to the current working directory.


4. We then set wavelength and xtype, both of which are necessary for absorption correction:

.. code-block:: python

    # Option 1: Specify wavelength directly
    args = Namespace(wavelength=0.7)
    # Option 2: Use a valid anode type
    args = Namespace(anode_type="Mo")
    args = set_wavelength(args)

Note that you should specify either a wavelength or an anode type, not both, to avoid conflicts.
If you provide an anode type, the corresponding wavelength will be retrieved from global parameters.
You may use ``labpdfproc --help`` to view a list of valid anode types.
If neither is given, it's only acceptable if the input diffraction data is already on a two-theta grid.
To simplify workflows and avoid re-entering it every time,
we recommend saving the wavelength or anode type to a diffpy config file. For example:

.. code-block:: python

    from pathlib import Path
    import json
    home_dir = Path.home()
    wavelength_data = {"wavelength": 0.3}
    with open(home_dir / "diffpyconfig.json", "w") as f:
        json.dump(wavelength_data, f)

To set the x-axis type (xtype) for your diffraction data:

.. code-block:: python

    args = Namespace(xtype="tth")
    args = set_xtype(args)

This sets the xtype to ``tth``. Other valid options including ``q`` and ``d`` spacing.


5. Finally, we load user metadata, user information, and package information into ``args``.
To load metadata, pass key-value pairs as a list:

.. code-block:: python

    args = Namespace(
        user_metadata=[
            "facility=NSLS II",
            "beamline=28ID-2",
    ])
    args = load_user_metadata(args)

This ensures all key-value pairs are parsed and added as attributes.

To load your user information (username, email, and orcid), you can manually add it through ``args``:

.. code-block:: python

    args = Namespace(username="Joe", email="joe@example.com", orcid="0000-0000-0000-0000")
    args = load_user_info(args)
    print(args.username, args.email, args.orcid)

Alternatively, this can be saved in a config file
(see https://www.diffpy.org/diffpy.utils/examples/tools_example.html).
If nothing is found, you will be prompted to create one.
Note that it is not recommended to store personal information on a public or shared computer.

Furthermore, the function ``load_package_info(args)`` is used to attach package name and version info for reproducibility.
This is typically run automatically but can be called explicitly:

.. code-block:: python

    args = load_package_info(args)
    print(args.package_info) # Output example: {"diffpy.labpdfproc": "0.0.1", "diffpy.utils": "3.0.0"}


6. We also provide a convenient function to run all steps above at once:

.. code-block:: python

    args = preprocessing_args(args)


7. The final step is converting your ``args`` to a metadata dictionary
so that it can be attached to the diffraction object's header during output writing.
Using the function ``load_metadata(args, filepath)``
requires both the ``argument.Namespace`` and the current input file path.
For more details about working with diffraction objects and how they are written to output files, see
https://www.diffpy.org/diffpy.utils/examples/diffraction_objects_example.html.
