from pathlib import Path


def set_output_directory(args):
    output_dir = Path(args.output_directory).resolve() if args.output_directory else Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
