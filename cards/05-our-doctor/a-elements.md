# CARD 05-A: Elements check
Tier: LOCAL | Output: JSON (schema: elements) | Temperature: 0

## Your one job
For our doctor's report or notes, mark each of 14 elements STATED, PARTIAL, or NOT_FOUND.

## Elements
treating_relationship, mechanism, history_prior_conditions, exam_findings, imaging_reviewed, diagnosis, causation, treatment_reasonable_necessary_related, bills_reasonable_related, work_status_restrictions, mmi, permanency_rating, future_treatment, records_reviewed

## Rules
- STATED: the doctor wrote it. Quote it.
- PARTIAL: something related but not the element itself (a diagnosis but no causation statement; "related" with no probability wording). Quote what is there; `absent_note` says what is missing in one neutral sentence.
- NOT_FOUND: give `pages_searched`.
- Treatment and bills are separate elements. A treatment statement does not cover bills.
- Copy work status marks exactly (temporary or permanent).
- Never suggest what the doctor should write.

## Example
```json
{"elements":[
{"element":"causation","status":"PARTIAL","quote":"lumbar radiculopathy related to work injury","cite":"(B1 148)","absent_note":"No probability wording.","pages_searched":"B1 140-175"},
{"element":"bills_reasonable_related","status":"NOT_FOUND","quote":"","cite":"","absent_note":"","pages_searched":"B1 140-175"}],
"coverage":"Our doctor records B1 140-175. Elements reported: 2 of 14 shown in example."}
```
In real output, list all 14 elements.

## Final check
- 14 elements. Nothing STATED without the doctor's own words.
