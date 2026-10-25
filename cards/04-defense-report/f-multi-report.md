# CARD 04-F: Two reports by the same doctor (one subject)
Tier: LOCAL | Output: JSON (schema: comparison) | Temperature: 0

## Your one job
Compare what the doctor's earlier and later reports say on ONE subject (history, a finding, a diagnosis, or an opinion).

## Steps
1. One item per difference: earlier report quote and cite (a), later report quote and cite (b), one neutral sentence.
2. Also list any recommendation in the earlier report (a test or evaluation) and whether the later report mentions its result.

## Example
```json
{"items":[{"subject":"Lasegue left","a_label":"Hale report 11/5/25","a_quote":"Lasegue: Positive left","a_cite":"Hale report 11/5/25 p.5","b_label":"Hale report 6/4/26","b_quote":"no tension signs","b_cite":"Hale report 6/4/26 Op. 3","note":"Earlier exam recorded positive left Lasegue; later report states no tension signs."}],
"coverage":"Subject: tension signs. Both reports compared."}
```

## Do not
- Do not ask or suggest why it changed.

## Final check
- Two quotes, two cites per item.
