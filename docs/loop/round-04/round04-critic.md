# Round 4 output critic (stage 4: model client and gates)

OUTPUT CRITIC 6/10 · high 2 · med 4 · low 4

Critic: Opus 5.5, fresh context, no part in building round 4. Branch `loop/round-04`, tip 6d16eef. Read as the
attorney who will see these rows as open items, and the operator who runs the Studio.

## What was run (all through `scripts/run.sh`)

1. `scripts/run.sh casefile bench --config config.example.toml --matters tests/fixtures/matters --candidate tests/fixtures/bench/flawed.json` (exit 1) and the same with `--candidate tests/fixtures/matters/9001.001/ideal.json` (exit 0).
2. `scripts/run.sh casefile doctor --config config.example.toml` (exit 1, `doctor failed=3 of 8`).
3. `scripts/run.sh pytest -q -s tests/test_stage4_exit.py` (1 passed, `stage4 exit=0 gates=6 of 6 cases=14 of 14 ...`).
4. A driver script (`$TMPDIR/r4critic/dump.py`) run with `scripts/run.sh python`: it imports `tests/test_stage4_exit.py`,
   runs its 14 cases against the stand-in exactly as the test does, plus one extra case (stand-in mode `empty`, an
   empty `message.content`, which reaches the `gate.model` path), writes the run log under `$TMPDIR/r4critic/run`, and
   prints every `gates`, `failures` and `coverage` row and `open_items` for each matter. Full dump:
   `$TMPDIR/r4critic/out.txt`.

Reproduce any row below with step 4 (copy the script from this record's appendix) or, for the 14 exit cases, by
adding a print of `result["failures"]` and `result["coverage"]` to a copy of the exit test.

Environment note for the chair: the brief and HANDOFF say there is no Ollama on this Mac, but `lsof -nP
-iTCP:11434 -sTCP:LISTEN` shows an `ollama` process listening, and the doctor's context check reached it
(404, model not found). No matter text was sent to it; only the doctor's own warmup ran.

## Findings, most severe first

### H1 (high). Raw Python reprs and cut-off server payloads are written as open-item reasons and doctor lines
- Output: `coverage.reason` and `failures.message` rows, and `doctor context`.
  - Case `prompt_too_long`, all 14 coverage rows: `gate.truncation: status=400: b'{"error": "the prompt is longer than the context length ..."}'` (a Python bytes repr).
  - Extra case (stand-in mode `empty`), all 14 coverage rows and both failure rows: `gate.model: status=200 empty message.content: {'model': 'qwen3.8:27b', 'created_at': ..., 'load_duration': 100, 'prom` (a Python dict repr cut mid-word at 200 characters).
  - `casefile doctor`: `doctor context FAIL status=404: b'{"error":"model \'qwen3.8:27b\' not found"}' | do: ...`.
- What is wrong: the text an attorney reads beside a failed page is a byte string or dict repr cut mid-key, and the
  `gate.model` name is not one of the six gates of spec §4, so the open item names a gate the attorney has never heard of.
- Breaks: the usability bar (no raw Python reprs where a person reads); Librarian R03-OC-L1 ("use words and not a
  pattern, and keep library noise off the line"); spec §4 (six gates, in order).
- Source: `src/casefile/model.py:92,100,106,109,126,128` build the messages with `!r` and `str(raw)[:200]`;
  `gates.ask` copies them into `coverage.reason`.
- Reproduce: step 4, cases `prompt_too_long` and the extra `empty` case; step 2 for the doctor line.

### H2 (high). No gate failure message says, in words, which check failed, what was searched and what to do
- Output: `failures.message` and `coverage.reason` for every failing case of the exit test:
  `gate.truncation: over budget`; `gate.truncation: done_reason=length`; `gate.truncation: prompt cut (prompt_id missing)`;
  `gate.truncation: answer cut (end_id missing)`; `gate.repair: not JSON: Expecting ',' delimiter`;
  `gate.schema: facts[0].text: missing required key`; `gate.rules: no-dme-ime: IME`; `gate.coverage: empty answer`.
- What is wrong: each is an internal token (`done_reason=length`, `prompt_id`, `end_id`, `facts[0].text`, a JSON
  decoder message) with no plain statement of the problem and no instruction; the only message with an instruction
  (gate 4, `...; check source pages and retry`) points the reader at a manual check, which Q44 item 42 rules out as a way
  to close a page ("stays open until the model reads it; no manual read"). Nothing tells the operator the fix for the
  common case (shorter chunk, larger `num_ctx`, rerun the job).
- Breaks: Librarian R03-OC-L1 (name every page involved, say what to do, words not a pattern); ledger Q44 item 42.
- Reproduce: step 3 then step 4; every `failures:` line of cases `budget` through `empty_answer`.

### M1 (med). "pages searched" claims all 14 pages when the ladder searched one, and names them by page id beside a Bates cite
- Output: case `bad_quote`, `failures.message`: `quote on MED0001 not found (pages searched: medical/001, medical/002, ... defense-report/003)`.
- What is wrong: the quote ladder searched only the cited page (`gates._references`, `quotes.match(item["quote"],
  page.text)`), yet the message lists all 14 pages, so the attorney is told the quote is nowhere in the chunk when it may
  sit on another page (a mis-cite, not an invention); the list also uses page ids while the cite is a Bates number, so
  the reader cannot see that `MED0001` is `medical/001`.
- Breaks: spec §4 rule 4 ("otherwise rejected with the pages searched": the list must be the pages actually searched);
  task criterion that Bates stamps are shown where the page has one.
- Reproduce: step 4, case `bad_quote`, first failure row.

### M2 (med). Open items and coverage rows show page ids only, never the page's Bates stamp
- Output: `open_items("9001.001")` keys and `coverage` rows, e.g. `('defense-report/001', 'bench_extract') ('uncited', 'no fact or flag cites defense-report/001', ...)`; every failed row likewise (`medical/001` ... `defense-report/003`).
- What is wrong: all 14 pages of 9001.001 carry a stamp (MED0001 to MED0008, EMP0001 to EMP0003, DEF0001 to DEF0003,
  which the cites resolve against), but no open item or reason shows it, so the attorney sees `defense-report/001`
  where the firm cites `DEF0001`.
- Breaks: playbook `rules.toml` rule `bates-cites` ("Cite by Bates number; when the records are not stamped, cite page
  IDs"); task criterion on Bates stamps. The page id is right as the key; the stamp is missing from what is shown.
- Reproduce: step 4, the `uncited` rows of case `replay` and the `OPEN ITEMS 9001.001` block.

### M3 (med). Gate 4 and gate 5 faults do not say which fact or flag is wrong
- Output: case `bad_quote`: `text number 03 not in quote`, `text number 99999 not in quote`, `quote on MED0001 not found`;
  case `forbidden_json`: `no-dme-ime: IME`.
- What is wrong: with 31 facts, four of them on MED0001, the reader cannot find the faulty fact: the text-number faults
  give no page and no fact, the quote fault gives no quote, and the rules fault gives neither page nor fact nor the
  firm's fix (`rules.toml` has it: write "the report").
- Breaks: Librarian R03-OC-L1 (name every page involved); spec §4 "retried once with the error shown" (the retry prompt
  carries the same message, so the model is not told which fact to fix either).
- Reproduce: step 4, cases `bad_quote` and `forbidden_json`.

### M4 (med). Doctor tells the operator to reload a model that is not installed
- Output: `casefile doctor`, line `doctor context FAIL status=404: ... model 'qwen3.8:27b' not found | do: rerun doctor; if it repeats, reload the model`; and `doctor runlog_job FAIL blocked by context | do: rerun doctor; if it repeats, reload the model`.
- What is wrong: the server said the model is not found, so rerunning or reloading cannot help; the operator needs
  "pull the model or correct `model.name` in the config".
- Breaks: Librarian R03-OC-L1 ("say what to do"); ledger Q43 (the login-user Ollama app is the server the operator acts on).
- Reproduce: step 2 on a Mac where the listener answers 404 for the configured model (this Mac today).

### L1 (low). Each failure reason is copied whole onto every page, and the gate 4 reason repeats the 14-page list three times
- Output: case `bad_quote`, each of 14 coverage rows holds the same reason of about 1,500 characters with the
  `pages searched` list three times.
- What is wrong: every page of the failed chunk is named, as spec §4 asks, but an open-items list built from these rows
  will show the same wall of text 14 times; the chunk's fault belongs once, the pages under it.
- Breaks: usability bar (clear, ordered).
- Reproduce: step 4, case `bad_quote`, coverage rows.

### L2 (low). Over budget and cut prompt fail after one attempt, and the row does not say no retry was made
- Output: cases `budget` and `cut_prompt`, `ok False attempts 1`, one `gates` row each.
- What is wrong: spec §4 says a failure is retried once; these two are not (a deliberate choice, since a retry would be
  the same prompt), but nothing in the row tells the reader that the single attempt was final by design.
- Breaks: spec §4 last paragraph; D31 ("re-checked on the retry"). Possibly a spec wording question rather than a defect.
- Reproduce: step 4, cases `budget` and `cut_prompt`.

### L3 (low). Bench detail lines do not say why a fact is invented or show the forbidden words
- Output: flawed bench, `invented: MED0099 "Date of service: 03/11/2025"` (no such page) and `invented: MED0003 "Patient was lifting 80 pounds."` (quote not on the page) read alike; `rules: no-dme-ime DEF0003` gives no fact text.
- What is wrong: D35 defines two kinds of invented (cite not a page of the matter, quote at no rung), and the operator
  cannot tell them apart or find the offending text from the line.
- Breaks: D35; Librarian R03-OC-L1.
- Reproduce: step 1, flawed candidate.

### L4 (low, owner question). The rule id `no-dme-ime` is shown to the reader in bench and gate output
- Output: flawed bench `rules: no-dme-ime DEF0003`; case `forbidden_json` `gate.rules: no-dme-ime: IME`.
- What is wrong: the firm's own output carries the forbidden abbreviations in a rule label. The playbook does not say
  whether rule ids may appear where the attorney reads; owner question: show the rule's sentence ("Never name the exam
  as a DME or IME in any form; write 'the report'") or a neutral id instead?
- Breaks: nothing settled; spec §4 rule 5 and Q44 item 43 (our words only) bear on it.
- Reproduce: step 1 and step 4.

## What is good enough to keep

- The bench numbers match the answer key line by line: flawed `found=26 of 29 missed=3` (F04, F15, F24 are the three
  facts the flawed candidate omits), `invented=2`, `flags=8 of 9` with G3 missed and the extra MED0001,MED0004 conflict,
  `rules=1` for the IME fact on DEF0003; ideal `found=29 of 29 ... flags=9 of 9` and exit 0.
- Spec §4 semantics are right in the rows: every failing case marks all 14 pages `failed` and lists them in
  `open_items`; no failed answer is saved (`empty_saved=0`); a passing answer marks only cited pages `read` and the one
  page the key never cites (defense-report/001) `uncited`, kept open, per D38 and owner question 47's interim.
- The gate order in the `gates` table is the spec's six, in order, each failure retried once with a fresh prompt, and
  `retry_ok` recovers on attempt 2.
- Q44 is followed: a verbatim record quote with "IME" (probe page 2) passes, the model's own "IME" fails; punctuation
  repairs (`fence`, `control`, `trailing-comma`, `closers`) and ladder rungs are in the run log only.
- The unstamped warning is plain and complete: `warning: no Bates stamp on probe/001, probe/002, probe/003; cites are page ids`.
- The doctor's other lines (config, folders, playbook, run log schema, OCR) name the check and say what to do.

## Appendix: driver script (step 4)

Saved at `$TMPDIR/r4critic/dump.py`. It inserts `tests` and `src` on `sys.path`, imports `test_stage4_exit as T`,
builds the stand-in exactly as `test_stage4_exit` does (`FakeModel(recordings=[*recordings_for(T.MATTER), probe_row])`,
`serve(port=0)`), loops over `T.CASES` plus `("model_error", mode "empty")`, sets each mode through `/_fake/mode`,
calls `gates.ask(card, pages, client=client, rules=firm, log=log, matter=number)` with the budget card override for
`budget`, and prints the `gates`, `failures` and `coverage` rows of each run and `log.open_items` for 9001.001 and
9003.001. Run: `scripts/run.sh python "$TMPDIR/r4critic/dump.py" "$TMPDIR/r4critic/run"`.
