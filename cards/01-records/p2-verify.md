# CARD 01-P2: Claim verification
Tier: LOCAL | Output: JSON (schema: verify) | Temperature: 0

## Your one job
Check extracted items against their source page. Be strict.

## You receive
- Up to 10 extracted items (each with an `item_ref`), all from the same page.
- The full text of that page.
The script has already confirmed each quote appears on the page.

## Steps
For each item, answer one label:
- SUPPORTED: the summary says only what the page says, with the right attribution, date, body part, and side.
- OVERSTATED: the summary adds certainty, severity, causation, side, or meaning. Give `corrected_summary`.
- UNSUPPORTED: wrong date, patient, provider, or body part, or the page does not support it.

Check each item for:
1. Right speaker? (patient vs provider, patient vs family member)
2. Right status? (ordered vs performed)
3. Qualifiers kept? ("at this time", "temporary", "may")
4. Side stated on the page for this exact finding?
5. Date of service, or some other date on the page?

When unsure, choose OVERSTATED or UNSUPPORTED.

## Example
Input item: `item_ref: B1-p148-a-4`, summary "EMG performed", quote "EMG ordered".
Output:
```json
{"results":[{"item_ref":"B1-p148-a-4","label":"OVERSTATED","reason":"Page says the EMG was ordered, not performed.","corrected_summary":"EMG ordered"}],
"coverage":"Checked 1 item from PDF page 148."}
```
For a SUPPORTED item, `corrected_summary` is an empty string.

## Final check
- One result per item. Every non-SUPPORTED result has a reason.
