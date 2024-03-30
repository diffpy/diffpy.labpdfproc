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

