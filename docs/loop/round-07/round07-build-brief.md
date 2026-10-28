# Round 7 build brief: stage 7 brief package and anonymizer (R7-1 to R7-4)

Revised 2026-10-28 after the adversarial plan review (`.workflow/scratch/round07-brief-review.md`, 3 high, 10 medium, 8 low;
dispositions in §8) and the owner's answers to questions 88 to 95 (ledger Q62: the defense examiner's company is kept,
`[DOB]` placeholder, `--pages all`, a Word draft for `brief-in`, an `adjuster` kind kept automatically; 90, 91, 92 keep
their interims). Written 2026-10-28 by the round 7 architect on `loop/round-07` at `6999988` (working tree: untracked `.agents/`,
`.claude/worktrees/`, `AGENTS.md`; leave them, HANDOFF leftovers). Scope (owner Q61, ledger `## Round 7`): R7-1 the
anonymizer under casefile-anon/1; R7-2 the brief package (spec §2) and re-import; R7-3 fact identity (critic 2 M1);
R7-4 binder role edge cases plus verifier test gaps S1, S3, S4. Exit test (spec §7 stage 7): "the identifier check passes
on the test matter; re-import fact-checks a draft". Out of scope: stage 7b (cloud client, sent-log, approvals, kill
switch, `[cloud]` config, run log v3, cloud stand-in), the stage 6 output follow-up (Q59 items 82 to 86, the format
specification, critic 2 M2 to M6). Tiers (owner Q46): Opus 5.5 orchestrates; Codex `gpt-6.1-sol` codes and fixes through
`codex exec` (builders never commit; the chair re-runs every CHECK and seed, runs the gate, commits); fresh Fable agents
do the plan review and the code review; Fable writes and revises this brief. Every run goes through `scripts/run.sh`; the
model is the stand-in `tests/fakemodel/`; tests default to `http://127.0.0.1:9` (`tests/conftest.py:41`) and no test may
reach 127.0.0.1:11434. Prose has no em or en dashes.

Privacy (hard rule, §6b): every page, name, date, number, placeholder and answer in this brief and in every fixture it
specifies is invented, built from `tests/fixtures/matters/9001.001/`. The one file read outside the repo was
`~/local-worker/anonymize.py`, for its code logic only (owner Q61); it holds string literals in its prompts, comments
and examples that look like personal names and a claim number, and it depends on `httpx`, `jsonschema`, a `compare`
module (OpenRouter), `/usr/share/dict/words` and a direct call to `127.0.0.1:11434` (`anonymize.py:148`): none of those
literals and none of those dependencies is ported. Nothing under `~/local-worker/` data folders, `~/.claude/uploads/`,
`Cases/` or `Bench/` was read.

Measured on the tip by this architect inside the sandbox through `scripts/run.sh` (quoted where used): the fixture key
holds 36 facts and 9 flags; its facts collide once under the folded-quote identity (`F05` MED0002 03/11/2025 and `F34`
DEF0002 06/20/2025, both "Straight leg raise negative bilaterally.") and zero times under folded quote plus date plus
folded provider; `ideal.json` (38 facts) collides once the same way, `flawed.json` (30) once (a MED0001 quote repeated
under the invented cite MED0099, which is `invented` not `found`); the key loader refuses only an equal cite and quote
pair (`benchkey.py:90-93`), so the key loads today. Fixture pages: 14, 440 lines by `wc -l` (422 text lines above the stamps), 75 `M/D/YYYY` dates of which 14 are
the invented date of birth and 61 are other dates, 5 bare years of which 3 sit inside the 3 occurrences of the
invented claim number (2 remain once the claim number is replaced whole: review M1), 46 surname occurrences of the 10
invented people (every full-name form contains its surname), 30 organization-name occurrences (7 invented
organizations: the employer 8, the six kept facilities and the examiner's company 22), 20 titled names (`Dr.` or `Mr.`
plus a capitalised word; the only surname-only titled form is one `Mr. <surname>`), 14 stamps, 0 hits of a state-bound
ZIP detector and 0 of a six-digit detector (the wage line `$11861.20` is the control, review M6); the reference code's id pattern hits nothing on the pages (the
claim number has no five-digit run), so the claim number is caught only by the name list. `ideal.json` quotes hold 7
dates and 0 names; 3 of its 9 flag abouts name a doctor.

## §0 Drift since the round 6 close (every premise verified in the code on `6999988`)

- D0.1 **Owner answers landed.** Ledger `## Clarified` Q60, Q61 and `## Round 7` R7-1 to R7-4 are committed (`6999988`
  "Spec: D44 to D62 ratified"); `docs/spec.md` §9 D44 to D62 read `ratified by the owner 2026-10-28 (ledger Q61)`.
  Uncommitted at this revision: `.workflow/LEDGER.md` (Q62 appended), `docs/loop/questions-for-owner.md` (88 to 95
  appended and marked answered; W6 appends nothing twice, review L5), untracked `docs/loop/round-07/` (the review's
  tracked copy) and the three HANDOFF leftovers.
- D0.2 **The spec's D rows were added but the section text they amend was not.** D55 says §3 gains step 7; `docs/spec.md:49-58`
  still lists six steps. D57 says the §5 Anonymizer row is amended; `docs/spec.md:97` still reads `Presidio plus the matter's
  own name list; the identifier check blocks any leak`. D54's §2 cloud paragraph and D56's §4 closing sentence are absent
  too. The stage 7 parts (step 7's first half, the Anonymizer row) are applied at W6 (§6); the 7b parts stay as rows.
- D0.3 **The anonymization card exists and no job runs it.** `cards/07-anonymize/entities.md` (one paragraph: names of
  people, organizations, places and the injury anchor date; `pages_seen`; each hit with `quote` and `cite`; "Code does every
  replacement and date conversion"), `schemas/anonymize.schema.json` (`pages_seen [string]`; `people [{name, kind enum
  claimant|doctor|attorney|person, quote, cite}]`; `organizations [{name, kind enum employer|insurer|provider|other, quote,
  cite}]`; `places [{name, quote, cite}]`; `anchor_dates [{date, quote, cite}]`; every key required,
  `additionalProperties: false`), manifest row `07-ANON` (`job null`, `stage 7`, `required_any []`, `echo "pages_seen"`,
  `coverage false`, `numbers_in "page"`; `cards/manifest.json`), version pin `07-ANON: bd075ed6a208`
  (`tests/test_cards.py:12`). Gate 6 with `card.echo` compares the echoed set with the page ids sent (`gates.py:290-294`)
  and skips `required_any`; blanks are still refused (`:298-311`). Gate 4 checks each `quote` on its cited page
  (`gates.py:119-130`) but never checks that `name` lies inside `quote` or on the page; gate 5 runs the firm rules over
  every string but `quote, cite, cites, prompt_id, end_id` (`gates.py:17`), so a `name` holding `IME` would fail the
  answer (`schemas/anonymize.schema.json` is the only schema with a `name` key, measured by grep).
- D0.4 **The packet is the unit a task sends.** `packet.Packet(matter, task, options, playbook_version, facts, pages, flags)`
  (`packet.py:22-30`); `PacketFact(id, quote, cite, page_id, date, category, provider, text)` (`:10-19`); `body()`
  renders `Matter N`, the task line, one fact line `[F12] MED0003 (medical/003; 03/14/2025, prior_history): "quote"`,
  then `extract.page_block(page)` for every page (`:32-51`; `extract.py:19-20` gives `=== PAGE <id> BATES <stamps> ===`);
  `to_json`/`from_json` round-trip (`:53-62`). `build` takes every case-file fact with its first present cite and the
  pages those facts cite (`:65-83`). `options` carry attorney-typed strings (`name`, `when`, `issue`, `standard`, `relief`;
  `depo.py:115`, `hearing.py:24`) and `bills_providers` (`depo.py:20`); `flags` carry the model's `abouts`.
- D0.5 **The gates and the stand-in.** `gates.ask(card, pages, *, client, rules, log, matter, nonce=None, job, playbook_version,
  body=None, echo=None, providers=())` (`gates.py:196-197`); `messages()` puts `prompt_id: <nonce>` first in the system
  message and the body (or `Matter N` plus page blocks) in the user message (`:61-65`); coverage rows only when
  `card.coverage` (`:351-360`). Stand-in: `FakeModel.record(row)` (`tests/fakemodel/core.py:96-99`), `recording_for(card,
  pages, number, answer, *, body=None)` (`tests/fakemodel/bench.py:14-18`), `MODES` 17 (`core.py:12-14`), `_fault_content`
  handles answers without `facts` for `bad_schema`, `forbidden_json`, `empty_answer` (`:39-51`). A request with no
  recording is a 404 (`:170-171`), which `ModelClient` raises as a received `ModelError` and `gates.ask` records as
  `gate.model` (`gates.py:229-234`).
- D0.6 **Fact identity today.** `facts.merge` keys facts by `quotes.fold(fact.quote)` (`facts.py:255`, `:271`); a repeated
  quote on a new page adds a `cite` event carrying its own `date` and `provider` (`:281-287`) and a `reading` when the
  text differs per page (`:288-291`). `Fact(id, quote, cites, page_ids, readings, reading_pages, dates, category, providers)`
  (`:34-44`). Event kinds are the seven of `FIELDS_V1` (`:56-65`); `FIELDS` adds `date, category, provider` to `fact` and
  `date, provider` to `cite` (`:67-68`); `_decode` refuses any other key set except the round 5 shapes, counted as
  `upgraded` (`:183-193`). The view (`CaseFile.facts`, `:97-116`) and every renderer place a fact by its first present cite
  (`outputs.fact_paragraphs`, `outputs.py:360-372`; `memo.build`, `memo.py:110-120`); the critic's M1 is exactly that:
  `F34`'s DEF0002 finding sits under the 03/11/2025 ER entry as `Also cited: [cite DEF0002]`. Pins that move with the
  identity (measured): `tests/test_stage5_exit.py:30-38` (`facts=37`, `facts=38`, `chronology=37 dated=37 of 37`,
  `dated=37 of 38`, `casefile_lines=56`, `expected_line_count = (50, 52, 55, 56)` at `:231`), `tests/test_stage6_exit.py:25`
  and `:297` (`chronology=37 dated=37 of 37`, `facts=37`), `tests/test_status.py:61-65` (`facts=37`), `:100` and `:176`
  (`facts=38`), `tests/test_bench_detail.py:18` unchanged (bench `found` compares cite plus quote, `benchscore.py:96-99`).
- D0.7 **Roles today.** `roles.role(binder, info)`: a typed `[roles]` entry wins; `plaintiffs > 1` gives `ROLE NEEDED`;
  then `re.sub(r'\b([di])[\W_]*m[\W_]*e', r'\1me', ...)`, separators to spaces, and `re.search(r'\b(?:dme|ime)|\b(?:defense
  |independent) medical\b', name)` (`roles.py:6-13`). The first alternative has no trailing boundary, so `imelda health`
  is `defense` (verifier finding 7); `time-records` is `ours` (no boundary before `ime`). `tests/test_roles.py` pins
  `roles_by_name=6 of 6` (`DME-report`, `defense_medical`, `Defense Medical Exam`, `ime-free-notes` defense; `medical`,
  `records` ours). `matterinfo.ask` returns at once when `[header]` exists (`matterinfo.py:127-128`) and never asks for
  roles; `outputs.start` calls `ask` only when `not info.has_header and stream.isatty()` (`outputs.py:313-314`);
  `outputs.needed` prints `ROLE NEEDED: <binder>` for a role outside `ours, defense, other` (`outputs.py:342-348`);
  `memo.build` prints its own `ROLE NEEDED` sentences (`memo.py:141-146`, `:173-175`). `matterinfo.load` refuses any top-level
  key outside `number, binders, header, hearing, roles` (`matterinfo.py:52-54`; `matter.py:60` the same); `matterinfo.write`
  rewrites every table one level deep with `json.dumps` values (`:103-110`), so a nested table would be written as JSON
  and not reload.
- D0.8 **The three verifier gaps.** S1: `cli.py:127-130` passes `doctor=args.doctor, closing=args.closing`; no test drives
  `cli.main` for `hearing`, so swapping them stays green (`tests/test_cli.py` has five subprocess tests, none for
  `hearing`; `tests/test_hearing.py` calls `hearing.run` directly). S3: `schemas/questions.schema.json:32-37` requires
  `text, cite, quote, note`; no test asserts it; `outputs.evidence` indexes `item['quote']` unguarded (`outputs.py:91`).
  Measured over `schemas/*.json`: 16 object schemas carry a `quote` property, 15 require `quote` and `cite`, one (the stage
  8 `procedural.schema.json` `deadlines_stated` items: `date, quote, what`) requires no `cite`; over the six schemas the manifest
  lists at stage 6 or 7 the count is 13 of 13. S4: `cards/02-depo/c-our-doctor.md:21` "Topics 7 and 8 are ALWAYS two separate
  questions. Never combine them." is guarded only by the version pin (`tests/test_cards.py:29`).
- D0.9 **Privacy row.** `privacy.scan` flags `Cases`/`Bench` first components, unsafe links and binary suffixes outside
  `tests/fixtures/` (`privacy.py:30-39`); nothing about `anon/`, `key.json` or `sk-ant-` (D62, ratified, "can land earlier").
  Measured for the rule (review H1): `privacy.paths` lists tracked and untracked files (`privacy.py:11`, `--cached
  --others`), so the bench key `tests/fixtures/matters/9001.001/key.json` (tracked, D25) and this ignored brief are in the
  inventory; a bare `key.json` rule would flag the key, a bare `sk-ant-` rule would flag `docs/spec.md:280` and
  `docs/loop/design/cloud-roundtrip-proposal.md` (the D62 row and P11). Measured: 0 inventory paths end in `anon/key.json`;
  0 files match a key-shaped `sk-ant-[A-Za-z0-9_-]{20,}`. The rule is scoped so (§1.13).
- D0.10 **Matter folder and jobs.** `outputs.start` takes the matter lock, loads the case file, refuses `no facts` with
  `run casefile memo first`, checks stamps, loads `matterinfo`, opens the run log and the model client (`outputs.py:296-318`);
  `publish` writes `outputs/<name>.docx` through `.tmp` and appends one `output` event (`:192-220`). `runlog.record_approval`
  exists and has no production caller (`runlog.py:111-116`; stage 7b). `config.KNOWN_KEYS` has `paths, model, ocr` only
  (`config.py:30-34`); nothing is added this round.
- D0.11 **Numbering.** Spec §9 ends at D62 (next D63); owner questions end at 87 (next 88); ledger round 7 items R7-1 to
  R7-4; worktrees `r4-lane-b`, `r5-lane-b`, `r6-lane-b` still exist (`git worktree list`), lane B gets `r7-lane-b`;
  tuning entries end at T-22 in `docs/loop/tuning-questions.md` (round 6 said T-23 would be added; it was not; the
  chair numbers the next entry by that file at W6). Baselines: `786 passed`, gate `0`, `unused_imports=0`, bench lines and
  stage lines as in ledger `## Project`.

## §1 Decisions, with trade-offs

- **1.1 One module does every exact step; the model only finds names and the anchor date (Q47, Q61).** New
  `src/casefile/anon.py`, pure code with no model call: `Key` (the matter's placeholder table), `names(info) -> NameList`,
  `mapping(namelist, hits, pages, key) -> Key`, `text(value, key, *, protected) -> str`, `packet(packet, key) -> Packet`,
  `check(data, key, namelist, pages) -> Verdict`, `restore(value, key) -> str`, `restore_quote(quote, key, page) -> str |
  None`, `load_key(folder)`, `save_key(folder, key)`. The model runs twice through `gates.ask` with card `07-ANON` and
  nothing else: an entity pass over the packet's real pages, and a second pass over the anonymized pages (the identifier
  check's step 4). Everything between and after is code (pillar 4; the convention's decision 2). Rejected: Presidio or
  GLiNER-PII as a detector this round (D57 says optional, second; a dependency with no benchmark yet, pillar 6; the
  owner's convention makes code the replacer); the reference script's shape (it reads whole files, calls a server
  directly and caches model answers in the output folder; our pass runs through the gates so a cut, malformed, off-page or
  rule-breaking answer is refused like every other answer, #R01-CX-5, #R04-PC-6).
- **1.2 The name list is the attorney's; the model proposes; a new name halts (Q53 mode A, pillar 5).** `matter.toml`
  gains `[anon]` (`employer` string; `ids`, `places`, `keep` arrays of strings) and two sub-tables `[anon.people]` and
  `[anon.organizations]` (name to kind: `claimant|doctor|attorney|adjuster|person`; `employer|insurer|provider|other`; the schema enum gains
  `adjuster`, owner Q62 item 95). The header
  feeds the list without retyping: `client_name` is the claimant, `treating_physician` a doctor with its title stripped
  (`Dr. Priya Okonkwo-Lind` enters as the name without `Dr.`, so the title stays outside the brackets: review L6),
  `iab_hearing_number` an id (Q61). `[anon]` also holds `dob` (the claimant's date of birth as typed, owner Q62 item 89);
  people kinds are `claimant|doctor|attorney|adjuster|person`, organization kinds `employer|insurer|provider|other`. `anon.names(info)` merges them; `matterinfo.load` admits the table (refusing an unknown key, a non-string, an
  unknown kind, exit 2 naming the key as today), `matterinfo.write` learns to write one level of sub-tables (D0.7). At a
  `brief-out` run the entity pass's hits are compared with the list by folded whole token (`quotes.fold`, #R03-CX-5): a
  hit whose `name` is not found on its cited page by `quotes.found_in` is dropped and logged (pillar 1); a hit already on
  the list confirms it; a new hit on a tty prompts the attorney once per name (`anon.ask(namelist, hits, stdin, stdout)`:
  the kind the model proposed as default, `keep` as a choice) and writes `[anon]` once; a new hit with stdin not a tty
  prints `NAME LIST NEEDED: <n> names found on the pages are not in matter.toml [anon]: <name> (<kind>, <cite>) ...` and
  exits 2 before any replacement, any key write and any package (the names are printed to the attorney's own terminal,
  never to a file: #R03-OC-L1 wants the remedy named, and the terminal is inside the matter's boundary). Rejected: trusting
  the model's list as the replacement set (a missed or mis-kinded name would leak by design; #R02-OC-H1's class); a
  separate `names.txt` (the reference's `--names`; the matter already has one attorney file).
- **1.3 The anchor date is the typed date of accident; the model's anchor is a check, not a source.**
  `[header].date_of_accident` parsed by `dates.parse` is the anchor (the owner types it once, Q57); when it is empty the
  entity pass's `anchor_dates` (each verified: the quote is on its page and `dates.parse(date)` equals a date written in
  that quote) vote and the majority wins, logged; neither gives `ANCHOR NEEDED: add date_of_accident to matter.toml
  [header]` exit 2. When both exist and disagree the run prints `anchor: the pages say <model date> at <cite>; matter.toml
  says <typed>` as a warning and uses the typed date (pillar 5). Fixture: `03/11/2025`. Rejected: the model alone (the
  reference's default; the typed date exists and is the attorney's word).
- **1.4 Replacement, ported logic (casefile-anon/1).** `anon.text(value, key, *, protected)` applies, in this order and
  per line so the line count never changes: (1) bracketed tokens already in the text that match the convention's grammar
  become `[SRC-n]` and are restored as written; (2) pattern detectors email, SSN, phone, street address, ZIP, claim-style
  ids (letter groups and digit groups with a five-digit run, or six or more digits alone) become `[EMAIL-n]`, `[SSN-n]`,
  `[PHONE-n]`, `[STREET-n]`, `[ZIP-n]`, `[ID-n]`; (3) every value in `[anon].ids` and the IAB hearing number become
  `[ID-n]` as whole tokens (the fixture's claim number is caught here and only here, measured; its inner `2025` goes with
  it, so the bare-year count on the fixture is 2, review M1), and every spelling of `[anon].dob` and any date on the same
  line after a `DOB` or `Date of Birth` label becomes `[DOB]` (unnumbered, owner Q62 item 89; measured 14, all after the
  label); (4) dates: `M/D/YYYY`, `YYYY-MM-DD`, `M-D-YYYY`, month-name forms with a year become `[DATE D+n]` with `n` the
  day offset from the anchor, the reader allowing one line break before the year and keeping that break after the tag so
  the line count holds (review L8; the same reader serves the check, #R04-PC-4); a month name with a year becomes
  `[MONTH M+n]`; a bare year 1930 to 2049 becomes `[YEAR Y+n]`; a capitalised month name with a day and no year becomes
  `[DATE-REF-n]` kept in the key; the ZIP detector of step (2) fires only after a two-letter state code and a space, and
  the digit-only id detector needs six digits alone, so the wage line `$11861.20` is untouched (measured 0 hits, review
  M6); (5) names by variant, longest first, matched as written or
  in capitals only, as whole tokens (`(?<![\w\[])...(?![\w\]])`), titles and credentials left outside the brackets:
  `[CLAIMANT]` for the claimant (unnumbered), `[DR-n]` doctors, `[ATTY-n]` attorneys, `[PERSON-n]` other people,
  `[EMPLOYER]` for the organization named in `[anon].employer` (unnumbered, Q61), `[ORG-n]` for organizations of kind
  `other`, `[PLACE-n]` places; people of kind `adjuster`, organizations of kind `insurer` or `provider` and every `keep`
  entry are never replaced (Q61 and Q62: carrier, adjuster, treating facilities and the defense examiner's company stay;
  the fixture lists the examiner's company as `provider`). Variants of a person: the full name, the surname, both in capitals,
  every hit form with its title stripped; a given name alone only when a hit names it alone (no dictionary). Numbers are
  assigned by first appearance in the packet's page order on the first run and never reused: the key is append-only, so a
  second package on the same matter gives byte-identical placeholders. Protected tokens, never replaced by any step: every
  stamp of every page (raw and normalised), every page id, the `=== PAGE ... ===` lines, and `[cite X]`/`[page x/001]`
  runs. Rejected: dictionary-based filters (`/usr/share/dict/words` is a machine dependency and the owner's list decides);
  numbering per package (the drafter and the key would disagree across packages).
- **1.5 The identifier check runs on the exact bytes that would leave and fails closed, reporting kind and offset,
  never the value (proposal §4; D52, D55).** `anon.check(data: bytes, key, namelist, pages) -> Verdict(ok, hits)` with
  `hits` a tuple of `(step, kind, offset)`: step 1, every variant of every replaced entity of the key, every `ids` value, the IAB number and every
  spelling of the `dob` absent at every rung of the quote ladder's folding and as a whole token (`quotes.fold`; kept
  kinds and `keep` entries are not searched: on the fixture the six kept organizations occur 22 times, review M5); step 2, no absolute date in any form of
  1.4 (4) remains; step 3, the pattern detectors of 1.4 (2) find nothing, and no `Dr./Mr./Mrs./Ms.` followed by a
  capitalised non-placeholder word remains (`titled_name`); step 4, the second entity pass by the local model over the
  anonymized pages (same page ids and stamps, anonymized text) returns no person, organization or place that is not in
  `keep`, and a model failure at this step is a block, not a pass; step 5, every bracketed token is a placeholder of the
  key, a generic form with a literal `n` (`[DR-n]`, `[DATE D+n]`, `[DATE D-n]`, `[MONTH M+n]`, `[YEAR Y+n]`,
  `[DATE-REF-n]`, `[ID-n]`, the unnumbered `[CLAIMANT]`, `[EMPLOYER]`, `[DOB]`: the drafter rules need them, review
  H3), or a cite run `[cite <stamp>]` or `[page <page id>]` naming a page of the packet; no loose tag (`[DR 3]`,
  `[Dr-3]`, `[DATE]`) remains. Stamps and page ids are exempt from steps 2 and 3. Steps
  1, 2, 3, 5 run before step 4 so no model call happens on bytes code already rejects. A block: nothing is written under
  `outbox/`, the run log holds `failures` rows `gate.identifier` with `step=<n> kind=<k> offset=<o>` on the entity pass's
  run, the job prints the same and exits 1. Measured expectation on the fixture after replacement: 0 hits (the exit test
  prints `leaks=0`). Rejected: a hit count threshold (pillar 2); printing the leaked value in the log (#R06-CX-1's class).
- **1.6 Restore is page-aware for quotes, canonical for prose.** `anon.restore(value, key)` replaces every placeholder
  with its canonical value (people: the full name, with `Dr. [DR-1]` giving `Dr. <name>` once; dates `M/D/YYYY` from the
  anchor; month and year forms by arithmetic; `[DATE-REF-n]`, `[ID-n]` and every ref from the key; `[SRC-n]` last) and
  fixes the shortened forms the reference counts (`DR-3`, `D+469`). `anon.restore_quote(quote, key, page)` restores a
  quoted span so that it is on its real page by the ladder: for each placeholder occurrence it tries the entity's variants
  (and for a date the spellings of that offset the key saw in this matter) left to right, keeping a prefix only while
  `quotes.found_in(prefix, page.text)` holds, and returns the first full restoration the ladder accepts or `None`.
  Why: the fixture writes every date as `MM/DD/YYYY` and one page writes `Mr. <surname>`, so a canonical restore
  (`3/11/2025`, `Mr. <full name>`) would fail the restore check on every page (measured: the convention's `M/D/YYYY`
  matches none of the 75 page dates); the key therefore records every date spelling it replaced, per offset, append-only.
  The round trip `anon.text` then `anon.restore_quote` on each fixture page reproduces the page bytes (`anon_pages=14 of
  14`). Rejected: a date rung in the quote ladder (D35 is ratified and the bench numbers rest on it; a folding that maps
  dates would widen every quote check); dropping any quote a canonical restore misses (proposal §4 accepts drops; here
  that would drop most of the matter).
- **1.7 The restore check (`gate.restore`) is a code gate with the proposal's five parts and runs on `brief-in` now,
  on cloud answers at 7b; the draft is a Word file (owner Q62 item 94).** `brief-in` reads the `.docx` with python-docx
  (already a dependency, `pyproject.toml:9`) and takes its body paragraphs in order as the units; a cite is written in the
  paragraph text as `[cite MED0003]` or `[page medical/003]` (the same forms the outputs print), a quoted span in straight
  double quotes; tables, headers and footers are ignored and counted (`skipped=`). `brief.fact_check(paragraphs, key,
  pages, rules) -> Report`: before restoring, `check_draft`
  blocks on an invented placeholder (not in the key), a malformed one, a real name token of the key or a calendar date in
  the draft (exit 1, nothing written, kinds and offsets only); then every cited sentence is checked: the cite is a page
  of the matter (stamp or page id; an ambiguous stamp fails), a quoted span restores onto its page by `restore_quote`
  (fails otherwise, naming the page), a cited paragraph without a quoted span has every digit run outside its bracketed tokens on the page (the
  `numbers_in = "page"` rule of D49, read on the placeholder form so a `[DATE D+3]` offset is never a prose number and a
  canonical restore never fails it: review M8), the firm rules run over the restored prose with quoted spans exempt (hits
  are withheld as `[withheld: <rule id>]`, #R06-CX-1, and counted), and the paragraph count is unchanged by the restore;
  paragraphs with no cite are listed as `uncited` (counted, not failed: argument is the attorney's, D3). The Word
  document (`outputs/brief-in-<stem>.docx`) holds the restored draft with `[FACT CHECK FAILED: <reason>]` after each
  failing paragraph and a `Fact check` section (checks, failures, uncited, rule hits, open items); exit 0 when every
  check passes, 1 otherwise (the document is still written, as `.partial.docx`, no `output` event, D49), 2 when blocked
  or cannot run. Rejected: a model judging the draft's claims (Q48 interim; pillar 1 wants the page); refusing the whole
  document on one failed sentence (the attorney needs to see which one).
- **1.8 The brief package is a Markdown file plus the anonymized packet JSON, built from the case file, with the
  conflict excerpts the owner asked for (spec §2, Q41, Q53 mode B for briefs).** `casefile brief-out --matter N
  "<issue>" [--pages all]` runs through `outputs.start` (job `brief`; `run casefile memo first` as today), builds `packet.build(...,
  task="brief", options={"issue": <typed>})` over every fact and every cited page, runs the entity pass, the name list
  halt (1.2), the replacement (`anon.packet`), the identifier check on `package.json` and `package.md` bytes (1.5), then
  writes `<matter>/outbox/<packet_id>/` (mode 700) with `package.md`, `package.json`, `check.txt` (steps, counts, the
  review words of 1.9, no values) all mode 600, `packet_id` the first 12 hex of the sha256 of `package.md`, appends an
  `output` event named `brief-out` (path the package folder; `status` then lists `brief-out:current` and the memo's
  `Outputs out of date` covers it), prints `brief-out <N> packet=<id> sha256=<64 hex> facts=<f> pages=<p> conflicts=<c>
  check=pass review=<r>` and exits 0 (1 blocked, 2 cannot run). `package.md` in order: the drafter rules (the convention's
  rules 1 to 7 in our own words, generic placeholder forms only, no name; the text comes from `anon.drafter_rules()` and is
  passed into the renderer as a parameter, review M7), `Matter <N>` and `Issue: <anonymized issue text>`, the keep list as
  the line `Real names kept in this package (never placeholders): <kept organizations, adjusters and keep entries, comma
  separated, or none>` (no bracketed token on that line, review H3), `Facts` in chronological order
  (parsed date, then case-file order; undated last) one line each `[DATE D+3], [DR-2], prior history: "<anonymized
  quote>" [cite MED0003]`, `Conflicts` (Q41): per conflict flag, in the memo's defense-against-ours-first order, the
  anonymized abouts as `Model's reading`, then `From [cite A]:` and the full anonymized text of page A, the same for B
  (interim excerpt size, question 90), then `Gaps` (abouts), and with `--pages all` a final `Pages` section holding every anonymized page block of the matter in
  page order (owner Q62 item 93; the identifier check then covers every page). `package.json` is `anon.packet(packet).to_json()` (the whole
  anonymized packet: 7b sends it). Approval (`casefile approve`, the `approvals` row) is stage 7b (D54); the printed sha256
  is what that row will hold. Rejected: a Word package (the drafter is a model; Markdown is what it reads); sending every
  page by default (the facts are gated; pages add bulk and risk; `--pages all` is question 93); the memo as the package
  (it holds our words, not a fact list).
- **1.9 A review list is printed, not enforced (owner question 91).** `check.txt` and the status line carry
  `review=<n>`: capitalised words of the anonymized package that are not placeholders, stamps, keep entries, month names
  or words of `/usr/share/dict/words` when that file exists (else `review=unavailable`). It never blocks. Rejected: making
  it a block (on a medical page the list is long and the owner has not said).
- **1.10 Fact identity is the folded quote plus the parsed date plus the folded provider; an already merged fact is
  split by an append-only event the first time a job writes (owner Q61; D40, D46 amended).** `facts.identity(quote,
  date, provider) = (quotes.fold(quote), dates.iso(date) or date, quotes.fold(provider))`; `merge` keys facts by it
  (`facts.py:255`, `:271`); a repeated quote on a new page with the same date and provider still adds a `cite`; a
  different date or provider makes a new fact (measured on the fixture: `F05` and `F34` separate; zero other pairs move).
  New event kind `split` with payload `{fact, page_id, to, cite, date, provider, text}`: the view removes `page_id`'s
  cite, date, provider and its readings from `fact` and creates fact `to` (id allocated like a fact, `F<seq>`) carrying
  the origin's quote and category with that cite, date, provider and reading. `split` joins `CHANGE_KINDS` (`facts.py:56`), so `stale_outputs` and `changed_since` see it and the memo's What changed
  gains `N facts split` (review M3); `CaseFile.split_needed` counts facts whose cites span more than one identity
  (computed on the view); `facts.upgrade_events(casefile) -> list[Event]` returns the
  split events for every such fact (one per cite beyond the first identity group, in cite order); `memo_job._run_locked`
  and `outputs.start` append them under the matter lock before any other write (`outputs.start` already appends `output`
  events; `memo_job` already holds the lock) and print `split=<n>` once; `load` never writes (`casefile status` prints
  `split_needed=<n>` so the state is visible, #R05-OC-1's class). A round 5 file (`FIELDS_V1`, undated) needs no split
  (every identity is `(fold, "", "")`), so D51 stands. Why an event and not a view-only split: a split-off fact needs a
  stable id that later `cite` and `reading` events can reference, and the chain must not be rewritten (D40, #R05-PC-7);
  this is the append-only correction contract #R06-CX-18 asked for. Rejected: identity by cite (two pages of one visit
  would become two facts; #R05-CX-7 wants distinct pages, not distinct facts); refusing old files (owner Q54 item 67);
  rebuilding (pages would be re-read, cost).
- **1.11 Binder roles: whole word or ask (owner Q61; D48 amended).** `roles.role`: after a typed `[roles]` entry and
  the multi-plaintiff rule as today, fold the name (dots, hyphens, underscores, spaces to one space, casefold); a token
  equal to `dme` or `ime` followed by digits only (`dme`, `dme2`, `ime-2025`, `d.m.e.`), or the phrase `defense medical`
  or `independent medical` (kept from the code review M2 ruling, as built) gives `defense`; otherwise a token that
  starts with `dme` or `ime` and is longer (`imelda`, `dmexport`) gives `ROLE NEEDED`; everything else `ours`. New
  `matterinfo.ask_roles(info, binders, stdin, stdout)`: for every binder whose role is `ROLE NEEDED` it asks `Binder
  <name>: defense, ours or other` and writes `[roles]` once (existing entries kept), on a tty only; `outputs.start` calls
  it after `ask` (it runs even when `[header]` exists, unlike `ask`, D0.7); a non-tty run prints `ROLE NEEDED: <binder>`
  as today (`outputs.needed`, the memo's sentences) and does not block; `casefile memo` never prompts. Rejected: guessing
  (Q61 says ask); a flag per run (a role is a fact about the matter).
- **1.12 The three test gaps close with independent assertions.** S1: `tests/test_cli.py` drives `cli.main` with
  monkeypatched `hearing.run` capturing kwargs for `--outline`, `--client`, `--doctor`, `--closing` (`hearing_flags=4 of
  4`). S3: `tests/test_schema.py` asserts that every object schema with a `quote` property among the six schemas the
  manifest lists at stage 6 or 7 (`anonymize`, `concessions`, `elements`, `factsheet`, `medical_memo`, `questions`)
  requires `quote` and `cite` (`schema_evidence=13 of 13`, review L2; the stage 8 `procedural` exception is recorded as an
  open item, not fixed: its card is untouched this round), and `outputs.evidence` raises `OutputError` naming the item
  when `quote` or `cite` is absent, disclosed through the failed-step path. S4: `tests/test_cards.py` asserts the three
  practice sentences the cards must carry independently of the version pin (`card_practice=3 of 3`: `02-C-OURDOC` holds
  "ALWAYS two separate questions" and the `our-doctor-treatment-and-bills` rule text; `02-C-DEFDOC` holds the
  `question-form` rule text).
- **1.13 D62 lands now, scoped to what it means (review H1).** The privacy row also fails on any inventory path whose
  last two components are `anon/key.json` (any case) and on a key-shaped secret, the bytes `sk-ant-` followed by twenty
  or more of `[A-Za-z0-9_-]`, in any tracked or ignored text file (the row already inventories ignored files,
  `privacy.py:10-14`). The bench key `tests/fixtures/matters/9001.001/key.json` (D25) and the bare `sk-ant-` of
  `docs/spec.md:280` are not offenders; measured on the tip: 0 and 0, so `offenders=0` holds after the change. Fixtures
  live under `tests/fixtures/anonymizer/` and the fixture key is never stored (the tests build it under `tmp_path`). D62's
  text is amended to this scope (D63).
- **1.14 Carried and boundary.** Not this round: `casefile approve`, the sent-log, the cloud client and stand-in, the
  bridge, the kill switch, `[cloud]`, run log v3, the Outbox share, the web page; the Q59 items 82 to 86 and the format
  specification; critic 2 M2 to M6; the records-audit card; a head anchor for the case file (#R05-CX-6, recorded limit);
  the oversize client packet (code review L7); re-extraction correcting a stored date (#R06-CX-18 gains the `split`
  contract as a precedent, not a date correction). The 07-ANON card gains one sentence ("The name is copied exactly as
  it is written on the page; an adjuster is kind adjuster.") and its schema the `adjuster` kind, so its version pin moves
  once, measured by W2.
- **1.15 What counts as a leak is what leaves the matter boundary (review H2, chair ruling).** The run log's `answers`
  table stores every raw reply (`gates.py:331-333`, `runlog.py:17,94-102`, D15), so after an entity pass it holds every
  name the model found, and the memo's stored answers quote the pages; the run log lives in `state/` under the `casefile`
  user beside the matter (D14, §8b) and is never shared, so entity names there are not a leak. `key_leak` is measured over
  what leaves or could be copied out: every file under `outbox/`, the `failures` and `gates` message columns, and the
  job's stdout and stderr on a non-tty run; the `answers` table and `<matter>/anon/` are inside the boundary and are not
  searched. Rejected: redacting raw answers in the run log (D25 says every received reply is stored whole; the gates'
  audit trail needs it).

## §1b Placeholder table for the fixture (measured from page order; shared by both lanes, review M7)

Page order is the matter's binder order `medical`, `employer`, `defense-report` (`matter.toml:2`), pages ascending.
Numbers are by first appearance of any variant in that order; the owner's Q62 kinds apply. Both lanes write their
fixtures (goldens, `entities.json`, the drafts) from this table; W5's `checks=10 of 10` is its proof.

| Placeholder | Invented entity (kind) | First page | Occurrences (surname or org form) |
|---|---|---|---|
| `[CLAIMANT]` | Morgan Ashby-Vale (claimant; `Mr. Ashby-Vale` once on defense-report/001) | medical/001 | 17 |
| `[DR-1]` | Dr. Halvard Quist-Benning (doctor) | medical/001 | 3 |
| `[DR-2]` | Dr. Ines Castellanos-Reyes (doctor) | medical/003 | 6 |
| `[DR-3]` | Odalys Ferro-Lindqvist, PT, DPT (doctor; credentials stay outside) | medical/004 | 4 |
| `[DR-4]` | Dr. Ansgar Velloso-Krantz (doctor) | medical/006 | 2 |
| `[DR-5]` | Dr. Priya Okonkwo-Lind (doctor; also the header's treating physician) | medical/007 | 4 |
| `[PERSON-1]` | Rosalind Mbeki-Farrow (person) | employer/001 | 4 |
| `[PERSON-2]` | Tobiah Varga-Ellison (person) | employer/001 | 1 |
| `[PERSON-3]` | Silas Vane-Harrow (person) | employer/003 | 1 |
| `[DR-6]` | Dr. Theodore Marchetti (doctor) | defense-report/001 | 4 |
| `[EMPLOYER]` | Quarry Ridge Logistics LLC (employer) | medical/001 | 8 |
| kept | Fennimore County Hospital, Brightwater Family Medicine, Ridgeline Physical Therapy, Lakeshore Imaging, Lakeshore Orthopedic Associates (provider), Northgate Medical Evaluations (provider, Q62 item 88) | | 4, 3, 4, 4, 3, 4 |
| `[ID-1]` | the claim number `QRL-2025-0418` (`[anon].ids`) | employer/001 | 3 |
| `[DOB]` | `02/17/1981` (`[anon].dob`) | medical/001 | 14 |
| `[YEAR Y-6]` | `2019` (medical/003, defense-report/001) | medical/003 | 2 |

No `[ATTY-n]`, `[ORG-n]`, `[PLACE-n]`, `[DATE-REF-n]`, `[MONTH M+n]` or pattern placeholder occurs on the fixture
(measured: 0 ZIP, phone, email, street, SSN or six-digit hits). Date offsets from the anchor `03/11/2025` (61 dates,
every one written `MM/DD/YYYY`): `08/02/2021` D-1317; the thirteen wage weeks `12/13/2024` D-88, `12/20/2024` D-81,
`12/27/2024` D-74, `01/03/2025` D-67, `01/10/2025` D-60, `01/17/2025` D-53, `01/24/2025` D-46, `01/31/2025` D-39,
`02/07/2025` D-32, `02/14/2025` D-25, `02/21/2025` D-18, `02/28/2025` D-11, `03/07/2025` D-4; `03/11/2025` D+0;
`03/14/2025` D+3; `03/15/2025` D+4; `03/24/2025` D+13; `04/07/2025` D+27; `04/10/2025` D+30; `04/11/2025` D+31;
`04/14/2025` D+34; `04/18/2025` D+38; `05/09/2025` D+59; `06/20/2025` D+101. The key's `dates` map therefore holds one
spelling per offset on this matter, and the good draft quotes dates only through `[DATE D+n]` tags from this list.

## §2 Work items, in build order

Every CHECK runs through `scripts/run.sh`; every seed is applied to a copy, confirmed with `cmp`, run with a fresh
`PYTHONPYCACHEPREFIX` (#R04-OC-1) and restored (`cmp` identical) before the pass counts. Counts marked "measured" are
derived by the builder from the fixtures, printed, and accepted by the chair after a read (round 5 and 6 precedent); every
other number is fixed here.

### W0 (chair, before any builder)
- `git worktree add .claude/worktrees/r7-lane-b -b r7/lane-b` after W1b is committed (not before); toolchain
  `T=$HOME/.casefile-dev/r7-lane-b` synced with the sandbox off (HANDOFF). Prompts in `.workflow/scratch/round07-prompts/`
  (`common.txt` copied from round 6 with "round-7"). The chair reads every fixture file of W2, W3, W5 against the pages
  before the critic round (#R02-OC-H1, #R03-OC-M1) and confirms every name in them is one of the fixture's invented names.

### W1 (one builder, main tree, first): fact identity and the split event
- Files: `src/casefile/facts.py` (`identity()`, `FIELDS["split"]`, `CHANGE_KINDS` gains `split` at `:56` (review M3), the
  view's `split` handling in `facts` and `_decode` (`split.to` is an id, refused if seen; `split.fact` must exist),
  `split_needed`, `upgrade_events`, `merge` keyed by identity at `:255` and `:271`), `src/casefile/memo.py:96-100` (What
  changed gains `, N facts split` when the count is non-zero), `src/casefile/memo_job.py:30-33` (append `upgrade_events` after `load`, print
  `split=<n>` on the memo line when `n > 0`), `src/casefile/outputs.py:305-309` (the same inside `start`, before `check_stamps`),
  `src/casefile/status.py` (`split_needed=` on the status line, after `gaps`), `tests/test_facts.py` (`casefile_ok=22 of
  22`: the 17 of today plus `split_on_append` (a file holding one fact with two cites of different dates loads with
  `split_needed=1`, `upgrade_events` gives one `split`, `append` writes it, the view shows two facts with one cite each
  and the reading moved with its page, `split_needed=0`), `same_identity_still_cites` (same quote, date and provider on
  a second page adds a `cite`, no new fact), `different_date_new_fact` (the fixture pair `F05`/`F34` through `merge`
  gives two facts), `split_refused` (a `split` naming an unknown fact or a reused `to` id is `_broken`), `split_through_start` (review
  M2: a stored case file written by the test in the round 6 shape with the merged pair, one `fact` on MED0002 dated
  03/11/2025 with a `cite` on DEF0002 dated 06/20/2025 and a `reading` per page, loads with `split_needed=1`; `outputs.start`
  on that matter appends exactly one `split` and leaves `split_needed=0`, `stale_outputs()` lists `memo` and
  `changed_since` counts the split; the same through `memo_job.run` with zero unread pages (`chunks=0`) prints `split=1`
  and the memo's What changed says `1 fact split`)), the pins of
  D0.6: `tests/test_stage5_exit.py:30-38` and `:231` (expected: `facts=38`/`39`, `chronology=38 dated=38 of 38`, memo 3
  `dated=38 of 39`, `casefile_lines=55`, `(49, 51, 54, 55)`: one `fact` event replaces one `cite` and one `reading`
  event; `cites=` and `readings=` re-derived, builder prints, chair confirms), `tests/test_stage6_exit.py:25,297`
  (`chronology=38 dated=38 of 38`, `facts=38`), `tests/test_status.py:61-65,100-101,176` (`facts=38`, `facts=39`; the whole-line assertion at `:100-101` gains
  `split_needed=0` after `gaps=4`, review L4), any
  `test_memo.py` case that relied on a cross-date merge (builder lists each), `tests/test_round05_fixes.py:56,129` if
  the dates differ (builder checks).
- Ships: `casefile_ok=22 of 22`; the moved pins printed before and after; the memo and the defense report no longer show
  `F34`'s finding as `Also cited` under the ER entry (`tests/test_stage6_exit.py` reads `report-defense-report.docx`: the
  06/20/2025 straight leg raise entry stands under `Examination findings` with no `Also cited` run: `m1_fixed=1` printed
  on the defense report line); both `--candidate` bench lines byte-identical to the baseline (bench `found` is by cite and
  quote, `benchscore.py:96-99`; `extend` merges in memory the same way, so `ideal.json` still scores `36 of 36`: the
  candidate gains one fact row, `extra` stays 2 because `F34` is in the key).
- CHECK: `scripts/run.sh pytest -q -s tests/test_facts.py tests/test_status.py tests/test_stage5_exit.py
  tests/test_stage6_exit.py` prints `casefile_ok=22 of 22`, the stage 5 lines with `casefile_lines=55`, the stage 6 lines
  with `chronology=38` and `m1_fixed=1`, and passes; `scripts/run.sh pytest -q` passes; the gate prints `0`; both bench
  runs print the baseline lines.
- Seeds, each alone: (a) `identity()` returning the folded quote only -> `different_date_new_fact` red and
  `chronology=37`; (b) the view ignoring `split` events -> `split_on_append` red; (c) `upgrade_events` not called in
  `outputs.start` -> `split_through_start` leaves `split_needed=1`, red; (c2) `split` left out of `CHANGE_KINDS` ->
  `stale_outputs()` empty after the split, red; (d) `_decode` accepting a `split` with a
  reused `to` -> `split_refused` red; (e) `identity()` comparing the raw date string -> a `3/11/2025` against
  `03/11/2025` case red (the `same_identity_still_cites` case writes the second page's date in the other spelling).
- Librarian pre-flight: #R05-PC-7 (never rewrite a complete line; the split is appended), #R05-CX-4 (the split append
  happens under the matter lock), #R05-CX-5 (readings move with their page), #R02-CX-5 (the `to` id is unique), #R03-PC-3
  (every pin in D0.6 listed and moved with a printed before/after), #R06-CH-2 (the identity rule was measured on the key:
  one pair moves, zero others), #R05-OC-3 (`What changed` counts a split fact as a fact added).

### W1b (the same builder, main tree, after W1): roles, the role prompt, the three test gaps, the privacy row
- Files: `src/casefile/roles.py` (§1.11), `src/casefile/matterinfo.py` (`ask_roles`, `write` with one level of sub-tables
  for `[roles]` as today and the `[anon]` tables of §1.2 admitted and validated now so W3 needs no second change to the
  loader: `anon_employer`, `anon_ids`, `anon_places`, `anon_keep`, `anon_people`, `anon_organizations` fields on
  `MatterInfo`), `src/casefile/matter.py:60` (admit `anon`), `src/casefile/outputs.py:313-314` (`ask_roles` after `ask`,
  on a tty), `src/casefile/privacy.py` (§1.13), `src/casefile/cli.py` untouched, `tests/test_roles.py` (`roles_by_name=15
  of 15`: the six of today plus `dme2`, `IME-2025`, `d.m.e.`, `independent-medical`, `medical-ime` defense; `time-records`,
  `primed` ours; `Imelda Health`, `dmexport` ROLE NEEDED), `tests/test_matterinfo.py` (`matterinfo_ok=18 of 18`: the 12
  of today plus `ask_roles` writing `[roles]` for one ROLE NEEDED binder on injected streams and keeping an existing
  entry, `ask_roles` on a non-tty writing nothing, `[anon]` tables loading with the fixture values, an unknown kind
  refused naming `anon.people.<name>`, `write` round-tripping `[anon.people]`, a non-string `anon.employer` refused),
  `tests/test_cli.py` (`hearing_flags=4 of 4`), `tests/test_schema.py` (`schema_evidence=13 of 13`), `tests/test_cards.py`
  (`card_practice=3 of 3`), `tests/test_outputs.py` (`evidence` without `quote` raises `OutputError` naming the item:
  `evidence_closed=1`), `tests/test_privacy.py` (`offenders` gains two planted cases, `x/anon/key.json` and an ignored file holding a
  synthetic key-shaped string `sk-ant-` plus 24 invented key characters, and two controls that must not offend, a
  `tests/fixtures/matters/x/key.json` and a text file holding the bare words `sk-ant-` as in `docs/spec.md:280`:
  `expected=6`), `tests/fixtures/matters/9001.001/matter.toml` (the invented `[anon]`
  tables: `employer = "Quarry Ridge Logistics LLC"`, `ids = ["QRL-2025-0418"]`, `places = []`, `keep = []`,
  `[anon.people]` the ten invented people with kinds (the claimant `claimant`; the six clinicians `doctor`, the therapist
  included; the shift lead, the supervisor and the wage clerk `person`), `[anon.organizations]` the seven invented
  organizations (`Quarry Ridge Logistics LLC = "employer"`, the five treating facilities and `Northgate Medical
  Evaluations` all `provider`, owner Q62 item 88), `dob = "02/17/1981"`).
- Ships: `roles_by_name=15 of 15`, `matterinfo_ok=18 of 18`, `hearing_flags=4 of 4`, `schema_evidence=13 of 13`,
  `card_practice=3 of 3`, `evidence_closed=1`, `offenders=6 expected=6`; `outputs_ok=13 of 13` and the stage 6 lines
  unchanged (the fixture has no ROLE NEEDED binder; `defense-report` keeps its typed role).
- CHECK: `scripts/run.sh pytest -q -s tests/test_roles.py tests/test_matterinfo.py tests/test_cli.py tests/test_schema.py
  tests/test_cards.py tests/test_outputs.py tests/test_privacy.py` prints the seven lines and passes; `scripts/run.sh
  pytest -q` passes; the gate prints `0`.
- Seeds, each alone: (a) `roles.py` back to `\b(?:dme|ime)` without the whole-token rule -> `Imelda Health` reads
  `defense`, `roles_by_name=14 of 15`; (b) `ask_roles` prompting on a non-tty -> the StringIO case writes a file, red;
  (c) `cli.py:128` `doctor=args.closing, closing=args.doctor` -> `hearing_flags=2 of 4` (verifier S1 verbatim); (d)
  `quote` dropped from `questions.schema.json` required -> `schema_evidence=12 of 13` (S3 verbatim); (e)
  `c-our-doctor.md:21` reversed to "may be asked together" with `VERSIONS` re-pinned -> `card_practice=2 of 3` (S4
  verbatim, re-pinning cannot hide it); (f) `privacy.scan` without the `anon/key.json` rule -> `expected=6` red; (f2) the secret rule widened to the bare
  `sk-ant-` -> the spec-wording control offends, red; (g) `write`
  dumping `[anon.people]` with `json.dumps` -> the round-trip case red (TOML refuses `{"a": "b"}`).
- Librarian pre-flight: #R03-CX-5 (a whole-token rule at both ends; `time-records` and `primed` are the controls),
  #R06-CX-12 (the prompt can collect the role, so the multi-plaintiff guard is reachable), #R01-OC-M7 (`ask_roles` never
  creates `matter.toml` on a non-tty), #R01-V-B2 (each CLI flag has its own assertion), #R04-PC-7 (quote and cite required
  on every asserting item), #R01-CX-10 (the practice assertion is independent of the hash), #R01-CX-2 (the privacy class
  is the folder name in any case and the file name, not one spelling).

### W2 (lane A, main tree, after W1b): the anonymizer core, pure code
- Files: `src/casefile/anon.py` (new, §1.1, §1.3 to §1.6, §1.9: `Key` dataclass and JSON form `{"convention":
  "casefile-anon/1", "anchor": "YYYY-MM-DD", "entities": {"[CLAIMANT]": {"name", "kind", "variants"}, ...}, "refs":
  {"[ID-1]": "...", "[DATE-REF-1]": "..."}, "dates": {"D+0": ["03/11/2025"]}, "srcs": {...}}`; `load_key(folder)`
  refusing a missing `anon/` quietly as an empty key and refusing a key file whose mode has any group or other bit
  (`KeyError`-free: `AnonError("anon/key.json must be mode 600")`), `save_key(folder, key)` creating `anon/` 0o700 and
  writing `key.json` through `os.open(..., O_WRONLY|O_CREAT|O_EXCL, 0o600)` on a `.tmp` then `os.replace`; `NameList`,
  `names(info)`, `mapping(namelist, hits, pages, key)`, `text(value, key, *, protected)`, `packet(packet, key)`
  (anonymizes every `quote`, `text`, `provider`, `date`, every string option including the `issue`, every flag `about`; leaves `id`, `cite`,
  `page_id`, `category`, `matter`, `task`, `playbook_version`; pages keep `binder`, `number`, `stamps`), `check` steps
  1, 2, 3, 5 (`check_code(data, key, namelist, pages)`; step 4 is W3's), `restore`, `restore_quote`, `review(text,
  key, namelist, pages)`, `drafter_rules()` the convention's seven rules in our words), `cards/07-anonymize/entities.md`
  (the one added sentence of §1.14; `tests/test_cards.py` `VERSIONS["07-ANON"]` re-pinned, measured),
  `schemas/anonymize.schema.json` (people `kind` enum gains `adjuster`), `src/casefile/gates.py:17`
  (`_SKIP_RULES` gains `name`; only `anonymize.schema.json` has that key, D0.3), `tests/test_gates.py` (`CASES` gains
  `anon_name_exempt`: `gate_cases=40 of 40`), `tests/test_anon.py` (new), the golden
  files `tests/fixtures/anonymizer/9001.001/DEF0001.txt` and `EMP0001.txt` (the two pages' expected anonymized text,
  written by the builder from the code and read by the chair against §1.4 line by line before the commit).
- Ships: `anon_text=32 of 32` (unit cases on invented strings: each pattern kind once; each date form once including
  the month-name, yearless and bare-year forms and a date split before its year by a line break; a title stays outside;
  a capitals-only form replaced and a lowercase common-word form not; a name inside a longer token not replaced; a stamp
  and a page id protected; the wage line `Total gross pay, 13 weeks: $11861.20` untouched (review M6); a date whose year
  follows a line break replaced with the break kept (review L8); a typed `dob` in two spellings and a labelled
  `Date of Birth: 02/17/1981` becoming `[DOB]`; an `adjuster` kind kept and an `other` organization numbered; a bracketed token already present becomes `[SRC-1]` and restores as written; a claim number
  from the list replaced as a whole token and not inside a longer token; the employer unnumbered and a second
  organization `[ORG-1]`; a `provider` and an `insurer` kept; a `keep` entry kept; numbering by first appearance;
  a second call on the same key reusing numbers); `anon_pages=14 of 14` (every fixture page: `text` then `restore_quote`
  equals the page bytes); `anon_golden=2 of 2`; `stamps_kept=15 of 15` (every stamp and page id of the fixture survives in the anonymized page blocks, plus one unit
  page whose raw stamp is `MED 123456`, a six-digit run the id detector would eat without the protected set: review M4); `lines_kept=14 of 14`; `anon_stable=1` (anonymizing the packet twice from the saved key gives
  identical bytes); `restore_quote=6 of 6` (a quote with a date in the page's spelling; a `Mr. <surname>` form; two
  placeholders in one quote; a quote that is on no page returns `None`; a quote whose placeholder is not in the key
  returns `None`; prose `restore` gives `M/D/YYYY`); `check_code=16 of 16` (the code-step kinds of §1.5 each planted
  once into the anonymized fixture package bytes and blocked with the right `(step, kind)`, the offset pointing at the
  planted bytes, and the clean bytes passing with `hits=()`); `key_mode=600` (a key saved then `stat` is `0o600`; a key
  chmod 644 is refused); `key_grows=1` (a second `save_key` with one more entity keeps every earlier entry and number;
  a `save_key` that would drop an entry is refused: review L7); `replaced=` counts printed (people, orgs, ids, dates, years, kept) for the chair to compare with
  the architect's measurement (§1b: dates 61, dob 14, years 2, ids 3, people 46, employer 8, kept organizations 6 with 22 occurrences); `review=<measured>` printed.
- CHECK: `scripts/run.sh pytest -q -s tests/test_anon.py tests/test_cards.py tests/test_gates.py tests/test_schema.py` prints every line above
  and passes; `scripts/run.sh pytest -q` passes; the gate prints `0` (`tests/fixtures/anonymizer/` holds `.txt` only).
- Seeds, each alone: (a) step 2 (absolute dates) skipped in `check_code` -> the planted date passes, `check_code=15 of
  16`; (b) the protected set dropped from the pattern step -> the `MED 123456` unit page's stamp becomes `[ID-n]`,
  `stamps_kept=14 of 15` (review M4); (c) `restore_quote` returning the canonical
  restore only -> `anon_pages=0 of 14` (every page writes `MM/DD/YYYY`); (d) the key's `dates` spellings not recorded ->
  the same, `anon_pages=0 of 14`; (e) a date pattern that eats the line break before the year -> `lines_kept=13 of 14`
  on a unit page with such a date (the test holds one); (f) numbering restarted per call -> `anon_stable=0`; (g) `[EMPLOYER]`
  numbered -> `anon_text` case red; (h) `save_key` writing the file with the default umask -> `key_mode` red; (i)
  `_SKIP_RULES` without `name` -> `test_gates` case `anon_name_exempt` (a hit named with an `IME` word on the invented
  page passes gate 5 for `07-ANON`) red; (j) the whole-token name boundary dropped at one end -> the "inside a longer
  token" case red.
- Librarian pre-flight: #R03-CX-5 (every token match bounded at both ends; stamps are the control), #R03-PC-2 (the golden
  files catch one changed digit), #R04-CX-3 (a line-break hyphen inside a date never joins digits), #R04-PC-4 (one
  canonical form on both sides: `text` and `check` share the date and pattern readers), #R01-OC-M2 (no silent default:
  `protected` is required), #R03-CX-2 (the `.tmp` key is removed on failure; only `anon/` this run created is removed),
  #R02-CX-7 (the key is read as UTF-8 with `jsonrepair.loads`, duplicate keys refused, #R04-CX-7).

### W3 (lane A, after W2): the entity pass, the name list halt, the second pass, the key on disk
- Files: `src/casefile/anon_job.py` (new: `entity_pass(pages, *, client, rules, log, matter, playbook_version, job) ->
  list[Hit]` running `cards.card("07-ANON")` through `pipeline.chunk` and `gates.ask` per chunk, with `echo=("pages_seen",
  [ids of the chunk])`, dropping hits whose `name` is not found on the cited page by `quotes.found_in` (logged on the run
  as `gate.identifier: hit dropped: name not on <page>`), merging `anchor_dates` votes; `halt(namelist, hits, stdin,
  stdout)` (§1.2, `anon.ask`); `anonymize(packet, *, folder, info, hits) -> (Packet, Key)` (anchor §1.3, `mapping`,
  `packet`, `save_key`); `check(data, key, namelist, pages, *, client, ...) -> Verdict` = `anon.check_code` then the
  second pass on the anonymized `Page` objects with a model failure as a block (`step 4, kind model, offset 0`)), `tests/test_anon_job.py`
  (new), `tests/fixtures/anonymizer/9001.001/entities.json` (the invented first-pass answer for the 14 real pages, written
  by the chair's read of the pages against §1b: 10 people, 7 organizations, 0 places, anchor dates with quotes from EMP0001, MED0001,
  MED0007; every `name` as written on its cited page), `entities-empty.json` (the second-pass answer: `pages_seen` only),
  `entities-second-hit.json` (a second-pass answer naming the shift lead on `employer/001`).
- Ships: `entity_pass=4 of 4` (the fixture answer through `FakeTransport` gives 17 hits in page order; a hit whose name
  is not on its page is dropped and logged; a chunked run over a forced three-chunk split echoes each chunk's ids; a
  `bad_schema` mode answer fails the pass and the job stops before any key write); `halt=4 of 4` (every hit on the list:
  no prompt, no write; one new hit on a tty with injected streams: prompted with the proposed kind, `[anon.people]`
  written once, `keep` chosen writes `keep`; one new hit on a non-tty: `NAME LIST NEEDED` on stdout, exit 2, no `anon/`,
  no `outbox/`); `anchor=3 of 3` (typed date wins; empty header with a verified model vote; neither: `ANCHOR NEEDED`);
  `second_pass=3 of 3` (empty answer passes; the second-hit answer blocks with `step=4 kind=person offset=<o>` and the
  value absent from stdout and the run log; a 404 blocks with `kind=model`); `key_leak=0` (after a full anonymize and
  check, every file under `outbox/`, the run log's `failures` and `gates` message columns and the job's captured stdout
  and stderr hold none of the replaced variants, the ids, the dob or the five header values; the `answers` table and
  `anon/` are not searched, §1.15, review H2).
- CHECK: `scripts/run.sh pytest -q -s tests/test_anon_job.py` prints the five lines and passes; the gate prints `0`.
- Seeds, each alone: (a) the name-on-page drop removed -> the invented off-page hit enters the mapping, `entity_pass=3
  of 4`; (b) `halt` writing on a non-tty -> red; (c) the second pass's `ModelError` treated as pass -> the 404 case
  passes, `second_pass=2 of 3`; (d) the second pass run before `check_code` -> the planted-date case makes a model
  request (counted by `FakeTransport.requests`), red; (e) the hit value printed in the block message -> `key_leak=1`.
- Librarian pre-flight: #R03-V-L1 (the halt and the anchor refusal happen before any key or package write), #R04-PC-6
  (an empty entity answer is valid only with every page id echoed, D44), #R01-CX-9 (a dropped hit is logged, never
  silently absorbed), #R05-PC-8 (every stand-in through `FakeTransport` or a port the test opened), #R06-CX-1 (no value in
  any diagnostic that reaches a file).

### W4 (lane B, worktree): the package renderer, the draft check and the brief-in document, with an injectable transform
- Files: `src/casefile/brief.py` (new: `package_text(packet, casefile, pages, info, *, issue, keep, rules_text, transform,
  pages_all=False) -> str` (§1.8 layout; `rules_text` is the drafter rules block passed in, review M7; `transform(str) -> str` is applied to every quote, about, issue and page text, identity in lane B's tests,
  `anon.text` after the merge), `conflict_excerpts(casefile, pages, info, transform)`, `read_draft(path) -> list[str]` (python-docx body
  paragraphs; tables, headers and footers counted as skipped), `parse_draft(paragraphs) -> list[Unit]` (paragraphs with
  their `[cite X]` or `[page x]` cites outside quoted spans and their quoted spans, indexes kept), `fact_check(draft, pages, rules, *,
  restore_prose, restore_quote) -> Report` (§1.7 with the two restorers injected; identity restorers in lane B's tests),
  `render(report, info, *, playbook_version, model) -> outputs.Doc`, `publish_package(folder, packet_id, files)` (mode
  700 folder, 600 files, `.tmp` and `os.replace`, refusing an existing folder)), `src/casefile/cli.py` (subparsers
  `brief-out` (`--matter`, positional `issue`, `--config`) and `brief-in` (`--matter`, positional `file`, `--config`)
  dispatching to `brief_out.run` and `brief_in.run`, which W5 writes; until then the branches import lazily and the
  parser test asserts the arguments only), `tests/test_brief.py` (new), `tests/fixtures/anonymizer/9001.001/draft.txt`
  (one paragraph per line, an invented placeholder-form draft of 12 paragraphs written from §1b: 8 with cites and quoted
  spans on the fixture pages in placeholder form, 2 cited paragraphs without quotes whose digit runs are on the page, 2
  uncited argument paragraphs; no real name, no calendar date), `draft-bad-placeholder.txt`, `draft-real-name.txt`,
  `draft-bad-quote.txt` (one invented quote not on its page); the tests build each `.docx` from these lines with
  python-docx under `tmp_path` (no `.docx` is committed, owner Q62 item 94).
- Ships: `package_ok=9 of 9` (the drafter rules first, the text given as the parameter; `Issue:` transformed; facts in parsed-date order with undated last
  and the `[DATE ...]`-style line shape taken from the transform; every fact line carries `[cite X]`; conflicts in
  defense-first order each with both pages' full text after `From [cite A]:`; gaps; the keep list names the kept kinds;
  `publish_package` refuses an existing folder and leaves no `.tmp`; folder 0o700 and files 0o600; `pages_all=True`
  appends a `Pages` section with every page block in page order and `False` appends none); `draft_ok=10 of 10`
  (`read_draft` on a built `.docx` with one table returns the 12 paragraphs and `skipped=1`; `parse_draft` finds 10 cited
  paragraphs and 2 uncited; every good check passes; an unknown cite fails naming it; an
  ambiguous stamp fails; a quote not on its page fails naming the page; a cited sentence with a digit run absent from
  its page fails; a rule hit in prose is withheld and counted; the paragraph count is checked; `render` writes the document
  with `[FACT CHECK FAILED: ...]` after the failing sentence and the `Fact check` section).
- CHECK: `scripts/run.sh pytest -q -s tests/test_brief.py` prints `package_ok=9 of 9 draft_ok=10 of 10` and passes; the
  gate prints `0` (every `.docx` under `tmp_path`).
- Seeds, each alone: (a) conflict excerpts taken from matching facts only instead of the page text -> red; (b)
  `publish_package` creating files with the default umask -> the mode case red; (c) a failed quote check not marked in
  the document -> red; (d) `parse_draft` taking `[cite X]` inside a quoted span as the sentence's cite -> the ambiguous
  case red; (e) the digit-run check reading the quote instead of the page -> red; (f) the digit-run check reading the
  digits inside `[DATE D+3]` -> the unquoted cited paragraph case red (review M8).
- Librarian pre-flight: #R04-CH-1 (a quote must be on its cited page, not any page), #R04-V-2 (cite digits are not prose
  numbers), #R03-OC-L1 (every failure names the sentence, the page and the remedy), #R03-CX-2 (publish owns only what it
  created), #R06-CX-16 (the test's expected package text is written from the fixture, not from `package_text`).

### W5 (lane A, main tree, after the merge of lane B): the jobs, the CLI, the stage 7 exit test
- Files: `src/casefile/brief_out.py` (new: `run(config, number, issue, *, out, err, opener=None, stdin=None)`: `outputs.start`
  (job `brief`), `packet.build(task="brief", options={"issue": issue})`, `anon_job.entity_pass`, `halt`, `anonymize`,
  `brief.package_text(..., transform=lambda s: anon.text(s, key, protected=...))`, `anon_job.check` on both files' bytes,
  `publish_package`, the `output` event, the status line of §1.8; exits 0, 1 blocked (`brief-out: blocked at step <n>
  (<kind>, offset <o>); nothing was written`), 2 cannot run), `src/casefile/brief_in.py` (new: `run(config, number, file,
  *, out, err)`: `outputs.start` without a model client need (it still opens the run log for the `output` event path;
  no model call), `anon.load_key`, `check_draft` (blocked: exit 2, nothing written), `brief.fact_check(...,
  restore_prose=anon.restore, restore_quote=anon.restore_quote)`, `brief.render`, `outputs.publish(... name
  f"brief-in-{stem}")` with `failed_steps` set when any check failed; status line `brief-in <N> file=<stem> checks=<c>
  of <t> failed=<f> uncited=<u> rule_hits=<r> output=<name> exit=<code>`), `src/casefile/cli.py` (the two branches),
  `tests/test_stage7_exit.py` (new, socket, one stand-in: copy the fixture matter to `9001.001` and a second copy to
  `9001.002` with `number = "9001.002"` rewritten in its `matter.toml` (`pages.py:90-92` refuses a mismatch, review L3)
  and `[anon.people]` lacking the shift lead; `casefile memo` on both (the second matter needs its own extraction recording, `recording_for(extract.card(), pages,
  '9001.002', ideal)`, since the prompt names the matter); register `entities.json` for `9001.001`
  and a copy without the shift lead for `9001.002` through `recording_for(card, pages, number, answer)`, and the
  second-pass recordings on the anonymized pages computed by `anon.packet` from the fixture list (`entities-empty.json`
  for `9001.001`, `entities-second-hit.json` for `9001.002`); `brief-out --pages all` on `9001.001` and plain `brief-out` on `9001.002`; `brief-in` with the `.docx` the test builds
  from `draft.txt` and from `draft-bad-quote.txt`; the seeded leak matrix of W2 and W3 is not repeated here), `tests/test_cli.py` (parser cases for
  the two commands).
- Ships, printed with `capsys.disabled()`, every number asserted:
  `stage7 package matter=9001.001 pages=14 pages_in_package=14 entities=17 of 17 anchor=D+0 people=46 employer=8 ids=3 dob=14 dates=61 years=2 kept_orgs=6 leaks=0 review=<measured> key_mode=600 facts=38 conflicts=5 exit=0`
  `stage7 blocked matter=9001.002 step=4 kind=person package_written=0 key_written=1 exit=1`
  `stage7 draft=draft paragraphs=12 checks=10 of 10 uncited=2 placeholders_restored=<measured> rule_hits=0 exit=0`
  `stage7 draft=draft-bad-quote checks=9 of 10 failed=1 marked=1 partial=1 exit=1`
  `stage7 status outputs=memo:current,brief-out:current,brief-in-draft:current;partial=brief-in-draft-bad-quote.partial.docx`
  `stage7 exit=0 packages=1 of 1 blocked_seeded=1 of 1 drafts=2 of 2 answers=+6 identifiers_in_package=0 server_stopped=1`
  where `identifiers_in_package` counts occurrences in `package.md` and `package.json` of every replaced `[anon]` value
  (the ten surnames, the employer, the ids, the dob), the five typed header strings (client name, date of accident,
  treating physician without its title, hearing number, hearing date; never `plaintiffs` or `matter_type`, review M9)
  and every `M/D/YYYY` string (0 by the check's own rule; the test counts independently,
  #R06-CX-16), `answers=+6` is two memo runs plus two passes per `brief-out` (the blocked run's second pass counts as a
  received answer), `package_written=0` is the absence of `outbox/` under `9001.002`, `key_written=1` that its
  `anon/key.json` exists with mode 600 (the key is written before the check so numbering is stable across a retry; the
  key never leaves the folder), `partial=1` the `.partial.docx` for the failed draft and no `output` event for it.
  The memo exit test line (`stage5`), the stage 6 lines and the bench lines are unchanged by W5.
- CHECK: `scripts/run.sh pytest -q -s tests/test_stage7_exit.py` prints the six lines with `stage7 exit=0` and passes;
  `scripts/run.sh pytest -q` passes; `scripts/run.sh python -m casefile.gate` prints `0`; `scripts/run.sh
  scripts/suite_time.sh 3` prints `verdict=PASS`.
- Seeds, each alone: (a) `publish_package` called before `anon_job.check` -> `package_written=1`, red; (b) the typed
  anchor ignored in favour of the model's -> `anchor=D+0` still (same date), so the seed instead blanks the fixture's
  `date_of_accident` and drops the model vote: `ANCHOR NEEDED`, `packages=0 of 1`, red; (c) the fact check's quote
  restorer replaced by prose `restore` -> `checks=0 of 10` (every quoted date is `M/D/YYYY`), red; (d) the `output`
  event appended for a failed draft -> the status line shows `brief-in-draft-bad-quote:current`, red; (e) a real surname
  written into `package.md` by the test's transform seam -> `identifiers_in_package=1`, red (the control that the
  independent count bites); (f) `FakeModel.record` for the second pass skipped -> 404, `blocked ... kind=model` on the
  good matter, `packages=0 of 1`.
- Librarian pre-flight: #R01-P-1 (server stopped in `finally`), #R05-PC-17 (fixture copied under the test's root), #R01-CX-11
  (exit codes 0, 1, 2 asserted), #R03-PC-3 (every measured count printed and read by the chair), #R06-PC-12 (a failed
  draft is a partial, never current), #R04-OC-1.

### W6 (chair, at the close): records
- `docs/spec.md`: §9 D63 to D67 (§6); §3 step 7's stage 7 half and §5's Anonymizer row applied as text (D0.2); §2
  brief paragraph amended; §11 stage 7 row; §10 the conflict-excerpt question marked interim (question 90).
  `docs/loop/tuning-questions.md`: the second entity pass's cost (two full passes of the matter per package; the
  fixture's `answers=+2` per package) as the next T entry. `Librarian.md` round 7 entries. Ledger baselines (suite count,
  `casefile_lines=55`, stage 6 `chronology=38`, the `stage7` lines, `roles_by_name=15 of 15`, `casefile_ok=21 of 21`,
  `offenders`). HANDOFF; the next-round prompt.

## §3 Parallelisation map

- W1 then W1b first, one builder in the main tree, each committed by the chair only after `scripts/run.sh pytest -q`,
  the gate and both `--candidate` bench runs are green; both lanes start from the W1b commit (the identity and `split`
  contract, the `[anon]` tables in `matterinfo`, the roles rule, the privacy row and the three closed test gaps are the
  shared base).
- Lane A (main tree): W2, W3, in that order; then W5 after the merge. Owns `src/casefile/anon.py`, `anon_job.py`,
  `brief_out.py`, `brief_in.py` (W5), `gates.py:17` (one line), `cards/07-anonymize/entities.md`, `tests/test_anon.py`,
  `test_anon_job.py`, `test_stage7_exit.py`, `tests/fixtures/anonymizer/` except the four draft files, and the `VERSIONS`
  pin line of `tests/test_cards.py`.
- Lane B (worktree `.claude/worktrees/r7-lane-b`, branch `r7/lane-b` from the W1b commit, toolchain
  `~/.casefile-dev/r7-lane-b`): W4. Owns `src/casefile/brief.py`, the two `cli.py` subparser blocks and `elif`
  branches (lane A adds none; W5's branches are written into the W4 blocks after the merge), `tests/test_brief.py`,
  the four draft fixtures.
- Frozen after W1b: `facts.py`, `roles.py`, `matterinfo.py`, `matter.py`, `outputs.py`, `privacy.py`, `status.py`,
  `memo_job.py`, the stage 5 and 6 exit tests; a lane that needs a change files it with the chair (one ruling, one
  commit in the main tree that lane B merges).
- Sequential and why: W1 before W1b (W1b's `matterinfo` and `outputs.start` edits sit beside W1's `outputs.start`
  split append); W1b before both lanes (contract); W3 after W2 (the pass builds on `mapping` and `check_code`); the
  merge of B into A's tip by the chair, then the full suite, gate and baselines; W5 after the merge (it joins both
  lanes); then the critic round.
- Interfaces fixed by this brief: `facts.identity(quote, date, provider)`, `facts.upgrade_events(casefile)`,
  `CaseFile.split_needed`; `roles.role(binder, info) -> "defense" | "ours" | "other" | "ROLE NEEDED"`;
  `matterinfo.ask_roles(info, binders, stdin, stdout)`; `MatterInfo.anon_*` fields and `anon.names(info) -> NameList`;
  `anon.load_key(folder) -> Key`, `anon.save_key(folder, key)`, `anon.mapping(namelist, hits, pages, key) -> Key`,
  `anon.text(value, key, *, protected) -> str`, `anon.packet(packet, key) -> Packet`, `anon.check_code(data, key,
  namelist, pages) -> Verdict`, `anon.restore(value, key) -> str`, `anon.restore_quote(quote, key, page) -> str | None`,
  `anon.review(...)`, `anon.drafter_rules() -> str`; `anon_job.entity_pass(...) -> list[Hit]`, `anon_job.halt(...)`,
  `anon_job.anonymize(packet, *, folder, info, hits) -> (Packet, Key)`, `anon_job.check(...) -> Verdict`;
  `brief.package_text(packet, casefile, pages, info, *, issue, keep, transform) -> str`, `brief.parse_draft(text)`,
  `brief.fact_check(draft, pages, rules, *, restore_prose, restore_quote) -> Report`, `brief.render(report, info, *,
  playbook_version, model) -> outputs.Doc`, `brief.publish_package(folder, packet_id, files)`; `brief_out.run(config,
  number, issue, *, out, err, opener=None, stdin=None)`, `brief_in.run(config, number, file, *, out, err)`.

## §4 Test design

- Regression set and what moves on purpose: gate `0`; `unused_imports=0`; `suite_time.sh 3` under 90 s; doctor
  `runlog_schema PASS schema=2 triggers=21` (schema untouched); stage 1 to 4 lines unchanged; the two `--candidate`
  bench lines byte-identical (W1 measures); `bench_chunks=3 found=36 of 36 flags=5 of 9` unchanged; stage 5
  `casefile_lines=56` -> `55` and `facts=37/38` -> `38/39` (W1, deliberate); stage 6 `chronology=37 dated=37 of 37` ->
  `38 ... 38 of 38` and the CLI `facts=37` -> `38` (W1, deliberate), `m1_fixed=1` added; `roles_by_name=6 of 6` -> `15
  of 15`; `matterinfo_ok=12 of 12` -> `18 of 18`; `casefile_ok=17 of 17` -> `22 of 22`; the status line gains
  `split_needed=`; `gate_cases=39 of 39` ->
  `40 of 40` (`anon_name_exempt`); `cards_loaded=15 of 15 schemas_loaded=11 of 11` unchanged with `VERSIONS["07-ANON"]`
  re-pinned once (W2); `offenders` planted `4` -> `6`; `len(MODES) == 17` untouched (no new stand-in mode: the second
  pass's faults are reached by recordings and the 404).
- New tables, each `*_ok=N of N` or a fixed line: `hearing_flags` 4, `schema_evidence` 13, `card_practice` 3,
  `evidence_closed` 1, `anon_text` 32, `anon_pages` 14, `anon_golden` 2, `stamps_kept` 15, `lines_kept` 14,
  `anon_stable` 1, `restore_quote` 6, `check_code` 16, `key_mode` 600, `key_grows` 1, `entity_pass` 4, `halt` 4, `anchor` 3,
  `second_pass` 3, `key_leak` 0, `package_ok` 9, `draft_ok` 10, the six `stage7` lines. Every N is fixed above; counts
  marked measured are printed and read by the chair before they are pinned.
- The stage 7 exit test is the only place the two jobs run end to end through the CLI with a socket stand-in; every other
  anonymizer test is in-process through `FakeTransport` (the entity pass) or pure (`anon.py`). Recordings are built by
  `recording_for(card, pages, number, answer)` with the pages the job will send (real pages for the first pass; the
  anonymized `Page` objects for the second pass, computed by the test from the fixture list and `anon.packet`), never by
  hand-written message JSON (#R04-PC-4).
- Oracles independent of the implementation (#R06-CX-16): the golden anonymized pages (W2) are read by the chair against
  §1.4; `identifiers_in_package` is counted by the test from the fixture values, not by `anon.check`; the draft's expected
  check verdicts are written in the test from the fixture pages.
- Suite time (T-11): W5 adds four `run.sh` subprocess runs, two memo runs and four entity passes (about 5 s); the pure
  tests are in-process. Acceptance: `scripts/suite_time.sh 3` exits 0; if over, the T-18 lever is pre-approved; never a
  skip.
- Open for the code review (8a): a name that is also a month name or a medical word (`May`, `Lind`); a provider string
  that is a person (`Dr. Priya Okonkwo-Lind` is both a provider value and a `[DR-n]`: the provider field must be
  replaced like any text, and `bills_providers` in options too); a date split by a line break inside a quoted span (the reader handles the page, `restore_quote` must too); a `split`
  whose origin fact has readings on both pages; the halt when the same surname belongs to two listed people; a package
  built while another job holds the matter lock (both block on `flock`); `restore_quote` cost on a long quote with many
  placeholders (bounded by variants per placeholder; the test measures the fixture's worst case).

## §5 Risks, each with a measurable tripwire

- R1 The local model's entity pass misses a name and so does the second pass. Tripwire: `leaks=0` is necessary, not
  sufficient; `review=<n>` printed per package and read by the attorney; `check_code=13 of 13` and `second_pass=3 of 3`
  prove each detector bites; on the Studio the per-matter hit counts in `check.txt`. The name list halt is the real
  guard (Q53).
- R2 Restore drops or mangles quotes (a placeholder inside a token, a date spelling the key never saw). Tripwire:
  `anon_pages=14 of 14`, `restore_quote=6 of 6`, `checks=10 of 10` on the good draft; a drop rate over 10 percent of items
  on a real matter fails the run (proposal R10, built at 7b).
- R3 Placeholder numbers drift between runs or packages. Tripwire: `anon_stable=1`; the key is append-only and a test
  asserts a saved key is never shrunk by `save_key` (`key_leak` case rereads it).
- R4 The anonymizer alters a stamp, a page id or a line count, breaking cites and page:line references. Tripwire:
  `stamps_kept=14 of 14`, `lines_kept=14 of 14`, the second pass's gate 4 (quotes on anonymized pages) and the restore
  check's line count rule.
- R5 The split upgrade corrupts a chain or loses a reading. Tripwire: `casefile_ok=21 of 21` with seeds (b), (d); stage
  5 `chain_ok=1`; `split_needed=0` after the first job on the fixture.
- R6 The key or a real value reaches the run log, `outbox/`, stdout of a non-tty run or the repo. Tripwire: `key_leak=0`,
  `identifiers_in_package=0`, the gate's privacy row with the `key.json` and `anon` names, `key_mode=600`.
- R7 A fixture holds something that is not invented. Tripwire: the chair reads every new fixture (W0) against the 14
  pages; every name in `entities.json`, `[anon]` and the drafts must be one of the pages' invented names or a placeholder.
- R8 Two lanes edit `cli.py`. Tripwire: lane B owns the subparsers; lane A touches `cli.py` only at W5 after the merge.
- R9 Suite time over 90 s. Tripwire: `suite_time.sh 3`; the T-18 lever.
- R10 Two full entity passes per package are slow on a 300 page matter (about 2 x 14 chunks at 65536). Tripwire: the
  stage 9 benchmark records seconds per package; the tuning entry of W6 names the second lever (a code-only second pass
  when the first pass found nothing new, decided by the benchmark).
- R11 The role prompt asks twice or blocks a job. Tripwire: `matterinfo_ok` cases (a typed role is never re-asked; non-tty
  writes nothing) and the stage 6 lines unchanged.

## §6 Contradictions with the spec, plan or owner rulings, and the rows they become (pending veto)

- **D63** (new; spec §5 Anonymizer row text replaced per D57; §3 gains the stage 7 half of step 7). "The anonymizer is
  `anon.py` under casefile-anon/1: the local model's entity pass (`07-ANON`, through the gates, chunked) finds names and
  the anchor date only, each as written on its page; the matter's name list lives in `matter.toml` `[anon]` (employer,
  ids, places, keep, people and organizations with kinds) and is fed by the header; a name the pass finds that is not on
  the list halts: asked on a tty and written once, `NAME LIST NEEDED` exit 2 otherwise; the anchor is the typed date of
  accident, the model's verified vote only when it is empty, else `ANCHOR NEEDED`; code replaces patterns, list ids, dates
  and names in that order per line, numbering by first appearance, never reusing a number, never touching a stamp, a page
  id or a line count; `[CLAIMANT]`, `[EMPLOYER]` and `[DOB]` are unnumbered; adjusters, insurers, providers (treating facilities and the
  defense examiner's company) and `keep` entries are kept (owner Q61, Q62); the identifier check runs on the exact bytes that would leave (list values, dates, patterns and titled
  names, every bracketed token a known placeholder, then a second entity pass whose failure is a block) and a hit stops
  the job before any file is written, logging step, kind and offset only; the key is `<matter>/anon/key.json`, mode 600,
  append-only, holding entities, refs and every date spelling seen; restore is canonical for prose and page-aware for
  quotes; what leaves the matter boundary is the package files, the failure and gate messages and a job's terminal output,
  never the run log's stored answers; the privacy row refuses an inventory path ending `anon/key.json` and a key-shaped
  `sk-ant-` secret in the checkout (D62 amended to that scope; the bench key and the spec's own wording are not
  offenders)." Why: §1.1 to §1.6, §1.9, §1.13, §1.15; Q47, Q53, Q61, Q62; D0.2; review H1, H2.
- **D64** (new; spec §2 brief paragraph made concrete; D49 extended). "`casefile brief-out --matter N "<issue>"
  [--pages all]` builds the anonymized fact package under `<matter>/outbox/<packet_id>/` (`package.md`: drafter rules,
  issue, the kept-names line, facts in chronological order with cites, conflicts with both pages' anonymized text, gaps,
  and with `--pages all` every anonymized page; `package.json`: the anonymized packet; `check.txt`), appends an `output` event `brief-out`, prints the package's sha256 and exits 0, 1 blocked, 2
  cannot run; approval and download are stage 7b and 8. `casefile brief-in --matter N FILE` reads a Word draft's body
  paragraphs (cites as `[cite X]` in the text, quotes in straight double quotes) and restores it from the key after `check_draft` (an invented or malformed placeholder, a real name or a calendar date blocks,
  exit 2, nothing written), fact-checks every cited paragraph against the real pages (cite resolves, quoted span on the
  page by the ladder through the page-aware restore, digit runs outside placeholders on the page, firm rules on prose with
  hits withheld, paragraph count unchanged), lists uncited paragraphs, and writes `outputs/brief-in-<stem>.docx` with each failure marked and a
  Fact check section (`.partial.docx` and exit 1 when any check fails)." Why: §1.7, §1.8; spec §2, §7 stage 7; Q41; Q62 items 93, 94;
  proposal §4 and §8.
- **D65** (D40, D46 amended). Old text (D40): "a fact's identity is the folded quote (`quotes.fold`)". New: "a fact's
  identity is the folded quote, the parsed date and the folded provider (`facts.identity`); a repeated quote with the
  same date and provider on a new page adds a `cite`; a different date or provider is a new fact; a new event kind
  `split` (`fact, page_id, to, cite, date, provider, text`) moves one cite and its reading from a fact merged under the
  old identity to a new fact id, appended by the next job that writes the matter (`memo`, `report`, `depo`, `hearing`,
  `brief-out`) before any other write, under the matter lock; `split` is a change kind for staleness and What changed;
  `casefile status` prints `split_needed`; a round 5 file
  needs no split." Why: §1.10; owner Q61; critic 2 M1; measured on the key (one pair, zero others).
- **D66** (D48 amended). Old text: "a binder's role is read from its name (`dme` or `defense medical`, any case or
  separator, is `defense`; every other binder is `ours`)". New: "a binder's role is read from its name: a whole word `dme`
  or `ime`, with or without digits or dots, or the phrase `defense medical` or `independent medical`, is `defense`; a
  word that only starts with `dme` or `ime` is `ROLE NEEDED` and is asked of the attorney at the first task run on a tty
  (`matterinfo.ask_roles`, written once to `[roles]`), a non-interactive run printing `ROLE NEEDED` without blocking;
  every other binder is `ours`." Why: §1.11; owner Q61; verifier finding 7; code review M2.
- **D67** (D34, D44 noted; no text change). The D44 rule "every object with a `quote` key carries a `cite` string" is now
  asserted by a test over the stage 6 and 7 schemas (13 of 13) and `outputs.evidence` fails closed; the stage 8
  `procedural` schema's `deadlines_stated` items carry `quote` without `cite` and are recorded as an open item for the
  stage 8 brief. Why: §1.12; verifier S3.
- Spec text drift (D0.2): D54 to D62 were added as rows without their section edits; W6 applies the stage 7 parts (§3 step
  7's first half, the §5 Anonymizer row) and leaves the 7b parts as rows with a note in §10. No owner ruling is
  overridden: Q47's four decisions, Q53's halts for briefs (mode B is the printed sha256 plus the 7b approval row), Q55,
  Q57, Q61 (fact identity, scope, roles, name list, port logic only) are built as written. Spec §2's "attorney approval;
  download" for the brief package is deferred to 7b and 8 by D54 and D58, which the owner ratified; D64 says so.

## §6b Privacy

Every fixture this round adds is invented and built from the 14 invented pages of `tests/fixtures/matters/9001.001/`: the
`[anon]` tables name only the ten people and seven organizations written on those pages; `entities.json` and its two
companions quote those pages; the two golden anonymized pages are the code's output over two fixture pages; the four
drafts are placeholder-form sentences about the fixture's invented facts with cites to its stamps; no key file is stored
in the repo (tests build keys under `tmp_path`); every `.docx` and every `outbox/` a test produces lives under
`tmp_path`. The reference script was read for logic only; its example names, its claim-number example and its prompt
wording are not reproduced here or in any fixture, card or test; the drafter rules in `anon.drafter_rules()` are written
fresh with placeholders only. Nothing under `~/local-worker/` data folders, `~/.claude/uploads/`, `Cases/` or `Bench/` was
read or will be read by a builder; the privacy row gains the `anon`/`key.json`/`sk-ant-` rules so a mistake is a red gate.

## §7 Questions only the owner can answer (appended to `docs/loop/questions-for-owner.md` as 88 to 95; all answered by
the owner, ledger Q62, and built as answered: 88 kept, 89 `[DOB]`, 90 interim, 91 interim, 92 interim, 93 `--pages all`,
94 Word draft, 95 `adjuster` kind; kept here as filed. The plan review raised no question only the owner can answer.)

88. The defense examiner's company (the fixture's invented evaluation vendor): numbered `[ORG-n]` like other organizations
    (interim), or kept unreplaced like a treating facility?
89. The date of birth: converted to a day offset from the injury like every other date (interim, the convention), or its
    own placeholder `[DOB]` so the package carries no exact age arithmetic?
90. Conflict excerpts for Claude (your Q41): the full anonymized text of both conflicting pages goes in the package
    (interim), or a fixed number of lines around each quoted line?
91. The review list (capitalised words that survive anonymization and are not placeholders, stamps, keep entries or
    dictionary words): printed in `check.txt` and on the status line only (interim), or a block until you clear each word?
92. Should the matter number and the Bates stamps stay in the package (interim: yes, they are the shared language of
    spec §8b), or be replaced too?
93. Package contents: the facts, the conflict pages and the gaps (interim), or every anonymized page of the matter as
    well (a `--pages all` flag), given that Claude reads the whole matter at a stage 7b task run?
94. `brief-in` input: a Markdown or plain-text draft with `"quote" [cite MED0003]` cites (interim), or a Word file?
95. People of kind `person` (a shift lead, a coworker, a wage clerk): replaced as `[PERSON-n]` (interim), and an adjuster
    is kept only when you add the name to `[anon].keep` (interim, per your Q61 "adjuster not replaced"): confirm, or
    should the entity card gain an `adjuster` kind that is kept automatically?

## §8 Plan review dispositions

Every finding was re-checked in the code on `6999988` or measured on the fixture through `scripts/run.sh python`
before it was accepted; the evidence is the file and line or the measured value. Counts: 21 accepted, 0 rejected,
0 owner (the owner's Q62 answers settled M10 and the four interims that changed).

| Finding | Disposition | Evidence and what changed |
|---|---|---|
| H1 privacy row red on the bench key and the spec | ACCEPTED | `tests/fixtures/matters/9001.001/key.json` is tracked; `privacy.py:11` inventories `--cached --others`; `docs/spec.md:280` holds `sk-ant-`. Measured: 0 inventory paths end `anon/key.json`, 0 files match `sk-ant-[A-Za-z0-9_-]{20,}`. Rule scoped to the path pair and the key-shaped secret, controls for the bench key and the spec wording, `expected=6`, D63 amends D62's text. §1.13, D0.9, W1b. |
| H2 `key_leak=0` cannot pass | ACCEPTED | `gates.py:331-333` records every raw answer; `runlog.py:17` `raw_answer TEXT NOT NULL`. Chair ruling: the run log is inside the matter boundary. `key_leak` scoped to `outbox/`, the `failures` and `gates` message columns and the job's stdout and stderr; recorded as decision §1.15 and in D63. W3. |
| H3 step 5 blocks the drafter rules and the keep line | ACCEPTED | §1.5 step 5 now admits the generic forms with a literal `n`, the unnumbered placeholders and `[cite X]`/`[page x]` runs naming packet pages; the keep line is bracket-free. §1.5, §1.8. |
| M1 `years=5` double counts the claim number | ACCEPTED | Measured: 5 bare years, 3 inside `QRL-2025-0418`; after the whole-token id step 2 remain (`medical/003.txt`, `defense-report/001.txt`). Stage 7 line reads `years=2 ids=3`; §1.4 (3) says so. |
| M2 no test drives the upgrade through a job | ACCEPTED | `outputs.py:296-318` and `memo_job.py:24-33` had no caller on a stored merged file. W1 gains `split_through_start` (both paths, `split_needed=1` to `0`), `casefile_ok=22 of 22`; seed (c) now goes red. |
| M3 `split` invisible to staleness and What changed | ACCEPTED | `facts.py:56` `CHANGE_KINDS`, `:138-146`, `memo.py:96-100` confirmed. `split` joins `CHANGE_KINDS`; What changed gains `N facts split`; seed (c2). §1.10, W1, D65. |
| M4 W2 seed (b) masked by the protected set | ACCEPTED | The seed now drops the protected set and the control is a unit page with raw stamp `MED 123456` (a six-digit run the detector would eat): `stamps_kept=15 of 15`, seed red at `14 of 15`. W2. |
| M5 step 1 over every list value blocks the fixture | ACCEPTED | Measured: the six kept organizations occur 22 times (the review's 18 plus the examiner's company, kept by Q62). Step 1 searches replaced variants, ids, the IAB number and the dob only. §1.5. |
| M6 ZIP and five-digit detectors unmeasured | ACCEPTED | Measured on the pages: 0 hits of `(?<=\b[A-Z]{2} )\d{5}(?:-\d{4})?\b`, 0 of `\b\d{6,}\b`; `$11861.20` present once. §1.4 binds ZIP to a state code; the wage line is an `anon_text` control. W2. |
| M7 lane B depends on lane A's numbering and rules text | ACCEPTED | §1b tabulates every placeholder by first appearance in page order and every date offset (measured); `rules_text` is a parameter of `package_text`. §1b, §1.8, W4. |
| M8 digit runs fail after a canonical restore | ACCEPTED | `gates.py:169-174` compares `\d+` run sets; `dates.py:13` gives `3/14/2025`. The rule reads the placeholder form outside bracketed tokens; seed (f) in W4. §1.7, D64. |
| M9 `identifiers_in_package` counts `plaintiffs = 1` | ACCEPTED | `matter.toml:5,11`. The oracle enumerates the ten surnames, the employer, the ids, the dob and the five typed header strings. W5. |
| M10 adjuster built the other way | ACCEPTED (owner) | Ledger Q61 and Q62 item 95: an `adjuster` kind in the schema enum, kept automatically; the keep-list interim withdrawn. §1.2, §1.4, W2. |
| L1 422 lines | ACCEPTED | `wc -l` over the 14 pages: 440 (422 text lines above the stamps). Header paragraph. |
| L2 "ten stage 6 and 7 schemas" | ACCEPTED | The manifest lists six schemas at stage 6 or 7 (13 quote objects) and five at stage 8. D0.8, §1.12. |
| L3 the `9001.002` copy keeps `number` | ACCEPTED | `pages.py:90-92` refuses the mismatch; W5 rewrites `number`. |
| L4 `test_status.py:100-101` whole-line pin | ACCEPTED | Confirmed; W1 lists it with `split_needed=0` after `gaps=4`. |
| L5 D0.1 stale | ACCEPTED | `git status`: ledger and questions file modified, `docs/loop/round-07/` untracked. D0.1; W6 appends nothing twice. |
| L6 title inside the brackets for the header's doctor | ACCEPTED | `matter.toml:8` `Dr. Priya Okonkwo-Lind`; §1.2 strips the title from header-fed names; §1b shows `[DR-5]`. |
| L7 key-never-shrunk test in no Ships list | ACCEPTED | W2 ships `key_grows=1` with a refusal case. |
| L8 a date split by a line break before its year | ACCEPTED | The reader allows one line break before the year in `text` and `check` alike and keeps the break after the tag; a unit control in `anon_text`; `lines_kept` holds. §1.4, W2. |

Owner Q62 folded in (not review findings): 88 the examiner's company is `provider` in the fixture list and kept
(`kept_orgs=6`); 89 `[anon].dob` and the `[DOB]` placeholder (`dob=14`, `dates=61`); 93 `--pages all` on the exit test's
good matter (`pages_in_package=14`); 94 the Word draft read by python-docx, fixtures as `.txt` lines built into `.docx`
under `tmp_path`; 95 the `adjuster` kind. 90, 91, 92 interims kept.
