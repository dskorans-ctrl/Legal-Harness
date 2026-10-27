"""casefile bench: score invented matters against their answer keys (D25)."""

from pathlib import Path
import sqlite3
import sys

from casefile import benchkey, benchrun, benchscore, matter as matters, playbook, runlog
from casefile.benchcandidate import CandidateError, parse_text
from casefile.config import ConfigError, load


def one_line(exc) -> str:
    return " ".join(str(exc).splitlines())


def main(matters_dir, config_path=None, candidate_path=None, *, out=None, err=None,
         opener=None, runner=benchrun.run) -> int:
    out = sys.stdout if out is None else out
    err = sys.stderr if err is None else err

    # Load Config
    try:
        config = load(config_path)
    except ConfigError as exc:
        print(f"ConfigError: {one_line(exc)}", file=err)
        return 2

    # Load Playbook
    try:
        book = playbook.load(config.paths.playbook)
    except playbook.PlaybookError as exc:
        print(f"PlaybookError: {one_line(exc)}", file=err)
        return 2

    # Find Matter Roots
    try:
        roots = sorted(p for p in Path(matters_dir).iterdir() if (p / "matter.toml").is_file())
    except OSError as exc:
        print(f"bench: cannot read {matters_dir}: {one_line(exc)}", file=err)
        return 2

    # Check if roots exist
    if not roots:
        print(f"bench: no matters under {matters_dir}", file=err)
        return 2

    # Check candidate path constraints
    if candidate_path is not None and len(roots) != 1:
        print("bench: --candidate needs exactly one matter", file=err)
        return 2

    # Open Run Log
    log = None
    if candidate_path is None:
        log_path = config.paths.state / "runlog.sqlite"
        try:
            log = runlog.open_db(log_path)
        except (OSError, sqlite3.Error) as exc:
            print(f"bench: cannot open run log {log_path}: {one_line(exc)}", file=err)
            return 2

    # Main Loop
    imperfect = 0
    seen_numbers = {}
    try:
        for root in roots:
            # Load Matter and Key
            try:
                matter = matters.load(root)
                key = benchkey.load(root / "key.json", matter)
            except (matters.MatterError, benchkey.BenchKeyError) as exc:
                print(f"{type(exc).__name__}: {one_line(exc)}", file=err)
                return 2

            if matter.number in seen_numbers:
                print(f"bench: duplicate matter number {matter.number} in {seen_numbers[matter.number]} "
                      f"and {root}", file=err)
                return 2
            seen_numbers[matter.number] = root

            candidate = None
            pages_failed = 0
            model_tag = "candidate" if candidate_path is not None else config.model.name

            if candidate_path is not None:
                # Load candidate text
                try:
                    candidate = parse_text(Path(candidate_path).read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError, CandidateError) as exc:
                    print(f"CandidateError: {one_line(exc)}", file=err)
                    return 2
            else:
                # Run benchmark
                try:
                    result = runner(matter, config, log, book.version, opener)
                except sqlite3.Error as exc:
                    print(f"bench: run log: {one_line(exc)}", file=err)
                    return 2

                candidate = result.candidate
                pages_failed = result.pages_failed

                if result.failure:
                    print(f"bench {matter.number} failure {result.failure}", file=out)
                    if not result.reply_received:
                        print(f"bench: cannot run: no reply from the model server at "
                              f"{config.model.host}: {result.failure.removeprefix('bench.model: ')}", file=err)
                        return 2

            # Score
            s = benchscore.score(key, candidate, matter, book.rules, pages_failed)
            print(s.line(matter.number, model_tag), file=out)
            for detail in s.details():
                print(detail, file=out)
            imperfect += not s.perfect

    finally:
        if log is not None:
            log.close()

    # Final Result
    print(f"bench matters={len(roots)} imperfect={imperfect}", file=out)
    return 0 if imperfect == 0 else 1
