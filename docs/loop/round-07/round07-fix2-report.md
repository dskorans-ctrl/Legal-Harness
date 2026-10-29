Implemented 11 findings and L1’s prose-date fix. No commit.

**L1 remains partial:** page-exact quotes can retain a different date spelling from canonical prose. [brief.py:232](/Users/davidskoranski/legal-harness/src/casefile/brief.py:232) requires the original page match, contradicting the absolute no-mixed-form rule. [Reproduction](/private/tmp/round07-fix2/date-conflict.txt).

[34 mutation controls](/private/tmp/round07-fix2/controls.json) completed baseline GREEN, seeded RED, byte-identical restore (`cmp=0`), GREEN. B/A/S below are `test_brief.py`, `test_anon.py`, and `test_stage7_exit.py`, run through `scripts/run.sh pytest -q`.

| Claim | Verified by | Seed -> RED text |
|---|---|---|
| H1/M3 | B numeric cases | Quote bypass/digit bags -> `unsupported whole numeric token accepted` |
| H2 | B uncited cases | Ignore uncited evidence -> `uncited evidence published as final` |
| H2 footnotes | B Word cases | Drop anchored notes -> `Word footnote citations lost or associated with wrong paragraph` |
| M1 | S package surfaces | Extra pages/fields -> `JSON includes pages whose full text is not displayed`; `package facts carry more than quote and cite` |
| M2 | S rules | Drop rule IDs -> `package omits a rule id or its source text` |
| M4 | S open items | Suppress section/count -> `package omits unread-page section`; `status omits open-item count` |
| L1 prose | A dates | Restore unpadded dates -> `prose date differs from sole page spelling` |
| L2/L3 | B header/summary | Blank matter/count cites only -> `restored brief header lost matter number`; `check counters do not measure the same operations` |
| L4 | B saved marks | Remove formatting/Bates -> `failure marks are not bold and highlighted`; `failure mark lost Bates stamp` |
| L5 | B style | Disable dash detection -> `prohibited dash passed as final prose` |
| L6 | A/S privacy | Disable ages/anchor/filter -> `stated age survived anonymization`; anchor/review controls also RED |
| Original W4/W5 | B/S | All 12 brief seeds caught, including publication, permissions, source restoration, partials and leaks |
| Additional fixes | B/cards | Broad numeric labels/old pin -> `numeric label became part of the asserted number`; `card versions differ from pinned values` |

Files touched: `src/casefile/{anon,anon_job,brief,brief_in,brief_out,outputs}.py`; `playbook/hearing.toml`; `tests/{test_anon,test_brief,test_cards,test_stage7_exit}.py`; `tests/fixtures/anonymizer/9001.001/DEF0001.txt`.

Necessary scope extensions: shared styling in `outputs.py`, the one-line playbook formatting rule, and the `03-CLIENT` version pin (`dbead8527c45` -> `3adfe3d8de7f`).

Librarian IDs checked: R01-CX-10, R01-CX-11, R01-P-1, R02-CX-7, R03-PC-3, R03-CX-2, R03-CX-5, R03-OC-L1, R04-PC-7, R04-CX-1, R04-OC-1, R04-V-2, R04-CH-1, R05-PC-17, R05-CX-3, R05-CX-5, R06-PC-6, R06-PC-12, R06-CX-1, R06-CX-16, R06-CH-2.

Bench and stage 5/6 lines are unchanged. Stage 7 old -> new: review `30 -> 24`; default pages `13 -> 10`; good checks `10/10 -> 44/44`; bad checks `9/10 -> 43/44`. [Verbatim pairs](/private/tmp/round07-fix2/stage7-old-new.txt).

Unpredicted reds recorded: card pin and compact numeric labels, both fixed; initial timing maximum 103.84 seconds. Final timing: `suite_time runs=3 max=81.61 verdict=PASS`; `unused_imports=0`.

Verbatim last lines of full pytest and gate, respectively:

```text
937 passed in 82.14s (0:01:22)
0
```