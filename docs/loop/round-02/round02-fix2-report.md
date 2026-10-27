# Round 2 fix cycle 2 report (orchestrator, Opus 5.5; builder Gemma 4 e4b, owner Q28)

Branch `loop/round-02`, from 4d8269b. Scope: OR-7 (critic H1, H2, M1). All code, tests and fixture data
written by `gemma4:e4b-it-qat` through `scripts/gemma_task.py`; the chair wrote task files, seeds and
records only. No Sonnet fallback. Per-call numbers: `round02-gemma-tally.md`, "Fix cycle 2". Baseline at
4d8269b: `260 passed in 36.59s`, gate `0`, listening Python processes 0.

## Items: red before, green after (verdict is the exit status)
| Item | Test | RED before the fix | GREEN after | Commit |
|---|---|---|---|---|
| 1 key G6, F27 to F29 | `test_key_loads` | `assert (26, 5, 14) == (29, 6, 14)`, exit 1 | `key_facts=29 flags=6 pages=14`, exit 0 | 6c1968c |
| 2, 3, 4 ideal, flawed, pinned lines | `test_shipped_fixtures`, `test_bench_exits`, `test_stage2_exit`, `test_stage2_inprocess_control` | `4 failed, 1 passed`; ideal scored `found=26 of 29 missed=3 ... flags=5 of 6 flags_missed=1` | perfect and flawed lines below, `8 passed`, exit 0 | 6c1968c |
| 4 replay count | `test_benchrun_modes` | full suite `1 failed, 259 passed`: `benchrun_modes=6 of 7` (28 facts pinned) | `benchrun_modes=7 of 7` | 6c1968c |
| 5 detail lines (M1) | new `tests/test_bench_detail.py` (flawed, ideal, a long-quote and flag-rule probe) | `2 failed, 1 passed`, `detail_lines=0` | `3 passed`; flawed `detail_lines=6`, ideal `0`, probe `2` | d007821 |

Seeds (each restored, `cmp` ok): G6 removed from ideal.json -> `3 failed, 1 passed` (perfect line shows
`flags=5 of 6 flags_missed=1`), exit 1. The `missed:` line dropped from `Score.details` ->
`test_flawed_detail_lines` fails (`detail_lines=5`), exit 1.

Quotes checked on the pages before the tasks (grep): MED0008:15, DEF0003:23, MED0003:22, MED0007:25,
DEF0002:25. The ideal's two extras (EMP0001 hire date, EMP0002 50 pounds) are not F27 to F29 and stay.
`flawed.json` diffed against `ideal.json`: the same eight hunks as before (six defects), nothing else.

## Standing commands
- `scripts/run.sh casefile bench --config config.example.toml --matters tests/fixtures/matters --candidate tests/fixtures/bench/flawed.json`, exit 1:
```
bench 9001.001 found=26 of 29 missed=3 invented=2 extra=2 flags=5 of 6 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14
  missed: F04 F15 F24
  invented: MED0003 "Patient was lifting 80 pounds."
  invented: MED0099 "Date of service: 03/11/2025"
  flags_missed: G3
  flags_extra: conflict MED0001,MED0004
  rules: no-dme-ime DEF0003
bench matters=1 imperfect=1
```
- Same with `tests/fixtures/matters/9001.001/ideal.json`, exit 0:
```
bench 9001.001 found=29 of 29 missed=0 invented=0 extra=2 flags=6 of 6 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14
bench matters=1 imperfect=0
```
- `scripts/run.sh pytest -q -s tests/test_stage2_exit.py`, exit 0: `stage2 exit=0 runs=+1 answers_ok=+1
  server_stopped=1`, the perfect line, `stage2-control exit=0 runs=+1 answers_ok=+1`, `2 passed`.
- Final: `263 passed in 37.98s`; gate `0`. Listening Python processes after: 0.

## Design choices the chair made (owner asleep; conservative reading, flagged)
- New texts follow the firm rule ("the report", never DME, IME or the payer): F27 "Dr. Okonkwo-Lind
  restricted the patient to sedentary duty with no lifting over 15 pounds until re-evaluation on
  06/20/2025."; F28 "The report states no further treatment is medically necessary."; F29 "The family
  medicine record assessed a lumbar strain, likely work related."; G6 about "Dr. Okonkwo-Lind's
  impression is left L5 radiculopathy; the report found no objective findings of radiculopathy." The
  older texts still say "Dr. Marchetti's report" (owner question 29 open).
- Detail formats where the ruling left room: `flags_extra` and a flag's rule hit list the cites sorted
  and joined by commas; a rule hit on a flag's about reads `rules: <rule id> flag <cite,cite>`; one
  `flags_extra` line per distinct extra flag, one `rules` line per finding, facts before flags.
- Detail lines print in candidate runs and model runs alike; they are console output only (no run-log
  column added, M1's run-log half is not in OR-7's scope).

## Deviations
- Items 1 to 4 are one commit (6c1968c): the key change alone turns the perfect, flawed and replay
  tests red, and no commit may leave the suite or gate red.
- FC2-6a: Gemma computed `flags_extra` as the length of the new extra-items list instead of keeping the
  old set difference (same value: distinct candidate sets not in the key), and left one unused local
  (`flags_extra_items = []`) and one whitespace-only line. Left as written; joins the OR-5 cosmetic
  items for round 3.
- `docs/spec.md` D25 was not edited (the bench line is unchanged); the detail lines are described here
  and in the test only. Flagged for the chair.

## Gemma
11 tasks, 11 driver calls, 11 first-try passes, 0 re-splits, 0 fallbacks. Tokens: prompt 25001, answer
27815; model time 973 s.
