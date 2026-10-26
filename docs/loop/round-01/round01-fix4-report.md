# Round 1 fix cycle 4 (Q23, B1b and B3 only)
Checked CLAUDE.md, Librarian #R01-CX-1/#R01-V-B1/#R01-V-B2, spec D12/D13/D23.
All probes invented; every command through scripts/run.sh; no exemptions.

B1b matters: RED original aliases (existing target and nonexistent tail): 2 failed, 21 passed.
Fix src/casefile/config.py:129: resolve(strict=False), realpath, samefile on typed/resolved ancestors.
GREEN scripts/run.sh pytest -q tests/test_config.py: 23 passed.
Teeth: omit resolved ancestors: RED 2 failed; OSError raise -> inside=False: RED 1 failed.
OSError seed before new test: GREEN 20 passed; chmod-000 test asserts CLI exit 2/cannot verify, restores mode in finally.
Each seed restored byte-identically with scripts/run.sh cmp (0); post-restore GREEN 23 passed.
B1b toolchain: RED 5 failed, 1 passed (aliases accepted; old refusals exit 98).
Fix scripts/run.sh:3 and :16: cd -P/pwd -P, inode identity along typed/physical ancestors; refusal exit 95.
GREEN scripts/run.sh pytest -q tests/test_run_sh.py: 20 passed before B3 tests.
Teeth: omit physical ancestors: RED 2 failed; refusal exit 95 -> 98: RED 3 failed.
Each seed restored with cmp (0); post-restore GREEN 20 passed.
B3: RED original short capture and deterministic short writer: 2 failed, 1 passed.
Write-error seed before new test: GREEN 20 passed; new RLIMIT write-error test: RED 1 failed.
Fix scripts/run_capture.py:39: loop until each chunk is fully written; no progress or OSError returns 98.
GREEN scripts/run.sh pytest -q tests/test_run_sh.py: 23 passed.
Teeth: write-error return capture_failed(exc) -> pass: RED 2 failed; single write: RED 2 failed.
Each seed restored with cmp (0); post-restore combined config/wrapper GREEN 46 passed in 7.18s.
RLIMIT_FSIZE=1024 covers 4096/200000-byte writes; deterministic 7-byte writer verifies complete capture.

Files changed: src/casefile/config.py; scripts/run.sh; scripts/run_capture.py; tests/test_config.py; tests/test_run_sh.py; this report.
Pre-existing edits to .workflow/LEDGER.md, Librarian.md, docs/loop/agent-log.md left untouched.
Full pytest exit 1, last line: `5 failed, 187 passed in 8.49s`. All five are sandbox bind PermissionError; no workaround.
Gate exit 1, verdict lines verbatim (nested pytest last line: `5 failed, 187 passed in 8.03s`):
```
gate pytest FAIL exit=1
gate privacy PASS offenders=0 scanned=222
gate rules_selftest PASS misses=0 false_hits=0
gate playbook PASS invalid=0 unmarked=0 version=pb-00be6eb62752
gate prose PASS dashes=0 files=61
1
```
