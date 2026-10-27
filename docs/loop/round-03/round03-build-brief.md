# Round 3 build brief: stage 3 intake and OCR with page IDs (plus R3-2 to R3-7)

Branch `loop/round-03` at `92935be` (working tree: the chair's uncommitted
`docs/loop/questions-for-owner.md` edit plus this brief's §7 appendix to it, untracked `.agents/`,
`AGENTS.md`, `.claude/worktrees/`; leave them). Scope: ledger R3-1 (spec §7 stage 3: a scanned PDF becomes page text with correct IDs), R3-2
(doctor OCR PASS for real, R1-19 smoke), R3-3 (bench exit 2 on no reply, `model=` on the line), R3-4 (key
completeness, Q36), R3-5 (model client carried items), R3-6 (matter loader carried items), R3-7 (hygiene and
verifier gaps N2 to N5). R3-8 stays deferred. Tiers: Q30 defaults (Opus orchestrates, Sonnet 5.5 codes,
Codex reviews plan and code). Privacy: every page, name, date, number and stamp below is invented (§6b);
the one PDF this round adds is generated from invented text by a committed script and lives under
`tests/fixtures/scanned/`.

Measured on the tip 2026-10-27 (this architect, inside the sandbox): `scripts/run.sh pytest -q` ->
`270 passed in 41.98s`; `scripts/run.sh python -m casefile.gate` -> `gate pytest PASS exit=0`, `gate
privacy PASS offenders=0 scanned=567`, `gate rules_selftest PASS misses=0 false_hits=0`, `gate playbook
PASS invalid=0 unmarked=0 version=pb-00be6eb62752`, `gate prose PASS dashes=0 files=140`, prints `0`; flawed
bench -> exit 1, `bench 9001.001 found=26 of 29 missed=3 invented=2 extra=2 flags=5 of 6 flags_missed=1
flags_extra=1 rules=1 pages_failed=0 of 14` plus six detail lines; ideal -> exit 0, `found=29 of 29 ...
flags=6 of 6 ... pages_failed=0 of 14`. Both match the ledger `## Project` baselines.

## §0 Drift (premises verified in the code, not in a report)

- D0.1 **OCR tools are installed (revision pass, Q40).** `/opt/homebrew/bin/ocrmypdf --version` ->
  `17.13.0`; `/opt/homebrew/bin/tesseract --version` -> `tesseract 5.5.3`, `leptonica-1.87.0`;
  `--list-langs` -> `eng`, `osd`; `gs`, `qpdf`, `unpaper`, `pngquant`, `jbig2`, `img2pdf` present. The
  sandbox shell's `PATH` (measured) has no `/opt/homebrew/bin`, so `shutil.which("ocrmypdf")` fails in
  every sandboxed run unless the wrapper adds it (§1.17), and ocrmypdf itself finds tesseract by PATH
  (measured: with `/opt/homebrew/bin` absent, `ocrmypdf` exits 3 `Could not find program 'tesseract' on
  the PATH` even when invoked by absolute path), so intake must put the configured tesseract's folder on
  the child's PATH (§1.7). At the first writing of this brief neither tool nor Homebrew existed; §5 R1 is
  closed.
- D0.14 **Measured on the installed tools (revision pass, invented three-page image-only PDF in
  `$TMPDIR`).** `ocrmypdf --redo-ocr --output-type pdf --sidecar S -l eng IN OUT` -> exit 0 in 3 s;
  sidecar holds 2 form feeds for 3 pages (one segment per page, the blank page's segment empty); page
  texts against the rendered lines score ratio `1.0` on both text pages; stamps found `['KMR2342']` and
  `['KMR2344', 'TWP7731']`; pdfminer (stand-in for pypdf, which the brew python lacks) reads the output
  text layer as `Harrowgate Occupational Clinic Progress Note ... KMR2342 \x0cPinecrest Imaging ...
  KMR2344 TWP7731 \x0c\x0c`. With `--tesseract-timeout 0` -> exit `0` and a sidecar of three segments each
  `[skipped page]` (Codex 3 confirmed: a per-page timeout is not a failure to ocrmypdf). Source read:
  `tesseract.py:402-407` (`except TimeoutExpired: ... _generate_null_hocr`), `_pipeline.py:787-791` (`if
  options.mode == ProcessingMode.redo: mask = True  # Mask visible text, but not invisible text`),
  `_pipeline.py:1543-1565` `merge_sidecars` writes `\f` between pages and, for pages with no OCR text
  file, one `[OCR skipped on page(s) N-M]` placeholder per compressed range (Codex 4 confirmed). **Sandbox
  quirk:** tesseract cannot open a file spelled `/tmp/claude-501/...` inside this sandbox (`Error in
  fopenReadStream: failed to open locally`) but reads the same file as `/private/tmp/claude-501/...` or
  under the checkout; every run with input, output, sidecar and `TMPDIR` given as resolved
  `/private/tmp/...` paths succeeded. Intake resolves every path it hands to ocrmypdf (§1.7); pytest's
  `tmp_path` is already resolved (`/private/tmp/...`), so the suite is unaffected, but a hand run with
  `$TMPDIR` spelled `/tmp/...` fails with exit 7 (§5 R13). Pillow 13.0.0 (brew python; the project venv
  gets the same version) writes byte-identical PDFs when `creationDate` and `modDate` are fixed and the
  output basename is the same (its `/Title` is the basename; `PdfImagePlugin.py:217-218` defaults the
  dates to `time.gmtime()`).
- D0.2 **Doctor OCR check is a stub by design.** `src/casefile/doctor.py:156-172` `check_ocr` runs
  `--version` on both tools and always returns `False, "OCR not verified: ..." + "; smoke test arrives in
  stage 3"` (line 172); `next_step` at `:190-195` says `expected until stage 3`. `tests/conftest.py:200-202`
  `ocr_expected_fail()` returns `True`; `tests/test_stage1_exit.py:22` and `tests/test_doctor.py:57, 215`
  read it; `tests/test_doctor.py:197-215` asserts the stub's exact reason string. Stage 1 exit prints
  `exit=1 verdicts=8 fails={'ocr'} test_jobs=1` today (ledger R2 report).
- D0.3 **Config has `[ocr]` with tool names only.** `src/casefile/config.py:25` `DEFAULTS["ocr"] =
  {"tesseract": "tesseract", "ocrmypdf": "ocrmypdf"}`, `:30` `KNOWN_KEYS["ocr"] = ("tesseract", "ocrmypdf")`,
  `:50-53` `class OCR: tesseract: str; ocrmypdf: str`; `:98` types every key as `str` except `num_ctx`,
  `timeout_s` (int) and `temperature` (float), so a new int key must be added to that tuple. An unknown key
  is `ConfigError` (`:85-87`). `config.example.toml:16-18` mirrors the two names.
- D0.4 **Page has one stamp.** `src/casefile/matter.py:18-27` `Page(binder, number, bates, text)` with
  `page_id = f"{self.binder}/{self.number:03d}"`; `:36-41` `Matter.page(bates)` compares `page.bates ==
  bates`; `:115-134` takes the last non-blank line as the stamp, `re.fullmatch(STAMP_PATTERN, stamp)` at
  `:121`, refuses a duplicate at `:132-133`; `STAMP_PATTERN = r"[A-Z]{1,8}[ -]?\d{4,}"` at `:9`,
  `NUMBER_PATTERN = r"\d{4}\.\d{3}"` at `:10`. Users of `.bates`: `src/casefile/benchrun.py:30`
  (`=== PAGE {page.page_id} BATES {page.bates} ===`), `tests/test_fixture_matter.py:19`,
  `tests/test_fakemodel_bench.py:14`. `benchkey.py:79, 121` and `benchscore.py:73` go through
  `matter.page(cite)`.
- D0.5 **Matter loader carried defects, as the code stands.** `matter.py:71` checks `binders` is a nonempty
  list of nonempty strings, not that the names are distinct (F4). `:77` `names = sorted(p.name for p in
  records.iterdir())` and `:81-83` refuse any entry not in `binders`, so a Finder `.DS_Store` refuses the
  matter as `unlisted binder folder .DS_Store` (F3); `:97` lists binder entries the same way. `:102-105`
  validates each page name inside the read loop (F5). `benchkey.py:75` and `:117, 126` accept a
  whitespace-only `text` or `about` (`isinstance(..., str) and item[k]`; F6). `bench.py:37, 65-73` loads
  each root and never compares `matter.number` across roots (duplicate numbers, OR-8).
- D0.6 **Model client carried defects (corrected in the revision pass).** `src/casefile/model.py:55-56`
  `except error.HTTPError as exc: reply = exc.read()`: on Python 3.12.13 an `HTTPError` built with
  `fp=None` reads `b""` (measured: `HTTPError("http://x", 503, "x", {}, None).read()` -> `b''`, `fp` is a
  `BytesIO`; `urllib/error.py:45` substitutes it), so the "no body stream" carried item is already
  correct code and needs only a test (Codex 8). `benchrun.py:69-71` stores a row only `if exc.raw is not
  None` and the redirect test has no empty-body 3xx case (verifier 3 S5). `model.py:61-62` `except
  (OSError, error.URLError)` raises `ModelError(str(exc))` with `raw=None` both when the connection fails
  and when a read fails after the status line (`model.py:49` reads the status, `:54` the body; a read
  timeout is an `OSError`), so `raw is None` cannot mean "no reply" (Codex 9). `http.client.IncompleteRead`
  is an `HTTPException`, not an `OSError` (measured), so a short body escapes both handlers as a traceback.
- D0.7 **Bench line and exits.** `benchscore.py:43-47` `Score.line(matter_number)` prints `bench <number>
  found=... pages_failed=P of N` with no model; `bench.py:95-96` prints `bench <number> failure <text>`
  then scores anyway (`:99-103`) and returns `0 if imperfect == 0 else 1` (`:111`); exit 2 branches are
  `:25, :32, :40, :45, :50, :60, :72, :83, :90`. `benchrun.py:46-50` `RunResult(candidate, pages_failed,
  failure)`; `:68-73` the `ModelError` path. Six test files hold the exact line text:
  `tests/test_benchscore.py`, `test_bench_detail.py`, `test_bench_discovery.py`, `test_bench_cli.py`,
  `test_stage2_exit.py:19-20`, `test_bench_multi.py` (grep `found=29 of 29`, `found=26 of 29`).
- D0.8 **Key as it stands.** `tests/fixtures/matters/9001.001/key.json` has 29 facts F01 to F29 and 6 flags:
  G1 conflict MED0001,EMP0001 (tote weight); G2 conflict MED0001,MED0003 (prior back); G3 conflict
  MED0008,DEF0003 (causation); G4 gap MED0002 (x-ray); G5 gap MED0005 (PT discharge summary); G6 conflict
  MED0007,DEF0002 (radiculopathy). `benchkey.py:129-131` refuses two flags with the same kind and cite set,
  so a second conflict on MED0008,DEF0003 cannot be a separate flag (Q34: D25 kind plus cite set stands).
  `ideal.json` carries the 6 flags and 31 facts (29 key plus hire date EMP0001:17 and 50 pounds EMP0002:26,
  the `extra=2`); `flawed.json` misses G3 and adds conflict MED0001,MED0004 (the `flags_extra=1`).
  `tests/test_fixture_matter.py:35-37` asserts `(29, 6, 14)` and ids `G1..G6`.
- D0.9 **Privacy and ignore rules admit a fixture PDF.** `.gitignore:4` ignores `*.[pP][dD][fF]`, `:52`
  `!tests/fixtures/**` un-ignores the fixtures tree; `src/casefile/privacy.py:7` `SUFFIXES` holds `.pdf`,
  `.png`, `.jpg` and more, `:37` exempts paths starting `tests/fixtures/`. `git ls-files --others` lists
  the nested worktree `.claude/worktrees/agent-a582821e2b2e41b16/` as one directory entry (measured: 1
  match, 0 files), so a PDF committed inside a lane B worktree is not an offender in the main tree. The
  prose row (`src/casefile/prose.py:6-8`) scans `tests/**/*.py` and `tests/fixtures/**/*.json`, so the
  generator and the manifest must hold no dashes.
- D0.10 **Dependencies.** `pyproject.toml` has `dependencies = []`, dev group `pytest>=8,<9`; the venv at
  `~/.casefile-dev/legal-harness/venv` (Python 3.12.13) holds pytest and casefile only. `uv pip install
  --dry-run pypdf pillow` (temp cache, hosts `pypi.org`, `files.pythonhosted.org`) resolves `pypdf==6.21.3`
  and `pillow==13.0.0`. The toolchain cache `~/.casefile-dev/legal-harness/cache` is outside the sandbox
  write allowlist (`Operation not permitted` on `sdists-v9/.git`), so `uv add` and `uv sync` run once with
  the sandbox off, by the chair (§5 R4). `scripts/run.sh:4` builds the toolchain path from `basename
  "$ROOT"`, so a worktree named `agent-...` gets its own venv under `~/.casefile-dev/agent-.../` and needs
  its own sync (§3, §5 R7). `scripts/run.sh` never runs `uv sync` itself (no `uv` call in run.sh or
  run_capture.py).
- D0.11 **Run log schema v1 cannot hold an intake run.** `src/casefile/runlog.py:12-15` `runs` requires
  `card`, `card_version`, `model` and `prompt_sha256` NOT NULL; `count_test_jobs` at `:89-93` counts
  `doctor.warmup` rows only. Intake makes no model call; §1.6 keeps it out of the run log this round.
- D0.12 **Harness facts the builder relies on.** `tests/conftest.py:26-71` `write_config(tmp_path,
  **overrides)` (ocr table at `:46`, overrides merge by table or key); `tests/test_doctor.py:28-41`
  `setup_config`, `invoke(config, *, fake=None, lsof=None)` calls `doctor.run(config, out=, opener=,
  lsof_runner=)` (`doctor.py:203`); `tests/test_stage1_exit.py:21-40` `assert_exit` reads
  `ocr_expected_fail()` to decide `expected` and the exit code; `tests/fakemodel/core.py:138-154`
  `FakeTransport.open` raises `HTTPError(url, status, msg, headers, response)` for status >= 400 and
  returns `FakeResponse` (a `BytesIO` with `getcode`, `headers`) otherwise; `tests/test_model.py:18-23`
  has a bare `Transport(response)` stub. `tests/test_run_sh.py:382` runs the wrapper with
  `PATH="/usr/bin:/bin"` to test python3 resolution: `PY` is resolved at `run.sh:9` before any PATH edit,
  so appending to PATH later in the script cannot disturb it.
- D0.13 Tuning entries end at T-10 (`docs/loop/tuning-questions.md`); owner questions end at 36 (31 to 36
  answered, ledger Q40); spec §9 ends at D26; the ledger's round 3 section is R3-1 to R3-8.
- D0.15 **Regression contracts the first draft missed (Codex 10 to 13, each confirmed in the file).**
  `tests/test_bench_multi.py:22-23` copies matter 9001.001 into `a` and `b` (two roots, one number) and
  expects both runners to run and exit 1; `tests/test_benchscore_cite.py:31` calls `s.line("9001.001")`
  with one argument and asserts the old format; `tests/test_config.py:99` asserts `len(lines) == 10`
  config fields; `tests/test_fix_cycle2.py:28-32` asserts the stub reason `OCR not verified: tools found
  (tesseract exit=0, ocrmypdf exit=0); smoke test arrives in stage 3`; `tests/test_doctor.py:34-39`
  `invoke()` calls `doctor.run` with no OCR injection and is used by `test_fix_cycle2.py:106, 108, 120,
  158, 164`, `test_fix_cycle4.py:111` and `test_fix_cycle2.py:113` calls `doctor.run` directly;
  `tests/test_stage1_exit.py:54, 87` run the doctor with `timeout=60`. `benchrun.py:56` and `:95` build
  `RunResult` with three positional arguments.

## §1 Decisions, with trade-offs

1. **Stage 3 uses ocrmypdf and Tesseract plus pypdf; Docling waits.** OCR runs as one `ocrmypdf` call per
   PDF (`--redo-ocr --output-type pdf --sidecar <work>/sidecar.txt -l eng <in> <out>`); page text is read
   from the output PDF with `pypdf` (`PdfReader(out).pages[i].extract_text()`), the same call for OCR'd
   and born-digital pages. `--redo-ocr` (not `--skip-text`) because Bates software stamps scanned pages
   with a digital text layer; `--skip-text` would then skip the whole page and the scanned body would
   never be read (fail-open by tool default). D6 names Docling for layout and tables; stage 3 produces
   page text, which needs neither, and Docling pulls torch plus model downloads from Hugging Face at
   first run (hundreds of MB, network in a sandbox, nondeterministic page text across model versions).
   Deferring is not rebuilding: no layout code is written here. Docling returns when a stage needs tables
   (stage 5 memo) and only if the benchmark says so (pillar 6). Rejected: `--force-ocr` with the sidecar as
   the only text source (no pypdf): simpler, but it re-OCRs born-digital pages and loses exact text,
   against pillar 1. Rejected: pdfminer or PyMuPDF for extraction (heavier; PyMuPDF is AGPL). Spec §9 row
   D27 (§6). **Per-page OCR outcome (Codex 3, 4; measured D0.14).** ocrmypdf exits 0 when Tesseract times
   out on a page and writes `[skipped page]` as that page's sidecar text, and in redo mode the sidecar
   never holds visible digital text (it is masked before OCR), so the sidecar is read for outcomes, never
   for page text: intake passes `--tesseract-timeout 180` (constant `PAGE_TIMEOUT_S`, T-14), splits the
   sidecar on `\f`, requires exactly one segment per input page (else exit 2 `sidecar segments=S pages=P`),
   and marks a page whose segment is `[skipped page]` as `status: "failed"`, `reason: "ocr timeout"`,
   `text: ""`, `stamps: []`, counted and listed like an empty page (exit 1). Any `[OCR skipped on page(s)`
   placeholder (a page ocrmypdf declined entirely; it should not occur in redo mode) is exit 2, fail
   closed. The sidecar fallback for page text from the first draft is withdrawn: masking makes it lose
   digital stamps and compressed placeholders make its segment count unreliable; if pypdf's text scores
   under the §1.8 floor the builder stops and reports the measured ratios (chair call), nothing is
   substituted.
2. **A page ID is matter, binder, page; stamps are a list, none chosen (Q35), each raw and normalised
   (Q40).** The intake page record (§1.5) has `"id": "<binder>/<nnn>"` (the `matter.Page.page_id` format,
   D0.4) and `"stamps": [{"raw": "MED 0001", "stamp": "MED0001"}, ...]`: every match of the configured
   stamp pattern anywhere in the page text, in text order, where `stamp` is `stamps.normalize(raw)`
   (uppercase, spaces and hyphens removed; letters plus digits) and two matches with one normalised form
   are kept once (first raw wins). `src/casefile/stamps.py` (W0, written before the lanes split) holds
   `normalize(raw) -> str` and `find(text, pattern) -> list[Stamp]`; every cite comparison in the bench
   (`Matter.page`, `benchkey`, `benchscore`) normalises both sides with the same function, so `MED-0001`
   in a candidate matches the page stamped `MED0001` (owner Q40). What changes now: `matter.Page` gains
   `stamps: tuple[str, ...]` (normalised) and loses `bates`; the authored bench format (the stamp alone on
   the last line, D25) stays and loads as `stamps=(normalize(last_line),)`; `Matter.page(cite)` returns
   the first page with `normalize(cite) in page.stamps`; `benchrun.page_block` prints `BATES
   {" ".join(page.stamps)}` (identical text for the 14 authored stamps, so the stage 2 prompt and its sha
   are unchanged). What waits: hearing
   prep asking which stamp to cite (stage 6); stamp positions (OCR text carries none; pypdf positions are a
   later refinement if the attorney wants a default). The stage 2 bench format does not move: the
   benchmark matters are authored text (Q34 Q22: same layout outside the checkout) and the key's cites
   are the author's stamps. Rejected: a `bates` property returning `stamps[0]` for compatibility: that is
   the silent choice Q35 forbids (#R01-OC-M2 class). D25 amended (§6).
3. **Stamp pattern and OCR timeout become config keys under `[ocr]`.** `[ocr].stamp_pattern` (default
   `[A-Z]{1,8}[ -]?\d{4,}`, Q21, T-10) and `[ocr].timeout_s` (default 3600, int, positive). The pattern must
   compile and is applied as `(?<![A-Z0-9])(?:<pattern>)` so a match never starts inside a longer token
   (`9KMR2344` yields nothing; `kmr2344` and `KMR234` yield nothing; `XKMR2344` and `KMR23441` are complete
   stamps under Q21 and are recorded, Codex 2; the first draft's examples were wrong and its trailing
   lookahead was redundant because `\d{4,}` is greedy); a pattern that does not compile is `ConfigError`
   (fail closed, D13). `matter.STAMP_PATTERN`
   stays the authored-format constant (the loader takes no config; T-10 note updated). Rejected: a new
   `[intake]` table (one more table for two keys) and reading the pattern from `playbook/rules.toml`'s
   `bates_pattern` (`rules.toml:57` admits ranges and lists; a page stamp is one stamp).
4. **`casefile intake --matter NUMBER --binder NAME FILE [--config]`.** `NUMBER` must fullmatch
   `matter.NUMBER_PATTERN`; `NAME` must fullmatch `[a-z][a-z0-9-]{0,39}`; `FILE` must be a readable PDF
   (pypdf opens it and counts pages before OCR). The matter folder `<paths.matters>/<NUMBER>/` must exist
   (never created: #R01-OC-M7) and must be where it says: `pathguard.classify(str(matter_dir), checkout)`
   must be `outside` and `matter_dir.resolve()` must be a descendant of `config.paths.matters` (already
   resolved by identity at config load, `config.py:146`), so a symlinked matter folder cannot send
   `source.pdf` into the checkout or into another matter (Codex 7; #R01-V-B1b class; exit 2 `matter folder
   resolves outside the matters root`). Neither `<matter>/records/<NAME>/` nor `<matter>/pages/<NAME>/`
   may exist (no silent overwrite; re-intake is refused, owner Q40 item 34; Codex 6). Rejected: deriving the
   binder from the file name (spaces, dates and client names in file names; the attorney decides, pillar
   5).
5. **Page store: JSON, one file per page, beside the OCR'd copy.** Layout under the matter folder:
   `records/<binder>/source.pdf` (byte copy of the input), `records/<binder>/ocr.pdf` (ocrmypdf output),
   `records/<binder>/sidecar.txt`, `pages/<binder>/<nnn>.json` and `pages/<binder>/binder.json`. Page
   record keys, exactly: `matter`, `binder`, `page` (int, 1-based), `id`, `stamps` (list of `{"raw",
   "stamp"}`, §1.2), `text` (pypdf text as extracted, no normalisation), `had_text_layer` (bool: the input
   page had extractable text), `ocr_added` (bool: normalised text differs before and after OCR), `source`
   (`"text"`, `"ocr"`, `"mixed"` or `"none"`, derived: text layer only, OCR only, both, neither), `status`
   (`"ok"` when the normalised text is nonempty and the page was not skipped; `"empty"` when it is empty;
   `"failed"` when the sidecar says `[skipped page]`, §1.1), `reason` (`""`, or `"ocr timeout"`), `sha256`
   (of the input file). `binder.json`: `matter`, `binder`, `file` (input name), `sha256`, `pages`, `ok`,
   `empty`, `failed`, `open_ids` (every page not `ok`), `tools` (`ocrmypdf` and `tesseract` version
   strings), `args` (the ocrmypdf argument list), `written` (UTC ISO). Publication is atomic per folder:
   intake builds `records/<binder>.tmp/` and `pages/<binder>.tmp/`, writes every file, then renames each to
   its final name (`os.rename`, same filesystem); on any failure before the renames both `.tmp` folders
   are removed and nothing else is touched (Codex 6; a crash between the two renames leaves `pages/
   <binder>.tmp`, which the next intake refuses with a message naming it). Why JSON: the
   stage 5 case file is JSON; a list of stamps and the per-page provenance do not fit the D25 text
   format. Why keep `source.pdf` and `ocr.pdf`: the attorney and the stage 8 page need the page image, and
   the sha256 ties records to the file. Rejected: writing D25 `.txt` pages (one stamp, no provenance) and
   a single `pages.json` per binder (a 300-page binder in one file is hard to diff and to append to).
6. **Fail closed on empty and skipped pages and on every tool failure; no run log rows this round.** A
   page whose normalised text is empty after OCR is written with `status: "empty"`, `text: ""`, `stamps:
   []`; a page Tesseract skipped is `status: "failed"`, `reason: "ocr timeout"` (§1.1); both are counted and
   listed (`  empty: <id>` and `  failed: <id> ocr timeout` detail lines), never counted as read (owner Q40
   item 32). Exit codes: 0 when every page is `ok`; 1 when intake completed but some pages are `empty` or
   `failed` (spec §4: marked and listed as open items); 2 when it cannot run (bad arguments, matter folder
   missing or resolving outside the matters root, `records/<binder>` or `pages/<binder>` or a `.tmp` of
   either exists, unreadable PDF, tool not found, ocrmypdf non-zero exit or timeout with the last 300
   characters of its stderr, sidecar segments not equal to pages, an `[OCR skipped on page(s)` placeholder,
   input and output page counts differ, cannot write). Nothing final is published until every page record
   is built (§1.5 atomic rename); on exit 2 the `.tmp` folders are removed. Intake writes no run log row:
   `runs`
   needs a card and a model (D0.11) and OR-8 set the precedent that a mode with no model call writes none;
   the job runner at stage 5 adds intake rows with schema v2. Rejected: exit 0 with empty pages (silent
   empty text, pillar 2) and stub `runs` rows with placeholder card and model (a false record).
7. **ocrmypdf works inside the matter folder, in its own process group that intake owns.** Intake runs
   ocrmypdf with `TMPDIR` set to `<matter>/records/<binder>.tmp/work/` and removes that folder in a
   `finally`, so client bytes never sit in the shared TMPDIR (#R01R-OC-F1 class). Every path handed to
   ocrmypdf (input, output, sidecar, TMPDIR) is `Path.resolve()`d first (D0.14 sandbox quirk; also the
   honest spelling for the record). The child's environment PATH is `dirname(which(config.ocr.tesseract))
   + os.pathsep + PATH` because ocrmypdf finds tesseract by PATH (D0.1). Process control (Codex 5):
   `subprocess.Popen(args, start_new_session=True, stdout=PIPE, stderr=PIPE)` then `communicate(timeout=
   config.ocr.timeout_s)`; on `TimeoutExpired`, `os.killpg(proc.pid, SIGKILL)`, `wait()`, exit 2; for the
   duration of the call intake installs SIGINT, SIGTERM and SIGHUP handlers that `killpg` the OCR group,
   remove the `.tmp` folders and exit `128 + n` (mirrors run_capture's own handlers; run_capture.py:122
   kills the app's group, which the OCR group has left, so intake must do it). `subprocess.run(timeout=)`
   is rejected: it kills only the direct child (`subprocess.py:548`), leaving tesseract and gs running.
   The lifecycle has a test with a stub `ocrmypdf` that spawns a sleeping grandchild (W5). Cancel from the
   job runner is stage 5.
8. **"Correct page text" is a per-page similarity, with an exact stamp set.** For each manifest page:
   `ratio = difflib.SequenceMatcher(None, quotes.normalize(expected), quotes.normalize(got)).ratio()`
   (`quotes.normalize`: casefold, straight quotes, collapsed whitespace, `quotes.py:7-10`); a page passes
   when `ratio >= 0.95` (T-12), every span in the manifest's `must_contain` list for that page is found
   verbatim in the normalised text (`quotes.found_in`), the record's normalised `stamps` equal the
   manifest's list as a set, its `id` equals `scan/<nnn>` for its position, and `status` matches (`empty`
   for the blank page). `must_contain` holds the spans a digit or a negation would change (Codex 14,
   measured: one digit plus one dropped "no" in a 120-character line still scores 0.98): for the fixture,
   page 1 `02/18/2026`, `6 out of 10`, `no lifting over 10 pounds`; page 2 `03/04/2026`, `released to
   full duty`; page 3 `02/25/2026`, `partial thickness`; page 5 `two visits per week for four weeks`; page
   6 `return to work 03/16/2026`. Threshold reasoning: Tesseract on clean 300 dpi rendered text measured
   `1.0` on the probe pages (D0.14); pypdf spacing artefacts may cost a point or two; a half-page loss
   scores about 0.67. The threshold is a constant in the test, printed with the measured minimum, never a
   parameter (#R02-CH-1: a boundary test at 0.95 and 0.9499 proves the comparison). Stamps are exact
   because IDs are the point of the stage: a misread stamp is a red test, not a tolerance. Rejected: byte
   equality on OCR text (OCR is fuzzy) and a global ratio over the whole binder (one lost page hides in
   six).
9. **The fixture is a generated, committed, manifest-pinned, byte-stable PDF.** `tests/fixtures/scanned/
   make_scanned.py` (Pillow for the image pages, now a runtime dependency because the doctor renders its
   smoke page with it, §1.10; pypdf for assembly) renders invented pages with Pillow's bundled font
   (`ImageFont.load_default(size=...)`, no system font) at 300 dpi (2550 x 3300, mode `L`, JPEG quality
   90; T-15) through `casefile.pdfsmoke.image_pdf(pages, out_path)` (Pillow save with `creationDate=
   time.gmtime(0)`, `modDate=time.gmtime(0)`, always written under the basename `scanned.pdf` so the
   `/Title` is fixed: measured byte-identical across two runs, D0.14), writes `scanned.pdf` and
   `scanned.json` (the manifest: matter, binder, sha256 of the PDF, per page `page`, `kind`, `stamps`,
   `must_contain`, `text`). The text page and the digital stamp overlay come from `casefile.pdfsmoke
   .text_pdf(lines)` (stdlib, hand-written PDF with Helvetica, no embedding). Six pages (matter
   `9002.001`, binder `scan`): 1 image, stamp `KMR2342`
   bottom centre; 2 image, `KMR2343`; 3 image, two stamps `KMR2344` bottom centre and `TWP7731` bottom
   right; 4 blank, unstamped (a separator sheet; status `empty`); 5 born-digital text page, stamp
   `KMR2345` in the text; 6 image body with a digital text-layer stamp `KMR2346` (the Bates-software case
   §1.1 exists for). Six stamps on five stamped pages. Reproducible means: the generator is committed, the
   manifest pins the committed PDF's sha256 (a test checks it), and `make_scanned.py --check` regenerates
   into a temp folder and compares bytes first (`bytes_equal=1` expected on the locked Pillow and pypdf
   versions), then content regardless of bytes: per page the sha256 of the decoded image pixels (`pypdf`
   `page.images[0].image.tobytes()`), the text-layer text and the page count; it exits 1 when content
   differs and prints which page (Codex 15). No PNG or intermediate image is written anywhere. Rejected: a
   hand-scanned or printed PDF (not reproducible, and nothing real may be scanned, Q9) and reportlab
   (another dependency for one text page).
10. **The doctor's OCR check runs the intake path, with the intake flags, on an image-only smoke page.**
    `check_ocr`: `shutil.which` on both configured tools (FAIL `not found: <name>`), `--version` on both
    (kept as evidence strings), then `pdfsmoke.image_pdf([["CASEFILE OCR SMOKE 7342"]], tmp / "smoke.pdf")`
    (Pillow, bundled font, 300 dpi, no text layer: the input has nothing to copy, Codex 16),
    `intake.run_ocr(...)` with exactly intake's `--redo-ocr` arguments (no `mode` parameter: the doctor
    proves the production path), `intake.page_texts(out)`, `stamps.find(text, pattern)`: PASS only when
    `page_texts(smoke.pdf)` was empty before OCR, the normalised text after OCR contains `casefile ocr
    smoke` and the stamps normalise to `["SMOKE7342"]` (raw `SMOKE 7342` matches the Q21 pattern, so one
    line proves OCR, the stamp finder and Q40's normalisation together). Reason line on PASS: `smoke=ok
    stamps=SMOKE7342 ocrmypdf=<ver> tesseract=<ver> ms=<n>`; on FAIL the specific step (`smoke input had
    text`, `smoke text not read: <first 40 chars>`, `smoke stamp not found`, `ocrmypdf exit=<n>: <tail>`,
    `timeout after 120 s`). Timeout 120 s (T-14). Claims only what ran (#R01-CX-9, #R01-OC-H1). The smoke
    callable is injectable (`doctor.run(..., ocr_smoke=None)`, as `lsof_runner` is) and `tests/test_doctor
    .py:34` `invoke()` injects a passing fake by default (Codex 13), so unit tests do not pay for a real
    OCR run; exactly one unit test (`ocr_smoke=None`), both stage 1 exit tests and the stage 3 tests run the
    real tools. Rejected: the committed fixture PDF as the smoke input (`src/` reading `tests/`; the doctor
    runs on the Studio without the fixture tree's guarantees) and the first draft's vector text page with
    `--force-ocr` (a tool that copies input to output would have passed, and the mode differed from
    intake's).
11. **Tests that need OCR fail when the tools are absent; they never skip.** Q39 makes the tools a
    precondition of this Mac and the Studio; a skip would turn the stage 3 exit test green on a machine
    with no OCR (#R01-CX-9 class). They carry a `pytest.mark.ocr` marker (registered in `pyproject.toml`
    beside `socket`) so a builder can select or count them. Rejected: `pytest.skip` when `which` fails.
12. **Bench: no reply from the model server is exit 2 (Q26); the line names the model (Q27).**
    `ModelError` gains `received: bool` set by `_request` itself, not inferred from `raw` (Codex 9):
    `received = False` before `self.opener.open(...)`; the moment `open` returns or raises `HTTPError`
    (a status line arrived) it is `True`; every `ModelError` raised after that point carries
    `received=True` even with `raw=None` (a read timeout after the status, an `OSError` mid-body);
    `OSError`/`URLError` raised by `open` itself carries `received=False`. `http.client.HTTPException`
    (`IncompleteRead`, `RemoteDisconnected`, bad status line) is caught beside `OSError`: `IncompleteRead`
    stores `exc.partial.decode("utf-8", errors="replace")` as `raw`, the others `raw=None`, both
    `received=True` when `open` had returned. `benchrun.run`: a received error with `raw=None` stores one
    `failed` row with `raw_answer=""` (OR-8: every received reply is a row; the body never came). `RunResult`
    gains `reply_received: bool` with no default, set explicitly at all three construction sites
    (`benchrun.py:56` `_fail` and `:95` success -> `True`; the `ModelError` path -> `exc.received`; Codex
    12). `bench.main`: when `result.failure` and not `result.reply_received`, print the failure line as
    today, then `bench: cannot run: no reply from the model server at <config.model.host>: <error>` to
    stderr and return 2 without scoring; a received bad reply still scores `found=0` with exit 1 (D25).
    `Score.line(matter_number, model)` prints `bench <number> model=<tag> found=...`; `model` is
    `config.model.name` in runner mode and the literal `candidate` in `--candidate` mode (a file has no
    model; the path is on the command line). Rejected: `raw is None` as the signal (wrong on a read
    timeout), exit 2 on any `bench.model` failure (a 404 for an unknown model tag is a received reply and a
    real score of the setup) and `model=candidate:<file>` (file names with spaces break the one-line
    format).
13. **Key completeness (Q36): two new flags, three widened `about` texts, facts unchanged.** From the
    pages (every line cited is in `tests/fixtures/matters/9001.001/records/`): G7 gap MED0003 (MED0003:27
    "Follow up in four weeks": no later Brightwater note is in the records); G8 gap MED0008 (MED0008:13 the
    planned injection and :19 the 06/20/2025 re-evaluation: neither record is present). Withdrawn from the
    first draft (Codex 18, owner question 37): a conflict MED0006,DEF0002 over the report calling L4-L5
    "degenerative" (DEF0002:32) against the MRI's "4 mm posterior central disc protrusion" (MED0006:25):
    MED0006:23 also reads "mild degenerative change noted at the lower vertebral levels", so the MRI does
    not exclude degeneration at L4-L5 and the disagreement is an inference; under D25 a keyed flag a careful
    model declines to infer fails that model (`benchscore.py:40`), so only unambiguous disagreements are
    keyed (interim, pending the owner). Widened abouts, because
    their cite sets already exist and D25 matching is by kind plus cite set: G3 (MED0008,DEF0003) names
    causation (MED0008:17 vs DEF0003:20), MMI (MED0008:18 vs DEF0003:21), restrictions (MED0008:15 vs
    DEF0003:22) and treatment (MED0008:13 vs DEF0003:23); G5 (MED0005) names the visit notes other than
    the evaluation and visit 6 (MED0005:7 "Visit: 6 of 12"), the letter to Dr. Castellanos-Reyes
    (MED0005:34) and the discharge summary (MED0005:33); G6 (MED0007,DEF0002) names radiculopathy
    (MED0007:25 vs DEF0002:25), the straight leg raise (MED0007:23 vs DEF0002:24) and strength (MED0007:20
    vs DEF0002:19). Not added: a third cite DEF0001 on G1 (DEF0001:21 repeats the claimant's own 60 pound
    account; the two primary accounts are MED0001 and EMP0001) and the job description's 50 pounds
    (EMP0002:26, a limit, not an account of the incident); conflict MED0001,MED0004 (pain scores on
    different dates) stays the flawed candidate's `flags_extra`. Facts stay at 29 (Q36 is about gaps and
    conflicts; critic L1 stays an owner matter). `ideal.json` and `flawed.json` both gain G7 and G8 so the
    flawed candidate keeps missing exactly G3 (#R02-OC-H1: the key is read against the pages, not only
    loaded). Eight flags in all.
14. **Model client: the no-body-stream HTTPError is closed by a test, not a change; the empty-body 3xx
    case is tested.** Measured on the project interpreter (D0.6): `HTTPError(..., fp=None).read()` returns
    `b""`, so `model.py:56` already yields `raw=""` and `benchrun.py:69-71` already stores the row. W3 adds
    the test that proves it (a stub transport raising `HTTPError(url, 503, "x", {}, None)` -> one `failed`
    row, `raw_answer == ""`) and no code change (Codex 8). The redirect test gains a 302 with an empty body
    through the `FakeResponse` path so verifier 3's S5 seed goes red. (#R02-V-F1: every reply path has a
    test.)
15. **Matter loader: dotfiles ignored, distinct binders, names first, whitespace refused, numbers unique.**
    (a) Entries whose name starts with `.` are ignored in `records/` and in each binder folder (F3; macOS
    writes `.DS_Store`; this is the only ignore rule, D25 amended); (b) `binders` must be distinct (F4,
    message `binders must be distinct`); (c) every binder's listing is validated before any page is read
    (F5); (d) `benchkey` refuses a whitespace-only `text` or `about` (F6: `item[k].strip()`); (e)
    `bench.main` refuses two roots with the same `matter.number` with `bench: duplicate matter number
    <n> in <a> and <b>` and exit 2 (OR-8 carried; #R02-CX-5 class). `tests/test_bench_multi.py:22-23`
    copies one matter into `a` and `b` (Codex 10): the test rewrites `b/matter.toml` to `number =
    "9001.002"` (its key and pages are unchanged; `key.json` is validated against pages, not the number)
    and keeps its imperfect-first, perfect-second scenario; a second case keeps both numbers equal and
    asserts exit 2 with the message, so the accumulation protection and the new refusal each have a test.
16. **Hygiene and verifier gaps as tests, not as a reformat.** Trailing whitespace removed in `src`,
    `tests`, `scripts`; unused imports removed from the eight test files F8 names; the numbered
    prompt-framing comments (`# 1. ...`) in `matter.py`, `bench.py`, `benchcandidate.py` and the three
    false comments plus unencoded `open()` calls in `tests/test_bench_cli.py` (F7) replaced; `p.name
    .split('/')[-1]` (F8) removed. A stdlib checker `scripts/unused_imports.py` prints `unused_imports=N`
    (ast walk, names imported and never referenced) so the hygiene has a CHECK. N2 to N5 each get the test
    the verifier would have written (§2 W8). Rejected: adding pyflakes or ruff (a dependency for one
    number).
17. **`scripts/run.sh` appends Homebrew's bin folders to PATH.** After line 23 (`PATH="$TOOLCHAIN/venv/
    bin:$PATH"`), append `/opt/homebrew/bin` and `/usr/local/bin` when they exist (append, never prepend:
    the venv and the resolved `PY` keep priority). Every run goes through run.sh (ledger `## Project`); the
    sandbox strips brew's bin (D0.1) and so does launchd on the Studio, and `shutil.which` on the
    configured name is the honest lookup. `config.example.toml` keeps the bare names. Rejected: absolute
    tool paths in `config.example.toml` (a spelled path is a guess about the Studio) and a search list
    inside `check_ocr` (a hidden default, #R01-OC-M2 class).
18. **Lane B's intake module does not import `matter.Page`; both lanes import `stamps.py`.**
    `intake.PageRecord` is its own dataclass with the fields of §1.5; the shared convention is the `id`
    format, asserted by one test against `matter.Page(...).page_id`. The one shared piece of code,
    `src/casefile/stamps.py` (`Stamp(raw, stamp)`, `normalize`, `find`), is written and committed by the
    chair as W0 before either lane starts, with its own test, so neither lane edits it. Two page types are
    a known drift, paid for lane independence this round; stage 5 unifies them when the pipeline loads
    page stores. Rejected: W2 first and sequential (lane B would wait a whole item for a one-field change).

## §2 Work items, in build order

Every CHECK runs through `scripts/run.sh` from the checkout root (or the worktree root). Every seed is
applied, its red output recorded verbatim, the file restored byte-identical (`cmp -s`), and green confirmed
before the item counts. The orchestrator re-runs every CHECK and seed before accepting (Librarian
R01-P-1). Lane letters are §3's.

### W0 (chair, before the lanes split): `stamps.py`
- Files: new `src/casefile/stamps.py` (`@dataclass(frozen=True) class Stamp: raw: str; stamp: str`;
  `def normalize(raw: str) -> str: return re.sub(r"[ -]", "", raw).upper()`; `def find(text: str,
  pattern: str) -> list[Stamp]`: `re.finditer(r"(?<![A-Z0-9])(?:" + pattern + ")", text)`, first raw per
  normalised form, text order), new `tests/test_stamps.py`, committed on `loop/round-03` with the gate run
  first.
- Ships: `find("Stamps KMR2344 and TWP7731; not 9KMR2344, kmr2344 or KMR234; also MED 0001, MED-0001 and
  MED0001", "[A-Z]{1,8}[ -]?\d{4,}")` -> normalised `["KMR2344", "TWP7731", "MED0001"]` with the first
  `MED0001` raw `MED 0001`; `normalize("med-0001") == "MED0001"`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_stamps.py` prints `stamps_cases=5 of 5`. Seeds: (a)
  lookbehind dropped -> `9KMR2344` yields `KMR2344` -> `4 of 5`; (b) `normalize` keeps hyphens -> `3 of 5`.
- Librarian pre-flight: #R01-CX-7 and #R01-CX-8 (a pattern tested in both directions with a must-pass
  list), #R02-CX-5 (duplicates by normalised form kept once).

### W1 (lane B, first): dependencies, `pdfsmoke`, the scanned fixture and its acceptance probe
- Files: `pyproject.toml` (`dependencies = ["pypdf>=6,<7", "pillow>=13,<14"]`; markers add `"ocr: runs
  ocrmypdf and tesseract"`), `uv.lock` (the chair runs `uv add pypdf pillow` then `uv sync` with the
  sandbox off, in the main tree and in the lane B worktree; §5 R4, R7), new `src/casefile/pdfsmoke.py`
  (`text_pdf(lines: list[str], *, size=14, left=72, top=720) -> bytes`: one Letter page, Helvetica, one
  `Tj` per line, valid xref, stdlib only; `render_page(lines, stamps) -> PIL.Image` and
  `image_pdf(pages: list[PIL.Image], out_path: Path) -> None`: Pillow, mode `L`, 300 dpi, JPEG quality
  90, `creationDate=time.gmtime(0)`, `modDate=time.gmtime(0)`), new `tests/fixtures/scanned/
  make_scanned.py` (`PAGES` data with `must_contain`, `build(out_dir)`, `--check`, `--probe`), new
  `tests/fixtures/scanned/scanned.pdf`, new `tests/fixtures/scanned/scanned.json`, new
  `tests/test_pdfsmoke.py`, new `tests/test_scanned_fixture.py`.
- Ships: 6 pages as §1.9; manifest `pages[i].stamps` = `[["KMR2342"], ["KMR2343"], ["KMR2344", "TWP7731"],
  [], ["KMR2345"], ["KMR2346"]]`; `kind` = `image, image, image, blank, text, mixed`; `must_contain` as
  §1.8; `scanned.pdf` under 3 MB; `pypdf` reports `len(reader.pages) == 6`, `extract_text().strip()` empty
  for pages 1 to 4, nonempty for 5 and 6 (page 6 only the stamp); `sha256` in the manifest equals the
  committed file's; `--check` prints `bytes_equal=1` on the locked versions. Invented names only: patient
  Delphine Okafor-Brandt, DOB 09/03/1979, Harrowgate Occupational Clinic, Dr. Rafael Soto-Lindgren,
  Pinecrest Imaging, Wexley Physical Therapy; injury 02/10/2026 lifting a crate; right shoulder strain; no
  claim number, no phone number, no token with letters followed by four digits other than the stamps
  (§1.3 pattern), no dashes.
- CHECK (fixture): `scripts/run.sh pytest -q -s tests/test_pdfsmoke.py tests/test_scanned_fixture.py`
  prints `scanned pages=6 text_layer=[5, 6] sha_ok=1 size_kb=<n>` and `pdfsmoke text_ok=1 image_pages=1
  image_text_layer=0`; `scripts/run.sh python tests/fixtures/scanned/make_scanned.py --check` prints
  `check bytes_equal=1 content_equal=1` and exits 0. Seeds: (a) flip one byte of `scanned.pdf` in a temp
  copy used by the test -> `sha_ok=0`, `1 failed`; (b) in `pdfsmoke.text_pdf`, drop the `BT`/`ET`
  operators -> `text_ok=0`; (c) change one word in `PAGES` and run `--check` against the committed PDF ->
  `content_equal=0`, exit 1 naming the page.
- CHECK (acceptance probe): `scripts/run.sh python tests/fixtures/scanned/make_scanned.py --probe` runs
  intake's exact ocrmypdf arguments (resolved paths, `TMPDIR` under the probe's temp folder) on
  `scanned.pdf`, extracts every page with pypdf, and prints one line per page `probe page=<n> ratio=<0.xxx>
  must_ok=<k> of <m> stamps=<found> want=<manifest>` and a last line `scanned_probe pages=6 stamps_exact=6
  of 6 must_ok=5 of 5 min_ratio=<0.xxx> text_layer=[5, 6] sidecar_segments=6 skipped=0 verdict=PASS`, and
  **exits 1 on any failed condition** (wrong stamps, a `must_contain` miss, `min_ratio` under 0.95, page 4
  not empty, segments not 6, any `[skipped page]`, no output) with `verdict=FAIL` (Codex 17; ledger line
  19). If stamps are misread, the builder changes glyph size or stamp digits in `PAGES` and regenerates;
  if `min_ratio` is under 0.95 the builder stops and reports the per-page lines (chair call). The threshold
  never moves. Seeds: (a) in the probe, compare against `PAGES` with one stamp changed to `KMR2348` ->
  `stamps_exact=5 of 6`, exit 1; (b) run the probe with `--tesseract-timeout 0` added -> `skipped=6`,
  `verdict=FAIL`, exit 1 (this also measures D0.14's marker on the real fixture).
- Librarian pre-flight: #R01-CX-2 (no image or Word file anywhere but `tests/fixtures/`), #R01-CX-9
  (the probe measures OCR, versions are not evidence), #R01-CX-11 (the probe's exit code carries the
  verdict), #R02-CX-7 (sidecar read as UTF-8 with the error surfaced), #R02-P-1 (gate before the commit:
  the generator and manifest are prose-scanned).

### W2 (lane A): `Page.stamps`, loader fixes R3-6, duplicate matter numbers
- Files: `src/casefile/matter.py` (`Page` :18-27 -> `binder, number, text, stamps`; `Matter.page` :36-41
  with `stamps.normalize(cite)`; `load` :69-73 distinct binders, :77 and :97 dotfile filter, :101-137
  validate names first then read, build `Page(binder, index, body, (stamps.normalize(stamp),))`),
  `src/casefile/benchrun.py:30` (`" ".join(page.stamps)`), `src/casefile/benchkey.py:78-81, 120-123`
  (cites normalised before `matter.page`; stored normalised), `benchscore.py:73, 81, 90-91, 98` (cite
  comparisons and flag cite sets on normalised stamps), `src/casefile/bench.py:65-73` (seen numbers, exit
  2), `tests/test_fixture_matter.py:19`, `tests/test_fakemodel_bench.py:14`, `tests/test_matter.py` (new
  cases), `tests/test_bench_discovery.py` (duplicate numbers case), `tests/test_bench_multi.py:22-23`
  (`b` renumbered `9001.002`, plus the equal-numbers case; Codex 10), `tests/test_benchscore_cite.py`
  (a candidate cite `MED-0001` matching page `MED0001` scores `found`), `src/casefile/benchkey.py:75, 117,
  126` (strip).
- Ships: `matter_pages=3 refusals=15 of 15` (12 today plus distinct binders, names-first message on a stray
  file, whitespace-only text in benchkey counted in its own test), `dotfiles_ignored=2` (a `.DS_Store` in
  `records/` and one in a binder folder both load), `duplicate_numbers_exit=2`, `cite_spellings=3 of 3`
  (`MED0001`, `MED 0001`, `MED-0001` each match the page).
- CHECK: `scripts/run.sh pytest -q -s tests/test_matter.py tests/test_fixture_matter.py
  tests/test_bench_discovery.py tests/test_bench_multi.py tests/test_benchkey.py
  tests/test_benchscore_cite.py` prints `matter_pages=3 refusals=15 of 15 dotfiles_ignored=2
  duplicate_numbers_exit=2 cite_spellings=3 of 3 fixture_pages=14 binders=3` and passes. Seeds, each alone:
  (a) matter.py dotfile filter dropped -> `dotfiles_ignored=0`; (b) distinct-binders check dropped ->
  `refusals=14 of 15` (the message becomes `duplicate Bates stamp`, F4's false report); (c) bench.py seen
  set dropped -> `duplicate_numbers_exit=1` and the equal-numbers case red; (d) `benchkey` strip dropped
  -> `1 failed` in test_benchkey; (e) `Matter.page` compares the raw cite -> `cite_spellings=1 of 3`.
- Librarian pre-flight: #R02-CX-5 (a loader refuses collisions), #R02-CX-7 (encoding named), #R01-OC-M2
  (the dotfile rule is explicit, not a default parameter), #R01-OC-M8 (the fix matches D25 as amended in
  §6, nothing wider).

### W3 (lane A): model client carried items, bench exit 2 and `model=` on the line (R3-3, R3-5)
- Files: `src/casefile/model.py:8-13` (`ModelError.__init__(message, raw=None, *, received=False)`),
  `:43-72` (`received` flag set after `open`; `except http.client.HTTPException` beside `OSError`;
  `IncompleteRead.partial` as raw), `src/casefile/benchrun.py:46-50` (`reply_received: bool`, no
  default), `:56` (`_fail` passes `True`), `:68-73` (`exc.received`; a received error with `raw=None`
  stores a `failed` row with `""`), `:95` (`True`), `src/casefile/bench.py:95-103, 110` (exit 2 branch;
  `s.line(matter.number, model)`), `src/casefile/benchscore.py:43-47` (`line(self, matter_number,
  model)`), tests: `tests/test_model.py` (no-stream HTTPError row; `received` False on `open` raising
  `ConnectionRefusedError`; True on a response whose `read()` raises `socket.timeout`; `IncompleteRead
  (b"par")` -> `ModelError` with `raw == "par"`, `received` True), `tests/test_benchrun.py` (empty-body
  302 row; read-timeout row `""`; `reply_received` both ways), `tests/test_bench_cli.py`,
  `tests/test_bench_detail.py`, `tests/test_bench_discovery.py`, `tests/test_bench_multi.py`,
  `tests/test_benchscore.py`, `tests/test_benchscore_cite.py:31` (Codex 11), `tests/test_stage2_exit.py:
  19-20` (new line text with `model=`), new test `test_bench_no_reply_exit2` (runner mode, host
  `http://127.0.0.1:9`) beside a received-404 test that must stay exit 1.
- Ships: `no_stream_row=1` (an `HTTPError(url, 503, "x", {}, None)` from a stub transport gives one
  `failed` row with `raw_answer == ""`; code unchanged, Codex 8), `empty_302_row=1`, `read_timeout_row=1`
  (`received=True`, row `""`, exit 1), `incomplete_read_row=1` (`raw == "par"`), `no_reply_exit=2` with
  stderr `bench: cannot run: no reply from the model server at http://127.0.0.1:9: <urlopen error ...>`,
  `received_404_exit=1`, candidate lines begin `bench 9001.001 model=candidate found=`, the stand-in line
  begins `bench 9001.001 model=qwen3.8:27b found=`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_model.py tests/test_benchrun.py tests/test_bench_cli.py`
  prints `no_stream_row=1 empty_302_row=1 read_timeout_row=1 incomplete_read_row=1 no_reply_exit=2
  received_404_exit=1` and passes; `scripts/run.sh casefile bench --config config.example.toml --matters
  tests/fixtures/matters --candidate tests/fixtures/bench/flawed.json | head -1` starts with `bench 9001.001
  model=candidate `. Seeds, each alone: (a) `received = True` set before `open` instead of after ->
  `no_reply_exit=1`; (b) benchrun.py:69 `is not None` -> truthiness -> `empty_302_row=0`; (c) bench.py
  exit 2 branch returns 1 -> `no_reply_exit=1`; (d) `model=` dropped from `Score.line` -> `test_bench_cli`
  red on the first line; (e) `HTTPException` dropped from the except -> `incomplete_read_row` test red
  with the traceback; (f) `reply_received=False` at benchrun.py:56 -> `received_404_exit=2`, red.
- Librarian pre-flight: #R02-V-F1 (every reply path stores and has a test), #R01-V-B2 (the new exit branch
  has its own test), #R01-CX-11 (exit code asserted, not only the text), #R01-CX-10 and #R02-CH-1 (the
  no-reply test and the received-404 test sit side by side so each guard is probed alone).

### W4 (lane A): key completeness (R3-4, Q36)
- Files: `tests/fixtures/matters/9001.001/key.json` (G7 gap MED0003 and G8 gap MED0008 appended after G6;
  abouts of G3, G5, G6 widened as §1.13), `tests/fixtures/matters/9001.001/ideal.json` and
  `tests/fixtures/bench/flawed.json` (the two flags appended), `tests/test_fixture_matter.py:35-37`
  (`(29, 8, 14)`, ids `G1..G8`), the exact-line tests listed in W3 (`flags=7 of 8`, `flags=8 of 8`),
  `tests/test_bench_detail.py` (detail lines unchanged: `flags_missed: G3`).
- Ships: flawed -> exit 1, `bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2
  flags=7 of 8 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14` then the same six detail lines as
  today; ideal -> exit 0, `bench 9001.001 model=candidate found=29 of 29 missed=0 invented=0 extra=2
  flags=8 of 8 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14`; `key_facts=29 flags=8 pages=14`;
  every new `about` passes the firm rules (`findings == []` in `test_key_loads`).
- CHECK: the two bench commands above print those lines and exit codes; `scripts/run.sh pytest -q -s
  tests/test_fixture_matter.py` prints `key_facts=29 flags=8 pages=14`. Seeds: (a) delete G7 from key.json
  -> ideal exits 1 with `flags_extra=1`; (b) change G8's cite to `MED0004` -> this seed must stay green,
  which shows that the loader cannot judge a gap's page (record it as the known D25 limit, not a finding);
  (c) one character changed in G6's about to the word `IME` -> `test_key_loads` red (`findings`
  nonempty).
- Librarian pre-flight: #R02-OC-H1 (every flag read against its pages before it is keyed; the builder
  quotes the line numbers in its report), #R02-CX-5 (no two flags with one kind and cite set), #R01-OC-H2
  (no DME or IME form in any about).

### W5 (lane B): config keys, `intake.py`, `casefile intake`
- Files: `src/casefile/config.py` (`DEFAULTS["ocr"]`, `KNOWN_KEYS["ocr"]`, `OCR` dataclass, int typing at
  :98 for `timeout_s` under `[ocr]`, compile check), `config.example.toml:16-18` (two new lines with
  comments), new `src/casefile/intake.py` (`IntakeError`, `PageRecord` (no default on `status`),
  `page_texts(pdf_path) -> list[str]`, `run_ocr(ocr_config, src, dst, sidecar, *, workdir, timeout_s,
  runner=None) -> tool_versions` (always intake's flags; `runner` defaults to the `Popen` plus `killpg`
  function of §1.7), `sidecar_outcomes(sidecar_text, pages) -> list[str | None]` (`None` ok, `"ocr
  timeout"` for `[skipped page]`; raises on a segment mismatch or an `[OCR skipped on page(s)`
  placeholder), `intake(config, number, binder, file, *, out, err) -> int`), `src/casefile/cli.py`
  (subparser `intake`), new `tests/test_intake.py`, `tests/test_config.py` (three new cases: unknown
  `[ocr].x`, `timeout_s = 0`, `stamp_pattern = "("`; `:99` `len(lines) == 10` becomes `12`, Codex 11),
  `tests/conftest.py:46` (the `ocr` table may stay as is: defaults cover the new keys). Stamps come from
  `stamps.find` (W0); intake defines no finder of its own.
- Ships: exit branches each with a test: bad number (2), bad binder name (2), matter folder missing (2,
  nothing created), matter folder a symlink resolving into the checkout (2, nothing written there), matter
  folder a symlink to another matter (2), `records/<binder>` exists (2), `pages/<binder>` exists (2),
  `pages/<binder>.tmp` left over (2, message names it), not a PDF (2), tool not found (2), ocrmypdf exit 7
  from a stub (2, stderr tail in the message), timeout from a stub `ocrmypdf` script that spawns `sleep 60
  &` (2; after the call `kill -0` on the recorded grandchild pid fails and `work/` is gone: the group was
  killed, Codex 5), sidecar with 5 segments for 6 pages from a stub (2), sidecar holding `[OCR skipped on
  page(s) 2-3]` from a stub (2), page count mismatch from a stub output (2); a stub sidecar with `[skipped
  page]` for page 2 -> exit 1, page 2 `status="failed"`, `reason="ocr timeout"`, `  failed: scan/002 ocr
  timeout`; a born-digital one-page PDF from `pdfsmoke.text_pdf` (0, `had_text_layer=true`,
  `ocr_added=false`, `source="text"`); the scanned fixture (1, `pages=6 ok=5 empty=1 failed=0 stamps=6
  had_text=2 ocr_added=4`, work folder removed, no `.tmp` folder left, `source.pdf` sha equals
  `binder.json.sha256`, every stamp record has `raw` and `stamp`). The child's PATH starts with the
  configured tesseract's folder (asserted through the stub's recorded environment). Summary line format,
  exact: `intake <matter> <binder> pages=P ok=O empty=E failed=F stamps=S had_text=T ocr_added=A`, then
  `  empty: <id>` and `  failed: <id> <reason>` lines.
- CHECK: `scripts/run.sh pytest -q -s -m "not ocr" tests/test_intake.py tests/test_config.py` prints
  `intake_refusals=15 of 15 skipped_page_exit=1 group_killed=1 born_digital_exit=0 config_refusals=+3
  config_fields=12`; `scripts/run.sh pytest -q -s -m ocr tests/test_intake.py` prints `intake_fixture
  exit=1 pages=6 ok=5 empty=1 failed=0 stamps=6 had_text=2 ocr_added=4 work_removed=1 tmp_left=0`. Seeds,
  each alone: (a) `stamps.find` called on the last line only -> the fixture `stamps=5`; (b) `status =
  "ok"` for every page -> `empty=0`, exit 0, red; (c) `enumerate(..., start=0)` on page numbers -> the id
  test red; (d) the `finally` that removes `work/` dropped -> `work_removed=0`; (e) the mkdir of a missing
  matter folder added -> the "nothing created" test red; (f) `subprocess.run(timeout=)` in place of the
  `Popen` plus `killpg` -> `group_killed=0`; (g) the `[skipped page]` check dropped -> `skipped_page_exit=0`;
  (h) the resolved-descendant check dropped -> the symlink-into-checkout test red (a file appears under the
  checkout's temp alias).
- Librarian pre-flight: #R01-OC-M7 (never create the matter folder), #R01-V-B1b and #R01R-1 (the
  destination is judged by identity of the resolved path, through `pathguard.classify`, not by
  spelling), #R01-V-B2 and #R01-V-B3 (every exit branch has its own test; the write-failure branch too),
  #R01-CX-11 (exit codes asserted), #R01R-OC-F1 (client bytes never left in a temp folder; `work/` and
  `.tmp` removed on every path, including HUP, TERM, INT), #R01-CX-4 (the OCR process group is killed, not
  only the child), #R02-CX-7 (sidecar and JSON written and read as UTF-8), #R01-OC-M2 (`reply`-style
  defaults: `PageRecord.status` has no default), #R01-OC-M8 (the intake layout is D27 as written in §6,
  nothing wider).

### W6 (lane B): doctor OCR check for real, stage 1 exit test, run.sh PATH (R3-2)
- Files: `src/casefile/doctor.py:156-172` (`check_ocr` as §1.10), `:190-195` (`next_step` for `ocr`:
  `install ocrmypdf (brew install ocrmypdf) and rerun doctor` when a tool is missing, `check the ocrmypdf
  stderr in the reason and rerun doctor` otherwise), `:23-33` `State` gains `ocr_smoke`, `:203` `run(...,
  ocr_smoke=None)`, `tests/conftest.py:200-202` (`ocr_expected_fail` returns `False`),
  `tests/test_doctor.py:34-39` (`invoke(config, *, fake=None, lsof=None, smoke=None)` injects a passing
  fake smoke unless `smoke` is given; Codex 13), `:197-215` (rewritten: which, versions, injected smoke
  PASS and four FAIL reasons; one `@pytest.mark.ocr` test with `smoke=doctor.REAL` running the real
  tools), `tests/test_fix_cycle2.py:28-32` (the old stub reason assertion replaced by the new PASS shape
  with an injected smoke; Codex 11), `:113` (direct `doctor.run` call gains `ocr_smoke=<fake>`),
  `tests/test_fix_cycle4.py:111` (through `invoke`, no edit needed once the helper injects),
  `tests/test_stage1_exit.py:54, 87` (`timeout=60` -> `180`: the real smoke adds up to 120 s; Codex 13),
  `scripts/run.sh` (PATH append after :23).
- Ships: `doctor ocr PASS smoke=ok stamps=SMOKE7342 ocrmypdf=17.13.0 tesseract=5.5.3 ms=<n>`; stage 1 exit
  `exit=0 verdicts=8 fails=set() test_jobs=1` (both the socket test and the in-process control);
  `doctor failed=0 of 8` with the stand-in on this Mac; `PATH=/usr/bin:/bin scripts/run.sh python -c
  "import shutil; print(shutil.which('ocrmypdf'))"` prints `/opt/homebrew/bin/ocrmypdf`; `grep -c
  'doctor.run(' tests/*.py` equals the count of calls that pass `ocr_smoke=` plus the two stage 1
  subprocess runs (no unit test runs real OCR by accident).
- CHECK: `scripts/run.sh pytest -q -s tests/test_doctor.py tests/test_stage1_exit.py tests/
  test_fix_cycle2.py` prints `ocr_unit=6 of 6 ocr_real=PASS` and `exit=0 verdicts=8 fails=set()
  test_jobs=1`, and its wall time is under 25 s (three real smokes). Seeds, each alone: (a) `check_ocr`
  returns PASS when only `--version` succeeds (the old stub inverted) -> the injected-smoke FAIL tests red
  (`4 failed`); (b) the stamp assertion in `check_ocr` dropped -> a smoke stub returning text with no stamp
  passes -> `1 failed`; (c) a stub `ocrmypdf` that copies input to output and writes an empty sidecar ->
  `smoke text not read`, FAIL (Codex 16; this seed is a test, kept); (d) the "input had no text" check
  dropped -> a smoke stub fed a text page passes -> `1 failed`; (e) run.sh PATH append dropped -> the
  `which` CHECK prints `None` inside the sandbox.
- Librarian pre-flight: #R01-CX-9 and #R01-OC-H1 (the reason names what ran: smoke text and stamp, not
  versions), #R01-CX-10 (a smoke stub where only the stamp is wrong, and one where only the text is wrong,
  so the two guards do not mask each other), #R01-CX-11, #R01R-RX-2 (the interpreter that runs the guard
  runs the capture; the PATH append comes after `PY` is fixed at run.sh:9).

### W7 (lane B): stage 3 exit test
- Files: new `tests/test_stage3_exit.py` (`@pytest.mark.ocr`; `write_config(tmp_path)`, `mkdir
  matters/9002.001`, `scripts/run.sh casefile intake --matter 9002.001 --binder scan
  tests/fixtures/scanned/scanned.pdf` with `CASEFILE_CONFIG`, then reads `pages/scan/*.json` against
  `tests/fixtures/scanned/scanned.json` as §1.8; a second test asserts the 0.95 boundary with two
  constructed strings; a third asserts that a `must_contain` span with one digit changed fails its page
  while the ratio stays over 0.95).
- Ships: `stage3 exit=1 pages=6 ids_ok=6 of 6 stamps_ok=6 of 6 text_ok=6 of 6 must_ok=5 of 5 empty=1
  failed=0 min_ratio=<0.xxx>` (exit 1 is the blank page, by design §1.6; the test asserts `== 1`,
  `open_ids == ["scan/004"]` and every stamp record carries `raw` and `stamp`).
- CHECK: `scripts/run.sh pytest -q -s tests/test_stage3_exit.py` prints that line and `3 passed`. Seeds,
  each alone: (a) in the manifest copy the test reads, `KMR2343` -> `KMR2348` -> `stamps_ok=5 of 6`; (b)
  intake.py `page_texts` returns `text[: len(text) // 2]` -> `text_ok` under 6; (c) threshold constant
  `0.95` -> `0.0` -> the boundary test red; (d) `start=0` page numbering -> `ids_ok=0 of 6`; (e) in the
  manifest copy, `10 pounds` -> `40 pounds` in page 1's `must_contain` -> `must_ok=4 of 5` with
  `min_ratio` unchanged (Codex 14: the ratio alone would not have caught it).
- Librarian pre-flight: #R01-CX-11, #R02-CH-1 (boundary test), #R01-OC-M7 (the test, not intake, creates
  the matter folder), #R01-P-1 (pytest-driven run that cleans up; no server here).

### W8 (lane A): hygiene and verifier gaps (R3-7)
- Files: every `src/casefile/*.py`, `tests/*.py`, `scripts/*` with trailing whitespace (33 lines per the
  Fable review); unused imports in `tests/test_matter.py` (Path, pytest), `test_benchkey.py` (pytest),
  `test_benchcandidate.py` (pytest), `test_benchscore.py` (Path), `test_bench_cli.py` (Path, pytest),
  `test_fixture_matter.py` (Path), `test_benchrun.py` (Path, sqlite3), `test_stage2_exit.py` (Path);
  numbered comments in `matter.py`, `bench.py`, `benchcandidate.py`; F7 in `tests/test_bench_cli.py:19-26,
  48-56`; F8 `tests/test_matter.py:32`; new `scripts/unused_imports.py`; new tests: N2
  (`benchcandidate` flag `about: 7` -> `flag 1: about must be a string`), N3 (`records/xray/` unlisted ->
  `unlisted binder folder xray`), N4 (`benchkey` fact `text: 5` refused), N5 (`bench.main` with a stub
  runner returning `RunResult(EMPTY, 14, "bench.truncation: done_reason=length", reply_received=True)`
  prints `bench 9001.001 failure bench.truncation: done_reason=length` and exits 1).
- Ships: `git grep -c -E '[ \t]+$' -- 'src/*.py' 'tests/*.py' 'scripts/*'` prints nothing (0 files);
  `scripts/run.sh python scripts/unused_imports.py src tests scripts` prints `unused_imports=0`; `git grep
  -c -E '^\s*# [0-9]+\. ' -- src tests` prints nothing.
- CHECK: the three commands above plus `scripts/run.sh pytest -q -s tests/test_fix_cycle5.py` (the N2 to
  N5 tests) prints `verifier_gaps=4 of 4`. Seeds, each alone: (a) `import os` added unused to a test file
  -> `unused_imports=1`; (b) benchcandidate.py:71 `not isinstance(about, str)` -> `about is None` -> N2 red;
  (c) matter.py unlisted-folder check dropped -> N3 red; (d) benchkey.py:75 `isinstance` dropped -> N4 red;
  (e) bench.py failure print dropped -> N5 red.
- Librarian pre-flight: #R02-P-1 (gate before commit), #R01-V-B2 (each gap test fails on its own seed),
  #R01-OC-M8 (hygiene changes behaviour nowhere: the full suite count only grows).

## §3 Parallelisation map

- **W0 (chair, first, main tree)**: `src/casefile/stamps.py` and `tests/test_stamps.py` committed before
  either lane is spawned; neither lane edits them.
- **Lane A (main tree, `loop/round-03`)**: W2, W3, W4, W8 in that order (W2 before W3 because both touch
  `benchrun.py` and `bench.py`; W4 after W3 because the line text changes once). Owns `src/casefile/
  {matter,model,benchrun,bench,benchscore,benchkey,benchcandidate}.py`, `scripts/unused_imports.py`,
  `tests/{test_matter,test_model,test_benchrun,test_bench_cli,test_bench_detail,test_bench_discovery,
  test_bench_multi,test_benchscore,test_benchscore_cite,test_benchkey,test_benchcandidate,
  test_fixture_matter,test_fakemodel_bench,test_stage2_exit,test_fix_cycle5}.py`,
  `tests/fixtures/matters/**`, `tests/fixtures/bench/**`. Needs no new dependency and no OCR tool; it can
  start after W0.
- **Lane B (own worktree, branch `r3/lane-b` from the W0 tip)**: W1, W5, W6, W7 in that order. Owns
  `pyproject.toml`, `uv.lock`, `config.example.toml`, `scripts/run.sh`, `src/casefile/{config,doctor,
  intake,pdfsmoke,cli}.py`, `tests/conftest.py`, `tests/{test_config,test_doctor,test_stage1_exit,
  test_fix_cycle2,test_fix_cycle4,test_intake,test_pdfsmoke,test_scanned_fixture,test_stage3_exit}.py`,
  `tests/fixtures/scanned/**`. The tools are installed (D0.1); the chair's `uv sync` of the worktree's
  toolchain is the only gate before W1.
- **Shared files, split by function**: none this round by design. `cli.py` is lane B only (lane A's
  bench changes live in `bench.py`); `conftest.py` is lane B only (W8's unused-import pass must not touch
  it; lane A's whitespace pass skips every lane B file and the orchestrator runs the whitespace check
  again after the merge). `tests/test_stage2_exit.py` is lane A (line text) and must not be edited by
  lane B even though its `write_config` call is unchanged. `tests/test_fix_cycle2.py` is lane B (its
  doctor assertions at :28-32 and :113 change; its bench or rules content does not). `stamps.py` is W0
  and read-only for both lanes.
- **Sequential**: the chair's unsandboxed `uv add` and `uv sync` in both trees before W1's tests run
  (§5 R4, R7); the merge of `r3/lane-b` into `loop/round-03` after both lanes report; then the full
  regression set, the whitespace and unused-import checks, the gate, and the §4 baselines, all by the
  orchestrator on the merged tree. Chair-only afterwards: spec §9 rows (§6), `## Project` baselines,
  tuning entries T-11 to T-15, D25 note in spec.
- **Worktree assignment**: lane B gets `isolation: "worktree"`. Its `scripts/run.sh` resolves the
  toolchain as `~/.casefile-dev/<worktree folder name>/` (run.sh:4), a fresh venv: the chair runs
  `UV_PROJECT_ENVIRONMENT=... uv sync` there (or sets `CASEFILE_TOOLCHAIN` to a folder outside the
  checkout) before lane B's first CHECK; lane B's report states the toolchain path it used.

## §4 Test design

- Regression set after the merge (the orchestrator measures; the chair records the exact count in
  `## Project`): `scripts/run.sh pytest -q` -> `N passed` with N about 315 (270 plus W0 1, W1 4, W2 about
  9, W3 8, W5 about 22, W6 6, W7 3, W8 4; no test removed); `scripts/run.sh python -m casefile.gate` ->
  `0` (`gate privacy PASS offenders=0` with the PDF under `tests/fixtures/scanned/`; `gate prose PASS
  dashes=0 files=<n>`); wall time under 90 s (T-11; was 42 s; the real OCR runs are the stage 1 socket
  and control runs, one doctor unit test, the W5 fixture test and the stage 3 exit test: five, each 3 to 5
  s on the measured tools).
- Bench baselines change in two steps and are stated once, after W4: flawed -> exit 1, `bench 9001.001
  model=candidate found=26 of 29 missed=3 invented=2 extra=2 flags=7 of 8 flags_missed=1 flags_extra=1
  rules=1 pages_failed=0 of 14`, then `  missed: F04 F15 F24`, `  invented: MED0003 "Patient was lifting 80
  pounds."`, `  invented: MED0099 "Date of service: 03/11/2025"`, `  flags_missed: G3`, `  flags_extra:
  conflict MED0001,MED0004`, `  rules: no-dme-ime DEF0003`, `bench matters=1 imperfect=1`; ideal -> exit
  0, `bench 9001.001 model=candidate found=29 of 29 missed=0 invented=0 extra=2 flags=8 of 8
  flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14`, `bench matters=1 imperfect=0`.
- Stage 2 exit test: prints `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1` as today; its `PERFECT`
  first line becomes `bench 9001.001 model=qwen3.8:27b found=29 of 29 missed=0 invented=0 extra=2 flags=8
  of 8 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14`; `stage2-control` unchanged in shape.
- Stage 1 exit test: `exit=0 verdicts=8 fails=set() test_jobs=1` (was `exit=1 ... fails={'ocr'}`); the
  doctor on this Mac with the stand-in prints `doctor failed=0 of 8`.
- Stage 3 exit test (new, `pytest -q -s tests/test_stage3_exit.py`): `stage3 exit=1 pages=6 ids_ok=6 of 6
  stamps_ok=6 of 6 text_ok=6 of 6 must_ok=5 of 5 empty=1 failed=0 min_ratio=<measured>`, `3 passed`; the
  measured minimum is recorded in the build report and the ledger, not asserted beyond the 0.95 floor.
- New standing lines for `## Project`: the W1 probe line `scanned_probe pages=6 stamps_exact=6 of 6
  must_ok=5 of 5 min_ratio=<measured> text_layer=[5, 6] sidecar_segments=6 skipped=0 verdict=PASS` (exit
  0); the intake summary `intake 9002.001 scan pages=6 ok=5 empty=1 failed=0 stamps=6 had_text=2
  ocr_added=4`; `check bytes_equal=1 content_equal=1`; the hygiene lines `unused_imports=0` and the empty
  whitespace grep.
- Verifier guidance (for the chair's prompt): seeds the builders will have used are listed in §2; fresh
  ones worth trying: a stamp regex without the lookbehind (`XKMR2344` recorded), `status` computed from
  `text` before normalisation (a page of spaces counted `ok`), `reply_received` defaulting True, the
  `ocr` marker tests run with the tools hidden from PATH (must fail, not skip), a 300 dpi page rotated 90
  degrees (expected: low ratio, red; out of scope to fix, T-13 notes `--rotate-pages`).

## §5 Risks, each with a tripwire

- R1 **Closed in the revision pass:** the tools are installed (D0.1). Residual tripwire: `scripts/run.sh
  python -c "import shutil; print(shutil.which('ocrmypdf'), shutil.which('tesseract'))"` prints two
  `/opt/homebrew/bin/...` paths after W6's PATH append; before W6, lane B prefixes `PATH=/opt/homebrew/bin:
  $PATH` on its own runs.
- R2 **Tesseract misreads a stamp (0 for O, 5 for S).** Tripwire: W1 probe `stamps_exact=6 of 6`; a lower
  number means the fixture rendering changes (size, digits), never the comparison or the pattern. Measured
  on the probe pages: `KMR2342`, `KMR2344`, `TWP7731` read exactly (D0.14).
- R3 **pypdf's text from Tesseract's layer scores under 0.95.** Tripwire: W1 probe `min_ratio` per page;
  the builder stops and reports (no fallback exists); pdfminer read the probe layer verbatim (D0.14), so the
  risk is low.
- R4 **`uv add` and `uv sync` cannot run in the sandbox** (cache outside the write allowlist, D0.10) and
  need `pypi.org` and `files.pythonhosted.org`. Tripwire: `scripts/run.sh python -c "import pypdf, PIL;
  print(pypdf.__version__, PIL.__version__)"` prints `6.21.3 13.0.0` (or the locked versions) in both
  trees before W1's tests; the chair runs the sync once with the sandbox off.
- R13 **Sandbox path spelling (D0.14).** Tesseract cannot read `/tmp/claude-501/...` inside this sandbox
  but reads `/private/tmp/claude-501/...`. Tripwire: any `ocrmypdf` exit 7 whose stderr holds `Error in
  fopenReadStream` with a `/tmp/` path; the fix is a resolved path (intake resolves every path, §1.7; a
  hand probe must use `$(cd $TMPDIR && pwd -P)`), never a sandbox change. On the Studio there is no
  sandbox.
- R14 **A per-page Tesseract timeout on a real binder.** Tripwire: `failed=<n>` with `ocr timeout` in the
  intake summary; the page stays an open item; raising `PAGE_TIMEOUT_S` is a tuning change (T-14), never
  a silent retry.
- R5 **Suite wall time.** Tripwire: `pytest -q` total over 90 s (T-11); the fix is fewer real OCR runs
  (cache the fixture intake per session), never a skip.
- R6 **`--redo-ocr` leaves page 6's scanned body unread** (mixed page). Tripwire: probe `page=6 ratio`
  under 0.95 while pages 1 to 3 are over; the builder stops and reports (a mode change is a chair call).
  Source read (D0.14): redo mode masks visible text and OCRs the rest of the image, which is the intended
  behaviour; the probe measures it on the real fixture.
- R7 **Worktree toolchain.** Tripwire: lane B's first `scripts/run.sh pytest -q tests/test_pdfsmoke.py`
  exits 95 or fails on `ModuleNotFoundError: pypdf`; the fix is the chair's sync of that toolchain.
- R8 **Client bytes in the shared TMPDIR.** Tripwire: `work_removed=1` in W5's fixture test and
  `ls "$TMPDIR" | grep -c ocrmypdf` unchanged across a run.
- R9 **Ghostscript cannot render Helvetica on the smoke page** (fonts missing from the brew install).
  Tripwire: `doctor ocr FAIL ocrmypdf exit=...` with `gs` in the stderr tail; the doctor reason must show
  it; the fix is the install, not the check.
- R10 **The line-format change leaves an old string somewhere.** Tripwire: after W4, `git grep -c -E
  'bench 9001.001 found=' -- tests src docs/spec.md` prints nothing.
- R11 **Pillow's bundled font differs by version**, so a regenerated PDF differs in bytes. Tripwire: the
  sha test is against the committed file; `make_scanned.py --check` compares structure only; a builder
  must not regenerate and commit a new PDF without rerunning the probe and updating the manifest sha in
  the same commit.
- R12 **The fixture's 300 dpi JPEG pages make a large file.** Tripwire: `size_kb` over 3072 in W1's CHECK;
  lower JPEG quality to 85 before anything else.

## §6 Contradictions and new spec rows (pending veto unless the owner already ruled)

- **D27 (new, chair, pending veto): stage 3 intake.** `casefile intake --matter N --binder B FILE`:
  ocrmypdf `--redo-ocr --output-type pdf --sidecar -l eng --tesseract-timeout 180` once per PDF, page text
  by pypdf from the output, per-page outcome from the sidecar (`[skipped page]` -> `failed`); Docling
  deferred until a stage needs layout or tables and the benchmark keeps it (D6 unchanged in intent, not
  used at stage 3); page store `pages/<binder>/<nnn>.json` and `binder.json` with the §1.5 keys, published
  by renaming `.tmp` folders, copies `source.pdf`, `ocr.pdf`, `sidecar.txt` under `records/<binder>/`; the
  matter folder must exist and resolve under the matters root by identity; a page ID is matter, binder,
  page; every stamp matching `[ocr].stamp_pattern` is recorded as raw text plus its normalised form
  (letters plus digits), none chosen (owner Q35, Q40); a page with no text after OCR is `empty`, a skipped
  page `failed`, both listed, never read; exits 0 all pages ok, 1 open pages listed, 2 cannot run; no run
  log row until the stage 5 job runner (schema v2); ocrmypdf runs in its own process group under the
  matter folder with `[ocr].timeout_s` (default 3600), killed as a group on timeout or interrupt;
  `scripts/run.sh` appends `/opt/homebrew/bin` and `/usr/local/bin` to PATH when present; Pillow and pypdf
  are runtime dependencies (the doctor's smoke page is rendered image-only).
- **D25 amended (chair, pending veto):** old "the Bates stamp alone on the last line"; new "the authored
  stamp alone on the last line, loaded as the page's only stamp (`Page.stamps`, normalised); intake pages
  (D27) may carry several; a cite matches a page when its normalised form (letters plus digits, owner Q40)
  is one of that page's stamps; entries named with a leading
  `.` under `records/` and in binder folders are ignored; `binders` must be distinct; two roots with one
  matter number are refused (exit 2)". Old line format `bench <number> found=...`; new `bench <number>
  model=<tag> found=...` with `model=candidate` in `--candidate` mode (owner Q34 Q27). Old "a model failure
  ... is a scored run with pages_failed = pages_in and exit 1"; new "a received bad reply is scored so
  (exit 1); no reply from the server at all is exit 2, cannot run" (owner Q34 Q26). Why: Q35, Q34, F3, F4,
  OR-8.
- **D19 amended (chair, pending veto):** old "OCR FAIL until stage 3 (owner Q11)"; new "OCR passes only
  when both tools are found and a generated image-only smoke page (no text layer before) is OCR'd through
  the intake path with intake's flags, its text read and its stamp `SMOKE 7342` found and normalised to
  `SMOKE7342`; the reason names the smoke result and the tool versions" (owner Q39).
- **D21 amended (chair, pending veto):** old "an empty answer is an error"; add "`ModelError.received`
  says whether a status line arrived; `http.client.HTTPException` is a `ModelError` (partial body kept as
  `raw` for `IncompleteRead`); a received error with no body is stored as a `failed` row with an empty
  body". Why: Codex 9; D25 exit 2 (Q26) needs a true "no reply" signal.
- **Spec §3 step 2 wording (chair proposes the edit at close):** old "every page gets an ID (matter,
  binder, page, Bates if stamped)"; new "every page gets an ID (matter, binder, page) and the list of
  every Bates stamp found on it; hearing prep asks which stamp to cite" (owner Q35).
- **Spec §5 row "Intake and OCR" (chair proposes at close):** old "Docling (layout, tables), ocrmypdf and
  Tesseract"; new "ocrmypdf and Tesseract, page text by pypdf (stage 3, D27); Docling for layout and
  tables when a stage needs them, kept only if the benchmark says so".
- **Q36 applied (owner ruling, pending veto as written):** the key grows to 8 flags (§1.13); facts stay 29;
  the MED0006/DEF0002 degeneration conflict waits for owner question 37. Not a contradiction, recorded
  here because it changes every exact bench number.
- **T-6 superseded by T-11:** the suite budget moves from 60 s to 90 s because five real OCR runs are
  the stage's exit evidence.
- No owner ruling is overridden. Q11's "no brew" is superseded by Q39 for OCR only; this brief adds no
  other brew install.

## §6b Privacy

Every fixture this round adds is invented: matter `9002.001`, binder `scan`, the six pages' patient
Delphine Okafor-Brandt, clinic Harrowgate Occupational Clinic, Dr. Rafael Soto-Lindgren, Pinecrest Imaging,
Wexley Physical Therapy, the dates in February and March 2026, stamps `KMR2342` to `KMR2346` and
`TWP7731`; the smoke line `CASEFILE OCR SMOKE 7342`; the two new key flags G7 and G8 restate lines
already on the invented 9001.001 pages. The PDF is generated from that text by a committed script; no
scan, photo or real document is read, copied or opened. The revision pass's probe PDF was three invented
pages rendered in `$TMPDIR` and is not part of the repo. Nothing under `Cases/` or `Bench/` is touched;
the intake tests write only under pytest's temp folders, and ocrmypdf's temp files stay under the matter
folder (§1.7). The one PDF lives under `tests/fixtures/scanned/`, the only place `.gitignore:52` and
`privacy.py:37` admit one.

## §7 Questions only the owner can answer

Questions 31 to 36 (first draft) were answered by the owner on 2026-10-27 (ledger Q40): 31 same stamp,
raw plus normalised form kept; 32 listed, exit 1; 33 typed binder name; 34 re-intake refused; 35 every
match recorded and shown; 36 English only. The revision pass adds one, appended to
`docs/loop/questions-for-owner.md` under "## Held 2026-10-27 (round 3 brief revision)": 37 whether the
report's "L4-L5 disc changes are described as degenerative" (DEF0002:32) against the MRI's "4 mm
posterior central disc protrusion" at L4-L5 (MED0006:25) is a conflict you would flag, given the MRI also
notes "mild degenerative change" at the lower levels (MED0006:23). Interim: not keyed.

Tuning values (not owner questions; the chair appends to `docs/loop/tuning-questions.md`): T-11 suite
budget 90 s; T-12 OCR text ratio floor 0.95 plus exact `must_contain` spans; T-13 ocrmypdf flags
`--redo-ocr --output-type pdf -l eng`, no `--deskew`, `--clean` or `--rotate-pages` until a real binder
shows the need; T-14 `[ocr].timeout_s` 3600, `PAGE_TIMEOUT_S` 180 (`--tesseract-timeout`) and the doctor
smoke timeout 120 s; T-15 fixture rendering 300 dpi, body 44 px, stamps 60 px, JPEG quality 90, fixed
PDF dates.

## §8 Codex dispositions (revision pass, 2026-10-27)

| # | Disposition | Evidence or change |
|---|---|---|
| 1 | ACCEPTED | Owner Q40 (LEDGER.md:143). §1.2 stamps are `{raw, stamp}`; W0 `stamps.py` with `normalize` and `find`; W2 normalises every bench cite (`Matter.page`, benchkey, benchscore); §6 D25 and D27 reworded; the W5 and W7 lines check `raw` and `stamp`. |
| 2 | ACCEPTED | Measured: `re.findall` with the lookbehind on `XKMR2344` and `KMR23441` returns both whole tokens (they are valid Q21 stamps). §1.3 drops the trailing lookahead and corrects the examples (`9KMR2344`, `kmr2344`, `KMR234` yield nothing); W0 and W5 cases rewritten. |
| 3 | ACCEPTED | Measured: `--tesseract-timeout 0` -> exit 0, sidecar `[skipped page]` per page (D0.14); `tesseract.py:402-407`. §1.1 and §1.5: `status: "failed"`, `reason: "ocr timeout"`, `--tesseract-timeout 180`, sidecar segments must equal pages; W5 tests and seed (g); W1 probe counts `skipped`; §5 R14. |
| 4 | ACCEPTED | `_pipeline.py:787-791` masks visible text in redo mode; `:1543-1565` compresses skipped ranges into one placeholder. The sidecar fallback is withdrawn (§1.1); the sidecar is read for outcomes only; `[OCR skipped on page(s)` is exit 2; `source` values unchanged. |
| 5 | ACCEPTED | `subprocess.run` kills only the direct child. §1.7: `Popen(start_new_session=True)`, `communicate(timeout)`, `os.killpg` on timeout, HUP/TERM/INT handlers; W5 lifecycle test with a stub that spawns `sleep 60 &` (`group_killed=1`), seed (f). |
| 6 | ACCEPTED | `matter.py:89-94` reads binders under `records/`. §1.4 refuses an existing `records/<binder>` or `pages/<binder>` or either `.tmp`; §1.5 atomic publish by renaming `.tmp` folders; cleanup removes only the `.tmp` folders; W5 tests. |
| 7 | ACCEPTED | `config.py:139-146` guards the root only. §1.4: `pathguard.classify` must say `outside` for the matter folder and its resolved path must descend from the resolved root; W5 symlink tests and seed (h); pre-flight #R01-V-B1b. |
| 8 | REJECTED as a code change, ACCEPTED as a test | Measured on the venv's Python 3.12.13: `HTTPError("http://x", 503, "x", {}, None).read()` -> `b''` (`fp` is `BytesIO`). `model.py:56` is correct; D0.6 and §1.14 corrected; W3 ships the test only and seed (a) is replaced. |
| 9 | ACCEPTED | `model.py:49` reads the status, `:54` the body, `:61` catches `OSError` with `raw=None`; measured: `IncompleteRead` is not an `OSError`. §1.12: `ModelError.received` set after `open`; `HTTPException` caught; `IncompleteRead.partial` kept; received-with-no-body stores `""`; D21 amended (§6); W3 tests and seeds (a), (e). |
| 10 | ACCEPTED | `tests/test_bench_multi.py:22-23` copies one matter into `a` and `b`. §1.15 and W2: `b` renumbered `9001.002`, scenario kept; an equal-numbers case asserts exit 2. |
| 11 | ACCEPTED | `test_benchscore_cite.py:31` one-argument `line`; `test_config.py:99` `len(lines) == 10`; `test_fix_cycle2.py:28-32` old stub reason. Added to W3, W5, W6 file lists with the new values (`12`; new PASS shape). |
| 12 | ACCEPTED | `benchrun.py:56` and `:95` build `RunResult` positionally. §1.12 and W3: `reply_received` has no default and is set explicitly at all three sites; seed (f) proves the `_fail` site. |
| 13 | ACCEPTED | `test_doctor.py:34-39` `invoke` has no OCR injection; callers at `test_fix_cycle2.py:106, 108, 113, 120, 158, 164`, `test_fix_cycle4.py:111`; `test_stage1_exit.py:54, 87` `timeout=60`. §1.10 and W6: `invoke` injects a passing fake by default, `doctor.run` direct call gets `ocr_smoke=`, timeouts `180`, a grep CHECK counts the calls; §4 names the five real runs. |
| 14 | ACCEPTED | Measured: one digit plus one dropped "no" in a 120-character line scores `0.98`. §1.8 adds `must_contain` spans per page (exact after normalisation); manifest carries them; W1 probe prints `must_ok`; W7 seed (e) flips `10 pounds` to `40 pounds`. |
| 15 | ACCEPTED | Measured: Pillow 13.0.0 writes byte-identical PDFs with fixed `creationDate` and `modDate` and the same basename (`/Title`); `PdfImagePlugin.py:217-218` defaults to `time.gmtime()`. §1.9: fixed dates, `--check` compares bytes then per-page pixel sha and text, exits 1 on a content difference; W1 seed (c). |
| 16 | ACCEPTED | `doctor.py:156-172` has no smoke; the first draft's vector text input could be passed by a copying stub. §1.10: image-only smoke page rendered by Pillow (now a runtime dependency), intake's own flags, "input had no text" asserted; W6 seeds (c) copy stub and (d). |
| 17 | ACCEPTED | LEDGER.md:19 requires a nonzero exit on FAIL. W1 probe prints `verdict=PASS` or `FAIL` and exits 1 on any failed condition; seeds (a) and (b) assert exit 1. |
| 18 | OWNER (question 37); interim ACCEPTED | `medical/006.txt:23` "mild degenerative change noted at the lower vertebral levels" and `:25` the L4-L5 protrusion; `defense-report/002.txt:32`. The MRI does not exclude degeneration at L4-L5, so G7 was an inference; withdrawn (§1.13), key at 8 flags, every exact number updated (W4, §4). |

Counts: accepted 16, rejected 1 (as a code change; its test stays), owner 1. Three insisted-on changes:
(1) per-page outcomes, process group, destination guard, atomic publish: §1.1, §1.4 to §1.7, W5; (2)
image-only smoke, byte-stable fixture, `must_contain` seeds, probe exit codes: §1.8 to §1.10, W1, W6, W7;
(3) Q40 reconciled, HTTPError premise withdrawn, regression call graph repaired: §1.2, §1.3, §1.12, §1.14,
D0.15, W0, W2, W3, W6.

## §9 Chair rulings (2026-10-27, before any code)

- §1 decisions 1 to 12 and 14 to 18: ACCEPTED as written.
- §1.13: ACCEPTED with one change from the owner's answer to question 37 (ledger Q41): "Where records
  conflict, especially between defense examinations and our records, those need to be flagged." Add G9
  conflict MED0006,DEF0002, about: the report calls the L4-L5 disc changes degenerative (DEF0002:32) while
  the MRI reports a 4 mm posterior central disc protrusion at L4-L5 (MED0006:25). Both `ideal.json` and
  `flawed.json` gain G9, so the flawed candidate still misses exactly G3. Nine flags. Every baseline in §4
  moves: flawed `flags=8 of 9`, ideal and stage 2 `flags=9 of 9`.
- W0 (`stamps.py`, `tests/test_stamps.py`) is written by a Sonnet builder in the main tree and committed by
  the orchestrator before the lanes split (Sonnet writes all code, Q30), not by the chair.
- §6 rows D27, D25, D19 and D21 amendments: entered in spec §9 by the chair now, pending veto. §3 and §5
  wording and tuning entries T-11 to T-15: at close.
- Codex dispositions §8: accepted as Fable recorded them (16 accepted, 1 rejected with measured evidence, 1
  owner, now answered).
