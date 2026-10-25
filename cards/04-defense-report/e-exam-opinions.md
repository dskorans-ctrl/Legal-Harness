# CARD 04-E: Exam findings and opinion basis (one opinion)
Tier: LOCAL_REVIEW | Output: JSON (schema: opinion_basis) | Temperature: 0

## Your one job
For ONE opinion in the report: list the related exam findings, check each fact it relies on against the record, list tests not done, and list anything dated after the exam.

## Steps
1. related_findings: findings in the same report that relate to this opinion, positive and negative.
2. facts_relied_on: each fact the report says supports the opinion. Check against the case file: CONFIRMED, DIFFERS (give the record quote and cite), or NOT_IN_RECORD.
3. tests_not_performed: tests the report shows were not done, deferred, or declined. Quote.
4. after_exam_items: treatment, tests, or records dated after the exam date.

## Do not
- Do not judge whether the opinion is medically right. Do not explain why findings differ.

## Example
```json
{"opinions":[{"opinion_quote":"6% whole person impairment for non-verifiable radicular complaints","opinion_cite":"Hale report p.9, Op. 6",
"related_findings":[{"quote":"Lasegue: negative left","cite":"Hale report p.5"}],
"facts_relied_on":[{"fact_quote":"no electrodiagnostic evidence of radiculopathy","report_cite":"Hale report p.8","check":"DIFFERS","record_quote":"EMG denied pending IME results","record_cite":"(B1 172)"}],
"tests_not_performed":[{"quote":"EMG not available for review","cite":"Hale report p.8"}],
"after_exam_items":[]}],
"coverage":"Opinion 6. Report pages 5-9."}
```

## Final check
- Every DIFFERS has both quotes.
