# casefile: loop ledger

Chair: the primary Claude Code session for each round. Loop: create (Fable brief, Codex review, Fable
revision) → build (Opus orchestrates, Sonnet codes) → critic (Codex code review, output critic, blind
verifier) → close, one round per branch and per session. Owner decisions are binding; see `## Clarified`.
Seeded 2026-10-25; round 1 opened 2026-10-25 on `loop/round-01`.

## Project
- Spec: docs/spec.md (canon). Pillars §1 · decisions table §9 · open questions §10 · roadmap with an
  exit test per stage §7 · as-built §11.
- App: casefile, a fixed-workflow case system for one attorney, run locally on a Mac Studio. Python
  3.12, FastAPI and plain HTML, Ollama native API, SQLite run log, append-only JSON case file.
- Harness (round 1 builds and measures these): every run through `scripts/run.sh` (50 MB cap, exit 97);
  tests `scripts/run.sh pytest -q`; gate `scripts/run.sh python -m casefile.gate` prints 0;
  benchmark `scripts/run.sh casefile bench --matters tests/fixtures/matters`; full run
  `scripts/run.sh casefile demo tests/fixtures/matters/<matter>`; a stand-in model server in
  `tests/fakemodel/` (recorded answers, plus truncated, malformed and forbidden ones on demand);
  page screenshots with Playwright.
- Checks: a check prints the one number that fails it, exits non-zero on FAIL, and has been proven
  red on a seeded defect before its pass counts.
- Finish line (owner): spec §7 stages 1 to 8 done and verified in the loop; then stage 9 on the Studio.
- Standing freezes: none.
- Privacy: no real client record, name or fact in any loop session; fixtures are invented.
- Regression baselines: set in round 2.
- Records: Librarian.md · docs/loop/round-NN/ · docs/loop/agent-log.md · docs/loop/questions-for-owner.md ·
  docs/loop/tuning-questions.md · docs/loop/HANDOFF.md · docs/loop/next-round.md.

## Standing rules digest
- Spec is canon; every design change goes in spec §9.
- One round per session; Remote Control on; handoff and next-round prompt written at close.
- No client data in any session or commit.
- Every check proven red on a seed before its pass counts; never lower a threshold or exempt by name.
- `main` pushed only on the owner's word (`git push origin main`).
- Prose has no em or en dashes.

## Clarified
- Q1: scope? -> the case system in spec §2 and §7, built in stage order.
- Q2: done means? -> spec §7 stages 1 to 8 pass their exit tests and the verifier's V. in the loop;
  stage 9 (real benchmark on the Studio) is run by the owner.
- Q3: freezes? -> none.
- Q4: where does work land? -> branch per round `loop/round-NN`, merged to main only after V.
- Q5: stall rule? -> three verify-fix cycles per round, then discard and re-brief; two stalled rounds
  in a row stop the loop and report to the owner.
- Q6: check rule? -> every new check, test or gate goes red on a seeded defect before its pass counts.
- Q7: rulings while the owner is away? -> the chair, by the spec's pillars, logged as pending veto.
- Q8: sessions (owner, 2026-10-25)? -> a fresh session for each round, automatically on Remote
  Control, with a critic round before every close.
- Q9: client data (owner, 2026-10-25)? -> never in any build session; invented test matters only.
- Q10: tiers (owner, 2026-10-25)? -> gdd-loop's: Fable writes and revises the brief; Codex gpt-6.1-sol
  reviews plan and code; Opus 5.5 orchestrates, critiques outputs, verifies; Sonnet 5.5 writes all code.
  Builders may delegate to Sonnet children only.
- Q11: machine (owner, 2026-10-25)? -> this Mac is a dev Mac, not the Studio. Install Python 3.12
  project-local with uv only; no Ollama, no Tesseract, no brew. The stand-in model server replaces the
  model. `casefile doctor` reports OCR as FAIL (never skipped) until stage 3.
- Q12: first playbook (owner, 2026-10-25)? -> `rules.toml` holds the four firm rules in spec §4; every
  other playbook entry is an invented test fixture marked SAMPLE. Practice content is the owner's.
- Q13: additional instructions (owner, 2026-10-25)? -> none; proceed.
- Q14: builder tier (owner, 2026-10-25, supersedes Q10's coding tier for cost)? -> Codex gpt-6.1-sol
  writes all code, via the local `codex exec` CLI with `-s workspace-write` in the repo (or a worktree),
  never with network or outside-repo write. Opus still orchestrates and re-runs every CHECK and seed;
  Codex still does the plan and code reviews (independence reduced; the blind Opus verifier carries it).
- Q15: critic timing (owner, 2026-10-25)? -> no code review until the night of 2026-10-26. This session
  runs brief, plan review, revision and build, then stops before the critic round with round 1 unmerged
  on `loop/round-01`. The next session runs the critic round (8a to 8c) and close; the owner may
  change tiers then.
- Q16: firm rule 5 (owner, 2026-10-25, owner question 4)? -> checked on outputs only, never on the
  records being read. Outputs never name the exam as a DME or IME in any form: block "DME", "IME",
  "independent medical examination" and "defense medical examination" (whole words, any case); always
  "the report".
- Q17: matters folder (owner, question 3)? -> outside the repo checkout (e.g. ~/Cases), set in config.toml.
- Q18: local binding (owner, question 6)? -> yes: `sandbox.network.allowLocalBinding: true` in the
  project's `.claude/settings.json`.
- Q19: Ollama on the Studio (owner, question 7)? -> not decided; build for the login-user app case,
  question stays open.
- Q20: model tag (owner, question 2)? -> `qwen3.8:27b`, set in config.toml.
- Q21: Bates format (owner, question 5)? -> letters plus digits: `[A-Z]{1,8}[ -]?\d{4,}`, configurable.
- Q22: tiers for round 1 session 2 (owner, 2026-10-26)? -> code review Codex gpt-6.1-sol (high);
  output critic and blind verifier fresh Opus 5.5, one each; fixes written by Codex gpt-6.1-sol
  (as Q14), chair commits and re-runs seeds.
- Q23: cycle cap reached in round 1 (owner, 2026-10-26)? -> one extra fix cycle (exception to Q5),
  limited to B1b and B3, then one focused fresh re-verify; if that fails, discard per Q5.

## Round 1: stage 1 skeleton and harness (opened 2026-10-25)

- [~] R1-1. Build brief reconciled to the code at main `5a55b54`, a CHECK and seed per item, Codex
  reviewed, revised with dispositions. `.workflow/scratch/round01-build-brief.md`.
  deferred: chair at close
- [x] R1-2. `scripts/run.sh <cmd>`: caps combined stdout/stderr at 50 MB, exits 97 when the cap is hit,
  otherwise carries the child's exit code.
  Build note (chair re-run, not a tick): cap `exit=97 bytes=52428800`, child `3`, capture `98`; SEED `head -c "$CAP"` -> `exit=0`; restored by cmp.
  Verifier (blind, 2026-10-26, tip 9c25e8f): `scripts/run.sh bash -c 'head -c 52428801 /dev/zero | tr "\0" a' | wc -c` -> `52428800`, pipefail exit `97`, stderr `run.sh: output cap 52428800 bytes hit (child status -9); exit 97`; `bash -c 'exit 3'` -> `3`; exact cap -> `0`; no args -> `96`; `TMPDIR=/nonexistent/dir` -> `98`. SEED run_capture.py:32 `128 - status` -> `1`: `1 failed, 161 passed` (sigkill `(1, 0) == (137, 0)`), restored cmp 0.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): still holds: pipefail cap `52428800` bytes, exit `97`, `secs=0` with `sleep 30` after the overflow and with a background `sleep 30`; `bash -c 'exit 3'` -> `3`; exact cap -> `0`; no args -> `96`; `TMPDIR=/nonexistent/dir` -> `98`.
- [x] R1-3. Skeleton: Python 3.12 (uv, project-local), package `casefile`, console entry `casefile`,
  `scripts/run.sh pytest -q` green.
  Build note: `3.12.13 0.1.0`, `casefile 0.1.0`; isolation SEED (matters -> repo `Cases`) -> pytest exit 3 `test isolation failed`; restored by cmp, exit 0.
  Verifier (blind, 2026-10-26, tip 9c25e8f): `scripts/run.sh python --version` -> `Python 3.12.13`; `scripts/run.sh casefile version` -> `casefile 0.1.0` (venv `~/.casefile-dev/legal-harness/venv`, D23); `scripts/run.sh pytest -q` -> `162 passed in 9.82s`.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): `scripts/run.sh pytest -q` -> `184 passed in 10.40s`.
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): still holds: `scripts/run.sh pytest -q` -> `192 passed in 11.26s`, exit `0`.
- [ ] R1-4. Config: one config file with defaults and validation; an unknown key or bad value fails
  closed with a message, never a silent default.
  Build note: SEED unknown-key raise -> `continue` gave `4 failed, 21 passed`; restored green.
  Verifier (blind, 2026-10-26, tip 9c25e8f): REFUSED. Unknown key, bad type, low num_ctx, bad host, missing file, matters in checkout all exit 2 with a ConfigError (seed config.py:69 missing-file branch -> `3 failed, 159 passed`). But `[paths].matters = "/Users/davidskoranski/LEGAL-HARNESS/invented-matters"` (case variant of the checkout on case-insensitive APFS) -> `casefile config show` exit `0`, `paths.matters = "/Users/davidskoranski/LEGAL-HARNESS/invented-matters" (source=file)`: config.py:128 `is_relative_to(checkout)` compares case-sensitively. Fail open on D13/Q17. Blocking.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): REFUSED. B1 itself is fixed: `/Users/davidskoranski/LEGAL-HARNESS/invented-matters`, `Legal-Harness`, `LEGAL-harness/SRC/new/deeper`, `tests/../INVENTED/x`, a symlink to the checkout (plain or case-swapped), `/System/Volumes/Data/...` firmlink, `~/legal-harness/invented` all exit `2` `must be outside the checkout`; relative `invented-matters` and `./invented-matters` exit `2` `must be an absolute path`; unknown key, unknown table, bad type, num_ctx 32768, host localhost/0.0.0.0/https//v1, no matters, matters int, missing file all exit `2` with a ConfigError. But a symlink to a case-swapped SUBDIRECTORY of the checkout loads: `$SCRATCH/aliasFix -> /Users/davidskoranski/LEGAL-HARNESS/tests/fixtures`, `matters = "$SCRATCH/aliasFix/invented-matter"` -> `casefile config show` exit `0`, `paths.matters = "/Users/davidskoranski/LEGAL-HARNESS/tests/fixtures/invented-matter" (source=file)` (also `aliasSrc -> .../Legal-Harness/src` exit `0`). config.py:129-131 walks the ancestors of the unresolved path and compares the resolved path by spelling. Fail open on D13/Q17. Blocking. Also SEED config.py:134 OSError raise -> `inside = False` stays `81 passed` (branch reachable: matters under a chmod 000 folder -> exit 2 `cannot verify`).
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): REFUSED. Config guard holds on 17 aliases: case-swapped checkout, symlink to root (plain and case-swapped), symlink to case-swapped subfolder, chains `chain2 -> chain1 -> .../Legal-Harness/tests/fixtures` and to root, relative symlink to `LEGAL-harness/src`, dangling symlink into `LEGAL-HARNESS/no-such-dir`, `tests/../INVENTED/x`, `$S/nope/../../../../../../Users/davidskoranski/legal-harness/inv`, `~/legal-harness/inv`, the checkout itself all exit `2` `must be outside the checkout`; relative and `./` exit `2` `must be an absolute path`; chmod 000 parent exit `2` `cannot verify ... [Errno 13]`; outside existing and new folders exit `0`. SEEDS config.py:132 drop `resolved` candidate `2 failed`; config.py:129 `resolved = matters` `2 failed`; cmp restored, `192 passed`. But (1) a symlink loop `loopA -> loopB -> loopA`, `matters = "$S/loopA/m"` -> exit `1`, traceback `RuntimeError: Symlink loop from '.../loopA/m'` at config.py:129 (pathlib raises RuntimeError, not OSError; fails closed but not exit 2 with a ConfigError). (2) Toolchain guard fails open on `..` after a missing component: `CASEFILE_TOOLCHAIN="$S/nope/../../../../../Users/davidskoranski/legal-harness" scripts/run.sh sh -c 'mkdir -p "$UV_PROJECT_ENVIRONMENT"'` -> exit `0` and created `/Users/davidskoranski/legal-harness/legal-harness/venv` (removed). Expected `95` (D12, D23). Both blocking (verify3 V3-1, V3-2). Other toolchain aliases (literal, case, symlink, case-swapped symlink, chain, `tests/..`, relative) exit `95`; locked folder `95` `cannot verify`; normal `0`.
- [x] R1-5. `playbook/rules.toml` with the four spec §4 firm rules, loaded and validated; each rule has a
  test with a forbidden output that goes red.
  Build note: SEED drop `re.IGNORECASE` (rules.py:59) -> `2 failed, 39 passed`; restored green.
  Verifier (blind, 2026-10-26, tip 9c25e8f): four rule ids loaded; `rules_red=9 of 9`, `good_clean=4 of 4`; probes "The IME found a normal gait." -> `['no-dme-ime']`, "Who retained the doctor?" -> `['no-hired-paid-retained']`, question "What treatment did you get and who paid the bills?" -> `['treatment-and-bills-apart']`, "Gait normal [cite p. 12]" -> `['bates-cites']` (unstamped `warning`). SEEDS rules.py:76 fullmatch->match `2 failed`; rules.py:61 unit skip off `2 failed`; rules.toml:43 drop bill pattern `4 failed`; all restored cmp 0. Non-blocking: "independent-medical-examination" and "defense medical-examination" (hyphens) -> `[]`.
- [x] R1-6. Playbook loader: entries carry rule, why, good example, bad example, date added, where
  learned (spec §6); malformed entry fails closed; a playbook version is computed. Entries other than
  rules.toml are invented and marked SAMPLE (Q12).
  Build note: lane B reports `refused=3 of 3`, `version_changed=1` with seeds red; chair did not re-run these two seeds.
  Verifier (blind, 2026-10-26, tip 9c25e8f): `casefile playbook show` -> `version=pb-8c41a5ae7727 entries=7` (4 rules + 3 SAMPLE); missing-why fixture -> exit 2 `missing field why`; unmarked fixture -> exit 2 `field sample: round 1 requires sample = true and rule starting SAMPLE:`; one byte appended -> `version=pb-959a6c383d9a`. SEEDS playbook.py:72 sample check off `3 failed`; playbook.py:109 duplicate id off `2 failed`; playbook.py:86 rules.toml guard off `1 failed`; restored cmp 0. Non-blocking: SEED cli.py:38 playbook error `return 2` -> `return 0` stays `162 passed` (CLI exit untested).
- [x] R1-7. Run log (SQLite): every run, card version, pages in, raw answer, failures, approvals
  (spec §5); records a test job.
  Build note: SEED `approvals_no_delete` -> `SELECT 1` gave `1 failed, 24 passed`; restored green.
  Verifier (blind, 2026-10-26, tip 9c25e8f): driven doctor x2 on stand-in: runs `(1, 'doctor', 'doctor.warmup', 'a48ba54e9a3e', 'pb-8c41a5ae7727', 'qwen3.8:27b', 0, ...)`, answers `(1, 'ok', 'stop', 21, 2, '{"model": ...')`, `DELETE FROM runs` -> `runlog is append-only`. SEEDS runlog.py:111 foreign_keys OFF `2 failed`; runlog.py:92 drop card filter `1 failed` (`assert 2 == 1`); doctor.py:142 status always failed `4 failed`; restored cmp 0.
- [x] R1-8. Stand-in model server `tests/fakemodel/`: Ollama native `/api/chat` shape; replays recorded
  answers; returns truncated, malformed or forbidden answers on demand.
  Build note: socket `test_http_roundtrip` 1 passed outside the sandbox; FAILS (not skips) inside it until the session restarts with Q18's setting.
  Verifier (blind, 2026-10-26, tip 9c25e8f): over HTTP on 127.0.0.1: replay `'READY' stop ctx 65536`; truncated `'RE' length`; malformed `'{"facts": [{"page": 1,'`; forbidden `'The IME found no injury; ...retained by the employer.'`; short_context ps `8192`; empty `''`; unrecorded `404`; `/v1/chat/completions` `404`. SEEDS core.py:88 stream check off `2 failed`; core.py:46 short_context ctx `4 failed`; restored cmp 0. Note: mode `incomplete` is not in D18's list.
- [x] R1-9. `casefile doctor`: Ollama on 127.0.0.1 only, full context loaded, OCR works, folders
  writable; each check PASS or FAIL with a reason, none skipped; exit code carries the verdict.
  Build note: covered by the R1-11 run; doctor seeds are Codex's only (chair did not re-run).
  Verifier (blind, 2026-10-26, tip 9c25e8f): driven run, eight lines: `config PASS`, `folders PASS writable=3 of 3`, `playbook PASS version=pb-8c41a5ae7727`, `runlog_schema PASS schema=1 triggers=15 (counted)`, `ollama_loopback PASS addr=127.0.0.1:53510`, `context PASS context_length=65536`, `runlog_job PASS test_jobs=+1`, `ocr FAIL OCR not verified: tools unavailable (...) | do: install tesseract and ocrmypdf; expected until stage 3`; `doctor failed=1 of 8`, exit 1. SEEDS cli.py:32 drop doctor return `3 failed`; doctor.py:83 lsof error ignored `1 failed`; doctor.py:47 missing matters `1 failed`; restored cmp 0. Non-blocking: SEED doctor.py:152 `== 1` -> `>= 0` stays `162 passed`; with doctor.py:142 also seeded the doctor prints `runlog_job PASS test_jobs=+0` (only the exit test's own count catches it).
- [x] R1-10. Gate `scripts/run.sh python -m casefile.gate` prints 0 when green; includes the privacy
  check (PDF, Word or image outside `tests/fixtures/`, or anything under `Cases/` or `Bench/`, fails).
  Build note: gate prints `0`, exit 0 (rows pytest, privacy scanned=188, rules_selftest, playbook pb-e46d368e8caf, prose); SEED `docs/seed.pdf` -> `privacy FAIL offenders=1`, prints `1`, exit 1.
  Verifier (blind, 2026-10-26, tip 9c25e8f): `scripts/run.sh python -m casefile.gate` -> rows pytest, privacy `offenders=0 scanned=213`, rules_selftest, playbook, prose `dashes=0 files=57`, prints `0`, exit 0. SEED transient `state/probe-seed.HEIC` (ignored), `Bench/invented-notes.txt`, `docs/probe-seed.md` with U+2013 -> `gate privacy FAIL offenders=2 scanned=216`, `gate prose FAIL dashes=1 files=58`, prints `2`, exit 2; removed. SEED privacy.py:11 drop `--others` `4 failed`; restored cmp 0. Non-blocking: SEED gate.py:37 drop `false_hits == 0` stays `162 passed`.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): gate rows pytest `exit=0`, privacy `offenders=0 scanned=218`, rules_selftest `misses=0 false_hits=0`, playbook `version=pb-00be6eb62752`, prose `dashes=0 files=59`, prints `0`, exit `0`.
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): still holds: gate rows pytest `exit=0`, privacy `offenders=0 scanned=223`, rules_selftest `misses=0 false_hits=0`, playbook `version=pb-00be6eb62752`, prose `dashes=0 files=61`, prints `0`.
- [x] R1-11. Stage 1 exit test (spec §7): `casefile doctor` runs and the run log records a test job,
  driven end to end through `scripts/run.sh`.
  Build note: `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`, 1 passed via scripts/run.sh outside the sandbox. Full suite `98 passed`.
  Verifier (blind, 2026-10-26, tip 9c25e8f): `scripts/run.sh pytest -q -s tests/test_stage1_exit.py` -> `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`, `stage-control exit=1 verdicts=8 fails={'ocr'} expected={'ocr'} test_jobs=1`, `2 passed`; socket server stopped by the test.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): `scripts/run.sh pytest -q -s tests/test_stage1_exit.py` -> `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`, `stage-control exit=1 verdicts=8 fails={'ocr'} expected={'ocr'} test_jobs=1`, `2 passed in 0.75s`. Driven doctor on the stand-in (port 18434): eight lines config, folders `writable=3 of 3`, playbook `pb-00be6eb62752`, runlog_schema `schema=1 triggers=15`, ollama_loopback `addr=127.0.0.1:18434`, context `context_length=65536`, runlog_job `test_jobs=+1` (again `+1` on a second run), ocr `FAIL ... | do: install tesseract and ocrmypdf; expected until stage 3`; `doctor failed=1 of 8`, exit `1` (R1-9 holds).
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): still holds: `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`, `stage-control exit=1 verdicts=8 fails={'ocr'} expected={'ocr'} test_jobs=1`, `2 passed in 0.78s`.
- [~] R1-12. Spec §9 rows for this round's rulings, §11 as-built updated; Librarian, agent log,
  round report under `docs/loop/round-01/`.
  deferred: chair at close
## Discoveries during round 1 (appended, not yet scheduled)

- [ ] R1-13. Brief CHECK wording: R1-2 CHECK 1 needs caller `pipefail` (without it prints `FAIL exit=0`);
  R1-2 second SEED (mktemp) is masked by the later unreadable-capture guard, which also returns 98 (two
  guards mask each other: isolate each); R1-4 missing-file shell CHECK prints PASS under its seed; R1-7
  trigger seed leaves `test_jobs=1` (Codex added a status-filter seed). -> verifier checks each.
  Verifier (blind, 2026-10-26, tip 9c25e8f): REFUSED (one of four parts). (a) without pipefail the overflow pipeline exits `0`, with pipefail `97`: reproduced. (b) mktemp guard now isolated: SEED run.sh:8 drop `|| {...}` -> `capture-failure (1, 0)`, red (it also wrote a stray `out` in the cwd, removed). But the second guard is not: SEED run_capture.py:35 `return 98` -> `return 0` stays `162 passed`; `scripts/run.sh invented-no-such-cmd` -> `capture stage failed ... exit 98` on the tip, untested. Blocking. (c) SEED config.py:69 missing-file branch removed -> `3 failed, 159 passed` (message falls to `cannot load config`): red. (d) SEED runlog.py:92 card filter -> `assert 2 == 1`: red.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): REFUSED. (a) holds: without pipefail the overflow pipeline exits `0`, with pipefail `97`. (b) B2 fixed: SEED run_capture.py:13 `return 98` -> `return 0` -> `5 failed, 13 passed`; SEED run.sh:29 drop mktemp `|| {...}` -> `test_run_sh[capture-failure]` red (falls to the is_dir guard, told apart by message); run_capture.py:17 is_dir guard drop -> `2 failed`; 127 and 126 branches each red (seeds 127->126, 126->1, 126->127, FileNotFoundError->IsADirectoryError: `1 failed` each); probes missing `127`, non-executable file `126`, directory `126`, child `3`, child SIGTERM `143`. But the capture WRITE guard is not isolated: SEED run_capture.py:40-41 `return capture_failed(exc)` -> `pass` stays `81 passed`, while the branch is live (`ulimit -f 1`, 200000 bytes -> `[Errno 27] File too large; exit 98`), and a short write is ignored (`ulimit -f 1`, 4096 or 65536 bytes -> exit `0`). Blocking (same class as B2). (c) SEED config.py:69 missing-file branch -> `3 failed, 22 passed`: red. (d) SEED runlog.py:92 card filter -> `assert 2 == 1`: red.
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): REFUSED. Probes all per D12: no args `96`; cap `52428800` bytes, exit `97`, `secs=0` with `sleep 30` after overflow; `TMPDIR=/nonexistent/dir` `98`; `ulimit -f 1` 200000 and 4096 bytes `98` `[Errno 27] File too large` (B3 fixed), 400 bytes `0`; toolchain in checkout `95`; non-executable file and directory `126`; missing `127`; child `3`; background grandchild after overflow killed. SEEDS RED (cmp restored each): run.sh:23 `exit 95`->`true` `5 failed`; run.sh:19 drop physical `2 failed`; run.sh:34 mktemp `exit 98`->`0` `1 failed`; run_capture.py:13 `7 failed`; :32 127->126 `1 failed`; :35 126->1 `1 failed`; :55 `return 97`->`0` `3 failed`; :57 child code `13 failed`; :44 skip short write `2 failed`. GREEN (findings): run.sh:32 `exit 96`->`exit 0` `192 passed` (no args then exits `0`; 96 untested); run_capture.py:51 `os.killpg`->`child.kill()` `192 passed` while a background grandchild survives the cap (`grandchild=ALIVE`, tip `dead`; D12 group kill untested); run.sh:17 cannot-verify `exit 95`->`physical=/` `192 passed` while a chmod 000 toolchain parent then exits `0` (tip `95`). Blocking (same class as B2, B3).
- [x] R1-14. Codex workspace-write cannot write `.git` (`index.lock: Operation not permitted`); the chair
  commits every Codex item after re-running its CHECKs. -> process note, Librarian.
  Verifier (blind, 2026-10-26, tip 9c25e8f): ticked on reading the record: agent-log row 4 `uncommitted (sandbox denies .git), chair committed`; every build commit 7fd2913..9d05301 is by the chair. Process note; Librarian entry is R1-12's.
- [x] R1-15. Q18's `allowLocalBinding` did not take effect mid-session; socket tests ran outside the
  sandbox. -> confirm in a fresh session.
  Note (chair, session 2, fresh session): `scripts/run.sh pytest -q -m socket` inside the sandbox -> `5 passed, 93 deselected`; the setting takes effect at session start.
  Verifier (blind, 2026-10-26, tip 9c25e8f): fresh session, inside the sandbox: `scripts/run.sh pytest -q -m socket` -> `5 passed, 157 deselected in 2.76s`.
- [x] R1-16. Toolchain inside the checkout broke the strict privacy row (4 idlelib PNGs under `.uv/`);
  fixed by D23 (commit 9d05301), seed `toolchain_inside_repo=1` red per Codex. -> verifier re-seeds.
  Verifier (blind, 2026-10-26, tip 9c25e8f): SEED run.sh:5 `UV_CACHE_DIR="$ROOT/.uv/cache"` -> `AssertionError: toolchain_inside_repo=1`, restored cmp 0; ignored-file scan proven by `state/probe-seed.HEIC` -> privacy offender (R1-10).
- [x] R1-17. Process slip: the chair committed loop records (3e12678) while a Codex lane was live in the
  main tree (catalog #53); disjoint files, no conflict. -> Librarian.
  Verifier (blind, 2026-10-26, tip 9c25e8f): ticked on reading the record: `git show --stat 3e12678` touches only ledger, spec, loop records and `.claude/settings.json`, no src or tests. Process note.
- [x] R1-18. Built in four Codex batches (A1, A2+B, A3, F1) instead of one run per item, to save chair
  usage. -> process note.
  Verifier (blind, 2026-10-26, tip 9c25e8f): ticked on reading the record: agent-log rows 4 to 8 (A1, A2, lane B, A3, F1). Process note.

- [~] R1-19. CX-9's real OCR smoke test (ocrmypdf on an invented fixture PDF) is stage 3 work (Q11);
  cycle 1 makes check_ocr honest ("versions only"). -> carry to the stage 3 brief.
  deferred: carried (chair, 2026-10-26)

## Round 1 critic round (session 2, 2026-10-26)
- 8a Codex code review (gpt-6.1-sol, read-only): 11 findings, 2 high, 8 med, 1 low; all 11
  REPRODUCED by the chair (`docs/loop/round-01/round01-codex-review.md`). Librarian R01-CX-1 to CX-11.
- Fix cycle 1 (Codex gpt-6.1-sol builder, Q22): CX-1 to CX-11, commit 28a5f96. Chair re-run:
  `150 passed`, gate `0`; chair repros all clear (CX-1 ConfigError, CX-3 `runlog is append-only`, CX-4
  `exit=97 secs=0`, CX-6 `scan=['Cases']`, CX-7/CX-8 caught); chair SEED drop done_reason guard
  (doctor.py:126) -> `1 failed, 32 passed`, restored by cmp. Chair found the CX-7 fix over-blocked
  benefits prose; follow-up narrowed it to one clause, 60 chars (T-5). run.sh now execs
  `scripts/run_capture.py` (needs a python3 on PATH before `uv sync`).

- 8b output critic (fresh Opus 5.5): `OUTPUT CRITIC 5/10 · high 3 · med 8 · low 3`
  (`docs/loop/round-01/round01-critic.md`). Chair reproduced H2 (7 of 7 DME/IME forms missed), H3 (6 of 6
  false hits), M2 (bad example `[]` as text), M5 (ranges and lists rejected), M8 (config-dir limit from
  cycle 1's CX-1 instruction, chair's own error). Owner questions 8 to 14 held with interim rulings.
- Fix cycle 2 (Codex): H1, H2, H3, M1 (partial), M2, M3, M5, M6, M7, M8, L1, L2. Carried: M4 (unbracketed
  cites, to the stage that writes cited text) as R1-20; L3 (gate selftest breadth is the rules suite).
  Done: chair re-run `162 passed`, gate `0`, critic repros clear (H2 missed `[]`, H3 false hits `[]`, M5 `[]`);
  doctor with no server: `failed=4 of 8`, exit 1, every FAIL line has `| do:`.
- Cycle budget (Q5): 8a fixes = cycle 1, critic fixes = cycle 2; one cycle left for the verifier's findings.
- [~] R1-20. Critic M4: `bates-cites` sees only bracketed cites; "(Ex. 3 at 12)" and "See page 12" pass.
  -> brief of the stage that generates cited prose.
  deferred: carried (chair, 2026-10-26)

- 8c blind verifier (fresh Opus 5.5): FAIL, 14 ticked, 4 deferred, 2 refused (B1 R1-4, B2 R1-13);
  `docs/loop/round-01/round01-verify.md`. Chair reproduced B1 (`exit=0`, want 2).
- Fix cycle 3 (Codex, last allowed): B1, B2, S2, S6, S9, S10, N1 to N3; spec D12 and D18 amended
  (chair rulings, pending veto). Commit f2023ae. Chair re-run `184 passed`, gate `0`, B1 `exit=2`,
  missing command `127`; SEED run_capture.py:13 `return 98` -> `return 0` -> `5 failed, 13 passed`, cmp, `18 passed`.

- 8c re-verifier (fresh Opus 5.5): FAIL on B1b (R1-4) and B3 (R1-13); chair reproduced B1b (`exit=0`).
  Owner Q23: one extra cycle.
- Fix cycle 4 (Codex, Q23): B1b and B3. Chair re-run `192 passed`, gate `0`, B1b `exit=2`, toolchain alias
  `exit=95`; SEED run_capture.py:46 `return capture_failed(exc)` -> `pass` -> `2 failed, 21 passed`, cmp, `23 passed`.

- [ ] V1. Fresh blind verification: every non-deferred R1 item `[x]` with the verifier's own evidence.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): not ticked; R1-4 and R1-13 refused. `docs/loop/round-01/round01-verify2.md`.
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): not ticked; R1-4 and R1-13 refused. `docs/loop/round-01/round01-verify3.md`.
