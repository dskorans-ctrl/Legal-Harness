# Round 6 fix cycle 3

Restored W2/D46: a non-empty fact date must occur on its cited page and parse. Removed the withdrawn L7 gate and helper, restored the extraction card, and inverted the affected L7 checks. Restored all 16 changed key/ideal date values to HEAD; retained all seven new DEF0002 facts dated 06/20/2025. The flawed fixture is byte-identical to the inherited version.

The chronology's first paragraph now says `Entries run by the date of the record.` It is checked against the firm rules in the saved document. An empty chronology keeps `none` beneath this paragraph.

Every moved pin and the complete inherited-tree-to-cycle-3 diff are in [pins.md](pins.md). The benchmark lines match the requested counts without discrepancies. Flawed exits 1; ideal exits 0.

## Mutation evidence

Every row ran baseline green, applied the seed, verified non-identical bytes with cmp, observed exit 1 with the exact assertion text, restored from its pre-seed copy with cmp=0, and confirmed green. Every pytest invocation used scripts/run.sh and a separate PYTHONPYCACHEPREFIX.

| Claim | Verified by | Seed | Exact RED text |
|---|---|---|---|
| Date on cited page outside quote passes | scripts/run.sh pytest -q tests/test_round06_fix2.py::test_l7_date_rule | Restore cycle 2 gates.py and dates.py | L7: record date on the cited page but outside the quote was refused |
| Date absent from cited page fails | Same test | Disable page occurrence guard | L7: date written on no page was accepted; L7: date written only on another page was accepted |
| Invalid calendar date fails | Same test | Disable parse guard | L7: unparseable date written on the cited page was accepted |
| Chronology states record-date convention first | scripts/run.sh pytest -q tests/test_round06_fix2.py::test_chronology_record_date_label | Remove introductory paragraph | Chronology: record-date convention missing from first paragraph |
| Empty chronology keeps marker and no legacy facts | scripts/run.sh pytest -q tests/test_memo.py::test_upgraded_fact_is_undated | Remove empty chronology marker | upgrade: undated fact entered chronology |

Machine-readable results: mutations.json. Exact red and green logs have the seed names as prefixes.

## Additional finding

The first full post-edit run returned `2 failed, 784 passed in 67.55s (0:01:07)`. Both failures were the shared `tests/test_memo.py:390` legacy-upgrade assertion: `upgrade: undated fact entered chronology`. Adding the introduction displaced the old `none` marker. Preserved that marker and changed the exact expected section from `['none']` to `['Entries run by the date of the record.', 'none']`. This is the additional load-bearing assertion outside the initially identified files. It retains the no-legacy-fact-in-chronology check and has its own red seed. The memo extraction card was also necessarily restored so it no longer instructs the model to apply the withdrawn rule.

## Files touched by this worker

- cards/01-records/memo.md
- src/casefile/dates.py
- src/casefile/gates.py
- src/casefile/memo.py
- tests/fixtures/matters/9001.001/key.json
- tests/fixtures/matters/9001.001/ideal.json
- tests/test_bench_cli.py
- tests/test_bench_detail.py
- tests/test_bench_multi.py
- tests/test_benchscore.py
- tests/test_cards.py
- tests/test_extract.py
- tests/test_stage5_exit.py
- tests/test_stage6_exit.py
- tests/test_round06_fix2.py
- tests/test_memo.py

Evidence files are under /private/tmp/round06-fix3 only. No ledger edit, commit or git write command. Independent concurrent changes to .workflow/LEDGER.md, docs/loop/agent-log.md and docs/loop/questions-for-owner.md were preserved. All other tracked files match the worker's initial snapshot.

## Librarian entries checked

Read Librarian.md in full. Applied: R01-CX-7, R01-CX-8, R01-CX-10, R01-CX-11, R01-OC-H2, R01-OC-H3, R01-OC-M8, R01-V-B2, R02-CX-5, R02-OC-H1, R03-PC-2, R03-PC-3, R03-OC-L1, R04-PC-7, R04-PC-11, R04-CH-1, R04-OC-1, R04-V-2, R05-PC-8, R05-PC-17, R05-CX-3, R05-CX-5, R05-CX-6, R05-V-2.

These cover scoped source evidence, exact fixture and pin expectations, unmasked and cache-isolated mutation controls, honest chronology wording, output rules in both directions, stable placement and source provenance, preserved legacy behavior, and closed test endpoints. No stronger claim is made about the recorded integrity limit or adjacent A2 date-update limit; neither changed.

## Final verification

Commands: `scripts/run.sh pytest -q` and `scripts/run.sh python -m casefile.gate`, both exit 0. The full suite includes every remaining fix cycle 2 control.

Verbatim last lines:

```text
786 passed in 66.75s (0:01:06)
0
```
