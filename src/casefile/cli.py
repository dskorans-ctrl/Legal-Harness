"""Command line entry point for casefile."""

import argparse
from dataclasses import fields
import json
from pathlib import Path
import sys

from casefile import __version__, bench, doctor, intake, memo_job, playbook, status
from casefile.config import ConfigError, load


def main() -> int:
    parser = argparse.ArgumentParser(prog="casefile")
    subcommands = parser.add_subparsers(dest="command", required=True)
    version = subcommands.add_parser("version", help="Print the installed version")
    version.add_argument("--config", type=Path)
    doctor_parser = subcommands.add_parser("doctor", help="Check local readiness")
    doctor_parser.add_argument("--config", type=Path)
    playbook_parser = subcommands.add_parser("playbook", help="Inspect the playbook")
    playbook_commands = playbook_parser.add_subparsers(dest="playbook_command", required=True)
    playbook_show = playbook_commands.add_parser("show")
    playbook_show.add_argument("--config", type=Path)
    config_parser = subcommands.add_parser("config", help="Inspect configuration")
    config_commands = config_parser.add_subparsers(dest="config_command", required=True)
    show = config_commands.add_parser("show", help="Print effective values and their sources")
    show.add_argument("--config", type=Path)
    bench_parser = subcommands.add_parser("bench", help="Score invented matters against their answer keys")
    bench_parser.add_argument("--matters", type=Path, required=True)
    bench_parser.add_argument("--candidate", type=Path)
    bench_parser.add_argument("--config", type=Path)
    intake_parser = subcommands.add_parser("intake", help="OCR a PDF into page records with page IDs")
    intake_parser.add_argument("--matter", required=True)
    intake_parser.add_argument("--binder", required=True)
    intake_parser.add_argument("file", type=Path)
    intake_parser.add_argument("--config", type=Path)
    for command in ("memo", "status"):
        command_parser = subcommands.add_parser(command)
        command_parser.add_argument("--matter", required=True)
        command_parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    if args.command == "version":
        print(f"casefile {__version__}")
    elif args.command == "doctor":
        return doctor.run(args.config)
    elif args.command == "playbook":
        try:
            book = playbook.load(load(args.config).paths.playbook)
        except (ConfigError, playbook.PlaybookError) as exc:
            print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
            return 2
        print(f"version={book.version} entries={len(book.entries)}")
        for entry in book.entries:
            print(f"{entry.id}: {entry.rule}")
    elif args.command == "intake":
        try:
            config = load(args.config)
        except ConfigError as exc:
            print(f"ConfigError: {exc}", file=sys.stderr)
            return 2
        return intake.intake(config, args.matter, args.binder, args.file,
                             out=sys.stdout, err=sys.stderr)
    elif args.command in ("memo", "status"):
        try:
            config = load(args.config)
        except ConfigError as exc:
            print(f"{args.command}: cannot run: {exc}", file=sys.stderr)
            return 2
        job = memo_job if args.command == "memo" else status
        return job.run(config, args.matter, out=sys.stdout, err=sys.stderr)
    elif args.command == "bench":
        return bench.main(args.matters, args.config, args.candidate)
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
