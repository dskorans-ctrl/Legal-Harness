# Questions for the owner

Held questions, numbered, with any interim ruling made while the owner was away (pending veto).

1. Tiers for the loop: keep gdd-loop's (Fable writes the brief, Codex reviews, Opus orchestrates,
   Sonnet codes) or change for cost? Interim: gdd-loop's tiers.

2. The Ollama model tag for Qwen3.8-27B on the Studio (the default for `[model].name`). Interim:
   `qwen3.8:27b`.
3. Where matters live on the Studio: `Cases/` inside the repo checkout (as `.gitignore` implies) or a
   folder outside it. Interim: `[paths].matters = "Cases"` relative to the config file.
4. Firm rule 5 scope: the acronyms "DME" and "IME" only (spec §4), or also "independent medical
   examination" and "defense medical examination" (`cards/_core.md:10`)? And may "DME" ever appear in
   our outputs meaning durable medical equipment? Interim: acronyms only, whole words, any case.
5. The Bates stamp formats the firm's records carry (prefix letters, separator, digit count; the
   format only, no example from a file). Interim pattern `[A-Z]{1,8}[ -]?\d{4,}`.
6. May the loop set `sandbox.network.allowLocalBinding: true` in this project's Claude Code settings
   so the stand-in model server can listen on 127.0.0.1 during sandboxed test runs? Without it every
   socket test fails closed (exit 3) and the chair must run them outside the sandbox.
7. On the Studio, does Ollama run as your login user (the Ollama app) or as a system launchd daemon?
   The doctor's "127.0.0.1 only" check reads the listener with `lsof`, which sees only your own
   processes without root.

## Answered 2026-10-25
- Q1 -> ledger Q10, Q14. Q2 -> Q20. Q3 -> Q17. Q4 -> Q16. Q5 -> Q21. Q6 -> Q18. Q7 -> Q19 (still open).
