Fixed all 13 findings. No commits. [Report with exact commands, RED logs, and baseline changes](.workflow/scratch/round07-fix1-report.md).

| Claim | Verified by | Control seed → RED text |
|---|---|---|
| H1 variants/aliases | anon tests | Drop given variant → `H1: listed variant escaped replacement` |
| M1 package pages | stage 7 exit | Disable narrowing → `M1: default JSON carries unused pages` |
| M2 ambiguity | ambiguity tests | Choose last identity → `M2: ambiguous mention assigned an identity` |
| M3 dates | date tests | Share detector patterns → `M3: check shares replacer blind spot` |
| M4 grouped splits | fact tests | Group by page → `assert (2 == 1)` |
| L1 restoration | restore test | Restore loose offsets → `L1: loose prose rewritten` |
| L2 lines | line tests | Allow newline consumption → `L2: page lost a line break` |
| L3 DOB | label tests | Remove labels → `L3: labelled birth date became offset` |
| L4 diagnostics | validation tests | Print name key → `L4: private name in validation message` |
| L5 contacts | separator tests | Require dashes → `L5: contact separator escaped` |
| L6 second pass | second-pass test | Remove either exemption → `L6: placeholder or authorized kept variant blocks` |
| L7 quotes | draft tests | Disable folding/error guard → `L7: quote verification silently skipped` |
| L8 totals | totals test | Constant summary → expected `package_ok=1 of 2 draft_ok=1 of 1` differs |

All 19 mutation controls restored with `cmp`, then passed GREEN.

Files: six affected source modules; `test_anon`, `test_anon_job`, `test_brief`, `test_facts`, `test_matterinfo`, `test_stage7_exit`; new `variant-page.txt`; report.

Librarian entries checked:
R01-CX-7, R01-CX-8, R01-CX-9, R01-CX-10, R01-CX-11, R01-OC-H2, R01-OC-H3, R01-OC-M2, R01-V-B2;
R02-CX-5, R02-CX-7, R02-OC-H1;
R03-PC-2, R03-PC-3, R03-CX-2, R03-CX-5, R03-OC-L1, R03-V-L1, R03-V-S1;
R04-PC-4, R04-PC-6, R04-PC-7, R04-PC-11, R04-CX-3, R04-CX-7, R04-OC-1, R04-V-2, R04-CH-1;
R05-PC-7, R05-PC-8, R05-PC-12, R05-PC-17, R05-CX-4, R05-CX-5, R05-CX-6, R05-CX-7, R05-OC-3, R05-V-1, R05-V-2;
R06-PC-3, R06-PC-6, R06-PC-12, R06-CX-1, R06-CX-5, R06-CX-12, R06-CX-16, R06-CX-18, R06-CH-2.

Both bench lines and stage 5/6 baselines unchanged. Stage 7 totals: packages `1 of 1` → `2 of 2`, answers `+6` → `+8`; added default-page check `15` total / `13` packaged. Exact lines are in the report.
Additional RED recorded: the old matter-info assertion expected a private name in its diagnostic; corrected to table/index.
Timing: `suite_time runs=3 max=80.31 verdict=PASS`. Full pytest and gate last lines:

```text
907 passed in 82.73s (0:01:22)
0
```