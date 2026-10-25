# CARD 00-CHANGE: Change report after an update
Tier: LOCAL | Output: Markdown | Temperature: 0

## Your one job
Tell the attorney, in a few lines, what the latest update changed. The script gives you the counts and lists. Do not add anything.

## Format
```
CASE FILE UPDATED: v[old] to v[new]
Source: [DOC id], [document description], [pages]
Added: [n] ([by section])
Corroborates: [n]   Conflicts: [n]   Supersedes: [n]   Duplicates skipped: [n]
Open items resolved: [list or none]
New open items: [list or none]

POSSIBLY OUT OF DATE:
- [output file]  ([tags that changed])
```
If the script lists no out-of-date outputs, write `POSSIBLY OUT OF DATE: none`.

## Final check
- Every number copied from the script's data. No commentary.
