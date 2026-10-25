---
name: orchestrator
description: Chair discipline for multi-agent work (Rylaa/fable5-opus5-orchestrator). Use when a job is big enough to delegate — a multi-phase plan, 3+ tracker tasks, bulky research, or parallel edits — and the chair must clarify first, write a Requirements Ledger, route work by tier and effort, and close with a fresh verifier. Trigger on "orchestrate", "delegate this", "spin up workers", "fan out", "requirements ledger", "clarify before delegating", "which tier should do this", "fresh-eyes verification", "wrap the close".
license: MIT (see reference/plugin/LICENSE)
user-invocable: true
---

# Orchestrator — Fable asks and decides, Sonnet does the volume, Opus takes the hard slices

The chair's tokens are for judgment. Delegated bulk work preserves the window and the usage limit. When the limit and context hygiene conflict, the limit wins. Workers cannot ask the user anything, so every ambiguity is resolved before the first spawn, on the record, and a fresh agent closes the job.

This skill is the advisory form. The upstream is a Claude Code plugin whose four hooks make the same rules mechanical; it is bundled unchanged under `reference/plugin/` and can be installed from there (see the last section). Without the hooks, the discipline below depends on you following it.

## Rule 0 — threshold

Orchestrate when work produces bulky intermediates or independent phases. Hard cap on solo work: a multi-phase plan or 3+ tracker tasks is over the threshold even as an approved plan. Workers run the phases; you sequence them. The chair codes directly only single-sitting diffs, roughly three files or fewer. A bounded, context-heavy follow-up may fork (at most 2 per session, only while the conversation is short).

## Rule 0.5 — clarify before you commit

Read the repo first; never ask what it answers. Code shows what is, never what they want. Then ask at the start, before the ledger and before any spawn, in front-loaded rounds. One `AskUserQuestion` carries four questions. Answers reshape the map, so the next round derives from them. No cap on rounds.

Scan seven axes at every size. Each one that is unresolved and would change the work is a question:

1. **Scope edge** — what is deliberately out.
2. **Acceptance** — how "done" is observed: the test, the command, the screen.
3. **Constraints** — compatibility, dependencies, budget, what must not move.
4. **Ownership of choices** — whose taste decides each call.
5. **Priority conflict** — when speed, correctness, and token cost disagree, which wins here.
6. **Contact with what exists** — which file, pattern, or contract this touches.
7. **Failure behaviour** — what happens on error, what rollback looks like.

Filter: would a different answer produce different code? If not, do not ask. One question is exempt and always asked: does the work land on the branch checked out now, or a new one?

Stop condition: no `?` is unanswered under `## Clarified`, and you could write a worker's spec without guessing at any part. A recommendation is a proposal; the record holds what the user picked. After the go, the window is closed. A genuine unknown mid-work stops the work, goes to the user, and is named a clarify miss in the close report.

## Rule 1 — the Requirements Ledger

Before any delegation, write `./.workflow/LEDGER.md` (any `LEDGER*.md`; `LEDGER-<topic>-archive.md` is retired):

```markdown
## Clarified
- Q1: does this replace the old exporter, or run beside it? -> beside it, for one release
- Q2: is the CSV column order part of the contract? -> yes, downstream parses by position
- Branch: main, the checkout in place

- [ ] 1. Every explicit requirement, one line each
- [ ] 2. Implicit expectations and constraints too
- [x] 3. Marked done only after verification confirms it
- [~] 4. deferred: user approved postponing this
- [ ] V. fresh-eyes verification passed
```

Rules the hooks read by: every `## Clarified` bullet's last `?` has a `->` answer; no `Assumption:` line; at least one answered question; a `Branch:` line; plain bullets only, since any checkbox line ends the section. `- [x]` means addressed and verified. `- [~] deferred:` needs user approval. `V.` is always last and closed only by the verifier. Phases cite item numbers. Discoveries are appended. Write the ledger and the first worker wave in one message.

## Rule 2 — the filesystem is shared memory

Bulk lives in `./.workflow/scratch/`. Agents return paths plus briefs, never dumps. Every subagent report, at most 40 lines total:

1. ledger items addressed, by number
2. summary
3. verbatim code, config, errors, or quotes the conclusion depends on, at most 10 lines inline; longer goes to scratch with the path
4. confidence: "confident" or "uncertain because X"
5. "out of scope but noticed"

A violating report is rejected and re-run, never silently accepted.

## Rule 3 — spawn discipline

- Batch similar mechanical lookups into one worker with a checklist. Five greps is one agent, not five. Every spawn pays a fixed overhead before useful work.
- Spawn independent agents in one message. Read-only agents share the repo; parallel editors each get `isolation: "worktree"`.
- Name every substantive worker (implementation, review, research, verification) so the user can watch it. Only sub-minute lookups stay unnamed.
- Steer a running worker with SendMessage. Once its report is accepted with no follow-up planned, dismiss it with `{"type": "shutdown_request"}`. Never leave finished workers stacked.
- Forks clone your full conversation at your model and spend the limit. Forking a plan's phases is disguised solo work.

## Routing and effort

Tier names only: sonnet, opus, fable. Never dated IDs, no haiku.

| Work | Tier |
|---|---|
| Questions, planning, arbitration, decisions | the chair |
| Implementation, tests, refactors, briefs, standard review | sonnet |
| Bulk gathering: fetch, grep, scan | sonnet, low effort |
| Architecture, irreversible migrations, complex multi-system work, stubborn debugging, all security review | opus, directly |
| A sonnet "uncertain" | escalates to opus, then fable |
| Fresh-eyes verification | opus or fable; security always on opus |

Effort per spawn: low for mechanical, medium for routine spec work, high for multi-file implementation, debugging, or review, xhigh for the hardest agentic work, max for architecture, migrations, security, and escalations. Unsure, round up.

Escalation is one-way. A decline reruns unchanged on another tier. If that declines too, stop and tell the user. Never reword past a classifier.

**Opus-chair fallback.** When the Fable limit is spent and the chair moves to Opus, the same rules hold with one change: do not spawn fable agents. Opus takes the escalation ceiling and every verification. The delta notes are in `reference/plugin/instructions/`.

## Research pipeline

You pick the questions and sources, never a fetch worker. One sonnet (medium) per source: it saves the source verbatim to scratch first, as the audit trail, then returns a brief built from that disk copy with claims, evidence, exact quotes, confidence, contradictions, and the path. A final sonnet (high) synthesizes across the briefs. You check the synthesis and its verbatim evidence against the ledger and decide. Intermediates never enter your context.

## Verification — mandatory before closing

The verifier is fresh: it did not work on the task. Give it the original request, the ledger path, and the work-product paths (diffs, reports, not the raw scratch dump). Its only job is to find what is missing, wrong, or unaddressed, item by item. Only it ticks `V.`. Effort scales with blast radius: max for architecture, irreversible changes, security, and the largest closes; high is allowed for small, low-risk, non-security closes. Findings become new phases; re-verify after fixes. Cap: 3 verify-fix cycles, then stop and report the open items to the user. Do not end a turn with open `- [ ]` items without finishing them, deferring with approval, or saying so.

## Chair hygiene

Consume briefs and verbatim snippets; bulk stays on disk. When a decision hinges on short exact content, read it yourself; never decide on a summary when the source fits in a few hundred lines. Prefer per-task sessions: ledger and scratch survive a clear, so finish a task, close it, and start the next one clean. Parallelize independent calls. Keep outputs minimal.

## Red flags

| Thought | Reality |
|---|---|
| "I get the gist, I'll start" | The gist is the part you already knew. The ambiguity is the rest. |
| "I'll write it as an assumption" | An assumption is a question you chose not to ask. |
| "I'll ask when I get there" | You get there with three workers running. |
| "The worker will figure it out" | Workers cannot reach the user. Your ambiguity becomes their guess. |
| "Nothing here is ambiguous" | The branch question is still asked. The section is never empty. |
| "I'll run the phases myself, the plan is approved" | Over the threshold. Workers run phases; you sequence them. |

## Composes with

- `verification-discipline` — what the fresh verifier applies; a green check has to have gone red on a seeded defect before it closes `V.`.
- `andon` — a clarify miss or a survived verification cycle is a Defect Ledger entry with a countermeasure.
- `verification-before-completion` — the per-claim gate every worker report is held to.

## Installing the mechanical version

The bundled plugin adds four hooks: SessionStart injects the chair profile; PreToolUse denies Agent, Task, Workflow, and TaskCreate calls over 1500 characters (and the third tracker task) while no clarified ledger exists; Stop holds the first turn-end with open ledger items, once per session; SessionEnd clears the session cache and reaps finished tmux teammate panes. It also writes a local metrics log. All of it is configurable by env var (see `reference/plugin/README.md`). It fires in every project once installed, so install it deliberately:

```
/plugin marketplace add <path to reference/plugin>
/plugin install orchestrator@fable-orchestrator
```

Needs python3 on PATH, macOS or Linux, and a restart. Tests: `python3 -m pytest tests/ -q` inside the plugin folder (232 tests as of v0.23.0).

## Reference map

```
reference/plugin/                   the upstream plugin, unmodified (v0.23.0)
├── README.md                       install, gates table, env vars, limitations
├── .claude-plugin/                 plugin.json · marketplace.json
├── hooks/hooks.json                the four hook registrations
├── scripts/                        inject_instructions · ledger_guard_spawn · ledger_guard_stop · cleanup_session_cache · stats
├── instructions/                   dynamic-workflow-fable.md · dynamic-workflow-opus.md · profile-switch-to-*.md
├── skills/                         clarify/SKILL.md · playbook/SKILL.md (the full upstream text)
└── tests/                          232 end-to-end hook tests
```

Source: https://github.com/Rylaa/fable5-opus5-orchestrator (Yusuf Demirkoparan, MIT).
