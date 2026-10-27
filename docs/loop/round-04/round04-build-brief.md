# Round 4 build brief: stage 4 model client and gates (plus R4-2 to R4-4)

Branch `loop/round-04` at `54932ba` (working tree: untracked `.agents/`, `AGENTS.md`; leave them). Scope: ledger
R4-1 (spec §7 stage 4: every gate of spec §4 tested with good and bad answers, including truncated ones), R4-2
(R2-CX-2 prompt truncation detection, OR-4), R4-3 (verifier gaps S1, S2, S5), R4-4 (verifier lows: duplicate
matter number refused up front, `normalize`, step comments, suite time T-11). R4-5 (R1-20) stays deferred.
Tiers: Q30 defaults (Opus orchestrates, Sonnet 5.5 codes, Codex reviews plan and code). Privacy: every answer,
page, name, stamp and number below is invented (§6b); no Ollama runs on this Mac (Q11); the model is the
stand-in `tests/fakemodel/` in every test and probe.

Measured on the tip 2026-10-27 (this architect, inside the sandbox, through `scripts/run.sh`):
`scripts/run.sh pytest -q --durations=25` -> `358 passed in 95.33s`, `real 97.26` (over the 90 s budget, T-11; the
verifier's run at the round 3 close was 72.67 s; see §0 D0.1); the stage lines printed unchanged: `exit=0 verdicts=8
fails=set() test_jobs=1`, `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`, `stage3 exit=1 pages=6 ids_ok=6 of
6 stamps_ok=6 of 6 text_ok=6 of 6 must_ok=5 of 5 empty=1 failed=0 min_ratio=1.000`. Ladder prototype against the
shipped fixtures (`$TMPDIR/proto/ladder.py`, not committed): `ideal.json {'exact': 31}`, `flawed.json {'exact': 28,
None: 2}` (MED0003 "Patient was lifting 80 pounds." and MED0099 match at no rung), key `{'exact': 29}`; none of the
14 pages holds a curly quote, a ligature or a hyphen at a line end.

## §0 Drift (premises verified in the code, not in a report)

- D0.1 **Suite time is over budget on this Mac today.** `358 passed in 95.33s` with the 25 slowest:
  `test_intake.py::test_intake_fixture_with_real_tools` 11.54 s, `test_config.py::test_matters_alias_table` 9.68 s,
  `test_doctor.py::test_ocr_real_tools` 5.85 s, `test_fix_cycle3.py::test_stopped_then_continued_child_is_not_an_exit`
  4.41 s, `test_stage1_exit.py::test_stage1_exit` 4.24 s, `test_stage3_exit.py::test_stage3_exit` 4.12 s,
  `test_stage1_exit.py::test_stage1_inprocess_control` 4.04 s, six `test_run_sh.py` rows at 2.0 to 2.4 s. Five real
  OCR runs: two intakes of the six-page fixture (`test_intake.py:422-428` in process, `test_stage3_exit.py:55-58`
  through `run.sh`) and three doctor smokes (`test_doctor.py:303-304`, both stage 1 exit tests). The run shared the
  machine with two curl fetches and the prototype, so the number is an upper reading; the budget rule (T-11) still
  applies: fewer real OCR runs, never a skip (§4).
- D0.2 **Ollama today refuses an over-long prompt on request and reports cached tokens.** Read on `ollama/ollama`
  main (GitHub API, `pushed_at 2026-10-27T18:03:57Z`): `api/types.go:114-116` `// Truncate is a boolean that, when
  set to true, truncates the chat history messages if the rendered prompt exceeds the context length limit.
  Truncate *bool json:"truncate,omitempty"` on the chat request; `server/routes.go:642` `genTruncate :=
  (req.Truncate == nil || *req.Truncate) && !m.IsMLX()` and `:757` `Truncate: req.Truncate == nil ||
  *req.Truncate` (absent means true). `llm/llama_server.go:300-302`: `if !req.Truncate || len(req.Media) > 0 ||
  s.options.NumCtx <= 1 || len(prompt) < s.options.NumCtx { return prompt, nil }` (with `truncate: false` the prompt
  goes to llama-server untouched, which answers with an error; `:2635` `promptTooLongMessage = "the prompt is
  longer than the context length currently available to the model; ..."`, `:2641-2643` matches `"context length"`
  and `"exceeds the available context"`); `:312-314` with context shift off: `StatusCode: http.StatusBadRequest,
  ErrorMessage: promptTooLongMessage`. With truncation on, `:319-335` keeps `nKeep` tokens (`NumKeep`, plus one
  for BOS) and the tail, and the limit is `contextShiftPromptLimit` at `:338-347`: `numCtx - max((numCtx-numKeep)/2,
  1)`, so a cut prompt is about HALF the context (32771 of 65536), not the context length: a "count near num_ctx"
  rule cannot detect a cut. `:1631-1641` `promptEvalCount()` returns `PromptN` when llama-server reports no
  `cache_n`, else `*t.CacheN + t.PromptN`; `:1862-1863` `PromptEvalCount: lsResp.Timings.promptEvalCount(),
  PromptEvalCachedCount: lsResp.Timings.CacheN`; `api/types.go:565` `PromptEvalCachedCount *int
  json:"prompt_eval_cached_count,omitempty"`, `:1101` `uncached := max(0, m.PromptEvalCount-cached)`. So OR-4's
  premise (cached tokens not counted) holds on an Ollama whose llama-server sends no `cache_n`, and is false on the
  current one; the Studio's version is not known here (Q43 fixed only the user, not the version). `server/prompt.go:
  21-22` `chatPrompt truncates any messages that exceed the context window ... always include 1) the latest message
  and 2) system messages`, `:63` `if ctxLen <= opts.NumCtx`. Gate 1's design (§1.1) is sound under both versions.
- D0.3 **Model client as it stands.** `src/casefile/model.py:97-102` `chat(self, messages, *, options=None)` sends
  `{"model", "messages", "stream": False, "options"}` only; `:99-100` `settings.update(num_ctx=..., temperature=...)`
  (a caller's `num_predict` survives, `num_ctx` does not); `:109` `done is not True` -> `ModelError`; `:111-113`
  counts must be `int` when present; `:36-42` `Answer(content, done_reason, prompt_eval_count, eval_count, raw)` has
  no cached count. `tests/test_benchrun.py:50` asserts `sent["options"] == {"num_ctx": 65536, "temperature": 0.1}`
  (top-level body keys are free; options are not).
- D0.4 **Stage 2 runner guards.** `benchrun.py:42-43` `counts_ok` (positive ints), `:68` `client.chat(msgs,
  options={"num_ctx": ...})`, `:81-87` guard 1 `done_reason != "stop"` -> `bench.truncation`, guard 2 ->
  `bench.counts`, `:89-93` `parse_text` -> `bench.answer`; `:12-22` `CARD_TEXT`, `:29-35` `messages(matter)` (the
  recorded stand-in prompt, `tests/fakemodel/bench.py:14`). `tests/test_benchrun.py:116` pins the failure gate
  list `["bench.truncation", "bench.answer", "bench.answer", "bench.truncation", "bench.model", "bench.counts"]`.
- D0.5 **Quote matching and scoring.** `quotes.py:7-10` `normalize` (curly to straight, collapsed whitespace,
  casefold), `:13-15` `found_in`; `benchscore.py:76` invented test `found_in(fact.quote, page.text)`, `:83` found
  test `normalize(k.quote) == normalize(fact.quote)`, `:108-113` rules over `text` and `about` only, `:44-48` the
  line, `:50-63` detail lines; `benchkey.py:84` validates key quotes with `found_in`, `:87-90` refuses a repeated
  (cite, normalised quote). `doctor.py:191`, `tests/test_stage3_exit.py:45`, `tests/test_scanned_fixture.py:60`
  use `found_in` or `normalize` and keep them.
- D0.6 **Rules API.** `rules.py:53` `Rules.check(self, text, *, unit, stamped=True)` returns `Finding(rule_id,
  severity, start, end, excerpt)`; `:56-57` unit is `text` or `question`; `:74-78` the cite rule is `error` when
  stamped, `warning` otherwise. `playbook/rules.toml` holds the four rules (Q12).
- D0.7 **Run log schema v1 and the trigger count.** `runlog.py:8-34` `SCHEMA` (five tables, eight triggers);
  `:105-133` `open_db` adds five `no_replace` and two `schema_meta` triggers (15 in all); `:116-117` refuses
  `schema_version != 1`; `:125-129` `schema_meta_no_update` forbids the version row's UPDATE. `doctor.py:79`
  `version == 1 and count == 15`; `tests/test_runlog.py:26` `== 15`; `tests/test_fix_cycle2.py:159` `"doctor
  runlog_schema PASS schema=1 triggers=15 (counted)"`. `record_answer` at `:67-75` has no cached-count column.
- D0.8 **Stand-in server.** `tests/fakemodel/core.py:11` `MODES` (seven); `:76-78` allowed `/api/chat` keys
  `{"model", "messages", "stream", "options", "format", "keep_alive", "tools", "think"}` (no `truncate`: a request
  carrying it gets 400 `unknown keys`); `:102-104` exact canonical lookup of the messages, 404 otherwise; `:106-124`
  mode edits; `:116` `prompt_count = chars // 4 + 8` (T-4); `:120-124` reply keys. `tests/test_fakemodel.py:30`
  iterates six modes (`modes_ok=... of 6`), `:82` asserts the error text holds `"replay, truncated, malformed,
  forbidden, short_context, empty"` as a substring (modes appended at the end keep it true), `:55-57` pins the reply
  key set. `tests/fakemodel/bench.py:10-15` records one row per bench matter from `benchrun.messages`.
- D0.9 **Schemas.** 19 files in `schemas/`, keywords used: `type` 337, `properties` 62, `required` 62,
  `additionalProperties` 62 (every one `false`), `items` 56, `enum` 27, `$schema` 19, `title` 19; `type` values
  `object, array, string, integer, boolean` only. Three property NAMES collide with keywords
  (`concessions.schema.json:9` a property called `type`, `comparison.schema.json` and `encounters.schema.json`
  properties called `items`): a validator must read keys under `properties` as names. The venv holds `Pygments,
  casefile, iniconfig, packaging, pillow, pluggy, pypdf, pytest`; no `jsonschema`.
- D0.10 **Carried verifier items, as the code stands.** `intake.py:306` `PageRecord(number, binder, index, ...)`
  and `tests/test_stage3_exit.py:41-47` `judge` asserts `record["id"]` only (S1); `intake.py:84-86` `if len(parts)
  != pages: raise` and `tests/test_intake.py:172` covers `sidecar 5 of 6` only, `:195` `len(cases) == 15` (S2);
  `tests/fixtures/scanned/make_scanned.py` `check()` compares `(pixels, text)` tuples per page and
  `tests/test_scanned_fixture.py:63-72` changes page 2 pixels only (S5). `bench.py:66-79` finds a duplicate number
  on the second root after the first ran; `tests/test_bench_multi.py:63` asserts `seen == ["a"]` (the late refusal
  is pinned). `stamps.py:14` `re.sub(r"[ -]", "", raw).upper()`; `config.py:124` compiles
  `r"(?<![A-Z0-9])(?:" + pattern + ")"` while `stamps.py:23` uses the four-clause wrapper. Comments `# Load Config`,
  `# Load Playbook`, `# Find Matter Roots`, `# Main Loop`, `# Load Matter and Key`, `# Score`, `# Final Result`
  (`bench.py:21-122`) and `# Check overall structure`, `# Process facts`, `# Process flags`, `# Return result`
  (`benchcandidate.py:39-77`).
- D0.11 **Harness facts.** `tests/conftest.py:26-71` `write_config(tmp_path, **overrides)`; `tests/test_stage2_exit.py:
  51-66` starts `serve(port=0, model=FakeModel(recordings=...))` on a thread and drives `scripts/run.sh casefile
  bench` with `CASEFILE_CONFIG`; `:37-46` the in-process control swaps `benchrun.ModelClient`. `scripts/run.sh:4`
  names the toolchain by `basename "$ROOT"`, so a lane B worktree needs its own `uv sync` with the sandbox off
  (chair). Worktree `.claude/worktrees/r3-lane-b` and branches `r3/lane-b`, `control/r2-sonnet` still exist
  (HANDOFF leftovers, owner's say-so to delete).
- D0.12 Tuning entries end at T-15; owner questions end at 41; spec §9 ends at D30; the ledger's round 4 section is
  R4-1 to R4-5.

## §1 Decisions, with trade-offs

- **1.1 Gate 1, truncation, is four checks, none of them "tokens read equals tokens sent" (R4-2, OR-4).**
  (a) Before any call, the pipeline refuses a prompt whose conservative token ceiling `model.tokens_at_most(chars)
  = ceil(chars / CHARS_PER_TOKEN_FLOOR)` with `CHARS_PER_TOKEN_FLOOR = 2.0` exceeds `num_ctx -
  card.max_answer_tokens` (no model call, no retry; #R03-V-L1). (b) Every pipeline call sends `"truncate": false`
  (D0.2), so a current Ollama answers an over-long prompt with an error instead of a cut; a received non-200 whose
  body holds `context length` or `exceeds the available context` is `gate.truncation` (no retry: a retry is longer),
  any other received error is `gate.model` (retry once). (c) The system message begins with `prompt_id: <nonce>`
  (16 hex characters from `secrets.token_hex(8)`, one per `ask`) and the card asks the model to write the object's
  first key as `"prompt_id": "<nonce>"` and its last key as `"end_id": "<nonce>"`; an answer whose text does not
  begin `{ "prompt_id": "<nonce>",` fails `gate.truncation: prompt cut (prompt_id missing)` without retry, because an
  Ollama that ignores `truncate` (older than D0.2) cuts tokens from the front (`llama_server.go:331-332` keeps
  `nKeep` then the tail; `NumKeep` defaults to 4 at `api/types.go:1226`, plus one for BOS: the five kept tokens are
  the template header `<|im_start|>system\n` and the first token of the `prompt_id` label), and the nonce value sits
  beyond the kept tokens, so any cut that reaches card or page text has removed it, while a cut of one or two tokens
  loses only the label and no content; the model cannot guess 64 random bits. An answer whose last key is not `"end_id":
  "<nonce>"` fails `gate.truncation: answer cut (end_id missing)` with one retry, which catches a cut answer even
  when `done_reason` says `stop` and keeps gate 2's missing-closer repair from turning a cut list into a shorter
  valid one. (d) `done_reason == "stop"`, both counts positive ints, `prompt_eval_count <= num_ctx`,
  `prompt_eval_count + eval_count <= num_ctx`, `eval_count < card.max_answer_tokens`; `prompt_eval_cached_count` is
  read when present and stored (D0.2, §1.5). Rejected: comparing `prompt_eval_count` with an estimate of tokens sent
  (D0.2: a cut prompt counts about half the context, a cached prompt may count less than sent on an older Ollama, and
  the estimate is a tuning value, T-4); `/api/tokenize` (not in the native API). Cost accepted: the nonce defeats
  Ollama's prefix cache for the card text on every call (a few thousand tokens re-read per call); T-16 asks the
  stage 9 benchmark whether the nonce should move behind the card once the Studio's Ollama is known to honour
  `truncate: false`. The stage 2 runner gets only (b): `benchrun.run` sends `truncate=False` and maps the
  context-length error to `bench.truncation` (the recorded bench prompt and the stage 2 line stay as they are, D25).
- **1.2 Where the gates live and the pipeline API.** New `src/casefile/gates.py` (`Card`, `Verdict`, `Outcome`,
  `GATES = ("truncation", "repair", "schema", "quotes", "rules", "coverage")`, `messages(card, pages, nonce)`,
  `ask(card, pages, *, client, rules, log, matter, nonce=None) -> Outcome`, `open_items(log, matter)`), new
  `src/casefile/jsonrepair.py` (gate 2), new `src/casefile/schema.py` (gate 3), `quotes.py` gains the ladder
  (gate 4), `rules.py` unchanged (gate 5 calls `Rules.check`), `runlog.py` gains the coverage and gates tables
  (gate 6). `Card(name, text, schema, unit="text", think=False, max_answer_tokens=8192)` with `version` =
  `sha256(text)[:12]` (as `benchrun.card_version`). `Outcome(ok, answer, attempts, verdicts, read, failed, run_id)`:
  `answer` is the validated object with `prompt_id` and `end_id` removed and is `None` whenever `ok` is false
  (never `{}`, never an object with empty lists: "never saved as empty" in code is this invariant plus the rule that
  the caller writes nothing when `answer is None`); `read` is every page id of the chunk when ok, else `()`;
  `failed` is `((page_id, "gate.<name>: <message>"), ...)` for every page of the chunk when not ok. Messages: system
  = `prompt_id: <nonce>\n` + card text + the one-object instruction naming both ids; user = `Matter <number>\n` +
  `benchrun.page_block` per page (rules and card first, page text last, spec §5). Rejected: putting the gates in
  `model.py` (transport must stay dumb: #R02-V-F1 class fixes were all transport-local); a gate per module with a
  registry (six modules for one fixed order is ceremony; the order is a tuple in one place).
- **1.3 Retry once, in code and in the log.** Attempt 1 runs the six gates in order and stops at the first failure.
  If that failure is retryable (`gate.model` received, `gate.truncation: done_reason=length` or `end_id missing`,
  `gate.repair`, `gate.schema`, `gate.quotes`, `gate.rules`), attempt 2 sends the same system and user messages plus
  `assistant: <attempt 1 raw content>` and `user: "That answer failed the <gate> check: <message>. Answer again with
  one JSON object and nothing else, with the same prompt_id and end_id."` (the same nonce). Not retried: the budget
  refusal, the server's context-length error, `prompt_id missing` (all prompt-side: a longer retry cannot pass),
  and a `ModelError` with `received=False` (raised out of `ask`: the caller decides, as bench exit 2 does under
  Q26). Run log per `ask`: one `runs` row (`job` from the caller, `card`, `card_version`, `pages_in`,
  `prompt_sha256` of attempt 1's messages); one `answers` row per received reply (status `ok` only for the attempt
  that passed every gate); one `failures` row per failed gate per attempt (`gate.<name>`); one `gates` row per gate
  reached per attempt (`verdict` pass, fail or repaired, with the message); after the last attempt, one `coverage`
  row per page: `read` when ok, else `failed` with `gate.<name>: <message>`. The budget refusal still opens a run
  (so the refusal is logged) with a `failures` row and coverage `failed`, and no `answers` row.
- **1.4 Gate 2, JSON repair, is punctuation only, and only after both ids were seen.** `jsonrepair.repair(text,
  *, nonce) -> Repaired(text, repairs)`: (1) a leading and trailing Markdown fence (```` ```json ```` or ```` ``` ````)
  and surrounding whitespace are removed; (2) raw control characters U+0000 to U+001F inside strings become one
  space (`\n`, `\r`, `\t` included: they are invalid inside a JSON string); (3) a comma directly before `]` or `}`
  (outside strings) is removed; (4) when the text ends after the `end_id` value with fewer closers than the open
  stack needs, the missing `]` and `}` are appended. Each applied kind is one `repaired` verdict (`gate.repair:
  fence`, `control`, `trailing-comma`, `closers`). Still rejected (gate 2 fails): a missing comma between items,
  single-quoted strings, unquoted keys, an unterminated string, a second object or any text after the closers,
  `NaN`, comments. Rejected alternative: a permissive parser (json5 or a "fix anything" loop): it would hide the
  model's errors from the benchmark (pillar 6) and invent structure (pillar 1).
- **1.5 Gate 3 uses a stdlib subset validator, not the `jsonschema` package.** `schema.load(path)` accepts
  exactly the keywords in use (D0.9): `type` (one of object, array, string, integer, number, boolean, null),
  `properties`, `required`, `additionalProperties` (must be `false`), `items`, `enum`, `title`, `$schema`, and
  refuses any other keyword, any other `type`, `additionalProperties: true` or an object, and `required` names not in
  `properties` (`SchemaError`, fail closed: a schema the validator cannot enforce is not a schema). Keys under
  `properties` are names, never keywords (D0.9). `schema.validate(instance, schema) -> list[str]` reports every
  error with a path (`facts[0].text: missing required key`, `flags[1].kind: not one of conflict, gap`, `facts[0]:
  unknown key page`). The validator also enforces the stage 4 cite rule: any object holding a `quote` key must hold
  a `cite` string (the pair gate 4 checks). Why not `jsonschema`: it brings `jsonschema-specifications`,
  `referencing`, `rpds-py` (a compiled wheel) and `attrs`, needs `uv add` with the sandbox off, and would accept
  keywords (`$ref`, `oneOf`, `pattern`) that nobody here has tested against a model answer; the subset is under 120
  lines and every keyword has a red test. D6's "reuse, do not rebuild" names Docling, ocrmypdf, LangExtract,
  Presidio and docuchat; a validator for six keywords is not in that class. If stage 6's card schemas need more
  keywords, that round decides again with the benchmark in hand.
- **1.6 Gate 4, the quote ladder.** `quotes.match(quote, page_text, *, running=()) -> Match(rung, text) | None`,
  rungs tried in order and the first hit returned: `exact` (the quote as written is a substring of the page);
  `whitespace` (both collapsed to single spaces); `curly` (then curly to straight quotes and casefold: this is
  today's `normalize`); `ocr` (then, on both sides, ligatures `ﬁ ﬂ ﬀ ﬃ ﬄ` to letters, a hyphen followed by a line
  break joined (`exam-\nination` to `examination`), and on the page side every line that is a stamp token alone
  (`stamps.find` with the default pattern), a `Page N` or `Page N of M` line, or a line in `running` is dropped
  before collapsing). Near-misses each rung must reject (tests): one changed digit (`7/10` to `8/10`); a dropped
  word; a dropped `no`; a quote that skips a non-running line of the page; `MED0001` inside the quote when the page
  shows `MED0002`. `found_in` keeps its meaning (rungs 1 to 3) for `benchkey.py:84`, `doctor.py:191`, the stage 3
  tests and the fixture tests. `quotes.same(a, b)` = equality after the full folding of both strings (no page) is
  the new "same quote" test. Rejected: a similarity ratio (R03-PC-2: closeness cannot see one wrong digit); fuzzy
  matching marked unverified (spec §5 names that for LangExtract only).
- **1.7 What changes in the bench (D25's "the quote match is replaced by the §4 ladder at stage 4").**
  `benchscore.py:76` invented test becomes `quotes.match(fact.quote, page.text) is None`; `:83` found test becomes
  `k.cite == cite and quotes.same(k.quote, fact.quote)`; a new detail line `  rungs: exact=E whitespace=W curly=C
  ocr=O` is printed only when W + C + O > 0. On the shipped fixtures nothing changes (prototype in the header: every
  ideal, flawed and key quote matches at `exact`, the two invented flawed quotes match at no rung), so the two
  baseline lines, `test_bench_detail.py:17-22` and `test_stage2_exit.py:18-19` stay as they are; the regression set
  pins this with a new case per rung on the small invented pages of `tests/test_benchscore.py:19-25`. The stage 2
  runner's guards stay (D25: replaced at stage 5); the gate pipeline is used by the stage 4 exit test only.
- **1.8 Gate 5, firm rules on outputs only.** `rules.check(value, unit=card.unit, stamped=every page in the chunk
  has a stamp)` runs over every string value in the answer except values under the keys `quote`, `cite`, `cites`,
  `prompt_id`, `end_id`: a quote is the record's own words (a defense report may say "IME"; Q16 bans the label in
  what we write, never in what we read) and the cite is a stamp. Any `error` finding fails `gate.rules` with
  `<rule-id>: <excerpt>` per finding (retry once); `warning` findings (the cite rule on unstamped pages) go in the
  pass message. Owner question 43 asks whether quoted spans holding the labels may appear in outputs at all.
- **1.9 Gate 6, the coverage ledger, is two tables in the run log (schema v2).** `coverage(id, run_id, matter,
  page_id, card, status IN ('read','failed'), reason, at)` and `gates(id, run_id, attempt, gate, verdict IN
  ('pass','fail','repaired'), message, at)`, both append-only by the same triggers; `answers` gains
  `prompt_eval_cached_count INTEGER` (nullable). `RunLog.record_coverage`, `record_gate`, `coverage(matter) ->
  {(page_id, card): (status, reason, run_id)}` (latest row wins by id), `open_items(matter)` = the pairs whose latest
  status is `failed`. `open_db` upgrades a v1 file in one transaction: `DROP TRIGGER schema_meta_no_update`,
  `UPDATE schema_meta SET value='2'`, create the two tables and their update and delete triggers, `ALTER TABLE
  answers ADD COLUMN`; the existing trigger loop then recreates `schema_meta_no_update` and adds the two `no_replace`
  triggers. Trigger count 15 -> 21 (`doctor.py:79`, `test_runlog.py:26`, `test_fix_cycle2.py:159` change together);
  any version other than 1 or 2 is refused. Rejected: a per-matter `coverage.jsonl` under `pages/` (intake publishes
  that folder once by rename and refuses re-intake, D27; a mutable ledger does not belong in it; and §8b
  `matter_status` reads counts the run log already indexes by matter); a v1 schema with `IF NOT EXISTS` tables and no
  version bump (dishonest versioning; D15 names the version).
- **1.10 Stand-in modes added (D18 amended), eight:** `cut_prompt` (the recorded answer with `__PROMPT_ID__`
  replaced by `unknown`, `prompt_eval_count = ctx // 2 + 3`: an old Ollama that cut the prompt), `prompt_too_long`
  (400 `{"error": "the prompt is longer than the context length currently available to the model; shorten the
  prompt, adjust the context length in settings, or use a model with a longer context length"}` whatever `truncate`
  says), `cut_answer` (the content cut at its half, `done_reason: "stop"`: a server that lies), `repairable` (the
  recorded JSON with a comma before the closing `]` of `facts`, one raw tab inside the first `text` value, a
  ```` ```json ```` fence, and the final `}` dropped), `bad_schema` (facts[0] loses `text`), `bad_quote` (two edits: facts[0]'s
  quote with its first digit incremented, facts[1]'s cite set to `MED0099`; gate 4 checks every pair and names every
  failure in one message, so this one mode proves both the quote and the cite branch), `forbidden_json` (facts[0].text = `"The IME found no injury."`),
  `retry_ok` (a two-message request gets the `malformed` content; a four-message request whose third message is
  `assistant` and fourth `user` gets the recorded answer). Plus two behaviours in every mode: the allowed `/api/chat`
  keys gain `truncate`; the recording lookup strips a first system line matching `^prompt_id: [0-9a-f]{16}$` and the
  answer text has `__PROMPT_ID__` replaced by that nonce (so one recording serves every nonce). `MODES` becomes 15.
- **1.11 Carried lows.** Bench pre-pass: `bench.main` loads every root's matter and key, refuses a duplicate number
  (`bench: duplicate matter number N in A and B`, exit 2) and any loader error before the run log is opened and before
  any model call; `test_bench_multi.py:63` changes to `seen == []` (the late refusal was pinned, R03-PC-3 class).
  `stamps.normalize` strips every character that is not a letter or digit (`re.sub(r"[^A-Za-z0-9]", "", raw).upper()`;
  Q40, Q42: a stamp is letters plus digits); `stamps.compile(pattern)` builds the four-clause pattern and
  `config.py:124` validates through it. Step comments listed in D0.10 are removed, nothing else in those lines.
- **1.12 Stage 5 boundary.** Stage 4 ends at `Outcome`: the validated answer object, the coverage rows and
  `open_items`. Not this round: chunking pages into prompts, reading intake's `pages/<binder>/*.json` into
  `matter.Page` objects, merging into the case file, the memo, `casefile status`, the job runner, the stage 5
  replacement of `benchrun`, cards from the playbook (stage 6) and the `cards/` and `schemas/` rewrite (spec §7).
  `ask` takes `Sequence[matter.Page]` so stage 5 feeds it chunks; `running` lines for the ladder are a parameter
  stage 5 fills from the binder.

## §2 Work items, in build order

Every CHECK runs through `scripts/run.sh`; every seed is applied to a copy, confirmed with `cmp`, run, and
restored (`cmp` identical) before the pass counts (Q6, HANDOFF).

### W0 (chair-run builder in the main tree, before the lanes split): quote ladder and the stand-in's shared edits
- Files: `src/casefile/quotes.py` (`Match`, `match`, `same`, `fold` helpers; `found_in` unchanged), `tests/test_quotes.py`
  (a `LADDER` table), `tests/fakemodel/core.py:76-78` (`truncate` added to the allowed keys), `:11` and `:106-124`
  (mode `prompt_too_long` only; the other seven modes are W4), `tests/test_fakemodel.py` (one case for the key and
  one for the mode).
- Ships: `ladder_ok=14 of 14` over the cases: exact hit; whitespace hit (`7/10   in the\nlow back`); curly hit;
  casefold hit; ligature hit (`ﬁnding` on the page, `finding` in the quote); hyphen line break hit (`exam-\nination`);
  stamp line dropped (quote spans a line `MED0001` alone); `Page 2 of 5` line dropped; `running=("Harrowgate
  Clinic",)` line dropped; rejects: one changed digit, a dropped `no`, a dropped word, a skipped ordinary line, an
  empty quote. `same("Today’s exam", "today's   exam") is True`; `same("7/10", "8/10") is False`.
  `fake_truncate_key=1 prompt_too_long_status=400`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_quotes.py tests/test_fakemodel.py` prints `ladder_ok=14 of 14` and
  `quotes_ok=8 of 8` (the old table still passes) and passes.
- Seeds, each alone: (a) the `ocr` rung's line-drop applies to every line, not only stamp, page and running lines ->
  the "skipped ordinary line" reject case passes wrongly, `ladder_ok=13 of 14`; (b) the digit case compared after
  `casefold` of digits (`re.sub(r"\d", "0", ...)`) -> `13 of 14`; (c) `truncate` left out of the allowed keys ->
  `fake_truncate_key=0`.
- Librarian pre-flight: #R03-PC-2 (one changed digit and a dropped `no` must fail), #R03-CX-5 (a token inside a
  longer token: the stamp-line rule drops whole lines only), #R01-OC-M2 (no silent default: `running` defaults to
  empty, which drops nothing extra).

### W1 (lane A): model client, `truncate: false`, counts and the budget (R4-2 client side)
- Files: `src/casefile/model.py:36-42` (`Answer` gains `prompt_eval_cached_count: int | None`), `:97-117` (`chat(self,
  messages, *, options=None, think=None, truncate=None)`: `think` and `truncate` are added to the body only when not
  `None`, so the doctor's and the bench's bodies are byte-identical to today; `prompt_eval_cached_count` typed like
  the other counts at `:111-113`), new module constants `CHARS_PER_TOKEN_FLOOR = 2.0`, `tokens_at_most(chars) ->
  int`, `context_length_error(message) -> bool` (case-insensitive `context length` or `exceeds the available
  context`), `src/casefile/benchrun.py:68` (`truncate=False`), `:69-75` (a received `ModelError` whose message passes
  `context_length_error` is logged under `bench.truncation`, the rest stays `bench.model`), `tests/test_model.py`,
  `tests/test_benchrun.py` (a `prompt_too_long` case appended to `test_benchrun_modes`: the gate list at `:116` gains
  a seventh entry `bench.truncation`, the printed `benchrun_modes=8 of 8`), `tests/test_bench_cli.py`.
- Ships: `chat_body_keys=1` (the doctor body is exactly `{"model","messages","stream","options"}`; a pipeline body
  adds `think` and `truncate`), `cached_count_read=1` (`prompt_eval_cached_count: 7` lands in `Answer`; `"x"` is a
  `ModelError`), `tokens_at_most(0)=0`, `tokens_at_most(3)=2`, `tokens_at_most(131072)=65536`, `benchrun_modes=8
  of 8`, bench on `prompt_too_long` prints `bench 9001.001 failure bench.truncation: status=400: ...` then the
  `found=0 of 29 ... pages_failed=14 of 14` line, exit 1.
- CHECK: `scripts/run.sh pytest -q -s tests/test_model.py tests/test_benchrun.py tests/test_bench_cli.py` prints
  `chat_body_keys=1 cached_count_read=1 benchrun_modes=8 of 8` and passes.
- Seeds, each alone: (a) `truncate` always sent -> the doctor body test red (`chat_body_keys=0`); (b)
  `context_length_error` returns False -> the new benchrun case logs `bench.model`, gate list red; (c) `tokens_at_most`
  uses floor division -> `tokens_at_most(3)=1`, red; (d) the cached count accepted as any type -> the `"x"` case
  red.
- Librarian pre-flight: #R01-CX-5 and #R01-CX-10 (every answer path reads the counts; each guard has a probe where
  only it is wrong), #R02-V-F1 (the 400 reply is stored as a failed row, which the existing path does), #R02-CH-1
  (zero and boundary values tested: `tokens_at_most(0)`).

### W2 (lane A): `jsonrepair.py` and `schema.py` (gates 2 and 3)
- Files: new `src/casefile/jsonrepair.py` (`Repaired(text, repairs)`, `RepairError`, `unfence(text)`, `repair(text, *,
  nonce)`; a small state machine over the text that knows when it is inside a string and tracks the open stack),
  new `src/casefile/schema.py` (`SchemaError`, `load(path) -> dict`, `check_schema(schema)`, `validate(instance,
  schema) -> list[str]`), new `schemas/bench_extract.schema.json` (object with `facts` of `{cite, quote, text}` and
  `flags` of `{kind enum conflict|gap, cites array of string, about}`, `additionalProperties: false` everywhere,
  `title: bench_extract`), new `tests/test_jsonrepair.py`, `tests/test_schema.py`.
- Ships: `repair_ok=12 of 12`: fence removed; control char in a string to a space; trailing comma before `}`;
  trailing comma before `]`; missing `]}` appended after `"end_id": "<nonce>"`; all four at once; and six rejects:
  missing comma between items, single quotes, unquoted key, unterminated string, text after the closers, a comma
  before `]` inside a string left alone (the string is unchanged and the text parses as is). `schema_ok=14 of 14`:
  every keyword accepted once and violated once (type, properties, required, additionalProperties, items, enum), the
  cite rule (a `quote` without `cite`), a property named `type` (D0.9), and refusals at load: `$ref`, `oneOf`,
  `pattern`, `additionalProperties: true`, `type: ["string","null"]`, a `required` name not in `properties`.
  `schemas_loaded=20 of 20` (the 19 existing files plus `bench_extract` load without error).
- CHECK: `scripts/run.sh pytest -q -s tests/test_jsonrepair.py tests/test_schema.py` prints `repair_ok=12 of 12
  schema_ok=14 of 14 schemas_loaded=20 of 20` and passes.
- Seeds, each alone: (a) the closer repair runs without checking that `end_id` was the last key -> the
  "unterminated string" reject case gets closers and parses, `repair_ok=11 of 12`; (b) trailing-comma removal
  applied inside strings -> the last case changes the string, red; (c) `validate` treats keys under `properties`
  as keywords -> the `type` property case red; (d) `check_schema` ignores unknown keywords -> the `$ref` refusal
  case red; (e) `required` not enforced -> red.
- Librarian pre-flight: #R02-CX-5 (a loader refuses what the checker cannot tell apart: unknown keywords), #R01-OC-M2
  (no silent default: `additionalProperties` absent is an error, not "true"), #R03-PC-2 (one changed character is
  a difference).

### W3 (lane A): run log schema v2 (gate 6 storage, D15 amended)
- Files: `src/casefile/runlog.py:8-34` (`SCHEMA` v2 for a new file: five tables plus `coverage` and `gates`,
  `answers.prompt_eval_cached_count`), `:67-75` (`record_answer(..., prompt_eval_cached_count=None)`), new
  `record_gate`, `record_coverage`, `coverage`, `open_items`, `:105-133` (`open_db`: v1 upgrade in one transaction as
  §1.9; `schema_version` 2 required after it), `src/casefile/doctor.py:79` (`version == 2 and count == 21`,
  `schema={version} triggers={count}`), `tests/test_runlog.py:26` (`== 21`), `tests/test_fix_cycle2.py:159`
  (`schema=2 triggers=21`), `tests/test_doctor.py` (grep finds no `schema=1` text today; nothing to change there),
  new tests in `tests/test_runlog.py`.
- Ships: `triggers=21`, `blocked_writes=12 of 12` (update and delete on six tables), `upgrade_v1=1` (a v1 file made
  by the committed v1 `SCHEMA` text kept in the test as a string: after `open_db` its rows are intact, version 2,
  21 triggers; the second open is a no-op), `coverage_latest=1` (two rows for one page: the later wins),
  `open_items=1 of 2` (one page read then failed, one read: only the first is open), `version_3_refused=1`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_runlog.py tests/test_doctor.py tests/test_fix_cycle2.py
  tests/test_stage1_exit.py` prints `triggers=21 blocked_writes=12 of 12 upgrade_v1=1 coverage_latest=1
  open_items=1 of 2` and `exit=0 verdicts=8 fails=set() test_jobs=1`, and passes.
- Seeds, each alone: (a) the upgrade forgets the coverage triggers -> `triggers=19`, red; (b) `coverage()` orders by
  `at` text instead of `id` with two rows in one second -> `coverage_latest=0`; (c) the upgrade runs outside a
  transaction and the ALTER is skipped -> `record_answer` with a cached count raises, red; (d) `open_db` accepts
  version 3 -> red.
- Librarian pre-flight: #R01-CX-3 (append-only: `INSERT OR REPLACE` refused on the new tables with recursive
  triggers off, one parametrised case each), #R01-V-B2 (the refused-version branch has its own test), #R01-OC-M7 (the
  upgrade never creates a file that did not exist: `open_db` already creates the parent, nothing more).

### W4 (lane A): `gates.py`, the stand-in's seven modes and recording, pipeline unit tests
- Files: new `src/casefile/gates.py` (§1.2, §1.3; gate order and the retry rule in one function `ask`; `GATE_NAMES`
  used by the run log rows; `_rules_strings(obj)` skipping the five keys of §1.8; the cite lookup over the chunk:
  `stamps.normalize(cite) in page.stamps or cite == page.page_id`), `tests/fakemodel/core.py:11` (`MODES` to 15),
  `:102-104` (lookup after stripping the nonce line; `__PROMPT_ID__` substitution), `:106-124` (the seven modes of
  §1.10 other than `prompt_too_long`), `tests/fakemodel/bench.py:10-15` (`recordings_for` returns two rows: the stage
  2 bench row as today and a `gates-<number>` row built from `gates.messages(card, pages, "__PROMPT_ID__")` with the
  answer `{"prompt_id": "__PROMPT_ID__", ...ideal.json..., "end_id": "__PROMPT_ID__"}` written with `prompt_id` first
  and `end_id` last), `tests/test_fakemodel.py` (the mode list; the nonce lookup), new `tests/test_gates.py` (in
  process through `FakeTransport`, one invented small matter of three pages plus the 9001.001 matter).
- Ships: `gate_cases=20 of 20`: good answer (`ok`, 14 `read`, answers rows 1 ok, gates rows 6 pass); budget refusal
  (a card with `max_answer_tokens = 65536 - 10`, no request made, `failed` 14, failures `gate.truncation`);
  `prompt_too_long` (one request, no retry, `gate.truncation`); `cut_prompt` (no retry, `prompt_id missing`);
  `truncated` (retry, both attempts `done_reason=length`, `failed` 14, two answers rows both `failed`, `answer is
  None`); `cut_answer` (`end_id missing`, retry); counts: `prompt_eval_count > num_ctx` fails; `eval_count >=
  max_answer_tokens` fails; `repairable` (ok after four `repaired` rows, `answer == ideal`); `malformed` (fail twice,
  `gate.repair`, the second request's fourth message holds `failed the repair check`); `bad_schema` (`gate.schema`);
  `bad_quote` (`gate.quotes`, message names the pages searched and both faults: the quote on `MED0001` and
  the cite `MED0099`); a cite not in the chunk alone (the payload patched in the test as `test_benchrun.py:15-26`
  does, `gate.quotes`); `forbidden_json` (`gate.rules: no-dme-ime`); a quote holding `IME` on a page that holds it passes gate 5; an
  unstamped three-page chunk passes with a `warning` message; `retry_ok` (attempt 1 fails repair, attempt 2 ok,
  `attempts=2`, coverage `read`, answers rows failed then ok); `received=False` raises `ModelError` with no run log
  row after the run row; `open_items` after `malformed` then `retry_ok` on the same pages is empty (latest wins);
  the request body carries `"truncate": false` and `"think": false` and options `num_predict`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_gates.py tests/test_fakemodel.py` prints `gate_cases=20 of 20
  modes_ok=6 of 6` and passes.
- Seeds, each alone: (a) the `end_id` check dropped -> `cut_answer` passes gate 1 and fails later or passes:
  `gate_cases=19 of 20`; (b) `prompt_id missing` made retryable -> the request count in the `cut_prompt` case is 2,
  red; (c) gate 5 run over `quote` values too -> the "quote holding IME" case red; (d) `Outcome.answer = {}` on
  failure -> the `answer is None` assertion red; (e) gate order swapped (rules before quotes) -> the `bad_quote` case
  reports `gate.quotes` still but the gates rows differ, red on the rows list; (f) coverage written before the retry
  instead of after -> `open_items` case red.
- Librarian pre-flight: #R01-CX-10 (each gate 1 check has a probe where only it is wrong: cut_prompt, cut_answer,
  truncated, the two count probes, prompt_too_long, budget), #R03-V-L1 (the budget refusal happens before the first
  side effect other than the run row), #R02-V-F1 (every received reply is an answers row, attempt 2 included),
  #R01-OC-M2 (`Card.unit` has a default only because `text` is the spec's unit for every stage 4 and 5 card; the
  stage 6 question cards must set it, noted in the docstring), #R03-OC-L1 (a failure message names the gate, the
  pages searched and what to do).

### W5 (lane B, worktree): bench on the ladder, bench pre-pass, benchrun gate map, `normalize`, comments (R4-2 bench, R4-4)
- Files: `src/casefile/benchscore.py:76, :83` (§1.7), `:50-63` (the `rungs` detail line; `Score` gains `rungs:
  tuple[tuple[str,int],...]`), `src/casefile/bench.py:62-79` (pre-pass: a list of `(root, matter, key)` built before
  the run log opens; the duplicate check in that loop), `:21-122` (comments removed), `src/casefile/benchcandidate.py:
  39-77` (comments removed), `src/casefile/stamps.py:14` (`normalize`), new `compile(pattern)` used by `:23` and
  `src/casefile/config.py:124`, `tests/test_benchscore.py` (one case per rung: a page with `ﬁnding` and a candidate
  quote `finding` is found, not invented; a whitespace variant of a key quote is `found`; a changed digit is still
  `invented`), `tests/test_bench_detail.py` (the `rungs` line appears for the ligature case and not for the shipped
  fixtures), `tests/test_bench_multi.py:46-65` (`seen == []`; a bad key in root `b` refuses before root `a` runs:
  `seen == []`, exit 2), `tests/test_stamps.py` (`normalize("MED.0001") == "MED0001"`, `normalize("med_0001")
  == "MED0001"`), `tests/test_config.py` (the stamp pattern error path still exits 2).
- Ships: `score_cases=14 of 14` (eleven today plus three rung cases), the baseline lines unchanged (`found=29 of
  29 ... flags=9 of 9 ...` exit 0; `found=26 of 29 missed=3 invented=2 ... flags=8 of 9 ...` exit 1, same six
  detail lines, no `rungs` line), `duplicate_numbers_exit=2` with `seen == []`, `stamps_cases=8 of 8`, grep
  `"# (Load|Find|Check|Main|Process|Return|Score|Final)"` over `bench.py` and `benchcandidate.py` -> 0 lines.
- CHECK: `scripts/run.sh pytest -q -s tests/test_benchscore.py tests/test_bench_detail.py tests/test_bench_multi.py
  tests/test_stamps.py tests/test_config.py` prints `score_cases=14 of 14 duplicate_numbers_exit=2 stamps_cases=8 of
  8` and passes; `scripts/run.sh casefile bench --config config.example.toml --matters tests/fixtures/matters
  --candidate tests/fixtures/bench/flawed.json` prints the baseline line and exits 1.
- Seeds, each alone: (a) `benchscore.py:76` back to `found_in` -> the ligature case counts `invented=1`, red; (b)
  the `rungs` line printed always -> `test_bench_detail` red on the shipped fixture; (c) the duplicate check moved
  back after the run -> `seen == ["a"]`, red; (d) `normalize` strips `[ -.]` only -> the `med_0001` case red; (e)
  `config.py` keeps its own wrapper -> the new config test, which monkeypatches `stamps.compile` to raise
  `re.error("probe")` and expects `ConfigError ... not a valid pattern: probe`, gets no error, red.
- Librarian pre-flight: #R03-V-L1 (refusal before the first side effect: no run log open, no model call), #R03-PC-3
  (the test that pinned the old order is named and changed), #R02-CX-5 (collisions refused up front), #R03-CX-5
  (`normalize` and the whole-token rule stay separate: finding is unchanged).

### W6 (lane B, worktree): verifier gaps S1, S2, S5 (R4-3) and suite time (T-11)
- Files: `tests/test_stage3_exit.py:41-47` (`"id": record["id"] == f"scan/{n:03d}" and record["matter"] ==
  "9002.001" and record["page"] == n`), `tests/test_intake.py:172` (a `sidecar 7 of 6` case beside `5 of 6`:
  `{"sidecar": "\f".join(["a"] * 7)}` expecting `sidecar segments=7 pages=6`; `:195` `len(cases) == 16`, the printed
  `intake_refusals=16 of 16`), `tests/test_scanned_fixture.py:63-72` (a second change: page 5's `lines` with
  `"Frequency: two visits per week for four weeks."` changed to `"... for five weeks."` expecting `content_equal=0`
  and `check page 5 differs`, with page 2 untouched), `tests/conftest.py` (a session-scoped `scanned_intake` fixture
  that runs the real command once, `scripts/run.sh casefile intake --matter 9002.001 --binder scan
  tests/fixtures/scanned/scanned.pdf` with `CASEFILE_CONFIG` from `write_config` on a `tmp_path_factory` folder,
  exactly as `test_stage3_exit.py:53-58` does today, and yields the `CompletedProcess`, the config and the matter
  root), `tests/test_stage3_exit.py:51-63` (reads the fixture instead of running the command; every assertion and
  the printed line unchanged), `tests/test_intake.py:421-449` (`test_intake_fixture_with_real_tools` reads the same
  fixture's records, `binder.json`, `source.pdf` and the command's stdout and exit code instead of calling
  `intake.intake`; assertions unchanged, `code == 1` now the command's code), `docs/loop/tuning-questions.md`
  (T-11 measurement appended at close by the chair, not by the lane).
- Ships: `ids_ok=6 of 6` still, `intake_refusals=16 of 16`, `check page 5 differs`, suite wall time measured
  three times with nothing else running, each under 90 s (`real` from `/usr/bin/time -p scripts/run.sh pytest
  -q`), and real OCR runs in the suite 5 -> 4 (one intake of the fixture through the real command, shared by the
  two tests; three doctor smokes: both stage 1 exit tests and `test_ocr_real_tools`).
- CHECK: `scripts/run.sh pytest -q -s tests/test_stage3_exit.py tests/test_intake.py tests/test_scanned_fixture.py`
  prints `stage3 exit=1 pages=6 ids_ok=6 of 6 ...` and `intake_refusals=16 of 16` and passes; `/usr/bin/time -p
  scripts/run.sh pytest -q` -> `real` under 90.
- Seeds, each alone (the verifier's own, restored by `cmp`): (a) `intake.py:306` `PageRecord(number,` ->
  `PageRecord(source.stem,` -> `ids_ok=0 of 6`, red; (b) `intake.py:85` `!=` -> `<` -> the `7 of 6` case red; (c)
  `make_scanned.py` `if a != b` -> `if a[0] != b[0]` -> `check page 5 differs` absent, red; (d) the session fixture
  skipping intake when the folder exists from an earlier session (a cache keyed on a path outside `tmp_path_factory`)
  -> `production_dirs_untouched` or the fixture's own `assert not root.exists()` red.
- Librarian pre-flight: #R01-V-B2 (a field, a direction and a layer each with its own assertion), #R03-PC-2 (the
  text-layer oracle fails on one changed word), #R01-OC-M7 (the session fixture never reuses a folder it did not
  create this session), T-11 (never a skip: the `ocr` marker tests still run the real tools).

### W7 (lane A, after W1 to W4; the stage 4 exit test, R4-1)
- Files: new `tests/test_stage4_exit.py` (socket test like `test_stage2_exit.py:49-78`: one stand-in server with the
  9001.001 recordings on a loopback port, mode switched through `POST /_fake/mode` between cases; the pipeline run
  through `ModelClient` with the real opener and a real run log in `tmp_path`), `docs/loop/round-04/` (the chair's
  records, not the lane).
- Ships, printed with `capsys.disabled()`, one line per gate then one summary line:
  `stage4 gate=truncation good=pass bad=2 of 2 truncated=4 of 4 retry=1`
  `stage4 gate=repair good=pass bad=1 of 1 truncated=0 of 4 reached repaired=4`
  `stage4 gate=schema good=pass bad=1 of 1 truncated=0 of 4 reached`
  `stage4 gate=quotes good=pass bad=1 of 1 faults=2 truncated=0 of 4 reached`
  `stage4 gate=rules good=2 of 2 bad=1 of 1 truncated=0 of 4 reached warning=1`
  `stage4 gate=coverage good=14 read bad=14 failed truncated=0 of 4 reached open_items=14`
  `stage4 exit=0 gates=6 of 6 cases=13 of 13 runs=+13 answers=+19 empty_saved=0 server_stopped=1`
  where good = the `replay` mode passes the gate (for rules, also the three-page probe below); bad = the gate's own
  bad mode fails at that gate (truncation: `cut_prompt`, `prompt_too_long`; repair: `malformed`; schema:
  `bad_schema`; quotes: `bad_quote`, whose one message names both faults, `faults=2`; rules: `forbidden_json`;
  coverage: the `malformed` outcome's 14 `failed` rows); truncated = the four truncated cases (`truncated`,
  `cut_answer`, `cut_prompt`, `prompt_too_long`) all fail at gate 1, and `0 of 4 reached` says none reached a later
  gate (read from the `gates` rows); `retry=1` is the `retry_ok` case; `empty_saved` counts outcomes with `ok` false
  and `answer is not None` plus answers rows with status `ok` for a failed attempt (must be 0); `runs` and `answers`
  are deltas in the run log. The three-page probe is an invented unstamped matter built in the test (clinic
  `Harrowgate Occupational Clinic`, pages `probe/001` to `probe/003`, no stamp on any page, page 2 holding the
  sentence `The IME report of 03/02/2026 notes a normal gait.`) with a recording row added to the server's rows
  whose answer quotes that sentence with the text `The report notes a normal gait.` and cites `probe/002`: it passes
  gate 5 (the quote is exempt) with the cite rule's `warning` (unstamped), `warning=1`. The `answers` delta is fixed
  by the case list: replay 1, budget 0, cut_prompt 1, prompt_too_long 1, truncated 2, cut_answer 2, repairable 1,
  malformed 2, bad_schema 2, bad_quote 2, forbidden_json 2, retry_ok 2, probe 1 = 19 over 13 runs (the budget refusal
  makes a run row and no answer row).
- CHECK: `scripts/run.sh pytest -q -s tests/test_stage4_exit.py` prints the seven lines above with `stage4 exit=0`
  and passes; the test asserts every number on those lines and exits non-zero (pytest failure) on any miss.
- Seeds, each alone: (a) `gates.py` end_id check dropped -> `truncated=3 of 4` and `cut_answer` reaches gate 2,
  `reached=1`, red; (b) coverage `read` written when gate 5 warns -> unchanged (a warning passes: this seed must stay
  green, and the brief says so to stop a builder from "fixing" it); (c) coverage rows written on attempt 1's failure
  before the retry -> `open_items` after `retry_ok` is 14, red; (d) `Outcome(ok=False, answer={"facts": [],
  "flags": []})` -> `empty_saved=1`, red; (e) gate 5 run over quotes -> the three-page probe fails `gate.rules:
  no-dme-ime` -> `good=1 of 2` on the rules line, red (the ideal answer's quotes trip no rule, measured: `[]` from
  `Rules.check` over all 31, so the probe is the only case that can catch this seed).
- Librarian pre-flight: #R01-CX-11 (the assertion is on the run log rows and the outcome, with the exit code of the
  server and pytest), #R01-P-1 and round 1 process notes (the server is stopped in `finally`; `server_stopped=1`
  printed), #R02-OC-H1 (the good answer is the ideal key read against the pages, already verified in round 3).

### W8 (chair, at the close): records
- `docs/spec.md` §9 D31 to D37 (§6), §4 unchanged text plus a sentence on `prompt_id` and `end_id` under gate 1 and
  on `truncate: false` under §5's model client row, §11 stage 4 row; `docs/loop/tuning-questions.md` T-16 to T-18
  (§4); `Librarian.md` round 4 entries; ledger baselines (`gate` 0, suite count and time, the stage 4 lines).

## §3 Parallelisation map

- W0 first, in the main tree, by one builder, committed by the chair; both lanes start from that commit.
- Lane A (main tree): W1, W2, W3, W4, W7, in that order. Owns `src/casefile/model.py`, `benchrun.py` (lines 68 to 75
  only), `jsonrepair.py`, `schema.py`, `gates.py`, `runlog.py`, `doctor.py:79`, `schemas/bench_extract.schema.json`,
  `tests/fakemodel/core.py`, `tests/fakemodel/bench.py`, `tests/test_model.py`, `test_benchrun.py`, `test_bench_cli.py`,
  `test_jsonrepair.py`, `test_schema.py`, `test_runlog.py`, `test_doctor.py`, `test_fix_cycle2.py`, `test_fakemodel.py`,
  `test_gates.py`, `test_stage4_exit.py`.
- Lane B (worktree `.claude/worktrees/r4-lane-b`, branch `r4/lane-b`, its own `uv sync` by the chair with the
  sandbox off, D0.11): W5 then W6. Owns `src/casefile/benchscore.py`, `bench.py`, `benchcandidate.py`, `stamps.py`,
  `config.py:124`, `tests/conftest.py`, `tests/test_benchscore.py`, `test_bench_detail.py`, `test_bench_multi.py`,
  `test_bench_discovery.py`, `test_stamps.py`, `test_config.py`, `test_stage3_exit.py`, `test_intake.py`,
  `test_scanned_fixture.py`.
- Shared-file splits: `benchrun.py` is lane A's at lines 68 to 75 and untouched by B (B's bench changes never enter
  it); `tests/fakemodel/core.py` is W0's for the key and one mode, then lane A's; `quotes.py` is W0's only (neither
  lane edits it; a lane that needs a change files it to the chair). `tests/conftest.py` is lane B's; lane A's socket
  test uses `write_config` as it stands.
- Sequential and why: W0 before both (the ladder is used by A's gate 4 and B's scorer; the `truncate` key by A's W1
  and B's benchrun test); W7 after W1 to W4 (it drives the whole pipeline over a socket); the merge of B into A's tip
  by the chair, then the full suite, gate and bench baselines, then Codex 8a.

## §4 Test design

- Regression set unchanged in meaning: the three stage exit lines, the two bench baseline lines and their six detail
  lines (§1.7), `test_benchrun.py:116`'s gate list plus one entry, `test_fakemodel.py` six-mode loop, the doctor's
  eight verdicts. Numbers that move on purpose: `triggers=15` -> `21` in three files (W3); `intake_refusals=15` ->
  `16` (W6); `benchrun_modes=7 of 7` -> `8 of 8` (W1); `seen == ["a"]` -> `seen == []` (W5); `MODES` 7 -> 15.
- New tables, each a `*_ok=N of N` line: ladder 14, repair 12, schema 14, gates 20, score 14, stamps 8; the stage 4
  exit test's seven lines (W7). Every line's N is fixed in §2 so a builder cannot pad or trim a table unnoticed.
- Suite time (T-11): measured 95.33 s today under load, 72.67 s at the round 3 close. W6 removes one real intake (the
  11.5 s test shares the stage 3 fixture run); the stage 4 tests add about 3 s (one loopback server, SQLite in
  `tmp_path`, no OCR). Acceptance: three consecutive `/usr/bin/time -p scripts/run.sh pytest -q` runs with nothing
  else running, each `real` under 90. If still over: second lever, `test_config.py::test_matters_alias_table` (9.68 s,
  19 `config show` subprocesses) runs the rows in process through `config.load` and keeps one subprocess row, logged
  as T-18; never a skip, never a marker left out of the default run.
- Tuning entries for the chair to append at close: T-16 the prompt nonce position (front, defeating the prefix
  cache; move behind the card once the Studio's Ollama is shown to honour `truncate: false`, measured by prompt eval
  time on the stage 9 benchmark); T-17 `CHARS_PER_TOKEN_FLOOR = 2.0` and `Card.max_answer_tokens = 8192` (measure
  `prompt_eval_count / chars` from the run log on the Studio before changing either); T-18 the suite's second lever
  above.
- The Codex plan review should attack: the end_id regex against models that emit the keys in another order; the
  repair state machine on escaped quotes (`\"`) and `\\` at a string end; the v1 to v2 upgrade on a file opened by
  another process (WAL); the stand-in's nonce stripping when a card text itself contains `prompt_id:`.

## §5 Risks, each with a measurable tripwire

- R1 The Studio's Ollama ignores `truncate: false` (older than D0.2) and cuts prompts. Tripwire: stage 9, the run
  log's `prompt_eval_count` on a 60 k-token probe prompt below 40 000 with no `gate.truncation` row; the `prompt_id`
  check is the backstop and T-16 keeps the nonce in front until that probe passes.
- R2 Qwen writes `prompt_id` and `end_id` unreliably, failing good answers at gate 1. Tripwire: stage 9, more than 2
  of 100 pipeline calls fail with `prompt_id missing` or `end_id missing` while `done_reason=stop` and the content
  parses; then the ids move into a `format` schema (T-16 follow-up), never dropped.
- R3 The repair gate masks model errors. Tripwire: bench `missed` on a `repairable`-style run differs from the
  `replay` run (must be 0 difference: W5's score cases), and the `gates` table's `repaired` rows per 100 calls on
  the Studio above 10 is reported in the stage 9 report.
- R4 The subset validator diverges from JSON Schema on a keyword stage 6 needs. Tripwire: `schemas_loaded=20 of
  20` goes red the day a schema uses an unsupported keyword (the loader refuses it), which is the signal to decide
  again, not to widen silently.
- R5 The v1 to v2 upgrade corrupts an existing `state/runlog.sqlite`. Tripwire: `upgrade_v1=1` with row counts
  compared before and after; the chair runs `casefile doctor` on this Mac's own `state/` copy (invented data only)
  before merging and reads `schema=2 triggers=21`.
- R6 Suite time stays over 90 s. Tripwire: the three-run measurement in §4; the second lever is pre-approved.
- R7 Lane B's `test_bench_multi` change hides a regression in error order. Tripwire: the new case (bad key in root
  `b`, `seen == []`, exit 2) plus the existing bad-key CLI case (`test_bench_cli.py:83`) both red when the pre-pass
  is removed.
- R8 The exit test's `answers=+19` drifts when a case is added. Tripwire: the summary line's `cases=13 of 13` and the
  per-case table in the test both change together or the test is red; the chair re-derives 19 from the table.

## §6 Contradictions and new spec rows (pending veto)

- **D31** (new; spec §4 and §5 model client row amended). Old text (§4): "1. Truncation: the answer did not stop
  early, and the model read as many tokens as were sent." New: "1. Truncation: the prompt was within budget before
  the call (`tokens_at_most`), the call asked the server not to cut (`truncate: false`), the answer begins with the
  call's `prompt_id` and ends with its `end_id`, and `done_reason` and the token counts agree with the context."
  Why: D0.2 shows a cut prompt counts about half the context and a cached prompt may count less than sent, so the
  old sentence has no sound test; the four checks of §1.1 are each probed alone. Row: the gate pipeline of §1.2 and
  §1.3 (`gates.py`, order, retry rule, `Outcome.answer is None` on failure, gate names `gate.<name>`, firm rules
  skip `quote`, `cite`, `cites`, `prompt_id`, `end_id`).
- **D32** (D15 amended). Run log schema v2: `coverage` and `gates` tables, `answers.prompt_eval_cached_count`,
  v1 upgraded in place in one transaction, triggers 21, any other version refused (§1.9). Why: gate 6 needs a durable
  per-page ledger and §8b `matter_status` reads it; the published `pages/` folder is immutable by D27.
- **D33** (new). JSON repair is punctuation only, the four kinds of §1.4, each logged as `repaired`; the closer
  repair runs only after `end_id` was seen last; everything else is `gate.repair` failure. Why: pillar 1 and 6, the
  cut-list hazard in §1.1(c).
- **D34** (new). Schema check by a stdlib subset validator over `type, properties, required, additionalProperties:
  false, items, enum, title, $schema`; any other keyword or value refuses the schema at load; every object with a
  `quote` key carries a `cite` string; `schemas/bench_extract.schema.json` is the stage 4 card's schema. Why: §1.5.
  Spec §7's "stage 6 updates them" gains: the 19 schemas are loaded by this validator today (D0.9) and stage 6 keeps
  them inside the subset or decides again with the benchmark.
- **D35** (D25 amended, the sentence "a fact's text is not compared with its quote at stage 2 (the §4 ladder,
  stage 4)" replaced). New: "invented = cite not a page of the matter or quote matched at no rung of the §4 ladder
  (`quotes.match`); found = same cite and the same quote after the ladder's folding (`quotes.same`); a `rungs:`
  detail line when any match used a rung other than exact; the stage 2 runner's own guards stay until stage 5." Why:
  §1.6, §1.7; the shipped numbers do not move.
- **D36** (D18 amended). Stand-in modes: the seven of D18 plus `prompt_too_long`, `cut_prompt`, `cut_answer`,
  `repairable`, `bad_schema`, `bad_quote`, `forbidden_json`, `retry_ok` (15); `truncate` accepted on `/api/chat`; the
  lookup ignores the nonce line and substitutes `__PROMPT_ID__`. Why: §1.10, the exit test's four truncated cases.
- **D37** (D28 amended). Two roots with one matter number, or any loader error, are refused before the run log is
  opened and before any matter runs; `stamps.normalize` keeps letters and digits only; one `stamps.compile` wrapper
  for the finder and the config check. Why: R03-V-L1; Q40 and Q42 say a stamp is letters plus digits.
- No owner ruling is overridden. OR-4's sentence "Ollama does not count cached prompt tokens" is narrowed by D0.2
  (true for an Ollama whose llama-server sends no `cache_n`, false on current main); the design holds either way.

## §6b Privacy

Every fixture this round adds is invented: `schemas/bench_extract.schema.json` (structure only); the stand-in's
stage 4 recording is built at run time from the invented matter 9001.001 and its `ideal.json`; the modes edit that
text (a digit, a key, a tab, the sentence "The IME found no injury."); `tests/test_gates.py`'s three-page matter
uses the invented clinic names and stamps of the round 2 fixtures (`Harrowgate Occupational Clinic`, `MED0001` to
`MED0003`); the v1 run log in `tests/test_runlog.py` holds the rows `_start` writes today (`invented-model`,
`pb-invented`). No PDF, image or Word file is added. No real client record, name or fact appears in this brief, in
any test, or in any probe; the Ollama source read for D0.2 is public code.

## §7 Questions only the owner can answer (appended to `docs/loop/questions-for-owner.md` as 42 to 46)

42. When a chunk of pages fails both attempts, should you be able to mark those pages as read by hand (an approval
    row in the run log, with your name) so the memo can proceed with them, or must a failed page stay open until the
    model reads it on a later run? Interim: open until the model reads it; no manual read.
43. A quote copied from a defense report may itself say "IME" or "retained by the employer". The firm rule check
    skips quoted spans (they are the record's words, not ours) and checks everything we write around them. Is that
    right, or should a quote holding those labels never appear in an output either? Interim: quotes are exempt.
44. Do your scanned binders carry a repeated line on every page besides the Bates stamp (firm name, "CONFIDENTIAL",
    a fax header, a date), which the quote check should ignore when a quoted passage runs across it? If so, what
    does it look like (shape only, no example from a file)? Interim: only a stamp alone on a line and "Page N of M"
    lines are ignored.
45. When a quote matches the page only through the OCR-fault rung (a ligature, a hyphen at a line end, a header
    inside the passage), should the memo mark it (for example "[OCR]") so you check the page by eye, or treat it as
    verified like an exact match? Interim: counted as verified; the rung is recorded in the run log only.
46. Repairs to an answer's punctuation (a trailing comma, a missing final brace) are logged and the answer is used.
    Should any output tell you that its source answer was repaired, or is the log enough? Interim: the log only.
