# Round 4 blind verification (stage 4: model client and gates)

VERDICT: PASS (R4-1 to R4-4 reproduced on aa11799, R4-5 deferred; 10 seeds, 9 red, 1 low test gap; no blocking finding).

Verifier: fresh Opus agent, no part in building round 4 and no context from it. Branch `loop/round-04`, tip aa11799
(2026-10-28 00:12). Every run went through `scripts/run.sh`, one blocking call at a time. Inputs read blind: the
request, the ledger's `## Project` and `## Round 4` (items, CHECK block), `.workflow/scratch/round04-mutated-lines.txt`,
the source tree, and spec §4. Builder reports, Codex reviews, the critic's report and the brief were opened only after
every item was ticked (reconciliation below).

## Measured numbers (probe -> line my run printed)

| Item | Probe | My line | Ledger states | Match |
|---|---|---|---|---|
| R4-1 | `pytest -q -s tests/test_stage4_exit.py` | the seven `stage4` lines, ending `stage4 exit=0 gates=6 of 6 cases=14 of 14 runs=+14 answers=+21 empty_saved=0 server_stopped=1`; `1 passed in 0.60s` | same seven lines | yes |
| R4-1 | `pytest -q -s tests/test_gates.py tests/test_fakemodel.py` | `gate_cases=27 of 27`, `68 passed` | `gate_cases=27 of 27` | yes |
| R4-1 | `pytest -q -s tests/test_quotes.py` | `ladder_ok=14 of 14`, `quotes_ok=8 of 8`, `24 passed` | same | yes |
| R4-1 | `pytest -q -s tests/test_jsonrepair.py tests/test_schema.py` | `repair_ok=13 of 13`, `schema_ok=14 of 14`, `schemas_loaded=20 of 20`, `39 passed` | same | yes |
| R4-1 | `pytest -q -s tests/test_runlog.py` | `triggers=21`, `blocked_writes=12 of 12`, `upgrade_v1=1`, `upgrade_atomic=1`, `15 passed` | same | yes |
| R4-1 | doctor, in process through `FakeTransport` (see process notes) | `doctor runlog_schema PASS schema=2 triggers=21 (counted)`; `doctor failed=0 of 8` | `runlog_schema PASS schema=2 triggers=21` | yes (line carries a ` (counted)` suffix the ledger omits) |
| R4-2 | `pytest -q -s tests/test_model.py tests/test_benchrun.py` | `chat_body_keys=1`, `cached_count_read=1`, `benchrun_modes=8 of 8 answers_ok=1 answers_failed=7 failures=7`, `75 passed` | `chat_body_keys=1 cached_count_read=1 benchrun_modes=8 of 8` | yes |
| R4-3 | `pytest -q -s tests/test_stage3_exit.py tests/test_intake.py tests/test_scanned_fixture.py` | `stage3 exit=1 pages=6 ids_ok=6 of 6 ...`, `intake_refusals=16 of 16 group_killed=1`, `check page 5 differs`, `40 passed` | `ids_ok=6 of 6`, `intake_refusals=16 of 16`, `check page 5 differs` | yes; S1 read at test_stage3_exit.py:40-41 (`record["matter"] == "9002.001" and record["page"] == n`), S2 at test_intake.py:171 (`sidecar 7 of 6`) |
| R4-4 | `pytest -q -s tests/test_benchscore.py tests/test_bench_multi.py tests/test_stamps.py tests/test_benchkey.py` | `score_cases=14 of 14`, `duplicate_numbers_exit=2`, `stamps_cases=8 of 8`, `key_refusals=13 of 13`, `11 passed` | same | yes |
| R4-4 | `grep -n -i "step\|^ *# "` over `bench.py`, `benchcandidate.py` | no output (no comment lines at all) | no step comments | yes |
| R4-4 | `scripts/suite_time.sh 3` | `suite_time runs=3 max=57.46 verdict=PASS`, exit 0 | `verdict=PASS`, exit 0 | yes |
| Regr. | `pytest -q` | `537 passed in 57.80s` | baseline 358 (round 3); round grew the suite | yes, under 90 s |
| Regr. | `python -m casefile.gate` | `0` (pytest, privacy `offenders=0 scanned=667`, rules_selftest, playbook, prose `dashes=0 files=170` all PASS) | `0` | yes |
| Regr. | `python scripts/unused_imports.py src tests scripts` | `unused_imports=0` | same | yes |
| Regr. | `casefile bench --config config.example.toml ... --candidate tests/fixtures/bench/flawed.json` | exit 1, `bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2 flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14` | identical | yes |
| Regr. | same with `--candidate tests/fixtures/matters/9001.001/ideal.json` | exit 0, `bench 9001.001 model=candidate found=29 of 29 missed=0 invented=0 extra=2 flags=9 of 9 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14` | identical | yes |
| Regr. | `pytest -q -s tests/test_stage1_exit.py tests/test_stage2_exit.py` | `exit=0 verdicts=8 fails=set() test_jobs=1`, `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1` | identical | yes |
| Regr. | intake fixture (inside the R4-3 run) | `intake 9002.001 scan pages=6 ok=5 empty=1 failed=0 stamps=6 had_text=2 ocr_added=4` | identical | yes |

## Visible outputs I produced myself

Probe `$SCRATCH/stage4_probe.py` (`$SCRATCH` is this session's scratchpad, `/private/tmp/claude-501/-Users-davidskoranski-legal-harness/4bdc9076-359c-45c6-94f2-7c7e2696528f/scratchpad`) (run with `scripts/run.sh python`): `gates.ask` over the invented matter
`tests/fixtures/matters/9001.001` (14 pages), the stand-in `FakeModel` from `tests/fakemodel/` through `FakeTransport`,
run log under `$TMPDIR`, ten modes in one log. What the rows show:

- `replay`: `ok=True attempts=1 read=13 uncited=['defense-report/001']`; coverage `read` rows have reason `""`; the
  one open item is `('defense-report/001', 'bench_extract') -> ('uncited', 'no fact or flag cites defense-report/001')`.
  Matches the ledger's `good=13 read 1 uncited ... open_items=... then 1`.
- `truncated`: failures `gate.truncation: the answer stopped before it finished (done_reason=length); retried once`,
  then `...; not retried: the one retry was used`; all 14 coverage rows `failed` with reason `gate.truncation: the
  answer stopped before it finished (done_reason=length); the page stays open until a later run reads it`.
- `cut_answer`: `gate.truncation: the answer was cut off (end_id missing)`, retried once, 14 pages failed.
- `unrepairable`: `gate.repair: the answer is not valid JSON: Expecting ',' delimiter`, retried, 14 failed.
- `bad_schema`: `gate.schema: the answer does not match the schema: facts[0].text: missing required key`.
- `bad_quote`: `gate.quotes: 5 faults (faults=5): facts[0]: quote not found on MED0001, the page it cites (quote:
  "Date of service: 13/11/2025"); facts[1].cite: cite MED0099 is not a page of this chunk; flags[0].cites[2]: cite
  MED0098 is not a page of this chunk; facts[0].text: number 03 is not in its quote; facts[2].text: number 99999 is not
  in its quote; chunk pages: MED0001, ... DEF0003`. The reason names the cited page only and lists the chunk pages
  only because a cite fault occurred, as the fix cycle 2 claim says. It is long, and every one of the 14 coverage
  rows repeats it in full.
- `forbidden_json`: `gate.rules: facts[0].text: Never name the exam as a DME or IME in any form; write "the report".
  (no-dme-ime: IME)`. Plain instruction, rule id kept (owner question 49 interim).
- `empty_answer`: `gate.coverage: the answer has no facts and no flags`, 14 failed, never saved.
- `retry_ok`: one `gate.repair` failure `retried once`, then `ok=True attempts=2`, 13 read, 1 uncited.
- `repairable`: `ok=True attempts=1`, no failure row.

No reason line holds a Python repr (`b'...'`) or a mid-word cut; the `prompt_too_long` case (exit test) ends
`... or use a model ...`. Against the claims (plain reasons, cited page only, never saved empty): they hold.

Doctor (in process, stand-in transport, state under `$TMPDIR`): all eight `PASS`, `doctor failed=0 of 8`.

Bench lines: the two `## Project` lines above, with detail lines (`missed: F04 F15 F24`, two `invented:`,
`flags_missed: G3`, `flags_extra: conflict MED0001,MED0004`, `rules: no-dme-ime DEF0003`).

## Seeds (each alone: backup copy, apply, full `pytest -q`, restore with `cp -p`, `cmp` identical)

| # | File and change | In the mutated list? | Result |
|---|---|---|---|
| 1 | `gates.py:208` `e >= card.max_answer_tokens` -> `e > ...` (answer limit off by one) | no ("count sum ceiling" is :206) | RED: `FAILED tests/test_gates.py::test_gate_cases[answer_limit]` (1 failed, 536 passed) |
| 2 | `model.py:140` `raw.get("done") is not True` -> `is False` (a missing or non-bool `done` accepted) | no (function `chat` done check) | RED: 4 failed, `test_model.py::test_requires_completed_answer[None]`, `[0]`, `[1]`, `[true]` |
| 3 | `schema.py:61` `_has_type`: `type(value) in (int, float)` -> `isinstance(value, (int, float))` (booleans pass as integer) | no (function not mentioned) | RED: `FAILED tests/test_schema.py::test_schema_table` (`type:` case) |
| 4 | `jsonrepair.py:63-64` backslash no longer sets `escaped` (an escaped quote ends the string) | no | RED: `FAILED tests/test_jsonrepair.py::test_escaped_quotes_and_backslashes[escaped \\\\\\" comma,]]` |
| 5 | `runlog.py:102` `record_answer` swaps `prompt_eval_count` and `eval_count` in the insert tuple | no (function not mentioned) | RED: `FAILED tests/test_runlog.py::test_persisted_fields_and_constraints` |
| 6 | `stamps.py:23` `compile` loses `(?<![A-Za-z0-9][-./])` (a stamp joined after a hyphen matches) | no (list names `normalize` only) | RED: `FAILED tests/test_stamps.py::test_stamps` (`case_joined_toke...`) |
| 7 | `gates.py:241` `stamped=all(p.stamps ...)` -> `any(...)` (a chunk with some unstamped pages treated as stamped) | no | GREEN, test gap: `537 passed`; re-run with a fresh `PYTHONPYCACHEPREFIX` (stale bytecode ruled out): `537 passed in 52.40s`. Direct probe `$SCRATCH/mixed_probe.py` (one stamped page, one unstamped, fact text `... [page second]`): tip `mixed ok=True attempts=1`, `gate.rules pass warning: no Bates stamp on mixed/002; cites are page ids; facts[1].text: bates-cites: [page second]`; seeded `mixed ok=False attempts=2`, `gate.rules fail ... (bates-cites: [page second]); not retried: the one retry was used`. The behaviour changes and no test sees it. |
| 8 | `benchscore.py:99` candidate flag cites no longer normalised (`frozenset(f.cites)`) | no (list names invented test, rungs line, found-test cite) | RED: `FAILED tests/test_benchscore_cite.py::test_candidate_cite_spellings_match_the_page` |
| 9 | `tests/fakemodel/core.py:165` `truncated` mode no longer sets `done_reason = "length"` | no (list names the allowed keys only) | RED: 10 failed, including `test_stage4_exit.py::test_stage4_exit`, `test_gates.py::test_gate_cases[truncated]`, `test_fakemodel.py::test_modes`, `test_doctor.py::test_truncated_fails` |
| 10 | `quotes.py:9` `CURLY` drops the right single quote `’` | no (list names `_drop_line`, digits, boundaries, hyphen join) | RED: 2 failed, `test_quotes.py::test_found_in`, `test_quotes.py::test_same_and_legacy_boundary` |

After every restore `git status --short -- <file>` printed nothing; final `git diff --stat` over `src` and `tests` is
empty.

Seed 7 severity: low, not blocking. The code is right by the brief's ruling (§1.8: "when any page of the chunk has no
stamp ... `Rules.check` runs with `stamped=False`"), and `stamped` changes only the `bates-cites` severity, which sees
bracketed cites only (R1-20, deferred). Fix (for whichever round touches gate 5 next): add a `test_gates.py` case with a
mixed chunk (one page with a stamp, one without) whose fact `text` carries a bracketed non-Bates cite without digits
(e.g. `[page second]`), asserting `gate.rules` passes with the `bates-cites` finding in the warning message.

## Design calls found unlogged

1. D38's digit-run check and bracketed cites in a fact's `text` collide. Probe (first version of `mixed_probe.py`,
   fact text `The clinic recommends follow-up. [cite mixed/002]`, quote without digits): `gate.quotes: 1 fault
   (faults=1): facts[1].text: number 002 is not in its quote`, retried, failed. The playbook's own good example for
   `bates-cites` (`rules.toml:60`, `The report records a normal gait. [cite ABC0001]`) would fail gate 4 the same way
   (`number 0001`). Latent at stage 4: the brief (§1.8) says an extraction answer holds no bracketed cites. It needs a
   ruling before the stage that writes cited prose (with R1-20): either strip `[cite ...]` spans before the digit-run
   check, or keep cites out of `text`. Not in T-19 (that covers date reformatting only).
2. The behaviour of a mixed stamped and unstamped chunk is ruled in the brief (§1.8) but not in spec §4 or §9; spec
   §4 rule 5 says only "with a warning when records are not stamped". Low; a sentence in the as-built (§11) would do.

## Process notes

- Doctor: I did not run `casefile doctor --config config.example.toml`. That config points at
  `http://127.0.0.1:11434`, where the critic found the owner's local `ollama` listening, and my brief forbids sending
  anything to a local model server. I ran `doctor.run` in process with `tests/test_doctor.py`'s `setup_config` and
  `invoke` (stand-in `FakeTransport`, port 18434 that is never opened, injected OCR smoke), state under `$TMPDIR`.
  The `runlog_schema` line is the same code path either way.
- The first `suite_time.sh 3` run was piped into `tail`, so its exit code was hidden; I re-ran it to a file:
  `suite_time_rc=0`.
- Working tree: at the end, `docs/spec.md` and `docs/loop/tuning-questions.md` show uncommitted edits (spec §4
  rewritten to D31, D33, D35, D38 wording; T-16 to T-19 added), timestamped 00:13, one minute after the tip commit
  and before this session. I did not make or touch them. The gate's prose check passed with them present. Commit or
  discard them before the merge; my verification is of aa11799's code (no diff in `src`, `tests`, `scripts`).
- Every seed used a copy in my scratchpad and `cp -p` back; every `cmp` printed identical.
- Ledger: I ticked R4-1 to R4-4 and V. with my own lines added under each item; no claim text was changed.

## Reconciliation (opened after every tick)

Numbers that match: every CHECK number in the ledger reproduced exactly. Fix cycle 2's final `537 passed in 57.61s`
matches my `537 passed in 57.80s`; `gate_cases=27 of 27`, `ladder_ok=14 of 14`, `unused_imports=0`, both bench lines
and stage 1 to 4 lines match fix 1 and fix 2. W1's `chat_body_keys=1`, `cached_count_read=1`, `benchrun_modes=8 of 8`,
W2's `repair_ok=13 of 13 schema_ok=14 of 14 schemas_loaded=20 of 20`, W3's `triggers=21 blocked_writes=12 of 12
upgrade_v1=1 upgrade_atomic=1 coverage_latest=1 coverage_statuses=3 of 3 open_items=2 of 3` (I saw the last three in
the full run too), W5's `score_cases=14 of 14 key_refusals=13 of 13 duplicate_numbers_exit=2 stamps_cases=8 of 8`.
Suite time: T-18 records `max=54.47` at the round 4 merge; fix 2 `max=57.93` (one run); mine `max=57.46` (three
runs). All PASS against 90 s.

Claims I could not reproduce: none. One I chose not to reproduce as written: the critic ran the real
`casefile doctor --config config.example.toml` (its step 2, `doctor failed=3 of 8`, reached the local ollama with a
404); I used the stand-in instead (process notes). Codex R04-CX-4 is recorded as not reproduced by the chair; I did not
probe it.

Seeds they used that I would have chosen too: W4 (g) to (i) and the brief's `eval_count == max_answer_tokens` count
edit are the same family as my seed 1, and the `answer_limit` case that caught it is that edit. W1 (d) (cached count
type check) is next to my seed 2 (the `done` check); both are guard checks on `chat`. W2 (b) (commas inside strings)
is next to my seed 4, which attacks the same string tracker from the escape side. W5 (e) (shared stamp compiler) is
next to my seed 6. The brief's W7 seed (h) (unstamped warning dropped) covers the pipeline warning but not the
severity flag `stamped`; that is the gap my seed 7 found. The brief's W7 seed (b) (read written when gate 5 warns)
was told to stay green, which is consistent with what my mixed probe shows on the tip (a warning passes, page read).

Critic findings checked against my outputs: H1 (Python reprs in reasons) is fixed in what I produced (no `b'...'` in
any row); M1 (every page listed) is fixed (`quote not found on MED0001, the page it cites`; chunk pages listed only on
a cite fault); M4 (doctor model-not-found advice) I saw only through the test suite (`test_doctor.py` M4 case passes).
