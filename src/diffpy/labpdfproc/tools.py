WAVELENGTHS = {"Mo": 0.71, "Ag": 0.59, "Cu": 1.54}
known_sources = [key for key in WAVELENGTHS.keys()]


def set_wavelength(args):
    if args.wavelength and args.wavelength <= 0:
        raise ValueError("Please rerun the program specifying a positive float number.")
    if not args.wavelength and args.anode_type and args.anode_type not in WAVELENGTHS:
        raise ValueError(
            f"Invalid anode type {args.anode_type}. "
            f"Please rerun the program to either specify a wavelength as a positive float number "
            f"or specify anode_type as one of {known_sources}."
        )

    if args.wavelength:
        return args.wavelength
    elif args.anode_type:
        return WAVELENGTHS[args.anode_type]
    else:
        return WAVELENGTHS["Mo"]
