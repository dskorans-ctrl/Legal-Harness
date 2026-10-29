# Round 7 code review (static, fresh Fable)

Scope: `git diff main...loop/round-07 -- src cards schemas tests` on `loop/round-07` at 99fb224. Read first: CLAUDE.md,
`Librarian.md` (pre-flight and rounds 1 to 6), brief §1, §1b, §1.15, §6, ledger Q61, Q62, `## Round 7`, and the chair rulings
(non-tty halt prints kind and cite only; run log and `<matter>/anon/` inside the boundary; package files, failure and gate
message columns and a job's terminal output outside). No file was modified except this report; nothing was run.

Counts: 1 high, 4 medium, 8 low.

Line numbers are those of the working tree on `loop/round-07`.

## High

### H1. A second spelling of the claimant or the employer leaves through every code step and cannot be registered (CONFIRMED)
Files: `src/casefile/anon.py:104-109` (`variants`), `:160-161` (`mapping` merges a hit only when `quotes.same(strip_title(hit.name), v)` for an existing variant), `:168-171` (`[CLAIMANT]`/`[EMPLOYER]` refuse a second entity), `src/casefile/anon_job.py:96-102` (`_members`), `:125-143` (`halt` writes the hit as a new claimant).
Defect: a person's variants are only the full name and its last token (plus capitals), an organization's only its typed name, so a given name alone, a `Surname, Given` form, a `Logistics, LLC` form or an abbreviation is neither replaced by `text()` nor searched by `check_code` step 1 (`:398-404` searches `key.entities` variants only); the only remaining guard is the model's second pass (step 4), and the remedy the halt offers cannot be taken for the two unnumbered kinds.
Scenario: a face sheet line `ASHBY-VALE, MORGAN` (or an OCR wrap `Morgan\nAshby-Vale`). `text()` yields `[CLAIMANT], MORGAN`; steps 1, 2, 3, 5 pass (`MORGAN` is no variant, no date, no pattern, no tag); if the local model does not report `MORGAN` on the anonymized page the package leaves with the given name in `package.md` and `package.json`. If the model does report it on pass 1, `halt` demands a list entry (`NAME LIST NEEDED ... claimant (MED0001)`); on a tty the default kind `claimant` is written to `[anon.people]`, then `mapping` raises `conflicting unnumbered entity` on every later run until `matter.toml` is hand edited. The same chain holds for `Quarry Ridge Logistics, LLC` (`strip_title` cuts at the comma, so it never matches the typed employer) against `[EMPLOYER]`. The brief's promise "a given name alone only when a hit names it alone" (§1.4) is not implemented: `mapping:160` merges only hits equal to an existing variant. The exit test cannot see this: `_identifiers` (`tests/test_stage7_exit.py:50-52`) counts surnames and typed values only, and the fixture writes every person with a surname (brief line 34).

## Medium

### M1. `package.json` carries every page of the matter whether or not `--pages all` was given (CONFIRMED)
Files: `src/casefile/brief_out.py:33` (`value = replace(value, pages=tuple(started.loaded.pages))`), `:40`, `:46` (`anonymous.to_json()` is the packet with those pages).
Defect: the packet's page set is widened to the whole matter for the entity pass and never narrowed back before serialization, so the owner's ruling (Q62 item 93: the package is facts, conflict pages and gaps; `--pages all` adds every page) holds for `package.md` only.
Scenario: `casefile brief-out --matter 9001.001 "issue"` without the flag: `package.md` has no `## Pages` section, but `package.json` under `outbox/<id>/` holds all 14 anonymized page texts; stage 7b would send them. The exit test only runs `--pages all` (`tests/test_stage7_exit.py:118`) and pins `len(anonymous.pages) == 14`, so the default path is unmeasured. The pages are at least identifier-checked (`:48-55`), so this is bulk the owner rejected, not an unchecked leak.

### M2. Two people who share a surname get one placeholder, the last entity's, for every surname-only mention (CONFIRMED)
Files: `src/casefile/anon.py:253-257` (`lookup = dict(forms)`; a repeated variant keeps the last tag), `:104-109`.
Defect: the replacement map is keyed by variant text, so a surname variant shared by two entities maps to whichever entity comes later in `key.entities`; `halt` refuses an ambiguous model hit (`anon_job.py:114-116`) but `mapping` and `text` never refuse the ambiguity.
Scenario: `[anon.people]` holds `Althea Quill = doctor` and `Beatrice Quill = person`; a page line `Dr. Quill reviewed the MRI` becomes `Dr. [PERSON-1]`, the drafter attributes the opinion to a lay person, and `brief-in` restores the quote to `Dr. Beatrice Quill` (which `restore_quote` may still find on the page if the surname alone is written there). A restore to the wrong person with no block and no warning.

### M3. Date forms outside the four handled spellings leave with the check passing (CONFIRMED)
Files: `src/casefile/anon.py:70-74` (`FULL_DATE`, `MONTH_DATE`, `YEAR`, `DATE_REF`), `:412-415` (step 2 uses the same regexes).
Defect: the replacer and the check share one set of patterns, so a date the replacer cannot read is also a date the check cannot see; two-digit years, ordinal days and day-first forms are common in medical records.
Scenario: a page line `DOS 3/11/25` is untouched and passes steps 1 to 5 (`\d{4}` required; `25` is not a `YEAR`); `March 11th, 2025` becomes `March 11th, [YEAR Y+0]` (the `,?` then `\d{4}` fails on `th`; `DATE_REF` fails on the `t`), leaving month and day of the accident; `11 March 2025` becomes `11 [MONTH M+0]`. Each is the accident date in a form the brief's list (§1.4 item 4) did not include. A planted `03/12/2025` is the only date form `test_code_sixteen` seeds.

### M4. The upgrade splits every later cite into its own fact, so two cites with one identity become two facts that can never merge (CONFIRMED, pinned by a test)
Files: `src/casefile/facts.py:288-302` (`upgrade_events` emits one `split` per cite whose identity differs from the first, with no grouping), `:326` (`merge` keys `facts` by identity, so duplicates shadow one another), `tests/test_facts.py` `split_on_append` (`assert new.split_needed == 0 and len(new.facts) == 3`).
Defect: the brief (§1.10) rejected identity by cite because "two pages of one visit would become two facts"; the upgrade does exactly that for every identity group after the first.
Scenario: a fact cited on medical/002 (03/11/2025, Dr. A), defense-report/002 and defense-report/003 (both 06/20/2025, Dr. Marchetti). The upgrade appends two splits; the view holds three facts, two with the same quote, date and provider; `split_needed` is 0 so nothing will ever rejoin them (append only); the memo and the brief package list the examiner's finding twice, once per page; a later extraction of that quote attaches its cite to whichever duplicate `merge` built last. The test pins `len(new.facts) == 3` where the identity rule wants 2.

## Low

### L1. `restore` turns loose `D-n` and `DR-n` tokens in ordinary prose into dates and names (CONFIRMED)
File: `src/casefile/anon.py:296-297`. `vitamin D-3 supplement [cite MED0005]` passes `check_draft` (no tag) and the digit check, then `restore` writes `vitamin 3/8/2025 supplement` into `outputs/brief-in-<stem>.docx` with no failure mark; `D+2`, `DR-1` in text behave the same. The reference's "shortened forms" repair needs a context test (a preceding `[` or the word `DATE`) or a draft-side block.

### L2. `DATE_REF` may consume a line break, breaking the per-line invariant (CONFIRMED)
File: `src/casefile/anon.py:74` (`\s+` spans newlines), `:252` (`_allocate` returns the tag without re-adding the break, unlike `_date_tag:214`). A page wrap `on March\n14 the patient` becomes one line; `lines_kept` is measured only on the fixture, which has no such wrap. `restore_quote` still succeeds (whitespace folding), so only the line count claim of §1.4 breaks.

### L3. A birth date is `[DOB]` only when typed or labelled `DOB`/`Date of Birth`; other labels give an offset (CONFIRMED)
File: `src/casefile/anon.py:231-233`. With `[anon].dob` empty and a page writing `D.O.B.: 02/17/1981`, `Birth date:` or `Born`, the date becomes `[DATE D-16093]`, the day offset the owner rejected (Q62 item 89); step 1 cannot flag it (`namelist.dob` empty). The label regex should admit dotted and other common labels, or an empty `dob` should be refused like an empty anchor.

### L4. A `MatterInfoError` prints a typed name on a non-tty stderr (CONFIRMED)
Files: `src/casefile/matterinfo.py:114-115` (`refuse(f'anon.{key}.{name}')`), `src/casefile/brief_out.py:88-90`, `src/casefile/brief_in.py:61-63` (`cannot run: {exc}`). A `[anon.people]` entry with a mistyped kind makes `brief-out` print `.../matter.toml: anon.people.Morgan Ashby-Vale: invalid or unknown value` to stderr, which the chair ruled outside the boundary. The key name alone (`anon.people`, entry 3) would do.

### L5. SSN and phone spellings without hyphens pass the pattern detectors (CONFIRMED)
File: `src/casefile/anon.py:77-78`. `321 54 9876` and `321.54.9876` match neither `ssn` (hyphens required) nor `phone` (`\d{3}[ .-]\d{4}` needs a three-digit middle group) nor `id` (digits are not six contiguous); the number leaves and step 3 is silent. Same class as M3 (one pattern set serves both replacer and check).

### L6. Step 4 blocks on things the attorney cannot fix: a placeholder reported as a name, or a kept entry reported in another form (PLAUSIBLE)
File: `src/casefile/anon_job.py:212-218`. `entity_pass` keeps any hit whose `name` is found on the anonymized page; a model that returns `name: "[CLAIMANT]"` (it is on the page) or `Beatrice Finch` for a `keep` entry stored as `Dr. Beatrice Finch` (`halt:137` keeps the hit as written; `check:213` compares by `quotes.same`) blocks every package with `step 4 (person, offset N)` and no remedy the message names. Fail closed, but the card's "copied exactly as written" instruction is the only defence; a hit that is itself a known placeholder should be dropped like an off-page hit.

### L7. Curly quotes in a Word draft silently skip quote verification (PLAUSIBLE)
File: `src/casefile/brief.py:16` (`QUOTED` straight quotes only), `:187-191`. Word's autocorrect turns typed straight quotes into curly ones; such a paragraph is then "a cited paragraph without a quoted span": its digits are checked against the page, its quoted words go through the firm rules unexempt, and the status line still prints `checks=N of N`. The brief specifies straight quotes (§1.7), but the degradation is invisible; counting curly-quoted spans as `skipped` or failing them would make it visible.

### L8. `test_contract_totals` prints a constant verdict (CONFIRMED)
File: `tests/test_brief.py` (`print('package_ok=9 of 9 draft_ok=10 of 10')`). The nine and ten parametrized rows do fail individually, but the summary line the chair reads is not derived from them (#R01-CX-9 class: a claim not measured by the thing printing it). Stage 7's `errors` list in `tests/test_stage7_exit.py` is likewise never appended to; the asserts carry that verdict.

## Rulings and pre-flight walked (no finding)
- Employer always `[EMPLOYER]`, IAB number and claim number `[ID-n]`, carrier, adjuster, treating facilities and the examiner's company kept (`NameList.kept`, `mapping:156`), `[DOB]` unnumbered, adjuster kind in schema and card, review list printed only (`brief_out.py:60-63`), matter number and stamps kept (`protected`, `package_text`), `--pages all` for `package.md`, `brief-in` refuses anything but `.docx` (`brief_in.py:35`), roles whole word or `ROLE NEEDED`, non-tty prints `ROLE NEEDED` and never writes (`ask_roles`), non-tty halt prints kind and cite only (`anon_job.py:122-123`).
- Key: written only under `<matter>/anon/` through `O_EXCL` 0600 and `os.replace`, directory 0700, load refuses mode bits over 600 and symlinks, append-only guard on every table; not shrunk.
- Model answers: both passes go through `gates.ask` with `_PrivateLog`, a non-ok outcome or `ModelError` is `EntityError`, a step-4 failure is a block (`check:207-209`), code steps run before the model call (`check:201-203`).
- Split: refused for an unknown origin, a reused `to`, a page not on the fact; applied once (`_decode` refuses a second split of the same page); appended under the matter lock before any other write; `status` never writes; round 5 files need none.
- Pre-flight classes rechecked: #R03-CX-5 boundaries at both ends (`boundary`, step 1 `(?<!\w)...(?!\w)` on the folded text, `_fold_positions` mirrors `quotes.fold`); #R06-CX-1 reasons are rules-checked in documents (`checked_runs`); #R03-CX-2 package publish rolls back only owned paths; #R03-V-L1 refusals before side effects (the halt follows one model call by design); #R01-CX-11 exit codes asserted in the stage 7 tests.
