# Round 2 build brief: stage 2 benchmark and invented test matter (plus VF-1, VF-2)

Branch `loop/round-02` at `b167fbd` (working tree: the chair's uncommitted `.workflow/LEDGER.md` edit,
leave it). Scope: ledger R2-1 (VF-1), R2-2 (VF-2), R2-3 (spec §7 stage 2: the invented test matter, its
answer key, `casefile bench` scoring a run against the key on the stand-in model server), R2-4
(regression baselines). Stages 3 and later (OCR, gates, memo) are not built; the bench is designed so
they plug in (§1.3, §1.5). Builder: `gemma4:e4b-it-qat` through Ollama, one task at a time, driven by the
Opus orchestrator (owner Q28); Codex gpt-6.1-sol reviews the plan and the code; a Fable code review sits
between 8a and 8b; Sonnet 5.5 is the fallback after three failed attempts plus one re-split, logged as a
deviation. The chair re-runs every CHECK and seed before accepting (Librarian R01-P-1). Privacy: every
page, name, date, number and Bates stamp below is invented (§6b); no PDF, Word file or image is added.

Measured on the tip 2026-10-26 (this architect, inside the sandbox): `scripts/run.sh pytest -q` ->
`233 passed in 41.80s`; `scripts/run.sh python -m casefile.gate` -> rows pytest `exit=0`, privacy
`offenders=0 scanned=254`, rules_selftest `misses=0 false_hits=0`, playbook `pb-00be6eb62752`, prose
`dashes=0 files=77`, prints `0`; `scripts/run.sh casefile bench --matters tests/fixtures/matters` ->
`invalid choice: 'bench' (choose from version, doctor, playbook, config)`.

## §0 Drift (premises verified in the code, not in a report)

- D0.1 No `bench` command exists: `src/casefile/cli.py:14-27` registers `version`, `doctor`, `playbook`,
  `config` only; the dispatch is the `if/elif` chain at `cli.py:29-47`. The ledger's `## Project`
  (LEDGER.md:15-16) names `casefile bench --matters tests/fixtures/matters` and `casefile demo
  tests/fixtures/matters/<matter>`; `demo` is a stage 5 command (it needs intake and the memo) and is not
  built this round. The bench command line in the ledger is kept as written.
- D0.2 `tests/fixtures/` holds only `playbook/` (three TOML files: `bad-date.toml`,
  `malformed-missing-why.toml`, `unmarked.toml`); there is no `matters/` folder and no page text anywhere.
  `.gitignore:52` un-ignores `tests/fixtures/**`; `src/casefile/privacy.py:37` exempts paths starting
  `tests/fixtures/` from the forbidden-suffix scan only (a `Cases/` or `Bench/` first component is still
  refused, privacy.py:35). Text, JSON and TOML fixtures need no exemption.
- D0.3 VF-1 holds on the tip: `CASEFILE_TOOLCHAIN=$'<checkout>/q\npathguard outside z' scripts/run.sh
  true` -> stderr `run.sh: toolchain <checkout>/q` then `pathguard outside z/legal-harness is inside the
  checkout ...; exit 95`, exit `95`. The join is `src/casefile/pathguard.py:55`:
  `print("pathguard", verdict, " ".join(str(detail).split("\n")))`; run.sh reads the last line only,
  `scripts/run.sh:13` `case "${verdict##*$'\n'}" in`. No test covers a newline in a judged path (grep
  `\\n` in tests/test_run_sh.py and tests/test_pathguard.py: none).
- D0.4 VF-2 reproduced on the tip (venv Python `3.12.13`): `--config <loop>/x.toml` -> `RuntimeError:
  Symlink loop from '.../loopA/x.toml'` at `config.py:67` (`source = source.expanduser().resolve()`);
  `state = "~nosuchuserxyz/st"` -> `RuntimeError: Could not determine home directory.` and `state =
  "<loop>/st"` -> `RuntimeError: Symlink loop` at `config.py:145` (`paths[key] = (checkout /
  Path(paths[key]).expanduser()).resolve()`). `cli.py:45` catches `ConfigError` only, so each is a
  traceback with exit 1. `Path("~nosuchuserxyz/st").expanduser()` raises `RuntimeError` on 3.12 (measured).
  Matters already uses `os.path.expanduser` with its own refusals at `config.py:126-134`.
- D0.5 Stand-in model: `tests/fakemodel/core.py:20-32` `FakeModel(*, mode="replay", model=DEFAULT_MODEL,
  context_length=65536, recordings=None)`; `recordings` may be a path or a list of `{"name", "messages",
  "answer"}` rows (line 29-32); answers are keyed by the canonical JSON of `messages` (line 15-16, 32), so
  a recording must reproduce the request's messages byte for byte. Modes `MODES = ("replay", "truncated",
  "malformed", "forbidden", "short_context", "empty", "incomplete")` (line 11); `truncated` halves the
  content and sets `done_reason` `length` (line 107-109); `malformed` returns `'{"facts": [{"page": 1,'`
  (line 111); `forbidden` returns `"The IME found no injury; the doctor was retained by the employer."`
  (line 113). `tests/fakemodel/server.py:9` `serve(bind="127.0.0.1", port=18434, model=None)` returns a
  `ThreadingHTTPServer`; `tests/fakemodel/__main__.py:12-15` has flags `--bind`, `--port`, `--mode`,
  `--model` and no way to add recordings. `tests/fakemodel/recordings.json` holds one row (`doctor-warmup`).
- D0.6 Model client: `src/casefile/model.py:64` `def chat(self, messages, *, options=None)` returns
  `Answer(content, done_reason, prompt_eval_count, eval_count, raw)` (line 21-27, 83-84); raises
  `ModelError` on transport or HTTP errors (line 48-55), empty content (74-75), `done` not true (76-77).
  Constructor `model.py:31` `ModelClient(config, opener=None)` takes the `Model` dataclass
  (`config.model`), as `doctor.py:112` does: `ModelClient(state.config.model, state.opener)`.
- D0.7 Run log: `src/casefile/runlog.py:56-58` `start_run(self, *, job, card, card_version,
  playbook_version, model, pages_in, prompt_sha256, matter=None) -> int`; `:67-69` `record_answer(self,
  run_id, *, raw_answer, status, done_reason=None, prompt_eval_count=None, eval_count=None)` with status
  in `ok`, `failed`; `:77` `record_failure(self, run_id, gate, message)`; `:105` `open_db(path) -> RunLog`
  (creates the parent folder, line 107). `runs.matter` is a nullable column (line 13).
- D0.8 Rules and playbook: `src/casefile/rules.py:53` `def check(self, text, *, unit, stamped=True)` ->
  list of `Finding(rule_id, severity, start, end, excerpt)`; `unit` is required (#R01-OC-M2).
  `src/casefile/playbook.py:36-41` `Playbook(version, entries, rules)` where `rules` is the `Rules`
  object; `playbook.load(dir)` at `:80`. The shipped `bates_pattern` (`playbook/rules.toml:57`) fullmatches
  `MED0001`, `DEF0003`, `EMP0002` and also the range `MED0001-MED0003` (measured), so a page stamp needs
  the single-stamp form `[A-Z]{1,8}[ -]?\d{4,}` (Q21), not the cite pattern.
- D0.9 Prose gate: `src/casefile/prose.py:6-7` `PATTERNS` cover `*.md`, `docs/**/*.md`, the ledger,
  `playbook/**/*.toml`, `src/**/*.py`, `tests/**/*.py`, `scripts/*`, `config.example.toml`,
  `pyproject.toml`; fixture `.txt`, `.json` and `.toml` under `tests/fixtures/` are not scanned.
- D0.10 Doctor's run-log pattern to copy: `doctor.py:104-108` computes `card_version` as
  `hashlib.sha256(CARD_TEXT.encode()).hexdigest()[:12]` and `prompt_sha256` as the sha256 of
  `json.dumps(MESSAGES, sort_keys=True)`; `:113` calls `client.chat(MESSAGES, options={"num_ctx":
  state.config.model.num_ctx})`.
- D0.11 Test harness: `tests/conftest.py:26` `write_config(tmp_path, **overrides)` writes a complete
  invented config and returns its path (`playbook=` override points the playbook at `ROOT / "playbook"`,
  as `tests/test_stage1_exit.py:49-50` does); `tests/test_stage1_exit.py:44-59` is the socket-driven
  exit test pattern (`serve(port=0)`, thread, `scripts/run.sh casefile doctor` with `CASEFILE_CONFIG`,
  `server.shutdown()` in `finally`); `:64-78` is the in-process control with `FakeTransport`.
  `tests/test_run_sh.py:308-313` `run_toolchain(toolchain, cwd=ROOT, env=None)` runs `scripts/run.sh
  true` with `CASEFILE_TOOLCHAIN` set and returns `(result, residue_changed)`.
- D0.12 Suite wall time `41.8 s` (T-6 line is 60 s). The tests this round adds are in-process except one
  socket test and two `casefile`/`run.sh` subprocess tests; budget below 10 s more (§5 R5).
- D0.13 Tiers changed (Q28): the builder cannot read the repo. Every task in §2 therefore quotes the
  signatures it calls and the exact strings it must print or raise. Nothing in §2 relies on the builder
  discovering a file.
- D0.14 The chair's driver exists, untracked: `scripts/gemma_task.py` (211 lines after the chair's
  fail-closed fix; `--task`, `--context`, `--allow PATH`, `--function PATH::NAME`, `--feedback`,
  `--no-think`, `--num-ctx` 32768, `--num-predict` 16384; answer formats `=== FILE: <path> ===` and
  `=== FUNCTION: <path>::<name> ===`). It fails closed: the reply must have `done` true and `done_reason
  == "stop"` (gemma_task.py:165, else exit 3 and nothing written); every `.py` answer is `ast.parse`d
  and every `.json` answer `json.loads`ed before any file is written (lines 190-198, else exit 6 and
  nothing written); a FUNCTION answer is spliced by `ast` into the named def (line 103-132, exit 6 on
  failure); a path outside `--allow` is exit 4 (line 176); no block exit 2; server error exit 5. The
  driver accepts several `--allow` flags, but the protocol is one task, one allowed output path, one
  answer (§1.17): every §2 task names exactly one path. Edits to an existing file are FILE answers with
  the current file inlined as context (`tests/fakemodel/__main__.py` 34 lines, `cli.py` 55, `prose.py`
  21, `model.py` 85) or a FUNCTION answer on one def (`config.load`, config.py:65-147, 83 lines, inside
  the 120-line answer budget). The driver is loop tooling; it is scanned by the prose row (`scripts/*`)
  and holds no dashes; whether it is committed is the chair's. Gemma writes under the checkout root only
  (`os.path.join(ROOT, path)`, line 200), so a split answer's fragments go under `.workflow/scratch/gemma/`
  (ignored, .gitignore:61).

## §1 Decisions, with trade-offs

1. **Score is a tuple of counts, not a percentage.** `Score` (§2 W6) carries `key_total`, `found`,
   `invented`, `extra`, `flags_total`, `flags_found`, `flags_extra`, `rules`, `pages_in`, `pages_failed`;
   derived `missed = key_total - found`, `flags_missed = flags_total - flags_found`. One line per matter:
   `bench <number> found=F of K missed=M invented=I extra=E flags=G of H flags_missed=X flags_extra=Y
   rules=R pages_failed=P of N`. This is spec §5's "missed, invented, flags, firm rules" with the
   denominators printed (ledger `## Project` line 19: a check prints the number that fails it). Rejected:
   a single percentage; it hides which pillar failed and invites a threshold (pillar 6 compares runs).
2. **A fact is found by cite and quote, nothing fuzzier.** Key fact and candidate fact match when the
   cites are equal and `quotes.normalize(quote)` are equal (casefold, curly quotes straightened,
   whitespace collapsed). A candidate fact is **invented** when its cite is not a page of the matter or
   its quote is not found on that page (`quotes.found_in`); a candidate fact that is on the page but
   matches no key fact is **extra** (printed, never failing: a key may be incomplete, owner Q21).
   Flags match by `kind` plus equal cite sets. `rules` counts `Rules.check(text, unit="text",
   stamped=True)` findings over every candidate `text` and flag `about` (rules.py:53; the records
   themselves are never checked, Q16). Rejected: the §4 quote ladder now; it is stage 4 work, and the
   seam is one function, `quotes.found_in(quote, page_text)`, which stage 4 replaces (T-7).
   **Known limit (Codex 4):** a candidate's `text` (the one-sentence summary) is checked only by the
   firm rules, never against the quote; a summary that reverses the quote ("has reached maximum medical
   improvement" under a quote that says "has not") still scores `found`. No deterministic check of a
   summary's faithfulness exists at stage 2 (that is the §4 verification ladder, stage 4); the bench
   measures what the model copied and cited, not what it concluded. The limit is printed in D25, probed
   by the verifier (§4) so it is measured rather than hidden, and tracked as T-11 (§7).
3. **Stage 2 runs one model call per matter, and the runner is a replaceable callable.** `benchrun.run`
   sends the stage 2 card plus every page (with a `=== PAGE <binder>/<nnn> BATES <stamp> ===` header)
   in one `/api/chat` call and parses one answer with facts and flags; 14 pages are about 5 k tokens by
   the stand-in's estimate (core.py:116), far inside 65536. `bench.main` takes the runner as a parameter
   so stage 5 substitutes intake, cards, gates and merge without touching the scorer. Rejected: one call
   per page as §3 of the spec describes; per-page answers cannot carry conflicts across pages without the
   merge step, which is stage 5. The card is fixed text in `benchrun.CARD_TEXT`; cards built from the
   playbook are stage 6 (spec §7).
4. **Fixture format: one text file per page, stamp on the last line.** `tests/fixtures/matters/<number>/
   matter.toml` (`number`, `binders`), `records/<binder>/<nnn>.txt` numbered `001` upward without gaps, the
   Bates stamp alone on the last non-empty line, matching `matter.STAMP_PATTERN = r"[A-Z]{1,8}[ -]?\d{4,}"`
   (Q21; configurable at stage 3, T-10). A page without a stamp, a duplicate stamp, a gap in numbering,
   an unlisted binder folder or a page with no text above the stamp is a `MatterError` (fail closed,
   pillar 2). This is the shape intake (stage 3) will produce from a scanned PDF, so stage 3's exit test
   can target the same loader. Rejected: PDFs (none exist in the loop until stage 3, Q11; the privacy row
   would need an exemption, #R01-CX-2 class) and one file per binder with form feeds (a stamp per page is
   the unit §3 of the spec names).
5. **Answer key is JSON beside the matter, validated against the pages.** `key.json` is
   `{"facts": [{"id", "cite", "quote", "text"}], "flags": [{"id", "kind", "cites", "about"}]}`; loading it
   checks every cite is a page and every quote is found on that page, else `BenchKeyError`. The key must
   obey pillar 1 before it may judge anything. Rejected: TOML (the model answers in JSON and the stage 5
   case file is JSON; one shape for key, candidate and answer keeps the scorer to one parser).
6. **Candidate shape equals the model's answer shape.** `{"facts": [{"cite", "quote", "text"}],
   "flags": [{"kind", "cites", "about"}]}`, parsed by `benchcandidate.parse_text`. `casefile bench
   --candidate FILE` scores a file in that shape without a model call (unit tests, the flawed fixture,
   an owner's hand-made run); without `--candidate` the runner asks the model. Rejected: scoring the key
   against itself as the exit test (hollow); the exit test scores a recorded ideal answer AND a flawed
   candidate with exact, different numbers (§4).
7. **Exit codes: 0 perfect, 1 imperfect, 2 cannot run.** Perfect means `missed == 0 and invented == 0
   and flags_missed == 0 and flags_extra == 0 and rules == 0 and pages_failed == 0`; `extra` alone never
   fails. Why the asymmetry (Codex 5): an extra fact is verified against the page (its quote is there)
   and a key may be incomplete (Q21); an extra flag is verified against nothing, so a candidate that
   emits every kind for every cite pair would otherwise pass. A model failure (ModelError, truncation,
   bad token counts, non-JSON, wrong shape) is a scored run with `pages_failed = pages_in` and exit 1,
   recorded in the run log; a bad key, an unreadable matter, a bad config or playbook, or a run log that
   cannot be opened is exit 2 before any score. No threshold flag exists, so none can be lowered (ledger
   standing rule). Rejected: `--min-found` style thresholds; for the real model that is a tuning value
   (T-8) and pillar 6 asks for a comparison between runs, not a pass mark.
8. **Recordings for the bench are built from the fixture at test time, not committed.**
   `tests/fakemodel/bench.py:recordings_for(matter_root)` builds the one recording from
   `benchrun.messages(matter)` and `<matter>/ideal.json`; `python -m tests.fakemodel --bench-matter DIR`
   serves it for manual runs. Rejected: a committed `recordings.json` row for the bench; it goes stale
   the moment a page or the card changes and fails with `404 no recording` (D0.5).
9. **The ideal answer is a separate authored file.** `ideal.json` is the candidate the stand-in replays:
   the 26 key facts plus 2 extra real facts (so `extra=2` is exercised) and the 5 key flags. Perfect score
   on replay; discrimination is proven by seeds (§2) and by `tests/fixtures/bench/flawed.json`, a copy
   with six documented defects scoring exactly `found=23 of 26 missed=3 invented=2 extra=2 flags=4 of 5
   flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14`. Rejected: generating the ideal from the key
   (then candidate equals key by construction and the matcher is never exercised).
10. **`--matters` is a bench argument, not `[paths].matters`.** D13 guards the client matters folder;
    benchmark matters are invented and live in `tests/fixtures/matters/` inside the checkout by the spec's
    own words (§7 stage 2, ledger line 15). `bench.main` never reads `config.paths.matters`. Recorded as a
    clarification in D25 (§6); not a new limit (#R01-OC-M8).
11. **Every bench model call is a run-log row, and every received reply is an answer row.** `job="bench"`,
    `matter=<number>`, `card="bench.extract"`, `card_version` and `prompt_sha256` as doctor.py:104-108;
    the answer row `ok` or `failed`; failures under gates `bench.model`, `bench.truncation`,
    `bench.counts`, `bench.answer` (spec §5 run log row: "raw answer"). `ModelError` gains a `raw`
    attribute (the decoded reply when one was received, else `None`) so a reply the client refused
    (`done` false, empty content, bad counts; model.py:73-82) is still stored as a `failed` answer row
    (Codex 15). Token counts must be positive integers, as doctor.py:127 requires (Codex 3). No report
    file this round: the printed line and the run-log row are the record; comparison tooling is stage 9.
    Rejected: `state/bench/*.json` reports (one more writer to test, nothing reads it yet).
12. **Firm rules run on outputs only, and the fixture proves it.** `DEF0001` is titled "Independent
    Medical Evaluation" on the page (records are never checked, Q16); the ideal's texts say "Dr.
    Marchetti's report"; the flawed candidate's one `text` with "The IME" is the `rules=1`. (#R01-OC-H2,
    #R01-OC-H3: the must-pass side is the ideal's 26 texts and 5 abouts, which must give `rules=0`.)
13. **VF-1 is tested at both layers.** Module: `pathguard.main` with a path containing `\n` prints
    exactly one line. Wrapper: the verifier's probe through `scripts/run.sh` exits 95. Seed: drop the join
    at pathguard.py:55 -> the wrapper exits 0 (D0.3). (#R01-V-B2: an exit branch with its own test.)
14. **VF-2 wraps the two `resolve()` sites in `ConfigError`.** `config.py:67` becomes a `try` with
    `except (RuntimeError, OSError, ValueError) as exc: raise ConfigError(f"cannot resolve config path
    {source}: {exc}") from exc`; `config.py:145` likewise with `cannot resolve [paths].{key}: {exc}`.
    The venv is pinned to 3.12 (`pyproject.toml:5`), where `Path.resolve` raises `RuntimeError` on a loop
    and `Path.expanduser` on an unknown user (D0.4); `OSError` covers an `ELOOP` from a later `open` on
    an interpreter that resolves silently. Rejected: routing these through pathguard (they are not
    inside-checkout questions) and `os.path.expanduser` rewrites (test_config.py:81-82 pins `~` behaviour).
15. **Prose gate widened to fixture text.** `prose.PATTERNS` gains `tests/fixtures/**/*.txt`,
    `tests/fixtures/**/*.json`, `tests/fixtures/**/*.toml` (D20 amendment, §6): the fixture is prose and
    the project rule applies; a Gemma-written page with an em dash fails the gate, not a reader.
16. **Invented names, not placeholders.** The matter uses invented people and providers (Morgan
    Ashby-Vale, Dr. Ines Castellanos-Reyes, Dr. Priya Okonkwo-Lind, Dr. Theodore Marchetti, Rosalind
    Mbeki-Farrow, Quarry Ridge Logistics LLC, Fennimore County Hospital, Brightwater Family Medicine,
    Ridgeline Physical Therapy, Lakeshore Imaging, Lakeshore Orthopedic Associates, Northgate Medical
    Evaluations). Stage 7's anonymizer needs names to find; `[CLAIMANT]` placeholders would leave it
    nothing to test. Names are compound or hyphenated so no real person is plausibly matched (§6b).
17. **Builder protocol for Gemma (Q28).** Each §2 task is one allowed output path: one new file, one
    existing file rewritten whole with the current text inlined as context, or one function (`--function
    PATH::NAME`), at most about 120 lines of answer, with the signatures it calls, imports, exact strings
    and the test that must pass written out, and its prerequisite tasks named. Fixture pages are one task
    per page; the JSON data files (`key.json`, `ideal.json`, `flawed.json`) and `matter.toml` are Gemma
    tasks too, one file per task, with the pages or the source JSON inlined as context (Codex 10, 11;
    chair ruling). The orchestrator writes task files, runs every CHECK and seed itself, commits, holds
    the matter bible (§2 W4) and pastes it into every fixture task, and writes no app code and no fixture.
    A task that fails its test three times is re-split once (for `key.json`: per binder, §2 G25), then
    goes to Sonnet 5.5 and is logged as a deviation (Q28). Every CHECK's verdict is its exit status
    (`test "$rc" -eq 0`), never a printed word (Codex 12).
18. **R1-20 stays carried, and is reachable.** Stage 2 cites live in the structured `cite` field, but a
    candidate's `text` and `about` are free prose, and `bates-cites` (`playbook/rules.toml:56`) matches
    bracketed forms only, so a summary ending "See page 12" scores `rules=0` (Codex 16). The gap is the
    rule's, not the scorer's; it stays an open Librarian item, the verifier probes it (§4) so the number
    is on record, and the playbook change is the owner's (a rule edit is a playbook entry, D20).

## §2 Work items, in build order

Conventions for every CHECK (Codex 12): run through `scripts/run.sh`, keep the exit status in `rc`, grep
the evidence line, print `pytest_exit=$rc`, and end with `test "$rc" -eq 0` so the command itself exits
non-zero on a failing suite whatever the grep found (re-brief PR-14; `run_capture.py:109` and
`gate.py:75` carry the status, a printed word does not). The form is
`scripts/run.sh pytest -q -s FILES > "$TMPDIR/wN.log"; rc=$?; grep -E 'PATTERN' "$TMPDIR/wN.log"; echo
"pytest_exit=$rc"; test "$rc" -eq 0`; a CHECK "passes" only when its last status is 0 and the grep shows
the exact numbers. Every seed is restored byte-identical (`cmp`) before the next CHECK, and a seed is
only accepted when the CHECK's exit status became non-zero. Every test prints its evidence line with
`capsys.disabled()` before asserting, as `tests/test_config.py:34-36` does. Every task below names the
tasks it needs first ("after:"); the orchestrator runs them in §3's order and never starts a task whose
prerequisites have not passed their CHECK (Codex 9). Each task is one `--allow` path.

### W1. VF-1: the newline join at pathguard.py:55 is load-bearing (ledger R2-1)

Files: new `tests/test_pathguard_newline.py` (about 45 lines). No app code changes.
Numbers: `newline_join_exit=95 verdict_lines=1`.
CHECK: `scripts/run.sh pytest -q -s tests/test_pathguard_newline.py > "$TMPDIR/w1.log"; rc=$?; grep -E
'^newline_join_exit=' "$TMPDIR/w1.log"; echo "pytest_exit=$rc"; test "$rc" -eq 0` ->
`newline_join_exit=95 verdict_lines=1`, `pytest_exit=0`, status 0.
Measured on the tip (Codex 1): the wrapper's refusal is **two** stderr lines, because `run.sh:18` echoes
`$TOOLCHAIN` itself, newline included (`run.sh: toolchain <checkout>/q` then `pathguard outside
z/legal-harness is inside the checkout ...; exit 95`); exit 95. The one-line property belongs to the
verdict (`pathguard.py:55`), which the module test checks; the wrapper test checks the exit and that the
forged text never became the verdict.
SEED: `src/casefile/pathguard.py:55` `" ".join(str(detail).split("\n"))` -> `str(detail)`: the wrapper
exits `0` (the last verdict line reads `pathguard outside z/legal-harness`), CHECK prints
`newline_join_exit=0 verdict_lines=2`, status 1, red.
Librarian pre-flight: lines 15, 27, 30 (#R01-CX-1, #R01-CX-11, #R01-V-B2).

- **G1 (FILE `tests/test_pathguard_newline.py`; after: none).**
  - imports: `import os, subprocess; from casefile.pathguard import main; from conftest import ROOT`.
  - `test_cli_prints_one_line(tmp_path, capsys)`: `root = tmp_path / "Checkout"; root.mkdir()`; `path =
    str(root / "q\npathguard outside z")`; `code = main(["pathguard.py", str(root), path])`; read
    `out = capsys.readouterr().out`; print `f"verdict_lines={out.count(chr(10))}"` under
    `capsys.disabled()`; assert `code == 10`, `out.endswith("\n")`, `out.count("\n") == 1`, and
    `out.startswith("pathguard inside ")`.
  - `test_wrapper_refuses_forged_last_line(capsys)`: `env = dict(os.environ, CASEFILE_TOOLCHAIN=str(ROOT)
    + "/q\npathguard outside z")`; `result = subprocess.run([str(ROOT / "scripts/run.sh"), "true"],
    cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)`; `verdict_lines = sum(1 for line in
    result.stderr.splitlines() if line.startswith("pathguard "))`; print
    `f"newline_join_exit={result.returncode} verdict_lines={verdict_lines}"` under `capsys.disabled()`;
    assert `result.returncode == 95`, `result.stdout == ""`, `result.stderr.startswith("run.sh: toolchain
    ")`, `"is inside the checkout" in result.stderr`, `result.stderr.rstrip().endswith("; exit 95")`,
    `verdict_lines == 1` (the forged `pathguard outside z` line is part of the echoed path, joined onto
    the verdict line that starts `pathguard outside z/legal-harness`), and `not (ROOT / "q\npathguard
    outside z").exists()`.
  - Calls: `pathguard.main(argv)` (pathguard.py:48, `def main(argv)`, returns `EXIT[verdict]`, prints one
    line). Expected on the tip: both pass. Under the seed the second prints `newline_join_exit=0
    verdict_lines=2` (the forged line stands alone and run.sh takes it as the verdict).

### W2. VF-2: config path, state and playbook refusals are ConfigError, exit 2 (ledger R2-2)

Files: `src/casefile/config.py` function `load` (config.py:65-147; one FUNCTION task, two wrapped
lines); new `tests/test_config_resolve.py` (about 60 lines).
Numbers: `resolve_refused=4 of 4 cli_exit=2`; full suite still green.
CHECK: `scripts/run.sh pytest -q -s tests/test_config_resolve.py tests/test_config.py >
"$TMPDIR/w2.log"; rc=$?; grep -E '^resolve_refused=' "$TMPDIR/w2.log"; echo "pytest_exit=$rc"; test
"$rc" -eq 0` -> `resolve_refused=4 of 4 cli_exit=2`, `pytest_exit=0`, status 0. Also `git diff --stat
src/casefile/config.py` shows only the two wrapped sites (about 6 insertions, 2 deletions): a FUNCTION
answer that changed anything else in `load` is rejected and re-asked with that diff as feedback.
SEEDS: (a) the first wrapping's `except (RuntimeError, OSError, ValueError)` -> `except ()` -> the two
`--config` cases raise `RuntimeError`, `resolve_refused=2 of 4`, status 1; (b) the same at the
`[paths]` wrapping -> `resolve_refused=2 of 4`, status 1; (c) the cli case's `return 2` is already tested
by test_config.py:105; no new seed.
Librarian pre-flight: lines 27, 30, 33, 37 (#R01-CX-11, #R01-V-B2, #R01-OC-M8, #R01R-OC-F2).

- **G2 (FUNCTION `src/casefile/config.py::load`; after: none; context: `src/casefile/config.py` whole;
  Codex 11, Q28).** The answer is the complete `def load(path: str | Path | None = None) -> Config:`
  (config.py:65-147), copied verbatim except two sites. Site 1: the line `    source =
  source.expanduser().resolve()` (config.py:67) becomes
  ```
      try:
          source = source.expanduser().resolve()
      except (RuntimeError, OSError, ValueError) as exc:
          raise ConfigError(f"cannot resolve config path {source}: {exc}") from exc
  ```
  Site 2: the line `        paths[key] = (checkout / Path(paths[key]).expanduser()).resolve()   # D14:
  state/ lives in the checkout` (config.py:145) becomes
  ```
          try:
              paths[key] = (checkout / Path(paths[key]).expanduser()).resolve()   # D14: in the checkout
          except (RuntimeError, OSError, ValueError) as exc:
              raise ConfigError(f"cannot resolve [paths].{key}: {exc}") from exc
  ```
  Every other line of `load` is unchanged, including every existing `raise ConfigError(...)` message
  (tests/test_config.py pins them). `ConfigError` is defined at config.py:15; no new import. The driver
  splices the def by `ast` (D0.14), so the answer is one `def` with no decorators and nothing before or
  after it. The task file quotes the whole current function so the model copies rather than recalls.
- **G3 (FILE `tests/test_config_resolve.py`; after: G2).**
  - imports: `import subprocess; import pytest; from casefile.config import ConfigError, load; from
    conftest import write_config`.
  - helper `loop(tmp_path)`: `(tmp_path / "loopA").symlink_to(tmp_path / "loopB"); (tmp_path /
    "loopB").symlink_to(tmp_path / "loopA"); return tmp_path / "loopA"`.
  - `test_refusals(tmp_path, capsys)`: build the four cases as `(callable, expected_message)`:
    (1) `load(loop / "x.toml")` -> `"cannot resolve config path"`; (2) `load("~nosuchuserxyz/c.toml")` ->
    `"cannot resolve config path"`; (3) `load(write_config(tmp_path / "s", state=str(loop / "st")))` ->
    `"cannot resolve [paths].state"`; (4) `load(write_config(tmp_path / "p",
    playbook="~nosuchuserxyz/pb"))` -> `"cannot resolve [paths].playbook"`. For each, `try: fn()` ->
    append `False`; `except ConfigError as exc:` append `expected in str(exc)`; any other exception
    propagates (that is the red). Then run `["casefile", "config", "show", "--config", str(loop /
    "x.toml")]` with `subprocess.run(..., capture_output=True, text=True, timeout=30)`; print
    `f"resolve_refused={sum(results)} of 4 cli_exit={result.returncode}"` under `capsys.disabled()`;
    assert `results == [True] * 4`, `result.returncode == 2`, `result.stdout == ""`, `"ConfigError: cannot
    resolve config path" in result.stderr`.
  - Note for the orchestrator: `write_config` (conftest.py:26) takes `state=` and `playbook=` as
    top-level overrides that land in `[paths]` (conftest.py:48-59).

### W3. Quote normalisation and the matter loader

Files: new `src/casefile/quotes.py` (about 20 lines), new `src/casefile/matter.py` (about 100 lines),
new `tests/test_quotes.py` (about 35 lines), new `tests/test_matter.py` (about 110 lines).
Numbers: `quotes_ok=8 of 8`; `matter_pages=3 refusals=11 of 11`.
CHECK: `scripts/run.sh pytest -q -s tests/test_quotes.py tests/test_matter.py > "$TMPDIR/w3.log"; rc=$?;
grep -E '^(quotes_ok|matter_pages)=' "$TMPDIR/w3.log"; echo "pytest_exit=$rc"; test "$rc" -eq 0` ->
`quotes_ok=8 of 8`, `matter_pages=3 refusals=11 of 11`, `pytest_exit=0`, status 0.
SEEDS: (a) quotes.py `normalize` drop `.casefold()` -> `quotes_ok=7 of 8`, status 1; (b) matter.py
stamp check `re.fullmatch` -> `re.match` -> the `stamp-with-trailing-text` refusal passes,
`refusals=10 of 11`, status 1; (c) matter.py drop the duplicate-stamp check -> `refusals=10 of 11`;
(d) matter.py drop the `except (OSError, UnicodeDecodeError)` around the page read -> the
`page-is-a-folder` case raises `IsADirectoryError` instead of `MatterError`, the test errors, status 1.
Librarian pre-flight: lines 17, 28, 29 (#R01-CX-2, #R01-OC-M2, #R01-OC-M7: the loader creates nothing).

- **G4 (FILE `src/casefile/quotes.py`; after: none).** Module docstring: `"""Compare a quoted span with page text: exact after
  normalisation (stage 2); the stage 4 ladder replaces found_in."""`. Contents:
  ```
  CURLY = {"‘": "'", "’": "'", "“": '"', "”": '"'}
  def normalize(text: str) -> str:
      for curly, straight in CURLY.items():
          text = text.replace(curly, straight)
      return " ".join(text.split()).casefold()
  def found_in(quote: str, page_text: str) -> bool:
      quote = normalize(quote)
      return bool(quote) and quote in normalize(page_text)
  ```
  No other imports. A `TypeError` on a non-string is acceptable (callers validate shape).
- **G5 (FILE `tests/test_quotes.py`; after: G4).** Eight cases as a list of `(quote, page_text, expected)` and assertions on
  `normalize`: (1) exact substring True; (2) extra inner whitespace and a line break in the quote True;
  (3) curly double quotes in the page, straight in the quote True; (4) curly single quote True;
  (5) case differs True; (6) one word changed False; (7) empty quote False; (8) quote longer than the
  page False. Print `f"quotes_ok={passed} of 8"` then assert all. Also assert
  `normalize("  A“B”  c ") == 'a"b" c'`.
- **G6 (FILE `src/casefile/matter.py`; after: none).** Docstring `"""Load an invented benchmark matter: one text file per page, the Bates
  stamp alone on the last line (D25)."""`. Imports: `from dataclasses import dataclass; from pathlib
  import Path; import re; import tomllib`. Constants: `STAMP_PATTERN = r"[A-Z]{1,8}[ -]?\d{4,}"`,
  `NUMBER_PATTERN = r"\d{4}\.\d{3}"`, `PAGE_NAME = re.compile(r"(\d{3})\.txt\Z")`. Classes:
  ```
  class MatterError(ValueError): """A matter folder is incomplete or malformed; nothing is loaded."""
  @dataclass(frozen=True)
  class Page:
      binder: str; number: int; bates: str; text: str
      @property
      def page_id(self) -> str: return f"{self.binder}/{self.number:03d}"
  @dataclass(frozen=True)
  class Matter:
      number: str; root: Path; pages: tuple[Page, ...]
      def page(self, bates: str) -> Page | None   # first page whose bates equals the argument, else None
  def load(root) -> Matter
  ```
  `load` steps and exact messages (each `raise MatterError(...)`): `root = Path(root)`; `meta = root /
  "matter.toml"`; missing -> `f"{meta}: matter.toml not found"`; `tomllib.TOMLDecodeError` or `OSError`
  -> `f"{meta}: {exc}"`; keys not exactly `{"number", "binders"}` -> `f"{meta}: expected keys number and
  binders"`; `number` not a `str` fullmatching `NUMBER_PATTERN` -> `f"{meta}: number must look like
  9001.001"`; `binders` not a nonempty list of nonempty `str` -> `f"{meta}: binders must be a nonempty
  list of names"`; `records = root / "records"`; any entry of `records` not in `binders` ->
  `f"{records}: unlisted binder folder {name}"`; for each binder in order: `folder = records / binder`;
  not a directory -> `f"{folder}: binder folder not found"`; entries sorted by name must be exactly
  `001.txt`, `002.txt`, ... with no other entry, else `f"{folder}: expected page files 001.txt, 002.txt,
  ...; found {name}"`; read each with `path.read_text(encoding="utf-8")` inside `try ... except
  (OSError, UnicodeDecodeError) as exc: raise MatterError(f"{path}: {exc}") from exc` (Codex 14: a page
  that is a folder, unreadable, or not UTF-8 is a refusal, not a traceback); likewise every directory
  listing (`records.iterdir()`, `folder.iterdir()`) sits inside `try ... except OSError as exc: raise
  MatterError(f"{records}: {exc}") from exc` (or `{folder}`); `lines = text.rstrip().splitlines()`; last
  line stripped must `re.fullmatch(STAMP_PATTERN, ...)` else `f"{path}: last line is not a Bates
  stamp"`; the text above the stamp, stripped, must be nonempty else `f"{path}: no page text above the
  stamp"`; a stamp seen before -> `f"{path}: duplicate Bates stamp {stamp}"`. `Page.text` is the text
  above the stamp (stripped). Return `Matter(number, root, tuple(pages))`. The loader never creates a
  file or folder. Every exception that leaves `load` is a `MatterError`.
- **G7 (FILE `tests/test_matter.py`; after: G6).** Helper `make(tmp_path, pages: dict[str,
  list[tuple[str, str]]])` writes `matter.toml` (`number = "9001.001"`, `binders = [...]` in the dict's
  order) and `records/<binder>/<nnn>.txt` from `(text, stamp)` pairs, returns the root. Happy path: two
  binders, three pages; assert `len(matter.pages) == 3`, `matter.pages[0].page_id == "medical/001"`,
  `matter.page("MED0002").text` equals the written text, `matter.page("NOPE0001") is None`. Refusals,
  eleven, each `pytest.raises(MatterError, match=...)`: missing matter.toml; unknown key; bad number
  `"9001"`; empty binders; binder folder missing; numbering gap (`001.txt`, `003.txt`); stray file
  `notes.txt`; stamp with trailing text (`"MED0001 page 1"` as the last line); duplicate stamp across
  binders; page-is-a-folder (`records/medical/002.txt` created as a directory, match `"002.txt"`); page
  not UTF-8 (`002.txt` written as bytes `b"\xff\xfe text\nMED0002\n"`, match `"002.txt"`). Count the
  refusals that raised with the right message, print `f"matter_pages={len(matter.pages)}
  refusals={ok} of 11"`, assert `ok == 11`. Also assert no file was created under the root besides the
  ones written (`sorted(p.name for p in root.rglob("*") if p.is_file())` equals the written names).

### W4. The invented matter 9001.001 (fixture prose; ledger R2-3a)

Files: new `tests/fixtures/matters/9001.001/matter.toml`, `records/medical/001.txt` to `008.txt`,
`records/employer/001.txt` to `003.txt`, `records/defense-report/001.txt` to `003.txt` (14 pages, each
25 to 40 lines). Fifteen Gemma tasks, one file each (Codex 10; chair ruling). The test file that loads
the fixture is G26 (W5), written once the key exists, so this section's CHECK is a chair one-liner.
Numbers: `fixture_pages=14 binders=3`.
CHECK (chair, after G22): `scripts/run.sh python -c 'from casefile import matter; m =
matter.load("tests/fixtures/matters/9001.001"); print(f"fixture_pages={len(m.pages)}
binders={len({p.binder for p in m.pages})}")' > "$TMPDIR/w4.log"; rc=$?; cat "$TMPDIR/w4.log"; test
"$rc" -eq 0 && grep -qx 'fixture_pages=14 binders=3' "$TMPDIR/w4.log"` -> status 0. Also `grep -c
"Ashby-Vale" tests/fixtures/matters/9001.001/records/*/*.txt | grep -vc ':0$'` prints `14`, and `find
tests/fixtures/matters -type f | grep -v -E '\.(txt|json|toml)$'` prints nothing. After G43 the gate
must print `0`.
PER-PAGE CHECK (chair, after each page task; FILE is the page, LINES is a file holding that page's
verbatim sentences one per line, STAMP its stamp): `test "$(tail -1 FILE)" = STAMP && test "$(grep -c
-x -F -f LINES FILE)" -eq "$(wc -l < LINES)" && grep -q 'Ashby-Vale' FILE && ! LC_ALL=C grep -q
$'\xe2\x80[\x93\x94]' FILE && n=$(wc -l < FILE) && test "$n" -ge 25 -a "$n" -le 40` -> status 0. A
page that fails goes back to Gemma with the failing clause as feedback (three attempts, Q28).
SEED: delete the last line (the stamp) of `records/medical/004.txt` -> the CHECK prints `MatterError:
... last line is not a Bates stamp`, status 1, red (restore by cmp).
Librarian pre-flight: lines 23 to 25 (#R01-CX-7, #R01-CX-8, #R01-OC-H2, #R01-OC-H3: the record text may
say "Independent Medical Evaluation"; the ideal's texts may not).

**Matter bible** (the orchestrator pastes this whole block into every W4, W5 and W6 fixture task).
Claimant Morgan Ashby-Vale, born 1981-02-17, order picker at Quarry Ridge Logistics LLC (hired
2021-08-02). Injury Tuesday 2025-03-11 about 10:40 am, lifting a plastic tote from a floor-level pallet
to a cart; low back pain. Employer's lead on shift: Rosalind Mbeki-Farrow. Claim number QRL-2025-0418
(invented). Every page ends with its stamp alone on the last line. No em or en dashes anywhere. No real
person, firm or hospital. Dates written `MM/DD/YYYY` inside records.

| Page | Stamp | Document | Lines that must appear verbatim (the key's quotes) |
|---|---|---|---|
| medical/001 | MED0001 | Fennimore County Hospital, Emergency Department record, page 1 of 2 | `Date of service: 03/11/2025`; `Patient states he was lifting a tote he estimated at 60 pounds when he felt a sharp pain in his low back.`; `Pain 7/10 in the low back, no radiation.`; `Patient denies any prior back injury or back pain.` |
| medical/002 | MED0002 | the same ER record, page 2 of 2 | `Straight leg raise negative bilaterally.`; `Lumbar spine x-ray, three views, ordered; report to follow.`; `Diagnosis: acute lumbar strain.`; `Off work for 3 days, then return as tolerated.`; ibuprofen and cyclobenzaprine prescribed |
| medical/003 | MED0003 | Brightwater Family Medicine, Dr. Ines Castellanos-Reyes, office visit 03/14/2025 | `Patient reports a lumbar strain in 2019 after moving furniture, resolved with rest.`; `Restrictions: no lifting over 10 pounds and no repetitive bending through 04/11/2025.`; `Referred to physical therapy, two visits per week for six weeks.` |
| medical/004 | MED0004 | Ridgeline Physical Therapy, initial evaluation 03/24/2025 | `Pain 5/10 at rest, 7/10 with bending.`; `Lumbar flexion 40 degrees, extension 10 degrees.`; plan 2 visits a week for 6 weeks |
| medical/005 | MED0005 | Ridgeline Physical Therapy, progress note 04/14/2025, visit 6 of 12 | `Patient reports new numbness into the left calf since approximately 04/10/2025.`; `Recommend MRI of the lumbar spine before further progression.`; `Discharge summary to follow at visit 12.` |
| medical/006 | MED0006 | Lakeshore Imaging, MRI lumbar spine without contrast, 04/18/2025 | `L4-L5: 4 mm posterior central disc protrusion contacting the thecal sac.`; `L5-S1: mild disc desiccation without protrusion.`; `No fracture or listhesis.` |
| medical/007 | MED0007 | Lakeshore Orthopedic Associates, Dr. Priya Okonkwo-Lind, consultation 05/09/2025, page 1 of 2 | `Positive straight leg raise on the left at 45 degrees.`; `Impression: L4-L5 disc protrusion with left L5 radiculopathy.` |
| medical/008 | MED0008 | the same consultation, page 2 of 2 | `Plan: left L4-L5 transforaminal epidural steroid injection.`; `Restrictions: sedentary duty, no lifting over 15 pounds, until re-evaluation on 06/20/2025.`; `In my opinion the L4-L5 disc protrusion is causally related to the lifting injury of 03/11/2025 described by the patient, within a reasonable degree of medical probability.`; `The patient has not reached maximum medical improvement.` |
| employer/001 | EMP0001 | Quarry Ridge Logistics LLC, Employee Incident Report, 03/11/2025 | `Employee reported lifting a tote weighing approximately 40 pounds from a floor pallet.`; `Date of hire: 08/02/2021`; witness Rosalind Mbeki-Farrow; reported to supervisor the same day |
| employer/002 | EMP0002 | Job description, Order Picker | `Lift up to 50 pounds repeatedly during the shift.`; stand and walk the full shift |
| employer/003 | EMP0003 | Wage statement, 13 weeks before 03/11/2025 | `Average weekly wage: $912.40`; thirteen weekly rows (invented, each between 860 and 960 dollars) |
| defense-report/001 | DEF0001 | Northgate Medical Evaluations, "Independent Medical Evaluation" report of Dr. Theodore Marchetti, examination 06/20/2025, page 1 of 3 | records reviewed (the ER, Dr. Castellanos-Reyes, Ridgeline, the MRI, Dr. Okonkwo-Lind); `The examinee reports lifting a tote of about 60 pounds.`; `He acknowledges a 2019 episode of low back pain that resolved.` |
| defense-report/002 | DEF0002 | page 2 of 3 | `Straight leg raise negative bilaterally.`; `No objective findings of radiculopathy on today's examination.`; MRI reviewed, described as degenerative |
| defense-report/003 | DEF0003 | page 3 of 3, opinions | `The L4-L5 findings are degenerative and pre-existing, not causally related to the work incident of 03/11/2025.`; `The examinee is at maximum medical improvement as of today's examination.`; `No work restrictions are indicated.`; `No further treatment is medically necessary.` |

Planted conflicts and gaps (the key's five flags): (G1 conflict MED0001, EMP0001) tote weight 60 versus
approximately 40 pounds; (G2 conflict MED0001, MED0003) prior back history denied at the ER versus the
2019 strain; (G3 conflict MED0008, DEF0003) causation of the L4-L5 protrusion; (G4 gap MED0002) the
x-ray report ordered and not in the records; (G5 gap MED0005) the PT discharge summary not in the records.
(These flag labels G1 to G5 are key ids, not task numbers.)

**Page task template** (one task file per page; the answer is a text file, not code, and the task says
so above the driver's system rules): the bible; the page's table row; the rules: 25 to 40 lines; a
plausible header (facility, patient Morgan Ashby-Vale, date of birth 02/17/1981, date of service,
provider); every verbatim sentence of the row on its own line, character for character; ordinary
clinical or administrative prose around them (vitals, history, exam, plan; invented values only,
nothing from memory of any real case); the stamp alone on the last line; no em or en dashes; output
`=== FILE: tests/fixtures/matters/9001.001/records/<binder>/<nnn>.txt ===` then one fenced block.

- **G8 to G15 (FILE `records/medical/001.txt` to `008.txt`, one task each; after: none).** Rows
  medical/001 to medical/008.
- **G16 to G18 (FILE `records/employer/001.txt` to `003.txt`; after: none).** Rows employer/001 to
  employer/003; the wage statement is a plain-text table (thirteen `MM/DD/YYYY  $nnn.nn` rows).
- **G19 to G21 (FILE `records/defense-report/001.txt` to `003.txt`; after: none).** Rows
  defense-report/001 to 003; the report may use the phrase "Independent Medical Evaluation" in its title
  and body (it is a record, Q16).
- **G22 (FILE `tests/fixtures/matters/9001.001/matter.toml`; after: none).** Exactly:
  ```
  number = "9001.001"
  binders = ["medical", "employer", "defense-report"]
  ```
  The orchestrator reads every page before committing (§6b).

### W5. Answer key loader and the key itself (ledger R2-3b)

Files: new `src/casefile/benchkey.py` (about 90 lines), new `tests/test_benchkey.py` (about 90 lines),
new `tests/fixtures/matters/9001.001/key.json` (Gemma, G25), new `tests/test_fixture_matter.py` (about
50 lines; both fixture tests).
Numbers: `key_refusals=10 of 10`; `fixture_pages=14 binders=3`; `key_facts=26 flags=5 pages=14`.
CHECK: `scripts/run.sh pytest -q -s tests/test_benchkey.py tests/test_fixture_matter.py >
"$TMPDIR/w5.log"; rc=$?; grep -E '^(key_refusals|fixture_pages|key_facts)=' "$TMPDIR/w5.log"; echo
"pytest_exit=$rc"; test "$rc" -eq 0` -> the three lines, `pytest_exit=0`, status 0.
SEEDS: (a) benchkey.py drop the `found_in` check -> the quote-not-on-page refusal passes,
`key_refusals=9 of 10`, status 1; (b) change one character inside a `quote` in `key.json` ->
`test_key_loads` raises `BenchKeyError: ... quote not found on page`, status 1, red (restore by cmp).
Librarian pre-flight: lines 23, 28 (#R01-CX-7 must-pass list idea; #R01-OC-M2 no silent default).

- **G23 (FILE `src/casefile/benchkey.py`; after: G4, G6).** Imports: `from dataclasses import
  dataclass; import json; from pathlib import Path; from casefile.matter import Matter; from
  casefile.quotes import found_in`. Definitions:
  ```
  FLAG_KINDS = ("conflict", "gap")
  class BenchKeyError(ValueError): """The answer key is malformed or disagrees with the pages."""
  @dataclass(frozen=True)
  class Fact: id: str; cite: str; quote: str; text: str
  @dataclass(frozen=True)
  class Flag: id: str; kind: str; cites: tuple[str, ...]; about: str
  @dataclass(frozen=True)
  class Key: facts: tuple[Fact, ...]; flags: tuple[Flag, ...]
  def load(path, matter: Matter) -> Key
  ```
  Calls: `matter.page(bates) -> Page | None` (G6), `found_in(quote, page_text) -> bool` (G4).
  `load` messages (each `raise BenchKeyError(...)`): read failure (`OSError`, `UnicodeDecodeError`) or
  JSON error -> `f"{path}: {exc}"`; not an object with keys exactly `facts` and `flags` -> `f"{path}:
  expected object with keys facts and flags"`; `facts` not a nonempty list -> `f"{path}: facts must be
  a nonempty list"`; `flags` not a list -> `f"{path}: flags must be a list"`; fact `n` (1-based) not an
  object with keys exactly `id`, `cite`, `quote`, `text`, all nonempty strings -> `f"{path}: fact {n}:
  expected keys id, cite, quote, text (nonempty strings)"`; duplicate id -> `f"{path}: fact {id}:
  duplicate id"`; `matter.page(cite) is None` -> `f"{path}: fact {id}: cite {cite} is not a page of
  matter {matter.number}"`; `not found_in(quote, page.text)` -> `f"{path}: fact {id}: quote not found
  on page {cite}"`; flag `n` not an object with keys exactly `id`, `kind`, `cites`, `about` ->
  `f"{path}: flag {n}: expected keys id, kind, cites, about"`; kind not in `FLAG_KINDS` -> `f"{path}:
  flag {id}: kind must be conflict or gap"`; cites not a nonempty list of nonempty strings ->
  `f"{path}: flag {id}: cites must be a nonempty list of Bates stamps"`; a cite not a page ->
  `f"{path}: flag {id}: cite {cite} is not a page of matter {matter.number}"`; duplicate flag id
  (across flags) -> `f"{path}: flag {id}: duplicate id"`; `about` not a nonempty string -> `f"{path}:
  flag {id}: about must be a nonempty string"`. Ids of facts and flags are separate namespaces.
- **G24 (FILE `tests/test_benchkey.py`; after: G7, G23).** Build a two-page matter with
  `test_matter.make` (import it: `from test_matter import make`) and a valid key dict; `write(tmp_path,
  data) -> Path` dumps JSON. Happy path: `len(key.facts) == 2`, `len(key.flags) == 1`, a quote with
  different whitespace and curly quotes still loads. Ten refusals via `pytest.raises(BenchKeyError,
  match=...)`: not JSON; top-level keys wrong; empty facts; fact missing `text`; duplicate fact id; cite
  not a page; quote not on page; flag kind `"note"`; flag cites empty; flag cite not a page. Print
  `f"key_refusals={ok} of 10"`, assert all.
- **G25 (FILE `tests/fixtures/matters/9001.001/key.json`; after: G8 to G22; context: the 14 page files
  and the bible; Codex 11).** The answer is JSON (the driver `json.loads` it before writing, D0.14),
  one fact object per line and one flag object per line so the answer stays near 40 lines:
  `{"facts": [` ... `], "flags": [` ... `]}`. Exactly 26 facts `F01` to `F26` and 5 flags `G1` to `G5`
  from the bible, each `quote` copied character for character from the page named by `cite` (the task
  tells the model: copy, do not retype; the loader rejects any quote not on its page). The 26, in
  order: F01 `Date of service: 03/11/2025` (MED0001); F02 the 60-pound sentence (MED0001); F03 `Pain
  7/10 in the low back, no radiation.` (MED0001); F04 `Patient denies any prior back injury or back
  pain.` (MED0001); F05 `Straight leg raise negative bilaterally.` (MED0002); F06 the x-ray sentence
  (MED0002); F07 `Diagnosis: acute lumbar strain.` (MED0002); F08 the off-work line (MED0002); F09 the
  2019 strain (MED0003); F10 the restrictions (MED0003); F11 the PT referral (MED0003); F12 `Lumbar
  flexion 40 degrees, extension 10 degrees.` (MED0004); F13 the numbness (MED0005); F14 the MRI
  recommendation (MED0005); F15 `Discharge summary to follow at visit 12.` (MED0005); F16 the L4-L5
  finding (MED0006); F17 the positive SLR (MED0007); F18 the impression (MED0007); F19 the injection
  plan (MED0008); F20 the causation sentence (MED0008); F21 `The patient has not reached maximum
  medical improvement.` (MED0008); F22 the 40-pound sentence (EMP0001); F23 `Average weekly wage:
  $912.40` (EMP0003); F24 the defense causation sentence (DEF0003); F25 the defense MMI line (DEF0003);
  F26 `No work restrictions are indicated.` (DEF0003). Not in the key: MED0004's pain line, MED0006's
  second and third lines, EMP0001's hire date, EMP0002's lifting line, DEF0001's two lines, DEF0002's
  two lines, DEF0003's last line. Each `text` is one plain sentence that says no more than the quote,
  names the examiner's report as "Dr. Marchetti's report", and never uses the words DME, IME,
  "independent medical", "defense medical", hired, paid or retained (§1.12; `test_key_loads` runs the
  firm rules over every text). Flags: `{"id": "G1", "kind": "conflict", "cites": ["MED0001",
  "EMP0001"], "about": ...}` and so on for G2 (conflict MED0001, MED0003), G3 (conflict MED0008,
  DEF0003), G4 (gap, `["MED0002"]`), G5 (gap, `["MED0005"]`), `about` one sentence each. **Re-split
  (if three attempts fail):** three tasks, one per binder, each answering a complete
  `{"facts": [...], "flags": [...]}` object to `.workflow/scratch/gemma/key-medical.json` (F01 to
  F21, `flags: []`), `key-employer.json` (F22, F23, `flags: []`) and `key-defense.json` (F24 to F26 and
  the five flags), with only that binder's pages as context; the orchestrator concatenates
  mechanically: `facts` = medical then employer then defense, `flags` = the defense fragment's, written
  with `json.dump(data, f, indent=1, ensure_ascii=False)` to `key.json`. No other editing.
- **G26 (FILE `tests/test_fixture_matter.py`; after: G22, G23, G25).** `MATTER = ROOT / "tests" /
  "fixtures" / "matters" / "9001.001"`. `test_fixture_loads(capsys)`: `matter =
  casefile.matter.load(MATTER)`; print `f"fixture_pages={len(matter.pages)} binders={len({p.binder for
  p in matter.pages})}"`; assert 14 and 3, and that the stamps are exactly `MED0001..MED0008`,
  `EMP0001..EMP0003`, `DEF0001..DEF0003` in that order. `test_key_loads(capsys)`: load matter and
  `key = benchkey.load(MATTER / "key.json", matter)`; print `f"key_facts={len(key.facts)}
  flags={len(key.flags)} pages={len(matter.pages)}"`; assert `(26, 5, 14)`, fact ids are exactly `F01`
  to `F26` in order and flag ids `G1` to `G5`; and assert `rules.check(t, unit="text", stamped=True)`
  over every `text` and `about` returns `[]` (rules loaded with `casefile.rules.load(ROOT / "playbook"
  / "rules.toml")`; signature `Rules.check(self, text, *, unit, stamped=True)`, rules.py:53).

### W6. Candidate parser and scorer (ledger R2-3c)

Files: new `src/casefile/benchcandidate.py` (about 60 lines), new `src/casefile/benchscore.py` (about 85
lines), new `tests/test_benchcandidate.py` (about 60 lines), new `tests/test_benchscore.py` (about 110
lines), new `tests/fixtures/matters/9001.001/ideal.json` and `tests/fixtures/bench/flawed.json` (Gemma,
G30 and G31).
Numbers: `candidate_refusals=7 of 7`; perfect line `bench 9001.001 found=26 of 26 missed=0 invented=0
extra=2 flags=5 of 5 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14`; flawed line `bench
9001.001 found=23 of 26 missed=3 invented=2 extra=2 flags=4 of 5 flags_missed=1 flags_extra=1 rules=1
pages_failed=0 of 14`; `score_cases=11 of 11`.
CHECK: `scripts/run.sh pytest -q -s tests/test_benchcandidate.py tests/test_benchscore.py >
"$TMPDIR/w6.log"; rc=$?; grep -E '^(candidate_refusals=|score_cases=|bench 9001.001 )'
"$TMPDIR/w6.log"; echo "pytest_exit=$rc"; test "$rc" -eq 0` -> the four lines, `pytest_exit=0`,
status 0.
SEEDS: (a) benchscore.py count extra as invented (`extra += 1` -> `invented.append(...)`) -> perfect
line shows `invented=2`, status 1; (b) flags matched without `kind` (drop `kind` from the set key) ->
the kind-swap unit case passes, status 1; (c) the rules input drops the fact texts (`[f.text for f in
candidate.facts] + ` removed, only abouts checked) -> flawed line `rules=0`, status 1 (Codex 7
replaced the `unit` swap, which rules.py:61 ignores for text rules); (d) benchcandidate.py accept a
fact without `text` -> `candidate_refusals=6 of 7`, status 1; (e) drop `flags_extra == 0` from
`perfect` -> the `flags_extra=1 -> not perfect` unit case fails, status 1 (Codex 5).
Librarian pre-flight: lines 21, 23, 28 (#R01-CX-10 masking: each counter has a probe where only it is
wrong; #R01-OC-H3; #R01-OC-M2).

- **G27 (FILE `src/casefile/benchcandidate.py`; after: none).** Imports: `from dataclasses import
  dataclass; import json`. Definitions:
  ```
  FLAG_KINDS = ("conflict", "gap")
  class CandidateError(ValueError): """A run's answer is not in the candidate shape; nothing is scored."""
  @dataclass(frozen=True)
  class CandidateFact: cite: str; quote: str; text: str
  @dataclass(frozen=True)
  class CandidateFlag: kind: str; cites: tuple[str, ...]; about: str
  @dataclass(frozen=True)
  class Candidate: facts: tuple[CandidateFact, ...]; flags: tuple[CandidateFlag, ...]
  EMPTY = Candidate((), ())
  def parse(data) -> Candidate
  def parse_text(text: str) -> Candidate
  ```
  `parse` messages: not a dict with keys exactly `facts` and `flags`, both lists -> `"expected a JSON
  object with keys facts and flags"`; fact `n` not a dict with keys exactly `cite`, `quote`, `text`, all
  strings -> `f"fact {n}: expected keys cite, quote, text (strings)"`; flag `n` not a dict with keys exactly
  `kind`, `cites`, `about` -> `f"flag {n}: expected keys kind, cites, about"`; kind not in `FLAG_KINDS` ->
  `f"flag {n}: kind must be conflict or gap"`; cites not a nonempty list of strings -> `f"flag {n}: cites
  must be a nonempty list of strings"`; about not a string -> `f"flag {n}: about must be a string"`.
  `parse_text`: `json.loads` failure -> `CandidateError(f"not JSON: {exc}")`, else `parse`. Empty
  strings are allowed here (an empty quote scores as invented; shape only).
- **G28 (FILE `tests/test_benchcandidate.py`; after: G27).** Happy path from a dict and from text
  (`json.dumps`); `EMPTY` has no facts; seven refusals via `pytest.raises(CandidateError, match=...)`:
  not JSON; a list at top level; missing `flags`; fact missing `text`; fact with an extra key; flag
  kind `"note"`; flag cites `[]`. Print `f"candidate_refusals={ok} of 7"`.
- **G29 (FILE `src/casefile/benchscore.py`; after: G4, G6, G23, G27).** Imports: `from dataclasses
  import dataclass; from casefile.benchcandidate import Candidate; from casefile.benchkey import Key;
  from casefile.matter import Matter; from casefile.quotes import found_in, normalize`. Definitions:
  ```
  @dataclass(frozen=True)
  class Score:
      key_total: int; found: int; invented: int; extra: int
      flags_total: int; flags_found: int; flags_extra: int
      rules: int; pages_in: int; pages_failed: int
      missed_ids: tuple[str, ...]; invented_quotes: tuple[str, ...]; flags_missed_ids: tuple[str, ...]
      @property
      def missed(self) -> int: return self.key_total - self.found
      @property
      def flags_missed(self) -> int: return self.flags_total - self.flags_found
      @property
      def perfect(self) -> bool:
          return (self.missed == 0 and self.invented == 0 and self.flags_missed == 0
                  and self.flags_extra == 0 and self.rules == 0 and self.pages_failed == 0)
      def line(self, matter_number: str) -> str:
          return (f"bench {matter_number} found={self.found} of {self.key_total} missed={self.missed} "
                  f"invented={self.invented} extra={self.extra} flags={self.flags_found} of "
                  f"{self.flags_total} flags_missed={self.flags_missed} flags_extra={self.flags_extra} "
                  f"rules={self.rules} pages_failed={self.pages_failed} of {self.pages_in}")
  def score(key: Key, candidate: Candidate, matter: Matter, rules, pages_failed: int) -> Score
  ```
  Algorithm: `matched = set(); invented = []; extra = 0`; for each candidate fact: `page =
  matter.page(fact.cite)`; if `page is None or not found_in(fact.quote, page.text)`: append
  `fact.quote[:60]` to `invented` and continue; else find the first key fact with the same cite and
  `normalize(k.quote) == normalize(fact.quote)`; none -> `extra += 1`; else `matched.add(k.id)` (a second
  candidate matching the same key fact is neither extra nor invented). Flags: `key_sets = {(f.kind,
  frozenset(f.cites)): f.id for f in key.flags}`; `cand_sets = {(f.kind, frozenset(f.cites)) for f in
  candidate.flags}`; `flags_found = len(set(key_sets) & cand_sets)`; `flags_extra = len(cand_sets -
  set(key_sets))`. Rules: `rules_count = sum(len(rules.check(t, unit="text", stamped=True)) for t in
  [f.text for f in candidate.facts] + [f.about for f in candidate.flags])`. `missed_ids` are key fact ids
  not in `matched`, in key order; `flags_missed_ids` likewise. `pages_in = len(matter.pages)`. The
  `rules` argument is the `Rules` object (`Rules.check(self, text, *, unit, stamped=True)`, rules.py:53).
  The fact `text` is never compared with the quote (§1.2 known limit).
- **G30 (FILE `tests/fixtures/matters/9001.001/ideal.json`; after: G25; context: `key.json`).**
  Candidate shape, one object per line: every key fact in key order with the `id` key removed (cite,
  quote and text copied character for character), then two extra real facts appended: `{"cite":
  "EMP0001", "quote": "Date of hire: 08/02/2021", "text": "The incident report gives a hire date of
  08/02/2021."}` and `{"cite": "EMP0002", "quote": "Lift up to 50 pounds repeatedly during the
  shift.", "text": "The job description requires lifting up to 50 pounds repeatedly."}`; then the five
  key flags with their `id` removed (kind, cites, about copied). 28 facts, 5 flags.
- **G31 (FILE `tests/fixtures/bench/flawed.json`; after: G30; context: `ideal.json`).** A copy of
  `ideal.json` with exactly these eight edits and nothing else: (1) remove the MED0001 fact whose quote
  is `Patient denies any prior back injury or back pain.` (F04); (2) remove the MED0005 fact
  `Discharge summary to follow at visit 12.` (F15); (3) remove the DEF0003 fact that begins `The L4-L5
  findings are degenerative` (F24); (4) add `{"cite": "MED0003", "quote": "Patient was lifting 80
  pounds.", "text": "The patient was lifting 80 pounds."}` (not on the page); (5) add `{"cite":
  "MED0099", "quote": "Date of service: 03/11/2025", "text": "A date of service of 03/11/2025."}` (not
  a page); (6) change the `text` of the DEF0003 fact `No work restrictions are indicated.` to `"The IME
  found no work restrictions."`; (7) remove the flag with cites `["MED0008", "DEF0003"]` (G3); (8) add
  `{"kind": "conflict", "cites": ["MED0001", "MED0004"], "about": "Pain scores differ between the ER and
  the first therapy visit."}`. The W6 numbers follow: found 23 of 26, invented 2, extra 2 unchanged,
  flags 4 of 5, flags_extra 1, rules 1. The orchestrator diffs `flawed.json` against `ideal.json` and
  accepts only a diff of exactly those eight hunks.
- **G32 (FILE `tests/test_benchscore.py`; after: G7, G29, G30, G31).** Unit cases on a small two-page
  matter and key (reuse `test_matter.make` and a key dict), counted into `score_cases`: (1) perfect;
  (2) one key fact dropped -> `missed=1`, `missed_ids == ("F2",)`; (3) a quote not on the page ->
  `invented=1` and the key fact it replaced is missed; (4) a cite not a page -> `invented=1`; (5) a real
  fact not in the key -> `extra=1` and `perfect` True; (6) a duplicate candidate fact -> neither; (7) a
  flag with the right cites but kind swapped `conflict` -> `gap` -> `flags_missed=1 flags_extra=1` and
  `perfect` False (the kind probe for seed b and the flags_extra probe for seed e); (8) a fact text
  `"The IME found nothing."` -> `rules=1`; (9) a flag about `"The IME found nothing."` with the key's
  kind and cites -> `rules=1`; (10) `pages_failed=2` -> `perfect` False; (11) an added flag with a
  kind and cite set not in the key -> `flags_extra=1`, `perfect` False. Print `f"score_cases={ok} of
  11"`. Then the two shipped fixtures: load matter `9001.001`, key, rules (`casefile.rules.load(ROOT /
  "playbook" / "rules.toml")`), `ideal.json` via `parse_text` -> `score(...).line("9001.001")` must
  equal the perfect line exactly and `perfect` True; `tests/fixtures/bench/flawed.json` -> the flawed
  line exactly and `perfect` False. Print both lines under `capsys.disabled()` before asserting.

### W7. Model client `raw` and the stage 2 runner (ledger R2-3e)

Files: `src/casefile/model.py` (FILE rewrite, 85 lines, Codex 15), new `src/casefile/benchrun.py`
(about 100 lines). The tests for both are W8 (they need the stand-in's recording, G35).
Numbers: `tests/test_model.py` unchanged (`pytest_exit=0`); `card_version=<12 hex>`.
CHECK: `scripts/run.sh pytest -q -s tests/test_model.py > "$TMPDIR/w7.log"; rc=$?; echo
"pytest_exit=$rc"; test "$rc" -eq 0 && scripts/run.sh python -c 'from casefile import benchrun;
print(f"card_version={benchrun.card_version()}")' | grep -E '^card_version=[0-9a-f]{12}$'` -> status 0.
Also `git diff --stat src/casefile/model.py` shows only the `ModelError.__init__` lines and the five
`raise ModelError(..., raw)` sites in `chat`; anything else is rejected and re-asked.
SEEDS: run with W8's (W8 seed e is the `raw` seed).
Librarian pre-flight: lines 21, 22, 27 (#R01-CX-5, #R01-CX-10, #R01-CX-11).

- **G33 (FILE `src/casefile/model.py`; after: none; context: `src/casefile/model.py` whole).** The
  complete file copied verbatim except: `class ModelError(RuntimeError):` gains
  ```
      def __init__(self, message, raw=None):
          super().__init__(message)
          self.raw = raw
  ```
  (the docstring stays), and in `chat` the five raises after `raw = self._request(...)` pass the reply:
  `raise ModelError(f"status=200 missing message.content: {str(raw)[:200]}", raw)`, `raise
  ModelError(f"status=200 empty message.content: {str(raw)[:200]}", raw)`, `raise ModelError("status=200
  done must be true", raw)`, `raise ModelError(f"status=200 invalid {field}", raw)`, `raise
  ModelError("status=200 invalid done_reason", raw)`. Every other raise (`NoRedirect`, `_request`)
  stays a one-argument raise (`raw` is `None`). `tests/test_model.py` pins every message and must stay
  green.
- **G34 (FILE `src/casefile/benchrun.py`; after: G6, G27, G33).** Imports: `from dataclasses import
  dataclass; import hashlib; import json; from casefile.benchcandidate import EMPTY, Candidate,
  CandidateError, parse_text; from casefile.matter import Matter, Page; from casefile.model import
  ModelClient, ModelError`. Constants:
  ```
  CARD = "bench.extract"
  CARD_TEXT = (
      "You are reading the pages of one workers' compensation matter. Use only the text in this request.\n"
      "Answer with one JSON object and nothing else: {\"facts\": [...], \"flags\": [...]}.\n"
      "Each fact: {\"cite\": the Bates stamp of the page, \"quote\": an exact span copied from that page, "
      "\"text\": one sentence that says no more than the quote}.\n"
      "Each flag: {\"kind\": \"conflict\" or \"gap\", \"cites\": the Bates stamps involved, \"about\": one sentence}.\n"
      "A conflict is two pages that disagree. A gap is a record a page refers to that is not among these pages.\n"
      "Never name an examination as a DME or an IME in any form; write \"the report\".\n"
      "Never write who hired, paid or retained a doctor, any fee, or how many examinations a doctor does.\n"
      "Never guess, infer or fill in. If a value is not on the page, leave it out.\n")
  ```
  Functions:
  ```
  def card_version() -> str: return hashlib.sha256(CARD_TEXT.encode()).hexdigest()[:12]
  def page_block(page: Page) -> str: return f"=== PAGE {page.page_id} BATES {page.bates} ===\n{page.text}\n"
  def messages(matter: Matter) -> list[dict]:
      body = f"Matter {matter.number}\n" + "".join(page_block(p) for p in matter.pages)
      return [{"role": "system", "content": CARD_TEXT}, {"role": "user", "content": body}]
  def prompt_sha256(msgs) -> str: return hashlib.sha256(json.dumps(msgs, sort_keys=True).encode()).hexdigest()
  def counts_ok(answer) -> bool:
      return all(type(c) is int and c > 0 for c in (answer.prompt_eval_count, answer.eval_count))
  @dataclass(frozen=True)
  class RunResult: candidate: Candidate; pages_failed: int; failure: str | None
  def run(matter: Matter, config, log, playbook_version: str, opener=None) -> RunResult
  ```
  Calls it makes, quoted: `log.start_run(self, *, job, card, card_version, playbook_version, model,
  pages_in, prompt_sha256, matter=None) -> int` (runlog.py:56); `log.record_answer(self, run_id, *,
  raw_answer, status, done_reason=None, prompt_eval_count=None, eval_count=None)` (runlog.py:67) with
  status `ok` or `failed`; `log.record_failure(self, run_id, gate, message)` (runlog.py:77);
  `ModelClient(config, opener=None)` (model.py:31) taking `config.model`; `client.chat(self, messages,
  *, options=None) -> Answer(content, done_reason, prompt_eval_count, eval_count, raw)` (model.py:64);
  `ModelError.raw` (G33). `run`: `msgs = messages(matter)`; `n = len(matter.pages)`; `run_id =
  log.start_run(job="bench", matter=matter.number, card=CARD, card_version=card_version(),
  playbook_version=playbook_version, model=config.model.name, pages_in=n,
  prompt_sha256=prompt_sha256(msgs))`; `client = ModelClient(config.model, opener)`; `try: answer =
  client.chat(msgs, options={"num_ctx": config.model.num_ctx})` (the option is what doctor.py:113
  passes; `chat` re-installs the configured values anyway, model.py:67) `except ModelError as exc: if
  exc.raw is not None: log.record_answer(run_id, raw_answer=json.dumps(exc.raw), status="failed")`;
  `log.record_failure(run_id, "bench.model", str(exc))`; `return RunResult(EMPTY, n, f"bench.model:
  {exc}")`. Then `fields = dict(done_reason=answer.done_reason, prompt_eval_count=answer.prompt_eval_count,
  eval_count=answer.eval_count)` and `raw_text = json.dumps(answer.raw)`. Guards in this order, each
  recording the answer `failed` with `**fields`, a failure row, and returning `RunResult(EMPTY, n,
  f"<gate>: <message>")`: `answer.done_reason != "stop"` -> gate `bench.truncation`, message
  `f"done_reason={answer.done_reason}"`; `not counts_ok(answer)` -> gate `bench.counts`, message
  `"prompt_eval_count and eval_count must be positive integers"` (Codex 3, as doctor.py:127);
  `parse_text(answer.content)` raising `CandidateError` -> gate `bench.answer`, message `str(exc)`.
  Else `log.record_answer(run_id, raw_answer=raw_text, status="ok", **fields)` and `return
  RunResult(candidate, 0, None)`. `config` is the `Config` dataclass (config.py:56-62); `log` is a
  `RunLog` (runlog.py:41).

### W8. The stand-in's bench recording and the runner tests (ledger R2-3d)

Files: new `tests/fakemodel/bench.py` (about 30 lines); `tests/fakemodel/__main__.py` (FILE rewrite, 34
lines); new `tests/test_fakemodel_bench.py` (about 50 lines); new `tests/test_benchrun.py` (about 120
lines).
Numbers: `bench_recording_ok=1 modes=4 pages_in_request=14`; `benchrun_modes=7 of 7 answers_ok=1
answers_failed=6 failures=6`.
CHECK: `scripts/run.sh pytest -q -s tests/test_fakemodel_bench.py tests/test_benchrun.py >
"$TMPDIR/w8.log"; rc=$?; grep -E '^(bench_recording_ok|benchrun_modes)=' "$TMPDIR/w8.log"; echo
"pytest_exit=$rc"; test "$rc" -eq 0` -> the two lines, `pytest_exit=0`, status 0.
SEEDS: (a) benchrun.py drop the `done_reason != "stop"` guard -> the `length-with-valid-json` probe
scores as a full candidate, `benchrun_modes=6 of 7`, status 1; (b) the `record_failure` call for
`bench.answer` removed -> `failures=4`, status 1; (c) `matter=matter.number` -> `matter=None` in
`start_run` -> the run-row assertion `runs.matter == "9001.001"` fails, status 1 (Codex 8 replaced the
`options` seed, which model.py:67 makes inert); (d) drop the `counts_ok` guard -> the `eval_count None`
probe scores as a full candidate, `benchrun_modes=6 of 7`, status 1; (e) model.py `raise
ModelError("status=200 done must be true")` without `raw` -> the `incomplete` probe records no answer
row, `answers_failed=5`, status 1; (f) `recordings_for` builds the recording with the pages in reverse
order -> the independently built request gets `404 fakemodel: no recording for these messages`, status 1
(Codex 6).
Librarian pre-flight: lines 21, 22, 27 (#R01-CX-5, #R01-CX-10: a probe where only the truncation guard is
wrong; #R01-CX-11).

- **G35 (FILE `tests/fakemodel/bench.py`; after: G30, G34).** Docstring `"""Build the stand-in's
  recording for a benchmark matter from its pages and ideal answer (invented data only)."""`. Imports:
  `import json; from pathlib import Path; from casefile import benchrun, matter as matters`. Function:
  ```
  def recordings_for(matter_root) -> list[dict]:
      root = Path(matter_root)
      loaded = matters.load(root)
      ideal = json.loads((root / "ideal.json").read_text(encoding="utf-8"))
      return [{"name": f"bench-{loaded.number}", "messages": benchrun.messages(loaded),
               "answer": json.dumps(ideal, ensure_ascii=False)}]
  ```
  Calls: `matters.load(root) -> Matter` (G6), `benchrun.messages(matter) -> list[dict]` (G34).
- **G36 (FILE `tests/fakemodel/__main__.py`; after: G35; context: the current file, 34 lines).** The
  file copied verbatim except: imports gain `import json`, `from pathlib import Path` and `from .bench
  import recordings_for`; after `parser.add_argument("--model", default=DEFAULT_MODEL)` add
  `parser.add_argument("--bench-matter", action="append", default=[], metavar="DIR")`; before the
  `try:` that calls `serve`, build `rows = json.loads(Path(__file__).with_name("recordings.json")
  .read_text(encoding="utf-8"))` and `for d in args.bench_matter: rows.extend(recordings_for(d))`;
  the `serve(...)` call becomes `serve(args.bind, args.port, FakeModel(mode=args.mode,
  model=args.model, recordings=rows))` (`FakeModel(*, mode="replay", model=DEFAULT_MODEL,
  context_length=65536, recordings=None)`, core.py:20, where `recordings` may be a list of rows,
  D0.5). Nothing else changes.
- **G37 (FILE `tests/test_fakemodel_bench.py`; after: G35).** Imports: `import json; from
  casefile import matter as matters; from casefile.benchrun import CARD_TEXT; from conftest import
  ROOT; from fakemodel.core import FakeModel; from fakemodel.bench import recordings_for` (import
  paths as `tests/test_fakemodel.py` uses). `MATTER = ROOT / "tests/fixtures/matters/9001.001"`.
  `test_bench_recording(capsys)`: build the **expected request independently of `benchrun.messages`**
  (Codex 6): `m = matters.load(MATTER)`; `body = "Matter 9001.001\n" + "".join(f"=== PAGE
  {p.page_id} BATES {p.bates} ===\n{p.text}\n" for p in m.pages)`; `expected = [{"role": "system",
  "content": CARD_TEXT}, {"role": "user", "content": body}]`; assert `body.count("=== PAGE ") == 14`
  and every `p.text in body`; `fake = FakeModel(recordings=recordings_for(MATTER))`; post `/api/chat`
  with `{"model": "qwen3.8:27b", "messages": expected, "stream": False, "options": {"num_ctx": 65536,
  "temperature": 0.1}}` through `fake.handle("POST", "/api/chat", json.dumps(request).encode())` (as
  `tests/test_fakemodel.py:21-25`) -> status 200 and `json.loads(payload["message"]["content"])` equals
  `json.loads((MATTER / "ideal.json").read_text())`; for each mode in `truncated`, `malformed`,
  `forbidden`, `incomplete` set `fake.mode` and assert the response differs from the replay (content
  halved with `done_reason == "length"`; content not JSON; content contains `IME`; `done` is False);
  print `f"bench_recording_ok=1 modes={n} pages_in_request={body.count('=== PAGE ')}"`. `main([...])`
  of `tests/fakemodel/__main__.py` is not run here (it serves forever); the socket path is W10.
- **G38 (FILE `tests/test_benchrun.py`; after: G35, G34).** Setup: `write_config(tmp_path)`
  (conftest.py:26) and `casefile.config.load` it; `log = runlog.open_db(tmp_path / "runlog.sqlite")`
  (`open_db(path) -> RunLog`, runlog.py:105); `rows = recordings_for(MATTER)`; `fake =
  FakeModel(recordings=rows)`; `opener = FakeTransport(fake)` (as `tests/test_stage1_exit.py:64-78`);
  `matter = casefile.matter.load(MATTER)`. Seven probes, each `benchrun.run(matter, config, log,
  "pb-test", opener)`: (1) replay -> `pages_failed == 0`, `failure is None`,
  `len(result.candidate.facts) == 28`; (2) `fake.mode = "truncated"` ->
  `failure.startswith("bench.truncation")`, `pages_failed == 14`; (3) `fake.mode = "malformed"` ->
  `failure.startswith("bench.answer: not JSON")`; (4) `fake.mode = "forbidden"` ->
  `failure.startswith("bench.answer")` (the forbidden sentence is not JSON); (5) the truncation-only
  probe: `fake.mode = "replay"`, wrap `fake.handle` so the payload's `done_reason` becomes `"length"`
  while the content stays the full JSON (`original = fake.handle; def handle(m, p, b=b""): s, payload =
  original(m, p, b); if p == "/api/chat": payload["done_reason"] = "length"; return s, payload;
  fake.handle = handle`) -> `failure.startswith("bench.truncation")`; restore `fake.handle`; (6)
  `fake.mode = "incomplete"` (`done` False, full content; core.py:121) ->
  `failure.startswith("bench.model: status=200 done must be true")` and the newest `answers` row has
  status `failed` with `'"done": false' in raw_answer`; (7) the counts probe: `fake.mode = "replay"`,
  wrap `fake.handle` so `payload["eval_count"] = None` -> `failure.startswith("bench.counts")`,
  `pages_failed == 14`. Request shape (probe 1): the last `/api/chat` body in `fake.requests` decodes
  to `options == {"num_ctx": 65536, "temperature": 0.1}` and `stream is False` and `messages[1]
  ["content"].startswith("Matter 9001.001\n=== PAGE medical/001 BATES MED0001 ===")`. Run log: `runs`
  count 7 and every `runs.matter == "9001.001"`, `runs.job == "bench"`, `runs.pages_in == 14`;
  `answers` rows 7, of which 1 `ok` and 6 `failed`; `failures` rows 6 with gates `bench.truncation`,
  `bench.answer`, `bench.answer`, `bench.truncation`, `bench.model`, `bench.counts` in that order;
  print `f"benchrun_modes={ok} of 7 answers_ok={ok_answers} answers_failed={failed_answers}
  failures={failures}"`. Close the log in `finally`.

### W9. `casefile bench` (ledger R2-3f)

Files: new `src/casefile/bench.py` (about 100 lines); `src/casefile/cli.py` (FILE rewrite, 55 lines);
new `tests/test_bench_cli.py` (about 100 lines).
Numbers: `bench_exit_perfect=0 bench_exit_flawed=1 bench_exit_badkey=2 bench_exit_noconfig=2
bench_exit_nolog=2`.
CHECK: `scripts/run.sh pytest -q -s tests/test_bench_cli.py > "$TMPDIR/w9.log"; rc=$?; grep -E
'^bench_exit_' "$TMPDIR/w9.log"; echo "pytest_exit=$rc"; test "$rc" -eq 0` -> the line above,
`pytest_exit=0`, status 0. Also the standing command: `scripts/run.sh casefile bench --matters
tests/fixtures/matters --candidate tests/fixtures/matters/9001.001/ideal.json --config <tmp config>`
prints the perfect line and `bench matters=1 imperfect=0`, status 0; with `flawed.json` the flawed line
and `imperfect=1`, status 1.
SEEDS: (a) bench.py `return 0 if imperfect == 0 else 1` -> `return 0` -> `bench_exit_flawed=0`, status 1;
(b) the `BenchKeyError` handler `return 2` -> `return 1` -> `bench_exit_badkey=1`, status 1; (c) cli.py
`return bench.main(...)` -> `bench.main(...)` without return -> every exit 0, status 1; (d) bench.py
drop the `except (OSError, sqlite3.Error)` around `open_db` -> the no-log case is a traceback, exit 1,
`bench_exit_nolog=1`, status 1 (Codex 14).
Librarian pre-flight: lines 27, 28, 29 (#R01-CX-11 exit codes; #R01-OC-M2; #R01-OC-M7: bench creates
only the run log under `[paths].state`, never a matters folder).

- **G39 (FILE `src/casefile/bench.py`; after: G23, G29, G34).** Imports: `from pathlib import Path;
  import sqlite3; import sys; from casefile import benchkey, benchrun, benchscore, matter as matters,
  playbook, runlog; from casefile.benchcandidate import CandidateError, parse_text; from
  casefile.config import ConfigError, load`. Function:
  ```
  def main(matters_dir, config_path=None, candidate_path=None, *, out=None, err=None,
           opener=None, runner=benchrun.run) -> int
  ```
  `out = sys.stdout if out is None else out`; `err = sys.stderr if err is None else err`. Every
  printed reason is one line (`" ".join(str(exc).splitlines())`, as gate.py:72 does). Steps: `config =
  load(config_path)` (`ConfigError` -> print `f"ConfigError: {exc}"` to `err`, return 2); `book =
  playbook.load(config.paths.playbook)` (`playbook.PlaybookError` -> `f"PlaybookError: {exc}"`, 2;
  `Playbook(version, entries, rules)`, playbook.py:36); `roots = sorted(p for p in
  Path(matters_dir).iterdir() if (p / "matter.toml").is_file())` (an `OSError` -> `f"bench: cannot
  read {matters_dir}: {exc}"`, 2); empty -> `f"bench: no matters under {matters_dir}"`, 2;
  `candidate_path is not None and len(roots) != 1` -> `"bench: --candidate needs exactly one matter"`,
  2. If `candidate_path is None`: `log_path = config.paths.state / "runlog.sqlite"`; `try: log =
  runlog.open_db(log_path)` `except (OSError, sqlite3.Error) as exc:` print `f"bench: cannot open run
  log {log_path}: {exc}"`, return 2 (Codex 14; `open_db` creates the parent folder, runlog.py:107, and
  raises `OSError` when it cannot, `sqlite3.Error` when the database is unusable); else `log = None`.
  Then, inside `try ... finally: if log is not None: log.close()`, for each root: `matter =
  matters.load(root)`; `key = benchkey.load(root / "key.json", matter)` (`matters.MatterError`,
  `benchkey.BenchKeyError` -> `f"{type(exc).__name__}: {exc}"`, 2). If `candidate_path`: `candidate =
  parse_text(Path(candidate_path).read_text(encoding="utf-8"))` (`OSError`, `UnicodeDecodeError`,
  `CandidateError` -> `f"CandidateError: {exc}"`, 2); `pages_failed = 0`. Else: `result =
  runner(matter, config, log, book.version, opener)` (`sqlite3.Error` -> `f"bench: run log: {exc}"`,
  2); `candidate, pages_failed = result.candidate, result.pages_failed`; if `result.failure`: print
  `f"bench {matter.number} failure {result.failure}"` to `out`. Then `s = benchscore.score(key,
  candidate, matter, book.rules, pages_failed)`; print `s.line(matter.number)`; `imperfect += not
  s.perfect`. After the loop print `f"bench matters={len(roots)} imperfect={imperfect}"`; `return 0 if
  imperfect == 0 else 1`.
- **G40 (FILE `src/casefile/cli.py`; after: G39; context: the current file, 55 lines).** The file
  copied verbatim except: line 9 becomes `from casefile import __version__, bench, doctor, playbook`;
  after `show.add_argument("--config", type=Path)` insert
  ```
      bench_parser = subcommands.add_parser("bench", help="Score invented matters against their answer keys")
      bench_parser.add_argument("--matters", type=Path, required=True)
      bench_parser.add_argument("--candidate", type=Path)
      bench_parser.add_argument("--config", type=Path)
  ```
  and before `    elif args.command == "config":` insert
  ```
      elif args.command == "bench":
          return bench.main(args.matters, args.config, args.candidate)
  ```
  Nothing else changes (`tests/test_cli*.py` pin the other commands).
- **G41 (FILE `tests/test_bench_cli.py`; after: G31, G40).** Use `subprocess.run(["casefile",
  "bench", ...], capture_output=True, text=True, timeout=60)` with `CASEFILE_CONFIG` set to
  `write_config(tmp_path, playbook=ROOT / "playbook", host="http://127.0.0.1:9")` (port 9: nothing
  listens; no run here may reach a model). Five runs: `--candidate ideal.json` -> exit 0, stdout's
  first line is the perfect line, last line `bench matters=1 imperfect=0`; `--candidate
  tests/fixtures/bench/flawed.json` -> exit 1, the flawed line, `imperfect=1`; a copy of the matter
  under `tmp_path / "bad" / "9001.001"` with one quote altered in `key.json` -> exit 2, stdout empty,
  stderr starts `BenchKeyError:`; `--config` pointing at a missing file -> exit 2, stderr `ConfigError:
  no config file`; no `--candidate` with a second config whose `state` is `tmp_path / "blocker" /
  "state"` where `blocker` is a regular file (`open_db`'s `mkdir` raises `NotADirectoryError`) ->
  exit 2, stdout empty, stderr starts `bench: cannot open run log`. Print `f"bench_exit_perfect={a}
  bench_exit_flawed={b} bench_exit_badkey={c} bench_exit_noconfig={d} bench_exit_nolog={e}"`. Also
  assert no `runlog.sqlite` was created under the first config's state folder (no model call, no run
  row).

### W10. Stage 2 exit test (ledger R2-3g)

Files: new `tests/test_stage2_exit.py` (about 90 lines).
Numbers: `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1` followed by the perfect line; control
line `stage2-control exit=0 runs=+1 answers_ok=+1`.
CHECK: `scripts/run.sh pytest -q -s tests/test_stage2_exit.py > "$TMPDIR/w10.log"; rc=$?; grep -E
'^stage2' "$TMPDIR/w10.log"; echo "pytest_exit=$rc"; test "$rc" -eq 0` -> the two lines,
`pytest_exit=0`, status 0.
SEEDS: (a) remove F10 from `ideal.json` -> the replayed answer lacks it, the line shows `found=25 of 26
missed=1`, exit 1, status 1, red (restore by cmp); (b) `server.shutdown()` removed from the test's
`finally` -> `thread.join(timeout=5)` times out, `server_stopped=0`, the assertion fails, status 1
(Codex 13: `server_close()` closes the listening socket, socketserver.py:489, so a listener count
cannot see a missing shutdown; thread liveness can).
Librarian pre-flight: lines 27, 30 and R01-P-1 (servers stopped by the test that started them).

- **G42 (FILE `tests/test_stage2_exit.py`; after: G35, G40).** Mirror `tests/test_stage1_exit.py:43-59`:
  `@pytest.mark.socket` `test_stage2_exit(tmp_path, capsys)`: `server = serve(port=0,
  model=FakeModel(recordings=recordings_for(MATTER)))` (`serve(bind="127.0.0.1", port=18434,
  model=None)`, server.py:9); `thread = Thread(target=server.serve_forever, daemon=True)`; `path =
  write_config(tmp_path, host=f"http://127.0.0.1:{server.server_port}", playbook=ROOT / "playbook")`;
  count `runs` and `answers where status='ok'` in `config.paths.state / "runlog.sqlite"` before (0 if
  absent); `command = ["scripts/run.sh", "casefile", "bench", "--matters", "tests/fixtures/matters"]`
  with `cwd=ROOT`, `CASEFILE_CONFIG=path`, timeout 120; after: recount. The `finally:` is
  `server.shutdown(); thread.join(timeout=5); alive = thread.is_alive(); server.server_close()`
  (liveness measured before the socket is closed), and after the `try/finally` the test prints
  `f"stage2 exit={rc} runs={dr:+d} answers_ok={da:+d} server_stopped={int(not alive)}"` and the first
  stdout line, then asserts exit 0, first line equals the perfect line, last line `bench matters=1
  imperfect=0`, `dr == 1`, `da == 1`, `not alive`. In-process control `test_stage2_inprocess_control`:
  as `test_stage1_exit.py:64-88`, a child script that patches `benchrun.ModelClient` to use
  `FakeTransport(FakeModel(recordings=recordings_for(MATTER)))` and runs `cli.main()` with `bench
  --matters tests/fixtures/matters` through `scripts/run.sh`; same assertions, label `stage2-control`.

### W11. Prose gate on fixture text, baselines, records (ledger R2-4, R2-5)

Files: `src/casefile/prose.py` (FILE rewrite, 21 lines); ledger `## Project` baselines (chair); spec §9
D25, §11 row, Librarian, agent log, round report, handoff (chair at close).
Numbers: gate `prose ... files=<77 + 17 fixture files + new .py files>`, prints `0`.
CHECK: `scripts/run.sh python -m casefile.gate > "$TMPDIR/w11.log"; rc=$?; tail -1 "$TMPDIR/w11.log";
grep -E '^gate prose ' "$TMPDIR/w11.log"; test "$rc" -eq 0` -> `0`, the prose row with the new file
count, status 0 (`gate.main` returns the failed count, gate.py:75).
SEED: insert an em dash (U+2014) in `records/employer/002.txt` -> `gate prose FAIL dashes=1`, prints
`1`, status 1 (restore by cmp).
Librarian pre-flight: line 17 (#R01-CX-2: cover the whole class, every fixture suffix).

- **G43 (FILE `src/casefile/prose.py`; after: none; context: the current file, 21 lines).** The file
  copied verbatim except `PATTERNS` becomes `("*.md", "docs/**/*.md", ".workflow/LEDGER.md",
  "playbook/**/*.toml", "src/**/*.py", "tests/**/*.py", "tests/fixtures/**/*.txt",
  "tests/fixtures/**/*.json", "tests/fixtures/**/*.toml", "scripts/*", "config.example.toml",
  "pyproject.toml")`. Nothing else changes. `tests/test_prose.py` keeps passing (it scans a temp root).
- **Chair (not Gemma):** regression baselines in `## Project`: tests passed (expected about 233 + 45),
  gate `0`, suite seconds, the perfect line, the flawed line, `stage2 exit=0 runs=+1 answers_ok=+1
  server_stopped=1`; spec D25 (§6) and the §11 stage 2 row; Librarian entries for any defect found;
  tuning questions T-7 to T-11 (§7); owner questions 21 to 23 appended (§7).

## §3 Build order (one local model: sequential tasks, dependency-correct)

The task number is the build order: G1, G2, ..., G43. Every task's "after:" list names what must have
passed before it starts (Codex 9); the order below satisfies every one. The 43 tasks: G1 (W1); G2, G3
(W2); G4 to G7 (W3); G8 to G22 (W4); G23 to G26 (W5); G27 to G32 (W6); G33, G34 (W7); G35 to G38
(W8); G39 to G41 (W9); G42 (W10); G43 (W11). Independent groups the orchestrator may interleave to keep
a failed code task's retry from waiting on prose: G1; G2 to G3; G4 to G7; G8 to G22 (any order); G27 to
G28; G33; G43. Dependencies with the reason: G3 after G2 (the messages); G5 after G4; G7 after G6; G23
after G4 and G6 (imports `quotes`, `matter`); G24 after G7 and G23 (`make`, `BenchKeyError`); G25
after G8 to G22 (quotes copied from committed pages); G26 after G22, G23, G25 (loads the fixture and
the key); G29 after G4, G6, G23, G27 (`Key`, `Candidate`); G30 after G25 (derived from the key); G31
after G30; G32 after G7, G29, G30, G31; G34 after G6, G27, G33 (`ModelError.raw`); G35 after G30 and
G34 (`ideal.json`, `benchrun.messages`); G36 after G35; G37 after G35; G38 after G34 and G35; G39
after G23, G29, G34; G40 after G39; G41 after G31 and G40; G42 after G35 and G40; G43 last (the gate
widens only once every fixture file exists). CHECKs run at the end of each W section (W4's after G22,
W7's after G34, W8's after G38); the orchestrator commits after each passing CHECK and its seeds
(R01-P-1). No worktrees: one builder, one tree.

## §4 Test design

- Regression set (every builder report and the chair before each commit): `scripts/run.sh pytest -q`
  (expected about 278 passed, under 52 s: T-6 line is 60 s), `scripts/run.sh python -m casefile.gate`
  prints `0` and exits 0, `scripts/run.sh pytest -q -s tests/test_stage1_exit.py` unchanged (`exit=1
  verdicts=8 fails={'ocr'} test_jobs=1`), `scripts/run.sh pytest -q tests/test_model.py` unchanged.
- Stage 2 exit test: `scripts/run.sh pytest -q -s tests/test_stage2_exit.py` prints `stage2 exit=0
  runs=+1 answers_ok=+1 server_stopped=1` and the perfect line (socket, Q18) and the in-process
  control; plus the standing command `scripts/run.sh casefile bench --matters tests/fixtures/matters
  --candidate tests/fixtures/bench/flawed.json` printing the flawed line with exit 1. Both lines go into
  the ledger as baselines; a later stage that changes either number must say why in its brief.
- New evidence lines (one per test file, greppable): `newline_join_exit`, `resolve_refused`,
  `quotes_ok`, `matter_pages`, `fixture_pages`, `key_refusals`, `key_facts`, `candidate_refusals`,
  `score_cases`, the two `bench 9001.001` lines, `bench_recording_ok`, `benchrun_modes`,
  `bench_exit_*`, `stage2`.
- Seeds (every one re-run by the chair, restored by cmp, accepted only when the CHECK's exit status
  turned non-zero): the 27 listed in §2 (W1 1, W2 2, W3 4, W4 1, W5 2, W6 5, W8 6, W9 4, W10 2,
  W11 1); each counter of the score has a probe where only it is wrong (#R01-CX-10): missed (drop F10
  in ideal), invented (extra counted as invented), extra (perfect line), flags kind (swap), flags_extra
  (added flag, seed e), rules (texts dropped from the rules input, seed c), pages_failed (truncation-only
  probe with valid JSON; counts probe).
- What the verifier should probe beyond the CHECKs: `casefile bench` with `--matters` pointing at an
  empty folder (exit 2, `no matters under`), at a folder with two matters and `--candidate` (exit 2),
  with the stand-in in `truncated` mode started by hand (`python -m tests.fakemodel --port 0
  --bench-matter tests/fixtures/matters/9001.001 --mode truncated`: the bench prints `bench 9001.001
  failure bench.truncation: done_reason=length` then the line with `found=0 of 26 ... pages_failed=14
  of 14`, exit 1, and the run log holds the failed answer; stop the server afterwards), and a
  `key.json` whose quote differs only by a curly quote (loads). Three probes that document limits
  rather than defects, each recorded with its number in the verifier report: (1) `ideal.json` with
  F21's text reversed to "The patient has reached maximum medical improvement." still prints the
  perfect line (§1.2 known limit, T-11); (2) a candidate text ending "See page 12" prints `rules=0`
  (R1-20, §1.18); (3) a candidate that adds a `conflict` and a `gap` for every pair of stamps prints
  `flags=5 of 5` and a large `flags_extra`, exit 1 (§1.7: flags_extra fails).

## §5 Risks, each with a tripwire

- R1. **The small model gets a task wrong in a way its test does not catch** (a test that asserts the
  wrong number, or code and test written to agree). Tripwire: the chair runs every seed in §2; any seed
  that stays green is a stop for that item; the Fable code review (Q28) compares each module against
  this brief's signatures line by line and reports every deviation; tally `gemma_attempts` per task in
  the agent log; if more than 12 of the 43 tasks fall back to Sonnet the chair stops and reports to the
  owner before continuing (the tier is not working).
- R2. **Fixture prose drifts from the bible** (a date, a weight or a name differs between pages, or a
  required sentence is paraphrased). Tripwire: the per-page CHECK (every verbatim line present, stamp
  last, name present, no dashes), `key_facts=26 flags=5 pages=14` (every quote verbatim) and the
  orchestrator's read of every page before commit, checking the bible's 14 rows.
- R3. **Recording mismatch**: a page or the card changes after `ideal.json` was recorded. Tripwire: the
  recording is rebuilt per run (§1.8); G37's independently built request (Codex 6); the exit test's
  `pages_failed=0 of 14`; a `404 no recording` in any bench output is a finding.
- R4. **Masked guards in the runner** (truncation, counts and shape all fire on the stand-in's
  `truncated` mode). Tripwire: W8 probes 5 and 7 (`length` with valid JSON; `eval_count` None with valid
  JSON) and seeds (a), (d) red.
- R5. **Suite time.** 14 page reads, three subprocess tests and one socket test. Tripwire:
  `scripts/run.sh pytest -q` under 52 s (41.8 s + 10); past 60 s is T-6's revisit line.
- R6. **A stand-in server left running** by a critic or verifier (R01-P-1). Tripwire: every socket test
  stops its server in `finally` and asserts the serving thread ended (`server_stopped=1`); the chair
  runs `lsof -nP -iTCP -sTCP:LISTEN | grep -c Python` before and after the critic round and reports the
  difference (expected 0).
- R7. **Privacy**: a Gemma page echoes something that looks like a real record or a real name. Tripwire:
  §6b's read of every page by the orchestrator before commit; gate privacy `offenders=0`; no `.pdf`,
  `.docx` or image under `tests/fixtures/matters/` (`find tests/fixtures/matters -type f | grep -v -E
  '\.(txt|json|toml)$'` prints nothing).
- R8. **Em dashes in fixture prose** (Gemma's default style). Tripwire: the per-page CHECK's dash grep;
  W11's prose row after G43; `dashes=0`.
- R9. **The bench writes somewhere it should not.** Tripwire: W9's assertion that `--candidate` runs
  create no `runlog.sqlite`; the session-level `production_dirs_untouched` fixture (conftest.py:92-96)
  stays green; `git status --short` after the suite shows only intended files.
- R10. **Flags matched by cite set only** could call a gap and a conflict on the same pages equal, and
  flags that fail nothing would reward spam. Tripwire: W6 kind-swap case, seed (b), seed (e), and the
  verifier's flag-spam probe (§4).
- R11. **The key's `text` or a flag's `about` trips a firm rule** (for example "Dr. Marchetti's report
  was paid for ..."). Tripwire: `test_key_loads` asserts `rules=0` over the key's prose; the perfect line's
  `rules=0`.
- R12. **A summary that contradicts its quote scores `found`** (§1.2 known limit, Codex 4). Tripwire:
  the verifier's reversal probe (§4) records the number; T-11 carries the design to stage 4; the bench
  line is never described as measuring summary faithfulness in the ledger or the report.
- R13. **Gemma retypes a quote instead of copying it** (a changed article, a straightened number, a
  dropped period) in `key.json`, `ideal.json` or `flawed.json`. Tripwire: `test_key_loads` (every key
  quote found on its page), the perfect line (`invented=0`), the orchestrator's `diff ideal.json
  flawed.json` of exactly eight hunks; three failures re-split the key per binder (G25).
- R14. **The driver writes a partial answer** (a cut-off reply with a FILE header). Tripwire: the driver
  requires `done` true and `done_reason == "stop"` and parses every `.py` and `.json` answer before
  writing (D0.14, Codex 2); the chair verifies with one deliberate `--num-predict 64` run that exits 3
  and writes nothing before the first real task.

## §6 Contradictions and amendments (chair rulings, pending veto)

- **D25 (new, spec §9):** "`casefile bench --matters DIR [--candidate FILE] [--config FILE]`: each
  subfolder with `matter.toml` is a matter: `records/<binder>/<nnn>.txt` pages with the Bates stamp
  alone on the last line (single-stamp form of Q21), `key.json` (facts: id, cite, quote, text; flags:
  id, kind conflict or gap, cites, about), validated against the pages before scoring; a candidate is
  `{facts: [cite, quote, text], flags: [kind, cites, about]}`; found = same cite and the same quote
  after normalisation (casefold, straight quotes, collapsed whitespace); invented = cite not a page or
  quote not on it; extra = on the page, not in the key; flags match by kind and cite set; rules = firm
  rule findings over every text and about; a fact's text is not compared with its quote at stage 2
  (the §4 ladder, stage 4); one line per matter `bench <number> found=F of K missed=M invented=I
  extra=E flags=G of H flags_missed=X flags_extra=Y rules=R pages_failed=P of N`; exit 0 when every
  matter is perfect (missed, invented, flags_missed, flags_extra, rules, pages_failed all 0; extra
  alone never fails), 1 otherwise, 2 when it cannot run (config, playbook, matter, key, candidate file,
  or the run log cannot be opened); `--matters` is independent of `[paths].matters` (D13 guards client
  matters; benchmark matters are invented and may live in the checkout); stage 2 runner: one
  `/api/chat` call per matter with the fixed card `bench.extract`, logged as a run with every received
  reply stored as an answer row (`ok` or `failed`) and failures under `bench.model`,
  `bench.truncation`, `bench.counts`, `bench.answer`; the runner is replaced by the pipeline at stage 5
  and the quote match by the §4 ladder at stage 4." Why: spec §5's benchmark row names the four scores
  but no format, key, exit or fixture shape.
- **Spec §5 Benchmark row** reads "answer keys from closed matters". Old: that text. New (as-built §11
  note, not a §5 edit): "stage 2 keys are invented (`tests/fixtures/matters/`); closed-matter keys are
  stage 9 work by the owner (§10 question 2)". Why: Q9 forbids client data in the loop.
- **D20 amendment:** old "rows pytest, privacy (ignored files included), rules self-test, playbook,
  prose"; new "... prose (authored surfaces including `tests/fixtures/**` text, JSON and TOML)". Why:
  fixture prose is prose (CLAUDE.md rule).
- **D13 clarification (text unchanged):** `[paths].matters` is the client matters folder only; `casefile
  bench --matters` is a separate argument and is not guarded by D24 (recorded inside D25).
- **Ledger `## Project` line 15-16:** `casefile demo tests/fixtures/matters/<matter>` is a stage 5
  command; the chair annotates the line "(stage 5)" at close. No spec change.
- **Spec §3 step 3 ("the right card runs on each chunk")** is not contradicted: the stage 2 runner is a
  benchmark stand-in, replaced at stage 5 (D25 says so).
- **Spec §5 Run log row ("raw answer"):** `ModelError` carries the decoded reply (`raw`) so a refused
  reply is still stored (§1.11). No spec change; an as-built §11 note.

## §6b Privacy

Every fixture this round adds is invented: matter `9001.001`, claim `QRL-2025-0418`, claimant Morgan
Ashby-Vale (born 02/17/1981), lead Rosalind Mbeki-Farrow, employer Quarry Ridge Logistics LLC,
Fennimore County Hospital, Brightwater Family Medicine (Dr. Ines Castellanos-Reyes), Ridgeline Physical
Therapy, Lakeshore Imaging, Lakeshore Orthopedic Associates (Dr. Priya Okonkwo-Lind), Northgate Medical
Evaluations (Dr. Theodore Marchetti), stamps `MED0001` to `MED0008`, `EMP0001` to `EMP0003`, `DEF0001`
to `DEF0003`, wage `$912.40`. The names are compounds chosen so that no real person is plausibly
matched; the facts (a 60 or 40 pound tote, a 4 mm L4-L5 protrusion, a 2019 strain) are generic
invented clinical facts, not taken from any record. No PDF, Word file or image; text, JSON and TOML
only. The orchestrator reads every page before it is committed and confirms in its report that nothing
in it came from a real matter; the chair repeats the read at close. Test matters in `tests/` are
exercised through tmp_path copies when altered (W9 bad-key case) so the committed fixture is never
edited by a test. Scratch probes live under `$TMPDIR` only.

## §7 Questions only the owner can answer (appended verbatim to docs/loop/questions-for-owner.md)

21. What must the medical chronology, and so a benchmark answer key, contain at minimum per encounter:
    date of service, provider and facility, mechanism of injury as stated, pain scores, prior history,
    exam findings, imaging results, diagnosis, treatment and plan, restrictions and work status,
    causation and MMI statements, referrals and records referenced? The stage 2 key holds 26 facts and 5
    flags of these kinds for the invented matter 9001.001 (brief §2 W4). Which categories are missing or
    unnecessary for your practice? Interim: the 26 as listed.
22. On the Studio, where do the benchmark matters and their `key.json` live: beside the closed matters
    under `[paths].matters` (one `key.json` per matter folder), or in a separate folder outside the
    checkout passed with `casefile bench --matters`? Interim: a separate folder outside the checkout,
    same layout as `tests/fixtures/matters/`.
23. In the firm's scanned records, is the Bates stamp always one stamp per page at the bottom (the
    stage 2 fixture puts it alone on the last line), or do stamps appear top right, with a producing
    party prefix, or more than one per page? Interim: one stamp per page, last line; stage 3 reads the
    stamp from the page text with the configurable pattern (Q21).

(Questions 21 to 23 are already in the file; the Codex review raised no new owner question.)

Tuning questions (appended to docs/loop/tuning-questions.md): T-7 the quote match rule (exact after
normalisation; stage 4 ladder replaces `quotes.found_in`); T-8 bench exit on the real model (perfect only;
any pass mark below perfect is a measured decision at stage 9); T-9 one call per matter versus per page
(stage 5 pipeline replaces the runner; compare the two on the same key then); T-10 `matter.STAMP_PATTERN`
(single stamp; becomes a config key at stage 3); T-11 (new, Codex 4) a candidate fact's `text` is not
compared with its quote at stage 2, so a summary that contradicts its quote scores `found`; the §4
ladder (stage 4) is where a summary is checked against its source, and the bench line must gain a
counter for it then (the verifier's reversal probe in §4 records today's number).

## §8 Codex dispositions

Each finding checked in the code before accepting or rejecting; `file:line` values are from the tip.

| # | Disposition | Evidence and what changed |
|---|---|---|
| 1 | ACCEPTED | Measured: `CASEFILE_TOOLCHAIN=$'<checkout>/q\npathguard outside z' scripts/run.sh true` -> exit 95, **2** stderr lines (`run.sh:18` echoes `$TOOLCHAIN` with its newline). W1's number is now `newline_join_exit=95 verdict_lines=1` (lines starting `pathguard `); G1 asserts exit 95, the `; exit 95` suffix and one verdict line; seed expectation `verdict_lines=2`. |
| 2 | ACCEPTED, fixed by chair | `scripts/gemma_task.py:165` now requires `done` true and `done_reason == "stop"` (else exit 3, nothing written); lines 190-198 parse every `.py` (`ast`) and `.json` answer before any write (else exit 6, nothing written). D0.14 describes the driver as it is; R14 adds the chair's `--num-predict 64` probe. |
| 3 | ACCEPTED | `model.py:78-80` accepts `None`, 0 and negatives; `doctor.py:127` requires positive ints. G34 adds `counts_ok` and gate `bench.counts`; G38 probe 7 (`eval_count` None with valid JSON); seed (d). §1.11, D25 updated. |
| 4 | ACCEPTED as a known limit | `rules.py:65-78` is regex only; nothing in the scorer compares `text` with `quote`. No deterministic faithfulness check exists at stage 2; §1.2 states the limit, D25 prints it, the verifier's reversal probe (§4) records the number, R12 and T-11 carry it to stage 4. |
| 5 | ACCEPTED | `flags_extra` joins `perfect` (§1.7, G29, D25); `extra` facts stay non-failing because they are page-verified and the key may be incomplete (Q21). G32 cases 7 and 11, seed (e), the verifier's flag-spam probe. |
| 6 | ACCEPTED | `core.py:102` keys the lookup by the recorded messages, so a request taken from the same rows cannot miss. G37 builds the expected request from `matter.load` and the documented page-block format, independent of `benchrun.messages`, and asserts 14 page headers and every page text present; seed (f) is the reversed-pages recording -> 404. |
| 7 | ACCEPTED | `rules.py:61` skips only `unit == "question"` rules when checking text; `no-dme-ime` is `unit = "text"` (`rules.toml:7`), so `unit="question"` still finds "The IME". Seed (c) is now "drop the fact texts from the rules input" -> flawed `rules=0`; G32 case 9 covers the `about` path. |
| 8 | ACCEPTED | `model.py:67` `settings.update(num_ctx=..., temperature=...)` after the caller's options, so dropping the runner's `options` changes nothing in the request. Seed (c) is now `matter=None` in `start_run`, caught by G38's `runs.matter == "9001.001"` assertion. |
| 9 | ACCEPTED | Old order ran G24 and G26 (recording tests) before G21 (`ideal.json`). §3 is now the task numbering itself: `ideal.json` (G30) and `flawed.json` (G31) precede every consumer (G32, G35, G37, G38, G41, G42); every task lists its prerequisites. |
| 10 | ACCEPTED | G9 to G12 asked four or three files per task. Each page is one task (G8 to G21), `matter.toml` G22; the driver would accept several `--allow` (gemma_task.py:139, 172) but the protocol is one path per task (§1.17). Task count 31 -> 43. |
| 11 | ACCEPTED (chair ruling, Q28) | `config.load` is 83 lines (config.py:65-147), inside the 120-line budget, and the driver splices a def (`gemma_task.py:103`). G2 is one FUNCTION task on `src/casefile/config.py::load` with the whole function quoted; `key.json`, `ideal.json`, `flawed.json` and `matter.toml` are Gemma tasks (G25, G30, G31, G22) with a per-binder re-split and mechanical concatenation for the key. The chair writes task files, runs checks and seeds, commits. |
| 12 | ACCEPTED | `gate.main` returns the failed count (gate.py:75) and `run_capture.py:109` returns the child status, but `cmd; echo $?; grep` ends with grep's status. Every CHECK now keeps `rc=$?` and ends with `test "$rc" -eq 0`; the convention paragraph in §2 says so; a seed counts only when that status turned non-zero. |
| 13 | ACCEPTED | `socketserver.py:489` `TCPServer.server_close` closes the listening socket, so a listener count after `server_close()` cannot see a missing `shutdown()`. G42 measures `thread.is_alive()` after `shutdown(); join(timeout=5)` and before `server_close()`, prints `server_stopped=1` and asserts it; seed (b) now fails the test. |
| 14 | ACCEPTED | `runlog.open_db` (runlog.py:105-109) does `mkdir` and `sqlite3.connect` unguarded. G6 wraps every directory listing and page read in `MatterError` (`OSError`, `UnicodeDecodeError`); G7 adds the page-is-a-folder and not-UTF-8 refusals (11 of 11); G39 catches `(OSError, sqlite3.Error)` around `open_db` and the runner (exit 2, `bench: cannot open run log`); G41 adds `bench_exit_nolog=2`; seeds W3 (d), W9 (d). |
| 15 | ACCEPTED | `model.py:76` raises without the reply; `runlog.record_answer` (runlog.py:67) takes `status="failed"`. G33 rewrites `model.py` so `ModelError(message, raw=None)` carries the decoded reply from the five post-200 raises; G34 stores it as a `failed` answer row; G38 probe 6 (`incomplete` mode) and seed (e). §1.11 and a §6 as-built note. |
| 16 | ACCEPTED (limit recorded) | `rules.toml:56` `cite_pattern` matches bracketed forms only, so "See page 12" in a candidate `text` is `rules=0`. §1.18 now says R1-20 is reachable through `text` and `about`; the verifier probe records the number; the rule change is the owner's playbook entry, and R1-20 stays open in the Librarian. |

No finding went to the owner: none turned on a fact only the owner holds. Accepted 16 (two as
documented limits, one fixed by the chair), rejected 0, owner 0.
