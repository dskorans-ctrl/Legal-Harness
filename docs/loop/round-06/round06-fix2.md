Implemented H1-H4, M1-M9, L1-L7 and A1. L8 unchanged. No commit or ledger edit.
[Full report, files and Librarian IDs checked](/Users/davidskoranski/legal-harness/.workflow/scratch/round06-fix2.md). All 59 controls went RED, restored with `cmp`, then GREEN.

Verified by `tests/test_round06_fix2.py`; test suffixes below:

| Claim | Verified by | Control seed and RED text |
|---|---|---|
| H1 | `practice_defense` | Restore primary: `H1: primary locks in adverse conclusions` |
| H2 | `h2_bills_providers` | Broaden roles: `H2: bills packet includes defense-only providers or has no provider list` |
| H3 | `practice_report` | Clear findings: `H3: report omits documented supporting findings` |
| H4 | `h4_empty_conflict` | Drop warning: `H4: empty conflict block hides missing evidence` |
| M1 | `m1_strongest` | Include both labels: `M1: strongest facts include harmful or unranked facts` |
| M2 | `m2_defense_roles` | Skip roles: `M2: defense view includes our records` |
| M3 | `m3_headings` | Flatten headings: `M3: category heading sits outside its issue subsection` |
| M4 | `m4_conflicts_once` | Disable deduplication: `M4: doctor section repeats a conflict block` |
| M5 | `m5_conflict_categories` | Quote all facts: `M5: conflict includes an unmatched diagnosis category` |
| M6 | `practice_ours` | Restore causation basis: `M6: treatment question rests on a causation opinion` |
| M7 | `practice_defense` | Drop risk: `M7: danger zone omits negative bilaterally` |
| M8 | `practice_defense` | Remove findings question: `M8: primary omits document-based cross tools` |
| M9 | `h3_m9_honest_absence` | Skip disclosure: `M9: report omits unrepresented pages without disclosure` |
| L1 | `l1_jargon` | Restore stage wording: `L1: attorney document contains build jargon` |
| L2 | `l2_human_labels` | Restore IDs: `L2: attorney document exposes raw field labels` |
| L3 | `l3_empty_headings` | Restore headings: `L3: undated page heading has no content` |
| L4 | `practice_report` | Restore rating: `L4: unsupported element labelled present: Permanency rating` |
| L5 | `practice_defense` | Copy primary: `L5: redirect repeats primary` |
| L6 | `l6_deponent_placeholder` | Remove labels: `L6: deposition placeholder is unlabelled` |
| L7 | `l7_date_rule` | Disable guard: `L7: unrelated page date accepted for a dated quote` |
| A1 | `a1_append_failure` | Skip rollback: `A1: append failure replaced the published Word file` |

Files: 8 modules, 6 cards, 12 fixture JSONs, 23 test files and 4 scratch records; exact paths in the report.
[Every moved pin, with old/new values](/Users/davidskoranski/legal-harness/.workflow/scratch/round06-fix2-pins.md). Key facts: 29 → 36; stage 5 lines: 48 → 56.
Adjacent A2 remains: re-extraction cannot correct dates already stored for the same fact/page. Reproduction is in the report. Fresh practice criticism remains required.

Verbatim standalone pytest last line and gate last line:
```text
782 passed in 66.56s (0:01:06)
0
```