# Round 5 code review (static, fresh reviewer)

Branch `loop/round-05` at df845df, scope `git diff main...loop/round-05 -- src tests scripts schemas playbook`.
Reviewer had no part in the brief, the rulings or the build. Read first: `CLAUDE.md`, `Librarian.md`,
brief §1 and §6 (D39 to D43), ledger `## Round 5`. No model, no app, nothing written outside `$TMPDIR`
except this file. Probes: one read-only script against invented pages
(`$TMPDIR/.../scratchpad/probe_r5.py`, run through `scripts/run.sh python`); its outputs are quoted
under each finding marked CONFIRMED.

Counts: 11 findings; high 2, medium 4, low 5; CONFIRMED 9, PLAUSIBLE 2.

## High

### H1. A gate-passing cite by page id on a stamped page makes the memo refuse, for ever (CONFIRMED)

`src/casefile/gates.py:101-102` accepts `cite == page.page_id` on any page, stamped or not, and gate 5
skips `cite` keys (`gates.py:17`). `src/casefile/facts.py:246` then stores the page id as the fact's
`cite`. `src/casefile/memo.py:56` renders that as `[page medical/001]`, and `memo.py:143` checks every
memo paragraph with `stamped=all(page.stamps ...)`, which is True on a fully stamped matter, so the
`bates-cites` rule fires at `error` and `memo.py:154` raises `MemoError`: no file, exit 2.

Scenario: pages `medical/001` (MED0001) and `medical/002`; the model answers
`{"cite": "medical/001", "quote": "Gait is normal today.", "text": "The gait was normal."}` (the page
header shows both ids, `extract.py:35`). Probe: gate 4 `exact=1 ... ['medical/001']`, gate 5 `[]`,
stored cite `['medical/001']`, memo check `[('bates-cites', '\n [page medical/001]: [page medical/001]')]`,
`render refused`. The event is in the append-only case file, so every later `casefile memo` on this
matter fails the same way, and there is no recovery command (brief §1.5). The failure is masked on any
matter with one unstamped page (then the rule is a warning), so the exit test and `test_memo_intake`
cannot see it. Fix direction: at merge, store the page's first stamp when the page has stamps
(as flags already do at `facts.py:267`), or render `[cite <stamp>]` from `page_ids` at memo time.

### H2. Coverage says `read` before the case file holds the facts; a failed append loses them silently (CONFIRMED by trace)

`gates.ask` commits the coverage rows (`gates.py:312-317`) before it returns; `memo_job.py:49-51`
merges and appends to `casefile.jsonl` afterwards. A `CaseFileError` from `facts.append`
(`facts.py:216-217`, for example a matter folder that is not writable, or a disk full) or a kill
between the two leaves the run log saying `read` and the case file without the facts. The next run
computes `unread` from the run log alone (`memo_job.py:40-42`), finds nothing to send, builds a memo
from an empty case file and exits 0 ("every page read"). The run log is append-only, so the pages can
never be re-sent without editing it by hand.

Scenario: `chmod a-w <matters>/9001.001`, `casefile memo` -> model called, 13 pages `read`,
`memo: cannot run: cannot append case file ...`, exit 2; restore the permission, run again ->
`chunks=0 ... facts=0`, memo written, exit 0. Same window for SIGINT between `record_coverage` and
`append`. Fix direction: refuse before the model call when the case file cannot be opened for append
(a probe open, as `pages.load` already checks links), and treat a page as read only when the run log
row and a case-file `run` event with that `run_id` both exist. Related low: the `output` event is
appended after `os.replace` (`memo_job.py:70-76`); a failure between leaves a memo on disk with
`outputs=none` and the next memo says `First memo for this matter`.

## Medium

### M1. A fact whose first page is not among the memo's pages is dropped from the memo without a trace (CONFIRMED)

`memo.py:98-102` places a fact only under the heading of `fact.page_ids[0]`; a fact whose first page is
absent from `pages` is rendered nowhere, while `status` and the CLI line still count it
(`status.py:39`). The documented remedy for a bad binder name is "remove the binder by hand and
intake it under another name" (`memo.py:130`): after that, every fact first cited on the old binder
vanishes from the memo even when a later run re-cites it on the new binder (the `cite` event does not
move `page_ids[0]`). Probe: case file with F1 at `old/001` plus a cite on `medical/002`, pages
`(medical/002,)` -> `facts in casefile: 1, quote shown in memo: False`. Fix direction: render under the
first page that exists in `pages`, and list facts with no present page under an explicit heading.

### M2. No writer lock and no id-to-seq check: two writers from one base keep the chain intact and lose a fact from every view (CONFIRMED mechanism, PLAUSIBLE trigger)

`facts.merge` numbers new ids from the case file it was given (`facts.py:237-239`); `facts.append`
re-reads the file and reassigns `seq` and `prev` (`facts.py:202`) but never the payload `id`, and
`_decode` (`facts.py:169-175`) does not check `id == F<seq>`. Two `casefile memo` processes on one
matter (nothing prevents it; the lock is deferred to stage 8, brief §1.3) each merge from the same base
and both append: the chain validates, both facts carry `F41`, and `CaseFile.facts` (`facts.py:95`)
keeps only the second. Probe: `ids: ['F1', 'F1']`, `facts seen: [('F1', 'Reflexes are normal.')]`
(the first fact is gone from the memo and from `facts=`). Cheap guards: `fcntl.flock` on the case
file for the whole job, and `_decode` refusing `fact`/`flag` ids that differ from their `seq`.

### M3. A reading carries no page; the memo shows readings of other pages under the first page's heading (CONFIRMED)

The `reading` event is `{fact, text, run_id}` (`facts.py:56`, `:258-259`): the page whose occurrence
produced the sentence is not stored, and `memo.py:109-110` prints every reading under
`fact.page_ids[0]`. Scenario: quote `Normal.` cited at MED0001 with text "Gait is normal.", later
cited at MED0007 with text "Reflexes are normal."; memo under `medical page MED0001`:
`"Normal." [cite MED0001]`, `Also cited: [cite MED0007]`, `Model's reading: Gait is normal.`,
`Model's reading: Reflexes are normal.` (probe output). The second sentence is labelled a model reading
(Q48 holds) but the reader is told it reads page MED0001, which the digit check never tested it
against. Store `page_id` on `reading` events and print `Model's reading (MED0007): ...`.

### M4. The chain's head is unanchored: an edited last line and a deleted tail load clean (CONFIRMED)

`_decode` checks `prev` of each line against its predecessor (`facts.py:171`), so the last line's own
bytes are covered by nothing, and removing any number of complete trailing lines leaves a valid chain.
D40 and the `_broken` message ("edited or truncated") promise refusal for both. Probe: three events,
last payload `Reflexes are normal.` edited to `Reflexes are ABSENT.` -> loads, quotes show the edit,
`torn = 0`; first two lines only -> loads, `last_seq = 2`, `stale = []`. In practice the last line is
a `run` or `output` event, so the edit case changes metadata (`built_from_seq`, run lists), and the
deleted-tail case erases a whole run's facts with no refusal. Anchor the head: record the last line's
hash and `seq` in the run log `runs` row (or a sidecar) and compare on load; `tests/test_facts.py` has
no case for either.

## Low

### L1. Flag cites are not deduplicated with page ids; a one-page "conflict" passes and is stored (CONFIRMED)

`facts.py:263` dedups `page_ids`, `facts.py:267` builds `cites` from the undeduped list, and gate 4
does not require two distinct pages for a conflict. Probe: `cites: ["MED0001", "MED 0001"]` ->
`flag cites: ['MED0001', 'MED0001'] page_ids: ['medical/001']`, memo
`Conflict between [cite MED0001].`; the exit test's `cites=` oracle (`test_stage5_exit.py:141`)
would also miscount such a flag.

### L2. An intake layout with an empty `pages/` loads zero pages and the memo exits 0 (CONFIRMED)

`pages.py:106-131` accepts a `pages/` folder with no binders; `memo_job.py:82` then returns 0 and
writes a memo with no facts and `Pages read in 0 runs`. Probe: `PageSet(pages=(), open_pages=())`,
`open = 0`. After the documented "remove the binder by hand" remedy this is the state of the matter
until re-intake. Refuse with the same `no pages for matter N ...: run casefile intake first`.

### L3. The playbook's `bates_pattern` and the config's `stamp_pattern` are two definitions of a stamp (PLAUSIBLE)

`playbook/rules.toml:57` demands four or more digits; `[ocr].stamp_pattern` (`config.py:28`) is
owner-configurable. A firm whose stamps are `ABC123` intakes fine and every memo cite then fails the
memo's own check at `error` (probe: `[cite ABC123]` -> `('bates-cites', 'error')`), so no memo can
be written for any stamped matter. Defaults agree today; `doctor` or `playbook.load` should check the
two patterns against each other.

### L4. `RETRY_MARGIN` is a guess, not a bound (computed)

`pipeline.py:11`: the attempt 2 `Retry:` line carries the whole gate reason; on the fixture an
all-quotes-wrong answer costs about 121 bytes per fault (probe: 3776 bytes for 31), so a chunk with
more than about 67 faults loses its retry as `the prompt was too long; the chunk must be made smaller`
(`gates.py:193`, `:296`), which the attorney cannot act on. Cap the reason carried into the retry line.

### L5. The memo refusal message starts with a newline and repeats the excerpt (CONFIRMED)

`memo.py:140-145` substitutes `\n` for exempt runs and prefixes the whole paragraph, so H1's refusal
reads `bates-cites: \n [page medical/001]: [page medical/001]` (probe). Name the section and the
paragraph number instead (#R03-OC-L1 class).

## Checked and not raised

- Failed outcomes never merge (`memo_job.py:49`, `answer is None` on failure, `gates.py:318`);
  `test_status_six_cases` and `test_pipeline[empty]` cover it.
- Coverage job filter (`runlog.py:135-146`) and `only_unread` (`pipeline.py:73-76`) isolate bench and
  memo rows; `test_coverage_job_is_required_and_isolated` and `test_chunks[unread_*]` have teeth.
- Binder refusal precedes `open_db`, the model and any write (`memo_job.py:23-29`); test asserts no
  run log file.
- Torn tail: `load` ignores, `append` truncates before writing (`facts.py:198-215`); a prefix of a JSON
  object can never parse as an object, so a torn tail cannot be mistaken for an event.
- Quote runs and run-log reasons are the only exempt runs (`memo.py:79`, `:104`); titles, headings,
  labels, readings and abouts are checked. `test_memo` seeds a title and a binder red.
- Exit codes: memo 0/1/2 each tested; status 0 by design (view) with 2 tested on a missing matter.
- Privacy: every fixture is invented; outputs go under `[paths].matters` (outside the checkout); no
  model text is printed beyond the run log reasons the brief allows; nothing leaves the machine.
- D42 gate 4 prose cites (`gates.py:128-144`) verify then strip; `text_see_page`, `text_cite_bad`,
  `mixed_chunk` and `test_prose_cites_use_chunk_lookup` cover the stated contract.

Librarian entries this review checked against: #R01-CX-3, #R01-CX-11, #R01-V-B2, #R02-CX-5,
#R03-CX-2, #R03-OC-L1, #R03-V-L1, #R04-PC-6, #R04-PC-7, #R04-CX-1, #R04-V-2, #R04-CH-1.

## Chair reproduction (8a, 2026-10-28), at df845df

The chair read the reviewer's probe (`scratchpad/probe_r5.py`; writes only under a temp folder) and ran it through
`scripts/run.sh python`; its lines reproduced as quoted above. H2 was traced in `memo_job.py:44-51`: `pipeline.run`
commits coverage rows inside `gates.ask` before `facts.append` runs.

| Finding | Status | Chair ruling for fix cycle 1 |
|---|---|---|
| H1 page-id cite on a stamped page | REPRODUCED (P1: render refused) | at merge, a cite by page id on a page with stamps is stored as that page's first stamp (as flags do at `facts.py:267`); a test renders a memo from such an answer |
| H2 coverage read before the append | REPRODUCED (trace) | the memo job counts a page read only when its latest `memo` coverage row is `read` and the case file holds a `run` event with that `run_id`; `casefile memo` opens the case file for append (probe) before any model call and refuses exit 2 if it cannot; a test injects an append failure after a passing chunk and the next run re-sends those pages |
| M1 fact under an absent first page | REPRODUCED (P2) | a fact is placed under the first of its `page_ids` present in the memo's pages; facts with none present go under a closing heading `Facts on pages not in this matter` with their cites, never dropped; count asserted equal to `status` facts |
| M2 two writers, duplicate fact ids | REPRODUCED mechanism (P4b) | an exclusive `fcntl.flock` on `casefile.jsonl.lock` around load, merge and append in `memo_job`; `facts.load` refuses a repeated fact id |
| M3 reading shown under the wrong page | REPRODUCED (P3) | a `reading` event carries `page_id`; a reading whose page is not the heading's page renders `Model's reading of [cite <label>]: ...` |
| M4 unanchored chain head | REPRODUCED (P4) | a deleted tail of complete lines is recovered by H2's join (pages re-sent); an edited last line is a recorded limit (Librarian open item, D40 wording narrowed at close); no fix this cycle |
| L1 one-page conflict | REPRODUCED (P5) | gate 4 fault `flags[i]: a conflict must cite two different pages`; flag cites deduplicated by page |
| L2 empty `pages/` | REPRODUCED (P7) | `casefile memo` refuses exit 2 `no pages to read in <matter>` |
| L3 two stamp definitions | PLAUSIBLE, not reproduced (defaults agree) | logged as an open item for stage 6 |
| L4 RETRY_MARGIN | computed, tuning | tuning entry at close, no change |
| L5 refusal message format | REPRODUCED (P1 text) | one line per finding, `<rule-id>: <excerpt> (in <section>)`, no leading newline, no repeated excerpt |
| CH-1 (chair seed, build) | REPRODUCED (green under seed) | a test whose last line carries a wrong `seq` must be refused |
