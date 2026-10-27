# Round 4 build brief: stage 4 model client and gates (plus R4-2 to R4-4)

Branch `loop/round-04` at `54932ba` (working tree: untracked `.agents/`, `AGENTS.md`; leave them). Scope: ledger
R4-1 (spec §7 stage 4: every gate of spec §4 tested with good and bad answers, including truncated ones), R4-2
(R2-CX-2 prompt truncation detection, OR-4), R4-3 (verifier gaps S1, S2, S5), R4-4 (verifier lows: duplicate
matter number refused up front, `normalize`, step comments, suite time T-11). R4-5 (R1-20) stays deferred.
Tiers: Q45 (round 4 only): Opus orchestrates, critiques and verifies; the builders and fix workers are Codex
`gpt-6.1-sol` run through the `codex exec` CLI with `-s workspace-write -c sandbox_workspace_write.network_access=true`
(the loopback stand-in server of W7 and the stage exit tests need the network flag); the plan review and the code
review are Codex `gpt-6-astra`, read-only; Fable writes and revises the brief. Privacy: every answer, page, name,
stamp and number below is invented (§6b); no Ollama runs on this Mac (Q11); the model is the stand-in
`tests/fakemodel/` in every test and probe. Revised once after the Codex plan review (§8 lists every disposition).

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
  casefold), `:13-15` `found_in`. Measured: `"ﬁ".casefold() == "fi"`, and the same for `ﬂ ﬀ ﬃ ﬄ ﬅ ﬆ` (full
  case folding maps the ligature code points), so `found_in("finding", "ﬁnding")` is already `True` today and a
  ligature is not an OCR-rung case; `found_in("examination", "exam-\nination")` is `False`. `benchscore.py:76`
  invented test `found_in(fact.quote, page.text)`, `:83` found
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
  `tests/test_runlog.py:58` asserts `reopened.schema_version == 1` and `:82-83` compares the whole answers row with
  a dict that has no cached-count column: both move with the schema. `runlog.py:37-38` `_now()` is `isoformat()`
  with microseconds, so two rows written in one second still sort by `at`; only reversed timestamps can tell an
  ordering by `at` from an ordering by `id`. A v1 file made from the `SCHEMA` text alone has 8 triggers; the
  deployed v1 file has 15 (`open_db` adds 7).
- D0.8 **Stand-in server.** `tests/fakemodel/core.py:11` `MODES` (seven); `:76-78` allowed `/api/chat` keys
  `{"model", "messages", "stream", "options", "format", "keep_alive", "tools", "think"}` (no `truncate`: a request
  carrying it gets 400 `unknown keys`); `:102-104` exact canonical lookup of the messages, 404 otherwise; `:106-124`
  mode edits (`:107-109` `truncated` halves the content AND sets `done_reason="length"`; `:111` `malformed` is
  `'{"facts": [{"page": 1,'`, no ids; `:115` `empty` is `""`, which `model.py:106-107` refuses before any gate);
  `:116` `prompt_count = chars // 4 + 8` (T-4: the stand-in's count is a stand-in, never a bound);
  `:120-124` reply keys. `model.py:111-113` lets a missing count (`None`) and an integer `0` through transport, so
  those are gate 1's to refuse. `tests/test_fakemodel.py:30`
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
  (`benchcandidate.py:39-77`). `bench.py:52-60` opens the run log before `:66-73` loads any matter or key;
  `tests/test_bench_cli.py:46` (the bad-key case) runs with `--candidate`, a path that never opens the log (`:54`).
  `tests/test_stage3_exit.py:97-99` calls `judge` with a synthetic record holding only `id`, `status`, `text`,
  `stamps`. `scripts/run_capture.py:108-109` returns the child's exit status: `/usr/bin/time -p` around a passing
  suite exits 0 whatever `real` says.
- D0.11 **Harness facts.** `tests/conftest.py:26-71` `write_config(tmp_path, **overrides)`; `tests/test_stage2_exit.py:
  51-66` starts `serve(port=0, model=FakeModel(recordings=...))` on a thread and drives `scripts/run.sh casefile
  bench` with `CASEFILE_CONFIG`; `:37-46` the in-process control swaps `benchrun.ModelClient`. `scripts/run.sh:4`
  names the toolchain by `basename "$ROOT"`, so a lane B worktree needs its own `uv sync` with the sandbox off
  (chair). Worktree `.claude/worktrees/r3-lane-b` and branches `r3/lane-b`, `control/r2-sonnet` still exist
  (HANDOFF leftovers, owner's say-so to delete).
- D0.12 Tuning entries end at T-15; owner questions end at 46 (42 to 46 answered, Q44); spec §9 ends at D30; the
  ledger's round 4 section is R4-1 to R4-5.
- D0.13 **Fixture facts the new gates lean on (measured).** `ideal.json` cites 13 of the 14 pages of 9001.001
  (every page but `DEF0001`, the defense report's cover and history page); `key.json` cites 12 (also not
  `EMP0002`). Every digit run in every `text` of `ideal.json` (31 facts) and `key.json` (29) appears in that fact's
  `quote` (0 misses). `Rules.check` over the 31 ideal quotes returns `[]`. `tests/test_benchkey.py:146` prints
  `key_refusals=N of 12`.

## §1 Decisions, with trade-offs

- **1.1 Gate 1, truncation, is four checks, none of them "tokens read equals tokens sent" (R4-2, OR-4).**
  (a) Before any call (attempt 2 included), the pipeline refuses a prompt whose token ceiling `sum(model.tokens_at_most
  (m["content"]) for m in messages) + model.TEMPLATE_TOKENS` exceeds `num_ctx - card.max_answer_tokens`, where
  `tokens_at_most(text) = len(text.encode("utf-8"))` and `TEMPLATE_TOKENS = 64` (no model call, no retry;
  #R03-V-L1). Why bytes: a byte-level BPE tokenizer (Qwen's) never emits more than one token per byte, so the byte
  count is a demonstrated upper bound for any text, digits and ligatures included; `ceil(chars / 2)` was an estimate
  (Qwen tokenizes every digit alone: `MED0001` is five tokens for seven characters) and the stand-in's `chars // 4 +
  8` (D0.8) is not evidence either way. `TEMPLATE_TOKENS` covers the chat template's structural tokens (about ten for
  Qwen's template) with margin. Cost accepted: at `num_ctx` 65536 and `max_answer_tokens` 8192 a chunk holds about
  57 000 bytes of card plus pages (roughly 12 to 25 OCR pages); T-17 lets the Studio loosen the bound only by a
  measured ratio from the run log, never by argument. (b) Every pipeline call sends `"truncate": false` (D0.2), so a
  current Ollama answers an over-long prompt with an error instead of a cut; a received non-200 whose body holds
  `context length` or `exceeds the available context` is `gate.truncation` (no retry: a retry is longer), any other
  received error is `gate.model` (retry once). An older Ollama ignores the unknown field silently (Go's JSON decoding
  drops it): (c) is the backstop for that, and the design never treats `truncate` as honoured. (c) The system
  message's first line is `prompt_id: <nonce>` (16 hex characters from `secrets.token_hex(8)`, fresh for every
  attempt) and the value appears nowhere else in the prompt: the card's one-object instruction says "the first key is
  `prompt_id` and the last key is `end_id`, both holding the value of the `prompt_id` line at the top of this
  message" without repeating it (so the stand-in's lookup, §1.10, canonicalises one line). Gate 1 inspects
  `jsonrepair.unfence(content).strip()` (a pure function; the fence itself is gate 2's `repaired` verdict): a text
  that does not begin `{` followed by optional whitespace and `"prompt_id"`, whitespace, `:`, whitespace,
  `"<nonce>"` fails `gate.truncation: prompt cut (prompt_id missing)` without retry, because an Ollama that ignores
  `truncate` cuts tokens from the front (`llama_server.go:331-332` keeps `nKeep` then the tail; `NumKeep` defaults to
  4 at `api/types.go:1226`, plus one for BOS) and cuts only when the prompt reaches `num_ctx`, down to
  `contextShiftPromptLimit`, about half the context (D0.2 `:338-347`): every cut removes at least `num_ctx / 2`
  tokens from just after the kept header, and the nonce value sits within the first dozen tokens, so every cut
  removes it; the model cannot guess 64 random bits. A text whose last key is not `end_id` with the nonce (after
  the value only whitespace, `]` and `}` may follow, since closers may be missing and repairable) fails
  `gate.truncation: answer cut (end_id missing)` with one retry, which catches a cut answer even when `done_reason`
  says `stop` and keeps gate 2's missing-closer repair from turning a cut list into a shorter valid one. Retry
  message loss cannot happen: a retry is a fresh two-message prompt (§1.3), and Ollama's chat-history truncation
  (`server/prompt.go:21-22`) always keeps the system message and the latest user message, which are the only two;
  the previous answer is not sent, so there is no old nonce to copy, and the fresh nonce was never in any earlier
  reply. (d) `done_reason == "stop"`, both counts present and positive ints (a missing count or `0` fails:
  `model.py:111-113` lets them through transport), `prompt_eval_count <= num_ctx`, `prompt_eval_count + eval_count
  <= num_ctx`, `eval_count < card.max_answer_tokens`; `prompt_eval_cached_count` is read when present and stored
  (D0.2, §1.9). The counts are evidence against the server's own claims, never proof that the pages were read: only
  (a) to (c) carry that, and each is probed alone (W4). Rejected: comparing `prompt_eval_count` with an estimate of
  tokens sent (D0.2: a cut prompt counts about half the context, a cached prompt may count less than sent on an
  older Ollama, and the estimate is a tuning value, T-4); `/api/tokenize` (not in the native API); trusting
  `truncate: false` without (c). Cost accepted: the nonce defeats Ollama's prefix cache for the card text on every
  call (a few thousand tokens re-read per call); T-16 asks the stage 9 benchmark whether the nonce should move
  behind the card once the Studio's Ollama is shown to honour `truncate: false`. The stage 2 runner gets only (b):
  `benchrun.run` sends `truncate=False` and maps the context-length error to `bench.truncation` (the recorded bench
  prompt and the stage 2 line stay as they are, D25).
- **1.2 Where the gates live and the pipeline API.** New `src/casefile/gates.py` (`Card`, `Verdict`, `Outcome`,
  `GATES = ("truncation", "repair", "schema", "quotes", "rules", "coverage")`, `messages(card, pages, nonce)`,
  `ask(card, pages, *, client, rules, log, matter, nonce=None) -> Outcome`, `open_items(log, matter)`), new
  `src/casefile/jsonrepair.py` (gate 2), new `src/casefile/schema.py` (gate 3), `quotes.py` gains the ladder
  (gate 4), `rules.py` unchanged (gate 5 calls `Rules.check`), `runlog.py` gains the coverage and gates tables
  (gate 6). `Card(name, text, schema, unit="text", think=False, max_answer_tokens=8192)` with `version` =
  `sha256(text)[:12]` (as `benchrun.card_version`). `Outcome(ok, answer, attempts, verdicts, read, uncited, failed,
  run_id)`: `answer` is the validated object with `prompt_id` and `end_id` removed and is `None` whenever `ok` is
  false (never `{}`, never an object with empty lists: "never saved as empty" in code is this invariant, the empty
  answer rule of §1.13, and the rule that the caller writes nothing when `answer is None`); `read` is every page id
  of the chunk that the validated answer cites at least once (a fact `cite` or a flag `cites` entry) when ok, else
  `()`; `uncited` is the other pages of the chunk when ok (§1.13), else `()`; `failed` is `((page_id, "gate.<name>:
  <message>"), ...)` for every page of the chunk when not ok. "Validated" means exactly: within budget, ids and
  counts sound, JSON after punctuation repair, schema-valid, every `cite` and `cites` entry a page of the chunk,
  every quote on its page by the ladder, every digit run of a fact's `text` present in its `quote`, no firm-rule
  error in our words, and at least one fact or flag. Nothing else about a `text` or `about` is verified (owner
  question 48). Messages: system = `prompt_id: <nonce>\n` + card text (whose one-object instruction names both ids
  without repeating the value, §1.1(c)); user = `Matter <number>\n` + (on a retry only) `Retry: <reason>\n` +
  `benchrun.page_block` per page (rules and card first, page text last, spec §5). Rejected: putting the gates in
  `model.py` (transport must stay dumb: #R02-V-F1 class fixes were all transport-local); a gate per module with a
  registry (six modules for one fixed order is ceremony; the order is a tuple in one place).
- **1.3 Retry once, in code and in the log.** Attempt 1 runs the six gates in order and stops at the first failure.
  If that failure is retryable (`gate.model` received, `gate.truncation: done_reason=length`, `counts` or `end_id
  missing`, `gate.repair`, `gate.schema`, `gate.quotes`, `gate.rules`, `gate.coverage: empty answer`), attempt 2 is
  a fresh two-message prompt: the same system message with a fresh nonce, and the same user message with one line
  inserted after `Matter <number>`: `Retry: the previous answer failed the <gate> check: <message>. Answer again with
  one JSON object and nothing else.` (gate messages are one line, so the retry line is one line). The previous
  answer is not sent back. Why: with two messages Ollama's history truncation can drop nothing (§1.1(c)), the fresh
  nonce cannot be copied from an earlier reply, and the error shown is what spec §4 asks for ("retried once with the
  error shown"); the model re-reads the pages at temperature 0.1 with the fault named, which is the only kind of
  retry whose input the gates can vouch for. Attempt 2 runs the budget check again on its own messages (about 150
  bytes longer): over budget is `gate.truncation: over budget` with no call. Not retried: the budget refusal, the
  server's context-length error, `prompt_id missing` (all prompt-side: a longer retry cannot pass), and a
  `ModelError` with `received=False` (raised out of `ask`: the caller decides, as bench exit 2 does under Q26). Run
  log per `ask`: one `runs` row (`job` from the caller, `card`, `card_version`, `pages_in`, `prompt_sha256` of
  attempt 1's messages); one `answers` row per received reply (status `ok` only for the attempt that passed every
  gate); one `failures` row per failed gate per attempt (`gate.<name>`); one `gates` row per gate reached per
  attempt (`verdict` pass, fail or repaired, with the message); after the last attempt, one `coverage` row per
  page: `read` or `uncited` when ok (§1.13), else `failed` with `gate.<name>: <message>`. The budget refusal still
  opens a run (so the refusal is logged) with a `failures` row and coverage `failed`, and no `answers` row.
- **1.4 Gate 2, JSON repair, is punctuation only, and only after both ids were seen.** `jsonrepair.repair(text,
  *, nonce) -> Repaired(text, repairs)`: (1) a leading and trailing Markdown fence (```` ```json ```` or ```` ``` ````)
  and surrounding whitespace are removed; (2) raw control characters U+0000 to U+001F inside strings become one
  space (`\n`, `\r`, `\t` included: they are invalid inside a JSON string); (3) a comma directly before `]` or `}`
  (outside strings) is removed; (4) when the text ends after the `end_id` value with fewer closers than the open
  stack needs, the missing `]` and `}` are appended; when the text ends anywhere else with closers missing (no
  `end_id` at the tail), `repair` raises `RepairError("closers missing and end_id not last")` and nothing is
  appended. Each applied kind is one `repaired` verdict (`gate.repair: fence`, `control`, `trailing-comma`,
  `closers`). Still rejected (gate 2 fails): a missing comma between items, single-quoted strings, unquoted keys, an
  unterminated string (no closer repair can close a string quote), a second object or any text after the closers,
  `NaN`, comments. Order with gate 1: `unfence` is a pure function; gate 1 reads the ids from the unfenced text, gate
  2 then runs `repair` on the raw text and logs `fence` as a `repaired` verdict, so a fenced good answer passes gate 1
  and is repaired at gate 2. Rejected alternative: a permissive parser (json5 or a "fix anything" loop): it would
  hide the model's errors from the benchmark (pillar 6) and invent structure (pillar 1).
- **1.5 Gate 3 uses a stdlib subset validator, not the `jsonschema` package.** `schema.load(path)` accepts
  exactly the keywords in use (D0.9): `type` (one of object, array, string, integer, number, boolean, null),
  `properties`, `required`, `additionalProperties` (must be `false`), `items`, `enum`, `title`, `$schema`, and
  refuses any other keyword, any other `type`, `additionalProperties: true` or an object, and `required` names not in
  `properties` (`SchemaError`, fail closed: a schema the validator cannot enforce is not a schema). Keys under
  `properties` are names, never keywords (D0.9). `schema.validate(instance, schema) -> list[str]` reports every
  error with a path (`facts[0].text: missing required key`, `flags[1].kind: not one of conflict, gap`, `facts[0]:
  unknown key page`). The validator also enforces the stage 4 cite rule: any object holding a `quote` key must hold
  a `cite` string (the pair gate 4 checks). Empty `facts` and `flags` arrays are schema-valid: the schema describes
  shape; whether an empty answer counts is gate 6's rule (§1.13), not a `minItems` keyword. Why not `jsonschema`: it brings `jsonschema-specifications`,
  `referencing`, `rpds-py` (a compiled wheel) and `attrs`, needs `uv add` with the sandbox off, and would accept
  keywords (`$ref`, `oneOf`, `pattern`) that nobody here has tested against a model answer; the subset is under 120
  lines and every keyword has a red test. D6's "reuse, do not rebuild" names Docling, ocrmypdf, LangExtract,
  Presidio and docuchat; a validator for six keywords is not in that class. If stage 6's card schemas need more
  keywords, that round decides again with the benchmark in hand.
- **1.6 Gate 4, the quote ladder.** `quotes.match(quote, page_text) -> Match(rung, text) | None`, rungs tried in
  order and the first hit returned: `exact` (the quote as written is a substring of the page); `whitespace` (both
  collapsed to single spaces); `curly` (then curly to straight quotes and casefold: this is today's `normalize`;
  casefold already folds the ligatures `ﬁ ﬂ ﬀ ﬃ ﬄ ﬅ ﬆ` to letters, D0.5, so a ligature matches here and the OCR
  rung does not need its own ligature table); `ocr` (then, on both sides, a hyphen followed by a line break joined
  (`exam-\nination` to `examination`), and on the page side only two kinds of line are dropped before collapsing,
  exactly Q44's two: a line that is one stamp token alone (`stamps.find` with the default pattern finds one token and
  the line holds nothing else) and a `Page N of M` line (`^page \d+ of \d+$` after strip, case-insensitive). Nothing
  else is dropped: not a bare `Page N`, not a firm name, not `CONFIDENTIAL`, not a date line, and there is no
  caller-supplied list of running lines (Q44 is binding; a wider rule would let a quote span omitted text, and a
  hook for caller lines could drop a negation if the caller misclassified it). Near-misses each rung must reject
  (tests): one changed digit (`7/10` to `8/10`); a dropped word; a dropped `no`; a quote that skips an ordinary line
  of the page; a quote that skips a bare `Page 2` line; `MED0001` inside the quote when the page shows `MED0002`.
  `found_in` keeps its meaning (rungs 1 to 3) for `benchkey.py:84`, `doctor.py:191`, the stage 3 tests and the
  fixture tests. `quotes.fold(text)` is the full folding (normalize plus the hyphen join; no line dropping, which
  needs a page) and `quotes.same(a, b)` = `fold(a) == fold(b)` is the new "same quote" test. Rejected: a similarity
  ratio (R03-PC-2: closeness cannot see one wrong digit); fuzzy matching marked unverified (spec §5 names that for
  LangExtract only).
- **1.7 What changes in the bench (D25's "the quote match is replaced by the §4 ladder at stage 4").**
  `benchscore.py:76` invented test becomes `quotes.match(fact.quote, page.text) is None`; `:83` found test becomes
  `k.cite == cite and quotes.same(k.quote, fact.quote)`; a new detail line `  rungs: exact=E whitespace=W curly=C
  ocr=O` is printed only when W + C + O > 0. The loader moves with the scorer (R02-CX-5: a key must never hold two
  facts the scorer cannot tell apart): `benchkey.py:87` refuses a repeated `(cite, quotes.fold(quote))`, which is
  wider than today's `(cite, normalize(quote))` by exactly the hyphen join, so a page holding both `exam-\nination`
  and `examination` cannot carry two key facts that `quotes.same` would merge. On the shipped fixtures nothing
  changes (prototype in the header: every ideal, flawed and key quote matches at `exact`, the two invented flawed
  quotes match at no rung; no key pair collides under `fold`), so the two baseline lines, `test_bench_detail.py:17-22`
  and `test_stage2_exit.py:18-19` stay as they are; the regression set pins this with a new case per rung on the
  small invented pages of `tests/test_benchscore.py:19-25`. The stage 2 runner's guards stay (D25: replaced at
  stage 5); the gate pipeline is used by the stage 4 exit test only.
- **1.8 Gate 5, firm rules on outputs only.** `rules.check(value, unit=card.unit, stamped=every page in the chunk
  has a stamp)` runs over every string value in the answer except values under the keys `quote`, `cite`, `cites`,
  `prompt_id`, `end_id`: a quote is the record's own words (a defense report may say "IME"; Q16 bans the label in
  what we write, never in what we read) and the cite is a stamp. Any `error` finding fails `gate.rules` with
  `<rule-id>: <excerpt>` per finding (retry once); `warning` findings go in the pass message. Spec §4 rule 5's
  "with a warning when records are not stamped" is the pipeline's own: when any page of the chunk has no stamp, gate
  5 passes with the message `warning: no Bates stamp on <page ids>; cites are page ids` (and `Rules.check` runs with
  `stamped=False`, so a bracketed cite in our words is a `warning` finding too). Why the pipeline and not the rule:
  `rules.py:75-78` makes a cite finding only where a bracketed `[cite ...]` form appears (`rules.toml:56`), and an
  extraction answer holds no bracketed cites, so the rule alone would warn about nothing on an unstamped chunk. Q44
  answered question 43: a verbatim record quote is exempt; firm rules check our words only.
- **1.9 Gate 6, the coverage ledger, is two tables in the run log (schema v2).** `coverage(id, run_id, matter,
  page_id, card, status IN ('read','uncited','failed'), reason, at)` and `gates(id, run_id, attempt, gate, verdict
  IN ('pass','fail','repaired'), message, at)`, both append-only by the same triggers; `answers` gains
  `prompt_eval_cached_count INTEGER` (nullable). `RunLog.record_coverage`, `record_gate`, `coverage(matter) ->
  {(page_id, card): (status, reason, run_id)}` (latest row wins by `id`, never by `at`), `open_items(matter)` = the
  pairs whose latest status is not `read`. `open_db` upgrades a v1 file by running the module tuple `UPGRADE_V1_V2`
  (SQL statements, in this order: `DROP TRIGGER schema_meta_no_update`, create the two tables and their update and
  delete triggers, `ALTER TABLE answers ADD COLUMN prompt_eval_cached_count INTEGER`, `UPDATE schema_meta SET
  value='2' WHERE key='schema_version'`) inside one explicit `BEGIN` ... `COMMIT` (SQLite DDL is transactional);
  any exception rolls back and the file is the complete v1 file it was (15 triggers, every row, version 1); the
  existing trigger loop then recreates `schema_meta_no_update` and adds the two `no_replace` triggers. Trigger
  count 15 -> 21 (`doctor.py:79`, `test_runlog.py:26`, `test_fix_cycle2.py:159` change together); any version other
  than 1 or 2 is refused. Rejected: a per-matter `coverage.jsonl` under `pages/` (intake publishes
  that folder once by rename and refuses re-intake, D27; a mutable ledger does not belong in it; and §8b
  `matter_status` reads counts the run log already indexes by matter); a v1 schema with `IF NOT EXISTS` tables and no
  version bump (dishonest versioning; D15 names the version).
- **1.10 Stand-in modes added (D18 amended), ten:** `cut_prompt` (the recorded answer with `__PROMPT_ID__`
  replaced by `unknown`, `prompt_eval_count = ctx // 2 + 3`: an old Ollama that cut the prompt), `prompt_too_long`
  (400 `{"error": "the prompt is longer than the context length currently available to the model; shorten the
  prompt, adjust the context length in settings, or use a model with a longer context length"}` whatever `truncate`
  says), `cut_answer` (the content cut at its half, `done_reason: "stop"`: a server that lies), `repairable` (the
  recorded JSON with a comma before the closing `]` of `facts`, one raw tab inside the first `text` value, a
  ```` ```json ```` fence, and the final `}` dropped: both ids survive every edit), `unrepairable` (the recorded JSON
  with the comma between `facts[0]` and `facts[1]` removed: both ids present, so gate 1 passes and gate 2 fails;
  stage 2's `malformed` content has no ids and would fail gate 1, so it is not a stage 4 case), `bad_schema`
  (facts[0] loses `text`), `bad_quote` (four edits, one per gate 4 branch: facts[0]'s quote with its first digit
  incremented; facts[1]'s cite set to `MED0099`; facts[2]'s `text` with its first digit run changed to a run not in
  its quote; flags[0]'s `cites` gains `MED0098`; gate 4 checks everything and names every fault in one message, so
  this one mode proves all four branches, `faults=4`), `forbidden_json` (facts[0].text = `"The IME found no
  injury."`), `empty_answer` (`{"prompt_id": "<nonce>", "facts": [], "flags": [], "end_id": "<nonce>"}`), `retry_ok`
  (a request without a `Retry:` line gets the `unrepairable` content; a request with one gets the recorded answer).
  Plus three behaviours in every mode: the allowed `/api/chat` keys gain `truncate`; the lookup is symmetric: the
  stand-in canonicalises a request by replacing, in each message, a first line matching `^prompt_id: [0-9a-f]{16}$`
  with `prompt_id: __PROMPT_ID__` and by removing, from the user message, a second line matching `^Retry: .*$`
  (remembered as the retry flag), then looks the canonical messages up; the recording is built from
  `gates.messages(card, pages, "__PROMPT_ID__")` so its first system line is literally `prompt_id: __PROMPT_ID__`
  (the regex leaves it alone) and the two sides agree; the answer text has `__PROMPT_ID__` replaced by the request's
  nonce (so one recording serves every nonce and every attempt). The card text holds the nonce once (§1.1(c)), so
  one line is the whole substitution; a card whose own text held a `prompt_id:` line would not be touched (only the
  first line is). `MODES` becomes 17.
- **1.11 Carried lows.** Bench pre-pass: `bench.main` loads every root's matter and key, refuses a duplicate number
  (`bench: duplicate matter number N in A and B`, exit 2) and any loader error before the run log is opened
  (today `bench.py:52-60` opens it first, D0.10) and before any model call; `test_bench_multi.py:63` changes to
  `seen == []` plus the direct assertion `not (config.paths.state / "runlog.sqlite").exists()` after exit 2 (the
  `seen` list alone proves only that the runner was not called; the file is the side effect R03-V-L1 forbids). The
  late refusal was pinned (R03-PC-3 class).
  `stamps.normalize` strips every character that is not a letter or digit (`re.sub(r"[^A-Za-z0-9]", "", raw).upper()`;
  Q40, Q42: a stamp is letters plus digits); `stamps.compile(pattern)` builds the four-clause pattern and
  `config.py:124` validates through it. Step comments listed in D0.10 are removed, nothing else in those lines.
- **1.12 Stage 5 boundary.** Stage 4 ends at `Outcome`: the validated answer object, the coverage rows and
  `open_items`. Not this round: chunking pages into prompts, reading intake's `pages/<binder>/*.json` into
  `matter.Page` objects, merging into the case file, the memo, `casefile status`, the job runner, the stage 5
  replacement of `benchrun`, cards from the playbook (stage 6) and the `cards/` and `schemas/` rewrite (spec §7).
  `ask` takes `Sequence[matter.Page]` so stage 5 feeds it chunks. No caller-supplied running lines (Q44, §1.6).
- **1.13 Gate 4 checks every reference and the text's numbers; gate 6 gives every page its own disposition.**
  Gate 4, over the validated object: every fact `cite` and every entry of every flag `cites` must be a page of the
  chunk (`stamps.normalize(cite) in page.stamps or cite == page.page_id`), else `gate.quotes: cite <X> is not a page
  of this chunk (pages searched: ...)`; every fact `quote` must match its page by the ladder; and every digit run
  (`\d+`) in a fact's `text` must appear as a digit run in that fact's `quote`, else `gate.quotes: text number <N>
  not in quote` (pillar 1: a number the quote does not carry is an inference or an error; `Pain was 0/10` against a
  quote of `7/10` is caught, D0.13 shows the fixtures pass). All faults are collected and named in one message
  (retry once). What is still not verified about a `text` or `about` is its words: a paraphrase with the right
  numbers and the wrong sense passes. Interim, fail closed: no output of this round or the next uses `text` as a
  verified statement; the memo stage shows the quote as the verified thing and carries `text` as the model's own
  reading until owner question 48 is answered. Gate 6, per page: an answer with no facts and no flags fails
  `gate.coverage: empty answer` (retry once; then `failed`, `answer is None`, nothing saved: pillar 2, "nothing is
  saved empty"); when the answer passes, a page the answer cites at least once is `read`, and a page it never cites
  is `uncited` (`reason: no fact or flag cites <page>`), listed as an open item exactly like a failed page, never
  counted as read, no retry (the answer is valid and is saved; the page's standing is the open question). Why not
  "every page of a passing chunk is read": the gates can verify a cited page's quotes but cannot verify an absence,
  and a page with no cite looks the same whether it is a blank cover sheet or a page the model skipped (Codex finding
  6). On the shipped matter the ideal answer cites 13 of 14 pages (D0.13), so the good case reads 13 and leaves
  `DEF0001` uncited; that is the honest state of the benchmark, not a defect. Owner question 47 asks whether a
  per-page "nothing relevant" claim by the model should ever count as read; interim: never.

## §2 Work items, in build order

Every CHECK runs through `scripts/run.sh`; every seed is applied to a copy, confirmed with `cmp`, run, and
restored (`cmp` identical) before the pass counts (Q6, HANDOFF).

### W0 (chair-run builder in the main tree, before the lanes split): quote ladder and the stand-in's shared edits
- Files: `src/casefile/quotes.py` (`Match`, `match`, `same`, `fold` helpers; `found_in` unchanged), `tests/test_quotes.py`
  (a `LADDER` table), `tests/fakemodel/core.py:76-78` (`truncate` added to the allowed keys), `:11` and `:106-124`
  (mode `prompt_too_long` only; the other nine modes are W4), `tests/test_fakemodel.py` (one case for the key and
  one for the mode).
- Ships: `ladder_ok=14 of 14` over the cases, each asserting the rung name: exact hit; whitespace hit (`7/10   in
  the\nlow back`); curly hit; casefold hit; ligature hit (`ﬁnding` on the page, `finding` in the quote: rung
  `curly`, since casefold folds it, D0.5); hyphen line break hit (`exam-\nination`: rung `ocr`); stamp line dropped
  (quote spans a line `MED0001` alone: `ocr`); `Page 2 of 5` line dropped (`ocr`); rejects (`None`): one changed
  digit, a dropped `no`, a dropped word, a skipped ordinary line (`Harrowgate Clinic` between two quoted lines), a
  skipped bare `Page 2` line (Q44: not one of the two dropped kinds), an empty quote. `same("Today’s exam",
  "today's   exam") is True`; `same("exam-\nination", "examination") is True`; `same("7/10", "8/10") is False`.
  `fake_truncate_key=1 prompt_too_long_status=400`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_quotes.py tests/test_fakemodel.py` prints `ladder_ok=14 of 14` and
  `quotes_ok=8 of 8` (the old table still passes) and passes.
- Seeds, each alone: (a) the `ocr` rung's line-drop applies to every line, not only the two Q44 kinds -> the
  "skipped ordinary line" reject case passes wrongly, `ladder_ok=13 of 14`; (b) the digit case compared after
  `casefold` of digits (`re.sub(r"\d", "0", ...)`) -> `13 of 14`; (c) `truncate` left out of the allowed keys ->
  `fake_truncate_key=0`; (d) the page-line regex loosened to `^page \d+` -> the bare `Page 2` reject case passes
  wrongly, `13 of 14`.
- Librarian pre-flight: #R03-PC-2 (one changed digit and a dropped `no` must fail), #R03-CX-5 (a token inside a
  longer token: the stamp-line rule drops whole lines only), #R01-OC-M2 (no silent default: no `running` parameter
  exists, so nothing can be dropped by a caller's say-so), #R03-PC-3 (the ligature premise was run against the
  interpreter: it folds at rung 3).

### W1 (lane A): model client, `truncate: false`, counts and the budget (R4-2 client side)
- Files: `src/casefile/model.py:36-42` (`Answer` gains `prompt_eval_cached_count: int | None`), `:97-117` (`chat(self,
  messages, *, options=None, think=None, truncate=None)`: `think` and `truncate` are added to the body only when not
  `None`, so the doctor's and the bench's bodies are byte-identical to today; `prompt_eval_cached_count` typed like
  the other counts at `:111-113`), new module constant `TEMPLATE_TOKENS = 64`, `tokens_at_most(text) -> int` (the
  UTF-8 byte count, §1.1(a)), `context_length_error(message) -> bool` (case-insensitive `context length` or `exceeds
  the available context`), `src/casefile/benchrun.py:68` (`truncate=False`), `:69-75` (a received `ModelError` whose message passes
  `context_length_error` is logged under `bench.truncation`, the rest stays `bench.model`), `tests/test_model.py`,
  `tests/test_benchrun.py` (a `prompt_too_long` case appended to `test_benchrun_modes`: the gate list at `:116` gains
  a seventh entry `bench.truncation`, the printed `benchrun_modes=8 of 8`), `tests/test_bench_cli.py`.
- Ships: `chat_body_keys=1` (the doctor body is exactly `{"model","messages","stream","options"}`; a pipeline body
  adds `think` and `truncate`), `cached_count_read=1` (`prompt_eval_cached_count: 7` lands in `Answer`; `"x"` is a
  `ModelError`), `tokens_at_most("")=0`, `tokens_at_most("abc")=3`, `tokens_at_most("ﬁ")=3`,
  `tokens_at_most("’")=3` (bytes, not characters), `TEMPLATE_TOKENS=64`, `benchrun_modes=8 of 8`, bench on
  `prompt_too_long` prints `bench 9001.001 failure bench.truncation: status=400: ...` then the `found=0 of 29 ...
  pages_failed=14 of 14` line, exit 1.
- CHECK: `scripts/run.sh pytest -q -s tests/test_model.py tests/test_benchrun.py tests/test_bench_cli.py` prints
  `chat_body_keys=1 cached_count_read=1 benchrun_modes=8 of 8` and passes.
- Seeds, each alone: (a) `truncate` always sent -> the doctor body test red (`chat_body_keys=0`); (b)
  `context_length_error` returns False -> the new benchrun case logs `bench.model`, gate list red; (c) `tokens_at_most`
  counts characters -> `tokens_at_most("ﬁ")=1`, red; (d) the cached count accepted as any type -> the `"x"` case
  red.
- Librarian pre-flight: #R01-CX-5 and #R01-CX-10 (every answer path reads the counts; each guard has a probe where
  only it is wrong), #R02-V-F1 (the 400 reply is stored as a failed row, which the existing path does), #R02-CH-1
  (zero and boundary values tested: `tokens_at_most("")`).

### W2 (lane A): `jsonrepair.py` and `schema.py` (gates 2 and 3)
- Files: new `src/casefile/jsonrepair.py` (`Repaired(text, repairs)`, `RepairError`, `unfence(text)`, `repair(text, *,
  nonce)`; a small state machine over the text that knows when it is inside a string and tracks the open stack),
  new `src/casefile/schema.py` (`SchemaError`, `load(path) -> dict`, `check_schema(schema)`, `validate(instance,
  schema) -> list[str]`), new `schemas/bench_extract.schema.json` (object with `facts` of `{cite, quote, text}` and
  `flags` of `{kind enum conflict|gap, cites array of string, about}`, `additionalProperties: false` everywhere,
  `title: bench_extract`), new `tests/test_jsonrepair.py`, `tests/test_schema.py`.
- Ships: `repair_ok=13 of 13`: fence removed (and `unfence` alone returns the inner text unchanged otherwise);
  control char in a string to a space; trailing comma before `}`; trailing comma before `]`; missing `]}` appended
  after `"end_id": "<nonce>"`; all four at once; and seven rejects: missing comma between items, single quotes,
  unquoted key, unterminated string (closed strings are a precondition of every repair), text after the closers, a
  comma before `]` inside a string left alone (the string is unchanged and the text parses as is), closers missing
  where the text ends after a fact object and no `end_id` is at the tail (`RepairError`, §1.4). `schema_ok=14 of
  14`: every keyword accepted once and violated once (type, properties, required, additionalProperties, items,
  enum), the cite rule (a `quote` without `cite`), a property named `type` (D0.9), and refusals at load: `$ref`,
  `oneOf`, `pattern`, `additionalProperties: true`, `type: ["string","null"]`, a `required` name not in
  `properties`; plus the note that `{"facts": [], "flags": []}` is schema-valid (one assertion inside the table's
  `type` accept case, so the count stays 14). `schemas_loaded=20 of 20` (the 19 existing files plus `bench_extract`
  load without error).
- CHECK: `scripts/run.sh pytest -q -s tests/test_jsonrepair.py tests/test_schema.py` prints `repair_ok=13 of 13
  schema_ok=14 of 14 schemas_loaded=20 of 20` and passes.
- Seeds, each alone: (a) the closer repair runs without checking that `end_id` was the last key -> the "closers
  missing, no end_id" reject case gets `]}` appended and parses as a shorter valid object, `repair_ok=12 of 13`
  (the unterminated-string case cannot play this part: no closer closes a string quote); (b) trailing-comma removal
  applied inside strings -> the last case changes the string, red; (c) `validate` treats keys under `properties`
  as keywords -> the `type` property case red; (d) `check_schema` ignores unknown keywords -> the `$ref` refusal
  case red; (e) `required` not enforced -> red.
- Librarian pre-flight: #R02-CX-5 (a loader refuses what the checker cannot tell apart: unknown keywords), #R01-OC-M2
  (no silent default: `additionalProperties` absent is an error, not "true"), #R03-PC-2 (one changed character is
  a difference).

### W3 (lane A): run log schema v2 (gate 6 storage, D15 amended)
- Files: `src/casefile/runlog.py:8-34` (`SCHEMA` v2 for a new file: five tables plus `coverage` and `gates`,
  `answers.prompt_eval_cached_count`), `:67-75` (`record_answer(..., prompt_eval_cached_count=None)`), new
  `record_gate`, `record_coverage`, `coverage`, `open_items`, `:105-133` (`open_db`: v1 upgrade by the module
  tuple `UPGRADE_V1_V2` in one explicit transaction as §1.9; `schema_version` 2 required after it),
  `src/casefile/doctor.py:79` (`version == 2 and count == 21`, `schema={version} triggers={count}`),
  `tests/test_runlog.py:26` (`== 21`), `:58` (`reopened.schema_version == 2`), `:82-83` (the answers row dict gains
  `prompt_eval_cached_count=None`), `tests/test_fix_cycle2.py:159` (`schema=2 triggers=21`), `tests/test_doctor.py`
  (grep finds no `schema=1` text today; nothing to change there), new tests in `tests/test_runlog.py`.
- Ships: `triggers=21`, `blocked_writes=12 of 12` (update and delete on six tables), `upgrade_v1=1` (a v1 file made
  in the test from the committed v1 `SCHEMA` text and the seven trigger statements of the v1 `open_db` loop, both
  kept in the test as strings, asserted `schema_version == 1` and 15 triggers before the upgrade, with one row in
  each of `runs`, `answers`, `failures`, `approvals`: after `open_db` every row is intact, version 2, 21 triggers,
  and the second open changes nothing), `upgrade_atomic=1` (`runlog.UPGRADE_V1_V2` monkeypatched to hold `INSERT
  INTO no_such_table VALUES (1)` after its second statement: `open_db` raises `sqlite3.Error`, and the file then
  still has version 1, exactly 15 triggers, no `coverage` or `gates` table, no new column, and every row; a later
  unpatched `open_db` upgrades it cleanly), `coverage_latest=1` (`runlog._now` monkeypatched so the first coverage
  row for a page carries a LATER timestamp than the second: the second wins, which proves the order is by `id` and
  not by `at`), `coverage_statuses=3 of 3` (`read`, `uncited`, `failed` accepted; `done` refused by the CHECK
  constraint), `open_items=2 of 3` (one page read then failed, one read then uncited, one read: the first two are
  open), `version_3_refused=1`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_runlog.py tests/test_doctor.py tests/test_fix_cycle2.py
  tests/test_stage1_exit.py` prints `triggers=21 blocked_writes=12 of 12 upgrade_v1=1 upgrade_atomic=1
  coverage_latest=1 coverage_statuses=3 of 3 open_items=2 of 3` and `exit=0 verdicts=8 fails=set() test_jobs=1`,
  and passes.
- Seeds, each alone: (a) the upgrade forgets the coverage triggers -> `triggers=19`, red; (b) `coverage()` orders by
  `at` instead of `id` -> with the reversed timestamps the first row wins, `coverage_latest=0`; (c) each upgrade
  statement runs in its own autocommit (no `BEGIN`) -> after the injected failure the file holds the two new tables
  and no `schema_meta_no_update` trigger, `upgrade_atomic=0`; (d) `open_db` accepts version 3 -> red; (e)
  `open_items` returns only `failed` -> `open_items=1 of 3`, red.
- Librarian pre-flight: #R01-CX-3 (append-only: `INSERT OR REPLACE` refused on the new tables with recursive
  triggers off, one parametrised case each), #R01-V-B2 (the refused-version branch has its own test), #R01-OC-M7 (the
  upgrade never creates a file that did not exist: `open_db` already creates the parent, nothing more).

### W4 (lane A): `gates.py`, the stand-in's nine modes and recording, pipeline unit tests
- Files: new `src/casefile/gates.py` (§1.2, §1.3, §1.13; gate order and the retry rule in one function `ask`;
  `GATE_NAMES` used by the run log rows; `_rules_strings(obj)` skipping the five keys of §1.8; the reference lookup
  over the chunk for every `cite` and `cites` entry: `stamps.normalize(cite) in page.stamps or cite ==
  page.page_id`; the digit-run check of §1.13; the per-page `read` or `uncited` disposition), `tests/fakemodel/
  core.py:11` (`MODES` to 17), `:102-104` (the symmetric canonical lookup of §1.10: nonce line, `Retry:` line,
  `__PROMPT_ID__` substitution), `:106-124` (the nine modes of §1.10 other than `prompt_too_long`),
  `tests/fakemodel/bench.py:10-15` (`recordings_for` returns two rows: the stage 2 bench row as today and a
  `gates-<number>` row built from `gates.messages(card, pages, "__PROMPT_ID__")` with the answer `{"prompt_id":
  "__PROMPT_ID__", ...ideal.json..., "end_id": "__PROMPT_ID__"}` written with `prompt_id` first and `end_id` last),
  `tests/test_fakemodel.py` (the mode list; the canonical lookup: a live nonce and a `Retry:` line both find the
  recording; `retry_ok` answers by the flag), new `tests/test_gates.py` (in process through `FakeTransport(model,
  edit=None)`, where `edit` is a function applied to the reply dict so a single field can be wrong; one invented
  small matter of three pages plus the 9001.001 matter).
- Ships: `gate_cases=27 of 27`: good answer (`ok`, 13 `read`, `uncited == ("DEF0001",)`, answers rows 1 ok, gates
  rows 6 pass); budget refusal (a card with `max_answer_tokens = 65536 - 10`, no request made, `failed` 14, failures
  `gate.truncation: over budget`); `prompt_too_long` (one request, no retry, `gate.truncation`); `cut_prompt` (no
  retry, `prompt_id missing`); `truncated` (retry, both attempts `done_reason=length`, `failed` 14, two answers rows
  both `failed`, `answer is None`); `cut_answer` (`end_id missing`, retry); `length_only` (the whole recorded content
  with `done_reason` edited to `length`: fails on `done_reason` alone, retry); `prompt_eval_count` edited to `None`
  (fails `counts` alone); `eval_count` edited to `0` (fails alone); `prompt_eval_count` edited to `num_ctx - 5` and
  `eval_count` to `10` (each within its own bound, the sum over: fails on the sum alone); `eval_count` edited to
  `max_answer_tokens` (fails alone); `repairable` (ok after four `repaired` rows including `fence`, `answer ==
  ideal`); `unrepairable` (fail twice, `gate.repair`, the second request has two messages, a fresh `prompt_id` and
  a user message whose second line starts `Retry: the previous answer failed the repair check`); `bad_schema`
  (`gate.schema`); `bad_quote` (`gate.quotes`, one message naming the pages searched and all four faults: the quote
  on `MED0001`, the cite `MED0099`, the text number, the flag cite `MED0098`); a fact cite not in the chunk alone
  (the payload patched in the test as `test_benchrun.py:15-26` does); a text digit run not in its quote alone; a
  flag `cites` entry not in the chunk alone; `forbidden_json` (`gate.rules: no-dme-ime`); a quote holding `IME` on a
  page that holds it passes gate 5; an unstamped three-page chunk passes with the pass message `warning: no Bates
  stamp on probe/001, probe/002, probe/003; cites are page ids`; `empty_answer` (`gate.coverage: empty answer`,
  retry, `failed` 14, `answer is None`); `retry_ok` (attempt 1 fails repair, attempt 2 ok, `attempts=2`, 13 `read`,
  answers rows failed then ok); a retry over budget (a card sized so attempt 1 fits and attempt 2's longer prompt
  does not: one request, `gate.truncation: over budget` on attempt 2, no second request); `received=False` raises
  `ModelError` with no run log row after the run row; `open_items` after `unrepairable` then `retry_ok` on 9001.001
  is exactly `{("DEF0001", "bench_extract")}` (latest wins; the uncited page stays open); the request body carries
  `"truncate": false` and `"think": false` and options `num_predict`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_gates.py tests/test_fakemodel.py` prints `gate_cases=27 of 27
  modes_ok=6 of 6` and passes.
- Seeds, each alone: (a) the `end_id` check dropped -> `cut_answer` passes gate 1 and fails later or passes:
  `gate_cases=26 of 27`; (b) `prompt_id missing` made retryable -> the request count in the `cut_prompt` case is 2,
  red; (c) gate 5 run over `quote` values too -> the "quote holding IME" case red; (d) `Outcome.answer = {}` on
  failure -> the `answer is None` assertion red; (e) gate order swapped (rules before quotes) -> the `bad_quote` case
  reports `gate.quotes` still but the gates rows differ, red on the rows list; (f) coverage written before the retry
  instead of after -> `open_items` case red; (g) the `done_reason` guard dropped -> `length_only` passes, red (and
  `truncated` stays red on `end_id`, which is why `length_only` exists); (h) a missing count accepted -> the `None`
  case red; (i) the sum ceiling dropped -> the `num_ctx - 5` case red; (j) every page of a passing chunk marked
  `read` -> the good case's `uncited` assertion red; (k) an empty answer passed through -> `empty_answer` case red;
  (l) the digit-run check dropped -> the text-number case red and `bad_quote` names three faults, red.
- Librarian pre-flight: #R01-CX-10 (each gate 1 check has a probe where only it is wrong: cut_prompt, cut_answer,
  length_only, the four count probes, prompt_too_long, budget), #R03-V-L1 (the budget refusal happens before the first
  side effect other than the run row), #R02-V-F1 (every received reply is an answers row, attempt 2 included),
  #R01-OC-M2 (`Card.unit` has a default only because `text` is the spec's unit for every stage 4 and 5 card; the
  stage 6 question cards must set it, noted in the docstring), #R03-OC-L1 (a failure message names the gate, the
  pages searched and what to do).

### W5 (lane B, worktree): bench on the ladder, bench pre-pass, benchrun gate map, `normalize`, comments (R4-2 bench, R4-4)
- Files: `src/casefile/benchscore.py:76, :83` (§1.7), `:50-63` (the `rungs` detail line; `Score` gains `rungs:
  tuple[tuple[str,int],...]`), `src/casefile/benchkey.py:87` (the collision pair becomes `(cite,
  quotes.fold(quote))`, §1.7; the message `same cite and quote as fact F<n>` unchanged), `src/casefile/bench.py:
  52-79` (pre-pass: a list of `(root, matter, key)` built before the run log opens, which moves below it; the
  duplicate check in that loop), `:21-122` (comments removed), `src/casefile/benchcandidate.py:39-77` (comments
  removed), `src/casefile/stamps.py:14` (`normalize`), new `compile(pattern)` used by `:23` and
  `src/casefile/config.py:124`, `tests/test_benchscore.py` (one case per rung: a page with `exam-\nination` and a
  candidate quote `examination` is found, not invented (the hyphen join is the one rung `found_in` lacks, D0.5); a
  whitespace variant of a key quote is `found`; a changed digit is still `invented`), `tests/test_benchkey.py:103-146`
  (case 13 appended to `test_key_refusals`: a page holding both `exam-\nination` and `examination`, two key facts on
  that cite with those two quotes -> `fact F2: same cite and quote as fact F1`; the printed line becomes
  `key_refusals=13 of 13`), `tests/test_bench_detail.py` (the `rungs` line appears for the hyphen case and not for
  the shipped fixtures), `tests/test_bench_multi.py:46-65` (`seen == []` and `not (state / "runlog.sqlite").exists()`
  where `state` is `write_config`'s `tmp_path / "state"`; a bad key in root `b` refuses before root `a` runs: `seen
  == []`, the same file assertion, exit 2), `tests/test_stamps.py` (`normalize("MED.0001") == "MED0001"`,
  `normalize("med_0001") == "MED0001"`), `tests/test_config.py` (the stamp pattern error path still exits 2).
- Ships: `score_cases=14 of 14` (eleven today plus three rung cases), `key_refusals=13 of 13`, the baseline lines
  unchanged (`found=29 of 29 ... flags=9 of 9 ...` exit 0; `found=26 of 29 missed=3 invented=2 ... flags=8 of 9
  ...` exit 1, same six detail lines, no `rungs` line), `duplicate_numbers_exit=2` with `seen == []` and no run log
  file, `stamps_cases=8 of 8`, grep `"# (Load|Find|Check|Main|Process|Return|Score|Final)"` over `bench.py` and
  `benchcandidate.py` -> 0 lines.
- CHECK: `scripts/run.sh pytest -q -s tests/test_benchscore.py tests/test_benchkey.py tests/test_bench_detail.py
  tests/test_bench_multi.py tests/test_stamps.py tests/test_config.py` prints `score_cases=14 of 14
  key_refusals=13 of 13 duplicate_numbers_exit=2 stamps_cases=8 of 8` and passes; `scripts/run.sh casefile bench
  --config config.example.toml --matters tests/fixtures/matters --candidate tests/fixtures/bench/flawed.json` prints
  the baseline line and exits 1.
- Seeds, each alone: (a) `benchscore.py:76` back to `found_in` -> the hyphen case counts `invented=1`, red; (b)
  the `rungs` line printed always -> `test_bench_detail` red on the shipped fixture; (c) the duplicate check moved
  back after the run -> `seen == ["a"]`, red; (d) `normalize` strips `[ -.]` only -> the `med_0001` case red; (e)
  `config.py` keeps its own wrapper -> the new config test, which monkeypatches `stamps.compile` to raise
  `re.error("probe")` and expects `ConfigError ... not a valid pattern: probe`, gets no error, red; (f) only
  `open_db` moved back above the pre-pass, the checks themselves still first -> `seen == []` stays green and the
  file assertion goes red (the file assertion is the control that `seen` is not); (g) `benchkey.py:87` kept on
  `normalize` -> case 13 loads without error, `key_refusals=12 of 13`, red.
- Librarian pre-flight: #R03-V-L1 (refusal before the first side effect: no run log open, no model call, asserted on
  the file), #R03-PC-3 (the test that pinned the old order is named and changed), #R02-CX-5 (collisions refused up
  front, by the same folding the scorer uses), #R03-CX-5 (`normalize` and the whole-token rule stay separate:
  finding is unchanged).

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
  `intake.intake`; assertions unchanged, `code == 1` now the command's code), `tests/test_stage3_exit.py:97-98` (the
  synthetic record of `test_changed_digit_fails_must_contain_while_ratio_stays_high` gains `"matter": "9002.001"`
  and `"page": 1`, so the changed `judge` does not raise `KeyError` before its oracle runs), new
  `scripts/suite_time.sh` (runs `/usr/bin/time -p scripts/run.sh pytest -q` N times, default 3, parses each `real`,
  prints one line per run `suite_time run=<i> real=<seconds> budget=<B> verdict=PASS|FAIL`, then `suite_time
  runs=<N> max=<seconds> verdict=PASS|FAIL`, and exits 1 when any run has no `real` line (`real=missing`, FAIL), any
  run fails pytest, or any `real` is at or over the budget; the budget is `SUITE_BUDGET`, default 90; the command
  under test is `SUITE_CMD` when set, so the script's own verdict can be seeded), `docs/loop/tuning-questions.md`
  (T-11 measurement appended at close by the chair, not by the lane).
- Ships: `ids_ok=6 of 6` still, `intake_refusals=16 of 16`, `check page 5 differs`, `suite_time runs=3 max=<under
  90> verdict=PASS` exit 0 with nothing else running, and real OCR runs in the suite 5 -> 4 (one intake of the
  fixture through the real command, shared by the two tests; three doctor smokes: both stage 1 exit tests and
  `test_ocr_real_tools`).
- CHECK: `scripts/run.sh pytest -q -s tests/test_stage3_exit.py tests/test_intake.py tests/test_scanned_fixture.py`
  prints `stage3 exit=1 pages=6 ids_ok=6 of 6 ...` and `intake_refusals=16 of 16` and passes; `scripts/suite_time.sh`
  prints three `verdict=PASS` run lines and the summary `verdict=PASS`, exit 0 (the verdict is in the exit status,
  not in a number someone reads: `run_capture.py:108` returns the child's status, so `/usr/bin/time` alone never
  fails, D0.10).
- Seeds, each alone (the verifier's own, restored by `cmp`): (a) `intake.py:306` `PageRecord(number,` ->
  `PageRecord(source.stem,` -> `ids_ok=0 of 6`, red; (b) `intake.py:85` `!=` -> `<` -> the `7 of 6` case red; (c)
  `make_scanned.py` `if a != b` -> `if a[0] != b[0]` -> `check page 5 differs` absent, red; (d) the session fixture
  skipping intake when the folder exists from an earlier session (a cache keyed on a path outside `tmp_path_factory`)
  -> `production_dirs_untouched` or the fixture's own `assert not root.exists()` red; (e) `SUITE_BUDGET=1
  scripts/suite_time.sh 1` -> `verdict=FAIL`, exit 1; (f) `SUITE_CMD=true scripts/suite_time.sh 1` (no `real` line)
  -> `real=missing verdict=FAIL`, exit 1; (g) the synthetic record left without `matter` -> the changed-digit test
  raises `KeyError`, red.
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
  `stage4 gate=quotes good=pass bad=1 of 1 faults=4 truncated=0 of 4 reached`
  `stage4 gate=rules good=2 of 2 bad=1 of 1 truncated=0 of 4 reached warning=1`
  `stage4 gate=coverage good=13 read 1 uncited bad=14 failed empty=14 failed truncated=0 of 4 reached open_items=14 then 1`
  `stage4 exit=0 gates=6 of 6 cases=14 of 14 runs=+14 answers=+21 empty_saved=0 server_stopped=1`
  where good = the `replay` mode passes the gate (for rules, also the three-page probe below; for coverage, 13
  `read` rows and one `uncited` row for `DEF0001`, D0.13, §1.13); bad = the gate's own bad mode fails at that gate
  (truncation: `cut_prompt`, `prompt_too_long`; repair: `unrepairable`; schema: `bad_schema`; quotes: `bad_quote`,
  whose one message names all four faults, `faults=4`; rules: `forbidden_json`; coverage: the `unrepairable`
  outcome's 14 `failed` rows, and `empty=14 failed` is the `empty_answer` case's rows with reason `gate.coverage:
  empty answer`); truncated = the four truncated cases (`truncated`, `cut_answer`, `cut_prompt`, `prompt_too_long`)
  all fail at gate 1, and `0 of 4 reached` says none reached a later gate (read from the `gates` rows); `retry=1` is
  the `retry_ok` case; `open_items=14 then 1` is `open_items("9001.001")` read twice: after `empty_answer`, the last
  failing case on that matter (14 pairs), then after the final `replay` run (one pair, `DEF0001`): the case order
  on 9001.001 is fixed as budget, cut_prompt, prompt_too_long, truncated, cut_answer, repairable, unrepairable,
  bad_schema, bad_quote, forbidden_json, retry_ok, empty_answer, replay, with the probe matter's case anywhere;
  `empty_saved` counts outcomes with `ok` false and `answer is not None`, outcomes with `ok` true whose answer has
  no facts and no flags, and answers rows with status `ok` for a failed attempt (must be 0); `runs` and `answers`
  are deltas in the run log. The three-page probe is an invented unstamped matter built in the test (clinic
  `Harrowgate Occupational Clinic`, pages `probe/001` to `probe/003`, no stamp on any page, page 2 holding the
  sentence `The IME report of 03/02/2026 notes a normal gait.`) with a recording row added to the server's rows
  whose answer holds three facts, one per page, the page 2 fact quoting that sentence with the text `The report
  notes a normal gait.` and citing `probe/002`: it passes gate 5 (the quote is exempt) with the pipeline's unstamped
  warning in the pass message (§1.8), `warning=1`, and all three pages `read`. The `answers` delta is fixed by the
  case list: replay 1, budget 0, cut_prompt 1, prompt_too_long 1, truncated 2, cut_answer 2, repairable 1,
  unrepairable 2, bad_schema 2, bad_quote 2, forbidden_json 2, retry_ok 2, empty_answer 2, probe 1 = 21 over 14
  runs (the budget refusal makes a run row and no answer row).
- CHECK: `scripts/run.sh pytest -q -s tests/test_stage4_exit.py` prints the seven lines above with `stage4 exit=0`
  and passes; the test asserts every number on those lines and exits non-zero (pytest failure) on any miss.
- Seeds, each alone: (a) `gates.py` end_id check dropped -> `truncated=3 of 4` and `cut_answer` reaches gate 2,
  `reached=1`, red; (b) coverage `read` written when gate 5 warns -> unchanged (a warning passes: this seed must stay
  green, and the brief says so to stop a builder from "fixing" it); (c) coverage rows written on attempt 1's failure
  before the retry -> `open_items` after `retry_ok` is 14 and the final reading is not 1, red; (d) `Outcome(ok=False,
  answer={"facts": [], "flags": []})` -> `empty_saved=1`, red; (e) gate 5 run over quotes -> the three-page probe
  fails `gate.rules: no-dme-ime` -> `good=1 of 2` on the rules line, red (the ideal answer's quotes trip no rule,
  measured: `[]` from `Rules.check` over all 31, so the probe is the only case that can catch this seed); (f) the
  empty answer passed as ok -> `empty=0 failed`, `empty_saved=1`, red; (g) every page of a passing chunk marked read
  -> `good=14 read 0 uncited` and `open_items=14 then 0`, red; (h) the unstamped warning dropped from the pass
  message -> `warning=0`, red (the cite rule alone finds nothing here, D0.6, `rules.py:75-78`).
- Librarian pre-flight: #R01-CX-11 (the assertion is on the run log rows and the outcome, with the exit code of the
  server and pytest), #R01-P-1 and round 1 process notes (the server is stopped in `finally`; `server_stopped=1`
  printed), #R02-OC-H1 (the good answer is the ideal key read against the pages, already verified in round 3).

### W8 (chair, at the close): records
- `docs/spec.md` §9 D31 to D37 (§6), §4 unchanged text plus a sentence on `prompt_id` and `end_id` under gate 1 and
  on `truncate: false` under §5's model client row, §11 stage 4 row; `docs/loop/tuning-questions.md` T-16 to T-18
  (§4); `Librarian.md` round 4 entries; ledger baselines (`gate` 0, suite count and time, the stage 4 lines).

## §3 Parallelisation map

- Builders (Q45): every work item is coded by Codex `gpt-6.1-sol` through `codex exec`, run by the chair with `-s
  workspace-write -c sandbox_workspace_write.network_access=true` (W7's loopback server and the stage exit tests
  bind a port; without the flag the socket tests fail for a reason that is not the code's); the chair reads each
  builder's report against the CHECK line before accepting it, as with any tier. Fix workers after the critic round
  are the same model. The code review (8a) is Codex `gpt-6-astra`, read-only.
- W0 first, in the main tree, by one builder, committed by the chair; both lanes start from that commit.
- Lane A (main tree): W1, W2, W3, W4, W7, in that order. Owns `src/casefile/model.py`, `benchrun.py` (lines 68 to 75
  only), `jsonrepair.py`, `schema.py`, `gates.py`, `runlog.py`, `doctor.py:79`, `schemas/bench_extract.schema.json`,
  `tests/fakemodel/core.py`, `tests/fakemodel/bench.py`, `tests/test_model.py`, `test_benchrun.py`, `test_bench_cli.py`,
  `test_jsonrepair.py`, `test_schema.py`, `test_runlog.py`, `test_doctor.py`, `test_fix_cycle2.py`, `test_fakemodel.py`,
  `test_gates.py`, `test_stage4_exit.py`.
- Lane B (worktree `.claude/worktrees/r4-lane-b`, branch `r4/lane-b`, its own `uv sync` by the chair with the
  sandbox off, D0.11; the builder's `codex exec` is started with that worktree as its working directory): W5 then
  W6. Owns `src/casefile/benchscore.py`, `benchkey.py:87`, `bench.py`, `benchcandidate.py`, `stamps.py`,
  `config.py:124`, `scripts/suite_time.sh`, `tests/conftest.py`, `tests/test_benchscore.py`, `test_benchkey.py`,
  `test_bench_detail.py`, `test_bench_multi.py`, `test_bench_discovery.py`, `test_stamps.py`, `test_config.py`,
  `test_stage3_exit.py`, `test_intake.py`, `test_scanned_fixture.py`.
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
  `16` (W6); `benchrun_modes=7 of 7` -> `8 of 8` (W1); `seen == ["a"]` -> `seen == []` plus the no-file assertion
  (W5); `key_refusals=12 of 12` -> `13 of 13` (W5); `MODES` 7 -> 17; `test_runlog.py:58` version 1 -> 2 and `:82`
  one more column (W3); `test_stage3_exit.py:97` synthetic record gains two keys (W6).
- New tables, each a `*_ok=N of N` line: ladder 14, repair 13, schema 14, gates 27, score 14, stamps 8; the stage 4
  exit test's seven lines (W7). Every line's N is fixed in §2 so a builder cannot pad or trim a table unnoticed.
  Each gate 1 guard has a case where only it is wrong (W4: `cut_prompt`, `cut_answer`, `length_only`, the four
  count edits, `prompt_too_long`, budget), so no seed is masked by a second failing guard.
- Suite time (T-11): measured 95.33 s today under load, 72.67 s at the round 3 close. W6 removes one real intake (the
  11.5 s test shares the stage 3 fixture run); the stage 4 tests add about 3 s (one loopback server, SQLite in
  `tmp_path`, no OCR). Acceptance: `scripts/suite_time.sh` (three runs, nothing else running) exits 0, which it does
  only when every run printed a `real` under 90 and passed; a missing measurement is a FAIL, not a pass. If still
  over: second lever, `test_config.py::test_matters_alias_table` (9.68 s, 19 `config show` subprocesses) runs the
  rows in process through `config.load` and keeps one subprocess row, logged as T-18; never a skip, never a marker
  left out of the default run.
- Tuning entries for the chair to append at close: T-16 the prompt nonce position (front, defeating the prefix
  cache; move behind the card once the Studio's Ollama is shown to honour `truncate: false`, measured by prompt eval
  time on the stage 9 benchmark); T-17 the byte budget (`tokens_at_most` = bytes, `TEMPLATE_TOKENS = 64`) and
  `Card.max_answer_tokens = 8192` (measure `prompt_eval_count / bytes` from the run log on the Studio over every
  stage 9 call; the budget may be loosened only to a measured worst-page ratio with margin, and the cached count
  must be added back before dividing on an Ollama that reports it); T-18 the suite's second lever above.
- The Codex plan review attacked (§8): the retry's history loss, the budget's bound, the ligature premise, the
  benchmark key equivalence, the stand-in's lookup, the malformed payload, the empty answer, the text-versus-quote gap,
  the Q44 boundary, the unstamped warning, masked guards, the fence-before-ids order, the migration tests and
  controls, the `judge` caller, the pre-pass proof and the timing verdict. Still open for the code review (8a): the
  repair state machine on escaped quotes (`\"`) and `\\` at a string end; the v1 to v2 upgrade on a file opened by
  another process (WAL); `end_id` detection when a model emits the keys in another order.

## §5 Risks, each with a measurable tripwire

- R1 The Studio's Ollama ignores `truncate: false` (older than D0.2) and cuts prompts. Tripwire: stage 9, the run
  log's `prompt_eval_count` on a 60 k-token probe prompt below 40 000 with no `gate.truncation` row; the `prompt_id`
  check is the backstop (every cut removes at least half the context from just after the kept header, §1.1(c)),
  the retry is two messages so history truncation has nothing to drop, and T-16 keeps the nonce in front until that
  probe passes. The byte budget (§1.1(a)) means a prompt that reaches the cut path at all is already a gate bug.
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
  `b`, `seen == []`, no run log file, exit 2) red when the pre-pass is removed, and W5 seed (f) (only `open_db` moved
  above the checks) red on the file assertion alone. The CLI bad-key case `test_bench_cli.py:46` runs with
  `--candidate`, which never opens the log (D0.10), so it is not a control here and is not claimed as one.
- R8 The exit test's `answers=+21` drifts when a case is added. Tripwire: the summary line's `cases=14 of 14` and the
  per-case table in the test both change together or the test is red; the chair re-derives 21 from the table.
- R9 The uncited rule (§1.13) leaves honest blank pages open forever and the memo stage inherits a backlog.
  Tripwire: the stage 9 report counts `uncited` rows per 100 pages; owner question 47 decides what, if anything, may
  close them; until then they are listed, never counted as read.

## §6 Contradictions and new spec rows (pending veto)

- **D31** (new; spec §4 and §5 model client row amended). Old text (§4): "1. Truncation: the answer did not stop
  early, and the model read as many tokens as were sent." New: "1. Truncation: the prompt was within budget before
  the call (a byte-count ceiling, `tokens_at_most`, re-checked on the retry), the call asked the server not to cut
  (`truncate: false`), the answer, after fence removal, begins with the call's `prompt_id` and ends with its
  `end_id` (a fresh nonce per attempt, present once in the prompt), and `done_reason` and the token counts are
  present and agree with the context; the counts are stored, never trusted as proof of reading." Why: D0.2 shows a
  cut prompt counts about half the context and a cached prompt may count less than sent, so the old sentence has no
  sound test; the checks of §1.1 are each probed alone. Row: the gate pipeline of §1.2 and §1.3 (`gates.py`, order,
  the retry as a fresh two-message prompt with the error shown and no history, `Outcome.answer is None` on failure,
  gate names `gate.<name>`, firm rules skip `quote`, `cite`, `cites`, `prompt_id`, `end_id`, the pipeline's own
  unstamped warning).
- **D32** (D15 amended). Run log schema v2: `coverage` (status `read`, `uncited` or `failed`) and `gates` tables,
  `answers.prompt_eval_cached_count`, v1 upgraded in place by `UPGRADE_V1_V2` in one explicit transaction that
  rolls back whole, latest coverage row by `id`, open items = not `read`, triggers 21, any other version refused
  (§1.9). Why: gate 6 needs a durable per-page ledger and §8b `matter_status` reads it; the published `pages/`
  folder is immutable by D27.
- **D33** (new). JSON repair is punctuation only, the four kinds of §1.4, each logged as `repaired`; the closer
  repair runs only when `end_id` is the last key at the tail, else `RepairError`; `unfence` is pure and gate 1 reads
  the ids from the unfenced text; everything else is `gate.repair` failure. Why: pillar 1 and 6, the cut-list hazard
  in §1.1(c), the fence-before-ids order.
- **D34** (new). Schema check by a stdlib subset validator over `type, properties, required, additionalProperties:
  false, items, enum, title, $schema`; any other keyword or value refuses the schema at load; every object with a
  `quote` key carries a `cite` string; empty arrays are schema-valid (gate 6 rules on them, D38);
  `schemas/bench_extract.schema.json` is the stage 4 card's schema. Why: §1.5. Spec §7's "stage 6 updates them"
  gains: the 19 schemas are loaded by this validator today (D0.9) and stage 6 keeps them inside the subset or
  decides again with the benchmark.
- **D35** (D25 amended, the sentence "a fact's text is not compared with its quote at stage 2 (the §4 ladder,
  stage 4)" replaced). New: "invented = cite not a page of the matter or quote matched at no rung of the §4 ladder
  (`quotes.match`); found = same cite and the same quote after the ladder's folding (`quotes.same`); the key loader
  refuses two facts equal under that folding; a `rungs:` detail line when any match used a rung other than exact;
  the ladder's OCR rung joins line-break hyphens and drops only a stamp alone on a line and a `Page N of M` line
  (owner Q44), ligatures being folded by casefold at the curly rung; a fact's text is compared with its quote at
  stage 4 by the digit-run check only (D38); the stage 2 runner's own guards stay until stage 5." Why: §1.6, §1.7,
  §1.13; the shipped numbers do not move. Spec §4 rule 4's "running headers" reads, by Q44, as those two line kinds.
- **D36** (D18 amended). Stand-in modes: the seven of D18 plus `prompt_too_long`, `cut_prompt`, `cut_answer`,
  `repairable`, `unrepairable`, `bad_schema`, `bad_quote`, `forbidden_json`, `empty_answer`, `retry_ok` (17);
  `truncate` accepted on `/api/chat`; the lookup canonicalises the nonce line and the `Retry:` line on both sides
  and substitutes `__PROMPT_ID__` in the answer. Why: §1.10, the exit test's four truncated cases.
- **D37** (D28 amended). Two roots with one matter number, or any loader error, are refused before the run log is
  opened and before any matter runs; `stamps.normalize` keeps letters and digits only; one `stamps.compile` wrapper
  for the finder and the config check. Why: R03-V-L1; Q40 and Q42 say a stamp is letters plus digits.
- **D38** (new; spec §4 rules 4 and 6 gain a sentence each). Gate 4 checks every reference: each fact `cite` and
  each flag `cites` entry is a page of the chunk, each quote is on its page by the ladder, and each digit run in a
  fact's `text` appears in its `quote`; a `text`'s words are otherwise unverified and no output treats them as
  verified until owner question 48 is answered. Gate 6: an answer with no facts and no flags fails (`empty
  answer`, retry once, nothing saved); in a passing answer a page it cites is `read` and a page it never cites is
  `uncited`, an open item never counted as read (owner question 47). Why: §1.13; pillars 1 and 2.
- No owner ruling is overridden. OR-4's sentence "Ollama does not count cached prompt tokens" is narrowed by D0.2
  (true for an Ollama whose llama-server sends no `cache_n`, false on current main); the design holds either way.
  Q44 is applied as written (§1.6); nothing beyond its two line kinds is dropped.

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

Answered 2026-10-27 (Q44): every interim kept; 44 is binding on §1.6. Added after the Codex plan review (appended
to `docs/loop/questions-for-owner.md` as 47 and 48):

47. When a chunk of pages passes every check but the model cites nothing on one of its pages (a cover sheet, a
    blank page, or a page it skipped: the code cannot tell which), that page is listed as an open item marked
    "uncited" and never counted as read. Should that stay so, or should the model's own per-page statement
    "nothing relevant on this page" close it, or should you close it by hand with your name in the log (as question
    42 asked for failed pages)? Interim: it stays open; nothing closes it.
48. The checks verify a fact's quote against the page and that every number in the fact's summary sentence appears
    in its quote; the rest of the summary's wording is the model's and is not verified. Should the memo show the
    quote as the verified text and label the summary as the model's reading, or should a second model call judge
    each summary against its quote before the memo uses it? Interim: no output of this round or the next uses a
    summary as verified; the quote is the verified thing.

## §8 Codex dispositions (plan review, `gpt-6-astra`, 16 findings; each checked in the code before ruling)

| # | Ruling | Evidence and what changed |
|---|---|---|
| 1 | ACCEPTED | Retry is a fresh two-message prompt with a fresh nonce and no history (§1.3; Ollama's history truncation keeps system and latest, the only two); nonce appears once in the prompt (§1.1(c)); ids read after `unfence`; budget is the UTF-8 byte count plus `TEMPLATE_TOKENS` (a byte-level BPE never exceeds one token per byte; `ceil(chars/2)` was an estimate, Qwen tokenizes digits singly); counts stored, never trusted (§1.1(d)); `truncate` never assumed honoured. The stand-in's `chars // 4 + 8` (`core.py:116`) was never the bound and is noted as such (D0.8). D31, R1, W1, W4 (retry-over-budget case). |
| 2 | ACCEPTED | Measured: `"ﬁ".casefold() == "fi"` and `found_in("finding", "ﬁnding")` is `True` today (D0.5). Ligatures fold at the `curly` rung; the OCR rung is the hyphen join plus Q44's two line kinds. W0's ligature case asserts rung `curly`; W5's rung case and seed (a) use `exam-\nination`. §1.6, D35. |
| 3 | ACCEPTED | `benchkey.py:87` pairs `(cite, normalize(quote))`; `benchscore.py:82-85` stops at the first key. The loader's pair becomes `(cite, quotes.fold(quote))`, with `test_benchkey.py` case 13 and W5 seed (g); `benchkey.py:87` and `test_benchkey.py` move into lane B's list. §1.7, D35. |
| 4 | ACCEPTED | `core.py:32` keys the whole canonical list and `:102-104` returns 404. The lookup is now symmetric (nonce line to `__PROMPT_ID__` on the request side, the recording built with that literal; a `Retry:` line removed and remembered); the nonce appears once in the prompt; retries are two messages, so no four-message contract is needed; `retry_ok` answers by the retry flag. §1.10, D36, W4. |
| 5 | ACCEPTED | `core.py:111` is `'{"facts": [{"page": 1,'`, no ids, so it fails gate 1 under §1.1(c). New mode `unrepairable` (both ids, the comma between two facts removed) is gate 2's bad case and `retry_ok`'s first answer; `malformed` stays stage 2's. §1.10, W4, W7 (`answers=+21`, `cases=14`). |
| 6 | ACCEPTED, with OWNER 47 | `benchcandidate.py:40-41` accepts empty lists and the proposed schema would too. Decided on pillar 2: an answer with no facts and no flags fails `gate.coverage: empty answer` (retry once, nothing saved); a page a passing answer never cites is `uncited`, an open item never counted as read (the ideal cites 13 of 14, D0.13). What may ever close an uncited page is the owner's: question 47, interim nothing. §1.13, D32, D38, W3, W4, W7, R9. |
| 7 | ACCEPTED, with OWNER 48 | `benchscore.py:76` checks the quote only and `:108-113` the prose for rule hits; the brief's gates kept that gap, and `flags[].cites` went unchecked. Now gate 4 checks every `cite` and `cites` entry against the chunk and every digit run of a fact's `text` against its quote (fixtures pass: 0 misses over 60 facts, D0.13); "validated" is defined in §1.2 as exactly what is checked. Whether the text's words need a second model call or a label is the owner's: question 48, interim no output uses `text` as verified. §1.13, D38, W4 (`bad_quote` four faults). |
| 8 | ACCEPTED | Q44 (ledger `Clarified`) allows a stamp alone on a line and `Page N of M` only. `Page N` alone and the `running` parameter are removed; a bare `Page 2` line is a reject case; `ask` has no running-lines parameter. §1.6, §1.12, W0 (seed (d)), D35. |
| 9 | ACCEPTED | `rules.py:75-78` makes a cite finding only for a bracketed cite match (`rules.toml:56`) and `stamped` sets the severity; the probe text has no bracket, so the rule path yields nothing. The warning is the pipeline's own (`warning: no Bates stamp on ...`), which is what spec §4 rule 5 says; `warning=1` counts it. §1.8, W4, W7 (seed (h)). |
| 10 | ACCEPTED | `core.py:107-109` halves the content and sets `length` together; `model.py:111-113` passes `None` and `0`. W4 gains `length_only` (whole content, `done_reason=length`) and four count edits through `FakeTransport(edit=...)`: `None`, `0`, the sum over with each part under, `eval_count == max_answer_tokens`; seeds (g) to (i). §1.1(d), W4, §4. |
| 11 | ACCEPTED | Gate 1 reads the ids from `jsonrepair.unfence(content)`; gate 2 logs the fence repair. W2 seed (a) now targets a closed-string payload that ends before `end_id` (the "closers missing, no end_id" reject case); the unterminated-string case stays a plain reject. §1.1(c), §1.4, D33, W2 (`repair_ok=13 of 13`). |
| 12 | ACCEPTED | `test_runlog.py:58` asserts `schema_version == 1`; `:82-83` compares the whole answers row with no cached-count key. Both are named in W3's file list. |
| 13 | ACCEPTED | `runlog.py:38` is `isoformat()` with microseconds; `SCHEMA` has 8 triggers and `open_db` adds 7. W3: the v1 fixture is built from the v1 `SCHEMA` text plus the seven v1 `open_db` trigger statements (15 asserted first); `coverage_latest` uses reversed timestamps through a monkeypatched `_now`; `upgrade_atomic=1` injects a failing statement into `UPGRADE_V1_V2` and asserts the complete v1 file survives; seeds (b) and (c) rewritten. §1.9, D32. |
| 14 | ACCEPTED | `test_stage3_exit.py:97-99` builds a record with `id`, `status`, `text`, `stamps` only and calls `judge`. W6 updates that record (`matter`, `page`) with seed (g). |
| 15 | ACCEPTED | `bench.py:52-60` opens the log before `:66-73` loads anything; `test_bench_cli.py:46` runs with `--candidate`, which never opens the log. W5 asserts `not (state / "runlog.sqlite").exists()` after the refusal, seed (f) moves only `open_db`; R7 drops the CLI case as a control. §1.11, D0.10. |
| 16 | ACCEPTED | `run_capture.py:108-109` returns the child's status, so `/usr/bin/time -p` around a passing suite exits 0 at any `real`. W6 adds `scripts/suite_time.sh` (parses every `real`, FAIL on missing, pytest failure or `real >= SUITE_BUDGET`, exit 1), with seeds (e) and (f); §4's acceptance is that script's exit status. |

Counts: 16 accepted (two of them with an owner question), 0 rejected, 0 owner-only. Every finding was checked
against the file and line it named (`core.py`, `model.py`, `quotes.py`, `benchkey.py`, `benchscore.py`,
`benchcandidate.py`, `rules.py`, `rules.toml`, `runlog.py`, `bench.py`, `run_capture.py` and the three tests), and
the ligature and fixture claims were run through the project interpreter (D0.5, D0.13). Decisions the review did
not touch (§1.2's module layout, §1.5's validator and its keyword set, §1.9's two tables, §1.11's `normalize` and
comments, §1.12's boundary, D37) are unchanged.
