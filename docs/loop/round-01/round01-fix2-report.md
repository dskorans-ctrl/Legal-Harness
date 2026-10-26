# Round 1 fix cycle 2 report

All commands used scripts/run.sh. All probe sentences are invented. No client data or binary artifacts added.
Initial regression run: scripts/run.sh pytest -q tests/test_fix_cycle2.py --tb=short -> 12 failed in 0.63s.
M1 was also isolated before its fix: 1 failed in 0.04s, specifically on the charge-for-exam sentence.
Per-row checks: scripts/run.sh pytest -q tests/test_fix_cycle2.py::<test> --tb=short.
Each seed changed one load-bearing line; scripts/run.sh cmp returned 0 after byte-identical restore, then GREEN.

| Row | RED line | Fix file:line | GREEN line after cmp | Teeth seed -> RED line |
| --- | --- | --- | --- | --- |
| H1 | FAILED tests/test_fix_cycle2.py::test_h1_ocr_unverified_with_two_successful_stubs | src/casefile/doctor.py:171 | 1 passed in 0.26s | False -> codes == [0, 0] -> 1 failed in 0.28s |
| H2 | FAILED tests/test_fix_cycle2.py::test_h2_exam_label_variants | playbook/rules.toml:8 | 1 passed in 0.02s | restore original acronym/phrase patterns -> 1 failed in 0.03s |
| H3 | FAILED tests/test_fix_cycle2.py::test_h3_hiring_and_fees_scoped_to_doctor_clause | playbook/rules.toml:22 | 1 passed in 0.04s | doctor-clause pattern -> bare hired/retained/fees pattern -> 1 failed in 0.04s |
| M1 | FAILED tests/test_fix_cycle2.py::test_m1_doctor_billing_and_engagement | playbook/rules.toml:24 | 1 passed in 0.02s | billing/request pattern -> referral-only pattern -> 1 failed in 0.02s |
| M2 | FAILED tests/test_fix_cycle2.py::test_m2_unit_is_required | src/casefile/rules.py:53 | 1 passed in 0.02s | unit -> unit="text" -> 1 failed in 0.03s |
| M3 | FAILED tests/test_fix_cycle2.py::test_m3_treatment_cost_words | playbook/rules.toml:43 | 1 passed in 0.02s | restore original bill-word group -> 1 failed in 0.02s |
| M5 | FAILED tests/test_fix_cycle2.py::test_m5_bates_ranges_lists_and_no_pinpoints | playbook/rules.toml:57 | 1 passed in 0.02s | restore single-Bates-only pattern -> 1 failed in 0.03s |
| M6 | FAILED tests/test_fix_cycle2.py::test_m6_every_failure_has_action | src/casefile/doctor.py:221 | 1 passed in 0.06s | action append -> reason = reason -> 1 failed in 0.05s |
| M7 | FAILED tests/test_fix_cycle2.py::test_m7_missing_matters_is_not_created | src/casefile/doctor.py:45 | 1 passed in 0.02s | name == "state" -> name != "playbook" -> 1 failed in 0.03s |
| M8 | FAILED tests/test_fix_cycle2.py::test_m8_matters_beside_config_and_exact_errors | src/casefile/config.py:128 | 1 passed in 0.01s | restore source.parent restriction -> 1 failed in 0.02s |
| L1 | FAILED tests/test_fix_cycle2.py::test_l1_schema_reason_only_reports_this_run | src/casefile/doctor.py:70 | 1 passed in 0.02s | restore exercised-by-test-suite claim -> 1 failed in 0.03s |
| L2 | FAILED tests/test_fix_cycle2.py::test_l2_runlog_job_blocked_by_context | src/casefile/doctor.py:175 | 1 passed in 0.02s | drop context dependency -> 1 failed in 0.03s |

Changed: playbook/rules.toml; src/casefile/{doctor,rules,config}.py;
tests/{test_fix_cycle2,test_doctor,test_rules,test_config,conftest}.py; this report.
Four legacy context-free hiring/fee probes now name a doctor or exam, as the explicit H3 clause requirement requires.
OCR test oracle now always expects FAIL until stage 3; no socket test or gate was weakened.
Protected files and existing chair changes were left untouched. M4 and L3 remain carried.
Librarian entries checked: Builder pre-flight and Open items; both sections are empty, with no numbered entries.

Full command: scripts/run.sh pytest -q (exit 1). Verbatim last line:
```text
5 failed, 157 passed in 6.37s
```
Exactly five socket tests fail at bind with PermissionError: [Errno 1] Operation not permitted. No workaround applied.
Gate command: scripts/run.sh python -m casefile.gate (exit 1). Verbatim verdict output:
```text
gate pytest FAIL exit=1
gate privacy PASS offenders=0 scanned=212
gate rules_selftest PASS misses=0 false_hits=0
gate playbook PASS invalid=0 unmarked=0 version=pb-8c41a5ae7727
gate prose PASS dashes=0 files=57
1
```
Gate child pytest has the same five bind failures; complete raw outputs: /tmp/casefile-fix2-{pytest,gate}.log.
Per-row seed and restored pytest logs: /tmp/casefile-fix2-<ROW>-{seed,restore}.log.
