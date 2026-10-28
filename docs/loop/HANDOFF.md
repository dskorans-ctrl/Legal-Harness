# casefile: loop handoff (2026-10-28, round 6 closed)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Clarified` Q1 to Q59, `## Round 6`), then `Librarian.md`
(builder pre-flight and open items). Spec (canon): `docs/spec.md`.

## Where things stand
- Stages 1 to 6 are built, verified and merged to local `main`. `main` is NOT pushed: the owner runs `git push origin main`.
- Round 6 (outputs, cards, schemas): PASS after three fix cycles, `docs/loop/round-06/round06-report.md`; output critic
  second grading `7/10 · high 0 · med 6 · low 9`.
- `loop/round-07` is open at the round 6 close with no work.
- Baselines (ledger `## Project`): `786 passed`, gate `0`, `unused_imports=0`, bench flawed `found=26 of 36 ... dates_wrong=1`,
  ideal `found=36 of 36 ... dates_wrong=0`, stage 5 `casefile_lines=56`, stage 6 `stage6 exit=0 docs=6 of 6 answers=+16
  rule_hits=0 server_stopped=1`.

## Direction set by the owner in round 6 (ledger Q52, Q53, Q55, Q57, Q59)
- Nothing runs continually. Loading a document files it into its matter. When the attorney runs a task (deposition prep,
  hearing prep, brief, report), the local model anonymizes the whole matter, casefile sends it to Claude by API key,
  the answer passes the gates, is re-identified and rendered. Approval is the Run click (mode A), with halts on a matter's
  first packet and on any name not on the name list; brief packets are approved per packet. 30 day API retention is
  acceptable. Codex is an optional read-only second review. Design: `docs/loop/design/cloud-roundtrip-proposal.md`, spec
  D52 to D62, roadmap stage 7b (after the stage 7 anonymizer).
- The owner's five example final documents define the output format: `docs/loop/design/output-format-from-examples.md`
  (placeholders only; the originals are real work product and never enter the repo).

## Owner check-in first (round 7)
- Pending veto: spec §9 D44 to D51 (round 6) and D52 to D62 (cloud), and the round 6 chair build rulings in the ledger
  (defense binder widening; IME and unseparated DME as defense, which makes a binder named "Imelda..." defense).
- Decide round 7's scope with the owner. Two candidates, both ready: (a) spec §7 stage 7, the brief package and the
  anonymizer (casefile-anon/1, ledger Q47), which stage 7b needs; (b) the stage 6 carry-overs below. Recommend (a) with
  critic 2 M1 (fact identity) folded in, since 7b depends on the anonymizer and M1 corrupts the chronology.
- Present the format specification's 15 practice questions and the critic 2 findings M2 to M6.

## Carried into round 7
Critic 2 M1 (fact identity is the folded quote; identical findings on two dates merge; D40 amendment) and M2 to M6
(deposition practice); owner Q59 items 82 to 86 (our doctor's deposition is used at the hearing; bill memo is the source
of truth for bills; caption line; our doctor's testimony topics; facts per hearing issue); the format specification;
verifier test gaps S1, S3, S4; recorded limits code review L7, fix cycle 2 A2, round 5 M4. Librarian open items hold each.

## Tiers (owner Q46)
Opus 5.5 orchestrates; Codex `gpt-6.1-sol` codes and fixes (`codex exec`); fresh Fable agents do the plan review and
the code review (read-only); Fable writes and revises the brief; Opus runs the output critic and the blind verifier.

## Machine rules
- Every run goes through `scripts/run.sh`; pass `--config config.example.toml` to `casefile bench` on this Mac. For
  `casefile memo`, `report`, `depo`, `hearing`, `status` or `doctor`, write a temp config whose model host is the
  stand-in's own port: `config.example.toml` points at `127.0.0.1:11434`, where the owner's local-worker Ollama listens.
- Tests default to `http://127.0.0.1:9`; no test may reach 11434.
- Codex builders: `codex exec -C <tree> -m gpt-6.1-sol -s workspace-write -c sandbox_workspace_write.network_access=true
  -c model_reasoning_effort=high -o <report.md> "<prompt>" < /dev/null > <log> 2>&1`, sandbox off, with the tool's own
  background mode (not a shell `&`, which gives no completion notice). Builders do not commit; the chair re-runs CHECKs,
  seeds, gates, commits. Prompts live in `.workflow/scratch/round0N-prompts/` (`common.txt` plus a header).
- A lane B worktree needs its own toolchain: `T=$HOME/.casefile-dev/<worktree-name>`, then `UV_PYTHON_INSTALL_DIR=$T/python
  UV_CACHE_DIR=$T/cache UV_PROJECT_ENVIRONMENT=$T/venv uv sync` with the sandbox off, and the same three variables in the
  builder's environment.
- Privacy: `~/local-worker/log.jsonl`, `~/local-worker/allowed/` and `~/.claude/uploads/` hold real client material. No
  loop agent reads them unless the owner waives it for named files in that session (Q59 did, for five files, once).
- Inside the sandbox, Tesseract needs resolved paths (`$(cd $TMPDIR && pwd -P)`). macOS has no `timeout` command.
- Run the gate before every chair commit. Verify a seed applied (`cmp -s`) before counting it. Measure a gate rule on
  the answer key before ruling it (Mistakes Log, R6).
- Leftovers needing the owner's say-so to delete: worktrees `.claude/worktrees/agent-a582821e2b2e41b16`, `r3-lane-b`,
  `r4-lane-b`, `r5-lane-b`, `r6-lane-b` (branches `r3/lane-b` to `r6/lane-b`, all merged); branch `control/r2-sonnet`; the
  untracked `tests/fixtures/matters/9001.001/.claude/`; untracked `.agents/` and `AGENTS.md`; old `casefile-run.*` and
  `critic6*`, `verify6`, `chair6` folders in the shared TMPDIR; `/private/tmp/round06-fix3/`, `/private/tmp/w1-controls/`.

## Cost rules (owner)
One orchestrator alive at a time. Builders report once, with no polling. Logs go to files, with short summaries. A fresh
session per round; this page is the entry point.
