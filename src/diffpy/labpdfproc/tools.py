WAVELENGTHS = {"Mo": 0.71, "Ag": 0.59, "Cu": 1.54}


def set_wavelength(args):
    wavelength = WAVELENGTHS["Mo"]
    if args.wavelength:
        wavelength = args.wavelength
    elif args.anode_type:
        wavelength = WAVELENGTHS[args.anode_type]
    return wavelength
