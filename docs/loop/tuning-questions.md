# Tuning questions

Values settled by the benchmark, not by argument: the as-built value, its file:line, what the
benchmark says, and what to watch for.

- T-1 (round 1 brief, D-7): rule `no-dme-ime` patterns `\bDME\b`, `\bIME\b`, case-insensitive, in
  `playbook/rules.toml`. `DME` also means durable medical equipment in medical bills; watch for
  findings whose excerpt is followed by "supplier", "equipment" or "provider". Benchmark: stage 4.
- T-2 (round 1 brief, D-7): rule `no-hired-paid-retained` pattern list (`hired|paid|retained|referred
  by`, `fee(s)`, `how many exams`, `exams per year`). Watch for misses in the depo question benchmark
  (stage 6) and for `fee` false hits on "fee schedule" in bills.
- T-3 (round 1 brief, D-7): rule `treatment-and-bills-apart` term groups (treatment, therapy, surgery
  versus bill, charges, invoice, paid). Watch for a question about "paid time off" tripping it.
- T-4 (round 1 brief, D-9): the stand-in's token estimate `prompt_eval_count = chars // 4 + 8`. Replace
  with the real model's counts recorded on the Studio at stage 9 before any truncation threshold is
  tuned on it.
