# Round 3 report: stage 3, intake and OCR with page IDs

**Verdict: PASS, merged to `main` (2026-10-27).** The blind verifier (fresh Opus, no reports read before
ticking) ticked R3-1 to R3-7 and V. with its own runs; R3-8 stays deferred (R2-CX-2 to stage 4, R1-20 to the
stage that writes cited prose). Two fix cycles of the three allowed were used (Codex 8a, output critic 8b).
Spec §7 stage 3 exit test, "a scanned PDF becomes page text with correct IDs", passes on an invented
six-page scanned binder with real ocrmypdf and Tesseract on this Mac (owner Q39).

Branch `loop/round-03` fast-forwarded into `main`; `loop/round-04` opened from it.

## Measured on the tip (chair and verifier re-runs)
- `scripts/run.sh pytest -q` -> `358 passed in 72.67s` (verifier; 63 to 87 s across runs, budget 90 s, T-11;
  round 2: 270).
- `scripts/run.sh python -m casefile.gate` -> `0`; `scripts/run.sh python scripts/unused_imports.py src tests
  scripts` -> `unused_imports=0`.
- Stage 3 exit test (`pytest -q -s tests/test_stage3_exit.py`): `stage3 exit=1 pages=6 ids_ok=6 of 6
  stamps_ok=6 of 6 text_ok=6 of 6 must_ok=5 of 5 empty=1 failed=0 min_ratio=1.000` (exit 1 because the blank
  separator page is an open item, owner Q40 item 32).
- Stage 1 exit test: `exit=0 verdicts=8 fails=set() test_jobs=1` (was `fails={'ocr'}`; the doctor's OCR check
  is real now: `doctor ocr PASS smoke=ok stamps=SMOKE7342 ocrmypdf=17.13.0 tesseract=5.5.3`).
- Stage 2 exit test: `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`, perfect line `bench 9001.001
  model=qwen3.8:27b found=29 of 29 ... flags=9 of 9 ...`.
- `casefile bench --config config.example.toml --matters tests/fixtures/matters --candidate
  tests/fixtures/bench/flawed.json` -> exit 1: `bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2
  extra=2 flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14`.
- Same with `tests/fixtures/matters/9001.001/ideal.json` -> exit 0: `bench 9001.001 model=candidate found=29 of
  29 missed=0 invented=0 extra=2 flags=9 of 9 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14`.
- Chair driven intake of `tests/fixtures/scanned/scanned.pdf`: `intake 9002.001 scan pages=6 ok=5 empty=1
  failed=0 stamps=6 had_text=2 ocr_added=4`, `  empty: scan/004 no text after OCR`, exit 1; re-intake exit 2.
- An unreachable model server: `casefile bench` exit 2 (verifier).

## What was built (all code by Sonnet 5.5; Q30 tiers)
- `casefile intake --matter N --binder B FILE` (D27): ocrmypdf `--redo-ocr` once per PDF, page text by pypdf,
  per-page outcome from the sidecar (`[skipped page]` is `failed`), JSON page store per page plus `binder.json`,
  published by renaming `.tmp` folders; matter folder must exist and resolve under the matters root, and its
  `records` and `pages` folders must not be links; re-intake refused; OCR in its own process group, killed on
  timeout, signal or return; client bytes never in the shared TMPDIR.
- `stamps.py`: every stamp on a page recorded raw and normalised, none chosen (Q35, Q40); a stamp must stand
  as a whole token (CX-7, H1; owner question 38).
- Doctor OCR check (D29) on a generated image-only smoke page through intake's own path.
- Bench: exit 2 when no reply arrives (Q26), `model=` on the line (Q27), `ModelError.received` (D30);
  loader ignores dotfiles, refuses repeated binders and duplicate matter numbers; cites match across
  stamp spellings.
- Key completeness (Q36, Q41): G7 gap MED0003, G8 gap MED0008, G9 conflict MED0006,DEF0002 (degeneration);
  abouts of G3, G5, G6 widened. 29 facts, 9 flags.
- Invented scanned binder (matter 9002.001): generator, byte-stable PDF, manifest with exact `must_contain`
  spans; `--check` compares bytes then content.
- Hygiene: trailing whitespace, unused imports (`scripts/unused_imports.py`), numbered comments; verifier
  round 2 gaps N2 to N5 tested.

## Output critic
`OUTPUT CRITIC 7/10 · high 1 · med 1 · low 6` (`round03-critic.md`). Page records matched every rendered page.
H1 (a claim number's prefix `QRL-2025` recorded as a stamp) and M1 (G9 wording) were reproduced by the chair
and fixed in cycle 2 with L1 to L4 (refusal and empty-page messages). L5 is owner question 40; L6 rejected
(the sidecar is an outcome record by design, D27).

## Critic round
- 8a Codex: 8 findings (3 high, 5 med), all reproduced (2 by run, 6 by trace), all fixed in cycle 1
  (4d615be): symlinked `records` or `pages` wrote into another matter (reproduced: 7 files), cleanup removed
  another run's `.tmp`, publish rollback on interrupt, redirect body read classed as no reply, OCR group not
  killed after a normal return, signals after OCR skipped cleanup, `MED0001A` recorded as `MED0001`, a vacuous
  doctor exit assertion.
- 8b output critic: above; cycle 2 (ab507e1).
- 8c blind verifier: PASS. Six fresh seeds: three red (pdfsmoke resolution, bool `timeout_s`, `open_ids`
  for empty only), three green test gaps where the code is right (S1 record `matter` not asserted, S2 sidecar
  `7 of 6` untested, S5 `--check` text-layer change untested), carried to round 4 like round 2's.

## Design calls pending owner veto
D27 to D30 (spec §9); G9 keyed per Q41; stamp whole-token rule (CX-7, H1; question 38); lowercase binder names
(question 41); first raw spelling kept (question 40); stamp position not recorded (question 39).

## Discoveries
- ocrmypdf 17 exits 0 when Tesseract times out on a page and writes `[skipped page]` (measured); intake reads
  the sidecar for per-page outcomes only.
- In redo mode the sidecar never holds visible digital text; page text comes from pypdf.
- A difflib ratio scores 0.98 with a changed digit and a dropped "no"; exact `must_contain` spans carry the
  medical facts.
- Tesseract inside the Claude sandbox cannot read `/tmp/claude-501/...`, only the resolved `/private/tmp/...`.
- The owner wants anonymized excerpts around each conflict for Claude review (Q41): spec §10, a later stage.

## Process notes
- Remote Control was on. Owner online for the check-in and brief questions (Q34 to Q41).
- Homebrew was not installed; the owner installed it and ocrmypdf (Q39).
- The chair made one code edit: one unused import in `tests/test_fix_cycle2.py` at the merge (2f864a5), left
  between the two lanes' file sets.
- The sandbox hides processes started with the sandbox off; the first Codex waiter fired early (fixed by
  waiting outside the sandbox).

## Cost (agent log)
Fable 664 k (brief 284 k, revision 380 k); Sonnet 693 k plus the Librarian close (W0 60 k, lane A 205 k,
lane B 227 k, fix 1 103 k, fix 2 98 k); Opus 258 k (critic 117 k, verifier 141 k), chair not counted; Codex
two runs.
