"""Command line entry point for casefile."""

import argparse

from casefile import __version__


def main() -> int:
    parser = argparse.ArgumentParser(prog="casefile")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("version", help="Print the installed version")
    args = parser.parse_args()
    if args.command == "version":
        print(f"casefile {__version__}")
    return 0
