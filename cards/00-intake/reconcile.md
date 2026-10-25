# CARD 00-RECONCILE: Compare one new fact with the case file
Tier: LOCAL (SUPERSEDES results go to attorney review) | Output: JSON (schema: reconcile) | Temperature: 0

## Your one job
Decide how ONE new fact relates to existing case file entries. The script builds the update from your answer.

## You receive
- One candidate fact (verified quote and cite) with a `candidate_ref`.
- Up to 8 existing active entries with the same tags and nearby dates, each with an entry ID.

## Choose one relation
| Relation | Use when |
|---|---|
| NEW | Nothing existing covers it |
| DUPLICATE | Same fact, same source pages (record produced twice) |
| CORROBORATES | Same fact, from a different source |
| SUPERSEDES | The new document says it amends, corrects, or replaces the earlier one. Quote where it says so. |
| CONFLICTS | It says something different about the same subject |
| RESOLVES | It is the primary record behind an existing secondhand (S) entry or open item |

## Rules
- A later visit with a different finding is NOT a supersession. If it disagrees with an earlier statement on the same subject, it is CONFLICTS.
- SUPERSEDES needs `quote_supporting_relation` showing the document says it replaces the earlier one. No such words means it is not SUPERSEDES.
- When unsure between CONFLICTS and anything else, choose CONFLICTS.

## Example
Candidate: "Mechanism: patient lost consciousness and the truck left the road" (Neuro note, B1 74).
Existing: CH-0041 "Mechanism: brakes failed, no loss of consciousness" (ER, B1 3).
Output:
```json
{"candidate_ref":"NEW-12","relation":"CONFLICTS","linked_ids":["CH-0041"],"reason":"Neurology history records loss of consciousness; ER history records none.","quote_supporting_relation":"","coverage":"Compared 1 candidate with 3 existing entries."}
```

## Final check
- linked_ids lists every entry the relation refers to. NEW has an empty list.
