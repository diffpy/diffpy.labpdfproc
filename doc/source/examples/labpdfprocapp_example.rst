.. _labpdfprocapp Example:

:tocdepth: -1

labpdfprocapp Example
#####################

This example provides a quick-start tutorial for using ``diffpy.labpdfproc``.
It will demonstrate how to apply absorption correction to your 1D diffraction data
using either the command-line (CLI) or graphical user interface (GUI).
For more details, run ``labpdfproc --help``.

1. In order to use this app,
you will need: (1) your input diffraction data file(s), and (2) information required to compute the mu*D value.
To launch the GUI, use either ``labpdfproc`` or ``labpdfproc --gui``.
Note that the GUI currently does not support Python 3.13.

2. Here we provide a basic example first.
Assume you have an uncorrected data called zro2_mo.xy in the current directory with a muD of 2.5 in two-theta.
Then the minimum command would be:

.. code-block:: python

    labpdfproc zro2_mo.xy --mud 2.5

3. You must provide at least one file path.
In the GUI, the file browser supports selecting multiple files, but not entire folders.
To include directories in GUI mode, you can:
(1) create a text file named ``file_list.txt`` listing the desired paths and load it,
(2) select all files in a folder manually,
(3) manually enter file paths separated by semicolons.

4. You can specify the wavelength in different ways:

.. code-block:: python

    # manually enter wavelength
    labpdfproc zro2_mo.xy --mud 2 -w 0.71303
    # use a known anode_type
    labpdfproc zro2_mo.xy --mud 2 -a Mo

5. To specify the output directory where the corrected data should be saved:

.. code-block:: python

    labpdfproc zro2_mo.xy --mud 2 -w 0.71303 -o "output_dir"

This will save the processed data into the folder ``output_dir``.

6. Additional options:
- ``xtype``: choose the x-axis variable for your diffraction data.
- You can also choose to output the cve file as well (via ``-o`` in CLI or checkbox in GUI).
- Use the overwrite option carefully - it will replace existing files.
- You are encouraged to input user information to help save progress and support reproducibility.

.. code-block:: python

    labpdfproc zro2_mo.xy --mud 2 -n Joe -e Joe@email.com --orcid 0000-0000-0000-0000


You can also enter this information during input prompts or store it in a diffpy configuration file.
For a full tutorial, refer to the documentation on ``diffpy.utils``.
