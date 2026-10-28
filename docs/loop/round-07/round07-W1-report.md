Built W1 only: composite fact identity, append-only splits under the matter lock, reading provenance, status counts and memo change reporting. No commit.

| Claim | Verified by | Control seed and exact RED text |
|---|---|---|
| Different dates separate | `different_date_new_fact` | (a) quote-only identity: `different_date_new_fact: different dates merged`; chronology returned to 37 |
| Split view works | `split_on_append` | (b) ignore splits: `split_on_append: split view did not create two facts` |
| Jobs upgrade stored files | `split_through_start` | (c) omit start upgrade: `split_through_start: split_needed=1 after outputs.start` |
| Splits stale outputs | `split_through_start` | (c2) omit change kind: `split_through_start: split left memo current` |
| Target IDs stay unique | `split_refused` | (d) accept reused ID: `split_refused: reused to id accepted` |
| Date spellings merge | `same_identity_still_cites` | (e) raw dates: `same_identity_still_cites: parsed date or folded provider failed to merge` |

Each control ran through `scripts/run.sh`: green, RED, byte-identical restoration confirmed by `cmp`, green.

Pin moves: `casefile_ok` 17→22; facts 37/38→38/39; initial new facts 37→38; chronology 37→38; dated 37/37 and 37/38→38/38 and 38/39.
Stage 5 events `(50,52,55,56)`→`(49,51,54,55)`; cites 118/120→117/119; readings remain 38. Stage 6 adds `m1_fixed=1`.
Ideal merge events 48→47; fact IDs `F1..F35,F38,F39`→`F1..F38`; flag IDs `G40..G48`→`G39..G47`.
Additional findings fixed: omitted packet/round-5 count pins, bench probe metadata, provider-order assertions, and an implementation variable-name collision. Marchetti page order `/002,/003`→`/003,/002`.
Both benchmark lines are byte-identical to ledger baselines, with exits 1/0. `bench/ideal.json` is absent; the ideal run used the ledger’s `tests/fixtures/matters/9001.001/ideal.json`.

Files touched: `src/casefile/{facts,memo,memo_job,outputs,status}.py`.
Tests touched: `tests/{test_facts,test_status,test_stage5_exit,test_stage6_exit,test_round05_fixes,test_bench_pipeline,test_packet,test_round06_fix1}.py`.
Outside-list one-line edits: `test_bench_pipeline.py`, `test_packet.py`, `test_round06_fix1.py`. No `test_memo.py` change was needed.

Librarian entries checked: R01-CX-11; R02-CX-5; R03-PC-3; R03-V-L1; R04-CX-7; R04-OC-1; R04-CH-1; R05-PC-7; R05-PC-8; R05-PC-17;
R05-CX-2; R05-CX-3; R05-CX-4; R05-CX-5; R05-CX-6; R05-OC-1; R05-OC-3; R06-CX-16; R06-CX-18; R06-CH-2.

Required final runs: `scripts/run.sh pytest -q` and `scripts/run.sh python -m casefile.gate`. Also `unused_imports=0` and clean `git diff --check`.
Verbatim final pytest line and gate ending:
```text
786 passed in 66.88s (0:01:06)
gate pytest PASS exit=0
gate privacy PASS offenders=0 scanned=825
gate rules_selftest PASS misses=0 false_hits=0
gate playbook PASS invalid=0 unmarked=0 practice=13 samples=3 version=pb-b0f17098b48d
gate prose PASS dashes=0 files=247
0
```