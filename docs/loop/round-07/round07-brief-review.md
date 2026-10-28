# Round 7 brief review (adversarial, read-only)

Reviewed: `.workflow/scratch/round07-build-brief.md` against `6999988` on `loop/round-07`, 2026-10-28. Static
review: premises traced in the source and the invented fixture (`tests/fixtures/matters/9001.001/`); no model run,
no app run, no `scripts/run.sh`, no git write. Fixture counts were re-measured with the system interpreter over the
fixture files only. Nothing under `~/local-worker/` (the reference script included), `~/.claude/uploads/`, `Cases/`
or `Bench/` was read. The brief's names, dates and the claim number were checked against the fixture pages: every
one is the repo's invented matter (no HIGH privacy finding on the brief's text).

Counts: 3 high, 10 medium, 8 low. CONFIRMED = traced in code or measured on the fixture; PLAUSIBLE = reasoned
from the brief's text.

## High

- **H1 (CONFIRMED) §1.13 and W1b: "offenders=0 today and after the change" is false; W1b commits red.** The
  bench answer key is a tracked file named `key.json` (`tests/fixtures/matters/9001.001/key.json`; D25 names that
  file), so the "file named `key.json` anywhere in the checkout" rule flags it. The bytes `sk-ant-` are in
  `docs/spec.md:280` (the D62 row itself) and `docs/loop/design/cloud-roundtrip-proposal.md`; `privacy.paths`
  (`privacy.py:11`, `git ls-files --cached --others` without `--exclude-standard`) also lists ignored files, so the
  brief itself (`.workflow/scratch/` is ignored by `.gitignore:61`; the literal is at brief line 274) and the planted
  literal inside `tests/test_privacy.py` would be offenders too. Built as written the gate prints at least 4, both
  lanes split from a red base, and the Mistakes Log R6 rule (measure a gate rule before ruling it) was skipped.
  Needed: the `key.json` rule scoped to the path pair `anon/key.json` (or any `key.json` outside
  `tests/fixtures/matters/*/`), the secret rule as a key-shaped pattern (`sk-ant-` followed by a run of key
  characters) with the test planting a synthetic key, and D62's text amended to say so.
- **H2 (CONFIRMED) W3 `key_leak=0` cannot pass: the run log stores every raw answer.** `gates.py:331-333` calls
  `log.record_answer(run_id, raw_answer=raw, ...)` on every received reply and `runlog.py:17,94-102` keeps it
  (`answers.raw_answer TEXT NOT NULL`, D15). After the entity pass the run log holds every `name` and `quote` of
  `entities.json`, and the memo's stored answers quote the date of birth (`02/17/1981`, 14 occurrences on the
  pages). "grep of the run log for each list value and the date of birth finds nothing" is red on a correct build,
  so the builder will narrow it without a ruling. Scope it: `failures` and `gates` message columns, stdout of the
  job, and every file under `outbox/`; the `answers` table is inside the matter boundary by D15.
- **H3 (CONFIRMED in the brief's text) §1.5 step 5 blocks the package §1.8 renders.** Step 5 says every bracketed
  token in the bytes must be a placeholder of the key and names `[DR 3]`, `[Dr-3]`, `[DATE]` as loose tags.
  `package.md` opens with the drafter rules "placeholders only" (generic forms such as `[DR-n]`, `[DATE D+n]`,
  `[EMPLOYER]` when no employer appears) and a keep-list line written as "`[anon].keep`"; none of those tokens is in
  the key. Lane A writes the check and lane B writes the renderer, so the collision surfaces only at W5, where the
  exit test needs `check=pass leaks=0`. Say which tokens the rules block may hold (or render the rules without
  bracket tokens) and what the keep-list line prints.

## Medium

- **M1 (CONFIRMED) W5 pins `ids=3 dates=75 years=5`; the step order of §1.4 gives `years=2`.** Of the five
  bare-year hits on the pages, three are the `-2025-` inside the three claim-number occurrences
  (`records/employer/001.txt:6`, `employer/003.txt:5`, `defense-report/001.txt:7`); step 3 replaces
  `QRL-2025-0418` whole before step 4 runs, leaving `2019` on `medical/003.txt:10` and `defense-report/001.txt:23`.
  Either the exit line is wrong or the id step is not whole-token; the `[ID-n]` count and the year count are
  double-counting the same bytes.
- **M2 (CONFIRMED) The upgrade path (R7-3 "old case files upgraded in place") ships with no test; W1 seed (c)
  cannot go red.** W1's test list drives `split_on_append` through `facts.append` directly; the stage 5 and 6 exit
  tests build fresh case files under the new identity (no split is ever needed); `tests/fixtures/outputs/9001.001/`
  holds JSON answers, not a case file. No test calls `outputs.start` (`outputs.py:296-318`) or
  `memo_job._run_locked` (`memo_job.py:24-33`) on a stored file with `split_needed=1`, so removing the
  `upgrade_events` call there turns nothing red. Add a case that writes a round 6 style file with the merged
  F05/F34 pair, runs `outputs.start` (and the memo job) and reads `split_needed=0` plus the `split` event.
- **M3 (CONFIRMED) A `split` event is invisible to staleness and What changed.** `CHANGE_KINDS`
  (`facts.py:56`) is `fact, cite, reading, flag, about`; `stale_outputs` (`:142-146`) and `changed_since`
  (`:138-140`) ignore any other kind, and `memo.py:96-100` renders What changed from those five counts only. After
  a `report` run appends the split, `status` still prints `memo:current` while the memo on disk shows F34 under the
  ER entry (the critic's M1), and the next memo says nothing changed. W1 lists neither `CHANGE_KINDS` nor `memo.py`
  although its pre-flight cites #R05-OC-1 and #R05-OC-3.
- **M4 (CONFIRMED in the brief's text) W2 seed (b) is masked by the protection it sits under.** §1.4 protects
  every stamp and page id from every step; loosening the id pattern to `\d{4,}` therefore cannot change
  `stamps_kept` (`14 of 14` stays), while it would eat every `2025` before step 4 and turn `anon_pages` red
  instead. The seed must target the protected set (or name `anon_pages` as the red line); as written the chair
  would record a green seed as proof.
- **M5 (CONFIRMED) §1.5 step 1 "every list and key value absent" blocks the fixture or is narrowed.** The list
  includes organizations of kind `insurer` and `provider` and every `keep` entry, which §1.4 never replaces; on the
  pages the five providers occur 18 times (Fennimore County Hospital 4, Lakeshore Imaging 4, Ridgeline Physical
  Therapy 4, Brightwater Family Medicine 3, Lakeshore Orthopedic Associates 3). As written step 1 reports
  `leaks=18` on a correct package and `kept_orgs=5` cannot coexist with `leaks=0`. Say "every variant of every
  replaced entry".
- **M6 (CONFIRMED) The ZIP and five-digit detectors were never measured on the pages (R6 rule).**
  `records/employer/003.txt:27` reads `Total gross pay, 13 weeks: $11861.20`; a bare five-digit ZIP detector (§1.4
  step 2) writes `$[ZIP-1].20`, breaks a wage figure the hearing needs, and the restore digit check then fails any
  draft citing it. The brief measured only "the reference code's id pattern". Bind ZIP to context (a state code or
  the word ZIP before it) and put the wage line in `anon_text` as the control.
- **M7 (PLAUSIBLE, from §1.8, W2, W4, W5) Lane B depends on lane A's numbering and rules text.** `package_text`
  (lane B) prints the drafter rules that `anon.drafter_rules()` (lane A, W2) owns; `draft.md` (lane B) is written
  in placeholder form with `[DR-1]`, `[DATE D+n]` and quoted spans that must restore byte-exact through lane A's
  `mapping` (numbers by first appearance in page order) and anchor arithmetic, which the brief never tabulates.
  They meet only at W5 (`checks=10 of 10`). Put the entity-to-placeholder table (measured from page order) and the
  anchor offsets of the quoted dates in the brief, and pass the rules text into `package_text` as a parameter.
- **M8 (CONFIRMED) §1.7's digit-run check on an unquoted cited sentence fails after a canonical restore.**
  `anon.restore` gives `M/D/YYYY` (`3/14/2025`) and the pages write `MM/DD/YYYY` (§1.6: "matches none of the 75
  page dates"); the digit-run rule as built (`gates.py:169-174`) compares sets of `\d+` runs, so `3` must be a run on
  the page. Any unquoted sentence carrying a date placeholder is red at W5 with no defect. Say whether digit runs are
  read on the placeholder form (placeholder numbers excluded) or on a page-aware restore.
- **M9 (CONFIRMED) `identifiers_in_package` counts "every header value".** `matter.toml:11` has `plaintiffs = 1`
  and `:5` `matter_type = "workers-comp"`; `1` is in every package, so the one independent oracle (#R06-CX-16) is
  red on a correct build and will be narrowed by the builder. Enumerate the five values (client name, date of
  accident, treating physician, hearing number, hearing date) and the DOB.
- **M10 (CONFIRMED against ledger Q61) The adjuster ruling is built the other way.** Q61: "the carrier, the
  adjuster and treating facilities are NOT replaced". §1.4 replaces every person of kind `person` as `[PERSON-n]`
  and keeps an adjuster only when the attorney types the name into `keep`; the card's kinds
  (`schemas/anonymize.schema.json` people enum) give the model no way to mark one. Question 95 asks what the owner
  already answered; the interim contradicts the ruling. Add an `adjuster` kind that is kept (the fixture has no
  adjuster, so the exit test cannot show it either way).

## Low

- **L1 (CONFIRMED)** "422 text lines": `wc -l` over the 14 pages gives 440. Informational only (`lines_kept` is per
  page), but a measured number that is wrong.
- **L2 (CONFIRMED)** "over the ten stage 6 and 7 schemas the count is 13 of 13": the manifest has six schemas at
  stage 6 or 7 (anonymize 4, concessions 4, elements 1, factsheet 1, medical_memo 1, questions 2 = 13) and five at
  stage 8. A builder who takes "ten" and includes `bills` (stage 8) gets 14.
- **L3 (CONFIRMED)** W5 copies the fixture to `9001.002`; `pages.py:90-92` refuses a `matter.toml` whose `number`
  differs from the folder (`number differs from matter folder`). The copy must rewrite `number`; the brief only
  mentions the extraction recording.
- **L4 (CONFIRMED)** `tests/test_status.py:100-101` asserts the whole status line; `split_needed=` after `gaps`
  moves it, and W1 lists that line for `facts=` only.
- **L5 (CONFIRMED)** D0.1 "three untracked leftovers only" is stale: `docs/loop/questions-for-owner.md` (88 to 95
  already appended) and `.workflow/LEDGER.md` are modified. §7's append is done; W6 must not append twice.
- **L6 (CONFIRMED)** The header feeds `treating_physician = "Dr. Priya Okonkwo-Lind"` (`matter.toml:8`) to the
  list as a doctor; §1.2 does not say the title is stripped, so the whole string becomes a variant and the title
  lands inside the brackets, against §1.4's "titles outside".
- **L7 (CONFIRMED in the brief's text)** R3's tripwire "a test asserts a saved key is never shrunk by `save_key`"
  is in no work item's Ships list.
- **L8 (PLAUSIBLE)** §1.4 replaces per line and §1.5 step 2 shares the date reader (#R04-PC-4), so a date split
  by a line break before its year is neither replaced nor detected: a leak class with no control. The fixture has
  none; the brief leaves it "open for the code review" rather than fixing the reader to look across one line break.

## Three changes to insist on before build

1. **Re-measure and re-specify the three red checks before W1b is cut (H1, H2, M9).** The privacy row scoped as
   in H1 with D62's text amended; `key_leak` over `failures`, `gates`, stdout and `outbox/` only;
   `identifiers_in_package` over the five named header values and the DOB. Each with its `offenders=` or count
   measured on the tip and written into the brief.
2. **Reconcile the identifier check with the package it checks (H3, M5, M6, M1).** Step 1 over replaced
   variants only; step 5 with the rules block and keep-list line either bracket-free or named as the one exemption;
   ZIP and id detectors measured on the fixture with `$11861.20` as the control; the stage7 line corrected to
   `years=2` (or the id step changed and the line re-derived).
3. **Close the two unguarded seams before the lanes split (M2, M3, M7, M8).** A W1 test that runs `outputs.start`
   and the memo job on a stored case file with the merged pair (`split_needed=1` to `0`, the `split` event in
   `CHANGE_KINDS` and in What changed); and an entity-to-placeholder table plus the digit-run rule for unquoted
   sentences fixed in the brief so lane B's drafts and lane A's goldens agree at W5.
