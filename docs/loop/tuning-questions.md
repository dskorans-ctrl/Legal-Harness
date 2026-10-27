# Tuning questions

Values settled by the benchmark, not by argument: the as-built value, its file:line, what the
benchmark says, and what to watch for.

- T-1 (round 1 brief, D-7): rule `no-dme-ime` patterns `\bDME\b`, `\bIME\b`, case-insensitive, in
  `playbook/rules.toml`. `DME` also means durable medical equipment in medical bills; watch for
  findings whose excerpt is followed by "supplier", "equipment" or "provider". Benchmark: stage 4.
- T-2 (round 1 brief, D-7): rule `no-hired-paid-retained` pattern list (`hired|paid|retained|referred
  by`, `fee(s)`, `how many exams`, `exams per year`). Watch for misses in the depo question benchmark
  (stage 6) and for `fee` false hits on "fee schedule" in bills.
- T-3 (round 1 brief, D-7): rule `treatment-and-bills-apart` term groups (treatment, therapy, surgery
  versus bill, charges, invoice, paid). Watch for a question about "paid time off" tripping it.
- T-4 (round 1 brief, D-9): the stand-in's token estimate `prompt_eval_count = chars // 4 + 8`. Replace
  with the real model's counts recorded on the Studio at stage 9 before any truncation threshold is
  tuned on it.
- T-5 (round 1 fix cycle 1, CX-7): rule `no-hired-paid-retained` pairs a payment term with
  doctor/examiner/exam in one clause within 60 characters (`playbook/rules.toml:21`). The 120-character
  cross-sentence window over-blocked benefits prose ("The carrier paid temporary total disability ...;
  Dr. Lane released him"). Measure false hits on the benchmark memos before widening or narrowing.
- T-6 (round 1 re-brief, R5): full suite rose from 12.9 s to 32 s (pathguard rows run /usr/bin/python3
  per row, about 8 s; three 2 s grace waits). Revisit if the suite passes 60 s.
- T-7 (round 2 brief, §1.2): the benchmark's quote match is exact after normalisation (casefold,
  straight quotes, collapsed whitespace), `src/casefile/quotes.py`. The spec §4 ladder (OCR faults,
  line-break hyphens, running headers) replaces `quotes.found_in` at stage 4; measure missed counts on
  the real model's answers before loosening.
- T-8 (round 2 brief, §1.7): `casefile bench` exits 0 only on a perfect score. Whether the real model
  gets a pass mark below perfect is decided by the stage 9 benchmark, never by a flag.
- T-9 (round 2 brief, §1.3): the stage 2 runner makes one model call per matter. Stage 5 replaces it
  with the per-chunk pipeline; score both on the same key before the switch and record the difference.
- T-10 (round 2 brief, §1.4): `matter.STAMP_PATTERN = r"[A-Z]{1,8}[ -]?\d{4,}"` (single stamp, Q21)
  becomes a config key at stage 3; owner question 23 decides where stamps sit on the page.
- T-11 (round 3 brief, supersedes T-6): suite budget 90 s; measured 63 to 87 s at the round 3 close (five real
  OCR runs). Fix if exceeded: fewer real OCR runs (cache the fixture intake per session), never a skip.
- T-12 (round 3 brief, §1.8): OCR page text passes at `difflib` ratio >= 0.95 on `quotes.normalize` text plus
  exact `must_contain` spans (`tests/test_stage3_exit.py`); measured min_ratio 1.000 on the fixture.
- T-13 (round 3 brief): ocrmypdf flags `--redo-ocr --output-type pdf -l eng` (`intake.OCR_FLAGS`); no `--deskew`,
  `--clean` or `--rotate-pages` until a real binder shows the need (stage 9 benchmark).
- T-14 (round 3 brief): `[ocr].timeout_s` 3600 per PDF; `intake.PAGE_TIMEOUT_S` 180 (`--tesseract-timeout`);
  doctor smoke timeout 120 s.
- T-15 (round 3 brief): fixture rendering 300 dpi, body 44 px, stamps 60 px, JPEG quality 90, fixed PDF dates
  (`tests/fixtures/scanned/make_scanned.py`); `scanned.pdf` 895 KB.
