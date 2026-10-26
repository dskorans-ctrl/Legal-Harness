Implemented R1-9, R1-10 and R1-11. Socket acceptance remains for the orchestrator.

Files written: `src/casefile/{cli,doctor,model,gate,privacy,prose}.py`; `tests/test_{cli,doctor,model,gate,privacy,prose,stage1_exit}.py`.

Ran only `scripts/run.sh pytest -q -m "not socket"`. Final line:
`92 passed, 5 deselected in 6.78s`

Every control had a green baseline, went red, restored with `cmp` exit 0, then returned green. CHECK quotes below occurred before and after restoration. [Full verbatim transcripts](/private/tmp/casefile-lane-a-evidence.txt).

| Claim | Verified by: CHECK output | Control: SEED output |
|---|---|---|
| Exact context | `test_short_context_fails`: `doctor context FAIL context_length=8192 want 65536` | `>=8192`: `doctor context PASS context_length=8192` |
| Exact READY answer | `test_wrong_word_fails`: `doctor context FAIL answer=READY. want READY` | Drop equality: `doctor context PASS context_length=65536` |
| Ignored files scanned | `test_offenders`: `offenders=4 expected=4 scanned=8` | Add exclusion: `offenders=2 expected=4 scanned=5` |
| Fixture prefix enforced | `test_offenders`: `offenders=4 expected=4 scanned=8` | Substring: `offenders=3 expected=4 scanned=8` |
| Gate returns verdict | `gate return=1 printed=1`; `gate process=1 printed=1` | Return zero: `gate return=0 printed=1`; `gate process=0 printed=1` |
| Prose detector | `test_dashes`: `dashes=1` | Disable U+2014 detection: `dashes=0` |
| Answer persisted | Stage companion, S below | Remove write: `stage-control exit=1 verdicts=8 fails={'runlog_job', 'ocr'} expected={'ocr'} test_jobs=0` |
| OCR stays FAIL | Stage companion, S below | Force PASS: `stage-control exit=0 verdicts=8 fails=set() expected={'ocr'} test_jobs=1` |
| Eight verdicts required | Stage companion, S below | Suppress folders: `stage-control exit=1 verdicts=7 fails={'ocr'} expected={'ocr'} test_jobs=1` |

S: `stage-control exit=1 verdicts=8 fails={'ocr'} expected={'ocr'} test_jobs=1`.

Brief lines that did not work as written:

- 818: corrected `scanned=7` to `scanned=8`, including the copied `.gitignore`.
- 814, 817, 819: used a disposable git index without commits, following your explicit prohibition.
- 811-812: checkout gate cannot currently print green. Privacy finds four pre-existing idlelib PNGs under `.uv/python/cpython-3.12.13-macos-aarch64-none/`; prose finds one prohibited dash at `docs/loop/round-01/round01-brief-codex.md:3`. Left untouched and unexempted.
- 842-851: socket acceptance was not run here. Its three seeds were calibrated through the subprocess companion.

Catalog checked: #25, #32, #48, #52, #69, #73, #74, #79, #80, #81, #84, #86, #90, #91, #96, #101, #102, #111, #117; dispatcher exit override, fail-open CLI default, self-certifying probes, presence-anywhere. Librarian was blank.