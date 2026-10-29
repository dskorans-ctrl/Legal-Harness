# Round 7 report: stage 7, the anonymizer and the brief package

**Verdict: PASS** (blind verifier, `docs/loop/round-07/round07-verify.md`, tip 68f57fa, 12 fresh seeds, all red), then fix
cycle 3 (the cap) closed the verifier's five open findings at b7e4184 with every baseline unchanged.
Output critic: `OUTPUT CRITIC 6/10 · high 2 · med 4 · low 6` (`round07-critic.md`); all 12 findings fixed in fix cycle 2
(L1 partly, recorded). Spec §7 stage 7 exit: the identifier check passes on the test matter; re-import fact-checks a draft.

Owner present for the whole round (check-in Q61 before the brief; Q62 answered questions 88 to 95 during the plan review;
Q63 answered the critic's age question). No real client data entered the repo or any agent: the architect read
`~/local-worker/anonymize.py` for logic only and ported no literal from it; every builder, critic and verifier prompt
forbade `~/local-worker/`, uploads, `Cases/` and `Bench/`; every fixture is written from the invented matter 9001.001.

## Measured on the tip (chair re-runs, every run through `scripts/run.sh`)

| Claim | Number | Check |
|---|---|---|
| Stage 7 exit | `stage7 exit=0 packages=2 of 2 blocked_seeded=1 of 1 drafts=2 of 2 answers=+8 identifiers_in_package=0 server_stopped=1` | `pytest -q -s tests/test_stage7_exit.py` |
| Package | `stage7 package matter=9001.001 pages=14 pages_in_package=14 entities=17 of 17 anchor=D+0 people=46 employer=8 ids=3 dob=14 dates=61 years=2 kept_orgs=6 leaks=0 review=24 key_mode=600 facts=38 conflicts=5 exit=0` | same |
| Drafts | `checks=44 of 44 ... exit=0`; bad quote `checks=43 of 44 failed=1 marked=1 partial=1 exit=1` | same |
| Suite | `993 passed`; `suite_time runs=3 max=84.61 verdict=PASS` | `pytest -q`; `scripts/suite_time.sh 3` |
| Gate, imports | `0`; `unused_imports=0` | `python -m casefile.gate`; `scripts/unused_imports.py` |
| Bench, flawed (exit 1) and ideal (exit 0) | byte-identical to the round 6 baselines | `casefile bench --candidate ...` |
| Stage 5, 6 | `stage5 exit=0 ... casefile_lines=55 ...` (56 to 55, deliberate, D65); `stage6 exit=0 docs=6 of 6 answers=+16 rule_hits=0 server_stopped=1` | exit tests |
| Leak probes (chair) | 9 of 9 raw identifier forms block the check; the code review's and the verifier's leaking forms are replaced | `$TMPDIR/repro7*.py` against `anon.text` and `anon.check_code` |
| Verifier oracle | 78 `[anon]` values and variants over both packages: `leak_total=0`; control over raw records `60` | verifier's own grep |

## What was built
Fact identity as folded quote, date and provider with an append-only `split` event (critic 2 M1 closed; the key's one
colliding pair, the straight leg raise at MED0002 and DEF0002, now two facts); binder roles whole word or asked, ROLE
NEEDED on a non-tty run; the `[anon]` name list in `matter.toml` with aliases; `anon.py` and `anon_job.py` under
casefile-anon/1 (model finds names and the anchor only, code replaces, checks and restores; key at
`<matter>/anon/key.json` mode 600); `casefile brief-out` (package.md, package.json, check.txt; firm rules; conflicts with
both full pages; pages not yet read; `--pages all`) and `casefile brief-in` (a Word draft with inline or footnote cites,
restored and fact-checked; any failure gives `.partial.docx`); round 6 test gaps S1, S3, S4 closed; privacy row scoped.

## Owner direction during the round
Q62: examiner's company kept; `[DOB]`; both full conflict pages; review list printed only; matter number and stamps kept;
`--pages all`; brief-in reads Word; an `adjuster` kind kept automatically. Q63: stated ages become `[AGE]`.

## Plan review, rulings, critic round
Plan review (fresh Fable): 3 high, 10 med, 8 low, all accepted; the chair reproduced H1 (tracked key.json would fail the
privacy row), H2 (the run log stores raw answers) and M1, and measured the key (1 collision under the quote, 0 under the
triple). Chair rulings: the run log and `anon/` are inside the matter boundary (brief §1.15); D63 to D67. Build: W1, W1b
(main), lanes A (W2, W3) and B (W4, worktree) in parallel, merge clean, W5. Chair rulings in build: a non-tty name-list
halt prints kind and cite only, never a name; lane B's measured seed count accepted. Code review (fresh Fable): 1 high,
4 med, 8 low; the chair reproduced H1 and M3 as leaks (a bare given name, "Surname, Given", "Logistics, LLC", `3/11/25`,
`March 11th, 2025` passed the check); fix cycle 1 fixed all 13. Output critic: 2 high (numbers in quoted paragraphs and
uncited quotes went unchecked), fix cycle 2 fixed all 12. Blind verifier: PASS with five open findings; fix cycle 3.

## Design calls pending owner veto
D63 to D67 (round 7 brief), D68 (`[AGE-n]` for two or more distinct ages), the chair's build rulings above, and the
fix cycle 1 rulings (name variants, `[anon.aliases]`, ambiguous names block, an independent date detector).

## Carried to round 8
- Recorded limits (Librarian open items): a restored quote keeps its page's date spelling while prose uses the key's;
  the date checker over-blocks "Stages 44 and 45." (fails closed); weekday names stay; a trailing legal suffix after
  `[EMPLOYER]` stays; D67 the stage 8 procedural schema's quote without cite.
- From round 6: owner Q59 items 82 to 86, the format specification and its 15 questions, critic 2 M2 to M6, code review
  L7, fix cycle 2 A2, round 5 M4, verifier notes 3 and 4.
- Stage 7b (cloud round trip, D52 to D62) now has its anonymizer, package and restore check.

## Process notes
- Chair caught a fix builder editing firm practice text (`playbook/hearing.toml`) to satisfy a packaging finding;
  reverted, the cite form moved to drafter rule 8 (#R07-CH-1). Builder prompts now say practice files are the owner's.
- Three of the round's leaks were found only by adversarial probes of forms the fixtures did not hold; the exit test
  counts identifiers independently of the replacer, and fix cycles 1 and 3 gave the check its own detectors.
- The owner answered questions live while agents ran; no answer reached a builder except through the brief or a prompt.

## Cost (agent log)
See `docs/loop/agent-log.md` `## Round 7`.
