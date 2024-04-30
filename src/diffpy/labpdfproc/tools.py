def load_additional_info(args):
    if args.additional_info:
        for item in args.additional_info:
            key, value = item.split("=")
            setattr(args, key, value)
    delattr(args, "additional_info")
    return args
