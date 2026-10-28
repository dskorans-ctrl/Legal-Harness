Found nine correctness issues. **CONFIRMED** below means traced through the code, not runtime-tested. No files modified; no app, model, tests or scripts run. Pipeline examples assume valid nonces and completion counts.

1. **high | CONFIRMED | [gates.py:74](/Users/davidskoranski/legal-harness/src/casefile/gates.py:74)**  
   **Coverage identifies pages by their first stamp, allowing one cited page to mark another unread page as read.**  
   Scenario: page A has stamps `("MED0001",)` and page B has `("MED0001","MED0002")`, because B references A. An answer quotes only A. Lookup adds `MED0001` to `cited`; the final coverage loop marks both pages `read`. Their coverage entries also collapse into one dictionary key. No uniqueness check protects `ask()`.

2. **high | CONFIRMED | [quotes.py:55](/Users/davidskoranski/legal-harness/src/casefile/quotes.py:55)**  
   **Quote matching accepts fragments inside longer numbers and words as verified quotations.**  
   Scenario: source page says `Take 15 mg daily.`; answer supplies quote `5 mg daily.` and text `Take 5 mg daily.`. The quote passes the exact substring rung, and the text’s digit `5` appears in that shortened quote, so all gates pass. Likewise, `able to work` matches inside `unable to work`.

3. **high | CONFIRMED | [quotes.py:31](/Users/davidskoranski/legal-harness/src/casefile/quotes.py:31)**  
   **OCR folding removes numeric range separators and minus signs, allowing invented numbers to become verified.**  
   Scenario: source is `Dose 1-\n2 mg.`; answer quotes `Dose 12 mg.`. The OCR rung removes `-\n`, producing an exact match. Text `Dose 12 mg.` also passes the digit-run check. The dehyphenation needs to distinguish broken words from numeric punctuation.

4. **med | CONFIRMED | [runlog.py:179](/Users/davidskoranski/legal-harness/src/casefile/runlog.py:179)**  
   **The v1 upgrade commits before restoring all append-only protections, so the complete upgrade is not atomic.**  
   Scenario: an interrupt or SQLite error occurs after this commit but before the trigger loop finishes. The durable database now reports version 2 but lacks `schema_meta_no_update` and potentially the new `coverage_no_replace` and `gates_no_replace` triggers. Closing the connection cannot roll back that committed upgrade. The atomicity test injects its failure only inside the earlier transaction.

5. **med | CONFIRMED | [gates.py:223](/Users/davidskoranski/legal-harness/src/casefile/gates.py:223)**  
   **The empty-answer guard accepts empty placeholder records and can mark their cited pages read.**  
   Scenario: `{"facts":[],"flags":[{"kind":"gap","cites":["MED0001"],"about":""}]}` passes schema, reference and rule checks. The nonempty `flags` list bypasses coverage’s empty check, and `MED0001` becomes `read` despite containing no extracted statement. With `cites:[]`, the same placeholder still returns `ok=True`, although every page remains uncited.

6. **med | CONFIRMED | [gates.py:127](/Users/davidskoranski/legal-harness/src/casefile/gates.py:127)**  
   **The truncation guard rejects a permitted trailing-comma repair before the repair gate can run.**  
   Scenario: an otherwise correct answer ends `"end_id":"<nonce>",}`. `_end_id()` permits only whitespace and closers after the nonce, so it reports `answer cut`. If repeated, every page fails. `jsonrepair.repair()` explicitly supports removing this comma, but the pipeline never reaches it.

7. **med | CONFIRMED | [jsonrepair.py:76](/Users/davidskoranski/legal-harness/src/casefile/jsonrepair.py:76)**  
   **Duplicate JSON keys silently discard extracted content instead of failing the repair gate.**  
   Scenario: an answer contains `"facts":[F1],"facts":[F2]`, where both facts are valid and concern the same page. Both JSON loads retain only F2; subsequent gates pass and mark the page read. The returned validated answer loses F1 without a failure or repair verdict, although the raw log retains the original response.

8. **med | CONFIRMED | [jsonrepair.py:77](/Users/davidskoranski/legal-harness/src/casefile/jsonrepair.py:77)**  
   **JSON decoder failures other than `JSONDecodeError` escape the pipeline before the received answer is logged.**  
   Scenario: under Python 3.12’s default integer-conversion limit, an answer with valid boundary IDs and a 5,000-digit integer property passes gate 1 but makes `json.loads()` raise plain `ValueError`. This handler misses it, and `ask()` catches only `RepairError`. The call aborts without retry, an answer row or final failed coverage. Excessive nesting similarly exposes an uncaught `RecursionError`.

9. **med | CONFIRMED | [schema.py:80](/Users/davidskoranski/legal-harness/src/casefile/schema.py:80)**  
   **Composite enum comparison uses Python equality, which conflates nested booleans and numbers.**  
   Scenario: the accepted schema `{"type":"array","items":{"type":"integer"},"enum":[[true]]}` incorrectly validates `[1]`: Python considers `[1] == [True]`, the outer array type matches, and the integer item check passes. JSON Schema requires those enum values to be distinct; the advertised subset therefore accepts an instance its constraint excludes.
## Chair reproduction (8a, 2026-10-27), probes against the production code at 8a2973b

| # | Status | Probe and observed result | Chair ruling for fix cycle 1 |
|---|---|---|---|
| 1 | REPRODUCED | pages `MED0001` and `MED0001,MED0002`, answer cites `MED0001`: `ids=['MED0001', 'MED0001'] read_both=True` | coverage keyed by `page_id`; a cite whose normalised form is a stamp of two pages of the chunk is a fault `cite X is ambiguous (pages ...)` |
| 2 | REPRODUCED | `match('5 mg daily.', 'Take 15 mg daily.')` and `match('able to work', 'He is unable to work.')` both `rung='exact'` | at every rung a hit must start and end on a token boundary (no letter or digit just outside the quoted span on the page) |
| 3 | REPRODUCED | `match('Dose 12 mg.', 'Dose 1-\n2 mg.')` -> `rung='ocr'` | the line-break hyphen join applies only between two letters |
| 4 | NOT REPRODUCED | every opener uses `open_db` (`bench.py:69`, `doctor.py:73`); an upgrade cut after the commit (two triggers dropped) reopens with `triggers_before_reopen=19 after_reopen=21` | no fix; recorded |
| 5 | REPRODUCED | `{"facts": [], "flags": [{"kind": "gap", "cites": ["MED0001"], "about": ""}]}` passes references, coverage marks `MED0001` read | gate 6 fails a fact with a blank `text` or `quote`, a flag with a blank `about` or no `cites` (`empty answer: <path> blank`) |
| 6 | REPRODUCED | `..."end_id": "<nonce>",}` -> `end_id_ok=False`, while `repair` handles it as `('trailing-comma',)` | gate 1's end check allows one comma between the `end_id` value and the closers |
| 7 | REPRODUCED | two `facts` keys -> `repairs=() parsed_facts=[{'x': 2}]` | a duplicate key anywhere fails gate 2 (`duplicate key <name>`); gate 3 parses with the same hook |
| 8 | REPRODUCED | a 5000-digit integer -> `ESCAPES ValueError` | every parse error (`ValueError`, `RecursionError`) is a `RepairError`, logged and retried as gate 2 |
| 9 | REPRODUCED | schema `enum [[true]]` accepts `[1]`: `errors_for_[1]=[]` | `enum` compares with JSON types (a boolean never equals a number), deep |
| CH-1 | REPRODUCED (chair seed) | `gates.py:105` checked against the whole chunk stays green, 28 passed | a test quoting a sentence that is on another page of the chunk than the one cited, which must fail |
