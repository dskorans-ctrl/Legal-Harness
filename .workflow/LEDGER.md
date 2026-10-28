# casefile: loop ledger

Chair: the primary Claude Code session for each round. Loop: create (Fable brief, Codex review, Fable
revision) → build (Opus orchestrates, Sonnet codes) → critic (Codex code review, output critic, blind
verifier) → close, one round per branch and per session. Owner decisions are binding; see `## Clarified`.
Seeded 2026-10-25; round 1 opened 2026-10-25 on `loop/round-01`.

## Project
- Spec: docs/spec.md (canon). Pillars §1 · decisions table §9 · open questions §10 · roadmap with an
  exit test per stage §7 · as-built §11.
- App: casefile, a fixed-workflow case system for one attorney, run locally on a Mac Studio. Python
  3.12, FastAPI and plain HTML, Ollama native API, SQLite run log, append-only JSON case file.
- Harness (round 1 builds and measures these): every run through `scripts/run.sh` (50 MB cap, exit 97);
  tests `scripts/run.sh pytest -q`; gate `scripts/run.sh python -m casefile.gate` prints 0;
  benchmark `scripts/run.sh casefile bench --matters tests/fixtures/matters`; full run
  `scripts/run.sh casefile demo tests/fixtures/matters/<matter>`; a stand-in model server in
  `tests/fakemodel/` (recorded answers, plus truncated, malformed and forbidden ones on demand);
  page screenshots with Playwright.
- Checks: a check prints the one number that fails it, exits non-zero on FAIL, and has been proven
  red on a seeded defect before its pass counts.
- Finish line (owner): spec §7 stages 1 to 8 done and verified in the loop; then stage 9 on the Studio.
- Standing freezes: none.
- OCR tools (Q39): ocrmypdf and tesseract under `/opt/homebrew/bin`; `scripts/run.sh` appends it to PATH.
- Privacy: no real client record, name or fact in any loop session; fixtures are invented.
- Regression baselines (set at the round 4 merge, 2026-10-28, tip of `loop/round-04`):
  `scripts/run.sh pytest -q` -> `537 passed` (under 90 s: `scripts/run.sh scripts/suite_time.sh 3` -> `suite_time runs=3 max=57.46
  verdict=PASS`, exit 0); `scripts/run.sh python -m casefile.gate` -> `0`;
  `scripts/run.sh python scripts/unused_imports.py src tests scripts` -> `unused_imports=0`;
  `casefile bench --config config.example.toml --matters tests/fixtures/matters --candidate
  tests/fixtures/bench/flawed.json` -> exit 1, `bench 9001.001 model=candidate found=26 of 29 missed=3
  invented=2 extra=2 flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14`; the same with
  `--candidate tests/fixtures/matters/9001.001/ideal.json` -> exit 0, `bench 9001.001 model=candidate found=29
  of 29 missed=0 invented=0 extra=2 flags=9 of 9 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14`;
  stage 1 exit test `exit=0 verdicts=8 fails=set() test_jobs=1`; stage 2 exit test `stage2 exit=0 runs=+1
  answers_ok=+1 server_stopped=1`; stage 3 exit test `stage3 exit=1 pages=6 ids_ok=6 of 6 stamps_ok=6 of 6
  text_ok=6 of 6 must_ok=5 of 5 empty=1 failed=0 min_ratio=1.000`; stage 4 exit test `stage4 exit=0 gates=6 of 6
  cases=14 of 14 runs=+14 answers=+21 empty_saved=0 server_stopped=1` (seven `stage4` lines); doctor
  `runlog_schema PASS schema=2 triggers=21 (counted)`; intake of the fixture `intake 9002.001 scan pages=6 ok=5
  empty=1 failed=0 stamps=6 had_text=2 ocr_added=4`, exit 1.
- Records: Librarian.md · docs/loop/round-NN/ · docs/loop/agent-log.md · docs/loop/questions-for-owner.md ·
  docs/loop/tuning-questions.md · docs/loop/HANDOFF.md · docs/loop/next-round.md.

## Standing rules digest
- Spec is canon; every design change goes in spec §9.
- One round per session; Remote Control on; handoff and next-round prompt written at close.
- No client data in any session or commit.
- Every check proven red on a seed before its pass counts; never lower a threshold or exempt by name.
- `main` pushed only on the owner's word (`git push origin main`).
- Prose has no em or en dashes.

## Clarified
- Q1: scope? -> the case system in spec §2 and §7, built in stage order.
- Q2: done means? -> spec §7 stages 1 to 8 pass their exit tests and the verifier's V. in the loop;
  stage 9 (real benchmark on the Studio) is run by the owner.
- Q3: freezes? -> none.
- Q4: where does work land? -> branch per round `loop/round-NN`, merged to main only after V.
- Q5: stall rule? -> three verify-fix cycles per round, then discard and re-brief; two stalled rounds
  in a row stop the loop and report to the owner.
- Q6: check rule? -> every new check, test or gate goes red on a seeded defect before its pass counts.
- Q7: rulings while the owner is away? -> the chair, by the spec's pillars, logged as pending veto.
- Q8: sessions (owner, 2026-10-25)? -> a fresh session for each round, automatically on Remote
  Control, with a critic round before every close.
- Q9: client data (owner, 2026-10-25)? -> never in any build session; invented test matters only.
- Q10: tiers (owner, 2026-10-25)? -> gdd-loop's: Fable writes and revises the brief; Codex gpt-6.1-sol
  reviews plan and code; Opus 5.5 orchestrates, critiques outputs, verifies; Sonnet 5.5 writes all code.
  Builders may delegate to Sonnet children only.
- Q11: machine (owner, 2026-10-25)? -> this Mac is a dev Mac, not the Studio. Install Python 3.12
  project-local with uv only; no Ollama, no Tesseract, no brew. The stand-in model server replaces the
  model. `casefile doctor` reports OCR as FAIL (never skipped) until stage 3.
- Q12: first playbook (owner, 2026-10-25)? -> `rules.toml` holds the four firm rules in spec §4; every
  other playbook entry is an invented test fixture marked SAMPLE. Practice content is the owner's.
- Q13: additional instructions (owner, 2026-10-25)? -> none; proceed.
- Q14: builder tier (owner, 2026-10-25, supersedes Q10's coding tier for cost)? -> Codex gpt-6.1-sol
  writes all code, via the local `codex exec` CLI with `-s workspace-write` in the repo (or a worktree),
  never with network or outside-repo write. Opus still orchestrates and re-runs every CHECK and seed;
  Codex still does the plan and code reviews (independence reduced; the blind Opus verifier carries it).
- Q15: critic timing (owner, 2026-10-25)? -> no code review until the night of 2026-10-26. This session
  runs brief, plan review, revision and build, then stops before the critic round with round 1 unmerged
  on `loop/round-01`. The next session runs the critic round (8a to 8c) and close; the owner may
  change tiers then.
- Q16: firm rule 5 (owner, 2026-10-25, owner question 4)? -> checked on outputs only, never on the
  records being read. Outputs never name the exam as a DME or IME in any form: block "DME", "IME",
  "independent medical examination" and "defense medical examination" (whole words, any case); always
  "the report".
- Q17: matters folder (owner, question 3)? -> outside the repo checkout (e.g. ~/Cases), set in config.toml.
- Q18: local binding (owner, question 6)? -> yes: `sandbox.network.allowLocalBinding: true` in the
  project's `.claude/settings.json`.
- Q19: Ollama on the Studio (owner, question 7)? -> not decided; build for the login-user app case,
  question stays open.
- Q20: model tag (owner, question 2)? -> `qwen3.8:27b`, set in config.toml.
- Q21: Bates format (owner, question 5)? -> letters plus digits: `[A-Z]{1,8}[ -]?\d{4,}`, configurable.
- Q22: tiers for round 1 session 2 (owner, 2026-10-26)? -> code review Codex gpt-6.1-sol (high);
  output critic and blind verifier fresh Opus 5.5, one each; fixes written by Codex gpt-6.1-sol
  (as Q14), chair commits and re-runs seeds.
- Q23: cycle cap reached in round 1 (owner, 2026-10-26)? -> one extra fix cycle (exception to Q5),
  limited to B1b and B3, then one focused fresh re-verify; if that fails, discard per Q5.
- Q24: round 1 discarded after the focused re-verify failed (owner, 2026-10-26)? -> re-brief on the
  branch: keep `loop/round-01`'s tip; the next session runs a Fable brief limited to a redesign of the
  path-identity guards and wrapper exit branches plus V3-1 to V3-4, a Codex plan review, build, the full
  critic round, then close and merge. `main` stays at the seed until then.
- Q25: additional instructions at round 1 close (owner, 2026-10-26)? -> "Hold the round for now": do not
  start the re-brief until the owner says so.
- Q26: (owner, 2026-10-26, after merging origin/main 4614a1e spec §8b) -> "ok, finish round 1": the Q25 hold
  is lifted; run the Q24 re-brief in this session with Q22 tiers, then close and merge.
- Q27: tiers for the re-brief (owner, 2026-10-26, supersedes Q22's coding tier)? -> Opus 5.5 orchestrates
  (the chair); Sonnet 5.5 writes all code, builds and fixes; Codex gpt-6.1-sol keeps the plan review and
  code review. Fable brief, Opus output critic and blind verifier unchanged.
- Q28: tiers for round 2 (owner, 2026-10-26, supersedes Q27's coding tier)? -> the local model
  `gemma4:e4b-it-qat` (Ollama on this Mac, localhost:11434) writes all code and fixes, driven by the Opus
  orchestrator with small, fully specified tasks; Opus adapts its builder instructions to that model.
  Codex gpt-6.1-sol keeps plan and code review. Fallback: a task Gemma fails after 3 attempts with test
  feedback plus one re-split goes to Sonnet 5.5, logged as a deviation. An extra Fable agent reviews the
  round's code for quality and errors against what Sonnet 5.5 would produce, placed after 8a Codex and
  before 8b; its reproduced findings join fix cycle 1. Fable brief, Opus critic and verifier unchanged.
  Additional instructions: none.
- Q29: cost report (owner, 2026-10-26)? -> the round report states how many tokens the build cost
  (Gemma local tokens, Opus orchestration, Sonnet fallbacks) compared with the token cost of a Sonnet
  build of the same work, counting every Sonnet takeover.
- Q30: Gemma scope (owner, 2026-10-26)? -> Gemma codes for round 2 only, as a trial. From round 3 the
  tiers return to the defaults (Q27: Fable brief, Codex plan and code review, Opus orchestrator, critic
  and verifier, Sonnet 5.5 code). The round 2 build resumes when the owner's other Gemma job is done
  (checked every 30 minutes).
- Q31: owner away overnight (owner, 2026-10-26 ~23:05)? -> keep the loop running until the owner returns;
  the chair makes the calls, each logged in `docs/loop/questions-for-owner.md` under "Round 2 overnight
  rulings" as pending veto or ratification.
- Q32: round 2 hold, question 30 (owner, 2026-10-27)? -> (a) one extra fix cycle limited to V2b-F1, then a
  focused fresh blind re-verify, then close. Overnight rulings OR-1 to OR-9 ratified; spec D25 and D26
  ratified.
- Q33: coder for the V2b-F1 fix (owner, 2026-10-27; the owner's other Gemma job was running)? -> Sonnet
  writes it; a deviation from Q28, logged in the round report.
- Q34: round 3 check-in (owner, 2026-10-27), held questions 21 to 29 and round 1 holds? -> Q21 keep the key
  categories as listed. Q22 benchmark matters live in a separate folder outside the checkout, same layout
  as `tests/fixtures/matters/`. Q25 flags match by kind plus cite set (D25 stands). Q26 an unreachable model
  server makes `casefile bench` exit 2 (cannot run); Q27 the bench line names the model (`model=<tag>`).
  Q29 "Dr. X's report" is allowed; only the DME and IME labels are banned (Q16). Round 1 holds 8 to 20: all
  interim rulings ratified; question 7 (Ollama user or daemon) stays open (Q19).
- Q35: Bates stamps (owner, 2026-10-27, question 23)? -> "Bates stamps only necessary for hearing prep. For
  hearings, ask me which bates stamp to use. Normally for a hearing I'll upload a medical binder which has
  our bates stamp at bottom center of each page." A page may carry more than one stamp. Chair reading: a
  page ID is matter, binder, page (spec §3); intake records every Bates stamp found on a page without
  choosing one; hearing prep asks the attorney which stamp to cite.
- Q36: question 24, key completeness (owner: no preference)? -> chair ruling, pending veto: the key lists
  every real gap and conflict a careful reader would flag; an extra flag keeps failing the run.
- Q37: bills (owner, question 28)? -> "Billing memo will be provided, no need to create that separately."
  The attorney supplies the billing memo; casefile does not build one and test matters need no bills.
- Q38: round 3 scope and tiers (owner, 2026-10-27)? -> spec §7 stage 3 on `loop/round-03`; Q30 default tiers;
  merge to `main` after V.; do not start round 4. Additional instructions: none; proceed.
- Q39: OCR on this dev Mac (owner, 2026-10-27, supersedes Q11 for OCR only)? -> install ocrmypdf here with
  brew (the owner runs `brew install ocrmypdf`, which brings Tesseract, Ghostscript and qpdf). D6 unchanged;
  the doctor's OCR check must PASS for real. Ollama and other brew installs stay barred.
- Q40: round 3 brief questions 31 to 36 (owner, 2026-10-27)? -> 31 `MED0001`, `MED 0001`, `MED-0001` are the
  same stamp: intake keeps the raw text and a normalised form (letters plus digits) so cites match across
  spellings. 32 a page with no text after OCR is listed as an open item, exit 1, never counted as read. 33
  the binder is a typed name (letters, digits, hyphens). 34 re-intake into an existing binder is refused
  until the old binder is removed by hand. 35 every token matching the stamp pattern is recorded and shown.
  36 OCR in English only. Homebrew, ocrmypdf and tesseract are installed under `/opt/homebrew/bin`.
- Q41: question 37, the degeneration disagreement MED0006 vs DEF0002 (owner, 2026-10-27)? -> "Where records
  conflict, especially between defense examinations and our records, those need to be flagged. Records
  around that should be anonymized so I can upload to Claude for more advanced review." Keyed as conflict
  G9 (9 flags). Standing rule for the key: a disagreement between a defense examination and our records is
  a conflict to flag, even where one record does not expressly exclude the other. The anonymized excerpt
  around each conflict is a new requirement for the anonymization stage (spec §2 brief package, §10),
  not stage 3.
- Q42: round 3 close check-in (owner, 2026-10-27)? -> question 38: no suffixes; a stamp is letters plus digits and
  a token that runs on is not a stamp (whole-token rule stands). 39: no stamp position recorded. 40: the first
  raw spelling of a stamp is enough. 41: lowercase binder names accepted. Spec D27 to D30, the whole-token
  stamp rule and G9 RATIFIED. Additional instructions: none.
- Q43: question 7, Ollama on the Studio (owner, 2026-10-27, round 4 check-in; closes Q19)? -> the login-user app
  (Ollama.app). The doctor's listener check stays `lsof` as the login user; a listener it cannot see is FAIL, never skip.
- Q44: round 4 brief questions 42 to 46 (owner, 2026-10-27)? -> 42 a page that fails both attempts stays open until the
  model reads it; no manual read. 43 firm rules check our words only; a verbatim record quote is exempt. 44 only a stamp
  alone on a line and "Page N of M" lines are ignored by the quote ladder. 45 an OCR-rung match counts as verified; the
  rung is in the run log only. 46 punctuation repairs are in the run log only. Additional instructions: none; proceed.
- Q45: round 4 tiers (owner, 2026-10-27, session 2)? -> "use Codex Sol 6.1 to code this round, and Astra for the
  review". Chair's reading: Codex `gpt-6.1-sol` (CLI, `-s workspace-write`) replaces Sonnet 5.5 as builder and fix
  worker; Codex `gpt-6-astra` (read-only) takes the plan review (6) and the code review (8a). Opus 5.5 still
  orchestrates and runs the output critic and blind verifier; Fable still revises. Round 4 only. The Sol plan review
  in progress was stopped and rerun on Astra (partial log kept, `round04-brief-codex-sol-stopped.log`).
- Q46: tiers from round 5 on (owner, 2026-10-27, round 4 session 2)? -> "For the next rounds use Opus 5.5 to
  orchestrate, Codex Sol 6.1 to code, Fable to review." Chair's reading: from round 5, Opus 5.5 orchestrates, Codex
  `gpt-6.1-sol` codes and fixes, Fable takes the plan review and the code review (each a fresh Fable agent with no
  context from the brief's writing, read-only). Unchanged unless the owner says otherwise: Fable writes the brief,
  Opus runs the output critic and blind verifier. Round 4 stays on Q45 (Astra reviews its code). Chair's caution,
  for the round 5 check-in: a Fable review of a Fable brief is one model family checking itself; the fresh agent
  and the blind verifier are the guard.
- Q47: anonymization convention (owner input, 2026-10-27, `~/local-worker/handoff/anonymization-convention.md`,
  "casefile-anon/1"; outside the repo)? -> four decisions asked for stage 7, not round 4: (1) one fixed bracketed
  placeholder convention on every matter (`[CLAIMANT]`, numbered `[DR-n]`, `[ATTY-n]`, `[PERSON-n]`, org and place
  kinds, dates relative to the injury date `[DATE D+n]`, `[MONTH M+n]`, `[YEAR Y+n]`, `[DATE-REF-n]`, `[ID-n]` and
  contact kinds, `[SRC-n]`; titles outside brackets; restored dates M/D/YYYY); (2) the local model finds only names
  and the anchor date, code does every replacement, date conversion, re-identification and check; (3) fail closed
  both ways (draft check before re-identifying, restore check after, line count kept for page:line cites); (4) spec
  §3 Anonymizer row to "local model entity pass plus code rules, the matter's name list in the identifier check;
  Presidio or GLiNER-PII optional as a second detector". Reference code `~/local-worker/anonymize.py` with 16 offline
  tests on `fixtures/anon-matter/`. Status: logged; carried to the stage 7 brief and its plan review (spec §10). Open
  there: the spec's unnumbered `[EMPLOYER]` examples; Q41 excerpt size; the key lives only in the `casefile` user's
  matter folder (§8b). Chair's privacy note: the convention's evidence came from a de-identified real matter, and
  `~/local-worker/log.jsonl` holds real client prompts; before any port, the stage 7 builder copies code only, and
  the chair confirms `fixtures/anon-matter/` is invented before it enters the repo.
- Q48: after round 4 (owner, 2026-10-27, going offline)? -> "if this round finishes, just start the next one without
  me. Once I'm up I'll push to main and we'll do the handoff." Overrides "one round per session" and the session's
  "do not start round 5" for tonight only. Round 4 closes in full (merge to local `main`, records, handoff draft);
  round 5 opens on `loop/round-05` with Q46 tiers; the owner check-in is replaced by held questions in
  `docs/loop/questions-for-owner.md` with interim rulings by the pillars, pending veto (skill autonomy rule). No push.

## Round 1: stage 1 skeleton and harness (opened 2026-10-25)

- [~] R1-1. Build brief reconciled to the code at main `5a55b54`, a CHECK and seed per item, Codex
  reviewed, revised with dispositions. `.workflow/scratch/round01-build-brief.md`.
  deferred: chair at close
- [x] R1-2. `scripts/run.sh <cmd>`: caps combined stdout/stderr at 50 MB, exits 97 when the cap is hit,
  otherwise carries the child's exit code.
  Build note (chair re-run, not a tick): cap `exit=97 bytes=52428800`, child `3`, capture `98`; SEED `head -c "$CAP"` -> `exit=0`; restored by cmp.
  Verifier (blind, 2026-10-26, tip 9c25e8f): `scripts/run.sh bash -c 'head -c 52428801 /dev/zero | tr "\0" a' | wc -c` -> `52428800`, pipefail exit `97`, stderr `run.sh: output cap 52428800 bytes hit (child status -9); exit 97`; `bash -c 'exit 3'` -> `3`; exact cap -> `0`; no args -> `96`; `TMPDIR=/nonexistent/dir` -> `98`. SEED run_capture.py:32 `128 - status` -> `1`: `1 failed, 161 passed` (sigkill `(1, 0) == (137, 0)`), restored cmp 0.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): still holds: pipefail cap `52428800` bytes, exit `97`, `secs=0` with `sleep 30` after the overflow and with a background `sleep 30`; `bash -c 'exit 3'` -> `3`; exact cap -> `0`; no args -> `96`; `TMPDIR=/nonexistent/dir` -> `98`.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds: pipefail `head -c 52428801` -> `52428800` bytes, exit `97`, `secs=0.45`, background grandchild `dead`; exact cap `52428800` exit `0`; `bash -c 'exit 3'` -> `3`; no args `96`; `TMPDIR=/nonexistent/dir` `98`.
- [x] R1-3. Skeleton: Python 3.12 (uv, project-local), package `casefile`, console entry `casefile`,
  `scripts/run.sh pytest -q` green.
  Build note: `3.12.13 0.1.0`, `casefile 0.1.0`; isolation SEED (matters -> repo `Cases`) -> pytest exit 3 `test isolation failed`; restored by cmp, exit 0.
  Verifier (blind, 2026-10-26, tip 9c25e8f): `scripts/run.sh python --version` -> `Python 3.12.13`; `scripts/run.sh casefile version` -> `casefile 0.1.0` (venv `~/.casefile-dev/legal-harness/venv`, D23); `scripts/run.sh pytest -q` -> `162 passed in 9.82s`.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): `scripts/run.sh pytest -q` -> `184 passed in 10.40s`.
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): still holds: `scripts/run.sh pytest -q` -> `192 passed in 11.26s`, exit `0`.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds: `scripts/run.sh pytest -q` -> `233 passed in 43.24s` (again `233 passed` x2 inside the gate).
- [x] R1-4. Config: one config file with defaults and validation; an unknown key or bad value fails
  closed with a message, never a silent default.
  Build note: SEED unknown-key raise -> `continue` gave `4 failed, 21 passed`; restored green.
  Verifier (blind, 2026-10-26, tip 9c25e8f): REFUSED. Unknown key, bad type, low num_ctx, bad host, missing file, matters in checkout all exit 2 with a ConfigError (seed config.py:69 missing-file branch -> `3 failed, 159 passed`). But `[paths].matters = "/Users/davidskoranski/LEGAL-HARNESS/invented-matters"` (case variant of the checkout on case-insensitive APFS) -> `casefile config show` exit `0`, `paths.matters = "/Users/davidskoranski/LEGAL-HARNESS/invented-matters" (source=file)`: config.py:128 `is_relative_to(checkout)` compares case-sensitively. Fail open on D13/Q17. Blocking.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): REFUSED. B1 itself is fixed: `/Users/davidskoranski/LEGAL-HARNESS/invented-matters`, `Legal-Harness`, `LEGAL-harness/SRC/new/deeper`, `tests/../INVENTED/x`, a symlink to the checkout (plain or case-swapped), `/System/Volumes/Data/...` firmlink, `~/legal-harness/invented` all exit `2` `must be outside the checkout`; relative `invented-matters` and `./invented-matters` exit `2` `must be an absolute path`; unknown key, unknown table, bad type, num_ctx 32768, host localhost/0.0.0.0/https//v1, no matters, matters int, missing file all exit `2` with a ConfigError. But a symlink to a case-swapped SUBDIRECTORY of the checkout loads: `$SCRATCH/aliasFix -> /Users/davidskoranski/LEGAL-HARNESS/tests/fixtures`, `matters = "$SCRATCH/aliasFix/invented-matter"` -> `casefile config show` exit `0`, `paths.matters = "/Users/davidskoranski/LEGAL-HARNESS/tests/fixtures/invented-matter" (source=file)` (also `aliasSrc -> .../Legal-Harness/src` exit `0`). config.py:129-131 walks the ancestors of the unresolved path and compares the resolved path by spelling. Fail open on D13/Q17. Blocking. Also SEED config.py:134 OSError raise -> `inside = False` stays `81 passed` (branch reachable: matters under a chmod 000 folder -> exit 2 `cannot verify`).
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): REFUSED. Config guard holds on 17 aliases: case-swapped checkout, symlink to root (plain and case-swapped), symlink to case-swapped subfolder, chains `chain2 -> chain1 -> .../Legal-Harness/tests/fixtures` and to root, relative symlink to `LEGAL-harness/src`, dangling symlink into `LEGAL-HARNESS/no-such-dir`, `tests/../INVENTED/x`, `$S/nope/../../../../../../Users/davidskoranski/legal-harness/inv`, `~/legal-harness/inv`, the checkout itself all exit `2` `must be outside the checkout`; relative and `./` exit `2` `must be an absolute path`; chmod 000 parent exit `2` `cannot verify ... [Errno 13]`; outside existing and new folders exit `0`. SEEDS config.py:132 drop `resolved` candidate `2 failed`; config.py:129 `resolved = matters` `2 failed`; cmp restored, `192 passed`. But (1) a symlink loop `loopA -> loopB -> loopA`, `matters = "$S/loopA/m"` -> exit `1`, traceback `RuntimeError: Symlink loop from '.../loopA/m'` at config.py:129 (pathlib raises RuntimeError, not OSError; fails closed but not exit 2 with a ConfigError). (2) Toolchain guard fails open on `..` after a missing component: `CASEFILE_TOOLCHAIN="$S/nope/../../../../../Users/davidskoranski/legal-harness" scripts/run.sh sh -c 'mkdir -p "$UV_PROJECT_ENVIRONMENT"'` -> exit `0` and created `/Users/davidskoranski/legal-harness/legal-harness/venv` (removed). Expected `95` (D12, D23). Both blocking (verify3 V3-1, V3-2). Other toolchain aliases (literal, case, symlink, case-swapped symlink, chain, `tests/..`, relative) exit `95`; locked folder `95` `cannot verify`; normal `0`.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): `casefile config show` exits `2` with a ConfigError on unknown key `[paths].bogus`, `num_ctx = "65536"` (bad type), host `http://localhost:11434`, missing file, config path a directory, and every matters alias in R1-22 (26 probes); outside `$S/out/m` and `$S/out/new/m` exit `0`. SEED config.py:71 missing-file branch dropped -> `3 failed, 27 passed`, cmp 0. SEED config.py:118 host path/query/fragment check -> `and True`: `http://127.0.0.1:11434/v1?x=1#f` loads, `1 failed, 55 passed`, cmp 0. Non-blocking (fails closed, exit 1, traceback, no ConfigError): `--config $S/loopA` (symlink loop) -> `RuntimeError: Symlink loop` (config.py:67); `state = "~nosuchuserxyz/st"` and `playbook = "~nosuchuserxyz/pb"` -> `RuntimeError: Could not determine home directory.`; `state = "$S/loopA/st"` -> `RuntimeError: Symlink loop` (config.py:145). Same class as the carried 8a low; D13's ConfigError clause names matters only.
- [x] R1-5. `playbook/rules.toml` with the four spec §4 firm rules, loaded and validated; each rule has a
  test with a forbidden output that goes red.
  Build note: SEED drop `re.IGNORECASE` (rules.py:59) -> `2 failed, 39 passed`; restored green.
  Verifier (blind, 2026-10-26, tip 9c25e8f): four rule ids loaded; `rules_red=9 of 9`, `good_clean=4 of 4`; probes "The IME found a normal gait." -> `['no-dme-ime']`, "Who retained the doctor?" -> `['no-hired-paid-retained']`, question "What treatment did you get and who paid the bills?" -> `['treatment-and-bills-apart']`, "Gait normal [cite p. 12]" -> `['bates-cites']` (unstamped `warning`). SEEDS rules.py:76 fullmatch->match `2 failed`; rules.py:61 unit skip off `2 failed`; rules.toml:43 drop bill pattern `4 failed`; all restored cmp 0. Non-blocking: "independent-medical-examination" and "defense medical-examination" (hyphens) -> `[]`.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds: gate `rules_selftest PASS misses=0 false_hits=0`; full suite `233 passed`.
- [x] R1-6. Playbook loader: entries carry rule, why, good example, bad example, date added, where
  learned (spec §6); malformed entry fails closed; a playbook version is computed. Entries other than
  rules.toml are invented and marked SAMPLE (Q12).
  Build note: lane B reports `refused=3 of 3`, `version_changed=1` with seeds red; chair did not re-run these two seeds.
  Verifier (blind, 2026-10-26, tip 9c25e8f): `casefile playbook show` -> `version=pb-8c41a5ae7727 entries=7` (4 rules + 3 SAMPLE); missing-why fixture -> exit 2 `missing field why`; unmarked fixture -> exit 2 `field sample: round 1 requires sample = true and rule starting SAMPLE:`; one byte appended -> `version=pb-959a6c383d9a`. SEEDS playbook.py:72 sample check off `3 failed`; playbook.py:109 duplicate id off `2 failed`; playbook.py:86 rules.toml guard off `1 failed`; restored cmp 0. Non-blocking: SEED cli.py:38 playbook error `return 2` -> `return 0` stays `162 passed` (CLI exit untested).
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds: gate `playbook PASS invalid=0 unmarked=0 version=pb-00be6eb62752`; doctor `playbook PASS version=pb-00be6eb62752`.
- [x] R1-7. Run log (SQLite): every run, card version, pages in, raw answer, failures, approvals
  (spec §5); records a test job.
  Build note: SEED `approvals_no_delete` -> `SELECT 1` gave `1 failed, 24 passed`; restored green.
  Verifier (blind, 2026-10-26, tip 9c25e8f): driven doctor x2 on stand-in: runs `(1, 'doctor', 'doctor.warmup', 'a48ba54e9a3e', 'pb-8c41a5ae7727', 'qwen3.8:27b', 0, ...)`, answers `(1, 'ok', 'stop', 21, 2, '{"model": ...')`, `DELETE FROM runs` -> `runlog is append-only`. SEEDS runlog.py:111 foreign_keys OFF `2 failed`; runlog.py:92 drop card filter `1 failed` (`assert 2 == 1`); doctor.py:142 status always failed `4 failed`; restored cmp 0.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds: two driven doctor runs -> runs `(1|doctor|doctor.warmup|qwen3.8:27b)`, `(2|...)`, answers `1|ok|stop|21|2`, `2|ok|stop|21|2`; `delete from runs` -> `runlog is append-only (19)`. SEED runlog.py:92 card filter dropped -> `1 failed, 41 passed`, cmp 0.
- [x] R1-8. Stand-in model server `tests/fakemodel/`: Ollama native `/api/chat` shape; replays recorded
  answers; returns truncated, malformed or forbidden answers on demand.
  Build note: socket `test_http_roundtrip` 1 passed outside the sandbox; FAILS (not skips) inside it until the session restarts with Q18's setting.
  Verifier (blind, 2026-10-26, tip 9c25e8f): over HTTP on 127.0.0.1: replay `'READY' stop ctx 65536`; truncated `'RE' length`; malformed `'{"facts": [{"page": 1,'`; forbidden `'The IME found no injury; ...retained by the employer.'`; short_context ps `8192`; empty `''`; unrecorded `404`; `/v1/chat/completions` `404`. SEEDS core.py:88 stream check off `2 failed`; core.py:46 short_context ctx `4 failed`; restored cmp 0. Note: mode `incomplete` is not in D18's list.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds: the driven doctor ran over HTTP against `fakemodel` on `127.0.0.1:51384` (context PASS `context_length=65536`); SEED model.py:18 drop `ProxyHandler({})` (D21) -> `2 failed, 74 passed`, cmp 0.
- [x] R1-9. `casefile doctor`: Ollama on 127.0.0.1 only, full context loaded, OCR works, folders
  writable; each check PASS or FAIL with a reason, none skipped; exit code carries the verdict.
  Build note: covered by the R1-11 run; doctor seeds are Codex's only (chair did not re-run).
  Verifier (blind, 2026-10-26, tip 9c25e8f): driven run, eight lines: `config PASS`, `folders PASS writable=3 of 3`, `playbook PASS version=pb-8c41a5ae7727`, `runlog_schema PASS schema=1 triggers=15 (counted)`, `ollama_loopback PASS addr=127.0.0.1:53510`, `context PASS context_length=65536`, `runlog_job PASS test_jobs=+1`, `ocr FAIL OCR not verified: tools unavailable (...) | do: install tesseract and ocrmypdf; expected until stage 3`; `doctor failed=1 of 8`, exit 1. SEEDS cli.py:32 drop doctor return `3 failed`; doctor.py:83 lsof error ignored `1 failed`; doctor.py:47 missing matters `1 failed`; restored cmp 0. Non-blocking: SEED doctor.py:152 `== 1` -> `>= 0` stays `162 passed`; with doctor.py:142 also seeded the doctor prints `runlog_job PASS test_jobs=+0` (only the exit test's own count catches it).
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds: driven run through `scripts/run.sh casefile doctor` on the stand-in prints eight lines, each PASS or FAIL with a reason: `config PASS source=...`, `folders PASS writable=3 of 3`, `playbook PASS version=pb-00be6eb62752`, `runlog_schema PASS schema=1 triggers=15 (counted)`, `ollama_loopback PASS addr=127.0.0.1:51384`, `context PASS context_length=65536`, `runlog_job PASS test_jobs=+1`, `ocr FAIL OCR not verified: tools unavailable (tesseract exit=not-found, ocrmypdf exit=not-found) ... | do: install tesseract and ocrmypdf; expected until stage 3`; `doctor failed=1 of 8`, exit `1`; second run identical (`test_jobs=+1`). SEED doctor.py:97 accept `*:{port}` -> `2 failed, 65 passed` (`listening on *:50908` expected), cmp 0.
- [x] R1-10. Gate `scripts/run.sh python -m casefile.gate` prints 0 when green; includes the privacy
  check (PDF, Word or image outside `tests/fixtures/`, or anything under `Cases/` or `Bench/`, fails).
  Build note: gate prints `0`, exit 0 (rows pytest, privacy scanned=188, rules_selftest, playbook pb-e46d368e8caf, prose); SEED `docs/seed.pdf` -> `privacy FAIL offenders=1`, prints `1`, exit 1.
  Verifier (blind, 2026-10-26, tip 9c25e8f): `scripts/run.sh python -m casefile.gate` -> rows pytest, privacy `offenders=0 scanned=213`, rules_selftest, playbook, prose `dashes=0 files=57`, prints `0`, exit 0. SEED transient `state/probe-seed.HEIC` (ignored), `Bench/invented-notes.txt`, `docs/probe-seed.md` with U+2013 -> `gate privacy FAIL offenders=2 scanned=216`, `gate prose FAIL dashes=1 files=58`, prints `2`, exit 2; removed. SEED privacy.py:11 drop `--others` `4 failed`; restored cmp 0. Non-blocking: SEED gate.py:37 drop `false_hits == 0` stays `162 passed`.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): gate rows pytest `exit=0`, privacy `offenders=0 scanned=218`, rules_selftest `misses=0 false_hits=0`, playbook `version=pb-00be6eb62752`, prose `dashes=0 files=59`, prints `0`, exit `0`.
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): still holds: gate rows pytest `exit=0`, privacy `offenders=0 scanned=223`, rules_selftest `misses=0 false_hits=0`, playbook `version=pb-00be6eb62752`, prose `dashes=0 files=61`, prints `0`.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds on two runs: gate pytest `exit=0`, privacy `offenders=0 scanned=247`, rules_selftest `misses=0 false_hits=0`, playbook `version=pb-00be6eb62752`, prose `dashes=0 files=74`, prints `0`, exit `0`. SEED privacy.py:37 `.lower()` dropped -> `5 failed, 27 passed`, cmp 0.
- [x] R1-11. Stage 1 exit test (spec §7): `casefile doctor` runs and the run log records a test job,
  driven end to end through `scripts/run.sh`.
  Build note: `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`, 1 passed via scripts/run.sh outside the sandbox. Full suite `98 passed`.
  Verifier (blind, 2026-10-26, tip 9c25e8f): `scripts/run.sh pytest -q -s tests/test_stage1_exit.py` -> `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`, `stage-control exit=1 verdicts=8 fails={'ocr'} expected={'ocr'} test_jobs=1`, `2 passed`; socket server stopped by the test.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): `scripts/run.sh pytest -q -s tests/test_stage1_exit.py` -> `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`, `stage-control exit=1 verdicts=8 fails={'ocr'} expected={'ocr'} test_jobs=1`, `2 passed in 0.75s`. Driven doctor on the stand-in (port 18434): eight lines config, folders `writable=3 of 3`, playbook `pb-00be6eb62752`, runlog_schema `schema=1 triggers=15`, ollama_loopback `addr=127.0.0.1:18434`, context `context_length=65536`, runlog_job `test_jobs=+1` (again `+1` on a second run), ocr `FAIL ... | do: install tesseract and ocrmypdf; expected until stage 3`; `doctor failed=1 of 8`, exit `1` (R1-9 holds).
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): still holds: `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`, `stage-control exit=1 verdicts=8 fails={'ocr'} expected={'ocr'} test_jobs=1`, `2 passed in 0.78s`.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds: `scripts/run.sh pytest -q -s tests/test_stage1_exit.py` -> `stage-control exit=1 verdicts=8 fails={'ocr'} expected={'ocr'} test_jobs=1`, `2 passed in 0.81s`; in the full suite `exit=1 verdicts=8 fails={'ocr'} test_jobs=1`.
- [x] R1-12. Spec §9 rows for this round's rulings, §11 as-built updated; Librarian, agent log,
  round report under `docs/loop/round-01/`.
  deferred: chair at close
## Discoveries during round 1 (appended, not yet scheduled)

- [x] R1-13. Brief CHECK wording: R1-2 CHECK 1 needs caller `pipefail` (without it prints `FAIL exit=0`);
  R1-2 second SEED (mktemp) is masked by the later unreadable-capture guard, which also returns 98 (two
  guards mask each other: isolate each); R1-4 missing-file shell CHECK prints PASS under its seed; R1-7
  trigger seed leaves `test_jobs=1` (Codex added a status-filter seed). -> verifier checks each.
  Verifier (blind, 2026-10-26, tip 9c25e8f): REFUSED (one of four parts). (a) without pipefail the overflow pipeline exits `0`, with pipefail `97`: reproduced. (b) mktemp guard now isolated: SEED run.sh:8 drop `|| {...}` -> `capture-failure (1, 0)`, red (it also wrote a stray `out` in the cwd, removed). But the second guard is not: SEED run_capture.py:35 `return 98` -> `return 0` stays `162 passed`; `scripts/run.sh invented-no-such-cmd` -> `capture stage failed ... exit 98` on the tip, untested. Blocking. (c) SEED config.py:69 missing-file branch removed -> `3 failed, 159 passed` (message falls to `cannot load config`): red. (d) SEED runlog.py:92 card filter -> `assert 2 == 1`: red.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): REFUSED. (a) holds: without pipefail the overflow pipeline exits `0`, with pipefail `97`. (b) B2 fixed: SEED run_capture.py:13 `return 98` -> `return 0` -> `5 failed, 13 passed`; SEED run.sh:29 drop mktemp `|| {...}` -> `test_run_sh[capture-failure]` red (falls to the is_dir guard, told apart by message); run_capture.py:17 is_dir guard drop -> `2 failed`; 127 and 126 branches each red (seeds 127->126, 126->1, 126->127, FileNotFoundError->IsADirectoryError: `1 failed` each); probes missing `127`, non-executable file `126`, directory `126`, child `3`, child SIGTERM `143`. But the capture WRITE guard is not isolated: SEED run_capture.py:40-41 `return capture_failed(exc)` -> `pass` stays `81 passed`, while the branch is live (`ulimit -f 1`, 200000 bytes -> `[Errno 27] File too large; exit 98`), and a short write is ignored (`ulimit -f 1`, 4096 or 65536 bytes -> exit `0`). Blocking (same class as B2). (c) SEED config.py:69 missing-file branch -> `3 failed, 22 passed`: red. (d) SEED runlog.py:92 card filter -> `assert 2 == 1`: red.
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): REFUSED. Probes all per D12: no args `96`; cap `52428800` bytes, exit `97`, `secs=0` with `sleep 30` after overflow; `TMPDIR=/nonexistent/dir` `98`; `ulimit -f 1` 200000 and 4096 bytes `98` `[Errno 27] File too large` (B3 fixed), 400 bytes `0`; toolchain in checkout `95`; non-executable file and directory `126`; missing `127`; child `3`; background grandchild after overflow killed. SEEDS RED (cmp restored each): run.sh:23 `exit 95`->`true` `5 failed`; run.sh:19 drop physical `2 failed`; run.sh:34 mktemp `exit 98`->`0` `1 failed`; run_capture.py:13 `7 failed`; :32 127->126 `1 failed`; :35 126->1 `1 failed`; :55 `return 97`->`0` `3 failed`; :57 child code `13 failed`; :44 skip short write `2 failed`. GREEN (findings): run.sh:32 `exit 96`->`exit 0` `192 passed` (no args then exits `0`; 96 untested); run_capture.py:51 `os.killpg`->`child.kill()` `192 passed` while a background grandchild survives the cap (`grandchild=ALIVE`, tip `dead`; D12 group kill untested); run.sh:17 cannot-verify `exit 95`->`physical=/` `192 passed` while a chmod 000 toolchain parent then exits `0` (tip `95`). Blocking (same class as B2, B3).
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): (a) without pipefail the overflow pipeline exits `0`; with pipefail `97`. (b) SEEDS RED, cmp 0 each: run.sh:25 mktemp `exit 98`->`exit 0` `1 failed`; run_capture.py:95 write guard `return capture_failed(exc)`->`pass` `2 failed`; run.sh:6 `exit 96`->`exit 0` `2 failed`; run.sh:20 cannot-verify `exit 95`->`;;` `2 failed`; run_capture.py:101 cap `os.killpg`->`child.kill()` `1 failed`. Probes: `ulimit -f 1` 200000 and 4096 bytes -> `98` `[Errno 27] File too large`. (c) SEED config.py:71 missing-file branch -> `3 failed, 27 passed`. (d) SEED runlog.py:92 card filter -> `1 failed, 41 passed`.
- [x] R1-14. Codex workspace-write cannot write `.git` (`index.lock: Operation not permitted`); the chair
  commits every Codex item after re-running its CHECKs. -> process note, Librarian.
  Verifier (blind, 2026-10-26, tip 9c25e8f): ticked on reading the record: agent-log row 4 `uncommitted (sandbox denies .git), chair committed`; every build commit 7fd2913..9d05301 is by the chair. Process note; Librarian entry is R1-12's.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds on the record (process note); no code claim to re-run.
- [x] R1-15. Q18's `allowLocalBinding` did not take effect mid-session; socket tests ran outside the
  sandbox. -> confirm in a fresh session.
  Note (chair, session 2, fresh session): `scripts/run.sh pytest -q -m socket` inside the sandbox -> `5 passed, 93 deselected`; the setting takes effect at session start.
  Verifier (blind, 2026-10-26, tip 9c25e8f): fresh session, inside the sandbox: `scripts/run.sh pytest -q -m socket` -> `5 passed, 157 deselected in 2.76s`.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds: full suite inside the sandbox `233 passed` (socket tests included); driven doctor bound `127.0.0.1:51384` inside the sandbox.
- [x] R1-16. Toolchain inside the checkout broke the strict privacy row (4 idlelib PNGs under `.uv/`);
  fixed by D23 (commit 9d05301), seed `toolchain_inside_repo=1` red per Codex. -> verifier re-seeds.
  Verifier (blind, 2026-10-26, tip 9c25e8f): SEED run.sh:5 `UV_CACHE_DIR="$ROOT/.uv/cache"` -> `AssertionError: toolchain_inside_repo=1`, restored cmp 0; ignored-file scan proven by `state/probe-seed.HEIC` -> privacy offender (R1-10).
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds: default toolchain `~/.casefile-dev/legal-harness/venv` (probe with `CASEFILE_TOOLCHAIN=` empty made `/Users/davidskoranski/.casefile-dev/legal-harness/venv`); gate privacy `offenders=0 scanned=247`.
- [x] R1-17. Process slip: the chair committed loop records (3e12678) while a Codex lane was live in the
  main tree (catalog #53); disjoint files, no conflict. -> Librarian.
  Verifier (blind, 2026-10-26, tip 9c25e8f): ticked on reading the record: `git show --stat 3e12678` touches only ledger, spec, loop records and `.claude/settings.json`, no src or tests. Process note.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds on the record (process note).
- [x] R1-18. Built in four Codex batches (A1, A2+B, A3, F1) instead of one run per item, to save chair
  usage. -> process note.
  Verifier (blind, 2026-10-26, tip 9c25e8f): ticked on reading the record: agent-log rows 4 to 8 (A1, A2, lane B, A3, F1). Process note.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): still holds on the record (process note).

- [~] R1-19. CX-9's real OCR smoke test (ocrmypdf on an invented fixture PDF) is stage 3 work (Q11);
  cycle 1 makes check_ocr honest ("versions only"). -> carry to the stage 3 brief.
  deferred: carried (chair, 2026-10-26)

## Round 1 critic round (session 2, 2026-10-26)
- 8a Codex code review (gpt-6.1-sol, read-only): 11 findings, 2 high, 8 med, 1 low; all 11
  REPRODUCED by the chair (`docs/loop/round-01/round01-codex-review.md`). Librarian R01-CX-1 to CX-11.
- Fix cycle 1 (Codex gpt-6.1-sol builder, Q22): CX-1 to CX-11, commit 28a5f96. Chair re-run:
  `150 passed`, gate `0`; chair repros all clear (CX-1 ConfigError, CX-3 `runlog is append-only`, CX-4
  `exit=97 secs=0`, CX-6 `scan=['Cases']`, CX-7/CX-8 caught); chair SEED drop done_reason guard
  (doctor.py:126) -> `1 failed, 32 passed`, restored by cmp. Chair found the CX-7 fix over-blocked
  benefits prose; follow-up narrowed it to one clause, 60 chars (T-5). run.sh now execs
  `scripts/run_capture.py` (needs a python3 on PATH before `uv sync`).

- 8b output critic (fresh Opus 5.5): `OUTPUT CRITIC 5/10 · high 3 · med 8 · low 3`
  (`docs/loop/round-01/round01-critic.md`). Chair reproduced H2 (7 of 7 DME/IME forms missed), H3 (6 of 6
  false hits), M2 (bad example `[]` as text), M5 (ranges and lists rejected), M8 (config-dir limit from
  cycle 1's CX-1 instruction, chair's own error). Owner questions 8 to 14 held with interim rulings.
- Fix cycle 2 (Codex): H1, H2, H3, M1 (partial), M2, M3, M5, M6, M7, M8, L1, L2. Carried: M4 (unbracketed
  cites, to the stage that writes cited text) as R1-20; L3 (gate selftest breadth is the rules suite).
  Done: chair re-run `162 passed`, gate `0`, critic repros clear (H2 missed `[]`, H3 false hits `[]`, M5 `[]`);
  doctor with no server: `failed=4 of 8`, exit 1, every FAIL line has `| do:`.
- Cycle budget (Q5): 8a fixes = cycle 1, critic fixes = cycle 2; one cycle left for the verifier's findings.
- [~] R1-20. Critic M4: `bates-cites` sees only bracketed cites; "(Ex. 3 at 12)" and "See page 12" pass.
  -> brief of the stage that generates cited prose.
  deferred: carried (chair, 2026-10-26)

- 8c blind verifier (fresh Opus 5.5): FAIL, 14 ticked, 4 deferred, 2 refused (B1 R1-4, B2 R1-13);
  `docs/loop/round-01/round01-verify.md`. Chair reproduced B1 (`exit=0`, want 2).
- Fix cycle 3 (Codex, last allowed): B1, B2, S2, S6, S9, S10, N1 to N3; spec D12 and D18 amended
  (chair rulings, pending veto). Commit f2023ae. Chair re-run `184 passed`, gate `0`, B1 `exit=2`,
  missing command `127`; SEED run_capture.py:13 `return 98` -> `return 0` -> `5 failed, 13 passed`, cmp, `18 passed`.

- 8c re-verifier (fresh Opus 5.5): FAIL on B1b (R1-4) and B3 (R1-13); chair reproduced B1b (`exit=0`).
  Owner Q23: one extra cycle.
- Fix cycle 4 (Codex, Q23): B1b and B3. Chair re-run `192 passed`, gate `0`, B1b `exit=2`, toolchain alias
  `exit=95`; SEED run_capture.py:46 `return capture_failed(exc)` -> `pass` -> `2 failed, 21 passed`, cmp, `23 passed`.

- 8c focused re-verify (fresh Opus 5.5, Q23): FAIL, V3-1 to V3-4 (`round01-verify3.md`); chair reproduced
  V3-2 (`CASEFILE_TOOLCHAIN=<scratch>/nope/../../../../../<checkout>` -> `exit=0`, want 95).
- Round 1 verdict: DISCARDED per Q23/Q5, not merged (Q24: re-brief on the branch). R1-4 and R1-13 refused;
  V1 not ticked. Carried to the re-brief: V3-1 to V3-4, verify2 N2 (non-blocking), R1-12 (spec §11 as-built,
  written at the merge).

- [~] R1-21. Spec §8b (owner, 4614a1e) labels its decisions D12 to D16, which collide with §9 rows D12 to D16
  (round 1 rulings). -> owner question 15; chair does not edit the owner's section.
  deferred: owner question 15 (chair, 2026-10-26)

## Round 1 re-brief (Q24, Q26; opened 2026-10-26 on `loop/round-01` at 3502fc5)
- [x] R1-22. One shared path-identity check (Python) used by config.py and scripts/run.sh: matters and
  toolchain refused when inside the checkout by any alias; V3-1 (symlink loop exits 2, ConfigError),
  V3-2 (`..` toolchain exits 95, nothing created), V3-4 (cannot-verify branch tested); table-driven
  alias tests shared by both callers.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): matters through `scripts/run.sh casefile config show` (S=`/private/tmp/claude-501/v4r`, 5 levels deep): case-swapped checkout, symlink to root, symlink to case-swapped `LEGAL-HARNESS/Tests/Fixtures`, chain `c2 -> c1 -> Legal-Harness/src`, relative symlink `../../../../Users/davidskoranski/LEGAL-harness`, dangling into `LEGAL-HARNESS/no-such-dir`, `$S/nope/` plus five `..` to the checkout, the same via `/tmp/...`, `ltests/../inv`, `ltests/nope/../../inv`, `<checkout>/nope/../../elsewhere`, trailing slash (bare and via symlink), `~/legal-harness/inv`, `~davidskoranski/LEGAL-HARNESS/inv`, `/.vol/<dev>/<ino>/inv`, `/System/Volumes/Data` firmlink: all exit `2` `must be outside the checkout`; loop `loopA -> loopB -> loopA` exit `2` `cannot verify ... [Errno 62]` (V3-1); chmod 000 ancestor exit `2` `cannot verify ... [Errno 13]`; `~root/inv` exit `2` cannot verify; `~nosuchuserxyz` exit `2` `unknown user`; relative and `./` exit `2` `must be an absolute path`; control one `..` short -> `/private/Users/...` exit `0`; outside existing and new exit `0`. Toolchain through `scripts/run.sh sh -c 'mkdir -p "$UV_PROJECT_ENVIRONMENT"'`: literal, case, symlink to root, symlink to case-swapped subfolder, chain, relative symlink, dangling, `..` at the right depth (both `/private/tmp` and `/tmp` spellings, V3-2), `ltests/nope/..`, `ltests/../x`, trailing slash, `/.vol`, firmlink, and `venv`, `venv/bin`, `cache` children symlinked into the checkout: all exit `95`, nothing created (`<checkout>/legal-harness` absent); loop and chmod 000 exit `95` `cannot verify` (V3-4); relative `rel-tc`, `~/x` and `../y` from inside the checkout or a symlinked cwd exit `95`; outside exit `0`. SEEDS: pathguard.py:54 judge only the first path -> venv-child probe exits `0`, `5 failed, 38 passed`, cmp 0; run.sh:20 cannot-verify -> `;;` `2 failed`, cmp 0. GREEN (finding, non-blocking, tip correct): pathguard.py:55 drop the newline join -> `233 passed` while `CASEFILE_TOOLCHAIN=$'<checkout>/q\npathguard outside z'` then runs the command with exit `0` (tip: `95`); the one-line verdict protocol is untested.
- [x] R1-23. One test per D12 exit branch (96, 97 incl. grandchild killed, 98 mktemp and write, 95,
  126, 127, child code); V3-3; verify2 N2.
  Build note (re-brief, Sonnet 5.5, commits 330ff81..a69814d; chair re-run, not a tick): `214 passed`;
  gate `0` on three runs (one earlier run printed `1`, row not captured: tripwire for the verifier);
  wrapper and pathguard tests `43 passed` x4; V3-1 loop -> `exit=2` ConfigError; V3-2 at the right
  depth -> `exit=95`, nothing created; B1b `exit=2`; outside `exit=0`; chair SEED run.sh inside branch
  -> `;;` -> `10 failed, 27 passed`, cmp restored, no residue. Builder deviations 1 to 7 accepted
  (6: suite 12.9 s -> 32 s, over the brief's 20 percent R5 line; accepted as the cost of real
  interpreter and grace tests, T-6).
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): every D12 branch probed (TMPDIR=`$S/tx`, capture folders counted): no args `96` (also with an inside toolchain); inside `95`; cannot-verify `95`; mktemp `98`; capture write `98` (200000 and 4096 bytes under `ulimit -f 1`); missing `127`; non-executable file and directory `126`; cap `97`, `52428800` bytes, `secs=0.45`, grandchild `dead`; held pipe `exit 3` -> `3` `secs=2.09`, `kill -KILL` -> `137` `secs=2.09`, holder `dead`; escaped (setsid) holder -> `4` `secs=2.16`, holder alive as D12 says; self-stop then CONT -> `5` `secs=1.41`; HUP `129`, TERM `143`, INT `130`, each `secs=0.21`, child `dead`, capture folders `1` during and `0` after; child `3`, `0`, self-SIGTERM `143`. SEEDS RED (cmp 0 each): run.sh:6 `exit 96`->`0` `2 failed`; run_capture.py:101 killpg->`child.kill()` `1 failed`; run_capture.py:96 write the whole chunk -> `52428801` bytes, `2 failed`; run_capture.py:129 drop `shutil.rmtree` `9 failed`.

- Re-brief 8a Codex code review: 8 findings (1 high, 4 med, 3 low), RX-1 reproduced at runtime (stop and
  continue -> `exit=137 secs=2`). Fix cycle 1 (Sonnet, Q27, 22d0125): kqueue NOTE_EXIT replaces SIGCHLD
  and select; run.sh execs the guard's python3. Chair re-run `223 passed`, gate `0`, RX-1 probe `exit=3
  secs=4`, held pipe `exit=3 secs=3`, `run.sh false` -> 1. Carried low: state/playbook expanduser in
  config.py can still traceback on a bad `~user` (fails closed, exit 1).

- Re-brief 8b output critic (fresh Opus 5.5): `OUTPUT CRITIC 7/10 · high 0 · med 2 · low 4`
  (`round01r-critic.md`); chair reproduced F1 (HUP -> exit 129, capture folder left). Owner questions 19, 20.
- Re-brief fix cycle 2 (Sonnet, 9f86d07): F1 to F6. Chair re-run `233 passed`, gate `0`, HUP -> `exit=129`,
  capture folders `before=13 after=13`; F3 message names path and fix. Chair could not delete 13 older
  capture folders in the shared TMPDIR (classifier denied); they hold invented test output only.

  R1-12 (chair at close, 2026-10-26): spec §11 as-built row for stage 1; §9 D12, D13, D18, D23 amended and
  D24 added (pending veto); Librarian round 1 entries; agent log; reports `round01-report.md`.
- Carried to round 2 (non-blocking, from the final verifier): VF-1 newline join at pathguard.py:55 has no
  test (tip correct, exits 95); VF-2 config.py:67 and :145 traceback on `--config` through a loop and on a
  bad `~user` or loop in state/playbook (refuses, exit 1, not ConfigError).

- [x] V1. Fresh blind verification: every non-deferred R1 item `[x]` with the verifier's own evidence.
  Verifier 2 (blind, 2026-10-26, tip c997bc1): not ticked; R1-4 and R1-13 refused. `docs/loop/round-01/round01-verify2.md`.
  Verifier 3 (blind, focused per Q23, 2026-10-26, tip 6db09cb): not ticked; R1-4 and R1-13 refused. `docs/loop/round-01/round01-verify3.md`.
  Verifier 4 (blind, re-brief, 2026-10-26, tip 4db60e2): every non-deferred item R1-2 to R1-23 is `[x]` with this verifier's evidence (R1-1, R1-12, R1-19, R1-20, R1-21 deferred). `docs/loop/round-01/round01r-verify.md`.

## Round 2: stage 2 benchmark and invented test matter (opened 2026-10-26 on `loop/round-02` at b167fbd)
Tiers: Q28 (Gemma 4 e4b codes, Opus orchestrates, Codex reviews, extra Fable code review, Sonnet fallback).
Exit test (spec §7 stage 2): `casefile bench` scores the invented test matter against its answer key.
- [x] R2-1. VF-1: a test that the newline join at pathguard.py:55 is load-bearing (seed: drop the join
  -> red).
  Build note (orchestrator, 2026-10-27): 94f6a3b, Gemma G1. `newline_join_exit=95 verdict_lines=1`, exit 0;
  seed (join dropped) -> `newline_join_exit=0 verdict_lines=0`, exit 1; restored by cmp.
    Verifier (blind, round 2, 2026-10-27, tip 2099304): `newline_join_exit=95 verdict_lines=1`, `2 passed`;
    join dropped -> `verdict_lines=2`, `newline_join_exit=0 verdict_lines=0`, `2 failed`; restored, cmp ok.
- [x] R2-2. VF-2: config.py:67 and :145 refusals raise ConfigError (exit 2), never a traceback.
  Build note: cad2779, Gemma G2 (FUNCTION splice, diff only the two sites) and G3. `resolve_refused=4 of 4
  cli_exit=2`, exit 0; seeds a and b -> `RuntimeError: Symlink loop`, exit 1; restored by cmp.
    Verifier (blind, round 2, 2026-10-27, tip 2099304): `resolve_refused=4 of 4 cli_exit=2`, `1 passed`; RuntimeError
    dropped from config.py:69 and :150 each -> `RuntimeError: Symlink loop`, `1 failed`; restored, cmp ok.
- R2-3. Stage 2 work items (brief `docs/loop/round-02/round02-build-brief.md`, ruled by the chair 2026-10-26:
  all §1 decisions 1 to 18 accepted; D25 and D26 in spec §9, pending veto):
- [x] R2-3a. W3 quote normalisation and matter loader (11 refusals) and W4 invented matter 9001.001 (14 pages).
  Build note: d1fd758 (W3: `quotes_ok=8 of 8`, `matter_pages=3 refusals=11 of 11`; seeds a to d red) and
  3d095c0 (W4: `fixture_pages=14 binders=3`; stamp seed -> `last line is not a Bates stamp`). Every page
  read against the bible; ten pages corrected by feedback (names, dates, unplanned conflicts).
    Verifier (blind, round 2, 2026-10-27, tip 2099304): `quotes_ok=8 of 8`; `matter_pages=3 refusals=12 of 12` (not
    11: the twelfth is fix cycle 1's CX-7 case; dropping UnicodeDecodeError from matter.py's toml except fails
    test_matter::test_refusals); `fixture_pages=14 binders=3`. Ledger number not amended for the 12th: drift only.
- [x] R2-3b. W5 answer key loader and `key.json` (26 facts, 5 flags), validated against the pages.
  Amended by fix cycle 2 (OR-7): the key holds 29 facts and 6 flags (F27 to F29, G6 added); key collisions
  refused (fix cycle 1, R2-CX-5).
  Build note: b553411, Gemma G23 to G26. `key_refusals=10 of 10`, `key_facts=26 flags=5 pages=14`,
  firm rules over the key's prose `[]`; seeds a (found_in dropped) and b (one quote character) red.
    Verifier (blind, round 2, 2026-10-27, tip 2099304): `key_facts=29 flags=6 pages=14`; `key_refusals=12 of 12` (10
    plus the two CX-5 collision cases; not amended in the ledger: drift only); key G6 = conflict MED0007,DEF0002,
    F27 MED0008, F28 DEF0003, F29 MED0003 as OR-7 says; fact-collision check disabled -> test_key_refusals red.
- [x] R2-3c. W6 candidate parser and scorer; `flawed.json` scores exactly `found=23 of 26 missed=3
  invented=2 extra=2 flags=4 of 5 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14`.
  Build note: 09ad98a, Gemma G27 to G32. `candidate_refusals=7 of 7`, `score_cases=11 of 11`, perfect and
  flawed lines exact; seeds a to e red (d fails with KeyError, not `6 of 7`).
  Amended by fix cycle 2 (OR-7): flawed now scores exactly `found=26 of 29 missed=3 invented=2 extra=2 flags=5 of 6
  flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14` (exit 1) followed by detail lines naming the missed
  facts, invented facts, missed and extra flags and rule hits; ideal `found=29 of 29 ... extra=2 flags=6 of 6 ...`
  (exit 0).
    Verifier (blind, round 2, 2026-10-27, tip 2099304): `scripts/run.sh casefile bench --matters tests/fixtures/matters
    --config config.example.toml --candidate tests/fixtures/bench/flawed.json` -> `bench 9001.001 found=26 of 29
    missed=3 invented=2 extra=2 flags=5 of 6 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14` then
    `  missed: F04 F15 F24`, two `  invented:` lines (MED0003 "80 pounds" is on no page; MED0099 is not a page),
    `  flags_missed: G3`, `  flags_extra: conflict MED0001,MED0004`, `  rules: no-dme-ime DEF0003`, exit 1; ideal
    -> `found=29 of 29 ... extra=2 flags=6 of 6 ... rules=0 pages_failed=0 of 14`, exit 0; `candidate_refusals=7
    of 7`, `score_cases=11 of 11`. Unseeded test gaps (code correct by direct probe): V2-S2 (cite not compared)
    and V2-S5 (duplicate extra flag) stay green; see round02-verify.md.
- [x] R2-3e. W7 `ModelError.raw` and the stage 2 runner (counts gate, every received reply an answer row).
  Build note: afed11b, Gemma G33, G34. test_model.py green, `card_version=092368692dd3`; model.py diff is
  `__init__` plus the five raw raises; seed W8 e (raw dropped) -> `answers_failed=5`, exit 1.
    Verifier (blind, round 2, 2026-10-27, tip 2099304): REFUSED. `card_version=092368692dd3` and test_model `16
    passed` reproduce, and every 200 reply gets a row; but a received non-200 reply gets none: stand-in serving a
    different model tag -> `probe404 failure= bench.model: status=404: b'{"error": "fakemodel: unknown model"}'`,
    `probe404 answers= 0 failures= 1` (model.py raises without `raw` at `status != 200` and on HTTPError). Finding
    V2-F1. Also V2-S4: done_reason missing accepted as stop is untested (seed green).
    Verifier 2 (blind, round 2, 2026-10-27, tip b875949): REFUSED, narrowly. 19 received replies through the
    stand-in each give exactly one row and one failure (`probe_d25 cases=20 bad=1`): 404, 500, 503 empty, 502
    html, 201, non-JSON 200, JSON array, bad UTF-8, truncated, done false, no done_reason, eval 0, eval -3,
    prompt "12", prompt 12.0, eval true, no message, malformed answer -> one `failed` row holding the body, and
    a good reply -> one `ok` row. But a received 3xx reply stores none, through the real opener on a loopback
    socket: `real_opener status=302 answers=[] failures=['bench.model'] failure='bench.model: redirect refused:
    302 to http://127.0.0.1:9/x'` (307 the same; 404 on the same server -> one row). model.py:18, :50, :54
    raise without `raw`. Finding V2b-F1; OR-8 rules "every received reply, any status, is stored".
    Verifier 3 (blind, round 2 extra cycle, 2026-10-27, tip 695b97b): TICKED. Own probe on matter 9001.001,
    loopback server, real opener: 302, 307, 301, 303, 308 and a 302 with an empty body each give exactly one
    `failed` row holding the body and one `bench.model` failure `redirect refused: ...`, redirect target hit 0
    times; 404 and 503 one `failed` row each; 200 one `ok` row. Transports returning 302/307 and raising
    HTTPError 302/307: one row with the body each (`probe_v3 bad=0 runs=13 answers=13 target_hits=0`).
- [x] R2-3d. W8 stand-in bench recording and runner tests (`benchrun_modes=7 of 7`).
  Build note: afed11b, Gemma G35 to G38. `bench_recording_ok=1 modes=4 pages_in_request=14`,
  `benchrun_modes=7 of 7 answers_ok=1 answers_failed=6 failures=6`; seeds a to f red (a and d via
  AttributeError on a None failure, not `6 of 7`).
    Verifier (blind, round 2, 2026-10-27, tip 2099304): `bench_recording_ok=1 modes=4 pages_in_request=14`,
    `benchrun_modes=7 of 7 answers_ok=1 answers_failed=6 failures=6`; my seed (exc.raw stored as `str()` not JSON)
    -> `benchrun_modes=6 of 7`, `1 failed, 2 passed`; restored, cmp ok.
- [x] R2-3f. W9 `casefile bench` CLI (exit 0 perfect, 1 imperfect, 2 cannot run).
  Build note: 31a3a9e, Gemma G39 to G41. `bench_exit_perfect=0 bench_exit_flawed=1 bench_exit_badkey=2
  bench_exit_noconfig=2 bench_exit_nolog=2`; standing command status 0 and 1; seeds a to d red.
    Verifier (blind, round 2, 2026-10-27, tip 2099304): `bench_exit_perfect=0 bench_exit_flawed=1 bench_exit_badkey=2
    bench_exit_noconfig=2 bench_exit_nolog=2`; standing commands exit 0 (ideal) and 1 (flawed); two-matter probe
    (first fails, second perfect) -> `exit=1`, `bench matters=2 imperfect=1`. Unseeded gaps: V2-S1 (discovery)
    and V2-S6 (`imperfect +=` -> `=`, probe exit 0) stay green; cli.py arg swap seed red.
- [x] R2-3g. W10 stage 2 exit test (`stage2 exit=0 ... server_stopped=1`) and W11 prose gate on fixtures.
  Build note: 0d922ed (W10: `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`, control
  `stage2-control exit=0 runs=+1 answers_ok=+1`; seeds a, b red) and 4f03e69 (W11: gate `0`, `gate prose PASS
  dashes=0 files=122`; em dash seed -> `dashes=1`). b6a9624 replaced 7 dashes in the Codex review record
  (the gate printed 1 at 600ad8f): orchestrator deviation.
    Verifier (blind, round 2, 2026-10-27, tip 2099304): `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`,
    perfect line, `stage2-control exit=0 runs=+1 answers_ok=+1`, `2 passed`; gate exit 0, `gate prose PASS dashes=0
    files=129` (files grew since 4f03e69); em dash appended to key.json -> `gate prose FAIL dashes=1 files=129`;
    restored, cmp ok. `python -m tests.fakemodel --bench-matter` + `casefile bench` -> perfect line, exit 0, run
    log 1 run (bench.extract, 092368692dd3, pages_in 14) and 1 ok answer row; listeners 0 after.
- [x] R2-4. Regression baselines set in `## Project` from measured numbers (chair, 2026-10-27, from verifier 3's
  regression set and the chair re-run at 695b97b).
- [x] R2-5. Close: report, Librarian, agent log, spec §11 as-built, handoff, next-round prompt (chair, 2026-10-27).
- [x] V2. Fresh blind verification: every non-deferred R2 item `[x]` with the verifier's own evidence.
    Closed by verifier 3's V2 under "Round 2 extra fix cycle" (R2-3e, R2-8, R2-9 ticked; the rest by verifier 1).
    Verifier (blind, round 2, 2026-10-27, tip 2099304): NOT ticked. R2-3e refused (V2-F1: a received non-200
    reply gets no answer row). All other items `[x]`. Report: docs/loop/round-02/round02-verify.md.
    Verifier 2 (blind, round 2, 2026-10-27, tip b875949): NOT ticked. R2-3e and R2-8 refused on V2b-F1 (a received
    3xx reply stores no answer row). `269 passed in 37.28s`; gate prints `0` (`gate prose PASS dashes=0
    files=136`); stage 1 `2 passed`, stage 2 `stage2 exit=0 runs=+1 answers_ok=+1`, `2 passed`; flawed bench
    exit 1, ideal exit 0. New seeds: N1, N6 red; N2, N3, N4, N5 green, code right by probe (non-blocking).
    Report: docs/loop/round-02/round02-verify2.md.
- PAUSED (owner, 2026-10-26, "Pause local work") after G7. Committed: W1 94f6a3b, W2 cad2779. Uncommitted
  Gemma output left in the tree: src/casefile/quotes.py, src/casefile/matter.py, tests/test_quotes.py,
  tests/test_matter.py (W3 CHECK green, seeds a to d not run). Resume at: W3 seeds and commit, then G8.
- RESUMED 2026-10-27; build G1 to G43 done, all W CHECKs and seeds red-then-green; no Sonnet fallback.
  Report: docs/loop/round-02/round02-build-report.md; tally docs/loop/round-02/round02-gemma-tally.md.
- Chair re-run of the build (2026-10-27, tip dff4707): `253 passed in 36.89s`; gate `0`; stage 2 exit
  `stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1` and the perfect line; `casefile bench --config
  config.example.toml --candidate flawed.json` -> the flawed line, exit 1; ideal -> perfect line, exit 0.
  Chair seeds: quotes.py:15 drop `bool(quote) and` -> `1 failed`, cmp ok; benchscore.py:37 drop `rules == 0`
  -> `1 failed`, cmp ok; benchrun.py:43 `c > 0` -> `c >= 0` -> GREEN (`1 passed`): zero token counts are
  accepted untested. -> finding R2-CH-1 for fix cycle 1.
- 8a Codex code review (2026-10-27, `round02-codex-review.md`): 7 findings, all reproduced or traced by the
  chair. Driver (loop tooling, chair-owned): CX-1 proxy honoured, CX-3 symlink target, CX-4 FILE answer on a
  function task -> fixed by the chair in scripts/gemma_task.py and proven on fake answers (link refused,
  nothing written; mixed answer writes nothing; FILE on function task exit 4; opener has no proxy). App, for
  fix cycle 1 (Gemma): R2-CX-5 key collisions (repro: duplicate fact F99 -> `found=26 of 27`, never
  perfect); R2-CX-6 non-JSON 200 reply gets no answer row (traced model.py:62-65, no `raw`); R2-CX-7 bad
  byte in matter.toml -> `UnicodeDecodeError`, exit 1 (repro, D25 wants 2); R2-CH-1 zero token counts.
  R2-CX-2 (prompt truncation not detected: spec §4 gate 1 "read as many tokens as were sent"): deferred to
  stage 4 (model client and gates) by the chair, OR-4, pending veto.
- Fable code-quality review (Q28, `round02-fable-review.md`): fit to merge after fixes; Gemma 7/8/7/5 vs
  Sonnet control 7/9/7/9 (correctness, brief fidelity, test strength, readability); no high; F1 = CX-5,
  F1b = CX-7 (both builds); F2 `from exc`. Rulings OR-5.
- [x] R2-6. Fix cycle 1 (Gemma, Opus orchestrating): R2-CH-1, R2-CX-5, R2-CX-6, R2-CX-7, F2; each seed red
  before the fix, green after.
    Verifier (blind, round 2, 2026-10-27, tip 2099304): each fix reverted one line at a time, targeted tests:
    CH-1 `c >= 0` -> test_benchrun_zero_counts `1 failed`; CX-6 `raw` dropped from model.py non-JSON raise ->
    test_benchrun_unparsed_reply `1 failed`; CX-7 UnicodeDecodeError dropped -> `2 failed`; CX-5 fact collision
    off -> test_key_refusals `1 failed`; F2 `from exc` dropped (records) -> test_records_missing_chains `1 failed`;
    all restored, cmp ok. CLI: 0xff in matter.toml -> `MatterError ... can't decode byte 0xff`, exit 2; duplicate
    fact F99 -> `BenchKeyError ... fact F99: same cite and quote as fact F01`, exit 2. Note CX-6 covers 200 only:
    see V2-F1 under R2-3e.
  Note (fix cycle 1, 2026-10-27, not a tick: the verifier ticks): all five red then green; commits 9c82349
  R2-CH-1, 0f2022d R2-CX-5, ba24d90 R2-CX-6, 408991c R2-CX-7, 365f1e0 F2; `260 passed`, gate `0`; Gemma 11
  tasks, 14 calls, no fallback. Report: docs/loop/round-02/round02-fix1-report.md.
  Chair re-run after fix cycle 1 (tip 0025bb9): `260 passed in 37.62s`; gate `0`; CX-7 repro (0xff in
  matter.toml) -> exit 2 `MatterError ... can't decode byte 0xff`; CX-5 repro (duplicate fact F99) -> exit 2
  `BenchKeyError ... fact F99: same cite and quote as fact F01`; CH-1 seed `c >= 0` -> `1 failed, 2 passed`,
  restored, cmp ok. Gemma: 11 tasks, 14 calls, 8 first try, 0 fallbacks.
- 8b output critic (`round02-critic.md`): `OUTPUT CRITIC 6/10 · high 2 · med 5 · low 6`. Chair verified H1
  (radiculopathy conflict MED0007 vs DEF0002 missing; a correct model fails on flags_extra) and H2 (MED0008
  restriction, DEF0003 "No further treatment", MED0003 "likely work related" unkeyed). Rulings OR-7; owner
  questions 24 to 29.
- [x] R2-7. Fix cycle 2 (Gemma): key G6, F27 to F29, ideal and flawed updated, exact numbers updated; bench
  prints missed, invented, flag and rule detail (critic M1).
    Verifier (blind, round 2, 2026-10-27, tip 2099304): key holds G6 conflict MED0007,DEF0002 and F27 to F29;
    ideal -> `found=29 of 29 ... flags=6 of 6 flags_missed=0 flags_extra=0 rules=0`, exit 0, no detail lines;
    flawed -> the amended line, exit 1, six detail lines (`bench_detail_flawed exit=1 detail_lines=6`, quoted
    under R2-3c); truncated stand-in run -> `missed: F01 ... F29`, `flags_missed: G1 G2 G3 G4 G5 G6`, exit 1.
    `263 passed in 37.27s`, gate exit 0.
  Note (fix cycle 2, 2026-10-27, not a tick: the verifier ticks): items 1 to 4 red then green at 6c1968c
  (perfect `found=29 of 29 ... flags=6 of 6 ... rules=0`, exit 0; flawed `found=26 of 29 missed=3 invented=2
  extra=2 flags=5 of 6 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14`, exit 1); M1 detail lines
  at d007821 (`  missed: F04 F15 F24` ... `  rules: no-dme-ime DEF0003`); `263 passed`, gate `0`; Gemma 11
  tasks, 11 calls, all first try, no fallback. Report: docs/loop/round-02/round02-fix2-report.md.
  Chair re-run after fix cycle 2 (tip 0d5e0a0): `263 passed in 36.86s`; gate `0`; flawed bench exit 1 with
  the amended line and six detail lines; ideal exit 0 `found=29 of 29 ... flags=6 of 6`; listeners 0.
- [x] R2-8. Fix cycle 3 (Gemma; OR-8): V2-F1 (non-200 replies stored as failed answer rows with the body)
  and tests that turn the verifier's seeds S1, S2, S4, S5, S6 red.
  Note (fix cycle 3, 2026-10-27, not a tick: the verifier ticks): V2-F1 RED on e637357 (`assert [] ==
  [('failed', '...own model"}')]`), GREEN at 81c78ce (model.py passes the whole decoded body as `raw` at
  both non-200 sites; seeds at each site and a 200-byte excerpt seed red, cmp ok). Seed tests, each green
  on the tip and red under the verifier's exact mutation, cmp ok: S1 a1af3ac, S2 f2148ca, S4 12876e9, S5
  73baa0c, S6 1e84c60. `269 passed in 37.13s`, gate `0` (`files=135`); Gemma 7 tasks, 8 calls, no
  fallback. Report: docs/loop/round-02/round02-fix3-report.md.
  Chair re-run after fix cycle 3 (tip 64231af): `269 passed in 36.54s`; gate `0`; seed model.py status!=200
  site drops raw -> `1 failed, 3 passed`, cmp ok; seed V2-S2 (drop cite clause) -> `1 failed, 268 passed`,
  cmp ok. (A first chair seed did not apply, raw being positional; caught by `cmp -s`, not counted.)
    Verifier 2 (blind, round 2, 2026-10-27, tip b875949): REFUSED on the first clause only (V2b-F1: a 302 or 307
    reply is a non-200 reply and stores no answer row; see R2-3e). The rest reproduces: model.py raw dropped at
    the HTTPError site -> `1 failed, 268 passed`, at `status != 200` -> `1 failed, 268 passed`; each of the five
    seeds applied (`cmp -s` differed) and turned its own test red: S1 test_bench_discovery `1 failed`, S2
    test_benchscore_cite `1 failed`, S4 test_benchrun_done_reason `1 failed`, S5 test_benchscore_flag_dedupe
    `1 failed`, S6 test_bench_multi `1 failed`; all restored, `cmp` ok.
    Verifier 3 (blind, round 2 extra cycle, 2026-10-27, tip 695b97b): TICKED. The refused first clause now holds:
    every non-200 reply in my probe, 3xx included, stores one `failed` row with the body (`probe_v3 bad=0`, see
    R2-3e). Non-200 sites seeded again: model.py:60 raw dropped -> `1 failed, 269 passed`; model.py:64 raw
    dropped -> `1 failed, 269 passed`; both applied (`cmp -s` differed) and restored (`cmp` ok).
- Round 2 verdict (chair, 2026-10-27): HELD at the fix-cycle cap (Q5). Verifier 2 FAIL on V2b-F1 (3xx replies
  store no answer row). Not merged; owner question 30 (recommend one extra cycle limited to V2b-F1, Q23
  precedent). Report `docs/loop/round-02/round02-report.md`.

## Round 2 extra fix cycle (Q32, 2026-10-27)
- [x] R2-9. V2b-F1: every received 3xx reply is stored as a failed answer row holding its body, on all three
  refusal paths (model.py:18 `NoRedirect.redirect_request`, :50 status 3xx returned, :54 HTTPError 3xx);
  the refusal itself stays (D21). CHECK: `pytest -q tests/test_benchrun.py` passes and the new 3xx test
  fails when the `raw` argument is dropped at any one of the three raises (three seeds, each RED alone).
  Note (extra fix cycle, 2026-10-27, not a tick: the verifier ticks): 695b97b, Sonnet (Q33). New
  test_benchrun_redirect_reply red on the unfixed model.py (`1 failed`); builder seeds at :18, :50, :54 each
  red alone, cmp ok; chair seed at :18 (real opener path) -> `1 failed`, cmp ok; `270 passed in 36.99s`;
  gate `0` (`gate prose PASS dashes=0 files=138`).
    Verifier 3 (blind, round 2 extra cycle, 2026-10-27, tip 695b97b): TICKED. `pytest -q tests/test_benchrun.py`
    `5 passed`; raw dropped at each of model.py:19, :52, :58 alone -> `1 failed, 4 passed`, cmp ok each. Own
    seeds off those lines, each applied and restored (cmp ok): benchrun.py:71 status ok -> `1 failed` (redirect
    test); benchrun.py:70 always json.dumps -> `1 failed`; model.py:50 `300 <=` to `303 <=` -> `1 failed`;
    model.py:23 NoRedirect dropped -> `1 failed` (probe: target hit 4 times). Refusal stays: redirect target hit
    0 times in my probe. Gap, non-blocking: benchrun.py:69 `is not None` -> truthiness stays green (no 3xx
    empty-body case in the test); code right by probe (empty 302 -> one row `''`).
- [x] V2. Focused fresh blind re-verify of R2-9 and the regression set (269+ passed, gate 0, bench lines).
    Verifier 3 (blind, round 2 extra cycle, 2026-10-27, tip 695b97b): TICKED. R2-3e, R2-8, R2-9 `[x]`.
    `270 passed in 36.71s`; gate prints `0` (`gate prose PASS dashes=0 files=138`); stage 1 and 2 exit tests
    `4 passed` (`stage2 exit=0 runs=+1 answers_ok=+1 server_stopped=1`); flawed bench exit 1 `found=26 of 29
    ... flags=5 of 6` with six detail lines; ideal (tests/fixtures/matters/9001.001/ideal.json) exit 0
    `found=29 of 29`. Report: docs/loop/round-02/round02-verify3.md.
- Round 2 verdict (chair, 2026-10-27): PASS after the extra fix cycle (Q32). Verifier 3 PASS at 695b97b;
  non-blocking: no empty-body 3xx case in the redirect test (seed S5 green, code right by probe). Merged to `main`.

## Round 3: stage 3 intake and OCR with page IDs (opened 2026-10-27 on `loop/round-03` at a0d3c6a)
Tiers: Q30 defaults (Fable brief and revision, Codex plan and code review, Opus orchestrator, output critic
and blind verifier, Sonnet 5.5 code). OCR engine: ocrmypdf and Tesseract on this Mac (Q39).
Exit test (spec §7 stage 3): a scanned PDF becomes page text with correct IDs. The scanned PDF is an
invented fixture under `tests/fixtures/`.
- [x] R3-1. Stage 3 work items (defined by the round 3 brief, ruled by the chair before any code):
  intake of a PDF into page text; OCR where a page has no text layer; every page gets an ID (matter,
  binder, page) and the list of every Bates stamp found on it, none chosen (Q35).
    Verifier (blind, round 3, 2026-10-27, tip b864faf): hand-driven `casefile intake --config $D/config.toml --matter 9002.001 --binder scan
    tests/fixtures/scanned/scanned.pdf` -> `intake 9002.001 scan pages=6 ok=5 empty=1 failed=0 stamps=6 had_text=2
    ocr_added=4`, `  empty: scan/004 no text after OCR`, exit 1; records matter=9002.001, ids scan/001 to scan/006, page 3
    stamps KMR2344 and TWP7731, page 6 `mixed`; text, dates, numbers and stamps match the rendered pages. Re-intake exit 2
    naming both folders. Invented spaced page: `stamps=[{'raw': 'MED 0001', 'stamp': 'MED0001'}, {'raw': 'ABC-0042',
    'stamp': 'ABC0042'}]`, `QRL-2025-0418` not a stamp, exit 0. Stage 3 exit `stage3 exit=1 pages=6 ids_ok=6 of 6
    stamps_ok=6 of 6 text_ok=6 of 6 must_ok=5 of 5 empty=1 failed=0 min_ratio=1.000`. Non-blocking test gaps: seeds S1
    (record `matter` field wrong), S2 (sidecar with extra segments) stay green; see round03-verify.md.
- [x] R3-2. Doctor's OCR check turns PASS for real on this Mac (Q11, Q39); R1-19 OCR smoke test on an
  invented fixture PDF.
    Verifier (blind, round 3, 2026-10-27, tip b864faf): `casefile doctor` -> `doctor ocr PASS smoke=ok stamps=SMOKE7342 ocrmypdf=17.13.0
    tesseract=5.5.3 ms=3474`; suite `ocr_real=PASS`, `pdfsmoke text_ok=1 image_pages=1 image_text_layer=0`; stage 1
    `exit=0 verdicts=8 fails=set() test_jobs=1`.
- [x] R3-3. Bench: an unreachable model server exits 2 (Q26); the bench line names the model (Q27).
    Verifier (blind, round 3, 2026-10-27, tip b864faf): host 127.0.0.1:9 -> `bench: cannot run: no reply from the model server at
    http://127.0.0.1:9: <urlopen error [Errno 61] Connection refused>`, exit 2; candidate line `bench 9001.001
    model=candidate ...`; suite `bench 9001.001 model=qwen3.8:27b found=29 of 29 ...`, `no_reply_exit=2`.
- [x] R3-4. Key completeness (Q36): the 9001.001 key lists every real gap and conflict a careful reader
  would flag (critic H1 list); every exact bench number updated.
    Verifier (blind, round 3, 2026-10-27, tip b864faf): key `facts 29 flags 9` (G7, G8 gaps; G9 conflict MED0006,DEF0002, about read
    against both pages); flawed exit 1 `bench 9001.001 model=candidate found=26 of 29 missed=3 invented=2 extra=2
    flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0 of 14`; ideal exit 0 `found=29 of 29 missed=0
    invented=0 extra=2 flags=9 of 9 flags_missed=0 flags_extra=0 rules=0 pages_failed=0 of 14`.
- [x] R3-5. Model client carried items: empty-body 3xx test case (verifier 3, S5); a non-200 HTTPError with
  no body stream stores an answer row.
    Verifier (blind, round 3, 2026-10-27, tip b864faf): suite lines `no_stream_row=1`, `empty_302_row=1`, `no_stream_error raw='' received=True`,
    `redirect_truncated received=True raw='partial'`, `redirect_stall received=True raw=''`, `incomplete_read_row=1`.
- [x] R3-6. Matter loader carried items: duplicate matter numbers refused; OR-5 F3 (`.DS_Store` and other
  hidden files in `records/`), F4 (binder listed twice), F5 (validate names before reading), F6
  (whitespace-only page text).
    Verifier (blind, round 3, 2026-10-27, tip b864faf): `.DS_Store` in `records/` and in `records/medical/` -> exit 0 perfect line; binder
    listed twice -> `binders must be distinct` exit 2; `records/BadName` -> `unlisted binder folder BadName` exit 2;
    whitespace-only 002.txt -> `last line is not a Bates stamp` exit 2; suite `duplicate_numbers_exit=2`,
    `dotfiles_ignored=2`. Low: a duplicate number is found only after the first matter has run (see report).
- [x] R3-7. Hygiene carried from OR-5: trailing whitespace, unused imports in test files, prompt-framing
  comments, F7, F8; verifier test gaps N2 to N5.
    Verifier (blind, round 3, 2026-10-27, tip b864faf): `unused_imports=0`; trailing-whitespace lines in src tests scripts `0`; F7 false
    comments and F8 `split('/')` grep `0`; gate prints `0`. Re-seeded N2 `2 failed`, N3 `3 failed`, N4 `2 failed`,
    N5 `5 failed`, each restored by cmp. Suite `358 passed in 72.67s`.
- [~] R3-8. deferred: R2-CX-2 (prompt truncation detection) waits for stage 4 (OR-4, owner ratified).
  R1-20 (`bates-cites` sees only bracketed cites) waits for the stage that writes cited prose.
- [x] V. Fresh blind verification: every non-deferred R3 item `[x]` with the verifier's own evidence.
    Verifier (blind, round 3, 2026-10-27, tip b864faf): PASS. R3-1 to R3-7 `[x]`, R3-8 deferred. Report:
    docs/loop/round-03/round03-verify.md.
- Build notes (orchestrator, 2026-10-27, tip 2f864a5): W0 77c7f56; lane A fd73d4b, 523b283, 77a5a61, 9e19eb6;
  lane B df25349, fadd27a, 13b066a, 2668c48, merged c8bff68; chair tail 2f864a5 (one unused import). Merged:
  `335 passed in 66.93s`, gate `0`, `unused_imports=0`. Flawed exit 1 `bench 9001.001 model=candidate
  found=26 of 29 missed=3 invented=2 extra=2 flags=8 of 9 flags_missed=1 flags_extra=1 rules=1 pages_failed=0
  of 14`; ideal exit 0 `... flags=9 of 9 ...`; chair seed G9 deleted from key -> ideal exit 1 `flags_extra=1`,
  restored by cmp. `stage3 exit=1 pages=6 ids_ok=6 of 6 stamps_ok=6 of 6 text_ok=6 of 6 must_ok=5 of 5
  empty=1 failed=0 min_ratio=1.000`; stage 1 `exit=0 verdicts=8 fails=set() test_jobs=1`. Chair driven intake
  on the fixture: `intake 9002.001 scan pages=6 ok=5 empty=1 failed=0 stamps=6 had_text=2 ocr_added=4`, exit
  1, page 3 two stamps, page 6 `mixed`, re-intake exit 2. 46 builder seeds red (lane reports).
- Fix cycle 1 notes (worker, 2026-10-27, code 4d615be; a note, not a tick; each test RED before the fix, seeded RED alone after):
  CX-1 `pages`/`records` link to another matter, the checkout, or a dangling target: intake now exit 2 "records or
  pages folder must not be a link", nothing written (6 tests; seed `if False and (` red). CX-2 `.tmp` mkdir fails
  after a rival made one: only folders this run created are removed (2 tests; seed red). CX-3 KeyboardInterrupt
  between renames: `_publish` rolls back on BaseException, re-intake exit 0 (seed `except OSError` red).
  CX-4 302 with stalled or truncated body: `received=True`, raw `partial` or empty (loopback socket, 2 tests;
  seed re-raise red). CX-5 detached child of ocrmypdf (exit 0 and 7) killed after normal return (seed red).
  CX-6 SIGTERM in page extraction and JSON writing: whole-intake handlers, exit 143, no `.tmp` (seed red).
  CX-7 stamp match must end at a token boundary (`(?![A-Za-z0-9])`), 6th stamps case (seed red). CX-8 doctor
  OCR failure cases now assert exit 1 (seed: doctor returns 0 on OCR FAIL red). Sweep `350 passed in 63.42s`,
  gate `0`, `unused_imports=0`, stage3 exit line unchanged. Open: lookbehind is still upper-case only (a
  lowercase letter before a stamp is not refused); a signal between `mkdir` and `created.append` leaks one folder.
- Fix cycle 2 notes (worker, 2026-10-27, code ab507e1; a note, not a tick; each test RED before the fix, seeded RED alone after):
  H1 stamp match no longer continues into a joined token at either end: after, no letter or digit and no
  `-./` plus letter or digit; before, two fixed-width lookbehinds (any-case letter or digit, or one then `-./`).
  `QRL-2025-0418`, `MED0001-A`, `MED0001.2`, `MED0001/3`, `xMED0001`, `AB-MED0001`, `MED0001A` give nothing;
  `MED 0001`, `MED0001.` ending a sentence, `(MED0001)`, `KMR23441`, `XKMR2344`, `MED 0001 Page 3` still match
  (case_joined_tokens; seeds: drop lookahead clause, drop lookbehind clause, upper-case-only lookbehind, each red).
  M1 G9 about (key, ideal, flawed) now names the L5-S1 mild degenerative disease; bench lines unchanged, rules
  find nothing (test_g9_about_matches_the_pages...; seed: key.json at HEAD red). L1 re-intake names every
  existing folder (records, pages, `.tmp`) and says to remove the old binder by hand (seed: keep only the last
  folder red). L2 binder refusal in words (seed red). L3 `file not found: <path>` and pypdf's logger silenced
  for every read (two seeds red; the warnings reach the log, so the test reads caplog). L4 empty page reason
  `no text after OCR`, failed keeps `ocr timeout`, detail line shows it (two seeds red). Same-shape fix: the
  real-tools fixture test expectation `  empty: scan/004` now carries the reason. Sweep `358 passed`, gate `0`.

## Round 4: stage 4 model client and gates (opened 2026-10-27 on `loop/round-04` at 204f6fd)
Tiers: Q45 (Fable brief and revision, Codex `gpt-6-astra` plan and code review, Opus orchestrator, output critic
and blind verifier, Codex `gpt-6.1-sol` code). Ollama on the Studio: login-user app (Q43).
Exit test (spec §7 stage 4): every gate (spec §4) tested with good and bad answers, including truncated ones.
All answers are invented fixtures served by the stand-in model server (`tests/fakemodel/`).
- [x] R4-1. Stage 4 work items (defined by the round 4 brief, ruled by the chair before any code): the model
  client and the six gates of spec §4 in order (truncation, punctuation-only JSON repair, schema check, quote
  check ladder, firm rules on outputs, coverage ledger), with retry once then pages marked failed, never saved empty.
  Verifier (2026-10-28, aa11799): `stage4 exit=0 gates=6 of 6 cases=14 of 14 runs=+14 answers=+21 empty_saved=0
  server_stopped=1` (all seven lines as stated); `gate_cases=27 of 27`; `ladder_ok=14 of 14`, `quotes_ok=8 of 8`;
  `repair_ok=13 of 13`, `schema_ok=14 of 14`, `schemas_loaded=20 of 20`; `triggers=21 blocked_writes=12 of 12
  upgrade_v1=1 upgrade_atomic=1`; doctor via stand-in `doctor runlog_schema PASS schema=2 triggers=21 (counted)`.
- [x] R4-2. Carried: R2-CX-2 prompt truncation detection (OR-4: Ollama does not count cached prompt tokens).
  Verifier (2026-10-28, aa11799): `chat_body_keys=1`, `cached_count_read=1`, `benchrun_modes=8 of 8 answers_ok=1
  answers_failed=7 failures=7` (75 passed).
- [x] R4-3. Carried verifier test gaps from round 3: S1 (stage 3 exit test asserts record `matter` and `page`),
  S2 (sidecar `7 of 6` case), S5 (`make_scanned.py --check` text-layer change).
  Verifier (2026-10-28, aa11799): `stage3 exit=1 pages=6 ids_ok=6 of 6 ...` (asserts `record["matter"]` and
  `record["page"]`, test_stage3_exit.py:40-41), `intake_refusals=16 of 16 group_killed=1` (case `sidecar 7 of 6`,
  test_intake.py:171), `check page 5 differs` (40 passed).
- [x] R4-4. Carried verifier lows: bench refuses a duplicate matter number before the first matter runs;
  `normalize` beyond spaces and hyphens (as the brief rules); leftover step comments in `bench.py` and
  `benchcandidate.py`; suite time near the 90 s budget (T-11).
  Verifier (2026-10-28, aa11799): `score_cases=14 of 14`, `duplicate_numbers_exit=2`, `stamps_cases=8 of 8`,
  `key_refusals=13 of 13` (11 passed); no comment lines at all in `bench.py`, `benchcandidate.py`;
  `suite_time runs=3 max=57.46 verdict=PASS`, exit 0. Regression: `537 passed in 57.80s`, gate `0`,
  `unused_imports=0`, both bench lines and exits (1, 0) and stage 1 to 3 lines identical to `## Project`.
- [~] R4-5. deferred: R1-20 (`bates-cites` sees only bracketed cites) waits for the stage that writes cited prose.
- Plan review and rulings (session 2, 2026-10-27): Codex gpt-6-astra plan review, 16 findings (`docs/loop/round-04/round04-brief-codex.md`); Fable revision accepted 16, rejected 0 (brief §8, 892 lines). Chair ruled D31 to D38 as written in brief §6, logged in spec §9 pending owner veto. Owner questions 47 (uncited pages) and 48 (summary wording) held for the close check-in; interims fail closed (D38). Tuning note for close: the digit-run check of D38 can fail a good answer that reformats a date (`3/2/2026` against `03/02/2026`); fails closed, settled by the benchmark (T-19).
- Chair ruling (build, 2026-10-27 23:12): W4 and W7 blocked on brief §1.10's `bad_quote` count of 4 faults; the mode's first-digit edit of facts[0].quote also makes D38's digit-run check fire on that fact (`text number 03 not in quote`), which is correct. Ruled `faults=5`, every fault message asserted exactly; no gate changed. Builder API deviation accepted: `gates.messages` takes `matter=` because `matter.Page` carries no matter number.
- R04-CH-1 (chair seed, build): `gates.py:105` checking a quote against the whole chunk instead of its cited page stays green on test_gates.py and test_stage4_exit.py (28 passed): no case quotes a sentence that is on another page of the chunk. Code right, test gap; routed to fix cycle 1 (a case that must fail with `quote on <cite> not found`).
- 8a Codex code review (gpt-6-astra, 2026-10-27 23:26 to 23:33): 9 findings; chair reproduced 8 (R04-CX-1 to 3, 5 to 9) by probes on 8a2973b, R04-CX-4 NOT REPRODUCED (every opener re-creates the triggers: 19 -> 21 on reopen); table and rulings in `docs/loop/round-04/round04-codex-review.md`. Fix cycle 1 (Codex gpt-6.1-sol) carries the eight plus R04-CH-1.
- 8b output critic (fresh Opus, 2026-10-28 00:00): `OUTPUT CRITIC 6/10 · high 2 · med 4 · low 4` (`docs/loop/round-04/round04-critic.md`). Chair reproduced H1 (`model.py:92-128` `!r` and `[:200]`), M1 (`gates.py:100,111` list every page), M4 (`doctor.py:209`); H2, M3, L1, L2 read in the messages. Fix cycle 2 (Codex gpt-6.1-sol): H1, H2, M1, M3, M4, L1, L2 by the chair's rulings (`.workflow/scratch/round04-prompts/fix2.txt`). Deferred to the round 5 brief, chair: M2 (open items by stamp: stage 5's status view), L3 (bench invented kinds: moves pinned detail lines). L4: owner question 49, interim the rule id stays. Critic's environment note: an `ollama` listens on 127.0.0.1:11434 on this Mac (the owner's local worker); the doctor sent only its warmup, no matter text.
- CHECKs for R4-1 to R4-4 (the brief's contract, `docs/loop/round-04/round04-build-brief.md` §2; every run through `scripts/run.sh`):
  R4-1: `pytest -q -s tests/test_stage4_exit.py` prints seven `stage4` lines ending `stage4 exit=0 gates=6 of 6 cases=14 of 14
  runs=+14 answers=+21 empty_saved=0 server_stopped=1`; `pytest -q -s tests/test_gates.py tests/test_fakemodel.py` -> `gate_cases=27 of
  27`; `tests/test_quotes.py` -> `ladder_ok=14 of 14 quotes_ok=8 of 8`; `tests/test_jsonrepair.py tests/test_schema.py` -> `repair_ok=13
  of 13 schema_ok=14 of 14 schemas_loaded=20 of 20`; `tests/test_runlog.py` -> `triggers=21 blocked_writes=12 of 12 upgrade_v1=1
  upgrade_atomic=1`; doctor `runlog_schema PASS schema=2 triggers=21`. R4-2: `tests/test_model.py tests/test_benchrun.py` ->
  `chat_body_keys=1 cached_count_read=1 benchrun_modes=8 of 8`. R4-3: `tests/test_stage3_exit.py tests/test_intake.py
  tests/test_scanned_fixture.py` -> `ids_ok=6 of 6`, `intake_refusals=16 of 16`, `check page 5 differs`. R4-4: `tests/test_benchscore.py
  tests/test_bench_multi.py tests/test_stamps.py tests/test_benchkey.py` -> `score_cases=14 of 14 duplicate_numbers_exit=2
  stamps_cases=8 of 8 key_refusals=13 of 13`; no step comments in `bench.py`, `benchcandidate.py`; `scripts/suite_time.sh 3` ->
  `verdict=PASS`, exit 0. Regression: the `## Project` baselines (bench lines, stage 1 to 3 lines, gate `0`, `unused_imports=0`).
- [x] V. Fresh blind verification: every non-deferred R4 item `[x]` with the verifier's own evidence.
  Verifier (2026-10-28, aa11799): PASS; R4-1 to R4-4 reproduced, R4-5 deferred; 10 seeds, 9 red, 1 test gap (low,
  mixed stamped and unstamped chunk); every seed restored, `cmp` identical. `docs/loop/round-04/round04-verify.md`.
- Close (2026-10-28): verifier PASS (`docs/loop/round-04/round04-verify.md`). Carried to the round 5 brief: verifier L1 (no mixed stamped and unstamped chunk test; `gates.py:241` `all` to `any` stays green), verifier L2 (D38 digit check fails a summary holding a bracketed cite; rule with R1-20 before cited prose; T-19), critic M2 (open items by stamp) and L3 (bench invented kinds). Owner questions 47, 48, 49 held; D31 to D38 pending veto. Machine notes: Codex builders need `-c sandbox_workspace_write.network_access=true`; an `ollama` from the owner's local worker listens on 127.0.0.1:11434 here, so verifiers run the doctor in process against the stand-in.

## Round 5: stage 5 case file, merge, medical memo (opened 2026-10-28 on `loop/round-05` at 4755170, same session, owner Q48)
Tiers: Q46 (Fable brief and revision; a fresh Fable agent for the plan review and the code review, read-only; Opus
orchestrator, output critic and blind verifier; Codex `gpt-6.1-sol` code and fixes). The owner is offline (Q48): no
check-in; questions held in `docs/loop/questions-for-owner.md` with interim rulings by the pillars, pending veto.
Exit test (spec §7 stage 5): the test matter produces a memo with cites, conflicts and open items. All model answers
are invented fixtures served by the stand-in model server (`tests/fakemodel/`).
- [ ] R5-1. Stage 5 work items (defined by the round 5 brief, ruled by the chair before any code): the case file,
  merge into it, and the medical memo, built on the round 4 gate pipeline (`gates.ask`), with cites, conflicts and open
  items, under owner interims for questions 47 (uncited pages stay open) and 48 (no summary used as verified).
- [ ] R5-2. Carried: R1-20 (`bates-cites` sees only bracketed cites) and round 4 verifier L2 (the D38 digit check reads
  digits inside a bracketed cite), both due now that a stage writes cited prose; round 4 verifier L1 (a mixed stamped
  and unstamped chunk test).
- [ ] R5-3. Carried: round 4 critic M2 (open items shown by stamp, not page id) and L3 (bench `invented:` lines separate
  no-such-page from quote-not-on-page).
- Plan review and rulings (2026-10-28): fresh Fable plan review, 20 findings (`docs/loop/round-05/round05-brief-review.md`); Fable revision accepted 18, rejected 1 (L6, `model.py:127-128` always sends num_ctx), owner 2 (questions 56, 57); brief 984 lines. Chair ruled D39 to D43 as written in brief §6, logged in spec §9 pending owner veto. Chair's flag for the check-in: question 56's interim (no re-send across runs; the memo states the limit) leaves a defense report read in a later run unchecked against earlier pages, the conflict class Q41 ranks first; acceptable only because the memo says so.
- Chair ruling (build, W5 blocked, 2026-10-28 02:05): brief W5 check 14 (`Pages read in 2 runs`) and seed (i) ("the second run read nothing") contradict. Ruled: the sentence counts runs with at least one `read` coverage row; the fixture has two runs that read pages plus a third run that read nothing, so check 14 expects `Pages read in 2 runs` and seed (i) (counting every run) gives 3, red. Missing inputs: `memo.build(casefile, pages, open_items, *, matter, playbook_version, model)` and `memo.render(memo, path, *, rules)`; W7 passes the matter number and the loaded playbook rules.
- R05-CH-1 (chair seed, build): `facts.py:170` dropping `or obj["seq"] != index` from `load` stays green on `tests/test_facts.py` (`casefile_ok=14 of 14`): no case gives the last line a wrong `seq` (no later `prev` covers it). Code right, test gap; routed to fix cycle 1.
- Chair rulings (build, lane A, 2026-10-28 02:20): the brief ran W3 before the lane B merge although `pipeline.merge` needs `facts.py`; lane B merged first (d3dd5a9), lane A's W1 to W3 on top. Measured counts accepted over the brief's: W2 (two plus one records, 12 read with DEF0001 and DEF0002 uncited in the chunked fixture, two run rows and one answer on a chunk-two no reply), W3 (`uncited=2`, `extra=3`), W1 seed (e) `cite_forms=7 of 11`. Finding: the forced three-chunk bench prints `bench_chunks=3 found=29 of 29 flags=5 of 9`: conflicts and gaps whose pages fall in different chunks are lost within one run, not only across runs (Q56). Ruled: the memo's conflicts sentence reads `Pages read in N run(s); conflicts and gaps are checked only between pages sent to the model together.`; owner question 56 amended to name chunks. W3b (Codex) also re-pins `tests/test_bench_cli.py` to the `gate.*` labels and makes the no-reply failure plain words (it printed `<urlopen error [Errno 61] Connection refused>`, the round 4 H1 class).
- 8a code review (fresh Fable, Q46, 2026-10-28): 11 findings (2 high, 4 med, 5 low; 9 confirmed). Chair ran the reviewer's probe and traced H2: 9 reproduced, L3 plausible only, L4 tuning. Rulings in `docs/loop/round-05/round05-code-review.md`; fix cycle 1 (Codex) carries H1, H2, M1, M2, M3, L1, L2, L5 and R05-CH-1; M4 (an edited last line of the case file loads clean) becomes a recorded limit.
- [ ] V. Fresh blind verification: every non-deferred R5 item `[x]` with the verifier's own evidence.
