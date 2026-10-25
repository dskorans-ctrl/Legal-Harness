---
name: andon
description: Lean quality system for AI-assisted work (PrimeFoldTools/andon). Use when a mistake recurs, when an agent over-claims "done", or when setting up or auditing project memory, a Mistakes Log, a Defect Ledger, session wrap/orient, lanes for parallel sessions, or the claim-check Stop hook. Trigger on "andon", "mistakes log", "defect ledger", "countermeasure", "poka-yoke", "log this mistake", "stop repeating this", "wrap the session", "orient", "lanes", "set up andon", "install the claim-check hook".
license: MIT (code and templates, see reference/LICENSE)
user-invocable: true
---

# Andon — every defect becomes a permanent countermeasure

Andon is the cord on a Toyota line you pull to stop production when something is wrong. This skill is that cord for agent work: catch the defect, fix it once, and make it un-repeatable. The fix is never "remember to"; it is a hook, a test, a rule file, or a schema that catches the class next time.

The full doctrine (11 laws, 5 patterns) and the drop-in kit live under `reference/`. Read this file first; open reference files only when the task needs them.

## The core loop

```
defect → root cause → countermeasure → result
```

A defect is not closed when it is fixed. It is closed when it cannot recur by accident. Prefer countermeasures in this order:

1. **Mechanical** — hook, test, schema, one canonical loader. Skipping it must be a deliberate act.
2. **Rule** — a line in CLAUDE.md or the project rules file that every session reads.
3. **Memory** — a typed memory entry. Weakest; use when nothing mechanical exists yet.

## Two record formats

**Mistakes Log** (one line, lives in CLAUDE.md or the project rules file, cap ~30 active entries):

```
- YYYY-MM-DD — <symptom>. **Correction:** <how to avoid>. **Codified:** <test path / hook / rule / "not yet">
```

`Codified` is the prune signal. Entries with a concrete codification that has held ≥30 days can be pruned. `not yet` entries stay until codified. When ≥3 entries share a root cause, collapse them into one meta-entry.

**Defect Ledger** (four lines per entry, lives in `DEFECT_LEDGER.md` or `docs/`, accumulates across passes):

```
### YYYY-MM — <short title>
**Defect:** what happened, concretely.
**Root cause:** the class, not the instance.
**Countermeasure:** the hook / test / rule that makes the class hard to repeat.
**Result:** what changed after.
```

Add for: operator corrections, a test that failed on first run from a wrong assumption, a "complete" claim with gaps, a claim contradicted by data. Do not add for transient errors, preference shifts, or typos.

## The 11 laws, one line each

1. **Operator as CEO.** Gates advise; the operator decides. Freezes name specific items, never a default posture.
2. **Mistakes Log.** Append-only, one line, three fields. Read every session.
3. **Ready-claim-check.** No "done / shipped / complete / ready / verified" without a verification trail. Mechanical, not aspirational.
4. **Search before building.** Grep the code, check memory, check the tool library. Build only when all come up empty.
5. **Lane discipline.** With ≥2 sessions, claim a lane in LANES.md before working; irreversible lanes are single-session.
6. **Wrap to N places.** Session state goes to ≥2 durable surfaces. One surface is one bad day from gone.
7. **Schema as enforcement.** A convention read from memory by several scripts will drift. One canonical loader.
8. **Operator-trust gate.** Multi-agent consensus is not authorization.
9. **Iteration cap.** Bound retry loops; after N failures, stop and report.
10. **Freeze with explicit scope.** A freeze lists what it freezes.
11. **Memory as typed index.** `MEMORY.md` is a one-line-per-file index; files are prefixed `project_`, `feedback_`, `reference_`, `user_`.

## Procedures

**Log a mistake** (`/log-mistake` in `reference/commands/`): write the one-line entry with today's date, then ask the real question: can this be made mechanical? If a hook or test could stop the class, say so in `Codified` and offer to build it.

**Wrap a session** (`reference/templates/wrap_protocol.md`): trigger at 70–80% context or a milestone. Stop new work. Write a handoff (running / shipped / next / blockers / files touched / tests to run). Update CONTEXT.md. Write to ≥2 surfaces. One line in MEMORY.md. Commit. Print the resume command. Never declare "done" while work is in flow; name what is pending.

**Orient** (`reference/commands/orient.md`): read the memory index, CONTEXT.md, and the last 1–2 recent entries. Then re-read the version-control log since the handoff timestamp; a handoff is a snapshot, not live state. Give a 3-line summary and the single highest-leverage next move. Do not start work.

**Install the kit in a project** (`reference/AGENTS.md`): Layer 1 memory → Layer 2 CLAUDE.md with Mistakes Log → Layer 3 hooks → Layer 4 lanes/commands/agents. Rules that are not optional:

- Ask before overwriting any existing CLAUDE.md or settings.json; show the diff first.
- Hooks go in `warn` mode. The operator promotes to `block`.
- Merge into an existing `"hooks"` object; never paste a second top-level key. Validate the JSON after.
- Smoke-test: `echo '{"transcript_path":"/dev/null"}' | python3 claim_check_hook.py` must print `{"continue": true, ...}`. A traceback means stop and report.
- Confirm Layer 1 works before climbing. One MEMORY.md is a real win.

## Honest limits of the claim-check hook

- It confirms a *fresh* verification entry exists (15-minute window). It does not bind the entry to the claim, and the agent writes its own log. It is a forcing function and audit trail, not proof.
- Regex detection is conservative and tuned per operator (`COMPLETION_VERBS`). Pass reports full of "complete" and "done" will false-fire until tuned.
- It is a Stop hook, checked at turn end, not before a tool call.
- A green verification can still be a wrong verification. For that class, use the `verification-discipline` skill: prove the check can fail before trusting its pass.

## The four failure families

Read enough ledger entries and they cluster. Spot the family and catch the next one early:

- **Claim exceeded evidence** — false "done", fixed-5-claimed-14, tested the proxy not the real path, relayed a finding. *A claim is only as good as the verification behind it.*
- **Decision outran reality** — "it doesn't exist" after one grep, rebuilt what existed, acted on yesterday's handoff. *Check current state, not your memory of it.*
- **System leaned on assumption** — four parsers four schemas, block-mode gate with no escape, test that passed by luck. *If it isn't mechanically enforced, it drifts.*
- **Pressure replaced evidence** — reversed a right answer when asked "you sure?". *A challenge is a request for more evidence, not a reason to fold.*

## Composes with

- `verification-discipline` — the checks this skill's ledger points at; seed the defect and watch the test go red.
- `verification-before-completion` — the per-turn gate; Andon is the cross-session record that makes its lessons stick.
- `investigating-bugs` — root-cause work feeds the Defect Ledger's second line.

## Reference map

```
reference/
├── README.md, QUICKSTART.md, HOOK_INSTALL.md, TROUBLESHOOTING.md, AGENTS.md
├── DEFECT_LEDGER.md                 the author's real defects → countermeasures
├── docs/THE_OPERATORS_CODE.md       full doctrine, 11 laws + 5 patterns (~500 lines)
├── templates/                       CLAUDE.md · MEMORY.md · LANES.md · CONTEXT.md · lane · skill · wrap_protocol
├── hooks/                           claim_check_hook.py · auto_orient.py · log_claim.py · tests/
├── commands/                        wrap.md · orient.md · log-mistake.md
├── agents/                          researcher · auditor · memory-steward · builder · chief-of-staff (briefs, not files to install)
├── scripts/memory_rotate.py         keeps MEMORY.md from bloating
└── examples/sample-project/         a filled-in CLAUDE.md + MEMORY.md
```

Source: https://github.com/PrimeFoldTools/andon (v0.1.0, MIT). Not affiliated with Andon Labs.
