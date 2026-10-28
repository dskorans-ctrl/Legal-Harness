# Round 5 build brief: stage 5 case file, merge and medical memo (plus R5-2, R5-3)

Branch `loop/round-05` at `4755170` (working tree: modified `.workflow/LEDGER.md`, untracked `.agents/`,
`.claude/worktrees/`, `AGENTS.md`; leave them). Scope: ledger R5-1 (spec §7 stage 5: "the test matter produces a
memo with cites, conflicts and open items"), R5-2 (R1-20 unbracketed cites, verifier L2 digit check inside a bracketed
cite, verifier L1 mixed stamped and unstamped chunk), R5-3 (critic M2 open items by stamp, critic L3 bench invented
kinds and rule excerpts). Tiers (owner Q46): Opus 5.5 orchestrates, runs the output critic and the blind verifier;
Codex `gpt-6.1-sol` through `codex exec -s workspace-write -c sandbox_workspace_write.network_access=true` writes
every line of code and every fix (builders do not commit; the chair re-runs every CHECK and seed, runs the gate and
commits); a fresh Fable agent does the plan review and, later, the code review, read-only; Fable writes and revises
the brief. The owner is offline (Q48): no check-in; §7 questions are held with fail-closed interims, pending veto.
Privacy: every page, name, stamp, quote, answer and number below is invented (§6b). The model is the stand-in
`tests/fakemodel/` in every test and probe; an `ollama` listens on 127.0.0.1:11434 on this Mac (owner's local
worker) and no agent sends it anything (HANDOFF).

Measured on the tip 2026-10-28 by this architect, inside the sandbox, through `scripts/run.sh`: gate prints `0`
(`gate prose PASS dashes=0 files=172`); `casefile bench --config config.example.toml --matters tests/fixtures/matters
--candidate tests/fixtures/bench/flawed.json` -> exit 1, `bench 9001.001 model=candidate found=26 of 29 missed=3
invented=2 extra=2 flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14` with the six detail lines;
`--candidate tests/fixtures/matters/9001.001/ideal.json` -> exit 0, `found=29 of 29 ... flags=9 of 9 ... pages_failed=0
of 14`; `pytest -q -s tests/test_stage1_exit.py tests/test_stage2_exit.py tests/test_stage3_exit.py
tests/test_stage4_exit.py` -> `8 passed`, `exit=0 verdicts=8 fails=set() test_jobs=1`, `stage4 exit=0 gates=6 of 6
cases=14 of 14 runs=+14 answers=+21 empty_saved=0 server_stopped=1`. Probe over the fixture (project interpreter):
the 9001.001 extraction prompt is 19462 bytes against a 57344 byte budget (one chunk); `ideal.json` holds 31 facts,
all 31 distinct by `(cite, quotes.fold(quote))` and by `fold(quote)` alone, 9 flags (5 `conflict`, 4 `gap`) with 14
cite entries; the extraction card's version is `4ab2bdb30535`, its text 920 bytes.

## §0 Drift (every premise verified in the code on `4755170`, not in a report)

- D0.1 **No Word library.** `scripts/run.sh python -c "import docx"` -> `ModuleNotFoundError: No module named
  'docx'`, exit 1. `pyproject.toml:6-9` lists `pillow` and `pypdf` only; `uv 0.11.30`. Spec §5 "Outputs: python-docx
  templates" and §3 step 6 "download as Word documents" are not built. `privacy.py:7` SUFFIXES holds `.docx` and
  `.gitignore` ignores `*.[dD][oO][cC][xX]`, so a produced memo may never sit in the checkout; `tests/fixtures/` is the
  only exemption (`privacy.py:37`) and this brief adds no Word file there.
- D0.2 **The gate pipeline as it stands.** `gates.py:55-59` `messages(card, pages, nonce, *, matter)` builds the system
  message `prompt_id: <nonce>\n<card text>` and the user message `Matter <number>\n` plus `benchrun.page_block` per
  page; `:153-154` `ask(card, pages, *, client, rules, log, matter, nonce=None, job="gates", playbook_version="")`;
  `:159-161` one run row with `benchrun.prompt_sha256`; `:172-174` the retry line `Retry: the previous answer failed
  the <gate> check: <message>. Answer again with one JSON object and nothing else.` inserted after the first line of the
  user message; `:179-181` budget `sum(model.tokens_at_most(m["content"])) + model.TEMPLATE_TOKENS` against
  `client.config.num_ctx - card.max_answer_tokens` (`Card.max_answer_tokens = 8192`, `:28`); `:92-139` `_references`:
  `:98-99` lookup `stamps.normalize(cite) in page.stamps or cite == page.page_id`, `:125-131` the digit-run check
  `re.findall(r"\d+", fact["text"])` over the whole text, no cite exclusion (verifier L2); `:16` `_SKIP_RULES`,
  `:62-71` `_rules_strings`; `:239-241` gate 5 runs `rules.check(value, unit=card.unit, stamped=all(p.stamps for p in
  pages))` (verifier L1: `all` to `any` stays green); `:88-89` `_page_label` is the first stamp else the page id;
  `:295-304` coverage rows `read`, `uncited`, `failed` keyed by `page.page_id`; `:186-188` a `ModelError` with
  `received=False` is raised out of `ask`. `model.py:11` `TEMPLATE_TOKENS = 64`, `:14-15` `tokens_at_most` is the
  UTF-8 byte count, `:75-78` `ModelClient(config, opener=None)`.
- D0.3 **The cite rule sees bracketed forms only (R1-20).** `playbook/rules.toml:56` `cite_pattern =
  '\[(?:cite|p\.|page)\s*([^\]]*)\]'`, `:57` `bates_pattern` (single, range, comma list; owner question 12);
  `rules.py:74-78` `re.finditer(rule.cite_pattern, ...)` then `re.fullmatch(rule.bates_pattern, match.group(1).strip())`,
  severity `error` when `stamped` else `warning`; `rules.py:154-156` the loader requires `cite.groups >= 1`. Measured
  with the project interpreter: `Rules.check` returns `[]` for `See page 12`, `(Ex. 3 at 12)`, `at p. 12` (R1-20
  reproduced) and `[]` for `Defense report`, `Medical memo for matter 9001.001`, `a 12 page report`, `Page 2 of 3`,
  `the next page`; it returns `no-dme-ime error` for `Independent Medical Evaluation`, so a memo may never copy a
  record's title into its own words (quotes are exempt by Q44 item 43, headings are ours). `gate.py:29-37`
  `rules_selftest` checks each rule's `good` and `bad` example only.
- D0.4 **The stage 2 runner is still the bench runner (D25, D35: replaced at stage 5).** `benchrun.py:13-22`
  `CARD_TEXT`, `:29-30` `page_block`, `:33-35` `messages(matter)` (no nonce, no ids), `:38-39` `prompt_sha256`,
  `:46-51` `RunResult(candidate, pages_failed, failure, reply_received)`, `:60-98` `run(matter, config, log,
  playbook_version, opener=None)` with its own three guards. Callers: `gates.py:10,59,161` (`page_block`,
  `prompt_sha256`), `bench.py:7,17` (`runner=benchrun.run`), `tests/fakemodel/bench.py:7,11,24`
  (`CARD_TEXT`, `benchrun.messages` for the `bench-<number>` recording row), `tests/test_gates.py:9,164`
  (`benchrun.prompt_sha256`), `tests/test_stage2_exit.py:38-44` (`INPROCESS_CHILD` patches
  `benchrun.ModelClient`), `tests/test_bench_multi.py:8` and `tests/test_fix_cycle5.py:10` (`RunResult`, runner
  signature `(matter, config, log, playbook_version, opener)`), `tests/test_benchrun_done_reason.py:3,25`,
  `tests/test_fakemodel_bench.py:4` (`CARD_TEXT`, drives the bench row through `/api/chat` and four modes),
  `tests/test_benchrun.py` (the R4-2 line `benchrun_modes=8 of 8`). `tests/fakemodel/bench.py:10-15`
  `extraction_card()` = `CARD_TEXT` plus the one-sentence id instruction, `gates.Card("bench_extract", ...)` with
  `schemas/bench_extract.schema.json`; version `4ab2bdb30535` (measured); `:18-28` `recordings_for` returns the
  bench row and the `gates-<number>` row built from `gates.messages(card, loaded.pages, "__PROMPT_ID__",
  matter=loaded.number)` with the ideal answer wrapped in `prompt_id` and `end_id`. The production code has no
  extraction card of its own: the card lives in test code.
- D0.5 **Bench and its detail lines.** `bench.py:16-17` `main(matters_dir, config_path=None, candidate_path=None, *,
  out=None, err=None, opener=None, runner=benchrun.run)`; `:47-63` the pre-pass (D37); `:65-72` the run log opens only
  in model mode; `:87-102` the runner call, `bench <number> failure <text>` line, exit 2 when `not
  result.reply_received`; `:104-108` `benchscore.score(key, candidate, matter, book.rules, pages_failed)` and
  `s.details()`. `benchscore.py:51-66` `details()`: `invented: <cite> "<quote>"` with no reason (`:82-83` collects
  `(cite, fact.quote[:60])` whether the page is missing or the quote is not on it, critic L3), `rules: <rule_id>
  <where>` with no excerpt (`:114-119` collects `(finding.rule_id, where)` only), `rungs:` only when a rung other than
  exact was used. `tests/test_bench_detail.py:17-24` pins `FLAWED_DETAIL` (six lines, `  rules: no-dme-ime DEF0003`),
  `:28-31` `PROBE_DETAIL` (`  rules: no-dme-ime flag MED0002`), `:55` the perfect candidate prints no detail line;
  `tests/test_bench_cli.py:11-14` pins the two main lines.
- D0.6 **Run log.** `runlog.py:135-142` `coverage(matter)` returns the latest row per `(page_id, card)` by `id` over
  every job (a bench run and a memo run on one matter number share rows); `:144-145` `open_items`; `:22-24` the
  `approvals` table (unused by any stage so far); schema v2, 21 triggers; `start_run` `:83-92` takes `job`, `matter`,
  `card`, `card_version`, `playbook_version`, `model`, `pages_in`, `prompt_sha256`.
- D0.7 **Two page layouts exist and no loader reads intake's.** `matter.py:20-29` `Page(binder, number, text, stamps)`
  with `page_id = f"{binder}/{number:03d}"`, `stamps` a tuple of normalised strings; `:48-125` `load(root)` reads the
  bench layout (`matter.toml`, `records/<binder>/NNN.txt`, the stamp alone on the last line, D25). `intake.py:41-54`
  `PageRecord(matter, binder, page, id, stamps, text, had_text_layer, ocr_added, source, status, reason, sha256)`
  with `stamps` a list of `{"raw", "stamp"}` (`:302-303`) and `status` in `ok`, `empty`, `failed` (`:296-301`);
  `:308-309` written as `pages/<binder>/NNN.json`; `:311-315` `binder.json` with `matter`, `binder`, `file`, `sha256`,
  `pages`, `ok`, `empty`, `failed`, `open_ids`, `tools`, `args`, `written`. Intake writes no `matter.toml` and no run
  log row (D27). `intake.py:200-226` `_check_destination` is the identity check pattern for a matter folder (resolves
  under the matters root, `records` and `pages` must be plain folders). No code reads `pages/*.json` back today
  except `tests/test_stage3_exit.py` and `tests/test_intake.py`.
- D0.8 **Fixture facts the memo leans on (measured).** 9001.001: 14 pages, binders `medical` (8), `employer` (3),
  `defense-report` (3) in `matter.toml` order; page block bytes (header line plus text plus newline): medical 1106,
  1285, 1094, 1118, 1633, 1439, 1500, 1346; employer 1275, 1220, 995; defense-report 1383, 1624, 1416. The ideal cites
  13 pages, never `DEF0001` (`defense-report/001`), whose text holds `The examinee reports lifting a tote of about 60
  pounds.` (`records/defense-report/001.txt:20`, an invented sentence the key does not use). `Rules.check` over the 31
  ideal quotes returns `[]` (round 4 D0.13). 9002.001 (`tests/fixtures/scanned/scanned.json`): six pages, page 4
  `blank` (intake status `empty`, `no text after OCR`), page 3 carries two stamps `KMR2344` and `TWP7731`; the
  `must_contain` spans are proven present in the OCR text by the stage 3 exit test (`must_ok=5 of 5`).
- D0.9 **Stand-in.** `tests/fakemodel/core.py:12-14` `MODES` (17; `tests/test_fakemodel.py:151` pins `len(MODES) ==
  17`); `:23-34` `_prompt_parts` canonicalises the `prompt_id:` first line and removes a `Retry:` second line of the
  user message; `:151-153` an unknown canonical prompt is 404 (so every chunk a test sends needs its own recording
  row); `:37-65` `_fault_content` edits `facts[0]`, `facts[1]`, `facts[2]` and `flags[0]` (`bad_quote` needs three
  facts and one flag, `bad_schema` needs `facts[0]`); `:206-225` `FakeTransport(model, edit=None)`.
- D0.10 **Exit tests and tables that move.** `tests/test_stage2_exit.py:18-19` `PERFECT` (model `qwen3.8:27b`),
  `:75-76` asserts `lines[0]` and `lines[-1]` only (a detail line between them is free); `tests/test_stage4_exit.py:15`
  imports `extraction_card`, `:125` `open_items` keys use the card name `bench_extract`; `tests/test_gates.py:36-41`
  `CASES` (27), `:79` prints `gate_cases=... of 27`; `tests/test_bench_multi.py:30-33` and `:51-53` runners return
  `RunResult(..., 0, None, True)`; `tests/conftest.py:131-144` `scanned_intake` (session scope, real OCR once,
  matter root under its own tmp config); `tests/conftest.py:27-39` `write_config` puts `matters`, `state`, `playbook`
  under `tmp_path`; `:93-97` `production_dirs_untouched` watches `state/`, `Cases/`, `Bench/`.
- D0.11 **Config bounds the chunk test.** `config.py:115-116` refuses `num_ctx < 65536`, so a multi-chunk test cannot
  shrink the context; it must raise `Card.max_answer_tokens` (`gates.py:180` subtracts it from `num_ctx`).
  `config.py:150-158` `[paths].matters` outside the checkout by identity; `:159-163` `state` and `playbook` resolve
  against the checkout; `state/` and `*.sqlite` are gitignored.
- D0.12 **Cards, schemas, playbook.** `cards/manifest.json` lists 45 cards of the earlier two-model plan (among them
  `00-CHANGE` change report, `00-RECONCILE` compare one new fact with the case file, `01-P1` encounter extraction with
  categories and dates); spec §7 says stage 6 rewrites them and adds the medical memo card; stage 4 and 5 run only
  `bench_extract` (D34). `playbook/rules.toml` holds the four firm rules; `playbook/samples/depo-goals.toml` three
  SAMPLE entries; no playbook entry describes the memo. The two Claude skills named in spec §6 (`deposition-prep`,
  `workers-comp-hearing-prep`) live outside this repo and were not read (the brief's privacy rule); the playbook
  does not point to them. What a memo contains is therefore settled by spec §2 alone, plus owner rulings Q37 (no
  billing memo), Q41 (conflicts flagged, defense against ours above all), Q44 item 43 (quotes exempt), Q48 (no
  summary used as verified), Q49 (rule ids shown); the rest is §7.
- D0.13 **Numbering.** Spec §9 ends at D38; owner questions end at 49; tuning entries end at T-19; ledger round 5 has
  R5-1 to R5-3; worktree `.claude/worktrees/r4-lane-b` (branch `r4/lane-b`, merged) still exists; toolchains under
  `~/.casefile-dev/`: `legal-harness`, `r3-lane-b`, `r4-lane-b`.

## §1 Decisions, with trade-offs

- **1.1 The memo of stage 5 is built from verified material only; its sections are an owner interim (question 50).**
  Spec §2 names the running memo's content (treatment chronology, providers, diagnoses, restrictions, history,
  opinions, gaps, conflicts, "what changed", outputs out of date) and spec §7 puts the medical memo card in stage 6;
  the only extraction card today is `bench_extract` (D0.4, D0.12), whose facts carry `cite`, `quote`, `text` and
  nothing else (no date, no category, no provider). A chronology by date of service would need a `date` field the
  gates can verify, and a grouping by category would rest on an unverified model label. By the brief's rule (practice
  from the playbook, the spec and owner rulings, never from taste) the layout that needs no inference is the interim:
  (1) title `Medical memo: matter <number>` and a line `built <date> from case file entry <seq>; playbook <version>;
  model <tag>`; (2) `What changed since the last memo` (counts of facts, cites, readings, flags added, or `First memo
  for this matter`); (3) `Outputs out of date` (`none` or the names, §1.6); (4) `Open items` (every page not read, one
  line each, §1.7); (5) `Conflicts`, opening with the sentence `Pages read in <N> run(s); conflicts between runs are
  checked only for pages sent together.` (N = distinct run ids among the memo job's `read` coverage rows; plan
  review H1, question 56), then one entry per conflict flag in case-file order (`seq`; question 54 asks about
  ordering): the cites in bracket form, then one `Model's reading: <about>` paragraph per `about` of the flag (plan
  review L2); (6) `Gaps and missing records` (the same for gap flags); (7) `Verified facts by record`: a heading per
  page in binder order (`<binder> page <stamps> (<page id>)`), and under it, per fact, one paragraph holding the quote
  in straight double quotes followed by its cite `[cite <stamp>]` (or `[page <page id>]` when the page has no stamp),
  then `Also cited: [cite ...]` when the same quote was found on other pages, then one `Model's reading: <text>`
  paragraph per reading. A fact's paragraphs sit under the heading of the first page that cited it and nowhere
  else: a quote found on two pages (the scanned fixture repeats `Seen by Dr. Rafael Soto-Lindgren.` on pages 1 and
  2) appears once, with `Also cited`, and the second page's section does not repeat it (plan review L1; spec §3.5
  "a repeated fact adds a cite"); every paragraph of a page lies between that page's heading and the next heading
  (W5 and W8 assert the order, plan review M4). The quote is the verified text (Q48 interim, D38); every `text` and
  `about` is labelled as the model's reading. Rejected: grouping by the model's categories or dates (pillar 1: no
  inference in an output);
  waiting for stage 6 to produce any memo (the stage 5 exit test asks for one now). Cite form: the playbook's own
  good example (`rules.toml:60`, `[cite ABC0001]`) is the firm's form; questions 52 and 53 ask the owner to confirm
  it and the page-id fallback.
- **1.2 The memo is a Word document written with python-docx; the content check opens the file.** Spec §3 step 6 and
  §5 say outputs download as Word documents built with python-docx templates (D6: reuse, do not rebuild). `uv add
  "python-docx>=1.1,<2"` (brings `lxml` and `typing_extensions`) is run by the chair with the sandbox off before the
  lanes split (W0) so the lock changes once. No template file: a `.docx` template cannot be committed outside
  `tests/fixtures/` (D0.1) and a firm template is practice (question 51); `docx.Document()` default styles,
  `add_heading` levels 0 to 2 and `add_paragraph`. The memo goes to `<matters>/<number>/outputs/memo.docx`
  (outside the checkout by D13; never under `state/`, which the privacy row would flag). Every test that judges a memo
  opens the produced file with `docx.Document(path)` and reads `paragraphs` (and their `runs`), never the file name.
  Rejected: Markdown or plain text as the memo (spec says Word; a second rendering doubles the surface and the
  critic's reading); `python-docx` deferred to stage 6 (then the stage 5 memo would exist in no file the attorney can
  open).
- **1.3 `casefile memo --matter N` is the stage 5 job, in one process, with pages read from either layout.** New
  `src/casefile/pages.py` `load(matters_root, number, stamp_pattern) -> PageSet(number, pages, open_pages)`:
  the matter folder `<matters>/<number>` must exist and resolve under the matters root by identity (as
  `intake._check_destination`, D0.7), `casefile.jsonl` and `outputs` must not be links; layout by `matter.toml`
  present (bench layout, `matter.load`, every page `ok`) else `pages/` present (intake layout: every
  `pages/<binder>/NNN.json` read, binders in sorted name order, pages by number; `id`, `matter` equal to the folder
  name, `binder`, `page`, `text`, `stamps` of `{raw, stamp}`, `status` in `ok`, `empty`, `failed`, `reason` required;
  `binder.json` `pages` equal to the record count; `status == "ok"` pages become `matter.Page(binder, page, text,
  tuple(s["stamp"] ...))`, the others `open_pages` as `(page_id, stamps, status, reason)`); neither layout ->
  `PagesError("no pages for matter N under <root>: run casefile intake first")`; both -> `PagesError("ambiguous
  layout ...")`; any malformed record -> `PagesError` naming the file. Exit 2 on `PagesError`, `ConfigError`,
  `PlaybookError`, a broken case file (§1.5) or a model server that never replies (`ModelError.received False`,
  Q26 style: `memo: cannot run: no reply from the model server at <host>: ...`); exit 1 when the memo was written but
  open items remain (as intake, Q40 item 32); exit 0 when every page is read. A benchmark matter that lives in the
  checkout must first be copied under `[paths].matters` (`config.py:150-158` requires that root outside the checkout;
  D25 lets benchmark matters live inside it; `casefile bench` is unchanged): the memo never reads the checkout (plan
  review L10). A binder whose name fails a firm rule at `error` (`ime`, `defense-medical-exam`: `rules.py:59` runs
  every pattern with `re.IGNORECASE`, measured in §8 M8) cannot be rendered, because every heading, label and cite
  of its pages holds the name; `casefile memo` exits 2 before any model call with `memo: cannot run: binder <name>
  fails the firm rule <id> (<excerpt>); remove the binder by hand and intake it under another name (question 34)`
  (question 57 interim; intake is unchanged this round). Rejected: a job queue, the one-at-a-time
  lock and Cancel (spec §5 "job runner": stage 8's web page needs them, the CLI runs one job per process); reading
  only the intake layout (the benchmark matters, Q34 item 22, use the bench layout and the owner may want their memo);
  a memo that runs the model on every page every time (§1.4).
- **1.4 Chunking is deterministic, by bytes, in page order; only unread pages are sent; a page too long for one
  prompt is refused.** New `src/casefile/pipeline.py`: `RETRY_MARGIN = 8192`; `chunk(card, pages, num_ctx, matter)
  -> (chunks, refused)` fills a chunk with consecutive pages (binder order, then page number) while
  `tokens_at_most(system) + tokens_at_most(user) + TEMPLATE_TOKENS + RETRY_MARGIN <= num_ctx -
  card.max_answer_tokens`, where the messages are `gates.messages(card, chunk, "0" * 16, matter=matter)` (the nonce
  is always 16 hex characters, `secrets.token_hex(8)`); a page whose one-page chunk does not fit is refused with
  `page too long for one prompt (<bytes> bytes, budget <bytes>); split the binder` and never sent. Why the margin:
  `gates.py:172-174` makes attempt 2 longer by the `Retry:` line, whose reason can run to several kilobytes for a
  chunk with many quote faults, and a chunk that passes attempt 1's budget and fails attempt 2's is a failure the next
  run repeats forever; 8192 bytes is about 14 percent of the budget (T-20). On the fixture one chunk of 14 pages
  (19462 of 57344 bytes). Arithmetic the multi-chunk test rests on: with `max_answer_tokens = 65536 - 8192` the page
  blocks of a chunk may total at most `8192 - 64 - 8192 - 948 - 16`, which is negative (every page refused), so the
  test uses `max_answer_tokens = 65536 - 16384`: `16384 - 64 (TEMPLATE_TOKENS) - 8192 (RETRY_MARGIN) - 948 (system:
  11 + 16 + 1 + 920) - 16 ("Matter 9001.001\n") = 7164` bytes of page blocks per chunk; from D0.8: chunk 1 `medical/001` to `medical/005` (6236; adding
  `medical/006` gives 7675), chunk 2 `medical/006` to `employer/002` (6780; adding `employer/003` gives 7775), chunk 3
  `employer/003` to `defense-report/003` (5418): three chunks of 5, 5 and 4 pages. `run(pages, *, card, client, rules,
  log, matter, playbook_version, job, only_unread) -> PipelineResult(outcomes, refused, chunks)`: with `only_unread`
  the pages whose latest coverage row for `(page_id, card.name)` among runs with this `job` is `read` are skipped
  (`runlog.coverage(matter, job=...)` gains a required job filter, plan review L3, D0.6: a bench run and a memo run on the same number
  must not read each other's rows); a refused page gets one run row (`pages_in` 1, the would-be prompt's sha256), one
  `failures` row `gate.truncation: <reason>; not retried: the page must be split`, one coverage row `failed`, no
  `answers` row (the budget refusal precedent of round 4 §1.3); every chunk goes through `gates.ask` unchanged; a
  `ModelError` with `received False` stops the run and propagates (chunks already answered keep their rows). Pages
  the previous run left `failed` or `uncited` are sent again on the next run, in their own chunk if nothing else is
  unread: that is D38's "a page it cites is read" applied on a later run (Q42, Q47 interims: nothing else closes a
  page; question 55 asks whether re-sending every run is acceptable). What re-sending an uncited page alone costs
  (plan review M7, verified at `gates.py:246-247`, `:286`, `:297-304`): a cover sheet yields an answer with no facts
  and no flags, gate 6 fails it, the one retry is used, so two model calls per run, and its coverage row becomes
  `failed` with the reason `gate.coverage: the answer has no facts and no flags; not retried: the one retry was
  used; the page stays open until a later run reads it`; `status` and the memo show that reason verbatim (the
  status word is `failed`, the reason says what the model answered); question 55 states both. Known limit, stated
  by the memo's conflicts sentence (§1.1 (5)) and measured by W3: a conflict between pages in different chunks
  cannot be flagged by this card (the `00-RECONCILE` card is stage 6 or later), and because only unread pages are
  sent, a record that arrives after the first run is read in a chunk of new pages only, so a conflict between it and
  an already-read page is never flagged on a matter read in more than one run (plan review H1). The reviewer's
  proposal (fill the chunk with already-read pages up to the budget) is not adopted as an interim: on the fixture it
  re-sends the whole matter (run 3 would send all 14 pages, the stand-in's ideal answer cites no `DEF0001`, and the
  page stays uncited), it re-reads every page on every later run (the cost question 55 already raises), and a
  re-sent page the model then fails to cite would flip from `read` to `uncited` on its latest coverage row, which
  needs a ruling on what "read" means across runs. Decided on the pillars: the memo states the number of runs and
  the limit in its own words (an honest output), re-found facts merge to nothing by identity (§1.5) so any later
  fill is safe for the case file, and the rest is question 56 with the fail-closed interim (no fill, the sentence
  shown, W8 asserts `runs_seen=2` on the third memo). Rejected: chunking per binder
  (the fixture's four cross-binder conflicts would vanish from the exit test, and a small matter is one prompt);
  a token estimate instead of bytes (D31); sending every page every run (the model's cost on the Studio, and a page
  once read is read: pillar 6 measures, the run log keeps the proof).
- **1.5 The case file is an append-only JSON Lines file with a hash chain; merge is by exact identity, never by
  meaning.** New `src/casefile/facts.py`: `<matters>/<number>/casefile.jsonl`, one JSON object per line, keys `seq`
  (1, 2, ... contiguous), `at`, `prev` (sha256 hex of the previous line's bytes without its newline, `""` on the
  first), `kind`, then the payload. `load(path) -> CaseFile` verifies `seq` and every `prev`, refusing with
  `CaseFileError("case file chain broken at line N; the file was edited or truncated")` (exit 2); `append(path,
  events)` opens in append mode, writes, flushes and `os.fsync`s; nothing complete is ever rewritten (#R01-CX-3 by
  construction: there is no update path). A torn tail (plan review M5: a crash or power loss mid-append leaves bytes
  after the last newline that do not parse as a JSON object) is not an event: `load` ignores it and reports it
  (`CaseFile.torn` = its byte count, printed by `casefile memo` and `casefile status` as `casefile: torn last line
  (<N> bytes) discarded; the event was never completed`), and `append` truncates the file to the last newline
  (`os.ftruncate`) before writing, so the chain is intact by construction; a final line that parses but lacks its
  newline is complete, and `append` writes the newline first. Every other break (a line edited, removed or cut in
  the middle of the file) stays a refusal: the attorney never edits the file, and a recovery command is stage 8 or
  later. Kinds: `fact` `{id: "F<seq>", cite, page_id, quote, text, run_id}`; `cite` `{fact, cite, page_id,
  run_id}`; `reading` `{fact, text, run_id}`; `flag` `{id: "G<seq>", kind, cites, page_ids, about, run_id}`;
  `about` `{flag, about, run_id}`; `run` `{run_id, job, card, card_version, pages, ok, read, uncited, failed}`;
  `output` `{name, path, built_from_seq, facts, conflicts, gaps, open}`. `merge(casefile, outcome, pages, run_id) ->
  events` over a passing `Outcome.answer` only: a fact's identity is `quotes.fold(quote)`; the same identity on the
  same page adds nothing; on a new page adds a `cite` (spec §3.5 "a repeated fact adds a cite"); a `text` not yet
  among the fact's readings adds a `reading` ("added detail adds a version"); a flag's identity is `(kind,
  sorted page ids)` (the cite set, D25, Q34 item 25); a new `about` wording on a known flag adds an `about`; a conflict
  is whatever the model flagged as one within its chunk and the gates verified ("disagreement is kept as a conflict
  for the attorney", never resolved: pillar 5). Cites resolve to page ids through the same lookup gate 4 used
  (`gates.py:98-99`), so every stored `page_id` names a page that exists. Rejected: a single rewritten JSON document
  (append-only by promise, not by construction); SQLite for the case file (the run log is the audit trail, the case
  file is the matter's own portable record, spec §5 "append-only JSON, versioned"); merging by similarity of `text`
  (inference).
- **1.6 "What changed" and "outputs out of date" are computed from the case file's sequence numbers.** The memo's
  `output` event records `built_from_seq` (the last `seq` before the output); "what changed" counts the `fact`,
  `cite`, `reading`, `flag`, `about` events after the previous `output` named `memo` (none: `First memo for this
  matter`); an output is out of date when any of those kinds has a `seq` above its `built_from_seq`. `casefile status`
  prints `outputs=memo:current`, `memo:stale` or `none`. A memo build on a matter with nothing new still writes a
  new memo and a new `output` event (the file is rebuilt, the attorney asked). Rejected: file timestamps (not evidence).
- **1.7 Open items are shown by stamp, keyed by page id, from one source per page (critic M2).** An open item is a
  page whose latest coverage row for the memo job is not `read` (`failed`, `uncited`, or a refused page) or an intake
  page with status `empty` or `failed` (D0.7; these never reach the model and get no run log row, D27). Label:
  `<stamps joined by one space> (<page id>)` when the page has stamps, else the page id alone (`KMR2344 TWP7731
  (scan/003)`, `DEF0001 (defense-report/001)`, `probe/001`); a line reads `  open: <label>: <status>: <reason>` in
  page order, in `casefile memo`'s output, in `casefile status`, and in the memo's `Open items` section. The reason is
  the run log's or the page record's text verbatim (rule ids included, Q49 interim); a page the model answered
  nothing about on a re-send shows `failed` with the `gate.coverage` reason of §1.4 (plan review M7). Rejected:
  choosing one stamp (Q35: intake chooses none; hearing prep asks).
- **1.8 The memo checks its own words against the firm rules before it is written; quotes and run-log reasons are
  exempt.** `memo.check(memo, rules) -> findings` runs `Rules.check(unit="text", stamped=<every page of the matter
  has a stamp>)` over every paragraph the code or the model wrote: titles, headings, labels, `Model's reading` texts,
  flag abouts, open-item labels. Exempt: the quote runs (the record's words, Q44 item 43) and the open-item reason
  runs (the run log's record of a failure; a `gate.rules` reason quotes the rule's own sentence, which names the
  labels it forbids). Any `error` finding -> `MemoError` naming the paragraph, the memo is not written, exit 2 (fail
  closed). `text` and `about` passed gate 5 at extraction; the re-check guards a playbook changed since (spec §6:
  every output records the playbook version it used). Binder names are checked first, before the run log opens and
  before any model call (§1.3, plan review M8): a name that fails a rule at `error` is the refusal with the remedy
  sentence, not a `MemoError` on a heading after the model has run. The rules run with `stamped=False` when any
  page is unstamped, and the memo then opens its facts section with the rule's own warning sentence naming those
  pages (question 53).
- **1.9 Gate 4 treats a bracketed cite inside `text` or `about` as a reference: verified against the chunk, then
  excluded from the digit-run check (R5-2, verifier L2, Librarian #R04-V-2).** In `gates._references`, every string
  under a `text` or `about` key is scanned with the firm's `cite_pattern` (the `bates-cites` rule of the `rules`
  object passed to `ask`, so the form has one source, with the rule's own flags: `rules.py:59` `re.IGNORECASE`);
  the span's body is read by one helper, `rules.cite_body(match) -> str` (the first capture group that is not
  `None`), used by `rules.py:76` and by gates alike, because §1.10 makes the pattern a three-group alternation and
  `match.group(1)` is `None` for the unbracketed forms (`stamps.normalize(None)` raises `TypeError`, measured; plan
  review M2); each body goes through `lookup` (a page of the chunk by stamp or page id, else `facts[i].text: cite
  <body> is not a page of this chunk`, an ambiguous stamp the same as today), and the digit-run check runs over the
  text with the spans removed. So a model sentence `... see page 12` fails gate 4 with `facts[0].text: cite 12 is
  not a page of this chunk` (W1 `text_see_page`). A range or list body (owner question
  12's interim for prose) is not a page and fails here; stage 6, which writes prose from the playbook, decides again
  with the benchmark. Why verify rather than strip: pillar 1 ("every fact carries a cite to a page that exists"); why
  not forbid cites in `text`: the playbook's good example for `bates-cites` is a sentence ending in a cite, and the
  stage 6 cards will write exactly that. The playbook example `The report records a normal gait. [cite ABC0001]`
  therefore passes gate 4 when `ABC0001` is a page of the chunk and its quote lacks `0001`.
- **1.10 The `bates-cites` rule sees the unbracketed forms too (R1-20), narrowly.** `rules.toml:56` `cite_pattern`
  becomes an alternation with three capture groups: the bracketed form as today; `\b(?:see|at)\s+(?:page|p\.)\s*
  ((?:[A-Z]{1,8}[ -]?)?\d+)\b`; `\((?:Ex\.|Exhibit)\s+[^)]*?\bat\s+((?:[A-Z]{1,8}[ -]?)?\d+)\)`. The body is a
  number or a stamp-shaped token, never the next word (plan review M3: the brief's first draft captured `after` in
  `He looked at page after page` and `MED` in `see page MED 0012`); the rule runs with `re.IGNORECASE` (`rules.py:59`,
  `:75`), so `See` matches, and `rules.py:76` `re.fullmatch(rule.bates_pattern, ...)` is case-sensitive as today.
  `rules.py:76` reads the body through `rules.cite_body` (§1.9); the loader's `groups >= 1` check stays. Table
  (`cite_forms=11 of 11`, measured on the pattern above): must fail when stamped: `See page 12.`, `see p. 12`, `at
  page 12 of the report`, `(Ex. 3 at 12)`; must pass: `a 12 page report`, `Page 2 of 3`, `the next page`, `page
  count 14`, `see page MED0012` (a Bates body), `see page MED 0012` (the same stamp, Q40), `He looked at page after
  page.` (no cite at all). `rules_selftest` (gate) is unchanged: the rule's `good` and `bad` examples still behave.
  Rejected: a wider pattern over any `page N` (over-blocking, #R01-CX-7 class); leaving the rule as is (the memo's
  own words are code-authored and never say `see page`, but the rule is the firm's checker for every stage 6
  output).
- **1.11 The mixed chunk rule is kept and tested (verifier L1).** `gates.py:241` stays `stamped=all(p.stamps for p in
  pages)`: when any page of the chunk is unstamped, the cite rule warns instead of erring and the pipeline's own
  warning names the unstamped pages. W1 adds the case the verifier described, with a cite that is a page of the chunk
  (`[page mixed/002]`, §1.9), so that `all` to `any` turns it red. Spec §4 rule 5 gains the sentence (§6, D42).
- **1.12 Bench runs the pipeline (D25 and D35 "replaced at stage 5"); `benchrun.py` is removed.** `pipeline.bench_run
  (matter, config, log, playbook_version, opener=None) -> RunResult(candidate, pages_failed, failure, reply_received,
  uncited)` runs every page (`only_unread=False`, job `bench`), merges every passing chunk into an in-memory
  `CaseFile` (nothing written to the matter folder), and builds the candidate from it: one `CandidateFact(cite, quote,
  text)` per (fact, cite) with the fact's first reading, one `CandidateFlag(kind, cites, about)` per flag with the
  flag's first about and cites as the page labels; `pages_failed` counts pages whose coverage is `failed` (a failed
  chunk, a refused page), `uncited` lists the uncited page labels, `failure` is the first failing chunk's final
  failure message (printed as `bench <number> failure <message>`, as today), `reply_received` is False only when the
  server never replied (bench exit 2, Q26). `bench.py:17` `runner=pipeline.bench_run`; after `s.details()` bench
  prints `  uncited: <labels>` in model mode only (candidate mode has no coverage; its lines are byte-identical to
  today). `pages_failed` keeps D25's meaning (failed, not uncited), so the stage 2 line and the perfect exit 0 hold
  (the key itself cites neither `DEF0001` nor `EMP0002`: an uncited page is the honest state, not a model fault; a
  page the key cites and the model skips shows as `missed`). `extract.py` (W0) takes `CARD_TEXT`, `page_block`,
  `prompt_sha256` and `card()` out of `benchrun.py` and test code; the stage 2 recording row goes with the runner
  (`recordings_for` returns the gates row only; `tests/test_fakemodel_bench.py` drives that row). The runner-level
  proof that every received reply is stored as an `answers` row (D25, D30, #R02-V-F1, #R02-V-F1b) moves with the
  runner (plan review H2): `tests/test_benchrun.py:155-389` holds the only tests of it on each transport path, and
  `tests/test_model.py:227-331` tests `ModelError.received` and `raw` at the client with no run log, so W3 rewrites
  those cases against `pipeline.bench_run` as `reply_rows=9 of 9` (W3 Ships) before `test_benchrun.py` goes; the
  one place that now stores the rows is `gates.py:186-191` and `:275-277`. T-9 is answered on
  the fixture: the pipeline scores the same perfect line as the stage 2 runner (one chunk, same ideal answer), and
  W3's three-chunk run measures what chunking costs (`flags=5 of 9`). Rejected: keeping `benchrun.py` beside the
  pipeline (two runners for one measurement, dead code the verifier would flag); counting uncited pages as failed
  (the ideal answer could never be perfect, and D38 keeps `uncited` apart from `failed`).
- **1.13 Bench detail lines say why (critic L3).** `invented: <cite> "<quote>" (no such page)` when the cite matches
  no page of the matter, `invented: <cite> "<quote>" (quote not on the page)` otherwise; `rules: <rule_id> <where>
  "<excerpt>"` with the finding's matched words (Q49: the id stays beside what it caught). `Score.invented_facts`
  becomes `(cite, quote, reason)` and `rule_hits` `(rule_id, where, excerpt)`; every pinned detail line moves with
  them (W6 lists the files).
- **1.14 `casefile status --matter N` is the §8b `matter_status` view.** New `src/casefile/status.py`
  `matter_status(config, number) -> dict` with `pages`, `read`, `failed`, `uncited`, `empty`, `open`, `facts`,
  `conflicts`, `gaps`, `outputs` (counts and names, no content) and `open_items` (labels, status, reason), printed as
  `status <number> pages=P read=R failed=F uncited=U empty=E open=O facts=N conflicts=C gaps=G outputs=<memo:current|
  memo:stale|none>` plus the open lines of §1.7; exit 0 always (a view, not a check); exit 2 when the matter, config or
  case file cannot be read. The bridge (stage 8b) calls `matter_status` and returns the counts only.
- **1.15 The extraction card lives in production code, byte-identical to today's.** `src/casefile/extract.py`
  holds three constants (plan review L5): `CARD_TEXT`, byte-identical to `benchrun.py:13-22` (the stage 2 system
  message, so the stage 2 recording row and `benchrun.messages` do not change in W0); `ID_SENTENCE`, the one
  sentence of `tests/fakemodel/bench.py:11-13`; `TEXT = CARD_TEXT + ID_SENTENCE`, the card's text. `card() ->
  gates.Card("bench_extract", TEXT, schema.load(<checkout>/schemas/bench_extract.schema.json))`, `page_block`,
  `prompt_sha256`; `benchrun.card_version()` has no caller outside its file (measured) and goes with it in W3.
  `tests/fakemodel/bench.py:extraction_card` returns `extract.card()`, so the recordings, the stage 4 exit test and
  `open_items` keys (`bench_extract`) do not move; `card().version == "4ab2bdb30535"` and `card().text is
  extract.TEXT` are asserted. Card text from the playbook is stage 6 (spec §7).
- **1.16 Stage 6 boundary.** Not this round: the deposition, hearing and report outputs; rewriting `cards/` and
  `schemas/`; a memo card with categories or dates; the reconcile card for cross-chunk conflicts; the anonymizer
  (stage 7, Q47 convention); the web page, job queue and Cancel (stage 8); the bridge (8b). The memo's sections are
  code and will be rebuilt from the playbook when the memo card exists.

## §2 Work items, in build order

Every CHECK runs through `scripts/run.sh`; every seed is applied to a copy, confirmed with `cmp`, run with a fresh
`PYTHONPYCACHEPREFIX` (#R04-OC-1), and restored (`cmp` identical) before the pass counts (Q6, HANDOFF).

### W0 (chair, then one builder in the main tree, before the lanes split): python-docx, `extract.py`, the card in production
- Chair, sandbox off, in the checkout: `uv add "python-docx>=1.1,<2"`; `pyproject.toml` and `uv.lock` change;
  `scripts/run.sh python -c "import docx; print(docx.__name__)"` prints `docx`, exit 0; then `uv sync` for the lane B
  worktree toolchain (`T=$HOME/.casefile-dev/r5-lane-b`, HANDOFF).
- Builder files: `tests/conftest.py:41` (`write_config`'s default `host` becomes `http://127.0.0.1:9`, the port the
  no-reply tests already use, so no test reaches the owner's `ollama` on 11434 unless it names a port it opened
  itself; plan review M6: `tests/test_gates.py:88,279`, `tests/test_model.py`, `tests/test_jsonrepair.py:119` and
  the session fixtures `conftest.py:103,135` all take the default today); new `src/casefile/extract.py` (`CARD_TEXT`,
  `ID_SENTENCE`, `TEXT`, `CARD_NAME = "bench_extract"`, `card()`, `page_block`, `prompt_sha256`, §1.15);
  `src/casefile/benchrun.py:13-22,29-39` (`CARD_TEXT`, `page_block`, `prompt_sha256` become
  imports from `extract`; `run` untouched until W3); `src/casefile/gates.py:10,59,161` (`extract.page_block`,
  `extract.prompt_sha256`); `tests/fakemodel/bench.py:10-15` (`extraction_card` returns `extract.card()`), new helper
  `recording_for(card, pages, number, answer) -> dict` (the `gates.messages(..., "__PROMPT_ID__", matter=number)` row
  with the answer wrapped in `prompt_id` and `end_id`, as `tests/test_stage4_exit.py:70-74` builds by hand; both
  rows of `recordings_for` kept this item); `tests/test_gates.py:164` (`extract.prompt_sha256`);
  `tests/test_fakemodel_bench.py:4` (`extract.CARD_TEXT` for the stage 2 row still); `tests/test_extract.py` (new).
- Ships: `card_version=4ab2bdb30535 card_name=bench_extract docx_import=1`; `recording_for` round trip: a
  `FakeModel` holding one `recording_for` row answers a live-nonce request with the nonce substituted (`recording_ok=1`);
  full suite unchanged in count (`537 passed`).
- CHECK: `scripts/run.sh pytest -q -s tests/test_extract.py tests/test_fakemodel_bench.py tests/test_stage4_exit.py`
  prints `card_version=4ab2bdb30535 card_name=bench_extract docx_import=1`, `recording_ok=1` and the stage 4 line
  `stage4 exit=0 gates=6 of 6 cases=14 of 14 runs=+14 answers=+21 empty_saved=0 server_stopped=1`, and passes;
  `grep -rn 11434 tests` lists only `tests/conftest.py` (none after this item) and `tests/test_config.py` rows (22,
  49, 50, 181: `config.load` only, no socket); the chair confirms the `ollama` request log on this Mac shows no
  request during the full suite (the method of §8 M6).
- Seeds, each alone: (a) one character added to `CARD_TEXT` -> `card_version` differs, red, and the stage 4 test's
  recordings no longer match (404 -> `gate.model`), red; (b) `recording_for` writes the answer without `end_id` ->
  `recording_ok=0`; (c) `extraction_card` building its own string instead of `extract.TEXT` -> `test_extract`'s
  `extraction_card().text is extract.TEXT` red; (d) `conftest.py:41` back to 11434 -> the grep line of the CHECK
  lists it, red.
- Librarian pre-flight: #R03-PC-3 (the version was measured, every caller of `benchrun` is listed in D0.4),
  #R04-PC-4 (the recording and the live request canonicalise the same way: the helper reuses `gates.messages`).

### W1 (lane A): gate 4 cites in text, mixed chunk, unbracketed cite forms (R5-2)
- Files: `src/casefile/gates.py:92-139` (`_references`: cite spans in `text` and `about` by the `bates-cites` rule's
  `cite_pattern` with the rule's flags, bodies read by `rules.cite_body`, looked up, removed before the digit check;
  `ask` passes `rules` through), `src/casefile/rules.py:76` (`cite_body(match)` helper, used here), `playbook/
  rules.toml:56` (§1.10 pattern; `good`, `bad`, `rule`, `why` unchanged), `tests/test_rules.py` (a `CITE_FORMS`
  table of 11), `tests/test_gates.py:36-41` (`CASES` gains `text_cite_ok`, `text_cite_bad`, `text_see_page`,
  `mixed_chunk`; `:79` prints `gate_cases=31 of 31`; `:89` `assert len(CASES) == 31`, plan review L8).
- Ships: `gate_cases=31 of 31`: `text_cite_ok` (9001.001, `facts[0].text` = its text plus ` [cite MED0001]`, quote
  `Date of service: 03/11/2025` without `0001`: `ok`, gate 4 pass, 13 read); `text_cite_bad` (` [cite MED0099]` ->
  `gate.quotes: 1 fault (faults=1): facts[0].text: cite MED0099 is not a page of this chunk; chunk pages: ...`,
  retry, failed); `text_see_page` (` see page 12` appended to `facts[0].text`: `gate.quotes: 1 fault (faults=1):
  facts[0].text: cite 12 is not a page of this chunk; chunk pages: ...`, retry, failed, no traceback; plan review
  M2); `mixed_chunk` (two invented pages `mixed/001` with stamp `MIX0001` and `mixed/002` unstamped, two
  facts, the second's text `The clinic recommends follow-up. [page mixed/002]`: `ok`, gate 4 pass (the span is a
  reference, no digit fault), gate 5 pass with message `warning: no Bates stamp on mixed/002; cites are page ids;
  facts[1].text: bates-cites: [page mixed/002]`, both pages read). `cite_forms=11 of 11`. `rules_selftest` still
  `misses=0 false_hits=0`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_gates.py tests/test_rules.py tests/test_fakemodel.py` prints
  `gate_cases=31 of 31` and `cite_forms=11 of 11` and passes; `scripts/run.sh python -m casefile.gate` prints `0`.
- Seeds, each alone: (a) `gates.py:241` `all(` -> `any(` -> `mixed_chunk` fails gate 5 (`bates-cites` error), red
  (the verifier's L1 seed); (b) the digit check run on the text with spans kept -> `text_cite_ok` fails `number 0001`,
  red; (c) spans stripped but not looked up -> `text_cite_bad` passes, red; (d) `cite_body` replaced by `group(1)` in
  `rules.py` -> the `see page 12` row raises `TypeError`, `cite_forms` at most 7 of 11, red; (d2) `group(1)` kept in
  gates -> `text_see_page` dies with `TypeError` out of `ask`, red; (e) the new alternatives dropped from
  `rules.toml` -> `cite_forms=8 of 11`, red; (f) the must-pass rows: pattern widened to `page\s*(\d+)` -> `a 12
  page report` or `Page 2 of 3` hit, red; the body class widened to `[A-Za-z0-9-]+` -> `He looked at page after
  page.` and `see page MED 0012` hit, red.
- Librarian pre-flight: #R04-V-2 and #R01-20 (this item), #R01-CX-7 and #R01-OC-H3 (both directions tested, must-pass
  list), #R04-CH-1 (the cite in text must be on the chunk's page, not anywhere), #R04-CX-1 (an ambiguous stamp inside
  a text cite is refused by the same lookup), #R01-V-B2 (the mixed case is the branch's own test).

### W2 (lane A): `pages.py`, `pipeline.py`, the coverage job filter
- Files: new `src/casefile/pages.py` (§1.3), new `src/casefile/pipeline.py` (§1.4: `RETRY_MARGIN`, `chunk`,
  `refuse`, `run`, `PipelineResult`, `RunResult` with `uncited: tuple[str, ...] = ()`, `bench_run` in W3),
  `src/casefile/runlog.py:135-145` (`coverage(matter, *, job)` and `open_items(matter, *, job)`: `job` is a required
  keyword with no default, joined through `runs`, so no caller can mix jobs by omission, plan review L3 and
  #R01-OC-M2; every caller named here passes its job: `src/casefile/gates.py:149-150` `open_items(log, matter, *,
  job)`, `tests/test_stage4_exit.py:199` and `tests/test_gates.py:188,264,268` pass `job="gates"`,
  `tests/test_runlog.py:254-269` pass `job="doctor"`, the job `_start` uses at `:13`), `tests/test_runlog.py` (one
  case: a `bench` run's `read` row is invisible to `coverage(job="memo")`; the printed `open_items=2 of 3` stays),
  new `tests/test_pages.py`, new `tests/test_pipeline.py` (in process through `FakeTransport`).
- Ships: `pages_ok=10 of 10`: bench layout of 9001.001 -> 14 pages, 0 open; an intake layout written in `tmp_path`
  (two binders, three records: `ok` with two stamps, `ok`, `empty` with reason `no text after OCR`; `binder.json`
  with `pages` 3 and 1 record respectively) -> 2 pages in binder name order with stamps `("KMR2344", "TWP7731")`, 1
  open `("scan/003", (), "empty", "no text after OCR")`; refusals (each `PagesError`, message naming the folder or
  file): no layout; both layouts; a record whose `matter` differs from the folder; `status` `done`; `binder.json`
  `pages` 4 against 3 records; `pages/<binder>` a symlink; a matter folder that is a symlink to another matter (the
  intake identity check); a folder name that is not a matter number. `chunks_ok=8 of 8` (plan review L4 recounted):
  (1) default card -> one chunk of 14 page ids in order; (2) `max_answer_tokens = 65536 - 16384` -> `[5, 5, 4]`
  pages with the page ids of §1.4; (3) a synthetic 9000-byte page under that card -> refused with the reason naming
  `9000 bytes` and the budget, no chunk; (4) no pages -> no chunks, no refusals; (5) a chunk's attempt 2 message
  (the retry line of a 2000-character reason added) still within `num_ctx - max_answer_tokens` for every chunk of
  the `[5, 5, 4]` split (the margin does its job); (6) `only_unread` with coverage `read` for 13 pages of 9001.001
  under job `memo` -> one chunk `["defense-report/001"]`; (7) the same rows under job `bench` -> all 14 (the
  filter); (8) the budget boundary (#R02-CH-1): under the `65536 - 16384` card a synthetic page whose block is
  exactly 7164 bytes fits as a one-page chunk and one of 7165 bytes is refused. `pipeline_ok=5 of 5`: one chunk replay ->
  one outcome ok, runs +1, 13 read; a refused page -> runs +1, one `failures` row `gate.truncation: page too long
  ...`, one coverage row `failed`, no `answers` row, no request to the stand-in; three chunks with per-chunk
  recordings (built in the test from the ideal: facts whose cite is in the chunk, flags whose cites all are) -> runs
  +3, 14 read, `chunks == [5, 5, 4]` by length; `no_reply` (a transport raising `ModelError(received=False)` on the
  second chunk) -> raises, runs +1 kept; `empty_answer` on a chunk -> that chunk's pages `failed`, the others read.
- CHECK: `scripts/run.sh pytest -q -s tests/test_pages.py tests/test_pipeline.py tests/test_runlog.py` prints
  `pages_ok=10 of 10 chunks_ok=8 of 8 pipeline_ok=5 of 5` and `open_items=2 of 3` and passes.
- Seeds, each alone: (a) `RETRY_MARGIN` set to 0 -> the retry-fit case red (`[5, 5, 4]` becomes a different split
  and the 2000-character retry overflows one chunk); (b) the refused page sent anyway -> the refusal case counts a
  request, red; (c) `only_unread` ignoring the job -> the `bench` rows case yields one chunk, red; (d) `pages.load`
  accepting `status` outside the three -> the `done` row loads, red; (e) the identity check dropped -> the symlinked
  matter folder loads, red; (f) a refused page written as `uncited` -> the status assertion red; (g) `coverage(job=)`
  filter ignored -> the new `test_runlog` case red; (h) `job` given a default of `None` meaning every job -> a
  `test_runlog` call without `job` must raise `TypeError` (asserted), red.
- Librarian pre-flight: #R03-CX-1 and #R01-V-B1b (links below a valid matter: `pages/<binder>`, `casefile.jsonl`,
  `outputs`), #R01-OC-M2 (`status` has no default; `only_unread` is a required keyword), #R03-V-L1 (a refusal
  happens before any model call), #R04-PC-6 (an empty page never reaches a chunk), #R02-CH-1 (a page exactly at the
  budget boundary is a case: fits), #R03-OC-L1 (every refusal names the page, the bytes and what to do).

### W3 (lane A, after W2): bench on the pipeline, `benchrun.py` removed
- Files: `src/casefile/pipeline.py` (`bench_run`, §1.12), `src/casefile/bench.py:7,17,87-108` (`runner=
  pipeline.bench_run`; `  uncited: <labels>` line after the details in model mode), `src/casefile/benchrun.py`
  (deleted), `tests/test_benchrun.py` (deleted after its reply-storage cases at `:155-389` are rewritten as
  `reply_rows` in `tests/test_bench_pipeline.py`; `tests/test_model.py:227-331` covers the client only, plan review
  H2), `tests/test_benchrun_done_reason.py` (rewritten against `pipeline.bench_run`: a missing `done_reason` ->
  `failure == "gate.truncation: the answer stopped before it finished (done_reason=None); not retried: the one retry
  was used"`, `pages_failed == 14`, two `failed` answers rows, two `gate.truncation` failures), `tests/test_bench_multi.py:8`
  and `tests/test_fix_cycle5.py:10` (`from casefile.pipeline import RunResult`), `tests/test_stage2_exit.py:37-46`
  (`INPROCESS_CHILD` patches `pipeline.ModelClient`; `pipeline.py` imports `ModelClient` by name),
  `tests/fakemodel/bench.py:18-28` (`recordings_for` returns the gates row only), `tests/test_fakemodel_bench.py`
  (drives the gates row: request body with `truncate: false`, `think: false`, a live nonce; the same four modes;
  prints `bench_recording_ok=1 modes=4 pages_in_request=14`), new `tests/test_bench_pipeline.py`.
- Ships: `bench_modes=12 of 12` (twelve modes listed, plan review M1 recounted; in process, `bench.main` with the
  transport patched): `replay` exit 0, first line `PERFECT` (model `qwen3.8:27b`), detail `  uncited: DEF0001`, last
  line `bench matters=1 imperfect=0`, runs +1, ok answers +1; `retry_ok` exit 0, runs +1, answers +2 (failed then
  ok); `truncated`, `cut_answer`, `unrepairable`, `bad_schema`, `bad_quote`, `forbidden_json`, `empty_answer` each
  exit 1 with `bench 9001.001 failure gate.<name>: ...` then `... pages_failed=14 of 14`, answers +2; `cut_prompt`
  and `prompt_too_long` exit 1, answers +1 (no retry); `no_reply` exit 2 with `bench: cannot run: no reply from the
  model server at ...`, no answers row. `reply_rows=9 of 9` (the `test_benchrun.py:155-389` cases against
  `pipeline.bench_run`, each with a transport of its own and `write_config`'s default host; `gates.ask` retries a
  received `gate.model` failure once (`gates.py:186-191`, `:275-277`), so each case asserts answers +2, both rows
  `failed` with the `raw_answer` named, `reply_received=True`, `pages_failed=14`, `failure` starting `gate.model:`,
  one `gate.model` failures row per attempt): (1) a 200 reply whose body is not JSON (raw = the body); (2) the
  stand-in serving another model tag, an `HTTPError` 404 with body (raw `{"error": "fakemodel: unknown model"}`);
  (3) a 503 returned without an exception, body over 200 bytes (raw = the whole body); (4) an `HTTPError` 503 with no
  body stream (raw `""`); (5) a 302 response object with a body and a `Location` (raw = the body); (6) an `HTTPError`
  307 with a body (raw = the body); (7) a real loopback server answering 302 through the real opener's redirect
  handler, `socket`-marked, on a port the test opened (raw = the body); (8) a 302 with an empty body (raw `""`);
  (9) a read timeout after the status line (raw `""`). `no_reply` of `bench_modes` is the control: no row.
  `bench_chunks=3 found=29 of 29 flags=5 of 9 runs=+3 uncited=1` (the three-chunk card from W2 with per-chunk
  recordings: the four cross-chunk flags G1, G3, G6, G9 are missed, `flags_missed: G1 G3 G6 G9` printed). Stage 2
  exit line unchanged: `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`. `grep -rn benchrun src tests scripts`
  -> no lines.
- CHECK: `scripts/run.sh pytest -q -s tests/test_bench_pipeline.py tests/test_stage2_exit.py tests/test_bench_multi.py
  tests/test_fix_cycle5.py tests/test_benchrun_done_reason.py tests/test_fakemodel_bench.py` prints `bench_modes=12
  of 12`, `reply_rows=9 of 9`, `bench_chunks=3 found=29 of 29 flags=5 of 9 runs=+3 uncited=1`, `stage2 exit=0 runs=+1 answers_ok=+1
  server_stopped=1`, `bench_recording_ok=1 modes=4 pages_in_request=14` and passes; `scripts/run.sh casefile bench
  --config config.example.toml --matters tests/fixtures/matters --candidate tests/fixtures/bench/flawed.json` prints
  the baseline line and its detail lines (W6 changes two of them) and exits 1.
- Seeds, each alone: (a) `pages_failed` counting uncited pages -> `replay` prints `pages_failed=1 of 14`, exit 1, red;
  (b) the `uncited:` line printed in candidate mode -> `test_bench_detail.py::test_perfect_has_no_detail` red; (c)
  `bench_run` sending only unread pages (`only_unread=True`) -> a second `replay` in the same log makes no request,
  `runs=+0`, red; (d) `reply_received` True on a never-answered transport -> `no_reply` exits 1, red; (e) the
  candidate built from the model's raw answer instead of the merged case file -> the three-chunk run's `found`
  differs only if merge changes anything (it does not on the fixture), so this seed must stay green and the brief
  says so; the control is (f): a fact repeated in two chunks' recordings (the test adds the same quote on a second
  page in chunk 2) -> merged candidate holds one fact with two cites, `extra` unchanged; built from raw answers,
  `extra` would count it twice, red; (g) `gates.py:189` `if not exc.received: raise` inverted or the `record_answer`
  call at `:275-277` skipped for a `ModelError` reply -> `reply_rows` cases (1) to (9) count 0 rows, red; (h) the
  real opener's redirect handler bypassed (a plain `urlopen`) -> case (7) follows the redirect to port 1 and is
  `no reply`, red.
- Librarian pre-flight: #R03-PC-3 (every pinned caller of `benchrun` named in D0.4 and changed here), #R02-V-F1 and
  #R02-V-F1b (every received reply is an answers row on every transport path, including the real opener's redirect
  handler: `reply_rows`), #R03-V-L1 (the pre-pass of D37
  is untouched: `duplicate_numbers_exit=2` still prints), #R01-CX-11 (exit codes asserted per mode).

### W4 (lane B, worktree): the case file store (`facts.py`)
- Files: new `src/casefile/facts.py` (§1.5, §1.6: `Event`, `CaseFile` with `facts`, `flags`, `runs`, `outputs`,
  `last_seq`, `changed_since(seq)`, `stale_outputs()`; `load`, `append`, `merge`, `CaseFileError`), new
  `tests/test_facts.py`. `merge` takes `(casefile, answer: dict, pages: Sequence[Page], run_id)` and resolves cites
  with the lookup of `gates.py:98-99` (import `stamps`, not `gates`).
- Ships: `casefile_ok=14 of 14`: append then load round trip (3 events, `seq` 1 to 3, `prev` chain); a line's text
  edited -> `CaseFileError` naming line 2; a line removed from the middle -> refused; a line in the middle cut short
  -> refused; a torn tail (the last line cut mid-object, no newline; plan review M5) -> loads with `torn` equal to
  the tail's byte count and `last_seq` of the line before, and `append` of one event truncates the tail, writes,
  and `load` then verifies the whole chain; a complete last line missing only its newline -> loads with `torn=0`
  and the next `append` writes the newline first; merge of the 9001.001 ideal answer against its pages -> 31 `fact` and 9 `flag` events with `page_id`s
  resolved (`G1` -> `["medical/001", "employer/001"]`); the same answer merged again -> 0 events; the same quote
  cited on a second page (an invented two-page matter) -> 1 `cite` event; a new `text` for a known quote -> 1
  `reading`; a known flag with a new `about` -> 1 `about`; a flag with the same cites in another order -> 0 events;
  `changed_since` counts after an `output` event; `stale_outputs()` empty right after the memo's `output`, then
  `["memo"]` after one more `fact`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_facts.py` prints `casefile_ok=14 of 14` and passes.
- Seeds, each alone: (a) `prev` not verified on load -> the edited-line case loads, red; (b) identity by `quote`
  instead of `fold(quote)` -> a curly-quote variant becomes a second fact, the repeat case yields 1, red; (c) flag
  identity by `about` -> the reordered-cites case or the new-about case red; (d) `append` opening with `"w"` -> the
  round trip loses lines, red; (e) `stale_outputs` comparing timestamps -> the stale case red (events carry a fixed
  `at` in the test); (f) `load` refusing a torn tail as a broken chain -> the torn case red; (g) `append` not
  truncating the tail -> the torn case's reload finds a broken chain, red; (h) a torn tail accepted anywhere but at
  the end (a cut line in the middle tolerated) -> the cut-middle case loads, red.
- Librarian pre-flight: #R01-CX-3 (append-only by construction, tested by the three corruption cases), #R02-CX-5
  (identities match what the scorer and the gates can tell apart: `fold` and the cite set), #R03-PC-2 (one changed
  character in a line is a broken chain), #R01-V-B2 (each refusal branch has its own case).

### W5 (lane B, worktree): the memo (`memo.py`): build, check, render, open and read back
- Files: new `src/casefile/memo.py` (§1.1, §1.2, §1.6, §1.7, §1.8: `OpenItem(page_id, label, status, reason)`,
  `Memo` of sections and paragraphs, `build(casefile, pages, open_items, *, playbook_version, model) -> Memo`,
  `check(memo, rules) -> findings`, `render(memo, path)` which calls `check` and raises `MemoError` on any error,
  `label(page)`), new `tests/test_memo.py` (python-docx opens the produced file).
- Ships: `memo_docx_ok=14 of 14` over one invented in-memory case file (three facts on three pages, `medical/001`
  with stamp `MED0001`, `medical/002` with `MED0002` and the unstamped `probe/001`; the first fact with two cites
  and two readings; one conflict; one gap with two `about`s; two open items, one `uncited` and one `empty` with
  stamps `KMR2344 TWP7731`; the memo built from two runs' coverage rows), read back from `docx.Document(path)`: (1)
  heading 0 `Medical memo: matter 9009.001`; (2) the built line names the playbook version and model tag; (3) `What
  changed since the last memo` says `First memo for this matter`; (4) `Outputs out of date` says `none`; (5) the
  `Open items` section holds exactly two paragraphs, `KMR2344 TWP7731 (scan/003): empty: no text after OCR` and
  `probe/002: uncited: no fact or flag cites probe/002`, in that order; (6) the conflict entry reads `Conflict
  between [cite MED0001] and [cite DEF0002].` followed by one `Model's reading: <about>` paragraph; (7) the gap entry
  `Gap at [cite MED0002].` is followed by two `Model's reading:` paragraphs, one per `about`, in case-file order
  (plan review L2); (8) the fact paragraph is `"<quote>" [cite MED0001]` with the quote in its own run and the cite
  in another; (9) `Also cited: [cite MED0002]` follows it; (10) two `Model's reading:` paragraphs follow; (11) the
  page heading is `medical page MED0001 (medical/001)`; (12) an unstamped page's fact ends `[page probe/001]` and
  the facts section opens with the rule's warning sentence naming `probe/001`; (13) by-page order (plan review M4):
  walking the paragraphs in document order, every quote paragraph of a page lies after that page's heading and
  before the next page heading, the headings run `medical/001`, `medical/002`, `probe/001`, and the `medical/002`
  section holds no quote paragraph (its only fact is the `Also cited` of the first, §1.1 (7), plan review L1); (14)
  the conflicts section opens with `Pages read in 2 runs; conflicts between runs are checked only for pages sent
  together.` (plan review H1). `memo_refused=2 of 2`: (a) a section title set to `IME summary` -> `MemoError`
  naming it, no file written; (b) a page of a binder named `ime` -> `MemoError` naming the binder, `no-dme-ime` and
  the remedy sentence of §1.3, no file written (plan review M8). `memo_changed=1`: a case file with a previous
  `output` and one later `fact` -> `1 fact added, 0 cites added, 0 readings added, 0 flags added` and `Outputs out
  of date: memo`. `memo_reason_exempt=1`: an open item whose reason holds the `no-dme-ime` rule sentence renders
  (the reason run is exempt).
- CHECK: `scripts/run.sh pytest -q -s tests/test_memo.py` prints `memo_docx_ok=14 of 14 memo_refused=2 of 2
  memo_changed=1 memo_reason_exempt=1` and passes.
- Seeds, each alone: (a) `render` skipping `check` -> `memo_refused=1 of 2`; (b) the quote and the cite joined in one
  run -> check 8 red; (c) the label built from the first stamp only -> check 5 red; (d) readings deduplicated by
  nothing (both readings dropped) -> check 10 red; (e) `check` run over the reason runs -> `memo_reason_exempt=0`;
  (f) the page heading by page id only -> check 11 red; (g) every fact filed under the first page heading, or facts
  in case-file order with the headings emitted first -> check 13 red; (h) one reading per flag -> check 7 red; (i)
  the runs sentence counting runs rather than runs with a `read` row -> check 14 red (the test's second run read
  nothing); (j) the binder check dropped -> `memo_refused=1 of 2`.
- Librarian pre-flight: #R04-PC-7 (nothing but the quote is presented as verified: every `text` is under a `Model's
  reading` label; seed (d)), #R03-OC-L1 (open lines name the page, the status and what happened), #R01-OC-M7 (`render`
  creates `outputs/` only, never the matter folder), #R01-CX-9 (the memo claims only what the gates verified).

### W6 (lane B, worktree): bench detail lines (R5-3 L3)
- Files: `src/casefile/benchscore.py:27,29` (`invented_facts: tuple[tuple[str, str, str], ...]`, `rule_hits:
  tuple[tuple[str, str, str], ...]`), `:56-57` (`invented: <cite> "<quote>" (<reason>)`), `:62-63` (`rules: <rule_id>
  <where> "<excerpt>"`), `:77-84` (reason `no such page` when `page is None`, else `quote not on the page`),
  `:116-119` (excerpt kept), `tests/test_bench_detail.py:17-24,28-31` (`  invented: MED0003 "Patient was lifting 80
  pounds." (quote not on the page)`, `  invented: MED0099 "Date of service: 03/11/2025" (no such page)`, `  rules:
  no-dme-ime DEF0003 "IME"`, `  rules: no-dme-ime flag MED0002 "IME"`), `tests/test_benchscore.py` (a table row per
  reason and the excerpt tuple), `tests/test_bench_cli.py` and `tests/test_fix_cycle*.py` wherever `grep -rn
  "invented: \|rules: " tests` finds a pinned line (the builder lists every file it changed).
- Ships: `invented_kinds=2 of 2`, `rule_excerpt_ok=1`; the flawed bench prints the two new `invented:` lines and the
  new `rules:` line, the main line unchanged; the perfect candidate still prints no detail line.
- CHECK: `scripts/run.sh pytest -q -s tests/test_bench_detail.py tests/test_benchscore.py tests/test_bench_cli.py`
  prints `invented_kinds=2 of 2 rule_excerpt_ok=1` and `bench_detail_flawed exit=1 detail_lines=6` and passes;
  `scripts/run.sh casefile bench --config config.example.toml --matters tests/fixtures/matters --candidate
  tests/fixtures/bench/flawed.json` prints the baseline main line, exit 1.
- Seeds, each alone: (a) both reasons `quote not on the page` -> `invented_kinds=1 of 2`; (b) the excerpt replaced by
  the whole text -> `rule_excerpt_ok=0` (the expected excerpt is `IME`, the matched span, `rules.py:79`).
- Librarian pre-flight: #R03-OC-L1 (words, not a pattern; the reason says which kind), #R03-PC-3 (every pinned
  detail line found by grep and moved).

### W7 (lane A, after the merge of lane B): `casefile memo`, `casefile status`, the intake-layout memo
- Files: new `src/casefile/memo_job.py` (`run(config, number, *, out, err, opener=None) -> int`: §1.3 order:
  config, playbook, pages, run log, case file, `pipeline.run(only_unread=True, job="memo")`, merge and append after
  every passing chunk, open items from coverage (job `memo`) plus `open_pages`, `memo.build`, `memo.render` to
  `outputs/memo.docx`, the `output` event, the printed lines, exit code), new `src/casefile/status.py` (§1.14),
  `src/casefile/cli.py:28-36` (subparsers `memo --matter N [--config]`, `status --matter N [--config]`), new
  `tests/test_status.py`, new `tests/test_memo_intake.py` (copies `scanned_intake`'s matter folder with
  `shutil.copytree` under its own `write_config(tmp_path)` matters root and runs there, so the session-scoped folder
  that `tests/test_intake.py:421-445` and `tests/test_stage3_exit.py:50-55` read is never written to, plan review
  L7; in process through `FakeTransport` on `write_config`'s default host `127.0.0.1:9`, plan review M6; the chunk's
  recording is built in the test from the loaded pages with one fact per page whose quote is that page's
  `must_contain` span from `tests/fixtures/scanned/scanned.json` and one gap flag citing `KMR2345`; the `about`
  text invented in the test). `memo_job.run` checks the binder names against the rules before the run log opens
  (§1.3, §1.8).
- Ships: the printed line `memo <number> chunks=C runs=+R read=X open=O facts=F conflicts=K gaps=G new_facts=A
  new_flags=B memo=<path>` and the open lines of §1.7. `status_ok=6 of 6` (in process, 9001.001 copied under
  `write_config`'s matters root): before any run `pages=14 read=0 failed=0 uncited=0 empty=0 open=14 facts=0
  conflicts=0 gaps=0 outputs=none` (every page open with status `unread`, reason `no run has read this page`); after
  a replay memo run `read=13 uncited=1 open=1 facts=31 conflicts=5 gaps=4 outputs=memo:current`; after one appended
  `fact` event `outputs=memo:stale`; the open line `  open: DEF0001 (defense-report/001): uncited: no fact or flag
  cites defense-report/001`; exit 0; a missing matter folder -> exit 2 with the path; the 9001.001 copy with its
  `medical` binder renamed `ime` in both `matter.toml` and `records/` -> `casefile memo` exit 2 with the §1.3
  binder refusal, no run log row, no request to the stand-in (`binder_refused=1`). `memo_intake 9002.001 chunks=1
  read=5 open=1 facts=5 gaps=1 label_ok=1 exit=1`: the open line is `  open: scan/004: empty: no text after OCR`
  (`label_ok` is the memo paragraph `scan page KMR2344 TWP7731 (scan/003)` present in the produced file, critic M2 on
  a two-stamp page) and the docx holds five quote paragraphs each ending `[cite KMR234<n>]`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_status.py tests/test_memo_intake.py` prints `status_ok=6 of 6
  binder_refused=1` and `memo_intake 9002.001 chunks=1 read=5 open=1 facts=5 gaps=1 label_ok=1 exit=1` and passes;
  `ls <scanned_intake root>/9002.001` after the test shows `records` and `pages` only.
- Seeds, each alone: (a) the empty intake page sent to the model anyway -> the stand-in has no recording for a
  six-page chunk, 404, `read=0`, red; (b) `status` reading coverage with `job="bench"` after a bench run on the
  same number (the test runs `bench_run` first) -> `read=13` before any memo run, red; (c) `outputs` judged by file
  mtime -> the stale case red; (d) exit 0 with open items -> `exit=1` assertion red; (e) the memo written before
  `check` -> covered by W5 (e); (f) `memo_job` writing the case file before the outcome passed (merge of a failed
  outcome) -> a `bad_schema` run adds fact events, red (`test_status` includes one failed run: `facts` stays 31);
  (g) the binder check moved after the run log opens -> `binder_refused` finds a run row, red; (h) `opener` not
  threaded into `ModelClient` -> on host `127.0.0.1:9` the memo exits 2 `no reply`, `memo_intake ... exit=1` red,
  and nothing was sent anywhere.
- Librarian pre-flight: #R03-V-L1 (the refusals of §1.3 happen before the run log opens and before any call),
  #R03-CX-2 (`outputs/` is created by this run only; a failed render leaves no partial file: write to
  `memo.docx.tmp` then `os.replace`), #R01-OC-M7 (never create the matter folder), #R04-CX-1 (labels show stamps,
  keys stay page ids), #R01-CX-11 (exit codes asserted: 0, 1, 2).

### W8 (lane A, after W7): the stage 5 exit test
- Files: new `tests/test_stage5_exit.py` (socket test in the style of `tests/test_stage2_exit.py` and
  `tests/test_stage4_exit.py`: one stand-in server on a loopback port with `recordings_for(MATTER)` plus
  `recording_for(card, (the DEF0001 page,), "9001.001", {"facts": [{"cite": "DEF0001", "quote": "The examinee reports
  lifting a tote of about 60 pounds.", "text": "The examinee reported lifting a tote of about 60 pounds."}], "flags":
  []})`; the fixture matter copied with `shutil.copytree` under `write_config`'s matters root; four runs of
  `scripts/run.sh casefile memo --matter 9001.001` as subprocesses with `CASEFILE_CONFIG`, the mode switched through
  `POST /_fake/mode` between them; `casefile status` after runs 1 and 3; the docx opened after runs 1, 2 and 3 with
  `docx.Document`), `docs/loop/round-05/` (the chair's records, not the lane).
- Ships, printed with `capsys.disabled()`, every number asserted:
  `stage5 run=1 mode=replay exit=1 chunks=1 runs=+1 read=13 open=1 facts=31 conflicts=5 gaps=4 new_facts=31 new_flags=9`
  `stage5 run=2 mode=bad_schema exit=1 chunks=1 runs=+1 read=13 open=1 facts=31 conflicts=5 gaps=4 new_facts=0 new_flags=0`
  `stage5 run=3 mode=replay exit=0 chunks=1 runs=+1 read=14 open=0 facts=32 conflicts=5 gaps=4 new_facts=1 new_flags=0`
  `stage5 run=4 mode=replay exit=0 chunks=0 runs=+0 read=14 open=0 facts=32 conflicts=5 gaps=4 new_facts=0 new_flags=0`
  `stage5 memo=1 quotes=31 of 31 by_page=1 cites=45 readings=31 conflicts=5 gaps=4 runs_seen=1 open=1 open_status=uncited rule_hits=0 changed=first`
  `stage5 memo=2 quotes=31 of 31 by_page=1 cites=45 readings=31 conflicts=5 gaps=4 runs_seen=1 open=1 open_status=failed rule_hits=0 changed=0`
  `stage5 memo=3 quotes=32 of 32 by_page=1 cites=46 readings=32 conflicts=5 gaps=4 runs_seen=2 open=0 open_status=none rule_hits=0 changed=1`
  `stage5 status read=13 then 14 open=1 then 0 outputs=memo:current`
  `stage5 exit=0 runs=4 of 4 memos=3 of 3 answers=+4 casefile_lines=48 chain_ok=1 server_stopped=1`
  where: run 1 sends the one chunk of 14 pages (the `gates-9001.001` recording), reads 13, leaves `DEF0001` uncited
  (D0.8); run 2 re-sends `DEF0001` alone under `bad_schema` (retry, both attempts fail, answers +2), the page is
  `failed` with reason `gate.schema: the answer does not match the schema: facts[0].text: missing required key; the
  page stays open until a later run reads it`; run 3 re-sends it under `replay` (the one-page recording), reads it,
  one fact added; run 4 has nothing unread, makes no call, rebuilds the memo (`What changed`: `0 facts added ...`).
  `quotes` = every quote of the case file present verbatim in a quote run; `by_page` = 1 when every quote paragraph
  lies after the heading of the first page its fact cites and before the next page heading, the headings in binder
  order (plan review M4); `runs_seen` = the N of the conflicts sentence of §1.1 (5), equal to the distinct run ids
  among the memo job's `read` coverage rows (1 after run 1, still 1 after the failed run 2, 2 after run 3; plan
  review H1); `cites` = `[cite ` tags in the document
  (31 fact cites plus 14 flag cites, then 32 plus 14); `readings` = `Model's reading:` paragraphs; `open` = entries
  of the `Open items` section and `open_status` the status word on the only entry; `rule_hits` = `Rules.check`
  errors over every paragraph that is not a quote run or a reason run (0); `changed` = `first`, then the facts count
  of the `What changed` section. `answers` is the run log delta over the four runs (1 + 2 + 1 + 0). `casefile_lines`
  = 42 after run 1 (31 fact, 9 flag, 1 run, 1 output), 44 after run 2 (run, output), 47 after run 3 (fact, run,
  output), 48 after run 4 (output); `chain_ok` = `facts.load` succeeds on the final file. `memos=3 of 3` are the
  three docx readings that matched. `server_stopped` as the other exit tests.
- CHECK: `scripts/run.sh pytest -q -s tests/test_stage5_exit.py` prints the nine lines above with `stage5 exit=0` and
  passes; the test asserts every number and fails on any miss.
- Seeds, each alone: (a) `only_unread` off -> run 2 sends 14 pages, the stand-in's `bad_schema` edits the big answer,
  `read=0`, red; (b) a failed outcome merged -> run 2 `new_facts` not 0 or `casefile_lines` off, red; (c) the memo's
  open section built from `uncited` rows only -> `memo=2 open_status` red; (d) `Also cited` and readings aside, the
  quote run holding the quote plus the cite in one run -> `quotes=0 of 31`, red; (e) `output` event not appended on a
  run with no new chunk -> `casefile_lines=47`, red; (f) exit 0 on open items -> run 1 `exit=1` red; (g) the hash
  chain not written -> `chain_ok` stays 1 (load does not verify what was never written) unless W4's seed (a) is also
  applied, so this seed is not claimed; the control is W4 (a); (h) every fact filed under the first page heading ->
  `by_page=0`, red; (i) the runs sentence counting run rows -> memo 2 `runs_seen=2`, red.
- Librarian pre-flight: #R01-P-1 (the server is stopped in `finally`), #R01-CX-11 (the exit codes of the four runs
  are asserted), #R02-OC-H1 (the one-page recording's quote was read on `defense-report/001.txt:20`), #R04-PC-6 (run
  4 saves nothing empty: no `answers` row, no fact), #R03-PC-3 (every number above was derived from D0.8 and §1.4;
  the builder re-derives them before asserting).

### W9 (chair, at the close): records
- `docs/spec.md` §9 D39 to D43 (§6), §4 rules 4 and 5 sentences, §7 stage 5 row text unchanged, §11 stage 5 row;
  `docs/loop/tuning-questions.md` T-20 (`RETRY_MARGIN`), T-21 (re-sending open pages every run); `Librarian.md`
  round 5 entries; ledger baselines (`gate` 0, suite count and `suite_time`, the stage 5 lines, the bench lines with
  their new detail lines, the `uncited:` line in model mode).

## §3 Parallelisation map

- Builders: every work item is coded by Codex `gpt-6.1-sol` through `codex exec -C <tree> -m gpt-6.1-sol -s
  workspace-write -c sandbox_workspace_write.network_access=true ... < /dev/null`, one item per run, started by the
  chair; builders do not commit; the chair re-runs each CHECK and the seeds, runs the gate and commits with targeted
  paths. The plan review and the code review (8a) are fresh Fable agents, read-only (Q46).
- W0 first: the chair's `uv add` and worktree `uv sync`, then one builder in the main tree, committed by the chair;
  both lanes start from that commit.
- Lane A (main tree): W1, W2, W3, in that order. Owns `src/casefile/gates.py` (`_references`, `ask`, and
  `open_items` at `:149-150`), `rules.py`, `playbook/rules.toml`, `pages.py` (new), `pipeline.py` (new),
  `runlog.py:135-145`, `bench.py`, `benchrun.py` (deleted), `tests/fakemodel/bench.py` (after W0),
  `tests/test_gates.py` (including `:89` and the `open_items` calls at `:188,264,268`), `test_stage4_exit.py:199`
  (`job="gates"` only), `test_rules.py`, `test_pages.py` (new), `test_pipeline.py` (new), `test_runlog.py`,
  `test_bench_pipeline.py` (new; `bench_modes`, `reply_rows`, `bench_chunks`), `test_benchrun.py` (deleted),
  `test_benchrun_done_reason.py`, `test_bench_multi.py:8`, `test_fix_cycle5.py:10`, `test_stage2_exit.py:37-46`,
  `test_fakemodel_bench.py`. `tests/conftest.py:41` is W0's (the chair's commit before the lanes split) and neither
  lane touches `conftest.py` after it.
- Lane B (worktree `.claude/worktrees/r5-lane-b`, branch `r5/lane-b` from the W0 commit, toolchain
  `~/.casefile-dev/r5-lane-b` synced by the chair with the sandbox off after W0's `uv add`; the builder's `codex exec`
  runs with that worktree as its working directory): W4, W5, W6, in that order. Owns `src/casefile/facts.py` (new),
  `memo.py` (new), `benchscore.py`, `tests/test_facts.py` (new), `test_memo.py` (new), `test_bench_detail.py`,
  `test_benchscore.py`, `test_bench_cli.py` (detail-line pins only).
- Shared-file splits: `bench.py` is lane A's (runner swap, `uncited:` line); lane B's `benchscore.py` changes the
  `Score` tuples and `details()` only, and `bench.py:104-107` calls `score(...)` and `details()` by the same names, so
  the merge is clean. `test_bench_cli.py`: lane B edits only lines that pin `invented:` or `rules:` detail lines;
  lane A does not touch it. `facts.merge` imports `stamps` and `quotes`, never `gates` or `pipeline` (no import cycle
  with lane A). `memo.py` takes `matter.Page` objects and `OpenItem`s, never a run log (lane A's W7 adapts).
- Sequential and why: W0 before both lanes (the docx dependency is in the lock before the worktree syncs; `extract`
  is used by A's W2 and B's W5 tests); W3 after W2 (bench runs the pipeline); the merge of B into A's tip by the
  chair, then the full suite, gate and bench baselines; W7 after the merge (it joins `pipeline`, `facts`, `memo`,
  `status`); W8 after W7; then the plan's critic round (Fable 8a, Opus critic, Opus verifier).
- Interfaces fixed by this brief so the lanes do not wait on each other: `pipeline.run(...) -> PipelineResult(outcomes,
  refused, chunks)` (A); `facts.load`, `append`, `merge(casefile, answer, pages, run_id) -> events`, `CaseFile.facts`,
  `flags`, `changed_since`, `stale_outputs` (B); `memo.OpenItem`, `memo.build(casefile, pages, open_items, *,
  playbook_version, model)`, `memo.render(memo, path)`, `memo.label(page)` (B); `extract.card()` (W0).

## §4 Test design

- Regression set unchanged in meaning: stage 1 to 4 exit lines (stage 4 untouched: `extraction_card` keeps the card
  text and name); the stage 2 line `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1` with the same perfect main
  line (one chunk, one run, one ok answer); the two `--candidate` bench main lines byte-identical; `gate` 0;
  `unused_imports=0`; `suite_time.sh 3` under 90 s; doctor `runlog_schema PASS schema=2 triggers=21 (counted)`
  (schema untouched). Numbers that move on purpose: `gate_cases=27 of 27` -> `31 of 31` (W1); the two `invented:`
  detail lines and the `rules:` line gain a reason and an excerpt (W6); model-mode bench prints `  uncited: DEF0001`
  after the details (W3; `test_stage2_exit` asserts first and last line only, D0.10); `benchrun_modes=8 of 8` and
  the reply-storage tests of `test_benchrun.py:155-389` are retired with `benchrun.py` and replaced by
  `bench_modes=12 of 12` and `reply_rows=9 of 9` (W3); the suite count changes (the chair sets the baseline at the
  merge). `test_fakemodel.py:151` (`len(MODES) == 17`) is untouched: no mode is added. `write_config`'s default
  host is `http://127.0.0.1:9` from W0 (plan review M6): a test that needs a live stand-in names the port it opened.
- New tables, each a `*_ok=N of N` or fixed line: `pages_ok` 10, `chunks_ok` 8, `pipeline_ok` 5, `bench_modes` 12,
  `reply_rows` 9, `casefile_ok` 14, `memo_docx_ok` 14, `memo_refused` 2, `cite_forms` 11, `status_ok` 6,
  `binder_refused` 1, `invented_kinds` 2, the `bench_chunks` line, the `memo_intake` line, the nine `stage5` lines
  (the three `memo=` lines carry `by_page` and `runs_seen`). Every N is fixed above so a builder cannot pad or trim
  a table unnoticed; the plan review found two miscounts in the first draft (M1, L4) and every N was re-derived for
  this revision.
- Every memo check opens the produced `.docx` with python-docx and reads paragraphs and runs; no test asserts a file
  name beyond the path it passed in. Quote runs and cite runs are separate runs so a test can tell the verified text
  from the cite and from the model's reading.
- Suite time (T-11, T-18): W3 removes `test_benchrun.py` (about 20 tests, one socket test) and adds
  `test_bench_pipeline` (in process but for `reply_rows` case 7, one socket test); W8 adds four `run.sh` subprocess
  runs (about 0.5 s each) and three docx readings; W7's intake-layout memo copies the `scanned_intake` folder
  (small) and shares its one real OCR run (no new OCR). Acceptance: `scripts/run.sh scripts/suite_time.sh 3`
  exits 0 with nothing else running. If over: the second lever of T-18 (`test_config.py::test_matters_alias_table`
  in process) is pre-approved; never a skip.
- Tuning entries for the chair to append at close: T-20 `pipeline.RETRY_MARGIN = 8192` bytes (measure the longest
  `Retry:` line in the run log on the Studio; shrink only to a measured maximum with margin); T-21 open pages are
  re-sent on every memo run (count re-sends per matter on the stage 9 benchmark; question 55).
- Open for the code review (8a): the hash chain under concurrent appends (two memo runs on one matter at once; the CLI
  has no lock this round; the torn-tail truncation of §1.5 must never run while another process appends); `pages.load`
  on a binder folder with a gap in page numbers (`001`, `003`); a `text` whose bracketed cite body is a range
  (`[cite MED0001-MED0003]`) failing gate 4 by design (§1.9); docx paragraph order when a page has facts from two
  runs (the by-page check of W5 (13) holds whatever the run order).

## §5 Risks, each with a measurable tripwire

- R1 The retry prompt of a chunk near the budget overflows (`gate.truncation: over budget` on attempt 2) and the same
  chunk fails on every run. Tripwire: any `gates` row with `attempt = 2` and message starting `gate.truncation: the
  prompt is too long` in a run log is a defect of `RETRY_MARGIN` (T-20); W2's retry-fit case and seed (a) prove the
  margin on the fixture split.
- R2 A cover sheet or index page stays open forever and is re-sent on every memo run: two model calls per run
  (gate 6 fails the empty answer, the one retry is used, plan review M7) and its status reads `failed` with the
  `gate.coverage` reason after the first re-send. Tripwire: the stage 9 report counts re-sent pages per memo run
  and the `gate.coverage` rows per matter; question 55 and T-21. On the fixture run 4 sends nothing (every page
  read), so the loop sees the opposite case only.
- R3 Conflicts between records in different chunks, and between records read in different runs, are never flagged
  (the card sees one chunk; only unread pages are sent; plan review H1). Tripwire: W3's `bench_chunks=3 found=29
  of 29 flags=5 of 9` is the measured cost on the fixture when split in three; the memo's conflicts section states
  the run count and the limit (`runs_seen` in W8); the stage 9 benchmark on real closed matters (larger than one
  chunk, intaken in more than one run) reports `flags_missed` by cross-chunk and cross-run pairs before a reconcile
  card is designed; question 56 holds the fill proposal.
- R4 python-docx (lxml) fails to install or to import on the Studio's Python. Tripwire: `docx_import=1` in W0's CHECK
  and `casefile doctor` unchanged (no new doctor row: the import error would surface at `casefile memo` as a
  traceback, which the chair checks by running the memo on this Mac before the merge).
- R5 A memo written into the checkout trips the privacy row. Tripwire: the gate's `privacy` row (`offenders=0`) after
  every chair run of `casefile memo`; `write_config` keeps matters under `tmp_path` (D0.10); the memo path is derived
  from `[paths].matters` only.
- R6 The case file and the run log disagree (a fact merged from a run whose coverage says failed). Tripwire: W7 seed
  (f) and W8 run 2 (`new_facts=0` after a failed chunk); `facts.load` after the exit test (`chain_ok=1`).
- R7 The `cite_pattern` widening over-blocks ordinary prose in a later stage's outputs. Tripwire: `cite_forms=11 of 11`
  must-pass rows; the stage 6 output critic reads every `bates-cites` finding; T-5's measure applies.
- R8 Lane B's `Score` tuple change breaks a pinned line lane A did not list. Tripwire: `grep -rn "invented: \|rules: "
  tests` run by the chair at the merge must match W6's changed-file list exactly.
- R9 The exit test's counts (`cites=45`, `casefile_lines=48`) drift when a fixture or the one-page recording changes.
  Tripwire: the test derives `cites` from the case file it reads back and compares to the document count, and the
  brief's arithmetic (§2 W8) is re-derived by the builder and the verifier from D0.8.
- R10 A test reaches the owner's `ollama` on 127.0.0.1:11434 (plan review M6; the chair's reading of the server's
  request log shows no suite request tonight, so prevention, not a leak). Tripwire: `write_config`'s default host
  is port 9 from W0; W0's CHECK greps `tests` for `11434`; the chair reads the `ollama` request log after the full
  suite at the merge and at the close and records `ollama_requests=0` in the round report.
- R11 A torn tail is truncated while another process is appending (the CLI has no lock). Tripwire: open for the
  code review (§4); the stage 8 job runner's one-at-a-time lock closes it; until then the owner runs one memo at a
  time (HANDOFF note).

## §6 Contradictions and new spec rows (pending veto)

- **D39** (D25, D35 executed; §5 benchmark row amended). Old text (D35 tail): "the stage 2 runner's own guards stay
  until stage 5". New: "From stage 5 `casefile bench` runs the gate pipeline (`pipeline.bench_run`): every page of
  the matter, chunked by bytes in page order (`pipeline.chunk`, `RETRY_MARGIN`), one run row per chunk, the candidate
  built from the merged in-memory case file; `pages_failed` counts pages with coverage `failed` (a failed chunk or a
  page too long for one prompt); a `uncited:` detail line lists pages no passing answer cited, in model mode only;
  `benchrun.py` and its recording row are removed; the extraction card is `extract.card()` (name `bench_extract`,
  version unchanged)." Why: §1.4, §1.12, T-9 measured on the fixture.
- **D40** (new; spec §3 step 5 and §5 case file row made concrete). "The case file is `<matters>/<number>/
  casefile.jsonl`: one JSON object per line with a contiguous `seq` and a `prev` sha256 of the previous line; kinds
  `fact`, `cite`, `reading`, `flag`, `about`, `run`, `output`; a fact's identity is the folded quote (`quotes.fold`),
  a flag's the kind and page-id set; a repeated fact on a new page adds a `cite`, a new wording a `reading`, a
  repeated flag with new wording an `about`; a broken chain refuses the matter (exit 2); nothing complete is
  rewritten: a torn tail after the last newline that is not a JSON object is reported, ignored by `load` and
  truncated by the next `append`, which also `fsync`s every write." Why: §1.5, §1.6; pillars 2 and 5; plan review
  M5.
- **D41** (new; spec §2 running memo and §3 step 6 at stage 5). "`casefile memo --matter N` reads the matter's pages
  (intake layout, or the bench layout of a benchmark matter copied under `[paths].matters`), sends only pages not
  yet read by the memo job, merges every passing chunk, and writes `outputs/memo.docx` with python-docx (no template
  file): title and build line, what changed since the last memo, outputs out of date, open items by stamp,
  conflicts (opening with the number of runs that read pages and the sentence that conflicts between runs are
  checked only for pages sent together), gaps, verified facts by record page (a fact under the first page that cited
  it, with `Also cited` for the others; every paragraph of a page between its heading and the next) with the quote
  as the verified text and every model sentence, one paragraph per reading or about, labelled `Model's reading`; the
  memo's own words pass the firm rules before the file is written (quote runs and run-log reasons exempt), and a
  binder whose name fails a firm rule is refused before any model call with the remedy named; exit 0 all read, 1
  open items listed, 2 cannot run; the sections are an owner interim (question 50)." Why: §1.1, §1.2, §1.3, §1.7,
  §1.8; Q48 interim; plan review H1, L1, L2, M4, M8, L10.
- **D42** (D38 amended; spec §4 rule 4 sentence "every number in a fact's summary is in its quote" becomes "every
  number in a fact's summary outside a bracketed cite is in its quote, and a bracketed cite inside a summary or a
  flag's about is itself a reference to a page of the chunk"; rule 5 gains "a chunk with any unstamped page runs the
  cite rule as a warning and names the unstamped pages"). The `bates-cites` rule also matches `see page N`, `at p. N`
  and `(Ex. X at N)` forms where N is a number or a stamp-shaped token, never the next word (R1-20); the cite body
  of any form is read by one helper shared by the rule and gate 4. Why: §1.9, §1.10, §1.11; verifier L1 and L2;
  Librarian #R04-V-2; plan review M2, M3.
- **D43** (new; §8b `matter_status` and critic M2, L3). "`casefile status --matter N` prints pages, read, failed,
  uncited, empty, open, facts, conflicts, gaps and outputs (`memo:current`, `memo:stale`, `none`), then one line per
  open item labelled by every stamp of the page with the page id in parentheses, keyed by page id; the bridge returns
  these counts. Bench detail lines say `(no such page)` or `(quote not on the page)` and carry the rule's matched
  excerpt." Why: §1.7, §1.13, §1.14.
- No owner ruling is overridden. Q47 and Q48 interims are applied as written (an uncited page stays open until a
  later run's passing answer cites it, which D38 already allows; no summary is shown as verified). Q49's interim
  (rule id beside the message) is kept in every line. Spec §7's "stage 6 adds the medical memo card" stands: this
  round's memo is built by code from verified material and takes no card.

## §6b Privacy

Every fixture this round adds is invented: the one-page recording in `tests/test_stage5_exit.py` quotes an invented
sentence of the invented defense report page (`tests/fixtures/matters/9001.001/records/defense-report/001.txt`); the
intake-layout records written by `tests/test_pages.py` reuse the invented stamps `KMR2344`, `TWP7731` and the clinic
names of `tests/fixtures/scanned/scanned.json`; the memo test's in-memory case file uses invented matter `9009.001`,
quotes and abouts written in the test; `tests/test_memo_intake.py`'s answer uses the `must_contain` spans of the
invented scanned binder and an invented gap sentence; the mixed-chunk pages in `tests/test_gates.py` are two invented
sentences. No PDF, image or Word file is added to the repo; every `.docx` a test produces lives under `tmp_path` and
is never copied into the checkout. No real client record, name or fact appears in this brief, in any test or in any
probe; nothing outside this repo was read (the Claude skills of spec §6, `~/local-worker/`, the owner's matters).

## §7 Questions only the owner can answer (appended to `docs/loop/questions-for-owner.md` as 50 to 57; 54 and 55 amended after the plan review)

50. The stage 5 memo lists verified facts by record page (binder, then page), each as the quoted record text with
    its cite and the model's one-sentence reading labelled as such, then conflicts, gaps and open items. Spec §2
    names a treatment chronology, providers, diagnoses, restrictions, history and the two sides' opinions as sections.
    Do you want those sections (which needs a date and a category per fact from the stage 6 memo card), and in what
    order should the memo run? Interim: by record page, in binder order, with the quote as the text; no chronology or
    category sections until the memo card exists.
51. Should the memo use a firm Word template (letterhead, styles, caption block)? If so, where does the template
    live on the Studio (it cannot be committed to the repo)? Interim: python-docx default styles, no template.
52. Cites in the memo follow the playbook's good example, `[cite MED0001]` after each quote. Is that the form you
    want in a memo you read, or a footnote or parenthetical `(MED0001)`? Interim: the bracketed form.
53. For a binder with no Bates stamps the memo cites the page id in brackets, `[page medical/001]`, and opens the
    facts section with the rule's warning naming those pages. Acceptable until the binder is stamped? Interim: yes.
54. A conflict entry shows the two cites and the model's sentence about the disagreement, labelled as the model's
    reading; no quoted passage is attached, because the flag carries none. Should the memo also show the facts
    quoted from those two pages beneath the conflict? And in what order should conflicts run: as found, or those
    between a defense examination and our records first (your question 41 priority; the code can tell binders apart
    only by the names you give them)? Interim: cites and the labelled sentence only, in the order found.
55. A page that stays open (failed, or cited by nothing) is sent to the model again on every memo run, alone if
    nothing else is unread. A cover sheet re-sent alone comes back with no facts and no flags, which the checks
    treat as a failed answer and retry once, so it costs two model calls per run for the life of the matter, and
    from then on it is listed as `failed` with the reason "the answer has no facts and no flags" rather than
    "uncited". Acceptable, or should re-sending need your say-so per page? Interim: re-sent every run; nothing
    else closes a page (question 47); the reason is shown verbatim.
56. When new records arrive after the first memo run, only the new pages are sent to the model, so a conflict
    between a new page (say, a defense report) and a page already read (our medical records) can never be flagged:
    the model only sees pages sent together. The plan reviewer proposes filling each run's prompt with already-read
    pages up to the budget so the new record is read beside the old; that re-reads the old pages on every later run
    (more time on the Studio per run, and a page the model fails to cite the second time would turn from read to
    open) and on the test matter it re-sends the whole matter. Do you want the re-send, and how much (the whole
    matter when it fits, or only the binder you name), or should cross-run conflicts wait for the stage 6 reconcile
    card that compares one new fact with the case file? Interim: no re-send; the memo's conflicts section states
    how many runs read pages and that conflicts between runs are not checked.
57. The firm rule against "DME" and "IME" also catches a binder name you type at intake (`ime`,
    `defense-medical-exam`) because the memo's headings and cites carry the binder name. Is a folder label "our
    words" that the rule should govern, or should intake refuse such a name up front, or should the memo show it
    as typed? Interim: the memo refuses to run and names the binder, the rule and the remedy (remove the binder
    by hand and intake it under another name, question 34); intake does not check names this round.

## §8 Plan review dispositions

Every finding was re-checked in the code on `4755170` or by a read-only probe through `scripts/run.sh python -c`
before it was accepted or rejected; the evidence is the file and line or the measured value.

| Finding | Disposition | Evidence and what changed |
|---|---|---|
| H1 cross-run conflicts | ACCEPTED in part, rest OWNER (Q56) | `benchrun.py:19` "A conflict is two pages that disagree"; `gates.py:96-99` resolves cites against the chunk only; §1.4 sends unread pages only. Decided on the pillars: the memo's conflicts section opens with `Pages read in N run(s); conflicts between runs are checked only for pages sent together.` (§1.1 (5)), W5 check (14), W8 `runs_seen=1, 1, 2` and seed (i); re-found facts merge to nothing (§1.5), so a later fill is safe. The fill itself is Q56 with the fail-closed interim (no fill): on the fixture it re-sends all 14 pages and the ideal answer still leaves `DEF0001` uncited, and a re-sent page the model fails to cite would flip from `read` to `uncited`, which needs a ruling. R3 rewritten. |
| H2 reply-storage tests lost | ACCEPTED | `tests/test_benchrun.py:155-389` holds the nine runner-level cases (non-JSON 200, 404 with body, 503 status path, 503 without stream, 302 and 307 with body, a real loopback 302 through the real opener, empty-body 302, read timeout); `tests/test_model.py:227-331` has no `runlog` import or call (grep). §1.12 and W3: `reply_rows=9 of 9` in `tests/test_bench_pipeline.py` against `pipeline.bench_run`, each case answers +2 (the one retry of `gates.py:186-191`, `:275-277`), seeds (g) and (h); pre-flight #R02-V-F1b restored; §4 updated. |
| M1 `bench_modes` miscount | ACCEPTED | Twelve modes listed, `11 of 11` printed. W3, W3 CHECK and §4 say `bench_modes=12 of 12`. |
| M2 `group(1)` is `None` in gates | ACCEPTED | `stamps.normalize(None)` raises `TypeError: expected string or bytes-like object, got 'NoneType'` (probe); `gates.py:97` calls it inside `ask` after `start_run` (`:159`) and before any coverage row (`:299-304`). §1.9: one helper `rules.cite_body(match)` for `rules.py:76` and gates; W1 case `text_see_page` (`facts[0].text: cite 12 is not a page of this chunk`), `gate_cases=31 of 31`, seed (d2). |
| M3 pattern captures the next word | ACCEPTED (and a second defect found) | Probe on the first draft's pattern: `He looked at page after page.` -> `['after']`, `see page MED 0012` -> `['MED']`, and `See page 12.` -> `[]` under plain `re` (the draft's `(?:see|at)` is lower case; the real rule runs `re.IGNORECASE`, `rules.py:59,75`, so this one was masked). §1.10 pattern body is now `((?:[A-Z]{1,8}[ -]?)?\d+)\b`; measured on the new pattern: the four must-fail rows capture `12`, the seven must-pass rows capture nothing or a Bates body (`MED 0012`); `cite_forms=11 of 11`, seed (f) widened. |
| M4 facts not tied to their page heading | ACCEPTED | Design gap, no code to cite. §1.1 (7) states the by-page order; W5 check (13) and seed (g); W8 `by_page=1` on every memo line and seed (h). |
| M5 torn last line after a crash | ACCEPTED | Design gap; `append` was append-mode only. §1.5: a torn tail (bytes after the last newline that are not a JSON object) is reported, ignored by `load` and truncated by the next `append`, which `fsync`s; a complete last line without its newline is complete; every other break stays a refusal. W4 `casefile_ok=14 of 14` (two new cases) and seeds (f) to (h); D40 amended; R11 and a code-review item for the concurrent case. |
| M6 default host is the owner's `ollama` | ACCEPTED | `tests/conftest.py:41` `"host": "http://127.0.0.1:11434"`; callers taking the default with an in-process transport: `tests/test_gates.py:88,279`, `tests/test_model.py` (ten calls), `tests/test_jsonrepair.py:119`, `tests/test_fix_cycle4.py:84`, `conftest.py:103,135`. The chair's evidence (the server's request log shows no suite request) makes it prevention. W0: the default becomes `http://127.0.0.1:9` (the port `tests/test_bench_cli.py:100` and five other files already use for "no reply"); W0 CHECK greps `tests` for `11434` (only `tests/test_config.py:22,49,50,181`, `config.load` only); W7 seed (h); R10. |
| M7 re-sent uncited page costs two calls and turns `failed` | ACCEPTED | `gates.py:246-247` `if not obj.get("facts") and not obj.get("flags"): message = "the answer has no facts and no flags"`; `:286` `retryable` stays True for gate 6; `:297-304` every page of a failed chunk gets `status="failed"` with `final_reason`. §1.4 and §1.7 state the cost and the status; R2 and Q55 rewritten in both files. |
| M8 binder name fails the firm rules | ACCEPTED as interim, rest OWNER (Q57) | Probe through `playbook.load`: `Rules.check("ime page MED0001 (ime/001)", unit="text", stamped=True)` -> two `no-dme-ime` errors (excerpt `ime`); the same for `defense-medical-exam`, `dme`, `IME` (`rules.py:59` `re.IGNORECASE`); `intake.py:30` `BINDER_PATTERN = r"[a-z][a-z0-9-]{0,39}"` allows them; `intake.py` imports no playbook (grep), so an intake check is new scope. §1.3 and §1.8: `casefile memo` refuses before the run log opens, naming the binder, the rule and the remedy (Q34 interim: remove the binder by hand); W5 `memo_refused=2 of 2`, W7 `binder_refused=1`, seeds; Q57 holds the practice call. |
| L1 repeated quote shown under one page | ACCEPTED | Design consequence of §1.5 identity. §1.1 (7) states it (the scanned fixture's repeated sentence); W5 check (13) asserts the `medical/002` section holds no quote paragraph; D41 amended. |
| L2 one reading per flag | ACCEPTED | §1.1 (5) and (6): one `Model's reading` paragraph per `about`; W5's gap flag carries two abouts, check (7), seed (h). |
| L3 `job=None` default | ACCEPTED | `runlog.py:135-145` today has no job at all; W2 now makes `job` a required keyword on `coverage` and `open_items` (and on `gates.open_items`, `gates.py:149-150`), every caller named with its job (`tests/test_runlog.py` `_start` uses `job="doctor"`, `:13`), seed (h). |
| L4 `chunks_ok` miscount | ACCEPTED | Seven cases listed plus the pre-flight boundary case. W2 `chunks_ok=8 of 8`, numbered, with the boundary arithmetic (7164 fits, 7165 refused). |
| L5 which text is `CARD_TEXT` | ACCEPTED | `benchrun.py:13-22` `CARD_TEXT` is the stage 2 text; `tests/fakemodel/bench.py:11-13` appends the id sentence; `benchrun.card_version()` (`:25-26`) has no caller outside its file (grep). §1.15: `extract.CARD_TEXT` (stage 2 text, byte-identical), `ID_SENTENCE`, `TEXT`; `card().text is extract.TEXT` asserted; W0 seed (c) rewritten. |
| L6 no `num_ctx` on the gate path | REJECTED | `src/casefile/model.py:127-128`: `settings = dict(options or {})` then `settings.update(num_ctx=self.config.num_ctx, temperature=self.config.temperature)`, so every `ModelClient.chat` call carries `num_ctx` whatever `options` the caller passes; `tests/test_gates.py:167` pins the gate path's request: `assert request['options'] == {'num_predict': card.max_answer_tokens, 'num_ctx': 65536, 'temperature': 0.1}`. Spec §5 "on every call" holds after W3. |
| L7 writes into the session fixture | ACCEPTED | `tests/conftest.py:131-144` is session-scoped. W7: `test_memo_intake.py` copies the matter folder under its own `write_config(tmp_path)` root; the CHECK lists the fixture folder afterwards (`records`, `pages` only). |
| L8 `assert len(CASES) == 27` | ACCEPTED | `tests/test_gates.py:89` `assert len(CASES) == 27` (the review says `:88`; `:88` is `settings = ...`). W1 files name `:89` -> 31. |
| L9 conflict order | ACCEPTED, folded into Q54 | §1.1 (5): case-file order; Q54 asks whether defense-against-ours comes first (Q41) and notes the code tells binders apart only by their names. |
| L10 memo of a benchmark matter | ACCEPTED | `config.py:150-158` refuses `[paths].matters` inside the checkout; D25 lets benchmark matters live inside it. §1.3 and D41: copy the matter under `[paths].matters` first; `casefile bench` unchanged. |

Counts: 18 accepted (two of them in part, with the rest to the owner), 1 rejected (L6), 2 owner questions (56 from
H1, 57 from M8). Decisions the review did not touch are unchanged. Owner questions 54 and 55 are this round's own
held questions (owner offline, Q48) and were amended in both files rather than re-numbered.
