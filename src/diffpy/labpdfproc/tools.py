WAVELENGTHS = {"Mo": 0.71, "Ag": 0.59, "Cu": 1.54}
known_sources = [key for key in WAVELENGTHS.keys()]


def set_wavelength(args):
    """
    Set the wavelength based on the given input arguments

    Parameters
    ----------
    args argparse.Namespace
        the arguments from the parser

    Returns
    -------
        float: the wavelength value

    we raise an ValueError if the input wavelength is non-positive
    or if the input anode_type is not one of the known sources

    """
    if args.wavelength is not None and args.wavelength <= 0:
        raise ValueError(
            "No valid wavelength. Please rerun specifying a known anode_type or a positive wavelength"
        )
    if not args.wavelength and args.anode_type and args.anode_type not in WAVELENGTHS:
        raise ValueError(
            f"Anode type not recognized. please rerun specifying an anode_type from {*known_sources, }"
        )

    if args.wavelength:
        return args.wavelength
    elif args.anode_type:
        return WAVELENGTHS[args.anode_type]
    else:
        return WAVELENGTHS["Mo"]
