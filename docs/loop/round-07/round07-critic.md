OUTPUT CRITIC 6/10 · high 2 · med 4 · low 6

# Round 7 output critic (stage 7 brief package and anonymizer)

Critic: Opus, fresh session, no build context this round. Branch `loop/round-07` at a06a256. Nothing in the repo was
edited except this file. Test matter only (`tests/fixtures/matters/9001.001`); the stand-in from `tests/fakemodel/` on
its own port; no run touched 127.0.0.1:11434.

## How the outputs were made

Driver scripts live outside the repo, in `$TMPDIR/critic7/` (`$TMPDIR` is `/tmp/claude-501` on this Mac).

1. `phase1.py` reproduces the setup of `tests/test_stage7_exit.py`: `write_config` with the stand-in's port and
   `playbook/`, copies the matter to `$TMPDIR/critic7/work/matters/9001.001`, records `ideal.json` for the memo card,
   `entities.json` for the first `07-ANON` pass and `entities-empty.json` for the second pass (all 14 pages, and the used
   pages for the default package), then runs through `scripts/run.sh`:
   `casefile memo`, `casefile brief-out "Whether the L4-L5 disc protrusion is causally related to the work injury" --pages all`
   (packet `992f3add5ef7`), the same without `--pages all` (packet `ac3d2a225148`), `casefile status`.
2. `mkdraft.py` writes two Word drafts from the package as a drafter would (15 body paragraphs): `draft-critic.docx` and
   `draft-realname.docx` (the same, with `Dr. Okonkwo-Lind` for `Dr. [DR-5]` in paragraph 7). Planted defects: a wrong
   quote (paragraph 5, MED0006, "6 mm ... herniation compressing"), an invented number (paragraph 6, "30 degrees"; MED0007
   says 45), a real name (realname draft), an IME and hired sentence (paragraph 14), an em dash (paragraph 15), curly
   quotes (paragraphs 9 and 10).
3. `CASEFILE_CONFIG=$TMPDIR/critic7/work/settings/config.toml scripts/run.sh casefile brief-in --matter 9001.001 <draft>`
   for each draft, then `casefile status`. Probes: `draft-nums.docx` and `draft-uncited.docx` (below). `phase3.py`
   reruns brief-out with names and a date typed into the issue.

Results: brief-out exit 0 both times, `check=pass leaks=0 entities=17`; realname draft exit 2 (blocked, nothing
written); critic draft exit 1, `checks=10 of 11 failed=2 uncited=4 rule_hits=2`, `brief-in-draft-critic.partial.docx`;
status `outputs=memo:current,brief-out:current;partial=brief-in-draft-critic.partial.docx`.

## Findings, most severe first

### H1 (high) An invented number inside a quoted paragraph is not checked
- Output: `outputs/brief-in-draft-critic.partial.docx`, Draft paragraph 16 (draft paragraph 6): "Dr. Priya Okonkwo-Lind
  found a positive straight leg raise on the left at 30 degrees and recorded "Impression: ..." [cite MED0007]", with no
  FACT CHECK FAILED mark; MED0007 says 45 degrees.
- What is wrong: the digit check runs only when a cited paragraph has no quote (`src/casefile/brief.py` line 191,
  `if unit.cites and not unit.quotes:`), so any number in the prose of a paragraph that also quotes the page is restored
  into the attorney's brief unverified.
- Rule: D64 ("digit runs outside placeholders on the page" for every cited paragraph); spec §2 re-import "fact-checked
  against the case file".
- Control: the same sentence without the quote (`draft-nums.docx` paragraph 1) is marked `number not on medical/007`.
- Repro: run `phase1.py`; write a docx with the single paragraph
  `Dr. [DR-5] found a positive straight leg raise on the left at 30 degrees and recorded "Impression: L4-L5 disc protrusion with left L5 radiculopathy." [cite MED0007]`;
  `scripts/run.sh casefile brief-in --matter 9001.001 <file>`: exit 0, `failed=0`.

### H2 (high) An uncited misquote and an invented number publish as a final draft with "Open items: none"
- Output: `outputs/brief-in-draft-uncited.docx` (not `.partial`), exit 0, `checks=0 of 0 failed=0 uncited=2`; Draft holds
  `The emergency record notes "Pain 9/10 in the low back, radiating to the left leg."` (MED0001 says 7/10, no radiation)
  and `Dr. Theodore Marchetti found strength of 3/5.` (DEF0002 says 5/5); Fact check says `Open items: none`.
- What is wrong: a quote is checked only when its paragraph carries an inline `[cite X]` (`brief.py` line 185,
  `if not good and unit.cites`), and the package never tells the drafter that rule, while the firm skill
  (`motion-brief-memo-drafting` §2, "Every factual sentence carries a footnote to the record") tells the drafter to cite in
  footnotes, which brief-in does not read; a draft written to firm practice is therefore uncited throughout and passes.
- Rule: spec §2 ("the draft is ... fact-checked"); D64; firm skill §2.
- Repro: docx with the two paragraphs above; `scripts/run.sh casefile brief-in --matter 9001.001 draft-uncited.docx`.

### M1 (med) The default package ships 13 full pages in package.json that package.md does not show
- Output: `outbox/ac3d2a225148/package.json` `pages` holds 13 anonymized pages (all but DEF0001), including the wage
  statement EMP0003, MED0002, MED0004, MED0005, EMP0002; `package.md` has no Pages section and its conflicts show 8
  pages; `check.txt` says `pages=13`.
- What is wrong: without `--pages all` the package that leaves is larger than the one the attorney reads, and larger than
  the owner's definition (facts, conflict pages and gaps; every page only with the flag).
- Rule: ledger Q62 item 93; D64 ("with `--pages all` every anonymized page").
- Repro: `phase1.py`; `python3 -c "import json;print(len(json.load(open('outbox/ac3d2a225148/package.json'))['pages']))"`
  gives 13; `grep -c '=== PAGE' outbox/ac3d2a225148/package.md` gives 0.

### M2 (med) The package carries none of the firm's drafting rules
- Output: `outbox/992f3add5ef7/package.md` lines 1 to 8, "Drafter rules (casefile-anon/1)": seven placeholder rules only.
- What is wrong: the drafter is never told the rules brief-in later enforces or the firm requires (no DME or IME, write
  "the report"; never who hired or paid the doctor; cite by Bates as `[cite MED0001]` inline in the paragraph; straight
  quotes; no em dashes), so a compliant drafter is set up to fail: paragraph 14 of the critic draft came back as
  `The [withheld: no-dme-ime] report ... the [withheld: no-hired-paid-retained] by the carrier.`
- Rule: `playbook/rules.toml` `no-dme-ime`, `no-hired-paid-retained`, `bates-cites`; firm skill §4 (em dashes); D64
  brief-in parsing rule (cites as `[cite X]`, straight double quotes).
- Repro: `awk '/^## Facts/{exit} {print}' outbox/992f3add5ef7/package.md`.

### M3 (med) A cited number that differs from the page passes when its digits occur anywhere on the page
- Output: `outputs/brief-in-draft-nums.partial.docx` paragraph 2, `Dr. Theodore Marchetti graded strength 4/5 bilaterally
  [cite DEF0002].`, no mark; DEF0002 says "5/5 bilaterally".
- What is wrong: the check compares a set of digit runs against all digit runs on the page (`brief.py` line 194), so
  "4" (from "L4-L5") and "5" satisfy "4/5"; a wrong strength grade, pain score or weight built from common digits passes.
- Rule: D64 digit check; spec §2 fact check.
- Repro: docx with that paragraph; `scripts/run.sh casefile brief-in --matter 9001.001 draft-nums.docx`.

### M4 (med) The package is silent that a defense page was never read
- Output: brief-out stdout and `outbox/992f3add5ef7/package.md` say nothing of the open item; `casefile status` prints
  `open: DEF0001 (defense-report/001): uncited`. DEF0001 holds "The examinee reports lifting a tote of about 60 pounds"
  and "He acknowledges a [YEAR Y-6] episode of low back pain that resolved", both on the tote and prior-injury conflicts.
- What is wrong: brief-out exits 0 and the drafter gets no notice that a page bearing on two listed conflicts produced no
  facts (the default package omits the page entirely), while memo exits 1 for the same open item.
- Rule: D38 (an uncited page is an open item, never counted as read); D41 open items listed.
- Repro: `phase1.py`; compare the memo and status lines with `grep -c DEF0001 outbox/ac3d2a225148/package.md` (0).

### L1 (low) Restored prose dates differ in form from restored quote dates
- Output: `brief-in-draft-critic.partial.docx` paragraph 11 "On 3/11/2025" and paragraph 13 "on 3/14/2025", against
  paragraph 17 "of 03/11/2025" and paragraph 20 "06/20/2025" in quotes.
- What is wrong: one document shows two date forms for the same dates; the records use `MM/DD/YYYY`.
- Rule: firm skill §5 (match the record's conventions); D63 restore canonical for prose.
- Repro: read paragraphs 11 to 20 with python-docx.

### L2 (low) The brief-in header prints a bare "Matter "
- Output: `brief-in-draft-critic.partial.docx` paragraph 8, text `Matter ` with no number.
- What is wrong: `brief.render` calls `outputs.header(info, '', 'brief')` with an empty matter (`brief.py` line 240).
- Rule: D48 header block (an entry is printed or marked NEEDED).
- Repro: read paragraph 8 of any brief-in output.

### L3 (low) The Fact check line does not add up
- Output: `brief-in-draft-critic.partial.docx` paragraph 28 `Checks: 10 of 11; failures: 2; ...`; stdout the same.
- What is wrong: 10 of 11 passing implies one failure; the rule hit is counted as a failure but not as a check.
- Rule: D64 summary line; usable as is.
- Repro: the critic draft run above.

### L4 (low) Failure marks are plain text and name page ids, not Bates
- Output: paragraphs 15 and 25, `[FACT CHECK FAILED: paragraph 5: quote not on medical/006; ...]`, no bold, colour or
  highlight (python-docx runs report `bold=None`, no colour).
- What is wrong: in a long brief the mark reads like body text, and the attorney cites MED0006, not `medical/006`.
- Rule: `bates-cites` (cite by Bates); task item 3 (marked where the attorney will see them).
- Repro: read the runs of paragraph 15.

### L5 (low) An em dash passes into the restored brief
- Output: `brief-in-draft-critic.partial.docx` paragraph 26, "... compensable [U+2014 em dash] the treating ..."
  (character named here, not reproduced), no mark.
- What is wrong: the firm skill calls this a hard rule for every brief; `rules.toml` has no rule for it, so brief-in
  cannot catch it.
- Rule: `motion-brief-memo-drafting` §4 ("Never use em dashes").
- Repro: paragraph 15 of `mkdraft.py`.

### L6 (low) Small privacy and review-list leftovers
- Output: `outbox/992f3add5ef7/package.md`: "Chief Complaint: Low back pain, onset Tuesday [DATE D+0]." (MED0002 page,
  line 496) gives the weekday of the anchor; "44 year old male" four times; check.txt review words include the
  package's own headings `Conflicts, Facts, Gaps, Pages, Dr`; the package never says that D+0 is the date of accident.
- What is wrong: the weekday plus offsets narrows the real dates; the review list pads 30 slots with noise; spec §2 says
  "dates as days from the injury" but the drafter is not told the anchor.
- Rule: D63 identifier check; spec §2.
- Repro: `grep -n Tuesday outbox/992f3add5ef7/package.md`; `cat outbox/992f3add5ef7/check.txt`.

## Grading by area

1. Privacy: clean. A grep of both packages and check.txt for every `[anon]` value, every given name and surname,
   `QRL`, `1981`, `1234567`, every year, month name and slash date found none. The six providers, including Northgate
   Medical Evaluations, are kept and listed on the kept-names line; examiners and doctors are `[DR-n]`; the shift lead,
   supervisor and payroll clerk are `[PERSON-1..3]`; claim number `[ID-1]`; DOB `[DOB]`; 2019 `[YEAR Y-6]`; the 13 wage
   weeks `[DATE D-88]` to `[DATE D-4]`. A name or date typed into the issue (`Morgan Ashby-Vale's`, `Morgan's`,
   `3/11/25`, `Dr. Marchetti's`) is replaced in package.md and package.json. No local path in package.json. Nothing
   over-replaced. Only L6 and M1 touch this area.
2. Answer key: 36 of 36 key facts in the package with the right cite and the right relative date (checked by converting
   offsets back from 03/11/2025), plus two employer facts not in the key; 5 of 5 conflicts with both full pages; 4 of 4
   gaps; the MED0002 and DEF0002 "Straight leg raise negative bilaterally" pair is two facts on two dates (D65 works).
   Restored names and dates in the brief-in document are right (DR-2 Castellanos-Reyes, DR-5 Okonkwo-Lind, DR-6
   Marchetti, D+38 04/18/2025, D+101 06/20/2025).
3. Fact check: wrong quote caught and marked; real name blocks the whole draft with exit 2 and nothing written; invented
   number missed (H1); uncited fabrications pass (H2); digit-bag false pass (M3).
4. Firm rules: brief-in withholds IME and hired prose and marks it; the package does not hand the drafter the rules (M2);
   em dash unchecked (L5); footnote citation practice defeats the check (H2).
5. Usable as is: package.md reads well and the drafter could work from it today; the brief-in document needs H1 and H2
   fixed before an attorney can rely on "failures: 0".

## Good enough to keep

- The anonymizer output: placeholders are consistent across facts, conflict pages and pages; providers kept per Q61 and
  Q62; dates as offsets with the year form for bare years; issue text anonymized.
- Package layout: rules, issue, kept-names line, chronological facts with date, provider and category, conflicts with
  the model's reading labelled and both full pages, gaps; folder name equal to the sha256 prefix, modes 700 and 600.
- The real-name block (exit 2, step and kind only, no name echoed, nothing written).
- The wrong-quote mark and the `.partial.docx` plus status `partial=` line.
- Curly quotes in the draft are read and checked.
