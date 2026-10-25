# Bundled third-party skills

`gdd-loop` composes three upstream skills and one upstream tool. They are bundled here so the skill stands alone.

| Skill | Source | Licence | What is bundled |
|---|---|---|---|
| orchestrator | https://github.com/Rylaa/fable5-opus5-orchestrator (Yusuf Demirkoparan) | MIT | `orchestrator/SKILL.md` and the full plugin under `reference/plugin/` (hooks, scripts, tests) |
| andon | https://github.com/PrimeFoldTools/andon | MIT | `andon/SKILL.md` and the full kit under `reference/` (doctrine, templates, hooks, commands, agents) |
| verification-discipline | https://github.com/PrimeFoldTools/verification-discipline | code MIT; **prose all rights reserved (Collin Nerdahl)** | only the MIT code: `reference/gate-mutation-example/` (a runnable mutation-check harness). The prose (SKILL.md, README, CASE_STUDY, WHAT_THIS_DOES_NOT_PROVE, mistakes-log-excerpt) is **not** redistributed; `gdd-loop/SKILL.md` states the discipline in its own words and links to the upstream for the essays |
| agent-flow | https://github.com/patoles/agent-flow (Simon Patole) | Apache 2.0; the name "Agent Flow" and its logo are the author's trademarks (`TRADEMARK.md`) | the source tree unmodified, minus `.vscode/`, `.github/` and `extension/media/screenshot.png`; nothing built, no `node_modules`. How the loop uses it: `references/agent-flow.md` |

Keep each `LICENSE` file with its directory. Before sharing `gdd-loop` outside your own machine,
re-check the upstream licences; the verification-discipline prose may not be republished without
written permission.
