# Round 1 re-brief Codex code review (8a), gpt-6.1-sol, read-only, high, 2026-10-26

1. **RX-1 | high | CONFIRMED** : [scripts/run_capture.py:29](/Users/davidskoranski/legal-harness/scripts/run_capture.py:29): The SIGCHLD handler mistakes a stopped child for an exited child and starts the destructive grace timer.  
   Scenario: the child receives SIGSTOP, resumes after 0.1 seconds, then continues legitimate work for five seconds → the wrapper kills its entire group after two seconds and returns 137. CPython installs this handler without `SA_NOCLDSTOP`. ([CPython source](https://github.com/python/cpython/blob/v3.12.13/Python/pylifecycle.c#L2975))

2. **RX-2 | med | CONFIRMED** : [scripts/run.sh:17](/Users/davidskoranski/legal-harness/scripts/run.sh:17): Changing PATH after the guard allows a different, unchecked capture interpreter to silently return success without running the command.  
   Scenario: bootstrap Python is valid, but the outside toolchain’s `venv/bin/python3` is a shim containing `exit 0` → the guard passes, `scripts/run.sh false` returns 0 without executing `false`, and the capture directory remains.

3. **RX-3 | med | CONFIRMED** : [scripts/run_capture.py:60](/Users/davidskoranski/legal-harness/scripts/run_capture.py:60): The second clock read can produce a negative `select` timeout after the preceding deadline check passed.  
   Scenario: deadline is 102.0; line 50 observes 101.999; scheduling delays execution until line 60 observes 102.001 → `select` raises ValueError, exit 3 becomes exit 1, and a surviving pipe holder escapes the grace kill because cleanup reaps the already-dead leader. ([CPython timeout validation](https://github.com/python/cpython/blob/v3.12.13/Modules/selectmodule.c#L290))

4. **RX-4 | med | CONFIRMED** : [scripts/run_capture.py:93](/Users/davidskoranski/legal-harness/scripts/run_capture.py:93): The unguarded cleanup `killpg` can replace the intended capture-failure exit 98 with an exception.  
   Scenario: capture writing fails, cleanup’s `poll()` observes a running child, and that last group member exits before `killpg` → macOS rejects the zombie-only group with EPERM; the wrapper exits 1 and skips the remaining cleanup. The cap and grace branches catch this error, but `finally` does not. ([XNU implementation](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/kern/kern_sig.c#L1612))

5. **RX-5 | med | CONFIRMED** : [scripts/run_capture.py:61](/Users/davidskoranski/legal-harness/scripts/run_capture.py:61): Introducing `select.select` adds an undocumented descriptor-number limit.  
   Scenario: the wrapper inherits enough open descriptors that its child-output pipe receives descriptor 1024 or higher → `select` raises ValueError on this Mac, so an otherwise successful command returns 1. This limit is absent from D12. ([CPython descriptor validation](https://github.com/python/cpython/blob/v3.12.13/Modules/selectmodule.c#L159))

6. **RX-6 | low | CONFIRMED** : [src/casefile/pathguard.py:27](/Users/davidskoranski/legal-harness/src/casefile/pathguard.py:27): Non-strict `realpath` can raise an uncaught RecursionError before the identity walk on supported Python 3.9/3.12.  
   Scenario: roughly 2,000 distinct symlinks form an acyclic chain ending at the checkout → their recursive resolver exceeds its recursion limit; pathguard produces a traceback and exit 1, and config loading escapes instead of returning ConfigError/exit 2 for an unverifiable path.

7. **RX-7 | low | CONFIRMED** : [src/casefile/config.py:126](/Users/davidskoranski/legal-harness/src/casefile/config.py:126): Tilde expansion can raise before either the unexpandable-home check or pathguard handles the input.  
   Scenario: valid TOML supplies `matters = "~bad\u0000/x"` → `pwd.getpwnam` rejects the embedded NUL with ValueError, producing a traceback and exit 1 instead of ConfigError/exit 2. ([CPython username validation](https://github.com/python/cpython/blob/v3.12.13/Modules/pwdmodule.c#L202))

8. **RX-8 | low | CONFIRMED** : [tests/test_run_sh.py:343](/Users/davidskoranski/legal-harness/tests/test_run_sh.py:343): The `venv` refusal probe is masked by the separate `venv/bin` check.  
   Static mutation trace: removing `$TOOLCHAIN/venv` from the guard arguments leaves this probe refusing through `venv/bin`. The missed regression is an outside toolchain whose `venv` links to a checkout subfolder while that subfolder’s `bin` links outside → the omitted guard allows uv to use a venv inside the checkout.

Count: **1 high, 4 med, 3 low.**
## Chair reproduction

| ID | Status | Evidence |
|---|---|---|
| RX-1 | REPRODUCED | `run.sh bash -c '(sleep 0.3; kill -CONT $$) & kill -STOP $$; sleep 4; exit 3'` -> `exit=137 secs=2` (want 3 after ~4 s) |
| RX-2 | ACCEPTED (trace) | run.sh:17 prepends venv/bin before `exec python3`; the capture interpreter is not the one that ran the guard |
| RX-3 | ACCEPTED (trace) | run_capture.py:50 and :60 read the clock twice |
| RX-4 | ACCEPTED (trace) | run_capture.py:93 `killpg` in `finally` without the OSError guard the other two sites have |
| RX-5 | ACCEPTED (trace) | `select.select` has an FD_SETSIZE limit; `selectors.DefaultSelector` (kqueue) does not |
| RX-6 | ACCEPTED (trace) | pathguard.py:27 `os.path.realpath` recursion; RecursionError not caught |
| RX-7 | ACCEPTED (trace) | config.py:126 `os.path.expanduser` on `~user` with NUL raises ValueError |
| RX-8 | ACCEPTED (trace) | `venv` refusal masked by `venv/bin`; a test needs a fake root in tmp where `venv` links into it and `venv/bin` links out |

Routing: all eight to re-brief fix cycle 1 (Sonnet 5.5, Q27).
