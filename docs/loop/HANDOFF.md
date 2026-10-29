# casefile: loop handoff (2026-10-28, round 7 closed)

Read this page, then `.workflow/LEDGER.md` (`## Project`, `## Clarified` Q1 to Q63, `## Round 7`), then `Librarian.md`
(builder pre-flight and open items). Spec (canon): `docs/spec.md`.

## Where things stand
- Stages 1 to 7 are built, verified and merged to local `main`. `main` is NOT pushed: the owner runs `git push origin main`.
- Round 7 (anonymizer, brief package, fact identity): PASS, `docs/loop/round-07/round07-report.md`; output critic
  `6/10 · high 2 · med 4 · low 6`, every finding fixed in fix cycle 2; three fix cycles used (the cap).
- `loop/round-08` is open at the round 7 close with no work.
- Baselines (ledger `## Project`): `993 passed`, gate `0`, `unused_imports=0`, bench flawed `found=26 of 36 ... dates_wrong=1`,
  ideal `found=36 of 36 ... dates_wrong=0`, stage 5 `casefile_lines=55`, stage 6 `docs=6 of 6`, stage 7 `stage7 exit=0
  packages=2 of 2 blocked_seeded=1 of 1 drafts=2 of 2 answers=+8 identifiers_in_package=0 server_stopped=1`.

## Owner check-in first (round 8)
- Pending veto: spec §9 D63 to D67 (round 7 brief), D68 (`[AGE-n]` for two or more distinct ages, refining Q63), and the
  chair's round 7 rulings in the ledger `## Round 7` (non-tty name-list halt prints kind and cite only; run log and
  `anon/` inside the matter boundary; name variants, `[anon.aliases]`, ambiguous names block; the playbook revert).
- Decide round 8's scope. Candidates: (a) stage 7b, the cloud round trip (D52 to D62, `docs/loop/design/cloud-roundtrip-proposal.md`),
  which now has its anonymizer, package and restore check; (b) the stage 6 output follow-up: owner Q59 items 82 to 86,
  the format specification and its 15 practice questions (`docs/loop/design/output-format-from-examples.md`), critic 2
  M2 to M6. Recommend asking the owner which matters first for daily use; (b) improves documents used today, (a) is new
  capability.
- Present the round 7 recorded limits (below).

## Carried into round 8
Recorded limits: a restored quote keeps its page's date spelling while prose uses the key's; the date checker over-blocks
"Stages 44 and 45." (fails closed); weekday names stay in the package; a trailing legal suffix after `[EMPLOYER]` stays;
D67 the stage 8 procedural schema's quote without cite. From round 6: Q59 items 82 to 86, the format specification,
critic 2 M2 to M6, code review L7, fix cycle 2 A2, round 5 M4, verifier notes 3 and 4. Librarian open items hold each.

## Tiers (owner Q46)
Opus 5.5 orchestrates; Codex `gpt-6.1-sol` codes and fixes (`codex exec`); fresh Fable agents do the plan review and
the code review (read-only); Fable writes and revises the brief; Opus runs the output critic and the blind verifier.

## Machine rules
- Every run goes through `scripts/run.sh`; pass `--config config.example.toml` to `casefile bench` on this Mac. For
  `casefile memo`, `report`, `depo`, `hearing`, `brief-out`, `brief-in`, `status` or `doctor`, write a temp config whose
  model host is the stand-in's own port: `config.example.toml` points at `127.0.0.1:11434`, the owner's Ollama.
- Tests default to `http://127.0.0.1:9`; no test may reach 11434.
- `uv` cannot open its cache inside the Claude sandbox here: chair runs of `scripts/run.sh` need the sandbox off.
- Codex builders: `codex exec -C <tree> -m gpt-6.1-sol -s workspace-write -c sandbox_workspace_write.network_access=true
  -c model_reasoning_effort=high -o <report.md> "<prompt>" < /dev/null > <log> 2>&1`, sandbox off, with the tool's own
  background mode. Builders do not commit; the chair re-runs CHECKs, seeds, gates, commits. Prompts live in
  `.workflow/scratch/round0N-prompts/` (`common.txt` plus a header). `common.txt` forbids `~/local-worker/` and uploads;
  add: practice files (`playbook/`, `rules.toml`) are the owner's and are never edited to make a test pass (#R07-CH-1).
- A lane B worktree needs its own toolchain: `T=$HOME/.casefile-dev/<worktree-name>`, then `UV_PYTHON_INSTALL_DIR=$T/python
  UV_CACHE_DIR=$T/cache UV_PROJECT_ENVIRONMENT=$T/venv uv sync` with the sandbox off, and the same three variables in the
  builder's environment.
- Privacy: `~/local-worker/log.jsonl`, `~/local-worker/allowed/`, `~/local-worker/fixtures/`, `~/local-worker/handoff/`
  and `~/.claude/uploads/` hold real client material. No loop agent reads them unless the owner waives it for named files
  in that session. `~/local-worker/anonymize.py` was read once in round 7 for logic only (owner Q61).
- Inside the sandbox, Tesseract needs resolved paths (`$(cd $TMPDIR && pwd -P)`). macOS has no `timeout` command.
- Run the gate before every chair commit. Verify a seed applied (`cmp -s`) before counting it. Measure a gate rule on
  the answer key before ruling it (Mistakes Log, R6). Probe a privacy check with forms the fixture does not hold.
- Leftovers needing the owner's say-so to delete: worktrees `.claude/worktrees/agent-a582821e2b2e41b16`, `r3-lane-b` to
  `r7-lane-b` (branches `r3/lane-b` to `r7/lane-b`, all merged); branch `control/r2-sonnet`; the untracked
  `tests/fixtures/matters/9001.001/.claude/`; untracked `.agents/` and `AGENTS.md`; old `casefile-run.*`, `critic6*`,
  `verify6`, `chair6`, `critic7`, `verify7` folders in the shared TMPDIR; `/private/tmp/round06-fix3/`,
  `/private/tmp/w1-controls/`, `/private/tmp/round07-extra-controls.log`, `/private/tmp/round07-fix2/`,
  `/private/tmp/casefile-r7-fix3/`.

## Cost rules (owner)
One orchestrator alive at a time. Builders report once, with no polling. Logs go to files, with short summaries. A fresh
session per round; this page is the entry point.
