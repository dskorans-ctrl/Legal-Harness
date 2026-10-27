OUTPUT CRITIC 7/10 · high 1 · med 1 · low 6

# Round 3 output critic (stage 3 intake and OCR)

Critic: fresh context, built nothing this round. Branch `loop/round-03` at 70357ea. Every record used is
invented: the scanned binder `tests/fixtures/scanned/scanned.pdf` (matter 9002.001), the bench matter
`tests/fixtures/matters/9001.001`, and one probe page I generated under `$D/gen` (not committed, removed).

## Runs

- Intake: `scripts/run.sh casefile intake --config $D/config.toml --matter 9002.001 --binder scan
  tests/fixtures/scanned/scanned.pdf` printed `intake 9002.001 scan pages=6 ok=5 empty=1 failed=0 stamps=6
  had_text=2 ocr_added=4` and `  empty: scan/004`, exit 1 (D27: exit 1 when open pages are listed).
- Exit tests: `scripts/run.sh pytest -q -s tests/test_stage1_exit.py tests/test_stage3_exit.py` printed
  `exit=0 verdicts=8 fails=set() test_jobs=1`, `stage-control exit=0 verdicts=8 fails=set() expected=set()
  test_jobs=1`, `stage3 exit=1 pages=6 ids_ok=6 of 6 stamps_ok=6 of 6 text_ok=6 of 6 must_ok=5 of 5 empty=1
  failed=0 min_ratio=1.000`, `5 passed`. No doctor `ocr` line is printed by these tests, so I ran the doctor
  with `[paths].state` moved under `$D` (nothing written to the checkout): `doctor ocr PASS smoke=ok
  stamps=SMOKE7342 ocrmypdf=17.13.0 tesseract=5.5.3 ms=3453`; the doctor as a whole exits 1 here only because
  the model tag is not on the local server (`context FAIL ... not found`), which is not this round's work.
- Bench, flawed: `bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2 flags=8 of 9
  flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14` with detail lines `missed: F04 F15 F24`, two
  `invented:` lines (MED0003, MED0099), `flags_missed: G3`, `flags_extra: conflict MED0001,MED0004`,
  `rules: no-dme-ime DEF0003`; `bench matters=1 imperfect=1`, exit 1.
- Bench, ideal: `... found=29 of 29 missed=0 invented=0 extra=2 flags=9 of 9 flags_missed=0 flags_extra=0
  rules=0 pages_failed=0 of 14`, `bench matters=1 imperfect=0`, exit 0.

## Findings, most severe first

### H1 (high) A hyphenated number is cut and recorded as a stamp that is not on the page

- Output: page record `pages/<binder>/<nnn>.json`, field `stamps`.
- What is wrong: a page reading `Claim Number: QRL-2025-0418` gets the stamp `{"raw": "QRL-2025", "stamp":
  "QRL2025"}`, a fragment of a longer token that appears nowhere on the page as a stamp.
- Breaks: owner Q40 item 35 ("every token matching the stamp pattern is recorded"; `QRL-2025` is not a
  token, it is the front of `QRL-2025-0418`); Q35 and D27 (no invented stamp); the code's own promise in
  `src/casefile/stamps.py` ("a truncated token is never recorded (CX-7)"): the lookahead `(?![A-Za-z0-9])`
  does not refuse a following hyphen. The same claim line sits on three pages of the bench matter
  (`records/employer/001.txt` EMP0001, `records/employer/003.txt` EMP0003, `records/defense-report/001.txt`
  DEF0001), so a scan of that matter would give three pages one shared false stamp `QRL2025`, and under D28
  a cite `QRL2025` would match all three. The scanned fixture has no such line, so the stage 3 exit test
  cannot see it.
- Reproduce: render an image page holding the line `Claim Number: QRL-2025-0418` (any invented text; I
  used Pillow, Arial 40 pt, 300 dpi, saved as PDF), create `$D/matters/9002.002/`, run `scripts/run.sh
  casefile intake --config $D/config.toml --matter 9002.002 --binder probe probe.pdf`; exit 0, `stamps=3`,
  and `pages/probe/001.json` lists `QRL-2025`.

### M1 (med) Key flag G9's `about` does not say what the conflict is

- Output: `tests/fixtures/matters/9001.001/key.json`, flag G9 (cites MED0006, DEF0002), field `about`; the
  same text is in `ideal.json`.
- What is wrong: the about sets "degenerative" against "a 4 mm posterior central disc protrusion at L4-L5",
  which are not opposites, and leaves out the actual disagreement on the pages: DEF0002, under "Imaging
  Review" of the 04/18/2025 MRI, says "The L4-L5 disc changes are described as degenerative", while MED0006
  reports only a protrusion at L4-L5 and places "Mild degenerative disc disease" at L5-S1 (it also notes
  "mild degenerative change ... at the lower vertebral levels"). "The report" is also ambiguous here because
  both cited pages are reports (MED0006 is the imaging report).
- Breaks: the brief's own test for key abouts ("does each about describe what the pages say"); Q41 asks
  that defense and treating disagreements be flagged so the attorney can act on them, and an about that
  does not name the disagreement does not let her do that. G9 itself is right to exist under Q41, and G7
  and G8 are true to MED0003 ("Follow up in four weeks or sooner if symptoms worsen") and MED0008 (the
  planned injection and the 06/20/2025 re-evaluation, neither in the records).
- Reproduce: open `key.json` flag G9 beside `records/medical/006.txt` (FINDINGS and IMPRESSION) and
  `records/defense-report/002.txt` (Imaging Review). Suggested wording, no banned labels: "Dr. Marchetti's
  report, reviewing the 04/18/2025 MRI, says the L4-L5 disc changes are described as degenerative; the MRI
  reports a 4 mm central disc protrusion at L4-L5 and places degenerative disc disease at L5-S1."

### L1 (low) Re-intake refusal names one folder and does not say what to do

- Output: stderr `intake: cannot run: <matter>/records/scan already exists; re-intake is refused`, exit 2.
- What is wrong: the user is not told to remove the old binder by hand, and the message names only the first
  folder found, so after removing `records/scan` the next run refuses again on `pages/scan`.
- Breaks: Q40 item 34 (refused "until the old binder is removed by hand"; the message should say which
  folders); usable as is.
- Reproduce: intake the fixture twice; then delete `records/<binder>` only and run again.

### L2 (low) Binder names refuse capital letters, and the message is a regular expression

- Output: stderr `intake: cannot run: binder name must match [a-z][a-z0-9-]{0,39}, got 'Medical'` (also
  for `my scan`, `my_scan`, `2026-binder`), exit 2.
- What is wrong: `Medical` is refused although the owner allowed letters, digits and hyphens, and the rule
  is shown as a pattern an attorney cannot read.
- Breaks: Q40 item 33 ("letters, digits, hyphens"); usable as is. Plain wording would be: "binder name:
  lower case letters, digits and hyphens, starting with a letter, up to 40 characters".
- Reproduce: `--binder Medical` or `--binder "my scan"`.

### L3 (low) A non-PDF or a missing file prints library noise or the wrong cause

- Output: for `tests/fixtures/scanned/scanned.json`, stderr shows `invalid pdf header: b'{\n  "'`, `EOF marker
  not found` twice, then `not a readable PDF: ...: Stream has ended unexpectedly`; for a missing path,
  `not a readable PDF: ...: [Errno 2] No such file or directory`.
- What is wrong: pypdf warnings leak above the casefile line, and a file that does not exist is reported
  as an unreadable PDF.
- Breaks: usable as is (one clear line per refusal, as every other refusal has).
- Reproduce: run intake with those two arguments.

### L4 (low) The empty page record gives no reason

- Output: `pages/scan/004.json`, `"status": "empty"`, `"reason": ""`.
- What is wrong: the open item a reader opens says nothing about why it is open or what to do, while a
  failed page carries `"ocr timeout"`.
- Breaks: D27 and Q40 item 32 (listed as an open item) are met by `binder.json` `open_ids` and the summary
  line; this is usability only. Something like "no text found after OCR; check the page by eye".
- Reproduce: intake the fixture and open `004.json`.

### L5 (low) A second spelling of the same stamp on one page is dropped

- Output: `stamps` on the probe page above: the page shows `MED 0001` and, at bottom centre, `MED-0001`;
  only `{"raw": "MED 0001", "stamp": "MED0001"}` is recorded.
- What is wrong: the raw form printed at the bottom centre (where the owner says the firm's stamp sits, Q35)
  is lost because only the first raw per normalised form is kept.
- Breaks: Q40 item 31 ("intake keeps the raw text"); it is the same stamp, so this is low.
- Reproduce: the probe page in H1.

### L6 (low) `records/scan/sidecar.txt` is not the binder's text

- Output: `records/scan/sidecar.txt`.
- What is wrong: it holds nothing for page 5 (text layer kept) and omits the stamp `KMR2346` on page 6, so
  anyone who opens it as "the OCR text" sees an incomplete binder; the page records are complete.
- Breaks: usable as is (no rule; the file is a working file kept beside `ocr.pdf`).
- Reproduce: intake the fixture and read the sidecar.

## Owner questions (practice, not settled by the rulings)

1. The stamp pattern also matches whole tokens that are not Bates stamps, for example an account line
   `ABC 123456` (recorded as stamp `ABC123456` on the probe page) or a billing code such as `CPT 99213`.
   Q40 item 35 says record every match. Should the page record also say where on the page each stamp sits
   (for example bottom centre), so hearing prep can offer the firm's stamp first?
2. When one page shows the same stamp in two spellings (`MED 0001` and `MED-0001`), keep both raw forms?
3. Binder names: may they use capital letters (`Medical`), or is lower case the rule?

## Good enough to keep

- Every page record of the scanned binder matches what the page shows: all lines present, dates
  (02/18/2026, 02/10/2026, 03/04/2026, 02/25/2026, 03/12/2026, 03/16/2026, DOB 09/03/1979), numbers
  ("6 out of 10", "10 pounds", "two visits per week for four weeks"), negations and restrictions ("No full
  thickness tear is seen", "no lifting over 10 pounds", "released to full duty with the brace", "on light
  duty") are exact.
- Stamps match the manifest page by page: KMR2342 to KMR2346, both KMR2344 and TWP7731 on page 3, none on
  page 4, raw and normalised, none chosen, none invented.
- Page 4 is `empty`, listed in `open_ids` and in the summary line, not counted in `ok`, exit 1. IDs `scan/001`
  to `scan/006` with `matter` and `binder` fields are right. Page 5 kept its text layer, page 6 is `mixed`
  with both the text-layer stamp and the OCR body.
- `records/scan/ocr.pdf` renders all six pages with a correct text layer; `source.pdf` is byte-identical to
  the fixture; `binder.json` counts (6, 5, 1, 0), `open_ids`, tool versions (tesseract 5.5.3, ocrmypdf
  17.13.0) and flags are right.
- Refusals for an unknown matter and a malformed matter number are one clear line, exit 2, and nothing is
  written on any refusal.
- Bench lines and detail lines are clear; the key and ideal abouts hold no DME or IME label (the only hit is
  the planted one in `flawed.json`, caught as `rules: no-dme-ime DEF0003`); no em or en dash in any output
  or key.
