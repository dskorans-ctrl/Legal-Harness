# casefile: loop handoff (2026-10-27, round 3 closed and merged)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Clarified` Q1 to Q41), then `Librarian.md`
(builder pre-flight and open items). Spec (canon): `docs/spec.md`.

## Where things stand
- Stages 1 to 3 are built, verified and merged to `main`. Round 3 (stage 3, intake and OCR with page IDs)
  passed the blind verifier after two fix cycles: `docs/loop/round-03/round03-report.md`.
- Baselines (ledger `## Project`): `358 passed` (under 90 s), gate `0`, `unused_imports=0`, flawed bench exit 1
  `... flags=8 of 9 ...`, ideal exit 0 `... flags=9 of 9 ...` (both `model=candidate`), stage 1 `exit=0 ...
  fails=set()`, stage 2 `stage2 exit=0 ...`, stage 3 `stage3 exit=1 pages=6 ids_ok=6 of 6 ... min_ratio=1.000`.
- OCR tools on this Mac (Q39): ocrmypdf 17.13.0 and tesseract 5.5.3 in `/opt/homebrew/bin`; run.sh adds it.

## Next session: round 4 on `loop/round-04` (spec §7 stage 4)
- Stage 4: model client and gates. Exit test: every gate (spec §4) tested with good and bad answers,
  including truncated ones.
- Tiers: Q30 defaults (Fable brief and revision, Codex plan and code review, Opus orchestrator, critic and
  verifier, Sonnet 5.5 code).
- Carry into the round 4 brief: R2-CX-2 (prompt truncation not detectable; Ollama does not count cached
  prompt tokens, OR-4); verifier test gaps S1 (stage 3 exit test does not assert record `matter` and
  `page`), S2 (no sidecar `7 of 6` case), S5 (`make_scanned.py --check` text-layer change untested); verifier
  lows (bench finds a duplicate matter number only after the first matter ran; `normalize` strips only spaces
  and hyphens; leftover step comments in `bench.py` and `benchcandidate.py`); suite time near the 90 s
  budget (T-11). R1-20 waits for the stage that writes cited prose.

## Held owner questions
- Answered at the round 3 close (ledger Q42): 38 to 41 settled; D27 to D30, the whole-token stamp rule and
  G9 ratified. Still open: question 7 (Ollama user or daemon, Q19). Nothing else is held.
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
