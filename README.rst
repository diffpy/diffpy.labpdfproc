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

The package is available on conda-forge and on pypi.  Assuming you are using conda/mamba (we recommend using miniconda)

1. create a virtual environment, e.g.

.. code-block:: python

   mamba create -n labpdfproc python=3.12
   mamba activate labpdfproc
   cd path/to/diffpy.labpdfproc
   mamba install -c conda-forge diffpy.labpdfproc

The code may also be installed from pipy using pip.  This is not recommended as the package has not been tested on all platforms.
