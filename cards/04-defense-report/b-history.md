# CARD 04-B: History check
Tier: LOCAL | Output: JSON (schema: comparison) | Temperature: 0

## Your one job
Compare the history in the report with the records on ONE subject: mechanism, prior conditions, job duties, or current complaints.

## You receive
- The report's history quotes for that subject.
- Case file entries on the same subject.

## Steps
1. For each difference, one item: report quote and cite (a), record quote and cite (b), one neutral sentence.
2. Watch for family history the report records as the patient's own.
3. If they match, list nothing.

## Example
```json
{"items":[{"subject":"Prior low back history","a_label":"Hale report","a_quote":"chronic history of low back pain since a 2014 motor vehicle accident","a_cite":"Hale report p.3","b_label":"Primary care 12/5/23","b_quote":"low back pain, midline, intermittent","b_cite":"(B3 14)","note":"Report says chronic; the only prior record says intermittent."}],
"coverage":"Subject: prior conditions. Report pages 3-4. Entries compared: 5."}
```

## Do not
- Do not call the doctor wrong. Describe the difference only.

## Final check
- Every item has two quotes and two cites.
