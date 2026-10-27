# Round 3 blind verification

**Verdict: PASS.** R3-1 to R3-7 `[x]`, R3-8 deferred, V. `[x]`. Three non-blocking test gaps (S1, S2, S5).

Verifier: fresh Opus 5.5, built nothing this round. Branch `loop/round-03`, tip b864faf. Every record used
is invented: the scanned fixture (matter 9002.001), the bench matter 9001.001, and one probe page I made
with `pdfsmoke.render_page` under `$D` (`D=/private/tmp/claude-501/verify`, removed at the end).

## Measured numbers (each from my own run on the tip)

| Probe | Result |
|---|---|
| `/usr/bin/time -p scripts/run.sh pytest -q` | `358 passed in 72.67s (0:01:12)`, `real 73.25` (T-11 budget 90 s: inside) |
| `scripts/run.sh python -m casefile.gate` | prints `0` (`gate prose PASS dashes=0 files=156`, `gate privacy PASS offenders=0 scanned=601`) |
| `scripts/run.sh python scripts/unused_imports.py src tests scripts` | `unused_imports=0` |
| `pytest -q -s tests/test_stage1_exit.py tests/test_stage3_exit.py` | `exit=0 verdicts=8 fails=set() test_jobs=1`; `stage3 exit=1 pages=6 ids_ok=6 of 6 stamps_ok=6 of 6 text_ok=6 of 6 must_ok=5 of 5 empty=1 failed=0 min_ratio=1.000`; `5 passed in 15.33s` |
| bench `--candidate tests/fixtures/bench/flawed.json` | exit 1, `bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2 flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14` |
| bench `--candidate .../9001.001/ideal.json` | exit 0, `found=29 of 29 missed=0 invented=0 extra=2 flags=9 of 9 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14` |
| hand intake of `tests/fixtures/scanned/scanned.pdf` into `$D/matters/9002.001` (config from `config.example.toml`, `[paths].matters` set) | exit 1, `intake 9002.001 scan pages=6 ok=5 empty=1 failed=0 stamps=6 had_text=2 ocr_added=4`, `  empty: scan/004 no text after OCR` |
| same again | exit 2, `re-intake is refused; these folders already exist: .../records/scan, .../pages/scan; remove the old binder by hand before intake runs again` |
| `--binder Scan` | exit 2, plain-words binder message |
| same intake with `matters = "/tmp/claude-501/verify/matters"` (unresolved, `/tmp` is a link) | exit 1, same summary line |
| `casefile doctor --config $D/config.toml` | `doctor ocr PASS smoke=ok stamps=SMOKE7342 ocrmypdf=17.13.0 tesseract=5.5.3 ms=3474` |
| invented image page with `MED 0001` (centre), `ABC-0042` (right), body `QRL-2025-0418` and `MED0001-A` | exit 0, stamps `[{'raw': 'MED 0001', 'stamp': 'MED0001'}, {'raw': 'ABC-0042', 'stamp': 'ABC0042'}]`; no fragment of the claim number |
| `stamps.find` direct | `MED0001-A`, `MED0001A`, `MED0001.2`, `xMED0001`, `QRL-2025-0418` give `[]`; `MED 0001 Page 3`, `(MED0001)`, `Ends MED0001.` give `MED0001` |
| bench, host `127.0.0.1:9` | exit 2, `bench: cannot run: no reply from the model server at http://127.0.0.1:9: <urlopen error [Errno 61] Connection refused>` |
| copy of 9001.001 with `.DS_Store` in `records/` and in `records/medical/` | exit 0, perfect line |
| `binders` listing `medical` twice | exit 2, `binders must be distinct` |
| `records/BadName` folder | exit 2, `unlisted binder folder BadName` |
| whitespace-only `medical/002.txt` | exit 2, `last line is not a Bates stamp` |
| key.json | `facts 29 flags 9`; G7, G8 gaps and G9 (MED0006, DEF0002) read against the pages: true |
| hygiene greps | trailing-whitespace lines in `src tests scripts` `0`; F7 false comments `0`; F8 `split('/')` `0` |

## Visible output

I rendered the six fixture pages with Ghostscript (the Read tool needs poppler, which is not installed) and
read each beside its page record. Page 1: clinic header, DOB 09/03/1979, visit 02/18/2026, injury
02/10/2026, "6 out of 10", "no lifting over 10 pounds", stamp KMR2342: all in the record, word for word.
Page 2: 03/04/2026, "released to full duty with the brace", KMR2343: match. Page 3: study 02/25/2026,
"partial thickness tear", "No full thickness tear is seen", two stamps KMR2344 (centre) and TWP7731
(right): both recorded, none chosen. Page 4 is blank on the image; record `status=empty`, reason
`no text after OCR`, no stamps, listed in `open_ids`. Page 5 (born digital): text and KMR2345 match,
`source=text`, `ocr_added=False`. Page 6: 03/12/2026, "return to work 03/16/2026 on light duty",
KMR2346, `source=mixed`. IDs `scan/001` to `scan/006`, `matter=9002.001`, `page` 1 to 6. In the fixture
every raw stamp equals its normalised form; my probe page shows the raw kept (`MED 0001`, `ABC-0042`) and
the normalised form (`MED0001`, `ABC0042`).

## Seeds (copy, apply, `cmp` differs, full suite, restore, `cmp` identical; every seed restored identical)

| Seed | Mutation | Result |
|---|---|---|
| S1 | intake.py:306 `PageRecord(number, binder,` -> `PageRecord(source.stem, binder,` (every page record says matter `scanned`) | **GREEN** `358 passed`. Test gap |
| S2 | intake.py:85 sidecar `if len(parts) != pages:` -> `if len(parts) < pages:` (extra segments accepted, `zip` drops them) | **GREEN** `358 passed`. Test gap |
| S3 | pdfsmoke.py:87 `resolution=float(DPI)` -> `resolution=72.0` | RED `1 failed` (test_generator_check_passes_and_names_a_changed_page) |
| S4 | config.py:103 `type(value) is expected` -> `isinstance(value, expected)` (`timeout_s = true` accepted) | RED `1 failed` (test_bad_values[... got bool]) |
| S5 | make_scanned.py:171 `--check` compares pixels only: `if a != b` -> `if a[0] != b[0]` | **GREEN** `358 passed`. Test gap |
| S6 | intake.py:313 `open_ids` `!= "ok"` -> `== "empty"` (failed pages left out) | RED `1 failed` (test_skipped_page_is_failed_and_listed) |
| N2 | benchcandidate.py:71 `not isinstance(about, str)` -> `about is None` | RED `2 failed` |
| N3 | matter.py:82 unlisted binder raise -> `pass` | RED `3 failed` |
| N4 | benchkey.py:76 drop `isinstance(item[k], str) and` | RED `2 failed` |
| N5 | bench.py:104 failure line print -> `pass` | RED `5 failed` |

Test gaps, non-blocking (the code is right by direct probe), for a fix worker:
- S1: the stage 3 exit test `judge` (tests/test_stage3_exit.py:42) checks only `record["id"] ==
  "scan/nnn"`; no test reads a page record's `matter` field, though D27 defines the page ID as matter,
  binder, page and `id` itself omits the matter. Add `record["matter"] == "9002.001"` and `record["page"]
  == n` to the `id` verdict.
- S2: tests/test_intake.py:172 covers `5 of 6` only; add a `7 of 6` sidecar case expecting `sidecar
  segments=7 pages=6`.
- S5: tests/test_scanned_fixture.py:63 changes page 2 pixels only; add a text-layer change on page 5 (or 6's
  overlay) expecting `check page 5 differs`.

## Design calls found unlogged (low, none blocking)

- bench.py:64 to 79: a duplicate matter number is found only when the second root is reached, after the
  first matter has run (model call, run log rows, its bench line printed); then exit 2. D28 says refused
  (exit 2) and it is, but the refusal is not up front.
- stamps.py:14 `normalize` strips only space and hyphen. With the default pattern that is letters plus
  digits (Q40); a configured pattern allowing another separator (for example `.`) would give a normalised
  form that is not letters plus digits. config.py:124 also compiles the pattern with a different wrapper
  than stamps.py:23 uses.
- Page record `id` is `binder/nnn`; the matter is a separate field. Fine for D27, but cites in later stages
  must carry the matter themselves.
- Gemma step comments remain in src (`# Main Loop`, `# Load Matter and Key` in bench.py; `# Check overall
  structure`, `# Process facts` in benchcandidate.py). Not the false "prompt-framing" comments of F7, which are
  gone.

## Process notes

- `docs/loop/agent-log.md` gained one line in the working tree during my run; I did not write it (stat
  only, not opened before reconciliation).
- Owner question 38 (`questions-for-owner.md`) still says `MED0001-A` records `MED0001`; after fix cycle 2
  (H1) it records nothing (probe above). The question text is stale.
- The doctor and the stage 3 exit test print different `ms`; nothing else drifted between runs.

## Reconciliation (after every item was ticked)

Read: round03-codex-review.md (with the orchestrator's reproduction notes) and round03-critic.md, plus the
build and fix-cycle notes in the ledger.

- Numbers that match: suite `358 passed` (fix cycle 2); gate `0`; `unused_imports=0`; the flawed and ideal
  bench lines; the stage 3 exit line `stage3 exit=1 pages=6 ids_ok=6 of 6 ... min_ratio=1.000`; the stage 1
  line; the intake summary `pages=6 ok=5 empty=1 failed=0 stamps=6 had_text=2 ocr_added=4`, exit 1, page 3
  two stamps, page 6 `mixed`, re-intake exit 2; the doctor OCR PASS with the same tool versions (ms 3474
  against the critic's 3453).
- Claims I could not reproduce: none. Critic H1 (`QRL-2025` fragment), L1 (one folder named), L3 and L4
  (empty reason) are fixed on the tip, each re-checked by my probes. Critic L5 (second spelling dropped) is
  real and now owner question 40.
- The build notes cite `335 passed in 66.93s` at 2f864a5 and fix cycle 1 `350 passed in 63.42s`; the tip is
  `358 passed` in 72.67 s, still inside T-11.
- Seeds they used that I would have chosen too: dropping the stamp lookahead and lookbehind clauses (H1),
  the doctor returning 0 on OCR FAIL (CX-8), `_publish` catching only `OSError` (CX-3), and the G9 flag
  deleted from the key (chair). None of the builders' seeds touched the page record's `matter` field, the
  sidecar extra-segment direction, or the fixture check's text-layer comparison (S1, S2, S5).
