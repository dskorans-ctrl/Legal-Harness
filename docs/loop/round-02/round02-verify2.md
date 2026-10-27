# Round 2 verification, second pass (blind verifier 2, 2026-10-27, tip b875949)

FAIL: R2-3e and R2-8 refused on one finding, V2b-F1 (a received 3xx reply stores no answer row). V2 not
ticked. Every other check reproduces. I built nothing this round and had no context from building it.

## Regression set (each through `scripts/run.sh`, foreground)
- `pytest -q`: `269 passed in 37.28s`.
- `python -m casefile.gate`: prints `0`, exit 0; `gate pytest PASS exit=0`, `gate privacy PASS offenders=0
  scanned=550`, `gate rules_selftest PASS misses=0 false_hits=0`, `gate playbook PASS invalid=0 unmarked=0
  version=pb-00be6eb62752`, `gate prose PASS dashes=0 files=136`.
- `pytest -q -s tests/test_stage1_exit.py`: `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`, `stage-control
  exit=1 verdicts=8 fails={'ocr'} expected={'ocr'} test_jobs=1`, `2 passed in 0.76s`.
- `pytest -q -s tests/test_stage2_exit.py`: the perfect line, `stage2-control exit=0 runs=+1 answers_ok=+1`,
  `2 passed in 0.76s` (the full suite also printed `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`).
- `casefile bench --config config.example.toml --matters tests/fixtures/matters --candidate
  tests/fixtures/bench/flawed.json`: `bench 9001.001 found=26 of 29 missed=3 invented=2 extra=2 flags=5 of 6
  flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14`, then `  missed: F04 F15 F24`, two `  invented:`
  lines, `  flags_missed: G3`, `  flags_extra: conflict MED0001,MED0004`, `  rules: no-dme-ime DEF0003`,
  `bench matters=1 imperfect=1`, exit 1.
- Same with `tests/fixtures/matters/9001.001/ideal.json`: `bench 9001.001 found=29 of 29 missed=0 invented=0
  extra=2 flags=6 of 6 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14`, `bench matters=1
  imperfect=0`, exit 0.
- Listening Python processes: 0 before, 0 after.

## R2-3e: every received reply an answer row (D25)
Probe (scratch script, `benchrun.run` against the stand-in `FakeModel`, the reply reshaped per case, one run
per case, rows counted by run id): `probe_d25 cases=20 bad=1`.
- One `ok` row, no failure: the good replay.
- One `failed` row holding the body and one failure row: 404 (wrong model tag, `{"error": "fakemodel: unknown
  model"}`), 500, 503 empty body (row holds `''`), 502 HTML, 201, non-JSON 200, JSON array 200, bad UTF-8 200,
  truncated (`bench.truncation`), done false, done_reason missing (`bench.truncation: done_reason=None`),
  eval_count 0 and -3 (`bench.counts`), prompt_eval_count `"12"` and `12.0`, eval_count `true`, no message
  (`bench.model`), malformed answer (`bench.answer`).
- None: 302. Confirmed with the real opener (`NoRedirect`) against a loopback `HTTPServer` in the same
  process: `real_opener status=302 answers=[] failures=['bench.model'] failure='bench.model: redirect refused:
  302 to http://127.0.0.1:9/x'`; 307 the same; a 404 from the same server stores one row.

**V2b-F1 (blocking).** D25: "every received reply stored as an answer row"; OR-8: "every received reply, any
status, is stored". A 3xx reply is received (status, headers and body arrive) but model.py raises without
`raw` at :18 (`NoRedirect.redirect_request`), :50 and :54. The refusal itself is right (D21); only the row is
missing. Either pass the body as `raw` at those raises (`fp.read()` in the handler) and add a 302 case to
`test_benchrun_non200_reply`, or the chair rules redirects out of D25 (the build brief G33 kept `NoRedirect`
raw-less, before OR-8). Fix cycle 3 was the last this round allows, so this is the chair's call.

## R2-8: the fix and the five tests
Fix sites (full suite each): model.py HTTPError raise without `raw` -> `1 failed, 268 passed`; `status != 200`
raise without `raw` -> `1 failed, 268 passed`. Seeds, each applied (`cmp -s` differed), targeted test:
| Seed | Mutation | Result |
|---|---|---|
| S1 | bench.py `(p / "matter.toml").is_file()` -> `p.is_dir()` | test_bench_discovery `1 failed` |
| S2 | benchscore.py drop `k.cite == fact.cite and` | test_benchscore_cite `1 failed` |
| S4 | benchrun.py `!= "stop"` -> `not in ("stop", None)` | test_benchrun_done_reason `1 failed` |
| S5 | benchscore.py drop `or flag_key in seen` | test_benchscore_flag_dedupe `1 failed` |
| S6 | bench.py `imperfect += not s.perfect` -> `imperfect = int(not s.perfect)` | test_bench_multi `1 failed` |
All restored with `cp`, `cmp` ok, `git status` clean apart from the untracked `.claude/worktrees/`. R2-8 is
refused only because its first clause ("non-200 replies stored as failed answer rows with the body") does not
hold for 3xx (V2b-F1).

## New seeds (full suite each, all restored, cmp ok)
| ID | Mutation | Result | Unmutated code |
|---|---|---|---|
| N1 | benchcandidate.py:68 drop `or not cites` (empty flag cites accepted) | RED `1 failed, 268 passed` | |
| N2 | benchcandidate.py:71 `not isinstance(about, str)` -> `about is None` | GREEN `269 passed` | right: `flag 1: about must be a string` |
| N3 | matter.py:82 unlisted binder folder accepted | GREEN `269 passed` | right: `unlisted binder folder xray` |
| N4 | benchkey.py:75 drop the `isinstance(item[k], str)` check | GREEN `269 passed` | right: fact text 5 refused |
| N5 | bench.py:95 runner failure line never printed | GREEN `269 passed` | right: truncated stand-in via `bench.main` -> exit 1, `bench 9001.001 failure bench.truncation: done_reason=length` |
| N6 | stand-in bench.py records `messages(...)[1:]` | RED `6 failed, 263 passed` | |
N2 to N5 are test gaps, non-blocking (code right by direct probe).

## Observations (non-blocking)
- matter.py refuses any non-binder name under `records/` and any non-page name in a binder; a Finder
  `.DS_Store` would make a bench matter exit 2. Invented matters in the checkout only; for the chair.

## Reconciliation (read after the items above)
- round02-fix3-report.md: agrees on every listed case and seed (F1-a, F1-b, S1 to S6 red, `269 passed`). It
  covered a 404 through HTTPError and a 503 returned without an exception; neither it nor the chair re-run
  exercised a 3xx, which the brief (G33) had left raw-less before OR-8 widened D25 to any status.
- round02-verify.md: V2-F1 (404) is closed; V2-S1, S2, S4, S5, S6 are now red under their own seeds.
