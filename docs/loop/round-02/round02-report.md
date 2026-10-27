# Round 2 report: stage 2, benchmark and invented test matter (Gemma trial, Q28)

**Verdict: PASS, merged to `main` (2026-10-27).** The round was held at the fix-cycle cap on V2b-F1 (a 302 or
307 model reply stored no answer row). The owner chose one extra fix cycle limited to that finding (Q32,
question 30 (a)); Sonnet wrote it because the owner's other Gemma job was running (Q33, a deviation from
Q28). Fix 695b97b: the body is stored on all three redirect refusals; the new test is red on the old code
and under each of three seeds. Verifier 3 (fresh, blind) PASS: `probe_v3 bad=0 runs=13 answers=13
target_hits=0` (301, 302, 303, 307, 308 and an empty body through the real opener; redirects still
refused). The owner ratified OR-1 to OR-9, D25 and D26.

Branch `loop/round-02` fast-forwarded into `main`; `loop/round-03` opened from it.

## Measured on the tip (chair re-runs, inside the session sandbox)
- `scripts/run.sh pytest -q` -> `270 passed in 36.99s` after the extra cycle (269 before it; round 1: 233).
- `scripts/run.sh python -m casefile.gate` -> `0` (`gate prose PASS dashes=0 files=136`).
- Stage 1 exit test unchanged: `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`.
- Stage 2 exit test: `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1` and the perfect line.
- `casefile bench --config config.example.toml --matters tests/fixtures/matters --candidate
  tests/fixtures/bench/flawed.json` -> exit 1:
  `bench 9001.001 found=26 of 29 missed=3 invented=2 extra=2 flags=5 of 6 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14`
  then six detail lines (missed F04 F15 F24; two invented; flags_missed G3; one extra flag; rule no-dme-ime).
- Same with `tests/fixtures/matters/9001.001/ideal.json` -> exit 0: `found=29 of 29 missed=0 invented=0 extra=2 flags=6 of 6 ... pages_failed=0 of 14`.
- Proposed regression baselines (R2-4, set at merge): the two bench lines above, `269 passed`, gate `0`.

## What was built (all code, tests and fixture data written by gemma4:e4b-it-qat)
VF-1 and VF-2 carried from round 1; quote normalisation and the matter loader; the invented matter
9001.001 (14 pages, three binders, invented people); the answer key (29 facts, 6 flags) validated against
the pages; candidate parser and scorer; `ModelError.raw` and the stage 2 runner with its gates; the
stand-in's bench recording; `casefile bench` (exit 0 perfect, 1 imperfect, 2 cannot run); the stage 2
exit test; the prose gate over fixture text. Spec §9 D25 and D26 (pending veto).

## Critic round
- 8a Codex: 7 findings, all reproduced or traced. Three were in the chair's driver (proxy, symlink, FILE
  answer on a function task), fixed by the chair; four went to fix cycle 1; R2-CX-2 (prompt truncation
  not detectable) deferred to stage 4 (OR-4).
- Extra Fable review (Q28): Gemma 7/8/7/5 vs the Sonnet control 7/9/7/9 (correctness, brief fidelity, test
  strength, readability). Same program, same two bugs; Gemma's gap is hygiene: dropped `from exc`, 33
  trailing-whitespace lines, unused imports, prompt text leaked into comments.
- 8b output critic: `OUTPUT CRITIC 6/10 · high 2 · med 5 · low 6`. H1, H2 (an incomplete key that would fail
  a correct model) verified on the pages and fixed in cycle 2; M1 fixed (detail lines); the rest are owner
  questions 24 to 29.
- 8c verifier 1: FAIL on V2-F1 (non-200 replies unstored); 8 fresh seeds, 5 green test gaps. Fixed in cycle 3.
- 8c verifier 2: FAIL on V2b-F1 (3xx replies unstored); 20 reply cases probed, 19 correct; 6 fresh seeds,
  4 green test gaps where the code is right (non-blocking).
- Extra fix cycle (Q32) and verifier 3: PASS; 8 seeds, 7 red; S5 (truthiness test of `raw` in benchrun.py:69)
  green because the test has no empty-body 3xx case; code right by probe (carried).

## Cost: Gemma build against a Sonnet build (owner Q29)
| | Gemma route (measured) | Sonnet route |
|---|---|---|
| Code, tests, fixtures, three fix cycles | Opus orchestration 877 k (build 474 k, fixes 130 k, 142 k, 130 k) | about 400 k to 550 k Sonnet (estimate below) |
| Local model | Gemma 197 k prompt + 202 k answer tokens, 120 min of model time, no usage cost | none |
| Sonnet takeovers | 0 of 72 tasks | n/a |
| Wall clock for build plus fixes | about 3 h 15 min | about 30 to 45 min |

How the Sonnet figure is built: the measured control (Sonnet rebuilt W3, the W5 code, W6 and W9 from the
same brief in a throwaway worktree, never merged) took 125 k tokens and 6 minutes for 939 lines of code
and tests; Gemma's version of the same items is 1,216 lines. Scaled to the round: all build code about
170 k, fixture prose and data about 100 k (an upper guess, not measured), three fix cycles about 255 k at
round 1's Sonnet fix-cycle rate (95 k, 80 k). Shared costs that both routes pay are left out of both
columns: Fable brief and revision (434 k), Codex reviews, critic (96 k), verifiers (147 k, 103 k), the
chair. The extra Fable review (184 k) and the control (125 k) were costs of the trial itself.

Reading: by token count the Gemma route used about 1.6 to 2.2 times the cloud tokens of a Sonnet build,
all of them Opus tokens, which cost more per token than Sonnet's; it also took about five times the wall
clock. The local model's work is free, but driving it is not: the orchestrator writes each task in full,
reads each answer, and writes the feedback. How much Gemma wrote itself, measured as answer lines found
word for word in the orchestrator's task text: build code 35 percent, fixtures 8 percent, fix cycles 24, 20
and 78 percent. So Gemma truly wrote most of the build and nearly all the fixtures; fix cycle 3 was mostly
copying.

Quality: equal correctness to Sonnet on the same items (both builds had the same two bugs, from the brief),
lower readability. 26 of 43 build tasks passed first try, 2 needed a re-split, none needed Sonnet. The
driver's fail-closed checks caught 5 bad answers (truncated, wrong format, a whole file on a function
task) before anything was written.

## Design calls
D25, D26 and OR-1 to OR-9: ratified by the owner 2026-10-27 (Q32). Owner questions 21 to 29 remain held.

## Carried to round 3 (with the default tiers, Q30)
The empty-body 3xx test case (verifier 3, S5); OR-5's cosmetic and design lows (whitespace, unused imports,
`.DS_Store` refusing a matter, F4 to F6); a non-200 HTTPError with no body stream (fix 3 report);
duplicate matter numbers not refused (OR-8); verifier test gaps N2 to N5 and the brief's anchored greps;
R2-CX-2 to stage 4; R1-20 still open; owner questions 24 to 29.

## Process notes
- The chair committed a copied review with em dashes without running the gate (Mistakes Log); the gate
  now runs before every chair commit.
- One chair seed did not apply (a positional argument) and was caught by `cmp -s` before it counted.
- An orchestrator's driver call ran past the tool's 120 s default and was moved to the background; later
  calls used a 600 s foreground timeout.
- The owner paused the build once (Gemma busy with another job) and the loop resumed at 23:31 by a
  30-minute log check (OR-1).
