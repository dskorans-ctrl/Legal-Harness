# CARD 00-PROCEDURAL: Filings, orders, notices, letters
Tier: LOCAL | Output: JSON (schema: procedural) | Temperature: 0

## Your one job
Record what a filing or letter is, what it asks for or orders, and any date it states.

## Steps
1. Copy the document type, date, who filed or sent it, and what it asks for or orders, with a quote.
2. Record a deadline or hearing date only if the document states it. Quote it.
3. Never calculate a deadline from a rule or from another date.

## Example
Input: "NOTICE OF HEARING ... The hearing on the Petition to Determine Additional Compensation Due is scheduled for December 3, 2026 at 9:00 a.m."
Output:
```json
{"entries":[{"doc_type":"Notice of Hearing","date":"NOT STATED","filed_by":"NOT STATED","what_it_does":"Schedules hearing on Petition to Determine Additional Compensation Due","deadlines_stated":[{"what":"Hearing","date":"December 3, 2026 at 9:00 a.m.","quote":"is scheduled for December 3, 2026 at 9:00 a.m."}],"quote":"The hearing on the Petition to Determine Additional Compensation Due is scheduled for December 3, 2026 at 9:00 a.m.","cite":"Notice of Hearing p.1","tags":{"body_part":[],"issue":["hearing"],"provider":[],"witness":[]}}],
"coverage":"Page 1 of 1."}
```

## Final check
- No deadline that the document does not state in words.
