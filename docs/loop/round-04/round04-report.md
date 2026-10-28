# Round 4 report: stage 4, the model client and gates

**Verdict: PASS.** The blind verifier (fresh Opus 5.5) re-ran every CHECK on `aa11799` and ticked R4-1 to R4-4 and V.
with its own evidence. R4-5 (R1-20) stays deferred. Two fix cycles were used (8a's fixes count as the first), out of
a cap of three. Spec §7 stage 4's exit test passes: every gate of spec §4 is tested with good and bad answers,
including four truncated ones.

Tiers (owner Q45): Fable wrote and revised the brief; Codex `gpt-6-astra` did the plan review and the code review;
Opus 5.5 orchestrated and ran the output critic and the blind verifier; Codex `gpt-6.1-sol`, through `codex exec`,
wrote every line of code and every fix. Every answer, page and name used is invented; no Ollama was called.

## Measured on the tip (chair and verifier re-runs)

| Number | Check that produced it |
|---|---|
| `537 passed` (was 358) | `scripts/run.sh pytest -q` |
| `suite_time runs=3 max=57.46 verdict=PASS` (was 95.33 s at round open) | `scripts/run.sh scripts/suite_time.sh 3` (verifier); chair at the merge `max=54.47` |
| gate `0`, `unused_imports=0` | `python -m casefile.gate`, `scripts/unused_imports.py src tests scripts` |
| `stage4 exit=0 gates=6 of 6 cases=14 of 14 runs=+14 answers=+21 empty_saved=0 server_stopped=1` | `pytest -q -s tests/test_stage4_exit.py` (seven `stage4` lines; `faults=5`, `warning=1`, `open_items=14 then 1`) |
| `gate_cases=27 of 27`, `ladder_ok=14 of 14`, `quotes_ok=8 of 8` | `tests/test_gates.py`, `tests/test_quotes.py` |
| `repair_ok=13 of 13 schema_ok=14 of 14 schemas_loaded=20 of 20` | `tests/test_jsonrepair.py tests/test_schema.py` |
| `triggers=21 blocked_writes=12 of 12 upgrade_v1=1 upgrade_atomic=1`; doctor `runlog_schema PASS schema=2 triggers=21 (counted)` | `tests/test_runlog.py`, doctor in process |
| `chat_body_keys=1 cached_count_read=1 benchrun_modes=8 of 8` (R4-2) | `tests/test_model.py tests/test_benchrun.py` |
| `ids_ok=6 of 6`, `intake_refusals=16 of 16`, `check page 5 differs` (R4-3) | `tests/test_stage3_exit.py tests/test_intake.py tests/test_scanned_fixture.py` |
| `score_cases=14 of 14 duplicate_numbers_exit=2 stamps_cases=8 of 8 key_refusals=13 of 13` (R4-4) | `tests/test_benchscore.py tests/test_bench_multi.py tests/test_stamps.py tests/test_benchkey.py` |
| bench lines unchanged: flawed exit 1 `found=26 of 29 ... flags=8 of 9 ...`, ideal exit 0 `found=29 of 29 ... flags=9 of 9 ...` | `casefile bench --candidate ...` |
| stage 1 to 3 lines unchanged | the three exit tests |

## What was built

- Model client: `truncate` and `think` are sent only by the gate pipeline (the doctor's and the bench's bodies are
  unchanged); `prompt_eval_cached_count` is read and stored; budget `tokens_at_most` is the UTF-8 byte count plus
  `TEMPLATE_TOKENS = 64`; a context-length refusal is `bench.truncation` in the stage 2 runner (D31, R4-2).
- `gates.py`: the six §4 gates in order; gate 1 is four checks (budget, `truncate: false`, a `prompt_id` and `end_id`
  nonce per attempt, `done_reason` and counts present and within the context); retry once as a fresh two-message
  prompt; `Outcome.answer is None` whenever not ok; coverage rows `read`, `uncited`, `failed`, keyed by page id;
  firm rules skip quoted record words (Q44); failure reasons in plain words that name the cited page and what
  happens next (D31, D38).
- `quotes.py` ladder (exact, whitespace, curly and case, OCR faults limited to Q44's two line kinds and letter
  hyphens), every match on token boundaries; `jsonrepair.py` (punctuation only, duplicate keys refused);
  `schema.py` (stdlib subset validator); run log schema v2 (`coverage`, `gates`, 21 triggers, v1 upgraded in one
  transaction) (D32 to D35).
- Bench: scored by the ladder, key collisions under the same folding, duplicate matter numbers and loader errors
  refused before the run log opens, `stamps.compile` shared with config (D37, R4-4); stand-in at 17 modes (D36).
- Verifier gaps S1, S2, S5 closed; one real intake shared by two tests; `scripts/suite_time.sh` carries the time
  verdict in its exit status (R4-3, T-11).

## Plan review

Codex `gpt-6-astra` found 16 issues in the brief (8 high, 9 confirmed). Fable accepted all 16 with code evidence;
the false ligature premise, the unreachable repair case and the nonce lookup were the confirmed highs. The revised
brief added D38 (every reference checked, digit runs, empty and uncited pages) and owner questions 47 and 48.

## Critic round

- 8a code review (Astra): 9 findings. Chair reproduced 8 by probes on the production code (ambiguous first-stamp
  page identity marking an unread page read; quote fragments inside longer words and numbers; numeric hyphen joins;
  blank placeholder records; a tail comma rejected before repair; duplicate keys; decoder errors escaping the
  pipeline; type-blind enum). Finding 4 (upgrade commit before the triggers) did not reproduce: every opener
  re-creates the triggers (19 -> 21 on reopen). Plus chair seed CH-1 (a quote checked against the whole chunk stayed
  green: test gap). All fixed in cycle 1, each red first.
- 8b output critic: `OUTPUT CRITIC 6/10 · high 2 · med 4 · low 4`. Raw reprs and cut dicts in reasons, no plain
  words or next step, every chunk page listed as "searched", no fact location, wrong doctor advice for a missing
  model. Seven fixed in cycle 2; M2 (open items by stamp) and L3 (bench invented kinds) carried to the round 5 brief;
  L4 is owner question 49.
- 8c blind verifier: PASS; 10 fresh seeds, 9 red. L1: `gates.py:241` `stamped=all(...)` to `any(...)` stays green (no
  mixed chunk test; low, the rule it touches sees bracketed cites only, R1-20). L2: the D38 digit check reads digits
  inside a bracketed cite in a summary; must be ruled with R1-20 before any stage writes cited prose (T-19).

## Design calls pending owner veto

D31 to D38 (spec §9), the chair's build ruling `faults=5` for `bad_quote` (the digit check rightly fires on the
edited quote), and the cycle 1 and 2 rulings recorded in `round04-codex-review.md` and the ledger. Owner questions
47 (what closes an uncited page), 48 (summary wording), 49 (rule ids in outputs) are held with fail-closed interims.

## Discoveries

- Codex `workspace-write` refuses a loopback bind; builders need `-c sandbox_workspace_write.network_access=true` or
  the socket tests fail and the gate prints 1 for a reason that is not the code's.
- An `ollama` (the owner's local worker) listens on 127.0.0.1:11434 on this Mac; the real doctor reaches it. The
  critic's doctor run sent only its warmup; the verifier ran the doctor in process against the stand-in.
- The owner's anonymization convention (casefile-anon/1, ledger Q47) is logged for the stage 7 brief.

## Process notes

- Each Codex builder ran one work item and did not commit; the chair re-ran every CHECK, added a seed of its own per
  lane, ran the gate and committed with targeted paths. W4 and W7 stopped correctly on a brief count error instead
  of loosening a guard.
- The owner paused once (W0 restarted cleanly) and changed tiers twice (Q45 this round, Q46 from round 5).
- The owner asked for round 5 to start in this session (Q48), overriding one round per session for tonight.

## Cost (agent log)

Fable 526 k (brief 322 k, revision 204 k); Codex `gpt-6.1-sol` about 1.7 M across 12 runs (builders 1.24 M, fixes
477 k, plus the Librarian); Codex `gpt-6-astra` two reviews (136 k for 8a; the plan review's count is in its log);
Opus 253 k (critic 102 k, verifier 151 k); chair not counted.
