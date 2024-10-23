|Icon| |title|_
===============

.. |title| replace:: diffpy.labpdfproc
.. _title: https://diffpy.github.io/diffpy.labpdfproc

.. |Icon| image:: https://avatars.githubusercontent.com/diffpy
        :target: https://diffpy.github.io/diffpy.labpdfproc
        :height: 100px

|PyPi| |Forge| |PythonVersion| |PR|

|CI| |Codecov| |Black| |Tracking|

.. |Black| image:: https://img.shields.io/badge/code_style-black-black
        :target: https://github.com/psf/black

.. |CI| image:: https://github.com/diffpy/diffpy.labpdfproc/actions/workflows/matrix-and-codecov-on-merge-to-main.yml/badge.svg
        :target: https://github.com/diffpy/diffpy.labpdfproc/actions/workflows/matrix-and-codecov-on-merge-to-main.yml

.. |Codecov| image:: https://codecov.io/gh/diffpy/diffpy.labpdfproc/branch/main/graph/badge.svg
        :target: https://codecov.io/gh/diffpy/diffpy.labpdfproc

.. |Forge| image:: https://img.shields.io/conda/vn/conda-forge/diffpy.labpdfproc
        :target: https://anaconda.org/conda-forge/diffpy.labpdfproc

.. |PR| image:: https://img.shields.io/badge/PR-Welcome-29ab47ff

.. |PyPi| image:: https://img.shields.io/pypi/v/diffpy.labpdfproc
        :target: https://pypi.org/project/diffpy.labpdfproc/

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/diffpy.labpdfproc
        :target: https://pypi.org/project/diffpy.labpdfproc/

.. |Tracking| image:: https://img.shields.io/badge/issue_tracking-github-blue
        :target: https://github.com/diffpy/diffpy.labpdfproc/issues

Tools for processing x-ray powder diffraction data from laboratory sources.

PDFgetX3 has revolutionized how PDF methods can be applied to solve nanostructure problems.
However, the program was designed for use with Rapid Acquisition PDF (RAPDF) data from synchrotron sources.
A key approximation inherent in the use of PDFgetX3 for RAPDF data is that absorption effects are negligible.
This is typically not the case for laboratory x-ray diffractometers, where absorption effects can be significant.

This app is designed to preprocess data from laboratory x-ray diffractometers before using PDFgetX3 to obtain PDFs.
The app currently carries out an absorption correction assuming a parallel beam capillary geometry
which is the most common geometry for lab PDF measurements.

The theory is described in the following paper:

An ad hoc Absorption Correction for Reliable
Pair-Distribution Functions from Low Energy x-ray Sources,
Yucong Chen, Till Schertenleib, Andrew Yang, Pascal Schouwink,
Wendy L. Queen and Simon J. L. Billinge, in preparation.

The related experimental data acquisition protocols are described in the following paper:

Protocols for Obtaining Reliable PDFs from Laboratory
x-ray Sources Using PDFgetX3,
Till Schertenleib, Daniel Schmuckler, Yucong Chen, Geng Bang Jin,
Wendy L. Queen and Simon J. L. Billinge, in preparation.

For more information about the diffpy.labpdfproc library, please consult our `online documentation <https://diffpy.github.io/diffpy.labpdfproc>`_.

Citation
--------

If you use diffpy.labpdfproc in a scientific publication, we would like you to cite this package as

        diffpy.labpdfproc Package, https://github.com/diffpy/diffpy.labpdfproc

Installation
------------

The preferred method is to use `Miniconda Python
<https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html>`_
and install from the "conda-forge" channel of Conda packages.

To add "conda-forge" to the conda channels, run the following in a terminal. ::

        conda config --add channels conda-forge

We want to install our packages in a suitable conda environment.
The following creates and activates a new environment named ``diffpy.labpdfproc_env`` ::

        conda create -n diffpy.labpdfproc_env diffpy.labpdfproc
        conda activate diffpy.labpdfproc_env

To confirm that the installation was successful, type ::

        python -c "import diffpy.labpdfproc; print(diffpy.labpdfproc.__version__)"

The output should print the latest version displayed on the badges above.

If the above does not work, you can use ``pip`` to download and install the latest release from
`Python Package Index <https://pypi.python.org>`_.
To install using ``pip`` into your ``diffpy.labpdfproc_env`` environment, type ::

        pip install diffpy.labpdfproc

If you prefer to install from sources, after installing the dependencies, obtain the source archive from
`GitHub <https://github.com/diffpy/diffpy.labpdfproc/>`_. Once installed, ``cd`` into your ``diffpy.labpdfproc`` directory
and run the following ::

        pip install .

Example
-------

Navigate to the directory that contains 1D diffraction patterns that you would like to process.
Activate the conda environment (`conda activate diffpy.labpdfproc_env`) that contains the package and run the following command ::

        labpdfproc <muD> <path/to/inputfile.txt>

Here replace <muD> with the value of muD for your sample
and <path/to/inputfile.txt> with the path and filename of your input file.
For example, if the uncorrected data case is called zro2_mo.xy and is in the current directory
and it has a muD of 2.5 then the command would be ::

        labpdfproc 2.5 zro2_mo.xy

Please type ::

        labpdfproc --help

for more information on the available options.

Getting Started
---------------

You may consult our `online documentation <https://diffpy.github.io/diffpy.labpdfproc>`_ for tutorials and API references.

Support and Contribute
----------------------

`Diffpy user group <https://groups.google.com/g/diffpy-users>`_ is the discussion forum for general questions and discussions about the use of diffpy.labpdfproc. Please join the diffpy.labpdfproc users community by joining the Google group. The diffpy.labpdfproc project welcomes your expertise and enthusiasm!

If you see a bug or want to request a feature, please `report it as an issue <https://github.com/diffpy/diffpy.labpdfproc/issues>`_ and/or `submit a fix as a PR <https://github.com/diffpy/diffpy.labpdfproc/pulls>`_. You can also post it to the `Diffpy user group <https://groups.google.com/g/diffpy-users>`_.

Feel free to fork the project and contribute. To install diffpy.labpdfproc
in a development mode, with its sources being directly used by Python
rather than copied to a package directory, use the following in the root
directory ::

        pip install -e .

To ensure code quality and to prevent accidental commits into the default branch, please set up the use of our pre-commit
hooks.

1. Install pre-commit in your working environment by running ``conda install pre-commit``.

2. Initialize pre-commit (one time only) ``pre-commit install``.

Thereafter your code will be linted by black and isort and checked against flake8 before you can commit.
If it fails by black or isort, just rerun and it should pass (black and isort will modify the files so should
pass after they are modified). If the flake8 test fails please see the error messages and fix them manually before
trying to commit again.

Improvements and fixes are always appreciated.

Before contributing, please read our `Code of Conduct <https://github.com/diffpy/diffpy.labpdfproc/blob/main/CODE_OF_CONDUCT.rst>`_.

Contact
-------

For more information on diffpy.labpdfproc please visit the project `web-page <https://diffpy.github.io/>`_ or email Prof. Simon Billinge at sb2896@columbia.edu.
