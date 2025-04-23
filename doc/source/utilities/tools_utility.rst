.. _Tools Utility:

Tools Utility
=============

The ``diffpy.labpdfproc.tools`` module provides functions to
manage user inputs, output directories, and diffraction information.
These functions work mostly with an ``argparse.Namespace`` object and help prepare data for diffraction processing.

- ``set_mud()``: This function determines the mu*D value used to compute absorption correction.
  Users can either provide mu*D directly, upload a z-scan file,
  or specify relevant chemical information to get a theoretical estimation.

- ``set_input_lists()``: This function parses all specified input files.
  Users can provide a list of files or directories via command-line arguments or GUI selection.
  You can also specify a ``file_list.txt`` that contains file paths (one per line),
  including paths to entire directories.
  Wildcard patterns are also supported for matching multiple files.

- ``set_output_directory()``: This function ensures that an output directory is defined and exists.
  If it is not explicitly provided, it defaults to the current working directory.
  This directory is used to store all cve and corrected output files.

- ``load_wavelength_from_config_file()`` and ``set_wavelength()``:
  These two functions work together to determine the wavelength for processing.
  ``load_wavelength_from_config_file()`` reads the default wavelength or anode type
  from user input or a diffpy configuration file, and ``set_wavelength()`` finalizes the wavelength value.
  It is recommended to store the wavelength information in a diffpy configuration file
  to avoid re-entering it every time.

- ``set_xtype()``: This function sets the x-axis variable for intensity interpolation (e.g. two-theta, q, d-spacing)
  and should be the same of the input diffraction data. The default is two-theta.

- ``load_user_metadata()``: This function loads experimental metadata
  or any user-defined key-value pairs to be recorded in the output files.

- ``load_user_info()``: This function loads user identification (name, email, orcid).
  Users can provide the information directly through arguments or store it in a diffpy configuration file.
  If no information is found, the function will prompt the user to create a configuration file,
  which is then saved for use in output metadata and future uses.

- ``load_package_info()``: This functions stores the package name and version for record-keeping.

- ``preprocessing_args()``: This is a convenience function that runs all standard setup steps listed above.
  It ensures the input/output paths, wavelength, mu*D value, metadata, and user and package info are
  fully initialized before applying the correction.

- ``load_metadata()``: This function transfers all collected information from the ``argparse.Namespace`` object
  into a diffraction object, allowing it to be saved in the output file header for tracking purpose.

For a more in-depth tutorial for how to use these tools, click :ref:`here <Tools Example>`.
