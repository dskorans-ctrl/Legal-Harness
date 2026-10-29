Built all five fixes. No commit. Starting tip was `2ef748a`, the verifier-record commit after `68f57fa`.

Tests below ran through `scripts/run.sh pytest -q tests/test_round07_fix3.py -k <test>`.

| Claim | Verified by | Control seed → RED text |
|---|---|---|
| Age forms replaced | `test_age_forms` | Old AGE pattern → `F1: stated age survived replacement` |
| Independent age check | `test_age_detector_independent` | Disable checker → `F1: independent age detector missed raw age` |
| Distinct ages numbered | `test_distinct_ages` | Always `[AGE]` → `F2: distinct ages share a placeholder` |
| Separate age restoration | `test_distinct_ages` | Restore first group → assertion failure restoring age 45 |
| Literal age tags preserved | `test_distinct_ages` | Remove AGE grammar → `assert '[AGE-2]' == '[SRC-1]'` |
| Ages discovered before rendering | `test_packet_age_preallocation` | Disable discovery → `F2: metadata rendered before all ages discovered` |
| Ordinal dates replaced | `test_ordinal_dates` | Old FULL_DATE → `F3: ordinal date partly replaced` |
| Independent day check | `test_day_detector_independent` | Disable checker → `F3: raw day beside month escaped check` |
| Initial variants absorbed | `test_initial_variants` | Remove variants → `F4: initial is not a listed variant` |
| Leftover initials blocked | `test_initial_detector` | Disable checker → `F4: lone initial before person placeholder escaped` |
| Non-tty role warning | `test_non_tty_role_warning` | Suppress warning → `F5: non-tty role warning absent or discloses binder name` |

All 11 seeds went RED, with byte-identical `cmp` restoration and GREEN reruns. [Exact mutation output](/private/tmp/casefile-r7-fix3/mutations.log).

Files touched: [anon.py](/Users/davidskoranski/legal-harness/src/casefile/anon.py), [brief_out.py](/Users/davidskoranski/legal-harness/src/casefile/brief_out.py), [test_anon.py](/Users/davidskoranski/legal-harness/tests/test_anon.py), [test_round07_fix3.py](/Users/davidskoranski/legal-harness/tests/test_round07_fix3.py). `anon_job.py` unchanged.

Bench lines and all stage 5, 6 and 7 measured lines are byte-identical; no stage 7 measurement changed.
Drafter rule 2 old: `Use [CLAIMANT], [EMPLOYER], [DOB] and [AGE] without numbers.`
New: `Use [CLAIMANT], [EMPLOYER] and [DOB] without numbers; preserve [AGE] for one distinct age or [AGE-n] for multiple ages.`

Additional finding, unchanged: the existing date checker falsely rejects `Stages 44 and 45.` Legacy ambiguous `[AGE]` prose now refuses restoration.

Librarian read fully; checked against: R01-CX-7, R01-CX-8, R01-CX-10, R01-CX-11, R01-OC-H2, R01-OC-H3, R01-OC-M8, R01-V-B2, R02-CX-5, R03-PC-2, R03-PC-3, R03-CX-5, R03-OC-L1, R04-PC-9, R04-PC-11, R04-OC-1, R04-CH-1, R05-PC-8, R05-PC-17, R05-CX-5, R05-V-2, R06-CX-16, R06-CH-2.

Timing: `suite_time runs=3 max=84.61 verdict=PASS`. Unused imports: `0`. Verbatim final lines, full pytest then gate:

```text
993 passed in 84.76s (0:01:24)
0
```