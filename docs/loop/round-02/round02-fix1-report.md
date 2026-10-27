# Round 2 fix cycle 1 report (orchestrator, Opus 5.5; builder Gemma 4 e4b, owner Q28)

Branch `loop/round-02`, from b88c605. Findings per OR-5: R2-CH-1, R2-CX-5 (= Fable F1), R2-CX-6,
R2-CX-7 (= Fable F1b), Fable F2. All code and tests written by `gemma4:e4b-it-qat` through
`scripts/gemma_task.py`; the chair wrote task files, feedback, seeds and records only. No Sonnet fallback.
Per-call numbers: `round02-gemma-tally.md`, "Fix cycle 1". Baseline at b88c605: `253 passed in 36.23s`,
gate `0`, listening Python processes 0.

## Findings: red before, green after (verdict is the exit status)
| Finding | Test | RED before the fix | GREEN after | Commit |
|---|---|---|---|---|
| R2-CH-1 zero counts | `test_benchrun_zero_counts` (eval_count=0, prompt_eval_count=0) | no code change needed; seed `c > 0` -> `c >= 0`: `AssertionError: ('eval_count', None)`, `1 failed, 1 passed`; seed counts_ok on eval_count only: `AssertionError: ('prompt_eval_count', None)`; both restored, cmp ok | `2 passed` | 9c82349 |
| R2-CX-5 / F1 key collisions | `test_key_refusals` 10 -> 12 | `key_refusals=10 of 12`, `assert 10 == 12` | `key_refusals=12 of 12`; seeding out either new check gives `11 of 12`, restored, cmp ok | 0f2022d |
| R2-CX-6 unparsed 200 reply | `test_benchrun_unparsed_reply` (non-JSON text, JSON array) | `AssertionError: invented reply that is not JSON` (no answer row) | `19 passed` (benchrun and model); seeds: array raise without raw, runner json.dumps of a str: both red, restored, cmp ok | ba24d90 |
| R2-CX-7 / F1b non-UTF-8 matter.toml | `test_refusals` 11 -> 12 | `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 54` | `refusals=12 of 12`; CLI on a tmp copy with 0xff appended: `exit 2` (was 1) | 408991c |
| F2 `from exc` | `tests/test_exc_chain.py` (one test per site) | `5 failed` (`__cause__` is None) | `5 passed` | 365f1e0 |

After every finding: `scripts/run.sh pytest -q` exit 0 and `scripts/run.sh python -m casefile.gate` printed
`0`. Final: `260 passed in 39.37s`; gate `0`.

## Design choices the chair made (owner asleep; conservative reading, flagged)
- R2-CX-6: `ModelError.raw` is now a dict or the decoded reply text (utf-8, errors replaced). The runner
  stores a str raw as it is and a dict through `json.dumps` as before. A non-200 status (model.py:59)
  still carries no raw: not in the finding's scope and not a 200 reply; left for round 3 to rule on.
- R2-CX-5 messages: `fact F3: same cite and quote as fact F2`, `flag G2: same kind and cites as flag G1`
  (the later id first, the earlier one second). Cite sets compare as sets (order and repeats ignored).
- F2 seed test is a new file, `tests/test_exc_chain.py`; `test_binder_unreadable_chains` uses chmod 0 on a
  tmp_path folder and restores 0o755 in a finally.

## Deviations
- FC1-2's driver call outlived the Bash tool's 120 s default timeout and was moved to the background by
  the tool; the chair started nothing else and waited for it to exit (exit 0). Every later call used a
  600 s foreground timeout. No process left running (listening Python count 0 after).
- FC1-1 ran the driver with the system `python3`, not through `scripts/run.sh`; every later call went
  through `scripts/run.sh`.
- Gemma's FC1-2 answer added one blank line with trailing spaces in `benchkey.py` (cosmetic, joins the
  OR-5 trailing-whitespace item deferred to round 3); `test_benchrun_zero_counts` keeps an unused
  `failures` list that was in the chair's task text. Both left as written.

## Gemma
11 tasks, 14 driver calls, 8 first-try passes, 0 re-splits, 0 fallbacks. Tokens: prompt 27944, answer
26757; model time 926 s. Retries: two FILE answers on function tasks (refused, exit 4, by the CX-4 driver
guard) and one indented method (splice exit 6); each passed on its second attempt with one feedback file.
