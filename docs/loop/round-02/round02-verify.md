# Round 2 blind verification (fresh verifier, 2026-10-27, tip 2099304)

FAIL: R2-3e refused (a received non-200 reply gets no answer row); every other Round 2 item ticked; V2 not ticked.

The verifier built nothing this round and had no context from the build. Every run went through
`scripts/run.sh`, in the foreground. `--config config.example.toml` was used for `casefile` commands, and a
scratch config (state and matters under the session scratchpad) was used for the stand-in runs. Listening
Python processes: 0 before, 0 after every stand-in run, 0 at the end. All data is the invented matter
9001.001 or invented probe pages. No real client record, name or fact was used.

## Measured numbers (probe -> line)
| Item | Probe | Line produced |
|---|---|---|
| suite | `scripts/run.sh pytest -q` | `263 passed in 37.27s` |
| gate | `scripts/run.sh python -m casefile.gate` | exit 0; `gate prose PASS dashes=0 files=129`, privacy, rules_selftest, playbook PASS |
| stage 1 | `pytest -q -s tests/test_stage1_exit.py` | `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`, control same, `2 passed` |
| stage 2 | `pytest -q -s tests/test_stage2_exit.py` | `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`, perfect line, `stage2-control exit=0 runs=+1 answers_ok=+1`, `2 passed` |
| R2-1 | test_pathguard_newline.py -s | `newline_join_exit=95 verdict_lines=1`, `2 passed` |
| R2-2 | test_config_resolve.py -s | `resolve_refused=4 of 4 cli_exit=2` |
| R2-3a | test_quotes, test_matter, test_fixture_matter -s | `quotes_ok=8 of 8`; `matter_pages=3 refusals=12 of 12` (ledger says 11: the 12th is fix cycle 1's CX-7); `fixture_pages=14 binders=3` |
| R2-3b | test_fixture_matter, test_benchkey -s | `key_facts=29 flags=6 pages=14`; `key_refusals=12 of 12` (ledger says 10: plus the two CX-5 collisions) |
| R2-3c | CLI flawed, ideal; test_benchcandidate, test_benchscore | flawed `bench 9001.001 found=26 of 29 missed=3 invented=2 extra=2 flags=5 of 6 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14`, exit 1; ideal `found=29 of 29 ... extra=2 flags=6 of 6 ... rules=0 pages_failed=0 of 14`, exit 0; `candidate_refusals=7 of 7`; `score_cases=11 of 11` |
| R2-3e | `card_version()`; test_model; 404 probe | `card_version=092368692dd3`; `16 passed`; `probe404 failure= bench.model: status=404: b'{"error": "fakemodel: unknown model"}'`, `probe404 answers= 0 failures= 1` |
| R2-3d | test_fakemodel_bench, test_benchrun -s | `bench_recording_ok=1 modes=4 pages_in_request=14`; `benchrun_modes=7 of 7 answers_ok=1 answers_failed=6 failures=6` |
| R2-3f | test_bench_cli -s; two-matter probe | `bench_exit_perfect=0 bench_exit_flawed=1 bench_exit_badkey=2 bench_exit_noconfig=2 bench_exit_nolog=2`; probe (first matter fails, second perfect) `exit=1`, `bench matters=2 imperfect=1` |
| R2-3g | stage 2 test; gate; em dash seed | as above; em dash appended to key.json -> `gate prose FAIL dashes=1 files=129`; restored, cmp ok |
| R2-6 | each fix reverted, targeted tests; CLI repros | CH-1 `1 failed`; CX-6 `1 failed`; CX-7 `2 failed`; CX-5 `1 failed`; F2 `1 failed`; 0xff matter.toml exit 2 `MatterError ... can't decode byte 0xff`; duplicate F99 exit 2 `BenchKeyError ... fact F99: same cite and quote as fact F01` |
| R2-7 | key read; CLI; test_bench_detail -s | G6 conflict MED0007,DEF0002; F27 MED0008, F28 DEF0003, F29 MED0003; `bench_detail_flawed exit=1 detail_lines=6`, `bench_detail_perfect exit=0 detail_lines=0` |

## Visible output against the claim
Ideal (`--candidate .../9001.001/ideal.json`): the perfect line, `bench matters=1 imperfect=0`, exit 0, no
detail lines, no run log written (candidate mode never opens it). Flawed: the amended line, then
`  missed: F04 F15 F24`, `  invented: MED0003 "Patient was lifting 80 pounds."` (on no page),
`  invented: MED0099 "Date of service: 03/11/2025"` (not a page), `  flags_missed: G3`,
`  flags_extra: conflict MED0001,MED0004`, `  rules: no-dme-ime DEF0003`, `bench matters=1 imperfect=1`,
exit 1. Matches the R2-3c and R2-7 claims exactly.

Model run (`scripts/run.sh python -m tests.fakemodel --port 18534 --bench-matter tests/fixtures/matters/9001.001`,
then `casefile bench --matters tests/fixtures/matters --config <scratch>`): perfect line, exit 0; run log
`run (1, 'bench', '9001.001', 'bench.extract', '092368692dd3', 'pb-00be6eb62752', 'qwen3.8:27b', 14, '8f93e48924dc')`,
`answer (1, 1, 'ok', 'stop', 4817, 1642, 7312, ...)`. Truncated mode: `bench 9001.001 failure bench.truncation:
done_reason=length`, `found=0 of 29 ... pages_failed=14 of 14`, all 29 IDs and six flag IDs listed, exit 1,
answer row `failed`/`length` with the raw reply, failure row `bench.truncation`. Malformed mode: `failure
bench.answer: not JSON: ...`, exit 1, answer row `failed`, failure row `bench.answer`. Server stopped by
SIGTERM each time (`run.sh: interrupted by SIGTERM; job stopped`); listeners 0 after.

## Seeds (verifier's own; none in the places listed as builder-mutated)
Baseline green (`263 passed`) before each; one-line mutation; full suite unless noted; restored, `cmp` ok every time.
| ID | File (seeded by a builder?) | Mutation | Should be caught by | Result |
|---|---|---|---|---|
| V2-S1 | bench.py discovery (no) | `if (p / "matter.toml").is_file()` -> `if p.is_dir()` | a matters dir with a non-matter subfolder | GREEN `263 passed` (finding) |
| V2-S2 | benchscore.py match (no: cite clause) | drop `k.cite == fact.cite and` | D25 "found = same cite": same quote on two pages | GREEN `263 passed` (finding) |
| V2-S3 | benchcandidate.py flag parsing (no: flags) | drop `not cites or` (empty cites accepted) | candidate refusals | RED `1 failed` test_benchcandidate::test_refusals |
| V2-S4 | benchrun.py truncation guard (no: None case) | `!= "stop"` -> `not in ("stop", None)` | missing done_reason is not a stop | GREEN `263 passed` (finding) |
| V2-S5 | benchscore.py flag dedupe (no) | drop `or flag_key in seen` | the same extra flag sent twice counts once | GREEN `263 passed` (finding) |
| V2-S6 | bench.py exit tally (no) | `imperfect += not s.perfect` -> `imperfect = int(not s.perfect)` | exit 1 when any matter is imperfect | GREEN `263 passed` (finding); under the seed my two-matter probe exits 0 |
| V2-S7 | benchrun.py raw storage (model.py raw path) | `json.dumps(exc.raw)` -> `str(exc.raw)` | answer row holds the JSON reply | RED `benchrun_modes=6 of 7`, `1 failed, 2 passed` |
| V2-S8 | cli.py (no) | swap `args.config` and `args.candidate` | CLI exits | RED `1 failed` test_bench_cli::test_bench_exits |

The unmutated code is right in every green case (direct probes on the tip): S1 stray `notes/` folder and
`readme.txt` -> `exit=0 ... imperfect=0`; S2 same quote on MED0001 and MED0002, candidate cites MED0002 ->
`found=0 of 1 ... extra=1`; S4 done_reason removed -> `failure=bench.truncation: done_reason=None
pages_failed=14`; S5 one extra flag twice -> `flags_extra=1`; S6 -> `exit=1`, `imperfect=1`. So these are
test gaps, not wrong behaviour: a regression in any of them would pass the suite.

## Blocking finding
- **V2-F1 (refuses R2-3e).** D25 and R2-3e: "every received reply an answer row". A non-200 HTTP reply is
  received but stored nowhere except a 200-byte failure message. Repro: `benchrun.run` against
  `FakeModel(recordings=recordings_for(MATTER), model="other:model")` through `FakeTransport` ->
  `answers= 0 failures= 1`. Cause: `src/casefile/model.py` raises `ModelError(f"status={status}: ...")` at
  the `status != 200` check (line 59) and `ModelError(f"status={exc.code}: ...")` in the HTTPError handler
  (line 55) without `raw`, so `benchrun.run` (line 69) skips `record_answer`. Fix: pass the decoded body
  (`payload.decode("utf-8", errors="replace")`, and `exc.read()` decoded for HTTPError, read once) as `raw`;
  add a test_benchrun case (model tag mismatch -> 404) asserting one `failed` answer row holding the body.
  Seed: drop the new `raw` -> red. Alternative: the chair rules that "received reply" means a 200 reply,
  logs it in `## Clarified` and amends D25 and R2-3e's wording; then R2-3e can be ticked on the evidence above.

## Non-blocking findings (test gaps; recommend the same fix cycle)
- V2-S1: add a test with a non-matter subfolder and a stray file beside 9001.001 (expect the same perfect line).
- V2-S2: add a score case where the same quote is on two pages and the candidate cites the wrong one (expect extra, missed).
- V2-S4: add a test_benchrun probe with done_reason removed (expect `bench.truncation`).
- V2-S5: add a score case with one extra flag sent twice (expect `flags_extra=1`).
- V2-S6: add a two-matter bench test (first imperfect, second perfect; expect exit 1, `imperfect=1`), e.g. via
  `bench.main(..., runner=...)` as my probe did.
- Ledger drift: R2-3a says 11 refusals and R2-3b `key_refusals=10 of 10`; the tip prints 12 of 12 each
  (fix cycle 1 added cases). R2-3g's `files=122` is now 129. Not amended in the ledger.

## Design calls found unlogged in the ledger
- Non-200 replies carry no `raw` (V2-F1): flagged in the fix 1 report as "left for round 3 to rule on", never
  ruled or logged in `## Clarified`.
- A duplicate candidate fact matching an already matched key fact counts as neither found nor extra
  (probe: two extra copies of F01 -> line unchanged). The build brief's score case 6 states it; not in D25 or the ledger.
- Two matters with the same `number` load and score side by side (two identical `bench 9001.001` lines in
  my probe); no refusal. Not in D25.
- Candidate mode writes no run log row (ideal and flawed runs create no `runlog.sqlite`). The build report
  says so; not in D25.

## Process notes
- Every probe used invented data. Scratch files only under the session scratchpad. Only `.workflow/LEDGER.md`
  and this file were changed. The sandbox stayed on.
- The stand-in ran as a separate process via `scripts/run.sh python -m tests.fakemodel` inside the same
  foreground call as the bench, then got SIGTERM; run_capture killed the group and listeners went to 0.
- `nice(5) failed: operation not permitted` printed once per stand-in start (sandbox; harmless).

## Reconciliation (read after every item was ticked or refused)
- Build report, fix 1 and fix 2 reports: every number I re-ran matches theirs at the commits they name; the
  later growth (refusals 11 -> 12, key refusals 10 -> 12, prose files 122 -> 129, key 26/5 -> 29/6) is
  explained by fix cycles 1 and 2. Their seeds and mine do not overlap, by design of this brief.
- Codex CX-6 and Fable's note on it framed the gap as a 200 reply that could not be decoded; fix cycle 1
  closed that case and explicitly left non-200 to round 3 (fix 1 report, "Design choices"). V2-F1 is that
  leftover: known to the builders, but unruled and contradicted by R2-3e's own wording.
- Codex CX-2 (positive counts do not prove the prompt was consumed) is deferred to stage 4 by OR-4; my
  V2-S4 is a different, narrower gap (missing done_reason), and the code handles it.
- No report seeded discovery, the cite clause, flag dedupe, the multi-matter tally or the missing
  done_reason case; those five green seeds are new.
- The critic's stand-in-by-hand run (truncated mode) matches mine except the key totals it predates (26 vs 29).
