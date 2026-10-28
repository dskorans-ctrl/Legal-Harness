# casefile: loop handoff (2026-10-28, round 4 closed; round 5 opened in the same session by owner Q48)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Clarified` Q1 to Q48, `## Round 5` if present), then
`Librarian.md` (builder pre-flight and open items). Spec (canon): `docs/spec.md`.

## Where things stand
- Stages 1 to 4 are built, verified and merged to local `main` (round 4 close). `main` is NOT pushed: the owner runs
  `git push origin main`.
- Round 4: verifier PASS after two fix cycles; report `docs/loop/round-04/round04-report.md`.
- Round 5 (spec §7 stage 5: case file, merge, medical memo) is on `loop/round-05`. Its state is in the ledger's
  `## Round 5` section; if this page was not updated after it, round 5 has not passed its plan review yet.
- Baselines (ledger `## Project`): `537 passed`, `suite_time runs=3 max=57.46 verdict=PASS`, gate `0`,
  `unused_imports=0`, bench lines unchanged, stage 1 to 4 exit lines (stage 4: `stage4 exit=0 gates=6 of 6 cases=14
  of 14 runs=+14 answers=+21 empty_saved=0 server_stopped=1`).

## Tiers
- From round 5 (owner Q46): Opus 5.5 orchestrates; Codex `gpt-6.1-sol` codes and fixes (`codex exec`); Fable reviews
  the plan and the code (each a fresh Fable agent, read-only); Fable writes the brief; Opus runs the output critic
  and the blind verifier.

## Held owner questions (`docs/loop/questions-for-owner.md`)
- 47 what closes an uncited page (interim: nothing; it stays open); 48 label a fact's summary as the model's reading
  or judge it with a second call (interim: no output treats a summary as verified); 49 rule ids in outputs
  (interim: shown next to the rule's message). Plus any round 5 questions, numbered from 50.
- Pending veto: spec §9 D31 to D38 and the round 4 chair rulings (ledger `## Round 4`).
- Owner input for stage 7: the anonymization convention casefile-anon/1 (ledger Q47).

## Carried into round 5
- Verifier L1 (no mixed stamped and unstamped chunk test), L2 (D38 digit check reads a bracketed cite: rule with R1-20
  before cited prose, T-19), critic M2 (open items shown by stamp) and L3 (bench invented kinds), R1-20 (R4-5).

## Machine rules
- Every run goes through `scripts/run.sh`; pass `--config config.example.toml` to `casefile` on this Mac.
- Codex builders: `codex exec -C <tree> -m gpt-6.1-sol -s workspace-write -c sandbox_workspace_write.network_access=true
  ... < /dev/null`, sandbox off, background. Without the network flag the loopback socket tests fail (gate prints 1).
  Builders do not commit; the chair re-runs CHECKs, seeds, gates and commits.
- A lane B worktree needs its own toolchain: `T=$HOME/.casefile-dev/<worktree-name>`, then `UV_PYTHON_INSTALL_DIR=$T/python
  UV_CACHE_DIR=$T/cache UV_PROJECT_ENVIRONMENT=$T/venv uv sync` with the sandbox off.
- An `ollama` (the owner's local worker) listens on 127.0.0.1:11434 here. Agents never send matter text to it; run
  the doctor in process against the stand-in.
- Privacy: `~/local-worker/log.jsonl` and `~/local-worker/allowed/` hold real client material. No loop agent reads
  them. Copy invented fixtures only into `allowed/` for local-worker calls, and remove them after.
- Inside the sandbox, Tesseract needs resolved paths (`$(cd $TMPDIR && pwd -P)`). macOS has no `timeout` command.
- Run the gate before every chair commit (Mistakes Log). Verify a seed applied (`cmp -s`) before counting it.
- Leftovers needing the owner's say-so to delete: worktrees `.claude/worktrees/agent-a582821e2b2e41b16`,
  `r3-lane-b` (branch `r3/lane-b`), `r4-lane-b` (branch `r4/lane-b`, merged); branch `control/r2-sonnet`; old
  `casefile-run.*` folders in the shared TMPDIR.

## Cost rules (owner)
One orchestrator alive at a time. Builders report once, with no polling. Logs go to files, with short
summaries. A fresh session per round; this page is the entry point.
