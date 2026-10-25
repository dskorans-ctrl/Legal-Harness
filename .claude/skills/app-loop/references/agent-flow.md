# Agent Flow — the second window: what every agent is doing, live, for no tokens

The loop has two views and they answer different questions.

| | **Loop Watch** (`assets/loop-watch.html`) | **Agent Flow** (`references/bundled/agent-flow/`) |
|---|---|---|
| Answers | What does the loop *mean* right now — round, stage, % and time left, lanes, the finish-line number, what comes next | What are the agents *doing* right now — the chair and every sub-agent as a node graph, each tool call as it happens, a timeline, a file-attention heatmap, the transcript |
| Where | A private claude.ai artifact: any device, the phone included | `http://localhost:3001` on the machine that runs the loop, only |
| Fed by | The chair: one small `ArtifactData` write per event (~100–250 tokens) | Claude Code itself: command hooks plus the session transcripts under `~/.claude/projects/` — **zero model tokens**, nothing for the chair to do |
| Granularity | Events the chair judges worth reporting | Every tool call of every agent, in real time |
| Evidence? | No — a status page | **No** — a viewer. Nothing seen in it ticks a ledger item; the CHECK's own number does |

Agent Flow is by Simon Patole (https://github.com/patoles/agent-flow), Apache 2.0, bundled unmodified
(minus editor config and a screenshot) so the skill stands alone. "Agent Flow" is the author's
trademark: refer to it by name as the origin, never rename a fork after it (`TRADEMARK.md`).

## The owner starts it. The chair never does.

Starting it is three things the chair must not do on its own: it **rewrites `~/.claude/settings.json`**
(adds one command hook to nine events — SessionStart, PreToolUse, PostToolUse, PostToolUseFailure,
SubagentStart, SubagentStop, Notification, Stop, SessionEnd — preserving the hooks already there),
**installs `~/.claude/agent-flow/hook.js`**, and the published `npx` build **downloads from npm and ships
opt-out telemetry** (session count and duration, event count, OS/arch, version, model ids, error class
names — no prompts, paths or tool calls — to the author's Supabase project). Global hook configuration
is the owner's security surface. So:

- At session start, after Remote Control, check read-only whether the hook is installed
  (`grep -c "agent-flow/hook.js" ~/.claude/settings.json`) and say one line: either "Agent Flow's hook
  is installed — start the viewer when you want the live graph" or "Agent Flow is not set up; here is
  the command". Never block on it and never mention it again that session unless asked.
- Give the owner the command; do not run it, do not edit any settings file for it, do not install it
  for a sub-agent.

The quick start, telemetry off, run by the owner in their own terminal:

```bash
AGENT_FLOW_TELEMETRY=false npx agent-flow-app
```

Options: `--port <n>` (default 3001), `--no-open`, `--verbose`. From the bundled source instead of npm
(the source build sends no telemetry at all): in `references/bundled/agent-flow/`, `pnpm i`, then
`pnpm run setup` (the hook install) and `pnpm run dev` (web app on 3000, relay on 3001). Needs Node 20+.

With the viewer closed the hook is harmless: it looks for a live listener, finds none and exits 0 inside
its 2-second timeout — it cannot fail a tool call. To remove everything (hooks from every settings file
it touched, then `~/.claude/agent-flow/`): `node references/bundled/agent-flow/extension/scripts/uninstall.js`,
also the owner's to run.

## What it is good for in a round

- **Is the lead alive?** A lane lead that has ended its turn with children still running (Mistakes
  Log 2026-09-10) shows as a finished node with live children under it — visible at a glance, hours
  before a missing completion notice would be noticed.
- **Two engines at once, a worker polling in a loop, a watcher left armed** — the failure classes in
  catalog #34, #40 and #43–#53 are all *shapes* in the graph: parallel Bash nodes on the engine, a
  ladder of identical calls, a node that never closes.
- **Where the time went** — slow tool calls and redundant reads are visible per agent, which the agent
  log's one elapsed figure per worker cannot show.

It does not replace the agent log (tokens and outcomes per worker, committed with the round) or the
chair's completion checklist. If the graph and the log disagree, the log and the process table win and
the disagreement is a finding.

## Under the Loop Watch header

Served from the loop machine, the Loop Watch page frames this viewer directly under its live header
(`references/agent-log.md`, "One page, two places"): `http://127.0.0.1:3002/docs/loop/loop-watch.html`.
The published claude.ai page cannot — it shows a note in that slot instead.

## Observed on the project that produced this skill (2026-09-21)

Run by the owner as `AGENT_FLOW_TELEMETRY=false npx agent-flow-app` (v0.9.1): it installed
`~/.claude/agent-flow/hook.js`, added its hook to nine events in `~/.claude/settings.json`, wrote no
`~/.agent-flow/` directory (telemetry off), and **a session started from the Claude desktop app appeared
at once** as a live node with its tool calls and token count. It serves no `X-Frame-Options` or CSP, so
it frames cleanly.
**Sub-agents appear as child nodes.** The round-9 brief writer, spawned with the Agent tool from a
desktop-app session, showed within seconds as a second hexagon linked to the chair's, with its own tool
calls and token count ("2 agents" in the viewer's header).
