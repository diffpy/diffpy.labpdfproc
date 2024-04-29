def load_wavelength(args, WAVELENGTHS):
    wavelength = WAVELENGTHS["Mo"]
    if args.wavelength:
        wavelength = args.wavelength
    elif args.anode_type:
        wavelength = WAVELENGTHS[args.anode_type]
    return wavelength
