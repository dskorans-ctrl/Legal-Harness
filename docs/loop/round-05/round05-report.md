# Round 5 report: stage 5, the case file, merge and medical memo

**Verdict: PASS.** The blind verifier (fresh Opus 5.5) re-ran every CHECK on `ff79699` and ticked R5-1 to R5-3 and V.
with its own evidence; 5 fresh seeds, all red, no test gap. Two fix cycles of three. Spec §7 stage 5's exit test
passes: the invented test matter produces a memo with cites, conflicts and open items.

Run in the same session as round 4 at the owner's word (Q48, owner offline): no check-in; owner questions held with
fail-closed interims. Tiers (Q46): Fable wrote and revised the brief; fresh Fable agents did the plan review and the
code review; Opus 5.5 orchestrated and ran the output critic and the blind verifier; Codex `gpt-6.1-sol` wrote every
line of code and every fix. Every answer, page and name is invented; no model outside the stand-in was called.

## Measured on the tip (chair and verifier re-runs)

| Number | Check that produced it |
|---|---|
| `652 passed` (was 537) | `scripts/run.sh pytest -q` |
| `suite_time runs=3 max=51.57 verdict=PASS` | `scripts/run.sh scripts/suite_time.sh 3` (verifier) |
| gate `0`, `unused_imports=0` | `python -m casefile.gate`, `scripts/unused_imports.py src tests scripts` |
| `stage5 exit=0 runs=4 of 4 memos=3 of 3 answers=+4 casefile_lines=48 chain_ok=1 server_stopped=1` | `pytest -q -s tests/test_stage5_exit.py` (nine `stage5` lines; memo 3 `quotes=32 of 32 by_page=1 cites=46 ... conflicts=5 gaps=4 open=0`) |
| `casefile_ok=14 of 14`, `memo_docx_ok=14 of 14 memo_refused=2 of 2 memo_changed=1 memo_reason_exempt=1` | `tests/test_facts.py`, `tests/test_memo.py` |
| `pages_ok=10 of 10 chunks_ok=8 of 8 pipeline_ok=5 of 5`, `status_ok=6 of 6 binder_refused=1` | `tests/test_pages.py tests/test_pipeline.py`, `tests/test_status.py` |
| `memo_intake 9002.001 chunks=1 read=5 open=1 facts=5 gaps=1 label_ok=1 exit=1` | `tests/test_memo_intake.py` (the scanned matter) |
| `bench_modes=12 of 12`, `reply_rows=9 of 9`, `gate_cases=31 of 31`, `cite_forms=11 of 11` | `tests/test_bench_pipeline.py`, `tests/test_gates.py tests/test_rules.py` |
| `invented_kinds=2 of 2 rule_excerpt_ok=1` | `tests/test_bench_detail.py tests/test_benchscore.py` |
| bench lines, stage 1 to 4 lines, doctor `schema=2 triggers=21` unchanged | baselines in ledger `## Project` |
| local Ollama requests during a full gate run: `delta=0` | chair audit of the server's request log |

The memo, opened with python-docx by the chair, the critic and the verifier: 29 of 29 key facts as `"quote" [cite
STAMP]`, every quote verbatim on its page, 9 of 9 key conflicts and gaps with the key's cites, open items by stamp,
every model sentence its own `Model's reading:` paragraph (owner interim 48).

## What was built

`extract.py` (the extraction card in production); `pages.py` and `pipeline.py` (pages from either layout, byte-budget
chunks with a retry margin, only unread pages sent per job); bench on the pipeline (`benchrun.py` removed); `facts.py`
(hash-chained append-only case file, torn tail recovered, fold identity, matter lock); `memo.py`, `memo_job.py` and
`casefile memo` (Word memo, firm-rule self-check, atomic publish); `casefile status`; cites inside summaries checked as
references and unbracketed cite forms recognised (R1-20, round 4 verifier L1 and L2); bench detail reasons and open
items by stamp (round 4 critic L3 and M2). Spec rows D39 to D43.

## Plan review

A fresh Fable reviewer found 20 issues (2 high): cross-run conflicts can never be flagged when records arrive in later
runs (H1), and deleting `test_benchrun.py` would retire the only proof that received replies are stored (H2). Fable
accepted 18, rejected 1 with code evidence, and put 2 to the owner (56, 57). The reviewer also found the tests'
default model host was the owner's own Ollama port; the chair checked the server's request log (no suite run reached
it) and W0 moved every test to port 9.

## Build rulings

W5 stopped on a brief contradiction (the runs sentence) and missing inputs; W3 stopped because the brief ran it
before the lane B merge it depends on. Both were ruled and rebuilt. Measured counts replaced six predicted ones. The
forced three-chunk bench printed `flags=5 of 9`: conflicts whose pages fall in different chunks are lost within one
run, so owner question 56 was widened and the memo's sentence names chunks.

## Critic round

- 8a code review (fresh Fable): 11 findings; the chair ran the reviewer's probe: 9 reproduced. Fixed in cycle 1: a
  page-id cite on a stamped page made every later memo refuse (H1); coverage said `read` before the case file held
  the facts, so a failed append lost them silently (H2); a fact dropped when its first page left the matter; two
  writers duplicating ids; a reading shown under the wrong page; a one-page conflict; an empty matter; the refusal
  text. M4 (an edited last line loads clean) is a recorded limit. Chair seed R05-CH-1 (last-line `seq`) closed.
- 8b output critic: `OUTPUT CRITIC 7/10 · high 0 · med 2 · low 5`; answer key complete. Fixed in cycle 2: the memo
  listed itself as out of date, empty headings and sections without a word, plurals, the unstamped warning, casing.
  L5 ("defense report" in our words) is owner question 58.
- 8c blind verifier: PASS; lows carried: the no-reply reason says "the page stays open" even in the doctor; D41 text
  amended at close.

## Design calls pending owner veto

D39 to D43 (D41 amended at close), the build rulings in the ledger `## Round 5`, and owner questions 50 to 58 with their
interims. Most important for the owner: question 56 (conflicts across runs and chunks are not checked; the memo says
so), because Q41 ranks defense-against-our-records conflicts first.

## Discoveries

- Bench now runs the real gate pipeline; `uncited:` is shown in model mode.
- The memo is the first attorney-facing output; its quotes are exact and its model sentences labelled.
- An untracked `tests/fixtures/matters/9001.001/.claude/` (a Claude Code marker) is copied into exit-test matters.

## Process notes

- The owner asked for round 5 in the same session; the session ran rounds 4 and 5 back to back with one context.
- Builders stopped correctly on brief errors three times instead of guessing; each stop cost one rerun.
- The output critic stopped its own stand-in with the sandbox off; the port was confirmed closed.

## Cost (agent log)

Fable about 1.03 M (brief 377 k, revision 177 k, plan review 240 k, code review 232 k); Codex `gpt-6.1-sol` about
2.3 M across 16 runs (builders, fixes, Librarian); Opus 262 k (critic 119 k, verifier 143 k); chair not counted.
