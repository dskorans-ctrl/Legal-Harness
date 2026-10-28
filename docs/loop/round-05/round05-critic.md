# Round 5 output critic (stage 5: case file, merge, medical memo)

OUTPUT CRITIC 7/10 · high 0 · med 2 · low 5

Critic: Opus 5.5, fresh agent with no part in building round 5. Branch `loop/round-05`, tip `320c551`. Code not
edited. Invented matters only (9001.001, scanned 9002.001); the model was the stand-in on its own port (exit test
port 0, bench on 18434 with a scratch config whose host, matters and state point at the stand-in and `$TMPDIR`);
127.0.0.1:11434 was never contacted.

## What was run

- `scripts/run.sh pytest -q -s tests/test_stage5_exit.py --basetemp=$B/exit` (B = `$TMPDIR` resolved with `pwd -P`,
  then `/critic5`): all nine `stage5` lines as expected, `stage5 exit=0 runs=4 of 4 memos=3 of 3`.
- `scripts/run.sh pytest -q -s tests/test_memo_intake.py --basetemp=$B/intake`: `memo_intake 9002.001 chunks=1
  read=5 open=1 facts=5 gaps=1 label_ok=1 exit=1`.
- The exit test leaves only the memo of run 4. To read memos 1, 2 and 3 I ran a scratch copy of the test
  (`$B/copytest/test_copy5.py`, identical but for a `shutil.copy` of `outputs/memo.docx` and a save of the CLI and
  status text after each run; run with `PYTHONPATH=tests scripts/run.sh pytest ...`). Same nine lines.
- Every `memo.docx` opened with python-docx through `scripts/run.sh python` (paragraph text and style).
- `casefile status` after runs 1 and 3; `casefile bench` with `flawed.json`, with `ideal.json`, and in model mode
  against the stand-in.

Context for every grade below: the stand-in replays `ideal.json`, so the memo's facts and flags are the answer key
by construction. The key checks below prove that merge, placement, cites and labels carry the key through to Word
without loss or invention; they say nothing about extraction quality on a real model.

## Grade against the answer key (key.json)

- All 29 key facts appear as `"<quote>" [cite <stamp>]` under the right page heading (scripted check over the run 4
  memo: missing none).
- All 9 key flags appear with the key's cite set and the key's `about` as a labelled reading: 5 conflicts (G1, G2,
  G3, G6, G9) and 4 gaps (G4, G5, G7, G8).
- No invented fact: the three facts beyond the key (`Date of hire: 08/02/2021` at EMP0001, `Lift up to 50 pounds
  repeatedly during the shift.` at EMP0002, `The examinee reports lifting a tote of about 60 pounds.` at DEF0001)
  are each on their page (checked with grep on the fixture).
- Open items are right in each state: memo 1 `DEF0001 (defense-report/001): uncited`, memo 2 the same page
  `failed` with the gate reason, memo 3 and 4 none. `casefile status` agrees (`read=13 ... open=1`, then
  `read=14 ... open=0`, `outputs=memo:current`).
- Bench: `flawed.json` gives `found=26 of 29 missed=3 invented=2 extra=2 flags=8 of 9 flags_missed=1 flags_extra=1
  rules=1`, with detail lines naming F04 F15 F24, the two invented facts with `(quote not on the page)` and
  `(no such page)`, G3, the extra flag and `no-dme-ime DEF0003 "IME"` (D43, Q49 interim). `ideal.json` gives
  `found=29 of 29 ... rules=0`, exit 0. Model mode gives the same plus `uncited: DEF0001` (D39).

## Findings, most severe first

### M1 (med) The rebuilt memo says it is itself out of date
- Output: memo of run 3 (`$B/memo_run3.docx`), section "Outputs out of date", paragraph 1: `memo`.
- What is wrong: the memo just written from case file entry 46 lists "memo" as an output now out of date, while
  `casefile status` run straight after says `outputs=memo:current`; the attorney reading the fresh memo is told not
  to trust it.
- Breaks: spec §2 ("a list of outputs now out of date"); D41 "outputs out of date"; D43 `memo:current`. Cause:
  `facts.stale_outputs()` is read before the new memo's own output event is recorded, so the previous memo's
  staleness is printed into its replacement. The exit test pins this (`"memo" if number == 3`), so it is not
  caught.
- Reproduce: run the exit test with a copy of `outputs/memo.docx` after run 3 (scratch copy above); paragraph 5 of
  that file reads `memo`.

### M2 (med) Page headings with nothing under them and no explanation
- Output: every 9001.001 memo, "Verified facts by record", heading `defense-report page DEF0002 (defense-report/002)`
  (run 4 paragraph 97) followed directly by the next heading; memos 1 and 2 the same for `DEF0001` (paragraph 95)
  while that page is an open item; scanned memo, heading `scan page scan/004` (paragraph 24).
- What is wrong: a read page whose only use is in flags, an open page and a blank page all show as a bare heading,
  so the attorney cannot tell "read, nothing quoted" from "not read" from "blank"; DEF0002 is one side of two
  conflicts (G6, G9) and the memo carries no verified text for it anywhere.
- Breaks: usability (no empty sections); pillar on showing what was read. Whether facts from the two pages should
  sit beneath each conflict is owner question 54, not graded here; the bare heading is graded.
- Reproduce: open the run 4 memo of the exit test; paragraphs 97 and 98 are consecutive Heading 2.

### L1 (low) "What changed" line: wrong number and counts that hide the change
- Output: memo of run 3, "What changed since the last memo": `1 fact added, 0 cites added, 0 readings added, 0 flags
  added`; memos 2 and 4: `0 fact added, ...`.
- What is wrong: "0 fact added" is the wrong number (beside "0 cites", "0 readings"); "0 readings added" is shown
  while a new "Model's reading" paragraph did appear (under DEF0001); and the line never says which fact or page
  changed, so the attorney must compare two memos by hand.
- Breaks: usability (singular and plural); spec §2 "what changed" summary. What the summary should name is an owner
  question; the plural and the readings count are graded.
- Reproduce: `memo.py` `build()`, the `changed` f-string; visible in any memo after the first.

### L2 (low) Empty sections with no "none"
- Output: memos of runs 3 and 4, "Open items" heading followed directly by "Conflicts" (paragraphs 6 and 7);
  scanned memo, "Conflicts" holds only the runs sentence and no line saying none were found.
- What is wrong: "Outputs out of date" says `none` but "Open items" and an empty "Conflicts" say nothing, so an
  empty section reads like a missing one.
- Breaks: usability (empty sections).
- Reproduce: open either file and list Heading 1 paragraphs.

### L3 (low) Scanned memo: the unstamped warning is the rule's instruction and names a blank page
- Output: scanned memo (`$B/intake/test_memo_intake0/matters/9002.001/outputs/memo.docx`), "Verified facts by
  record", paragraph 14: `Cite by Bates number; when the records are not stamped, cite page IDs and expect a warning.
  Unstamped pages: scan/004.`
- What is wrong: the paragraph is the rule's wording addressed to a writer ("expect a warning"), not a warning to the
  reader, and the one page it names is the blank page that OCR found empty, not a record lacking a stamp.
- Breaks: Q53 interim asks for "the rule's warning naming those pages"; usability (plain wording). Whether a blank
  page should count as unstamped is an owner question.
- Reproduce: `tests/test_memo_intake.py` with `--basetemp`, open the memo, paragraph 14.

### L4 (low) Lowercase starts and folder slugs in headings
- Output: every memo, paragraph 1 `built 2026-10-28 from case file entry ...`; every page heading, for example
  `medical page MED0001 (medical/001)`, `defense-report page DEF0003 (defense-report/003)`.
- What is wrong: the build line and every page heading begin in lowercase and show the folder name as typed, which
  reads as a machine label in a document the attorney prints.
- Breaks: usability (plain wording, headings).
- Reproduce: any memo, paragraph 1 and any Heading 2.

### L5 (low, owner question attached) "Defense report" framing in our own memo
- Output: every 9001.001 memo, "Conflicts", reading under `Conflict between [cite MED0006] and [cite DEF0002].`:
  `Model's reading: The defense report says the L4-L5 disc changes are degenerative, ...`; and the headings
  `defense-report page DEF000n`.
- What is wrong: the firm rule's stated why is that labels which frame the examiner as the defense's are avoided, and
  Q16 says always "the report"; the pattern list does not catch "defense report", so it passes.
- Breaks: `playbook/rules.toml` `no-dme-ime` why; ledger Q16 "always 'the report'". Whether "defense report" alone
  is in scope (and whether a binder slug is our words, question 57) is for the owner; graded low because the text
  is in our output today.
- Reproduce: run 4 memo, paragraph 18 and paragraphs 94, 97, 98.

## Owner questions seen in the output (not graded)

- Structure: the memo is ordered by record page only; there is no treatment chronology, provider list, diagnoses,
  restrictions or a split of our doctors' and the report's opinions (spec §2; question 50 interim).
- Conflict order and content: conflicts run in the order found (G1, G2, G3, G6, G9), so the two that set our
  doctor against the report on causation and radiculopathy are third and fourth; no quotes beneath (question 54).
- The "Conflict between ..." and "Gap at ..." lines are in the memo's own voice, but the kind and the pairing are the
  model's; only the reading below is labelled (question 54 interim allows this; Q48 could be read to cover it).
- Memo 2 open item shows `gate.schema: the answer does not match the schema: facts[0].text: missing required key;
  the page stays open until a later run reads it`, a developer message in an attorney document (question 55
  interim: verbatim).
- After run 3 the new DEF0001 fact ("about 60 pounds") stands against EMP0001 ("approximately 40 pounds") with no
  flag, because DEF0001 was read alone; the conflicts section states this limit (question 56).
- No caption, client, injury date or Word template (question 51).

## Good enough to keep

- Q48 is met throughout: every quote stands alone with its cite as the verified text, and every model sentence (31
  and 32 fact readings, all 9 flag readings) is its own paragraph beginning `Model's reading:`.
- Key coverage is complete and nothing invented; cites are Bates stamps in the playbook form `[cite MED0001]`, and a
  page with two stamps is headed with both (`KMR2344 TWP7731`).
- The cross-chunk and cross-run limit is stated in plain words at the top of "Conflicts", with the run count in the
  right number ("1 run", "2 runs").
- Open items show the stamp and page id and the reason as its own run; status and CLI lines agree with the memo.
- No em or en dashes, no raw reprs, no firm rule hits (`rule_hits=0`) in any memo.
- Bench detail lines are clear and point at the exact page and words.
