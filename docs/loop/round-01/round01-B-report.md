Built R1-8, R1-5, then R1-6. Wrote 15 lane B files:

- `tests/fakemodel/{__init__.py,__main__.py,core.py,server.py,recordings.json}`
- `src/casefile/{rules.py,playbook.py}`
- `playbook/{rules.toml,samples/depo-goals.toml}`
- `tests/fixtures/playbook/{malformed-missing-why.toml,unmarked.toml,bad-date.toml}`
- `tests/{test_fakemodel.py,test_rules.py,test_playbook.py}`

All test runs used `scripts/run.sh pytest -q -m "not socket"`.

| Claim | Verified by: CHECK before and after restore | Control: SEED and verbatim RED output |
|---|---|---|
| Six modes and two refusals | `test_modes`: `modes_ok=6 of 6 refusals=2 of 2` | Truncated reason becomes `stop`: `modes_ok=5 of 6 refusals=2 of 2` |
| Case-insensitive rules | `test_each_rule_goes_red`: `rules_red=9 of 9` | Drop `IGNORECASE`: `rules_red=7 of 9` |
| Whole Bates body | `test_each_rule_goes_red`: `rules_red=9 of 9` | `fullmatch` becomes `search`: `rules_red=7 of 9` |
| Malformed entries refused | `test_malformed_fail_closed`: `refused=3 of 3` | Exempt missing `why`: `refused=2 of 3` |
| Version includes file bytes | `test_version_moves`: `version_changed=1` | Remove bytes from digest: `version_changed=0` |

Every SEED exited 1. Every restoration passed `cmp` against its backup and returned green. Final suite last line: `41 passed, 1 deselected in 5.44s`.

Brief discrepancy: line 746 predicts `rules_red=8 of 9`; the actual result is `rules_red=7 of 9`, because mixed-case `Independent Medical Examination` also stops matching. No CHECK needed weakening or replacement.

The HTTP smoke test carries `socket` and remains for the orchestrator. Stand-in compatibility with real Ollama remains provisional until Studio verification.

Catalog IDs checked: #29, #32, #35, #52, #62, #69, #72, #101, #108, #155. Librarian had no entries.