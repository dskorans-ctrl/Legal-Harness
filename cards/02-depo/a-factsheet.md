# CARD 02-A: Deposition fact sheet
Tier: LOCAL | Output: JSON (schema: factsheet) | Temperature: 0

## Your one job
List the facts about ONE topic that matter for this deponent. Each fact keeps its quote, cite, and case file entry ID.

## You receive
- Snapshot, deponent name and type, the topic.
- Case file entries for that topic.

## Steps
1. One fact per entry that bears on the topic.
2. Copy the quote and cite from the entry. Copy the entry ID. Copy V or S.
3. Set `use`: our_case, defense_case, both, or danger (cuts both ways or the defense will use it).

## Do not
- Do not merge two entries into one fact. Do not add facts that are not in the entries.

## Example
```json
{"facts":[
{"fact":"Restrictions marked temporary on 8/18/25","quote":"[X] Temporary","cite":"(B1 148 / footer p.2)","entry_id":"WS-0004","verified":"V","use":"danger"},
{"fact":"Note records patient could not perform light duty","quote":"he has not been able to perform even that","cite":"(B1 165 / footer p.3)","entry_id":"CH-0102","verified":"V","use":"our_case"}],
"coverage":"Topic: work status. Entries reviewed: 9. Facts listed: 2."}
```

## Final check
- Every fact traces to an entry ID.
