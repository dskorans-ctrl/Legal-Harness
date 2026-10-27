# casefile: loop handoff (2026-10-26, end of round 1)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Clarified` Q1 to Q27), then `Librarian.md`
(builder pre-flight and open items). Spec (canon): `docs/spec.md`.

## Where things stand
- Round 1 (spec §7 stage 1 plus the harness) PASSED after the re-brief (Q24, Q26) and is merged:
  `main` was fast-forwarded to the round 1 close. Branch `loop/round-02` is open from it, with no work yet.
- Measured on `main`: `233 passed`, gate `0`, stage 1 exit test `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`.
- Round report: `docs/loop/round-01/round01-report.md`. Spec §11 has the stage 1 as-built row.

## Next session: round 2 (spec §7 stage 2: benchmark and invented test matter)
1. Ask the owner the tiers (Q27 is the last answer: Fable brief, Codex plan and code review, Opus
   orchestrator, critic and verifier, Sonnet code).
2. Full round per the app-loop skill: brief, plan review, revision, build, critic round (8a, 8b, 8c),
   fix cycles (cap three), close. Exit test: `casefile bench` scores the invented test matter against its
   answer key. Set the regression baselines (ledger `## Project`).
3. First items carried from round 1: VF-1 (a test for the newline join at pathguard.py:55), VF-2
   (config.py:67 and :145 tracebacks become ConfigError), R1-20 if stage 2 writes cited text.

## Held owner questions
- `docs/loop/questions-for-owner.md`: Q7, and items 8 to 20 (critic practice questions, spec §8b decision
  numbering, python3 on the Studio, the held-pipe kill, a TMPDIR inside the checkout, a matters folder
  that contains the checkout, Ctrl-Z). All have interim rulings in force.
- Pending veto: spec §9 D12 to D24 (chair rulings, including the 2026-10-26 amendments and D24).

## Machine rules
- Every run goes through `scripts/run.sh`. It runs `src/casefile/pathguard.py` with the first `python3` on
  PATH (3.9 or newer), then `scripts/run_capture.py`. The toolchain lives at
  `~/.casefile-dev/legal-harness` (D23).
- Codex reviews only (`codex exec -m gpt-6.1-sol -s read-only ... < /dev/null`), with the sandbox off, in
  the background. Sonnet builders commit their own work. The chair re-runs every CHECK and seed before
  accepting.
- Socket tests run inside this sandbox (Q18). Agents must not leave processes running, and must not turn
  the sandbox off to clean up (two did this round).
- The shared TMPDIR holds old `casefile-run.*` folders from killed test runs (invented text). Deleting
  them needs the owner's permission.
- The suite takes about 45 s (T-6).

## Cost rules (owner)
- One orchestrator alive at a time. Builders report once, with no polling. Logs go to files, with short
  summaries and small tool outputs. A fresh session per round; this page is the entry point.
