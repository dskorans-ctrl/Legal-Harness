# Design proposal: the cloud round trip (anonymize, send to Claude or Codex, restore)

Status: proposal for the owner, 2026-10-28, written mid round 6 at the chair's request (ledger Q52). Nothing
here is canon until the owner rules and the chair moves the rulings into spec §9. Every example person,
matter and record below is invented. No real client fact was read or written in preparing this file.

The owner's request, verbatim: "I need to make sure the design has a way for me to automatically send
anonymized documents to Claude via the API key. Also need a way to send things to Codex via MCP. The
pipeline should be pretty seamless and automatic, I load documents, then select what I want done with
them (deposition prep, hearing prep, brief, etc). Then the local AI takes over, anonymizes everything,
sends it to Claude for analysis/synthesis and then Claude sends back automatically when done and Local AI
de-anonymizes it and gives me the final output."

## 0. The proposal in one paragraph

Claude becomes a second model client behind the same six gates. The engine (code) builds the task's
packet from the case file, the local model finds the names and the anchor date, code replaces them under
casefile-anon/1, the identifier check runs on the exact bytes about to leave, the approval mode chosen by
the owner is satisfied, and the anonymized pages go to `api.anthropic.com` with the same card, nonce and
schema the local model would get. The reply runs through `gates.ask` unchanged, against the anonymized
pages, so a cut answer, bad JSON, a wrong schema, a quote not on its page, a cite to a page not sent, a
firm-rule breach or an empty answer fails before any name is put back. Only a passing answer is
re-identified by code from the key that never left the matter folder, then the restore check runs it
against the real pages, and only then is the Word document rendered. Every send is a row in an
append-only sent-log with an approval id, and a kill switch stops every send with one file. Codex is
not reachable as an MCP server from the installed CLI (verified below), so "Codex via MCP" is offered in
two honest forms: `codex exec` driven by code as a read-only second-opinion critic on the same anonymized
packet (off until the owner settles OpenAI's terms), and the §8b bridge registered in Codex as an MCP
server so an interactive Codex session gets the same fixed menu Claude Code gets.

## 1. Premises checked in the code (file:line)

- The model client is a small urllib client with no proxy and no redirects (`src/casefile/model.py:84-85`,
  D21). `ModelClient.chat` (`model.py:149-174`) returns an `Answer` of `content, done_reason,
  prompt_eval_count, eval_count, prompt_eval_cached_count, raw` (`model.py:88-96`). Nothing in it is Ollama
  specific except the request body (`model.py:153-158`) and the field names. A cloud client that returns the
  same `Answer` drops into every caller.
- The gates are one function, `gates.ask(card, pages, *, client, rules, log, matter, ...)`
  (`src/casefile/gates.py:171`). It builds the prompt itself (`gates.py:176`, `messages()` at `gates.py:56-60`),
  checks the byte budget against `client.config.num_ctx` (`gates.py:197-198`), calls
  `client.chat(msgs, options=..., think=..., truncate=False)` (`gates.py:202-203`), and runs the six gates
  in order (`gates.py:215-290`). Gate 1 reads `done_reason`, both counts, `num_ctx`, `prompt_id` and `end_id`
  (`gates.py:219-231`). Gate 4 already refuses "cite X is not a page of this chunk" (`gates.py:109`) and a
  quote not on its page (`gates.py:118-123`). So "a response that cites a page not sent" is caught today
  by code that needs no change, provided the cloud reply enters through `gates.ask`.
- Chunking is by bytes against `num_ctx` with a retry margin (`src/casefile/pipeline.py:11, 35-55`); the
  memo job runs one `pipeline.run` per chunk and merges each passing answer into the case file at once
  (`src/casefile/memo_job.py:39-50`). A cloud context of 200 000 tokens would make one chunk of most matters,
  which also shrinks the cross-chunk conflict gap the owner ranked first (Q49 item 56).
- Config refuses an unknown table or key (`src/casefile/config.py:85-92`) and a model host that is not
  `http://127.0.0.1:<port>` (`config.py:129-138`). A `[cloud]` table is therefore a D13 amendment, not a
  convention.
- The run log has an `approvals` table with `decision IN ('approved','rejected','edited')` and `by_whom`
  (`src/casefile/runlog.py:19-21`) and a `record_approval` method (`runlog.py:111-116`) that no production
  code calls yet. The approval step below writes it.
- The case file's event kinds are `fact, cite, reading, flag, about, run, output` (`src/casefile/facts.py:55-63`);
  there is no event for "sent" or "approved". The proposal adds none: the sent-log lives in the run log,
  the case file records the `output` as today.
- The privacy row scans tracked and ignored files for forbidden prefixes and binary formats
  (`src/casefile/privacy.py:30-39`); it does not look for an API key. Added below.
- The stand-in is a stdlib HTTP server on 18434 (`tests/fakemodel/server.py:9`) with an in-process
  `FakeTransport` opener (`tests/fakemodel/core.py:206-224`); tests default to the closed port 9
  (HANDOFF machine rules, Librarian #R05-PC-8). The cloud stand-in copies this shape.
- `casefile` has no `depo`, `hearing`, `report` or `brief-out` command yet (`src/casefile/cli.py:37-40`);
  stage 6 (round 6) adds the first three on the local model. The 45 cards under `cards/` predate the single
  model decision (spec §7); `cards/06-brief/_brief-rules.md` already forbids an authority not in the packet.
- The §8b bridge is an MCP server the `casefile` user runs for the `claude` user's Claude Code, with six
  tools and no content reads (spec lines 160-175). It is a pull model: Claude asks for a cleared package.
  The owner's request is a push model: the engine sends. Both can stand (§3 below).

## 2. Where the request collides with canon

| Canon | The request | What this proposal does |
|---|---|---|
| Pillar 3 (spec line 17): data leaves only as "anonymized brief packages the attorney approves" | Deposition prep, hearing prep, report analysis and briefs all go out, and "automatic" may drop the approval click | P1 rewrites pillar 3: any anonymized packet, for any task in the fixed menu, that passed the identifier check and carries an approval under the mode the owner picks (§7). The approval becomes a recorded decision, not necessarily a per-package click. The key never leaves. |
| Pillar 4 (line 18): code decides the steps, the model fills one step, no agent loop, no model tools | A Claude API call fits: one request, one JSON answer, no tools. A Codex run is an agent with a shell | P2: the Claude path is a plain model client. Codex runs only as `codex exec -s read-only --ephemeral` over a folder that holds nothing but the anonymized packet, answers one schema, writes nothing the engine reads except its final JSON; it is a critic, never a source of facts. Off until the owner rules. |
| §8b: Claude Code reaches casefile only through the fixed-menu bridge under a separate macOS user | The API path has the `casefile` user's engine call Anthropic directly | P6: add beside. The bridge stays for interactive work (research, argument drafting, questions). The API path is the engine's own client, same identifier check, same sent-log, same approval table. Not routed through the bridge (the bridge gives a tool surface, which pillar 4 bars for the automatic path), not replacing it (research needs web search, a model tool, so it stays interactive). |
| Stage order (§7): outputs are stage 6 on the local model; anonymizer is stage 7 | The owner wants the outputs to come from Claude | Round 6 builds stage 6 on the local model as briefed, with two engine-neutral constraints (§13). The round trip is a new stage 7b after the anonymizer and before the web page. Nothing in the request is built in round 6. |
| D3: no legal research locally, research with Claude | A brief "sent to Claude automatically" implies research by API, which needs the `web_search` server tool | Brief by API covers the statement of facts and the argument outline with `[CITATION NEEDED]` markers (brief rule 4); research and authorities stay interactive through the bridge. Owner question 64. |

## 3. The flow

### 3.1 As the attorney sees it

Invented matter 1012.001: claimant Mara Quill, employer Harbor Crate Co., treating physician Dr. Tobin
Vance, defense examiner Dr. Selma Orr. Date of injury 02/11/2025.

1. Load. Drop the medical binder and the defense report into the matter's Inbox share or the web page.
   `casefile intake` runs; pages get IDs and stamps (stage 3). No change.
2. Pick a task. On the web page (stage 8) or over SSH: `casefile depo --matter 1012.001 --deponent
   defense-doctor --taken-by us --engine claude`. The job card shows what will run, which engine, the
   approval mode in force, the cost cap, and the Run button. Under mode A (§7) Run is the approval.
3. No further input. The job updates the memo if pages are unread (local), builds the fact packet,
   anonymizes it, runs the identifier check, records the approval, sends, gates the reply, restores,
   runs the restore check, renders the Word document, and prints the status line.
4. What comes back. `outputs/depo-defense-doctor.docx` (the two-page outline, question document, danger
   zones, points for our expert, per the deposition-prep skill), `outputs/depo-defense-doctor.cloud.md`
   (what left: packet id, byte count, model, tokens in and out, cache reads, cost, request id, time; and
   what was dropped by the restore check, by cite), and the open-items list. If anything blocks, the job
   stops and says which check, which kind of item, and what to do; nothing partial is saved.

Under mode B the job pauses at step 3 after the identifier check and shows the anonymized packet; the
attorney reads it (it is short: placeholders, relative dates, quotes) and clicks Approve or Reject; the
rest runs without input.

### 3.2 As code sees it

| # | Step | Who | Input | Output | On disk |
|---|---|---|---|---|---|
| 1 | Intake | code, OCR tools | PDF | pages with IDs and stamps | `pages/<binder>/<nnn>.json` (D27) |
| 2 | Memo update | code + local model through `gates.ask` | unread pages | facts, flags | `casefile.jsonl`, run log (D40, D32) |
| 3 | Packet build | code | task, case file, pages cited by the facts | packet: facts with quote, cite, page id; the cited pages' text; task options; playbook version | `<matter>/outbox/<packet_id>/packet.json` (real text, 600 perms, never shared) |
| 4 | Entity pass | local model through `gates.ask` with the anonymization card (round 6 writes it, R6-2) | packet text | names and the anchor date, each with a quote and cite | run log answer row |
| 5 | Replace | code, casefile-anon/1 | packet, name list, entity pass | anonymized packet, key | `outbox/<id>/anon.json` (what will leave); `<matter>/anon/key.json` (never leaves, 600) |
| 6 | Identifier check | code (plus a second local entity pass on the anonymized bytes) | anonymized packet bytes, name list, key | pass, or `blocked` with the kind and offset of each hit, never the value | run log `cloud_sends` row status `blocked` |
| 7 | Approval | attorney (mode A: at Run; mode B: here; mode C: standing) | packet id, byte count, sha256 | `approvals` row (`runlog.py:111`) | run log |
| 8 | Send | code, `CloudClient` | anonymized pages as `Page` objects (same page ids and stamps, anonymized text), card, nonce | `Answer` | `cloud_sends` row written before the request; the reply as received under `outbox/<id>/reply.json` |
| 9 | Gates 1 to 6 | code, `gates.ask` unchanged | the `Answer`, the anonymized pages | `Outcome`, coverage rows | run log gates, coverage |
| 10 | Restore | code | passing answer, key | re-identified answer | `outbox/<id>/restored.json` |
| 11 | Restore check | code | restored answer, real pages | pass, or the item dropped with a reason | run log gate `gate.restore` |
| 12 | Merge or render | code | restored answer | depo/hearing/report output (stage 6 renderer), `output` event | `outputs/*.docx`, `casefile.jsonl` |
| 13 | Optional critic | `codex exec` (if on) | the same anonymized packet plus the anonymized answer | findings with cites | `outbox/<id>/codex.json`, then steps 9 to 11 again on the findings |

Steps 4 to 6 and 10 to 11 are stage 7 (the anonymizer, Q47). Steps 7, 8, 13 and the sent-log are stage 7b.
Step 12 is stage 6. A page-based task (report analysis, the Q41 conflict excerpts) sends anonymized pages
instead of a fact packet; the table is the same with step 3 picking pages.

## 4. Anonymization out and re-identification back (casefile-anon/1, ledger Q47)

Convention as logged: fixed bracketed placeholders (`[CLAIMANT]`, `[DR-n]`, `[ATTY-n]`, `[PERSON-n]`, org
and place kinds, `[DATE D+n]`, `[MONTH M+n]`, `[YEAR Y+n]`, `[DATE-REF-n]`, `[ID-n]`, contact kinds,
`[SRC-n]`); the local model finds only names and the anchor date; code does every replacement, date
conversion, re-identification and check; fail closed both ways; line count kept for page:line cites.

**The key.** `<matters>/<number>/anon/key.json`, mode 600, owned by the `casefile` user, one per matter,
append-only (a placeholder number is never reused; a new entity gets the next number). It holds the
placeholder, the real value and the kind. It is read by the replace step and the restore step only. It is
never copied into `outbox/`, never into the run log, never into a reply, never over the bridge, never into
the Outbox share. The privacy row (`privacy.py`) gains `anon/` and `key.json` as forbidden names in the
checkout, beside `Cases/` and `Bench/`.

**The identifier check (before any byte leaves; fail closed).** On the exact bytes of `anon.json`:
1. Every value in the matter's name list and in the key (names, employer, insurer, adjuster, addresses,
   date of birth, SSN, claim and hearing numbers, phone, email, record numbers) is absent, at every rung of
   the quote ladder's folding (`quotes.fold`: casefold, straight quotes, collapsed whitespace) and as a
   whole token (#R03-CX-5: no prefix or fragment match).
2. No absolute date remains: any `M/D/YYYY`, `YYYY-MM-DD` or month-name date fails, because the convention
   makes every date relative to the injury. A Bates stamp's digits are not a date.
3. Pattern detectors: SSN, phone, email, a street number followed by a street word, ZIP, a 6 to 12 digit
   number that is not a stamp (claim or account numbers).
4. A second entity pass by the local model on the anonymized bytes returns no person, organization or
   place; a model failure here is a block, not a pass.
5. Every bracketed token in the packet is a placeholder in the key, and every key entry used appears
   only as its placeholder.
A hit at any step: the packet is not sent, the `cloud_sends` row is `blocked` with the step number, the
kind and the byte offset (never the value), the job exits 1 and names the step and the remedy ("add the
item to the name list", "the entity pass found a name on page MED0012; add it or reject"). Nothing is
saved as sent.

**Restore (after the gates pass).** Code replaces placeholders from the key; dates come back as
M/D/YYYY from the anchor date. Then the restore check, logged as `gate.restore`:
1. No bracketed placeholder-shaped token remains. A placeholder not in the key (Claude wrote `[DR-9]` and
   the key stops at `[DR-4]`) fails that fact or finding; it is dropped with the reason "unknown
   placeholder [DR-9]" and listed as an open item.
2. Every quote in the restored answer is found on its real page by the ladder (`quotes.match`). A quote
   that matched the anonymized page but not the real one (a placeholder sat inside a token) fails that item.
3. Every cite still resolves to a page of the packet (gate 4 over again, on real pages).
4. The firm rules run again on the restored words (a restored name cannot create a breach, but the check is
   cheap and the rule is "every output").
5. The page:line count of each quoted page is unchanged by the round trip.
A failure drops the item, never the run; the output says what was dropped and why. If every item fails,
the output is not written (pillar 2) and the job exits 1.

**What is not an identifier.** Bates stamps and page ids are the shared language (§8b) and stay. The
matter number stays. Medical terms, body parts, diagnoses, medication names, dollar amounts and
restrictions stay; they are the content. Provider and facility names are identifiers (`[DR-n]`,
`[ORG-n]`). Owner question 63 asks about the edge cases (the hearing number, the carrier).

## 5. The Claude API path

**Key storage.** The `casefile` user's login Keychain, item service `casefile.anthropic`, added once by
the owner over Screen Sharing with `security add-generic-password -a casefile -s casefile.anthropic -w`
(interactive prompt; the key is never on a command line, in shell history, in `config.toml`, in the repo
or in the run log). The engine reads it at job start with `security find-generic-password -s
casefile.anthropic -w`, holds it in memory for the job, sends it only as the `x-api-key` header, and never
logs headers. `config.toml` gets `[cloud].keychain_item = "casefile.anthropic"`. For tests and the loop,
`[cloud].key_source = "file:<path>"` is allowed only when `[cloud].host` is loopback (the stand-in).
The privacy row scans every tracked and ignored file for the `sk-ant-` prefix; a hit is a red gate.
`casefile doctor` gains a row `cloud`: PASS when `[cloud].enabled` is false ("off"), or when the Keychain
item exists and `GET https://api.anthropic.com/v1/models` answers 200 (no content sent); FAIL otherwise.

**Model.** `claude-opus-5-5` by default (owner question 62). Reasons from the docs read today
(`platform.claude.com/docs/en/manage-claude/api-and-data-retention`): Claude Fable 5.1 and Claude Fable 5
are Covered Models that "require 30-day data retention and are not available under ZDR unless expressly
authorized by Anthropic"; Opus 5.5 carries no such requirement, so a zero data retention arrangement stays
possible. Price (pricing page, read today): Opus 5.5 $4 per million input tokens, $20 output, cache write
$5 (5 minute) or $8 (1 hour), cache read $0.20. Sonnet 5.5 is $2 / $10 with $0.10 cache reads and is the
measured fallback if the benchmark says the outputs hold (pillar 6). One model per run; no `fallbacks`
parameter (a fallback would route the packet to a second model the owner did not pick).

**Request shape** (`POST /v1/messages`, raw HTTPS through the same urllib opener as `model.py`, no proxy,
no redirects, so the stand-in pattern and D21 carry over; the SDK is not added as a dependency):
- `model`, `max_tokens` (card's `max_answer_tokens`, default 16 000; the §4 truncation gate treats
  `stop_reason: max_tokens` as "stopped before it finished"), `system` as a list with the card text and the
  firm rules block carrying `cache_control: {type: ephemeral}`, `messages` with one user turn holding the
  page blocks (same `=== PAGE ... BATES ... ===` encoding as `extract.page_block`, `extract.py:34-35`) as a
  text block with `cache_control`, then a final text block `prompt_id: <nonce>`.
- `output_config: {format: {type: json_schema, schema: <card schema>}, effort: "high"}`. The schema is a
  fixed file under `schemas/` with no client data (the retention page says schemas are cached up to 24
  hours and must hold no PHI; ours never do). Gate 3 still runs; structured output is belt, the gate is
  braces.
- No `thinking` parameter (adaptive is the default and cannot be disabled on this model), no
  `temperature` (a 400 on the current API version), no tools, no prefill.
- Headers: `x-api-key`, `anthropic-version`, `content-type: application/json`.
- The nonce moves from the first line of the system prompt (`gates.py:58`) to the last block of the user
  turn so the cached prefix survives the retry and a second card over the same pages. `gates.ask` still
  builds `messages()` as today; `CloudClient.chat` re-splits them (strip the `prompt_id:` line from the
  system text, append it as the final block). The ids the gates check are in the answer, unchanged.

**Mapping the reply to `Answer`** so `gates.ask` runs unchanged: `content` = the text blocks joined;
`done_reason` = `"stop"` when `stop_reason == "end_turn"`, `"length"` for `max_tokens`, `"refusal"` for
`refusal` (gate 1 fails it: "stopped before it finished (done_reason=refusal)", and the client marks it
not retryable); `prompt_eval_count` = `usage.input_tokens + cache_read_input_tokens +
cache_creation_input_tokens`; `eval_count` = `usage.output_tokens`; `prompt_eval_cached_count` =
`cache_read_input_tokens`; `raw` = the whole body. `client.config.num_ctx` for the cloud client is
`[cloud].context_tokens` (default 200 000), so the byte budget (`gates.py:197`) and the count check
(`gates.py:224`) keep working; bytes over-count tokens for English text, so the budget is conservative.

**Size and chunking.** `pipeline.chunk` with the cloud `num_ctx`. One chunk for most matters. A page too
long for one prompt is refused as today (`pipeline.py:40-47`). Per call cap `[cloud].max_input_bytes`
(default 600 000) regardless of context, so a runaway binder cannot send a megabyte by accident.

**Retries and timeouts.** Transport: `[cloud].timeout_s` (default 600, the SDK's own default). 429 and
5xx: retry with backoff (1 s, 4 s, 16 s), at most 3, honouring `retry-after`; connection errors the same;
400, 401, 403, 404: no retry, the job stops with the status and the error type (never the body verbatim
into an output; the body goes to the run log as a received reply, D25 rule). Each attempt is a fresh
nonce. The gate pipeline's own one retry (a fresh prompt with the error shown, §4) stays on top.

**Cost cap.** Before each call: estimate = `bytes_in / 3` tokens at the input price plus `max_tokens`
at the output price (an upper bound). The call is refused when the run's running total plus the estimate
exceeds `[cloud].cost_cap_usd_per_run` (default 10) or the day's total from `cloud_sends` plus the
estimate exceeds `[cloud].cost_cap_usd_per_day` (default 50). After each call the row records the real
usage and cost. A refused chunk is an open item with the reason "cost cap". Worked size: an invented
300 page matter at about 2.5 KB a page is 750 KB, about 200 000 tokens: about $0.80 in and, at 20 000
output tokens, $0.40 out, so about $1.20 a pass on Opus 5.5 before caching.

**Prompt caching.** The system block (card plus rules, over the 512 token minimum once the playbook text
is in) and the pages block carry `cache_control`. The 5 minute entry covers the retry and a second card
over the same pages in one job (deposition outline then questions). Tripwire: `cache_read_input_tokens`
is stored per answer (the column exists, D32) and the `.cloud.md` summary prints it; zero on the second
call of a job is a logged warning. Measured on the Studio at stage 9, not argued.

**Batches.** Not used. The Batches API is "No" for both ZDR and HIPAA on the eligibility table read today
(29 day retention), and a 24 hour window does not fit a job the attorney is waiting on.

**Commercial terms and retention: what must be true of the account.**
- The key belongs to a Claude Console organization (API, commercial terms), not a consumer plan. The
  privacy page read today: "By default, we will not use your inputs or outputs from our commercial
  products" to train models.
- Default retention on the API: inputs and outputs "deleted ... within 30 days of receipt or generation";
  flagged content up to 2 years. Zero data retention: "contact the Anthropic sales team"; "enabled per
  organization". With ZDR, the Messages API, prompt caching, structured outputs (qualified: only the schema
  is cached), thinking and token counting are eligible; batches and code execution are not.
- HIPAA readiness exists as a separate arrangement (a BAA accepted in the Console, permanent once on).
  Whether the firm needs it for workers' compensation medical records is a legal call for the owner.
- Unverifiable from here, so owner questions 59 and 62: which organization, whether ZDR has been granted
  for it, whether a BAA is wanted, and the model choice that follows. Interim: `[cloud].enabled = false`
  and a required `[cloud].terms_confirmed = "<date>"` line that the owner writes after reading the terms;
  the doctor prints the date.

## 6. Codex via MCP

**What is verifiable.** The installed Codex CLI is 0.159.2. `codex --help` lists `mcp` (manage external
MCP servers for Codex: `add`, `list`, `get`, `remove`, `login`, `logout`), `exec`, `app-server`
(experimental, JSON-RPC) and `exec-server`; there is no `mcp-server` subcommand, the binary holds no such
string, and OpenAI's current MCP page for Codex documents only external servers that Codex calls. So
"send things to Codex via MCP" cannot mean "casefile is an MCP client of a Codex MCP server" with this
CLI. Two forms remain, both honest:

1. **Automatic critic through `codex exec`.** `codex exec -C <scratch> -s read-only --ephemeral
   --ignore-user-config --output-schema <schema> -o <answer.json> -m <model> < prompt`, where `<scratch>`
   is a fresh folder holding only `anon.json` and the anonymized answer, created for the call and removed
   after, and `--ephemeral` keeps the session out of `~/.codex` (tripwire R8 greps for the nonce after the
   run). The schema is a findings list: each finding has a cite, a quote and one sentence; the findings go
   through steps 9 to 11 of §3.2 like any answer and are rendered as a "Second review" section, never
   merged as facts. Why Codex rather than Claude for this: an output reviewed by a second model family is
   the loop's own critic pattern (ledger Q46, the adversarial review skills); the value is independence,
   not capability. Which tasks: the deposition cross outline and the hearing outline (where a missed
   danger zone costs most); never the memo, never a fact source. Pillar 4: `codex exec` is an agent with a
   shell; the read-only sandbox over a folder that holds only what Claude already saw bounds it. This is
   the one exception P2 names, and it is off by default.
2. **Interactive Codex as a bridge client.** Under the `claude` macOS user, `codex mcp add casefile --url
   http://127.0.0.1:<bridge port>` with the bridge token gives a Codex session the same six fixed tools §8b
   gives Claude Code, nothing more; every reply passes the identifier check in the bridge; every call is
   logged. No new code beyond stage 8b; one line in the setup guide.

**Terms.** OpenAI's enterprise privacy page could not be fetched from this session (HTTP 403). Whether
Codex runs on an API key or a ChatGPT login, under which plan, with which retention and training terms,
is owner question 61. Interim: `[cloud].codex = false`; nothing goes to Codex.

## 7. The approval question

| Option | What the attorney does | Failure mode | Guard |
|---|---|---|---|
| A. Approve once per task, at selection | Run is the approval for every packet the job builds | A packet the attorney never read goes out; a missed identifier rides along | The identifier check and the second entity pass; a packet whose entity pass found a name not in the name list halts for a per-package approval regardless of mode; the first packet of each matter always halts (it proves the name list) |
| B. Approve each outbound packet | The job pauses, shows the anonymized packet, the attorney approves or rejects | Friction turns into rubber-stamping; a headless Studio needs the CLI (`casefile approve <packet>`) until the web page exists | The packet view is short and placeholder-only; the approval row records the sha256 the attorney saw, and a changed packet needs a new approval |
| C. Fully automatic with a sent-log and a kill switch | Sets `[cloud].approval = "standing"` once; reads the sent-log | Pillar 3 is kept only by code; a bug or a bad name list sends every matter's packets until someone looks | Kill switch file, per-run and per-day cost caps, the halts of option A, a daily sent-log mail or status line |

In every mode: the kill switch (`<state>/cloud.off`, written by `casefile cloud off`, checked before every
send, reported by the doctor), the sent-log (run log v3 table `cloud_sends`, append-only), the per-run
and per-day cost caps, the `approvals` row per packet (`by_whom` is the web login or the SSH user, the
`item` is the packet sha256), and the Firewalla egress rule as the out-of-band switch (owner question 69).

**Recommendation: A, with the two halts.** A fact packet for deposition or hearing prep is built from
gated facts and quotes, carries placeholders and relative dates only, and is the same kind of thing every
time; a click per packet adds no information the attorney does not already have from the job card. The
two halts (first packet of a matter; any new entity) are where a human read changes the outcome. Keep B
for brief packets (spec §2 already requires approval and download there, and a brief packet carries
narrative) and as the standing interim until the owner rules (owner question 60). C is not recommended.

## 8. The fixed workflow menu

Practice rules come from the firm's skills (`deposition-prep`, `workers-comp-hearing-prep`,
`motion-brief-memo-drafting`), read for rules only.

| Task | Local (never leaves) | Goes out (anonymized, gated, restored) | Practice rules enforced by code |
|---|---|---|---|
| Memo (`memo`) | everything: extraction, merge, memo | nothing | firm rules on the memo's words (D41) |
| Deposition prep, our doctor (`depo --deponent our-doctor`) | memo update, fact packet, entity pass, replace, checks, render | outline and question document | treatment and bills as two separate questions, the second anchored on the bill memo by name (skill §1); never one compound question (rule 5, `unit=question`); Bates cite on every record fact |
| Deposition prep, defense doctor (`--deponent defense-doctor`) | same | outline, cross questions, danger zones, points for our expert | the nine tests of skill §2 as card text; forbidden defense-work questions are firm rule 5 (hired, retained, fees, exam volume); short leading questions, one fact each, a cite each; a danger-zone section is required by the schema |
| Deposition prep, client or witness | same | outline and questions | cites; no medical inference (pillar 1) |
| Transcript designation | memo update, packet from the transcript pages | designation guide | page:line cites; the two propositions of skill §1 checked and flagged at the top if missing |
| Hearing prep (`hearing --outline --client --doctor --closing`) | same; the attorney's billing memo is never sent (Q37, owner question 67) | outline sections, client prep, doctor prep, closing | the billing memo item first on the checklist, flagged, with the itemized totals the attorney supplied; which stamp to cite is asked (Q35); page:line for deposition facts |
| Report analysis (`report --defense` or `--ours`) | pages chosen, entity pass, replace, checks | the report pages plus the record pages around each conflict (Q41) | "the report", never DME or IME (rule 5); conflicts flagged, never resolved (pillar 5) |
| Brief package (`brief-out`) | packet build, replace, checks, mode B approval, download | statement of facts and argument outline with `[CITATION NEEDED]` markers | brief rules 1 to 7 (`cards/06-brief/_brief-rules.md`); chronological facts, one fact one sentence one cite; no em dashes; research stays interactive (owner question 64) |
| Brief re-import (`brief-in`) | restore, fact check against the case file, Word | nothing | every factual sentence re-checked by quote and cite |
| Second review (Codex) | packet reuse | the packet and the anonymized answer | findings only, same gates, never merged |

Every output heads with the work-product line, caption, hearing number, date of accident and the dates
the skills list; the caption and hearing number are restored by code from the key, never sent.

## 9. Testability in the loop (invented fixtures only)

- `tests/fakecloud/`: a stdlib HTTP server on 18435 speaking `POST /v1/messages` and
  `/v1/messages/count_tokens`, plus an in-process `FakeTransport`, in the shape of `tests/fakemodel/`.
  Modes: `replay` (recorded invented answers keyed by the canonical prompt), `max_tokens`, `refusal`,
  `rate_limited` (429 twice with `retry-after`, then ok), `server_error`, `malformed`, `bad_schema`,
  `bad_cite` (cites a page not sent), `bad_quote`, `unknown_placeholder` (answer holds `[DR-9]`),
  `absolute_date` (answer holds `03/04/2025`), `slow` (past the timeout), `cache_hit` (reports
  `cache_read_input_tokens`), `empty`. Every mode is reached by one test and each gate's test proves red on
  its seed before the pass counts (Q6).
- `tests/fakecodex/codex`: an executable on a test PATH that honours `exec --output-schema -o`, writes a
  recorded findings file, and records its argv so a test can assert `-s read-only`, `--ephemeral` and the
  scratch folder's contents (only `anon.json` and the anonymized answer).
- A session-wide socket guard in `tests/conftest.py`: any `connect` to a non-loopback address raises;
  one test proves the guard by attempting a public address and asserting the refusal. Tests default to
  `http://127.0.0.1:9` for the cloud host, as for the model (#R05-PC-8).
- Seeded leaks: a fixture packet for the invented matter 9001.001 with 20 planted identifiers of 8 kinds
  (name, employer, DOB, SSN, phone, email, address, claim number, absolute date) must be blocked at step 6
  with the stand-in's request counter unchanged at 0; the log row holds the kind and offset and not the
  value (a test greps the run log for each planted value).
- Restore seeds: a reply with a placeholder not in the key; a reply whose quote matches the anonymized
  page only; a reply citing an unsent page; each drops exactly that item and the output says so.
- Kill switch and caps: with `cloud.off` present, every task in the menu makes 0 requests; with a cap of
  $0.01 the first call is refused with "cost cap" and 0 requests reach the stand-in.
- Key hygiene: the privacy row goes red on a planted `sk-ant-` string in an ignored file; a test asserts no
  request header appears in any run log column.
- Exit test (stage 7b): `stage7b exit=0 packets=4 of 4 blocked_seeded=20 of 20 sent=4 gated=4 of 4
  restored=4 of 4 dropped_seeded=3 of 3 killswitch_requests=0 cap_requests=0 real_endpoint_requests=0
  cache_read_reported=1 server_stopped=1`. Stage 7's own exit test (the identifier check on the test matter,
  re-import fact-checks a draft) stays as written in §7.
- Benchmark (pillar 6): `casefile bench --engine cloud` scores the invented matter through the stand-in
  in replay mode so the gates' numbers are comparable between engines; on the Studio the owner runs the
  same line against the real endpoint with the benchmark matters (closed, invented keys) and the
  round report records tokens and cost per matter.

## 10. Proposed spec changes (draft §9 rows; the chair assigns D numbers)

P1. (§1 pillar 3 amended). Old: "Client data never leaves the Studio, except anonymized brief packages the
attorney approves." New: "Client data never leaves the Studio, except an anonymized packet for a task on
the fixed menu that passed the identifier check on the bytes sent, carries a recorded approval under the
mode in force (§9 Dnn), and is logged in the sent-log; the re-identification key never leaves the matter
folder." Roadmap: stage 7b.

P2. (§1 pillar 4 gains a sentence). New: "A cloud model called by code with a fixed card, a fixed schema
and no tools is the model filling one step. Codex runs only as a read-only, ephemeral second review over an
anonymized packet, never as a source of facts; it is off until the owner enables it." Roadmap: stage 7b.

P3. (§2 gains a paragraph after "Brief and motion package"). New: "Cloud round trip. Any task on the menu
may run its synthesis step on Claude by API instead of the local model: the engine builds the packet,
anonymizes it (casefile-anon/1), checks it, records the approval, sends it, runs the six gates on the reply
against the anonymized pages, restores it from the key, runs the restore check against the real pages, and
renders the output. Commands: `--engine local|claude`, `cloud on|off`, `cloud log`, `approve <packet>`."
Roadmap: stage 7b.

P4. (§3 gains step 7). New: "7. A task that goes out: packet, entity pass, replace, identifier check,
approval, send, gates, restore, restore check, render. A failure at any check stops before the next step;
blocked and dropped items are listed, never saved as sent or read." Roadmap: stages 7 and 7b.

P5. (§4 gains a closing sentence). New: "The gates run on every model answer, local or cloud, before
re-identification; a cloud reply is mapped to the local answer shape (`end_turn` is `stop`; `max_tokens`
and `refusal` fail gate 1, `refusal` without retry). After re-identification the restore check runs
(`gate.restore`): no unknown placeholder, every quote on its real page by the ladder, every cite a page of
the packet, firm rules again, line counts unchanged." Roadmap: stage 7b.

P6. (§5 three new rows). "Cloud client | raw HTTPS to `https://api.anthropic.com/v1/messages` through the
same opener as the model client (no proxy, no redirects), key from the `casefile` user's Keychain, model
`claude-opus-5-5` unless the benchmark says otherwise, structured output with the card's schema,
`cache_control` on card and pages, no tools, no thinking parameter, no temperature; per-run and per-day
cost caps; kill switch file". "Sent-log | run log schema v3: `cloud_sends` (packet sha256, bytes, provider,
model, approval id, status blocked/sent/failed, tokens, cache reads, cost, request id), append-only;
`approvals` written per packet". "Cloud stand-in | `tests/fakecloud/` on 18435 and `tests/fakecodex/`, the
modes of §9 of the proposal; a socket guard so no test reaches a real endpoint". And the Anonymizer row
amended per Q47: "local model entity pass plus code rules, the matter's name list in the identifier check;
Presidio or GLiNER-PII optional as a second detector; the key under `<matter>/anon/`, mode 600, never
shared". Roadmap: stage 7 (anonymizer row), 7b (the rest).

P7. (§7 roadmap). Stage 6 row gains: "cards are engine-neutral: a synthesis card takes a fact packet
(facts with quote, cite, page id) and the cited pages, answers in a D34 schema with a cite and quote on
every assertion, and uses no Ollama-only feature; the renderer takes the gated answer". Stage 7 row
unchanged in intent. New row: "7b. Cloud round trip: cloud client, sent-log, approvals, kill switch, cost
caps, cloud stand-in, Codex second review (off) | Loop | the stage 7b exit line of proposal §9, and a
seeded leak of each of the 8 kinds blocked with 0 requests". Stage 8 row gains "approve and cloud screens;
the sent-log view". Stage 9 gains "`casefile cloud probe` with an invented page against the real endpoint:
tokens, cache read, cost, request id".

P8. (§8b gains a paragraph). New: "The API path. The engine under the `casefile` user calls Anthropic
directly for the automatic round trip; it shares the bridge's identifier check, sent-log and approval
table but not its tools. The bridge stays for interactive work. A Codex session under the `claude` user may
register the bridge with `codex mcp add` and gets the same six tools." Roadmap: 7b and 8b.

P9. (D13 amended). New `[cloud]` table: `enabled` (default false), `host` (exactly
`https://api.anthropic.com`, or `http://127.0.0.1:<port>` for the stand-in; anything else refused),
`model`, `context_tokens` (default 200000), `max_input_bytes` (600000), `max_answer_tokens` (16000),
`timeout_s` (600), `cost_cap_usd_per_run` (10), `cost_cap_usd_per_day` (50), `approval`
(`task|package|standing`, default `package`), `keychain_item`, `key_source` (`keychain`, or `file:<path>`
only with a loopback host), `terms_confirmed` (a date, required when enabled), `codex` (default false),
`codex_model`. Unknown keys refused as today. Roadmap: stage 7b.

P10. (D32 amended). Run log schema v3: `cloud_sends` table and its triggers; v2 upgraded in one
transaction; the doctor's `runlog_schema` row reports `schema=3`. Roadmap: stage 7b.

P11. (D20 amended). The privacy row also fails on `sk-ant-` in any tracked or ignored file and on the names
`anon/` and `key.json` in the checkout. Roadmap: stage 7b (the row can land earlier at no cost).

## 11. Risks with tripwires

| # | Risk | Tripwire (measured) |
|---|---|---|
| R1 | An identifier the name list misses leaves in a packet | Seeded leaks: 20 of 20 of 8 kinds blocked with 0 requests, every round; on the Studio the second entity pass's hit count per matter is printed in `.cloud.md`; any hit halts |
| R2 | Claude invents a placeholder, a cite or a date | `unknown placeholder`, `cite not a page`, `absolute date` counts per run in `.cloud.md`; any count over 0 drops the item; over 3 in one run fails the run (a sign the card is wrong) |
| R3 | Cost runaway | per-run cap 10, per-day cap 50 (owner question 65); `cloud_sends` daily sum printed by `status`; a refused call is an open item named "cost cap" |
| R4 | The API key leaks into the repo, the run log or an output | privacy row red on `sk-ant-`; a test asserts no header text in any run log column; the key is read from the Keychain, never from config |
| R5 | A code path sends around the kill switch or the check | one function `cloud.send()` is the only caller of the opener; a test flips the switch and asserts 0 requests for every menu task; the stand-in's request counter is the oracle |
| R6 | The stand-in drifts from the real API | a recorded real reply from `casefile cloud probe` on the Studio (invented page) is checked against the stand-in's shape at stage 9; a field the mapping needs that is missing fails the probe |
| R7 | The nonce or a timestamp busts the cache and doubles cost | `cache_read_input_tokens` stored per answer; zero on the second call of a job is a logged warning; stage 9 measures the ratio |
| R8 | Codex keeps the packet in `~/.codex` or reaches beyond the scratch folder | after each run a grep of `~/.codex` for the packet nonce must return 0; the scratch folder listing before the call is exactly two files; `-s read-only` and `--ephemeral` asserted in argv |
| R9 | Cut answers (`max_tokens`) | the share of calls with `done_reason=length` per run; over 5 percent raises `max_answer_tokens` or splits the packet, decided by the benchmark |
| R10 | The restore check drops too much (a quote through a placeholder) | dropped items per run; over 10 percent of items fails the run and names the pages; the anonymizer's token-boundary rule is the first suspect |
| R11 | Approval fatigue under mode B | approvals per day and the median time between "shown" and "approved"; under 10 seconds for a week is reported as rubber-stamping |

## 12. Owner questions (numbered 59 to 69 here; filed as 70 to 80 in `docs/loop/questions-for-owner.md`; each with a fail-closed interim)

59. Account and retention: which Claude Console organization holds the key, is it under commercial terms,
    has zero data retention been granted for it by Anthropic's sales team, and do you want the HIPAA
    arrangement (a BAA accepted in the Console)? Interim: `[cloud].enabled = false`; nothing is sent until
    `terms_confirmed` carries a date you wrote.
60. Approval mode: A (once per task, with the two halts), B (per packet) or C (standing)? Interim: B for
    every task.
61. Codex: what should Codex do (the second-review critic proposed, or something else), on which plan and
    terms (API key or ChatGPT login, Business or Enterprise, retention, training opt-out)? Interim: off.
62. Model: Opus 5.5 (ZDR possible) or Fable 5.1 (30 day retention required, no ZDR)? Interim: Opus 5.5.
63. The name list: beyond casefile-anon/1, are the IAB hearing number, the claim number, the carrier and the
    adjuster identifiers to replace, and is a treating facility's name one? Interim: all replaced.
64. Briefs: should the argument with legal research go out automatically (it needs the web search tool, a
    pillar 4 change), or stay interactive through the bridge with the API drafting facts and outline only?
    Interim: facts and outline only.
65. Cost caps: $10 a run and $50 a day as defaults? Interim: those numbers; the job stops at the cap.
66. Stage order: 7b after 7 and before the web page (approval by CLI over SSH meanwhile), or after stage 8?
    Interim: after 7, before 8.
67. Hearing prep: is the billing memo you supply ever sent out (it names providers and amounts)? Interim:
    never; its totals are inserted locally after restore.
68. Retention on the Studio: keep every sent packet, reply and restored answer in the matter folder for the
    life of the matter, or purge after a period? Interim: kept, append-only.
69. Network: will you add a Firewalla egress rule allowing the Studio to reach `api.anthropic.com` (and
    OpenAI's endpoint only if 61 says yes) and nothing else? Interim: assumed blocked; the doctor's `cloud`
    row reports it.

## 13. Effect on round 6

Nothing in this proposal is built in round 6. The round 6 brief keeps its scope (stage 6 outputs on the
local model, the cards and schemas rewrite, the Q49 reconcile pass) with two constraints that cost nothing
now and save a rewrite later:
1. Engine-neutral synthesis cards: input is a fact packet (facts with quote, cite, page id) plus the
   cited pages; output is a D34 schema with a cite and quote on every assertion; no Ollama-only feature in
   the card text. The anonymization card (R6-2) finds names and the anchor date only, with a quote and cite
   each, per Q47.
2. The deposition, hearing and report renderers take the gated JSON answer, not the model call, so a
   restored cloud answer renders through the same code.
What waits: everything in §4 to §9 (stages 7 and 7b), the config table, the run log v3, the stand-ins, the
doctor row, the bridge paragraph. The chair reconciles this file with the round 6 brief before the plan
review (ledger Q52).
