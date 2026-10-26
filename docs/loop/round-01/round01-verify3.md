# Round 1 focused re-verification (verifier 3, owner Q23)

**Verdict: FAIL.** R1-4 and R1-13 refused on new residues (V3-1 to V3-4); V1 not ticked.

Fresh Opus 5.5 session, no building or earlier verifying context. Branch `loop/round-01`, tip `6db09cb`.
Scope per Q23: R1-4 and R1-13 plus regression. Probes invented; scratch folder `$S` under `$TMPDIR`.
Reports and scratch read only after ticks were set.

## Regression

| Result | Command |
|---|---|
| `192 passed in 11.26s`, exit 0 | `scripts/run.sh pytest -q` |
| gate rows pytest `exit=0`, privacy `offenders=0 scanned=223`, rules_selftest `misses=0 false_hits=0`, playbook `pb-00be6eb62752`, prose `dashes=0 files=61`; prints `0` | `scripts/run.sh python -m casefile.gate` |
| `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`; `stage-control ... expected={'ocr'} test_jobs=1`; `2 passed in 0.78s` | `scripts/run.sh pytest -q -s tests/test_stage1_exit.py` |

No ticked item unticked. No server left running.

## R1-4 probes (`scripts/run.sh casefile config show --config <tmp>`)

Exit `2` `must be outside the checkout`: `/Users/davidskoranski/LEGAL-HARNESS/invented-m`; symlink to root;
case-swapped symlink to root; symlink to `.../Legal-Harness/tests/fixtures`; chain `chain2 -> chain1 -> subCase`;
chain to root; relative symlink to `LEGAL-harness/src`; dangling symlink into `LEGAL-HARNESS/no-such-dir`;
dangling symlink to `/Users/davidskoranski/nope/../LEGAL-HARNESS/x`; `tests/../INVENTED/x`;
`$S/nope/../../../../../../Users/davidskoranski/legal-harness/inv`; `$S/subCase/../../x`; `~/legal-harness/inv`; the checkout.
Exit `2` `must be an absolute path`: `invented-m`, `./invented-m`. Exit `2` `cannot verify ... [Errno 13]`: chmod 000 parent.
Exit `0`: `$S/out/ok` (exists), `$S/out/new-matter` (new). Exit `1`: symlink loop (V3-1).

Toolchain (`CASEFILE_TOOLCHAIN=<alias> scripts/run.sh true`): normal `0`; checkout, case-swapped checkout,
symlink, case-swapped symlink, case-swapped subfolder symlink, chain, `$R/tests/..`, relative `relchk` all `95`;
chmod 000 parent `95` `cannot verify`; outside `0`; `..` after a missing component `0` (V3-2).

## R1-13 probes

No args `96`; cap `52428800` bytes, `97`, `secs=0` with `sleep 30` after overflow; `TMPDIR=/nonexistent/dir` `98`;
`ulimit -f 1` with 200000 and 4096 bytes `98` `[Errno 27] File too large` (B3 fixed; 4096 was `0` at c997bc1),
400 bytes `0`; toolchain in checkout `95`; non-executable file `126`, directory `126`; missing `127`; child `3`;
background grandchild after overflow killed.

## Seeds (pytest from the venv with its bin on PATH, baseline `192 passed`; each restored, `git diff --quiet` clean)

| Line | Mutation | Result |
|---|---|---|
| run.sh:23 | identity `exit 95` -> `true` | RED `5 failed` |
| run.sh:19 | drop `"$physical"` walk | RED `2 failed` |
| run.sh:19 | drop `"$TOOLCHAIN"` walk | GREEN: equivalent for safety (physical walk covers every real inside path) |
| run.sh:17 | cannot-verify `exit 95` -> `physical=/` | GREEN: finding V3-4 |
| run.sh:32 | `exit 96` -> `exit 0` | GREEN: finding V3-3 |
| run.sh:34 | mktemp `exit 98` -> `exit 0` | RED `1 failed` |
| run_capture.py:13 | `return 98` -> `return 0` | RED `7 failed` |
| run_capture.py:32 | 127 -> 126 | RED `1 failed` |
| run_capture.py:35 | 126 -> 1 | RED `1 failed` |
| run_capture.py:42 | no-progress guard -> `if False:` | GREEN: non-blocking (write of 0 on a regular file not reachable here) |
| run_capture.py:44 | `remaining[written:]` -> `remaining[len(remaining):]` | RED `2 failed` |
| run_capture.py:51 | `os.killpg(...)` -> `child.kill()` | GREEN: finding V3-3 |
| run_capture.py:55 | `return 97` -> `return 0` | RED `3 failed` |
| run_capture.py:57 | child code -> `0` | RED `13 failed` |
| config.py:129 | `resolved = matters` | RED `2 failed` |
| config.py:132 | candidates `(matters,)` | RED `2 failed` |
| config.py:132 | candidates `(resolved,)` | GREEN: equivalent for safety |
| config.py:139 | store `matters` not `resolved` | GREEN: non-blocking (stored spelling only) |

## Findings

**V3-1 (blocking, R1-4, D13).** `src/casefile/config.py:129`. Probe: `loopA -> loopB -> loopA`,
`matters = "$S/loopA/m"`. Observed exit `1`, traceback `RuntimeError: Symlink loop from '.../loopA/m'`
(pathlib raises RuntimeError, the `except OSError` misses it). Expected exit `2` with a ConfigError
`cannot verify`. Fails closed (nothing loads), so not a fail open, but outside the contract.

**V3-2 (blocking, D12 95, D23).** `scripts/run.sh:6-29`. Probe:
`CASEFILE_TOOLCHAIN="$S/nope/../../../../../Users/davidskoranski/legal-harness" scripts/run.sh sh -c 'mkdir -p "$UV_PROJECT_ENVIRONMENT"'`.
Observed exit `0` and `/Users/davidskoranski/legal-harness/legal-harness/venv` created (removed after).
Expected `95`. The deepest existing ancestor is `$S` (outside), and no typed prefix past `nope` exists, so `-ef` never
matches; the path normalizes lexically and physically (after `mkdir -p`) into the checkout. Fix: refuse a
`..` segment in `$TOOLCHAIN`, or normalize lexically before the walk (config.py already does: same probe exits `2`).

**V3-3 (blocking, R1-13, same class as B2, B3).** Two D12 branches have no test: `scripts/run.sh:32`
exit 96 (seed `exit 0`: `192 passed`, no args then exits `0`), and the group kill at
`scripts/run_capture.py:51` (seed `child.kill()`: `192 passed`; probe `bash -c "sleep 77 & ...; head -c 52428801 /dev/zero"`:
grandchild `ALIVE` under the seed, `dead` on the tip). `test_cap_terminates_sleeping_child` checks only the direct child.

**V3-4 (blocking, R1-13).** `scripts/run.sh:16-17` cannot-verify 95 untested: seed `physical=/` -> `192 passed`;
with a chmod 000 toolchain parent the seeded wrapper exits `0` (tip `95`).

## Reconciliation

- verify2 B1b: fixed. Both case-swapped subfolder symlinks exit `2`, and the fix4 seeds (omit resolved ancestors,
  `resolved = matters`) go red as fix4 reports. verify2 C3 (OSError branch untested): now tested (chmod 000 probe).
- verify2 B3: fixed. Short writes now `98`; fix4's write-guard and single-write seeds agree with mine (RED `2 failed`).
- fix4 claims are accurate as far as they go: its toolchain teeth cover the physical walk and the 95 code, not
  `..` after a missing component (V3-2), the cannot-verify branch (V3-4), 96 or the group kill (V3-3).
  Its full-suite `5 failed` was sandbox bind; here `192 passed` inside the sandbox.
- verify2 N2 (a background grandchild holds the wrapper on the non-cap path) is out of Q23 scope, still unscheduled.
