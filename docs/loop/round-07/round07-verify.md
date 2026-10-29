# Round 7 blind verification (stage 7 brief package and anonymizer)

**Verdict: PASS.** R7-1 to R7-4 and V ticked with fresh evidence. 12 of 12 seeds went RED. Three medium findings and
two low ones are open, and none of them blocks the exit test.

Verifier: Opus, fresh session, 2026-10-28, branch `loop/round-07` at tip 68f57fa. I built nothing this round. I opened
no builder record, critic record, review record or brief until every item was ticked. Scratch and seed copies are under
`$TMPDIR/verify7` (`/private/tmp/claude-501/verify7`). Every run went through `scripts/run.sh`, and the stand-in model
listened on an ephemeral port. I read nothing under `~/local-worker/`, `~/.claude/uploads/`, `Cases/` or `Bench/`.

## Measured numbers (probe, then the line it printed)

| Probe | Line | Baseline |
|---|---|---|
| `scripts/run.sh pytest -q` | `937 passed in 81.08s (0:01:21)` | 786 at round 6 (round 7 adds tests) |
| `scripts/run.sh python -m casefile.gate` | `0`, exit 0 (`gate prose PASS dashes=0 files=275`, `gate privacy PASS offenders=0 scanned=891`) | `0` |
| `scripts/run.sh python scripts/unused_imports.py src tests scripts` | `unused_imports=0` | same |
| `pytest -q -s tests/test_stage7_exit.py` | `stage7 exit=0 packages=2 of 2 blocked_seeded=1 of 1 drafts=2 of 2 answers=+8 identifiers_in_package=0 server_stopped=1` (31 passed) | new |
| stage 5 exit test | `stage5 exit=0 runs=4 of 4 memos=3 of 3 answers=+4 casefile_lines=55 chain_ok=1 server_stopped=1` | `casefile_lines=56` (see note) |
| stage 6 exit test | `stage6 exit=0 docs=6 of 6 answers=+16 rule_hits=0 server_stopped=1` | same |
| bench, flawed candidate | exit 1, `bench 9001.001 model=candidate found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=1 flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14` | byte-equal |
| bench, ideal candidate | exit 0, `bench 9001.001 model=candidate found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14` | byte-equal |

Note on stage 5: under the new identity, DEF0002's `Straight leg raise negative bilaterally.` is one `fact` event. The
old identity wrote it as a `cite` event plus a `reading` event, so the case file has one line fewer. W1 recorded this in
its report (`(50,52,55,56)` to `(49,51,54,55)`). The ledger `## Project` baseline still says 56.

## Outputs I produced from the invented matter

Driver: `$TMPDIR/verify7/driver.py`. It copies `9001.001` into a scratch config, records the ideal extraction and the
fixture entity answers on the stand-in, then runs the real CLI: `memo`, `status`, `brief-out "Review the records"
--pages all`, `brief-out "Review selected records"`, then `brief-in` on Word drafts I wrote myself.

- `brief-out ... --pages all` printed `brief-out 9001.001 packet=49e5914290bf sha256=49e59142...0e facts=38 pages=14
  conflicts=5 open_items=1 check=pass review=24` and exited 0. The default run printed `packet=cf31616a898d ... facts=38
  pages=9 ... review=14` and exited 0.
- **package.md** (both packages) contains, in order:
  - the drafter rules 1 to 8, plus the firm rules (`no-dme-ime`, `no-hired-paid-retained`, `treatment-and-bills-apart`,
    `bates-cites`, `header-block`);
  - the matter number, the issue, and the kept-names line (six providers);
  - `## Facts`: 38 facts in date order, each quote with its `[cite ...]`;
  - `## Conflicts`: 5 conflicts, each with the model's reading and both full anonymized pages, defense and ours pairs
    first;
  - `## Gaps` (4) and `## Pages not yet read` (DEF0001, with its anonymized page).

  Only the `--pages all` package has `## Pages`, with 14 page blocks. This matches D64 and Q62 item 93.
- **package.json** has the keys `facts, flags, matter, options, pages, playbook_version, task`. Its facts carry only
  `quote` and `cite` (38 of them). It holds 14 pages with the flag and 9 without, and the 9 are the pages that
  package.md shows. This matches the claim.
- **check.txt**: `steps=1,2,3,4,5 check=pass leaks=0 entities=17 pages=14 review=24` plus the review words, which are
  ordinary clinical words. Modes: folder 700, files 600, `anon/key.json` 600 inside the matter folder.
- **Leak grep** (`$TMPDIR/verify7/leak.py`, independent of `anon.py`): 78 values were checked. They are every
  `[anon.people]` name and the header names, each as full name, given name, surname, `Surname, Given` and surname
  halves; the employer with and without LLC, `Quarry Ridge`, `Quarry` and `QRL`; the ids; the DOB in four spellings;
  the IAB number; the date of accident and hearing date spellings. A calendar-date regex also runs on text outside
  placeholders. Result over all six package files: `leak_total=0`. Control over `records/medical/001.txt` and
  `records/defense-report/001.txt`: `leak_total=60`, so the oracle works.
- **brief-in**, own 8 paragraph draft (`v7draft2.docx`): `brief-in 9001.001 file=v7draft2 checks=24 of 28 failed=4
  uncited=2 rule_hits=1 output=brief-in-v7draft2.partial.docx exit=1`. The .docx contains:
  - the header block with the real names, and the restored paragraphs (`On 03/11/2025 Morgan Ashby-Vale was seen: "Date
    of Service: 03/11/2025" [cite MED0001].`);
  - bold, highlighted marks after exactly the four bad paragraphs: `9/10` (number not on MED0003), a quote with the
    wrong date (quote not on MED0001), an uncited quote, and an em dash (style failure);
  - a Fact check section `Checks: 24 of 28; failures: 4; uncited: 2; rule hits: 1; skipped: 0`.

  The good number `4/10` and the `[DATE D+101]` quote on DEF0001 passed. No final `.docx` was written. This matches the
  claim.
- brief-in with an invented placeholder `[DATE D+99]` printed `blocked at step 5 (placeholder, offset 278); nothing was
  written` and exited 2. A real surname draft printed `blocked at step 1 (claimant, offset 0)` and exited 2. Neither
  message contains a value.
- **Fact identity upgrade**: I forged a round 6 style case file by turning DEF0002's straight-leg fact into a cite plus
  a reading on the MED0002 fact (`$TMPDIR/verify7/forge.py`).
  - Before the upgrade, `status` printed `facts=37 ... split_needed=1`.
  - The next `memo` appended `{"kind":"split","payload":{"fact":"F5","to":"F53","page_id":"defense-report/002","cite":"DEF0002","date":"06/20/2025",...}}`.
    The split was appended before the model call. That memo then exited 2 on my scratch config's host, which is my
    setup, not the code.
  - After the upgrade, `status` printed `facts=38 ... split_needed=0 outputs=memo:stale,brief-out:stale`.
- **Binder roles** (`roles.role` probe):
  - defense: DME, dme-2, D.M.E., IME_report, ime2, IME 3, ime.2, defense medical, Independent-Medical;
  - ROLE NEEDED: Imelda Health, imex, DMEs;
  - ours: crime-scene, medical, Dimes, primes.

  This matches D66.

## Seeds (each applied by `seed.py`, checked not identical, full suite `-x`, restored, `cmp` identical)

| # | File:line (seeded by a builder?) | Defect | Result |
|---|---|---|---|
| V1 | `brief_in.py` publish (no) | `failed_steps=()` always: a failing draft publishes as final | RED `test_brief.py::test_fix2_uncited_partial` |
| V2 | `matterinfo.py` ask_roles (no) | answers not written to `[roles]` | RED `test_matterinfo.py::test_matterinfo` |
| V3 | `status.py` snapshot (no) | `split_needed=0` | RED `test_facts.py::test_casefile` |
| V4 | `facts.py` split replay (no; only identity() was) | moved cite not removed from the source fact | RED `test_facts.py::test_casefile` |
| V5 | `anon.py` restore (no) | `[SRC-n]` second pass dropped | RED `test_anon.py::test_text_32` |
| V6 | `cli.py` brief-out dispatch (no) | `pages_all=False` | RED `test_cli.py::test_brief_dispatch` |
| V7 | `brief.py` conflict_excerpts priority (no) | defense and ours pairs sorted last | RED `test_brief.py::test_package_contract[4]` |
| V8 | `outputs.py` start (no) | roles never asked on a tty | RED `test_outputs.py::test_roles_through_start` |
| V9 | `anon_job.py` anonymize tie rule (no) | `<=` to `<`: a tie supplies the anchor | RED `test_anon_job.py::test_ambiguous_surname_and_anchor_tie` |
| S1 | `cli.py` hearing flags (round 6 gap) | doctor and closing swapped | RED `test_cli.py::test_hearing_flags` |
| S3 | `schemas/questions.schema.json` (round 6 gap) | `quote` dropped from required | RED `test_schema.py::test_schema_evidence` |
| S4 | `cards/02-depo/c-our-doctor.md` (round 6 gap) | two-question rule reversed | RED on the version pin, and alone `test_cards.py::test_card_practice` RED |

After all seeds: `git status --short` shows only the pre-existing untracked `.agents/`, `.claude/worktrees/` and
`AGENTS.md`.

## Findings (open; not blocking)

1. **Medium, privacy. `Aged 44` survives.**
   - `anon.AGE` matches `age 44`, `44 year old` and `44 y/o`, but not `aged 44`.
   - Probe (`$TMPDIR/verify7/probe_anon.py`): `'Aged 44 at the time.' -> 'Aged 44 at the time.'`, and `check_code`
     returned `ok=True`.
   - Q63 lists three forms, so the build matches the ruling's letter. It does not match its intent.
2. **Medium, re-identification. Two different stated ages restore in prose to the first.**
   - `anon._canonical('[AGE]')` returns `key.ages[0]`.
   - Probe: `A 44 year old man. Later, a 45 year old man.` -> `A [AGE] man. Later, a [AGE] man.` -> restore -> `A 44
     year old man. Later, a 44 year old man.`
   - In brief-in, prose numbers are counted with placeholders removed, so a wrong age in the restored brief is never
     marked. This is an unlogged design call: D63 says restore is canonical for prose, but `[AGE]` has no canonical value
     when the key holds two ages.
3. **Medium, privacy. The `11th of March 2025` form keeps the day.** It becomes `the 11th of [MONTH M+0]` and the check
   passes. With M+0 on the accident month, this reveals the accident's day of month. The code review's ordinal-date item
   covered `March 11th, 2025` but not this form.
4. **Low. `M. Ashby-Vale` becomes `M. [CLAIMANT]`.** The given-name initial stays outside the placeholder.
5. **Low. brief-out on a non-tty prints no `ROLE NEEDED` line.** It uses roles only to order conflicts. Depo, hearing,
   report and memo put ROLE NEEDED in their documents. D66 says a non-interactive run prints ROLE NEEDED.

## Unlogged design calls

- `[AGE]` prose restore takes the first age seen (finding 2).
- A job that fails after the upgrade still leaves its `split` events. This fits D65 ("before any other write"), but no
  ruling says so.
- brief-out does not surface ROLE NEEDED (finding 5).

## Reconciliation with the builder, critic and review records (read after ticking)

- Stage 5 `casefile_lines` 56 to 55 is in `round07-W1-report.md`. The ledger `## Project` baselines (786 passed,
  `casefile_lines=56`) have not been moved to the round 7 values (937 passed, 55). That is the chair's job at the merge.
- The output critic's H1, H2, M1 to M4 and L1 to L6 are each reflected in what I measured:
  - numbers are checked in cited paragraphs;
  - an uncited quote fails;
  - the default package.json pages match package.md (9 pages);
  - the firm rules and the unread page are in the package;
  - the em dash is marked;
  - `[AGE]` is in place.

  The critic's privacy grep was clean, which agrees with my `leak_total=0`.
- Code review M2 (dates) fixed `3/11/25`, `March 11th, 2025` and `11 March 2025`. My probe got `2/17/81` -> `[DOB]` and
  `2025-03-14` -> `[DATE D+3]`. The `11th of March` form is new (finding 3).
- Code review raised that the upgrade can split two pages of one visit. I did not re-measure this. On the fixture the
  split is exactly the one pair the chair measured.
- No record raises findings 1, 2 or 5.

## Process notes

- `scripts/run.sh` merges stderr into stdout, so brief-in and brief-out block messages show on stdout. The exit test
  allows for this.
- My first own draft used an invented `[DATE D+99]`, and brief-in correctly blocked it at step 5. I replaced that
  paragraph with a real offset to reach the fact check.
- Under zsh, `PIPESTATUS` is empty. I took the bench exit codes from separate runs.
