# CARD 04-D: Summary accuracy (one entry)
Tier: LOCAL_REVIEW | Output: JSON (schema: summary_accuracy) | Temperature: 0

## Your one job
Compare ONE record summary in the report with the record it summarizes.

## Labels
- ACCURATE: matches.
- SELECTIVE: accurate, but leaves out part of the same passage. Put the full passage in record_quote.
- INACCURATE: says something the record does not say.
- NO_PRIMARY: we do not have the record.

## Example
```json
{"results":[{"report_quote":"Dr. Lee agreed the patient had reached MMI","report_cite":"Hale report p.4","record_quote":"He may be approaching MMI from a musculoskeletal standpoint; neurologic workup pending.","record_cite":"(B1 171)","label":"INACCURATE","note":"Record says approaching MMI from a musculoskeletal standpoint with workup pending; report says reached MMI."}],
"coverage":"1 summary entry checked."}
```

## Final check
- Quotes word for word from each source.
