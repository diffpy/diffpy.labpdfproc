import json
import os
from pathlib import Path

CONFIG_FILE = "labpdfprocconfig.json"


def find_conf_file():
    # Return config file path if such a file exists
    if os.path.exists(CONFIG_FILE):
        return Path(CONFIG_FILE).resolve()
    return None


def read_conf_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def write_conf_file(file_path, username, useremail):
    config = {"username": username, "useremail": useremail}
    with open(file_path, "w") as f:
        json.dump(config, f)


def prompt_user_info():
    username = input("Please enter your username (or press Enter to skip): ")
    useremail = input("Please enter your email (or press Enter to skip): ")
    return username, useremail


def user_info_conf(args):
    username, useremail = prompt_user_info()
    write_conf_file(CONFIG_FILE, username, useremail)
    setattr(args, "username", username)
    setattr(args, "useremail", useremail)
    return args
