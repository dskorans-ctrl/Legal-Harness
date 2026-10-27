# casefile: loop handoff (2026-10-27, round 4 session 1 stopped by the owner after the brief)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Clarified` Q1 to Q44, `## Round 4`), then `Librarian.md`
(builder pre-flight and open items). Spec (canon): `docs/spec.md`.

## Where things stand
- Stages 1 to 3 are built, verified and merged to `main` (tip 204f6fd, the round 3 close). Round 4 is open on
  `loop/round-04` with no code yet.
- Round 4 done so far: check-in (question 7 answered, Q43: login-user Ollama app); Fable brief written
  (`docs/loop/round-04/round04-build-brief.md`, tracked copy of `.workflow/scratch/round04-build-brief.md`, 628 lines,
  decisions 1.1 to 1.12, rows D31 to D37 pending); brief questions 42 to 46 answered (Q44, every interim kept).
- Not done: the Codex plan review was stopped by the owner before it reported. No decision of the brief is ruled yet.
- Baselines (ledger `## Project`): `358 passed` (under 90 s; brief §0 measured 95.33 s today, T-11), gate `0`,
  `unused_imports=0`, flawed bench exit 1 `... flags=8 of 9 ...`, ideal exit 0 `... flags=9 of 9 ...`, stage 1 `exit=0
  ... fails=set()`, stage 2 `stage2 exit=0 ...`, stage 3 `stage3 exit=1 pages=6 ids_ok=6 of 6 ... min_ratio=1.000`.
- OCR tools on this Mac (Q39): ocrmypdf 17.13.0 and tesseract 5.5.3 in `/opt/homebrew/bin`; run.sh adds it.

## Next session: resume round 4 on `loop/round-04` at step 4 (Codex plan review)
- Copy the tracked brief back to `.workflow/scratch/round04-build-brief.md` if the scratch copy is gone.
- Then: Codex plan review (§6) -> Fable revision (§7) -> chair rulings on D31 to D37 (pending veto) -> build (Opus
  orchestrates, Sonnet 5.5 codes; lane A in the checkout, lane B in worktree `r4-lane-b`) -> critic round (Codex,
  output critic, blind verifier) -> fix cycles (cap three) -> close. Agent log rows continue from round 4 #3.
- Brief §0 drift to weigh when ruling: the suite is over T-11 today; decision 1.1 rests on Ollama source claims (a
  `truncate` request field, `prompt_eval_cached_count`) that cannot be checked on this Mac (no Ollama, Q11).

## Held owner questions
- None held. Question 7 answered (Q43); round 4 brief questions 42 to 46 answered (Q44).
- New requirement for a later stage (Q41, spec §10): anonymized excerpts around each conflict for Claude review.

## Machine rules
- Every run goes through `scripts/run.sh`; pass `--config config.example.toml` to `casefile` on this Mac.
- Inside the sandbox, Tesseract needs resolved paths (`$(cd $TMPDIR && pwd -P)`), never `/tmp/claude-501/...`.
- Codex reviews only (`codex exec -m gpt-6.1-sol -s read-only ... < /dev/null`), sandbox off, background. The
  sandbox cannot see that process: wait on it with the sandbox off too.
- `uv add` and `uv sync` need the sandbox off (cache outside the write allowlist).
- Run the gate before every chair commit (Mistakes Log). Verify a seed applied (`cmp -s`) before counting it.
- Leftovers needing the owner's say-so to delete: worktrees `.claude/worktrees/agent-a582821e2b2e41b16` and
  `.claude/worktrees/r3-lane-b` (branch `r3/lane-b`, merged), branch `control/r2-sonnet`; old
  `casefile-run.*` folders in the shared TMPDIR.

## Cost rules (owner)
One orchestrator alive at a time. Builders report once, with no polling. Logs go to files, with short
summaries. A fresh session per round; this page is the entry point.
