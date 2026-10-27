# Round 1 re-brief build report (W1 to W6), builder Sonnet 5.5

Branch loop/round-01, from d7fd451. Commits: 330ff81 (W1), 7959f27 (W2), 2364c7b (W3, W4), b428bfa (W5), a69814d (W6).
Files: src/casefile/pathguard.py (new), src/casefile/config.py, scripts/run.sh, scripts/run_capture.py,
tests/conftest.py (`alias_table` context manager), tests/test_pathguard.py (new), tests/test_config.py, tests/test_run_sh.py.

## Built
- W1 pathguard.classify(path, root) and CLI per brief 1.1 and 1.2 (typed and real spelling, every ancestor, only ENOENT/ENOTDIR skipped).
- W2 config.py uses os.path.expanduser, refuses an unexpanded `~`, maps the four verdicts, stores the walked realpath.
- W3 run.sh: `$PWD` join, usage 96, guard call with the five strings, token check, then exports and mktemp. W4 usage test.
- W5 grandchild-in-group test. W6 run_capture.py: SIGCHLD record, select 0.2 s, GRACE_S 2.0, OSError-tolerant killpg in both places, normalised status.

## Mutation table (every seed: baseline green, seed, RED, cmp restore, green)
| Claim | Seed | RED text | Control |
|---|---|---|---|
| realpath spelling needed | W1a drop realpath spelling | `alias_wrong=5 of 19` (chain, dangling, dotdot-after-missing, 2 subfolder) | cmp ok, `6 passed` |
| no normpath | W1b add normpath | `alias_wrong=3` hop-dotdot-through-link (1 row, 3 callers) | cmp ok |
| EACCES not missing | W1c | unreadable-ancestor wrong | cmp ok |
| ELOOP not missing | W1d | loop wrong | cmp ok |
| CLI exit codes | W1e inside 10 to 0 | `alias_wrong=13 of 19` | cmp ok |
| stdlib only | W1f add pathlib import | `imports=errno,os,pathlib,sys` | cmp ok |
| typed spelling needed | W1g drop typed | test_link_inside_checkout_pointing_out `'outside' == 'inside'` | cmp ok |
| CLI reads all paths | W1h paths[:1] | test_cli_many_paths red | cmp ok |
| config maps inside | W2a | `matters_alias_wrong=13 of 19` | cmp ok, 25 passed |
| config maps cannot-verify | W2b | 2 rows (loop, unreadable) | cmp ok |
| config maps relative | W2c | 1 row (relative) | cmp ok |
| config refuses bare `~` | W2d | `Regex pattern did not match ... must be an absolute path` | cmp ok |
| run.sh inside branch | W3a | `toolchain_alias_wrong=16 of 20` | cmp ok |
| run.sh fail-closed branch | W3b | 2 rows (loop, unreadable) + guard-unavailable shims | cmp ok |
| run.sh `$PWD` join | W3d | 1 run (relative at tmp cwd) wrong | cmp ok |
| nothing created | W3e (unique mkdir before guard) | `toolchain_alias_wrong=20 of 20 created=20` | cmp ok, dirs removed |
| guard covers cache | W3c2 drop cache | child test `[cache]` red (returncode 0) | cmp ok |
| guard covers python | W3c3 | child test `[python]` red | cmp ok |
| usage 96 | W4 `exit 96` to `exit 0` | `usage_exit=0`, `(0, b'') == (96, b'')` | cmp ok |
| group kill on cap | W5 killpg to child.kill() | `grandchild_alive=1` | cmp ok |
| grace bounded | W6a GRACE_S 3600 | 3 held-pipe tests fail by 10 s timeout | cmp ok |
| finite select | W6b POLL_S None | same 3 fail | cmp ok |
| group kill after grace | W6c | `grandchild_alive=1` twice | cmp ok |
| EPERM tolerated | W6d1 grace branch / d2 cap branch | PermissionError traceback; `escaped_cap_exit=1` | cmp ok |
| status normalised | W6e | `child exited 137 ... assert` sigkill row red | cmp ok |

Final CHECK values: `alias_wrong=0 of 19 interpreters=2`, `py39_syntax=ok`, `imports=os,sys,errno`, `matters_alias_wrong=0 of 19`,
`toolchain_alias_wrong=0 of 20 created=0`, `usage_exit=96`, `grandchild_alive=0`, `held_pipe_secs=2.06/2.08/2.12`, `escaped_cap_exit=97`.

## Deviations and findings (chair to rule)
1. W3 seed (c) as written cannot go red: the guard walks ancestors, so `$TOOLCHAIN/venv` is covered by `venv/bin`. Dropping `cache` or `python` is red (rows above). The `venv` string is redundant but kept as the brief lists it.
2. run.sh checks the LAST line of the guard output: `/usr/bin/python3` printed an xcrun cache warning (stderr, merged by 2>&1) above the token and the system-python tripwire failed closed (95). The whole output is still shown in the 95 message.
3. Row `hop-dotdot-through-link`: the sandbox forbids a link beside the checkout (`ln: Operation not permitted` in /Users/davidskoranski). Row is `$B/hop -> $B/deep/sub`, path `$B/hop/../lroot/m` (lroot is the root alias): normpath reads inside, the kernel says outside. Same seed value, nothing outside tmp.
4. W3 seed (e) as written (fixed mkdir name) stays green because test_toolchain_outside_repo creates it before the first snapshot; a per-pid name goes red.
5. Added `test_run_sh_on_system_python_only` (brief 5 R1; asserts /usr/bin/python3 exists, TMPDIR set because /tmp is not writable here). No seed (tripwire).
6. Suite wall time rose from 12.9 s to 32 s: /usr/bin/python3 CLI runs in test_pathguard (8 s) and three 2 s grace waits. R5 asked for 20 percent; not met.
7. Gate prints `1`, not 0: `gate prose FAIL dashes=5` all in docs/loop/round-01/round01r-brief-codex.md (chair file, committed in d7fd451, untouched by me). pytest, privacy, rules, playbook PASS.
8. grep -c poll scripts/run_capture.py = 1. The guard line is below usage and above the `venv/bin` test (grep -n: lines 6, 8, 16).

## Regression
Full pytest last line: `214 passed in 32.60s` (192 + 22 new). Stage 1 exit: `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`, 2 passed.
`time scripts/run.sh true` 0.047 s. Working tree clean after W6 except this report. No process left running.

## Librarian entries checked
Pre-flight lines: #R01-CX-1, #R01-V-B1 (identity), #R01-V-B1b (every alias), #R01-CX-4 (group kill, python3 on PATH), #R01-OC-M7 (never create the subject; os.walk snapshot), #R01-V-B2, #R01-V-B3 (one test per exit branch), #R01-CX-11 (exit codes asserted), #R01-OC-M8 (no new limit: relative override and `~` work), #R01-P-1 (chair re-runs).
