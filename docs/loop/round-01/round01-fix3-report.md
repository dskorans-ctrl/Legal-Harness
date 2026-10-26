# Round 1 fix cycle 3

Invented probes only. Every command used scripts/run.sh. No commits by this worker.
Socket-free seed baseline: scripts/run.sh pytest -q -m "not socket", 157 passed, 5 deselected. Full baseline: 5 failed, 157 passed.
Each mutation was restored byte-identically with scripts/run.sh cmp, exit 0; raw probe logs: /tmp/casefile-fix3/.
The symlink identity test forces a lexical miss; case-alias tests assert samefile and never skip.

| Row | Before | Fix or new test | GREEN | Teeth seed RED |
|---|---|---|---|---|
| B1 | RED 4 failed | src/casefile/config.py:129; tests/test_config.py:126 | 4 passed | identity comparison -> False: 4 failed |
| B2 | GREEN-seed 157 passed; RED 2 failed | scripts/run_capture.py:11,32,35; tests/test_run_sh.py:102 | 1 passed per exit path | 98 -> 0: 1 failed; 127 -> 0: 1 failed; 126 -> 0: 1 failed |
| S6 | GREEN-seed 157 passed | tests/test_gate.py:76; gate.py:37 already correct | 1 passed | drop false_hits check: 1 failed |
| S9 | GREEN-seed 157 passed | tests/test_doctor.py:236; doctor.py:152 already correct | 1 passed | == 1 -> >= 0: 1 failed |
| S10 | GREEN-seed 157 passed | tests/test_config.py:156; config.py:116 already correct | 1 passed | drop host.path check: 1 failed |
| S2 | GREEN-seed 157 passed | tests/test_cli.py:49; cli.py:38 already correct | 1 passed | return 2 -> 0: 1 failed |
| N1 | RED 4 failed | playbook/rules.toml:8; tests/test_rules.py:142 | 4 passed | separators restored to whitespace only: 4 failed |
| N2 | RED 4 failed | scripts/run_capture.py:17; tests/test_run_sh.py:131 | 4 passed | directory guard -> False: 4 failed |
| N3 | RED 3 failed | scripts/run.sh:12; tests/test_run_sh.py:149 | 3 passed | inside guard -> False: 3 failed |
| N4 | Documentation only | Chair: add fake mode incomplete (done=false) to D18 | N/A | N/A |

B2 follows the chair ruling: command not found is 127 with the required message; non-executable is 126; capture file open/write failures are 98. The chair should record this ruling in D12.
N2 refuses absent arguments, empty strings, nonexistent directories and regular files without writing ./out or deleting the supplied file.
N3 tests literal, case-swapped and symlink paths before toolchain environment setup.
Files changed by worker: src/casefile/config.py, scripts/run.sh, scripts/run_capture.py, playbook/rules.toml, tests/test_config.py, tests/test_run_sh.py, tests/test_gate.py, tests/test_doctor.py, tests/test_cli.py, tests/test_rules.py, this report.
Existing docs/loop/agent-log.md edit was not made or altered by this worker.
Librarian entries checked: Builder pre-flight and Open items; both are empty, with no numbered entries.

Final socket-free suite: 179 passed, 5 deselected in 7.73s.
Final scripts/run.sh pytest -q, exit 1, verbatim last line:
5 failed, 179 passed in 7.66s
Final scripts/run.sh python -m casefile.gate, exit 1, verbatim gate rows and verdict:
```text
gate pytest FAIL exit=1
gate privacy PASS offenders=0 scanned=217
gate rules_selftest PASS misses=0 false_hits=0
gate playbook PASS invalid=0 unmarked=0 version=pb-00be6eb62752
gate prose PASS dashes=0 files=59
1
```
The five socket tests fail at bind with PermissionError in this sandbox. No workaround, skip or test change was applied.
