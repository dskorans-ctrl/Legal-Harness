# CARD 04-G: Concessions, labels, danger zone
Tier: LOCAL_REVIEW for concessions and labels; danger zone reviewed by attorney | Output: JSON (schema: concessions) | Temperature: 0

## Your one job
From the report and earlier findings, list three things.

## 1. Concessions
Every statement that helps the claimant, word for word: causally related diagnoses, treatment reasonable (to any date), bills reasonable, any rating, restrictions, recommended treatment, positive findings, complaints called consistent or credible. Treatment and bills are separate items.

## 2. Undefined labels
Terms like "symptom magnification", "non-physiologic", "no objective findings", "resolved". For each, the specific findings the report gives. If none: write the pages searched in `none_stated_pages`.

## 3. Danger zone
Facts that cut both ways or the defense will rely on: effort or validity concerns, prior conditions, inconsistent histories, findings with another explanation the record mentions, gaps. Each with cite and one line on why not to open it.

## Example
```json
{"concessions":[{"type":"treatment_reasonable","quote":"Treatment through 11/21/25 was reasonable and necessary","cite":"Hale report p.9, Op. 4"}],
"undefined_labels":[{"label":"non-verifiable radicular complaints","cite":"Hale report p.9","supporting_findings":[],"none_stated_pages":"Hale report pp.1-9"}],
"danger_zone":[{"fact":"Primary care note 12/5/23 records prior low back pain","cite":"(B3 14)","why_not_to_open":"Gives the doctor a prior-condition explanation."}],
"coverage":"Report pages 1-9 and passes A-F reviewed."}
```

## Final check
- Concessions word for word. "None stated" only with pages searched.
