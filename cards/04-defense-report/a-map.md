# CARD 04-A: Map the defense doctor's report
Tier: LOCAL | Output: JSON (schema: report_map) | Temperature: 0

## Your one job
Pull the structure of the report: who, when, what records, what history, what findings, what opinions. Copy exactly.

## You receive
- One chunk of the report (it may take several requests for a long report).

## Steps
1. Copy doctor, specialty, exam date, report date, and signature date separately.
2. Copy the list of records reviewed, item by item, exactly as listed.
3. Copy the history the doctor recorded, by subject (mechanism, prior conditions, complaints).
4. Copy exam findings test by test, with side and result.
5. Copy diagnoses and each opinion, numbered as in the report, word for word.
6. Fields not in this chunk: NOT STATED IN PAGES PROVIDED, or an empty list.

## Example
```json
{"doctor":"Victor Hale, M.D.","specialty":"Orthopaedic surgery","exam_date":"06/04/2026","report_date":"06/30/2026","signature_date":"07/25/2026","body_parts":["lumbar spine"],
"records_listed":[{"as_listed":"Harbor Orthopaedics 3/24/25-11/21/25","cite":"Hale report p.2"}],
"history":[{"subject":"prior conditions","quote":"chronic history of low back pain since a 2014 motor vehicle accident","cite":"Hale report p.3"}],
"exam_findings":[{"test":"Straight leg raise","side":"left","result_quote":"negative","cite":"Hale report p.5"}],
"diagnoses":[{"quote":"Lumbar strain, resolved","cite":"Hale report p.7"}],
"opinions":[{"number":"6","quote":"6% whole person impairment for non-verifiable radicular complaints","cite":"Hale report p.9, Op. 6"}],
"coverage":"Report pages 1-9 of 9."}
```

## Final check
- Opinions word for word. Exam, report, and signature dates kept separate.
