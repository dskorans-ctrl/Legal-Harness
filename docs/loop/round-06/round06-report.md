# Round 6 report: stage 6, outputs, cards and schemas

**Verdict: PASS** (blind verifier, `docs/loop/round-06/round06-verify.md`, tip 6fba08f), after three fix cycles (the cap).
Output critic, second grading after the fixes: `OUTPUT CRITIC 7/10 · high 0 · med 6 · low 9`
(`round06-critic2.md`); first grading `5/10 · high 4 · med 9 · low 8` (`round06-critic.md`), 19 of its findings fixed, 0 worse.
Spec §7 stage 6 exit: six Word documents built from the invented test matter, no high finding left.

Owner present for the whole round (check-in at the open, Q49 to Q59 answered during it). No real client data entered
the repo; the owner waived the rule for reading five example documents in this session only (Q59), from which a
placeholder-only format specification was distilled (`docs/loop/design/output-format-from-examples.md`); the chair's
name check found no source name or date in it, and every scratch copy was deleted.

## Measured on the tip (chair and verifier re-runs, every run through `scripts/run.sh`)

| Claim | Number | Check |
|---|---|---|
| Stage 6 exit | `stage6 exit=0 docs=6 of 6 answers=+16 rule_hits=0 server_stopped=1` | `pytest -q -s tests/test_stage6_exit.py` |
| Suite | `786 passed`; `suite_time runs=3 max=66.17 verdict=PASS` | `pytest -q`; `scripts/suite_time.sh 3` |
| Gate, imports | `0`; `unused_imports=0` | `python -m casefile.gate`; `scripts/unused_imports.py` |
| Bench, flawed (exit 1) | `found=26 of 36 missed=10 invented=2 extra=2 dates_wrong=1 flags=8 of 9 ... pages_failed=0 of 14` | `casefile bench --candidate tests/fixtures/bench/flawed.json` |
| Bench, ideal (exit 0) | `found=36 of 36 missed=0 invented=0 extra=2 dates_wrong=0 flags=9 of 9 ... pages_failed=0 of 14` | same, `ideal.json` |
| Stage 5 exit | `stage5 exit=0 runs=4 of 4 memos=3 of 3 answers=+4 casefile_lines=56 chain_ok=1 server_stopped=1` | `tests/test_stage5_exit.py` |
| Outputs | `packet_ok=6 of 6 outputs_ok=13 of 13 report_ok=9 of 9 depo_ok=12 of 12 hearing_ok=12 of 12` | the five output test files |
| Cards, rules, roles | `cards_loaded=15 of 15 schemas_loaded=11 of 11`; `rule5_forms=18 of 18 bills_forms=7 of 7`; `roles_by_name=6 of 6 matterinfo_ok=12 of 12`; `gate_cases=39 of 39`; `casefile_ok=17 of 17` | test files named in the ledger CHECKs |
| Documents | 490 quotes on their cited pages; 0 rule hits on our words; DEF0002 quoted under its conflicts; no defense examiner in the bills question | verifier's python-docx read of all six |

Baselines moved deliberately: the key gained DEF0002's seven examination facts (29 to 36; an answer-key gap since round 2,
found by the critic) and the bench line gained `dates_wrong=`. New baselines in the ledger `## Project`.

## What was built
One card loader (manifest v2, 15 cards, 11 schemas, JSON only, engine neutral) with practice ported from the firm skills
into `playbook/deposition.toml` and `hearing.toml`; facts with date, category and provider verified on the page; old case
files upgraded in place; binder roles by name (DME, IME, defense medical); the header and issues asked once at the first
task run into `matter.toml`; `casefile report`, `depo` and `hearing` (packet, one gated step per card, `render(answers)`
from the gated JSON only, `.partial.docx` on a failed step); the memo in spec §2 sections with conflict quotes, defense
against ours first; the bills question to our doctor exempt from two rules, fee questions to the examiner blocked.

## Owner direction during the round
Q52 and Q53: the cloud round trip (anonymize locally, Claude by API key, approval once per task at Run, 30 day retention
acceptable, Codex as an optional read-only second review) became a design proposal and spec D52 to D62 (stage 7b,
pending veto). Q55: nothing runs continually; the local model files and anonymizes; Claude reads the whole matter per
task; the reconcile pass (D47) was withdrawn. Q54, Q57: petition header dropped for questions asked of the attorney;
roles by binder name.

## Plan review, rulings, critic round
Plan review (fresh Fable): 20 findings, all accepted; two owner amendments followed (§9, §10). Chair ruled D44 to D51.
Build: W1 one green commit; lanes A (W2, W4) and B (W5 to W7, worktree) in parallel; lane B blocked at W6 (defense pages
outside the provider packet), chair ruled the defense binder widening; merge clean; W8 exit test. Code review (fresh
Fable): 17 findings, 4 reproduced by the chair, 16 fixed in cycle 1. Output critic: 21 findings, highs reproduced in the
documents, fixed in cycle 2 with the practice rewrite of the recorded answers. Fix cycle 3 reverted a wrong chair ruling
(below). Blind verifier: PASS, 6 fresh seeds, 4 red.

## Design calls pending owner veto
D44 to D51 (round 6 brief, as amended); D52 to D62 (cloud round trip, stage 7b); chair build rulings in the ledger: defense
binder widening in provider selection, six providers, depositions with an open item exit 1, code review M2 (IME and
unseparated DME count as defense; note: a binder named for a person whose name starts "Ime" reads defense).

## Carried to round 7
- Critic 2 M1 (design): a fact's identity is its folded quote, so the ER's and the examiner's identical "Straight leg raise
  negative bilaterally" merge across dates and providers; identity should include date and provider (D40 amendment).
- Critic 2 M2 to M6 (practice in the defense-doctor and our-doctor deposition answers and cards): concessions, omission
  points, real cross and redirect, points for our expert, the 4/5 strength reading.
- Owner Q59 items 82 to 86 and the format specification (caption, layout, witness-by-witness hearing, new outputs).
- Verifier test gaps S1 (hearing `--doctor` and `--closing` swap stays green), S3 (schema required quote untested; a
  question without a quote crashes render), S4 (card wording guarded only by the version pin); verifier notes on the
  hearing "Defense report points: none" and Q82 "Purpose: discovery".
- Recorded limits: code review L7 (an oversize client packet fails instead of shrinking), fix cycle 2 A2 (re-extraction
  cannot correct a stored date), round 5 M4 (an edited last case file line loads clean).

## Process notes
- Chair mistake (Mistakes Log): the critic L7 ruling "a fact's date must appear in its quote" was ruled without measuring
  it on the key; it re-dated 16 key facts (a causation opinion to the accident date it cites) and cost the third fix
  cycle. Measure a gate rule on the answer key before ruling it.
- The owner answered questions live, which changed the brief twice before build; both amendments went to the architect,
  not to builders, and W1 stayed one green commit.
- Fix cycle 3's working files lived under `/private/tmp/round06-fix3/`; the pins and report were copied into this folder.

## Cost (agent log)
See `docs/loop/agent-log.md` `## Round 6`.
