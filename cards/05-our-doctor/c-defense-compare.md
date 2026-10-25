# CARD 05-C: Our doctor vs defense doctor (one opinion)
Tier: LOCAL | Output: JSON (schema: comparison) | Temperature: 0

## Your one job
Put ONE defense opinion next to what our doctor said on the same subject.

## Steps
1. a = defense doctor's opinion quote and cite. b = our doctor's statement on the same subject, or b_quote "OUR DOCTOR HAS NOT ADDRESSED THIS" with empty cite.
2. Note: the facts each side relies on, as each report states them, in one neutral sentence.

## Example
```json
{"items":[{"subject":"Impairment rating","a_label":"Dr. Hale","a_quote":"6% whole person impairment","a_cite":"Hale report p.9, Op. 6","b_label":"Dr. Lee","b_quote":"OUR DOCTOR HAS NOT ADDRESSED THIS","b_cite":"","note":"Dr. Hale's rating rests on non-verifiable radicular complaints; no rating from Dr. Lee in the file."}],
"coverage":"Defense opinion 6 compared."}
```

## Do not
- Do not say which doctor is right. Never write DME or IME.

## Final check
- One item per defense opinion.
