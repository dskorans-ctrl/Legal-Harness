Built W1b: binder roles and prompts, validated `[anon]` tables including Q62, S1/S3/S4 assertions, evidence guard and scoped privacy checks. W1 behavior is preserved; W2 is untouched. No commit.

Every control ran through `scripts/run.sh pytest -q -s`, with green before, seeded RED, byte-identical `cmp=0` restoration and green afterward.

| Claim | Verified by | Control seed and RED text |
|---|---|---|
| Role boundaries | `test_roles.py` | Old prefix rule: `roles_by_name=13 of 15` |
| Non-tty writes nothing | `test_matterinfo.py` | Remove tty guard: `non-tty role prompt wrote matter.toml` |
| Hearing flags | `test_cli.py` | Swap doctor/closing: `hearing_flags=2 of 4` |
| Required evidence | `test_schema.py` | Drop required quote: `schema_evidence=12 of 13` |
| Independent practice check | `test_cards.py` | Reverse sentence and re-pin: `card_practice=2 of 3` |
| Private key path | `test_privacy.py` | Remove path rule: `offenders=5 expected=6` |
| Secret scope | `test_privacy.py` | Match bare prefix: `offenders=7 expected=6` |
| Nested TOML round trip | `test_matterinfo.py` | JSON-dump subtable: `Expected '=' after a key in a key/value pair` |
| Evidence fails closed | `test_outputs.py` | Remove guard: `KeyError: 'quote'` |
| Prompt through start | `test_outputs.py` | Skip role prompt: `Right contains 2 more items:` |

Finding: seed (a) produces **13**, not the brief’s 14, because both ambiguous names fail. The unpredicted regression was `M2: examiner binder assigned ours: DMEreport`; one assertion outside the list, [test_round06_fix1.py:73](/Users/davidskoranski/legal-harness/tests/test_round06_fix1.py:73), was updated to W1b’s role contract.

Files touched: `src/casefile/{matter,matterinfo,outputs,privacy,roles}.py`; `tests/{test_cards,test_cli,test_matterinfo,test_outputs,test_privacy,test_roles,test_schema,test_round06_fix1}.py`; `tests/fixtures/matters/9001.001/matter.toml`.

Librarian entries checked: R01-CX-2, R01-CX-6, R01-CX-10, R01-CX-11, R01-OC-M7, R01-V-B2; R03-CX-5, R03-PC-2, R03-PC-3, R03-V-S1, R03-V-L1; R04-PC-7, R04-OC-1; R05-PC-8, R05-PC-17, R05-CX-4; R06-PC-10, R06-CX-12, R06-CX-16.

Both bench lines are byte-identical to ledger baselines. Stage 5/6 lines are unchanged. `unused_imports=0`.

Verbatim final lines:
```text
792 passed in 66.95s (0:01:06)
gate pytest PASS exit=0
gate privacy PASS offenders=0 scanned=830
gate rules_selftest PASS misses=0 false_hits=0
gate playbook PASS invalid=0 unmarked=0 practice=13 samples=3 version=pb-b0f17098b48d
gate prose PASS dashes=0 files=248
0
```