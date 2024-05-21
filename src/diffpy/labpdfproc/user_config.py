import json
from pathlib import Path

CONFIG_FILE = "labpdfprocconfig.json"


def prompt_user_info():
    username = input("Please enter your username (or press Enter to skip if you already entered before): ")
    email = input("Please enter your email (or press Enter to skip if you already entered before): ")
    return username, email


def read_conf_file(config_file=CONFIG_FILE):
    config_path = Path(config_file).resolve()
    if config_path.exists() and config_path.is_file():
        with open(config_file, "r") as f:
            config = json.load(f)
            return config.get("username"), config.get("email")
    return None, None


def write_conf_file(username, email, config_file=CONFIG_FILE):
    with open(config_file, "w") as f:
        json.dump({"username": username, "email": email}, f)
