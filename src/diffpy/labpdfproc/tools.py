def load_key_value_pair(s):
    items = s.split("=")
    key = items[0].strip()
    if len(items) > 1:
        value = "=".join(items[1:])
    return (key, value)


def load_user_metadata(args):
    if args.user_metadata:
        for item in args.user_metadata:
            if "=" not in item:
                raise ValueError("please provide key-value pairs in the format key=value.")
            key, value = load_key_value_pair(item)
            setattr(args, key, value)
    delattr(args, "user_metadata")
    return args


# Notes, can ignore
# ideal inputs: "key1=value1" "key2=value2"
# (different pairs are separated by white spaces, key and value are separated by =)

# question 1: white spaces in key, value, both?
# if value contains whitespace, you can specify key="value value" or "key=value value"
# if key contains whitespace, for example, you have "key key=value",
# then you can access like getattr(args, 'key key'), but we dont recommend this

# question 2: more than one =?
# if i have key is hello, value is hello=world, then i can have hello=hello=world to process okay
# if i have = in key then it's still processing as value => would this be an issue?
