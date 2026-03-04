=============
Release notes
=============

.. current developments

0.3.0
=====

**Added:**

* Functionalities to estimate mu*D theoretically.
* Added published reference to ``README.rst``.
* Fast calculation supports values up to muD = 7
* Recookiecut with updated ``scikit-package`` to enable docs preview in PRs.
* Updated package standards to scikit-package 0.3.0.
* Added ``cookiecutter.json`` file for the ``package update`` command.
* Functionality to read wavelength and anode type directly from a diffpy configuration file.
* Utility and example documentation for ``tools`` module.
* Gooey support so that the app can be run with GUI
* Coverage report in each PR
* doi in Readme for papers.
* Support for independent variables other than two-theta.
* new subcommand ``applymud`` to run the original absorption correction process through CLI.
* Utility and example documentation for the main module.
* Added documentation for new CLI updates.
* Documentation for functions module.
* Spelling check via Codespell in pre-commit
* Python 3.13 support
* Functionality in `load_user_info` to enable user to enter an ORCID.

**Changed:**

* Default to brute-force computation when muD < 0.5 or > 7.
* Print a warning message instead of error, explicitly stating the input muD value
* Functions that use DiffractionObject` in `diffpy.utils` to follow the new API.
* Workflow for loading wavelength - raise an error when both wavelength and anode type are specified.
* Readme: muD now requires the ``--mud`` flag instead of a required argument.
* Made muD an optional argument and provided different options (manually entry / z-scan file path) for users to specify muD
* Increased the number of significant figures for wavelength and separated values for Ka1 and Ka2.
* hyphens / underscores format according to new scikit-package group standard.
* GitHub workflows for renamed test file.
* Return a ``ValueError`` if no wavelength is found on config file or if its not specified.
* Compartmentalize commands into the subcommands ``mud``, ``zscan``, and ``sample``. See documentation for more info.
* Changed ``doc`` to ``docs`` and ``CODE_OF_CONDUCT.rst`` to ``CODE-OF-CONDUCT.rst`` to comply with scikit-package standards.
* All function docstrings and tests to be more informative, incorporating new ORCID function and improving overall clarity.

**Fixed:**

* duplicated wavelength information in output files

**Removed:**

* Remove the import of extend_path from pkgutil in diffpy/__init__.py since we are not strictly following the Python namespace package convention.


0.2.0
=====

**Added:**

* Support for Python 3.13

**Removed:**

* Support for Python 3.10


0.1.3
=====

**Added:**

* generate package API doc
* redo cookiecutter to add issue templates and update readme


0.1.2
=====

**Added:**

* polynomial interpolation as the default method for cve computation.

**Fixed:**

* add PyPI packages under pip.txt



0.1.1
=====



0.1.1
=====



0.1.0
=====



Initial release of labPDFproc.  Please see README and documentation for details
