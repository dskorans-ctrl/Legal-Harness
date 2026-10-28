# casefile: spec (canon)

The local case system for one personal injury and workers' compensation attorney. It reads client and
medical records on a Mac Studio, keeps a running case file and medical memo per matter, and produces
deposition prep, hearing prep and anonymized brief and motion packages. This file is canon: it wins
over plans, comments and rules files. Every design change lands in §9; new questions in §10.

Owner-facing setup guide (Claude Docs, "Local AI Setup Guide"): https://claude.ai/artifact/RYMsSFNdBPkWus4ZqLtnCU
UI mockup: https://claude.ai/artifact/TcvRDeJAfG3B5MnvEnoQnk

## §1 Pillars (tie-breakers for every ruling)

1. **Only trust what is on the page.** Every fact carries a cite to a page that exists; quotes are
   checked against the source in code. No assumption, no guess, no medical inference.
2. **Fail closed.** A step that cannot be verified stops and says so. Nothing is saved empty, partial
   or unverified as if it were read.
3. **Client data never leaves the Studio**, except anonymized brief packages the attorney approves.
4. **Code decides the steps; the model fills one step at a time.** No agent loop, no model tools.
5. **The attorney decides.** Instructions become a confirm card; playbook changes need a click;
   conflicts between records are kept and shown, never resolved silently.
6. **Measured, not argued.** A change to the model, a card or a gate is kept only if the benchmark says so.

## §2 What it does

- **Matters.** One folder and one case file per matter. Records arrive by drag and drop on the web
  page or in the matter's inbox folder.
- **Running medical memo.** Treatment chronology, providers, diagnoses, restrictions, medical history,
  our doctors' and defense doctors' opinions, gaps and missing records, conflicts. Rebuilt after every
  upload, with a "what changed" summary and a list of outputs now out of date.
- **Deposition prep.** Deponent: our doctor, defense doctor, our client, witness. Taken by us or by the
  defense. Discovery or trial preservation. Output: a two-page case outline (our view, then the
  defense view) and a question document (primary, anticipated cross, redirect), a danger zone list and
  points for our expert.
- **Hearing prep (workers' comp).** Hearing outline, client prep, doctor prep, closing. The billing memo
  to the Hearing Officer is always first on the checklist.
- **Report analysis.** Defense medical examination reports and our doctors' reports, against the case file.
- **Brief and motion package.** The attorney describes the issue in a chat box. The system builds an
  anonymized fact package (no legal research is done locally): placeholders such as [CLAIMANT],
  [EMPLOYER], [DR-1]; dates as days from the injury; a keep list of identifying items research needs;
  an identifier check that must pass; attorney approval; download. Research and drafting happen with
  Claude under commercial terms. Re-import: the draft is re-identified, fact-checked against the case
  file, and produced as a Word document.
- **Ask or instruct panel.** Questions answered with verified, cited quotes (docuchat or its
  verification code). Instructions become a filled-in job form shown as a card; nothing runs until Run.
- **Commands:** `casefile new`, `intake`, `memo`, `depo --deponent our-doctor|defense-doctor|client|witness
  --taken-by us|defense`, `hearing --outline --client --doctor --closing`, `brief-out "<issue>"`,
  `brief-in`, `report --defense|--ours`, `status`, `search`, `bench`, `doctor`, `web`, `service install`.

## §3 How a file moves

1. A file arrives (web page or inbox folder).
2. Intake: OCR where needed; every page gets an ID (matter, binder, page) and the list of every Bates stamp
   found on it; hearing prep asks which stamp to cite (owner Q35).
3. Cards: pages are split into chunks well inside the context; the right card runs on each chunk.
4. Gates (§4) on every answer.
5. Merge into the append-only case file: a repeated fact adds a cite; added detail adds a version;
   disagreement is kept as a conflict for the attorney.
6. Outputs are built from the case file, never from a chat, and download as Word documents.

## §4 Gates (every model answer, in order)

1. Truncation (D31): the prompt was within budget before the call (UTF-8 bytes plus a template allowance, re-checked
   on the retry), the call asked the server not to cut (`truncate: false`), the answer begins with the call's
   `prompt_id` and ends with its `end_id` (a fresh nonce per attempt), and `done_reason` and both token counts are
   present and agree with the context. The counts are stored, never trusted as proof of reading.
2. JSON repair, punctuation only (a fence, control characters, trailing commas, missing closers only when `end_id`
   is last); a duplicate key or any other parse error fails (D33).
3. Schema check against the card's schema.
4. Quote check ladder, on the page the quote cites: exact, then whitespace, then curly versus straight quotes and
   case (which folds ligatures), then OCR faults (a hyphen at a line break between letters; a stamp alone on a line
   and a "Page N of M" line ignored, owner Q44); every match on token boundaries; otherwise rejected, naming the
   page searched. Every cite is a page of the chunk, and every number in a fact's summary is in its quote (D35, D38).
5. Firm rules check (`rules.toml`), on outputs only: never "DME", "IME", "independent medical
   examination" or "defense medical examination" (say "the report"); never who hired, paid or
   retained the doctor, fees or exam volume; treatment and bills never in one question; Bates cites,
   with a warning when records are not stamped.
6. Coverage ledger: a page counts as read only when all of the above pass and the answer cites it; an answer with
   no facts and no flags, or with a blank field, fails; a page a passing answer never cites is an open item
   (`uncited`, D38, owner question 47).

A failure is retried once, as a fresh prompt with the error shown and no history (a prompt-side failure is not
retried); then the pages are marked failed and listed as open items. Never saved as empty.

## §5 Parts, and what is reused

| Part | Built with |
|---|---|
| Job runner, one job at a time, Cancel stops model call and OCR together | Python, SQLite |
| Intake and OCR | ocrmypdf and Tesseract, page text by pypdf (stage 3, D27); Docling for layout and tables when a stage needs them, kept only if the benchmark says so |
| Model client | Ollama native API (`/api/chat`, never the OpenAI-compatible route), Qwen3.8-27B, `num_ctx` 65536 in the Modelfile and on every call, low temperature, thinking mode per card, stable prompt order (rules and card first, page text last), `truncate: false` on every gate pipeline call (D31) |
| Extraction | LangExtract with fuzzy matching off or marked unverified, kept only if it beats direct calls on the benchmark |
| Gates | Python (§4) |
| Case file | append-only JSON, versioned |
| Run log | SQLite: every run, card version, pages in, raw answer, failures, approvals |
| Rules | `rules.toml`, read by cards and checker |
| Outputs | python-docx templates |
| Anonymizer | Presidio plus the matter's own name list; the identifier check blocks any leak |
| Ask panel | docuchat (pinned version, outside connectors off) or its quote-verification code |
| Web page | FastAPI and plain HTML, localhost, published with `tailscale serve`, password |
| Benchmark | `casefile bench`: answer keys from closed matters, scored on missed, invented, flags, firm rules |
| Startup check | `casefile doctor`: Ollama on 127.0.0.1 only, full context loaded, OCR works, folders writable |

## §6 The playbook

`playbook/` holds the attorney's practice, with no client facts: deposition goals, topic order,
question banks and how to ask (per deponent type); hearing outline, client prep, doctor prep, closing
and checklist; and `rules.toml`. Each entry records the rule, why, a good and a bad example of the
wording, the date added and where it was learned. Cards are built from it at run time.

Updating it: the attorney types or dictates a lesson; Qwen drafts a before-and-after edit, flags
conflicts and strips identifiers; the attorney approves, edits or rejects; the playbook gets a new
version; a hard rule also goes into the checker; the affected cards run on the benchmark; every output
records the playbook version it used. An update packet regenerates the Claude skills
(`deposition-prep`, `workers-comp-hearing-prep`) so both stay in step.

Possible later (not decided): Obsidian as an editor for the playbook, and as a read-only matter view on
the Studio only, with Restricted Mode on and no community or AI plugins on client data.

## §7 Roadmap (build stages, each with its exit test)

| Stage | Where | Exit test |
|---|---|---|
| 1. Skeleton, config, rules file, playbook loader, run log | Loop | `casefile doctor` runs and the run log records a test job |
| 2. Benchmark and invented test matter | Loop | `casefile bench` scores the test matter against its answer key |
| 3. Intake and OCR with page IDs | Loop | a scanned PDF becomes page text with correct IDs |
| 4. Model client and gates | Loop | every gate tested with good and bad answers, including truncated ones |
| 5. Case file, merge, medical memo | Loop | the test matter produces a memo with cites, conflicts and open items |
| 6. Outputs: deposition, hearing, report analysis (cards built from the playbook) | Loop | Word documents built from the test matter pass the output critic |
| 7. Brief package and anonymizer | Loop | the identifier check passes on the test matter; re-import fact-checks a draft |
| 7b. Cloud round trip (D52 to D62, pending veto) | Loop | a task on the test matter goes out anonymized to the Claude API stand-in, its answer passes the gates, is re-identified and renders the same document; the identifier check blocks a seeded leak with 0 bytes sent |
| 8. Web page, Lessons screen and update packet | Loop | all screens work against the test matter |
| 9. Install on the Studio; benchmark real closed matters | Studio | benchmark passes at 8-bit and full precision over three days |
| 10. First live matter | Studio | one live matter run alongside the usual process |

The 45 cards and 19 schemas in `cards/` and `schemas/` were written before the single-model decision.
Stage 6 updates them: single model; drop the brief outline, argument and authority-check cards; add the
anonymization card and the medical memo card; build card text from the playbook.

## §8 Install and access (summary; full steps in the setup guide)

Clone on the Studio, `./install.sh`, `casefile doctor`, set the web password, run the benchmark on
closed matters (owner only), `casefile service install`, `tailscale serve --bg 8080`. Reached from the
owner's devices over Tailscale with the page password; never on the public internet. Updates:
`git pull && ./install.sh`, then `casefile bench` before any live use.

## §8b The headless Studio and the Claude bridge (owner, 2026-10-26)

The Studio runs headless (no monitor) and also hosts Claude Code, so Claude can plan and draft with the
local system's results without ever reading client files. Decisions D12 to D16 below; they are
recorded here rather than in the §9 table so this section merges cleanly with round 1.

**Two macOS users; the operating system is the wall.**
- `casefile` (standard user): owns `~/Cases`, the run log, the playbook copy in use, and runs Ollama,
  the engine, the web page and the bridge. Its home folder is 700: no other user can read it.
- `claude` (standard user, not admin once setup is done): runs Claude Code. It cannot read the
  `casefile` user's files at all. Its Claude Code settings also deny reads and shell commands on
  `/Users/casefile`, but the file permissions are the real boundary; instructions are not.
- Setup and installs happen under an admin account before any client file is on the machine.
- Claude Code uses a Team or Enterprise account (commercial terms; zero data retention if Enterprise).

**The bridge: an MCP server run by the `casefile` user.** It listens on 127.0.0.1 only (streamable
HTTP, with a token the `claude` user's Claude Code holds), and offers a fixed menu, nothing else:

| Tool | Returns |
|---|---|
| `list_matters` | matter numbers (e.g. 1012.001) and status counts only |
| `matter_status(matter)` | pages read and failed, open-item count, which outputs are ready; no content |
| `start_job(matter, job, options)` | a job id; jobs are the §2 menu (intake, memo, depo, hearing, report, brief-out) |
| `job_status(job_id)` | queued, running, done or failed, with counts |
| `get_package(matter, package_id)` | only a package that passed the identifier check AND that the attorney approved on the web page |
| `submit_draft(matter, file)` | the brief-in re-import; returns the fact-check report, itself anonymized |

There is no tool to read a file, search a matter or fetch the memo. Every payload the bridge returns
passes the identifier check in code first (fail closed: a hit blocks the reply and is logged). Every
call is written to the run log. The mapping from matter numbers to client names lives only in the
`casefile` user's config.

**Matter numbers are the shared language, not the protection.** Claude's skills may refer to 1012.001;
a number plus enough facts can still identify a client, so returned packages are anonymized as in §2
(placeholders, dates as days from injury, keep list).

**The local model still has no tools.** Text in a document cannot make it act, because it can only
answer in JSON to the engine. No local agent loop, no MLX, no Alfred: the engine's fixed jobs and
scripts are the only actions.

**Shared folders on the network (macOS File Sharing).**
- `Outbox` (read-only share): approved, anonymized packages only, for the operations computer.
- `Inbox` (write-only drop box share): records dropped from the operations computer land in the
  `casefile` intake queue; nobody can list or read it over the network.
- Shares limited to one network user and to the operations computer; a Firewalla rule blocks every
  other device. Client files themselves are never shared.

**Headless operation.**
- Managed with Screen Sharing and SSH from the M4 or over Tailscale; a dummy display adapter only if
  Screen Sharing needs one for a usable resolution.
- Restart automatically after a power loss (`pmset autorestart 1`), with the UPS shutting it down
  cleanly first. FileVault stays on; whether this macOS can unlock FileVault over SSH after a
  restart is an open question (§10). If it cannot, a restart needs a Screen Sharing unlock.
- The engine, web page, bridge and Ollama start at login of the `casefile` user (launchd), and
  `casefile doctor` reports their state.

**Firm financial documents.** Same rules, in their own area (`~/Finance` under `casefile`, IDs such as
F-2026-01), as a later job type; not in the current build scope.

**Build stage 8b (after stage 8, before the Studio).** The bridge server, its six tools, the
identifier check on every reply, the two-user install steps and the shares in `install.sh`.
Exit test: in the loop, a planted client name in a package is blocked by the bridge and logged, and
no tool returns content outside the table above; on the Studio (stage 9), the `claude` user gets
"permission denied" on `/Users/casefile/Cases`.

Decisions: D12 headless Studio hosts Claude Code under its own user; D13 two macOS users with the OS
as the boundary; D14 MCP bridge with the fixed menu and cleared-results-only rule; D15 Inbox drop box
and read-only Outbox shares for the operations computer; D16 no local agent loop, no MLX, no Alfred.

## §9 Decisions

| # | Decision | By | Date |
|---|---|---|---|
| D1 | Fixed workflow, not an agent; the model has no tools | owner | 2026-10-25 |
| D2 | One model, Qwen3.8-27B (8-bit or full precision decided by the benchmark) | owner | 2026-10-25 |
| D3 | Brief and motion outputs anonymized; no legal research locally (done with Claude) | owner | 2026-10-25 |
| D4 | Running medical memo per matter | owner | 2026-10-25 |
| D5 | Benchmark built before the engine | owner | 2026-10-25 |
| D6 | Reuse Docling, ocrmypdf, LangExtract (if it wins), Presidio, docuchat; do not rebuild them | owner | 2026-10-25 |
| D7 | Playbook as the one source for local cards and Claude skills; updates need approval | owner | 2026-10-25 |
| D8 | Built in rounds with app-loop: one fresh session per round, Remote Control on, a critic round | owner | 2026-10-25 |
| D9 | Code in the private repo dskorans-ctrl/Legal-Harness; only `main` pushed, on the owner's word | owner | 2026-10-25 |
| D10 | Obsidian: possible later, not decided | owner | 2026-10-25 |
| D11 | No MLX work; Ollama is the engine | owner | 2026-10-25 |
| D12 | `scripts/run.sh`: 50 MB combined cap; exit 96 no command, then 95 toolchain inside the checkout or not verifiable (D24), then 98 capture failure, 127 command not found, 126 not executable, 97 cap hit (process group killed), else the child's code (a signal as 128 + n); after the child exits the wrapper reads at most 2 s more, then kills the group (best effort) and returns the child's code (a process that left the group is not reached) | chair, pending veto | 2026-10-25, amended 2026-10-26 (CX-4, B2, B1b, V3-2 to V3-4, N2) |
| D13 | Config: `$CASEFILE_CONFIG` or `./config.toml`, TOML; missing file, unknown key, bad type, `num_ctx` below 65536 or a host other than `http://127.0.0.1:<port>` fail closed; `[paths].matters` required and outside the checkout by identity (D24; owner Q17); absolute after `~` expansion; an unverifiable path or an unexpandable `~` is refused (ConfigError, exit 2); model tag `qwen3.8:27b` (owner Q20) | chair, pending veto | 2026-10-25, amended 2026-10-26 (R1-22) |
| D14 | Data root outside the checkout; `state/` (run log) in the checkout, gitignored; `Cases/` and `Bench/` forbidden repo prefixes | chair, pending veto | 2026-10-25 |
| D15 | Run log SQLite schema v1 (`schema_meta`, `runs`, `answers`, `failures`, `approvals`), append-only by triggers; "a test job" is the doctor's warmup run with an `ok` answer | chair, pending veto | 2026-10-25 |
| D16 | `rules.toml` schema; rule 5 on outputs only, blocking DME, IME and both spelled-out phrases (owner Q16); a Bates cite body must fully match the configurable pattern (owner Q21); "every fact has a cite" is gate 6 at stage 4 | chair, pending veto | 2026-10-25 |
| D17 | Playbook entries in TOML with the six §6 fields; non-rules entries are SAMPLE until owner content (owner Q12), enforced by a gate row; version `pb-` plus a sha256 prefix | chair, pending veto | 2026-10-25 |
| D18 | Stand-in model server: stdlib, Ollama native `/api/chat` and `/api/ps` shape, port 18434 (never 11434), modes replay, truncated, malformed, forbidden, short_context, empty, incomplete (done=false) | chair, pending veto | 2026-10-25, amended 2026-10-26 (CX-5) |
| D19 | `casefile doctor`: eight checks, each PASS or FAIL with a reason, none skipped; loopback by hostname, `/api/version` and `lsof`; full context by a warmup answering `READY` and `/api/ps` context; OCR FAIL until stage 3 (owner Q11); exit 0 or 1 | chair, pending veto | 2026-10-25 |
| D20 | Gate `python -m casefile.gate`: rows pytest, privacy (ignored files included), rules self-test, playbook, prose; prints and exits the failed-row count; the doctor is covered by the stage 1 exit test, not a gate row | chair, pending veto | 2026-10-25 |
| D21 | Model client transport: no proxy, redirects refused, an empty answer is an error | chair, pending veto | 2026-10-25 |
| D22 | Codex gpt-6.1-sol writes code instead of Sonnet (owner Q14); critic round of round 1 held to the next session (owner Q15) | owner | 2026-10-25 |
| D23 | Dev toolchain (uv Python, cache, venv) lives outside the checkout under `~/.casefile-dev/<checkout name>` (override `CASEFILE_TOOLCHAIN`), so the privacy row can scan ignored files with no exemption; the override (taken against the current directory when not absolute) and its `python`, `cache`, `venv` and `venv/bin` children are checked by identity (D24) before any uv call | chair, pending veto | 2026-10-25, amended 2026-10-26 (R1-22) |
| D24 | `src/casefile/pathguard.py`: the one place that decides whether a path is inside the checkout, by filesystem identity (st_dev, st_ino) of every existing ancestor of the typed and real spellings; stdlib only, python3 >= 3.9, used by config.py and scripts/run.sh; verdicts outside, inside, cannot-verify, relative; CLI takes one root and one or more paths, prints one `pathguard <verdict> <detail>` line, exits 0, 10, 11, 12 | chair, pending veto | 2026-10-26 |
| D25 | `casefile bench --matters DIR [--candidate FILE] [--config FILE]`: each subfolder with `matter.toml` is a matter of `records/<binder>/<nnn>.txt` pages, the Bates stamp alone on the last line; `key.json` (facts: id, cite, quote, text; flags: id, kind conflict or gap, cites, about) is validated against the pages before scoring; a candidate is `{facts: [cite, quote, text], flags: [kind, cites, about]}`; found = same cite and the same quote after normalisation (casefold, straight quotes, collapsed whitespace); invented = cite not a page or quote not on it; extra = on the page, not in the key; flags match by kind and cite set; rules = firm rule findings over every text and about; a fact's text is not compared with its quote at stage 2 (the §4 ladder, stage 4); one line per matter `bench <number> found=F of K missed=M invented=I extra=E flags=G of H flags_missed=X flags_extra=Y rules=R pages_failed=P of N`; exit 0 when every matter is perfect (missed, invented, flags_missed, flags_extra, rules, pages_failed all 0; extra alone never fails), 1 otherwise, 2 when it cannot run (config, playbook, matter, key, candidate file or run log); `--matters` is independent of `[paths].matters` (D13 guards client matters only; benchmark matters are invented and may live in the checkout); stage 2 runner: one `/api/chat` call per matter with the fixed card `bench.extract`, logged as a run with every received reply stored as an answer row and failures under `bench.model`, `bench.truncation`, `bench.counts`, `bench.answer`; replaced by the pipeline at stage 5 and the quote match by the §4 ladder at stage 4 | chair; owner ratified 2026-10-27 | 2026-10-26 |
| D26 | D20 amended: the prose row also covers authored fixture text (`tests/fixtures/**` .txt, .json, .toml). Round 2 code is written by the local model gemma4:e4b-it-qat through `scripts/gemma_task.py`, Opus orchestrating, Sonnet fallback per task (owner Q28) | chair; owner ratified 2026-10-27 (Q28 part: owner) | 2026-10-26 |
| D27 | Stage 3 intake: `casefile intake --matter N --binder B FILE`; ocrmypdf `--redo-ocr --output-type pdf --sidecar -l eng --tesseract-timeout 180` once per PDF, page text by pypdf from the output, per-page outcome from the sidecar (`[skipped page]` is `failed`); Docling deferred until a stage needs layout or tables and the benchmark keeps it (D6 intent unchanged); page store `pages/<binder>/<nnn>.json` and `binder.json`, published by renaming `.tmp` folders, with `source.pdf`, `ocr.pdf`, `sidecar.txt` under `records/<binder>/`; the matter folder must exist and resolve under the matters root by identity; re-intake into an existing binder refused; a page ID is matter, binder, page; every stamp matching `[ocr].stamp_pattern` is recorded raw and normalised (letters plus digits), none chosen (owner Q35, Q40); a page with no text after OCR is `empty`, a skipped page `failed`, both listed and never read; exit 0 all ok, 1 open pages listed, 2 cannot run; no run log row until the stage 5 job runner; ocrmypdf runs in its own process group under the matter folder with `[ocr].timeout_s` (default 3600), killed as a group on timeout or interrupt; `scripts/run.sh` appends `/opt/homebrew/bin` and `/usr/local/bin` to PATH when present; Pillow and pypdf are runtime dependencies | chair; owner ratified 2026-10-27 (Q42) | 2026-10-27 |
| D28 | D25 amended: the authored stamp alone on the last line loads as the page's only stamp (normalised); a cite matches a page when its normalised form is one of the page's stamps (owner Q40); entries named with a leading `.` are ignored under `records/` and in binder folders; `binders` must be distinct; two roots with one matter number are refused (exit 2); the line reads `bench <number> model=<tag> found=...` (`model=candidate` in `--candidate` mode, owner Q27); a received bad reply is scored (exit 1), no reply from the server at all is exit 2, cannot run (owner Q26); the 9001.001 key holds 29 facts and 9 flags (G7, G8 gaps, G9 conflict MED0006,DEF0002; owner Q36, Q41) | chair; owner Q34, Q41; ratified 2026-10-27 (Q42) | 2026-10-27 |
| D29 | D19 amended: OCR passes only when both tools are found and a generated image-only smoke page (no text layer before) is OCR'd through the intake path with intake's flags, its text read and its stamp `SMOKE 7342` found and normalised to `SMOKE7342`; the reason names the smoke result and the tool versions (owner Q39) | chair; owner ratified 2026-10-27 (Q42) | 2026-10-27 |
| D30 | D21 amended: `ModelError.received` says whether a status line arrived; `http.client.HTTPException` is a `ModelError` (the partial body kept as `raw` for `IncompleteRead`); a received error with no body is stored as a `failed` row with an empty body | chair; owner ratified 2026-10-27 (Q42) | 2026-10-27 |
| D31 | (new; spec §4 and §5 model client row amended). Old text (§4): "1. Truncation: the answer did not stop early, and the model read as many tokens as were sent." New: "1. Truncation: the prompt was within budget before the call (a byte-count ceiling, `tokens_at_most`, re-checked on the retry), the call asked the server not to cut (`truncate: false`), the answer, after fence removal, begins with the call's `prompt_id` and ends with its `end_id` (a fresh nonce per attempt, present once in the prompt), and `done_reason` and the token counts are present and agree with the context; the counts are stored, never trusted as proof of reading." Why: D0.2 shows a cut prompt counts about half the context and a cached prompt may count less than sent, so the old sentence has no sound test; the checks of §1.1 are each probed alone. Row: the gate pipeline of §1.2 and §1.3 (`gates.py`, order, the retry as a fresh two-message prompt with the error shown and no history, `Outcome.answer is None` on failure, gate names `gate.<name>`, firm rules skip `quote`, `cite`, `cites`, `prompt_id`, `end_id`, the pipeline's own unstamped warning). | chair (round 4 brief, Astra plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-27 |
| D32 | (D15 amended). Run log schema v2: `coverage` (status `read`, `uncited` or `failed`) and `gates` tables, `answers.prompt_eval_cached_count`, v1 upgraded in place by `UPGRADE_V1_V2` in one explicit transaction that rolls back whole, latest coverage row by `id`, open items = not `read`, triggers 21, any other version refused (§1.9). Why: gate 6 needs a durable per-page ledger and §8b `matter_status` reads it; the published `pages/` folder is immutable by D27. | chair (round 4 brief, Astra plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-27 |
| D33 | (new). JSON repair is punctuation only, the four kinds of §1.4, each logged as `repaired`; the closer repair runs only when `end_id` is the last key at the tail, else `RepairError`; `unfence` is pure and gate 1 reads the ids from the unfenced text; everything else is `gate.repair` failure. Why: pillar 1 and 6, the cut-list hazard in §1.1(c), the fence-before-ids order. | chair (round 4 brief, Astra plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-27 |
| D34 | (new). Schema check by a stdlib subset validator over `type, properties, required, additionalProperties: false, items, enum, title, $schema`; any other keyword or value refuses the schema at load; every object with a `quote` key carries a `cite` string; empty arrays are schema-valid (gate 6 rules on them, D38); `schemas/bench_extract.schema.json` is the stage 4 card's schema. Why: §1.5. Spec §7's "stage 6 updates them" gains: the 19 schemas are loaded by this validator today (D0.9) and stage 6 keeps them inside the subset or decides again with the benchmark. | chair (round 4 brief, Astra plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-27 |
| D35 | (D25 amended, the sentence "a fact's text is not compared with its quote at stage 2 (the §4 ladder, stage 4)" replaced). New: "invented = cite not a page of the matter or quote matched at no rung of the §4 ladder (`quotes.match`); found = same cite and the same quote after the ladder's folding (`quotes.same`); the key loader refuses two facts equal under that folding; a `rungs:` detail line when any match used a rung other than exact; the ladder's OCR rung joins line-break hyphens and drops only a stamp alone on a line and a `Page N of M` line (owner Q44), ligatures being folded by casefold at the curly rung; a fact's text is compared with its quote at stage 4 by the digit-run check only (D38); the stage 2 runner's own guards stay until stage 5." Why: §1.6, §1.7, §1.13; the shipped numbers do not move. Spec §4 rule 4's "running headers" reads, by Q44, as those two line kinds. | chair (round 4 brief, Astra plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-27 |
| D36 | (D18 amended). Stand-in modes: the seven of D18 plus `prompt_too_long`, `cut_prompt`, `cut_answer`, `repairable`, `unrepairable`, `bad_schema`, `bad_quote`, `forbidden_json`, `empty_answer`, `retry_ok` (17); `truncate` accepted on `/api/chat`; the lookup canonicalises the nonce line and the `Retry:` line on both sides and substitutes `__PROMPT_ID__` in the answer. Why: §1.10, the exit test's four truncated cases. | chair (round 4 brief, Astra plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-27 |
| D37 | (D28 amended). Two roots with one matter number, or any loader error, are refused before the run log is opened and before any matter runs; `stamps.normalize` keeps letters and digits only; one `stamps.compile` wrapper for the finder and the config check. Why: R03-V-L1; Q40 and Q42 say a stamp is letters plus digits. | chair (round 4 brief, Astra plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-27 |
| D38 | (new; spec §4 rules 4 and 6 gain a sentence each). Gate 4 checks every reference: each fact `cite` and each flag `cites` entry is a page of the chunk, each quote is on its page by the ladder, and each digit run in a fact's `text` appears in its `quote`; a `text`'s words are otherwise unverified and no output treats them as verified until owner question 48 is answered. Gate 6: an answer with no facts and no flags fails (`empty answer`, retry once, nothing saved); in a passing answer a page it cites is `read` and a page it never cites is `uncited`, an open item never counted as read (owner question 47). Why: §1.13; pillars 1 and 2. | chair (round 4 brief, Astra plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-27 |
| D39 | (D25, D35 executed; §5 benchmark row amended). Old text (D35 tail): "the stage 2 runner's own guards stay until stage 5". New: "From stage 5 `casefile bench` runs the gate pipeline (`pipeline.bench_run`): every page of the matter, chunked by bytes in page order (`pipeline.chunk`, `RETRY_MARGIN`), one run row per chunk, the candidate built from the merged in-memory case file; `pages_failed` counts pages with coverage `failed` (a failed chunk or a page too long for one prompt); a `uncited:` detail line lists pages no passing answer cited, in model mode only; `benchrun.py` and its recording row are removed; the extraction card is `extract.card()` (name `bench_extract`, version unchanged)." Why: §1.4, §1.12, T-9 measured on the fixture. | chair (round 5 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-28 |
| D40 | (new; spec §3 step 5 and §5 case file row made concrete). "The case file is `<matters>/<number>/ casefile.jsonl`: one JSON object per line with a contiguous `seq` and a `prev` sha256 of the previous line; kinds `fact`, `cite`, `reading`, `flag`, `about`, `run`, `output`; a fact's identity is the folded quote (`quotes.fold`), a flag's the kind and page-id set; a repeated fact on a new page adds a `cite`, a new wording a `reading`, a repeated flag with new wording an `about`; a broken chain refuses the matter (exit 2); nothing complete is rewritten: a torn tail after the last newline that is not a JSON object is reported, ignored by `load` and truncated by the next `append`, which also `fsync`s every write." Why: §1.5, §1.6; pillars 2 and 5; plan review M5. | chair (round 5 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-28 |
| D41 | (new; spec §2 running memo and §3 step 6 at stage 5). "`casefile memo --matter N` reads the matter's pages (intake layout, or the bench layout of a benchmark matter copied under `[paths].matters`), sends only pages not yet read by the memo job, merges every passing chunk, and writes `outputs/memo.docx` with python-docx (no template file): title and build line, what changed since the last memo, outputs out of date, open items by stamp, conflicts (opening with the number of runs that read pages and the sentence that conflicts between runs are checked only for pages sent together), gaps, verified facts by record page (a fact under the first page that cited it, with `Also cited` for the others; every paragraph of a page between its heading and the next) with the quote as the verified text and every model sentence, one paragraph per reading or about, labelled `Model's reading`; the memo's own words pass the firm rules before the file is written (quote runs and run-log reasons exempt), and a binder whose name fails a firm rule is refused before any model call with the remedy named; exit 0 all read, 1 open items listed, 2 cannot run; the sections are an owner interim (question 50)." Why: §1.1, §1.2, §1.3, §1.7, §1.8; Q48 interim; plan review H1, L1, L2, M4, M8, L10. Amended at the round 5 close (code review and fix cycles, chair, pending veto): a page heading with no quote says `Open item: <status> (see Open items).` or `No fact was quoted from this page.`; an empty section says `none`; unstamped pages are named in one plain sentence (`These pages carry no Bates stamp and are cited by page id: ...`, pages with text only); a fact whose pages are all absent goes under `Facts on pages not in this matter`; a reading from another page reads `Model's reading of [cite X]: ...`; the memo never lists itself as out of date; the conflicts sentence names chunks (`checked only between pages sent to the model together`). | chair (round 5 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-28 |
| D42 | (D38 amended; spec §4 rule 4 sentence "every number in a fact's summary is in its quote" becomes "every number in a fact's summary outside a bracketed cite is in its quote, and a bracketed cite inside a summary or a flag's about is itself a reference to a page of the chunk"; rule 5 gains "a chunk with any unstamped page runs the cite rule as a warning and names the unstamped pages"). The `bates-cites` rule also matches `see page N`, `at p. N` and `(Ex. X at N)` forms where N is a number or a stamp-shaped token, never the next word (R1-20); the cite body of any form is read by one helper shared by the rule and gate 4. Why: §1.9, §1.10, §1.11; verifier L1 and L2; Librarian #R04-V-2; plan review M2, M3. | chair (round 5 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-28 |
| D43 | (new; §8b `matter_status` and critic M2, L3). "`casefile status --matter N` prints pages, read, failed, uncited, empty, open, facts, conflicts, gaps and outputs (`memo:current`, `memo:stale`, `none`), then one line per open item labelled by every stamp of the page with the page id in parentheses, keyed by page id; the bridge returns these counts. Bench detail lines say `(no such page)` or `(quote not on the page)` and carry the rule's matched excerpt." Why: §1.7, §1.13, §1.14. | chair (round 5 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q50) | 2026-10-28 |
| D44 | (spec §7's cards paragraph replaced; D34 and D39 amended for the names). Old text: "The 45 cards and 19 schemas in `cards/` and `schemas/` were written before the single-model decision. Stage 6 updates them: single model; drop the brief outline, argument and authority-check cards; add the anonymization card and the medical memo card; build card text from the playbook." New: "Cards are JSON-only (every answer passes the schema gate) and engine-neutral (no card sentence names a message layout, server or model; a synthesis card's input is a fact packet of facts with quote, cite and page id plus the cited pages; every assertion in its answer carries a cite and a quote or the field does not exist); one loader (`cards.py`, manifest version 2) builds each card's text from the firm rules, the card body and the playbook's practice entries of its kinds and deponent; the manifest fixes per card the arrays of which one must be non-empty, the keys that may be blank, an echo key whose array must repeat the ids or page ids sent, and whether pages are marked read; 15 cards and 11 schemas remain (nine run by stage 6 jobs, one for stage 7, five for stage 8), the rest retired at `53a6f82`; the extraction card is `01-MEMO` (`medical_memo`); the anonymization card `07-ANON` finds names and the anchor date only, quote and cite each, and passes on an empty answer that echoes every page sent (Q47, Q53)." Why: §1.2, D0.3; review H3, L3, M3, M4. (Round 6 brief §6, owner amendments Q54 to Q57 included.) | chair (round 6 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D45 | (D17 amended; spec §6 gains a sentence). "Practice entries ported from the firm's own skills carry `sample = false` and `learned = "firm skill <name> section N"`; sample entries keep the SAMPLE marking; the gate counts both; cards include practice entries only." Why: §1.1, D0.11; Q12 ("practice content is the owner's": the skills are). (Round 6 brief §6, owner amendments Q54 to Q57 included.) | chair (round 6 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D46 | (D25, D28, D40 amended; spec §2 and §4 rule 4). "A fact carries `date`, `category` and `provider`; a non-empty date or provider is verified on the cited page by the ladder and a date must parse; the case file's `fact` and `cite` payloads carry them; a pre-round-6 payload is upgraded on load (undated, category `other`, bytes untouched) and any other shape is refused; the key's facts carry a date and the bench line gains `dates_wrong`." Why: §1.3; owner Q49 item 50; Q54 item 67. (Round 6 brief §6, owner amendments Q54 to Q57 included.) | chair (round 6 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D47 | WITHDRAWN before build (owner Q55). The reconcile pass of the earlier drafts (a comparison card after each extraction chunk, Q49 item 56) is not built; a cloud task run sends the whole anonymized matter (stage 7b), which closes the cross-run and cross-chunk gap there. The memo's conflicts sentence gains `A cloud task run reads the whole matter (stage 7b).`; T-22 stays a measurement of the local path. Spec §3 step 5 and §4 gate 6 are unchanged by this row. Why: §1.4; ledger Q55; #R05-PC-1 stays open for the local path only. (Round 6 brief §6, owner amendments Q54 to Q57 included.) | chair (round 6 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D48 | (D41 amended). "The memo's sections are spec §2's (chronology, providers, diagnoses, restrictions, history, opinions by binder role, gaps, conflicts, undated facts by page); each conflict shows the quotes of its two pages; conflicts between a `defense` binder and an `ours` binder come first and, with no such pair, the memo prints `ROLE NEEDED` and keeps the found order; binder names are shown as typed in exempt runs and `check_binders` is withdrawn; a binder's role is read from its name (`dme` or `defense medical`, any case or separator, is `defense`; every other binder is `ours`), with `matter.toml` `[roles]` as the override that a multi-plaintiff matter must supply (else `ROLE NEEDED`); `matter.toml` also holds `[header]` (matter type, client name, date of accident, treating physician, IAB hearing number, hearing date and time, plaintiffs) and `[hearing]` (`issues` from the type's list, `standard`, `relief`), read in both layouts by `matterinfo.load`; the header block prints those entries, `NEEDED` when empty; a page stamp the playbook's cite rule would reject refuses the job; the no-reply reason is transport-only and each command adds its own consequence." Why: §1.5; Q49 items 50, 54, 57; Q54 item 62; Q57 (superseding Q54 item 60 and Q56); #R05-CX-9; #R05-V-1. (Round 6 brief §6, owner amendments Q54 to Q57 included.) | chair (round 6 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D49 | (new; spec §2 deposition, hearing and report paragraphs made concrete; §3 step 6). "`casefile report`, `depo` and `hearing` build Word documents in `outputs/` in three fixed steps: `packet.build` (facts with quote, cite and page id, the cited pages, the task's options, the playbook version; JSON round trip), `outputs.ask` (one gated model step per card) and `render(answers, packet, ...)` (code only, from the gated JSON answers, so a restored cloud answer renders through the same code): the header block of the firm's conventions, code-assembled sections from verified facts by category group, model steps limited to labelling facts (`02-A`), writing questions with a verified quote each (`02-C-*`, `03-CLIENT`), concessions, labels and danger items (`04-G`) and elements (`05-A`), every model string labelled; output cards mark no page read, must return at least one item, verify prose numbers against the cited page and question strings with the question unit; a failed step is disclosed in the document, which is written as `.partial.docx` with no output event (exit 1); the our-doctor primary section must hold a treatment question and a bills question or say which is missing; the checklist's starred billing memo item is first; the standard, relief and issues come from `matter.toml` `[hearing]`, a run flag overrides for that run, and an absent one is marked NEEDED; the doctor's own records are the pages of the facts whose extracted provider matches `--provider`, with `--binder` or `--pages` as overrides; at a task run with no `[header]` table, code asks the attorney on the terminal (matter type, client name, date of accident, treating physician, IAB hearing number, hearing date and time, issues from the type's list), writes `matter.toml` once and never asks again; a non-interactive run prints `NEEDED` and does not block." Why: §1.6 to §1.9; spec §2; the firm skills; owner Q53; Q54 items 61, 62; Q57; review H6, M1, M2, M6. (Round 6 brief §6, owner amendments Q54 to Q57 included.) | chair (round 6 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D50 | (D16 amended). "`no-hired-paid-retained` also matches a fee paired with deposition, testimony or appearance, and `how often/frequently/many times ... retain`; the hire, engage, refer, `you`, share and split forms wait for the owner (question 64) because they block ordinary client and employment questions. Provider names (the packet's or the case file's extracted providers) do not count toward the treatment group of `treatment-and-bills-apart` (masked before that rule runs); `charges` and `bills` are exempt from the doctor pairing of `no-hired-paid-retained` in a question (the pairing keeps them for memo text through a `patterns_text_only` list; `charges?/charged` joins the `fees ... report` mirror), so the firm skill's bills question passes as written." Why: §1.11, §1.12, D0.9; review H5; owner Q54 item 59 (b) and (c). (Round 6 brief §6, owner amendments Q54 to Q57 included.) | chair (round 6 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D51 | (new; D40 amended). "A case file written before round 6 is upgraded on load: a `fact` or `cite` payload with exactly the round 5 key set is read with `date ""`, `category "other"`, `provider ""`, counted as `upgraded`, its bytes and hash chain untouched; such facts are undated in every output; any other key set stays a broken chain." Why: §1.3; owner Q54 item 67; #R05-PC-7. items 59 to 62 and 67 are built as answered, 63, 64, 65, 68 and 69 as the confirmed interims; 47, 48, 49, 51, 52, 53, 55 and 58 interims are kept (an uncited page stays open; the quote is the verified text; rule ids beside messages; default styles; `[cite X]`; page-id cites with the warning; re-send every run; "defense report" shown). Q37: no bills are read. Q41: defense-against-ours first. Q57 withdraws D41's refusal sentence. The spec §7 exit test is unchanged. (Round 6 brief §6, owner amendments Q54 to Q57 included.) | chair (round 6 brief, Fable plan review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D52 | (cloud round-trip proposal P1, `docs/loop/design/cloud-roundtrip-proposal.md` §10; built at stage 7b) (§1 pillar 3 amended). Old: "Client data never leaves the Studio, except anonymized brief packages the attorney approves." New: "Client data never leaves the Studio, except an anonymized packet for a task on the fixed menu that passed the identifier check on the bytes sent, carries a recorded approval under the mode in force (§9 Dnn), and is logged in the sent-log; the re-identification key never leaves the matter folder." Roadmap: stage 7b. | chair from owner Q52, Q53 (approval mode A, 30 day retention acceptable, Codex second review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D53 | (cloud round-trip proposal P2, `docs/loop/design/cloud-roundtrip-proposal.md` §10; built at stage 7b) (§1 pillar 4 gains a sentence). New: "A cloud model called by code with a fixed card, a fixed schema and no tools is the model filling one step. Codex runs only as a read-only, ephemeral second review over an anonymized packet, never as a source of facts; it is off until the owner enables it." Roadmap: stage 7b. Owner Q53: Codex is the read-only, tool-less second-review critic, off by default (the CLI has no MCP server mode). | chair from owner Q52, Q53 (approval mode A, 30 day retention acceptable, Codex second review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D54 | (cloud round-trip proposal P3, `docs/loop/design/cloud-roundtrip-proposal.md` §10; built at stage 7b) (§2 gains a paragraph after "Brief and motion package"). New: "Cloud round trip. Any task on the menu may run its synthesis step on Claude by API instead of the local model: the engine builds the packet, anonymizes it (casefile-anon/1), checks it, records the approval, sends it, runs the six gates on the reply against the anonymized pages, restores it from the key, runs the restore check against the real pages, and renders the output. Commands: `--engine local/claude`, `cloud on/off`, `cloud log`, `approve <packet>`." Roadmap: stage 7b. | chair from owner Q52, Q53 (approval mode A, 30 day retention acceptable, Codex second review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D55 | (cloud round-trip proposal P4, `docs/loop/design/cloud-roundtrip-proposal.md` §10; built at stage 7b) (§3 gains step 7). New: "7. A task that goes out: packet, entity pass, replace, identifier check, approval, send, gates, restore, restore check, render. A failure at any check stops before the next step; blocked and dropped items are listed, never saved as sent or read." Roadmap: stages 7 and 7b. | chair from owner Q52, Q53 (approval mode A, 30 day retention acceptable, Codex second review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D56 | (cloud round-trip proposal P5, `docs/loop/design/cloud-roundtrip-proposal.md` §10; built at stage 7b) (§4 gains a closing sentence). New: "The gates run on every model answer, local or cloud, before re-identification; a cloud reply is mapped to the local answer shape (`end_turn` is `stop`; `max_tokens` and `refusal` fail gate 1, `refusal` without retry). After re-identification the restore check runs (`gate.restore`): no unknown placeholder, every quote on its real page by the ladder, every cite a page of the packet, firm rules again, line counts unchanged." Roadmap: stage 7b. | chair from owner Q52, Q53 (approval mode A, 30 day retention acceptable, Codex second review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D57 | (cloud round-trip proposal P6, `docs/loop/design/cloud-roundtrip-proposal.md` §10; built at stage 7b) (§5 three new rows). "Cloud client / raw HTTPS to `https://api.anthropic.com/v1/messages` through the same opener as the model client (no proxy, no redirects), key from the `casefile` user's Keychain, model `claude-opus-5-5` unless the benchmark says otherwise, structured output with the card's schema, `cache_control` on card and pages, no tools, no thinking parameter, no temperature; per-run and per-day cost caps; kill switch file". "Sent-log / run log schema v3: `cloud_sends` (packet sha256, bytes, provider, model, approval id, status blocked/sent/failed, tokens, cache reads, cost, request id), append-only; `approvals` written per packet". "Cloud stand-in / `tests/fakecloud/` on 18435 and `tests/fakecodex/`, the modes of §9 of the proposal; a socket guard so no test reaches a real endpoint". And the Anonymizer row amended per Q47: "local model entity pass plus code rules, the matter's name list in the identifier check; Presidio or GLiNER-PII optional as a second detector; the key under `<matter>/anon/`, mode 600, never shared". Roadmap: stage 7 (anonymizer row), 7b (the rest). | chair from owner Q52, Q53 (approval mode A, 30 day retention acceptable, Codex second review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D58 | (cloud round-trip proposal P7, `docs/loop/design/cloud-roundtrip-proposal.md` §10; built at stage 7b) (§7 roadmap). Stage 6 row gains: "cards are engine-neutral: a synthesis card takes a fact packet (facts with quote, cite, page id) and the cited pages, answers in a D34 schema with a cite and quote on every assertion, and uses no Ollama-only feature; the renderer takes the gated answer". Stage 7 row unchanged in intent. New row: "7b. Cloud round trip: cloud client, sent-log, approvals, kill switch, cost caps, cloud stand-in, Codex second review (off) / Loop / the stage 7b exit line of proposal §9, and a seeded leak of each of the 8 kinds blocked with 0 requests". Stage 8 row gains "approve and cloud screens; the sent-log view". Stage 9 gains "`casefile cloud probe` with an invented page against the real endpoint: tokens, cache read, cost, request id". | chair from owner Q52, Q53 (approval mode A, 30 day retention acceptable, Codex second review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D59 | (cloud round-trip proposal P8, `docs/loop/design/cloud-roundtrip-proposal.md` §10; built at stage 7b) (§8b gains a paragraph). New: "The API path. The engine under the `casefile` user calls Anthropic directly for the automatic round trip; it shares the bridge's identifier check, sent-log and approval table but not its tools. The bridge stays for interactive work. A Codex session under the `claude` user may register the bridge with `codex mcp add` and gets the same six tools." Roadmap: 7b and 8b. | chair from owner Q52, Q53 (approval mode A, 30 day retention acceptable, Codex second review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D60 | (cloud round-trip proposal P9, `docs/loop/design/cloud-roundtrip-proposal.md` §10; built at stage 7b) (D13 amended). New `[cloud]` table: `enabled` (default false), `host` (exactly `https://api.anthropic.com`, or `http://127.0.0.1:<port>` for the stand-in; anything else refused), `model`, `context_tokens` (default 200000), `max_input_bytes` (600000), `max_answer_tokens` (16000), `timeout_s` (600), `cost_cap_usd_per_run` (10), `cost_cap_usd_per_day` (50), `approval` (`task/package/standing`, default `package`), `keychain_item`, `key_source` (`keychain`, or `file:<path>` only with a loopback host), `terms_confirmed` (a date, required when enabled), `codex` (default false), `codex_model`. Unknown keys refused as today. Roadmap: stage 7b. | chair from owner Q52, Q53 (approval mode A, 30 day retention acceptable, Codex second review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D61 | (cloud round-trip proposal P10, `docs/loop/design/cloud-roundtrip-proposal.md` §10; built at stage 7b) (D32 amended). Run log schema v3: `cloud_sends` table and its triggers; v2 upgraded in one transaction; the doctor's `runlog_schema` row reports `schema=3`. Roadmap: stage 7b. | chair from owner Q52, Q53 (approval mode A, 30 day retention acceptable, Codex second review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |
| D62 | (cloud round-trip proposal P11, `docs/loop/design/cloud-roundtrip-proposal.md` §10; built at stage 7b) (D20 amended). The privacy row also fails on `sk-ant-` in any tracked or ignored file and on the names `anon/` and `key.json` in the checkout. Roadmap: stage 7b (the row can land earlier at no cost). | chair from owner Q52, Q53 (approval mode A, 30 day retention acceptable, Codex second review); ratified by the owner 2026-10-28 (ledger Q61) | 2026-10-28 |

## §10 Open questions

- Tiers for the loop: keep gdd-loop's (Fable brief, Codex review, Opus orchestrates, Sonnet codes) or
  change for cost? (ask at round 1)
- Which closed matters form the benchmark, and who writes each answer key (owner; names never in this repo).
- 8-bit or full precision: decided by the benchmark.
- Will firm IT allow Tailscale on the office computer?
- Can this macOS unlock FileVault over SSH after a restart (headless Studio)? (§8b)
- Which computer is the "operations computer" for the Inbox and Outbox shares? (§8b)
- Conflict excerpts for Claude review (owner Q41): where records conflict, above all a defense examination against our records, the attorney wants the records around the conflict anonymized for upload to Claude. Which stage builds it (the brief package, spec §2), and how much surrounding text goes with each conflict?
- Uncited pages (owner question 47, round 4): what, if anything, closes a page a passing answer never cites; interim: it stays an open item (D38).
- Summary wording (owner question 48, round 4): label a fact's summary as the model's reading, or judge it against its quote with a second call; interim: no output uses a summary as verified (D38).
- Anonymization convention casefile-anon/1 (owner input, ledger Q47): fixed bracketed placeholders, local model finds names and the anchor date only, code replaces and re-identifies, fail closed both ways, §3 Anonymizer row change; decided in the stage 7 brief and its plan review.
- Round 5 owner questions 50 to 57 (`docs/loop/questions-for-owner.md`): memo sections and order, Word template, cite form, unstamped binders, conflict entries, re-sent open pages, cross-run conflicts (56), binder names against firm rules (57); each held with a fail-closed interim (D41).

## §11 As-built

| Part | State |
|---|---|
| Stage 1 (round 1, merged 2026-10-26) | built and verified: `scripts/run.sh` and `scripts/run_capture.py` (D12), `src/casefile/` config (D13), pathguard (D24), rules and `playbook/rules.toml` (§4, Q16), playbook loader, append-only run log, model client (loopback, no proxy), doctor (D19, eight checks), privacy scan and gate; stand-in model server `tests/fakemodel/` (D18); 233 tests, gate prints 0; stage 1 exit test `exit=1 verdicts=8 fails={'ocr'} test_jobs=1` (OCR FAIL until stage 3, Q11) |
| Stage 2 (round 2, merged 2026-10-27) | built and verified: quote normalisation (`quotes.py`), matter loader (`matter.py`), answer key (`benchkey.py`), candidate parser (`benchcandidate.py`), scorer (`benchscore.py`), stage 2 runner with fixed card `bench.extract` (`benchrun.py`, every received reply an answer row), `casefile bench` (`bench.py`, D25: exit 0 perfect, 1 imperfect, 2 cannot run, with detail lines); invented matter `tests/fixtures/matters/9001.001` (14 pages, three binders) with `key.json` (29 facts, 6 flags), `ideal.json` and `tests/fixtures/bench/flawed.json`; stand-in bench recording; prose gate covers fixtures (D26); code by gemma4:e4b-it-qat (Q28), the V2b-F1 fix by Sonnet (Q33); 270 tests, gate prints 0; stage 2 exit test `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`; flawed `found=26 of 29 ... flags=5 of 6 ...` exit 1, ideal `found=29 of 29 ... flags=6 of 6 ...` exit 0. Deferred: prompt truncation detection (R2-CX-2) to stage 4 |
| Stage 3 (round 3, merged 2026-10-27) | built and verified: `casefile intake` (`intake.py`, D27), `stamps.py` (every stamp raw and normalised, none chosen, whole tokens only; Q35, Q40), doctor OCR on a generated image-only smoke page (D29), `pdfsmoke.py`, invented scanned binder `tests/fixtures/scanned/` (matter 9002.001, 6 pages); bench exit 2 on no reply and `model=` on the line (D28, D30); key 29 facts, 9 flags (Q36, Q41); 358 tests, gate prints 0; stage 3 exit test `stage3 exit=1 pages=6 ids_ok=6 of 6 stamps_ok=6 of 6 text_ok=6 of 6 must_ok=5 of 5 empty=1 failed=0 min_ratio=1.000`; stage 1 exit test now `exit=0 verdicts=8 fails=set() test_jobs=1` |
| Stage 4 (round 4, merged 2026-10-28) | built and verified: model client (`truncate` and `think` sent only by the gate pipeline, cached count read, UTF-8 byte budget, D31); `gates.py` (the six §4 gates in order, retry once as a fresh prompt, `Outcome.answer` None on failure, coverage `read`, `uncited`, `failed`, plain failure reasons naming the cited page; D31, D38); `quotes.py` ladder on token boundaries (D35, Q44); `jsonrepair.py` punctuation only, duplicate keys refused (D33); `schema.py` stdlib subset validator, 20 schemas load (D34); run log schema v2 with `coverage` and `gates`, 21 triggers, v1 upgraded in one transaction (D32); stand-in 17 modes (D36); bench on the ladder, duplicate numbers refused up front, `stamps.compile` (D37); `scripts/suite_time.sh`; 537 tests, gate prints 0; stage 4 exit test `stage4 exit=0 gates=6 of 6 cases=14 of 14 runs=+14 answers=+21 empty_saved=0 server_stopped=1` |
| Stage 5 (round 5, merged 2026-10-28) | built and verified: `extract.py` (the extraction card in production, version 4ab2bdb30535); `pages.py` and `pipeline.py` (pages from either layout, chunks by bytes with a retry margin, only unread pages sent per job); bench on the pipeline (`benchrun.py` removed, D39); `facts.py` case file (hash-chained append-only JSONL, torn tail recovered, fold identity, matter lock, D40); `memo.py` and `casefile memo` (Word via python-docx, quote as the verified text, every model sentence labelled, conflicts and gaps with cites, open items by stamp, firm-rule self-check, D41); `casefile status` (D43); cites in summaries checked as references, unbracketed cite forms (D42, R1-20); 652 tests, gate prints 0; stage 5 exit test `stage5 exit=0 runs=4 of 4 memos=3 of 3 answers=+4 casefile_lines=48 chain_ok=1 server_stopped=1` |
| Stage 6 (round 6, merged 2026-10-28) | built and verified: one card loader (`cards.py`, manifest v2: 15 cards, 11 schemas, JSON only, engine neutral; practice from `playbook/deposition.toml` and `hearing.toml` ported from the firm skills, filtered by kind and deponent; D44, D45); facts carry date, category, provider, each verified on the cited page (D46); old case files upgraded in place (D51); `roles.py` (defense by binder name: DME, IME, defense medical; Q57); `matterinfo.py` (header and issues asked once at the first task run, stored in `matter.toml`; Q57); `packet.py`, `outputs.py`, `report.py`, `depo.py`, `hearing.py` (`casefile report`, `depo`, `hearing`: packet, one gated step per card, `render(answers, ...)` from the gated JSON only; a failed step writes `.partial.docx`; reasons checked by the rules and withheld on a hit; D49); memo in spec §2 sections with conflict quotes, defense against ours first (D48); rules: fee for a deposition and how often retained blocked, the bills question to our doctor exempt (Q59 b, c; D50). Reconcile pass withdrawn (Q55, D47). Exit test `stage6 exit=0 docs=6 of 6 answers=+16 rule_hits=0 server_stopped=1` |
| Rest of §5 | not built |
| Cards and schemas | rewritten in round 6 (see Stage 6); the stage 8 cards are carried unchanged |
