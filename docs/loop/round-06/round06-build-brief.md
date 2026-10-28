# Round 6 build brief: stage 6 outputs, cards and schemas (R6-1 to R6-4)

Revised 2026-10-28 after the adversarial plan review (`docs/loop/round-06/round06-brief-review.md`, dispositions in
§8) and the owner's Q53 constraints (ledger `## Clarified` Q52, Q53; `docs/loop/design/cloud-roundtrip-proposal.md`
§13): output cards are engine-neutral (a fact packet of facts with quote, cite and page id plus the cited pages in;
a D34 schema with a cite and quote on every assertion out; no Ollama-only feature in card text), the anonymization
card finds names and the anchor date only and passes on an empty answer, and the deposition, hearing and report
renderers take the gated JSON answer (`render(answers, packet, ...)`), never the model call. Nothing else from the
proposal is built this round.

Amended 2026-10-28 on the owner's answers to questions 59 to 69 and the new direction (ledger Q54, Q55, Q56; §9
lists every change): the local model files and anonymizes; Claude does fact finding and synthesis from the
anonymized whole matter when the attorney runs a task; nothing runs continually. Round 6 keeps the engine-neutral
outputs exactly as revised, drops the reconcile pass (D47 withdrawn, superseded by stage 7b's whole-matter
re-send), adds no continually-updated-memo behaviour, lets the bills question pass as the skill writes it (Q59 b
and c), takes the header and the issues from the attorney at the first task run and stores them in `matter.toml` (Q57, superseding Q54 item 60), reads binder roles from binder names with a typed override for multi-plaintiff matters (Q57), stores standard and relief in `matter.toml` (Q62), finds the doctor's records by provider (Q61), and upgrades
old case files on load (Q67).

Branch `loop/round-06` at `53a6f82` (working tree: modified `.workflow/LEDGER.md`, `docs/loop/agent-log.md`,
`docs/loop/questions-for-owner.md`, `docs/spec.md`; untracked `.agents/`, `.claude/worktrees/`, `AGENTS.md`; leave
them, the chair commits the records). Scope: ledger R6-1 (spec §7 stage 6: "Word documents built from the test matter
pass the output critic"), R6-2 (the `cards/` and `schemas/` rewrite), R6-3 (owner answers Q49: 56, 50, 54, 57), R6-4
(round 5 verifier L1, code review L3; M4 stays a recorded limit, §1.13). Tiers (owner Q46): Opus 5.5 orchestrates and
runs the output critic and the blind verifier; Codex `gpt-6.1-sol` through `codex exec -s workspace-write -c
sandbox_workspace_write.network_access=true` writes every line of code and every fix (builders do not commit; the chair
re-runs every CHECK and seed, runs the gate and commits); fresh Fable agents do the plan review and the code review;
Fable writes and revises the brief. Privacy: every page, name, stamp, quote, answer, date and number below is invented
(§6b); the firm skills were read for their practice rules only and no example, name, date or fact from them appears
here or in any fixture. The model is the stand-in `tests/fakemodel/` in every test and probe; nothing reaches
127.0.0.1:11434 (`tests/conftest.py:45` default host `http://127.0.0.1:9`).

Measured on the tip 2026-10-28 by this architect, inside the sandbox, through `scripts/run.sh`: `python -m
casefile.gate` prints `0` with `gate pytest PASS exit=0` (`652 passed in 57.68s`), `gate privacy PASS offenders=0
scanned=757`, `gate rules_selftest PASS misses=0 false_hits=0`, `gate playbook PASS invalid=0 unmarked=0
version=pb-ca16b0882a97`, `gate prose PASS dashes=0 files=193`. Probes with the project interpreter are quoted where
used (D0.9, D0.10).

## §0 Drift since the round 5 close (every premise verified in the code on `53a6f82`)

- D0.1 **Owner answers landed after the close, uncommitted.** Ledger `## Clarified` Q49 to Q51 (round 6 check-in) and
  `## Round 6` R6-1 to R6-4; `docs/spec.md` §9 D31 to D43 now read `ratified by the owner 2026-10-28 (ledger Q50)`;
  `docs/loop/questions-for-owner.md:307-310` records 56, 50, 54, 57 answered and the rest kept. Nothing in `src/`,
  `tests/`, `cards/`, `schemas/` or `playbook/` changed since `53a6f82` (`git diff --stat`: four record files only).
- D0.2 **The owner's direction (ledger Q52 to Q56) and what stage 5 behaviour stays this round.** The cloud round
  trip is stage 7b after the anonymizer; Claude reads the anonymized whole matter per task run (Q55), so cross-run and
  cross-chunk conflicts are closed there and the reconcile pass is withdrawn here. Stage 5 behaviours that stay as
  built in round 6 (no item needs them removed, and removing working code without a replacement would leave the
  memo exit test without a subject): `casefile memo` as a task the attorney runs (`memo_job.py:81-104`), its
  only-unread chunking (`memo_job.py:36-39`) and the re-send of open pages on every run (T-21, Q55 item 55), the
  `What changed since the last memo` and `Outputs out of date` sections (`memo.py:88-101`), the coverage ledger and
  `casefile status`. Stage 7b's brief retires the first three (a task run sends the whole anonymized matter; a memo
  is rebuilt from that answer) and decides whether `What changed` survives; `Outputs out of date` stays useful
  (spec §2). Nothing continual is added this round: no watcher, no scheduled run, no reconcile call after a chunk.
- D0.3 **The extraction card is a string in code, not a card file.** `src/casefile/extract.py:10-19` `CARD_TEXT`,
  `:20-22` `ID_SENTENCE`, `:24` `CARD_NAME = "bench_extract"`, `:27-31` `card()` loads
  `schemas/bench_extract.schema.json`; version `4ab2bdb30535`, 920 bytes (`tests/test_extract.py:19,24`). Facts carry
  `cite`, `quote`, `text` only (`schemas/bench_extract.schema.json:12-16`): no date, no category, no provider. No code
  reads `cards/` (`grep -rn "cards/" src tests` hits only `tests/test_prose.py:18`, an exclusion); `cards/manifest.json`
  still lists 45 cards with `tier` LOCAL, LOCAL_REVIEW or STRONG, `temperature` and `max_material_tokens`
  (`manifest.json:3` "Tier STRONG cards should run on a stronger model or be done by the attorney"), 18 of them with
  `"output": "markdown"` and `"schema": null` (an answer the schema gate of §4 rule 3 cannot check). `cards/_core.md:10`
  says `Write "Dr. [Name]'s report"` while `playbook/rules.toml:9` says `write "the report"`: two rule texts. The 20
  schemas load in the D34 subset today (`tests/test_schema.py:137-148`, `schemas_loaded=20 of 20`); `encounters.schema.json`
  (the old 01-P1 card) holds a 22-value `category` enum and `date_of_service` object the gates never saw.
- D0.4 **Callers of the card name and version.** `extract.card()`: `src/casefile/pipeline.py:92`, `memo_job.py:32`,
  `status.py:26` (`card_name` keys the coverage rows); tests `test_stage5_exit.py:72,110,162`, `test_memo_intake.py:31`,
  `test_fakemodel_bench.py:14`, `test_bench_pipeline.py:202`, `test_status.py:78,171,184`, `test_pipeline.py:31,79,81,130`,
  `test_gates.py:87,304,509`, `tests/fakemodel/bench.py:10-11,25`. The literal `bench_extract`: `tests/test_stage4_exit.py:125,137`,
  `test_memo.py:46`, `test_facts.py:39`, `test_gates.py:295-296`, `test_pipeline.py:60,65`, `test_schema.py:12,40`,
  `test_extract.py:20`; spec D34 and D39. `recordings_for` (`tests/fakemodel/bench.py:21-26`) builds the one recording
  from `ideal.json` at test time, so a card text change re-records itself; `tests/fakemodel/recordings.json` holds only
  `doctor-warmup` (measured, 1 row).
- D0.5 **The gates assume one card shape.** `gates.py:20-33` `Card(name, text, schema, unit="text", think=False,
  max_answer_tokens=8192)`; `:56-60` `messages` always renders `extract.page_block` per page; `:256-262` gate 5 runs
  `rules.check(value, unit=card.unit, ...)` over every string with one unit; `:263-273` gate 6 fails when `not
  obj.get("facts") and not obj.get("flags")` and blank-checks `facts[].text/quote` and `flags[].about/cites` by name;
  `:313-322` writes a coverage row (`read`, `uncited`, `failed`) for every page passed in; `:143-149` the digit-run
  check reads `facts[i].text` against `facts[i].quote`. A card whose answer has no `facts` key, or whose legitimate
  answer is empty, or whose pages must not be marked read, cannot run through `ask` today.
- D0.6 **The case file's fact payload is fixed by name.** `facts.py:53-62` `FIELDS`: `fact` = `{id, cite, page_id, quote,
  text, run_id}`, `cite` = `{fact, cite, page_id, run_id}`; `:172-178` refuses any line whose payload keys differ
  (`_broken`), so adding fields refuses every case file written before the change. `Fact` (`:35-42`) has no date,
  category or provider. `merge` (`:238-285`) keys facts by `quotes.fold(quote)` and flags by `(kind, sorted page ids)`.
- D0.7 **The memo as built (D41).** `memo.py:85-154` `build`: sections `What changed`, `Outputs out of date`, `Open items`,
  `Conflicts` (`:105-108` the sentence `Pages read in N run(s); conflicts and gaps are checked only between pages sent to
  the model together.`), `Gaps and missing records`, `Verified facts by record` (`:131` heading
  `{page.binder.capitalize()} page {label}`), `Facts on pages not in this matter`; `:110-116` one entry per flag in
  case-file order, no quotes beneath; `:164-171` `check_binders` refuses a binder whose name fails a rule at `error`
  (owner Q57 withdrew this: `test_status.py:112-129` `binder_refused=1` and `test_memo.py:236-248` `memo_refused=2 of 2`
  pin the refusal; `:192` `render` calls `check_binders` too); `:174-188` `check` replaces any run with a non-empty
  `exempt` by a newline (`:180-181`), so new exemption names need no change to `check`; today only `quote` and
  `reason` runs are marked, and `_cite` (`:55-56`) builds cite runs unmarked, so a cite run `[page ime/001]` of a
  binder named `ime` would hit `\bIME\b` (probe: `Rules.check("ime page DEF0001 (ime/001)")` gives two `no-dme-ime`
  errors). `memo_job.py:36-50` runs the chunks and merges; `:58-59` builds; `:98-100` prints `memo: cannot run: no
  reply from the model server at <host>: <exc>` where `<exc>` already starts `no reply from the model server (...)`
  and ends `the page stays open until a later run reads it` (`model.py:57-58`; verifier L1). Pins of that clause:
  `tests/test_bench_pipeline.py:90`, `test_fix_cycle2.py:127` (doctor), `test_bench_cli.py:123,210`; the gate's own
  clause at `gates.py:315` is a different string and stays.
- D0.8 **Bench shapes.** `benchcandidate.py:44-47` refuses a fact with keys other than `{cite, quote, text}`;
  `benchkey.py:60-62` requires exactly `{id, cite, quote, text}`; `benchscore.py:41-45` prints the line; the bench
  line is pinned in seven test files (`test_bench_cli.py`, `test_bench_detail.py`, `test_bench_discovery.py`,
  `test_bench_multi.py`, `test_bench_pipeline.py`, `test_benchscore.py`, `test_stage2_exit.py`). `ideal.json` holds 31
  facts (the 29 key facts plus `EMP0001 "Date of hire: 08/02/2021"` and `EMP0002 "Lift up to 50 pounds repeatedly during
  the shift."`) and 9 flags; `flawed.json` 30 and 9. The three-chunk split test (`test_bench_pipeline.py:200-222`)
  pins `[5, 5, 4]` with `max_answer_tokens = 65536 - 16384`, which depends on the card's byte size (the page budget is
  `16384 - 64 - 8192 - system bytes - 16`; with the 920-byte card that is 7164 bytes); `:225-241` pins `(29, 29, 5, 9,
  3)` and `flags_missed: G1 G3 G6 G9`: all four lost flags are conflicts (`key.json` G1 MED0001/EMP0001, G3
  MED0008/DEF0003, G6 MED0007/DEF0002, G9 MED0006/DEF0002); no gap is lost by chunking on this fixture.
- D0.9 **The firm rules against the firm skill's own wording (probed through `playbook.load`).** The deposition skill's
  suggested treatment question (its §1, placeholders filled with invented providers) returns `no-hired-paid-retained`
  (excerpt `Doctor, you were provided a bill memo listing charges`: rule pattern 3 pairs `charges` with `doctor` within
  60 characters, `rules.toml:24`) and `treatment-and-bills-apart` (`bill memo listing charges ... Ridgeline Physical
  Therapy`); its suggested bills question returns both rules too, the conjunction because the provider name `Ridgeline
  Physical Therapy` satisfies `\btherapy\b` in the treatment group (`rules.toml:43`). The seed card's treatment question
  (`cards/02-depo/c-our-doctor.md`, no bill word) returns `[]`; a bills question naming only non-therapy providers and
  saying `bills` rather than `charges` returns `[]`; one naming a physical therapy provider returns the conjunction
  error. The rules miss `What is your fee for this deposition?`, `How often does the carrier retain you?`, `How many
  times has this firm hired you?`, `Is there a fee for your testimony today?` and `What percentage of your practice is
  examinations for employers?` (all `[]`), which the skill's §2 forbids. Must-pass controls today: `When were you hired
  by Quarry Ridge Logistics LLC?`, `How much time did you spend face to face with the claimant?`, `Do you currently
  treat patients with low back injuries?`, `What share of your practice is treating patients?` all `[]`.
- D0.10 **Other wording probes.** `Attorney Work Product | Privileged & Confidential`, `Deposition of the defense
  doctor, taken by us`, `Conflicts between a defense examination binder and our records come first.`, `Dr. Marchetti's
  report records a normal gait. [cite DEF0002]`, `Danger zone: findings that cut both ways`, `Points for our expert`,
  the starred billing memo sentence and `Totals: not on file; the billing memo is supplied by the attorney.` all
  return `[]`; `[page medical/001]` is a `bates-cites` error when `stamped=True` and a warning when `False` (as D42).
- D0.11 **Practice lives outside the repo.** `playbook/` holds the four rules and three SAMPLE entries
  (`playbook/samples/depo-goals.toml`); `playbook.py:72-73` refuses any entry with `sample` not `true` or `rule` not
  starting `SAMPLE:` (D17); `playbook.py:12` `KINDS = depo-goal, topic-order, question, hearing, checklist, rule`;
  `gate.py:40-47` counts `unmarked`. The firm's `deposition-prep` and `workers-comp-hearing-prep` skills (read this
  round for rules only) hold the practice spec §6 says the playbook is the one source of (D7). Rules taken from them:
  deposition §1 (two separate questions, treatment then bills, the second anchored on the bill memo by name with the
  provider list; for the defense examiner, concessions on each as two questions in the report's own words), §2 (cross
  on documents, his own words and his process, never on medicine; nine tests; forbidden: who hired, retained, how
  often, exam counts, practice share, employer versus claimant split, fees for exam, report or deposition; allowed:
  current treating practice and face time, short and leading; use instead: concessions, consistency, internal
  contradictions, omissions in his review, accurate quotation, undefined labels asking what never why, process on the
  face of the report; questions short, leading, one fact each, tied to a Bates cite; medicine from our expert in a
  "Points for our expert" section; a marked danger-zone section), §4 (Word deliverables, Bates cites, page:line for
  transcripts, verbatim marked apart from designated, the header block: Attorney Work Product | Privileged &
  Confidential, caption, IAB hearing number, date of accident, deposition date and time, hearing date; no em dashes);
  hearing §1 (the starred billing memo item first in every checklist, itemized by provider, date range and balance
  with a grand total when known) and §2 (the same conventions, header with hearing date and time). The
  motion-brief-memo-drafting skill governs voice for stage 7's re-import and is not used this round beyond its
  no-em-dash rule, which the prose gate already enforces.
- D0.12 **What a matter knows about itself.** `matter.toml` holds `number` and `binders` only (`matter.py:60-61`
  refuses other keys); the intake layout has no matter file at all and `pages.py:88-89` refuses a folder with both
  `matter.toml` and `pages/`. Nothing records which binder is a defense examination (Q41, Q54: "the code can tell
  binders apart only by the names you give them"), the caption, the IAB number, the date of accident or a hearing
  date. `intake.py:30` `BINDER_PATTERN = r"[a-z][a-z0-9-]{0,39}"`. The seed card `00-PROCEDURAL`
  (`cards/00-intake/procedural.md`, `schemas/procedural.schema.json`) extracts a filing's type, date, filer and
  deadlines with a quote and cite, but no caption, hearing number or accident date, and its schema carries a
  model-written `coverage` string. The fixture matter's invented parties are `Morgan Ashby-Vale` and `Quarry Ridge Logistics LLC` (`records/employer/001.txt`), its invented accident date `03/11/2025`; it stays 14 pages this round (Q57).
- D0.13 **Numbering.** Spec §9 ends at D43; owner questions end at 80 (59 to 69 are this brief's, 70 to 80 the
  cloud proposal's, §12 of that file; W9 renumbers nothing; this revision adds no question); tuning at T-22; ledger round 6 has R6-1 to R6-4;
  worktrees `r3-lane-b`, `r4-lane-b`, `r5-lane-b` and their toolchains under `~/.casefile-dev/` still exist (HANDOFF
  leftovers); `.workflow/scratch/` is gitignored (this file). Stand-in `MODES` is 17 (`tests/fakemodel/core.py:12-14`,
  pinned at `tests/test_fakemodel.py:151`); no mode is added this round.

## §1 Decisions, with trade-offs

- **1.1 Practice enters the playbook as owner entries; cards are built from it.** Spec §6 and D7 make the playbook the
  one source for cards and the Claude skills; today the skills hold the practice and the playbook holds samples
  (D0.11). This round ports the rules of D0.11 into `playbook/deposition.toml` and `playbook/hearing.toml` as entries
  with `sample = false`, `learned = "firm skill deposition-prep section N"` (or `workers-comp-hearing-prep`), `good`
  and `bad` written from the rule with placeholders or invented names only. `playbook.py:72-73` changes: `sample =
  true` still requires `rule` to start `SAMPLE:`; `sample = false` requires `rule` not to start `SAMPLE:` and `learned`
  to start `firm skill ` (the owner's authored source, D17's "owner content"); every other field rule is unchanged.
  `gate.py:40-47` prints `playbook PASS invalid=0 unmarked=0 practice=P samples=3 version=...` where `unmarked` counts
  entries violating either marking rule. The card loader (§1.2) places into a card only entries with `sample = false`
  whose `kind` is in the card's `kinds`: invented samples never enter a prompt. Entries (ids fixed so the cards and
  tests can name them): `our-doctor-treatment-and-bills` (depo-goal, deponent our-doctor), `defense-doctor-two-concessions`
  (depo-goal, defense-doctor), `defense-doctor-documents-not-medicine` (depo-goal, defense-doctor; the nine tests as
  numbered sentences), `defense-doctor-no-defense-work` (depo-goal, defense-doctor), `defense-doctor-practice-allowed`
  (depo-goal, defense-doctor), `defense-doctor-use-instead` (topic-order, defense-doctor), `question-form` (question),
  `points-for-our-expert` (depo-goal), `danger-zone` (depo-goal), `header-block` (hearing), `billing-memo-first`
  (checklist), `transcript-cites-page-line` (hearing), `verbatim-marked-apart` (hearing): 13 entries. The seed cards'
  own lists (the our-doctor topic order of `c-our-doctor.md`, the client topics of `c-client.md` and
  `client-prep.md`, the 14 elements of `a-elements.md`, the concession types of `g-concessions.md`, the client
  instruction block of `client-prep.md`) stay card text as they are today (they were in the repo at the seed and no
  owner ruling changed them; question 68 asks the owner to confirm them). Rejected: hard-coding the skill rules in card
  files (spec §7 "card text built from the playbook"; D7 wants one source so the update packet can regenerate the
  skills); reading the skills at run time (outside the repo, absent on the Studio); leaving the practice out (then the
  outputs would be decided by taste, which the round rules forbid). Risk owned: a Fable agent ported practice text; the
  chair reads every entry against the skill before the lanes split and the owner can veto any entry (D45).
- **1.2 Cards are JSON-only, loaded by one loader, the practice injected at load time; 30 cards retire.** Every model
  answer passes the schema gate (spec §4 rule 3, D34), so a card with `"output": "markdown"` cannot run; its prose is
  the attorney's deliverable, which code assembles from verified material (pillar 4). New `src/casefile/cards.py`:
  `load(root) -> dict[str, Spec]` reads `cards/manifest.json` version 2 (`{"version": 2, "cards": [{"id", "title",
  "file", "schema", "job": "memo"|"depo"|"hearing"|"report"|null, "stage": 6|7|8, "kinds": [...], "deponent":
  "our-doctor"|"defense-doctor"|"client"|"witness"|null, "question_keys": [...], "numbers_in": "quote"|"page",
  "required_any": [...], "optional_blank": [...], "echo": "compared"|"pages_seen"|null, "coverage": bool}]}`, unknown
  keys refused, every file and schema must exist, every schema loads through `schema.load`); `text(spec, book) ->
  str` = the core block rendered from `rules.toml` (`Firm rules:` then one line per rule in `RULE_IDS` order: `<n>.
  <rule.rule>`, plus the fixed lines `Use only the text in this request.`, `Never guess, infer or fill in; leave out
  what is not on the page.`, `Copy qualifiers, sides, dates, numbers and checkbox marks exactly as written.`, `Say who
  said it.`, `Do only the job on this card.`), then the card file's body, then `Practice:` with one block per entry
  whose `kind` is in the card's `kinds` and whose `deponent` is absent or equals the card's `deponent` (review M4: a
  defense-doctor rule never enters the our-doctor, client or witness cards; `question-form` carries `deponent =
  "defense-doctor"`, its source section) (`- <rule> Good: <good> Bad: <bad>`), then `extract.ID_SENTENCE` reworded
  engine-neutral: `The first key is "prompt_id" and the last key is "end_id", both holding the prompt_id value given
  in this request.` (review L3; no sentence in any card names a message layout, a server or a model); `card(id,
  book) -> gates.Card`. Per-card blank rules (review H3): gate 6 blank-checks every string of every item except the
  keys in `optional_blank`; `echo` names the key whose array must equal the ids or page ids the request listed
  (`pages_seen` for `07-ANON`; `compared` was the withdrawn reconcile card's), and a card with an `echo` passes gate 6 on empty
  arrays (review M3). `cards/_core.md`
  is deleted (its text is generated; the `Dr. [Name]'s report` line of D0.3 goes with it). `Card.version` stays the
  sha256 of the text, so a playbook edit changes every card version (spec §6: the affected cards run on the
  benchmark). Manifest after the round (15 cards, 11 schemas): run this round `01-MEMO` (`cards/01-records/memo.md`,
  `schemas/medical_memo.schema.json`, job memo; the reconcile and header cards of the earlier drafts are withdrawn, §1.4 and §1.5), `02-A` (`cards/02-depo/a-factsheet.md`, `schemas/factsheet.schema.json`, jobs depo and hearing),
  `02-C-CLIENT`, `02-C-DEFDOC`, `02-C-OURDOC`, `02-C-WITNESS` (`schemas/questions.schema.json`, job depo),
  `03-CLIENT` (`cards/03-hearing/client-prep.md`, questions schema, job hearing), `04-G` (`cards/04-defense-report/g-concessions.md`,
  `schemas/concessions.schema.json`, job report), `05-A` (`cards/05-our-doctor/a-elements.md`, `schemas/elements.schema.json`,
  jobs report and hearing); stage 7 `07-ANON` (`cards/07-anonymize/entities.md`, `schemas/anonymize.schema.json`,
  new); stage 8, text untouched but loaded and versioned, `00-BILLS`, `00-CLASSIFY`, `00-TESTIMONY`,
  `01-P0` (their five schemas unchanged). Retired (deleted; their text
  stays at `53a6f82`): the 17 markdown cards
  other than `03-CLIENT` (`00-ATTORNEY`, `00-CHANGE`, `00-SNAPSHOT`, `01-P4`, `01-P5`, `02-B`, `03-CHECKLIST`,
  `03-CLOSING`, `03-DOCTOR`, `03-OUTLINE`, `04-H`, `05-D`, `06-A`, `06-B`, `06-C`, `06-D`, `06-F`, with
  `cards/06-brief/_brief-rules.md`), and 13 JSON cards whose check the gates do in code (`01-P2`, `02-D`: Q48 interim
  and gates 4 and 5), whose work is code from the case file (`03-ISSUE` = factsheet, `03-CONSIST`, `04-A`, `04-B`,
  `04-F`, `05-C` = conflicts and facts by category), or whose job is later work not yet designed (`04-C` records
  audit, `04-D` summary accuracy, `04-E` opinion basis, `05-B`, `06-E` the authority check, D3). Schemas removed with
  them: `cite_verify`, `comparison`, `encounters`, `opinion_basis`, `qverify`, `records_audit`, `report_map`,
  `summary_accuracy`, `verify`; `bench_extract.schema.json` is renamed `medical_memo.schema.json`. Spec §7's "drop
  three, add two" becomes this list (D44, §6). `extract.card()` returns `cards.card("01-MEMO", book)` (name
  `medical_memo`); `extract.CARD_TEXT` and `TEXT` go, `ID_SENTENCE`, `page_block`, `prompt_sha256` stay. The
  anonymization card lands in `cards/07-anonymize/` with the Q47 convention's job (names and the anchor date only, one
  quote and cite per hit; code does every replacement) so the cards and schemas are complete and loadable; its
  answer `{"pages_seen": [every page id sent], "people": [...], "organizations": [...], "places": [...],
  "anchor_dates": [{date, quote, cite}]}` is valid with every array but `pages_seen` empty (the identifier check's
  second pass wants exactly that answer, proposal §4; review M3); no job runs it this round and the stage 7 brief may
  amend it. Measured: `tests/test_cards.py` prints one `card <id> version=<12
  hex> schema=<title>` line per manifest entry and `cards_loaded=15 of 15 schemas_loaded=11 of 11`; the memo card's
  bench effect is §1.3's `dates_wrong`; the output cards have no
  answer key, so their measure is the stage 6 exit test's counts and the output critic (spec §7). Rejected: keeping 45
  files with a `tier` the single model ignores and `max_material_tokens` D31 replaced (dead text misleads builders:
  #R03-PC-3); a manifest per stage (one loader, one gate).
- **1.3 The medical memo card gives each fact a date, a category and a provider; date and provider are verified on the
  page; category is a labelled enum (Q50).** `schemas/medical_memo.schema.json`: facts `{cite, quote, text, date,
  category, provider}` all required strings, `category` an enum of 24 (`mechanism_of_injury`, `chief_complaint`,
  `pain_score`, `prior_history`, `family_history`, `comorbidity_social`, `exam_finding`, `imaging_result`,
  `diagnostic_test`, `diagnosis`, `treatment_rendered`, `medication`, `procedure`, `order_or_referral`,
  `work_status`, `mmi_statement`, `causation_statement`, `impairment_rating`, `future_treatment`, `patient_statement`,
  `compliance`, `records_referenced`, `employment`, `other`; T-23); flags unchanged. The card text (`cards/01-records/memo.md`)
  says: `date` is the date of service of the record the page belongs to, copied exactly as written on the page (not a
  print, fax or signature date), empty when the page shows none; `provider` the provider or facility name as written
  on the page, empty when none; `category` one of the list. Gate 4 (`gates._references`) gains: a non-empty `date`
  must match the cited page by the ladder (`quotes.match`) and parse by new `src/casefile/dates.py` `parse(text) ->
  date | None` over `MM/DD/YYYY`, `M/D/YYYY`, `YYYY-MM-DD` and `Month D, YYYY` (full month names, any case), else the
  fault `facts[i].date: <value> is not a date written on <page label>` or `... is not a recognised date form`; a
  non-empty `provider` must match the cited page by the ladder, else `facts[i].provider: not on <page label>`. The
  case file (D40 amended): `fact` payload gains `date`, `category`, `provider`; `cite` payload gains `date` and
  `provider` (the pair fact and page carries its own date, as readings carry their page: #R05-CX-5); `Fact` gains
  `dates: list[str]` (parallel to `cites`), `category: str`, `providers: list[str]`. Old case files are upgraded on load (owner Q54 item 67): `facts._decode`
  accepts a `fact` payload with exactly the round 5 key set and a `cite` payload with exactly its round 5 key set,
  filling `date ""`, `category "other"`, `provider ""` in the loaded view (the file's bytes and hash chain are
  untouched; nothing complete is rewritten, D40) and counts them in `CaseFile.upgraded`; such facts are undated and
  land in the memo's `Facts without a date, by page` section; any other key set, a broken chain or an unknown kind is
  refused as today (`_broken`), so an un-upgradable file still fails closed; `append` writes new events in the new
  shape after old ones. Bench: `benchkey` facts gain a required `date` (validated on the page like the quote and
  parsed; the chair writes the 29 dates from the pages: MED0001 and MED0002 `03/11/2025`, MED0003 `03/14/2025`, MED0004
  `03/24/2025`, MED0005 `04/14/2025`, MED0006 `04/18/2025`, MED0007 and MED0008 `05/09/2025`, EMP0001 `03/11/2025`,
  EMP0003 `03/15/2025`, DEF0003 `06/20/2025`); `benchcandidate` facts accept and keep `date`, `category`, `provider`
  (`CandidateFact(cite, quote, text, date="", category="", provider="")`); `benchscore` adds `dates_wrong` = found
  facts whose parsed date differs from the key's, printed after `extra` (`... extra=E dates_wrong=W flags=...`), a
  detail line `  dates_wrong: F03 (03/12/2025 for 03/11/2025)`, and `perfect` requires `W == 0` (D25 and D28 amended,
  D46). `ideal.json` and `flawed.json` gain the three fields on every fact (flawed: one wrong date, so its line reads
  `dates_wrong=1` and exit 1 as today); `key.json` gains `date` only (category is not scored: it is a label, judged by
  the output critic on the memo's sections; the summary wording stays the model's, Q48). Rejected: scoring categories
  (no owner answer on the list; T-23); dates as free text (the chronology needs an order; pillar 1 needs a check);
  inferring a page's date in code from the page text (which date on a page is the date of service is a reading: the
  model says, code verifies the span); refusing pre-round-6 files (the owner said upgrade; question 67).
- **1.4 The reconcile pass is withdrawn (owner Q55).** The first two drafts built a cross-chunk, cross-run comparison
  card after each extraction chunk (Q49 item 56). The owner's direction supersedes it: a task run sends the whole
  anonymized matter to Claude (stage 7b), so new records are read beside old ones and the cross-run gap of Q56
  closes there; the local model files and anonymizes and does not reconcile. Nothing of the pass is built: no
  `reconcile.py`, no `00-RECONCILE` card or `reconcile.schema.json` (retired with the other 13 JSON cards, so the
  manifest holds 15 cards and 11 schemas), no `echo "compared"` (the `echo` field stays for `07-ANON`'s
  `pages_seen`), no reconcile `run` events, no `compares=` on the status line. The memo's conflicts sentence
  (`memo.py:105-108`) stays as built with one addition: `Pages read in N run(s); conflicts and gaps are checked only
  between pages sent to the model together. A cloud task run reads the whole matter (stage 7b).` The three-chunk
  bench keeps its measured loss `bench_chunks=3 found=29 of 29 flags=5 of 9 runs=+3 uncited=2` and `flags_missed: G1
  G3 G6 G9` as the record of what the local model alone cannot see (T-22 stays a measurement, now of the local path
  only). `pipeline.batches(blocks, budget)` is still built (W5 needs it for packets). D47 is recorded as withdrawn
  in §6.
- **1.5 The memo takes spec §2's sections (Q50), shows the quotes beneath each conflict with defense-examination
  conflicts first (Q54), shows binder names as typed (Q57), reads binder roles, issues, standard and relief from
  `matter.toml`, with roles read from binder names and the header entries asked of the attorney once by code (Q57, Q62).**
  Sections in order: `What changed since the last memo`, `Outputs out of date`, `Open items` (as today); `Treatment
  chronology` (every fact with a date, by parsed date then case-file order, one paragraph `<date as written>,
  <provider or binder name>, <category>: "quote" [cite X]` then `Also cited` and `Model's reading` paragraphs as
  today); `Providers` (distinct non-empty providers, each `<provider>: first <date>, last <date>, pages [cite ...]`);
  `Diagnoses` (categories `diagnosis`, `imaging_result`); `Restrictions and work status` (`work_status`); `Medical
  history` (`prior_history`, `family_history`, `comorbidity_social`, each labelled); `Our doctors' opinions`,
  `Defense doctors' opinions`, `Opinions in other records` (categories `causation_statement`, `mmi_statement`,
  `impairment_rating`, `future_treatment`, `work_status`, `diagnosis`, split by the binder role of the fact's first
  present page: `ours`, `defense`, `other`); `Gaps and missing records`; `Conflicts`; `Facts without a date, by page`
  (facts whose primary cite has an empty date, under a heading per page as D41's by-page layout); `Facts on pages not
  in this matter` (as today). A fact appears in the chronology once (its first present cite) and in every topical
  section whose category set holds its category; `Verified facts by record` is retired. Each conflict entry: `Conflict
  between [cite A] and [cite B].`, the `Model's reading` paragraphs, then `From [cite A]:` followed by one `"quote"`
  paragraph per fact cited on A (case-file order) and the same for B; order: first the conflicts whose page ids include
  a page of a binder with role `defense` and a page of a binder with role `ours` (Q41 and Q49 item 54 say defense
  against our records, not against any other binder; review M7), in case-file order, then the rest in case-file
  order; with no `defense` or no `ours` binder the section's second sentence reads `ROLE NEEDED: no binder pair is
  marked defense and ours in matter.toml; conflicts are in the order found.` and the role-based opinion sections
  print `ROLE NEEDED: no binder is marked <role> in matter.toml` instead of guessing (chair note Q56). Binder names:
  `check_binders` is deleted
  (Q57); page headings read `Page <label>, binder <name>` with the name in a run `exempt="binder"`, and every
  code-built cite run (`[cite X]`, `[page x/001]`) is `exempt="cite"` (a cite is stamps and page ids, never prose;
  D0.7's `[page ime/001]` case); the rules still check every title, heading word, label, model sentence and the
  attorney's typed entries. Binder roles (owner Q57): new `src/casefile/roles.py` `role(binder, info) -> str`: a
  binder whose name, lowercased with every `-`, `_` and space folded to one space, holds the token `dme` or the
  phrase `defense medical` is `defense`; every other binder is `ours`; a typed role in `matter.toml` `[roles]`
  overrides, and is required for a multi-plaintiff matter (`plaintiffs` > 1 with no typed role for a binder prints
  `ROLE NEEDED` for that binder in the conflict order and the opinion sections rather than guessing). Matter entries
  (Q57, Q62): `matter.toml` gains optional tables `[header]` (`matter_type` one of `workers-comp`, `mva`,
  `slip-and-fall`; `client_name`; `date_of_accident`; `treating_physician`; `iab_hearing_number`; `hearing_date`;
  `plaintiffs` integer, default 1; strings may be empty and print `NEEDED`), `[hearing]` (`issues` an array from
  the type's list: workers' comp `permanency`, `termination`, `DCD`, `DACD`, `other`; MVA and slip and fall
  `liability`, `treatment`, `other`; `standard`, `relief` strings) and `[roles]` (binder to `defense`, `ours`,
  `other`); `matter.py:60-61` admits them beside `number` and `binders`; in the intake layout a `matter.toml`
  holding `number` and the tables but no `binders` is allowed, and `pages.py:88-89` refuses only a `matter.toml`
  with `binders` beside `pages/` (new `src/casefile/matterinfo.py` `load(folder) -> MatterInfo(matter_type,
  client_name, date_of_accident, treating_physician, iab_hearing_number, hearing_date, plaintiffs, issues,
  standard, relief, roles)` reads both layouts; unknown keys, a wrong type, an issue outside the type's list, an
  unknown role or a binder the matter does not have are refused, exit 2, naming the key; a missing file or table
  gives empty entries). The header is asked once by code, never by the model (pillar 4): at a task run (`report`,
  `depo`, `hearing`) with no `[header]` table, `matterinfo.ask(info, stdin, stdout) -> MatterInfo` prompts on the
  terminal for the matter type, the client name, the date of accident, the treating physician (optional), the IAB
  hearing number (optional), the hearing date and time (optional) and the issues from the type's list (numbers,
  comma-separated), writes `[header]` and `[hearing].issues` into `matter.toml` once (a `.tmp` and `os.replace`;
  existing tables kept) and never asks again; a blank answer stays empty and prints `NEEDED`; when `stdin` is not a
  tty (every test, every job started by the stage 8 page) the prompt does not run, nothing is written, every field
  prints `NEEDED` and the job neither blocks nor fails on that account; run flags (`--issue`, `--standard`,
  `--relief`, `--when`) override for the run and never write the file; `casefile memo` reads the file and never
  prompts. `outputs.header(info, matter, kind, *, when="", deponent="")` prints `Attorney Work Product | Privileged
  & Confidential`, `Matter type: ...`, `Client: ...`, `Date of accident: ...`, `Treating physician: ...`, `IAB hearing
  number: ...`, `Hearing date: ...`, each `NEEDED` when empty, the deposition line from `--when` or `NEEDED`,
  `Matter <number>` and the build line; the typed values are our words and are rules-checked. The fixture
  `matter.toml` gains invented entries (`[header]` `matter_type = "workers-comp"`, `client_name = "Morgan
  Ashby-Vale"`, `date_of_accident = "03/11/2025"`, `treating_physician = "Dr. Priya Okonkwo-Lind"`,
  `iab_hearing_number = "1234567"`, `hearing_date = "01/15/2026 9:00 AM"`, `plaintiffs = 1`; `[hearing]` `issues =
  ["permanency", "termination"]`, `standard = ""`, `relief = ""`; no `[roles]`: `defense-report` is `ours` by name
  and the fixture therefore carries `[roles]` `defense-report = "defense"` as the typed override the test also
  exercises) and the pages stay 14; no petition page, no `00-HEADER` card, no `attorney.toml`. Stamp compatibility (code review L3, #R05-CX-9): before the run log opens, every job calls
  `rules.check_stamps(pages)` which refuses, exit 2, the first page stamp that fails `re.fullmatch(bates_pattern)`:
  `stamp ABC123 on page scan/001 does not match the playbook's bates-cites pattern; align [ocr].stamp_pattern with
  rules.toml bates_pattern before running`. No-reply wording (verifier L1, #R05-V-1): `model.no_reply_reason(exc,
  host)` returns `no reply from the model server at <host> (<detail>)` and nothing more; `memo_job` prints `memo:
  cannot run: <reason>; the pages of this run stay open until a later run reads them`; `bench` prints `bench: cannot
  run: <reason>`; the doctor prints `<reason> | do: start the Ollama app`; the gate's own page clause at `gates.py:315`
  is unchanged. Rejected: a role flag on the command line each run (roles are facts about the matter the attorney
  types once); reading roles from binder names (`defense-report` is a label, Q57); an intake-time name check (Q57:
  a folder label is not our words); header values read off a petition by the model (the owner asks to be asked, Q57; a model call per job is gone); guessing a role on a multi-plaintiff matter (ROLE NEEDED instead, Q57).
- **1.6 Outputs are code-rendered Word documents from a fact packet and gated JSON answers; the model labels and
  writes questions in engine-neutral steps; nothing in a document is unverified without a label (owner Q53; review
  H6, M1, M2, M6).** Three fixed interfaces, one per step, so a restored cloud answer (stage 7b) renders through the
  same code. (1) New `src/casefile/packet.py`: `build(casefile, pages, *, matter, task, options, playbook_version,
  facts=None) -> Packet` with `Packet(matter, task, options: dict, playbook_version, facts: tuple[PacketFact, ...],
  pages: tuple[Page, ...], flags)` where `PacketFact(id, quote, cite, page_id, date, category, provider, text)`,
  `facts` every case-file fact (or the subset given) with its first present cite, `pages` the pages those facts cite
  (text included), `options` the task's typed choices (`deponent`, `taken_by`, `purpose`, `deponent_pages`,
  `section`, `issue`, `side`); `Packet.body() -> str` renders `Matter N\nTask: <task> <options as key=value>\nFacts:\n`
  one line per fact `[F12] MED0003 (medical/003; 03/14/2025, prior_history): "quote"` (with `[deponent's record]`
  appended when the page is in `deponent_pages`), then `Pages:\n` and `extract.page_block(page)` for every packet
  page; `Packet.to_json()` and `from_json()` round-trip (the stage 7 anonymizer works on this JSON); `packet.batches
  (packet, card, num_ctx) -> list[Packet]` splits by facts with their pages so each body fits the `pipeline.chunk`
  arithmetic with `RETRY_MARGIN`, refusing a single fact whose page alone does not fit with the reason of
  `pipeline.chunk`. (2) `outputs.ask(packet, card, *, client, rules, log, job, playbook_version) -> gates.Outcome`
  calls `gates.ask(card, packet.pages, body=packet.body(), ...)`; every output card has `coverage false` (no page
  is marked read or failed by an output), gate 6 requires at least one non-empty array among `required_any` and no
  blank string except under `optional_blank`, gate 4 checks every item's `quote` on its cited page and every digit run
  of an item's prose (`text`, `note`, `why`, `absent_note`) against the cited page's text with cite spans removed
  (`numbers_in = "page"`; the memo card keeps `"quote"`), gate 5 checks strings under `question_keys` with
  `unit="question"` and the rest with `unit="text"` (replacing `Card.unit`, D0.5). (3) `report.render`, `depo.render`,
  `hearing.render` each `(answers: dict[str, dict | None], packet, casefile, pages, attorney, *, open_items,
  playbook_version, model) -> outputs.Doc` where `answers` maps a step name (`factsheet`, `questions:primary`,
  `concessions`, `elements`, `factsheet:issue:1`, ...) to the gated answer or `None` when the step failed; a renderer
  never calls the model and is tested with answers loaded from the fixture files. A job is `start` (below), then
  `packet.build`, then one `ask` per step, then `render`, then `check` and `publish`. New `src/casefile/outputs.py`:
  `Doc(title, header, sections)`; the memo's `Paragraph`, `Run`, `Section` dataclasses move here (`memo.py` imports
  them; `OpenItem`, `label`, `Memo`, `build`, `check`, `render` stay in `memo.py`, which `status.py:31,37` uses,
  review L4); `Run.exempt` in `quote`, `cite`, `binder`, `reason`; `Paragraph.unit` (`text` or `question`);
  `header(info, matter, kind, *, when="", deponent="")` builds the block of §1.5 from the `MatterInfo` (`NEEDED` for every empty entry), for a deposition `Deposition of <name as typed or the deponent type>, <--when as typed or NEEDED>`, `Matter <number>`, `Built <date> from case file entry <seq>; playbook <version>; model <tag>`; `check(doc, rules, stamped)`
  runs every non-exempt run with its paragraph's unit (findings at `error` refuse the document, exit 2, as
  `memo.render` today); `publish(folder, name, doc, rules, casefile, counts, *, failed_steps) -> CaseFile` renders
  to `outputs/<name>.docx.tmp` and `os.replace`s; with no failed step the final name is `outputs/<name>.docx` and the
  `output` event `{name, path, built_from_seq, facts, conflicts, gaps, open}` is appended, so `stale_outputs` and the
  memo's `Outputs out of date` cover every output (spec §2); with any failed step the file is `outputs/<name>.partial.docx`,
  no `output` event is appended, `status` never calls it current, and the next run rebuilds it (review M6, pillar 2,
  #R05-OC-1). Common job order (`outputs.start(config, number, job)`): config, playbook, pages (none: exit 2), case
  file (no facts: exit 2 `run casefile memo first`), `matterinfo.load` then `matterinfo.ask` when `[header]` is absent and stdin is a tty (§1.5), `check_stamps`, then the run log and the model.
  A step whose answer fails both attempts is disclosed in the document: the section's first paragraph reads
  `<section>: the model's answer failed the <gate> check after one retry: <reason>` and the job exits 1; a packet
  that must be batched (factsheet) merges the batches' labels; a step that cannot be batched (questions) sends the
  deponent's pages and facts first and discloses `<N> facts were not sent to the model for this section (prompt
  budget); they are listed in the memo`, never silently. Every document ends with `Open items` (unread pages as the
  memo lists them, failed sections, header fields and roles `NEEDED`) and exits 0 when that section says `none`, 1
  otherwise, 2 when it cannot run. Every assertion a card returns carries a `quote` and a `cite` or the field does
  not exist (Q53; review M2): question items `{text, cite, quote, note}`, factsheet items `{cite, quote, use, note}`,
  danger items `{quote, cite, why}`, points for our expert `{text, quote, cite}`, elements `{element, status, quote,
  cite, absent_note}`, labels `{label, quote, cite, supporting_findings}`; the free-text `missing` list is dropped
  (gaps are the memo's flags). Model-written strings appear only as: question text (its own paragraph, with the
  verified quote beneath as `Rests on: "quote" [cite X]`), `Model's reading:` (fact text), `Model's note:` (`note`,
  `why`, `absent_note`, a point for our expert's `text`, each beneath its quote and cite). Rejected: markdown or
  prose cards stitched by code (D34; #R04-PC-7); a document with sections silently missing (pillar 2); outputs
  outside `outputs/` (D13, privacy row); a per-job prompt string (M1: two paths would diverge).
- **1.7 `casefile report --matter N (--provider "..." | --binder B | --pages S1,S2,...) (--defense | --ours)`: the
  report against the case file.** Pages of the report = by default (Q61) the pages of every fact whose extracted
  `provider` holds the typed `--provider` text (casefold substring; none: exit 2 `no fact names that provider; pass
  --binder or --pages`), overridden by the named binder's pages or the named stamps or page ids (an unknown one:
  exit 2).
  Document `outputs/report-<binder or first-last stamp>.docx`: header; `Coverage` (pages of the report read, open, with
  labels); `What the report states` by category group (`Records referenced`, `History` = mechanism_of_injury,
  prior_history, patient_statement, chief_complaint, pain_score; `Examination findings` = exam_finding,
  diagnostic_test; `Imaging` = imaging_result; `Diagnoses`; `Opinions` = causation_statement, mmi_statement,
  impairment_rating, work_status, future_treatment; `Other statements`), each fact `<date>: "quote" [cite X]` plus
  readings; `Conflicts with other records` (every conflict flag citing a report page, with the quotes beneath as
  §1.5); for `--defense`: card `04-G` on the report's pages plus the case file's facts from other binders in the
  history, examination, imaging, diagnoses and opinions groups (as fact blocks, batched by budget) answering
  `{"concessions": [{"type": enum of the seed card's nine, "quote", "cite"}], "undefined_labels": [{"label", "quote",
  "cite", "supporting_findings": [{"quote", "cite"}]}], "danger_zone": [{"quote", "cite", "why"}]}` (`required_any`
  = all three; `optional_blank` empty; the label's `quote` is the sentence holding the label), the whole built as a
  packet of the report's pages plus those facts (`packet.build(..., task="report", options={"side": "defense"},
  facts=<the groups' facts>)`) and rendered by `report.render(answers, packet, ...)` from the `concessions` answer,
  rendered as `Concessions (the report's own
  words)` (type, quote, cite), `Undefined labels` (label, the quote, then `Findings the report gives:` quotes or
  `none stated on the pages sent: <labels>`), `Danger zone` (quote, cite, `Model's note: <why>`), `Candidate cross
  topics (document-based)` = code: the concessions, the conflicts and the undefined labels, each one line with its
  cite, and the fixed sentence `Records review audit: not built this round; the report's records-referenced statements
  are listed under What the report states for your own comparison.`; for `--ours`: card `05-A` on the report's pages
  answering `{"elements": [{"element": enum of 14, "status": "STATED" | "PARTIAL", "quote", "cite", "absent_note"}]}`
  (`required_any = ("elements",)`, `optional_blank = ("absent_note",)`: STATED elements carry an empty note, review
  H3), rendered as `Elements` (one line per element in the fixed order: STATED or
  PARTIAL with quote and cite and `Model's note: <absent_note>`, or `NOT FOUND on pages <labels>` for every element
  the answer omits: the negative is code's, never a cite the model invents), `Gaps` (PARTIAL and NOT FOUND, with
  `treatment_reasonable_necessary_related` and `bills_reasonable_related` always listed separately), `Defense
  comparison` (conflicts between the report's pages and pages of `defense` binders, quotes beneath), `Items to raise
  with the doctor (subjects only)` (the NOT FOUND and PARTIAL element names). Rejected: the model writing the memo's
  prose (04-H); a records audit by provider-name matching in code (an inference about names); omitting the limit
  sentence (the skill's omissions point is real; the document says it is not done).
- **1.8 `casefile depo --matter N --deponent our-doctor|defense-doctor|client|witness --taken-by us|defense [--purpose
  discovery|trial] [--provider "..."] [--binder B]* [--pages ...] [--name "..."] [--when "..."]`: the deposition
  package.** For `our-doctor` and `defense-doctor` the deponent's own records are, by default (owner Q54 item 61),
  the pages of every fact whose extracted `provider` holds the `--provider` text (casefold substring; `--name`
  is the display name only), overridden by `--binder` or `--pages`; with neither a provider nor an override, exit 2
  `name the deponent with --provider, or the records with --binder or --pages`; a provider that matches no fact is
  exit 2 naming the providers on file; for `client` and `witness` every page. The packet:
  `packet.build(casefile, pages, task="depo", options={"deponent", "taken_by", "purpose", "deponent_pages"})`, every
  fact with its page. Step A, card `02-A` (`packet.batches`): answer `{"facts": [{"cite", "quote", "use": "our_case"
  | "defense_case" | "both" | "danger" | "none", "note"}]}` (`required_any = ("facts",)`, `optional_blank =
  ("note",)`; a danger fact with an empty note renders `Model's note: none given`, review H3). Step B, one call per
  section (`primary`, `cross`, `redirect`) with the deponent's card (`02-C-OURDOC`, `02-C-DEFDOC`, `02-C-CLIENT`,
  `02-C-WITNESS`; `question_keys = ("text",)`, `optional_blank = ("note",)`), the packet's body followed by
  `Labels:\n` one line per fact `[F12] <use>` and `Section: <name>`, where the card text defines the sections: taken
  by us, `primary` is our examination, `cross` the questions the other side will ask, `redirect` ours after cross;
  taken by the defense, `primary` is the other side's likely examination, `cross` ours, `redirect` theirs; answer
  `{"section", "questions": [{"text", "cite", "quote", "note"}], "points_for_our_expert": [{"text", "quote", "cite"}]}`
  (`required_any = ("questions",)`; review M2: every item carries a quote on a packet page, and the old `missing`
  list is dropped). `depo.render(answers, packet, ...)` takes `answers["factsheet"]` and `answers["questions:<section>"]`. Document `outputs/depo-<deponent>-<taken-by>.docx`: header (with `Deposition of ...`, purpose);
  `Case outline: our view` (facts labelled `our_case` or `both`, grouped by the §1.5 category groups, each `<date>:
  "quote" [cite X]`, readings) then a page break; `Case outline: the defense view` (`defense_case` or `both`) then a
  page break; `Questions: primary`, `Questions: anticipated cross`, `Questions: redirect` (numbered `1. <text>` as a
  question paragraph, then `Rests on: "quote" [cite X]`, then `Model's note: <note>` when non-empty); `Danger zone`
  (facts labelled `danger`: `"quote" [cite X]` and `Model's note: <note>`); `Points for our expert` (`"quote" [cite
  X]` then `Model's note: <text>`, or `none`); `Open items`. For `our-doctor` the code checks the primary section (when taken by us) for one question text matching
  `\btreatment\b` and one matching `\bbills?\b`; a missing one prints `Missing: the <treatment|bills> question (firm
  practice: two separate questions)` as the section's first paragraph and an open item. Rejected: a prose outline
  written by the model (02-B: unverifiable sentences); a per-topic call (the seed cards' "one topic" design multiplies
  calls; one section per call keeps the labelled facts together); a page cap on the outline (question 70 in 68).
- **1.9 `casefile hearing --matter N [--outline] [--client] [--doctor (--provider "..." | --binder B | --pages ...)]
  [--closing] [--issue "..."]* [--standard "..."] [--relief "..."] [--when "..."]`: one document
  `outputs/hearing.docx`; with no part flag every part is built; issues, standard and relief come from `matter.toml`
  `[hearing]` (Q62) and a run flag overrides the stored value for that run only (the file is never written by a job); packets `task="hearing"` with `options` per step (`issue`, `section`,
  `deponent_pages`), rendered by `hearing.render(answers, packets, ...)` where `answers` holds
  `factsheet:issue:<n>`, `questions:primary`, `questions:cross` and `elements`.** `Pre-hearing checklist` always first: the starred item `★ GIVE THE BILLING
  MEMO TO THE HEARING OFFICER. Hand it up at the outset with the exhibits.` as its own paragraph, then `Totals: not
  on file; the billing memo is supplied by the attorney (question 28).` (Q37: the system reads no bills), `Exhibits to
  mark: <binder>: <first stamp> to <last stamp> (<n> pages)` per binder, `Deposition transcripts to submit: none on
  file (transcripts are stage 8).`, `Witness availability: not on file.`, `Stipulations: none on file.`; `Hearing
  outline`: one block per issue (none stored or typed: `Issues: NEEDED; answer the prompt at the next interactive run, add [hearing] issues to matter.toml, or pass --issue "..." from the type's list.`), each `Issue: <as stored or typed>`, `Standard: <as stored or typed,
  else STANDARD NEEDED>`, `Our key facts` (card `02-A` called with the
  request line `Issue: <text>` instead of a deponent, facts labelled `our_case`/`both`), `Deposition designations:
  none on file.`, `Defense position` (`defense_case`/`both`), `Conflicts` (flags whose pages include a `defense`
  binder page, quotes beneath), `Open items for this issue` (gap flags, unread pages); `Client preparation`: card
  `03-CLIENT` (rewritten to JSON, `question_keys = ("text",)`) called for `primary` (direct examination: open
  questions, not leading, with the record entry each rests on) and `cross` (likely cross), rendered as the depo
  sections, then `Consistency flags` (conflict flags whose facts include `patient_statement`, `mechanism_of_injury`
  or `prior_history` categories, quotes beneath) and the fixed instruction block of the seed card (listen to the
  whole question; pause; answer only what was asked; do not guess; "I don't know" or "I don't remember" only when
  true; speak to the Hearing Officer; keep answers short); `Doctor preparation` (requires the doctor's pages): `What
  the doctor's records say` (the §1.7 category groups over those pages), `Opinions the case needs` (card `05-A` on
  those pages as §1.7, treatment and bills listed separately), `Defense report points to be ready for` (facts of
  `defense` binders in the opinions group, each with the conflicts it sits in), `Records the doctor may not have
  seen: not checked this round (no records audit card runs).`, `Conflicts between the doctor's records and other
  records` (quotes beneath); `Closing outline`: per issue, `Standard`, `Our strongest facts` (`our_case`/`both` by
  date), `Defense says` (`defense_case`), `Our answer` (for each conflict with a `defense` page, the our-side quote
  beneath the defense quote), `Relief requested: <as stored or typed, else RELIEF NEEDED>`, with the fixed sentence
  `No law is cited; the attorney supplies the standard and the relief.`; `Open items`. Rejected: issues read from a petition by a card (the owner answers the type's list once, Q57, Q62); a closing written by the model (03-CLOSING was STRONG tier: argument is the attorney's, D3's spirit); the
  billing memo itemized from bills (Q37); a job that writes `matter.toml` (the attorney's file).
- **1.10 The stage 6 exit test builds six documents from the test matter and prints the counts the output critic
  checks against the answer key and the recorded answers.** `tests/test_stage6_exit.py` (socket, one stand-in): copy
  the fixture matter (its invented `matter.toml` header, issues and role override, W1), run `casefile memo` (one chunk of 14 pages), then `depo --deponent defense-doctor --taken-by us --provider "Marchetti" --name "Dr.
  Marchetti"`, `depo --deponent our-doctor --taken-by us --provider "Okonkwo-Lind" --name "Dr. Okonkwo-Lind"`,
  `hearing --provider "Okonkwo-Lind"` (issues from `matter.toml`), `report --binder defense-report --defense`,
  `report --provider "Okonkwo-Lind" --ours`, each as a `scripts/run.sh` subprocess; the recorded answers are
  invented fixture files under `tests/fixtures/outputs/9001.001/` (one per distinct packet: `factsheet-defense-doctor.json`, `questions-defense-doctor-primary.json`,
  `-cross`, `-redirect`, the same four for `our-doctor`, `factsheet-issue-1.json`, `factsheet-issue-2.json`,
  `client-primary.json`, `client-cross.json`, `elements-okonkwo-lind.json` (shared by the hearing's doctor part and
  the ours report, whose packets are byte-identical by construction), `concessions-defense-report.json`: 15 files)
  registered on the in-process `FakeModel` through `FakeModel.record(row)` (W1) before each command, built by
  `packet.build` and `recording_for(card, packet.pages, number, answer, body=packet.body())` (W1). The critic is
  told: the our-doctor bills question in `questions-our-doctor-primary.json` names every provider the case file
  holds (`Fennimore County Hospital`, `Brightwater Family Medicine`, `Ridgeline Physical Therapy`, `Lakeshore
  Imaging`, `Lakeshore Orthopedic Associates`) and says `bills` and `charges`, as the skill writes it, and passes
  the rules under the owner's Q59 (b) and (c) (§1.12); the stage 6 line prints `providers_named=5 of 5`. The test
  opens every `.docx` with python-docx and prints one `stage6` line per document (§2 W8) and the final `stage6
  exit=0 docs=6 of 6 answers=+16 rule_hits=0 server_stopped=1` (one extraction call, 15 synthesis calls; every job runs with stdin not a tty, so no prompt runs and the header comes from the fixture file). The critic's answer key: `key.json` (facts and flags), the 15 recorded answers (every question's quote and
  cite), the practice entries (D0.11) and the probes of D0.9 and §1.12. Rejected: a critic reading documents the chair built by hand (not
  reproducible); one document per kind only (the our-doctor rule and the defense-doctor rule differ, both must be
  seen).
- **1.11 Rule 5 patterns gain the fee-for-deposition and how-often-retained forms only; every hire, engage, refer and
  `you` form is held for the owner (review H5).** `rules.toml:21-30` gains
  `'\bfees?\b[^.;:?!\r\n]{0,60}\b(?:deposition|testimony|testif(?:y|ied|ying)|appearance)\b'`, its mirror, and
  `'\bhow\s+(?:often|frequently|many\s+times)\b[^.;:?!\r\n]{0,60}\bretain(?:s|ed|ing)?\b'`. Measured after the
  review: must-fail `What is your fee for this deposition?`, `Is there a fee for your testimony today?`, `How often
  does the carrier retain you?`, `How many times has the carrier retained you this year?` all hit; must-pass (14)
  `When were you hired by Quarry Ridge Logistics LLC?`, `You were hired by Quarry Ridge Logistics in August 2021,
  correct?`, `Who hired you at the warehouse?`, `Quarry Ridge hired you as a forklift operator, correct?`, `You have
  been engaged in warehouse work since 2021, correct?`, `How many times did your supervisor refer you to the clinic?`,
  `How much time did you spend face to face with the claimant?`, `Do you currently treat patients with low back
  injuries?`, `What share of your practice is treating patients?`, `How often do you see patients with disc
  protrusions?`, `Were you paid for the day you missed work?`, `Did the employer hire a replacement while you were
  out?`, `You retained a copy of the incident report, correct?`, `How often did you attend physical therapy?` all
  pass the new patterns and the rules as built. The first draft's `retain|hire|engage ... you` and `how often ...
  hire|engage|refer` patterns hit the four client employment sentences above (the reviewer's probe, reproduced) and
  are withdrawn; `How many times has this firm hired you?` therefore stays unblocked and joins question 64 with the
  percentage, share and split forms (all collide with ordinary client, witness or clinical practice questions, and
  gate 5 runs the rules over every question card whatever the deponent, `gates.py:256-262`); the defense-doctor card
  forbids them all in words meanwhile. Rejected: a deponent-aware checker this round (question 64 asks whether the
  owner wants one).
- **1.12 The skill's bills question passes as written (owner Q54 item 59, (b) and (c)).** Two rule changes, both in
  code and `rules.toml`, measured by W1's `bills_forms` table: (b) provider names do not count toward the treatment
  group of `treatment-and-bills-apart`: `Rules.check(text, *, unit, stamped, providers=())` masks every occurrence
  of each provider name (casefold, whitespace-folded) with spaces before the conjunction rule runs (the forbid and
  cite rules see the original text); gate 5 passes `providers` = the packet's distinct `provider` values, and
  `outputs.check` passes the case file's; (c) `charges` and `bills` are exempt from the doctor pairing of
  `no-hired-paid-retained` inside a bills question: the pairing pattern at `rules.toml:24` loses `charges?|charged|
  billed|bill` and a new `unit = "text"`-only pattern keeps them for memo prose (a `forbid` rule gains an optional
  `patterns_text_only` list, applied when `unit == "text"`), so `Doctor, as to the bills themselves, the charges
  from ...` passes as a question while `The doctor billed the carrier for the report.` still fails in a memo.
  Controls (`bills_forms=7 of 7`): must-pass as questions with providers `("Ridgeline Physical Therapy", "Lakeshore
  Orthopedic Associates")`: the skill's bills question verbatim with those providers filled in; the same with every
  fixture provider; `What treatment did you receive at Ridgeline Physical Therapy?` (a provider name alone does not
  make a treatment word); must-fail: `What treatment did you receive and what bills followed?` (conjunction),
  `Doctor, what were you paid for the examination?` (`paid ... examination`, pattern 2 unchanged), the skill's
  treatment question with `bill memo listing charges` (the conjunction: `treatment` and `bill memo`; the seed card's
  wording without the bill memo is the one the `02-C-OURDOC` card asks for, and the critic is told), `Doctor, what
  did you charge for the report?` (`charge ... report` stays in `fees? ... report`'s class: the mirror pattern at
  `rules.toml:27` gains `charges?|charged`). `rules_selftest` keeps `misses=0 false_hits=0`. Rejected: masking
  provider names for every rule (a provider named `Independent Medical Evaluation Services` must still trip
  `no-dme-ime` in our words); dropping the doctor pairing for text (memo prose about fees stays blocked).
- **1.13 Carried items not ruled otherwise.** M4 (an edited last case-file line loads clean) stays a recorded limit:
  no head anchor this round (the round's surface is large; the stage 8 job runner is the natural owner of a stored
  head). T-16 to T-22 stay tuning; T-22 is now a measurement of the local path only (§1.4). The untracked fixture
  `.claude/` marker is the owner's (HANDOFF).
- **1.14 Boundary.** Not this round: transcripts and page:line cites (stage 8 `00-TESTIMONY`); the records review
  audit, summary accuracy and opinion basis cards; a second model pass judging questions (02-D) or summaries (Q48
  interim); running the anonymization card (stage 7); bills (Q37); the web page, job queue and Cancel (stage 8); the
  bridge (8b); the cloud round trip and the whole-matter re-send (stage 7b, D0.2); any reconcile or continual update
  (Q55); retiring stage 5 code (stage 7b's brief).

## §2 Work items, in build order

Every CHECK runs through `scripts/run.sh`; every seed is applied to a copy, confirmed with `cmp`, run with a fresh
`PYTHONPYCACHEPREFIX` (#R04-OC-1) and restored (`cmp` identical) before the pass counts. Counts marked "measured" are
derived by the builder from the fixtures it writes, printed, and accepted by the chair after a read (round 5
precedent); every other number is fixed here.

### W0 (chair, before any builder): worktree and reading
- `git worktree add .claude/worktrees/r6-lane-b -b r6/lane-b` after W1 is committed (not before); toolchain
  `T=$HOME/.casefile-dev/r6-lane-b` synced with the sandbox off (HANDOFF). The chair reads every playbook entry W1
  writes against the skill sections named in `learned` and every fixture file of W2, W6, W7, W8 against the pages
  before the critic round (#R02-OC-H1, #R03-OC-M1).

### W1 (one builder, main tree, before the lanes split): foundation, committed green
The commit must leave the full suite, the gate and both `--candidate` bench runs green (review H1, H2, H4): every
parser, schema, budget derivation and stand-in helper the fixture edits or lane B need is in this item.
- Files: `playbook/deposition.toml` and `playbook/hearing.toml` (the 13 entries of §1.1, every field; `deponent` where
  named); `src/casefile/playbook.py:72-73` (the two marking rules of §1.1); `src/casefile/gate.py:40-47` (`practice=`
  and `samples=` counts); `src/casefile/cards.py` (new, §1.2: `Spec`, `load`, `text`, `card`, `CardsError`);
  `cards/manifest.json` (version 2, the 15 entries of §1.2 and §1.4 with every field: `01-MEMO` `required_any
  ["facts", "flags"]`, `optional_blank []`, `echo null`, `coverage true`, `numbers_in "quote"`, `question_keys []`,
  `deponent null`; `02-A` `required_any
  ["facts"]`, `optional_blank ["note"]`, `coverage false`, `numbers_in "page"`; `02-C-OURDOC` `deponent
  "our-doctor"`, `02-C-DEFDOC` `"defense-doctor"`, `02-C-CLIENT` and `03-CLIENT` `"client"`, `02-C-WITNESS`
  `"witness"`, each `required_any ["questions"]`, `optional_blank ["note"]`, `question_keys ["text"]`, `numbers_in
  "page"`; `04-G` `required_any ["concessions", "undefined_labels", "danger_zone"]`, `optional_blank []`; `05-A`
  `required_any ["elements"]`, `optional_blank ["absent_note"]`; `07-ANON` `required_any []`, `echo "pages_seen"`,
  `coverage false`; stage 8 cards `00-BILLS`, `00-CLASSIFY`, `00-PROCEDURAL`, `00-TESTIMONY`, `01-P0` `job null`, `stage 8`, `required_any` naming their top array), the 31 retired card files (the 30 of §1.2 plus `00-RECONCILE`) and 10
  schemas (the 9 of §1.2 plus `reconcile`) deleted, `cards/_core.md` deleted, `schemas/bench_extract.schema.json`
  renamed `schemas/medical_memo.schema.json` with `title` `medical_memo` and the six fields and 24-value enum of §1.3,
  `cards/07-anonymize/entities.md`
  and `schemas/anonymize.schema.json` (new, §1.2: `pages_seen [string]`, `people [{name, kind enum
  claimant|doctor|attorney|person, quote, cite}]`, `organizations [{name, kind enum employer|insurer|provider|other,
  quote, cite}]`, `places [{name, quote, cite}]`, `anchor_dates [{date, quote, cite}]`, every array may be empty but
  `pages_seen`), `cards/01-records/memo.md` (the full §1.3 body: field sentences, the date rule, the category list),
  the five output card files kept in place with their old bodies and their schemas replaced by the §1.7 and §1.8
  shapes (lane B rewrites the bodies; `cards_loaded=15 of 15` holds at this commit); `src/casefile/extract.py`
  (`card(book=None)` -> `cards.card("01-MEMO", book)`, `book` loaded from the checkout's `playbook/` when `None` and
  passed by `pipeline.bench_run`, `memo_job`, `status`; `CARD_TEXT` and `TEXT` removed; `ID_SENTENCE` reworded as
  §1.2; `CARD_NAME = "medical_memo"`); `src/casefile/dates.py` (new: `parse`, `iso`, §1.3); `src/casefile/facts.py:53-62`
  (`FIELDS` of §1.3 plus the round 5 key sets kept as `FIELDS_V1` for the upgrade on load; `:35-42` `Fact` gains
  `dates`, `category`, `providers`; `:91-105` views; `:238-270` `merge` copies the fields and `cite` events carry the
  item's date and provider; `:172-178` accepts a `fact` or `cite` payload with exactly its `FIELDS_V1` key set,
  fills the defaults of §1.3 and counts `CaseFile.upgraded`; every other key set stays `_broken`);
  `src/casefile/matter.py:60-61` and `src/casefile/pages.py:88-89` (the `[header]`, `[hearing]` and `[roles]` tables of §1.5, the intake-layout `matter.toml` without `binders`), `src/casefile/matterinfo.py` (new, §1.5: `MatterInfo`, `load(folder)`, `ask(info, stdin, stdout)`, `write(folder, info)`, refusals naming the key, the two issue lists as constants), `src/casefile/roles.py` (new, §1.5: `role(binder, info)`), `tests/fixtures/matters/9001.001/matter.toml` (the invented `[header]`, `[hearing]` and `[roles]` of §1.5; the 14 pages and three binders unchanged), `key.json` (date on all 29 facts), `ideal.json` (31 facts: date, category, provider on every fact), `tests/fixtures/bench/flawed.json` (the three
  fields; its one wrong date is W2's), `src/casefile/benchkey.py:60-66` (`date` required, a non-empty one found on
  the page by `found_in` and parsed by `dates.parse`, an empty one allowed for a page that shows no date; review L5);
  `src/casefile/benchcandidate.py:44-47` (`CandidateFact(cite, quote, text, date="", category="", provider="")`, the
  three keys optional, any other key refused); the seven files pinning the bench line (D0.8), `tests/test_stage2_exit.py`, `tests/test_stage4_exit.py` and `tests/test_stage5_exit.py` untouched at W1 (14 pages, 29 key facts, the baseline lines byte-identical); `src/casefile/rules.py` (`check(text, *, unit, stamped=True, providers=())` with the
  provider mask of §1.12 and the `patterns_text_only` field; `check_stamps(pages, rules)`, §1.5), `playbook/rules.toml`
  (the §1.11 patterns at `:21-30`; the §1.12 split of the doctor pairing at `:24` and the `charges?|charged` mirror
  at `:27`; `rules.toml` `version` stays 1), `src/casefile/gates.py:20-33` (`Card` gains `coverage: bool = True`,
  `required_any: tuple[str, ...] = ("facts", "flags")`, `optional_blank: tuple[str, ...] = ()`, `echo: str | None =
  None`, `question_keys: tuple[str, ...] = ()`, `numbers_in: str = "quote"`; `unit` removed and `tests/test_gates.py`
  re-pinned), `:56-60` (`messages(card, pages, nonce, *, matter, body=None)`), `:171-172` (`ask(..., body=None,
  echo=None, providers=())` where `echo` is the tuple `(key, values)`), `:256-262` (unit per key; `providers` passed
  to `rules.check`), `:263-273` (gate 6: `required_any` unless `card.echo`, the echo set equality, blanks except
  `optional_blank`), `:313-322` (no coverage rows when `card.coverage` is false; `Outcome.read/uncited/failed` empty
  then), `:143-149` (`numbers_in`); `src/casefile/model.py:40-58`
  (`no_reply_reason(exc, host)`, §1.5) with `memo_job.py:98-100`, `bench.py:101-104`, `doctor.py:150-151` and the
  pins `tests/test_bench_pipeline.py:90`, `test_fix_cycle2.py:127`, `test_bench_cli.py:123,210` re-pinned to each
  command's own sentence; `tests/fakemodel/core.py` (`FakeModel.record(row)` adds a recording to a live stand-in;
  `_fault_content` `:37-65`: when `obj` has no `facts`, `bad_schema` deletes a required key of the first item under
  `required_any[0]`, `forbidden_json` writes `The IME found no injury.` into that item's first string, `empty_answer`
  empties every top-level array; review H4), `tests/fakemodel/bench.py` (`recording_for(card, pages, number, answer,
  *, body=None)` passing `body` through `gates.messages`; `recordings_for` unchanged); `tests/conftest.py`
  (`split_card(card)` returning `replace(card, max_answer_tokens=65536 - (7164 + 64 + 8192 + len(system bytes) +
  16))` so the page budget stays 7164 bytes whatever the card size: measured, the 920-byte card plus 400 bytes
  already gives `[5, 4, 5]` and the derived budget gives `[5, 5, 4]` at plus 3000; review H2), used by
  `tests/test_bench_pipeline.py:202`, `test_pipeline.py:31` and `test_status.py:184`; `tests/test_cards.py` (new), `tests/test_matterinfo.py` (new), `tests/test_roles.py` (new), `tests/test_dates.py` (new), `tests/test_facts.py` (fields and the upgrade),
  `tests/test_schema.py:146-147` (`of 11`), `tests/test_extract.py` (the new name, a measured version),
  `tests/test_playbook.py` (the marking rules both ways), `tests/test_gate.py` (the row text), `tests/test_benchkey.py`,
  `tests/test_benchcandidate.py`, `tests/test_rules.py` (`rule5_forms=18 of 18` and `bills_forms=7 of 7`, §1.11 and
  §1.12), the `bench_extract` pins of D0.4 (`medical_memo`).
- Ships: `cards_loaded=15 of 15 schemas_loaded=11 of 11`, one `card <id> version=<12 hex> schema=<title>` line per
  card (versions measured; `02-C-OURDOC` text holds no `defense-doctor` entry: `practice_filtered=1`);
  `playbook_entries practice=13 samples=3`; gate `playbook PASS invalid=0 unmarked=0 practice=13 samples=3
  version=<measured>`; `rule5_forms=18 of 18`; `bills_forms=7 of 7`; `rules_selftest PASS misses=0 false_hits=0`;
  `dates_ok=9 of 9` (`03/11/2025`, `3/1/2025`, `2025-03-11`, `March 11, 2025`, `march 11, 2025` parse to
  `2025-03-11`; `13/01/2025`, `03/11/25`, `Yesterday`, the empty string give None); `matterinfo_ok=12 of 12` (no tables -> empty entries, `plaintiffs` 1, no roles; the fixture file -> every header value, two issues, one typed role; the intake layout with a `matter.toml` without `binders` loads and `pages.load` still reads `pages/`; `ask` with injected streams answering every prompt writes `[header]` and `[hearing].issues` and a second `load` reads them back; `ask` with a blank client name leaves it empty; `ask` with a non-tty stdin (an `io.StringIO`) writes nothing and returns the empty info; `write` keeps an existing `[roles]` table; refusals naming the key: unknown key, non-string value, an issue outside the type's list, unknown role, a binder the matter lacks, a `matter.toml` with `binders` beside `pages/` still refused as ambiguous); `roles_by_name=6 of 6` (`DME-report`, `defense_medical`, `Defense Medical Exam` -> `defense`; `medical`, `records`, `ime-free-notes` -> `ours`; a typed `[roles]` entry wins; `plaintiffs = 2` with no typed role -> `ROLE NEEDED`); `stamps_compatible=2 of 2` (the default config over the
  fixture passes; a config `stamp_pattern` of `[A-Z]{1,8}\d{3,}` over an intake layout with stamp `ABC123` is refused
  with the §1.5 sentence before the run log exists); `casefile_ok=17 of 17` (the 14 cases of round 5 with the new
  fields, plus: a round 5 case file (its `fact` and `cite` lines in the old shape) loads with `upgraded=N`, every
  old fact undated with category `other`, and `append` adds a new-shape event after it with the chain intact; an
  old-shape file with one edited interior line is refused as `_broken`; a `cite` event carrying a different date for
  the same quote on a second page loads with `dates == [d1, d2]`); `gate_cases=34 of 34` (the 31 of today plus
  `no_coverage`: a `coverage=False` card over two pages writes zero coverage rows; `required_any`: a card with
  `required_any=("questions",)` and an answer `{"questions": [{"text": "x", "cite": "MED0001", "quote": "Pain 7/10",
  "note": ""}]}` passes gate 6 with `optional_blank=("note",)` and fails it without; `echo`: a card with
  `echo="pages_seen"` passes on `{"pages_seen": [ids], "people": [], ...}` and fails when one id is missing); `no_reply_forms=3 of
  3` (doctor, memo, bench sentences); `recording_body_ok=1` (a `recording_for(..., body="Matter 9001.001\nFacts:\n...")`
  row answers a live-nonce request built with the same body); `fault_branches=3 of 3` (the three fault modes on an
  answer without `facts`); the full suite green with the memo producing today's layout (W4 changes it); both `--candidate` bench lines byte-identical to the baseline (dates are parsed and kept, not yet scored).
- CHECK: `scripts/run.sh pytest -q -s tests/test_cards.py tests/test_playbook.py tests/test_gate.py tests/test_rules.py
  tests/test_matterinfo.py tests/test_roles.py tests/test_dates.py tests/test_facts.py tests/test_schema.py tests/test_extract.py
  tests/test_gates.py tests/test_benchkey.py tests/test_benchcandidate.py tests/test_fakemodel.py
  tests/test_bench_pipeline.py tests/test_pipeline.py tests/test_status.py tests/test_fixture_matter.py` prints every
  line above and passes; `scripts/run.sh pytest -q` passes; `scripts/run.sh python -m casefile.gate` prints `0` and
  the new playbook row; `scripts/run.sh casefile bench --config config.example.toml --matters tests/fixtures/matters
  --candidate tests/fixtures/matters/9001.001/ideal.json` exits 0 with the baseline line, and with `flawed.json` exits 1 with the baseline line.
- Seeds, each alone: (a) `cards.text` omitting the practice block -> every card version differs from the pinned
  measured values, `test_cards` red; (b) a sample entry admitted into a card (`sample` filter dropped) -> the
  `02-C-DEFDOC` text holds `SAMPLE:`, red; (b2) the deponent filter dropped -> `practice_filtered=0`; (c)
  `playbook.py` accepting `sample = false` with `rule` starting `SAMPLE:` -> `test_playbook` red; (d) `matterinfo.load` accepting an unknown role -> `matterinfo_ok=11 of 12`; (d2) `roles.role` matching `dme` without folding `-` and `_` to a space -> `defense_medical` or `DME-report` reads `ours`, `roles_by_name` red; (d3) `ask` prompting on a non-tty stdin -> the `StringIO` case writes a file, red; (e) `check_stamps` called after `open_db`
  -> the three-digit case finds a run log, red; (f) `FIELDS["fact"]` without `provider` -> the fixture round trip
  red; (f2) the upgrade accepting any key subset (the `FIELDS_V1` equality loosened to `issubset`) -> the
  edited-interior-line case loads, red; (g) coverage rows written for a `coverage=False` card -> `no_coverage` red;
  (h) `optional_blank` ignored -> the `required_any` case red; (h2) the echo set compared by length -> the `echo` case with a wrong id of the same count passes, red;
  (i) the deposition-fee pattern dropped -> `rule5_forms=16 of 18`; (j) the first draft's `retain|hire|engage ...
  you` pattern restored -> four must-pass rows red; (j2) the provider mask applied to every rule -> `bills_forms`
  must-pass row 3 still passes but the control row (a provider named with `IME` in our words) passes too, red;
  (j3) the doctor pairing keeps `charges?` for questions -> `bills_forms=5 of 7`; (k) `no_reply_reason` keeping
  the page clause -> `no_reply_forms=2 of 3`; (l) `split_card` using the fixed `65536 - 16384` -> a different split
  with the new card, red; (m) `benchcandidate` refusing `date` -> the ideal bench run exits 2, red; (n)
  `recording_for` ignoring `body` -> `recording_body_ok=0`; (o) `pages.py` keeping the old ambiguity rule -> the
  intake-layout `matter.toml` case red.
- Librarian pre-flight: #R03-PC-3 (every caller in D0.4 and every pinned split site is listed and changed here; the
  commit is run green before the lanes split), #R01-OC-M2 (`required_any`, `coverage`, `numbers_in` default to
  today's behaviour; `optional_blank`, `echo`, `question_keys`, `providers` default empty), #R01-CX-7 and
  #R01-OC-H3 (both directions of every pattern change tested, the widened must-pass list), #R03-V-L1 (stamp and
  matter-entry refusals before the run log opens), #R05-CX-9, #R05-V-1, #R02-CX-5 (manifest ids and card names
  unique, refused otherwise), #R04-CX-7 (`cards.load` and `matterinfo.load` use `jsonrepair.loads` and `tomllib`
  only), #R01-OC-M7 (`matterinfo.load` never creates the file), #R04-PC-4 (the body-aware recording helper is the
  one builder for every stand-in row), #R05-PC-7 (the upgrade on load never rewrites a complete line), #R01-OC-M7 (`matterinfo.write` runs only after the attorney answered on a tty; a non-tty run creates nothing).

### W2 (lane A): dates and providers verified in gate 4, bench `dates_wrong`
- Files: `src/casefile/gates.py:93-158` (`_references`: the date and provider checks of §1.3),
  `src/casefile/benchscore.py:41-45,56-66` (`dates_wrong`, the detail line, `perfect`), `tests/fixtures/bench/flawed.json`
  (one wrong date on a found fact), the seven files pinning the bench line (D0.8) with `dates_wrong=0` (flawed:
  `dates_wrong=1`), `tests/test_gates.py:36-41` (`CASES` gains `date_ok`, `date_not_on_page`, `date_bad_form`,
  `provider_not_on_page`, `date_empty_ok`: `gate_cases=40 of 40`, `:90` `assert len(CASES) == 40`),
  `tests/test_benchscore.py`, `tests/test_bench_detail.py` (a `dates_wrong:` line pinned), `tests/test_stage4_exit.py`
  (the modes still act on `facts[0..2]`; the line's numbers do not move: `answers=+21` depends on the mode table, not
  the card; the builder prints and the chair confirms).
- Ships: `gate_cases=40 of 40`; bench baselines: flawed `bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14` exit 1 with a `  dates_wrong: <id> (<wrong> for <right>)` line; ideal `... found=29 of 29 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 ... pages_failed=0 of 14` exit 0; the stage 4 line unchanged in its
  numbers.
- CHECK: `scripts/run.sh pytest -q -s tests/test_gates.py tests/test_benchscore.py tests/test_bench_detail.py
  tests/test_bench_cli.py tests/test_stage4_exit.py` prints `gate_cases=40 of 40`, `invented_kinds=2 of 2
  rule_excerpt_ok=1`, the stage 4 line, and passes; the two `casefile bench --candidate` runs print the lines above.
- Seeds, each alone: (a) the date check skipped -> `date_not_on_page` passes gate 4, red; (b) `dates_wrong` counted
  but not in `perfect` -> the control is ideal with one key date changed by the test -> exit 0, red
  (`test_benchscore` case `date_only_fault`); (c) `provider` unchecked -> `provider_not_on_page` passes, red.
- Librarian pre-flight: #R03-PC-2 (one changed digit in a date is a fault: `date_not_on_page` uses `03/12/2025` on
  MED0001), #R04-CX-3 (the ladder's OCR rung joins letters only; a date never joins), #R04-V-2 (a date is matched on
  the page, not as a digit run in the quote), #R02-OC-H1 (the chair reads every key date on its page), #R04-PC-7 (a
  verified date confers nothing on the category label).

### W3: WITHDRAWN (the reconcile pass, owner Q55; §1.4)
Not built. The three-chunk bench test keeps `(29, 29, 5, 9, 3)`, the split `[5, 5, 4]` held by `conftest.split_card`, and prints `bench_chunks=3 found=29 of 29 flags=5 of 9 runs=+3 uncited=2` as today. `pipeline.batches` is built
in W5 where it is used. Numbering is kept so the review's dispositions still point at the right items.

### W4 (lane A, after W2): the memo's sections, conflict quotes, binder names, matter entries
- Files: `src/casefile/memo.py:85-154` (§1.5 sections; `_cite` `:55-56` returns a `Run(..., exempt="cite")`; the
  binder name in a `Run(..., exempt="binder")`; `check_binders` deleted at `:164-171` and its call at `render`
  `:192`; `build(casefile, pages, open_items, *, matter, playbook_version, model, info)` where `info` is the `MatterInfo`; the conflicts sentence of §1.4 with its added cloud
  sentence; `check` `:174-188` needs no change, it already drops every exempt run, review L1), `src/casefile/memo_job.py:58-59,87,91`
  (`matterinfo.load`, never `ask`; the header block through `outputs.header` once W5 lands: until the merge, memo keeps its own two-line title and the
  chair accepts the join at the merge; `check_binders` calls removed), `tests/test_memo.py` (`memo_docx_ok=22 of
  22`: the round 5 checks re-pinned to the new sections plus: chronology order by parsed date with a tie kept in
  case-file order; a fact in two topical sections; providers' first and last dates; an undated fact under `Facts
  without a date, by page`; an upgraded round 5 fact lands there too; the conflict entry's `From [cite A]:` quotes in
  case-file order; a `defense` against `ours` conflict first, a `defense` against `other` conflict not promoted, and
  the `ROLE NEEDED` sentence with no roles; the opinion sections' `ROLE NEEDED` line with no roles; the binder `ime`
  heading with the name in an exempt run and `rule_hits=0`; `memo_refused=1 of 1` (title case only)),
  `tests/test_status.py:112-129` (`binder_shown=1`: the `ime` matter runs, exit 1, the heading run reads `ime`),
  `tests/test_memo_intake.py` (sections; the scanned matter has no `matter.toml`, so every header field prints `NEEDED`), `tests/test_stage5_exit.py` (the four run lines, `answers=+4` and `casefile_lines=48` as today; only the memo lines move, reading `sections=15 chronology=31 dated=31 of 31 providers=<measured> conflicts=5 conflict_quotes_ok=1
  defense_first=1 header_ok=1 ...` (builder re-derives every number from the fixture)).
- Ships: `memo_docx_ok=22 of 22 memo_refused=1 of 1 memo_changed=1 memo_reason_exempt=1 binder_shown=1`; the stage 5
  lines as re-derived; the gate `0`.
- CHECK: `scripts/run.sh pytest -q -s tests/test_memo.py tests/test_status.py tests/test_memo_intake.py
  tests/test_stage5_exit.py` prints the lines and passes.
- Seeds, each alone: (a) chronology sorted by date string -> a `March 11, 2025` and a `03/14/2025` fact order red;
  (b) conflict quotes taken from the whole case file instead of the two pages -> check red; (c) `defense` against
  `ours` ordering widened to any other role -> the `defense` against `other` case promoted, red; (d) `_cite` at
  `memo.py:55-56` returning an unmarked run -> the `ime` matter refuses on `[page ime/001]`, `binder_shown=0`; (e) a
  fact with category `other` placed in `Diagnoses` -> red; (f) `check_binders` kept at `:192` -> `binder_shown=0`;
  (g) a missing role guessed from the binder name (`defense-report` treated as `defense`) -> the no-roles case
  shows no `ROLE NEEDED`, red; (h) an upgraded fact placed in the chronology with date `""` -> red.
- Librarian pre-flight: #R05-CX-3 (every fact has a place: chronology or the undated section or the absent-page
  section; the test asserts rendered facts equal the case file's), #R05-PC-12 (every reading and about rendered),
  #R04-CH-1 (quotes beneath a conflict come only from its two pages), #R03-OC-L1 (the `ROLE NEEDED` and `NEEDED`
  sentences name the file to edit), #R05-OC-1 (the memo omits itself from `Outputs out of date`, kept).

### W5 (lane B, worktree): the packet, the outputs framework and the report analysis
- Files: `src/casefile/packet.py` (new, §1.6: `Packet`, `PacketFact`, `build`, `body`, `to_json`, `from_json`,
  `batches`, with `pipeline.batches(blocks, budget)` as its byte splitter), `src/casefile/outputs.py` (new, §1.6:
  `Paragraph`, `Run`, `Section` moved from `memo.py` with `memo.py` importing them and nothing else moved, review
  L4; `Doc`, `header(info, ...)`, `check(doc, rules, stamped, providers)`, `render`, `publish` with the `.partial.docx` rule, `start` (with `matterinfo.load` and, on a tty with no `[header]`, `matterinfo.ask`), `ask`,
  `provider_pages(casefile, text)` for Q61, `open_items_section`, category groups as one table `GROUPS`),
  `src/casefile/report.py` (new, §1.7: `run(config, number, *, out, err, opener, ...)` and `render(answers, packet,
  casefile, pages, info, ...)`), `src/casefile/cli.py:37-40` (the `report` subparser: `--matter`, `--provider`,
  `--binder` (repeatable), `--pages`, `--defense`/`--ours` exclusive and required, `--config`),
  `cards/04-defense-report/g-concessions.md`, `cards/05-our-doctor/a-elements.md` (bodies; the schemas are W1's),
  `tests/test_packet.py` (new), `tests/test_outputs.py` (new), `tests/test_report.py` (new),
  `tests/fixtures/outputs/9001.001/concessions-defense-report.json` and `elements-okonkwo-lind.json` (invented answers read
  from the pages: concessions may include `DEF0001`'s `He acknowledges a 2019 episode of low back pain that
  resolved.` only as a danger-zone item, never as a concession; the elements answer marks `causation` STATED with the
  MED0008 opinion sentence, `treatment_reasonable_necessary_related` and `bills_reasonable_related` absent, so the
  document shows them NOT FOUND).
- Ships: `packet_ok=6 of 6` (every case-file fact with its first present cite and page id; `pages` exactly the
  cited pages; `body()` holds the task line, one fact line per fact with `[deponent's record]` on the named pages,
  then every page block; `to_json` and `from_json` round-trip to an equal `Packet`; `batches` splits a 300-fact
  packet with its pages so every body fits the retry budget; a page that alone exceeds the budget is refused with
  the `pipeline.chunk` reason); `outputs_ok=13 of 13` (header lines in order from the fixture `matter.toml`; a blank `hearing_date` prints `Hearing date: NEEDED`; a matter with no `matter.toml` run with a non-tty stdin prints every field `NEEDED`, writes no file and exits 1 for the open items without blocking (the test runs it under a timeout); a question paragraph
  checked with `unit="question"` and the case file's providers masked for the conjunction rule; a `binder` run
  exempt; `publish` writes through `.tmp` and appends one `output` event; `stale_outputs` lists the new name after a
  fact; `publish` with a failed step writes `<name>.partial.docx`, appends no event, and `status` shows the outputs
  unchanged (review M6); `start` refusals: no facts, bad `matter.toml` tables, incompatible stamp, each before the
  run log exists; a failed step disclosed as the section's first paragraph with exit 1; `ask` sends `packet.body()`
  and passes `packet.pages` for lookup; `provider_pages("okonkwo-lind")` returns `medical/007` and `medical/008` from
  the fixture case file and `provider_pages("nobody")` is empty); `report_ok=9 of 9` (`--defense` on
  `defense-report`: the three report pages' facts under their groups with dates, three conflicts (G3, G6, G9 cite
  report pages) with quotes beneath, concessions rendered with types, labels with `none stated` wording, danger zone
  with `Model's note`, the audit sentence, exit 0; `--ours --provider "Okonkwo-Lind"`: elements in fixed order, two
  NOT FOUND lines naming the pages, gaps listing treatment and bills separately, defense comparison with quotes,
  subjects only; `--ours --pages MED0007,MED0008` gives the same document; an unknown binder exit 2; `--pages` with
  an unknown stamp exit 2; `--provider` matching no fact exit 2 naming the providers on file; both side flags exit 2;
  a concessions answer with a quote not on its page fails gate 4, retried, disclosed, `.partial.docx`, exit 1), every
  rendering through `report.render` with answers loaded from the fixture files and a `None` entry for the failed
  case.
- CHECK: `scripts/run.sh pytest -q -s tests/test_packet.py tests/test_outputs.py tests/test_report.py` prints
  `packet_ok=6 of 6 outputs_ok=13 of 13 report_ok=9 of 9` and passes; the gate `0` (no `.docx` in the checkout:
  every file under `tmp_path`).
- Seeds, each alone: (a) `publish` writing the final path directly -> the `.tmp` case red; (a2) `publish` appending
  the event on a failed step -> the `.partial` case red; (b) NOT FOUND elements taken from the model's answer instead
  of computed -> the two NOT FOUND lines absent, red; (c) the failed step silently omitted -> the disclosure case
  red; (d) question paragraphs checked as `text` -> a seeded compound question passes `check`, red; (e) `start`
  opening the run log before `check_stamps` -> red; (f) `body()` leaving the page blocks out -> `packet_ok=5 of 6`
  and the recorded prompt 404s; (g) `render` calling the model (any `ask` inside `render`) -> the fixture-answer
  render case makes a request on port 9, red; (h) `header` printing a default instead of `NEEDED` -> the blank-field case red; (h2) `start` calling `ask` on a non-tty stdin -> the no-file case blocks or writes, red; (i) `provider_pages` matching on the fact text instead of `providers` -> the `nobody` case
  returns pages, red.
- Librarian pre-flight: #R03-V-L1 (refusals before side effects), #R03-CX-2 (`outputs/` created by this run only,
  tmp removed on failure), #R01-CX-9 (the audit sentence and every `NEEDED` claim only what ran), #R04-PC-7 (every
  model string labelled; a header value is shown with its cite), #R03-OC-L1 (every disclosure names the section,
  gate and reason), #R01-OC-M7 (never create the matter folder), #R05-OC-1 (a partial document is never current).

### W6 (lane B, after W5): the deposition package
- Files: `src/casefile/depo.py` (new, §1.8: `run` and `render(answers, packet, ...)`), `src/casefile/cli.py` (the
  `depo` subparser with `--provider`), `cards/02-depo/a-factsheet.md`, `c-client.md`, `c-defense-doctor.md`,
  `c-our-doctor.md`, `c-witness.md` (bodies of §1.8; the seed lists kept; the practice comes from the loader,
  filtered by deponent; the our-doctor card asks for the treatment question in the seed card's wording and the
  bills question in the skill's wording, naming the billing memo and every provider), `tests/test_depo.py` (new),
  the eight invented answer files of §1.10 for the two deponents (defense-doctor questions rest on the report's own
  words: `DEF0003`'s four opinion sentences, `DEF0001`'s records-reviewed list, `DEF0002`'s negative straight leg
  raise against `MED0007`'s positive one; no why, how or what-causes question; our-doctor primary holds the two
  separate questions, the bills question in the skill's wording naming every provider of the case file including
  `Ridgeline Physical Therapy`; the danger labels include `MED0003`'s 2019 lumbar strain).
- Ships: `depo_ok=12 of 12` (defense-doctor by `--provider "Marchetti"`: outline pages with the labelled facts and
  two page breaks; three question sections numbered with `Rests on:` quotes; danger zone and points for our expert
  with notes, quotes and cites; exit 0; our-doctor by `--provider "Okonkwo-Lind"`: the treatment and bills questions
  found, the bills question naming five providers and passing gate 5 with the case file's providers masked,
  `Missing:` absent; `--pages MED0007,MED0008` gives the same packet; a recorded primary answer without a bills
  question -> `Missing: the bills question ...` and exit 1; client without `--pages` runs on every page; our-doctor
  with neither `--provider` nor an override exit 2; `--taken-by defense` passes `taken_by=defense` in the packet's
  task line and the card's section meaning; a question with `IME` in its text fails gate 5 (the stand-in
  `forbidden_json` mode on a questions recording, W1's branch), retried, disclosed, `.partial.docx`, exit 1; a
  question whose `quote` is on another page fails gate 4; a question text holding a number absent from its cited
  page fails gate 4 (`numbers_in = "page"`); every output's name in `status` `outputs=`; `render` with the fixture
  answers and `None` for one section reproduces the disclosed document without a model).
- CHECK: `scripts/run.sh pytest -q -s tests/test_depo.py` prints `depo_ok=12 of 12` and passes.
- Seeds, each alone: (a) the treatment and bills check dropped -> the `Missing:` case red; (b) `numbers_in` read as
  `quote` for the questions card -> the control case puts the number on the page and not in the quote: red when the
  check reads the quote; (c) the deponent's pages not marked in the packet body -> the recorded prompt no longer
  matches, 404, red; (d) outline facts taken from every label including `none` -> the outline count case red; (e)
  `render` ignoring a `None` answer -> the no-model render case red; (f) the providers not passed to gate 5 -> the
  five-provider bills question fails the conjunction on `Physical Therapy`, the section is disclosed, red.
- Librarian pre-flight: #R04-CH-1 (a question's quote must be on its cited page), #R01-OC-H3 and #R01-CX-7 (the
  client question fixture includes `When were you hired by Quarry Ridge Logistics LLC?` and `Who hired you at the
  warehouse?`, which the rules must pass; the bills question is the measured must-pass of §1.12), #R03-OC-L1
  (`Missing:` and disclosures in words), #R01-CX-11 (exit codes 0, 1, 2 asserted).

### W7 (lane B, after W6): the hearing package
- Files: `src/casefile/hearing.py` (new, §1.9: `run` and `render(answers, packets, ...)`), `src/casefile/cli.py` (the
  `hearing` subparser with `--provider`), `cards/03-hearing/client-prep.md` (JSON body), `tests/test_hearing.py`
  (new), the invented answer files `factsheet-issue-1.json`, `factsheet-issue-2.json`, `client-primary.json`,
  `client-cross.json` (direct questions open and not leading, each resting on a record quote; cross questions on the
  2019 strain and the tote weight with both cites in the note).
- Ships: `hearing_ok=12 of 12` (the checklist first with the starred paragraph first and the totals sentence;
  exhibits per binder with stamp ranges (three binders); the two issues `permanency` and `termination` read from `matter.toml` with `STANDARD NEEDED`; `--issue "Only this issue"` overrides the stored list for the run and the file is unchanged; `--standard`
  typed overrides `STANDARD NEEDED`; our key facts and defense position from the labels; conflicts with a `defense`
  page first with quotes; client direct and cross sections and the instruction block last; consistency flags;
  doctor preparation's five parts by `--provider "Okonkwo-Lind"` with the elements shared with W5's fixture and the
  `not checked` sentence; closing per issue ending `Relief requested: RELIEF NEEDED` and the no-law sentence; no
  stored or typed issue -> the `Issues: NEEDED` sentence; `--doctor` with no provider and no override exit 2;
  `render` from the fixture answers without a model).
- CHECK: `scripts/run.sh pytest -q -s tests/test_hearing.py` prints `hearing_ok=12 of 12` and passes.
- Seeds, each alone: (a) the checklist placed after the outline -> red; (b) the starred paragraph's text changed by
  one word -> red (the practice entry's wording is the test's expectation); (c) consistency flags drawn from every
  conflict -> the count case red; (d) relief typed but not rendered -> red; (e) a run flag written back to
  `matter.toml` -> the file-unchanged case red; (f) stored issues ignored -> the two-issue case red.
- Librarian pre-flight: #R01-CX-9 (`none on file` and `NEEDED` sentences claim only what the case file and the
  matter entries hold), #R04-PC-7 (labels), #R03-OC-L1, #R01-CX-11, #R01-OC-M7 (a job never writes `matter.toml`).

### W8 (lane A, after the merge of lane B): the stage 6 exit test and the memo header
- Files: `tests/test_stage6_exit.py` (new, §1.10), `src/casefile/memo_job.py` (the memo's header through
  `outputs.header`; its title line kept), `tests/test_stage5_exit.py` (the header lines), `docs/loop/round-06/` (the
  chair's records, not the lane).
- Ships, printed with `capsys.disabled()`, every number asserted:
  `stage6 memo sections=15 chronology=31 dated=31 of 31 providers=<measured> conflicts=5 conflict_quotes_ok=1 defense_first=1 header_ok=1 rule_hits=0 exit=1`
  `stage6 depo=defense-doctor-us outline_our=<measured> outline_defense=<measured> questions=<measured> rests_on_page=<Q> of <Q> danger=<measured> points=<measured> forbidden_topics=0 rule_hits=0 header_ok=1 exit=0`
  `stage6 depo=our-doctor-us ... treatment_q=1 bills_q=1 compound=0 providers_named=5 of 5 rule_hits=0 header_ok=1 exit=0`
  `stage6 hearing checklist_first=1 starred=1 issues=2 standard_needed=2 client_direct=<measured> client_cross=<measured> elements=14 not_found=2 closing=2 relief_needed=2 rule_hits=0 header_ok=1 exit=1`
  `stage6 report=defense-report concessions=<measured> labels=<measured> danger=<measured> conflicts=3 conflict_quotes_ok=1 audit_limit=1 rule_hits=0 header_ok=1 exit=0`
  `stage6 report=okonkwo-lind elements=14 stated=<measured> partial=<measured> not_found=2 gaps_separate=1 rule_hits=0 header_ok=1 exit=0`
  `stage6 status outputs=memo:current,depo-defense-doctor-us:current,depo-our-doctor-us:current,hearing:current,report-defense-report:current,report-okonkwo-lind:current partial=0`
  `stage6 exit=0 docs=6 of 6 answers=+16 rule_hits=0 server_stopped=1`
  where `rests_on_page` counts questions whose `Rests on` quote is verbatim on the cited page (read from the
  fixture pages by the test), `forbidden_topics` counts question texts hitting any rule at `error` over the whole
  document with the case file's providers masked (0 by construction: the gates refuse them), `compound` the
  our-doctor question texts hitting `treatment-and-bills-apart` under the same mask, `providers_named` the case
  file's distinct providers found in the bills question's text (5 of 5, §1.12), `header_ok` the header paragraphs in order with the fixture `matter.toml` values (the deposition lines carry `--when` absent as `NEEDED`), `rule_hits` the firm rules over every non-exempt run,
  `conflict_quotes_ok` that every `From [cite X]:` block holds exactly the case file's quotes on X, `partial` the
  `.partial.docx` files under `outputs/`; `answers=+16` is one extraction call and fifteen synthesis calls; no prompt runs (stdin is not a tty). The memo exits 1 (DEF0001 uncited after one chunk, as stage 5 run 1); the hearing exits 1
  (`STANDARD NEEDED` and `RELIEF NEEDED` are open items); the others 0.
- CHECK: `scripts/run.sh pytest -q -s tests/test_stage6_exit.py` prints the eight lines with `stage6 exit=0` and
  passes; `scripts/run.sh pytest -q` passes; `scripts/run.sh python -m casefile.gate` prints `0`;
  `scripts/run.sh scripts/suite_time.sh 3` prints `verdict=PASS` (budget 90 s, T-11).
- Seeds, each alone: (a) a question fixture given a quote from another page -> `rests_on_page` short by one, the
  job writes `.partial.docx` and exits 1, `partial=1`, red; (b) the fixture's `client_name` blanked -> `Client: NEEDED`, `header_ok=0`; (c) `FakeModel.record` not registering -> 404,
  `docs=1 of 6`; (d) a rule-hitting word seeded into a section title -> the document is refused, exit 2, red; (e)
  the provider mask dropped from gate 5 -> the five-provider bills question is refused, `bills_q=0`, red (the
  measured collision of D0.9 is the control).
- Librarian pre-flight: #R01-P-1 (server stopped in `finally`), #R01-CX-11, #R05-PC-17 (the fixture matter copied
  under the test's root), #R03-PC-3 (every measured count derived by the builder, printed and read by the chair),
  #R04-OC-1.

### W9 (chair, at the close): records
- `docs/spec.md` §9 D44 to D51 (§6; D47 recorded as withdrawn), §2 memo sentence, §4 rules 4 to 6 sentences, §6
  (practice entries), §7 (the cards paragraph replaced), §11 stage 6 row; `docs/loop/tuning-questions.md` T-23
  (categories), T-22 updated (local path only); `Librarian.md` round 6 entries; ledger baselines (suite count, `suite_time`,
  gate `0`, the bench lines with `dates_wrong`, the stage 5 and stage 6 lines, `bench_chunks`); HANDOFF; the next
  round prompt.

## §3 Parallelisation map

- W1 first, one builder in the main tree, committed by the chair only after `scripts/run.sh pytest -q`, the gate and
  both `--candidate` bench runs are green on it (review H1); both lanes start from that commit (the gates, the case
  file fields and upgrade, the parsers, the loader, the matter entries and the terminal prompt, the roles by name, the rule changes, the
  stand-in helpers and the split budget are the shared contract).
- Lane A (main tree): W2, W4, in that order (W3 withdrawn); then W8 after the merge. Owns `src/casefile/gates.py`
  (`_references` only after W1), `memo.py` (`build`, `render`, the sections), `memo_job.py`, `status.py`,
  `benchscore.py`, the fixture `flawed.json` (its wrong date), and the tests `test_gates.py`, `test_bench_*.py`,
  `test_benchscore.py`, `test_memo.py`, `test_status.py`, `test_memo_intake.py`, `test_stage5_exit.py`,
  `test_stage6_exit.py`.
- Lane B (worktree `.claude/worktrees/r6-lane-b`, branch `r6/lane-b` from the W1 commit, toolchain
  `~/.casefile-dev/r6-lane-b`): W5, W6, W7, in that order. Owns `src/casefile/packet.py`, `outputs.py`, `report.py`, `depo.py`, `hearing.py`, `pipeline.py` (`batches` only,
  appended at the end of the file), the `cli.py` subparsers (lane A adds no subparser), the five output card bodies,
  `tests/fixtures/outputs/`, `tests/test_packet.py`, `test_outputs.py`, `test_report.py`, `test_depo.py`,
  `test_hearing.py`.
- Shared-file splits: `cli.py`: lane B adds three `add_parser` blocks after `:40` and three `elif` branches after
  `:70`; lane A does not touch it. `memo.py`: lane B moves exactly the `Paragraph`, `Run` and `Section` dataclasses
  (`memo.py:24-40`) to `outputs.py` and leaves `memo.py` importing them (`from casefile.outputs import Paragraph,
  Run, Section`); `OpenItem`, `Memo`, `label`, `build`, `check`, `render` stay where `status.py:31,37` finds them
  (review L4); lane A edits `build` and `render` only; the chair resolves the import at the merge. `gates.py`, `facts.py`, `dates.py`, `matter.py`, `pages.py`, `matterinfo.py`, `roles.py`, `rules.py`, `playbook/rules.toml`,
  `benchkey.py`, `benchcandidate.py`, `cards/manifest.json`, the four output schemas and `tests/fakemodel/core.py` are W1's and frozen after it: a lane that needs a change files it with the chair (one
  ruling, then one commit in the main tree that lane B merges). Fixture answers: lane B owns `tests/fixtures/outputs/`,
  lane A owns `tests/fixtures/matters/` and `tests/fixtures/bench/` after W1.
- Sequential and why: W1 before both lanes (contract, green); W4 after W2 (the chronology rests on gate 4's final
  date and provider checks); the merge of B into A's tip by the chair, then the full suite, gate and baselines; W8 after the merge (it joins every job); then the
  critic round.
- Interfaces fixed by this brief: `cards.card(id, book) -> gates.Card`; `gates.ask(card, pages, *, client, rules, log,
  matter, nonce=None, job, playbook_version, body=None, echo=None) -> Outcome` with `echo` a `(key, values)` tuple;
  `facts.Fact(id, quote, cites, page_ids, readings, reading_pages, dates, category, providers)`;
  `matterinfo.load(folder) -> MatterInfo(...)`, `matterinfo.ask(info, stdin, stdout)`, `matterinfo.write(folder, info)`; `roles.role(binder, info) -> str`; `rules.check(text, *, unit, stamped=True,
  providers=())`; `outputs.header(info, matter, kind, *, when="", deponent="")`; `outputs.provider_pages(casefile,
  text)`;
  `rules.check_stamps(pages, rules)`; `pipeline.batches(blocks, budget) -> list[list[str]]`; `packet.build(casefile,
  pages, *, matter, task, options, playbook_version, facts=None) -> Packet`, `Packet.body()`, `to_json`, `from_json`,
  `packet.batches(packet, card, num_ctx)`; `outputs.ask(packet, card, *, client, rules, log, job, playbook_version)
  -> Outcome`; `report.render`, `depo.render`, `hearing.render` `(answers, packet(s), casefile, pages, info, *, open_items,
  playbook_version, model) -> outputs.Doc`; `outputs.header(...)`, `check`, `publish(..., failed_steps)`,
  `start`; `extract.card(book=None)`; `FakeModel.record(row)`; `recording_for(card, pages,
  number, answer, *, body=None)`; `conftest.split_card(card)`.

## §4 Test design

- Regression set and what moves on purpose: `gate` 0; `unused_imports=0`; `suite_time.sh 3` under 90 s; doctor
  `runlog_schema PASS schema=2 triggers=21` (schema untouched); stage 1 to 3 lines unchanged; stage 4 line's numbers
  unchanged (the card name under `open` keys becomes `medical_memo`); stage 2 line unchanged (`stage2 exit=0 runs=+1
  answers_ok=+1 server_stopped=1`: one chunk, no reconcile call); the two `--candidate` bench lines keep the baseline main lines (14 pages, 29 facts) and gain `dates_wrong=` in W2 only; `bench_chunks` stays `[5, 5, 4]` with `flags=5 of 9` (W3 withdrawn); the stage 5 run lines, `answers=+4` and `casefile_lines=48` stay, only its memo lines move (W4); `gate_cases=31 of 31` -> `34 of 34` (W1) -> `39 of 39` (W2); `schemas_loaded=20 of 20` -> `11 of 11`; `memo_docx_ok=14 of 14 memo_refused=2 of 2` ->
  `22 of 22` and `1 of 1`; `binder_refused=1` -> `binder_shown=1`;
  `card_version` measured; `len(MODES) == 17` untouched (the three fault branches are inside existing modes); the
  playbook row gains `practice=13 samples=3`; the three-chunk split `[5, 5, 4]` is held by `conftest.split_card`
  from W1 on.
- New tables, each `*_ok=N of N` or a fixed line: `cards_loaded` 15, `schemas_loaded` 11, `rule5_forms` 18,
  `bills_forms` 7, `matterinfo_ok` 12, `roles_by_name` 6, `stamps_compatible` 2, `casefile_ok` 17, `no_reply_forms` 3, `dates_ok` 9,
  `fault_branches` 3, `recording_body_ok` 1, `practice_filtered` 1, `packet_ok` 6, `outputs_ok` 13, `report_ok` 9,
  `depo_ok` 12, `hearing_ok` 12, the eight `stage6` lines. Every N is fixed above; counts marked measured are
  printed and read by the chair before they are pinned.
- Every document check opens the produced `.docx` with python-docx and reads paragraphs, runs and page breaks
  (`run._r.xpath('.//w:br[@w:type="page"]')`); quote, cite and binder runs are separate runs so the tests tell
  verified text from code's labels and from the model's sentences.
- The stand-in: recordings for every call are built by `packet.build` plus `recording_for(..., body=packet.body())`
  (W1) and registered with `FakeModel.record` (W1), never by hand-written message JSON (#R04-PC-4); the modes that
  edit `facts[0..2]` keep working on the memo card (`_fault_content`, `tests/fakemodel/core.py:37-65`); W1 gives
  `bad_schema`, `forbidden_json` and `empty_answer` their branch for an answer without `facts` (`fault_branches=3 of
  3`), so lane B's gate 5 case runs at the split (review H4). Renderers are tested twice: through the job with the
  stand-in, and directly with answers loaded from `tests/fixtures/outputs/` and no model (the stage 7b restore path).
- Suite time (T-11): W8 adds six `run.sh` subprocess runs and six docx readings (about 4 s); W3's 300-fact case is
  in-process. Acceptance: `scripts/suite_time.sh 3` exits 0; if over, the second lever of T-18 is pre-approved; never
  a skip.
- Open for the code review (8a): the provider mask when a provider name is itself a treatment word alone (a
  binder named `therapy` as a provider); the upgrade on load when a round 5 file holds a torn tail; `batches`
  when one block alone exceeds the budget (refused with a reason,
  like a long page); concurrent `depo` and `memo` on one matter (both take the matter lock); the header's typed
  values against the rules when the caption itself names an examination service; `numbers_in = "page"` and a
  question quoting a page number that is also a stamp digit run.

## §5 Risks, each with a measurable tripwire

- R1 The practice port misstates a skill rule. Tripwire: the chair's read of every entry against its `learned`
  section before the lanes split, recorded in the agent log; the output critic's practice table in its report.
- R2 The terminal prompt blocks a non-interactive run, asks twice, or a binder-name role is wrong. Tripwire: `matterinfo_ok` non-tty case (nothing written, no block) and the `outputs_ok` no-file case under a timeout; `ask` never runs when `[header]` exists; `roles_by_name=6 of 6` with seed (d2); a multi-plaintiff matter prints `ROLE NEEDED` rather than a guess.
- R3 The provider mask or the question-only pairing lets a forbidden question through (a provider name that
  hides a treatment word, or `charges` in a memo sentence). Tripwire: `bills_forms=7 of 7` with its must-fail rows,
  `rules_selftest` unchanged, `compound=0`, `bills_q=1` and `providers_named=5 of 5` on the stage 6 line; the
  critic reads the bills question against the provider list; seed W1 (j2), (j3).
- R12 A document with a failed step is treated as current. Tripwire: `partial=0` on the stage 6 status line and
  `outputs_ok` case `.partial`; `status` never lists a `.partial.docx`.
- R4 Date verification refuses good answers whose page writes the date in a form `dates.parse` lacks (`11 March
  2025`, `3-11-25`). Tripwire: `gate.quotes` failures naming `.date` on the stage 9 benchmark; T-23 lists the forms.
- R5 The upgrade on load admits a corrupted old file. Tripwire: `casefile_ok` cases: an edited interior line of a
  round 5 file is still `_broken`; `upgraded=N` is printed by `casefile status` so an upgraded matter is visible.
- R6 The output cards' answers are invented by the builder to fit the tests, not the practice. Tripwire: the chair
  reads all 16 against the pages and the skill sections; the critic scores them; a question resting on a quote
  absent from the page cannot pass gate 4 (`rests_on_page=Q of Q`).
- R7 Two lanes both edit `memo.py`. Tripwire: the §3 split; the chair's merge runs the full suite before W8 starts.
- R8 A document lands in the checkout. Tripwire: the gate's privacy row after every chair run; every output path is
  under `[paths].matters` (D13); the exit test runs under `tmp_path`.
- R9 The stand-in's 404 on a prompt the job builds differently from the test. Tripwire: `docs=6 of 6`; a 404 shows as
  `gate.model` in the disclosed section and the line fails.
- R10 A test reaches 127.0.0.1:11434. Tripwire: `grep -rn 11434 tests` lists only `tests/test_config.py` rows; the
  chair's request-log delta at the merge and at the close.
- R11 Suite time over 90 s with six more subprocess runs. Tripwire: `suite_time.sh 3`; the T-18 lever.

## §6 Contradictions with the spec, plan or owner rulings, and the rows they become (pending veto)

- **D44** (spec §7's cards paragraph replaced; D34 and D39 amended for the names). Old text: "The 45 cards and 19
  schemas in `cards/` and `schemas/` were written before the single-model decision. Stage 6 updates them: single
  model; drop the brief outline, argument and authority-check cards; add the anonymization card and the medical memo
  card; build card text from the playbook." New: "Cards are JSON-only (every answer passes the schema gate) and
  engine-neutral (no card sentence names a message layout, server or model; a synthesis card's input is a fact
  packet of facts with quote, cite and page id plus the cited pages; every assertion in its answer carries a cite
  and a quote or the field does not exist); one loader (`cards.py`, manifest version 2) builds each card's text from
  the firm rules, the card body and the playbook's practice entries of its kinds and deponent; the manifest fixes
  per card the arrays of which one must be non-empty, the keys that may be blank, an echo key whose array must
  repeat the ids or page ids sent, and whether pages are marked read; 15 cards and 11 schemas remain (nine run by
  stage 6 jobs, one for stage 7, five for stage 8), the rest retired at `53a6f82`; the extraction card is `01-MEMO`
  (`medical_memo`); the anonymization card `07-ANON` finds names and the anchor date only, quote and cite each, and
  passes on an empty answer that echoes every page sent (Q47, Q53)." Why: §1.2, D0.3; review H3, L3, M3, M4.
- **D45** (D17 amended; spec §6 gains a sentence). "Practice entries ported from the firm's own skills carry `sample =
  false` and `learned = "firm skill <name> section N"`; sample entries keep the SAMPLE marking; the gate counts both;
  cards include practice entries only." Why: §1.1, D0.11; Q12 ("practice content is the owner's": the skills are).
- **D46** (D25, D28, D40 amended; spec §2 and §4 rule 4). "A fact carries `date`, `category` and `provider`; a
  non-empty date or provider is verified on the cited page by the ladder and a date must parse; the case file's
  `fact` and `cite` payloads carry them; a pre-round-6 payload is upgraded on load (undated, category `other`,
  bytes untouched) and any other shape is refused; the key's facts carry a date and the bench line gains
  `dates_wrong`." Why: §1.3; owner Q49 item 50; Q54 item 67.
- **D47** WITHDRAWN before build (owner Q55). The reconcile pass of the earlier drafts (a comparison card after each
  extraction chunk, Q49 item 56) is not built; a cloud task run sends the whole anonymized matter (stage 7b), which
  closes the cross-run and cross-chunk gap there. The memo's conflicts sentence gains `A cloud task run reads the
  whole matter (stage 7b).`; T-22 stays a measurement of the local path. Spec §3 step 5 and §4 gate 6 are
  unchanged by this row. Why: §1.4; ledger Q55; #R05-PC-1 stays open for the local path only.
- **D48** (D41 amended). "The memo's sections are spec §2's (chronology, providers, diagnoses, restrictions, history,
  opinions by binder role, gaps, conflicts, undated facts by page); each conflict shows the quotes of its two pages;
  conflicts between a `defense` binder and an `ours` binder come first and, with no such pair, the memo prints `ROLE
  NEEDED` and keeps the found order; binder names are shown as typed in exempt runs and `check_binders` is
  withdrawn; a binder's role is read from its name (`dme` or `defense medical`, any case or separator, is `defense`; every other binder is `ours`), with `matter.toml` `[roles]` as the override that a multi-plaintiff matter must supply (else `ROLE NEEDED`); `matter.toml` also holds `[header]` (matter type, client name, date of accident, treating physician, IAB hearing number, hearing date and time, plaintiffs) and `[hearing]` (`issues` from the type's list, `standard`, `relief`), read in both layouts by `matterinfo.load`; the header block prints those entries, `NEEDED` when empty; a page stamp the playbook's cite rule would reject refuses the job; the no-reply reason is
  transport-only and each command adds its own consequence." Why: §1.5; Q49 items 50, 54, 57; Q54 item 62; Q57 (superseding Q54 item 60 and Q56); #R05-CX-9; #R05-V-1.
- **D49** (new; spec §2 deposition, hearing and report paragraphs made concrete; §3 step 6). "`casefile report`,
  `depo` and `hearing` build Word documents in `outputs/` in three fixed steps: `packet.build` (facts with quote,
  cite and page id, the cited pages, the task's options, the playbook version; JSON round trip), `outputs.ask`
  (one gated model step per card) and `render(answers, packet, ...)` (code only, from the gated JSON answers, so a
  restored cloud answer renders through the same code): the header block of the firm's conventions,
  code-assembled sections from verified facts by category group, model steps limited to labelling facts (`02-A`),
  writing questions with a verified quote each (`02-C-*`, `03-CLIENT`), concessions, labels and danger items
  (`04-G`) and elements (`05-A`), every model string labelled; output cards mark no page read, must return at least
  one item, verify prose numbers against the cited page and question strings with the question unit; a failed step
  is disclosed in the document, which is written as `.partial.docx` with no output event (exit 1); the our-doctor
  primary section must hold a treatment question and a bills question or say which is missing; the checklist's
  starred billing memo item is first; the standard, relief and issues come from `matter.toml` `[hearing]`, a run flag overrides for that run, and an absent one is marked NEEDED; the doctor's own records are the pages of the facts whose extracted provider matches `--provider`, with `--binder` or `--pages` as overrides; at a task run with no `[header]` table, code asks the attorney on the terminal (matter type, client name, date of accident, treating physician, IAB hearing number, hearing date and time, issues from the type's list), writes `matter.toml` once and never asks again; a non-interactive run prints `NEEDED` and does not block." Why: §1.6 to §1.9; spec §2; the firm skills; owner Q53; Q54 items 61, 62; Q57; review H6, M1, M2, M6.
- **D50** (D16 amended). "`no-hired-paid-retained` also matches a fee paired with deposition, testimony or
  appearance, and `how often|frequently|many times ... retain`; the hire, engage, refer, `you`, share and split forms
  wait for the owner (question 64) because they block ordinary client and employment questions. Provider names
  (the packet's or the case file's extracted providers) do not count toward the treatment group of
  `treatment-and-bills-apart` (masked before that rule runs); `charges` and `bills` are exempt from the doctor
  pairing of `no-hired-paid-retained` in a question (the pairing keeps them for memo text through a
  `patterns_text_only` list; `charges?|charged` joins the `fees ... report` mirror), so the firm skill's bills
  question passes as written." Why: §1.11, §1.12, D0.9; review H5; owner Q54 item 59 (b) and (c).
- **D51** (new; D40 amended). "A case file written before round 6 is upgraded on load: a `fact` or `cite` payload
  with exactly the round 5 key set is read with `date ""`, `category "other"`, `provider ""`, counted as
  `upgraded`, its bytes and hash chain untouched; such facts are undated in every output; any other key set stays
  a broken chain." Why: §1.3; owner Q54 item 67; #R05-PC-7.
- No owner ruling is overridden. Q49's four answers are built as written, Q49 item 56 as superseded by Q55; Q54
  items 59 to 62 and 67 are built as answered, 63, 64, 65, 68 and 69 as the confirmed interims; 47, 48, 49, 51, 52,
  53, 55 and 58 interims are kept (an uncited page stays open; the quote is the verified text; rule ids beside messages; default styles;
  `[cite X]`; page-id cites with the warning; re-send every run; "defense report" shown). Q37: no bills are read.
  Q41: defense-against-ours first. Q57 withdraws D41's refusal sentence. The spec §7 exit test is unchanged.

## §6b Privacy

Every fixture this round adds is invented: the `[header]`, `[hearing]` and `[roles]` tables of the fixture's `matter.toml` (the fixture's invented claimant and treating doctor, an invented IAB number `1234567`, the fixture's invented accident date, an invented hearing date, issues from the fixed list); no page is added, the matter stays 14 invented pages; the dates, categories and providers added to `ideal.json`, `key.json` and
`flawed.json` are read from the invented pages; the 16 recorded answers under `tests/fixtures/outputs/9001.001/`
quote the invented pages only and name only the invented people and providers of those pages; the playbook entries
in `playbook/deposition.toml` and `playbook/hearing.toml` carry practice rules with placeholders (`[providers]`,
`[date]`) or the fixture's invented names in their examples, and no name, date or fact from the firm skills'
examples; `tests/test_packet.py`'s 300-fact case file is generated in the test. No PDF, image or Word file is
added to the repo; every `.docx` a test produces lives under `tmp_path`. Nothing under `~/local-worker/`, `~/Bench/`
or any `Cases/` folder was read; the three skill files were read for rules only.

## §7 Questions only the owner can answer (appended to `docs/loop/questions-for-owner.md` as 59 to 69; all answered by the owner, ledger Q54 and Q55, and built as §9 says; kept here as filed)

59. The deposition skill's suggested bills question ("Doctor, ... as to the bills themselves, the charges from
    [providers], ...") fails two firm rules as built: "Doctor" within 60 characters of "charges" trips the
    hired-paid-retained rule, and a provider named "... Physical Therapy" trips treatment-and-bills-apart, so any bills
    question that walks a provider list with a therapy provider is refused. Which governs: (a) the rules, with the
    question phrased "bills" not "charges" and therapy providers left out of the list, (b) exempt provider names from
    the treatment group, (c) exempt the words "charges" and "bills" from the doctor pairing in a bills question?
    Interim: (a); a refused question fails its section and the document says so.
60. Where do the header entries (caption, IAB hearing number, date of accident, hearing date and time, deposition
    date and time) and the binder roles (which binder is the defense examination, which holds our doctor's records)
    come from: a file `attorney.toml` you type in the matter folder (interim), the web page at stage 8, or the
    petition through a procedural card?
61. For a deposition or doctor prep, "the doctor's own records" are the binder or pages you name on the command line
    (`--binder`, `--pages MED0007,MED0008`). Should the system find them by the provider name the memo card extracts
    instead? Interim: named by you.
62. The hearing outline's issues, legal standard and relief are typed per run (`--issue`, `--standard`, `--relief`),
    else the document prints STANDARD NEEDED and RELIEF NEEDED. Keep them per run, or store them per matter in
    `attorney.toml`? Interim: per run.
63. The outputs show the model's suggestions (danger-zone reasons, points for our expert, "not in the record" lists,
    notes on questions) as "Model's note" with a cite. Keep them, or omit model suggestions and show verified material
    only? Interim: shown, labelled, cited.
64. The rules miss "What percentage of your practice is examinations for employers?" and "the split between employer
    and claimant requests"; blocking percentage, share and split words would also block the allowed clinical practice
    questions ("What share of your practice is treating patients?"). Should those forms be blocked whatever they ask
    about, or should the checker learn the deponent type so doctor questions get wider patterns? Interim: not blocked;
    the defense-doctor card forbids them in words; the fee-for-deposition and how-often-retained forms are blocked
    (D50).
65. The memo card's 24 fact categories (mechanism of injury, chief complaint, pain score, prior history, family
    history, comorbidity or social, exam finding, imaging result, diagnostic test, diagnosis, treatment rendered,
    medication, procedure, order or referral, work status, MMI statement, causation statement, impairment rating,
    future treatment, patient statement, compliance, records referenced, employment, other): any to add, merge or
    drop? Interim: the list (T-23).
66. The reconcile pass compares each new chunk's facts with every earlier fact in batches; on a large matter that is
    many model calls per upload (counted on the memo line). Acceptable, or limit it to defense binders against our
    records (your Q41 priority) or to facts of the same category? Interim: every pair, counted.
67. Case files written before this round are refused and must be rebuilt (delete `casefile.jsonl`; pages are re-read;
    the run log keeps every past run). Acceptable, given no real matter exists yet? Interim: refused with that message.
68. The seed cards' lists are kept as practice: the our-doctor topic order (qualifications, mechanism, history, exam
    and tests, diagnosis, causation, treatment, bills, work status, MMI and rating, future treatment), the client
    topics, the 14 elements of our doctor's report, the nine concession types, the client instruction block, and no
    page cap on the two-page outline. Confirm or edit? Interim: as in the seed cards.
69. When the defense takes the deposition, the question document's "primary" section is the defense's likely
    examination, "anticipated cross" is ours and "redirect" theirs; taken by us, the reverse. Is that the reading you
    want? Interim: that reading.

## §8 Plan review dispositions

Every finding was re-checked in the code on `53a6f82` or by a read-only probe through `scripts/run.sh python`
before it was accepted or rejected; the evidence is the file and line or the measured value.

| Finding | Disposition | Evidence and what changed |
|---|---|---|
| H1 W1 red at the split | ACCEPTED | `benchcandidate.py:46` `set(item) != {"cite", "quote", "text"}` raises; `benchkey.py:64-66` requires exactly `{id, cite, quote, text}`; the schema with `additionalProperties: false` would fail gate 3 on a six-field ideal. W1 now holds the candidate parser, the key loader, `dates.py`, the six-field schema and the fixture edits together, and the chair commits it only green (W1 CHECK: full suite, gate, both bench lines byte-identical); W2 keeps the gate 4 checks and `dates_wrong`. §2 W1, W2, §3. |
| H2 split moves at W1 | ACCEPTED | Probe reproduced: the 920-byte card plus 400 bytes gives `[5, 4, 5]`, plus 600 `[5, 4, 4, 1]`, plus 3000 `[3, 2, 2, 3, 3, 1]`; the derived budget `65536 - (7164 + 64 + 8192 + system + 16)` gives `[5, 5, 4]` at plus 3000. `conftest.split_card` in W1, used by `test_bench_pipeline.py:202`, `test_pipeline.py:31`, `test_status.py:184`; seed W1 (l). |
| H3 blank rule refuses optional notes | ACCEPTED | The brief's own §1.6 and §1.7, §1.8 texts conflicted. Manifest field `optional_blank` per card (`note` for `02-A`, the question cards and `03-CLIENT`; `absent_note` for `05-A`); a danger fact with an empty note renders `Model's note: none given`; W1 `gate_cases=34 of 34` covers the optional blank; seed W1 (h). §1.2, §1.6, §1.7, §1.8. |
| H4 lane B needs stand-in support after the merge | ACCEPTED | `tests/fakemodel/bench.py:14-18` has no `body`; `FakeModel.record` was W8's. Both, and the three fault branches for answers without `facts`, move to W1 (`recording_body_ok=1`, `fault_branches=3 of 3`); `tests/fakemodel/core.py` is frozen after W1. §2 W1, §3, §4. |
| H5 new patterns block client questions | ACCEPTED | Probe reproduced: the `retain|hire|engage ... you` pattern hits all four client sentences and `how ... refer` hits the supervisor sentence. Withdrawn; only the fee-for-deposition pair and `how often|frequently|many times ... retain` ship; must-fail 4, must-pass 14 including the reviewer's five (`rule5_forms=18 of 18`, measured); the hire, engage, refer and `you` forms join question 64. §1.11, D50, W1. |
| H6 renderers not separated from the model call | ACCEPTED | The first draft's §3 interfaces had no `render`. `report.render`, `depo.render`, `hearing.render` `(answers, packet(s), ...) -> Doc` are fixed interfaces; every renderer is tested from fixture answers with no model (W5 seed (g), W6 case and seed (e), W7); `publish(..., failed_steps)`. §1.6 to §1.9, §3, D49. |
| M1 ad hoc prompt per job | ACCEPTED | New `packet.py` (`Packet`, `build`, `body`, `to_json`, `from_json`, `batches`): facts with quote, cite and page id, the cited pages' text, options, playbook version; every output card's body is `Packet.body()`. The reconcile card keeps a facts-only body by the owner's "no re-send" (its fact lines carry page ids). §1.4, §1.6, W5 `packet_ok=6 of 6`. |
| M2 assertions without quote | ACCEPTED | `points_for_our_expert` becomes `{text, quote, cite}`; `missing` is dropped (gaps are the memo's flags); every item in every output schema carries `quote` and `cite`; prose (`note`, `why`, `absent_note`) sits beneath its item's quote and is labelled. §1.6, §1.8, D44. |
| M3 anonymization card cannot pass empty | ACCEPTED | `07-ANON`: `required_any []`, `echo "pages_seen"`, `anchor_dates` an array that may be empty; an answer echoing every page id with every other array empty passes gate 6. §1.2, W1 manifest. |
| M4 practice injected by kind only | ACCEPTED | Manifest `deponent` per card; the loader injects an entry only when its `deponent` is absent or equals the card's; `question-form` carries `deponent = "defense-doctor"`; `practice_filtered=1` asserts `02-C-OURDOC` holds no defense-doctor entry; seed W1 (b2). §1.2, D44. |
| M5 fixture dodges the therapy provider | ACCEPTED | `records/medical/003.txt`, `004.txt`, `007.txt` and `defense-report/001.txt`, `003.txt` name `Ridgeline Physical Therapy`; the §1.10 bills question omits it. The omission is now stated to the critic (§1.10), printed as `providers_omitted=1` on the stage 6 line, kept in the fixture's `note`, and controlled by seed W8 (e) (adding the provider makes gate 5 refuse the section). Question 59 unchanged. |
| M6 partial document published as current | ACCEPTED | `status.py:45-47` prints `<name>:current` for every `output` event. `publish` writes `<name>.partial.docx` and appends no event when any step failed; `partial=0` on the stage 6 status line; W5 `outputs_ok` case and seed (a2); risk R12. §1.6, D49. |
| M7 Q54 ordering widened | ACCEPTED | Q49 item 54 and Q41 say defense against our records. First group = conflicts with a `defense` page and an `ours` page; `defense` against `other` is not promoted (W4 check and seed (c)); the no-pair sentence names both roles. §1.5, D48. |
| M8 reconcile verification overstated | ACCEPTED | `gates.py:99-112` resolves cites, `:131-132` requires two distinct pages, `:143-149` reads `facts[].text` only. §1.4 and D47 now say exactly that; every reconcile `about` is `Model's reading`. |
| L1 D0.7 misreads `memo.check` | ACCEPTED | `memo.py:180-181` drops any run with a non-empty `exempt`; `:192` `render` calls `check_binders`. D0.7 corrected; W4 marks runs in `_cite` (`memo.py:55-56`) and the binder run, deletes the `:192` call, seed (d) targets `_cite`. |
| L2 counts disagree | ACCEPTED | W5 now says three conflicts (G3, G6, G9); W3 case (5) is a one-page conflict refused by `gates.py:131-132` with seed (g), replacing a case that could not go red. |
| L3 `ID_SENTENCE` names the prompt layout | ACCEPTED | `extract.py:20-22` says "the prompt_id line at the top of this message". Reworded to "the prompt_id value given in this request"; the proposal's nonce move (its §5) then needs no card change. §1.2, D44. |
| L4 what moves to `outputs.py` | ACCEPTED | `status.py:31,37` use `memo.OpenItem` and `memo.label`. Exactly `Paragraph`, `Run`, `Section` (`memo.py:24-40`) move; `OpenItem`, `label`, `Memo` and the functions stay. §1.6, §3. |
| L5 key dates on undated pages | ACCEPTED | `benchkey` requires the `date` key, allows `""` for a page that shows no date, and validates a non-empty one on the page; the fixture's 29 facts cite 11 pages, all dated (§1.3 lists them). W1. |
| L6 numbering stale | ACCEPTED | `docs/loop/questions-for-owner.md:312-381` holds 59 to 80. D0.13 corrected; W9 renumbers nothing; this revision adds no owner question. |

Counts: 20 accepted, 0 rejected, 0 owner. Decisions the review did not touch (§1.1, §1.3, §1.5 but for the
ordering, §1.10 but for the critic note, §1.12 to §1.14, D45, D46, D48 but for the ordering) are unchanged.

After the owner amendment (§9): H5's withdrawn patterns stay withdrawn; M5's `providers_omitted` interim is
superseded by Q54 item 59 (the bills question now names every provider and passes under D50); M8's statement and
every reconcile row (parts of H4, M1, L2 case (5)) describe work that D47 withdraws; the rest stands as written.

## §9 Owner amendment (ledger Q54 to Q56, 2026-10-28)

- Q55 direction: the reconcile pass is withdrawn (§1.4 rewritten, W3 marked WITHDRAWN, D47 withdrawn in §6; the
  `00-RECONCILE` card, `reconcile.schema.json`, `reconcile.py`, `compares=` and every reconcile count removed from
  W1, W4, W8, §3, §4, §5; `bench_chunks` keeps the measured loss; T-24 dropped from W9).
- Q55 direction: no continually-updated-memo behaviour is added; D0.2 names the stage 5 behaviours that stay as
  built (memo as a task run, only-unread chunking, re-send of open pages, What changed, Outputs out of date) and
  which stage 7b retires; §1.14 boundary extended; the conflicts sentence gains the stage 7b sentence (§1.4, W4).
- Q54 item 59 (b) and (c): provider names masked for the treatment group, `charges` and `bills` exempt from the
  doctor pairing in a question (§1.12 rewritten; `rules.check(..., providers=)` and `patterns_text_only` in W1 with
  `bills_forms=7 of 7` and seeds (j2), (j3); D50 extended; `providers_omitted` replaced by `providers_named=5 of 5`
  in §1.10 and W8; the fixture bills question names every provider, W6; risk R3 rewritten).
- Q54 item 60: the header comes from an invented petition page through the `00-HEADER` card (the seed
  `00-PROCEDURAL` rewritten), each value verified as a span of a quote on its page, a missing field `NEEDED`
  (§1.5, §1.6; W1 fixture `records/petition/001.txt`, `PET0001`, two key facts; W5 `header-petition.json`; W8
  `answers=+22`; D48; risk R2 rewritten; §6b).
- Q56 chair note: binder roles move from `attorney.toml` to `matter.toml` `[roles]` with `petition` added; no role
  prints `ROLE NEEDED` in the conflict order and the opinion sections (§1.5, W4 seed (g), D48); `attorney.py` and
  `attorney.toml` are not built (`matterinfo.py` replaces them; W1, §3 interfaces).
- Q54 item 61: the doctor's records are the pages of the facts whose extracted provider matches `--provider`, with
  `--binder` or `--pages` as overrides (§1.7, §1.8, §1.9; W5 `provider_pages`, W6, W7; the exit test uses
  `--provider` for both doctors; D49).
- Q54 item 62: issues, standard and relief stored in `matter.toml` `[hearing]`, a run flag overrides for the run
  and no job writes the file (§1.9, W1 fixture, W7 cases and seeds (e), (f); D49).
- Q54 item 67: old case files upgraded on load, not refused (§1.3; W1 `FIELDS_V1`, `casefile_ok=17 of 17`, seed
  (f2); D46 amended, new D51; risk R5 rewritten; W4 places upgraded facts in the undated section).
- Q54 items 63, 64, 65, 68, 69: interims confirmed, text unchanged (§1.6 labels, §1.11, §1.3 categories, §1.1 seed
  lists, §1.8 section meaning).
- Counts moved: cards 16 -> 15, schemas 12 -> 11, fixture pages 14 -> 15, key facts 29 -> 31, ideal 31 -> 33,
  `gate_cases` 34/39 -> 35/40, `casefile_ok` 16 -> 17, `outputs_ok` 11 -> 13, `report_ok` 8 -> 9, `depo_ok` 11 ->
  12, `hearing_ok` 10 -> 12, stage 6 `answers` +16 -> +22, stage 5 `answers` +4 -> +8 (a header call per run),
  recorded answers 15 -> 16; new tables `bills_forms` 7, `matterinfo_ok` 9; `attorney_ok` and `reconcile_ok` gone.
- No new owner question.
- Superseded by §10 (ledger Q57): the petition page, the `00-HEADER` card and its call per job, the `petition` role
  and the counts those moved (`answers`, pages, key facts, `casefile_lines`, `gate_cases` 35/40, `outputs_ok`
  header cases, `matterinfo_ok` 9).


## §10 Owner amendment 2 (ledger Q57, 2026-10-28)

- Binder roles by name: `dme` or `defense medical` in the binder name (any case; `-`, `_` or spaces between the
  words) is `defense`, every other binder `ours`; `matter.toml` `[roles]` is the override, required on a
  multi-plaintiff matter (`plaintiffs` > 1 else `ROLE NEEDED`) (§1.5; W1 `roles.py`, `roles_by_name=6 of 6`,
  seed (d2); D48; §3 interfaces).
- Header and issues from the attorney: the petition page (`records/petition/001.txt`, `PET0001`), the `00-HEADER`
  card and schema rewrite and its model call per job are dropped; `00-PROCEDURAL` stays a stage 8 card untouched;
  at a task run with no `[header]`, code asks on the terminal for matter type, client name, date of accident,
  treating physician (optional), IAB hearing number (optional), hearing date and time (optional) and issues from
  the type's list, writes `matter.toml` once, never asks again; run flags override; blank prints `NEEDED`; a
  non-tty run with no file prints `NEEDED` and does not block or fail (§1.5, §1.6, §1.10; W1 `matterinfo.ask`,
  `write`, `matterinfo_ok=12 of 12`, seeds (d3), (h2 in W5); W5 header cases; D48, D49; risk R2; §6b).
- Counts restored to the pre-amendment-1 values: fixture 14 pages, three binders; key 29 facts, ideal 31; the
  bench lines back to `found=26 of 29 ... pages_failed=0 of 14` and `found=29 of 29 ... of 14` (the W1 commit keeps
  them byte-identical; W2 adds `dates_wrong=`); `bench_chunks=3 ... flags=5 of 9 runs=+3`, split `[5, 5, 4]`;
  stage 2, 4 and 5 pins untouched at W1 and the stage 5 run lines, `answers=+4` and `casefile_lines=48` kept (only
  the memo lines move in W4); stage 6 `answers=+22` -> `+16`, recorded answers 16 -> 15; `chronology=31 dated=31
  of 31`; `gate_cases` 35/40 -> 34/39 (the `header_value` case gone); `outputs_ok` stays 13 (three header cases
  replaced); `matterinfo_ok` 9 -> 12; new `roles_by_name` 6; cards 15 and schemas 11 unchanged (`00-PROCEDURAL`
  back among the stage 8 five, nine cards run by stage 6).
- Q62's per-matter storage now holds the type's issue list; standard and relief unchanged (§1.5, §1.9).
- Everything else kept; no new owner question.
