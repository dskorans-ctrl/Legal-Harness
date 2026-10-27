# Round 1 re-brief fix cycle 2 (F1 to F6) report

Librarian entries checked: whole file read; applied #R01-V-B2/B3 (each exit branch has its own test,
so teeth below seed each load-bearing line), #R01-CX-4 (group kill kept), #R01-OC-M7 (no check
creates its subject; F2 test calls check_playbook only, nothing in the checkout), #R01-OC-M8 (each
fix checked against its spec row: D12, D13, D14, D23, D24; no new limit), #R01-V-B1b (guard
unchanged, only its message). Q-A and Q-B untouched.

New tests: `tests/test_fix_cycle4.py` (10 tests). All RED on the old tree (8 failed, 2 controls pass).

| Row | Fix | Teeth (defect back, test RED, cmp restore, GREEN) |
|---|---|---|
| F1 | `scripts/run_capture.py` handlers for HUP/TERM/INT raise `Interrupted`; except clause prints `run.sh: interrupted by <NAME>; job stopped`, returns 128+n; existing finally kills the group and removes the folder (signals ignored during cleanup). Tests: HUP, TERM, INT each: exit 128+n, child and grandchild gone, `casefile-run.*` count 0 in TMPDIR. | handler install -> `pass`: 3 failed; restored: 3 passed |
| F2 | `src/casefile/config.py` state and playbook resolve against the checkout; `config.example.toml` comments updated. | `source.parent`: 1 failed; restored: 2 passed |
| F3 | `scripts/run.sh` refusal names resolved toolchain and checkout, the fix, and the `~` / `$HOME` hint; exit 95. | tilde case pattern broken: 1 failed; old text: 1 failed; restored green |
| F5 | `src/casefile/doctor.py` `State.root` tracks the first own failure; blocked hint is `fix the <root> line above` when root differs from the immediate blocker. | `False`: 1 failed; restored green |
| F6 | `src/casefile/config.py` `unknown user in [paths].matters: ~name` (bare `~` keeps the old message). | `len(user) > 1` -> `False`: 1 failed; restored green |

Old behaviour encoded in tests, updated: `tests/test_config.py::test_paths_defaults_and_frozen_config`
(state/playbook now ROOT); `tests/test_run_sh.py` (four sites) and `tests/test_fix_cycle3.py:188`
matched the old refusal text and now match the new prefix `run.sh: toolchain `, "is inside the checkout", suffix `; exit 95`.

Note: SIGHUP/TERM/INT arriving in the few microseconds before Popen returns are not covered
(child unset, nothing to kill); capture folder is still removed.

Regression: pytest 233 passed (223 baseline + 10); gate exit 0, five rows PASS; stage1 exit test 2 passed.
No leftover processes; nothing created in the checkout by probes.
