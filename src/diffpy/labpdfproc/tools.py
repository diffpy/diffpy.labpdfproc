import sys


def load_user_metadata(args):
    if args.user_metadata:
        for item in args.user_metadata:
            if not item:
                sys.exit(
                    "please provide at least one key-value pair in the format key=value. "
                    "you can exclude -add if you don't want to provide additional info."
                )
            if "=" not in item:
                sys.exit("please provide key-value pairs in the format key=value.")
            key, value = item.split("=", 1)
            # if "=" in value:
            #    sys.exit("please use only one equals sign for key=value.")
            setattr(args, key, value)
    delattr(args, "user_metadata")
    return args
