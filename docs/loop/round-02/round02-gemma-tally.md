# Round 2 Gemma tally

Model `gemma4:e4b-it-qat` through `scripts/gemma_task.py`. Tokens and seconds come from the driver's `gemma: ok;` line (one exit-6 call counted too: its tokens were spent). Attempts count every driver call on the task, including orchestrator review feedback on fixture content; re-split calls are counted separately.

| Task | File | Attempts | Re-split | Fallback | Seconds | Prompt tokens | Answer tokens | Outcome |
|---|---|---|---|---|---|---|---|---|
| G1 | tests/test_pathguard_newline.py | 1 | n | n | 46 | 1170 | 1254 | pass; docstring after imports |
| G2 | src/casefile/config.py::load | 1 | n | n | 112 | 1959 | 2937 | pass |
| G3 | tests/test_config_resolve.py | 1 | n | n | 46 | 1148 | 1209 | pass |
| G4 | src/casefile/quotes.py | 1 | n | n | 9 | 587 | 211 | pass; curly quotes as literal characters |
| G5 | tests/test_quotes.py | 1 | n | n | 17 | 898 | 446 | pass |
| G6 | src/casefile/matter.py | 1 | n | n | 119 | 1718 | 3379 | pass; omits from exc on four wrapped raises |
| G7 | tests/test_matter.py | 2 | n | n | 304 | 6098 | 8283 | pass; a1 changed match texts; pass a2 |
| G8 | records/medical/001.txt | 3 | y (1) | n | 235 | 7070 | 3703 | pass; a1 common invented name (Dr. Evelyn Reed) and arrival time; a2, a3 trailing === (no fence, --no-think plus context echo); re-split r1 (draft fenced in task) pass |
| G9 | records/medical/002.txt | 2 | n | n | 118 | 3408 | 3105 | pass; a1 second ER pain score 6/10 (unplanned conflict); fixed a2 |
| G10 | records/medical/003.txt | 1 | n | n | 62 | 1465 | 1817 | pass |
| G11 | records/medical/004.txt | 2 | n | n | 134 | 3297 | 2653 | pass; a1 referral date 03/20; fixed a2 |
| G12 | records/medical/005.txt | 1 | n | n | 36 | 1433 | 1014 | pass |
| G13 | records/medical/006.txt | 2 | n | n | 114 | 3489 | 3312 | pass; a1 L5-S1 line x5, 42 lines; fixed a2 |
| G14 | records/medical/007.txt | 1 | n | n | 42 | 1465 | 1178 | pass |
| G15 | records/medical/008.txt | 2 | n | n | 102 | 3587 | 2924 | pass; a1 no stamp, read as a later visit; fixed a2 |
| G16 | records/employer/001.txt | 2 | n | n | 97 | 3515 | 2795 | pass; a1 reused ER doctor and therapist as staff; fixed a2 |
| G17 | records/employer/002.txt | 2 | n | n | 89 | 3291 | 2533 | pass; a1 verbatim line twice, therapist as author; fixed a2 |
| G18 | records/employer/003.txt | 2 | n | n | 153 | 3899 | 4482 | pass; a1 12 wage rows, total did not match; a2 with 13 given rows |
| G19 | records/defense-report/001.txt | 2 | n | n | 120 | 3887 | 3455 | pass; a1 exam and plan on page 1 contradicting page 3; fixed a2 |
| G20 | records/defense-report/002.txt | 2 | n | n | 112 | 3580 | 3216 | pass; a1 deferred treatment, denied numbness; fixed a2 |
| G21 | records/defense-report/003.txt | 1 | n | n | 35 | 1511 | 955 | pass |
| G22 | matter.toml | 1 | n | n | 6 | 398 | 152 | pass |
| G23 | src/casefile/benchkey.py | 1 | n | n | 105 | 1738 | 3104 | pass; omits from exc on wrapped raises |
| G24 | tests/test_benchkey.py | 3 | n | n | 299 | 7131 | 8685 | pass; a1 cases unmodified; a2 files not written; pass a3 |
| G25 | 9001.001/key.json | 2 | n | n | 301 | 12596 | 7665 | pass; a1 loads (26, 5, rules=0); a2 orchestrator text review (F08, F20, F24 to F26, capitals) |
| G26 | tests/test_fixture_matter.py | 1 | n | n | 43 | 1072 | 1267 | pass |
| G27 | src/casefile/benchcandidate.py | 1 | n | n | 78 | 1226 | 2316 | pass |
| G28 | tests/test_benchcandidate.py | 1 | n | n | 66 | 1167 | 1951 | pass |
| G29 | src/casefile/benchscore.py | 1 | n | n | 127 | 1733 | 3721 | pass |
| G30 | 9001.001/ideal.json | 1 | n | n | 162 | 3065 | 4645 | pass |
| G31 | tests/fixtures/bench/flawed.json | 2 | n | n | 349 | 6018 | 10161 | pass; a1 dropped F23 too; pass a2 |
| G32 | tests/test_benchscore.py | 3 | n | n | 285 | 9127 | 8246 | pass; a1 lambda with del (exit 6, nothing written); a2 changed PERFECT; pass a3 |
| G33 | src/casefile/model.py | 1 | n | n | 81 | 1715 | 2362 | pass |
| G34 | src/casefile/benchrun.py | 1 | n | n | 88 | 2018 | 2554 | pass |
| G35 | tests/fakemodel/bench.py | 1 | n | n | 7 | 517 | 181 | pass |
| G36 | tests/fakemodel/__main__.py | 1 | n | n | 44 | 996 | 1308 | pass |
| G37 | tests/test_fakemodel_bench.py | 1 | n | n | 81 | 1326 | 2413 | pass |
| G38 | tests/test_benchrun.py | 3 | y (1) | n | 312 | 10314 | 8929 | pass; a1 reads after log.close; a2 probe 6 order; a3 sqlite3.Row vs tuple (orchestrator spec error); re-split r1 pass |
| G39 | src/casefile/bench.py | 1 | n | n | 84 | 1802 | 2438 | pass |
| G40 | src/casefile/cli.py | 1 | n | n | 97 | 1269 | 2905 | pass |
| G41 | tests/test_bench_cli.py | 2 | n | n | 178 | 4981 | 5125 | pass; a1 --matters pointed at the matter itself; pass a2 |
| G42 | tests/test_stage2_exit.py | 1 | n | n | 75 | 1914 | 2162 | pass |
| G43 | src/casefile/prose.py | 1 | n | n | 18 | 728 | 518 | pass |

## Totals
- Tasks: 43. First-try passes: 26. Tasks with retries: 17. Re-splits: 2 (G8, G38). Sonnet fallbacks: 0 (R1 tripwire 12 not approached).
- Driver calls: 66 task calls (attempts 64 plus re-split 2), plus 1 R14 probe = 67.
- Gemma tokens, task calls: prompt 131326, answer 137669; model time 4988 s (83 min).
- R14 probe (not a task): exit 3, nothing written, 93 s, prompt 309, answer 64.
- Sonnet fallback tokens: 0 (no fallback ran).
- Opus orchestration tokens are not in this table; the session's own usage is the chair's to read.

## Fix cycle 1

Same model and driver. Every call except FC1-1 ran through `scripts/run.sh python3 scripts/gemma_task.py`; FC1-1 ran with the system `python3` directly (as the build did). Refused attempts (exit 4, exit 6) are counted: their tokens were spent and nothing was written.

| Task | Finding | File | Attempts | Re-split | Fallback | Seconds | Prompt tokens | Answer tokens | Outcome |
|---|---|---|---|---|---|---|---|---|---|
| FC1-1 | R2-CH-1 | tests/test_benchrun.py::test_benchrun_zero_counts | 1 | n | n | 37 | 1985 | 980 | pass |
| FC1-2t | R2-CX-5 | tests/test_benchkey.py | 1 | n | n | 97 | 2226 | 2809 | pass |
| FC1-2 | R2-CX-5 | src/casefile/benchkey.py | 1 | n | n | 150 | 2218 | 4411 | pass; one blank line with trailing spaces |
| FC1-3t | R2-CX-6 | tests/test_benchrun.py::test_benchrun_unparsed_reply | 2 | n | n | 121 | 4974 | 3496 | a1 FILE answer on a function task, exit 4 (89 s, 2425/2564); pass a2 |
| FC1-3a | R2-CX-6 | src/casefile/model.py::ModelClient._request | 2 | n | n | 115 | 3876 | 3377 | a1 method indented 4 spaces, splice exit 6 (55 s, 1882/1564); pass a2 |
| FC1-3b | R2-CX-6 | src/casefile/benchrun.py::run | 1 | n | n | 55 | 1883 | 1575 | pass |
| FC1-4t | R2-CX-7 | tests/test_matter.py | 1 | n | n | 92 | 2275 | 2652 | pass |
| FC1-4 | R2-CX-7 | src/casefile/matter.py::load | 1 | n | n | 38 | 1784 | 1058 | pass |
| FC1-5t | F2 | tests/test_exc_chain.py | 1 | n | n | 27 | 1086 | 779 | pass; identical to the task text |
| FC1-5a | F2 | src/casefile/matter.py::load | 2 | n | n | 145 | 3701 | 4261 | a1 FILE answer on a function task, exit 4 (79 s, 1778/2313); pass a2 |
| FC1-5b | F2 | src/casefile/benchkey.py::load | 1 | n | n | 49 | 1936 | 1359 | pass |

### Fix cycle 1 totals
- Tasks: 11. First-try passes: 8. Retries: 3 (two exit 4, one exit 6; the new driver guard CX-4 caught both FILE answers, nothing written). Re-splits: 0. Sonnet fallbacks: 0.
- Driver calls: 14. Gemma tokens: prompt 27944, answer 26757; model time 926 s (15 min).

## Fix cycle 2

Same model and driver, every call through `scripts/run.sh python3 scripts/gemma_task.py` with a 600 s
foreground timeout (OR-7: key G6 and F27 to F29, ideal and flawed, pinned numbers, critic M1 detail lines).

| Task | Item | File | Attempts | Re-split | Fallback | Seconds | Prompt tokens | Answer tokens | Outcome |
|---|---|---|---|---|---|---|---|---|---|
| FC2-1t | 1 | tests/test_fixture_matter.py | 1 | n | n | 56 | 1151 | 1660 | pass |
| FC2-1 | 1 | tests/fixtures/matters/9001.001/key.json | 1 | n | n | 126 | 3268 | 3577 | pass; diff is the four added objects only |
| FC2-2t | 4 | tests/test_benchscore.py | 1 | n | n | 84 | 2468 | 2407 | pass |
| FC2-3t | 4 | tests/test_bench_cli.py | 1 | n | n | 62 | 1990 | 1767 | pass |
| FC2-4t | 4 | tests/test_stage2_exit.py | 1 | n | n | 58 | 1752 | 1645 | pass |
| FC2-2 | 2 | tests/fixtures/matters/9001.001/ideal.json | 1 | n | n | 142 | 3132 | 4033 | pass; first 29 facts equal the key's, flags equal |
| FC2-3 | 3 | tests/fixtures/bench/flawed.json | 1 | n | n | 118 | 2914 | 3344 | pass; diff against ideal is the same eight hunks |
| FC2-5t | 4 | tests/test_benchrun.py::test_benchrun_modes | 1 | n | n | 82 | 2451 | 2347 | pass; 28 -> 31 replayed facts (found by the full suite) |
| FC2-6t | 5 | tests/test_bench_detail.py | 1 | n | n | 48 | 1849 | 1338 | pass; identical to the task text |
| FC2-6a | 5 | src/casefile/benchscore.py | 1 | n | n | 147 | 2460 | 4258 | pass; flags_extra counted from the new list (same value), one unused local, one whitespace-only line |
| FC2-6b | 5 | src/casefile/bench.py::main | 1 | n | n | 50 | 1566 | 1439 | pass |

### Fix cycle 2 totals
- Tasks: 11. First-try passes: 11. Retries: 0. Re-splits: 0. Sonnet fallbacks: 0.
- Driver calls: 11. Gemma tokens: prompt 25001, answer 27815; model time 973 s (16 min).
