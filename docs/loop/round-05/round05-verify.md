# Round 5 blind verification (stage 5: case file, merge, medical memo)

VERDICT: PASS (R5-1, R5-2, R5-3 and V. ticked; no blocking finding; three low findings below)

Verifier: Opus 5.5, fresh agent with no part in the round 5 brief, build or fixes. Branch `loop/round-05`, tip
`ff79699`. Blind: the ledger's own wording, the tip and `.workflow/scratch/round05-mutated-lines.txt` only, until every item
was ticked. Every run went through `scripts/run.sh`, one blocking call at a time. Invented fixtures only; the model was the
stand-in (`tests/fakemodel/`) on an ephemeral port; 127.0.0.1:11434 was never contacted.

## Measured numbers (own runs, verbatim)

| Claim (ledger CHECK) | Probe | Own line |
|---|---|---|
| R5-1 exit test, nine lines | `pytest -q -s tests/test_stage5_exit.py --basetemp=/private/tmp/claude-501/v5/exit` | `stage5 exit=0 runs=4 of 4 memos=3 of 3 answers=+4 casefile_lines=48 chain_ok=1 server_stopped=1` (all nine lines equal to the test's EXPECTED) |
| R5-1 case file | `pytest -q -s tests/test_facts.py` | `casefile_ok=14 of 14` |
| R5-1 memo | `pytest -q -s tests/test_memo.py` | `memo_docx_ok=14 of 14 memo_refused=2 of 2 memo_changed=1 memo_reason_exempt=1` |
| R5-1 pages, pipeline | `pytest -q -s tests/test_pages.py tests/test_pipeline.py` | `pages_ok=10 of 10`, `chunks_ok=8 of 8 pipeline_ok=5 of 5` |
| R5-1 status, intake memo | `pytest -q -s tests/test_status.py tests/test_memo_intake.py` | `status_ok=6 of 6 binder_refused=1`, `memo_intake 9002.001 chunks=1 read=5 open=1 facts=5 gaps=1 label_ok=1 exit=1` |
| R5-1 bench pipeline | `pytest -q -s tests/test_bench_pipeline.py` | `bench_modes=12 of 12`, `reply_rows=9 of 9` |
| R5-1 card | `pytest -q -s tests/test_extract.py` | `card_version=4ab2bdb30535 card_name=bench_extract docx_import=1` |
| R5-2 | `pytest -q -s tests/test_gates.py tests/test_rules.py` | `gate_cases=31 of 31`, `cite_forms=11 of 11`, `109 passed`; case `mixed_chunk` at `tests/test_gates.py:126` |
| R5-3 detail | `pytest -q -s tests/test_bench_detail.py tests/test_benchscore.py` | `invented_kinds=2 of 2 rule_excerpt_ok=1` |
| R5-3 status by stamp | own driver: stand-in on port 0, `casefile memo` (replay) then `casefile status --config <temp> --matter 9001.001` on a temp copy of 9001.001 | `status 9001.001 pages=14 read=13 failed=0 uncited=1 empty=0 open=1 facts=31 conflicts=5 gaps=4 outputs=memo:current` / `  open: DEF0001 (defense-report/001): uncited: no fact or flag cites defense-report/001` |
| Suite | `pytest -q` | `652 passed in 51.90s` (baseline was 537 at round 4; growth is round 5 tests) |
| Gate | `python -m casefile.gate` | `0` (`gate prose PASS dashes=0 files=191`) |
| Unused imports | `python scripts/unused_imports.py src tests scripts` | `unused_imports=0` |
| Suite time | `scripts/suite_time.sh 3` | `suite_time runs=3 max=51.57 verdict=PASS` |
| Bench flawed | `casefile bench --config config.example.toml --matters tests/fixtures/matters --candidate tests/fixtures/bench/flawed.json` | exit 1, `bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2 flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14`; detail `(quote not on the page)` and `(no such page)` |
| Bench ideal | same with `--candidate tests/fixtures/matters/9001.001/ideal.json` | exit 0, `bench 9001.001 model=candidate found=29 of 29 missed=0 invented=0 extra=2 flags=9 of 9 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14` |
| Stage 1 to 4 | inside the suite run | `exit=0 verdicts=8 fails=set() test_jobs=1`; `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`; `stage3 exit=1 pages=6 ids_ok=6 of 6 stamps_ok=6 of 6 text_ok=6 of 6 must_ok=5 of 5 empty=1 failed=0 min_ratio=1.000`; seven `stage4` lines ending `stage4 exit=0 gates=6 of 6 cases=14 of 14 runs=+14 answers=+21 empty_saved=0 server_stopped=1` |
| Intake | inside the suite run | `intake 9002.001 scan pages=6 ok=5 empty=1 failed=0 stamps=6 had_text=2 ocr_added=4` |
| Doctor schema | `casefile doctor --config <temp config, host a closed ephemeral port>` (not the default config) | `doctor runlog_schema PASS schema=2 triggers=21 (counted)` |
| No test reaches 11434 | static: `grep -rn 11434 tests src scripts` | only config refusal cases in `tests/test_config.py` (`localhost`, `[::1]`, `https`, a path suffix); isolated default host is `127.0.0.1:9` |

All numbers reproduce the ledger's CHECK block exactly.

Deviation from the instruction: `config.example.toml` sets `matters = "~/Cases"` and the host to 11434, so `casefile memo`,
`status` and `doctor` ran against a temp config in `$TMPDIR` (matters and state in `$TMPDIR`, host the stand-in's port).
`casefile bench --candidate` used `config.example.toml` as told (it calls no model; `--matters` overrides the folder).

## Seeds (none from the mutated list; each: backup, edit, full suite, `cp -p` back, `cmp` clean)

| # | File and function | Defect seeded | Result |
|---|---|---|---|
| 1 | `memo.py` `_fact_paragraphs` (not in the list) | `if page_id != heading_page:` to `if False and ...`: a reading from another page loses its `of [cite X]` | RED: `tests/test_memo.py::test_memo` "check 10 red" (run with `-x`) |
| 2 | `facts.py` `merge` reading dedupe | `(item["text"], page.page_id) not in zip(...)` to `item["text"] not in fact.readings`: the same reading on a second page is not recorded for that page | RED: `test_facts.py::test_casefile` ("new page lost its..."), `test_round05_fixes.py::test_m3_same_reading_on_another_page_is_retained`; `2 failed, 650 passed` |
| 3 | `pages.py` `load`, intake branch (the list names only the status and identity guards) | drop `or meta["pages"] != len(records)`: a binder missing a page file loads silently | RED: `test_pages.py::test_pages[count]` (DID NOT RAISE); `1 failed, 651 passed` |
| 4 | `status.py` `snapshot` (list names other status lines only) | open items keep only `failed` and `uncited`: `empty` and `unread` pages vanish | RED: `test_memo_intake`, `test_h2_status_joins_latest_coverage_to_casefile_runs`, `test_status_six_cases`, `test_empty_binder_keeps_intake_order`; `4 failed, 648 passed` |
| 5 | `memo.py` `check` (the all/any seed was in `gates.py`, not here) | `stamped=all(...)` to `any(...)`: the memo's own words judged as fully stamped | RED: 10 tests in `tests/test_memo.py` incl. `test_memo` (`MemoError: bates-cites`); `10 failed, 642 passed` |

After seed 5: `git status --short src` empty; `cmp` printed nothing for all five files. No test gap found.

## What the memo shows

Produced twice: by the exit test (`/private/tmp/claude-501/v5/exit/test_stage5_exit0/matters/9001.001/outputs/memo.docx`,
the run 4 memo) and by my own driver after one replay run (`/private/tmp/claude-501/v5/drive1/.../outputs/memo.docx`).
Read with python-docx through `scripts/run.sh python`.

- Structure (driver memo, 108 paragraphs, no tables): Title `Medical memo: matter 9001.001`; `Built 2026-10-28 from case
  file entry 41; playbook pb-ca16b0882a97; model qwen3.8:27b`; Heading 1 sections in order: What changed since the last
  memo (`First memo for this matter`), Outputs out of date (`none`), Open items, Conflicts, Gaps and missing records,
  Verified facts by record; one Heading 2 per page, `Medical page MED0001 (medical/001)` and so on.
- Facts against `key.json`: `key_facts=29 of 29 missing=[]` (each as `"<quote>" [cite <stamp>]`); extras beyond the key
  are `Date of hire: 08/02/2021` (EMP0001), `Lift up to 50 pounds repeatedly during the shift.` (EMP0002), and in the run 4
  memo also the DEF0001 one-page answer. `quotes_on_cited_page=32 bad=0`: every quote is verbatim on the page its stamp names.
- Cites: Bates form `[cite MED0001]` throughout; quote and cite are separate runs.
- Conflicts and gaps: `key_flags=9 of 9` with the key's exact cite sets and `about` text: conflicts G1, G2, G3, G6, G9 and
  gaps G4, G5, G7, G8. The Conflicts section opens with `Pages read in 1 run; conflicts and gaps are checked only between
  pages sent to the model together.` (the chair's ruled sentence).
- Open items: driver memo `DEF0001 (defense-report/001): uncited: no fact or flag cites defense-report/001`, the reason a
  separate run; the DEF0001 heading below says `Open item: uncited (see Open items).`; run 4 memo says `none`.
- Labels (Q48): every model sentence is its own paragraph starting `Model's reading: ` (31 fact readings plus 9 flag
  readings in the driver memo); no paragraph carries model text unlabelled. The `Conflict between ...` and `Gap at ...`
  lines are the app's wording, with the pairing taken from the model (the critic raised this as an owner question).
- DEF0002 reads `No fact was quoted from this page.` though two conflicts cite it; accurate, but the heading does not
  point to those conflicts (owner question 54 territory, not graded).

## Findings (none blocking)

- L1 (low, new) No-reply wording leaks memo language into other commands. `src/casefile/model.py:57-58` ends every
  no-reply reason with `; the page stays open until a later run reads it`. Seen: `casefile doctor` prints `doctor
  ollama_loopback FAIL no reply from the model server (connection refused); the page stays open until a later run reads it
  | do: start the Ollama app` (no page is involved); `casefile memo` with the server down prints `memo: cannot run: no reply
  from the model server at http://127.0.0.1:52810: no reply from the model server (connection refused); the page stays
  open until a later run reads it` and exits 2 (the phrase "no reply from the model server" twice). Fix: keep the page
  clause in the gate's reason (`gates.py:315` already adds it) and drop it from `model.py`'s message, or have
  `memo_job.py:99` print the reason without its own prefix; re-pin `tests/test_fix_cycle2.py` (doctor) accordingly.
- L2 (low, unlogged design call) The memo's per-page placeholder lines (`No fact was quoted from this page.`, `Open item:
  <state> (see Open items).`), the unstamped-page warning paragraph and the closing section `Facts on pages not in this
  matter` are chair rulings in `docs/loop/round-05/round05-code-review.md` (M1) and fix cycle 2, but spec §9 D41 still
  lists only the six sections. Standing rule: every design change goes in spec §9. Fix: amend D41 at close.
- L3 (low, process) The fixture folder `tests/fixtures/matters/9001.001/.claude/.cc-writes` (untracked, harness made) is
  copied by `shutil.copytree` into every exit-test matter; harmless today (dot names are skipped by `pages.load`), noted.

## Process notes

- `docs/loop/tuning-questions.md` showed as modified during my session (T-20 to T-22, mtime 03:47); not my edit, left
  untouched; the chair's uncommitted work.
- `casefile bench --config config.example.toml` writes its run log under the checkout's `state/` (gitignored), as the
  example config says.
- My edits: `.workflow/LEDGER.md` (ticks and evidence under `## Round 5`) and this file only. Scratch under
  `/private/tmp/claude-501/v5/` and the session scratchpad.

## Reconciliation (opened after every item was ticked)

- Output critic (`round05-critic.md`, tip 320c551): its key grade (29 of 29, 9 of 9, nothing invented) matches mine. Its
  M1 (memo lists itself stale), M2 (bare page headings), L1 (plurals and readings count), L2 (empty sections), L3 (the
  rule's instruction as warning) and L4 (lowercase) are all fixed at ff79699 in the memos I read: `Outputs out of date:
  none`, explained page lines, `Medical page ...`, `Built ...`. L5 (`defense report` framing) is still in the output
  (G9 reading and the `Defense-report page` headings), held as owner question 58.
- Code review (`round05-code-review.md`): my seed 1 and seed 2 attack the M3 fix (reading page provenance) from the
  render and the merge side; both went red, so that fix has teeth. Seed 3 and seed 4 hit code no reviewer flagged and were
  still caught. M4 (edited last line loads clean) remains a recorded limit; not re-tested.
- Fix cycle 2 (`round05-fix2.md`) reports `652 passed`, gate `0` and nine unchanged `stage5` lines; all reproduce.
- W3b (`round05-W3b.md`) changed the no-reply message and re-pinned the doctor assertion to it; no report or review
  noticed the page clause in the doctor line (my L1).
- The chair's CH-1 seed (`facts.py` seq check) and the builders' seeds are in the mutated list; none of my five overlaps.
