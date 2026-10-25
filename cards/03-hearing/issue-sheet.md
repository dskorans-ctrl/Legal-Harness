# CARD 03-ISSUE: Issue sheet (one issue)
Tier: LOCAL | Output: JSON (schema: factsheet) | Temperature: 0

## Your one job
List the facts for and against ONE issue before the Board, each with cite and entry ID.

## You receive
- Snapshot, the issue as stated in the petition, case file entries tagged with that issue (records, opinions, testimony).

## Steps
1. One fact per entry. Copy quote, cite, entry ID, V or S.
2. `use`: our_case, defense_case, both, or danger.
3. Testimony cites use page:line.

## Example
```json
{"facts":[{"fact":"Dr. Hale rated 6% lumbar","quote":"6% whole person impairment","cite":"Hale report 6/4/26 Op. 6","entry_id":"OP-0007","verified":"V","use":"defense_case"}],
"coverage":"Issue: permanency. Entries reviewed: 12. Facts: 1."}
```

## Do not
- Do not state the legal standard. The attorney supplies it.

## Final check
- Every fact has an entry ID.
