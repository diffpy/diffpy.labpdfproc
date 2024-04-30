import sys

WAVELENGTHS = {"Mo": 0.71, "Ag": 0.59, "Cu": 1.54}


def set_wavelength(args):
    if args.wavelength and not isinstance(args.wavelength, float):
        sys.exit("Please enter the wavelength as a float value.")
    if not args.wavelength and args.anode_type and not (args.anode_type in WAVELENGTHS):
        sys.exit(
            "Please either specify a wavelength as a float value "
            "or specify anode_type as one of 'Mo', 'Ag', or 'Cu'."
        )

    wavelength = WAVELENGTHS["Mo"]
    if args.wavelength:
        wavelength = args.wavelength
    elif args.anode_type:
        wavelength = WAVELENGTHS[args.anode_type]
    return wavelength
