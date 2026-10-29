Built W4: package rendering, full conflict pages, `--pages all`, private publication, Word draft parsing, fact checks, failure markers, CLI parsers, and four draft fixtures. No commits or frozen/lane-A edits.

CHECK: `package_ok=9 of 9 draft_ok=10 of 10`; 23 tests passed; `unused_imports=0`.

All six seeds went RED, restored byte-identically by `cmp`, then returned GREEN. Test nodes below are in `tests/test_brief.py`, run through `scripts/run.sh pytest`.

| Claim | Verified by | Control seed and exact RED text |
|---|---|---|
| Full conflict pages | `test_package_contract[4]` | (a) facts-only excerpts: `package conflicts must include both full pages in defense-first order` |
| Private files | `test_package_contract[7]` | (b) default umask: `package files mode must be 600` |
| Failed quotes marked | `test_draft_contract[9]` | (c) omit marker: `failed quote check not marked in saved document` |
| Quoted cites excluded | `test_draft_contract[4]` | (d) parse quoted cites: `quoted cite became a paragraph cite` |
| Numbers checked against page | `test_draft_contract[6]` | (e) read quote instead: `digit check must read the page when no quote exists` |
| Placeholder digits excluded | `test_draft_contract[6]` | (f) scan date offset: `placeholder offset counted as a prose number` |

Finding for chair: W5 seed (c) produces `checks=2 of 10 failed=8`, rather than the brief’s predicted `0 of 10`; the two unquoted paragraphs still pass. Also caught and fixed a firm-rule phrase escaping across a citation boundary.

Files touched: `src/casefile/{brief.py,cli.py}`, `tests/test_brief.py`, and `tests/fixtures/anonymizer/9001.001/{draft,draft-bad-placeholder,draft-real-name,draft-bad-quote}.txt`. No `.docx` committed.

Librarian entries checked: R01-CX-2, R01-CX-10, R01-OC-M2, R02-CX-7, R03-PC-2, R03-PC-3, R03-CX-2, R03-OC-L1, R03-V-L1, R04-PC-4, R04-PC-7, R04-CX-1, R04-OC-1, R04-V-2, R04-CH-1, R05-PC-12, R05-PC-17, R05-CX-3, R05-CX-5, R06-PC-6, R06-CX-1, R06-CX-16.

Verbatim final pytest and gate lines:

```text
815 passed in 85.40s (0:01:25)
```

```text
gate pytest PASS exit=0
gate privacy PASS offenders=0 scanned=427
gate rules_selftest PASS misses=0 false_hits=0
gate playbook PASS invalid=0 unmarked=0 practice=13 samples=3 version=pb-b0f17098b48d
gate prose PASS dashes=0 files=254
0
```