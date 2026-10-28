Restored W2’s page-level date rule, all 16 moved fixture dates, and the extraction card. Kept seven DEF0002 facts dated `06/20/2025`; `flawed.json` is unchanged. Added “Entries run by the date of the record.”

Every mutation ran green -> RED -> byte-identical `cmp` restore -> green. Tests below used `scripts/run.sh pytest -q`.

| Claim | Verified by | Seed and exact RED text |
|---|---|---|
| Page date outside quote passes | `test_l7_date_rule` | Restore L7: `L7: record date on the cited page but outside the quote was refused` |
| Missing date fails | Same | Disable page guard: `L7: date written on no page was accepted`; `L7: date written only on another page was accepted` |
| Date must parse | Same | Disable parse guard: `L7: unparseable date written on the cited page was accepted` |
| Chronology explains ordering | `test_chronology_record_date_label` | Remove paragraph: `Chronology: record-date convention missing from first paragraph` |
| Empty chronology retains marker | `test_upgraded_fact_is_undated` | Remove marker: `upgrade: undated fact entered chronology` |

Additional finding: the first full run exposed two legacy chronology failures. Preserved `none` beneath the introduction and repinned the shared assertion in `test_memo.py`.

Benchmarks match exactly: flawed `found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=1`; ideal `found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0`.

[Every moved pin, old -> new](/private/tmp/round06-fix3/pins.md). [Full report and evidence](/private/tmp/round06-fix3/report.md).

Files touched:

- `cards/01-records/memo.md`; `src/casefile/{dates,gates,memo}.py`.
- `tests/fixtures/matters/9001.001/{key,ideal}.json`.
- `tests/test_{bench_cli,bench_detail,bench_multi,benchscore,cards,extract,memo,round06_fix2,stage5_exit,stage6_exit}.py`.

Librarian entries checked: R01-CX-7, R01-CX-8, R01-CX-10, R01-CX-11, R01-OC-H2, R01-OC-H3, R01-OC-M8, R01-V-B2, R02-CX-5, R02-OC-H1, R03-PC-2, R03-PC-3, R03-OC-L1, R04-PC-7, R04-PC-11, R04-CH-1, R04-OC-1, R04-V-2, R05-PC-8, R05-PC-17, R05-CX-3, R05-CX-5, R05-CX-6, R05-V-2.

Remaining cycle-2 controls pass. No ledger edit, commit, or git write command.

Verbatim final lines from `scripts/run.sh pytest -q` and `scripts/run.sh python -m casefile.gate`:

```text
786 passed in 66.75s (0:01:06)
0
```