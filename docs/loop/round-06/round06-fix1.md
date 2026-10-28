Implemented all 16 ruled fixes; L7 is unchanged. Added 19 tests and completed 30 RED → `cmp`-identical restore → GREEN controls. [Full report and evidence](/Users/davidskoranski/legal-harness/.workflow/scratch/round06-fix1.md). No commit or ledger edit.

Verified through `scripts/run.sh pytest -q tests/test_round06_fix1.py`; suffixes below identify tests.

| Claim | Verified by | Control seed and RED text |
|---|---|---|
| H1 | `h1` | Raw reasons: `H1: rejected model text escaped into output` |
| H2 | `h2_pages`, `h2_elements` | Drop pages: `H2: batch lost factless pages`; overwrite: `H2: later partial overwrote stated element` |
| M1 | `m1`, `m1_exam`, `m1_cards` | Broaden exemption: `M1: non-bills-card fee question passed` |
| M2 | `m2` | Old matcher: `M2: examiner binder assigned ours: IME-report` |
| M3 | `m3` | Disable validation: `DID NOT RAISE <class 'casefile.matterinfo.MatterInfoError'>` |
| M4 | `m4` | Suppress refusal: `DID NOT RAISE <class 'casefile.outputs.OutputError'>` |
| M5 | `m5` | Omit staleness: `M5: failed replacement left prior output current`; omit cleanup: `M5: success retained partial` |
| L1 | `l1` | Remove compound guard: `L1: compound question satisfied separate topics` |
| L2 | `l2` | Drop label check: `L2: unsupported label number passed` |
| L3 | `l3` | Remove fallback: `L3: unstamped page selection raised IndexError` |
| L4 | `l4` | Prompt first: `L4: attorney prompt preceded stamp refusal` |
| L5 | `l5` | Persist one plaintiff: `L5: prompt did not record multiple plaintiffs` |
| L6 | `l6` | Omit warnings: `L6: unstamped output missing warning` |
| L8 | `l8` | Restore role demand: `L8: ordinary matter demands other role` |
| L9 | `l9` | Disable oracle: `L9: exit oracle trusted production reason exemption` |
| L10 | `l10` | Keep absent fact: `L10: packet listed absent-page fact` |

Files: `playbook/rules.toml`; `src/casefile/{depo,gates,hearing,matterinfo,memo,outputs,packet,report,roles,rules,status}.py`.
Tests: `tests/{test_round06_fix1,test_hearing,test_matterinfo,test_memo,test_outputs,test_roles,test_rules,test_stage6_exit}.py`. Reports: `.workflow/scratch/round06-fix1.md`, `round06-fix1-controls.json`.
Librarian checked: R01-CX-5, R01-CX-7, R01-CX-8, R01-CX-10, R01-CX-11, R01-OC-H2, R01-OC-H3, R01-OC-M2, R01-V-B2;
R03-PC-2, R03-PC-3, R03-CX-2, R03-CX-5, R03-OC-L1, R03-V-L1;
R04-PC-1, R04-PC-4, R04-PC-6, R04-PC-7, R04-PC-9, R04-PC-11, R04-CX-1, R04-CX-3, R04-CX-7, R04-OC-1, R04-V-2, R04-CH-1;
R05-PC-1, R05-PC-8, R05-PC-12, R05-PC-17, R05-CX-2, R05-CX-3, R05-CX-4, R05-CX-5, R05-CX-6, R05-CX-7, R05-CX-9, R05-OC-1, R05-OC-3, R05-V-1, R05-V-2.

Adjacent A1 remains: an append failure after Word replacement can leave status `current`. Reproduction is recorded in the report.
Stage 1 to 6 counts remain unchanged. Bench baselines match with `dates_wrong=1/0`; every moved assertion is named in the report.

Verbatim final pytest, gate and timing lines:
```text
748 passed in 63.43s (0:01:03)
0
suite_time runs=3 max=64.81 verdict=PASS
```