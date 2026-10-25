# Legal Harness (casefile)

A local case system for a personal injury and workers' compensation practice. It runs on a Mac Studio
with a local model (Qwen3.8-27B through Ollama), reads client and medical records, keeps a verified
case file and a running medical memo per matter, and builds deposition prep, hearing prep and
anonymized brief packages. Client data never leaves the Studio.

- Design: `docs/spec.md`
- Build process: rounds run with the `app-loop` skill; start at `docs/loop/HANDOFF.md`
- Status: seeded 2026-10-25; nothing built yet

Private repository. No client records, names or facts are ever committed here.
