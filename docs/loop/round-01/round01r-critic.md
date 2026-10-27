# Round 1 re-brief: output critic

OUTPUT CRITIC 7/10 · high 0 · med 2 · low 4

Critic: fresh Opus 5.5, no build context. Tip c729336, branch loop/round-01. All probes invented, under $TMPDIR (`/tmp/claude-501/oc-probe`), removed or killed after use. Read: CLAUDE.md, spec §5, §7 stage 1, §9 D12, D13, D23, D24, LEDGER `## Clarified`.

## Findings

**F1 (med). Closing the Terminal window (SIGHUP) or a SIGTERM to the wrapper leaves the job running and a copy of its output on disk.**
- Command: `scripts/run.sh bash -c 'echo INVENTED-PAGE-TEXT Jane Roe DOB 01/01/1970; sleep 20'`, then `kill -HUP <wrapper pid>` (same with `-TERM`).
- Output: wrapper exits 129 (143 for TERM) with no message; the child is still alive (`kill -0` succeeds; a tick loop kept growing 24 -> 38 lines after the wrapper was gone); `/tmp/claude-501/casefile-run.eysZxj/out` still holds `INVENTED-PAGE-TEXT Jane Roe DOB 01/01/1970`.
- Wrong: the child runs in its own session (`start_new_session=True`), so a hangup reaches only the wrapper, whose default SIGHUP and SIGTERM actions skip the `finally` that kills the group and removes the capture folder.
- Breaks: D12 (the wrapper owns the child's group and cleans up; here a running job outlives it, out of reach of the cap) and pillar privacy (page text left in a temp folder). Ctrl-C (SIGINT) does run the cleanup.
- Repro: run `/tmp/claude-501/oc-probe/drive.py`-style driver: spawn the wrapper with the child above, sleep 1, `os.kill(wrapper, SIGHUP)`, then check the child pid and `ls $TMPDIR/casefile-run.*`. 11 older `casefile-run.*` folders from earlier sessions were already in $TMPDIR (19:49 to 20:25).

**F2 (med). A config file kept outside the checkout (e.g. `~/config.toml` with `matters = "~/Cases"`) puts the run log in that folder and sends the attorney to fix the wrong thing.**
- Command: `HOME=$P/home CASEFILE_TOOLCHAIN=~/.casefile-dev scripts/run.sh casefile doctor` with `$P/home/config.toml` holding only `[paths] matters = "~/Cases"`.
- Output: `doctor folders FAIL .../home/playbook: [Errno 2] No such file or directory: '.../home/playbook/.doctor-write-72926' | do: check the configured folder paths and write access`; `doctor playbook FAIL .../home/playbook: playbook directory not found | do: correct the playbook files and rerun doctor`; `doctor runlog_schema PASS`, and `$P/home/state/runlog.sqlite` now exists.
- Wrong: `state` and `playbook` default to folders beside the config file, so the doctor silently creates a run log in the home folder and tells the attorney to "correct the playbook files" when the files are fine and only `[paths].playbook` is missing.
- Breaks: D14 (state, the run log, lives in the checkout, gitignored). Also seen with a typo'd matters config in $TMPDIR: `$P/state/runlog.sqlite` created.
- Repro: as above; `casefile config show` prints `paths.state = ".../home/state" (source=default)`.

**F3 (low). The toolchain refusal does not say which path it judged or what to do.**
- `CASEFILE_TOOLCHAIN=/Users/davidskoranski scripts/run.sh true` and `CASEFILE_TOOLCHAIN='~/.casefile-dev' scripts/run.sh true` both print `run.sh: toolchain must be outside the checkout; exit 95`. Exit 95 is right (D12, D23), but the attorney typed a folder that is outside: the wrapper appends `legal-harness` (giving the checkout itself) or reads a quoted `~` as relative to the current folder. Naming the resolved path and the fix ("use an absolute path; the checkout name is added") would make it self-explaining.

**F4 (low). Ctrl-C prints a Python traceback.** Driver sends SIGINT to the wrapper during `bash -c 'for i in $(seq 1 100); do echo line $i; sleep 0.1; done'`: stderr ends `File ".../scripts/run_capture.py", line 66, in main ... KeyboardInterrupt`, exit 130. Cleanup is correct (child gone); the message is not attorney-readable.

**F5 (low). Downstream "blocked" lines point at the wrong fix.** With a missing playbook: `doctor runlog_job FAIL blocked by context | do: rerun doctor; if it repeats, reload the model`. The root cause is the playbook, not the model (doctor.py `next_step` uses the immediate blocker, not the root one).

**F6 (low). `~nosuchuserxyz/Cases` gives `cannot expand ~ in [paths].matters: no home directory`** (exit 2, correct per D13) though the attorney has a home; the real cause is an unknown user name after `~`.

## Owner questions

- Q-A: `matters = "~"` and `matters = "/"` load (`casefile config show` exit 0) although the checkout sits inside them. D24 judges only "inside the checkout"; should a matters folder that contains the checkout be refused too?
- Q-B: Ctrl-Z stops only the wrapper (child in its own session keeps running: ticks 7 -> 17 while stopped). Resume works (`exit 7`, all output). Is "pause" expected to pause the job?

## Good enough to keep

- Exit codes all match D12: no args 96, `casefil` 127 `command not found: casefil`, `./README.md` 126, toolchain at checkout, `..`, symlink alias, `.`, `tools`, `nope/../../...` all 95, locked folder 95 `cannot verify`, child exit 4/7 carried, child killed by TERM 143, helper holding the pipe: exit 4 after 2.1 s with a clear message.
- Config (D13): symlink alias to the checkout and to `tests/`, `$R/../legal-harness/Cases`, relative `Cases` all exit 2 with plain messages; `~/Cases`, trailing slash, outside folders exit 0. Doctor turns each into `config FAIL ... | do: correct the config file` and a typo'd matters folder into `matters folder not found`.
- `scripts/run.sh python -m casefile.gate`: 223 passed, five rows PASS, exit 0. `scripts/run.sh pytest -q -s tests/test_stage1_exit.py`: 2 passed, `fails={'ocr'} test_jobs=1`, exit 0. Nothing left in `git status`.
