# Round 1 re-verification (verifier 2)

**Verdict: FAIL.** R1-4 and R1-13 refused again on new residues (B1b, B3); V1 not ticked.

Fresh Opus 5.5 session, no building or earlier verifying context. Branch `loop/round-01`, tip `c997bc1`.
Blind: ticks were decided before opening `round01-verify.md` and `round01-fix3-report.md`. Every probe
used invented paths and text. Scratch files lived in the session scratchpad (`$SCRATCH` below).

## Measured numbers

| Number | Probe |
|---|---|
| `184 passed in 10.40s` | `scripts/run.sh pytest -q` (sockets on 127.0.0.1 allowed) |
| gate prints `0`, exit `0`; privacy `offenders=0 scanned=218`, prose `dashes=0 files=59`, playbook `pb-00be6eb62752` | `scripts/run.sh python -m casefile.gate` |
| `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`; `stage-control ... expected={'ocr'} test_jobs=1`; `2 passed` | `scripts/run.sh pytest -q -s tests/test_stage1_exit.py` |
| doctor eight lines, `doctor failed=1 of 8`, exit `1` | `CASEFILE_CONFIG=$SCRATCH/doc/config.toml scripts/run.sh casefile doctor` against `python -m fakemodel` on 127.0.0.1:18434 |
| cap: `52428800` bytes, exit `97`, `secs=0` | `scripts/run.sh bash -c 'head -c 52428801 /dev/zero; sleep 30' \| wc -c` with pipefail; same with `(sleep 30; echo late) &` before the overflow |
| no pipefail `0`, pipefail `97` | R1-13 (a), same overflow pipeline |
| exact cap `0`; no args `96`; child `3`; child SIGTERM `143` | `scripts/run.sh bash -c 'head -c 52428800 ...'`; `scripts/run.sh`; `bash -c 'exit 3'`; `bash -c 'kill -TERM $$'` |
| missing command `127`; non-executable file `126`; directory `126` | `scripts/run.sh invented-no-such-cmd`; mode 644 script; a folder |
| capture dir `98` (mktemp guard); capture open `98`; empty or non-dir arg `98` | `TMPDIR=/nonexistent/dir scripts/run.sh true`; `run_capture.py 100 <chmod 555 dir> true`; `""` and a regular file |
| capture write failure `98` at 200000 bytes, but `0` at 4096 and 65536 bytes | `(ulimit -f 1; python3 scripts/run_capture.py 52428800 <dir> bash -c 'head -c N /dev/zero') \| wc -c` |
| background grandchild: exit `3` after `secs=30` | `scripts/run.sh bash -c 'sleep 30 & exit 3'` |

Doctor lines against R1-9 and R1-11: `config PASS`, `folders PASS writable=3 of 3`, `playbook PASS
version=pb-00be6eb62752`, `runlog_schema PASS schema=1 triggers=15 (counted)`, `ollama_loopback PASS
addr=127.0.0.1:18434`, `context PASS context_length=65536`, `runlog_job PASS test_jobs=+1` (again `+1`
on a second run), `ocr FAIL OCR not verified: tools unavailable (...) | do: install tesseract and
ocrmypdf; expected until stage 3`. Every check has PASS or FAIL with a reason, none skipped, exit 1
carries the single expected FAIL. R1-9 and R1-11 hold.

## R1-4 matters guard probes (D13, Q17)

Exit `2` with `must be outside the checkout`: `/Users/davidskoranski/LEGAL-HARNESS/invented-matters`,
`Legal-Harness/invented-matters`, `LEGAL-HARNESS` itself, `LEGAL-harness/SRC/new/deeper`,
`legal-harness/tests/../INVENTED/x`, `legal-harness/../legal-harness/x`, `~/legal-harness/invented`,
`/System/Volumes/Data/Users/davidskoranski/{legal-harness,LEGAL-HARNESS}/invented`, `$SCRATCH/alias`
and `$SCRATCH/alias/invented` (symlink to the checkout), `$SCRATCH/aliasU/invented` (symlink to
`LEGAL-HARNESS`), `$SCRATCH/aliasLowSrc/new` (symlink to `legal-harness/src`).
Exit `2` other reasons: `invented-matters` and `./invented-matters` (`must be an absolute path`), `""`
(`must be non-empty`), unknown key, unknown table, `num_ctx = "65536"`, `num_ctx = 32768`, host
`localhost`, `0.0.0.0`, `https`, `/v1` path, no matters, matters int, missing file, matters under a
`chmod 000` folder (`cannot verify ... Permission denied`).
Exit `0` (fail open): see B1b.

## Seeds

All restored with `cmp` (0) and `git diff --quiet`; full suite after restore `184 passed`, gate `0`.
Test set per seed: `tests/test_config.py tests/test_run_sh.py tests/test_rules.py tests/test_cli.py`
unless noted.

| Seed | Line | Mutation | Result |
|---|---|---|---|
| C1 | config.py:130 | identity `ancestor.exists() and samefile` -> `False and ...` | RED `4 failed, 77 passed` (case and symlink tests) |
| C2 | config.py:131 | ancestors `(matters, *matters.parents)` -> `(matters,)` | RED `2 failed, 79 passed` (nested variants) |
| C3 | config.py:134 | OSError `raise ConfigError(...)` -> `inside = False` | GREEN `81 passed`: finding (B1b) |
| C4 | config.py:129 | `inside = matters.resolve().is_relative_to(...) or any(` -> `False and any(` | RED `5 failed, 76 passed` |
| R1 | run_capture.py:32 | `return 127` -> `return 126` | RED `1 failed` (`test_missing_command_relays_127`) |
| R2 | run_capture.py:35 | `return 126` -> `return 1` | RED `1 failed` (`test_nonexecutable_command_relays_126`) |
| R3 | run_capture.py:30 | `except FileNotFoundError` -> `except IsADirectoryError` | RED `1 failed` (127 test) |
| R4 | run_capture.py:35 | `return 126` -> `return 127` | RED `1 failed` (126 test) |
| R5 | run_capture.py:17 | drop `or not Path(sys.argv[2]).is_dir()` | RED `2 failed` (`nonexistent`, `file`) |
| R6 | run_capture.py:40-41 | write `except OSError: return capture_failed(exc)` -> `pass` | GREEN `81 passed`: finding (B3) |
| R7 | run.sh:20 | toolchain inside `SystemExit(98)` -> `SystemExit(0)` | RED `3 failed` (literal, case, symlink) |
| R8 | run.sh:14 | toolchain ancestors -> `(toolchain,)` | RED `1 failed` (case) |
| P1 | rules.toml:8 | `[\s-]+` -> `\s+` | RED `4 failed` (hyphenated labels) |
| B | run_capture.py:13 | `return 98` -> `return 0` (tests/test_run_sh.py) | RED `5 failed, 13 passed` |
| M | run.sh:29 | drop the mktemp `\|\| {...}` guard (tests/test_run_sh.py) | RED `1 failed` (`test_run_sh[capture-failure]`, falls to the is_dir guard, told apart by message) |
| F | config.py:69 | missing-file branch removed (test_config, test_cli) | RED `3 failed, 22 passed` |
| D | runlog.py:92 | drop `AND runs.card='doctor.warmup'` (runlog, doctor, stage1) | RED `1 failed` (`assert 2 == 1`) |

Count: 17 code seeds, 15 RED, 2 GREEN (C3, R6). Seeds C1 to C4, R1 to R8 and P1 sit on lines f2023ae
added or changed; R1 to R4 cover the 126 and 127 branches; C1 to C3 cover the identity check.

## Findings

**B1b (blocking, R1-4, D13/Q17).** `src/casefile/config.py:129-131`. The ancestor walk runs over the
unresolved path, and the resolved path is compared by spelling. A symlink outside the checkout that
points at a case-swapped SUBDIRECTORY of the checkout passes:
`$SCRATCH/aliasFix -> /Users/davidskoranski/LEGAL-HARNESS/tests/fixtures`, `matters =
"$SCRATCH/aliasFix/invented-matter"` -> `casefile config show` exit `0`, `paths.matters =
"/Users/davidskoranski/LEGAL-HARNESS/tests/fixtures/invented-matter" (source=file)`. Also
`$SCRATCH/aliasSrc -> /Users/davidskoranski/Legal-Harness/src` exit `0`. Expected exit `2`. Fix: walk
the existing ancestors of `matters.resolve()` as well (samefile each against the checkout); add a test
with that symlink, with and without a nonexistent tail. Seed C3 also stays green: add a test for the
`cannot verify` branch (matters under a `chmod 000` folder exits 2). The run.sh toolchain guard
(`scripts/run.sh:12-15`) has the same shape and the same hole: `CASEFILE_TOOLCHAIN=$SCRATCH/aliasSrc
scripts/run.sh true` exit `0` (toolchain resolves inside `src/`), while `aliasLowSrc` and a
case-swapped literal give `98`. Fix both together.

**B3 (blocking, R1-13 (b), D12 98, same class as B2).** `scripts/run_capture.py:38-41`. The capture
write guard has no test (seed R6 `return capture_failed(exc)` -> `pass` stays `81 passed`) though it is
live: `ulimit -f 1` with 200000 bytes -> `[Errno 27] File too large; exit 98`. And a short write is
ignored: `capture.write(chunk)` return value is unchecked, so 4096 or 65536 bytes under `ulimit -f 1`
exit `0` with a truncated capture. Expected `98`. Fix: treat `write(...) != len(chunk)` as a capture
failure; add a test that runs `run_capture.py` with `RLIMIT_FSIZE` lowered (preexec) and asserts `98`
for both the short write and the EFBIG write.

Non-blocking:
- N1. `scripts/run.sh:18-24` refuses an inside toolchain with exit `98`, and a here-document failure
  (`ulimit -f 1`: `cannot create temp file for here document`) also exits `98`. D12 reserves 98 for
  capture failure; D12 names D23 but no code. Chair ruling: a distinct code, or amend D12.
- N2. A background grandchild that keeps the pipe open holds the wrapper until it exits
  (`sleep 30 & exit 3` -> `3` after 30 s). D12 is silent; note for the job runner.
- N3. A child that itself exits 96, 97, 98, 126 or 127 is indistinguishable from the wrapper (`bash -c
  'exit 98'` -> `98`). By D12's design; the stderr line tells them apart.
- N4. `Librarian.md` was modified by another process at 15:09 during this session (my first read showed
  15 lines; it now has 160 more). Not mine; left as found, so `git status -s` shows it too.

Still-ticked items: R1-2, R1-3, R1-9, R1-10, R1-11 re-measured above and hold; R1-5 to R1-8 hold by the
green suite, the stage 1 exit test, and seeds P1 and D red. Nothing unticked.

## Reconciliation

- First verifier B1 (case variant of the checkout loads) is fixed: exit 2 on every literal case swap
  and on symlinks to the checkout root. Fix3's report says "the symlink identity test forces a lexical
  miss": true for the root only; a symlink to a case-swapped subdirectory still misses (B1b). The
  Librarian pre-flight line now in the working tree asks for "every existing ancestor"; the code walks
  the ancestors of the wrong path.
- First verifier B2 (run_capture `return 98` -> `0` green) is fixed: seed B is `5 failed`, matching the
  chair's ledger number. Fix3 says "capture file open/write failures are 98": the open path is tested,
  the write path is not and misses short writes (B3).
- Fix3 rows S2, S6, S9, S10, N1, N2, N3 were not re-seeded by me except N1 (P1 red), N2 (R5 red) and
  N3 (R7, R8 red); all agree.
- Numbers: chair's `184 passed`, gate `0`, B1 `exit=2`, missing command `127` all reproduce. Fix3's own
  `5 failed, 179 passed` and gate `1` were socket binds denied in its sandbox; here sockets bind and the
  suite is `184 passed`. Privacy `scanned=218` against fix3's `217`: one file (the fix3 report) added.
