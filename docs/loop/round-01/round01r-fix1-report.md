# Round 1 re-brief, fix cycle 1 report (RX-1 to RX-8), Sonnet 5.5

Librarian entries checked: pre-flight items on process-group kill on cap (CX-4), every exit-code branch
has its own test (V-B2, V-B3), guard aliases not only the named one (V-B1b), a check never creates its
subject (OC-M7), failure tests assert the exit code (CX-11), fix checked against the spec row (OC-M8:
no new limit; kqueue is macOS only, as the project is). Tests: `tests/test_fix_cycle3.py` (9 tests).
Probes use tmp_path or $TMPDIR; nothing was created in the checkout; no process left running.

| ID | RED on old tree | Fix | Teeth seed -> RED |
|---|---|---|---|
| RX-1 | `assert 137 == 3` (chair probe, stopped child killed at 2 s) | run_capture.py:35-39,45-56: no SIGCHLD handler; kqueue NOTE_EXIT on the child pid (not raised by stop or continue, does not reap) | SIGCHLD handler and 0.2 s poll re-added: `assert 137 == 3` |
| RX-2 | `assert 0 == 1` (shim python3 ran `false` as success) | run.sh:8-9,23: `PY="$(command -v python3)"` before the PATH change; guard and exec both use `$PY` | `exec "$PY"` -> `exec python3`: `assert 0 == 1` |
| RX-3 | `ValueError: timeout must be non-negative` (fake clock, +0.6 s per read) | run_capture.py:44,57: one clock read per pass, `max(0.0, deadline - now)` | clamp and single read removed: `ValueError: timeout must be positive or None` |
| RX-4 | `PermissionError` out of the `finally` instead of exit 98 | run_capture.py:109-112: killpg in `finally` tolerates OSError | try/except removed: `PermissionError` |
| RX-5 | `ValueError: filedescriptor out of range in select()` (pipe forced above fd 1100 with RLIMIT_NOFILE raised to 4096; this Mac allows it) | run_capture.py:54: kqueue, no FD_SETSIZE limit (RX-1 and RX-5 share it) | `select.select` back in: same ValueError, exit 1 |
| RX-6 | `RecursionError` from a real 2000-link chain and from a patched realpath (both tests red) | pathguard.py:44: `except Exception` -> cannot-verify (message falls back to the class name) | `except (OSError, ValueError)`: both `RecursionError` |
| RX-7 | `ValueError: embedded null byte` for `~bad\u0000/x` | config.py:125-128: any exception from expanduser -> ConfigError "cannot expand ~ in [paths].matters" (exit 2 via cli) | `except RuntimeError`: `ValueError` |
| RX-8 | green on the current tree by design (guard already has venv) | test only: fake root in tmp, `T/venv` -> `<root>/sub`, `<root>/sub/bin` -> outside; run.sh copy must exit 95 and create nothing; module check venv alone inside, venv/bin alone outside | `"$TOOLCHAIN/venv"` dropped from the guard call: `(0, b'') == (95, b'')` |

Notes
- RX-3 cannot be red by real timing; the closest deterministic test replaces the module's clock with one
  that advances 0.6 s per read (two reads per pass then straddle the 2 s deadline). RX-4 patches `os.killpg`
  in a copy of the module globals to kill the group and then raise EPERM.
- RX-8 module-level equivalent is a classify check of the two spellings; it does not read the run.sh
  argument list, so the run.sh test is the one with teeth.
- Not changed (out of scope, same class): `config.py` state/playbook `Path(...).expanduser()` can still raise.
- Seeds were restored byte-identically (cmp) after each RED; each test GREEN after restore.

Regression: `pytest -q` 223 passed (baseline 214 + 9); gate prints 0; `test_stage1_exit.py -s` 2 passed.
