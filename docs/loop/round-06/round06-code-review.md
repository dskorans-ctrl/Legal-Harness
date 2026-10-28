# Round 6 code review (fresh Fable reviewer, read-only)

Branch `loop/round-06` at 2c921ea, scope `git diff main...loop/round-06 -- src tests playbook cards schemas`.
Read first: CLAUDE.md, Librarian pre-flight and open items, spec §1, §4, D44 to D51, ledger Q49 to Q58 and
the round 6 chair rulings, the build brief (intent only). Probes ran through `scripts/run.sh python` on an
in-memory case file built from `tests/fixtures/matters/9001.001/ideal.json`; nothing in the repo was written
except this file. No real client data was read.

Counts: 2 high, 5 medium, 10 low. CONFIRMED means traced in code and, where marked, reproduced by a probe.

## High

### H1. Model strings reach every document through the exempt `reason` run, skipping the rules check (CONFIRMED, probed)
- `src/casefile/outputs.py:253-257` (`failure`), `:273-277` (`open_items_section`), `src/casefile/memo.py:105-106`;
  source strings at `src/casefile/gates.py:127-128` (60 characters of the rejected quote) and `:286` (`f.excerpt`,
  the text that broke a firm rule), carried by `:342`, `:352` and `log.record_coverage(reason=...)` into
  `status.snapshot` open items.
- Defect: `outputs.check` replaces every exempt run with a newline, so the gate's failure detail (which embeds the
  model's own violating excerpt or an unverified quote) is written into the `.docx` unchecked.
- Scenario: the defense-doctor card answers "The IME found a normal gait"; the rules gate fails it twice; the
  deposition document's primary section and open items both print `... (no-dme-ime: The IME found a normal gait)`.
  Probe: a `Doc` with that failure reason and an open item whose reason quotes "the IME exam of Dr. Marchetti was
  paid for by the carrier" returned `check findings: []` and rendered both strings into the Word file.
- The exempt list was meant for page text (quote), cites and typed binder names. A gate failure reason is our
  wording wrapped around a model string; it should be rules-checked or the excerpt dropped before it enters a
  document (keep the full message in the run log).

### H2. `packet.batches` drops every page that has no fact, then the document says those pages were searched (CONFIRMED, probed)
- `src/casefile/packet.py:84-86` (`_subset` keeps only pages whose id is a chosen fact's page), `:99-116`; compare
  `packet.fit` `:125-128`, which re-adds `deponent_pages`. Consumers: `report.run:94`, `hearing.run:203`,
  `depo.run:91`. Label: `outputs.elements:334-339` prints `NOT FOUND on pages <every packet page>`.
- Defect: `report_pages` and `deponent_pages` added at `packet.build:77-78` (the chair's defense-binder widening,
  the doctor's own records) survive only in the single-batch path (`:114`). As soon as the packet needs two
  batches, DEF0001 and DEF0002 (or any own-record page without a fact) are in no batch at all, so the model can
  never cite them, while the elements section names them as searched.
- Probe: the ours report packet for `defense-report` had pages 001, 002, 003 and 4 facts; with a `num_ctx` that
  forces splitting, `batches` returned three parts, each with pages `['defense-report/003']` only.
- Scenario: a defense report of 12 pages where the memo extracted facts from 3; concessions and the history
  pages are never sent; the report-analysis document prints `records_reviewed: NOT FOUND on pages DEF0001 ...
  DEF0012` as if read. Also, with several batches, `outputs.elements:333` keeps the last item per element, so a
  STATED from batch 1 is overwritten by a PARTIAL from batch 2 (`hearing.run:211-215` and `report.run:100-101`
  concatenate the lists).

## Medium

### M1. The bills exemption applies to every question, including the defense-examiner cross (CONFIRMED, probed)
- `playbook/rules.toml` `patterns_text_only`; `src/casefile/rules.py:72`.
- Q54 item 59(c) exempted charges and bills "inside a bills question" to our doctor. The code exempts the
  doctor pairing of `charges|charged|billed|bill|rate|engaged by` for the question unit of every card.
- Probe: `What did you bill for this examination, Doctor?` and `What did Dr. Marchetti charge for the
  examination?` give no finding with `unit='question'` and `no-hired-paid-retained` with `unit='text'`.
  The 02-C-DEFDOC card forbids fees only in words (ledger Q54 item 64 kept this interim for hire forms, not for
  billing forms).

### M2. Roles by binder name ignore IME and unseparated DME (CONFIRMED, probed)
- `src/casefile/roles.py:10-11`: `[-_\s]+` normalisation and `\bdme\b|\bdefense medical\b` only.
- Probe: `IME-report`, `IME`, `DMEreport`, `DME2025`, `D.M.E.` all return `ours`.
- Scenario: a binder named `IME Marchetti` (the common label in this practice; see #R01-CX-8, #R01-OC-H2 for the
  DME/IME class) is treated as our record: its opinions go under "Our doctors' opinions", conflicts with it are
  not put first, `provider_pages` does not widen it, and the hearing "Defense report points" section prints
  `none`, with no ROLE NEEDED anywhere because a role was assigned.

### M3. `--issue` accepts any text; the type's list is enforced only for `matter.toml` (CONFIRMED, probed)
- `src/casefile/cli.py:68`, `src/casefile/hearing.py:20`; the list lives in `matterinfo.py:9-10, 74-77`.
- Q57 ruled "issues from the type's list" and "the issues list replaces free-typed issues". Probe:
  `hearing.prepare(..., issue=('made up issue',))` yields a factsheet packet with `Issue: made up issue`, sent to
  the model and printed as the outline heading.

### M4. `provider_pages` is a case-folded substring test (CONFIRMED, probed)
- `src/casefile/outputs.py:172-173`.
- Probe: `--provider Dr` selects `medical/007, medical/008, defense-report/001..003` (our doctor and the defense
  examiner, widened), so an our-doctor deposition packet marks the defense examiner's report as the deponent's
  own record and `report --ours --provider Dr` analyses both doctors as one. A fixture provider `Dr. Theodore
  Marchetti` versus a typed `Marchetti` is fine; a short or shared token is not. Require a whole-provider or
  whole-word match, or refuse when more than one provider matches.

### M5. A failed run leaves the previous `.docx` reported `current` beside the new `.partial.docx` (PLAUSIBLE, traced)
- `src/casefile/outputs.py:145-147, 164-167`; `facts.stale_outputs:142-146`; `status.snapshot:45-47`.
- Scenario: `depo` succeeded yesterday (`depo-our-doctor-us.docx`, output event recorded); today a step fails
  and `depo-our-doctor-us.partial.docx` is written with exit 1 and no event. `casefile status` prints
  `depo-our-doctor-us:current` for yesterday's file, which no longer reflects today's run; and after a later
  success the `.partial.docx` is never removed, so two documents of the same name sit in `outputs/`.

## Low

- L1. `depo.missing_questions` (`depo.py:29-34`) is a presence-anywhere check: one compound question
  "Were the bills for the treatment sent to you?" satisfies both the treatment and the bills requirement
  (CONFIRMED, probed: returns `[]`).
- L2. Numbers in `undefined_labels[].label` are not checked against the page (`gates.py:149, 170` list
  `text, note, why, absent_note` only); probe: label `symptom magnification 9 of 10` passed with `exact=1`
  (CONFIRMED). The label is printed as "Model's note" in the report.
- L3. `report.run:107-108` indexes `stamps[0]` for the slug; on an unstamped matter run with `--pages` this is an
  IndexError, which is not in `outputs.ERRORS`, so the job ends in a traceback after the model calls and before
  publication (CONFIRMED by trace).
- L4. `outputs.start:234-236` asks the attorney and writes `matter.toml` before `rules.check_stamps` can refuse
  the matter (#R03-V-L1: refusals before side effects) (CONFIRMED by trace).
- L5. `matterinfo.ask` never asks whether the matter has more than one plaintiff (`HEADER[:-1]`, `:130, :144`),
  so a matter set up through the prompt always keeps `plaintiffs = 1` and roles are guessed by name; the Q57
  ruling's "multi-plaintiff needs typed roles" is reachable only by hand-editing (PLAUSIBLE).
- L6. Output documents for an unstamped matter carry `[page binder/NNN]` cites with no warning line; only the
  memo prints one (`memo.py:198-200, 232-235`). Cites are exempt runs, so `bates-cites` never runs on outputs
  and the Q53 interim "page-id cites plus the warning" holds for the memo only (PLAUSIBLE).
- L7. `packet.fit` always keeps every `deponent_pages` page (`:127`), and for the client and witness deponents
  that is every page of the matter (`depo.prepare:16-17`, `hearing.prepare:23, 33`), so on a matter whose pages
  alone exceed the budget the question step sends zero facts and fails the truncation gate instead of shrinking
  (PLAUSIBLE).
- L8. `memo.build:138-140` prints `ROLE NEEDED: no binder is marked other in matter.toml` in every memo whose
  binders are all ours or defense, which is the normal case (CONFIRMED by trace).
- L9. `tests/test_stage6_exit.py:285, 309, 330` build the expected document with the production renderers and
  `_rules` (`:74-96`) reuses the production exempt flags, so H1 cannot be caught there; the independent checks
  are `_rests`, `_conflicts_ok` and the count lines (CONFIRMED).
- L10. `packet.build:71-75` lists a fact none of whose pages is present (index 0 fallback) with a cite to a page
  not in the packet; any answer citing it fails `lookup` as "not a page of this chunk" (PLAUSIBLE; #R05-CX-3).

## Checked and not found
- Fail-open: `depo.run:106`, `hearing.run:216`, `report.run:102` store `None` for a failed step; `publish`
  writes `.partial.docx` and no output event when `failed_steps` is truthy (`outputs.py:145, 164`).
- Quotes, dates, providers and cites in every output answer are verified on the cited page by
  `gates._references`; prose numbers of `text, note, why, absent_note` are checked against the page for the
  stage 6 cards (`numbers_in: page`). Renderers read only gated answers, case-file facts and flags, pages and
  `matter.toml`; `tests/test_depo.py:90-92` proves render makes no model call.
- Q59 provider mask: applied only to the treatment group of `treatment-and-bills-apart`, with spaces of equal
  length, so `IME` inside a provider name still trips `no-dme-ime` (`tests/test_rules.py` asserts it).
- `matterinfo.ask` on a non-tty returns without reading or writing; no run flag writes `matter.toml`; the
  prompt refuses a matter type or issue number outside the lists.
- D51 upgrade: a V1 `fact` or `cite` payload is accepted by key set only, bytes and chain untouched; any other
  key set is still a broken chain. The recorded M4 limit (edited last payload) is unchanged.
- Privacy: nothing new leaves the machine; refusal text on stderr names providers (`outputs.py:196`), and the run
  log keeps gate reasons with model excerpts as before.

## Chair reproduction and rulings (2026-10-28)

Reproduced: H1 (traced: `outputs.py:253-257` `failure` and `memo.py:105-106` open items put `reason` text in exempt runs),
H2 (traced: `packet.py:84-86` `_subset` keeps only pages carrying a chosen fact; `outputs.py:333-339` NOT FOUND lists
every page of the packet), M1 (probed: `What did you bill for this examination, Doctor?` and `What did Dr. Marchetti
charge for the examination?` both return no finding as questions), M2 (probed: `IME-report`, `IME`, `DMEreport`,
`DME2025`, `D.M.E.` give `ours`; `DME-report` gives `defense`). M3 to M5 and L1 to L10 taken as traced by the reviewer;
each fix proves its finding red first.

Rulings (fix cycle 1, Codex):
- H1: text a document shows from a reason, a rejected quote or a rule excerpt is checked by the firm rules like our own
  words; any span a rule catches is replaced in the document by `[withheld: <rule id>]`; the run log and the CLI keep it
  verbatim. Only quotes verified on their page and cites stay exempt.
- H2: every page of a packet is sent in at least one batch (a page with no fact joins the first batch of its binder,
  else the first batch); element answers merge across batches (found in any batch wins; NOT FOUND names only pages sent
  in the batches that answered).
- M1: the bills exemption (Q59 c) applies only to a bills question on the our-doctor card; any question pairing a fee,
  bill, charge or rate with an examination, report, deposition or testimony still fails on every card.
- M2 (pending veto, extends Q57 with its synonym): after folding case and punctuation, a binder name whose word starts
  with `dme` or `ime`, or holding `defense medical` or `independent medical`, is `defense`.
- M3: `--issue` must be one of the type's list, else exit 2 before any model call. M4: provider selection matches the
  whole provider name after folding, or one unique word-bounded match; an ambiguous value refuses and lists the
  candidates. M5: a failed run leaves the earlier output listed `stale` (with the partial named), and a later success
  removes the stale `.partial.docx`.
- L1 a compound question satisfies neither topic; L2 numbers in labels checked on the page; L3 unstamped `--pages` use
  the page id, checked before any model call; L4 `check_stamps` before `ask` writes `matter.toml`; L5 `ask` asks the
  number of plaintiffs; L6 documents built from unstamped pages carry the warning line; L8 no ROLE NEEDED line when no
  binder needs a role; L9 the stage 6 exit test gains an oracle independent of the renderers (every run's text of each
  saved .docx, read back with python-docx, checked by the rules except verified quotes and cites); L10 a fact is
  listed only if a page it cites is in the packet. L7 (an oversize client packet fails instead of shrinking): recorded
  limit, tuning question.
