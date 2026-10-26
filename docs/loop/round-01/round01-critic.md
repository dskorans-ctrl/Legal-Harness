OUTPUT CRITIC 5/10 · high 3 · med 8 · low 3

# Round 1 output critic (stage 1)

Critic: fresh Opus 5.5, no build context this round. Branch `loop/round-01`, tip `28a5f96`. Nothing
under `docs/loop/round-01/` was opened except this file. All probe text is invented.

Setup used for every doctor probe: a stand-in server started with
`scripts/run.sh python -m tests.fakemodel [--mode M] [--port P]`, and a config at
`$TMPDIR/critic1/settings/config.toml` with `[paths].matters = "$TMPDIR/critic1/matters"`,
`state` beside it, `playbook = <checkout>/playbook`, host `http://127.0.0.1:18434`, `num_ctx = 65536`,
`[ocr] tesseract = "tesseract"`, `ocrmypdf = "ocrmypdf"`. Doctor run as
`scripts/run.sh casefile doctor --config <that file>`. Rules probes run as
`PYTHONPATH=. scripts/run.sh python probe.py` with
`R = casefile.rules.load("playbook/rules.toml")` and `R.check(text, unit=...)`.

Baseline (replay mode, this dev Mac): seven PASS, `doctor ocr FAIL versions only: tesseract --version
exit=not-found; ocrmypdf --version exit=not-found`, `doctor failed=1 of 8`, exit 1. Gate: five PASS rows,
prints `0`, exit 0. `pytest -q tests/test_stage1_exit.py -s`: 2 passed.

## Findings, most severe first

### H1. Doctor passes OCR on a version check alone, so the Studio would report all clear with OCR untested
- Severity: high.
- Output: `casefile doctor`, line `doctor ocr`; `src/casefile/doctor.py` `check_ocr` returns PASS when
  both `--version` calls exit 0.
- Wrong: with any `tesseract` and `ocrmypdf` that answer `--version`, the doctor prints `ocr PASS` and
  `failed=0 of 8`, exit 0, though nothing was OCRed.
- Breaks: ledger Q11 and D19 ("OCR FAIL until stage 3", "never skipped"); spec §5 doctor row "OCR works".
- Reproduce: make two stub scripts `printf '#!/bin/sh\nexit 0\n'` at `$TMPDIR/critic1/bin/tesseract`
  and `.../ocrmypdf` (chmod +x), point `[ocr]` at them, run the doctor. Output:
  `doctor ocr PASS versions only: tesseract --version exit=0; ocrmypdf --version exit=0`,
  `doctor failed=0 of 8`, exit 0.

### H2. DME and IME rule misses common written forms of the same labels
- Severity: high.
- Output: `playbook/rules.toml` rule `no-dme-ime`.
- Wrong: dotted, plural and short forms pass with no finding.
- Breaks: ledger Q16 ("never name the exam as a DME or IME in any form"); spec §4 gate 5.
- Reproduce (each returns `[]` with `unit="text"`):
  `The D.M.E. report of Dr. Example is dated 3 May 2025.`;
  `The I.M.E. physician found no ratable impairment.`;
  `Dr. Example has performed many IMEs for this carrier.`;
  `Dr. Example's DMEs are routinely adverse.`;
  `The independent medical exam took place on 3 May 2025.`;
  `The defense medical exam lasted twenty minutes.`;
  `The independent medical evaluation found no injury.`

### H3. The hired, paid or retained rule blocks ordinary memo and deposition prose
- Severity: high.
- Output: `rules.toml` rule `no-hired-paid-retained` (bare `hired|retained`, bare `fees?`, `paid` near
  `exam`, `who referred`).
- Wrong: the rule fires on anything containing these words, not only on who hired, paid or retained
  the doctor, so the employment history, the attorney fee and benefit history in every memo fail gate 5.
- Breaks: spec §4 gate 5 scopes it to "who hired, paid or retained the doctor, fees or exam volume";
  spec §4 failure line (a gate failure is retried once, then the pages are marked failed).
- Reproduce (each returns `['no-hired-paid-retained']`):
  `Mr. Example was hired by Example Widgets on 2 June 2019 as a forklift operator. [cite EXW0001]`;
  `Q. When were you hired?`;
  `The MRI shows retained hardware from the 2018 fusion. [cite MED0012]`;
  `He retained full grip strength on the left. [cite MED0013]`;
  `The claimant retained counsel in April 2025.`;
  `Temporary disability was paid through 3 May 2025, two weeks before the exam. [cite ADJ0004]`;
  `Medical bills are payable under the official medical fee schedule.`;
  `Applicant's attorney fees are set at 15 percent.`;
  `Q. Who referred you to Dr. Example for your therapy?`;
  `Q. How many reports did you prepare in this case?`

### M1. Hired, paid, fees and exam volume rule misses plain paraphrases
- Severity: med.
- Output: `rules.toml` rule `no-hired-paid-retained`.
- Wrong: fee, payment, engagement and volume questions without the listed trigger words pass.
- Breaks: spec §4 gate 5 ("never who hired, paid or retained the doctor, fees or exam volume").
- Reproduce (each returns `[]`): `Q. How much were you compensated for this?`;
  `Q. What did you charge for the report?`; `Q. What is your hourly rate for testimony?`;
  `Q. Did you bill the insurer for your time?`; `Q. Doctor, you were engaged by the carrier, correct?`;
  `Q. At whose request did you examine Mr. Example?`;
  `Q. How many evaluations do you perform each year?`;
  `Q. What percentage of your practice is for insurance companies?`
  (Where the line between "volume" and practice mix sits is an owner question, below; the fee and
  engagement forms are inside the spec text.)

### M2. Treatment and bills rule is silently skipped unless the caller passes unit="question"
- Severity: med.
- Output: `src/casefile/rules.py` `Rules.check`, `if rule.unit == "question" and unit != "question": continue`;
  `check` defaults to `unit="text"`.
- Wrong: the rule's own bad example passes when an outline is checked as text, with no finding and
  no warning that a rule was not run.
- Breaks: spec §4 gate 5 ("treatment and bills never in one question"), every output checked.
- Reproduce: `R.check("Q. What treatment did you receive and what bills followed?")` returns `[]`;
  the same with `unit="question"` returns `['treatment-and-bills-apart']`.

### M3. Treatment and bills rule misses cost words and fires on wage questions
- Severity: med.
- Output: `rules.toml` rule `treatment-and-bills-apart` (`all_of` group 1: treat, therapy, surgery;
  group 2: bill, charge, invoice, `paid`).
- Wrong: cost, expense, lien and balance questions pass, while `paid` makes core wage loss questions fail.
- Breaks: spec §4 gate 5.
- Reproduce with `unit="question"`. Misses (`[]`): `Q. What medical care did you get, and what did it cost?`;
  `Q. Tell me about your physical therapy and the expenses for it.`;
  `Q. Did the surgery result in a lien or an outstanding balance?`.
  False hits (`['treatment-and-bills-apart']`):
  `Q. Did you stop working when you started treatment, and were you paid during that time?`;
  `Q. After the surgery, did you return to work and were you paid your usual wage?`

### M4. Cites outside square brackets are never checked, so page and exhibit cites pass
- Severity: med.
- Output: `rules.toml` rule `bates-cites`, `cite_pattern = '\[(?:cite|p\.|page)\s*([^\]]*)\]'`.
- Wrong: only bracketed `[cite ...]`, `[p. ...]`, `[page ...]` are examined; any other cite form is
  invisible to the rule.
- Breaks: spec §4 gate 5 ("Bates cites"), ledger Q21.
- Reproduce (each returns `[]`): `The report records a normal gait. (Ex. 3 at 12)`;
  `The report records a normal gait. See page 12.`; `The report records a normal gait. [12]`.
  (A sentence with no cite at all also passes; D16 places that in gate 6 at stage 4, so it is noted
  only.)

### M5. Bates ranges, lists and pinpoints are rejected
- Severity: med.
- Output: `rules.toml` rule `bates-cites` (`bates_pattern` must fully match the whole bracket body).
- Wrong: the normal way to cite a multi-page report fails as a non-Bates cite.
- Breaks: spec §4 gate 5 (Bates cites are the required form), spec §4 failure line (retried once, then pages marked failed).
- Reproduce (each returns `['bates-cites']`):
  `The report records a normal gait. [cite MED0001-MED0009]`;
  `The report records a normal gait. [cite MED0001, MED0004]`;
  `The report records a normal gait. [cite MED 0001 at 3]`

### M6. Doctor FAIL reasons are engineer text an attorney cannot act on
- Severity: med.
- Output: `casefile doctor` lines `ollama_loopback`, `context`, `ocr`.
- Wrong: the likeliest Studio failures print Python or API internals instead of what to do
  (start Ollama, reload the model with the Modelfile, install OCR).
- Breaks: D19 ("each PASS or FAIL with a reason"), spec §8 (the attorney runs the doctor at install).
- Reproduce: config host on a port with nothing listening (`http://127.0.0.1:18599`):
  `doctor ollama_loopback FAIL <urlopen error [Errno 61] Connection refused>`.
  `--mode short_context`: `doctor context FAIL context_length=8192 want 65536`.
  `--mode truncated`: `doctor context FAIL done_reason=length`.
  `--mode empty`: `doctor context FAIL status=200 empty message.content: {'model': 'qwen3.8:27b', ...`
  (a raw JSON dump cut mid-word). Baseline: `doctor ocr FAIL ... exit=not-found`.

### M7. Doctor creates a mistyped matters folder and reports it writable
- Severity: med.
- Output: `casefile doctor` line `doctor folders`; `check_folders` calls `mkdir(parents=True)` on matters.
- Wrong: a typo in `[paths].matters` gives `folders PASS writable=3 of 3` and a new empty folder,
  so the attorney is told the case folder is fine when it points nowhere.
- Breaks: spec §5 doctor row ("folders writable"), D13 (config errors fail closed, no silent default).
- Reproduce: set `matters = "$TMPDIR/critic1/typo/Casess"` (folder absent), run the doctor:
  `doctor folders PASS writable=3 of 3`; afterwards `ls -d $TMPDIR/critic1/typo/Casess` exists.

### M8. Config refuses a matters folder beside the config file, with a message that does not say which limit was hit
- Severity: med.
- Output: `casefile doctor` line `doctor config`, from `src/casefile/config.py` line 126.
- Wrong: matters inside the config file's own folder (for example config in the home folder and
  matters at `~/Cases`) is refused, a limit D13 and Q17 do not set, and the message names two limits
  without saying which failed; a relative path gets the same message rather than "must be absolute".
  All eight lines then FAIL.
- Breaks: D13 and Q17 (matters "outside the checkout"); D19 reason quality.
- Reproduce: config at `$TMPDIR/critic1/config.toml` with `matters = "$TMPDIR/critic1/matters"`:
  `doctor config FAIL [paths].matters must be outside the checkout /Users/davidskoranski/legal-harness and config directory /private/tmp/claude-501/critic1`,
  then seven `blocked by config`, `failed=8 of 8`. Same message with `matters = "Cases"`.

### L1. runlog_schema reason claims what this run did not check
- Severity: low.
- Output: `doctor runlog_schema PASS schema=1 triggers=15 (counted, exercised by the test suite)`.
- Wrong: on the Studio the doctor only counts triggers; "exercised by the test suite" describes a dev
  run, not this machine.
- Breaks: D19 (a reason for what was checked).
- Reproduce: any baseline doctor run.

### L2. runlog_job does not say it was blocked by the failed warmup
- Severity: low.
- Output: `doctor runlog_job FAIL test_jobs=+0` after `context FAIL` (any of the bad modes above),
  while `context` itself says `blocked by ollama_loopback` when that fails.
- Wrong: the attorney sees two separate failures where there is one cause.
- Breaks: D19 reason quality.
- Reproduce: `--mode truncated` run above, lines 6 and 7.

### L3. Gate rules row reports false_hits=0 over four sentences
- Severity: low.
- Output: `scripts/run.sh python -m casefile.gate`, line `gate rules_selftest PASS misses=0 false_hits=0`.
- Wrong: the row checks each rule only against its own one good and one bad example, so
  `false_hits=0` reads broader than it is (H3 and M5 show many false hits).
- Breaks: D20 (a measured row should say what it measured).
- Reproduce: `src/casefile/gate.py` `rules_selftest_row`; gate output line 3.

## Owner questions (practice content, not defects)

1. "DME" as durable medical equipment: Q16 blocks the bare word in any case, so
   `The physician ordered DME, a lumbar brace. [cite MED0021]` fails gate 5. Exempt that meaning, or
   require "durable medical equipment" spelled out in outputs?
2. Does the hired, paid or retained rule reach only the author of the report, or any doctor? Is
   `Q. Who referred you to Dr. Example for your therapy?` (a treating doctor) allowed?
3. Is a wage or temporary disability payment a "bill" for the treatment and bills rule? Are liens,
   costs and expenses bills?
4. Exam volume: does it include testimony counts and practice mix (`How many times have you testified
   for employers?`, `What percentage of your practice is for insurance companies?`)?
5. Which cite forms are allowed: Bates ranges, lists of Bates numbers, Bates plus a pinpoint?
6. Should local exam labels other than DME and IME (for example QME, AME, PQME) be treated as "any form"?
7. Should the doctor ever create a missing matters folder, or always FAIL and name the path?

## Good enough to keep

- Doctor prints exactly eight named lines, each PASS or FAIL, then `doctor failed=N of 8`; exit 1 on any
  FAIL, 0 only when all pass. Dependency blocking (`blocked by config`, `blocked by ollama_loopback`)
  keeps one cause from showing as eight unrelated errors.
- OCR is honestly FAIL on this dev Mac (Q11), and the reason starts with `versions only:`.
- The warmup catches short context, truncation, empty and wrong answers (all FAIL against the stand-in
  modes) and logs exactly one test job on success (`runlog_job PASS test_jobs=+1`).
- Gate prints `0` and exits 0 when green; each row carries a count; privacy scans ignored files.
- All three playbook samples are marked SAMPLE in every text field and `sample = true`; the four firm
  rules in `rules.toml` are not marked SAMPLE, as Q12 requires. Every rule's own good example is clean
  and its own bad example fires, against all four rules, not only its own.
- Unstamped records turn a non-Bates cite into a warning rather than an error (`stamped=False`).
