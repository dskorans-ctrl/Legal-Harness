# Round 1 re-brief: path identity guards and wrapper exit branches (Q24, Q26)

Branch `loop/round-01` at `3502fc5` (working tree: chair's uncommitted ledger and owner-question edits,
leave them). Scope is LIMITED to ledger R1-22 and R1-23: verify3 V3-1 to V3-4, verify2 N2. Nothing else in
stage 1 reopens; 18 of 20 items hold at `192 passed` (re-measured 2026-10-26: `scripts/run.sh pytest -q`
-> `192 passed in 12.21s`), gate `0`. Builder: Sonnet 5.5 per Q27, one lane; Codex gpt-6.1-sol keeps the
reviews; the chair commits and re-runs every CHECK and seed (Librarian R01-P-1). Privacy: every path, name
and byte below is invented; no PDF, Word or image anywhere; the toolchain guard creates nothing inside the
checkout (capture dir under `${TMPDIR:-/tmp}`, run.sh:33, removed at run_capture.py:66, §7 Q18). Revised once after Codex (§8).

## §0 Drift (plan versus the code and the machine, verified 2026-10-26)

- D1. The chair's design says "resolve strictly where possible, catch RuntimeError and OSError". Measured:
  `Path.resolve(strict=False)` on a loop raises RuntimeError on 3.9 and 3.12 (that is V3-1, config.py:129)
  but returns the unresolved path silently on 3.14; `os.path.realpath` never raises on a loop on any of the
  three; `os.path.exists` swallows ELOOP and EACCES; `os.stat` raises ELOOP (62) and EACCES (13). So the
  module must not detect loops by exception from resolve: it stats every ancestor itself and treats only
  ENOENT and ENOTDIR as "missing". No RuntimeError catch (dead code a verifier would seed green).
- D2. `python3` on PATH here is 3.14.6 (`/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`);
  `/usr/bin/python3` is 3.9.6 (Xcode CLT, prints an xcrun cache warning inside the sandbox, exit 0); the
  venv is 3.12 (`~/.casefile-dev/legal-harness/venv`). run.sh:31 prepends the venv only if it exists and
  run.sh:35 `exec python3 ...`, so on a fresh checkout before `uv sync` the guard and the capture stage
  both run on whatever `python3` PATH gives. The module must run on 3.9 syntax (no `X | Y` annotations).
  `os.waitid` is absent on the 3.9 and 3.12 builds here (present on 3.14): N2 cannot use it (§1.8).
- D3. run.sh has no mkdir of its own (verified lines 1 to 35): the only creation on a refused run is what
  the CHILD does with the exported `UV_*` paths (V3-2 created `<checkout>/legal-harness/venv` through
  `mkdir -p`). The guard therefore only needs to run before the exports (line 30) and the exec (line 35).
  run.sh:4 appends `$(basename "$ROOT")` to the override, so the judged path is `<override>/legal-harness`.
- D4. Current branch order in run.sh is 95 (lines 6 to 29) then 96 (line 32) then 98 (line 33); D12 lists
  codes with no order. This brief fixes the order 96, 95, 98, exec (§1 item 5) and writes it into D12.
- D5. Reproduced on the tip: V3-2 `CASEFILE_TOOLCHAIN="$S/nope/../../../../../../../../Users/davidskoranski/
  legal-harness" scripts/run.sh true` -> exit `0` (literal inside -> `95`); V3-1 -> `RuntimeError: Symlink
  loop`; no args -> `96` with no test (grep `96` in tests/test_run_sh.py: none); N2 `bash -c 'sleep 4 &
  exit 3'` -> `3` after 4.08 s. A prototype of §1's walk (`$TMPDIR/pg/proto.py`, not in the repo) gave the
  right verdict on all 19 rows of §4 under 3.9, 3.12 and 3.14 with the spellings typed and realpath; adding
  `normpath` made row `hop-dotdot-through-link` a false `inside` on all three (§8 PR-10, PR-11).
- D6. Measured for N2 on 3.9, 3.12 and 3.14: `os.killpg` on a group whose leader is an unreaped zombie
  and whose only other member left the group raises `PermissionError` (EPERM), not `ProcessLookupError`;
  so run_capture.py:51 tracebacks (exit 1, not 97) when an escaped descendant supplies the overflow after
  the leader exits (§8 PR-9). A prototype of §1.8 (`$TMPDIR/cap_proto.py`) returned 3 at 2.01 s (group
  member killed), 137 (`kill -KILL $$`), 3 at 2.03 s (escaped holder), 97 at 0.54 s, 5 at once (EOF).

## §1 Decisions (accept, improve, reject; Librarian IDs cited)

1. ACCEPT one module `src/casefile/pathguard.py`, stdlib only (`os`, `sys`, `errno`), python3 >= 3.9,
   importable without the venv, no import of the `casefile` package. One function
   `classify(path, root) -> (verdict, detail)`, verdict in `relative`, `inside`, `outside`,
   `cannot-verify`; for `outside` the detail is the realpath the walk used (config stores it, so the
   stored path is the checked one). CLI `python3 -I pathguard.py <root> <path> [<path>...]`: classifies
   each path in order, reports the first verdict that is not `outside` (else `outside` with the first
   path's realpath) as one stdout line `pathguard <verdict> <detail>`, nothing on stderr; exits 0
   outside, 10 inside, 11 cannot-verify, 12 relative (never 1: a traceback must be told apart).
   Root is an explicit argument (config passes `Path(__file__).resolve().parents[2]` as today at
   config.py:125; run.sh passes `$ROOT` from line 3) so tests can use a throwaway root. (#R01-CX-1,
   #R01-V-B1, #R01-V-B1b: third guard rewrite; this time one implementation and one table.)
2. IMPROVE the walk (from D1): `root_id = (st_dev, st_ino)` of `os.stat(root)` (missing root ->
   cannot-verify). Spellings, deduplicated in order: the typed path and `os.path.realpath(typed)`. For
   each spelling walk itself and every `os.path.dirname` ancestor up to `/`; `os.stat` each (follows
   links); ENOENT or ENOTDIR -> skip; any other OSError (EACCES, ELOOP, ENAMETOOLONG, EIO) ->
   `cannot-verify` with `str(exc)`; identity equal to root -> `inside`. Only when every ancestor of every
   spelling is missing or different: `outside`. Why two spellings: typed catches a symlink inside the
   checkout pointing out (an ancestor is the root); realpath catches a link to a subfolder, a chain, a
   dangling link into the checkout and `..` after a missing segment (V3-2; Python's realpath takes `..`
   lexically there on 3.9, 3.12 and 3.14, measured). NO `normpath` spelling: it turns `$H/hop/../
   legal-harness/m` (hop -> elsewhere) into the checkout's name and refuses a path whose destination is
   outside (§0 D5). No pathlib, no `is_relative_to`, no spelling comparison; a relative path is a verdict.
3. ACCEPT config.py calls it: replace config.py:124 to 139. Line 124 becomes `expanded =
   os.path.expanduser(paths["matters"])`; if `expanded` still starts with `~` -> ConfigError `cannot
   expand ~ in [paths].matters: no home directory` (pathlib's expanduser raises RuntimeError there,
   pathlib.py:1406 on 3.12, and cli.py:45 catches only ConfigError; `~` keeps working, test_config.py:82).
   Then `relative` -> ConfigError `[paths].matters must be an absolute path` (kept verbatim,
   test_config.py:23 and :126); `inside` -> `[paths].matters must be outside the checkout {checkout}`
   (kept verbatim); `cannot-verify` -> `cannot verify [paths].matters is outside the checkout: {detail}`
   (kept verbatim, test_config.py:193); `outside` -> store `Path(detail)` (the walked realpath).
   cli.py:45 to 47 already maps ConfigError to exit 2 (V3-1 closes by never raising RuntimeError).
4. ACCEPT run.sh calls it before the exports. After line 4, a non-absolute `$TOOLCHAIN` is joined to
   `$PWD` (`case "$TOOLCHAIN" in /*) ;; *) TOOLCHAIN="$PWD/$TOOLCHAIN";; esac`): a relative override keeps
   working as today (run.sh:4 and the `-ef` walk at :21 take it against cwd; D23 is unqualified, M8).
   Then `verdict="$(python3 -I "$ROOT/src/casefile/pathguard.py" "$ROOT" "$TOOLCHAIN" "$TOOLCHAIN/python"
   "$TOOLCHAIN/cache" "$TOOLCHAIN/venv" "$TOOLCHAIN/venv/bin" 2>&1)"`: the five strings run.sh actually
   exports or prepends (lines 30 and 31), since any child can be a symlink into the checkout while the
   parent passes. Three branches on the captured line: `pathguard outside *` continues; `pathguard
   inside *` prints `run.sh: toolchain must be outside the checkout; exit 95` (kept verbatim,
   test_run_sh.py:161 and :175); anything else (cannot-verify, relative, a traceback, an `exit 0` or
   `exit 1` shim that prints nothing, `python3: command not found`) prints `run.sh: cannot verify
   toolchain path: ${verdict:-no verdict}; exit 95` and exits 95: the token closes the fail-open of a
   `python3` shim on PATH that exits 0. Lines 5 to 29 are deleted. The guard runs BEFORE line 31's own
   PATH prepend; an inherited PATH is the caller's (#R01-CX-4: one more call to the same python3, §7 Q16).
5. IMPROVE order: usage 96 first (no interpreter needed, nothing to do), then guard 95, then mktemp 98,
   then exec; D12 gains the order (§6). A no-argument run with an inside toolchain exits 96.
6. ACCEPT one alias table shared by three test files through a conftest helper
   `alias_table(base, root)` returning rows `(id, path, expected)`; it builds the links under `base`
   (a tmp_path) and uses `root` as the checkout (the real ROOT for the two callers, a throwaway tmp root
   for the module test). Every row is asserted by every caller; no row is skipped by name (ledger rule).
7. ACCEPT one test per D12 branch (§4 table) and ADD the grandchild rows V3-3 (same group, killed by the
   cap) and N2 (pipe held after the child exits). (#R01-V-B2, #R01-V-B3: a branch without its own seed is untested.)
8. N2 decision: BOUND THE WAIT, redesigned after PR-6 to PR-9 (all four close cleanly, §0 D6).
   run_capture.py installs a SIGCHLD handler before Popen that only records `time.monotonic()` in a list
   (never reaps); the read loop is `select.select([fd], [], [], timeout)` with timeout `0.2` while no
   exit is recorded (finite, so an exit between two checks is seen within 0.2 s) and `deadline - now`
   after it, `deadline = first SIGCHLD + GRACE_S`, `GRACE_S = 2.0`; readable -> `os.read` as today, EOF
   -> `child.wait()` and the normal return. No `child.poll()` in the loop: the leader stays an unreaped
   zombie, so its pid and the group id cannot be reused before the kill. On deadline: `os.killpg(child.pid,
   SIGKILL)` inside `try/except OSError` (ESRCH or EPERM, D6), `status = child.wait()`, print `run.sh:
   child exited {code} but its output pipe stayed open; process group killed after 2.0s` on stderr
   and return `status if status >= 0 else 128 - status` (line 57's normalisation, so a signalled
   child still gives 128 + n). The cap branch at :51 gets the same `try/except OSError`, still 97. A
   grandchild that left the group (`os.setsid`) is not reachable: the wrapper still returns after the
   grace; D12 says so. Reason: a harness that waits on strays is the stray-server problem of R01-P-1;
   pillar 2 wants a bounded, stated outcome. Rejected "document only": `sleep 30 & exit 3` holds 30 s.
9. REJECT adding a distinct exit code for cannot-verify (verify2 N1 asked): 95 stays one code for
   "toolchain refused", the stderr line carries the reason; D12 is amended to say "inside or not verifiable". Fewer codes, same fail-closed behaviour, tested by message.
10. The chair's instruction to the builder is this brief; each work item below is checked against its
    spec row before build (#R01-OC-M8). No new limit beyond D12, D13, D23 (M8 class): relative overrides
    and `~` keep working; no TMPDIR check (Q18); no interpreter version floor (a python that cannot run
    the guard fails closed by the token, one that runs it right is right).

## §2 Work items, in build order (one lane)

W1. `src/casefile/pathguard.py` (new, about 70 lines) + `tests/test_pathguard.py` (new) + conftest
  `alias_table`. Module per §1.1 and §1.2; `if __name__ == "__main__"` CLI per §1.1 (many paths).
  The module test also has `test_root_argument_aliases` (every row again with the root passed as
  `$B/lroot`, `$B/CHECKOUT` and the `/var/...` spelling of a `/private/var/...` tmp root: verdicts
  unchanged) and `test_link_inside_checkout_pointing_out` (`$R/lout -> $B/out`, `$R/lout/m` -> inside;
  the typed spelling's own case, throwaway root only, measured).
  CHECK: `scripts/run.sh pytest -q -s tests/test_pathguard.py > "$TMPDIR/w1.log"; echo "pytest_exit=$?";
  grep -E '^(alias_wrong|py39_syntax|imports)=' "$TMPDIR/w1.log"` prints `pytest_exit=0`,
  `alias_wrong=0 of 19 interpreters=N` where the test runs the table through `classify` in process and
  through the CLI (stdout token AND exit code) under every interpreter in `{sys.executable,
  /usr/bin/python3, shutil.which("python3")}` that exists (deduplicated; N >= 1), `py39_syntax=ok` from
  `ast.parse(source, feature_version=(3, 9))` and `imports=os,sys,errno` from an ast walk.
  SEEDS (each must go red, restored by cmp): (a) drop `os.path.realpath(typed)` from the spellings ->
  rows `symlink-subfolder-case`, `symlink-subfolder-bare`, `chain`, `dotdot-after-missing`,
  `dangling-into-checkout` wrong (measured: exactly these five; `dotdot-after-symlink` is caught by the
  typed walk); (b) add `os.path.normpath(typed)` as a spelling -> row `hop-dotdot-through-link` wrong;
  (c) `MISSING += (errno.EACCES,)` -> row `unreadable-ancestor` wrong; (d) `MISSING += (errno.ELOOP,)`
  -> row `loop` wrong; (e) CLI `inside` exit 10 -> 0 -> CLI rows wrong; (f) add `from pathlib import
  Path` -> `imports=` red; (g) drop the typed spelling -> `test_link_inside_checkout_pointing_out` red;
  (h) CLI classifies only `argv[2]` -> `test_cli_many_paths` red (and W3's child test).
  Pre-flight: Librarian line 15 (identity, every existing ancestor), line 31 (every alias at once).
W2. `src/casefile/config.py:124 to 139` call `classify` per §1.3; `tests/test_config.py` adds
  `test_matters_alias_table` driving every row through `load()` and through
  `scripts/run.sh casefile config show --config <tmp>` (exit 2, stdout has no `paths.matters =`, the
  expected message in `stdout + stderr`, since run_capture.py:28 merges the child's stderr into the
  wrapper's stdout, as test_config.py:193 already does; `outside` rows exit 0 and print the realpath)
  and `test_matters_unexpandable_home` (monkeypatch `os.path.expanduser` to return its argument,
  `matters = "~/invented"` -> ConfigError `cannot expand ~`). Existing alias tests stay.
  CHECK: `scripts/run.sh pytest -q -s tests/test_config.py > "$TMPDIR/w2.log"; echo "pytest_exit=$?";
  grep -E '^matters_alias_wrong=' "$TMPDIR/w2.log"` prints `pytest_exit=0`, `matters_alias_wrong=0 of 19`.
  SEEDS: (a) config.py mapping `if verdict == "inside"` -> `if verdict == "never"` -> 13 rows wrong;
  (b) `cannot-verify` raise removed (fall through to outside) -> rows `loop`, `unreadable-ancestor`;
  (c) `relative` check removed -> row `relative` (message `must be an absolute path`); (d) the `~`
  check removed -> `test_matters_unexpandable_home` red (message differs).
  Pre-flight: Librarian line 27 (assert exit code), #R01-OC-M8 (no limit beyond D13 and Q17).
W3. `scripts/run.sh`: delete lines 5 to 29; new order per §1.5; join and guard call per §1.4.
  `tests/test_run_sh.py` adds `test_toolchain_alias_table` (every row as `CASEFILE_TOOLCHAIN` with
  `scripts/run.sh true`, so run.sh judges `<row>/legal-harness` and the four children, which never
  changes a row's verdict since ancestors are walked: inside and cannot-verify rows exit 95, stdout
  `b""`, stderr starts `run.sh: toolchain` or `run.sh: cannot verify toolchain path`; outside rows exit
  0; the `relative` row runs twice, `cwd=ROOT` -> 95 inside and `cwd=tmp_path` -> 0) with a residue
  snapshot `sorted(join(d, n) for d, ds, fs in os.walk(ROOT) for n in ds + fs)` (every entry, ignored
  and empty directories included; 806 entries, 0.015 s) before and after each row, asserted equal.
  Adds `test_toolchain_exported_child_symlink_refused` (parametrised over `python`, `cache`, `venv`,
  `venv/bin`: `$B/tc` is a plain outside directory and only `$B/tc/legal-harness/<child>` is a symlink
  to `<case-swapped ROOT>/tests/fixtures` -> 95, nothing created). Adds
  `test_toolchain_guard_unavailable_exits_95` over three PATHs: a `tmp/bin/python3` shim `exit 1`, a
  shim `exit 0` (prints nothing: PR-3's fail-open), and a PATH holding only symlinks to `dirname`,
  `basename` and `mktemp` (no python3, shell 127) -> each 95, stderr contains `cannot verify toolchain
  path`, no `Traceback`. The three existing toolchain tests stay unchanged (their exact stderr lines hold).
  CHECK: `scripts/run.sh pytest -q -s tests/test_run_sh.py -k toolchain > "$TMPDIR/w3.log"; echo
  "pytest_exit=$?"; grep -E '^toolchain_alias_wrong=' "$TMPDIR/w3.log"` -> `pytest_exit=0`, `toolchain_alias_wrong=0 of 20 created=0`.
  SEEDS: (a) run.sh `pathguard outside *` branch -> `pathguard *` -> inside rows wrong; (b) the "anything
  else" branch mapped to continue -> rows `loop`, `unreadable-ancestor` (V3-4) and all three shim cases;
  (c) drop `"$TOOLCHAIN/venv"` from the guard call -> the child test's `venv` row red; (d) drop the
  `$PWD` join -> the `relative` row's `cwd=tmp_path` run exits 95 (red: a limit D23 does not have);
  (e) add `mkdir -p "$ROOT/.workflow/scratch/invented-residue"` before the guard -> `created=1` (git
  status would stay clean, .gitignore:61: why the snapshot is an os.walk); (f) the guard call moved after
  line 31's prepend has no runtime oracle (the shims sit on the inherited PATH either way): the chair
  confirms by `grep -n` that the guard line is below the usage line and above `[ -d "$TOOLCHAIN/venv/bin" ]`, with `-I`.
  Pre-flight: Librarian line 29 (never create the thing checked), line 20 (#R01-CX-4 python3 on PATH).
W4. `tests/test_run_sh.py::test_no_command_exits_96`: `scripts/run.sh` with no args -> `(96, b"")`,
  stderr `run.sh: usage: scripts/run.sh <cmd> [args]`; and with `CASEFILE_TOOLCHAIN=<checkout>/x` still
  96 (order). CHECK prints `usage_exit=96`. SEED run.sh `exit 96` -> `exit 0` -> red (V3-3 part 1).
W5. `tests/test_run_sh.py::test_cap_kills_grandchild_in_group`: `bash -c 'sleep 77 & echo $! > <pid>;
  head -c 52428801 /dev/zero'` -> 97 within 5 s and `os.kill(pid, 0)` raises ProcessLookupError
  (finally: SIGKILL the pid if alive). CHECK prints `grandchild_alive=0`. SEED run_capture.py:51
  `os.killpg(child.pid, signal.SIGKILL)` -> `child.kill()` -> `grandchild_alive=1` (V3-3 part 2).
W6. `scripts/run_capture.py` read loop per §1.8 (SIGCHLD record, finite select, no poll in the loop,
  grace, OSError-tolerant killpg in both branches, normalised status). Tests:
  `test_pipe_held_by_group_member_bounded` parametrised `exit 3` -> 3 and `kill -KILL "$$"` -> 137
  (`bash -c 'sleep 30 & echo $! > <pid>; <tail>'`, each in under 10 s, grandchild dead, stderr has `pipe
  stayed open`); `test_pipe_held_by_escaped_process_bounded` (child is `python3 -c` that Popens `sleep
  30` with `start_new_session=True`, writes its pid, `os._exit(3)` -> exit 3 in under 10 s, grandchild
  ALIVE, killed in finally); `test_cap_from_escaped_holder_after_exit` (child Popens with
  `start_new_session=True` a `bash -c 'sleep 0.5; head -c 52428801 /dev/zero'`, then `os._exit(3)` ->
  97 in under 5 s, stderr has `output cap`; a traceback today, §0 D6; holder killed in finally).
  CHECK prints `held_pipe_secs=<n>` (< 10) for each and `escaped_cap_exit=97`.
  SEEDS: (a) `GRACE_S = 2.0` -> `3600.0` -> the held-pipe tests time out (red by
  `subprocess.TimeoutExpired`, 10 s); (b) select timeout `0.2` -> `None` -> same time out (PR-6: with
  the handler installed, Python retries the interrupted select forever); (c) drop the killpg after grace
  -> group-member rows red (`grandchild_alive=1`); (d) `except OSError` -> `except ProcessLookupError`
  in both places -> the two escaped tests red (EPERM, D6); (e) grace return `status if status >= 0 else
  128 - status` -> `status` -> the 137 row red; (f) `child.poll()` added to the loop head -> no oracle
  at this scale (pid reuse); the chair confirms by `grep -c poll scripts/run_capture.py` = 1 (finally).
  Pre-flight: Librarian line 20 (#R01-CX-4), line 30 (#R01-V-B2, B3).
W7. Chair only, at close (R1-12): spec §9 rows per §6, Librarian entries R01-V3-1 to V3-4 and R01-N2,
  ledger R1-22 and R1-23 build notes, then the critic round (8a, 8b, 8c) with a fresh cycle cap.

## §3 Lanes

One lane: W1 to W6 touch `scripts/run.sh`, `scripts/run_capture.py`, `src/casefile/config.py`,
`tests/conftest.py`, `tests/test_run_sh.py`, `tests/test_config.py` and the new pair; W3 and W6 share
run_capture.py tests. Order W1, W2, W3, W4, W5, W6; one Sonnet run, one chair commit per item.

## §4 Test design

Alias table (19 rows; `$B` = tmp base, `$R` = root; every link made by the test; the `unreadable`
row chmod 000 restored in finally): `case-swapped-root` `/Users/davidskoranski/LEGAL-HARNESS/m`
(the module test uses `$B/Checkout` vs `$B/CHECKOUT`; a row asserts `samefile` first so a
case-sensitive disk fails loudly, as test_config.py:131 does); `symlink-root` `$B/lroot -> $R`, `$B/lroot/m`;
`symlink-root-bare` `$B/lroot`; `symlink-subfolder-case` `$B/lsub -> <case-swapped $R>/tests/fixtures`,
`$B/lsub/m`; `symlink-subfolder-bare` `$B/lsub`; `chain` `$B/c2 -> $B/c1 -> $B/lsub`, `$B/c2/m`; `loop`
`$B/loopA <-> $B/loopB`, `$B/loopA/m` (cannot-verify); `dotdot-after-missing`
`$B/nope/../../(enough)../$R/tc`; `dangling-into-checkout` `$B/dang -> <case-swapped $R>/no-such/x`,
`$B/dang/m`; `dotdot-after-symlink` `$B/lsrc -> $R/src`, `$B/lsrc/../m`; `relative` `relchk`;
`unreadable-ancestor` `$B/blocked (000)/m` (cannot-verify); `checkout-itself` `$R`; `trailing-slash`
`$R/`; `nfd-alias` `$B/Café -> $R` made with the NFC name, typed with the NFD name (`Café`),
`$B/Café/m`; `firmlink` `/System/Volumes/Data<$R>/m` (same `(st_dev, st_ino)` as `$R`, measured;
callers only: the module test substitutes a second symlink root alias); `hop-dotdot-through-link`
`<parent of $R>/hop -> $B/deep`, `<parent of $R>/hop/../<name of $R>/m` (outside: the kernel lands in
`$B`; callers make `hop` beside the real checkout in `/Users/davidskoranski`, removed in finally; not
writable -> the row fails loudly, never skips); `outside-existing` `$B/out/ok`; `outside-new` `$B/out/new/deeper`.
Expected: 13 inside, 2 cannot-verify, 1 relative, 3 outside. Prototype result: all 19 right on 3.9,
3.12 and 3.14 with the two spellings (§0 D5). Wrapper caller: 20 runs (the `relative` row twice).

D12 branch table (test name, file; NEW marks this round):
96 `test_no_command_exits_96` NEW (W4) | 95 inside: `test_toolchain_inside_checkout_refused` (3 rows,
test_run_sh.py:148) + `test_toolchain_alias_table` NEW + `test_toolchain_exported_child_symlink_refused`
NEW | 95 cannot-verify: alias rows `loop`, `unreadable-ancestor` NEW + `test_toolchain_guard_unavailable_exits_95`
NEW (3 PATHs, V3-4) | 98 mktemp: `test_run_sh[capture-failure]` (:47) | 98 open:
`test_python_capture_open_failure` (:119) | 98 write: `test_capture_write_failure_exits_98` (:179) | 98
bad dir arg: `test_capture_directory_required` (:130) | 97: `test_run_sh[overflow,stderr]` (:44, :48),
`test_cap_terminates_sleeping_child` (:73), `test_cap_kills_grandchild_in_group` NEW (W5),
`test_cap_from_escaped_holder_after_exit` NEW (W6) | 126: `test_nonexecutable_command_relays_126` (:110)
| 127: `test_missing_command_relays_127` (:102) | child code: `test_run_sh[child-exit,sigkill]` (:45,
:49) | held pipe (N2): `test_pipe_held_by_group_member_bounded` (2 rows), `test_pipe_held_by_escaped_process_bounded` NEW (W6).

Regression set: `scripts/run.sh pytest -q` green with count 192 plus the new tests (the chair records
the exact number); `scripts/run.sh python -m casefile.gate` prints `0`; `scripts/run.sh pytest -q -s
tests/test_stage1_exit.py` -> `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`. Every seed in §2 run by
the chair after the builder, restored by `cmp` and `git diff --quiet`, before the commit. Every CHECK
carries pytest's own status (`pytest_exit=`, no pipe) and prints one failing number.

## §5 Risks with tripwires

- R1. Fresh checkout before `uv sync`: run.sh must still work with only a system python3. Tripwire:
  `env -i HOME=$HOME PATH=/usr/bin:/bin CASEFILE_TOOLCHAIN=<tmp> scripts/run.sh /usr/bin/true` exits 0
  (3.9 runs the guard and run_capture.py; the latter already runs on 3.9: verified `exit 98` usage line
  under `/usr/bin/python3 -I`). Add as `test_run_sh_on_system_python_only` if `/usr/bin/python3` exists;
  on a Mac without the CLT this is §7 Q16. W3's no-python3 PATH case covers the other side.
- R2. A refused run must create nothing inside the checkout. Tripwire: W3's os.walk snapshot equality on
  every alias and child row (git status cannot see an empty directory or a new file under an ignored
  one, .gitignore:61 and :64), plus the existing `assert not (ROOT / "invented-toolchain").exists()`.
- R3. Python 3.14 silent resolve and 3.9 syntax. Tripwire: W1 runs the CLI under every interpreter found; `py39_syntax=ok`; `imports=os,sys,errno`.
- R4. The grace kill could cut a legitimate same-group helper that outlives the child. Tripwire: full
  suite, gate and stage 1 exit test stay green through the wrapper (pytest's fake servers are stopped by
  their tests); any new `pipe stayed open` line in the chair's runs is a finding, not noise.
- R5. Guard cost on every run.sh call (one interpreter start) and the 0.2 s select wake. Tripwire: `time
  scripts/run.sh true` under 0.5 s; the suite's wall time within 20 percent of 12.2 s.
- R6. Interpreter hygiene. `-I` excludes the script directory and ignores `PYTHONPATH` on 3.9, 3.12 and
  3.14 (measured: `sys.path[0]` is the stdlib zip under `-I`, the script's directory without it), and
  os, sys and errno are builtin or frozen, so no file can shadow them: no executable seed for `-I`; the
  tripwire is `imports=os,sys,errno` plus W3(f). Verdict provenance IS executable: the token, three PATHs.
- R7. Sandbox: chmod 000 and `start_new_session` work inside it (verify3 and this session); socket
  tests need Q18 of the ledger (R1-15), unchanged. Codex's runs show 5 socket failures (R01-P-1); the chair re-runs.
- R8. The chair's uncommitted ledger and owner-question edits must survive the builder: the builder is
  told not to touch `.workflow/LEDGER.md`, `docs/loop/*`, `Librarian.md`, `docs/spec.md`.
- R9. `killpg` semantics on macOS (EPERM on a zombie-only group, §0 D6). Tripwire: W6 seed (d), `test_cap_from_escaped_holder_after_exit`.
- R10. Trailing-newline folder names: `$(...)` strips them (run.sh:3, :4, :33). Measured: `printf '%s'
  "$ROOT" | tail -c 1` is `s`; the checkout is named by D9. Not guarded (outside R1-22, R1-23); §8 PR-4.

## §6 Contradictions with the spec (each a §9 amendment, chair ruling pending veto)

- D12 (spec.md:220): says "95 toolchain inside the checkout" but run.sh:9, :13, :17 already exit 95 for
  "cannot verify"; no order of branches; silent on a held pipe. Amend: "exit 96 no command, then 95
  toolchain inside the checkout or not verifiable (D24), then 98 capture failure, 127 not found, 126 not
  executable, 97 cap hit (process group killed), else the child's code (a signal as 128 + n); after the
  child exits the wrapper reads at most 2 s more, then kills the group (best effort) and returns the
  child's code (a process that left the group is not reached)". Date 2026-10-26 (V3-2 to V3-4, N2).
- D13 (spec.md:221): "[paths].matters required and outside the checkout" does not say by identity or what
  an unverifiable path does. Amend: "outside the checkout by identity (D24); absolute after `~`
  expansion; a path that cannot be verified, or a `~` that cannot be expanded, is refused (ConfigError, exit 2)".
- D23 (spec.md:231): `CASEFILE_TOOLCHAIN` override unqualified. Amend: "the override (taken against the
  current directory when not absolute, as today) and its `python`, `cache`, `venv` and `venv/bin`
  children are checked by identity (D24) before any uv call". No absolute-only rule (M8).
- D24 (new): "`src/casefile/pathguard.py`: the one place that decides whether a path is inside the checkout,
  by filesystem identity (st_dev, st_ino) of every existing ancestor of the typed and real spellings;
  stdlib only, python3 >= 3.9, used by config.py and scripts/run.sh; verdicts outside, inside,
  cannot-verify, relative; CLI takes one root and one or more paths, prints one `pathguard <verdict>
  <detail>` line, exits 0, 10, 11, 12". §8b's own D12 to D16 are untouched (owner question 15).

## §6b Privacy

All aliases are made under a pytest tmp_path with invented names, except the `hop` link made beside the
checkout and removed in finally; targets inside the checkout are `tests/fixtures`, `src` and non-existent
names; no fixture file of a forbidden format; the chmod 000 folder is restored in `finally`; the os.walk
snapshot proves no residue. Scratch probes live under `$TMPDIR` only. No real matter, name or record.

## §7 Owner-only questions (appended to docs/loop/questions-for-owner.md)

16. On the Studio, will a `python3` be on PATH before `uv sync` (Xcode Command Line Tools installed, or a
    python.org build)? `scripts/run.sh` needs one for the path guard and the capture stage before the
    venv exists; without one it exits 95 "cannot verify". Interim: assumed yes; the setup guide (stage 9)
    lists it as a prerequisite.
17. When a job's child exits but a background process it started still holds the output pipe, may the
    wrapper kill that process group after 2 seconds and return the child's code (so no run can hang on a
    stray server)? A process that detached itself is not reached. Interim: yes, 2 seconds, in D12.
18. `scripts/run.sh` puts its capture directory under `${TMPDIR:-/tmp}` (run.sh:33) and removes it when
    the run ends (run_capture.py:66). If TMPDIR were ever set to a folder inside the checkout, captured
    output would briefly live there. Should the wrapper refuse such a TMPDIR (a new limit, D12), or is
    "TMPDIR is never inside the checkout" a setup-guide rule? Interim: no new limit; the setup guide says
    it; the test suite's TMPDIR is outside (sandbox).

## §8 Codex dispositions (review `.workflow/scratch/round01r-brief-codex.md`; one row each)

| PR | Disposition | Evidence and change |
|---|---|---|
| PR-1 | ACCEPTED | run.sh:30 exports `$TOOLCHAIN/python`, `/cache`, `/venv`, :31 prepends `/venv/bin`, :4 appends `basename "$ROOT"`. §1.1 CLI takes many paths; §1.4 passes the five strings; W3 child test; §0 D3 and §4 note the judged path. |
| PR-2 | ACCEPTED in part | §1.1 and §1.3: classify returns the realpath it walked and config stores that (config.py:139 stored a second computation). The check-then-use race itself is REJECTED: `grep -n -i -E 'threat|adversar|attacker' docs/spec.md` finds nothing; R1-22 (LEDGER.md:226) asks for alias refusal, not race-free writes; one attorney's Mac (CLAUDE.md:3). |
| PR-3 | ACCEPTED | run.sh:35 `exec python3` via PATH. §1.4: the verdict is a stdout token `pathguard outside`, so a shim that exits 0 and prints nothing is 95; W3 adds the `exit 0` shim PATH. |
| PR-4 | REJECTED | Measured `ROOT="$(cd -P scripts/.. && pwd -P)"; printf '%s' "$ROOT" \| tail -c 1 \| od -c` -> `s`; the checkout is named by D9 (`Legal-Harness`) on the owner's disk; run.sh:3 is outside R1-22 and R1-23 (LEDGER.md:226 to 231). Recorded as §5 R10. |
| PR-5 | OWNER | run.sh:33 `mktemp -d "${TMPDIR:-/tmp}/..."`, run_capture.py:24 opens `out`, :66 removes the directory. Whether to refuse a TMPDIR inside the checkout is a new limit (M8): §7 Q18, appended verbatim. The header's claim is reworded. |
| PR-6 | ACCEPTED | §1.8: select timeout is finite (0.2 s) while the child runs; a SIGCHLD record replaces `poll()`; W6 seed (b) `None` -> time out. |
| PR-7 | ACCEPTED | subprocess.py:1990 `waitpid(WNOHANG)` reaps; `os.waitid` absent on the 3.9 and 3.12 builds here (measured, §0 D2). §1.8: no `poll()` in the loop, the leader stays a zombie until after `killpg`; W6 seed (f) grep. |
| PR-8 | ACCEPTED | run_capture.py:57 normalises; §1.8 grace path returns `status if status >= 0 else 128 - status`; W6 `kill -KILL "$$"` row -> 137, seed (e). |
| PR-9 | ACCEPTED | Measured stronger than reviewed: `os.killpg` on the zombie-only group raises `PermissionError` (EPERM) on 3.9, 3.12, 3.14 (§0 D6), so run_capture.py:51 tracebacks today. §1.8 `except OSError` in both branches; W6 `test_cap_from_escaped_holder_after_exit` (prototype: 97 at 0.54 s), seed (d). |
| PR-10 | ACCEPTED | Measured: `os.path.realpath("$B/nope/../../../<R>/tc")` -> `<R>/tc` on 3.9, 3.12, 3.14 (`nope` missing); with spellings (typed, real) every row right. `normpath` dropped (§1.2); W1 seed (a) relisted by measurement, (b) is now "add normpath". |
| PR-11 | ACCEPTED | Measured: `<parent>/hop -> $B/deep`, path `<parent>/hop/../Checkout/m` is `inside` with normpath and `outside` without, on all three. Row `hop-dotdot-through-link` added (§4) as the seed for (b). |
| PR-12 | ACCEPTED | D23 (spec.md:231) is unqualified and run.sh:4 and :21 (`-ef`) take a relative override against cwd today; `relative` -> 95 was a new limit (M8). §1.4 joins to `$PWD`; §6 D23 reworded; W3 `relative` row runs with two cwds, seed (d). §1.10 corrected. |
| PR-13 | ACCEPTED | Measured `python3 -I script.py` -> `sys.path[0]` is the stdlib zip on 3.9, 3.12, 3.14 (script dir without `-I`); R6 rewritten, the fake `os.py` seed and W3(c) dropped (os, sys, errno are builtin or frozen); provenance is tested by the token and the three PATH cases instead. |
| PR-14 | ACCEPTED | Every CHECK now redirects to `$TMPDIR/wN.log`, prints `pytest_exit=$?` and greps one `*_wrong=` line (§2, §4). |
| PR-15 | ACCEPTED | .gitignore:61 `.workflow/scratch/`, :64 `__pycache__/`. W3 snapshot is an os.walk of every entry (806 entries, 0.015 s measured); seed (e) makes an empty ignored directory -> `created=1`; §5 R2, §6b. |
| PR-16 | ACCEPTED | run_capture.py:28 `stderr=subprocess.STDOUT`, :47 forwards to wrapper stdout; test_config.py:193 checks `stdout + stderr`. W2 oracle corrected. |
| PR-17 | ACCEPTED in part | W3 adds the no-python3 PATH (shell 127 -> 95) and the `exit 0` shim. A version floor is REJECTED (M8, §1.10): a python that cannot run the guard prints no token and is 95; one that runs it right is right; the guard's syntax floor is 3.9 by `py39_syntax=ok`. |
| PR-18 | ACCEPTED in part | Rows `trailing-slash`, `nfd-alias`, `hop-dotdot-through-link` added; `test_root_argument_aliases` (symlink, case and `/var` vs `/private/var` roots) in the module test, since config.py:125 and run.sh:3 fix the callers' root. Tilde rows REJECTED: config.py:124 expands `~` before the guard (test_config.py:82) and run.sh never expands it, as today. |
| PR-19 | ACCEPTED | pathlib.py:1406 raises RuntimeError; cli.py:45 catches only ConfigError. §1.3 uses `os.path.expanduser` and refuses an unexpanded `~` with ConfigError; W2 test and seed (d). |

Counts: 17 accepted (3 in part), 1 rejected, 1 owner. N2: grace-kill kept and redesigned (§1.8), since
all four high findings on it closed cleanly in the prototype (§0 D6).
