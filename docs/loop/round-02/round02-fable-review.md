# Round 2 Fable code review: the Gemma build against the Sonnet control

Reviewer: Fable 5.1, 2026-10-27, between 8a and 8b. Owner question Q28: what does a 7.5B local
builder (`gemma4:e4b-it-qat`, one task at a time under the Opus orchestrator) produce, compared with
Sonnet 5.5 given the same brief? Gemma side: `loop/round-02` (tip 8175226). Sonnet side:
`control/r2-sonnet` (43ef0d9), an independent build of W3, W5 code, W6 and W9 from 2dfa4f5. Fixtures
are byte-identical on both branches (`git diff --stat control/r2-sonnet loop/round-02 -- tests/fixtures`
is empty), so this is a comparison of code and tests only. Written before reading the Codex review or
the build report; the overlap note at the end was added afterwards.

Evidence: all 17 round 2 tests pass on the current checkout
(`scripts/run.sh pytest -q -s` over the ten round 2 test files: `17 passed in 1.12s`; the printed
numbers match the brief: `quotes_ok=8 of 8`, `refusals=11 of 11`, `key_refusals=10 of 10`,
`candidate_refusals=7 of 7`, `score_cases=11 of 11`, both bench lines exact,
`bench_exit_perfect=0 ... bench_exit_nolog=2`, `benchrun_modes=7 of 7 answers_ok=1 answers_failed=6
failures=6`, `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`). Edge cases below were traced with
a throwaway script in the scratchpad against the Gemma modules and Sonnet's `benchkey.py` loaded
standalone; the Sonnet test suite was not run (no checkout of that branch in this tree).

## 1. Verdict

The Gemma code is fit to merge after small fixes, and none of the fixes is a logic change. Every
signature, message, exit code, guard order and printed line in the brief's §2 is implemented exactly;
the runner (W7, W8) and the stage 2 exit test (W10), which have no Sonnet counterpart, are faithful and
fail closed on every probe. The two medium findings (a key whose flags or facts collide on their
matching identity can never score perfect, and the loader accepts such a key; a `matter.toml` that is
not UTF-8 escapes the loader as a traceback, exit 1 instead of 2) are shared line for line with the
Sonnet build and come from the brief's own algorithm and except clause, not from either builder; the
second was found by Codex, not by me. What separates the two builds is
hygiene, not correctness: Gemma dropped `from exc` at five of the six sites the brief spelled it out,
left 33 lines of trailing whitespace, imported names it never used in eight of ten test files, echoed
the task's numbered steps as comments, and leaked prompt framing into committed test code ("Mock bench
function based on background description"). Sonnet's build is the cleaner artifact (zero lint noise,
idiomatic helpers, a two-pass name check) but is not more correct: it accepts a non-string flag id that
Gemma refuses, and its tests write fixtures without an encoding. Functionally the two are the same
program; a reader who did not know would guess the Gemma side was written by a careful junior and the
Sonnet side by a senior, and would find the same bugs in both.

## 2. Correctness findings in the Gemma code, most severe first

No high finding. Severity is judged against D25's fail-closed promise (a bad key is exit 2 before any
score) and the Librarian pre-flight.

**F1 (med, CONFIRMED). `src/casefile/benchscore.py:69-82` with `src/casefile/benchkey.py:89-122`.**
A key whose flags repeat a `(kind, cite set)` pair is accepted by the loader and can never score
perfect: `key_sets` is a dict keyed on the pair, so two key flags collapse to one, `flags_total` stays
2 and `flags_found` tops out at 1. Scenario: a key with G1 and G2 both `gap` on `["MED0002"]` (two
different gaps on one page, a realistic authoring choice) and a candidate that reports both; traced
line `flags=1 of 2 flags_missed=1`, `perfect=False`, and `flags_missed_ids=()`, which contradicts the
count on the same line (the ids are derived from the collapsed dict, the count from `len(key.flags)`).
The bench then fails the ideal answer with no message naming the key as the cause. Fix: in
`benchkey.load`, refuse a duplicate `(kind, frozenset(cites))` pair as a `BenchKeyError` so the exit
is 2 with a reason, and derive `flags_missed_ids` from `key.flags`. Sonnet: same defect (its
`benchscore.py:73-76` is the same algorithm and its loader accepts the same key, traced); its
`flags_missed_ids` comprehension (`benchscore.py:92-94`) also yields `()` here. Root: the brief's G29
algorithm; neither builder questioned it. The Codex review (CX-5, read after this was written) adds
the fact-side twin, CONFIRMED by reading `benchscore.py:58-67`: two key facts with the same cite and
the same normalised quote under different ids match only the first (`hit` is the first key fact in
key order), so the second is missed by every candidate; same in Sonnet's `next(...)` at
`benchscore.py:65-68`. The loader fix is the same: refuse a duplicate `(cite, normalize(quote))` pair.

**F1b (med, CONFIRMED; found via Codex CX-7 after my own pass, so it is not an unanchored finding).
`src/casefile/matter.py:54-58`.** `tomllib.load` on a binary stream raises `UnicodeDecodeError` for a
manifest that is not UTF-8, and the except clause names only `OSError` and `TOMLDecodeError`, so the
error escapes `load` and `bench.main` as a traceback. Traced: a `matter.toml` ending in a `0xff` byte
gives `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff` out of `matters.load`; through the CLI
that is exit 1 (traceback), where D25 and the brief ("every exception that leaves `load` is a
`MatterError`"; "a bad key, an unreadable matter ... is exit 2 before any score") want exit 2 with a
reason. The page read at `matter.py:110-113` catches `UnicodeDecodeError`; the manifest read does not.
Fix: add `UnicodeDecodeError` to the tuple at line 57 and a `page-not-utf8` style refusal for the
manifest in `tests/test_matter.py` (the brief's eleven refusals had none for the manifest, which is
why both suites are green). Sonnet: same defect, identical clause at `matter.py:57`.

**F2 (low, CONFIRMED). `src/casefile/matter.py:58, 79, 99, 113` and `src/casefile/benchkey.py:46`.**
The brief wrote `raise MatterError(f"{path}: {exc}") from exc` and Gemma dropped `from exc` at five
of the six sites inside an `except ... as exc` (kept only at `benchcandidate.py:85`). Behaviour under
the tests is identical because every caller catches the wrapper, but an uncaught `MatterError` from a
future caller prints "During handling of the above exception, another exception occurred", which
says the loader crashed while handling an error rather than that it translated one. Sonnet: no, all
six sites chain explicitly.

**F3 (low, CONFIRMED). `src/casefile/matter.py:81-83`.** Any entry under `records/` that is not a
listed binder refuses the matter as `unlisted binder folder <name>`, including a Finder `.DS_Store`
file (traced: `unlisted binder folder .DS_Store`). Fail closed is what the brief asked ("any entry"),
but the owner's Mac will produce that file the first time Finder opens the folder, and the message
then calls a file a folder. Sonnet: same (`matter.py:72-74`). Worth a chair ruling, not a builder fix.

**F4 (low, CONFIRMED). `src/casefile/matter.py:89-137`.** A binder listed twice in `matter.toml`
reads its pages twice and refuses with `001.txt: duplicate Bates stamp MED0001`, naming a page that is
not duplicated. The toml check at `matter.py:71` should refuse repeated names. Sonnet: same
(`matter.py:77-103`).

**F5 (low, PLAUSIBLE). `src/casefile/matter.py:102-113`.** Page names are validated one at a time
while reading, so a folder whose `001.txt` has a bad stamp and which also holds `notes.txt` reports
the stamp, not the stray file; the brief's wording ("entries sorted by name must be exactly ...")
reads as a check on the listing before any read. Both outcomes are a `MatterError`, so only the
message differs. Sonnet validates the whole listing first (`matter.py:82-86`) and then reads.

**F6 (low, CONFIRMED). `src/casefile/benchkey.py:74` and `:119`.** "Nonempty string" admits a
whitespace-only `text` or `about` (traced: a fact with `"text": "   "` loads). A whitespace-only
`quote` is refused by `found_in` (normalises to empty), so this only reaches the firm-rule input,
where it is harmless. Sonnet: same (`benchkey.py:39-40`).

**F7 (low, CONFIRMED by reading). `tests/test_bench_cli.py:19-26, 48-56`.** The CLI helper carries
three false comments ("Mock bench function based on background description", "In a real test
environment, this would call the actual CLI runner", "We rely on the provided implementation
structure for testing purposes"): the function is the real runner. The bad-key step wraps the edit
in `if data and 'facts' in data and data['facts']:`, so a key in an unexpected shape would be
written back unchanged; the test still goes red (exit 0 is not 2), so it is not fail-open, but the
guard exists only to avoid a KeyError the test should want. `open(key_path, 'r')` and `'w'` have no
encoding (lines 48, 55) where every other file in the repo passes `encoding="utf-8"`. Sonnet: no.

**F8 (low, CONFIRMED by reading). `tests/test_matter.py:32`.** `p.name.split('/')[-1]` is a no-op
(`Path.name` never holds a slash) and `pytest` and `Path` are imported and unused. Unused imports
appear in eight of the ten Gemma test files (`test_matter` Path, pytest; `test_benchkey` pytest;
`test_benchcandidate` pytest; `test_benchscore` Path; `test_bench_cli` Path, pytest;
`test_fixture_matter` Path; `test_benchrun` Path, sqlite3; `test_stage2_exit` Path); trailing
whitespace on 33 lines across the Gemma source and tests. Sonnet: zero of each.

**Sonnet-only, for the record.** (S1, low, CONFIRMED) `benchkey.py:82`: a flag `id` is never checked
to be a nonempty string; `{"id": 7, ...}` loads and `Flag.id` is an `int` against its `str`
annotation (Gemma refuses it at `benchkey.py:94-96`; the brief's flag message does not say "nonempty
strings", so Sonnet read it literally). (S2, low, PLAUSIBLE) eight `write_text` calls in the Sonnet
tests pass no encoding (`test_matter.py:11, 16, 31`, `test_benchkey.py:29`, `test_bench_cli.py:56`,
and others); the loader reads UTF-8, so on a non-UTF-8 locale the curly-quote page in
`test_benchkey.py:13` would be refused as not UTF-8. macOS defaults to UTF-8, so it passes here.

**Gemma-only modules (W7, W8, W10), reviewed on their own.** `benchrun.py`, `tests/fakemodel/bench.py`,
`tests/fakemodel/__main__.py`, `tests/test_benchrun.py`, `tests/test_fakemodel_bench.py`,
`tests/test_stage2_exit.py` and the `model.py` change: no defect found. The `model.py` diff is exactly
the brief's (the `raw` attribute and the five two-argument raises, nothing else). The runner's guard
order (truncation, counts, shape) is the brief's; each guard records a failed answer row with the
counts and a failure row, and returns `pages_failed = n`. Traced with the model unreachable (port 9):
`bench.model: <urlopen error [Errno 61] Connection refused>`, exit 1, one run row, one failure row,
no answer row, which is the brief's rule for a reply never received. `_fail` is a sensible helper the
brief did not spell out. `test_benchrun.py`'s `patched()` wrapper and the ordered gate list are strong
checks; its `r.failure.startswith(...)` at lines 59, 65, 71, 79, 98 would raise `AttributeError`
instead of asserting if a guard were dropped (still red, less readable). `test_stage2_exit.py`
mirrors the stage 1 test, measures thread liveness before `server_close()`, and prints before
asserting as the CHECK needs.

## 3. Side by side per module

**quotes.py.** Identical code, both verbatim from the brief (Gemma wraps the docstring at 100
columns, Sonnet does not). Tests: both have eight cases and the `normalize` assertion; Gemma's cases
are closer to real page text and it keeps `normalize` in its own test; Sonnet's are terser. Tie.

**matter.py.** Same refusals, same messages, same loader shape. Sonnet is better: `from exc` on all
four wrapped sites, a `_list` helper instead of two copies of the try, and the listing validated
before any read (F5). Gemma carries nine numbered step comments that restate the brief
(`# 2. If not meta.is_file(): f"{meta}: matter.toml not found"`) above one-line bodies. Tests: the
same eleven refusals in both, both counted in a loop (the brief's `pytest.raises` per case was
dropped by both in favour of the printed count); Gemma's `make` nests the root under `tmp_path /
"matter"` and keeps the happy path and refusals in separate tests, which reads better; Sonnet's
`make` matches the brief's "returns the root" literally. Both suites catch every W3 seed. Sonnet,
narrowly.

**benchkey.py.** Both exact on messages and order. Gemma checks the flag id is a nonempty string
(Sonnet does not, S1) but drops `from exc` (F2) and checks the fact keys in two steps where one
`all()` would do. Sonnet's `_nonempty` helper is the idiom of the surrounding code. Tests: both
have the ten refusals; both match "not JSON" on the `Expecting` text of `JSONDecodeError`; Gemma's
happy path also asserts the second fact's id and the flag's cite tuple. Tie on correctness, Sonnet
on readability.

**benchcandidate.py.** Near-identical; Gemma's is the only Gemma module that keeps `from exc`.
Gemma catches `json.JSONDecodeError`, Sonnet `ValueError` (its superclass); for a `str` input they
are the same set. Tests: both seven refusals; Gemma's cases are named functions, Sonnet's are inline
lambdas over `json.dumps`; both go through `parse_text` at least once. Tie.

**benchscore.py.** Same algorithm, same F1. Gemma's `flags_missed_ids` is derived from the
collapsed dict, Sonnet's from `key.flags`; the two agree except on a duplicated pair, where both
are wrong in the same direction. Sonnet's `next(..., None)` is one line where Gemma's loop is five.
Tests: eleven cases each with the same checks, both run the shipped ideal and flawed fixtures to the
exact lines; Gemma collects results then checks, Sonnet checks inline; neither names the failing case
in its assert, so a red run needs a print to locate. Both catch every W6 seed. Tie.

**bench.py.** Same control flow, same exit codes, same one-line reasons. Sonnet's `fail()` closure
removes nine `print ... return 2` pairs; Gemma's `one_line` is a public name without a leading
underscore where Sonnet's `_one_line` matches `gate.py`. Gemma's eight step comments (`# 1. Load
Config`) are noise. Sonnet's `run_model` stub raises `NotImplementedError`, which is the honest
placeholder for a measurement run. Tests: five exit codes in both with the same assertions; Gemma
prints the `bench_exit_` line before asserting (the CHECK's grep then has a line even on a red run),
Sonnet prints after four asserts, so a wrong first line leaves no count on the log; Gemma uses the
bare `casefile` as `tests/test_cli.py` does, Sonnet pins `Path(sys.executable).parent / "casefile"`,
more robust but a different idiom from the surrounding tests; Gemma's helper carries false comments
(F7). Sonnet on readability, Gemma on CHECK discipline; tie overall.

**cli.py.** The diff is byte-identical on both branches.

**The tests as a whole.** Both suites would catch a real regression in every counter and exit
branch (the brief's seeds were run by the chair on the Gemma side; by reading, Sonnet's would go red
on the same seeds, since the assertions are the same). Neither was written to agree with its code:
the shipped-fixture lines and exit tuples are fixed strings from the brief, not computed from the
module under test. Gemma's leftover comments and imports make its tests look less finished than
they are; Sonnet's missing encodings are the one latent portability fault.

## 4. Quality scorecard (1 to 10)

| Axis | Gemma | Evidence | Sonnet | Evidence |
|---|---|---|---|---|
| Correctness | 7 | No defect of its own; shares F1 (unwinnable key accepted) and F1b (non-UTF-8 manifest is a traceback, exit 1 not 2) with Sonnet; refuses a non-string flag id; dropped `from exc` costs diagnostics, not behaviour | 7 | Same F1 and F1b, same lines; accepts a non-string flag id (S1); tests write fixtures without an encoding (S2) |
| Brief fidelity | 8 | Every signature, message, guard order, exit code and printed line exact; `from exc` dropped at 5 of 6 sites; `pytest.raises` per case replaced by a counting loop | 9 | Same exactness plus every `from exc`; listing validated before reading; the no-config case uses the env path instead of `--config` and the summary line prints after asserts |
| Test strength | 7 | Catches every seed; counting loops do not name the failing case; one helper guarded with a no-op condition; AttributeError in place of an assert on five probe lines | 7 | Same assertions and seeds; same unnamed cases; `bench_exit_` line printed only after four asserts pass |
| Readability | 5 | 41 numbered-step or prompt-leak comments, 33 trailing-whitespace lines, unused imports in 8 of 10 test files, a no-op `split('/')`, a local `import subprocess` | 9 | Zero lint noise; `_list`, `_nonempty`, `fail()` helpers match `gate.py` and `config.py`; one local `import json` in `test_benchscore.small` |

## 5. Patterns typical of the small model, for a future round's checklist

1. **It drops `from exc`** even when the instruction prints it: 5 of 6 sites. Grep every
   `except ... as exc:` block for a `raise` without `from exc` before accepting a loader task.
2. **It restates the task as comments.** Numbered step comments (`# 1. root = Path(root); meta =
   ...`, `# Guard 1: Check done_reason`) above bodies that say the same in code; nine in `matter.py`,
   eight in `bench.py`. Ask for "no comments that restate the line below" in the task text, and strip
   them in review.
3. **It leaks the prompt into committed code.** "Mock bench function based on background
   description", "Assuming ROOT and write_config are available via conftest", "Constants defined in
   background", "# Case 2" annotations. Grep new files for `background`, `assuming`, `in a real`, `we
   rely` before commit.
4. **It imports what the task mentions, not what the code uses.** `pytest` imported in four tests
   that never call it; `Path` in six. Run an unused-import check on every Gemma file (the scratch
   `ast` scan above took one call).
5. **Trailing whitespace on blank lines inside blocks**, 33 lines. A `grep -nE ' +$'` gate on Gemma
   output would be cheap.
6. **Defensive conditions that can only hide**: `if data and 'facts' in data and data['facts']:`
   around a one-line edit; `p.name.split('/')[-1]`. When a test edits a fixture, the edit must be
   unconditional so a wrong path raises.
7. **It validates while consuming** rather than validating the listing first (F5): acceptable here,
   but a pattern to watch when the order of refusals matters.
8. **`open()` without an encoding** when the line is not copied from the brief (two sites); the
   brief's own `read_text(encoding="utf-8")` was copied faithfully everywhere.
9. **Where it had exact strings it was exact.** Not one message, format line, exit code, gate name or
   guard order deviates. The model's weakness is idiom and hygiene, not semantics; the orchestrator's
   protocol of writing out every string paid off, and the review budget should go to the lines the
   brief did not spell out.
10. **Not observed this round**: literal `\n` or quote characters in the wrong place, `assert True`
    style weak asserts, swallowed exceptions, or a test that computes its expected value from the
    code under test. The `--function` and FILE-only driver (`scripts/gemma_task.py`) and the chair's
    seeds appear to have held those off.

## Overlap with the Codex review and the build report

(Added after sections 1 to 5 were written; `round02-codex-review.md` and `round02-build-report.md`
were opened only then.)

- **Codex CX-5 is my F1**, and Codex adds the fact-side collision, which I had seen but not written
  down; it is now in F1 as CONFIRMED by reading. Same fix: refuse both collisions in `benchkey.load`.
- **Codex CX-7 I missed.** It is now F1b, confirmed by trace on the Gemma loader; Sonnet's clause at
  `matter.py:57` is identical, so the control build has it too. Both suites are green because the
  brief's eleven refusals cover a non-UTF-8 page but not a non-UTF-8 manifest.
- **Codex CX-6 (a 200 reply that `_request` cannot decode leaves no answer row)** is the brief's own
  design (G33: `raw` is `None` when the reply was not decoded; G34 records an answer only when
  `exc.raw is not None`). Gemma built what was asked; whether D25's "every received reply" means
  "every decoded reply" is a chair ruling. A fix would store the raw bytes (`payload[:N]`) on the
  `ModelError` from `model.py:59-65` and record them; not a builder error.
- **Codex CX-2 (positive counts do not prove the prompt was consumed)** is a spec §4.1 design point
  against the brief's §1.3 sizing (14 pages, about 5 k tokens, inside 65536); not a builder error on
  either side and outside what the brief asked W7 to guard. Worth a tripwire in the stage 3 brief when
  real page counts arrive.
- **Codex CX-1, CX-3, CX-4** are in `scripts/gemma_task.py`, the chair's driver, outside this review's
  scope; the tip commit 8175226 says the chair fixed them, and the diff I read from 2dfa4f5 (proxy-free
  opener, FILE-answer-on-function-task refusal, link-or-outside-checkout refusal) matches.
- **Build report item 5** already lists the dropped `from exc` (my F2), the `.startswith` on a
  possibly `None` failure (my W8 note) and seeds that go red by exception rather than by count (same
  note). Its "G4 writes curly quotes as literal characters" is the brief's own `CURLY` dict and is not
  a defect; Sonnet's `quotes.py:3` is the same line.
- **Build report totals** (43 tasks, 26 first-try, 17 with retries, 2 re-splits, 0 Sonnet fallbacks)
  are consistent with what the code shows: nothing semantically wrong that a test could catch survived
  the CHECK and seed loop, and what survived is the class of thing no test looks at (chaining,
  whitespace, imports, comments). That is the answer to Q28 in one line: with exact strings and a
  seed loop, the small model's errors move out of the logic and into the hygiene.
