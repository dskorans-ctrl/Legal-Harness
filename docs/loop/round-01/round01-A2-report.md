Implemented R1-4 and R1-7.

Files written:

- [config.py](/Users/davidskoranski/legal-harness/src/casefile/config.py), [config.example.toml](/Users/davidskoranski/legal-harness/config.example.toml), [test_config.py](/Users/davidskoranski/legal-harness/tests/test_config.py)
- [runlog.py](/Users/davidskoranski/legal-harness/src/casefile/runlog.py), [test_runlog.py](/Users/davidskoranski/legal-harness/tests/test_runlog.py)
- Updated [cli.py](/Users/davidskoranski/legal-harness/src/casefile/cli.py) and [conftest.py](/Users/davidskoranski/legal-harness/tests/conftest.py), which now calls `config.load` directly.

Every test run used `scripts/run.sh pytest -q -m "not socket"`.

| Claim | Verified by: baseline and restored CHECK output | Control: SEED and RED output |
|---|---|---|
| Seven config refusals | `test_rejections`: `rejected=7 of 7` | Unknown-key raise replaced with `continue`: `rejected=6 of 7` |
| CLI rejects unknown keys | `test_config_show`: `unknown_key_cli_exit=2` | Same seed: `unknown_key_cli_exit=0`; `4 failed, 21 passed in 5.85s` |
| All eight writes blocked | `test_append_only`: `blocked_writes=8 of 8` | `approvals_no_delete` body replaced with `SELECT 1`: `blocked_writes=7 of 8`; `1 failed, 24 passed in 6.46s` |
| Only successful doctor jobs count | `test_test_job_count`: `test_jobs=1` | Removed answer-status filter: `test_jobs=2`; `1 failed, 24 passed in 5.74s` |

Every mutation was restored byte-identically and verified with `cmp`. Restored suite outputs were `25 passed in 6.16s`, `25 passed in 6.02s`, and finally **`25 passed in 5.34s`**.

Brief checks requiring correction:

- Lines 683 to 685: missing-file shell CHECK printed `PASS` both before and under the unknown-key seed. Retained it and strengthened `test_config_show` with an unknown-key CLI refusal check.
- Lines 697 to 699: the trigger seed leaves `test_jobs=1`. Added the separate status-filter seed above to calibrate that CHECK.

Catalog checked: #48, #69, #96, #101, #102, #111; “Fail-open CLI default”; “Probe certifies its own mechanism.” Librarian has no entries.

Lane B files untouched. No network, commits, or socket tests.