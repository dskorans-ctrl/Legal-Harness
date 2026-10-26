# Round 1 fix cycle 1

Implemented CX-1 through CX-11. Regression acceptance remains blocked by sandbox socket permissions.
Read CLAUDE.md, Librarian.md, spec sections 4, 5, 7, 9, ledger Clarified and HANDOFF.
Librarian checked: Builder pre-flight and Open items a future pass must not re-discover; both empty.
All probes used scripts/run.sh pytest -q with the named test selections. RED locations below are line numbers at execution time.
Mutation backups were restored byte-identically with scripts/run.sh cmp, then the same tests ran GREEN.
Detailed command output: /tmp/casefile-fix1-*.log; structured receipts: /tmp/casefile-fix1-evidence.json.

CX-1 RED tests/test_config.py:122: DID NOT RAISE ConfigError (1 failed). Fix src/casefile/config.py:125 checks checkout and config directory; GREEN: 1 passed in 0.01s.
Teeth: checkout predicate -> False; RED same :122 (1 failed in 0.01s); cmp; GREEN: 1 passed in 0.01s.
CX-2 RED tests/test_privacy.py:53: expected GIF inventory, got [] (1 failed). Fix src/casefile/privacy.py:7 and .gitignore:4 cover formats and case; GREEN: 1 passed in 0.03s.
Teeth: remove .gif -> RED :53; remove GIF ignore -> RED :58, each 1 failed; cmp and each 1 passed. DOTM/SVGZ/JP2/J2K/HIF extension followup also RED, GREEN, seeded RED and restored GREEN.
CX-3 RED tests/test_runlog.py:112: DID NOT RAISE DatabaseError (5 failed). Fix src/casefile/runlog.py:119 rejects existing keys on INSERT in every table, also upgrades existing databases; doctor.py:68 expects 15 triggers; GREEN: 5 passed in 0.03s.
Teeth: duplicate predicate -> WHERE 0; RED :112 (5 failed in 0.03s); cmp; GREEN: 5 passed in 0.02s. Changed append-only count test: omit schema_meta delete trigger -> RED :26; cmp; 1 passed in 0.01s.
CX-4 RED tests/test_run_sh.py:89: cap did not terminate sleeping child within 5 seconds (1 failed in 5.08s). Fix scripts/run.sh:10 and scripts/run_capture.py:26 kill child process group, reap child, return 97; GREEN: 1 passed in 0.10s.
Teeth: group kill -> pass; RED :89 (1 failed in 5.08s); cmp; GREEN: 1 passed in 0.09s. Full wrapper suite: 8 passed in 5.38s, including child status, exact cap, stderr and capture failure.
CX-5 RED tests/test_model.py:102,108: DID NOT RAISE ModelError; tests/test_doctor.py:178: context PASS on missing/zero/negative counts. Fix model.py:76, doctor.py:124, tests/fakemodel/core.py:121; GREEN: 18 passed in 0.07s.
Teeth: disable done guard -> 6 failed at model :102,108; remove counts_ok -> isolated 12 failed at doctor :186; force fake done=True -> 1 failed at model :108; each cmp and GREEN (6, 12, 1 passed).
CX-6 RED tests/test_privacy.py:65,83: missing first-component and symlink offenders (2 failed). Fix src/casefile/privacy.py:17,35 checks casefolded first component and resolved symlink targets; GREEN: 2 passed in 0.01s.
Teeth: restore lexical prefix -> RED :65; bypass link check -> RED :83, each 1 failed in 0.01s; each cmp; each GREEN: 1 passed in 0.01s.
CX-7 RED tests/test_rules.py:116: set() != payment rule (6 failed). Fix playbook/rules.toml:21 checks payment and doctor terms in either order within 120 characters; GREEN: 7 passed in 0.01s, including good examples.
Teeth: restore original payment regex; RED :116 (6 failed, 1 passed in 0.02s); cmp; GREEN: 7 passed in 0.01s.
CX-8 RED tests/test_rules.py:123: set() != no-dme-ime (8 failed). Fix playbook/rules.toml:8 uses \s+ for both spelled-out labels; GREEN: 8 passed in 0.01s.
Teeth: restore literal spaces; RED :123 (8 failed in 0.03s); cmp; GREEN: 8 passed in 0.01s.
CX-9 RED tests/test_doctor.py:204,205: missing second version call or wrong verdict (4 failed). Fix src/casefile/doctor.py:153 and tests/conftest.py:135 checks both versions and labels the reason versions only; GREEN: 4 passed in 0.02s.
Teeth: verdict checks first code only -> RED :204 (1 failed, 3 passed); helper omits second command -> RED :209,210 (4 failed); each cmp; each GREEN: 4 passed in 0.02s.
CX-10 Test gap: seeded removal of doctor.py:126 done_reason guard left old probes GREEN (3 passed). New READY/length and READY/done=false tests RED at tests/test_doctor.py:219 (1 failed, 1 passed); fix tests/test_doctor.py:223; restore original production guard; GREEN: 2 passed in 0.02s.
Teeth: remove done_reason guard -> RED :219; disable model done guard -> RED :219, each 1 failed, 1 passed in 0.03s; each cmp; each GREEN: 2 passed in 0.02s.
CX-11 Test gap: excluding context from exit aggregation left old probes GREEN (20 passed). New exit assertions RED at tests/test_doctor.py:68,74,81,88,99,191,225: 0 != 1 (20 failed); fix these tests plus isolation fixture :231; restore aggregation; GREEN: 20 passed in 0.11s.
Teeth: failed += not ok and name != "context"; RED at all seven assertions (20 failed in 0.13s); cmp; GREEN: 20 passed in 0.10s.

Additional changed suffix test teeth: remove .pdf -> RED tests/test_privacy.py:45 (10 != 11); cmp; GREEN: 1 passed in 0.03s.
A model type-guard mutation initially survived due to doctor's redundant guard; the doctor token test now supplies Answer values directly to isolate its guard, proving all 12 cases RED.
An overbroad temporary count edit also changed blocked == 8 to 15; corrected, then count mutation rerun RED, cmp, GREEN.
CX-10 and CX-11 production logic was already correct; their RED baselines necessarily used the reported mutants to expose missing test coverage.

Files changed by this worker:
.gitignore; playbook/rules.toml; scripts/run.sh; scripts/run_capture.py;
src/casefile/config.py; src/casefile/privacy.py; src/casefile/runlog.py; src/casefile/model.py; src/casefile/doctor.py;
tests/conftest.py; tests/fakemodel/core.py; tests/test_config.py; tests/test_privacy.py; tests/test_runlog.py;
tests/test_run_sh.py; tests/test_model.py; tests/test_doctor.py; tests/test_rules.py; docs/loop/round-01/round01-fix1-report.md.
No protected records or repo .git edited. Other working-tree changes left intact. Invented data only. No real OCR smoke test built.
Fresh git diff --check exited 0. Full pytest included all socket tests; five fail socket.bind with PermissionError [Errno 1] Operation not permitted. No skip or exemption added.
The chair must rerun both regression commands with local binding permitted. Gate cannot print 0 in this sandbox; its other four rows pass.

Verbatim last line from scripts/run.sh pytest -q:
5 failed, 141 passed in 6.10s
Gate output from scripts/run.sh python -m casefile.gate:
gate pytest FAIL exit=1
gate privacy PASS offenders=0 scanned=202
gate rules_selftest PASS misses=0 false_hits=0
gate playbook PASS invalid=0 unmarked=0 version=pb-03c17e804495
gate prose PASS dashes=0 files=54
1

## Follow-up
CX-7 now pairs payment with doctor/examiner/exam terms in either order within 60 characters, stopping at . ; : ? ! or a newline; report alone is excluded.
The period in Dr. belongs to the doctor term so the passive payment example remains caught.
New pattern: `\b(?:(?:paid|pays|paying|payment|compensat(?:ed|ion))\b[^.;:?!\r\n]{0,60}\b(?:doctor|dr|examiner|exam|examination)|(?:doctor\b|dr\b\.?|examiner\b|exam\b|examination\b)[^.;:?!\r\n]{0,60}\b(?:paid|pays|paying|payment|compensat(?:ed|ion)))\b`
Tests: both supplied benefits sentences must pass; all four supplied payment examples must fail the rule check (two existing cases retained, two added).
Initial RED: scripts/run.sh pytest -q tests/test_rules.py -k 'benefit_payment_prose_clean or doctor_payment_any_order': 2 failed, 8 passed.
Teeth RED: restored the original 120-character [\s\S] payment pattern; scripts/run.sh pytest -q tests/test_rules.py -k benefit_payment_prose_clean: 2 failed, 32 deselected.
Restore: scripts/run.sh cmp /tmp/casefile-round01-followup-rules.fixed playbook/rules.toml exited 0 after copying the fixed backup back.
GREEN: scripts/run.sh pytest -q tests/test_rules.py: 34 passed in 0.02s, including all existing bad-output cases.
Gate: scripts/run.sh python -m casefile.gate exited 1; pytest row: 5 failed, 145 passed in 6.59s; all five failures are sandbox socket.bind PermissionError.
Gate privacy, rules_selftest, playbook and prose rows PASS. No socket workaround or exemption added; full acceptance still requires socket binding.
