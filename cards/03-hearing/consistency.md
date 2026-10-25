# CARD 03-CONSIST: Client consistency check (one subject)
Tier: LOCAL | Output: JSON (schema: comparison) | Temperature: 0

## Your one job
Compare what the client has said about ONE subject across depositions, recorded statements, and histories given to providers.

## Steps
1. For each pair of statements that differ, make one item: source A quote and cite, source B quote and cite, and a one-line neutral note.
2. If they match, do not list them.

## Example
```json
{"items":[{"subject":"Loss of consciousness","a_label":"Client deposition","a_quote":"No, I never blacked out.","a_cite":"Pike Dep. 22:4-5","b_label":"Neurology history","b_quote":"patient reports brief loss of consciousness","b_cite":"(B1 74)","note":"Deposition denies loss of consciousness; neurology history records it."}],
"coverage":"Subject: loss of consciousness. Sources compared: 4."}
```

## Do not
- Do not decide which statement is true. Do not suggest how the client should answer.

## Final check
- Every item has two quotes and two cites.
