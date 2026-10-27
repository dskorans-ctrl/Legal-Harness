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
2. Intake: OCR where needed; every page gets an ID (matter, binder, page, Bates if stamped).
3. Cards: pages are split into chunks well inside the context; the right card runs on each chunk.
4. Gates (§4) on every answer.
5. Merge into the append-only case file: a repeated fact adds a cite; added detail adds a version;
   disagreement is kept as a conflict for the attorney.
6. Outputs are built from the case file, never from a chat, and download as Word documents.

## §4 Gates (every model answer, in order)

1. Truncation: the answer did not stop early, and the model read as many tokens as were sent.
2. JSON repair, punctuation only (control characters, trailing commas, missing closers).
3. Schema check against the card's schema.
4. Quote check ladder: exact, then whitespace, then curly versus straight quotes, then OCR faults
   (ligatures, line-break hyphens, running headers); otherwise rejected with the pages searched.
5. Firm rules check (`rules.toml`), on outputs only: never "DME", "IME", "independent medical
   examination" or "defense medical examination" (say "the report"); never who hired, paid or
   retained the doctor, fees or exam volume; treatment and bills never in one question; Bates cites,
   with a warning when records are not stamped.
6. Coverage ledger: a page counts as read only when all of the above pass.

A failure is retried once with the error shown; then the pages are marked failed and listed as open
items. Never saved as empty.

## §5 Parts, and what is reused

| Part | Built with |
|---|---|
| Job runner, one job at a time, Cancel stops model call and OCR together | Python, SQLite |
| Intake and OCR | Docling (layout, tables), ocrmypdf and Tesseract |
| Model client | Ollama native API (`/api/chat`, never the OpenAI-compatible route), Qwen3.8-27B, `num_ctx` 65536 in the Modelfile and on every call, low temperature, thinking mode per card, stable prompt order (rules and card first, page text last) |
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

## §10 Open questions

- Tiers for the loop: keep gdd-loop's (Fable brief, Codex review, Opus orchestrates, Sonnet codes) or
  change for cost? (ask at round 1)
- Which closed matters form the benchmark, and who writes each answer key (owner; names never in this repo).
- 8-bit or full precision: decided by the benchmark.
- Will firm IT allow Tailscale on the office computer?
- Can this macOS unlock FileVault over SSH after a restart (headless Studio)? (§8b)
- Which computer is the "operations computer" for the Inbox and Outbox shares? (§8b)

## §11 As-built

| Part | State |
|---|---|
| Stage 1 (round 1, merged 2026-10-26) | built and verified: `scripts/run.sh` and `scripts/run_capture.py` (D12), `src/casefile/` config (D13), pathguard (D24), rules and `playbook/rules.toml` (§4, Q16), playbook loader, append-only run log, model client (loopback, no proxy), doctor (D19, eight checks), privacy scan and gate; stand-in model server `tests/fakemodel/` (D18); 233 tests, gate prints 0; stage 1 exit test `exit=1 verdicts=8 fails={'ocr'} test_jobs=1` (OCR FAIL until stage 3, Q11) |
| Stage 2 (round 2, merged 2026-10-27) | built and verified: quote normalisation (`quotes.py`), matter loader (`matter.py`), answer key (`benchkey.py`), candidate parser (`benchcandidate.py`), scorer (`benchscore.py`), stage 2 runner with fixed card `bench.extract` (`benchrun.py`, every received reply an answer row), `casefile bench` (`bench.py`, D25: exit 0 perfect, 1 imperfect, 2 cannot run, with detail lines); invented matter `tests/fixtures/matters/9001.001` (14 pages, three binders) with `key.json` (29 facts, 6 flags), `ideal.json` and `tests/fixtures/bench/flawed.json`; stand-in bench recording; prose gate covers fixtures (D26); code by gemma4:e4b-it-qat (Q28), the V2b-F1 fix by Sonnet (Q33); 270 tests, gate prints 0; stage 2 exit test `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`; flawed `found=26 of 29 ... flags=5 of 6 ...` exit 1, ideal `found=29 of 29 ... flags=6 of 6 ...` exit 0. Deferred: prompt truncation detection (R2-CX-2) to stage 4 |
| Rest of §5 | not built |
| Cards and schemas | written for the earlier two-model plan; updates listed in §7 |
