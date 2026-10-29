Built W2 and W3: reversible anonymization, private keys, entity passes, name-list halt, anchor selection and fail-closed checks. No commits; W5 untouched.

Unresolved brief conflict: [line 155](/Users/davidskoranski/legal-harness/.workflow/scratch/round07-build-brief.md:155) requires names in non-tty halt output; [line 329](/Users/davidskoranski/legal-harness/.workflow/scratch/round07-build-brief.md:329) puts that output outside the boundary. The prescribed halt behavior remains pending chair ruling.

Checks below used `scripts/run.sh pytest`; every seed had a green baseline, fresh bytecode, RED, byte-identical `cmp` restoration and green rerun.

| Claim | Verified by | Control: seed → RED |
|---|---|---|
| W2a dates | `test_code_sixteen` | Skip date check → `check_code=15 of 16` |
| W2b stamps | `test_pages_and_goldens` | Drop pattern protection → `stamps_kept=14 of 15` |
| W2c restoration | Same | Canonical restore only → `anon_pages=0 of 14` |
| W2d spellings | Same | Stop recording spellings → `anon_pages=0 of 14` |
| W2e lines | Same | Consume date newline → `lines_kept=13 of 14` |
| W2f stability | `test_packet_stable_and_key` | Restart numbering → `anon_stable=0` |
| W2g employer | `test_text_32` | Number employer → `anon_text=31 of 32` |
| W2h mode | `test_packet_stable_and_key` | Default umask → `key_mode: not 600` |
| W2i name exemption | `anon_name_exempt` | Remove exemption → `valid answer refused` |
| W2j boundaries | `test_text_32` | Drop boundary → `anon_text=31 of 32` |
| W3a page verification | `test_entity_four` | Remove drop → `entity_pass=3 of 4` |
| W3b non-tty halt | `test_halt_four` | Permit write → `DID NOT RAISE` |
| W3c model failure | `test_second_three_and_order` | Treat 404 as pass → `second_pass=2 of 3` |
| W3d ordering | Same | Model before code → `check_code must run before second pass` |
| W3e disclosure | Same | Print hit value → `key_leak=1` |

Additional findings fixed and independently seeded: OCR folding, multiline streets, month case, grouped IDs, unseen year tags and missing audit receipts. [Seven extra controls](/private/tmp/round07-extra-controls.log).

Files touched: `src/casefile/{anon.py,anon_job.py,gates.py}`; `cards/07-anonymize/entities.md`; `schemas/anonymize.schema.json`; `tests/{test_anon.py,test_anon_job.py,test_cards.py,test_gates.py}`; anonymizer fixtures `DEF0001.txt`, `EMP0001.txt`, `entities.json`, `entities-empty.json`, `entities-second-hit.json`. No frozen or lane B files changed.

Librarian entries checked: R01-CX-2, R01-CX-5, R01-CX-9, R01-CX-10, R01-CX-11, R01-OC-M2, R02-CX-5, R02-CX-7, R02-V-F1, R03-PC-2, R03-PC-3, R03-CX-2, R03-CX-5, R03-OC-L1, R03-V-L1, R04-PC-1, R04-PC-4, R04-PC-6, R04-PC-7, R04-CX-1, R04-CX-3, R04-CX-7, R04-OC-1, R04-CH-1, R04-V-2, R05-PC-8, R05-PC-17, R06-PC-3, R06-CX-1, R06-CX-2, R06-CX-16.

W2 full suite: 800 passed, gate 0. Final full pytest and gate last lines, verbatim:

```text
808 passed in 77.06s (0:01:17)
gate prose PASS dashes=0 files=258
0
```