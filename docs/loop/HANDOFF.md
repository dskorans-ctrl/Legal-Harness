# casefile: loop handoff (2026-10-28, rounds 4 and 5 closed in one session at the owner's word, Q48)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Clarified` Q1 to Q48, `## Round 5`), then `Librarian.md`
(builder pre-flight and open items). Spec (canon): `docs/spec.md`.

## Where things stand
- Stages 1 to 5 are built, verified and merged to local `main`. `main` is NOT pushed: the owner runs
  `git push origin main`.
- Round 4 (model client and gates): PASS after two fix cycles, `docs/loop/round-04/round04-report.md`.
- Round 5 (case file, merge, medical memo): PASS after two fix cycles, `docs/loop/round-05/round05-report.md`.
- `loop/round-06` is open at the round 5 close with no work. Round 6 is spec §7 stage 6: outputs (deposition, hearing,
  report analysis), cards built from the playbook, and the `cards/` and `schemas/` rewrite.
- Baselines (ledger `## Project`): `652 passed`, `suite_time runs=3 max=51.57 verdict=PASS`, gate `0`,
  `unused_imports=0`, bench lines unchanged, stage 1 to 5 exit lines (stage 5: `stage5 exit=0 runs=4 of 4 memos=3 of 3
  answers=+4 casefile_lines=48 chain_ok=1 server_stopped=1`).

## Owner check-in first (nothing below is ruled by the owner yet)
- Pending veto: spec §9 D31 to D43 (D41 amended at the round 5 close) and the chair's build rulings in the ledger's
  round 4 and round 5 sections.
- Held questions, `docs/loop/questions-for-owner.md`: 47 to 58, each with a fail-closed interim. Lead with 56: conflicts
  between pages read in different runs, or sent in different chunks of one run, are not checked (measured: 4 of 9
  known conflicts and gaps lost when the invented matter is split into three chunks); the memo says so. Q41 ranks
  defense-against-our-records conflicts first, so this interim is the weakest one held.
- Owner input logged for stage 7: the anonymization convention casefile-anon/1 (ledger Q47).

## Tiers (owner Q46)
Opus 5.5 orchestrates; Codex `gpt-6.1-sol` codes and fixes (`codex exec`); fresh Fable agents do the plan review and
the code review (read-only); Fable writes and revises the brief; Opus runs the output critic and the blind verifier.

## Carried into round 6
Round 5 verifier L1 (the no-reply reason says the page stays open even in the doctor; memo repeats the no-reply
words); code review M4 (an edited last case-file line loads clean: recorded limit) and L3 (two stamp definitions);
tuning T-16 to T-22.

## Machine rules
- Every run goes through `scripts/run.sh`; pass `--config config.example.toml` to `casefile bench` on this Mac. For
  `casefile memo`, `status` or `doctor`, write a temp config whose model host is the stand-in's own port:
  `config.example.toml` points at `127.0.0.1:11434`, where the owner's local-worker Ollama listens.
- Tests default to `http://127.0.0.1:9`; no test may reach 11434. The chair's audit: count `^[GIN]` lines in
  `~/local-worker/ollama-serve.log` before and after a full gate run (request lines only; never read prompts there).
- Codex builders: `codex exec -C <tree> -m gpt-6.1-sol -s workspace-write -c sandbox_workspace_write.network_access=true
  ... < /dev/null`, sandbox off, background. Builders do not commit; the chair re-runs CHECKs, seeds, gates, commits.
- A lane B worktree needs its own toolchain: `T=$HOME/.casefile-dev/<worktree-name>`, then `UV_PYTHON_INSTALL_DIR=$T/python
  UV_CACHE_DIR=$T/cache UV_PROJECT_ENVIRONMENT=$T/venv uv sync` with the sandbox off (the same three variables for `uv add`
  in the main checkout, with `T=$HOME/.casefile-dev/legal-harness`).
- Privacy: `~/local-worker/log.jsonl` and `~/local-worker/allowed/` hold real client material. No loop agent reads them.
- Inside the sandbox, Tesseract needs resolved paths (`$(cd $TMPDIR && pwd -P)`). macOS has no `timeout` command.
- Run the gate before every chair commit (Mistakes Log). Verify a seed applied (`cmp -s`) before counting it.
- Leftovers needing the owner's say-so to delete: worktrees `.claude/worktrees/agent-a582821e2b2e41b16`, `r3-lane-b`,
  `r4-lane-b`, `r5-lane-b` (branches `r3/lane-b`, `r4/lane-b`, `r5/lane-b`, all merged); branch `control/r2-sonnet`; the
  untracked `tests/fixtures/matters/9001.001/.claude/` (a Claude Code marker); untracked `.agents/` and `AGENTS.md`; old
  `casefile-run.*` folders in the shared TMPDIR.

## Cost rules (owner)
One orchestrator alive at a time. Builders report once, with no polling. Logs go to files, with short
summaries. A fresh session per round; this page is the entry point.
