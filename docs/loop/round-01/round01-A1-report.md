Files written:
- R1-2: `scripts/run.sh` (executable), `tests/test_run_sh.py`.
- R1-3: `.gitignore`, `.python-version`, `pyproject.toml`, `src/casefile/__init__.py`, `src/casefile/cli.py`, `tests/conftest.py`, `tests/test_cli.py`.

Both items remain uncommitted. Targeted staging failed: `fatal: Unable to create '/Users/davidskoranski/legal-harness/.git/index.lock': Operation not permitted`.
R1-3 CHECKs and SEEDs were not attempted. Interpreter setup, sync, and `uv.lock` remain for the orchestrator.

| Claim | Verified by, verbatim output | Control |
|---|---|---|
| Overflow exits 97, relays CAP bytes | CHECK 1 with caller `pipefail`: `PASS exit=97 bytes=52428800` | Cap SEED: `FAIL exit=0 bytes=52428800`, exit 1. `cmp: identical after cap seed`. Restored: `PASS exit=97 bytes=52428800` |
| Child exit 3 survives | CHECK 2: `PASS` | No mutation |
| Exact CAP exits 0 | CHECK 3: `PASS` | No mutation |
| Capture failure exits 98 | CHECK 4: `PASS` | Second SEED survived: `PASS`; `mktemp seed CHECK exit=0`. `cmp: identical after mktemp seed`. Restored: `PASS` |
| Stderr overflow is capped | `PASS stderr exit=97 bytes=52428800` | No separate mutation |
| Signal status survives | `PASS signal exit=137` | No mutation |

Verbatim capture diagnostics, final green CHECK followed by second SEED:
```text
mktemp: mkdtemp failed on /nonexistent/dir/casefile-run.ReUeK6: No such file or directory
run.sh: cannot create capture dir under /nonexistent/dir; exit 98
mktemp: mkdtemp failed on /nonexistent/dir/casefile-run.SSl6Yb: No such file or directory
tee: /out: Operation not permitted
scripts/run.sh: line 11: /out: No such file or directory
run.sh: capture file unreadable (stages 0 0 1 0); exit 98
```

Brief discrepancies:
- [Lines 631-633](.workflow/scratch/round01-build-brief.md:631): CHECK 1 without caller `pipefail` printed `FAIL exit=0 bytes=52428800`. Added caller `pipefail` for verification.
- [Line 642](.workflow/scratch/round01-build-brief.md:642): second SEED prints `PASS`, because the later unreadable-capture guard still returns 98.
- [D-5 line 262](.workflow/scratch/round01-build-brief.md:262) requires `config.load`, while [line 661](.workflow/scratch/round01-build-brief.md:661) requires standalone R1-3. Fixture validates TOML paths directly until R1-4 supplies `config.py`, then uses `config.load`.

Catalog IDs checked: #26, #34, #41, #52, #64, #91, #111.