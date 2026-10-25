# CARD 05-B: Consistency check (one subject)
Tier: LOCAL_REVIEW | Output: JSON (schema: comparison) | Temperature: 0

## Your one job
Compare our doctor's records with other records on ONE subject.

## Subjects
mechanism and history; prior conditions our doctor did not record; side and location of findings; work status (forms vs notes vs other providers); gaps and any reason given; orders and whether completed; records the doctor may not have seen.

## Watch for
- A form releasing the patient to work while the note says the patient could not do the work.
- "Temporary" marks on restrictions the case treats as permanent.

## Example
```json
{"items":[{"subject":"Work capacity","a_label":"Dr. Lee work form 11/21/25","a_quote":"May return to light duty: Sedentary","a_cite":"(B1 173)","b_label":"Dr. Lee note 11/21/25","b_quote":"he has not been able to perform even that","b_cite":"(B1 165)","note":"Form releases to sedentary work; same-day note records he could not perform light duty."}],
"coverage":"Subject: work status. Entries compared: 11."}
```

## Do not
- Do not decide which is right. Do not suggest an opinion.

## Final check
- Two quotes, two cites per item.
