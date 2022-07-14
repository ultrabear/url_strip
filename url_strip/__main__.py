"""
Module to use library as a cli script
"""

import sys
import argparse
import platform

from typing import List

from . import strip_url, Ok, Err, version_info


def main(args: List[str]) -> int:
    """
    Runs main cli user interface loop
    """

    parser = argparse.ArgumentParser(args[0])

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--strip", "-s", help="Strips the given url")
    group.add_argument(
        "--version", "-v", action="store_true", help="Prints the version info and exits"
        )

    if not sys.stdout.isatty():
        print("WARNING: url-strip does not have a stable cli interface", file=sys.stderr)

    parsed = parser.parse_args()

    if parsed.version:
        pyver = f"{platform.python_implementation()} {platform.python_version()}"
        print(f"url_strip {version_info.as_pep440_str()} @ {__file__}\n{pyver} @ {sys.executable}")
        return 0

    if Ok.is_instance(res := strip_url(parsed.strip)):
        print("Stripped url: ", Ok.unwrap(res).into_str())
        return 0

    print(f"Err: {Err.unwrap(res)}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
