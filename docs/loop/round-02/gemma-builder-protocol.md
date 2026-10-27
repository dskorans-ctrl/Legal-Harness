# Round 2 builder protocol: Gemma 4 e4b writes the code (owner Q28)

The §2 Sonnet builder prompt assumes an agent that reads the repo, runs tools, commits and reports.
`gemma4:e4b-it-qat` (7.5B, Q4, Ollama on this Mac) can do none of that: it sees one prompt and answers
with text. So the Opus orchestrator (the chair) takes every agent duty and Gemma only writes code.

## Who does what
- **Gemma**: one task, one answer: a whole file (`=== FILE: path ===`) or one function
  (`=== FUNCTION: path::name ===`). No tools, no repo access, no memory between tasks.
- **Driver** `scripts/gemma_task.py`: inlines the context files the task names, calls Ollama
  (temperature 0.2, 32k context, thinking on unless `--no-think`), writes only `--allow` paths, splices a
  function by AST, logs every exchange to `.workflow/scratch/gemma/`. Fails closed: a truncated answer
  (`done_reason=length`) exits 3 and writes nothing; no usable block exits 2; a path outside `--allow`
  exits 4; a splice that does not parse exits 6. Smoke tested 2026-10-26: whole file, function splice,
  truncation (nothing written, `cmp` unchanged).
- **Opus orchestrator**: writes each task file from the brief's Gemma task list; picks the context
  files; runs the CHECK and the suite; writes feedback; seeds and restores (`cmp`); commits with
  targeted paths; reads the Librarian pre-flight for Gemma (the model never sees `Librarian.md`, so the
  task file carries the one or two entries that apply, in plain words).

## How a task file is written for a small model
1. One file or one function. At most about 120 lines of answer.
2. Exact signature, imports, return type, error type and message text. Quote the signature of every
   project function it must call, with its file:line. Never "use the existing helper".
3. Inputs and expected outputs as literal examples (three to five), including one failure case.
4. The context it needs inlined (the file being edited, the module it calls), nothing else: the
   smaller the prompt, the better the answer.
5. Forbidden moves stated: no new dependencies, no network, no printing client data, no em or en dashes.
6. Tests are their own tasks, written against the brief's CHECK, never by the same call as the code.

## The loop per task
1. Run the driver. 2. Run the task's test and `scripts/run.sh pytest -q`. 3. On red, write a feedback
file with the failing assertion and the traceback's last lines (under 40 lines) and re-run with
`--feedback`. 4. Three attempts, then one re-split into smaller tasks (three attempts each). 5. Still
red: Sonnet 5.5 writes that item (Q28 fallback), logged as a deviation in the agent log and the round
report, so the Fable comparison review can count it.

## What is measured for the owner
Per task: attempts, seconds, prompt and answer tokens, pass or fallback. Totals go in the round report
next to the round 1 Sonnet numbers.
