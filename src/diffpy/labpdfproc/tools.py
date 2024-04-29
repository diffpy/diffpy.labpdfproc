def load_wavelength(args_wavelength, args_anode_type, WAVELENGTHS):
    wavelength = WAVELENGTHS["Mo"]
    if args_wavelength:
        wavelength = args_wavelength
    elif args_anode_type:
        wavelength = WAVELENGTHS[args_anode_type]
    return wavelength
