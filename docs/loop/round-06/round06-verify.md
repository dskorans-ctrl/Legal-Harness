# Round 6 blind verification (8c)

Verdict: PASS. R6-1, R6-2, R6-3, R6-4 and V. ticked with my own evidence. No blocking finding; seven
non-blocking findings and one unlogged design call below.

Verifier: fresh Opus session, no building context this round. Branch `loop/round-06`, tip 6fba08f. Blind
inputs only (request, ledger item wording, the CHECKs entry, the tree, `round06-mutated-lines.txt`) until every
item was ticked; then the reconciliation sources were opened. Every run went through `scripts/run.sh`; the model
was the stand-in; no test points at 127.0.0.1:11434 (`tests/conftest.py:41` uses port 9; the `11434` strings in
`tests/test_config.py` are refusal cases). Nothing outside the ledger and this file was left changed.

## Measured numbers (probe, then result)

| Probe | Result (verbatim) |
|---|---|
| `pytest -q -s tests/test_stage6_exit.py --basetemp=$TMPDIR/verify6` | eight `stage6` lines, last `stage6 exit=0 docs=6 of 6 answers=+16 rule_hits=0 server_stopped=1`; `1 passed` |
| `pytest -q -s` packet, outputs, report, depo, hearing tests | `packet_ok=6 of 6` `outputs_ok=13 of 13` `report_ok=9 of 9` `depo_ok=12 of 12` `hearing_ok=12 of 12`; `53 passed` |
| `tests/test_cards.py tests/test_playbook.py` | `cards_loaded=15 of 15` `schemas_loaded=11 of 11`; `16 passed` |
| `tests/test_memo.py` | `memo_docx_ok=22 of 22 memo_refused=1 of 1 memo_changed=1 memo_reason_withheld=1`; `24 passed` |
| `tests/test_roles.py tests/test_matterinfo.py` | `roles_by_name=6 of 6` `matterinfo_ok=12 of 12` `stamps_compatible=2 of 2`; `3 passed` |
| `tests/test_extract.py` | `no_reply_forms=3 of 3`; `3 passed` |
| `tests/test_rules.py` | `rule5_forms=18 of 18` `bills_forms=7 of 7`; `41 passed` |
| `tests/test_gates.py` | `gate_cases=39 of 39`; `78 passed` |
| `tests/test_facts.py` | `casefile_ok=17 of 17` |
| `tests/test_round06_fix1.py tests/test_round06_fix2.py` | `57 passed` |
| `pytest -q` | `786 passed in 65.76s`; prints `bench_chunks=3 found=36 of 36 flags=5 of 9 runs=+3 uncited=1` and `stamps_cases=8 of 8` |
| `python -m casefile.gate` | `gate playbook PASS invalid=0 unmarked=0 practice=13 samples=3 version=pb-b0f17098b48d`, last line `0` |
| `python scripts/unused_imports.py src tests scripts` | `unused_imports=0` |
| `scripts/suite_time.sh 3` | `suite_time runs=3 max=66.17 verdict=PASS`, exit 0 |
| bench `--candidate tests/fixtures/bench/flawed.json` | exit 1, `found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14` |
| bench `--candidate .../9001.001/ideal.json` | exit 0, `found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14` |
| stage 1 to 5 lines in the suite output | as pinned in `## Project` and the CHECK (`stage5 ... casefile_lines=56 chain_ok=1 server_stopped=1`) |

Every number the CHECKs entry names matches verbatim.

## The six documents (python-docx, `$TMPDIR/verify6/test_stage6_exit0/matters/9001.001/outputs/`)

Own probes: (a) every `"quote" [cite X]` pair checked as a substring of the cited fixture page (records in the
basetemp equal `tests/fixtures/matters/9001.001/records`, `diff -r` clean): 490 of 490 on their page; control (one
memo quote changed from negative to positive): `off=2`. (b) `rules.check` from `playbook/rules.toml` over every
paragraph with quotes blanked, numbered lines as questions: 0 hits in all six; control question "Did Dr. Marchetti
charge you for the IME report?": 3 hits. (c) DME, IME, independent medical, defense medical outside quotes: 0; em
or en dash: 0.

- memo.docx (215 paragraphs): header equals `matter.toml` `[header]` (workers-comp, Morgan Ashby-Vale,
  03/11/2025, Dr. Priya Okonkwo-Lind, 1234567, 01/15/2026 9:00 AM). Sections in spec §2 order: what changed,
  outputs out of date, open items (DEF0001 uncited), chronology (37 entries, "Entries run by the date of the
  record."), providers (6), diagnoses, restrictions, medical history, our doctors' opinions, defense doctors'
  opinions (DEF0003 only), other records (none), gaps (4), conflicts (5), undated by page (DEF0001 only, shown as
  `binder defense-report`). Conflicts: the three defense against ours come first (MED0008/DEF0003,
  MED0007/DEF0002, MED0006/DEF0002), then MED0001/EMP0001 and MED0001/MED0003; each is followed by
  `From [cite X]:` quotes from both pages. DEF0002 is quoted under both its conflicts (six findings under
  MED0007/DEF0002, "The L4-L5 disc changes are described as degenerative." under MED0006/DEF0002). Matches R6-3.
- depo-our-doctor-us.docx: header plus "Deposition of: Dr. Okonkwo-Lind", "Deposition date and time: NEEDED",
  "Purpose: discovery". Our view (19), defense view (11, all DEF0002 and DEF0003). Primary: the treatment question
  and, separately, the bills question naming "Fennimore County Hospital, Brightwater Family Medicine, Ridgeline
  Physical Therapy, Lakeshore Imaging, Dr. Priya Okonkwo-Lind": no Marchetti, no Northgate. One cross, one
  redirect, six danger items, points for our expert "none". Matches the claims.
- depo-defense-doctor-us.docx: six primary questions, all document based (records list, "What specific findings
  support the label", MRI accurate quotation twice, history); none asks him to confirm his own conclusion. One
  cross, one redirect, danger zone, one point for our expert.
- hearing.docx (531 paragraphs): starred billing memo item first; exhibits by binder; permanency and termination
  each with STANDARD NEEDED, our key facts, defense position, conflicts with quotes from both pages, open items;
  client direct 2 and likely cross 2; doctor prep with 14 elements (9 stated, 5 NOT FOUND); closing per issue with
  RELIEF NEEDED. The two issue sections are identical (owner Q59 item 86 parked to round 7).
- report-defense-report.docx: coverage (DEF0001 open, 002 and 003 read), what the report states, three conflicts
  with quotes, one concession, the undefined label with the four findings the report gives, danger item, cross
  topics, "Records review audit: not performed" disclosed.
- report-okonkwo-lind.docx: coverage MED0007 and MED0008 read, 14 elements (9 stated, 5 NOT FOUND, gaps listed
  separately), defense comparison, subjects to raise.

Content matches every claim of R6-1 and R6-3 that I checked. Content findings are listed below.

## Seeds (each applied alone, full `pytest -q`, restored and `cmp` clean, `git diff --quiet` on the file)

| Seed | File (on mutated list?) | Defect | Suite |
|---|---|---|---|
| S1 | `src/casefile/cli.py:128` (no) | hearing `doctor=args.closing, closing=args.doctor` (flags swapped) | GREEN, 786 passed: test gap |
| S2 | `src/casefile/status.py:47` (no) | partial outputs no longer counted stale | RED, 3 failed (`test_round06_fix1.py::test_m5`, `test_round06_fix2.py::test_a1_append_failure[report]` and `[memo]`) |
| S3 | `schemas/questions.schema.json` (no) | `quote` dropped from a question's required keys | GREEN, 786 passed: test gap |
| S4 | `cards/02-depo/c-our-doctor.md` (no) | "Topics 7 and 8 are ALWAYS two separate questions" reversed to "may be asked together" | RED, 1 failed (`test_cards.py::test_cards`, "card versions differ"): red by the version pin only |
| S5 | `src/casefile/outputs.py:95` (file listed, label code not) | "Model's note: " label dropped | RED, 2 failed (`test_depo_contract[0]`, `test_report_contract[0]`) |
| S6 | `src/casefile/benchscore.py:47` (no) | `dates_wrong` left out of `perfect` | RED, 1 failed (`test_benchscore.py::test_date_only_fault`) |

S3 follow-up probe (scratch test outside the repo, reusing `tests/test_depo.py` helpers): with S3 applied, an
our-doctor primary question with no `quote` key passes the schema and quote gates and the render then raises
`KeyError: 'quote'` at `src/casefile/outputs.py:91`, a traceback instead of a disclosed failure. Without S3, a
question with `"quote": ""` is refused by the coverage gate ("blank value at questions[0].quote"), exit 1,
`.partial.docx`: that path is guarded.

## Findings (none blocking)

1. Unlogged design call (med). depo-our-doctor-us prints "Purpose: discovery" (`cli.py:54` and `depo.py:14`
   default `discovery` for every deponent). Owner Q59 item 82 says our doctor's deposition is testimony preserved
   for the hearing. The chair parked 83 to 86 to round 7; 82's consequence (deponent-aware default, or a NEEDED
   purpose) has no ruling in the ledger. The chair should log one.
2. Test gap (med), S1: no test drives `casefile hearing --outline|--client|--doctor|--closing` through `cli.py`;
   swapping two flags stays green. Fix worker: a CLI test per flag asserting which sections the document holds.
3. Test gap (low), S3: no test pins that every output schema requires `quote` and `cite` on each asserting item
   (D44); `outputs.evidence` (`outputs.py:91`) indexes `item['quote']` unguarded. Fix worker: a schema test over
   `schemas/*.json` for the D44 rule, and fail closed in `evidence`.
4. Test gap (low), S4: card practice wording is guarded only by `test_cards`' version pin; a reversed firm rule is
   red only because a hash moved, and re-pinning would hide it. Fix worker: assert the firm skill sentences the
   cards must carry (treatment and bills apart, one fact per question).
5. Render (low): hearing.docx "Defense report points to be ready for" prints a bare "none" under the second,
   third and fourth DEF0003 opinions (my dump lines 333, 336, 339), the residue of the one block per conflict
   rule. Print nothing, or "conflict shown above".
6. Content (low): memo chronology lists DEF0002's 06/20/2025 "Straight leg raise negative bilaterally." only as
   "Also cited" under the 03/11/2025 Fennimore County Hospital entry (memo lines 27 to 30), so the examiner's
   finding sits under the ER's date and provider; report-defense-report has the mirror ("Also cited: [cite
   MED0002] " with a trailing space, and the also-cited reading printed before the main reading).
7. Roles (low, ruling consequence): `roles.role('Imelda Health', ...)` returns `defense` (`roles.py:13`, word
   starting with `ime`). This is the code review M2 ruling as written (pending owner veto); worth showing the owner
   with the veto.
8. Note: R6-4 "one stamp definition" is built as one refusal check (`rules.check_stamps` in `bench.py:53`,
   `memo_job.py:102`, `outputs.py:310`, each before the run log); three pattern strings remain (`matter.py:11`,
   `config.py:28`, `rules.toml:62`). Accepted under the CHECK's own wording.
9. Note: the spec §7 exit test says "pass the output critic"; the only recorded critic score is 5/10 on 1f987f6,
   before fix cycles 2 and 3. R6-1 is ticked on the ledger CHECK plus my own read; no re-critic is recorded.
10. Housekeeping: `cards/06-brief/` is an empty untracked directory.

## Reconciliation (after ticking)

Opened: `round06-critic.md`, `round06-code-review.md`, `round06-fix2.md`, `round06-fix3.md`, `.workflow/scratch/round06-W8.md`.

- Critic H1 to H4 are fixed in the documents I read: the defense primary is document based (H1); no Marchetti in
  the bills question (H2, now `providers_named=5 of 5`); the undefined label lists the four findings (H3); DEF0002
  is quoted under its conflicts (H4). M2 (defense view from defense binders only), M3 (nested headings), M4 (one
  block per conflict, see finding 5), L1 (no build jargon), L2 (human labels), L3 (one undated heading) and L6
  ("Deposition date and time: NEEDED") hold in my read. My 490 quotes and the critic's 479 come from different
  documents (fix cycle 2 added seven DEF0002 facts and removed repeated conflict blocks); 0 off in both.
- My finding 1 is the critic's owner question 1, filed as 82 and answered by the owner; it is the one owner answer
  of 82 to 87 with neither a build nor a parking ruling.
- The memo conflicts sentence ends "A cloud task run reads the whole matter." without D47's "(stage 7b)": the critic
  L1 ruling removed it on purpose. Not a finding.
- My finding 7 is code review M2 as ruled. Code review L9 (an independent oracle in the exit test) is what my own
  quote and rules probes repeat, and they agree with it.
- Builders' numbers agree with mine: fix3 `786 passed`, flawed `dates_wrong=1`, ideal 36 of 36; W8's
  `providers_named=6 of 6` was moved to 5 of 5 by the H2 fix.
- Process: fix3's moved pin record and full report link to `/private/tmp/round06-fix3/`, outside the repo, so they
  will not survive; fix2's pin record is in `.workflow/scratch/round06-fix2-pins.md`. Neither builder seeded the
  CLI flag wiring, the schema required lists or the card wording; S1, S3 and S4 are new.
