# Round 5 build brief: adversarial plan review

Reviewer: a fresh Fable agent, read-only, no context from the brief's writing. Static review on `loop/round-05`
at `4755170` (working tree as the brief describes). Every number below was checked in the code or by a read-only
probe through `scripts/run.sh python -c ...`; nothing outside the repo was read. Every fixture is invented.

## Premises verified (no finding)

- D0.1 to D0.13 line references all match the files as they stand (`gates.py`, `rules.py`, `rules.toml`,
  `benchrun.py`, `bench.py`, `benchscore.py`, `runlog.py`, `matter.py`, `intake.py`, `model.py`, `config.py`,
  `privacy.py`, `tests/fakemodel/core.py`, `tests/fakemodel/bench.py`).
- Probe: card text 920 bytes, version `4ab2bdb30535`; page blocks exactly as D0.8; the §1.4 split under
  `max_answer_tokens = 65536 - 16384` is `[5, 5, 4]` with 6236, 6780, 5418 bytes. The "19462 bytes" prompt is
  19398 message bytes plus `TEMPLATE_TOKENS` 64 (the gate's budget sum), not the message bytes alone; harmless.
- `key.json` flags G1, G3, G6, G9 are the four cross-chunk pairs, so `flags=5 of 9` (W3) is right. The ideal
  cites 13 pages, never `DEF0001`; the key cites neither `DEF0001` nor `EMP0002`.
- `flawed.json`: `MED0003 "Patient was lifting 80 pounds."` is a quote not on an existing page; `MED0099` is no
  page; the rule hit is `IME` in the DEF0003 text (W6's four new lines are right).
- `tests/test_stage2_exit.py:75-77` asserts `lines[0]` and `lines[-1]` only (the `uncited:` line is free);
  `:42-44` patches `benchrun.ModelClient`. `tests/test_stage4_exit.py:125` keys open items by `bench_extract`.
- `Rules.check` today returns `[]` for `at page 12 of the report`, `see page MED 0012`, `He looked at page after
  page.` (R1-20 reproduced; the last two matter for finding M3).
- No test or fixture holds `[cite` inside an ideal `text` or `about`, so W8's `cites=45` arithmetic holds.

## Findings

Severity, brief section, code it rests on, the defect, what goes wrong if built as written.

### High

**H1. CONFIRMED. §1.4, §1.5, R3, W8.** `benchrun.py:19` (card: "A conflict is two pages that disagree"),
`gates.py:96-109` (a cite resolves only against the chunk's pages), §1.4 "only unread pages are sent", spec §2
"rebuilt after every upload". Defect: with `only_unread`, every record that arrives after the first run is read
in a chunk that holds nothing but new pages, so a conflict between a new page and an already-read page can never
be flagged by this card, whatever the chunk size. On a real matter the medical binder arrives first and the
defense report later (the owner's Q41 priority, "especially between defense examinations and our records"), so
the memo's conflicts section is structurally empty of exactly the conflicts the owner asked for, on every matter
read in more than one run. The brief files this under R3 as a chunk-size cost ("on the fixture one chunk holds
every page") and the exit test cannot see it: W8 run 3 reads `DEF0001` alone and the ideal has no conflict on
that page, so `conflicts=5` is unchanged by construction. The stage 5 exit criterion "a memo with conflicts" is
therefore proven only for a matter that arrives whole. No owner question (50 to 55) raises it.

**H2. CONFIRMED. W3 (files), §4.** `tests/test_benchrun.py:155-389` holds the only runner-level tests that a
received reply is stored as an `answers` row on each transport path: non-JSON 200 (`:155`), non-200 with a body
(`:186`), 302 and 307 with and without a body (`:228`, `:324`), an HTTPError with no body stream (`:308`), a read
timeout after the status line (`:343`), and `reply_received` on a failed gate (`:377`). The brief says their
"transport probes exist in `tests/test_model.py:227-331`", but those test `ModelError.received` and `raw` at
the client, never the row (`test_model.py:227-331` writes no run log). `tests/test_gates.py:36-41` has only
`prompt_too_long` and `no_reply` on this path; W3's `bench_modes` adds no redirect, timeout or empty-body case.
Deleting the file retires #R02-V-F1, #R02-V-F1b and D30 at the runner, the pre-flight bullet "does a test drive
each path, including the real opener's redirect handler" walks in again, and `gates.py:186-191, 275-277` (the
one place that now stores those rows) is unguarded.

### Medium

**M1. CONFIRMED. W3 Ships and CHECK.** The `bench_modes` table lists `replay`, `retry_ok`, `truncated`,
`cut_answer`, `unrepairable`, `bad_schema`, `bad_quote`, `forbidden_json`, `empty_answer`, `cut_prompt`,
`prompt_too_long`, `no_reply`: twelve modes, printed as `bench_modes=11 of 11`. The code will not produce the
CHECK line as written; a builder will drop one mode or change N, and §4's "every N is fixed so a builder cannot
pad or trim" fails on this table.

**M2. PLAUSIBLE. §1.9, W1.** `gates.py:96-99` `lookup(cite, path)` calls `stamps.normalize(cite)`. §1.10 turns
`cite_pattern` into a three-group alternation; §1.9 scans every `text` and `about` with that same pattern, but
only `rules.py:76` is told to read the first non-None group. A builder who keeps `match.group(1)` in gates gets
`None` for a model sentence such as "see page 12" and `normalize(None)` raises `TypeError` out of `gates.ask`
after `start_run` (`:159`) and before any coverage or failure row (`:291`, `:299-304`): `casefile memo` dies
with a traceback and a run row with no disposition. W1's table has no case with an unbracketed cite in `text`,
so no seed turns this red.

**M3. PLAUSIBLE. §1.10, W1 must-pass rows.** `\b(?:see|at)\s+(?:page|p\.)\s*([A-Za-z0-9-]+)` captures the
next word, whatever it is. "He looked at page after page" captures `after`, fails `bates_pattern`
(`rules.toml:57`), and is an error when stamped. "see page MED 0012" captures `MED` and errors on a valid cite
(Q40: `MED 0012` is the same stamp; `bates_pattern` allows the space). Neither sentence is in the nine-row
table, so `cite_forms=9 of 9` stays green on both. #R01-CX-7 class (the pre-flight asks for a list of ordinary
memo sentences in both directions).

**M4. PLAUSIBLE. W5 (8), (11); W8 `quotes=31 of 31`.** `quotes` counts a quote "present verbatim in a quote
run" anywhere in the document; W5 checks that a heading and a fact paragraph exist but not that the paragraph
sits between its own page's heading and the next. A memo that files every fact under the first page heading
(or in case-file order ignoring pages) passes every listed CHECK, and no seed covers it. #R04-CH-1 class
(evidence present somewhere, not associated with the named source).

**M5. PLAUSIBLE. §1.3, §1.5, W7 pre-flight #R03-CX-2.** `facts.append` writes to `casefile.jsonl` in append
mode; `load` refuses any broken chain with exit 2, "the file was edited or truncated". A crash or power loss
mid-append (the Studio, `pmset autorestart`) leaves a partial last line, after which every `casefile memo` and
`casefile status` on that matter exits 2 forever; the brief's `.tmp` then `os.replace` protection covers
`memo.docx` only, and no recovery path is stated (the attorney cannot edit the file by design).

**M6. PLAUSIBLE. W7 (`test_status.py`, `test_memo_intake.py`), D0.10.** `tests/conftest.py` `write_config`
defaults `host` to `http://127.0.0.1:11434`, and `scanned_intake` (`:131-144`) uses that default; the HANDOFF
says the owner's local `ollama` listens there and no agent sends it matter text. Both W7 tests run the memo job
in process and rely on `opener=FakeTransport(...)` being threaded through `memo_job.run` into `ModelClient`
(`model.py:75-78`); a builder who drops the parameter once sends the (invented) scanned pages to the real
server before the test goes red. `tests/test_bench_detail.py:36` shows the safe form (`host="http://127.0.0.1:9"`).

**M7. CONFIRMED mechanics. §1.4, R2, question 55.** A page re-sent alone because it is `uncited` (a cover sheet)
yields an answer with no facts and no flags; `gates.py:246-247` fails gate 6, `:286` retries once, and
`:297-304` marks the page `failed` with "gate.coverage: the answer has no facts and no flags". So the cost is
two model calls per run (Q55 says one) and the open item's status flips from `uncited` to `failed`, which
misdescribes a blank page as a model failure in `status` and in the memo. Q55's interim is written on an
undercount.

**M8. PLAUSIBLE. §1.8, W5 `memo_refused`.** `memo.check` runs the firm rules over page headings built from the
binder name (`<binder> page <stamps> (<page id>)`). D27 lets the attorney type the binder name at intake; a
binder named `IME` or `defense-medical-exam` makes every memo heading a `no-dme-ime` error (`rules.toml:8`),
`MemoError`, exit 2, and Q40 item 34 refuses re-intake until the binder is removed by hand. Q16 governs what the
memo says about the exam; whether a folder label is "our words" is a practice call the brief makes by default
(fail closed, unrecoverable) rather than by a ruling. Either validate binder names against the rules at intake
(before OCR, #R03-V-L1) or hold it as an owner question.

### Low

**L1. PLAUSIBLE. §1.5, §1.1 (7), §1.12.** Fact identity is the folded quote across pages. A phrase that appears
on two pages (the scanned fixture repeats "Seen by Dr. Rafael Soto-Lindgren." on pages 1 and 2) shows only under
the first page's heading with `Also cited`; the second page's "Verified facts by record" section omits it, and
`bench_run` attaches the first page's reading to the second cite. Acceptable under spec §3.5, but the memo's
by-page promise is weaker than it reads; state it.

**L2. PLAUSIBLE. §1.5, W5 (6), (7).** Flag identity is `(kind, page ids)`, so two gaps on one page (two
missing records referred to by one note) collapse into one flag with two `about`s; W5 formats one `Model's
reading` per flag. Specify one reading paragraph per `about`, as (10) does for facts.

**L3. PLAUSIBLE. W2 (`runlog.coverage(matter, *, job=None)`).** The default means "every job", the mixing the
filter exists to prevent (#R01-OC-M2: a default that silently skips a rule). The memo and status paths depend
on remembering `job="memo"`; only seeds W2 (c) and W7 (b) guard it.

**L4. CONFIRMED. W2 `chunks_ok=6 of 6`.** The listed cases are seven if the two `only_unread` runs (memo rows,
bench rows) are separate, six if one; and the pre-flight claims a budget-boundary case (#R02-CH-1, "a page
exactly at the budget boundary: fits") that is in neither count.

**L5. PLAUSIBLE. §1.15, W0.** §1.15 says `extract.CARD_TEXT` is the stage 2 text plus the id sentence; W0 says
`benchrun.messages` and `tests/test_fakemodel_bench.py:15` keep using `CARD_TEXT` as the stage 2 system message.
Under the first reading the stage 2 runner's prompt and `benchrun.card_version()` (`benchrun.py:25-26`) change
silently in W0 while the brief says the suite is unchanged in meaning; under the second, seed (c)'s "identity of
module constant" has no shared object to compare. Say which.

**L6. CONFIRMED. §1.12, spec §5 model client row.** `gates.ask` sends `options={"num_predict": ...}`
(`gates.py:184`) and never `num_ctx`; the stage 2 runner sent `num_ctx` (`benchrun.py:68`). After W3 no bench
or memo call carries `num_ctx` although spec §5 says "on every call". Pre-existing since stage 4; W3 makes it
the only path. Amend the row in D39 or add the option.

**L7. CONFIRMED. W7 `test_memo_intake.py`.** It writes `casefile.jsonl` and `outputs/` into the session-scoped
`scanned_intake` matter folder. `tests/test_intake.py:421-445` and `tests/test_stage3_exit.py:50-55` read only
`records/` and `pages/`, so nothing breaks today; the coupling is order-dependent and unstated.

**L8. CONFIRMED. W1 files.** `tests/test_gates.py:88` also has `assert len(CASES) == 27`; the brief names only
the `:79` print. Trivial, but the file list is the builder's contract.

**L9. PLAUSIBLE. §1.1 (5), Q41.** Conflicts are listed in flag order; Q41 puts defense-versus-ours "above all".
Ordering is taste either way; fold it into question 54.

**L10. CONFIRMED. §1.3, §1.14.** `casefile status` is §8b's `matter_status` (stage 8b) and `casefile memo` on a
benchmark matter needs the matter copied under `[paths].matters` (`config.py:150-158` requires outside the
checkout; D25 lets benchmark matters live inside it). Scope is defensible for critic M2; say that the owner's
"memo of a benchmark matter" needs a copy.

## Counts

High 2 (both CONFIRMED). Medium 8 (M1, M7 CONFIRMED; M2 to M6, M8 PLAUSIBLE). Low 10 (L4, L6, L7, L8, L10
CONFIRMED; the rest PLAUSIBLE).

## Three changes to insist on before build

1. **Cross-run conflicts (H1).** When unread pages are sent, fill the rest of the chunk with already-read pages
   of the matter (binder order, nearest first) up to the budget, so the card sees the new record beside the
   old; re-found facts merge to nothing by identity, so the case file does not grow. Add owner question 56
   (how much context to re-send; the cost on the Studio), a memo line under Conflicts stating "pages read in N
   runs; conflicts between runs are checked only for pages sent together", and a W8 assertion on run 3's memo
   that the line names 2 runs. If the chair rejects the re-send, the question and the memo line still go in.
2. **Keep the reply-storage tests and fix the mode count (H2, M1).** Rewrite `test_benchrun.py:155-389`'s
   received-error cases against `pipeline.bench_run` (non-JSON 200, non-200 with and without a body stream, 302
   and 307 with and without a body, read timeout after the status line), each asserting exactly one `failed`
   answers row and `reply_received=True`, and `no_reply` asserting no row; print `bench_modes=12 of 12`.
3. **Teeth for the memo and gate 4 (M2, M4, M6).** Every in-process test that builds a `ModelClient` writes
   `host="http://127.0.0.1:9"`; W1 adds a `text_see_page` gate case (unbracketed cite in `text`, expected
   `facts[0].text: cite 12 is not a page of this chunk`) and gates reads the first non-None group; W5 and W8
   assert that each quote paragraph lies between its own page heading and the next, with a seed that files
   every fact under the first heading going red.
