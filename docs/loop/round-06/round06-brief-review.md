# Round 6 brief review (adversarial, read-only)

Reviewed: `.workflow/scratch/round06-build-brief.md` against `53a6f82` plus the uncommitted records, on
2026-10-28. Premises were traced in the code or probed through `scripts/run.sh` with the project
interpreter (no file written, `PYTHONPYCACHEPREFIX` under `$TMPDIR`). No client data read. The firm skills
were read for their practice rules only.

Counts: 6 high, 8 medium, 6 low. CONFIRMED = traced in code or probed; PLAUSIBLE = reasoned from the brief.

## High

- **H1 (CONFIRMED) W1 edits three fixtures whose parsers it does not change; the lanes split from a red
  commit.** Brief §2 W1 adds `date`, `category`, `provider` to `ideal.json`, `key.json`, `flawed.json` and
  claims "the full suite green", `casefile bench --candidate ideal.json` exit 0 and a byte-identical bench
  line. But `src/casefile/benchcandidate.py:46` refuses any fact whose keys are not exactly `{cite, quote,
  text}` (exit 2), `src/casefile/benchkey.py:64-66` requires exactly `{id, cite, quote, text}` (every
  `test_bench_*` red), and `schemas/bench_extract.schema.json:10-16` keeps three fields with
  `additionalProperties: false` while `tests/fakemodel/bench.py:17,24-26` records `ideal.json` whole
  (`**answer`), so every stand-in extraction answer fails gate 3 at the W1 commit (stage 2, 4, 5 exit tests,
  `bench_chunks`, `test_memo_intake`). Those three parser changes are listed under W2. Built as written, W1
  cannot be committed green and both lanes start from a broken base.
- **H2 (CONFIRMED by probe) The three-chunk split moves at W1, not W3.** `tests/test_bench_pipeline.py:201-213`
  fixes `max_answer_tokens = 65536 - 16384` and asserts `[5, 5, 4]`. Probe with today's 920-byte card: +200
  bytes `[5, 5, 4]`, +400 `[5, 4, 5]`, +600 `[5, 4, 4, 1]`, +1200 `[4, 4, 4, 2]`. W1's card text (the
  `Firm rules:` block, five fixed lines, the §1.3 field sentences and the 24-category list) exceeds +300
  bytes. W1's file list omits `tests/test_bench_pipeline.py`; the budget fix is scheduled in W3. Red at W1.
- **H3 (CONFIRMED in the brief's own text) Gate 6's blank rule refuses the brief's own fixture answers.**
  §1.6 (lines 321-322): gate 6 for an output card requires "no blank string in any item". §1.8 (369-370):
  `02-A` `note` is "required non-empty only for danger"; (381) questions' `note` rendered "when non-empty";
  §1.7 (354-356): STATED elements carry no `absent_note`. Under the §1.6 rule every factsheet answer with a
  non-danger fact and every elements answer with a STATED element fails gate 6 on both attempts, the section
  is disclosed as failed and the job exits 1: `depo_ok`, `report_ok`, `hearing_ok` and the stage 6 lines
  cannot be reached. The brief needs per-card blank rules (a manifest field, or absent keys instead of empty
  strings) and W1's `required_any` test must cover the optional-blank case.
- **H4 (CONFIRMED) Lane B's tests depend on lane-A-owned stand-in changes that are scheduled after the
  merge.** W5 to W7 register recorded answers "through a new `FakeModel.record(row)`" (W8, lane A, after the
  merge) and W6's gate 5 case uses "the stand-in `forbidden_json` mode on a questions recording" whose
  `required_any[0]` branch is in `tests/fakemodel/core.py:37-65` (lane A, §4). The only recording builder,
  `tests/fakemodel/bench.py:14-18`, calls `gates.messages(card, pages, ...)` with no `body=`, so lane B has
  no sanctioned way to record a body-based prompt (#R04-PC-4 forbids hand-written message JSON).
  `FakeModel(recordings=[...])` (core.py:72-80) exists but W5 to W7 cannot run as written.
- **H5 (CONFIRMED by regex probe) The two new rule 5 patterns block ordinary client and witness questions.**
  Pattern `\b(?:retain|hire|engage)\w*\s+you\b|\byou\s+(?:are|were|have\s+been|had\s+been)\s+(?:retained|hired|engaged)\b`
  hits "You were hired by Quarry Ridge Logistics in August 2021, correct?", "Who hired you at the
  warehouse?", "Quarry Ridge hired you as a forklift operator, correct?", "You have been engaged in warehouse
  work since 2021, correct?"; the `how often|many times ... refer` pattern hits "How many times did your
  supervisor refer you to the clinic?". Gate 5 runs the rules over every output card's question text
  whatever the deponent (`gates.py:255-262`), so client-depo and client-prep sections fail closed and the
  document says `failed`. The D0.9 must-pass list holds only the "hired by" form; #R01-OC-H3 again
  (Librarian pre-flight line 23-25).
- **H6 (CONFIRMED in the brief's text; Q53 item 2) The renderers are not separated from the model call.**
  §1.7 to §1.9 describe `report.py`, `depo.py`, `hearing.py` as jobs that call `gates.ask(card, pages,
  body=...)` and assemble the document inline; §3's fixed interfaces (lines 789-794) list `outputs.header`,
  `check`, `publish`, `start` and no `render(answers, casefile, pages, attorney, ...) -> Doc` taking the gated
  JSON. The proposal's step 12 (`cloud-roundtrip-proposal.md` §3.2, "Merge or render: code, restored answer,
  stage 6 renderer") has nothing to call. Owner Q53 (ledger) requires the renderers to take the answer.

## Medium

- **M1 (CONFIRMED in the brief's text; Q53 item 1) The fact packet is an ad hoc prompt string per job, not
  a packet.** §1.4 and §1.6: blocks `[F12] MED0003 (03/14/2025, prior_history): "quote"` carry the stamp
  only (the page id only when unstamped); pages are passed "for cite lookup only" and their text is not in
  the body; no task options or playbook version in the body. Proposal §3.2 step 3 defines `packet.json` as
  facts with quote, cite and page id, the cited pages' text, options and playbook version, and its restore
  check (§4 step 3) resolves cites to pages of the packet. A restored cloud answer would come from a prompt
  of another shape. One `packet.build(...)` structure, shared by both paths, is missing.
- **M2 (CONFIRMED in the brief's text; Q53 item 1) Not every assertion carries a cite and a quote.**
  §1.8 line 376: `points_for_our_expert [{text, cite}]` (no quote), `missing: [string]` (neither);
  `danger_zone[].why` and `note` are prose with a cite only. Q53 asks a cite and quote on every assertion;
  `missing` and `points_for_our_expert` have nothing gate 4 can verify. Either add a quote or drop them
  (question 63 is the owner's call on notes, not on unverifiable lists).
- **M3 (CONFIRMED against proposal §4) The anonymization card cannot pass when nothing is found.**
  W1 sets `07-ANON` `required_any ["people", "organizations", "places"]` and a required `anchor_date
  {date, quote, cite}`; §1.6 makes an answer with every `required_any` array empty a gate 6 failure. The
  identifier check's step 4 (proposal §4) needs the second entity pass to return no person, organization or
  place as its pass, and a packet without the accident date fails the schema. The card as specified fails
  closed on the exact answer the check wants.
- **M4 (CONFIRMED in the brief's text) Practice entries are injected by `kind` only, with no deponent
  filter.** §1.2 lines 143-144: "entries with `sample = false` whose `kind` is in the card's `kinds`";
  manifest v2 has no `deponent` field while the entries carry one. So `defense-doctor-no-defense-work` and
  `defense-doctor-documents-not-medicine` (depo-goal) enter `02-C-OURDOC`, `02-C-CLIENT`, `02-C-WITNESS`
  wherever `kinds` holds `depo-goal`, and `question-form` ("short, leading") enters `03-CLIENT`, whose seed
  card (`cards/03-hearing/client-prep.md`) says direct examination is open questions, not leading. A firm
  rule applied to the wrong deponent is the builder's taste, not the skill.
- **M5 (CONFIRMED) The exit fixture dodges the fixture's own provider list.** The test matter has a
  therapy provider (`Ridgeline Physical Therapy`: `records/medical/003.txt`, `004.txt`, `007.txt`,
  `defense-report/001.txt`, `003.txt`), which §1.3's `provider` field will extract. The skill (§1) says the
  bills question walks the provider list; the §1.10 fixture names only `Lakeshore Orthopedic Associates` and
  `Lakeshore Imaging` so `treatment-and-bills-apart` (`rules.toml:43`, `\btherapy\b`) does not fire. The
  stage 6 line's `bills_q=1` then certifies a question that omits a provider of record; the brief says the
  document "shows the practice as the skill wants it", which is not so. Question 59's interim (a) is being
  built into the fixture as if settled; the output critic must be told.
- **M6 (PLAUSIBLE) A document with a failed section is published as current.** §1.6 `publish` appends the
  `output` event `{name, path, built_from_seq, facts, conflicts, gaps, open}` whether or not a section
  failed (exit 1). `status.py:45-47` then prints `<name>:current`, `stale_outputs` and the memo's `Outputs
  out of date` never list it, and no later run rebuilds it until a fact changes. Pillar 2 and #R05-OC-1: the
  event needs the failed sections (or `publish` must not append on a failed step).
- **M7 (CONFIRMED) Q54's ordering is widened.** Ledger Q49 item 54 and Q41: conflicts between a defense
  examination binder and our records first. §1.5 orders first every conflict with a `defense` page and a
  page "of a binder with another role", which includes `other` (the employer binder in the fixture). Should
  be `defense` against `ours`, the rest in found order.
- **M8 (PLAUSIBLE) The reconcile answer is verified less than §1.4 implies.** The reconcile body carries
  no page text and its flags carry cites only, so gate 4 verifies that two cites resolve to distinct pages
  (`gates.py:98-105, 134-135`) and nothing else; `about` digits are not checked (`gates.py:148-153` checks
  `facts[].text` only). "Gates 1 to 5 unchanged" reads as if the conflict were verified on the page. The
  memo must label reconcile abouts as the model's reading (it does, through `Model's reading`), and the
  brief and D47 should say exactly what gate 4 verifies for a reconcile call.

## Low

- **L1 (CONFIRMED) D0.7 misreads `memo.check`.** `memo.py:178` exempts any run with a non-empty `exempt`,
  not only `quote` and `reason`; W4's `cite` and `binder` exemptions need no change to `check`, and seed
  W4(d) must target `_cite` (`memo.py:56-57`) to go red. `render` (`memo.py:192`) also calls `check_binders`;
  W4 lists only the `memo_job.py` calls.
- **L2 (CONFIRMED) Counts disagree inside the brief.** W5 says "two conflicts (G3, G6, G9 cite report
  pages: three)" while the stage 6 line pins `conflicts=3`. W3 case (5) asserts that no check exists (a case
  that cannot go red on the defect it names).
- **L3 (CONFIRMED; Q53 "no Ollama-only feature in card text")** `extract.ID_SENTENCE` ("the prompt_id
  line at the top of this message") stays in every card text; the proposal §5 moves the nonce to the last
  block of the user turn for the cloud path, where the sentence is wrong.
- **L4 (PLAUSIBLE)** `status.py:31,37` uses `memo.OpenItem` and `memo.label`; §3 says lane B moves "the
  paragraph model" to `outputs.py` without listing what moves. If `OpenItem` or `label` moves, `status`
  breaks at the merge.
- **L5 (PLAUSIBLE)** W1 makes `benchkey` require a `date` on every key fact "validated on the page" but
  §1.3 lists dates for eleven pages only; whether a key fact on a page with no date of service may carry an
  empty date is not stated.
- **L6 (CONFIRMED)** D0.13 says owner questions end at 58; `docs/loop/questions-for-owner.md` already holds
  59 to 69 (this brief) and 70 to 80 (the proposal). W9 must not renumber.

## Three changes to insist on before build

1. **Make W1 a green commit.** Either move `benchcandidate.parse`, `benchkey.load`, the widened
   `medical_memo.schema.json` and the split test's budget derivation into W1, or move the fixture edits to
   W2; and put the stand-in support lane B needs (`FakeModel.record`, a body-aware recording builder, the
   `forbidden_json` branch on `required_any[0]`) into W1 so both lanes can test against it (H1, H2, H4).
2. **Give every output job the shape Q53 requires:** `packet.build(casefile, pages, task) -> Packet`
   (facts with quote, cite and page id, the cited pages, options, playbook version), `ask(packet, card)`,
   and `render(answers: dict[str, dict], packet, attorney, ...) -> Doc` as fixed interfaces; per-card blank
   rules in the manifest; a `deponent` filter on practice injection; a quote on every schema assertion or
   the field dropped; `07-ANON` allowed to answer empty (H3, H6, M1, M2, M3, M4).
3. **Narrow the new rule 5 patterns to the defense-doctor card or hold them for question 64**, add the
   client-employment leading forms to the must-pass table, and tell the output critic that the fixture's
   bills question omits the matter's therapy provider under question 59's interim (H5, M5).
