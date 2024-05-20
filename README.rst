=================
diffpy.labpdfproc
=================

.. image:: https://github.com/diffpy/diffpy.labpdfproc/actions/workflows/testing.yml/badge.svg
   :target: https://github.com/diffpy/diffpy.labpdfproc/actions/workflows/testing.yml


.. image:: https://img.shields.io/pypi/v/diffpy.labpdfproc.svg
        :target: https://pypi.python.org/pypi/diffpy.labpdfproc


An app for preprocessing data from laboratory x-ray diffractometers before using PDFgetX3 to obtain PDFs

* Free software: 3-clause BSD license
* Documentation: (COMING SOON!) https://sbillinge.github.io/diffpy.labpdfproc.

Background
----------

PDFgetX3 has revolutionized how PDF methods can be applied to solve nanostructure problems.  However, the program was designed for use with Rapid Acquisition PDF (RAPDF) data from synchrotron sources.  A key approximation inherent in the use of PDFgetX3 for RAPDF data is that absorption effects are negligible.  This is typically not the case for laboratory x-ray diffractometers, where absorption effects can be significant.

This app is designed to preprocess data from laboratory x-ray diffractometers before using PDFgetX3 to obtain PDFs.  The app currently carries out an absorption correction assuming a parallel beam capillary geometry which is the most common geometry for lab PDF measurements.

The theory is described in the following paper:

An ad hoc Absorption Correction for Reliable
Pair-Distribution Functions from Low Energy x-ray Sources
Yucong Chen, Till Schertenleib, Andrew Yang, Pascal Schouwink,
Wendy L. Queen and Simon J. L. Billinge, in preparation.

The related experimental data acquisition protocols are described in the following paper:

Protocols for Obtaining Reliable PDFs from Laboratory
x-ray Sources Using PDFgetX3,
Till Schertenleib, Daniel Schmuckler, Yucong Chen, Geng Bang Jin,
Wendy L. Queen and Simon J. L. Billinge, in preparation.

Installation
------------

The package is available on conda-forge and on pypi.  Assuming you are using conda/mamba (we recommend using miniconda), create a virtual environment and install the package as follows:

.. code-block:: python

   mamba create -n labpdfproc python=3.12
   mamba activate labpdfproc
   cd path/to/diffpy.labpdfproc
   mamba install -c conda-forge diffpy.labpdfproc

The code may also be installed from pipy using pip.  This is not recommended as the package has not been tested on all platforms.

Usage
-----

Navigate to the directory that contains 1D diffraction patterns that you would like to process.  Activate the conda environment (`conda activate labpdfproc`) that contains the package and run the following command:

.. code-block:: python

   labpdfproc <muD> -i <path/to/inputfile.txt> --anode-type Mo


Here replace <muD> with the value of muD for your sample and  <path/to/inputfile.txt> with the path and filename of your input file.  For example, if the uncorrected data case isc alled  zro2_mo.xy and is in the current directory and it has a muD of 2.5 then the commands would be

.. code-block:: python

   labpdfproc 2.5 -i zro2_mo.xy --anode-type Mo

Please type
.. code-block:: python

   labpdfproc --help

for more information on the available options.


Getting Started
---------------

An example input file can be found in the docs/examples directory in the distribtuion (you should find it in your miniconda envs locateion).  The file is called zro2_mo.xy.

1. Copy this file to a new scratch directory
2. Navigate to that directory in a terminal
3. Activate the conda environment that contains the package
4. Run the command (see above)

An example output is also present in the example data and you can compare your output to this file.  The example was processed with a muD of 2.5, though for experimentation you can try processing data with different muD values.

Contributing
------------
We welcome contributors from the community.  Please consider posting issues, and taking issues and posting PRs.

To ensure code quality and to prevent accidental commits into the default branch, please set up the use of our pre-commit
hooks.

1. modify the permissions to executable on the bash script called `prevent_commit_to_main.sh` in this directory: `chmod +x prevent_commit_to_main.sh`
2. install pre-commit in your working environment `conda install pre-commit`
3. initialize pre-commit (one time only) `pre-commit install`

Thereafter your code will be linted by black and isort and checked against flake8 before you can commit.
If it fails by black or isort, just rerun and it should pass (black and isort will modify the files so should
pass after they are modified).  If the flake8 test fails please see the error messages and fix them manually before
trying to commit again
