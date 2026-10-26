"""Command line entry point for casefile."""

import argparse
from dataclasses import fields
import json
from pathlib import Path
import sys

from casefile import __version__
from casefile.config import ConfigError, load


def main() -> int:
    parser = argparse.ArgumentParser(prog="casefile")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("version", help="Print the installed version")
    config_parser = subcommands.add_parser("config", help="Inspect configuration")
    config_commands = config_parser.add_subparsers(dest="config_command", required=True)
    show = config_commands.add_parser("show", help="Print effective values and their sources")
    show.add_argument("--config", type=Path)
    args = parser.parse_args()
    if args.command == "version":
        print(f"casefile {__version__}")
    elif args.command == "config":
        try:
            config = load(args.config)
        except ConfigError as exc:
            print(f"ConfigError: {exc}", file=sys.stderr)
            return 2
        for table in ("paths", "model", "ocr"):
            for field in fields(getattr(config, table)):
                key = f"{table}.{field.name}"
                value = getattr(getattr(config, table), field.name)
                if isinstance(value, Path):
                    value = str(value)
                print(f"{key} = {json.dumps(value)} (source={config.sources[key]})")
    return 0
