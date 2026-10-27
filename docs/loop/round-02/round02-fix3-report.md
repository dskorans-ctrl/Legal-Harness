# Round 2 fix cycle 3 report (orchestrator, Opus 5.5; builder Gemma 4 e4b, owner Q28)

Branch `loop/round-02`, from e637357. Scope: OR-8 (verifier finding V2-F1 and test gaps V2-S1, S2, S4,
S5, S6 from `round02-verify.md`). Fix cycle 3 is the last this round allows. All code and tests written
by `gemma4:e4b-it-qat` through `scripts/gemma_task.py`; the chair wrote task files, seeds and records
only. No Sonnet fallback. Per-call numbers: `round02-gemma-tally.md`, "Fix cycle 3". Baseline at
e637357: `263 passed in 36.40s`, gate `0` (`gate prose PASS dashes=0 files=130`), listening Python
processes 0. Every verdict below is the exit status of a `scripts/run.sh` call.

## V2-F1: a received non-200 reply is stored (D25, R2-3e)
| Step | Result | Commit |
|---|---|---|
| Test `test_benchrun_non200_reply` (404 through `FakeTransport` with `FakeModel(..., model="other:model")`, then a 503 with a 540-byte body through a plain opener) on the tip | RED, exit 1: `assert [] == [('failed', '...own model"}')]`, `1 failed, 3 passed` | 81c78ce |
| Fix: model.py passes the whole body decoded (`errors="replace"`) as `raw` in the HTTPError handler (body read once) and at `status != 200`; the message keeps the 200-byte excerpt | GREEN, exit 0: `4 passed`; one `failed` answer row holding `{"error": "fakemodel: unknown model"}` and one `bench.model` failure row, then the 540-character body whole | 81c78ce |

## Seed table (each: test GREEN on the tip first; one-line mutation; targeted test; restored with `cp`, `cmp` ok, `git diff --quiet` ok; GREEN again)
| ID | Mutation | Test | Red text (exit 1 each) | cmp |
|---|---|---|---|---|
| F1-a | model.py HTTPError raise: drop the new `raw` argument | test_benchrun.py::test_benchrun_non200_reply | `assert [] == [('failed', '...own model"}')]`, `1 failed, 3 passed` | ok |
| F1-b | model.py `status != 200` raise: drop the new `raw` argument | same | `assert [('failed', '...own model"}')] == [('failed', '...busy reply ')]`, `1 failed, 3 passed` | ok |
| F1-c | model.py `status != 200`: store `payload[:200]` instead of the whole body | same | `assert [('failed', '...invented se')] == [('failed', '...busy reply ')]`, `1 failed, 3 passed` | ok |
| V2-S1 | bench.py `if (p / "matter.toml").is_file()` -> `if p.is_dir()` | test_bench_discovery.py | `assert 'bench: --can... one matter\n' == ''`, `1 failed` | ok |
| V2-S2 | benchscore.py drop `k.cite == fact.cite and` | test_benchscore_cite.py | `assert (2, 0, 0, 0) == (1, 1, 1, 0)`, `1 failed` | ok |
| V2-S4 | benchrun.py `!= "stop"` -> `not in ("stop", None)` | test_benchrun_done_reason.py | `assert None == 'bench.truncation: done_reason=None'`, `1 failed` | ok |
| V2-S5 | benchscore.py drop `or flag_key in seen` | test_benchscore_flag_dedupe.py | `assert 2 == 1` (flags_extra), `1 failed` | ok |
| V2-S6 | bench.py `imperfect += not s.perfect` -> `imperfect = int(not s.perfect)` | test_bench_multi.py | `assert 'bench matters=2 imperfect=0' == 'bench matters=2 imperfect=1'`, `1 failed` | ok |

Commits: S1 a1af3ac, S2 f2148ca, S4 12876e9, S5 73baa0c, S6 1e84c60. Every test uses tmp_path copies or
`test_matter.make`; the committed fixture was not edited (`git status` clean for `tests/fixtures`).

## Suite and gate after the last item (tip 1e84c60)
- `scripts/run.sh pytest -q`: `269 passed in 37.13s`, exit 0.
- `scripts/run.sh python -m casefile.gate`: exit 0, prints `0`; `gate pytest PASS exit=0`, `gate privacy PASS
  offenders=0 scanned=549`, `gate rules_selftest PASS misses=0 false_hits=0`, `gate playbook PASS invalid=0
  unmarked=0 version=pb-00be6eb62752`, `gate prose PASS dashes=0 files=135`.
- Suite and gate ran green before each of the six commits (264, 265, 266, 267, 268, 269 passed).
- Listening Python processes: 0 before, 0 after.

## Gemma
7 tasks, 8 driver calls, 6 first try; one retry (FC3-1 a1 indented the method, splice exit 6, nothing
written; the same slip as FC1-3a). Tokens: prompt 12629, answer 9410; model time 335 s. No re-split, no
Sonnet fallback, no deviation.

## Notes for the owner (conservative readings, flagged)
- The task files dictated each test and the model.py change nearly verbatim (the practice of fix cycles 1
  and 2); six of seven answers are byte-identical to the task text. Gemma transcribed here more than it
  designed: count it that way in the Fable comparison.
- V2-F1 test covers both raise sites (the verifier's 404 probe reaches only the HTTPError path, so a 503
  returned without an exception was added) and checks the whole body is stored, not the 200-byte excerpt.
- `exc.read()` on an HTTPError with no body stream was already possible before this fix (`exc.read(200)`);
  unchanged, not probed.
- The uncommitted `docs/loop/agent-log.md` change in the tree predates this cycle and was left alone.
- Ledger R2-8 carries a note, not a tick; R2-3e and V2 stay for the verifier.
