# Round 1 re-brief: blind verifier (8c)

Verifier: fresh Opus 5.5, no build or prior verify context. Branch `loop/round-01`, tip `4db60e2`, 2026-10-26.
Probes invented, all under `/private/tmp/claude-501/v4r` (S), wrapper runs with `TMPDIR=$S/tx` so capture
folders could be counted. Reports and `.workflow/scratch/` opened only after every item was ticked.

## Verdict: PASS

R1-4, R1-13, R1-22, R1-23 ticked; every other ticked item still holds; R1-21 and R1-12 deferred; V1 ticked.
One seed stayed green (finding F1, non-blocking, tip behaves correctly).

## Numbers

- `scripts/run.sh pytest -q` -> `233 passed in 43.24s`; gate twice: rows pytest `exit=0`, privacy
  `offenders=0 scanned=247`, rules_selftest `misses=0 false_hits=0`, playbook `pb-00be6eb62752`, prose
  `dashes=0 files=74`, prints `0`, exit `0` (the build note's one-off `1` did not recur).
- `scripts/run.sh pytest -q -s tests/test_stage1_exit.py` -> `stage-control exit=1 verdicts=8 fails={'ocr'}
  expected={'ocr'} test_jobs=1`, `2 passed`.
- Driven doctor (stand-in on 127.0.0.1:51384, through run.sh, twice): eight lines, seven PASS and `ocr FAIL
  ... | do: install tesseract and ocrmypdf; expected until stage 3`, `doctor failed=1 of 8`, exit 1, `test_jobs=+1`
  each run; run log rows `ok|stop|21|2` x2; `delete from runs` -> `runlog is append-only`.
- Matters (config show, 26 probes) and toolchain (run.sh, 26 probes): every alias refused (2 / 95), loop and
  chmod 000 are cannot-verify, `..` at the right depth (5 levels) refused in both `/private/tmp` and `/tmp`
  spellings, one `..` short is genuinely outside (exit 0), nothing created in the checkout.
- D12: 96, 95 (inside and cannot-verify), 98 (mktemp, capture write 200000 and 4096 bytes), 126 (file, dir),
  127, 97 (`52428800` bytes, 0.45 s, grandchild dead), held pipe 2.09 s keeps `3` and `137`, escaped setsid
  holder 2.16 s keeps `4`, STOP then CONT keeps `5`, HUP 129, TERM 143, INT 130 (child dead, capture folders
  1 during, 0 after), child 3, 0, 143.

## Seeds (mine, lines nobody listed; cmp 0 after each)

| Line | Mutation | Result |
|---|---|---|
| pathguard.py:54 | judge only the first path | venv-child probe exits 0; `5 failed, 38 passed` |
| pathguard.py:55 | drop the newline join in the verdict line | GREEN `233 passed` (F1) |
| run_capture.py:96 | write the whole chunk past the cap | `52428801` bytes; `2 failed` |
| run_capture.py:129 | drop `shutil.rmtree` | `9 failed` |
| doctor.py:97 | accept `*:{port}` | `2 failed, 65 passed` |
| config.py:118 | drop host path/query/fragment check | `/v1?x=1#f` loads; `1 failed, 55 passed` |
| model.py:18 | drop `ProxyHandler({})` (D21) | `2 failed, 74 passed` |
| privacy.py:37 | drop `.lower()` on the suffix | `5 failed, 27 passed` |

Ledger CHECK re-runs (also red, cmp 0): run.sh:6 96->0, run.sh:20 cannot-verify, run.sh:25 mktemp, run_capture.py:95
write guard, run_capture.py:101 cap killpg, config.py:71 missing file, runlog.py:92 card filter.

## Findings

- F1 (med, non-blocking): pathguard.py:55's newline join is untested. Seeded off, `CASEFILE_TOOLCHAIN=$'<checkout>/q\npathguard outside z'`
  makes the guard print a forged last line and run.sh runs the command, exit 0 (tip: 95). Want a test row with a newline path.
- F2 (low, non-blocking): config.py:67 and :145 raise RuntimeError (exit 1, traceback, no ConfigError) for
  `--config` through a symlink loop, `state`/`playbook = "~nosuchuserxyz/..."`, and `state` under a loop. Fails
  closed; D13's ConfigError clause names matters only. Same class as the carried RX-7 residue.

## Reconciliation with the round reports

- Build report (`214 passed`, 22 new tests) plus fix cycles 1 and 2 match the tip's `233 passed`; the gate `1`
  in the build note was deviation 7 (dashes in a chair file), not a flake; I saw `0` twice.
- V3-1 to V3-4 and verify2 N2 (held pipe) are fixed as the brief asked; N2 is the 2 s grace I measured.
- F1 is adjacent to brief R10 / Codex PR-4 (newline names, ruled out of scope) and build deviation 2 (last-line
  parsing); the join was written but never seeded. F2 matches fix1's "not changed: state/playbook expanduser".
- The output critic's F1 (HUP leaves a capture folder) is fixed: 0 folders after HUP, TERM, INT.
