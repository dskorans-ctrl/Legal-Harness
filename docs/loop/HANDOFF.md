# casefile: loop handoff (2026-10-27, round 2 HELD at the fix-cycle cap)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Clarified` Q1 to Q31, `## Round 2`), then
`Librarian.md` (builder pre-flight and open items). Spec (canon): `docs/spec.md`.

## Where things stand
- Round 2 (spec §7 stage 2, Gemma trial per Q28) is built and verified except one narrow finding, V2b-F1:
  a 302 or 307 model reply stores no answer row (`src/casefile/model.py:18`, `:50`, `:54` raise
  `ModelError` without `raw`). Three fix cycles are spent (Q5), so the chair held the round: NOT merged,
  `loop/round-03` NOT opened, no re-brief. `main` is still b167fbd (round 1).
- Measured on `loop/round-02`: `269 passed`, gate `0`, stage 2 exit test green, flawed bench line exit 1,
  ideal exit 0 (exact lines in `docs/loop/round-02/round02-report.md`).
- Report with the Gemma against Sonnet cost comparison (Q29): `docs/loop/round-02/round02-report.md`.

## Next session: finish round 2 on the owner's answer to question 30
- (a) recommended: one extra fix cycle limited to V2b-F1 (body as `raw` at the three raises, a 302 test,
  seed each raise red), one focused blind re-verify, then close.
- (b) rule that a refused redirect is not a received reply (amend D25 and OR-8), then close.
- (c) discard and re-brief per Q5.
- Close still to do: Librarian round 2 entries (app-loop prompts §5), spec §11 as-built row for stage 2,
  ledger `## Project` baselines (R2-4), tick R2-5, fast-forward `main`, open `loop/round-03`, rewrite this
  page, write `next-round.md` for round 3, prompt the owner to `git push origin main`.
- Coder for any fix: Gemma (Q28 covers round 2) unless the owner says otherwise; round 3 returns to the
  default tiers (Q30: Fable brief, Codex reviews, Opus orchestrator, critic and verifier, Sonnet code).

## Held owner questions
- `docs/loop/questions-for-owner.md`: question 30 (the hold), 21 to 29 (round 2: key contents, Studio
  bench folder, Bates placement, key completeness, flag wording, unreachable model exit, model name on
  the line, bills, "the report" wording), Q7 and items 8 to 20 from round 1.
- Overnight rulings OR-1 to OR-9 (Q31) and spec §9 D25, D26: pending ratification or veto.

## Machine rules
- Every run goes through `scripts/run.sh`; pass `--config config.example.toml` to `casefile` on this Mac.
- Gemma driver: `scripts/gemma_task.py` (protocol `docs/loop/round-02/gemma-builder-protocol.md`); give
  each call a 600 s foreground timeout; Gemma free = no POST in `~/local-worker/ollama-serve.log` for
  15 minutes (OR-1).
- Codex reviews only (`codex exec -m gpt-6.1-sol -s read-only ... < /dev/null`), sandbox off, background.
- Run the gate before every chair commit (Mistakes Log). Verify a seed applied (`cmp -s`) before counting it.
- Leftovers: worktree `.claude/worktrees/agent-a582821e2b2e41b16` and branch `control/r2-sonnet` (the
  Sonnet cost control, never merged; delete with the owner's say-so). Old `casefile-run.*` folders in
  the shared TMPDIR need the owner's permission to delete.

## Cost rules (owner)
One orchestrator alive at a time. Builders report once, with no polling. Logs go to files, with short
summaries. A fresh session per round; this page is the entry point.
