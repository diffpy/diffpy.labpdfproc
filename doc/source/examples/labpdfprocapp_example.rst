.. _labpdfprocapp Example:

:tocdepth: -1

labpdfprocapp Example
#####################

This example provides a quick-start tutorial for using ``diffpy.labpdfproc``
to apply absorption correction to your 1D diffraction data using the command-line (CLI).
Check ``labpdfproc --help`` for more information.
A graphical user interface (GUI) is also available and is designed to be intuitive and easy to use.


1. To use this application, you will need:
(1) your input diffraction data file(s), and (2) information required to compute the muD value.
To launch the GUI, use ``labpdfproc`` or ``labpdfproc --gui``.
Note that the GUI is currently not supported on Python 3.13.


2. Here we first provide a basic CLI example.
Assume you have an uncorrected diffraction data file named ``zro2_mo.xy`` in the current directory
with a muD of 2.5 on the two-theta x-axis. Then the minimum command would be:

.. code-block:: python

    labpdfproc zro2_mo.xy --mud 2.5


3. You must provide at least one file path, and filepath(s) should immediately follow ``labpdfproc``.

To process multiple files at once in the CLI, separate each file path with a whitespace.
In general, avoid spaces in filenames, but if necessary, enclose them in quotes; otherwise, quotes are optional.
For example, the following is a valid and more complex CLI command:

.. code-block:: python

    labpdfproc "SiO2 uncorrected.xy" input_dir file_list.txt ./*.chi data* --mud 2.5

This command will process ``"SiO2 uncorrected.xy"``,
all files in the ``input_dir`` directory, all files listed in ``file_list.txt``,
all ``.chi`` files in the current directory, and all files matching the pattern ``data``,
using a muD value of 2.5.
Check ``labpdfproc --help`` to see all supported file types.

In the GUI, you can select multiple individual files via the file browser, but not entire directories.
To include directories, you can either:
(1) create a text file named ``file_list.txt`` containing the desired paths and load it,
(2) manually select all files in a folder, or
(3) enter paths manually separated by a colon with no spaces.

We will now continue using ``zro2_mo.xy`` as the example input throughout the rest of this tutorial.


4. The muD value is required for absorption correction, and you can specify it in one of the four ways:

.. code-block:: python

    # Option 1: Manual value
    labpdfproc zro2_mo.xy --mud 2.5
    # Option 2: From a z-scan file
    labpdfproc zro2_mo.xy -z zscan.xy
    # Option 3: Using sample mass density
    labpdfproc zro2_mo.xy -d ZrO2,17.45,1.2
    # Option 4: Using packing fraction
    labpdfproc zro2_mo.xy -p ZrO2,17.45,0.2

Note that you can only use one method at a time. The following examples are not allowed:

.. code-block:: python

    labpdfproc zro2_mo.xy --mud 2.5 -z zscan.xy
    labpdfproc zro2_mo.xy --mud 2.5 -d ZrO2,17.45,1.2

If the packing fraction option is not supported at the moment, you can approximate the sample mass density as:
``mass density = packing fraction * material density``, where the material density can be looked up manually.


5. You can specify the wavelength in two ways:

.. code-block:: python

    # Option 1: Manually enter wavelength
    labpdfproc zro2_mo.xy --mud 2.5 -w 0.71303
    # Option 2: Use a known anode type
    labpdfproc zro2_mo.xy --mud 2.5 -a Mo

Do not use both ``-w`` and ``-a`` at the same time. For example:

.. code-block:: python

    labpdfproc zro2_mo.xy --mud 2.5 -w 0.71303 -a Mo

is not valid. This is to avoid confusion when wavelength conflicts with anode type.
To avoid retyping, you can save your wavelength or anode type in a diffpy configuration file.
See full instructions at https://www.diffpy.org/diffpy.labpdfproc/examples/tools_example.html.


6. You are also encouraged to provide your information (name, email, and orcid) for reproducibility:

.. code-block:: python

    labpdfproc zro2_mo.xy --mud 2.5 -n Joe -e Joe@email.com --orcid 0000-0000-0000-0000


Alternatively, you can enter this information during the interactive prompts
or save it in your diffpy configuration file.
For more details, refer to https://www.diffpy.org/diffpy.utils/examples/tools_example.html.


7. You can further customize the diffraction correction process using the following options:

- Choose xtype: use ``-x`` to specify your input data's xtype, which will be used for the output.
- Select correction method: use ``-m`` to choose between "brute_force" or "polynomial_interpolation" (faster and preferred for muD 0.5-7).
- Specify output directory: use ``-o`` to save the corrected file(s) to a specific folder.
- Add custom metadata: use ``-u`` to provide key-value pair for information tracking (e.g., experimental details).
- Output the cve file: use ``-c`` to export the cve file along with the corrected data.
- Overwrite existing files: use ``-f`` to replace any previous corrected files with the same names.


8. To summarize, a full command might look like this:

.. code-block:: python

    labpdfproc zro2_mo.xy --mud 2.5 -w 0.71303 -n Joe -x q -m brute_force -o results -u "facility=NSLS II" beamline=28ID-2 -c -f

After running the command, check your output folder (in this case, ``results``)
for the corrected data file and cve file (if ``-c`` was used).
In this example, the corrected and cve files are called ``zro2_mo_corrected.chi`` and ``zro2_mo_cve.chi``.
The headers include all the arguments you provided
—such as diffraction settings, personal information, and metadata—making it easy to track your analysis.
